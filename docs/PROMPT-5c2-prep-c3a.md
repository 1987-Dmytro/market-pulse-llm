# PROMPT-5c2-prep-c3a — the build track: cap 33, the post-text pass, the prefilter census

**Contract:** `docs/SPEC.md` amendment **3.18 (7)** (the STOP ruling — read that
clause, not the whole spec) and this file. **$0 session:** no pod, no endpoint,
no serverless job, no OpenRouter call, no Telegram client. All artifacts in
English. Team-lead files (`docs/STATUS.md`, `docs/SPEC.md`, `docs/PRODUCT.md`,
`docs/PROMPT-*.md`) are read-and-commit, **never edit** (File ownership).

**Context in four lines:** the operator ruled on the prep-c2 STOP and the ruling
is law (3.18 (7)): anchor 2026-08-09 ratified, phase cap 30 → 33, the session
buys the whole two-leg window, the leaflet leg's population is the corpus on
disk (159 pages), and the post leg enters ONLY through the relevance prefilter —
whose writer does not exist yet. This contract builds what the pre-registration
(prep-c3b, NOT this session) will pin.

## Step 0 — commit the tail

`git status --short` at issue time, verified by the team lead: `docs/SPEC.md`
(M — the 3.18 (7) amendment, team-lead hand), `docs/STATUS.md` (M — the
acceptance edits, team-lead hand), `knowledge/daily_logs/2026-08-13.md`,
`knowledge/hot.md`, `knowledge/index.md` (M — session ends), `docs/reviews/`
(untracked — the 2026-08-13 process audit, an operator document) and
`docs/PROMPT-5c2-prep-c3a.md` (untracked, this file). Stage by path, never
`git add -A`. Three commits:

1. `docs: 5c2-prep-c3a queued — the STOP ruling in law (SPEC 3.18 (7))` —
   SPEC, STATUS, this prompt.
2. `docs(vault): the prep-c2 session tail` — the three knowledge/ paths.
3. `docs(reviews): the 2026-08-13 process audit — the self-improvement loop` —
   `docs/reviews/`.

Your session tail at the end is pre-authorised into its own final commit. STOP
only for a path neither this list nor the session-tail rule explains.

## Deliverable 1 — the cap moves 30 → 33 (3.18 (7)(b))

Move MEANING, not literals (the prep-a precedent). Consumers enumerated at
issue time by grep + code read — verify each against disk before editing:

| consumer | what it needs |
|---|---|
| `scripts/runpod_guard.py:42` `PHASE_CAP_USD` | the one live home; uses at 183/221/236/251/253 follow it |
| `tests/test_runpod_guard.py` 26, 192 | fixture ledgers' `phase4_cap_usd` |
| same file, 82 and 121–122 | DOCSTRING arithmetic written against 30.00 — rewrite the semantics to 33; never leave a true-sounding sentence about a dead cap |
| same file, 98 | `remaining_usd == 29.6` arithmetic shifts |
| same file, 116 | equality literal `== 30.00` |
| `tests/test_repair_phase4_ledger.py:100` | `== 30.00` → `== 33.00`; line 101's `CAP_IN_FORCE_USD != PHASE_CAP_USD` stays true (25 ≠ 33) — verify, don't assume |
| **meaning-flip class:** `tests/test_projection_5c2.py:202` and `test_the_whole_window_does_not_fit_and_the_record_says_so` (:259) | the prep-c2 record was written UNDER cap 30 and is NEVER regenerated (3.18 (7)(b)). Decouple by the cap-in-force pattern: the record pins against 30.00-in-force-at-write, `fits: false` stays a true sentence about 2026-08-13T07:59; docstrings cite 3.18 (7)(b). `results/projection_5c2.json` bytes do not change. |
| ledger `results/spend_phase4.json` | append the raise entry mirroring the 25→30 precedent (note cites 3.18 (7)(b)); the anchor and all 35 logged entries UNTOUCHED |
| prose | `knowledge/hot.md:36,181` — yours, regenerate at session end; `docs/STATUS.md:622` — team-lead file, do NOT touch. Re-grep prose for `30.00`/`$30` before closing. |

Acceptance requires the test that fails if the cap moves BACK: an equality on
33.00 in a live (non-record) test.

## Deliverable 2 — the post-text pass (3.18 (7)(e))

The seam, named: a third `*_pass` in `src/market_pulse/loop.py` beside
`inference_pass` (:197) and `page_pass` (:455) — page_pass's own docstring
declares the house pattern ("the ordering, the seam and the failure mode are
inference_pass's, deliberately"). The new pass:

- feeds a window post's TEXT to the TEXT TIER instrument of 3.18 (2) — the
  skub2 text leg: ONE instrument, two input shapes ("the page leg sends an
  image and the text leg sends a string", `scripts/positions_gm4_skub.py`).
  Open that code path first; a grep hit is not a capability.
- writes rows through the prep-c1 producers. Expected: the existing kinds
  suffice — `position_row` carries presence/tier/warnings, REQUIRED carries
  rendering+reply, and the validate sitting of 3.18 (6) must be buildable from
  the rows. If you conclude a new kind or field is needed, STOP and report —
  that fork is the team lead's. `evidence.REQUIRED`/`KIND_FIELDS` stay frozen.
- carries the four properties prep-b/c1 measured on the sibling legs, each
  tested in BOTH directions: durable write BEFORE watermark; the queue
  subtracts the answered set; the send seam replaceable by a stub and nothing
  else; refusal messages carry THIS leg's queue depth (the Dv265 class).
- smoke: the c1 pattern (`StubPageTransport` precedent) — one clean invocation
  over the full stub queue, then idempotence on the exhausted queue (the Dv266
  lesson: exhaust, re-run, byte-identical, 0 transport calls).

Known consumer that flips: `tests/test_projection_5c2.py:236–240` pins
`dir(loop)`'s `*_pass` list to exactly `["inference_pass", "page_pass"]` — it
documented the repo at the record's write moment. Rewrite it to pin the
RECORD's claim (the record carries `posts_in_scope_and_unpriced` BECAUSE no
writer existed at write time — that sentence stays true forever), not the live
module; docstring cites 3.18 (7)(e).

## Deliverable 3 — the prefilter census over THIS window ($0)

Population of the post leg. The instrument precedent is
`scripts/sku_prefilter_census.py` (the frame `build_sku_text_pack.py` drew its
30 rows from — lexicon over post text, the matched LINE kept as evidence). Read
it FIRST; extend or re-run over the WINDOW's posts — the census_5c2 anchor
`2026-08-09T00:00:00+00:00`, its selection pinned by that record's
`ids_sha256`. Do not rebuild what exists.

Output: a NEW record `results/census_c3a_posts.json` — do NOT touch
`results/census_5c2.json` (its byte-identity under its anchor is a sealed
gate):

- per-channel prefilter pass counts over the window's 9 158 posts, the
  matched-line evidence convention kept;
- the leg priced at skub2's text marginal (2.8132 s/row, derived by the house
  function `write_sku_projection_b2.text_marginal`, cited via the cite()
  pattern of `scripts/projection_5c2.py` — source path + quoted line beside
  every number);
- the leaflet corpus total read from `results/post_media_5c1.json` (159 pages /
  19 posts — the citable source for 3.18 (7)(d) in the prereg);
- house record hygiene: `producer.sha256`, no `git` block, no clock — mirror
  the prep-c2 AST tests;
- determinism: run twice, byte-identical, both sha256 in the report.

## Deliverable 4 — RECORD debts

ADR in `knowledge/decisions/` + INDEX line for the 3.18 (7) ruling: anchor
ratified, cap 33, whole-window composition, leaflet corpus scope, filtered
post leg — and the rule that BINDS THE TEAM LEAD: records written under cap 30
are never regenerated to fit the new cap.

## Verify gate — evidence, not assertions

1. `make check` green after EVERY commit; the per-commit worktree checkout
   table with the control row (Dv193: re-measure the collect-guard nodeid, do
   not inherit the sentence).
2. The new record's determinism pair (both sha256) + the smoke's
   one-invocation numbers.
3. The cap guards shown in BOTH directions: the meaning-flip tests red under
   the naive `== guard` form, green under the decoupled form — and the live
   33.00 equality red if the cap moves back.
4. `git log --oneline` for the session; clean `git status --short` at the end
   apart from the pre-authorised tail.

## Do NOT

- Spend anything; register an endpoint/template/serving config; open
  `ENDPOINT`; build a Telegram client.
- Write the pre-registration, in any file, under any name — that is prep-c3b.
- Touch the bytes of `results/census_5c2.json` or
  `results/projection_5c2.json`, or regenerate ANY record written under
  cap 30.
- Edit `evidence.REQUIRED`/`KIND_FIELDS`, `src/market_pulse/positions.py`,
  sealed sku artifacts, or team-lead files. Do NOT rotate `RAW_STORE_SALT`.

## Report

`docs/reports/5c2-prep-c3a.md`, opening with three plain sentences: what is
true now that was not true this morning. `implementation-notes.md` Deviations
current — silence is not compliance — and **every Dv ends with a cause tag**
`[cause: contract-gap | spec-gap | env | tooling | model | process]`. The
report closes with a **"Process signals" section, five lines max**: what
rubbed in the process, what the contract lacked, what had to be discovered
rather than read. Both are the new house rule per the 2026-08-13 audit
(`docs/reviews/2026-08-13-process-audit-and-self-improvement.md`).

**Read-back before you start:** name in one line each — the two records this
session must not touch; the function whose seam your pass mirrors; what
happens to the cap-30 records under the new cap (nothing).
