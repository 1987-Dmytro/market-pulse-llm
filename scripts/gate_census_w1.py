#!/usr/bin/env python3
"""The comment-thread gate, censused and priced — `results/gate_census_w1.json`.

**What this answers.** `docs/PLAN-comment-signals.md` §2 puts a $0 gate in front of the only paid
step: a thread passes when the lexicon (brands ∪ tracked categories) finds something anywhere in it,
and four cheap silencers drop what the operator has already ruled is not a brand signal. Two knobs
are open — how wide the category vocabulary is, and whether the silencers run — so this walks the
2×2 grid over window-1's own evidence and prices each cell at the MEASURED serverless rate.

**What it does not do.** It writes no pre-registration. The bars for the stance probe are the
operator's word at the design sitting (§5 of the plan), and a record that quietly proposed them
would be a registration written by its own executor. Nothing here is spent, sent or inferred.

**The unit is a thread**, and the join is checked rather than assumed: every one of the window's
comments carries a `parent_msg_id`, and all 514 distinct parents are present in `data/raw/posts`.
The post's TEXT is part of the gate — the plan's step B reads the whole thread — and it comes from
the raw store, not from the rendered prompt, so a thread whose post said the only category word is
still a thread that passes.

**The price is a bound, not a rate.** `results/run_5c2_comments.json` measured 4.247 s per COMMENT
row, one call per row. The plan's step C is one call per THREAD, whose input is the whole thread and
whose output is a single verdict. Those are different jobs, so the projection is carried as an
interval — see :func:`price` — and never as a single number derived from somebody else's unit.

    PYTHONPATH=src python3 scripts/gate_census_w1.py
    PYTHONPATH=src python3 scripts/gate_census_w1.py --out /tmp/again.json   # the pair
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_aggregates as builder  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import brands, loop, yield_screen  # noqa: E402
from market_pulse.lexicon import load_lexicon  # noqa: E402

RAW_POSTS = REPO_ROOT / "data" / "raw" / "posts"
LEXICON = REPO_ROOT / "config" / "lexicon.yaml"
DRAFT = REPO_ROOT / "data" / "category_lexicon_draft.json"
PRICES = REPO_ROOT / "results" / "run_5c2_comments.json"
OUT = REPO_ROOT / "results" / "gate_census_w1.json"

CARRIER = "comment"

PLUS_SPAM = re.compile(
    r"^[+\-—•.,!?)(\s]*(?:\+|тест|test|тесты|тест\s*\d*)?[+\-—•.,!?)(\s]*$", re.I
)
"""The «плюс-спам» silencer of the plan's step B (3): a comment that is a participation marker and
nothing else. Deliberately narrow — it fires only when the WHOLE comment is that marker, so a
sentence containing «+» survives. A census definition, not law: the taxonomy is the sitting's."""

MONEY = re.compile(r"(?:\d[\d\s.,]*\s*(?:грн|₴|\$|usd|дол)|(?:грн|₴|\$)\s*\d)", re.I)
CONTACT = re.compile(r"(?:https?://|t\.me/|@[A-Za-z][A-Za-z0-9_]{3,})")
"""The scam silencer of step B (4): money AND a way to be contacted, in one comment."""


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def raw_posts() -> dict[tuple[str, int], str]:
    """`(channel, msg_id) -> text` for every post in the raw store.

    `msg_id` is cast: the raw store writes it as a STRING and the derived rows carry an int, and two
    id fields that look comparable and are not is how a join silently returns nothing.
    """
    posts: dict[tuple[str, int], str] = {}
    for path in sorted(RAW_POSTS.glob("*.jsonl")):
        for row in summary.read_rows(path):
            posts[(row["channel"], int(row["msg_id"]))] = row.get("text") or ""
    return posts


def threads(comments: list[dict], posts: dict) -> tuple[list[dict], list[tuple[str, int]]]:
    """The window's comments grouped by their parent post — and the parents that are missing.

    The missing list is RETURNED rather than raised on: a thread whose post is not in the store is
    still a thread, and the census has to say how many of them there are before anybody builds a
    pipeline on the assumption that there are none.
    """
    grouped: dict[tuple[str, int], dict] = {}
    for row in comments:
        key = (row["channel"], int(row["parent_msg_id"]))
        thread = grouped.setdefault(key, {"channel": key[0], "post_id": key[1], "comments": []})
        thread["comments"].append(row)
    for key, thread in grouped.items():
        thread["post_text"] = posts.get(key, "")
    return [grouped[key] for key in sorted(grouped)], sorted(
        key for key in grouped if key not in posts
    )


def category_terms(wide: bool) -> dict[str, list[str]]:
    """The two vocabularies, each read from the file that owns it.

    Narrow is `config/lexicon.yaml`'s tracked groups — the LAW (SPEC 3.17 (8)), dairy and ice cream.
    Wide adds the draft's other families (bakery, meat, drinks, …), which are explicitly NOT law and
    are here only to price what a wider gate would let through.
    """
    law = load_lexicon(LEXICON)
    terms = {group: list(stems) for group, stems in law["tracked"].items()}
    if wide:
        draft = json.loads(DRAFT.read_text(encoding="utf-8"))
        for group, stems in sorted(draft["draft"].items()):
            terms[group] = list(stems)
    return terms


def compiled(wide: bool):
    law = load_lexicon(LEXICON)
    return yield_screen.compile_categories(
        {"tracked": category_terms(wide), "endings": law["endings"]}
    )


def hits(text: str, categories, aliases, rules) -> dict:
    """What the gate finds in one piece of text: brand ids and category groups."""
    found = (
        brands.find_watchlist_brands(text, aliases, rules, carrier=CARRIER)
        if rules
        else (brands.find_watchlist_brands(text, aliases))
    )
    return {
        "brands": sorted(one["brand_id"] for one in found),
        "categories": sorted(set(yield_screen.category_hits(text, categories))),
    }


SILENCERS = ("varto_rule", "plus_spam", "scam")
"""The three of the plan's four that have an input in this window, in the order the pipeline applies
them. `giveaway_threads` is the fourth and is absent for a reason the record states."""


def silenced_comment(row: dict, active: tuple[str, ...]) -> str | None:
    """Which per-comment silencer removes this row, or None. First match wins, and it is named."""
    text = summary.comment_text(row)
    if not loop.has_text(text):
        return None
    if "plus_spam" in active and PLUS_SPAM.fullmatch(text.strip()):
        return "plus_spam"
    if "scam" in active and MONEY.search(text) and CONTACT.search(text):
        return "scam"
    return None


def price(threads_kept: int, comments_kept: int, prices: dict) -> dict:
    """The projected cost of ONE LLM reading per kept thread — as an interval, with its sample.

    The only measured price this repo owns for this instrument is per COMMENT row: 4.247 s of
    serverless worker time at $0.00030669/s, over 5 078 rows in 55 calls. A per-thread call is a
    different job — its input is every comment in the thread, its output one verdict — so the
    measured rate cannot be multiplied by a thread count and called an answer.

    * `lower` — one thread call costs at least what one comment call cost. Threads × the unit.
    * `upper` — a thread call cannot cost more than reading each of its comments separately: the
      same text goes in, and one verdict comes out instead of N. Comments × the unit.

    The truth is inside that interval and the probe of the plan's §5 is what collapses it. Naming
    both ends is the `.claude/rules/registrations-and-draws.md` rule applied to a projection: a rate
    is a property of the sample it was measured on, and this one was not measured on threads.
    """
    unit_seconds = prices["timing"]["seconds_per_row"]
    rate = prices["rate_usd_per_second"]
    return {
        "lower_usd": round(threads_kept * unit_seconds * rate, 4),
        "upper_usd": round(comments_kept * unit_seconds * rate, 4),
        "unit": "one comment row, one call — NOT one thread",
        "unit_seconds": unit_seconds,
        "rate_usd_per_second": rate,
        "sample": (
            f"{prices['timing']['rows']} comment rows in {prices['timing']['calls']} calls on"
            f" endpoint {prices['endpoint']}, {prices['timing']['worker_seconds']} worker-seconds"
            f" ({rel(PRICES)})"
        ),
    }


def cell(
    all_threads: list[dict], wide: bool, active: tuple[str, ...], aliases, rules, prices
) -> dict:
    """One gate configuration: which threads pass, how many payable comments they carry, the cost.

    ``active`` is the set of silencers running, so a caller can ask for one at a time — the kills
    OVERLAP (a thread can lose its only hit to the plus-spam rule and to the varto rule at once) and
    a decomposition that only ever ran them together could not show that.
    """
    categories = compiled(wide)
    kept, killed = [], dict.fromkeys(("plus_spam", "scam"), 0)
    for thread in all_threads:
        comments = thread["comments"]
        if set(active) & {"plus_spam", "scam"}:
            surviving = []
            for row in comments:
                why = silenced_comment(row, active)
                if why:
                    killed[why] += 1
                else:
                    surviving.append(row)
            comments = surviving
        texts = [thread["post_text"]] + [summary.comment_text(row) for row in comments]
        rule = rules if "varto_rule" in active else None
        if not any(
            one["brands"] or one["categories"]
            for one in (hits(text, categories, aliases, rule) for text in texts)
        ):
            continue
        kept.append(
            {
                "comments": comments,
                "payable": [row for row in comments if loop.has_text(summary.comment_text(row))],
            }
        )
    payable = sum(len(one["payable"]) for one in kept)
    return {
        "silencers": list(active),
        "threads": len(kept),
        "comments": sum(len(one["comments"]) for one in kept),
        "comments_payable": payable,
        "comments_silenced_window_wide": killed,
        "cost": price(len(kept), payable, prices),
    }


def census(argv: list[str] | None = None) -> dict:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--derived-root", type=Path, default=builder.DERIVED)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)

    prereg = json.loads(summary.read_text_or_refuse(builder.PREREG))
    registry = summary.registry_through_the_seal(prereg, builder.REGISTRY)
    aliases = brands.watchlist_aliases(registry.watchlist)
    rules = brands.load_watchlist_rules(builder.RULES)

    sources: dict[str, str] = {}
    comments: list[dict] = []
    for path in summary.leg_files(args.derived_root, loop.RECORD_TYPE):
        sources[rel(path)] = summary.sha256_of(path)
        comments += summary.read_rows(path)
    for path in sorted(RAW_POSTS.glob("*.jsonl")):
        sources[rel(path)] = summary.sha256_of(path)

    posts = raw_posts()
    all_threads, orphans = threads(comments, posts)
    prices = json.loads(summary.read_text_or_refuse(PRICES))
    text_less = sum(1 for row in comments if not loop.has_text(summary.comment_text(row)))

    grid = {
        f"{width}|silencers_{'on' if on else 'off'}": cell(
            all_threads, width == "wide", SILENCERS if on else (), aliases, rules, prices
        )
        for width in ("narrow", "wide")
        for on in (False, True)
    }
    # one silencer at a time, on the narrow gate — because the kills OVERLAP and the 2×2 alone
    # would read as four disjoint buckets. The sum of the three singles is not the trio's effect,
    # and the record has to be able to show that rather than leave it to be assumed.
    alone = {name: cell(all_threads, False, (name,), aliases, rules, prices) for name in SILENCERS}
    record = {
        "phase": "fix-a",
        "contract": "docs/PROMPT-fix-a.md deliverable 3",
        "authority": (
            "docs/PLAN-comment-signals.md §2 (the gate and its four silencers) and docs/SPEC.md"
            " amendment 3.21 (2), which ratifies that architecture. No pre-registration is written"
            " here: the probe's bars are the operator's word at the design sitting (plan §5)."
        ),
        "window": {
            "id": builder.WINDOW_ID,
            "comments": len(comments),
            "comments_text_less": text_less,
            "threads": len(all_threads),
            "threads_with_no_post_in_the_raw_store": [
                {"channel": channel, "post_id": post_id} for channel, post_id in orphans
            ],
            "reading": (
                "the unit is a thread: one post and every comment that replies to it. The post's"
                " own text is part of the gate, so a thread whose post carried the only category"
                " word still passes. Text-less comments are counted and never read — SPEC 3.19 (1)"
                " skips them before payment — so the priced population is the payable one"
            ),
        },
        "lexicons": {
            "narrow": {
                "source": rel(LEXICON),
                "sha256": summary.sha256_of(LEXICON),
                "groups": category_terms(wide=False),
                "reading": "the tracked vocabulary as LAW (SPEC 3.17 (8)): dairy and ice cream",
            },
            "wide": {
                "source": f"{rel(LEXICON)} + {rel(DRAFT)}",
                "sha256": summary.sha256_of(DRAFT),
                "groups": category_terms(wide=True),
                "reading": (
                    "the law plus the draft's other families, which are explicitly NOT law"
                    " (`status: draft-not-law`). Priced to show what a wider gate would let in"
                ),
            },
            "matcher": "stem + one of the lexicon's endings, bounded by non-word characters",
        },
        "silencers": {
            "varto_rule": {
                "implemented": True,
                "definition": (
                    f"the named revision {rules.revision} of {rel(builder.RULES)}: a hit on"
                    f" {', '.join(sorted(rules.required))} survives only with its marker in the"
                    " same text (SPEC 3.21 (1))"
                ),
                "authority": "operator sitting 2026-08-10 §1–§2, ruling 2026-08-15",
            },
            "plus_spam": {
                "implemented": True,
                "definition": (
                    "a comment whose WHOLE text is a participation marker — «+», «Тест» and the"
                    " punctuation around them. A sentence that contains «+» is not silenced"
                ),
                "authority": "docs/PLAN-comment-signals.md §2 B (3) — census definition, not law",
            },
            "scam": {
                "implemented": True,
                "definition": (
                    "a comment carrying BOTH a money token (грн / ₴ / $ / дол) and a way to be"
                    " contacted (an http link, a t.me link or an @handle)"
                ),
                "authority": "docs/PLAN-comment-signals.md §2 B (4) — census definition, not law",
            },
            "giveaway_threads": {
                "implemented": False,
                "definition": (
                    "threads whose POST is a giveaway, dropped whole — the plan reads the post-type"
                    " label the model already produces (gate G1d)"
                ),
                "why_not": (
                    "window-1 carries no post-type label. The post-type head was gated on the"
                    " frozen test set and never run over this window's posts: the window's post leg"
                    " is the POSITION instrument (`positions_text_gm4`, 44 rows over 10 channels),"
                    " and its replies are position lists, not post types. So this silencer would"
                    " remove exactly 0 threads of the window's total — not because giveaway threads"
                    " are absent, but because nothing in the store can name one"
                ),
                "unlock": (
                    "run the post-type head over the window's post texts. It is a model call and"
                    " therefore not $0; it belongs to the cycle-2 loop or to its own probe, and"
                    " until it runs the silencers-on cells below are THREE silencers, not four"
                ),
            },
        },
        "grid": grid,
        "silencer_decomposition": {
            "lexicon": "narrow",
            "gate_without_any": grid["narrow|silencers_off"]["threads"],
            "each_alone": {
                name: {
                    "threads": one["threads"],
                    "threads_removed": grid["narrow|silencers_off"]["threads"] - one["threads"],
                    "comments_silenced_window_wide": one["comments_silenced_window_wide"],
                }
                for name, one in alone.items()
            },
            "all_three_together": {
                "threads": grid["narrow|silencers_on"]["threads"],
                "threads_removed": grid["narrow|silencers_off"]["threads"]
                - grid["narrow|silencers_on"]["threads"],
                "sum_of_the_singles": sum(
                    grid["narrow|silencers_off"]["threads"] - one["threads"]
                    for one in alone.values()
                ),
            },
            "reading": (
                "run one at a time AND together, because silencer kills can overlap and a 2×2 that"
                " only ever ran them as a set would read as buckets it is not. Compare"
                " `threads_removed` with `sum_of_the_singles`: equal means no thread was removed"
                " twice in this window, and any gap is the overlap measured rather than assumed"
            ),
        },
        "versus_the_plan": {
            "planned_threads": "docs/PLAN-comment-signals.md §2 C and §6: «~12–15 тредов на окно»",
            "planned_budget": "§6: «проба на ВСЕХ кандидатах окна-1 — в пределах ≤$0.20»",
            "measured_threads": {name: one["threads"] for name, one in sorted(grid.items())},
            "reading": (
                "the plan's thread count is the team lead's HAND reading — the threads that were"
                " worth reading. The gate is a lexicon over the whole thread, and window-1's feeds"
                " are recipe and parenting channels where a post about syrnyky carries a tracked"
                " stem, so the mechanical gate passes an order of magnitude more. The narrowest"
                " configuration's LOWER cost bound is inside the plan's $0.20; its upper bound is"
                " not. Which of the two the probe actually costs is what the probe measures, and"
                " tightening the gate beyond the lexicon is a design question for the sitting"
            ),
        },
        "reading": (
            "each cell is a gate configuration: which threads reach the paid step, how many payable"
            " comments they carry, and what one LLM reading per thread would cost. The cost is an"
            " INTERVAL because the only measured price is per comment row and a per-thread call is"
            " a different job — the lower end assumes a thread call costs one comment call, the"
            " upper end that it costs as much as reading its comments one by one. The"
            " silencers-on cells run three of the plan's four silencers; the fourth has no input in"
            " this window and says so above rather than reporting a zero as an effect"
        ),
        "sources": sources,
        "producer": {
            "script": rel(Path(__file__)),
            "sha256": summary.sha256_of(Path(__file__)),
            "borrowed": {
                name: summary.sha256_of(REPO_ROOT / name)
                for name in (
                    "scripts/window_summary_5c2.py",
                    "src/market_pulse/brands.py",
                    "src/market_pulse/lexicon.py",
                    "src/market_pulse/yield_screen.py",
                    "src/market_pulse/loop.py",
                )
            },
        },
        "inputs": {
            rel(path): summary.sha256_of(path)
            for path in (LEXICON, DRAFT, builder.RULES, builder.REGISTRY, PRICES, builder.PREREG)
        },
    }
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, add_help=False)
    parser.add_argument("--out", type=Path, default=OUT)
    args, _ = parser.parse_known_args(argv)
    record = census(argv)
    args.out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {rel(args.out)}  sha256 {summary.sha256_of(args.out)[:16]}…")
    print(
        f"  window        {record['window']['threads']} threads ·"
        f" {record['window']['comments']} comments ({record['window']['comments_text_less']}"
        " text-less)"
    )
    for name, one in record["grid"].items():
        print(
            f"  {name:22s} {one['threads']:4d} threads · {one['comments_payable']:5d} payable"
            f" comments · ${one['cost']['lower_usd']:.4f} – ${one['cost']['upper_usd']:.4f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
