#!/usr/bin/env python3
"""Turn the operator's filled audit CSVs into a per-head ceiling (SPEC amendment 3.7, 4.5a).

Built with the pack, run only once the CSVs come back. It reads the rulings, the
sealed key and the committed manifest, and prints — with its assumptions, because
the formula is subject to team-lead review before any verdict is ingested:

- how often gold is wrong where the model disagreed with it (fully observed),
- how often gold is wrong where nobody disagreed (a control sample, extrapolated),
- **two ceilings, in two different units**, and they are not interchangeable:

  ``metric units`` re-scores a simulated perfect model through
  ``market_pulse.scorer`` — the same judge the gates use — flipping only the rows
  the operator ruled for the model. Comparable to a G1a/G1c bar, and an **upper
  bound**: it cannot see the agreement stratum's errors.

  ``accuracy units`` is the share of rows a perfect model keeps once *both*
  strata are counted. It is the number that answers "is 0.98 reachable", and it
  is **not** comparable to an F1 bar: a gold error on a rare class costs macro-F1
  far more than it costs accuracy.

    python3.11 scripts/audit_ceiling.py

Every path it reads comes out of the manifest, so the run is described by one
committed file. It refuses while any verdict cell is empty, and it never prints
the key's mapping row by row: the blinding is reusable, and a later re-audit of
the same rows must not be contaminated by this run's output.
"""

import argparse
import csv
import json
import sys
from collections import Counter
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed

from market_pulse import audit, scorer  # noqa: E402
from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

MANIFEST = REPO_ROOT / "results" / "audit_45a_manifest.json"

ASSUMPTIONS = """ASSUMPTIONS — this is a formula, not a measurement of the truth
  1. A perfect model outputs the truth, so it loses exactly the rows where gold
     is not the truth. The ceiling is 1 minus that share.
  2. Disagreements are fully observed: gold-wrong there is a count.
  3. Agreements are seen only through the control sample, so their gold-error
     share is EXTRAPOLATED over the whole stratum. That stratum is most of the
     test set and the sample is a few dozen rows — the sensitivity line below
     shows what one more `incorrect` does to the number.
  4. Ambiguous rows are a band, never a point: a perfect model may lose all of
     them (low) or none (high).
  5. WHAT THIS CANNOT SEE: rows where the model and gold are wrong the SAME way
     and that the control sample did not draw. Nothing flags such a row, and the
     only estimate of them is the control's `incorrect` rate in (3)."""

CLOSING = """The two ceilings are in different units and do not bound each other. A macro-F1
bar and an accuracy share are not comparable: put the target in the head's own
unit before reading either against 0.98."""


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def read_csv(path: Path, columns: tuple[str, ...]) -> list[dict]:
    """A pack CSV, or a refusal naming the columns that are not the sealed ones.

    A spreadsheet round-trip is how a column actually appears — an autofilled
    helper, a stray paste, a re-export that renames one. Reading by name would
    not notice, and an unknown column can hold anything, including an attribution
    or a second opinion that the ingestion would silently ignore.
    """
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        found = tuple(reader.fieldnames or ())
        if unexpected := [name for name in found if name not in columns]:
            raise SystemExit(
                f"{path.name}: unknown column(s) {unexpected}. The pack's columns are"
                f" {list(columns)} and they are part of the sealed artifact — remove the extra"
                " column, or rebuild the pack if it belongs there."
            )
        if missing := [name for name in columns if name not in found]:
            raise SystemExit(f"{path.name}: missing column(s) {missing} — this is not the pack")
        return list(reader)


def check_vocabulary(rows: list[dict], vocabulary: tuple[str, ...]) -> None:
    for row in rows:
        if row["verdict"].strip() not in vocabulary:
            raise SystemExit(
                f"{row['head']}:{row['id']}: verdict {row['verdict']!r} is not one of {vocabulary}"
            )


def rulings(pack: Path, key: dict, heads: list[str]) -> tuple[dict[str, list[dict]], list[dict]]:
    """The filled pack, checked against the key — or a refusal naming the defect."""
    control = read_csv(pack / "control.csv", audit.CONTROL_COLUMNS)
    disagreements: dict[str, list[dict]] = {head: [] for head in heads}
    for name in sorted({audit.CSV_OF[head] for head in heads}):
        for row in read_csv(pack / name, audit.COLUMNS):
            entry = key.get(f"{row['head']}|{row['id']}")
            if entry is None:
                raise SystemExit(f"{name}: {row['id']} ({row['head']}) is not in the key")
            if (row["label_A"], row["label_B"]) != (entry["label_A"], entry["label_B"]):
                raise SystemExit(
                    f"{name}: the labels of {row['id']} differ from the key. The CSV was edited"
                    " beyond its verdict column, so the blinding no longer maps back."
                )
            disagreements[row["head"]].append(row)

    ruled = [row for rows in disagreements.values() for row in rows]
    empty = [
        f"{row['head']}:{row['id']}" for row in (*ruled, *control) if not row["verdict"].strip()
    ]
    if empty:
        raise SystemExit(
            f"{len(empty)} verdict cells are still empty ({', '.join(empty[:5])} ...)."
            " A ceiling computed over a half-filled pack is a ceiling of nothing."
        )
    check_vocabulary(ruled, audit.VERDICTS)
    check_vocabulary(control, audit.CONTROL_VERDICTS)
    if len(key) != len(ruled):
        raise SystemExit(
            f"the key holds {len(key)} rows and the pack {len(ruled)} — a row was added or"
            " removed, so the pack is not the one that was sealed."
        )
    return disagreements, control


def universe(head: str, rows: dict, slice_ids: list[str]) -> list[dict]:
    """The head's row population — the G1b slice is 44 ids, not the whole holdout."""
    if head == "sarcasm_pair":
        wanted = set(slice_ids)
        return [row for row in rows["sarcasm_holdout"] if row["id"] in wanted]
    return rows[audit.INPUT_OF[head]]


def metric_ceiling(head, rows, predicted, aliases, gold_wrong, slice_ids) -> tuple[str, float]:
    """A perfect model's score in the head's OWN metric, through the scorer.

    "Perfect" means: gold everywhere except the rows the operator ruled for the
    model, where gold is wrong and the truth is what the model said. Scored
    against the unrepaired gold, which is what a gate would do — so this is the
    ceiling the disagreement stratum alone imposes, and an upper bound.
    """
    population = universe(head, rows, slice_ids)
    perfect = [
        predicted[audit.INPUT_OF[head]][row["id"]] if row["id"] in gold_wrong else row
        for row in population
    ]
    if head == "sentiment":
        return "macro-F1", scorer.sentiment_macro_f1(
            [row["sentiment"] for row in population],
            [row["sentiment"] for row in perfect],
            [row["language"] for row in population],
        )["overall"]
    if head == "intents":
        return "micro-F1", scorer.intents_micro_f1(
            [row["intents"] for row in population], [row["intents"] for row in perfect]
        )
    if head == "post_type":
        return "macro-F1", scorer.launch_detection_macro_f1(
            [row["post_type"] for row in population], [row["post_type"] for row in perfect]
        )
    if head == "brands":
        return "F1", scorer.brand_extraction_f1(
            [row["brands"] for row in population], [row["brands"] for row in perfect], aliases
        )
    pair = ("sentiment", "sarcasm")
    return "fix-rate", scorer.sarcasm_slice_fix_rate(
        slice_ids,
        {row["id"]: {key: row[key] for key in pair} for row in population},
        {
            row["id"]: {key: answer[key] for key in pair}
            for row, answer in zip(population, perfect, strict=True)
        },
    )["rate"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    args = parser.parse_args(argv)

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    pack = REPO_ROOT / manifest["pack_path"]
    key_path = REPO_ROOT / manifest["key_path"]
    digest = sha256(key_path.read_bytes()).hexdigest()
    if digest != manifest["key_sha256"]:
        raise SystemExit(
            f"{key_path}: sha256 {digest}, manifest says {manifest['key_sha256']}. The key was"
            " regenerated or edited — the blinding it describes is not the one the operator ruled."
        )
    key = json.loads(key_path.read_text(encoding="utf-8"))
    heads = list(manifest["strata"])
    disagreements, control = rulings(pack, key, heads)

    frozen = REPO_ROOT / manifest["frozen_path"]
    rows = {
        name: load_jsonl(frozen / f"{name}.jsonl")
        for name in {audit.INPUT_OF[head] for head in heads} | {"sarcasm_holdout"}
        if (frozen / f"{name}.jsonl").exists()
    }
    predicted: dict[str, dict[str, dict]] = {}
    for row in load_jsonl(REPO_ROOT / manifest["predictions_path"]):
        predicted.setdefault(row["input"], {})[row["id"]] = row["pred"]
    aliases = watchlist_aliases(load_registry(REPO_ROOT / "config" / "registry.yaml").watchlist)
    slice_ids = (
        json.loads((REPO_ROOT / manifest["slice_path"]).read_text(encoding="utf-8"))["ids"]
        if "sarcasm_pair" in heads
        else []
    )
    tally = Counter((row["head"], row["verdict"].strip()) for row in control)

    print(f"audit ceiling — arm {manifest['arm']} @ {manifest['arm_record_timestamp']}")
    print(f"pack {manifest['pack_path']} · key sha256 verified\n")
    print(ASSUMPTIONS, "\n")

    for head in heads:
        stratum = manifest["strata"][head]
        ruled = disagreements[head]
        gold_wrong = {
            row["id"]
            for row in ruled
            if row["verdict"].strip() == key[f"{head}|{row['id']}"]["model_column"]
        }
        ambiguous = sum(1 for row in ruled if row["verdict"].strip() == "ambiguous")
        control_n = sum(tally[head, verdict] for verdict in audit.CONTROL_VERDICTS)
        incorrect, control_ambiguous = tally[head, "incorrect"], tally[head, "ambiguous"]
        total = stratum["scoreable"]
        estimate = audit.ceiling(
            total, len(ruled), len(gold_wrong), ambiguous, control_n, incorrect, control_ambiguous
        )
        unit, exact = metric_ceiling(head, rows, predicted, aliases, gold_wrong, slice_ids)

        print(f"--- {head} ({audit.GATE_OF[head]}, {stratum['input']}, n={total})")
        print(
            f"  disagreements n={len(ruled):<4} gold wrong {len(gold_wrong):<4}"
            f" model wrong {len(ruled) - len(gold_wrong) - ambiguous:<4} ambiguous {ambiguous}"
        )
        print(
            f"  agreements    n={estimate['agreement_n']:<4} control {control_n}:"
            f" incorrect {incorrect}, ambiguous {control_ambiguous}"
            f" -> gold-error {incorrect / control_n:.3f} extrapolated over the stratum"
        )
        print(f"  ceiling, {unit} units (disagreements only, UPPER BOUND): {exact:.4f}")
        print(
            f"  ceiling, accuracy units (both strata): {estimate['low']:.4f}"
            f" .. {estimate['high']:.4f}  [ambiguous lost .. kept]"
        )
        sensitivity = " · ".join(
            f"{k}->"
            + format(
                audit.ceiling(
                    total, len(ruled), len(gold_wrong), ambiguous, control_n, k, control_ambiguous
                )["high"],
                ".4f",
            )
            for k in range(max(0, incorrect - 1), min(control_n, incorrect + 1) + 1)
        )
        print(f"  sensitivity, control incorrect -> accuracy ceiling (high): {sensitivity}\n")

    print(CLOSING)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
