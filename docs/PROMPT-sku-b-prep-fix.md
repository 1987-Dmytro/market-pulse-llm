# PROMPT-sku-b-prep-fix — the cap discipline, hardened before the paid run ($0)

> Authority: SPEC §3.17 (10) — ratified at the sku-b-prep acceptance
> (operator, 2026-08-11) — plus the acceptance's fresh-context security
> review: 1 blocker + 4 nits, all in the money path of
> `scripts/positions_gm4_skub.py`. This contract is $0 and local: no
> pods, no endpoints, no templates, no /run calls. sku-b-prep is
> otherwise ACCEPTED; the phase closes when this pass lands.

## Read first (sections, not documents)

- `docs/SPEC.md` §3.17 (10) — new today; F1 and F2 implement it.
  Transcribe, do not redesign.
- `docs/reports/sku-b-prep.md` — your own report; the fix pass appends
  to it (see Report below).
- `results/sku_projection.json` — F6 regenerates it with one added term.

**On checkout, ONE test is red BY DESIGN, same mechanism as last time:**
the marker enumeration of `tests/test_sku_prereg.py` knows three names
and `docs/SPEC.md` now carries four. Step 0.2 adds
`sku-b-ratification-4`; green from there.

**Read-back check — FIRST lines of the fix-pass section:** F1–F6 one
line each, then the invariant "no paid calls in this contract".

## Step 0 (commits pre-authorised)

1. Team-lead docs commit, unedited: `docs/SPEC.md` (the -4 block),
   `docs/PROMPT-sku-b-prep-fix.md`, `docs/STATUS.md` (the 11.08-evening
   block).
2. `tests/test_sku_prereg.py`: enumeration gains `sku-b-ratification-4`.
3. **ADR** `knowledge/decisions/sku-b-serving-and-cap-discipline.md` +
   INDEX entry — the RECORD debt of the prep phase, named as such: the
   three joint-review ratifications behind 3.17 (9), the cap readings of
   (10), and the security blocker that motivated (10)(c), with artifact
   paths. English, template as usual.
4. Vault tail (fixed paths as usual) → its own final commit.

## Fixes (six; STOP and report if one runs deeper than briefed)

F1 **(blocker) One job must not be able to out-bill the cap — SPEC
   3.17 (10)(c).** `JOB_TIMEOUT_S` 1800 → **900.0** (≥2× the longest
   projected honest job — the 30-row text job at the stated corner is
   ~400 s; one 900 s job bills ≈$0.28 < cap). A job that ends
   `TIMED_OUT` (or times out client-side) ends the **RUN**, not just the
   batch: its items are forfeit under one-attempt, the remainder is
   recorded `unbought`, and the record is still written. Test: a
   TIMED_OUT job on the fake endpoint stops the run and the record says
   why.

F2 **Go/no-go after the warm-up — SPEC 3.17 (10)(a).** After BOTH
   non-gold warm-up calls, project the whole run (all 138 gold calls,
   each leg from its own warm-up-measured marginal, plus everything
   already billed, plus F6's idle tail); if the projection exceeds what
   is left of the $0.35 cap, REFUSE before any gold call: `SystemExit`,
   record written with `stopped_before_gold: true` and zero gold
   artifacts. Per (10)(a) that stop consumes NO attempt. Tests both
   ways: a cheap warm-up proceeds, an expensive one refuses.

F3 **A crash after the paid legs must not lose the run's record.**
   `spend_now` wrapped: on any subprocess/parse failure the record is
   written with `cost.usd: null` and a note naming the failure (the
   ledger anchor already survives, so the money stays recoverable).
   Test drives the failure.

F4 **Smoke redirects each defaulted path independently.**
   `--smoke --out X` must not write a fake record at the real
   `--record` default (today the redirect fires only when BOTH are
   defaulted). Test: the real path stays untouched.

F5 **An explicit `--project-stop-usd` TIGHTENS, never replaces.** In a
   ledgered run, `budget = min(args.project_stop_usd, remaining cap)` —
   a value above the remaining cap must not disable the in-run stop.
   Test.

F6 **The idle-timeout tail enters every projection.** Serverless bills
   wall uptime plus the endpoint's idle tail (~60 s ≈ $0.018 at the
   settled rate — larger than the stated corner's $0.0104 headroom). Add
   it as a named constant term inside `projected_usd`, the F2 go/no-go,
   AND `scripts/write_sku_projection.py`; regenerate
   `results/sku_projection.json` (legitimate: a projection is not a
   pre-registration, and the run has not happened) and update its tests.
   The corners move up ~$0.018 and the "over" corner gets worse — report
   it plainly, tune nothing.

Also, mechanical (standing delegation): the Verify table of
`docs/reports/sku-b-prep.md` says `make check` → 1728; HEAD's fact is
1734 — fix the prose in the fix-pass commit.

## Do NOT

- No paid calls, no RunPod resources of any kind (GOAL: the single paid
  session of 3.17 (6) is sku-b-run's, after this pass is accepted).
- Do not edit `docs/STATUS.md`, `docs/SPEC.md`, `docs/PRODUCT.md`,
  `docs/PROMPT-*.md` — team-lead files; commit-only.
- Do not re-pin `results/sku_pilot_prereg.json` / `_v2.json`; do not
  touch the two stale `max_new_tokens: 256` records (they are witnesses,
  not bugs to fix); frozen family, frozen sets, `baselines.json`,
  `spend_phase4.json` untouched.
- Never `git add -A`; vault tail → its own final commit.

## Report — evidence, not assertions

Append a `## Fix pass (Dv141+)` section to `docs/reports/sku-b-prep.md`
(own commit `docs(report): sku-b-prep -- fix pass`); chat gets ONLY the
path. Read-back lines first; per fix the test names and their run
output; the regenerated projection's four corners beside the old ones;
`make check` tail; Deviations Dv141+, explicitly "none" if none.
English. State your assumptions.
