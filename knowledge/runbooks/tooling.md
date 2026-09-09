# Runbook — tooling inventory (MCP servers & plugins)

What is wired up, at which scope, how it authenticates, and where it bites. The short routing map
(`task → tool`) lives in `CLAUDE.md ## Tooling`; this file is the full inventory and is **not**
loaded at startup. Tool *schemas* are already in the agent's context — nothing here restates them.

Detected 2026-08-11, plugin state re-read 2026-08-27 with `claude plugin list` (name, scope,
enabled). Re-detect with `/mcp` (live servers) and `claude mcp list`; plugin state is
`enabledPlugins` in `~/.claude/settings.json`.

## Scopes — where each server comes from

| Scope | Where it is declared | Servers |
|---|---|---|
| Project (committed) | `.mcp.json` in this repo | **none** — `{"mcpServers": {}}` |
| User | `~/.claude.json` → `mcpServers` | `blockscout`, `ref` |
| Plugin | `context7@claude-plugins-official` | `context7` |
| Account connector | claude.ai, per-account (not in any repo file — observed in-session) | Canva, Gmail, Google Calendar, Google Drive |
| Host | Chrome extension / IDE extension (same: not repo-declared) | `claude-in-chrome`, `ide` |

The project file stays empty on purpose: the data budget is $0 and the project has no database and no
API of its own. A server earns a place in `.mcp.json` only if it is *this project's* backend — see
the scoping rule in the file's own `_comment`.

## Relevant here

- **`ref`** (user) · **`context7`** (plugin) — library/API documentation. Free, no key in the repo.
  Use either before writing against `telethon`, `pyyaml`, `pytest` or `ruff` APIs; never guess a
  version. `context7` resolves a library id first, so it is the better one for "which version has X".
- **`ide`** — `getDiagnostics` gives fast lint feedback while editing. It is *not* the verifier:
  `make check` (`ruff check . && pytest -q`) is the single judge, per `CLAUDE.md`.
- **`ponytail`** (plugin, level `full`) — anti-overengineering pressure on every response. Explains
  why a diff here is expected to be small and why deliberate simplifications carry a `ponytail:`
  comment naming their ceiling.
- **`commit-commands`** (plugin) — commit helpers. Commits stay atomic and staged **by path**;
  never `git add -A` (a queued prompt or a Stop-hook regeneration gets swept in).
- **`security-guidance`** (plugin) — worth a pass over the collector and any credential path
  (`TELEGRAM_API_*`, session files).
- **`gh` CLI** — all GitHub work. Preferred over a GitHub MCP: less context, saner rate limits.
- **`code-review`** (plugin) — decided IN on 27.08 (`docs/PROCESS.md`, «MCP/plugins»): a fresh
  subagent reviews the diff before `/report` on money, secrets or guard code (team-lead skill v2.1
  §6). **ENABLED 08.09** (ruling (ee)3) — `~/.claude/settings.json :: enabledPlugins` now carries
  `"code-review@claude-plugins-official": true`, at USER scope like the install; the repo's
  `.claude/settings.json` still has no `enabledPlugins` block by design.
- **`graphify`** (CLI + git `post-commit` hook, not an MCP) — the repo's knowledge graph; see its
  section below. Kept by the 27.08 decision together with `ref`/`context7`, `commit-commands`,
  `security-guidance`, `ponytail` and `gh`; `.mcp.json` stays empty.
- Team-lead side (Cowork, not this session): device folder access to the repo, web search for
  sources, Project docs for handoffs. It never runs the executor's tools on the repo.

## Present but irrelevant to this project

- **`blockscout`** (user) — blockchain explorer. No chain in this repo; do not reach for it.
- **`rust-analyzer-lsp`** (plugin) — no Rust here. `~/CLAUDE.md` lists it in a generic cross-project
  dev stack; this project narrows that.
- **Canva / Gmail / Google Calendar / Google Drive** — account connectors, unrelated to the pipeline.
- **`claude-in-chrome`** — no web sources in the MVP (Telegram only, `docs/SPEC.md`).
- **`serena`**, **`drawio`**, **`improve`** — deliberately unused here (27.08 decision); all three
  are disabled in `~/.claude/settings.json`. `code-review` is decided IN and listed above.
- **`pyright-lsp`** (plugin, enabled at user scope) — Python diagnostics while editing; like `ide`
  it is not the verifier. Not named by the 27.08 decision, listed here so the inventory is complete.

## graphify — the repo's knowledge graph

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).

Moved out of `CLAUDE.md` on 2026-08-19 by `boot-debloat`, verbatim; the one-line
trigger stayed there.

## Gotchas

- **Telegram is not an MCP.** Collection is Telethon inside `scripts/collect_*.py`; handle FloodWait
  with backoff + cursor resume, never harvest members. One paced client per session file.
- **Nothing in this inventory bills.** Paid model calls go through the repo's own scripts, under the
  cap named by the phase's pre-registration — not through a server.
- **`/code-review ultra` is operator-triggered and billed.** The plugin is disabled and an agent
  cannot launch it; do not try via Bash.
- **Connector servers need an interactive login.** In a headless or cron run Canva/Gmail/Calendar/
  Drive may simply be absent — never make a step depend on one.
- **Chrome dialogs freeze the extension.** An `alert`/`confirm` blocks every later command; read
  console output instead.
- **Secrets via env vars only.** `.mcp.json` is committed — a key pasted into it is a key published.
