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
- Verify source channels have comments enabled before relying on them.
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

## Code map

Which phase is live is in `knowledge/hot.md` and `docs/STATUS.md`, never here or in code comments.

- `src/market_pulse/scorer.py` — one public function per Tier-1 gate; every one raises
  `NotImplementedError` until its phase implements it. `tests/test_scorer.py` discovers those
  functions reflectively, so adding a public function to the module immediately puts it under the
  same rule: it must refuse to run until real numbers back it.
- `src/market_pulse/registry.py` — `config/registry.yaml` → frozen `Source` / `Taxonomy` /
  `WatchlistBrand` inside a `Registry`, raising `ValueError` that names the defect (malformed
  `@handle`, duplicate id, empty channel list, unknown `source_type`, no tracked groups). Strict on
  purpose: a silently accepted typo collects nothing and only surfaces as wrong analytics much
  later. Channel handles are candidates with `verified: false` until the Phase 2 entry check.
- The target pipeline — collector → normalize/dedup/lang-id → model service → aggregation →
  dashboard, behind a source-agnostic connector interface — is specified in SPEC §5; `src/` is the
  authority on which parts are built.

## Harness plumbing

- Hooks in `.claude/settings.json`: SessionStart runs `scripts/refresh-hot-cache.py`,
  `scripts/stale-check.sh` and `scripts/context-census.py`; Stop runs
  `scripts/brain-session-end.py`, which regenerates `knowledge/index.md` and the daily-log stub.
  Generated regions belong to those scripts — do not hand-edit them.
- `/save` (checkpoint) and `/close` (end of day) in `.claude/commands/` are operator-invoked only.

## Tooling

- Library/API docs → `context7` or `ref`; never guess a version.
- GitHub → `gh` CLI, never a GitHub MCP (context + rate limits).
- `blockscout` / `rust-analyzer-lsp` are user-level and irrelevant here — do not reach for them.
- `ponytail` is active (level `full`) — smallest working diff; a deliberate simplification carries a
  `ponytail:` comment naming its ceiling.
- Full inventory, auth and gotchas: `knowledge/runbooks/tooling.md`.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
