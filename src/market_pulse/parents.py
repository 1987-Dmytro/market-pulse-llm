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
