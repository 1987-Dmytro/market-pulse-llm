"""Telethon client factory (docs/SPEC.md §2).

Credentials live in ``.env`` only — never in code, logs or committed files. The
session file is written next to the repo root and is gitignored: it authenticates
the collector account, so it is as sensitive as the API hash.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient

REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIRED = ("TELEGRAM_API_ID", "TELEGRAM_API_HASH", "TELEGRAM_SESSION")


def build_client(env_file: str | Path | None = None) -> TelegramClient:
    """Build a disconnected Telethon client from ``.env``.

    Raises ``RuntimeError`` naming every missing variable — a half-configured
    client would otherwise fail deep inside the first API call.
    """
    env_path = Path(env_file) if env_file else REPO_ROOT / ".env"
    load_dotenv(env_path)

    missing = [name for name in REQUIRED if not os.getenv(name)]
    if missing:
        raise RuntimeError(
            f"{env_path}: missing {', '.join(missing)}. "
            "Create the app at https://my.telegram.org (API development tools) and put "
            "TELEGRAM_API_ID / TELEGRAM_API_HASH / TELEGRAM_SESSION there."
        )

    api_id = os.environ["TELEGRAM_API_ID"]
    if not api_id.isdigit():
        raise RuntimeError(f"{env_path}: TELEGRAM_API_ID must be numeric, got {api_id!r}")

    # Relative session names resolve against the repo, so the login survives a run
    # from any working directory instead of creating a second session file.
    session = REPO_ROOT / os.environ["TELEGRAM_SESSION"]
    return TelegramClient(str(session), int(api_id), os.environ["TELEGRAM_API_HASH"])
