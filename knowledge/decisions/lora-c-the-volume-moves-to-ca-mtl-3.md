---
type: decision
date: 2026-08-26
status: accepted
tags: [decision, phase6, lora, migration, volume, money, pod, stock]
---

# The training line's volume moves to CA-MTL-3 — and the cheaper cards arrived 107 minutes late

`lora-c-migrate r2` executed on 2026-08-25 under ruling (с) and was **accepted 2026-08-26**, tally
6/2. One pod, **744 s = $0.287267** of a $1.50 cap. This record is the English long form;
`docs/reports/lora-c-migrate-r2.md` is the report and carries every number.

## What this replaces

Ruling (р) had moved the line to **EU-SE-1 / RTX A6000 / $0.53**. The previous contract's first free
reading refuted it in one command: EU-SE-1 does not support network volumes, and neither do the
other three datacenters that reading's §5 had named. Ruling (с) then chose **CA-MTL-3 / A100 PCIe
80 GB / ≤$1.50/h** — volume-capable by the create endpoint's own enumeration, and the datacenter
`scripts/runbook_4a.md` §1 had chosen on the same intersection on 2026-08-01.

## What was built, and the reading that matters

| | |
|---|---|
| volume | `mp-lora-c` (`soymlju8q0`), 100 GB, CA-MTL-3 |
| weights | 62 580 183 517 B in ~184 s, 12 blobs, **0 incomplete**, snapshot = `842da379…` |
| **the load proof** | the shipped `local_llm.load` put the model on the GPU in **40.22 s at 17.046 GiB of 79.138** |
| card occupancy | **21.5%** — the memory question this line died on twice is closed with room |
| money | 744 s × $1.39/h = **$0.287267**, $1.212733 of the cap unspent |

Two stage measurements are new to this project and every future plan budgets from them: **the venv
build, 132.0 s** (`python -m venv`, 27 packages, and the torch-importing proof line — three things
in one number, not decomposed) and **the download at 340 MB/s** onto a network volume, which
reproduces phase 4a's ~180 s onto the same kind of volume in the same datacenter.

## Rung 5 KILLed, and the rule was not edited

The rung asked whether `du -sb /workspace/hf` moved across the load. It moved — **by 40 bytes**:
`refs/main` (40 B, the resolved revision) and four **zero-byte** `.no_exist` markers for optional
files this repo does not ship. **Blobs written after the download: 0.** The load read 62.58 GB off
the volume and fetched none of it.

The verdict stands as recorded. A HuggingFace cache is not immutable under a read, and an equality
on the CONTAINER grades the loader's own bookkeeping identically to a re-download; the invariant
worth registering is that no BLOB grows. But a threshold edited after the reading it fired on has
stopped being a threshold, so the remedy was written down rather than applied: **step 0.5 of
`lora-c-run r3` carries the blob invariant.** The 40 bytes were enumerated by name and size on the
pod before it was deleted (`results/lora_c_migrate_r2_load_bytes.json`), which is what makes «nothing
was fetched» a reading instead of an argument. See
[[an_invariant_on_the_container_not_the_payload]].

## The choice the operator made, priced before the money

The issue-time stock reading at **19:48:13Z** — 107 minutes after the table ruling (с) was written
on — held **four cheaper volume-capable rows at ≥48 GB**, three of them in **US-KS-2**, a datacenter
that also carries the ruling's own A100 at the same $1.39:

| card | VRAM | datacenter | $/h | what the r2 remainder ($3.2394) buys per step |
|---|---|---|---|---|
| RTX A6000 | 48 | US-KS-2 | 0.53 | **102.84 s** — the only row above lora-b's measured 61.047 |
| L40 | 48 | US-KS-2 | 0.82 | 50.96 s |
| RTX 6000 Ada | 48 | US-KS-2 / US-WA-1 | 0.84 | 48.71 s |
| A100 PCIe | 80 | **CA-MTL-3** and US-KS-2 | 1.39 | 12.08 s |

Put to the operator with those numbers **before the volume was created**, because a volume starts a
rent only the operator can stop and the datacenter is the ruling's to name. The answer was
**CA-MTL-3, as ruled** — and the counter-argument is in the table's own blind spot: those three
cheap rows are all **48 GB, and 48 GB has never been measured at `max_seq_len` 3 072**, while 32 GB
refused this line twice. The A100 is dear and has headroom; the A6000 is cheap and unproven.

**Stock flickers on a minutes timescale.** Three read-only readings of `A100 PCIe` inside 17 minutes
returned three different availability rows; US-KS-2 read `none`, then `Low`. The
volume-capability half — the create endpoint's own refusal — did not move across any reading. Only
the create binds. A second migration is no longer a free option either: it would need a third
volume.

## What it costs from here

The project now rents **two** 100 GB volumes — `mp-srv2` (EU-RO-1, the serving stack, untouched by
this step) and `mp-lora-c` — at **~$0.47/day**, about **21 days** of what cycle 2 has left
($9.9930 of $20.00 at the team lead's 2026-08-26 reading). `mp-lora-c` is deleted when the line
closes, on the operator's word.

## What `lora-c-run r3` inherits

The volume is warm: `hf/` 59 GiB at the pinned revision, `venv/` 1.8 GiB, `repo/` 146 MB carrying
the three packs and both SFT files. **No re-download is needed — but «warm» has a path dependency.**
`pip install -e '.[dev,gpu]'` ran from `/workspace/repo`, so the editable install resolves imports
through that exact directory and the checkout there goes stale with every commit. r3 clones the
fresh bundle **over that same path** (seconds, the venv stays valid) or rebuilds the venv, which is
only correct if the dependency set moved and now has a price: 132 s. A clone to a different
directory does not bring the venv with it. See [[a_warm_environment_is_bound_to_a_path]].

Next: the 6-step smoke on the A100 buys this line's **first real s/step at 3 072**, and the cap for
the package follows the operator's word on those numbers (fixed ≈$3.1, fork $6.5–8). Related:
[[lora-c-the-card-cannot-train-at-3072]].
