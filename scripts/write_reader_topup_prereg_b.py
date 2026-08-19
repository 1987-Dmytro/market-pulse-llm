#!/usr/bin/env python3
"""`results/reader_topup_prereg_b.json` — attempt B, and the ONE block it is allowed to change.

Attempt A's registration stands with its verdict: its full-pass gate returned STOP at the first
reading and the pod was deleted on it (`docs/reports/reader-topup.md`). The operator ruled the
corrected estimator and a second attempt on 2026-08-19. This record is built FROM attempt A's and
**refuses unless the only things that moved are the gate, the model it needs, and this record's own
identity** — so «nothing but the projector changed» is a check and not a sentence.

The correction: attempt A projected `max(unread units ÷ read, unread payable ÷ read payable) ×
measured`. Attempt B projects each unread unit at its OWN size through the line
`results/reader_topup_projection.json` fitted on 26 v5b units, calibrated by `max(measured ÷
fitted(read), 1.0)`. Both of A's legs stay in the gate's output, reported and not binding.

    PYTHONPATH=src python3.11 scripts/write_reader_topup_prereg_b.py
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import window_summary_5c2 as summary  # noqa: E402

ATTEMPT_A = REPO_ROOT / "results" / "reader_topup_prereg.json"
PROJECTION = REPO_ROOT / "results" / "reader_topup_projection.json"
RUN = REPO_ROOT / "results" / "reader_topup_run.json"
OUT_NAME = "results/reader_topup_prereg_b.json"

MAY_MOVE = {
    ".attempt",
    ".go_no_go.gates.2_full_pass",
    ".money.arithmetic.model",
    ".money.arithmetic.the_names_are_the_consumers",
    ".producer.script",
    ".producer.sha256",
    ".supersedes",
    ".frozen_when_the_pod_exists",
}
"""Every path attempt B is allowed to differ from attempt A on. Anything else — a threshold, the
cap, a unit, a sha, the population — is a change nobody ruled, and :func:`assert_only_the_gate_moved`
refuses it. The list is the diff stated in advance, which is the only kind that can be checked."""


def read(path: Path) -> dict:
    return json.loads(summary.read_text_or_refuse(path))


def flat(node, prefix: str = ""):
    if isinstance(node, dict):
        for key, value in node.items():
            yield from flat(value, f"{prefix}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from flat(value, f"{prefix}[{index}]")
    else:
        yield prefix, node


def assert_only_the_gate_moved(older: dict, newer: dict) -> list[str]:
    """Every path that differs, held against the list above — in BOTH directions."""
    left, right = dict(flat(older)), dict(flat(newer))
    moved = sorted(
        {key for key in left.keys() & right.keys() if left[key] != right[key]}
        | (set(left) ^ set(right))
    )
    unexpected = [
        key
        for key in moved
        if not any(
            key == one or key.startswith(one + ".") or key.startswith(one + "[") for one in MAY_MOVE
        )
    ]
    if unexpected:
        raise SystemExit(
            f"attempt B differs from attempt A on {len(unexpected)} paths nobody ruled:"
            f" {unexpected[:6]}. The ruling was the ESTIMATOR — stop and report."
        )
    return moved


def build() -> tuple[dict, list[str]]:
    record = read(ATTEMPT_A)
    model = read(PROJECTION)["instrument"]["model"]
    spent = sum(float(one.get("billed_usd") or 0) for one in read(RUN)["segments"])

    record["attempt"] = (
        "ATTEMPT B. Attempt A billed"
        f" ${spent:.6f} over two segments and its own gate STOPped it; this attempt inherits the"
        " step's cap, its ledger and its run record, so the segment it opens is the third and last"
        " the recovery clause allows. One attempt, one cap, and no third registration"
    )
    record["supersedes"] = {
        "record": summary.rel(ATTEMPT_A),
        "sha256": summary.sha256_of(ATTEMPT_A),
        "why": (
            "its full-pass gate returned STOP at the first reading, on a run whose own measurement"
            " (77.5 s against a fitted 80.4 s) confirms the projection it was priced on. The gate"
            " was honoured and the pod deleted; the operator ruled the corrected estimator"
            " afterwards, in the open, and this is it"
        ),
        "billed_before_this_attempt_usd": round(spent, 6),
    }
    record["money"]["arithmetic"]["model"] = {
        **model,
        "borrowed_from": summary.rel(PROJECTION),
        "used_by": "scripts/read_threads_reader_topup.py::projection",
        "rule": (
            "each unread unit is projected at its OWN size, `intercept + slope × payable`, and the"
            " sum is calibrated by max(measured ÷ fitted(read units), 1.0). The floor is the"
            " conservatism: a pod faster than the fit is projected at the fit"
        ),
    }
    record["go_no_go"]["gates"]["2_full_pass"] = {
        "rule": (
            "`elapsed + max(measured ÷ fitted(read), 1.0) × Σ fitted(unread) ≤ usable`, where"
            " `fitted` is the registered line over a unit's payable comments. Attempt A's two legs"
            " — unread units ÷ read and unread payable ÷ read payable — are still COMPUTED and"
            " printed beside it, and neither binds"
        ),
        "why_it_changed": (
            "attempt A's rule extrapolates the units read across all 132, and this population's"
            " units carry 1 to 16 payable comments with a median of 2, ordered expensive-first. Its"
            " first reading therefore projected the largest unit onto the whole pack: 10 156 s"
            " against a 6 049 s fit, STOP at n=1, by construction rather than by chance. The"
            " property attempt A's rule needs — units of roughly one size — is written down here"
            " because it is what stopped holding"
        ),
        "scored_by": "scripts/read_threads_reader_topup.py::projection, through the swap onto v5",
        "conservatism": (
            "three ways. The calibration floors at 1.0 so a fast start cannot lengthen the run; the"
            " line over-predicts its own out-of-sample check by 1.08×; and the units are still"
            " ordered expensive-first, so the calibration is measured on the slowest units first"
        ),
    }
    record["frozen_when_the_pod_exists"] = sorted(
        set(record["frozen_when_the_pod_exists"]) | {OUT_NAME}
    )
    record["producer"]["script"] = "scripts/write_reader_topup_prereg_b.py"
    moved = assert_only_the_gate_moved(read(ATTEMPT_A), record)
    return record, moved


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    record, moved = build()
    record["producer"]["sha256"] = summary.sha256_of(Path(__file__))
    out = args.outdir / OUT_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {OUT_NAME}  sha256 {summary.sha256_of(out)[:16]}…")
    print(f"\nattempt B differs from attempt A on {len(moved)} paths, all of them ruled:")
    for path in moved:
        print(f"  {path}")
    print(
        f"\nthe cap is the STEP's and unchanged: ${record['money']['cap_usd_all_in']:.2f}, of which"
        f" ${record['supersedes']['billed_before_this_attempt_usd']:.6f} is already billed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
