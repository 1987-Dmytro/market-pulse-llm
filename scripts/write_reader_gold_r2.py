#!/usr/bin/env python3
"""`results/reader_gold_w1_r2.json` — the gold under the sitting's vocabulary adjudication.

**One ruling, one word, twelve cells.** `docs/REFERENCE-signals-w1.md` scores gold rows on
«категория»; the taxonomy the operator ratified on 2026-08-15 spells the same class
«категория_личное». The reader sitting of 2026-08-16 adjudicates them as the SAME class (ruling 4)
and fixes how that is applied: the gold is re-derived as a NAMED revision, the reference file itself
is NOT edited, and the ruling lives as its own record.

**Derived and not retyped.** Every row, every msg-id, every quote check and the whole reachability
block come from :mod:`write_reader_gold` — this producer imports it, builds v1's record and rewrites
the twelve `subject_type` cells that read «категория». Nothing else moves, which is a property of
the code: the walk keys on the FIELD NAME and the exact value, so a paraphrase in a `reading` or a
`derivation` sentence carrying the same word is not touched, and the count is asserted rather than
hoped for.

**v1 stays exactly where it is.** `results/reader_gold_w1.json` is pinned by
`results/prereg_reader_probe.json` and `results/prereg_reader_probe_v2.json`, and probe-a's and
probe-b's verdicts were scored against it. A revision that edited it would move two sealed records
for a reading of one word ([[the_old_record_with_one_field_replaced]]).

    PYTHONPATH=src python3 scripts/write_reader_gold_r2.py
    PYTHONPATH=src python3 scripts/write_reader_gold_r2.py --out /tmp/again.json   # the pair
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gate_census_w1 as census  # noqa: E402
import reader_population as population  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402
import write_reader_gold as v1  # noqa: E402

OUT = REPO_ROOT / "results" / "reader_gold_w1_r2.json"
RULING = REPO_ROOT / "knowledge" / "decisions" / "reader-sitting-16-08.md"

COLLAPSED = "категория"
RATIFIED = "категория_личное"
CELLS = 12
"""How many `subject_type` cells the reference's word reaches — four flagship signals and eight
per-comment rows, counted on v1's own record before this revision was written.

A literal and not a length: without it a thirteenth cell arriving under a later gold edit would be
relabelled silently, and «every cell» would stop being a claim anybody checked."""


def relabel(node, path: str = "") -> list[str]:
    """Rewrite every `subject_type` cell reading :data:`COLLAPSED`, and return where each one was.

    Typed, not textual. A `str.replace` over the document would also hit the sentences that DISCUSS
    the word — `derivation.per_comment_rule`, the reference's own `reading_reference` strings — and
    those are the team lead's prose, which this revision has no ruling to touch.
    """
    found = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "subject_type" and value == COLLAPSED:
                node[key] = RATIFIED
                found.append(f"{path}.{key}")
            else:
                found += relabel(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            found += relabel(value, f"{path}[{index}]")
    return found


def build() -> dict:
    record = v1.build(
        population.population(),
        v1.evidence_index(),
        census.raw_posts(),
        population.window(),
        population.gate(),
    )
    cells = relabel(record)
    if len(cells) != CELLS:
        raise SystemExit(
            f"the ruling reaches {len(cells)} `subject_type` cells and this revision is registered"
            f" for {CELLS}: {cells}. A gold that grew a cell is a gold whose relabelling nobody"
            " looked at — stop and report."
        )
    record["revision"] = {
        "name": "r2",
        "supersedes": {
            "record": summary.rel(v1.OUT),
            "sha256": summary.sha256_of(v1.OUT),
            "untouched": (
                "v1 is not edited and is not superseded as EVIDENCE: results/prereg_reader_probe"
                ".json and results/prereg_reader_probe_v2.json pin its sha and probe-a's and"
                " probe-b's bars were scored against it. This file is what a run AFTER the"
                " 2026-08-16 sitting scores against"
            ),
        },
        "ruling": {
            "record": summary.rel(RULING),
            "which": "ruling 4 — the vocabulary adjudication",
            # verbatim from the record above, whitespace-normalised, and grepped back to it by
            # tests/test_reader_gold_r2.py — a ruling quoted from memory is a ruling nobody checked
            "operator_words": [
                "The sitting adjudicates them as **the same class**",
                "the gold is re-derived as a NAMED revision (r2) in reader-v3",
                "the reference file itself is NOT edited",
            ],
            "reading": (
                "«категория» and «категория_личное» are ONE class. The reference states the first,"
                " the ratified taxonomy the second, and probe-b measured the cost of the"
                " disagreement in production: msg 21599 was scored gold «категория» against a"
                " reader that answered «категория_личное», and collapsing the two moved bar 4 from"
                " 0.357 to 0.429 as run and from 0.429 to 0.643 coerced"
            ),
        },
        "source": {
            summary.rel(v1.REFERENCE): summary.sha256_of(v1.REFERENCE),
            "rule": (
                "the reference file is NOT edited — pins do not move for a vocabulary reading"
                " (ruling 4). Every row, msg-id, quote check and reachability cell below is v1's,"
                " rebuilt from this file by scripts/write_reader_gold.py"
            ),
        },
        "change": (
            f"every `subject_type` cell reading «{COLLAPSED}» is re-labelled «{RATIFIED}»."
            " Nothing else: same rows, same msg-ids, same reachability block, same conflicts. The"
            " walk keys on the field name and the exact value, so prose that discusses the word is"
            " untouched"
        ),
        "cells": sorted(cells),
    }
    # v1's producer is BORROWED and not replaced: it built every row in this file, and a
    # `producer.sha256` still pointing at it would name a script that never wrote this record
    wrote_the_rows = record["producer"]
    record["producer"] = {
        "script": summary.rel(Path(__file__)),
        "sha256": summary.sha256_of(Path(__file__)),
        "borrowed": {
            wrote_the_rows["script"]: wrote_the_rows["sha256"],
            **wrote_the_rows["borrowed"],
        },
    }
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    record = build()
    args.out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {summary.rel(args.out)}  sha256 {summary.sha256_of(args.out)[:16]}…")
    print(f"  {len(record['revision']['cells'])} cells «{COLLAPSED}» -> «{RATIFIED}»")
    for cell in record["revision"]["cells"]:
        print(f"    {cell}")
    left = json.dumps(record, ensure_ascii=False).count(f'"subject_type": "{COLLAPSED}"')
    print(f"  `subject_type` cells still reading «{COLLAPSED}»: {left}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
