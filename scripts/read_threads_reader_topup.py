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
PREREG = REPO_ROOT / "results" / "reader_topup_prereg.json"
LEDGER = guard.step_ledger_path(PHASE)
PACK = REPO_ROOT / "results" / "reader_topup_pack.json"
RAW = REPO_ROOT / "results" / "reader_topup_pod.jsonl"
EVIDENCE = REPO_ROOT / "results" / "reader_topup_w1.jsonl"
RECORD = REPO_ROOT / "results" / "reader_topup_run.json"

SWAPPED = ("PHASE", "PREREG", "LEDGER", "PACK", "RAW", "EVIDENCE", "RECORD")


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
    keep_pack = v5.build_pack
    for name, value in ours.items():
        setattr(v5b, name, value)
    v5.build_pack = build_pack
    try:
        yield
    finally:
        for name, value in keep.items():
            setattr(v5b, name, value)
        v5.build_pack = keep_pack


def main(argv: list[str] | None = None) -> int:
    with as_this_phase():
        return v5b.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
