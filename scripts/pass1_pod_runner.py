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

`--adapter` is this file's third thing and it is lora-b's: the PEFT adapter goes on AROUND the
model `local_llm` constructs, after the shipped loader has built its client. `local_llm.py` is
pinned and is not edited, and neither is the shipped runner's argument parser — the flag is
consumed here and what reaches `reader_v5_pod_runner.main` is exactly the argv it has always
parsed.

    HF_HOME=/workspace/hf PYTHONPATH=/workspace/repo/src \\
    /workspace/venv/bin/python -u /workspace/pass1_pod_runner.py \\
        --pack /workspace/pass1_probe_pack.json \\
        --out /workspace/pass1_probe_pod.jsonl \\
        --repo /workspace/repo \\
        --adapter /workspace/run/arm_a/adapter
"""

import argparse
import json
import sys
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import reader_v5_pod_runner as runner  # noqa: E402
from reader_v4_pod_runner import sha256_of  # noqa: E402


SHIPPED_RENDER = runner.render
"""The reader's render, captured at IMPORT — before any swap, so the dispatch below cannot recurse
into itself the moment `as_pass1()` replaces the module global."""


def render(prompts, item: dict, task: str) -> str:
    """One pass-1 request — the topic, the thread's resolved entities, and ONE comment.

    Rendered from the pack's own fields on the pod, exactly as the reader's is: shipping the string
    would prove the two machines agree about a string, not that the model is shown what the
    registration registered.

    **A task that is not pass 1's goes to the reader's own render, and that branch is not defensive
    programming — it is a call this run MAKES.** `local_llm.ReaderClient.__init__` probes the chat
    template through `self.render(prompts.READER_TASK_V2, {…})` before it will build a client at all,
    so a swap that assumed every call was a pass-1 item raised `KeyError: 'topic'` inside the
    CONSTRUCTOR. pass1-probe's attempt died exactly there, at 427 billed seconds with the model
    loaded and nothing read, and the stub-driven test could not see it because a fake client replaces
    the very constructor whose self-check makes the call.
    """
    if task not in prompts.PASS1:
        return SHIPPED_RENDER(prompts, item, task)
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

    **The first check is over the tasks the PACK pins and not over `prompts.PASS1` whole.** It was
    written as a whole-dict equality, and `docs/PROMPT-pass1-fewshot.md` D0.2 registered a second
    pass-1 text — so the day `pass1_comment_gm4_v2` existed, this refused every pack nothing had
    touched, and with the wrong sentence. The reader's own handshake had already been narrowed for
    exactly this, one family earlier, and the narrowing is copied here rather than re-invented: a
    text registered LATER is not in an older pack's map and is not expected to be. Nothing is lost —
    a pod carrying a different set of texts carries different `prompts.py` bytes, which is the
    second check ([[the_record_says_subset_the_code_says_equality]]).
    """
    want = dict(pack["instruments"]["prompt_sha256"])
    got = {task: prompts.prompt_sha256(task) for task in sorted(prompts.PASS1)}
    unserved = sorted(set(want) - set(got))
    moved = {task: got[task] for task in sorted(want) if task in got and got[task] != want[task]}
    if unserved or moved:
        raise SystemExit(
            f"the pass-1 prompt shas on this pod are {got} and the registration pinned {want}"
            f" (unserved here: {unserved}; moved: {sorted(moved)})."
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


def split(argv: list[str] | None) -> tuple[Path | None, Path | None, list[str]]:
    """`--adapter` (and a peek at `--out`) taken out of the argv the shipped runner parses.

    The shipped parser knows three options and `argparse` errors on a fourth, so the alternative
    would be editing a file two frozen registrations pin by sha. `--out` is re-appended because it
    IS the shipped runner's and this only needed to read it.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--adapter", type=Path)
    parser.add_argument("--out", type=Path)
    ours, rest = parser.parse_known_args(argv)
    if ours.out is not None:
        rest += ["--out", str(ours.out)]
    return ours.adapter, ours.out, rest


def attach(client, adapter: Path):
    """Wrap the model `local_llm` built in the PEFT adapter, and REFUSE if the wrap did not take.

    `serve_handler.assert_no_adapter` runs inside `runner.load_reader`, which is called BEFORE
    this: the base-only handshake is not skipped, it is passed and then deliberately reversed by a
    run that registers an adapter. The refusal below is the other half — `from_pretrained` on a
    path with no adapter in it can hand back something that answers every job looking exactly like
    the base, and a run that quietly evaluated the base as an arm would publish an ablation with no
    ablation in it.
    """
    from peft import PeftModel

    model = PeftModel.from_pretrained(client.model, str(adapter))
    if not sorted(getattr(model, "peft_config", None) or ()):
        raise SystemExit(
            f"{adapter} produced a model carrying no peft_config, so nothing was attached and this"
            " run would score the BASE under an arm's name. Stop and report."
        )
    client.model = model
    return client


def with_adapter(adapter: Path | None):
    """The loader the shipped runner calls: its own, or its own plus the wrap."""
    if adapter is None:
        return runner.load_reader

    def load(pack: dict, repo: Path):
        return attach(runner.load_reader(pack, repo), adapter)

    return load


def adapter_record(adapter: Path) -> dict:
    """What was mounted, hashed file by file — written BEFORE the first reply.

    `PeftModel.from_pretrained` injects the adapter into the base modules in place, so the wrapped
    object and the base are not distinguishable by identity afterwards and no evidence row says
    which arm produced it. This is the observable: the arm's own weights, hashed, beside the
    evidence file they answered into ([[baseline_before_the_run_not_after]]).
    """
    files = sorted(one for one in adapter.iterdir() if one.is_file())
    return {
        "adapter": str(adapter),
        "files": {one.name: sha256_of(one) for one in files},
        "rule": (
            "written before the run, from the directory that was mounted. An evidence file with no"
            " record beside it was answered by the base"
        ),
    }


def main(argv: list[str] | None = None, loader=None) -> int:
    adapter, out, rest = split(sys.argv[1:] if argv is None else argv)
    if adapter is not None and out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.with_suffix(out.suffix + ".adapter.json").write_text(
            json.dumps(adapter_record(adapter), ensure_ascii=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
    with as_pass1():
        return runner.main(rest, loader=loader or with_adapter(adapter))


if __name__ == "__main__":
    raise SystemExit(main())
