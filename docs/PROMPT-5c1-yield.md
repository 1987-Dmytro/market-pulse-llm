# PROMPT-5c1-yield — the relevance floor: rulings, bars, the screen

**Contract:** Amendment 3.12 (docs/SPEC.md header block, approved 08.08).
Deliverable = the yield screen over the whole registry + the day-2
acceptance rulings landed on record. **$0; offline except ONE resolve
(step 5)** — the day-2 FloodWait discipline applies to that single call.
This contract sits BETWEEN day-2 (accepted 08.08) and the operator's
launch signing: the registry diff stays PROVISIONAL until the operator
reads `results/yield_screen_5c1.json` and signs.

## Steps, in order

0. **Tail hygiene:** commit the two modified vault files (daily log,
   index). Then reconcile one count in implementation-notes.md: the
   day-2 report said 13 joins-log rows for 08.08, but
   `grep -c 2026-08-08 results/joins_5c1.jsonl` returns 14 — name the
   extra row (likely a non-membership record). One sentence, no code.

1. **Registry rulings on record (operator, 08.08 acceptance):**
   - **@dikankaa → EXCLUDED.** Reason: `ru 1.00 on 20 decidable posts +
     RF oblasts in the channel's own description; UA-only policy
     (2026-07 census discipline)`. Keep the evidence line in the
     exclusion comment — house style: a silently shorter file cannot be
     told from one that never had the channel. Registry becomes **66**.
   - **RF_FLAG ×3 kept** (@myrhorodtown, @poltava_informue, @poltava20):
     per-row ruling `war-news-explained (Wildberries warehouse strike
     report)` recorded wherever today's gate rulings live (the --close
     pattern). The zero must not rot.
   - **Closed-groups flag (4 channels, option 1):** record as "the flag
     concerns a capability the assigned bucket does not use".

2. **Watchlist +3 (operator ruling 08.08; UA canon everywhere
   operator-facing, RU spellings are matching aliases only):** add to
   the registry watchlist AND docs/WATCHLIST.md:
   - `zarih` — display_names: Заріг, Зарог — notes: local
     Poltava-oblast competitor (Orzhytsia raion); regional: poltava
   - `myrhorodska-korivka` — display_names: Миргородська корівка,
     Миргородская коровка — notes: local Poltava-oblast competitor;
     regional: poltava
   - `yahotynske-dlia-ditei` — display_names: Яготинське для дітей,
     Яготинское для детей — notes: Molochnyi Alians baby-food line,
     tracked SEPARATELY from `yagotynske` (the Мгарське pattern);
     primary baby_food competitor.
   G1e history is never re-scored; any future run's provenance names
   the watchlist revision.

3. **Pre-registered bars — commit BEFORE the screen runs:**
   `results/yield_bars_5c1.preregistration.json` =
   `{bar_A_relevant_posts_28d: 4, bar_B_comments_under_relevant_28d:
   10, ruled_by: "operator 2026-08-08", currencies: "posts and comments
   are separate; never blended"}`. The census pattern: the screen
   record cites this file's sha256.

4. **The yield screen** — pure core in `src/market_pulse/`,
   `scripts/yield_screen_5c1.py`, tests.
   - Inputs: `config/registry.yaml` (all buckets), the 28-day windows
     in `data/raw/posts/*.jsonl` and `data/raw/comments/*.jsonl`,
     brand display_names from the registry watchlist (incl. step 2's
     three), categories from `data/category_lexicon_draft.json` —
     record its sha256 AND its `status: draft-not-law`: the lexicon is
     a screening instrument here, never the category law (5c3 owns the
     law).
   - Per channel: relevant_posts (n + share of window posts);
     brand_hits and category_hits SEPARATELY (per-28d and per-week);
     comments_under_relevant (n; join via parent_msg_id — the CHANNEL
     post id, never compared to reply_to_msg_id); bar A pass/fail;
     bar B pass/fail/N-A (N/A when no readable comment source);
     below_both flag; ONE quoted evidence line per channel with hits
     (evidence is a quoted line, never a counter).
   - Matching: casefold + the lexicon's own matcher/endings rules as
     shipped; a hit counts once per post.
   - Controls, refuse-to-report (`verdicts_reportable: false`, exit 1):
     POSITIVE — each of the four originals (atb_market_official,
     silposilpo, VARUS_channel, msuaaaa) must clear bar A on its
     window; NEGATIVE — a no-taxonomy fixture must produce 0 hits
     (test).
   - No-overwrite refusal with `--out` (the Dv2 pattern of census and
     market screen).
   - Output `results/yield_screen_5c1.json`: rows sorted by (audience,
     handle); summary = pass_A / pass_B / below_both lists +
     per-audience rollup.

5. **@KarlivkaLive through the track-R gate** (operator ruling, option
   2 of the supergroups menu): ONE resolve, wall-guarded. On PASS —
   collect its 28-day window and include it in the step-4 run
   (registry 66 → 67, provisional like everyone). On FAIL/FLAG —
   record and stop; no improvisation.

6. **ADR** `knowledge/decisions/5c1-relevance-floor-and-discovery.md`
   + INDEX line: the operator question that exposed the gap (channels
   were admitted with no taxonomy measurement), amendment 3.12, the
   measured discovery prices (Premium €5.99/mo on the collector
   account; 10 free full-text queries/day, then 10 Stars ≈ €0.20 per
   query; TGStat ruled out as an RF service; Telemetr.io free tier as
   catalog fallback), bars A=4 / B=10 pre-registered before any
   number existed, and the 08.08 acceptance rulings (@dikankaa out,
   RF_FLAG ×3 explained). Numbers with artifact paths.

## Verify & report
`make check` green (expect above 1201 — the screen brings tests); the
screen runs over the FULL registry; report = artifact paths, the
below_both list VERBATIM, and a Deviations section (silence is not
compliance). Numbers only from result files. Read-back first: list the
seven steps in one line each and state your assumptions; STOP on
anything neither this contract nor the standing rules explain.

## DO NOT
`docs/STATUS.md`, `docs/SPEC.md`, `docs/PROMPT-*.md` are team-lead
files — read and commit, never edit. No Stars spend, no OpenRouter, no
pods (the discovery session is a SEPARATE future contract). No edits to
frozen sets; no `--force` on any pack builder; never `git add -A`; do
not re-run theme_screen without `--out`. Nothing here touches serving —
batch 1 stands.
