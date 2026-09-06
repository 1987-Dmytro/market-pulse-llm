# PROGRESS — promo-pulse-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines; §8 of the phase file stays the DONE list)

## Done — 06.09 s34 «p1-prep» ($0, ruling (bb) addendum (b)): the close, the holdout-3 draw, P1 + its ONE test, the $0 table — and the table says RETURN
**Start ritual.** (bb) + addendum, PHASE v18, PROCESS «the paid command is pre-authorised and proven at $0», stop-patterns §5, STATUS 20:15 committed by
path (`5d724d7`); s33's knowledge checkpoint by path (`556bcac`). **`promo-holdout2` CLOSED (`1a0d503`):** read-only walk FIRST (`--until
2026-09-06T17:30:00Z`: pods $0.4009 at the walk), then `--close --tolerance 0.05 --expect-ms 2116000` → **settled $0.4253** (pods; 3.6 % off the
post-run reading $0.4107, the walk complete over the 2116 s) — the session's ONE ledger line. Guard: **CYCLE 3 SPENT $7.8822 of $10.00** (balance
delta; billing $7.8724), **REMAINING $2.1178**; `pod list -a` [].
**(2) Holdout-3 DRAW (`7a2bf3d`):** `results/promo_threads_draw_3.json` — seed 42 over draw-2's `eligible_after` 398 MINUS holdout-2's 40 = **358**
(re-derived in the transcript: draw-2's `eligible_after_ids_sha256` reproduces, draw-3's is that set minus the 40), 20/20 by stratum (pools 117 / 241),
disjoint from all 120 drawn, no paused channel, ranks spread (5–110, 6–239); K7 two runs byte-identical, sha `76435461…`. The producer: `--exclude-drawn`
repeats once per earlier draw; the record's `authority` / `ruling` / `already_drawn.rule` branch on the leg (`LEGS`, keyed by how many draws it excludes)
or the emitter REFUSES (§4 v8); draw 2 still rebuilds **byte for byte** (`567cb236…`, the sha the holdout-2 registration pins); the 7 draw tests green.
No gold — the team lead labels it BLIND; no reader opened its threads.
**(3) P1 (`4a27940`):** `src/market_pulse/promo_post.py :: apply(rows, thread, registry)` — pure, rows copied; exactly R1 / R2 / R3 of the addendum in
that order, a rewritten row carries `p1: [rules]`. Owner = the `official_retail` source listing the channel (`Varus`); an aggregator's retailer = the ONE
alias-table chain the POST names (1-/2-grams through `registry.chain_spellings()`, edge punctuation stripped). Lexicon = the addendum's 11 phrases
verbatim, matched at a word start as a PREFIX (`прострочен` → «прострочений», `нема` → «немає») after `promo_key`. ONE test, both directions per rule,
on the real registry + aliases: **3 passed**.
**(4) The $0 table (`9b8a2de`; `results/grade_promo_p1_readings.json`, two runs byte-identical; `results/promo_p1_predicted_{dev40,dev2,dev3}.jsonl`;
`scripts/promo_p1_apply.py`), K8 v2 before → after over the SAME gold, draw arm and grader functions:**
| set | rows | subject before → after | signal | R1 · R2 · R3 | rewritten | hit-flips (the grader's own predicate) |
|---|---|---|---|---|---|---|
| dev-40 | 139 | **0.8857 → 0.8857** | 0.8667 = | 0 · 0 · 0 | 0 | none: no `post` ≠ root, no own-channel `post` with signals; 9 sku/brand + `жалоба`, none on the lexicon |
| dev-2 | 188 | **0.8883 → 0.9043** | 0.8296 = | 4 · 1 · 0 | 5 | 3 miss→hit; 2 miss→miss (gold `chain/izibank`, a partner row R1 cannot reach); 0 hit→miss |
| dev-3 | 112 | **0.7054 → 0.7500** (84/112) | 0.8021 = | 2 · 0 · 3 | 5 | 5 miss→hit, 0 hit→miss; currency 0.766 → 0.7872 · decimal_only 0.6615 → 0.7231 |
Signals unmoved on all three (the script refuses if they move). Leak check, in the record: holdout-3's 40 threads ∩ the 120 threads this reading opened
= ∅; the lexicon's sources — the codebook and the three DEV error tables — are sha'd there.
**Of the addendum's 8 reachable dev-3 misses P1 reached 5** (2 format + 3 store-stock). The 3 store-stock misses it did NOT reach, by the law as written:
`@msuaaaa:7627/7134` «В Чернівцях немає(» — `спрос` only, no `жалоба`, and the post names Аврора, not a registry chain; `@VARUS_channel:5119/5988`
«в нашем Варусе его … нет пока» — «нет пока» is not in the lexicon; `@msuaaaa:4588/2509` «термін придатності закінчується» — the lexicon phrase in
the other word order, and the post «Акції одного дня в 🥲😊» names its chain by an emoji. Not extended: a word enters the lexicon by a ruling.
**DECISION TABLE (PHASE v18 §6.2), evaluated in the record: `holdout3_shot: false` — dev-3 0.7500 < 0.80; dev-40 and dev-2 hold their bars →
«RETURN to the operator at $0».** `make check` at `9b8a2de`: ruff clean; pytest **4326 passed / 2 skipped in 698 s ≥ 4266** (4323 + the ONE test's 3), HEAD unmoved under the run.

## Next — the operator's word on the fork; no holdout-3 registration, no pod, nothing paid
The item ENDS at the table. A ruling that widens the lexicon or its matching (the three unreached misses are the evidence) is a ≤ 5-line change to
`STORE_STOCK_LEXICON` and a re-run of `PYTHONPATH=src python3.11 scripts/promo_p1_apply.py` (minutes, $0); the holdout-3 gold stays BLIND either way.
Then c3 (≤ $0.50, ruling (l) 2–4), the volume `mp-srv2` after the phase's last paid run.

## Open stop — the pre-registered fork RETURNS to the operator at $0 (PHASE v18 §6.2, the addendum's own rule)
Stop-point: the decision table says the holdout-3 shot is NOT bought — P1's dev-3 subject 0.7500 < 0.80 (dev-40 0.8857 / dev-2 0.9043 hold).
Question: which branch — (a) ship as measured: S2 red on subject (0.7500 with P1), green on signals; (b) codebook v1.3 + a new dev loop (a new money
cycle); or (c) a ruling on P1's lexicon / matching, re-read at $0 first? The executor takes none of them without the word.
Tree: HEAD `9b8a2de`, porcelain empty but the operator's untracked `Claude outputs/`; NO pod; `promo-holdout2` CLOSED $0.4253; cycle 3 REMAINING
$2.1178; holdout-3 drawn (`76435461…`), unlabelled, unregistered, its emitter leg not built.

## Named, not built (the phase file forbids adding what it did not ask for)
- PROCESS v2.3's «the paid command is pre-authorised in the harness and PROVEN at $0 in the prep session» — the allow rule for `runpodctl pod create …`
  in `.claude/settings.json` and the `--help` proof in runbook §0: the holdout-3 prep session's, not this item's.
- Draw 3 has no test of its own (K7, 358, disjointness and the ranks were shown, not asserted); the holdout-3 leg is not in the emitter (`--part
  holdout3`, its line, its files); R3's PREFIX matching is a stated choice the addendum did not spell out — an order-insensitive match is a ruling.
- Carried from s33, unchanged: the hard-stop edge in the guard's close; `committed_registration()` does not re-verify `pinned_inputs`; `-r2` re-points
  nothing; a cross-leg `--step`. ultracode ON (operator): every step ran by hand, no workflow was spent.
**No pin, guard or ledger was added; the ONE test is the addendum's; the draw producer changed only to take its paths as parameters.**
