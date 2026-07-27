<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-07-27 11:13:45 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
3abbc8c docs: track the confirmed brand watchlist
0e02ae2 docs: land SPEC rev. 3 and the CLAUDE.md fold-in
3bd01e4 docs: drop stale competitor references after the rev. 3 migration
146aa5c test: cover new registry validation
d36e211 feat: migrate registry to sources/taxonomy/watchlist schema
```

## 📅 Recent daily logs

- `2026-07-27.md`
- `2026-07-26.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->

# Hot Cache — curated

**Last update:** 2026-07-27 11:08 (edited by hand / `/close`; the section above is auto-generated — do NOT touch the marker)

## 🔥 What's Hot
SPEC Phase 2, step **2a (registry migration) delivered**: `config/registry.yaml` = sources +
taxonomy + watchlist, `registry.py` rewritten, 9 tests, `make check` green after each of the 5
commits. Awaiting operator acceptance — the executor never self-accepts a step.
Phase 1 acceptance is still open. SPEC rev. 3 is committed but its status line says DRAFT:
approval is the operator's to give.

## ⏭️ Next
- Operator closes Phase 1 and accepts step 2a.
- Step **2b**: Telegram entry check per channel — resolve each chain to its blue-check channel,
  confirm comments enabled + traffic, then flip `verified: true` in `config/registry.yaml`.
  Handles shipped today are candidates only; `varto` / `varus-pl` private-label naming is verified
  in the same pass.
- Then 2c/2d: collector (rate-limited, incremental, provenance), annotation guidelines, FROZEN
  test sets.

## 🚧 Blockers
- none

## 🐞 Known harness bug
`knowledge/templates/daily-log.md` hard-codes `2026-07-26` instead of `{{DATE}}` → every daily-log
stub the Stop hook writes is stamped with the wrong date. One-word fix, operator's call.
