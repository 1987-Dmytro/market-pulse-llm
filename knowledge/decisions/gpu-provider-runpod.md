---
type: decision
id: dec-2026-07-28-gpu-provider-runpod
date: 2026-07-28
status: accepted
tags: [decision]
---

# GPU provider: RunPod, with Vast.ai as the cheap-experiment fallback

**Context:** SPEC §7 puts the fine-tune on a rented NVIDIA GPU and Phase 3b is the first step that
actually rents one. The provider was an open item in docs/STATUS.md until the research finished.

**Decision (2026-07-28):** **RunPod**, Secure Cloud, EU region where one is available. **Vast.ai**
stays as the fallback for cheap throwaway experiments. docs/STATUS.md scheduled this ADR for the
3b prompt; it is recorded here instead, ahead of the spend.

**Numbers:** RTX 4090 at $0.34/hour; Network Volumes at $0.07/GB/month. Surveyed: RunPod, Vast.ai,
Lambda, and the European Verda, Hyperstack and Scaleway.

**Why:** the balance of the three things this project needs at once — an hourly rate low enough for
a QLoRA run, persistent Network Volumes so a checkpoint survives between sessions, and a serverless
mode the production loop can reuse for the demo ([[architecture-stack]]). No single competitor won
on all three.

**Alternatives rejected:** Vast.ai as the primary — cheaper per hour, but a marketplace of
individual hosts, kept for experiments where an interrupted run costs nothing. Lambda, Verda,
Hyperstack and Scaleway — surveyed and not chosen on the same price/volumes/serverless balance;
the European ones remain the answer if data residency ever becomes a requirement.

**Sources:** docs/STATUS.md, "~~GPU-провайдер~~ РЕШЕНО 2026-07-28" · docs/SPEC.md §7 ·
[[2026-07-28]] · related [[architecture-stack]].
