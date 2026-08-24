#!/usr/bin/env python3
"""lora-c's generation leg — the v3 family served, and an adapter carried. A sibling, not a fork.

`scripts/pass1_fewshot_pod_runner.py` is CALLED, and through it `scripts/pass1_pod_runner.py` and
`scripts/reader_v5_pod_runner.py`. Each of those is pinned by a sealed record and none is edited:
the legs, the one-load-for-every-leg wrapper, the resume-skip, the balanced-object stop, the
per-row persistence and the progress lines are all theirs, already paid for three times.

**Why this file exists, measured at $0 before any pod.** `results/lora_c_eval_pack.json` pins
`pass1_comment_gm4_v2` and `pass1_comment_gm4_v3`, and the shipped chain serves neither leg:

- `pass1_pod_runner.check_instrument` builds the served family out of `prompts.PASS1`, which is
  `{v1, v2}`. v3 is not in it and may not be added — `pass1_v3.PASS1_TASK_V3`'s own docstring says
  «not in `prompts.PROMPTS` and not addable to it». So the handshake REFUSES this pack, and it
  refuses the base-v2 leg with it, because both legs read one pack and the map is compared whole.
- `pass1_fewshot_pod_runner.render` hands `task not in prompts.PASS1` to the shipped chain, which
  hands it to the READER's renderer, which raises `KeyError: 'post'`. That is the shape that killed
  pass1-probe's attempt at 427 billed seconds with the model loaded and nothing read
  ([[a_stub_replaces_the_guard_it_should_trigger]]).
- and `pass1_fewshot_pod_runner.main` has no `--adapter`, which lora-c's two arm legs need.

All three were driven on the shipped chain BEFORE this file was written, and all three are driven
again in `tests/test_pass1_v3_pod_runner.py`. A transport gap named in prose is a transport gap
somebody re-discovers on a meter ([[a_frozen_record_is_an_input_to_shipped_code]]).

**Three names move and nothing is copied.** `fewshot.render` (so the v3 branch sits in front of the
examples-aware one), `pass1.SWAPPED["check_instrument"]` (so the handshake knows the v3 family), and
the loader (so an adapter can ride). The swaps are undone in a `finally`, and each asserts that what
it replaces EXISTS first — a rename one layer down has to be a loud failure and never a silent
fall-back to the behaviour this file was written to replace ([[a_moved_guard_that_left_its_copy]]).

    # base v2 and base v3, one load, no adapter:
    HF_HOME=/workspace/hf PYTHONPATH=/workspace/repo/src \\
    /workspace/venv/bin/python -u /workspace/repo/scripts/pass1_v3_pod_runner.py \\
        --pack /workspace/repo/results/lora_c_eval_pack.json \\
        --outdir /workspace/run/base --repo /workspace/repo
    # arm A's eval — the v3 leg only, with the adapter it trained:
    ...   --only v3 --outdir /workspace/run/eval_a --adapter /workspace/run/arm_a/adapter
"""

import json
import sys
from contextlib import contextmanager
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pass1_fewshot_pod_runner as fewshot  # noqa: E402
import pass1_pod_runner as pass1  # noqa: E402
from reader_v4_pod_runner import sha256_of  # noqa: E402

from market_pulse import pass1_v3  # noqa: E402

SHIPPED_RENDER = fewshot.render
"""The examples-aware v1/v2 render, captured at IMPORT — so the dispatch below cannot recurse into
itself once `fewshot.render` is replaced."""


def render(prompts, item: dict, task: str) -> str:
    """One request. v3 goes to v3's renderer; every other task down the shipped chain, unchanged.

    The v3 request is v2's with the rationale clause and a richer examples block, and it is rendered
    ON THE POD from the pack's own fields — shipping the string would prove the two machines agree
    about a string, not that the model is shown what the registration registered.

    `examples` is passed as the item holds it and is never defaulted: `pass1_messages_gm4_v3`
    refuses an empty block by name, because v3 has no no-examples arm and a request without one
    would be a third instrument nobody registered.
    """
    if task != pass1_v3.PASS1_TASK_V3:
        return SHIPPED_RENDER(prompts, item, task)
    return pass1_v3.pass1_messages_gm4_v3(
        item["channel"],
        item["post_id"],
        item["topic"],
        item["entities"],
        item["msg_id"],
        item["text"],
        examples=item["examples"],
    )[0]["content"]


def check_instrument(pack: dict, repo: Path, prompts) -> dict:
    """The handshake over the family this pack actually names — v1, v2 AND v3.

    Two questions, both still asked, plus one this line adds. The per-task shas say the registered
    TEXT is what this checkout renders; `prompts.py`'s sha says the parser the Mac will read these
    replies with is the module this pod rendered them from; and `pass1_v3.py` gets a sha of its own
    because the pack pins one and the shipped handshake knows nothing about that module. A v3
    renderer that moved without its pack is exactly the failure the other two exist for.

    The subset rule is inherited and not re-invented: a text registered LATER is not in an older
    pack's map and is not expected to be ([[the_record_says_subset_the_code_says_equality]]).
    """
    want = dict(pack["instruments"]["prompt_sha256"])
    got = {task: prompts.prompt_sha256(task) for task in sorted(prompts.PASS1)}
    got |= {task: pass1_v3.prompt_sha256(task) for task in sorted(pass1_v3.PASS1_V3)}
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
    v3_module = sha256_of(repo / "src" / "market_pulse" / "pass1_v3.py")
    if v3_module != pack["instruments"]["module_v3_sha256"]:
        raise SystemExit(
            f"src/market_pulse/pass1_v3.py hashes {v3_module} here and the registration pinned"
            f" {pack['instruments']['module_v3_sha256']} — the v3 renderer this pod would use is"
            " not the one this pack was built with."
        )
    return {"prompt_sha256": got, "parser_sha256": module, "module_v3_sha256": v3_module}


@contextmanager
def as_v3():
    """`fewshot.render` and pass 1's handshake replaced, for the length of one call.

    It is `fewshot.render` that moves and not `runner.render`: `as_fewshot()` installs its own
    module global into the reader every time it is entered, so a swap made outside it would be
    overwritten the moment `fewshot.main` starts. Same for the handshake — `as_pass1()` reads
    `pass1.SWAPPED`, a dict built at import time, so replacing `pass1.check_instrument` alone looks
    correct, changes nothing, and fails on the pod.
    """
    if not hasattr(fewshot, "render") or "check_instrument" not in pass1.SWAPPED:
        raise SystemExit(
            "the shipped chain no longer carries `pass1_fewshot_pod_runner.render` or"
            " `pass1_pod_runner.SWAPPED['check_instrument']` — this file would be replacing"
            " something that no longer exists and the run would use the shipped behaviour. Stop."
        )
    keep_render, keep_table = fewshot.render, pass1.SWAPPED
    fewshot.render = render
    pass1.SWAPPED = {**keep_table, "check_instrument": check_instrument}
    try:
        yield
    finally:
        fewshot.render, pass1.SWAPPED = keep_render, keep_table


def main(argv: list[str] | None = None, loader=None) -> int:
    """`pass1_fewshot_pod_runner.main`, with the v3 family served and `--adapter` carried.

    `--adapter` is consumed here and `pass1_pod_runner`'s own `split`/`with_adapter`/`adapter_record`
    do the work: the adapter record beside the out-file is what the scorer reads to know which
    adapter answered, and re-deriving it here would be a second answer to that question.
    """
    argv = list(sys.argv[1:] if argv is None else argv)
    adapter, _, rest = pass1.split(argv)
    if adapter is not None:
        outdir = Path(rest[rest.index("--outdir") + 1])
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "adapter.json").write_text(
            json.dumps(pass1.adapter_record(adapter), ensure_ascii=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
    with as_v3():
        return fewshot.main(rest, loader=loader or pass1.with_adapter(adapter))


if __name__ == "__main__":
    raise SystemExit(main())
