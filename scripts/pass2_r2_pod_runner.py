#!/usr/bin/env python3
"""The pod side of `pass2-signals-r2` — one leg, one out-file, no go and no wait.

r1's runner had a smoke prefix and a go-wait because rung S′ decided the remaining 74 in the middle
of the session. r2 has a registered rate, so this is the shipped reader loop with pass 2's renderer
and pass 2's handshake swapped in, called ONCE over all 79 units. The four rows r1 bought are in the
out-file before this process starts and `reader_v5_pod_runner.already_answered` skips them — which
is why the seeded file has to be ON THE POD and not only on the Mac. The runbook scp's it; a test
asserts the runbook does.

**The renderer is r1's, not r2's, and that is deliberate.** `market_pulse.pass2_r2` differs from
`market_pulse.pass2` in its input ceiling and in its parser, and neither reaches a rendered string:
the widest unit is 11 856 characters, under both ceilings, and the parser runs on the Mac. So the
pod renders with the module r1's replies were rendered by, and `check_requests` holds all 79 to the
pack's `rendering_sha256` before the model is loaded. Both modules are hashed by the handshake
anyway — the one that renders and the one that will read the answers.

    python3 scripts/pass2_r2_pod_runner.py --pack /workspace/run/pass2_r2_pack.json \\
        --outdir /workspace/run --repo /workspace/repo
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


def render(prompts, item: dict, task: str) -> str:
    """One pass-2 request — the post, the thread's bought names, and the filtered comments.

    A task that is not pass 2's goes to the reader's own render, and that branch is a call this run
    MAKES: `local_llm.ReaderClient.__init__` probes the chat template through
    `self.render(prompts.READER_TASK_V2, {…})` before it will build a client at all, so a swap that
    assumed every call was a pass-2 item would raise inside the CONSTRUCTOR — where a stub-driven
    test cannot see it ([[a_stub_replaces_the_guard_it_should_trigger]]).
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
    """The handshake — the registered TEXT, and BOTH modules this run depends on.

    r1 hashed `pass2.py` because it carries the text and the renderer. r2 hashes `pass2_r2.py`
    beside it, because that is the module whose parser will decide what these replies say: a pod
    that rendered from the registered bytes and a Mac that read them with a different parser would
    be two instruments answering one question, and only one of them is in the record
    ([[the_guard_hashes_the_half_that_cannot_move]]).
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
        (
            "src/market_pulse/pass2_r2.py",
            repo / "src" / "market_pulse" / "pass2_r2.py",
            pack["instruments"]["module_r2"]["sha256"],
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
        "module_r2_sha256": sha256_of(repo / "src" / "market_pulse" / "pass2_r2.py"),
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


def carried(out: Path, pack: dict) -> list[str]:
    """The ids already in the out-file that the pack says were CARRIED — announced, never assumed.

    A run that silently skipped four units because a file happened to contain them would look
    exactly like a run whose pack was wrong. This prints them and refuses if the file carries a row
    the pack does not name as carried and the pod did not write.

    **An ABSENT file is the same refusal as an empty one.** The first version returned `[]` for a
    missing out-file and the whole check was skipped — so a seed whose scp silently failed left a
    pod that bought all 79 units and re-bought the four r1 paid for, which is the one thing the
    contract's DO NOT names in as many words. Staging does `rm -rf /workspace/run`, so absence is
    the DEFAULT state and the guard has to survive it ([[a_file_guard_is_not_a_row_filter]]).
    """
    lines = out.read_text(encoding="utf-8").splitlines() if out.exists() else []
    rows = []
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            # a TORN LAST line is the mid-write race the shipped `already_answered` also tolerates:
            # its unit is simply not answered yet. Any earlier line is a damaged file
            # ([[the_hardening_did_not_reach_the_sibling_reader]])
            if index != len(lines) - 1:
                raise SystemExit(
                    f"{out} line {index + 1} is not JSON and it is not the last one. That is a"
                    " damaged file, not the mid-write race — stop before the model is loaded."
                ) from None
    named = set(pack["carried"]["ids"])
    seeded = [one["id"] for one in rows if one.get("carried_from")]
    if sorted(seeded) != sorted(named):
        state = (
            "does not exist"
            if not out.exists()
            else "is empty"
            if not rows
            else f"carries {sorted(seeded)} as carried rows"
        )
        raise SystemExit(
            f"{out} {state} and the pack names {sorted(named)}. The out-file this pod would resume"
            " into is not the one the registration seeded — the seed did not reach this pod, and"
            " the run would RE-BUY the threads r1 already paid for. Stop before the model is"
            " loaded."
        )
    for one in rows:
        if one.get("carried_from") and one["rendering_sha256"] != next(
            item["rendering_sha256"] for item in pack["legs"][0]["items"] if item["id"] == one["id"]
        ):
            raise SystemExit(
                f"carried row {one['id']} was answered against a rendering this pack does not"
                " produce. Stop before the model is loaded."
            )
    return sorted(seeded)


def main(argv: list[str] | None = None, loader=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=Path("/workspace/repo"))
    parser.add_argument(
        "--serving",
        default=runner.DEFAULT_SERVING,
        choices=sorted(runner.SERVING_TEMPLATES),
        help="which registered instrument to render with; the out-file carries the name",
    )
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    pack = runner.with_serving(json.loads(args.pack.read_text(encoding="utf-8")), args.serving)
    (leg,) = fewshot.legs_of(pack, None)
    args.outdir.mkdir(parents=True, exist_ok=True)
    out = args.outdir / runner.out_name(leg["out"], args.serving)
    started = time.monotonic()

    seeded = carried(out, pack)
    print(
        f"\n=== {len(leg['items'])} units · task {leg['task']}"
        f" · serving {args.serving} · {out} ===\n"
        f"=== carried and NOT re-asked: {len(seeded)} — {' · '.join(seeded) or 'none'} ===\n"
        f"=== owed by this pod: {len(leg['items']) - len(seeded)} ===",
        flush=True,
    )
    runner.say(started, f"{len(seeded)} carried rows verified against the pack's renderings")
    with as_pass2():
        return runner.run(
            {**pack, "task": leg["task"], "items": leg["items"]},
            out,
            args.repo,
            fewshot.once(loader or runner.load_reader),
        )


if __name__ == "__main__":
    raise SystemExit(main())
