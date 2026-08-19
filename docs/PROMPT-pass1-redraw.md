# PROMPT — pass1-redraw: a targeted r2 labelling pack from the dairy-signal threads

**Sitting-2 rulings, 19.08 (docs/STATUS.md «День 19.08»): the class deficit is
closed by WEIGHTING + a TARGETED RE-DRAW from dairy-signal threads (synthetic
only if the gate later runs red); two training arms (A = 500 weighted, B =
500 + re-draw). This contract builds the RE-DRAW PACK only — the paid
training registration is a separate later contract. The labels file it
commissions, `docs/labels-pass1-r2.jsonl`, is a TEAM-LEAD file from the
moment it exists (same law as r1). $0, no cloud call.**

**Baselines (19.08 evening; measure and name, never silently fix):** suite
2 967 / 2 skipped; census 9.7K under registered TARGET_KTOK 10.7; window-1
reader tract 129 threads / 1 032 payable / r1 drew 500 → **468 payable
remain**; r1 distribution: не_наш_рынок 251 · null 167 · сеть_ритейлер 44 ·
категория_личное 36 · молочный_бренд 2. Porcelain at issue time:
M docs/STATUS.md · M knowledge/daily_logs/2026-08-19.md ·
M knowledge/index.md · M knowledge/hot.md (hook/save tails) + ?? this PROMPT;
re-read at your step 0 — a path neither list explains: STOP and report.

## Step 0 — the tail

1. Vault tail, its own commit: `knowledge/daily_logs/2026-08-19.md`,
   `knowledge/index.md`, `knowledge/hot.md` (inherited tails only — your own
   hot.md edit is step 0.5's deliverable and rides with it).
2. Team-lead files, verbatim, their own commit: `docs/STATUS.md` (sitting-2
   rulings) + `docs/PROMPT-pass1-redraw.md` (this contract).

## Step 0.5 — debts of the accepted boot-debloat (own commit)

- **Dv541 sweep of `knowledge/hot.md`:** ONE curation edit that reconciles
  the file with the 19.08 outcome — the ⛔ BOOT TAX blocker becomes CLOSED
  (target 10.7 registered at `ab372c4`, census 9.7K, ADR
  `boot-tax-re-registered-from-the-measured-floor`), and any Next line still
  quoting the suspended ≤9K or the file's own pre-debloat size is updated.
  List every sentence you changed in the report. Sealed literal blocks and
  AUTO-GEN stay byte-intact; run `pytest tests/test_volume_calc_5c1.py -q`
  right after.
- **The three orphan lessons find homes:** write memory lesson files + index
  lines for `[[a-checker-whose-failure-is-silence]]` (mechanism: boot-debloat
  report Dv540 row) and `[[a-guard-that-runs-after-the-write]]` (Dv542 row);
  for Dv521, read `<memory>/cooccurrence_is_not_explanation.md` and ensure
  the 4.5g5 family-size mechanism (23 co-occurring vs 10 explained) is
  STATED in it — add it there if it only names the max() tie. After
  planting: both MEMORY.md axes must stay ≤75% (≤150 lines / ≤18 750); if an
  index line would cross the bar, plant the files, skip that index line, and
  name the debt in the report.

## D1 — the dairy-signal census (read-only, paste the table)

- A thread is a CANDIDATE if the shipped matcher finds a watchlist hit
  (dairy brand or category) in the thread's post or comments.
  `market_pulse.brands` is the ONE matcher (its docstring and
  `config/watchlist_rules.yaml`'s header say so) — use its DEFAULT matching
  (the mode every sealed record was measured under), record that choice.
  `brands.py`, `config/registry.yaml`, `config/lexicon.yaml` are pinned:
  READ, never edit.
- From the candidates subtract the 7 exam threads
  (`results/pass1_label_pack_r1.json` `exclusion.threads`). AVAILABLE = the
  candidates' payable comments minus the 500 r1 units (`units` of the same
  record) minus the 14 gold rows' units. Paste: candidate threads · payable
  in them · already-drawn · available, with the arithmetic line.

## D2 — the r2 pack (own commit)

- **A NEW producer**: `scripts/build_pass1_label_pack_r2.py` — CREATE it;
  `scripts/build_pass1_label_pack.py` is pinned by
  `results/pass1_label_pack_r1.json.producer.sha256` and may not change.
  Importing shared helpers is fine; copying and adapting is fine.
- Draw discipline as r1: `SEED = 20260819` module constant; per-thread cap =
  p90 recomputed on the CANDIDATE subset; **target = min(150, available),
  and reachability under the cap is computed and printed BEFORE the target
  freezes** (Dv520/Dv527: an absolute number needs a reachability state). If
  reachable < 150, the honest smaller number ships with its inequality.
- Machine record `results/pass1_label_pack_r2.json`, self-pinned like r1
  (producer sha, rendering sha); pack page `docs/label-pack-pass1-r2.md`
  rendered under the SAME codebook law: attribution law v5 by the same
  bytes from `prompts.py` + F2a carve-out + gold-r2 rulings, with the Dv519
  excision on its literal markers. The two page-guard classes r1 has (no
  gold ids · no bar figures) get equivalent tests for the r2 page.
- Contamination proofs as r1: gold rows/threads, probe units, and r1-unit
  overlap — each an EMPTY list printed, not asserted in prose.
- **The labels clause, learned from Dv531:** `docs/labels-pass1-r2.jsonl` is
  written by the TEAM LEAD after this contract. Tests may assert the pack
  record names it and, WHEN it exists, its validity — **never that it does
  not exist yet** (ADR `the-absence-test-is-a-clock-and-flips-with-its-
  artifact`). Extend or parallel `scripts/validate_pass1_labels.py` so the
  r2 file validates against the r2 pack (a new gate module is fine; the r1
  validator's constants are consumed by tests — enumerate consumers before
  touching anything shared). Red-first refusals for the r2 gate, green path
  on a synthetic file.
- Blind subset: NOT drawn for r2 (the operator's blind-40 option lives on
  r1; do not spend pack rows on it here).

## Verify (paste outputs, `python3.11` throughout)

```
make check                            # green; final count named (2 967 + your new guards)
python3.11 -m pytest tests/test_volume_calc_5c1.py -q     # right after the hot.md sweep
python3.11 scripts/build_pass1_label_pack_r2.py           # then re-run: same record sha twice (determinism)
python3.11 scripts/check-wikilinks.py                     # 0 broken — including the two new lesson files
wc -l -c <memory>/MEMORY.md           # both axes ≤75% after the plantings
python3.11 scripts/context-census.py  # paste; expected ≈9.7K ± the hot.md sweep's delta, named
git status --porcelain                # only the hook tail; name it
```

## Report

`docs/reports/pass1-redraw.md`, path-only in chat. Deviations from **Dv545**,
closed enum v2, trailing `[[wiki-name]]`. Five-line Process signals. Read
back first, one line each: what is pinned and therefore read-only
(`build_pass1_label_pack.py`, `brands.py`, both configs, the r1 record and
labels); the no-absence-assert rule for `labels-pass1-r2.jsonl`; the
reachability-before-target order; the one-edit budget for hot.md; where the
blind option lives (r1, not here).

## DO NOT

- Never edit: `scripts/build_pass1_label_pack.py`,
  `results/pass1_label_pack_r1.json`, `docs/labels-pass1-r1.jsonl` +
  `results/labels_pass1_r1*.{jsonl,json}`, `docs/label-pack-pass1-r1*.md`,
  `src/market_pulse/brands.py`, `src/market_pulse/prompts.py`,
  `config/registry.yaml`, `config/lexicon.yaml` — pinned or sealed; preflight
  digests must match after as before.
- No test may assert the absence of `docs/labels-pass1-r2.jsonl`.
- `knowledge/hot.md`: exactly the one step-0.5 sweep edit; sealed blocks and
  AUTO-GEN byte-intact. MEMORY.md: only the step-0.5 lesson plantings.
- Team-lead files (docs/STATUS.md, docs/SPEC.md, docs/PROMPT-*): commit
  verbatim, never edit. Never `git add -A`. No cloud calls, no money.
