---
type: decision
date: 2026-08-19
status: accepted
tags: [decision, brain, boot-tax, census, hot-md, claude-md, ruling, rules]
---

# The boot tax is de-bloated in all five groups, and the target is re-registered from the measured floor

**Operator ruling of the joint sitting, 2026-08-19**, registered in `docs/STATUS.md` («СОВМЕСТНАЯ
СЕССИЯ СОСТОЯЛАСЬ 19.08») and executed by `docs/PROMPT-boot-debloat.md`. This record is the English
long form, and it is what **un-suspends** the target that
[[boot-tax-target-suspended-and-the-census-axis]] suspended the same day.

## What the sitting was handed

Not a proposal — a table. `labels-boot-audit` classified all 24 807 B of `knowledge/hot.md` block by
block and all 9 323 B of the three `CLAUDE.md` section by section, `hot` against `cold-candidate`
with a durable home named in every cold row, and **recommended nothing**: what leaves live state is
the operator's call, and the executor's job was to make the call cheap to make.

## The ruling

1. **All five groups go.** **A** — record and lesson duplicates in `hot.md` (11 blocks). **B** —
   prose copies of numbers that have producers (4 blocks). **C** — the day summary inside
   `**Last update:**`. **D** — `CLAUDE.md` sections into `paths:`-scoped rules. **E** — the
   `## Dev Stack` section leaves `~/CLAUDE.md`.
2. **The target is fixed by a PRE-REGISTERED FORMULA, not by opinion**:
   `TARGET_KTOK := the measured post-debloat floor × 1.1`, rounded half-up to one decimal. The
   number is written at the END, from the measurement, never before it. The sitting's own
   projection (floor ≈9.6K → target ≈10.5) is a forecast and is not the registered value.
3. **No home, no eviction — and a home is READ, not grepped** ([[a-citation-is-not-a-record]],
   `vault-dream` Dv529): for every block, the passage in the home the audit table names is opened
   and must state the block's CONTENT, not its name.
4. **Untouchable**: the seven blockers, ТЫ ЗДЕСЬ, ЦЕНА ПРОХОДА-1, Ячейка ценза, the two sealed
   literal blocks `scripts/volume_calc_5c1.py` greps, the AUTO-GEN region, Next/долги. `MEMORY.md`
   is not touched at all — it has its own law.

## What it measured out to

| step | census | what moved |
|---|---:|---|
| before | 13.2K | — |
| after D1 (groups A+B+C) | 10.4K | `hot.md` 24 662 → 13 457 B (−11 205) |
| after D2 (group D) | 9.8K | `CLAUDE.md` 6 999 → 4 581 B, 115 → 80 lines; three new `paths:`-scoped rules |
| after D3 (group E) | **9.7K** | `~/CLAUDE.md` 350 → 23 B, parked verbatim at `~/dev-stack-parked.md` |

The floor is the census's own printed reading, taken three times on the same invocation and
identical every time: **9.7K** = 38 791 B (1 974 + 23 + 4 581 + 18 756 loaded `MEMORY.md` +
13 457 `hot.md` + **0** from `.claude/rules/`). So **9.7 × 1.1 = 10.67 → `TARGET_KTOK = 10.7`**,
and the census now prints `9.7Ktok boot tax` with no warning behind it.

The constant, its docstring, the module docstring's own hardcoded «9K» and the pin in
`tests/test_context_census.py` moved in ONE commit — a constant with two homes goes green while one
of them drifts ([[a-moved-constant-fails-green]]).

## What the discipline cost, and what it bought

One block **stayed** against the ruling's own list: the idioms card. Its home in the audit table was
«one memory lesson per idiom, all of them written» — a roster claim, which is the reading Dv529
refuses — and one idiom, «право исполнителя на отказ», is stated in no file in `knowledge/`,
`docs/reports/` or native memory. Fourteen of fifteen blocks evicted with `file:line` behind each;
the mapping table is in `docs/reports/boot-debloat.md`.

The mechanism the sitting spent was proven before it was spent: `.claude/rules/*.md` now holds
**25 730 B** on disk and contributes **0** to the census, because every rule carries `paths:`
frontmatter inside the 300 bytes the census reads and loads only when a session touches the files it
teaches about. Group E is the same idea one level up: a parked file is not deleted knowledge, it is
knowledge with no loader.

## What this record does NOT decide

`knowledge/hot.md` still carries, on the untouchable list, a Next item and a blocker that both say
«цель ≤9K ПРИОСТАНОВЛЕНА». They were true when they were written and this ruling ends the
suspension; correcting them is the next contract's edit, not this one's — named in
`docs/reports/boot-debloat.md` rather than fixed silently.
