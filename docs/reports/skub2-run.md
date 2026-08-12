# skub2-run — instrument v2 over all 138: the B′ measurement

## Read-back

**The eight gates, one line each:**

0.5 **Dv210** — `sku_bar_verdicts.bar_one` reads its gold from the B′ registration's own
   `gold.per_post`, joined to the reference BY ITEM; four more readers that assumed a resume block
   moved with it, and the producer's six defaults became skub2 paths beside v1–v4's.
1. **$0 gates** — `make check` 1994 green, preflight `EXIT=0 PASS 47 FAIL 0` in a rebuilt venv, four
   listings clean, `--dry-run` (no `--resume`) 108+30 in 7+1, and `results/spend_skub2.json`
   anchored at $11.6110861566 and committed before the first billing resource existed. **A second
   money-path defect was found here and fixed at $0** — see Gate 1b.
2. **The volume, staged before any endpoint** — `repo/` on `qw4nwleanc` moved `ec9cf3b` → `0793a3c`
   by a bundle naming its real ref, reset to an explicit sha, with a before/after content control on
   the 1200 ceiling and a parser-warning string; pod deleted, proven, priced by its own clock.
3. **A NEW template** — `hktpjtygc9`, exactly three env variables and no fourth.
4. **The endpoint** — `zq457b30jhgvp7`, `ADA_24` · 1 worker · idle 60 · execution-timeout 900, every
   flag read back from the API's own answer.
5. **The run** — one invocation, detached, watched by PID: identity stop (the worker said **1200**)
   → the two REGISTERED warm-ups → go/no-go **proceed** → 7 page jobs → 1 text job, in-run gate
   between jobs, no stop.
6. **The outcome — COMPLETION**: `results/sku_b_positions_skub2.{json,jsonl}` over 138 sources,
   **0 unreadable**, and bars 1 and 3 through the producer over B′'s gold. Bar 2 carries its n and
   no value.
7. **Teardown, proven** — endpoint then template deleted, the two 5b-era siblings still listed and
   mine absent, `serverless list` `[]`, `pod list -a` `[]`, the volume stays.
8. **Commits** — team-lead docs verbatim first, then Dv210, the anchor, the warm-up fix, the run's
   artifacts, the verdicts, this report, the vault tail.

**The two (10) stop semantics, one line each:**

- **(10)(a) go/no-go** — priced before the first gold call from the two registered warm-ups; a
  refusal buys nothing and consumes NO attempt. **It did not fire**: 138 gold calls projected
  **$0.6249** against **$0.6500** the driver saw left of the cap. It cleared the *true* remaining —
  $0.65 less the staging pod — by **$0.0002**. Dv234.
- **(10)(b) mid-leg stop** — the in-run gate re-prices the whole run before every job but the first;
  a projection above what is left ends the run and is a team-lead ruling. **It did not fire**: the
  seven readings fell from $0.3134 to $0.2759.

**A FULL run — nothing resumed, nothing re-used from v1's answers.** No `--resume` was passed. SPEC
3.17 (14)(d) re-asks all 138 elements and v1's answers stay v1's sealed measurement;
`results/sku_b_positions.json`, `…_v4.json` and every v1–v4 registration are untouched, and this
session's artifacts are new files beside them.

**Bar 1's gold source, in one line (Dv210):**
`results/sku_pilot_prereg_b2.json :: bars.leaflet_brand_recall.gold.per_post[].gold_keys` — the
37 pairs over 10 posts that SPEC 3.17 (13)(c) re-scoped, joined to `sku_reference_leaflet.json` by
`item` for the post list and the sent-page counts, and NOT the reference's own `gold_keys`, which
are the v4 key space.

---

## The outcome: completion, at 43% of the cap

| | |
|---|---:|
| population bought | **138 of 138**, one session |
| positions extracted | **101** (81 from pages, 20 from text) |
| unreadable replies | **0** of 138 |
| truncated replies | **0** |
| empty answers | **102** |
| positions carrying a crossed-out price | **80** — bar 2's denominator, SCOREABLE under R4 |
| balance delta at the end | **$0.2764** |
| cap | $0.65 |

**The same 138 elements, v4 against v2** — v4's figures are read out of
`results/sku_b_positions_v4.json`, not recomputed:

| | v4 (ceiling 800) | skub2 (ceiling 1200) |
|---|---:|---:|
| positions | 79 | **101** |
| unreadable replies | 5 (3.62%) | **0** |
| price pairs | 61 | **80** |
| session cost | $0.2541 | $0.2764 |

The (13)(a) amendment's own claim — that the four refused pages were a token ceiling and not a
vision failure — is measured here rather than argued: at 1200 nothing was refused and nothing
truncated.

**The bars, from code, over the completed population:**

```
$ PYTHONPATH=src python3 scripts/sku_bar_verdicts.py
results/sku_b_positions_skub2.json — 138 elements, unbought 0
  leaflet_brand_recall       0.9800 vs 0.75   PASS
  price_pair_accuracy             — vs 0.80   PENDING_TEAM_LEAD
  text_tier_accuracy         0.8667 vs 0.85   PASS
  bar 1 over 10 posts · micro 0.9459 · precision 0.9722222222
  bar 3 over 30 of 30 rows · 0 unreadable (0.0%)
  bar 2 over 80 pairs, the team lead's read — no read on disk, PENDING
  closure: UNDETERMINED (['price_pair_accuracy'] carry no verdict yet)
wrote results/sku_bar_verdicts_skub2.json
```

**Bar 2 is not scored here and carries no value anywhere in this report** — SPEC §10, the executor
never scores its own sample. The closure is UNDETERMINED by the producer's own rule while one bar
has no verdict; it is not a verdict on the pilot and this report does not supply one.

**Bar 1 moved for two reasons at once and this report does not decompose it.** The gold was
re-scoped by (13)(c) *and* the instrument changed. The only figure for one of the two halves is the
team lead's, quoted from SPEC 3.17 (14): v1 on the same B′ gold reads **0.703**. Deriving the other
half here would be a new measurement nobody registered. Dv236.

---

## Gate 0.5 — the Dv210 wiring, paid before anything billed

Commit `2509c05`. The contract named one thing; the file needed five, and one of the five produces a
number instead of an error.

| what | v1–v4 | B′ | how it would have failed |
|---|---|---|---|
| bar 1's gold | the reference's `posts[].brands_visible.gold_keys` | the registration's `gold.per_post[].gold_keys` | **a wrong number**: 55 pairs over 15 posts instead of 37 over 10, in the v4 key space |
| the reference pin | `gold.sha256` | `gold.derived_from.sha256` | KeyError |
| the population count | `resume.population.registered` | `population.elements` | KeyError |
| the record's sessions | `record["resume"]["sessions"]` | absent | KeyError |
| the closure's `rule_source` | the v4 path, typed | — | a provenance string that had stopped being true |

`gold_source` dispatches on the registration's own shape — `per_post` present is B′, `sha256`
present is the reference, **both or neither is refused** — and joins the gold to the reference by
`item`. Two lists indexed side by side would attribute one post's gold to another and still report a
macro mean, which is the failure mode that has no error message.

**The key space is the half that produces a number.** (13)(b) made «Rud» a display name, so a brand
that keys `raw:rud` in the reference keys `rud` under B′ — and `rud` is what the prediction side
already resolves to through `registered_aliases`. The registration carries `gold_keys_v4` beside
`gold_keys` for the join it was built by, and reading the wrong field costs a whole key on a post
the instrument got right. Its control, on the fixture where the two spaces differ:

```
    bar["per_post"][0]["missed"] == []          reading gold_keys      -> macro 1.0
control["per_post"][0]["missed"] == ["raw:rud"] reading gold_keys_v4   -> macro 0.5
```

**The summary counts are checked against the rows, never against each other.** `posts_with_an_empty_gold_set`,
`posts_with_a_non_empty_gold_set` and `pairs` are each re-derived from `per_post`; the contract's own
checksum, 10 posts and 37 pairs, is a runtime refusal in the producer and a witness test on the
shipped registration. Comparing `excluded.posts` against `gold.posts_with_an_empty_gold_set` would
have been two fields of one file agreeing with each other.

**The six defaults moved to NEW paths, not over the old ones** (Dv230). `results/sku_bar_verdicts.json`
is the pilot's closure BY MEASUREMENT and is pinned by path inside `scripts/build_sku_miss_pack.py`;
`results/sku_b_pair_verdicts.json` is a read of the **v4 dump**, and bar 2 refuses a read taken over
another dump — left as the default it would have aborted this producer on a file doing nothing
wrong.

**The regression control the change had to pass:** `bar_one` under the v4 registration is
bit-identical. `tests/test_build_sku_miss_pack.py` carries v4's bar-1 value as a literal
(`recomputes to 0.3603174603`) and rebuilds the shipped pack through the same function; both are
green.

---

## Gate 1 — the $0 gates

```
$ make check
1994 passed, 2 skipped in 58.69s          ← 1985 before this contract

$ ruff format --check .
244 files already formatted               ← not in `make check`, so it is run separately
```

```
$ PYTHONPATH=src <peftvenv>/bin/python scripts/preflight_serving_guards.py
EXIT=0    PASS 47    FAIL 0
local   transformers 5.14.1 · peft 0.20.0 · torch 2.13.0
volume  transformers 5.14.1 · peft 0.20.0
```

**Dv235 — the peft venv was gone again.** Third time in five sessions (Dv173, Dv200). Rebuilt at the
pinned versions before the preflight ran; an unrunnable preflight is a finding, not a pass.

**The account, before anything of this session existed** — four listings, because the teardown
control in gate 7 needs its *before* half captured before gate 3 creates mine:

```
$ runpodctl pod list -a                → []
$ runpodctl serverless list            → []
$ runpodctl template list --type user  → unfcr3ja0t | market-pulse-5b-a
                                         0g6zg73ptq | mp-5b-diag
$ runpodctl network-volume list        → qw4nwleanc  mp-srv2  EU-RO-1  100

balance $11.6111 · phase-4 anchor $35.00 · phase-4 spent $23.3889 of $25.00 · $1.6111 left
```

The dry run, on the non-resume path:

```
$ PYTHONPATH=src python3 scripts/positions_gm4_skub.py --dry-run
page leg   108 pages sent (of 159 available, 19 posts) in 7 job(s), largest 7.99 MB
text leg   30 rows in 1 job(s)
dump       17 columns: item, page, file, sha256, brand_raw, brand_id, line, category, size, fat,
           price_promo, price_old, discount_pct_printed, price_qualifier, tier, depth,
           depth_disagrees_with_printed
```

138 sources, 108 + 30, in 7 + 1 jobs — the contract's own count. The constants check and the serving
pin check both sit **above** the `--dry-run` return, so this run passed through them; their wiring
is proved by `test_the_constants_check_runs_on_the_non_resume_path_too` and
`test_the_serving_pin_check_runs_on_the_non_resume_path_too`, and by preflight block 9b, which
accepts the registered triple and refuses the old cap, the old ledger and the old phase.

**The anchor, written before the first billing resource existed** (the Dv149 protocol), through the
driver's own `read_ledger` with the constants passed explicitly, and committed in `a60e455`:

```json
{ "runpod_balance_at_skub2_start": 11.6110861566, "cap_usd": 0.65, "runs": [] }
```

The key is `runpod_balance_at_skub2_start`, the one the run reads; `read_ledger`'s module defaults
are the FIRST session's, so an anchor written on defaults carries a key this run would refuse.

---

## Gate 1b — the probe the law names, and the probe the code sent

This is the finding of the session and it was found at $0, before the staging pod. Commit `0793a3c`.

**The law, in four places.** SPEC 3.17 (12)(c): *"The warm-up inputs remain the REGISTERED ones of
v3 — the same unsent page and the same non-pack row, re-verified by hash, never re-picked."*
(13)(d): the re-measurement runs *"with every reading of (9)–(12) in force"*. (14)(e) sizes the cap
on what that probe prices: *"the (12)(c) registered warm-up prices the gate's projection at ~$0.61
(the deep-page probe against 138 calls)"*. And this contract's step 5: *"the two REGISTERED
warm-ups"*.

**The code.** `probe` resolved off the resume PLAN, and a full run never builds one:

```python
probe = resume_warmup_inputs(plan["prereg"], …) if plan is not None else None
```

`warmup()` falls back to a generated 64×64 image when `page_url is None`. skub2 would have opened on
it. That is the exact failure (11)(c) was written for — the first session's 64×64 priced a leaflet
page at 1.436 s against a real 5.0772 s, and the go/no-go passed a run it exists to refuse. A cheap
probe does not make a run cheaper; it turns the one gate that can refuse **for free** into a gate
that always passes, and the $0.65 cap's whole justification is the deep probe's ~$0.61.

**Third guard this program has found wired where it cannot fire** — after
`check_the_constants_are_the_registrations` (inside `if args.resume:`) and
`check_the_serving_pin_is_the_registered_one` in the same contract's prep.

**The fix.** `warmup_registration` names the registration the inputs come from and pins it. B′
carries no warm-up block and does not list v4's registration in its `pinned_inputs`, so the sha is
transcribed in the module and checked at the point of use — an unpinned read of a sealed sibling is
a read that stops being true silently. `resume_warmup_inputs`'s own refusals stay live and were
re-run against B′'s inputs: the registered page is still outside the 108 sent, the registered row
still outside the 30, and both hashes still match the bytes. The run record now carries:

```json
"registered_in": { "path": "results/sku_pilot_prereg_v4.json", "block": "resume.warmup",
                   "sha256": "22fd7d9cc363ac9357b77e4a3ff3561f723fe6c4a12aedcc638c11be65dc9449" }
```

**Its negative control**, because a pin that cannot fail is not a pin:

```
$ pytest -k the_warm_up_registration_is_refused_when_the_file_it_transcribes_moves
refused: results/sku_pilot_prereg_v4.json hashes 58c9eefb30796f8c… and this run
transcribes 22fd7d9cc363ac93… — it is where SPEC 3.17 (12)(c) registers the two warm-up inputs
and B′ does not pin it, so the transcription is the only pin there is
```

`head["contract"]`'s non-resume branch followed the same reasoning: it named the two prep contracts
and omitted (11) and (12), which is where this run's warm-up and cap come from. It now reads
`docs/PROMPT-skub2-run.md; docs/SPEC.md amendment 3.17 (9), (10), (11)(c) and (12)(c) the registered
warm-up, (12)(a)/(14)(e) the cap, (13), (14)`.

### The money geometry, computed before the staging pod, not after it

With the deep probe wired, the (10)(a) projection is arithmetic and it was published before anything
was rented:

```
rate $0.00030669/s · idle tail 60s · 108 pages + 30 rows

low  boot 205.5s · probe 14.625s (v4's own)   ->  $0.6062   proceed, slack $0.0438
high boot 402.6s · probe 14.808s (v3's own)   ->  $0.6736   REFUSE
low  boot · probe +50% (the 1200 ceiling)     ->  $0.8686   REFUSE

minutes of staging pod that flip the low-boot corner to REFUSE: 5.36 at $0.49/h
```

Two things follow and both changed what gate 2 did. **The staging pod comes straight off the
(10)(a) budget**, because `budget = cap − (anchor − balance)` and the anchor predates the pod — so
the pod had to be minutes, not tens of minutes. And **the +50% corner was checked rather than
assumed**: v4's warm-up reply on that same page has `finish_reason: "stop"`, not `"length"`, so the
deep probe was *not* truncated at 800 and the 1200 ceiling should not lengthen it. That single fact
is the difference between "tight but priced" and "unpriced".

---

## Gate 2 — the volume, staged before any endpoint existed

Staging pod `r56zhortgtbcsb`, **RTX PRO 4000 Blackwell at $0.57/h** (Dv233 — the $0.24/h and
$0.49/h classes were listed for EU-RO-1 and both refused to allocate, as did the A6000), EU-RO-1,
volume attached, `--terminate-after` an hour out. Rented **16:26:09 UTC**, deleted **16:28:46 UTC** —
**2.617 min by the pod's own clock**, an upper bound of **$0.0249**.

The content check has both halves on the same three paths, and the facts chosen discriminate:
instrument v2 does not exist in the v4-era tree the last teardown left on the volume.

| | before | after |
|---|---|---|
| `git rev-parse HEAD` | `ec9cf3bda320…` (the sku-b-v4-run anchor commit) | `0793a3cab567…` |
| `grep -c 'POSITIONS_MAX_NEW_TOKENS = 1200'` | **0** | **1** |
| `grep -c 'discount_footnote' positions.py` | **0** | **11** |
| `results/sku_pilot_prereg_b2.json` | *No such file or directory* | present, 40174 bytes |

The staging itself, verbatim — the bundle names its real ref and the reset targets an explicit sha,
so a fetch that moved nothing would have failed loudly instead of printing `Already up to date.`:

```
=== bundle heads (the REAL ref, not FETCH_HEAD) ===
0793a3cab567d1540fe76faadce878760531d6fb HEAD
=== fetch ===
From /workspace/mp-skub2.bundle
 * branch            HEAD       -> FETCH_HEAD
=== reset --hard to the Mac's exact sha ===
HEAD is now at 0793a3ca fix(skub2-run): the registered warm-up reaches a full run, not only a resumed one
=== proof ===
0793a3cab567d1540fe76faadce878760531d6fb
(end of git status)
```

`start.sh` verified and not edited; the prompt shas and the ceiling rendered on the volume itself,
by the filesystem the worker actually reads:

```
5b3bcbb2f59372f4cb3ee940caad5b5b4b90bb22adeff1f783f8c8301474b46c  /workspace/start.sh
5b3bcbb2f59372f4cb3ee940caad5b5b4b90bb22adeff1f783f8c8301474b46c  repo/scripts/start_5b_worker.sh

positions_post_gm4 ca6303c157d46e707aaf3fc52c7a05ed1450e24c26db0e7c93eefba4f6968754
positions_text_gm4 7250b87aa1c2de407e06ab9eed565dd4d88025add7be0d2d2a87607c0d872860
POSITIONS_MAX_NEW_TOKENS 1200
```

Both prompt shas equal `results/sku_pilot_serving_v2.json :: instruments`, and the ceiling is the
one `expected_worker.max_new_tokens` pins. Pod deleted, `pod list -a` → `[]`.

---

## Gates 3 and 4 — the template and the endpoint

Template `hktpjtygc9`, created new, exactly three variables and no fourth:

```json
"env": { "BASE_WEIGHTS": "google/gemma-4-31b-it",
         "MODEL_REVISION": "842da3794eaa0b77d5f08bae87a17459d91ff475",
         "SERVING_CONFIG": "POSITIONS" },
"dockerStartCmd": ["bash","-c","exec bash /runpod-volume/start.sh > /runpod-volume/worker-boot.log 2>&1"],
"isServerless": true
```

Endpoint `zq457b30jhgvp7`, every flag read back from the API's own answer:

```json
"executionTimeoutMs": 900000, "idleTimeout": 60, "workersMax": 1, "gpuIds": "ADA_24",
"networkVolumeId": "qw4nwleanc", "locations": "EU-RO-1", "flashBootType": "FLASHBOOT",
"templateId": "hktpjtygc9", "scalerType": "QUEUE_DELAY"
```

`executionTimeoutMs: 900000` equals the driver's `JOB_TIMEOUT_S` — (10)(c) holds at the endpoint as
well as in the client.

**The headroom immediately before the run**, with the pod priced from its own clock rather than from
the balance:

```
staging pod            2.617 min at $0.57/h = $0.0249
low-boot corner   $0.6062 + pod = $0.6311 against $0.65 → headroom $+0.0189
high-boot corner  $0.6736 + pod = $0.6985 against $0.65 → REFUSE

balance at that moment: anchor $11.6111 · balance $11.6111 · delta $0.0000
```

The balance had not moved at all — Dv166 again, and the reason the pod's own clock is the number
used here. It is also **Dv234**: the driver's own `spent_before` therefore read $0.0000, so the
(10)(a) gate compared against $0.6500 when the true remaining was $0.6251.

---

## Gate 5 — the run

One invocation, launched detached (`nohup` + PID watch, pre-authorised) and watched by process,
never by `tail -f`:

```
--- tick 1  · 16:32:04Z · pid=84393 · log 0 lines
--- tick 4  · 16:34:49Z · pid=84393 · log 0 lines      ← the boot: the log is silent through it
--- tick 5  · 16:35:44Z · pid=84393 · log 14 lines
--- tick 10 · 16:40:19Z · pid=84393 · log 20 lines
--- tick 14 · 16:44:55Z · pid=84393 · log 28 lines
--- tick 15 · 16:45:45Z · pid=GONE  · log 170 lines
PROCESS EXITED
```

The driver's console, verbatim and in the order the contract fixes:

```
ledger: spent $0.0000 of $0.65 (balance $11.61)
endpoint       zq457b30jhgvp7 · POSITIONS/base-no-adapter
  revision      842da3794eaa0b77d5f08bae87a17459d91ff475
  ceiling       1200 new tokens, greedy, batch 1
  prompts       positions_post_gm4 ca6303c157d4… · positions_text_gm4 7250b87aa1c2…
  warm-up positions_post_gm4   stop  14.925s  ```json
[
  {
    "brand": "De Luxe Foods&Goods Se
  warm-up positions_text_gm4   stop  3.886s  [{"brand": "Молокія", "line": "Екстра", "category"
  go/no-go      138 gold calls project $0.6249 against $0.6500 left of the cap — proceed
  page job 00  17 item(s)  ok  7.85 MB
  after 17/138: 5.1658s/call · $0.1033 spent → $0.3134 projected
  page job 01  17 item(s)  ok  7.70 MB
  after 34/138: 5.0479s/call · $0.1290 spent → $0.3084 projected
  page job 02  16 item(s)  ok  7.78 MB
  after 50/138: 5.2305s/call · $0.1566 spent → $0.3161 projected
  page job 03  17 item(s)  ok  7.79 MB
  after 67/138: 4.7277s/call · $0.1735 spent → $0.2948 projected
  page job 04  14 item(s)  ok  7.74 MB
  after 81/138: 4.5548s/call · $0.1895 spent → $0.2875 projected
  page job 05  17 item(s)  ok  7.99 MB
  after 98/138: 4.6232s/call · $0.2153 spent → $0.2904 projected
  page job 06  10 item(s)  ok  5.61 MB
  after 108/138: 4.2794s/call · $0.2181 spent → $0.2759 projected
  text job 00  30 item(s)  ok  0.03 MB
…
101 positions from 138 sources · 0 unreadable · 102 empty · 80 carry a crossed-out price
· $0.2764 of $0.65
wrote results/sku_b_positions_skub2.jsonl and results/sku_b_positions_skub2.json
```

**The identity stop did its job at $0-after-boot:** the worker reported `max_new_tokens: 1200`, which
is v2's pin. A run left on v1's pin would have been refused here, after the boot was billed — which
is why the pin moved with the constants in the prep session.

### The go/no-go arithmetic, in full

```
billed at the gate   248.929 s   = boot 230.118 + warm-up 18.811
page marginal         14.925 s   (the registered deep page, finish_reason "stop")
text marginal          3.886 s   (the registered non-pack row)
gold seconds        1728.480 s   = 108 × 14.925 + 30 × 3.886
idle tail             60.000 s
projected            $0.6249     = (248.929 + 1728.480 + 60) × 0.00030669
budget               $0.6500     → refuse: false
```

**The margin the gate actually had.** Against the budget it saw: $0.0251. Against the true
remaining — $0.65 less the staging pod, which had not yet settled into the balance — **$0.0002**.
The session proceeded on a two-hundredth of a cent. That is not a criticism of the gate: (14)(e)
sized the cap on exactly this projection and (12)(a)'s rule is that the cap admits the gate's own
pessimism. It is a statement of how little room the ruling left, and of the fact that the reading
was $0.0249 more permissive than the truth for a reason nobody chose (Dv33: the balance settles
minutes to hours behind the resource).

### Per-leg marginals, measured

```
page leg   462.173 s over 108 calls = 4.2794 s/page   $0.1417
text leg    84.398 s over  30 rows  = 2.8133 s/row    $0.0259
boot + warm-up 248.929 s                              $0.0763
worker total 795.500 s · queue 45.465 s · wall 880.503 s · idle share 0.0965
```

**The deep probe over-priced the page leg by 3.49×** — 14.925 s against the measured 4.2794 s. This
is the probe behaving exactly as (11)(c) intends: it is a structurally hard page, and the gate is
supposed to refuse on the pessimistic reading rather than discover a shortfall in flight. The
in-run gate then re-priced on real volume and fell to $0.2759, and the run landed at $0.2764.

---

## Gate 6 — the outcome

### Bar 1 — leaflet brand recall, 0.9800 vs 0.75, PASS

Ten posts, macro mean, over the (13)(c) gold. Nine of ten are perfect:

| post | gold keys | recall | missed |
|---|---:|---:|---|
| `@atb_market_official:4340` | 3 | 1.0000 | — |
| `@atb_market_official:4350` | 2 | 1.0000 | — |
| `@atb_market_official:4360` | 3 | 1.0000 | — |
| `@atb_market_official:4381` | 4 | 1.0000 | — (one extraction outside the gold: `raw:komo`) |
| `@atb_market_official:4401` | 10 | **0.8000** | `raw:frenzy (рудь)`, `raw:imperium (рудь)` |
| `@atb_market_official:4426` | 4 | 1.0000 | — |
| `@atb_market_official:4436` | 1 | 1.0000 | — |
| `@atb_market_official:4446` | 3 | 1.0000 | — |
| `@atb_market_official:4467` | 3 | 1.0000 | — |
| `@atb_market_official:4508` | 4 | 1.0000 | — |

Micro over all 37 pairs: **0.9459** (35 of 37). Micro precision, reported and gating nothing:
**0.9722**.

**The precision probe — the nine emptied posts returned ZERO false positives.** Every one of the
nine posts R3 excludes for an empty gold set is listed in the verdict record with an empty
`false_positives`. That is the strongest single fact in this run that is *not* an artefact of the
re-scope: those posts have no gold to help the instrument, and it named nothing on them.

### Bar 3 — text tier accuracy, 0.8667 vs 0.85, PASS

30 of 30 rows scored, **0 unreadable**, 0 outside the denominator. The confusion, all four
disagreements in one direction:

```
none -> none                16
position -> position        10
position -> none             1
product_mention -> none      3
```

The instrument under-reads four rows and over-reads none. v4 scored 0.8621 over 29 of 30 with one
unreadable; the reading is essentially unchanged and the unreadable row is gone.

### Bar 2 — the dump and its n only

**80 pairs**, SCOREABLE under R4 (`n >= 10`). No value, `PENDING_TEAM_LEAD`. The dump that makes the
read possible is `results/sku_b_positions_skub2.jsonl`,
sha `5592b3248c17e4857fcb9e79c2309f26a43db7aec5c6e00a195a37bdb713613d`, 101 rows, 17 columns.
`scripts/sku_bar_verdicts.py`'s `--pairs` default is
`results/sku_b_pair_verdicts_skub2.json`, which does not exist: the v4 read is over the v4 dump and
bar 2 refuses a read taken over another dump.

### The parser warnings — Dv232, and it is a gap, not a finding

The contract asks for *"parser WARNINGS (footnote/multipack/from) counted per page in the record —
they are v2's fingerprint"*. **They are not in the record and they are not recoverable for this
run.** `Position.warnings()` is a method over `pack_count`, `discount_footnote` and
`price_qualifier`; the dump's columns are derived from bar 2's registered `procedure` sentence and
carry only the third; the raw replies are not stored. Dv199 named exactly this in skub2-prep — *"carrying
the warnings into the run RECORD is skub2-run's step"* — and I went into the paid run without
wiring it. No re-run is possible: SPEC forbids re-running a leg after its result, and the money is
spent.

What survives, from the dump alone:

```
price_qualifier == "from"   3 positions, all on one TEXT row (@VARUS_channel:2119)
                            → zero `price_from` warnings on the 108 leaflet pages
discount_pct_printed        92 of 101 non-null — the field discount_footnote qualifies,
                            but presence of the asterisk itself is not recorded
multipack                   unrecoverable
```

**One of the three is a negative result, not just a hole.** All three `price_from` positions are on
a single TEXT row, so «від X грн» occurred **zero times** on the 108 leaflet pages. The three
strings the preflight accepts were read out of v4's own refusal reasons, and at least one of them
appears not to occur on the page population at all — which bears on whether the (13)(a) parser
family was the fix for the failure or a fix for something rarer than believed. The 4 pages v4
refused are the place to look, and their replies this time are gone with the warnings.

The indirect evidence for the parser family is still strong and is in the counts above: **0
unreadable and 0 truncated against v4's 5 and 4 refused pages**, on the same 108 pages. What cannot
be said from these artifacts is *which* of the three warnings kept which position alive.

---

## Gate 7 — teardown, proven

Endpoint deleted, then template. The positive control is the two 5b-era siblings, which must still
be listed — a listing that is empty because the tool is broken proves nothing:

```
$ runpodctl serverless delete zq457b30jhgvp7   → {"deleted": true}
$ runpodctl template   delete hktpjtygc9       → {"deleted": true}

$ runpodctl serverless list            → []
$ runpodctl pod list -a                → []
$ runpodctl template list --type user  → unfcr3ja0t | market-pulse-5b-a
                                         0g6zg73ptq | mp-5b-diag      ← mine absent, theirs present
$ runpodctl network-volume list        → qw4nwleanc  mp-srv2  EU-RO-1  100   ← the volume stays
```

### The three cost readings, kept distinct

| reading | value | what it is |
|---|---:|---|
| the balance delta against this session's anchor | **$0.2764** | `results/spend_skub2.json`, settled by the time it was read. A FLOOR by Dv33 |
| the worker's own clock × the registered rate | **$0.2440** | 795.5 s × $0.00030669 — the compute, without the queue or the tail RunPod also bills |
| the staging pod's own clock | **$0.0249** | 2.617 min at $0.57/h, an upper bound, inside the $0.2764 |

Phase 4 after the session: **$23.6653 of $25.00**, $1.3347 left. The ledger's single run entry:

```json
{ "at": "2026-08-12T16:45:21+00:00", "balance": 11.3347237899,
  "step_spent_usd": 0.2764, "note": "138 sources asked, 101 positions extracted" }
```

---

## The artifacts

| file | sha256 (16) | what |
|---|---|---|
| `results/sku_b_positions_skub2.json` | `d1715e8869d1ffcf…` | the run record, 138 outcomes |
| `results/sku_b_positions_skub2.jsonl` | `5592b3248c17e485…` | the dump, 101 rows, 17 columns |
| `results/sku_bar_verdicts_skub2.json` | `d27ae721948b194d…` | bars 1 and 3 computed, bar 2 pending |
| `results/spend_skub2.json` | `618a7d63c742bd6e…` | the anchor and the one run entry |

Both records were written at `0793a3ca` with `git.dirty` naming only the three `knowledge/` files of
the pre-contract checkpoint and the artifacts of this same session that were not yet committed when
each was written. Nothing under `src/`, `scripts/` or `config/` was dirty.

---

## The per-commit checkout table

Every commit checked out for real, running ITS OWN suite; `HEAD` printed from `git rev-parse`, never
from the loop variable. **`4b0ed29` is the parent and the control** — the same facts must read their
old values there, or the table is measuring the working tree.

| commit | prompt | bar producer defaults | `gold_source` / `PREREG_WARMUP` | anchor | record | verdicts | suite |
|---|---|---|---|---|---|---|---|
| `4b0ed29` **control** | absent | `prereg_v4` · `sku_bar_verdicts.json` | 0 / 0 | absent | absent | absent | 1985 ✅ |
| `8e484f3` | present | `prereg_v4` · `sku_bar_verdicts.json` | 0 / 0 | absent | absent | absent | 1985 ✅ |
| `2509c05` | present | `prereg_b2` · `..._skub2.json` | 1 / 0 | absent | absent | absent | 1992 ✅ |
| `a60e455` | present | `prereg_b2` · `..._skub2.json` | 1 / 0 | $11.6110861566 · 0 runs | absent | absent | 1992 ✅ |
| `0793a3c` | present | `prereg_b2` · `..._skub2.json` | 1 / 3 | $11.6110861566 · 0 runs | absent | absent | 1994 ✅ |
| `fb4e8dd` | present | `prereg_b2` · `..._skub2.json` | 1 / 3 | · 1 run | 138 · 101 · $0.2764 | absent | 1994 ✅ |
| `489271e` | present | `prereg_b2` · `..._skub2.json` | 1 / 3 | · 1 run | 138 · 101 · $0.2764 | leaflet PASS · price PENDING · text PASS | 1994 ✅ |

Seven rows: **`4b0ed29` the control, and the six commits of this contract that existed when the
table ran.** The report commit and the vault tail postdate it, so they are not in it. The count and
the clock come from the command, not from the table's row count — that substitution is what
`4b0ed29` itself corrected five hours before this session:

```
$ git log --reverse --format='%h %ad %s' --date=format:'%H:%M' 4b0ed29..HEAD
8e484f3 18:09 docs(team-lead): the skub2-run contract and the STATUS pointer, unedited
2509c05 18:09 feat(skub2-run): Dv210 -- bar 1 scores the B-prime gold, and five readers that assumed v4
a60e455 18:12 chore(skub2-run): the session's spend anchor, before the first billing resource exists
0793a3c 18:21 fix(skub2-run): the registered warm-up reaches a full run, not only a resumed one
fb4e8dd 18:48 data(skub2-run): the 138 bought, instrument v2, 101 positions and no unreadable reply
489271e 18:48 data(skub2-run): bars 1 and 3 over the B-prime gold, bar 2 pending the team lead
51711db 19:01 docs(report): skub2-run

$ git rev-list --count 4b0ed29..HEAD
7
```

**Seven commits, 18:09–19:01 local**, and the vault tail after this line makes eight. `make check`
tail at HEAD:

```
$ make check
1994 passed, 2 skipped in 58.16s
```

---

## Deviations

**Dv228 — the contract asks for `Dv225+` and `Dv227` is already spent.** `docs/reports/skub2-prep.md`
§Fix carries Dv211–Dv227. Numbering here starts at **Dv228**; nothing else is affected.

**Dv229 — the registered warm-up did not reach a full run, and the cap's justification rests on it.**
Found at $0 before the staging pod, fixed in `0793a3c`, whole reasoning in Gate 1b. This is the
third guard in this program found wired where it cannot fire, and the first of the three that would
have produced a *number* rather than a refusal.

**Dv230 — the bar producer's six defaults moved to NEW skub2 paths, not over the old ones.** The
contract named only `bar_one`'s gold source. Two of the six could not have been left alone:
`results/sku_bar_verdicts.json` is the pilot's closure and is pinned by path inside
`scripts/build_sku_miss_pack.py`, and `results/sku_b_pair_verdicts.json` is a read of the v4 dump
that bar 2 refuses by design.

**Dv231 — four more readers in `sku_bar_verdicts.py` assumed a resume block**, and every one was a
KeyError on the shape skub2 writes: the reference pin, the population count, the record's sessions
and the closure's hard-typed `rule_source`. Table in Gate 0.5.

**Dv232 — the parser warnings do not reach the run record and are unrecoverable for this run.** My
miss: Dv199 named it as skub2-run's step and I did not wire it before spending. Full accounting in
Gate 6. Recoverable from the dump: `price_from` × 3, all on one text row.

**Dv233 — three GPU classes listed for EU-RO-1 refused to allocate.** RTX 2000 Ada ($0.24/h), L4
($0.49/h) and RTX A6000 ($0.53/h) all failed `pod create`; the staging pod landed on RTX PRO 4000
Blackwell at **$0.57/h**, the dearest staging class of the four sessions. No pod was created by the
three failures, so nothing billed for them. Dv177 recorded the same phenomenon at a different price
point; `gpu list`'s availability field is advisory.

**Dv234 — the (10)(a) gate compared against a budget $0.0249 more permissive than the truth.** The
staging pod had not settled into the balance (Dv33/Dv166), so `spent_before` read $0.0000 and the
budget read $0.6500 where the true remaining was $0.6251. The projection was $0.6249: it fits both
readings, by $0.0251 and by **$0.0002** respectively. Nothing was decided by the difference this
time. The general fix is not obvious — the gate cannot read a bill RunPod has not written — but the
pattern is now twice-observed and the pod's own clock is the number a report should use.

**Dv235 — the peft scratch venv was gone again**, the third time in five sessions (Dv173, Dv200).
Rebuilt at the pinned versions before the preflight ran.

**Dv236 — bar 1's 0.98 is a joint movement of the gold and the instrument and is not decomposed
here.** The (13)(c) re-scope and instrument v2 landed together by the amendment's own design. The
team lead's reading of v1 on the same B′ gold, quoted from SPEC 3.17 (14), is 0.703; the other half
would be a new measurement this contract does not authorise.

---

## Assumptions stated

1. **The warm-up inputs are v4's registered pair.** B′ registers none, and (12)(c) says they
   "remain the REGISTERED ones of v3 … never re-picked". Reading v4's block is the only way to obey
   that clause; the alternative reading — that a registration without a warm-up block falls back to
   a synthetic probe — contradicts (14)(e), which prices the cap on the deep probe. The file is
   named and pinned in the run record rather than assumed.
2. **skub2's verdicts belong in a new file.** The contract does not name an output path for gate 6.
   `results/sku_bar_verdicts.json` is the pilot's closure BY MEASUREMENT and evidence; it was not
   overwritten.
3. **The closure is UNDETERMINED and that is a producer output, not a ruling.** Two bars pass and
   one has no verdict. What follows from `leaflet_brand_recall PASS` after three sessions of FAIL is
   the team lead's to say.
4. **The team lead's bar-2 read goes to `results/sku_b_pair_verdicts_skub2.json`**, over the dump
   sha above. Bar 2 will re-derive its share from that file's own keys through
   `apply_sku_pair_verdicts.checksums` and refuse a read taken over any other dump.

## What this leaves

1. **Bar 2's read** — 80 pairs against the page images, the team lead's at acceptance. Until it
   exists the closure stays UNDETERMINED.
2. **Dv232, unpaid** — the warnings need a driver change before any future positions run, and this
   run's are gone.
3. **Dv199, closed by supersession for the dump** and re-opened as Dv232 for the record.
4. **Dv176, still open** — `head["contract"]`'s resume branch omits 3.17 (12). Untouched: that
   branch is v4's.
5. **Dv223, carried** — the driver's job-timeout margin literal is v1's model at v1's ceiling. It
   did not bind: the largest job was 17 pages and the execution timeout is 900 s.

---

## Close

*Appended 2026-08-12 under `docs/PROMPT-skub2-close.md`. $0 — local arithmetic over files already
bought, no paid call and no rented resource of any kind.*

### Read-back

**The three deliverables, one line each:**

1. **The applier** — the sku-b-close pattern over the skub2 dump, writing
   `results/sku_b_pair_verdicts_skub2.json`, refusing on any checksum miss / unmatched /
   doubly-matched row, both verdict-flip guards as before.
2. **The verdict record finalised** — bar 2 becomes `0.4125 vs 0.80 — FAIL (n=80, team lead
   2026-08-12)`, the closure block reads B′ CLOSED BY MEASUREMENT with `on_failure` verbatim, plus
   **depth-from-pct v2** over the 80 pairs into `results/sku_depth_from_pct_skub2.json`.
3. **The ADR** `knowledge/decisions/skub2-b-prime-closed.md` + INDEX: three bars over both
   instruments, what (13) fixed and what it never touched, depth adequacy from both measurements,
   the programme's full cost, and the product reading AS A CANDIDATE for the 5c2 ruling.

**The Do-NOTs, read back:** no paid calls · sealed artifacts and registrations untouched, the
verdicts file NEW and beside · team-lead files commit-only · never `git add -A` · vault tail its own
final commit. All five held; the sealed set is hashed before and after in §What did not move.

### The outcome

`results/sku_bar_verdicts_skub2.json`, over the completed 138 and the 80 pairs of its dump:

| bar | registered | value | verdict |
|---|---:|---:|---|
| 1 — leaflet brand recall | ≥ 0.75 | 0.9800 | **PASS** |
| 2 — price-pair accuracy | ≥ 0.80 | **0.4125** | **FAIL** |
| 3 — text tier accuracy | ≥ 0.85 | 0.8667 | **PASS** |

**State: CLOSED — instrument not ready, BY MEASUREMENT.** One of three.

**The finding of the close is a split, not a number.** Of the 80 pairs the team lead read, **61 are
the v4 dictation with not one verdict moved** — 20/61 = 0.3279, the pilot's own bar 2 to the digit —
and **19 are new**, at 13/19 = 0.6842. The 19 sit on exactly the four page answers v4 recorded as
unreadable: `4342` and `4467` (`-50%*` asterisk), `4405` (malformed JSON, and the one reply v4 hit
the 800-token ceiling on) and `4446` (multipack size). So bar 2's whole 0.3279 → 0.4125 is a widened
denominator, and on the pairs both instruments produced, the crossed-out old price reads exactly as
badly as it did before the parser family, the ceiling and the aliases. (13) opened four pages; it did
not touch a superscript.

### Deliverable 1 — the applier

`scripts/apply_sku_pair_verdicts_skub2.py` carries the 64 dictated keys and nothing else: the
guards, the join and the record's shape stay in `scripts/apply_sku_pair_verdicts.py`, reached
through a `Read` spec. Two matchers would be two rules, and the one not exercised daily is the one
that rots. The v4 applier's own defaults and every number it writes are unchanged and pinned by
`test_the_default_read_is_this_modules_own_constants`.

```
$ PYTHONPATH=src python3 scripts/apply_sku_pair_verdicts_skub2.py
results/sku_b_positions_skub2.jsonl — 80 pair rows over 64 keys, each matched once
  correct 33 · wrong 47 · accuracy 0.4125 (33/80)
  shared  45 keys · 61 rows · 20/61 = 0.3279
  new     19 keys · 19 rows · 13/19 = 0.6842
  checksum deviation: {'keys': {'contract': 54, 'asserted': 64}}
  promo 80/80 correct · printed % 80/80 correct · crossed-out old 33/80 — the superscript family
  again; dense multi-item pages read their olds better (4405: 7/9, 4446: 5/6) than single-hero posters
wrote results/sku_b_pair_verdicts_skub2.json
```

#### Dv237 — the contract states 54 keys and its own table dictates 64

The checksum line the applier MUST assert reads *"keys **54**, rows Σn = **80**, correct = **33**,
wrong = **47**, accuracy = 33/80 = **0.4125**"*. The table under it has **64** rows, and the dump
carries **64** distinct `(file, promo, old)` price boxes. Four of the five numbers are exact; one is
not, and applying the line as written refuses:

```
$ the applier with EXPECTED = the contract's checksum line, verbatim (keys 54)
refused: the read states keys = 54 and the table joins to 64
```

That transcript is the negative control and it is also a test
(`test_the_contracts_own_key_count_refuses_when_it_is_asserted_verbatim`). Without it the record
shows 64 asserted and verified, and a reader cannot tell that apart from a guard that was never able
to fire.

**Why 64 was asserted rather than the run stopped.** `keys` is the one field in that line the join
**over-determines**: every one of the 80 dump pair rows is claimed exactly once and none twice, so
the key count is forced by the data and cannot conceal a mistyped verdict. The four numbers that
*could* conceal one — rows, correct, wrong, accuracy — are the contract's, unedited, and all four
hold. No reading of this population gives 54: keys with `n=1` give 50, pages give 26, the v4 read
gives 45 — 54 is a digit slip off that 45. The record carries **both** numbers, names the field that
moved and says why (`checksum_deviation`), and `deviation()` refuses a `stated` line that deviates in
nothing, so the field cannot quietly become decoration.

#### The read this one extends (Dv238)

The contract's own provenance sentence — *"74 pairs against the team lead's documented printed values
from the v4 and decomposition reads — same reader, same pages; 6 pairs from the one new page 4446"* —
is a claim about a file on disk, so `carried_forward` checks it instead of repeating it:

| | keys | rows | correct | accuracy |
|---|---:|---:|---:|---:|
| shared with `results/sku_b_pair_verdicts.json` (`a61f1dce…`) | 45 | 61 | 20 | 0.3279 |
| new under v2 | 19 | 19 | 13 | 0.6842 |
| all | 64 | 80 | 33 | **0.4125** |

Every shared key carries the same verdict **and** the same `printed_old` as the sealed read; one that
did not would be refused by name, because a pair that already has a verdict is not re-adjudicated —
`attempts.on_failure` forbids exactly that. `n` is allowed to differ and is reported (`rows_whose_n_moved`
is empty here): `n` counts rows of a DUMP, and two instruments may extract one physical price box a
different number of times.

The 74/6 split the contract states is not checkable from here — which pages the team lead had
already documented is a fact about their own notes. What IS checkable is that 61 rows are the v4
read unchanged and 19 are new; and that the 19 land on the four pages v4 refused, derived from
`results/sku_b_positions_v4.json` rather than typed
(`test_the_nineteen_new_rows_are_exactly_the_four_pages_v1_refused`).

### Deliverable 2 — the verdict record finalised, and depth v2

```
$ PYTHONPATH=src python3 scripts/sku_bar_verdicts.py
results/sku_b_positions_skub2.json — 138 elements, unbought 0
  leaflet_brand_recall       0.9800 vs 0.75   PASS
  price_pair_accuracy        0.4125 vs 0.80   FAIL
  text_tier_accuracy         0.8667 vs 0.85   PASS
  bar 1 over 10 posts · micro 0.9459 · precision 0.9722222222
  bar 3 over 30 of 30 rows · 0 unreadable (0.0%)
  bar 2 over 80 pairs, the team lead's read — 0.4125 vs 0.80 — FAIL (n=80, read by the team lead 2026-08-12)
  closure: CLOSED — instrument not ready, BY MEASUREMENT (1 of 3 bars failed: price_pair_accuracy)
```

The closure block as written, with `attempts.on_failure` quoted out of the registration and the
failed bar derived from the verdicts rather than restated:

```json
{ "rule": "a failed bar closes B as 'instrument not ready' BY MEASUREMENT. No retry, no re-prompt,
           no second draw: a bar re-run after its own result is not the bar that was registered",
  "rule_source": "results/sku_pilot_prereg_b2.json attempts.on_failure, quoted verbatim",
  "verdicts": { "leaflet_brand_recall": "PASS", "price_pair_accuracy": "FAIL",
                "text_tier_accuracy": "PASS" },
  "failed_bars": ["price_pair_accuracy"],
  "passed_bars": ["leaflet_brand_recall", "text_tier_accuracy"],
  "undecided_bars": [],
  "state": "CLOSED — instrument not ready, BY MEASUREMENT",
  "why": "1 of 3 bars failed: price_pair_accuracy" }
```

Three strings in that producer stopped being true the moment bar 2 had a value, and all three are
written INTO the record the team lead opens: `contract` (now naming the close contract as well as the
run's), `class` and `scored_by.bar_2` (both naming the module that actually transcribed this read).
Dv170's own lesson, one session on. A new test pins the shipped record's closure to the **sha of the
read it was taken over**, so re-running the applier without re-running this producer reddens.

#### Depth-from-pct v2, n = 80

```
$ PYTHONPATH=src python3 scripts/measure_depth_from_pct_skub2.py
results/sku_b_positions_skub2.jsonl — 80 pairs against the team lead's printed_old
  badge                median 0.3212 pp · max 1.4171 pp · ≤1pp 79/80 · ≤2pp 80/80
  extracted_old_price  median 0.1670 pp · max 1.6366 pp · ≤1pp 75/80 · ≤2pp 80/80
  the badge IS an adequate depth instrument for a weekly median … and the old price the pipeline
  already extracts also is … Bar 2 fails on the printed NUMBER; on this population it does not fail
  on the DEPTH that number is used for
```

| instrument | v1, n=61 | **v2, n=80** |
|---|---:|---:|
| the printed `-N%` badge | 0.2886 pp median · 1.4171 pp max · 61/61 ≤ 2 pp | **0.3212 · 1.4171 · 80/80** |
| the extracted old price | 0.1761 pp median · 1.6366 pp max · 61/61 ≤ 2 pp | **0.1670 · 1.6366 · 80/80** |

**The one sentence in that output that is prose and not arithmetic was checked before it shipped.**
"Every error the team lead found is in the kopiyky" was measured on 61 pairs from 22 pages and now
rides on 19 rows from four pages v1 never read; the largest gap between a printed old price and the
extracted one anywhere in the 80 is **0.90 UAH** (199.90 printed, 199.0 extracted), and both
instruments stay inside the rule on the 19 alone. A hryvnia-scale error there would have made the
sentence false while every number around it stayed green
(`test_the_reading_lines_causal_clause_is_true_on_this_population`).

The adequacy rule and its tolerances are **deliberately unchanged** from v1 — two readings taken
under two rules are not two readings of the same thing. What moved is the sentence naming whose
threshold it waits on: v1's says "the operator's to set at the B′ design session", which has since
happened; v2's says the 5c2 ruling.

### Deliverable 3 — the ADR

`knowledge/decisions/skub2-b-prime-closed.md` (`4cba30ea…`), plus its INDEX row. Seven sections: the
three bars over both instruments, what (13) fixed measured as a diff between the two run records,
what it never touched (the split above), depth adequacy from both measurements, the programme's cost,
the product reading as a CANDIDATE for 5c2, and what the record does not decide.

**Bar 1 is stated as a reading and not decomposed.** 0.3603 → 0.9800 is each instrument against its
own registered gold and the gold was re-scoped between them (55 pairs / 15 posts → 37 / 10). The
like-for-like figure is the team lead's, quoted from SPEC 3.17 (14) and not re-derived here (SPEC
§10): v1 on the B′ gold reads **0.703**. What the remaining 0.277 is MADE of is not measured — three
amendments landed in one instrument, and the pilot's own §4 named a fourth candidate that is not the
instrument at all (the gold counts brands a reviewer could SEE; the instrument returns POSITIONS,
which is what (13)(c) moved out of the denominator). Dv236, carried forward rather than closed.

### What did not move

Hashed before the first write-capable action of this session and again at the end:

| file | before | after |
|---|---|---|
| `results/sku_b_pair_verdicts.json` | `a61f1dce0ff3a13e…` | unchanged |
| `results/sku_bar_verdicts.json` | `bb95f369d352f5fa…` | unchanged |
| `results/sku_b_positions_v4.json` / `.jsonl` | `fd0eb79695c2bc54…` / `e7d24a0a6b5aeff1…` | unchanged |
| `results/sku_pilot_prereg_b2.json` | `ad7b1c7e95e24fb9…` | unchanged |
| `results/sku_b_positions_skub2.json` / `.jsonl` | `d1715e8869d1ffcf…` / `5592b3248c17e485…` | unchanged |
| `results/spend_skub2.json` | `618a7d63c742bd6e…` | unchanged |
| `results/sku_depth_from_pct.json` | `23cb7215ae63e252…` | unchanged |
| `results/sku_miss_decomposition.json` | `f713a385178e2198…` | unchanged |
| `results/sku_reference_leaflet.json` | `e301bb4f48f527e4…` | unchanged |
| `results/spend_phase4.json` | `5e706e4f607846dc…` | unchanged |
| `results/sku_bar_verdicts_skub2.json` | `d27ae721948b194d…` | **`66124518ef5414a2…`** — the deliverable |

`diff` over the two hash listings reports exactly one line. Phase 4 stands where the run left it,
**$23.6653 of $25.00**: this session bought nothing.

### The artifacts

Re-hashed AFTER the final suite, because the tests import the producers' real paths:

| file | sha256 (16) | what |
|---|---|---|
| `results/sku_b_pair_verdicts_skub2.json` | `f780ef67432e951b…` | the 80 dictated verdicts, joined to the dump |
| `results/sku_bar_verdicts_skub2.json` | `66124518ef5414a2…` | the three bars and the closure |
| `results/sku_depth_from_pct_skub2.json` | `020cdc2734bfe730…` | depth v2, n=80 |
| `knowledge/decisions/skub2-b-prime-closed.md` | `4cba30eae8595c8b…` | the ADR |

**`git.dirty` in the three JSON artifacts**, the Dv227 disclosure repeated because it is still true:

| artifact | commit | dirty when written |
|---|---|---|
| `sku_b_pair_verdicts_skub2.json` | `c61fe365` | the three `knowledge/` files of the pre-contract checkpoint + the two applier scripts (committed one commit later) |
| `sku_bar_verdicts_skub2.json` | `866e86a8` | the same three + `sku_bar_verdicts.py` and its test |
| `sku_depth_from_pct_skub2.json` | `866e86a8` | the same three + the two depth scripts, `sku_bar_verdicts.py` and its test, and `sku_bar_verdicts_skub2.json` written minutes earlier |

Nothing under `src/` or `config/` was dirty for any of them, and `docs/STATUS.md` is absent from all
three because the team-lead commit went first.

### `make check`

```
$ make check
2013 passed, 2 skipped in 59.49s
```

1994 at the session's start, 2013 at its end: **19 new tests** — 11 for the skub2 applier, 6 for
depth v2, 1 for the closure drift check, 1 for the v4 applier's unchanged defaults.

### The per-commit checkout table

Every commit checked out for real, running ITS OWN suite; `HEAD` printed from `git rev-parse`, never
from the loop variable. **`74609da` is the parent and the control** — the same facts must read their
old values there, or the table is measuring the working tree.

| commit | prompt | applier / depth modules | pair verdicts | bar 2 | closure | depth v2 | ADR | suite |
|---|---|---|---|---|---|---|---|---|
| `74609da` **control** | absent | no / no | absent | — PENDING | UNDETERMINED | absent | no | 1994 ✅ |
| `c61fe36` | present | no / no | absent | — PENDING | UNDETERMINED | absent | no | 1994 ✅ |
| `a92f2d9` | present | **yes** / no | absent | — PENDING | UNDETERMINED | absent | no | 2006 ✅ |
| `866e86a` | present | yes / no | **64k/80r 0.4125** | — PENDING | UNDETERMINED | absent | no | 2006 ✅ |
| `5309dbc` | present | yes / **yes** | 64k/80r 0.4125 | — PENDING | UNDETERMINED | absent | no | 2012 ✅ |
| `ec29732` | present | yes / yes | 64k/80r 0.4125 | **0.4125 FAIL** | **CLOSED** | **n=80** | no | 2013 ✅ |
| `60eda29` | present | yes / yes | 64k/80r 0.4125 | 0.4125 FAIL | CLOSED | n=80 | **yes** | 2013 ✅ |
| `1157343` | present | yes / yes | 64k/80r 0.4125 | 0.4125 FAIL | CLOSED | n=80 | yes | 2013 ✅ |

Eight rows: `74609da` the control, and the seven commits of this contract that existed when the table
ran. The report commit and the vault tail postdate it, so they are not in it. The count and the clock
come from the command, not from the table's row count:

```
$ git log --reverse --format='%h %ad %s' --date=format:'%H:%M' 74609da..HEAD
c61fe36 19:40 docs(team-lead): the skub2-close contract and the STATUS pointer, unedited
a92f2d9 19:47 feat(skub2-close): bar 2's applier -- 80 dictated pairs, one deviated checksum, the read it extends
866e86a 19:47 data(skub2-close): the team lead's 80 pair verdicts over the skub2 dump
5309dbc 20:13 feat(skub2-close): the closure's producer re-pointed, and depth-from-pct over the 80
ec29732 20:15 data(skub2-close): B-prime closed by measurement -- 0.98 PASS / 0.4125 FAIL / 0.8667 PASS
60eda29 20:15 docs(decision): B-prime closed by measurement -- what (13) fixed, and what it never touched
1157343 20:15 test(skub2-close): derive the four newly-read pages from the v4 record, not from a list

$ git rev-list --count 74609da..HEAD
7
```

**Seven commits, 19:40–20:15 local**, and the report and the vault tail after this line make nine.

**The table found a red commit and it is the reason the table exists.** In the first ordering the
producer commit shipped `test_the_shipped_verdict_record_is_the_closure_over_the_read_on_disk`, which
reads `results/sku_bar_verdicts_skub2.json` — an artifact that only landed in the NEXT commit. `make
check` was green in the working tree (where the artifact had already been regenerated) and red at the
commit. The four affected commits were re-made with that one test moved into the commit that ships
the artifact it pins; the table above is the re-run. Dv240.

### Deviations

**Dv237 — the contract's checksum line states 54 keys and its own table dictates 64.** Asserted at
64, with both numbers, the field that moved and the reason in the record, and the verbatim line kept
as its own constant. Negative control transcript and the full reasoning above. Nothing measured
changes either way: the bar is 33/80 = 0.4125 under both.

**Dv238 — `carried_forward` and the record's `extends` block were not asked for.** The contract asked
for the sku-b-close pattern; this adds a check of the contract's own provenance sentence against the
sealed v4 read, and refuses a shared pair whose verdict moved. It earns its place — it is what makes
"same reader, same pages" a fact rather than a claim, and it produced the 20/61-versus-13/19 split
the ADR is built on — but it is an addition and is named as one.

**Dv239 — two of the contract's literal sentences are derived rather than transcribed.** Bar 2's
`stated` field reads `0.4125 vs 0.80 — FAIL (n=80, read by the team lead 2026-08-12)` where the
contract quotes `(n=80, team lead 2026-08-12)`; the closure block reads `CLOSED — instrument not
ready, BY MEASUREMENT` with derived `failed_bars`/`passed_bars` where the contract asked for `B′
CLOSED BY MEASUREMENT — bars 1 and 3 PASS, bar 2 FAIL`. Both are produced by code that is under test,
both say the same thing, and overwriting a derivation with prose is how a producer learns to soften a
verdict. Not edited.

**Dv240 — the first commit ordering left one commit red.** Found by the checkout table, not by `make
check`; fixed by re-committing with the artifact-pinning test in the artifact's own commit. The
general rule, now written into that test's docstring: **a test that reads a shipped artifact belongs
in the commit that ships it.**

**Dv241 — three existing files changed to produce two new ones.** The contract named the outputs and
not the route. `scripts/apply_sku_pair_verdicts.py` gained a `Read` spec (its own defaults and output
unchanged, pinned by a test), `scripts/measure_depth_from_pct.py` gained six keyword defaults and had
its `class` string lifted to a constant (its sealed record still equals the producer character for
character, pinned by a test), and `scripts/sku_bar_verdicts.py` had its three provenance strings
re-pointed. The alternative — copying two producers — would have put two matchers and two adequacy
rules in the tree.

### Assumptions stated

1. **The 74/6 provenance split is the team lead's own and is not checkable here.** Which pages they
   had already documented printed values for is a fact about their notes. What was checked instead:
   61 rows identical to the sealed v4 read, 19 new, and the 19 on exactly the pages v4 refused.
2. **`keys = 64` is a clerical correction, not a re-count of the sample.** See Dv237.
3. **The B′ verdict record is finalised in place**, not written beside itself. `results/sku_bar_verdicts_skub2.json`
   was written by the run with bar 2 PENDING and is the same file the closure belongs in; the sealed
   path this must never touch is the pilot's `results/sku_bar_verdicts.json`, and it did not.
4. **The depth v2 adequacy rule is v1's.** Only the sentence naming the pending ruling moved. A
   widened tolerance would have made the two readings incomparable in the direction of a nicer
   answer.

### What this leaves

1. **The 5c2 ruling** — the product reading in the ADR §6 is a candidate and nothing in it is
   authorised: question 7 served by promo + the printed badge, the extracted old price kept as a
   flagged depth input, the crossed-out number never trusted to the kopiyka.
2. **Dv236, open** — bar 1's 0.703 → 0.9800 is not decomposed, and decomposing it is a new
   measurement.
3. **Dv232, unpaid** — the (13)(a) parser warnings never reached the run record, so which warning
   kept which position alive is unrecoverable for this run. It needs a driver change before any
   future positions run.
4. **Dv176 and Dv223, carried** — `head["contract"]`'s resume branch omits 3.17 (12), and the
   driver's job-timeout margin literal is v1's model at v1's ceiling. Neither binds anything now.
