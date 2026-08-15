# PROMPT — probe-a (the thread-reader probe: prompt + gold + prereg + one gated paid pass; cap $0.20)

**Contract class:** prep is $0; ONE paid serverless pass under a **$0.20 cap** with a go/no-go
warm-up gate — the 12.08 manual-probe rule, applied to a new model capability.
**Baseline:** `make check` 2 438 passed / 2 skipped @ fix-c close; record HEAD.
**Design authority:** `docs/PLAN-comment-signals.md` (§2 duties order, §3 schema, §5 bars) ·
`docs/REFERENCE-signals-w1.md` (the gold source) · operator rulings 15.08: taxonomy ratified ·
per-comment agreement bar **≥0.80** · window reading time budget **≤30 min billed** · gate =
narrow lexicon + silencers, precision lives with the reader.
**Money discipline:** before the session, read the spend guard (never the ledger line — Dv33);
line remainder is ~$1.55; this contract may not exceed $0.20 all-in.

## Step 0 — tail

Commit the standing tail by path (verify live `git status`; `docs/REFERENCE-signals-w1.md` and this
prompt arrive untracked — verbatim, team-lead files). No SPEC amendment here: a pre-registration is
a registration, not law; the layer's law comes after adjudication.

## D1 ($0) — the reader prompt, registered

`reader_thread_gm4` in the prompts registry, own sha, registered BEFORE any serving exists. Build
it from the design authority, not from taste:

- Frame: the seven PRODUCT.md questions — a signal is only what answers one of them.
- Duties IN ORDER (plan §2 C): (1) what is this thread about — the post sets the topic; (2) for
  EVERY watchlist name present: resolve the entity from context, one phrase + quote (наш
  молочный бренд / сеть-ритейлер / категория-личное / не наш рынок); (3) only then signals.
- Taxonomy words exactly as ratified 15.08 (see REFERENCE header). The reader may propose a NEW
  signal_type only with an explicit `proposed: true` flag.
- Output: STRICT JSON per plan §3 (thread block, signals[] with evidence msg_ids + quotes,
  per_comment[], noise[]), UA strings, no free prose outside fields. `parse_reply` reads the first
  brace — extend it for the new task the same single-parser way (`prompts.py`), never a second parser.
- Input rendering: the full thread — post text + every payable comment with its msg_id, the SAME
  reading path as everything else (`window_summary_5c2` readers). Register a token ceiling for
  output (pick from the longest reference thread, state it; the 64-comment giveaways died at the
  gate, but assert an input-size guard with a LOUD refusal rather than silent truncation).

## D2 ($0) — the gold, structured from the reference

`results/reader_gold_w1.json` built from `docs/REFERENCE-signals-w1.md` WITHOUT reinterpretation:
five flagship signal sets (F1–F5), four entity cases (E1–E4), the noise-zero thread list (N), the
secondary list (S, non-gating), and the per-comment gold rows — ONLY the msg-ids the reference
names explicitly. A test holds every gold row to a quote actually present in the evidence store
(the reference could carry a typo; the store is the truth). Team-lead file stays untouched.

## D3 ($0) — the pre-registration, committed BEFORE any serving exists

`results/prereg_reader_probe.json`: population = the census cell narrow|silencers_on — **111
threads**, pinned by `results/gate_census_w1.json`'s sha; instruments = `reader_thread_gm4` sha +
serving config; bars, one attempt, no retry:

1. flagships **5/5** found (signal_type may differ in word, the finding must be there — scorer
   matches on subject+aspect+evidence overlap, spelled out in the prereg);
2. entity cases **4/4**;
3. noise: **0** signals out of N-threads;
4. per-comment agreement (subject_type + stance vs gold rows) **≥ 0.80**;
5. time: seconds-per-thread from the warm-up; registered projection for a full window **≤ 30 min
   billed**; and the probe's own cap **$0.20** all-in.

Go/no-go (the (10)(a) pattern): warm-up = 2–3 threads drawn from the population's MIDDLE by seed
(never the head — a registered price names its sample), full pipeline, real JSON back. If projected
cost > remaining cap OR projected window time > 30 min → **STOP before any further call**: the
attempt is intact, the measured rate returns to the operator. A failed BAR after a completed run
closes the question by design review, never by silent retry.

## D4 — serving (the paid part, only after D1–D3 are committed)

- Base GM4 NF4, **adapter OFF and asserted** (the reader is a new capability; the classification
  adapter stays out), `enable_thinking=False` explicit — a thinking-ON reader would be a NEW
  pre-registration, not a knob; batch 1; greedy.
- A NEW serving template for the READER config — `settings()` refuses config-mixing by design
  (runbook_vis_b §A.1 pattern); NEVER edit the srv-2d or CAPTION templates.
- `scripts/preflight_serving_guards.py` on real transformers BEFORE the endpoint exists ($0 —
  the house integration-preflight rule).
- Endpoint created only after the prereg commit; deleted at session end with a positive-controlled
  listing. RECOVERY clause: after a PROVEN deletion, the endpoint may be recreated within the same
  cap — never two billing endpoints concurrently (the goal, not just the letter).
- Every reply persisted raw (`results/reader_probe_w1.jsonl`: rendering sha, raw reply, timings,
  spend) — the sitting is unbuildable without per-row evidence (the 4.5h2 lesson).

## D5 — the run and the score

Warm-up → go/no-go → all 111 threads → scorer computes the five bars from
`results/reader_probe_w1.jsonl` vs `results/reader_gold_w1.json` → `results/reader_probe_verdict.json`
(numbers only through the scorer; the report points at paths). Also carried, non-gating: how many
of the 111 the reader marked signal-bearing vs «нет сигнала» (my hand count was ~12 of 51 — the
precision claim of the wide-gate design, measured for the first time).

## DO NOT

- No SPEC edits, no re-pin, sealed anchors untouched; `data/loop_cursor.json`, `data/raw`,
  collection — untouched; no adapter merge; no batch >1; no OpenRouter (the probe prices OUR
  serving); never `git add -A`.
- The prereg, prompt sha and gold are FROZEN the moment the endpoint exists — a defect found after
  that is a finding in the report, never an edit.
- Do not exceed $0.20 all-in; the endpoint dies before the session ends, listing-proven.

## Autonomy

Prompt wording free within D1's frame; scorer matching rules free but SPELLED OUT in the prereg
before the run; anything the prereg did not anticipate → STOP and report, attempt intact.

## Verify (evidence, not assertions)

`make check` green (baseline 2 438/2 — expect growth); prereg committed BEFORE endpoint creation
(git order shown); warm-up numbers (s/thread, projected cost and time) pasted; the five bars from
the verdict file; spend from the guard, not from memory; deletion listing with positive control.

## Report

`docs/reports/probe-a.md`, commit `docs(report): probe-a`; chat gets ONLY the path. Deviations
Dv378+, cause tags; Process signals ≤5. End with `/save`.

## Read-back first (one line each, before any edit)

1. The order of D1–D4 — what must exist before the endpoint may?
2. The go/no-go: what is measured, against which two ceilings, and what does a stop cost?
3. Which model configuration reads — and which two things are OFF and asserted?
4. What may change after the endpoint exists? (expected answer: nothing but the report)
