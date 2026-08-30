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


def draw(pool: list[dict], stratum: str) -> dict:
    """One stratum's 40, seeded with the stratum in the seed, split 20 dev / 20 holdout.

    Refuses rather than under-fills: a quota that cannot be met is a fact about the population and
    the team lead has to see it, not a shorter list that reads like a complete one.
    """
    owed = PER_STRATUM["dev"] + PER_STRATUM["holdout"]
    if len(pool) < owed:
        raise SystemExit(
            f"stratum {stratum!r} has {len(pool)} eligible threads and the draw owes {owed}"
            " — a quota that cannot be filled is a refusal, never a short draw"
        )
    ranked = {(row["store_file"], row["thread_root"]): i for i, row in enumerate(pool)}
    picked = random.Random(f"{SEED}:{stratum}").sample(pool, owed)
    dev, holdout = picked[: PER_STRATUM["dev"]], picked[PER_STRATUM["dev"] :]
    return {
        "eligible": len(pool),
        "dev": sorted(dev, key=lambda row: (row["store_file"], row["thread_root"])),
        "holdout": sorted(holdout, key=lambda row: (row["store_file"], row["thread_root"])),
        "dev_ranks": sorted(ranked[(r["store_file"], r["thread_root"])] for r in dev),
        "holdout_ranks": sorted(ranked[(r["store_file"], r["thread_root"])] for r in holdout),
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ids_sha256(rows_: list[dict]) -> str:
    """The population pinned BY ROW COUNT and by its ids, never by a date range read at run time."""
    blob = "\n".join(f"{r['store_file']}\x1f{r['thread_root']}" for r in rows_)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def build() -> dict:
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

    strata = {}
    for stratum in ("currency", "decimal_only"):
        strata[stratum] = draw([r for r in eligible if r["stratum"] == stratum], stratum)

    return {
        "contract": "docs/PHASE-promo-pulse-1.md S2 · docs/plans/promo-pulse-1.md S7 (K7)",
        "ruling": "operator 2026-08-30: «Все 678, дро 20/20 по типу» —"
        " docs/reviews/2026-08-30-plan-promo-pulse-1.md, SP-0 q3",
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
        "quotas": PER_STRATUM,
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
            " Channel is a recorded field on every drawn thread instead.",
            "threads_with_nothing_but_wordless_comments": len(silent),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)

    record = build()
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
    for stratum, block in sorted(record["draw"].items()):
        print(f"  {stratum:<13} eligible {block['eligible']:>4} → dev 20 · holdout 20")
    where = args.out.relative_to(REPO_ROOT) if args.out.is_relative_to(REPO_ROOT) else args.out
    print(f"wrote {where}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
