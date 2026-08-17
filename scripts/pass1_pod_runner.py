#!/usr/bin/env python3
"""pass 1's generation leg — the ONLY thing that runs on the rented pod.

`scripts/reader_v5_pod_runner.py` is CALLED, never edited: the boot, the resume-skip with its
tolerant reader, the balanced-object stop, the per-row persistence and the progress lines are all
its, unchanged and already paid for twice. Exactly two things are pass 1's own and they are swapped
in around the call — the RENDER, because a pass-1 request is one comment with its thread's entity
block, and the HANDSHAKE, because the shipped one asks whether this checkout serves the four READER
texts and a pass-1 pack pins a different family.

Swapping module globals rather than editing: the v5 runner's sha is pinned inside two frozen
registrations, and a `render=` keyword would move it for a keyword ([[a_sealed_caller_forces_the_
default]]). The swap asserts that every name it replaces EXISTS first, so a rename in the shipped
runner is a loud failure here rather than a silent second implementation.

    HF_HOME=/workspace/hf PYTHONPATH=/workspace/repo/src \\
    /workspace/venv/bin/python -u /workspace/pass1_pod_runner.py \\
        --pack /workspace/pass1_probe_pack.json \\
        --out /workspace/pass1_probe_pod.jsonl \\
        --repo /workspace/repo
"""

import sys
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import reader_v5_pod_runner as runner  # noqa: E402
from reader_v4_pod_runner import sha256_of  # noqa: E402


def render(prompts, item: dict, task: str) -> str:
    """One pass-1 request — the topic, the thread's resolved entities, and ONE comment.

    Rendered from the pack's own fields on the pod, exactly as the reader's is: shipping the string
    would prove the two machines agree about a string, not that the model is shown what the
    registration registered.
    """
    return prompts.pass1_messages_gm4(
        item["channel"],
        item["post_id"],
        item["topic"],
        item["entities"],
        item["msg_id"],
        item["text"],
        task=task,
    )[0]["content"]


def check_instrument(pack: dict, repo: Path, prompts) -> dict:
    """The handshake for the pass-1 family — the shipped one's two questions, asked of this family.

    The shipped check compares the pack's map against `prompts.READER`, so a pass-1 pack reads as
    «unserved here» on a pod that is perfectly correct. Both questions still have to be answered and
    they are still different questions: the per-task shas say the registered TEXT is what this
    checkout renders, and the module sha says the parser the Mac will read these replies with is the
    module this pod rendered them from.
    """
    want = dict(pack["instruments"]["prompt_sha256"])
    got = {task: prompts.prompt_sha256(task) for task in sorted(prompts.PASS1)}
    if want != got:
        raise SystemExit(
            f"the pass-1 prompt shas on this pod are {got} and the registration pinned {want}."
            " This checkout is not the registered instrument — stop before the model is loaded."
        )
    module = sha256_of(repo / "src" / "market_pulse" / "prompts.py")
    if module != pack["instruments"]["parser"]["sha256"]:
        raise SystemExit(
            f"src/market_pulse/prompts.py hashes {module} here and the registration pinned"
            f" {pack['instruments']['parser']['sha256']} — the parser and the renderer have parted."
        )
    return {"prompt_sha256": got, "parser_sha256": module}


SWAPPED = {"render": render, "check_instrument": check_instrument}


@contextmanager
def as_pass1():
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


def main(argv: list[str] | None = None, loader=None) -> int:
    with as_pass1():
        return runner.main(argv, loader=loader or runner.load_reader)


if __name__ == "__main__":
    raise SystemExit(main())
