# Runbook — Phase 3b baselines

Operator-facing. Copy-paste, in order. Every number these commands produce goes through
`src/market_pulse/scorer.py` into `results/baselines.json`, append-only; nothing here is ever
hand-edited. The decisions behind the commands are in
`knowledge/decisions/3b-infra-and-precision.md`.

**Budget: $8 hard cap across all of 3b.** The runner enforces it against OpenRouter's own usage
figures, not against a local guess. If the cap trips, see the last section — the answer is never
"raise it a little". The 2026-07-31 execution of this runbook spent **$0.78** in total —
$0.749 across the five recorded runs plus a few cents of live sizing probes.

---

## 0. What must be true before you start

- `.env` contains `OPENROUTER_API_KEY=sk-or-v1-…` (template in `.env.example`). No other key is
  needed: no Anthropic key, no vendor SDK, no GPU rented in this step.
- The working tree is clean, or at least `src/`, `scripts/` and `config/` are. Every run stamps the
  commit it was produced against plus the files that were not in it; if that list names code, the
  runner prints a WARNING, because then the recorded commit does not reproduce the numbers.
- `make check` is green.

```bash
cd ~/Desktop/Projects/market-pulse-llm
git status --short
make check
```

## 1. Install

The zero-shot harness needs nothing beyond the dev extra — its HTTP client is `urllib`.

```bash
pip install -e '.[dev]'
```

The XLM-R baseline needs `torch` and `transformers`, isolated in their own extra so `make check`
stays runnable without them:

```bash
pip install -e '.[xlmr]'                  # ~2.5 GB of wheels if torch is not already present
pip install 'transformers>=4.44'          # enough on its own when torch is already installed
```

## 2. Precision probe — free, GET requests only

The pre-registered rule: bf16 for **all three** candidates, otherwise fp8 for all three, never
mixed. This prints the table the rule is applied to and names the branch that fires.

```bash
python3.11 scripts/eval_zero_shot.py --precision-probe
```

Expected, and what happened on 2026-07-31: `qwen/qwen3.6-27b` offers no bf16 endpoint at any
provider, so the **fp8 branch fires** and all three candidates are pinned to fp8. If the probe
reports that neither precision covers all three, **stop and report** — do not improvise a third
option. The probe also re-checks that each pinned endpoint still serves fp8; every real run repeats
that check before spending anything and refuses to start if a pin has moved.

## 3. Dry run — the estimate before the spend

```bash
python3.11 scripts/eval_zero_shot.py --model qwen/qwen3.5-9b --dry-run
```

Prints the pinned endpoint, the prompt hashes, a per-input cost estimate, the per-run cap and how
much of the $8 has gone already. Nothing is spent. The estimates are deliberately conservative:
on 2026-07-31 they read $0.05 / $0.08 / $0.20 for the candidates and $0.63 for Haiku, against
actual spends of $0.034 / $0.034 / $0.129 / $0.514. An estimate several times *above* those is a
reason to stop and report, not to continue.

There is also a fully offline smoke — mocked client, no network, no money — that exercises the whole
pipeline including the failure counters:

```bash
python3.11 scripts/eval_zero_shot.py --model qwen/qwen3.5-9b --smoke
```

## 4. The three candidate rows

One at a time, cheapest first. Each is 758 requests at four workers and takes roughly 5–20 minutes,
deliberately unhurried: fallbacks are off, so a pinned endpoint's rate limit has to be waited out
rather than routed around.

```bash
python3.11 scripts/eval_zero_shot.py --model qwen/qwen3.5-9b
python3.11 scripts/eval_zero_shot.py --model google/gemma-4-31b-it
python3.11 scripts/eval_zero_shot.py --model qwen/qwen3.6-27b
```

After each run, read the line it prints per input:

```
comments_test: scored 400/400 · parse 0 · api 0 · truncated 0
```

`scored` below `rows` means rows were lost, and the two counts mean different things: `parse` is the
model failing to answer in the required shape, `api` is the endpoint failing to answer at all.
Losses above **2%** of any input mark the record `gate_anchor_valid: false`; that run must not
anchor a gate without your decision. Two things that happened on 2026-07-31:

- `venice/fp8` returned HTTP 429 for 11 of 400 comment rows at eight workers. Fixed by four workers
  and six retries; the re-run scored 758/758 and both records are in the file.
- `qwen/qwen3.6-27b` returned JSON without a `sentiment` field on 9 rows and malformed JSON on 1.
  That is the model, not the network — a re-run is not obviously the fix, and the record says so.

## 5. The frontier reference row

Reference only. It never anchors a gate: the record is written so a lookup for `G1d` cannot find it.

```bash
python3.11 scripts/eval_zero_shot.py --model anthropic/claude-haiku-4.5 --reference-only
```

Not `anthropic/claude-haiku-4.5:batch`. OpenRouter serves that variant only through
`/api/beta/batches`, asynchronously; it returns 404 on the endpoint this runner uses. Same model,
about $0.24 more. Passing the `:batch` slug prints that explanation and stops before reading a file.

## 6. XLM-R supervised baseline — local, $0

Always the timed smoke first. It trains a dozen real steps, measures the rate and projects the full
run:

```bash
python3.11 scripts/train_xlmr_baseline.py --smoke
```

Read the `PROJECTED FULL RUN` line. The full run refuses to start above the 60-minute ceiling and
prints the projection instead of training:

```bash
python3.11 scripts/train_xlmr_baseline.py
```

**Measured on this Mac, 2026-07-31 — over the ceiling on both devices, so the full run was not
started:**

| device | seconds/step | projected full run |
|---|---|---|
| `cpu` (default) | 3.503 | **130.8 min** |
| `mps` | 48.117 | **1764.0 min** (29.4 h) |

The default is `cpu` for that reason, not by preference. MPS on this machine is 14× slower per step
and additionally OOMs at its 9.07 GiB allocator ceiling unless the 250k × 768 word-embedding matrix
is frozen — which it is, and which is recorded in the run config rather than left as a silent
hyperparameter. To run it anyway, on a pod or with the ceiling lifted:

```bash
python3.11 scripts/train_xlmr_baseline.py --time-budget-min 180        # accept a longer run
python3.11 scripts/train_xlmr_baseline.py --device mps                 # only where MPS behaves
```

## 7. Read the table

The only sanctioned way to look at a project number. It computes nothing and writes nothing, so
anything it prints came from the scorer.

```bash
python3.11 scripts/show_results.py                          # every run of every model
python3.11 scripts/show_results.py --last                   # the most recent run of each
python3.11 scripts/show_results.py --model qwen/qwen3.5-9b
```

What to look for in a zero-shot row:

| field | reading |
|---|---|
| `G1a … values` | sentiment macro-F1: `overall` plus every language; only `ua` and `ru` are gated |
| `G1b … n.base_errs_*` | how many of the 108 holdout rows this base model gets wrong — the raw material of the G1b slice. Three counts, because amendment 3.2 says "misclassifies" and the holdout carries two labels |
| `G1d`, twice | the gated 3-class post type, and relevance reported beside it (amendment 3.3) |
| `ref` instead of a gate id | a reference-only row; it cannot anchor a gate |
| `diagnostics.gate_anchor_valid` | `false` means the run lost too many rows to be an anchor |
| `diagnostics.failures` | per input: rows, scored, parse vs api failures, the reasons, the ids |
| `config.scored_ids_sha256` | the exact paired subset the numbers were computed on |
| `config.spend_usd` | what that run cost |

`results/spend_3b.json` is the phase ledger: the lifetime OpenRouter usage recorded when 3b started,
plus one line per run. Phase spend is today's usage minus that anchor.

## 8. If the cap trips

The runner stops itself, prints

```
BUDGET CAP TRIPPED: per-run cap $1.50 tripped at $1.5012
No record was written — a partial run must not become a gate anchor.
```

and exits with status 2. Then:

1. **Do not re-run with a bigger `--max-run-usd`.** The per-run cap is a tripwire for a run costing
   an order of magnitude more than its estimate, and that means something changed: a price, a
   prompt, or a model that started emitting reasoning tokens.
2. Compare the estimate the run printed against what it actually spent. The gap is the finding.
3. Read both spend numbers, the ledger's and the provider's:

```bash
python3.11 -c "import json; print(json.load(open('results/spend_3b.json')))"
curl -s https://openrouter.ai/api/v1/credits -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

4. Report to the team lead with both. The $8 cap is the operator's; only the operator raises it, and
   $8 was chosen against a balance of $9.84 that is not being topped up.

A run that trips writes no record, so nothing partial reaches `results/baselines.json`.
