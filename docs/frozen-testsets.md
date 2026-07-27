# Frozen test sets (Phase 2, step 2e) — v2

**Version: v2, 2026-07-27.** **Immutable without operator approval** (CLAUDE.md). v2 exists
only because the operator approved 11 corrections on 2026-07-27, before any baseline number
was scored — see the changelog. After v2 the sets are immutable again; every number ever
published against them must name the version and the hashes below.

## Files

| file | rows | sha256 (v2) |
|---|---|---|
| `data/frozen/comments_test.jsonl` | 400 | `14b6172472e482d511d36c6a95e5204482a3c14c058c972d39005c82609b9627` |
| `data/frozen/comments_train.jsonl` | 1600 | `aa73fd717054e6f9e905b3d17438aa0ad8968b1a3c5f50a45cb5f8deab32ae7f` |
| `data/frozen/posts_test.jsonl` | 250 | `183de2b56e9cb7cc958884db51638c281404cf5c4b06e91ba61ac6330e3dade2` |
| `data/frozen/posts_train.jsonl` | 750 | `d9b87cdd44586b8011b164f1e3be00457c75e675fad8db7524535306cc609049` |

The post sets are byte-identical to v1; only the two comment files changed.

## Changelog

**v2 — 2026-07-27, operator-approved.** Eleven corrections to `comments_test.jsonl`, applied
by `scripts/refreeze_v2.py` (kept in the repo so the v1→v2 diff has provenance). None of
these rows was in the 300-row review sample of 2d-2 — this was a second, independent operator
pass over the test set, and it was made before any baseline number existed.

| ids | correction |
|---|---|
| `@VARUS_channel:10658`, `:11312`, `:19177`, `:58`, `:7979`, `:8120`, `:9797`, `@msuaaaa:5534` | `sarcasm` → `true` |
| `@VARUS_channel:15718` | `sentiment` → `negative` |
| `@msuaaaa:8175` | `sentiment` → `negative`, `sarcasm` → `true` |
| `@msuaaaa:9534` | `unclear` → `true`, moved to the train pool |

Every changed row carries `annotator: "operator-reviewed"`. `@msuaaaa:9534` could not stay in
a test set the guidelines keep free of `unclear` rows, so it moved to the train pool and
`@msuaaaa:12604` ("Це тільки онлайн?") was drawn in its place, seed 42, from the same stratum
(`ua`, `neutral`, not sarcasm/packaging) — the only scorable row of its thread, so no
thread-mate stayed behind in train. Test stays 400 rows, train stays 1600, and the
thread-disjointness assertion is re-checked at the end of the run.

**v1 — 2026-07-27**, `scripts/freeze_testsets.py`, seed 42. Superseded hashes:
`comments_test.jsonl` `3a37f328…530ed`, `comments_train.jsonl` `899000b1…82b1f`.

## Provenance

Built by `scripts/freeze_testsets.py`, seed 42, from `data/annotation/comments_batch.jsonl`
(2000 rows) and `posts_batch.jsonl` (1000 rows) — the 2d-2 batches after
`scripts/apply_review.py` applied the operator's review verdicts. Labels follow
`docs/annotation/comments.md` and `posts.md`; the value sets are enforced by
`scripts/validate_annotations.py`.

## Training sources

Training reads **two** files, not one. Reconstructing the training data from the frozen set
alone silently drops 800 hand-labelled rows.

| file | rows | scorable | sha256 |
|---|---|---|---|
| `data/frozen/comments_train.jsonl` | 1600 | 906 | `aa73fd717054e6f9e905b3d17438aa0ad8968b1a3c5f50a45cb5f8deab32ae7f` |
| `data/annotation/sarcasm_candidates.jsonl` | 800 | 594 | `cd61a83e921545d899486fa418cc77a60c9cc3300bbb93eb10ef5f08da5831a5` |

The mined pool (`scripts/mine_sarcasm_candidates.py`) is a training source only — it is
excluded from the test set by construction, and its hash is a snapshot, not a freeze: unlike
the four files above it may be extended by mining deeper.

## Leakage control

Comments are split by thread (`channel`, `parent_msg_id`): every comment of one post is on
one side only. Verified at build time — 0 threads shared between the test set and the
scorable train pool.

`unclear` rows are excluded from both test sets (SPEC §5 excludes them from every gate) but
remain in the train pool with the flag set: 694 of 1600 comment train rows and 1 of 750 post
train rows. 199 of those comment rows share a thread with a test row — **filter `unclear`
before training** and thread-disjointness is strict.

## Comments test set

400 rows of the 1306 scorable comments; train pool 1600 rows (906 scorable).

`pool` and `quota` record how v1 was drawn and do not move: they are properties of the split.
`v2` is what the test set holds now — the corrections moved nine rows between the
sarcasm/packaging cells of their own language, which is the point of them.

| language | sentiment | sarcasm/packaging | pool | quota | v1 | v2 |
|---|---|---|---|---|---|---|
| en | neutral | - | 1 | 0 | 0 | 0 |
| en | positive | - | 1 | 0 | 0 | 0 |
| other | negative | - | 55 | 15 | 15 | 13 |
| other | negative | yes | 10 | 5 | 5 | 7 |
| other | neutral | - | 86 | 24 | 24 | 24 |
| other | neutral | yes | 1 | 0 | 0 | 0 |
| other | positive | - | 80 | 22 | 22 | 22 |
| ru | negative | - | 150 | 43 | 43 | 43 |
| ru | negative | yes | 25 | 14 | 14 | 14 |
| ru | neutral | - | 68 | 19 | 19 | 19 |
| ru | neutral | yes | 3 | 1 | 1 | 1 |
| ru | positive | - | 32 | 9 | 9 | 9 |
| ua | negative | - | 335 | 97 | 97 | 93 |
| ua | negative | yes | 65 | 36 | 36 | 42 |
| ua | neutral | - | 247 | 71 | 71 | 69 |
| ua | neutral | yes | 10 | 5 | 5 | 6 |
| ua | positive | - | 138 | 39 | 39 | 38 |
| **total** |  |  | 1307 | 400 | 400 | 400 |

The per-language totals are unchanged — UA 248, RU 86, `other` 66, EN 0 — because every
correction and the swap stayed inside their own language.

## Posts test set

250 rows of the 999 scorable posts; train pool 750 rows. Half the launch rows are in test by
design.

| post_type | pool | taken |
|---|---|---|
| launch | 61 | 30 |
| other | 185 | 43 |
| promo | 753 | 177 |

## Depth of what the gates measure

The split is fixed by the operator's design; these are the counts the gates will be computed
on, recorded before any model exists.

| gate | what it needs | rows in test |
|---|---|---|
| G1a | per-language sentiment, UA + RU (amendment 3.1) | UA 248, RU 86 = 334 gated; `other` 66, EN 0 ungated |
| G1b | sarcasm | 52 (43 in v1, +9 from the v2 corrections) |
| G1c | packaging intent | 19 |
| G1d | relevant posts | 26 |
| G1e | brand mentions | 36 |

- **G1a's 2 pp per-language margin is thinner than it looks**: on RU (n=86) 2 pp is under
  two rows, so a per-language verdict there is one or two comments wide.
- **`language: other` is 66 test rows** — the langid heuristic's failures, not a fourth
  language. They are scored in the overall macro-F1 and in no per-language gate.
- **EN rounds out again**: 2 scorable EN comments across the strata gave it 0 test rows.
  Expected under amendment 3.1, noted so it is not a surprise twice.
- **The test set has now been through two operator passes, and 326 rows through neither.**
  64 rows were in the 2d-2 review sample (1 correction); the v2 pass corrected 11 further
  rows, none of them from that sample. 11 rows carry `annotator: "operator-reviewed"`. The
  remaining 326 were labelled before either pass showed that sarcasm and negativity were
  under-flagged, and the 2d-2 review measured that error rate at 2.3% per field — on RU
  (n=86) that is ~1.7 rows, the same width as G1a's 2 pp per-language margin. **Read the
  per-language clause of G1a as noise-dominated unless those 326 rows are reviewed too.**
- The mined pool (`scripts/mine_sarcasm_candidates.py`) is labelled under the corrected
  calibration, so it feeds training, never this test set.
