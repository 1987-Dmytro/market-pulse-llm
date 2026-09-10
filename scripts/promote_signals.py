#!/usr/bin/env python3
"""s2-promote — the threads the paid dev loop already READ, into `results/promo_signals/`. $0.

    PYTHONPATH=src python3.11 scripts/promote_signals.py
    make tick        # promotes what this wrote into the six promo tables

**Nothing is read again here.** The 120 threads of the three dev sets were bought under the four
pins of `d598573` (dev-40 + dev-2 in `results/promo_dev40_iter5.jsonl`, holdout-2 in
`results/promo_holdout2.jsonl`) and their answers have been on disk since. What was missing is the
step between the answer and the product: `results/promo_signals/` did not exist, so `make tick`
promoted nothing, `screen.feed` was `[]` and the screen said the leg had not been bought — bought
and not on the screen, which is a claim about us dressed as a claim about the market.

**The records are the loop leg's own.** Every one comes out of
`scripts/promo_p1_apply.py :: screened` — the generator the loop leg of
`results/grade_promo_loop_readings.json` grades — so the rows this file promotes and the rows that
record scores are the same rows, built once. A second spelling of parse → screen → record would
measure a third thing ([[a_moved_guard_that_left_its_copy]]).

**The PRODUCT's population, off the LIVE registry.** A thread of a channel the registry marks
`collect: false` is not written and is counted by name: the same rule `tick.not_collected` applies
to the position rows, read every run and never frozen into this directory
([[a_shrunk_population_is_a_test_change]]).

Two runs write byte-identical files: the records carry no clock, and their keys are sorted.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

import promo_p1_apply  # noqa: E402
import tick  # noqa: E402
from market_pulse import promo_prompts  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

REGISTRY = REPO_ROOT / "config" / "registry.yaml"


def write(record: dict, out: Path) -> Path:
    """One thread, in the file name `tick.signal_records` globs: `<channel>_<root>.json`."""
    path = out / f"{record['channel']}_{record['thread_root']}.json"
    path.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=tick.SIGNALS)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    args = parser.parse_args(argv)

    registry = load_registry(args.registry)
    excluded = tick.not_collected(registry)
    brand_ids = {brand.brand_id for brand in registry.watchlist}
    vocabulary = promo_prompts.vocabulary()

    args.out.mkdir(parents=True, exist_ok=True)
    written: Counter = Counter()
    paused: list[str] = []
    for name, spec in promo_p1_apply.SETS.items():
        for _item, _answer, record in promo_p1_apply.screened(spec, brand_ids, vocabulary):
            if record["channel"] in excluded:
                paused.append(f"{name} {record['channel']}/{record['thread_root']}")
                continue
            write(record, args.out)
            written[name] += 1
        print(f"{name:<6} {written[name]:>3} threads written")
    print(
        f"total  {sum(written.values()):>3} threads in {tick.rel(args.out)}"
        f" · {len(paused)} left out — their channel is `collect: false` in"
        f" {tick.rel(args.registry)}: {', '.join(sorted(paused)) or 'none'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
