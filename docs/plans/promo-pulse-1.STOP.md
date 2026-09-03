# STOP — promo-pulse-1, 2026-09-03 (the sixth; the fifth was answered by ruling 03.09 (b) and deleted)

**Stop-points, in order of size:** a design fork the plan does not settle · waiting on the team
lead's labels (positions-50) · one money figure that disagrees with the ruling that named it.
**Nothing was created and nothing was bought. No rung fired.** Both forks of ruling 03.09 (b) are
IMPLEMENTED and closed by their own checks, the codebook carries the ruled line, and K6's record is
page-level. What the ruling could not foresee is that S9's paid half has no instrument to run.

## Fork — S9 iteration 1 is AUTHORISED and there is nothing to authorise: the paid leg is unwritten

Ruling 03.09 (b) gives the decision table for iteration 1 «after the smoke». `scripts/promo_dev_pass.py`
has **no paid path at all** — `--help` offers `--render`, `--channel`, `--dry-run`, `--out` and
nothing else. There is no `--smoke` that reads the shortest/median/longest thread and writes
seconds/thread into `promo_dev40_prep.json`, no `--register` with the dev loop's own cap and ledger,
no `--run` over dev-40 with `extractor_version` per row, no K8 call on the result and no error
table. Every one of those is named by the ruling as an input to the decision, and each is new code
on the money path: a pod lifecycle, four rungs, a step ledger, a teardown proof.

Checked repo-wide, not just in that file: `promo_prompts` is imported by `promo_dev_pass.py` and by
two files that touch no endpoint, and `promo_dev_pass.py` is absent from every script that creates a
pod or calls one (`client_for` / `runpodctl` / `--endpoint`). **There is no paid runner for this
instrument anywhere.** The build is tractable — `scripts/read_threads_reader_v5b.py` and
`scripts/run_promo_c2.py` already carry the pod lifecycle, the rung ladder, the step ledger and the
teardown proof, and the dev pass would borrow them rather than invent them — which is exactly why it
is a design question and not a typing exercise: whose cap, whose ledger, which rungs, which stop-points.

**So the ruling authorises a RUN and what is missing is a BUILD**, and the plan's S9 does not carry
that instrument — building it and firing it in one unreviewed session is exactly the scope change
`CLAUDE.md` forbids («a threshold that is not in the plan is a scope change — stop and ask»).
What I need is one of: (1) a plan revision I write and you review before any pod exists, naming the
instrument's shape, its cap, its rungs and its stop-points; or (2) your ruling that the $0 half plus
the borrowed bound is enough to register iteration 1 directly, and the smoke is folded into the run.

**Option (1) is WRITTEN and waiting — `docs/plans/promo-pulse-1.md` §9 (rev 9, `d33c5a3`), $0, no
pod.** It names the new step `promo-dev-loop` and its own ledger, the cap `min($2.50, REMAINING −
$0.30)` = $2.50 today with the $2.00 floor, the four rungs, the four flags and which existing modules
each borrows (`run_promo_c2.py`'s registration and per-stage re-projection,
`read_threads_reader_v5b.py`'s never-two-pods / ssh dead-man / close-segment), the smoke's **n = 3**
and its shortest-median-longest rule, the 5-run ceiling, the plateau rule, and the checks. Your
decision table is quoted, not moved. **Nothing is implemented.** Rule on §9 or on option (2), and the
next session buys.
**The 16 posts without an evidence row ride that same pod and stay a named gap until it exists.**

**And there is no $0 route round it — checked, not assumed.** `src/market_pulse/local_llm.py` reads
«Local GPU inference: the same zero-shot evaluation, **on weights we rent**»; every consumer of it is
a `*_pod_runner.py`, and its torch / transformers / bitsandbytes imports live in the `gpu` extra
precisely so no test may import them. «Local» there means local to the RENTED card, not to this
machine. So (e) cannot be read at $0 by another instrument either: a predicted file needs a pod, a
pod needs a registration, and a registration needs §9 ruled.

## The money figure the ruling named is not the one the guard settles

The START RITUAL closed the step at the ruling's tolerance and it PASSED — but not at the ruling's
number. `--step promo-pulse-1 --step-cap 3.95 --close --tolerance 0.05` wrote
`results/spend_promo_pulse_1.json :: gpu_sessions[2]`: **`settled_usd` $2.986741**, checked against
`recorded_reading_usd` $3.0335 — a 1.54 % gap, inside 0.05. The decomposition is pods $0.052079 +
serverless $2.934662; the network volume's **$0.223611** is excluded by the closing walk's own rule
(«always on, beside the run and never inside it») and stays inside cycle 3, as the ruling directs.

The ruling says «the step's spend line is the guard's settled **$3.1909** (delta)». That figure is a
BALANCE DELTA read yesterday; today's delta is $3.220074 and the walk prices by billing lines.
**I did not type your number into the record** — the guard settled what it settled. Which figure is
the step's spend line of record for `docs/STATUS.md`: the settlement **$2.9867**, or the delta?
Cycle 3 today: **`CYCLE 3 SPENT $3.5117 of $7.00` · `REMAINING $3.4883`**, so the dev loop's
`min($2.50, $3.4883 − $0.30)` is the full **$2.50** and its $2.00 floor is clear.

## Fork 1 — CLOSED. The store is split and every sealed byte is back

The split point was found in the SEAL, never guessed: for each of the 38 sources
`results/window_summary_5c2.json` hashes, the k whose prefix sha256 IS the sealed digest.
**38/38 placed** — 23 at their full length, 15 shorter (529 lines), and 35 files the seal never
named moved whole (3 972 lines). Copy → verify → truncate, the backup (`data/derived_backup_2026-09-03`,
44 M) made before the first cut and its `ls -la` in the transcript. Closing check, all shown:

- **38/38 sealed sources hash to their sealed values**, re-read from disk after the truncation.
- `w1` re-derives **902/902** numeric leaves of the sealed summary, 0 disagreed, 0 missing.
- `results/dashboard_data_w1.json` re-exported: **55 differing leaves → 5**, all 4 474 data leaves
  identical and **0 under `provenance.evidence`**. The five are moved-file pins: four are the
  existing `MOVED_BY_*` groups; the fifth, `scripts/build_aggregates.py`, is CLAIMED through the
  same machinery — `MOVED_BY_THE_SECOND_WINDOW` at `58ff037`, witness `WINDOW_ID_C2` — and never
  re-pinned, as `CLAUDE.md` requires.
- `w2` from the new root: **17 channels · 3 397 markers · 1 113 positions**, unchanged.
- **The 19 fork-1 reds are green with no assertion of theirs changed.**

Named: `data/derived_w2/` is the live root (the ruling delegates the name); `pulse.db` stays at
`data/derived/pulse.db` — both windows build into the one DB and the seal hashes FILES, none of
which is the database. `build_aggregates.build` pools both roots and partitions by each window's
pinned population ids, so the 20 D-cut posts stay in w1's root and w2 reads them there.

## Fork 2 — CLOSED, and the ruling's conditional check FIRED

`test_positions_is_untouched` is re-scoped, not deleted (Dv `[cause: ruling]`): the shipped w1
export's 145 `row_id`s are all `channel:msg_id:ordinal` carrying no carrier, the key is
`(window_id, row_id, carrier)`, and one message read by both legs now stores two rows instead of one
replacing the other — driven, not described. The $0 reading you owed: **7 row_ids stored under BOTH
carriers**, **6 messages** with position rows from both, and **exactly 1** (brand, product, volume)
triple read by both legs — `@forainfo:6056`. **w1 has 0.** 1 > 0, so S3's trends dedupe — named in
the plan by revision 8 and driven three ways.

**And a third question for you: your key over-reaches, and I narrowed it rather than widen a
denominator quietly.** Taking ONE row per (window, channel, msg_id, brand, product, volume) — the key
as written, no carrier in it — drops **39** rows over **35** groups in today's store. Only **1**
group spans carriers. The other 34 are two readings of ONE SKU by ONE leg, **24** of them holding
more than one distinct promo price (`@atb_market_official:4359` prints Активіа Біфідойогурт 260 г at
**23.9 AND 24.7**), and **2** sit inside the w1 window whose seal this session spent its first half
restoring. Those are two promos, not one promo counted twice — and «prefer `leaflet_page`» cannot be
applied to a group with a single carrier at all, so it would fall through to an arbitrary `row_id`.
So the CTE keeps the preferred LEG whole instead of one row: measured effect **1 group · 1 row
dropped · 0 in w1** (`@forainfo:6056:0`, the very collision fork 2's key made storable), and
`results/promo_screen_data.json` moves in exactly one leaf — `@forainfo` · Ласунка · 2026-W35
`priced_positions` 4.0 → 3.0. **If you mean the literal key, say so and I widen it in one commit.**

## The codebook, and K6's record

`promo_prompts.CODEBOOK` rule 6 carries your line verbatim; `codebook_version()`
`a97d3c71b8cf9b14…` → **`a694d005972d3a66…`**, and the rendered rule 6 is in the transcript. The
gold re-driven through all four hooks after the edit: **140 about · 84 signal · 0 failures**,
140/140 comments with text covered, 0 rows on a wordless comment. `results/promo_dev40_prep.json`
re-emitted so its pinned sha is the live one — 40 renders, 214 817 chars, longest 8 170.

K6 is page-level as ruled: **46 pages**, `results/positions_50_predicted.jsonl` re-emitted as
**205** extracted rows of those pages (both carriers), sha `781b02b473ed8104…`. Each drawn row and
each page gained `image` — **45 of 46 resolve**; `@silposilpo:3822` is a `post_text` carrier and its
link is the whole of it. **The draw did not move**: the 50 `row_id`s are identical to the committed
record's and the rows without `image` are byte-identical to it, so `rows_sha256_as_drawn`
**`fe3f5841175a3953…`** is unchanged and is the anchor the labels are owed against; the FILE's own
sha necessarily moved from `61b4fda7…` and the record says so in `anchor_note`. Drawn twice:
`f221fa520ceba8e6…` and `781b02b473ed8104…` both times. **`docs/labels-positions-50.jsonl` is owed
against `fe3f5841…` — 46 pages, every in-scope position, one line each.**

## A defect of mine, found and repaired inside the session

`tests/test_run_promo_c2.py::stage()` patched `run_loop.DERIVED_ROOT` only, so when the driver
started writing to `LIVE_DERIVED_ROOT` the stub run appended **13 rows** into the REAL
`data/derived_w2/` (`@atb_aktsiyi`, msg_ids 101/102/103/7, all stamped 12:50:37). The live root was
rebuilt from the backup by re-running the split — **3008/1093/15/385**, byte for byte — and the w1
seal never moved (38/38 throughout). The fixture now checks that EVERY derived root is under
`tmp_path`, derived from `dir(run_loop)` rather than a list of two names; it refused `STORE_ROOT` by
name when first written too wide, which is its negative control.

## What is DONE and shown in the transcript

(a) 17 channels · 3 008 pages exact; `c2_priced_usd` $3.1563. (b) `collect: false` honoured, both
directions. (c) w2 positions per channel, 17 channels summing to **1 113**; five channels read 0 and
that is an ANSWER, not a gap — `@epicentrk_sale`, `@fozzyshopua`, `@kop1chat`, `@kopiyochka1`,
`@rrozetka` are DIY, coupon-aggregator and electronics channels and the dairy/ice-cream parser found
nothing to write. (d) the draw twice, one sha, labels owed. (e) **the $0 half only, and the other half is
UNREACHABLE at $0 — demonstrated, not asserted.** `scripts/grade_promo_signals.py` requires
`--predicted`, the model's dev-40 output; the only `promo_dev*` file in `results/` is
`promo_dev40_prep.json`, the $0 corpus record. The grader refuses by name: «results/promo_dev40_predicted.jsonl
is missing — the grader may not score against nothing». `docs/labels-promo-dev.jsonl` exists, so (e)'s
condition IS triggered and its bars cannot be read until a paid pass writes a predicted file — which
is the fork at the top of this document, in one command. (f) `tests/test_trends_sql.py`
**14 passed** (10 + the dedupe's four). (g) `make tick` twice, zero new rows in all six tables. (h)
clean clone `make tick && make promo-screen` exit 0 from `results/promo_screen_data.json` alone, and
that source removed → exit 2, «promo-screen REFUSED: missing source …». (i) `draw_truth_20.py`
20 rows, seed 42. (l) porcelain clean on the contract paths. (j) **`make check` GREEN at `bbc7483` — `4297 passed, 2 skipped in 735.60s`, exit 0, zero failed and zero errors.** Both halves of (j) hold: 4 297 ≥ 4 266, and green. The 20 reds of the last report are gone — 19 with no assertion of theirs touched.
