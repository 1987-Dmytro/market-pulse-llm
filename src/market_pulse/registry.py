"""Competitor registry: competitor -> Telegram channels (docs/SPEC.md §5).

Validation is strict on purpose. A typo in a handle silently collects nothing,
and a duplicate competitor id silently merges two competitors' data into one
rollup — both are failures that only surface as wrong analytics much later.
"""

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

# Telegram public username: 5-32 chars, starts with a letter, letters/digits/underscore.
_HANDLE = re.compile(r"^@[A-Za-z][A-Za-z0-9_]{4,31}$")


@dataclass(frozen=True)
class Competitor:
    id: str
    name: str
    telegram_channels: tuple[str, ...]


def load_registry(path: str | Path) -> list[Competitor]:
    """Load and validate the registry, or raise ``ValueError`` naming the defect."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    entries = data.get("competitors")
    if not entries:
        raise ValueError(f"{path}: no competitors defined")

    # ponytail: the 2-3 competitor MVP cap is an operator decision, not a loader
    # rule — enforce it here only if Phase 2 shows the registry drifting.
    competitors: list[Competitor] = []
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError(f"{path}: each competitor must be a mapping, got {entry!r}")
        cid, name = entry.get("id"), entry.get("name")
        if not cid or not name:
            raise ValueError(f"{path}: competitor needs both 'id' and 'name': {entry!r}")
        if cid in seen:
            raise ValueError(f"{path}: duplicate competitor id {cid!r}")
        seen.add(cid)
        channels = entry.get("telegram_channels") or []
        if not channels:
            raise ValueError(f"{path}: competitor {cid!r} has no telegram_channels")
        for channel in channels:
            if not isinstance(channel, str) or not _HANDLE.match(channel):
                raise ValueError(f"{path}: competitor {cid!r} has a malformed handle {channel!r}")
        competitors.append(Competitor(cid, name, tuple(channels)))
    return competitors


if __name__ == "__main__":
    import sys

    for competitor in load_registry(sys.argv[1]):
        print(f"{competitor.id}\t{competitor.name}\t{' '.join(competitor.telegram_channels)}")
