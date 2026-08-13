# PROMPT-5c2-prep-c3b — the pre-registration: the D cut, the fourth kind, the sealed numbers

**Contract:** `docs/SPEC.md` amendment **3.18 (7)** — now including **(g)**, the
operator's Dv290 ruling — and this file. **$0 session:** no pod, no endpoint, no
serverless job, no OpenRouter call, no Telegram client. All artifacts in
English. Team-lead files (`docs/STATUS.md`, `docs/SPEC.md`, `docs/PRODUCT.md`,
`docs/PROMPT-*.md`) are read-and-commit, **never edit**.

**Context in four lines:** c3a built the cap (33), the third leg and the
population number — and found the population is 72% recipes. The operator ruled
the **D cut** (3.18 (7)(g)): retail/aggregator carriers ∪ currency-bearing
rows. The team lead ratified the **fourth evidence kind** (the Dv285 fork).
This contract seals the pre-registration of 5c2-run. After it: the paid session.

## Step 0 — commit the tail, and one report amendment

`git status --short` at issue time, verified by the team lead: `docs/SPEC.md`
(M — the (g) ruling, team-lead hand), `docs/STATUS.md` (M — the c3a acceptance,
team-lead hand), `knowledge/daily_logs/2026-08-13.md`, `knowledge/hot.md`,
`knowledge/index.md` (M — session end) and `docs/PROMPT-5c2-prep-c3b.md`
(untracked, this file). Stage by path. Commits:

1. `docs: 5c2-prep-c3b queued — the D cut in law (SPEC 3.18 (7)(g))` — SPEC,
   STATUS, this prompt.
2. `docs(vault): the c3a session tail` — the three knowledge/ paths.

**The report amendment (the acceptance's finding):** the c3a report's Verify
gate §2 prints the determinism pair as `ab927a23…` — that is the `a39a8ad`
revision of `results/census_c3a_posts.json`; commit `9c723a7` added
`producer.borrows` and the file on disk is `4a7e755b73d6…`. Re-measure the pair
(two runs, both sha256) and amend §2 to show the CURRENT pair with one line
naming the stale-revision cause. Own commit:
`docs(report): c3a §2 — the determinism pair re-measured after 9c723a7`.

## Step 0.5 — the fourth kind (team-lead ruling on Dv285)

`evidence.KINDS` grows its fourth member — the ONE addition this contract
unfreezes; `REQUIRED` does not change:

- `"post_text"` in `KINDS`; `KIND_FIELDS["post_text"] = ()` (the `comment`
  shape — nothing of its own; `n_positions` / `unreadable` ride in `extra`).
- `post_pass` writes the marker row LAST per post, exactly as `leaflet_page`
  is written last per page (the c1 order-sensitivity precedent: measure the
  order, don't assert it).
- The two re-ask tests flip from documenting the gap to pinning its absence:
  an interrupted pass re-asks NOTHING it already answered — empty and
  unreadable posts included — and the exhausted-queue smoke goes back to
  `0 asked, 0 transport_calls` like its page sibling.
- `dedup_key` for the marker row follows the house pattern (`raw_store` —
  read how `leaflet_page` keys before writing).
- Both directions: the old gap measured red under the new code path
  (plant the c3a scenario), the new marker refused where it would collide.

## Deliverable 1 — the D cut, computed and pinned

A deterministic producer reads the SHIPPED `results/census_c3a_posts.json`
(bytes untouched — the cut is a new record, `results/postcut_c3b.json`):

- keep a passed row iff `carrier ∈ {official_retail, aggregator}` OR
  `"currency" ∈ pattern_kinds` (3.18 (7)(g), verbatim);
- the record carries: the kept count, per-channel breakdown, the three declined
  alternatives' counts (349 / 31 / 29) as context-not-headline, the leg priced
  at the text marginal via the cite() pattern, and the census's own sha256 as
  its input pin;
- house hygiene: `producer.sha256` (+ borrowed-module hashes, the 9c723a7
  precedent), no clock, no git block; determinism pair shown.

Expected magnitude ~50–55 rows / ~$0.07 — if the computed cut lands far off
that, STOP and report before the prereg.

## Deliverable 2 — the pre-registration of 5c2-run

The house precedent is `scripts/write_sku_prereg.py` and the B′ registration
(`results/sku_pilot_prereg_b2.json`) — read them first; the registered law is
the STRIPPED `docs/SPEC.md` (the strip family now includes today's (g)).
The registration pins BY VALUE, with an equality test per number (3.18 (7)(f)):

- **populations:** comments **5 075** (from `results/census_5c2.json`, its
  `ids_sha256` beside it); leaflet pages **159** (the corpus, 3.18 (7)(d),
  cited from `results/census_c3a_posts.json`'s leaflet block); posts = the D
  cut's count (Deliverable 1's record, cited by sha);
- **prices per leg** from the named paid measurements (the c2 projection's
  sources — unit-cost corner for dollars, marginal corner for wall clock,
  each field naming its model, the Dv274 discipline);
- **the session cap:** the three-leg projection with drift, rounded UP to the
  next half dollar; assert cap ≤ remaining **$9.1690** and print both. At
  c3a's numbers that is ≈ $7.87 → **$8.00** — recompute, don't inherit;
- **stop rules** (3.18 (7)(c)): the go/no-go re-projection of 3.17 (10)(a) at
  session start; the mid-run cap gate of (10)(b); on any stop, the resume
  discipline is the watermark + the fourth kind (state it in one clause);
- **the validate consequence** (3.18 (6)): the run persists per-row evidence —
  assert the registration names the fields the sitting needs;
- the registration REFUSES to write while `make check` is red or while any
  input sha disagrees (the B′ refusal precedent).

## Deliverable 3 — RECORD

ADR for the (g) ruling (`knowledge/decisions/`, + INDEX): the D cut, the three
declined alternatives with their numbers, and why `POST_PRICE_ORIGIN`'s
inheritance is now defensible. Update the c3a ADR only if it cross-references.

## Verify gate — evidence, not assertions

1. `make check` green after EVERY commit; per-commit worktree table with the
   control row — using c3a's REPAIRED instrument (per-entry symlinks, Dv291;
   an `error` row is a broken instrument, never a measurement).
2. The two new records' determinism pairs (both sha256 each).
3. The fourth kind measured in both directions (the flipped re-ask tests red
   under the old code path, green under the new; the exhausted-queue smoke at
   0/0).
4. The registration's refusal measured: red suite or moved input sha → it
   refuses, with the message shown.
5. `git log --oneline`; clean `git status --short` apart from the
   pre-authorised tail.

## Do NOT

- Spend anything; register an endpoint/template/serving config; open
  `ENDPOINT`; build a Telegram client. **Do not START 5c2-run** — the run is
  its own session under the sealed registration.
- Touch the bytes of `results/census_5c2.json`, `results/projection_5c2.json`,
  `results/census_c3a_posts.json`, or any record written under cap 30.
- No `evidence` change beyond the one step-0.5 names. No edits to
  `src/market_pulse/positions.py`, sealed sku artifacts, team-lead files.
  `RAW_STORE_SALT` stays.

## Report

`docs/reports/5c2-prep-c3b.md`, three plain sentences first.
`implementation-notes.md` Deviations current, **every Dv with its
`[cause: …]` tag**, and the closing **"Process signals" section (≤5 lines)**.

**Read-back before you start:** one line each — the D cut's rule verbatim; the
one file `evidence.py` change this contract permits; the number the session
cap must stay under; and the thing this session must not start.
