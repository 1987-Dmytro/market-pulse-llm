#!/usr/bin/env python3
"""reader-v4's generation leg — the ONLY thing that runs on the rented pod.

Nothing here parses and nothing here scores: the parser and the scorer are the instrument, they are
pinned by sha in `results/prereg_reader_probe_v4.json`, and the pod's checkout is deliberately a
commit behind (re-staging it costs money this cap does not have). What crosses to the pod is a PACK
— the 23 thread items with the registered sha of each one's rendered request — and what comes back
is one raw reply per line.

**It refuses before it loads.** The model load is the expensive rung, so everything checkable is
checked first, on a pod that is only provisioning-warm: the three reader prompt shas and the parser
module's sha as THIS checkout renders them, then every item's rendered request against the sha the
registration pinned. A volume a session behind reads happily under the wrong text, and that is the
failure a sha check exists for.

**The clock is printed, not inferred.** Every line carries seconds since this process started,
unbuffered, because the contract's kill rule is a deadline a human watches go past. The first
`reply` line is what stops it.

**One line per reply, flushed as it lands.** A killed run must still show what it read.

    HF_HOME=/workspace/hf PYTHONPATH=/workspace/repo/src \\
    /workspace/venv/bin/python -u /workspace/reader_v4_pod_runner.py \\
        --pack /workspace/reader_v4_pack.json \\
        --out /workspace/reader_v4_pod.jsonl \\
        --repo /workspace/repo
"""

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path


def sha256_of_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def say(started: float, message: str) -> None:
    """One progress line, with the seconds this process has been alive on the front of it."""
    print(f"[{time.monotonic() - started:8.1f}s] {message}", flush=True)


def check_instrument(pack: dict, repo: Path, prompts) -> dict:
    """The handshake, run where the weights are — refuse unless this checkout IS the registration.

    Two checks and they answer different questions. The per-task shas say the registered texts are
    what this checkout renders; the module sha says the PARSER the Mac will read these replies with
    is the module this pod rendered them from. probe-b's registration learned that distinction the
    hard way, and reader-v3 proved the volume can be moved to a commit and stay there.

    The first check is over the tasks the PACK pins and not over `prompts.READER` whole, which is
    what `results/prereg_reader_probe_v4.json`'s own `prompt_rule` says in as many words: «a text
    registered LATER is not in this map and is not expected to be». It was written as a whole-dict
    equality, so the day a fourth reader text was registered this refusal fired on a pack nothing
    had touched — and with the wrong sentence, since what actually parted is the MODULE, which the
    check below catches and names ([[a_new_guard_can_be_shadowed_by_an_old_one]]). Nothing is lost
    by narrowing it: a pod carrying a different set of texts carries different `prompts.py` bytes.
    """
    want = dict(pack["instruments"]["prompt_sha256"])
    got = {task: prompts.prompt_sha256(task) for task in sorted(prompts.READER)}
    unserved = sorted(set(want) - set(got))
    moved = {task: got[task] for task in sorted(want) if task in got and got[task] != want[task]}
    if unserved or moved:
        raise SystemExit(
            f"the reader prompt shas on this pod are {got} and the registration pinned {want}"
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


def check_requests(pack: dict, prompts) -> list[dict]:
    """Every item rendered by THIS checkout, against the sha the registration pinned for it.

    Rendered rather than shipped: a pre-rendered string would prove only that the Mac and the pod
    agree about a string, and what has to be true is that the model is shown what the registration
    registered. A comment edited in the store between the two moves this number and nothing else.
    """
    task = pack["task"]
    rendered = []
    for item in pack["items"]:
        content = prompts.reader_messages_gm4(
            item["channel"],
            item["post_id"],
            item["post"],
            [(int(msg_id), text) for msg_id, text in item["comments"]],
            task=task,
        )[0]["content"]
        got = sha256_of_text(content)
        if got != item["rendering_sha256"]:
            raise SystemExit(
                f"{item['thread']}: this checkout renders {got} and the registration pinned"
                f" {item['rendering_sha256']}. The thread moved — stop and report."
            )
        rendered.append({**item, "chars": len(content)})
    return rendered


def load_reader(pack: dict, repo: Path):  # pragma: no cover — needs the GPU and 59 GB of weights
    """The READER config, loaded exactly the way the serving handler loads it.

    Mirrored from `scripts/serve_handler.py`'s base-only branch rather than reconstructed: the model
    id, the revision, the NF4 quantization and the adapter refusal all live there, and a second
    spelling of them is a second instrument ([[build_the_training_prompt_with_the_inference_call]]).
    """
    sys.path.insert(0, str(repo / "scripts"))
    import serve_handler

    from market_pulse import local_llm

    serving = pack["serving"]
    processor, model = local_llm.load_captioner(
        serving["model"], revision=serving["model_revision"]
    )
    serve_handler.assert_no_adapter(model)
    return local_llm.ReaderClient(processor, model)


def run(pack: dict, out: Path, repo: Path, loader=load_reader) -> int:
    started = time.monotonic()
    sys.path.insert(0, str(repo / "src"))
    from market_pulse import prompts

    instrument = check_instrument(pack, repo, prompts)
    items = check_requests(pack, prompts)
    say(started, f"instrument OK · parser {instrument['parser_sha256'][:16]}…")
    say(started, f"{len(items)} requests match the registration's per-thread shas")
    say(started, f"loading {pack['serving']['model']} @ {pack['serving']['model_revision'][:12]}…")

    client = loader(pack, repo)
    boot = time.monotonic() - started
    say(started, f"READY · boot {boot:.1f}s · the kill clock stops at the first reply below")

    task = pack["task"]
    with out.open("a", encoding="utf-8") as handle:
        for index, item in enumerate(items):
            at = time.monotonic()
            # the item is handed over whole: `ReaderClient.render` reads channel / post_id / post /
            # comments and ignores the rest, so the object the sha was checked on is the object the
            # model is shown — no second construction in between
            reply = client.read(task, [item])[0]
            row = {
                "index": index,
                "thread": item["thread"],
                "rendering_sha256": item["rendering_sha256"],
                "reply": reply["content"],
                "finish_reason": reply.get("finish_reason"),
                "usage": reply.get("usage"),
                "seconds": round(time.monotonic() - at, 3),
                "elapsed_since_start": round(time.monotonic() - started, 3),
                "boot_seconds": round(boot, 3),
            }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()
            say(
                started,
                f"reply {index + 1:2d}/{len(items)} {item['thread']:32s}"
                f" {row['seconds']:6.1f}s · {len(reply['content']):5d} chars"
                f" · finish {row['finish_reason']}",
            )
    say(started, f"DONE · {len(items)} replies · {out}")
    return 0


def main(argv: list[str] | None = None, loader=load_reader) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=Path("/workspace/repo"))
    args = parser.parse_args(argv)
    pack = json.loads(args.pack.read_text(encoding="utf-8"))
    return run(pack, args.out, args.repo, loader=loader)


if __name__ == "__main__":
    raise SystemExit(main())
