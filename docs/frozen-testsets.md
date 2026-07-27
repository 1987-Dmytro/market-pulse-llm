# Frozen test sets (Phase 2, step 2e)

**Immutable without operator approval** (CLAUDE.md). Regenerating them invalidates every
number scored against them; `scripts/freeze_testsets.py` refuses to overwrite an existing
freeze without `--force`.

## Files

| file | rows | sha256 |
|---|---|---|
| `data/frozen/comments_test.jsonl` | 400 | `3a37f328b339fd81cfd343f8acf123efb22246a52f765c0046e63e4dbba530ed` |
| `data/frozen/comments_train.jsonl` | 1600 | `899000b1e5976aebde4c282edef677bde49b05e8f94b11e6092083dc45782b1f` |
| `data/frozen/posts_test.jsonl` | 250 | `183de2b56e9cb7cc958884db51638c281404cf5c4b06e91ba61ac6330e3dade2` |
| `data/frozen/posts_train.jsonl` | 750 | `d9b87cdd44586b8011b164f1e3be00457c75e675fad8db7524535306cc609049` |

## Provenance

Built by `scripts/freeze_testsets.py`, seed 42, from `data/annotation/comments_batch.jsonl`
(2000 rows) and `posts_batch.jsonl` (1000 rows) — the 2d-2 batches after
`scripts/apply_review.py` applied the operator's review verdicts. Labels follow
`docs/annotation/comments.md` and `posts.md`; the value sets are enforced by
`scripts/validate_annotations.py`.

## Leakage control

Comments are split by thread (`channel`, `parent_msg_id`): every comment of one post is on
one side only. Verified at build time — 0 threads shared between the test set and the
scorable train pool.

`unclear` rows are excluded from both test sets (SPEC §5 excludes them from every gate) but
remain in the train pool with the flag set: 693 of 1600 comment train rows and 1 of 750 post
train rows. 198 of those comment rows share a thread with a test row — **filter `unclear`
before training** and thread-disjointness is strict.

## Comments test set

400 rows of the 1307 scorable comments; train pool 1600 rows (907 scorable).

| language | sentiment | sarcasm/packaging | pool | quota | taken |
|---|---|---|---|---|---|
| en | neutral | - | 1 | 0 | 0 |
| en | positive | - | 1 | 0 | 0 |
| other | negative | - | 55 | 15 | 15 |
| other | negative | yes | 10 | 5 | 5 |
| other | neutral | - | 86 | 24 | 24 |
| other | neutral | yes | 1 | 0 | 0 |
| other | positive | - | 80 | 22 | 22 |
| ru | negative | - | 150 | 43 | 43 |
| ru | negative | yes | 25 | 14 | 14 |
| ru | neutral | - | 68 | 19 | 19 |
| ru | neutral | yes | 3 | 1 | 1 |
| ru | positive | - | 32 | 9 | 9 |
| ua | negative | - | 335 | 97 | 97 |
| ua | negative | yes | 65 | 36 | 36 |
| ua | neutral | - | 247 | 71 | 71 |
| ua | neutral | yes | 10 | 5 | 5 |
| ua | positive | - | 138 | 39 | 39 |
| **total** |  |  | 1307 | 400 | 400 |

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
| G1b | sarcasm | 43 |
| G1c | packaging intent | 19 |
| G1d | relevant posts | 26 |
| G1e | brand mentions | 36 |

- **G1a's 2 pp per-language margin is thinner than it looks**: on RU (n=86) 2 pp is under
  two rows, so a per-language verdict there is one or two comments wide.
- **`language: other` is 66 test rows** — the langid heuristic's failures, not a fourth
  language. They are scored in the overall macro-F1 and in no per-language gate.
- **EN rounds out again**: 2 scorable EN comments across the strata gave it 0 test rows.
  Expected under amendment 3.1, noted so it is not a surprise twice.
- **Two sarcasm calibrations exist in the labelled data.** 64 of the 400 test rows were in
  the operator's review sample, and the review changed the labels of 1 of them (`annotator:
  operator-reviewed`); the other 336 were never reviewed and were labelled before the review
  showed sarcasm and negativity were under-flagged. The mined pool
  (`scripts/mine_sarcasm_candidates.py`) is labelled under the corrected calibration, so it
  feeds training, never this test set.
