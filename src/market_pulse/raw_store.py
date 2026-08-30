"""Append-only raw store: one JSONL line per collected record (docs/SPEC.md §6).

Two record types, kept in separate files so a post and a comment can share a
message id without colliding: posts come from the channel, comments from its
linked discussion group, and the two id spaces are unrelated.

    data/raw/posts/<channel>.jsonl
    data/raw/comments/<channel>.jsonl

Raw sender ids are never written. A comment carries `sender_anon_id`, the HMAC of
the sender id under RAW_STORE_SALT, which is stable across runs and useless
without the salt.

Deduplication is on :func:`dedup_key` per (record_type, channel): the message id, unless the
record carries a finer ``row_id`` of its own. Everything in `data/raw/` is keyed on the message
id and stays keyed on it — the fallback IS the old behaviour.
"""

import hashlib
import hmac
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROOT = REPO_ROOT / "data" / "raw"

ARCHIVE_ROOT = DEFAULT_ROOT
"""Raw v1 — an ARCHIVE, read-only forever (SP-4 ruling (a), review 2026-08-30).

`results/raw_v1_baseline.sha256` pins six of its files and `data/` is gitignored, so an append
here is invisible to `git status` in both directions and cannot be undone. The baseline is the
only durable proof these files were never written, which is why the refusal lives in
:meth:`RawStore.append` — the one chokepoint every writer goes through — and not in a caller's
channel list ([[a_moved_guard_that_left_its_copy]])."""

LIVE_ROOT = REPO_ROOT / "data" / "raw_r2"
"""The ONE live root: S2's top-up for every collected channel, and later every tick (S12)."""


def live_store() -> "RawStore":
    """The corpus as the loop reads it: v1 ∪ r2, deduplicated on (channel, msg_id), r2 winning.

    Opt-in, never the default — `scripts/draw_promo_threads.py` draws over the FROZEN v1
    population and a union there would move 678/488 silently (plan §5.14).
    """
    return RawStore(LIVE_ROOT, archives=(ARCHIVE_ROOT,))


def load_salt(env_file: str | Path | None = None) -> str:
    """Read RAW_STORE_SALT, or explain how to create it once and never rotate it."""
    env_path = Path(env_file) if env_file else REPO_ROOT / ".env"
    load_dotenv(env_path)
    salt = os.getenv("RAW_STORE_SALT")
    if not salt:
        raise RuntimeError(
            f"{env_path}: RAW_STORE_SALT is missing. Create it once with\n"
            "  python3 -c \"import secrets; print('RAW_STORE_SALT=' + secrets.token_hex(32))\""
            f" >> {env_path}\n"
            "and never rotate it: a new salt orphans every sender_anon_id already stored."
        )
    return salt


def sender_anon_id(sender_id, salt: str) -> str | None:
    """Stable pseudonym for a sender. Anonymous posters have no id at all."""
    if sender_id is None:
        return None
    return hmac.new(salt.encode(), str(sender_id).encode(), hashlib.sha256).hexdigest()


def make_provenance(source, session: str) -> dict:
    """Where a record came from — carried on every record (SPEC §6, §9)."""
    return {
        "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "session": session,
        "source_type": source.source_type,
        "comments_enabled": source.comments_enabled,
    }


def post_record(message, source, channel: str, provenance: dict) -> dict:
    # raw_text, not text: the markdown the formatter adds is noise for the models.
    return {
        "record_type": "post",
        "source_id": source.id,
        "channel": channel,
        "msg_id": message.id,
        "date": message.date.isoformat(),
        "text": message.raw_text or "",
        "has_media": message.media is not None,
        "grouped_id": message.grouped_id,
        "reply_count": message.replies.replies if message.replies else 0,
        "provenance": provenance,
    }


def comment_record(message, source, channel: str, parent_msg_id: int, salt, provenance) -> dict:
    # reply_to_msg_id is stored raw and interpreted nowhere here. It lives in the
    # discussion group's id space, not the channel's, so it is not comparable to
    # parent_msg_id: a top-level comment replies to the group's mirror of the post,
    # a reply-to-a-commenter replies to another comment. Deciding which is which
    # needs the whole store, and a collector that guessed would bake the guess in.
    return {
        "record_type": "comment",
        "source_id": source.id,
        "channel": channel,
        "parent_msg_id": parent_msg_id,
        "msg_id": message.id,
        "reply_to_msg_id": message.reply_to_msg_id,
        "date": message.date.isoformat(),
        "text": message.raw_text or "",
        "sender_anon_id": sender_anon_id(message.sender_id, salt),
        "provenance": provenance,
    }


def collapse_albums(records: list[dict]) -> list[dict]:
    """One record per post: Telegram returns an album as several messages.

    The album keeps the id of its first item, the caption of whichever item
    carries one, and the highest reply counter — only one item holds each.
    """
    merged: list[dict] = []
    index: dict[int, int] = {}
    for record in records:
        group = record.get("grouped_id")
        if group is None:
            merged.append(record)
            continue
        seen = index.get(group)
        if seen is None:
            index[group] = len(merged)
            merged.append(dict(record))
            continue
        album = merged[seen]
        album["msg_id"] = min(album["msg_id"], record["msg_id"])
        album["text"] = album["text"] or record["text"]
        album["has_media"] = album["has_media"] or record["has_media"]
        album["reply_count"] = max(album["reply_count"], record["reply_count"])
    return merged


def dedup_key(record: dict):
    """What makes this record one row. ``row_id`` when it has one, its ``msg_id`` otherwise.

    A post and a comment ARE their message, so the message id is their identity and always was. A
    row whose identity is FINER than its message is new in 5c2: one leaflet page yields N positions
    and every one of them is a row the SPEC 3.18 (6) sitting reads field by field, so they all carry
    the page's ``msg_id`` — and under a msg_id-only key the second and every later position was
    dropped inside a single :meth:`RawStore.append`, silently, because :meth:`RawStore._by_file`
    marks each record seen as it iterates.

    The fallback is what keeps this free: no record ever written carries ``row_id``, so for every
    post and every comment in `data/raw/` the key is the msg_id it always was.
    """
    return record.get("row_id", record["msg_id"])


@dataclass
class StoreIndex:
    """What is already stored for one (record_type, channel) file."""

    ids: set[int] = field(default_factory=set)
    # `ids` is the MESSAGE id space and `keys` the ROW id space, and they are deliberately two
    # fields rather than one widened set: a queue subtracts the messages it has answered
    # (`loop.queued`), and answering a page with three positions on it means one message and three
    # rows. Collapsed into one set, `ids` would hold strings for a fanned-out type and the queue
    # would compare a msg_id against them forever without matching.
    keys: set = field(default_factory=set)
    parents: set[int] = field(default_factory=set)  # comments: posts already fetched
    with_replies: set[int] = field(default_factory=set)  # posts: threads worth fetching
    first_date: str | None = None
    last_date: str | None = None
    damaged_lines: int = 0

    @property
    def count(self) -> int:
        return len(self.ids)


class RawStore:
    """Append-only JSONL store, deduplicating on (channel, msg_id) per record type."""

    def __init__(self, root: str | Path = DEFAULT_ROOT, archives: tuple | list = ()):
        self.root = Path(root)
        self.archives = tuple(Path(one) for one in archives)
        """Read-only roots searched BEFORE `root`, oldest first. `root` is read last and wins."""
        self._index: dict[tuple[str, str], StoreIndex] = {}

    def path(self, record_type: str, channel: str) -> Path:
        """Where a record of this (type, channel) is WRITTEN — always under the live root."""
        return self.root / f"{record_type}s" / f"{channel.lstrip('@')}.jsonl"

    def paths(self, record_type: str, channel: str) -> list[Path]:
        """Every root this store READS, archives first and the live root last."""
        return [
            root / f"{record_type}s" / f"{channel.lstrip('@')}.jsonl"
            for root in (*self.archives, self.root)
        ]

    def index(self, record_type: str, channel: str) -> StoreIndex:
        key = (record_type, channel.lstrip("@"))
        if key not in self._index:
            index = StoreIndex()
            for path in self.paths(record_type, channel):
                self._read_into(index, path)
            self._index[key] = index
        return self._index[key]

    @staticmethod
    def _absorb(index: StoreIndex, record: dict) -> None:
        index.ids.add(record["msg_id"])
        index.keys.add(dedup_key(record))
        if record.get("parent_msg_id") is not None:
            index.parents.add(record["parent_msg_id"])
        if record.get("reply_count"):
            index.with_replies.add(record["msg_id"])
        date = record.get("date")
        if date:
            index.first_date = min(index.first_date or date, date)
            index.last_date = max(index.last_date or date, date)

    @classmethod
    def _read_index(cls, path: Path) -> StoreIndex:
        return cls._read_into(StoreIndex(), path)

    @classmethod
    def _read_into(cls, index: StoreIndex, path: Path) -> StoreIndex:
        """Absorb one file into an index that may already hold an older root's rows."""
        if not path.exists():
            return index
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                # A kill mid-write leaves a partial last line; refusing to read it
                # would turn "interrupt and rerun" into "interrupt and start over".
                index.damaged_lines += 1
                continue
            cls._absorb(index, record)
        return index

    def rows(self, record_type: str, channel: str) -> list[dict]:
        """Every stored record of one (type, channel), in the order it was appended.

        The index answers "which ids are here"; a caller that needs the record itself — the loop's
        inference leg needs a comment's text and its parent — was opening the JSONL by hand, and
        `data/raw/<type>s/<channel>.jsonl` is a layout that belongs to this class rather than to its
        callers. Damaged lines are skipped for the same reason :meth:`_read_index` counts them: a
        kill mid-write leaves a partial last line, and refusing the file would turn "interrupt and
        rerun" into "start over".
        """
        out: dict = {}
        for path in self.paths(record_type, channel):
            if not path.exists():
                continue
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                # Last root wins: the live root is read last, so an r2 row REPLACES the archive's
                # row of the same key in place, and a row only r2 has lands after the archive's.
                out[dedup_key(record)] = record
        return list(out.values())

    def append(self, records: list[dict]) -> int:
        """Write the records not already stored. Returns how many were new.

        Refuses outright when this store is rooted at :data:`ARCHIVE_ROOT`. The ruling is «v1 is
        read-only forever» and the append is irreversible, so the refusal is here rather than in
        each caller's channel list — a guard in the collector passes trivially the moment the
        collector is retargeted, and guards nothing.
        """
        if records and self.root.resolve() == ARCHIVE_ROOT.resolve():
            raise SystemExit(
                f"refusing to write into the raw v1 archive at {ARCHIVE_ROOT}: SP-4 ruling (a)"
                " (review 2026-08-30) makes it read-only forever, and"
                " `results/raw_v1_baseline.sha256` is the only durable proof of that —"
                f" `data/` is gitignored and the append cannot be undone.\nCollect into"
                f" {LIVE_ROOT} instead (`market_pulse.raw_store.live_store()` reads v1 \u222a r2)."
            )
        written = 0
        for path, batch in self._by_file(records).items():
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as handle:
                for record in batch:
                    handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                    written += 1
        return written

    def _by_file(self, records: list[dict]) -> dict[Path, list[dict]]:
        """Group the records that are new, marking them seen as we go."""
        batches: dict[Path, list[dict]] = {}
        for record in records:
            index = self.index(record["record_type"], record["channel"])
            if dedup_key(record) in index.keys:
                continue
            self._absorb(index, record)
            path = self.path(record["record_type"], record["channel"])
            batches.setdefault(path, []).append(record)
        return batches
