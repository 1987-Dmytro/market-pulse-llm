#!/usr/bin/env python3
"""One-time QR login for the collector account (docs/SPEC.md §2).

Scan the printed code with Telegram → Settings → Devices → Link Desktop Device.
It writes the session file every other script reuses, so this is the only place
that logs in interactively — and no phone number or code passes through a script.

    python3.11 scripts/tg_login.py
"""

import asyncio
import sys
from getpass import getpass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed

import qrcode
from telethon.errors import SessionPasswordNeededError
from telethon.utils import get_display_name

from market_pulse.telegram_client import build_client

# Telegram rotates the login token, so a stale code is redrawn rather than waited on.
QR_TIMEOUT = 30


def draw(url: str) -> None:
    code = qrcode.QRCode()
    code.add_data(url)
    # invert=True draws the quiet zone as blocks — the polarity a scanner expects
    # on a dark terminal.
    code.print_ascii(invert=True)


async def scan_qr(client) -> None:
    login = await client.qr_login()
    while True:
        draw(login.url)
        print("Telegram → Settings → Devices → Link Desktop Device, then scan.")
        try:
            await login.wait(QR_TIMEOUT)
            return
        except asyncio.TimeoutError:
            print("code expired, drawing a new one...\n")
            await login.recreate()
        except SessionPasswordNeededError:
            # 2FA is on: the QR scan is accepted, the cloud password finishes it.
            await client.sign_in(password=getpass("2FA cloud password: "))
            return


async def main() -> int:
    client = build_client()
    await client.connect()
    try:
        if not await client.is_user_authorized():
            await scan_qr(client)
        print(f"Logged in as {get_display_name(await client.get_me())}")
    finally:
        await client.disconnect()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
