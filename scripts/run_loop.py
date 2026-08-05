#!/usr/bin/env python3
"""One pass of the Phase-5 production loop — dry in 5a, on purpose.

`docs/PROMPT-5a.md` deliverable 3 asks for the skeleton and its verifier, not for collection:
the loop's live pass would append to `data/raw/`, and 5a's DO NOT list forbids writing to the
raw v1 stores (derived columns beside them only). So this script computes and prints what a
pass **would** do — from the cursor and the store, without a client — and refuses to run live.
Where the live pass writes is 5c's decision; it is not defaulted here.

Two flags, the house meanings (`scripts/migrate_intents_v4.py`, `scripts/precheck_uplabel.py`):

``--dry-run``
    print the plan and stop. Nothing is written, no client is built. This is the brief's
    literal command, and `tests/test_loop.py` holds it to both halves of that sentence.
``--smoke``
    the same dry pass over one channel, recorded in `results/smoke/loop_5a.json` in the shape
    a real record has. Smoke records are gitignored (`.gitignore`: `results/smoke/`), so the
    numbers are quoted in the task report rather than pointed at.

    PYTHONPATH=src python3 scripts/run_loop.py --once --dry-run
    PYTHONPATH=src python3 scripts/run_loop.py --once --smoke --channel @VARUS_channel
"""

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))

import relabel_intents as relabel  # noqa: E402
from build_audit_pack import git_state  # noqa: E402

from market_pulse import loop  # noqa: E402
from market_pulse.raw_store import RawStore  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

REGISTRY = REPO_ROOT / "config" / "registry.yaml"
STORE_ROOT = REPO_ROOT / "data" / "raw"
CURSOR = REPO_ROOT / "data" / "loop_cursor.json"
SMOKE = REPO_ROOT / "results" / "smoke" / "loop_5a.json"

ENDPOINT = None
"""The serving endpoint the loop would send queued rows to. `None` in 5a — no GPU exists, and
SPEC 3.11 (2) puts a serving-parity measurement in front of the first serving number. This is
the one place 5b changes to open the guard, and `loop.inference_refusal` defaults it closed."""

LIVE_REFUSAL = (
    "5a runs the loop dry only. A live pass appends to data/raw/, and docs/PROMPT-5a.md's DO NOT"
    " list forbids writing to the raw v1 stores (derived columns beside them only). The live"
    " pass and the store root it writes to are 5c's, with their own gate. Pass --dry-run to see"
    " what this pass would fetch, or --smoke to record it."
)


def channels_of(registry, only: str | None) -> list[tuple]:
    """The verified channels this pass covers, or the one the operator named."""
    found = [
        (source, handle)
        for source in registry.sources
        if source.verified
        for handle in source.telegram_channels
        if only is None or handle == only
    ]
    if not found:
        raise SystemExit(f"{only}: not a verified channel in {relabel.rel(REGISTRY)}")
    return found


def smoke_record(rows: list[dict], refusal: str | None, only: str | None) -> dict:
    return {
        "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
        "task": "loop_pass_5a",
        "smoke": True,
        "mode": "dry-run",
        "scope": {
            "registry": relabel.rel(REGISTRY),
            "store_root": relabel.rel(STORE_ROOT),
            "cursor": relabel.rel(CURSOR),
            "cursor_exists": CURSOR.exists(),
            "channel": only,
            "channels_in_pass": len(rows),
        },
        "plan": rows,
        "totals": {
            "threads_to_fetch": sum(row["threads_to_fetch"] for row in rows),
            "rows_to_inference": sum(row["rows_to_inference"] for row in rows),
        },
        "inference": {"endpoint": ENDPOINT, "refusal": refusal},
        "wrote": (
            "nothing — a dry pass builds no client, fetches nothing and leaves the store and the"
            " cursor byte-identical (tests/test_loop.py::test_a_dry_pass_writes_nothing)"
        ),
        "git": git_state(SMOKE),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--once", action="store_true", help="run a single pass (the only mode in 5a)"
    )
    parser.add_argument("--dry-run", action="store_true", help="print the plan and stop")
    parser.add_argument(
        "--smoke", action="store_true", help="the dry pass, recorded in results/smoke/"
    )
    parser.add_argument("--channel", help="restrict the pass to one channel handle")
    args = parser.parse_args(argv)

    if not args.once:
        parser.error("5a runs one pass at a time: pass --once")
    if not (args.dry_run or args.smoke):
        raise SystemExit(LIVE_REFUSAL)

    channels = channels_of(load_registry(REGISTRY), args.channel)
    store = RawStore(STORE_ROOT)
    cursor = loop.load_cursor(CURSOR)
    rows = loop.plan(store, channels, cursor)

    print(loop.render_plan(rows))
    queued = sum(row["rows_to_inference"] for row in rows)
    refusal = loop.inference_refusal(queued, ENDPOINT)
    print(
        f"\ninference: {refusal or 'endpoint registered — the pass would send ' + str(queued) + ' rows'}"
    )

    if args.smoke:
        SMOKE.parent.mkdir(parents=True, exist_ok=True)
        relabel.append_record(SMOKE, smoke_record(rows, refusal, args.channel))
        print(f"\nwrote {relabel.rel(SMOKE)} (gitignored — quote it, do not point at it)")
    else:
        print("\n--dry-run: nothing fetched, nothing written, no client built")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
