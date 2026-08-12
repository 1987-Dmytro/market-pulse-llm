# PROMPT-sku-b-v4-prep — the fresh-ledger re-registration ($0)

> Authority: SPEC §3.17 (12) — ratified at the sku-b-v3-run acceptance
> (operator, 2026-08-11). One more resumed session, cap **$0.65**, its
> OWN cap/ledger/phase constants set together ((12)(b), the Dv167
> finding). This contract is $0 and local: no pods, no endpoints, no
> templates, no /run calls. The session is sku-b-v4-run.

## Read first (sections, not documents)

- `docs/SPEC.md` §3.17 (12) — the four readings. Transcribe.
- `docs/reports/sku-b-v3-run.md` §Dv163, §Dv167 — the two debts this
  contract pays.
- `results/sku_pilot_prereg_v3.json` :: `resume` — what v4 inherits
  unchanged (population, warm-up pins, bought_already).

**On checkout, ONE test is red BY DESIGN** (the sixth marker); step 0.2
adds `sku-b-ratification-6` to the enumeration and greens it.

**Read-back check — FIRST lines of the report:** the four deliverables
one line each, then (12)(a)–(d) one line each, then "no paid calls in
this contract".

## Step 0 (commits pre-authorised)

1. Team-lead docs commit, unedited: `docs/SPEC.md` (the -6 block),
   `docs/PROMPT-sku-b-v4-prep.md`, `docs/STATUS.md`.
2. `tests/test_sku_prereg.py`: enumeration gains `sku-b-ratification-6`.
3. **ADR** `knowledge/decisions/sku-b-v3-refusal-and-v4.md` + INDEX:
   the (10)(a) refusal on the representative probe, the three-marginal
   picture (1.44/5.08/14.81) with the deep-page reading, the fresh-
   ledger ruling, the cap arithmetic. English.
4. Vault tail → its own final commit.

## Deliverables (four; STOP and report if one runs deeper)

1. **Pre-registration v4** `results/sku_pilot_prereg_v4.json` via the
   producer, BESIDE v3, committed before any v4-run artifact.
   `supersedes` names v3's sha and the (10)(a) refusal record
   (`results/sku_b_positions_v3.json`, its sha pinned); `moved`
   enumerates ONLY: `cap_usd` 0.65, the ledger/phase names
   (`sku-b-v4`), and the supersede metadata. Population, warm-up pins,
   `bought_already` (17 of 138), bars, thresholds, R1–R5, instruments,
   ladder, pinned_inputs — BYTE-EQUAL to v3, asserted row by row.

2. **Driver: the v4 constants, set together** ((12)(b)):
   `RESUME_CAP_USD = 0.65`, `RESUME_LEDGER =
   results/spend_sku_b_v4.json`, `RESUME_PHASE = "sku-b-v4"`, and the
   registration path pointed at v4 — one block, one commit, a test
   asserting the three name one phase (the Dv167 composition can never
   recur half-updated). Plus the Dv163 debt: BOTH exits (refusal and
   completion) write the `jobs_planned` / `jobs_submitted` split —
   one shared cost-block builder, a test driving both exits against
   the same field names.

3. **Projection v4** `results/sku_projection_v4.json`, BESIDE v3's:
   both marginals as corners — the gate-pessimistic 14.808 s/page
   (the registered probe's own price → ~$0.60, MUST fit under $0.65
   with the 402.6 s boot + 3% drift) and the population-drawn
   5.0772 s/page (~$0.33); text at 3.862 s measured; idle tail; the
   headroom per corner. Arithmetic over named artifacts only.

4. **Preflight pins**: the resume guards re-driven against the v4
   registration (accepts the honest v4, refuses a moved v3-refusal-
   record pin, refuses the OLD ledger name — a v4 run that reads
   spend_sku_b_v3.json is the Dv167 trap and must refuse), every
   existing control kept.

Tests + `make check` green; per-commit checkout table in the report;
Deviations **Dv169+**; report `docs/reports/sku-b-v4-prep.md`, chat
gets ONLY the path.

## Do NOT

- No paid calls, no RunPod resources of any kind.
- Do not edit registered prompts, the parser, the serving pin; do not
  re-pin prereg v1/v2/v3 or touch the sealed
  `results/sku_b_positions.{json,jsonl}` and the v3 refusal record
  beyond READING them.
- Do not change the warm-up inputs ((12)(c): the registered page 4476
  and row @silposilpo:3370, re-verified by hash, never re-picked).
- Team-lead files commit-only; frozen family, `baselines.json`,
  `spend_phase4.json`, the two stale 256 records untouched.
- Never `git add -A`; vault tail → its own final commit.

## Report — evidence, not assertions

Read-back lines first; per deliverable the commands and output tails
(the v4 byte-equality run, the constants-coherence test, the preflight
full output, `make check` tail, the checkout table). Deviations Dv169+,
explicitly "none" if none. English. State your assumptions.
