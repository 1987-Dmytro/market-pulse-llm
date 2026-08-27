# CLAUDE.md

Guidance for Claude Code (the EXECUTOR) in this repository. The team lead is a separate Claude
session (skill `team-lead` v2.1); the operator relays between the two and owns every decision.

# market-pulse-llm

Marketing-research instrument for a Ukrainian dairy brand: Telegram retail chains (prices, promo
depth, comments under promo posts) and Poltava-region chats; tracked category = dairy + ice cream;
brand watchlist. Local Gemma-4-31B + QLoRA adapter for comment labelling. Rented GPUs, $0 data budget.

## Where the truth lives (read in this order, only the sections your task names)

1. `docs/PRODUCT.md` — the customer's questions (north star). 2. `docs/SPEC-v2-promo-pulse.md` —
the current product spec: stage, success criteria S1–S4, sources, contracts. 3. `docs/PHASE-*.md` —
the executable phase spec you were handed (question · checks · files · out of scope · stop-points).
4. `docs/STATUS.md` — the map (where we are, proven numbers, live rulings). 5. `docs/PROCESS.md` —
mechanics: ownership, money rungs, pins, report and plan formats. `docs/SPEC.md` rev. 3.x is FROZEN
law for sealed registrations: consult it only when a sealed record cites it; never edit it.

## File ownership — one writer per file (enforced by `permissions.deny`)

- Team-lead files — read and commit BY PATH, never edit: `docs/STATUS.md`, `docs/SPEC*.md`,
  `docs/PRODUCT.md`, `docs/PROCESS.md`, `docs/PHASE-*.md`, `docs/PROMPT-*.md`, `docs/PLAN-*.md`,
  `docs/reviews/**`, `docs/labels-*.jsonl`. A fact for the map goes into your report or the daily
  log; the team lead moves it into STATUS at acceptance.
- Executor files: `src/`, `tests/`, `scripts/`, `results/`, `config/`, `knowledge/**`,
  `implementation-notes.md`, `docs/plans/**`, `docs/reports/**`, runbooks, `.claude/**`, the rest.

## Workflow per phase (the loop the team lead accepts)

1. Read the phase spec's question and checks FIRST; mechanics in it are constraints, not the goal.
2. Write `docs/plans/<phase>.md` (`/plan-phase`): the question, the artifact that answers it, every
   check you will run, steps, files touched, stop-points, and every threshold/floor/sample/window
   you intend to introduce. STOP and hand the plan to the operator for the team lead's review.
3. On «go»: implement in small commits by path; run the checks after every change; a stop-point
   (operator decision, paid or irreversible step) is a question BEFORE, never a report after.
4. Report (`/report`) to `docs/reports/<phase>.md`: the question and its answer in the first ten
   lines; evidence (commands, outputs, files); deviations with cause tags; `make check` tail.
   Tables over 40 rows are files the report links. Chat gets the path.
5. Two failed corrections in one session → say so; the team lead reissues in a fresh session.

## Rules
- Chat: Russian. All artifacts (code, comments, commits, docs, plans, reports): English; STATUS and
  PROCESS are the team lead's and may be Russian.
- Collection sources: Telegram only. HTTP is allowed for DISCOVERY of official handles (chain sites).
- Numbers only from result files through the scorer/build; never typed; fail loudly when a source is
  missing. `src/market_pulse/scorer.py` is the single judge of all numbers; never fork it.
- No training in stage 1; smoke before any paid run; money rungs and caps: `docs/PROCESS.md`.
- Frozen test sets, sealed registrations and `docs/SPEC.md` are immutable; a moved pinned module is
  claimed through `tests/moved_pins.py`, never by re-pinning.
- Never `git add -A`; never `make fmt` repo-wide (hooks refuse both). `make check` green after every
  commit — a red you did not cause is named in the report, not fixed silently.
- Execute the plan the team lead approved: never expand or silently shrink scope; a threshold that
  is not in the plan is a scope change — stop and ask.

## Second brain
- `knowledge/hot.md` is injected at SessionStart: keep the curated block ≤40 lines — it is a cache,
  not a log. Durable lessons → native memory; volatile state → hot.md; decisions → `knowledge/decisions/`.
- `knowledge/` is an Obsidian vault; `[[wikilinks]]` are reader pointers. Path-scoped invariants
  live in `.claude/rules/*.md` with `paths:` frontmatter, not here. This file stays ≤80 lines.

## Stack & commands
Python 3.11+, no framework; dev: `pytest`, `ruff` (`pip install -e '.[dev]'` in `.venv`).
`make check` → `ruff check . && pytest -q` (the verifier) · `make check-stamped` → a HOLDS reading at
a HEAD · `make preflight` → pins, digests, quotes before touching a pinned file · one test:
`pytest tests/test_registry.py -q`. Outside pytest: `PYTHONPATH=src`.

## Tooling
- `graphify query "<question>"` before grepping; `graphify query "what reads <file>"` before moving a
  shared artifact; the post-commit hook rebuilds the graph. Library/API docs → `context7` or `ref`.
- GitHub → `gh`. Full inventory and what is deliberately unused: `knowledge/runbooks/tooling.md`.
