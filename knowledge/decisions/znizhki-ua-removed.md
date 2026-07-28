---
type: decision
id: dec-2026-07-27-znizhki-ua-removed
date: 2026-07-27
status: accepted
tags: [decision]
---

# znizhki-ua dropped from the registry after the entry check

**Context:** SPEC §2 named `@znizhki_ua` as an aggregator candidate. The Phase 2b entry check
resolves every handle, verifies comments are enabled and measures traffic before collection.

**Decision:** `znizhki-ua` was removed from `config/registry.yaml`; `@msuaaaa`, found by the entry
check's `--discover` sweep, took the aggregator slot.

**Numbers:** the channel's entire history is 7 posts from March 2024 — 0 records inside the
backfill window. The registry went from 5 candidate sources to 4 verified ones. `@silpoua` and
`@varus_ua` were dropped in the same pass (unresolvable and dead).

**Why:** a dead channel collects nothing while looking like coverage. The check's printed table
hid it at first because it showed posts/day without the window — the fix was reading the window,
not the rate.

**Alternatives rejected:** keeping it as a nominal source until Phase 3.

**Sources:** config/registry.yaml (removal comment) · data/entry_check_report.json ·
[[2026-07-27]] · related [[retail-chains-pivot]].
