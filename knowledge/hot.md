<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-08-02 22:01:32 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
91952ca docs: what 4.5f found — the gate, the three rulings, and the 97 emptied rows
25b14d2 feat: the 14 unreadable rows go to the operator with nothing proposed
c4e545e feat: the emptied rows measured — 97 of them, and 31% of the drift v2 cannot explain
dce2f26 feat: the three operator rulings are law — 11972, 11960 and 11902 read `taste`
826d08e feat: the calibration gate is computed — 100/100, and the rebuild proves the pack
```

## 📋 Recent decisions

- `taxonomy-v2-relabel-and-appetite.md` — Taxonomy v2: the up-label appetite, three boundary calls, and how the re-label is staged
- `INDEX.md` — Decision records
- `test-v3.md` — Test set v3: 38 blind verdicts applied, and what they do not reopen

## 📅 Recent daily logs

- `2026-08-02.md`
- `2026-08-01.md`
- `2026-07-31.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->

# Hot Cache — curated

**Last update:** 2026-08-02 21:56 (`/save` after `PROMPT-4.5f` — **the ≥90% calibration gate is DECIDED and it is PASS: 100 of 100 gated rows came back `correct`. The taxonomy-v2 re-label is accepted, three operator rulings are applied, and everything that was waiting on this gate is unblocked — none of it is started**. Test v3 is frozen beside v2; Phase 4 stays closed at 2 of 5 against v2; edited by hand — the section above is auto-generated, do NOT touch the marker)

## 🔥 What's Hot

**THE GATE IS DECIDED — 100/100 `correct` = 100% against 0.90, PASS (2026-08-02, 4.5f).** The
taxonomy-v2 re-label is **accepted**. Record: `results/calib_45e_verdict.json` — the pre-registered
rule verbatim, 150 per-row verdicts, both sets of shas. The number is not read off the returns: the
reader **rebuilds** the sealed pack (seed 42, staged rows, sample sizes taken from the manifest and
not from the builder's constants), serializes it in the builder's dialect and requires the result to
hash to the pinned `f26fb86c…` / `6192643a…` — only then are cells compared, because a spreadsheet
round-trip changes bytes and no rows. Unregistered verdict form → stop; `Old` and `old` are one
verdict by a case-folded table; a blank gated cell counts against the bar, as registered.
**The counter-signal stands beside the number, not under it:** the diagnostic 50 read **47 `new` /
2 `old` / 1 `neither`**, labelled in the record as unable to move the verdict.

**Three operator rulings are law and applied** (`dce2f26`): `@VARUS_channel:11972` and `:11960`
`[] → ["taste"]`, `:11902` `["availability"] → ["taste"]` — all three in
`comments_train_tax2.jsonl`, diff exactly three lines, intents column only. `old` is never retyped
into the ruling table: such a row reads its v1 label out of the **source** and the run stops if the
two disagree; the dictated one is carried by its `neither` cell plus the table, because a notes cell
is free text and is never validated. **The drift block of `results/relabel_45e.json` was NOT
recomputed and the diff proves it — 56 insertions, 0 deletions**; `fixes` sits beside `runs` with
each row, both values, the authority and the staged sha on either side.

**The emptied rows: 97, and they are a third of the drift the taxonomy cannot explain.** Non-empty
under v1 → `[]` under v2: **97 of 3,249** = 20.5% of the 473 unexplained; **96 of 2,059 scoreable** =
**30.9% of the 311**. Decomposition of "the 15%": 97 + 376 = 473, and 96 + 215 = 311. They are
short — median **18** chars vs 55 for the rest, p75 30 vs 109 — and the label they lost most is
`taste` (40 of 97). **The premise is measured, not cited:** `parent_msg_id`, `msg_id`, `channel` and
`date` are checked absent from the rendered prompt, and **all 3,249 re-labelled rows are replies**,
so the parent is missing corpus-wide and only bites where the comment alone carries no intent. The
three rulings are reversed before counting (`changed` 1474 / `changed_without_service` 473 come out
equal to the 4.5e record — the proof the reversal restored the model's own output). Record:
`results/drop_45f.json`, $0.

**The 14 unreadable rows are with the operator, with nothing proposed.**
`data/annotation/calib_45e/unreadable14.csv` + `README-unreadable14.md`, `;`-delimited,
**`intents_v2` blank** — 13 of the 14 carried `[]`, and pre-filling is the bias that left them
unlabelled. The set is derived twice (source minus staged minus frozen, against the paid runs'
unusable ids) and a disagreement stops the build. Pinned in a **new**
`results/calib_45e_micro_manifest.json`; the sealed manifest is never rewritten. ~6 min of operator
time, not gated.

**THE RE-LABEL ITSELF (2026-08-02, 4.5e) — accepted by the gate above.** 3,317 rows in three files →
54 frozen holdout ids skipped → **3,249 staged** in `_tax2`
copies beside their sources (`data/frozen/comments_train_tax2.jsonl`,
`data/annotation/sarcasm_candidates_tax2.jsonl`, `sarcasm_holdout_pool_tax2.jsonl`); originals byte
for byte untouched. 3,263 labelable + 508 frozen = **3,771**, the figure 4.5d priced — that equality
is what proves the file list complete. **$0.5448 of $1.50** against `results/spend_45e.json`,
anchored before the first request. Record: `results/relabel_45e.json`. ADR:
[[taxonomy-v2-relabel-and-appetite]] (`accepted`).

**Drift, over the rows a gate scores (n=2,059): 49% of intent sets changed, 34% carry `service`,
15% changed WITHOUT gaining it.** Over all 3,249: 45% / 31% / 15%; over `unclear` (n=1,190): 38% /
25% / 14%. **The probe's n=25 (64 / 40 / 24) is superseded** — it was a scoping figure and this is
the measurement. The churn matrix (`drift.churn`) says where it came from: `price` loses 184 rows,
166 of them now carry `service`; `availability` gains 166 and **149 of those were `[]`** — drift no
taxonomy rule explains, and the only instrument for it is the calibration. Cells count (old → new)
pairs, so they do not sum to the margins; read totals off `before/after/kept/lost/gained`.

**14 rows have no v2 label, and 13 of them carried `[]` under v1.** All are
`parse: missing field: intents` — the model's `{}` answer, which the parser refuses. `--resume`
re-asked exactly the failing ids: **66 → 29 → 18 → 14** over four passes for $0.017, and the ids
repeat between passes, so the residual is the model, not the transport. Not coerced to `[]`: the
hole sits in the very class the taxonomy question is about, and filling it would have handed the
model the answer it declined to give.

**The pack: `data/annotation/calib_45e/` (gitignored), manifest `results/calib_45e_manifest.json`
with every sha.** `gated.csv` — 100 scoreable rows, `correct`/`incorrect`, **this is the gate**;
`changed.csv` — 50 changed rows with old beside new, `old`/`new`/`neither`, diagnostic only and it
cannot move the verdict. Disjoint by construction. Two things fixed **before** any verdict exists:
the denominator (`correct` / 100, a blank cell counting against the bar), worded identically in the
README and the manifest; and blinding — no column and no ordering reveals which rows moved. ~1.0 h.
**Returned, read and decided in 4.5f** — the three files are committed as they came back
(`git add -f`, the pack directory is gitignored) because they are now the authority a gate was
computed from.

**TAXONOMY v2 WAS PREPARED AND PRICED IN 4.5d — the gate then decided the appetite.** The law
question closed by interview, not by the pack: **amendment 3.8** keeps the old law where it was
challenged (17 of the 19 disputed `[]` rows stand; the "22 of 40" reading was a pack-design
artifact — intents were shown without sentiment and sarcasm) and adds a **sixth intent `service`**
with the WIDE boundary: in-store and online service, the delivery *process*, app/checkout, hotline,
staff, and how promos and giveaways are organised. `availability` keeps the *product*;
co-occurrence is allowed. Everything is in `docs/taxonomy-v2-prep.md` and `docs/annotation/comments.md`
(guideline v2, changelog at the top).

**The one trap, and it is load-bearing:** `records.assert_prompt_sha` builds its map out of
`prompts.TASKS` and compares whole maps, so registering `T1v2` **there** would have made every
recorded run fail to verify. `TASKS` stays `("T1","T2")`; `T1_PROMPT_V2` and
`RELABEL_INTENTS_PROMPT` live in `PROMPTS`/`DELIMITERS`, the label space is routed by task
(`prompts.INTENTS_OF`), and `scorer.INTENTS` stays at **five** members — `run_baseline.py` and
`train_xlmr_baseline.py` build one classifier per member. `INTENTS_V2` is a new constant.

**The probe: 50 train rows, `qwen3.6-27b` at the pinned fp8 endpoint, $0.0081.** Model chosen on
the only measurement that exists for the job — intents micro-F1 vs human gold in 3b: **0.768** here
vs 0.774 (haiku) vs 0.798 (gemma, i.e. the model under test, whose labels would make part of G1c
agreement with itself). Its scoreable half was n=25 and its rates (64 / 40 / 24) are **superseded by
the 4.5e full pass** above; what stands is the per-row cost, **$0.000162**, which the 3,263-row pass
reproduced at $0.000165. Ledger: `results/spend_45d.json`, **$0.0187 of $2.00** — a closed phase's
anchor, never written again.

**THE CORPUS IS THE BINDING CONSTRAINT, not money or hours.** After the two exclusions that decide
the count — 3,771 rows already labelled across five files, 1,239 rows in threads that carry a test
or holdout row — **1,912 rows are labelable**. Of them 382 are service-rich by keyword and
**ZERO are sarcasm candidates**: the highest irony score anywhere in the remaining pool is 1.
**No appetite tier is reachable**: +2k is 88 rows short (~2 weeks of collection at ~443 labelable
rows/month), +5k ~7 months, +9k ~16 months or a new source — and only two registry channels have
comments enabled at all. Calibration hours do **not** scale with the tier (0.7 h re-label, 2.0 h
up-label at any size); what a bigger tier buys is risk, not review. **The gate took all 1,912** —
de facto +2k without waiting — **strictly after** the re-label passes ≥90%, and ratified the three
boundary calls in guideline v2 as written.

**Two probe details worth not relearning:** `{}` is a model's way of saying "no intents" and the
parser refuses it (6% of rows lost until the prompt demanded the key explicitly — both runs are in
`results/relabel_probe_45d.json` under their own prompt hashes); and the `unclear` split was
**re-derived from the rows the paid run wrote** (`relabel_intents.py --from-rows`), because greedy
is not deterministic across a provider's batches and a re-run would be a second measurement.

**TEST v3 EXISTS, BESIDE v2 — 38 point fixes from the blind audit (2026-08-02).** Three new files:
`data/frozen/comments_test_v3.jsonl` (400 rows, 15 changed) · `sarcasm_holdout_v3.jsonl` (108, 15) ·
`posts_test_v3.jsonl` (250, 7). **v2 is untouched and immutable forever**, every published number
keeps its version, and **Phase 4's verdict (2 of 5) is a v2 result that v3 does not reopen** —
`results/rescores_v3.json` is a separate, append-only file and `results/baselines.json` was not
written. Rulings: sentiment 15 · G1b pair 15 · post_type 5 · brands 3, the split gate 4.5
pre-registered and `scripts/freeze_testsets_v3.py` refuses to deviate from. **`intents` in v3 is
byte-identical to v2** — 31 rulings derived, none applied, pending the law review. Record:
`results/frozen_v3.json`; changelog: `docs/frozen-testsets.md`; ADR: [[test-v3]] (`proposed`).

**What the same predictions score against corrected gold** (v2 → v3, program measurements, never
gate results): **arm A G1a 0.9107 → 0.9499** · G1d 0.9386 → **0.9705** · G1e 0.9333 → **0.9744** ·
**G1b on the pre-registered 44-id slice 21/44 → 36/44**. Arm B: G1a 0.9172 → 0.9456, G1e 0.9577 →
**0.9189**, G1b 24/44 → 29/44. Base: G1a 0.8918 → 0.9067, G1e 0.8974 → 0.9383. G1c and relevance are
unchanged to the last decimal — the cheapest proof that `intents` and `relevant` were not touched.
**Two G1b readings, and neither is *the* fix-rate:** the pre-registered 44 ids re-scored vs v3
(comparable with the verdict row) and the base model's error union recomputed vs v3 — **29 ids**,
because 15 of its 44 "errors" were gold's. `python3 scripts/show_results.py --gold v3` renders it.

**The fixes came out of arm A's dump**, so arm A's v3 column is not independent of v3 the way arm
B's is. On G1e the sign is visible on three rows: A rises, B falls.

**The intents law pack did its job and is now history.** `data/annotation/audit_45a/`
`intents-law-review.md` (Russian, gitignored data) put the guideline's `[]` rules verbatim beside
the 19 agreed-`[]` rows ruled incorrect, the 6 ruled correct and the 3 non-empty ones; the operator
answered it in a structured interview instead of a read-through, and the answer is amendment 3.8.
**Its builder is pinned to the guideline revision under review** (`GUIDELINE_REV = "0906de6"`) —
guideline v2 rewrote three of the spans it quotes, so reading the working tree would re-issue a
pack quoting the law that *replaced* the one the operator ruled on. It still rebuilds byte-for-byte
(`c6642920…`).

**THE 244 VERDICTS ARE IN AND THE CEILINGS ARE COMPUTED (2026-08-02) — awaiting the 4.5a gate
review.** The numbers, per head, metric-unit first (upper bound, disagreements only) then the
accuracy band over both strata: **sentiment 0.9613 macro-F1 · 0.9625** · **intents 0.9148 micro-F1
· 0.4596..0.4646** · **sarcasm_pair 0.6591 fix-rate · 0.6591** · **post_type 0.9683 macro-F1 ·
0.9800**. G1e is excluded from the ceiling arithmetic (team-lead decision 02.08) and contributes
raw verdict counts only: 4 disagreements (gold wrong 3), control 8 (incorrect 1). **The two units
do not bound each other and neither is a gate bar** — read [[phase45a-ceiling]] before quoting any
of them. Gold-wrong in the disagreement stratum: 15/35 · 31/67 · 15/23 · 5/11. Control `incorrect`:
**22 of the 23 fall in `intents`** (22 of its 40 rows), everything else is 0 except brands 1 of 8.
**The decisions that follow belong to the gate review, not to this record.**

**Amendment 3.7 inserted Phase 4.5 — a ceiling-driven quality program — before Phase 5**, because
the operator's 0.98 target sits above the instrument: comment gold was calibrated at 96.3%
agreement. The adjudication pack is `data/annotation/audit_45a/` (gitignored data;
`scripts/build_audit_pack.py` is the committed, deterministic builder, seed 42): 140 blinded
disagreements — sentiment **35** · intents **67** · slice pair **23** · posts **15** (post_type 11 +
brands 4) — plus **control 104** (sentiment 40 · intents 40 · the other three 8 each). **Every
disagreement row showed two candidate labels as `label_A`/`label_B` in per-row random order and
NOTHING said which was whose** — the key is `data/annotation/audit_45a_key.json`, outside the folder
the operator opened, sha-pinned in `results/audit_45a_manifest.json`. **The executor pre-filled,
suggested and commented on nothing** (SPEC §10). Nothing was judged, re-scored, or written back to a
frozen file.

**The returns were normalized, not retyped.** The operator's five CSVs came back through a
spreadsheet (semicolons, verdicts as `B — правильная метка label_B`);
`scripts/normalize_audit_returns.py` maps the five forms by table, derives every verdict twice
(table and leading token must agree), refuses any return set outside the team lead's five pinned
sha256, and rebuilds each row from the **sealed** row with one cell replaced — then blanks the
verdicts again and requires the sealed bytes back. Verified outside the script: **244 verdict cells
filled, 0 non-verdict cells changed**, and the tallies reproduce the team lead's independent count
(A19/B16 · A32/B33/amb2 · A3/B20 · A7/B8 · 81/23). Every sha is in
`results/audit_45b_returns.json`.

**The expansion did not resample the accepted pack.** All four disagreement CSVs and the key are
byte-identical to the accepted build, and the accepted 40 control rows are present verbatim inside
the 104: every head draws its first 8 before any head draws a top-up, so the seeded stream that
produced them is untouched. Widening a stratum by resampling it would make "the same pack,
expanded" a claim nobody could check.

**`scripts/audit_ceiling.py` HAS RUN, once, on the filled pack** — every refusal passed on the way
(key sha256, no empty cell, no unknown column, no edited label, row counts against the key). It
prints **two ceilings that are not interchangeable**: the *metric-unit* one re-scores a simulated
perfect model through `scorer.py` (comparable to a G1a/G1c bar, and an **upper bound** — it sees
only the disagreement stratum), and the *accuracy-unit* one counts both strata and is **not
comparable to an F1 bar**. The agreement stratum is ~90% of every head, so the harness prints a
sensitivity line beside the point estimate. **What the expansion bought:** one extra `incorrect`
now moves sentiment **2.28 pp** and intents **2.08 pp**, against **11.41** and **10.41 pp** at n=8.
The other three heads still sit at n=8 and their ceilings are read at that resolution.

**PHASE 4 IS CLOSED AT 2 OF 5 (2026-08-02) — accepted, and the one attempt is spent.** The team
lead recomputed every verdict number **bit-exact from the per-row dumps**, re-ran the selection
rule (output matched word for word), confirmed the one-attempt protocol from artefacts, and the
operator's quiz came back **2/2**. [[phase4-gate-verdict]] is `accepted`. Both ablation arms
trained in full on the frozen config, each scored on the frozen sets **exactly once**; **nothing
was retrained, re-scored or reconfigured after a gate number was seen** — arm B launched while arm
A's three failures were already on screen. **369 tests**, `make check` green after every commit.
**22 ADRs** ([[INDEX]]).

**THE DELIVERABLE: `results/train/4c-arm-a/adapter`** — the real-only LoRA adapter, sha256
`c0e462af81aad9f1…`, served **UNMERGED** on the same NF4 4-bit base every gate was scored through.
**Phase 5 is PAUSED** and Phase 4.5 (quality program, amendment 3.7) comes first — an operator
sequencing decision.

**THE VERDICT: 2 of 5 Tier-1 gates pass, on the real-only arm.**
G1d **0.9386** ≥ 0.8984 **PASS** · G1e **0.9333** ≥ 0.8874 **PASS** ·
G1a **0.9107** < 0.9418 FAIL · G1b **21/44** < 27 FAIL · G1c **0.8212** < 0.8436 FAIL.
The two that pass are the no-regression gates of amendment 3.5 (2), and they pass by **+3.02** and
**+3.59 pp above the anchor**, not by holding a line — the multi-task forgetting risk they were
rewritten to measure did not materialise. The three that fail are margin gates and they fail **by
margin, never by regression**: every gated head of both arms is above the zero-shot anchor. G1a
asked +5 pp and got +1.89, G1c asked +5 pp and got +2.76, G1b needed 27 of the base model's own 44
errors and fixed 21. A failed gate closes its question (SPEC §5) — nothing is retried.

**THE SYNTHETIC SOURCE IS DROPPED, on the half of the rule it was written for.** with-synthetic won
G1b outright — **24/44 against 21/44**, the largest single-head move either arm made — and lost the
second clause: G1c −1.39 pp and G1d −2.27 pp, both past the 0.5 pp tolerance. Exactly the trade
amendment 3.4 (3) pre-refused before any number existed. **Read this beside it and do not confuse
it with the verdict:** with-synthetic's G1a `ru` is **+4.44 pp** over real-only (0.9364 vs 0.8919),
the biggest per-language gap in the table — the strongest sign the generated Russian rows did
something real, and it changed nothing, because the rule was fixed first. Both columns are
published; there is no third run.

**Both arms, every gated head** (anchor → real-only → with-synthetic):
G1a overall 0.8918 → **0.9107** → 0.9172 · `ua` 0.8918 → 0.9146 → 0.9171 · `ru` 0.8849 → 0.8919 →
**0.9364** · G1b — → **21/44** → 24/44 · G1c 0.7936 → **0.8212** → 0.8073 · G1d 0.9084 →
**0.9386** → 0.9159 · G1e 0.8974 → **0.9333** → 0.9577 · relevance (not gated) 0.9415 → 0.9894 →
0.9891. Both arms' ≤2 pp G1b guard is **positive** (+0.0189, +0.0254): neither traded overall
sentiment for the slice.

**What G1b's failure is made of** — read off the committed dumps, nothing re-scored: of the 23
slice rows real-only misses, **15 are wrong on sarcasm only, 8 on both, 0 on sentiment only**. On
the full 108-row holdout (every row gold `sarcasm: true`) real-only detects **82** and
with-synthetic **83**, against the base model's **64**. Both arms moved that head ~19 rows and
neither cleared a bar defined as 60% of the base model's own errors.

**Beside the deliverable:** merging into bf16 stays forbidden until measured. The with-synthetic
adapter (`0566900e3f42451e…`) is kept next to arm A's — the ablation's second column is evidence,
not waste.

**Both arms ran clean and inside every box.** Arm A **270 steps in 3.40 h**, arm B **346 steps in
4.17 h** — both under 4b's own projections (3.42 / 4.37 h) and well under the 5 h ceiling. Peak GPU
30.86 / 30.84 GB of 48; micro-batch 2 × accum 8 held throughout, the OOM branch never fired.
**758/758 rows scored on both evals with zero failures of any kind** — no parse, no generation, no
truncation. Adapter hashes computed on the pod and on the Mac matched before either record was
appended.

**RESUME IS PROVED against the real stack** — 4b's [[4b-training-contract]] §(h) question, closed
in the first ten minutes of the first pod. Ten steps, reload with `is_trainable=True` onto the
k-bit base, `torch.load` of a real 238 MiB paged-AdamW state, five more steps: the optimizer step
counter continued (10 → 15, no reset) and the loss stayed on trajectory (0.10974 → **0.05680**,
carve 0.11247 → 0.05915). `assert_resumable` — added for this — stayed silent.

**TRAINING IS NOT BIT-REPRODUCIBLE ON THIS STACK.** Arm A's step-5 loss is **0.18010**; the resume
proof, on identical data, identical seed 42 and identical config on the same pod, gave **0.18051**.
Cause not isolated — NF4 reduction order (the family 4a measured when greedy turned out not to be
batch-invariant) or the `lora_dropout: 0.05` mask sequence. **Say "the ablation is paired on data
and config", never "identical"**; amendment 3.4 (3)'s "identical config and seed" reads stronger
than the hardware delivers, and the rule's 0.5 pp tolerance is what absorbs it.

**GPU money: $6.9903 of the $25 cap; remaining $18.01**, read at the close-out after the last pod
was deleted. 4c itself cost **$5.74** against ~$5.2 projected. **No pods exist any more** —
`pod list -a` is empty; the stale 4a pod `gxkdecf3g7k3y7` was deleted here. **The 100 GB CA-MTL-3
network volume `gfwa2an8fn` is KEPT on purpose** — its fate is a Phase 5 briefing decision, and it
is the only thing still billing (~$7/month, and the $0.11 between the 00:00 reading and the
close-out reading is what that looks like).

**The own-pod row is baseline (c) EVERYWHERE** — operator decision 2026-08-01
([[phase4-own-pod-anchor]] §(f)). **The bars, as amendment 3.5 leaves them:** G1a overall
**≥ 0.9418** (floors `ua` 0.8718 · `ru` 0.8649) · G1b **≥ 27 of 44** with the ≤2 pp macro-F1 guard ·
G1c **≥ 0.8436** · **G1d ≥ 0.8984** · **G1e ≥ 0.8874**. **Every one is derived in code from the
own-pod record — none is typed anywhere**; `PYTHONPATH=src python3 scripts/gate_bars.py` prints the
table and `scripts/gate_verdict.py` prints the rule's arithmetic and the verdicts.

**The own-pod row anchors G1d/G1e** ([[phase4-own-pod-anchor]]): `google/gemma-4-31b-it` at
revision `842da379…`, NF4 4-bit, RTX A6000, **758/758 rows scored, zero failures**,
`gate_anchor_valid: true`. Gated heads: G1a `ua` **0.8918** · `ru` **0.8849** · G1c **0.7936** ·
G1d **0.9084** · G1e **0.8974**; relevance 0.9415, not gated. **The own-pod number anchors
regardless of the OpenRouter disagreement — nothing is averaged.**

**The G1b slice is a file: `results/g1b_slice.json`, n = 44**, sha256 in the record and verified on
every load. Sentiment errors **13 ⊂** sarcasm errors **44**. 44 < 100 → amendment 3.2's
pre-registered fallback: report the smaller n beside the verdict, top nothing up. **An arm READS
this file and never writes it** — `build_gates` returns `None` for the slice on the fine-tuned
branch, so `write_slice` cannot be reached even by accident.

**GREEDY IS NOT BATCH-INVARIANT on bitsandbytes NF4 + A6000.** Measured 2026-08-01: one probe row
of 24 flipped its intents between batch 8 and batch 1. **Every gate eval ran at `--batch-size 1`**,
and the arm path *refuses* any other value by name rather than defaulting it.

**One writer per file, and the layer is live** (`2b423c8`): `docs/STATUS.md`, `docs/SPEC.md` and
`docs/PROMPT-*.md` are **team-lead files** — read them, commit them verbatim, never edit them.
Deny rules in `.claude/settings.json` refuse **both `Edit` and `Write`**.

**Phase 4's base model is `google/gemma-4-31b-it`** ([[phase4-base-model-gate]]) — ahead on every
gated head among the candidates. The 27B row's unpairedness was closed by a worst-case bound
analysis at $0; those rows keep `gate_anchor_valid: false` permanently.

**The Phase 3 baseline table** (`results/baselines.json`, read only via `scripts/show_results.py`),
G1a overall / G1c / G1d 3-class / G1e:
`tfidf-logreg` 0.6834 / 0.6000 / 0.6653 / 0.1964 · **gemma-4-31b-it (OpenRouter fp8) 0.8944 /
0.7981 / 0.8898 / 0.9211** · qwen3.6-27b 0.8541 / 0.7606 / 0.7605 / 0.8919 (`gate_anchor_valid:
false`) · qwen3.5-9b 0.7745 / 0.6252 / 0.5077 / 0.6476 · **xlm-roberta-base 0.7824 / 0.6007 /
0.7347 / NOT COVERED** · ref `claude-haiku-4.5` 0.8708 / 0.7739 / 0.7718 / 0.8537. That is the
**Phase 3** table; the own-pod anchor and the two Phase 4 arms are separate rows.

**The scorer computes, and it is the only thing that may.** `src/market_pulse/scorer.py` holds
every gate function, the margins, the selection rule and the verdicts. Bars and head deltas round
to ten decimals: `0.90 + 0.05` is 0.9500000000000001 and the gates are ">=", so a model exactly on
its bar must not fail on the last bit of an addition. A public function without a hand-computed
test fails the suite.

**Frozen test sets are at v2** — `docs/frozen-testsets.md` has the hashes and per-gate depth.
comments 400/1600, posts 250/750, thread-disjoint, zero `unclear` in test. **Training data is three
files**: `comments_train.jsonl` (1600) + `sarcasm_candidates.jsonl` (746) plus
`synthetic_sarcasm.jsonl`, 600 generated rows — **now measured and dropped by the ablation**
([[synthetic-sarcasm-augmentation]] stands as the record of how it was made and QA'd).
**G1b's holdout** is 108 rows, all `sarcasm: true`, thread-disjoint ([[hybrid-sarcasm-holdout-3.2]]).

## ⏭️ Next

1. **The team lead briefs 4.5g — the up-label of the 1,912** under a full-field v2 precheck plus a
   3-strata calibration, and the operator's ~2.0 h sitting **bundles with the 14 rows** of
   `unreadable14.csv` (~6 min, `intents_v2` blank, nothing proposed). The gate that gated this is
   decided; nothing of it is started here.
2. **Four things the gate did not answer, and none of them are closed by its PASS.** The 1,190
   `unclear` staged rows — **37% of the file** — were never sampled by the calibration, are excluded
   from every metric, and are still headed for training. The 54 frozen ids get **two homes** the
   moment the holdout moves to v2: their v1 copy stays in `sarcasm_holdout_pool.jsonl`, and 4.5f did
   not scope them (`no frozen-file changes`), so nobody is named. **Whether `unreadable14.csv` is
   committed blank** (today it follows the pack convention: gitignored, sha-pinned, rebuildable).
   And **whether the 97-row emptied class counts as the "repeating class"** that would put 11902's
   precedent — a dish wish reads `taste`, not `availability` — into the guideline; STATUS.md says
   only if the class repeats, and the measurement now says it is 97 rows. Also still unnamed from
   4.5a: **which unit the program calls "the ceiling"** — a macro-F1 bound and an accuracy share
   cannot both be read against 0.98.
3. **Test v4 has to lift a guard, not flip a flag.** `relabel_intents.py` refuses any row sitting in
   a frozen test file, unconditionally, and test v4 is exactly a re-label of the test set — a code
   change with a test, deliberately not the `--allow-test-rows` switch that does not exist today.
   Then a fresh G1c anchor under `T1v2` → retrain → new bars pre-registered BEFORE scoring. The three
   boundary rulings of guideline v2 are law but reach `comments_test.jsonl` only there.
4. **The filled pack is now the only copy of 244 verdicts.** `build_audit_pack.py --force` would
   destroy them and there is still no snapshot in the flow — the question the team lead has not
   ruled on. `normalize_audit_returns.py` is safe to re-run (it no-ops on an already-normalized
   pack), and the raw returns in `data/annotation/audit_45a_returned/` are the backup, sha-pinned
   in `results/audit_45b_returns.json`.
5. **Phase 5 is still PAUSED** — nothing Phase-5-shaped is scoped, planned or started; 4.5 comes
   first (operator sequencing decision, amendment 3.7). Everything after 4.5a — targeted
   re-labelling at scale, synthetic v2, a dev-set hyperparameter search — is **DEFERRED until the
   4.5a gate review rules on the numbers**, and each gets its own pre-registered gate.
6. **Still the operator's, carried out of Phase 4:** Phase 5's first measurement is already named —
   **do not merge the adapter into bf16 without scoring the merged artefact in the configuration
   production serves**; and the 100 GB CA-MTL-3 volume is kept pending the Phase 5 briefing.
7. **Six findings for Phase 5, none gate-relevant, all in [[phase4-gate-verdict]] §(f):** `planned`
   over-counts steps by one per epoch (272 planned, 270 run); leftover micro-batch gradients carry
   across the epoch boundary; the post-loop `save()` records the loop variable rather than the stop
   position after an early `--max-steps`; `seconds_per_step` in a resumed provenance is understated;
   training is not bit-reproducible; and the eval's last-line crash that the stub caught.
8. Still open from Phase 2 (not a blocker): dataset cards for the public augmentation datasets +
   licence check.

## 🚧 Blockers

**None open, and Phase 4 closed without leaving one.** 4c raised no escalation: the one
pre-registered stop it could have hit — a projection crossing the 5 h per-arm ceiling — did not
fire (3.40 h and 4.17 h, both under 4b's own
projections). Every earlier escalation came back decided at the next acceptance: 4b's three closed
by SPEC rev. 3.6 (the ceiling to 5 h/arm, an arm is a volume-less pod session, resume proved first
on the 4c pod — **done, and it passed**), and 4a's two by amendment 3.5 (G1d/G1e rescaled to
no-regression bars, the scorer taught to read the persisted slice).

**This Mac's device numbers, if anything is ever trained locally again:** 2 193 steps across
9 heads, **CPU 3.5 s/step**, **MPS 48.1 s/step** and OOM at 9.07 GiB unless the 250k×768 embedding
matrix is frozen. CPU beats MPS by 14×, which is the opposite of the intuition.

## ⚠️ Footguns for the next run

- **Two taxonomies exist now, and the five-class one is still the one every number was measured
  over.** `scorer.INTENTS` (5) is what `run_baseline.py`, `train_xlmr_baseline.py` and
  `parse_reply("T1", ...)` use; `INTENTS_V2` (6) is what guideline v2, `T1v2` and the re-labeller
  use. **Never widen the five-member tuple** — it would change old label spaces in files nobody
  edited. And never add a prompt to `prompts.TASKS`: that tuple is the identity map
  `records.assert_prompt_sha` compares whole against every stored record.
- **`results/spend_45d.json` and `results/spend_45e.json` are anchors, not logs.** Same footgun as
  `results/spend_3b.json` and `results/spend_phase4.json`: delete or regenerate one and its counter
  silently restarts at today's lifetime usage. Each is written *before* the first request on
  purpose, and `relabel_intents.py --phase` refuses a ledger carrying another phase's anchor key.
  **The run entries do not sum to the phase spend** — `Budget.reconcile` can only push a number up,
  so a run whose predecessor had not yet posted absorbs its tail ($0.5778 of entries against
  $0.5448 measured from the anchor). The anchored difference is the spend; the sum is a bound.
- **The `_tax2` files are accepted now, but they are still not drop-in replacements.** The ≥90% gate
  passed, so the labels are validated — the row *counts* are not: `sarcasm_holdout_pool_tax2.jsonl`
  has 915 of 971 rows (54 frozen ids + 2 with no answer) and `comments_train_tax2.jsonl` 1,594 of
  1,600. A trainer pointed at them silently drops the 14 unreadable rows and the frozen ids.
- **`read_calibration_returns.py` refuses to run, and that is correct.** It sha-pins the staged
  files against `results/calib_45e_manifest.json`, and the three 4.5f rulings moved them
  (`comments_train_tax2.jsonl` `d2132c1e…` → `e5a52a08…`). The gate was computed **before** the
  rulings and lives in `results/calib_45e_verdict.json`; the sealed manifest describes the corpus as
  it was sealed, and `fixes` in `results/relabel_45e.json` is the only place the chain to today's
  bytes is written down. Do not "fix" the refusal by re-pinning the manifest.
- **Two gold versions exist now, so every number has to name one.** `data/frozen/*_v3.jsonl` sit
  beside the v2 files and **nothing reads them by default** — the gates, the bars,
  `eval_zero_shot.py` and `run_baseline.py` all still score against v2, which is what keeps Phase 4's
  verdict meaningful. v3 numbers live only in `results/rescores_v3.json` (`gold_version: "v3"`) and
  are **program measurements, never gate results**; they must never be appended to
  `results/baselines.json`. Scoring a *new* run against v3 is a gate decision nobody has taken.
- **`data/annotation/audit_45a/` now holds 244 verdicts and gitignored data has no HEAD to restore
  from.** `build_audit_pack.py --force` is the only path that overwrites a filled pack and it takes
  no snapshot — do not run it to "regenerate" anything. What can be re-run safely:
  `normalize_audit_returns.py` (no-ops once the pack matches `results/audit_45b_returns.json`) and
  `audit_ceiling.py` (reads only). The verdicts survive in the raw returns under
  `data/annotation/audit_45a_returned/`, sha-pinned in the normalizer and in that record; treat that
  directory as read-only.
- **Registry brand normalization does not fold Unicode homoglyphs.** A mention spelled with a
  Cyrillic `о` inside a Latin-script brand casefolds to a token the watchlist alias table misses,
  so two strings that render identically score as two different entities — one FP and one FN on
  G1e. Found on the 4.5a brands stratum (n=4, so at least a quarter of it). **The fix is deferred
  to the 4.5 follow-ups on purpose: a normalization change mid-audit would silently redefine future
  G1e numbers against past ones** — Phase 3, the own-pod anchor and both arms were all scored
  through today's `normalise_brand`. Do not "just fix" it; it is a re-scoring decision with a plan,
  and every old run can be re-scored from its dump at $0 (`implementation-notes.md`, Phase 4.5a).
- **The results record holds TWO rows under the gate id `G1d`** — post_type, which gates, and
  relevance, which amendment 3.3 reports beside it and never inside it. A dict keyed by gate id
  returns the relevance number and a bar that looks entirely plausible (0.9315 instead of 0.8984).
  `records.anchor_values` selects on the metric name and refuses anything but one match.
- **Gemma 4's chat template drops the thinking channel when you render a full assistant turn.**
  The generation prompt ends `<|turn>model\n<|channel>thought\n<channel|>`; the turn form ends
  `<|turn>model\n` and then the content. Build a training example from the turn form and the model
  is conditioned on a context no gate row carries — silent, and it only shows up as gates lower
  than the smoke suggested. Take the prompt from the eval call, the end-of-turn marker from the
  turn form.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. If the pod exists only for one session, **delete** it
  (`runpodctl pod delete` — there is no `pod terminate`), do not stop it.
- **Python buffers stdout when it is redirected to a file.** 15 minutes into the 4b smoke the log
  still held nothing after the model load. `loss.jsonl` is written open/write/close per line and is
  the live view; `python3 -u` fixes the log itself.
- **`results/spend_phase4.json` is the $25 cap's anchor and must not be regenerated.** It stores
  the RunPod balance as Phase 4 opened; delete it and the counter silently restarts at today's
  balance. The guard also refuses when the balance is *above* the anchor — a mid-phase top-up means
  the delta stopped measuring this phase, and re-anchoring is an operator decision.
- **A stopped pod is not a stopped bill.** The 100 GB network volume bills by the month with no pod
  attached. `runpodctl billing pods` cannot see it; only the account-balance delta can, which is why
  the guard reads both and takes the larger.
- **`runpodctl pod list` shows running pods only.** An empty list is "nothing running", not
  "nothing exists". Use `pod list -a` or `pod get <id>` to show a stopped pod's `EXITED` state.
- **Network volumes live in a different datacenter set than the A6000 does.** `EU-SE-1` had the
  best A6000 stock and takes no volumes at all; the intersection was `CA-MTL-3`. Pick on the
  intersection or pay for a second volume.
- **`RUNPOD_POD_ID` is not inherited over ssh** — export it in the run command or the record's
  `runtime.pod_id` is `None` and the number cannot name its machine.
- **The RunPod PyTorch image's python is PEP 668 managed.** `pip install` refuses; use
  `python3 -m venv --system-site-packages` so the image's CUDA-matched torch is reused rather than
  a 3 GB re-download of a possibly different build.
- **Greedy decoding is NOT batch-invariant on bitsandbytes NF4 + A6000** — measured 2026-08-01, one
  row of 24 flipped its intents between batch 8 and batch 1. Every gate run goes at `--batch-size 1`
  until someone re-measures and records the result. Batch 1 is run-to-run identical, also measured.
- **`add_special_tokens=False` is load-bearing and now asserted.** Gemma 4's chat template emits
  `<bos>` itself; a template revision that stopped would silently make every prompt worse, so
  `LocalClient` refuses to construct if the rendered prompt does not start with the BOS token.
- **Gemma 4 has a thinking channel.** `enable_thinking=False` + `add_generation_prompt=True` emits
  an already-closed `<|channel>thought\n<channel|>` — the local equivalent of 3b's
  `reasoning: {"enabled": false}`. It is the current default and is passed explicitly anyway: with
  thinking on, `parse_reply` would read the first brace inside the reasoning text.
- **A `--probe` is not a smoke test unless it prints rows.** Aggregate counts are identical whenever
  two configurations merely parse, so a check built on them cannot fail. The batch-invariance check
  diffs the per-row prediction lines and guards with `test -s` — two crashed probes produce two
  empty files, and `diff` on those is silent success.

- **`docs/STATUS.md`, `docs/SPEC.md`, `docs/PROMPT-*.md` are team-lead files.** Read and commit,
  never edit — the deny rules refuse `Edit` *and* `Write` on them, without a restart. Phase-end
  facts go to the daily log or `implementation-notes.md`. The refusal reads "File is in a directory
  that is denied", but the rules are file-scoped: the rest of `docs/` is still writable.
- **A ceiling lifted by the operator is not a ceiling lifted in code.** `train_xlmr_baseline.py`
  refuses to train above `--time-budget-min` and exits **3** — it prints a projection and leaves no
  process, which reads exactly like a crash. Grep your own guards before any unattended launch.
- **The six 3b zero-shot records carry no per-row predictions — never claim paired re-scoring from
  them.** They hold `scored_ids_sha256` (a hash of the id list) and error counts, nothing that can
  be re-scored. Dumps exist only from step 3c onward, and the six are **not** backfilled: they
  cannot be reconstructed and a synthesized dump would be worse than the gap.
- **A prediction dump must be sorted before it is hashed.** Rows come back from four workers; a
  digest in completion order is a hash of the scheduler, not of the data. And it carries ids and
  predicted labels **only** — no gold, no source text, or it becomes a second copy of a frozen file.
- **`results/spend_3b.json` is the $8 cap's anchor and must not be regenerated.** It stores the
  lifetime OpenRouter usage as of the first 3b request; delete it and the next run re-anchors at
  today's usage, silently resetting the phase counter to zero.
- **Never use `anthropic/claude-haiku-4.5:batch`** — served only through `/api/beta/batches`, 404s
  on `/chat/completions`. The runner refuses the slug on purpose.
- **The reference row is marked in the record, not just the filename.** `build_record` rewrites
  every `gate` field of a `--reference-only` run to `ref`, so a lookup for `G1d` cannot find it.
  Do not "fix" those entries back to gate ids.
- **A run that trips the cap writes no record** — a partial run must never become a gate anchor.
  Do not re-run with a bigger `--max-run-usd` to get the record.
- **`GET /api/v1/generation?id=` 404s for our generations** at every delay tried (2 s to 60 s).
  Spend reads `usage.cost` and reconciles against `/credits`; do not "restore" that path.
- **Endpoint health readings are point-in-time.** The pins were chosen on status/uptime as read at
  pin time; `deepinfra/fp8` was deranked then and healthy hours later. The precision *rule* is
  pre-registered; re-pinning a provider is legal — but say so if you do it.
- **`scripts/freeze_testsets.py --force` would rebuild the split and destroy v2.** A fresh draw
  differs from v2 by 8 rows. Do not run it. Likewise `mine_sarcasm_candidates.py --force`
  (746 hand labels) and `mine_sarcasm_holdout.py --force` (971); `refreeze_v2.py`,
  `sync_batch_v2.py` and `freeze_sarcasm_holdout.py` are one-shot.
- **`data/annotation/sarcasm_holdout_pool.jsonl` is not training data** — its non-sarcastic rows
  share threads with the holdout.
- **Never merge `synthetic_sarcasm.jsonl` into a real-source file.** The Phase-4 ablation has to
  drop it by dropping one path. `data/annotation/*` is gitignored, so the file survives only
  through an explicit `!` exception — do not "tidy" that line away.
- **The generated rows passed QA but carry no QA number, and that is not an oversight.** ≥80% `ok`
  was pre-registered before the 50-row draw; the operator ruled it passed without returning the
  marked-up CSV. The executor never scores its own sample (SPEC §10), so the empty
  `operator_verdict` column stays empty. The ADR is the authority on the verdict.
- **The freeze shrank `sarcasm_candidates.pristine.jsonl` 800 → 746** so the validator would not
  read the moved rows as lost. Legitimate once, audited — but the validator can be silenced the
  same way again. Any further row loss must be diffed against the baseline before it is believed.
- **`results/baselines.json` is append-only and never hand-edited.** Numbers reach it only through
  the scorer; `scripts/show_results.py` only reads. A hand-typed number there is invisible.
- **A results record cannot name the commit that contains it**, so provenance is `commit` + the
  `dirty` paths at run time; the runner shouts if any is under `src/`, `scripts/` or `config/`.
- sklearn lives in the `baseline` extra and torch/transformers in `xlmr` — no test may import
  either, or `make check` stops being runnable on a bare checkout.
- `RAW_STORE_SALT` in `.env` must never be rotated: a new salt orphans every `sender_anon_id`.
- `packaging` has 19 rows in the test set — G1c is thin by construction, not by accident.
- **Do not merge a QLoRA adapter into bf16 base weights without measuring it (Phase 5).** An
  adapter trained against a 4-bit NF4 base learned to compensate THAT base's quantization error;
  merged into unquantized weights it corrects errors that are no longer there. Second-order but
  measurable — so measure it: score the final artefact in the EXACT configuration that will serve
  production. Safe default: serve the same 4-bit base plus the adapter, unmerged.
- **XLM-R cannot do G1e** without a token-classification head. An empty G1e cell means "not
  attempted", never "scored zero" — the two must never be conflated in a comparison table.

- **A print statement can crash a run after the record is written.** The G1b-slice line at the end
  of `eval_zero_shot.main` was guarded by `anchor_valid` alone; on a fine-tuned arm `slice_ids` is
  `None`. It would have raised at the end of a 45-minute eval following a 3.4 h training run. Drive
  `main` through `--record-out` with a stub: `--smoke` returns before the record is built and
  `--probe` before it is written, so neither exercises that path.
- **`planned` is not `steps`.** `ceil(rows / (micro × accum)) × epochs` over-counts by one step per
  epoch whenever the epoch's micro-batches do not divide by the accumulation, and those leftovers'
  gradients are never zeroed — they fold into the next epoch's first step. 272 planned, 270 run.
- **Two runs of the same arm at the same seed give different losses** (0.18010 vs 0.18051 at step 5,
  same pod, same data, same config). Never write "identical" about two runs on this stack.
- **A test fixture that copies the real results file will collide with reality.** `test_gate_verdict`
  adds two fixture arms to the committed history; once the real arms existed that was two rows per
  arm and the suite failed on its own setup. It now strips records carrying `config.fine_tune`.

## 🐞 Known harness bug

Fixed 2026-07-28: `knowledge/templates/daily-log.md` now carries `{{DATE}}`, the placeholder
`scripts/brain-session-end.py` actually substitutes; `tests/test_templates.py` keeps the pair
honest.
