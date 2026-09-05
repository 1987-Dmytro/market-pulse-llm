# PROGRESS — promo-pulse-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines; §8 of the phase file stays the DONE list)

## The money, live — read BY HAND from the guard today, never carried from a record
Cycle 3 **SPENT $5.5059, REMAINING $3.4941** of the **$9.00** ceiling of ruling (s) addendum 8; the anchor
$14.4800, `anchored_at` and every session line are UNMOVED — the raise lifts a fence, not the balance ($8.97
on the account). **s23 spent $0; no pod was created.** `promo-holdout` $0.296617, ledger OPEN; `promo-dev-loop` open by (r)4.

## Done — 05.09 s23 «v1.2-prep», ruling (s) item 5 (b), four commits, all $0
- **The ritual's money edit** (`a6868e5`): `CYCLE3_CAP_USD = 9.00` with the ruling in its docstring, the
  ledger's cap and its APPENDED note, `read_cycle3`'s stale «(now $7.00)» replaced by the constant's own
  name. No test moved: the tripwire fixtures carry their own 4.8 and `GUARD_SAYS` is a canned stdout.
- **holdout-2 is drawn** (`4a03307`) by PARAMETERS on the same producer (§4), not a fork:
  `--arms holdout=20 --exclude-drawn results/promo_threads_draw.json --drop-paused`. The two exclusions
  OVERLAP — the two `@matusi_ukr` threads of holdout-40 are in both — so the population is
  `eligible − union`: 12 eligible in paused channels + 80 drawn = **90 removed, 398 left** (137 / 261).
  **Draw 1 replays BYTE-IDENTICAL** (`cmp` clean, `6f9fa245b9d70254…`), draw 2 as itself (K7). Sets **40 /
  40 / 40**, 20/20 per stratum, all three intersections **0**, `@matusi_ukr` (21 of the 53 misses) out.
- **K8 v2** (`0224167`) — ONE pairwise `subjects_agree()` that the grade AND the error table call, so one
  record cannot disagree with itself: exact first, then token-Jaccard ≥ 0.5 for `sku`/`brand` only, and
  `k8_version` is IN the record. **Measured, not promised:** on holdout-40's frozen gold the alias buys
  **0 rows** and K8 v2 **1 of 188** (0.7181 → 0.7234, the v1 record untouched) — the rest of the form
  misses are single-token pairs a Jaccard cannot overlap.
- **The law re-rendered from codebook v1.2** (`4be406e`): partner → `chain` (never `brand`), new rule 11
  for an off-domain thread, rule 4's three product forms, the «а X де?» pair and the argument jab, (д)
  price-as-quality → `цена` alone, the near-quote «Шикарно…» out, three synthetic EXAMPLES, and
  `chain_aliases.yaml :: silpo` gains «Сильпо» (a NAME form under (j)1). Every literal is a PARAPHRASE — the
  codebook may quote gold, the law may not. **`--leak-check` CLEAN over all three sets: 440 comments (140
  dev-40 + 188 dev-2 + 112 holdout-2)**, 30 + 10 literals, 0 hits. Law pins MOVED as ordered: codebook
  `a587e0d6…` → **`0bbb665a…`**, template `57dd9d25…` → **`32fa6c42…`**; the corpus test reads 140/188 off the committed records now (§6.6).

## Next — the iteration-4 registration and its pack, BLOCKED by the stop below; nothing else is.
On the answer: leg-A arms (dev-40 first, dev-2 after), `ITERATION = 4`, `--dry-run` → `--register` → commit → `--pack` (it greens the red test) → iteration 4.

## Open stop — $0.60 and rung 0 cannot both hold: iteration 4 is unregisterable as ruled
**Shown, to scratch, the committed registration untouched:** `--register --part dev --cap 0.60` REFUSES —
43 units, dear corner **$1.3100 vs $0.6000, +118.3 %** — and the dev leg has no mean-corner fallback
(`rung_0` jumps dear→mean only when `part != "dev"`), so that is a refusal, not a reading. Priced for the
real iteration-4 population (3 smoke + 80, RTX 4090 $0.74/h, overhead 279 s) — cheap · priced · dear:
  borrowed `pass2_r2` 23.760/135.232 (what `rate_for("dev")` returns) → 0.4627 · 0.5201 · **2.4219**
  own `promo_dev40` 88.772/201.967 (the ONLY row in `measurements.jsonl`) → **1.5719 · 1.6292 · 3.5605**
  the holdout pod's 25.826/149.054 (never written, below) → 0.4980 · 0.5553 · **2.6577**
**(1)** PHASE v9 §6.1 calls iteration 4's only money gate «rung 0 FITS + the hard stop (ruling (r))» — is
that (r)2's pair on THIS leg, i.e. issued on the MEAN corner? At the dear corner NO rate fits $0.60.
**(2)** At which rate? `own_rate()` answers 88.772, where no corner fits and the 2919 s hard stop CUTS the
run (7647 s needed); the 25.826 this instrument measured never reached `measurements.jsonl`. May that row
be written from the run record at $0 — or does the cap move? **(3)** The dev decision table's bands
($0.80 / $1.20) all sit ABOVE a $0.60 cap; §4 v8 says such a field branches or the emitter refuses.
**Tree:** four commits, `git status` clean, no pod, no spend, one red test named below.

## Named, not built (the phase file forbids adding what it did not ask for)
- **ONE RED TEST, and it is the stop's:** `test_the_pack_pins_exactly_what_the_pod_re_derives` — the pack
  on disk is iteration 3's and this checkout renders the law the lead ordered re-rendered. It greens when
  the pack is rebuilt at iteration 4's registration; §8 (j) forbids touching the test, so it stays red and
  named. `make check`: ruff clean · pytest in three slices (1000 + 2027 + 1293) → **4320 passed, 1 failed, 2 skipped** — §8 (j)'s floor is 4266.
- **The holdout's measured rate still never reaches `measurements.jsonl`** — `write_measurement()` is
  called ONLY from `--project` and (r)2 does not run it. Now load-bearing: it is half of question (2).
- `gates.terminate_after_minutes` is v5b's borrowed 5400 s · a later field is unbranched until noticed ·
  holdout branches carry no test (§4 forbids one) · `prep()` calls its count `draw.dev_threads` · `pod.main`
  never lifts `close_arrays_too` · `committed_registration()` ignores `pinned_inputs` · `check_law` compares
  `codebook_version` ONLY, so the moved TEMPLATE passes the pod handshake · gold 140/208 · `1925810730`.
