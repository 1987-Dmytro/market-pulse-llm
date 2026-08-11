# PROMPT-sku-b-v3-prep — the resume, everything before the resumed session ($0)

> Authority: SPEC §3.17 (11) — ratified at the sku-b-run acceptance
> (operator, 2026-08-11). The (10)(b) stop resolves as RESUME: one more
> paid session buys EXACTLY the 121 unbought elements under a v3
> re-registration, cap $0.45, instrument FROZEN. This contract is $0 and
> local: no pods, no endpoints, no templates, no /run calls. The
> resumed session is sku-b-v3-run and it is NOT this contract.

## Read first (sections, not documents)

- `docs/SPEC.md` §3.17 (11) — the five readings this contract
  implements. Transcribe, do not redesign.
- `results/sku_b_positions.json` :: `population.unbought` (121 ids) and
  the dump `results/sku_b_positions.jsonl` (14 rows) — what exists and
  must never be re-bought.
- `results/sku_pilot_prereg_v2.json` :: `supersedes` — the v1→v2
  pattern D1 repeats for v2→v3.
- `docs/reports/sku-b-run.md` §"What a v3 can and cannot be priced
  from" — D4's inputs.

**On checkout, ONE test is red BY DESIGN, same mechanism as twice
before:** the marker enumeration knows four names, `docs/SPEC.md` now
carries five. Step 0.2 adds `sku-b-ratification-5`; green from there.

**Read-back check — FIRST lines of the report:** the five deliverables
one line each, then (11)'s readings (a)–(e) in one line each, then the
invariant "no paid calls in this contract".

## Step 0 (commits pre-authorised)

1. Team-lead docs commit, unedited: `docs/SPEC.md` (the -5 block),
   `docs/PROMPT-sku-b-v3-prep.md`, `docs/STATUS.md` (the 11.08-night
   block).
2. `tests/test_sku_prereg.py`: enumeration gains `sku-b-ratification-5`.
3. **ADR** `knowledge/decisions/sku-b-run-acceptance-and-resume.md` +
   INDEX: the (10)(b) stop and its probe finding, the calibration read
   (6/13, superscript pattern, non-gating per (11)(e)), the resume
   ruling with the operator's «завершить замер» decision, artifact
   paths. English.
4. Vault tail (fixed paths as usual) → its own final commit.

## Deliverables (five; STOP and report if one runs deeper than briefed)

1. **Pre-registration v3** `results/sku_pilot_prereg_v3.json`, via the
   producer (`write_sku_prereg` pattern), registered BESIDE v2 and
   committed BEFORE any v3-run artifact. `supersedes` names v2's sha
   and the reason (the (10)(b) stop + (11)); `moved` enumerates ONLY:
   the attempt clause (resume wording: the 121 unbought elements, one
   session), `cap_usd` 0.45, the warm-up inputs ((11)(c)), and a
   `bought_already` block pinning the run record and dump shas with
   the 17 ids. Every bar's verbatim text, thresholds, R1–R5, both
   instrument shas and the serving pin are BYTE-EQUAL to v2 — asserted
   row by row in tests, not claimed.

2. **Driver resume mode** (`--resume`, default off): reads the v1-run
   record and dump; buys ONLY `population.unbought`; REFUSES to start
   if any unbought id already carries an answer, if any bought id is
   requested again, or if the record/dump shas differ from v3's
   `bought_already` pins. Warm-up per (11)(c): one real UNSENT page
   (deterministic pick from the 51, seed-42, id recorded) and one real
   pre-filtered non-pack row (same rule); both answers recorded,
   never scored, never entering any bar artifact. Go/no-go and in-run
   gate unchanged, budget = $0.45 minus everything already billed to
   the v3 session. Final artifacts: the dump gains the new rows
   (append, provenance per row: which session bought it); a merged
   bar-input record carries all 108 page answers + 30 text answers
   with both sessions' shas. `--smoke`/`--dry-run` prove the whole
   resume path with zero network, including the three refusals.

3. **Guard and record fixes (fix-on-touch, Dv151/Dv153).**
   `runpod_guard.py` step ledgers: normalize step names (hyphen ≡
   underscore) AND refuse to create a NEW step anchor when one exists
   under the normalized name; test drives the exact Dv151 collision.
   Driver record: `cost.jobs` split into `jobs_planned` and
   `jobs_billed` (from the endpoint's own health read where present);
   test.

4. **Projection v2** `results/sku_projection_v3.json` (new file, the
   old one stands as history): 91 pages × the MEASURED 5.0772 s/call
   (n=17, its one-job caveat named), 30 text calls bounded by the page
   marginal (assumption stated: an image-free call at the same ceiling
   does not exceed an image call; srv-2d's 4.262 s/row named beside
   it), warm-up 2 × page-marginal, boot as the range [175.8 historical,
   391.4 measured yesterday], idle tail $0.0184, vs cap $0.45 with
   headroom per corner. Arithmetic over named artifacts only.

5. **Preflight extension**: the resume guards driven both ways on the
   tiny-config model + fakes — refuses a re-buy, refuses an
   unbought-with-answer, refuses mismatched `bought_already` pins,
   accepts the honest resume; keeps every existing control.

Tests + `make check` green; Deviations continue **Dv154+**; report is a
FILE `docs/reports/sku-b-v3-prep.md`, chat gets ONLY the path.

## Do NOT

- No paid calls, no RunPod resources of any kind (GOAL: the one
  resumed session of (11) is sku-b-v3-run's, after this pass is
  accepted).
- Do not edit the registered prompts, the parser, the serving pin, or
  re-pin prereg v1/v2 (GOAL: (11)(b) — the instrument under
  measurement must be the one that was registered; v3 is registered
  BESIDE, by the producer).
- Do not touch `results/sku_b_positions.json` / `.jsonl` beyond
  READING them (the 17 answers are evidence; the resume APPENDS in new
  artifacts and the dump append happens only in the paid run).
- Do not edit `docs/STATUS.md`, `docs/SPEC.md`, `docs/PRODUCT.md`,
  `docs/PROMPT-*.md` — team-lead files; commit-only.
- Frozen family, frozen sets, `baselines.json`, `spend_phase4.json`,
  the two stale `max_new_tokens: 256` records — untouched.
- Never `git add -A`; vault tail → its own final commit.

## Report — evidence, not assertions

Read-back lines first. Per deliverable: commands and output tails (the
v3 byte-equality test run, the three resume refusals firing on the
fakes, the preflight's full output, `make check` tail). The projection's
arithmetic with every input named by artifact path. Deviations Dv154+,
explicitly "none" if none. English. State your assumptions.
