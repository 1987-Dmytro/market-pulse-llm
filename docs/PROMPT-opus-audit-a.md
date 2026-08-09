# PROMPT-opus-audit-a — packs for the Opus 5 review ($0, default executor model)

> Authority: SPEC §3.16. Class: REVIEW (3.16 (1)) — nothing this program
> produces may enter a gate, the screen, or `results/baselines.json`; the
> matcher stays the judge. This contract is $0 and local: build the packs,
> the validator and the reader; the Opus sessions themselves run under
> `docs/PROMPT-opus-audit-protocol.md` afterwards.

## Read first

- `docs/SPEC.md` §3.16 only.
- The pack pattern you are reusing: `scripts/build_audit_pack.py` (4.5a)
  and `scripts/read_calibration_returns.py` (sha-pinned manifest, schema'd
  returns, refuse-on-drift).

**Read-back check — FIRST lines of the report:** the four strata and the
three scripts you will deliver, one line each.

## Deliverables

1. **`scripts/build_opus_audit_packs.py`** — builds
   `data/annotation/opus_audit_5c1/pack_NN.md` (15–20 posts each) plus a
   sha-pinned manifest `results/opus_audit_manifest.json`. Strata per
   SPEC 3.16 (4), drawn with a fixed seed:
   - S1: every post whose screen v2 hit was decided by a caption
     (`graded_on_a_caption` rows in `results/yield_screen_5c1_v2.json`).
   - S2: per channel, up to 10 posts where the matcher found brand hits
     (re-emit per-post hits with the `yield_screen` machinery; matcher
     output is the reference answer inside the pack).
   - S3: per channel, up to 10 relevant posts where the matcher found NO
     brand — the recall probe.
   - S4: all committed GM4 captions (`data/annotation/captions_5c1/
     gm4_atb19.jsonl` + `gm4_visc.jsonl`) with the LOCAL PATHS of their
     sha-matched sent images (`data/annotation/posts_media/…`) beside the
     caption text.
   Each pack embeds: the canon watchlist table (brand_id + display_names
   from `config/registry.yaml`), the post text (or `[image-only]`), the
   matcher's verdict for that post, the caption and image paths (S4), and
   an EMPTY returns row per item.
2. **`scripts/validate_opus_returns.py`** — schema check for
   `data/annotation/opus_audit_5c1/returns_NN.jsonl`: every row names
   pack id, item id, the four verdict fields (closed-book watchlist
   hits; open dairy/ice-cream brand mentions; caption verdict
   `faithful|partial|wrong|n/a`; `brands_visible_missed`), free-text
   note. Refuses rows for items not in the manifest; refuses a modified
   pack (sha).
3. **`scripts/read_opus_audit.py`** — aggregates validated returns into
   `results/opus_audit_5c1.json`: per-channel matcher precision/recall
   CANDIDATES (labelled `review, not measurement` in the record itself),
   missed-brand candidates with counts, caption faithfulness rates,
   `instrument: {model: claude-opus-5, protocol_sha: <sha of
   docs/PROMPT-opus-audit-protocol.md at HEAD>}`.
4. Tests for all three (schema refusals both ways); `make check` green.

## Do NOT

- Do not edit `config/registry.yaml`, the lexicon, `docs/WATCHLIST.md`,
  any `results/yield_screen*`, frozen sets, baselines — findings wait for
  the operator's sitting (3.16 (3)).
- Do not run any Opus session yourself and do not fill any returns file —
  the protocol sessions are the operator's to run.
- Team-lead files: commit-only. No paid calls of any kind.

## Report — evidence, not assertions

Manifest counts per stratum; pack count and sizes; `make check` tail;
validator refusal demo (one bad row rejected, output pasted); Deviations
continue Dv80+. Report in English.
