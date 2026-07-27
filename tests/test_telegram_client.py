"""Offline tests for the Telethon client factory — no network, no login."""

import pytest
from market_pulse.telegram_client import REQUIRED, build_client


def clean_env(monkeypatch):
    for name in REQUIRED:
        monkeypatch.delenv(name, raising=False)


def test_missing_credentials_are_named(tmp_path, monkeypatch):
    clean_env(monkeypatch)
    env = tmp_path / ".env"
    env.write_text("TELEGRAM_API_ID=12345\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="TELEGRAM_API_HASH, TELEGRAM_SESSION"):
        build_client(env)


def test_non_numeric_api_id_rejected(tmp_path, monkeypatch):
    clean_env(monkeypatch)
    env = tmp_path / ".env"
    env.write_text(
        "TELEGRAM_API_ID=not-a-number\nTELEGRAM_API_HASH=deadbeef\nTELEGRAM_SESSION=s\n",
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="must be numeric"):
        build_client(env)
