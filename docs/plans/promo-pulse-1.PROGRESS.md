# PROGRESS — promo-pulse-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines; §8 of the phase file stays the DONE list)

## Done — 09.09 s39 «c3-prep-2» ($0 = ruling (gg) item 6, all six sub-items): the leg is CLEAN and PRICED; no open stop
**The first line, as (gg)6 orders it.** A FRESH process, plain `claude`: the header says **bypass permissions on**;
the start injected ONE SessionStart hook (`refresh-hot-cache: OK (6427 bytes)`, hot.md once, the stale check,
`brain-census 7.7Ktok`); the live hook stamped `.claude/session_mode` = **`bypassPermissions`** at the first Bash
call — no stop. By path: ruling (gg) + the issued harness file (`2c1d63c`), s38's knowledge checkpoint (`bd27cb1`).
**PROGRESS's open stop (l)3 is CLOSED by (gg)2** — its own $0 item «chain-fold», shape (b), AFTER c3.
**(i) The harness (`2004216`).** `.claude/settings.json` = the issued `2026-09-09-harness-allow/settings.json` byte
for byte through the **Write tool** (`diff` exit 0, sha `fae771af…` both sides) — `cp` from `docs/reviews/**` is
refused BY DESIGN, the deny rules reaching into Bash (PROCESS v2.6), so one documented refusal met the documented
path and no probe was spent. The v2.6 check on the LIVE file **both ways**: `HARNESS FIELDS MISSING` exit 1 before
(its `allow` still carried the two `pod create` / `pod delete` rules), `HARNESS FIELDS OK` exit 0 after.
**(ii) The runbook's §0** is now gate 1 (the stamp) `&&` the v2.6 check, copied out of `PROCESS.md:119`, not retyped;
the create-prefix gate and the §2 note it pointed at are **deleted, not weakened** — over an `allow == []` list that
gate refuses every leg for a reason no harness change can fix ((gg)3), one sentence says so; the launch expectation
is plain `claude`. Both gates both ways: MODE bypass + FIELDS OK exit 0 here; `auto` stops the chain at gate 1, exit 1.
**(iii) Item 5 — the record stops naming a file it did not read.** `rel()` derives every named file from the path
`build()` actually read; `pagecount_used` is resolved ONCE and feeds `exact_pages`, `population.pages_counted_by`,
the `c2_priced_means` prose and the new `reads.pagecount`. Inherited C2 narrative (`decision`, `cap_rule`) named,
not moved ((gg)5). **The control, to a SCRATCH `--out` so nothing under `prereg_promo_c2.json` moves:** on the
DEFAULT path both spellings come out byte-identical to the pinned C2 record, and my edit's ONLY delta against the
parent commit's own producer is the one added line `"pagecount": "results/promo_pagecount_c2.json"`.
**Deviation, cause `stale-live-input`:** (gg)5's «the default path re-writes C2's projection byte-identical» is
**unreachable as worded, and was already unreachable with my change absent** — that record embeds a LIVE guard
reading ($4.8000, 2026-09-01) and an 11-row ledger against $1.4762 and 31 rows today: the parent producer's own
output differs from the pinned file in **40 lines**. The pinned file was never re-written; the stricter claim was
run instead (parent output vs mine = 1 line).
**c3 re-written** (`fc015d45…` → `5ea83a55…`): the four expected moves only — both spellings to c3, the new
`reads.pagecount`, the fresher remainder ($1.4956 → $1.4762). **Every priced number unmoved** ($0.0958 dearest,
$0.0793, $0.0724). **Dry run re-run** at the cap DERIVED from the live guard line — min($0.50, $1.4762 − $0.30) =
**$0.50**: 30 pages (`289b9cc9…`) + 8 posts (`9363ff8d…`), `pagecount: match`, dear corner **$0.1864, FITS
(−62.7%)**. Room over the cap $1.1762, so (l)4's «under $0.15 → STOP» does not fire.
**(iv) §4's volume line:** after the listings and ONLY on a COMPLETE run record (a second `--run` KEEPS the volume,
~$0.24/day against a re-download) — `runpodctl network-volume delete qw4nwleanc`, syntax off the CLI's own help
(`delete <volume-id>`, aliases `rm`/`remove`), proven by `network-volume list` showing it gone, never by an exit code.
**(v) `make check` green: ruff clean, 4326 passed / 2 skipped** — the baseline's own totals, in FIVE foreground
slices (the full run does not fit one call). Union proved by script over the 230 files on disk: overlap 0, missing 0,
floor 4266 HOLDS; the negative control (slice 5 dropped) REFUSES at 200/230.
**(vi) The item ends at the COMMITTED dry run:** no registration, no pod, no template, no endpoint; **$0**.

## Next — the fresh verifier, then the team lead's reading, then «c3» (PAID) in ANOTHER fresh process
**next: the fresh verifier** ((gg)6) over the money paths at HEAD `2004216`, the runbook, gate 1, the v2.6 check, the
volume line and the projection's spellings → the team lead's reading of the dry run + HEAD → **«c3»** (paid, step
`promo-c3`, cap = min($0.50, REMAINING − $0.30) **as the guard prints REMAINING in that session**, never carried from
here) in ANOTHER fresh process, runbook `promo_c3_paid_leg.md` §0 → §5 with the volume delete in §4 → «chain-fold»
($0) → clean-clone e2e + `draw_truth_20` → the gate 12.09.

## Open stop — NONE
The item closed on its own checks; the one deviation (`stale-live-input`) moved nothing sealed, opened no fork and
weakened no test. Tree: HEAD `2004216`, porcelain empty; no pod, no registration, no open step line, REMAINING $1.4762.

## Named, not built (the phase file forbids adding what it did not ask for)
- **No test asserts `reads.pagecount` or the derived spellings** — the control is a run, not a suite member.
- **`results/promo_projection_c2.json` cannot be reproduced from its producer** (a live guard reading and a growing
  ledger inside a sha-pinned record): a record whose bytes no re-run reaches is proved by its pin alone.
- **`tick.py --window` default stays `w2`** — `tests/test_draw_positions_50.py:151` reads it, so §5 carries `--window all`.
- Carried: `tooling.md`'s «the plugin is disabled»; no floor on the loop leg's arm selector; `graded()`'s `rows`
  holds only while no `about` row is dropped; no test asserts P1 in the tick, the S2 refusal or the README writer;
  ties at 16 of 28 ((dd)6); four other `get_entity` callers still pass the bare handle — other phases', not touched.
