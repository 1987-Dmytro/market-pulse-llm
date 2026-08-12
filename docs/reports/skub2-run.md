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
