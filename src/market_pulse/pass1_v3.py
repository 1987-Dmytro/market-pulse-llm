"""pass 1, v3 — v2's bytes plus a `rationale` written BEFORE the label, and a parser it cannot refuse.

`docs/PROMPT-lora-c-prep.md`, the operator's rulings (в) and (к) of 2026-08-22. Line B supervised
`subject_type` alone on a set that is 52 % `не_наш_рынок` and the adapter learned the marginal
([[an_identical_count_is_not_an_identical_model]]). v3's answer is to put a sentence of reasoning
in front of the label, so the token the loss lands on first is *what the comment is about* and not
*which class is commonest*.

**Why a second module and not an edit to `prompts.py`.** That file is pinned by 38 records, several
of them sealed accounts of paid sessions, and `prompts.pass1_messages_gm4` raises
`ValueError(f"{task}: not a registered pass-1 prompt")` for every task outside
:data:`prompts.PASS1`. So `build_pass1_fewshot_packs.rendered_item` — which is otherwise exactly
the renderer this line wants, neighbours and all — **cannot take v3**: it dispatches on a task name
`prompts.py` does not know and may not be taught. The sibling is this module, and the pieces are
CALLED rather than restated: the v2 text, the examples-block validator, the media-less-post string
and the input ceiling all come from `prompts` by reference ([[a-pinned-file-is-not-edited-to-grow-a-parameter]]).

**The rationale is REPORT-ONLY and can never refuse a reply.** That is pass2-r2's rule
([[a_report_only_field_can_refuse_the_whole_row]]) applied before the first paid call rather than
after it: `prompts._text` would refuse `"rationale": ""`, and a field the record calls report-only
must not be able to cost a row its label. :func:`parse_pass1_v3` delegates the four SCORED fields
to `prompts.parse_pass1` unchanged and reads the fifth beside them.
"""

from __future__ import annotations

import hashlib

from market_pulse import prompts

PASS1_TASK_V3 = "pass1_comment_gm4_v3"
"""The registered name of this text. Not in :data:`prompts.PROMPTS` and not addable to it."""

PASS1_RATIONALE_CLAUSE_V3 = (
    "Before the label, write ONE sentence saying what the comment is ABOUT as against what it"
    " merely MENTIONS, and name the cue in the comment that decides it. Ukrainian, one sentence, at"
    " most 160 characters, in one of two shapes: «коментар ПРО X (cue: …)» where the comment is"
    " about the thing it names, or «лише ЗГАДУЄ X; насправді про Y (cue: …)» where a name appears"
    " but the comment is about something else. The cue is a word or phrase you can point to in the"
    " comment itself — not a restatement of the label. Write it FIRST, in the field `rationale`,"
    " and let it decide `subject_type`; a sentence written to agree with a label already chosen"
    " teaches nothing."
)
"""The ONE clause v3 adds to v2, in the prompt's own register.

The two shapes are the error the line targets, stated as a template the answer must fill: the
mention-vs-about cell is 18 of the 52 `не_наш_рынок` rows on holdout-100, and every one of the four
classes `docs/reports/pass2-signals-r2.md` names is a name read as a subject. «not a restatement of
the label» is the defence against the failure this whole line exists to avoid — a rationale
derivable from its label is the label wearing a sentence, and a target that is still a deterministic
function of the label teaches the marginal exactly as line B's did."""

PASS1_COMMENT_PROMPT_V3 = prompts.PASS1_COMMENT_PROMPT_V2 + "\n\n" + PASS1_RATIONALE_CLAUSE_V3
"""v2's bytes, then the rationale clause — a strict PREFIX extension, as v2 is of v1.

`tests/test_lora_c_prep.py` asserts `startswith` in both directions, so the base-v2 and base-v3
columns of the paired table differ by exactly one paragraph and by nothing else. The attribution law
reaches v3 by the same reference it reaches v1 and v2 by, so the label, the base answer and the v3
answer are still decided by ONE law ([[the_prompt_must_carry_the_annotators_law]])."""

PASS1_V3 = frozenset({PASS1_TASK_V3})
PROMPTS_V3 = {PASS1_TASK_V3: PASS1_COMMENT_PROMPT_V3}

PASS1_EXAMPLES_HEADER_V3 = "Labelled examples (rationale, then subject_type):"
"""v2's header names the one field its examples carry. v3's carry two, and a header that still said
«subject_type only» would be false about the block under it."""

RATIONALE_MAX_CHARS = 160
"""The contract's own bound on one rationale. A LOUD ceiling for the producer, never a parser rule:
:func:`parse_pass1_v3` measures an over-long rationale and reports it, because a model that writes
170 characters has answered the question and a refusal there would be the report-only field
refusing the row again."""


def prompt_sha256(task: str) -> str:
    """SHA256 of the fixed prompt — the field that makes a record reproducible.

    `prompts.prompt_sha256` reads `prompts.PROMPTS`, which this task is not in and may not be added
    to. Same computation over this module's own map, so a record can pin v3's text by the same kind
    of number it pins v1's and v2's by.
    """
    return hashlib.sha256(PROMPTS_V3[task].encode("utf-8")).hexdigest()


def pass1_examples_block_v3(examples: list[dict]) -> str:
    """The five labelled neighbours with THEIR rationales — `"<text>" → <rationale> → <label>`.

    The order inside a row is the order the answer is asked for: reasoning, then label. A block that
    showed the label first would demonstrate the opposite of what the clause requires, and the model
    reads the block as the shape of its own reply.

    Every example's label is validated by `prompts.pass1_examples_block` — CALLED on the same rows
    with their rationales stripped — so an example can never carry a reading the parser would refuse
    in an answer, and the v2 and v3 blocks cannot disagree about what a legal label is.
    """
    prompts.pass1_examples_block([{k: one[k] for k in ("text", "label")} for one in examples])
    rows = [PASS1_EXAMPLES_HEADER_V3]
    for one in examples:
        rationale = str(one.get("rationale", "")).strip()
        if not rationale:
            raise ValueError(
                "a v3 labelled example with no rationale — the block exists to show the shape of"
                " the answer, and a row missing the first field shows the wrong shape"
            )
        text = str(one["text"]).strip()
        label = "null" if one["label"] is None else one["label"]
        rows.append(f'"{text}" → {rationale} → {label}')
    return "\n".join(rows)


def pass1_messages_gm4_v3(
    channel: str,
    post_id: int,
    topic: str,
    entities: list[dict],
    msg_id: int,
    text: str,
    *,
    examples: list[dict],
) -> list[dict]:
    """ONE comment as v3 asks it — v2's request with the rationale clause and richer examples.

    A near-copy of `prompts.pass1_messages_gm4` on purpose: that function refuses this task by name
    and is pinned, so the assembly is restated HERE rather than reached by a mode flag threaded
    through a sealed caller ([[a_sealed_caller_forces_the_default]]). The pieces that can be shared
    are shared — :data:`prompts.NO_POST_TEXT`, the examples validator, the ceiling — and
    `tests/test_lora_c_prep.py` renders one item under v2 and under v3 and asserts the two strings
    differ in exactly the prompt paragraph and the examples block.

    `examples` is not optional. v3 has no no-examples arm: base v3 is v2's five neighbours plus one
    clause, and a v3 request with no block would be a third instrument nobody registered.
    """
    if not examples:
        raise ValueError(
            f"{PASS1_TASK_V3} carries a labelled-examples block and this request has none. An empty"
            " block is the block forgotten, not a thread that resolved nothing — stop."
        )
    if not text.strip():
        raise ValueError(f"{channel}:{post_id}:{msg_id}: the comment has no text — nothing to read")
    rows = []
    for one in entities:
        name = str(one.get("name", "")).strip()
        if not name:
            raise ValueError(
                f"{channel}:{post_id}: an entity with no name — the block resolves references by"
                " name, and a nameless row resolves nothing"
            )
        reading = str(one.get("reading") or "").strip()
        subject_type = str(one.get("subject_type") or "").strip() or "?"
        rows.append(f"{name} → {subject_type}" + (f" → {reading}" if reading else ""))
    block = "\n".join(rows) if rows else "(this thread resolved no entity)"
    content = (
        f'{PASS1_COMMENT_PROMPT_V3}\n\n<thread channel="{channel}" post_id="{post_id}">\n'
        f"<topic>\n{topic.strip() or prompts.NO_POST_TEXT}\n</topic>\n"
        f"<entities>\n{block}\n</entities>\n"
        f"<examples>\n{pass1_examples_block_v3(examples)}\n</examples>\n"
        f'<comment msg_id="{msg_id}">\n{text.strip()}\n</comment>\n</thread>'
    )
    if len(content) > prompts.PASS1_MAX_INPUT_CHARS:
        raise ValueError(
            f"{channel}:{post_id}:{msg_id}: the rendered request is {len(content)} characters, over"
            f" the registered ceiling of {prompts.PASS1_MAX_INPUT_CHARS}. Stop and report it — a"
            " truncated request would be answered as if it were the whole one"
        )
    return [{"role": "user", "content": content}]


def parse_pass1_v3(reply: str, *, msg_id: int) -> dict:
    """v1's four fields by `prompts.parse_pass1`, plus `rationale` as a field that cannot refuse.

    **The four scored fields are not re-implemented and not relaxed.** `prompts.parse_pass1` is
    CALLED on the same reply: `_require` is a subset check — it collects only what is *missing* —
    so a payload carrying a fifth key passes it unchanged, and the strictness this line's bar rests
    on is the strictness the window was measured under.

    The fifth key is then read off the raw payload with no validator between: absent, empty, a
    number, 300 characters long — every one of those is an answer this function returns and a census
    row the scorer counts, never a refusal. `rationale_state` says which
    ([[an_empty_field_hides_several_states]]), because «the model omitted it», «the model wrote an
    empty string» and «the model wrote a paragraph» are three different findings about a prompt and
    one of them would otherwise be invisible.
    """
    row = prompts.parse_pass1(reply, msg_id=msg_id)
    payload = prompts._object(reply)
    raw = payload.get("rationale")
    if "rationale" not in payload:
        state, rationale = "omitted", None
    elif not isinstance(raw, str):
        state, rationale = "not_a_string", None
    elif not raw.strip():
        state, rationale = "empty", None
    elif len(raw.strip()) > RATIONALE_MAX_CHARS:
        state, rationale = "over_length", raw.strip()
    else:
        state, rationale = "read", raw.strip()
    return {**row, "rationale": rationale, "rationale_state": state}
