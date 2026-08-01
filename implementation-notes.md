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

### Deviations from `docs/PROMPT-3c.md` (rev. 1) and its team-lead addendum

| # | Contract text | What was done | Why |
|---|---|---|---|
| E1 | "use the full-run command from `scripts/runbook_3b.md` wrapped for an unattended night" | The launched command adds **`--time-budget-min 600`**. | G4 lifted the *operator's* ceiling; the 60-minute ceiling is also **code** — `train_xlmr_baseline.py:307` prints the projection and refuses to train above it, exiting **3**. The runbook command as written would have produced a log, no process and no run. Nothing else about the command changed: same script, `--device cpu`, no epoch / `MAX_LENGTH` / architecture change. |
| E2 | "Append a dated subsection … the original sentence stays as written" | The original sentence was **restored verbatim** first — a `/save` edit earlier the same day had rewritten it away, together with its stale `0.8522` — and the correction subsection sits at the **end** of that section rather than immediately under the sentence. | The claim has to be readable next to its correction, so the rewrite had to be undone. The subsection is a heading: placing it mid-section would have swallowed the two paragraphs that follow the sentence into "Correction". |
| E3 | "Commit the modified stragglers (`knowledge/daily_logs/2026-07-31.md`, `knowledge/index.md`)" plus VERIFY's "only the running log untracked" | `docs/STATUS.md` and `docs/PROMPT-3c.md` were also committed — **byte-for-byte as the team lead left them**, zero lines authored here. | The addendum forbids *editing* those files, and task 5 requires a clean tree before the launch. Leaving them modified/untracked would fail that precondition; editing them is what is forbidden, and none was done (`git show --stat` and `git diff` on the commit both show it). |
| E4 | "the record and your report must state per-gate coverage explicitly" | Stated in the report and in the run's own record, but **the record does not exist yet tonight** — it is written when the run finishes. | The run is launched last and finishes unattended. Coverage is pre-registered in `train_xlmr_baseline.py` (G1b `null`, G1e the explicit "NOT COVERED" string) so the finished record cannot come out silent on it. |

**One imprecision inside a written record, noted rather than edited.** The `gate_anchor_valid`
note says "this run must not anchor G1d/G1e" whichever input lost the rows. For
`qwen/qwen3.6-27b` the input over 2% is `sarcasm_holdout` (5 of 108, 4.6%), which bears on the
**G1b slice**, not on G1d/G1e — `posts_test` lost 0.4% there. The per-input shares in
`diagnostics.failures` are the authority; the note is coarse. The record is append-only and is not
being hand-corrected.

### Deviations from the file-ownership task (2026-07-31 evening)

| # | Contract text | What was done | Why |
|---|---|---|---|
| F1 | "forbidding Edit and Write on `docs/STATUS.md`, `docs/SPEC.md`, `docs/PROMPT-*.md` (rule syntax of the installed Claude Code version, e.g. `"Edit(docs/STATUS.md)"`, `"Write(docs/PROMPT-*.md)"`)" | Three `Edit(...)` rules only, anchored at the settings source: `Edit(/docs/STATUS.md)`, `Edit(/docs/SPEC.md)`, `Edit(/docs/PROMPT-*.md)`. No `Write(...)` rule. | This *is* the installed version's syntax. On Claude Code 2.1.220 a `Write(path)` rule is accepted but never consulted and prints a startup warning; an `Edit(path)` rule covers every file-editing tool, Write included. A bare tool-level `Write` deny would have blocked Write everywhere, executor files too. The `/docs/…` anchor is the project root rather than the cwd, so the rule holds in a session started from a subdirectory. |
| F2 | Task 1: "commit the checkpoint state as-is … ANY other unexpected diff in these files → stop and report before committing" | Committed. `knowledge/daily_logs/2026-07-31.md` also carried two lines the Stop hook appended after the checkpoint (`- 19:51: session ended (auto)`, `- 19:55: session ended (auto)`). | Hook output inside a generated region that `CLAUDE.md` assigns to the hook — the same class as the `knowledge/index.md` timestamp refresh already approved in the task. Zero authored lines beyond the verified checkpoint. Flagged in the report rather than silently swallowed. |
| F3 | "ownership layer (single separate commit)" naming three items (settings, command write-lists, the matrix) | The commit also carries this Deviations entry in `implementation-notes.md`. | The report requires the entry and the verify-gate requires a clean tree; a third commit would contradict "single separate commit". A commit message summarises, it is not a file manifest. |

**The deny rules are live without a restart**, and they are file-scoped despite the wording of the
refusal. Self-test: an `Edit` appending `OWNERSHIP-DENY-TEST` to `docs/STATUS.md` was refused with
"File is in a directory that is denied by your permission settings"; the same refusal came for
`docs/SPEC.md` and `docs/PROMPT-3c.md` (the glob matches). Negative control: the identical attempt
on `docs/WATCHLIST.md` reached the tool and failed on content ("String to replace not found"), so
`docs/` as a whole is still writable. `git status` shows no modification under `docs/`.

## The three candidate rows are not paired on identical instances

`gate_anchor_valid` answers "may this run anchor a gate". It does not answer the question the
operator asks next, which is comparing the three rows to pick a base model — and those rows were
not scored on the same instances:

| row | comments_test | posts_test | sarcasm_holdout |
|---|---|---|---|
| `google/gemma-4-31b-it` | 400 | 250 | 108 |
| `qwen/qwen3.5-9b` (2nd run) | 400 | 250 | 108 |
| `qwen/qwen3.6-27b` (2nd run) | **397** | **249** | **104** |
| `anthropic/claude-haiku-4.5` (ref) | 400 | 250 | 108 |

So qwen3.6-27b's G1a 0.8522 and gemma's 0.8944 have different denominators, and SPEC §5 requires
"comparisons paired on identical instances" — the same rule `scorer.py`'s module docstring spells
out for macro averaging. **Nothing here is unrecoverable and nothing needs re-spending:** every
record carries `config.scored_ids_sha256` per input, so a paired re-score on the intersection of
the four rows is reproducible from the file.

What it would take to close it properly is the operator's call. **The re-run happened**
(2026-07-31, $0.1328, operator request) and did not close it: 8 unusable rows instead of 10, the
holdout still at 3.7% and the record still `gate_anchor_valid: false`. The failures repeat on
largely the same rows — 3 of 4 comment ids and 3 of 5 holdout ids are shared between the two runs
— so they are a property of those texts, not network noise, and a third run is not the fix.

The re-run also produced the sharpest evidence for the determinism caveat in ADR §(d): with
everything held identical — same commit, same prompt hash, same pin, temperature 0, seed 42 —
qwen3.6-27b's **G1d moved 0.7308 → 0.7605**, nearly 3 pp, from nothing but a different scored
subset. Both runs are in the file; neither is the "right" one.

### Correction (2026-07-31, team-lead review)

**The sentence above — "a paired re-score on the intersection of the four rows is reproducible
from the file" — is false, and it stays above unedited so the claim and its correction can be read
together.**

Per-row predictions and holdout error ids were **never persisted**. `results/baselines.json`
carries `config.scored_ids_sha256` — a SHA256 *of the id list* — plus per-input error **counts**
and `diagnostics.failures[].failed_ids`. That recovers which rows a run scored. It does not
recover **what the model answered on them**, and without the answers no metric can be recomputed
on any subset, intersection or otherwise. So the "$0, from the file" paired option that this
section offered the operator, and that the executor's 3b report repeated, does not exist. Closing
the pairing by re-scoring costs a fresh paired run (~$0.90).

The claim was made by reading the field list and finding it sufficient-looking; it was disproved
by trying the reconstruction. The gate closed the unpairedness a different way — a worst-case
bound analysis over the dropped instances, [[phase4-base-model-gate]] §(b), $0 — and every real
run from step 3c persists a per-row prediction dump so that next time the sentence is true. The
six existing 3b runs get no dumps: they cannot be reconstructed and must not be faked.

(One number in the original sentence is also stale: `0.8522` is the 27B's **run-1** G1a overall on
396 rows; run 2 reads 0.8541 on 397. Left as written — it is what the claim said.)

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
- 2026-07-31 — `qwen/qwen3.6-27b` re-run at operator request: same failure mode, mostly the same
  rows, still `gate_anchor_valid: false`. Phase spend **$0.9124 of $8.00** across six runs.

---

# Implementation notes — Phase 4a

Working notes for the step specified in `docs/PROMPT-4a.md` rev. 1 (operator, 2026-08-01): pod
bootstrap, the local inference path, and the own-pod zero-shot re-run that anchors G1d/G1e and
defines the G1b slice. No training. Decisions with a lifetime beyond this step live in
`knowledge/decisions/phase4-own-pod-anchor.md`; this file is the build log.

## Read-back, before any file changed

- **Ablation selection rule** — two arms, with and without `data/annotation/synthetic_sarcasm.jsonl`,
  identical config and seed, exactly one data path differing; the synthetic source stays **iff** its
  arm's G1b fix-rate is strictly higher **and** no other gated head is lower by more than 0.5 pp.
  The Tier-1 verdict is the selected arm's, both columns are published, there is no third run.
- **Cap and per-arm ceiling** — hard **$25** GPU spend across all of Phase 4, checked against RunPod
  billing before every start; a projection over **4 h per arm** stops the line for an operator
  decision.
- **The G1b slice** — the union of the base model's sentiment and sarcasm errors on the 108-row
  frozen sarcasm holdout, measured by *its own zero-shot re-run on our pod*. OpenRouter's 40/108 is
  a preview, not the slice.
- **G1d/G1e anchor** — the own-pod `google/gemma-4-31b-it` row, and it anchors regardless of whether
  it agrees with the OpenRouter fp8 row (amendment 3.4 (2), ADR 3b-infra-and-precision §(d)/(f)).

## Assumptions stated before the code was written

1. **The cross-check must not move the measurement.** The local path reuses 3b's prompt builder,
   parser, failure taxonomy, record builder, dump writer and scorer unchanged; only the runtime
   differs. Anything else and the two rows would differ for reasons that are not the serving stack.
2. **The prompt-SHA equality is checked against the stored record, not recomputed on both sides.**
   `prompts.prompt_sha256(task) == prompts.prompt_sha256(task)` passes forever. The guard reads
   `config.prompt_sha256` out of the recorded OpenRouter run of the same model and refuses on any
   difference, before the weights load and before a dollar is spent.
3. **The own-pod row keys under the same model name.** `results/baselines.json` already
   accumulates several runs per model (the two qwen3.6-27b runs), and the runtime distinction
   belongs in `config.backend` / `config.runtime`, not in an invented pseudo-model name.
4. **A generation failure gets its own bucket.** `api_failures` keeps its meaning — no usable
   response from a third-party endpoint — and `generation_failures` is the local equivalent. Both
   keys are present in every record whichever backend ran, so the two rows stay diffable.
5. **The pod's `results/baselines.json` never travels home.** It belongs to a throwaway checkout;
   `--record-out` writes the record the scorer built, `--append-record` appends it here. Copying an
   append-only anchor wholesale is the mistake `results/spend_3b.json` carries a footgun note about.
6. **The batch-invariance claim is measured, not assumed.** Greedy decoding makes batch size a
   throughput choice in principle; left padding and kernel selection can still move a logit, so the
   runbook compares the same rows at batch 1 and batch 8 before the full run.

## The chat template, verified before the pod existed

Gemma 4 has a thinking channel, and `prompts.parse_reply` reads the first `{` it finds — so a
model that thinks out loud before answering would have looked like a systematic disagreement with
the OpenRouter row rather than a bug. The shipped `chat_template.jinja` was rendered locally
against the real prompts (jinja2 only, no weights, no transformers):

- `add_generation_prompt=True, enable_thinking=False` ends the prompt with
  `<|turn>model\n<|channel>thought\n<channel|>` — an already-closed thought channel, which is the
  local equivalent of the `reasoning: {"enabled": false}` every 3b request carried.
- `enable_thinking` already defaults to false, so passing it explicitly is a **pin**, not a change:
  the rendered strings are byte-identical either way. It is passed because a template revision that
  flipped the default would silently change every reply.
- The template emits `<bos>` itself, which is why the tokenizer is called with
  `add_special_tokens=False`; a second BOS would shift every position.
- Both fixed prompts appear verbatim in the rendered string and the row is fenced as
  `<comment>…</comment>` / `<post>…</post>`, so the measurement's prompt survives templating whole.

## Deviations from `docs/PROMPT-4a.md`

Every departure is logged here. Silence is not compliance.

| # | Contract text | What was done | Why |
|---|---|---|---|
| F1 | Step 0: "Expect modified team-lead files … (docs/STATUS.md, docs/SPEC.md, docs/PROMPT-4a.md, knowledge/daily_logs/2026-07-31.md, knowledge/index.md)" | The actual dirty set was committed as the one commit: the three named `docs/` files, `knowledge/index.md`, **`knowledge/daily_logs/2026-08-01.md`** instead of `2026-07-31.md`, and **`knowledge/hot.md`**, which the list omits. | The `/close` that produced them ran just past midnight, so the Stop hook stamped the new day's log; the SessionStart hook then refreshed `hot.md`'s auto-generated block. Both are hook output, not edits. "Commit them all as ONE commit" was followed on the set that actually existed. |
| F2 | Step 1: "batching as memory allows (greedy — batch size must not change outputs)" | The run went at **`--batch-size 1`**. | The parenthesis was treated as a claim to test, not a licence. At batch 8, one probe row of 24 came back with different intents than at batch 1 (`[]` against `["packaging", "quality"]`) — same weights, same prompt, greedy, temperature 0. Left padding and kernel selection move a logit on bitsandbytes NF4 + A6000, so the premise of "batching as memory allows" does not hold here. Batch 1 was then checked the other way: the same 48-row probe twice, byte-identical labels. Cost of the choice: 3.04 s/row, 39 min for 758 rows — inside every ceiling. |
| F3 | Step 2: "create a ~100 GB network volume, then an A6000 48 GB pod attached to it" | Datacenter **CA-MTL-3**, not the one with the most A6000 stock. | Network volumes exist in a different set of datacenters than the A6000 does. `EU-SE-1` had the best stock (`Medium`) and does not take volumes at all; the intersection of the two lists was `CA-MTL-3` (`Low`) and `EU-RO-1` (no stock). Discovered by the create call's own error message, before a volume existed — picking on stock alone and finding out afterwards is a second volume and a second monthly bill. |
| F4 | Step 2: "env install from the `gpu` extra" | Installed into a venv on the network volume (`python3 -m venv --system-site-packages /workspace/venv`), not into the image's Python. | The RunPod PyTorch image's Python is PEP 668 "externally managed" and refuses a plain `pip install`. `--system-site-packages` reuses the image's CUDA-matched `torch 2.8.0+cu128` instead of pulling ~3 GB of a possibly different build, and the venv lives on the volume so step 4b inherits it. |
| F5 | Step 1: "Provenance additions: … pod id" | `RUNPOD_POD_ID` is exported by hand in the run command. | RunPod sets it for the container's main process, not for an SSH session, so the first `--dry-run` recorded `pod_id: None`. Caught by reading the printed provenance block rather than by trusting the field existed. |

**Deviations: F1–F5 above. Nothing else departed from `docs/PROMPT-4a.md`.**

## What the preflight review caught, before the pod was paid for

The local path could not be tested on this Mac — no CUDA, and 62 GB of weights — so it went through
an adversarial read-only review (five lenses, each finding independently verified by a refuter)
while the pod downloaded. Twelve findings survived verification; all twelve were fixed in `ec2dfc9`
before the run. The three that would have cost real money:

1. **`--probe` dereferenced a null budget on the local backend.** Three of the runbook's five smoke
   commands would have crashed with `AttributeError` *after* loading 62 GB and generating the rows.
   No test drove `main()` with `--backend local --probe`; one does now.
2. **The batch-invariance check compared aggregate counts**, which are equal whenever both batch
   sizes merely parse — a check that could not fail, and which sat on top of the crash above, so two
   empty files would have `diff`ed clean and printed "batch invariant". `--probe` now prints the
   per-row prediction lines and the runbook diffs those behind `test -s` guards. This is the finding
   that made F2 possible: without it the run would have gone at batch 8 and quietly used labels that
   batch size had moved.
3. **One transient generation error was charged to all rows of its batch.** The OpenRouter client
   retries each row six times; the local path had none, and the 2% limit is 2.16 rows on the 108-row
   holdout — a single hiccup at batch 8 would have ended the run. A failed batch is now retried row
   by row and only rows that fail alone are counted.

Also fixed: `add_special_tokens=False` rested on an unasserted claim that the chat template emits
`<bos>` (now asserted at construction, with a negative-control test); `--revision` and
`--model-path` were accepted and recorded nowhere; the artifact ratchet covered only the prediction
dump and now covers every `*_path` with a matching `*_sha256`, which is what makes the fixed-name
`results/g1b_slice.json` safe.

## The run

One run, no re-runs. 758 rows, batch size 1, 39 minutes, `gate_anchor_valid: true`:

| input | scored | parse | generation | api | truncated |
|---|---|---|---|---|---|
| comments_test | 400/400 | 0 | 0 | 0 | 0 |
| posts_test | 250/250 | 0 | 0 | 0 | 0 |
| sarcasm_holdout | 108/108 | 0 | 0 | 0 | 0 |

379 443 prompt tokens, 14 782 completion tokens — ~19.5 completion tokens per row against a 256
ceiling, so `max_new_tokens` was never close to binding and the zero in the truncated column is a
measurement rather than a coincidence. The numbers, the cross-check table and the G1b slice are in
`knowledge/decisions/phase4-own-pod-anchor.md`; nothing is repeated here.

## Build log

- 2026-08-01 — step 0: the phase-3 close and the 4a briefing committed as one commit (`952e5dd`);
  the Write-tool probe on `docs/STATUS.md` refused with *"File is in a directory that is denied by
  your permission settings."* before the file was touched, `git status` clean afterwards.
- 2026-08-01 — go/no-go on the weights before any spend: `google/gemma-4-31B-it` on Hugging Face is
  **not gated**, Apache-2.0, 62.6 GB, `Gemma4ForConditionalGeneration`. A gated repo would have been
  an operator action and a stop.
- 2026-08-01 — the local backend and its tests (`4165306`); the $25 guard and the runbook
  (`57c976f`); the preflight review's twelve fixes (`ec2dfc9`).
- 2026-08-01 08:41 UTC — volume `gfwa2an8fn` (100 GB, CA-MTL-3) and pod `gxkdecf3g7k3y7`
  (RTX A6000, $0.53/hr, auto-stop 14:30 UTC). Weights downloaded in 3 minutes.
- 2026-08-01 09:11–09:45 UTC — the run. Pod stopped 09:52 UTC, `desiredStatus: EXITED`, the moment
  the artifacts were on this Mac and both sha256 fields re-derived. Volume kept for 4b.
- 2026-08-01 — phase spend **$0.6203 of $25.00**, volume included. The pod itself was ~$0.62 of
  wall-clock at $0.53/hr; the volume keeps billing while stopped, which is why the guard reads the
  account balance and not only the pod billing rows.
