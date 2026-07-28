---
type: decision
id: dec-2026-07-26-category-and-watchlist
date: 2026-07-26
status: accepted
tags: [decision]
---

# Tracked category = dairy + ice cream, with a brand watchlist

**Context:** SPEC §3 makes the registry the only place where sources, category taxonomy and brand
watchlist are defined, and requires coverage to stay category-wide — the watchlist prioritises,
it never filters.

**Decision:** the tracked category is dairy with all subcategories plus ice cream. The brand
watchlist was confirmed by the operator on 2026-07-26 from docs/WATCHLIST.md. New groups are
added by editing `config/registry.yaml`, never by changing code.

**Numbers:** 2 tracked groups — dairy with 9 subcategories (milk, kefir/ryazhanka, yogurt, curd,
sour cream, butter, cheese, dairy desserts, plant-based analogs) and ice cream as one group with
no subcategory split. 20 watchlist brands, 2 of them the operator's own (Гармонія, Мгарське);
the rest are competitors and the chains' private labels.

**Why:** a category-wide stream with brand highlighting answers "what is happening in the
category", which a watchlist-filtered stream cannot.

**Alternatives rejected:** filtering the stream down to watchlist brands · splitting ice cream
into subcategories before any data showed the split matters.

**Sources:** docs/SPEC.md rev. 3 change note and §3 · config/registry.yaml · docs/WATCHLIST.md.
