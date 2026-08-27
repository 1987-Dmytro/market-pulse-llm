# harness-v2.1 — the executor's environment now refuses what it used to only promise

**Question.** Does the executor's environment enforce the v2.1 loop — phase spec → plan → review →
go → report that answers first — by files and hooks rather than by memory? **Yes for every guard the
contract names: each was seen refusing and seen accepting.** One assertion in the contract is not
true — step 0's `test_the_registration_rebuilds…` is **still red at HEAD**, for a string the
contract does not name (Dv1).

| guard | refusal, shown | acceptance, shown |
|---|---|---|
| `PreToolUse(Bash)` sweeping stage | live tool call `git add -A --dry-run` **blocked**: `refused by hook: stage BY PATH (git add <file>...), never the whole tree`; `git add .` exit 2 offline | `git add docs/plans/.gitkeep` staged it; `git add -A-not-a-flag.txt`, `git commit -m 'x'` exit 0 |
| `PreToolUse(Bash)` repo-wide format | live tool call `ruff format . --check` **blocked**: `refused by hook: repo-wide format is forbidden (producer pins)`; `make fmt` exit 2 offline | `ruff format src/market_pulse/prompts.py`, `make check` exit 0 |
| `permissions.deny` team-lead paths | `Write docs/PHASE-x.md`, `Write docs/labels-x.jsonl`, `Edit docs/SPEC-v2-promo-pulse.md` → `File is in a directory that is denied by your permission settings`, 0 bytes written | the same tool wrote `docs/probe-acceptance-x.md` (same `docs/` root) and `docs/plans/.probe-acceptance.md`; both deleted after the reading |
| SessionStart cost | — | `context-census.py` **12.6Ktok → 9.3Ktok**, target 10.7K, warning gone; `hot.md` curated 148 → **40** lines |

## Evidence per check

**(1) `pytest tests/test_hooks.py -q` → `2 passed in 0.30s`**, driving the real
`scripts/hooks/refuse-sweeping-commands.sh` (mode 100755) both ways. The two live blocks above are
that guard refusing real Bash tool calls in this session, chosen non-destructive on purpose
(`--dry-run` stages nothing, `--check` writes nothing).

**(2) `permissions.deny`.** The discriminator: the two refused paths never existed and were never
created, and `docs/SPEC-v2-promo-pulse.md` was probed with an `old_string` that provably does not
occur in it — a guard that had failed to load would have answered «string not found» and still
written nothing. The acceptance half proves the refusal is by PATTERN, not by directory. The
replacement of `.claude/settings.json` is purely additive: normalised `diff` against the previous
version adds the guard and three deny patterns (`SPEC-*.md`, `PHASE-*.md`, `labels-*.jsonl`) and
drops nothing, the graphify hook included.

**(3) 12.6Ktok → 9.3Ktok — it shrank.** Everything dropped from `hot.md` is in
`knowledge/daily_logs/2026-08-27.md` verbatim. The two literals `scripts/volume_calc_5c1.py` greps
out of that file survive character-for-character and were grepped back out of the live file after
the rewrite: `pytest tests/test_volume_calc_5c1.py -q` → `10 passed`, `check-wikilinks.py` → `none
broken`. The new `.claude/rules/reports-and-plans.md` carries `paths:`, so it costs 0 at startup —
and it injected itself into this session the moment `docs/reports/harness-v2.1.md` was edited.

**(4) `make check`** — tail below; no new red.

**(5) `/plan-phase` and `/report` are in the command list.** The session's skill listing refreshed
as the files landed and reads, verbatim: `plan-phase: /plan-phase <name> — write the plan for
docs/PHASE-<name>.md, then STOP for review` · `report: /report <name> — write
docs/reports/<name>.md` (beside `save` and `close` from the same directory).

**Applied byte-verbatim** (`diff -u` silent on each): `CLAUDE.md` (72 lines) · `.claude/settings.json`
· `scripts/hooks/refuse-sweeping-commands.sh` (`chmod +x`) · `tests/test_hooks.py` ·
`.claude/commands/{plan-phase,report,save,close}.md` · `.claude/rules/reports-and-plans.md` ·
`docs/plans/.gitkeep`.

**Archive: 115 prompts → 28 moved to `docs/archive/prompts/` (28 `R` lines, nothing deleted), 87
stay.** 84 stay because a script, test or sealed record names them — every one of the 115 grepped as
a fixed string over `scripts/ tests/ src/ results/*.json`, and as a control over all of `results/`
and `data/` (zero further hits); `preflight`'s pin registry pins nine by sha, all nine already in
that 84. Three stay against the mechanical rule, which is the judgement it cannot make:
`PROMPT-harness-v2.1.md` is the contract being executed, `PROMPT-retail-census-r2.md` is untracked
and queued (`git mv` could not have touched it), `PROMPT-phase7-a1.md` is unexecuted work in
`hot.md`'s Next.

**MCP/plugins → `knowledge/runbooks/tooling.md` «Relevant here»**, from `docs/PROCESS.md` 27.08.
`code-review` is decided IN and is **not enabled**: `claude plugin list` reads it `Scope: user`,
`Status: ✘ disabled`, `~/.claude/settings.json` disables it by name, no repo file overrides that,
the drafted `.claude/settings.json` carries no `enabledPlugins` block, and a repo-side override of
an explicit user-level `false` cannot be verified from inside the session that writes it. **The
operator's one line, inside `enabledPlugins`: `"code-review@claude-plugins-official": true,`**
(equivalently `claude plugin enable code-review@claude-plugins-official`).

## Deviations

**Dv1 [cause: contract-gap] — step 0's test is red at HEAD, and not over the quotes.**
`producer.build()` finds all three (ф) sentences, so that half is fixed; the test fails one line
later at `assert witness in path.read_text()` — `MOVED_BY_D2_STEP_0`'s witness `D1 (инструмент, $0)`
is absent from `docs/STATUS.md`. Present at `09954df`, gone from `370f016` on: one re-spec washed
out two strings and the team lead restored one. Named, not fixed — the witness guards the D2
registration and what STATUS must carry is the team lead's to decide.

**Dv2 [cause: contract-gap] — `docs/STATUS.md` joined the step-0 commit though step 0 did not name
it.** Two of the three (ф) sentences existed only in the working tree, so «GREEN at HEAD» was
unmeasurable until STATUS was committed. Committed by path, unedited.

**Dv3 [cause: tooling] — the hook matches its patterns anywhere in the command text.** A `git commit`
whose *message* quotes the refused forms is itself refused; this contract's commits pass their
messages through `-F <file>`. The pattern is not anchored to the command's first word, so an `echo`,
a `grep` or a message that merely mentions the sweep is blocked too.

**Dv4 [cause: verify-gap] — the drafted `tests/test_hooks.py` is not `ruff format`-clean** (a blank
line after the docstring, one tuple exploded per line). `make check` runs `ruff check`, not the
formatter, so it is green either way. Kept byte-verbatim per «copy, do not paraphrase»; the remedy
is one allowed command, `ruff format tests/test_hooks.py`, on the team lead's word.

**Dv5 [cause: process] — this report is over the ≤30 prose lines `/report` sets.** The artifact
asked for each guard's refusal *and* acceptance plus evidence for five checks; the two ceilings do
not both fit. Prose was cut to the shortest that still shows every reading.

## Debts

- **The deny list does not follow the archive.** `Edit(/docs/PROMPT-*.md)` is not recursive: the 28
  files under `docs/archive/prompts/` are editable by the Edit tool. One line — `Edit(/docs/archive/**)`
  — closes it; `.claude/settings.json` is the team lead's draft, so it is named here, not changed.
- **`.claude/rules/harness-plumbing.md` is now incomplete**: it lists the SessionStart and Stop hooks
  and two operator commands, and knows nothing of the `PreToolUse` guard or of `/plan-phase` and
  `/report`. Not in the contract's file list; two lines when the team lead wants them.
- **Uncommitted, pre-existing, not mine:** `docs/reports/lora-c-run-r3.md` (modified in the tree by
  the team lead), `knowledge/daily_logs/2026-08-26.md` and `knowledge/index.md` (yesterday's
  `/close`), `_to_delete/` (a 0-byte `git-index.lock`), `docs/PROMPT-retail-census-r2.md` (queued).
- **Two reds, both older than this contract:** `test_the_registration_rebuilds…` (Dv1) and
  `test_repair_phase4_ledger` (the r3 ledger debt).

## The verifier

```
$ make check
ruff check .
All checks passed!
pytest -q
...
=========================== short test summary info ============================
FAILED tests/test_repair_phase4_ledger.py::test_the_silence_check_fires_on_the_LINE_ledger_too
FAILED tests/test_think_zero_shot.py::test_the_registration_rebuilds_except_where_step_0_moved_a_pin
2 failed, 4101 passed, 2 skipped in 704.45s (0:11:44)

# before this contract, at e11c9a9 + the uncommitted tree:
2 failed, 4099 passed, 2 skipped in 706.30s (0:11:46)
```

Same two reds before and after, +2 passed — `tests/test_hooks.py`. The reading was taken at
`abe56bb`, the commit before this report ([[provenance_cannot_name_itself]]).

Commits: `e60a233` step 0 · `8580d1d` the harness files · `9e7ae6e` hot.md at 40 lines and 9.3Ktok · `ce00b70` the tooling runbook · `abe56bb` 28 prompts archived · this report.
