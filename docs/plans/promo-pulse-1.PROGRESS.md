# PROGRESS — promo-pulse-1 (executor's one file: done / next / open stop, ≤60 lines)

Ruling 03.09 (e) made this file the phase's state; §8 of the phase file stays the DONE list.

## The money, live
`promo-dev-loop`: **$0.5254 spent**, cap **$2.4469** → **B ≤ $1.9215**. Cycle 3 **$4.2531 of $7.00**,
REMAINING **$2.7469**. Free for c3 = $2.7469 − $1.9215 − $0.30 = **$0.5254**: ruling (i)'s **$0.50 cap
still fits, by $0.0254** — the volume drips ~$0.24/day, so NOT tomorrow. This session spent **$0**.

## Done
- **03.09 s9 iteration 1** ($0.4358): signal 0.8792, subject 0.7929; **s10/s11 A(1)** (`c7a63a7`);
  **04.09 s12 «A-rest», $0** (`c2234a4`, `d64faf7`, `3f75106`) — ACCEPTED WHOLE by ruling (k).
- **04.09 s14 «sources-r3» (`449cab1`): the COLLECTION landed at $0; the census ARTIFACT and the
  paid leg are both inside the open stop — the $0 leg is NOT closed.**
  - **Never unjoined; no join was owed.** `joins_5c1.jsonl:33` logged `already_member` on 30.08 and
    a live `CheckChatInviteRequest` (a read) returns `ChatInviteAlready`, `left: False`, `1255265634`.
  - **The defect.** Telethon reads the `+` invite form only after a `t.me/`, so
    `parse_username('+Ejz6ubzm21IyMTQy')` → `(None, False)` and `collect_r2.py:377`'s
    `except Exception` left a silent zero row. `resolvable()` rewrites the RESOLVE ARGUMENT ONLY.
  - **Collected, $0: +33 posts, 2026-08-04 → 2026-09-04, all 33 carrying media**, 6 album heads, 9
    price-shaped texts, 0 comments. `--only` COLLAPSES the record (19 rows → 1), so `--plan` rebuilt
    every row from the store: the diff is marketopt's four fields plus `phase`, the other 18 equal.
  - **⚠ THE WRITE MOVED THE CORPUS ANCHOR; `data/` is gitignored, nothing to restore from.** The max
    was VARUS 2026-08-30, now marketopt **2026-09-04**, and `promo_census_c2.anchor_of()` computes
    `max(post date)+1` FROM THE STORE — the shipped anchor 2026-08-31 would recompute to
    **2026-09-05** and re-pin all 19 rows. `walk_window` has no upper bound, so no instrument in the
    tree could have avoided it. The 33 rows are a 33-day population under `window_days: 28`.
  - **The census READING is the numbers above; its ARTIFACT has no producer** — no census script
    writes this channel without new code (`census_c3a_posts.py --out` reads `data/raw/posts`, not
    `raw_r2`), and the PAGE count is not derivable at $0 at all (`collapse_albums` keeps one record
    per album). Estimate only: the public sibling is 12 posts → 52 pages, so 33 ≈ **$0.12**.

## Next — the census artifact + the paid leg, once the stop is ruled. THEN B: `*_iter2.*`, ≤ $1.9215.

## Open stop — the paid leg has no instrument, and its acceptance check is not expressible
1. **Every C2 producer writes a PINNED path and takes no `--out`:** `fetch_promo_media_c2.py` and
   `promo_pagecount_c2.py` declare only `--plan`; `promo_census_c2.py` has no channel filter and its
   `anchor_of()` re-pins all 19 rows. All ten `prereg_promo_c2.json :: pinned_inputs` MATCH on disk
   today, so running any moves a sealed sha and `through_the_seal()` then refuses to rebuild w2.
   `run_promo_c2.py` takes no `--prereg/--census/--cap/--step`; `STEP promo-pulse-1` is `closed`.
   **Q1 — parameters on the C2 producers, or c3 siblings?** Either is new code + its own ledger, and
   after the anchor move it must ALSO carry a **pinned anchor**. This blocks the census reading.
2. **«The screen shows Маркетопт beside w2» cannot pass as written.** `tick.py --window` is one
   scalar (default `w2`) and `build_promo_screen` renders one window id, so `--window w3` hides w2's
   1 113 positions; and `config/chain_aliases.yaml` gives the spellings to `marketopt_promo` alone
   («`marketopt_private` … is the SAME chain»), so a w3 row renders a SECOND chain id for one chain,
   against A(2). **Q2 — one screen over two windows, or folded into the one chain id?**
3. Tree clean, `make check` 4 319 passed / 2 skipped. Nothing paid or irreversible was reached.

## Needs named, not built (the standing prompt forbids adding what the phase did not ask for)
- **`resolvable()` has no unit test** (the fake in `tests/test_collect_r2.py` keys on `@{username}`,
  no test uses a `+` handle; its check was the live collection) **and the `--comments` branch still
  passes the bare handle** — dead today only because `comments_enabled: false`.
- **Ruling (k)2 holds the near-quote** «Шикарно…» + the codebook doc's 11 quotes to the law FREEZE
  before the holdout pre-registration — one move, one record.
- **`check_law` compares `codebook_version` only**; **`committed_registration()` ignores
  `pinned_inputs`**; **`--score` without `--suffix` and the runbook's K8 `--out` still point at the
  PAID `…_iter1.*` — B must repoint them.** PHASE §8 (c)'s «every collected channel» now counts
  marketopt_private; `1925810730` stays unaddressable; `@ON_LINE_MO` ((i)3) waits on Q1/Q2.
