# PROGRESS — promo-pulse-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines; §8 of the phase file stays the DONE list)

## Done — 09.09 s42 «c3» (PAID, ruling (jj) item 4): the leg is BOUGHT, $0.2272 of the $0.80 cap; the line is still OPEN
FRESH process, `bypassPermissions` stamped and read by §0's gate 1. Start ritual: no team-lead file was modified; the three
hook-touched `knowledge/` files by path (`58bb4e7`), then «next: c3» into this file by path (`b48431d`) as (jj)4 asks.
**Pre-flight at $0 before the anchor:** the four §1 inputs on disk, the three c3 outputs absent, and the cloud proven empty —
`serverless []`, templates the two pre-existing only, `pod list -a []`, volume `qw4nwleanc mp-srv2` (positive control).
**§0** from the runbook's own text, ONE chain: `MODE bypass` · `HARNESS FIELDS OK` · `REMAINING $1.4373` → **`CAP 0.80`** (room
$1.1373, so the operator's ceiling binds, not the room). **§1** in the same call: rung 0 **FITS at the dear corner $0.1864
(−76.7%)**, `promo-c3` anchored at $5.92 (16:26:09Z), registration + ledger committed `41406b3`.
**§2** T `c5vsl0pz4t` → E `mjnctafh13ausp` (ADA_24, workers-max 1, idle 60, exec 900, flash-boot, volume `qw4nwleanc`, EU-RO-1).
The endpoint create was gated on the TEMPLATE LISTING, so s41's propagation lag («Unable to find template») could not bite.
**§3** detached, one call, pid 1903, `--cap 0.80` read back off the committed registration; `ps -o args=` named it ALIVE.
**The record is COMPLETE:** `queued` 30 pages / 8 posts, `pages_bought 30`, `pages_left 0`, `unbought` 0/0, `stopped false`;
two leaflet packs 14 + 16 = **30 pages, 57 positions (28 + 29), 0 unreadable**; the text pack 8 asked / 8 read / 0 positions /
8 empty — in family with C2, whose text leg wrote 0 positions on 8 of its 16 channels. Wall 1115.5 s, 6 calls, one worker.
**§4** teardown proven by listing (endpoint gone, templates back to the two, volume intact, `pod list -a []`), then the post-run
`--note` with the counts DERIVED from the record: **`PROMO-C3 SPENT $0.2272 of $0.80`** (16:46:25Z), `REMAINING $1.2101`.
Record + log + ledgers committed `bc2a0f3`. **`make check` GREEN at `bc2a0f3`: ruff clean, 4326 passed / 2 skipped (11:48)** —
the same count as s41, so the leg's new result files moved no test. Clause (l)'s porcelain over its seven paths: empty.
**Measured, not priced:** the page leg ran **19.828 s/page** against the dear corner's 3.369 — 5.9× — and the leg still fits
because the CAP, not the projection, bounds it; the per-channel room gate re-priced after pack 00 (`room_usd_before 0.333` →
`room_usd_after_first_pack 0.2464`) and bought the 16-page remainder at its OWN measured rate ($0.0973).

## §5 — the close is REFUSED on the WALK (the runbook's own retry), THREE times, at $0 and writing nothing
17:18Z, 17:31Z and the read-only probes before them: `the billing walk over promo-c3's window answered «no billing rows yet»
and covered 0 ms ... there is no settled figure to close on`. Not the band — the walk. The CYCLE-3 walk reads fine in the same
output (`billing since $8.5627 (read)`), so billing works; RunPod has emitted no rows for the window since 16:26:09Z, 45+ min
after §4 against the runbook's 30–40. Nothing was written: `shut` is None before the write. The line stays OPEN, the volume
`mp-srv2` waits with it (~$0.24/day) and is NOT deleted until the close settles.

## Next — retry the close (read-only walk FIRST), then the volume; then «chain-fold»
**next: `runpod_guard.py --step promo-c3 --step-cap 0.80 --close --until "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --tolerance 0.05
--note "c3 closed"`**, read-only walk first, per §5. THEN `network-volume delete qw4nwleanc` + the listing, then
`make tick --window all` (the default is `w2`) and `make promo-screen`. Then «chain-fold» ($0) → clean-clone e2e +
`draw_truth_20` → the gate 12.09.

## Open stop — NONE YET, but §5's SECOND gate is predicted to refuse and no remedy is mine
The walk refusal above is the runbook's sanctioned retry, so nothing waits on a decision TODAY. Named before it happens, because
the team lead's line may be needed the moment the walk answers: §5 compares `off = |settled − recorded| / recorded` against
`--tolerance 0.05`, where `recorded` is §4's **$0.2272** — a BALANCE DELTA taken 20 min after the anchor, while the charge was
still landing. The delta kept climbing after it: 0.2272 → 0.2577 (17:02) → **0.2674** (17:07, 17:20, 17:31 — now stable), of
which ≈$0.009 is the volume's drip since the anchor, which `own_resources` leaves OUT. So settled ≈ $0.258 against a frozen
reference of $0.2272 → `off` ≈ 13–14%, outside 5%. The runbook's §4 ordering was built against the volume drip, which makes
`recorded` too HIGH; here the balance LAG dominates and makes it too LOW — the opposite sign, and a retry moves neither number.
Every remedy available to me is blocked: widening `--tolerance` is forbidden in the runbook's own words; a SECOND `--note` to
re-record the reference is moving the gate's own reference, i.e. the guard bypassed; waiting makes the volume's share grow.
This is a fork the phase file does not settle — if the walk answers and the band refuses, it is the team lead's ruling, not mine.
Tree: everything by path, clause (l) clean; no pod, no endpoint; step line `promo-c3` OPEN; REMAINING **$1.1699** (17:31Z).

## Named, not built (the phase file forbids adding what it did not ask for)
- **The measured/priced gap above is a finding, not a fix:** 19.828 s/page vs the registered 3.369. No threshold is introduced.
- **(jj)3's two nits stay folded into «chain-fold»** as ruled — §3's `export …=$(…)` masking the substitution status and the
  `--endpoint`/`-T` placeholders. I substituted both by hand from the create output and gated the endpoint create on the listing.
- Carried unchanged from s41: `promo_projection_c2.json` is not reproducible from its producer (proved by its pin); no test
  asserts `cap_from`, the `{leg}` string or the `{STEP}-s4` contract; `tick.py --window` stays `w2`; `tooling.md`'s «plugin
  disabled», the unfloored arm selector, `graded()`'s `rows`, P1/S2/README untested in the tick, the ties.
