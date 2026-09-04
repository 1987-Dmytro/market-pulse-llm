# PROGRESS — promo-pulse-1 (executor's one file: done / next / open stop, ≤60 lines)

Ruling 03.09 (e) made this file the phase's state; §8 of the phase file stays the DONE list.

## The money, live
`results/promo_dev_loop_run.json :: spent_all_segments_usd` = **$0.5254** of the step's $2.50 —
$0.089622 for the two pods a probe's dead-man killed, $0.435778 for iteration 1. **$1.9746 left.**
Cycle 3: $4.0631 of $7.00, REMAINING $2.9369; holdout $0.30 untouched. Ruling (f) settles the ledger:
the step's line of record is pod-priced and `--close --tolerance` does not apply — the walk is
informational. **This session spent $0 and created nothing.**

## Done
- **2026-09-03 s9 — ITERATION 1 RAN WHOLE** (pod `0z95ve2n570f0t`, 2 120 s, $0.4358): 56/56 units,
  signal 0.8792 HOLDS 0.75, subject 111/140 = 0.7929 against 0.80. Files:
  `results/promo_dev40_predicted_iter1.jsonl` · `grade_promo_dev40_iter1.json` · `…errors_iter1.json`.
- **2026-09-04 s10 — ruling (f) committed by path** (`7675946`: codebook v1.1, gold rows 8044 / 20083
  / 407 re-labelled, STATUS, the ruling) and session 9's knowledge artifacts (`5fcecad`).
  `make check` green at that HEAD — **4 313 passed, 2 skipped, exit 0**.
- Iteration 2 session A item (1) — **NOT built**: the stop below was reached before any edit.

## Next
Item A(1) once the fork below is ruled; then A(2) `promo_key` chain canonicalisation, A(3) the
template's worked examples, A(4) the $0 v1.1 reading, A(5) the stub tests of A's code.

## Open stop — «where `admin_anon_ids` may live»
**Stop-point.** A(1) puts `admin_anon_ids` in `config/registry.yaml`, a file **21 sealed records** pin
in four sha families (counted, `results/`): r1 `d4e3b237…` 7 · pre-(13)(b) `920c7f20…` 8 ·
signed-screen `c82d0cff…` 5 (reconstructed only inside `tests/test_registry.py`) · LIVE `eff8ba5b…` 1
(`results/prereg_promo_c2.json`, put there by the 02.09 (d) addendum). `@VARUS_channel` (`:36`) and
`@msuaaaa` (`:45`) are r1-era rows OUTSIDE the r2 bracket, so ANY added line lands in every
reconstruction. Driven, not reasoned: `run_promo_c2.preflight` passes at HEAD and refuses after one
added line; `build_aggregates.py:294` reaches the C2 seal from `tests/test_export_dashboard_data.py`,
so `make check` — session A's own exit condition — goes RED. A fourth revision (`R3_MARK` +
`registry_before_r3` composed under `registry_before_r2`) restores all four families exactly, and is
still NOT enough: `run_promo_c2.py::preflight` (`:523-535`, live at `:979`) compares raw bytes, never
walks revisions, and its own writer says «If the registry moved, that is a refusal for the team lead,
not a rewrite here».
**Question.** (a) authorise revision r3 in `registry.py` AND teach `preflight` the `run_5c2.py:145-148`
walk; (b) the ids live outside the registry — no pin moves, the render/pack path is identical; or
(c) rule C2 collection closed, so only (a)'s first half is needed?
**Tree.** Clean; `make check` 4 313 passed / 2 skipped / exit 0; nothing bought; both listings `[]`.

## Needs named, not built (the standing prompt forbids adding what the phase did not ask for)
- **The dev-loop registration's pinned gold MOVED.** `prereg_promo_dev_loop.json` pins
  `docs/labels-promo-dev.jsonl` at `302113b8…` (HEAD `2303ea43…`) and the codebook at `6a74bc81…`
  (HEAD `23610346…`) — the lead's own v1.1 commit `7675946`. `committed_registration()` checks only
  that the prereg is tracked and unmodified; nothing re-verifies `pinned_inputs`, so both moved pins
  pass SILENTLY. Session B needs a ruling on which registration and which gold it is bought under.
- **59 of the 82 admin-authored comments in the 40 dev threads are WORDLESS** (23 carry text; counted).
  They ship in the pack and render as blank lines today, so a naive `[admin] ` prefix turns them into
  visible content gold never labels. The marker must fire only where the text is non-empty.
- **@kopiyochka1 is a THIRD collected channel** with comments and a channel-own account; its source
  carries two handles for that one id, so the key's shape (per-source vs per-channel) is undecided.
  Dev-40 spans only the two named channels, so this does not block session B.
- **28 VARUS comments carry `sender_anon_id: null`** and read as the channel's own account: marker
  recall on the population is 874/902 (96.9 %), not 100 %. Dev-40 itself is clean.
- **`--score --iteration 1` rewrites `results/promo_dev40_errors_iter1.json` in place**, and A(4) says
  the v1.1 reading is «printed beside the paid number, never replacing it» — A(4) needs an out-path.
- **The pod's `check_law` compares `codebook_version` only.** A render-only change leaves the law sha
  identical to iteration 1's, so no record field separates the v1 instrument from the v1.1 one
  (`extractor_version` moves per row). And `[admin]` stays UNEXPLAINED to the model until A(3) lands
  the template examples — session B must not be bought with A(1) and without A(3).
- **The runbook's `--out` is iteration-1-specific**: a session-B run under that name would overwrite
  the committed iteration-1 raw replies.
- `gates.terminate_after_minutes` (90) is voided by ruling (d) and still printed beside every rung-1
  GO; `rung_0.dear_usd` $1.3193 prices a dead segment at 279 s where the gate now allows 560;
  `--go-deadline 1800` is unpriced in rung 0 (~14 s here, worst case $0.37). Report-only.
