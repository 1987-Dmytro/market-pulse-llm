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

CAPTION_SOURCES = ("qwen-4.5g2", "gm4-nf4-base")
"""The caption instruments, per SPEC amendment 3.13 (3). Two, and never a free string.

The amendment's rule is that "numbers with different caption sources are never compared without
saying so". That is only enforceable if the source is a closed vocabulary a reader can group by —
a record naming its model in prose can be read but cannot be *checked*."""

LEGACY_SOURCE = "qwen-4.5g2"
"""What a caption row with no ``caption_source`` field is.

Every caption on disk before 3.13 came from the 4.5g2 API instrument, and the amendment says
those bought captions stand as history: the old files are not rewritten, so the field is missing
rather than wrong. Resolved here in one place, so no reader invents its own default."""


def caption_source(row: dict) -> str | None:
    """Which instrument wrote this caption row — ``None`` for a row no model wrote.

    A poll row is the ``None``: its text is Telegram's own question and options, transcribed,
    with no model involved (`caption_posts.record_for` writes `model: None` for it). It is not
    a third instrument and must not read as one, so the fallback keys on ``model`` and not on
    the mere absence of the field.
    """
    if "caption_source" in row:
        source = row["caption_source"]
        if source is not None and source not in CAPTION_SOURCES:
            raise ValueError(
                f"caption_source {source!r} is not one of {list(CAPTION_SOURCES)} — a caption"
                " instrument nobody registered cannot be compared with one that was"
            )
        return source
    return LEGACY_SOURCE if row.get("model") else None


def sources_named(record: dict) -> set[str]:
    """The caption instruments a run record says it wrote, or an empty set.

    Two record shapes exist and both are read: `results/captions_45g2.json` is a ``runs`` list
    that `relabel.append_record` grows, `results/captions_5c1.json` is one flat document. Empty
    for every record written before this field existed, which is correct — those runs wrote one
    instrument and there is nothing for them to disclose.
    """
    runs = record.get("runs")
    block = runs[-1] if isinstance(runs, list) and runs else record
    return set(block.get("caption_sources") or [])


def assert_one_source(path, rows: list[dict], named: set[str]) -> set[str]:
    """Refuse a caption file that mixes instruments unless its record names them.

    SPEC amendment 3.13 (3): a caption from the 4.5g2 API and a caption from our own GM4 are
    two instruments, and a screen number computed over both is a number about neither. Mixing
    is legal — the 3.13 (4) bridge exists to do exactly that — but only *declared*: the run
    record has to name every source present, so the mixing is a sentence somebody wrote rather
    than a fact nobody noticed.
    """
    present = {source for source in map(caption_source, rows) if source}
    if len(present) > 1 and not present <= named:
        raise SystemExit(
            f"{path} mixes caption instruments {sorted(present)} and its record names"
            f" {sorted(named) or 'none of them'}. SPEC amendment 3.13 (3) forbids comparing"
            " numbers from different caption sources without saying so — either read one"
            " instrument's rows, or declare both in the record's caption_sources."
        )
    return present


def read_caption_rows(path: Path) -> list[dict]:
    """The rows of a caption file, as written. ``[]`` for a file that is not there."""
    if not path.exists():
        return []
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def load_captions(path: Path) -> dict[tuple[str, int], dict]:
    """``(channel, msg_id) -> {text, kind, source}`` over a caption file. No file, no captions."""
    found = {}
    for record in read_caption_rows(path):
        key = (record["channel"], record["msg_id"])
        if key in found:
            raise ValueError(f"{path}: {key[0]}:{key[1]} is captioned twice, so neither is the one")
        if record["kind"] not in STATE_OF:
            raise ValueError(f"{path}: {key[0]}:{key[1]} has kind {record['kind']!r}")
        found[key] = {
            "text": record["caption"],
            "kind": record["kind"],
            # Carried, never read by `context`: what reaches the model is the same string
            # either way. It is here so a caller that renders these captions can say in its
            # own record which instrument wrote them.
            "source": caption_source(record),
        }
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


def post_kwargs(found: dict) -> dict:
    """:func:`context`'s answer in the keywords :func:`prompts.build_messages` takes.

    The translation exists once. Four callers now render a with-post prompt — the
    labelling passes, the trainer and the gate eval — and a caller that assembled these
    three keys itself would be a second place that could disagree about which of the four
    states gets a caption.
    """
    return {
        "parent": found["parent"],
        "caption": found["caption"],
        "caption_kind": found["caption_kind"] or "image",
    }


def text_for(posts: dict[tuple[str, int], str], row: dict) -> str:
    """The parent post's text for one comment row, or a refusal naming the row.

    A missing parent is a STOP and never a skip: the alternative is a row silently asked
    with a different prompt than the 1,911 beside it.
    """
    key = (row["channel"], row["parent_msg_id"])
    if key not in posts:
        # `id` is the annotation batches' key and every caller before the 5c2 loop had one. A raw
        # `raw_store.comment_record` does not — it is keyed (channel, msg_id) — so naming the row by
        # `row["id"]` turned this deliberate STOP into a KeyError for the one caller that reads the
        # store directly, and the message that says what is wrong is the whole value of the stop.
        named = row.get("id") or f"{row['channel']}:{row['msg_id']}"
        raise ValueError(
            f"{named}: its parent {key[0]}:{key[1]} is not in the stored posts. Every"
            " comment was collected from a stored post's thread (docs/annotation/comments.md"
            " §Unit), so this is a gap in the store and not a row to ask without its post."
        )
    return posts[key]
