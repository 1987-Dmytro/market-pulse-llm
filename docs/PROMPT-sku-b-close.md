# PROMPT-sku-b-close — bar 2 scored by the team lead; the pilot closed ($0)

> Authority: SPEC §3.17 (6)–(12); the prereg's bar-2 procedure (the
> team-lead read of the per-position dump against the page images at
> acceptance, SPEC §10). The read is DONE — 2026-08-12, all 61 pairs
> against all 22 page images. This contract applies the dictated
> verdicts mechanically, finalises the verdict record, and records the
> pilot's closure. $0, local, no paid calls.

## The team lead's verdicts (the authoritative dictation)

**Result: 20 of 61 correct = 0.3279 vs 0.80 — FAIL.** A pair is keyed
`(file, price_promo, price_old)`; `n` = how many dump rows carry that
key (duplicates share one physical price box and one verdict);
`printed_old` = what the page actually prints where the pair is wrong.

| file | promo | old (dump) | n | verdict | printed_old |
|---|---:|---:|---:|---|---:|
| …4341.jpg | 37.9 | 75.9 | 1 | correct | |
| …4341.jpg | 131.5 | 264.5 | 1 | wrong | 264.90 |
| …4343.jpg | 17.9 | 29.9 | 1 | correct | |
| …4344.jpg | 27.9 | 39.99 | 1 | wrong | 39.90 |
| …4350.jpg | 49.9 | 71.9 | 1 | wrong | 71.50 |
| …4352.jpg | 12.9 | 19.99 | 1 | wrong | 19.90 |
| …4352.jpg | 30.9 | 44.9 | 1 | wrong | 44.40 |
| …4360.jpg | 21.9 | 40.9 | 1 | correct | |
| …4360.jpg | 23.5 | 42.5 | 2 | wrong | 42.90 |
| …4360.jpg | 42.9 | 80.9 | 1 | correct | |
| …4360.jpg | 24.9 | 46.9 | 1 | correct | |
| …4360.jpg | 29.9 | 55.9 | 1 | correct | |
| …4381.jpg | 74.5 | 149.0 | 1 | wrong | 149.50 |
| …4381.jpg | 99.5 | 199.0 | 1 | wrong | 199.90 |
| …4382.jpg | 24.5 | 49.0 | 2 | correct | |
| …4382.jpg | 39.5 | 79.0 | 2 | wrong | 79.90 |
| …4383.jpg | 13.9 | 19.9 | 1 | correct | |
| …4383.jpg | 119.9 | 159.9 | 2 | correct | |
| …4384.jpg | 15.5 | 26.75 | 2 | wrong | 26.80 |
| …4385.jpg | 59.9 | 89.9 | 2 | wrong | 89.40 |
| …4385.jpg | 59.9 | 90.0 | 1 | wrong | 90.70 |
| …4385.jpg | 68.9 | 103.0 | 1 | wrong | 103.70 |
| …4402.jpg | 46.9 | 79.9 | 1 | correct | |
| …4403.jpg | 79.9 | 111.9 | 1 | correct | |
| …4404.jpg | 11.7 | 17.7 | 1 | wrong | 17.80 |
| …4404.jpg | 20.5 | 29.5 | 1 | correct | |
| …4404.jpg | 26.9 | 39.9 | 1 | wrong | 39.70 |
| …4404.jpg | 26.5 | 39.9 | 1 | wrong | 39.80 |
| …4404.jpg | 15.9 | 22.9 | 1 | correct | |
| …4404.jpg | 119.9 | 171.9 | 1 | wrong | 171.30 |
| …4426.jpg | 103.9 | 230.0 | 3 | wrong | 230.90 |
| …4427.jpg | 17.9 | 35.0 | 1 | wrong | 35.80 |
| …4427.jpg | 22.3 | 44.0 | 1 | wrong | 44.90 |
| …4428.jpg | 25.5 | 37.0 | 2 | wrong | 37.90 |
| …4428.jpg | 117.9 | 157.0 | 2 | wrong | 157.90 |
| …4440.jpg | 64.5 | 93.0 | 3 | wrong | 93.90 |
| …4468.jpg | 18.3 | 40.0 | 1 | wrong | 40.90 |
| …4468.jpg | 26.5 | 58.0 | 1 | wrong | 58.90 |
| …4468.jpg | 36.3 | 80.0 | 1 | wrong | 80.90 |
| …4470.jpg | 16.9 | 29.99 | 1 | wrong | 29.80 |
| …4471.jpg | 28.9 | 41.99 | 2 | wrong | 41.90 |
| …4508.jpg | 29.9 | 55.9 | 2 | correct | |
| …4508.jpg | 21.9 | 36.9 | 2 | wrong | 36.50 |
| …4508.jpg | 24.9 | 46.9 | 1 | correct | |
| …4508.jpg | 22.9 | 41.9 | 2 | correct | |

Checksums the applier MUST assert: keys 45, rows Σn = 61, correct rows
= 20, wrong rows = 41, every jsonl pair-row matched exactly once, and
`accuracy = 20/61 = 0.327868…` (report to 4 dp: **0.3279**).

**The diagnosis line to carry verbatim into the record and the ADR:**
promo price 61/61 correct · printed % 61/61 correct · crossed-out old
price 20/61 — every error is confined to the small struck-through
number (superscript kopiyky garbled, truncated to .0, or digit-shifted),
and depth() is wrong wherever the old price is.

## Read-back check — FIRST lines of the report

The FOUR deliverables one line each, then the three bar verdicts in
one line, then "no paid calls in this contract".

## Deliverables (four)

1. **The applier** `scripts/apply_sku_pair_verdicts.py` (the dictated-
   verdicts pattern of `apply_dictated_verdicts.py`): carries the table
   above as its own data, writes `results/sku_b_pair_verdicts.json`
   (keys, per-key verdicts and printed_old, the checksums, the
   diagnosis line, provenance via `git_state`), and REFUSES on any
   checksum miss or an unmatched/doubly-matched row. Tests drive a
   passing apply and each refusal.
2. **The verdict record, finalised.** `scripts/sku_bar_verdicts.py`
   learns to consume `results/sku_b_pair_verdicts.json` (path pinned by
   sha inside the record it writes): bar 2 becomes
   `0.3279 vs 0.80 — FAIL (n=61, read by the team lead 2026-08-12)`;
   bars 1 and 3 unchanged; the record's `closure` block states the
   registered consequence verbatim: two bars failed → **B closes as
   "instrument not ready" BY MEASUREMENT** (attempts.on_failure).
   Re-written `results/sku_bar_verdicts.json` in its own commit.
3. **ADR** `knowledge/decisions/sku-b-pilot-closed-by-measurement.md`
   \+ INDEX: the three bars with their numbers; the diagnosis (big
   text perfect, small struck text 33%; under-reading never invention —
   precision 0.93, empty-gold probe clean, bar-3 misses all downward;
   the gold-vs-instrument mismatch on bar 1 — brands VISIBLE vs
   positions EXTRACTED; the asterisk/superscript family; the probe
   lessons 1.44/5.08/14.81/4.02); the program's cost $0.62 over three
   sessions and what each stop bought; the named post-pilot revision
   candidates (two-stage OCR read — operator's 2026-08-10 idea; a
   brands_visible side-channel so bar and instrument measure one
   thing; the superscript/asterisk parser family) — CANDIDATES, not
   commitments: the revision decision is the operator's at the 5c2
   briefing. English.

4. **Depth-from-percent, measured on what is already bought ($0).**
   The pilot's finding: the printed `-N%` badge reads 61/61, the
   crossed-out old price 20/61 — so question 7's depth may not need
   the old price at all. `scripts/measure_depth_from_pct.py` computes,
   for each of the 61 pairs: `true_depth` from the TEAM LEAD's
   printed_old (for correct pairs the dump's old IS the printed one)
   and the promo; `badge_depth = discount_pct_printed / 100`; and
   `delta = badge_depth − true_depth`. Writes
   `results/sku_depth_from_pct.json`: per-pair rows, the median and
   max |delta|, counts within 1 pp and 2 pp, and a plain reading line
   ("the badge is/is not an adequate depth instrument for a weekly
   median"). No threshold is registered — this is a measurement FOR
   the B′ design session, not a bar. Tests over the arithmetic.

Tests + `make check` green; the per-commit checkout table; Deviations
**Dv181+**; report appended as `## Close` to
`docs/reports/sku-b-v4-run.md` (own commit); chat gets ONLY the path.

## Do NOT

- No paid calls, no RunPod resources.
- Do not touch the dump, the run records, the registrations, the
  sealed pairs — the verdicts file is a NEW artifact beside them.
- Do not edit `docs/STATUS.md`, `docs/SPEC.md`, `docs/PRODUCT.md`,
  `docs/PROMPT-*.md` — team-lead files; commit-only.
- Never `git add -A`; vault tail → its own final commit.
