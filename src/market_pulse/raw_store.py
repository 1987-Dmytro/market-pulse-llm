"""Append-only raw store: one JSONL line per collected record (docs/SPEC.md §6).

Two record types, kept in separate files so a post and a comment can share a
message id without colliding: posts come from the channel, comments from its
linked discussion group, and the two id spaces are unrelated.

    data/raw/posts/<channel>.jsonl
    data/raw/comments/<channel>.jsonl

Raw sender ids are never written. A comment carries `sender_anon_id`, the HMAC of
the sender id under RAW_STORE_SALT, which is stable across runs and useless
without the salt.
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


@dataclass
class StoreIndex:
    """What is already stored for one (record_type, channel) file."""

    ids: set[int] = field(default_factory=set)
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

    def __init__(self, root: str | Path = DEFAULT_ROOT):
        self.root = Path(root)
        self._index: dict[Path, StoreIndex] = {}

    def path(self, record_type: str, channel: str) -> Path:
        return self.root / f"{record_type}s" / f"{channel.lstrip('@')}.jsonl"

    def index(self, record_type: str, channel: str) -> StoreIndex:
        path = self.path(record_type, channel)
        if path not in self._index:
            self._index[path] = self._read_index(path)
        return self._index[path]

    @staticmethod
    def _absorb(index: StoreIndex, record: dict) -> None:
        index.ids.add(record["msg_id"])
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
        index = StoreIndex()
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

    def append(self, records: list[dict]) -> int:
        """Write the records not already stored. Returns how many were new."""
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
            if record["msg_id"] in index.ids:
                continue
            self._absorb(index, record)
            path = self.path(record["record_type"], record["channel"])
            batches.setdefault(path, []).append(record)
        return batches
