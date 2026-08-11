---
type: decision
id: dec-2026-08-11-sku-b-serving-and-cap-discipline
date: 2026-08-11
status: accepted
tags: [decision]
---

# sku-b's serving configuration and its cap discipline: the prep/run split, the base-off pin, and the three readings that keep one job from out-billing the cap

**Context:** this is the **record debt of the sku-b-prep phase**, and it is named as such. Two SPEC
amendments landed on 2026-08-11 — 3.17 **(9)** at the joint review that opened the phase and 3.17
**(10)** at the acceptance that closed it — and neither had an English long form. Both are law
already: they sit in `docs/SPEC.md` as marker-wrapped blocks, which is how a living document grows
under a pre-registration that pins it byte-for-byte (`results/sku_pilot_prereg_v2.json` hashes the
**stripped** text, `973c87890ad049d5…`). This record is the long form with the numbers. **The home
of every value below is the artifact named beside it**, never this file: if the two ever disagree,
the artifact is the contract.

The subject is one paid session. SPEC 3.17 (6) buys sku-b **one attempt** at a **$0.35 cap**, and a
failed bar closes B as "instrument not ready" BY MEASUREMENT — no retry, no re-prompt, no second
draw. Everything here exists because that sentence leaves no room to learn anything twice.

## (1) The three ratifications behind 3.17 (9) — joint review, 2026-08-11

**(a) The prep/run split.** sku-b was one contract and is now two: `sku-b-prep` ($0, local — the
serving path, the driver, the pin, the projection) and `sku-b-run` (the single paid session). The
split is what lets every guard on the money path be built, driven and reviewed before a dollar is
at risk; the prep contract forbids RunPod resources of any kind, pods and templates included.
Artifacts: `docs/PROMPT-sku-b-prep.md`, `docs/reports/sku-b-prep.md`.

**(b) The serving configuration, transcribed and pinned.** `SERVING_CONFIG=POSITIONS`, the NF4 base
at revision `842da3794eaa0b77d5f08bae87a17459d91ff475` with **the adapter OFF**, greedy, forward
batch 1, `max_new_tokens` **800**. The pin is `results/sku_pilot_serving.json`, committed in its own
commit before any sku-b-run artifact exists — git history is the only witness to that ordering. Two
consequences worth stating separately:

* **The ceiling is a ceiling, not a target.** A reply that used its whole 800-token budget is a
  PARSE FAILURE, counted by reason and excluded from bar 3's denominator under R5 — never read as a
  shorter answer.
* **`expected_worker` is handed WHOLE to `serving.assert_serving`.** The driver
  (`scripts/positions_gm4_skub.py`) restates not one value of it, so the pin file *is* the identity
  stop, and a worker deployed from the wrong template stops the run before the first paid call.

**(c) The session opens on NON-gold inputs.** Before either leg touches gold the driver makes two
warm-up calls — a generated 64×64 image and a text row deliberately outside the 30-row pack
(`WARMUP_ROW`, checked against the pack's ids). What the warm-up buys is the cold start and the
proof that the instrument answers at all, paid for on inputs no bar is scored on.

## (2) The cap readings of 3.17 (10) — acceptance, 2026-08-11

Registered **before** the run, which is the only time a cap ruling can be written without being a
decision about a number one has already seen:

| | the reading | what it prevents |
|---|---|---|
| **(a)** | After the two warm-up calls the driver re-projects the WHOLE run from the warm-up-measured marginal plus everything already billed, and **REFUSES to make any gold call** if that projection exceeds what is left of the cap. A session stopped there has touched no gold and **has consumed NO attempt**; the pilot returns to the team lead for a v3 registration under the measured price | buying half a pilot. The one-attempt clause makes a partial run the most expensive outcome available: the money is gone and no bar is scoreable |
| **(b)** | A cap stop that fires **mid-leg**, after gold calls began, is a finding about the **CAP** and not about the instrument: it does not close B, it is not a failed bar, and what happens next is a team-lead ruling — never a silent re-run | a cap overrun being laundered into "the instrument failed". Bar 1's registered page set is EXACTLY the 108 sent pages (R2), so a page leg that stops early moves the numerator and not the denominator, which reads as a model that missed brands |
| **(c)** | **No single job may be CAPABLE of billing past the remaining cap on its own.** The per-job execution timeout is sized so one wedged job cannot overrun, and a job that ends `TIMED_OUT` **ends the run**, its unbought remainder recorded | the gap the security pass found — see (3) |

Thresholds (0.75 / 0.80 / 0.85), the $0.35 cap and the one-attempt clause of (6) are unchanged by
all three.

## (3) The security pass that motivated (10)(c): one blocker, four nits

A fresh-context review of the money path at acceptance. The **blocker** is (10)(c)'s reason for
existing:

> `JOB_TIMEOUT_S = 1800.0` with the projection gate running only **between** jobs. The gate is
> re-priced before each job and cannot see inside one, so a single wedged job could run its full
> 1800 s and bill **$0.5520** at the settled rate (`results/srv2d_cost.json :: rate.usd_per_second`
> = $0.00030669/s) — **1.58× the whole $0.35 cap**, with every guard in the driver reporting
> normally.

The fix is arithmetic, not vigilance: **900.0 s**, which bills **$0.2760** — under the cap on its
own — and is still ≥ 2× the longest *honest* job the projection predicts (the text leg is ONE job
carrying all 30 rows: 30 × 4.262 s × 3.125 decode uplift ≈ **400 s**; the page leg packs 108 pages
into 7 jobs of ≤ 8 MB, the largest ≈ 16 pages ≈ 75 s). 900 s is also what
`scripts/runbook_5b.md` and `scripts/runbook_srv2b.md` already pass as `--execution-timeout`.

The four nits, each a quiet way to lose money or evidence:

1. **A crash after the paid legs loses the run's record.** `spend_now` shells out to `runpodctl`;
   an exception there aborts `main` *after* the paid calls and before the record is written. The
   record is the only artifact of a one-attempt session.
2. **`--smoke --out X` writes a fake record at the real `--record` default.** The redirect fired
   only when BOTH paths were defaulted, so a half-explicit smoke could plant a fake artifact where
   the paid run's guard would then refuse to overwrite it.
3. **`--project-stop-usd` replaced the budget instead of tightening it.** A value above the
   remaining cap disabled the in-run stop entirely.
4. **The idle-timeout tail was outside the projection.** Serverless bills wall uptime plus the
   endpoint's idle tail; at the `--idle-timeout 60` every runbook in this repo passes, that is
   60 s ≈ **$0.0184** — larger than the $0.0104 of headroom the stated corner had.

All five are fixed under `docs/PROMPT-sku-b-prep-fix.md`; the fix pass's evidence is the
`## Fix pass` section of `docs/reports/sku-b-prep.md`.

**What nit 4 does to the finding, and it is not cosmetic.** With the idle tail inside every corner,
`results/sku_projection.json` moves from one corner over the cap to **two**: at the stated
ceiling-ratio decode uplift the pilot exceeds $0.35 on **both** cold-start readings ($0.3580
measured / $0.3750 pre-registered), and only the no-uplift corners fit ($0.1936 / $0.2106). The
decode uplift is the whole spread and it is an ASSUMPTION about a reply nothing has ever generated
— which makes (10)(a)'s go/no-go the likely first real event of sku-b-run, and the warm-up the
first thing that will price a positions reply for real.

## What this record does not do

It registers nothing and it moves no bar. The readings are SPEC's, the serving values are
`results/sku_pilot_serving.json`'s, the denominators are `results/sku_pilot_prereg_v2.json`'s (see
[[sku-b-pilot-readings-ratified]]), and the corners are `results/sku_projection.json`'s. It does
**not** authorise the paid session: sku-b-run is a separate contract, and under (10) it may yet
refuse itself before the first gold call. See [[5c1-vis-b-caption-instrument]] for why a position
layer exists at all, and [[srv2-program-close]] for the runtime and the rate the arithmetic above
is taken at.
