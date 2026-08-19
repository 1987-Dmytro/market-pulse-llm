# PROMPT — boot-debloat: everything evicted lives somewhere better, and the target is re-registered from the measured floor

**The joint sitting happened 19.08 (docs/STATUS.md, «День 19.08»). Operator
ruling: ALL FIVE groups of the labels-boot-audit tables go — A (record/lesson
duplicates), B (prose copies of numbers that have producers), C (the day
summary in hot.md's header), D (CLAUDE.md sections into `paths:`-scoped
rules), E (the Dev Stack section leaves `~/CLAUDE.md`). The boot-tax target is
re-registered by the PRE-REGISTERED FORMULA: `TARGET_KTOK` := the measured
post-debloat floor × 1.1, rounded to one decimal — the number is written at
the END, from the measurement, never before it. $0, no cloud call.**

**Baselines (19.08 afternoon, regime: measure and name, never silently fix):**
`knowledge/hot.md` 24 662 B; census 13.2K; `./CLAUDE.md` 6 999 B ·
`~/.claude/CLAUDE.md` 1 974 B · `~/CLAUDE.md` 350 B; `.claude/rules/` = 3
files, all with `paths:`, 0 in census; suite 2 966 / 2 skipped; porcelain:
M docs/STATUS.md · M knowledge/daily_logs/2026-08-19.md · M knowledge/hot.md ·
M knowledge/index.md (+ ?? this PROMPT once written). `grep -rln
'Bun|Foundry' Projects/*/CLAUDE.md` finds NOTHING outside `~/CLAUDE.md` —
the parked stack has no visible consumer today.

## Step 0 — the tail

1. Vault tail, its own commit: `knowledge/daily_logs/2026-08-19.md`,
   `knowledge/index.md`, `knowledge/hot.md` (the PREVIOUS session's `/save`
   curation — inherited tail, not this contract's work; D1 builds on top).
2. Team-lead files, verbatim, their own commit: `docs/STATUS.md` (the sitting
   ruling) + `docs/PROMPT-boot-debloat.md` (this contract).
3. A porcelain path neither list explains: STOP and report.

## Step 0.5 — debts of the accepted labels-boot-audit (small, named, first)

- `tests/test_validate_pass1_labels.py`, freeze test: assert the provenance
  record's four `file` paths ARE the expected four paths (the reviewer's
  CONFIRMED gap: a record pointing its blocks at other files passes today).
- `scripts/context-census.py` `loaded_memory`: match `String.trim()` rather
  than `str.strip()` — strip the JS WhiteSpace/LineTerminator set (incl.
  U+FEFF) and NOT the code points JS keeps (U+0085, U+001C–U+001F); add one
  guard test with a BOM'd fixture (the reviewer's CONFIRMED divergence).

## D1 — hot.md: groups A + B + C leave, by the vault-dream discipline

- **A (11 blocks):** МЕТКИ · ПАК ДЕТЕРМИНИРОВАН · ЭКЗАМЕН ВЫНЕСЕН · ЧТО
  ПРОВАЛИЛОСЬ · ГАРД УМЕЕТ КОНЕЦ ОКНА · ИДИОМЫ · ТРАНСПОРТ ПРОХОДА-1 · ОДИН
  ФЛАГ — ДВЕ КОМАНДЫ · РЕГИСТРАЦИЯ — ВХОД · суита-в-worktree · ПРОДЮСЕР — НЕ
  ВЕРИФИКАТОР. **B (4):** ДЕНЬГИ СЕЙЧАС · Деньги — три числа · ПРЕФЛАЙТ ·
  Карта RTX 4090/цены. **C:** the day-summary sentences inside
  `**Last update:**` (attribution line stays).
- **No home, no eviction — and a home is READ, not grepped** (vault-dream
  Dv529): for every block, open the passage in the home the audit table names
  and confirm it states the block's content, not its name. A block whose home
  fails that reading STAYS, and the report says which and why.
- Replacement: ONE pointer line total («вытеснено 19.08 → mapping-таблица в
  docs/reports/boot-debloat.md»), not one per block. The report carries the
  mapping table: block → home file:line.
- UNTOUCHED, byte-intact: all 7 blockers · ТЫ ЗДЕСЬ · ЦЕНА ПРОХОДА-1 · Ячейка
  ценза · both sealed literal blocks (nine tests in
  `tests/test_volume_calc_5c1.py` grep this file — run them right after the
  edit) · AUTO-GEN region · Next/долги · Footguns headers.

## D2 — ./CLAUDE.md sections into `paths:`-scoped rules

- Move: `## Code map` → `.claude/rules/code-map.md` with `paths:` covering
  `src/**` + `tests/**`; `## Harness plumbing` → rule scoped to `.claude/**` +
  `scripts/brain-*`; the collector-scoped Pitfalls sentences → the rule whose
  paths cover the collector scripts they describe; `## graphify` → fold into
  `knowledge/runbooks/tooling.md` (its pointer line already exists) keeping
  only the one-line trigger in CLAUDE.md. Follow `_TEMPLATE.md`'s frontmatter.
- What stays in ./CLAUDE.md: identity, Where the truth lives, File ownership,
  Rules, Second brain, Stack & commands, the Tooling pointer. ≤200 lines
  after, and every moved section verified reachable (open one rule file, show
  its `paths:` matches the files it teaches about).

## D3 — `~/CLAUDE.md`: the Dev Stack section is PARKED, not deleted

Cut `## Dev Stack` from `~/CLAUDE.md` and park it VERBATIM at
`~/dev-stack-parked.md` — a file nothing loads (no `@import` anywhere may
point at it; grep to prove). The grep above shows no project references
Bun/Foundry in its CLAUDE.md today; the operator re-homes the parked file
into specific projects if one ever needs it. `~/CLAUDE.md` keeps everything
else byte-for-byte. This file is OUTSIDE the repo — like MEMORY.md in
vault-dream, snapshot it (path + sha) before the first edit and show the
after-state beside it.

## D4 — the target, from the measurement (LAST, after every move above)

- Run `python3.11 scripts/context-census.py` three times, same invocation;
  the reading is the floor (they must agree; a spread is a finding).
- `TARGET_KTOK` := floor × 1.1, one decimal (pre-registered formula, sitting
  19.08). Update the constant, its docstring (suspension ENDS here — say the
  ruling and the formula), and the pin in `tests/test_context_census.py`
  (`== 9.0` becomes the new number) — SAME commit, moved-constant discipline.
- ADR in `knowledge/decisions/` + INDEX: the sitting's ruling (groups A–E,
  who ruled, the formula, the measured floor, the registered number) — this
  ADR is what un-suspends the target that
  `boot-tax-target-suspended-and-the-census-axis.md` suspended; link them.

## Verify (paste outputs, `python3.11` throughout)

```
scripts/context-census.py       # BEFORE step 0.5 · after D1 · after D2+D3 · the 3x floor of D4
make check                      # green at every commit boundary; final count named (2 966 + your new guards)
python3.11 -m pytest tests/test_volume_calc_5c1.py -q     # right after the hot.md edit, then covered by make check
python3.11 scripts/check-wikilinks.py                     # 0 broken, including the ADR and the pointer line
wc -l CLAUDE.md                 # ≤200; wc -c on all three CLAUDE.md + hot.md, before/after
git status --porcelain          # only the Stop-hook tail; name it
```

## Report

`docs/reports/boot-debloat.md`, path-only in chat. Deviations from **Dv537**,
closed enum v2, trailing `[[wiki-name]]`. Five-line Process signals. Read back
first, one line each: no-home-no-eviction (a home is read, not grepped); the
one-pointer-line rule; what in hot.md is untouchable; the D4 ordering (number
from measurement, LAST) and both files the new TARGET_KTOK lands in; the
parking rule for `~/CLAUDE.md` (verbatim, nothing loads it, snapshot first).

## DO NOT

- Blockers, ТЫ ЗДЕСЬ, ЦЕНА ПРОХОДА-1, Ячейка ценза, sealed literal blocks,
  AUTO-GEN, Next/долги — byte-intact. `MEMORY.md` untouched (its own law).
- `docs/labels-pass1-r1.jsonl`, the pack pages, `results/*.json` records —
  untouched (pinned; preflight digests must match after as before).
- No wholesale rewrite of any file: section-scoped moves, verbatim content.
- Team-lead files (docs/STATUS.md, docs/SPEC.md, docs/PROMPT-*): commit
  verbatim, never edit. Never `git add -A`. No cloud calls, no money.
