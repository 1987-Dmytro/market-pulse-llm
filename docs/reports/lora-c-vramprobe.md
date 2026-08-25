# `lora-c-vramprobe` — the setting worked, the card still cannot train this line

**Verdict: OOM again. RTX PRO 4500 32 GB is CLOSED for this line.** One pod, **376 s = $0.0752 of the
$0.30 cap** on the pod clock, killed on the registered rung with the frozen registration untouched
and the attempt not spent.

The answer is the contract's second branch, and the interesting part is *how* it got there.
`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` is proven to have reached the **training
process**, not just the shell, and **it did exactly what it claims**: reserved-but-unallocated memory
fell from r2's 1.33 GiB to 544.22 MiB. The allocator then spent the reclaimed headroom and OOMed on a
**larger** request — 1.99 GiB against 1.35 GiB free — in the same `backward()` at `micro_batch` 1,
after the shipped fallback had halved the batch again. Defragmenting bought ~0.8 GiB; the deficit is
bigger than the fragmentation was.

---

## The commits

| # | commit | what |
|---|---|---|
| 1 | `eae308e` | team-lead files verbatim: `docs/STATUS.md` with ruling (п), `docs/PROMPT-lora-c-vramprobe.md` |
| 2 | `d5283e5` | the 25.08 vault checkpoint |
| 3 | `c9b0e71` | the registration and its rungs — **the HEAD the pod cloned**, committed before the create |
| 4 | `04dd942` | the spend anchor, committed before the create |
| 5 | `01e4eb5` | the paid session: the log, the env proof, the record |
| 6 | this | the report |

---

## §1 — the answer, from the pod's own log

Both lines below are grepped out of the two logs by one regular expression, never typed:

| | r2, 2026-08-24 (no setting) | this probe (`expandable_segments:True`) |
|---|---|---|
| tried to allocate | 1.72 GiB | **1.99 GiB** |
| free | 1.66 GiB | 1.35 GiB |
| this process in use | 29.70 GiB | 30.01 GiB |
| allocated by PyTorch | 28.07 GiB | **29.17 GiB** |
| **reserved but unallocated** | **1.33 GiB** | **544.22 MiB = 0.531 GiB** |
| the trainer's own halving fired | yes | yes |
| optimizer steps | 0 of 6 | **0 of 6** |

```
OOM: micro_batch -> 1, grad_accum -> 16 (effective batch held)
...
torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 1.99 GiB. GPU 0 has a total
capacity of 31.37 GiB of which 1.35 GiB is free. ... 29.17 GiB is allocated by PyTorch, and
544.22 MiB is reserved by PyTorch but unallocated. If reserved but unallocated memory is large
try setting PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True to avoid fragmentation.
```

The last sentence is the machine recommending a setting that was already on. A live `nvidia-smi`
half a minute before the failure read **31 964 of 32 623 MiB** — a session reading, not a kept
artifact, and it is quoted as one.

**The setting reached the process, and that is a reading and not a claim.** A shell that exported a
variable and a process that inherited it are two different facts, and an inline `VAR=x cmd` never
appears in the shell's own environment at all — so the proof is `/proc/<pid>/environ` of the pid
running the trainer's command line, taken while it ran and pulled back as an artifact:

```
# the TRAINING process — /proc/215/environ, read while it ran
# cmdline: /workspace/venv/bin/python -u /workspace/repo/scripts/train_qlora_v3.py
#          --class-weights --max-steps 6 --data results/pass1_sft_v3_train.jsonl
#          --out /workspace/run/smoke
# started: Tue Aug 25 14:41:42 2026
HF_HOME=/workspace/hf
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
```

**The two smokes are PAIRED, and that was proven at $0 before the create.**
`train_qlora.sampling_order` is `random.Random(seed).choices(range(n), weights, k=n)` — a pure
function of the row count, the per-row weights and the seed, all three fixed by a data file pinned
by sha. The class weights recomputed on the Mac equal the paired pod's own logged line to the last
digit, so the first micro-batch is rows **[231, 4]** on both pods. Same card, same datacenter, same
image, same trainer bytes, same two rows in the same `backward()`. The environment variable is the
only thing that differed.

---

## §2 — the session, rung by rung

Every row is `results/lora_c_vramprobe.json::gates`, written by `scripts/gate_lora_c_vramprobe.py`
when it fired.

| at (UTC) | rung | verdict | reading |
|---|---|---|---|
| 14:40:19 | 0 — price and card | **GO** | `costPerHr 0.72`, card `RTX PRO 4500` — both registered; the hard stop re-solved to 1 500.0 s at the observed price, drift 0.0 |
| 14:40:34 | 1 — boot gate | WAIT | 21.1 s of the 500 s deadline |
| 14:40:42 | 1 — boot gate | **GO** | ssh answered at **29.4 s** |
| 14:45:25 | 3 — the smoke | WAIT | 223.8 s in; step-5 line due by 1 150.8 s; env var proven reached |
| 14:46:16 | 3 — the smoke | **KILL** | `torch.OutOfMemoryError` read out of the log, 0 loss lines |
| 14:46:41 | close-pod | GO | 376 s, $0.0752 |

**Rung 2, liveness, was never reached** and is reported as not-reached rather than as a passing
reading. The trainer was last seen alive **207 s** into the smoke (`ps -o etime` at `14:45:09Z`)
and was gone by **239 s** (`14:45:41Z`); the exact death is bounded and not known, and either
end of that bound is far inside a 600 s silence deadline.

The platform backstop was given `2026-08-25T15:05:13Z` against a create at `14:40:13Z` — exactly the
1 500 s the cap allows, and 1 124 s of it went unused.

---

## §3 — what binds, computed and not assumed

The contract registers **two** bounds on one run — «smoke ceiling 6 × 181.5 s + load 300 s» = 1 389 s
from the smoke's start, and a 1 500 s hard stop from the create — and does not say which one is the
rule. They are solved against each other in the registration rather than left to the moment:

> affordable s/step = (hard stop − smoke start − teardown margin − load allowance) / steps
> = (1 500 − s − 90 − 300) / 6 = (1 110 − s) / 6

which equals the registered 181.5 only at **s = 21.0 s**. This pod's smoke started **89.0 s** after
the create, so the binding rate was **170.17 s/step** and the registered 181.5 ceiling could never
have fired. No real pod boots, stages a 14 MB bundle and launches a trainer inside 21 s, so this is
not a property of today's pod — the CAP is the rung, always.

Two more numbers the rung had to get right before it could be trusted, both found at $0:

- **`config/qlora.yaml` sets `log_every: 5`**, and `train_qlora.train` writes a loss line when
  `step % log_every == 0 or step == total`. At `--max-steps 6` that is **two** lines, at steps 5 and
  6 — not six. `scripts/gate_lora_c.py::smoke_gate` waits for six and would have WAITed for ever on
  a surviving smoke; r2 never saw it because its `--oom` flag short-circuited the count.
- **the step-6 line's `seconds_per_step` is not a rate.** It is `(t6 − t5) / log_every` — one step's
  time divided by five. Only the step-5 line is a true five-step average, and the number this line
  may report is `<out>/provenance.json::run.seconds_per_step`, the whole loop's wall time over its
  steps. The two are printed side by side and never averaged.

Neither mattered today — zero loss lines were written — and both are registered because a surviving
smoke is the branch that needed them.

---

## §4 — the money

| reading | value | what it is |
|---|---|---|
| pod lifetime | `14:40:13Z` → `14:46:29Z` = **376 s** | create to delete, the only clock that bills |
| at $0.72/h | **$0.0752** | the conservative charge, and the one this report uses |
| guard balance delta | $0.0495 | a **LOWER BOUND** — the billing walk had posted no rows yet |
| step cap | $0.30 | **$0.2248 left**, unspent |
| cycle 2 | $9.4105 of $20.00 | $10.5895 remaining |

The delta being smaller than the pod clock is the walk lagging, exactly as in r2 ($0.0602 against
$0.7606). `--close` on this step is a debt for the next session, beside r2's.

**Nothing else was created.** One pod, no serverless, no second volume. The volume `mp-srv2` rents
beside this probe at ~$0.24/day and is never inside it.

**Nothing was kept.** The trainer OOMed before `save`, so `/workspace/run/smoke/` held no adapter;
the empty directory was removed and proven empty by `ls` before the delete. The two files the pull
was written to expect on a surviving run — `loss.jsonl` and `provenance.json` — do not exist, which
is the OOM path's own signature and not a transport failure. The three files that do exist were
hashed on the pod and again on the Mac, and the hashes are equal.

Deletion proven by three listings at `14:46:34Z`: pods `[]`, serverless `[]`, and the volume
`mp-srv2` still there as the positive control that the listing works at all.

---

## §5 — what the operator is being asked

**The card is closed and the datacenter question is now the whole question.** Two $0 readings taken
before the create, both dated `2026-08-25T14:10Z`:

| EU-RO-1 — the volume's own datacenter | stock |
|---|---|
| RTX PRO 4500 32 GB | Medium — and it cannot train this line |
| RTX A6000 48 GB | **empty** (third reading running) |
| RTX PRO 6000 96 GB | empty |
| RTX 4090 24 GB | empty — **the r2 contract's pre-authorised fallback is out of stock too** |

There is **no 48 GB card in EU-RO-1 today at any price.** Where they are:

| card | VRAM | $/h secure | in stock |
|---|---|---|---|
| RTX A6000 | 48 GB | **$0.53** | EU-SE-1 (Sweden), US-TX-1 — both `Low` |
| RTX PRO 6000 MIG 2g.48gb | 48 GB | $1.09 | EUR-IS-2 (Iceland), US-PA-1 — both `Low` |
| RTX PRO 6000 Server Edition | 96 GB | $2.09 | several — ruling (п) already declared it non-fitting |

A different datacenter means a **different network volume**: 59 GB of weights to download again, a
second ~$0.24/day rent, and neither is priced by any registration this line holds.

**And there is a second constraint that does not care which card is chosen.** What is left of the
r2 cap is $3.2394 = **16 197 s** at $0.72/h. An r3 that trains both arms owes, at ruling (п)'s
charged rates: boot 500 + load 300 + 396 adapter-eval calls × **9.20** = 3 643.2 + pass 2 2 134 =
**6 577.2 s** fixed, leaving 9 619.8 s for 150 optimizer steps (144 + a re-run smoke):

> **r3 fits the remaining cap only at ≤ 64.13 s/step** — 66.80 if the smoke is not re-bought.

lora-b measured **61.047 s/step** on a 48 GB A6000 (`results/baselines.json`) with rows of at most
**1 222** tokens (`results/prereg_lora_b.json::longest_kept`). This line's rows run to **2 975**
(`results/lora_c_encode_census.json::tokens.max`). So the remaining cap is very probably not enough even on a card that fits, and
raising the cap or shrinking the plan is a decision this session does not own.

---

## §6 — the numeric session audit

| | |
|---|---|
| pods created | 1 (`cs8vla37upmy42`) · deleted 1 · serverless 0 · volumes created 0 |
| pod lifetime | 376 s · $0.0752 at $0.72/h |
| optimizer steps | **0 of 6** |
| loss lines | **0** (two were expected, at steps 5 and 6) |
| adapters produced | **0** — the trainer OOMed before `save` |
| eval replies | **0** — the attempt is NOT SPENT |
| bars scored | **0** — `results/prereg_lora_c.json` is FROZEN and untouched, sha `4d5a8f1d34765b4a` unchanged |
| artifacts pulled before the delete | 3 files, hashes equal on both machines |
| suite | **3 805 passed / 2 skipped**, `make check-stamped` «reading HOLDS» at `c9b0e71`, before the create |

| file | sha256 (first 16) |
|---|---|
| `results/prereg_lora_c_vramprobe.json` | `4d57e40a234eb684` |
| `results/lora_c_vramprobe.json` | `8a5d25c17ac75103` |
| `results/lora_c_vramprobe_smoke.log` | `a23085c2792b5549` |
| `results/lora_c_vramprobe_environ.txt` | `032a002f248e3bd2` |
| `results/spend_lora_c_vramprobe.json` | `5103b8745985f87a` |
| `scripts/gate_lora_c_vramprobe.py` | `c3341d36e7f8c9f9` |
| `tests/test_lora_c_vramprobe.py` | `d4a303b279cd3f82` |

---

## Deviations — from Dv812, enum v2

| Dv | cause | what |
|---|---|---|
| **812** | contract-gap | the contract registers two bounds on one run — 6 × 181.5 s + 300 s from the smoke's start, and 1 500 s from the create — and names neither as the rule. Solved against each other before the money: they cross at a smoke starting 21.0 s after create, so the cap binds on every reachable pod. This one's bound at 170.17 s/step |
| **813** | verify-gap | `log_every: 5` makes `--max-steps 6` write TWO loss lines, not six. `gate_lora_c.smoke_gate` waits for six and would have WAITed for ever on a surviving smoke; the defect never showed because r2's `--oom` flag short-circuits the count |
| **814** | verify-gap | the step-6 loss line's `seconds_per_step` is one step's time over five, not a rate. Registered so the reported number is the whole loop's and the two are never averaged |
| **815** | tooling | `$!` after `VAR=x nohup cmd &` inside `bash -c` recorded the WRAPPER's pid, and `pgrep -f train_qlora_v3.py` matched the same wrapper because its command line contains the script's name. The env proof came back EMPTY — which reads exactly like «the setting is not set», the one false negative that would have destroyed this probe's answer. Fixed by walking `ps -eo pid,ppid` to the real trainer |
| **816** | process | `nohup … &` inside an `ssh` one-liner without `< /dev/null` held the ssh channel open; the call timed out at 120 s while the trainer ran on correctly. Two blind minutes, no extra pod seconds |
| **817** | tooling | zsh does not word-split an unquoted `$SSHOPT`; the first `scp` died with «Identity file … not accessible». `scripts/runbook_lora_c.md` names this defect by name and the shortcut was taken anyway. ~11 s of pod time |
| **818** | process | rung 2 (liveness) was never reached — the run died between 207 s and 239 s into the smoke, never near a 600 s silence. Reported as not-reached, never as a passing reading, and the death itself is reported as a BOUND because no artifact stamps it |

`contract-gap 1 · verify-gap 2 · tooling 2 · process 2` — seven, against seven rows.

---

## Process signals

- **`make fmt` would void a FROZEN record's producer pin.** `scripts/write_lora_c_prereg.py` is
  pinned at `a4eb2893…` by `results/prereg_lora_c.json::producer`; `ruff format` moves it to
  `6807d264…`. Two files are formatter-drifted in the tree today and both were left alone. `make
  check` runs `ruff check`, not `ruff format --check`, so it can see neither fact.
- **The cheapest step was the most fragile.** The whole probe reduces to one boolean — did the
  variable reach the process — and two plausible-looking commands answered it wrongly before the
  third answered it right. r2 was the negative control that made the answer legible at all.
- **The answer cost $0.0752 and arrived inside four minutes of the smoke.** The 1 500 s hard stop was never approached and
  1 124 s of it went unused: the binding constraint was the physics, not the clock or the cap.
