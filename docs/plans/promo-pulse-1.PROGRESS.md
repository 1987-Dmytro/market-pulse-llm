# PROGRESS — promo-pulse-1 (executor's one file: done / next / open stop, ≤60 lines)

Ruling 03.09 (e) made this file the phase's state; §8 of the phase file stays the DONE list.

## The money, live
`promo-dev-loop`: **$0.5254 spent**, cap **$2.4469** → **B ≤ $1.9215**. Cycle 3 **$4.2531 of $7.00**,
REMAINING **$2.7469**. Free for c3 = $2.7469 − $1.9215 − $0.30 = **$0.5254**: ruling (i)'s **$0.50 cap
still fits, by $0.0254** — the volume drips ~$0.24/day, so NOT tomorrow. This session spent **$0**.

## Done
- **03.09 s9 iteration 1** ($0.4358): signal 0.8792 HOLDS, subject 0.7929; **s10/s11 A(1)**
  (`c7a63a7`). **04.09 s12 «A-rest», $0** (`c2234a4`, `d64faf7`, `3f75106`) — ACCEPTED WHOLE by (k):
  fold → subject **0.8214**, law **v1.2**, `--leak-check` CLEAN, rung 0 FITS $1.3193 of $2.4469.
- **04.09 s14 «sources-r3: Маркетопт» — the $0 leg DONE; the PAID leg is the open stop.**
  - **Never unjoined; no join was owed.** `results/joins_5c1.jsonl:33` logged `already_member` on
    30.08, and a live `CheckChatInviteRequest` (a read — `ImportChatInvite` NOT called) returns
    `ChatInviteAlready`, `left: False`, chat `1255265634`. PHASE §3's «joined 30.08» and STATUS's
    «НЕ собран» are BOTH right: five days were ONE swallowed defect.
  - **The defect.** Telethon reads the `+` invite form only AFTER a `t.me/`:
    `parse_username('+Ejz6ubzm21IyMTQy')` → `(None, False)`, `'t.me/+Ejz…'` → `('Ejz6…', True)`;
    `collect_r2.py:377`'s `except Exception` swallowed the ValueError into a silent zero row.
    `resolvable()` rewrites the RESOLVE ARGUMENT ONLY — `handle` stays the registry spelling, the
    store key and `segment_for`'s join key.
  - **Collected, $0: +33 posts, 2026-08-04 → 2026-09-04, all 33 carrying media**, 6 album heads, 9
    price-shaped texts. `--only` COLLAPSES the record (`write_record` sets `channels` wholesale,
    19 → 1), so `--plan` rebuilt every row from the durable store: `git diff results/collect_r2.json`
    is marketopt's four fields plus `phase` («comments»→«plan»), the other 18 rows byte-identical.
  - **The page count is NOT derivable at $0** — `collapse_albums` keeps one record per album, no
    member count. Estimate for pricing only: the public sibling is 12 media posts → 52 pages
    (`promo_pagecount_c2.json`), so 33 posts ≈ **143 pages** ≈ **$0.12** at 2.7583 s/page ×
    $0.00030669/s (`run_promo_c2.json::runs[1].measured`) + boot $0.065.

## Next — the paid leg of «sources-r3», once the stop is ruled. THEN B: `*_iter2.*`, ≤ $1.9215.

## Open stop — the paid leg has no instrument, and its acceptance check is not expressible
1. **Every C2 producer writes a PINNED path and takes no `--out`:** `fetch_promo_media_c2.py` and
   `promo_pagecount_c2.py` declare only `--plan`; `promo_census_c2.py` has no channel filter and
   its `anchor_of()` would re-pin all 19 rows under a new window. All ten `prereg_promo_c2.json ::
   pinned_inputs` MATCH on disk today, so running any of them moves a sealed sha and
   `build_aggregates.through_the_seal()` then refuses to rebuild w2 at all. `run_promo_c2.py` takes
   no `--prereg/--census/--cap/--step`; its `STEP promo-pulse-1` ledger is `closed: true`.
   **Q1 — parameters on the C2 producers, or c3 siblings?** Either is new code + its own ledger.
2. **«The screen shows Маркетопт beside w2» cannot pass as written.** `tick.py --window` is one
   scalar (default `w2`) and `build_promo_screen` renders one window id, so `--window w3` hides
   w2's 1 113 positions; and `config/chain_aliases.yaml` gives the spellings to `marketopt_promo`
   alone («`marketopt_private` … is the SAME chain»), so a w3 row would render a SECOND chain id for
   one chain — against A(2). **Q2 — one screen over two windows, or folded into the one chain id?**
3. Tree clean, `make check` 4 319 passed / 2 skipped. Nothing paid or irreversible was reached.

## Needs named, not built (the standing prompt forbids adding what the phase did not ask for)
- **`resolvable()` has no unit test** — the fake in `tests/test_collect_r2.py` keys on `@{username}`
  and no test uses a `+` handle; its check was the live collection. **Ruling (k)2 holds the
  near-quote** «Шикарно…» + the codebook doc's 11 quotes to the law FREEZE — one move, one record.
- **`check_law` compares `codebook_version` only**; **`committed_registration()` ignores
  `pinned_inputs`**; **`--score` without `--suffix` and the runbook's K8 `--out` still point at the
  PAID `…_iter1.*` — B must repoint them.** Coverage: @kopiyochka1's admin account is outside
  `channel_admins.yaml`, 28 VARUS comments carry `sender_anon_id: null` (recall 874/902); PHASE §8
  (c)'s «every collected channel» now counts marketopt_private, and `1925810730` stays
  unaddressable. Alias file omits KFC, Roshen, Велмарт, Mono; `@ON_LINE_MO` ((i)3) waits on Q1/Q2;
  `terminate_after_minutes` 90, voided by (d), still prints at rung-1 GO.
