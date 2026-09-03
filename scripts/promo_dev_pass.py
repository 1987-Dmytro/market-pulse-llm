#!/usr/bin/env python3
"""S9 — the dev-40 pass over the promo-signal instrument. $0 until `--run` exists.

The draw (`results/promo_threads_draw.json`, seed 42) named 40 dev threads; the team lead labelled
every comment of them WITH TEXT in `docs/labels-promo-dev.jsonl`. This script renders what the model
reads for those threads, and turns one answer back into the row shape the grader scores.

**The render is shown before anything is bought.** Ruling 03.09 asks for the RENDERED prompt of one
dev thread at $0, so the team lead reads the law the model will actually obey rather than the
module's source. `--render` is that command.

**The answer is joined back per comment, not per signal.** Gold is one row per comment with a
`signal_types` LIST; the model answers with an `about` row per comment and free-standing `signal`
rows. `predicted_rows` joins them on `msg_id` — a comment the model said nothing about produces no
row and the grader counts it as a miss, which is what
[[an_abstention_is_an_answer]] asks for: silence is scored, never dropped.

**The price of iteration 1 is a BORROWED bound and the record says so.** No rate for THIS instrument
exists — `results/measurements.jsonl` has no row for the promo-signal prompt — so `--dry-run` prices
the leg at the nearest measured thing (`pass2_r2_seconds_per_thread`, 23.76 s over 75 cooled threads,
thinking off) and marks it BORROWED: a different prompt, a different pod, a different transport
([[a_rate_is_a_property_of_the_pod]], [[the_smokes_rate_carries_the_smokes_transport]]). It bounds
the ask; the smoke replaces it before anything is bought.

    python3.11 scripts/promo_dev_pass.py --render 6009 --channel @VARUS_channel
    python3.11 scripts/promo_dev_pass.py --dry-run          # $0: the corpus, its sizes, the bound
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

import draw_promo_threads as draw  # noqa: E402

from market_pulse import promo_prompts  # noqa: E402

DRAW = REPO_ROOT / "results" / "promo_threads_draw.json"
CODEBOOK = REPO_ROOT / "docs" / "CODEBOOK-promo-signals.md"
GOLD = REPO_ROOT / "docs" / "labels-promo-dev.jsonl"
MEASUREMENTS = REPO_ROOT / "results" / "measurements.jsonl"
RATE_RECORD = REPO_ROOT / "results" / "srv2d_cost.json"
PREP = REPO_ROOT / "results" / "promo_dev40_prep.json"

BORROWED_RATE = "pass2_r2_seconds_per_thread"
"""The nearest MEASURED seconds-per-thread in the house — READER, thinking off, 75 cooled threads.
Named, never typed: :func:`borrowed_rate` reads it out of `results/measurements.jsonl` and carries
the row's own `instrument` and `n` into the record, so a reader sees what was borrowed from where."""


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def dev_threads(path: Path = DRAW) -> list[dict]:
    """The draw's dev rows, both strata, in the record's own order."""
    body = json.loads(path.read_text(encoding="utf-8"))
    return [row for stratum in sorted(body["draw"]) for row in body["draw"][stratum]["dev"]]


def thread_of(row: dict) -> tuple[str, list[dict]]:
    """One thread's post text and its comments, from the frozen v1 archive the draw read.

    The join is the draw's own — `parent_msg_id` against the post's `msg_id`, both as strings — so
    a thread rendered here is the thread that was drawn and labelled, not a re-derived neighbour.
    """
    stem, root = row["store_file"], str(row["thread_root"])
    posts = {str(one.get("msg_id")): one for one in draw.rows(draw.POSTS / f"{stem}.jsonl")}
    if root not in posts:
        raise SystemExit(f"{row['channel']} root {root}: no post in data/raw/posts/{stem}.jsonl")
    comments = [
        one
        for one in draw.rows(draw.COMMENTS / f"{stem}.jsonl")
        if str(one.get("parent_msg_id")) == root
    ]
    return posts[root].get("text") or "", comments


def render_thread(row: dict) -> str:
    post, comments = thread_of(row)
    return promo_prompts.render(row["channel"], row["thread_root"], post, comments)


def predicted_rows(row: dict, answer: dict) -> list[dict]:
    """One model answer → gold-shaped rows, one per comment the model placed."""
    types: dict[str, set] = {}
    for signal in answer.get("signals") or []:
        types.setdefault(str(signal.get("msg_id")), set()).add(signal.get("type"))
    return [
        {
            "channel": row["channel"],
            "thread_root": str(row["thread_root"]),
            "msg_id": str(one.get("msg_id")),
            "subject_type": one.get("subject_type"),
            "subject": one.get("subject"),
            "source": one.get("source"),
            "signal_types": sorted(types.get(str(one.get("msg_id")), set()), key=str),
        }
        for one in (answer.get("about") or [])
    ]


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def borrowed_rate() -> dict:
    """The named measurement row, or a refusal. A projection with no named rate projects nothing —
    `scripts/project_think_zero_shot.py:107`'s rule, applied to an instrument that has none yet."""
    for line in MEASUREMENTS.read_text(encoding="utf-8").splitlines():
        if line.strip() and (row := json.loads(line))["name"] == BORROWED_RATE:
            return row
    raise SystemExit(
        f"{BORROWED_RATE} is not in results/measurements.jsonl — this leg has no rate of its own"
        " and no rate to borrow, so it prices nothing. The smoke writes it."
    )


def prep() -> dict:
    """The dev-40 corpus as the model will read it, its sizes, and the ask BOUNDED, not priced."""
    rows = dev_threads()
    rate = borrowed_rate()
    usd_per_second = json.loads(RATE_RECORD.read_text(encoding="utf-8"))["rate"]["usd_per_second"]
    threads = []
    for row in rows:
        rendered = render_thread(row)
        threads.append(
            {
                "channel": row["channel"],
                "thread_root": str(row["thread_root"]),
                "stratum": row["stratum"],
                "n_comments": row["n_comments"],
                "n_wordless": row["n_wordless"],
                "chars": len(rendered),
                "extractor_version": promo_prompts.extractor_version(rendered),
            }
        )
    seconds = rate["value"] * len(threads)
    return {
        "phase": "promo-pulse-1 S9 — dev-40, the $0 half: what the model reads and what it bounds",
        "authority": "docs/reviews/2026-08-30-plan-promo-pulse-1.md «Ruling 03.09» — the prompt's"
        " law is re-rendered from the codebook BEFORE the first paid K8 run, and the RENDERED"
        " prompt is read at $0 before any pod exists",
        "law": {
            "codebook": rel(CODEBOOK),
            "codebook_sha256": sha256_of(CODEBOOK),
            "codebook_version": promo_prompts.codebook_version(),
            "vocabulary": promo_prompts.vocabulary(),
        },
        "gold": {"path": rel(GOLD), "sha256": sha256_of(GOLD), "lines": len(
            [one for one in GOLD.read_text(encoding="utf-8").splitlines() if one.strip()]
        )},
        "draw": {"path": rel(DRAW), "sha256": sha256_of(DRAW), "dev_threads": len(threads)},
        "corpus": {
            "threads": threads,
            "chars_total": sum(one["chars"] for one in threads),
            "chars_max": max(one["chars"] for one in threads),
            "distinct_renders": len({one["extractor_version"] for one in threads}),
        },
        "bound": {
            "is_a_bound_and_not_a_price": "this instrument has no measured rate. The seconds below"
            " are BORROWED from another prompt, another pod and another transport; the smoke"
            " measures this leg's own and the registration is written against THAT",
            "borrowed_from": {
                "name": rate["name"],
                "value": rate["value"],
                "unit": rate["unit"],
                "n": rate["n"],
                "max": rate["max"],
                "instrument": rate["instrument"],
                "measured_on": rate["measured_on"],
                "source": rate["source"],
            },
            "threads": len(threads),
            "seconds_at_the_borrowed_mean": round(seconds, 1),
            "seconds_at_the_borrowed_max": round(rate["max"] * len(threads), 1),
            "usd_per_second": usd_per_second,
            "usd_at_the_borrowed_mean": round(seconds * usd_per_second, 4),
            "usd_at_the_borrowed_max": round(rate["max"] * len(threads) * usd_per_second, 4),
            "boot_not_included": "a boot is the endpoint's, not the leg's — the registration adds"
            " it once at the corner it is measured at",
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", metavar="THREAD_ROOT")
    parser.add_argument("--channel", default=None, help="disambiguate a root two channels share")
    parser.add_argument("--dry-run", action="store_true", help="$0: the corpus, its sizes, the bound")
    parser.add_argument("--out", type=Path, default=PREP)
    args = parser.parse_args(argv)

    if args.dry_run:
        record = prep()
        args.out.write_text(
            json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        bound, corpus = record["bound"], record["corpus"]
        print(f"wrote {rel(args.out)}")
        print(f"  law           {record['law']['codebook']} sha {record['law']['codebook_sha256'][:16]}…")
        print(f"  corpus        {bound['threads']} dev threads · {corpus['chars_total']} chars ·"
              f" longest {corpus['chars_max']} · {corpus['distinct_renders']} distinct renders")
        print(f"  BORROWED rate {bound['borrowed_from']['name']} ="
              f" {bound['borrowed_from']['value']} s/thread (n={bound['borrowed_from']['n']},"
              f" max {bound['borrowed_from']['max']}) — another prompt, pod and transport")
        print(f"  bound         ${bound['usd_at_the_borrowed_mean']} at its mean ·"
              f" ${bound['usd_at_the_borrowed_max']} at its max, boot excluded — NOT a price")
        return 0

    if not args.render:
        parser.error("choose --render or --dry-run")

    found = [
        row
        for row in dev_threads()
        if str(row["thread_root"]) == str(args.render)
        and (args.channel is None or row["channel"] == args.channel)
    ]
    if len(found) != 1:
        raise SystemExit(
            f"--render {args.render}: {len(found)} dev threads match"
            f"{' in ' + args.channel if args.channel else ''} — name --channel to pick one"
        )
    rendered = render_thread(found[0])
    print(rendered)
    print()
    print(f"--- codebook_version  {promo_prompts.codebook_version()}")
    print(f"--- extractor_version {promo_prompts.extractor_version(rendered)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
