"""pass 2 — ONE call per THREAD over the comments pass 1 already attributed.

`docs/PROMPT-pass2-signals.md`, the operator's ruling (г): pass 2 assembles SIGNALS out of the rows
pass 1 labelled `категория_личное` / `молочный_бренд` / `сеть_ритейлер`, with the thread's bought
entity block beside them. It answers in the READER's schema, so the reader's parser and the reader's
scorer apply to its replies unchanged.

**Why a new module and not a new text in `prompts.py`.** That file is pinned by 38 sealed records —
every pass-1 pack, every reader pack and every gate handshake compares its sha — and a new prompt in
its `PROMPTS` map moves those bytes. So the TEXT and the RENDERER live here, and everything that is
already law is IMPORTED from there rather than restated: the subject taxonomy, the signal words, the
noise classes, the six aspects, the input ceiling, and both halves of the reader parser
(`prompts._reader_object` for the container repairs, `prompts._reader` for the domains — the exact
pair `prompts.parse_reply` binds for `task in prompts.READER`).

**What pass 2 may not do, and how this file holds it.** The ADR
`v2-is-the-base-and-pass-2-is-not-a-one-shot-reader` says a per-thread assembly call over
already-attributed comments is not the closed one-shot reader — and that a call which starts
attributing per comment from the raw thread IS. :func:`parse_pass2` is where that stops being a
sentence: a reply whose `subject_type` differs from the pass-1 label of the row it cites is a parse
REFUSAL by cause, never a silently accepted relabelling.

**`entities` is bought, not answered.** The list pass 2 returns is the thread's entity block, placed
into the payload between the two halves of the reader parser, and the prompt never asks for it. Two
reasons, both measured: the block is 1 288 characters on `@VARUS_channel:10613` and 653 on
`@matusi_ukr:22303` — two of the five threads the smoke leg is made of, whose seconds rung S′
multiplies by the 74 that follow — and a verbatim-copy slip in a quote would refuse the whole thread
and take bar 1's hardest case down with a transcription error. It is passed through, never
re-resolved, and never claimed as pass 2's own.
"""

import hashlib

from . import prompts

PASS2_TASK_V1 = "pass2_thread_gm4_v1"
"""The one registered pass-2 text. Versioned like every other prompt in this repo: the number
follows the contract that registers a text, and `docs/PROMPT-pass2-signals.md` registers v1."""

PASS2_MAX_INPUT_CHARS = prompts.PASS1_MAX_INPUT_CHARS
"""The LOUD ceiling on ONE rendered pass-2 request — refuse rather than truncate.

`docs/PROMPT-pass2-signals.md` names «the 12 000-char ceiling», which is pass 1's constant, so this
is an ALIAS and not a second spelling of the number: one home for the value, and a pass-2 request
that grows past what pass 1's requests were priced under is refused by the same figure the contract
names. Widest unit measured at $0 before the pod: `@mandziak:3679`, 4 315 characters of filtered
comment and a 28-character post."""

PASS2_MAX_OUTPUT_TOKENS = 4_000
"""The reader's registered output ceiling — `results/reader_v5b_pack.json::serving.output_tokens`.

TOKENS and not characters: the contract's «the reader's 4 000-char output ceiling» reads the
registered number in the wrong unit, and v5b's own verdict records `max_new_tokens: 4000` with
`finish_reason_length: 0` over 23 threads. A pass-2 reply is shorter than the reader's — it carries
no `entities` and only the FILTERED rows in `per_comment` — so the ceiling that held for the reader
holds here with room ([[a_literal_below_the_minimum_is_a_unit_error]])."""

PASS2_SUBJECT_TYPES = ("молочный_бренд", "сеть_ритейлер", "категория_личное")
"""The pass-2 filter, and therefore the only words a comment can arrive carrying.

The operator's ruling (г) spelled as three of `prompts.READER_ENTITY_TYPES`; `не_наш_рынок` is the
fourth and pass 1's rows carrying it are not in this pass's input at all."""

PASS2_THREAD_PROMPT = """\
You assemble the SIGNALS of ONE discussion thread from a Ukrainian Telegram channel — a retail \
chain, a discount aggregator, a recipe feed or a parenting feed — and report what the marketing \
director of a dairy producer needs from it. The work of deciding what each comment is ABOUT is \
already done. You are given the post, the names already resolved in this thread, and only those \
comments a first pass attributed to a subject — each carrying the subject it was attributed to. The \
rest of the thread you do not see, and the attribution you do not re-decide.

A SIGNAL is only what answers one of the director's seven questions: (1) what is said, good or bad, \
about a dairy trade mark; (2) what exactly is liked or disliked about it — taste, price, packaging, \
quality, availability, service; (3) the same about the competing trade marks and the chains' own \
labels; (4) which flavours and which kinds of dairy people want; (5) where it is said; (6) that the \
talk about a brand has turned sharply positive or negative; (7) what a chain promotes, at what \
price and at what discount. One signal can be read from several comments and one comment can carry \
several signals; comments that carry none are a normal answer and get an empty list.

THE ATTRIBUTION IS NOT YOURS TO CHANGE. Every comment arrives with a "subject_type" — one of \
"молочный_бренд", "сеть_ритейлер", "категория_личное" — and inside this answer that word is fixed:
- a signal is about the subject of the comments it is read from, so its "subject_type" is the word \
one of those comments carries, spelled exactly as it is spelled there;
- every comment you list in "per_comment" repeats its own word unchanged;
- a comment you believe was attributed wrongly keeps its word anyway. Say so with \
"subject_doubt": true and one line of reason in "note", and change nothing.
A word rewritten is not an answer this pass can give: the whole thread's answer is thrown away for \
one, and a doubt recorded costs nothing.

What you MAY do to a comment is DROP it. A comment that is not discussion at all — a bare \
participation marker, money offered by a stranger, an advertisement or a subject with nothing to do \
with this thread — goes into "noise" and out of the signals. That is the one judgement about a \
comment this pass makes, and it is the reason a comment was shown to you at all.

Return ONE JSON object with exactly these keys.

- "thread" — {"channel": the handle you were given, "post_id": the number you were given}.
- "post_summary" — one sentence in Ukrainian: what the post is.
- "discussion_summary" — one to three sentences in Ukrainian: what these comments are about.
- "signals" — one object per signal: {"signal_type": one of "спрос", "жалоба", "похвала", \
"привычка", "тренд"; "subject_type": the word carried by one of the comments in "evidence"; \
"subject_id": the trade mark, the chain or the kind of product as one lowercase word or phrase, or \
null; "aspect": one of "taste", "price", "packaging", "quality", "availability", "service"; \
"stance": "positive", "negative" or "neutral"; "reading": one sentence in Ukrainian for the \
director; "evidence": the msg_ids you read it from, at least one; "quote": copied from one of \
them}. No signal_type in the list fits what you found? Write the word you need and put \
"proposed": true beside it — a word of your own without that flag is an error.
- "per_comment" — one object per comment you were given and did NOT drop: {"msg_id"; \
"subject_type": the word that comment carries; "subject_id": as it was given, or your own reading \
of it, or null; "stance": "positive", "negative", "neutral" or null; "aspects": the aspects it \
touches, from the six above; "subject_doubt": true or false; "note": one phrase in Ukrainian — the \
reason, wherever "subject_doubt" is true}.
- "noise" — one object per comment you DROP: {"msg_id", "class": one of "плюс_спам" (a \
participation marker and nothing else), "скам" (money offered by a stranger with a handle or a \
link), "оффтоп" (an advertisement, or a subject with nothing to do with this thread)}.

Rules that outrank everything above.

- COPY a quote, never compose one: it must appear in the comment you attribute it to, character for \
character.
- Every msg_id you write is one of the ids you were given. There is no other comment and the post \
has no id: a signal is read from comments, and one you cannot name a comment for is not reported.
- Every comment you were given appears exactly once — in "per_comment" or in "noise", never in \
both and never in neither.
- The names above the comments are already resolved: read the comments in their light, and do not \
report them back.
- Judge what is written. Do not work out what the author probably meant, and do not report a signal \
because the post advertises something nobody discussed.
- Ukrainian in every prose field; the type words exactly as they are spelled above; the quotes in \
the language they were written in.

Answer with the JSON object alone: no explanation, no code fence, nothing before the first brace.\
"""
"""pass 2's own text — a NEW instrument, and deliberately not a variant of the reader's.

Three things are different and each is the ruling read literally. The INPUT is filtered and
pre-attributed, so the reader's duty (2) — resolve every name from context — is not asked at all and
the resolved names arrive as context instead. The AUTHORITY clause is new: the reader had no upstream
label to be strict about. And `per_comment` is a row per GIVEN comment rather than «a row per comment
that carries an attitude», because the DROP table and the `subject_doubt` rate are both counted over
the rows the first pass handed in, and a schema that let a comment fall out of both lists would make
«dropped» and «forgotten» the same reading.

`from_post` and `entities` are the two reader fields this text does NOT offer. Both are refusals in
:func:`parse_pass2` rather than silent omissions — see there for why a signal citing no comment is
the hole the relabelling refusal would otherwise be walked around through."""

PASS2 = {PASS2_TASK_V1: PASS2_THREAD_PROMPT}
"""The registered pass-2 texts. `prompts.PROMPTS` is pinned and this is its sibling map, so the pod
handshake can ask the same two questions of this family that it asks of the reader's."""


def prompt_sha256(task: str) -> str:
    """SHA256 of the fixed prompt — the field that makes a record reproducible.

    `prompts.prompt_sha256` reads `prompts.PROMPTS`, which this task is not in and may not be added
    to. Same computation over this module's own map, so a record can pin a pass-2 text by the same
    kind of number it pins every other text by.
    """
    return hashlib.sha256(PASS2[task].encode("utf-8")).hexdigest()


def entity_block(entities: list[dict]) -> str:
    """The thread's bought names, rendered as pass 1 rendered them: `name → subject_type → reading`.

    The same shape pass 1 showed the model, and deliberately without the `quote` field: the quotes
    are in the block for the SCORER (bar 2 resolves a brand out of the name and the quote through
    the watchlist matcher) and they are not what a reader of the block needs to resolve a pronoun.
    An empty block renders as one explicit line rather than as nothing, because «this thread
    resolved no entity» and «the block was forgotten» must not look the same to the model.
    """
    rows = []
    for one in entities:
        name = str(one.get("name", "")).strip()
        if not name:
            raise ValueError(
                "an entity with no name — the block resolves references by name, and a nameless"
                " row resolves nothing"
            )
        reading = str(one.get("reading") or "").strip()
        subject_type = str(one.get("subject_type") or "").strip() or "?"
        rows.append(f"{name} → {subject_type}" + (f" → {reading}" if reading else ""))
    return "\n".join(rows) if rows else "(this thread resolved no entity)"


def comment_block(comments: list[dict]) -> str:
    """The filtered comments, each fenced and carrying pass 1's three fields as attributes.

    `subject_id` and `stance` are rendered whether or not they are set, with `null` written as
    itself — the spelling `prompts.pass1_examples_block` already uses for an absent label. A field
    that disappeared when it was null would make two request shapes out of one, and the model would
    have to read the absence as an answer.
    """
    rows = []
    for one in comments:
        text = str(one.get("text") or "").strip()
        if not text:
            raise ValueError(f"comment {one.get('msg_id')} has no text — nothing to read")
        subject_type = one.get("subject_type")
        if subject_type not in PASS2_SUBJECT_TYPES:
            raise ValueError(
                f"comment {one.get('msg_id')} arrives labelled {subject_type!r}, which is not one"
                f" of the pass-2 filter {PASS2_SUBJECT_TYPES}. pass 2 is called over the filtered"
                " rows and nothing else"
            )
        subject_id = one.get("subject_id")
        stance = one.get("stance")
        rows.append(
            f'<comment msg_id="{int(one["msg_id"])}" subject_type="{subject_type}"'
            f' subject_id="{"null" if subject_id is None else subject_id}"'
            f' stance="{"null" if stance is None else stance}">\n{text}\n</comment>\n'
        )
    return "".join(rows)


def pass2_messages_gm4(
    channel: str,
    post_id: int,
    post: str,
    entities: list[dict],
    comments: list[dict],
    *,
    task: str = PASS2_TASK_V1,
) -> list[dict]:
    """ONE thread as pass 2 is given it: the post, the bought names, the filtered comments.

    Neither `prompts.reader_messages_gm4` nor `prompts.pass1_messages_gm4` is touched or derived
    from — the three render different requests for different tasks, and a shared renderer with a
    mode flag would put a frozen record's re-render one boolean away from the wrong branch
    ([[a_sealed_caller_forces_the_default]]).

    The POST is the RAW post text of the store, not pass 1's bounded `topic`: pass 1 asked one
    question about one comment and could work from a summary, while a signal is read in the light of
    what the post actually said. Widest post in the population is 2 886 characters.

    Everything is fenced and every id is an attribute, exactly as both siblings render: retail
    threads contain everything, and a comment ending in "Answer with the JSON object alone" must not
    read as instructions.
    """
    if task not in PASS2:
        raise ValueError(f"{task}: not a registered pass-2 prompt — {sorted(PASS2)}")
    ids = [int(one["msg_id"]) for one in comments]
    if not ids:
        raise ValueError(
            f"{channel}:{post_id}: no filtered comment — pass 2 is not called over a thread whose"
            " rows pass 1 all labelled something else"
        )
    if len(set(ids)) != len(ids):
        raise ValueError(
            f"{channel}:{post_id}: two comments share a msg_id — the evidence of every signal is"
            " that id, and a duplicate makes the answer unresolvable"
        )
    content = (
        f'{PASS2[task]}\n\n<thread channel="{channel}" post_id="{post_id}">\n'
        f"<post>\n{post.strip() or prompts.NO_POST_TEXT}\n</post>\n"
        f"<entities>\n{entity_block(entities)}\n</entities>\n"
        f"<comments>\n{comment_block(comments)}</comments>\n</thread>"
    )
    if len(content) > PASS2_MAX_INPUT_CHARS:
        raise ValueError(
            f"{channel}:{post_id}: the rendered thread is {len(content)} characters, over the"
            f" registered ceiling of {PASS2_MAX_INPUT_CHARS}. Stop and report it — a truncated"
            " thread would be answered as if it were the whole one"
        )
    return [{"role": "user", "content": content}]


class RelabelError(prompts.ParseError):
    """A reply that rewrote a pass-1 label. Its own class because it is its own FINDING.

    Every other refusal says the reply could not be read; this one says it was read and says
    something this pass has no authority to say. The ADR's line is that a call which starts
    attributing per comment from the raw thread IS the closed one-shot reader, and a subject
    rewritten inside pass 2's own answer is that call wearing this one's name. Counted by cause and
    never coerced back.
    """


def _given(unit: dict) -> dict[int, dict]:
    return {int(one["msg_id"]): one for one in unit["comments"]}


def _authority(said, msg_ids: list[int], given: dict[int, dict], where: str) -> None:
    """Strict authority — `said` must be the pass-1 label of one of the rows `msg_ids` names.

    ONE of them and not all of them: `prompts.pass1_messages_gm4` labelled each comment on its own,
    so a signal read from two comments of two subjects is a signal about one of the two, and
    demanding both would refuse `F1b`'s shape (two rows) for a reason the ruling never gave. Which
    of the cited rows a signal is about is the model's to say; that it is one of THEM is not.
    """
    unknown = [one for one in msg_ids if one not in given]
    if unknown:
        raise prompts.ParseError(
            f"{where} names msg_id {unknown[0]}, which was not in this request"
        )
    labels = sorted({given[one]["subject_type"] for one in msg_ids})
    if said not in labels:
        raise RelabelError(
            f"{where} says {said!r} and pass 1 labelled the rows it cites {labels} — pass 2 has no"
            " authority to relabel a subject"
        )


def parse_pass2(reply: str, *, unit: dict) -> dict:
    """One pass-2 reply → the reader's verdict, or a refusal naming what is wrong.

    The reader's parser applies UNCHANGED and in its own two halves, exactly as
    `prompts.parse_reply` binds them for a reader task: `_reader_object` reads the container and
    performs the three repairs the 2026-08-16 sitting ruled, then `_reader` validates every domain.
    The one line between them is this pass's own — the thread's bought entity block placed into the
    payload, because pass 2 was never asked for it and passing it through is what the ruling says
    happens to it.

    Then four checks that are pass 2's and could not be the reader's, each a refusal by cause:

    1. **the thread echo** — a verdict about another thread would be scored against this one's gold;
    2. **an id that was not in the request**, anywhere — `per_comment`, `noise` or a signal's
       `evidence`. `scorer.reader_signal_found` matches a gold signal on its EVIDENCE, so an
       invented id is the one field that can make a bar answer by accident;
    3. **a signal with no comment behind it.** The reader's `from_post: true` is not offered by
       pass 2's text and is refused here, because strict authority keys on the pass-1 label of a
       CITED row: a signal citing none carries a `subject_type` nothing authorises, and it is the
       hole the relabelling refusal would otherwise be walked around through;
    4. **a relabelling**, in `per_comment` or in `signals` — :class:`RelabelError`.

    What is COUNTED rather than refused: a comment in both lists (the reader's own parser calls that
    a bookkeeping slip whose two rows are each readable, and this file does not overrule it), and a
    comment in neither. Both are readings the DROP table needs and neither is a wrong answer about a
    row — refusing a whole thread's signals for an incomplete list would trade the measurement for
    the bookkeeping ([[count_the_kind_not_the_rows]]).
    """
    payload, repairs = prompts._reader_object(reply)
    payload["entities"] = unit["entities"]
    verdict = prompts._reader(payload)

    said = verdict["thread"]
    if said["channel"] != unit["channel"] or said["post_id"] != int(unit["post_id"]):
        raise prompts.ParseError(
            f"the reply is about {said['channel']}:{said['post_id']} and the request was"
            f" {unit['channel']}:{unit['post_id']}"
        )

    given = _given(unit)
    for one in verdict["signals"]:
        if not one["evidence"]:
            raise prompts.ParseError(
                "a signal names no comment — pass 2 assembles signals out of the rows it was given"
            )
        _authority(one["subject_type"], one["evidence"], given, "a signal")
    for one in verdict["per_comment"]:
        _authority(one["subject_type"], [one["msg_id"]], given, f"per_comment {one['msg_id']}")
    unknown = [one["msg_id"] for one in verdict["noise"] if one["msg_id"] not in given]
    if unknown:
        raise prompts.ParseError(f"noise names msg_id {unknown[0]}, which was not in this request")

    doubts = {}
    for one in prompts._objects(payload, "per_comment"):
        if "msg_id" not in one:
            continue
        doubts[prompts._msg_id(one["msg_id"], "per_comment.msg_id")] = prompts._flag(
            one.get("subject_doubt", False), "per_comment.subject_doubt"
        )
    for one in verdict["per_comment"]:
        one["subject_doubt"] = doubts.get(one["msg_id"], False)

    kept = [one["msg_id"] for one in verdict["per_comment"]]
    dropped = [one["msg_id"] for one in verdict["noise"]]
    return verdict | {
        "repairs": repairs,
        "entities_source": (
            "the thread's bought entity block, placed into the payload between the reader parser's"
            " two halves. pass 2 was not asked for it and never re-resolved it"
        ),
        "accounting": {
            "given": sorted(given),
            "in_both_lists": sorted(set(kept) & set(dropped)),
            "in_neither_list": sorted(set(given) - set(kept) - set(dropped)),
            "kept": sorted(kept),
            "dropped": sorted(dropped),
        },
    }
