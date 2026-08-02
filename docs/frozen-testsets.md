# Frozen test sets (Phase 2, step 2e) — v2, and v3 beside it

**Version: v2, 2026-07-27.** **Immutable without operator approval** (CLAUDE.md). v2 exists
only because the operator approved 11 corrections on 2026-07-27, before any baseline number
was scored — see the changelog. After v2 the sets are immutable again; every number ever
published against them must name the version and the hashes below.

## Files

| file | rows | sha256 (v2) |
|---|---|---|
| `data/frozen/comments_test.jsonl` | 400 | `14b6172472e482d511d36c6a95e5204482a3c14c058c972d39005c82609b9627` |
| `data/frozen/comments_train.jsonl` | 1600 | `4b6ea7f354bcc396ee526ce193c445bb358fab1d070bbe429dfdeb3bace1a1d7` |
| `data/frozen/posts_test.jsonl` | 250 | `183de2b56e9cb7cc958884db51638c281404cf5c4b06e91ba61ac6330e3dade2` |
| `data/frozen/posts_train.jsonl` | 750 | `d9b87cdd44586b8011b164f1e3be00457c75e675fad8db7524535306cc609049` |

The post sets are byte-identical to v1; only the two comment files changed.

## v3 — 38 point fixes from the blind audit (2026-08-02)

**v3 does not replace v2, it sits beside it.** Three new files; every v2 file keeps its hash, and
every number ever published against v2 keeps meaning what it meant. Phase 4's verdict (2 of 5) is a
v2 result and stays one — the v3 re-scores in `results/rescores_v3.json` are program measurements,
never gate results.

| file | rows | rows changed | sha256 (v3) |
|---|---|---|---|
| `data/frozen/comments_test_v3.jsonl` | 400 | 15 | `d993ca6ff057060e73583a38addfbb78965b0f51a3cd994a5c9129d0606f135e` |
| `data/frozen/posts_test_v3.jsonl` | 250 | 7 | `a476414e26c410c12a56596edab2ff362989a67193dd0d93e3794eb2c073770d` |
| `data/frozen/sarcasm_holdout_v3.jsonl` | 108 | 15 | `9164d6f9aad24a469ea04745ef040984c8c5fabdf20fd83ad3f8448d614b8147` |

**Where the fixes come from.** Phase 4.5a put every disagreement between the deliverable arm
(`real-only`) and gold to the operator with the two candidate labels blinded, plus a control sample
of rows where both agreed. The operator ruled 244 rows without knowing which label was whose; on 38
of them the arm was right and gold was wrong — sentiment 15, the G1b `sentiment`+`sarcasm` pair 15,
`post_type` 5, `brands` 3, exactly the split gate 4.5 approved. `scripts/freeze_testsets_v3.py`
applies them from the sealed key and the arm's own dump; there are no hand edits, and a row that
takes no fix is proved byte-identical to its v2 line before anything is written.

Provenance — the audit manifest `results/audit_45a_manifest.json`, the returned verdicts
`results/audit_45b_returns.json`, the arm's dump `results/predictions/google-gemma-4-31b-it--20260801T183747Z.jsonl`
(`bdff8a4ad36b60f6…`) and the blinding key (`67bc859658f3663f…`). The full
record, with every sha and the machine-readable changelog, is `results/frozen_v3.json`.

**`intents` in v3 is byte-identical to v2**, deliberately. The operator ruled for the arm on 31
intents disagreements and none of them is applied: the audit's control sample says 22 of 40 agreed
`intents` rows carry a label the operator considers wrong, and 19 of those agreed on the *empty*
set — a disagreement about the annotation law rather than about these 400 rows. Gate 4.5 sent that
question to a face-to-face review; until it is decided, half-relabelling the head against two
readings at once would be worse than leaving it.

**A pair ruling confirms both labels and changes only what differed**: 13 of the 15 G1b rows keep
their `sentiment` and move only `sarcasm`. That is why the changelog below has 39 lines over 37
rows for 38 rulings.

**Three fixed rows amend a v2 operator correction.** `@msuaaaa:8175` — v2 set `sentiment` to
`negative`, v3 sets `positive`; `@VARUS_channel:9797` and `@msuaaaa:5534` — v2 set `sarcasm: true`,
v3 moves their `sentiment`. Recorded here because a signed-off correction that changes in silence
reads as a defect later.

Every changed row carries `annotator: "operator-blind-audit-45a"`.

| file | id | field | v2 | v3 |
|---|---|---|---|---|
| `comments_test_v3.jsonl` | `@VARUS_channel:10221` | `sentiment` | "negative" | "neutral" |
| `comments_test_v3.jsonl` | `@VARUS_channel:11424` | `sentiment` | "negative" | "neutral" |
| `comments_test_v3.jsonl` | `@VARUS_channel:12833` | `sentiment` | "negative" | "neutral" |
| `comments_test_v3.jsonl` | `@VARUS_channel:14969` | `sentiment` | "positive" | "neutral" |
| `comments_test_v3.jsonl` | `@VARUS_channel:19944` | `sentiment` | "positive" | "neutral" |
| `comments_test_v3.jsonl` | `@VARUS_channel:8087` | `sentiment` | "negative" | "neutral" |
| `comments_test_v3.jsonl` | `@VARUS_channel:8129` | `sentiment` | "negative" | "neutral" |
| `comments_test_v3.jsonl` | `@VARUS_channel:9797` | `sentiment` | "negative" | "neutral" |
| `comments_test_v3.jsonl` | `@msuaaaa:12252` | `sentiment` | "negative" | "positive" |
| `comments_test_v3.jsonl` | `@msuaaaa:12980` | `sentiment` | "negative" | "neutral" |
| `comments_test_v3.jsonl` | `@msuaaaa:13530` | `sentiment` | "neutral" | "negative" |
| `comments_test_v3.jsonl` | `@msuaaaa:4774` | `sentiment` | "negative" | "neutral" |
| `comments_test_v3.jsonl` | `@msuaaaa:4785` | `sentiment` | "negative" | "positive" |
| `comments_test_v3.jsonl` | `@msuaaaa:5534` | `sentiment` | "neutral" | "negative" |
| `comments_test_v3.jsonl` | `@msuaaaa:8175` | `sentiment` | "negative" | "positive" |
| `posts_test_v3.jsonl` | `@VARUS_channel:6737` | `post_type` | "promo" | "other" |
| `posts_test_v3.jsonl` | `@VARUS_channel:9450` | `post_type` | "promo" | "other" |
| `posts_test_v3.jsonl` | `@msuaaaa:10651` | `brands` | [] | [{"brand_id": null, "mention": "KFC"}] |
| `posts_test_v3.jsonl` | `@msuaaaa:5150` | `brands` | [] | [{"brand_id": null, "mention": "McDonald’s"}] |
| `posts_test_v3.jsonl` | `@msuaaaa:8280` | `post_type` | "promo" | "launch" |
| `posts_test_v3.jsonl` | `@msuaaaa:9676` | `post_type` | "other" | "launch" |
| `posts_test_v3.jsonl` | `@msuaaaa:9676` | `brands` | [] | [{"brand_id": null, "mention": "Roshen"}] |
| `posts_test_v3.jsonl` | `@silposilpo:3558` | `post_type` | "launch" | "promo" |
| `sarcasm_holdout_v3.jsonl` | `@VARUS_channel:10046` | `sarcasm` | true | false |
| `sarcasm_holdout_v3.jsonl` | `@VARUS_channel:10064` | `sarcasm` | true | false |
| `sarcasm_holdout_v3.jsonl` | `@VARUS_channel:11849` | `sarcasm` | true | false |
| `sarcasm_holdout_v3.jsonl` | `@VARUS_channel:14785` | `sarcasm` | true | false |
| `sarcasm_holdout_v3.jsonl` | `@VARUS_channel:16281` | `sarcasm` | true | false |
| `sarcasm_holdout_v3.jsonl` | `@VARUS_channel:16728` | `sarcasm` | true | false |
| `sarcasm_holdout_v3.jsonl` | `@VARUS_channel:18066` | `sarcasm` | true | false |
| `sarcasm_holdout_v3.jsonl` | `@VARUS_channel:2181` | `sarcasm` | true | false |
| `sarcasm_holdout_v3.jsonl` | `@VARUS_channel:2953` | `sarcasm` | true | false |
| `sarcasm_holdout_v3.jsonl` | `@VARUS_channel:2989` | `sarcasm` | true | false |
| `sarcasm_holdout_v3.jsonl` | `@VARUS_channel:3342` | `sarcasm` | true | false |
| `sarcasm_holdout_v3.jsonl` | `@VARUS_channel:3551` | `sarcasm` | true | false |
| `sarcasm_holdout_v3.jsonl` | `@VARUS_channel:7389` | `sarcasm` | true | false |
| `sarcasm_holdout_v3.jsonl` | `@msuaaaa:7500` | `sentiment` | "negative" | "neutral" |
| `sarcasm_holdout_v3.jsonl` | `@msuaaaa:7500` | `sarcasm` | true | false |
| `sarcasm_holdout_v3.jsonl` | `@msuaaaa:7907` | `sarcasm` | true | false |

## Changelog

**Train-source recalibration — 2026-07-27.** The v2 corrections landed on the test set only,
which left the training data measurably worse labelled than the test set on the very axis G1b
scores. Every scoreable `sarcasm: false` row of the two train sources that fires the irony
heuristics of `market_pulse.sarcasm` was read again under the v2 calibration — 908 candidates,
labelled in chunks of 100 with the validator after each. Changed rows carry `annotator:
"llm-recheck-v2"`.

| file | candidates | rows changed | sarcasm before | after |
|---|---|---|---|---|
| `data/frozen/comments_train.jsonl` | 286 | 60 | 37 | 97 |
| `data/annotation/sarcasm_candidates.jsonl` | 622 | 37 | 178 | 215 |

The sarcastic share of the scorable train pool moves from 4.1% to 10.7%, against 13.0% in the
test set — the two calibrations now agree to within a couple of points instead of a factor of
three. The test set is untouched: it stays at its v2 hash. The corrections were also synced
upstream into `data/annotation/comments_batch.jsonl` by `scripts/sync_batch_v2.py`, so a
forced rebuild cannot resurrect a pre-v2 label; the recalibration itself is deliberately not
synced back, the batch remains the 2d-2 record.

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

Training reads **three** files, not one. Reconstructing the training data from the frozen set
alone silently drops 800 hand-labelled rows — and the third file is not hand-labelled at all.

| file | rows | scorable | sha256 |
|---|---|---|---|
| `data/frozen/comments_train.jsonl` | 1600 | 906 | `4b6ea7f354bcc396ee526ce193c445bb358fab1d070bbe429dfdeb3bace1a1d7` |
| `data/annotation/sarcasm_candidates.jsonl` | 746 | 540 | `44cd226245bc5f6fd5ecd2edd588d4a77c6ae9faca024af42787f4f1f4279423` |
| `data/annotation/synthetic_sarcasm.jsonl` **ABLATION-GATED, QA-pending** | 600 | 600 | `f037f62bb9e0680501d53f72fed50a146eb6faae63c13afcc354e8f55871efb3` |

### The third source is generated, and conditional

`data/annotation/synthetic_sarcasm.jsonl` is 600 sarcastic comments written by an LLM session on
2026-07-28, not collected and not hand-labelled
(`knowledge/decisions/synthetic-sarcasm-augmentation.md`). Two conditions travel with it:

- **ABLATION-GATED.** Phase 4 trains with and without it and keeps it only if the gates improve.
  It stays a separate file for exactly that reason; every row also carries a `synthetic:NNNN` id
  and `source_id: "synthetic"`, so a merge into a real source would still be visible.
- **QA-pending.** 50 rows (seed 42) are exported by `scripts/make_synthetic_qa.py` to
  `data/annotation/synthetic_qa.csv`; the pre-registered gate is **≥80% `ok`** from the operator,
  and below that the flagged failure patterns are regenerated once. **No QA number exists yet** —
  the sample has been exported, not scored, and the executor does not score it (SPEC §10).

It is never in a test set or in the G1b holdout, and `scripts/check_synthetic.py` enforces that
from the other side: no row is a verbatim or near-verbatim (word-3-gram Jaccard ≥ 0.50) copy of
any row in the six real comment files, including `comments_test.jsonl` and
`sarcasm_holdout.jsonl`. The same check bounds internal near-duplicates (≥ 0.60), caps any single
two-word opening or closing at 8% of the file, and refuses a capitalised mid-sentence word that is
not a registry brand or chain.

Written to the proportions measured from the 230 real sarcastic scoreable training rows — the
targets, and what the file actually holds:

| property | real (n=230) | generated (n=600) |
|---|---|---|
| UA : RU | 67 : 26 (+7 `other`) | 70 : 30 |
| negative / neutral | 96.5% / 3.0% | 96.0% / 4.0% |
| no intent at all | 52.6% | 49.2% |
| price · availability · quality · packaging · taste | 30% · 17% · 6% · 3% · 1% | 30% · 17% · 7% · 3% · 1% |
| emoji · `))` | 43% · 12% | 39% · 7% |
| words: p25 / median / p75 / max | 8 / 13 / 27 / 168 | 7 / 12 / 20 / 37 |

The length tail is the one target the file cannot match: the generation brief caps a row at 40
words, and the real corpus' p75 of 27 is produced by complaints that run past 100. Median and the
lower quartile agree; above p75 the generated rows are systematically shorter, and a model trained
on them sees fewer long-form ironic complaints than the corpus contains.

The mined pool (`scripts/mine_sarcasm_candidates.py`) is a training source only — it is
excluded from the test set by construction, and its hash is a snapshot, not a freeze: unlike
the four files above it may be extended by mining deeper. It lost 54 rows to the holdout on
2026-07-28 (800 → 746); those rows are training data no longer.

**`data/annotation/sarcasm_holdout_pool.jsonl` (971 rows) is not a training source.** It is
the wave-2 mining pool the holdout was cut from; its 617 scorable non-sarcastic rows sit in
the same threads as holdout rows, so training on them would leak the holdout. It is kept
labelled for error analysis and for any future holdout extension.

## Sarcasm holdout (G1b)

**Frozen 2026-07-28, immutable without operator approval** — same rule as the four files
above. Approved by the operator as option 1a after the fresh-corpus-only holdout was shown to
be unreachable.

| file | rows | sha256 |
|---|---|---|
| `data/frozen/sarcasm_holdout.jsonl` | 108 | `f83a6cf0fecd0bb266f851803107771309b17d946719cb6da3ca4ff614cb37c3` |

Every row is `sarcasm: true`, `unclear: false`. SPEC amendment 3.2 scores the zero-shot base
model on this file at Phase 3; the G1b slice is the subset the base model gets wrong, so the
slice is smaller than 108 by however often the base model is right.

| origin | rows | ua | ru | other | sentiment |
|---|---|---|---|---|---|
| fresh corpus (wave 2) | 54 | 32 | 13 | 9 | 53 negative, 1 positive |
| moved out of the mined pool | 54 | 34 | 16 | 4 | 54 negative |
| **total** | **108** | **66** | **29** | **13** | 107 negative, 1 positive |

The single positive row is a mock reproach that means praise — sarcasm is a flag, not a
sentiment (`docs/annotation/comments.md`).

### Why 108 and not 180

`scripts/mine_sarcasm_holdout.py` swept the corpus for comments in threads disjoint from both
the test set and the scoreable train pool: 7,224 comments with text → 4,424 unlabelled →
1,068 outside those threads → 971 candidates after dropping verbatim copies of labelled texts
and repeats. All 971 were labelled (`annotator: llm-holdout`, v2 calibration); 54 came out
sarcastic and scoreable. Wave 1 had already skimmed the marked rows — only 89 of the 971 fire
an irony heuristic at all.

The top-up is bounded harder than it looks. Of the 187 sarcastic scoreable rows in the mined
pool, **131 share a thread with a scoreable `comments_train.jsonl` row** and 2 repeat a
training row's text verbatim; moving any of them would leak a thread that stays in training,
and train rows may not be removed. That leaves 54 movable, all of which were taken — seed 42
would only have chosen between them if more had been eligible.

### What training keeps

| source | sarcastic scoreable rows |
|---|---|
| `data/frozen/comments_train.jsonl` | 97 |
| `data/annotation/sarcasm_candidates.jsonl` (after the move) | 133 |
| **total** | **230** |

These 230 are the *real* sarcastic rows, and they are the reason the generated third source
exists. Counting `synthetic_sarcasm.jsonl` here would blur exactly the line the ablation has to
cut along, so it stays out of this table.

### Leakage, and the one residual

Checked independently of the freeze script: 0 holdout ids in the test set, the train pool or
the mined pool · 0 threads shared with the test set · 0 threads shared with the scoreable
train pool · 0 verbatim text overlap with any remaining training row.

**Residual:** 25 holdout threads still hold a scoreable row of the mined training pool — 31
of the 108 holdout rows. Wave 1 excluded test threads only, so its rows are spread through
threads this holdout also draws from, and the approved change allows removing moved rows from
the mined pool and nothing else. Closing it would mean either dropping those 31 holdout rows
or pulling their mined thread-mates out of training; both need a new operator decision.

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
| G1b | sarcasm | scored on the holdout, not here (amendment 3.2): 108 rows, of which the slice is whatever the base model gets wrong. The test set's own 52 sarcastic rows stay in the overall macro-F1 |
| G1c | packaging intent | 19 |
| G1d | relevant posts | 26 |
| G1e | brand mentions | 36 |

- **G1a's 2 pp per-language margin is thinner than it looks**: on RU (n=86) 2 pp is under
  two rows, so a per-language verdict there is one or two comments wide.
- **`language: other` is 66 test rows** — the langid heuristic's failures, not a fourth
  language. They are scored in the overall macro-F1 and in no per-language gate.
- **EN rounds out again**: 2 scorable EN comments across the strata gave it 0 test rows.
  Expected under amendment 3.1, noted so it is not a surprise twice.
- **Test and train are now calibrated alike, but by different hands.** The test set carries
  the operator's judgement (11 rows); the train sources carry the recalibration described in
  the changelog (97 rows), read from the operator's 22 corrections as worked examples. If the
  two ever disagree, the test set is the authority.
- **The test set has now been through two operator passes, and 326 rows through neither.**
  64 rows were in the 2d-2 review sample (1 correction); the v2 pass corrected 11 further
  rows, none of them from that sample. 11 rows carry `annotator: "operator-reviewed"`. The
  remaining 326 were labelled before either pass showed that sarcasm and negativity were
  under-flagged, and the 2d-2 review measured that error rate at 2.3% per field — on RU
  (n=86) that is ~1.7 rows, the same width as G1a's 2 pp per-language margin. **Read the
  per-language clause of G1a as noise-dominated unless those 326 rows are reviewed too.**
- The mined pool (`scripts/mine_sarcasm_candidates.py`) is labelled under the corrected
  calibration, so it feeds training, never this test set.
