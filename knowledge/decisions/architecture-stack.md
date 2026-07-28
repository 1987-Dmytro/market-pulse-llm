---
type: decision
id: dec-2026-07-28-architecture-stack
date: 2026-07-28
status: accepted
tags: [decision]
---

# Production-loop stack: serverless inference, Mac cron, SQLite, Streamlit

**Context:** SPEC §6 fixes the *shape* of the pipeline (collector → normalize → relevance filter →
model service → aggregation → dashboard) but names no runtime for any of it. The choice was
deliberately deferred and listed in docs/STATUS.md under "решения, которые сознательно отложены",
to be made with the operator once the data phase closed. It was taken at the architecture session
of 2026-07-28, before Phase 3b rents anything.

**Decision (architecture session, 2026-07-28):** four blocks, each replaceable on its own.

| block | choice |
|---|---|
| inference | RunPod serverless, batched 2–4× per day |
| collection loop | Mac cron for the MVP; a ~$5/month VPS when it goes live (Phase 5) |
| aggregates | SQLite |
| dashboard | Streamlit |

**Numbers:** inference ~$2–5/month at 2–4 batches a day; the VPS that replaces Mac cron in Phase 5
~$5/month. Provider and per-hour rates are a separate decision, [[gpu-provider-runpod]].

**Why:** the workload is batch, not interactive — a few runs a day over a Telegram stream — so
paying for an always-on GPU buys nothing, and serverless keeps the monthly bill in single digits.
Independent replaceability is the actual design property: every block can be swapped without
touching the others, which is the same reason SPEC §6 puts the connector interface behind a
source-agnostic boundary.

**Alternatives rejected:** an always-on rented GPU for inference — the batch profile does not
justify it. A VPS from day one is *not* rejected, only deferred: Mac cron is the MVP answer and the
VPS is scheduled for Phase 5, when the loop has to survive a closed laptop. For SQLite and
Streamlit docs/STATUS.md records no competing candidate — noting that rather than inventing one;
they stand on the replaceability principle above.

**Sources:** docs/STATUS.md, "Решения, которые СОЗНАТЕЛЬНО ОТЛОЖЕНЫ" (architecture session of
2026-07-28) · docs/SPEC.md §6 · [[2026-07-28]] · related [[gpu-provider-runpod]],
[[frontier-api-reference-baseline]].
