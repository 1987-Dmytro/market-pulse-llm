# PROMPT-sku-a — the position layer, everything before the pilot ($0)

> Authority: SPEC §3.17 (operator go 2026-08-10). This contract is $0 and
> local: schema, prompts, pre-filter, ground-truth packs, pre-registered
> bars. No paid calls, no endpoints, no pods. The pilot itself is sku-b.

## Read first (sections, not documents)

- `docs/SPEC.md` §3.17 — the whole amendment; it IS the mini-spec.
- `docs/PRODUCT.md` question 7 row.
- `results/opus_audit_5c1.json` — S4 rows and missed_brand_candidates
  (the leaflet ground-truth source).
- The prompt-registration discipline in `.claude/rules/
  phase345-artifacts.md` (never edit a registered prompt in place; the
  registration tests assert both ways).

**Read-back check — FIRST lines of the report:** the six deliverables
and the three pre-registered bars, one line each.

## Step 0 (commits pre-authorised)

1. **Registry stamp:** the 2026-08-10 operator signature lands in
   `config/registry.yaml` provenance — composition 66 = launch 59 +
   watch 7, day-2 PROVISIONAL diff becomes signed; no row changes.
2. **Two ADRs** + INDEX entries: (a) the opus-review programme close —
   fn_matcher = 0 on 498, captions 117/43/3, fp = ruled noise, artifact
   paths; (b) the 2026-08-10 sitting — ВАРТО text-matching OFF (hits
   via captions/images or anchored text), «Селянське» anchored-only,
   141-name revision deferred to the position-layer design (now SPEC
   3.17), composition signed.
3. Team-lead docs commit, unedited: `docs/SPEC.md`, `docs/PRODUCT.md`,
   `docs/STATUS.md`, `docs/PROMPT-sku-a.md`.
4. Vault tail (fixed paths as usual, own commit).

## Deliverables (six; STOP and report if one runs deeper than briefed)

1. **Schema module** `src/market_pulse/positions.py`: the position
   dataclass per SPEC 3.17 (2)-(4) — identity (brand_id|brand_raw,
   line, category from the 13+2 taxonomy, size, fat_pct), price
   OBSERVATION (price_promo, price_old, discount_pct_printed,
   price_qualifier, price_origin), carrier, extraction_source. The
   TIER LADDER as a pure function of field completeness
   (position / product_mention / brand_mention) with tests over field
   combinations. Normalization: sizes → г/мл, fat «2,5%» → 2.5, price
   parse with approx qualifier («по 90», «~»). `depth()` computed only
   when both prices exist + the printed-vs-computed disagreement FLAG
   (tests: pair present/absent/disagreeing). No field imputation
   anywhere — assert it.
2. **Two registered prompts** BESIDE existing ones, own shas:
   `positions_post_gm4` (one leaflet PAGE → JSON list of positions)
   and `positions_text_gm4` (one text row → same schema). A strict
   JSON parser that REFUSES non-schema replies (no salvage); both
   registered per the discipline, tests both ways.
3. **Pre-filter** `positions.prefilter(row)` — deterministic:
   watchlist/category-lexicon hit AND a size/price pattern nearby
   (число + г|кг|л|мл|%|грн). Tests incl. negatives. Run it over the
   corpus (posts + comments, $0) → `results/sku_prefilter_census.json`
   (counts by channel and carrier) — the text-leg sample frame.
4. **Ground-truth packs:** (a) leaflet reference
   `results/sku_reference_leaflet.json` from the Opus-audit S4 rows
   (19 ATB posts: item ids, brands_visible, image paths); (b) text
   pack — seed-42 sample of 30 pre-filtered rows via the build-pack
   pattern, for team-lead triage + operator adjudication (schema'd
   returns, validator).
5. **Pre-registration** `results/sku_pilot_prereg.json`, committed
   BEFORE any pilot: the three bars of SPEC 3.17 (6) verbatim
   (leaflet brand-recall ≥0.75/page; price-pair accuracy ≥0.80 with
   the team-lead-vs-images verification procedure named; text tier
   accuracy ≥0.85), one attempt, failure closes B by measurement.
6. **Tests + `make check` green**; Deviations continue Dv96+.

## Do NOT

- Do not edit `docs/STATUS.md`, `docs/SPEC.md`, `docs/PRODUCT.md`,
  `docs/PROMPT-*.md` — team-lead files; commit-only (File ownership).
- Do not change `config/registry.yaml` ROWS (the stamp touches
  provenance only): the 141-name / two-level watchlist revision is the
  5c3 NAMED revision, not this contract.
- Do not touch the frozen classification family (T1v2), frozen sets,
  `results/baselines.json`, verdict/parity records, the adapter.
- No paid calls of any kind; the census and packs are local.
- Never `git add -A`; vault tail → its own final commit.

## Report — evidence, not assertions

Registration greps + both prompt shas; the tier-ladder test names and
their run output; census counts (channels × carriers, prefilter yield);
pack manifests with shas; the prereg file sha and its commit BEFORE any
pilot artifact; `make check` tail. Report in English. State your
assumptions explicitly.
