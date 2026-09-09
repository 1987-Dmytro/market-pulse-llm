# PHASE — `promo-pulse-1` (stage 1 whole: C2–C5 of `docs/SPEC-v2-promo-pulse.md` §8) — v24 09.09 (ruling (hh)): §6.1 c3's cap is **$0.80** = min($0.80, REMAINING − $0.30) — the operator's word 15:20, quoted from the dry run (FITS $0.1864 at the dear corner); the verifier before the purchase read NOT SAFE at $0.50 (the in-run pack gate) — «c3-prep-3» ($0, fresh process: the detached launch, the close's flags, the API-key line, the volume AFTER the close, `register()` naming what it reads, the cap as a command) precedes «c3»; v23 09.09 (ruling (gg)): §6.1 the allow rules retired (inert in bypass), the paid runbook's §0 = the mode gate `&&` the fields check, the harness file goes in through the Write tool (the deny rules reach into Bash), «c3-prep-2» ($0, a FRESH process) precedes «c3», the volume is deleted in c3's §4 once the run record is complete; (l)3's «one chain id» = «chain-fold» ($0) AFTER c3, shape (b), the shipped number re-measured by the product's own functions; v22 09.09 (ruling (ff)): §6.1 the session MODE is a user-settings default, stamped by the harness and read by the paid runbook's first gate; v21 08.09 (ruling (ee)): §6.1 «harness-fields» ($0) precedes «c3-prep» — the executor's harness gets FIELDS (the launch line, effort, ultracode, two allow rules, hook timeouts in seconds, one start hook — PROCESS v2.4 «Harness fields»; the file to copy: `docs/reviews/2026-09-08-harness-fields/settings.json`); §8's effort ritual retired; v2.3's `--help` proof retired; v20 08.09 (ruling (dd)): §2 the SHIPPED number is measured on the product's pipeline end to end (hooks + P1 inside) by the product's own functions — `results/grade_promo_loop_readings.json`; the pre-registered readings stay the bar's record; §6.7 a filter the product applies that the grader did not see = a $0 reading by the product's own functions, never a widened record; v19 06.09 (21:45): §6.2 SHIP AS MEASURED; v18 06.09 (20:05): §6.2 holdout-2 READ RED on subject (0.7054) → dev-3; instrument P1 = the frozen reader + a deterministic post-processing layer (three conventions), measured at $0 on three dev sets; holdout-3 drawn from the remaining product population, ONE shot on `promo-holdout3` bought only if P1's dev-3 reading clears the bar (the operator's word); v17 06.09 (17:45): §6.1 a registration is never repeated on an anchored line (a re-registration = a new line), a runbook gate exits ≠ 0 before the step it guards, the hard-stop edge closes on the walk; holdout-2 cap $0.90 = the operator's word, quoted from the dry run; v16 06.09 (evening): §2 the holdout-2 gold is WRITTEN, blind — `docs/labels-promo-holdout2.jsonl`, 112 rows / 40 threads, sha `5525ddf1…`; the holdout-2 registration pins it; v15 06.09: §2 iteration 5 GREEN under law v1.2 (ruling (z)) — the frozen instrument for the holdout-2 shot is the four pins of `d598573`; §6.1 the cycle-3 ceiling is $10.00 (operator 06.09 15:55, anchor unchanged); v14 06.09: §6.1 the registration OPENS its line, so it runs in the PAID session minutes before the create (the team lead reads the dry run + HEAD before the purchase, the registration at acceptance); v13 05.09: §6.1 a step line's close settles against its POST-RUN reading (taken before any next pod); a line without one closes on the walk alone and never takes a late reading; §2 iteration 5 is the dev-40 read; v12 05.09: §6.5 a serving failure moves the serving, never the instrument, and surfaces at once; v11: §6.1 one paid run = one step line, the registration reads the guard with the step it names; v10: every leg prices on the slowest WHOLE run and issues on the mean when the dear corner refuses, a cap is quoted from the dry run; v9: §2 S2 holdout-40 read RED on subject → codebook v1.2, dev-2, holdout-2 (in-domain population), K8 v2; §4 «asked for once» + a re-used producer's record branches every decision field, §6.5 validity of a paid reading, §6.6 a test that reads the record, §6.1–6.2 a fence is an estimate and the frozen-set instrument is byte-for-byte

Team-lead file (process v3: launched by the standing prompt of §8, never `/plan-phase`). Mechanics named below are CONSTRAINTS; the goal is the question and the checks.

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
  `dev-2`, a reading, never a bar again. The line continues: codebook v1.2 (team lead) → law re-rendered → iteration 4 (INCOMPLETE, OOM — v12) → iteration 5
  on dev-40 (**GREEN 06.09, ruling (z): subject 0.8857 · signal 0.8667, complete 40/40; dev-2 read 0.8883/0.8296 beside it, no bar; the LAST of the 5 dev runs; the four pins of `d598573` are the frozen instrument**) → the ONE `holdout-2` shot.
  `holdout-2`: seed 42 over the frozen 678 price threads MINUS channels with `collect: false` in registry r2 (the
  product's population) MINUS the 80 already drawn, 20/20 by stratum, a NEW draw file — the old draw stays frozen. **v16: its gold is `docs/labels-promo-holdout2.jsonl` — 112 rows (47 currency + 65 decimal) over the 40 threads of `results/promo_threads_draw_2.json :: draw.*.holdout`, labelled BLIND by the team lead 06.09 under codebook v1.2 (no iteration-5 prediction file opened), self-checked by the team lead's validator (quotes as substrings, 40/40 threads covered, disjoint from dev-40/dev-2/holdout-40), sha256 `5525ddf1e16390dfec65934627e2bdf481ad4547966e537373e969dd431a9a48`; the executor commits it by path, the holdout-2 registration pins it; 36 rows carry `unsure` (honest ties, in the denominator).**
  K8 v2 for that line: `sku`/`brand` match on normalised exact OR token-Jaccard ≥ 0.5, `chain` folds as today, `post`
  exact — registered before iteration 4; the holdout-40 number stays under K8 v1.** **v20 (08.09, ruling (dd)): every reading above graded the RAW answer (`predicted_rows`), while the product screens each answer through the four hooks of S4 before P1 — so the SHIPPED number is the product's own: the same raw answers → `promo_hooks.screen` → `tick.p1_rows` → K8 v2, by the tick's own functions, in `results/grade_promo_loop_readings.json` (three sets; holdout-2 loop: subject 0.7411 / signal 0.7937 expected — the file decides), printed FIRST on the screen and in the README;
  the readings of (bb)/(cc) stay beside it as the bar's record, never rewritten. From this ruling on the graded instrument is the product's pipeline END TO END; a number measured upstream of a product filter is the model's, disclosed as such.**
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

1. Any pod/serverless create (paid): smoke first, project at measured rates; cycle 3 governs (ceiling **$10.00**, operator 06.09, ruling (z)
   addendum; $9.00 was (s) addendum 8; anchor unchanged) — the 30.08 estimate table and the cycle-2 remainder are history; never trim scope silently.
   **A fence for a LATER paid step is an estimate, never a cap (v7, ruling (q)):** it is re-priced at that step's registration on the
   instrument's OWN measured pace of the SLOWEST pod seen (hosts of one card ran 1.5–2.3× apart on identical outputs), the cap becoming
   the hard stop — holdout $1.10 (spent $0.2966), iteration 4 $1.20 (spent $0.6915, INCOMPLETE — v12), **iteration 5 $1.40 on a ≥ 32 GB
   card (operator 05.09 16:35)**, holdout-2 ≤ $0.90 on the measured pace — each with rung 0 FITS + the hard stop as its only money gate
   (ruling (r)). **v10 (ruling (t)):** on EVERY leg `rung_0` issues on the dear corner when it fits, else on the MEAN corner with the cap as
   the hard stop and the (r)2 table (no band gate); the mean is the WHOLE-RUN mean of the slowest pod seen (n = the run's units, never a
   smoke of three), written from the run record per pod; a cap named in a ruling is quoted from the `--dry-run` that priced it, never typed.
   **v11 (ruling (v)): one paid run = ONE step line** (`promo-iter<N>`, `promo-holdout2`, `promo-c3`), capped at the run's cap, closed by its run
   record; an open multi-run line carries no new run; the registration names its line and reads the guard WITH `--step` (FITS against that line's
   own remaining) — **and that reading OPENS the line (v14, ruling (y)): the registration runs in the PAID session, minutes before the create,
   never a session earlier** (an aged anchor drinks the volume's drip into the close's reference; the 5 % band shuts at ≈ 4 h); the team lead reads
   the dry run + HEAD before the purchase, the registration at acceptance. **v13 ((w) addendum): a line's close settles against its POST-RUN
   reading** — one more `--note` after its pod is deleted, before ANY next pod (the guard's RHS is the line's LAST open reading; a pre-pod one
   refuses for ever); the close waits at $0 for a COMPLETE walk over the run record's span (`--expect-ms`), retried at each session's start; a line
   whose readings all predate its pod closes on the walk alone, never takes a late reading. c3 after holdout-2; the volume `mp-srv2` goes after it. **v17 (ruling (aa), 06.09 evening): a registration is never repeated on an anchored line — a re-registration goes under a NEW line (`<line>-r2`, own ledger) or with `--cap` = the line's printed remaining, the operator's word; a runbook gate exits ≠ 0 and runs BEFORE the step it guards (the four-pin check before `--register`); at spent == cap the post-run `--note` refuses and the close settles on the walk alone (PROCESS «Money» v2.2). Holdout-2: cap $0.90 = the operator's word 06.09 17:45, quoted from the dry run's rung 0 — FITS $0.5170 on the mean corner, dear $2.8109, hard stop 4500 s.** **v21 (ruling (ee), 08.09): the paid session's launch line `claude --dangerously-skip-permissions` and the two allow rules (`pod create`, `pod delete`) are FIELDS of the harness and of the c3 runbook's §0 (PROCESS v2.4 «Harness fields»; the runbook's gate greps them and the create prefix, exit ≠ 0); «harness-fields» ($0) runs before «c3-prep»; a permission prompt or denial inside the paid session stays a stop, the team lead's. v22 (ruling (ff), 09.09): the MODE is the operator's user-settings default (bypass), not a flag; the harness stamps `permission_mode` into `.claude/session_mode` and the c3 runbook's §0 gate reads it FIRST (`grep -qx bypassPermissions`), before the pin check and the registration — «c3-prep» copies `docs/reviews/2026-09-09-harness-mode/settings.json` by path.** **v23 (ruling (gg), 09.09): the allow rules are retired («Allow rules have no effect in bypassPermissions» — inert once the first gate reads the mode), §0 = the mode gate FIRST `&&` PROCESS v2.6's fields check; a harness file goes in through the Write tool with `diff` as the proof (the deny rules reach into Bash file commands, every mode — a deny-listed path is never their operand); «c3-prep-2» ($0, a FRESH process — its first PROGRESS line records the header's mode and the live stamp; the issued file `docs/reviews/2026-09-09-harness-allow/settings.json`) precedes «c3»; the volume `qw4nwleanc` is deleted in c3's §4 after the listings, only once the run record is complete; (l)3's «one chain id» is «chain-fold» ($0) AFTER c3 — shape (b), the shipped number re-measured by the product's own functions, never on the executor's authority.** **v24 (ruling (hh), 09.09): c3's cap = min($0.80, REMAINING − $0.30) as the runbook's own command derives it from the guard's line — the operator's word 15:20, quoted from the dry run (FITS $0.1864 at the dear corner; at $0.50 the in-run pack gate — room = cap − billed − one wedged job $0.2843 − the tail, against one pack sized by time — ends the leg before its first page); the paid run launches DETACHED and is watched by short polls, the record read from its file; the close per PROCESS «Closing a line» (`--expect-ms`, `--until`, `--tolerance 0.05`); the volume goes AFTER the close, only on a complete run record; `register()` names what it reads; «c3-prep-3» ($0, a FRESH process) and a narrow second verifier pass precede «c3». Named for the retro: the pack priced by the rows left, the dry run running the in-run gates.**
2. The ONE holdout attempt: pre-register (readings + the two bars), tell the operator it is being
   spent. **The instrument on the frozen set is the one that took the dev bar, byte for byte** — every pin
   of the dev-bar registration unchanged; cosmetic law moves queue behind the attempt (v7, ruling (q)). **v18 (ruling (bb) + addendum, 06.09 20:05): holdout-2 READ RED on subject (0.7054; signal 0.8021 holds) — spent, now dev-3. The operator's word: instrument P1 = the frozen reader (the four pins of `d598573`, unchanged) + a deterministic post-processing layer `src/market_pulse/promo_post.py` with exactly three codebook conventions — R1 `post` ⇒ subject = thread root; R2 own channel: a `post` row with signals ⇒ `chain` = the owner; R3 a `sku`/`brand` row with `жалоба` on the store-stock lexicon ⇒ `chain` = the thread's retailer — measured at $0 on dev-40 (139) + dev-2 (188) + dev-3 (112) from the existing predictions (`results/grade_promo_p1_readings.json`, before/after per set). Holdout-3: seed 42 over draw-2's eligible 398 MINUS holdout-2's 40, 20/20 by stratum, `results/promo_threads_draw_3.json`, gold by the team lead BLIND, same bars 0.80/0.75, ONE shot on its own line `promo-holdout3`. DECISION TABLE of the holdout-3 stop-point: the shot is bought only if P1's dev-3 subject ≥ 0.80 AND dev-40 / dev-2 ≥ their bars; otherwise the fork returns to the operator at $0 (ship as measured · codebook v1.3). Fence ≤ $0.50 — an estimate re-priced at the registration on the measured 40.8653 s/thread (n = 40, the whole run of `p3krn2lwhhcyyi`); c3 after holdout-3, the volume after the phase's last paid run.** **v19 (ruling (cc) + addendum, 06.09 21:45): the $0 table read RETURN (dev-3 0.7500 < 0.80; dev-40 0.8857 =, dev-2 0.9043); the operator's word: SHIP AS MEASURED — S2 is CLOSED on the second reading, red on subject (0.7500 with P1 / raw 0.7054, 0.7181), green on signals (0.8021 / 0.7958); P1 ships in the loop; draw-3 frozen, unlabelled, a reserve; no holdout-3 shot; the numbers and the tie analysis on the screen and in the README from result files. Next: «p1-ship» ($0) → «c3-prep» → c3 (paid, `promo-c3`, ≤ $0.50) → the volume → e2e → the gate 12–13.09.**
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
   **v12 (ruling (w)): a SERVING failure (OOM, a crash, a dead process) is a transport defect of this class — the instrument
   (law, render, ceiling, dtype, decoding, parser) never moves for it; the serving environment does (a larger card in the
   volume's datacenter at the day's price, allocator settings), disclosed in the re-emission; the runner reports a failed unit
   as an ERROR reply and exits non-zero so the Mac never waits out a deadline; the re-buy takes the next number on its own line.**
6. **A test that pinned a literal of the record (v6, 04.09, ruling (o)):** when a ruling moves the registered record (a population,
   a leg, a pin) and a test's INVARIANT still passes while only literals of that record diverge, the executor rewrites the test to read
   the committed record — the claim stated in both directions — in the same commit and shows the diff: NOT a stop. Weakening an
   invariant, or a test whose claim fails on the record, remains the stop of §8 (j). A fixture never invents a unit the record lacks.
7. **The instrument ≠ the product (v20, 08.09, ruling (dd)):** a filter the product applies between the model and the screen (a hook, a post-processing layer, a dedup) that was NOT inside the graded instrument → the product's number is measured at $0 by the product's OWN functions over the same answers and shipped beside the reading; the reading is never rewritten, the record is never widened to make the product reproduce the instrument; the executor names the gap with its number in PROGRESS — NOT a stop. Widening a record's contract stays a stop.

## 7. Dependency the team lead owes

`docs/labels-positions-50.jsonl` (46 pages) is still owed — the S1 bar (d) waits for it, nothing else does; `docs/labels-promo-dev.jsonl`, `-dev2`, `-holdout2` have landed and are pinned.

## 8. DONE WHEN — the ONE `/goal` paste (v4, 03.09 — the PAUSE clause lost its resume tail, ruling 03.09 (c); v3 02.09; rulings file: `docs/reviews/2026-08-30-plan-promo-pulse-1.md`)

Process v3 (ruling 03.09 (e)): `/goal` is RETIRED for this phase — every session (start and after every STOP, always FRESH) is launched by
the operator's standing prompt — nothing typed before the paste: effort, `ultracode` and the launch line are fields of `.claude/settings.json` since v21 (PROCESS «Harness fields»). The block below is the phase's DONE
list: clauses (a)–(l) are the contract, kept as bytes — a clause moves only by a dated ruling of the team lead, never by the executor.

```
Phase promo-pulse-1 (docs/PHASE-promo-pulse-1.md) is COMPLETE per docs/plans/promo-pulse-1.md and every dated ruling in docs/reviews/2026-08-30-plan-promo-pulse-1.md. START RITUAL every session, before anything else: commit any modified team-lead file by path (docs/STATUS.md, docs/PROCESS.md, docs/PHASE-*.md, docs/reviews/*); read the plan and the NEWEST dated section of the rulings file; if docs/plans/promo-pulse-1.STOP.md exists, apply the newest ruling to it and delete it. Money: cycle-3 is OPEN — the ceiling and per-leg caps are those the NEWEST dated ruling in the rulings file names, four rungs per docs/PROCESS.md; a projection over the ceiling is a STOP. Demonstrate every check by running its command and showing the output in the conversation — the evaluator reads only the transcript. Met when ALL hold: (a) results/promo_pagecount_c2.json states the exact page count per channel for the census window from store/metadata only (or a <=10-line impossibility note with the priced alternative), and results/promo_projection_c2.json prices C2 as ONE number at the marginal rate against the re-read remainder; (b) scripts/collect_5c1.py::collectable honours collect: false, both directions tested; (c) positions for the census window exist in data/derived/pulse.db for every collected channel (vision for image carriers, text for the rest), bought inside the ceiling with the rungs logged and each paid leg's spend line named in the report; (d) results/positions_draw_50.json drawn twice with identical sha256 and, once docs/labels-positions-50.jsonl exists, scripts/grade_positions.py reports completeness >= 0.90 and promo-price accuracy >= 0.95; (e) once docs/labels-promo-dev.jsonl exists, scripts/grade_promo_signals.py on dev-40 reports subject >= 0.80 and signal >= 0.75 within at most 5 dev runs, and the ONE holdout attempt is pre-registered in a committed record, announced via a STOP notice, then spent once; (f) pytest tests/test_trends_sql.py green: trends recomputed twice identical, an empty week absent never zero; (g) make tick exists and a second run on an unchanged store writes zero new rows, counted per table including unsure; (h) on a clean clone, make tick && make promo-screen renders the screen from result files only, and a removed source yields a non-zero exit with a named error; (i) scripts/draw_truth_20.py renders 20 rows under seed 42 for the operator's gate; (j) make check is green with passed >= 4266 plus the new tests and no test file deleted — a test that must change to pass is a STOP; (k) docs/reports/promo-pulse-1.md exists, <=30 lines, opens with the phase's question and answers it in the first ten lines, every number naming its file; (l) git status --porcelain src tests scripts config results docs/plans docs/reports prints nothing. ALSO met, as a PAUSE, when docs/plans/promo-pulse-1.STOP.md exists (shown with cat) naming one of: waiting on the team lead's labels (dev-40 or positions-50), the dev-loop plateau (two iterations without gain), the holdout pre-registration notice, a rung firing or a projection over the ceiling, a design fork the plan does not settle, a sealed or frozen file that would move, a test that would have to be weakened. Or stop after 80 turns.
```
