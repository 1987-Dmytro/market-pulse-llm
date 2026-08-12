# sku-b-v4-run — the completing session: the 121 bought, the pilot closed by measurement

## Read-back

**Step 0.5 and the eight gates, one line each:**

0.5 **Dv170** — `scripts/sku_bar_verdicts.py`'s three v3 references move to v4: both defaults, and
   the provenance string it writes into the verdict record, now a constant pinned by a test.
1. **$0 gates** — `make check` 1824 green, preflight `EXIT=0 PASS 30 FAIL 0`, four listings clean,
   `--resume --dry-run` 91+30 in 6+1 under v4, and `results/spend_sku_b_v4.json` anchored at
   $11.9332 and committed before the first billing resource existed.
2. **The volume, staged before any endpoint** — `repo/` on `qw4nwleanc` moved `6811c74` → `ec9cf3b`
   by a bundle naming its real ref, reset to an explicit sha, with a before/after content control;
   pod deleted, proven.
3. **A NEW template** — `1baicjank8`, exactly three env variables and no fourth.
4. **The endpoint** — `goq8wqx92ambs8`, `ADA_24` · 1 worker · idle 60 · execution-timeout 900, every
   flag read back from the API's own answer.
5. **The run** — one invocation, detached, watched by PID: identity stop → the two REGISTERED
   warm-ups → go/no-go **proceed** → 6 page jobs → 1 text job, in-run gate between jobs, no stop.
6. **The outcome — COMPLETION**: `results/sku_b_positions_v4.{json,jsonl}` merged over 138 sources,
   and the bar-1/bar-3 verdicts through the fixed producer; bar 2 carries its n and no value.
7. **Teardown, proven** — endpoint then template deleted, the two 5b-era siblings still listed and
   mine absent, `serverless list` `[]`, `pod list -a` `[]`, the volume stays.
8. **Commits** — team-lead docs verbatim first, then the fix, the anchor, the run's artifacts, the
   verdicts, this report, the vault tail.

**The two (10) stop semantics, one line each:**

- **(10)(a) go/no-go** — priced before the first gold call; a refusal buys nothing, consumes NO
  attempt and comes home to the team lead. **It did not fire this session**: 121 gold calls projected
  **$0.5300** against **$0.6500** left of the cap.
- **(10)(b) mid-leg stop** — the in-run gate re-prices the whole run before every job but the first;
  a projection above what is left of the cap ends the run and is a team-lead ruling, never a silent
  continuation. **It did not fire either**: the six readings fell from $0.2685 to $0.2361.

**Each element bought exactly once across the program — nothing was re-asked.** The 121 the
registration lists as unbought were bought by this session; the 17 the first session paid for
(including its one parse refusal) entered the merged record as they stand, and every dump row names
the session that bought it in `bought_by`: 65 rows `sku-b-v4`, 14 rows `sku-b`.

**The Dv170 fix, in one line:** the string the team lead reads at acceptance now says
`docs/PROMPT-sku-b-v4-run.md step 6; docs/SPEC.md amendment 3.17 (6), (11), (12)` — the amendment the
second half of the population was bought under is no longer missing from the verdicts' own record.

---

## The outcome: completion, at 39% of the cap

| | |
|---|---:|
| population bought | **121 of 121**, merged to **138 of 138** |
| positions extracted | **79** (62 from pages, 17 from text) |
| unreadable replies | **5** of 138 (3.62%), four distinct reasons |
| empty answers | **102** |
| positions carrying a crossed-out price | **61** — bar 2's denominator, SCOREABLE under R4 |
| balance delta at the end / settled | **$0.2413** / **$0.2541** |
| cap | $0.65 |

**The bars, from code, over the merged population:**

```
$ PYTHONPATH=src python3 scripts/sku_bar_verdicts.py
results/sku_b_positions_v4.json — 138 elements, unbought 0
  leaflet_brand_recall       0.3603 vs 0.75   FAIL
  price_pair_accuracy             — vs 0.80   PENDING_TEAM_LEAD
  text_tier_accuracy         0.8621 vs 0.85   PASS
  bar 1 over 15 posts · micro 0.4727 · precision 0.9285714286
  bar 3 over 29 of 30 rows · 1 unreadable (3.3%)
  bar 2 n = 61 pairs, the team lead's read
wrote results/sku_bar_verdicts.json
```

Bar 1 is below its threshold. `attempts.on_failure` is registered and this report does not interpret
it: *"a failed bar closes B as 'instrument not ready' BY MEASUREMENT. No retry, no re-prompt, no
second draw."* Nothing was re-run, nothing re-prompted; the numbers are what the instrument returned.
**Bar 2 is not scored here and carries no value anywhere in this report** — SPEC §10.

---

## Gate 0.5 — the Dv170 debt, paid before anything billed

Commit `7033ba7`. Three references, and the reason only one of them was dangerous:

| what | was | now | guarded before? |
|---|---|---|---|
| `PREREG` | `results/sku_pilot_prereg_v3.json` | `results/sku_pilot_prereg_v4.json` | yes — a mismatched record is refused **by name** |
| `RECORD` | `results/sku_b_positions_v3.json` | `results/sku_b_positions_v4.json` | yes — same refusal |
| the `contract` string written INTO the verdict record | `docs/PROMPT-sku-b-v3-run.md step 6; … 3.17 (6), (11)` | `docs/PROMPT-sku-b-v4-run.md step 6; … 3.17 (6), (11), (12)` | **no — nothing re-derives a provenance string** |

It is a named constant now, and the test pins it against things that can move rather than restating
the literal: the registration's own `attempts.phase` (`sku-b-v4`), the contract file being in the
tree, the three amendment numbers present, and the superseded contract name absent.

**Its negative control**, because a pin that cannot fail is not a pin — the v3 string put back:

```
>       assert all(part in verdicts.CONTRACT for part in ("(6)", "(11)", "(12)"))
E       assert False
FAILED tests/test_sku_bar_verdicts.py::test_the_defaults_and_the_provenance_string_name_the_v4_session
1 failed, 20 deselected in 0.13s
```

**The residue, named rather than hidden.** `grep -n v3 scripts/sku_bar_verdicts.py` leaves exactly
two hits, both prose about history: the docstring of the new constant explaining what the v3 string
would have claimed, and the comment at the dump-path refusal recording that Dv162 was found on the
sku-b-v3 session. Neither is a path or a default.

---

## Gate 1 — the $0 gates

```
$ make check
1824 passed, 2 skipped in 55.48s          ← 1823 before gate 0.5; the one new row is its test

$ ruff format --check .
230 files already formatted               ← not in `make check`, so it is run separately
```

```
$ PYTHONPATH=src <peftvenv>/bin/python scripts/preflight_serving_guards.py
EXIT=0    PASS 30    FAIL 0
local   transformers 5.14.1 · peft 0.20.0 · torch 2.13.0
volume  transformers 5.14.1 · peft 0.20.0
```

**The Dv173 tax was not paid this time.** The scratch venv built in the v4-prep session survived, so
no rebuild was needed — the first time in four sessions. It is still a scratch venv outside the repo
and the next session may well rebuild it again.

The resume half of the preflight, verbatim — the four registration refusals, the (12)(b) constants
and their controls:

```
--- SPEC 3.17 (11)/(12): the resume ---

9. the registration          121 to buy, 17 already bought   <- the control: it ACCEPTS
   a moved dump pin                   REFUSE — the per-position dump hashes 4178ce5e53559c84… and results/sku_pilot_prereg_v4.json pins 0000000000000000… — the resume
   a moved serving pin                REFUSE — the serving pin hashes 5f900beb555f12f5… and the registration pins 0000000000000000… — SPEC 3.17 (11)(b) freezes the ins
   an unbought id with an answer      REFUSE — 1 id(s) the registration lists as UNBOUGHT already carry an answer in results/sku_b_positions.json — data/annotation/cap
   a moved (10)(a) refusal-record pin REFUSE — results/sku_b_positions_v3.json hashes 7196abfbf488168d… and results/sku_pilot_prereg_v4.json pins 0000000000000000…. Th

9b. the (12)(b) constants    cap, ledger and phase against the registration
    the registered set         ACCEPT   <- the control ($0.65 · sku-b-v4 · results/spend_sku_b_v4.json)
    the OLD ledger name        REFUSE — the run's constants do not match the registration — ledger: the run would use 'spend_sku_b_v3.json' and the registration
    the OLD cap                REFUSE — the run's constants do not match the registration — cap_usd: the run would use 0.45 and the registration names 0.65. SPE
    the OLD phase key          REFUSE — the run's constants do not match the registration — phase: the run would use 'sku-b-v3' and the registration names 'sku-
    read_ledger, for contrast  REFUSE — spend_sku_b_v3.json carries no runpod_balance_at_sku-b-v4_start — it is another phase's anchor. Spending against it woul

10. the selection            a bought id     REFUSE — the page leg selected 1 id(s) the first session already bought — data/annotation/captions_5c1/posts_media/atb_market_off
    an unbought id           1 kept   <- the control

11. the (11)(c) warm-up      atb_market_official_4476.jpg 0.32 MB · row @silposilpo:3370 (548 chars)   <- the control: ACCEPT
    a page inside the sent 108 REFUSE — data/annotation/captions_5c1/posts_media/atb_market_official_4340.jpg is one of the 108 SENT pages: the registered warm-
    a row inside the 30      REFUSE — @VARUS_channel:7119 is one of the 30 adjudicated rows: the registered warm-up row is inside bar 3's gold and 3.17 (9) op

12. the merged bar input     a source bought twice  REFUSE — 1 source(s) carry an answer from BOTH sessions — data/annotation/captions_5c1/posts_media/atb_market_official_4340.jpg….
    an unbought source       18 outcomes   <- the control
```

**The account, before anything of this session existed** — four listings, not two, because the
teardown control in gate 7 needs its *before* half captured before gate 3 creates mine:

```
$ runpodctl pod list -a                → []
$ runpodctl serverless list            → []
$ runpodctl template list --type user  → unfcr3ja0t | market-pulse-5b-a
                                         0g6zg73ptq | mp-5b-diag
$ runpodctl network-volume list        → qw4nwleanc  mp-srv2  EU-RO-1  100

balance $11.9332 · phase-4 anchor $35.00 · phase-4 spent $23.0668 of $25.00 · $1.9332 left
```

The dry run, under the v4 registration:

```
$ PYTHONPATH=src python3 scripts/positions_gm4_skub.py --resume --dry-run
page leg   91 pages sent (of 159 available, 19 posts) in 6 job(s), largest 7.99 MB
text leg   30 rows in 1 job(s)
dump       18 columns: item, page, file, sha256, brand_raw, brand_id, line, category, size, fat, price_promo, price_old, discount_pct_printed, price_qualifier, tier, depth, depth_disagrees_with_printed, bought_by
resume     SPEC 3.17 (11) under results/sku_pilot_prereg_v4.json
  bought    17 of 138 by results/sku_b_positions.json, never re-asked
  to buy    91 page(s) + 30 row(s) = 121 of 121 registered
  cap       $0.65 (12)(a) · phase sku-b-v4 · anchor results/spend_sku_b_v4.json
```

**The anchor, written before the first billing resource existed** (the Dv149 protocol), through the
driver's own `read_ledger` with the (12)(b) constants passed explicitly, and committed in `ec9cf3b`:

```json
{ "runpod_balance_at_sku-b-v4_start": 11.9332285148, "cap_usd": 0.65, "runs": [] }
```

The key is `runpod_balance_at_sku-b-v4_start`, which is the one the run reads — the module defaults
of `read_ledger` are the FIRST session's (`sku-b`, $0.35), so an anchor written on defaults would
have been refused by the run it was written for.

### The money geometry, computed before the staging pod, not after it

```
the registered probe, a deep unsent page        $0.5964 → $0.6143 with drift · headroom $+0.0357
the population's drawn marginal, 17 pages       $0.3218 → $0.3315 with drift · headroom $+0.3185
one more boot   $0.1235  → room for a second boot at the pessimistic corner: False
staging pod at $0.24/h = $0.00400/min → 8.93 min exhausts the pessimistic headroom
staging pod at $0.49/h = $0.00817/min → 4.37 min exhausts the pessimistic headroom
```

Two things follow, and both changed what was done next. **There is no room for a second boot at the
pessimistic corner** — so the recovery clause was treated as a decision that could only be taken
*after* reading the probe, never before it. And **staging-pod minutes come out of that $0.0357** — so
the pod was prepared for (bundle built, staging script written) before it was created, and it lived
under two minutes.

---

## Gate 2 — the volume, staged before any endpoint existed

Staging pod `yax8ck1ajwuip5`, **L4 at $0.49/h** (Dv177 — v3's $0.24/h class is not offered in
EU-RO-1 today), EU-RO-1, volume attached, `--terminate-after` an hour out. Rented **08:58:48 UTC**,
deleted **09:00:47 UTC** — **1 min 59 s by the pod's own clock**, an upper bound of **$0.0162**.

The content check has both halves, on the same two paths, and the fact chosen discriminates: the
producer's v4 string does not exist in the v3-era tree the last teardown left on the volume.

| | before | after |
|---|---|---|
| `git rev-parse HEAD` | `6811c74e0b9b…` (the sku-b-v3-run anchor commit) | `ec9cf3bda320…` |
| `grep -c 'sku-b-v4-run' scripts/sku_bar_verdicts.py` | **0** | **1** |
| `results/spend_sku_b_v4.json` | *No such file or directory* | present, 500 bytes |

The staging itself, verbatim — the bundle names its real ref and the reset targets an explicit sha,
so a fetch that moved nothing would have failed loudly instead of printing `Already up to date.`:

```
=== bundle heads (the REAL ref, not FETCH_HEAD) ===
ec9cf3bda3203859b0bbb3205c80491b39977b1f HEAD
=== fetch ===
From /workspace/mp-skub-v4.bundle
 * branch            HEAD       -> FETCH_HEAD
=== reset --hard to the Mac's exact sha ===
HEAD is now at ec9cf3b chore(sku-b-v4-run): anchor the ledger before anything bills
=== proof ===
ec9cf3bda3203859b0bbb3205c80491b39977b1f
(end of git status)
```

`start.sh` verified, not edited, and the prompt shas rendered on the volume itself — the serving pin,
re-derived on the filesystem the worker actually reads:

```
5b3bcbb2f59372f4cb3ee940caad5b5b4b90bb22adeff1f783f8c8301474b46c  /workspace/start.sh
5b3bcbb2f59372f4cb3ee940caad5b5b4b90bb22adeff1f783f8c8301474b46c  repo/scripts/start_5b_worker.sh

positions_post_gm4 ca6303c157d46e707aaf3fc52c7a05ed1450e24c26db0e7c93eefba4f6968754
positions_text_gm4 7250b87aa1c2de407e06ab9eed565dd4d88025add7be0d2d2a87607c0d872860
```

Both equal `results/sku_pilot_serving.json :: instruments`. Pod deleted, `pod list -a` → `[]`.

No boot-log work this time: the contract says the diagnosis is done, and the worker's own boot
measurement below is a better answer than a second reading of the same log would have been.

---

## Gates 3 and 4 — the template and the endpoint

Template `1baicjank8`, created new, exactly three variables and no fourth:

```json
"env": { "BASE_WEIGHTS": "google/gemma-4-31b-it",
         "MODEL_REVISION": "842da3794eaa0b77d5f08bae87a17459d91ff475",
         "SERVING_CONFIG": "POSITIONS" },
"dockerStartCmd": ["bash","-c","exec bash /runpod-volume/start.sh > /runpod-volume/worker-boot.log 2>&1"],
"isServerless": true
```

Endpoint `goq8wqx92ambs8`, every flag read back from the API's own answer:

```json
"executionTimeoutMs": 900000, "idleTimeout": 60, "workersMax": 1, "gpuIds": "ADA_24",
"networkVolumeId": "qw4nwleanc", "locations": "EU-RO-1", "flashBootType": "FLASHBOOT",
"templateId": "1baicjank8", "scalerType": "QUEUE_DELAY"
```

`executionTimeoutMs: 900000` equals the driver's `JOB_TIMEOUT_S` — (10)(c) holds at the endpoint as
well as in the client.

**The headroom re-checked immediately before `serverless create`**, with the pod priced from its own
clock rather than from the balance:

```
staging pod            1.983 min at $0.49/h = $0.0162
pessimistic corner  $0.5964 ($0.6143 with drift) + pod = $0.6305 against $0.65 → headroom $+0.0195
optimistic  corner  $0.3218 ($0.3315 with drift) + pod = $0.3477 against $0.65 → headroom $+0.3023
a second boot $0.1235 → still no room at the pessimistic corner

balance at that moment: anchor $11.9332 · balance $11.9332 · delta $0.0000
```

The balance had not moved at all — Dv166 again, and the reason the pod's own clock is the number
used here rather than a balance-derived "billed so far", which would have read $0.0000 and
overstated the headroom by exactly the pod.

---

## Gate 5 — the run

One invocation, launched detached (`nohup` + PID watch, pre-authorised) and watched by process, never
by `tail -f`:

```
--- tick 1 · 09:02:53 · pid=22334 · log 0 lines
--- tick 5 · 09:06:33 · pid=22334 · log 0 lines        ← the boot: the log is silent through it
--- tick 6 · 09:07:28 · pid=22334 · log 18 lines
--- tick 9 · 09:10:13 · pid=22334 · log 22 lines
--- tick 13 · 09:14:10 · pid=22334 · log 30 lines
--- tick 14 · 09:15:05 · pid=GONE · log 173 lines
PROCESS EXITED
```

The driver's console, verbatim and in the order the contract fixes:

```
ledger: spent $0.0000 of $0.65 (balance $11.93)
endpoint       goq8wqx92ambs8 · POSITIONS/base-no-adapter
  revision      842da3794eaa0b77d5f08bae87a17459d91ff475
  ceiling       800 new tokens, greedy, batch 1
  prompts       positions_post_gm4 ca6303c157d4… · positions_text_gm4 7250b87aa1c2…
  warm-up positions_post_gm4   stop  14.625s  ```json
[
  {
    "brand": "De Luxe Foods&Goods Se
  warm-up positions_text_gm4   stop  3.773s  [{"brand": "Молокія", "line": "Екстра", "category"
  go/no-go      121 gold calls project $0.5300 against $0.6500 left of the cap — proceed
  page job 00  17 item(s)  ok  7.70 MB
  after 17/121: 4.8881s/call · $0.0942 spent → $0.2685 projected
  page job 01  16 item(s)  ok  7.78 MB
  after 33/121: 5.1126s/call · $0.1204 spent → $0.2768 projected
  page job 02  17 item(s)  ok  7.79 MB
  after 50/121: 4.464s/call · $0.1371 spent → $0.2527 projected
  page job 03  14 item(s)  ok  7.74 MB
  after 64/121: 4.2907s/call · $0.1529 spent → $0.2463 projected
  page job 04  17 item(s)  ok  7.99 MB
  after 81/121: 4.4053s/call · $0.1781 spent → $0.2506 projected
  page job 05  10 item(s)  ok  5.61 MB
  after 91/121: 4.0161s/call · $0.1808 spent → $0.2361 projected
  text job 00  30 item(s)  ok  0.03 MB
```

The identity stop passed (the endpoint reported the pinned config and both prompt shas), the two
**registered** warm-up inputs were used and re-verified against their bytes, and the go/no-go ran
once, before any gold call.

### The go/no-go arithmetic, by hand

Every input is in `results/sku_b_positions_v4.json :: projection`; the rate is
`results/srv2d_cost.json :: rate.usd_per_second` = $0.00030669/s.

```
billed at the gate      223.916 s   (boot 205.518 + warm-ups 18.398)
gold_seconds            91 × 14.625 + 30 × 3.773 = 1330.875 + 113.190 = 1444.065 s
idle tail                60.000 s
                       ──────────
total                  1727.981 s × $0.00030669 = $0.5300
budget                                            $0.6500   →  proceed
```

**The boot halved.** 205.518 s against the refused session's 402.586 s on the same configuration —
$0.0630 instead of $0.1235. Nothing in this session set out to make that happen and nothing here can
prove why; the one structural candidate is the 112 s of cold network-volume shard reads the v3
boot-log diagnosis identified, which a volume read twice in twelve hours would not repeat. It is
recorded as a measurement of this boot, not as a new regime: two readings 2× apart are a spread, not
a trend.

### What the probe was worth, in the end

| probe | s/page | n | what it was |
|---|---:|---:|---|
| sku-b-run warm-up | 1.436 | 1 | a generated 64×64 image; the answer was `[]` |
| sku-b-run gold leg | 5.0772 | 17 | real pages, one job, 10 of the 17 answered `[]` |
| sku-b-v3-run warm-up | 14.808 | 1 | the registered unsent page — **the number that refused v3** |
| sku-b-v4-run warm-up | **14.625** | 1 | the same registered page, this session — it reproduces |
| **sku-b-v4-run gold leg** | **4.0161** | **91** | the population itself, across six jobs |

The registered probe **reproduces to 1.2%** — 14.625 against 14.808 — so it is a stable measurement
of that page. And the population it was standing in for costs **4.0161 s/page**: the probe
over-prices the thing it was chosen to price by **3.64×**. Both halves of that were visible before
today only as a disagreement between two samples; the completed leg is the first reading with n = 91
behind it. The text leg landed at **2.819 s/row** against the 3.773 s warm-up — the same direction,
1.34×.

This is what (11)(c) bought and what it cost: a representative probe stopped the run that would have
fitted, and (12)'s $0.65 cap is what let the same instrument finish for **$0.2541**.

---

## Gate 6 — the outcome and its artifacts

**Completion.** No (10)(a) refusal, no (10)(b) stop, no `JobExpired`, `ended_by: null`,
`population.unbought: []`.

| artifact | sha256 | what |
|---|---|---|
| `results/sku_b_positions_v4.json` | `fd0eb79695c2bc54…` | the merged record, 138 sources |
| `results/sku_b_positions_v4.jsonl` | `e7d24a0a6b5aeff1…` | the merged per-position dump, 79 rows |
| `results/spend_sku_b_v4.json` | — | the anchor and the run entry, written by `log_run` |
| `results/sku_bar_verdicts.json` | `e7fe6ae865e6a57d…` | bars 1 and 3 computed, bar 2 pending |

```
138 sources: pages 108 (82 empty · 22 answered · 4 unreadable)
             text  30 (20 empty ·  9 answered · 1 unreadable)
dump 79 rows: 62 from pages, 17 from text · bought_by: 65 sku-b-v4, 14 sku-b
61 rows carry a crossed-out price · depth disagrees with the printed % on 5 of 79
```

**The five unreadable replies, by their own reasons** — an unreadable reply and an empty answer are
different outcomes and are counted separately; none was re-asked:

```
atb_market_official_4342.jpg   printed discount '-50%*' is not a percentage   ← the first session's, entering as it stands
atb_market_official_4405.jpg   malformed JSON                                 ← and the only reply that hit the 800-token ceiling
atb_market_official_4446.jpg   size '6х100 г' is a multipack — a pack count is not a size
atb_market_official_4467.jpg   printed discount '-50%*' is not a percentage
@VARUS_channel:2119            price 'від 39,90 грн' is not one number
```

The asterisk-superscript family the team lead's calibration read found is here twice, exactly where
the (11)(b) freeze said it would be: it is a POST-pilot named revision, and this session did not
touch the prompts.

### Bar 1 — leaflet brand recall, 0.3603 vs 0.75, FAIL

Macro mean of per-post recall over the 15 posts with a non-empty gold set (R1), over the 108 SENT
pages (R2), with the 4 empty-gold posts excluded (R3).

| post | recall | gold | found | missed | unreadable pages |
|---|---:|---:|---:|---:|---:|
| `…:4377` | 0.0000 | 1 | 0 | 1 | 0 |
| `…:4391` | 0.0000 | 1 | 0 | 1 | 0 |
| `…:4411` | 0.0000 | 1 | 0 | 1 | 0 |
| `…:4421` | 0.0000 | 1 | 0 | 1 | 0 |
| `…:4446` | 0.0000 | 5 | 0 | 5 | 1 |
| `…:4498` | 0.0000 | 1 | 0 | 1 | 0 |
| `…:4340` | 0.3333 | 3 | 1 | 2 | 1 |
| `…:4401` | 0.4167 | 12 | 5 | 7 | 1 |
| `…:4436` | 0.5000 | 2 | 1 | 1 | 0 |
| `…:4467` | 0.5000 | 4 | 2 | 2 | 1 |
| `…:4381` | 0.5714 | 7 | 4 | 3 | 0 |
| `…:4350` | 0.6667 | 3 | 2 | 1 | 0 |
| `…:4508` | 0.6667 | 6 | 4 | 2 | 0 |
| `…:4360` | 0.7500 | 4 | 3 | 1 | 0 |
| `…:4426` | 1.0000 | 4 | 4 | 0 | 0 |

Beside it, and gating nothing: micro **0.4727** = **26 / 55**, precision **0.9286** = **26 / 28**.
Both denominators are (post, brand-key) PAIRS summed over the 15 scoreable posts, which is the
prereg's own word for the 55 — the gold's distinct key count is 27. **The instrument under-reads; it
does not mis-read**: of the 28 pairs it named on a scoreable post, **two** were not in the gold —
`raw:three bears` on `…:4340` and `raw:komo` on `…:4381` — against **29 gold pairs it never named**.
The **precision probe is clean** on top of that: on the four posts whose gold set is empty, the model
extracted **zero** brands, so it did not invent a dairy brand on a page of summer non-food.

Four of the 15 posts carry an unreadable page. Bar 1's registered reading has no unreadable clause —
only bar 3 does — so nothing is excluded and the exposure is reported: an unreadable page contributes
no brand to its post's union and costs recall exactly as an empty answer does.

### Bar 3 — text tier accuracy, 0.8621 vs 0.85, PASS

29 of 30 adjudicated rows scored; **1 unreadable (3.3%)**, under R5's 10% ceiling, excluded by its
reason and listed by id (`@VARUS_channel:2119`). Both carriers pooled as drawn.

```
confusion:  none → none 16 · position → position 9 · position → none 1 · product_mention → none 3
```

25 agreements over 29 rows = 0.8621. Every miss is in the same direction — the model returning fewer
rungs than the operator's ticks, never more — which is the same under-reading bar 1 measures on
pages.

### Bar 2 — the denominator, and nothing else

**n = 61 pairs**, class **SCOREABLE** under R4 (`n >= 10`). The dump carries one row per extracted
position with its page, that page's file and sha256, both prices and the code-assigned tier, which is
what makes the team lead's read possible without re-running anything. **No accuracy figure for bar 2
appears in this report, in the verdict record, or in the run record** — the executor never scores its
own sample (SPEC §10).

---

## Gate 7 — teardown, proven with the positive control

```
serverless delete goq8wqx92ambs8   → {"deleted": true}
template delete 1baicjank8         → {"deleted": true}

template list --type user:
  unfcr3ja0t | market-pulse-5b-a      ← the positive control: the two 5b-era siblings SHOW,
  0g6zg73ptq | mp-5b-diag               so the listing is not empty by accident
  mine present? False

serverless list  → []
pod list -a      → []
network-volume   → qw4nwleanc mp-srv2 EU-RO-1 100   (the volume STAYS)
```

The same two template ids were captured in gate 1, before gate 3 created mine, so the control holds
at both ends.

---

## The three cost readings, kept distinct

| reading | value | what it is |
|---|---:|---|
| billed seconds × rate | **$0.2251** | 673.944 worker s + 60 s idle tail at $0.00030669/s — the reading that does not wait for the account |
| \+ the staging pod | **≈ $0.2413** | ≤ 1.983 min at $0.49/h ≤ $0.0162 on top, priced by the pod's own clock |
| balance delta at the end of the run | **$0.2413** | a FLOOR (Dv33), read by the driver at 09:14:58 |
| balance delta, settled (09:25:34) | **$0.2541** | $0.0128 above the first read |
| the cap | $0.65 | **$0.3959 left**, and the population complete |

The billed-seconds reading and the balance delta agreed to four decimal places at the moment the run
ended, which is a coincidence of two floors meeting rather than a corroboration — ten minutes later
the balance had moved $0.0128 further and the billed-seconds reading had not. Two terms account for
most of that gap and both are standing costs rather than this session's: the 100 GB volume bills
continuously — **≈ $0.012/h measured across the 9.7 h idle window between the v3 teardown's settled
$12.0499 and this session's $11.9332 anchor**, which brackets the $7/month list price of 100 GB — so
the session's ~0.45 h of wall clock carries ≈ $0.005 of volume, and the rest is the tail of a floor
that had not finished settling. `results/spend_sku_b_v4.json :: runs` carries the entry the driver's
own `log_run` appended on the completion exit; its `step_spent_usd` is the $0.2413 read at the time,
which is why the settled $0.2541 is stated here rather than written over it.

Phase 4: `$23.3209 of $25.00` spent at the settled reading, `$1.6791` left.

---

## Verify

```
$ make check
1824 passed, 2 skipped in 55.23s

$ ruff format --check .
230 files already formatted
```

**The sealed artifacts, hashed before this session's first write-capable action and again after the
run** — identical both times, so nothing this session did touched them:

```
8d02b3aa477dd4b1…  results/sku_b_positions.json        4178ce5e53559c84…  results/sku_b_positions.jsonl
7196abfbf488168d…  results/sku_b_positions_v3.json     22fd7d9cc363ac93…  results/sku_pilot_prereg_v4.json
5e706e4f607846dc…  results/spend_phase4.json           46f0d4d396476555…  results/baselines.json
973c87890ad049d5…  docs/SPEC.md (the registered law, ratification blocks stripped)
```

### The per-commit checkout table

Stashed first (3 dirty vault paths), each commit checked out and running its OWN suite, HEAD printed
from `git rev-parse` rather than from the loop variable, stderr never swallowed. The parent is the
control for the checker's own bias.

| # | commit | what | fact at that commit | `make check` |
|---|---|---|---|---|
| — | `2fc88ae` | CONTROL (parent) | `docs/PROMPT-sku-b-v4-run.md` present? **no** | 1823 passed, 2 skipped |
| 1 | `910c4b6` | team-lead docs | `v4-prep ✅` ×1 in STATUS · `sku-b-v4-run` ×0 in the bar producer | 1823 passed, 2 skipped |
| 2 | `7033ba7` | Dv170 | `sku-b-v4-run` ×1 · both defaults read `…_v4.json` | 1824 passed, 2 skipped |
| 3 | `ec9cf3b` | the anchor | `11.9332285148 · 0.65 · 0 run(s)` | 1824 passed, 2 skipped |
| 4 | `fd4bf67` | the run's artifacts | `asked 138 · unbought 0 · positions 79 · $0.2413` | 1824 passed, 2 skipped |
| 5 | `e579382` | the verdicts | `FAIL · PENDING_TEAM_LEAD · PASS` | 1824 passed, 2 skipped |
| 6 | `8107ceb` | this report | `Dv176`…`Dv180` ×5 in `docs/reports/sku-b-v4-run.md` | 1824 passed, 2 skipped |
| 7 | `8a2c28f` | the vault tail | `sku-b-v4-run ✅ ЗАВЕРШЁН` ×1 in `knowledge/hot.md` | 1824 passed, 2 skipped |
| 8 | `483e4da` | this table's rows 6–7 | 4 hits for the two rows above | 1824 passed, 2 skipped |

Restored at `e579382` for the first pass with the same 3 dirty vault paths; rows 6–8 were checked out
afterwards on a clean tree, which is why they need no stash. **The table stops one commit short of
itself and always will** — a report cannot check out the commit that carries it, and the contract
pre-authorises the extra commit (the Dv175 reading). Commits 9–11 are in the commits table below:
they change prose only, no code, and each ran `make check` on its working tree before it landed.

The parent's 1823 is the baseline that says the growth is this phase's, and the one row it grows by
is gate 0.5's provenance test.

---

## Deviations

**Dv176 — the driver's own `contract` string has the defect Dv170 named, and it is not fixed here.**
`results/sku_b_positions_v4.json :: contract` reads `docs/PROMPT-sku-b-v3-prep.md deliverable 2;
docs/SPEC.md amendment 3.17 (9), (10), (11)`. The file it names is true as the builder's provenance —
the resume mode WAS built in v3-prep deliverable 2 — but the amendment list stops at (11) and this is
a v4 artifact: (12) is the clause its cap, ledger and phase come from. Not moved: step 0.5 is scoped
by name to `scripts/sku_bar_verdicts.py`, and the driver is the money path — editing the schema of
the record a paid session is about to write is the in-flight edit the (11)(b) freeze exists to stop.
Checked before naming it: `grep -rn '\["contract"\]'` over `scripts/`, `src/` and `tests/` finds no
consumer, so nothing downstream reads the field and the exposure is a reader's, exactly as Dv170's
was. The honest place for it is the next contract that touches the driver.

**Dv177 — v3's $0.24/h staging class is not offered in EU-RO-1 today, and the cheapest replacement
is double.** `runpodctl gpu list` returns no RTX 2000 Ada at all; the cheapest EU-RO-1 class with
stock is L4 at **$0.49/h** (RTX 4000 Ada at $0.28 shows `stockStatus: none`). Against the pessimistic
corner's $0.0357 headroom that halves the time a staging pod may live — 4.37 min instead of 8.93 —
which is why the bundle and the staging script were prepared before the pod was created and the pod
lived 1 min 59 s. The staging tax is now a term that has to be checked against the headroom of the
day, not a constant carried from a previous report.

**Dv178 — 55 seconds of the staging pod were spent polling for an SSH host key that was already
there.** The readiness loop grepped `runpodctl ssh info` for `"host"` and the tool's key is `"ip"`,
so the loop ran its full ten iterations against an answer that was complete on the second. It cost
≈ $0.0075 of a $0.0357 headroom and nothing else; named because it is the same class of mistake as
grepping a log for a success marker that never appears — the check has to match the thing it reads,
and a loop with no positive exit looks exactly like a slow resource.

**Dv179 — the boot halved and this report does not claim to know why.** 205.518 s against the refused
session's 402.586 s on the same template shape, same GPU class, same volume. The v3 boot-log
diagnosis attributed 112 s to a cold read of 1188 shards off the network volume, and a volume read
twice inside twelve hours is the one structural candidate; but this session copied no boot log (the
contract says the diagnosis is done) and two readings 2× apart are a spread, not a trend. It is
recorded as a measurement, and every projection in `results/sku_projection_v4.json` remains priced at
the full 402.586 s, which is the conservative direction.

**Dv180 — the registered probe reproduces and the population still costs a quarter of it.** 14.625 s
against v3's 14.808 s on the same page is a 1.2% spread, so (11)(c)'s probe is a stable measurement;
the completed page leg is 4.0161 s/page over n = 91. The probe is not noisy — it is a correct
measurement of a page that is 3.64× denser than the population's mean, which is what "one real UNSENT
page" selects for by construction, since the sent set is the first six pages of each leaflet. This is
not a defect to fix inside this contract and it is the number a future registration should price
from: the go/no-go's estimator is unbiased for the probe and biased against the run.

---

## Assumptions

1. **The 60 s idle tail is billed after the last job.** It is inside the go/no-go, inside the in-run
   gate and inside the billed-seconds reading above. If RunPod stopped billing the tail, those
   numbers are $0.0184 high.
2. **$0.00030669/s is still the rate.** Read from `results/srv2d_cost.json :: rate.usd_per_second`,
   settled, and not re-derived — this session's own balance is a floor and cannot separate the
   worker's seconds from the volume's hours.
3. **The staging pod is priced from its own clock, not from the balance** (Dv166). 1 min 59 s from
   `pod create` to `pod delete` is an upper bound on billed pod time, used as one.
4. **The volume's ≈ $0.012/h is an inference from two balance readings**, not a rate this repository
   measures. It is derived from a 9.7 h window in which nothing else of ours ran, and it is used only
   to explain why the settled delta exceeds the billed-seconds reading — no projection depends on it.
5. **`bought_by` is what separates the two sessions in the merged artifacts.** Every outcome in the
   record carries a `leg`, including the 17 the first session bought, so the leg field cannot be used
   to tell the sessions apart and the count 65 + 14 in the dump comes from `bought_by` alone.
6. **Bar 1's gold is one reviewer's reading** (SPEC 3.16 (1) REVIEW class), so the precision figure
   beside the recall is reported and gates nothing: a brand the pilot found and the reviewer did not
   is not evidence of a false positive.

---

## Commits

| # | commit | subject |
|---|---|---|
| 1 | `910c4b6` | `docs(team-lead)`: the sku-b-v4-run contract and STATUS — committed unedited |
| 2 | `7033ba7` | `fix(sku-b-v4-run)`: Dv170 — the bar producer's three v3 references move to v4 |
| 3 | `ec9cf3b` | `chore(sku-b-v4-run)`: anchor the ledger before anything bills |
| 4 | `fd4bf67` | `feat(sku-b-v4-run)`: the completed session — 121 bought, the merged record and dump |
| 5 | `e579382` | `feat(sku-b-v4-run)`: the bar-1 and bar-3 verdict records over the merged population |
| 6 | `8107ceb` | `docs(report)`: sku-b-v4-run |
| 7 | `8a2c28f` | `chore(vault)`: the sku-b-v4-run tail — the day's log, hot.md, the index |
| 8 | `483e4da` | `docs(report)`: sku-b-v4-run — the checkout table's own tail |
| 9 | `fbaae0d` | `docs(report)`: sku-b-v4-run — bar 1's false-positive count, factored from the record |
| 10 | `da5791a` | `docs(report)`: sku-b-v4-run — commit 8's row, and the rule that ends the regress |
| 11 | — | `docs(report)`: sku-b-v4-run — the last row, which is this one |

Eleven commits, and **the last row can never carry its own sha** — a report cannot name the commit
that carries it, which is why row 11 is blank rather than wrong. Rows 9–11 change prose only, no
code; the suite on each of their working trees is the `make check` under Verify above, run before
each was committed. The vault tail is commit 7 rather than the last, for the reason Dv175 gave in the
previous report and this contract pre-authorises. Commit 9 is a correction, not a tail — `micro
0.4727` factors as 26/55 and `precision 0.9286` as 26/28, so bar 1's false-positive count is two, and
the first draft of this report said one.

---

# Close — bar 2 applied, the pilot closed by measurement ($0)

`docs/PROMPT-sku-b-close.md` · executor · 2026-08-12 · **no paid calls, no RunPod resources**

## Read-back

**The four deliverables, one line each:**

1. **The applier** — `scripts/apply_sku_pair_verdicts.py` carries the 45 dictated keys as its own
   data, joins them to the sealed dump's 61 pair rows exactly once each, and writes
   `results/sku_b_pair_verdicts.json`; it refuses on any checksum miss, any unmatched or
   doubly-matched row, and on the two verdict flips the counts cannot see.
2. **The verdict record, finalised** — `scripts/sku_bar_verdicts.py` consumes that file (pinned by
   sha, over the same dump), bar 2 becomes **0.3279 vs 0.80 — FAIL (n=61, read by the team lead
   2026-08-12)**, bars 1 and 3 are unchanged to the digit, and the `closure` block quotes
   `attempts.on_failure` out of the registration.
3. **The ADR** — `knowledge/decisions/sku-b-pilot-closed-by-measurement.md` plus its INDEX row: three
   bars, the diagnosis, the under-reading evidence, the gold-vs-instrument mismatch, the four probe
   numbers, $0.6032 over three sessions, and three named revision CANDIDATES.
4. **Depth-from-percent** — `scripts/measure_depth_from_pct.py` prices the badge and the extracted
   old price against the team lead's own `printed_old` on all 61 pairs into
   `results/sku_depth_from_pct.json`; no threshold is registered and the adequacy rule is stated in
   the record as the script's own.

**The three bars:** brand recall **0.3603 vs 0.75 FAIL** · price-pair accuracy **0.3279 vs 0.80
FAIL** · text tier accuracy **0.8621 vs 0.85 PASS** → **CLOSED — instrument not ready, BY
MEASUREMENT** (2 of 3 bars failed).

**No paid calls in this contract.** No endpoint, no template, no pod, no network-volume operation,
no model request of any kind: every number below is arithmetic over files that were already on disk.

---

## Deliverable 1 — the applier

```
$ PYTHONPATH=src python3 scripts/apply_sku_pair_verdicts.py
results/sku_b_positions_v4.jsonl — 61 pair rows over 45 keys, each matched once
  correct 20 · wrong 41 · accuracy 0.3279 (20/61)
  promo price 61/61 correct · printed % 61/61 correct · crossed-out old price 20/61 — every error is confined to the small struck-through number (superscript kopiyky garbled, truncated to .0, or digit-shifted), and depth() is wrong wherever the old price is.
wrote results/sku_b_pair_verdicts.json
```

The join is the deliverable, not the arithmetic. A key is `(file, price_promo, price_old)` and `n`
is how many dump rows carry it — duplicates share one physical price box and therefore one verdict.
Every dictated key had to find its rows, every dump pair row had to be claimed once, and the file
suffix the table writes (`…4341.jpg`) is resolved against the dump rather than expanded in the
script, so a suffix that reached two pages would be a refusal instead of a silent pick.

**`EXPECTED` is the contract's own checksum line, transcribed — not computed from `DICTATED`.** A
checksum derived from the thing it checks agrees with every typo in it. The four counts
(45 / 61 / 20 / 41) and `0.3279` are therefore an independent statement the joined table has to
satisfy.

**The refusal the counts cannot see.** Flip one `correct` row to `wrong` and one `wrong` row to
`correct` and 20/41 still holds. The only field that has to move with the verdict is `printed_old`:
a `wrong` key must carry one AND it must differ from the dump's old price; a `correct` key must
carry none, and the record fills it from the dump (for a correct pair the dump's old price IS the
printed one, which is what makes deliverable 4 possible). Both directions are asserted, both are
tested.

### The guards, driven live — refusals with a positive control

```
$ … --record <a record re-pinned to a dump missing one pair row>
refused: 4341.jpg 37.9/75.9 was ruled on and no dump row carries it
exit=1

$ … --dump <that same short dump, against the REAL record's pin>
refused: …/dump_short.jsonl hashes 1dafcd286c4705ca… and results/sku_b_positions_v4.json pins
         e7d24a0a6b5aeff1… — these are not the pairs that were bought
exit=1

$ PYTHONPATH=src python3 scripts/sku_bar_verdicts.py --pairs <a read with a hand-edited accuracy>
refused: 20/61 rounds to 0.3279 and the read states 0.85
exit=1

$ …the same three commands against the sealed inputs
exit=0    exit=0                                    ← the positive control at the other end
```

The first two are the same tampered dump and they refuse for **different reasons on purpose**: the
sha pin fires first and would shadow the join guard, so the first run re-pins the record to reach
the join. A guard that is only ever exercised behind another guard has not been exercised.

### Bar 2 by page — it is not one bad page

| page | correct | rows |  | page | correct | rows |
|---|---:|---:|---|---|---:|---:|
| `…4341.jpg` | 1 | 2 | | `…4402.jpg` | 1 | 1 |
| `…4343.jpg` | 1 | 1 | | `…4403.jpg` | 1 | 1 |
| `…4344.jpg` | 0 | 1 | | `…4404.jpg` | 2 | 6 |
| `…4350.jpg` | 0 | 1 | | `…4426.jpg` | 0 | 3 |
| `…4352.jpg` | 0 | 2 | | `…4427.jpg` | 0 | 2 |
| `…4360.jpg` | 4 | 6 | | `…4428.jpg` | 0 | 4 |
| `…4381.jpg` | 0 | 2 | | `…4440.jpg` | 0 | 3 |
| `…4382.jpg` | 2 | 4 | | `…4468.jpg` | 0 | 3 |
| `…4383.jpg` | 3 | 3 | | `…4470.jpg` | 0 | 1 |
| `…4384.jpg` | 0 | 2 | | `…4471.jpg` | 0 | 2 |
| `…4385.jpg` | 0 | 4 | | `…4508.jpg` | 5 | 7 |

**22 pages, 20 correct rows of 61.** Four pages are clean (`4343`, `4383`, `4402`, `4403`, 6 rows
between them), **thirteen have not one correct pair**, and five are mixed. A failure concentrated on
one leaflet would be a page problem; spread over 18 of 22 pages it is the instrument.

---

## Deliverable 2 — the verdict record, finalised

```
$ PYTHONPATH=src python3 scripts/sku_bar_verdicts.py
results/sku_b_positions_v4.json — 138 elements, unbought 0
  leaflet_brand_recall       0.3603 vs 0.75   FAIL
  price_pair_accuracy        0.3279 vs 0.80   FAIL
  text_tier_accuracy         0.8621 vs 0.85   PASS
  bar 1 over 15 posts · micro 0.4727 · precision 0.9285714286
  bar 3 over 29 of 30 rows · 1 unreadable (3.3%)
  bar 2 over 61 pairs, the team lead's read — 0.3279 vs 0.80 — FAIL (n=61, read by the team lead 2026-08-12)
  closure: CLOSED — instrument not ready, BY MEASUREMENT (2 of 3 bars failed: leaflet_brand_recall, price_pair_accuracy)
wrote results/sku_bar_verdicts.json
```

**Bars 1 and 3 are unchanged to the digit** — `0.3603174603` and `0.8620689655`, the same values the
Gate 6 section above reports. Nothing in this contract touched the dump, the run record, the
registration or the sealed pairs.

**The share is re-derived, never read.** `bar_two` calls the applier's own `checksums` over the read
file's `keys`; it does not take `accuracy` out of the JSON. One implementation, two callers, and the
third refusal above is what that buys — a hand-edited accuracy field is caught by the read's own
stated counts. Two further refusals guard it: a read taken over a different dump, and a read whose
row count is not the bar's denominator (a bar scored over a sample of a sample).

**The closure is derived, and the rule is quoted.** `closure()` reads
`results/sku_pilot_prereg_v4.json :: attempts.on_failure` verbatim rather than restating it, and
names the failed bars from the computed verdicts — the registered sentence says "**a** failed bar"
in the singular and the pilot failed two, so the list has to come from the data. A bar still without
a verdict makes the state `UNDETERMINED`, never a closure taken on two thirds of the evidence.

```
"closure": {
  "rule": "a failed bar closes B as 'instrument not ready' BY MEASUREMENT. No retry, no re-prompt,
           no second draw: a bar re-run after its own result is not the bar that was registered",
  "failed_bars": ["leaflet_brand_recall", "price_pair_accuracy"],
  "passed_bars": ["text_tier_accuracy"],
  "state": "CLOSED — instrument not ready, BY MEASUREMENT"
}
```

---

## Deliverable 4 — depth from the printed percentage ($0, and it changes the reading)

```
$ PYTHONPATH=src python3 scripts/measure_depth_from_pct.py
results/sku_b_positions_v4.jsonl — 61 pairs against the team lead's printed_old
  badge                median 0.2886 pp · max 1.4171 pp · ≤1pp 60/61 · ≤2pp 61/61
  extracted_old_price  median 0.1761 pp · max 1.6366 pp · ≤1pp 56/61 · ≤2pp 61/61
wrote results/sku_depth_from_pct.json
```

| instrument | median \|Δ\| | max \|Δ\| | mean signed Δ | ≤ 1 pp | ≤ 2 pp | outside 1 pp |
|---|---:|---:|---:|---:|---:|---|
| the printed `-N%` badge | **0.2886 pp** | **1.4171 pp** | −0.3425 pp | 60/61 | **61/61** | `…4404` 26.5 (−1.4171) |
| the extracted old price | **0.1761 pp** | **1.6366 pp** | −0.1661 pp | 56/61 | **61/61** | `…4428` ×2, `…4427` ×2, `…4468` ×1 |

**The third column is the finding.** The brief's hypothesis — the badge reads 61/61 and the old
price 20/61, so question 7's depth may not need the old price at all — is only half right. Every
dictated error is kopiyky-scale (`230.0` where the page prints `230.90`, a 0.4% error on the old
price), and depth is insensitive to that: **the old price the pipeline already extracts is inside
2 pp on all 61 pairs too**, and beats the badge in the median. Dropping it would buy no accuracy.

The plain reading, computed from the two summaries rather than written down:

> the badge IS an adequate depth instrument for a weekly median (median 0.29 pp, max 1.42 pp, 61/61
> within 2 pp) — and the old price the pipeline already extracts also is (0.18 pp median, 1.64 pp
> max), because every error the team lead found is in the kopiyky and depth barely moves on them.
> **Bar 2 fails on the printed NUMBER; on this population it does not fail on the DEPTH that number
> is used for.**

**No threshold is registered.** The adequacy rule the sentence reads against — every pair within
2 pp AND the median within 1 pp — is stated inside the record as this script's own. It is a
measurement for the B′ design session, not a bar, and the real threshold is the operator's.

**The arithmetic has a control.** `measure_depth_from_pct.depth` is a second place `(old − promo)/old`
is written, so the suite asserts it against the `depth` the dump's own producer
(`positions.Position.depth`) wrote, on every one of the 20 pairs where the printed and extracted old
prices are the same number. A drift between the two implementations reddens the suite.

---

## Deliverable 3 — the ADR

`knowledge/decisions/sku-b-pilot-closed-by-measurement.md`, with its row appended to
`knowledge/decisions/INDEX.md` (which is ordered ascending by date, so it is the last row, not the
first). It carries the three bars, the diagnosis verbatim, the four pieces of under-reading evidence
(precision 0.9286 = 26/28 against 29 gold pairs never named · a clean empty-gold probe · every bar-3
miss downward · transcription-scale price errors), the gold-vs-instrument mismatch **with the fact
under it and without claiming it as a measured cause**, the programme's cost and what each stop
bought, the probe in four numbers, and three revision CANDIDATES marked as candidates.

---

## Verify

```
$ ruff format --check .
234 files already formatted                ← not in `make check`, so it is run separately

$ make check
1854 passed, 2 skipped in 56.29s           ← 1824 before this contract; the 30 new rows are its tests
```

**The immutables did not move.** Hashed before the first write of this session and again after the
last:

| file | sha256 | |
|---|---|---|
| `results/sku_b_positions_v4.json` | `fd0eb79695c2bc54…` | unchanged |
| `results/sku_b_positions_v4.jsonl` | `e7d24a0a6b5aeff1…` | unchanged |
| `results/sku_pilot_prereg_v4.json` | `22fd7d9cc363ac93…` | unchanged |
| `results/spend_sku_b_v4.json` | `d88b28a0085dedca…` | unchanged |
| `results/sku_reference_leaflet.json` | `e301bb4f48f527e4…` | unchanged |

**What this contract wrote:**

| file | sha256 |
|---|---|
| `results/sku_b_pair_verdicts.json` | `a61f1dce0ff3a13e…` |
| `results/sku_bar_verdicts.json` | `bb95f369d352f5fa…` |
| `results/sku_depth_from_pct.json` | `23cb7215ae63e252…` |

### Per-commit checkout table

Each commit checked out into the working tree, `HEAD` printed by `git rev-parse`, one content fact
read off that tree, and **that commit's own suite** run on it. The parent `06617c8` is the control
for the checker's own bias.

| # | commit | HEAD | content fact | ruff | its own suite |
|---|---|---|---|---|---|
| 0 | parent (control) | `06617c8` | new files present: **0** | clean | **1824 passed**, 2 skipped |
| 1 | team-lead docs | `0b103ec` | dictated rows in the contract: **45** | clean | **1824 passed**, 2 skipped |
| 2 | the applier | `4bfd391` | `DICTATED` **45** rows · `EXPECTED` **61** / **0.3279** | clean | **1839 passed**, 2 skipped |
| 3 | the read applied | `2fae1c2` | pair record: **20 / 61 = 0.3279** | clean | **1839 passed**, 2 skipped |
| 4 | the consumer | `5b2a649` | `closure()` present · `bar_two` takes **5** parameters | clean | **1845 passed**, 2 skipped |
| 5 | the verdict record | `20ac6dd` | bar 2 **FAIL** · failed bars **[recall, price-pair]** | clean | **1846 passed**, 2 skipped |
| 6 | depth-from-percent | `0f1e43e` | **61** pairs · badge adequate **True** · extracted adequate **True** | clean | **1854 passed**, 2 skipped |
| 7 | the ADR | `fa7f3df` | ADR tracked **1** · INDEX row **1** | clean | **1854 passed**, 2 skipped |
| 8 | this report | `c10f641` | `##` headings in the file: **23** | clean | **1854 passed**, 2 skipped |
| 9 | the vault tail | `043dfe6` | the two priced literals in `hot.md`: **3** and **3** | clean | **1854 passed**, 2 skipped |

The row counts climb 1824 → 1839 → 1845 → 1846 → 1854 in exactly the places tests were added, and
the control at the top proves the checker is not simply reporting today's tree ten times.

**Commit 5 carries one test beside the record** — see Dv186. **Commit 9 is checked out and run like
the rest, not waved through as prose**: `knowledge/hot.md` is grepped as a priced input by
`scripts/volume_calc_5c1.py`, so a vault commit can redden nine tests, and the content fact for that
row is the two literals it needs.

---

## Deviations

**Dv181 — the brief's "$0.62" and the ledgers' $0.6032.** `docs/PROMPT-sku-b-close.md` deliverable 3
asks for "the program's cost $0.62 over three sessions". The three settled balance deltas are
**$0.1965** (`sku-b`) **+ $0.1526** (`sku-b-v3`) **+ $0.2541** (`sku-b-v4`) = **$0.6032**, each of
them a floor (Dv33) read from its own session's report. The ADR states $0.6032 with the three
components and names the brief's figure beside it. The gap is $0.0168 and changes nothing; the
number in the ADR is the one that can be walked back to a ledger.

**Dv182 — the depth measurement qualifies the last clause of the diagnosis line, which is carried
verbatim anyway.** The team lead's line ends *"and depth() is wrong wherever the old price is"*.
That is arithmetically true and the magnitude is **≤ 1.6366 pp on every one of the 61 pairs**, with
a median of 0.1761 pp — so on this population the extracted old price is as adequate a depth
instrument as the badge (deliverable 4). The dictated line is **not edited**: it goes into
`results/sku_b_pair_verdicts.json :: diagnosis`, into the ADR and into this report exactly as
written, and the qualification is stated as a separate measurement beside it. A dictation is
transcribed, never improved.

**Dv183 — a wrong deviation cross-reference in this report, fixed in place.** The Gate 2 section
cited "Dv176" for the L4 staging class; the deviations list numbers that **Dv177** and Dv176 is the
driver's `contract` string. One word, no number, nothing derives from it, and it is corrected rather
than footnoted.

**Dv184 — the Gate 6 artifact table's sha for `results/sku_bar_verdicts.json` no longer matches the
file on disk, and is left as it stands.** That table records what the **v4-run** produced
(`e7fe6ae865e6a57d…`, bars 1 and 3 computed and bar 2 pending), which is a true statement about that
session and the evidence that bar 2 carried no value before the read. The rewritten record's sha is
in the Verify block above. Re-pinning the historical row would erase the only witness that the two
writings are different files.

**Dv185 — Dv176 stays open.** `scripts/positions_gm4_skub.py` still writes
`docs/PROMPT-sku-b-v3-prep.md deliverable 2; … 3.17 (9), (10), (11)` into every run record's
`head.contract`, omitting (12). This contract's Do-NOT list forbids touching the run records and does
not authorise touching the driver, and no consumer reads that field (grepped in the previous
session). It is a reader's exposure and it is still logged.

**Dv186 — "the verdict record in its own commit" carries one test with it.** Deliverable 2 asks for
`results/sku_bar_verdicts.json` re-written in its own commit. The test that pins the shipped record
(`test_the_shipped_run_has_a_read_to_score_and_does_not_fall_back_to_pending`) asserts on that file's
contents, so committing it one commit earlier would leave commit 4 with a red suite of its own — the
rule that every commit must pass its own tests. The test therefore ships in commit 5 beside the
record it pins, and commit 5 contains nothing else.

---

## Assumptions

1. **The dictated table is authoritative and was not checked against a page image.** SPEC §10 runs
   both ways: the executor never scores its own sample and never second-guesses the team lead's
   read. `printed_old`, the verdicts and the four checksums are transcribed; what was verified is
   that they are internally consistent and land on the dump exactly once.
2. **`n` means "dump rows sharing one physical price box".** The contract says so and the join
   confirms it: 45 keys expand to exactly the 61 pair rows the dump carries, with no row left over
   and none claimed twice.
3. **A missing read puts bar 2 back to PENDING rather than refusing.** `--pairs` defaults to the real
   file; if it went missing the producer would still write a record, with bar 2 pending and the
   closure `UNDETERMINED`. That is the state the bar was in for the whole pilot and is not an error
   — so the guard is a test asserting the file exists and that the record on disk is the scored one.
4. **The adequacy rule in deliverable 4 is this session's, not a registration.** Stated inside the
   record, named in the reading line, and repeated here so no later reader can mistake it for a
   pre-registered bar.
5. **The three session costs are settled balance deltas, each a floor** (Dv33). No new balance was
   read this session — nothing billed — so the programme total is as settled as the three reports
   left it.
6. **`graphify update .` was run after the code changes**, per CLAUDE.md. `graphify-out/` is
   gitignored, so it is not evidence and appears in no commit.

---

## Commits

| # | commit | subject |
|---|---|---|
| 1 | `0b103ec` | `chore(docs)`: the team lead's close contract and the STATUS tail — committed unedited |
| 2 | `4bfd391` | `feat(sku-b-close)`: the bar-2 applier — 45 dictated keys, 61 rows, matched exactly once |
| 3 | `2fae1c2` | `data(sku-b-close)`: the bar-2 read applied — 20 of 61 = 0.3279 vs 0.80 |
| 4 | `5b2a649` | `feat(sku-b-close)`: the bar producer learns the bar-2 read, and states the closure |
| 5 | `20ac6dd` | `data(sku-b-close)`: the verdict record, finalised — two bars of three FAIL, B closes |
| 6 | `0f1e43e` | `feat(sku-b-close)`: depth from the printed percentage, measured on what is already bought |
| 7 | `fa7f3df` | `docs(decision)`: the sku-b pilot closed by measurement |
| 8 | `c10f641` | `docs(report)`: sku-b-close — appended as the report's Close section |
| 9 | `043dfe6` | `chore(vault)`: the sku-b-close tail — the day's log, hot.md, the index |
| 10 | — | `docs(report)`: sku-b-close — the two rows this table could not name |

Ten commits. Row 10 is blank for the reason the previous table gives: a report cannot name the
commit that carries it, and one follow-up is where the regress ends. Commit 10 changes prose only —
the two table rows above and their checkout entries — on the tree commit 9 left, whose suite is the
`1854 passed, 2 skipped` in the row for commit 9.
