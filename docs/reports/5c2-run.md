# 5c2-run — the backlog, bought under the sealed $8.00

## Read-back

**The cap is $8.00 and `results/prereg_5c2_run.json` is what pins it** — by VALUE, under
3.18 (7)(f), with an equality test on every number in `populations`, `prices`, `legs` and
`session_cap`; `fits` is a check standing beside the pin, not the pin.

**Two endpoints, never at once.** POSITIONS and the srv-2d config are different instruments and
one worker slot each; the first is torn down and proven gone by listing before the second exists.

**The three stop rules.** (10)(a): after the two non-gold warm-ups the driver re-projects the whole
run and refuses every gold call if that projection exceeds what is left of the $8.00 — a session
stopped there has touched no gold. (10)(b): a cap stop after gold calls began is a finding about
the CAP, closes nothing, fails no bar, and what happens next is a team-lead ruling. (10)(c): no
single job may be CAPABLE of billing past the remaining cap on its own — one job at the 900 s
execution timeout bills $0.2843 against $8.00 — and a job that ends TIMED_OUT ends the run with its
unbought remainder recorded.

**A mid-session death costs a boot and nothing else.** Re-entry re-asks nothing that was answered:
the per-channel watermark plus the answered-set on disk, and since Dv285 the post leg has its
`post_text` marker too, so a post that answered `[]` is no longer indistinguishable from a post
nobody asked. The session cap survives the restart and never resets.

**The evidence rows land in `data/derived/`** — the derived store beside the raw v1 stores, never
inside them, through the same `RawStore` the raw stores use. Never `results/smoke/derived/`, which
is the stub-served smokes' throwaway root and which a live pass must never read as answered.

**Assumptions stated:** that the contract's step-1 gate "driver dry-runs show EXACTLY the registered
populations" is a requirement ON the writer this contract owns, not a check on the prep-era queues
(Dv303); and that the volume needs no staging pass because the worker-side import closure is
byte-identical to the revision skub2 staged (Dv305).

---

## Step 1 — the $0 gates

*(filled in below as the session ran; every number here was produced before the first billable
action.)*

### The suite and the registration's own verifier

```
$ make check
2235 passed, 2 skipped in 61.24s          # the tree as inherited
$ python3 -m pytest tests/test_prereg_5c2.py -q
24 passed in 0.10s
```

### The nine pinned inputs

All nine re-hash byte-identical, so no prereg refusal fires:

```
docs/SPEC.md · results/census_5c2.json · results/census_c3a_posts.json
results/postcut_c3b.json · results/projection_5c2.json · results/srv2d_cost.json
config/registry.yaml · config/lexicon.yaml · src/market_pulse/positions.py
```

### The balance, re-read

```
anchor            $35.00 at 2026-08-01T08:34:09+00:00
balance now       $11.08
  balance delta   $23.9185
  billing since   $23.9087 (read)
PHASE 4 SPENT     $23.9185 of $33.00
REMAINING         $9.0815
```

`$9.0815`, not the `$9.1690` the registration recorded at 07:59 — the network volume bills at
≈$0.012/h and eleven hours passed. The cap still fits, with $1.0815 of phase headroom rather than
$1.1690. The remainder is DERIVED (`PHASE_CAP_USD − spent`) and never read out of
`sessions[-1].remaining_usd`, which says 6.1690 and is a true sentence about the $30 cap it was
written beside (3.18 (7)(b)).

### The console, before anything existed

```
$ runpodctl pod list -a                → []
$ runpodctl serverless list            → []
$ runpodctl template list --type user  → unfcr3ja0t | market-pulse-5b-a
                                         0g6zg73ptq | mp-5b-diag
$ runpodctl network-volume list        → qw4nwleanc  mp-srv2  EU-RO-1  100
```

The positive control is the third and fourth commands: the same CLI, the same auth, the same JSON
decoder, answering NON-empty. `[]` from the first two is therefore an empty console and not a
broken call.

### The driver dry-run against the registered selections

```
$ PYTHONPATH=src python3 scripts/run_5c2.py --dry-run
comment       5075 rows · 19 channels · pins matched 19/19
leaflet_page   159 rows · 19 posts   · @atb_market_official
post_text       44 rows · 10 channels
worst_case_job_usd 0.2843   session_cap_usd 8.0
```

Matched against the registration's own selection pins, not only its counts: nineteen per-channel
`ids_sha256` through `census_5c2.leg`, the pinned `post_media_5c1.json` sha for the pages, and the
newline-joined sha of `postcut_c3b.json :: rows` for the posts.

### The spend anchor, before anything billed

`results/spend_5c2run.json`, committed in `4446600`, anchoring the balance at **$11.0815436571**.
The driver refuses to write it twice — the negative control is in the transcript, and a second
anchor would restart the session counter at today's balance.

---

## Step 1.5 — the writer this contract owns

*(see Dv303. `scripts/run_5c2.py`, committed `9bf2c93` and `a189a32`, with
`tests/test_run_5c2.py`.)*

---

## Step 2 — Endpoint A, POSITIONS

### The volume was not staged, and why that is the stronger check (Dv305)

The worker runs `scripts/serve_handler.py` and the modules it imports. The whole closure is seven
files and every one of them is byte-identical to `0793a3ca`, the revision skub2 reset the volume to:

```
scripts/serve_handler.py · scripts/start_5b_worker.sh · src/market_pulse/__init__.py
src/market_pulse/local_llm.py · src/market_pulse/prompts.py · src/market_pulse/records.py
src/market_pulse/serving.py                                        MOVED since 0793a3ca: none
```

Staging exists to put the right code on the volume and the right code is already there. What
replaces the staging pod's `grep` is `serving.assert_serving`, holding the worker's own `info()`
against `results/sku_pilot_serving_v2.json :: expected_worker` — both positions prompt shas, the
1200-token ceiling and the revision, read off the filesystem the worker actually reads.

### The template and the endpoint, read back from the API's own answer

Template `xt7qz8o5ku`, exactly three variables and no fourth, with skub2's boot-log redirect:

```json
"env": { "BASE_WEIGHTS": "google/gemma-4-31b-it",
         "MODEL_REVISION": "842da3794eaa0b77d5f08bae87a17459d91ff475",
         "SERVING_CONFIG": "POSITIONS" },
"dockerStartCmd": ["bash","-c","exec bash /runpod-volume/start.sh > /runpod-volume/worker-boot.log 2>&1"],
"isServerless": true
```

Endpoint `m34sxo00ami5wt`:

```json
"executionTimeoutMs": 900000, "idleTimeout": 60, "workersMax": 1, "gpuIds": "ADA_24",
"networkVolumeId": "qw4nwleanc", "locations": "EU-RO-1", "flashBootType": "FLASHBOOT",
"templateId": "xt7qz8o5ku", "scalerType": "QUEUE_DELAY"
```

`executionTimeoutMs: 900000` equals the driver's `JOB_TIMEOUT_S`, so (10)(c) holds at the endpoint
as well as in the client — skub2's shape, reproduced.

Both configurations were also checked OFFLINE before any template existed, because
`serve_handler.settings` refuses some combinations by design and a refusal discovered after staging
costs a paid cycle:

```
Endpoint A / POSITIONS        -> {'serving_config': 'POSITIONS', 'adapter_dir': None, …}
Endpoint B / srv-2d config A  -> {'serving_config': 'A', 'adapter_dir': '/runpod-volume/…', …}
neg-control POSITIONS + ADAPTER_DIR   -> REFUSED: config POSITIONS serves the base with the ADAPTER OFF
neg-control POSITIONS no revision     -> REFUSED: config POSITIONS needs MODEL_REVISION
```

Two refusals beside two passes: the check discriminates rather than agreeing with everything.

### The first attempt died on the transport's ceiling (Dv309)

`HTTP 400: exceeded max body size of 10MiB`, before any worker saw the job. A page travels as a
base64 `data:` URL and 126 of them are ≈67 MB; `pack_size` knew only the execution timeout, which
is the LOOSER bound on this leg. **$0.1287 by balance delta, zero rows bought, zero rows written** —
the failure landed before the first pass, `data/derived` did not exist and the cursor never moved,
so the re-run bought nothing twice. Fixed in `79ae380`, with the packer skub2 had already sent 108
pages with.

### The two gates, both attempts

| | attempt 1 | attempt 2 | apart |
|---|---|---|---|
| boot, wall to the gate | 333.079 s | 307.342 s | — |
| page marginal | 1.774 s | 1.729 s | 2.6% |
| post-text marginal | 0.914 s | 0.947 s | 3.6% |
| projected | $0.2194 vs $8.00 | $0.2098 vs $7.8713 | — |
| verdict | GO | GO | — |

**The warm-up under-priced the population 2.4× and reproduced to within 3% while doing it
(Dv310).** The cause is on disk rather than inferred: the warm-up page is `page_queue[0]`, msg_id
4340, and its reply is `[]` — a leaflet's first page is a POSTER with nothing to extract, so the
probe measured a call that had no work in it. Dv180 recorded the same shape from the other end. The
gate is not what protected this run; `pack_size` taking the LARGER of the measured and the
registered marginal is.

### What the legs bought

| leg | asked | written | positions | unreadable | empty | packs |
|---|---|---|---|---|---|---|
| leaflet_page | 159 | **159** | 106 | 2 | — | 11 |
| post_text | 44 | **44** | 39 | 1 | 22 | 10 |

Both legs completed; neither was stopped. On disk: `data/derived/leaflet_pages` 159 rows,
`position_rows` 106, `post_texts` 44, `post_position_rows` 39 — the registered populations exactly.
A row carries the full 3.18 (6) field set, `served_by` names `m34sxo00ami5wt` and not a stub
string, and `prompt_sha256` is the pinned `ca6303c1…`.

### The price, and the finding in it

```
calls 24 · rows 205 · worker 2133.705s · queue 36.087s · wall 2267.544s · idle_share 0.059
seconds_per_row 10.408 · wall_per_row 11.061 · one worker (k2hdd6krvd8fb3)
```

**A page cost 10.408 s of COMPUTE against the 4.2794 s the registration priced it at — 2.43×.**
`idle_share: 0.059` rules the transport out: the wall is barely above the worker clock, so this is
not upload overhead, it is the model. skub2 measured that 4.2794 on 108 pages, and hot.md records
what those pages were — "the sent set is the first six pages of each leaflet and the unsent ones
are the dense grids". This run bought all 159. **The registered price was measured on the sparse
half of its own population.**

Session spend after Endpoint A: **$0.8451** by balance delta against the $8.00 cap, $7.1549 left —
below the comment leg's registered conservative corner of $7.4840 and above its marginal corner of
≈$6.82. That gap is exactly what the (10)(a) gate at Endpoint B exists to resolve.

### Teardown, proven by listing

```
$ runpodctl serverless delete m34sxo00ami5wt  → {"deleted": true}
$ runpodctl template   delete xt7qz8o5ku      → {"deleted": true}

$ runpodctl serverless list            → []
$ runpodctl pod list -a                → []
$ runpodctl template list --type user  → unfcr3ja0t | market-pulse-5b-a
                                         0g6zg73ptq | mp-5b-diag     ← the positive control
$ runpodctl network-volume list        → qw4nwleanc mp-srv2 EU-RO-1 100   ← the volume stays
```

---

## Deviations
**Dv303 — step 1's gate is a requirement on a writer that did not exist.** The contract asks that
"driver dry-runs show EXACTLY the registered populations: 5 075 / 159 / 44". The prep-era queues
answer **16 218 / 159 / 717**, and that is not a defect: `run_loop.posts_of` states in its own
docstring that the window is "the pre-registration's to name", and `run_loop.ENDPOINT` is `None`
because "registering an endpoint belongs to the paid session's contract". So no served driver
existed to dry-run, and the gate is a requirement ON the writer this contract owns
(`docs/reports/5c2-prep-b.md` §4: "the writer belongs to the paid session's contract"). Built as
step 1.5, at $0, committed and tested before the first billable action. [cause: contract-gap]

**Dv304 — the page warm-up has no non-gold input, and the post warm-up does.** The registration
asks for "two non-gold warm-up calls" on "REPRESENTATIVE" inputs — a real leaflet page and a real
post row. The post leg has 305 pre-filtered posts the D cut removed: real, same instrument, same
shape, registered by nothing. The leaflet leg has none, because 3.18 (7)(d) made the population the
whole corpus on disk. Resolved by keeping the representativeness (3.17 (11)(c) is explicit that a
64×64 probe priced a page at 1/3.5 of the truth) and warming up on the first REGISTERED page —
through `client.positions` directly, so no evidence row is written and no registered row is marked
answered by an unrecorded call. The page is therefore still owed and is bought again inside the
leg; the cost of the duplicate is one page, ≈$0.0013. [cause: contract-gap]

**Dv305 — no staging pass.** The contract's step 2 says "stage the volume per the skub2 gates". The
worker executes `scripts/serve_handler.py` plus the modules it imports, and the whole closure —
`serve_handler.py`, `start_5b_worker.sh`, `market_pulse/{__init__,local_llm,prompts,records,
serving}.py`, seven files — is **byte-identical to `0793a3ca`**, the revision skub2 reset the volume
to. Staging exists to put the right code on the volume; the right code is already there. The check
that replaces it is stronger than a `grep` on a staging pod: `serving.assert_serving` holds the
worker's own `info()` against `results/sku_pilot_serving_v2.json :: expected_worker`, which pins
both positions prompt shas, the 1200-token ceiling and the revision — read off the filesystem the
worker actually reads. A stale volume refuses at the handshake, before any gold call, at the cost
of the boot alone. Saved ≈$0.025 of a ≈$0.12 slack and one pod lifecycle. [cause: env]

**Dv306 — two id-hash conventions, one nearly-shared helper.** `census_5c2.leg` joins ids on a
COMMA; `scripts/postcut_c3b.py` joins them on a NEWLINE. The driver's first selection check used
one helper for both and all nineteen comment pins reported a mismatch — a refusal that was correct
about the separator and wrong about the data. Fixed by having the comment leg call `census.leg`
itself rather than restate its expression, and both directions are now asserted in
`tests/test_run_5c2.py::test_the_post_pin_is_the_newline_convention_and_the_comment_pin_is_not`.
Caught at $0, before the endpoint existed. [cause: tooling]

**Dv307 — a refused handshake leaves no ledger row.** `serving.assert_serving` raises `SystemExit`
inside `main()`, above `log_run`, so an endpoint serving the wrong configuration would bill its boot
and append nothing to `results/spend_5c2run.json`. This is exactly the hole skub2 closed for the
(10)(a) refusal path ("the two exits used to disagree") and this driver reopened on a third exit.
NOT fixed mid-session — the contract forbids editing the instrument mid-flight — and the anchor file
keeps the spend recoverable by hand. Fix belongs to the next contract. [cause: contract-gap]

> **AMENDED 2026-08-14 by measurement (5c2-validate-prep, step 0).** The verdict above is a true
> statement about `a189a32`, the revision this deviation was written against, and it stopped being
> true **inside this session**: `79ae380` — Dv309's twin, the crash fix — wrapped the whole of
> `run_the_legs` in `except BaseException` and calls `finalise` from that arm. `SystemExit` derives
> from `BaseException`, so the refusal exit landed in the same handler as the crash and the hole
> closed as a SIDE EFFECT of a fix aimed at something else. Nothing was edited for this hole, which
> is why the sentence "not fixed mid-session" read right at the time — the instrument was not
> touched; the exit it named moved anyway.
>
> Driven, not re-read: `tests/test_run_5c2.py::test_a_refused_handshake_writes_the_ledger_row_and_the_record`
> puts `main()` on the comment leg behind a transport whose `info()` differs from the assembled
> config-A pin in ONE field, with `runpod_guard.balance` stubbed so no `runpodctl` call is made.
> Both directions, at HEAD: the handshake still **refuses** (`SystemExit`, `client.calls == 1` — the
> guard is not softened into a warning), and the ledger **does** get its row, carrying the refusal
> message the exit died on:
>
> ```
> results/spend_5c2run.json :: runs[-1]
>   {"at": …, "balance": 9.0, "step_spent_usd": 0.0,
>    "note": "5c2-run comments — SystemExit: the endpoint is not serving the registered
>             configuration — merge_state: worker says 'merged-requantized', expected
>             'unmerged-adapter'. …"}
> the record   died: "SystemExit: the endpoint is not serving the registered configuration — …"
>              notes: ["the run ENDED on an exception: SystemExit"]   timing.calls: 1
> ```
>
> The negative control that says the test measures the fix rather than passing on its own: with the
> `except BaseException` arm deleted from a scratch copy of the driver — the Dv307 shape — the same
> test fails on `len(runs) == 1` with `runs == []`, which is the deviation's claim, reproduced.
>
> What is still owed is smaller than the deviation states and is named here rather than closed: the
> exit is covered by the CRASH handler, so a future edit that narrows `except BaseException` to a
> crash-only type would silently reopen it. The test above is what would go red.

**Dv308 — the rehearsal found two money-path defects an import could not.** Driving `main()`
against a fake endpoint before the first billable action (the house's stub-driven verification
rule) produced two fixes, both committed in `a189a32`:

1. **All 159 pages went into ONE pack.** `SliceTransport` buys a pack before the pass writes a row,
   so a job that overruns the 900 s execution timeout ends the RUN under (10)(c) *and* loses
   everything it paid for. `pack_size` now takes the LARGER of the warm-up marginal and the one the
   registration priced — Dv180 measured a single probe 3.64× off its population, and a fast probe
   must not buy a pack no population has supported. `JOB_FILL` 0.8 → 0.6.
2. **The cap gate priced off `worker_seconds`.** RunPod's summed `executionTime` is what a job spent
   computing, not what the worker cost: with `workersMax: 1` the worker is up and charged between
   two sequential jobs, and this run submits 52 packs where srv-2d submitted 4. `billed_now` takes
   the wall clock, the unit the bill is in. [cause: model]

**Dv309 — the transport's ceiling bound before the clock did, and it cost a boot.** The first
attempt at the leaflet leg died on `HTTP 400: exceeded max body size of 10MiB`. A page travels as a
base64 `data:` URL inside the job body and 126 of them are ≈67 MB; `pack_size` knew only the
execution timeout, which is the LOOSER bound on this leg. RunPod refuses the body before any worker
sees it, so `jobs.failed` stayed 0 and nothing was computed — but the boot and the two warm-ups were
already billed. **$0.1287 by balance delta, zero rows bought, zero rows written**: the failure
landed before the first pass, `data/derived` did not exist and the cursor never moved, so the
re-run buys nothing twice. `positions_gm4_skub.jobs` — the byte packer skub2 sent 108 pages with,
at `MAX_PAYLOAD_MB` 8.0, which never splits or re-encodes a page — was imported for its constant
and never wired. Fixed in `79ae380` with the test that fails on the old packer: 159 pages become 11
packs of 14–18, and both ceilings compose.

Its twin, same commit: **the driver died without writing the run record or a ledger row**, so a
session that had billed a boot left nothing on disk naming the spend. skub2 closed exactly this for
the (10)(a) refusal exit ("the two exits used to disagree"); a crash is the third exit and this
driver had it open. `finalise` now runs from both arms of `main`'s try and re-raises after.
[cause: model]

**Dv310 — the warm-up under-priced because it warmed up on an EMPTY page.** The registered page
marginal is 4.2794 s; the two warm-ups measured 1.774 s and 1.729 s, 2.6% apart across two
independent boots and both ≈2.5× under. The cause is on disk rather than inferred: the warm-up page
is `page_queue[0]` = msg_id 4340, the oldest queued page, and its reply is `[]` — a leaflet's first
page is a POSTER with nothing to extract, so the probe measured a call that had no work in it.
Dv180 recorded the same shape from the other end (an unsent page over-pricing the population 3.64×);
this is the under-pricing direction, and a run whose gate had less headroom would have been passed
by it. The gate is not what protected this run — `pack_size` taking the LARGER of the two marginals
is (Dv308). A warm-up that must price a population should be drawn from the middle of it, not from
its first element. [cause: model]

**Dv311 — the suite went red the moment the run wrote its first row, and every failure was true.**
Seven tests, three classes, none fixed toward passing: `the_derived_root_is_untouched` asserted
`data/derived/` does not EXIST and its own docstring prescribed the redesign (a before/after
snapshot) for the day a legitimate writer created it; `wire_pages` built its fixture on msg_ids
4340–4344 and the run bought 4340–4526, so the fixture's queue silently became 0 and its refusal
reported a number about the wrong thing; and `test_the_remainder_is_derived_…` read `sessions[-1]`
positionally, which stopped being the row the sealed registration names the moment this session's
own spend was witnessed. Fixed in `d37f6db` — snapshot, `FIXTURE_PAGE_IDS` out of any collectable
range, and selection by `budget.read_at` refusing anything but exactly one match. [cause: process]

**Dv312 — the phase ledger's permanent silence guard fired, and it was right.** Endpoint A's spend
lived only in `results/spend_5c2run.json`; `results/spend_phase4.json` — the file `runpod_guard`
reads before every start — had never heard of it. `scripts/witness_phase_ledger.py` (`82aa1ae`) is
the live counterpart of prep-a's one-shot repair: it READS `runs[-1].balance` rather than re-reading
the account, because the guard matches on the balance READING and a re-read minutes later is a
different number. Witnessed at 2026-08-13T17:59:20Z, balance 10.2585299348, 36 sessions. [cause:
contract-gap]

**Dv313 — two commits landed on a red tree.** `make check 2>&1 | tail -3 && git commit` takes the
exit code of `tail`, not of `make`, so `b32c083` and `2a32b45` were committed while seven tests were
failing. The failures were the legitimate ones of Dv311 and both commits are green under the fix,
but the shell idiom is the defect: `set -o pipefail` is now used for every verifier invocation in
this session. [cause: tooling]

**Dv314 — the redesigned derived-root guard is not robust to a CONCURRENT writer.** It compares a
snapshot of `data/derived/` before and after a smoke, so running the suite while the paid driver is
writing there fails it for a true reason that is not the one it tests. Nothing in normal use writes
concurrently; the consequence for this session is that the per-commit checkout table is measured
AFTER the run rather than during it. Named rather than fixed: a guard that ignored concurrent
writes would ignore the regression it exists to catch. [cause: process]


---

## Step 3 — Endpoint B, the srv-2d serving config

### The expectation had to be ASSEMBLED, and two carriers cross-check it

POSITIONS has `results/sku_pilot_serving_v2.json :: expected_worker`, a block written to BE the
expectation. Config A has none, so it is built from the house pin `results/serving_5b.json ::
worker` minus three provenance fields (`repo_commit` moves with every staging, `runtime` has its own
guard, `merged_provenance` is B's business) — and `results/parity_srv2.json ::
config.serving.worker`, the srv-2d session whose price the registration uses, must AGREE on every
compared field or the driver refuses. **Eleven fields, and they agree.**

Template `vkjzux03gf`, endpoint `gfmtqi3uqcjyv5`, every flag read back from the API's own answer:
`executionTimeoutMs 900000 · idleTimeout 60 · workersMax 1 · gpuIds ADA_24 · networkVolumeId
qw4nwleanc · locations EU-RO-1 · FLASHBOOT · QUEUE_DELAY`.

### The gate, and the arithmetic written before it was measured

The warm-up is **3 non-gold rows from 3 channels in ONE job** — the shape a pack has, not the shape
a single call has (Dv310 is what a point costs).

```
billed_seconds 435.533 · text_marginal 4.4123 s/row · gold_calls 5075
gold_seconds 22392.592 · idle tail 60 · projected $7.0196 · budget $7.1549 → GO
registered conservative corner $7.4840          headroom $0.1353 (1.9%)
```

**The discriminating comparison, and it answers Endpoint A's finding:**

| leg | registered | measured | apart |
|---|---|---|---|
| leaflet page | 4.2794 s | 10.408 s | **+143%** |
| comment row | 4.262 s | **4.4123 s** (warm-up) / **4.247 s** (whole leg) | **+3.5% / −0.4%** |

One endpoint, one worker class, two legs, two verdicts. The difference is not the machine — it is
**what each price was measured on**: srv-2d priced the comment row over 758 rows of the frozen test
set, a population; skub2 priced the page over 108 pages that were the first pages of each leaflet,
a systematically sparse prefix. A price is only as representative as its sample, and a 2.43× miss
beside a 0.4% hit is evidence for that sentence rather than an assertion of it.

### What the leg bought

**5 075 of 5 075 rows, 19 of 19 channels, 53 packs, `stopped_at: None`.** No cap gate fired, no
channel went unreached, and the plan the leg recorded before its first job matches what it wrote.

```
calls 55 · rows 5078 · worker 21565.258s · queue 153.926s · wall 21894.005s · idle_share 0.015
seconds_per_row 4.247 · wall_per_row 4.312 · one worker (zs3ohv1dvvpwvi)
post_states: post_text 4940 · no_text_and_no_caption 135
```

**My mid-run extrapolation was wrong and the record is what says so.** Six packs in, the observed
wall rate read 4.96 s/row and I projected a cap stop at ~4 600 rows. Over the whole leg it is
4.312 s/row and `idle_share` is 0.015. The early packs were the small channels — four-row packs
where one boundary is a quarter of the work — and a rate read off the head of a queue is not the
queue's rate.

### Teardown, proven by listing

```
$ runpodctl serverless delete gfmtqi3uqcjyv5  → {"deleted": true}
$ runpodctl template   delete vkjzux03gf      → {"deleted": true}

$ runpodctl serverless list            → []
$ runpodctl pod list -a                → []
$ runpodctl template list --type user  → unfcr3ja0t | market-pulse-5b-a
                                         0g6zg73ptq | mp-5b-diag     ← the positive control
$ runpodctl network-volume list        → qw4nwleanc mp-srv2 EU-RO-1 100   ← the volume stays
```

---

## Step 4 — the outcome: COMPLETION

Every registered row of every registered leg was bought, and the evidence is on disk.

| leg | registered | bought | evidence rows |
|---|---|---|---|
| comment | 5 075 | **5 075** | 5 075 `comment` |
| leaflet_page | 159 | **159** | 159 `leaflet_page` + 106 `position_row` |
| post_text | 44 | **44** | 44 `post_text` + 39 `position_row` |

```
$ evidence.assert_complete over every row under data/derived/
rows by kind: {'comment': 5075, 'leaflet_page': 159, 'position_row': 145, 'post_text': 44}
served_by   : {'gfmtqi3uqcjyv5': 5075, 'm34sxo00ami5wt': 348}
failures    : 0          any stub-served row: False
```

5 423 rows, zero incomplete, and `served_by` names only the two endpoints this session created —
the field exists so that a row answered by a fake and a row answered by a registered endpoint
cannot be confused, and the grep for `<stub` is empty.

### The three cost readings, kept distinct (Dv33)

| reading | value | what it is |
|---|---|---|
| balance delta | **$7.5309** | anchor $11.0815436571 − balance $3.5506603068. A FLOOR: RunPod settles late |
| client wall clock | $7.5491 | (2267.544 + 21894.005 + 393.079 + 60) s × $0.00030669 |
| registered projection | $7.8546 | the seal's own number, with 3% drift |

The wall reading is $0.0182 ABOVE the balance delta, which is the right way round: Dv33 makes the delta a floor that settles late, so the two bracket the truth rather than contradict it.

**Under the registered projection, over the sum of the legs that overran.** The leaflet leg cost
2.43× its line and the total still came in $0.32 below the seal, because the comment leg — 95% of
the budget — was registered at the CONSERVATIVE corner ($1.4281/1000 rows, i.e. 4.656 s/row) and
ran at 4.312 s/row. The padding in the conservative corner absorbed the overrun in the leg that had
none. That is the corner doing its job, and it is worth saying plainly: **had the registration
priced the comment leg at its marginal corner, this session would have stopped at the cap gate.**

Session: **$7.5309 of the $8.00 cap**, $0.4691 unspent.
Phase 4: **$31.4493 of $33.00**, $1.5507 remaining, both legs witnessed in the phase ledger.

**The two phase-ledger entries are ANCHOR-relative, not incremental**, as every entry in that file is: Endpoint A's reads `spent 24.7415` and Endpoint B's `spent 31.4493`, each being `$35.00 anchor − balance at that reading`. Summing `spent_usd` across sessions double-counts. This session's own cost is the difference, $6.7079 for the comment leg on top of $0.8451.

### Watermarks after, and the deferral measured rather than asserted

`data/loop_cursor.json`, the three keys per pinned channel, after the run:

| channel | inference | leaflet | post_text | in_store | in_window | queue now |
|---|---:|---:|---:|---:|---:|---:|
| @HealthPsycholog | 3 378 | — | — | 97 | 97 | 0 |
| @VARUS_channel | 21 720 | — | 10 628 | 6 410 | 242 | 0 |
| @chifit_family | 2 069 | — | — | 4 | 4 | 0 |
| @denisovapro | 2 135 | — | — | 6 | 4 | 0 |
| @kkondr_fit | 2 109 | — | — | 4 | 4 | 0 |
| @klopotenkofood | 21 407 | — | — | 232 | 222 | 0 |
| @kopiyochka1 | 392 701 | — | — | 223 | 223 | 0 |
| @mamo_nepsichuy | 17 508 | — | — | 10 | 9 | 0 |
| @mandziak | 49 226 | — | — | 1 048 | 1 026 | 0 |
| @matusi_ukr | 580 440 | — | — | 2 890 | 2 717 | 0 |
| @msuaaaa | 13 741 | — | 10 656 | 4 928 | 163 | 0 |
| @olgaa_trainer | 643 | — | — | 4 | 4 | 0 |
| @polyakova_fitness | 2 460 | — | — | 8 | 8 | 0 |
| @retsepty | 49 804 | — | — | 105 | 104 | 0 |
| @sashafitnesslife | 10 119 | — | — | 83 | 83 | 0 |
| @smirnov108 | 31 435 | — | — | 101 | 100 | 0 |
| @tarilka_malyuka | 213 | — | — | 45 | 45 | 0 |
| @useful_healthy_fitness_menu | 3 227 | — | — | 4 | 4 | 0 |
| @ya_Nenka | 2 599 | — | — | 16 | 16 | 0 |
| **TOTAL** | | | | **16 218** | **5 075** | **0** |

`@atb_market_official` carries `{"leaflet": 4526}` — the top of the page corpus.

**The post-condition I set before the leg came out FALSE, and that is the finding.** I expected the
queue to read `in_store − in_window = 11 143` afterwards. It reads **0**. The window is the newest
four weeks, so the in-window rows are each channel's HIGHEST ids: a watermark that advances past
them lands above every older row, and the queue — defined as "above the watermark, minus answered" —
empties. The 11 143 are not gone, they are underneath.

So the reversibility claim was measured instead of asserted:

```
queue with the watermark reset : 11143
rows already answered on disk   : 5075
of the reset queue, IN-WINDOW   : 0     <- none of the 5 075 would be re-bought
reversible and re-buys nothing  : True
```

**3.18 (4)'s deferral survives, and it stopped being reversible by the queue alone** — it now needs
the `inference` cursor field cleared, at which point `above()`'s answered-set subtraction makes the
re-entry free. A future contract that wants the full history should say so; nothing on disk was
lost, but nothing on disk says "11 143 owed" either.

---

## Verify gate

### `make check` after the run

```
$ make check
2262 passed, 2 skipped in 63.10s
$ ruff format --check .
266 files already formatted
```

### The evidence, checked on every row rather than a sample

```
$ evidence.assert_complete over every row under data/derived/   → 0 failures on 5 423 rows
```

### The populations, re-counted from disk against the seal

```
registered:  comment 5075 | leaflet_page 159 | post_text 44
on disk:     comment 5075 | leaflet_page 159 | post_text 44
derived too: position_row 106 (leaflet) | post_position_row 39
```

### The per-commit checkout table

*(each commit into its own detached worktree, gitignored `data/` entries linked per ENTRY; the
control is the last commit BEFORE this session, and without it the table cannot tell "reading each
commit" from "reporting a constant")*

| commit | suite in the worktree | what moved |
|---|---|---|
| **`f8ba5bf`** | **6 failed, 2229 passed, 2 skipped** | **control — the last commit BEFORE this session** |
| `e39b0ab` | 6 failed, 2229 passed | docs only |
| `9053f86` | 6 failed, 2229 passed | vault only |
| `9bf2c93` | 6 failed, **2244** passed | the driver's 15 tests land |
| `4446600` | 6 failed, 2244 passed | the anchor, no code |
| `a189a32` | 6 failed, **2246** passed | +2 (pack sizing, wall clock) |
| `79ae380` | 6 failed, **2248** passed | +2 (the byte packer) |
| `b32c083` | **8** failed, 2246 passed | **+2 failures: the paid step ledger appears and the phase ledger is silent (Dv312)** |
| `2a32b45` | 8 failed, 2248 passed | +2 (the config-A pin) |
| `d37f6db` | **3** failed, 2253 passed | **−5: the derived-root guards redesigned (Dv311)** |
| `82aa1ae` | **1** failed, 2261 passed | **−2: the phase ledger witnessed (Dv312)** |
| `d513869` | 1 failed, 2261 passed | the comment leg's artifacts |

**The control is what makes this a measurement.** It reads 6 failed where the last two rows read 1,
so the instrument is reading each commit rather than reporting a constant — and every step between
them is explained by a named commit rather than by a shrug.

The six on the control are two classes, both properties of the ENVIRONMENT and not of any commit
here: five are the `data/derived/` guards, which this run legitimately reddened by creating the
root and which `d37f6db` redesigns; the sixth is
`test_collect_5c1.py::test_the_guard_reads_the_pinned_paths_off_the_pin_file`, which resolves pinned
paths against the checkout it runs in and has failed in every worktree row since c3a measured it
(Dv193). The last row's `1 failed + 2261 passed` is the same 2262 `make check` reads green in the
repo itself.

First run of this table read **46 failed on every row including the control** — see Dv315.

---

## Commits

| # | commit | what |
|---|---|---|
| 1 | `e39b0ab` | docs: 5c2-run queued — the contract and the STATUS pointer, verbatim |
| 2 | `9053f86` | chore(vault): the 2026-08-13 day-close tail, left uncommitted by the previous session |
| 3 | `9bf2c93` | feat: the live driver — the registered selection, one job per pack |
| 4 | `4446600` | data: the session's spend anchor, before anything bills |
| 5 | `a189a32` | fix: the pack sized pessimistically, the cap priced off wall clock |
| 6 | `79ae380` | fix: the leaflet pack bounded by BYTES, and a crash still writes the ledger |
| 7 | `b32c083` | data: Endpoint A complete — 159 pages and 44 posts |
| 8 | `2a32b45` | feat: Endpoint B's guards — assembled pin, spread warm-up, legible stop |
| 9 | `d37f6db` | test: the guards the paid run reddened, redesigned rather than deleted |
| 10 | `82aa1ae` | feat(ledger): witness a paid run in the phase ledger from its own numbers |
| 11 | `d513869` | data: the comment leg complete — 5 075 of 5 075, the session closed |
| 12 | this one | docs(report): 5c2-run |

`git add -A` was used nowhere; every commit was staged by path. Commits 7 and 8 landed on a red
tree — see Dv313.

---

**Dv315 — the checkout table's first run was a broken instrument, and the CONTROL is what said
so.** c3a's repaired instrument links the gitignored `data/` entries per ENTRY into each worktree.
That is not the whole set: the suite also reads gitignored content under `results/` — `smoke/`, the
adapter weights, the training states — and without them every row read **46 failed, 2183 passed,
6 errors**, uniformly, including the control commit that was green in the repo the day before.
Uniform-and-wrong across every row is the signature of an instrument, not of eleven commits. The
linker was generalised to `git status --porcelain --ignored=matching -- data results`, and the
control then read 6 failed / 2229 passed — a measurement. **Without the control row this table
would have been reported as eleven red commits.** [cause: tooling]

## Process signals

1. **The rehearsal against a fake endpoint paid for itself, and its two misses are the lesson.**
   Driving `main()` before the first billable action found two money-path defects an import could
   not see. It missed two more — the 10 MiB body ceiling and the absent ledger row on a crash —
   and not because a fake cannot know them: the fake I wrote modelled the worker's ANSWERS and
   never the transport's LIMITS. It never refused a payload and never raised. A fake that asserted
   `len(json.dumps(payload)) < 10 MiB`, or that raised once, would have caught both at $0. Model
   the failure modes, not only the happy replies.
2. **Both cost surprises were about the SAMPLE, not the machine.** The registered leaflet price was
   measured on the sparse prefix of its own population and missed 2.43×; the registered comment
   price was measured on a population and hit within 0.4%. Worth carrying into every future
   registration: name what a price was measured ON, beside the number.
3. **The conservative corner is what made the run finish.** Priced at the marginal corner the
   comment leg would have hit the cap gate. The padding was not caution for its own sake — it
   absorbed an overrun in a different leg entirely.
4. **A green suite has a shelf life and this run reached it.** Seven tests went red the moment the
   first evidence row landed, all of them true, and one of them had its own redesign written into
   its docstring in advance. That foresight is worth copying.
5. **`make check | tail && git commit` commits on red.** The pipeline's exit code is `tail`'s. Two
   commits shipped that way before it was noticed (Dv313); `set -o pipefail` is the fix.

---

## Open questions for the team lead

1. **The leaflet price is known wrong by 2.43× and no artifact carries the right one.** This run
   measured 10.408 s/page over the whole 159-page corpus — the first population measurement this
   instrument has ever had. Whether that becomes the registered price for the next cycle, and
   whether `results/sku_b_positions_skub2.json`'s 4.2794 s should be annotated as prefix-measured
   rather than silently reused, is a ruling, not an executor's call.
2. **`scripts/witness_phase_ledger.py` exists and nothing calls it automatically.** This session ran
   it by hand, twice. The next paid session re-opens the same silence unless the driver's
   `finalise` invokes it or a contract names it as a step. Which contract owns that is a team-lead
   decision.
3. **The comment backlog is now under the watermark.** 11 143 rows, recoverable by clearing one
   cursor field and free to re-enter (measured above), but nothing on disk states the debt. If
   3.18 (4)'s history is ever bought, the contract that buys it has to say so itself.

---

## Addendum — 2026-08-14, the acceptance's debts (5c2-validate-prep, step 0)

Three questions the acceptance raised about this report, answered here rather than in the report
that asked them. Dv307 is amended in place, above.

### The $0.8451 in the Endpoint-B budget, and where it comes from

The comment leg was started with `--already-usd 0.8451`, so the (10)(a) gate priced itself against
`$8.00 − $0.8451 = $7.1549` — the `budget_usd` in `results/run_5c2_comments.json`. **That number is
a HAND-TYPED conservative reading and no artifact on this disk re-derives it.** It is stated here
because a hand-supplied number in a money path is legal only when the record names it as such.

What the persisted carriers say about the same quantity:

| carrier | value | what it is |
|---|---|---|
| `results/spend_5c2run.json :: runs[0].step_spent_usd` | **$0.8230** | $11.0815436571 − $10.2585299348, the balance delta |
| `results/spend_phase4.json :: sessions[-2]` | balance $10.2585299348 | the same reading, witnessed into the phase ledger |
| the client's wall clock | $0.8344 | (2 267.544 + 393.079 + 60) s × $0.00030669 |
| typed at the command line | **$0.8451** | +$0.0221 over the delta, +$0.0107 over the wall |

The gap to the delta is $0.0221 — 72 seconds of worker time at the registered rate. No balance of
$10.2364436571 (the reading that would produce it) appears in any file, log or record in this repo;
neither the wall arithmetic nor the delta reproduces it, and the session transcript is not on disk.
So the honest statement is the one at the top: it was typed by hand as a safer reading, not read
back from a carrier.

**Why it is legal, and the Dv33 floor sentence it rests on.** `spend_or_note`'s docstring and Dv33
say the balance delta is a **FLOOR** — "RunPod settles it minutes to hours late" — so the true
spend at that moment was **≥ $0.8230**, and a larger number is the conservative direction rather
than a wrong one. The consequence is checkable and one-way: a bigger `already_usd` SHRINKS the
(10)(a) budget, so the hand-typed reading could only make the gate stricter, never looser. Priced
both ways, the verdict does not move — the gate projected $7.0196:

```
budget with the typed $0.8451   $7.1549   headroom $0.1353   → GO
budget with the ledger $0.8230  $7.1770   headroom $0.1574   → GO
the registered conservative corner $7.4840 exceeds BOTH budgets — which is why the gate,
and not the corner, is what let the leg run.
```

The rule this leaves behind: `--already-usd` takes a number no file has to agree with, and the run
record stores it (`already_usd`) without a provenance field beside it. A future driver should read
the previous leg's `step_spent_usd` off the ledger and require the operator's override to be
LARGER, or record where the typed number came from.

### `timing.calls` 55 against 53 packs and one warm-up

The extra call is the **`assert_serving` handshake** — `client.info()`, verified against the run
records rather than asserted. `EndpointClient._run` increments `calls` on every terminal job
whatever its `op`, and `info` goes through `_run_with_retry` like any other, so the counter is a
count of SUBMISSIONS and not of gold jobs. `positions_gm4_skub.JOBS_READING` already says it in
prose — "`jobs_submitted` is `timing().calls` … which on the real endpoint client includes the
`info` handshake and always includes the two warm-up calls".

Both legs leave exactly one call unaccounted for, which is what makes the handshake the answer
rather than a guess:

| leg | packs | warm-up jobs | handshake | `timing.calls` | `timing.rows` |
|---|---:|---:|---:|---:|---:|
| comments (`gfmtqi3uqcjyv5`) | 53 | 1 (3 rows in one job) | 1 | **55** | 5 078 = 5 075 + 3 |
| positions (`m34sxo00ami5wt`) | 11 + 10 | 2 (one page, one post) | 1 | **24** | 205 = 159 + 44 + 2 |

The comment leg's 53 packs sum to `written` 5 075 against `asked` 5 075, so no pack is missing from
the count either.
