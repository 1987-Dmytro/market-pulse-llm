#!/usr/bin/env python3
"""pass-1-probe's driver — the Mac side of one paid rung, and none of it written twice.

`scripts/read_threads_reader_v5b.py` is CALLED with its constants swapped (Dv451/Dv478's idiom, a
generation later): the never-two-pods check, the segment ledger, gate 0's ssh dead-man, the boot
deadline, the full-pass projection over the cap the ATTEMPT has left, the appended gate snapshots
and the torn-last-line normaliser are all its, unchanged and already paid for. It in turn calls
`scripts/read_threads_reader_v5.py` the same way, so there is ONE implementation of the cap
inequality in this repo and this file is not a second spelling of it.

Two things are pass 1's own, because they are the only two the reader's transport cannot do:

* **`--pack`** VERIFIES rather than builds. The pack is written by the registration's producer,
  because the pack IS part of what was registered — its order and its 64 rendering shas are solved
  through the gate before the money. Here it is rebuilt from the same inputs and compared byte for
  byte, on the Mac, before anything exists.
* **`--ingest`** parses with `prompts.parse_pass1`, which needs the request's own msg_id. A reader
  ingest would read these replies with the thread parser and return nothing usable.

    PYTHONPATH=src python3.11 scripts/read_pass1_probe.py --pack
    PYTHONPATH=src python3.11 scripts/read_pass1_probe.py --pre-create-check
    PYTHONPATH=src python3.11 scripts/read_pass1_probe.py --open --pod-id … --created-at … \\
        --usd-per-hour … --card …
    PYTHONPATH=src python3.11 scripts/read_pass1_probe.py --gate0 --ssh-ok
    PYTHONPATH=src python3.11 scripts/read_pass1_probe.py --gate
    PYTHONPATH=src python3.11 scripts/read_pass1_probe.py --ingest
"""

import argparse
import json
import sys
from contextlib import contextmanager
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import read_threads_reader_v5 as v5  # noqa: E402
import read_threads_reader_v5b as v5b  # noqa: E402
import runpod_guard as guard  # noqa: E402
import write_pass1_prereg as producer  # noqa: E402

from market_pulse import prompts  # noqa: E402

PHASE = "pass1-probe"
PREREG = REPO_ROOT / "results" / "prereg_pass1_probe.json"
LEDGER = guard.step_ledger_path(PHASE)
PACK = REPO_ROOT / "results" / "pass1_probe_pack.json"
RAW = REPO_ROOT / "results" / "pass1_probe_pod.jsonl"
EVIDENCE = REPO_ROOT / "results" / "pass1_probe_rows.jsonl"
RECORD = REPO_ROOT / "results" / "pass1_probe_run.json"

SWAPPED = v5b.SWAPPED

rel = v5.rel


@contextmanager
def as_this_phase():
    """v5b's module constants swapped for pass 1's, and put back after.

    v5b's own `as_this_phase` reads ITS globals at call time and pushes them down onto v5, so
    swapping them here reaches both modules through one assignment each. Restored in a `finally`:
    a module left pointing at another phase's files is the bug that only shows up in the second
    command.
    """
    ours = {name: globals()[name] for name in SWAPPED}
    keep = {name: getattr(v5b, name) for name in ours}
    for name, value in ours.items():
        setattr(v5b, name, value)
    try:
        yield
    finally:
        for name, value in keep.items():
            setattr(v5b, name, value)


def registration() -> dict:
    with as_this_phase():
        return v5b.registration()


def check_pack(record: dict) -> dict:
    """The committed pack, rebuilt from its own inputs and compared byte for byte.

    The pack is not built here because it was built BEFORE the registration was committed — the
    full-pass gate is solved over it and the table is in the record. What this does is prove the
    committed bytes are still what the inputs produce, on the Mac, for $0: a comment edited in the
    store costs nothing to discover now and a pod's boot to discover later.
    """
    rebuilt = (
        json.dumps(producer.build_pack(record), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )
    if rebuilt != PACK.read_text(encoding="utf-8"):
        raise SystemExit(
            f"{rel(PACK)} no longer rebuilds from the store and the bought verdicts. The pack is"
            " frozen with the registration — stop and report, do not re-write it."
        )
    pack = json.loads(rebuilt)
    if pack["instruments"]["prompt_sha256"] != record["instruments"]["prompt_sha256"]:
        raise SystemExit("the pack and the registration name different prompt shas")
    return {
        "pack": rel(PACK),
        "units": len(pack["items"]),
        "gold": sum(1 for one in pack["items"] if one["leg"] == "gold"),
        "census": sum(1 for one in pack["items"] if one["leg"] == "census"),
        "rebuilds_byte_for_byte": True,
    }


def ingest(record: dict, raw: list[dict], pack: dict) -> list[dict]:
    """The pod's raw replies turned into evidence — parsed here, on the Mac, with the pass-1 parser.

    One row per unit, carrying the request's own sha, the raw reply as the pod persisted it, the
    parse outcome and the timings. The parse is `prompts.parse_pass1(reply, msg_id=…)` and the id it
    is given is the PACK's, never the reply's: the echo check is only a check while the number it
    compares against comes from the request ([[the_guard_you_built_and_then_bypassed]]).
    """
    by_id = {one["id"]: one for one in pack["items"]}
    ids = v5.unit_ids(raw, pack, "the ingest")
    rows = []
    for one in raw:
        item = by_id[one["id"]]
        parsed, error = None, None
        try:
            parsed = prompts.parse_pass1(one["reply"], msg_id=int(item["msg_id"]))
        except prompts.ParseError as err:
            error = err.reason
        rows.append(
            {
                "id": one["id"],
                "thread": item["thread"],
                "msg_id": int(item["msg_id"]),
                "leg": item["leg"],
                "task": pack["task"],
                "prompt_sha256": pack["instruments"]["prompt_sha256"][pack["task"]],
                "rendering_sha256": item["rendering_sha256"],
                "request_chars": item["rendered_chars"],
                "reply": one["reply"],
                "parsed": parsed,
                "parse_error": error,
                "balanced": one.get("balanced"),
                "emitted_chars": one.get("emitted_chars"),
                "cut_chars": one.get("cut_chars"),
                "finish_reason": one.get("finish_reason"),
                "usage": one.get("usage"),
                "seconds": one.get("seconds"),
                "elapsed_since_start": one.get("elapsed_since_start"),
                "boot_seconds": one.get("boot_seconds"),
            }
        )
    rows.sort(key=lambda one: [item["id"] for item in pack["items"]].index(one["id"]))
    EVIDENCE.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )
    print(f"wrote {rel(EVIDENCE)}  {len(rows)} of {len(pack['items'])} units")
    print(f"  read {len(ids)} · parsed {sum(1 for one in rows if one['parsed'])}")
    refusals: dict[str, int] = {}
    for row in rows:
        if row["parse_error"]:
            refusals[row["parse_error"]] = refusals.get(row["parse_error"], 0) + 1
    for reason, count in sorted(refusals.items()):
        print(f"  refused {reason}: {count}")
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", action="store_true", help="verify the committed pack")
    parser.add_argument("--ingest", action="store_true", help="the pod's replies -> the evidence")
    parser.add_argument("--raw", type=Path, default=RAW)
    args, rest = parser.parse_known_args(argv)

    if args.pack:
        record = registration()
        print(json.dumps(check_pack(record), ensure_ascii=False, indent=2))
        return 0

    if args.ingest:
        record = registration()
        pack = json.loads(PACK.read_text(encoding="utf-8"))
        ingest(record, v5.raw_rows(args.raw), pack)
        return 0

    with as_this_phase():
        return v5b.main(rest)


if __name__ == "__main__":
    raise SystemExit(main())
