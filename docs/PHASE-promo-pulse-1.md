# PHASE — `promo-pulse-1` (stage 1 whole: C2–C5 of `docs/SPEC-v2-promo-pulse.md` §8) — v9 05.09: §2 S2 holdout-40 read RED on subject → codebook v1.2, dev-2, holdout-2 (in-domain population), K8 v2; §4 «asked for once» + a re-used producer's record branches every decision field, §6.5 validity of a paid reading, §6.6 a test that reads the record, §6.1–6.2 a fence is an estimate and the frozen-set instrument is byte-for-byte

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
  plateaus (two iterations without gain). **v9 (05.09, ruling (s)): holdout-40 was SPENT under law v1.2/K8 v1 —
  signal 0.7958 HOLDS, subject 0.7181 RED (`results/grade_promo_holdout40.json`, complete reading); it is now
  `dev-2`, a reading, never a bar again. The line continues: codebook v1.2 (team lead) → law re-rendered → iteration 4
  on dev-40 (the same two bars; dev-2 read beside it, no bar; ≤ 5 dev runs in total still) → the ONE `holdout-2` shot.
  `holdout-2`: seed 42 over the frozen 678 price threads MINUS channels with `collect: false` in registry r2 (the
  product's population) MINUS the 80 already drawn, 20/20 by stratum, a NEW draw file — the old draw stays frozen.
  K8 v2 for that line: `sku`/`brand` match on normalised exact OR token-Jaccard ≥ 0.5, `chain` folds as today, `post`
  exact — registered before iteration 4; the holdout-40 number stays under K8 v1.**
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
**Asked for here, once for all (v5, 04.09):** a caught PRODUCT defect gets ONE test, both directions, in the
same commit as its fix — no authorisation needed; every other new test, pin, guard or ledger stays forbidden.
Growth of a PINNED structure enters through its declared side file (`config/channel_admins.yaml`,
`config/chain_aliases.yaml`, `config/registry_extra.yaml` for a new channel), read by the one reader that
reads the pinned file; a second instance of anything (window, channel, carrier) keeps ONE id per entity across
sources and the screen renders all instances (`--window all`). Producers a new leg re-uses take their paths
as parameters (`--out --channels --anchor --prereg --step --cap`); a seal pins results, never a code path. **And every
field of the record such a producer WRITES that states a decision — bands, authority, out-of-scope, phase — branches on the
leg or the emitter refuses to write (v8, ruling (r)): a population parameterised under another leg's decision table is a false record.**

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
   **A fence for a LATER paid step is an estimate, never a cap (v7, ruling (q)):** it is re-priced at that
   step's registration on the instrument's OWN measured pace of the SLOWEST pod seen (hosts of one card ran
   1.5–2.3× apart on identical outputs), the cap becoming the hard stop; the holdout's cap was **$1.10**
   (operator 05.09; spent $0.2966 on a fast host); iteration 4 ≤ $0.60 (dev-40 + dev-2 in one pod), holdout-2 ≤ $0.90 on the measured pace,
   each with rung 0 FITS + the hard stop as its only money gate (ruling (r)); the cycle-3 ceiling is $9.00 from 05.09 (operator's word, ruling (s) addendum 8; anchor unchanged); c3 is deferred behind holdout-2.
   The volume `mp-srv2` is deleted after the phase's last paid run — now the holdout-2 shot (operator 05.09).
2. The ONE holdout attempt: pre-register (readings + the two bars), tell the operator it is being
   spent. **The instrument on the frozen set is the one that took the dev bar, byte for byte** — every pin
   of the dev-bar registration unchanged; cosmetic law moves queue behind the attempt (v7, ruling (q)).
3. The dev loop plateaus below the bars → STOP with the error table; the team lead reworks the
   codebook/prompt, not the executor.
4. Anything that would edit a sealed record, a frozen set, or a team-lead file.
5. **Validity of a paid reading (v5, 04.09, ruling (m)):** a reading COUNTS only when every registered unit
   is answered and parsed (`parse_failures = 0` in its error table). An incomplete run is recorded under its
   number, never compared to the bars or to the plateau rule; its transport defect (an answer the runner
   truncated, dropped or misparsed) is fixed with its one test (§4) and re-bought under the NEXT number
   inside the step's cap and the 5-run ceiling — NOT a stop, the diff named in the error table. Before
   the first purchase of a new instrument, the runner and the parser are drilled at $0 on every answer shape
   the prompt permits (object · array · fenced · unfenced); a shape the model produces later joins the drill once.
6. **A test that pinned a literal of the record (v6, 04.09, ruling (o)):** when a ruling moves the registered record (a population,
   a leg, a pin) and a test's INVARIANT still passes while only literals of that record diverge, the executor rewrites the test to read
   the committed record — the claim stated in both directions — in the same commit and shows the diff: NOT a stop. Weakening an
   invariant, or a test whose claim fails on the record, remains the stop of §8 (j). A fixture never invents a unit the record lacks.

## 7. Dependency the team lead owes

`docs/labels-positions-50.jsonl` and `docs/labels-promo-dev.jsonl` land after the executor's draws
(S1/S2) — C2 extraction and all $0 scaffolding (schema, hooks, graders, tick, digest) do not wait;
the graded readings and the holdout shot do.

## 8. DONE WHEN — the ONE `/goal` paste (v4, 03.09 — the PAUSE clause lost its resume tail, ruling 03.09 (c); v3 02.09; rulings file: `docs/reviews/2026-08-30-plan-promo-pulse-1.md`)

Only the USER can invoke `/goal`. Launch, every time (start and after every STOP, always in a
FRESH session): the operator TYPES `/goal ` by hand, then pastes the BODY below as the arguments —
a pasted block that begins with the command is plain text and no goal is active; the body must be
the file's bytes (it carries no slash command of its own — the parser cut v2 at its inner one);
if only «Goal set: …» appears and no tool call follows within a minute, send one word: «go».
Effort: `/effort xhigh` before the paste (PROCESS «Models and effort»); not `ultracode`.

```
Phase promo-pulse-1 (docs/PHASE-promo-pulse-1.md) is COMPLETE per docs/plans/promo-pulse-1.md and every dated ruling in docs/reviews/2026-08-30-plan-promo-pulse-1.md. START RITUAL every session, before anything else: commit any modified team-lead file by path (docs/STATUS.md, docs/PROCESS.md, docs/PHASE-*.md, docs/reviews/*); read the plan and the NEWEST dated section of the rulings file; if docs/plans/promo-pulse-1.STOP.md exists, apply the newest ruling to it and delete it. Money: cycle-3 is OPEN — the ceiling and per-leg caps are those the NEWEST dated ruling in the rulings file names, four rungs per docs/PROCESS.md; a projection over the ceiling is a STOP. Demonstrate every check by running its command and showing the output in the conversation — the evaluator reads only the transcript. Met when ALL hold: (a) results/promo_pagecount_c2.json states the exact page count per channel for the census window from store/metadata only (or a <=10-line impossibility note with the priced alternative), and results/promo_projection_c2.json prices C2 as ONE number at the marginal rate against the re-read remainder; (b) scripts/collect_5c1.py::collectable honours collect: false, both directions tested; (c) positions for the census window exist in data/derived/pulse.db for every collected channel (vision for image carriers, text for the rest), bought inside the ceiling with the rungs logged and each paid leg's spend line named in the report; (d) results/positions_draw_50.json drawn twice with identical sha256 and, once docs/labels-positions-50.jsonl exists, scripts/grade_positions.py reports completeness >= 0.90 and promo-price accuracy >= 0.95; (e) once docs/labels-promo-dev.jsonl exists, scripts/grade_promo_signals.py on dev-40 reports subject >= 0.80 and signal >= 0.75 within at most 5 dev runs, and the ONE holdout attempt is pre-registered in a committed record, announced via a STOP notice, then spent once; (f) pytest tests/test_trends_sql.py green: trends recomputed twice identical, an empty week absent never zero; (g) make tick exists and a second run on an unchanged store writes zero new rows, counted per table including unsure; (h) on a clean clone, make tick && make promo-screen renders the screen from result files only, and a removed source yields a non-zero exit with a named error; (i) scripts/draw_truth_20.py renders 20 rows under seed 42 for the operator's gate; (j) make check is green with passed >= 4266 plus the new tests and no test file deleted — a test that must change to pass is a STOP; (k) docs/reports/promo-pulse-1.md exists, <=30 lines, opens with the phase's question and answers it in the first ten lines, every number naming its file; (l) git status --porcelain src tests scripts config results docs/plans docs/reports prints nothing. ALSO met, as a PAUSE, when docs/plans/promo-pulse-1.STOP.md exists (shown with cat) naming one of: waiting on the team lead's labels (dev-40 or positions-50), the dev-loop plateau (two iterations without gain), the holdout pre-registration notice, a rung firing or a projection over the ceiling, a design fork the plan does not settle, a sealed or frozen file that would move, a test that would have to be weakened. Or stop after 80 turns.
```
