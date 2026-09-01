# PHASE — `promo-pulse-1` (stage 1 whole: C2–C5 of `docs/SPEC-v2-promo-pulse.md` §8)

Team-lead file. Executor: read this, then run `/plan-phase promo-pulse-1` and STOP for the plan
review. Mechanics named below are CONSTRAINTS; the goal is the question and the checks.

## 1. The operator's question and the artifact that answers it

«Что и почём промоутируют сети по молочке и мороженому, и как покупатели на это реагируют —
неделя за неделей?» The artifact: ONE screen (`dashboard/` promo view) built by `make tick` from
result files only, showing per week × chain: promo positions (brand · product · volume · promo price · printed −N%,
absent when none — the extracted old price is stored, flagged, NEVER printed: SPEC 3.21 (4)), depth per
chain and brand as a WINDOW AGGREGATE only (SPEC 3.22 (1)), price trend per SKU, and the reaction feed
(signal · quote · msg_id · thread) — plus the tables behind it in `data/derived/pulse.db`.

## 2. Success criteria — checks the executor can run (graders first, mechanics later)

- **S1 positions.** Grader `scripts/grade_positions.py` against the team lead's
  `docs/labels-positions-50.jsonl`: 50 positions drawn under seed 42 from ≥3 chains' flyers/posts
  of the backfilled 4 weeks → completeness ≥ 0.90 (gold matched on brand surface form · product ·
  volume), price accuracy ≥ 0.95 over the PROMO PRICE only (the green leg, 80/80); printed −N% and old
  price are readings, no bar. The draw script is the executor's, the labels are the team lead's; the
  grader runs at $0 once predictions exist. (Review 30.08, SP-0 q1–q2.)
- **S2 reactions.** Grader against `docs/labels-promo-dev.jsonl` (dev-40 price threads; population =
  ALL 678 price threads re-derived by `PRICE_BRANCHES` — a promo post with the price in the image IS a
  price post (operator 30.08: «Все 678, дро 20/20 по типу»); the draw — seed 42, 20 from the currency
  stratum + 20 from the `decimal`-only stratum, holdout-40 the same 20/20, disjoint, frozen — is
  produced by the executor at C3 step 0 as `results/promo_threads_draw.json`, the team lead labels from
  it; per-stratum agreement is reported beside the bars as a reading): per comment `about(subject,
  source ∈ explicit|reply_context|post_context)` and thread signals `{жалоба|похвала|спрос|привычка|
  цена}` with quote + msg_id. Bars on dev-40: subject agreement ≥ 0.80 · signal-type agreement
  ≥ 0.75. Holdout-40 (disjoint, frozen at the draw): ONE pre-registered attempt when the dev loop
  plateaus (two iterations without gain).
- **S3 trends.** SQL only, no LLM: price per SKU per week per chain; discount depth per chain and
  brand; test: recompute from `positions` twice → identical; a week with no data renders as absent,
  never as zero.
- **S4 the loop.** `make tick` is idempotent: run twice on an unchanged store → zero new rows
  (deterministic ids, uuid5 over normalised keys); reads `data/schedule.json` (min interval 1h,
  default 6h) and the cursors of `loop.py`; a thread is read when COOLED (24h without new comments),
  late comments join via the thread digest (children ids), never by re-reading raw. Hooks between
  calls: msg_id exists · quote is a substring · brand ∈ registry or `unknown-brand` · schema valid;
  a hook failure is a counted row, not an exception.
- **End-to-end (closes the phase):** on a CLEAN CLONE, `make tick && make promo-screen` from the raw
  store to the screen; the screen fails loudly on any missing source. Then the product-truth gate:
  20 rows under seed 42 (flyer/post · extracted position · comment · signal · quote) rendered for
  the operator, who says in his own words what is right and wrong.

## 3. Registry revision — step 0 of the phase (operator's ruling 30.08, confirmed list)

Write registry revision r2 (new revision, sealed file stays): **A1 prices, 17 rows** — `@atb_market_official`
(the LEAFLET carrier: all 159 pages of 5c2 and 106/145 positions; `media_share` 1.0 — the census's «без
промо» was a text-regex reading; images→vision), `@ATB_FANatik`
(+ its discussion group «АТБ / ЗНИЖКИ»), `@atb_aktsiyi` (images→vision), `@VARUS_channel`,
`@ekomarket_shop`, `@epicentrk_sale` (identity flag stays in the row), `@foraINFO`, Маркетопт private
(joined 30.08; images→vision), `@blyzenkoua`, `@silposilpo`, `@fozzyshopua`, `@sim23_simi`,
`@rrozetka`, `@msuaaaa`, `@kop1chat`, `@znishkom`, `@xochydeshevshe`. **A2 voice** — Varus, msuaaaa,
Копійочка, ATB_FANatik+group, Rozetka. **PAUSED 39** (moms/health/recipes/fitness) leave collection.
**B (Poltava) deferred to phase B** — census kept, nothing collected. Paused rows STAY in the registry
with `collect: false` (removing them breaks `pulse.db` at $0 — plan §5.2b). Every NEW channel enters
through the adaptation protocol (profile → sealed hundred → gate BEFORE aggregates/train);
ATB_FANatik's group traffic is measured at its entry — r1's 0.25 c/day read post replies, not the
group feed.

## 4. Files and interfaces (constraints, not steps)

Extend, do not fork: `positions.py` + 5c2 vision instrument (image flyers: Маркетопт, atb_aktsiyi,
Епіцентр); `pulse.db` gets `attribution / signal / evidence / digest / rollup / unsure` (schema: the plan's §5.7
as amended by `docs/reviews/2026-08-30-plan-promo-pulse-1.md` SP-5 — ids are uuid5 over normalised keys,
`window_id` never part of an identity); `loop.py` cursors carry the tick; `scorer.py` stays the single judge.
`prompts.py`, `local_llm.py`, pod runners, `registry.yaml`/`lexicon.yaml` are PINNED — new prompt
text goes in a NEW module; `make preflight` before touching anything pinned. Serving: existing stack,
thinking OFF, batch 1 for gate readings. Money mechanics: `docs/PROCESS.md` («Money»).

## 5. Out of scope

Brand trends/alerts; Poltava collection; training/LoRA; thinking anywhere; vLLM/merge; the schedule
UI (the loop only READS `data/schedule.json`); dashboard redesign beyond the one promo screen;
scanning the 81 unscanned census candidates.

## 6. Stop-points (ask BEFORE, never report after)

1. Any pod/serverless create (paid): smoke first, project at measured rates; estimate table —
   C2 vision backfill ≈ $0.4 · C3 dev loop (3–5 iterations × 40 threads × ~24 s) ≈ $1.1–1.7,
   cap $2.5 · holdout shot ≈ $0.3. **Cycle-2 remainder is $2.44** (guard, 30.08; the volume drips
   $0.2333/day): the programme already exceeds it, so the operator decides cycle-3 / narrowing / a pod
   runner AT S3's STOP on the census (K3) and the projection range (K4) — never trim scope silently.
2. The ONE holdout attempt: pre-register (readings + the two bars), tell the operator it is being
   spent.
3. The dev loop plateaus below the bars → STOP with the error table; the team lead reworks the
   codebook/prompt, not the executor.
4. Anything that would edit a sealed record, a frozen set, or a team-lead file.

## 7. Dependency the team lead owes

`docs/labels-positions-50.jsonl` and `docs/labels-promo-dev.jsonl` land after the executor's draws
(S1/S2) — C2 extraction and all $0 scaffolding (schema, hooks, graders, tick, digest) do not wait;
the graded readings and the holdout shot do.

## 8. DONE WHEN — the ONE `/goal` paste (v2, 01.09: only the USER can invoke /goal; the same paste starts the phase and resumes it after every STOP, always in a fresh session; rulings file: `docs/reviews/2026-08-30-plan-promo-pulse-1.md`)

```
/goal Phase promo-pulse-1 (docs/PHASE-promo-pulse-1.md) is COMPLETE per docs/plans/promo-pulse-1.md and every dated ruling in docs/reviews/2026-08-30-plan-promo-pulse-1.md. START RITUAL every session, before anything else: commit any modified team-lead file by path (docs/STATUS.md, docs/PROCESS.md, docs/PHASE-*.md, docs/reviews/*); read the plan and the NEWEST dated section of the rulings file; if docs/plans/promo-pulse-1.STOP.md exists, apply the newest ruling to it and delete it. Money: cycle-3 is OPEN (operator, 01.09) — ceiling $4.80 anchored at the current balance, four rungs and per-leg caps per docs/PROCESS.md; a projection over the ceiling is a STOP. Demonstrate every check by running its command and showing the output in the conversation — the evaluator reads only the transcript. Met when ALL hold: (a) results/promo_pagecount_c2.json states the exact page count per channel for the census window from store/metadata only (or a <=10-line impossibility note with the priced alternative), and results/promo_projection_c2.json prices C2 as ONE number at the marginal rate against the re-read remainder; (b) scripts/collect_5c1.py::collectable honours collect: false, both directions tested; (c) positions for the census window exist in data/derived/pulse.db for every collected channel (vision for image carriers, text for the rest), bought inside the ceiling with the rungs logged and each paid leg's spend line named in the report; (d) results/positions_draw_50.json drawn twice with identical sha256 and, once docs/labels-positions-50.jsonl exists, scripts/grade_positions.py reports completeness >= 0.90 and promo-price accuracy >= 0.95; (e) once docs/labels-promo-dev.jsonl exists, scripts/grade_promo_signals.py on dev-40 reports subject >= 0.80 and signal >= 0.75 within at most 5 dev runs, and the ONE holdout attempt is pre-registered in a committed record, announced via a STOP notice, then spent once; (f) pytest tests/test_trends_sql.py green: trends recomputed twice identical, an empty week absent never zero; (g) make tick exists and a second run on an unchanged store writes zero new rows, counted per table including unsure; (h) on a clean clone, make tick && make promo-screen renders the screen from result files only, and a removed source yields a non-zero exit with a named error; (i) scripts/draw_truth_20.py renders 20 rows under seed 42 for the operator's gate; (j) make check is green with passed >= 4205 plus the new tests and no test file deleted — a test that must change to pass is a STOP; (k) docs/reports/promo-pulse-1.md exists, <=30 lines, opens with the phase's question and answers it in the first ten lines, every number naming its file; (l) git status --porcelain src tests scripts config results docs/plans docs/reports prints nothing. ALSO met, as a PAUSE, when docs/plans/promo-pulse-1.STOP.md exists (shown with cat) naming one of: waiting on the team lead's labels (dev-40 or positions-50), the dev-loop plateau (two iterations without gain), the holdout pre-registration notice, a rung firing or a projection over the ceiling, a design fork the plan does not settle, a sealed or frozen file that would move, a test that would have to be weakened — after the ruling lands in the rulings file, the operator re-pastes this SAME /goal in a fresh session. Or stop after 80 turns.
```
