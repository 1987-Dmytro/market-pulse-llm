#!/usr/bin/env python3
"""reader-topup — the Mac half of branch B: 132 units over 105 threads, on v5b's own machinery.

Nothing about the segments, the ssh dead-man, the boot deadline, the full-pass gate, the ledger or
the resume is new. `read_threads_reader_v5b` is IMPORTED and ITS module constants are swapped for
this phase's for the length of a call, exactly as v5b does to v5 — so the cap guard, the gate
arithmetic and the append-only run record are one implementation and not a third spelling.

Two things are this phase's own and they are swapped onto `read_threads_reader_v5`:

**`build_pack`** — v5's reads a `leg_a` enumeration plus ONE chunked thread, and this population is
105 threads of which ten are over the chunk line. The units are a flat list in the registration, so
the pack is built from that list and every unit is still re-rendered here and refused unless its sha
equals the pinned one.

**`projection`** — attempt A's gate STOPped its own run at the first reading. `max(unread ÷ read)`
over UNITS extrapolates the largest unit across all 132 when the sizes are not alike, and this
population's are not. Attempt B projects each unread unit at its own size through the registration's
fitted line, calibrated against what the pod has actually done and floored at the fit. Both of
attempt A's legs are still computed and printed, because a reader has to see what changed.

**Nothing else.** In particular the INGEST is v5's, unchanged: it already merges the chunks of a
thread through `market_pulse.reader_v5.merge` whenever a unit's leg is `B`, so marking the chunked
units `B` is the whole of what this phase needed from it.

    PYTHONPATH=src python3.11 scripts/read_threads_reader_topup.py --pack
    PYTHONPATH=src python3.11 scripts/read_threads_reader_topup.py --pre-create-check
    PYTHONPATH=src python3.11 scripts/read_threads_reader_topup.py --open --pod-id <ID> \\
        --created-at <UTC ISO8601> --usd-per-hour <costPerHr> --card '<the card>'
    PYTHONPATH=src python3.11 scripts/read_threads_reader_topup.py --gate0 [--ssh-ok]
    PYTHONPATH=src python3.11 scripts/read_threads_reader_topup.py --gate \\
        --generation-started-at <UTC ISO8601>
    PYTHONPATH=src python3.11 scripts/read_threads_reader_topup.py --close-segment \\
        --deleted-at <UTC ISO8601> --outcome '<why it ended>'
    PYTHONPATH=src python3.11 scripts/read_threads_reader_topup.py --ingest
"""

import sys
from contextlib import contextmanager
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gate_census_w1_reader as cell  # noqa: E402
import read_threads_reader_v5 as v5  # noqa: E402
import read_threads_reader_v5b as v5b  # noqa: E402
import runpod_guard as guard  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

PHASE = "reader-topup"
PREREG = REPO_ROOT / "results" / "reader_topup_prereg_b.json"
"""ATTEMPT B's registration. Attempt A's (`reader_topup_prereg.json`) stands with its verdict —
its gate STOPped the run and the record of that is committed. What B changes is the projector and
nothing else; `write_reader_topup_prereg_b.py` builds it FROM A and refuses if anything but the
gate moved."""
LEDGER = guard.step_ledger_path(PHASE)
PACK = REPO_ROOT / "results" / "reader_topup_pack.json"
RAW = REPO_ROOT / "results" / "reader_topup_pod.jsonl"
EVIDENCE = REPO_ROOT / "results" / "reader_topup_w1.jsonl"
RECORD = REPO_ROOT / "results" / "reader_topup_run.json"

SWAPPED = ("PHASE", "PREREG", "LEDGER", "PACK", "RAW", "EVIDENCE", "RECORD")


def projected_remaining(record: dict, pack: dict, read: list[str], measured: float) -> dict:
    """What the units still unread will cost, through the registration's OWN fitted model.

    Attempt A projected `max(unread units ÷ read, unread payable ÷ read payable) × measured`. That
    is conservative when units are the same size and simply wrong when they are not: with sizes
    from 1 to 16 payable and a median of 2, ordered expensive-first, the by-unit leg extrapolates
    the largest unit across all 132 and returns STOP at the first reading of a run that fits. It
    did, and the pod was deleted on it.

    This projects each unread unit at its OWN size — `intercept + slope × payable`, the line
    `results/reader_topup_projection.json` fitted on 26 v5b units — and CALIBRATES it against what
    this pod has actually done: `ratio = measured ÷ fitted(read units)`, floored at 1.0. The floor
    is the conservatism: a pod that is running faster than the fit does not get to shorten its own
    leash, and a pod that is running slower stretches the projection immediately and proportionally.
    """
    model = record["money"]["arithmetic"]["model"]
    intercept = float(model["intercept_seconds"])
    slope = float(model["slope_seconds_per_payable"])
    fitted = {one["id"]: intercept + slope * one["payable_comments"] for one in pack["items"]}
    fitted_read = sum(fitted[unit] for unit in read)
    ratio = measured / fitted_read if fitted_read else 1.0
    used = max(ratio, 1.0)
    unread = [one["id"] for one in pack["items"] if one["id"] not in set(read)]
    remaining = used * sum(fitted[unit] for unit in unread)
    return {
        "fitted_seconds_of_the_read_units": round(fitted_read, 1),
        "fitted_seconds_of_the_unread_units": round(sum(fitted[unit] for unit in unread), 1),
        "measured_over_fitted": round(ratio, 4),
        "calibration_used": round(used, 4),
        "calibration_rule": (
            "max(measured ÷ fitted, 1.0). A pod slower than the fit stretches the projection by"
            " exactly that factor; a pod faster than the fit is projected at the fit, because a"
            " fast start is not a licence to run long"
        ),
        "seconds": round(remaining, 1),
        "units_unread": len(unread),
    }


def projection(record: dict, rate: float, rows: list[dict], elapsed: float, pack: dict) -> dict:
    """The full-pass gate of ATTEMPT B — v5's envelope, with the model as the binding leg.

    v5's own two legs are still computed and still reported: they are what attempt A stopped on and
    a reader of this record has to be able to see both. What BINDS is the calibrated model, and the
    verdict re-derives from the one inequality printed beside it.
    """
    usable = v5.usable_seconds(record, rate)
    read = v5.unit_ids(rows, pack, "the full-pass gate")
    if not read:
        raise SystemExit("no replies yet — there is nothing to project from")
    payable = {one["id"]: one["payable_comments"] for one in pack["items"]}
    measured = sum(float(row["seconds"]) for row in rows)
    of = len(pack["items"])
    unread = of - len(read)
    read_payable = sum(payable[unit] for unit in read) or 1
    unread_payable = sum(payable.values()) - read_payable
    by_unit, by_payable = unread / len(read), unread_payable / read_payable
    model = projected_remaining(record, pack, read, measured)
    projected = elapsed + model["seconds"]
    return {
        "units_read": len(read),
        "units_unread": unread,
        "legs_read": sorted({one["leg"] for one in pack["items"] if one["id"] in set(read)}),
        "payable_comments_read": read_payable,
        "payable_comments_unread": unread_payable,
        "elapsed_since_create_seconds": round(elapsed, 1),
        "measured_seconds": round(measured, 3),
        "measured_seconds_per_unit": round(measured / len(read), 3),
        "binding": {"which": "fitted_model", **model},
        "reported_and_not_binding": {
            "by_unit": {"factor": round(by_unit, 4), "seconds": round(measured * by_unit, 1)},
            "by_payable_comment": {
                "factor": round(by_payable, 4),
                "seconds": round(measured * by_payable, 1),
            },
            "why": (
                "attempt A's two legs, kept in sight. The by-unit one is what STOPped attempt A at"
                " its first reading, and printing it beside the model is how a reader sees the"
                " difference the correction makes rather than being told about it"
            ),
        },
        "usable_seconds": round(usable, 1),
        "projected_total_seconds": round(projected, 1),
        "headroom_seconds": round(usable - projected, 1),
        "the_verdict_re_derives_from_here": (
            "`elapsed + calibration × Σ fitted(unread) ≤ usable` IS the verdict. The dollars below"
            " are the same statement at this segment's rate"
        ),
        "usd": {
            "cap_usd_all_in": float(record["money"]["cap_usd_all_in"]),
            "spent_so_far_usd": round(elapsed * rate, 4),
            "projected_total_usd": round(projected * rate, 4),
        },
        "verdict": "GO" if projected <= usable else "STOP",
    }


def build_pack(record: dict) -> dict:
    """Every unit as the pod will be given it, re-rendered here and held to its registered sha.

    The population is rebuilt from the reader cell rather than read out of the record: a comment
    edited in the store costs $0 to discover on this machine and a pod's boot to discover on that
    one. What the record supplies is WHICH ids go in which unit — a registered fact a renderer may
    not decide.
    """
    task = record["instruments"]["task"]
    kept = {f"{one['channel']}:{one['post_id']}": one for one in cell.population()}
    items = []
    for unit in record["population"]["units"]:
        thread = kept.get(unit["thread"])
        if thread is None:
            raise SystemExit(f"{unit['thread']} is no longer in the reader cell — stop and report.")
        texts = {int(row["msg_id"]): row["text"] for row in thread["comments"]}
        missing = [one for one in unit["msg_ids"] if one not in texts]
        if missing:
            raise SystemExit(
                f"{unit['id']}: {len(missing)} of its comments are gone from the store"
                f" ({missing[:3]}). The registration was priced on a population that has moved."
            )
        part = None if unit["part"] is None else tuple(unit["part"])
        items.append(
            v5._item(
                thread["channel"],
                int(thread["post_id"]),
                thread["post_text"],
                [(one, texts[one]) for one in unit["msg_ids"]],
                task,
                leg="A" if part is None else "B",
                unit_id=unit["id"],
                pinned=unit["rendering_sha256"],
                part=part,
            )
        )
    return {
        "phase": PHASE,
        "registration": {"record": summary.rel(PREREG), "sha256": summary.sha256_of(PREREG)},
        "task": task,
        "instruments": {
            "prompt_sha256": dict(record["instruments"]["prompt_sha256"]),
            "parser": {"sha256": record["instruments"]["parser"]["sha256"]},
        },
        "serving": dict(record["instruments"]["serving"]),
        "items": items,
        "reading": (
            "the pod renders each item itself, chunk header included, and refuses unless its sha"
            " equals the one above. Shipping the rendered string would only prove the two machines"
            " agree about a string; what has to be true is that the model is shown what the"
            " registration registered"
        ),
    }


@contextmanager
def as_this_phase():
    """v5b's constants swapped for this phase's, and v5's pack builder for this phase's.

    Two levels, because v5b already swaps v5: setting v5b's globals is what makes ITS
    `as_this_phase` hand v5 these paths. The pack builder is swapped on v5 directly — it is the one
    function whose shape this population does not fit.
    """
    ours = {name: globals()[name] for name in SWAPPED}
    for name in ours:  # every name checked BEFORE anything is captured or replaced
        if not hasattr(v5b, name):
            raise SystemExit(
                f"read_threads_reader_v5b.py has no `{name}` any more, so this file is replacing"
                " something that no longer exists and the run would silently use v5b's own files."
                " Stop and report."
            )
    keep = {name: getattr(v5b, name) for name in ours}
    keep_pack, keep_projection = v5.build_pack, v5.projection
    for name, value in ours.items():
        setattr(v5b, name, value)
    v5.build_pack, v5.projection = build_pack, projection
    try:
        yield
    finally:
        for name, value in keep.items():
            setattr(v5b, name, value)
        v5.build_pack, v5.projection = keep_pack, keep_projection


def main(argv: list[str] | None = None) -> int:
    with as_this_phase():
        return v5b.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
