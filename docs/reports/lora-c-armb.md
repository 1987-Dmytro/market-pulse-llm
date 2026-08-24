# `lora-c-armb` — arm B is a file, the money is re-derived, and the header carries a tell

**Contract:** `docs/PROMPT-lora-c-armb.md` · **executed 2026-08-24** · **spent $0.0000** · no pod, no
endpoint, no paid call · the registration is still a **DRAFT** and its attempt is **UNSPENT**.

Everything below was bought on this Mac. The stock probe is a listing and created nothing.

| commit | what |
|---|---|
| `b646361` | the previous contract's vault tail, landed before this one could claim it |
| `34cc939` | (a) team-lead files verbatim — `docs/STATUS.md` day 24.08 with ruling (н), `docs/PROMPT-lora-c-armb.md` |
| `ba14ca4` | (b) step 0.5 — `make check-stamped`, the moving-tree verifier as an instrument |
| `fe0cc87` | (c) the producer, `results/pass1_sft_v3_arm_b.jsonl`, the censuses, the D1 tests |
| `b2ed1b3` | (d) the registration DRAFT v3, the re-derived money block, the stock probe, the D2 tests |
| (e) | this report + the ADR |
| (f) | the vault tail |

---

## 0 — the read-back gate, one line each

Every number re-derived from the file that owns it, before step 1.

| asked | derived from | reading |
|---|---|---|
| the (н) clauses | `docs/STATUS.md` п. 1 (н), lines 253–263 | «сначала $0-контракт на датасет арма B» · «Кап оставить $4.00 — решать после выбора объёма» · the two design rulings of 24.08 |
| the rendering rule | `docs/PROMPT-lora-c-armb.md` D1 | same renderer, same pool of 515, five per-class neighbours, own-thread block, equality refusal; target shape identical; provenance tag on every row |
| pass-2 = 2 legs | `docs/STATUS.md` (н), second design ruling | «проход-2 в ране — ТОЛЬКО для армов (2 ноги, не 4)» — quoted into the record, not paraphrased |
| 666 = 506 + 160 | the two files on disk | `wc -l results/pass1_sft_v3_train.jsonl` = 506 · `results/synthetic_pass1_v1.jsonl` = 160 |
| arm-B weight 4.1625 | `train_qlora.class_weights`, called | 666/(5·32) = 4.1625 with `PASS1_K` = 5 read from the module; 32 `молочный_бренд` rows, **all synthetic** — arm A has 0 |
| the break-even shape of §4 | `results/prereg_lora_c.json::money.pre_pod_arithmetic` | fixed part / cap → the largest s/step the cap can pay for, in the unit the smoke measures; no s/step registered |

No mismatch with any registered number. Two things the read-back *added*: the 160 rows sit in
**four** threads of 40 (`synthetic:<error class>`), and the 32 `молочный_бренд` targets are 8 per
class — which is where §3's finding comes from.

---

## 1 — the money, read from the guard

```
CYCLE 2 SPENT     $8.3043 of $20.00
REMAINING         $11.6957
```

`runpodctl pod list -a` → `[]`. `runpodctl serverless list` → `[]`. Before and after.
**$0.0000 attributable to this contract**; the growth since the team lead's reading of $8.2946 is
the `mp-srv2` volume's always-on rent, named separately per 3.23 (4).

---

## 2 — step 0.5: the verifier stops being a habit (`ba14ca4`)

Twice in two contracts a ten-minute reading had to be KILLED rather than quoted — Dv785 in
`lora-c-close`, Dv792 in `lora-c-run`. Neither offending edit was code: one was a fix I had just
decided on, the other was the operator's ruling landing in `knowledge/hot.md`, out of which
`scripts/volume_calc_5c1.py` greps a price literal that nine tests depend on.

`make check-stamped` → `scripts/check_stamped.py`: `HEAD` and `git status --porcelain` before and
after the suite, exit **2** with «reading VOID — the tree moved» if either changed outside the
whitelist. It writes nothing — a stamp file under a tracked path would be the very move it checks
for. The suite's own exit code is printed beside the verdict and never replaces it: a green suite
over a moved tree is still VOID.

**Driven three ways on the real git surface, not reasoned about:**

```
$ python3.11 scripts/check_stamped.py true
suite   true → exit 0
reading HOLDS — HEAD 34cc939, tree unmoved outside ['knowledge/daily_logs/']

$ python3.11 scripts/check_stamped.py sh -c 'touch results/.void_probe'
suite   sh -c touch results/.void_probe → exit 0
reading VOID — the tree moved: HEAD 34cc939 → 34cc939, porcelain ['?? results/.void_probe'].
The suite's exit code above describes neither tree and may not be quoted.        (exit 2)

$ python3.11 scripts/check_stamped.py sh -c 'echo "- probe" >> knowledge/daily_logs/2026-08-24.md'
reading HOLDS — HEAD 34cc939, tree unmoved outside ['knowledge/daily_logs/']     (exit 0)
```

The middle one is the negative control that matters: **a GREEN suite, refused.**

**The whitelist is licensed by a check that runs.** `knowledge/daily_logs/` is exempt because no
test opens it, and `test_the_whitelisted_directory_is_read_by_no_test` parses every test module and
refuses a CALL carrying that name — or the name of either hook that reads the directory and writes
`hot.md`. A plain grep could not do it: this file's own fixtures name the directory. The scan's
ceiling is stated where it lives — a path assembled from parts, or bound to a name first, evades it
exactly as it would evade a grep.

**What the whitelist does not license,** and it is written beside it: `scripts/refresh-hot-cache.py`
reads `knowledge/daily_logs/` and WRITES `knowledge/hot.md`. The exemption covers the day-log file
appearing, never a cache refresh mid-run. `knowledge/hot.md` and `knowledge/index.md` are outside it
by name, and the test above asserts both directions.

---

## 3 — D1: arm B's dataset (`fe0cc87`)

`scripts/build_lora_c_data.py --arm-b-out`. Nothing re-implemented: `examples_for` (so
`fewshot.neighbours` through amendment 3.25 (2)'s pre-filter), `render_v3` and `target_v3` are the
same functions arm A's 506 go through, which is the only reason the two arms compare.

**The prefix is checked against the SHIPPED bytes, before the write.** Comparing the prefix with the
bytes the same call is about to write would prove nothing; the file is read first and a diff is a
STOP naming the first differing line. The refusal guards the plain rebuild too —
`results/pass1_sft_v3_train.jsonl` is on this contract's DO-NOT list by name — and its negative
control is a test, not a paragraph.

### The censuses, each printed and written

**(1) Encode, over all 666** — `train_qlora_v3.py --census`, `train_qlora.encode_pass1` with the
real tokenizer at the revision `config/qlora.yaml` pins:

| rows | encoded | refused | min | median | max | `max_seq_len` | headroom |
|---|---|---|---|---|---|---|---|
| 666 | **666** | **0** | 1 445 | 1 603 | 2 975 | 3 072 | **97** |

The widest row is `@tarilka_malyuka:746#83` — **a real one**. No synthetic row is anywhere near the
ceiling, and the widest synthetic request is 6 436 chars against arm A's 9 241. Arm A's census
re-taken with the same instrument for the pair: 506/506, 0 refused, median 1 633, same max, same
headroom.

**(2) `class_weights` on arm B → FIVE classes:**

| class | rows | w_c |
|---|---|---|
| `не_наш_рынок` | 300 | 0.444 |
| `null` | 196 | 0.679592 |
| `категория_личное` | 72 | 1.85 |
| `сеть_ритейлер` | 66 | 2.018182 |
| **`молочный_бренд`** | **32** | **4.1625** |

666/(5·32) = 4.1625, re-derived in the test from the counts rather than compared to a literal. Arm A
returns four classes and no `молочный_бренд` at all — that asymmetry is the whole of the ablation.

**(3) Isolation — six readings, and the fifth is a finding:**

| # | reading |
|---|---|
| 1 | 800 examples across the 160 queries, **228 distinct**, **0 outside the pool** |
| 2 | over all **666** rows: **0** synthetic ids used as an example; **0** pool rows with a `synthetic:` thread |
| 3 | **0** example texts equal to their query (amendment 3.25 (2), through the pre-filter); **0** synthetic texts in the pool at all |
| 4 | synthetic ∩ E (198) = **0** · ∩ holdout-100 = **0** · ∩ gold-14 = **0** |
| 5 | **the header tell — below** |
| 6 | example slots: `молочный_бренд` is **1** distinct row in both the 506 and the 160 |

**(4) Length:** widest arm-B request 9 241 chars (a real row), widest synthetic 6 436, median
synthetic 5 381, ceiling `PASS1_MAX_INPUT_CHARS` = 12 000, synthetic headroom **5 564**.

### The finding the contract did not ask for — Dv795

The ruling names the renderer, the pool, the neighbour rules and the target shape. It does **not**
name the four HEADER fields the renderer needs — `channel`, `post_id`, `topic`, `entities` — and a
synthetic row has no store to read them from. What was built takes the branch the existing rules
already take: `synthetic:brand_vs_retailer` splits where `@tarilka_malyuka:746` splits, an absent
post renders `prompts.NO_POST_TEXT`, an empty entity list renders «(this thread resolved no
entity)». Nothing invented, nothing borrowed from a real thread.

**That leaves a marker, and it was measured rather than assumed** — every header line of the 160
counted against the 506, not only the lines common to all of them (the first version of the
instrument intersected the 160 and found ONE tell; the thread tag carries the error class, so it
differs between the four groups and the intersection could not see it):

| line | in the 160 | in the 506 |
|---|---|---|
| `(this post has no text of its own — it is an image or a video)` | **160** | **0** |
| `<thread channel="synthetic" post_id="brand_vs_retailer">` | 40 | **0** |
| `<thread channel="synthetic" post_id="retailer_non_dairy">` | 40 | **0** |
| `<thread channel="synthetic" post_id="non_dairy_brand">` | 40 | **0** |
| `<thread channel="synthetic" post_id="mention_vs_about">` | 40 | **0** |
| `(this thread resolved no entity)` | 160 | 284 — **not** a tell |

**All 160 rows are marked, and those 160 carry all 32 `молочный_бренд` targets in this line.** So an
adapter can condition that class on a marker that appears in no eval request, and «synthetic did not
help» becomes indistinguishable from «the model learned the marker» — a confound on the one
comparison arm B exists to make.

Why the alternative is worse: a synthetic row wearing a real channel and a real post id fabricates
provenance inside training data, and breaks the property `build_lora_c_synthetic.py` rests its whole
isolation on — that the `synthetic:` prefix makes every downstream refusal one string comparison.
The topic line is also the one that is FALSE: «it is an image or a video» describes a post that does
not exist. An honest replacement string would be a NEW registered string and a louder marker still.

The examples block, where a reader looks first, is clean: the pool holds exactly one
`молочный_бренд` row, so that slot shows the same row to every query in this line, real or
synthetic.

**This is reported, not repaired.** Changing what the header carries is a rendering decision, and the
rendering is the team lead's ruling.

### And a near-miss caught by a diff, not by a guard — Dv796

The first plain rebuild of `results/lora_c_data.json` silently deleted the whole `review_gate_1`
block — **15 keys**, including the boundary census the team lead's verdict ruled on. It is written
only under `--sample`, so a build without that flag replaces the record with one that has never
heard of it, with nothing raising and nothing in the output saying so. Caught by the key-path diff
and now refused **before any write**; driven both ways, with the train file's sha unmoved across the
refusal. The record's only remaining change is `produced_by.sha256`:

```
results/lora_c_data.json vs HEAD:  ADDED 0   REMOVED 0   CHANGED 1
  ~ .produced_by.sha256   e94afe31… → 648833b3…
results/pass1_sft_v3_train.jsonl unchanged vs HEAD: True
```

---

## 4 — D2: the registration, and the derivation the operator rules on (`b2ed1b3`)

`population.train` now names **both** files with their shas, the prefix rule and ruling (н)'s
rendering clause quoted through `quoted()`. `legs.arm_a`/`legs.arm_b` carry their `train_file`;
`frozen_when_the_pod_exists` grows by exactly `results/pass1_sft_v3_arm_b.jsonl` and
`results/lora_c_arm_b.json` and loses nothing. `train_qlora_v3.registered_training_shas()` reads
both, and `registered_first()` now REFUSES rather than let a `--census` default pick an arm in
silence — with two registered datasets, «the first one» would publish a 506-row census under a
report that says 666.

### The re-derived money

Ruling (н) fixes pass 2 at **2 legs**, not 4. That is the **only** term that moved: no rate
re-estimated, no row count touched, both arms' step counts (62 and 82, `planned` 64 and 84)
registered before either contract.

```
fixed  = boot 500 + load 300
       + base legs        2 × 198 × 6.14 = 2 431.44
       + adapter evals    2 × 198 × 6.14 = 2 431.44
       + pass-2           2 ×  11 ×  97  = 2 134.00      ← was 4 × 11 × 97 = 4 268.00
       + training smoke   6 × (121.0 × 1.5) = 1 089.00
       = 8 885.88 s                                       ← was 11 019.88 s
```

| price | source | budget | fixed | left for 144 steps | **break-even s/step** | readings under it |
|---|---|---|---|---|---|---|
| **$0.80/h** | lora-b rung 1 — a create refuses above it | 18 000.0 s | $1.9746 | 9 114.1 s | **63.29** | 61.047 |
| **$0.74/h** | what the last five pods billed | 19 459.5 s | $1.8265 | 10 573.6 s | **73.43** | 61.047 · 68.442 |

**`lora-c-run` reported 48.47 / 58.61 and called the plan short. At the ruled scope it no longer
is.** lora-b's registered 61.047 fits at both prices; its measured 68.442 fits at the price the last
five pods actually billed and not at the worst one a create is allowed at. The saving is
**2 134 s = $0.4742**, exactly the «~$0.47» the ruling names.

**Still no s/step is registered.** Both readings were taken on sequences of at most 1 222 tokens
against this line's 1 445–2 975, and `config/qlora.yaml`'s own comment says a raised `max_seq_len`
«changes no step time … except on the batches that need it» — here every batch needs it. The smoke
buys the rate. Hard stop = cap / worst rate = **18 000 s**.

The verdict is published as a FIELD — `readings_under_the_break_even` — beside the sentence, so a
test checks the finding instead of parsing prose.

**The projection rung's scenario, on the same accounting.** At the sibling-measured rates
(2.694083 s/call from pass1-window r2's own pod, 23.760 s/thread from pass2-signals r2's — 0.439 and
0.245 of the charge) the fixed part is 4 545.4 s and the break-even rises to **93.43 s/step at
$0.80/h · 103.57 at $0.74/h**. Both columns now charge the smoke identically and divide by **144** in
each; `lora-c-run` charged it in one column and divided by 144 + 6 in the other, which priced one
quantity two ways.

**What `bars` still says, reconciled without touching it.**
`bars.report_only.pass_2_tables` reads «per leg» and this contract may not edit `bars`. The
reconciliation lives in the money block and nowhere else: the tables are per leg for the legs that
RUN, and the ruling says those are the two arms — base v2's end-to-end BEFORE column is
`pass2-signals-r2`'s registered 4 of 5 on two signals, already bought, and base v3 takes no bar.

### The stock probe — read-only, and it dates the card question

`results/lora_c_stock_probe.json`, read at **2026-08-24T08:24:02Z**. `runpodctl gpu list
--include-unavailable` and `runpodctl datacenter list`; **nothing was created, started or stopped.**
The region is not a preference — EU-RO-1 is read out of `results/d7_reread_srv2b.json` as the
datacenter chosen for the network volume, and a pod that cannot mount the volume is a different
plan.

**The card ruling (к) names:** `RTX A6000` 48 GB → **`none`**. `A40` 48 GB → not catalogued in
EU-RO-1 at all. Seven of 47 catalogued cards report stock other than `none` there:

| card | memory | secure $/h | community $/h | stock |
|---|---|---|---|---|
| RTX 2000 Ada | 16 GB | $0.24 | — | Low |
| L4 | 24 GB | $0.49 | — | Low |
| RTX PRO 4000 | 24 GB | $0.57 | — | Medium |
| **RTX PRO 4500** | **32 GB** | **$0.72** | — | **High** |
| RTX 4090 | 24 GB | $0.74 | $0.34 | Low |
| RTX PRO 6000 | 96 GB | $2.09 | $1.69 | Low |
| B200 | 180 GB | $6.79 | $5.98 | Low |

Listed, priced, and **not chosen**: the card is the operator's word beside the cap. A listing is not
a create — stock at create-time may differ in both directions, the only free test of a create is the
create, and the create is also this record's freeze, so the two cannot be separated. What a
different card would move is stated too: every second in `fixed_seconds` was measured on a 4090 or
charged from one, so another PRICE re-prices the budget and another CLASS re-prices the seconds, and
this record holds no reading of any of them.

The matcher behind that table was wrong on its first run and is fixed: `"A40" in "RTX A4000"` is
true, so a 16 GB card was answering for a 48 GB one. Matched by equality now.

### Proof that only what was meant to move, moved

```
results/prereg_lora_c.json vs the (c) commit:
  ADDED   103   .money.pre_pod_arithmetic 74 · .population.train 20 · .legs 4
                · .authority 3 · .frozen_when_the_pod_exists 2
  REMOVED   9   the two superseded money keys, and population.train's flat file/sha/rows/distribution
  CHANGED  21   6 money cells · fixed_seconds.pass_2 and .total · the verdict · the state
                · 3 scenario cells · producer.sha256 · 6 list-index shifts in frozen_when_the_pod_exists
  the frozen SET grew by exactly ['results/lora_c_arm_b.json', 'results/pass1_sft_v3_arm_b.jsonl'] and lost nothing
```

`bars` untouched, `bars.attempt` still «ONE. No retry, no second draw…», `state` still
«DRAFT — frozen only by lora-c-run's first `pod create`», `hard_stop_seconds` still a sentence and
not a number, no price key anywhere.

---

## 5 — the numeric session audit

There was no session. Every count is zero and the table's job is to say so with readings.

| axis | reading |
|---|---|
| pods created | **0** — `runpodctl pod list -a` → `[]`, before and after |
| serverless endpoints | **0** — `runpodctl serverless list` → `[]` |
| per-leg call counts | base v2 **0** · base v3 **0** · arm A **0** · arm B **0** (of 198 each) |
| pass-2 threads run | **0** of 11 × 2 |
| optimizer steps run | **0** of 144, and **0** of the 6 smoke steps |
| paid API calls | **0** — the only network reads were two `runpodctl` listings and the guard's billing walk |
| refusals seen on a pod | **0** — every refusal in §3 and §4 was bought at $0 on this Mac |
| spend, balance delta | **$0.0000** attributable · cycle-2 $8.3043 both before and after |
| spend, billing walk | **$0.0000** attributable; the only live resource is the `mp-srv2` volume's always-on rent |
| guard reading vs cap | $11.6957 remaining of $20.00 · the $4.00 cap untouched |
| attempt | **UNSPENT** — no eval output of any leg was seen |

Artifact shas (first 16), the tree this report is written against:

| artifact | sha256 |
|---|---|
| `results/prereg_lora_c.json` | `ea65fe19e0f17446` |
| `results/pass1_sft_v3_arm_b.jsonl` | `85a5b278550e8771` |
| `results/pass1_sft_v3_train.jsonl` (unmoved) | `cf55d3f202161398` |
| `results/lora_c_arm_b.json` | `0be40db13489a017` |
| `results/lora_c_encode_census_arm_b.json` | `6f0c96c21d484811` |
| `results/lora_c_stock_probe.json` | `637485d554bd4fb8` |
| `scripts/build_lora_c_data.py` | `feab33005cc874c0` |
| `scripts/train_qlora_v3.py` | `2f265e6d895670bb` |
| `scripts/write_lora_c_prereg.py` | `ff5136679fb2fcd5` |
| `scripts/check_stamped.py` | `f16c6b78a4a34b13` |
| `scripts/probe_a6000_stock.py` | `b4beeb7c6ebd6ea7` |
| `scripts/train_qlora.py` (PINNED, unmoved) | `1a1a0b5983db60d8` |
| `config/qlora.yaml` (revision 3, unmoved) | `96b4b31865576c24` |
| `src/market_pulse/pass1_v3.py` (unmoved) | `9baab0e92078c137` |

---

## Deviations from Dv793

Each with its cause tag from the closed enum v2. **Every one was found at $0.**

| # | cause | what |
|---|---|---|
| **Dv793** | `[cause: contract-gap]` [[a_registered_bar_may_have_no_producer]] | **Step 0's commit list (c)/(d) cannot be separated as written, and one of the two commits would have been RED.** `results/lora_c_data.json` carries `produced_by.sha256`, `results/prereg_lora_c.json` pins that record's sha, and `tests/test_lora_c_prep.py::test_every_producer_is_driven_end_to_end_and_rebuilds_its_shipped_bytes` drives both producers — so editing `scripts/build_lora_c_data.py` forces a registration rebuild in the SAME commit. Measured, not assumed: with (d)'s files stashed, that test failed on `write_lora_c_prereg.py`. Resolved without merging the commits, by rebuilding the registration in (c) with the OLD producer — a pack-sha refresh and nothing else — and landing the money re-derivation in (d). Both commits are green in isolation; the cost is one extra registration build. |
| **Dv794** | `[cause: verify-gap]` [[a_prefilter_cannot_certify_the_population]] | **The first header-tell instrument found ONE tell and there are five.** It intersected the headers of all 160 synthetic rows and reported the lines common to every one of them — but the thread tag carries the error class, so it differs between the four groups of 40 and the intersection could not see it. A rule that finds a marker only when it marks the whole batch is the wrong instrument for a batch built in four groups. Now every header line of the 160 is counted against the 506 and the tells fall out of the counts. Found because the printed answer was one line where the `channel="synthetic"` tag obviously belonged. |
| **Dv795** | `[cause: contract-gap]` [[blinding_leaks_are_distributional]] | **Every synthetic row carries a marker no eval request will ever show, and those rows hold all 32 `молочный_бренд` targets.** Five header lines, in 160 of 160 and 0 of 506; the loudest is `NO_POST_TEXT`, which not one real row of this pool renders. Ruling (н) names the renderer, the pool and the target shape and does not name `channel`/`post_id`/`topic`/`entities`; what was built takes the branch the existing rules take, and the alternative fabricates provenance and breaks the `synthetic:` prefix the isolation rests on. Consequence: an adapter can condition `молочный_бренд` on the marker, and arm B's whole point — «did the synthetic top-up help» — stops being separable from «did the model learn the marker». Reported and NOT repaired: what the header carries is a rendering decision, and the rendering is the team lead's. |
| **Dv796** | `[cause: verify-gap]` [[rewriting_a_record_resets_state_you_do_not_own]] | **A plain rebuild deleted `review_gate_1` — 15 keys — from a DRAFT-pinned record, silently.** The block is written only under `--sample`; a build without it replaces the record with one that never had it, with no guard raising and no output line. Caught by the key-path diff of the rebuild, not by anything in the build. Now refused before any write, driven both ways, and the train file's sha is unmoved across the refusal. |
| **Dv797** | `[cause: tooling]` [[run_the_instrument_on_the_named_example]] | **The stock probe's card filter matched a 16 GB card for a 48 GB one.** `WANTED = ("A6000", "A40")` matched by substring, and `"A40" in "RTX A4000"` is true — so the first reading reported `{'RTX A4000': 'none', 'A40': None, 'RTX A6000': 'none'}` and a reader would have taken the A4000 row for the card ruling (к) names. Matched by `displayName` equality now, and the constant carries the reason. Caught by reading the instrument's own output against the example it is about. |
| **Dv798** | `[cause: verify-gap]` [[a_flag_that_asserts_turns_a_poll_into_a_verdict]] | **Two shipped tests asserted a FINDING that ruling (н) superseded, and fixing them looks exactly like fixing a broken test.** `test_the_derivation_solves_the_cap_inequality_backwards` asserted «neither reading fits under the bar» — true at four pass-2 legs, false at two — and `test_the_registration_names_no_arm_b_dataset` asserted a gap this contract closed. The first now re-derives WHICH readings fit and compares that against the record's own machine-readable field, so it stops pinning a direction; the second is renamed `test_the_registration_now_names_arm_bs_dataset`, because the old name is cited by `docs/reports/lora-c-run.md` and describes a state that no longer exists. Both changes are disclosed here rather than folded into a rebuild. |
| **Dv799** | `[cause: tooling]` [[a_frozen_record_is_an_input_to_shipped_code]] | **`train_qlora_v3.py --census` crashed on a relative `--data`.** `Path.relative_to(REPO_ROOT)` on `results/pass1_sft_v3_arm_b.jsonl` raises, and the command form in the file's own docstring is relative — so the shipped census command would have died on a pod, on the line after the tokenizer had loaded. Found by running it. `path.resolve()` first; the docstring now carries the arm-B command. |
| **Dv800** | `[cause: process]` | **The report's own commit lands after the closing reading, and that is licensed by a check, not by memory.** No test module passes a string containing `docs/reports` to a call; the eleven mentions in `tests/` are docstring prose. Two directories that ARE suite inputs were found by the same scan and both are committed BEFORE the verifier runs: `knowledge/templates/daily-log.md` (`test_templates.py`) and `knowledge/decisions/reader-sitting-16-08.md` (`test_reader_gold_r2.py`). |

**Tally:** contract-gap 2 · verify-gap 3 · tooling 2 · process 1 · spec-gap 0 · model 0 — **8 total**,
by the grep below.

The pattern carries the BRACKETS. Without them each command counts its own line in this block and
every tag reads one too high — the tally would have been 3 · 4 · 3 · 2 · 1 · 1 for eight deviations,
which does not even sum ([[a_count_in_prose_is_not_the_enumeration]]).

```
$ for t in contract-gap verify-gap tooling process spec-gap model; do
    printf "%-13s %s\n" "$t" "$(grep -c "\[cause: $t\]" docs/reports/lora-c-armb.md)"; done
contract-gap  2
verify-gap    3
tooling       2
process       1
spec-gap      0
model         0
$ grep -c "^| \*\*Dv" docs/reports/lora-c-armb.md
8
```

---

## What the operator is being asked

The cap word is due on **these** numbers, before any create, and the derivation is now for the real
scope.

1. **The cap.** At $0.74/h — what the last five pods billed — the $4.00 cap covers **73.43 s/step**
   over 144 steps, and both s/step readings this repo holds sit under it. At $0.80/h it covers
   **63.29** and only lora-b's registered 61.047 fits. Neither reading is this line's rate: both
   were taken at ≤1 222 tokens against 1 445–2 975, and no one has ever measured a step at 3 072.
   Leaving the cap at $4.00 is now a defensible bet rather than an arithmetic contradiction — and it
   is still a bet the smoke settles.
2. **The card.** `RTX A6000` reads `none` in the volume's own datacenter and `A40` is not catalogued
   there. The 4090 at $0.74 (Low) is what the last five pods used; `RTX PRO 4500` 32 GB at $0.72 is
   the only card at **High** stock and is 8 GB wider. Nothing here is chosen and no seconds have
   been measured on anything but a 4090.
3. **The header tell (Dv795).** Three readings are possible and only the team lead can take one:
   (a) accept it and read arm B's result with the confound named — the honest floor, since a RED
   arm B then means «no help OR a learned marker»; (b) rule a different header — any constant string
   is an equally perfect marker, so this only helps if the header VARIES across the 160 the way a
   real one does; (c) drop the topic line's falsehood by ruling a string for «this row has no post»,
   which fixes the untruth and not the tell.

---

## Open, and named rather than closed

1. **P-NULL from `lora-c-apply` is still open** — carried forward, untouched by this contract.
2. **`results/lora_c_encode_census*.json` are pinned by nothing.** Both are rebuilt on demand and
   both are asserted by tests, but no record hashes them; a substitution would be invisible to the
   registration. Named in `lora-c-run` and still true.
3. **`money.pre_pod_arithmetic` is a derivation, not a price.** It is superseded the moment the
   scope moves again — which is what just happened to `lora-c-run`'s version.
4. **The `reachability.the_pinned_trainer_refuses_a_v3_dataset` block still reads as open** in the
   registration. It is true about `scripts/train_qlora.py` and closed in practice by the sibling; the
   wording is `lora-c-prep`'s and this contract did not rewrite it.
5. **This report is long.** The tell measurement, the two-price table and the stock listing are each
   a table because each is a number the operator rules on; the prose around them could be shorter.

---

## Process signals

1. **The instrument that closes a repeated failure has to be run against the failure.** Three drives
   of `check_stamped.py` — including a GREEN suite over a moved tree — cost about a second, and
   without the middle one the target would have been a habit with a Makefile entry.
2. **A whitelist is a claim about a directory of tests that grows every week.** Writing «no test
   reads it» beside the exemption is worth nothing; parsing every test module for a call carrying
   the name is worth something, and naming what that scan cannot see is worth more than pretending
   it sees everything.
3. **The key-path diff caught what no guard did, twice in one session** — `review_gate_1`'s fifteen
   keys and the exact reach of the money edit. A rebuild is a rewrite, and «only X changed» is a
   belief until it is a list.
4. **A test that pins which way a measurement came out will be edited the day the measurement
   moves,** and the edit is indistinguishable from repairing a broken test. Two of them here. The
   fix is to publish the verdict as a field and let the test re-derive it.
5. **The finding that mattered most was not in the contract.** The four censuses it asked for all
   came back clean; the confound came from asking what the rendering choice PUTS IN THE PROMPT,
   which nothing in the brief required and which decides whether arm B's reading means anything.

---

**STOP.** Awaiting team-lead acceptance. No pod, no endpoint, $0.0000 spent, attempt unspent,
registration DRAFT.
