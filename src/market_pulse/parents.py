"""The post a comment replies to — the context `docs/annotation/comments.md` always allowed.

The guideline's §Unit has told the annotator since Phase 2 to judge the comment on its
own text "plus the parent post only when the comment is meaningless without it", and it
names the plumbing in the next paragraph: the parent is the row with ``msg_id ==
parent_msg_id`` in ``data/raw/posts/<channel>.jsonl``, same channel, and *"Every parent is
there, because comments were collected from the threads of stored posts."*

That last sentence is a claim about the corpus, so this module checks it instead of
trusting it: a comment whose parent is not in the store raises. Rendering the prompt
without the post it promises would produce a row that looks labelled and was judged under
a different instrument than its neighbours — a skip that nothing downstream could see.

An empty parent *text* is a different thing entirely and is not an error: a media-only
post exists, and what it says lives in an image nobody here can read. It comes back as
``""`` and :func:`prompts.build_messages` renders it as such.
"""

import json
from collections.abc import Iterable
from pathlib import Path


def index(records: Iterable[dict]) -> dict[tuple[str, int], str]:
    """``(channel, msg_id) -> text`` over stored posts. Pure: the caller owns the files."""
    return {(record["channel"], record["msg_id"]): record["text"] for record in records}


def load(directory: Path) -> dict[tuple[str, int], str]:
    """The index over every ``*.jsonl`` in a raw-posts directory."""
    records = []
    for path in sorted(directory.glob("*.jsonl")):
        records += [
            json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line
        ]
    if not records:
        raise ValueError(f"{directory}: no stored posts, so no comment has a parent to read")
    return index(records)


STATE_OF = {"image": "image_caption", "poll": "poll_text"}
"""Which surrogate a row was asked with, in the words the records count."""


def load_captions(path: Path) -> dict[tuple[str, int], dict]:
    """``(channel, msg_id) -> {text, kind}`` over a 4.5g2 caption file. No file, no captions."""
    if not path.exists():
        return {}
    found = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        key = (record["channel"], record["msg_id"])
        if key in found:
            raise ValueError(f"{path}: {key[0]}:{key[1]} is captioned twice, so neither is the one")
        if record["kind"] not in STATE_OF:
            raise ValueError(f"{path}: {key[0]}:{key[1]} has kind {record['kind']!r}")
        found[key] = {"text": record["caption"], "kind": record["kind"]}
    return found


def context(posts: dict, captions: dict, row: dict) -> dict:
    """What reaches the model in the post's place, and which of the four states that is.

    One home for the rule "the post's text if there is any, else what stands in for it": every
    caller that renders a with-post prompt goes through here, so no run can end up asking half
    its rows with a description and half without because two call sites disagreed. The ``state``
    is returned rather than derived by the caller for the same reason — it is what the record
    counts, and a count nobody can compute is a claim nobody can check.
    """
    text = text_for(posts, row)
    if text.strip():
        return {"parent": text, "caption": None, "caption_kind": None, "state": "post_text"}
    caption = captions.get((row["channel"], row["parent_msg_id"]))
    return {
        "parent": text,
        "caption": caption and caption["text"],
        "caption_kind": caption and caption["kind"],
        "state": STATE_OF[caption["kind"]] if caption else "no_text_and_no_caption",
    }


def text_for(posts: dict[tuple[str, int], str], row: dict) -> str:
    """The parent post's text for one comment row, or a refusal naming the row.

    A missing parent is a STOP and never a skip: the alternative is a row silently asked
    with a different prompt than the 1,911 beside it.
    """
    key = (row["channel"], row["parent_msg_id"])
    if key not in posts:
        raise ValueError(
            f"{row['id']}: its parent {key[0]}:{key[1]} is not in the stored posts. Every"
            " comment was collected from a stored post's thread (docs/annotation/comments.md"
            " §Unit), so this is a gap in the store and not a row to ask without its post."
        )
    return posts[key]
