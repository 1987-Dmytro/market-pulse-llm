# PROCESS — project overlay for the `team-lead` skill v2.1 (market-pulse-llm)

Team-lead file (executor: read and commit, never edit). Everything here is specific to THIS repo
and was moved out of the skill on 2026-08-26; the skill states the principle, this file the
mechanics. Operator-facing digest of the same rules: `docs/STATUS.md` («Правила, которые легко
забыть»). Case chronicles: `docs/reviews/`, `docs/reports/`, `knowledge/decisions/`.

## File ownership (single writer per file)
- Team-lead files: `docs/STATUS.md`, `docs/SPEC.md` (frozen rev. 3.x), `docs/SPEC-*.md` (current product
  spec), `docs/PRODUCT.md`, `docs/PROCESS.md`, `docs/PHASE-*.md` (executable phase specs), `docs/PROMPT-*.md`
  (one-sentence contracts and legacy prompts), `docs/PLAN-*.md`, `docs/reviews/`, `docs/labels-*.jsonl`.
  Executor commits them by path, never edits. Deny rules for Edit/Write on these paths live in
  `.claude/settings.json`; `/save` and `/close` carry the negative line.
- Executor files: `src/`, `tests/`, `scripts/`, `results/`, `config/`, `knowledge/**`, `implementation-notes.md`,
  `docs/plans/**` (the executor's plan per phase), `docs/reports/**`, runbooks, `.claude/**` (harness), the
  rest of `docs/`. The team lead reads, never edits; harness changes are issued as a contract with the
  file contents drafted under `docs/reviews/<date>-harness-*/` and applied by the executor.
- `docs/STATUS.md` is a machine-read INPUT: sealed producers grep rulings out of it verbatim
  (`scripts/write_lora_c_prereg.py :: quoted()`, `write_think_zero_shot_prereg.py`). Quoted rulings
  live in the MACHINE-READ BLOCK at its end and are never re-flowed; STATUS prose above the block
  may be compacted freely — a quoted sentence compacted by mistake reddened a test on 27.08 (Dv866).
  Before editing any team-lead file, ask who READS it (`make preflight`).

## Cadence per phase (skill v2.1 §3, §5)
1. Team lead writes `docs/PHASE-<name>.md`: **question → artifact → checks → files/interfaces → out of
   scope → stop-points → end-to-end check**; mechanics only as constraints. Phase boundaries are cut at
   stop-points (operator decision, paid or irreversible step), never at file boundaries.
2. Executor, fresh session, `/plan-phase <name>` → `docs/plans/<name>.md` → STOP. Team lead reviews the
   plan (checks named, stop-points respected, every threshold/floor/sample listed) → operator relays «go».
3. Executor implements by the plan; `/report <name>` → `docs/reports/<name>.md` (answer in ten lines).
4. Team lead accepts by diff, artifact and check; STATUS refreshed; one retro line.
One-sentence contracts (`docs/PROMPT-*.md`) remain for fixes and debts whose diff fits in a sentence.

## Hooks and guards (deterministic — "must happen every time")
- `PreToolUse(Bash)` `scripts/hooks/refuse-sweeping-commands.sh`: refuses `git add -A|--all|.` and
  `make fmt` / `ruff format .`; both directions asserted in `tests/test_hooks.py`.
- `permissions.deny` on every team-lead path (list above). `SessionStart`: hot-cache refresh, `hot.md`
  (curated block ≤40 lines), stale-check, context census. `Stop`: brain-session-end. Git `post-commit`:
  graphify rebuild.

## Pins and sealed records
- Sealed registrations pin `src/market_pulse/prompts.py`, `scorer.py`, `brands.py`, `local_llm.py`,
  `window_summary_5c2.py`, the pod runners, `registry.yaml`/`lexicon.yaml`, and PLAN files by sha.
  A sealed record is never re-pinned; a moved module is claimed through `tests/moved_pins.py`
  (allowance derived from live shas, both directions), never by editing the record.
- `make preflight` before any contract that moves a pinned file: names, digests, prose quotes, pin
  registry. `make fmt` repo-wide is forbidden (producer pins). Never `git add -A`.
- `results/measurements.jsonl` is the registry of physical constants (s/call, s/step, VRAM, rates),
  one row per measurement with `source`, `n`, `max`. A rate is a property of the pod it was
  measured on; a remembered number is not a prior (the 97 s/thread error, 26.08).

## Money (rented GPUs; console empty between sessions)
- Readings come from the guard (`results/spend_cycle2.json`), pod hours are the quotable number,
  the billing walk lags 30–40 min. Cap = 2× the registry estimate; one paid run per prompt.
- Four rungs on every paid contract: (0) price at create ≤ the registered ceiling; (1) liveness —
  deadline from the LAST log line or reply, never from create; (2) projection after the smoke and
  after every stage at the MEASURED rate — over cap by ≤20 % → ASK (hold ≤10 min for the
  operator's typed word, quoted verbatim in the report; silence = KILL), over by more → KILL;
  (3) platform hard stop from the cap at the observed price.
- Smoke first, stages in VALUE order, each completed stage a usable number. Never two billing
  resources concurrently; a probe that creates billable resources is not a probe. Teardown is
  proven by a listing from the team-lead side, positive-controlled on a known-live sibling.
  Every paid contract names its recovery clause (what may be re-created within the same cap).
- Pre-registration: readings-not-bars where the operator decides on a table; bars with kill
  criteria where a claim is made; one attempt; an aborted measurement resolves to its default;
  a program pre-registers its stop rule. Stop-rules that bind the team lead: one-pass reader
  (17.08), line B (20.08), lora-c (26.08).

## Executor conventions
- `implementation-notes.md` keeps a Deviations section; every Dv ends with a cause tag from the
  closed enum `[cause: contract-gap | spec-gap | verify-gap | env | tooling | model | process]`,
  optional trailing `[[lesson-name]]`. Reports close with ≤5 lines of Process signals.
- Reports are files in `docs/reports/` (≤30 lines under v2), the chat carries only the path. Numbers
  name the file they come from. **A report opens with the operator's question the contract names and
  answers it in its first ten lines**; a table longer than 40 rows is a file the report links, and the
  report carries the top rows that answer the question (D2: 64 lines; C1: 361 lines — the rule's cause).
- A contract states, before its mechanics, the ONE question the operator will answer from the
  deliverable; a deliverable that measures everything and answers nothing is not accepted.
- `make check` is the verifier (ruff + pytest); `make check-stamped` for a HOLDS reading at a HEAD;
  `scripts/preflight_serving_guards.py` renders the real chat template offline (zero cost) — run it
  before any pod that changes a template or serving config.
- Tools: vault in `knowledge/` (hot.md, daily logs, `knowledge/decisions/` + INDEX), code graph via
  `graphify` (`graphify query "what reads <file>"` before any contract that moves a shared
  artifact; post-commit hook rebuilds; `--update` after doc changes), `/save` at session end.
- MCP/plugins (decided 27.08, inventory `knowledge/runbooks/tooling.md`): `.mcp.json` stays empty; kept —
  `context7`/`ref` (docs), `commit-commands`, `security-guidance`, `ponytail`, `graphify` CLI + hooks, `gh`;
  enable `code-review` (fresh-subagent diff review before `/report` on money/secrets/guard code — skill v2.1
  §6); deliberately unused here — `blockscout`, `rust-analyzer-lsp`, `serena`, `claude-in-chrome`, `drawio`,
  account connectors. Team-lead side (Cowork): device folder access to the repo, web search for sources,
  Project docs for handoffs; it never runs the executor's tools on the repo.

## Operator language
- Conversation and `docs/STATUS.md` in Russian; code, commits, prompts, ADRs, reports in English.
