---
type: decision
id: dec-2026-08-02-taxonomy-v2-relabel-and-appetite
date: 2026-08-02
status: accepted
tags: [decision]
---

# Taxonomy v2: the up-label appetite, three boundary calls, and how the re-label is staged

**Context:** SPEC amendment 3.8 added a sixth intent, `service`, and pre-registered the work that
follows it — guideline v2, an intents re-label of all labelled data with operator calibration, test
v4, a fresh G1c anchor, one retrain. Phase 4.5d prepared and priced that work and measured what the
corpus can still give (`docs/taxonomy-v2-prep.md`): **1,912** labelable rows left, **zero** sarcasm
candidates among them, a full re-label at **$0.000162 a row**, and — on the rows a gate actually
scores — 64% of intent sets changed, 40% carrying `service`, 24% changed without gaining it. The
4.5d gate (operator, 2026-08-02) decided the appetite off those numbers.

## (a) Appetite: all 1,912, and not before the re-label is calibrated

**Take every labelable row.** That is the +2k tier in all but name, reached without waiting for
collection: training grows from 2,346 comment rows to ~4,258 (+81%). The three pre-registered tiers
were all out of reach — +2k by 88 rows, +9k by 7,088 — and the corpus refills at ~443 labelable
rows a month from the only two channels with comments enabled.

**Sequencing is part of the decision.** No row is up-labelled until this re-label passes the
pre-registered ≥90% agreement check. Labelling 1,912 rows against a law that has not been validated
would put the operator's hours behind an unverified boundary, and a failed calibration would send
all of them back rather than the 100-row sample.

**The corpus is mined out for sarcasm**, so G1b cannot be improved with data from it at any
appetite. Not one row of the pool scores 3 on the irony heuristic and the highest score in it is 1;
more sarcastic rows need a new source. That is a Phase 5 briefing question and is not reopened here
([[phase4-gate-verdict]] closed G1b's own gate).

## (b) The three boundary calls in guideline v2, ratified as written

Amendment 3.8 approved the class and its wide boundary; these three rows it did not decide, and
each is now law that thousands of rows are labelled against. The gate ratified all three:

| row | v1 | v2 | why |
|---|---|---|---|
| `@VARUS_channel:5951` — the shashlik promo refused at the till | `["price","availability"]` | `["price","service"]` | the product was there; the refusal is the process around it |
| `docs/annotation/comments.md` sarcasm example 2 — `Знову виграв працівник компанії` | `[]` | `["service"]` | a rigged-draw accusation is promo *mechanics*, which the wide boundary keeps |
| sarcasm example 3 — `ми знову в прольоті` | `["availability"]` | `["service"]` | the row sits under a giveaway post; its v1 label was wrong under v1 too |

The second is the one the amendment recorded as **correct** under the old law: under a narrow
boundary it would stay `[]`, and the gate chose the wide one knowingly. The first is a row of
`data/frozen/comments_test.jsonl`, so the ruling is law here and reaches the row itself in 4.5f —
the guideline quotes it as an example, and nothing in this step relabels it.

## (c) How a re-labelled row is staged

- **v2 copies beside the originals**, never a file mutated in place — the convention the frozen
  test sets already use (`_v3` beside v2, [[test-v3]]). A labelled file is a read-only input to
  this step.
- **`annotator` is never rewritten.** A re-labelled row still says who labelled it; what moved its
  intents lives in the run record (`results/relabel_45e.json`) and nowhere else. Test v3 took the
  opposite convention and stamped `operator-blind-audit-45a` on every row it fixed, because there a
  *human* ruled each row. Here a model moved one column with no human in the loop yet, and a row
  that claimed otherwise would be claiming a provenance it does not have.
- **One column moves and it is proved, not promised.** Every produced line has the old intents put
  back and must then reproduce its source line byte for byte, or the run stops.
- **The re-label set is all labelled data, `unclear` rows included** (amendment 3.8). Skipping the
  `unclear` rows would save $0.16 and leave two taxonomies in one column.
- **Frozen test and holdout rows are not in this step.** The code guard that refuses them stays in
  place; test v4 (4.5f) lifts it as an explicit code change, not a flag.

## (d) Provenance

| what | value |
|---|---|
| the numbers this decision was made on | `docs/taxonomy-v2-prep.md`, `results/uplabel_candidates.json`, `results/relabel_probe_45d.json` |
| the law | `docs/SPEC.md` amendment 3.8, `docs/annotation/comments.md` (guideline v2) |
| the gate | operator, 2026-08-02 — recorded in `docs/STATUS.md` |
| the re-label | `scripts/relabel_intents.py --phase 45e`, ledger `results/spend_45e.json`, cap $1.50 |
| calibration | `scripts/build_calibration_pack.py` → `results/calib_45e_manifest.json` |

Related: [[test-v3]] — the staging convention this follows and the `intents` question it left open;
[[phase45a-ceiling]] — the audit that raised the law question; [[testset-refreeze-v2]] — the first
time gold moved and the discipline it set.
