# PROMPT-arch-a — code graph, architecture document, instrument inventory ($0)

Issued 2026-08-11 (team-lead file — read and commit, never edit). Repo state at issue:
HEAD 1c3ecc9 + two dirty vault files; suite 1611 passed / 2 skipped (post-adjudication,
Dv111 by design); sku-b prereg ratified R1–R5 (operator, 10.08). This phase maps the
codebase BEFORE the paid pilot: no new instruments, no deletions, $0.

**Read-back check (first lines of your report):** list step-0 items (1)–(4), deliverables
A–C, and the DO-NOT list — one line each — before any work.

## Step 0, in order

**(1) Commit the standing dirty set — grouped by paths, never `git add -A`:**
(a) `data/annotation/sku_a_text/text30.csv` — the adjudicated gold, its own commit;
(b) team-lead docs + env, committed not edited: `docs/STATUS.md`,
`docs/PROMPT-arch-a.md`, `.claude/settings.json` (the PRODUCT.md deny line);
(c) the augment layer: `CLAUDE.md`, `knowledge/runbooks/`;
(d) vault tail: both daily logs (2026-08-10, 2026-08-11), `knowledge/hot.md`,
`knowledge/index.md`. `.mcp.json` stays empty — operator ruling 11.08: the project
has no backend server.

**(2) SPEC amendment 3.17 (7) + pin-test evolution — ONE green commit.** Insert the
verbatim block below into `docs/SPEC.md` immediately after the 3.17 (6) paragraph
(which ends "…only on a green gate.") and before the `**Date:**` line. This is
team-lead-authored text: transcribe byte-exact, never reword (File ownership; the
3f1f0a7 precedent). In the SAME commit evolve
`tests/test_sku_prereg.py::test_every_pinned_input_still_hashes_to_what_it_says`
the yield-screen way: for `docs/SPEC.md` ONLY, strip the marked block (begin/end
marker lines inclusive) before hashing and assert the stripped text reproduces the
prereg's pinned sha `973c87890ad049d5…`; also assert the marked block IS present in
the live file. All other pinned inputs stay hashed as-is. Never re-pin the prereg.
Evidence both directions: live file hash ≠ pin; stripped hash == pin.

The verbatim block (markers included):

```
<!-- sku-b-ratification begin — stripped by tests/test_sku_prereg.py before hashing
docs/SPEC.md against the prereg pin; the registered law is the stripped text -->
(7) **Pilot bar operationalization — ratified (operator, 2026-08-10).** The five
readings registered in results/sku_pilot_prereg.json (ratification_required, R1–R5)
are ratified as written there: R1 — bar 1's "per page" is read per POST (recall over
the union of the post's page answers), macro-averaged over the 15 posts with a
non-empty gold set; the micro reading over the 55 pairs is reported beside it and
gates nothing. R2 — the page set is exactly the 108 sent pages. R3 — the four
empty-gold posts are outside the recall mean and serve as a precision probe. R4 —
bar 2 is SCORED at n >= 10 pairs, REPORTED and not scored at 1–9, NOT_REACHABLE at 0.
R5 — unreadable replies are excluded and counted (>10% blocks bar 3); n >= 20
adjudicated rows to score; both carriers pooled as drawn. Thresholds, the $0.35 cap
and the one-attempt clause are unchanged. Text gold: data/annotation/sku_a_text/
text30.csv adjudicated 2026-08-10, 30/30 rows, validator clean (11 position ·
3 product_mention · 16 none).
<!-- sku-b-ratification end -->
```

**(3) ADR + INDEX:** `knowledge/decisions/sku-b-pilot-readings-ratified.md` — the five
readings (from the prereg record, not from chat), the two triage rulings on the text
pack (row @VARUS_channel:1912 → category not line; row @silposilpo:2529 → all-empty,
out-of-taxonomy biscuit), the caption-quiz observation (operator 10.08: 2 bad / 2
partial / 1 no-verdict on 5 posts — matches audit faithful 9 · partial 10 · wrong 0),
and one line pointing to STATUS's deferred two-stage OCR alternative. State the
gold composition (11 position · 3 product_mention · 16 none — of the none-rows,
12 carry no-brand ticks and 4 are all-empty) and the REGISTERED bar-3 denominator:
ALL 30 adjudicated legal rows. Gold `none` is a value — the model must answer []
to match it (prereg "comparison" clause); the 16 none-rows price the refusal
discipline, the 14 rung-rows price tiering. A narrowing of the denominator to 14
is a post-hoc change of a registered bar and is REFUSED (team-lead ruling 11.08).
Wikilinks to the 10.08 sitting ADR; INDEX updated; check-wikilinks green.

**(4) hot.md curation:** remove the stale blocker "the launch signature waits on the
SITTING" (superseded by the 10.08 signature); replace the sku-a "Next: ratify R1–R5"
lines with the post-ratification state (ratified 10.08; text gold adjudicated; next:
arch-a → sku-b); fold remaining opus-audit prose into ADR pointers. Measured lever
(augment census 11.08): boot tax 18.3K tok, hot.md carries 12.0K of it (66%);
MEMORY.md 4.23K; the three CLAUDE.md 2.04K; path-scoped rules cost 0. THIS phase's
bar: hot.md curated to ≤6.0K tok by folding closed-phase blocks into ADR/STATUS
pointers — curation, not restructuring; nothing decided is deleted, every pointer
names its ADR. Re-run the census and state new totals in the report. The 9.0K
total target stays standing and is NOT this phase's gate.

## Deliverable A — the code graph (graphify)

Precondition: the `/brain-init augment` run precedes this prompt (separate session,
operator-approved spec) and owns the Tooling layer. VERIFY it landed: CLAUDE.md has
a Tooling section naming context7 and ponytail, `knowledge/runbooks/tooling.md`
exists, `permissions.deny` in `.claude/settings.json` is untouched (4 entries incl.
PRODUCT.md), hot.md markers intact. Any of these absent → STOP and report; never
write the Tooling section yourself and never duplicate user-level plugins into
`.mcp.json`.

`graphify claude install` (marked CLAUDE.md section; file stays ≤200 lines total
after both sections). Build the graph over the repo; `graphify hook install` (post-commit
rebuild); demonstrate the hook fired by citing its output on one of this phase's
later commits. `graphify-out/` stays outside `knowledge/`, gitignore per graphify
defaults.

## Deliverable B — docs/ARCHITECTURE.md (English, mermaid)

Two flow diagrams, node lists ratified by the operator 10–11.08 (transcribe, then
VERIFY every named module/prompt/file against the graph or grep — cite the query per
node in implementation-notes.md; a node that fails verification is a Deviation, not
a silent fix):

Flow 1 — leaflet page → SKU (sku-b pilot): telegram channels → `telegram_client`
collector (jpg + sha on disk, $0) → one page = one call (base64 in job, ≤10 MB) →
RunPod serverless, GM4-31B NF4, adapter OFF, prompt `positions_post_gm4` → strict
JSON parser (`positions.py` / `prompts.py`, no salvage) → position records
(`extraction_source`, tier assigned by code) → per-position price-pair dump
(team-lead read at acceptance) → brand matcher → question-7 aggregate (code only).
Text leg: `positions.prefilter` (769 of 31 638) → `positions_text_gm4` → same
parser. Caption side-branch `caption_post_gm4` labeled: "themes/coverage only —
brands come from the position layer".

Flow 2 — comment → five heads: comment + parent post (`parents.py`) →
`T1v2_with_post` rendering → GM4 NF4 + adapter 4.5h2-arm-A (batch 1, greedy) →
strict parser → G1a sentiment · G1b sarcasm · G1c intents · G1d post type ·
G1e brands → scorer (`scorer.py`) → result files with sha.

## Deliverable C — instrument inventory (a section of docs/ARCHITECTURE.md)

Every entry, no sampling: all 16 `PROMPTS` registry entries (plus the RENDER_ONLY
twin, named), every file in `scripts/` (recount; state the count), all 21
`src/market_pulse/` modules. Classify each: battle · pilot-pending ·
closed-by-measurement (kept for provenance) · one-shot-done (kept, dated) ·
candidate-dead (PROPOSAL only). Every row carries one-line evidence: a result file,
a test, an ADR, or a git ref. NOTHING is deleted or renamed in this phase — the
candidate-dead list goes to the operator for a ruling at acceptance.

## Verify (evidence, not assertions)

`make check` green after every commit (expect 1611 passed / 2 skipped + whatever
the evolved pin-test adds); pin-test evidence both directions (see step 0 (2));
check-wikilinks green; hook demonstration; counts stated in the report (prompts,
scripts, modules); Deviations continue at **Dv112**; the vault tail of THIS session
(hot.md, daily log 2026-08-11, index.md) is its own final commit.

## DO NOT

- Delete, rename or rewrite anything in `scripts/`, `src/`, `results/`, `data/` —
  this phase only maps. (Goal: the inventory must describe the terrain, not move it.)
- Edit docs/STATUS.md, docs/PRODUCT.md, docs/PROMPT-*.md; in docs/SPEC.md nothing
  beyond the exact verbatim block at the marked place (team-lead files).
- Touch `results/sku_pilot_prereg.json` or any results file; never re-pin the prereg;
  never loosen the pin-test (evolution = strip-then-match).
- No paid calls of any kind; no new MCP servers; no duplication of user-level
  plugins into `.mcp.json`.

**Recovery clause:** if the step-0 (2) commit cannot go green, revert that single
commit entirely and STOP with the failing diff in the report. (The prohibition's
goal: the prereg pin must stay re-derivable at every commit; a red pin-test is
never committed.)

**Report:** artifact paths + evidence blocks; read-back at the head; Deviations
section even if empty ("none" is a statement). Operator review budget at
acceptance: ~20–30 min (diagrams + candidate-dead ruling).
