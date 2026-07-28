---
type: decision
id: dec-2026-07-28-frontier-api-reference-baseline
date: 2026-07-28
status: accepted
tags: [decision]
---

# A frontier-API reference row in Phase 3 — reference, not a gate

**Context:** SPEC §5 requires every comparison table to carry the cheapest realistic baseline, and
Phase 3 pre-registers three: TF-IDF + logreg, XLM-R, and the zero-shot base LLM. None of them
answers the question an operator will ask anyway — *what would simply calling a frontier API cost
and score?*

**Decision (2026-07-28):** add a fourth row to the Phase 3 table, a zero-shot frontier API
(Claude Haiku), as a **reference**. Gates G1a–G1e stay pinned to the three primary baselines: the
reference row is reported next to them and never enters a gate arithmetic.

**Numbers:** ~$1–3, one-off, for the whole reference run — small enough that the row costs less
than arguing about it.

**Why:** the honest framing of "cheapest realistic alternative" includes the alternative of not
training anything at all, and refusing to measure it would leave the project's central claim
untested. Keeping it out of the gates is what stops that convenience from moving a pre-registered
number: the gates were fixed before any baseline was scored (SPEC §5, "pre-registered"), and
adding a row is not a reason to redefine them.

**Alternatives rejected:** making the frontier API a gated baseline — it would rewrite
pre-registered gates after the fact, and it compares against a moving target no one here versions.
Leaving it out entirely — cheap to run, and the number is one the operator needs.

**Sources:** docs/STATUS.md, "Бейзлайны Phase 3 расширены" · docs/SPEC.md §5 · [[2026-07-28]] ·
related [[architecture-stack]], [[gpu-provider-runpod]].
