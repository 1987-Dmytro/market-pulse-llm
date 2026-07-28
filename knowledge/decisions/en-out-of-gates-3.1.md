---
type: decision
id: dec-2026-07-27-en-out-of-gates-3.1
date: 2026-07-27
status: accepted
tags: [decision]
---

# EN removed from the per-language gates (amendment 3.1)

**Context:** G1a is a per-language gate over the frozen comment test set. The collected corpus is
UA-dominant — the retail chains post in Ukrainian and their audiences answer in UA or RU.

**Decision (SPEC amendment 3.1, approved 2026-07-27):** gates run on UA and RU only. The model
stays multilingual; EN support is untested and is not claimed. Decided before any baseline was
scored.

**Numbers:** 8 EN comments in the 2,000-row annotation sample. In the frozen test set EN ends up
with 0 of 400 rows (UA 248, RU 86, `other` 66) — `other` is the langid heuristic's failures, not
a fourth language, and is scored in the overall macro-F1 only.

**Why:** a per-language metric over n=8 measures nothing; publishing one would be worse than
having no EN number at all.

**Alternatives rejected:** keeping EN in the gate over n=8 · oversampling EN rows into the test
set, which would have distorted the split for a language the product does not need.

**Sources:** docs/SPEC.md amendment 3.1 · docs/frozen-testsets.md, gate-depth table ·
docs/STATUS.md, key decision 3.
