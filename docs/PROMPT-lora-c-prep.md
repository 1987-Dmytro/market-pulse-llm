# PROMPT — lora-c-prep: data and registration for the rationale-supervised LoRA line (all $0; two team-lead review gates inside)

**Fresh executor session. Authority:** the operator's rulings of 2026-08-22 in the team-lead
session, `docs/STATUS.md` «Открытые решения» п. 1 (в) and (к): *the next line is a LoRA on
pass 1 supervised by RATIONALE → label, on top of prompt v2, with synthetic data as arm B;
prompt v3 = v2 + a `rationale` field BEFORE the label, one rendering for training and
inference; rationales written by Claude Code from the codebook and the team lead's label,
reviewed by the team lead; holdout-100 and every row of the 16 reference threads excluded from
training AND from the neighbour pool; bar per arm: holdout ≥ 64 AND end-to-end bar 1 = 5/5 AND
bar 3 = 0.* Read: this file → `docs/reports/pass2-signals-r2.md` §«What returns to the
operator» (the four error classes this line targets) → `docs/reports/lora-b-run.md` §13 and
`knowledge/decisions/lora-b-red-and-line-b-closes.md` (why label-only supervision learned the
prior) → `results/prereg_lora_b.json` (the training shape to inherit) → `docs/PROMPT-pass1-
fewshot.md` §neighbours (the v2 rendering). **Nothing in this contract costs money; nothing
creates a pod.** Deviations from **Dv728**, enum v2 `[cause: …]` + `[[lesson]]`; five-line
Process signals; team-lead files verbatim (commit `docs/STATUS.md` and this file first); never
`git add -A`.

## What this line IS (state your assumptions against it)

- **The question:** does rationale-supervised QLoRA on pass 1 fix the subject-attribution
  errors pass 2 measured — brand ↔ retailer (F2: `580124`), a retailer mentioned in a
  non-dairy context (N2: `@VARUS_channel:10366`, four rows pass 1 called `сеть_ритейлер`; the
  team lead's labels on all 12 rows are `null`), non-dairy «brands» (café, stationery, throat
  spray → `молочный_бренд`), and mention-vs-about (18 of 52 `не_наш_рынок` rows on holdout-100
  pulled into `категория_личное`) — without learning the prior the way line B did.
- **Prompt v3 = prompt v2 + a rationale clause,** in a NEW module `src/market_pulse/pass1_v3.py`
  (`prompts.py` is pinned by 38 records): the reply is ONE JSON object `{"rationale": one
  sentence — what the comment is ABOUT versus what it merely MENTIONS, naming the deciding
  cue; "msg_id"; "subject_type"; "subject_id"; "stance"}` — `rationale` FIRST, so the label is
  conditioned on it. The v2 text is IMPORTED (`prompts.PASS1_COMMENT_PROMPT_V2`, task
  `pass1_comment_gm4_v2`) and extended, never retyped; the parser wraps `prompts.parse_pass1`'s
  validators and treats `rationale` as REPORT-ONLY (it can never refuse — the pass2-r2 rule).
  The five neighbours come from `build_pass1_fewshot_packs.py::neighbours` (the same Jaccard
  rule, over the shared pool); the v3 rendering is pass1_v3's own renderer calling the same
  pieces `::rendered_item` calls — `rendered_item` dispatches on a task name `prompts.py`
  does not know, so say whether it can take v3 or why a sibling renderer is needed BEFORE
  writing one. Neighbour examples carry their rationale too, so the model sees the shape it
  is asked to produce.
- **One rendering for training and inference** (`[[build_the_training_prompt_with_the_
  inference_call]]`): the SFT row's prompt is the v3 inference request for that comment,
  byte for byte; the target is the reply object. The mask sits on the target only
  (`build_pass1_sft.py::target_for`'s END-offset rule — import it, do not copy).
- **The neighbour POOL is one pool for every leg:** labels MINUS holdout-100 MINUS every row
  of the 16 reference threads (derive the 16 from `results/reader_gold_w1_r2.json` flagships +
  entity_cases + noise_threads; 8 of them carry labelled rows — name the count). Base v2, base
  v3, arm A and arm B are all rendered against this pool, so the paired table compares prompts
  and adapters, never neighbours. The window's v2 numbers were measured on the FULL pool and
  are therefore report-only context here; base v2 is RE-MEASURED on the eval set in
  `lora-c-run`.
- **Four legs, paired on identical instances:** base v2 · base v3 (the rationale clause
  alone — no adapter) · arm A (QLoRA on real rows with rationales) · arm B (arm A's rows +
  synthetic). Without the base-v3 column nothing separates «the adapter learned» from «a
  sentence of reasoning helped».

## D0 — the training set (`results/pass1_sft_v3_train.jsonl`) and the rationales

1. **Rows:** the 650 labels (`results/labels_pass1_r1.jsonl` + `_r2.jsonl`, keyed by the pair)
   MINUS holdout-100 (`results/pass1_holdout_100.json`; `build_pass1_sft.py` already refuses a
   set containing one) MINUS every row whose thread is one of the 16 reference threads. Print
   the count and the class distribution (expect ~430 rows, ~7 % «our»); the record carries
   both. Class balance for training: inherit lora-b's weighting rule from
   `results/prereg_lora_b.json` and ALSO cap the majority class by sampling so no class is
   under 8 rows per epoch-equivalent — say which rule you applied, in the record, with the
   resulting per-class counts.
2. **Rationales — written by YOU (Claude Code), one per training row**, from the codebook
   (`build_pass1_label_pack.py::codebook()` — the labeller's own text, law v5+F2a+r2) and
   the team lead's label, in Ukrainian, one sentence, ≤ 160 characters, naming the deciding cue:
   «коментар ПРО X (cue)» or «лише ЗГАДУЄ X; насправді про Y (cue)». Provenance in every row:
   `rationale_author: "claude-code"`, `rationale_reviewed: false` until the gate below.
   Written to `results/rationales_pass1_v1.jsonl` (pair key, label, rationale, text).
3. **Team-lead review gate 1 (STOP until cleared):** write
   `docs/reviews/lora-c-rationales-sample.md` — EVERY «our» row (категория_личное +
   молочный_бренд, ~43) and 40 boundary rows drawn under a recorded seed from
   `не_наш_рынок`/`сеть_ритейлер`/`null` rows whose text mentions a retailer or brand name
   (`brands.py` / the watchlist matcher — name the instrument), each with text · label ·
   rationale · a blank verdict column. The team lead writes
   `docs/reviews/lora-c-rationales-verdict.md` (a TEAM-LEAD file: read, never edit) naming rows
   to rewrite and the pattern behind each; you rewrite ONLY the named rows and every other row
   matching the named pattern, set `rationale_reviewed` accordingly, and record the counts.
   Until that verdict file exists, D0 stops here and the report says so.

## D0 — synthetic rows for arm B (`results/synthetic_pass1_v1.jsonl`)

- **~160 comments, 40 per error class** (brand ↔ retailer · retailer in a non-dairy context ·
  non-dairy «brand» that must be `не_наш_рынок` · mention-vs-about), written by YOU in the
  register of the window's comments (Ukrainian/Russian mix, short, colloquial — read 30 real
  rows first and say what you matched), each with label, `subject_id`, `stance`, rationale,
  and a synthetic `thread` id that can never collide with a real one (prefix `synthetic:`).
  Balanced ACROSS classes so synthetic cannot teach a prior: per class, label counts within
  ±2. Provenance: `synthetic: true`, `author: "claude-code"`, the error class, the seed.
- **Contamination, printed as empty lists:** no synthetic text shares a 6-gram with any
  labelled row, any holdout row, any reference-thread comment, or the gold; synthetic rows are
  NEVER in the neighbour pool, never in any eval set, never in arm A.
- **Team-lead review gate 2:** `docs/reviews/lora-c-synthetic.md` — all ~160 rows with a blank
  verdict column; the team lead's `docs/reviews/lora-c-synthetic-verdict.md` names rows to
  drop or rewrite; you apply ONLY those. STOP until it exists.

## D0 — eval packs ($0 now, bought in `lora-c-run`)

- **Eval set E (pass 1):** holdout-100 + every payable comment of the 16 reference threads
  (from `gate_census_w1_reader.population()`; count them — expect ~100–120) — rendered under
  v2 AND v3 against the shared pool, as ONE pack with two legs per prompt family the way
  `pass1_dev_pack.json` carries `base`/`v2`: `results/lora_c_eval_pack.json`. The gold-14 rows
  are inside the reference threads: they are answered as part of E and scored as a
  REPORT-ONLY census row (the SIXTH look; say so in the record). dev-200 is NOT in E: it is
  training data now (its «our» rows are the training set's «our» rows), and its agreement is
  reported as training FIT only.
- **Eval set for pass 2:** the pass-2 r2 machinery (`pass2_r2.py`, `scripts/build_pass2_r2_
  pack.py`'s unit shape, the strict-authority parser, `score_pass2_signals_r2.py`'s bars)
  over the reference threads ONLY, built per leg from that leg's pass-1 out-file through
  `census_pass1_window.pass_2_filter` — bars 1 and 3 are what they score; bar 2 is inherited
  and reported «held». A builder `scripts/build_lora_c_pass2_pack.py` that takes a pass-1
  out-file path and emits the pass-2 pack for these threads, driven at $0 on the EXISTING
  window out-files (it must reproduce r2's 4/5 · RED(2) on them — that is its test).
- **The bar, registered per arm, one attempt, all-or-RED:** holdout-100 agreement ≥ 64 (base v2
  on the window pool read 64/100; the RE-MEASURED base v2 on the shared pool is the «before»
  column, and the bar is the registered 64 regardless) AND bar 1 = 5 of 5 AND bar 3 = 0.
  Report-only: the `не_наш_рынок → категория_личное` cell on holdout (18 before), «our» on
  holdout (6/8), dev-200 fit, the gold-14 row, the per-class tables, the DROP/doubt tables of
  pass 2, and the arm-A-vs-arm-B ablation on the same instruments. Base v3 takes no bar — it
  is a control column.

## D0 — the registration draft and what `lora-c-run` will price

- `scripts/write_lora_c_prereg.py` → `results/prereg_lora_c.json` (DRAFT — frozen only by
  `lora-c-run`'s first `pod create`): population (train rows, synthetic rows, pool, E, the
  reference threads), the four legs, the bars above, instruments pinned (pass1_v3.py, the
  packs, the rationale and synthetic files with their review states, `train_qlora.py`,
  `config/qlora.yaml`, the pass-2 r2 instruments, the gold), the training shape inherited by
  name from lora-b (rank, lr, steps-per-row at the MEASURED 61.047 s/step and the 121 s/step
  worst — both, from `results/prereg_lora_b.json`), and a money block LEFT OPEN: seconds per
  leg as FORMULAS of the measured rates (eval calls × the stack's worst pass-1 rate 6.14
  s/call; pass-2 calls × 97 s/thread; training steps × 121 s/step), the cap the ruling set
  ($4.00) and the hard stop to be derived in `lora-c-run`'s contract — do NOT register a
  price here; a number without a run behind it is what r1 of pass1-window taught.
- Tests, both directions: the training set contains no holdout row and no reference-thread
  row (a planted one is refused); the pool contains none either; a synthetic row in the pool
  or in E is refused; the SFT prompt of a row equals its v3 inference rendering byte for
  byte; the rationale field can never refuse a reply; the pass-2 builder reproduces r2's bars
  on the window out-files; every gate COMMAND you add is driven end to end.
- `make check` green; `make preflight ARGS='pass1_v3.py prereg_lora_c.json'` pasted; five-lens
  review on a COMMITTED tree with a second skeptic pass on the fixes (pass2-r2's
  construction); ADR `lora-c-rationale-supervision-and-the-shared-pool` + INDEX quoting
  rulings (в)/(к) verbatim and the review gates' outcomes. Report `docs/reports/lora-c-prep.md`
  — with a **ready-to-price table** for `lora-c-run`: rows, calls per leg, steps per arm,
  tokens per SFT row (median/max), all from the files.

## Read back FIRST, one line each

the four error classes and where each was measured · what v3 adds and where it lives · the
shared pool and what it excludes · the four legs and why base v3 exists · who writes
rationales, who reviews, and what STOPS until the verdict file exists · what synthetic may
never touch · the bar per arm and the report-only rows · why the money block stays open.

## DO NOT

No pod, no endpoint, no paid call of any kind; no edit to `prompts.py`, `scorer.py`,
`build_pass1_sft.py`, the labels, the holdout, the gold, the reference, or any pinned file;
no rationale rewritten outside the team lead's named rows and patterns; no synthetic row in
the pool, in E, or in arm A; no price registered; team-lead files verbatim (docs/STATUS.md,
docs/SPEC.md, docs/PROMPT-*.md, docs/reviews/lora-c-*-verdict.md) — commit, never edit.
