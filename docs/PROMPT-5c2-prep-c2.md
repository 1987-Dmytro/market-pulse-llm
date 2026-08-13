# PROMPT-5c2-prep-c2 — the money track: the census, the projection, and a STOP with numbers

**Contract:** `docs/SPEC.md` amendment **3.18 (4)**, the operator rulings of 13.08 —
(a) window composition is decided ON the census numbers, (b) leaflets are
**ATB-only by default this cycle** (revisable at the STOP against the coverage
table), (c) the pre-registration is **prep-c3**, written only AFTER the ruling —
and this file. Read that one clause, not the whole spec. **$0 session:** no pod,
no endpoint, no template, no serverless job, no OpenRouter call, no Telegram
client. All artifacts in English. Team-lead files (`docs/STATUS.md`,
`docs/SPEC.md`, `docs/PRODUCT.md`, `docs/PROMPT-*.md`) are read-and-commit,
**never edit**.

**Context in four lines:** prep-c1 gave all three record shapes a producer, so the
paid session first-writes nothing. What is not known is money: what the 4-week
window actually holds, per channel and per leg, and what it costs at a measured
serverless rate. This contract ends at a **STOP with numbers for the operator** —
it does not pre-register and it does not spend.

## Step 0 — commit the tail

`git status --short` shows exactly five paths, verified by the team lead at issue
time: `docs/STATUS.md` (modified — the acceptance and the rulings, the team
lead's hand), `knowledge/daily_logs/2026-08-13.md`, `knowledge/hot.md`,
`knowledge/index.md` (modified, your prep-c1 session end) and
`docs/PROMPT-5c2-prep-c2.md` (untracked, this file). Stage by path, never
`git add -A`. Two commits: `docs: 5c2-prep-c2 queued — STATUS after the prep-c1
acceptance` and `docs(vault): the prep-c1 session tail`. Your session output at
the end is pre-authorised into its own final commit. STOP only for a path
neither list explains.

## Step 0.5 — `image_path` goes repo-relative (team-lead ruling, Dv264)

`run_loop.pages_of` emits the path; the ruling: the RECORD stores it
repo-relative, and the code that READS the file resolves it against `REPO_ROOT`
at use time. `image_sha256` stays the row's identity, unchanged. Consumers,
enumerated at issue time — **4 files**: `src/market_pulse/loop.py`
(`render_page` reads the bytes — must resolve), `src/market_pulse/evidence.py`
(field name only, no change), `tests/test_loop.py`, `tests/test_evidence.py`
(adjust whichever assertion inspects the path; the
sha-of-the-bytes-sent test must stay green untouched). No rows exist on disk to
migrate: `data/derived/` is absent and the smoke sandbox is throwaway.

## Deliverable 1 — the census of the window, a pure read

- **One anchor.** A single timestamp, chosen once, recorded INSIDE the artifact;
  the window is exactly 28 days back from it (SPEC 3.18 (4): four weeks). A
  re-run is handed the anchor explicitly and must reproduce the artifact
  byte-identically — determinism is the census's own gate.
- **Per channel, inside the window:** comments (note plainly that the
  `inference` watermark is unset, so in-window comments are all unanswered),
  posts, and **posts-with-media** — reuse the media-presence definition of
  `scripts/image_census_5c1.py` (read it first); where the raw records cannot
  answer for a channel, the census writes CANNOT ANSWER for that cell, never a
  guess.
- **Leaflet coverage, the operator's number:** pages DOWNLOADED per channel from
  `results/post_media_5c1.json` (today that is `@atb_market_official` only)
  side by side with posts-with-media. The gap between those two columns is what
  the ATB-only default is measured against at the STOP.
- **Composition:** per-channel row counts and shares — the concentration
  question (whose window is this) answered by enumeration, not by reading the
  tail of a printed table.
- Output `results/census_5c2.json`, produced by a script with a test. No
  hand-typed numbers anywhere downstream of it.

## Deliverable 2 — the projection, from named paid measurements

- **Per leg, from a NAMED paid serverless measurement**, its path and its number
  QUOTED inside the artifact. Positions leg: the skub2-run session bought 138
  pages in one serverless session — locate its cost and per-page rate in the
  skub2 artifacts (report, runbook, ledger entry) and quote the line. Comment
  leg: the srv-2 programme's artifacts are the candidates — `results/parity_srv2.json`
  (`diagnostics`) and `results/serving_srv2d_smoke.json` — READ them and use
  what they actually hold; a candidate is not a source until its number is on
  the screen.
- **A leg with no paid serverless rate on disk says so:** the projection row is
  marked `NO PAID MEASUREMENT` and goes no further for that leg. Pod rates (5b)
  may appear only as clearly-labelled context beside it, never in the headline
  row — that is the letter of the 13.08 ruling.
- **Project:** the window's cost per leg with a drift margin (the v4-prep
  precedent), and the same at 2–3 candidate session caps that fit inside the
  remaining phase budget. Read the remaining budget from the guard/ledger and
  name the source — do not restate it from memory.
- Output `results/projection_5c2.json` + a test that asserts every projected
  number's `source` path exists and the quoted figure matches the file it cites.

## The STOP — how this contract ends

The report's final section is the operator's table: window composition per
channel, leaflet coverage vs downloaded, per-leg cost projection with sources,
candidate caps. **No pre-registration is written** — that is prep-c3, after the
operator's ruling, and the report says so in one line. If a number for the
prereg falls into your lap, it goes into the table, not into a registration.

## Verify gate — evidence, not assertions

1. `make check` green after **every** commit, and the per-commit checkout table
   with the control beside it (Dv193: the worktree `data/` symlink reddens one
   collect-guard nodeid on every row including the control — re-measure it, do
   not inherit the sentence).
2. The census command run TWICE with the same anchor — byte-identical artifact,
   both sha256 shown. One cross-check against an independent count (e.g. a
   channel where the 5a dry pass's queue is comparable), or a stated reason why
   none is comparable.
3. For each projection row: the quoted source line pasted beside the derived
   number.
4. `git log --oneline` for the session and a clean `git status --short` at the
   end apart from the pre-authorised vault tail.

## Do NOT

- Do NOT spend anything, register an endpoint/template/serving config, open the
  spend guard's endpoint constant, or build a Telegram client. If the census
  reveals a collection gap, it goes in the report — nothing is fetched.
- Do NOT write the pre-registration, in any file, under any name.
- Do NOT write outside `results/`, the step-0.5 line and its tests. Do NOT edit
  `src/market_pulse/positions.py`, `evidence.REQUIRED`/`KIND_FIELDS`, sealed sku
  artifacts, or team-lead files. Do NOT rotate `RAW_STORE_SALT`.

## Report

`docs/reports/5c2-prep-c2.md`, opening with three plain sentences: what is true
now that was not true this morning. `implementation-notes.md` **Deviations**
section current — silence is not compliance.

**Read-back before you start:** state the anchor rule in one line, name the two
legs' candidate source artifacts you will open first, and name the one thing
this contract must NOT write.
