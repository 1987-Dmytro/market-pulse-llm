---
type: decision
id: dec-2026-07-26-telegram-only-mvp
date: 2026-07-26
status: accepted
tags: [decision]
---

# Telegram-only MVP, $0 data budget

**Context:** SPEC §2 costed four source families in 2026-07: Telegram via MTProto (free), X API
(pay-per-use), FB/IG via managed scrapers, and retailer website monitoring.

**Decision:** the MVP collects from Telegram only, at a $0 data budget. The other families are
future extensions behind the source-agnostic connector interface — no code for them in the MVP.

**Numbers:** the corpus collected under this decision is 11,338 comments + 6,057 posts from 4
verified sources; the pre-registered collection gate was ≥5,000 comments, passed ×2.3. Data
spend: $0.

**Why:** MTProto access is legal and free with a dedicated account and conservative rate limits;
every other family costs money, carries ToS risk, or both.

**Alternatives rejected:** X API pay-per-use · FB/IG managed scrapers · website monitoring — all
researched and costed, deferred to a later track rather than dropped.

**Sources:** docs/SPEC.md §1 (MVP constraint) and §2 (source table) · docs/STATUS.md, key
decision 1 · related [[retail-chains-pivot]].
