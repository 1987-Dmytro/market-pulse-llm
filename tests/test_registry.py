"""Validation tests for the source registry loader."""

from pathlib import Path

import pytest
from market_pulse.registry import load_registry

REGISTRY = Path(__file__).resolve().parents[1] / "config" / "registry.yaml"

SOURCES = (
    "sources:\n"
    "  - id: a\n    name: A\n    source_type: official_retail\n"
    "    telegram_channels: ['@chan_one']\n"
)
TAXONOMY = "taxonomy:\n  tracked_groups:\n    dairy:\n      name: Молочні продукти\n"


def write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "registry.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def test_shipped_registry_loads():
    registry = load_registry(REGISTRY)
    assert registry.sources
    assert all(s.telegram_channels for s in registry.sources)
    assert len({s.id for s in registry.sources}) == len(registry.sources)
    assert registry.taxonomy.tracked_groups
    assert any(b.own for b in registry.watchlist)


def test_duplicate_source_id_rejected(tmp_path):
    path = write(
        tmp_path,
        "sources:\n"
        "  - id: a\n    name: A\n    source_type: official_retail\n"
        "    telegram_channels: ['@chan_one']\n"
        "  - id: a\n    name: A again\n    source_type: aggregator\n"
        "    telegram_channels: ['@chan_two']\n" + TAXONOMY,
    )
    with pytest.raises(ValueError, match="duplicate source id"):
        load_registry(path)


def test_source_without_channels_rejected(tmp_path):
    path = write(
        tmp_path,
        "sources:\n  - id: a\n    name: A\n    source_type: official_retail\n"
        "    telegram_channels: []\n" + TAXONOMY,
    )
    with pytest.raises(ValueError, match="no telegram_channels"):
        load_registry(path)


def test_malformed_channel_handle_rejected(tmp_path):
    path = write(
        tmp_path,
        "sources:\n  - id: a\n    name: A\n    source_type: official_retail\n"
        "    telegram_channels: ['chan_without_at']\n" + TAXONOMY,
    )
    with pytest.raises(ValueError, match="malformed handle"):
        load_registry(path)
