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
