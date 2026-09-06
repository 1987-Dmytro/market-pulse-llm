# PROGRESS — promo-pulse-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines; §8 of the phase file stays the DONE list)

## The money, live — nothing was spent this session and no line was opened
Cycle 3 **SPENT $6.2494, REMAINING $2.7506** of the **$9.00** ceiling (s28's reading, 15:28:28Z; NOT
re-read today — no guard command was run, see the stop). `promo-iter4` CLOSED **$0.694815**/$1.20,
`promo-holdout` CLOSED **$0.298209**/$1.10. **`promo-dev-loop` is the only open line and it REFUSES**
($2.5799 of its own $2.50, unbounded by construction (r)4) — **never named again**.
**`promo-iter5` is NOT anchored: `results/spend_promo_iter5.json` does not exist.** That is the stop.

## Done — 06.09 s29: ruling (x)'s $0 prep, everything except the registration.
- **Team-lead files by path:** ruling **(x)**, its stop-pattern row, STATUS 19:40 (`d2060b9`);
  **PROCESS «Money» v2** (`26582d8`), which arrived mid-session and independently states three of the
  four fixes below as general law. `knowledge/` s28 (`e61ce6b`). All of the below is `39022ac`.
- **(x)3 the card — a FIELD of the record, not a constant.** `CARD = "…RTX 4090"` was a literal
  `offered_price` matched by hand, so «≥ 32 GB» was a ruling no code could obey. `CARDS` is (w)2's
  order; `offered_price(cards)` takes the FIRST with ≥ `MIN_VRAM_GB`, stock in EU-RO-1 and a dearer
  offer ≤ $0.90/h. Both names come off ONE listing row: `displayName` matched **EXACTLY** (the `SE` twin is another card at the same price) and `gpuId`, which `pod create` / `--open --card` take.
- **(x)3 the backstop.** `terminate_after_minutes` = the CAP's own minutes at the registered price,
  **116 min**, against v5b's borrowed **90** — which would have killed a FITS run at $1.08. The
  record carries both and says which is live; `terminate*60 ≤ hard_stop` holds in both directions.
- **(x)4 the ERROR reply, read everywhere replies are read.** `reply_rows` goes through the pod
  runner's own `whole_lines`, so a torn LAST line (the scp race off a LIVE pod) is **WAITING**, not a
  traceback on the command that decides whether a billing pod is deleted. `answered_rows` drops a
  dead unit and `--close-segment`'s rate row, `--project` and `--score` count it **UNANSWERED** — the
  money gate is appended BEFORE that row is written. A death is not a parse failure: `dead_units`
  names it and all three print it.
- **`ITERATION = 5`; `re_emission` discloses** the card, its gpu-id, its price and
  `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`. **The runbook is re-pointed** off every
  `_holdout` path onto iteration 5: part dev, `_iter5` files, `promo-iter5` $1.40, the gpu-id, the allocator in the launch line, `--smoke` + `pgrep`, two-arm `--score`, the v13 close.
- **Checks. `runpodctl gpu list` at $0:** `RTX PRO 4500`, **32 GB**, `NVIDIA RTX PRO 4500 Blackwell`,
  **$0.72/h** secure, EU-RO-1 stock **High**; A6000 48 GB $0.53 has stock `none`, L40S is absent.
  **Rung 0 priced at $0, writing nothing:** mean **$0.8470** (−39.5 %) · priced $0.9028 ·
  dear $4.8633 → **FITS on the mean**, hard stop **7000 s**. `ruff` clean; `pytest` **4323 passed,
  2 skipped, exit 0** over both slices (§8 (j) wants ≥ 4266). **ONE test added** — (x)3's backstop,
  both directions; (w)3's ONE test **extended** with (x)4's four readings (torn last line ·
  `id: null` death · the rate row · the grader's count).

## Open stop — the registration ANCHORS the line, and the anchor's age decides the close
**Stop-point.** `--register --step promo-iter5` calls the guard, which CREATES
`results/spend_promo_iter5.json` and anchors it at today's balance. Ruling (x) puts that in the prep
session and the pod in the NEXT one; PROCESS «Money» v2 opens the line «BEFORE the pod» at §0 of the
paid session. They disagree about when the anchor exists, and the gap is money.
**Why it matters, measured.** The close settles on `own_resources` (always-on kinds OUT) while its
tolerance reference is the post-run `--note`, a balance delta with them IN — so the drift is the
anchor's AGE, and it is measured, not modelled: `promo-iter4` settled $0.694815 against $0.7143,
and $0.7143 − $0.694815 = **$0.019444 = its `network-volume` line, exactly**; its whole 2.73 % was
the volume over 2.45 h. At $0.0079/h and this leg's $0.85 of pod, **5 % is reached at ≈ 6 h**, and a
cheaper pod sooner. Register tonight, buy tomorrow → the close **REFUSES** and `promo-iter5` joins
`promo-dev-loop`. **`--since` cannot help:** `recorded_reading()` is the note's own `step_spent_usd`.
**The question (yours — money, and a fourth spelling of the close rule).** Which:
(i) the pod follows the registration inside ~6 h — the operator's word on timing, nothing else moves;
(ii) `--register` moves INTO the paid session (PROCESS v2's own order), prep ends at `--dry-run`;
(iii) the never-used `spend_promo_iter5.json` is deleted before the paid session anchors it.
**Tree.** Clean; `make check` 4323/2 exit 0 at `39022ac`; $0 spent, no pod, no guard call, no ledger line.

## Named, not built (the phase file forbids adding what it did not ask for)
- **§6.5's $0 fit proof** — the smoke's longest unit stands in for it at minutes' cost.
- **`--open`/`--close-segment` write the run record at BATCH scale** — `--expect-ms` and `STOP_AT`
  filter segments to `created_at >=` the line's anchor; now written into the runbook's own code.
- **No test for the arm selector** (§4) or the step-aware guard read ((v)3 «no new test»).
