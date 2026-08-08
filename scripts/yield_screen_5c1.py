#!/usr/bin/env python3
"""The yield screen: how much of OUR taxonomy is in each channel's window? ($0, offline.)

Canon: `docs/SPEC.md` amendment 3.12 (1), the relevance floor of the track-R entry gate — the
operator's question that exposed the gap was "channels were admitted with no taxonomy measurement
at all". The gate grades capability, the census grades language, the market screen grades market
origin, the theme screen grades "about food"; none of them ever asked whether the tracked category
is in there. This does, retroactively, over the whole registry.

Posts and comments are SEPARATE currencies and are never blended: retail_official earns on posts,
audience segments earn on comments. Two bars, one per currency, pre-registered in
`results/yield_bars_5c1.preregistration.json` before any number existed; the constants below are
checked against that file on every run and the record cites its sha256.

The lexicon is a SCREENING INSTRUMENT here, never the category law — 5c3 owns the law. Its own
file says `status: draft-not-law` and the record carries that word beside its hash.

Nothing enters or leaves the registry on this screen. It writes its record; the operator rules.

    PYTHONPATH=src python3 scripts/yield_screen_5c1.py
"""

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_audit_pack import git_state  # noqa: E402

from market_pulse import yield_screen as core  # noqa: E402
from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

REGISTRY = REPO_ROOT / "config" / "registry.yaml"
LEXICON = REPO_ROOT / "data" / "category_lexicon_draft.json"
PREREGISTRATION = REPO_ROOT / "results" / "yield_bars_5c1.preregistration.json"
COLLECT_RECORD = REPO_ROOT / "results" / "collect_5c1.json"
POSTS = REPO_ROOT / "data" / "raw" / "posts"
COMMENTS = REPO_ROOT / "data" / "raw" / "comments"
RECORD = REPO_ROOT / "results" / "yield_screen_5c1.json"

BAR_A = 4
BAR_B = 10
"""Ruled by the operator on 2026-08-08 and written into PREREGISTRATION before the screen existed.
`check_preregistration` refuses to run if these drift from it: a bar moved to make the answer nicer
would have to be moved there first, in writing, beside the original."""

WINDOW_DAYS = 28
WEEKS = WINDOW_DAYS / 7

POSITIVE_CONTROLS = ("@atb_market_official", "@silposilpo", "@VARUS_channel", "@msuaaaa")
"""The four original registry channels — two chains, an aggregator, a retailer with comments. If
the instrument cannot find the tracked category in the channels the project was BUILT on, no
verdict it produces about an unknown channel is worth reading. Pre-registered with its direction:
each must clear bar A on its own window."""

NEGATIVE_CONTROL = (
    "Розклад тренувань на тиждень: понеділок — ноги, середа — спина, п'ятниця — руки."
    " Реєстрація за посиланням, знижка 20% до кінця місяця."
)
"""A fitness post with no taxonomy in it: no dairy, no ice cream, no watchlist brand. It has the
shape of a hit — a food-adjacent feed, a discount, a percentage — and must produce nothing. Without
it, "the screen found 0 hits here" and "the screen finds 0 hits" look the same."""


def check_preregistration() -> tuple[str, dict]:
    """The bars must be the ones written down first. Returns the file's sha256 and its content."""
    raw = PREREGISTRATION.read_bytes()
    bars = json.loads(raw)
    if (bars["bar_A_relevant_posts_28d"], bars["bar_B_comments_under_relevant_28d"]) != (
        BAR_A,
        BAR_B,
    ):
        raise SystemExit(
            f"the bars in this script ({BAR_A}, {BAR_B}) are not the ones registered in"
            f" {PREREGISTRATION.name}. Change that file first, keeping the original beside the"
            " move and saying why."
        )
    return hashlib.sha256(raw).hexdigest(), bars


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue  # a damaged line is not a yield; collect_5c1.json counts them
    return rows


def collect_window() -> tuple[str, str]:
    """The window `collect_5c1.py` fixed on its first run — read back, never recomputed."""
    since = json.loads(COLLECT_RECORD.read_text(encoding="utf-8"))["window"]["since"]
    until = datetime.fromisoformat(since) + timedelta(days=WINDOW_DAYS)
    return since, until.isoformat()


def collected_handles() -> set[str]:
    record = json.loads(COLLECT_RECORD.read_text(encoding="utf-8"))
    return {row["channel"] for row in record["channels"]}


def window_for(
    handle: str, posts: list[dict], shared: tuple[str, str], collected: set[str]
) -> dict:
    """The 28 days this channel is screened over, and where that window comes from.

    Amendment 3.12 says "a channel's collected 28-day window", and the four originals do not have
    the same one as everybody else: their store is the pinned raw v1 corpus, collected weeks before
    `collect_5c1.json`'s `since` existed and stopped on 2026-07-23…27. Screening them over the
    shared window would measure the collection schedule — they would get 13 to 17 days of coverage
    against everyone else's 28 while bar A counts absolutely. So they are screened over their own
    last 28 days, ending with the day their store ends, and every row says which rule it got.
    """
    if handle in collected:
        since, until = shared
        return {"since": since, "until": until, "source": "collect_5c1"}
    if not posts:
        since, until = shared
        return {"since": since, "until": until, "source": "collect_5c1 (no posts in the store)"}
    last = max(datetime.fromisoformat(row["date"]) for row in posts)
    until = last.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    return {
        "since": (until - timedelta(days=WINDOW_DAYS)).isoformat(),
        "until": until.isoformat(),
        "source": "raw_v1_own_last_28d",
    }


def in_window(rows: list[dict], window: dict) -> list[dict]:
    return [row for row in rows if window["since"] <= row.get("date", "") < window["until"]]


def screen_channel(handle: str, window: dict, compiled: dict, aliases: list, bars: dict) -> dict:
    """One channel's yield over one window. Reads two files and decides nothing."""
    posts = in_window(load_jsonl(POSTS / f"{handle.lstrip('@')}.jsonl"), window)
    comments_path = COMMENTS / f"{handle.lstrip('@')}.jsonl"
    has_comment_source = comments_path.exists()
    comments = load_jsonl(comments_path)

    texted = [row for row in posts if (row.get("text") or "").strip()]
    by_group: dict[str, int] = {}
    by_brand: dict[str, int] = {}
    relevant, carried, with_category, with_brand = [], [], 0, 0
    examples: dict[str, dict] = {}
    for row in texted:
        groups = core.category_hits(row["text"], compiled)
        brands = core.brand_hits(row["text"], aliases)
        for group in groups:
            by_group[group] = by_group.get(group, 0) + 1
        for brand in brands:
            by_brand[brand] = by_brand.get(brand, 0) + 1
        with_category += bool(groups)
        with_brand += bool(brands)
        if groups or brands:
            relevant.append(row)
            terms = core.carriers(row["text"], compiled, aliases)
            carried.append(terms)
            for term in terms - set(examples):
                if found := core.evidence_line(row["text"], compiled, aliases, want=term):
                    examples[term] = {"msg_id": row["msg_id"], **found}

    relevant_ids = {row["msg_id"] for row in relevant}
    under_relevant = [row for row in comments if row.get("parent_msg_id") in relevant_ids]
    threads = {row["parent_msg_id"] for row in under_relevant}

    evidence = None
    for row in sorted(relevant, key=lambda r: r["msg_id"]):
        if found := core.evidence_line(row["text"], compiled, aliases):
            evidence = {**found, "msg_id": row["msg_id"], "date": row["date"]}
            break

    return {
        "handle": handle,
        "window": {
            **window,
            "last_post": max((row["date"] for row in posts), default=None),
        },
        "posts": {
            "in_window": len(posts),
            "with_text": len(texted),
            # The project already excludes channels as TEXT-FREE — «on topic and unreadable»
            # (@ATB_FANatik, @discountua1). A bar over all window posts cannot tell that class
            # from an off-category one, and they are different operator rulings.
            "without_text": len(posts) - len(texted),
        },
        "relevant_posts": len(relevant),
        "relevant_per_week": round(len(relevant) / WEEKS, 2),
        "relevant_share_of_window": round(len(relevant) / len(posts), 3) if posts else 0.0,
        "relevant_share_of_texted": round(len(relevant) / len(texted), 3) if texted else 0.0,
        "brand_hits": {
            "posts": with_brand,
            "per_week": round(with_brand / WEEKS, 2),
            "by_brand": dict(sorted(by_brand.items())),
        },
        "category_hits": {
            "posts": with_category,
            "per_week": round(with_category / WEEKS, 2),
            "by_group": dict(sorted(by_group.items())),
        },
        "comments": {
            "source": "collected" if has_comment_source else "none",
            "in_store": len(comments),
            "under_relevant": len(under_relevant),
            "relevant_threads_with_comments": len(threads),
        },
        **core.bar_verdicts(len(relevant), len(under_relevant), has_comment_source, bars),
        # Whether a FAIL on bar A is about content at all. A channel with fewer readable posts
        # than the bar cannot clear it whatever it publishes — and the whole `watch` bucket is
        # silent by definition, which the operator already ruled on once.
        "bar_A_reach": core.bar_A_reach(len(posts), len(texted), bars["bar_A_relevant_posts_28d"]),
        # Which terms this row's bar-A pass hangs on. Measured, not judged: a row carried by
        # «сир» and a row carried by «варто» read identically in the counts above.
        "bar_A_sole_carriers": core.sole_carriers(carried, bars["bar_A_relevant_posts_28d"]),
        "evidence": evidence,
        "_carried": carried,
        "_examples": examples,
    }


def term_evidence(rows: list[dict]) -> dict:
    """Every matcher term, with what it actually fired on. The audit of the counts above.

    «варто» is on the watchlist as an АТБ private label and is also the ordinary Ukrainian word
    for "it is worth"; «масл» + the lexicon's `ов` ending is the surname «Маслов»; «Президент» is
    a brand and a head of state. None of that is decided here — the lexicon says `draft-not-law`
    and the watchlist is the operator's. What is decided here is that a term cannot hide inside a
    total: each one carries its post count, the channels it fired in, one quoted line, and the
    rows whose bar-A pass would not survive its removal.
    """
    out: dict[str, dict] = {}
    for row in rows:
        for terms in row["_carried"]:
            for term in terms:
                entry = out.setdefault(
                    term, {"posts": 0, "channels": set(), "sole_carrier_for": []}
                )
                entry["posts"] += 1
                entry["channels"].add(row["handle"])
    for row in rows:
        for term in row["bar_A_sole_carriers"]:
            out[term]["sole_carrier_for"].append(row["handle"])
    for term, entry in out.items():
        entry["example"] = next(
            (
                {"handle": row["handle"], **row["_examples"][term]}
                for row in rows
                if term in row["_examples"]
            ),
            None,
        )
        entry["channels"] = len(entry["channels"])
    return dict(sorted(out.items(), key=lambda pair: (-pair[1]["posts"], pair[0])))


def run_controls(rows: dict[str, dict], compiled: dict, aliases: list) -> dict:
    """The screen's exam, taken before its verdicts are read."""
    out = {}
    for handle in POSITIVE_CONTROLS:
        row = rows.get(handle)
        out[handle] = {
            "kind": "positive",
            "expected": f"clears bar A ({BAR_A} relevant posts) on its own window",
            "window_source": (row or {}).get("window", {}).get("source"),
            "relevant_posts": (row or {}).get("relevant_posts"),
            "measured": (row or {}).get("bar_A"),
            "evidence": (row or {}).get("evidence"),
            "ok": bool(row) and row["bar_A"] == "PASS",
        }
    hits = core.category_hits(NEGATIVE_CONTROL, compiled) + core.brand_hits(
        NEGATIVE_CONTROL, aliases
    )
    out["negative control :: a fitness post with no taxonomy"] = {
        "kind": "negative",
        "expected": "no category and no brand — a discount and a percentage are not the category",
        "line": NEGATIVE_CONTROL,
        "measured": hits,
        "ok": not hits,
    }
    return out


RULINGS = {
    # Operator, yield-screen acceptance 2026-08-08. Both rows cleared bar A, and the screen's own
    # `bar_A_sole_carriers` says each of them clears it on ONE term that is an ordinary word:
    # «варто» is an АТБ private label and the Ukrainian for "it is worth"; «Президент» is a cheese
    # brand and a head of state. The ruling is about these two rows, not about the terms — the
    # lexicon says `draft-not-law` and the matcher guards are 5c3's work, so nothing is patched.
    "@polyakova_fitness": (
        "COUNTS AS BELOW bar A — the pass hangs on `brand:varto` alone, the ordinary word."
        " Matcher guard for «Варто» deferred to the 5c3 lexicon session"
    ),
    "@myrhorodtown": (
        "COUNTS AS BELOW bar A — the pass hangs on `brand:president` alone, the head of state."
        " Matcher guard for «Президент» deferred to the 5c3 lexicon session"
    ),
}
"""Operator rulings over rows this screen already measured, applied by `--close` and never by a
re-screen. The market screen's division of labour: the screen records what it found, a human
decides what it means, and the reading goes into the record beside the evidence."""


def close_rulings(out: Path) -> int:
    """Write the rulings onto their rows. No re-measurement, and the measurement's own git stays.

    Two things this deliberately does not do. It does not flip `bar_A`: PASS is what the
    instrument measured, BELOW is what the operator ruled, and a record that showed only the
    second could never be re-read as evidence about the first. And it does not touch the
    top-level `git` block — that is the provenance of the screen the operator signed against, not
    of a ruling pass; the ruling carries its own.
    """
    record = json.loads(out.read_text(encoding="utf-8"))
    rows = {row["handle"]: row for row in record["sources"]}
    if missing := sorted(set(RULINGS) - set(rows)):
        raise SystemExit(
            f"{out.name} has no rows for {missing} — refusing to write a ruling to no one"
        )
    for handle, ruling in RULINGS.items():
        rows[handle]["ruling"] = ruling
        print(f"{handle:<24}{rows[handle]['bar_A']:<6}{rows[handle]['bar_A_sole_carriers']}")
    # The pass list is 29 rows and two of them are now ruled below the bar. Said in the summary
    # because that is where a reader counts, and `pass_A` itself is the measurement and stands.
    record["summary"]["pass_A_ruled_below_bar_A"] = sorted(RULINGS)
    record["rulings"] = {
        "applied_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "by": "operator 2026-08-08, yield-screen acceptance",
        "contract": "docs/PROMPT-5c1-captions-pilot.md step 0",
        "note": (
            "read onto rows that were already measured; no re-screen, no evidence re-derived."
            " `bar_A` stays PASS — it is what the instrument found — and the ruling beside it is"
            " what the operator decided that pass is worth. Matcher guards for «Варто» and"
            " «Президент» are deferred to the 5c3 lexicon session and are not applied here"
        ),
        "git": git_state(out),
    }
    out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {len(RULINGS)} ruling(s) into {out.name}")
    return 0


def refuse_to_overwrite(out: Path) -> None:
    """A screen is a measurement of a composition, and the composition moves.

    The same refusal the census and the market screen carry (D68). This record is what the
    operator's launch signature is given against — amendment 3.12's rider — so a later pass under
    a different registry must not be able to land under the name the signature cites.
    """
    if out == RECORD and RECORD.exists():
        raise SystemExit(
            f"{rel(RECORD)} already exists — it is the screen of the composition as it stood when"
            " the operator signed against it. A pass over a moved registry is a different"
            " measurement: give it --out with another path."
        )


def print_table(rows: list[dict]) -> None:
    header = (
        f"{'channel':<30}{'posts':>6}{'rel':>5}{'br':>4}{'cat':>4}{'cmt':>6}  A    B     evidence"
    )
    print(f"\n{header}\n{'-' * len(header)}")
    for row in rows:
        evidence = row["evidence"] or {}
        shown = f"{evidence.get('matched', '—')}: {evidence.get('line', '')}"
        print(
            f"{row['handle'][:29]:<30}{row['posts']['in_window']:>6}{row['relevant_posts']:>5}"
            f"{row['brand_hits']['posts']:>4}{row['category_hits']['posts']:>4}"
            f"{row['comments']['under_relevant']:>6}  {row['bar_A']:<5}{row['bar_B']:<6}{shown[:52]}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=RECORD, help="where to write the record")
    parser.add_argument("--only", metavar="HANDLE", nargs="+", help="screen only these handles")
    parser.add_argument(
        "--close",
        action="store_true",
        help="write the operator's rulings onto an existing record; measures nothing",
    )
    args = parser.parse_args(argv)
    if args.close:
        return close_rulings(args.out)
    refuse_to_overwrite(args.out)

    prereg_sha, bars = check_preregistration()
    lexicon = json.loads(LEXICON.read_text(encoding="utf-8"))
    registry = load_registry(REGISTRY)
    compiled = core.compile_categories(lexicon)
    aliases = core.compile_aliases(watchlist_aliases(registry.watchlist))

    shared = collect_window()
    collected = collected_handles()
    sources = {handle: source for source in registry.sources for handle in source.telegram_channels}
    handles = list(sources)
    if args.only:
        if missing := set(args.only) - set(handles):
            raise SystemExit(f"--only names handles the registry does not carry: {sorted(missing)}")
        handles = [handle for handle in handles if handle in args.only]

    rows = []
    for handle in handles:
        posts = load_jsonl(POSTS / f"{handle.lstrip('@')}.jsonl")
        window = window_for(handle, posts, shared, collected)
        row = screen_channel(handle, window, compiled, aliases, bars)
        source = sources[handle]
        rows.append(
            {
                **row,
                "audience": source.audience,
                "source_type": source.source_type,
                "watch": source.watch,
            }
        )
        if window["source"] == "raw_v1_own_last_28d":
            # The reading under the shared window, beside the one the row is scored on. The rule
            # was chosen because 3.12 says "a channel's collected window" and the brief says "on
            # ITS window" — and it is favourable to these four, so the alternative is published
            # rather than described.
            alternative = screen_channel(
                handle,
                {**dict(zip(("since", "until"), shared)), "source": "collect_5c1"},
                compiled,
                aliases,
                bars,
            )
            rows[-1]["alternative_window"] = {
                "source": "collect_5c1",
                "posts_in_window": alternative["posts"]["in_window"],
                "relevant_posts": alternative["relevant_posts"],
                "bar_A": alternative["bar_A"],
                "note": "reported, not scored: the store ends before this window does",
            }

    term_block = term_evidence(rows)
    for row in rows:
        del row["_carried"], row["_examples"]

    rows.sort(key=lambda row: (row["audience"] or "", row["handle"].lower()))
    by_handle = {row["handle"]: row for row in rows}
    controls = run_controls(by_handle, compiled, aliases)
    reportable = all(control["ok"] for control in controls.values())

    by_audience: dict[str, dict] = {}
    for row in rows:
        bucket = by_audience.setdefault(
            row["audience"] or "unassigned",
            {"n": 0, "pass_A": 0, "pass_B": 0, "below_both": 0, "below_both_gradeable": 0},
        )
        bucket["n"] += 1
        bucket["pass_A"] += row["bar_A"] == "PASS"
        bucket["pass_B"] += row["bar_B"] == "PASS"
        bucket["below_both"] += row["below_both"]
        bucket["below_both_gradeable"] += row["below_both"] and row["bar_A_reach"] == "gradeable"

    record = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "phase": "5c1 — the relevance floor",
        "asks": "how much of the tracked taxonomy is in each channel's collected 28-day window",
        "contract": "docs/SPEC.md amendment 3.12 (1); docs/PROMPT-5c1-yield.md step 4",
        "report_only": (
            "nothing enters or leaves the registry on this screen. Zero-yield members are"
            " surfaced with their numbers; removal is an operator ruling, never automatic"
        ),
        "preregistration": {
            "path": rel(PREREGISTRATION),
            "sha256": prereg_sha,
            **bars,
        },
        "lexicon": {
            "path": rel(LEXICON),
            "sha256": sha256_of(LEXICON),
            "status": lexicon["status"],
            "role": (
                "a screening instrument, never the category law — 5c3 owns the law. Only the"
                " `tracked` half is read: dairy and ice-cream are the taxonomy, the `draft`"
                " families beside them are other people's categories"
            ),
            "known_collision": lexicon["known_collision"],
        },
        "registry": {
            "path": rel(REGISTRY),
            "sha256": sha256_of(REGISTRY),
            "sources": len(registry.sources),
            "watchlist_brands": len(registry.watchlist),
            "note": "the watchlist revision this run read — G1e history is never re-scored on it",
        },
        "window": {
            "days": WINDOW_DAYS,
            "shared": {"since": shared[0], "until": shared[1]},
            "rule": (
                "since <= date < until, half-open, so the bar counts exactly 28 days. This is"
                " STRICTER than the census and the market screen, which filter `date >= since`"
                " only: @myrhorodtown reads 273 posts there and 260 here, and the difference is"
                " the overhang of channels collected on 08.08, not a disagreement"
            ),
            "raw_v1": (
                "the four original channels are screened over their own last 28 days: their store"
                " is the pinned raw v1 corpus, collected before this window's `since` existed. The"
                " shared-window reading is published beside them under `alternative_window`"
            ),
        },
        "rules": {
            "currencies": bars["currencies"],
            "bar_A": f"relevant posts in the window >= {BAR_A}",
            "bar_B": f"comments under relevant posts >= {BAR_B}",
            "bar_B_na": (
                "no readable comment source — no comments file for the channel. A group that WAS"
                " read and produced nothing scores a measured zero, which is a FAIL"
            ),
            "relevant_post": "a post whose text names a tracked category group or a watchlist brand",
            "comment_join": (
                "comment.parent_msg_id == post.msg_id — the CHANNEL post id. It is never compared"
                " to reply_to_msg_id, which lives in the discussion group's own id space"
            ),
            "matching": (
                "casefold; categories by the lexicon's own matcher and endings as shipped; brands"
                " by the display name exactly as written, the matcher G1e is scored against. A hit"
                " counts once per post"
            ),
            "nested_aliases": (
                "«Яготинське для дітей» contains «Яготинське» and the operator tracks them"
                " separately, so the longer span wins and the shorter one inside it is dropped"
            ),
            "below_both": "cleared neither bar — bar A FAIL and bar B not PASS",
            "bar_A_reach": (
                "whether bar A was reachable at all: NO_POSTS_IN_WINDOW, or TOO_FEW_TEXTED_POSTS"
                " when the channel has fewer readable posts than the bar is high. A refusal to"
                " rule, not a verdict — the census answers the same way, and the whole `watch`"
                " bucket is silent by definition"
            ),
            "evidence": "a quoted line with the term that matched it, never a counter",
        },
        "controls": controls,
        "verdicts_reportable": reportable,
        "term_evidence": term_block,
        "summary": {
            "n": len(rows),
            "pass_A": [row["handle"] for row in rows if row["bar_A"] == "PASS"],
            "pass_B": [row["handle"] for row in rows if row["bar_B"] == "PASS"],
            "below_both": [row["handle"] for row in rows if row["below_both"]],
            # The same list split by whether the bar was reachable. `below_both` is the
            # pre-registered flag and is not touched; this says which of its rows are a finding
            # about CONTENT and which are a channel the window could not grade at all.
            "below_both_gradeable": [
                row["handle"]
                for row in rows
                if row["below_both"] and row["bar_A_reach"] == "gradeable"
            ],
            "below_both_not_gradeable": {
                row["handle"]: row["bar_A_reach"]
                for row in rows
                if row["below_both"] and row["bar_A_reach"] != "gradeable"
            },
            "by_audience": dict(sorted(by_audience.items())),
        },
        "sources": rows,
        "git": git_state(args.out),
    }
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print_table(rows)
    summary = record["summary"]
    print(
        f"\n{len(rows)} sources · bar A passed {len(summary['pass_A'])}"
        f" · bar B passed {len(summary['pass_B'])} · below both {len(summary['below_both'])}"
    )
    for name, control in controls.items():
        print(f"control {name:<52}{'OK' if control['ok'] else 'FAILED'} — {control['expected']}")
    print(f"\nwrote {rel(args.out)}")
    if not reportable:
        print("STOP: a control came back wrong, so the verdict columns are not reportable.")
        return 1
    print("REPORT ONLY: every number here is the operator's to rule on; nothing was removed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
