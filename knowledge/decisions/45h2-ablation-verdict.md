---
type: decision
id: dec-2026-08-05-45h2-ablation-verdict
date: 2026-08-05
status: accepted
tags: [decision]
---

# The пласт is dropped: it made every gated head worse but one

**Context:** [[45h-v4-and-the-precheck]] built test v4, re-anchored every bar on a fresh own-pod
zero-shot, and committed the selection rule as code before either arm existed. This record is the
numbers and what the rule did with them. Two arms, one data path apart, trained once and scored
once; there is no third run and nothing was reconfigured after a number was seen.

## (a) Both columns

Bars derived by `scripts/gate_bars.py --version v4` from the anchor of 2026-08-04T12:26:38Z; no
threshold is typed anywhere. Verdict artifact: `results/verdict_45h2.json`, printed by
`scripts/gate_verdict_45h.py`.

| | `without-plast` | `with-plast` | delta | bar |
|---|---|---|---|---|
| G1a sentiment macro-F1 | **0.9214** | 0.9264 | +0.0049 | 0.9470 |
| — ua | **0.9306** | 0.9237 | −0.0069 | 0.8764 (floor) |
| — ru | **0.8697** | 0.8943 | **+0.0246** | 0.8840 (floor) |
| G1b slice fix-rate | **23/38** = 0.6053 | 20/38 = 0.5263 | −0.0789 | 23 of 38 |
| G1c intents micro-F1 | **0.8478** | 0.8073 | **−0.0405** | 0.8483 |
| G1d post_type macro-F1 | **0.9586** | 0.9348 | −0.0237 | 0.9090 |
| G1e brand extraction F1 | **0.9610** | 0.9333 | −0.0277 | 0.9283 |
| relevance (reported, never gated) | 1.0000 | 1.0000 | +0.0000 | — |

Provenance: `without-plast` dataset `ba368273cc4d…` / adapter `b3ca630846c7…` / 2 171 rows;
`with-plast` dataset `a4ecb36332f0…` / adapter `d8ef92a5fedd…` / 3 457 rows; `carve_sha256`
`8347abd74ae9…` **identical on both**, which is amendment 3.9 (2) holding. Both arms trained from
the same bundle at commit `551c7828` and were scored at `0310dfe`; each eval scored 758 rows with
**zero failures of any kind**.

## (b) The rule, applied

> the пласт stays iff arm B's G1c is strictly higher than arm A's AND no other gated head of B is
> lower than A's by more than 0.5 pp

It fails at the **first clause**: arm B's G1c is not higher, it is **4.05 pp lower**. Three more
heads then regress past the tolerance (G1b −7.89, G1e −2.77, G1d −2.37 pp). **The пласт is
dropped**, and the selected arm is `without-plast`.

The direction is what makes this a result rather than a null. The пласт is 1 912 rows whose entire
purpose was the `intents` column — it is the up-label the taxonomy-v2 program produced — and
**G1c is the head it damaged most**. That agrees with what the program's own three pre-registered
KILLs had already said about those labels ([[45g3-sitting-gates]], [[45g4-v22-affirmative-rewrite]],
[[45g6-context-lines-probe]]): every stratum came back under the calibration bar, and no prompt
revision moved it. The ablation is the last question that was still open about them, and it is now
closed by measurement instead of by argument.

One head moved up: **ru sentiment, +2.46 pp** — and ru is the smaller language (n=86), where the
per-language clause has always been noise-dominated (`docs/frozen-testsets.md`). It is reported
and it decides nothing.

## (c) The five verdicts, on the selected arm

| gate | value | bar | verdict |
|---|---|---|---|
| G1a overall | 0.9214 | 0.9470 | **FAIL** |
| — ua floor | 0.9306 | 0.8764 | PASS |
| — ru floor | 0.8697 | 0.8840 | **FAIL** |
| G1b fixed | 23 | 23 | **PASS** (exactly at the bar) |
| G1b guard delta | +0.0244 | ≥ −0.0200 | PASS |
| G1c | 0.8478 | 0.8483 | **FAIL** |
| G1d | 0.9586 | 0.9090 | PASS |
| G1e | 0.9610 | 0.9283 | PASS |

**3 of 5**, against Phase 4's 2 of 5 on v2 ([[phase4-gate-verdict]]) — and the two are *not*
comparable as a score: different test set, different anchor, different bars, and a G1b slice of 38
instead of 44. What is comparable is that G1b now passes and did not before.

**G1c fails by 0.0005.** Five ten-thousandths, on a head where the fine-tune gained 4.95 pp over
the anchor and the bar asks for 5.00. It is not retried and no bar is adjusted: a failed gate
closes its question (SPEC §5), the bar was derived before either arm ran, and a threshold that
moves after the number arrives is not a threshold. It is recorded here because a reader who sees
"G1c FAIL" and not the margin would draw a different conclusion than the data supports.

**Two numbers travel with G1b, always.** The v4 slice is **38 ids**, not 44 — the base model errs
on fewer rows of the corrected holdout, which is amendment 3.2's pre-registered fallback and not a
defect. So one row is **2.6 pp** of the fix-rate, and under this phase's rule G1b is a *protected*
head: a single noisy slice row could have dropped an arm that won on G1c. It did not have to
here — arm B lost on the pivot outright.

## (d) What it cost, and what it cost that was not money

| | |
|---|---|
| OpenRouter | **$0.1080** over 555 requests of a $0.30 cap (508 gold rows + 47 re-asked) |
| GPU | **$8.8287** of a $9.00 cap — anchor $0.4204, arm A $3.5255, arm B $4.8828 |
| Phase 4 total | $16.2954 of the $25.00 cap (amendment 3.4 (4)) |
| ceiling | arm A 4.58 h, arm B **7.51 h**, against the 8.5 h the operator authorised on 2026-08-04 |

**Arm A's per-row dump was written and then lost** (`results/predictions/LOST.md`). No gate number
moves and `scored_ids_sha256` still proves which rows were scored, but if gold is ever corrected
again the way 4.5a corrected it, `without-plast` cannot be re-measured and `with-plast` can — so a
future comparison of these two columns would be **unpaired and must say so**.

## (e) Owed to the team lead

Two amendments this executor cannot write, both authorised by the operator on 2026-08-04 and both
recorded in `implementation-notes.md` D2, the runbook and the runs' provenance — **neither is in
`docs/SPEC.md`**: the per-arm ceiling **6.5 h → 8.5 h** (amendment 3.9's 6.5 was set against a
rendering without the parent post) and `config/qlora.yaml` **`max_seq_len` 1024 → 1408**. Without
them a later reader finds arm B at 7.51 h against a stated 6.5 h ceiling and reads a decision as a
breach.

## (f) Provenance

| what | value |
|---|---|
| anchor | `google/gemma-4-31b-it` @ `2026-08-04T12:26:38Z`, test set v4, rendering `T1v2_with_post` |
| bars | `results/gate_bars_45h.json` — derived, none typed |
| slice | `results/g1b_slice_v4.json` — 38 ids, sha256 verified by every arm before its weights loaded |
| rule | `scripts/gate_verdict_45h.py`, committed at `dabc12c` **before** either arm was scored |
| verdict | `results/verdict_45h2.json` |
| arms | `results/train/45h2-arm-a/`, `results/train/45h2-arm-b/` — adapter, loss curve, provenance |
| ledger | `results/spend_45h2.json` — both anchors, three GPU sessions, two OpenRouter runs |
| deviations | `implementation-notes.md` § Phase 4.5h2, D1–D24 |

Related: [[45h-v4-and-the-precheck]] — what v4 is and what the precheck changed;
[[phase4-gate-verdict]] — the verdict this one does not reopen; [[45g6-context-lines-probe]] — the
last KILL before the пласт became an ablation; [[taxonomy-v2-relabel-and-appetite]] — the law the
пласт was labelled under.
