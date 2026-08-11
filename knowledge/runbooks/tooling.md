# Runbook — tooling inventory (MCP servers & plugins)

What is wired up, at which scope, how it authenticates, and where it bites. The short routing map
(`task → tool`) lives in `CLAUDE.md ## Tooling`; this file is the full inventory and is **not**
loaded at startup. Tool *schemas* are already in the agent's context — nothing here restates them.

Detected 2026-08-11. Re-detect with `/mcp` (live servers) and `claude mcp list`; plugin state is
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

## Present but irrelevant to this project

- **`blockscout`** (user) — blockchain explorer. No chain in this repo; do not reach for it.
- **`rust-analyzer-lsp`** (plugin) — no Rust here. `~/CLAUDE.md` lists it in a generic cross-project
  dev stack; this project narrows that.
- **Canva / Gmail / Google Calendar / Google Drive** — account connectors, unrelated to the pipeline.
- **`claude-in-chrome`** — no web sources in the MVP (Telegram only, `docs/SPEC.md`).
- Disabled plugins: `code-review`, `improve`, `drawio`, `serena`.

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
