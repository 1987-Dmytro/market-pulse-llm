# market-pulse-llm

Competitor Intelligence System (food/snack, RU/UA/EN): Telegram-only MVP, $0 data
budget. docs/SPEC.md is the source of truth — read it before any task.

## Rules
- Chat: Russian. All artifacts (code, comments, commits, docs): English.
- Sources: Telegram only. No X/FB/IG/web code in MVP.
- No training before pre-registered baselines; smoke run before any long run.
- Frozen test sets and docs/SPEC.md are immutable without operator approval.
- Dashboard/README numbers come from result files only; fail loudly if missing.
- Small diffs, atomic commits, `make check` green after every commit.
- Every task report includes verifier command output, not just a summary.
- Execute the given scope exactly; state assumptions explicitly; never expand
  or silently shrink scope — flag conflicts and stop.

## Pitfalls
- Handle Telegram FloodWait with backoff + cursor resume; no member harvesting.
- Verify competitor channels have comments enabled before relying on them.
- Sarcasm labeling: follow the annotation guideline; `unclear` excluded from gates.
- src/market_pulse/scorer.py is the single judge of all numbers; never fork it.
