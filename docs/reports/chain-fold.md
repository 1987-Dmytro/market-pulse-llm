# chain-fold — ONE Маркетопт on the screen and in P1 ($0, s45, PHASE-ship-1 §2 item 2)

## Answer
**Question (§2 item 2): does the screen carry ONE Маркетопт, and does the shipped number move when
it does?** — **Yes, and no.** `results/promo_screen_data.json :: screen.positions` = **1301** rows,
1301 distinct `(carrier, row_id)`; `chain.id == "marketopt_private"` = **0**; `marketopt_promo` =
**83** = 26 (w1's 4 post positions + w2's 22) + 57 (c3's w3) — ruling (oo) 2's number, measured on
the union the check runs on. Re-measured through the product's own functions
(`results/grade_promo_loop_readings.json`, two runs byte-identical): loop **dev40 0.8857 / 0.8667 ·
dev2 0.9043 / 0.8296 · dev3 0.7411 / 0.7937**; `grade_promo_p1_readings.json` dev3 0.7500 / 0.8021.
Every reading, stratum, miss and tie count is what it was — the only fields that moved in either
record are shas, because the rows moved surface form only (`"Varus"` → `"varus"`, `subject_id`
unchanged, `chain_key` folds both to `varus`).

## Evidence
- `673eb65` — `config/chain_aliases.yaml` gains a `chain_of_channel` section (`marketopt_private:
  marketopt_promo`), the flat map under `spellings:`; `registry.chain_of_channel()` beside
  `chain_spellings()`; `aggregates.chain_key` reads the channel map BEFORE the spellings, two
  separate lookups; `promo_post` R2/R3 write `chain_key(own.id)`; `promo_positions` emits
  `chain_key(ch.source_id)`, folded once into a local the row and the sort key both read.
- `6f4a682` — `make tick` ×2: `new 0` in all six tables, export sha unmoved (K10). Counts above.
  `named_by_amendment_3_20` false on all 83 (`tick.CHAINS` names neither Маркетопт).
  `draw_truth_20.py --json` → population 1301, `results/truth_20.json` BYTE-IDENTICAL `6958e002…`
  (it sorts by `row_id` before sampling). `make promo-screen` green; README's S2 block byte-identical.
  `promo_p1_apply.py` twice → identical shas; `p1.sha256` b2c0e2b9… → 74132120…;
  `promo_p1_predicted_dev40.jsonl` byte-identical (R2/R3 fired nowhere in it).
- `b6100ce` — (jj) 3's two runbook nits in `knowledge/runbooks/promo_c3_paid_leg.md` §3.
- Tests: ONE new, both ways (`test_promo_tables.py :: test_a_chains_second_own_channel_folds_…`) —
  the private channel IS the chain, every other own channel folds to itself, R2 lands on
  `marketopt_promo`; **negative control**: with `chain_of_channel` emptied the same calls return the
  split id again. `preflight` before the edit: `promo_post.py` pinned by the two readings records
  only, digests matched; `config/chain_aliases.yaml` pinned by nothing.

## Deviations
- `Dv1 [cause: contract-gap]` — `results/grade_promo_p1_readings.json` re-published though §2 named
  only the loop record: ONE producer writes both, no sealed record pins it (`preflight`: 0 pins),
  and stale against a P1 it no longer describes is worse. The bar's pre-registered readings untouched.
- `Dv2 [cause: process]` — three team-lead docs read with `sed -n` before I re-read §4.5. No refusal
  fired (the deny rules are Edit-only), nothing was written; the rest used the Read tool.
- Fork decided under §4 (not a stop, named in PROGRESS): the sidecar got **two named sections**
  rather than a reserved key inside the id namespace — `chain_spellings()` validates every top-level
  key as `id: [str]`, so a bare mapping there would raise. `test_promo_post.py`'s three `"Varus"`
  literals are the owner NAME that legitimately moved: rewritten to read the registry (fork (e), §4.4).

## Debts
- No validation guard on the map (§3 forbids adding one): nothing checks both sides are registry ids,
  or that a folded-FROM id is never a fold TARGET. Executor, ~10 lines, needs the team lead's word.
- The fold lives in `chain_key`, so EVERY `chain` subject folds through it, not only the screen and
  P1 that §2 names. Nothing is spelled with a channel id today; the reach is wider than the check.
- `promo_by_chain` / `coverage` keep raw `source_id` keys AND their own `WHERE window_id = ?` — they
  split Маркетопт where `positions` folds it. (oo) 3 gives both to «serve-loop»; w1 has none of the 57.
- A store row already written as «Varus» is not re-folded (`subject_id` unchanged, `INSERT OR
  IGNORE`). Invisible while `screen.feed` is empty; «s2-promote» is the first tick that writes signals.

## make check
`ruff check .` → `All checks passed!` · `pytest -q` in four slices (the suite is over one call's
ceiling): `930 passed` · `1279 passed` · `1114 passed` · `1010 passed, 2 skipped` = **4333 passed /
2 skipped** at `b6100ce` (4332 at `a7b9f74` + my one test). Porcelain EMPTY. **$0 this session.**
HEAD at writing: `3cc99adbe81ec4effcf238db39188ad6336df3b2`.
