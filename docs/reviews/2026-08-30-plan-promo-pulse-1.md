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

## Ruling 03.09 (c) — the sixth STOP: plan §9 (rev 9) is ACCEPTED with five amendments — build the S9 instrument at $0, then buy the smoke and iteration 1; the step's line of record is the SETTLEMENT $2.9867; the dedupe keeps the LEG; §8 becomes v4 (the PAUSE clause loses its tail)

**Accepted, by diff and by files, $0:** `85138c2` (the split — 38/38 sealed sources hash to their sealed values after the truncation,
backup `data/derived_backup_2026-09-03` listed before the first cut, `w1` 902/902, the w1 export 55 → 5 differing leaves and all five are
moved-file pins claimed through `MOVED_BY_THE_SECOND_WINDOW`, `w2` 17 · 3 397 · 1 113 from `data/derived_w2/`, the 19 reds green with no
assertion of theirs touched), `fe84da8` + `bbc7483` (fork 2 closed; the reading owed: 7 row_ids under both carriers, 6 messages, exactly
1 cross-carrier triple `@forainfo:6056`, w1 0), `1f67c73` (step closed at tolerance 0.05), `a6e1994` (rule 6's whole-promo clause;
`codebook_version()` `a694d005972d3a66…`; the gold re-driven 140/84/0), `c01f2ff` (K6 page-level: 46 pages, 205 predicted rows both
carriers, `image` on 45/46 — `@silposilpo:3822` is its own text — and the draw unmoved: `rows_sha256_as_drawn` **`fe3f5841175a3953…`** is the
anchor the positions gold is owed against). **`make check` GREEN at `bbc7483`: 4 297 passed, exit 0** — (j) holds in both halves. The
defect the executor found in its own fixture (13 stub rows into the live root) was repaired from the backup byte for byte and the
fixture now refuses any derived root outside `tmp_path` with a negative control shown — accepted as reported. Nothing silently narrowed;
the one narrowing (the dedupe) was measured and asked, which is the rule.

**Money — the settlement is the line of record; my delta figure is withdrawn.** `docs/STATUS.md` carries `PROMO-PULSE-1 CLOSED —
settled $2.9867 of $3.95` (pods $0.0521 + serverless $2.9347; the network volume's $0.2236 stays in cycle 3 by the walk's own rule).
«$3.1909 (delta)» in ruling 03.09 (b) was a balance reading, not a settlement, and the executor was right not to type it into the record —
the guard settles what it settles, and a ruling that names a figure the guard cannot produce is the ruling's error. Cycle 3 today:
spent $3.5117 of $7.00, remaining $3.4883; the dev loop's cap is the full **$2.50**, floor $2.00, the holdout's $0.30 untouched.

**Fork 2's dedupe — the LEG, not the literal key.** The literal key (window, channel, msg_id, brand, product, volume) would drop 39 rows
over 35 groups, 34 of which are two promos of ONE SKU by ONE leg at different prices (`@atb_market_official:4359`, Активіа 260 г at
23.9 and 24.7) — two promos, not one counted twice — and 2 of them inside w1. The executor's CTE keeps the preferred leg (`leaflet_page`)
whole per message and drops exactly the cross-carrier collision (1 group · 1 row · 0 in w1; `@forainfo` Ласунка 2026-W35 `priced_positions`
4 → 3). That is the ruling now, by the measurement; the literal wording of 03.09 (b) is withdrawn. Plan rev 8's clause reads the same.

**Plan §9 (rev 9, `d33c5a3`) — ACCEPTED as the shape of S9's paid instrument, with five amendments folded in by revision (one commit,
before any code):**
1. **Registration prices smoke + iteration 1, not five.** Rung 0 at `--register` runs on the BORROWED corners (23.76 s mean, its max) for
   smoke (3) + iteration 1 (40) + the 16 posts + one boot + the idle inside one session; the dear corner must fit $2.50 or `--run` refuses.
   Iterations 2–5 are each re-projected at the MEASURED rate against what remains of the cap before they are bought (rung 2); the step
   is not priced at five iterations up front — the borrowed max ($1.659 × 5) would refuse a loop the smoke may prove cheap.
2. **One pod per iteration; teardown before every STOP and before the session ends** — the listing (`serverless list` → `[]`,
   `pod list -a` → `[]`) in the transcript each time. The team lead's read of an error table happens between sessions; no pod idles across it.
3. **What an iteration may change, and what it may not.** Iteration 1 is the BASELINE: `CODEBOOK` `a694d005…` and today's TEMPLATE,
   untouched — it measures the law as ruled. Iterations 2–5 may vary the TEMPLATE, the rendering (thread order, truncation), decoding
   (temperature 0, max tokens) and the answer repair — each variant a new `extractor_version`, its diff named in `results/promo_dev40_errors_iter<N>.json`
   and in the report. `CODEBOOK` itself changes only by the team lead, at the plateau STOP, as the plan already says.
4. **Every iteration keeps its evidence:** `results/promo_dev40_predicted_iter<N>.jsonl` (never overwritten), `grade_promo_dev40_iter<N>.json`,
   `promo_dev40_errors_iter<N>.json` — the error table carries per-stratum readings beside the two bars, the top-10 subject misses with the
   gold row beside the model's, and the Jaccard per thread.
5. **`--close --tolerance 0.05`**, the fraction named now, as on S4. The smoke's rate lands in `results/measurements.jsonl` under the
   instrument's own name and the projection names it instead of the borrow — as §9 says; the borrow is never reused after the smoke.
Everything else in §9 stands as written: the new step `promo-dev-loop` and its own ledger, cap `min($2.50, REMAINING − $0.30)`, floor
$2.00, the four rungs, the four flags borrowing `run_promo_c2.py` and `read_threads_reader_v5b.py`, the smoke's n = 3 by the
shortest/median/longest rule over `promo_dev40_prep.json :: chars`, the 5-run ceiling, the plateau rule (two without gain on either bar),
the decision table of 03.09 (b) quoted and not moved, the out-of-scope list. **Sequence:** the flags and their stub tests at $0 (`--register`
and the projection testable without a pod), `make check` green, `--register` shown with `fits` at the dear corner → **then, in the same
session if the registration fits, the pod: smoke → the table → iteration 1 → K8 → error table → teardown → STOP «iteration 1 read»** (or
the table's own STOP). Option (2) — registering iteration 1 on the borrowed bound with the smoke folded in — is refused: the rate is the
one number nothing in the repo has measured for this prompt.

**§8 becomes v4 — the PAUSE clause loses its tail.** The ADR `the-pause-branch-is-unsatisfiable-as-worded` is right and the evaluator's
own words prove it: «after the ruling lands in the rulings file, the operator re-enters this SAME predicate in a fresh session» reads as a
precondition that the pausing session can never satisfy. The predicate describes a STATE; the resume protocol is a sequence and lives
in `docs/PROCESS.md` §Cadence 3 (ENDING A PAUSE), where the operator reads it. `docs/PHASE-promo-pulse-1.md` §8 is edited by the team
lead today: the tail after «a test that would have to be weakened» is deleted, the sentence ends there; nothing else in the body moves.
The operator pastes v4 from now on; a STOP still ends with «STOP — /goal clear» and the operator's `/goal clear`.

**Team lead's debts.** `docs/labels-positions-50.jsonl` against `fe3f5841…` — 46 pages, every in-scope position, next team-lead session(s);
the holdout-40 after the pre-registration STOP notice. The dev loop does not wait for the positions gold.

## Ruling 03.09 (d) — the seventh STOP: the $0 half of S9 is ACCEPTED; the next session is the runbook and nothing else; the create line is the sibling's, verbatim; `--terminate-after` is derived from the cap, never typed

**Accepted, by diff and by files, $0:** `379edb1` (`--register` — `results/prereg_promo_dev_loop.json`: step `promo-dev-loop`, its own
ledger, cap `min($2.50, REMAINING − $0.30)` = $2.50 from the guard's own REMAINING $3.4591, floor $2.00, rung 0 FITS at the dear corner
**$1.3193 of $2.50** in the pod's own unit — seconds × the day's $/h on the dearer cloud, the boot/load/scp/delete overhead taken from the
sibling that SETTLED, the dead-man derived; nothing typed), `f47ea1a` (the pack — 56 units re-derived: leg A 40 dev threads, leg B the 16 C2
posts by ids, the smoke's three first by the shortest/median/longest rule: `@msuaaaa:6523` · `@VARUS_channel:9006` · `@VARUS_channel:6009`;
the runner swaps ONE function of `reader_v5_pod_runner`; stub tests), `491687a` (transport gates from v5b's frozen record; the dry contact's
refusal at `@ekomarket_shop:1457` — payload sha vs rendered sha — fixed and now a test; the runbook), `bf21167` (plan §9a: the five
amendments folded in; the transport is a POD because `local_llm.batch` renders from the pinned `prompts.py` — a fact, accepted).
`make check` at `ae99c7a`: **4 313 passed, 2 skipped, exit 0**; 12 new tests each with a negative control. Nothing bought, listings `[]`.

**The pause is legitimate and it is now a rule.** A paid run is a whole session: create → settlement, with nothing else in front of it. The
executor drew the boundary where the money is instead of starting a run it could not finish — the right call, and the reason is stated
plainly rather than dressed as a listed cause. `docs/PROCESS.md` §Money gains the line; §8 does not change (the STOP file may name «the
session boundary before a paid run» as its cause; the evaluator's list is not the law, the rulings file is).

**The create line — the sibling's, verbatim, name and stop changed.** `scripts/runbook_pass2_signals_r2.md:89–92` is the authority the
runbook's placeholder asked for:
```
runpodctl pod create --name mp-promo-dev-1 --gpu-id 'NVIDIA GeForce RTX 4090' --gpu-count 1 \
  --network-volume-id qw4nwleanc --data-center-ids EU-RO-1 --cloud-type SECURE \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --container-disk-in-gb 30 \
  --ports '22/tcp' --ssh --terminate-after '<the seconds the registration's cap buys at the day's price, printed by --pre-create-check>'
```
Three corrections to `scripts/runbook_promo_dev_1.md` §1, by the executor before the create, one commit: (1) `--image` with that image —
the sibling's flag spelling (`runpodctl pod create --help` is the authority; the runbook's `--image-name` is not r1's); (2) `--data-center-ids
EU-RO-1 --cloud-type SECURE --ssh` and disk 30 as the sibling — the network volume `qw4nwleanc` lives in EU-RO-1 and the registration
priced that cloud; (3) **`--terminate-after` is DERIVED, not typed:** the runbook's `90m` is below the dear corner ($1.3193 at $0.74/h is
≈107 min) and would cut a run inside its own registration; rung 3 is the platform stop at the CAP at the observed price (§9a), so the
value is the seconds `--pre-create-check`/`--register` prints for the cap — and the record carries it.

**Next session, in this order and nothing else:** `scripts/runbook_promo_dev_1.md` §0 → §6 — guard read, price read, create, rung 1, dead-man,
bundle, launch detached, the smoke, the decision table of 03.09 (b) (≤ $0.80 → run; $0.80–1.20 → run then STOP; > $1.20 → STOP before
buying, pod deleted, listing shown), the GO, 40 threads + 16 posts, fetch, delete, settle (`--close --tolerance 0.05`), K8, the error
table → STOP «iteration 1 read» with `results/promo_dev40_predicted_iter1.jsonl`, `grade_promo_dev40_iter1.json`,
`promo_dev40_errors_iter1.json`, the spend line, and both listings `[]`. No $0 work before the create; no second create in the session.

**Pattern of the seven pauses (the operator's question, answered in `docs/STATUS.md` §Уроки).** Seven STOPs, seven correct refusals, $0
lost; six root causes on the team-lead side: two collisions of growth with the seals the spec never queried (4, 5), three money rulings
that named a mechanism or a figure the instrument then refused (1, 3, 6), one plan line accepted without its instrument (6 — S9), one
session sized for a build AND a buy (7). The fix is in this ruling and in PROCESS: a ruling names the command whose output is the number,
never the number; a fork on a sealed file lists the seals it touches before the ruling (the STOP already does); a paid run is a session.

## Ruling 03.09 (e) — the eighth STOP: the dead-man is the PRODUCTION sibling's 500 s; rungs 1–2 are lifted for this step; the next session runs WITHOUT `/goal`; the process is re-based on the retro (`docs/reviews/2026-09-03-retro-process-v3.md`)

**Accepted, by files, $0.09:** `e4340e1`, `9c5af91`, `49860d1` — two pods created at the registered $0.74/h, both killed at 180 s by the
executor's own dead-man, $0.089622 of $2.50 spent, both listings `[]`, the unused recreate refused on the record (right: a gate set below
the span it measures gives the same answer every time). The create line of ruling (d) is vindicated; `--terminate-after` is a datetime
and was derived from the cap. The defect is named correctly by the executor: `gates.ssh_deadman_seconds` was read from a PROBE's record
(`prereg_reader_probe_v5b.json`, 180 s) while the production sibling on the same image/card/datacenter registers **500 s** with six
measurements (14.5 → 262.5 s; two pods unreachable past 230 s). Nothing else moved.

**Ruled.** (1) `gates.ssh_deadman_seconds` = **500** from `results/prereg_pass2_signals_r2.json :: kill_clock[rung 2].deadline_seconds`,
the record with measurements; the registration is re-emitted with that source named. (2) For THIS step and every step of ≤ $3.00 from
now on, rungs 1 and 2 are LIFTED: the money is bounded by `--terminate-after` derived from the cap (rung 3, the platform) and by the
step's registration (rung 0); one ledger line per session (`--note` at create, `--close` at delete); no per-stage re-projection, no ASK
ladder. The retro's reason: the guard has cost more sessions than the money it guards. (3) The dead-man stays as a LIVENESS check only:
no ssh by 500 s → delete, one recreate, then STOP — never a third. (4) `max_recreates` stays 2.

**The next session runs the runbook WITHOUT `/goal`.** The `/goal` evaluator cannot honour a pause (three sessions, 27 blocked turns,
the ADR `the-pause-branch-is-unsatisfiable-as-worded` and its sequel); the phase's stop-points are human decisions by design, so the
loop is the wrong instrument. From now the operator pastes the STANDING PROMPT below into a fresh session; the session does ONE item
and ends its turn at a stop-point after writing it to `docs/plans/promo-pulse-1.PROGRESS.md` (the executor creates it this session:
done / next / open stop, ≤ 60 lines; it replaces new STOP files and reports for the rest of the phase — the existing STOP file is
folded into it and deleted). §8 of the phase spec stays as the DONE list; it is no longer a `/goal` condition.

**Standing prompt (the operator pastes this, verbatim, every session of the phase from now on):**
```
Phase promo-pulse-1. Read, in this order and nothing else first: git log -15 --oneline; docs/plans/promo-pulse-1.PROGRESS.md (create it from docs/plans/promo-pulse-1.STOP.md if it does not exist, then delete the STOP file); the NEWEST dated section of docs/reviews/2026-08-30-plan-promo-pulse-1.md; docs/PHASE-promo-pulse-1.md §8 as the DONE list. Commit any modified team-lead file by path first. Then do exactly ONE item: the "next" line of PROGRESS. Verify it with its own check and show the output. Commit by path. Update PROGRESS (done / next / open stop, ≤60 lines). If you reach a stop-point — a paid or irreversible step not yet authorised, a design fork the plan does not settle, a test that would have to be weakened, a sealed file that would move — write it into PROGRESS as the open stop (≤15 lines: stop-point, question, tree state) and END YOUR TURN. Never add a test, pin, guard or ledger the phase file did not ask for; name the need in PROGRESS instead. Money: the step's cap is in results/prereg_promo_dev_loop.json; --terminate-after is derived from it; one ledger line per session.
```
Today's «next» line, which the executor writes into PROGRESS first: *run `scripts/runbook_promo_dev_1.md` end to end with the
dead-man at 500 s — create → smoke → the decision table of ruling 03.09 (b) → 40 threads + 16 posts → fetch → delete → settle → K8 →
error table; end the turn with the open stop «iteration 1 read» and the three iteration-1 files named.*

**Process re-base.** The retro `docs/reviews/2026-09-03-retro-process-v3.md` is the team lead's finding on the eight pauses and the
15:1 verification inversion; its §5 (principles), §6 (brain-init M6 v2 deltas) and the team-lead skill v3 draft on the operator's card
are proposed, not yet applied; nothing in the phase waits for them except what this ruling already applies: no `/goal`, one item per
session, PROGRESS instead of STOP+report, rungs lifted for small steps, rulings ≤ 12 lines from here.

## Ruling 03.09 (f) — iteration 1 READ: accepted; the misses are attribution, not meaning; codebook v1.1; iteration 2 = admin marker + chain canonical id + codebook examples in the template

**Accepted ($0.4358, pod `0z95ve2n570f0t`, 2 120 s at $0.74/h):** `b0c90cc` — 56/56 units answered, `results/grade_promo_dev40_iter1.json`:
signal 0.8792 (bar 0.75 HOLDS; currency 0.8583 · decimal 0.9000), subject 111/140 = 0.7929 (bar 0.80, one comment short).
`36ef74f` (fence stripped in `parse`, nothing else; malformed still fails by cause) — accepted, `[cause: the data]`; the raw replies are on
disk. The $0 pre-work (`--project`, `--score`, the eight audit fixes) accepted; the stub tests for `--score`/`--project` are AUTHORISED
now (product path, not process). Leg B: 16 empty arrays are correct. Reading of the 29 misses, by the team lead against the texts: 4 are the
channel's own account (12507, 9838, 16807, 1071 → the model says chain, the gold says post: it cannot see who wrote them); 5 are the
CHAIN's name written as a feature or a spelling (`додаток`, `програма лояльності`, `сертифікати`, `Варус` for VARUS; `msuaaaa` for Roshen);
3 are the availability rule (12510, 12511, 13529: «коли у всіх маках?», «в якому ашані?» → the gold says product, the model says chain);
3 were the gold's own ambiguous calls (8044, 20083, 407 — two carried `unsure`); the rest are hard ironies and jokes (8056, 8134, 2785,
7497) and post-vs-chain on the aggregator (12638, 12639, 12647). Meaning is read (sarcasm 8030/8038 right, both types); attribution is
where the model stumbles — exactly the layer the operator named on 27.08, now with a number and a table.

**Codebook v1.1 (team-lead file, committed by path):** (а) a reply to another commenter that names nothing and carries no signal → `post`
— gold rows 8044, 20083, 407 re-labelled under it (the three ambiguous ones; re-graded at $0 they turn iteration 1 into a READING of
114/140 = 0.814, which is not a claim on the bar — the bar is claimed on dev-40 by iteration 2 and on the holdout once); (б) the subject
of a `chain` row is the chain's NAME, never its feature; chain names are canonicalised to the registry's chain id in `promo_key` for chain
rows only (`VARUS`=`Варус`=`варус`; `sku`/`brand` unchanged) — applied to gold and predicted alike, before iteration 2, as a product
normalisation the dashboard needs anyway; (в) the render marks the channel's own account `[admin]`.

**Iteration 2 — two sessions, one item each.** Session A ($0): (1) `config/registry.yaml` gains `admin_anon_ids` per collected channel — the
executor resolves the full ids in the store from the prefixes the codebook names (VARUS `2fa2b7…`, msuaaaa `58805a…`) and pins them; the
render prefixes those comments with `[admin] `; (2) `promo_key` canonicalises chain rows via the registry's names/aliases; the grader and
`aggregates` use it; (3) the TEMPLATE (not CODEBOOK) gains a ≤12-line block of worked examples taken from `docs/CODEBOOK-promo-signals.md`
§3–§6 — never from a dev-40 or holdout thread — covering: feature → chain name; availability question → product with the store in the
note; admin → post; aggregator's own posting → post; bare reply → post; (4) `--score` re-run on iteration 1's replies under v1.1 as a $0
reading, printed beside the paid number, never replacing it; (5) the stub tests of (A)'s code; `make check` green. Session B (paid, ≤ the
step's $1.9746): the runbook with a new `extractor_version` → `promo_dev40_predicted_iter2.jsonl`, `grade_…_iter2.json`, `errors_…_iter2.json`.
Plateau rule unchanged (two without gain on either bar). Nothing else changes in the prompt for iteration 2.

**Money.** The step's line of record is pod-priced: `promo_dev_loop_run.json :: spent_all_segments_usd` = $0.5254 of $2.50 (both sessions);
the $0.089622 of session 8 enters the ledger as its own line from that record (`[cause: ruling]`, the anchor of the ledger post-dates it);
`--close --tolerance` is not applied to pod-priced steps — the walk is informational. Cycle 3: $4.0631 of $7.00, remaining $2.9369.
The «needs named» list stays in PROGRESS as debts; none blocks iteration 2.

## Ruling 04.09 (g) — `admin_anon_ids` live OUTSIDE the registry (option b); wordless comments leave the render; session B is bought under a registration re-emitted for v1.1

1. **(b).** The ids go into a new file `config/channel_admins.yaml` (`"@VARUS_channel": [<full sender_anon_id>], "@msuaaaa": [...]`,
   resolved from the store, committed), read ONLY by the render. `config/registry.yaml` does not move; no revision r3; no preflight change.
   The seals pin a file that must not grow — the same lesson as the derived store, applied before it costs a session.
2. The render DROPS wordless comments (`text.strip()==""`): they are outside the queue (SPEC 3.19), outside the gold, and a blank
   `[admin]` line would be content nobody labelled. `[admin] ` is prefixed only where the sender id matches; a null sender gets nothing.
3. Session B is bought under `results/prereg_promo_dev_loop.json` RE-EMITTED with v1.1's shas (gold `2303ea43…`, codebook `23610346…`)
   and a new `template_sha256` (TEMPLATE + the examples block) so a render-only change is visible in the record; `committed_registration()`
   not verifying `pinned_inputs` is a named debt, not built now. B is not bought before A(3) lands.
4. A(4)'s reading writes to `results/promo_dev40_errors_iter1_v1.1.json`; the paid `…_iter1.json` is never rewritten. The runbook's `--out`
   takes the iteration number (`promo_dev40_iter2.jsonl`). C2 collection stays open (not (c)). The rest of the «needs named» list stays as debts.

## Ruling 04.09 (h) — A(1) accepted; A(2)–A(5) and the (g)3 re-emission are ONE item in ONE session; B follows without a team-lead read

1. A(1) `c7a63a7` accepted by diff: `config/channel_admins.yaml` (two ids, resolved from the store, one reader), the render marks 23 and
   drops 68 = the draw's `n_wordless`, the pack's per-unit sha covers the unpinned file (refusal shown), `make check` 4 313 green.
2. «One item per session» is for items that carry a check of their own; A(2)–A(5) share one — so they are ONE item, «A-rest», in the
   next session: `promo_key` chain canonicalisation via the registry's names/aliases (grader + `aggregates`) → the template's ≤12-line
   examples block → the $0 v1.1 reading into `results/promo_dev40_errors_iter1_v1.1.json` → stub tests → the registration re-emitted
   under v1.1's shas with `template_sha256` and `"iteration": 2` in the pack → `make check` green. End the turn with NEXT = B.
3. The examples block is VERBATIM sentences and examples from `docs/CODEBOOK-promo-signals.md` v1.1 §3–§6, each cited by section, never a
   dev-40 or holdout thread; PROGRESS carries the block. Because the words are the codebook's own, B does not wait for a team-lead read of
   the render — the team lead reads it with iteration 2's numbers at «iteration 2 read».
4. B = the runbook with `--out results/promo_dev40_iter2.jsonl`, files `*_iter2.*`, ≤ $1.9746; the debts list stays as it is.

## Ruling 04.09 (i) — Маркетопт's own promo channel is collected NOW: the item goes right after «A-rest», before B

1. The operator authorised joining the private Маркетопт channel on 30.08 (rulings (ц)/(ш)); five days later it is still uncollected —
   the team lead's sequencing error, not a fork. It becomes the executor's NEXT item after «A-rest», ahead of the paid iteration 2.
2. The item «sources-r3: Маркетопт»: join `marketopt_private` (`+Ejz6ubzm21IyMTQy`, already a registry row — no registry change) → collect
   its posts into the live root ($0) → census reading (posts, price/media share, comments) → its leaflet pages through the same S4
   machinery under its own registration `results/prereg_promo_c3.json`, **cap $0.50** (cycle 3 remaining $2.94 − dev loop $1.97 − holdout
   $0.30 = $0.67 free) → its positions in a THIRD window through its own seal, exactly as w2 was built → `make tick` twice, the screen
   shows the Маркетопт rows beside w2's. The check the operator reads: `make promo-screen` renders Маркетопт positions from the new window.
3. `@ON_LINE_MO` (Маркетопт ON_LINE, 1 091 subscribers, census verdict «enter») is not a registry row: it joins through a side file
   (`config/registry_extra.yaml`, read beside the sealed registry — the `channel_admins` pattern), same item if the census shows prices,
   else named in PROGRESS. `@rozlyvne` (beer) and `@marketoptwork` (jobs) are out of scope.
4. Wholesalers: the operator names them or says «find» — discovery by HTTP of official handles is allowed; they enter through the same
   side file as a separate item. Nothing in the dev loop waits for this item; B follows it in the next session.

## Ruling 04.09 (j) — A(2) is a side file of chain spellings; the 11 verbatim dev quotes leave the law; every example is synthetic and checked against the store

1. **A(2) = (a), principled, not per-miss:** `config/chain_aliases.yaml` (the `channel_admins` pattern — the registry does not move) lists,
   per registry chain id, its nominative spellings in Latin and Cyrillic derived from the chain's NAME (`varus: [VARUS, Varus, Варус]`,
   `silpo: [Сільпо, Silpo]`, `atb: [АТБ, ATB]`, `mcdonalds: [McDonald’s, McDonald's, Макдональдс]`…) — never a synonym harvested from a
   miss. `promo_key` folds `chain` rows through it, gold and predicted alike. +1 row on dev today; the dashboard's one-id-per-chain tomorrow.
2. **The leak is real and is closed now, at $0.** The 11 dev-40 comments quoted verbatim in `promo_prompts.CODEBOOK` are replaced by
   paraphrases of the same shape; the old→new pairs go into PROGRESS; a check shows none of the new strings (and none of A(3)'s examples)
   is a substring of any dev-40 or holdout-40 comment text. `codebook_version` moves (law v1.2); `docs/CODEBOOK-promo-signals.md` follows
   at the next acceptance from those pairs. Iteration 1 stands as measured, marked in STATUS «instrument had seen 11 of 140 dev comments»;
   the dev bar is claimed only from iteration 2 on; the holdout claim was never touched.
3. **A(3), fifth category — the examples are the team lead's, synthetic:** «Ну да» · «Ок, зрозуміло» · «+1» · «І що?» → `post`. (h)3 is
   amended: examples are synthetic paraphrases in the codebook's shape, cited by section, never store text.
4. Order unchanged: A-rest (with 1–3) → «sources-r3: Маркетопт» (ruling (i)) → B.

## Ruling 04.09 (k) — «A-rest» ACCEPTED in full; the near-quote waits for the law freeze before the holdout; next: Маркетопт, then B at ≤ $1.9215

1. Accepted by diff and files (`c2234a4`, `d64faf7`, `3f75106`): `config/chain_aliases.yaml` from the chains' NAMES (+1 row, `8865`, none broken
   — 0.8214 as a $0 reading under v1.1); law v1.2 (`a587e0d6…`) with the 11 paraphrases; the synthetic examples block, two of the team lead's
   own examples rightly swapped («Ну да» was holdout text — the check caught its author); `--leak-check` CLEAN over 328 comments;
   `--score --suffix`; the registration re-emitted with v1.1 pins, `template_sha256`, `"iteration": 2`, rung 0 FITS $1.3193 of $2.4469;
   `make check` 4 319 green; the layering invariant kept (the layer is handed the spellings, it opens nothing).
2. The near-quote «Шикарно. Цілий день тиша, а потім скидка» is NOT changed before B: a law move now would re-derive the pack for a
   cosmetic gain. It is replaced (with the codebook doc synced to the same paraphrases, v1.2) at the law FREEZE that precedes the holdout
   pre-registration — one move, one registration.
3. The cap fell with the always-on volume to $2.4469; B is bought at ≤ $1.9215 as PROGRESS says. Order stands: Маркетопт (ruling (i)) → B.

## Ruling 04.09 (l) — Маркетопт's 33 posts are in; B goes first (it is ready and it is the critical path); the c3 leg gets parameters, not siblings; one screen over all windows, one existing chain id

1. Accepted: `449cab1` — the invite-form defect found by a live read and fixed in the resolve argument only; **33 posts, 2026-08-04 → 09-04,
   all with media, $0**. A unit test for `resolvable()` with a `+` handle is authorised (product path). The moved corpus anchor is harmless
   while no C2 producer re-runs: C2's truth is its sealed result files, not the store's max date.
2. **Q1 — parameters on the C2 producers, no siblings:** `--out`, `--channels`, `--anchor` (pinned in the registration), `--prereg`, `--step`,
   `--cap`; every C2 result file stays byte-identical (the ten pins hold, nothing under `prereg_promo_c2.json` is re-run) and c3 writes
   `results/*_c3.json` under `results/prereg_promo_c3.json` with its own anchor (the day after its last post) and its own ledger `promo-c3`.
3. **Q2 — the screen renders ALL windows** (`tick.py --window all`; it becomes the default unless a test pins `w2`, then the runbook's tick
   line carries `--window all`), and BOTH channels carry ONE chain id — the EXISTING `marketopt_promo` (w2's id; nothing sealed moves):
   the alias side file gains a `chain_of_channel: {marketopt_private: marketopt_promo}` map, read by the same one reader before the spellings.
4. **Order: B now** — everything for it is ready and the dev loop is the phase's critical path — **then «c3» in ONE session: the $0 build (2, 3,
   the census artifact) and its paid leg together**, because the leg is minutes of serverless pages, not an hour of pod: cap = min($0.50,
   REMAINING − $0.30 as `runpod_guard.py` prints it after B); if that room is under $0.15, STOP for the operator's word before buying.
   `@ON_LINE_MO` after c3 if its census shows prices; the ATB group id stays unaddressable, named.

## Ruling 04.09 (m) — iteration 2 stands as measured (signal HOLDS, subject RED by ONE fenced array); the repair is a new `extractor_version` = iteration 3, bought in the session that fixes it; no plateau; leg B closes at two `[]` readings

1. Accepted: `8d4108d`, `90996cc`, `20fdeb9` — B ran whole at the registered price ($0.2239, 1 089 s, teardown shown, 4 319 green), the
   runbook repointed off every paid `…_iter1.*`. **Iteration 2 is the record as measured:** signal 0.8854 HOLDS, subject 0.7500 RED
   (`grade_promo_dev40_iter2.json`); its `…_iter2.*` files are never rewritten ((c)4). The counterfactual 0.8786 enters no record.
2. **Q1 — a new `extractor_version`, iteration 3, by (c)3's own letter:** the stop rule and the answer repair ARE the instrument, and
   nothing is «re-bought» under an old number. Law v1.2, the template and the gold do not move. The repair: the dispatch reads the
   first `[`/`{` AFTER the fence that all 40 answers carry (`unfence` first, dispatch second), and a bare array is read as the rows it is.
   ONE test, both directions, is authorised as a caught product defect (§7): a fenced 3-object array stops at its `]` and parses to 3 rows;
   an unfenced object still stops at its own close. The diff is named in `promo_dev40_errors_iter3.json` as (c)3 asks.
3. **Q2 — no plateau.** The registered rule is «two without gain on EITHER bar»; iteration 2 gained on signal (0.8792 → 0.8854) and on the
   122 delivered comments (25 → 17 misses); subject fell by one transport failure, not by the law. The plateau counter stands at 0.
4. **Leg B closes at two identical readings:** 16 of 16 posts answered `[]` twice — the evidence is the empty array under iteration 2's
   files; iteration 3 buys leg A only, the re-emission says so. S4's leftover posts stay without a position row, named, not bought a third time.
5. **Iteration 3 = ONE session, as B was:** the fix and its test → the re-emission (`iteration: 3`, the runner's sha among the pins) →
   the purchase → K8 → the error table; money as in B (the three numbers pre-declared before the smoke, the cap being the step's
   remainder as the guard prints it; `project()`'s KILL against the whole cap stays named). Subject ≥ 0.80 → the holdout NOTICE is the
   open stop, END (the law freeze of (k)2 and the holdout gold are the team lead's, before the registration); RED → the error table, END.
   c3 follows either way, as (l)4.

## Ruling 04.09 (n) — s16 ACCEPTED by diff ($0): the repair is both halves as (m)2 wrote it; the re-emission pins BOTH files; iteration 3 is bought next

1. Accepted: `f872a53` — `balanced_prefix` unfences BEFORE the dispatch and returns a prefix of the emitted text; `promo_prompts.fold` reads a
   bare array as the rows it is, a non-object element still a parse failure; the law (`CODEBOOK`, template) untouched; `make preflight` 0 pinned
   paths touched; the one test is §6.5's $0 drill (object · array × fenced · unfenced, three negative controls); the paid record re-parses to
   the SAME 122 rows and the SAME one failure — iteration 2 stands. PROGRESS ≤60 lines, open stop «none».
2. The executor's reading is right: `extractor_version` = sha256(rendered prompt) cannot carry a transport repair, so the re-emission pins
   `scripts/promo_dev_pod_runner.py` AND `src/market_pulse/promo_prompts.py` beside it — that IS (m)5's «runner's sha among the pins», not
   a new pin. Nothing else moves; the named list stays named. Next session = iteration 3 whole, as (m)5 and PROGRESS «Next» say.

## Ruling 04.09 (o) — the count was never the claim: the test reads the population from the registration, both directions; the synthetic unit is refused; the borrow retires from rung 0 before iteration 4, with the mean corner as the fallback — no further stop on either

1. Accepted: s17's $0 half (`8efb0c8`, `48537b9`, `1962ee5`) — `ITERATION = 3`, both halves of the repair among the pins, leg B closed
   with its 16 ids named under `not_bought`, the 40 leg-A renders byte-identical to iteration 2's, dear $1.3100 FITS at cap $2.1638, the
   runbook off every `_iter2`, the three numbers pre-declared. The stop was right under §8 (j) as it was written.
2. **(a):** `len(items)` and the leg-B count are read from the committed registration (`population.leg_a.threads`, `population.leg_b.posts`),
   and the claim is stated in BOTH directions — every registered unit is in `items`, every item is registered; that is what «exactly»
   meant, and the literal 56 was iteration 2's population, a process pin (§7). The docstring loses «56». Leg B's render-pin claim is kept
   as a loop over the record's leg-B units — empty today by the record's truth, not by weakening. **(c) is refused:** a fixture that
   invents a unit the record does not carry tests the fixture. `test_leg_b_pins_ids_and_not_a_count` stays as is. Diff in the commit.
3. **PHASE §6.6 (v6), so this class never stops again:** when a ruling moves the registered record and a test's invariant still passes while
   only literals of that record diverge, the test is rewritten to read the record, both directions, in the same commit — the diff shown;
   weakening an invariant remains the stop of §8 (j).
4. **The borrow:** (c)5 retired it after the first smoke; two smoke rows in `measurements.jsonl` say «it replaces the borrowed…», the emitter
   kept reading it, and the team lead accepted two registrations without re-reading `rung_0` against that file — my miss. Iteration 3 runs
   as registered (its `--project` reads the measured rate; the 90-min stop is $1.1100). **Before iteration 4's re-emission the emitter prices
   rung 0 on the instrument's OWN measured maximum** (the larger smoke row, 178.298 s until iteration 3's smoke adds a third); if that dear
   corner does not fit the remainder, the registration is issued FITS on the measured MEAN corner with the cap as the hard stop and says so
   in one line — no stop, the whole step being inside ruling (e)'s «a step ≤ $3 the operator can lose without a word»; only a mean corner
   that does not fit comes to the operator.
5. Order unchanged: `make check` green → buy iteration 3 → K8 → the error table; subject ≥ 0.80 → the holdout notice, END; RED → the table, END.

## Ruling 04.09 (p) — s18 ACCEPTED by diff ($0): the pack test reads the record in both directions; nothing is open; the next session is the purchase of iteration 3 and nothing else

1. Accepted: `2f2b62c` — the population is read from the committed registration (`leg_a.order` + `leg_b.by_channel`, the count
   `threads + posts`), «exactly» stated both ways with no id twice, leg B's render-pin loop over the record's own units (empty while (m)4
   holds), the pack's registration sha checked against `PREREG` first; three negative controls refused at $0; `make check` 4 320 passed,
   exit 0, no file deleted. The synthetic unit stayed refused; `test_leg_b_pins_ids_and_not_a_count` untouched. Exactly (o)2.
2. Next session = the paid item alone, as PROGRESS «Next» writes it: runbook §0–§6, the three numbers already declared ($1.4146 · KILL by
   hand · 90 min = $1.1100), `--score --iteration 3`, K8, the error table naming the diff against iteration 2; subject ≥ 0.80 → the holdout
   NOTICE, END; RED → the table, END. `items[:3] == pack["smoke_ids"]` stays as it is — named, not moved.

## Ruling 05.09 (q) — iteration 3 ACCEPTED on a COMPLETE reading, both bars HOLD, the dev loop is DONE at 3 of 5; the law is FROZEN as bought; the holdout is ONE shot at cap $0.90 and goes before c3; the volume is deleted after the phase's last paid run

1. Accepted: `b93c997` (+ `ca0dfdb`, `0aa3dd8`, `0b4211c`). Complete by §6.5: 40/40 units, `parse_failures` 0, 140 gold-shaped rows. K8 re-run by the
   team lead AND a fresh verifier (`python3 scripts/grade_promo_signals.py --gold docs/labels-promo-dev.jsonl --predicted results/promo_dev40_predicted_iter3.jsonl
   --draw results/promo_threads_draw.json`), bars byte-identical to `grade_promo_dev40_iter3.json`: **subject 0.8714 ≥ 0.80 HOLDS · signal 0.9104 ≥ 0.75 HOLDS**;
   currency 48/61 = 0.7869, decimal_only 74/79 = 0.9367 (readings). The diff is the transport repair and nothing else: 122 rows unchanged, +18 (all
   `@VARUS_channel:6216`), 0 moved; all 7 pins re-derived; the registration `48537b9` precedes the purchase. The hand-read KILL is accepted — the mean corner fit and
   the 90-min hard stop bounded the spend at $1.11, (o)4's own branch. Spend $0.493744 = 2402 billed s at $0.74/h: this pod ran 1.5–2.3× slower than iteration 2's
   on IDENTICAL outputs (6009: 88.2 → 202.0 s) — host variance, not the repair. The dev loop is DONE (3 of 5, plateau moot). `make check` after `b93c997` was not
   shown — the next session shows it first. Of the 18 misses 13 are currency; 13 of 18 carry the gold's signal types — the residue is attribution (post ↔ chain ↔ sku), 3 irony.
2. **The law is FROZEN as iteration 3 bought it** — `codebook_version a587e0d6…`, `template_sha256 57dd9d25…`, `scripts/promo_dev_pod_runner.py 102fa524…`,
   `src/market_pulse/promo_prompts.py dd260cb5…` — the holdout's registration pins these four UNCHANGED, so the holdout measures the instrument that took the dev
   bar, byte for byte. (k)2 is amended: the near-quote «Шикарно…» and the codebook-doc sync move AFTER the holdout (packaging), disclosed in STATUS — the one
   near-quoted dev comment, `@msuaaaa:3454:1217`, is among iteration 3's misses.
3. **Operator's word 05.09 (money):** the holdout's cap is **$0.90** — the $0.30 fence was §6.1's estimate on the borrowed 23.76 s/thread that (c)5 retired;
   `--terminate-after` derives from $0.90; rung 0 is priced by (o)4 on the instrument's OWN measured pace, the slowest pod: iteration 3's segment, 2402 billed s
   for 140 text rows — the holdout carries 188 text rows in 296 comments, longest thread 39 (`draw.<stratum>.holdout`), so $0.37–0.58 expected; a dear corner over
   the cap is issued FITS on the mean corner with the cap as the hard stop, in one line. §6.5 governs an incomplete run: recorded, re-bought under the next number,
   the law not moving — the ONE shot is one VALID reading.
4. **Order:** holdout → «c3» as (l)2–4 at cap $0.50 → the volume `mp-srv2` DELETED after c3 (operator's word 05.09; the empty volume listing shown in the transcript);
   C6's first pod loads the model cold, ≈ +10–15 min a boot, named in the C6 design.
5. **Next executor session = «holdout-prep», ONE item at $0, one check:** `scripts/promo_dev_pass.py` takes the holdout as parameters (PHASE §4: `--part holdout`
   → population `draw.<stratum>.holdout`, 40 threads, leg A only; `--gold docs/labels-promo-holdout.jsonl` among the pins — the emitter REFUSES to write the record
   while that file does not exist and says so; `--step promo-holdout --cap 0.90` with its own ledger; rung 0 as item 3); `grade_promo_signals.py` takes `--part`;
   the runbook is off every `_iter3` path onto `_holdout` (smoke = the holdout's first three units); `promo-dev-loop` closed with `--close` (the last iteration,
   one-way). Check shown: `--dry-run --part holdout` prints 40 threads, the pricing and «gold missing → no record»; `grep -n _iter3 scripts/runbook_promo_dev_1.md`
   → nothing; `make check` green. The paid session after the gold is committed: `--register` (gold pin) → smoke → buy → K8 → the error table — END at the reading
   either way (a failed bar closes S2's question); then c3.
6. Team lead today: holdout-40 gold `docs/labels-promo-holdout.jsonl` under the codebook doc as pinned (`2361…`), written blind — no holdout prediction exists;
   then positions-50 (46 pages). STATUS carries the dates.
7. **(q) addendum, 05.09 08:40 — the holdout gold LANDED:** `docs/labels-promo-holdout.jsonl`, 188 rows = every text comment of the 40 holdout threads
   (296 − 108 wordless; validator 0 errors; 4 `unsure`), written blind under the codebook doc as pinned (`2361…`), audited by a fresh reader against the
   codebook's letter (15 rows corrected: own-channel post = chain §3, noise source §4, signals per row subject §3/§5). sha256 `6fa804880d5d14db…`. Two of the
   40 threads are `@matusi_ukr` (off-domain, 25 rows) — the frozen population's own truth, labelled as `post`/named institution as `chain`. The executor
   commits the file by path at its start ritual; the registration pins it. `.git/index.lock` (empty, 05:12 UTC, left by the team lead's `git status` on the
   mount) must be removed by the operator before the next executor session.

## Ruling 05.09 (r) — s20 «holdout-prep» ACCEPTED ($0); s21's stop was RIGHT: the holdout's money gate is rung 0 FITS + the cap as the hard stop, the record's decision table branches on the part, `project()` is not run on this shot; the dev ledger stays open by construction; cap $1.10 (operator's word); the shot is bought next

1. Accepted: `f879bf9` `7a7d90c` `858ead0` `31f9461` — `--part {dev,holdout} --gold --step --cap`, `use_part()` binds both halves (the `use_part("dev")` no-op
   caught and fixed at $0), `own_rate()` reads the instrument's own smoke rows (mean 88.772 s · max 201.967 s), `--register` REFUSES without the gold, the dev
   prep record byte-identical (`0a553add…`), no test/guard/pin/ledger added, `make check` 4320 at `858ead0`; the gold pinned (`6fa80488…`, 188 lines) in
   `results/promo_holdout40_prep.json`; the runbook carries no `_iter3`. Verified by a fresh reader. Named, not moved: the prep record's `phase`/`draw.dev_threads`/
   `bound…BORROWED` prose still reads dev — display strings of the $0 record; the registration is the record.
2. **s21's stop (a) was right and was PREVENTABLE by (q)5** — my miss: I parameterised the population and left the record's decision-bearing fields (`decision_table`,
   `authority`) on the dev leg, so `--register --part holdout` would have sealed a false record. **Ruled (ii):** the holdout's money gate is rung 0 FITS on the
   measured MEAN corner ($0.8420 ≤ cap) plus the cap as the platform's hard stop (`--terminate-after`); §5's band gate is NOT run on this shot — GO is written the
   moment the smoke's three replies are in (their seconds stay in the pod log); `project()` and its literals stay untouched. `register()` branches `decision_table`
   on the part; the holdout's table names THIS ruling as its authority and says exactly that; a run the hard stop cuts is an incomplete reading under §6.5.
3. **Operator's word 05.09: cap $1.10** (the instrument's own mean corner is $0.8420 — the team lead's $0.37–0.58 of (q)3 was a per-thread realised estimate and is
   superseded by the registered pricing; realistic $0.64–0.72 on a slow host); `--terminate-after` derives from $1.10 (≈ 89 min); c3 after it at min($0.50, REMAINING).
4. **Stop (b): `promo-dev-loop` stays OPEN by construction, no guard moves.** The close gate's right-hand side is a balance delta taken BEFORE the last pod, which a
   multi-pod, multi-day step (1.7 days of volume drip ≈ $0.4) can never meet within 5 %. The step's number of record is the run record's five segments,
   $1.153372 (`results/promo_dev_loop_run.json`), cross-checked by the guard's own settlement $1.159076 (0.49 % off, printed at the refusal). The RHS of `--close`
   for multi-pod steps (the run record, never the last note) is a harness debt for the retro — not this phase's code.
5. **Next executor session = the shot, ONE item:** `register()`'s part branch (item 2) → `--register --part holdout --step promo-holdout --cap 1.10 --gold
   docs/labels-promo-holdout.jsonl` → commit → §1–§4 → smoke → GO → §6–§7: K8 (`--part holdout`) → the error table naming the holdout misses. A complete reading
   closes S2's question green or red; an incomplete one is recorded and re-bought under the next number only after the operator's money word. END at the reading.
   Then «c3» (l)2–4, then the volume deleted (the listing shown).

## Ruling 05.09 (s) — the holdout shot is READ: signal 0.7958 HOLDS, subject 0.7181 RED on a COMPLETE reading; the registered question is closed with that number; operator's word: rework the codebook NOW and draw a new holdout; c3 deferred behind it; money needs a top-up

1. Accepted: `50959b5` `582a655` `26d4373` `ea1c615` `5174f2b` `6c6b37f` (+ `0726665` the part branch — SEVEN decision fields branched, named). Complete by §6.5: 40/40,
   `parse_failures` 0, 188 rows; K8 re-run by the team lead and a fresh verifier, byte-identical: **signal 0.7958 ≥ 0.75 HOLDS · subject 0.7181 < 0.80 RED**
   (`results/grade_promo_holdout40.json`; currency 95/140, decimal 40/48). Registration `50959b5` (07:47Z) precedes the pod (07:52Z); the four law pins are the
   dev-bar instrument's; the gold pinned; cap $1.10, FITS on the mean, hard stop 5351 s; spend **$0.296617** (1443 s, a fast host: 25.8 s/thread). The ledger
   `promo-holdout` twice refused to close on a PARTIAL billing walk (lag) — retried once at the next session's start, $0; if still partial, carried open like (r)4,
   number of record $0.296617 (`promo_holdout_run.json`). **The registered question is closed by this number: instrument v1.2 carries meaning across threads
   (signal) and does NOT carry attribution at 0.80. The reading stands as measured; nothing is re-scored.**
2. The 53 misses, read whole (`promo_holdout40_errors.json` + the team lead's full diff): **21** in ONE off-domain thread `@matusi_ukr:22155` (a moms' channel the
   r2 registry PAUSES — the frozen v1 population never excluded it; the codebook has no type for a kindergarten: gold `post`/`chain`, model `sku`); **11** partner
   services (`izibank`/`OTP` ×8, `Укрпошта` ×3: gold `chain`, model `brand` — the codebook never defined a promo partner); **7** same type, another surface form
   («морожено»/«морозиво» ×3, «ескімо Varto»/«мороженое», «Pilsner»/«… від ТМ MOVA», «Рошен»/«msuaaaa», «Сильпо»/«VARUS»); **14** in-domain attribution
   (argument replies `post`→`chain` ×4, promo praise sku↔chain, brand↔sku). Post-hoc READING, not a bar: without the two `@matusi_ukr` threads 131/163 = 0.8037.
   Signal misses cluster on the pair «коли буде знижка на X → спрос+цена» (the model gives спрос alone) and 1-comment threads (Jaccard 0.5).
3. **Operator's word 05.09: rework the codebook NOW, then a NEW holdout.** The line: (a) team lead — codebook **v1.2** (promo partners → `chain` named as in the
   post; terms of a joint promo → the channel's chain; an off-domain thread (no retailer, no product) → every row `post`; a product not in the post → Ukrainian
   nominative of the type; a product in the post → the post's bullet trimmed of «ТМ/від/торгова марка», volume and percent; the спрос+цена pair and argument-reply
   examples as synthetic template examples; the near-quote «Шикарно…» replaced; the doc synced) and the re-read of BOTH gold files by the convention diff — the
   used holdout-40 becomes **dev-2** (a reading, never a bar again); (b) executor, $0: law re-rendered from v1.2, `--leak-check`, **holdout-2 draw** — seed 42
   over the frozen 678 MINUS channels with `collect: false` in registry r2 MINUS the 80 drawn, 20/20, a NEW draw file (`promo_threads_draw_2.json`; the old stays
   frozen), the registration of **iteration 4** (dev-40 bar + dev-2 as a reading in ONE pod, cap $0.60); (c) executor, paid: iteration 4; (d) team lead:
   holdout-2 gold, blind; (e) executor: the ONE holdout-2 shot, cap $0.90 on the measured pace. **K8 v2 (proposed, enters iteration 4's registration unless the
   operator objects before it):** `sku`/`brand` subjects match on normalised exact OR token-Jaccard ≥ 0.5 — the product's identity, not its spelling; `chain`
   folds as today; `post` exact. The holdout-40 number above stays under K8 v1.
4. **Money (operator's decision, table given):** cycle 3 REMAINING $1.50 (guard 09:05); iteration 4 ≤ $0.60 + holdout-2 ≤ $0.90 + the volume's drip ≈ $0.24/day
   exceed it → a top-up is needed before iteration 4 (≈ $3 covers the line, c3 and two days of drip); **c3 is deferred behind holdout-2**; the volume `mp-srv2`
   STAYS until the holdout-2 shot (pods are coming) and is deleted after it. STATUS moves the gate to 10–11.09.
5. Next executor session = (b) above, ONE item at $0, after the codebook doc lands (the team lead says when): check shown — `--leak-check` CLEAN over dev-40 +
   dev-2 + holdout-2 texts, the draw's three sets disjoint and sized 40/40/40, the registration `--dry-run --part dev` FITS with `iteration: 4` and the law pins
   moved (codebook_version, template) and the transport pins unchanged; `make check` green. Standing prompt unchanged.
6. **(s) addendum, 05.09 12:20 — codebook v1.2 LANDED** (`docs/CODEBOOK-promo-signals.md`, sha `7b70caf75feeb3b3…`, §9 carries the convention diff: partners →
   `chain`; off-domain thread → `post`; product form (post's words without ТМ/об'єм/%; Ukrainian nominative of the type off-post; brand-as-product → `brand`);
   the спрос+цена pair and the argument-reply examples; the near-quote replaced by a synthetic sarcasm line). Gold re-read: dev-40 — 0 rows;
   holdout-40 → **`docs/labels-promo-dev2.jsonl`** (188 rows, 14 re-read, validator 0 errors, sha `20f496d8ca62a8ae…`); `labels-promo-holdout.jsonl` untouched
   (pinned by the shot's record). The executor's «v1.2-prep» ($0, one item, (s)5) also: the law's rule 4 and the sarcasm examples re-rendered from §3/§7,
   three synthetic template examples (partner · off-domain · «а X де?» → спрос+цена), `config/chain_aliases.yaml :: silpo` gains the chain's own Russian
   spelling «Сильпо» (a NAME form under (j)1, not a harvested synonym); the iteration-4 pack orders dev-40 FIRST and dev-2 after it, the registration saying
   that the bar needs dev-40 complete and dev-2 is a reading the hard stop may cut; cap $0.60; K8 v2's token-Jaccard is over whitespace tokens after
   `promo_key`, one two-direction test as a caught grader defect (§4). Then the paid iteration 4.
7. **(s) addendum, 05.09 12:40 — operator's product reading:** «Ковбаса за 19 це опасно» is a judgement on price as a quality indicator — `цена` only, not a
   complaint. Codebook v1.2 §5 gains rule (д) (sha now `86ed01a484611fd5…`); dev-2 row `@msuaaaa:9577:11108` → [цена] (sha `4b60ab99a21045e6…`); every other
   цена+жалоба row in dev-40/dev-2 is a claim against a price (too high, wrong, unfair) and stays. The frozen holdout-40 gold and its number do not move.
   The law re-render in «v1.2-prep» carries (д) as one line of the signal rules.
8. **(s) addendum, 05.09 12:55 — money: the operator's word «на счету есть деньги» → the cycle-3 CEILING rises to $9.00**, the anchor unchanged. The
   account holds $8.98 (console, 05.09 11:37) = the $14.48 anchor − $5.50 spent: the money was there, the $7.00 ceiling was the fence. Executor, in the START
   RITUAL of «v1.2-prep», ONE edit under this word (as the 01.09 raise from $4.80 to $7.00): `scripts/runpod_guard.py :: CYCLE3_CAP_USD = 9.00` (docstring names
   this ruling), `results/spend_cycle3.json :: cycle3_cap_usd = 9.0`, `note` APPENDED «CEILING RAISED 2026-09-05 to $9.00 on the operator's word (ruling 05.09 (s)
   addendum 8); anchor and anchored_at unchanged»; run the guard and SHOW `CYCLE 3 SPENT ≈ $5.50 of $9.00, REMAINING ≈ $3.50`; commit by path. No test moves
   (the tripwire fixtures carry their own cap). The line then fits: iteration 4 ≤ $0.60, holdout-2 ≤ $0.90, c3 ≤ $0.50, the drip — inside $3.50. No top-up.

## Ruling 05.09 (t) — s23 «v1.2-prep» ACCEPTED ($0); the stop was RIGHT and PREVENTABLE by (s): the cap was typed, not priced; the borrow died on one leg only. Every leg now issues on the MEAN corner of the slowest WHOLE run with the cap as the hard stop; cap $1.20 (operator's word); dev-40 first, dev-2 after

1. Accepted: `a6868e5` (ceiling $9.00, guard shown), `4a03307` (holdout-2: the product's population 398 = 678 − 12 paused − 80 drawn, 20/20, three sets 40/40/40
   disjoint, draw 1 replays byte-identical), `0224167` (K8 v2: one `subjects_agree()` shared by grade and error table; measured on the frozen holdout gold it buys
   1 row of 188, the alias 0 — the relaxation is small and now known), `4be406e` (law from codebook v1.2 incl. (д); `--leak-check` CLEAN over 440 comments;
   pins moved: codebook `0bbb665a…`, template `32fa6c42…`; transport pins unchanged). The red `test_the_pack_pins…` is the OLD pack against the NEW law — it greens
   at `--pack` inside this item, §6.6's class, not a stop; the two `== 40` literals read the record in the same commit (§6.6).
2. **The stop was right, and mine:** (s)5 typed «cap $0.60» without the dry run that prices it (§9: the command, not the number), and (o)4's borrow retirement was
   accepted with `rate_for("dev")` still reading `pass2_r2` — the verifier's line said so and I let the dev leg go «done». Two rules enter (§10, PHASE v10, skill).
3. **The corner, every leg (answer 1):** `rung_0` issues on the DEAR corner when it fits, else on the MEAN corner with the cap as the platform's hard stop — for
   `dev` as for `holdout`; the `part != "dev"` condition goes. The decision table follows the corner: dear → the bands; mean → (r)2's table (GO on the smoke's
   three replies, no band gate, `--project` not run). That is the answer to (3) as well.
4. **The rate (answer 2):** the borrow is retired on EVERY leg — `rate_for(part)` = `own_rate()`. A smoke of three, built to hold the longest thread, is a MAXIMUM,
   not a mean: `own_rate()` prices the mean corner on the WHOLE-RUN mean of the SLOWEST pod seen (n = 40: iteration 3 **47.7 s/thread**, max 286.2; the fast hosts
   17.7 and 25.8) and keeps the dear corner from the largest max. Whole-run rows are written from the run record by `--close-segment`, one per pod under
   `<part>_seconds_per_thread` (n, mean, max, source = the pod log) — iteration 2, iteration 3 and the holdout get theirs now at $0 (`4a03307`'s producer, same
   file, no new ledger); smoke rows stay as history and price nothing. Numbers to expect at `--dry-run`: 83 units × 47.7 s + overhead ≈ $0.87 mean corner.
5. **Operator's word 05.09 13:05: cap $1.20**, pack dev-40 FIRST, dev-2 after (the bar needs dev-40 complete; dev-2 is a reading the stop may cut); hard stop
   ≈ 97 min. Money after it: holdout-2 ≤ $0.90, c3 ≤ $0.50, the drip — inside REMAINING $3.49; an iteration 5 would need the operator's word on the ceiling.
6. Next session = the unblocked item: `rate_for`/`rung_0`/`--close-segment` as 3–4 → whole-run rows → `ITERATION = 4`, `--dry-run --part dev --cap 1.20` FITS on
   the mean → `--register` → commit → `--pack` (green) → the paid iteration 4 in the SAME session if the smoke is alive, else the next: smoke → GO → K8 v2 on dev-40
   (bars 0.80 / 0.75) and dev-2 (reading) → error tables → END at the reading. Standing prompt unchanged.

## Ruling 05.09 (u) — s24 ACCEPTED ($0): iteration 4 is registered on the MEAN corner ($0.8705 of $1.20) with the borrow dead on every leg; before the pod the registration gains dev-2's gold pin and `--score` takes the ARM as parameters; then the purchase

1. Accepted: `1ebc321` (`own_rate()` on `sample == "whole run"` rows — mean from the slowest pod, dear from the largest max; `part != "dev"` gone from
   `rung_0`; table, smoke prefix and gate 3 follow the corner; the three whole-run rows backfilled at $0 — iteration 2 17.71/88.24, iteration 3 47.66/286.25,
   holdout 25.83/149.05, n=40 each — the team lead's own log arithmetic (17.7 · 47.7 · 25.8) agrees), `426a7d7` (the dev leg = two arms of the first draw,
   dev-40 at order[0:40], dev-2 at [40:80]; `ITERATION = 4`; every dev-branch prose field says iteration 4), `1ee15f4` (rung 0 at the day's offer: cheap
   $0.8705 FITS · priced $0.9279 · dear $4.9984 NO → issued on the MEAN, hard stop 5838 s, the 90-min backstop bites first at 5400 s; 83 units; law pins moved
   to v1.2 — codebook doc `86ed01a4…` with (д), `codebook_version 0bbb665a…`, template `32fa6c42…`, `promo_prompts.py da60348d…`; runner `102fa524…` unchanged;
   dev-40 gold `2303ea43…`), `a6a5b1c` (the pack; the named red green by name; `make check` 4321 passed, 0 failed). All 7 pins re-derived by the team lead.
2. **The executor named it, and the answer is the word it asked for:** a reading needs its reference pinned as much as a bar does (§9). Before the pod, at $0:
   the registration is re-emitted with `docs/labels-promo-dev2.jsonl` (`4b60ab99a21045e6…`, HEAD) among `pinned_inputs` and `gold.covers` naming both arms;
   `--score` takes the arm as parameters (`--arm dev40 --gold docs/labels-promo-dev.jsonl` · `--arm dev2 --gold docs/labels-promo-dev2.jsonl`, strata from the
   arm's own part of the draw) and writes per-arm files — `grade_promo_dev40_iter4.json` / `promo_dev40_errors_iter4.json` (the BAR) and
   `grade_promo_dev2_iter4.json` / `promo_dev2_errors_iter4.json` (the READING); `--pack` again on the re-emitted record; commit — then the pod. A small fix
   and the paid run it unblocks share the session (§5).
3. The smoke rule promoting two dev-2 renders to the front is accepted as named: dev-40 completes at unit 45 of 83, deep inside the backstop. The out-file
   handed to `--close-segment` being unchecked against the pod stays named; the run's out-file is `results/promo_dev40_iter4.jsonl` and nothing else.
4. Sequence unchanged from (t)6: create → `--open` → smoke (3) → GO on the three replies, no band gate → the 80 → delete → `--close-segment --replies …iter4.jsonl`
   (the whole-run row for this pod) → listings `[]` → `--score --arm dev40` (bars 0.80 / 0.75) and `--score --arm dev2` (reading) → END at the readings.
5. **(u) addendum, 05.09 14:20 — s25 ACCEPTED ($0):** `705e2d1` `0bb62fb` — `--score` takes the arm (`dev40` · `dev2`, each its own units, gold and strata;
   refuses without `--arm` on a two-arm leg and refuses an arm under the wrong part), `pinned_inputs` gains `docs/labels-promo-dev2.jsonl 4b60ab99…` (all 8
   pins re-derived by the team lead), the pack re-pins the registration (`9ded3a79…`, units byte-identical), rung 0 unmoved ($0.8705 mean, cap $1.20), `make
   check` 4321/0. The $0 arm drive on OLD replies reproduces iteration 3 exactly (0.8714 / 0.9104) and reads holdout-40's old replies against the re-read
   key at 0.7394 / 0.7833 — plumbing, not a v1.2 reading. Next session = the purchase, (u)4 unchanged; the arm-selector test stays named, not asked for.

## Ruling 05.09 (v) — s26's stop was RIGHT and PREVENTABLE by the team lead: a paid run is bought under ITS OWN step line — `promo-iter4`, own anchor, own ledger, cap $1.20; the old `promo-dev-loop` line stays as (r)4 left it; the registration reads the guard WITH the step it names

1. The stop (`6408e94`, $0, no pod): `--step promo-dev-loop --step-cap 1.20` refuses at $1.8462 spent (pods $1.4573 + the volume's $0.3792 since the 03.09
   anchor); at the ledger's own $2.50 it leaves $0.6538, under the registered mean $0.8705. The registration read FITS because `guard_reading()`
   (`promo_dev_pass.py:515`) calls the guard WITHOUT `--step`, so `cap_rule min($1.20, REMAINING)` saw the CYCLE's $3.48 and never the step's own line.
   The team lead accepted (u)1 and (u) addendum 5 «guard read before the write» without asking WHICH guard — the miss is mine, twice.
2. **(a): a paid run is its own money line.** Iteration 4 is bought under **`promo-iter4`** — `results/spend_promo_iter4.json`, anchored at this session's
   own `--note` before the pod, cap **$1.20** (the operator's word, unmoved), the hard stop derived from it as registered (5838 s; the 90-min backstop bites
   first), closed in the SAME session after the pod with `--close --expect-ms <the segment's billed ms> --tolerance 0.05` — one pod, one hour: the gate
   S4 closed under. The `promo-holdout` precedent is the rule from here: **`promo-iter<N>` · `promo-holdout2` · `promo-c3` — one line per paid run**, opened
   by its `--note`, closed by its run record; the cycle-3 ceiling ($9.00) governs the sum. `promo-dev-loop` stays as (r)4 left it — open by construction,
   number of record $1.153372 — and carries no new run.
3. **The registration names its line and reads its guard ($0, before the pod, then `--pack`):** `step.name = promo-iter4`, `step.ledger` its file,
   `cap_rule = min($1.20, THIS step's REMAINING)`; `guard_reading()` runs the guard WITH `--step <name> --step-cap <cap>` and the record's `money` carries
   the step's own line (a new line: spent $0.00, REMAINING $1.20) beside the cycle's; rung 0 unmoved ($0.8705 FITS on the mean). A registration that names
   a step but prices against the cycle is a false record — the same class as (r)2's decision table. No new test (§7): the refusal was seen at both numbers.
4. Then the purchase in the same session, (u)4 unchanged: create → `--open` → smoke → GO on the three replies → the 80 → delete → `--close-segment --replies
   results/promo_dev40_iter4.jsonl` → `--close` the step → listings `[]` → `--score --arm dev40` (BAR 0.80 / 0.75) · `--score --arm dev2` (READING) → END.

## Ruling 05.09 (w) — iteration 4 is an INCOMPLETE reading (CUDA OOM on the longest render at the smoke): the instrument does not move, the SERVING does — a card ≥ 32 GB, `expandable_segments`, the runner reports a failed unit at once; re-bought as iteration 5 on its own line `promo-iter5`, cap $1.40 (operator's word); `promo-iter4` closes on its run record

1. Accepted: `3930fa0` `d964fbd` `3e2c538` `badbc8d` — the registration on its own line (guard read WITH `--step`; the negative control refused), the pack re-pinned,
   the pod `kzcnhe01mgdwvk` (rung 1 GO), the smoke's third unit `@VARUS_channel:8647` (14 281 chars, the longest render — the smoke rule chose it on purpose and it
   paid for itself) died in `gemma4._norm` with 338 MiB refused at 23.19 of 23.52 GiB; no GO, none of the 80 bought; $0.691489 (3364 s). **§6.5: an incomplete
   reading — recorded under iteration 4, compared to nothing.** `promo-iter4` CLOSES now on its run record (`--close --expect-ms 3364000 --tolerance 0.05`): one line,
   one run, the run happened.
2. **The instrument is untouched.** Law v1.2, template, render, the 4000-token ceiling, NF4/bf16, greedy decoding, runner and parser stay byte-for-byte — none of
   them is the remedy. What moves is the SERVING ENVIRONMENT, which the registration prices but does not pin as the instrument: (a) a card with **≥ 32 GB** VRAM
   in EU-RO-1 (the volume's datacenter) — RTX PRO 4500 32 GB first (ruling 22.08 (о) precedent, ~$0.72/h), else A6000 / L40S 48 GB — at the day's dearer offer
   **≤ $0.90/h**; the 4090 is not bought again for this prompt; (b) `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` in the pod's launch line — allocator
   hygiene, no effect on what the model computes. Both are disclosed in the record's `re_emission`; `extractor_version` is unchanged; hosts have differed before
   and the outputs stayed byte-identical on 122 rows, so a different card is not a different instrument — a divergence, if any, is named at the reading.
3. **The crash cost $0.62 of waiting, not computing** — the runner died at 164 s and the Mac waited for a third reply until the deadline. A caught TRANSPORT defect
   (§4, one test both directions, in the fix's commit): the runner catches a unit's exception, writes an ERROR reply for that unit (`error`, the exception's name,
   the unit) and exits non-zero; the Mac treats an error reply among the smoke's three as «the smoke did not come back» and deletes AT ONCE. The runner's pin
   moves with the fix — the re-emission carries it.
4. **Iteration 5 = the re-buy, the NEXT number by §6.5 and the LAST of the registered five**; same `extractor_version`, same pins but the runner's, the card and
   the price as in 2; line **`promo-iter5`**, cap **$1.40** (operator 05.09 16:35), FITS on the mean corner at the day's price (the dry run quotes it), the hard
   stop from the cap, the 90-min backstop lifted to the cap's own minutes if it bites first (the registration says which). Sequence as (v)4. If iteration 5 reads
   RED on dev-40, the registered question closes red and the operator decides; GREEN → holdout-2's gold and its shot on `promo-holdout2`.
5. Money after it: cycle 3 REMAINING $2.81 → ≥ $1.41 → holdout-2 ≤ $0.90 → c3 needs the ceiling raised (the account holds $8.29) — the operator's word then.
6. **(w) addendum, 05.09 18:20 — s27 ACCEPTED by diff (`961d425` the team-lead files; `e75342b` the ledger; `a68d999`…`89f775a` PROGRESS, 60 lines; $0):**
   (w)1 could not pass as the ledger stood — `recorded_reading()` takes the line's LAST open `step_spent_usd` as the tolerance gate's right-hand
   side, and `promo-iter4`'s only entry was s26's PRE-pod $0.0097: a settled ~$0.6915 is ~7000 % off, refused every time, not once. Every line that
   ever closed under a tolerance settled against a POST-run reading (`lora-c` 0.7338→0.764952 · `promo-pulse-1` 3.0335→2.986741 · `srv2b` · `srv2d`
   · `45h2`, re-read in the ledgers today), so the reading is the guard's own path: **$0.7143 at 14:40:49Z (balance 8.2403244051), the session's one
   ledger line — accepted**; expected gap to the settle 3.19 % < 5 % (the volume's drip, as `promo-pulse-1` named at 3.15 %). The close waits on
   billing (walk 57.7 % at 14:57Z; `complete()` refuses a PARTIAL walk): **retried at the next session's start, read-only walk first, $0, the command
   as PROGRESS carries it**. My miss, the day's fourth money one: (w)1 ordered a close whose reference the line did not have. **PHASE v13 §6.1: a
   line's gate reference is its post-run `--note`, taken after the pod is deleted and before ANY next pod; a line whose readings all predate its pod
   closes on the walk alone and never takes a late reading.** That line is `promo-holdout` today: its one entry reads 0.0 (pre-pod) and the guard
   skips the tolerance on a 0/None reading, so it closes at $0 on `--expect-ms 1443000 --until <any instant between its last billing row and
   13:21:09Z> --tolerance 0.05` (unbounded, the walk swallows iteration 4's pod); a `--note` on it NOW would read ≈ $1.06 and shut it for good. Order: both closes → (w)3 → (w)4.

## Ruling 05.09 (x) — s28 ACCEPTED (both closes, (w)3 at $0, report (k) sessions 9–28); a fresh verifier read the runner fix and the money paths BEFORE the purchase and found five latent bites — iteration 5 goes in TWO sessions: «iteration 5 prep» ($0, ends at the committed registration) → my reading of the record → «iteration 5» (paid, cap $1.40)

1. Accepted by diff and my own readings: `promo-iter4` CLOSED $0.694815 (walk 3 363 287 / 3 364 000 ms, 2.73 % off its post-run $0.7143) · `promo-holdout` CLOSED $0.298209 on the walk
   alone (`window_end` 08:20Z, recorded 0.0) · cycle 3 **$6.2494 of $9.00, REMAINING $2.7506** · (w)3 `acfe360`+`54c0cc5` with its resume refusal (the fix's consequence, not a new guard)
   and ONE test both directions, `--part dev` asserted · `make check` 4322/2 at `54c0cc5`, docs-only after it · report (k) 21 lines, every number re-read in its file. No stop, $0.
2. **«iteration 5 prep» = ONE $0 item** (check: `make check` green + `--dry-run` FITS shown): `ITERATION = 5`; `--register --part dev --step promo-iter5 --cap 1.40` — the emitter's
   default `STEP` is `promo-dev-loop`, whose guard now REFUSES (exit 1): the guard is never called without `--step`; `re_emission` discloses the card and `expandable_segments`.
3. **The card is a PARAMETER of the emitter, not a new constant** — two names read at $0 from `runpodctl gpu list`: the gpu-id (typed at `--open --card`, rung 1) and the `displayName`
   (`offered_price`, EXACT — «RTX PRO 4500», not «… SE»), in (w)2's order: `NVIDIA RTX PRO 4500 Blackwell` 32 GB ($0.72/h secure on 24.08, no community offer), else A6000 / L40S;
   price = the day's dearer offer ≤ $0.90/h. **Backstop ((w)4):** `terminate_after_minutes` = the cap's minutes at the registered price when the borrowed 90 would bite first (the mean
   corner at $0.72/h is ≈ 71 min; a slower card needs the room); the record says which bound is live — the cap is the hard stop, nothing else bounds the money.
4. **The Mac reads an ERROR reply everywhere it reads replies:** `smoke_state` through `whole_lines` (a torn line is «waiting», not a traceback); `--close-segment`'s rate row and `--score`
   count an error row as unanswered instead of dying after the gate — inside (w)3's ONE test, extended. The runbook is re-pointed to iteration 5 in this item (part dev, `_iter5` files,
   `promo-iter5` $1.40, the card's gpu-id, the allocator env in the launch line, `--smoke` + `pgrep`) so the paid session pastes. The $0 fit proof stays a named debt: with (w)3 the
   smoke's longest unit is the fit proof at minutes' cost. Then `--pack`, commit, END; the purchase is the NEXT session after my reading of the record — sequence (v)4, close as v13
   (post-run `--note` before any next pod, `--until` after the pod), `--score --arm dev40` (BAR) · `--arm dev2` (READING). The ceiling for holdout-2/c3 is the operator's word (table
   in the team-lead message). Skill v3.9: a fresh verifier reads every money path BEFORE a purchase, not after a stop.

## Ruling 06.09 (y) — s29 «iteration 5 prep» ACCEPTED ($0); the stop was RIGHT and PREVENTABLE by the team lead (the fifth money miss): the registration OPENS the line, so it runs in the PAID session, minutes before the create — (x)2's «prep ends at the committed registration» is withdrawn; my pre-purchase reading is the dry run + HEAD, done today; the purchase is the NEXT session

1. Accepted by diff and my own readings at `31a6bc5`: (x)3 card and backstop as FIELDS (`offered_price`, `backstop`; `runpodctl gpu list` today: `RTX PRO 4500` 32 GB,
   gpu-id `NVIDIA RTX PRO 4500 Blackwell`, $0.72/h secure, EU-RO-1 High; A6000 none; L40S absent) · (x)4 the ERROR row read in `reply_rows` / `answered_rows` /
   `whole_run_row` / `--score`, the close gate appended BEFORE the rate row · runbook on `_iter5` · ONE test both directions (90 vs 7000 s → 116 live; 90 vs 2500 s → 41).
   Bound at source: `results/measurements.jsonl` whole-run **47.6615 s/thread** (pod `cd918wet7sea5b`, n = 40, the slowest) → rung 0 by my own arithmetic
   (279 + 83 × 47.6615) s × $0.72/h = **$0.8470 FITS** of $1.40 on the mean corner, dear $4.8633 named; hard stop 7000 s = 116 min, the cap live. No pod alive;
   `results/spend_promo_iter5.json` ABSENT. A fresh verifier (read-only, HEAD `31a6bc5`) CONFIRMED seven readings and found one bite + two risks (items 3–4).
2. **The stop's answer is (ii).** `--register` reads the guard WITH `--step`, and that reading CREATES and anchors the line; the close's right-hand side is a balance delta
   with the volume's drip IN while the settled figure keeps it OUT, so the anchor's AGE is the drift (iter4: $0.019444 = the volume line exactly, 2.73 % over 2.45 h;
   the 5 % band shuts at ≈ 4 h of age before the pod). PROCESS «Money» v2's order stands; (x)2 sat the anchor a session early. (i) rejected — a rule on the operator's
   clock; (iii) rejected — a ledger is never deleted. Fix the runbook's §0a FIRST (verifier bite 1): `--pack` before the commit refuses on `committed_registration()`.
3. **«iteration 5» (paid, cap $1.40) is the NEXT session, §0a inside it:** `--dry-run --part dev` → `--register --part dev --step promo-iter5 --cap 1.40` (FITS shown) →
   commit `results/promo_dev40_prep.json` + `results/prereg_promo_dev_loop.json` + `results/spend_promo_iter5.json` → `--pack --part dev` → commit the pack → `make check`
   at that HEAD (its tests read the committed record) → §0 → §1 create → smoke → the 80 → delete → `--close-segment --replies` → post-run `--note` on `promo-iter5` →
   `--close --expect-ms <segment ms> --until <after the pod> --tolerance 0.05` → `--score --arm dev40` (BAR 0.80/0.75) · `--arm dev2` (READING) → END. A refusal at
   `--register` (price moved, no card in stock, FITS lost) ENDS the turn with the guard's and the listing's output — before any create. No top-up before the run.
4. Named, not built (PROGRESS): risk 2 — readers key on a truthy `error`, an exception with an EMPTY message reads as answered (`pgrep` still deletes the pod; fix
   `"exception" in row` + (w)3's test, first $0 item after iteration 5); risk 3 — `close_segment` sums ALL segments of the batch-scale run record against the cap, so its
   `OVER` is a false field nothing gates on (the money is the guard's line) — filter by `anchored_at`, same item. The ceiling word waits for iteration 5's settlement.
5. Team lead: PHASE **v14** §6.1, PROCESS «Money» **v2.1**, patterns 06.09, STATUS; skill v3.11 — «registration ≠ opening», «the standing law beats a ruling on a mechanic».

**(y) addendum, 06.09 13:55 — s30 ACCEPTED ($0, no stop).** Runbook §0a at `4b996af` read in full: the registration FIRST and its own commit, the pack SECOND and its own commit
(the verifier's bite closed; the refusal was DEMONSTRATED by the executor and its mechanism re-read by me in `committed_registration()`), then `ruff` + three pytest slices
whose coverage and floor are COMMANDS — re-run by me: 229 test files, slices 60 + 85 + 84 COVER, `ruff` clean, `results/` clean against HEAD (the committed record is still
iteration 4's, as it must be until §0a re-emits it). Docs-only diff, no test/pin/guard/ledger added; the `hot.md` contradiction corrected under PROCESS v2.1 without a stop.
**Next session = «iteration 5», PAID, ≤ $1.40, nothing in front of §0a.** GREEN on dev-40 → holdout-2 gold (team lead, blind) → the shot; RED → the question closes red, the operator's word.

## Ruling 06.09 (z) — iteration 5 ACCEPTED on a COMPLETE reading: both dev-40 bars HOLD under law v1.2 (subject 0.8857 · signal 0.8667); the dev loop is DONE at 5 of 5; the instrument is FROZEN as bought (`d598573`); `promo-iter5` closes at the next start; next, in parallel: the team lead's holdout-2 gold (blind) and the executor's «holdout-2 prep» ($0, ends at the DRY RUN) → the shot

1. Accepted by files and my own runs: `results/promo_dev40_iter5.jsonl` 80 rows / 80 ids / 0 ERROR rows; both error tables 40/40, `parse_failures 0`, dead []; K8 v2 re-run by me on both
   arms — dev-40 **0.8857 / 0.8667 HOLD** (identical to `grade_promo_dev40_iter5.json`), dev-2 0.8883 / 0.8296 (a READING: dev-2 is the spent holdout-40 whose misses v1.2 was written on);
   stratum readings dev-40 currency 0.7869 · decimal 0.962. Ruling (w) answered: the SERVING was the cause — the 14 281-char render answered in 313.9 s on 32 GB, `finish stop`, no OOM.
2. Money by files: registration `d598573` FITS at the mean $0.8470 (= my arithmetic of 06.09), card/price/backstop as fields (116 min, the cap live), anchor 11:06:19Z; pod `xt4c5osyr36ew0`
   11:20:39Z → 12:38:57Z, 4698 s = **$0.9396**; post-run reading **$0.9495 of $1.40** (drift 1.04 % — (y)'s same-session rule, measured); cycle 3 **$7.3933 of $9.00, REMAINING $1.6067**;
   `pod list -a` []. `--close` refused on a PARTIAL walk (1 072 748 of 4 698 000 ms) — a delay, not a decision: retried read-only at the next session's start (expected ≈ 1 % off).
   New whole-run row **53.6254 s/thread (max 313.867, n = 80)** prices holdout-2. The `close_segment` `OVER` is the false field (y)4 named — it fired as predicted and gates nothing.
3. **The instrument is FROZEN as bought (§6.2):** codebook `86ed01a4…` · template `32fa6c42…` · `promo_prompts.py da60348d…` · runner `87072444…` — the four pins the holdout-2
   registration carries byte for byte. Verifier risks 2–3 are fixed on the MAC side only (`promo_dev_pass.py`: `"exception" in row`; `close_segment` filtered by `anchored_at`), inside
   (w)3's ONE test extended — the runner does not move. A pin that moves before the shot is a stop.
4. **Next, in parallel:** the team lead labels holdout-2 BLIND (112 comments, `results/promo_threads_draw_2.json`); the executor's ONE $0 item **«holdout-2 prep»**: the holdout-2 leg as
   a PART of the emitter (`--part holdout2`: draw-2's holdout arm, gold `docs/labels-promo-holdout2.jsonl`, step `promo-holdout2`, own stem/files; every decision field of the record
   branches on the leg — §4), item 3's two fixes, the runbook re-pointed to the shot (§0a inside the paid session, (y)), `--dry-run --part holdout2` shown (mean corner on 53.6254 ≈ $0.52,
   dear ≈ $2.81 → issued on the mean; cap $0.90 = hard stop 4500 s), `promo-iter5` closed at start; it ENDS at the committed dry run — no `--register`. Then the fresh verifier → my reading
   → the shot in the session after the gold is committed (the registration pins it); §6.2's notice to the operator = the dry run's figure, before that session.
5. Ceiling: $1.6067 − ≈ $0.24/day holds the shot under $9.00 for ≈ 2.5 days; c3 ($0.50) does not fit behind it → the operator's word (keep $9.00 · $10.00 · $10.50), not blocking the shot.
   Stop class: planned read (§6.2 notice) — nothing preventable. The day: 3 executor sessions, 1 stop (s29, mine), 1 planned read.

**(z) addendum, 06.09 15:55 — the operator's money word: cycle-3 ceiling $10.00** (from $9.00; the anchor $14.4799665639 of 01.09 does NOT move — a ceiling is a line, not a balance;
no top-up). Applied by the executor at the next session's start exactly as (s) addendum 8 was: `CYCLE3_CAP_USD = 10.00` in `scripts/runpod_guard.py`, one commit by path, shown by the
guard's own line `CYCLE 3 SPENT $… of $10.00` on the `promo-iter5` close retry (REMAINING at the 12:39Z reading becomes $2.6067). What it buys: the holdout-2 shot (≤ $0.90) + c3
(≤ $0.50) + the volume's drip for ≈ 4 days. The operator is asked again only if a sixth reading is ever needed.

**(z) addendum 2, 06.09 16:50 — the holdout-2 gold is on the mount, labelled BLIND:** `docs/labels-promo-holdout2.jsonl` — **112 rows** (47 currency + 65 decimal_only)
over the 40 threads of `results/promo_threads_draw_2.json :: draw.*.holdout`, sha256 **`5525ddf1e16390dfec65934627e2bdf481ad4547966e537373e969dd431a9a48`**, written by the
team lead under codebook v1.2 (`86ed01a4…`) without opening any iteration-5 prediction file; self-checked by the team lead's validator (every quote a substring, 40/40
threads covered, 0 rows on wordless comments, disjoint from dev-40 / dev-2 / holdout-40); 36 rows carry `unsure` (the tie named; the row stays in the denominator).
Executor: it is an UNTRACKED team-lead file — commit it by path in the start ritual (`git add docs/labels-promo-holdout2.jsonl`, one commit, `shasum -a 256` shown), never
edit it; the holdout-2 registration pins it as the leg's gold (§4 (c)); `--dry-run --part holdout2` now has its gold. Nothing else in (z)4 moves: «holdout-2 prep» ends at the
committed dry run, no `--register`; then the fresh verifier → the team lead's reading → the shot. PHASE v16 §2 names the file. Class: no stop — a planned team-lead deliverable.

## Ruling 06.09 (aa) — s32 «holdout-2 prep» ACCEPTED ($0) on my own runs; the fresh verifier says SAFE TO BUY with one risk and two nits that are a ≤ 3-line RUNBOOK fix; the operator's word 17:45: **GO, cap $0.90** — the NEXT executor session is the PAID «holdout-2» shot, opened by that fix, then runbook §0a → §7 → `--score --part holdout2` → END at the reading

1. Accepted by files and my own runs: `--dry-run --part holdout2 --out /tmp/…` is IDENTICAL to `results/promo_holdout2_prep.json` (sorted keys: 40 threads, longest render 10 529 chars, gold `5525ddf1…` 112 rows pinned, rate 53.6254 s/thread whole run n = 80, max 313.867); my read-only rung 0 at today's offer (RTX PRO 4500 Blackwell $0.72/h, EU-RO-1 High): cheap **$0.5170** (−42.6 %) · priced $0.5728 · dear $2.8109 (+212 %) → **FITS on the mean, hard stop 4500 s = 75 min**; the four pins on disk == `d598573`; `pod list -a` []; `promo-iter5` CLOSED in its ledger (14:21:40Z, walk 4 698 769 ms ≥ 4 698 000, pods $0.9450, 0.47 % off the post-run reading); guard `CYCLE3_CAP_USD = 10.00` (REMAINING $2.5723 at the verifier's read-only reading); the ONE test extended both directions — (e) `died()` in every reader, (f) the anchor filter and its two refusals, (g) the `--cap` refusal; runbook re-pointed; tree clean at `2c20513`; `make check` 4323/2 shown by the executor.
2. Fresh verifier (subagent at HEAD, 32 reads, 20 tests + ruff + listing + its own dry run and rung 0): **SAFE TO BUY as written.** RISK: a second `--register` on the anchored line refuses once the line has swallowed any cent (`cap = min(cap, step_remaining, remaining)`, `promo_dev_pass.py:1080–1086`) — the runbook's own recovery paths (a price move in §0 → «re-read rung 0 with `--register`»; a STOP retried ≥ 1 h later) would hit it. NIT: the §0a pin check prints «PIN MOVED — STOP» with exit 0, unchained, and runs AFTER the anchoring `--register`. NIT: at spent == cap (the hard stop fired) the post-run `--note` refuses and the runbook does not say the close then settles on the walk alone. NIT: dev-40 display residue (`phase`, «iteration None») — nothing reads it, stays named.
3. **The paid session opens with a ≤ 3-line runbook fix by path — no code, no test, no pin moves** (PROCESS «Money» v2.2, PHASE v17): (a) the four-pin check runs on the disk files BEFORE `--register` and exits 1 on `moved`, the commit chained with `&&`; (b) a re-registration after the anchor goes under a NEW line (`--step promo-holdout2-r2`, its own ledger) or with `--cap` = the guard's printed remaining of the line — never a second `--register` on the anchored line; (c) if the post-run `--note` refuses at spent == cap it is not retried — `--close` settles on the walk alone. One commit by path, then §0a exactly as written: `--dry-run` → `--register --part holdout2 --step promo-holdout2 --cap 0.90` (FITS shown) → commit → `--pack --part holdout2` → commit → `ruff` + the three slices → §0 … §7 → `--score --part holdout2` (subject ≥ 0.80 · signal ≥ 0.75 on 112 rows, ONE arm) → the post-run `--note`, `--close` → END the turn at the reading, the error table named — my planned read (§6.2).
4. Money: **cap $0.90 = the operator's word (06.09 17:45)**, quoted from the dry run's rung 0 (FITS at $0.5170 on the mean corner); the line `promo-holdout2` opens at `--register` inside the paid session; REMAINING $2.5723 → ≈ $1.67 after the shot at the mean, ≈ $1.68 at worst (the hard stop) → c3 ≤ $0.50 → the drip ≈ $0.24/day: inside $10.00, no new word unless the platform stop fires. The instrument does not move: a pin that differs from `d598573` at the check is a STOP before any anchor.
5. Class: planned read (§6.2 notice given and answered) — no stop; the verifier's finding = a stop that did not happen, its pattern in PROCESS v2.2 / PHASE v17 / skill v3.12. The day: 4 executor sessions (s29–s32), 1 stop (s29, mine), 2 planned reads.

## Ruling 06.09 (bb) — holdout-2 READ on a COMPLETE reading under the instrument frozen at `d598573`: signal 0.8021 HOLDS, subject 0.7054 RED (79 of 112) — S2's question is closed by the second reading, RED on subject twice (holdout-40 0.7181, holdout-2 0.7054); the shot cost $0.4232 of $0.90; the line closes at the next start; the next word is the operator's

1. Accepted by files and my own runs: `results/promo_holdout2_predicted.jsonl` 112 rows / 40 threads; `promo_holdout2_errors.json` `leg_a_units_answered 40`, `parse_failures 0`, dead []; my K8 v2 run (`grade_promo_signals.py --part holdout --draw results/promo_threads_draw_2.json`, `--out /tmp`) identical to `results/grade_promo_holdout2.json`: **signal 0.8021 (bar 0.75) HOLDS · subject 0.7054 (bar 0.80) RED**; strata currency 0.766 / 0.7125 · decimal 0.6615 / 0.8917. A COMPLETE reading (§6.5): the 3 smoke units are the run's first 3, 40/40 answered, `finish=stop` on all.
2. The instrument: registration `3193858` carries the four pins of `d598573` byte for byte (read against the disk and the dev-bar record), the gold `5525ddf1…` and draw-2 pinned; rung 0 FITS on the mean at $0.72/h, hard stop 4500 s; rung 1 GO; the pin GATE ran before `--register` ((aa) fix `215f80f`, self-tested both ways). §9 holds: the holdout number and the dev number belong to one instrument.
3. Money: pod `p3krn2lwhhcyyi` 16:45:21Z → 17:20:37Z, 2116 s = **$0.4232** of $0.90 (forecast $0.5170; the card ran **40.8653 s/thread, n = 40, max 219.4** — 24 % faster than iteration 5's 53.6); post-run reading 17:21:14Z **$0.4107** = the close's reference; `--close` refused on «no billing rows yet» (walk 0 of 2 116 000 ms) — a delay: retried at the next start, read-only walk first; cycle 3 **$7.8480 of $10.00, REMAINING $2.1520**; `pod list -a` []. One registration, one segment on the line (`segments_of_this_line 1` — (y)4's filter live). The create was denied twice by the executor's harness classifier and lifted by the operator's word — no money, ≈ 16 min of anchor age → patterns §5, the executor kit.
4. The 33 subject misses read in full (my tool over gold × predicted with the grader's own keys): **15 rows carry the gold's own `unsure` and the model chose the alternative I named** (a post-hoc reading with every tie resolved the model's way ≈ 0.84 — a reading, never the bar); **6** «not in stock / near expiry» read as the PRODUCT where the codebook says the store (`chain`); **6** the retailer's own posts (typo, raffle terms, sarcasm at the store) read as a `sku` or `post`; **2** `post` rows whose subject the model set to the PARENT comment's id, not the thread root (a format rule, K8 exact); **2** word forms (`чіпси`/`чипси` — my gold's spelling, the normative form is «чипси»; `ягоди`/`ягоды`); 1 irony misread; 1 invented `brand/виробник`. Signals: 26 threads at 1.0, 5 at 0.67, 5 at 0.5, 1 at 0.25, 3 at 0.0.
5. Verdict by the registered question: **NO** — the instrument does not clear subject ≥ 0.80 on the product's population; it clears signals twice (0.7958, 0.8021). Subject ≈ 0.71 on two independent draws: the dev bar 0.8857 was fit on dev-40 (five iterations on its misses) and does not transfer. Holdout-2 is spent — **dev-3**, a reading, never a bar again. Class: planned read. **The next word is the operator's** (decision table, one visit): (a) ship as measured — S2 red on subject, green on signals, the numbers on the screen, c3 → gate 11–12.09; (b) a **$0 post-processing layer** on the reader's output (`post` = the thread root; store-stock and sarcasm-at-the-store → `chain`; Ukrainian word forms) written from the misses of dev-40 + dev-2 + dev-3, measured at $0 on all 439 rows (the predictions exist), then ONE holdout-3 shot (≈ $0.45 at 40.9 s/thread) for the bar — +1–2 days, inside $10.00 beside c3; (c) codebook v1.3 + a new dev loop — a new money cycle, +3–4 days.

**(bb) addendum, 06.09 20:05 — the operator's word: (b) — a $0 post-processing layer P1 over the reader's output, then ONE holdout-3 shot.** Honest expectation first: the deterministic rules below reach 8 of holdout-2's 33 misses (2 format + 6 store-stock) → ≈ 0.777 on dev-3 — the bar 0.80 is NOT assured; that is why the purchase is gated on a $0 reading. PHASE v18 §2 defines P1 and §6.2 the holdout-3 stop-point with its decision table. **Executor's ONE item «p1-prep» ($0), one check = the table of numbers:** (1) start ritual — commit team-lead files by path; `--close` of `promo-holdout2` read-only walk first (`--expect-ms 2116000 --until <after 17:20:37Z, before any next pod>`, reference = the 17:21:14Z reading); (2) **holdout-3 DRAW** at $0: `results/promo_threads_draw_3.json` — seed 42 over draw-2's `eligible_after` (398) MINUS holdout-2's 40 threads (= 358), 20/20 by stratum, disjoint from all 120 drawn, the draw producer re-used with its paths as PARAMETERS (§4 (c)); no gold yet — the team lead labels it BLIND; (3) **P1 = `src/market_pulse/promo_post.py`**, a pure function over predicted rows + the thread (post text, channel, registry), exactly the three conventions of PHASE v18 §2 — R1 `post` ⇒ subject = thread root; R2 in a retailer's OWN channel a `post` row with non-empty signals ⇒ `chain` = the channel's owner; R3 a `sku`/`brand` row with `жалоба` whose comment matches the store-stock lexicon (немає · нема · не було · нет в наличии · небыло · не знайшла/не знайшов · не можливо вхопити/купити · закінчується термін придатності · прострочен) ⇒ `chain` = the thread's retailer (own channel → the owner; aggregator → the ONE registry chain named in the post, else the row stays) — nothing else, no sarcasm rule, no word-form rule; ONE test, both directions per rule (a product component's invariant, §3.3); (4) P1 applied to the EXISTING predictions — `promo_dev40_predicted_iter5.jsonl` (dev-40, 139 rows), `promo_dev2_predicted_iter5.jsonl` (dev-2, 188), `promo_holdout2_predicted.jsonl` (**dev-3**, 112) → `results/promo_p1_predicted_<set>.jsonl` + K8 v2 before/after per set in `results/grade_promo_p1_readings.json`, shown as a table; leak-check: R3's lexicon comes from the codebook's words and the three DEV error tables only — holdout-3 is never opened. ENDS at the table — no registration, no pod. **Decision rule, pre-registered (PHASE v18 §6.2): the holdout-3 shot is bought only if P1's dev-3 subject reading ≥ 0.80 AND dev-40 / dev-2 stay ≥ their bars; otherwise the fork returns to the operator with the numbers (ship as measured · codebook v1.3) at $0.** Money: fence ≤ $0.50 for the shot (an ESTIMATE — re-priced at its registration on the measured 40.8653 s/thread), c3 ≤ $0.50, drip ≈ $0.24/day: inside REMAINING $2.1520 for ≈ 3 days. Gate estimate → 13–14.09.

## Ruling 06.09 (cc) — s34 «p1-prep» ACCEPTED ($0): `promo-holdout2` CLOSED $0.4253, holdout-3 DRAWN blind (358 → 20/20, 133 text comments), P1 built with its ONE test, the $0 table read by me — dev-3 0.7054 → **0.7500**, dev-40 0.8857 =, dev-2 0.8883 → 0.9043, signals unmoved; the pre-registered decision table RETURNS the fork to the operator at $0 — the holdout-3 shot is NOT bought; the stop is planned and right

1. Accepted by files and my own runs: my K8 v2 on `results/promo_p1_predicted_dev3.jsonl` = **0.7500 / 0.8021** (84/112; currency 0.7872 · decimal 0.7231), on `…_dev40.jsonl` = 0.8857 / 0.8667 — identical to `results/grade_promo_p1_readings.json` (two executor runs byte-identical); draw-3 record: 358 eligible, 20/20, **0 overlap with the 120 drawn**, no reader opened its threads; ledger `promo-holdout2` closed (walk 2 116 299 ≥ 2 116 000 ms, $0.4253 pods, 3.6 % off the post-run $0.4107); cycle 3 $7.8822 of $10.00, REMAINING $2.1178; `pod list -a` []; `make check` 4326/2 at `9b8a2de`; the ONE test both directions per rule; nothing added beyond the addendum.
2. What the $0 table says, plainly: P1 reached 5 of the 8 misses I named (2 format + 3 store-stock); the 3 it did not reach are the law as written («нет пока» not in the lexicon; `спрос` without `жалоба`; a chain the registry does not carry) — a lexicon ruling would lift dev-3 to at most 87/112 = 0.777, still red. **No deterministic rule reaches 0.80 on dev-3: 15 of the remaining 28 misses are the gold's own declared ties** (store-stock → chain vs product; own channel → chain vs post), i.e. the codebook's ambiguity, not the reader's. Signals hold on every set.
3. Money: $0 spent this session; the shot is not bought (the addendum's rule, as written). Draw-3 stays frozen and unlabelled until the operator's word — the gold is written only for a branch that buys the shot.
4. **The operator's decision table (one visit):** (a) **ship as measured** — S2 red on subject (0.7500 with P1 on holdout-2; raw 0.7054 / 0.7181 on two draws), green on signals (0.8021 / 0.7958); P1 ships in the product; the numbers and the tie analysis go on the screen and into the README; c3 next → gate 12–13.09; $0. (b) **K8 v3 «declared ties» + holdout-3** — a gold row may declare ONE alternative subject and the grader accepts either; pre-registered BEFORE the holdout-3 gold exists; re-read at $0 on dev-40 / dev-2 / dev-3 first (dev-3 post hoc ≈ 0.84), the same buy rule (dev-3 ≥ 0.80 under K8 v3), instrument unchanged (frozen prompt + P1), the shot ≈ $0.45 — the bar's meaning changes to «agreement with either defensible reading» and is disclosed as such everywhere the number appears; +1–2 days (133 comments to label), gate 13–14.09. (c) **codebook v1.3** — conventions resolved, the prompt re-rendered → the instrument moves → a paid dev iteration ≈ $0.95 + the shot ≈ $0.45 ≈ $1.40 + c3 $0.50 against $2.12 with no room for the drip: a new money cycle in practice; +3–4 days, gate 15–16.09.
5. Class: planned read (the decision table fired as pre-registered — nothing preventable; the stop is the phase file's own design). The day: 6 executor sessions, 2 stops (s29, s33), 3 planned reads + this fork.

**(cc) addendum, 06.09 21:45 — the operator's word, after the fork was re-explained in plain words: (a) SHIP AS MEASURED.** S2 closes on the second reading: subject **0.7500** with P1 on holdout-2 (raw 0.7054; holdout-40 0.7181), signal **0.8021** (0.7958) — RED on subject, GREEN on signals; both numbers with their files go on the screen and into the README, the tie analysis beside them (15 of the 28 remaining misses are the codebook's own declared ties: store-stock → chain vs product; own channel → chain vs post). No further purchase for S2; draw-3 (`76435461…`) stays frozen and UNLABELLED — a reserve, never opened. **Executor's ONE next item «p1-ship» ($0):** P1 wired into the product — `make tick` applies `promo_post.apply` to every reader row before the aggregates (the idempotency check stays: two ticks → 0 new rows); the screen's S2 block and the README read their numbers from `results/grade_promo_p1_readings.json`, `results/grade_promo_holdout2.json`, `results/grade_promo_holdout40.json` (fail loudly if a file is missing), labelled «holdout · with P1 / raw»; `make check` ≥ 4326; ENDS at the shown screen block — no registration, no pod. Then «c3-prep» ($0: the c3 leg per ruling (l) 2–4 on its own line `promo-c3`, cap ≤ $0.50 re-priced at its dry run, the create permission PROVEN at $0 (PROCESS v2.3), the runbook re-pointed) → the fresh verifier → «c3» (paid) → the volume `mp-srv2` deleted → clean-clone e2e + `draw_truth_20` → the operator's gate **12–13.09**. Team lead in parallel: positions-50 gold (46 pages) → K6 → the S1 bars. Class: planned read; the operator's «объясни, я запутался» = a red gate on the MAP (§8) — the fork was written in the team lead's jargon; the plain explanation is now STATUS «Честно» and patterns §6.
