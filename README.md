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

## Running it

```
pip install -e '.[serve]'   # fastapi + uvicorn, pinned
make serve                  # http://localhost:8000/ — the app and its API, localhost only
make loop                   # the $0 loop: wake on the schedule, tick, one line into results/loop.log
```

`make loop` buys nothing. `data/loop.json :: endpoint` is the operator's own field: the daemon
reads it, says in the log which of the two nothings the queue is, and never starts a paid pass.

To keep the loop running at login, install the launchd template — the executor never does this:

```
sed -e "s|__REPO__|$PWD|g" \
    -e "s|__PYTHON__|$(python3.11 -c 'import sys; print(sys.executable)')|g" \
    ops/com.marketpulse.loop.plist > ~/Library/LaunchAgents/com.marketpulse.loop.plist
launchctl load ~/Library/LaunchAgents/com.marketpulse.loop.plist    # unload to stop it
```

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

Read from result files only, never hand-typed: the block below is written by
`scripts/build_readme_results.py` and the promo screen (`make promo-screen`,
`dashboard/promo.html`) prints the same rows through the same reader; both refuse,
by name, when a file is missing.

<!-- S2 READINGS — written by scripts/build_readme_results.py from the result files each row names; regenerate, never edit -->
**S2 — reactions under promo posts, graded on the frozen holdouts.** Per comment: what it is about (subject, bar 0.80); per thread: what it says (signal types, bar 0.75). Shipped as measured (ruling 06.09 (cc)); every number below is the named file's.

| reading | subject | signal | file |
|---|---|---|---|
| holdout-2 · loop (hooks + P1) — shipped | 0.7411 (83/112) ❌ bar 0.80 | 0.7937 ✅ bar 0.75 | `results/grade_promo_loop_readings.json` :: sets.dev3.after |
| holdout-2 · with P1 — reading | 0.7500 (84/112) ❌ bar 0.80 | 0.8021 ✅ bar 0.75 | `results/grade_promo_p1_readings.json` :: sets.dev3.after |
| holdout-2 · raw — reading | 0.7054 (79/112) ❌ bar 0.80 | 0.8021 ✅ bar 0.75 | `results/grade_promo_holdout2.json` :: whole_40 |
| holdout-40 · raw — reading | 0.7181 (135/188) ❌ bar 0.80 | 0.7958 ✅ bar 0.75 | `results/grade_promo_holdout40.json` :: whole_40 |

The shipped row is the product's pipeline end to end: every answer through the four hooks of §2 S4 — a signal row whose quote is not a substring of the comment it cites is dropped — and then P1. The «with P1» reading beside it is that same layer over the model's RAW answer, one filter upstream, so the two differ by exactly what the hooks drop; the «raw» rows are the reader before P1 at all. A number measured upstream of a product filter is the model's, disclosed as such, never the product's (ruling 08.09 (dd)).

Of the 28 comments «holdout-2 · with P1 — reading» still misses, 16 are rows the gold itself marked `unsure` — the codebook allows two readings there (a store-stock complaint: the chain or the product; a post in the chain's own channel: the chain or the post).
<!-- /S2 READINGS -->
