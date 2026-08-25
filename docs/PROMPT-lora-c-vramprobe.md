# PROMPT — `lora-c-vramprobe` (fresh session, ONE tiny paid probe, cap $0.30, Dv from 812)

One question, one pod, minutes: **does `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` let
RTX PRO 4500 32 GB survive the 6-step smoke of arm A's config at `max_seq_len` 3 072?** The r2
session OOMed by 1.72 GiB with 1.33 GiB sitting reserved-but-unallocated
(`docs/reports/lora-c-run-r2.md` §3) — the error message itself names this setting. It is a
GUESS until a pod measures it; this probe is that measurement.

Rules:

- **This is NOT the registered attempt.** `results/prereg_lora_c.json` is FROZEN and is not
  touched. The probe writes its own micro-record `results/lora_c_vramprobe.json` (question,
  card, env, verdict, seconds, spend by the pod clock) — the same shape prior probes used.
  No eval leg, no bar, no adapter kept: the smoke's output adapter is discarded ON the pod.
- One pod `RTX PRO 4500` at ≤$0.80/h in EU-RO-1 (rung 0 grades card AND price by equality);
  `expandable_segments:True` set in the env before the trainer starts; the smoke = 6 optimizer
  steps of arm A via `scripts/train_qlora_v3.py` exactly as r2 ran it. Kill-clock: boot 500 s;
  smoke ceiling 6 × 181.5 s + load 300 s; liveness 600 s from the last log line; hard stop
  1 500 s (`--terminate-after` at create). Cap $0.30 all-in — a probe that threatens it is
  KILLED, not finished.
- **Both outcomes are answers.** SURVIVES → record the measured s/step at 3 072 (the number
  every derivation has been missing) and the peak memory if the trainer logs it. OOMs AGAIN →
  record the traceback tail; the card is closed for this line and the datacenter question goes
  back to the operator. Either way: pull the record, delete the pod, prove deletion by listing
  (volume `mp-srv2` as the positive control), commit, short report
  `docs/reports/lora-c-vramprobe.md` (one page: the verdict, the gates table, the money from
  the pod clock, Deviations from Dv812 on enum v2, three-line Process signals). STOP.
- **DO NOT:** touch the frozen registration, the packs, the bars, or any team-lead file (commit
  only); train past 6 steps; keep the adapter; run any eval; create a second billing resource;
  leave the pod unpolled past the liveness deadline.

Context to read first: `docs/reports/lora-c-run-r2.md` §2 (the rungs), §3 (the OOM), and
`docs/STATUS.md` п. 1 (п). `make check-stamped` for any suite reading.
