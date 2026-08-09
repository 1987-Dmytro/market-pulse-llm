# PROMPT-5c1-vis-a-r — the GM4 caption instrument, re-issued against the serverless runtime ($0)

> Re-issue 2026-08-09. The HOLD original at this path is preserved in git
> (commit `74a5adb`). Authority: SPEC amendments 3.13 (captions move to our
> own GM4) and 3.14 (runtime target = serverless); executed after srv-2d —
> `results/parity_srv2.json` holds, serverless is the validated runtime.
> This contract is **$0**: code, tests, records, runbook. Creating ANY
> billable resource (endpoint, pod, template, volume) is OUT of scope.

## Read first (sections, not whole documents)

- `docs/SPEC.md` — the 3.13 and 3.14 amendment entries only.
- `knowledge/hot.md` — "Next" and the first six footguns (smoke `--record`
  default; ms-vs-seconds policy; FETCH_HEAD; guard blindness to serverless
  billing; shared `marketpulse.session`; bare `--posts`/`--comments`).
- `scripts/serve_handler.py` docstring and the job contract around
  `batch_size` / `dump_path`; `src/market_pulse/prompts.py` around
  `CAPTION_TASK` / `FREE_TEXT`; `src/market_pulse/parents.py::context`.

**Read-back check — the FIRST lines of your report:** list the four step-0
commits and the five deliverables, one line each, before any diff.

## Step 0 — session tail and the record debt (commits pre-authorised)

1. Vault-tail commit, exactly these paths: `knowledge/hot.md`,
   `knowledge/index.md`, `knowledge/daily_logs/2026-08-08.md`,
   `knowledge/daily_logs/2026-08-09.md`, `.claude/rules/phase345-artifacts.md`.
2. Team-lead docs commit — content unedited, commit only:
   `docs/STATUS.md`, `docs/PROMPT-5c1-vis-a.md`.
3. ADR `knowledge/decisions/srv2-program-close.md` + INDEX entry, numbers
   only from artifacts: probe (~$0.03, `docs/probe-serverless-20260808.md`)
   → srv-2a $0 → srv-2b abort ($0.9999, `results/spend_srv2b.json`) →
   srv-2c boot log + unwrapped control ($0.1377,
   `results/srv2c_bootlog.json`) → srv-2d parity spent-and-holds
   ($1.2383, `results/spend_srv2d.json`, `results/parity_srv2.json`,
   `results/srv2d_cost.json`). Decision lines: serverless = production
   runtime (ruling 23 / amendment 3.14); srv-2b blame = platform
   transient, established by the unwrapped control; cost finding
   $1.0825/pass vs $0.4611 (×2.35) goes to the 5c2 briefing;
   scale-to-zero saving NOT measured. One commit.
4. Ownership hardening: in `.claude/settings.json`, add `Write(...)`
   mirrors for the three existing `Edit(...)` deny rules (STATUS, SPEC,
   PROMPT-*). One commit.

## Deliverables (five; if one runs deeper than briefed — STOP and report, do not compress quality to fit)

1. **`CAPTION` serving config.** `src/market_pulse/serving.py` +
   `scripts/serve_handler.py` gain a third config beside A/B: NF4 base at
   the pinned revision, vision path via the existing
   `AutoModelForImageTextToText` branch (`local_llm.py:109`), **no adapter
   loaded — assert its absence at load**, greedy, forward batch 1 always.
   Job shape reuses the proven contract (`batch_size`, `dump_path`; the
   volume is the dump/log channel). `settings()` refuses
   `SERVING_CONFIG=CAPTION` combined with any adapter env var set.
2. **Registered GM4 caption prompt.** New task `caption_post_gm4` BESIDE
   `caption_post` (registered prompts are never edited in place): its own
   sha, member of `FREE_TEXT`, refused by `build_messages` / `parse_reply`
   by name, registration asserted both ways following the
   `tests/test_prompts.py` pattern. Draft the text from `caption_post`,
   adapted to GM4's chat template; thinking channel OFF as everywhere.
3. **`caption_source` provenance.** New required field on every NEW
   caption record: `"qwen-4.5g2"` | `"gm4-nf4-base"`. Old caption files
   stay bytes. The two existing caption READERS
   (`scripts/rematch_with_captions_5c1.py`,
   `scripts/recheck_with_captions.py`) refuse an input mixing sources
   unless the record names both. Nothing else changes.
4. **Driver + runbook.** `scripts/caption_gm4_5c1.py`: consumes a media
   manifest of the `results/post_media_5c1.json` shape, submits ONE job
   per slice to an endpoint id given by flag/env with NO default, writes
   `results/captions_gm4_<scope>.json` with its own three-key spend
   anchor (copy `scripts/caption_atb_5c1.py`; do NOT import the relabel
   ledger helper — wrong-phase provenance, see the rules file).
   `scripts/runbook_vis_b.md`: §A endpoint from template (env incl.
   `SERVING_CONFIG=CAPTION`; request policy via
   `serving.execution_policy` only); §B smoke — 1 post, dump read back
   byte-for-byte, `--record` to a NEW path; §C rate measure → re-pilot
   of the 19 ATB posts → GM4-vs-qwen bridge on identical posts → screen
   v2 bar A against the UNTOUCHED prereg
   (`results/yield_screen_5c1.json`, sha `1aa89818…`); abort ladder (no
   retries), cleanup proven by listing; worker stdout redirected to the
   volume as a standing line.
5. **Tests.** `make check` green. New tests: CAPTION refusals (adapter
   env set; missing endpoint id), prompt registration both ways, required
   `caption_source` on new records, reader refusal on silent mixing, and
   that no NEW seconds→ms conversion point exists outside
   `serving.execution_policy`.

## Do NOT

- Do not edit `docs/STATUS.md`, `docs/SPEC.md`, `docs/PROMPT-*.md` —
  team-lead files (File ownership); commit-only. Phase-end facts go to
  `implementation-notes.md` / the daily log.
- Do not create endpoints, pods, templates or volumes; no paid API calls.
- Do not touch `data/frozen/**`, `results/baselines.json`,
  `results/verdict_*.json`, `results/parity_*.json`, the adapter, or any
  registered prompt in place.
- Do not run `smoke_5b.py` without an explicit `--record` path.
- Never `git add -A`; stage by path. The vault tail of THIS session goes
  to its own final commit (same fixed paths as step 0.1 plus today's log).

## Verify — evidence, not assertions

- `make check` tail (test count + wall time) after step 0 and at close.
- `grep -n "caption_post_gm4" src/market_pulse/prompts.py` (+ the sha line).
- `grep -n "CAPTION" scripts/serve_handler.py src/market_pulse/serving.py`.
- One-liner output proving `settings()` refuses CAPTION + adapter env.
- `git log --oneline` for the session (atomic commits, dependencies first).
- `implementation-notes.md` gains a Deviations section for this contract —
  silence is not compliance.

Report in English. State your assumptions explicitly.
