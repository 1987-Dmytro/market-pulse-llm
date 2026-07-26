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

<!-- brain-init: second-brain layer (added 2026-07-26) -->
## Second brain

- Live state (active now / next / blockers) → `knowledge/hot.md`, injected at every SessionStart.
  Edit only the curated block below the AUTO-GEN marker; never touch the markers themselves.
- Durable lessons → native memory; volatile state → `hot.md` only. One home per fact.
- `knowledge/` is an Obsidian vault: open THAT folder, not the repo root. Do not create vault files
  unless asked, do not restructure its folders. `[[wikilinks]]` are reader pointers — the harness
  does not resolve them.
- Bulky instructions scoped to a path → `.claude/rules/*.md` with `paths:` frontmatter (0 tokens at
  startup). This file keeps only always-needed rules and stays ≤200 lines.

<!-- /init fold-in: code map / stack, filled by native /init; apply the removal test afterwards -->
