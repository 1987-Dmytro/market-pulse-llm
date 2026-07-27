# market-pulse-llm

Category Intelligence System for the Ukrainian food retail market (UA / RU / EN).
The system monitors the Telegram channels of retail chains and discount
aggregators, filters the stream to the tracked category (dairy and ice cream),
detects new-product and promo announcements, extracts brand mentions, and
classifies audience reactions in the comments (sentiment, sarcasm, and the
hidden intents taste / price / packaging / quality / availability) into
comparative per-brand and per-launch analytics.

**MVP constraint:** Telegram only, $0 data budget. X, FB/IG and website
monitoring are deferred extensions with no code in this repo.

**`docs/SPEC.md` is the single source of truth** for scope, success gates and
phases — read it before any task.

## Requirements

Python 3.11+ with `pytest`, `ruff` and `pyyaml` available (pinned in
`pyproject.toml`; `pip install -e '.[dev]'` inside a `.venv` if they are not on
your PATH already).

## Verifier

```
make check        # ruff check . && pytest -q — must be green after every commit
```

## Source registry

`config/registry.yaml` holds the three registry entities (SPEC §3): **sources**
(Telegram channels per retail chain / aggregator, tagged by `source_type`),
**taxonomy** (tracked category groups) and the brand **watchlist**. New sources,
groups and brands are added by editing that file — no code changes. Channel
handles ship as candidates with `verified: false` until the Phase 2 entry check
confirms the blue-check channel and that comments are enabled.

```
PYTHONPATH=src python3 -m market_pulse.registry config/registry.yaml
```

## Results

No measured numbers are published yet. When they are, this README and the
dashboard will read them from result files only and fail loudly if a source is
missing — never hand-typed.
