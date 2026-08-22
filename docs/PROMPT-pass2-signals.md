# PROMPT — pass2-signals: signal assembly over the bought window, scored by the reader's own bars (D0 $0 → D1 paid: smoke then full, cap $1.50 → D2 $0)

**Fresh executor session. Authority:** the operator's rulings of 2026-08-21/22 registered in
`docs/STATUS.md` («Открытые решения» п. 1 (г), (д), (ж)): pass 2 = ONE call per thread over
the comments pass 1 labelled `категория_личное` / `молочный_бренд` / `сеть_ритейлер`; output in
the v5 reader's schema, scored by the reader's existing scorer against the reader's gold r2;
STRICT authority (pass 2 never relabels a subject; it may DROP a comment as noise; a report-only
`subject_doubt` records disagreement); input = filtered comments + the post + the entity block,
never the raw unfiltered comments; the reference's bar as written; the smoke on the five F
threads FIRST; cap **$1.50**. Read: this file → `docs/REFERENCE-signals-w1.md` (the bar's
text) → `knowledge/decisions/v2-is-the-base-and-pass-2-is-not-a-one-shot-reader.md` (what pass 2
may not be) → `results/pass1_window_r2_census.json` `pass_2_filter.per_thread` (the population)
→ `docs/PROMPT-pass1-window-r2.md` §«kill-clock» (the rungs this inherits). Deviations from
**Dv680**, enum v2; five-line Process signals; team-lead files verbatim (commit `docs/STATUS.md`
and this file first); never `git add -A`.

## What pass 2 is (state your assumptions against it)

- **Population:** the 79 threads with ≥ 1 filtered row (281 rows, 32 756 chars) — derived by
  CALLING the census's filter over the UNION out-files `results/pass1_window_v2.jsonl` +
  `results/pass1_window_r2_v2.jsonl` against `results/pass1_window_pack.json`, keyed by the PAIR
  (thread, msg_id), never typed. The 48 callable threads with no filtered row are NOT called
  and are listed as «no signal by construction». One unit = one thread.
- **Input per unit:** the post text (`build_pass1_label_pack_r2.raw_threads()` — the store the
  pass-1 pack was rendered from), the thread's entity block (`build_pass1_sft.verdicts()` /
  `envelope()` — the bought v5b/v4/topup verdicts, nothing re-purchased; may be empty, e.g.
  `@mandziak:3703`), and the filtered comments with their pass-1 fields `subject_type ·
  subject_id · stance` beside each text. Raw unfiltered comments are NOT rendered — the
  measurement is of the filter. Widest unit: 26 rows (`@klopotenkofood:6040`), 4 315 chars
  (`@mandziak:3679`); the 12 000-char ceiling and the reader's 4 000-char output ceiling apply.
- **Output = the reader's lists**, so the reader's parser and scorer apply unchanged:
  `signals` (`signal_type` ∈ `prompts.READER_SIGNAL_TYPES`, `subject_type` ∈
  `READER_SUBJECT_TYPES` — the reader's «категория» ≡ pass 1's «категория_личное», collapse via
  `score_reader_probe_b.collapse`; `subject_id`; `aspect`; `evidence` msg_ids; `quote`),
  `entities` (the entity block PASSED THROUGH, never re-resolved), `per_comment` (pass 1's
  labels PASSED THROUGH for the filtered rows — strict authority), `noise` (the filtered
  comments pass 2 DROPS, each with a class from `READER_NOISE_CLASSES` or «не_сигнал»). Plus
  ONE new report-only field per comment: `subject_doubt: true/false` with a one-line reason —
  it changes nothing downstream; it is the FP/FN reading the ruling (б) asked for.
- **Strict authority, verified by the parser:** every `subject_type` in `signals` and
  `per_comment` equals the pass-1 label of the evidence row it cites — a reply that relabels is
  a parse REFUSAL counted by cause, never silently accepted. This is the ADR's line and the
  test that holds it is the first test of D0.
- **The prompt is NEW and lives in a NEW module** (`src/market_pulse/pass2.py`, task
  `pass2_thread_gm4_v1`): `src/market_pulse/prompts.py` is pinned by 38 sealed records and is
  never edited; import `READER_SIGNAL_TYPES`, `READER_SUBJECT_TYPES`, `READER_NOISE_CLASSES`
  and the reader parser (`prompts._reader_object` / `parse_reply` — name which) from it.
  `scripts/reader_v5_pod_runner.py` takes a duck-typed `prompts` object exposing
  `reader_messages_gm4(channel, post_id, post, comments, task=, part=)`; if the pass-2 module
  can satisfy that interface with labelled comments, reuse the runner unchanged; if not, a
  sibling runner — say which, and why, BEFORE writing it.

## Bars — the reference's, through the reader's scorer (`score_reader_probe_b.py::flagships`, `::entity_cases`, `scorer.reader_noise_count`), gold `results/reader_gold_w1_r2.json`

- **Bar 1 — flagships F1–F5, 5 of 5, every named signal** (F1 carries three): signal_type +
  subject (collapsed) + at least one named evidence msg_id. All or nothing, as the reference
  says. **Registered EXPECTATION, written into the record:** F2 is expected RED by
  construction — pass 1 labelled `580124` `сеть_ритейлер` and strict authority forbids the
  brand; F5's `579457` is outside the filter (`579379` is inside). The bar is NOT moved for
  that; the expectation is named so the RED reads as the measurement it is.
- **Bar 2 — entity cases E1–E4:** INHERITED through the pass-through `entities` list; scored,
  reported as «held», never claimed as pass 2's own.
- **Bar 3 — noise: zero signals from the reference's N threads** (N1 `@VARUS_channel:10529` is
  excluded with cause by the scorer as r1 registered it; `@VARUS_channel:10366` carries FOUR
  filtered rows labelled `сеть_ритейлер` — pass 2 must DROP them; the retsepty scam threads
  carry no filtered row and are «no signal by construction»).
- **Bar 4 (per-comment agreement on the fourteen) is NOT registered** — `per_comment` is pass
  1's pass-through, so it would be the SIXTH look at the fourteen through a bar. Report-only,
  captioned, multiplicity named.
- **The answer of the contract, beside the bars (pre-registered tables, D2):** per-flagship
  scorecard (found / missing / why, citing the pass-1 label of the named row); the DROP table
  (filtered rows pass 2 sent to `noise`, by thread and by pass-1 label — the FP reading);
  `subject_doubt` rate by pass-1 label; the comparison row **v5b one-shot reader bar-1 2/5 ·
  bar-2 4/4 vs pass 2** on the same gold and scorer (`results/reader_v5b_verdict.json`); the
  bought cost of the whole signal layer (pass 1 $0.742 + this step) beside v5b's.

## Money — the H6 block, with the rate MEASURED by the smoke, not assumed

- **This prompt has no rate.** Pass-1 replies were ~50 tokens; a pass-2 reply is a list of
  signals, ~300–600 tokens, and nothing on this stack has measured that decode. So the
  registration prices the SMOKE at an assumed ceiling and the FULL run from the smoke's own
  reading, on the same pod, with a go/no-go rung in between.
- **Smoke (rung S):** the five F threads (`@VARUS_channel:10613`, `@matusi_ukr:22303`,
  `@mandziak:3676`, `@mandziak:3703`, `@matusi_ukr:22272`), charged **120 s/call** (a 600-token
  reply at a 5 tok/s worst decode + prefill; name it as an ASSUMPTION, the only one in the
  block) = 600 s. Pre-generation charged as r2 charged it: ssh 500 + stage/launch 150 + load 450
  = 1 100 (backstop 1 100 from create; rung 3 on `launched_at`). Overhead 1 300. **Smoke worst
  = 3 000 s = $0.6667 at $0.80/h.**
- **Go/no-go after the smoke (rung S′, the gate computes it from the smoke's out-file):**
  `charged_full = max(1.5 × smoke_mean, smoke_max)` s/call — same pod, so the spread charged is
  the CALL-LENGTH spread, not the pod-class spread; `projected = create_elapsed_now + 74 ×
  charged_full + 1 300`. **GO** if `projected ≤ hard stop 6 600 s`; else **STOP**: the five
  F-thread replies are scored (bars 1/3 on the five, the scorecard) and the question returns to
  the operator with the measured rate — no full run at a price the record did not register.
  Worked arm, in the record: the full run fits iff `charged_full ≤ (6 600 − 1 300 − 1 100 −
  smoke_seconds) / 74`; at a 600 s smoke that is **48.6 s/call**.
- **Cap $1.50; cumulative hard stop 6 600 s = $1.4667 < $1.50; session ceiling 6 750 s.**
  `--terminate-after` = create + 6 600 (tolerance 60 s from the record). Rung 4 (projection at
  max(mean, last call) on every poll against 6 600 and $1.50) runs from the first reply and
  covers the full run exactly as it did in r2; rung 5 liveness 600 s from the last event —
  **a pass-2 call may take minutes, so the liveness event is the pod LOG line the runner
  prints per call, not only a new out-file row** (the v5 runner prints one; assert it).
- **Recovery:** one re-creation after a proven deletion, allowed ONLY for a death BEFORE the
  smoke's first reply (rungs 1–3: ssh, boot); after the first reply a KILL closes the session
  — the smoke replies on the Mac are the evidence, and the remainder is a new registration.
  Widest dead pod that still fits: 6 600 − 3 000 − (74 × charged_full) — computed live, never
  typed; H6 carries the inequalities at the 120 s arm.

## D0 — at $0, before any pod

- `src/market_pulse/pass2.py` (prompt v1 + renderer + the strict-authority parser wrapper);
  `scripts/build_pass2_pack.py` → `results/pass2_pack.json` (79 units in `channel:post_id`
  order, the five F threads FIRST as the smoke leg, each unit carrying `rendering_sha256`, its
  filtered rows with pass-1 fields, the entity block, membership flags F/E/N); length check
  against both ceilings; contamination: the pack carries NO labels and NO gold — the pod sees
  pass-1's fields only.
- `scripts/write_pass2_prereg.py` → `results/prereg_pass2_signals.json` (bars 1/2/3 + the
  expectation on F2/F5 + the report-only tables named; kill-clock by name incl. rungs S/S′;
  money with H6 rows; `instruments` pins: pass2.py, the pack builder, the gate, the scorer, the
  runner it uses, the gold `reader_gold_w1_r2.json`, the two pass-1 out-files, the census);
  `scripts/gate_pass2_signals.py` (the window gate's rungs by the Dv663 construction or a
  sibling — say which — plus rungs S/S′); `scripts/score_pass2_signals.py` = the reader scorer
  IMPORTED over pass 2's out-file, writing `results/pass2_signals_verdict.json` with the v5b
  comparison row; `scripts/runbook_pass2_signals.md`.
- Tests, both directions, on a fake transport: a reply that relabels a subject → REFUSED by
  cause; a DROP lands in `noise` and removes nothing from `per_comment`; the smoke leg is
  exactly the five F threads; rung S′ GO at 30 s/call and STOP at 60 s/call on a 600 s smoke;
  rung 5 fires on a log that stops, not only on a file that stops; bar 1 on a synthetic reply
  that carries F1's three signals → found, minus one → RED; N-thread 10366 with a signal → bar 3
  RED; the deadlines of every rung read by KEY, not by `first_number` over prose (Dv669).
- **ADR `pass-2-in-the-readers-schema-and-strict-authority`** + INDEX: rulings (г)/(ж) quoted
  verbatim, the expectation on F2 registered, the sixth-look rule on the fourteen.
- `make check` green; `make preflight ARGS='pass2.py prereg_pass2_signals.json'` pasted;
  five-lens review before the create, mutations watched red; `--pre-create-check` GO pasted and
  RECORDED. Commits: pass2 module + tests · pack builder + pack · producer + record + gate +
  scorer + tests · runbook · ADR · guard anchor (`pass2-signals`, `--step-cap 1.50`) · vault
  tail — ALL before the first `pod create`.

## D1 / D2

D1: r2's runbook order with the smoke leg first, rung S′ on the Mac from the smoke's out-file
before the remaining 74 are launched (the runner waits for the go — name the mechanism), `--watch`
never left, scp + sha, deletion by listing with the volume control. D2: bars 1/2/3 through the
reader scorer; the scorecard, the DROP table, `subject_doubt` rates, the v5b comparison row, the
cost table; everything read from `results/pass2_signals_v1.jsonl` and the verdict; report
`docs/reports/pass2-signals.md`, path-only in chat.

## Read back FIRST, one line each

the population and who derives it · what pass 2 may and may not do to a pass-1 label · the four
output lists and the one new field · which bars are registered and which is NOT, and why · the
expectation on F2 and why the bar still stands · the smoke, rung S′'s formula, the hard stop ·
what a death after the first reply means · which file is never edited and where the prompt lives.

## DO NOT

No edit to `prompts.py`, `scorer.py`, the reader gold, any pinned file, the pass-1 out-files or
packs; no raw unfiltered comments in any request; no relabelling path, however named; no bar
on the fourteen; no full run without rung S′'s GO; no generation before H6 and the commits;
never leave `--watch`; never two billing endpoints CONCURRENTLY; no third pod; team-lead files
verbatim (docs/STATUS.md, docs/SPEC.md, docs/PROMPT-*.md) — commit them, never edit.
