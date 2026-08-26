#!/usr/bin/env python3
"""reader-v5's generation leg — the ONLY thing that runs on the rented pod.

Everything reader-v4's runner refused before the model was loaded is refused here too, by IMPORTING
that runner rather than restating it: the three-prompt handshake and the module sha are
`reader_v4_pod_runner.check_instrument`, unchanged. What is new is what the sitting of 2026-08-17
ruled, and only that.

**Generation STOPS at the first balanced top-level JSON object.** Two of v4's four refusals were
`two disagreeing objects` — the model closed its object and went on writing. A prompt line asking it
not to is in v3 and v5 keeps it; the parser's refuse-on-conflict clause stays as defence. Neither is
the cure: a generation loop that ends at the closing brace is. The persisted raw reply is EXACTLY
the emitted prefix, cut by `reader_v5.balanced_prefix`, so what a reader sees on disk is what the
model produced up to that brace and never a repair. A reply that never balances runs to the ceiling
exactly as today.

**Nothing shipped is edited.** The stop is wired in with a model PROXY and a `render` override, so
`local_llm.ReaderClient.read` stays the one inference path in this repo — the model id, the
quantisation, the greedy decoding and the usage counters are its, not a second spelling of them
([[build_the_training_prompt_with_the_inference_call]]). Editing `local_llm.py` would also move a
sha three sealed registrations pin, for a keyword argument.

**The output ceiling comes from the PACK and is refused if absent.** A ceiling registered in a
record and never passed to the client is a ceiling nobody lifted
([[a_lifted_ceiling_is_not_lifted_code]]).

    HF_HOME=/workspace/hf PYTHONPATH=/workspace/repo/src \\
    /workspace/venv/bin/python -u /workspace/reader_v5_pod_runner.py \\
        --pack /workspace/reader_v5_pack.json \\
        --out /workspace/reader_v5_pod.jsonl \\
        --repo /workspace/repo
"""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from reader_v4_pod_runner import check_instrument, sha256_of_text  # noqa: E402

DEFAULT_SERVING = "READER"
SERVING_TEMPLATES = {DEFAULT_SERVING: "CHAT_TEMPLATE", "READER_THINK": "THINK_CHAT_TEMPLATE"}
"""The instrument names `--serving` accepts, and the `local_llm` template each one renders with.

A CLOSED table, the same shape `serving.CONFIG_OPS` is: a name outside it is refused rather than
falling through to the shipped default, because the one failure worth money here is a run that
believed it was thinking and rendered the closed-channel prompt.

`READER_THINK` is deliberately NOT in `market_pulse.serving.CONFIGS`. No HTTP worker serves it —
`load_reader` builds the client in this process — and `serve_handler.settings` refusing the unknown
name is the correct guard until one does. The name is registered where it is used: in the pack, and
in `results/prereg_think_zero_shot.json`.

The values are ATTRIBUTE NAMES and not the dicts themselves: this module is imported on the pod
before `repo/src` is on the path, so a table holding `local_llm.CHAT_TEMPLATE` could not be built
at import time at all.
"""


def template_of(config: str, local_llm):
    """The template `--serving <config>` renders with, or a refusal naming the closed table."""
    if config not in SERVING_TEMPLATES:
        raise SystemExit(
            f"{config}: not a serving name this runner knows — {sorted(SERVING_TEMPLATES)}."
            " A run under an unregistered instrument is a run nobody can read; stop and report."
        )
    return getattr(local_llm, SERVING_TEMPLATES[config])


def with_serving(pack: dict, config: str) -> dict:
    """The pack with ``serving.serving_config`` set — what :func:`load_reader` picks a template by.

    `serving_config` is the field every pack of this family already carries — the shipped ones say
    `READER` — so the switch writes into the record's own vocabulary rather than beside it. Carried
    in the PACK and not passed as an argument, for the reason the output ceiling is: what the run
    was served under has to be in the thing the record pins, not in an argv nobody kept.
    """
    return {**pack, "serving": {**pack["serving"], "serving_config": config}}


def out_name(name: str, config: str) -> str:
    """``leg["out"]``, carrying the serving name unless it is the shipped default.

    The default keeps the shipped filename, so nothing already on disk moves and the resume clause
    still finds what it wrote. Every other instrument says so in its own filename: a paired table is
    two files over the same rows, and the failure that would make it meaningless is reading one of
    them as the other ([[a_retry_inherits_the_last_attempts_output]]).
    """
    if config == DEFAULT_SERVING:
        return name
    stem, dot, ext = name.rpartition(".")
    return f"{stem}.{config}{dot}{ext}" if dot else f"{name}.{config}"


STOP_EVERY = 4
"""Tokens between two balance checks inside the generation loop.

Not 1, because the check decodes the whole answer so far and the loop is O(n) of them; not 32,
because every token past the closing brace is paid for. At v4's measured ~20 tok/s the overshoot is
under a fifth of a second and `balanced_prefix` trims it off the persisted bytes anyway — the stop
is about not GENERATING a second object, and four tokens cannot finish one."""


def say(started: float, message: str) -> None:
    """One progress line with the seconds this process has been alive — v4's, and for its reason:
    the kill rule is a deadline a human watches go past."""
    print(f"[{time.monotonic() - started:8.1f}s] {message}", flush=True)


def part_of(item: dict) -> tuple[int, int] | None:
    """`(i, n)` for a chunked item, or None. JSON has no tuples, so the pack carries a list."""
    part = item.get("part")
    return None if part is None else (int(part[0]), int(part[1]))


def render(prompts, item: dict, task: str) -> str:
    """One item's request — the chunk header included when the item is a chunk."""
    return prompts.reader_messages_gm4(
        item["channel"],
        item["post_id"],
        item["post"],
        [(int(msg_id), text) for msg_id, text in item["comments"]],
        task=task,
        part=part_of(item),
    )[0]["content"]


def check_requests(pack: dict, prompts) -> list[dict]:
    """Every item rendered by THIS checkout, against the sha the registration pinned for it.

    v4's loop with the chunk header in it. Not imported, because v4's renders no `part` and a chunk
    whose header was dropped would hash to something the registration never pinned — which this
    check would then report as a moved thread. One construction of the request per side, and both
    sides call `prompts.reader_messages_gm4`.
    """
    task = pack["task"]
    rendered = []
    for item in pack["items"]:
        content = render(prompts, item, task)
        got = sha256_of_text(content)
        if got != item["rendering_sha256"]:
            raise SystemExit(
                f"{item['id']}: this checkout renders {got} and the registration pinned"
                f" {item['rendering_sha256']}. The request moved — stop and report."
            )
        rendered.append({**item, "chars": len(content)})
    return rendered


def thought_and_answer(text: str, prompts) -> tuple[str, str | None]:
    """The working-out, and the ANSWER — `None` while a thought channel is open and unclosed.

    **The thought is not the answer, and a thought contains braces.** Under
    `local_llm.THINK_CHAT_TEMPLATE` the model writes its working-out first, and a model reasoning
    about the object it is about to emit writes `{` inside it — `balanced_prefix` would balance
    that. So while a channel is open and unclosed there is no answer at all, and the whole emission
    is thought; `local_llm.thought_fields` counts the same state the same way, every token spent.

    Both readers of the rule are here — the stop below decides whether to keep generating, `run`
    decides what to persist — and they must not drift: a `length` cut-off is precisely the state
    where the stop never fired, so a second copy of the rule would be exercised only on the rows
    the first one never saw ([[two_values_for_one_input_get_quoted_kindly]]).

    With no thinking channel this is `split_thought` unchanged, which is the identity.
    """
    thought, answer = prompts.split_thought(text)
    if not thought and prompts.THOUGHT_OPEN in text:
        return text, None
    return thought, answer


def stops_here(text: str, prompts, reader_v5) -> bool:
    """Has the ANSWER closed its first top-level object? The rule the criterion below applies.

    Split out of the `StoppingCriteria` so it can be driven with no GPU: the class needs
    `transformers`, this needs a string. That state is invisible to a fake client — it lives in
    `generate` — which is why it has a test of its own with both controls
    ([[a_stub_replaces_the_guard_it_should_trigger]]).
    """
    _, answer = thought_and_answer(text, prompts)
    return answer is not None and reader_v5.balanced_prefix(answer) is not None


def stop_at_balanced(processor, width: int, reader_v5, prompts):  # pragma: no cover — transformers
    """A `StoppingCriteria` that ends generation at the first balanced top-level object.

    Built here and not in `market_pulse` because it is the only thing in this file that needs
    `transformers` on the path, and the Mac's suite has to be able to import everything else.

    Decoded with the specials KEPT: `<|channel>` and `<channel|>` are special tokens, and the rule
    above cannot see a boundary that `skip_special_tokens=True` has erased. No reply this repo has
    bought carries either marker in its generated half, so the shipped path reads the same text it
    always did with `<turn|>` on the end of it — which has no braces and no quotes.
    """
    from transformers import StoppingCriteria

    class Balanced(StoppingCriteria):
        def __call__(self, input_ids, scores, **kwargs) -> bool:
            new = input_ids[0].tolist()[width:]
            if len(new) % STOP_EVERY:
                return False
            text = processor.tokenizer.decode(new, skip_special_tokens=False)
            return stops_here(text, prompts, reader_v5)

    return Balanced()


def load_reader(pack: dict, repo: Path):  # pragma: no cover — needs the GPU and 59 GB of weights
    """The READER config, loaded the way `scripts/serve_handler.py` loads it, with v5's ceiling.

    A `render` override and a wrapped `model.generate` rather than two edits to `local_llm.py`:
    `ReaderClient.read` — the encode, the ONE `generate` call, the usage counters and
    `finish_reason` — is inherited untouched, so this run and every run before it go through the
    same inference path, and no sha three sealed registrations pin has to move for a keyword.
    """
    sys.path.insert(0, str(repo / "scripts"))
    import serve_handler

    from market_pulse import local_llm, prompts, reader_v5

    serving = pack["serving"]
    template = template_of(serving.get("serving_config", DEFAULT_SERVING), local_llm)
    ceiling = serving.get("output_tokens")
    if not ceiling:
        raise SystemExit(
            "the pack carries no `serving.output_tokens`, so the client would silently take"
            f" local_llm's default of {local_llm.READER_MAX_NEW_TOKENS}. A ceiling registered and"
            " never passed is a ceiling nobody lifted — stop and report."
        )
    processor, model = local_llm.load_captioner(
        serving["model"], revision=serving["model_revision"]
    )
    serve_handler.assert_no_adapter(model)

    class Client(local_llm.ReaderClient):
        def render(self, task, item):
            return processor.apply_chat_template(
                [{"role": "user", "content": render(prompts, item, task)}],
                tokenize=False,
                **self.chat_template,
            )

    client = Client(processor, model, max_new_tokens=int(ceiling), chat_template=template)
    generate = model.generate

    def stopping(**kwargs):
        width = kwargs["input_ids"].shape[1]
        return generate(
            **kwargs, stopping_criteria=[stop_at_balanced(processor, width, reader_v5, prompts)]
        )

    model.generate = stopping
    return client


def whole_lines(text: str, where: str) -> tuple[list[dict], str | None]:
    """Every WHOLE json row of an out-file, and the torn LAST line if it has one.

    The Mac's `read_threads_reader_v5.raw_rows` states the same rule and cannot be imported here:
    that one runs inside the repo on the Mac, this one runs on a rented pod with two files beside it
    and no `market_pulse` on the path until the checkout is verified. Two implementations of one rule
    is a drift risk, so their agreement on one fixture is a TEST
    (`test_the_pod_runner_and_the_mac_driver_DROP_THE_SAME_torn_line`) rather than a hope.

    Only the last line is forgiven: this file is scp'd back off a dying pod while the pod is still
    appending to it, so its final line can be half written. A torn line anywhere else is a damaged
    file, and resuming over it would silently re-ask a unit that HAS an answer.
    """
    lines = [line for line in text.splitlines() if line]
    rows, torn = [], None
    for index, line in enumerate(lines):
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            if index != len(lines) - 1:
                raise SystemExit(
                    f"{where}: line {index + 1} of {len(lines)} is not JSON, and it is not the last"
                    " one — that is a damaged file and not the mid-write race the final line is"
                    " forgiven for. Resuming over it would re-ask a unit that already has an answer."
                    " Move it aside and stop."
                ) from None
            torn = line
    return rows, torn


def already_answered(out: Path, ids: set[str]) -> set[str]:
    """The unit ids this out-file already carries — the whole mechanism of the recovery clause.

    The run contract allows a replacement pod «to answer ONLY the units with no persisted reply —
    answered units are NEVER re-asked», and one attempt means one answer per unit. Without this the
    loop would re-ask all 26 from the top and APPEND a second reply for units that already have one,
    which is worse than a re-ask: the Mac's projection counts rows, so the duplicates would loosen
    the cap gate on a live pod.

    A file carrying an id this pack never asked for belongs to a different run and is REFUSED here,
    before the model is loaded, rather than resumed against. `--out` is append-only by design and a
    stale file is the one way that design can hurt.

    A TORN last line is not an answer, so its unit is re-asked — and the fragment is dropped from the
    FILE and not only from this count: `--out` is opened in append mode, and a final line with no
    newline would have the next reply concatenated onto it. The drop is a byte-prefix of the file, so
    every reply that did land is left exactly as the pod wrote it.
    """
    if not out.exists():
        return set()
    text = out.read_text(encoding="utf-8")
    rows, torn = whole_lines(text, str(out))
    done = [row["id"] for row in rows]
    foreign = sorted(set(done) - ids)
    if foreign:
        raise SystemExit(
            f"{out} already carries {len(foreign)} unit id(s) this pack never asked for"
            f" ({foreign[:3]}) — it is another run's file, and appending to it would mix two"
            " populations. Move it aside and stop."
        )
    if torn is not None:
        out.write_text(text[: len(text) - len(torn)], encoding="utf-8")
        print(
            f"  (dropped a torn last line of {out}: {len(torn)} chars, no closing brace — the pod"
            " that wrote it died mid-write, and that unit counts as UNANSWERED)",
            flush=True,
        )
    return set(done)


def run(pack: dict, out: Path, repo: Path, loader=load_reader) -> int:
    started = time.monotonic()
    sys.path.insert(0, str(repo / "src"))
    from market_pulse import prompts, reader_v5

    instrument = check_instrument(pack, repo, prompts)
    items = check_requests(pack, prompts)
    say(started, f"instrument OK · parser {instrument['parser_sha256'][:16]}…")
    say(started, f"{len(items)} requests match the registration's per-item shas")
    say(
        started,
        f"serving {pack['serving'].get('serving_config', DEFAULT_SERVING)}"
        f" · ceiling {pack['serving'].get('output_tokens')} output tokens · stop at the brace",
    )

    order = {item["id"]: index for index, item in enumerate(items)}
    done = already_answered(out, set(order))
    todo = [item for item in items if item["id"] not in done]
    if done:
        say(started, f"{len(done)} of {len(items)} units are already answered and are NOT re-asked")
    if not todo:
        say(started, f"every unit in the pack is answered in {out} — nothing to generate")
        return 0
    say(started, f"loading {pack['serving']['model']} @ {pack['serving']['model_revision'][:12]}…")

    client = loader(pack, repo)
    boot = time.monotonic() - started
    say(started, f"READY · boot {boot:.1f}s · the kill clock stops at the first reply below")

    task = pack["task"]
    with out.open("a", encoding="utf-8") as handle:
        for item in todo:
            index = order[item["id"]]
            at = time.monotonic()
            reply = client.read(task, [item])[0]
            emitted = reply["content"]
            # the working-out is cut off the FRONT before the brace is looked for, and put back on
            # the persisted bytes: the thought is evidence (its length is a registered reading) and
            # it is not the answer. An unclosed channel — what a `length` cut-off looks like here —
            # has NO answer, so nothing is balanced and the whole emission is thought.
            thought, answer = thought_and_answer(emitted, prompts)
            prefix = None if answer is None else reader_v5.balanced_prefix(answer)
            row = {
                "index": index,
                "id": item["id"],
                "thread": item["thread"],
                "part": item.get("part"),
                "rendering_sha256": item["rendering_sha256"],
                # the PREFIX is what is persisted: the reply as the model emitted it, up to the
                # brace that closed its object. `cut_chars` is what the stop removed, so a reader
                # can always tell a stop from an answer that ended on its own
                "reply": emitted if prefix is None else thought + prefix,
                "balanced": prefix is not None,
                "emitted_chars": len(emitted),
                "cut_chars": 0 if prefix is None else len(answer) - len(prefix),  # answer is set
                "thought_chars": len(thought),
                "thought_tokens": reply.get("thought_tokens"),
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
                f"reply {index + 1:2d}/{len(items)} {item['id']:38s}"
                f" {row['seconds']:6.1f}s · {row['emitted_chars']:5d} chars"
                f" · thought {row['thought_tokens'] if row['thought_tokens'] is not None else '-'}"
                f" · cut {row['cut_chars']:4d} · balanced {row['balanced']}"
                f" · finish {row['finish_reason']}",
            )
    say(started, f"DONE · {len(todo)} generated here · {len(items)} replies in {out}")
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
