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

Staging pod `yax8ck1ajwuip5`, **L4 at $0.49/h** (Dv176 — v3's $0.24/h class is not offered in
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

Restored at `e579382` for the first pass with the same 3 dirty vault paths; rows 6 and 7 were checked
out afterwards on a clean tree, which is why they need no stash. Commit 8 is this paragraph and the
two rows above it — a report cannot check out the commit that carries it, so the last row is always
one commit behind, and the contract pre-authorises the extra commit (the Dv175 reading).

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
| 8 | — | `docs(report)`: sku-b-v4-run — the checkout table's own tail |

Eight commits. The vault tail is commit 7 rather than the last, for the reason Dv175 gave in the
previous report and this contract pre-authorises: the checkout table can only record the suite of
the commit that carries the report after that commit exists.
