# PROMPT — pass1-window r2: the 901 comments still owed, priced on the POD CLASS (step 0.5 addendum $0 → D0′ $0 → D1 paid, cap $2.00 → D2 $0)

**Fresh executor session. Authority:** the operator's ruling of 2026-08-21 (evening) in
the team-lead session, registered in `docs/STATUS.md` («Открытые решения» п. 1 (е),
очередь п. 3): *re-register the remainder as `pass1-window r2`, cap **$2.00**; the
smoke of pass 2 waits for the finished window.* Read: this file →
`docs/PROMPT-pass1-window.md` (the contract; every clause not amended here stands) →
`docs/reports/pass1-window.md` §«Rung 4», §«a rate is a property of the POD», Dv647/
Dv657/Dv631 → `results/prereg_pass1_window.json` (r1, superseded, NEVER edited).
Deviations from **Dv659**, enum v2; five-line Process signals; team-lead files verbatim
(commit `docs/STATUS.md` and this file as your first commit); never `git add -A`.

## Step 0.5 — the acceptance addendum of r1 ($0, its own commits, BEFORE D0′)

The team lead's acceptance found two defects the r1 report cannot absorb. Fix them as an
**ADDENDUM section** of `docs/reports/pass1-window.md` (append-only), with the numbers
corrected in the census, the ADR and hot.md:

1. **The census's report-only readings on the 650 / 450 labelled rows are inflated by
   msg_id collisions.** `src/market_pulse/scorer.py::reader_comment_agreement` keys
   answers by `msg_id` ALONE (`answers = {int(one["msg_id"]): …}`) and
   `gate_pass1_fewshot.py::leg_table` derives `agreed_ids` as a set of msg_ids — while
   seven msg_ids inside `membership.labelled_650` live in two threads each
   (21164 · 21195 · 21209 · 21211 · 21236 · 21239 · 21256, `@VARUS_channel` ↔
   `@klopotenkofood`). Five of them have exactly one answered twin, so the unanswered
   twin inherits an answer. Team lead's pair-keyed recount, reproduced by a fresh
   refuter: **650 → answered 112 (not 117) · agreed 68 (not 69) · our_agreed 21 (not
   23); 450 → 64 / 34 (not 65 / 35)**; dev-200 (48 / 34 / 21) and the fourteen are
   unaffected. The scorer is PINNED by sealed records — do not edit it. Fix the census
   path: score per THREAD (or otherwise key on the pair) and add a test that builds a
   subset with one collision and goes RED on the old path. State in the ADDENDUM that
   **comment identity anywhere in the window is the pair (thread, msg_id)** — this
   binds `pass2-signals`.
2. **The post-kill `--pre-create-check` refusal (6 761.54 > 6 500 s; $1.4885 ≤ $1.50)
   exists only in stdout** — no gate entry, no run-record key carries it. Append it
   to `results/pass1_window_run.json` as a recorded gate (append-only, the verdict as
   the command printed it) and make `--pre-create-check` record its verdict from now
   on: a guard whose verdict lives only in a terminal is not a record.
3. Note in the census that the pod log shows a **132nd reply** (`@klopotenkofood:
   6035#21205`, 759 s) absent from the copied-back file — the concrete instance of
   Dv657's lower bound.

Commit the addendum separately (report · census+tests · vault), then D0′.

## What r2 changes — and ONLY this (state your assumptions against it)

The population, the prompt v2, the neighbours, the context, the completeness bar's
SHAPE, the kill-clock rungs by name, the fourteen-as-census-row rule — all r1's. What
moved is the PRICE and the POPULATION OWED:

1. **Owed: the 901 ids the Mac does not hold.** `results/pass1_window_r2_pack.json` =
   the r1 pack's leg MINUS the 131 ids of `results/pass1_window_v2.jsonl` (each of the
   131 verified by `rendering_sha256` against the pack before it is subtracted), same
   order, same rendering — the pack builder is a thin sibling that READS the r1 pack and
   never re-renders (a re-render would move shas the census must match). One leg,
   out-file `pass1_window_r2_v2.jsonl`.
2. **The rate is charged on the POD CLASS, at the TOP of the stack's measured spread
   (Dv647).** Base means across pods: probe-b **5.162** s/call (64 rows,
   `results/pass1_probe_b_rows.jsonl`) vs r2 **2.293** (200 rows) — a 2.25× spread the
   r1 contract ignored. v2 over base, measured on one pod: 2.726 / 2.293 = **1.189**.
   Charged: 5.162 × 1.189 = **6.14 s/call** (1.37× the 4.498 this line measured; the
   slowest single call this stack has ever measured is probe-b's 6.214). Derive it in
   H6 from those three files, never from this prose.
3. **The file on the volume is EVIDENCE, not input.** `/workspace/run/pass1_window_v2.jsonl`
   survives on `qw4nwleanc` with ≥ 132 rows. On the pod, BEFORE the run directory is
   cleared: `scp` it to `results/pass1_window_volume_tail.jsonl`, sha it on both sides,
   count its rows beyond the Mac's 131 — and do NOT merge it: its extra rows are bought
   again inside the 901 and the census names the count and the cost («N rows bought
   twice, N × measured s/call»). Merging two answers for one id is an ambiguity this
   registration does not buy. Then clear the dead pod's clocks (Dv621/632).
4. **Money re-derived (H6 block, step-1 refusal):** generation 901 × 6.14 = **5 532.14
   s**; + ssh 500 + stage/launch 150 + load 450 + overhead 1 300 = **7 932.14 s =
   2.2034 h → worst $1.7627 at $0.80/h** ($1.1678 at $0.53). **Cap $2.00**; cumulative
   hard stop **8 600 s = $1.9111 < $2.00**; session ceiling 2.00 / 0.80 = 2.5 h = 9 000 s
   ≥ hard stop. Recovery: one dead pod at rung 2 (500 s, $0.1111; with r1's measured
   deletion tail 578.5 s) + worst = 8 432.14 ≤ 8 600 ✓ and $1.8738 ≤ $2.00 ✓; widest
   dead pod 667.86 s; `re_creations_allowed: 1`, a second dead pod = STOP. **Rung 4's
   knife edge at the CHARGED spans: (8 600 − 1 300 − 1 100) / 901 = 6.88 s/call** —
   above the 6.14 charged and above 6.214, the worst call ever measured; at the
   measured pre-generation (252.5 s) it is 7.82. Publish both arms (Dv630/655). **STEP
   SUM:** r1 pod $0.173694 (clock) + r2 cap $2.00 = $2.1737 — the guard step is
   **`pass1-window-r2`**, fresh anchor, `--step-cap 2.00`; r1's ledger stays open for
   `money-anchors`.
5. **No rate rung is added.** Rung 4 re-prices the remainder on every poll at
   max(mean, last call) and kills any pod that cannot finish inside 8 600 s at the first
   poll that shows it (a 8 s/call pod dies ≈ 20 calls in, ≈ $0.10, re-creation still
   reachable) — a separate rung would be the same check twice. Say so in the record.

## D0′ — at $0, before any pod

- `scripts/build_pass1_window_r2_pack.py` (reads the r1 pack + the r1 out-file, writes
  the 901-item pack; refuses if any of the 131 fails its sha or if the remainder is not
  exactly `1 032 − 131`); `scripts/write_pass1_window_prereg_r2.py` → `results/
  prereg_pass1_window_r2.json` with `supersedes` = r1 + its sha and r1's closing state
  («closed RED at rung 7, 131 of 1 032, killed by rung 4 on the rate; recovery refused
  on seconds»); copied blocks audited pin by pin AND threshold by threshold (the r2
  sweep test for repealed numbers — Dv613's class: 6 500, 3.4075, 5 916.54, 583.46,
  1.50 must not survive as NUMBERS anywhere in r2's money block except where a
  `supersedes` field quotes them by name).
- `scripts/gate_pass1_window.py` gains `--revision r2` ONLY if that leaves r1's pinned
  bytes untouched — otherwise a sibling, and say which (Dv624's split stands). The
  runbook `scripts/runbook_pass1_window_r2.md`: r1's corrected order + the volume
  evidence step (3 above) + the r2 pack staged to the pod; pod runner unchanged,
  `--only v2`.
- Tests in BOTH directions on the fake transport: the 901-pack is exactly the
  complement; a pod at 6.9 s/call after 20 rows → rung 4 KILL with re-creation still
  allowed; a pod at 6.0 → GO to the end; recovery arithmetic at 667 s dead → allowed,
  at 669 → refused; the volume tail with 5 extra rows → counted, never merged.
- `make check` green; `make preflight ARGS='gate_pass1_window.py prereg_pass1_window_r2.json'`
  pasted; the five-lens review before the create, each survivor fixed with a mutation
  watched red; `--pre-create-check` GO pasted. Commits: addendum (step 0.5) · r2 pack
  builder + pack · producer + record + gate + tests · runbook · guard anchor · vault
  tail — ALL before the first `pod create`.

## D1 / D2

D1 as r1's runbook, with the volume evidence copied BEFORE the clear, rung 3 on
`launched_at`, `--watch` never left, scp + sha (three for three) before delete, deletion
by listing with the volume control. **D2 census over the UNION** 131 + 901 = 1 032, keyed
by the pair: the completeness bar of THIS registration (answered 901 / 901 · sha · refusals
≤ 9) AND the window's completeness (1 032 / 1 032) beside it; label distribution in three
states; the per-thread pass-2 filter table over the WHOLE window — this is what prices
`pass2-signals`; report-only readings pair-keyed (650 · 450 — its «our» is 0 by
construction, Dv652 · dev-200 vs r2's 136/38, the difference explained from artifacts ·
the fourteen with the multiplicity sentence, now their FIFTH look); measured spans beside
charges — ssh, load, s/call of THIS pod beside 2.726 / 4.498 / 5.162, per-poll copy-back
measured at ≥ 900 rows. Report `docs/reports/pass1-window-r2.md`, path-only in chat.

## Read back FIRST, one line each

what step 0.5 corrects and why the scorer is not edited · the 901 and how the pack is
built without re-rendering · the rate, the three files it is derived from, and the knife
edge at both spans · the worst case, the cap, the hard stop, the recovery arithmetic, the
step sum · what the volume's file is and is not · why there is no separate rate rung.

## DO NOT

No change to prompt v2, neighbours, labels, gold, the sealed r1 window record, r1's
pack or out-file, or any pinned file (the scorer included); no merge of the volume tail;
no second leg; no dev gate; no bar on the fourteen; no generation before H6 and the
commits; never leave `--watch`; never two billing endpoints CONCURRENTLY (one
re-creation after a proven deletion is allowed); no third pod; team-lead files verbatim
(docs/STATUS.md, docs/SPEC.md, docs/PROMPT-*.md) — commit them, never edit.
