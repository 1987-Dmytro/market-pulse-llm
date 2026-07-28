---
type: decision
id: dec-2026-07-28-g1d-gate-clarification-3-3
date: 2026-07-28
status: accepted
tags: [decision]
---

# G1d gates the 3-class post type, not a relevance blend (amendment 3.3)

**Context:** SPEC §5 rev. 3 worded G1d as "T2 post classification (relevance + 3-class) macro-F1
≥ zero-shot base LLM + 10 pp". `src/market_pulse/scorer.py` read the same gate as the 3-class post
type alone. Phase 3a implemented both heads and scored them separately rather than guess, and
reported the conflict instead of picking a side ([[2026-07-28]]).

**Decision (2026-07-28, operator):** G1d reads **`launch_detection_macro_f1`** — the 3-class
`launch / promo / other` macro-F1 on the frozen post test set. **`relevance_macro_f1` is reported
next to it with its own n and is not gated.** The +10 pp threshold and the test set are unchanged.

**Numbers:** the TF-IDF+logreg baseline (`results/baselines.json`) scores post-type **0.6653** and
relevance **0.8119**. Merging the heads into one 4-class macro average would also put an n=1 class
(relevant + `other`) into the denominator, where a single row moves the average by ~25 pp.

**Why:** the two heads are two metrics, and "+10 pp" means different things on each. Relevance is
near its ceiling already, so a blended number would be moved by whichever head has the least room
to give — the gate would be passable without the model getting better at the thing G1d is about.
Keeping relevance published (with its own n) keeps SPEC §9's critical-path claim measurable: T2a
is the filter the whole pipeline sits behind.

**Alternatives rejected:** one blended 4-class metric — the n=1 class makes it a coin flip, and it
is the arithmetic this ADR exists to avoid. Gating both heads at +10 pp — relevance has no 10 pp
of headroom, so the gate would fail for a reason unrelated to model quality. Leaving the SPEC
ambiguous until Phase 4 — the gate would then be chosen with the fine-tuned number in hand, which
is the one ordering pre-registration exists to forbid.

**Ordering, recorded rather than smoothed over:** unlike amendments 3.1 and 3.2 this one was
decided **after** a baseline was scored. What it changes is which of two already-implemented
metrics is read, not the threshold, the test set or the data; no fine-tuned number exists yet.
The honest description is a disambiguation of a gate that was never one metric — and the fact that
a baseline was visible when it was made belongs in the record.

**Sources:** docs/SPEC.md amendment 3.3 and §5 · `src/market_pulse/scorer.py` docstrings ·
`results/baselines.json` (`tfidf-logreg`) · [[2026-07-28]] · related
[[frontier-api-reference-baseline]].
