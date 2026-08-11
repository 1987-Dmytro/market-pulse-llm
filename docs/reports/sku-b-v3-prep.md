# sku-b-v3-prep — the resume, everything before the resumed session ($0)

## Read-back

**The five deliverables:**

1. **Pre-registration v3** — `results/sku_pilot_prereg_v3.json`, written by the producer, registered
   BESIDE v2 and committed before any artifact of the resumed session; `supersedes` names v2's sha
   and `moved` enumerates exactly four changes; every bar, threshold, R1–R5, both instrument shas
   and every pinned input byte-equal to v2, asserted row by row.
2. **Driver resume mode** — `--resume`, default off: buys only `population.unbought`, refuses a
   re-buy, an unbought-with-an-answer and moved `bought_already` pins; (11)(c)'s registered warm-up;
   go/no-go and in-run gate unchanged against $0.45; a merged bar-input record and a dump that gains
   the new rows with per-row provenance; `--smoke`/`--dry-run` prove the whole path with no network.
3. **Guard and record fixes (Dv151/Dv153)** — `runpod_guard.py` step ledgers normalise hyphen ≡
   underscore and refuse to create a second anchor for one step; the driver's `cost.jobs` splits
   into `jobs_planned` and `jobs_billed` (shipped as `jobs_submitted` — the briefed name has no
   producer, Dv154); both under test.
4. **Projection v2** — `results/sku_projection_v3.json`: 91 pages at the measured 5.0772 s/call
   (n=17, its one-job caveat named), 30 text calls bounded by the page marginal with srv-2d's 4.262
   s/row beside it, warm-up at 2 × the page marginal, boot as a range, idle tail $0.0184, against
   the $0.45 cap with headroom per corner, over named artifacts only.
5. **Preflight extension** — the resume guards driven both ways on the tiny-config model and fakes;
   every existing control kept.

**SPEC 3.17 (11)'s readings:**

* **(a)** Each element of the registered 138 is bought EXACTLY ONCE across the program: the resumed
  session buys only the 121 recorded as unbought, and the 17 existing answers — the parse refusal
  included — enter the bars as they stand and are never re-asked.
* **(b)** The instrument is FROZEN as registered: prompts, parser and serving pin unchanged; the
  superscript and asterisk findings are a post-pilot NAMED revision, never an in-flight edit.
* **(c)** The warm-up becomes REPRESENTATIVE: one real UNSENT page of the 51 outside the R2 gold and
  one real pre-filtered text row outside the 30-row pack; warm-up answers are never scored.
* **(d)** The resumed session's cap is $0.45, priced from the measured marginals, and every reading
  of (10) applies unchanged against it.
* **(e)** The team lead's calibration read of the 13 prefix pairs (6 correct) is NON-GATING: bar 2
  is scored only over the pairs of the COMPLETED population, at acceptance.

**The invariant: no paid calls in this contract.** No pod, no endpoint, no template, no `/run` — see
*Verify*.

---

## Step 0

| # | commit | what |
|---|---|---|
| 0.1 | `7e0632c` | team-lead docs committed unedited: `docs/SPEC.md` (the `-5` block), `docs/PROMPT-sku-b-v3-prep.md`, `docs/STATUS.md` |
| 0.2 | `f9d0a15` | the marker enumeration gains `sku-b-ratification-5` |
| 0.3 | `<vault>` | ADR `knowledge/decisions/sku-b-run-acceptance-and-resume.md` + INDEX |
| 0.4 | `<vault>` | the day's log, hot.md, the index |

The brief's prediction was exact — one test red on checkout, the marker enumeration:

```
$ python3 -m pytest tests/test_sku_prereg.py -q          # before 0.2
>       assert prereg.RATIFICATION_NAME.findall(spec_text) == [
E       AssertionError: assert ['sku-b-ratif...tification-5'] == ['sku-b-ratif...tification-4']
E         Left contains one more item: 'sku-b-ratification-5'
1 failed, 19 passed in 0.54s

$ python3 -m pytest tests/test_sku_prereg.py -q          # after 0.2
20 passed in 0.47s
```

The strip itself needed nothing — it is name-agnostic by design — and the SPEC pin still re-derives
after the extension, which is the proof that (11) moved no registered law: same stripped bytes, same
sha.

---

## D1 — pre-registration v3

`results/sku_pilot_prereg_v3.json`, sha `a80e8e55488439372244715f24f7bbfb56cf46a3a2586d38fa75a14c4c643656`,
commit `8767270`. Produced by `scripts/write_sku_prereg.py`, re-pointed at v3 the same way uni-b
re-pointed it at v2 — one producer, one strip, one bar-verbatim check.

```
$ PYTHONPATH=src python3 scripts/write_sku_prereg.py
wrote results/sku_pilot_prereg_v3.json
  leaflet_brand_recall   >= 0.75  (leaflet brand-recall ≥ 0.75 per page vs audit-visibl…)
  price_pair_accuracy    >= 0.8  (price-pair accuracy ≥ 0.80 on positions carrying a c…)
  text_tier_accuracy     >= 0.85  (text tier-assignment accuracy ≥ 0.85 vs adjudicated …)
  5 line(s) need a team-lead word before sku-b runs
  ladder 6a257e04375b4579… · prompts ca6303c1…/7250b87a…
  resume        17 bought, 121 to buy of 138 · cap $0.45
  warm-up page  data/annotation/captions_5c1/posts_media/atb_market_official_4476.jpg (0.32 MB, 1 of 51 never sent)
  warm-up row   @silposilpo:3370 post_text (548 chars, 1 of 739 outside the pack)
  supersedes    results/sku_pilot_prereg_v2.json d4ced2a8ba00b48b…
```

### The byte-equality, leaf by leaf

```
bars                   identical: True
ratification_required  identical: True
not_in_scope           identical: True
instruments            identical: True
ladder                 identical: True
pinned_inputs          identical: True
attempts key set equal: True
  MOVED attempts.cap_usd: '0.35' -> '0.45'
  MOVED attempts.verbatim: 'sku-b (one paid session, cap $0.35 GPU):' -> 'The (10)(b) stop at 17 of 138 gold calls'
new sections: ['resume'] · removed: []
moved entries: 4
```

`pinned_inputs` is compared **as a mapping**, not as a key set. The assertion that was already there
(`set(record["pinned_inputs"]) == {...}`) would pass a pin whose VALUE had moved — which is the only
way a pinned input can betray a bar.

Two things (11) required that are not in `moved` and are named rather than hidden:

* `resume.bought_already.serving_pin` carries the serving pin's sha instead of a sixth
  `pinned_inputs` entry, so (11)(b)'s freeze is registered without moving the pinned-input set;
* the record's own description (`phase`, `written_by`, `authority`, `class`, `generated_at`, `git`)
  necessarily moves — v2 was written before any sku-b artifact existed and v3 is not — and is listed
  in a sibling `supersedes.moved_metadata` (Dv157).

### The ordering rule v3 needed

The existing test could not be extended. `results/sku_pilot_serving.json` was added AFTER the v2
commit (`0577bef` vs `fc662e0`), so the old "no `results/sku_pilot_*` other than pre-registrations
existed" reading would fail v3 for being exactly what (11) asked for. What v3 proves instead is
narrower and stronger — at the commit that added it, the ONLY `results/sku_b_*` artifacts in the tree
were the two its `bought_already` pins, and `git show <commit>:<path>` hashed to what it pinned. That
rules out both directions: a resume registered after the resumed session had bought something, and a
resume registered against a record that has since moved (Dv156).

v2 leaves the producer's hands here exactly as v1 did, so it is **sealed by a literal sha**
(`d4ced2a8…`) beside v1's `b1bfa40d…`. It matters more than v1's did: v2 is the record the 17 paid
answers were bought under, and nothing rebuilds it now.

```
$ python3 -m pytest tests/test_sku_prereg.py -q
26 passed in 0.68s
```

---

## D2 — the driver's resume mode

`scripts/positions_gm4_skub.py`, commit `ae5d0ec`.

```
$ PYTHONPATH=src python3 scripts/positions_gm4_skub.py --resume --dry-run
page leg   91 pages sent (of 159 available, 19 posts) in 6 job(s), largest 7.99 MB
text leg   30 rows in 1 job(s)
dump       18 columns: item, page, file, sha256, brand_raw, brand_id, line, category, size, fat,
           price_promo, price_old, discount_pct_printed, price_qualifier, tier, depth,
           depth_disagrees_with_printed, bought_by
resume     SPEC 3.17 (11) under results/sku_pilot_prereg_v3.json
  bought    17 of 138 by results/sku_b_positions.json, never re-asked
  to buy    91 page(s) + 30 row(s) = 121 of 121 registered
  cap       $0.45 (11)(d) · anchor results/spend_sku_b_v3.json
```

`--resume --smoke` drives the whole write path with no network:

```
population: pages_sent 108 · text_rows 30 · asked 138 · asked_this_session 121 · unbought 0
dump rows:  95 (14 + 81)   columns: 18
outcomes:   138            bought_by: {'sku-b-v3': 121, 'sku-b': 17}
dump:                      bought_by: {'sku-b-v3': 81,  'sku-b': 14}
cost:       jobs_planned 7 · jobs_submitted 9 · cap_usd 0.45
resume.sessions: ['sku-b', 'sku-b-v3']
```

### The four refusals

Three guard the inputs and one guards the output, and they are deliberately at different layers,
because they are three different mistakes:

| # | fires in | on |
|---|---|---|
| 1 | `resume_plan` | a moved pin — the run record, the dump, or the serving pin ((11)(b): a resumed half served under another configuration is another instrument) |
| 2 | `resume_plan` | an id the registration calls unbought that already carries an answer in the record |
| 3 | `resume_population` | a bought id that reaches the SELECTION — checked on what is about to travel, because a filter with an inverted condition is what would put it there |
| 4 | `merge_sessions` | a source answered by BOTH sessions in the merged outcomes — the thing that would actually be scored |

All four fire, and each has its control, in D5's output below.

### The registered warm-up, not a re-picked one

(11)(c)'s two inputs are chosen ONCE by the producer and pinned; the driver reads them and never
re-derives the rule. A rule the paid run re-runs can disagree with the one that was registered, and
the disagreement lands on the go/no-go's input — the exact quantity this amendment exists to fix.
What the driver DOES re-check is the property (11)(c) cares about: the page is not one of the 108
sent, the row is not one of the 30 adjudicated, and both hashes re-derive (the page from disk, the
row from the raw store through the same `store_text` the pack used).

### Assumption: the resumed session writes NEW files

`results/sku_b_positions_v3.jsonl` / `.json`, containing the first session's rows plus the new ones.
This is **forced, not chosen**: v3 pins `sku_b_positions.jsonl` by sha, so an in-place append would
break — in the same commit the rows landed — the pin that proves the 17 answers were not re-asked.
The sealed pair stays evidence; the new pair is the merged bar input (Dv155).

```
$ python3 -m pytest tests/test_positions_driver.py -q -k "resume or merged or job_count or warm_up"
13 passed, 40 deselected in 0.84s
```

---

## D3 — the guard and record fixes

`scripts/runpod_guard.py`, commit `8211328`. Dv151 measured yesterday: `--step sku-b` created
`results/spend_sku-b.json` beside the driver's own `results/spend_sku_b.json`, holding the balance
AFTER the step had spent $0.0943 and a `step_spent_usd` of 0.0. Every number in it was false and
none of them looked it.

Two halves, and either alone leaves the hole open — the ledger FILE is normalised (hyphen and
underscore are one step; underscore wins, because that is what the driver writes), and inside it the
anchor key is looked for under BOTH spellings, because the driver writes
`runpod_balance_at_sku-b_start` into the underscored file. The test drives the exact collision:

```
$ python3 -m pytest tests/test_runpod_guard.py -q
15 passed in 0.05s

# the collision, replayed:
SKU-B SPENT      $0.1965 of $0.35  (anchor $12.42 from runpod_balance_at_sku-b_start)
# — and no "anchored …" line: an existing anchor is never written a second time.
# the control: a step that genuinely has no anchor still gets one.
```

Dv153: `cost.jobs` was the packing PLAN. The interrupted run recorded 8 while 4 submissions were
made, and read as a job count it said the session did twice the work it did. Split into
`jobs_planned` and `jobs_submitted`, with what each includes said in the record itself.

The 4 is what the test reproduces, and getting there needed a fix to the FAKE: the real
`EndpointClient` counts the `info` handshake as a submission and `FakeEndpoint` did not, so the
field's own prose ("includes the `info` handshake") would have been checked by a client where it was
false — the same shape of defect as the one Dv153 closes. The fake now counts its handshake, and the
test asserts the smoke's 4 beside the interrupted session's own `timing.calls = 4` against
`cost.jobs = 8`.

---

## D4 — the projection

`results/sku_projection_v3.json`, sha
`3f0b5693abf06469fc99638263d379254b6eff458f9ca7e8a257c5ab8bdbea47`, commit `b8eae3d`. It is
registered BESIDE `results/sku_projection.json`, which priced the pilot before anything had been
measured and is what the $0.35 cap was set against.

### The inputs, each by artifact path

| term | value | source |
|---|---|---|
| rate | $0.00030669/s | `results/srv2d_cost.json :: rate.usd_per_second` |
| page marginal | **5.0772 s/call, n=17** | `results/sku_b_positions.json :: projection.per_gate[0].marginal_seconds_per_call` |
| population | 91 pages + 30 rows | `results/sku_pilot_prereg_v3.json :: resume.bought_already.unbought` |
| text rate (stated) | bounded by the page marginal | assumption, below |
| text rate (neighbour) | 4.262 s/row | `results/srv2d_cost.json :: measured.like_for_like_seconds_per_row` |
| boot (measured) | 391.369 s | `results/sku_b_positions.json :: projection.boot_seconds` |
| boot (vis-c serverless) | 183.58 s | `results/captions_gm4_visc.json :: projection.per_slice[0].boot_seconds` |
| boot (srv-2b POD control) | 175.791 s | `results/d7_reread_srv2b.json :: pod_control_the_same_evening.cold_start_s_wall` |
| idle tail | 60 s = $0.0184 | `scripts/positions_gm4_skub.py :: IDLE_TAIL_SECONDS` |
| cap | $0.45 | `results/sku_pilot_prereg_v3.json :: attempts.cap_usd` |

### The arithmetic

`total = (boot + 2 × 5.0772 + 91 × 5.0772 + 30 × text_rate + 60) × 0.00030669`

```
measured on this endpoint class yesterday · bounded by the page marginal $0.3300  headroom +$0.1200  fits
measured on this endpoint class yesterday · srv-2d's image-free row      $0.3225  headroom +$0.1275  fits
vis-c's serverless boot on the same base  · bounded by the page marginal $0.2662  headroom +$0.1838  fits
vis-c's serverless boot on the same base  · srv-2d's image-free row      $0.2587  headroom +$0.1913  fits
the srv-2b pod control                    · bounded by the page marginal $0.2638  headroom +$0.1862  fits
the srv-2b pod control                    · srv-2d's image-free row      $0.2563  headroom +$0.1937  fits
break-even   8.2594 s/call at the worst boot (measured 5.0772)
```

**The decision it supports is the inequality, not the estimate.** At the worst boot the measured
page marginal would have to reach **8.2594 s/call — 1.63×** — before the cap is exhausted. The
interrupted session's error was **3.54×** in exactly that quantity, so the margin is real and it is
not unlimited; the go/no-go of (10)(a) remains what refuses, and under (11)(c) it finally has a
representative probe to refuse from.

### The two assumptions, stated

* **The text leg is BOUNDED, not measured.** No positions call has ever been made on text. Both legs
  run the same instrument at the same 800-token ceiling and a call with no image skips the vision
  prefill entirely, so at equal decode it cannot be slower than one that pays it. The stated corner
  therefore over-counts by however much of the 5.0772 s is prefill — in the safe direction for a cap.
  srv-2d's 4.262 s/row is a **neighbour** at a 256-token ceiling and is priced as its own corner,
  never as the stated rate: substituting a different instrument's rate is the class of error that
  made the first projection wrong.
* **The boot range's ends are different transports** (Dv158). 391.369 s is the only
  same-configuration reading. 175.791 s is a POD cold start — it pays no serverless container start,
  so it is a floor for a different thing and is carried as the optimistic end rather than as an
  expectation. vis-c's 183.58 s was added as the same-transport neighbour; it sits within 4.4% of the
  pod figure, which is why the caveat does not change the verdict. The **2.13× boot regression
  against vis-c is named and not diagnosed** — `worker-boot.log` is on volume `qw4nwleanc` and a
  staging pod can read it for near-free.

```
$ python3 -m pytest tests/test_sku_projection_v3.py -q
10 passed in 0.10s
```

---

## D5 — the preflight extension

`scripts/preflight_serving_guards.py`, commit `fa2fd0f`. Run under the rebuilt peft venv (Dv160).

```
local   transformers 5.14.1 · peft 0.20.0 · torch 2.13.0
volume  transformers 5.14.1 · peft 0.20.0

--- SPEC 3.17 (11): the resume ---

9. the registration          121 to buy, 17 already bought   <- the control: it ACCEPTS
   a moved dump pin               REFUSE — the per-position dump hashes 4178ce5e53559c84… and results/sku_pilot_prereg_v3.json pins 0000000000000000… — the resume
   a moved serving pin            REFUSE — the serving pin hashes 5f900beb555f12f5… and the registration pins 0000000000000000… — SPEC 3.17 (11)(b) freezes the ins
   an unbought id with an answer  REFUSE — 1 id(s) the registration lists as UNBOUGHT already carry an answer in results/sku_b_positions.json — data/annotation/cap

10. the selection            a bought id     REFUSE — the page leg selected 1 id(s) the first session already bought — data/annotation/captions_5c1/posts_media/atb_
    an unbought id           1 kept   <- the control

11. the (11)(c) warm-up      atb_market_official_4476.jpg 0.32 MB · row @silposilpo:3370 (548 chars)   <- the control: ACCEPT
    a page inside the sent 108 REFUSE — …is one of the 108 SENT pages: the registered warm-up page is inside bar 1's page set (R2)…
    a row inside the 30      REFUSE — @VARUS_channel:7119 is one of the 30 adjudicated rows: …3.17 (9) opens on inputs NO bar is scored on.

12. the merged bar input     a source bought twice  REFUSE — 1 source(s) carry an answer from BOTH sessions — …atb_market_official_4340.jpg….
    an unbought source       18 outcomes   <- the control

PASS  the fixed guard ACCEPTS a bare real model
PASS  the fixed guard REFUSES an adapter-carrying one
PASS  the control fires: the vis-a guard refuses the bare model
PASS  POSITIONS serves the base with no adapter directory
PASS  POSITIONS refuses ADAPTER_DIR
PASS  POSITIONS refuses MERGED_DIR
PASS  POSITIONS refuses an unpinned base
PASS  the adapter refusal reaches the POSITIONS config too
PASS  every config x op cell behaves as CONFIG_OPS says
PASS  a job exactly at the payload budget passes
PASS  a job one byte over it refuses rather than shortening the album
PASS  a truncated tail is a parse REFUSAL, never an empty answer
PASS  the control: an empty array is an ANSWER and is accepted
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
EXIT=0
```

24 checks, 0 FAIL, every existing control kept (13 of them predate this contract).

---

## Verify

```
$ make check
1780 passed, 2 skipped in 54.68s

$ ruff format --check .
226 files already formatted

$ runpodctl pod list -a          → (not run: no RunPod resource was created or destroyed
$ runpodctl serverless list      →  in this contract, so there is nothing to tear down.
                                    The $0 invariant is that no such command was issued.)
```

**No paid call was made.** No pod, no endpoint, no template, no `/run`, no `runpodctl` invocation of
any kind. The only network access in the whole pass was `pip install peft==0.20.0` into a scratch
venv outside the repo (Dv160). Every artifact above was produced from files already in the checkout.

## Deviations

**Dv154 — `jobs_billed` as briefed has no producer, and the field is named for what it is.** The
brief asks for `jobs_billed` "from the endpoint's own health read where present". There is no health
read on `serving.EndpointClient`; its `timing()["calls"]` counts terminal `/run` submissions,
including the `info` handshake and both warm-up calls. Adding a health endpoint would be a new
network path in a $0 contract. The field is therefore `jobs_submitted`, and the record says in its
own `jobs_reading` what it counts.

**Dv155 — the resumed session writes new artifact files instead of appending in place.** Forced by
D1: `resume.bought_already.dump.sha256` pins `results/sku_b_positions.jsonl`, so an append would
break the pin that proves the 17 answers were not re-asked. The merged pair is
`results/sku_b_positions_v3.{json,jsonl}`; those names are the executor's choice, the brief did not
fix them.

**Dv156 — v3 has its own ordering test rather than an extension of the existing one.** Reason and
evidence in D1 above (`results/sku_pilot_serving.json` post-dates the v2 commit).

**Dv157 — `supersedes.moved` carries the four briefed entries; a sibling `moved_metadata` names what
else necessarily moved.** The record's own self-description cannot stay v2's without lying. Naming
it separately keeps `moved` exactly the contract-level list the brief enumerates, and
under-reporting a change would have been the worse failure.

**Dv158 — a third boot corner was added and the briefed lower end is labelled as a pod.** The brief
names `[175.8 historical, 391.4 measured yesterday]`. 175.791 s is `results/d7_reread_srv2b.json ::
pod_control_the_same_evening.cold_start_s_wall` — a POD, a different transport. It is kept as the
brief names it and vis-c's 183.58 s serverless boot is carried beside it, which is what makes the
caveat checkable: 4.4% apart, verdict unchanged.

**Dv159 — the (10)(a) refusal message now says "a re-registration" instead of "a v3 registration".**
The same stop can fire inside the resumed session, which already runs under v3. One existing test
assertion moved with the wording; nothing else changed on that path.

**Dv160 — the peft venv of Dv138 was gone and was rebuilt.** It was a scratch venv and scratch dirs
do not survive. Rebuilt with `python3 -m venv --system-site-packages` + `pip install peft==0.20.0`
in the session scratchpad; `transformers` 5.14.1 and `torch` 2.13.0 were already present and are the
volume's versions. No repo dependency moved; `pyproject.toml` is untouched.

## Assumptions

1. **The resumed run's artifact paths** (`results/sku_b_positions_v3.*`, `results/spend_sku_b_v3.json`)
   and the `bought_by` provenance column are the executor's naming; the brief specified the
   behaviour, not the names.
2. **The serving pin is registered inside `resume.bought_already`** rather than as a sixth
   `pinned_inputs` entry, so that `moved` stays the four briefed items and `pinned_inputs` stays
   byte-equal to v2. (11)(b)'s freeze is enforced either way — the driver refuses a pin that does not
   match.
3. **`--resume` composes with `--leg`.** A resumed page-only or text-only run is legal and its record
   names the smaller population honestly; the merge and the refusals behave identically.
4. **`jobs_submitted` is null-safe.** A client that reports no clock yields `None` rather than a
   crash, the same reading `billed_seconds` takes.
5. **The 121-element population is the registration's, not the record's.** The two are asserted equal
   as SETS before anything travels; if they ever disagree the run refuses rather than picking one.

## Commits

| # | commit | what |
|---|---|---|
| 0.1 | `7e0632c` | team-lead docs, unedited |
| 0.2 | `f9d0a15` | the marker enumeration learns the fifth block |
| D1 | `8767270` | pre-registration v3, registered beside v2 |
| D2 | `ae5d0ec` | `--resume`, the four refusals, the merged bar input, the `cost.jobs` split |
| D3 | `8211328` | one step, one anchor, however its name is typed (Dv151) |
| D4 | `b8eae3d` | the resumed session priced from what the interrupted one measured |
| D5 | `fa2fd0f` | the preflight learns the resume guards, both ways |
