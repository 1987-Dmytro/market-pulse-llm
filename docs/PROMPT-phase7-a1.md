# PROMPT — `phase7-a1` (fresh session, $0, ONE feature: README results from result files; plus the lora-c close-out)

You are the executor on `market-pulse-llm`. Ruling (у) of 26.08 re-planned the project: read ONLY
`docs/STATUS.md` §«Живые рулинги» (у) and §«Definition of Done» — nothing else before step 0. The
process diet applies: this contract is ≤50 lines, your report is ≤80 lines, evidence over prose.

## Step 0 — commit team-lead files verbatim, by path (never `-A`)
`docs/STATUS.md`, `docs/PROMPT-phase7-a1.md`, `docs/reviews/2026-08-26-lora-c-week-retro.md`,
`docs/reviews/2026-08-26-replan-and-process-diet.md`. Baseline: `make check-stamped` (read the
stamped output; quote the counts).

## Step 1 — lora-c close-out ($0, mechanical; one commit)
a. `results/prereg_lora_c_close.json` — sidecar, never the frozen file: `status: CLOSED-UNSPENT`,
   ruling (у) quoted through `quoted()` from STATUS, frozen sha `4d5a8f1d34765b4a…` asserted
   unchanged, the volume listings from (c). `results/prereg_lora_c.json` is NOT edited.
b. ADR `knowledge/decisions/lora-c-closed-by-stop-rule.md` (+ INDEX line), ≤30 lines: data reality
   (≤41 train / 8 eval positives), arm A's bar 1 unreachable by construction, lora-b red on the same
   data, `docs/PRODUCT.md` scope («the ONLY thing we fine-tune»); the measured numbers stay:
   89.961 s/step, 49.54 GiB peak at 3 072 on A100 PCIe. Reopen condition: a labelling contract with
   ≥300 positives.
c. Delete network volume `mp-lora-c` (`runpodctl`): list BEFORE and AFTER, `mp-srv2` is the positive
   control and MUST remain; both listings go into the sidecar verbatim. No pod, no endpoint.
d. Seed `results/measurements.jsonl` — one JSON row per measurement: `what, value, unit, hardware,
   seq_len, date, source` (artifact path + sha8, or report path + section). Seed from STATUS
   §«Реестр измерений»; a number you cannot trace to an artifact is NOT seeded — list those in the
   report instead.
e. `docs/FEATURES-phase7.json` — the DoD rows A1–A6 + B from STATUS: `id, title, verify, status
   (todo|done), report`. Executor-owned progress file: you flip `status`, the team lead ticks STATUS.

## Step 2 — feature A1: the README results table, built from files
- `scripts/build_readme.py` renders the block between `<!-- results:begin -->` / `<!-- results:end -->`
  in `README.md` from `results/baselines.json` + `results/verdict_45h2.json`. Shipped arm =
  `without-plast`; the verdict's `anchor.timestamp` selects the zero-shot base rows. Rows: TF-IDF+
  logreg · XLM-R · Qwen3.5-9B zero-shot · Qwen3.6-27B zero-shot · Gemma-4-31B zero-shot · Claude
  Haiku 4.5 (reference; mark unpaired if its n differs) · **Gemma-4-31B + QLoRA 4.5h2**. Columns:
  G1a overall (ua / ru), G1b fixed/n, G1c, G1d, G1e, gate verdict; n per test set; footnote naming
  each source file + sha8.
- `make readme` target. Law 3.20: the script exits non-zero when a source file or key is missing.
  Exactly two tests: (1) drive `main()` on a tmp copy with one source removed → non-zero;
  (2) rendered numbers equal the JSON values.
- Replace the stale «No measured numbers are published yet» paragraph with 10–15 English lines:
  what the model does, the caveats (G1c fails by 0.0005; G1b n = 38 by pre-registered fallback;
  the shipped arm's per-row dump is lost — `results/predictions/LOST.md`), links to PRODUCT/SPEC.
- Verify: `make readme` idempotent (second run = no diff), `make check` green, README renders.

## Report — `docs/reports/phase7-a1.md`, ≤80 lines
What · where (paths) · evidence (commands and what they returned: stamped counts, `make readme`
output, both volume listings, sidecar sha) · deviations only where you departed from THIS contract
or touched money/spec (enum v2 tags, Dv from 844) · one line of Process signals. Flip A1 in
`docs/FEATURES-phase7.json`. No per-report checker script, no separate vault-tail deliverable
(`/save` as usual). STOP — the team lead accepts by opening README and the sidecar.

**DO NOT:** edit team-lead files (STATUS, SPEC, PROMPT-*, docs/reviews/); edit `results/prereg_lora_c.json`
or any sealed record; touch `mp-srv2`; create a pod or endpoint; hand-type a number into README;
`git add -A`; `make fmt` repo-wide; add gates, rungs or tests beyond the two named.
