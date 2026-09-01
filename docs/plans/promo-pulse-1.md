# PLAN — `promo-pulse-1` (C2–C5), executor's plan for `docs/PHASE-promo-pulse-1.md`

Written under `/plan-phase`. Nothing is implemented until the operator relays the team lead's «go».
Every number below names the file it came from; none is typed.

## 1. Question and the artifact that answers it

> «Что и почём промоутируют сети по молочке и мороженому, и как покупатели на это реагируют —
> неделя за неделей?» (`docs/PHASE-promo-pulse-1.md` §1)

The artifact: ONE promo screen built by `make tick` + `make promo-screen` from result files only —
per week × chain: promo positions (brand · product · volume · promo price · depth), price trend per
SKU, and the reaction feed (signal · quote · `msg_id` · thread) — plus the tables behind it in
`data/derived/pulse.db`.

**The one contested column of §1's artifact is now RULED — SP-0 q2, and the phase spec §1 was
corrected with it.** §1 as written named `price old` as a screen column. `docs/SPEC.md` amendment
3.21 (4) says «the extracted old price is never printed», 3.18 (1) says it «never reaches a
surface that prints it as a price», and 3.22 (1) keeps arithmetic depth out of any row that shows
its own promo price, because `promo ÷ (1 − depth)` reconstructs the old price. Those rulings rest
on a measurement SPEC v2 does not move: the extracted old price is right as a number on **33 of 80
pairs** (`results/sku_bar_verdicts_skub2.json`, bar 2 = 0.4125 against 0.80). The team lead ruled
with those amendments: **the screen does not print `price_old`**, the row is brand · product ·
volume · promo price · printed `−N%` (absent when none), and depth per chain and brand is a
**window aggregate** only (3.22 (1)). So `price_old` is **stored and flagged** — the column
already exists in `positions` — and never rendered. This was the difference between storing and
printing, and it is settled.

## 1a. What needs an answer, and what can start without one

| | |
|---|---|
| **Answer FIRST — the phase does not fit its money (SP-1)** | The live guard reads **$2.4394** remaining, not $3.17; the phase's own estimate table is $3.20, and the volume eats $0.2333/day. Choose: **(a)** open cycle-3 and name the sum · **(b)** narrow C2 and say which chains are dropped · **(c)** pay to build a positions **pod** runner (2.383× cheaper per 1 000 rows). |
| **~~Answer before S7~~ — ANSWERED (SP-0 q3)** | Operator, 30.08: «Все 678, дро 20/20 по типу». Population = all 678 (a promo post whose price is in the image IS a price post); the draw is 20 + 20 by branch stratum, not by channel. S7 is unblocked and joins the $0 slice. |
| **Answer at review, cheap** | SP-0 q1–q2 (the S1 price bar's denominator; whether the screen prints `price old`) · SP-5 (my proposed five-table schema) · and **two mechanism changes I made myself**: S1a widens the handle regex to a union, §5.2b makes «paused» a `collect: false` flag instead of a removed row. |
| **«Go» needs no answer at all** | **S0 · S1a · S1b · S2 · S3 · S6 · S7 · S8** — the whole $0 scaffold: the debt fix, the loader, the revision, collection, the census, the six tables, the draw, the instrument, hooks and graders. S7 joined it when q3 was answered. |

## 2. Checks

Graders first, mechanics after. A check I cannot run today is marked **[BLOCKED]** with its blocker.

| # | command | pass condition |
|---|---|---|
| K0 | `make check` | ruff + pytest green. Baseline **measured, twice, independently**: `1 failed · 4 129 passed · 2 skipped`, `ruff check .` clean, `make: *** [check] Error 1`; `.suite-stamp.json` carries the whole-suite run at `81af568`. The one red is pre-existing and not mine: `tests/test_repair_phase4_ledger.py::test_the_silence_check_fires_on_the_LINE_ledger_too` — the silence-check reads the LIVE `results/spend_cycle2.json`, which grew past it (the repo's own `[[a_sealed_reports_checker_reads_a_live_file]]`). `docs/STATUS.md` assigns it as the $0 debt of the next contract's step 0, so **S0 fixes it**, by asserting what the check was really protecting rather than by deleting the assertion. |
| K0s | `make check-stamped` | the same reading with a proof the tree did not move under it. **The K0 counts above are NOT a HOLDS-at-HEAD baseline**: HEAD moved twice mid-run (this plan's own commits), and `scripts/check_stamped.py` voids on a HEAD change alone — its whitelist is only `knowledge/daily_logs/` and `knowledge/index.md`. The counts are still trustworthy as a reading (no test reads `docs/plans/**`, and `hot.md`, the one suite input outside the whitelist, did not move), but the Baselines block of every step quotes **K0s at a settled tree**, never K0. |
| K1 | `make preflight ARGS='config/registry.yaml'` | run BEFORE and AFTER S1. `config/registry.yaml` is pinned by **21 sealed records**, live sha `d4e3b2373c43…`. After the edit every record pinning the old sha is claimed through `tests/moved_pins.py` (derived from live shas, both directions) — **never re-pinned**. |
| K2 | `PYTHONPATH=src python3.11 -m market_pulse.registry config/registry.yaml` | r2 loads; source count and the A1/A2/PAUSED split are what §3 of the phase spec names. |
| K3 | `python3.11 scripts/promo_census_c2.py` → `results/promo_census_c2.json` | $0. Per channel over the 4-week window: posts, leaflet **pages**, text-price posts, `media_share`, and a `selection.ids_sha256` pin. Pre-registers the paid population **by row count**, never as a date range evaluated at run time (SPEC 3.18 (4)). |
| K4 | `python3.11 scripts/promo_projection_c2.py` → `results/promo_projection_c2.json` | $0. Emits a **range, not a number**: K3's page count × each of the three candidate rates (1.729 warm-up marginal · a fitted middle · 10.408 realised) × $/s, against the guard's freshly re-read remainder. It cannot emit a single figure — `results/measurements.jsonl` has **no vision s/page row**, and the projection precedent hard-exits on a missing named rate (`scripts/project_think_zero_shot.py:107`: «the smoke writes it — project nothing until it has»). The range IS the table SP-1 asks the operator to choose against; the single number arrives only after S4's smoke seeds the row. This is a STOP, not a pass/fail. |
| K5 | `python3.11 scripts/draw_positions_50.py` twice | `results/positions_draw_50.json` — 50 positions, seed 42, from ≥3 chains' flyers/posts of the backfilled 4 weeks; two runs produce an identical sha. Handed to the team lead. |
| K6 | `python3.11 scripts/grade_positions.py` → `results/grade_positions_50.json` | completeness ≥ 0.90, price accuracy ≥ 0.95. **[BLOCKED]** on `docs/labels-positions-50.jsonl` (team lead's, owed after K5) and on SP-0's answer, which fixes the bar's denominator. |
| K7 | `python3.11 scripts/draw_promo_threads.py` twice | `results/promo_threads_draw.json` — dev-40 + holdout-40, **disjoint and frozen at the draw**, seed 42, over **all 678** price threads re-derived by `PRICE_BRANCHES`, stratified **by branch**: 20 from the currency stratum (229 threads matching `грн|₴|grn`) + 20 from the `decimal`-only stratum (449), and holdout-40 the same 20/20 (operator 30.08, review SP-0 q3). Each stratum owes 40 of the 80 across both draws, so 229 and 449 both clear it; a quota that could not be filled is a **refusal**, never a short draw. Channel is a recorded field per thread, not a stratum. The record names the strata, the predicate and the **wordless-comment count the queue rule removed** (§5.6). Two runs identical by sha — the record is sorted and carries no clock. Handed to the team lead. |
| K8 | `python3.11 scripts/grade_promo_signals.py` → `results/grade_promo_dev40.json` | subject agreement ≥ 0.80 · signal-type agreement ≥ 0.75 on dev-40. **[BLOCKED]** on `docs/labels-promo-dev.jsonl` (team lead's, owed after K7). |
| K9 | `pytest tests/test_trends_sql.py -q` | S3 recomputed from `positions` twice → identical; a week with no data renders **absent**, never `0`. Asserted in both directions. |
| K10 | `make tick && make tick` | second run writes **zero** new rows. Asserted per table by count before/after, not by a global total — an aggregate counter cannot see a per-row change. The per-table counts are all **six** of §5.7 — `attribution`, `signal`, `evidence`, `digest`, `unsure`, `rollup`: `unsure` is written by the same pass and an idempotence check that skipped it would leave the abstention path unmeasured. |
| K11 | `pytest tests/test_promo_hooks.py -q` | between calls: `msg_id` exists · quote is a substring of the source text · brand ∈ registry or the store's unresolved state (§5.9) · schema valid. A hook failure is a **counted row**, not an exception — asserted with a negative control (a row that must fail and be counted). |
| K12 | `make promo-screen` on a **clean clone** after `make tick` | the screen renders from result files only and **fails loudly** on any missing source. Negative control: remove one source, assert a non-zero exit and a named error. |
| K13 | `python3.11 scripts/draw_truth_20.py` → 20 rows, seed 42 | flyer/post · extracted position · comment · signal · quote, rendered for the operator. The gate is his words, not a number. |

End-to-end (closes the phase) = K12 then K13, in that order.

## 3. Steps

Each ends in a commit **by path** and the checks named. No `git add -A`; no repo-wide `make fmt`.

| # | what | files | check |
|---|---|---|---|
| S0 | Commit the team lead's uncommitted files by path (`docs/STATUS.md`, `docs/PHASE-promo-pulse-1.md`); clear the `test_repair_phase4_ledger` debt STATUS assigns to step 0 of the next contract. | commit by path only; `tests/` | K0 |
| S1a | **Loader extension first** (§5.2a): two of the 17 A1 rows **cannot be expressed** under today's `_HANDLE` regex. `src/market_pulse/registry.py` is pinned by nothing, so this is a cheap, legal prerequisite — a `chat_id` / `invite` field beside `telegram_channels`, with the regex left intact for real usernames. | `src/market_pulse/registry.py`, `tests/test_registry.py` | K2, K0 |
| S1b | **Registry revision r2.** 17 A1 rows · 5 A2 · PAUSED 39 leave collection · B deferred. Preflight, edit, then claim the moved pins. Of the **18** A1 entries §3 names (17 rows + ATB_FANatik's discussion group), **8 are in the registry and 10 are not** — recounted from `config/registry.yaml` against §3's list, printed in §5.3a rather than asserted as a total: the 10 absent are `@ATB_FANatik`, its discussion group, Маркетопт private, `@blyzenkoua`, `@fozzyshopua`, `@sim23_simi`, `@rrozetka`, `@kop1chat`, `@znishkom`, `@xochydeshevshe`. **`@atb_market_official` stays in collection** (review 30.08: it is the leaflet carrier — 159 pages, 106/145 positions — and dropping it would cut the one proven S1 source); only the PAUSED 39 leave **collection**, and their registry rows **stay** — §5.2b: removing them makes the aggregates build refuse at $0. Every new row needs an `audience` from the closed list of 8 — `test_every_shipped_source_carries_an_audience` forbids a null. | `config/registry.yaml`, `tests/moved_pins.py`, `tests/` | K1, K2, K0 |
| S2 | **$0 collection, into the live root `data/raw_r2/` (§5.14).** The population §1 measures does not exist on disk: the newest post across every A1 channel is **2026-08-08** (today is 2026-08-30, so ≥22 days of the 4-week window are uncollected for *every* channel), and **8 of the 18 entries have no store file at all** — the 6 missing handles plus Маркетопт private and the discussion group. Collect them, top up the rest to the window, and collect the `@ATB_FANatik` discussion group (its traffic is measured at entry — r1's 0.25 c/day read post replies, not the group feed). Every NEW channel enters through the adaptation protocol: profile → sealed hundred → gate **before** aggregates. Telegram only. | `scripts/`, `src/market_pulse/raw_store.py`, `data/raw_r2/`, `results/` | K0 |
| S3 | **$0 census + projection** of the paid legs (K3, K4) over the window S2's top-up fixes (§5.1), then **STOP** — SP-1, decided on this table. The two paths go to the operator the moment they exist; S6/S7/S8 continue meanwhile, since none of them is paid. | `scripts/promo_census_c2.py`, `scripts/promo_projection_c2.py`, `results/` | K3, K4, K0 |
| S4 | **C2 backfill (PAID).** Positions for the 17 channels over the 4 weeks, via the existing 5c2 instrument — vision for image flyers, text for the rest. **`positions.py` is not touched** (§5.12): the scale is in which carriers get fed, not in the parser. Smoke first; rungs per `docs/PROCESS.md`. | `scripts/`, `results/`, `data/derived/` | K0 |
| S5 | **S1 draw** (K5) → hand `results/positions_draw_50.json` to the team lead for `docs/labels-positions-50.jsonl`. | `scripts/draw_positions_50.py`, `results/` | K5, K0 |
| S6 | **The six new tables** — `attribution / signal / evidence / digest / unsure / rollup`, uuid5 ids over normalised keys, `window_id` in no identity but `rollup`'s week (§5.7, the review's amended schema). `aggregates.py` extended; `positions` untouched. | `src/market_pulse/aggregates.py`, `tests/` | K0 |
| S7 | **C3 step 0.** Enumerate the 678 price threads (the yield file carries **counts only, no ids** — see §5.5), split them into the two branch strata (229 currency / 449 `decimal`-only) and draw dev-40 + holdout-40 at 20/20 each (K7) → hand to the team lead. | `scripts/draw_promo_threads.py`, `results/` | K7, K0 |
| S8 | **Instrument + hooks + graders**, all $0: a NEW prompt module (`prompts.py` is pinned), the four hooks, `grade_positions.py`, `grade_promo_signals.py`. Graders are written and unit-tested against synthetic gold before any real gold exists. | new module in `src/market_pulse/`, `scripts/grade_*.py`, `tests/` | K11, K0 |
| S9 | **C3 dev loop (PAID).** 3–5 iterations × dev-40. Thinking OFF, batch 1. Plateau → SP-3. | `scripts/`, `results/` | K8, K0 |
| S10 | **The ONE holdout shot (PAID)** — pre-registered first (SP-2), then spent once. | `scripts/write_promo_prereg.py`, `results/` | K8, K0 |
| S11 | **S3 trends, SQL only, no LLM.** Price per SKU per week per chain; depth per chain and brand. | `src/market_pulse/aggregates.py`, `tests/test_trends_sql.py` | K9, K0 |
| S12 | **S4 the loop.** `make tick`, `data/schedule.json` (READ only), `loop.py` cursors, the cooled-thread digest and the late-comment delta. | `Makefile`, `src/market_pulse/loop.py`, `tests/` | K10, K0 |
| S13 | **C5 the screen.** `make promo-screen`, one promo view, result files only, loud failure on a missing source. | `dashboard/`, `scripts/build_dashboard.py`, `Makefile` | K12, K0 |
| S14 | **End-to-end + the product-truth gate**: clean clone, `make tick && make promo-screen`, then the 20 rows for the operator. | `scripts/draw_truth_20.py`, `results/` | K12, K13, K0 |

## 4. Stop-points — asked BEFORE, never reported after

**SP-0 — ANSWERED at the plan review (`docs/reviews/2026-08-30-plan-promo-pulse-1.md`,
«Рулинги»). All three, so nothing on the $0 path waits.** The questions as asked, each with the
ruling that closed it:
1. Does S1's `price accuracy ≥ 0.95` denominate over the **promo price only** (the green leg, 80/80
   in `results/sku_b_pair_verdicts_skub2.json`) or over the **price pair**? At the pair the bar is
   unreachable by measurement — 0.4125 — and the gold file that fixes the denominator is the team
   lead's to write. → **ANSWERED: the promo price only**, exact after normalisation. Completeness =
   gold positions matched on (brand surface form, product, volume) by a match rule the grader
   states. The printed `−N%` and the extracted old price are stored and reported as **readings, no
   bar**. `docs/labels-positions-50.jsonl` rows: `row_id · brand · product · volume · price_promo ·
   badge_pct (nullable) · price_old (nullable, unscored) · note`.
2. Does the §1 screen **print** `price old`, against 3.21 (4) / 3.22 (1)? I store it either way.
   → **ANSWERED: no.** The screen row is brand · product · volume · promo price · printed `−N%`
   (absent when none); depth per chain and brand is a **window aggregate** (3.22 (1)), never beside
   a row's own promo price. `price_old` stays stored and flagged, exactly as today — the phase spec
   §1 was corrected to match, so §1 of this plan is no longer contested.
3. **Which population is S2 graded on** — 678, 229 or 449 (§5.5a)? Two thirds of the 678 are
   selected by a regex matching **dates**, not prices, and the operator's ruling says «только треды
   под ЦЕНОВЫМИ промо». → **ANSWERED by the operator, 30.08: «Все 678, дро 20/20 по типу».** A promo
   post whose price is in the image is a price post, so the population is **all 678** and the
   `decimal` finding becomes a **stratum**, not a cut: dev-40 = 20 currency + 20 `decimal`-only,
   holdout-40 the same 20/20, disjoint, frozen at the draw, seed 42 (K7, §5.5a–b). Bars are on the
   whole 40; per-stratum agreement is a reading beside them.

Nothing in SP-0 blocks anything now. K6 has its denominator, the screen has its column list, and S7
runs in this slice.

**SP-1 — ASKED at plan review, ANSWERED: «Go на $0, деньги — на стопе S3» (operator, 30.08).**
The finding below stands unchanged — the phase does not fit its own remainder — and the ruling is
**where** the choice is made, not that it goes away: the three options are decided by the operator
at **S3's STOP**, on K3's page count and K4's range, and on a guard remainder re-read at that
moment. Nothing paid runs before that table exists. **$2.44** is the number STATUS carries from
now on (guard, 30.08); the phase spec's $3.17 is retired.
Read live from the guard while writing this plan (`PYTHONPATH=src python3.11 scripts/runpod_guard.py`,
read-only, `git status --porcelain results/ config/` clean afterwards):

```
anchor $22.51 at 2026-08-16T12:14:48+00:00 · balance now $4.95
CYCLE 2 SPENT  $17.5606 of $20.00        REMAINING  $2.4394
```

**$2.4394, not $3.17.** The phase spec's $3.17 is `results/spend_cycle2.json :: sessions[-1]`
(2026-08-27T09:43Z) and SPEC v2 §9's $3.41 is `sessions[-2]`; both are stale by the `mp-srv2` drip
(≈$0.24/day, `currentSpendPerHr` 0.01 with `pod list -a` empty). The phase's own estimate table at
its caps is **$0.4 + $2.5 + $0.3 = $3.20 — $0.7606 over the remainder before the first paid step**,
so `enforce()` refuses before the last one. And every day the team lead spends labelling the 50
positions and 40 threads costs another $0.24 of it.

**The remainder is also a clock.** `mp-srv2` bills $0.009722222574/h settled
(`results/srv2c_bootlog.json :: price_now_read` — $7.00/month exactly, `per_day 0.2333`) with zero
pods and zero endpoints, so **$2.4394 is exhausted by the volume alone in 10.4 days**. The compute
must fit under `$2.4394 − 0.2333 × (days until the last paid step closes)`, and the team lead's
labelling turnaround sits inside that window. Priced end to end — C2 + one boot retry + five C3
iterations + the holdout + one dead-pod allowance — the programme is **$2.09–2.51 at the ledger's
23.76 s/thread and $2.88–3.29 at a fitted rate**, against $2.4394. It fits only in the optimistic
corner and only if every paid step closes inside ~36 hours.

`docs/SPEC-v2-promo-pulse.md` §6.1 says «if the projection at any point exceeds the remainder → ASK
the operator (cycle-3 is his word), do not trim scope silently». It already exceeds it, which is why
the ask was owed at review rather than at S4 — deferring it to S4 would mean paying for C2 and then
discovering the guard refuses at C3, leaving a bought population and no graded reading. The operator
took the ask and **deferred the answer to the evidence**: the $0 slice runs, S3 builds the census
and the range, and he chooses on that table. §6.1's remainder is **$2.44**, not $3.17. Three
options, still the operator's, still not mine to narrow:
**(a)** open cycle-3 and name the sum · **(b)** narrow C2 to the pages that fit the remainder after
C3 and say which chains are dropped · **(c)** build a positions **pod** runner — the pod is 2.383×
cheaper per 1 000 rows than serverless (`results/srv2d_cost.json`: $0.5993 vs $1.4281) — but no
positions pod runner exists, so it is a new sibling runner and its own work.

**SP-1b — before S4, the mechanics.** The guard is `scripts/runpod_guard.py`
(`CYCLE2_CAP_USD = 20.00`; `spend()` is the pessimistic max of the balance delta and the billing
walk; `enforce()` prints refusals and returns 1, and «a cap is not raised to finish a run»). The
step gets its own ledger — `runpod_guard.py --step promo-pulse-1 --step-cap <usd>` — and both caps
bind, neither spending the other's room. (`would_exceed` in `scripts/retail_resolve_r2.py` counts
MTProto requests, not dollars; it is not this phase's guard.) I re-read the guard, run the census
and the projection, and re-read the remainder at that moment rather than quoting the number above.
The projection is computed at the **measured** rate, not the smoke's — see §5.4. Rungs 0–3 and the
cap-2× rule per `docs/PROCESS.md`.

**A $0 prerequisite K4 must not assume away:** `results/measurements.jsonl` (15 rows) carries **no
vision s/page row at all** and none for C3's new prompt, and the projection precedent hard-exits on
a missing named rate — `scripts/project_think_zero_shot.py:107` «stage {order} has no rate:
`{rate_name}` is not in the ledger. The smoke writes it — project nothing until it has.» So the
smoke seeds those two rows before any projection is quotable. That is why S3's census and S4's smoke
are separate things and the smoke is inside the paid step, not before it.

**SP-2 — before S10.** The ONE holdout attempt: pre-registered (readings + the two bars + the kill
rule) in a committed record before the pod exists, and the operator is told it is being spent.

**SP-3 — inside S9.** Two iterations without gain = plateau: I STOP with the error table. The team
lead reworks the codebook/prompt; the executor does not.

**SP-4 — anywhere.** Anything that would edit a sealed record, a frozen set, or a team-lead file.

**SP-5 — RESOLVED at the plan review: «accepted with amendments», seven of them.**
`claude/review-2026-08-27-new-rag-transfer.md` §2 is **not in this repo and not in its git history**;
SPEC v2 §4 carries the pointer, not the schema. I proposed five tables so the team lead could diff
mine against theirs in one read, and the review quoted the missing §2 into this repo and amended
mine against it. §5.7 now carries **the ruling, not the proposal** — six tables, `unsure` added, and
`window_id` out of every identity but `rollup`'s. S6 builds that.

## 5. Assumptions and scope choices

**5.1 Window — and the anchor is read AFTER S2, not before it (review correction 4).** 4 weeks =
**28 days**; the anchor is the corpus's own **last day + 1**, the ratified precedent of
`5c2-stop-ruling-and-cap-33` (a) — a later anchor buys days that are empty by construction and
measures the collection schedule instead of the content.

S2 moves that day. Today the store's newest A1 post is **2026-08-08**, so an anchor computed now
would open a window over a corpus that S2 is about to extend by three weeks, and K3 would
pre-register a population that no longer exists by the time it is bought. So the order is fixed:
**S2 tops up the store first, and the C2 window anchor is the topped-up corpus's last day + 1**,
read at S3 off the store and never carried in from this document. `results/promo_census_c2.json`
**states the anchor date it used** beside `selection.ids_sha256`, so the projection, the paid pass
and the team lead's re-run all read one window and can prove it is the same one. The window is
pinned by `ids_sha256`, not by a row count (SPEC 3.18 (4)).

**5.2 Registry r2 is an edit, not a new file.** `config/registry.yaml` lives under the executor's
`config/`; SPEC v2 §3's «правка ревизией, не редактированием» is answered by the r1 proposal's own
sentence — «ревизия — отдельный шаг после решения». It has moved before (two records still pin
`c82d0cff1ee7…`). The 21 pins are handled by preflight + `tests/moved_pins.py`; nothing is re-pinned.

**5.2a Two A1 rows have no expressible handle, and the loader must grow first.**
`src/market_pulse/registry.py:15` is
`_HANDLE = re.compile(r"^@[A-Za-z][A-Za-z0-9_]{4,31}$")`, enforced in `_sources` with a hard
`ValueError`. Two of the 17 A1 rows are not public usernames and fail it:
**Маркетопт private** is the invite hash `+Ejz6ubzm21IyMTQy`, and **@ATB_FANatik's discussion
group «АТБ / ЗНИЖКИ»** is `id: 1925810730` with `"username": null`
(`results/retail_census.json`). Both verified against the live regex, not assumed. The enabling
fact: **`registry.py` is pinned by nothing** — zero occurrences across `results/*.json` — so
extending it is cheap and moves no sealed record.

**But a sibling field would break two live tests, so S1a widens the accepted entry instead.**
`tests/test_registry.py:80` asserts `all(s.telegram_channels for s in registry.sources)` and the
loader itself raises `ValueError("no telegram_channels")` on an empty list
(`test_source_without_channels_rejected`). A row carrying only a `chat_id` with
`telegram_channels: []` fails both. So `_HANDLE` becomes a **union** — `@username` ∪ `+inviteHash`
∪ a numeric chat id — and every existing assertion stays true: each source still has ≥ 1 entry, and
`test_malformed_channel_handle_rejected`'s `'chan_without_at'` still matches nothing and still
raises «malformed handle». The regex is widened where the world is wider, not loosened.

**5.2b «Paused» is a collection flag, not a removed row — verified by driving the build.**
`scripts/build_aggregates.py:99 segment_for()` raises `SystemExit` for any channel that carries
evidence rows and has no registry entry: «SPEC 3.20 (1) fails loudly on a missing source rather than
aggregating a channel with an empty segment column». I handed it an A1+A2-only segments map against
the channels actually on disk: **28 channels carry evidence and it refused on 21 of them** —
`@atb_market_official` first among them, which holds **106 of the 145 positions (73%)** and the
entire leaflet leg, plus `@matusi_ukr` (2 717 comments) and `@mandziak` (1 026) of the PAUSED 39,
together ~74% of the 5 075.

So a revision that *deletes* or *comments out* those rows breaks `pulse.db`, and with it
`export_dashboard_data.py` and the screen — at $0, at step two. SPEC v2 §3 already says the right
thing and I mis-read it first: «выводится из **сбора**… данные и замороженные тесты остаются» — out
of **collection**, not out of the registry. The data stays, so the row that explains it must stay
too. r2 therefore adds a per-source **`collect: false`** (name at the team lead's discretion) and
the collector honours it; `segment_for` keeps resolving every historical channel. This is a change
of mechanism, not of scope: the 39 still stop being collected, exactly as §3 rules.
`@atb_market_official` is a **different** case and the review corrected me on it: it is not
paused at all — it stays in A1 **and** in collection as the leaflet carrier, and it appears in
the refusal list above only because it was one of the 21 channels the A1+A2-only map could not
resolve. Its row keeps `collect: true`.

**5.3 The 8 uncollected entries.** Six named handles have no store file — `@blyzenkoua`,
`@fozzyshopua`, `@sim23_simi`, `@rrozetka`, `@kop1chat`, `@xochydeshevshe` — and so do the two of
§5.2a. `@kop1chat` and the registry's `@kopiyochka1` are **different handles**; I collect the one
the phase spec names and report the pair rather than merge them on a guess. `@znishkom` is the
opposite case: 193 posts in the store and no registry row.

**5.3a The 18 A1 entries, one line each — the split is a list, not a total.**
Recounted against `config/registry.yaml` (66 sources) and `data/raw/posts/`. **8 carry a
registry row today**: `@atb_market_official` (`atb`), `@atb_aktsiyi` (`atb_aktsiyi`),
`@VARUS_channel` (`varus`), `@ekomarket_shop` (`ekomarket_shop`), `@epicentrk_sale`
(`epicentrk_sale`), `@foraINFO` (`forainfo`), `@silposilpo` (`silpo`), `@msuaaaa` (`msuaaaa`).
**10 do not**: `@ATB_FANatik` (store file, no row), its discussion group, Маркетопт private,
`@blyzenkoua`, `@fozzyshopua`, `@sim23_simi`, `@rrozetka`, `@kop1chat`, `@znishkom` (193 posts,
no row), `@xochydeshevshe`.

The 8 rests on **three identity judgments**, written out because the count moves if the team
lead overturns any of them: `@foraINFO` ≡ the registry's `@forainfo` (case only — Telegram
usernames are case-insensitive, so this is one channel and I do not add a second row);
`@kop1chat` ≢ the registry's `@kopiyochka1` (different handles — §5.3); Маркетопт private
(`+Ejz6ubzm21IyMTQy`) ≢ the registry's `@marketopt_promo` (a private invite is not the public
promo channel). §3's own arithmetic — 17 rows + the discussion group = **18 entries** — is what
8 + 10 sums to.

**5.4 The rate — 10.408 s/row, not 1.7.** `docs/STATUS.md` quotes «1.7 с/стр.» That number is
`results/run_5c2_positions.json :: go_no_go.page_marginal_seconds = 1.729`, a two-call warm-up
**marginal**. The realised rate in the same file is `timing.seconds_per_row = 10.408` over 205 rows
(2 133.705 worker seconds), and `5c2-closed-…` names 10.408 as «the number the next registration
starts from». At `rate_usd_per_second = 0.00030669` that is **$0.003192/row**, so the phase spec's
«≈$0.4» buys ≈**125 rows** — while ATB alone was 159 pages in three weeks. The projection of K4
settles it; I do not carry either number into the plan as a conclusion.

**5.5 The 678 threads must be enumerated, not read off.**
`results/promo_comment_yield.json` carries per-channel **counts** and no thread ids
(`total.price_threads = 678`, `total.under_price = 4 718` of `16 324`). S7 re-derives the ids with
the **same** predicate its producer used — `retail_census.PRICE_BRANCHES` joined on `parent_msg_id`
(`scripts/promo_comment_yield.py`) — so the draw and the census measure the same instrument. I
re-ran that logic over `data/raw/` and reproduced **678 / 4 718 exactly**, so the draw is buildable
at $0 today with no new input.

**5.5a Two thirds of the 678 are selected by a regex firing on DATES — SP-0 question 3, ANSWERED.**
`PRICE_BRANCHES` has four branches; `decimal` is `\d+[,.]\d\d`. Splitting the 678 by branch
(measured, reproduced twice): **229** threads carry a real currency marker (`грн` / `₴` / `grn`) and
**449 (66%) match on `decimal` alone.** Ten of those 449 read under seed 42 are **10 of 10 dates**,
not prices — «Пропозиції діють з 14.08 по 20.08», «з 18.03.26 по 24.03.2026», «Лише по 08.07.26».
The producer's own docstring already warned it: «a yield carried entirely by `decimal` is a yield to
distrust». These are still *promo* posts («Знижки в АТБ», «До -67% у Сільпо») — they simply carry no
price in the text, because the price is in the image. **The ruling: the finding stands, the
conclusion is a stratum and not a cut.** The operator answered «Все 678, дро 20/20 по типу» — a
promo post whose price is in the **image** is a price post, the same reading the review used to keep
`@atb_market_official` in A1. So the population is all **678**, and the branch split becomes the
draw's **stratification**: 229 currency (`грн|₴|grn`) and 449 `decimal`-only — measured, disjoint
and exhaustive (229 + 449 = 678 exactly, reproduced twice). dev-40 = 20 + 20 and holdout-40 = 20 +
20, so each stratum owes 40 of the 80 and both clear it with room. What the finding buys is no
longer a smaller population but a **column**: per-stratum agreement is reported beside the bars, so
if the `decimal`-only half grades worse the number says so, instead of the population having hidden
it.

**5.5b Channel is a recorded field, not a stratum — accepted by the review (SP-0 q3, «Channel is
recorded per thread, not a stratum (5.5b accepted)»).** 665 of the 678 (98.1%) are `@msuaaaa` (447)
and `@VARUS_channel` (218); the tail is `@matusi_ukr` 4, `@HealthPsycholog` 3, `@mandziak` 2 and
four channels with 1 each. Channel-proportional quotas for dev-40 would have given msuaaaa 27 /
VARUS 13 / **zero from the other seven**, and dev-40 + holdout-40 = 80 would still have reached no
third channel — a stratification that cannot discriminate. The strata are the two **branches** of
§5.5a instead, and channel is written on every drawn thread as a field. Six of the seven tail
channels are in the **PAUSED 39** that §3 removes from collection; that changes nothing about the
population — the threads are already on disk and §3 removes those channels from *collection*, not
their history from the store — but the draw record marks which drawn threads come from a
no-longer-collected channel, so nobody later reads them as ongoing coverage. The record states its
quotas, its seed, the predicate (`retail_census.PRICE_BRANCHES`) and what it could not reach.

**5.6 Text-less comments.** SPEC 3.19: they leave the inference queue from the next paid cycle —
a **queue** rule, never a deletion — and «the volume of wordless reactions is itself a signal», so
the wordless class is printed as its own named class beside every distribution over comments. The
S2 draw is taken **after** the queue rule, and the draw record states the count it removed.

**5.7 The six tables — the team lead's ruling, not my proposal (review 30.08, SP-5 «accepted
with amendments»).** My five-table proposal was amended on seven points and the amended shape is
what S6 builds; where the two differ, the ruling wins. ids are `uuid5(NAMESPACE, key)` with
`NAMESPACE = uuid5(NAMESPACE_URL, "market-pulse-llm/promo-pulse-1")`, keys normalised (NFC, lower,
whitespace-collapsed) and joined by `\x1f`:

`subject_id` = `uuid5(NAMESPACE, subject_type|name)` with `subject_type ∈ chain|brand|sku|post` —
amendment (2). The key is fixed; the ruling leaves the carrier to me and I take the **pure
function**, no `subject` table: `attribution` already carries `subject` and `subject_type` as
columns, so a table would hold nothing a join does not already have (added when a subject needs
attributes of its own, not before).

- `attribution(attribution_id ← channel|msg_id|subject_id, channel, msg_id, subject_id,
  subject_type, subject, role, source ∈ explicit|reply_context|post_context, confidence)`
- `signal(signal_id ← channel|thread_root|type|subject_id, channel, thread_root, type ∈
  жалоба|похвала|спрос|привычка|цена, subject_id, confidence, extractor_version)`
- `evidence(evidence_id ← signal_id|msg_id|quote, signal_id, msg_id, quote, span)` — `span` nullable
- `digest(digest_id ← channel|thread_root, channel, thread_root, version, text,
  children_ids, supporting_signal_ids, covers_up_to_msg_id, cooled_at)`
- `unsure(unsure_id ← channel|msg_id|reason, channel, msg_id, candidates, reason)`
- `rollup(rollup_id ← week|chain|brand|metric, week, chain, brand, metric, value)`

Four amendments carry a reason I have to build to, so they are written out rather than listed:
**(1)** `signal`'s key gains `subject_id` — two complaints in one thread about different subjects
must not collapse into one row. **(3)** `digest` holds the state, not just the children: the
late-comment delta (phase spec S4) reads digest + delta, so `version`, `text`,
`supporting_signal_ids` and `covers_up_to_msg_id` sit beside `children_ids` and `cooled_at`.
**(4)** `window_id` is **not part of any identity** in `attribution` / `signal` / `evidence` /
`digest` — week is derived from the thread root's post date at query time; a thread that cools
across a tick boundary would otherwise get a second identity and break K10. This is the one place
the new tables depart from every existing table in `aggregates.py :: SCHEMA`, each of which carries
`window_id` in its primary key, so S6 states it in the schema comment. `rollup` is the exception the
ruling keeps: its identity is `week|chain|brand|metric`, week included, because a rollup **is** a
per-week fact. **(5)** `unsure` is written by the instrument on low-confidence attribution or on a
class the codebook lacks (SPEC v2 §4 (в)) — the team lead reads it at SP-3, so an abstention is a
row, never a silent drop.

`extractor_version` is the sha256 of the **rendered** prompt of the new module (§5.11), not of the
module file: a row has to say which instrument produced it, and the render is what the model saw.
Existing ids are **not** migrated: `positions.row_id` is already deterministic
(`channel:msg_id:ordinal`).

**5.8 Idempotence has one known hole and S12 closes it.** `evidence.KINDS` is
`("comment", "leaflet_page", "position_row", "post_text")` — there is no member for «read and
yielded nothing», so an interrupted **post_text** pass re-buys the row (2 re-asked against the
leaflet leg's 0, `5c2-stop-ruling-and-cap-33` (e)). The derived `markers` table already records the
empties (127 of 159 leaflet pages, 22 of 44 post texts yielded 0 positions) but the raw evidence
ledger the paid pass reads does not. S12 adds the fourth kind; K10 is the check that it worked.

**5.9 `unknown-brand` is the store's existing state, not a new literal.** The phase spec's hook
reads «brand ∈ registry or `unknown-brand`». That literal is **nowhere in the codebase**, and the
store already has the state: `positions.brand_id IS NULL` with the surface form kept in `brand_raw`
(65 of the 145 rows today, e.g. `Дольче`). The hook asserts that pair; it does not invent a third
value. If the team lead wants the literal on the wire, say so at review and I will add it as a
rendering of the same state, never as a second way to mean it.

**5.10 Thresholds I introduce.** seed **42** everywhere · cooled = **24 h** without a new comment ·
schedule min interval **1 h**, default **6 h** (READ from `data/schedule.json`, which does not exist
yet and S12 creates) · dev-40 / holdout-40 disjoint and frozen at the draw · plateau = **2**
iterations without gain · cap **$2.5** on the C3 dev loop, per phase spec §6.

**5.11 Serving — «thinking OFF, batch 1» is already structural and costs no work.**
`local_llm.py` carries `CHAT_TEMPLATE = {..., "enable_thinking": False}` as the default of every
client, and `PositionsClient.render` / `CaptionClient.render` hardcode it with no kwarg at all.
Batch 1 is likewise structural: the positions, caption and reader legs each loop one item per
forward. So the constraint needs **no flag and no change** — I assert it in a test rather than
implement it. New prompt text still goes in a **new module** (`prompts.py` is pinned), and
`scripts/preflight_serving_guards.py` renders the real chat template offline ($0) before any pod.
`scorer.py` stays the single judge and is not forked.

**5.12 `positions.py` is pinned and I do not plan to touch it.** Its live sha
`0b058e800244…` is identical to its pin in four sealed records (`prereg_5c2_run`,
`sku_pilot_prereg_b2`, `validate_5c2_pack`, `window_summary_5c2`). The frozen `Position` dataclass
already carries all 16 fields S1 needs, `depth()` already returns `None` rather than reconstructing
from the printed % (3.17 (3)), and `depth_disagrees_with_printed()` already flags at
`PRINTED_TOLERANCE_PP = 1.0`. C2 is a **population** change — which carriers are fed to the existing
instrument — so it lives in the callers. If S4 finds a parser change is truly unavoidable I stop and
say so (SP-4) rather than move a pinned file inside a paid step.

**5.12a Result files have four envelopes, not one, and each step uses the right one.** A **sealed
pre-registration** (`results/prereg_5c2_run.json`: `pinned_inputs` as `{path: sha256}`, every number
carrying an equality test, a `verifier` block) is the shape for the S2 pre-registration and the
holdout shot. A **derived export** (`results/dashboard_data_w1.json`: `provenance = {evidence,
inputs, producers, reads}`, a `window` with `"rule": "since <= date < until, half-open"`, written
sorted-keys with **no clock and no git block** so it is byte-deterministic) is the shape for
positions, trends and the screen's export. Emitting a clock into a derived export is what makes a
determinism check unrunnable, so K9 and K10 depend on getting this right.

**5.12b The paid steps are sequenced, never shared on one pod — and the guard would refuse the
shared one anyway.** C2's page leg is a **serverless endpoint** and C3's thread legs are a **pod**,
so they cannot share a machine at all (and `docs/PROCESS.md` forbids two billing resources
concurrently — free to satisfy by sequencing). For C3's own five iterations, one long-lived pod
looks cheaper by five fixed taxes (≈$0.29) but bills every gap between them: break-even is a
**4.65-minute** turnaround, and a real gap — pull the output, score it against the team lead's
labels, read the error table, edit the prompt module, re-stage — is nearer 15, i.e. ≈$0.93 of idle
against $0.29 saved. Two harder reasons settle it: `--terminate-after` is fixed at create
(`runpodctl pod update` has no such flag), so a shared pod must declare its whole span up front —
≈4.36 h × $0.74/h = **$3.23, larger than the line has**, and `enforce()` refuses before the create;
and a pod registered for six legs has already bought legs that §6.3's plateau rule may forbid.
**One create per iteration.**

**5.13 The tick's spine already exists.** `loop.py` carries four watermarks — `posts`, `inference`,
`leaflet`, `post_text` — and the three passes `inference_pass` / `page_pass` / `post_pass`, each
recording durably **before** advancing its watermark, with `send` as the only seam. S12 is wiring a
`make tick` over those, plus the cooled-thread digest and the fourth evidence kind of §5.8 — not new
machinery. That is why K10 is a cheap check and not a rewrite.

**5.14 The live raw root and the `RawStore` union — SP-4, ruling (a) (review 2026-08-30,
«Acceptance of the scaffold slice»).** S2 stopped because four A1 channels write into the four
pinned files of `results/raw_v1_baseline.sha256`. The ruling widens option (a) from the top-up to
the whole loop, and this section is what S2, S12 and every reader of the store build to.

**The three rules.** (1) `data/raw/` is an **archive**: read-only forever, and the baseline stays
the proof — `data/` is gitignored, so `shasum -c results/raw_v1_baseline.sha256` is the only
durable evidence in either direction. (2) ONE live root, **`data/raw_r2/`**, receives S2's top-up
for **all** collected channels — the pinned four and the free sixteen alike, so no reader has to
know which of the two a channel's rows came from. (3) A reader that wants the corpus reads
**v1 ∪ r2, deduplicated on (channel, msg_id), r2 winning** — `RawStore(LIVE_ROOT,
archives=(ARCHIVE_ROOT,))`; the union is **opt-in and never the default**, because one consumer
must NOT have it (the draw, below).

**The guard is in `RawStore.append`, not in the collector.** `scripts/collect_r2.py::refuse_pinned`
guards a channel list; the moment `STORE_ROOT` points at the live root it passes trivially and
guards nothing. The refusal therefore moves to the one chokepoint every writer goes through — an
`append` whose root is the archive raises — and `refuse_pinned` stays as the second, earlier
refusal ([[a_moved_guard_that_left_its_copy]]: the copy that holds the writer is the one that
matters). Tested in both directions: a write into `data/raw/posts` and into `data/raw/comments`
refused, a write into the live root accepted, and `shasum -c` re-run after the test.

**The consumers, counted.** `graphify query "what reads RawStore"` returns a depth-2 subgraph of
285 nodes — a neighbourhood, not a consumer list — so it is the *starting* set and the count below
is the reconciled one: every construction of `RawStore(...)` and every direct read of the raw tree
in `src/` and `scripts/`. Nine consumers, and the column that matters is **which root**, not the
filename ([[a_consumer_list_is_not_a_meaning_list]]):

| consumer | reads | writes | under the ruling |
|---|---|---|---|
| `scripts/collect_r2.py:272` | v1 ∪ r2 | **r2** | S2's collector — retargeted; the index must see v1 or the top-up re-fetches threads v1 already holds |
| `scripts/promo_census_c2.py:50` (`POSTS`, direct read) | v1 ∪ r2 | — | K3 prices the **topped-up** corpus, so it must see r2 |
| `scripts/draw_promo_threads.py:56-57` (direct read) | **v1 only** | — | K7's population is the FROZEN 678 (ruling: «the frozen holdout comes from the frozen store»). A union here silently moves 678/488 — it is the one consumer the default must keep |
| `scripts/run_loop.py:609` | v1 ∪ r2 (S12) | — | reads the store, writes only `data/derived/`; the union lands with S12, not here |
| `scripts/run_5c2.py:713` | v1 ∪ r2 (S4) | — | same shape; the paid pass reads what S2 collected |
| `src/market_pulse/loop.py` | its caller's | its caller's derived root | takes stores as arguments; `ingest` is `RawStore.append`, so the guard covers it for free |
| `scripts/collect_5c1.py:120,446` | v1 | *(was v1)* | the r1 collector, **superseded**: the guard now refuses its writes. Left in place, not deleted — it is how the archive was built and its tests pin that behaviour on temporary roots |
| `scripts/backfill.py:221` | v1 | *(was v1)* | same: an r1 writer the guard now refuses |
| `scripts/fetch_comments_v2.py:212` | v1 (read) + `data/raw_fresh_45g5/` (write) | that third root | the precedent the ruling cites. **Named debt:** its two comment files are a third root the ruling's «v1 ∪ r2» does not mention; nothing in this phase reads them and I do not fold them in on my own word |

Seven test modules construct `RawStore` (`test_raw_store`, `test_loop`, `test_collect_5c1`,
`test_collect_r2`, `test_comments_v2`, `test_backfill`, `test_run_5c2`); all use temporary roots,
which is why a guard on the archive root leaves them green.

**One seam S12 will hit.** `loop.ingest` IS `RawStore.append`, and it has no production caller today — grepped: only `tests/test_loop.py` calls it, which is why `run_loop.py`'s row above says «writes only `data/derived/`». When S12 wires `make tick`, the store it hands `ingest` must be the live root: handed `RawStore(STORE_ROOT)` as `run_loop.py:609` builds it today, the guard refuses and the tick is dead on line one.

**What this does not change.** The window (§5.1) is still anchored on the topped-up corpus's last
day + 1, and the census still states the anchor and `ids_sha256`; the anchor is now read across the
union rather than off `data/raw/` alone. `positions.py` and every sealed record stay untouched.

## 6. Out of scope

From the phase spec §5, unchanged: brand trends/alerts · Poltava collection · training/LoRA ·
thinking anywhere · vLLM/merge · the schedule **UI** (the loop only READS `data/schedule.json`) ·
dashboard redesign beyond the one promo screen · scanning the 81 unscanned census candidates.

Added by me: no migration of `positions.row_id` to uuid5 (5.7) · no re-scoring of anything bought
under an earlier cap · no edit to `docs/SPEC.md`, any sealed record or any frozen set · no second
positions instrument (the two-stage OCR read and the `brands_visible` channel stay named candidates,
unbuilt, per SPEC 3.18 (2)) · no reopening of bar 2.

---

**Reviewed and ACCEPTED — `docs/reviews/2026-08-30-plan-promo-pulse-1.md`, 30.08. This revision
carries the five corrections that review asked for and nothing else of my own. GO on the $0
slice: S0 · S1a · S1b · S2 · S3 · S6 · S7 · S8. Every paid step still waits at S3's STOP.**

---

## 7. Revision 2026-09-01 — what this session introduced, and what in §2/§3 moved

PROCESS §Cadence 1 (as amended 01.09): information found AT a stop joins THIS plan by revision,
never a new contract file. `docs/PROMPT-c2-pagecount.md` was therefore never written; its work is
below. Every threshold, filter and sample introduced this session is listed here — one that reached
only the report would be a scope change.

**K4 moved from a range to ONE number** — the plan's §2 says «Emits a range, not a number… It
cannot emit a single figure», and the reason it gave was the missing `vision_seconds_per_page` row.
The smoke wrote that row on 30.08 and the pagecount below removed the other half of the width, so
the clause that justified the range is spent. `verdict.c2_priced_usd` is the number;
`the_one_number_usd` keeps its old boot-inclusive meaning beside it, unchanged, because
`tests/test_smoke_vision_c2.py` asserts the ordering between the two blocks.

**New instrument — `scripts/promo_pagecount_c2.py` ($0, Telegram metadata only).** Not in §3.
Population: the census's PINNED ids (`selection.ids_sha256`), never a window re-derived at run time
(SPEC 3.18 (4)). Two filters and one fallback, all new and all listed here:
- **a page is a PHOTO member** of the post's album. `has_media` is true of a video, a poll and a
  document alike; the window holds 146 videos and 3 polls, and no documents at all.
- **the fold key is `min(msg_id)`** of the album — what `RawStore.collapse_albums` kept.
- **an unreachable pinned post is priced at the store's msg_id-gap bound, never at 0.** The bound
  over-counts (240 of 258 exact against the manifests, 0 under), so the total stays an upper bound.
  Nothing was unreachable in the shipped run; the path is tested, not exercised.

**Guard — `CYCLE3_CAP_USD = 4.80`**, anchored at the balance the word was given on ($4.4800, i.e.
BELOW the ceiling). Cycle 2 is SUPERSEDED, not closed: one line is enforced at a time, and its
sealed record is neither edited nor re-scored. `--open-cycle3` anchors once.

**S11 landed in `src/market_pulse/trends.py`, not in `aggregates.py`** as §3 says. No schema change
and no pin moved. New keys: the **SKU is brand_raw+line+size_value+size_unit** (no price — a SKU
identified by its own promo price has one row per promo and no trend); the **week is ISO `%G-W%V`**
so the label sorts across a year boundary; a position whose post is not in the store is **dropped**,
never bucketed under an invented week.

**Proposed and NOT applied — the even cut (STOP).** C2's share as $4.80 − $2.50 − $0.30 = **$2.00**,
and the fraction it implies, **1 889 of 3 008 pages (62.8 %)**, are arithmetic in
`docs/plans/promo-pulse-1.STOP.md` and are NOT thresholds this plan adopts: they allocate against
C3's cap rather than its cost, and which pages survive inside a chain is unsettled. Both are the
team lead's.

**Out of scope, unchanged:** §6.
