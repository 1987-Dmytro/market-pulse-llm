# PROMPT — `think-zero-shot-d2` (fresh session; ONE paid pod, cap $8.00; issued only on the operator's «go»)

You are the executor on `market-pulse-llm`. D1 (`9c29ae0`, report `docs/reports/think-zero-shot-d1.md`) is
accepted. This session RUNS the registered measurement — `results/prereg_think_zero_shot.json` is the
contract (stages 1–7 in order, packs by sha, rungs under `money`); `docs/PROCESS.md` has the money mechanics.
Read STATUS §6t, PROCESS «Money», the prereg, and this file. Nothing else before step 0.

**Step 0 ($0, before the pod).** Commit the six untracked/modified team-lead files BY PATH, one commit:
`docs/STATUS.md`, `docs/PROCESS.md`, `docs/PLAN-harness-gemma4-think.md`, `docs/PROMPT-phase7-a1.md`, this
prompt, `docs/reviews/2026-08-26-*.md` (an untracked team-lead file VOIDs `make check-stamped`, Dv852). Add
`Edit(/docs/PROCESS.md)`, `Edit(/docs/PLAN-*.md)`, `Edit(/docs/reviews/**)` to the deny list in
`.claude/settings.json` (PROCESS «File ownership» promises them; the file carries four). Fix the one defect the
fresh reviewer found: `scripts/reader_v5_pod_runner.py :: run` persists a `length`-cut reply through
`split_thought` alone, so an UNCLOSED thought with a balanced object inside is written as `balanced: True`
with the working-out truncated — apply the unclosed rule `stops_here` already uses (`prefix = None` when
`not thought and THOUGHT_OPEN in emitted`; `thought_chars` = the whole emitted length in that state, since
the thought-length distribution is a registered reading) and add the test that fails without it. Re-run
`tests/test_think_zero_shot.py` and `scripts/preflight_serving_guards.py`; paste both tails.

**The pod.** `mp-srv2` volume, RTX PRO 4500 32 GB EU-RO-1 (fallback 4090), price ≤$0.80/h at create (rung 0).
Stage 1–2 = smoke (longest pass-2 thread + 3 dev rows): s/call, thought tokens, peak VRAM → three rows into
`results/measurements.jsonl` (`source` = the out-file). Project every remaining stage at the MEASURED rate
(rung 2) and stop where the contract says; then stages 3 → 7 in order, one command each, out-files
`*.READER_THINK.jsonl`, pulled and hashed both sides after every stage. Liveness (rung 1): 900 s from the last
reply. Never leave the pod unpolled; never a second billing resource; never touch `mp-lora-c`. Teardown
proven by a listing (`mp-srv2` present).

**Report — `docs/reports/think-zero-shot.md`, ≤30 lines + the table.** Per stage: BEFORE · thinking · delta ·
n on identical rows (dev-200 v1/v2, «our» 49, pass-2 bars 4/5 · 3/4 · red via the shipped gate, holdout 64/100);
flips both ways with row ids; parse failures and `length` cut-offs counted; thought-length distribution;
s/call and $ per stage by the pod clock, guard delta beside. Deviations with cause tags; STOP — the operator
decides the path on the table.

**DO NOT:** edit prompts, packs, gold, sealed records or team-lead files; tune anything after seeing a reply;
exceed $8.00; `git add -A`; invent a number a file does not carry.
