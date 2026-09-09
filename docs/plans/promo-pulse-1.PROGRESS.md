# PROGRESS — promo-pulse-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines; §8 of the phase file stays the DONE list)

## Done — 09.09 s40 «c3-prep-3» ($0 = ruling (hh) item 4, all six sub-items): the runbook and the registration; no open stop
FRESH process, plain `claude`, «bypass permissions on»; the live hook stamped `.claude/session_mode` = `bypassPermissions`.
By path: ruling (hh) + its pattern pass (`dcfe3a9`). **PROGRESS's «next» is SUPERSEDED by (hh)4** — «the fresh verifier …
then «c3»» became «next: c3-prep-3», done here; the verifier follows it, narrow.
**(i) §0's cap is a COMMAND, not arithmetic (NIT 5).** First the `RUNPOD_API_KEY` export off `~/.runpod/config.toml`
(NIT 2; only its length printed), then ONE `&&` chain: gate 1 (the stamp) `&&` the v2.6 fields check `&&` the guard `&&`
`CAP = min(0.80, REM − 0.30)` off the guard's OWN `REMAINING` line, rounded DOWN to the cent, with a floor gate
`REM − 0.30 ≥ 0.15` that exits 1 ((l)4). $0.80 is the operator's word ((hh)3). Run from the FILE's own text, three ways:
bypass + FIELDS OK + `REMAINING $1.4664` → `CAP 0.80` exit 0; a scratch tree stamped `auto` dies at gate 1, exit 1; the
cap code on canned readings — `$0.4000` → the floor message, exit 1 · `$0.9000` → `0.60` (the room, not the ceiling) ·
`$1.4664` → `0.80` (the ceiling). **(ii) §1 is the TAIL of that same call** (`--register … --cap $CAP`, the guard's
`--step-cap $CAP`, the anchor commit): shell state does not survive between calls, so §3 reads the cap BACK from the
registration §1 committed (`step.cap_usd` → `0.80`) — the same number by construction, the one the anchor carries.
**(iii) §3 is DETACHED (RISK 2):** `nohup env PYTHONPATH=src … > results/run_promo_c3.log 2>&1 &`, `$!` into
`results/run_promo_c3.pid`, three short polls (PID alive · log tail · the record's last run). `| tee` DELETED with its
reason — the form the harness killed twice in C2 (`run_promo_c2.log:113`, `:171`), and a kill bypasses
`except BaseException`. `setsid` is NOT on macOS (same log :172 `command not found`); hot.md's «ТОЛЬКО setsid» is the
REMOTE runner's rule, named where it could mislead.
**(iv) §5 closes per PROCESS (NIT 1):** the post-run `--note` first, then `--close --expect-ms $MS --until <after the run>
--tolerance 0.05 --note`, `$MS` READ from the record (wall seconds × 1000 over the line's runs — `billed_now` prices a
`workers-max 1` worker in WALL, not `worker_seconds`; 5 840 215 ms on C2's real record as the shakedown). A PARTIAL walk
is retried at the next start, never widened. **The volume delete MOVES out of §4 to after the close (NIT 3** — the walk
asks `billing network-volume`, an unreadable kind refuses the close), still only on a COMPLETE run record.
**(v) `register()` names what it reads (NIT 4).** The leg label resolved ONCE from the census path (`promo_census_c3.json`
→ C3); the spellings come through `rel()` from the paths actually read — phase, both `population` sources, `order_from`'s
pagecount, `page_from`, `boot_derived_from`, the `kill_rules` guard line, the contract (`{STEP}-s4`). **Both controls to a
scratch `--prereg`, nothing under `prereg_promo_c2.json` touched:** on DEFAULT flags parent vs mine is **byte-identical,
delta 0 lines** (stronger than (hh)4(v)'s «differ only in the derived strings»); on c3 flags exactly **SEVEN** lines move,
all derived spellings, **no number among them**. The parent's default output was run FIRST — it reproduces the pinned C2
registration but for the `--register-addendum` half — so the ordered control was reachable before it was relied on ((hh)1).
**(vi) Dry run at `--cap 0.80`:** 30 pages (`289b9cc9…`) + 8 posts (`9363ff8d…`), `pagecount: match`, dear corner
**$0.1864, FITS (−76.7%)** — the four numbers (hh)4(vi) expects. Emitter's tests 27 passed. **`make check` green at
`474eaf0`: ruff clean, 4326 passed / 2 skipped** in five foreground slices; the union over the 230 files on disk proved
(overlap 0, missing 0, extra 0, floor 4266 HOLDS), the negative control (slice 5 dropped) REFUSES at 184/230.
**Ends at the committed dry run: no registration, no pod, no template, no endpoint; $0.**

## Next — the verifier's SECOND pass (narrow), then the team lead's reading, then «c3» (PAID)
**next: the narrow verifier pass over THIS item's diff only** ((hh)4) — the runbook and `register()` at HEAD `474eaf0` →
the team lead's reading of the dry run + HEAD → **«c3»** (paid, step `promo-c3`, cap $0.80 as §0's own command derives it
from the guard's `REMAINING` in THAT session, never carried from here) in ANOTHER fresh process, runbook §0 → §5 →
«chain-fold» ($0) → clean-clone e2e + `draw_truth_20` → the gate 12.09.

## Open stop — NONE
Closed on its own checks; nothing sealed moved, no fork opened, no test weakened, no threshold introduced. Tree: HEAD
`474eaf0`, porcelain empty; no pod, no endpoint, no registration, no step line open; REMAINING **$1.4664** (15:47Z — the
volume's drip since (hh)'s $1.4762).

## Named, not built (the phase file forbids adding what it did not ask for)
- **No test asserts the derived spellings or the `{STEP}-s4` contract** (both controls are runs); **§5's `--until`
  is the one hand-typed value left in the runbook**. **RISK 1 stands as (hh)3 left it:** the in-run pack gate is
  sized by TIME; `min(size, rows left)` and the dry run's
  exercise of the in-run room gate at the registered cap are NAMED — the $0.80 cap is what makes the leg pass.
- **Inherited narrative in `register()`, named not moved ((gg)5):** the verbatim quote in `authority`, `rung_0.cap_from`
  (still cites ruling 02.09 (b), not (hh)3's cap), `go_no_go`'s «the first queued C2 page».
- `promo_projection_c2.json` is not reproducible from its producer (live guard reading + growing ledger in a sha-pinned
  record) — proved by its pin. `tick.py --window` default stays `w2` (`tests/test_draw_positions_50.py:151`) — §5 carries
  `--window all`. Carried: `tooling.md`'s «the plugin is disabled»; no floor on the loop leg's arm selector; `graded()`'s
  `rows` holds only while no `about` row is dropped; no test asserts P1 in the tick, the S2 refusal or the README writer;
  ties at 16 of 28 ((dd)6); four other `get_entity` callers still pass the bare handle — other phases', not touched.
