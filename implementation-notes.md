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
- 2026-08-01 — phase spend **$0.6203 of $25.00 at 09:52 UTC**, when the pod stopped; **$0.6456 at
  10:15 UTC**. The volume bills continuously, so a phase figure without its timestamp is stale by
  construction. The pod itself was ~$0.62 of
  wall-clock at $0.53/hr; the volume keeps billing while stopped, which is why the guard reads the
  account balance and not only the pod billing rows.

## Operator decision received after the report (2026-08-01)

**The own-pod row is baseline (c) everywhere**, not only the G1d/G1e anchor — the second open
question of the report, closed by the operator before 4b trains and before any fine-tuned number
exists. Recorded in `knowledge/decisions/phase4-own-pod-anchor.md` §(f) with the bar table it
implies. No code changed: nothing in `src/` or `scripts/` selects a baseline row today, and adding
that machinery now would be building 4b's comparison ahead of 4b.

The decision made one arithmetic fact unavoidable and it went straight back to the operator:
**G1d's bar is 0.9084 + 0.10 = 1.0084, above the 1.0 ceiling of a macro-F1.** The condition predates
4a — on the OpenRouter anchor it was G1e that was impossible (1.0211) and G1d that was merely brutal
(0.9898) — so no anchor makes both +10 pp gates satisfiable. The executor does not touch SPEC §5;
flagged and left.

# Implementation notes — Phase 4b

Executed under `docs/PROMPT-4b.md` rev. 1 on 2026-08-01, after 4a was accepted and SPEC amendment
3.5 landed. Scope: the scorer learns the persisted slice, the QLoRA trainer and its frozen config,
one training smoke. **No full training run, and nothing scored a frozen set or the holdout.**

## Read-back, before any file changed

- **The two things 4b must not do:** no full training runs (that is 4c, after this report is
  accepted), and no scoring of any frozen set or the holdout by anything in this step — the
  one-attempt gates see a fine-tuned model exactly once.
- **The pre-registered synthetic selection rule** (amendment 3.4 (3)): the synthetic source stays
  iff its arm's G1b fix-rate is strictly higher AND no other gated head is lower by more than
  0.5 pp; both columns published, no third run, no retraining after gate numbers are seen.
- **The per-arm hour ceiling:** 4 h (amendment 3.4 (4)); a projection over it stops the line for an
  operator decision.
- **"Fixed" under amendment 3.5 (3):** a G1b slice row is fixed iff the fine-tuned model is correct
  on BOTH sentiment and sarcasm for that row — it leaves the union that put it in the slice.

## Assumptions stated before the code was written

1. **`unclear` rows are dropped from training** (the brief's default, taken). 694 of 1 600 comments
   and 206 of 746 candidates — a 43% drop on the comment sources. A row the annotator could not
   decide has no right answer to teach, and SPEC §4 already excludes it from every gate; training
   on it would teach a label `parse_reply` rejects out of hand.
2. **The brief's "never read `data/frozen/*`" means the frozen test inputs**, not the folder: the
   same sentence names `comments_train.jsonl` and `posts_train.jsonl` as training sources and both
   live there. Enforced as a named refusal list — the two test sets, the holdout and the holdout
   pool — rather than a path prefix, so it can neither forbid the training data nor accidentally
   permit a test set.
3. **The carve is held out of training**, 24 rows drawn from the real pool before the synthetic
   rows join. "A carve from the training pool" that stayed in training would report training loss
   under another name; drawing it after the synthetic rows would break arm identity.
4. **`gate_thresholds` refuses a bar above 1.0.** The lesson of 4a's escalation turned into a
   guard: a bounded metric cannot clear `anchor + margin` when that exceeds its ceiling, and the
   cheapest moment to notice is when the anchor lands.
5. **The smoke's adapter is evidence, not an artefact.** 4c trains from scratch on the same config;
   the smoke's 490 MB adapter was hashed, its `adapter_config.json` kept, and the file left on the
   pod that was then deleted.

## The train/eval skew caught before the pod existed

Rendering the whole assistant turn through the chat template — the obvious way to build a training
example — produces a different prefix than the eval path sends. With `enable_thinking=False` the
*generation* prompt ends with an already-closed thinking channel; the *turn* form drops that
channel entirely:

```
eval / generation prompt : …</comment><turn|>\n<|turn>model\n<|channel>thought\n<channel|>
assistant-turn form      : …</comment><turn|>\n<|turn>model\n{"sentiment": …}<turn|>\n
```

Training on the turn form would have conditioned the model on a context no gate row ever carries —
no error, no failing assert at gate time, just lower numbers and nothing to point at. The
assertion that caught it was written because the split needed one, and it fired on the real
template on this Mac, before any pod was created. The trainer now takes the prompt from the same
`apply_chat_template(..., **local_llm.CHAT_TEMPLATE)` call the eval client makes and only the
end-of-turn marker from the turn form.

## What the stub run of the training loop caught

The loop is the densest new logic in 4b and had never executed, so it was driven end to end on this
Mac's CPU with a stub model — real tokenizer, real examples, a fake bitsandbytes optimizer.

1. `collate()` returns a plain dict and the loop called `.to(device)` on it. That is
   `BatchEncoding`'s method, not `dict`'s: the first forward pass of the first paid step would have
   died with `AttributeError` after a 62 GB load.
2. The cosine schedule was built over `min(planned, --max-steps)`, so a 50-step smoke decayed the
   learning rate to zero inside the smoke and previewed a trajectory the full run never follows.

The same run exercised the OOM branch (micro-batch 2 → 1, accumulation 2 → 4, effective batch
held) and resume (step 6 → 8, row index restored), neither of which the real smoke happened to
touch.

## The record's two G1d rows

`anchor_values` was first written as a dict keyed by gate id, and it returned the **wrong G1d**:
`build_gates` writes two rows under that id — post_type, which gates, and relevance, which
amendment 3.3 reports beside the gate and never inside it. The bar came out 0.9315 instead of
0.8984 and looked entirely plausible. It now selects on the metric name and refuses anything but
exactly one match. Nothing downstream had consumed the wrong number.

## Deviations from `docs/PROMPT-4b.md`

- **D1 — Step 0's docs commit carried less than the brief expected.** `docs/SPEC.md` rev. 3.5 and
  `docs/STATUS.md` were already in the tree at 12:18 on 2026-08-01 and went into `35c44c1`, so this
  step's commit carries `docs/PROMPT-4b.md` and the day's records only. Named because `35c44c1`'s
  own message flags G1d's bar as unresolved while the SPEC text in the same commit resolves it —
  an inconsistency of mine, retired in the Step 0 commit body.
- **D2 — the smoke ran in US-TX-1 on a volume-less pod, not in CA-MTL-3 on the network volume.**
  CA-MTL-3 had no A6000 from 10:49 to 11:38 UTC and the exited 4a pod's host had no free GPU. The
  fallback re-downloaded the 62 GB in 4 minutes (~$0.04) onto an 80 GB container disk. Same card
  and driver as 4a, so `s/step` transfers; the pod was **deleted** rather than stopped, because a
  container disk bills by the month whether the pod runs or not. Not gate-relevant: the smoke
  measures mechanics and throughput, not a gate. See the ADR §(g) — the same constraint is a real
  scheduling risk for 4c and it is an operator decision.
- **D3 — `results/baselines.json` was not touched.** The brief does not ask for a record and the
  smoke's numbers are meaningless by construction; an append-only anchor file must not carry a row
  that looks like a baseline and is not.
- **D4 — the with-synthetic arm's dataset was built but not trained**, as the brief specifies
  ("smoke the `--with-synthetic` dataset BUILD too; no second training needed"). Its content hash
  was reproduced on the pod.

Nothing else. No prompt, frozen file, slice, spend anchor, threshold or gate definition changed.

## What 4c should prove before it starts a four-hour arm

**The trainable adapter reload has only been exercised against a stub.** The stub run verified the
loop's bookkeeping (step and row index restored) and the smoke verified `PeftModel.from_pretrained`
for *inference*, where `is_trainable` defaults to false. The path that has never run on the real
stack is the reload with `is_trainable=True` onto a k-bit-prepared base, plus
`torch.load(state.pt, weights_only=True)` on a 250 MB paged-AdamW state. With arms of 3.42 h and
4.37 h that cannot be paused, resume is the only thing between a death at hour three and a lost
run — so 4c should train three steps, kill them, resume, and watch the loss continue. Ten minutes,
before it is needed rather than after.

## The run

| | |
|---|---|
| pod | `ouhimpvjem3spe`, RTX A6000 48 GB, US-TX-1, secure, no network volume |
| stack | driver 570.195.03 · CUDA 12.8 · torch 2.8.0+cu128 · transformers 5.14.1 · bitsandbytes 0.50.0 · peft 0.20.0 |
| dataset | real-only arm, 2 171 train + 24 carve, `train_sha256 d2fa6742…` reproduced on the pod |
| steps | 50 of a planned 272, micro-batch 2 × accum 8, never halved |
| loss | 0.1799 (step 5) → 0.0399 (step 50); carve 0.0585 → 0.0335 |
| LoRA | 410 modules, all `model.language_model.*`, zero vision modules |
| memory | peak 30.47 GB of 48 (4a's inference figure was 18.9 GB) |
| checkpoint | adapter 490 MB saved, base reloaded from scratch, adapter loaded onto it |
| mechanics | 24 carved training rows at batch size 1, **zero parse failures** |
| wall-clock | 2 261.6 s of training → **45.23 s/step** |
| money | $0.4649 for the session; phase spend **$1.1203 of $25.00** at 12:00 UTC |

## Build log

- 2026-08-01 — `ff471e3` the docs set; `8c2c774` the scorer's slice input, `records.py` and the
  derived bars; `975a731` the trainer and `config/qlora.yaml`; `221d2a1` the 4b runbook;
  `fde75d2` the two stub-run fixes. `make check` green after each.
- 2026-08-01 — CA-MTL-3 A6000 stock observed every 3 minutes from 10:50 to 11:38 UTC: `none`
  throughout, then `Low`. The poller creates nothing; it only reads `runpodctl gpu list`.
- 2026-08-01 — the smoke, 11:07 → 11:46 UTC. Artifacts in `results/train/4b-smoke/`.
- 2026-08-01 — pod stopped (`EXITED` shown), then deleted; only the 4a pod and the CA-MTL-3 volume
  remain. Guard re-read: **$1.1203 of $25.00 spent, $23.8797 remaining.**

## Two things the next session should not relearn

- **Python buffers stdout when it is redirected to a file.** The smoke's `print` lines were still
  in the buffer while the run was 15 minutes in; `loss.jsonl` is written with an explicit
  open/write/close per line and is the live view. `python3 -u` would fix the log.
- **A stopped pod without a network volume still bills for its container disk.** 80 GB is roughly
  the price of the 100 GB network volume, which is why this one was deleted and not stopped.

# Phase 4c — the two arms, and the one attempt

Executed under `docs/PROMPT-4c.md` rev. 1, 2026-08-01 13:33 → 2026-08-02 00:03 UTC. Both arms
trained in full, each scored on the frozen sets exactly once, the pre-registered rule applied, the
five Tier-1 gates decided. The record is [[phase4-gate-verdict]]; this file carries the mechanics.

## Read-back, before any file changed

The selection rule verbatim (amendment 3.4 (3)); the five bars **as `scripts/gate_bars.py` derives
them** — G1a ≥ 0.9418 (floors ua 0.8718, ru 0.8649) · G1b ≥ 27 of n=44 with ≤2 pp macro-F1 loss ·
G1c ≥ 0.8436 · G1d ≥ 0.8984 · G1e ≥ 0.8874; that after any gate number is seen nothing is
retrained, re-scored or reconfigured and no third run exists; the resume protocol and its two-part
PASS; the 5 h per-arm ceiling of amendment 3.6.

## Assumptions stated because they are assumptions

1. **"One arm per pod session" was read as "one pod per arm".** Each arm got a freshly created,
   volume-less pod, deleted once its artifacts were home. The alternative reading — reuse one pod
   for both — would have saved one 62 GB download (~7 min, ~$0.06) and was not taken, because arm
   A's pod carried a `--stop-after` that could not be extended past arm B's needs anyway.
2. **The ≤2 pp G1b guard is measured against `sentiment_macro_f1`'s `overall` on the comment test
   set**, against the same anchor every other bar uses. That reading was already fixed in the
   scorer's docstring at 4b and is not a new decision here.
3. **Reading the committed per-row dumps to characterise a failed gate is analysis, not a frozen-set
   pass.** No model was run outside the two sanctioned arm evals; the G1b breakdown in the ADR is
   arithmetic over files that already existed.
4. **The stale 4a pod is not 4c's to delete.** `gxkdecf3g7k3y7` (`EXITED`, on the CA-MTL-3 network
   volume) predates this step; it is flagged in the report, not touched.

## Deviations

- **D1 — arm A trained at `16e3af1` and was scored at `34a27d7`; arm B ran `34a27d7` throughout.**
  The commit between them fixes a crash in the *eval* script's last line and adds its test.
  `git diff 16e3af1 34a27d7 -- scripts/train_qlora.py config/ src/` is **empty**, so both arms
  trained on identical code, config and seed. Gate-relevant only if that diff were non-empty; it
  was checked, not assumed.
- **D2 — the resume proof's two runs ended at their own `--max-steps` cap rather than being killed
  by a signal.** `docs/PROMPT-4c.md` step 1 says "kill the process". The same unconditional
  `save()` writes the same artifact either way and the reload path under test is unchanged, so the
  proof stands; recorded because it is a difference from the written protocol.
- **D3 — arm A's checkpoints synced every 10–15 minutes, not continuously.** The adapter and
  optimizer state are only rewritten at `save_every: 100` — about every 75 minutes at the measured
  step time — so that save cadence, not the rsync cadence, is the real recovery granularity. A
  crash would have cost ≤75 minutes of training (~$0.66). Recorded rather than fixed: editing a
  frozen config to improve a number nobody is measuring is the wrong trade.
- **D4 — the two pods ran different drivers** (550.127.08 for arm A, 570.195.03 for arm B), because
  volume-less pods land on whichever host has stock. Everything else in the stack was identical and
  both records carry their own `runtime` block. See finding 5 for why bit-identical arms were never
  on the table anyway.

Nothing above is gate-relevant, so nothing stopped for an operator decision. The one thing that
would have — a projection crossing the 5 h ceiling — did not happen: 3.40 h and 4.17 h, both under
4b's own projections.

## The run table

| | resume proof | arm A (real-only) | arm B (with-synthetic) |
|---|---|---|---|
| pod | `wol5tdhnbyrj1c` | `wol5tdhnbyrj1c` | `lxsgsyxdw9jqvd` |
| datacenter | US-TX-1, volume-less, 80 GB | same pod | US-TX-1, volume-less, 80 GB |
| driver | 550.127.08 | 550.127.08 | 570.195.03 |
| rows | 2 171 | 2 171 | 2 771 |
| `train_sha256` | `d2fa6742…` | `d2fa6742…` (= 4b's) | `d6d3c800…` |
| steps | 10 then 15 | **270** | **346** |
| training | ~11 min | **12 244 s = 3.40 h** | **15 022 s = 4.17 h** |
| s/step | 43.6 → 42.9 | 45.35 | 43.42 |
| peak GPU | 29.85 GB | 30.86 GB | 30.84 GB |
| micro × accum | 2 × 8, never halved | 2 × 8, never halved | 2 × 8, never halved |
| adapter sha256 | — | `c0e462af…` | `0566900e…` |
| eval | — | 758/758, 0 failures | 758/758, 0 failures |
| record | — | `2026-08-01T18:37:47Z` | `2026-08-01T23:56:21Z` |

Adapter hashes were computed on the pod and on the Mac and compared before either record was
appended: identical both times, so the sync is verified rather than assumed.

## Build log

- 2026-08-01 — `42ac2ea` the team lead's SPEC rev. 3.6 / STATUS / PROMPT-4c, committed verbatim;
  `b690f02` the arm eval path with its crash-resume checkpoint; `01aa6c9` the selection rule and
  the verdict script; `16e3af1` the 4c runbook and `assert_resumable`; `411bd84` `.gitignore` for
  the 250 MB optimizer state; `34a27d7` the eval's last-line crash and the stub test that found it;
  `8314dfb` arm A. `make check` green after every one.
- 2026-08-01 13:33 → 14:10 UTC — pod, 62 GB download (~7 min at ~235 MB/s), venv, dataset check,
  resume proof.
- 2026-08-01 14:10 → 18:37 UTC — arm A trained and scored. Pod deleted, ledger logged.
- 2026-08-01 18:44 → 23:56 UTC — arm B, second pod, same protocol. Pod deleted, ledger logged.
- 2026-08-02 — `scripts/gate_verdict.py` applied the rule and produced the five verdicts.

## Three things the next session should not relearn

- **A print statement can crash a run after the record is written.** The G1b-slice line at the end
  of `eval_zero_shot.main` was guarded by `anchor_valid` alone; on an arm, `slice_ids` is `None`.
  It would have raised at the end of a 45-minute eval following a 3.4 h training run. The test that
  found it drives `main` through the whole `--record-out` path with stubbed weights — that path had
  never run, because `--smoke` returns before the record is built and `--probe` before it is
  written.
- **`planned` is not `steps`.** `ceil(rows / (micro × accum)) × epochs` over-counts by one step per
  epoch whenever the epoch's micro-batches do not divide by the accumulation, and the leftovers'
  gradients carry into the next epoch's first step. 272 planned, 270 run.
- **Two runs of the same arm at the same seed do not give the same loss.** 0.18010 against 0.18051
  at step 5, identical data and config on the same pod. Say "paired on data and config", never
  "identical".

# Phase 4.5a — the audit pack, and one finding filed rather than fixed

## Registry brand normalization does not fold Unicode homoglyphs

Found while building the 4.5a pack, on the four rows where arm A and gold disagree on `brands`
(G1e's whole disagreement stratum). One of them is not a semantic disagreement at all: gold carries
a watchlist `brand_id`, the model emitted a mention spelled with a **Cyrillic `о` in a Latin-script
word**, and `scorer.normalise_brand` casefolds it and looks it up in `watchlist_aliases` — where it
misses, because the alias table is keyed on the Latin spelling. Two strings that render identically
score as two different entities: one false positive and one false negative on a metric whose whole
gold stratum is 246 posts.

**Filed, not fixed — deliberately.** `docs/PROMPT-4.5a-add.md` §3 says so, and the reason outlives
the prompt: a normalization change would silently redefine every future G1e number against every
past one. The Phase 3 baselines, the own-pod anchor and both Phase 4 arms were all scored through
today's `normalise_brand`; folding homoglyphs would make the next G1e incomparable to all of them
without a single line of the change saying so. It is a test-set-v3-shaped decision, not a bug fix,
and it belongs to the 4.5 follow-ups with its own re-scoring plan (every old run can be re-scored
from its persisted dump at $0 — that is what makes the deferral cheap).

**What it costs meanwhile:** G1e's disagreement stratum is n=4 and at least one of the four is this
artifact, so the effective semantic n is ≤3. The brands ceiling is not estimable from this audit at
any confidence, whatever the operator rules on those four rows. The operator still judges them —
the executor does not pre-empt a verdict — but the harness's brands line should be read as a
placeholder, not a measurement.

# Phase 4.5b — the returns ingested, the harness run once

## What the normalization is allowed to change, and how that is proved

The pack went out as five UTF-8, comma-separated CSVs and came back through a spreadsheet:
semicolons, and verdicts written out as `B — правильная метка label_B`. `scripts/normalize_audit_returns.py`
maps the five forms the returns actually carry by table, derives every verdict twice (the table and
the cell's leading token, which must agree), and — the part that matters — builds every output row
from the **sealed** row with one cell replaced. It then blanks those cells again and requires the
sealed bytes back. A round-trip to the sealed file covers quoting, column order, line endings and
encoding; a field-by-field comparison covers none of them, and this pack is the only copy of 244
verdicts.

Checked outside the script as well, sealed against normalized: 244 verdict cells filled, **0**
non-verdict cells changed, CRLF and comma preserved, no BOM. The verdict tallies reproduce the
team lead's independent count of the returns exactly (A19/B16 · A32/B33/amb2 · A3/B20 · A7/B8 ·
81/23).

## Deviations from `docs/PROMPT-4.5b.md`

1. **"Assert per-row against the empty originals (git HEAD copies)" — there are no HEAD copies.**
   `data/annotation/*` is gitignored (only the frozen sets and the sarcasm pool are exceptions), so
   the sealed pack has never been in git. The authority used instead is the committed
   `results/audit_45a_manifest.json`, whose per-CSV sha256 all five on-disk originals matched
   exactly before the run — a stronger pin than a HEAD copy, since the manifest is the file the
   harness already trusts for the key. The assertion itself is per-row as prompted, plus the byte
   round-trip above.
2. **The record is a sibling file, not an extension of the manifest.** `results/audit_45b_returns.json`
   holds the raw / sealed / normalized sha256 of every file, the verdict tallies and the mapping
   table. The manifest's `csv` shas describe the *sealed empty* pack; overwriting them would erase
   the only record of what went out, and `scripts/audit_ceiling.py` reads `key_sha256` from that
   same file.
3. **G1e: the harness prints it, the record excludes it.** `scripts/audit_ceiling.py` is the
   approved artifact and was run unmodified, so its brands lines are in the complete output. The
   ADR carries G1e as raw verdict counts only, per the team-lead decision of 02.08.
4. **`git_state` took a parameter.** The builder's helper leaves the record it is writing out of its
   own dirty list; it now takes that path as an argument so the normalizer can reuse it instead of
   copying it. The manifest it produces is unchanged.
5. **Four additive ones, none asked for.** The five raw-return sha256 are pinned *inside* the script
   (the prompt made matching them a verify-gate item, i.e. a thing to check afterwards); a rerun
   over an already-normalized pack is a no-op instead of a second overwrite; the normalizer ships
   with 8 tests; and today's daily log carries the checkpoint.

## Two things the next session should not relearn

- **A pin belongs in the script, not in the checklist.** The team lead sha-pinned the authoritative
  return set in the prompt; encoding those five digests in the normalizer means an unauthorized copy
  cannot be ingested by accident, rather than being caught by whoever remembers to hash the files.
  The same guard makes a rerun a no-op: a pack that is neither sealed nor already-normalized stops
  the run instead of being overwritten.
- **For G1b the two ceiling units coincide, and that is arithmetic, not agreement.** The fix-rate is
  the share of the 44 slice rows a perfect model gets right, which is the accuracy ceiling's own
  definition; the control adds nothing because its 8 rows carry no `incorrect`. Nowhere else do the
  columns mean the same thing, and a reader who generalizes from that row will read a macro-F1 bound
  as an accuracy share.

# Phase 4.5c — the law-review pack, test v3, and every dump re-scored

## Three artifacts, three refusal surfaces

- **`scripts/build_intents_law_pack.py`** slices the guideline's `[]` rules out of
  `docs/annotation/comments.md` by anchor string and prints them with the line numbers they came
  from. Nothing is retyped, because a paraphrase of a rule under review is an argument about it —
  and the end-to-end test runs against the real guideline, so an anchor that stops matching fails
  the suite instead of quoting whatever moved into its place. The finished page is swept for
  attribution vocabulary outside the fenced row texts.
- **`scripts/freeze_testsets_v3.py`** applies the 38 rulings and proves the rest: every row that
  took no fix is re-serialised and must reproduce its v2 line byte for byte. That check is what
  turns "v3 differs from v2 in 38 rows" into a statement with a failure mode — a JSON writer that
  reordered keys or changed spacing would otherwise rewrite all 758 rows silently.
- **`scripts/rescore_v3.py`** re-scores from dumps only, verifies each dump against the sha256 its
  own record stored, and names the eight runs that have none. `results/baselines.json` is read and
  never written.

## What the numbers turned out to be

Arm A on the original 44-id slice goes 21/44 → **36/44** under v3, and its G1a overall 0.9107 →
0.9499. G1c and relevance are unchanged to the last decimal, which is the cheapest available proof
that `intents` and `relevant` were not touched. The base model's own error union shrinks 44 → 29
ids, which is why G1b needs two readings and why neither is called *the* fix-rate.

**The fixes came out of arm A's dump.** Where the operator ruled for the arm, v3's gold now carries
arm A's label, so arm A's v3 column is not independent of v3 the way arm B's is. On G1e the sign is
visible: arm A 0.9333 → 0.9744, arm B 0.9577 → 0.9189, on three fixed rows.

## Deviations from `docs/PROMPT-4.5c.md`

1. **The changelog is generated, and the doc quotes it.** `docs/frozen-testsets.md` carries the
   table `freeze_testsets_v3.py` prints, and `tests/test_freeze_v3.py` asserts the doc still
   contains exactly what `results/frozen_v3.json` renders. A hand-typed changelog is a second
   source of truth that disagrees with nothing.
2. **A field the ruling confirms is not logged as a change.** 13 of the 15 pair rulings leave
   `sentiment` where it was; a changelog line reading `negative -> negative` is noise in the one
   document that has to be read row by row. The rulings are counted per head (38); the field-level
   changes are 39 over 37 rows, and all three counts are in the record.
3. **A brand entry's `brand_id` is derived, not copied.** `docs/annotation/posts.md` makes both keys
   mandatory and a prediction carries only the mention, so the id comes from the watchlist alias
   table — the same lookup `scorer.normalise_brand` performs, which makes the written row score
   identically to the entry it came from.
4. **v3 is written for all three inputs**, including one that took no fix, so "v3" names a whole
   test set rather than a subset. In this run all three changed, so the rule is only visible in the
   tests.
5. **Additive, not asked for:** the deriver refuses a count other than the gate's 15/15/5/3; the
   re-scorer is idempotent (a second run appends nothing) and takes `--frozen` / `--slice` /
   `--out` so its tests cannot reach real data; 21 new tests; today's daily log.

## Two things the next session should not relearn

- **A corrected test set does not un-measure anything.** Phase 4's verdict is a v2 result and stays
  one; the v3 columns say what the same predictions would have scored had gold been right. Keeping
  them in a separate file with `gold_version: "v3"` is what stops a program measurement from being
  read as a gate result six weeks later.
- **When gold moves, the base model's error set moves with it.** G1b's denominator is defined as
  "the rows the base model gets wrong", so re-scoring the slice against corrected gold silently
  changes the question unless the pre-registered ids travel with the number. Report both, name both,
  persist the new ids.

# Phase 4.5d — taxonomy v2 prepared, probed, and priced

## The one trap in registering a second prompt

`records.assert_prompt_sha` builds the map it compares against stored records out of
`prompts.TASKS`, and it compares whole maps. A sixth entry there — `"T1v2"` — would have made
**every recorded run fail to verify**, which is the opposite of what "registered beside v1" means.
So `TASKS` is frozen at `("T1", "T2")` and the v2 prompts live in `PROMPTS`/`DELIMITERS`, named by
whoever asks for them. Two tests hold it: one runs the real records through the real check, and its
negative control widens `TASKS` and requires the failure.

The same reasoning kept `scorer.INTENTS` at five members. `run_baseline.py` and
`train_xlmr_baseline.py` build one classifier per member, and `parse_reply("T1", ...)` refuses
anything outside it — a sixth member would have changed old label spaces silently. `INTENTS_V2` is
a new constant and the label space is chosen by task (`prompts.INTENTS_OF`).

## Deviations from `docs/PROMPT-4.5d.md`

1. **Guideline v2 broke the law-review pack builder.** It slices the guideline by anchor strings
   and v2 renamed "Off-topic replies". Re-pointing the anchor would have re-issued the pack quoting
   the law that *replaced* the one the operator ruled on, so `build_intents_law_pack.py` now reads
   the guideline at a pinned revision (`0906de6`, `--guideline-rev` to override). The pack rebuilds
   byte-identically: `c6642920287689b35d13194d263999621069b4bd500bd4e8d54f6f363eda7252`.
2. **The prompt names no re-label model.** Chosen on the only measurement that exists for the job —
   intents micro-F1 against human gold in 3b: `qwen3.6-27b` 0.768, `claude-haiku-4.5` 0.774,
   `gemma-4-31b-it` 0.798. The last is the model under test, so its labels would make part of G1c
   agreement with itself; the first is 4× cheaper than the second at a 0.6 pp difference. The
   alternatives are priced by arithmetic off `results/spend_3b.json`, not by a second probe.
3. **The probe ran twice.** The first 50 rows lost 3 to replies of `{}` — the model's way of saying
   "no intents", which the parser refuses rather than coerces (coercing would hand it the majority
   answer for free). One clause was added to the re-label prompt (*always write the `intents` key*)
   and the same seeded 50 were re-run: 0 unusable. Both runs are in the record under their own
   prompt hashes; total spend $0.0083 of the $2.00 cap.
4. **Three diagnostic calls outside the script**, to see the raw `{}` replies before changing the
   prompt. Their $0.0023 was appended to `results/spend_45d.json` with a note naming them — the
   ledger is the phase's, not the script's.
5. **Two exclusions the prompt does not name decide the counts.** Already-labelled ids live in five
   files, not the batch (3,771 rows), and 1,239 rows sit in threads that carry a test or holdout
   row — an up-label pool feeds training, so those may not be labelled at all. Both are printed as
   funnel steps rather than folded into a single number.
6. **All three appetite tiers are out of reach** (+2k by 88 rows, +9k by 7,088). Reported with the
   collection arithmetic — ~805 comments/month, ~55% labelable — rather than as a bare "NO".
7. **`docs/taxonomy-v2-prep.md` is new.** The prompt names no home for the calibration plan; its
   tables are generated by `uplabel_candidates.render` and a test holds the doc to them.
8. **No escape hatch for test rows.** `relabel_intents.py` refuses any drawn row that is in a
   frozen test file, unconditionally. 4.5e re-labels the test set to build v4 and will have to lift
   that guard explicitly — it is a code change, not a flag that exists today.

## What the probe actually found

| | |
|---|---|
| intent sets that changed | 24 of 50 (48%) |
| ... without gaining `service` | 9 (18%) — drift the taxonomy does not explain |
| rows carrying `service` | 15 (30%), replacing `[]` ×12, `availability` ×2, `price` ×1 |
| cost | $0.000162 a row → $0.45 for the 2,746 rows the prompt names |

The 18% is the number the ≥90% calibration will be deciding on: it is model-versus-annotator
disagreement inside the five old classes, and it is consistent with this model's measured G1c of
0.768. The corpus is also **mined out for sarcasm** — not one row of the 1,912-row labelable pool
scores 3 on the irony heuristic, and the highest score in it is 1.

## Two things the next session should not relearn

- **A prompt's label space is part of its identity.** Widening a shared constant to add a class
  changes what an *old* prompt's parser accepts and what an old baseline's classifier iterates, in
  files nobody edited. Version the vocabulary and route it by task.
- **`{}` is an answer in the model's mind and a failure in the parser's.** Any prompt that allows an
  empty collection has to demand the key explicitly, or it loses rows at the rate the empty class
  occurs — 6% here, and all of them from the class the taxonomy question is about.

## Added after the probe was paid for: the split by `unclear`

The headline drift was computed over all 50 drawn rows, and **half of that draw is `unclear`** —
retailer replies and cross-commenter banter, which every gate excludes. Over a population a third
to a half of which G1c never scores, "30% carry `service`" answers a question about a file rather
than about the measurement. Split, the same 50 rows say: scoreable (n=25) 64% changed, 40% carry
`service`, 24% changed without gaining it; `unclear` (n=25) 32% / 20% / 12%.

Re-running was the wrong way to get that: greedy decoding is not deterministic across a provider's
batches (Phase 4a), so a second run is a second measurement. `relabel_intents.py --from-rows`
re-derives the drift block from the rows the paid run wrote — no requests, cost `0` in the record,
and the record says so. The two paid runs' own `drift` blocks stay as they were written.

# Phase 4.5e — the taxonomy-v2 re-label, staged and put up for calibration

## What ran

Every labelled **non-frozen** row, three files, one column:

| source | rows | staged | frozen ids skipped | unusable |
|---|---:|---:|---:|---:|
| `data/frozen/comments_train.jsonl` | 1600 | 1594 | 0 | 6 |
| `data/annotation/sarcasm_candidates.jsonl` | 746 | 740 | 0 | 6 |
| `data/annotation/sarcasm_holdout_pool.jsonl` | 971 | 915 | 54 | 2 |
| **total** | **3317** | **3249** | **54** | **14** |

3,317 − 54 = **3,263** rows this step may legally label, and 3,263 + the 508 frozen test/holdout ids
= **3,771**, the "every labelled comment row" figure 4.5d priced. That equality is the proof the
file list is complete, and the per-file identity (`source = staged + skipped + unusable`) is
asserted in the script rather than reported by it.

**$0.5448 of the $1.50 cap**, measured as lifetime usage minus the anchor. The ledger's twelve
run entries sum to $0.5778, which is higher: `Budget.reconcile` can only push a run's number *up*,
so a run whose predecessor's cost had not yet posted absorbs the tail of it. The anchored
difference is the phase's spend; the sum of the entries is an upper bound on it.

The first pass took 10.5 minutes at four workers. Each row is its own generation, so concurrency
buys wall-clock and changes no label.

## The rows that came back without an answer are not a random 14

`parse: missing field: intents` for every one of them — the 4.5d failure mode, which the prompt
clause reduced but did not close. Retrying is what `--resume` is for and it worked: **66 → 29 → 18
→ 14** over four passes, at $0.017 for all three retries. The ids repeat between passes, so this is
the model and not the transport.

**Thirteen of the fourteen carried `[]` under v1.** The hole is not random: it sits almost entirely
in the empty class, which is the class the taxonomy question is about. Coercing them to `[]` would
have closed the accounting and quietly handed the model the answer it failed to give — so they are
absent from the staged files, named in the record, and their rows stay on v1 until something
decides them.

## Deviations from `docs/PROMPT-4.5e.md`

1. **`--phase` is required and has no default.** The prompt names one ledger; a forgotten flag
   would have spent 4.5e's rows against 4.5d's anchor and 4.5d's $2.00 cap. `read_ledger` also
   refuses a ledger file that carries another phase's anchor key.
2. **Four workers.** Not asked for. Sequential is ~70 minutes for 3,263 rows and the exposure
   window of a paid run is worth cutting; the pattern (locked budget, ordered results) is
   `eval_zero_shot`'s, which has run this endpoint before.
3. **`--skip-frozen` instead of the bare refusal.** 54 of the holdout pool's 971 rows are the
   frozen holdout's own ids. The guard is not switched off — the post-draw check runs either way
   and the dropped rows are counted; the flag chooses *skip* over *stop*.
4. **`--resume` and incremental writes.** A 3,263-row pass that dies at row 3,000 has still been
   paid for. Rows land on disk as they arrive and are re-emitted in source order at the end; a
   resume re-checks every line already on disk against its source before adopting it.
5. **A staged file is not a drop-in replacement for its source.** `sarcasm_holdout_pool_tax2.jsonl`
   has 915 of 971 rows. The 54 frozen ids are 4.5f's and the 2 unusable are nobody's yet.
6. **`--from-rows` verifies as well as re-derives.** Each staged line must be its source line with
   only `intents` moved, and in the source's order, or the drift pass stops. That makes one command
   the evidence for both verify-gate items instead of a second script nobody would test.
7. **The diagnostic 50 are drawn from *scoreable* changed rows.** The prompt says "50 changed
   rows". `unclear` rows are excluded from every metric, so operator attention spent on them
   answers a question no gate asks.
8. **The denominator is pre-registered in the pack.** The prompt names the ≥90% bar; it does not
   say what a blank cell is. `agreement = correct / 100`, blank or anything else counting against
   the bar — written into the README and the manifest in the same words, before the pack shipped.
9. **`.gitignore`: `!data/annotation/*_tax2.jsonl`.** The two annotation sources are whitelisted by
   name, so their v2 copies would have been ignored and the deliverable would have existed only on
   this laptop.

## What the drift says, over 3,249 rows

| | all | scoreable, n=2059 | `unclear`, n=1190 |
|---|---|---|---|
| intent set changed | 1474, 45% | **49%** | 38% |
| ... without gaining `service` | 473, 15% | **15%** | 14% |
| rows carrying `service` | 1001, 31% | **34%** | 25% |

`service` replaced `[]` 730 times, `price` 118, `availability` 80, `availability + price` 42. The
churn matrix (`results/relabel_45e.json`, `drift.churn`) is what says where it came from: `price`
loses 184 rows and 166 of them now carry `service`; `availability` loses 84 and gains 166 —
149 of the gains are rows that were `[]`, which is drift the taxonomy does not explain and which
the calibration is the only instrument for.

**The probe over-read every one of these.** 4.5d's scoreable half (n=25) said 64% changed, 40%
carrying `service`, 24% unexplained; the full pass says 49% / 34% / 15%. 4.5d called that number a
scoping figure and not a measurement, and the full pass is why.

## Two things the next session should not relearn

- **A JSON-shaped answer goes missing exactly where the answer is "nothing".** Demanding the key in
  the prompt cut it from 6% to 2%; four retries cut it to 0.4%; it does not reach zero, and the
  survivors are the empty class. Any pipeline that fills a collection field has to count that hole
  and report which class it falls in, because coercing it is free and wrong.
- **A retry is only cheap if the run can be resumed by id.** The retries cost $0.017 against a
  first pass of $0.53 — 3% — because `--resume` re-asks exactly the rows that have no answer. A
  re-run of the file would have cost thirty times that and produced a different measurement.

# Phase 4.5f — the verdicts read, three rulings applied, and the emptied rows counted

$0. Four steps, five commits, no API call. The re-label is **accepted**: 100 of 100 gated rows
came back `correct`, against a bar of 0.90 registered before the pack went out.

## The gate is arithmetic, and the arithmetic is checked against the sealed bytes

`scripts/read_calibration_returns.py` does not read the returns and add them up. It rebuilds the
pack first — `build_calibration_pack.load_pairs` → `strata` → the two row builders, seed 42, the
two sample sizes taken from the manifest rather than from the builder's constants — serializes it
in the builder's own dialect and requires the result to hash to the sha256 the manifest pins. It
does: `f26fb86c…` for `gated.csv`, `6192643a…` for `changed.csv`. Only then are the returned cells
compared, one cell at a time, because a spreadsheet round-trip changes bytes (`;`, a BOM, `Old` for
`old`) and changes no row.

Three refusals carry it: an unknown verdict form stops the run (`'правильно' is not one of
['correct', 'incorrect']`); a returned row whose `intents` cell was retyped stops it; rows that
came back in a different order stop it, positionally *and* by id. `verdict` and `notes` are the
only two mutable columns — `notes` because 11902 came back carrying the team lead's transcription
of the operator's dictation.

A blank gated cell is not a missing row. `results/calib_45e_manifest.json` registered it as
disagreement before the pack shipped, so it counts against the bar and the run continues. The real
returns contain no blanks, which is exactly why the behaviour has its own fixture rather than
sharing one with the unknown-form control.

**The record keeps the counter-signal beside the number, not under it.** `gate` is 100/100 = 1.00,
PASS. `diagnostic` is 47 `new` / 2 `old` / 1 `neither`, labelled as not gated and unable to move
the verdict. Both are in `results/calib_45e_verdict.json`, with the rule quoted verbatim and every
per-row verdict.

## The three rulings, and what makes each one law

| id | text | staged v2 | ruling | authority |
|---|---|---|---|---|
| `@VARUS_channel:11972` | `Картопля з печінкою` | `[]` | `["taste"]` | diagnostic verdict `old` |
| `@VARUS_channel:11960` | `З вишнею` | `[]` | `["taste"]` | diagnostic verdict `old` |
| `@VARUS_channel:11902` | `…зʼявився суп том ям` | `["availability"]` | `["taste"]` | verdict `neither` + dictation |

All three are in `comments_train_tax2.jsonl` and the diff is three lines. `old` is never retyped
into the ruling table: a row ruled `old` has its v1 label read out of the **source** file and the
run stops if the two disagree — which is the check that would have caught a transcription slip.
The dictated one cannot be checked that way, so it is carried by its `neither` cell plus the table,
and the record says so; a notes cell is free text and is never validated.

Each rewritten line goes through `relabel.relabelled`, so putting the old intents back has to
reproduce the staged line byte for byte. A second run reports `already ['taste'] — nothing to
apply` and writes nothing, including the record.

**The drift block of `results/relabel_45e.json` is deliberately not recomputed.** It is what the
calibration judged; a block silently corrected by its own verdicts stops describing the thing that
was verdicted. The `fixes` block beside it names each row, both values, the authority, and the
staged sha on either side — which is also the only place the chain from the sealed manifest's
`staged` hashes to the current bytes is written down.

A consequence worth stating: **the reader now refuses to run.** `comments_train_tax2.jsonl` hashes
to `e5a52a08…` where the sealed manifest pins `d2132c1e…`, and the refusal names
`results/calib_45e_verdict.json` as the place the gate was computed. That is the intended end
state, not a regression — the gate is a measurement of a corpus that has since been corrected.

## The emptied rows: 97, and a third of the drift the taxonomy cannot explain

| population | rows | changed | changed w/o `service` | emptied | share of the unexplained |
|---|---:|---:|---:|---:|---:|
| all | 3249 | 1474 | 473 (14.6%) | **97** | **20.5%** |
| scoreable | 2059 | 1018 | 311 (15.1%) | **96** | **30.9%** |
| `unclear` | 1190 | 456 | 162 (13.6%) | 1 | 0.6% |

"The 15%" is `changed_without_service_rate`, and it resolves two ways: 14.6% over all 3,249 rows
(the 473 the prompt names) and 15.1% over the 2,059 a gate scores. The decomposition is
**97 emptied + 376 other = 473** overall, and **96 + 215 = 311** on the population that matters.

Length, as quantiles because the distribution is long-tailed:

| | n | p25 | median | p75 | max |
|---|---:|---:|---:|---:|---:|
| emptied | 97 | 8 | **18** | 30 | 247 |
| the rest | 3152 | 24 | **55** | 109 | 2677 |

The label they lost: `taste` 40, `price` 29, `availability` 12, `packaging` 9, `quality` 6,
`packaging + quality` 1.

The premise is measured, not cited. `prompts.build_messages(TASK, row["text"])` is rendered for a
row that carries all four context fields, and `parent_msg_id`, `msg_id`, `channel` and `date` are
required to be absent from it — so a future change that starts threading a parent into the prompt
ends this explanation instead of leaving it stale. **All 3,249 re-labelled rows are replies**;
the reply share therefore separates nothing, and that is the finding: the parent is missing for
the whole corpus and only bites where the comment alone carries no intent.

The three rulings are **reversed** before counting. This measures the re-labeller, and two of the
three ruled rows are the cleanest instances of the class being measured — leaving them corrected
would have understated it by 2. `changed` 1474 and `changed_without_service` 473 come out equal to
the 4.5e record's own numbers, which is the check that the reversal restored exactly the model's
output. A re-run reproduces every number byte for byte; only the `git` block moves.

## Deviations from `docs/PROMPT-4.5f.md`

1. **The reader stops working after step 2, by design.** It sha-pins the staged files against the
   sealed manifest, and step 2 moves them. The alternative — un-applying known fixes inside the
   reader — buys re-runnability for a one-time gate at the cost of a code path that could rewrite
   history. The refusal names the record instead.
2. **The rulings table lives in code, checked against the verdict record.** Every id must carry the
   stated non-`new` verdict in `results/calib_45e_verdict.json` or the run stops. A ruling that no
   returned cell backs is a label invented by the executor.
3. **The drop measurement reverses the fixes.** Not asked for; without it the number depends on
   which side of step 2 the script runs on, and it drops the two rows that are the best evidence
   for the hypothesis.
4. **The measurement is split three ways** (all / scoreable / `unclear`), following 4.5e's own
   split. The prompt names one share; the gate's population gives a different one (31% against
   20.5%) and reporting only the first would understate it.
5. **The micro-pack ships a README.** The prompt asks for the CSV and its manifest. Twelve lines
   of Russian say what an `intents_v2` cell looks like (`["taste", "service"]`), that `[]` is a
   real answer, and that `intents_v1` is a reference and not a proposal — the alternative is a
   round-trip with the operator over cell format.
6. **The micro-pack's row set is derived twice.** Source minus staged minus frozen, against the
   unusable ids the paid runs recorded; a disagreement stops the build. A list of failures is the
   kind of set that quietly becomes "the ones I happened to collect".
7. **The micro-pack stays gitignored, its manifest is committed.** The pack convention. The filled
   `gated.csv` and `changed.csv` were committed with `git add -f` because the prompt asks for the
   operator-filled pack and those three files are now the authority a gate was computed from.
8. **Four scripts, four records.** `read_calibration_returns.py`, `apply_calibration_rulings.py`,
   `measure_empty_drop.py`, `build_micro_pack.py` — one per step, each with its own tests, because
   the four have different write scopes (nothing / the corpus / nothing / a new pack).

## Two things the next session should not relearn

- **A gate computed from a returned file is only as good as the file it is compared to.** Hashing
  the *returns* proves nothing — they are supposed to differ. What has to be proved is that the
  thing they are compared against is the thing that went out, and the only way to say that is to
  rebuild it and match the sealed sha. It cost one `lineterminator="\n"` and bought the whole
  chain.
- **An operator ruling and a model measurement pull in opposite directions on the same rows.**
  Applying the rulings makes the corpus better and the measurement of the model worse, because the
  corrected rows are the evidence. Whichever artifact the number is about has to be reconstructed
  explicitly — and how many rows were reconstructed has to be printed, or the number silently means
  something different depending on the order the scripts ran in.
