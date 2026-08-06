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


def test_a_swapped_env_names_the_variable_and_never_echoes_it(tmp_path, monkeypatch):
    """PROMPT-5a1 F3. The case this error exists for is an .env with the two values swapped.

    Then the non-numeric thing in TELEGRAM_API_ID *is* the API hash, and an error message goes
    to stderr, into logs, and into whatever a caller pastes into a bug report. The message may
    name the variable; it may not repeat what was in it.
    """
    clean_env(monkeypatch)
    secret = "0123456789abcdef0123456789abcdef"
    env = tmp_path / ".env"
    env.write_text(
        f"TELEGRAM_API_ID={secret}\nTELEGRAM_API_HASH=12345678\nTELEGRAM_SESSION=s\n",
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError) as raised:
        build_client(env)

    message = str(raised.value)
    assert "TELEGRAM_API_ID" in message, "the message still has to say which variable"
    assert secret not in message, "the value is the API hash in exactly the case that fires"
