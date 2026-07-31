# Implementation notes — Phase 3b

Working notes for the step specified in `docs/PROMPT-3b.md` rev. 2 (operator, 2026-07-31):
zero-shot LLM baselines via OpenRouter, an XLM-R supervised baseline, and the Claude Haiku
reference row. Decisions with a lifetime beyond this step live in
`knowledge/decisions/3b-infra-and-precision.md`; this file is the build log.

## Assumptions stated before the code was written

1. **One request per frozen row**, not many rows per request. Batching rows into one prompt would
   let one malformed answer poison several rows and make the parse-failure counter meaningless.
   "Batched with bounded concurrency" is read as concurrency, not prompt-packing.
2. **The prompt is the guideline, compressed.** `docs/annotation/comments.md` and
   `docs/annotation/posts.md` are the definition of the labels, so the zero-shot prompt states
   those rules — including the ones a model cannot guess: a promo-mechanic complaint is not
   `price`, a service-only complaint carries no product intent, dairy as an ingredient is not
   relevant, and `launch` beats `promo` when both apply. Giving a zero-shot model *less* than the
   annotator had would measure prompt starvation, not the model. The guideline's `unclear` rules
   are the exception and are deliberately absent — see 3.
3. **`unclear` is not offered to the model.** The frozen test sets contain zero `unclear` rows
   (400/400, 250/250, 108/108 scoreable), so an `unclear` option could only ever cost a model a
   row. Gold `unclear` handling stays where it belongs — inside the scorer.
4. **No `response_format` / structured-outputs parameter.** One fp8 endpoint in the pinned set
   (`chutes/fp8`) does not advertise `response_format`, and sending a parameter to some rows and
   not others would make the four rows non-comparable. Strict JSON is asked for in the prompt and
   enforced by the parser; formatting wrappers (```json fences, prose around the object) are
   unwrapped before validation and are not counted as failures — a code fence is not a different
   answer.
5. **Reasoning is disabled on every request** (`reasoning: {"enabled": false}`), uniformly. Qwen3.5
   and Qwen3.6 are hybrid-reasoning models; left on, they spend the fixed `max_tokens` thinking and
   return empty content, which would read as a 100% parse-failure rate bought with real money.
6. **Temperature 0, `max_tokens` 256, `seed` 42 where the endpoint accepts it.** 256 is far above
   the ~60 tokens the longest legal answer needs, so truncation is a model behaviour, not a budget
   artefact.
7. **XLM-R is `xlm-roberta-base`, one independent fine-tune per head**, mirroring how the
   TF-IDF+logreg baseline fits one classifier per head. A shared-encoder multi-head model would
   score differently and is not what "the XLM-R baseline" in SPEC §7 names.

## Deviations from `docs/PROMPT-3b.md`

Every departure is logged here. Silence is not compliance.

| # | Contract text | What was done | Why |
|---|---|---|---|
| D1 | "track actual spend during it (X-Generation-Id header -> GET /api/v1/generation?id=)" | Per-row cost is read from `usage.cost` in the response body (`"usage": {"include": true}`); the run is reconciled against `GET /api/v1/credits`. The generation endpoint **was implemented and probed, and it does not work for our generations**: `GET /api/v1/generation?id=gen-…` returns `404 not found` for a valid `X-Generation-Id`, at 2 s, 4 s, 8 s, 16 s and 60 s after the completion, and `/generations/<id>` 404s too. | Not a preference — the named mechanism returns no data. `usage.cost` carries the same number in the response that produced it, and the credits delta counts rows whose record was never written, which neither of the others does. |
| D2 | "report 'base model errs on N of 108' per candidate" | Three numbers are reported per candidate, not one: sentiment errors, sarcasm errors, and their union, each with its own `n`. | Amendment 3.2 says "misclassifies" and the holdout carries two labels. Picking one reading would be the executor deciding a gate definition. Flagged for the operator at the Phase 4 gate; ADR §(e). |
| D3 | Candidate list annotated "`google/gemma-4-31b-it` (~31B dense, **Gemma Terms of Use**)" | Recorded as **Apache-2.0**. | "record the licence you actually find". The HF card says `license: apache-2.0` and Google's own `gemma_4_license` page is titled "Apache License 2.0". The candidate was not substituted; only the licence annotation differs. |
| D4 | — (addition, not a departure) | `gate_anchor_valid: false` is written into any record where unusable rows exceed 2% of an input. | G1d and G1e are defined *relative to this number*, so a run with holes must not become an anchor by default. Pre-registered before the first request; ADR §(e). |
| D5 | the frontier row's slug given as `anthropic/claude-haiku-4.5:batch` | The reference row runs on **`anthropic/claude-haiku-4.5`** — the synchronous slug for the same model. See "Batch variant" below. | `:batch` 404s on `/chat/completions`. Costs ~$0.24 more on a row that anchors no gate; the alternative was an asynchronous second code path with a 24 h worst case. |
| D6 | "Atomic commits … (a) … (b) … (c) … (d)" | **Seven** commits, not four. The four named ones plus: `fix: patience over parallelism` (the 429 fix, after the first run), `feat: precision probe as a runner mode` (making task 2 reproducible as a command), and `chore: 3b zero-shot results and the phase spend ledger`. | The first two are real work that arrived after (b) was already committed and squashing them would have orphaned the commit hash a results record already names. The third is SPEC §8, which gates Phase 3 on "results file committed". |
| D7 | "XLM-R supervised baseline — LOCAL, on this Mac (**Apple MPS**)" | The script's device default is **`cpu`**; `--device mps` still exists. | Measured, not assumed: 3.503 s/step on the CPU against 48.117 s/step on MPS, and MPS OOMs at its 9.07 GiB allocator ceiling. Committing an MPS default would hand the next operator a 29-hour run. |
| D8 | — (config decision forced by hardware) | XLM-R's **word-embedding matrix is frozen** (192M of 278M parameters). | AdamW's two fp32 moments for a 250k × 768 matrix are exactly what the MPS allocator refuses, and 1,446 training rows cannot move a 250k-row vocabulary anyway. Chosen before any number existed and recorded in `config.frozen_parameters`, not left silent. |
| D9 | "train on REAL sources only (comments_train.jsonl + sarcasm_candidates.jsonl…)" | The two T2 heads also train on **`data/frozen/posts_train.jsonl`** (749 scoreable rows). | The named pair is the T1 pool, and the sentence's subject is excluding `synthetic_sarcasm.jsonl` — which was not opened. G1d is a T2 gate and cannot be covered without T2 training data; `scripts/run_baseline.py` uses the same three sources. `synthetic_sarcasm.jsonl` and `sarcasm_holdout_pool.jsonl` were not read by either script. |

**One imprecision inside a written record, noted rather than edited.** The `gate_anchor_valid`
note says "this run must not anchor G1d/G1e" whichever input lost the rows. For
`qwen/qwen3.6-27b` the input over 2% is `sarcasm_holdout` (5 of 108, 4.6%), which bears on the
**G1b slice**, not on G1d/G1e — `posts_test` lost 0.4% there. The per-input shares in
`diagnostics.failures` are the authority; the note is coarse. The record is append-only and is not
being hand-corrected.

## The three candidate rows are not paired on identical instances

`gate_anchor_valid` answers "may this run anchor a gate". It does not answer the question the
operator asks next, which is comparing the three rows to pick a base model — and those rows were
not scored on the same instances:

| row | comments_test | posts_test | sarcasm_holdout |
|---|---|---|---|
| `google/gemma-4-31b-it` | 400 | 250 | 108 |
| `qwen/qwen3.5-9b` (2nd run) | 400 | 250 | 108 |
| `qwen/qwen3.6-27b` | **396** | **249** | **103** |
| `anthropic/claude-haiku-4.5` (ref) | 400 | 250 | 108 |

So qwen3.6-27b's G1a 0.8522 and gemma's 0.8944 have different denominators, and SPEC §5 requires
"comparisons paired on identical instances" — the same rule `scorer.py`'s module docstring spells
out for macro averaging. **Nothing here is unrecoverable and nothing needs re-spending:** every
record carries `config.scored_ids_sha256` per input, so a paired re-score on the intersection of
the four rows is reproducible from the file.

What it would take to close it properly is the operator's call, because the missing rows are
`missing field: sentiment` from the model itself, not 429s from an endpoint — at temperature 0 a
re-run is not obviously a fix, and a model that cannot answer 9 rows is telling you something. A
re-run of qwen3.6-27b costs $0.13 and 20 minutes.

## Batch variant — resolved 2026-07-31

`anthropic/claude-haiku-4.5:batch` exists on OpenRouter at half price ($0.50/$2.50 per Mtok against
$1.00/$5.00), and one live probe row settled whether it can be used here. It cannot:

```
POST /api/v1/chat/completions  {"model": "anthropic/claude-haiku-4.5:batch", …}
HTTP 404 {"error":{"message":"This model is only available through the Batch API.
                              Use the /api/beta/batches endpoint instead.","code":404}}
```

The Batch API is asynchronous — a submitted job is polled, and OpenRouter allows it hours. Building
that path would mean a second request/poll/collect flow inside the runner, with its own failure
modes, for the one row in the table that anchors no gate. The reference row therefore runs on
`anthropic/claude-haiku-4.5`: the same model, the same prompt, the same `--reference-only` marking,
synchronous, ~$0.48 instead of ~$0.24. The runner refuses the `:batch` slug with this explanation
rather than letting 758 rows 404 one at a time.

## XLM-R: why the full run did not start

The contract's own stop condition, not a departure from it: *"If the estimate exceeds 60 minutes,
STOP and report the estimate instead of starting the full run."*

The plan is 9 heads, **2,193 training steps** and **3,516 eval rows** (sentiment and sarcasm each
predict `comments_test` + the holdout; five intent heads predict `comments_test`; relevance and
post_type predict `posts_test`). The timed smoke trains 12 real steps on the sentiment head, drops
the first (lazy kernel compilation) and measures the rest:

| device | s/step | ms/eval row | projected full run |
|---|---|---|---|
| `cpu` | 3.503 | 47.3 | **130.8 min** |
| `mps` | 48.117 | 90.8 | **1764.0 min** (29.4 h) |

Both are over the ceiling, so nothing was trained and no `xlm-roberta-base` record exists in
`results/baselines.json`. Treat 130.8 min as a **floor**: the rate was measured on the sentiment
head over comments (mean 87 chars), and the two T2 heads train on posts (mean 278 chars) with
dynamic padding, so their 282 steps will run slower than the extrapolation assumes.

Three things were *not* done to make it fit, because each would be tuning a pre-registered
baseline to a wall clock: fewer epochs, a shared-encoder multi-head model in place of nine
independent fine-tunes, and a shorter `MAX_LENGTH`. That call is the operator's.

**Gate coverage of this baseline, stated here because the record that would state it was never
written:**

| gate | status |
|---|---|
| G1a sentiment | covered |
| G1b sarcasm slice | `null` — amendment 3.2 defines the slice by the *zero-shot* base LLM's errors, and a fix-rate needs a fine-tune. Same reason TF-IDF's is `null` |
| G1c intents | covered |
| G1d post type | covered (relevance reported beside it, not gated — amendment 3.3) |
| G1e brand extraction | **NOT COVERED — not attempted.** Brand extraction is span extraction; this baseline is a sequence classifier and no token-classification head was trained for it. Not a zero, not a blank |

## Build log

- 2026-07-31 — precision probe run, `fp8` branch fired (ADR §(b)); ADR + INDEX written.
- 2026-07-31 — prompts, harness and offline tests; live sizing probes on all four models
  (`reasoning: {"enabled": false}` confirmed honoured, `reasoning_tokens: 0` everywhere).
- 2026-07-31 — first `qwen/qwen3.5-9b` run at 8 workers lost 11 rows to HTTP 429; the 2% guard
  marked it `gate_anchor_valid: false`. Concurrency dropped to 4, retries raised to 6.
- 2026-07-31 — four scoring runs: qwen3.5-9b, gemma-4-31b-it, qwen3.6-27b, and the Haiku
  reference row. **Phase spend $0.7795 of the $8 cap** once OpenRouter's usage settled — the
  last run printed $0.7569, and `/credits` lags by a few cents for minutes afterwards, which is
  exactly why `Budget.reconcile` takes the larger of the local sum and the provider's figure.
  $0.7490 of it is the five recorded runs; the remainder is the live sizing probes. Five records
  in the results file.
- 2026-07-31 — XLM-R smoke on both devices; both over the 60-minute ceiling, full run not started.
