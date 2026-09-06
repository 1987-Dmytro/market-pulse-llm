# PROGRESS — promo-pulse-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines; §8 of the phase file stays the DONE list)

## ⚠️ IN FLIGHT — a pod is LIVE and the line `promo-iter5` is OPEN (s31, 06.09)
Pod **`xt4c5osyr36ew0`** `mp-promo-iter5`, NVIDIA RTX PRO 4500 Blackwell, **$0.72/h**, EU-RO-1,
created **2026-09-06T11:20:39Z**, `--terminate-after` **13:16:14Z** (6960 s = the registered 116 min).
Line anchored **11:06:19Z**, `results/spend_promo_iter5.json`, cap **$1.40**, rung 0 FITS at the mean
**$0.8470**. GO written 11:31:47Z. **If this session died here: delete the pod, `--close-segment`,
take the POST-RUN `--note`, then `--close --expect-ms --until --tolerance 0.05` (§6 of the runbook).**

## The money, live — read at 11:06Z and 11:20Z of THIS session
Cycle 3 **SPENT $6.4438, REMAINING $2.5562** of $9.00 (fresh; s28's $2.7506 is superseded).
`PROMO-ITER5 SPENT $0.0000 of $1.40` at the anchor. `promo-iter4` CLOSED $0.694815/$1.20,
`promo-holdout` CLOSED $0.298209/$1.10. `promo-dev-loop` refuses and is never named again.

## Done — 06.09 s31 (this session), §0a and §0–§5 of `scripts/runbook_promo_dev_1.md`
- **Start ritual:** team-lead files committed by path (`fd08517`), knowledge by path (`c17dbe5`).
- **§0a, the line's opening.** `--dry-run` ($0) → the listing read READ-ONLY first (`runpodctl gpu
  list`, $0, creates nothing) so a card that had moved would refuse BEFORE the anchor, not after it:
  RTX PRO 4500, 32 GB, `NVIDIA RTX PRO 4500 Blackwell`, $0.72/h secure, stock **High** — the record's
  own card. → `--register --part dev --step promo-iter5 --cap 1.40`: **FITS at the mean $0.8470
  (−39.5 %)**, priced $0.9028, dear $4.8633 (over the cap, named, not hidden), hard stop 7000 s.
  Record verified BEFORE the commit: `cap_usd` 1.4 · `terminate_after_minutes` **116** ·
  `rung_0.price.card` the Blackwell · phase «iteration 5». **Commit 1 = the registration**
  (`d598573`), **commit 2 = the pack** (`782bb7f`) — `build_pack()` passed `committed_registration()`
  exactly because the registration was committed first (s30's fix, proven in the live run).
- **`make check` at HEAD `782bb7f`:** `ruff` clean · SLICES COVER THE LIST · **1000 + 2030 + 1293 =
  4323 passed, 2 skipped** · **FLOOR HOLDS** (≥ 4266, §8 (j)). Tree clean.
- **§0:** `pod list -a` and `serverless list` both `[]` · listing re-read, card unmoved ·
  the session's ONE ledger line taken pre-pod: «promo-iter5, iteration 5 — pod about to be created».
- **§1:** `STOP_AT` computed from the record (cap $1.40 vs REMAINING $2.5562 → 116 min binds) ·
  gpu-id READ from the record, never typed · create → `costPerHr` **0.72**, machine RTX PRO 4500, RO ·
  `--open` **rung 1 GO**: price and card both the registered ones, backstop $1.392 ≤ cap.
- **§2:** dead-man 500 s READ from `gates.ssh_deadman_seconds`; the port answered at **27 s**.
- **§3:** bundle from `782bb7f`; the pod's clone `git rev-parse HEAD` equals it and `git status
  --short` is empty; volume warm (59 G of weights); `/workspace/run` emptied and shown empty.
- **§4:** detached (`setsid nohup`) with `HF_HOME`, `PYTHONPATH` and
  `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`. The ssh wrapper held its channel open — the
  PROCESS was the signal, not the wrapper's exit.
- **§5, the answer ruling (w) was bought for:** boot 195.8 s, then all three smoke units back —
  including **`@VARUS_channel:8647`, 14 281 chars, the render iteration 4 OOM'd on: 313.9 s, 6881
  chars, balanced, `finish stop`**. `--smoke` printed «3 REPLIES ARE IN — write GO», **exit 0**.
  GO written 11:31:47Z. The 32 GB card plus the allocator answered the serving defect.
- **Liveness, corrected twice before it was trusted:** `pgrep -f promo_dev_pod_runner.py` also matches
  the probe's own shell and the launcher wrapper, so it can never read 0 — a guard that cannot fire.
  Pinned to the runner's own PID (`[ -d /proc/184 ]`), which was proved to be that cmdline.

## Next — §6 and §7 of the runbook, in this session, at $0 once the pod is gone
Fetch the 80 units and `pod.log` → `wc -l` = 80 → **delete the pod** → prove both listings `[]` →
`--close-segment --deleted-at --billed-seconds --outcome --replies` → the **POST-RUN `--note`**
(PHASE v13 §6.1: the reference the close settles against, after the delete and before any next pod) →
`--close --tolerance 0.05 --expect-ms <filtered by anchor> --until <after this pod>` → §7
`--score --arm dev40` (the BAR, subject ≥ 0.80 / signal ≥ 0.75) and `--arm dev2` (a READING beside
it), then `grade_promo_signals.py`. GREEN → the team lead draws holdout-2 blind. RED → §2's fifth and
last dev run has closed the question red and the next word is the operator's.

## Open stop — NONE yet. The pod is live and inside its own gates.

## Named, not built (the phase file forbids adding what it did not ask for)
- **Contradiction, named per PROCESS v2.1 (the standing law wins, no stop):** the runbook takes THREE
  guard `--note`s (§0 pre-pod, §6 post-run, §6 close) while the operator's line is «one ledger line
  per session». PHASE **v13 §6.1** mandates the post-run reading and `--close` writes the settlement —
  the §0 note is the session's ledger line and the other two are the close's own machinery.
- **(y)4 risk 2 — an exception with an EMPTY message reads as ANSWERED** (`"exception" in row` +
  (w)3's test) and **risk 3 — `close_segment` sums ALL segments** against the cap (filter by
  `anchored_at`). Both remain the FIRST $0 items after iteration 5.
- **§6.5's $0 fit proof** — the smoke's longest unit stood in for it again, and this time it passed.
- **No test for the arm selector** (§4) or the step-aware guard read ((v)3 «no new test»).
**No test, pin, guard or ledger was added this session.**
