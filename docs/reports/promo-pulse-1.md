# promo-pulse-1 — «Что и почём промоутируют сети по молочке и мороженому, и как покупатели на это реагируют — неделя за неделей?»

**Not answered yet — the screen needs positions, positions are the paid leg, and this session bought
nothing. What it settled is the number that leg waited on.** C2's population is **3 008 leaflet
pages**, counted rather than bounded (`results/promo_pagecount_c2.json`) against the census's
1 022…9 653; C2 prices at **$3.1563** at the marginal's pessimistic end, $2.4681 at its optimistic
one (`results/promo_projection_c2.json :: verdict.c2_priced_usd`). Cycle 3 is open at **$4.80** on a
balance of **$4.48** (`results/spend_cycle3.json`), so C2 fits the ceiling but not beside C3's caps
($3.16 + $2.50 + $0.30 = $5.96). The 01.09 ruling's even cut applies, its two parameters are unset,
and the phase pauses there: `docs/plans/promo-pulse-1.STOP.md`.

**Why the count was free.** `RawStore.collapse_albums` merges an album into one record and keeps
`has_media` as a bool — the member count is discarded at write time, and that alone is why the
census could only bound the pages. The store's own msg_id gap recovers it on **240 of 258**
manifest-measured posts, over-counting on 18 and **under-counting on 0**: a sound upper bound of
3 362. The count is one $0 Telegram pass over the census's *pinned* ids (`ids_sha256 a56dc6dace…`,
never a window re-derived now) — **968 of 968 posts reached, 0 unreachable**. A page is a PHOTO
member: the window also holds 146 videos and 3 polls `has_media` would have billed as pages, and no
documents, asserted so the rule fails if that stops being true. `git status --porcelain data/` empty
afterwards, `shasum -c` 6/6 OK. Cycle 3 is a new line; cycle 2 is superseded, not edited.

**Also landed.** `collect_5c1.py::collectable` now reads `collect: false` (the `/code-review`
finding: r2 wrote the flag, no reader looked at it); the pause narrows COLLECTION only, so `joinable`
moved to `entered_rows` and eighteen joins already made are not un-said — both directions tested.
S3 trends: `src/market_pulse/trends.py`, SQL only, recomputed twice identical, an empty week **absent
never zero**, asserted on a week *between* two weeks with data plus its negative control.

**Left undone:** S4/S5 wait on the cut's parameters, S9/S10 on the dev labels, K6 on the positions
labels; S12–S14 render the six promo tables, empty until the paid legs fill them — a tick asserting
«zero new rows» over zero rows is a saturated proxy. **Deviations** (plan §7 revision carries each):
Dv12 K4 range → one number, the rate row that justified the range now exists `[cause: contract-gap]`;
Dv13 `promo_pagecount_c2.py` and its photo-only rule joined the plan by revision, not a new contract
file `[cause: process]`; Dv14 S11 landed in a new module, no pin moved `[cause: process]`.

**`make check` at `d305953`: 4 230 passed · 2 skipped · exit 0** — predicted before the reading
(4 225 after the six reds, + 5 new tests) and it landed on the prediction. Every red this session
was mine: opening cycle 3 let `main()` read `CYCLE3_LEDGER` past the autouse redirect Dv424 added
for cycle 2, so a `--close --note` test appended a session to the LIVE line at a fixture's balance.
Restored, then closed as a class — explicit cycle-3 redirect, a session-scoped tripwire over all
three ledgers in `tests/conftest.py`, and `tests/test_ledger_tripwire.py` re-deriving its watch list
from the guard's own constants. `git status --porcelain results/` clean after the full run.
