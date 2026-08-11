# sku-b-run — the position-layer pilot, the one paid attempt

`docs/PROMPT-sku-b-run.md` · executor · 2026-08-11 · session spend **$0.1965** of the $0.35 cap

## Read-back

The eight sequence gates, one line each:

1. **$0 gates before anything exists** — `make check`, the preflight in the peft venv at exit 0,
   the balance re-read against `results/spend_phase4.json`, empty pod and serverless listings, and
   the driver's `--dry-run` showing 108+30 sources in 7+1 jobs.
2. **Stage the volume BEFORE any endpoint exists** — `repo/` on `qw4nwleanc` to HEAD by git bundle,
   ending in a CONTENT check, because `Already up to date.` is the signature of a no-op.
3. **A NEW template with exactly three variables** — `market-pulse-sku-positions`, POSITIONS, the
   base weights and the full revision sha; never an srv-2d-era template reused.
4. **The endpoint from that template** — `--gpu-id ADA_24 --workers-max 1 --idle-timeout 60
   --execution-timeout 900`, the 900 matching the driver's `JOB_TIMEOUT_S`.
5. **The run, exactly one invocation** — the driver owns the order: identity stop → two NON-gold
   warm-up calls → go/no-go → page leg → text leg, with the in-run gate between jobs.
6. **Outcome A (the go/no-go refuses) or Outcome B (the run completes)** — A goes straight to
   teardown with no v3 in this session; B writes the bar-1 and bar-3 verdicts through R1–R5 and
   reports bar 2 as the dump and its n only.
7. **Teardown, proven not asserted** — delete the endpoint then the template, prove by listing WITH
   the positive control, the volume stays, the balance is re-read into the record and the ledger.
8. **Step 0 / tail commits** — team-lead docs verbatim at the start, the run's artifacts by path,
   the vault tail as its own final commit.

The two stop semantics:

- **(10)(a), before gold:** a projection made after the two warm-up calls that exceeds what is left
  of the cap REFUSES every gold call; that session has touched no gold and **has consumed NO
  attempt**, and the pilot returns to the team lead for a v3 under the measured price.
- **(10)(b), mid-leg:** a cap stop after gold calls began is a finding about the **CAP** and not
  about the instrument — it does not close B, it is not a failed bar, and what happens next is a
  team-lead ruling, never a silent re-run.

**One attempt — no bar, leg or draw is ever re-run after its result.**

## The outcome: neither A nor B

The go/no-go **passed** the run (projected $0.1936 against $0.3403 left of the cap) and the in-run
gate then **stopped** it after the first page job, 17 gold calls into 138. That is SPEC 3.17
**(10)(b)**: a finding about the cap. No bar is scored, B is not closed, and the ruling is the team
lead's.

The brief predicted a (10)(a) refusal as the likely first outcome. It did not happen, and the reason
is the most useful thing this session bought — see *The finding*.

## Gate 1 — the $0 gates

```
make check                → 1750 passed, 2 skipped in 53.40s
preflight (peft venv)     → EXIT=0
                            PASS  the fixed guard ACCEPTS a bare real model
                            PASS  the fixed guard REFUSES an adapter-carrying one
                            PASS  the control fires: the vis-a guard refuses the bare model
                            PASS  POSITIONS serves the base with no adapter directory
                            PASS  POSITIONS refuses ADAPTER_DIR / MERGED_DIR / an unpinned base
                            PASS  every config x op cell behaves as CONFIG_OPS says
                            PASS  a job exactly at the payload budget passes
                            PASS  a job one byte over it refuses rather than shortening the album
                            PASS  a truncated tail is a parse REFUSAL, never an empty answer
                            PASS  the control: an empty array is an ANSWER and is accepted
runpodctl pod list -a     → []
runpodctl serverless list → []
network-volume list       → qw4nwleanc mp-srv2 EU-RO-1 100
```

The driver's dry run, verbatim:

```
page leg   108 pages sent (of 159 available, 19 posts) in 7 job(s), largest 7.99 MB
text leg   30 rows in 1 job(s)
dump       17 columns: item, page, file, sha256, brand_raw, brand_id, line, category, size, fat,
           price_promo, price_old, discount_pct_printed, price_qualifier, tier, depth,
           depth_disagrees_with_printed
```

The guard, before anything was created:

```
anchor            $35.00 at 2026-08-01T08:34:09+00:00
balance now       $12.42
  balance delta   $22.5815
  billing since   $22.5718 (read)
PHASE 4 SPENT     $22.5815 of $25.00
REMAINING         $2.4185
```

**The cap anchor, written before the first billed step** (Dv149, operator-approved): the driver
creates `results/spend_sku_b.json` at ITS OWN start, which is after gate 2's staging pod, so the
pod's cost would have sat outside the cap arithmetic and (10)(a) would have projected against a full
$0.35. The anchor was written here instead, by calling the driver's own `read_ledger` — the same
producer, not a hand-built record:

```json
{ "runpod_balance_at_sku-b_start": 12.4184987367, "cap_usd": 0.35, "runs": [] }
```

It worked as intended: the driver's first ledger line of the session read
`ledger: spent $0.0097 of $0.35`, which is the staging pod, not zero.

## Gate 2 — the volume, staged before any endpoint existed

Staging pod `3b1eigbclu7lho`, RTX 2000 Ada at **$0.24/h** (Dv150 — the runbook's class is ~$0.53/h;
this gate does git and nothing else), EU-RO-1, volume attached, `--terminate-after` two hours out.

**The content check has a negative control, because it was read before the re-stage as well as
after:**

| | before | after |
|---|---|---|
| `grep -c POSITIONS scripts/serve_handler.py` | **0** | **10** |
| `src/market_pulse/provenance.py` | *No such file or directory* | present, 3906 bytes |
| `git rev-parse HEAD` | `d408034db4c2…` (vis-c era) | `49665c7d0397…` |

The staging itself, verbatim — the bundle names its real ref and the reset targets an explicit sha,
so a fetch that moved nothing would have failed loudly instead of printing `Already up to date.`:

```
=== bundle heads (the REAL ref, not FETCH_HEAD) ===
49665c7d0397d24bea21d66fdd981c1c05e1d123 HEAD
=== fetch ===
From /workspace/mp-skub.bundle
 * branch            HEAD       -> FETCH_HEAD
=== reset --hard to the Mac's exact sha ===
HEAD is now at 49665c7 docs(team-lead): the sku-b-run contract and the acceptance that authorises it
=== proof ===
49665c7d0397d24bea21d66fdd981c1c05e1d123
(git status --short printed nothing)
```

`start.sh` verified, not edited:

```
5b3bcbb2f59372f4cb3ee940caad5b5b4b90bb22adeff1f783f8c8301474b46c  /workspace/start.sh
5b3bcbb2f59372f4cb3ee940caad5b5b4b90bb22adeff1f783f8c8301474b46c  scripts/start_5b_worker.sh
```

And the second net the runbook names — the prompt shas the worker will report, rendered on the
volume itself:

```
positions_post_gm4 ca6303c157d46e707aaf3fc52c7a05ed1450e24c26db0e7c93eefba4f6968754
positions_text_gm4 7250b87aa1c2de407e06ab9eed565dd4d88025add7be0d2d2a87607c0d872860
```

Both equal `results/sku_pilot_serving.json :: expected_worker`. Pod deleted, `pod list -a` → `[]`.

## Gates 3 and 4 — the template and the endpoint

Template `90xcwcwtyu`, exactly three variables and no fourth:

```json
"env": { "BASE_WEIGHTS": "google/gemma-4-31b-it",
         "MODEL_REVISION": "842da3794eaa0b77d5f08bae87a17459d91ff475",
         "SERVING_CONFIG": "POSITIONS" },
"dockerStartCmd": ["bash","-c","exec bash /runpod-volume/start.sh > /runpod-volume/worker-boot.log 2>&1"],
"isServerless": true
```

Endpoint `0yqlvm0b8wzzsw`, every flag read back from the API's own answer:

```json
"executionTimeoutMs": 900000, "idleTimeout": 60, "workersMax": 1, "gpuIds": "ADA_24",
"networkVolumeId": "qw4nwleanc", "locations": "EU-RO-1", "flashBootType": "FLASHBOOT",
"templateId": "90xcwcwtyu", "scalerType": "QUEUE_DELAY"
```

`executionTimeoutMs: 900000` is the flag's seconds stored as milliseconds, and it equals the
driver's `JOB_TIMEOUT_S` — (10)(c) holds at the endpoint as well as in the client.

## Gate 5 — the run, and both stops in order

One invocation, launched detached (Dv148, operator-approved) and watched by PID. The driver's
console, verbatim:

```
ledger: spent $0.0097 of $0.35 (balance $12.41)
endpoint       0yqlvm0b8wzzsw · POSITIONS/base-no-adapter
  revision      842da3794eaa0b77d5f08bae87a17459d91ff475
  ceiling       800 new tokens, greedy, batch 1
  prompts       positions_post_gm4 ca6303c157d4… · positions_text_gm4 7250b87aa1c2…
  warm-up positions_post_gm4   stop  1.436s  []
  warm-up positions_text_gm4   stop  0.756s  []
  go/no-go      138 gold calls project $0.1936 against $0.3403 left of the cap — proceed
  page job 00  17 item(s)  ok  7.85 MB
  after 17/138: 5.0772s/call · $0.1472 spent → $0.3540 projected
  STOP before positions_post_gm4 job 01: the run projects $0.3540 against $0.3403 left of the
    $0.35 cap. A cap is not raised to finish a run
  after 17/138: 5.0772s/call · $0.1472 spent → $0.3540 projected
  STOP before positions_text_gm4 job 00: the run projects $0.3540 against $0.3403 left of the
    $0.35 cap. A cap is not raised to finish a run
  [17 per-page lines]

14 positions from 17 sources · 1 unreadable · 10 empty · 13 carry a crossed-out price · $0.0943 of $0.35
wrote results/sku_b_positions.jsonl and results/sku_b_positions.json
STOP AND REPORT: a reply was refused by the parser. No retry is made.
```

**Two stops, in this order, and the second is not the cap.** The in-run gate ended both legs; the
record was then written in full; the process finally exited non-zero on the parse refusal of one
page answer. A reader who sees only the last line will think the cap ended the process — it did not.

**The stop was not caused by the anchor fix.** The projection was **$0.3540**, which exceeds the
whole **$0.35** cap as well as the $0.3403 that was left of it. Even with the staging pod outside
the arithmetic, this run would have stopped at the same job.

## The numbers

| | value | what it measures |
|---|---|---|
| boot | **391.369 s = $0.1200** | the weight load, billed to the `info` handshake; the historical cold start is 175.8 s, so this is **2.2× worse** |
| warm-up, page | **1.436 s** | a generated 64×64 image |
| warm-up, text | **0.756 s** | one row outside the 30-row pack |
| go/no-go projection | **$0.1936** vs $0.3403 budget → proceed | 138 gold calls at the warm-up marginals + the 60 s idle tail |
| page gold marginal | **5.0772 s/call** (n=17) | **3.54× the warm-up page marginal** |
| re-projection at 17/138 | **$0.3540** vs $0.3403 → stop | the same arithmetic on the measured marginal |
| text gold marginal | **never measured** | the text leg made no gold call |
| idle tail | 60 s = $0.0184 | inside every projection since the fix pass |

Three cost readings, none of which is the others:

- **`cost.usd: 0.0943`** — the balance delta at record-write. A FLOOR (Dv33: RunPod settles minutes
  to hours late).
- **`per_gate[0].spent_usd: 0.1472`** — billed seconds × the settled rate. **This is the number the
  gate acted on**, and the only one available to it mid-run.
- **$0.1965** — the anchor delta re-read at `2026-08-11T18:23:45Z`, ~7 minutes after the teardown.
  Still a floor. Phase 4 stands at **$22.7780 of $25.00**.

## The finding: the probe, not the cap and not the instrument

F2's load-bearing assumption **held**. The boot went to the `info` handshake — 391.369 s of the
393.561 `billed_seconds` the gate saw — and neither warm-up call carried it (1.436 s and 0.756 s are
clean marginals). The gate counted what it was designed to count.

Its **input** was wrong. A generated 64×64 image prices nothing that a leaflet page costs: real
pages ran **3.54×** the warm-up page marginal. So the gate whose stated purpose is "never buy half a
pilot" projected $0.1936, passed the run, and the run bought **12% of one** (17 of 138 calls) before
the same arithmetic on real numbers stopped it.

That is a finding about the **probe**, and it is separable from both the cap (which behaved exactly
as (10)(c) and (10)(b) specify) and the instrument (which answered 16 of 17 page calls readably).

## The bars: none is scored, and the arithmetic that makes each unscoreable

- **Bar 1 (leaflet brand recall).** 17 of the registered **108** pages were bought. R2 fixes the
  denominator at exactly the 108 sent pages, so a numerator from a 17-page prefix over that
  denominator reads as a model that missed brands. No recall figure is computed here, not even as an
  aside.
- **Bar 3 (text tier accuracy).** **0** of the ≥20 adjudicated rows required by R5. The text leg
  never made a gold call.
- **Bar 2 (price-pair accuracy).** The dump exists and its n is reported, and nothing else:
  `results/sku_b_positions.jsonl`, sha256 `4178ce5e53559c8449bad90e48d750fd6c5b09142055329d3f1768be15109c22`,
  **14 rows**, **`price_pairs.n = 13`**. n=13 clears R4's ≥10 threshold — **but the pairs come from a
  17-page prefix of a 108-page registered population**, which is not the sample R4 describes.
  Whether "SCORED" applies is a team-lead ruling. The pair verdicts themselves are the team lead's
  read against the images (SPEC §10) in any case; this executor never scores its own sample.

What the 17 page answers contained: 14 positions, all at tier `position`, from 6 pages; 10 pages
answered `[]`; **1 page was a parse refusal** — `printed discount '-50%*' is not a percentage`. That
is 1 of 17 (5.9%, n=17). Asterisk-footnoted discounts are ordinary on Ukrainian retail leaflets, so
this is an instrument finding worth the team lead's eye — but R5's >10% rule governs bar 3, which
has zero rows, so this rate gates nothing today.

`population.unbought` lists **121** ids (138 − 17), all unique: 91 pages and all 30 text rows.

## What a v3 can and cannot be priced from

Measured this session: **boot 391.369 s = $0.1200 once**, **page gold 5.0772 s/call (n=17)**, **idle
tail 60 s = $0.0184**.

**Not measured: the text leg's gold marginal.** The only text number in existence is the 0.756 s
warm-up, and this session is the proof that a warm-up marginal does not price a gold call. A v3
registration that extrapolates the text leg from 0.756 s repeats the exact error that stopped this
run. (10)(a) hands the v3 to the team lead "under the measured price", and half of that price does
not exist yet.

The session's `worker-boot.log` is on the volume; a future staging pod can read the 391 s boot apart
for near-free, which is where the 2.2× regression against the historical cold start would be
diagnosed.

## Gate 7 — teardown, proven with the positive control

```
serverless delete 0yqlvm0b8wzzsw   → {"deleted": true}
template delete 90xcwcwtyu         → {"deleted": true}

template list --type user:
  unfcr3ja0t | market-pulse-5b-a      ← the positive control: the two 5b-era siblings SHOW,
  0g6zg73ptq | mp-5b-diag               so the listing is not empty by accident
  mine present? False

serverless list  → []
pod list -a      → []
network-volume   → qw4nwleanc mp-srv2 EU-RO-1 100   (the volume STAYS)
```

The same two ids were captured **before** the template was created, so the control is proven at both
ends.

The phase ledger, verbatim — including one false line, annotated rather than trimmed:

```
anchor            $35.00 at 2026-08-01T08:34:09+00:00
balance now       $12.23
  balance delta   $22.7675
  billing since   $22.5815 (read)
PHASE 4 SPENT     $22.7675 of $25.00
REMAINING         $2.2325
SKU-B SPENT      $0.0000 of $0.35  (anchor $12.23)      ← FALSE, see Dv151
anchored spend_sku-b.json for sku-b — commit it and never regenerate it
logged: sku-b-run: staging pod, POSITIONS endpoint, cap stop mid-page-leg at 17/138 …
```

## Verify

```
$ make check
1750 passed, 2 skipped in 53.53s

$ ruff format --check .
224 files already formatted
```

## Deviations

**Dv148 — the run was launched detached (`nohup` + PID watch), not in a single foreground call.**
Operator-approved before gate 2. The harness caps one Bash call at 600 s and the brief's own
estimate for Outcome B was 17–22 min, so the letter of "foreground, never `run_in_background`" could
not survive a completed run; a `nohup` process is neither harness-managed background nor killable by
the harness, which serves the prohibition's stated goal exactly. **Ex post it was not needed**: the
realized run was **538.272 s of wall** and would have fit one foreground call. The deviation was
insurance that this outcome did not cash in.

**Dv149 — the cap anchor was written before the staging pod, not at the driver's start.**
Operator-approved. Written by calling the driver's own `read_ledger`, so the file has one producer
and no hand-built fields. Without it the pod's cost sat outside (10)(a)'s "everything already
billed". It changed the budget from $0.35 to $0.3403 and, as shown above, **did not cause the
stop**.

**Dv150 — the staging pod was an RTX 2000 Ada at $0.24/h, not the runbook's ~$0.53/h class.** Gate 2
runs git and a sha check; no GPU work happens on it. The saving is inside a cap with no headroom.

**Dv151 — `runpod_guard.py --step sku-b` created a second, false anchor.** The guard derives its
step-ledger name from the step string, so `--step sku-b` wrote `results/spend_sku-b.json` (hyphen)
beside the driver's `results/spend_sku_b.json` (underscore). Its `runpod_balance_at_sku-b_start` was
today's POST-spend balance and its `step_spent_usd` was `0.0` — every number in it false, and a live
trap for the next session's cap arithmetic. It was read, then deleted while still untracked; the
phase-level line it logged into `results/spend_phase4.json` is correct and stands. The guard's
console line quoted above is that file's output and is false for the same reason.

**Dv152 — the overwrite guard sat above the `$0` dry run, and the suite reddened the moment the
paid artifacts existed.** `make check` was green before gate 5 and red after it:
`tests/test_positions_driver.py::test_the_dry_run_reaches_no_client_at_all` failed with
`results/sku_b_positions.jsonl already exists`. The guard is right to exist; its position was wrong,
because `--dry-run` writes nothing and the artifacts exist forever once bought — so the $0 path that
the run contract puts in its FIRST gate stops working the day it is first needed. Moved below the
early return (commit `dffd8d3`), still ahead of the registry read and long ahead of any client. Both
controls:

```
$ PYTHONPATH=src python3 scripts/positions_gm4_skub.py --dry-run
page leg   108 pages sent (of 159 available, 19 posts) in 7 job(s), largest 7.99 MB     ← works again

$ PYTHONPATH=src python3 scripts/positions_gm4_skub.py --endpoint-id NOPE
…/results/sku_b_positions.jsonl already exists — it is what a paid run bought.          ← still refuses
```

The fix was forced by the standing "`make check` green after every commit" rule, not chosen.

**Dv153 — `cost.jobs: 8` in the record is the PLAN, not what was billed.** The field is
`len(page_jobs) + len(text_jobs)` = 7+1, computed before the run. Four jobs actually ran (the `info`
handshake, two warm-ups, one page job), which the endpoint's own health read confirms
(`jobs.completed: 4`). **The artifact was not edited** — it is what the paid run wrote, and a record
that is corrected by hand stops being evidence. The defect is named here and belongs to a future
$0 pass.

## Assumptions

1. **The item this session did not buy is the text leg's price**, and I have not estimated it. Any
   number I could produce would come from the same warm-up that this run proved unrepresentative.
2. **`cost.usd` and the $0.1965 re-read are floors**, not settled costs; the settled figure will be
   visible in the next session's balance and may be higher.
3. **The 5.0772 s/call page marginal is measured on ONE job of 17 pages.** It carries that job's
   page mix; a different 17 pages could price differently.
4. **Nothing here rules on a bar.** The (10)(b) stop, the bar-2 n=13 on an unregistered prefix, the
   5.9% parse-refusal rate and the 2.2× boot regression are all facts handed to the team lead.
