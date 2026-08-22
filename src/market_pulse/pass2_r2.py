"""pass 2, r2 — the same request byte for byte, and a parser no report-only field can refuse.

`docs/PROMPT-pass2-signals-r2.md`, the operator's ruling (з). r1 bought five of the 79 threads and
lost one of them to `"note": ""` — a field the contract calls report-only, on a row the model did
not doubt, refusing a whole thread's signals through `prompts._reader`'s `_text`. That is Dv702, and
r2's answer to it is structural rather than another special case: **every field the record marks
report-only is read through a tolerant reader that records `unreadable` beside the value and never
raises**, and the reply's refusal set is closed and named.

**Why a second module and not an edit to `pass2.py`.** That file is pinned by
`results/pass2_pack.json::instruments.module.sha256`, and `results/prereg_pass2_signals.json` pins
the pack — a sealed record of a closed paid session. `tests/test_pass2_signals.py`'s
`test_the_pack_rebuilds_byte_for_byte_from_its_own_inputs` re-runs the builder and compares, so one
character in `pass2.py` turns `make check` red on r1's own artifacts. The contract states the rule
for the gate — «if r1's pinned bytes stay untouched, otherwise a sibling (say which)» — and the same
rule decides this file. The sibling is this one.

**The prompt does not move.** `PASS2_THREAD_PROMPT`, `entity_block`, `comment_block` and the request
assembly are r1's, imported and not restated, because r2 CARRIES FOUR REPLIES r1 paid for. A copied
reply is only an answer to r2's request if r2's request is r1's request, and the cheapest way to
hold that is to render with the same code and pin every unit's `rendering_sha256` against r1's pack
([[the_fixture_and_the_artifact_share_anchors]]).

What this module adds to r1's: a ceiling derived from a proven serving envelope instead of aliased
from pass 1's constant, and :func:`parse_pass2`.
"""

from __future__ import annotations

import json
from contextlib import contextmanager

from market_pulse import pass2, prompts

PASS2 = pass2.PASS2
PASS2_TASK_V1 = pass2.PASS2_TASK_V1
PASS2_SUBJECT_TYPES = pass2.PASS2_SUBJECT_TYPES
PASS2_MAX_OUTPUT_TOKENS = pass2.PASS2_MAX_OUTPUT_TOKENS
RelabelError = pass2.RelabelError
SUBJECT_SYNONYMS = pass2.SUBJECT_SYNONYMS
collapse = pass2.collapse
entity_block = pass2.entity_block
comment_block = pass2.comment_block
prompt_sha256 = pass2.prompt_sha256
"""r1's, by reference and not by copy. `prompt_sha256` in particular reads `pass2.PASS2`, so the
handshake a pod runs and the sha a record pins are the same computation over the same bytes."""


CEILING = {
    "proven_prompt_tokens": 4_510,
    "proven_by": (
        "results/reader_v5b_w1.jsonl :: @matusi_ukr:22272 — 15 673 rendered characters,"
        " usage.prompt_tokens 4 510, finish_reason `stop`, 1 896 completion tokens. The widest"
        " request the READER serving config has been PROVEN to serve on this stack"
    ),
    "serving_field": "results/reader_v5b_pack.json :: serving.output_tokens = 4000",
    "serving_rule": (
        "the serving config bounds the ANSWER and names no input bound at all. The proven point"
        " already carries that reservation — the reader ran under the same 4 000 — so a pass-2"
        " request of the same prompt length sits inside an envelope this stack has served"
    ),
    "chars_per_prompt_token": 3.4523,
    "density_measured_on": (
        "the five PAID pass-2 requests: 41 922 rendered characters over 11 907 prompt tokens."
        " Mean 3.5208; the per-request range is 3.4523 (@mandziak:3703) to 3.6894"
        " (@matusi_ukr:22303). The MINIMUM is used — fewest characters per token is most tokens"
        " per character, so it is the conservative direction"
    ),
    "the_model_context_is_not_on_this_stack": (
        "the contract asks for a ceiling derived from «the model's context». No record, pack,"
        " config or report in this repository carries a context length for"
        " google/gemma-4-31b-it — grepped for context_window / context_length /"
        " max_position / n_ctx and for the round numbers, nothing. A ceiling taken from"
        " outside would be a typed number wearing a derivation, so the anchor is the largest"
        " prompt this exact serving config has been observed to serve, which is a LOWER BOUND"
        " on that context and is the only reading with a record behind it"
    ),
}
"""Every input of :data:`PASS2_MAX_INPUT_CHARS`, so a reader can redo the arithmetic without this
file. `tests/test_pass2_signals_r2.py` re-derives both numbers from the artifacts they name."""

PASS2_MAX_INPUT_CHARS = int(CEILING["proven_prompt_tokens"] * CEILING["chars_per_prompt_token"])
"""**15 569 characters** — the LOUD ceiling on ONE rendered pass-2 request, derived and not typed.

`4 510 × 3.4523 = 15 569.9 → 15 569`, floored. r1 aliased `prompts.PASS1_MAX_INPUT_CHARS`, a number
sized for a pass-1 request whose prompt is ~2 300 characters; pass 2's prompt is 5 480 and the
widest unit renders to 11 856, leaving 144 characters — 1.2 % — of a ceiling that was never derived
for this request. This one is: it is the widest prompt the READER serving config has been proven to
serve, expressed in the unit the renderer refuses in, at the worst density pass 2 itself has
measured.

15 569 ≥ 11 856, so no unit is refused and the contract's «if the derived ceiling is below 11 856,
that is a STOP» does not fire. Headroom on the widest unit: 3 713 characters, 23.8 %."""


@contextmanager
def _ceiling(value: int):
    """r1's renderer, run against r2's ceiling — and put back after.

    `pass2.pass2_messages_gm4` reads its ceiling as a module global at call time, so the only way to
    grow that one parameter without touching the file a sealed record pins is to swap the constant
    for the length of the call ([[a_self_pinning_producer_cannot_grow_a_parameter]]). The RENDERING
    is unaffected: the ceiling is read once, after the string is built, and only to refuse it.
    """
    keep = pass2.PASS2_MAX_INPUT_CHARS
    pass2.PASS2_MAX_INPUT_CHARS = value
    try:
        yield
    finally:
        pass2.PASS2_MAX_INPUT_CHARS = keep


def pass2_messages_gm4(
    channel: str,
    post_id: int,
    post: str,
    entities: list[dict],
    comments: list[dict],
    *,
    task: str = PASS2_TASK_V1,
) -> list[dict]:
    """One pass-2 request — r1's bytes exactly, refused at r2's ceiling."""
    with _ceiling(PASS2_MAX_INPUT_CHARS):
        return pass2.pass2_messages_gm4(channel, post_id, post, entities, comments, task=task)


SCORED_FIELDS = {
    "thread.channel / thread.post_id": (
        "the reply is scored against ONE thread's gold and this is what says which"
    ),
    "signals[].evidence": (
        "`scorer.reader_signal_found` matches a gold signal on its EVIDENCE first, and strict"
        " authority keys on the pass-1 label of a CITED row"
    ),
    "signals[].subject_type": "compared by the scorer wherever the gold states it, and the ADR's line",
    "signals[].aspect": (
        "compared by the scorer wherever the gold states it — F1b is `availability` and F1c is"
        " `taste`, and those two are what the r1 review's paid-for clauses bought"
    ),
    "per_comment[].subject_type": "the ADR's line: rewriting a pass-1 subject is what pass 2 may not do",
    "per_comment[].msg_id / noise[].msg_id": (
        "identity. An id that was not in the request is the one field that can make a bar answer by"
        " accident, so it is a refusal and not a repair"
    ),
    "signals / per_comment / noise, as lists": (
        "bar 3 counts `len(signals)` and the DROP table partitions the other two, so a missing"
        " container is a non-answer and defaulting it to `[]` would read GREEN over nothing"
    ),
}
"""What a domain violation still costs the whole thread, and why each one is scored.

Read off the scorer rather than asserted: `scorer.reader_signal_found` compares evidence,
`subject_type` and `aspect` and says in its own docstring that `signal_type` and `subject_id` are
deliberately NOT compared; `scorer.reader_noise_count` counts signals; bar 2 is scored over the
`entities` block this pass injects and never asks for."""

REPORT_ONLY_FIELDS = {
    "post_summary": "nothing reads it; `_text` refuses an empty one and takes the thread with it",
    "discussion_summary": "the same",
    "signals[].signal_type": (
        "«signal_type is deliberately NOT compared» — `scorer.reader_signal_found`, in as many words"
    ),
    "signals[].subject_id": "not compared: the reference spells subjects in Russian prose",
    "signals[].stance": "not read by any bar",
    "signals[].reading": "prose for a human",
    "signals[].quote": "prose for a human; the bar matches on the evidence ids",
    "signals[].proposed / signals[].from_post": "flags; `_flag` refuses `0`, `null` and a Ukrainian yes",
    "per_comment[].subject_id / .stance / .aspects": (
        "`per_comment` is pass 1's pass-through and bar 4 is NOT registered — it would be the"
        " fourteen's sixth look through a threshold"
    ),
    "per_comment[].note": 'Dv702: `"note": ""` on a row the model did not doubt cost F2 its thread',
    "per_comment[].subject_doubt": "the ruling (ж) calls it report-only in as many words",
    "noise[].class": "the DROP table counts the ROW; the class is the reason printed beside it",
}
"""Every field that may no longer refuse a thread. Each is still READ, with the pinned validator
that owns it, and each unreadable one is recorded by name and by value in `unreadable_fields`."""

REFUSALS = (
    "a relabel — a `subject_type` that is not the pass-1 label of a row the reply cites",
    "an id that was not in the request, in `per_comment`, `noise` or a signal's `evidence`",
    "a signal citing no comment",
    "a reply about another thread",
    "an unbalanced or unreadable object — the pinned container reader's own refusals",
    "a domain violation on a SCORED field",
)
"""The closed set. A cause outside it is a defect in this module, not a finding about a reply."""

UNREADABLE = "(unreadable)"
"""What a NON-nullable report-only string becomes when its pinned validator refuses it.

**It SURVIVES into the verdict, and that is a correction the five-lens review paid for.** The first
version nulled every repaired field, and `prompts._reader` guarantees five of them are non-empty
STRINGS: `post_summary`, `discussion_summary`, `signals.signal_type`, `signals.reading`,
`signals.quote` and `noise.class`. Consumers group on two of those —
`score_pass2_signals.drop_table` does `sorted(Counter(noise.class).items())` and is a SEALED file,
and r2's own verdict producer does the same over `signals.signal_type` — so ONE unreadable field
anywhere in 79 threads raised `TypeError: '<' not supported between 'NoneType' and 'str'` **after
the whole run was paid for and rung 7 had said GO**. A tolerant reader that hands the next stage a
type its contract forbids has moved the refusal, not removed it
([[a_consumer_list_is_not_a_meaning_list]]).

«Unreadable» and «absent» stay two readings because the field is ALSO named in `unreadable_fields`
with the validator's own message and the raw value beside it. Nullable fields keep `None`: that is
what the pinned reader itself returns for an absent one, so no consumer can be surprised by it."""


def _refused(validator, *args) -> str | None:
    """The pinned validator's own refusal message, or None if it accepts. Never its value."""
    try:
        validator(*args)
    except prompts.ParseError as err:
        return f"{err}"
    return None


def _tolerate(payload: dict) -> tuple[dict, list[dict], list[tuple], list[dict]]:
    """Every report-only field checked with the validator that owns it, repaired where it refuses.

    The domains are NOT re-implemented here — `prompts._text`, `_choice`, `_flag` and `_msg_id` are
    called, and the only thing this function decides is what happens when one of them says no. A
    second spelling of a domain is the two-copies state one of the two files moves out of silently
    ([[a_moved_constant_fails_green]]).

    Returns the sanitised payload, the `unreadable_fields` rows, the `overwritten_fields` rows, the
    (container, index, key) triples whose value must read :data:`UNREADABLE` in the verdict, and the
    rows dropped for having no readable id.
    """
    unreadable: list[dict] = []
    overwritten: list[dict] = []
    nulled: list[tuple] = []
    dropped: list[dict] = []

    def _row(where: tuple, value, why: str) -> dict:
        container, index, key = where
        return {
            "where": f"{container}[{index}].{key}" if container else key,
            "field": f"{container}.{key}" if container else key,
            "value": json.dumps(value, ensure_ascii=False)[:120],
            "why": why,
        }

    def note(where: tuple, value, why: str) -> None:
        """A field the pinned validator REFUSED. This list is the Dv702 measurement and nothing
        else goes in it — a field the parser overwrote for its own reasons was READ fine, and
        filing it here would inflate the very census the contract was bought to take."""
        unreadable.append(_row(where, value, why))

    def overwrite(where: tuple, raw, why: str) -> None:
        """A field this parser CHANGED for its own reasons, with the model's own value beside it.

        Its own list, because it is its own kind: `unreadable_fields` answers «what could the
        reader not read» and this answers «what did the reader write». One list holding both would
        make the first question unanswerable ([[count_the_kind_not_the_rows]])."""
        overwritten.append(_row(where, raw, why))

    def text(row: dict, key: str, field: str, where: tuple, *, nullable: bool) -> None:
        value = row.get(key)
        if nullable and value is None:
            return
        why = _refused(prompts._text, value, field)
        if why is None:
            return
        note(where, value, why)
        row[key] = None if nullable else UNREADABLE
        if not nullable:
            nulled.append(where)

    def choice(row: dict, key: str, field: str, allowed, where: tuple, *, nullable: bool) -> None:
        value = row.get(key)
        if nullable and value is None:
            return
        why = _refused(prompts._choice, value, field, allowed)
        if why is None:
            return
        note(where, value, why)
        row[key] = None if nullable else allowed[0]
        if not nullable:
            nulled.append(where)

    def flag(row: dict, key: str, field: str, where: tuple) -> None:
        if key not in row:
            return
        why = _refused(prompts._flag, row[key], field)
        if why is None:
            return
        note(where, row[key], why)
        row[key] = False

    # the two top-level summaries: required by `_require`, read by nobody
    for key in ("post_summary", "discussion_summary"):
        text(payload, key, key, ("", 0, key), nullable=False)

    for index, row in enumerate(payload.get("signals") or []):
        if not isinstance(row, dict):
            continue
        # captured BEFORE `flag()` can repair it: the overwrite below promises to publish the
        # MODEL's own flag, and after the repair the value in the row is this parser's
        raw_proposed = row.get("proposed", None)
        flag(row, "proposed", "signals.proposed", ("signals", index, "proposed"))
        flag(row, "from_post", "signals.from_post", ("signals", index, "from_post"))
        where = ("signals", index, "signal_type")
        why = _refused(prompts._text, row.get("signal_type"), "signals.signal_type")
        if why is None and not prompts._flag(row.get("proposed", False), "signals.proposed"):
            said = prompts._text(row["signal_type"], "signals.signal_type").casefold()
            if said not in prompts.READER_SIGNAL_TYPES:
                why = "signal_type outside its domain and not flagged proposed"
        if why is not None:
            note(where, row.get("signal_type"), why)
            # `proposed` is OVERWRITTEN to carry the unreadable word past the pinned domain check,
            # and an overwrite nobody records is a value the model never gave being published as
            # its answer. Recorded ONLY when it actually changed, with the value the MODEL wrote —
            # `raw`, captured before `flag()` above could repair it — and in its own list, because
            # a field the reader WROTE is not a field the reader could not READ
            # ([[an_abstention_is_an_answer]])
            if raw_proposed is not True:
                overwrite(
                    ("signals", index, "proposed"),
                    raw_proposed,
                    "overwritten to True so the unreadable signal_type could pass the pinned"
                    " domain check. The model's own flag is the `value` beside this line",
                )
            row["signal_type"], row["proposed"] = UNREADABLE, True
            nulled.append(where)
        text(row, "reading", "signals.reading", ("signals", index, "reading"), nullable=False)
        text(row, "quote", "signals.quote", ("signals", index, "quote"), nullable=False)
        text(
            row, "subject_id", "signals.subject_id", ("signals", index, "subject_id"), nullable=True
        )
        choice(
            row,
            "stance",
            "signals.stance",
            prompts.SENTIMENT_LABELS,
            ("signals", index, "stance"),
            nullable=True,
        )

    kept: list[dict] = []
    # a container that is PRESENT and not a LIST is left exactly as it is, so `prompts._objects`
    # refuses it under closed-set cause 5 — rewriting it to `[]` would answer «this thread dropped
    # nothing» over a container nobody could read. A container that IS a list and whose rows are
    # individually unreadable is a DIFFERENT state and is not this guard's: those rows are dropped
    # one by one into `rows_without_a_readable_id`, which is a receipt a reader can count, and the
    # accounting's `in_neither_list` shows every comment they left unplaced
    # ([[a_structural_stop_accepts_a_structural_non_answer]], [[count_the_kind_not_the_rows]])
    for row in payload.get("per_comment") if isinstance(payload.get("per_comment"), list) else []:
        if (
            not isinstance(row, dict)
            or _refused(prompts._msg_id, row.get("msg_id"), "x") is not None
        ):
            dropped.append(
                {"list": "per_comment", "row": json.dumps(row, ensure_ascii=False)[:120]}
            )
            continue
        kept.append(row)
    if isinstance(payload.get("per_comment"), list):
        payload["per_comment"] = kept
    for index, row in enumerate(kept):
        # a MISSING `subject_type` is the same omission a `null` one is (Dv699) — it rewrote
        # nothing, and the authoritative label is in the pack either way. `_require` would refuse
        # the thread for it, so the key is supplied and the omission is counted downstream
        row.setdefault("subject_type", None)
        text(
            row,
            "subject_id",
            "per_comment.subject_id",
            ("per_comment", index, "subject_id"),
            nullable=True,
        )
        text(row, "note", "per_comment.note", ("per_comment", index, "note"), nullable=True)
        choice(
            row,
            "stance",
            "per_comment.stance",
            prompts.SENTIMENT_LABELS,
            ("per_comment", index, "stance"),
            nullable=True,
        )
        where = ("per_comment", index, "aspects")
        aspects = row.get("aspects") or []
        why = (
            "per_comment.aspects is not a list"
            if not isinstance(aspects, list)
            else next(
                (
                    one
                    for one in (
                        _refused(prompts._choice, aspect, "per_comment.aspects", prompts.INTENTS_V2)
                        for aspect in aspects
                    )
                    if one is not None
                ),
                None,
            )
        )
        if why is not None:
            note(where, row.get("aspects"), why)
            row["aspects"] = []

    kept = []
    for row in payload.get("noise") if isinstance(payload.get("noise"), list) else []:
        if (
            not isinstance(row, dict)
            or _refused(prompts._msg_id, row.get("msg_id"), "x") is not None
        ):
            dropped.append({"list": "noise", "row": json.dumps(row, ensure_ascii=False)[:120]})
            continue
        kept.append(row)
    if isinstance(payload.get("noise"), list):
        payload["noise"] = kept
    for index, row in enumerate(kept):
        choice(
            row,
            "class",
            "noise.class",
            prompts.READER_NOISE_CLASSES,
            ("noise", index, "class"),
            nullable=False,
        )

    return payload, unreadable, overwritten, nulled, dropped


def parse_pass2(reply: str, *, unit: dict) -> dict:
    """One pass-2 reply → the reader's verdict, or a refusal from the closed set :data:`REFUSALS`.

    Same three steps as r1's — `prompts._reader_object` for the container repairs, the thread's
    bought entity block placed into the payload, then `prompts._reader` for the domains — with
    :func:`_tolerate` between the second and the third. The pinned reader is neither edited nor
    re-implemented: it is handed a payload whose report-only fields have already been checked by its
    own validators, so the only rows it can still refuse are the ones a bar reads.

    The four refusals of r1's stand unchanged and are re-verified here: the thread echo, an id that
    was not in the request, a signal citing no comment, and a RELABELLING. A per-comment
    `subject_type` of `null` — or absent — is an OMISSION and counted, not a rewrite.
    """
    payload, repairs = prompts._reader_object(reply)
    payload["entities"] = unit["entities"]
    payload, unreadable, overwritten, nulled, dropped_rows = _tolerate(payload)
    verdict = prompts._reader(payload)
    for container, index, key in nulled:
        # :data:`UNREADABLE` and never `None` — see the constant. Two of these fields are grouped on
        # by a SEALED consumer, and a `None` in them crashes D2 after the run is paid for
        if container:
            verdict[container][index][key] = UNREADABLE
        else:
            verdict[key] = UNREADABLE

    said = verdict["thread"]
    if said["channel"] != unit["channel"] or said["post_id"] != int(unit["post_id"]):
        raise prompts.ParseError(
            f"the reply is about {said['channel']}:{said['post_id']} and the request was"
            f" {unit['channel']}:{unit['post_id']}"
        )

    given = pass2._given(unit)
    for one in verdict["signals"]:
        if not one["evidence"]:
            raise prompts.ParseError(
                "a signal names no comment — pass 2 assembles signals out of the rows it was given"
            )
        pass2._authority(one["subject_type"], one["evidence"], given, "a signal")
    omitted = []
    for one in verdict["per_comment"]:
        if one["msg_id"] not in given:
            raise prompts.ParseError(
                f"per_comment names msg_id {one['msg_id']}, which was not in this request"
            )
        if one["subject_type"] is None:
            omitted.append(one["msg_id"])
            continue
        pass2._authority(
            one["subject_type"], [one["msg_id"]], given, f"per_comment {one['msg_id']}"
        )
    unknown = [one["msg_id"] for one in verdict["noise"] if one["msg_id"] not in given]
    if unknown:
        raise prompts.ParseError(f"noise names msg_id {unknown[0]}, which was not in this request")

    doubts, doubt_unreadable = {}, []
    for one in prompts._objects(payload, "per_comment"):
        try:
            msg_id = prompts._msg_id(one["msg_id"], "per_comment.msg_id")
        except (KeyError, prompts.ParseError):
            continue
        try:
            doubts[msg_id] = prompts._flag(one.get("subject_doubt", False), "subject_doubt")
        except prompts.ParseError as err:
            doubts[msg_id] = None
            doubt_unreadable.append(msg_id)
            unreadable.append(
                {
                    "where": f"per_comment[{msg_id}].subject_doubt",
                    "field": "per_comment.subject_doubt",
                    "value": json.dumps(one.get("subject_doubt"), ensure_ascii=False)[:120],
                    "why": f"{err}",
                }
            )
    for one in verdict["per_comment"]:
        one["subject_doubt"] = doubts.get(one["msg_id"], False)

    synonyms = sorted(
        {
            one["subject_type"]
            for one in (*verdict["signals"], *verdict["per_comment"])
            if one["subject_type"] in SUBJECT_SYNONYMS.values()
        }
    )
    kept = [one["msg_id"] for one in verdict["per_comment"]]
    dropped = [one["msg_id"] for one in verdict["noise"]]
    return verdict | {
        "repairs": repairs,
        "entities_source": (
            "the thread's bought entity block, placed into the payload between the reader parser's"
            " two halves. pass 2 was not asked for it and never re-resolved it"
        ),
        "unreadable_fields": unreadable,
        "unreadable_field_names": sorted({one["field"] for one in unreadable}),
        "overwritten_fields": overwritten,
        "overwritten_field_names": sorted({one["field"] for one in overwritten}),
        "rows_without_a_readable_id": dropped_rows,
        "subject_doubt_unreadable": sorted(doubt_unreadable),
        "per_comment_subject_omitted": sorted(omitted),
        "vocabulary_synonyms_used": synonyms,
        "accounting": {
            "given": sorted(given),
            "in_both_lists": sorted(set(kept) & set(dropped)),
            "in_neither_list": sorted(set(given) - set(kept) - set(dropped)),
            "kept": sorted(kept),
            "dropped": sorted(dropped),
        },
    }
