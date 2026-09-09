# PROGRESS — promo-pulse-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines; §8 of the phase file stays the DONE list)

## Done — 09.09 s42 «c3» (PAID, ruling (jj) item 4): the leg is BOUGHT, settled $0.2577 of the $0.80 cap; the line is OPEN
FRESH process, `bypassPermissions` stamped and read by §0's gate 1. Start ritual: no team-lead file was modified; the three
hook-touched `knowledge/` files by path (`58bb4e7`), then «next: c3» into this file by path (`b48431d`) as (jj)4 asks.
**Pre-flight at $0 before the anchor:** the four §1 inputs on disk, the three c3 outputs absent, the cloud proven empty
(`serverless []`, the two pre-existing templates, `pod list -a []`, volume `qw4nwleanc` as positive control). **§0** ONE chain: `MODE bypass` · `HARNESS FIELDS OK` · `REMAINING $1.4373` → **`CAP 0.80`** (room
$1.1373, so the operator's ceiling binds, not the room). **§1** in the same call: rung 0 **FITS at the dear corner $0.1864
(−76.7%)**, `promo-c3` anchored at $5.92 (16:26:09Z), registration + ledger committed `41406b3`.
**§2** T `c5vsl0pz4t` → E `mjnctafh13ausp` (ADA_24, workers-max 1, idle 60, exec 900, flash-boot, `qw4nwleanc`, EU-RO-1); the
endpoint create was gated on the TEMPLATE LISTING, so s41's propagation lag could not bite. **§3** detached, one call, pid 1903,
`--cap 0.80` read back off the committed registration; `ps -o args=` named it ALIVE.
**The record is COMPLETE:** `queued` 30 pages / 8 posts, `pages_bought 30`, `pages_left 0`, `unbought` 0/0, `stopped false`;
two leaflet packs 14 + 16 = **30 pages, 57 positions (28 + 29), 0 unreadable**; the text pack 8 asked / 8 read / 0 positions /
8 empty — in family with C2, whose text leg wrote 0 positions on 8 of its 16 channels. Wall 1115.5 s, 6 calls, one worker.
**§4** teardown proven by listing (endpoint gone, templates back to the two, volume intact, `pod list -a []`), then the post-run
`--note` with the counts DERIVED from the record: **`PROMO-C3 SPENT $0.2272 of $0.80`** (16:46:25Z), `REMAINING $1.2101`.
Record + log + ledgers committed `bc2a0f3`. **`make check` GREEN at `bc2a0f3`: ruff clean, 4326 passed / 2 skipped (11:48)** —
the same count as s41, so the leg's new result files moved no test; the commits after that reading touch only this PROGRESS file.
**Measured, not priced:** the page leg ran **19.828 s/page** against the dear corner's 3.369 — 5.9× — and still fits because
the CAP, not the projection, bounds it; the room gate re-priced after pack 00 ($0.333 → $0.2464) and bought the 16-page
remainder at its OWN measured rate ($0.0973).

## §5 — the close REFUSED FOUR times at $0, writing nothing: three on the WALK, then ONCE ON THE BAND
17:18Z and 17:31Z: `the billing walk ... answered «no billing rows yet» and covered 0 ms ... no settled figure to close on` —
the runbook's own retry, not the band. The CYCLE-3 walk read fine in the same output, so billing worked; RunPod simply emitted
no rows for the window since 16:26:09Z until ~17:56Z, 70 min after §4 against the runbook's 30–40 — the lag itself is a finding.
**17:56Z the walk settled and the SECOND gate refused:** `promo-c3 settles at $0.257668 against its own recorded reading of
$0.227200 — 13.4% off, outside the registered tolerance of 5.0%. NOT closed`. `shut` is None before the write: the ledger still
carries only its single §4 entry, the line is OPEN, and the volume is NOT deleted.

## Next — the team lead's ruling on the band (below), THEN the close, THEN the volume
**next: the ruling.** With it: `--close --until <iso> --tolerance 0.05 --note "c3 closed"`, read-only walk first; then
`network-volume delete qw4nwleanc` + the listing; then `make tick --window all` (the default is `w2`) and `make promo-screen`.
Then «chain-fold» ($0) → clean-clone e2e + `draw_truth_20` → the gate 12.09.

## Open stop — §5 REFUSES ON THE BAND: settled $0.257668 against a recorded $0.227200, 13.4% off a 5.0% tolerance
**Stop-point.** Measured at 17:56Z, no longer a forecast. The settled figure is `step resources $0.2577` = `pods $0.0305` +
`serverless $0.2272`, the volume $0.0000 and outside it by construction. §4's recorded reading of **$0.2272 equals the
serverless kind EXACTLY**: at 16:46 the balance had absorbed that charge and not yet the $0.0305 of `pods`, so the reference is
not merely stale — it MISSES A WHOLE BILLED KIND, and `off` is that kind divided by the rest, 0.0305 / 0.2272 = 13.4%.
**Question, which is not mine to answer:** a 5% RELATIVE band cannot grade a $0.23 leg — 5% is $0.0114 while one late-landing
billing kind is $0.0305; C2 drifted 2.73% and 1.29% on comparable absolute cents only because its spend was large enough to
absorb them. Is the ruling (a) an absolute floor beside the relative band for small legs, (b) §4's post-run reading re-taken
AFTER the walk settles — an ordering change to PROCESS «Closing a line», and it does move the gate's own reference — or (c)
something else? Widening `--tolerance` and appending a second `--note` are both the guard bypassed; neither is mine to do.
**Tree at 17:57Z:** clause (l)'s porcelain over its seven paths EMPTY; `make check` green at `bc2a0f3` (4326 passed / 2
skipped), and every commit after that reading touches only this file. No pod and no endpoint — both deleted and proven by
listing; templates back to the two pre-existing. Step line `promo-c3` OPEN with its single §4 entry. Volume `mp-srv2`
(`qw4nwleanc`) ALIVE and waiting on the close at ≈$0.24/day. REMAINING **$1.1699**; the leg itself cost $0.2577 of the $0.80 cap.
## Named, not built (the phase file forbids adding what it did not ask for)
- **The measured/priced gap above is a finding, not a fix:** 19.828 s/page vs the registered 3.369. No threshold is introduced.
- **(jj)3's two nits stay folded into «chain-fold»** as ruled — §3's `export …=$(…)` masking the substitution status and the
  `--endpoint`/`-T` placeholders. I substituted both by hand from the create output and gated the endpoint create on the listing.
- Carried unchanged from s41: `promo_projection_c2.json` is not reproducible from its producer (proved by its pin); no test
  asserts `cap_from`, `{leg}` or the `{STEP}-s4` contract; `tick.py --window` stays `w2`; `tooling.md`'s «plugin disabled», the
  unfloored arm selector, `graded()`'s `rows`, P1/S2/README untested in the tick, the ties.
