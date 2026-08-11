# sku-b-v3-run — the resumed session, refused at the go/no-go

> One resumed session under `results/sku_pilot_prereg_v3.json`, cap $0.45, buying the 121 unbought
> elements. It bought none of them: the (10)(a) go/no-go refused before the first gold call.

## Read-back

**The eight gates.**
1. **$0 gates** — `make check` green, the preflight in the peft venv exit 0, the balance re-read
   against `results/spend_phase4.json`, all three listings empty, the driver's `--resume --dry-run`
   showing 91+30 in 6+1 jobs, and the anchor written BEFORE anything bills.
2. **Stage the volume before any endpoint exists** — `repo/` on `qw4nwleanc` to HEAD by git bundle,
   content-checked, and `worker-boot.log` read off the same pod for the 391 s boot's diagnosis; pod
   deleted and proven by listing.
3. **A NEW template**, three variables and no fourth, never a reused or edited one.
4. **The endpoint** — `ADA_24`, one worker, 60 s idle, 900 s execution, every flag read back from
   the API's own answer.
5. **The run, one invocation**, launched detached and watched by PID: identity stop → the two
   registered warm-ups → go/no-go → page leg → text leg.
6. **Outcomes** — a go/no-go refusal, a (10)(b) mid-leg stop, or completion; the first two are
   teardown-report-STOP with the ruling left to the team lead.
7. **Teardown, proven** by listings with a positive control at both ends; the volume stays.
8. **Commits** — team-lead docs first, then the run's artifacts by path, then the vault tail alone.

**The two (10) stop semantics.**
**(10)(a)** — the go/no-go fires ONCE, after the two warm-up calls and before the first gold call;
it is the only stop that leaves nothing half-bought, and it consumes **no attempt**.
**(10)(b)** — the in-run projection gate fires between jobs, after gold has been bought; the money
is spent, the population is half-bought, and it is a team-lead ruling, never a silent continuation.

**Each element is bought exactly once across the program — nothing is re-asked.** The 17 the first
session paid for, the parse refusal included, enter the bars as they stand; this session was
authorised to buy the other 121 and bought none of them, so the count is unchanged at 17 of 138.

---

## The outcome: refused, with the attempt intact

```
  warm-up positions_post_gm4   stop  14.808s  ```json
[
  {
    "brand": "De Luxe Foods&Goods Se
  warm-up positions_text_gm4   stop  3.862s  [{"brand": "Молокія", "line": "Екстра", "category"
  go/no-go      121 gold calls project $0.5964 against $0.4500 left of the cap — REFUSE
REFUSED before the first gold call: the run projects $0.5964 against $0.4500 left of the $0.45 cap
(SPEC 3.17 (10)(a)). No gold call was made and NO attempt was consumed —
results/sku_b_positions_v3.json is the record. Stop and report; the pilot needs a re-registration
under the measured price, not a raised cap.
```

`results/sku_b_positions_v3.json` carries `stopped_before_gold: true`, `population.asked: 0` and
121 ids under `population.unbought`. **`results/sku_b_positions_v3.jsonl` does not exist** — a stop
before gold leaves no gold artifact on disk:

```
$ ls -la results/sku_b_positions_v3.jsonl
ls: results/sku_b_positions_v3.jsonl: No such file or directory
```

**What refused the run is the amendment written to make the refusal possible.** (11)(c) replaced
the first session's synthetic 64×64 warm-up image with a real unsent leaflet page, because the
synthetic one priced a page at 1.436 s against the 5.0772 s/call the run then measured — a gate
that passes the run it exists to refuse. The representative page priced at **14.808 s**, and the
gate refused. It did exactly what it was registered to do.

---

## Gate 1 — the $0 gates

```
$ make check
1802 passed, 2 skipped in 52.62s

$ PYTHONPATH=src <peftvenv>/bin/python scripts/preflight_serving_guards.py
EXIT=0    PASS 24    FAIL 0
local   transformers 5.14.1 · peft 0.20.0 · torch 2.13.0
volume  transformers 5.14.1 · peft 0.20.0
```

The scratch venv of Dv160 survived this time; no rebuild was needed. The four resume refusals and
their controls are in the preflight's own output:

```
PASS  the honest registration is accepted and names 121 elements to buy
PASS  the resume refuses a moved dump pin
PASS  the resume refuses a moved serving pin
PASS  the resume refuses an unbought id with an answer
PASS  a bought id that reaches the selection is refused
PASS  the control: an unbought id passes the same selection
PASS  the registered warm-up inputs are real, full-size and accepted
PASS  the warm-up refuses a page inside the sent 108
PASS  the warm-up refuses a row inside the 30
PASS  a source answered by both sessions is refused in the merge
PASS  the control: the merged record carries 17 + what this session bought
```

The account, before anything of this session existed:

```
pods            []
serverless      []
network-volume  qw4nwleanc mp-srv2 EU-RO-1 100
templates       unfcr3ja0t | market-pulse-5b-a      ← captured BEFORE gate 3, so the teardown
                0g6zg73ptq | mp-5b-diag               control is proven at both ends

phase-4 anchor $35.0000 · balance now $12.2025 · phase-4 spent $22.7975 of $25.00 · $2.2025 left
```

The dry-run:

```
$ PYTHONPATH=src python3 scripts/positions_gm4_skub.py --resume --dry-run
page leg   91 pages sent (of 159 available, 19 posts) in 6 job(s), largest 7.99 MB
text leg   30 rows in 1 job(s)
resume     SPEC 3.17 (11) under results/sku_pilot_prereg_v3.json
  bought    17 of 138 by results/sku_b_positions.json, never re-asked
  to buy    91 page(s) + 30 row(s) = 121 of 121 registered
  cap       $0.45 (11)(d) · anchor results/spend_sku_b_v3.json
```

**The anchor, written before the first billing resource existed** (the Dv149 protocol), through the
driver's own `read_ledger` and committed in `6811c74`:

```json
{ "runpod_balance_at_sku-b-v3_start": 12.2025374089, "cap_usd": 0.45, "runs": [] }
```

One thing that anchor makes visible: **sku-b's own tail settled after its record was written.** The
first session recorded $0.1965 at teardown and its anchor now reads a $0.2160 delta — $0.1965 plus
the $0.0184 idle tail is $0.2149, and the remaining $0.0011 is the last of it. A balance delta is a
floor in both directions.

---

## Gate 2 — the volume, staged before any endpoint existed

Staging pod `1xr3yu4dp2rqn2`, RTX 2000 Ada at **$0.24/h**, EU-RO-1, volume attached,
`--terminate-after` two hours out. The content check has a negative control because the volume was
read before the re-stage as well as after:

| | before | after |
|---|---|---|
| `git rev-parse HEAD` | `49665c7d0397…` (the sku-b-run era) | `6811c74e0b9b…` |
| `scripts/sku_bar_verdicts.py` | *No such file or directory* | present, 18359 bytes |
| `grep -c 'def leaflet_brand_recall' src/market_pulse/scorer.py` | **0** | **1** |

The staging itself — the bundle names its real ref and the reset targets an explicit sha, so a
fetch that moved nothing would have failed loudly instead of printing `Already up to date.`:

```
=== bundle heads (the REAL ref, not FETCH_HEAD) ===
6811c74e0b9bf58210de87d948a8cd30f0bbd5f4 HEAD
=== fetch ===
From /workspace/mp-skub-v3.bundle
 * branch            HEAD       -> FETCH_HEAD
=== reset --hard to the Macs exact sha ===
HEAD is now at 6811c74 chore(sku-b-v3-run): anchor the ledger before anything bills
=== proof ===
6811c74e0b9bf58210de87d948a8cd30f0bbd5f4
(end of git status)
```

`start.sh` verified, not edited, and the prompt shas rendered on the volume itself:

```
5b3bcbb2f59372f4cb3ee940caad5b5b4b90bb22adeff1f783f8c8301474b46c  /workspace/start.sh
5b3bcbb2f59372f4cb3ee940caad5b5b4b90bb22adeff1f783f8c8301474b46c  scripts/start_5b_worker.sh

positions_post_gm4 ca6303c157d46e707aaf3fc52c7a05ed1450e24c26db0e7c93eefba4f6968754
positions_text_gm4 7250b87aa1c2de407e06ab9eed565dd4d88025add7be0d2d2a87607c0d872860
```

Both equal `results/sku_pilot_serving.json :: expected_worker`. Pod deleted, `pod list -a` → `[]`.

### The boot-log diagnosis: where the 391 s went

`worker-boot.log` was copied off the volume **before** gate 3, because the template's
`dockerStartCmd` redirects with `>` and the next boot truncates it. 22,111 bytes, 287 lines, written
by the sku-b-run worker at 18:14. It has **no timestamps**, so what it can date is what it prints
its own durations for; the rest is bounded by subtraction.

```
runpod SDK 1.11.0
--- Starting Serverless Worker |  Version 1.11.0 ---
{"message": "Running 7 fitness check(s)...", "level": "INFO"}
{"message": "GPU binary test passed: 1 GPU(s) healthy (CUDA 13.0)", "level": "INFO"}
{"message": "Memory check passed: 149.28GB available (of 187.82GB total)", "level": "INFO"}
{"message": "Disk space check passed: 29.98GB free (99.9% available)", "level": "INFO"}
{"message": "Network connectivity passed: Connected to 8.8.8.8 (25ms)", "level": "INFO"}
{"message": "CUDA version check passed: 12.8 (minimum: 11.8)", "level": "INFO"}
{"message": "CUDA initialization passed: 1 device(s) initialized successfully", "level": "INFO"}
{"message": "GPU compute benchmark passed: Matrix multiply completed in 48ms", "level": "INFO"}
{"message": "All fitness checks passed. (11758.52ms)", "level": "INFO"}
{"message": "Jobs in queue: 1", "level": "INFO"}
{"requestId": "sync-370ddfbc-…-e2", "message": "Started.", "level": "INFO"}

Loading weights:   0%|          | 0/1188 [00:00<?, ?it/s]
…
Loading weights: 100%|██████████| 1188/1188 [01:52<00:00, 10.55it/s]
{"requestId": "sync-370ddfbc-…-e2", "message": "Finished.", "level": "INFO"}
```

| phase | seconds | share of 391.369 | how it is known |
|---|---:|---:|---|
| SDK fitness checks (7 of them) | **11.76** | 3.0% | the log states it: `11758.52ms` |
| weight load, 1188 shards | **112.0** | 28.6% | the tqdm bar's own elapsed, `[01:52]` |
| everything else | **267.6** | 68.4% | 391.369 − the two above |

Three readings, in decreasing confidence:

1. **The weight load is a network-volume read, and it shows.** The first 822 shards load at
   **7.61/s over 108 s**; the last 366 load **in 4 s, at 91.5/s** — a 12× step, and the fastest
   single step in the bar is 28 shards in one second. That is the signature of a cold read followed
   by cache hits, not of a CPU-bound loader. The weights live on `qw4nwleanc` under
   `HF_HOME=/runpod-volume/hf`.
2. **The 267.6 s the log does not name is bounded, not identified.** `start.sh` is four `export`
   lines and an `exec`, so the log begins the moment the python process prints the SDK banner —
   everything before that (container start, the volume mount, and python's import of torch,
   transformers and runpod) produces no line here, and neither does the model's own construction
   between the fitness checks and the first shard. It is one of those, and this log cannot say
   which. Naming a split from line ordering would be an invention.
3. **The number reproduces.** This session's boot, on a different worker (`8hdfifshaj73fa` against
   the first session's `gtszhrcxvcvh5z`), measured **402.586 s** — 2.9% above 391.369. The ~390–400 s
   regime is a property of this configuration, not an unlucky draw, and the 175.8 s pod figure and
   vis-c's 183.58 s serverless figure belong to a different one.

Cheapest thing that would move it: the shard-count. 1188 shards at 7.6/s cold is 108 s of the boot
before anything else; a consolidated `safetensors` layout on the volume is the lever, and it is a
5c-era decision, not this contract's.

---

## Gates 3 and 4 — the template and the endpoint

Template `n53w9uilj8`, created new, exactly three variables and no fourth:

```json
"env": { "BASE_WEIGHTS": "google/gemma-4-31b-it",
         "MODEL_REVISION": "842da3794eaa0b77d5f08bae87a17459d91ff475",
         "SERVING_CONFIG": "POSITIONS" },
"dockerStartCmd": ["bash","-c","exec bash /runpod-volume/start.sh > /runpod-volume/worker-boot.log 2>&1"],
"isServerless": true
```

Endpoint `fq2z68hnraf055`, every flag read back from the API's own answer:

```json
"executionTimeoutMs": 900000, "idleTimeout": 60, "workersMax": 1, "gpuIds": "ADA_24",
"networkVolumeId": "qw4nwleanc", "locations": "EU-RO-1", "flashBootType": "FLASHBOOT",
"templateId": "n53w9uilj8", "scalerType": "QUEUE_DELAY"
```

`executionTimeoutMs: 900000` equals the driver's `JOB_TIMEOUT_S` — (10)(c) holds at the endpoint as
well as in the client.

**Before the endpoint was created, the headroom was checked against the projection**, because there
is room for exactly one boot: $0.45 − $0.3300 (the worst corner of `results/sku_projection_v3.json`)
is $0.1200, and a second boot costs $0.1199. Billed at that moment: the staging pod only, priced by
its measured seconds rather than by the balance — rented 20:33:31 UTC, deleted before 20:37, so at
most 3.5 min at $0.24/h = **at most $0.0140**. Headroom $0.1060. The balance itself still read
$12.2025, unmoved: it lags, which is why the pod's own clock is the number used here.

---

## Gate 5 — the run, and the stop

One invocation, launched detached (`nohup` + PID watch, pre-authorised by the contract) and watched
by process, never by `tail -f`:

```
--- tick 1 · 22:38:31 · pid=20440 · log 8 lines
--- tick 2 · 22:39:27 · pid=20440 · log 8 lines
…
--- tick 7 · 22:44:03 · pid=20440 · log 8 lines
--- tick 8 · 22:44:58 · pid=GONE · log 19 lines
PROCESS EXITED
```

The driver's console, verbatim and in the order the contract fixes:

```
ledger: spent $0.0000 of $0.45 (balance $12.20)
endpoint       fq2z68hnraf055 · POSITIONS/base-no-adapter
  revision      842da3794eaa0b77d5f08bae87a17459d91ff475
  ceiling       800 new tokens, greedy, batch 1
  prompts       positions_post_gm4 ca6303c157d4… · positions_text_gm4 7250b87aa1c2…
  warm-up positions_post_gm4   stop  14.808s  ```json
[
  {
    "brand": "De Luxe Foods&Goods Se
  warm-up positions_text_gm4   stop  3.862s  [{"brand": "Молокія", "line": "Екстра", "category"
  go/no-go      121 gold calls project $0.5964 against $0.4500 left of the cap — REFUSE
```

The identity stop passed (the endpoint reported the pinned config and both prompt shas), the two
**registered** warm-up inputs were used and re-verified against their bytes, and the go/no-go ran
once, before any gold call.

### The go/no-go arithmetic, by hand

Every input is in `results/sku_b_positions_v3.json :: projection`; the rate is
`results/srv2d_cost.json :: rate.usd_per_second` = $0.00030669/s.

```
billed at the gate      421.256 s   (boot 402.586 + warm-ups 18.670)
gold_seconds            91 × 14.808 + 30 × 3.862 = 1347.528 + 115.860 = 1463.388 s
idle tail                60.000 s
                       ──────────
total                  1944.644 s × $0.00030669 = $0.5964
budget                                             $0.4500   →  REFUSE
```

Two numbers the team lead will want beside it:

```
break-even page marginal:  9.5622 s/page   (the cap is exactly exhausted there)
at the first session's measured 5.0772 s/page:
  421.256 + (91 × 5.0772 + 30 × 3.862) + 60 = 1059.141 s → $0.3248   — it would have proceeded
```

---

## What the probe measured, and the question it hands back

The refusal turns on one quantity: **seconds per leaflet page.** Three measurements of the same
frozen instrument now exist, and they disagree by an order of magnitude:

| probe | s/page | n | what it was |
|---|---:|---:|---|
| sku-b-run warm-up | 1.436 | 1 | a generated 64×64 image; the answer was `[]` |
| sku-b-run gold leg | **5.0772** | 17 | real pages, one job, average — and **10 of the 17 answered `[]`**, 14 positions in total, 1 parse refusal |
| sku-b-v3-run warm-up | **14.808** | 1 | a real unsent page (`atb_market_official_4476.jpg`, 0.32 MB); the answer is a multi-field JSON list, `finish_reason: stop` |

What can be said from the artifacts, and no more:

- **The 17 are not a shallow slice.** They are pages 1–6 of three posts; the remaining 91 are
  pages 1–6 of the other sixteen. Page depth does not separate the two samples.
- **The first session's marginal is dominated by pages with nothing to say.** 10 of 17 returned an
  empty list, and a page that answers `[]` decodes in a fraction of the time a page listing several
  positions does. 5.0772 s/call is an honest average of that mix.
- **The warm-up page had a great deal to say.** Its stored reply is truncated at 200 characters by
  the record writer, so its full length is not recoverable, but it completed normally and the text
  call beside it — 153 characters, one position, no image — took 3.862 s.
- **n = 1 against n = 17.** A single page is a high-variance estimator of a population mean, and
  (11)(c) deliberately bought exactly one.

So the go/no-go is not obviously wrong and not obviously right: it priced the run from a page that
may be denser than the population's mean, and the alternative estimate comes from a sample that may
be emptier than it. **Nothing was re-run to get a second draw** — the contract forbids it and so
does the amendment. Which marginal the next registration is priced from is the team lead's ruling.

---

## Gate 6 — the outcome, and what it costs to answer the same question again

Outcome (a) of the contract: **go/no-go refusal → teardown, report, STOP; the attempt is intact.**

Priced from this session's own measurements, a session that buys the 121 at 14.808 s/page needs
$0.5964; at 5.0772 s/page it needs $0.3248. A cap that covers the worse of the two with the
first-session boot regime is **$0.60**, and $0.65 would carry a boot at the 402.6 s measured today
plus the observed 3% boot variance. That is arithmetic, not a proposal: the re-registration is the
team lead's, and (11) authorised one session at $0.45.

### And a number that cap has to be set with open eyes about

**Re-running `--resume` today would refuse again, at a budget of $0.2974 — even at the optimistic
marginal.** Three constants compose into it, and none of them is a flag:

```
RESUME_CAP_USD  = 0.45                            # hardcoded; --project-stop-usd only TIGHTENS (F5)
RESUME_LEDGER   = results/spend_sku_b_v3.json     # hardcoded, and read_ledger returns the EXISTING
RESUME_PHASE    = "sku-b-v3"                      #   file when its key is there

anchor $12.2025 − balance $12.0499 = spent_before $0.1526
budget = cap − spent_before = 0.45 − 0.1526 = $0.2974   <   $0.3248, the optimistic projection
```

So this session's refused spend — a boot and two warm-up calls that bought nothing — is charged
against the anchor the next attempt would run under, and the cap would have to rise by that much
just to stand still. **Whether a refused (10)(a) session's spend counts against the next one is a
team-lead ruling**; that the driver currently makes it count *silently*, with no flag to say
otherwise, is the finding (Dv167). A v4 needs its own `RESUME_*` constants — cap, ledger path and
phase key together — not a raised number in one of them.

---

## Gate 7 — teardown, proven with the positive control

```
serverless delete fq2z68hnraf055   → {"deleted": true}
template delete n53w9uilj8         → {"deleted": true}

template list --type user:
  unfcr3ja0t | market-pulse-5b-a      ← the positive control: the two 5b-era siblings SHOW,
  0g6zg73ptq | mp-5b-diag               so the listing is not empty by accident
  mine present? False

serverless list  → []
pod list -a      → []
network-volume   → qw4nwleanc mp-srv2 EU-RO-1 100   (the volume STAYS)
```

The same two template ids were captured **before** gate 3 created mine, so the control holds at both
ends.

---

## The three cost readings, kept distinct

| reading | value | what it is |
|---|---:|---|
| balance delta at the refusal | **$0.1416** | a FLOOR (Dv33). Re-read immediately after teardown: **the same number**, so nothing had settled yet |
| billed seconds × rate | **$0.1476** | 421.256 worker s + 60 s tail at $0.00030669/s — the reading that does not wait for the account |
| \+ the staging pod | **≈ $0.1556** | ≤ 3.5 min at $0.24/h ≤ $0.0140 on top, priced by the pod's own clock |
| balance delta, ~20 min later | **$0.1526** | the same floor once it settled — $0.0110 above the first read, and within $0.0030 of the bound above. The two instruments agree |
| the cap | $0.45 | **$0.2974 left**, and the attempt not consumed |

`results/spend_sku_b_v3.json :: runs` now carries the entry; that it did not is Dv161 below. Its
`step_spent_usd` is the $0.1416 read at teardown, which is why the settled $0.1526 is stated here
rather than written over it — a ledger entry is what a read returned at the time it ran.

---

## The bar producer, built before the endpoint existed

Step 6 asks for bar-1 and bar-3 verdict records "THROUGH the registered readings (R1–R5) over the
MERGED population". **No such producer existed** — `scripts/gate_bars.py` is Phase 4's Tier-1 table
and knows nothing about sku-b — so it was written and tested first, at $0, and driven end to end by
`--resume --smoke`'s merged pair. Discovering a registered bar has no producer on the far side of a
paid run means the answers sit unscored while the instrument gets written.

`market_pulse.scorer` gains the two metrics, because it is the single judge: `leaflet_brand_recall`
(macro mean of per-post recall; micro and precision reported beside it and gating nothing; an empty
gold set REFUSED, not skipped) and `text_tier_accuracy`. Both carry hand-computed tests — the
reflective test in `tests/test_scorer.py` demands one per public function.

`scripts/sku_bar_verdicts.py` refuses before it computes: a moved gold, manifest, prereg or dump
sha; a ladder that drifted from the registration; a population still carrying unbought elements; a
population whose sources do not land exactly once; a smoke record aimed at the paid verdict path;
and a record that stopped before gold. Bar 2 gets its denominator, its R4 reachability class and its
dump — never a value, because SPEC §10 says the executor does not score its own sample.

**The one thing no fixture could check on paper is the key space, and it is a trap.** The gold
renders the reviewer's brands through `build_sku_reference_leaflet.gold_key`, whose alias table is
keyed on **display names** — so a watchlist id like `rud` does not resolve and lands as `raw:rud`.
26 of the 27 distinct gold keys carry that prefix; only `president` resolves, because `President` is
its own display name. A prediction normalised the obvious way (`scorer.normalise_brand` → the
`brand_id`) would have compared `rud` against `raw:rud` and scored **0.0 recall on every watchlist
brand in the pilot**. The producer therefore renders the prediction through the SAME `gold_key`, on
`brand_id or brand_raw`: one function, both halves. The test pins both routes with a control — a
resolved watchlist brand («Рудь» → `rud` → `raw:rud`) and an off-watchlist one («Каштан» →
unresolved → `raw:каштан`) inside one post, both found.

Driven against the completed *smoke* population — meaningless numbers, real plumbing:

```
$ PYTHONPATH=src python3 scripts/sku_bar_verdicts.py --record results/smoke/sku_b_positions_v3.json
results/smoke/sku_b_positions_v3.json — 138 elements, unbought 0
  leaflet_brand_recall       0.1633 vs 0.75   FAIL
  price_pair_accuracy             — vs 0.80   PENDING_TEAM_LEAD
  text_tier_accuracy         0.4615 vs 0.85   NOT_SCORED
  bar 1 over 15 posts · micro 0.1818 · precision 0.5263157895
  bar 3 over 26 of 30 rows · 4 unreadable (13.3%)
  bar 2 n = 72 pairs, the team lead's read
wrote results/smoke/sku_bar_verdicts.json
```

And against the real record of this session, which is the positive control that matters:

```
$ PYTHONPATH=src python3 scripts/sku_bar_verdicts.py
refused: results/sku_b_positions_v3.json stopped before the first gold call — it has no dump and
no answers. There is nothing to score: the bars need the COMPLETED population of (11)
```

Bar 3's gold is complete and waiting: 30 rows, `{'position': 11, 'product_mention': 3,
'brand_mention': 0, 'none': 16}`, ladder `6a257e04375b4579…` matching the manifest.

---

## Verify

```
$ make check
1804 passed, 2 skipped in 53.31s

$ ruff format --check .
228 files already formatted
```

**The per-commit checkout table.** The vault tail was stashed first (`git stash push -- knowledge/`),
each commit was checked out for real, and the parent `6888de7` is the control for the checker's own
bias. `HEAD` is printed from the checkout, never assumed, and stderr is not swallowed.

| commit | HEAD printed | content fact | its own suite |
|---|---|---|---|
| `6888de7` (parent, control) | `6888de7` | `results/sku_pilot_prereg_v3.json` present | **1780 passed**, 2 skipped |
| `84a7d22` team-lead docs | `84a7d22` | `sku-b-v3-run` ×3 in the contract; `v3-prep ✅ ПРИНЯТ` ×1 in STATUS | **1780 passed**, 2 skipped |
| `20e2f8c` bar producer | `20e2f8c` | `def leaflet_brand_recall` ×1; `sku_bar_verdicts.py` 18359 bytes | **1802 passed**, 2 skipped |
| `6811c74` the anchor | `6811c74` | `anchor 12.2025374089` | **1802 passed**, 2 skipped |
| `53f33b6` the two fixes | `53f33b6` | `def log_run` ×1; the stopped-before-gold refusal ×1 | **1804 passed**, 2 skipped |
| `5dd9e1a` the run's artifacts | `5dd9e1a` | `stopped_before_gold True · projected 0.5964` | **1804 passed**, 2 skipped |
| restored | `5dd9e1a` on `main` | stash popped, three vault files back | — |

The suite grows exactly where a commit adds tests, and the parent's 1780 is the baseline that says
the growth is this phase's.

---

## Deviations

**Dv161 — a (10)(a) refusal never reached the ledger, and this session is where it showed.**
`main` had two exits that write money and only one of them appended to the anchor's `runs`: the
completed run did, the go/no-go refusal did not. So a session that billed a boot and two warm-up
calls and then refused left `results/spend_sku_b_v3.json` saying `runs: []` — and that file is what
the next session reads to see what is left of the cap. Fixed on touch: one `log_run`, called from
both exits, with notes that say which exit wrote them; the test drives the refusal through a
ledgered `main` and its control is the completed path. **This session's own entry was appended by
hand through that same function**, with the post-teardown balance and all three cost readings in
its note — the driver had already exited by the time the gap was found.

**Dv162 — the bar producer crashed on the record it is most likely to be pointed at.** A refusal
writes `dump.path: None`, and `REPO_ROOT / None` is a `TypeError` that says nothing. It refuses by
name now. Found by running the producer against the real record rather than only against fixtures.

**Dv163 — the refusal record's `cost` block still says `jobs`, not the `jobs_planned` /
`jobs_submitted` split of Dv154.** The two exits build their `cost` dicts separately, and only the
completed path was changed in v3-prep. `cost.jobs: 0` is not wrong here — no gold job was submitted
— but the field name is the one Dv153 found ambiguous. Not fixed in this contract: it is a record
schema change on the money path of a session that is over, and the honest place for it is the next
registration's driver work, where a test can drive both exits against the same field names.

**Dv164 — the refusal record carries no `resume` block.** `resume.sessions` and
`bought_exactly_once` are built on the completion path, so the record of a session that bought
nothing does not restate the merge invariant. Correct by construction — there is nothing merged —
but a reader looking for `resume` in a v3 record will not find it. Named rather than added.

**Dv165 — the boot-log diagnosis is 68% subtraction.** The contract asked where the 391 s went;
the log names 11.76 s of fitness checks and 112 s of weight loading, has no timestamps, and cannot
attribute the remaining 267.6 s between container start, the python import chain and model
construction. Reported as a bound with the one substantive finding (the cold network-volume read
profile) rather than as a split invented from line ordering.

**Dv167 — a refused session's spend is charged against the next attempt's budget, silently.**
`RESUME_CAP_USD`, `RESUME_LEDGER` and `RESUME_PHASE` are three module constants, `read_ledger`
returns the existing anchor whenever its key is present, and `--project-stop-usd` can only tighten
(the F5 fix). Compose them and a second `--resume` today gets `0.45 − 0.1526 = $0.2974`, which is
below even the optimistic $0.3248 — so the next run refuses on this run's boot, not on prices.
Whether a (10)(a) refusal's spend should carry forward is a team-lead ruling; that there is no flag
that says either way is the defect. **Not fixed here**: a v4 needs its own three constants set
together against its own registration, and inventing them inside a contract that authorised one
session at $0.45 would be exactly the "raised cap to finish a run" the DO-NOT list forbids. Named,
priced, and left on the team lead's desk. Same family as Dv163: constants scoped to a phase that
is over.

**Dv168 — bar 3 counted rows nobody had adjudicated.** The registered denominator excludes "a row
the operator left untouched"; the producer built its gold from every reading, and
`tier_from_presence` returns `none` for five blank cells — which is also a legitimate ANSWER. An
unfinished pack would have scored its blanks as agreements with every empty model reply, and the
validator returns 0 on an unfinished pack, so nothing upstream would have caught it. It does not
bite today (30 of 30 came back, asserted) but this is the producer that scores the real bar. Fixed:
the validator's own predicate promoted to `is_adjudicated` — a tick OR a note, because an operator
writing «пусто» has answered — and untouched rows land in their own `not_gold` block, separate from
`unreadable`. Found by re-reading the bar's registered text against the code after it was written,
which is the check that should have come first.

**Dv166 — the staging pod is priced from its own clock, not from the balance.** The balance had not
moved at all when the endpoint was created, so a balance-derived "billed so far" would have read
$0.0000 and overstated the headroom. Rented at 20:33:31 UTC and deleted before 20:37, so ≤ 3.5 min
at $0.24/h ≤ $0.0140 — an upper bound, used as one.

---

## Assumptions

1. **The 60 s idle tail is billed after the last job.** It is a named term in the driver's
   projection, in the go/no-go and in `results/sku_projection_v3.json`, and it is inside every
   number above. If RunPod stopped billing the tail, every projection here is $0.0184 high.
2. **$0.00030669/s is still the rate.** Read from `results/srv2d_cost.json :: rate.usd_per_second`,
   settled, and not re-derived this session — there was no completed run to re-derive it from.
3. **The warm-up page's density is unknown, not average.** Nothing in this report claims 14.808 s
   is the population's marginal; it claims the gate refused on it, and that the alternative estimate
   has its own bias in the other direction.
4. **`worker-boot.log` as read is the sku-b-run boot**, not this session's. It was copied before the
   new template existed, and this session's boot has since overwritten it on the volume. Reading
   today's would cost another pod and was not in the contract.
5. **The bar producer's numbers on the smoke population are plumbing, not measurement.** The smoke
   answers are generated by a fake; only the shapes, the refusals and the key-space test are
   evidence.

---

## Commits

| # | commit | what |
|---|---|---|
| 0 | `84a7d22` | team-lead docs, unedited: `docs/PROMPT-sku-b-v3-run.md`, `docs/STATUS.md` |
| 1 | `20e2f8c` | the bar producer — `scorer` gains bars 1 and 3, `scripts/sku_bar_verdicts.py`, both test files |
| 2 | `6811c74` | `results/spend_sku_b_v3.json`, anchored before anything billed |
| 3 | `53f33b6` | Dv161 and Dv162, fix-on-touch, each with a control |
| 4 | `5dd9e1a` | the session's whole output: the refusal record and the ledger entry |
| 5 | `545fe1b` | this report |
| 6 | `9e0be97` | Dv168 — bar 3's denominator drops the unadjudicated rows |
| 7 | `4c3d123` | this report again: Dv167, Dv168 and the settled balance |
| 8 | the vault tail | its own final commit |

The report has two commits because the last review pass found Dv167 and Dv168 after it was first
written. The checkout table above covers commits 0–4; `9e0be97` was checked separately —
`make check` **1806 passed, 2 skipped**, and the two rows it adds are the untouched-row exclusion
and its control.
