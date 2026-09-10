# PROCESS — project overlay for the `team-lead` skill v2.1 (market-pulse-llm)

Team-lead file (executor: read and commit, never edit). Everything here is specific to THIS repo
and was moved out of the skill on 2026-08-26; the skill states the principle, this file the
mechanics. Operator-facing digest of the same rules: `docs/STATUS.md` («Правила, которые легко
забыть»). Case chronicles: `docs/reviews/`, `docs/reports/`, `knowledge/decisions/`.

## File ownership (single writer per file)
- Team-lead files: `docs/STATUS.md`, `docs/SPEC.md` (frozen rev. 3.x), `docs/SPEC-*.md` (current product
  spec), `docs/PRODUCT.md`, `docs/PROCESS.md`, `docs/PHASE-*.md` (executable phase specs), `docs/PROMPT-*.md`
  (one-sentence contracts and legacy prompts), `docs/PLAN-*.md`, `docs/reviews/`, `docs/labels-*.jsonl`,
  `docs/CODEBOOK-*.md` (the annotator's law the labels follow; versioned inside the file, cited by the dev-loop report).
  **v2.7 (10.09, ruling (nn)):** `docs/DESIGN-*.md` (the front end's brief) is a team-lead file too; `frontend/`, `dashboard/app/`, `ops/`,
  `firebase.json` and `scripts/{serve,loop_daemon,export_front_data}.py` are the executor's.
  Executor commits them by path, never edits. Deny rules for Edit/Write on these paths live in
  `.claude/settings.json`; `/save` and `/close` carry the negative line.
- Executor files: `src/`, `tests/`, `scripts/`, `results/`, `config/`, `knowledge/**`, `implementation-notes.md`,
  `docs/plans/**` (the executor's plan per phase), `docs/reports/**`, runbooks, `.claude/**` (harness), the
  rest of `docs/`. The team lead reads, never edits; harness changes are issued as a contract with the
  file contents drafted under `docs/reviews/<date>-harness-*/` and applied by the executor.
- Team-lead files are suite INPUTS beyond the machine-read block: tests also grep WITNESS phrases out
  of STATUS **prose** (`MOVED_BY_D2_STEP_0`; the 30.08 compaction erased «D1 (инструмент, $0)» and
  reddened `test_think_zero_shot` — second occurrence of Dv866's class). After ANY compaction of a
  team-lead file, the team lead runs `make check` BEFORE handing over — not at the next acceptance.
- `docs/STATUS.md` is a machine-read INPUT: sealed producers grep rulings out of it verbatim
  (`scripts/write_lora_c_prereg.py :: quoted()`, `write_think_zero_shot_prereg.py`). Quoted rulings
  live in the MACHINE-READ BLOCK at its end and are never re-flowed; STATUS prose above the block
  may be compacted freely — a quoted sentence compacted by mistake reddened a test on 27.08 (Dv866).
  Before editing any team-lead file, ask who READS it (`make preflight`).

## Cadence per phase (skill v2.1 §3, §5)
1. Team lead writes `docs/PHASE-<name>.md`: **question → artifact → checks → files/interfaces → out of
   scope → stop-points → end-to-end check → §8 DONE WHEN covering the WHOLE phase**; mechanics only as
   constraints. Phase boundaries are cut at stop-points (operator decision, paid or irreversible step),
   never at file boundaries. **Every stop-point names its DECISION TABLE** — the columns the operator
   reads to decide in ONE visit — and the $0 steps filling those columns are phase steps BEFORE the
   stop (30.08: census→smoke→pagecount became three artifacts because the money stop never said «the
   table = exact pages × measured rate × remainder»). Information found missing AT a stop joins the
   SAME plan by revision — never a new contract file.
2. Executor, fresh session, `/plan-phase <name>` → `docs/plans/<name>.md` → STOP. Team lead reviews the
   plan (checks named, stop-points respected, every threshold/floor/sample listed) → operator relays «go».
3. Executor implements by the plan, launched as ONE GOAL LOOP PER PHASE (30.08; hardened 01.09
   after the slice-pile retro and the /goal docs check). Only the USER can invoke `/goal`, and the
   command itself starts the work — so the phase spec's §8 is a SINGLE-LINE predicate the operator
   pastes into a FRESH session, the same paste at start and after every STOP. The predicate opens
   with the START RITUAL (commit team-lead files by path; read the plan + the newest dated section
   of the rulings file `docs/reviews/<date>-plan-<name>.md`; apply and delete `docs/plans/<name>.STOP.md`
   if present). Every clause is a command and its expected output, or a file and its field — never
   prose — and the predicate orders each check's output SHOWN in the conversation, because the
   evaluator is a small model reading ONLY the transcript (it runs nothing); a passed-count floor,
   no test deleted, «a test that must change to pass» is a STOP. A STOP (stop-point · question ·
   tree state, ≤15 lines) is a PAUSE: the team lead APPENDS a dated ruling, the operator re-pastes
   the SAME `/goal`. LAUNCH (02.09, from the transcripts): the operator TYPES `/goal ` by hand and
   pastes the BODY — a pasted block that begins with the command is plain text, no goal is active
   (01.09 08:18 ran 35 min with no evaluator, reading the turn cap as its own rule); the body carries
   no slash command of its own — the args are cut at the first one (01.09 19:16 lost the turn cap
   and the resume sentence); the phase spec's §8 holds the body's exact bytes. After pasting, WATCH
   FOR THE FIRST TOOL CALL: on this build `/goal` can merely SET the condition («Goal set: …»)
   without starting a turn — 02.09 idled 12 h on exactly this; if nothing runs within a minute, send
   one word («go»). ENDING A PAUSE (03.09, from the transcript + the /goal docs): the evaluator
   does not honour the predicate's PAUSE branch — it blocked eight turns in a row before the
   Stop-hook cap (`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`, default 8) forced the end. So when the STOP
   file is written and the report committed, the executor's last line is «STOP — /goal clear» and
   the OPERATOR types `/goal clear` (aliases `stop`, `off`); the resume is a fresh session with the
   same paste (an active goal is restored only by `--continue`/`--resume`, never by a new session).
   The predicate never changes mid-phase — one exception ruled 03.09 (c): a clause the evaluator
   provably reads as an unsatisfiable precondition (the PAUSE branch's resume tail) is REMOVED by the
   team lead, the version bumps (§8 v4) and the operator pastes the new body from then on; a predicate
   describes a STATE, never a sequence. The rulings file grows; handovers never
   assume session survival. Slices and per-slice predicates are the failure mode this rule prevents.
   `/report <name>` is a clause of the predicate. The evaluator's «met» is NOT acceptance (step 4).
   **v3 (03.09 evening, ruling (e) + `docs/reviews/2026-09-03-retro-process-v3.md`): for phases with stop-points the
   `/goal` launch above is RETIRED** — the evaluator cannot honour a pause (27 blocked turns in three sessions). The
   operator pastes a STANDING PROMPT (≤12 lines, in the newest ruling) into a fresh session; the session does ONE item,
   shows its check, updates `docs/plans/<name>.PROGRESS.md` (done / next / open stop, ≤60 lines — replaces STOP files
   and reports) and ends its turn at a stop-point. Rulings ≤12 lines, decide and never legislate. `/goal` only for a
   single session with one measurable end and no human decision inside.
4. Team lead accepts by diff, artifact and check; STATUS refreshed; one retro line.
One-sentence contracts (`docs/PROMPT-*.md`) remain for fixes and debts whose diff fits in a sentence.

## Models and effort (02.09; v2.4 08.09 — effort and orchestration are FIELDS of the harness, see «Harness fields»)
- Executor = **Claude Opus 5 (1M)** until the phase gate (a model change re-issues the standing prompt — at a phase boundary,
  never inside a paid step; Fable 5.1 is the candidate from C6). Effort `xhigh` and `ultracode` OFF come from `.claude/settings.json`
  (v2.4); the operator types NOTHING before pasting. `ultracode` (xhigh + a workflow per task, up to 16 agents) is switched on only
  by `/effort ultracode` in a session the team lead names for a fan-out (an audit, a review sweep) — never for an item or a paid run
  (s35: 57 agents, 40 dead on the model limit, 22 of 26 findings unverified; s36: a 20-agent review starved `make check` of memory).
- Fresh-context reviewer on money/guards (`/code-review`): the strongest model available (Fable when offered, else
  Opus); mechanical sweeps (file audits, migrations): Sonnet. A model change re-dials autonomy and re-issues prompts.

## Hooks and guards (deterministic — "must happen every time"; v2.4: timeouts are SECONDS, one SessionStart hook)
- `PreToolUse(Bash)` `scripts/hooks/refuse_sweeping_commands.py`: refuses `git add -A|--all|.` and
  `make fmt` / `ruff format .` (exit 2 — blocks in every permission mode); both directions asserted in `tests/test_hooks.py`.
  Its `timeout` is 30 s and generous on purpose — the docs: «a timed-out command hook doesn't block the tool call».
- `permissions.deny` on every team-lead path (list above) — blocks in every mode, `bypassPermissions` included. `SessionStart`:
  ONE sequential hook (hot-cache refresh → `hot.md`, curated block ≤40 lines → stale-check → context census; hooks of one event
  run in PARALLEL, so a data dependency lives inside one command). `Stop`: brain-session-end. Git `post-commit`: graphify rebuild.

## Harness fields (v2.4, 08.09 — ruling (ee); v2.5, 09.09 — ruling (ff); v2.6, 09.09 — ruling (gg): no allow rules, the deny rules reach into Bash; the audit: `docs/reviews/2026-09-08-tooling-audit.md`)
- **The permission mode of every executor session is `bypassPermissions`, set where the platform reads it without a hand: the
  operator's USER settings, `~/.claude/settings.json :: permissions.defaultMode` (09.09)** — the docs («Which mode a session starts
  in»): the user file sets the starting mode, while a `bypassPermissions` in `.claude/settings.json` or `.claude/settings.local.json`
  is ignored and starts the session in Manual mode. The launch line is therefore plain `claude` (`--dangerously-skip-permissions`
  stays harmless); v2.4's flag-as-field failed in the first session that forgot it (s37 ran in auto mode; its refused `cp` and
  `sed -n` were the deny rules reaching into Bash, not the classifier — v2.6 below). Why bypass: the auto-mode classifier never sees `pod create` / `pod delete` (s33's two denials), while
  the protection that counts stays — `permissions.deny` on team-lead files («Deny rules block in every mode, including
  bypassPermissions»), the sweep-refusing hook (exit 2 blocks in every mode), the money guard in the repo's own scripts.
  **The proof:** a `PreToolUse(Bash)` hook stamps the hook input's `permission_mode` into `.claude/session_mode` (gitignored) on
  every Bash call, and every paid runbook's §0 gate reads it FIRST — `grep -qx bypassPermissions .claude/session_mode && echo
  "MODE bypass"`, chained with `&&` before the pin check and the registration: a session in another mode ends at $0 before any
  anchor. **No allow rules (v2.6, ruling (gg)):** «Allow rules have no effect in bypassPermissions» (permission-modes) — a rule that
  can only matter in a session the first gate refuses is inert, and an inert field maintained per leg is a ritual; (ee)'s
  `pod create` / `pod delete` pair (written for s33's symptom while the leg creates a template and an endpoint) is retired, the
  runbook's create-prefix gate with it. `permissions.allow` is `[]` and stays so.
- **Effort and orchestration are fields, not rituals:** `.claude/settings.json` → `"env": {"CLAUDE_CODE_EFFORT_LEVEL": "xhigh"}`
  (the highest-precedence effort setting in the docs' order) and `"ultracode": false` (the key persists; `/effort ultracode` is
  session-only). `/effort xhigh` is no longer typed.
- **Hook `timeout` is in SECONDS** (default 600): guard hooks get a generous one (30 s — a timed-out `PreToolUse` command hook
  does NOT block, so a short timeout is a hole, not a safety), context hooks a short one; a dependency between hooks of one event
  lives inside ONE command (they run in parallel).
- **The check of the fields** — run by the executor when the file changes and by the team lead at acceptance:
  `python3 -c 'import json,sys;s=json.load(open(".claude/settings.json"));h=[x for e in s["hooks"].values() for g in e for x in g["hooks"]];ok=s.get("env",{}).get("CLAUDE_CODE_EFFORT_LEVEL")=="xhigh" and s.get("ultracode") is False and s["permissions"].get("allow",[])==[] and len(s["permissions"]["deny"])==12 and all(x.get("timeout",600)<=60 for x in h) and len(s["hooks"]["SessionStart"][0]["hooks"])==1 and any("session_mode" in x.get("command","") for x in h);print("HARNESS FIELDS OK" if ok else "HARNESS FIELDS MISSING");sys.exit(0 if ok else 1)'`
  → `HARNESS FIELDS OK`, exit 0 (v2.6: `allow == []`, deny ×12, effort, ultracode, timeouts ≤ 60, one start hook, the stamp hook;
  MISSING on a file that still carries allow rules — both directions run when it was issued). A harness change is issued as a WHOLE
  file under `docs/reviews/<date>-harness-*/settings.json`; the executor reads it with the Read tool and writes `.claude/settings.json`
  with the Write tool (permission-modes «Protected paths»: writes under `.claude` are allowed in bypassPermissions), `diff` empty is
  the proof; the hooks are re-read by the file watcher (hooks-guide) and the start of the NEXT session verifies them (hot.md injected
  once, the census line) — the team lead never edits the executor's harness. A paid runbook's §0 = the mode gate FIRST `&&` this
  check, chained before the pin check and the registration.
- **A harness rule is written from the platform's documentation read that day** (the mechanism quoted beside the rule), never from a
  symptom in a transcript; its proof is deterministic — a field shown in the file, a rule shown to match — never a harmless call
  that passed (v2.3's `--help` proof is retired: a harmless call passes the classifier without any rule).
- **The deny rules reach into Bash (v2.6, ruling (gg)):** «Read and Edit deny rules apply to Claude's built-in file tools, to file
  commands Claude Code recognizes in Bash, such as `cat`, `head`, `tail`, and `sed`, and to the targets of Bash redirections such as
  `> file` and `< file`. They don't apply to arbitrary subprocesses that read or write files indirectly» (permissions; the CHANGELOG
  of 2.1.261 names `cp -r` under the same coverage) — in every mode. The `cp` and `sed -n` refused on `docs/reviews/**` in s37 (auto)
  and s38 (bypass, stamped) were the 12 rules working, not the classifier ((ff)2 corrected). The executor never names a deny-listed
  path as an operand of a Bash file command: team-lead files are read with the Read tool (the rules are Edit-only), the harness file
  is written with the Write tool, `diff` proves it; one refusal of a documented kind meets the documented path — never a series of
  probes (s38: five).

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

## Money (rented GPUs; console empty between sessions) — v2.1, 06.09 (ruling (y): the registration OPENS the line → it runs in the paid session); v2, 05.09: the mechanics rulings (q)…(x) fixed; `docs/PHASE-*.md` §6.1 is the phase's instance of this section
- **A PAID run is a whole session** (03.09): create → settlement in one session; in front of the create ONLY the line's
  opening (§0a of the runbook: `--dry-run` → `--register` → commit → `--pack` → commit → `make check`, minutes, no
  development) and no second create behind it; its runbook is written the session BEFORE and re-pointed to THAT run
  (part, file names, step line, card, launch line) so the paid session pastes and transposes nothing. Rulings name the
  command whose output is the number, never the number itself; a cap named in a ruling is quoted from the `--dry-run`.
- **One paid run = ONE step line** (`promo-iter<N>` · `promo-holdout2` · `promo-c3`), OPENED BY THE REGISTRATION ITSELF:
  `--register --part <part> --step <line> --cap <cap>` reads the guard WITH `--step <line>`, and that reading creates
  `results/spend_<line>.json` and anchors it at the balance then — so the registration runs in the PAID session, minutes
  before the create, NEVER a session earlier (ruling (y): the close's right-hand side is a balance delta with the volume's
  drip IN, the settled figure keeps it OUT — iter4's whole 2.73 % was the volume over 2.45 h; the 5 % band shuts at ≈ 4 h
  of anchor age). The pre-pod `--note "<line> — pod about to be created"` follows it as the session's ledger line. The team
  lead reads the dry run (`results/promo_dev40_prep.json`) + the code at HEAD BEFORE the purchase and the registration at
  acceptance, against the dry run (same pins, bound, card, backstop — only the anchor is new). The emitter's default step
  is the open multi-run line `promo-dev-loop` — its guard refuses (unbounded delta since 03.09); the line is never named again.
  **v2.2 (06.09, ruling (aa), the verifier's finding before the holdout-2 purchase): a registration is NEVER repeated on an
  anchored line** — once the line has swallowed any cent (the volume's drip across an hour boundary, a rung-1-killed pod) a
  second `--register` at the full cap refuses (`cap = min(cap, step_remaining, remaining)`); a re-registration (a price move
  in §0, a STOP retried an hour later) goes under a NEW line (`--step <line>-r2`, its own ledger) or with `--cap` = the guard's
  printed remaining of the line, the operator's word. **A runbook gate is a command that can fail the session** (exit ≠ 0, the
  next command chained with `&&`), placed BEFORE the step it guards — the four-pin check runs on the disk files before
  `--register`; a printed «STOP» with exit 0 is a note, not a gate. When the hard stop fires (spent == cap) the post-run
  `--note` refuses — it is not retried; `--close` settles on the walk alone (PHASE v13).
  **Where a ruling and this section disagree on a mechanic, this section wins: follow it, name the contradiction in PROGRESS, no stop.**
- **Pricing:** the rate is the WHOLE-RUN mean of the slowest pod seen (`results/measurements.jsonl`, `sample: whole run`,
  n = the run's units) — never a smoke of three, never a borrowed sibling; the dear corner (the run's max on every unit)
  is priced and shown; when it does not fit, the leg issues FITS on the MEAN corner with the cap as the hard stop and
  no band gate (rulings (r)(t)). The card and its price are FIELDS of the record read at $0 from `runpodctl gpu list`:
  the gpu-id (typed at `pod create` and `--open --card`, checked by rung 1) and the `displayName` (EXACT, for the dearer
  of secure/community) — never constants of the emitter; the card is chosen in the ruling's order when one is out of stock.
- **Bounds:** `--terminate-after` = the cap's minutes at the registered price — the hard stop; a borrowed minute-constant
  (the 90-min backstop) that would bite first bounds the READING, not the money: the record says which bound is live.
  Rungs today: (0) price at create ≤ registered; (1) liveness — the ssh dead-man from the sibling's production record;
  (2) the band gate is NOT run on a leg issued on the mean corner; (3) the platform hard stop. Never two billing
  resources at once; the always-on volume drips ≈ $0.24/day into every open window; teardown proven by
  `runpodctl pod list -a` → `[]` before every STOP and before the session ends.
- **The smoke** = the run's shortest, median and LONGEST render, first — a card too small fails on three units, not
  eighty. The runner writes a failed unit's ERROR reply (`id`, `error`, `exception`, `unanswered`) and exits non-zero;
  the Mac reads `--smoke --part <part> --replies <file>`: «3 replies are in» → GO · «the smoke did not come back» →
  delete AT ONCE · waiting → a poll, paired with `pgrep` (no runner alive = the same outcome). Every reader of the
  reply file (`--smoke`, `--close-segment`, `--score`) reads whole lines and counts an error row as unanswered.
- **Closing a line (PHASE v13):** after `pod delete` and BEFORE any next pod — the post-run `--note` on the line (the
  gate's reference is the line's LAST open reading; a pre-pod one refuses the close for ever), then `--close
  --expect-ms <the segment's billed ms, from results/promo_dev_loop_run.json at/after the line's anchor> --until <after
  the pod> --tolerance 0.05`. Billing lags 30–60 min: a PARTIAL walk is refused and retried at the next session's start,
  read-only walk first. A line whose readings all predate its pod closes on the walk alone and never takes a late
  reading — it would carry the next run's money. `--close-segment --replies <file>` writes the run record first.
- **Validity (PHASE §6.5):** a reading counts only when every registered unit is answered and parsed; a serving failure
  (OOM, a crash) moves the SERVING (a card ≥ the footprint, the allocator env in the launch line), never the
  instrument; the re-buy takes the next number on its own line inside the 5-run ceiling.
- Cycle ceiling = `CYCLE3_CAP_USD` in the guard (the operator's word; the anchor is never regenerated). Pre-registration:
  readings-not-bars where the operator decides on a table; bars with kill criteria where a claim is made; one attempt
  on a frozen set; a spent set is demoted to a reading. Stop-rules that bind the team lead: one-pass reader (17.08),
  line B (20.08), lora-c (26.08).

## Executor conventions
- `implementation-notes.md` keeps a Deviations section; every Dv ends with a cause tag from the
  closed enum `[cause: contract-gap | spec-gap | verify-gap | env | tooling | model | process]`,
  optional trailing `[[lesson-name]]`. Reports close with ≤5 lines of Process signals.
- `docs/plans/<name>.STOP.md` is the executor's honest exit from a goal loop: the stop-point
  reached, the question for the team lead, the tree's state (commits, uncommitted files); ≤15 lines.
- Reports are files in `docs/reports/` (≤30 lines under v2), the chat carries only the path. Numbers
  name the file they come from. **A report opens with the operator's question the contract names and
  answers it in its first ten lines**; a table longer than 40 rows is a file the report links, and the
  report carries the top rows that answer the question (D2: 64 lines; C1: 361 lines — the rule's cause).
- A contract states, before its mechanics, the ONE question the operator will answer from the
  deliverable; a deliverable that measures everything and answers nothing is not accepted.
- **The paid session's irreversible command never meets a permission gate it can lose** (v2.3 06.09 after s33's two classifier
  denials, ≈ 16 min of anchor age; **v2.4 08.09 replaces v2.3's `--help` proof, which proved nothing; v2.5 09.09 moves the mode
  out of the operator's hands; v2.6 09.09 retires the allow rules — inert in bypass**): the mode is the user settings' default and
  the mode stamp is a FIELD («Harness fields»); the paid runbook's §0 reads the stamp FIRST and then the fields check (exit ≠ 0)
  before any anchor; a deny-listed path is never an operand of a Bash file command (the deny rules reach into Bash, every mode).
  A permission prompt or denial inside a paid session is a stop, and the team lead's.
- `make check` is the verifier (ruff + pytest); `make check-stamped` for a HOLDS reading at a HEAD;
  `scripts/preflight_serving_guards.py` renders the real chat template offline (zero cost) — run it
  before any pod that changes a template or serving config. v2.9 (10.09, ruling (ss)): when the suite
  outruns the harness's one-call ceiling (~12 min against 10), the executor may run it in SLICES whose
  union is PROVEN equal to `ls tests/test_*.py` (no gap, no overlap, a dropped slice refused) — the
  totals are the claim, the slicing is named in PROGRESS; the ONE-call reading is the team lead's
  snapshot run, recorded in the next ruling.
- Tools: vault in `knowledge/` (hot.md, daily logs, `knowledge/decisions/` + INDEX), code graph via
  `graphify` (`graphify query "what reads <file>"` before any contract that moves a shared
  artifact; post-commit hook rebuilds; `--update` after doc changes), `/save` at session end.
- MCP/plugins (decided 27.08, inventory `knowledge/runbooks/tooling.md`): `.mcp.json` stays empty; kept —
  `context7`/`ref` (docs), `commit-commands`, `security-guidance`, `ponytail`, `graphify` CLI + hooks, `gh`;
  `code-review` ENABLED 08.09 (a fresh-subagent diff review on money/secrets/guard code; the team lead's verifier stays
  the gate); deliberately unused here — `blockscout`, `rust-analyzer-lsp`, `serena`, `claude-in-chrome`, `drawio`,
  account connectors. Team-lead side (Cowork): device folder access to the repo, web search for sources,
  Project docs for handoffs; it never runs the executor's tools on the repo. Its shell on the linked Mac is a VM
  that cannot delete files: never run `git status`/`git add` there (a leftover `.git/index.lock` blocks the
  executor's git — 03.09) — read-only `git --no-optional-locks status`, `git log`, `git rev-parse` only; the
  labels are written whole (`device_commit_files`), checked by the team lead's own validator against a dump of
  the drawn threads (`data/annotation/dev40_threads.json`, gitignored), never edited in place. Desktop Commander runs natively on
  the Mac (no VM): the team lead reads there, runs `git --no-optional-locks` read-only, runs its own suite ONLY ON A SNAPSHOT of the accepted tree (v2.8, 10.09, ruling (pp): `rsync -a --exclude graphify-out
  --exclude __pycache__ <repo>/ /tmp/mp-snap/ && cd /tmp/mp-snap && make check`, `.git` INCLUDED — the producers' `git ls-files` gates and
  ruff's gitignore need it; a snapshot without `.git` read 297 false «not tracked» failures — in the background; ONE known environment failure in a snapshot:
  `tests/test_baselines.py::test_the_block_carries_every_section_a_contract_pastes` — `scripts/baselines.py` keys the boot files by the repo's
  ABSOLUTE path, so `MEMORY.md` is absent at any other path; read it as expected, never as a defect) — a `make check` on the LIVE tree raced the executor's next session on 10.09 and read 8 false
  failures; the working tree is the executor's the moment the operator pastes the next prompt — uses `~/.pyenv/shims/python3.11` (homebrew's lacks the deps), and writes NOTHING
  into the repo while an executor session is running (its porcelain stamp) — team-lead files are written between sessions and
  committed by path at the next start ritual.

## Operator language
- Conversation and `docs/STATUS.md` in Russian; code, commits, prompts, ADRs, reports in English.
