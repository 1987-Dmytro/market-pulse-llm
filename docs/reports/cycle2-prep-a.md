# cycle2-prep-a — the 3.19 skip in the queue, and the batch-parity projection

**Contract:** `docs/PROMPT-cycle2-prep-a.md` · **class:** zero-cost, code + paper · **spend: $0.00**
**Baseline:** `make check` 2 332 passed / 2 skipped @ `b2ff741` — reproduced here before the first
edit. **Now:** 2 347 passed / 2 skipped. Nothing was collected, no endpoint or pod exists, no
pre-registration was written, `docs/SPEC.md` was not touched and `data/loop_cursor.json` is
byte-identical (`9b59aa5fd042bbb42d389b73ac55168f8941a16a64c4d8262e557e8f8f2a8b1a`, hashed before
the first run of any loop script and again after the last; the earlier steps of the session were
`make check` and commits, which do not open it).

Commits: `2b74cdf` (step 0 — the standing tail), `8d47fb3` (deliverable 1), `574915b`
(deliverable 2), `59618b2` and `7cef9c4` (two self-review findings: a reading in the projection that
re-derived a number the table above it already carried and disagreed with it by a rounding, and the
census/seal divergence of §1.5), plus `5427481` (the team lead's Phase-6 plan, Dv334), this report
and the session's vault tail.

---

## 1. Deliverable 1 — the 3.19 skip rule in the inference queue

### 1.1 The one text predicate, and where it was found

The predicate the 5c2 pipeline used to establish **3 714 with text / 1 361 text-less** lived inline
at **`scripts/window_summary_5c2.py:198`** — `"empty_text": not text.strip()`, computed on the text
recovered from each evidence row's own `rendering` (the string the model was actually sent). That is
the measurement SPEC amendment 3.19 was ruled on, so it is the one the queue rule had to reuse.

It is now **`market_pulse.loop.has_text`** (`src/market_pulse/loop.py:100`), and
`window_summary_5c2.py` calls it. There is no second definition: the only other file with an
`empty_text` field, `scripts/build_validate_pack.py`, READS the flag out of the summary record and
computes nothing.

**`strip()` vs `== ""` was settled empirically, not in prose.** Both predicates were run over the
window on both sides — the 5 075 derived inference rows (sent text) and the same rows re-joined to
`data/raw/comments` on `(channel, msg_id)`:

```
derived inference rows: 5075        window rows missing from data/raw: 0
SENT   not text.strip(): 1361       SENT   text == "": 1361
SOURCE not text.strip(): 1361       SOURCE text == "": 1361
rows where SOURCE-empty != SENT-empty: 0
SOURCE whitespace-only (non-empty but blank): 0
duplicate msg_id per comment file: none
```

The two readings agree exactly, and the amendment's «every one of them empty at the SOURCE store —
zero lost in the pipeline» reproduces independently. `strip()` was kept as the stricter reading: it
costs nothing today and is right about the one-space comment nobody has collected yet.

### 1.2 The seam, and what it does not touch

Two places build a queue somebody pays for, and both now apply the same two filters:

| | before | after |
|---|---|---|
| `loop.plan_channel` → `rows_to_inference` | `queue_depth(comments.ids, wm)` | `text_split(above(store.rows(…), set(), wm))[0]`, plus `text_less_skipped` |
| `loop.queued` (the list `scripts/run_5c2.py` bills against) | `above(rows, answered, wm)` | the text-bearing half of the same |

`plan_channel` had to stop reading `StoreIndex.ids`: the index answers "which ids are here" and the
skip is a question about text, which only the record carries. It reads the store's ROWS through
`above` with an **empty answered set** — the plan deliberately does not subtract what has already
been answered (that is `queued`'s job), but the watermark test and the skip are then literally the
same two filters in both places rather than two spellings of them.

**`loop.queue_depth` is untouched, on purpose.** `scripts/census_5c2.py:152` counts the window with
it and the committed `results/census_5c2.json` says so in its own `definitions.comments_unanswered`.
A skip folded in there would silently restate a committed census. Collection, watermark semantics,
`data/loop_cursor.json` (schema and values) and every sealed artifact are unchanged.

### 1.3 Consumers — the enumeration re-run

The contract named **7** (six files plus `hot.md` prose). The re-run enumeration is **11 files plus
2 sealed records**; four files the contract did not name were touched and one more inherits the rule
without an edit.

| what | verdict |
|---|---|
| `src/market_pulse/loop.py` | **changed** — the seam, the predicate, the counter |
| `scripts/run_loop.py` | **changed** — the pass summary and the smoke record carry the split |
| `scripts/window_summary_5c2.py` | **changed**, *not named* — the predicate's old home, now a caller |
| `scripts/run_5c2.py` | *not named*, **unchanged** — the paid driver calls `loop.queued` (`:909`) and inherits the skip. It also inherits a hazard, §1.5 |
| `scripts/census_5c2.py` | unchanged by design — `queue_depth` did not move |
| `scripts/collect_5c1.py` | unaffected — it uses `loop.POSTS` / `advance` / `save_cursor` only, never the comment queue |
| `tests/test_loop.py` | **changed** — the fixture and three new tests |
| `tests/test_census_5c2.py` | unaffected, green |
| `tests/test_window_summary_5c2.py` | **changed**, *not named* — the sealed-sha guard (Dv330) |
| `tests/test_build_validate_pack.py` | **changed**, *not named* — the same guard (Dv330) |
| `knowledge/hot.md` | prose, updated |
| `results/window_summary_5c2.json`, `results/validate_5c2_pack.json` | **pins, NOT re-pinned** — see Dv330 |

`results/discovery_5a.json` and `results/poll_census_5a.json` also name `src/market_pulse/loop.py`,
but as a filename in a list — no sha, no guard.

The graph agrees and is current: the post-commit hook rebuilt it (24 268 nodes / 28 492 edges) and
`graphify query` resolves `has_text()` and `text_split()` at their new lines in community 170 with
`loop.py`'s other queue functions.

### 1.4 Tests

Three added, both directions plus the window regression:

- `test_a_comment_with_text_is_never_skipped` — a texted row is queued by both the plan and `queued`.
- `test_a_text_less_comment_never_enters_the_paid_queue_and_stays_collected` — the row is out of
  both queues and still in the store, still in `StoreIndex.ids`, still counted by `queue_depth`
  (the census's instrument), and the watermark still moves over it: a pass that answers 100 and 102
  leaves 101 behind for good, which is what «stays watermarked» means.
- `test_the_skip_is_the_predicate_the_5c2_window_was_measured_with` — the two committed artifacts
  agree on the population, the shared predicate reproduces the sealed `empty_text` flag per row on
  all five real texts in `results/validate_5c2_pack.json`, and a store of the artifact's shape plans
  to `rows − empty` / `empty`. **5 075, 1 361 and 3 714 are read out of the JSON, never typed.**

### 1.5 The seam this opens between the census and the seal — for the next contract

`queue_depth` (what the census counts) and `queued` (what a pass buys) now count **different
populations by design**, and the paid driver does not notice. `scripts/run_5c2.py:250`:

```python
def restrict(rows: list[dict], keep: set) -> list[dict]:
    """The queue, intersected with the registered selection. Order is the queue's — oldest first."""
    return [row for row in rows if row["msg_id"] in keep]
```

It is a filter. Nothing between it and the money compares the queue's length against the length of
what a registration sealed — the refusal at `:295` is `SliceTransport`'s and fires when a *pack* is
missing a row's answer, not when the queue is short. So a pre-registration built from a census that
registered 5 075 would be met by a queue of 3 714, buy 3 714, and only trip
`window_summary_5c2.assert_populations` afterwards — **after the money is gone.**

That is the correct behaviour of a queue rule (the rows stay collected and counted), so nothing was
patched here: the money path is not this contract's to change, and the fix belongs in the next
pre-registration's producer, which must register the **payable** population rather than the
collected one. What was added instead is a red line for whoever writes it —
`tests/test_run_5c2.py::test_a_registered_selection_is_met_by_a_smaller_queue_and_nothing_raises`
pins the divergence with the number visible, so the next contract meets the fact as a test rather
than as a paragraph in a report.

---

## 2. Deliverable 2 — the batch-parity projection

**`results/batch_cycle2_projection.json`**, produced by `scripts/projection_batch_cycle2.py`
(the `scripts/projection_*.py` glob, so `.claude/rules/registrations-and-draws.md` binds).
Every figure is resolved through `projection_5c2.cite` by the dotted path printed beside it, and
`tests/test_projection_batch_cycle2.py` re-resolves all of them with a **second** resolver.

**What «batch» even means here:** `results/parity_srv2.json :: config.serving.job_shape` records
`rows_per_job: "one input slice"` with `forward_batch_size: 1`. Rows already travel many per JOB —
the 5c2-run comment leg was 55 calls for 5 078 rows. The candidate is the worker's forward batch,
so neither the loop nor the driver would change.

### (a) Candidate batch sizes on serverless RTX 4090 24 GB — an inequality, not a size

The four figures are regexed out of the verdict's own sentence (`batch_5b2_verdict.json :: blocker`),
so a reworded sentence stops the producer instead of leaving a stale bound behind:

> torch.OutOfMemoryError on the worker at the second sarcasm_holdout batch of 16: **1.85 GiB
> requested, 432 MiB free, 42.14 GiB allocated** by PyTorch against a **~20 GiB model at rest**

| | |
|---|---|
| demand at the failing step | 42.14 + 1.85 = **43.99 GiB** |
| above the weights | **23.99 GiB** (A6000 48 GB, 4-bit NF4) |
| headroom on a 4090 24 GB above the same weights | **3.99 GiB** (`24 564 MiB`, `parity_srv2 :: config.runtime`) |
| shortfall | **6.02×** |
| largest N the inequality admits | **2** — ruled out: 3, 4, 8, 16 |

Both cards ran the identical `load_in_4bit` / `nf4` / double-quant / bf16-compute block, so the
~20 GiB at rest transfers and the working set is the only variable. Batch 1 is not projected at all:
it is **demonstrated** — the 5c2-run comment leg served the whole window on this class.

**Whether batch 2 actually fits is NOT MEASURABLE** from the records: the per-row figure is the
failing step's peak divided by 16 and GPU memory scales with *tokens*, not rows (the ladder chose 16
on a 24-row carve whose longest T1 batch fitted and the test set's did not); no record in the
repository carries a memory reading from the *serverless* worker; and the KV cache of
`max_new_tokens: 256` is inside the same working set with nothing separating it.

### (b) What a new pre-registration would measure, and against which anchors

Gate evals stay batch 1 forever (SPEC 3.11 (2), as `batch_5b2_verdict :: rule_could_not_run` states
it), so the only candidate is the **production loop's comment row price** and nothing that feeds a
bar. Three measurements, two of which have anchors already:

1. **Row IDENTITY against batch 1, on the production population.** This is the finding the failed
   attempt left behind and it is easy to miss: of the 666 rows it scored before dying, **6 disagreed
   with batch 1** (`salvage.row_agreement_vs_batch_1.rate` = 0.990991) — while every batch size on
   the 24-row carve was byte-identical (`batch_ladder_5b2 :: control.identical` = true). Batching
   this stack is **not answer-neutral**, and the carve is exactly where that fact hides.
2. **Seconds per row at the candidate N**, against `run_5c2_comments :: timing.seconds_per_row`
   (4.247 s, n = 5 078) — a population price that does not have to be re-bought.
3. **Peak GPU memory per step at the candidate N.** No anchor exists; this is the new measurement,
   and it is the thing (a) cannot derive. The 5b.2 attempt learned its memory bound by dying at row
   666 of 758 with no record and no prediction dump written.

The abort rule to inherit is the 5b.2 registration's own: one attempt, no retry, and a failed
measurement closes the question in favour of batch 1.

### (c) The measurement session's own cost per candidate

| | seconds | USD |
|---|---|---|
| fixed — boot + staging + the two 3.17 (9) warm-up calls + the idle tail | 495.533 | **$0.1520** |
| per row at the **batch-1 ceiling** | 4.247 | **$0.0013025** |

The fixed cost is billed whether the session buys a gold row or refuses at its own gate. Arms are
priced at the batch-1 seconds-per-row deliberately: the candidate's own rate is what the session
exists to measure, so this is a **ceiling** and never a prediction.

| rows per arm | one arm | candidate only | with a batch-1 control | blind to the identity defect |
|---:|---:|---:|---:|---:|
| 24 (the 5b.2 carve) | $0.0313 | $0.1833 | **$0.2145** | **0.8048** |
| 400 (`comments_test`) | $0.5210 | $0.6730 | **$1.1940** | 0.0268 |
| 758 (the srv-2d parity population) | $0.9873 | $1.1393 | **$2.1266** | 0.0010 |

The last column is `(1 − 0.009009)^rows` at the one recorded batch-vs-1 disagreement rate: **a
24-row arm would have seen nothing four times out of five**, which is precisely how batch 16 came to
be certified by a ladder.

### (d) Break-even at −30% and −50%

Priced on the **marginal** row price ($0.0013025): a batch changes worker seconds and nothing else,
so crediting it with the boot it does not touch would inflate every saving. (The all-in figure is
carried in the record for the operator's arithmetic: $0.0013218/row, the comment leg's $6.7079 over
its 5 075 gold rows.)

| volume | rows | saving at −30% | saving at −50% |
|---|---:|---:|---:|
| history backlog | 11 143 | **$4.3536** | **$7.2574** |
| one cycle window, as bought | 5 075 | $1.9828 | $3.3053 |
| one cycle window, payable after 3.19 | 3 714 | **$1.4511** | **$2.4189** |

Break-even, against the 758-row two-arm probe ($2.1266): **5 444 rows at −30%**, **3 266 at −50%**.
Against the 24-row probe ($0.2145): 550 and 330 — but that arm cannot see the identity defect.

**Three readings.**

- **The free rule already beat the paid one.** The 3.19 skip banks **$1.7727 per window at $0** —
  1 361 rows that never reach the queue — which is more than a −30% batch would save on the rows
  that remain ($1.4511), and it needed no probe, no cap and no session.
- **A probe repays on the backlog, not on a single window.** At −30% a $2.13 two-arm probe is under
  water against one post-3.19 window ($1.4511) and clears against the 11 143-row history ($4.3536).
- **The window's 26.8% text-less share is NOT applied to the history.** It is a rate measured on one
  four-week window and the backlog is a different sample. How many of the 11 143 carry no text is
  derivable at $0, no anchor states it, and this record does not guess it.

The pod ladder (4.18 → 1.87 → 1.52 → 1.50 s/row wall at N = 1/4/8/16) is carried in the record as
`ladder_for_reference` and enters **no dollar figure**: different card, different runtime, a 24-row
training carve, and a floor-direction bound at best.

**HARD STOP honoured:** no pre-registration written, no SPEC edit, no GPU/pod/endpoint, no spend.
The money line is an open operator decision and this record does not take it.

---

## 3. Verify — evidence

**`make check`** (tail, measured **after** the self-review pass that produced §1.5, at `7cef9c4`):

```
........................................................................ [ 98%]
.............................................                            [100%]
2347 passed, 2 skipped in 65.13s (0:01:05)
```

`ruff format --check .` → `274 files already formatted` (the formatter is not in `make check`).

**The per-pass summary line, from the existing stub-served smoke path.** On the production store it
renders zeros, because the inference watermark covers the whole corpus (the standing blocker — the
comment queue reads 0, not 11 143). Both runs are printed, per Dv332:

```
# PYTHONPATH=src python3 scripts/run_loop.py --once --dry-run   (the real store, 66 channels)
TOTAL 0 comment threads would be fetched, 0 rows would go to inference, 0 text-less skipped (SPEC 3.19 (1))

# the same run_loop.main over a throwaway store: 6 comments under one post, 3 of them text-less
channel                    posts  comments     since  threads  to infer  comments
---------------------------------------------------------------------------------
@VARUS_channel                 1         6         1        0         3  yes

TOTAL 0 comment threads would be fetched, 3 rows would go to inference, 3 text-less skipped (SPEC 3.19 (1))

inference: 3 rows are queued and no serving endpoint is registered. SPEC 3.11 (2) pre-registers a
serving-parity measurement before any serving number reaches an aggregate, so 5a queues rows and sends none.
  stub-served @VARUS_channel              3 rows written, watermark now 105

record totals: {"threads_to_fetch": 0, "rows_to_inference": 3, "text_less_skipped": 3}
record plan[0]: {"channel": "@VARUS_channel", "comments_stored": 6, "rows_to_inference": 3, "text_less_skipped": 3}
```

The watermark lands at **105** — past the two text-less rows above the last answered one — which is
the amendment's «rows stay watermarked», demonstrated rather than asserted.

**The projection.** `results/batch_cycle2_projection.json`, `provenance` block:

```json
{
  "anchors": [
    {"path": "results/spend_5c2run.json",        "sha256": "c0ceb9ea…", "named_by_the_contract": true,  "why": "the only population-priced serverless anchor — 5 278 rows bought"},
    {"path": "results/parity_srv2.json",         "sha256": "d4d38959…", "named_by_the_contract": true,  "why": "srv-2d parity, batch 1, 758 rows; and the serving card's identity"},
    {"path": "results/serving_5b.json",          "sha256": "0f05aefa…", "named_by_the_contract": true,  "why": "the pod cost anchor — carried as a ratio, never as a price"},
    {"path": "results/batch_ladder_5b2.json",    "sha256": "02e39cfa…", "named_by_the_contract": true,  "why": "the 5b.2 ladder: the arms, the control, and the A6000 it ran on"},
    {"path": "results/batch_5b2_projection.json","sha256": "1a5efc51…", "named_by_the_contract": true,  "why": "the failed attempt's registration and its abort rule"},
    {"path": "results/batch_5b2_verdict.json",   "sha256": "228a0100…", "named_by_the_contract": true,  "why": "the OOM, the salvaged row agreement, and the batch-1 ruling"},
    {"path": "results/run_5c2_comments.json",    "sha256": "1bd8c197…", "named_by_the_contract": false, "why": "the serverless $/s, the population seconds-per-row and the boot. A balance anchor prices an account, not a step, so (c) cannot be answered without this file"},
    {"path": "results/window_summary_5c2.json",  "sha256": "7760d32d…", "named_by_the_contract": false, "why": "the reference cycle volume the contract names, and the 3.19 class beside it"}
  ],
  "producer": {"script": "scripts/projection_batch_cycle2.py", "sha256": "b47e237d…",
               "why": "no git block: `git status --porcelain` is a fact about the tree and would move this record on somebody else's commit"},
  "not_typed": "every figure above is resolved through `projection_5c2.cite` / `dig` by the dotted path printed beside it, except HISTORY_ROWS, which is the contract's own reference volume and is grepped back out of it by the test"
}
```

The `window_summary_5c2.json` sha in that block — `7760d32d0ffec80c…` — is byte-for-byte the one
`results/validate_5c2_pack.json` pinned on 2026-08-14: **the sealed record was read and not moved.**

---

## 4. Deviations

Full text in `implementation-notes.md § cycle2-prep-a`; numbering continues after Dv329.

- **Dv330** `[contract-gap]` — the named seam is pinned by two sealed records; editing `loop.py` at
  all (and `window_summary_5c2.py`, which the one-predicate clause forces) reddened three tests on
  bytes. Neither record re-pinned; both guards re-anchored to `git show d69c812…:` and asserted both
  ways. Two test files outside the contract's autonomy scope had to be edited.
- **Dv331** `[contract-gap]` — the six named anchors cannot answer (c); a balance anchor prices an
  account, not a step. Two extra records read and declared `named_by_the_contract: false`.
- **Dv332** `[env]` — the real store's smoke renders a zero split because the watermark covers the
  corpus; the non-zero line was produced by driving the same entry point over a throwaway store.
- **Dv333** `[process]` — `store_with`'s comments were text-less, so under the new rule three
  watermark tests would have stayed green while measuring nothing.
- **Dv334** `[process]` — `docs/PLAN-phase6-command-center.md` arrived untracked mid-session after
  Step 0's list closed; committed by path per its own header, unedited.

---

## 5. Process signals

1. A "consumer table" built by grep cannot see the consumer that IS a sha256 of the file the table
   tells you to edit — second sighting in two contracts, and it cost three red tests both times.
2. When a contract names a seam, the sha pins ON that seam are part of the seam's price; grepping
   the pins before the first edit turned a blocker into a fifteen-minute fix.
3. The batch question's real risk is not memory, it is answers: 6 of 666 rows moved at batch 16
   while a 24-row carve was byte-identical, and no ladder over a carve can see that.
4. A rate measured on one window is not a rate for the backlog — the projection says so out loud
   rather than multiplying 26.8% by 11 143, which was the tempting line.
5. A queue rule splits one population into two, and the guard that would notice sits downstream of
   the money: `restrict` filters, `assert_populations` refuses, and only one of them runs before the
   bill. Found by re-reading the paid driver after the deliverable was committed (§1.5).
