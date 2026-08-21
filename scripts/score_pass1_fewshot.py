#!/usr/bin/env python3
"""`results/pass1_fewshot_verdict.json` — D2: the dev table, the shot, and the paired fourteen.

**Nothing about either bar is new.** The dev gate is `scripts/gate_pass1_fewshot.py::dev_gate`,
CALLED — the same function the live session acts on, so the table in the report and the verdict the
pod was killed or cleared by are one computation. The gold bar is
`scripts/score_pass1_probe.py::bar_p1`, CALLED with this contract's registration and the shot's
evidence, so the comparison is still `scorer.reader_comment_agreement` under probe-b's symmetric
collapse, reached through exactly one implementation.

**The base is never re-run on the fourteen.** The paired table's first column is
`results/pass1_probe_b_verdict.json` as it was sealed, its second is `results/lora_b_verdict.json`'s
arm A, and only the third is this line's. Three readings of the same fourteen instances, two of them
already on disk.

**A leg with no replies is a STATE, never a zero.** A session that closed at the dev gate has no
shot file, and that is reported as `not_evaluated` with the reason — a 0 of 14 would read later as
«v2 answered and was wrong». And the reverse is refused: while the run record says a gold row was
answered and the replies are not on this machine, this REFUSES rather than publishing «no reading»
over a session that spent the attempt ([[a_checker_whose_failure_is_silence]]).

    PYTHONPATH=src python3.11 scripts/score_pass1_fewshot.py
    PYTHONPATH=src python3.11 scripts/score_pass1_fewshot.py --outdir /tmp/again   # the pair
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gate_pass1_fewshot as gate  # noqa: E402
import read_pass1_probe as p1  # noqa: E402
import read_threads_reader_v5 as v5  # noqa: E402
import score_pass1_probe as scoring  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

PHASE = gate.PHASE
PREREG = gate.PREREG
DEV_PACK = REPO_ROOT / "results" / "pass1_dev_pack.json"
SHOT_PACK = REPO_ROOT / "results" / "pass1_probe_b_pack_v2.json"
RUN = gate.RECORD
"""The registration and the run record are the GATE's, by reference and not by a second spelling.
r2 moved both files, and the two lines that used to name them here would have gone on reading r1's
— a judge pointed at a superseded law is the quietest way to score the wrong session
([[preregistration_is_a_file_not_a_constant]])."""
BASE_VERDICT = REPO_ROOT / "results" / "pass1_probe_b_verdict.json"
LORA_B_VERDICT = REPO_ROOT / "results" / "lora_b_verdict.json"
OUT_NAME = "results/pass1_fewshot_verdict.json"
EVIDENCE_NAME = "results/pass1_fewshot_shot_rows.jsonl"


def read(path: Path) -> dict:
    return json.loads(summary.read_text_or_refuse(path))


def shot_leg() -> dict:
    pack = read(SHOT_PACK)
    leg = pack["legs"][0]
    return {**pack, "task": leg["task"], "items": leg["items"], "out": leg["out"]}


def shot_replies() -> Path:
    return REPO_ROOT / "results" / shot_leg()["out"]


def the_attempt_was_spent(run: dict) -> bool:
    """Did the run record say a GOLD row was answered? That is when the attempt is spent.

    Read off the dev gate's own verdict rather than off a file's existence: the registration spends
    the attempt at the first gold-row reply, and the only rung that can produce one is a GO at rung
    7. A `--watch` on the shot pack is the other witness and either is enough.
    """
    for one in run.get("gates", []):
        if one.get("kind") == "dev-gate" and one.get("verdict") == "GO":
            return True
    return False


def refuse_a_missing_copy() -> bool:
    """Stop before scoring if the run cleared the shot and its replies are not on this machine."""
    if not RUN.exists():
        return False
    if the_attempt_was_spent(read(RUN)) and not shot_replies().exists():
        raise SystemExit(
            f"{summary.rel(RUN)} says the dev gate went GO, so the shot was fired and the ONE"
            f" attempt is SPENT — and {summary.rel(shot_replies())} does not exist on this machine."
            " Scoring now would publish NO READING over a session that spent it. Copy the replies"
            " and re-run; do not edit this refusal."
        )
    return True


def dev_table(record: dict) -> dict:
    """Rung 7's own computation, called — never a second spelling of the gate the pod was cleared by.

    `gate.dev_gate` needs a run state only for its clock block, so a session whose record is not on
    this machine is scored with an empty one and the clock reads zero. The two inequalities and the
    per-class table do not touch it.
    """
    pack = read(DEV_PACK)
    state = read(RUN) if RUN.exists() else {"pods": []}
    missing = [
        leg["out"] for leg in pack["legs"] if not (REPO_ROOT / "results" / leg["out"]).exists()
    ]
    if missing:
        return {
            "scored": False,
            "why": (
                f"{missing} are not on this machine — the dev legs produced no replies, or they were"
                " never copied back. A dev table is not published from half a run"
            ),
        }
    return {"scored": True, **gate.dev_gate(record, state, pack, REPO_ROOT / "results")}


def shot_reading(record: dict, outdir: Path) -> dict:
    """The gold bar for v2, through probe-b's own `bar_p1`, or the reason there is no reading."""
    replies = shot_replies()
    if not replies.exists():
        return {
            "evaluated": False,
            "why": (
                f"{summary.rel(replies)} does not exist — no gold row was answered. The ONE attempt"
                " is NOT spent and the question returns to the team lead. This is a STATE and is"
                " never scored 0 of 14"
            ),
        }
    pack = shot_leg()
    written = outdir / EVIDENCE_NAME
    written.parent.mkdir(parents=True, exist_ok=True)
    keep = p1.EVIDENCE
    p1.EVIDENCE = written
    try:
        evidence = p1.ingest(record, v5.raw_rows(replies), pack)
    finally:
        p1.EVIDENCE = keep
    return {
        "evaluated": True,
        "evidence": {
            "file": EVIDENCE_NAME,
            "rows": len(evidence),
            "sha256": summary.sha256_of(written),
            "replies": summary.rel(replies),
            "replies_sha256": summary.sha256_of(replies),
        },
        "bar": scoring.bar_p1(record, evidence),
        "census_50": scoring.census(record, evidence),
        "refusals": scoring.refusals(evidence),
    }


def paired_fourteen(shot: dict) -> dict:
    """The same fourteen instances read three times: the sealed base, the sealed arm A, and v2.

    Two of the three columns are files that already exist and are NOT re-computed here — the base's
    verdict was sealed by pass1-probe-b and arm A's by lora-b. A column re-derived from a re-run
    would be a fourth reading pretending to be one of the first two.
    """
    base = read(BASE_VERDICT)["bars"]["P1_per_comment_agreement"]
    arm_a = read(LORA_B_VERDICT)["arms"]["a"]["bar"]
    columns = {
        "base": {row["msg_id"]: row for row in base["rows"]},
        "arm_a": {row["msg_id"]: row for row in arm_a["rows"]},
    }
    if shot.get("evaluated"):
        columns["v2"] = {row["msg_id"]: row for row in shot["bar"]["rows"]}
    rows = []
    for msg_id in sorted(columns["base"]):
        cell = {"msg_id": msg_id}
        for name, table in columns.items():
            one = table.get(msg_id)
            cell[name] = None if one is None else bool(one["agreed"])
            if one is not None and not one["agreed"] and one.get("disagreed_on"):
                cell[f"{name}_said"] = {
                    field: value.get("reader") for field, value in one["disagreed_on"].items()
                }
        rows.append(cell)
    return {
        "rule": (
            "three readings of the same fourteen instances under the same judge. The base and arm A"
            " are READ from their sealed verdicts and are never re-run"
        ),
        "agreed": {
            "base": base["agreed"],
            "arm_a": arm_a["agreed"],
            **({"v2": shot["bar"]["agreed"]} if shot.get("evaluated") else {}),
        },
        "sources": {
            "base": {
                "record": summary.rel(BASE_VERDICT),
                "sha256": summary.sha256_of(BASE_VERDICT),
            },
            "arm_a": {
                "record": summary.rel(LORA_B_VERDICT),
                "sha256": summary.sha256_of(LORA_B_VERDICT),
            },
        },
        "rows": rows,
        "rows_only_v2_agrees_on": sorted(
            one["msg_id"] for one in rows if one.get("v2") and not one["base"] and not one["arm_a"]
        )
        if shot.get("evaluated")
        else None,
        "rows_v2_lost_that_the_base_had": sorted(
            one["msg_id"] for one in rows if one["base"] and one.get("v2") is False
        )
        if shot.get("evaluated")
        else None,
    }


def census_profiles(shot: dict) -> dict:
    """v2's census-50 distribution beside the base's and arm A's. OBSERVATION ONLY."""
    base = read(BASE_VERDICT).get("census", {}).get("subject_type_distribution", {})
    arm_a = read(LORA_B_VERDICT)["arms"]["a"].get("census_50", {})
    return {
        "rule": "reported and never gating — no number here moves any bar",
        "why_it_matters": (
            "line B's whole finding was a census that moved while the bar did not: None 25 → 9 and"
            " не_наш_рынок 8 → 23 under an adapter that scored the same 9 of 14 row for row"
        ),
        "base": base,
        "arm_a": arm_a.get("subject_type_distribution", arm_a),
        "v2": shot["census_50"]["subject_type_distribution"] if shot.get("evaluated") else None,
    }


def provenance(record: dict) -> dict:
    dev = read(DEV_PACK)
    shot = read(SHOT_PACK)
    return {
        "registration": {"record": summary.rel(PREREG), "sha256": summary.sha256_of(PREREG)},
        "run_record": (
            {"record": summary.rel(RUN), "sha256": summary.sha256_of(RUN)} if RUN.exists() else None
        ),
        "instruments": record["instruments"],
        "packs": {
            "dev": {"record": summary.rel(DEV_PACK), "sha256": summary.sha256_of(DEV_PACK)},
            "shot": {"record": summary.rel(SHOT_PACK), "sha256": summary.sha256_of(SHOT_PACK)},
        },
        "seeds": {"dev_draw": dev["draw"]["seed"], "holdout": record["population"]["holdout"]},
        "neighbours": {
            "rule": dev["neighbours"]["rule"],
            "per_item": {
                "dev_v2": {
                    one["id"]: one["examples_chosen"]
                    for one in next(leg for leg in dev["legs"] if leg["name"] == "v2")["items"]
                },
                "shot": {one["id"]: one["examples_chosen"] for one in shot["legs"][0]["items"]},
            },
        },
        "producer": {
            "script": summary.rel(Path(__file__)),
            "sha256": summary.sha256_of(Path(__file__)),
            "calls": {
                "dev gate": "scripts/gate_pass1_fewshot.py::dev_gate",
                "gold bar": "scripts/score_pass1_probe.py::bar_p1",
                "ingest": "scripts/read_pass1_probe.py::ingest",
            },
        },
    }


def build(outdir: Path) -> dict:
    refuse_a_missing_copy()
    record = read(PREREG)
    dev = dev_table(record)
    shot = shot_reading(record, outdir)
    verdict = "NOT EVALUATED"
    if shot.get("evaluated"):
        verdict = "GREEN" if shot["bar"]["passed"] else "RED"
    elif dev.get("scored"):
        verdict = f"CLOSED AT THE DEV GATE — {dev['verdict']}"
    return {
        "phase": PHASE,
        "contract": "docs/PROMPT-pass1-fewshot.md D2",
        "verdict": verdict,
        "attempt": record["attempt"],
        "multiplicity": record["multiplicity"],
        "return_to_the_operator": record["return_to_the_operator"],
        "dev_gate": dev,
        "shot": shot,
        "paired_fourteen": paired_fourteen(shot),
        "census_profiles": census_profiles(shot),
        "provenance": provenance(record),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    record = build(args.outdir)
    out = args.outdir / OUT_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {OUT_NAME}\n\nVERDICT  {record['verdict']}\n")

    dev = record["dev_gate"]
    if dev.get("scored"):
        print(
            f"DEV GATE  our {dev['base']['our_agreed']} → {dev['v2']['our_agreed']}"
            f" (delta {dev['our_delta']}, needs ≥ {dev['our_delta_minimum']})"
            f" · agreement {dev['base']['agreed']} → {dev['v2']['agreed']}"
            f" (delta {dev['agreement_delta']}, needs ≥ {dev['agreement_delta_minimum']})"
            f"  →  {dev['verdict']}"
        )
        for name in ("base", "v2"):
            per = dev[name]["per_class"]
            print(
                f"  {name:>4}: "
                + " · ".join(
                    f"{cls} {cell['agreed']}/{cell['n']}" for cls, cell in sorted(per.items())
                )
            )
    else:
        print(f"DEV GATE  not scored — {dev['why']}")

    shot = record["shot"]
    if shot.get("evaluated"):
        bar = shot["bar"]
        print(
            f"\nGOLD 14   {bar['agreed']} of {bar['n']} (threshold {bar['minimum_agreed']}) →"
            f" {'PASSED' if bar['passed'] else 'FAILED'}"
            f" · absent {bar['absent']} · refusals {shot['refusals']['refused']}"
        )
    else:
        print(f"\nGOLD 14   {shot['why']}")

    paired = record["paired_fourteen"]
    print(f"\nPAIRED    {paired['agreed']}")
    print(f"{'msg_id':>8}  {'base':>5} {'arm_a':>6} {'v2':>4}")
    for row in paired["rows"]:
        mark = {True: "✓", False: "·", None: "—"}
        print(
            f"{row['msg_id']:>8}  {mark[row['base']]:>5} {mark[row['arm_a']]:>6}"
            f" {mark[row.get('v2')]:>4}"
        )
    print(f"\nCENSUS-50 v2 {record['census_profiles']['v2']}")
    print(f"          base {record['census_profiles']['base']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
