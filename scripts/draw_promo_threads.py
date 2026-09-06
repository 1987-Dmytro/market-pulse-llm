#!/usr/bin/env python3
"""C3 step 0: the dev-40 / holdout-40 draw over the price threads ($0, no Telegram, no model).

The operator's ruling, 2026-08-30 — «Все 678, дро 20/20 по типу» — settles the population and the
stratification at once. A promo post whose price is in the IMAGE is a price post, so the population
is every thread `retail_census.PRICE_BRANCHES` selects, and the finding that two thirds of them
match on the `decimal` branch alone (which also fires on «14.08») becomes the draw's stratification
instead of a cut:

    currency      the post's text carries `грн`, `₴` or `grn`
    decimal-only  it matches `\\d+[,.]\\d\\d` and none of those three

dev-40 = 20 + 20 and holdout-40 = 20 + 20, disjoint and frozen at the draw. Bars are on the whole
40; per-stratum agreement is reported beside them as a reading, which is what the finding buys.

`results/promo_comment_yield.json` carries COUNTS and no thread ids, so the ids are re-derived here
with the SAME predicate its producer used — `PRICE_BRANCHES` joined on `parent_msg_id` — and the
draw and the census therefore measure the same instrument.

Two things the record has to say out loud, because neither is visible in a list of ids:

* **The queue rule.** SPEC 3.19: a text-less comment leaves the inference queue from the next paid
  cycle — a queue rule, never a deletion, and «the volume of wordless reactions is itself a signal».
  So the wordless count is printed, and a thread with nothing but wordless comments is not drawn:
  there is nothing in it to annotate. Both numbers are in the record.
* **Which channels no longer feed.** Six of the seven tail channels are in the PAUSED 39 that
  revision r2 takes out of collection. Their threads are already on disk and stay in the population,
  but a drawn thread from one of them is marked, so nobody later reads it as ongoing coverage.

Seeded PER STRATUM (`.claude/rules/registrations-and-draws.md`): one `Random(42)` walked across two
pools puts the two draws on correlated ranks, and the record prints only the seed. The ranks are in
the record so a test can measure their distribution rather than compare ids.

The record is sorted, carries no clock and no git block, so two runs are byte-identical — which is
the check (K7) and the reason the team lead can label from it.

    python3.11 scripts/draw_promo_threads.py
    python3.11 scripts/draw_promo_threads.py --arms holdout=20 --drop-paused \\
        --exclude-drawn results/promo_threads_draw.json \\
        --exclude-drawn results/promo_threads_draw_2.json --out results/promo_threads_draw_3.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

from market_pulse.registry import load_registry  # noqa: E402
from retail_census import PRICE_BRANCHES  # noqa: E402

POSTS = REPO_ROOT / "data" / "raw" / "posts"
COMMENTS = REPO_ROOT / "data" / "raw" / "comments"
REGISTRY = REPO_ROOT / "config" / "registry.yaml"
OUT = REPO_ROOT / "results" / "promo_threads_draw.json"
BASELINE = REPO_ROOT / "results" / "raw_v1_baseline.sha256"

SEED = 42
PER_STRATUM = {"dev": 20, "holdout": 20}
"""The operator's «дро 20/20 по типу»: 20 from each stratum into dev-40 and 20 into holdout-40."""

ARMS_2 = {"holdout": 20}
"""Draw 2 (ruling 05.09 (s) item 3 (b)) has ONE arm and no dev half: dev-40 and dev-2 are already
drawn, labelled and frozen, so the second draw owes only the new holdout — 20 of each stratum."""

LEGS = {
    1: {
        "authority": "ruling 05.09 (s) item 3 (b) — holdout-2 is drawn from the PRODUCT's"
        " population, not from «все 678»: the frozen v1 population carried threads of channels"
        " revision r2 had already stopped collecting, and 21 of holdout-40's 53 subject misses were"
        " ONE of them (@matusi_ukr, a moms' channel with no retailer and no product)",
        "ruling": "operator 2026-09-05, ruling (s) item 3 (b) — «seed 42 over the frozen 678 MINUS"
        " channels with `collect: false` in registry r2 MINUS the 80 drawn, 20/20, a NEW draw file"
        " (`promo_threads_draw_2.json`; the old stays frozen)»; PHASE-promo-pulse-1.md §2 v9",
        "already_drawn": "every thread the FIRST draw spent — dev-40 and the burned holdout-40,"
        " now dev-2 — leaves the population: the new holdout must be disjoint from both",
    },
    2: {
        "authority": "ruling 06.09 (bb) addendum (b), PHASE v18 §6.2 — holdout-2 read RED on subject"
        " (0.7054) and is spent, now dev-3; holdout-3 is drawn from what the product's population has"
        " LEFT: draw-2's `eligible_after` (398) minus holdout-2's 40 threads, seed 42, 20/20 by"
        " stratum, disjoint from all 120 drawn; its gold is the team lead's, BLIND, and the shot is"
        " bought ONCE and only if P1's dev-3 reading clears the bar",
        "ruling": "operator 2026-09-06 20:05, ruling (bb) addendum (b) — «holdout-3 DRAW at $0: seed 42"
        " over draw-2's eligible_after (398) MINUS holdout-2's 40 threads (= 358), 20/20 by stratum,"
        " disjoint from all 120 drawn, the draw producer re-used with its paths as PARAMETERS»;"
        " PHASE-promo-pulse-1.md §6.2 v18",
        "already_drawn": "every thread the first TWO draws spent — dev-40 and dev-2 (the first draw's"
        " 80) and holdout-2, now dev-3 (the second draw's 40) — leaves the population: holdout-3"
        " must be disjoint from all three",
    },
}
"""The record's decision fields, per LEG — the leg being how many earlier draws it excludes (one:
draw 2, holdout-2; two: draw 3, holdout-3). PHASE §4 v8: a field that states a decision branches
on the leg or the emitter refuses to write; a count with no entry here is refused, never handed a
neighbour's authority. Draw 1 excludes nothing and carries the 30.08 ruling in `build` itself.
Leg 1's three strings are the frozen draw-2 record's, byte for byte — it is pinned by the holdout-2
registration and this script must still reproduce it."""

CURRENCY_BRANCHES = ("грн", "₴", "grn")
"""The branches that are a real currency marker. `decimal` is the fourth and is the other stratum."""


def rows(path: Path) -> list[dict]:
    """Every JSON line of one store file. A damaged last line is skipped, not fatal — a kill
    mid-write is what `RawStore` already tolerates, and this reader must not disagree with it."""
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def branches(text: str) -> list[str]:
    return sorted(name for name, pattern in PRICE_BRANCHES.items() if pattern.search(text or ""))


def threads() -> list[dict]:
    """Every price thread on disk, one row each, sorted — the population the ruling names.

    A thread is a POST that the price predicate selects and that has at least one comment under it.
    The join is `parent_msg_id` against the post's `msg_id`, both as strings, which is what
    `scripts/promo_comment_yield.py` does; ids are stored as strings in the comment rows and as
    whatever the collector wrote in the post rows, so both sides are stringified here.
    """
    found: dict[tuple[str, str], dict] = {}
    for path in sorted(COMMENTS.glob("*.jsonl")):
        stem = path.stem
        by_id = {}
        for post in rows(POSTS / f"{stem}.jsonl"):
            hit = branches(post.get("text") or "")
            if hit:
                by_id[str(post.get("msg_id"))] = (hit, (post.get("date") or "")[:10])
        for comment in rows(path):
            root = str(comment.get("parent_msg_id"))
            if root not in by_id:
                continue
            hit, date = by_id[root]
            key = (stem, root)
            row = found.setdefault(
                key,
                {
                    "channel": comment.get("channel") or f"@{stem}",
                    "store_file": stem,
                    "thread_root": root,
                    "post_date": date,
                    "branches": hit,
                    "stratum": (
                        "currency" if any(b in hit for b in CURRENCY_BRANCHES) else "decimal_only"
                    ),
                    "n_comments": 0,
                    "n_wordless": 0,
                },
            )
            row["n_comments"] += 1
            if not (comment.get("text") or "").strip():
                row["n_wordless"] += 1
    return [found[key] for key in sorted(found)]


def draw(pool: list[dict], stratum: str, arms: dict[str, int] | None = None) -> dict:
    """One stratum's quota, seeded with the stratum in the seed, split across the arms in order.

    Refuses rather than under-fills: a quota that cannot be met is a fact about the population and
    the team lead has to see it, not a shorter list that reads like a complete one.
    """
    arms = arms or PER_STRATUM
    owed = sum(arms.values())
    if len(pool) < owed:
        raise SystemExit(
            f"stratum {stratum!r} has {len(pool)} eligible threads and the draw owes {owed}"
            " — a quota that cannot be filled is a refusal, never a short draw"
        )
    ranked = {(row["store_file"], row["thread_root"]): i for i, row in enumerate(pool)}
    picked = random.Random(f"{SEED}:{stratum}").sample(pool, owed)
    block: dict = {"eligible": len(pool)}
    taken = 0
    for arm, n in arms.items():
        rows_ = picked[taken : taken + n]
        taken += n
        block[arm] = sorted(rows_, key=lambda row: (row["store_file"], row["thread_root"]))
        block[f"{arm}_ranks"] = sorted(ranked[(r["store_file"], r["thread_root"])] for r in rows_)
    return block


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ids_sha256(rows_: list[dict]) -> str:
    """The population pinned BY ROW COUNT and by its ids, never by a date range read at run time."""
    blob = "\n".join(f"{r['store_file']}\x1f{r['thread_root']}" for r in rows_)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def drawn_ids(paths: list[Path]) -> set[tuple[str, str]]:
    """Every (store_file, thread_root) the earlier draws already spent, from their own records."""
    found: set[tuple[str, str]] = set()
    for path in paths:
        body = json.loads(path.read_text(encoding="utf-8"))
        found |= {
            (row["store_file"], row["thread_root"])
            for block in body["draw"].values()
            for arm, rows_ in block.items()
            if isinstance(rows_, list) and not arm.endswith("_ranks")
            for row in rows_
        }
    return found


def _relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def _one_or_all(values: list):
    """One earlier draw is named as a STRING — draw 2's frozen record, pinned by a registration's
    sha, has that shape and must stay reproducible; two or more are named as a list."""
    return values[0] if len(values) == 1 else (values or None)


def build(
    arms: dict[str, int] | None = None,
    *,
    exclude_drawn: list[Path] | None = None,
    drop_paused: bool = False,
) -> dict:
    """The draw record. With no exclusions and the default arms this is draw 1, byte for byte."""
    arms = arms or PER_STRATUM
    population = threads()
    registry = load_registry(REGISTRY)
    not_collected = {
        channel.lstrip("@").lower()
        for source in registry.sources
        if not source.collect
        for channel in source.telegram_channels
    }
    for row in population:
        row["from_a_channel_r2_stopped_collecting"] = row["store_file"].lower() in not_collected

    wordless = sum(row["n_wordless"] for row in population)
    silent = [row for row in population if row["n_comments"] == row["n_wordless"]]
    eligible = [row for row in population if row["n_comments"] > row["n_wordless"]]

    already = drawn_ids(exclude_drawn) if exclude_drawn else set()
    kept = [
        row
        for row in eligible
        if not (drop_paused and row["from_a_channel_r2_stopped_collecting"])
        and (row["store_file"], row["thread_root"]) not in already
    ]
    leg = LEGS.get(len(exclude_drawn or []))
    if (drop_paused or exclude_drawn) and leg is None:
        raise SystemExit(
            f"{len(exclude_drawn or [])} earlier draw(s) excluded and no leg of LEGS carries the"
            " record's decision fields for that count — refused, never a neighbour's authority"
            " (PHASE §4 v8)"
        )
    exclusions = (
        {
            "authority": leg["authority"],
            "paused_channels": {
                "rule": "a thread whose channel carries `collect: false` in config/registry.yaml"
                " (revision r2) leaves the population — the product does not read it, so it may not"
                " grade the instrument that serves the product",
                "channels": sorted(
                    {
                        row["channel"]
                        for row in eligible
                        if row["from_a_channel_r2_stopped_collecting"]
                    }
                ),
                "eligible_threads_in_them": len(
                    [row for row in eligible if row["from_a_channel_r2_stopped_collecting"]]
                ),
            },
            "already_drawn": {
                "rule": leg["already_drawn"],
                "from": _one_or_all([_relative(path) for path in exclude_drawn or []]),
                "sha256": _one_or_all([_sha256(path) for path in exclude_drawn or []]),
                "threads": len(already),
                "eligible_threads_in_them": len(
                    [row for row in eligible if (row["store_file"], row["thread_root"]) in already]
                ),
            },
            "union_removed": len(eligible) - len(kept),
            "union_rule": "the two exclusions OVERLAP — the two @matusi_ukr threads of holdout-40"
            " are in both — so the population is `eligible − union`, never `eligible − a − b`",
            "eligible_after": len(kept),
            "eligible_after_ids_sha256": ids_sha256(kept),
        }
        if (drop_paused or exclude_drawn)
        else None
    )

    strata = {}
    for stratum in ("currency", "decimal_only"):
        strata[stratum] = draw([r for r in kept if r["stratum"] == stratum], stratum, arms)

    return {
        **({"exclusions": exclusions} if exclusions else {}),
        "contract": "docs/PHASE-promo-pulse-1.md S2 · docs/plans/promo-pulse-1.md S7 (K7)",
        "ruling": "operator 2026-08-30: «Все 678, дро 20/20 по типу» —"
        " docs/reviews/2026-08-30-plan-promo-pulse-1.md, SP-0 q3"
        if exclusions is None
        else leg["ruling"],
        "predicate": {
            "name": "retail_census.PRICE_BRANCHES",
            "branches": {name: pattern.pattern for name, pattern in sorted(PRICE_BRANCHES.items())},
            "join": "comment.parent_msg_id == post.msg_id, both as strings",
            "same_instrument_as": "scripts/promo_comment_yield.py",
        },
        "strata": {
            "currency": f"the post's text matches any of {', '.join(CURRENCY_BRANCHES)}",
            "decimal_only": "it matches the `decimal` branch and none of the currency ones",
            "why": "two thirds of the population match on `decimal` alone, which also fires on a"
            " DATE. The ruling keeps the whole population and makes the split a stratum, so"
            " per-stratum agreement is a reading beside the bars instead of a cut nobody can see.",
        },
        "seed": SEED,
        "seeded_per_stratum": f"random.Random(f'{SEED}:<stratum>') —"
        " .claude/rules/registrations-and-draws.md",
        "quotas": arms,
        "population": {
            "threads": len(population),
            "ids_sha256": ids_sha256(population),
            "root": "data/raw — the FROZEN v1 archive, read v1-only on purpose",
            "why_not_the_union": "SP-4 ruling (a) makes `data/raw_r2/` the live root and every"
            " other reader takes v1 \u222a r2. This one does not: the holdout is frozen at the"
            " draw and its population has to be frozen too, so a top-up landing between two runs"
            " cannot move 678/488 under it (plan \u00a75.14).",
            "provenance": {
                "raw_v1_baseline.sha256": _sha256(BASELINE),
                "verify": "shasum -c results/raw_v1_baseline.sha256 \u2014 six files, all OK",
                "means": "the six pinned store files were the bytes this draw read; the baseline"
                " is the only durable proof, because `data/` is gitignored",
            },
            "by_stratum": {
                stratum: len([r for r in population if r["stratum"] == stratum])
                for stratum in ("currency", "decimal_only")
            },
            "by_channel": {
                channel: len([r for r in population if r["channel"] == channel])
                for channel in sorted({r["channel"] for r in population})
            },
            "from_channels_r2_stopped_collecting": len(
                [r for r in population if r["from_a_channel_r2_stopped_collecting"]]
            ),
        },
        "queue_rule": {
            "spec": "SPEC 3.19 — a text-less comment leaves the INFERENCE QUEUE from the next paid"
            " cycle. A queue rule, never a deletion: «the volume of wordless reactions is itself a"
            " signal», so the count is printed beside every distribution over comments.",
            "wordless_comments": wordless,
            "comments": sum(row["n_comments"] for row in population),
            "threads_with_nothing_but_wordless_comments": len(silent),
            "eligible_threads": len(eligible),
            "eligible_ids_sha256": ids_sha256(eligible),
        },
        "draw": strata,
        "could_not_reach": {
            "channels_outside_the_two_that_carry_the_population": "the draw is stratified by"
            " BRANCH, not by channel: 98% of the population is @msuaaaa and @VARUS_channel, and"
            " channel quotas would have put zero threads in seven channels across both draws."
            " Channel is a recorded field on every drawn thread instead."
            if exclusions is None
            else "the draw is stratified by BRANCH, not by channel, and after the exclusions above"
            " what is left is almost entirely @msuaaaa and @VARUS_channel — the two channels the"
            " product actually collects. Channel is a recorded field on every drawn thread instead.",
            "threads_with_nothing_but_wordless_comments": len(silent),
        },
    }


def parse_arms(text: str) -> dict[str, int]:
    """`dev=20,holdout=20` → the quota per stratum per arm, in the order the arms are written."""
    arms = {}
    for one in text.split(","):
        name, _, count = one.partition("=")
        if not name.strip() or not count.strip().isdigit():
            raise SystemExit(f"--arms {text!r}: each arm is `name=N`, comma separated")
        arms[name.strip()] = int(count)
    return arms


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument(
        "--arms",
        default="dev=20,holdout=20",
        help="the arms this draw owes and each one's quota PER STRATUM, in order",
    )
    parser.add_argument(
        "--exclude-drawn",
        type=Path,
        action="append",
        help="an earlier draw record whose threads are already spent and leave the population;"
        " repeated once per earlier draw (draw 3 names both)",
    )
    parser.add_argument(
        "--drop-paused",
        action="store_true",
        help="threads of channels with `collect: false` in registry r2 leave the population",
    )
    args = parser.parse_args(argv)

    record = build(
        parse_arms(args.arms),
        exclude_drawn=args.exclude_drawn,
        drop_paused=args.drop_paused,
    )
    args.out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    population = record["population"]
    print(f"population {population['threads']} threads — {population['by_stratum']}")
    print(
        f"queue rule: {record['queue_rule']['wordless_comments']} wordless of"
        f" {record['queue_rule']['comments']} comments;"
        f" {record['queue_rule']['threads_with_nothing_but_wordless_comments']} threads dropped,"
        f" {record['queue_rule']['eligible_threads']} eligible"
    )
    if "exclusions" in record:
        gone = record["exclusions"]
        print(
            f"exclusions: {gone['paused_channels']['eligible_threads_in_them']} eligible in paused"
            f" channels + {gone['already_drawn']['eligible_threads_in_them']} already drawn ="
            f" {gone['union_removed']} removed (they overlap), {gone['eligible_after']} left"
        )
    for stratum, block in sorted(record["draw"].items()):
        owed = " · ".join(f"{arm} {n}" for arm, n in record["quotas"].items())
        print(f"  {stratum:<13} eligible {block['eligible']:>4} → {owed}")
    where = args.out.relative_to(REPO_ROOT) if args.out.is_relative_to(REPO_ROOT) else args.out
    print(f"wrote {where}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
