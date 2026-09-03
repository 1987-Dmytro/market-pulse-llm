# Review — plan `promo-pulse-1` (2026-08-30, evening) — ACCEPTED, GO on the $0 slice

Team-lead file. Reviews `docs/plans/promo-pulse-1.md` @ `ef8f4a0` against `docs/PHASE-promo-pulse-1.md`
(skill v2.1 §3: checks named · stop-points respected · every threshold listed · nothing silently narrowed).

## Verdict

ACCEPTED. K0–K13 are commands with pass conditions and the end-to-end check is last; SP-0…SP-5 are
asked before, not reported after; §5.10 lists every threshold. Every file claim the plan makes was
opened by the team lead and holds: guard remainder (plan's verbatim read), `results/sku_bar_verdicts_skub2.json`
(bar 2 = 0.4125, 33/80), `results/promo_comment_yield.json` (counts only, 678/4 718; msuaaaa 447 + VARUS 218 =
665), `scripts/retail_census.py:90` (`decimal` = `\d+[,.]\d\d`, matches dates), `src/market_pulse/registry.py:16`
(`_HANDLE`) and `:196`, `tests/test_registry.py:80/158/168`, `scripts/build_aggregates.py:100` (`SystemExit`),
`results/run_5c2_positions.json` (`timing.seconds_per_row` 10.408 vs `go_no_go.page_marginal_seconds` 1.729),
`results/srv2d_cost.json` (2.383×), `results/srv2c_bootlog.json` (`per_day` 0.2333), `results/measurements.jsonl`
(15 rows, no vision s/page), `results/retail_census.json` (group id 1925810730, `username: null`), the store
(newest post ≤ 2026-08-08 on every A1 channel; VARUS/msuaaaa stop at 07-27), `docs/SPEC.md` 3.18 (1),
3.21 (4), 3.22 (1). The plan found five collisions the spec had not seen; nothing was silently cut.

## Rulings — answers to the plan's questions

**SP-0 q1.** S1 `price accuracy ≥ 0.95` denominates over the **promo price only** (the green leg, 80/80),
exact after normalisation. Completeness = gold positions matched on (brand surface form, product, volume)
by a match rule the grader states. Printed `−N%` and the extracted old price are stored and reported as
readings, **no bar**. Labels file `docs/labels-positions-50.jsonl` rows: `row_id · brand · product · volume ·
price_promo · badge_pct (nullable) · price_old (nullable, unscored) · note`.

**SP-0 q2.** The screen does **not** print `price_old`. Phase spec §1 corrected: row = brand · product ·
volume · promo price · printed −N% (absent when none); depth per chain and brand is a **window aggregate**
(SPEC 3.22 (1)), never beside a row's own promo price. `price_old` stays stored and flagged, as today.

**SP-0 q3 — operator's word (30.08):** «Все 678, дро 20/20 по типу». A promo post whose price is in the image
is a price post. Population = all 678. Draw (K7): dev-40 = 20 from the currency stratum (229: `грн|₴|grn`) +
20 from the `decimal`-only stratum (449); holdout-40 the same 20/20, disjoint, frozen at the draw, seed 42.
Bars on the whole 40; per-stratum agreement reported beside them as readings. Channel is recorded per
thread, not a stratum (5.5b accepted). The record names the strata, the predicate (`PRICE_BRANCHES`), and
the wordless-comment count the queue rule removed (5.6). S7 is unblocked.

**SP-1 — operator's word (30.08):** «Go на $0, деньги — на стопе S3». GO = S0 · S1a · S1b · S2 · S3 · S6 ·
S7 · S8, nothing paid. S3 ends in the STOP the plan names: `results/promo_census_c2.json` +
`results/promo_projection_c2.json` (the range) + a freshly re-read guard; the chat carries the two paths
the moment they exist, work continues on S6/S7/S8 meanwhile. Cycle-3 (and option (c), the positions pod
runner) is decided by the operator on that table, by K3's page count — not before. STATUS carries **$2.44**
from now (guard read 30.08); §6.1's $3.17 is retired.

**SP-5 — schema: accepted with amendments** (reference: Project `review-2026-08-27-new-rag-transfer.md` §2,
quoted here so the repo holds it):
1. `signal` key = `channel|thread_root|type|subject_id`, not `channel|thread_root|type` — two complaints in one
   thread about different subjects must not collapse. Columns add `subject_id`, `confidence`,
   `extractor_version` (sha256 of the rendered prompt of the new module).
2. `subject_id` = uuid5 over `(subject_type ∈ chain|brand|sku|post, name normalised)`; a `subject` table or a
   pure function — executor's choice, the key is fixed. `attribution.subject_row_id` → `subject_id`; add
   `confidence`.
3. `digest` adds `version`, `text`, `supporting_signal_ids`, `covers_up_to_msg_id` beside `children_ids`,
   `cooled_at` — the late-comment delta reads digest + delta (phase spec S4), so the digest holds the state.
4. `window_id` is **not** part of any identity in attribution/signal/evidence/digest — week is derived from the
   thread root's post date at query time; otherwise a thread cooling across a tick boundary breaks K10.
   `rollup` keeps `week|chain|brand|metric`.
5. Add `unsure(unsure_id ← channel|msg_id|reason, msg_id, candidates, reason)` — SPEC v2 §4 (в); written by the
   instrument on low-confidence attribution or a class the codebook lacks; the team lead reads it at SP-3.
6. `evidence` as proposed; `span` optional — the substring hook is the check. 7. `unknown-brand`: the store's
   existing state (`brand_id IS NULL` + `brand_raw`) — no wire literal (5.9 accepted).

**Mechanism changes — accepted.** S1a: `_HANDLE` union (`@username` ∪ `+inviteHash` ∪ numeric id), both
directions in tests (`+Ejz…` and `1925810730` accepted; `chan_without_at` still «malformed handle»). §5.2b:
field name `collect: false`, plus `paused_at: "2026-08-30"` and `paused_by: "ruling (ц) 30.08"` on every
paused row; the collector honours it; `segment_for` keeps resolving history; `test_registry` asserts both
directions (a `collect: false` row is loaded and not collected).

## Corrections to the team lead's own spec (my errors, surfaced by the plan's facts)

- **§3: `@atb_market_official` STAYS in A1 as row 17** (images → vision). The census read «без промо» from the
  TEXT regex (price_share 0.12) — but `media_share` is 1.0 and it is the leaflet carrier: all 159 leaflet pages
  of 5c2 and 106 of 145 positions came from it. Dropping it would have cut the one proven S1 source. A1 is
  therefore 17 rows + the ATB_FANatik discussion group = 18 entries; S1b's split becomes 8 in / 10 not.
- §1: `price old` off the screen (q2). §2 S2: population and strata (q3). §6.1: remainder $2.44.

## Plan corrections asked of the executor (edit `docs/plans/promo-pulse-1.md`, ONE commit, before S0)

1. S1b/§5.2b/§5.3: `@atb_market_official` kept in collection; recount the in/not split from the file.
2. §5.7 replaced by the amended schema above (six tables). K10 names `unsure` in its per-table counts.
3. K7 / S7 / §5.5a–b: the 20/20 strata and quotas per q3; SP-0 q3 marked answered.
4. §5.1: after S2 tops up the store, the C2 window anchor is the top-up's last day + 1 — the census record
   states the anchor date and `ids_sha256`.
5. §4 SP-1: reworded — decided at S3's stop on K3/K4; §6.1's number is $2.44.

## Acceptance of this slice

`/report promo-pulse-1-scaffold` when S8 lands. The operator's question the slice answers: «сколько
страниц и текстов купит C2 и за сколько (вилка) — и что уже готово к разметке». First ten lines: K3 counts
per channel (pages · texts · media_share), K4's range against the re-read remainder, the paths + shas of
`results/promo_threads_draw.json` (dev/holdout, strata) and of the registry r2. The team lead re-runs at
acceptance: K0s at HEAD, K2, K7 twice (sha), K11's negative control; opens the census and projection files.
Labelling: dev-40 threads (sessions of 10) start the day the draw lands; the 50 positions after S4.

---

## Acceptance of the scaffold slice (30.08, 18:40) — GREEN, with rulings for the next slice

Report `docs/reports/promo-pulse-1-scaffold.md` @ `76014ba`. Opened: `config/registry.yaml` (74 rows,
35 collected / 39 paused), `results/raw_v1_baseline.sha256` (six files, sealed 06.08, read by
`tests/test_raw_store.py`), `scripts/collect_r2.py :: refuse_pinned`, the seven commits. The team
lead's own `make check` at `76014ba`: see STATUS. S2 stopped at SP-4 BEFORE an irreversible append —
that is the process working (Dv5 is a merit, not a debt).

**SP-4 — ruling (a), widened to the loop:** v1 raw store is an ARCHIVE, read-only forever (the
baseline stays the proof). ONE live root — `data/raw_r2/` (name: executor's) — receives S2's top-up
for ALL channels and, later, every tick (S12). `RawStore` reads v1 ∪ r2, deduplicated on
(channel, msg_id), r2 wins; consumers counted (`graphify query "what reads RawStore"`) and named in
the plan revision; a guard refuses any write into v1 in both directions (test). Repo precedent:
`fetch_comments_v2.py` («`data/raw/comments/` is never opened for writing»).

**K7 — draw NOW** over the 678 price threads of the frozen v1 store (the frozen holdout comes from
the frozen store — no better population exists); eligible after the wordless rule = 488 (182 / 306);
strata 20/20 currency / decimal-only for dev and for holdout, disjoint, seed 42; the record pins
`results/raw_v1_baseline.sha256` as the population's provenance. Dv7 closed by this ruling.

**Registry r2 — three corrections (one commit):** `@znishkom` («ЗнижКом | Ігрові Знижки», Steam
discounts, dairy 0.0, theme-screen exclusion 07.08; the census title-matched the chain name) →
`collect: false`, `paused_by: "review 30.08 — off-category, census title-match false positive"`.
`@marketopt_promo` (public) STAYS collected beside the private one — Dv3 closed, A = 18 rows +
group. **B (Poltava, 17 rows) → `collect: false`, `paused_by: "deferred to phase B (ruling (ц) 30.08)"`**
— phase spec §3 says «nothing collected»; r2 left them collecting.

**Dv2 (revision chain) — accepted in principle**, the repo's own precedent (SPEC.md keep-strip);
conditions before the first PAID step: `/code-review` (fresh subagent) on the S1b+S6 diff —
correctness and stated-requirement gaps only, verdict quoted in the next report; a test in the
refusing direction (a corrupted r1 line → the chain refuses); `make preflight` naming the reached
revision for the two r2 paths instead of listing them as differing (a debt if not now).
Dv1, Dv4, Dv6 — accepted as reported.

**Money — operator's word (30.08): «Да, смок авторизован».** After S2 and K3: ONE smoke of the
vision leg, ≤30 pages, estimate ≈$0.15, **cap $0.35**, four rungs per `docs/PROCESS.md`, teardown
proven by listing; it writes `vision_seconds_per_page` into `results/measurements.jsonl` and K4
then emits ONE number against the re-read remainder. The cycle-3 / narrowing / pod-runner word is
the operator's on that table — the smoke is the only paid step authorised.

**Next slice = `promo-pulse-1-s2s3`:** plan revision (S2 root + consumers, one commit) → registry
corrections → K7 → S2 top-up into r2 → K3 census (anchor = top-up's last day + 1, `ids_sha256`) →
smoke → K4 → `/report promo-pulse-1-s2s3` (the operator's question: «сколько страниц купит C2 и по
какой измеренной ставке — и что готово к разметке»). Fresh session; DONE WHEN predicate below.

---

## Acceptance of slice s2s3 (30.08, ~21:00) — GREEN; SP-1 open on ONE number

Report `docs/reports/promo-pulse-1-s2s3.md` @ `ee23a13` (12 commits). Team lead's own readings:
`make check` at `ee23a13` = **4 205 passed · 2 skipped · exit 0**; `shasum -c raw_v1_baseline` = 6/6 OK;
`runpodctl serverless list` = `[]`, `pod list -a` = `[]` (own listing); guard = REMAINING **$2.3202**;
draw sha `6f9fa245b9d70254`, 20/20 + 20/20, disjoint (recomputed from the file). Opened: census
(window 03–31.08, ids_sha256, 968 leaflet posts), projection (marginal bound derived, nothing typed),
prereg_smoke (committed before create). Dv8–Dv11 accepted; the two moved tests verified not weakened
by their commit messages' own claims and K0's count. The `/code-review` finding (`collect_5c1.py ::
collectable` ignores `collect: false`) — fix ruled in, `docs/PROMPT-c2-pagecount.md` item 2.
The measured rate closes the rate question: **7.872 s/page boot-inclusive (n=30), marginal
2.623–3.369**. What remains for SP-1 is the PAGE COUNT (1 022…9 653; manifests know 63 posts) —
contract `docs/PROMPT-c2-pagecount.md` ($0) resolves it from store/metadata; the operator's word
(cycle-3 / narrow / pod runner) is asked ONCE, on that number. Labelling of dev-40 is unblocked.

---

## Ruling 01.09 — cycle-3 opened; ONE goal to the end of the phase; the relay protocol is fixed

**Operator's word (01.09, quoted):** «Цикл-3 = весь баланс, потолок $4.8». Executor: open cycle-3 in
the guard as a NEW anchor at the current balance with `CYCLE3_CAP_USD = 4.80` — a sidecar/new cycle,
no sealed cycle-2 record edited; the four rungs and per-leg caps stay (C2 backfill ≤ 2× its
projection from the pagecount table; C3 dev loop cap $2.5; holdout ≈$0.3); projection over the
CEILING → STOP, and if the page count prices C2 over its share, cut pages EVENLY per chain and say
so in the report — never silently. The money stop-point of the phase spec §6.1 is SATISFIED by this
word; no further money stop unless a rung fires.

**Process retro (operator's red gate, accepted):** three team-lead formulation errors caused the
slice pile — (1) stop-points issued without their decision table, so each stop spawned a
fact-finding contract; (2) handovers assumed session state, twice wrongly; (3) predicates were cut
per slice instead of one per phase. Fixed in `docs/PROCESS.md` (§Cadence 1 and 3) and proposed into
the skill as v2.3. From here: ONE `/goal` (phase spec §8, now covering pagecount → S4 → S5 → S9–S14 →
gate), STOPs are pauses, and the operator's resume line is CONSTANT:

> Fresh session: read docs/plans/promo-pulse-1.md, the newest section of
> docs/reviews/2026-08-30-plan-promo-pulse-1.md and docs/plans/promo-pulse-1.STOP.md; apply the
> ruling, delete the STOP file, re-enter the /goal from docs/PHASE-promo-pulse-1.md §8.

Expected STOPs left in the phase (each a pause, not a question-in-chat): «waiting on the team
lead's labels» (twice: dev-40, positions-50 — cleared the moment `docs/labels-*.jsonl` land),
possibly «dev-loop plateau» (SP-3 — the team lead reworks the codebook), and pre-registration
notice before the ONE holdout shot. Everything else runs inside the ceiling.

**Correction 01.09 (operator's catch):** only the USER can invoke `/goal` — a prompt cannot
«re-enter» it, and the evaluator reads only the transcript. The resume protocol is therefore ONE
constant paste: the single-line predicate of phase spec §8 v2 (start ritual folded in, every check's
output shown in-conversation), pasted fresh at start and after every STOP. The earlier two-line
protocol is void.

---

## Ruling 01.09 (later) — the fork is VOID: the operator topped up; ceiling $7.00; C2 runs whole

**Verified by the team lead's own reads:** RunPod balance **$14.3730** (guard's `balance()`; the
operator's «я внёс последние 10 долларов» landed: $4.48 → $14.37); cycle-3 spent so far $0.0972
(volume drip only), nothing bought.

**Operator's words (01.09, quoted):** «Сверь остаток — я внёс последние 10 долларов» · «Потолок
$7.00, резерв не трогаем». Executor: raise `CYCLE3_CAP_USD` to **7.00** (the operator's word, not a
mid-run raise; note it in the ledger's `note`), anchor unchanged. The remaining ≈$7.4 of balance is
RESERVE — outside the phase, not to be planned against.

**Both STOP parameters are void:** C2 buys ALL 3 008 pages (≈$3.16 at the pessimistic marginal);
C3 keeps its caps ($2.50 dev + $0.30 holdout); no page cut, no pod runner, no volume deletion.
The STOP's second question (which pages survive) is moot.

**Conditions before the FIRST paid leg (standing, from the scaffold acceptance):** `/code-review`
(fresh subagent) on the money-guard diff of this pause — `0a8d02a` (cycle-3 line) + `d305953` (the
ledger tripwire) + the cap change — correctness and stated-requirement gaps only, verdict quoted in
the report. The tripwire's own negative control (a throwaway test writing to a real ledger fails
the teardown) is accepted as reported; keep it.

**Team lead's debts, named:** `docs/labels-promo-dev.jsonl` (dev-40) — in progress, lands in
batches of 10; `docs/labels-positions-50.jsonl` — after S4's draw. The executor proceeds through
S4 → draw-50 → tick → screen while blocked checks wait on these files, and STOPs only per §8.

---

## Ruling 02.09 — re-anchor cycle 3 by the operator's top-up; the /goal launch protocol; §8 v3

**Acceptance of the 02.09 pause (`docs/reports/promo-pulse-1.md` @ `11bdbf6`) — GREEN as a PAUSE.** Team lead's
own readings: `make check` @ `11bdbf6` = **4 266 passed · 2 skipped · exit 0** (11 min 35 s); `dashboard/promo.html`
sha `28fffc93c723ab8d…` (matches); `results/positions_draw_50.json` drawn twice → `a3f659f9a8d73f5e…`,
`results/truth_20.json` twice → `3d80c81a9c353130…`; `results/promo_screen_data.json`: 145 positions · 89 rollup ·
signal/attribution/evidence/digest/unsure = 0 · 6 weeks; `git status --porcelain` on the contract paths empty; guard
(own run): `REFUSED: the balance ($14.23) is above CYCLE 3's anchor ($4.48)…`, `CYCLE 3 SPENT $0.2431 of $7.00`, exit 1.
Fresh reviewer on `97e84e6` (money): **VERDICT OK**, 3 notes — (i) `--step X --close --note` on a refused run still
writes the step ledger and a witness reading into the live ledger (by design, `:911`) — «byte-identical / sessions []»
holds only without `--step`; (ii) the held closing now FOLLOWS the step witness in `sessions` — nothing may derive
«closed» from `sessions[-1]`; (iii) an exception inside the `--step` block after the hold loses the closing while the
step ledger is written — line stays open, re-runnable, safe direction. Dv15 accepted `[cause: process]`. Named debt
stands: `promo_projection_c2.py` (`:366` / `:171` / `:153`) — K4 is not re-run until it is fixed; a one-sentence
contract after the phase, not on its critical path.

**Root cause of the pause — the team lead's, not the executor's.** Ruling «01.09 (later)» said «anchor unchanged»
after a +$10 top-up; the guard's invariant refuses on a balance ABOVE the anchor (`scripts/runpod_guard.py` `:96–98`,
`:113–116`). The balance was read (`balance()`), the refusal was never run (`enforce()`). The executor was right not
to weaken it. Lesson → skill v2.4 §5: a ruling that touches a guard is RUN through the guard before it is issued.

**Operator's word (02.09, quoted): «Да: якорь + $10.00».** Executor, in the START RITUAL of the next session, ONE
write to `results/spend_cycle3.json`: `runpod_balance_at_cycle3_start` := **14.4799665639** (the opening anchor
4.4799665639 + the operator's stated top-up $10.00); `anchored_at` UNCHANGED (`2026-09-01T06:34:08+00:00`);
`cycle3_cap_usd` stays 7.00; APPEND to `note`: «RE-ANCHORED 2026-09-02 on the operator's word «якорь + $10.00»
(ruling 02.09): anchor = opening anchor + the stated $10.00 top-up; anchored_at unchanged, so the billing walk keeps
the drip already spent». No other field moves; no test weakened. Show `python3.11 scripts/runpod_guard.py` → exit 0,
`anchor $14.48`, `balance delta` ≈ `billing since` (≈$0.25 vs ≈$0.24 — the max is the reading), `CYCLE 3 SPENT ≈
$0.25 of $7.00`, `REMAINING ≈ $6.75`. Commit the ledger by path, message naming this ruling. Then rung 0
(`--step promo-pulse-1 --step-cap 3.20`) and S4 as the plan says. If the guard still refuses after the write: STOP
with its stderr — the anchor is not touched a second time.

**The /goal launch protocol — read from the three transcripts of 01–02.09 (`~/.claude/projects/…market-pulse-llm/`):**
(1) 01.09 08:18 — the whole paste went as plain text (`promptSource: typed`, no `<command-name>`): no goal, no
evaluator; the executor read «stop after 80 turns» as its own rule and stopped at 35 min. (2) 01.09 19:16 — `/goal`
typed by hand → «Goal set», but the args were cut at the predicate's own inner «/goal» (3 286 of 3 336 chars; the turn
cap and the resume sentence fell off) and no turn started for 12 h. (3) 02.09 07:55 — 77 min, a legitimate PAUSE;
the evaluator fired once and complained the condition was cut mid-sentence. Fix, standing: the operator TYPES
`/goal ` and pastes the BODY from §8 v3 (no slash command inside it; the file's bytes = the paste); «Goal set:» with
no tool call → one word, «go». PROCESS §Cadence 3 and skill v2.4 carry it.

**§8 v3 (mechanical, same contract):** the inner «/goal» token removed from the PAUSE clause; floor (j) raised to
the proven count 4 266 (own run); the code block holds the BODY only. Expected STOPs unchanged: «waiting on labels»
(dev-40, positions-50), plateau, holdout notice. Team lead's debts unchanged: `docs/labels-promo-dev.jsonl` (dev-40,
batches of 10), `docs/labels-positions-50.jsonl` (after S4 — the draw on disk is PRE-C2 population, re-drawn after S4).

---

## Ruling 02.09 (b) — S4's step cap is $3.95, the whole step, text leg FIRST; the dev loop takes what remains

**Acceptance of the second pause (`docs/reports/promo-pulse-1.md` @ `99e1a24`) — GREEN as a PAUSE.** Team lead's own
readings: guard exit 0, `anchor $14.48`, `CYCLE 3 SPENT $0.2722 of $7.00`, `REMAINING $6.7278` (the drip keeps walking);
`runpodctl serverless list` → `[]`, `pod list -a` → `[]`; `results/post_media_promo_c2.json :: totals` = 968 posts fetched,
0 unreachable, 3 008 images = 3 008 expected, 17 of 17 channels matching the pagecount; 3 008 files on disk (573 MB,
gitignored); `results/prereg_promo_c2.json :: rung_0` table read — cheap $2.6041 · priced $3.5241 · dear $3.6059 against 3.20,
`fits` false; `make check` @ `99e1a24` = **4 278 passed · 2 skipped · exit 0** (own run, 11 min 30 s); porcelain on the
contract paths empty. The rung fired for the team lead's reason: 3.20 was set from `verdict.c2_priced_usd`, which priced the
vision leg alone — the text leg (405 posts) and the second boot were never in that number. The executor was right to stop
before creating anything and right not to re-price at a kinder corner.

**Operator's word (02.09, quoted): «$3.95 — весь шаг».** The ceiling ($7.00) and the reserve are untouched — this is the
split inside the ceiling, and it is ruled as follows:

1. **`STEP_CAP_USD = 3.95`** in `scripts/run_promo_c2.py` (one constant), a fresh `--register` (rung 0 must print `fits`
   true at the dear corner: $3.6059 + the one-job reserve $0.2843 = $3.8902 ≤ 3.95), the guard's step anchor with
   `--step promo-pulse-1 --step-cap 3.95`, then `knowledge/runbooks/promo_c2_paid_leg.md` top to bottom, TODAY — the
   room is a clock ($0.2333/day) and every day of delay comes out of the dev loop below.
2. **The text leg runs FIRST.** Today the driver buys pages by channel and the 405 text posts last; under a cap gate that
   puts the cheapest, surest, cross-chain data (≈$0.35 at the registered 2.8132 s) behind the dearest. Reorder: (10)(a)
   warm-ups → `post_leg` → the re-projection → the leaflet loop in the spec's channel order (unchanged). Check: `--dry-run`
   prints `post_text` as stage 0; `results/run_promo_c2.json :: stages[0].after == "post_text"`; the stub-driven tests
   still pass and ONE new test pins the order. No existing test is weakened; the channel-order test stays as it is.
3. **Mid-run: no cap raise, ever.** The gates decide — the (10)(a) gate, the re-projection after every channel, the per-pack
   cap gate. If the run stops on any of them, the unbought channels are recorded (`outcome.unbought`) and the next STOP
   carries the table: channel · pages left · $ at the measured marginal. A realised rate like 5c2's 10.408 s/page is the
   expected way this happens — it is a result, not a failure.
4. **Which side gives: the dev loop, never the holdout.** After S4 settles, C3's dev-loop cap = min($2.50, REMAINING −
   $0.30 for the holdout); its floor is **$2.00** — below that, STOP for the operator's word before the first dev run. The
   holdout's $0.30 is protected and pre-registered as before.
5. After the run: teardown proven by `runpodctl serverless list` → `[]` and `template` gone; the step's spend line
   (`results/spend_promo_pulse_1.json`, settled by `--close`) named in the report; `results/positions_draw_50.json`
   RE-DRAWN over the C2 population (seed 42, twice, one sha) — the pre-C2 draw is superseded, said so in the record.

**Evaluator note (no predicate change):** both Stop-hook passes read the pause correctly («met AS A PAUSE») yet returned it
as feedback; two cheap extra turns. The C6 redesign (`make done` printing STATE=COMPLETE|PAUSED|RUNNING) removes the
ambiguity; §8 v3 stays byte-identical until then. Team lead's debts unchanged: dev-40 labels in batches of 10;
positions-50 after the re-draw.

---

## Ruling 02.09 (c) — the (10)(a) gate goes per LEG and per CHANNEL; S4 buys whole channels in value order until the money stops; cap $3.95 unchanged

**Acceptance of the third pause (`docs/reports/promo-pulse-1.md` @ `9ce3c0a`) — GREEN as a PAUSE; the gate did its job.**
Team lead's own readings: guard exit 0, `CYCLE 3 SPENT $0.3516 of $7.00` (delta; walk $0.2917), `REMAINING $6.6484`;
`results/spend_promo_pulse_1.json` anchored $14.1883, one session, $0.0599 by delta («0 pages, 0 posts bought; one boot + two
warm-ups»); `serverless list` → `[]`, `pod list -a` → `[]`; porcelain on the contract paths empty. Run 1 bought a boot and two
warm-ups ($0.0579 at the rate) and refused before the first gold call — exactly what SPEC 3.17 (10)(a) is for.

**What the files say about the rate.** The population is not one population: pages per post — `@atb_market_official` 6.7,
`@ATB_FANatik` 7.8, `@kopiyochka1` 8.6, `@blyzenkoua` 5.7, `@atb_aktsiyi` 4.7 (leaflet albums) against `@epicentrk_sale` 0.6,
`@rrozetka` 0.7, `@silposilpo` 1.0 (single promo photos) (`results/promo_pagecount_c2.json` ÷ `promo_census_c2.json`). The smoke's
2.623–3.369 s/page was VARUS 18 · atb_aktsiyi 6 · msuaaaa 4 pages; ATB leaflet pages read 10.408 s (5c2, n = 205) and 13.466 s
(run 1, n = 1). A whole-step projection at ANY single rate is wrong in both directions: the rate is a property of the channel and
the paid transport, and it is measured per channel, on the run.

**The three answers (plan revision — log Dv `[cause: ruling]`; nothing narrowed silently):**
1. **Per leg — yes.** The text leg (385 posts) is projected on its own and bought as stage 0. It is never refused for the page leg.
2. **Per channel, measured by the channel's own first pack.** (a) The first pack of each channel (the transport's pack size) is
   its measurement: worker seconds per page, n = pack size, max — one row per channel in `results/measurements.jsonl` (`source`
   = this run's record). (b) The channel's remainder is projected at ITS measured rate against the room — cap − step spent − the
   one-job reserve ($0.2843) − the idle tail; fits → the channel runs whole; does not fit → its remainder is left UNBOUGHT, recorded
   per SPEC 3.17 (10)(b), and the next channel starts. (c) The run ends when the room is below one pack at the worst measured rate
   plus the reserve. The per-pack `cap_gate` stays as the hard stop. The whole-step page projection is RETIRED for this step:
   the test that asserted the whole-step refusal changes BY THIS RULING to assert the new law in both directions on the stub —
   a channel that fits runs whole, one that does not is skipped whole, the text leg is bought regardless of the page rate.
3. **Order (operator's word 02.09, quoted: «АТБ → дешёвые → малые»).** Stage 0 text → `@atb_market_official` whole (the
   leaflet carrier, 209 pages) → the smoke-measured channels `@VARUS_channel`, `@atb_aktsiyi`, `@msuaaaa` → every other channel
   ascending by page count (fozzy 3 · xochydeshevshe 7 · forainfo 11 · ekomarket 17 · silposilpo 34 · marketopt 52 · sim23 57 ·
   epicentrk 78 · rrozetka 113 · ATB_FANatik 133 · blyzenkoua 328 · kopiyochka1 396 · kop1chat 528). Derived in the driver from
   `promo_pagecount_c2.json` and the smoke's population file, not typed as a list; `--dry-run` prints it; `--register` again.

**Money.** Cap $3.95 stands. Room for pages today ≈ $3.95 − 0.0599 − 0.0938 − 0.2843 − one boot ≈ **$3.46**. Expected: ATB
≈ $0.9 at 13.5 s, the trio ≈ $1.1 at 3.4 s, then the small channels; the big albums (blyzenko · kopiyochka1 · kop1chat, 1 252
pages) are the likely remainder. One boot; teardown proven by listing; the step ledger stays OPEN (`--note` reading, no
`--close`) — the remainder, if bought, runs under the same step. C3's rule from (b) item 4 is unchanged.

**Before the next STOP, all $0 (the decision table for the remainder):** (i) the measurement rows above; (ii) the remainder table —
channel · pages left · measured s/page (or «unmeasured») · $ at its rate; (iii) a $0 RANKING instrument for the remainder, measured
before it is trusted: caption-lexicon rank for photo posts (dairy/ice-cream terms of `lexicon.yaml`, read-only) and, if
`tesseract` + `ukr` install in one `brew` command, OCR rank for leaflet pages — page-level recall on 5c2's 159 ATB pages against
`results/run_5c2_positions.json` (pages with ≥ 1 position); the table shows $ whole vs $ top-ranked at recall ≥ 0.90. Then the
STOP «unbought remainder» (a projection over the cap — a listed pause type) so the operator decides in ONE visit: buy whole ·
buy ranked · stop. S5's re-draw (seed 42, ≥ 3 chains) runs over what was bought; S1's bars are unchanged.

---

## Ruling 02.09 (d) — the C2 window is its own sealed window in the same DB (shape 1); the ledger test derives the live line; S4 is bought

**Acceptance of the fourth pause (`docs/reports/promo-pulse-1.md` @ `168ecc8`) — GREEN as a PAUSE; S4's money leg is DONE.**
Team lead's own readings (03.09 morning): guard exit 0, `CYCLE 3 SPENT $3.4437 of $7.00` (walk: serverless $2.9347 + volume
$0.4472), `REMAINING $3.5563`; `results/spend_promo_pulse_1.json` — two sessions, run 2 `$3.0335` by delta at 17:09Z; listing
`[]` / `[]`; `results/run_promo_c2.json :: runs[-1].unbought` = 0 pages · 0 posts; `data/derived/leaflet_pages/` = **3 167 rows
in 17 channels** (159 of 5c2 + the 3 008 of C2, every channel's count = `promo_pagecount_c2.json`'s); porcelain on the contract
paths empty. The per-channel law paid for itself twice: the text leg passed its own gate ($0.19 where the whole-step law would have
refused at ≈$11 again), and the rates ran 0.80–12.92 s/page across channels, the carrier at 5.23 s against its 11.7 s n=1 warm-up.
Ruling (c)'s expectation («12–14 chains, the big albums unbought») was too pessimistic: all 17 ran whole for $3.03. The ranker's
answer is a measured NEGATIVE and is accepted as such: at recall ≥ 0.90 the OCR rank keeps 100 % of pages (no cut exists), the
caption rank scores 0 — `results/rank_remainder_c2.json`; the instrument stays on the shelf, unused. The two harness kills
(≈$0.09 re-asked, nothing written twice) are logged beside the money; the runbook gains the rule: a paid run is launched detached
(`os.setsid`, output to a file, the PROCESS watched), never as a foreground call.

**The fork — shape 1, and nothing else.** `data/derived/pulse.db` gets a SECOND window, not a weaker seal:
1. **The C2 window's sealed record is `results/prereg_promo_c2.json`** (the S4 registration: population by ids, pagecount,
   manifest, rates). It pins the registry it was bought under — `config/registry.yaml` at revision r2, `eff8ba5b…` — added to
   `pinned_inputs` by the registration's own writer (`--register`, a dated addendum field; never by hand, never re-pinning what
   is already there). Window id: as the aggregate schema names its windows (`windows.window_id`; the plan's §5.7 convention) —
   the executor picks it and says so in the record; `w1` stays 5c2's.
2. **`scripts/build_aggregates.py` builds ALL windows into the one DB**, each window through ITS OWN seal: 5c2 → `w1` through
   r1 (`prereg_5c2_run.json`, exactly as today); C2 → its window through r2 (`prereg_promo_c2.json`). A row belongs to a window by
   that window's pinned population ids (the 20 D-cut posts belong to both — one position row, two windows: `window_id` is a key
   of the aggregate tables, never of the position's identity). `segment_for` keeps its law per window: a row whose channel the
   window's registry does not carry refuses, SPEC 3.20 (1). Brands and watchlist per window from its own seal (one lexicon pin).
   **No live-registry read anywhere in the build** — shape 2 is refused for the reason the STOP itself gives; shape 3 is refused
   because the phase's artifact IS the C2 screen.
3. **Checks that close this:** the `w1` mirror verdict (`aggregates.converge`) and the `w1` export sha are byte-identical before
   and after — a test pins it; the C2 window shows positions for all 17 channels; the 32 fixture-driven tests turn green by
   WIRING the second prereg into the fixtures, with no assertion weakened; `make tick` twice → zero new rows per table; the screen
   (`make promo-screen`) reads the C2 window; the clean-clone check (h) as before. Then S5's re-draw over the C2 population.

**Check (j), the second ruling — the test's pointer is stale, not its claim.** `tests/test_repair_phase4_ledger.py :: LINE_LEDGER`
names `results/spend_cycle2.json` as «the live ledger»; the guard's live line has been `results/spend_cycle3.json` since 01.09
(cycle 2 SUPERSEDED, `CYCLE3_LEDGER`). Change BY THIS RULING (Dv `[cause: ruling]`): the test DERIVES the lines a paid run may be
witnessed in from the guard's own constants — `PHASE4`, `CYCLE2_LEDGER`, `CYCLE3_LEDGER` — the same lesson as the tripwire
(`97e84e6`: derive, never restate); the claim is unchanged: a paid step witnessed by NONE of the guard's lines is still named,
both directions shown on the stub. Nothing else in that file moves.

**Money, closing S4.** The step ledger is closed by `--close --tolerance` in the START RITUAL once the billing walk has settled
against the delta (the guard's own rule); the settled line is the spend line check (c) names. C3 keeps `min($2.50, REMAINING −
$0.30)` = $2.50 today; the drip ($0.2333/day) is on the clock — the dev loop starts the day the labels land.

**Team lead's debts (the critical path, from here):** `docs/labels-promo-dev.jsonl` (dev-40, batches of 10, draw sha
`6f9fa245…`) — starts 03.09; `docs/labels-positions-50.jsonl` after the re-draw. No further money word is needed in this phase
unless a rung fires.

## Ruling 03.09 — dev-40 labels LANDED (140 lines, codebook v1); the prompt's law is re-rendered from the codebook BEFORE the first paid K8 run; the codebook is a team-lead file

**The open STOP (the fourth, 02.09 — the DB-window fork) is answered by Ruling 02.09 (d) above and NOTHING in it moves:** shape 1,
`prereg_promo_c2.json` as the C2 seal with the r2 registry pinned by the registration's writer, all windows built into the one DB each
through its own seal, `LINE_LEDGER` derived from the guard's constants, S4 closed by `--close --tolerance`. This ruling ADDS the labels'
arrival and the prompt-law contract; apply (d) and this together, then delete the STOP file. The «waiting on the team lead's labels
(dev-40)» line of that STOP is closed by the file below; positions-50 stays owed after the re-draw.

**What landed (team lead, 03.09, $0).** `docs/labels-promo-dev.jsonl` — 140 lines, sha256 `302113b8ae3c9598…`, ALL 40 dev threads
of the draw (`results/promo_threads_draw.json`, sha `6f9fa245…`, seed 42), one line per comment WITH TEXT: 208 comments − 68 wordless
= 140. Wordless comments (`text.strip() == ""`; the draw's `n_wordless`) are NOT labelled — SPEC 3.19 takes them out of the inference
queue, the prompt's rule 4 does not label them, so the grader's denominator is comments with text; a gold line for a wordless comment
is a defect. Self-check passed on every line: valid JSON, exactly the schema's fields (+ optional `unsure`), enums closed, `msg_id` in
its thread, `quote` a non-empty verbatim substring, every comment with text covered, no holdout id. The law the gold is labelled by
is `docs/CODEBOOK-promo-signals.md` **v1 · 2026-09-03** (sha256 `6a74bc81cd2a922d…`); the dev-loop report cites that version.
Reading of the gold (a reading, not a bar): subject types chain 56 · post 53 · sku 30 · brand 1; signals жалоба 40 · спрос 22 ·
похвала 12 · цена 10 · привычка 0; 63 lines carry no signal (23 admin replies, 14 noise, 26 neutral); 6 of 40 threads have an
EMPTY signal set (Jaccard 1.0 only if the model also says nothing); 7 lines carry `unsure` and stay in the denominator. Per stratum:
currency 61 lines (sku-heavy: boxes, chips, beer), decimal_only 79 lines (chain-heavy: VARUS support, app, loyalty).
START RITUAL: commit `docs/labels-promo-dev.jsonl` and `docs/CODEBOOK-promo-signals.md` by path, nothing edited.

**Ownership.** `docs/CODEBOOK-*.md` is a TEAM-LEAD file (PROCESS.md §File ownership names it as of today). Harness contract, ONE
line, one commit with the labels: add `"Edit(/docs/CODEBOOK-*.md)"` to `permissions.deny` in `.claude/settings.json`. Nothing else
in the harness moves.

**The prompt carries the annotator's law — so the law is re-rendered BEFORE S9's first paid iteration.** `promo_prompts.CODEBOOK`
(the Ukrainian block) was written before the codebook existed and disagrees with v1 in the places the grader scores. The executor
rewrites that block to carry the deltas below (its own words, Ukrainian, the model's language), `codebook_version()` moves, the
tests that pin the sha are updated with no assertion weakened, and the RENDERED prompt for one dev thread (`render(...)` on
`@VARUS_channel` root `6009`) is shown in the report — the team lead reads it at $0 before any pod exists. The deltas:
1. **about — exactly ONE subject per comment with text; every such comment gets an about-row.** Two explicit subjects → the one
   the comment OPENS with (the other may appear in a signal row). Wordless comments: rule 4 unchanged.
2. **`post` is the post or the CHANNEL as the object, and it is where noise goes.** Emoji-only, greetings, bare «дякую/спасибо»,
   punctuation, tags, off-topic («Слава ЗСУ»), banter between commenters, and the channel's OWN replies (admin: «Розуміємо вас»,
   «передали», «Фото вже прибрали», «напишіть у чат @varusua_bot») → `subject_type: post`, `subject: <root msg_id as a string>`,
   NO signal. A comment about the post/channel itself carries signals ONLY in an aggregator channel (msuaaaa: «на фото
   неправильна ціна» → post, жалоба + цена; «канал не о скидках, а о треше» → post, жалоба). In the RETAILER's own channel
   (VARUS) the channel, its posts and copy, app, site, loyalty program, support, hotline and promo mechanics are the chain →
   `chain` / `VARUS`. A `post` row is an answer, never an `unsure`.
3. **Surface form of `subject`: nominative; the POST's spelling when the entity is in the post** (`VARUS` even when the comment
   writes «варусу»; `McDonald’s` with the post's apostrophe; `Сільпо`, `KFC`, `Roshen`), otherwise the comment's spelling in
   nominative («масло», «атб», «рошен»). `sku` = brand + product type as written in the source text (`чипси Люкс`, `ПИВО BAVARIA`,
   `Щастябокс`, `МакМеню`, `курячі чіпси`) — NO volume/weight/fat unless the post lists several variants of one product. Chain
   named nowhere in the thread → the channel handle without `@`.
4. **Signals.** `спрос` = interest in the offer: availability / where / until when / what is inside → the PRODUCT (`sku`/`brand`);
   promo mechanics (promo code, coupon, voucher, app, kiosk, cashback, delivery, «у Вінниці є ваш магазин?») → the CHAIN; a request
   to the aggregator for another chain's promos («Нових знижок атб ще не виклали?») → that chain, explicit. `цена` includes the
   correctness or unit of a printed price («ціна на фото вірна», «це за 100г ціна?»). Pairs are BOTH types: «дорого», «500 грн за
   картонку» → цена + жалоба; «класна ціна» → цена + похвала. A grievance question («Що з бонусами, у мене нуль») → жалоба, not
   спрос. `привычка` needs a REGULARITY word (постійно, завжди, щотижня, регулярно, роками) — a purchase count («перший раз… вчора»,
   «декілька разів купувала») is not one. Thanks WITH an object («дякую за вашу працю») → похвала to the addressee; bare thanks →
   noise. Sarcasm by meaning: «Торгівля повітрям», «Потужно-незламний», «Шикарно. Цілий день тиша, а потім скидка» → жалоба.
5. **Neutral comments keep their subject and carry NO signal** — explanations, factual answers, clarifications, jokes without an
   evaluation («так працює система», «Або з 9 числа», «Працює 5%»); the model must not invent a signal to fill the row.
6. **`unsure` remains for a subject that cannot be established from post + thread**; noise is not unsure (2).

**Checks around the gold, all $0.** The gold passes the same hooks the model's output passes (msg_id exists · quote substring ·
schema) — run them on `docs/labels-promo-dev.jsonl` as a fixture once; a hook that refuses a gold line is a hook bug or a codebook
question, reported, never patched around. K8's first reading on dev-40 IS S9 iteration 1 — no paid iteration was to run on a
partial gold, and none is needed: the gold is complete. Optional, plan-named or not at all: the channel's own account has a stable
`sender_anon_id` (VARUS `2fa2b7…`, msuaaaa `58805a…`); rendering `[admin]` beside those comments would let the model apply (2)
mechanically — a scope change, allowed only if the plan names it.

**Team-lead debts from here.** `docs/labels-positions-50.jsonl` — after S5's re-draw over the C2 population
(`results/positions_draw_50.json`): STOP «waiting on the team lead's labels (positions-50)» names the draw's sha. Holdout-40 is
labelled by the team lead only AFTER the pre-registration STOP notice; the executor never sees `docs/labels-promo-holdout.jsonl`
before the ONE shot.

## Ruling 03.09 (b) — the fifth STOP: fork 1 = SPLIT the derived store (shape 2); fork 2 = `carrier` joins the key, the test's claim is re-scoped; the render is READ and accepted (+1 line); K6's gold is PAGE-level; S9 iteration 1 may start after the smoke, with its decision table; `/goal clear` ends a pause

**Accepted, by diff and by files, $0:** `1161187` (w2 through its own seal — `w1` 902/902 mirror leaves, `w2` 17 channels · 1 113
positions), `abe6e18` (ledger lines DERIVED from the guard's constants — the one test ruling 02.09 (d) named), `7c93fb0` (CODEBOOK
re-rendered; `codebook_version()` `a97d3c71…`), `6b6fe44` (the grader proven four directions against the shipped gold — 1.0/1.0 · subject
0.0 with signals 1.0 · signals 0.15 = 6/40 with subject 1.0 · silence both red; the share DERIVED), `b74123f` (dev-40 corpus and the dry
run: 40 renders, 209 897 chars, bound $0.29–$1.66 per iteration on a BORROWED rate and said so). The report `docs/reports/promo-pulse-1.md`
answers the question in its first four lines. **4 268 ≥ 4 266**: (j)'s count half is met; its green half is the two forks below.
Nothing silently narrowed; the seven reds the `--window w2` default caused were the executor's own and are fixed the right way (the
fixture names its window).

**Fork 1 — shape 2, the SPLIT. Ruled, with the check that closes it.** A seal is a statement «these bytes made this»; a seal whose bytes
move is not re-scoped into prose, it is restored. The C2 run only APPENDED (23 of 38 sealed sources unchanged, 15 an exact byte prefix,
0 diverged — measured by the executor), so the derived store splits the way the raw store did on 30.08 (v1 archive frozen, r2 live):
1. `data/derived/` returns to 5c2's bytes: every one of the 38 sealed sources hashes to its sealed value. The C2 rows move to their own
   root — the executor names it (the plan's S4 «write target `data/derived/`» is amended by THIS ruling, Dv `[cause: ruling]`: each
   window writes under its own root; C2 and every later tick under the new one). The 20 D-cut posts stay in w1's root and w2 reads them
   from there, as ruling (d) already says.
2. Order of operations is the safety: **copy first, verify, then cut.** A script writes the appended lines to the C2 root, verifies the
   C2 root's line counts (= today's minus the sealed prefix) and the sealed prefix hashes BEFORE truncating anything, and `data/` being
   gitignored, a dated backup listing (`tar` or a copy under `data/derived_backup_2026-09-03/`, with its `ls -la` in the transcript) exists
   before the first truncation. `unbought` and every C2 record keep their sha pins — nothing sealed is edited.
3. Closing check, shown: `sha256sum` of the 38 sealed sources == their sealed values (one command, 38/38); `w1` mirror 902/902 as before;
   `dashboard_data_w1.json` re-exported == the committed one **including `provenance.*`** (0 differing leaves, not 55); `w2` still 17
   channels / 1 113 positions from the new root; `make tick` twice zero rows; the 19 fork-1 reds go green with NO assertion changed.
Shape 1 is refused: it would leave the seals true only by definition.

**Fork 2 — `carrier` is part of the key; the test's claim is re-scoped, not deleted.** Two legs reading one message are two paid rows and
neither is dropped; `row_id` does not move (a sealed export's rows keep their ids). `tests/test_promo_tables.py::test_positions_is_untouched`
changes BY THIS RULING (Dv `[cause: ruling]`) to assert what the plan actually protects: no stored `row_id` moves, `w1`'s rows and values
are byte-identical before and after (the mirror + the export sha of fork 1), and the key is `(window_id, row_id, carrier)`. Reading owed in
the report, $0: for the 7 messages read by both legs, how many (brand, product, volume) triples appear in BOTH rows — if that number is
> 0, S3's trends dedupe per (window, channel, msg_id, brand, product, volume) preferring `carrier = leaflet_page`, named as a check in the
plan by revision; if 0, nothing changes and the number is the evidence.

**`--close --tolerance`: 0.05.** The 3.15 % gap is the always-on volume's drip inside the step's wall-clock, not pages; the step's spend
line is the guard's settled **$3.1909** (delta), the drip stays inside cycle 3 as it is. The START RITUAL closes the step at 0.05.

**The 16 pinned posts without an evidence row (14 `@epicentrk_sale`, 1 `@ekomarket_shop`, 1 `@forainfo`).** Re-asked ONLY on the S9
smoke's pod (≈$0.004 of compute, no separate boot), as its own step-ledger line; if the smoke never runs, the 16 stay in the report as a
named gap. Five channels with 0 positions are an answer — one line in the report and in `docs/STATUS.md`, no action.

**The render is READ (`render()` of `@VARUS_channel/6009`, the CODEBOOK block as committed) and ACCEPTED with ONE line added before the
pod:** rule 6 gains «строки чи умови акції В ЦІЛОМУ, без товару («акція діє 17.03?», «4 січня акції одного дня немає?») → МЕРЕЖА (chain)»
— the gold labels dec 09 and dec 15 that way and the block today routes «до коли» to the product only. Everything else matches codebook
v1 clause for clause. `codebook_version()` moves once more; the gold-as-fixture hooks (140/84/0) are re-run after the edit.

**K6's gold is PAGE-level — the row-level draw cannot be labelled blind.** The draw hands the labeller `(channel, msg_id, link)` and no
extraction, the grader matches on content, and a page carries up to 10 extracted rows (`@VARUS_channel:10843` — 10): a gold row written
blind for `…:0` names whichever item the labeller picks, and completeness would measure luck. Ruled: the gold `docs/labels-positions-50.jsonl`
carries EVERY in-scope position (the parser's own scope: dairy — milk, kefir/ryazhanka, yogurt, curd/syrky, sour cream, butter, cheese,
dairy desserts, plant-based analogs — and ice cream, `positions.py` categories) the team lead reads on each of the **46 pages/posts** the
50 drawn rows come from (draw sha `61b4fda7…` stays the anchor), one line per position, schema per SP-0 q1 above (`row_id · brand · product · volume · price_promo · badge_pct · price_old · note`;
`row_id` = `channel:msg_id:g<n>`, the labeller's own ordinal, never the extraction's). `positions_50_predicted.jsonl` is re-emitted as ALL extracted rows of those 46
messages (both carriers), `scripts/draw_positions_50.py --predicted-for-pages` or equivalent, sha in the record; the grader's rule is
unchanged (one-to-one content matching), `completeness` keeps its bar over the gold rows, `predicted_rows_no_gold_row_claims` is
reported as the precision reading (no bar). The 46 images live in `data/annotation/promo_c2/posts_media/` (gitignored); the executor
lists them by `msg_id` in `results/positions_draw_50.json` — add `image` (relative path) to each row in the next redraw-free write of the
record (a field, not a re-draw; sha of `rows` unchanged, said so in the record). The team lead labels in a fresh session; expect two.

**S9 iteration 1 — allowed after the smoke, on this table.** Pod up → smoke on 3 dev threads (the shortest, the median, the longest
render) → measured seconds/thread replace the borrow in `promo_dev40_prep.json` → projection for 40 threads at the measured mean and max:
| projected per iteration (mean) | do |
|---|---|
| ≤ $0.80 | run iteration 1 now; ≥ 3 iterations fit inside $2.50 with the holdout's $0.30 untouched |
| $0.80 – $1.20 | run iteration 1; STOP after it with the error table — the plateau rule needs two more and they may not fit |
| > $1.20 | STOP before buying: the table with mean and max, the pod torn down, listing shown |
Iteration = one pass over dev-40 with thinking OFF, batch 1, `extractor_version` on every row, K8 on the result, the error table
(top-10 subject misses with the gold row beside the model's, signal Jaccard per thread) in `results/` and the report. The 16 posts
(above) ride the same pod. Nothing else is bought.

**Pauses and `/goal`.** The Stop-hook evaluator does not honour the PAUSE branch and blocked eight turns before the cap ended the session
(Claude Code docs: the cap is eight; `/goal clear` — aliases `stop`, `off` — ends a goal). From now: when the STOP file is written and
the report committed, the executor's last message says «STOP — /goal clear», and the OPERATOR types `/goal clear`; the next resume is a
fresh session with the same §8 paste. §8 does not change.
