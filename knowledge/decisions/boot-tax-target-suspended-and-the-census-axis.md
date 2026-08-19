---
type: decision
date: 2026-08-19
status: accepted
tags: [decision, brain, boot-tax, census, hot-md, ruling, memory]
---

# The ≤9K boot-tax target is SUSPENDED, and the census moves onto the loader's axis

**Operator ruling 2 of 2026-08-19**, registered in `docs/STATUS.md` («День 19.08 — два рулинга») and
executed by `docs/PROMPT-labels-boot-audit.md` D2/D3. This record is the English long form.

## What forced it

`vault-dream` consolidated the executor's `MEMORY.md` 197 → 147 lines with a proven durable home
behind every evicted pointer, moved the boot tax 14.5K → 13.1K, and then showed — from an
inequality computed BEFORE the cut, not from a post-mortem — that the registered ≤9.0K target was
not reachable from inside that contract's scope:

> The census budget for ≤9.0K is **36 000 B**. Out of scope: three `CLAUDE.md` = **9 323 B**. In
> scope but rate-limited by the contract's own rule for it: `knowledge/hot.md`, which ended at
> **24 532 B**. That is **33 855 B = 8.46K before MEMORY.md contributes one byte**, so ≤9.0K needs
> MEMORY.md ≤ **2 145 B** — about 16 index lines out of 185 entries, a 91% eviction that the
> no-home-no-eviction law forbids. To reach 9.0K with MEMORY.md where it now stands, `hot.md` would
> have to fall to **8 230 B, −66.5%**.
> — `docs/reports/vault-dream.md`, «Step 1 — the constants»

Two thirds of the live-state file is not a consolidation, it is a decision about what the project
stops keeping in front of itself. That is not an executor's call.

## The ruling

1. **The target ≤9K is SUSPENDED**, not moved and not missed. `knowledge/hot.md` is NOT cut to hit
   a number.
2. **It is re-registered from the measured high-signal floor at a JOINT SITTING** with the operator
   — the floor being what live state actually costs once everything with a durable home elsewhere
   has been classified as a candidate to move.
3. **The three `CLAUDE.md` (9 323 B) enter the de-bloat scope.** They were out of scope for
   `vault-dream` and they are a quarter of the remaining budget.
4. **Until the re-registration, the census warning «> 9.0K» reads «the target is on
   re-registration»** — it is not a standing failure and no contract is judged against it.
5. **The census axis becomes the loader's** (Dv526), which is a separate defect that the same
   contract fixes.

## The axis (Dv526)

`scripts/context-census.py` counted the MEMORY.md share as `min(st_size, 25 * 1024)` UTF-8 bytes.
The loader that actually reads the file trims it, keeps **200 lines** (`vee`), then caps **25 000
UTF-16 code units** (`dde`, compared against `String.length`) cut back to the last newline at or
before the cap — constants re-derived from the binary in `docs/reports/vault-dream.md`. Two units
and two numbers, either of which could be wrong in the direction that hides tax.

`loaded_memory()` now models that and returns the loaded text's BYTE length, because bytes are the
unit the census sums: returning units would be the same defect pointing the other way. The measured
move is **−1 B** (18 587 → 18 586, the trailing newline the trim takes), because today's file is
under both caps — an expected ≈0 that was predicted before the run rather than explained after it.
`TARGET_KTOK` and the warning text did not change, and `tests/test_context_census.py` pins 200 /
25 000 / 9.0 with the truncation semantics driven on synthetic content over both caps
([[a_moved_constant_fails_green]]).

## What the sitting starts from

The audit prep is a **table**, not an edit: every block of `knowledge/hot.md` with its bytes and a
class — hot (live state) or cold-candidate with its durable home NAMED — plus the same one-line
treatment for the three `CLAUDE.md`. It is in `docs/reports/labels-boot-audit.md` («D3 — the audit
prep»). No row of it recommends an eviction; classification is the executor's work and the decision
is the sitting's.

The mechanism the sitting can spend is already proven in this repo: `.claude/rules/*.md` holds
**22 629 B** that costs **0** at boot, because all three files carry `paths:` frontmatter and load
only when a session touches the paths they scope.
