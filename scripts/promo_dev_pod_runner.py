#!/usr/bin/env python3
"""The pod side of the promo-signal dev loop — one pack, two legs, one out-file, one GO.

Nothing about the transport is new. `reader_v5_pod_runner` is IMPORTED and exactly ONE function of
it is swapped — the render — the way `pass2_r2_pod_runner` swaps in pass 2's; the resume clause
(`already_answered`), the per-item sha check, the balanced-prefix stop, the flushing writer and the
row shape are the shipped ones, so a reply written here is a reply of the same instrument family.

**Two legs on one pod, dispatched by the ITEM and never by inspection.** Leg A is the promo-signal
prompt — `market_pulse.promo_prompts`, a NEW module because `prompts.py` is pinned — and leg B is
the 16 C2 posts S4 left without an evidence row, under the REGISTERED `positions_text_gm4`. The
render below reads `item["task"]`, so one pack carries both and one boot pays for both.

**The GO between them is what makes the smoke affordable.** The registration prices the smoke and
iteration 1 together; the pod answers the three smoke units, stops, and waits for the Mac to read
the measured rate against ruling 03.09 (b)'s decision table. A runner that guessed GO would spend
money nobody authorised, so no token — or any word but GO — ends this process with 37 units unasked.

    python3 scripts/promo_dev_pod_runner.py --pack /workspace/run/promo_dev40_pack.json \\
        --out /workspace/run/promo_dev40_iter1.jsonl --repo /workspace/repo \\
        --go /workspace/run/promo_go --go-deadline 1800
"""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pass2_pod_runner as pass2  # noqa: E402
import reader_v5_pod_runner as runner  # noqa: E402

PROMO_TASK = "promo_signals_gm4_v1"
POST_TASK = "positions_text_gm4"

SHIPPED_RENDER = runner.render
"""The reader's render, captured at IMPORT — before the swap, so the dispatch below cannot recurse
into itself the moment `render` replaces the module global."""


def render(prompts, item: dict, task: str) -> str:
    """One request, chosen by the ITEM's own task.

    The fallback is a call this run MAKES and not a defensive branch: `local_llm.ReaderClient`
    probes the chat template through `self.render(prompts.READER_TASK_V2, {…})` inside its
    CONSTRUCTOR, where a swap that assumed every item was leg A's would raise before any test could
    see it ([[a_stub_replaces_the_guard_it_should_trigger]]).
    """
    from market_pulse import promo_prompts

    kind = item.get("task", task)
    if kind == PROMO_TASK:
        return promo_prompts.render(
            item["channel"],
            item["post_id"],
            item.get("post") or "",
            [{"msg_id": msg_id, "text": text} for msg_id, text in item.get("comments") or ()],
        )
    if kind == POST_TASK:
        return prompts.positions_messages_text_gm4(item["text"])[0]["content"]
    return SHIPPED_RENDER(prompts, item, task)


def check_law(pack: dict, repo: Path) -> dict:
    """The promo instrument's own handshake: this checkout IS the codebook the pack registered.

    `reader_v4_pod_runner.check_instrument` answers the same question for `prompts.py` and cannot
    answer it for a module it does not know. Both run — that one inside `runner.run`, this one
    before the model is loaded — because leg A's law lives in neither the reader's prompt shas nor
    its parser sha ([[provenance_cannot_name_itself]] read forwards: name the file that moved)."""
    sys.path.insert(0, str(repo / "src"))
    from market_pulse import promo_prompts

    want = pack["instruments"]["leg_a"]
    got = promo_prompts.codebook_version()
    if got != want["codebook_version"]:
        raise SystemExit(
            f"this checkout's codebook hashes {got} and the pack registered"
            f" {want['codebook_version']} — the LAW moved between the Mac and the pod. Stop before"
            " the model is loaded: every reply would be under a prompt nothing registered."
        )
    return {"codebook_version": got}


def once(loader):
    """One model load for both `runner.run` calls — the GO sits between them, not a second boot."""
    held = {}

    def load(pack, repo):
        if "client" not in held:
            held["client"] = loader(pack, repo)
        return held["client"]

    return load


def main(argv: list[str] | None = None, loader=runner.load_reader, sleep=time.sleep) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=Path("/workspace/repo"))
    parser.add_argument("--go", type=Path, required=True)
    parser.add_argument("--go-deadline", type=float, required=True)
    args = parser.parse_args(argv)

    started = time.monotonic()
    pack = json.loads(args.pack.read_text(encoding="utf-8"))
    law = check_law(pack, args.repo)
    runner.say(started, f"codebook {law['codebook_version'][:16]}… matches the pack")

    runner.render = render
    held = once(loader)
    smoke = [item for item in pack["items"] if item.get("smoke")]
    if not smoke:
        raise SystemExit("the pack carries no smoke units — the rate would be measured on nothing")

    code = runner.run(pack | {"items": smoke}, args.out, args.repo, loader=held)
    if code:
        return code
    runner.say(started, f"SMOKE DONE · {len(smoke)} units · waiting for {args.go}")
    gate = pass2.wait_for_go(args.go, args.go_deadline, started, sleep=sleep)
    if str(gate.get("verdict")) != "GO":
        runner.say(started, f"no GO ({gate.get('verdict')}) — {len(pack['items']) - len(smoke)} units unasked")
        return 0
    return runner.run(pack, args.out, args.repo, loader=held)


if __name__ == "__main__":
    raise SystemExit(main())
