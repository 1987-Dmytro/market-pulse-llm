# PROMPT — cycle2-money: close the Phase-4 ledger, open the $20 cycle-2 line, fix the step instrument

**$0 GPU. Cloud is READ-ONLY this whole contract: balance and billing reads are unlimited
(that is the recovery clause), creating ANY billable resource is forbidden.**

**Goal.** Phase 4's money loop closes honestly; the operator's cycle-2 line ($20, ruled
2026-08-16) gets its home and its law; the guard's `--step` reading stops lying by
construction (Dv411 family). Everything here is mechanically verifiable — autonomy is
yours on code structure and test names, ZERO invention on money semantics or law text:
where this contract fixes a number, a threshold or a manoeuvre, that is the ruling.

**Preconditions.** No other Claude Code session may be open on this repo (one was open
today writing vault files — confirm with the operator it is closed). Baseline: `make
check` 2562 passed / 2 skipped at `c916d67` with the uncommitted tail below.

## Step 0 — the standing tail, two commits by path (never `git add -A`)

Check live `git status` first. Expected, in two commits:
1. vault tail — `knowledge/daily_logs/2026-08-15.md`, `knowledge/hot.md`,
   `knowledge/index.md`, `knowledge/decisions/INDEX.md`,
   `knowledge/decisions/reader-probe-card-and-interface.md` (the probe-b ADR — already
   written, do NOT duplicate it), plus any further `knowledge/**` files today's parallel
   session left behind;
2. team-lead files — `docs/STATUS.md` (team-lead edits of 16.08) and this contract
   `docs/PROMPT-cycle2-money.md`, committed verbatim, never edited.

A dirty path outside those two classes → STOP and report before touching anything.

## Step 0.5 — two ADR debts (English long form, rows in `knowledge/decisions/INDEX.md`)

Source for both: `docs/STATUS.md`, the two «День 16.08» sections (operator-language; you
translate, you do not reinterpret).
- `serving-latency-deferred` — cold start ~239 s decomposed (~214 s = 62 GB bf16 load +
  on-the-fly NF4), warm row parity pod vs serverless (4.07 vs 4.10 s), decode ~5 tok/s
  by the research stack choice; operator ruling 16.08: remedies deferred until «готовим
  прод», runtime and cards unchanged.
- `reader-sitting-16-08` — four rulings, operator's word: (1) cycle-2 line $20;
  (2) reader instrument A+B as ONE new registration (v3): container-tolerant parser by
  explicit ruling (domains stay strict; two top-level objects that disagree on a key =
  refuse, never last-wins) + v3 prompt "one JSON object, `[]` for empty"; (3) the
  varto/marker silencer is OFF for the READER path only — payment gate of
  classification and r1 brand attribution untouched; the new census cell (narrow ·
  varto off · plus-spam/scam on) is MEASURED in reader-v3, never derived; (4) vocabulary
  adjudication: «категория» in `docs/REFERENCE-signals-w1.md` ≡ «категория_личное» of
  the ratified taxonomy — the gold will be re-derived as a NAMED revision in reader-v3,
  the reference file itself is not edited, the ruling lives as its own record.

## D1 — close the Phase-4 ledger

Run the guard, then APPEND a closing session entry to `results/spend_phase4.json`
`sessions` with the final readings (balance delta AND billing-since, per the Dv33 rule)
and a note that PHASE 4 IS CLOSED. Append-only: `runpod_balance_at_phase4_start`,
`anchored_at` and every existing session are untouchable (the file's own note is the
law; it must never be regenerated). The two tests that read the real file and select
their row by timestamp must stay green. The guard learns to SAY the phase is closed
when it is.

## D2 — SPEC amendment 3.23: the cycle-2 line (the house landing manoeuvre, SIX parts)

Precedent: fix-c's landing. Verified anchors on disk today: marker format =
`docs/SPEC.md:951–968` (the 3.22 block); `BLOCKS_TODAY` ends at "amendment-3.22"
(`scripts/write_prereg_5c2.py:92`); enumeration list `tests/test_sku_prereg.py:246–275`;
**the intruder is currently `amendment-3.23`** (`tests/test_prereg_5c2.py:316`) — it
MUST move to `amendment-3.24` in the same change or the suite reds. Enumerate every
strip family that names today's blocks (grep BOTH producers —
`scripts/write_prereg_5c2.py` and `scripts/write_sku_prereg.py`, whose
`registered_law()` the markers cite — plus the test enumerations) and show the negative
controls, as every prior landing did. Never touch `KEEP_BLOCKS` or the
`amendment-index` block (Dv335).

Block content (law text — translate faithfully, do not extend):
- Cycle-2 budget line **$20.00**, operator ruling 2026-08-16. Home:
  `results/spend_cycle2.json` + `CYCLE2_CAP_USD` in `scripts/runpod_guard.py` (beside
  `PHASE_CAP_USD = 33.00`, line 42).
- The anchor is the first guard balance reading **≥ $40.00** after the operator's
  top-up, recorded verbatim with its timestamp. Anchoring below the threshold is
  refused.
- Phase 4 is CLOSED at its D1 final reading. The inter-ledger gap (after Phase-4 close,
  before the cycle-2 anchor) is unbudgeted BY DESIGN and nothing may run in it; only
  the standing network volume bills there.
- Step readings must name the volume's rent separately from the step's own resources
  (the attribution rule of D3).

## D3 — the guard: cycle-2 ledger + the Dv411 family fix

Grep the pins BEFORE the first edit: `results/prereg_5c2.json` borrows this module
LIVE — its sha move takes the third `MOVED_BORROWS` entry by the house manoeuvre
(done twice already; same treatment, never a re-pin).

- (a) `CYCLE2_CAP_USD = 20.00` and the `results/spend_cycle2.json` ledger. Anchoring
  refuses while `balance()` reads below $40.00. If the top-up is still not visible this
  session, ship the refusal path TESTED and report «anchor deferred, awaiting funds» as
  a named debt — do not wait, do not poll.
- (b) Dv411: the step reading becomes TWO readings — `step anchor − balance now` AND
  `billing_since(step anchor time)`; the verdict takes the pessimistic maximum where
  both exist; where billing answers «no rows», print UNAVAILABLE and say the figure is
  a lower bound. One-sided prints are the bug, not a fallback.
- (c) Attribution: the step print decomposes billing by kind — `pods`,
  `network-volume`, `serverless` are already enumerated in `billing_since`
  (`scripts/runpod_guard.py:105`) — and the volume's line is named separately, never
  inside a probe's figure. (Today's lesson: the «$0.4396 step» was ≈$0.29 of probe +
  ≈$0.15 of volume rent.)
- (d) A step can be CLOSED: a closing entry appends the settled figure and its
  decomposition; a closed step prints «closed at X», never a live delta that grows at
  the volume's rate forever. Close `probe-b`'s step this way (append-only; its anchor
  keys are untouchable) — the guard then stops shouting a false cap breach.
- Every new refusal/behaviour gets a test in BOTH directions; every moved constant gets
  the test that reds if it moves back.

## Verify (evidence, not assertions — paste command + output in the report)

```
make check                      # green, count stated
ruff format --check .
python3 scripts/runpod_guard.py                      # says: phase 4 closed
python3 scripts/runpod_guard.py --step probe-b --step-cap 0.35
                                # says: closed at <X>, decomposition by kind, no breach
<negative controls of the D2 landing, as fix-c showed them>
```

## Report

`docs/reports/cycle2-money.md` (path-only in chat): what moved, numbers BY ARTIFACT
PATH, a Deviations section — every departure logged with a `[cause: …]` tag, silence
is not compliance — and a five-line Process signals section. Before writing code,
read back in one line each: the six landing parts, the anchor threshold, the two step
readings.

## DO NOT

- Never edit `docs/STATUS.md`, `docs/SPEC.md` (outside the D2 marked block),
  `docs/PROMPT-*.md`, `docs/PRODUCT.md` — team-lead files (File ownership); commit yes,
  edit no.
- No cloud resource creation of any kind; reads are unlimited.
- No regeneration or re-pinning of ANY sealed record or `spend_*.json` anchor —
  append-only where this contract says so, MOVED manoeuvres everywhere else.
- No reader / r1 / census / dashboard / collection changes — that is `reader-v3`'s
  contract, not this one.
- Never `git add -A`; stage by path.
