#!/usr/bin/env python3
"""pass1-fewshot's generation leg — the only thing that runs on the rented pod, both legs, one load.

`scripts/pass1_pod_runner.py` is CALLED, never edited: its pass-1 render and its handshake are
pinned by `results/prereg_lora_b.json` and are already paid for. Exactly two things are this
contract's own and they are swapped in around the call.

**The render carries the examples block.** `prompts.pass1_messages_gm4` grew an `examples=`
keyword for v2; the shipped pass-1 render does not pass one, so a v2 item rendered through it would
raise. This one passes `item["examples"]` and hands everything that is not pass 1 back to the
shipped chain, exactly as the file it wraps hands the reader's tasks back — the branch is a call
this run MAKES, through `ReaderClient.__init__`'s own template probe, and not defensive programming
([[a_stub_replaces_the_guard_it_should_trigger]]).

**A pack has LEGS and the model is loaded ONCE for all of them.** `results/pass1_dev_pack.json`
carries the same 200 rows twice — the base leg under v1 with no examples, the v2 leg under v2 with
five — and each leg names the out-file it is answered into. Running them as two invocations would
pay the 350-second boot twice on a billed pod; running them into ONE file would let the resume skip
half of them, because a leg's ids are the other leg's ids with a different suffix. So: one process,
one client, one out-file per leg, and the shipped `run()` untouched underneath.

    HF_HOME=/workspace/hf PYTHONPATH=/workspace/repo/src \\
    /workspace/venv/bin/python -u /workspace/repo/scripts/pass1_fewshot_pod_runner.py \\
        --pack /workspace/repo/results/pass1_dev_pack.json \\
        --outdir /workspace/run --repo /workspace/repo
    # ... the dev gate says GO on the Mac, and only then:
    ...   --pack /workspace/repo/results/pass1_probe_b_pack_v2.json --outdir /workspace/run
"""

import argparse
import json
import sys
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pass1_pod_runner as pass1  # noqa: E402
import reader_v5_pod_runner as runner  # noqa: E402


def render(prompts, item: dict, task: str) -> str:
    """One pass-1 request, with v2's labelled-examples block where the item carries one.

    `examples` is passed as the item holds it and is never defaulted: the renderer refuses a v2
    request with no block and a v1 request with one, so a pack that half-applied the revision stops
    here rather than being served as a third instrument nobody registered.
    """
    if task not in prompts.PASS1:
        return pass1.SHIPPED_RENDER(prompts, item, task)
    return prompts.pass1_messages_gm4(
        item["channel"],
        item["post_id"],
        item["topic"],
        item["entities"],
        item["msg_id"],
        item["text"],
        task=task,
        examples=item.get("examples"),
    )[0]["content"]


@contextmanager
def as_fewshot():
    """The pass-1 swap, then the examples-aware render ON TOP of it, and both put back after.

    `pass1_pod_runner.as_pass1()` installs the handshake this family needs and its own render; the
    second swap replaces only the render. Nesting rather than re-declaring the pair keeps the
    handshake a single implementation — a copy of `check_instrument` here would be a second answer
    to «is this checkout the registered instrument».
    """
    with pass1.as_pass1():
        if not hasattr(runner, "render"):
            raise SystemExit(
                "scripts/reader_v5_pod_runner.py has no `render` any more — this file would be"
                " replacing something that no longer exists. Stop and report."
            )
        keep = runner.render
        runner.render = render
        try:
            yield
        finally:
            runner.render = keep


def legs_of(pack: dict, only: str | None) -> list[dict]:
    """The legs to answer, in the pack's own order. `--only` narrows and never reorders."""
    legs = pack.get("legs")
    if not legs:
        raise SystemExit(
            "this pack carries no `legs`. Every pack of this contract names its legs and the"
            " out-file each one is answered into — a leg nobody named is a leg nobody can resume."
        )
    if only is None:
        return list(legs)
    chosen = [leg for leg in legs if leg["name"] == only]
    if not chosen:
        raise SystemExit(f"{only}: not a leg of this pack — {[leg['name'] for leg in legs]}")
    return chosen


def once(loader):
    """`load_reader` wrapped so the SECOND leg gets the client the first one built.

    The boot is the expensive half of a short run — 350 s measured on this stack against 5 s a call
    — and it is charged per model load, not per leg. The wrapper keeps the shipped `run()` exactly
    as it is: it still calls a loader, and the loader still returns a client.
    """
    built = {}

    def load(pack: dict, repo: Path):
        if "client" not in built:
            built["client"] = loader(pack, repo)
        return built["client"]

    return load


def main(argv: list[str] | None = None, loader=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=Path("/workspace/repo"))
    parser.add_argument("--only", help="answer just this leg (default: every leg, in pack order)")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    pack = json.loads(args.pack.read_text(encoding="utf-8"))
    legs = legs_of(pack, args.only)
    args.outdir.mkdir(parents=True, exist_ok=True)
    shared = once(loader or runner.load_reader)

    with as_fewshot():
        for leg in legs:
            out = args.outdir / leg["out"]
            print(
                f"\n=== leg {leg['name']} · task {leg['task']} · {len(leg['items'])} units"
                f" · {out} ===",
                flush=True,
            )
            code = runner.run(
                {**pack, "task": leg["task"], "items": leg["items"]},
                out,
                args.repo,
                loader=shared,
            )
            if code != 0:
                return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
