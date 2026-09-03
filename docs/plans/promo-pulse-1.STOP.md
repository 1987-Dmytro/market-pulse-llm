# STOP — promo-pulse-1, 2026-09-03 (the fifth; the fourth was answered by rulings 02.09 (d) + 03.09 and deleted)

**Stop-points, in order of size:** a design fork the plan does not settle · a test that would have to be weakened ·
waiting on the team lead's labels (positions-50). **No money question and no rung fired.** Ruling 02.09 (d) shape 1
is IMPLEMENTED and the C2 window is in `pulse.db`: `w1` re-derives **902/902** numeric leaves of the sealed
`results/window_summary_5c2.json`, 0 disagreed, 0 missing, and `w2` carries **17 channels · 3 397 markers · 1 113
positions**. What the ruling could not foresee is that shape 1 alone does not restore w1's SEALED artifacts.

## Fork 1 — w1's sealed records pin FILE hashes of a store that now holds two windows

The C2 run wrote into the SAME per-channel files (`data/derived/leaflet_pages/atb_market_official.jsonl` is 368 lines
where the seal hashed 159). Every w1 record that says «what bytes made this» therefore moved, and no fixture can reach it:

- `tests/test_window_summary_5c2.py` (2 red) — `test_the_record_carries_the_producer_and_every_source_it_read` asserts
  `set(record["sources"]) == everything`, where `everything` is a LIVE glob of `summary.DERIVED`, and then hashes each
  file live. It reads the committed record and a module constant: no fixture and no producer edit can reach either half.
- `tests/test_export_dashboard_data.py`, `tests/test_build_dashboard.py`, `tests/test_build_validate_pack.py` — the
  same, one layer up, and MEASURED leaf by leaf rather than eyeballed: today's `dashboard_data_w1.json` differs from
  the committed one in **55 leaves (20 changed + 35 new) and every single one is under `provenance.*`** —
  `provenance.evidence`, `provenance.inputs`, `provenance.producers`. **0 differing leaves outside it**, and the 4 474
  data leaves are identical (145 position rows, 902/902 anchor leaves, 30 shared figures equal). The record's numbers
  did not move; its statement about which bytes made it did.
- **So the ruling's own check «the `w1` export sha is byte-identical before and after» cannot hold** under one shared
  derived root. The MIRROR half of that check does hold and is shown above.

**The two shapes, and the second one is MEASURED, not hoped.** (1) The team lead re-scopes those claims: a sealed
record's `sources` is a statement about the run, not about today's directory, and the tests read it that way.
(2) The derived store splits — `data/derived/` returns to being 5c2's, C2 gets its own root, both windows still build
into the one DB (the 20 D-cut posts are read from w1's root). **The C2 run only APPENDED**: I checked every one of the
38 sealed sources against today's bytes — **23 unchanged · 15 an exact byte PREFIX · 0 diverged** — so the split
restores every sealed hash exactly and is verifiable in one command. I did not take it: plan S4 names `data/derived/`
as the write target, and where the sealed evidence root lives is the team lead's line, not mine.

## Fork 2 — `positions` cannot tell the image row from the text row, and the plan says it is untouched

Seven C2 posts were read by BOTH legs (`@ekomarket_shop:1465`, `@VARUS_channel:11300`, …): the producer's
`row_id` is `channel:msg_id:ordinal` and carries no carrier, so `PRIMARY KEY (window_id, row_id)` refuses two genuine
rows about one message. I added `carrier` to that key (and to `position_warnings`, which the warnings JOIN needs) —
**no stored id moves and w1 is untouched by it** — and `tests/test_promo_tables.py::test_positions_is_untouched` is RED
for exactly that, named and not weakened. The alternatives both lose: rewriting `row_id` moves a sealed export's rows,
dropping one leg's row throws away evidence that was paid for. If the ruling prefers the test's claim, say which row goes.

## What is DONE and shown in the transcript

(a) `promo_pagecount_c2.json` — 17 channels, 3 008 pages exact, from store/metadata; `promo_projection_c2.json` —
`c2_priced_usd` **$3.1563** as ONE number at the marginal (`the_one_number_usd` $7.2621 is the boot-inclusive ceiling).
(b) `collect: false` honoured, both directions, `tests/test_collect_5c1.py` 23 passed. (c) positions per channel in
`pulse.db`, spend lines named below. (d) the 50 re-drawn over the C2 population, twice, sha **`61b4fda7fdc83197…`**
— **the positions-50 labels are owed against THIS sha**. (f) `tests/test_trends_sql.py` 10 passed. (g) `make tick`
twice: attribution/signal/evidence/digest/unsure 0→0, rollup 401→401, **zero new rows per table**. (h) clean clone:
`make tick && make promo-screen` exit 0; source removed → exit 2, «promo-screen REFUSED: missing source …». (i)
`draw_truth_20.py` 20 rows, seed 42. (l) porcelain clean on the contract paths.

**Ruling 03.09 is applied and its $0 gate is READY FOR YOUR READ.** `promo_prompts.CODEBOOK` carries all six deltas,
`codebook_version()` = `a97d3c71b8cf9b14…`, no test assertion weakened (none pinned a literal sha). The RENDERED prompt
for `@VARUS_channel` root `6009` is in the transcript; `python3.11 scripts/promo_dev_pass.py --render 6009` reprints it.
The gold went through all four hooks as a fixture: **140 about rows and 84 signal rows, 0 failures**, 140 of 140
comments with text covered, 0 lines on a wordless comment. **S9 iteration 1 is not started: the ruling puts your read
of that rendering before the first paid K8 call.**

**And the ask is bounded so you can rule on the rendering and the money in one read.**
`scripts/promo_dev_pass.py --dry-run` → `results/promo_dev40_prep.json`: the codebook's sha and version beside the
vocabulary the prompt closes, the gold's sha and 140 lines, the draw's sha, and all 40 renders with their sizes —
**209 897 chars, longest 8 047, 40 distinct renders**. The seconds are a BOUND and the record says so in its own field:
this instrument has NO measured rate, so they are borrowed from `pass2_r2_seconds_per_thread` (23.76 s over 75 cooled
threads, thinking off — another prompt, another pod, another transport). **$0.2915 at that mean · $1.659 at its max**,
boot excluded, against the dev loop's $2.50: one iteration fits at either corner, and FIVE fit only at the mean
(5 × $1.659 = $8.30 does not). The smoke replaces the borrow before anything is bought.

**The GRADER is proven against the shipped gold, four directions, $0 — so iteration 1 measures the model, not the
plumbing.** Gold against itself **1.0 / 1.0**, both bars HOLD and both strata read 1.0. Every subject replaced →
subject **0.0 RED** while signals stay 1.0: the two bars are INDEPENDENT and neither carries the other. Every signal
stripped → signals **0.15 RED** while subject stays 1.0 — and **0.15 is exactly 6/40**, your own «6 of 40 threads have
an EMPTY signal set» re-derived by a different instrument. Silence → **both RED**, which is what «an abstention is an
answer» has to mean in a number. All four live in `tests/test_grade_promo_signals.py` with the share DERIVED, never
typed, so a drift between your gold's schema and the grader's reader goes red before a pod exists.

## `make check`, and it is now a clean statement

**13 failed · 4 268 passed · 2 skipped · 7 errors in 732.67 s**, measured at `6b6fe44` — 20 red against the 35 of
the last report, **+21 passed**. Check (j) has two halves and the COUNT half is MET — **4 268 ≥ 4 266** — so the
only thing holding (j) is green-ness, and that is the two forks. **Every red is one of the two forks above:** 19 are fork 1 — `test_build_dashboard` (7 errors + 4 failed),
`test_build_validate_pack` (4), `test_window_summary_5c2` (2), `test_export_dashboard_data` (2), each a w1 record whose
provenance names the store as it was sealed and refuses on a C2 file («`data/derived/position_rows/ATB_FANatik.jsonl`
is not in the export's provenance.evidence») — and 1 is fork 2. Nothing else is red. The 7 reds the new `--window w2`
default caused in `test_draw_positions_50` and `test_tick` were MINE and are FIXED: both helpers now NAME the window
their own fixture builds rather than riding a production default. Nothing weakened, no test file deleted, and the only
test changed to pass is the one ruling 02.09 (d) names.

## Two findings beside the money, and one number I refused to invent

1. **16 of the 405 pinned C2 posts have no evidence row** (14 `@epicentrk_sale`, 1 `@ekomarket_shop`, 1 `@forainfo`);
   all 16 are in the store with real text. `runs[1].unbought` reads 0/0 and `runs[1].post_text` is `[]` — the post
   leg's detail block was lost to the two harness kills, so that 0/0 is a claim about the PAGE stages only. Re-asking
   them is ~16 × 0.845 s ≈ $0.004 of compute plus a boot (~$0.065). Not bought: it is a new paid leg.
2. **Five channels have 0 positions and it is an ANSWER, not a gap** — `@epicentrk_sale`, `@fozzyshopua`, `@kop1chat`,
   `@kopiyochka1`, `@rrozetka`: every page and post was answered (`unreadable` 0) and `n_positions` sums to 0. They
   are DIY, coupon-aggregator and electronics channels; the dairy/ice-cream parser found nothing to write.
3. **The step is not closed.** `--close --tolerance` needs a FRACTION and the plan names none: the ledger's own
   readings sum to **$3.0934** ($0.0599 run 1 + $3.0335 run 2, `results/spend_promo_pulse_1.json`) and the guard settles
   the step at **$3.1909** by delta / **$3.1812** by the walk — a 3.15 % gap that is the always-on volume. A threshold
   I pick is a scope change; name it and the START RITUAL closes the step.

Money, unchanged and read today: `PROMO-PULSE-1 SPENT $3.1909 of $3.95` · `CYCLE 3 SPENT $3.4826 of $7.00` ·
`REMAINING $3.5174` — the dev loop keeps its full `min($2.50, …)`. Nothing was created and nothing was bought today.
