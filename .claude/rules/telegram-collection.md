---
paths:
  - "scripts/collect_*.py"
  - "scripts/fetch_*.py"
  - "scripts/harvest_*.py"
  - "scripts/late_batch_*.py"
  - "scripts/backfill.py"
  - "scripts/discover_channels.py"
  - "scripts/entry_check.py"
  - "scripts/poll_census.py"
  - "scripts/tg_login.py"
  - "src/market_pulse/telegram_client.py"
  - "src/market_pulse/backfill.py"
  - "src/market_pulse/entry_check.py"
---
# Telegram collection — the two Pitfalls that are collector-scoped

Moved out of `CLAUDE.md` on 2026-08-19 by `boot-debloat` (the joint sitting's group D),
verbatim: still true, and needed only by a session that opens the files below.

- Handle Telegram FloodWait with backoff + cursor resume; no member harvesting.
- Verify source channels have comments enabled before relying on them.
