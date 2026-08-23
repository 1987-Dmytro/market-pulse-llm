# PROMPT — `lora-c-apply` (fresh session, ALL $0, Dv from 765)

You are the executor on `market-pulse-llm`. This contract APPLIES the team lead's two review
verdicts and SPEC amendment 3.25 to the lora-c data, then re-issues the registration DRAFT.
**Everything is $0: no pod, no endpoint, no paid call of any kind.** Full context up front:

- Read `docs/SPEC.md` amendment 3.25 (the marked block at the end), both verdict files —
  `docs/reviews/lora-c-rationales-verdict.md` and `docs/reviews/lora-c-synthetic-verdict.md` —
  and your own report's sections «REVIEW GATE 1», «REVIEW GATE 2», «The second STOP» and «The
  most serious finding» (`docs/reports/lora-c-prep.md`). Do not re-read the whole SPEC.
- **Read-back before step 1:** one line each — the three clauses of 3.25, the five named
  gate-1 rulings, the six gate-2 rulings. STOP if any is not on disk.

## Step 0 — baselines

Run the baseline instrument (head, porcelain, suite stamp, preflight) exactly as in
`lora-c-prep` step 0. Commit list for this contract: `src/`, `tests/`, `scripts/`, `results/*`
rebuilt artifacts, `config/qlora.yaml` (new revision), `docs/reviews/lora-c-rationales-sample.md`
(addendum row only), `docs/reports/lora-c-apply.md`, the ADR update, and the vault tail
(`knowledge/hot.md`, daily log, index) as its own final commit. Team-lead files you may COMMIT
but never edit: `docs/STATUS.md`, `docs/SPEC.md`, `docs/PROMPT-*.md`, both verdict files.
Any path outside these lists: STOP and report.

## D1 — apply gate-1 verdict ($0)

1. The three named rationale rewrites (20696, 21190, 578032) exactly as the verdict words them.
2. The sample addendum: append row `@VARUS_channel:10367#20766` to
   `docs/reviews/lora-c-rationales-sample.md` with the verdict's PASSES ruling quoted.
3. **Labels r3 delta:** new file `results/labels_pass1_r3.jsonl` carrying ONE row —
   `@retsepty:7342` msg `49685` → `не_наш_рынок` — with provenance (verdict path, date, the
   precedent row ids). It COMPOSES with r1+r2 the way r2 composes with r1; nothing else moves.
   Rebuild every count that reads the labels (pool distribution, class weights, draws).
4. Enumerate P-NULL and P-MARKER by the verdict's rules; rewrite matches; print the row lists
   and counts in the report. Borderline P-NULL calls default to KEEP and are listed as kept.
5. Re-run the hybrid grep (RU letters in rationale body, cue excluded) and print the result.
6. Only after 1–5 land: flip `rationale_reviewed: true` on all 515.

## D2 — apply gate-2 verdict ($0)

R1 (15 texts, labels stay) · R2 (`mention_vs_about` 5 text) · R3 (7 rationales → Ukrainian) ·
R4 (2 invented handles, substring-checked against the window's raw comment texts — and against
author fields only if the store carries any; open one record first and say which check ran) ·
R5 (skeleton diversity: no skeleton over a third of the 32 `молочный_бренд` rows; print
before/after skeleton counts) · R6 (seeded newline pass, ~30 rows, seed registered) ·
«власний формат» → «формат мережі» in `non_dairy_brand` 25–26. Then re-run BOTH instruments
and print them: the four contamination lists (must be `[]`; the 6-gram index is rebuilt over
the NEW texts) and the register table (newline axis now present; length/question deltas stay
named-deliberate). Only then flip `reviewed: true` on all 160.

## D3 — amendment 3.25 (1): `config/qlora.yaml` revision 2 ($0)

`training.max_seq_len: 2816` as a NEW REVISION per the project's sealed-config convention
(lora-b's pin on the old revision stays sealed and green — verify with `make preflight`).
Then the reality check the amendment orders: **try the real tokenizer** (the model id the
config names). If importable/downloadable at $0: tokenize all 506 SFT rows through
`apply_chat_template`, print min/median/max of the POD-COUNT quantity (with `TEMPLATE_SLACK`),
and **STOP back to the team lead if any row exceeds 2 800**. If the tokenizer is not
obtainable: record that as its own reachability note — the pod-side `encode_pass1` refusal
then runs BEFORE any train step in `lora-c-run` and its kill rule is boot-stage; say so in the
registration. Either way the three-ratio model table is re-printed against 2 816.

## D4 — amendment 3.25 (2): the equality refusal + full rebuild ($0)

Add the single refusal to `build_pass1_fewshot_packs.neighbours`: a candidate whose
whitespace-collapsed casefolded text equals the query's is refused (equality ONLY — no
threshold below 1.0). Then rebuild EVERYTHING that renders: the training set, eval pack E
(both legs), and the pass-2 pack. Print, from your own scan of the rebuilt packs:
own-text-in-examples count (must be 0 of 198 and 0 of 506), the disjointness battery by
(thread, msg_id) pair, per-item «did any query lose its k-th neighbour» counts (a query that
now cannot fill five examples is a NEW instance of STOP 1 — report it, do not improvise a
remedy), and `--reproduce` on the rebuilt pass-2 pack (bars must still read 4 of 5 and 2).

## D5 — registration DRAFT v2 + report ($0)

Re-issue `results/prereg_lora_c.json`: new shas for every rebuilt input, the corrected sampler
numbers (drive the draws again over the r3-corrected classes), both `steps` numbers, the rates
with their invalidation conditions (unchanged), the tokenizer result from D3, amendment 3.25
quoted and grepped back into `docs/SPEC.md` on every build, money block still OPEN, and the
test that asserts no price keys — all still standing. `make check` green on a STABLE tree;
`make preflight` on everything touched; the rebuild-identity test covers the new producers.

**Final step — the second-skeptic debt:** after your closing commit, launch ONE fresh-context
review of `git diff <step-0 sha>..<closing sha>` with the checklist «does every change trace to
a verdict ruling or to 3.25; was anything else touched». Paste its verdict in the report. If it
does not return within 30 minutes, say so in Deviations and do not wait further.

Report: `docs/reports/lora-c-apply.md` — evidence, not assertions (commands and their output);
Deviations from **Dv765** with cause tags from the closed enum v2 and the tally grep; a
five-line Process signals section. STOP after the report for team-lead acceptance.

**DO NOT:** create any billable resource; edit team-lead files (list above); relabel anything
beyond the one r3 row; touch `prompts.py`, the sealed registries, or any sealed record; rewrite
any rationale or synthetic row not named by a verdict ruling; carry a price into the record.
