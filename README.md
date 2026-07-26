# market-pulse-llm

Competitor Intelligence System for the food / snack / confectionery market
(RU / UA / EN). The operator registers 2-3 direct competitors; the system
monitors their Telegram channels, detects new-product launch announcements, and
classifies audience reactions in the comments (sentiment, sarcasm, and the
hidden intents taste / price / packaging / quality / availability) into
comparative launch analytics.

**MVP constraint:** Telegram only, $0 data budget. X, FB/IG and website
monitoring are deferred extensions with no code in this repo.

**`docs/SPEC.md` is the single source of truth** for scope, success gates and
phases — read it before any task. Current phase: **1 — verifier skeleton**.

## Requirements

Python 3.11+ with `pytest`, `ruff` and `pyyaml` available (pinned in
`pyproject.toml`; `pip install -e '.[dev]'` inside a `.venv` if they are not on
your PATH already).

## Verifier

```
make check        # ruff check . && pytest -q — must be green after every commit
```

## Competitor registry

`config/competitors.yaml` maps each competitor to their Telegram channels. The
entries shipped today are placeholders: the real competitors are selected in
Phase 2, after checking that their channels have comments enabled.

```
PYTHONPATH=src python3 -m market_pulse.registry config/competitors.yaml
```

## Results

No measured numbers are published yet. When they are, this README and the
dashboard will read them from result files only and fail loudly if a source is
missing — never hand-typed.
