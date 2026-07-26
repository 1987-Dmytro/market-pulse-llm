"""Validation tests for the competitor registry loader."""

from pathlib import Path

import pytest
from market_pulse.registry import load_registry

REGISTRY = Path(__file__).resolve().parents[1] / "config" / "competitors.yaml"


def write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "competitors.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def test_shipped_registry_loads():
    competitors = load_registry(REGISTRY)
    assert competitors
    assert all(c.telegram_channels for c in competitors)
    assert len({c.id for c in competitors}) == len(competitors)


def test_duplicate_competitor_id_rejected(tmp_path):
    path = write(
        tmp_path,
        "competitors:\n"
        "  - id: a\n    name: A\n    telegram_channels: ['@chan_one']\n"
        "  - id: a\n    name: A again\n    telegram_channels: ['@chan_two']\n",
    )
    with pytest.raises(ValueError, match="duplicate competitor id"):
        load_registry(path)


def test_competitor_without_channels_rejected(tmp_path):
    path = write(tmp_path, "competitors:\n  - id: a\n    name: A\n    telegram_channels: []\n")
    with pytest.raises(ValueError, match="no telegram_channels"):
        load_registry(path)


def test_malformed_channel_handle_rejected(tmp_path):
    path = write(
        tmp_path,
        "competitors:\n  - id: a\n    name: A\n    telegram_channels: ['chan_without_at']\n",
    )
    with pytest.raises(ValueError, match="malformed handle"):
        load_registry(path)
