"""reader-v5's three additions to the reader: the transport stop, the echo census and the merge.

**Nothing here parses.** `prompts.parse_reply` is the parser and it is not touched: the sitting of
2026-08-17 rules on how generation STOPS and on how the pieces of a chunked thread are put back
together, not on how a reply is read. Every function below either runs before `parse_reply` (the
stop) or over what it returned (the census, the merge) — the Dv451 idiom, a generation later.

**Why the stop is in the transport and not in the prompt.** Two of reader-v4's four refusals were
`two disagreeing objects`, and both are the same shape: the model closes its object and keeps
writing. A prompt line asking it not to is already in v3 and v5 keeps it; what CANNOT be argued with
is a generation loop that stops at the closing brace. The prompt line and the parser's
refuse-on-conflict clause stay as defence — belt and braces, and the braces are here.

**Why the echo census counts three states and not two.** reader-v4 returned 93 `per_comment` rows
against 111 requested, which its own report reads as one row in six not written. It is not: the
other 18 are answered in `noise` (and 3 more ids are in BOTH lists), so over the parsed threads
`per_comment ∪ noise` covers 111 of 111 with nothing extra and nothing absent. A census over `per_comment` alone would score a reader for obeying
the prompt's own «a comment belongs to at most one of "per_comment" and "noise"»
([[count_the_kind_not_the_rows]]). Only `absent` is a shortfall.
"""

OPEN, CLOSE, QUOTE, ESCAPE = "{", "}", '"', "\\"

SIGNAL_KEY = ("signal_type", "subject_type", "subject_id", "aspect", "stance")
"""The dedupe key for a signal found in more than one chunk of one thread.

`evidence` and `quote` are deliberately NOT in it: the same finding read in two parts names
different msg_ids in each, and keying on evidence would keep both copies — which is the merge
failing to merge. `reading` is out for the same reason, one layer up: it is prose."""


def balanced_prefix(text: str) -> str | None:
    """The prefix of ``text`` that closes the FIRST top-level JSON object, or ``None``.

    Brace depth counted OUTSIDE string literals, because a reader's answer is full of Ukrainian
    prose and a quote containing ``{`` or ``}`` is ordinary. Escapes are handled the only way that
    is correct — a backslash inside a string consumes the next character whatever it is — so
    ``"a\\\\"`` ends the string and ``"a\\""`` does not.

    ``None`` means the text never balanced, which is the run-to-the-ceiling case and is left to the
    ceiling: inventing a closing brace here would be the transport writing the answer.
    """
    depth, inside, escaped, started = 0, False, False, False
    for index, char in enumerate(text):
        if escaped:
            escaped = False
            continue
        if char == ESCAPE and inside:
            escaped = True
            continue
        if char == QUOTE:
            inside = not inside
            continue
        if inside:
            continue
        if char == OPEN:
            depth, started = depth + 1, True
        elif char == CLOSE and started:
            depth -= 1
            if depth == 0:
                return text[: index + 1]
            if depth < 0:  # a closing brace before any opening one — not our shape
                return None
    return None


def echo(requested: list[int], verdict: dict) -> dict:
    """Which of the ids the request listed came back, and in WHICH list — three states, not two.

    Three defects and they are counted APART, because they have three causes and only one of them
    is about chunking:

    * `extra` — an id nobody sent;
    * `duplicated` — the same id twice in the SAME list, which is what a chunked request can break:
      two parts both answering for one comment. Leg B's mechanical bar m1 is about THIS one;
    * `in_both_lists` — one id in `per_comment` AND in `noise`, which is the prompt's «a comment
      belongs to at most one of the two» broken. The parser deliberately does not refuse it — two
      rows about one comment are each readable — and reader-v4 did it on three comments of
      `@VARUS_channel:10366`, with no chunking anywhere near it.

    Folding the third into the second would make m1 fail for a pre-existing prompt-obedience slip
    that has nothing to do with the mechanism m1 exists to prove
    ([[an_absolute_bar_needs_a_reachability_state]]).
    """
    wanted = list(requested)
    per_comment = [row["msg_id"] for row in verdict.get("per_comment") or ()]
    noise = [row["msg_id"] for row in verdict.get("noise") or ()]
    answered = per_comment + noise
    seen = set(wanted)
    counts: dict[int, int] = {}
    for row in (per_comment, noise):
        for msg_id in row:
            counts[msg_id] = max(counts.get(msg_id, 0), row.count(msg_id))
    return {
        "requested": len(wanted),
        "in_per_comment": [one for one in wanted if one in set(per_comment)],
        "in_noise": [one for one in wanted if one in set(noise) and one not in set(per_comment)],
        "absent": [one for one in wanted if one not in set(answered)],
        "extra": sorted({one for one in answered if one not in seen}),
        "duplicated": sorted(one for one, times in counts.items() if times > 1),
        "in_both_lists": sorted(set(per_comment) & set(noise)),
        "in_list_order": per_comment == [one for one in wanted if one in set(per_comment)],
        "covered": len([one for one in wanted if one in set(answered)]),
    }


class MergeError(ValueError):
    """Two chunks of one thread that cannot be put together. Its ``reason`` is what gets counted."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def merge(parts: list[dict]) -> dict:
    """The verdicts of one thread's chunks, back into one verdict.

    `per_comment` and `noise` are CONCATENATED, in chunk order, because the chunks partition the
    comment list — and «by construction» is verified rather than assumed: an id in two chunks'
    `per_comment` is a `MergeError`, not a row silently kept twice.

    `signals` and `entities` are DEDUPED, because a finding about the post's subject can legitimately
    be read in every chunk. A signal's key is :data:`SIGNAL_KEY` and the survivors' `evidence` lists
    are UNIONED, so the merged finding names every comment it was read from; an entity's key is
    (name, msg_id), which is already unique per mention.

    The three prose fields are the FIRST chunk's `thread` and `post_summary` — the post is the same
    post in every chunk, and a `thread` block that disagrees between chunks is a `MergeError` — and
    the chunks' own `discussion_summary` lines joined in order, because each one describes the
    comments its chunk carried and dropping the others would describe a third of the thread.
    """
    if not parts:
        raise MergeError("nothing to merge: no chunk of this thread produced a verdict")
    threads = [one["thread"] for one in parts]
    if any(one != threads[0] for one in threads):
        raise MergeError(f"the chunks name different threads: {threads}")

    per_comment: list[dict] = []
    seen_rows: dict[int, int] = {}
    for index, part in enumerate(parts):
        for row in part["per_comment"]:
            if row["msg_id"] in seen_rows:
                raise MergeError(
                    f"msg_id {row['msg_id']} is in the per_comment of chunk"
                    f" {seen_rows[row['msg_id']] + 1} and chunk {index + 1} — the chunks were sent"
                    " as a partition of the comment list and this answer is not one"
                )
            seen_rows[row["msg_id"]] = index
            per_comment.append(row)

    signals: dict[tuple, dict] = {}
    for part in parts:
        for one in part["signals"]:
            key = tuple(one.get(field) for field in SIGNAL_KEY)
            if key in signals:
                kept = signals[key]
                kept["evidence"] = sorted(set(kept["evidence"]) | set(one["evidence"]))
                kept["from_post"] = kept["from_post"] or one["from_post"]
            else:
                signals[key] = dict(one) | {"evidence": sorted(set(one["evidence"]))}

    entities: dict[tuple, dict] = {}
    for part in parts:
        for one in part["entities"]:
            entities.setdefault((one["name"], one["msg_id"]), one)

    return {
        "thread": threads[0],
        "post_summary": parts[0]["post_summary"],
        "discussion_summary": " ".join(one["discussion_summary"] for one in parts),
        "entities": list(entities.values()),
        "signals": list(signals.values()),
        "per_comment": per_comment,
        "noise": [row for part in parts for row in part["noise"]],
        "repairs": sorted({name for part in parts for name in part.get("repairs") or ()}),
        "merged_from": len(parts),
    }


def chunks(msg_ids: list[int], size: int) -> list[list[int]]:
    """The comment list cut into parts of at most ``size``, in order — the registered partition.

    A partition and never a sample: every id is in exactly one part and the order is the request's,
    which is what makes `merge`'s concatenation legal and what leg B's mechanical bar m1 checks.
    """
    if size < 1:
        raise ValueError(f"a chunk of {size} comments is not a chunk")
    return [msg_ids[at : at + size] for at in range(0, len(msg_ids), size)] or [[]]
