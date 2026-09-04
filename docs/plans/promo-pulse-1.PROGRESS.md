# PROGRESS — promo-pulse-1 (executor's one file: done / next / open stop, ≤60 lines)

Ruling 03.09 (e) made this file the phase's state; §8 of the phase file stays the DONE list.

## The money, live
`promo-dev-loop`: **$0.5254 spent**, cap **$2.4469** → **B ≤ $1.9215**. Cycle 3 **$4.2531 of $7.00**,
REMAINING **$2.7469**, volume ~$0.24/day. Ruling (l)4 re-based c3: its cap is **min($0.50, REMAINING
− $0.30) as the guard prints it AFTER B** — not a number carried from today; under **$0.15** of room
it is a STOP for the operator's word. Holdout $0.30 untouched. Sessions 10–14 spent **$0**.

## Done
- **03.09 s9 iteration 1** ($0.4358): signal 0.8792, subject 0.7929; **s10/s11 A(1)** (`c7a63a7`);
  **04.09 s12 «A-rest», $0** (`c2234a4`, `d64faf7`, `3f75106`) — ACCEPTED WHOLE by ruling (k).
- **04.09 s14 «sources-r3» collection — ACCEPTED by ruling (l)1** (`449cab1`, PROGRESS `97880de`).
  - **Never unjoined; no join was owed.** `joins_5c1.jsonl:33` logged `already_member` on 30.08 and
    a live `CheckChatInviteRequest` (a read) returns `ChatInviteAlready`, `left: False`, `1255265634`.
  - **The defect.** Telethon reads the `+` invite form only after a `t.me/`, so
    `parse_username('+Ejz6ubzm21IyMTQy')` → `(None, False)` and `collect_r2.py:377`'s
    `except Exception` left a silent zero row. `resolvable()` rewrites the RESOLVE ARGUMENT ONLY.
  - **Collected, $0: +33 posts, 2026-08-04 → 2026-09-04, all 33 carrying media**, 6 album heads, 9
    price-shaped texts, 0 comments. `--only` COLLAPSES the record (19 rows → 1), so `--plan` rebuilt
    every row from the store: the diff is marketopt's four fields plus `phase`, the other 18 equal.
  - **The write moved the corpus max** 2026-08-30 → **2026-09-04**, and `anchor_of()` computes
    `max(post date)+1` FROM THE STORE. **(l)1 rules this harmless while no C2 producer re-runs** —
    C2's truth is its sealed files — and **(l)2 makes the c3 anchor an explicit pinned `--anchor`.**
    `data/` is gitignored; the 33 rows are a 33-day population under a `window_days: 28` record.

## Next — **B, the paid iteration 2** ((l)4: everything for it is ready and the dev loop is the
critical path). `*_iter2.*`, **≤ $1.9215**; repoint `--score`'s `--suffix` and the runbook's K8
`--out` off the PAID `…_iter1.*` first. THEN «c3» in ONE session, $0 build + paid leg together.

## Open stop
**None.** Both questions of the 04.09 stop were answered by ruling (l); the c3 design below is
settled law, not a fork. Nothing paid or irreversible was reached this session.

## The c3 session, as ruling (l) settled it (build it when B is done, not before)
1. **(l)2 — parameters on the C2 producers, NOT siblings:** `--out`, `--channels`, `--anchor`
   (pinned in the registration), `--prereg`, `--step`, `--cap`. Every C2 result file stays
   byte-identical — the ten `prereg_promo_c2.json :: pinned_inputs` hold and nothing under them is
   re-run — and c3 writes `results/*_c3.json` under `results/prereg_promo_c3.json`, with its own
   anchor (the day after its last post) and its own ledger `promo-c3`: `run_promo_c2.py`'s `STEP
   promo-pulse-1` is `closed: true`, so that ledger is not optional.
2. **(l)3 — the screen renders ALL windows:** `tick.py --window all`, which becomes the default
   unless a test pins `w2` — then the runbook's tick line carries `--window all`. BOTH channels take
   ONE chain id, the EXISTING `marketopt_promo` (w2's id, nothing sealed moves): `chain_aliases.yaml`
   gains `chain_of_channel: {marketopt_private: marketopt_promo}`, read by its one reader BEFORE the
   spellings. This is what keeps A(2)'s «one spelling, one chain» true with two registry rows.
3. Sizing, for rung 0 only: 33 media posts; the public sibling is 12 posts → 52 pages
   (`promo_pagecount_c2.json`), so ≈ **143 pages ≈ $0.12** at 2.7583 s/page × $0.00030669/s.

## Needs named, not built (the standing prompt forbids adding what the phase did not ask for)
- **A unit test for `resolvable()` with a `+` handle is AUTHORISED by (l)1** (product path) and not
  yet written: the fake in `tests/test_collect_r2.py` keys on `@{username}` and no test uses a `+`
  handle, so today its only check was the live collection. **The `--comments` branch still passes
  the bare handle** — dead only because `marketopt_private` has `comments_enabled: false`.
- **Ruling (k)2 holds the near-quote** «Шикарно…» + the codebook doc's 11 quotes to the law FREEZE
  before the holdout pre-registration — one move, one record.
- **`check_law` compares `codebook_version` only**; **`committed_registration()` ignores
  `pinned_inputs`**. PHASE §8 (c)'s «every collected channel» now counts marketopt_private;
  `1925810730` stays unaddressable, named; `@ON_LINE_MO` follows c3 if its census shows prices.
