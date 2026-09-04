#!/usr/bin/env python3
"""The pod side of the promo-signal dev loop — one pack, two legs, one out-file, one GO.

Nothing about the transport is new. `reader_v5_pod_runner` is IMPORTED and TWO of its functions are
swapped, the way `pass2_r2_pod_runner` swaps in pass 2's: the render, and the balanced prefix — which
gains the ARRAY leg B's registered prompt answers with and keeps the shipped rule verbatim for every
object. The resume clause (`already_answered`), the per-item sha check, the flushing writer and the
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
            # named by column, not unpacked: a pack written before ruling 04.09 (g) carries pairs,
            # and a row with no `sender_anon_id` key is simply a comment no admin wrote
            [
                dict(zip(("msg_id", "text", "sender_anon_id"), one, strict=False))
                for one in item.get("comments") or ()
            ],
        )
    if kind == POST_TASK:
        return prompts.positions_messages_text_gm4(item["text"])[0]["content"]
    return SHIPPED_RENDER(prompts, item, task)


def balanced_prefix(text: str, shipped):
    """The prefix that closes the first top-level VALUE — an ARRAY as well as an object.

    Leg B's registered prompt ends «the first thing you write is "["», and the shipped rule closes
    the first top-level OBJECT: on a post with three offers it would keep one and drop the `]`, and
    every one of the 16 would come back unparseable with `balanced: true`. The rule is dispatched on
    the answer's shape — leg A's template asks for `{"about": …}` — so leg A keeps the shipped rule
    VERBATIM and nothing sealed moves.

    **The fence is read off BEFORE the dispatch, and that is ruling 04.09 (m).** Iteration 2 answered
    `@VARUS_channel:6216` with an array inside a ```` ```json ```` fence — the codebook asks for JSON
    and never fixes the outer container — and a dispatch on `text.lstrip()` read `` ` `` as «not an
    array»: the object rule ran, ENDED GENERATION at the first element's brace after 88 tokens, and 17
    of the thread's 18 answers were never written, which no parse-time repair can recover. All 40
    answers of that iteration were fenced, so the dispatch was reading the fence and never the shape.
    `promo_prompts.unfence` is the one spelling of «read the fence off» and it is imported, not
    re-written here ([[two_values_for_one_input_get_quoted_kindly]]); what is returned stays a prefix
    of the emitted TEXT, fence opener included, because that is what `run` persists and what
    `promo_prompts.parse` unfences again on the Mac.

    An array closes by `json.JSONDecoder().raw_decode`, the parser itself, rather than a second
    depth-walk — same reason. `None` while it has not closed is the run-to-the-ceiling case and is
    left to the ceiling: generation simply continues.
    """
    from market_pulse import promo_prompts

    lead = promo_prompts.unfence(text)[0].lstrip()
    if not lead.startswith("["):
        return shipped(text)
    try:
        _, end = json.JSONDecoder().raw_decode(lead)
    except ValueError:
        return None
    return text[: text.index(lead) + end]


def close_arrays_too(reader_v5) -> None:
    """Wire the rule above into the module BOTH readers of it resolve at call time.

    `stop_at_balanced` is handed this module and `run` imports it, so one attribute serves the stop
    that ends generation and the prefix that is persisted; patching only the stop would end
    generation on a whole array and still write a third of it down. Idempotent, and the shipped
    callable is captured before the attribute is replaced — a patch that called itself would recurse
    on the first reply.
    """
    shipped = reader_v5.balanced_prefix
    if getattr(shipped, "closes_arrays", False):
        return

    def dispatched(text: str):
        return balanced_prefix(text, shipped)

    dispatched.closes_arrays = True
    reader_v5.balanced_prefix = dispatched


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
    from market_pulse import reader_v5

    close_arrays_too(reader_v5)
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
