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

**One column of §1's artifact is contested and I do not decide it — see SP-0.** §1 names `price old`
as a screen column. `docs/SPEC.md` amendment 3.21 (4) says «the extracted old price is never
printed», 3.18 (1) says it «never reaches a surface that prints it as a price», and 3.22 (1) keeps
arithmetic depth out of any row that shows its own promo price, because `promo ÷ (1 − depth)`
reconstructs the old price. Those rulings rest on a measurement SPEC v2 does not move: the extracted
old price is right as a number on **33 of 80 pairs** (`results/sku_bar_verdicts_skub2.json`, bar 2 =
0.4125 against 0.80). So the plan **stores** `price_old` — the column already exists in
`positions` — and **does not print it** until the team lead rules. This is the difference between
storing and printing, not a scope cut.

## 2. Checks

Graders first, mechanics after. A check I cannot run today is marked **[BLOCKED]** with its blocker.

| # | command | pass condition |
|---|---|---|
| K0 | `make check` | ruff + pytest green. Baseline **measured, twice, independently**: `1 failed · 4 129 passed · 2 skipped`, `ruff check .` clean, `make: *** [check] Error 1`; `.suite-stamp.json` carries the whole-suite run at `81af568`. The one red is pre-existing and not mine: `tests/test_repair_phase4_ledger.py::test_the_silence_check_fires_on_the_LINE_ledger_too` — the silence-check reads the LIVE `results/spend_cycle2.json`, which grew past it (the repo's own `[[a_sealed_reports_checker_reads_a_live_file]]`). `docs/STATUS.md` assigns it as the $0 debt of the next contract's step 0, so **S0 fixes it**, by asserting what the check was really protecting rather than by deleting the assertion. |
| K0s | `make check-stamped` | the same reading with a proof the tree did not move under it. **The K0 counts above are NOT a HOLDS-at-HEAD baseline**: HEAD moved twice mid-run (this plan's own commits), and `scripts/check_stamped.py` voids on a HEAD change alone — its whitelist is only `knowledge/daily_logs/` and `knowledge/index.md`. The counts are still trustworthy as a reading (no test reads `docs/plans/**`, and `hot.md`, the one suite input outside the whitelist, did not move), but the Baselines block of every step quotes **K0s at a settled tree**, never K0. |
| K1 | `make preflight ARGS='config/registry.yaml'` | run BEFORE and AFTER S1. `config/registry.yaml` is pinned by **21 sealed records**, live sha `d4e3b2373c43…`. After the edit every record pinning the old sha is claimed through `tests/moved_pins.py` (derived from live shas, both directions) — **never re-pinned**. |
| K2 | `PYTHONPATH=src python3.11 -m market_pulse.registry config/registry.yaml` | r2 loads; source count and the A1/A2/PAUSED split are what §3 of the phase spec names. |
| K3 | `python3.11 scripts/promo_census_c2.py` → `results/promo_census_c2.json` | $0. Per channel over the 4-week window: posts, leaflet **pages**, text-price posts, `media_share`, and a `selection.ids_sha256` pin. Pre-registers the paid population **by row count**, never as a date range evaluated at run time (SPEC 3.18 (4)). |
| K4 | `python3.11 scripts/promo_projection_c2.py` → `results/promo_projection_c2.json` | $0. Pages × the **measured** rate × $/s against the guard's freshly re-read remainder. This is a STOP, not a pass/fail — see SP-1. |
| K5 | `python3.11 scripts/draw_positions_50.py` twice | `results/positions_draw_50.json` — 50 positions, seed 42, from ≥3 chains' flyers/posts of the backfilled 4 weeks; two runs produce an identical sha. Handed to the team lead. |
| K6 | `python3.11 scripts/grade_positions.py` → `results/grade_positions_50.json` | completeness ≥ 0.90, price accuracy ≥ 0.95. **[BLOCKED]** on `docs/labels-positions-50.jsonl` (team lead's, owed after K5) and on SP-0's answer, which fixes the bar's denominator. |
| K7 | `python3.11 scripts/draw_promo_threads.py` twice | `results/promo_threads_draw.json` — dev-40 + holdout-40, **disjoint and frozen at the draw**, seed 42, stratified by channel over the 678 price threads; two runs identical. Handed to the team lead. |
| K8 | `python3.11 scripts/grade_promo_signals.py` → `results/grade_promo_dev40.json` | subject agreement ≥ 0.80 · signal-type agreement ≥ 0.75 on dev-40. **[BLOCKED]** on `docs/labels-promo-dev.jsonl` (team lead's, owed after K7). |
| K9 | `pytest tests/test_trends_sql.py -q` | S3 recomputed from `positions` twice → identical; a week with no data renders **absent**, never `0`. Asserted in both directions. |
| K10 | `make tick && make tick` | second run writes **zero** new rows. Asserted per table by count before/after, not by a global total — an aggregate counter cannot see a per-row change. |
| K11 | `pytest tests/test_promo_hooks.py -q` | between calls: `msg_id` exists · quote is a substring of the source text · brand ∈ registry or the store's unresolved state (§5.9) · schema valid. A hook failure is a **counted row**, not an exception — asserted with a negative control (a row that must fail and be counted). |
| K12 | `make promo-screen` on a **clean clone** after `make tick` | the screen renders from result files only and **fails loudly** on any missing source. Negative control: remove one source, assert a non-zero exit and a named error. |
| K13 | `python3.11 scripts/draw_truth_20.py` → 20 rows, seed 42 | flyer/post · extracted position · comment · signal · quote, rendered for the operator. The gate is his words, not a number. |

End-to-end (closes the phase) = K12 then K13, in that order.

## 3. Steps

Each ends in a commit **by path** and the checks named. No `git add -A`; no repo-wide `make fmt`.

| # | what | files | check |
|---|---|---|---|
| S0 | Commit the team lead's uncommitted files by path (`docs/STATUS.md`, `docs/PHASE-promo-pulse-1.md`); clear the `test_repair_phase4_ledger` debt STATUS assigns to step 0 of the next contract. | commit by path only; `tests/` | K0 |
| S1a | **Loader extension first** (§5.2a): two of the 16 A1 rows **cannot be expressed** under today's `_HANDLE` regex. `src/market_pulse/registry.py` is pinned by nothing, so this is a cheap, legal prerequisite — a `chat_id` / `invite` field beside `telegram_channels`, with the regex left intact for real usernames. | `src/market_pulse/registry.py`, `tests/test_registry.py` | K2, K0 |
| S1b | **Registry revision r2.** 16 A1 rows · 5 A2 · PAUSED 39 leave collection · B deferred. Preflight, edit, then claim the moved pins. Of the **17** A1 entries §3 names (16 rows + ATB_FANatik's discussion group), **7 are in the registry and 10 are not** — derived, not counted by hand: `@ATB_FANatik`, its discussion group, Маркетопт private, `@blyzenkoua`, `@fozzyshopua`, `@sim23_simi`, `@rrozetka`, `@kop1chat`, `@znishkom`, `@xochydeshevshe`; `@atb_market_official` and the PAUSED 39 leave **collection**, and their registry rows **stay** — §5.2b: removing them makes the aggregates build refuse at $0. Every new row needs an `audience` from the closed list of 8 — `test_every_shipped_source_carries_an_audience` forbids a null. | `config/registry.yaml`, `tests/moved_pins.py`, `tests/` | K1, K2, K0 |
| S2 | **$0 collection.** The population §1 measures does not exist on disk: the newest post across every A1 channel is **2026-08-08** (today is 2026-08-30, so ≥22 days of the 4-week window are uncollected for *every* channel), and **8 of the 17 entries have no store file at all** — the 6 missing handles plus Маркетопт private and the discussion group. Collect them, top up the rest to the window, and collect the `@ATB_FANatik` discussion group (its traffic is measured at entry — r1's 0.25 c/day read post replies, not the group feed). Every NEW channel enters through the adaptation protocol: profile → sealed hundred → gate **before** aggregates. Telegram only. | `scripts/`, `data/raw/`, `results/` | K0 |
| S3 | **$0 census + projection** of the paid legs (K3, K4), then **STOP** — SP-1. | `scripts/promo_census_c2.py`, `scripts/promo_projection_c2.py`, `results/` | K3, K4, K0 |
| S4 | **C2 backfill (PAID).** Positions for the 16 channels over the 4 weeks, via the existing 5c2 instrument — vision for image flyers, text for the rest. **`positions.py` is not touched** (§5.12): the scale is in which carriers get fed, not in the parser. Smoke first; rungs per `docs/PROCESS.md`. | `scripts/`, `results/`, `data/derived/` | K0 |
| S5 | **S1 draw** (K5) → hand `results/positions_draw_50.json` to the team lead for `docs/labels-positions-50.jsonl`. | `scripts/draw_positions_50.py`, `results/` | K5, K0 |
| S6 | **The five new tables** — `attribution / signal / evidence / digest / rollup`, uuid5 ids over normalised keys (§5.7). `aggregates.py` extended; `positions` untouched. | `src/market_pulse/aggregates.py`, `tests/` | K0 |
| S7 | **C3 step 0.** Enumerate the 678 price threads (the yield file carries **counts only, no ids** — see §5.5) and draw dev-40 + holdout-40 (K7) → hand to the team lead. | `scripts/draw_promo_threads.py`, `results/` | K7, K0 |
| S8 | **Instrument + hooks + graders**, all $0: a NEW prompt module (`prompts.py` is pinned), the four hooks, `grade_positions.py`, `grade_promo_signals.py`. Graders are written and unit-tested against synthetic gold before any real gold exists. | new module in `src/market_pulse/`, `scripts/grade_*.py`, `tests/` | K11, K0 |
| S9 | **C3 dev loop (PAID).** 3–5 iterations × dev-40. Thinking OFF, batch 1. Plateau → SP-3. | `scripts/`, `results/` | K8, K0 |
| S10 | **The ONE holdout shot (PAID)** — pre-registered first (SP-2), then spent once. | `scripts/write_promo_prereg.py`, `results/` | K8, K0 |
| S11 | **S3 trends, SQL only, no LLM.** Price per SKU per week per chain; depth per chain and brand. | `src/market_pulse/aggregates.py`, `tests/test_trends_sql.py` | K9, K0 |
| S12 | **S4 the loop.** `make tick`, `data/schedule.json` (READ only), `loop.py` cursors, the cooled-thread digest and the late-comment delta. | `Makefile`, `src/market_pulse/loop.py`, `tests/` | K10, K0 |
| S13 | **C5 the screen.** `make promo-screen`, one promo view, result files only, loud failure on a missing source. | `dashboard/`, `scripts/build_dashboard.py`, `Makefile` | K12, K0 |
| S14 | **End-to-end + the product-truth gate**: clean clone, `make tick && make promo-screen`, then the 20 rows for the operator. | `scripts/draw_truth_20.py`, `results/` | K12, K13, K0 |

## 4. Stop-points — asked BEFORE, never reported after

**SP-0 — before S1, and it blocks nothing on the $0 path.** Two questions for the team lead:
1. Does S1's `price accuracy ≥ 0.95` denominate over the **promo price only** (the green leg, 80/80
   in `results/sku_b_pair_verdicts_skub2.json`) or over the **price pair**? At the pair the bar is
   unreachable by measurement — 0.4125 — and the gold file that fixes the denominator is the team
   lead's to write.
2. Does the §1 screen **print** `price old`, against 3.21 (4) / 3.22 (1)? I store it either way.
3. **Which population is S2 graded on** — 678, 229 or 449 (§5.5a)? Two thirds of the 678 are
   selected by a regex matching **dates**, not prices, and the operator's ruling says «только треды
   под ЦЕНОВЫМИ промо». This is the one SP-0 answer that gates a $0 step: S7's draw waits for it.

Questions 1–2 block only K6 (the graded S1 reading) and one screen column; question 3 blocks S7.
S0–S6 and S8 do not wait for any of them.

**SP-1 — OWED NOW, at plan review, not at S4: the phase does not fit its own remainder.**
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

§6.1 says «if the projection at any point exceeds the remainder → ASK the operator (cycle-3 is his
word), do not trim scope silently». It already exceeds it, so the ask is owed at review — deferring
it to S4 means paying for C2 and then discovering the guard refuses at C3, leaving a bought
population and no graded reading. Three options, the choice the operator's:
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

**SP-5 — the schema, resolved by this plan's review, not by a separate ask.**
`claude/review-2026-08-27-new-rag-transfer.md` §2 is **not in this repo and not in its git history**;
SPEC v2 §4 carries the pointer, not the schema. I propose the five tables in §5.7 so the team lead
can diff mine against theirs in one read. If theirs differs, theirs wins and S6 is rewritten.

## 5. Assumptions and scope choices

**5.1 Window.** 4 weeks = **28 days**; the anchor is the corpus's own **last day + 1**, the
ratified precedent of `5c2-stop-ruling-and-cap-33` (a) — a later anchor buys days that are empty by
construction and measures the collection schedule instead of the content. The window is pinned by
`ids_sha256`, not by a row count.

**5.2 Registry r2 is an edit, not a new file.** `config/registry.yaml` lives under the executor's
`config/`; SPEC v2 §3's «правка ревизией, не редактированием» is answered by the r1 proposal's own
sentence — «ревизия — отдельный шаг после решения». It has moved before (two records still pin
`c82d0cff1ee7…`). The 21 pins are handled by preflight + `tests/moved_pins.py`; nothing is re-pinned.

**5.2a Two A1 rows have no expressible handle, and the loader must grow first.**
`src/market_pulse/registry.py:15` is
`_HANDLE = re.compile(r"^@[A-Za-z][A-Za-z0-9_]{4,31}$")`, enforced in `_sources` with a hard
`ValueError`. Two of the 16 A1 rows are not public usernames and fail it:
**Маркетопт private** is the invite hash `+Ejz6ubzm21IyMTQy`, and **@ATB_FANatik's discussion
group «АТБ / ЗНИЖКИ»** is `id: 1925810730` with `"username": null`
(`results/retail_census.json`). Both verified against the live regex, not assumed. The enabling
fact: **`registry.py` is pinned by nothing** — zero occurrences across `results/*.json` — so
extending it is cheap and moves no sealed record. S1a widens the row shape rather than the regex,
so a malformed *username* still fails loudly.

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

**5.3 The 8 uncollected entries.** Six named handles have no store file — `@blyzenkoua`,
`@fozzyshopua`, `@sim23_simi`, `@rrozetka`, `@kop1chat`, `@xochydeshevshe` — and so do the two of
§5.2a. `@kop1chat` and the registry's `@kopiyochka1` are **different handles**; I collect the one
the phase spec names and report the pair rather than merge them on a guess. `@znishkom` is the
opposite case: 193 posts in the store and no registry row.

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

**5.5a Two thirds of the 678 are selected by a regex firing on DATES — SP-0 question 3.**
`PRICE_BRANCHES` has four branches; `decimal` is `\d+[,.]\d\d`. Splitting the 678 by branch
(measured, reproduced twice): **229** threads carry a real currency marker (`грн` / `₴` / `grn`) and
**449 (66%) match on `decimal` alone.** Ten of those 449 read under seed 42 are **10 of 10 dates**,
not prices — «Пропозиції діють з 14.08 по 20.08», «з 18.03.26 по 24.03.2026», «Лише по 08.07.26».
The producer's own docstring already warned it: «a yield carried entirely by `decimal` is a yield to
distrust». These are still *promo* posts («Знижки в АТБ», «До -67% у Сільпо») — they simply carry no
price in the text, because the price is in the image. The operator's ruling was «только треды под
ЦЕНОВЫМИ промо», so which population S2 is graded on is his, not mine:
**678** (any branch) · **229** (currency marker) · **449** (`decimal`-only). I draw nothing until it
is answered — a dev-40 from the 678 would put ~2/3 of its threads under posts with no price in them
and the bars would measure the wrong thing.

**5.5b The draw has two strata, not «stratified by channel».** 665 of the 678 (98.1%) are
`@msuaaaa` (447) and `@VARUS_channel` (218). Proportional quotas for dev-40 give msuaaaa 27 / VARUS
13 / **zero from the other seven channels**, and dev-40 + holdout-40 = 80 still reaches no third
stratum. Six of those seven tail channels are in the **PAUSED 39** that §3 removes from collection,
which is a second reason the honest population may be 665. The draw record states its quotas and
what it could not reach rather than implying coverage it does not have.

**5.6 Text-less comments.** SPEC 3.19: they leave the inference queue from the next paid cycle —
a **queue** rule, never a deletion — and «the volume of wordless reactions is itself a signal», so
the wordless class is printed as its own named class beside every distribution over comments. The
S2 draw is taken **after** the queue rule, and the draw record states the count it removed.

**5.7 The five tables (proposal — SP-5).** ids are `uuid5(NAMESPACE, key)` with
`NAMESPACE = uuid5(NAMESPACE_URL, "market-pulse-llm/promo-pulse-1")`, keys normalised (NFC, lower,
whitespace-collapsed) and joined by `\x1f`:
`attribution(window_id, attribution_id ← channel|msg_id|subject_row_id, subject, role, source ∈ explicit|reply_context|post_context)`;
`signal(window_id, signal_id ← channel|thread_root|type, type ∈ жалоба|похвала|спрос|привычка|цена)`;
`evidence(window_id, evidence_id ← signal_id|msg_id|quote, msg_id, quote)`;
`digest(window_id, digest_id ← channel|thread_root, children_ids, cooled_at)`;
`rollup(window_id, rollup_id ← week|chain|brand|metric, value)`.
Existing ids are **not** migrated: `positions.row_id` is already deterministic (`channel:msg_id:ordinal`).

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

## 6. Out of scope

From the phase spec §5, unchanged: brand trends/alerts · Poltava collection · training/LoRA ·
thinking anywhere · vLLM/merge · the schedule **UI** (the loop only READS `data/schedule.json`) ·
dashboard redesign beyond the one promo screen · scanning the 81 unscanned census candidates.

Added by me: no migration of `positions.row_id` to uuid5 (5.7) · no re-scoring of anything bought
under an earlier cap · no edit to `docs/SPEC.md`, any sealed record or any frozen set · no second
positions instrument (the two-stage OCR read and the `brands_visible` channel stay named candidates,
unbuilt, per SPEC 3.18 (2)) · no reopening of bar 2.

---

**Handed to the operator for the team lead's review. Nothing is implemented until «go».**
