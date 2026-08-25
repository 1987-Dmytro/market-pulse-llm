# lora-c-migrate r2 — the volume is built and the model loads from it

**Verdict: the deliverable is bought, and rung 5 KILLed on its own rule.** A 100 GB network volume
`mp-lora-c` (`soymlju8q0`) exists in **CA-MTL-3**; it holds this line's weights at the pinned
revision `842da379…`; and an **A100 PCIe 80 GB** pod there loaded them to GPU through the shipped
loader in **40.22 s at 17.046 GiB of 79.138**. **$0.287267 of the $1.50 cap**, 744 s by the pod's
own clock. Nothing was trained, nothing was evaluated, the r2 attempt is UNSPENT, and `mp-srv2` was
never touched.

Rung 5 refused anyway, and the refusal is recorded as its own: it asks whether `du -sb
/workspace/hf` moved across the load, and it moved — **by 40 bytes**, all of it HuggingFace
bookkeeping. The rule was registered before the reading and is not edited after it. §3 has the
enumeration.

| commit | what |
|---|---|
| `ada5848` | `docs/PROMPT-lora-c-migrate-r2.md` and `docs/STATUS.md`, verbatim |
| `8d3727e` | the previous session's vault tail, so the baseline reads a clean tree |
| `81069b5` | step 0.5 — the sealed report's checker selected the LEDGER's last row |
| `e837892` | D1 — the registration, the eight rungs, the load-proof runner, 57 tests |
| `96c8fa3` | D1 amended while DRAFT — the staging is one scp of 13.9 MB, before the venv |
| `4475907` | every command of the paid session, driven at $0 |
| `997a2a2` | the step ledger anchored at $13.02, before the volume |
| `a004ba6` | D2 — the paid step's artifacts |
| *(this)* | `docs/reports/lora-c-migrate-r2.md` and its checker |

---

## 1. The gates, each on a reading

Meter starts at `pod create` **2026-08-25T19:54:36Z** and stops at `pod delete` **20:07:00Z**.

| rung | what | reading | bound | verdict |
|---|---|---|---|---|
| 0 | price and card, by equality | `costPerHr` **1.39**, `A100 PCIe` | ≤$1.50/h, card `A100 PCIe` | **GO** |
| 6 | the platform backstop | given `20:54:35Z`, computed `20:54:36Z` | 3 600 s, overshoot ≤60 s | **GO** |
| 1 | the ssh dead-man | **35.3 s** | 500 s | **GO** |
| 3 | the venv build | **132.0 s** | 900 s | **GO** |
| 4 | the download, on BYTES | **62 580 183 517 B** in ~**184 s**, 7 polls | 1 200 s, floor 59 055 800 320 B | **GO** |
| 5 | the load proof | **40.22 s**, and `du` moved 40 B | 600 s, and the volume unmoved | **KILL** |
| 7 | never two pods | 1 pod, opened and closed | 1 | **GO** |

Rung 2's silence clock is what rung 4 measures against; it has one home and rung 4 reads it there.
The quietest the download ever got was **136.5 s** of 600, and the reading has **no blind window** —
the seven polls sit inside the registered 120 s cadence end to end.

Every one of those commands was driven as a COMMAND at $0 before the meter started (`4475907`):
`--pre-create-check`, `--open`, `--gate0`, `--venv`, `--download`, `--liveness`, `--load-proof`,
`--close-pod`, plus the two refusals — rung 7 blocking a second create, and a rung-0 KILL that still
records the pod.

## 2. The two readings this step exists to buy

**The venv — the first measurement of this stage this repo owns: 132.0 s.** No reading of it existed
before; the nearest thing was a 37-minute envelope containing the venv, a 62 GB download and two
other stages. The registered bound was 900 s and it is 6.8× the measurement. The venv's own
interpreter named the stack and the card, which is what makes it a reading rather than a caller's
claim:

```
2.8.0+cu128 5.15.1 0.50.1 NVIDIA A100 80GB PCIe
```

**The load proof — 40.22 s, 17.046 GiB allocated of 79.138 GiB, NVIDIA A100 80GB PCIe.** The
shipped `market_pulse.local_llm.load` was CALLED, at revision `842da3794eaa0b77d5f08bae87a17459d91ff475`,
and the snapshot directory on the volume is that revision's. The model occupies **21.5%** of this
card; the 32 GB that refused this line twice is smaller than this card's spare room.

**The download, and what it says about the bound.** 62 580 183 517 bytes — **58.28 GiB / 62.58 GB**
— landed in ~184 s of wall clock, **340.1 MB/s**; `hf download`'s own clock says `02:32`, i.e.
**411.7 MB/s**. 12 blobs, **0 incomplete**. The contract justified its 1 200 s bound with a 240 s
measurement taken on a volume-LESS pod's container disk in US-TX-1; the reading that matches this
transport is `implementation-notes.md`:340 — 62 GB onto a 100 GB network volume in CA-MTL-3, ~180 s
— and it is the one this step reproduced, to within 4 s.

## 3. Why rung 5 KILLed, enumerated rather than argued

`du -sb /workspace/hf` read **62 580 183 517** before the load and **62 580 183 557** after. Rung 5
registers that any movement means something was fetched, so it refused. Enumerated on the pod
before the delete (`results/lora_c_migrate_r2_load_bytes.json`), the load wrote **five files
totalling 40 bytes**:

| bytes | path | what |
|---|---|---|
| 40 | `…/refs/main` | the revision sha, written as a ref |
| 0 | `…/.no_exist/842da379…/added_tokens.json` | an absence marker |
| 0 | `…/.no_exist/842da379…/adapter_config.json` | an absence marker |
| 0 | `…/.no_exist/842da379…/model.safetensors` | an absence marker |
| 0 | `…/.no_exist/842da379…/special_tokens_map.json` | an absence marker |

**Blobs written after the download finished: 0**, of 12 blobs totalling 62 578 686 256 bytes. So the
load read 62.58 GB off the volume and fetched none of it.

The defect is in the rung, not in the load. A HuggingFace cache is not immutable under a read: the
loader records the ref it resolved and marks the optional files this repo does not ship. The
invariant worth registering is that **no blob grows** — the blobs are the weights, and they are what
a re-download would touch. Under that invariant the reading is **GO**. The rule stays as registered
and the remedy belongs to the next contract: a threshold changed after the reading it fired on is
not a threshold.

## 4. Money, by the pod's clock

| | |
|---|---|
| pod `khixo68oxnls38`, A100 PCIe, CA-MTL-3 | 744 s × $1.39/h = **$0.287267** |
| cap | $1.50 all-in — **$1.212733 left**, 19.2% used |
| what the four stages used of what they were allowed | 391.52 s of 3 200 s = **12.2%** |
| the pod against its hard stop | 744 s of 3 600 = **20.7%** |
| guard reading at the close (balance delta, a LOWER bound) | step $0.2453 · cycle 2 **$9.7306 of $20.00**, $10.2694 left |

**Beside the step, not inside it: the second volume.** 100 GB at ~$0.07/GB/month is **~$0.2333/day**,
and the project now rents two — **~$0.4667/day**, about **22.0 days** of what cycle 2 has left. It
starts now and it stops only when someone deletes the volume.

## 5. The closing state, read and not assumed

```
pods:        []
serverless:  []
volumes:     mp-srv2    qw4nwleanc  100 GB  EU-RO-1     <- untouched, the serving stack
             mp-lora-c  soymlju8q0  100 GB  CA-MTL-3    <- built by this step
```

On `mp-lora-c`: `hf/` 59 GiB at the pinned revision, `venv/` 1.8 GiB with the stack above, `repo/`
146 MB checked out at `997a2a23db7978d32e50675d29306f10e0a1d098` — carrying the three packs and both
SFT files, byte-identical to this Mac's.

## 6. What the free readings said that the ruling could not have known

Ruling (с) was written on the 18:01:18Z stock table, in which the A6000 at $0.53 was in stock in **no**
volume-capable datacenter. The issue-time reading at **19:48:13Z** — 107 minutes later, 21 capable
datacenters, 137 pairs cross-checked, 0 disagreements — holds **four cheaper volume-capable rows at
≥48 GB**, three of them in **US-KS-2**, which also carries the ruling's own A100 at the same $1.39:

| card | VRAM | datacenter | $/h | what the r2 remainder buys per step |
|---|---|---|---|---|
| RTX A6000 | 48 | US-KS-2 | 0.53 | **102.84 s** — the only row above lora-b's measured 61.047 |
| L40 | 48 | US-KS-2 | 0.82 | 50.96 s |
| RTX 6000 Ada | 48 | US-KS-2 / US-WA-1 | 0.84 | 48.71 s |
| A100 PCIe | 80 | **CA-MTL-3** and US-KS-2 | 1.39 | 12.08 s |

Put to the operator before the volume was created, with those numbers; the answer was **CA-MTL-3, as
ruled**, and that is what was built. Recorded here because the table moves: three readings of the
A100 inside 17 minutes returned three different availability rows, and 48 GB has never been measured
at `max_seq_len` 3 072 — the $0.53 row is cheap and unproven, the A100 is dear and has headroom.

## 7. The two guard `--close` debts

| step | outcome |
|---|---|
| `lora-c` (r2) | **CLOSED** before this session, 2026-08-25T17:59:54Z — $0.764952 settled against $0.7338 recorded. Not re-run: the step was already done |
| `lora-c-vramprobe` | **REFUSED AGAIN**, structurally. $0.075729 settled against $0.0495 recorded — **53.0%** off a 7% band. Nothing written, the ledger stays OPEN |

The contract's step 0.5 says the walk «has had a day». It had **five hours and six minutes**, and the
retry returned the same two figures to the cent — so the refusal is not a settlement delay. Both of
this line's records lag settlement by about the same **absolute** amount, $0.031152 and $0.026229,
which is 4.2% of a $0.76 step and 53.0% of a $0.075 one. At a 7% band no step cheaper than about
$0.37–0.45 can close however correct it is. n = 2, and the band is not this contract's to move.

## 8. The numeric audit

| claim | reading |
|---|---|
| optimizer steps | **0** |
| eval calls, scored replies, adapters | **0 · 0 · 0** |
| the r2 attempt | **UNSPENT** |
| `results/prereg_lora_c.json` | `4d5a8f1d34765b4a…` — asserted at every gate, unmoved |
| `mp-srv2` | listed before and after, not mounted, not written, not deleted |
| pods alive at any moment | **1** |
| `make fmt` | not run; both drifted files still pinned |
| suite, baseline | **3 843 passed / 2 skipped**, `make check-stamped` «reading HOLDS» at `8d3727e` |
| suite, closing | *(below)* |

| file | sha256 (first 16) |
|---|---|
| `results/prereg_lora_c_migrate_r2.json` | `f8bb64fcffa494f4` |
| `results/lora_c_migrate_r2_stock.json` | `d5f35d3b5de32a6f` |
| `results/lora_c_migrate_r2.json` | `c1089128b9150cd8` |
| `results/lora_c_migrate_r2_load_proof.json` | `272c40a54b60d6eb` |
| `results/lora_c_migrate_r2_load_bytes.json` | `9b2f2c439aa9b0f5` |
| `scripts/gate_lora_c_migrate_r2.py` | `046d7563f7654e0f` |
| `scripts/load_proof_pod_runner.py` | `5e16d44695b7fb88` |
| `tests/test_lora_c_migrate_r2.py` | `7b8fe3d2335ab318` |

---

## Deviations — from Dv829, enum v2

| Dv | cause | what |
|---|---|---|
| **829** | verify-gap | **the sealed migrate report's checker read a LIVE ledger.** It selected the r2 close as `spend_lora_c.json :: gpu_sessions[-1]` — the Dv828 class, in a second place nobody had grepped for. Run r3's first `--note` on `--step lora-c` appends a row with no `settled_usd` and that page turns red untouched. Fixed the SELECTOR by stamp, added the negative control, moved the checker's exit behind a `__main__` guard so the suite can drive it |
| **830** | contract-gap | **clause 4's stage ORDER cannot happen.** It stages the bundle, both SFT files and the three packs AFTER the load proof, inside the 90 s teardown margin. `pip install -e .` and the shipped loader both need the checkout, so the bundle has to land FIRST — and all five files are tracked, so they ride inside it. One scp of 13 931 068 bytes, before the venv; nothing after the load proof needs staging. Amended while the registration was DRAFT |
| **831** | verify-gap | **rung 5's byte-equality grades cache bookkeeping as a re-download.** It KILLed a load that fetched nothing: 40 bytes of `refs/main` and four ZERO-byte absence markers. 0 blobs written. The invariant is that no BLOB grows; the rule stays as registered and the remedy is the next contract's |
| **832** | spec-gap | **the 1 200 s download bound cites the wrong transport.** «the runbook measured 240 s for 62 GB» traces to a volume-LESS pod's 80 GB container disk in US-TX-1. The reading that matches this contract is 4a's ~180 s onto a CA-MTL-3 network volume, and this step measured 184 s. The bound holds either way; the citation would not have survived a slower transport |
| **833** | contract-gap | **§2 asks for the venv measurement «in the registration».** The registration is committed before the create and frozen by it, so a measurement cannot land there without un-dating the plan. It lands in the run record and this report; the gate says so in its own output |
| **834** | verify-gap | **the affordability inequality cannot fire at this cap.** `cap / stop × 3600` is exactly $1.50, which IS rung 0's ceiling, so no price rung 0 admits can fail it. Registered in the general form, said out loud in the record rather than presented as a second guard, and driven to its refusing branch on a synthetic pair |
| **835** | tooling | **stock flickers on a minutes timescale.** Three read-only readings of `A100 PCIe` inside 17 minutes returned three different availability rows; US-KS-2 read `none`, then `Low`. The volume-capability half — the create endpoint's own refusal — did not move across any reading. Only the create binds |
| **836** | process | **the contract says the billing walk «has had a day»; it had 5 h 06 m.** The vramprobe close was retried anyway and returned the same two figures to the cent, so the refusal is structural and not a delay |

`[cause: contract-gap 2 · verify-gap 3 · spec-gap 1 · tooling 1 · process 1]` — **eight rows**.

---

## Process signals

**The free check paid for itself twice, in opposite directions.** The previous contract's first $0
reading refuted its ruling and stopped at $0. This one's confirmed the ruling and found four cheaper
rows the ruling could not have seen — same instrument, and neither outcome was the one to hope for.

**Every gate command ran at $0 before it ran on a meter.** `main()` end to end, not just the gate
bodies: eight commands and two refusals. Nothing died on the line before the branch while the pod
billed.

**A guard that refuses correct work is still a finding, and it is not a licence to edit the guard.**
Rung 5 KILLed a load that fetched nothing. The answer was to enumerate the 40 bytes by name before
the delete, record the KILL as the rung's own, and leave the rule alone.

---

**STOP for acceptance.** The volume exists and it has been loaded from. The r3 contract — the smoke
on the A100 that buys s/step at 3 072, and the cap word that follows those numbers — is the next
team-lead session's to write, not this one's.
