#!/usr/bin/env python3
"""pass 2's generation leg — the ONLY thing that runs on the rented pod, and it WAITS in the middle.

`scripts/reader_v5_pod_runner.py` is CALLED, never edited, by `scripts/pass1_pod_runner.py`'s own
construction: the boot, the resume-skip with its tolerant reader, the balanced-object stop, the
per-row persistence and the progress lines are all its, and exactly two module globals are swapped
for the length of the call — the RENDER, because a pass-2 request is a post, a bought entity block
and the comments pass 1 attributed, and the HANDSHAKE, because a pass-2 pack pins a different
family. The swap asserts that every name it replaces EXISTS first.

**Why this is a SIBLING and not the shipped runner with a duck-typed `prompts`.** The contract asks
the question and the source answers it: `reader_v5_pod_runner.run` does `from market_pulse import
prompts` itself and hands that module to `check_instrument` and `check_requests`, and the `Client`
its `load_reader` builds imports the same module inside `render`. Nothing is passed in, so a prompt
living in `market_pulse.pass2` cannot be reached without replacing the module-level `render` — which
is precisely the swap pass 1 already makes. On top of that the shipped handshake compares the pack's
map against `prompts.READER`, and a pass-2 pack pins `pass2_thread_gm4_v1`.

**Two shipped helpers are IMPORTED and not re-written.** `pass1_fewshot_pod_runner.once` is the
loader wrapper that hands the second call the client the first one built, and `::legs_of` is the
one-leg reader. Both were bought for the fewshot contract's two legs and both do here exactly what
they did there.

**THE GO. `--go` is what makes rung S′ possible on one pod.** The registration prices the SMOKE at
an assumed ceiling and the FULL run from the smoke's own reading — «the runner waits for the go», and
this is the mechanism: the pack's first `smoke.units` items are answered as a pack of their own, the
process then BLOCKS on a token file the Mac writes over ssh, and the remaining units are answered by
a second call to the same shipped `main` with a loader that hands back the client it already built.
The model is loaded ONCE, which is why the registered arithmetic charges the 1 100 s of
pre-generation once and why the worked arm closes at 48.6 s/call.

**A WAIT line is not a reply line.** The gate's rung 5 counts LOG LINES as liveness events beside
out-file rows, so a pod that is legitimately waiting for the Mac has to keep the log rising — and a
human reading that log has to be able to tell it from a pod that is working. Each poll prints one
`WAIT` line naming the token it is waiting for and the seconds left.

    HF_HOME=/workspace/hf PYTHONPATH=/workspace/repo/src \\
    /workspace/venv/bin/python -u /workspace/repo/scripts/pass2_pod_runner.py \\
        --pack /workspace/repo/results/pass2_pack.json \\
        --outdir /workspace/run --repo /workspace/repo \\
        --go /workspace/run/pass2_go --go-deadline 600
"""

import argparse
import json
import sys
import time
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pass1_fewshot_pod_runner as fewshot  # noqa: E402
import reader_v5_pod_runner as runner  # noqa: E402
from reader_v4_pod_runner import sha256_of  # noqa: E402

SHIPPED_RENDER = runner.render
"""The reader's render, captured at IMPORT — before any swap, so the dispatch below cannot recurse
into itself the moment `as_pass2()` replaces the module global."""

GO_POLL_SECONDS = 15.0
"""Seconds between two looks at the token file, and therefore between two WAIT lines in the log.

Under the Mac's own 20 s watch poll on purpose: the log the gate reads is copied by that poll, and a
pod whose only liveness signal arrived less often than the thing reading it would look idle for one
poll in every two."""


def render(prompts, item: dict, task: str) -> str:
    """One pass-2 request — the post, the thread's bought names, and the filtered comments.

    Rendered from the pack's own fields on the pod, exactly as the reader's and pass 1's are:
    shipping the string would prove the two machines agree about a string, not that the model is
    shown what the registration registered.

    **A task that is not pass 2's goes to the reader's own render, and that branch is a call this
    run MAKES.** `local_llm.ReaderClient.__init__` probes the chat template through
    `self.render(prompts.READER_TASK_V2, {…})` before it will build a client at all, so a swap that
    assumed every call was a pass-2 item would raise inside the CONSTRUCTOR — where a stub-driven
    test cannot see it, because a fake client replaces the very constructor that makes the call
    ([[a_stub_replaces_the_guard_it_should_trigger]]).
    """
    from market_pulse import pass2

    if task not in pass2.PASS2:
        return SHIPPED_RENDER(prompts, item, task)
    return pass2.pass2_messages_gm4(
        item["channel"],
        item["post_id"],
        item["post"],
        item["entities"],
        item["comments"],
        task=task,
    )[0]["content"]


def check_instrument(pack: dict, repo: Path, prompts) -> dict:
    """The handshake for the pass-2 family — three questions, one more than the reader's two.

    The per-task shas say the registered TEXT is what this checkout renders, and the module sha says
    the parser the Mac will read these replies with is the module this pod rendered them from. Pass
    2 adds a third: `src/market_pulse/pass2.py` carries both the TEXT and the RENDERER, so a
    checkout whose prompt matched but whose renderer had moved would produce requests no
    `rendering_sha256` describes. `check_requests` would catch that on item one — this catches it
    before the model is loaded, which is 450 s and about $0.10 earlier.

    Over the tasks the PACK pins and not over `pass2.PASS2` whole, for the reason the reader's
    handshake and pass 1's were both narrowed: a text registered LATER is not in an older pack's map
    and is not expected to be ([[the_record_says_subset_the_code_says_equality]]).
    """
    from market_pulse import pass2

    want = dict(pack["instruments"]["prompt_sha256"])
    got = {task: pass2.prompt_sha256(task) for task in sorted(pass2.PASS2)}
    unserved = sorted(set(want) - set(got))
    moved = {task: got[task] for task in sorted(want) if task in got and got[task] != want[task]}
    if unserved or moved:
        raise SystemExit(
            f"the pass-2 prompt shas on this pod are {got} and the registration pinned {want}"
            f" (unserved here: {unserved}; moved: {sorted(moved)})."
            " This checkout is not the registered instrument — stop before the model is loaded."
        )
    for label, path, pinned in (
        (
            "src/market_pulse/prompts.py",
            repo / "src" / "market_pulse" / "prompts.py",
            pack["instruments"]["parser"]["sha256"],
        ),
        (
            "src/market_pulse/pass2.py",
            repo / "src" / "market_pulse" / "pass2.py",
            pack["instruments"]["module"]["sha256"],
        ),
    ):
        live = sha256_of(path)
        if live != pinned:
            raise SystemExit(
                f"{label} hashes {live} here and the registration pinned {pinned} — the renderer"
                " and the record have parted. Stop before the model is loaded."
            )
    return {
        "prompt_sha256": got,
        "parser_sha256": sha256_of(repo / "src" / "market_pulse" / "prompts.py"),
        "module_sha256": sha256_of(repo / "src" / "market_pulse" / "pass2.py"),
    }


SWAPPED = {"render": render, "check_instrument": check_instrument}


@contextmanager
def as_pass2():
    """The two shipped names replaced for the length of one call, and put back after."""
    keep = {}
    for name in SWAPPED:
        if not hasattr(runner, name):
            raise SystemExit(
                f"scripts/reader_v5_pod_runner.py has no `{name}` any more, so this file is"
                " replacing something that no longer exists and the run would silently use the"
                " shipped behaviour. Stop and report."
            )
        keep[name] = getattr(runner, name)
    for name, value in SWAPPED.items():
        setattr(runner, name, value)
    try:
        yield
    finally:
        for name, value in keep.items():
            setattr(runner, name, value)


def smoke_leg(pack: dict, leg: dict) -> list[dict]:
    """The leg's first `smoke.units` items, held to the pack's own `smoke.ids`.

    A PREFIX of the one leg and never a second pack: the resume-skip of the shipped `run()` is what
    lets the same out-file take the remaining units after the go, so «the five F threads FIRST» is
    the whole mechanism and no number is typed on a command line.
    """
    items = leg["items"][: int(pack["smoke"]["units"])]
    ids = [one["id"] for one in items]
    if ids != list(pack["smoke"]["ids"]):
        raise SystemExit(
            f"the leg's first {len(ids)} items are {ids} and the pack's own `smoke.ids` says"
            f" {pack['smoke']['ids']}. The smoke leg is a PREFIX of the leg — stop and report."
        )
    return items


VERDICTS = ("GO", "STOP")
"""The only two words this runner will ACT on. Anything else is «not yet»."""


def read_token(token: Path) -> dict | None:
    """The go token, or None while it is not a verdict yet — and a half-copied file is not one.

    `scp` writes into place over some seconds and the poll can land in the middle of it, so a token
    that does not parse, or parses without one of the two registered verdicts in it, means KEEP
    WAITING. Reading a truncated GO as a STOP would throw away 74 units the guard had just
    authorised, on one unlucky poll, with no way to tell afterwards that it happened
    ([[a_retry_inherits_the_last_attempts_output]] read forwards: the file on shared storage is not
    necessarily the file somebody finished writing).
    """
    if not token.exists():
        return None
    try:
        gate = json.loads(token.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return None
    if not isinstance(gate, dict) or str(gate.get("verdict")) not in VERDICTS:
        return None
    return gate


def wait_for_go(token: Path, deadline: float, started: float, sleep=time.sleep) -> dict:
    """BLOCK until the Mac writes the go, or give up after the registered deadline.

    Returns the verdict it read. A token that is not a GO — or no token at all — ends this process
    without generating another unit: the pod then stops writing, its log stops rising, and rung 5
    kills it on the Mac's own clock. A runner that guessed GO would be spending money the guard
    never authorised ([[a_flag_that_asserts_turns_a_poll_into_a_verdict]]).
    """
    began = time.monotonic()
    while True:
        gate = read_token(token)
        if gate is not None:
            runner.say(started, f"GO token read at {token}: {gate['verdict']}")
            return gate
        left = deadline - (time.monotonic() - began)
        if left <= 0:
            runner.say(
                started,
                f"WAIT gave up: no {token} after {deadline:.0f}s — this pod answers nothing more"
                " and the Mac's liveness rung ends it",
            )
            return {"verdict": "NO-TOKEN"}
        runner.say(started, f"WAIT for the go at {token} — {left:.0f}s left of {deadline:.0f}")
        sleep(GO_POLL_SECONDS)


def main(argv: list[str] | None = None, loader=None, sleep=time.sleep) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=Path("/workspace/repo"))
    parser.add_argument("--go", type=Path, required=True)
    parser.add_argument(
        "--go-deadline",
        type=float,
        required=True,
        help="seconds to wait for the go before this pod stops answering (the record's rung S)",
    )
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    pack = json.loads(args.pack.read_text(encoding="utf-8"))
    (leg,) = fewshot.legs_of(pack, None)
    args.outdir.mkdir(parents=True, exist_ok=True)
    args.go.parent.mkdir(parents=True, exist_ok=True)
    out = args.outdir / leg["out"]
    shared = fewshot.once(loader or runner.load_reader)
    started = time.monotonic()

    smoke = smoke_leg(pack, leg)
    print(
        f"\n=== SMOKE {len(smoke)} of {len(leg['items'])} units · task {leg['task']} · {out} ===\n"
        f"=== {' · '.join(one['id'] for one in smoke)} ===",
        flush=True,
    )
    with as_pass2():
        code = runner.run({**pack, "task": leg["task"], "items": smoke}, out, args.repo, shared)
    if code:
        return code

    gate = wait_for_go(args.go, args.go_deadline, started, sleep=sleep)
    if str(gate.get("verdict")) != "GO":
        runner.say(started, f"STOP: the go says {gate.get('verdict')} — no unit beyond the smoke")
        return 0
    print(
        f"\n=== FULL {len(leg['items'])} units · the {len(smoke)} answered above are NOT re-asked"
        f" · {out} ===",
        flush=True,
    )
    with as_pass2():
        return runner.run(
            {**pack, "task": leg["task"], "items": leg["items"]}, out, args.repo, shared
        )


if __name__ == "__main__":
    raise SystemExit(main())
