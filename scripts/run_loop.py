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

``--infer``
    5c2-prep-b's half: the queued rows go through the inference leg. With `--smoke` the transport
    is :class:`StubTransport` and the evidence rows land under `results/smoke/derived/`; WITHOUT
    it the pass asks `loop.inference_refusal` for permission and is refused, because no serving
    endpoint is registered and this contract may not register one. **A smoke never saves the
    cursor** — the watermark it advances lives in memory only, so `data/loop_cursor.json` comes
    out byte-identical and the next real pass still owes the rows a stub answered.

    PYTHONPATH=src python3 scripts/run_loop.py --once --dry-run
    PYTHONPATH=src python3 scripts/run_loop.py --once --smoke --channel @VARUS_channel
    PYTHONPATH=src python3 scripts/run_loop.py --once --smoke --infer --channel @VARUS_channel
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

from market_pulse import loop, parents  # noqa: E402
from market_pulse.raw_store import RawStore  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

REGISTRY = REPO_ROOT / "config" / "registry.yaml"
STORE_ROOT = REPO_ROOT / "data" / "raw"
DERIVED_ROOT = REPO_ROOT / "data" / "derived"
CAPTIONS = REPO_ROOT / "data" / "annotation" / "post_captions.jsonl"
CURSOR = REPO_ROOT / "data" / "loop_cursor.json"
SMOKE = REPO_ROOT / "results" / "smoke" / "loop_5a.json"
SMOKE_DERIVED = REPO_ROOT / "results" / "smoke" / "derived"

ENDPOINT = None
"""The serving endpoint the loop would send queued rows to. `None` in 5a — no GPU exists, and
SPEC 3.11 (2) puts a serving-parity measurement in front of the first serving number. This is
the one place 5b changes to open the guard, and `loop.inference_refusal` defaults it closed.

**Still None after 5c2-prep-b, deliberately.** This contract builds the inference leg end to end and
is forbidden from opening the guard: registering an endpoint belongs to the paid session's contract
(`docs/PROMPT-5c2-prep-b.md` DO NOT). The leg is exercised through :class:`StubTransport` instead,
which replaces the TRANSPORT and nothing else — `tests/test_loop.py::test_5a_registers_no_endpoint`
is the assertion that this line has not moved."""

STUB_SERVED_BY = "<stub: scripts/run_loop.py::StubTransport>"
"""What a stub-served evidence row names as its transport.

`market_pulse.evidence.REQUIRED` carries `served_by` for this one reason: a row answered by a fake
and a row answered by a registered endpoint must be distinguishable in the file they land in. The
value is deliberately unusable as an endpoint id — nothing can mistake it for one, and a grep for
``<stub`` finds every row that was never served by a model."""


class StubTransport:
    """The transport a smoke uses, and NOTHING else the pass does.

    It is a stub of the network hop only: the rendering, the prompt sha, the evidence table and the
    record-before-watermark ordering are the production path in a smoke exactly as they are in a
    run. That split is the point — vis-b's paid boot was refused by a guard whose stub had agreed
    with it, because a stub built from the same assumption as the code cannot contradict it.

    The reply shape is `local_llm.LocalClient.batch`'s, per row, so the record a smoke writes has
    the same keys a served record will. Two of the replies are broken on purpose, for the reason
    `positions_gm4_skub.FakeEndpoint` breaks two of its own: an unparseable answer and a refusal are
    different outcomes from an answer nobody could use, and a smoke that only ever succeeds proves
    the record shape on the easy half of the population.
    """

    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, task: str, rendering: list[dict]) -> dict:
        self.calls += 1
        broken = self.calls % 5 == 0
        return {
            "content": (
                '{"sentiment": '
                if broken
                else '{"sentiment": "negative", "sarcasm": false, "intents": ["price"]}'
            ),
            "finish_reason": "length" if broken else "stop",
            "cost": 0.0,
            "usage": {"prompt_tokens": 0, "completion_tokens": 0},
            "generation_id": None,
        }


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


def smoke_inference(channels, store, cursor, limit: int) -> dict:
    """The inference leg, stub-served, over at most ``limit`` queued rows per channel.

    Everything except the transport is the production path, and the evidence rows land in a
    throwaway store under `results/smoke/` (gitignored) rather than in `data/derived/`: a smoke
    must not leave records the next real pass would then read as already answered.
    """
    posts = parents.load(STORE_ROOT / "posts")
    captions = parents.load_captions(CAPTIONS)
    derived = RawStore(SMOKE_DERIVED)
    transport = StubTransport()
    per_channel = []
    for _, handle in channels:
        state = loop.channel_state(cursor, handle)
        rows = loop.queued(store, derived, handle, state.get(loop.INFERENCE))[:limit]
        summary = loop.inference_pass(
            rows,
            send=transport,
            posts=posts,
            captions=captions,
            derived=derived,
            state=state,
            # No endpoint is registered, so nothing can answer "which weights" — and an ABSENT
            # field and a field saying so are different states. The key is carried, holding the
            # only true value there is (`evidence.assert_complete` requires presence, not truth).
            model_revision=None,
            served_by=STUB_SERVED_BY,
        )
        per_channel.append({"channel": handle} | summary)
    return {
        "served_by": STUB_SERVED_BY,
        "why": (
            "the SEAM only. No endpoint is registered (`inference.refusal` above stands and this"
            " contract may not open it), no client is built, no request leaves the machine and"
            " nothing is billed. The rendering, the prompt sha, the evidence table and the"
            " record-before-watermark ordering are the production path in both cases — a stub"
            " shares the premises of the code it stands in for, so it may only replace the"
            " transport. NO NUMBER FROM THESE ROWS MAY REACH AN AGGREGATE."
        ),
        "records": relabel.rel(SMOKE_DERIVED),
        "transport_calls": transport.calls,
        "limit_per_channel": limit,
        "per_channel": per_channel,
    }


def smoke_record(rows: list[dict], refusal: str | None, only: str | None, served=None) -> dict:
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
        # Beside `inference` and never inside it: that block answers "is an endpoint registered",
        # which is still no, and a served-rows count folded into it would make one record say both
        # "sends none" and "here is what it sent". Absent on a plan-only smoke.
        **({"smoke_inference": served} if served is not None else {}),
        "wrote": (
            "nothing — a dry pass builds no client, fetches nothing and leaves the store and the"
            " cursor byte-identical (tests/test_loop.py::test_a_dry_pass_writes_nothing)"
            if served is None
            else "the plan above, plus stub-served evidence rows under results/smoke/derived/ —"
            " see `smoke_inference`. The raw v1 stores and data/derived/ are untouched"
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
    parser.add_argument(
        "--infer",
        action="store_true",
        help="run the inference leg (--smoke serves it from a stub; no endpoint exists)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="most queued rows per channel the stub-served leg answers (default 5)",
    )
    args = parser.parse_args(argv)

    if not args.once:
        parser.error("5a runs one pass at a time: pass --once")
    # `--infer` is a MODE here, not an option on the other two, and that is what keeps the right
    # guard answering. Left out of this list it fell through to LIVE_REFUSAL — a true refusal with
    # the wrong reason, since that one is about appending to the raw v1 stores and the inference leg
    # writes beside them. `--infer` is refused a few lines down by `inference_refusal`, which is the
    # guard that actually governs it.
    if not (args.dry_run or args.smoke or args.infer):
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

    served = None
    if args.infer:
        if not args.smoke:
            # The one place the guard is consulted for real. `--infer` without `--smoke` asks for a
            # SERVED pass, and `inference_refusal` is what stands between that and an endpoint this
            # contract is forbidden to register.
            raise SystemExit(
                refusal
                or "an endpoint is registered — a served pass belongs to the paid session's contract"
            )
        served = smoke_inference(channels, store, cursor, args.limit)
        for row in served["per_channel"]:
            print(
                f"  stub-served {row['channel'][:23]:<24} {row['written']:>4} rows written,"
                f" watermark now {row['watermark']}"
            )

    if args.smoke:
        SMOKE.parent.mkdir(parents=True, exist_ok=True)
        relabel.append_record(SMOKE, smoke_record(rows, refusal, args.channel, served))
        print(f"\nwrote {relabel.rel(SMOKE)} (gitignored — quote it, do not point at it)")
    else:
        print("\n--dry-run: nothing fetched, nothing written, no client built")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
