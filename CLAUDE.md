# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# market-pulse-llm

Category Intelligence System for Ukrainian food retail (UA/RU/EN): retail-chain and
aggregator Telegram channels, tracked category = dairy + ice cream, brand watchlist.
Telegram-only MVP, $0 data budget.

## Where the truth lives

`docs/SPEC.md` is the contract, not a briefing — consult the sections your task touches, not the
whole file: **§3** registry entities · **§5** pre-registered gates G1a–G1e · **§6** architecture ·
**§8** phases and their verify-gates. Amendments are in the header block.
`docs/STATUS.md` is the current map (phase, proven numbers, what is deferred). Decisions and their
numbers live in `knowledge/decisions/` (start at `INDEX.md`); the Russian summaries of the same
decisions are in STATUS.md.

## File ownership — one writer per file

- Team-lead files: `docs/STATUS.md`, `docs/SPEC.md`, `docs/PROMPT-*.md` — read and commit them,
  never edit. `permissions.deny` in `.claude/settings.json` enforces it (an `Edit(...)` rule covers
  every file-editing tool, Write included). Phase-end facts go to the daily log or
  `implementation-notes.md`, never into STATUS.md.
- Executor files (the team lead does not edit them): `src/`, `tests/`, `scripts/`, `results/`,
  `config/`, `knowledge/**`, `implementation-notes.md`, runbooks, the rest of `docs/`.
- `docs/reports/` — executor's; a phase report is a FILE (`docs/reports/<phase>.md`, own commit
  `docs(report): <phase>`), never a chat summary. Chat gets the path.

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

## Stack & commands

Python 3.11+, no framework. Runtime dep: `pyyaml`. Dev: `pytest`, `ruff` — `pip install -e '.[dev]'`
inside a `.venv` if they are not on PATH.

- `make check` → `ruff check . && pytest -q`. The single verifier; must be green after every commit.
- `make fmt` → `ruff format .` (line-length 100, configured in `pyproject.toml`).
- One test: `pytest tests/test_registry.py::test_duplicate_source_id_rejected -q`.
  `pythonpath = ["src"]` is set in `pyproject.toml`, so pytest needs no `PYTHONPATH`.
  Outside pytest the package is not installed — plain `python3 -c "import market_pulse"`
  fails; prefix with `PYTHONPATH=src`.
- Registry CLI: `PYTHONPATH=src python3 -m market_pulse.registry config/registry.yaml`.

## Tooling

- Library/API docs → `context7` or `ref`; never guess a version.
- GitHub → `gh` CLI, never a GitHub MCP (context + rate limits).
- `blockscout` / `rust-analyzer-lsp` are user-level and irrelevant here — do not reach for them.
- `ponytail` is active (level `full`) — smallest working diff; a deliberate simplification carries a
  `ponytail:` comment naming its ceiling.
- `graphify` — knowledge graph at `graphify-out/`; run `graphify query "<question>"` before
  grepping the codebase, and `graphify update .` after changing code. Rules: the runbook below.
- Full inventory, auth and gotchas: `knowledge/runbooks/tooling.md`.
