# PROMPT — pass2-signals r2: the 75 threads still owed, priced on the smoke's MAX and the pod class (step 0.5 addendum $0 → D0′ $0 → D1 paid, cap $2.50 → D2 $0)

**Fresh executor session. Authority:** the operator's ruling of 2026-08-22 (day) in the
team-lead session, `docs/STATUS.md` «Открытые решения» п. 1 (з): *buy the remaining 75
threads under a new registration, cap **$2.50**, the rate charged on the smoke's MAX × the
pod-class spread.* Read: this file → `docs/PROMPT-pass2-signals.md` (the contract; every
clause not amended here stands) → `docs/reports/pass2-signals.md` §«Rung S′», §«The
per-signal scorecard», Dv702/Dv703 → `results/prereg_pass2_signals.json` (r1, superseded,
NEVER edited). Deviations from **Dv704**, enum v2 — `[cause: contract-gap | spec-gap |
verify-gap | env | tooling | model | process]`, the lesson name as a separate
`[[wiki-link]]`; five-line Process signals; team-lead files verbatim (commit
`docs/STATUS.md` and this file first); never `git add -A`.

## Step 0.5 — the acceptance addendum of r1 ($0, its own commits, BEFORE D0′)

Append an **ADDENDUM** section to `docs/reports/pass2-signals.md`; correct the ADR and hot.md
where they quote the same numbers:

1. **Re-tag every Deviation Dv681–Dv703 (and Dv702/703) on the CLOSED enum.** The report's
   «cause» column carries free lesson names (`pinned-file`, `smoke-cost-and-refusal-risk`, …)
   and not one `[cause: …]` tag, so the tally cannot be counted. Keep the names as
   `[[lesson-name]]` links beside the enum tag; then compute the split tally (contract-gap +
   spec-gap + verify-gap = contract health; process + env + tooling + model = paid) with the
   grep the report template names.
2. **The pack's headroom is 144 chars, not 603.** `results/pass2_pack.json` → `length`:
   widest 11 856 (`@mandziak:3679`, 18 rows) of 12 000; the report's D0 section quotes the
   pre-review pack. Correct the number and say which rebuild moved it.
3. **«A smoke mean of 43.09 would have been a GO» is false by 0.29 s.** 517.3 + 74 × 1.5 ×
   43.09 + 1 300 = 6 600.29 > 6 600; the break-even mean is 43.087. Correct it — fourth
   instance of one input with two values on this line; say so.

## What r2 changes — and ONLY this (state your assumptions against it)

The population, the prompt text of `pass2_thread_gm4_v1` (BYTE-IDENTICAL — the renderings
and therefore the four smoke replies must carry over), the strict authority, the bars 1/2/3
and the report-only tables, the reader's scorer and gold — r1's. What moves:

1. **Owed: 75 units** — the 74 never bought PLUS `@matusi_ukr:22303` (F2), whose reply was
   REFUSED by the parser on `"note": ""` and never read; a refused reply is a transport
   outcome, not a verdict, so the thread is re-asked. The four parsed smoke replies
   (`@VARUS_channel:10613`, `@mandziak:3676`, `@mandziak:3703`, `@matusi_ukr:22272`) are
   COPIED into r2's out-file as its first four rows, each re-verified by `rendering_sha256`
   against the r2 pack, and never re-bought — decoding is greedy
   (`results/reader_v5b_pack.json::serving.decoding`), and pass 1 showed 200/200 identical
   answers across three pods. The pack: r1's 79 units, same order, same renderings; the
   builder asserts every unit's `rendering_sha256` equals r1's (a moved rendering is a STOP
   at build time — it would orphan the four replies).
2. **Report-only fields cannot refuse — by construction (Dv702).** `per_comment.note`,
   `subject_doubt` and any other field the record marks report-only are read through a
   tolerant reader that records `unreadable` beside the value and NEVER raises; the reply's
   refusal set is exactly: relabel, an id not in the request, a signal citing no comment, a
   reply about another thread, an unbalanced/unclosed object, a domain violation on a SCORED
   field. Test: the exact r1 F2 reply (`"note": ""` on two rows) parses with
   `subject_doubt=False`, `note_unreadable=True`, 0 signals — and is COUNTED, not refused.
   The prompt text does NOT change for this (byte-identity above); the parser does.
3. **Pass 2 gets its own input ceiling, derived, not typed.** `PASS2_MAX_INPUT_CHARS =
   prompts.PASS1_MAX_INPUT_CHARS` leaves 144 chars on the widest unit. Derive a ceiling from
   what the serving config actually bounds (the model's context and
   `reader_v5b_pack.json::serving` — name the field; the reader read whole threads wider than
   this) with the arithmetic in H6; the pack re-checks every unit against it. If the derived
   ceiling is below 11 856, that is a STOP before any pod, returned to the operator.
4. **The rate is charged on the smoke's MAX and the pod-class spread.** Smoke per-thread
   seconds `[58.07, 15.801, 40.845, 56.462, 56.732]` (from `results/pass2_signals_v1.jsonl`
   `seconds`, re-derived); **charged = 58.07 × 1.67 = 96.98 → 97 s/thread**, where 1.67 is
   v2's measured pod-class spread on pass 1 (2.694 → 4.498, three pods; the base's two-point
   spread is 2.25 and is named in the record as the wider reading the ruling did NOT charge).
   Why the MAX and not a row-weighted mean: the population's widest unit is 26 rows
   (`@klopotenkofood:6040`) against the smoke's widest 10 — a fit over the smoke extrapolates
   beyond its range; the max is the only reading that covers the heavy tail without a model.
5. **Money (H6, step-1 refusal):** generation 75 × 97 = **7 275 s**; + ssh 500 + stage/launch
   150 + load 450 + overhead 1 300 = **9 675 s = 2.6875 h → worst $2.15 at $0.80/h** ($1.424
   at $0.53). **Cap $2.50**; cumulative hard stop **11 000 s = $2.4444 < $2.50**; session
   ceiling 2.50/0.80 = 3.125 h = 11 250 s ≥ hard stop. Recovery: one dead pod at rung 2
   (500 s, $0.1111; 578.5 with the measured deletion tail) + worst = 10 175 ≤ 11 000 ✓ and
   $2.2607 ≤ $2.50 ✓; widest dead pod 1 325 s. **Rung 4's knife edge at the charged spans:
   (11 000 − 1 300 − 1 100) / 75 = 114.7 s/thread** — above 97 charged and above 58.07, the
   slowest pass-2 call measured; at r1's measured pre-generation (135 s) it is 127.5. Publish
   both arms AND the derived «widest create-elapsed at which a KILL still leaves the
   re-creation reachable» (r2's Dv668 construction). **STEP SUM:** r1 $0.108122 (clock) +
   r2 cap $2.50 = $2.608 on a fresh guard step `pass2-signals-r2`, `--step-cap 2.50`.
6. **No rung S′.** The rate is registered; rung 4 (projection at max(mean, last call) on
   every poll against 11 000 s and $2.50) and rung 5 (liveness on the pod LOG line per call)
   cover the run; one out-file, one leg, the resume-skip takes the 75 after the four copied
   rows. Recovery after the first NEW reply: a KILL closes the session, the rows bought stand
   in the out-file as evidence, the remainder is a new registration.

## D0′ — at $0, before any pod, on a FROZEN tree for the review

- `src/market_pulse/pass2.py`: the tolerant reader for report-only fields and the derived
  ceiling — prompt text byte-identical (a test pins the rendered request of every unit to
  r1's `rendering_sha256`). `scripts/build_pass2_r2_pack.py` → `results/pass2_r2_pack.json`
  (r1's 79 units, same order; `owed: 75`, `carried: 4` named by id); the out-file
  `pass2_signals_r2_v1.jsonl` seeded with the four carried rows by a named step.
- `scripts/write_pass2_prereg_r2.py` → `results/prereg_pass2_signals_r2.json` with
  `supersedes` = r1 + sha and r1's closing state («rung S′ STOP at 5 of 79, four replies
  parsed, F2 refused on a report-only field»); the Dv613 sweep for repealed numbers (6 600,
  1.50, 120, 48.6486, 32.4324, 12 000-as-ceiling) — quoted only inside `supersedes`.
- `scripts/gate_pass2_signals.py --revision r2` if r1's pinned bytes stay untouched,
  otherwise a sibling (say which); rung S′ removed from r2's clock; `--pre-create-check`
  recorded; the runbook `scripts/runbook_pass2_signals_r2.md` — no go token, no wait.
- Tests, both directions, on a fake transport: the four carried rows are accepted and never
  re-asked; F2's exact r1 reply parses and is counted; a relabel still refuses; rung 4 at
  115 s/thread after 10 threads → KILL with the recovery arithmetic published; at 90 → GO;
  the derived ceiling accepts 11 856 and refuses ceiling+1; every gate COMMAND driven end to
  end (r1's two fatal defects lived in `main`, not in the functions).
- **The five-lens review reads a COMMITTED tree:** commit D0′, run the five lenses and their
  skeptics on that commit, fix on top, then a second skeptic pass on the fixed commit before
  the create — the review's tally is then a tally and not a race.
- `make check` green; `make preflight ARGS='pass2.py prereg_pass2_signals_r2.json'` pasted;
  guard anchor `pass2-signals-r2`; ADR gains its r2 section (the carried rows, the tolerant
  reader, the ceiling, the ruling (з) verbatim). Commits: addendum (step 0.5) · module +
  tests · pack + seed · producer + record + gate · runbook · ADR · guard anchor · vault tail —
  ALL before the first `pod create`, and the last one at least five minutes before it.

## D1 / D2

D1 as r1's runbook minus the go/no-go: price → clock-bounded ssh poll → stage, the pod writes
`launched_at` → `--watch` never left (rungs 3/4/5/6 on every poll; liveness on the log line)
→ scp + sha (three for three) → delete → listings with the volume control → rung 7 on the
Mac. **D2 over all 79 units** (4 carried + 75 bought): bars 1/2/3 through the reader scorer
— bar 1 flagships 5/5 all-or-nothing (F2 expected RED by construction — say so beside the
verdict), bar 2 inherited and reported «held», bar 3 on the N threads pass 2 called (10366's
four rows); the per-flagship scorecard; the DROP table; `subject_doubt` rate by pass-1 label;
the comparison row v5b (bar-1 2/5, $0.3126, 23 threads) vs pass 2 (79 threads, pass 1 $0.742
+ pass 2 r1 $0.108 + r2); measured spans beside charges — s/thread mean/max of THIS pod
beside the smoke's 45.6/58.1. Report `docs/reports/pass2-signals-r2.md`, path-only in chat.

## Read back FIRST, one line each

what step 0.5 corrects (three items) · the 75 and the four carried rows, and why the prompt
must not move a byte · which fields can no longer refuse and which still can · the ceiling
and where it is derived from · the rate, its two factors and why the MAX · the worst case,
the cap, the hard stop, the recovery, the step sum · what a KILL after the first new reply
means · why the review reads a committed tree.

## DO NOT

No change to the prompt text, the population, the scorer, the gold, `prompts.py`, the r1
record/pack/out-file or any pinned file; no re-buy of the four carried threads; no
relabelling path; no bar on the fourteen; no go/no-go rung; no generation before H6 and the
commits; never leave `--watch`; never two billing endpoints CONCURRENTLY; no third pod;
team-lead files verbatim (docs/STATUS.md, docs/SPEC.md, docs/PROMPT-*.md) — commit them,
never edit.
