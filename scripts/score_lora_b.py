#!/usr/bin/env python3
"""`results/lora_b_verdict.json` — D4: the gate applied by the scorer, never by the eyeball.

**Nothing about the bar is new.** `scripts/score_pass1_probe.py`'s `bar_p1` is CALLED, once per arm,
with lora-b's own registration and that arm's evidence — so the comparison is still
`scorer.reader_comment_agreement` under probe-b's symmetric collapse, reached through exactly one
implementation. `scripts/read_pass1_probe.py`'s `ingest` is CALLED to turn each arm's raw replies
into evidence, with its EVIDENCE constant swapped for the arm's, so the parse the verdict reads is
the parse the probe's own path makes.

**What is this file's own** is the arm rule and the ablation. The gate is
`max(gold14(arm A), gold14(arm B)) ≥ 12 of 14`, ONE attempt, tie ships arm B — all three pre-named
in `results/prereg_lora_b.json`, and read out of it here rather than typed. The ablation table is
PAIRED per row against the base's SEALED verdict: the base is never re-run, so the three columns are
three readings of the same fourteen instances under the same prompt sha.

**An arm with no evidence file is not a zero.** A run that trained one arm, or one whose format
smoke killed an arm before its eval, has no reply for it — and a missing arm is reported as
`not_evaluated`, never scored 0/14. A zero would read later as «the adapter answered and was wrong».

    PYTHONPATH=src python3.11 scripts/score_lora_b.py
    PYTHONPATH=src python3.11 scripts/score_lora_b.py --outdir /tmp/again   # the pair
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import read_pass1_probe as p1  # noqa: E402
import read_threads_reader_v5 as v5  # noqa: E402
import score_pass1_probe as scoring  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

PHASE = "lora-b"
PREREG = REPO_ROOT / "results" / "prereg_lora_b.json"
PACK = REPO_ROOT / "results" / "pass1_probe_b_pack.json"
BASE_VERDICT = REPO_ROOT / "results" / "pass1_probe_b_verdict.json"
RUN = REPO_ROOT / "results" / "lora_b_run.json"
OUT_NAME = "results/lora_b_verdict.json"

RAW = {
    "a": REPO_ROOT / "results" / "lora_b_eval_arm_a.jsonl",
    "b": REPO_ROOT / "results" / "lora_b_eval_arm_b.jsonl",
}
"""Each arm's raw replies as the pod persisted them, ONE FILE PER ARM. The shipped runner's resume
skips every unit already answered, so two arms sharing an out-file would leave the second answering
nothing and looking complete (Dv560) — the separation starts on the pod and is kept here."""

EVIDENCE = {
    "a": REPO_ROOT / "results" / "lora_b_arm_a_rows.jsonl",
    "b": REPO_ROOT / "results" / "lora_b_arm_b_rows.jsonl",
}

ADAPTER_RECORD = {
    "a": REPO_ROOT / "results" / "lora_b_eval_arm_a.jsonl.adapter.json",
    "b": REPO_ROOT / "results" / "lora_b_eval_arm_b.jsonl.adapter.json",
}
"""What `pass1_pod_runner` wrote BESIDE the evidence, before the first reply: the arm's own adapter
files, hashed. `PeftModel.from_pretrained` injects in place, so no evidence row can say which arm
answered it — this record is the only thing that can ([[baseline_before_the_run_not_after]])."""


def read(path: Path) -> dict:
    return json.loads(summary.read_text_or_refuse(path))


def evaluated_arms(run: dict) -> set[str]:
    """Which arms the RUN RECORD says were cleared for eval — every arm whose format smoke went GO.

    This is the cross-check that keeps `evidence_for`'s `None` honest. A missing raw file is the
    right answer for an arm that never ran, and the WRONG answer for an arm that ran and whose
    replies were never copied back: the verdict would then print «neither arm produced a reply, the
    attempt is NOT spent» over a session that spent it. Two records, one claim
    ([[a_checker_whose_failure_is_silence]]).
    """
    return {
        one["arm"]
        for one in run.get("gates", [])
        if str(one.get("kind", "")).startswith("smoke-") and one.get("verdict") == "GO"
    }


def refuse_a_missing_copy() -> set[str]:
    """Stop before scoring if an arm the run cleared has no replies on this machine."""
    if not RUN.exists():
        return set()
    expected = evaluated_arms(read(RUN))
    missing = sorted(arm for arm in expected if not RAW[arm].exists())
    if missing:
        raise SystemExit(
            f"{summary.rel(RUN)} says arm(s) {missing} passed the format smoke and were evaluated,"
            f" and {[summary.rel(RAW[arm]) for arm in missing]} do not exist on this machine. The"
            " replies were never copied back — scoring now would report NO READING over a session"
            " that spent the attempt. Copy them and re-run; do not edit this refusal."
        )
    return expected


def evidence_for(
    arm: str, record: dict, pack: dict, outdir: Path
) -> tuple[list[dict], Path] | None:
    """One arm's raw replies, parsed into evidence by the probe's own ingest.

    Returns None when the arm has no replies at all — a milestone STOP before arm B, or a format
    smoke that killed an arm before its eval. That is a state, not a score.

    The written path is handed back rather than recomputed by the caller: under `--outdir` the
    evidence lands there, and a sha taken off the repo copy would be yesterday's file
    ([[the_fixture_and_the_artifact_share_anchors]]).
    """
    if not RAW[arm].exists():
        return None
    written = outdir / EVIDENCE[arm].relative_to(REPO_ROOT)
    written.parent.mkdir(parents=True, exist_ok=True)
    keep = p1.EVIDENCE
    p1.EVIDENCE = written
    try:
        return p1.ingest(record, v5.raw_rows(RAW[arm]), pack), written
    finally:
        p1.EVIDENCE = keep


def arm_reading(arm: str, record: dict, ingested: tuple[list[dict], Path] | None) -> dict:
    """The bar and the census for one arm, or the reason there is no reading."""
    if ingested is None:
        return {
            "arm": arm,
            "evaluated": False,
            "why": (
                f"{summary.rel(RAW[arm])} does not exist — arm {arm} produced no reply. A missing"
                " arm is a STATE and is never scored 0 of 14"
            ),
        }
    evidence, written = ingested
    return {
        "arm": arm,
        "evaluated": True,
        "evidence": {
            "file": summary.rel(EVIDENCE[arm]),
            "rows": len(evidence),
            "sha256": summary.sha256_of(written),
        },
        "adapter": read(ADAPTER_RECORD[arm]) if ADAPTER_RECORD[arm].exists() else None,
        "bar": scoring.bar_p1(record, evidence),
        "census_50": scoring.census(record, evidence),
        "refusals": scoring.refusals(evidence),
    }


def gate(record: dict, arms: dict) -> dict:
    """The registered arm rule, solved on the readings that exist.

    `max(gold14(A), gold14(B)) ≥ 12`, one attempt, tie ships arm B — every clause read out of the
    registration. The multiplicity is carried through verbatim: two shots at one bar is about double
    the false-pass odds of one, it was accepted by the sitting, and a verdict that dropped the
    sentence would read later as if one arm had been run.
    """
    bar = record["bars"]["P1_per_comment_agreement"]
    threshold = int(bar["minimum_agreed"])
    scored = {
        name: int(block["bar"]["agreed"]) for name, block in arms.items() if block["evaluated"]
    }
    if not scored:
        return {
            "scored": False,
            "verdict": "NO READING",
            "reading": (
                "neither arm produced a reply, so the bar was never scored and the ONE attempt is"
                " NOT spent. The question returns to the team lead"
            ),
            "minimum_agreed": threshold,
            "n": int(bar["n"]),
            "rule": bar["arm_rule"],
            "multiplicity": bar["multiplicity"],
        }
    best = max(scored.values())
    # the tie is pre-named and it is arm B; `sorted` puts b last, so the last max wins it
    winner = [name for name in sorted(scored) if scored[name] == best][-1]
    passed = best >= threshold
    return {
        "scored": True,
        "agreed_by_arm": scored,
        "arms_not_evaluated": sorted(name for name in arms if not arms[name]["evaluated"]),
        "max_agreed": best,
        "minimum_agreed": threshold,
        "n": int(bar["n"]),
        "passed": passed,
        "ships": winner if passed else None,
        "tie": len(set(scored.values())) < len(scored),
        "tie_rule": bar["tie"],
        "verdict": "GREEN" if passed else "RED",
        "rule": bar["arm_rule"],
        "multiplicity": bar["multiplicity"],
        "attempt": record["attempt"],
        "reading": (
            f"arm {winner} agreed on {best} of {bar['n']} against a threshold of {threshold}"
            if passed
            else record["bars"]["P1_per_comment_agreement"]["red"]
        ),
        "next": record["return_to_sitting"] if not passed else "the higher arm ships",
    }


def ablation(record: dict, arms: dict) -> dict:
    """base / arm A / arm B, PAIRED per row on the same fourteen.

    The base column is READ out of its sealed verdict and never re-run: the arms are compared
    against a record measured on identical instances under the same prompt sha, which is the whole
    reason that record was sealed ([[a_frozen_record_is_an_input_to_shipped_code]]).
    """
    base = read(BASE_VERDICT)
    if summary.sha256_of(BASE_VERDICT) != record["population"]["base"]["sha256"]:
        raise SystemExit(
            f"{summary.rel(BASE_VERDICT)} is not the record the registration pinned. The ablation"
            " would then pair the arms against a base nobody registered — stop and report."
        )
    columns = {
        "base": {
            row["msg_id"]: bool(row["agreed"])
            for row in base["bars"]["P1_per_comment_agreement"]["rows"]
        }
    }
    for name, block in arms.items():
        if block["evaluated"]:
            columns[f"arm_{name}"] = {
                row["msg_id"]: bool(row["agreed"]) for row in block["bar"]["rows"]
            }
    order = [int(one["msg_id"]) for one in record["population"]["gold"]["rows"]]
    if sorted(columns["base"]) != sorted(order):
        raise SystemExit(
            "the sealed base verdict does not carry the fourteen the registration names — stop."
        )
    return {
        "rule": (
            "paired per row on the registration's own fourteen. The base column is the SEALED"
            " record and is not re-run"
        ),
        "base_record": {
            "file": summary.rel(BASE_VERDICT),
            "sha256": summary.sha256_of(BASE_VERDICT),
        },
        "agreed": {name: sum(column.values()) for name, column in columns.items()},
        "rows": [
            {"msg_id": msg_id, **{name: column.get(msg_id) for name, column in columns.items()}}
            for msg_id in order
        ],
        "turned": {
            name: sorted(one for one in order if column.get(one) and not columns["base"][one])
            for name, column in columns.items()
            if name != "base"
        },
        "lost": {
            name: sorted(one for one in order if columns["base"][one] and not column.get(one))
            for name, column in columns.items()
            if name != "base"
        },
    }


def census_profiles(record: dict, arms: dict) -> dict:
    """The 50 neighbour rows beside the bar — OBSERVATION ONLY, and it moves no bar."""
    base = read(BASE_VERDICT)
    return {
        "rule": record["bars"]["census_50"]["rule"],
        "gating": False,
        "base_none": record["bars"]["census_50"]["baseline_none"],
        "base_distribution": base["census"]["subject_type_distribution"],
        "by_arm": {
            name: block["census_50"]["subject_type_distribution"]
            for name, block in arms.items()
            if block["evaluated"]
        },
    }


def provenance(record: dict, arms: dict) -> dict:
    """What produced the numbers: adapters, seeds, config, sampler weights, dataset digests."""
    return {
        "training": record["training"],
        "arms": {
            name: {
                "dataset": record["arms"][name]["dataset"],
                "sampler_weights": record["arms"][name]["sampler_weights"],
                "steps": record["arms"][name]["steps"],
                "command": record["arms"][name]["command"],
                "eval_command": record["arms"][name]["eval_command"],
                "adapter": arms[name].get("adapter"),
            }
            for name in sorted(record["arms"])
        },
        "instruments": record["instruments"],
        "registration": {"file": "results/prereg_lora_b.json", "sha256": summary.sha256_of(PREREG)},
        "run_record": {
            "file": summary.rel(RUN),
            "sha256": summary.sha256_of(RUN) if RUN.exists() else None,
        },
        "eval_pack": record["population"]["eval_pack"],
        "gold": {key: record["population"]["gold"][key] for key in ("n", "record", "sha256")},
    }


def build(outdir: Path) -> dict:
    record = read(PREREG)
    pack = read(PACK)
    cleared = refuse_a_missing_copy()
    arms = {
        name: arm_reading(name, record, evidence_for(name, record, pack, outdir))
        for name in sorted(record["arms"])
    }
    return {
        "phase": PHASE,
        "contract": "docs/PROMPT-lora-b.md D4",
        "cleared_for_eval_by_the_run_record": sorted(cleared),
        "gate": gate(record, arms),
        "arms": arms,
        "ablation": ablation(record, arms),
        "census_50": census_profiles(record, arms),
        "provenance": provenance(record, arms),
        "producer": {"script": "scripts/score_lora_b.py"},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    record = build(args.outdir)
    record["producer"]["sha256"] = summary.sha256_of(Path(__file__))
    out = args.outdir / OUT_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {OUT_NAME}  sha256 {summary.sha256_of(out)[:16]}…\n")

    verdict = record["gate"]
    if not verdict["scored"]:
        print(f"NO READING — {verdict['reading']}")
        return 0
    table = record["ablation"]
    print(f"{'row':>8}  " + "  ".join(f"{name:>7}" for name in table["agreed"]))
    for row in table["rows"]:
        cells = "  ".join(
            f"{'·' if row.get(name) is None else ('ok' if row[name] else 'X'):>7}"
            for name in table["agreed"]
        )
        print(f"{row['msg_id']:>8}  {cells}")
    print(f"{'AGREED':>8}  " + "  ".join(f"{count:>7}" for count in table["agreed"].values()))
    for name, turned in table["turned"].items():
        print(f"  {name} turned {turned or 'nothing'} · lost {table['lost'][name] or 'nothing'}")
    print(
        f"\nGATE {verdict['verdict']} — max {verdict['max_agreed']} of {verdict['n']}"
        f" against {verdict['minimum_agreed']}"
        + (f", ships arm {verdict['ships']}" if verdict["ships"] else "")
    )
    print(f"     {verdict['reading']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
