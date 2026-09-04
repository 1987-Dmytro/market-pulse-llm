# PROGRESS — promo-pulse-1 (executor's one file: done / next / open stop, ≤60 lines)

Ruling 03.09 (e) made this file the phase's state; §8 of the phase file stays the DONE list.

## The money, live
`results/promo_dev_loop_run.json :: spent_all_segments_usd` = **$0.5254** of the step's $2.50 —
$0.089622 for the two pods a probe's dead-man killed, $0.435778 for iteration 1. **$1.9746 left.**
Cycle 3: $4.0631 of $7.00, REMAINING $2.9369; holdout $0.30 untouched. **This session spent $0** — no pod.

## Done
- **2026-09-03 s9 — ITERATION 1 RAN WHOLE** (pod `0z95ve2n570f0t`, 2 120 s, $0.4358): 56/56 units,
  signal 0.8792 HOLDS 0.75, subject 111/140 = 0.7929 against 0.80. Files:
  `results/promo_dev40_predicted_iter1.jsonl` · `grade_promo_dev40_iter1.json` · `…errors_iter1.json`.
- **2026-09-04 s10 — ruling (f) committed** (`7675946`) + s9's knowledge (`5fcecad`); the stop came
  before any edit, and ruling **(g)** answered it with option (b) (`5d6aecf`).
- **2026-09-04 s11 — A(1) BUILT** (`c7a63a7`, $0). `config/channel_admins.yaml` is a NEW file, the
  registry untouched: each prefix the codebook names resolves to exactly ONE `sender_anon_id`, in
  exactly one channel, across all of `data/raw/comments/` (VARUS `2fa2b73f…`, msuaaaa `58805a36…`).
  `promo_prompts.admin_ids` is its only reader; the marker is the ID, so a `null` sender matches
  nothing; wordless comments leave the render. The flag rides IN the pack (`comments` entries are now
  `[msg_id, text, sender_anon_id]`), since the pod re-renders from those rows and nothing else; the
  pod names the columns, so an older pack of pairs still renders.
  **Checks, all shown in the transcript.** Over the 40 dev threads: dropped wordless lines **68** =
  the draw's own summed `n_wordless` **68**; `[admin] ` markers **23** = admin comments WITH text
  **23** (= 82 − 59). `@VARUS_channel:9999` printed before/after: it gains `[19483] [admin] Розуміємо
  вас…` and loses the blank `[19485]`. The pod's own checker accepts **56/56** on the rebuilt pack and
  REFUSES at `@VARUS_channel:2537` when the admins file diverges — the unpinned config is covered by
  the per-unit sha, demonstrated not asserted. Against the pack iteration 1 was rendered from: leg B's
  16 shas unmoved, leg A's `(msg_id, text)` identical, 26 of 40 renders moved — the live store grew
  nothing into the rebuild. `promo_dev40_prep.json` still hashes the pinned `7971ed66…`, and the drop
  can move no denominator: `promo_hooks.screen` has no caller outside `tests/`.
  **`make check` 4 313 passed, 2 skipped, exit 0** (681.84 s) — the same count as the previous HEAD.
  `git status --porcelain src tests scripts config results docs/plans docs/reports` prints nothing.

## Next
A(2) `promo_key` chain canonicalisation via the registry's names/aliases (grader + `aggregates`);
then A(3) the template's ≤12-line worked-examples block, A(4) the $0 v1.1 reading into
`results/promo_dev40_errors_iter1_v1.1.json`, A(5) the stub tests of A's code.

## Open stop — none. A(1) is committed, the tree is clean, `make check` green at `c7a63a7`.

## Needs named, not built (the standing prompt forbids adding what the phase did not ask for)
- **`build_pack` still writes `"iteration": 1`** and the pack it now writes is the v1.1-marker one.
  A(3) moves the render again, so the pack is rebuilt a third time; the literal belongs to the (g)3
  re-emission, not to A(1), and changing it now would be scope this session does not have.
- **The dev-loop registration's pinned gold and codebook MOVED** under the lead's own v1.1 commit
  `7675946`: `prereg_promo_dev_loop.json` pins `302113b8…`/`6a74bc81…`, HEAD is `2303ea43…`/`23610346…`.
  `committed_registration()` only checks the prereg is tracked and unmodified — nothing re-verifies
  `pinned_inputs`, so both pass SILENTLY. (g)3 re-emits the record for B; the debt is that check.
- **`check_law` compares `codebook_version` only**, and A(1) did not move `CODEBOOK`: a v1.1-marker
  checkout hashes as iteration 1's law did. Only (g)3's `template_sha256` separates the two
  instruments in a record; until then the per-unit `rendering_sha256` is the whole guard.
- **Coverage is not «every collected channel».** @kopiyochka1 has such an account too and is NOT in
  the new file: outside dev-40, outside the ruling, two handles for one id (per-source vs
  per-channel undecided). 28 VARUS comments carry `sender_anon_id: null` → recall 874/902 (96.9 %).
- **`--score --iteration 1` rewrites `results/promo_dev40_errors_iter1.json` in place** — A(4) needs
  the out-path (g)4 names. The runbook's `--out` is still iteration-1-specific: a B run under that
  name overwrites the committed iteration-1 raw replies.
- Report-only drift: `gates.terminate_after_minutes` (90) is voided by ruling (d) and still printed at
  every rung-1 GO; `rung_0.dear_usd` prices 279 s where the gate allows 560; `--go-deadline` unpriced.
