# PROGRESS — promo-pulse-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines; §8 of the phase file stays the DONE list)

## Done — 08.09 s36 «s2-loop» ($0, ruling (dd) item 5): the shipped number is measured on the PRODUCT's pipeline, and it ships first
**The number, and it is the file's.** `results/grade_promo_loop_readings.json` reads dev-3 end to end through the product
(the four hooks of §2 S4, then P1): **0.7411 (83/112) ❌ bar 0.80 · 0.7937 ✅ bar 0.75**, against the reading's 0.7500 /
0.8021. dev-40 (0.8857 / 0.8667) and dev-2 (0.9043 / 0.8296) come out identical both ways. The team lead's replay is
reproduced by the product's own functions; the verdicts do not change in kind — subject RED, signals GREEN.
**Start ritual.** (dd) + `docs/reviews/2026-09-08-stop-patterns.md`, PHASE v20, STATUS committed by path (`fd2c86b`);
s35's knowledge checkpoint (`033c4fe`); this file's «next» rewritten to «s2-loop» as (dd) item 5 orders (`e94c3b6`). No
STOP file. **$0**: no pod, no registration, no ledger line, `runpodctl` never called; cycle 3 REMAINING $2.1178 stands.
**(i) The loop leg (`0e1e809`).** `promo_p1_apply.py` gains a second leg over the SAME three sets, starting one step
earlier at the raw answers of the pod out-files each set now names: `promo_prompts.parse` → `promo_hooks.screen` →
a record shaped as `tick.signal_records` reads it → `tick.p1_rows` → `promo_dev_pass.predicted_rows` → K8 v2, every step
CALLED, none re-spelled. The grading tail is now ONE function both legs read (`graded`); the accepted reading's record
did not move under that extraction — `8b616de7…` before and after, the sha (cc) quotes. Two runs byte-identical
(`06d37e84…`), no clock, no git block. The boundary, measured: 3 signal rows dropped on dev-3, 2 on dev-40 and on dev-2,
every one `quote_is_a_substring` (dev-3's include `@VARUS_channel:5119/5987`), and NO `about` row dropped anywhere —
which is why each leg's `before` subject reading is the other's exactly. Holdout-3 disjointness re-checked over this
leg's own files (`leak_check` split so the reading's block could stay byte-for-byte what it was).
**(ii) The shipped row first (`212f905`).** `S2_SOURCES` gains «holdout-2 · loop (hooks + P1) — shipped» from
`sets.dev3`; the three raw-answer rows stay, labelled «reading». The loop record shares the P1 record's set shape, so
`s2_readings` gained a tuple, not a branch. The TIE flag is a fourth field, not «whichever file carries `misses_after`»:
two rows now do, and (dd) item 6 pins the published count to the P1 reading (16 of 28). `S2_FILES` unpacks the sources
once — a second spelling of that unpack lived in a message only `--check` reaches and broke on the new field, caught by
running the control. `--check` names all four; `--check --results <empty>` exits 1 naming the loop record.
**(iii)+(iv) (`075c93b`).** `make promo-screen` now runs `build_readme_results.py` — the writer's missing caller. The
tick's two docstrings say «ruled 08.09 (dd)» where they said «the team lead's to rule».
**(v) Three published sentences corrected (`5e9854e`) — prose and one print format, no number moved.** A read-only
4-lens review of my own diff (20 agents, **none died**; 8 findings, 1 survived both skeptics, raised independently by 3
lenses) caught `S2_BOUNDARY` claiming the readings «stand at or above the product's» while «holdout-2 · raw» 0.7054 and
«holdout-40 · raw» 0.7181 sit BELOW the shipped 0.7411 in the same table — they lack P1 entirely, so the hooks are not
the only difference; it now names the PAIR the hooks separate and orders nothing. From the refuted bucket, by hand: the
tie sentence NAMES its row, and the loop's `rewritten` prints over its own denominator (7/196, not «7» beside «112»).
**`make check` at `5e9854e`: ruff clean; 4326 passed / 2 skipped ≥ 4326, over 230 files in FIVE slices, not one
invocation** — the full run was killed three times for system memory (~66 MB free). Deviation, cause `env-memory`: the
totals are the claim, the method is the deviation. The slice list is closed by a UNION check (`set(slices) ==
ls tests/test_*.py`, 230 = 230) with a negative control that refuses when one slice is dropped, not by a count in prose.
HEAD `5e9854e`, porcelain identical on both sides (the session hook's two `knowledge/` files and the operator's
untracked `Claude outputs/` — nothing of the item's). README `2ac33ed5…`, `promo.html` `a5dc61b5…`, both stable.
**No open stop.** No test, pin, guard or ledger line was added; no record was widened; no number was typed.

## Next — «c3-prep» ($0), exactly as (cc) wrote it, plus (dd) item 5's contract line
The c3 leg per ruling (l) 2–4 on its own line `promo-c3`, cap ≤ $0.50 priced at its dry run; the create permission
PROVEN at $0 (PROCESS v2.3: the allow rule + the `--help` proof in runbook §0); the runbook re-pointed → the fresh
verifier → «c3» (paid) → the volume `mp-srv2` → clean-clone e2e + `draw_truth_20` → the gate 12–13.09. **Contract line
(dd) item 5:** the C3 record's `channel` is the registry's spelling WITH `@` and a channel the registry lacks is the
producer's refusal — `promo_post.owner()` needs the `@` while `RawStore` strips it, so a record writing the file stem
would silently never fire R2/R3.

## Named, not built (the phase file forbids adding what it did not ask for)
- **No floor on the loop leg's arm selector.** A missing draw file makes `k8.strata_of` return `{}`, `units` empty, and
  the leg would publish `0.0000` as the shipped number instead of refusing. The reading leg has the same hazard already;
  a floor is a guard, so it is named here and not built.
- **`graded()`'s `rows` is 139/188/112 on both legs only because no `about` row is dropped** — if a hook ever drops
  one, the loop leg's `rows` stops being the set's gold-shaped row count while the label stays the same.
- Still no test asserts P1 firing INSIDE the tick, the S2 refusal, or the README writer — all shown, none asserted. K12
  reads the repo's real `results/` through the screen's `--results` default; `tick.REGISTRY` is a module constant.
- Carried: PROCESS v2.3's allow rule + `--help` proof (c3-prep's); draw 3 without its own test; the hard-stop edge in
  the guard's close; `committed_registration()` does not re-verify `pinned_inputs`; `-r2` re-points nothing; a
  cross-leg `--step`. The tie count stands at the FILE's rule, 16 of 28, per (dd) item 6 — no gold edit.
