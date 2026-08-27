# PROMPT — vault-dream: the executor's memory is consolidated, and nothing true is lost

**Pilot H5b (weekly retro 2026-08-18, docs/reviews/). Your own blocker, ruled by
the team lead 18.08: MEMORY.md sits at the loader's ceiling (your figure:
24 992 bytes / 197 of 200 lines) and the Dv519 lesson has no home. No ad-hoc
eviction — this contract is the fix. $0, no cloud call, no project code.**

**This runs IN PARALLEL with the team lead labelling
`docs/label-pack-pass1-r1.md`. The footprints are disjoint and must stay so —
see DO NOT.**

**Baseline:** `make check` **2 959 / 2 skipped** (team lead's own run, 18.08).

## Step 0 — the tail (checked against live `git status`: exactly these paths)

1. Vault tail, its own commit: `knowledge/daily_logs/2026-08-18.md`,
   `knowledge/index.md`.
2. Team-lead file, verbatim, its own commit: `docs/STATUS.md` (accepted
   pass1-data-prep, registered the blocker ruling) and
   `docs/PROMPT-vault-dream.md` (this contract).

## Step 1 — the constants, re-derived (H6)

- **The loader's ceiling** — open the loader that actually reads MEMORY.md and
  re-derive the line/byte limits from ITS constants; your blocker's «200 lines»
  is a claim to reproduce. Name MEMORY.md's real path in the report (it is
  outside the repo; the team lead's `find` proves the repo holds none).
- **The consolidation target** — headroom, not a squeeze: end ≤75% of the
  re-derived ceiling on BOTH axes (lines and bytes), formula printed.
- **Boot tax** — measured with `scripts/context-census.py` (the instrument the
  repo already owns) BEFORE any edit and AFTER the last one, same invocation,
  both outputs pasted. Registered baseline 19.1K tok; target ≤9K. If the target
  is not reached, the honest number ships with the gap decomposed by file — a
  missed target reported beats a reached one asserted.

## D1 ($0) — the dream pass (auto-dream mechanics, ACE discipline)

- **MEMORY.md**: merge and prune by SECTION-scoped edits — never a wholesale
  rewrite. Every line removed or merged is verified to exist in a durable home
  FIRST (ADR / report / review / daily log); the report carries the mapping
  table: what left → where its record lives. A lesson with no home does not
  leave — it gets a home or it stays.
- **The Dv519 lesson LANDS**: «an artifact assembled from records can carry
  exam material the source record was entitled to hold» —
  [[the-codebook-that-quoted-the-answer-key]], one compact line.
- **knowledge/index.md**: within the auto-dream cap (200 lines; currently 51 —
  verify, curate only if stale entries exist).
- **knowledge/hot.md**: curated 364→203 this evening — verify sealed markers
  intact, no stale «open» items, every blocker has an owner and a decide-by;
  touch only what fails that check.
- Consolidation is judgment work: prefer merging near-duplicate lessons into
  one durable phrasing over deleting either. When unsure a line is safe to
  drop, it is not.

## Verify (paste outputs, `python3.11` throughout)

```
scripts/context-census.py            # BEFORE and AFTER, same invocation, both pasted
make check                           # green, 2959/2 expected (no code changes)
python3.11 scripts/check-wikilinks.py   # 0 broken — including the new [[...]] line
wc -l -c <MEMORY.md's real path>     # ≤75% of the re-derived ceiling, both axes
git status --porcelain               # clean at the end
```

## Report

`docs/reports/vault-dream.md`, path-only in chat. Deviations from **Dv524**,
cause tags from the CLOSED enum v2 only; lesson names as trailing
`[[wiki-name]]`. Five-line Process signals. Read back first, one line each:
the re-derived ceiling and the 75% target; the no-home-no-eviction law; the
mapping-table duty; what runs in parallel and what that forbids.

## DO NOT

- **Never touch `docs/labels-pass1-r1.jsonl`** — the team lead is writing it
  in parallel: do not stage it, do not commit it, do not read-depend on it,
  even if it appears mid-session. Same for `docs/label-pack-pass1-r1*.md`
  beyond reading.
- No deletion without a proven durable home; no wholesale rewrite of any vault
  file; sealed markers in hot.md stay byte-intact.
- No project code, no cloud calls, no frozen records, no gold, no prompts.
- Team-lead files: commit verbatim, never edit. Never `git add -A`.
