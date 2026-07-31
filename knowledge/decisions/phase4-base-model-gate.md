---
type: decision
id: dec-2026-07-31-phase4-base-model-gate
date: 2026-07-31
status: accepted
tags: [decision]
---

# Phase 4 base model = google/gemma-4-31b-it, and the unpaired 27B row cannot flip that

**Context:** 3b produced three zero-shot candidate rows plus a frontier reference row
([[3b-infra-and-precision]], [[frontier-api-reference-baseline]]). Two questions were left for the
gate: which model Phase 4 fine-tunes — §(f) of that ADR deliberately refused to answer it — and
what to do about `qwen/qwen3.6-27b`, whose rows were scored on fewer instances than everyone
else's and are therefore not paired in the sense SPEC §5 requires.

**Decision (2026-07-31, operator, joint gate review):** the base model is
**`google/gemma-4-31b-it`**; the unpairedness is closed by the bound analysis in §(b) at $0 rather
than by a ~$0.90 re-run; the G1b slice is defined later on our own hardware; and the persistence
gap the review uncovered is fixed forward, not backfilled.

## (a) G1 — the selection

Numbers below are `scripts/show_results.py --last`, the only sanctioned reader of
`results/baselines.json`; none are typed from memory. Gated cells only — G1a is gated on `ua` and
`ru` alone (amendment 3.1), G1d on the 3-class post type alone (amendment 3.3), and G1b has no
value at 3b because the fix-rate needs a fine-tune.

| gated head | **gemma-4-31b-it** | qwen3.5-9b | qwen3.6-27b (run 2) | haiku-4.5 (ref) |
|---|---|---|---|---|
| G1a sentiment macro-F1 · `ua` | **0.8957** | 0.7957 | 0.8536 | 0.8692 |
| G1a sentiment macro-F1 · `ru` | **0.8688** | 0.8579 | 0.8667 | 0.8988 |
| G1c intents micro-F1 | **0.7981** | 0.6252 | 0.7606 | 0.7739 |
| G1d post_type macro-F1 | **0.8898** | 0.5077 | 0.7605 | 0.7718 |
| G1e brand extraction F1 | **0.9211** | 0.6476 | 0.8919 | 0.8537 |

Gemma leads every gated head among the three candidates, and leads the frontier reference row on
four of the five. **The exception is G1a `ru`, where Haiku is ahead by 0.0300** — recorded because
the row exists, not because it changes anything: a reference row never anchors a gate and never
takes part in a selection ([[frontier-api-reference-baseline]]). Two things this table does not
say: `relevance` (0.9505 for Gemma against 0.9778 for both Qwens) is **not gated** under
amendment 3.3 and does not enter the selection, and the 27B column is unpaired — which is what
§(b) is for.

Consequence for [[3b-infra-and-precision]] §(f): G1d and G1e now have an anchor. It is the
**Gemma row**, re-measured on our own pod during the Phase 4 smoke, not the OpenRouter row —
§(d) of that ADR always required the cross-check, and §(b) below is one more reason to want it.

## (b) The bound analysis — why the unpaired 27B row cannot flip the selection

`qwen/qwen3.6-27b` run 2 lost 3 of 400 comments, 1 of 250 posts and 4 of 108 holdout rows to
malformed replies (ids in `diagnostics.failures[].failed_ids`), so its scores sit on 397 / 249 /
104 instances against Gemma's 400 / 250 / 108. A paired comparison would restrict Gemma to the
27B's subset. Per-row predictions were never stored — see §(d) — so that restricted score cannot
be computed. It can be **bounded**, which is enough to answer the only question the operator has:
can the missing instances reverse the ordering?

**Worst case = Gemma was perfect on every dropped row.** Dropping a row Gemma got *wrong* removes
one FP and one FN and can only raise its score; dropping a row it got *right* is the only
direction that hurts. So assuming perfection on all eight bounds the damage.

For a macro-F1 head, removing one correctly classified row of gold class `L` touches that class
only — `TP → TP−1`, gold support `n → n−1`, predicted count `p → p−1`; every other class keeps its
three counts. With `S = n + p`:

```
F1_L  = 2·TP / S
ΔF1_L = 2(TP−1)/(S−2) − 2·TP/S = −2(1 − F1_L)/(S − 2)
TP ≥ 1  ⟹  F1_L ≥ 2/S  ⟹  (1 − F1_L) ≤ (S−2)/S  ⟹  |ΔF1_L| ≤ 2/S ≤ 2/(n + 1)
```

and the macro average divides that by the number of gold-supported labels. Gold labels of the
dropped rows come from the frozen files: the three comments are `ua` / negative, `ua` / negative,
`ua` / neutral (intents `[]`, `[]`, `['quality']`); the post is `promo`, `relevant: false`, no
brands. That the three comments are all `ua` is corroborated independently by the record itself —
the 27B's G1a supports read `ua 245` against Gemma's `248`, with `ru 86` and `other 66` in both.

| gated head | gemma | 27B run 2 | observed gap | worst-case bound | arithmetic | verdict |
|---|---|---|---|---|---|---|
| G1a `ua` | 0.8957 | 0.8536 | **0.0421** | 0.018612 | `2/(135+1)/3 + 2/(134+1)/3 + 2/(75+1)/3` | protected |
| G1a `ru` | 0.8688 | 0.8667 | **0.0021** | 0.000000 | no `ru` row was dropped — the slice is identical, the comparison is already paired | protected |
| G1c intents | 0.7981 | 0.7606 | **0.0376** | 0.008658 | `2·1/(230+1)`; only 1 of 230 gold intent labels sits on a dropped row (0.001763 using the known micro value) | protected |
| G1d post_type | 0.8898 | 0.7605 | **0.1293** | 0.003745 | `2/(177+1)/3` | protected |
| G1e brands | 0.9211 | 0.8919 | **0.0292** | 0.000000 | the dropped post carries 0 gold entities (`gold_entities 36` in both records) — perfect means predicting nothing, so no TP is lost | protected |
| — relevance | 0.9505 | 0.9778 | −0.0273 | n/a | **not gated** (amendment 3.3); listed so the one head the 27B leads is not hidden | — |

G1c is a micro-F1, so the same derivation runs on the totals: `micro = 2T/(N+P)`, removing `g`
correctly predicted gold labels gives `|Δ| ≤ 2g/(N+P) ≤ 2g/(N+1)`, with `N = 230` gold intent
labels across the 400 rows and `g = 1`. Two of the three dropped comments carry no gold intent at
all, so under the perfection assumption they are exact no-ops for this head.

G1b is not in the table because it has no value on either row: amendment 3.2's fix-rate needs a
fine-tune. What the dropped rows change there is the *slice*, and §(c) takes that out of
OpenRouter's hands entirely.

**Every gated head's ordering survives its worst case, so the conclusion holds: the unpaired
table cannot flip the selection.** The 27B rows keep `gate_anchor_valid: false` permanently and
neither run may anchor G1d or G1e. The ~$0.90 paired re-run the operator held in reserve was not
needed and was not spent.

**One margin worth reading twice.** G1a `ru` is protected by a bound of exactly zero, so it is a
true paired result — but the margin is 0.0021, and 3b measured a same-config swing of **0.0298**
on the 27B's own G1d between two runs with identical commit, prompt hash, provider pin,
temperature 0 and seed 42 ([[3b-infra-and-precision]] §(d)). That swing is **14.2× the `ru`
margin**. On `ru` the two models are tied within third-party-endpoint noise; the selection rests
on the other four cells, where the gaps are 0.03–0.13. This does not reopen G1 — it is why §(d)'s
own-pod cross-check is an obligation and not a formality.

## (c) G3 — what defines the G1b slice

Verbatim from the gate review: the G1b slice is the **union** of the base model's sentiment and
sarcasm errors on the frozen holdout — that is the operator's reading of "misclassifies" in
amendment 3.2, the reading [[3b-infra-and-precision]] §(e) explicitly refused to pick. The slice
is **defined by the chosen model's zero-shot re-run on our own pod during the Phase 4 smoke**:
all 108 rows, our hardware, per-row outputs persisted. **OpenRouter's numbers are a preview, not
the slice** — Gemma's run reports `base_errs_sentiment 10`, `base_errs_sarcasm 40`,
`base_errs_union 40`, and the 40/108 that will be quoted in Phase 4 is whatever the own-pod run
produces. (The union equals the sarcasm count because the sentiment errors are a subset of them;
`eval_zero_shot.py` computes it as a real set union, `len(sentiment_errs | sarcasm_errs)`.)

## (d) The persistence gap, and the fix that only points forward

The acceptance review found that `implementation-notes.md` — and the executor's report — claimed a
paired re-score on the intersection was "reproducible from the file". It is not. A 3b record
carries `config.scored_ids_sha256`, a *hash* of the scored id list, plus the failing ids, so the
scored **subset** is recoverable; the **per-row predictions were never written anywhere**, so no
metric can be recomputed on that subset. The $0 paired option offered to the operator rested on
that false claim, and §(b) exists because of it. The finding is recorded, under the original
sentence, in `implementation-notes.md` § "Correction (2026-07-31, team-lead review)".

Fixed forward from step 3c: every real scoring run of `scripts/eval_zero_shot.py` writes
`results/predictions/<slug>--<UTC-ts>.jsonl`, one line per scored row — `input`, `id`, and the
predicted labels only, never gold labels and never source text — and the record gains
`config.predictions_path` and `config.predictions_sha256`. Lines are sorted by `(input, id)` so
the hash depends on the data and not on which worker finished first. **The six existing 3b runs
get no dumps.** They cannot be reconstructed, and a synthesized dump would be worse than the gap
it papers over.

**Sources:** joint gate review 2026-07-31 (operator) · docs/PROMPT-3c.md rev. 1 ·
`scripts/show_results.py --last` over `results/baselines.json` · `data/frozen/*.jsonl` gold labels
· docs/SPEC.md §5 (paired comparisons), amendments 3.1–3.3 · related
[[3b-infra-and-precision]], [[frontier-api-reference-baseline]], [[g1d-gate-clarification-3-3]],
[[hybrid-sarcasm-holdout-3.2]], [[gpu-provider-runpod]].
