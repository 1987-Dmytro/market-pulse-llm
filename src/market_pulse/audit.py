"""The 4.5a error audit — what a head is, how a row is blinded, how a ceiling is read.

SPEC amendment 3.7 asks a question the gates cannot answer: the operator's 0.98
target sits above the instrument, because gold was calibrated at 96.3% agreement.
The audit measures the instrument instead of arguing about it — the operator
rules disagreement rows blind, and this module turns those rulings into numbers.

Three ideas live here and nowhere else, because the builder and the harness must
agree on all three or the audit measures two different things:

- **a head is a comparable value.** ``value`` maps a labels dict — gold row or
  prediction, they share their key names — to the canonical object the head's
  gate compares. Sets for the multi-label heads, the normalised brand token for
  G1e, the ``(sentiment, sarcasm)`` pair for the G1b slice, because a slice row
  leaves the base model's error union only when *both* labels are right.
- **blinding is a per-row coin flip, and nothing else.** ``render`` is the only
  place a label becomes text, so both candidates in a row go through one
  function: a rendering that differs by side is an attribution channel the CSV's
  vocabulary check would never catch.
- **the ceiling is arithmetic over two strata**, and the agreement stratum is
  seen only through a small control sample. ``ceiling`` extrapolates it and says
  so; it never pretends the control's n is the stratum's n.

Pure: no path, no file, no random source of its own. The scripts own those.
"""

import json
from collections.abc import Iterable

from market_pulse.scorer import UNCLEAR, normalise_brand

HEADS = ("sentiment", "intents", "sarcasm_pair", "post_type", "brands")
"""Every head the audit adjudicates, in pack order. Not the gate ids: G1d and G1e
share one input and one CSV, and G1b's head is a label *pair*."""

GATE_OF = {
    "sentiment": "G1a",
    "intents": "G1c",
    "sarcasm_pair": "G1b",
    "post_type": "G1d",
    "brands": "G1e",
}

INPUT_OF = {
    "sentiment": "comments_test",
    "intents": "comments_test",
    "sarcasm_pair": "sarcasm_holdout",
    "post_type": "posts_test",
    "brands": "posts_test",
}

CSV_OF = {
    "sentiment": "comments_sentiment.csv",
    "intents": "comments_intents.csv",
    "sarcasm_pair": "slice_unfixed.csv",
    "post_type": "posts.csv",
    "brands": "posts.csv",
}

VERDICTS = ("A", "B", "ambiguous")
"""Disagreement vocabulary. `A` / `B` name columns, never sides of the comparison."""

CONTROL_VERDICTS = ("correct", "incorrect", "ambiguous")
"""Agreement vocabulary: the shown label is right, wrong, or undecidable."""

COLUMNS = ("head", "id", "text", "label_A", "label_B", "verdict", "notes")
CONTROL_COLUMNS = ("head", "id", "text", "label", "verdict", "notes")
"""The exact shape of a pack CSV, shared so the harness can refuse anything else.

A spreadsheet round-trip is the realistic way a column appears — an autofilled
helper column, a stray paste — and a harness that reads by name would not notice.
The pack's columns are part of the sealed artifact, like the labels are."""

ATTRIBUTION = ("model", "gold", "pred", "truth", "arm", "модел", "эталон", "золот")
"""Words that would say which side a label came from. Checked against column
names and every structural cell, never against the row's own ``text``: a comment
is free to contain any of these, and dropping such rows would bias the pack."""


def value(head: str, labels: dict, aliases: dict[str, str]):
    """The canonical object this head compares — same function for gold and prediction.

    ``aliases`` is only read by ``brands``; the other heads ignore it. Passing it
    everywhere keeps the call site uniform, which is what stops a caller from
    normalising one side of a comparison and not the other.
    """
    if head == "sentiment":
        return labels["sentiment"]
    if head == "intents":
        return frozenset(labels["intents"])
    if head == "sarcasm_pair":
        return (labels["sentiment"], bool(labels["sarcasm"]))
    if head == "post_type":
        return labels["post_type"]
    if head == "brands":
        return frozenset(normalise_brand(entry, aliases) for entry in labels["brands"])
    raise KeyError(f"unknown head {head!r}: the pack and the harness must share {HEADS}")


def scoreable(head: str, gold: dict) -> bool:
    """Whether the gates score this gold row — the scorer's ``unclear`` rule, row-wise.

    :func:`market_pulse.scorer._drop_unclear` drops these rows column-wise at gate
    time; the audit has to drop the same ones, or the operator spends an evening
    ruling rows no gate will ever read.
    """
    if head in ("sentiment", "post_type"):
        return gold[head] != UNCLEAR
    if head in ("intents", "brands"):
        return gold[head] is not None
    if head == "sarcasm_pair":
        return gold["sentiment"] != UNCLEAR and gold["sarcasm"] is not None
    raise KeyError(f"unknown head {head!r}")


def render(head: str, canonical) -> str:
    """The canonical value as the one string both candidates are shown as.

    Sets are sorted and JSON-encoded so that ``{"price", "taste"}`` and
    ``{"taste", "price"}`` are the same cell: an unordered value rendered in
    iteration order would leak which side built it.
    """
    if head in ("sentiment", "post_type"):
        return canonical
    if head in ("intents", "brands"):
        return json.dumps(sorted(canonical), ensure_ascii=False)
    if head == "sarcasm_pair":
        sentiment, sarcasm = canonical
        return f"sentiment={sentiment}; sarcasm={str(sarcasm).lower()}"
    raise KeyError(f"unknown head {head!r}")


def blind(rng) -> str:
    """Which column holds the model's label on this row — ``"A"`` or ``"B"``.

    One draw per disagreement row from a seeded generator, so a rebuild
    reproduces the pack byte for byte and the key stays the only way back.
    """
    return "A" if rng.random() < 0.5 else "B"


def disagreements(
    head: str, rows: Iterable[dict], predicted: dict[str, dict], aliases: dict[str, str]
) -> list[dict]:
    """Scoreable rows where this head's gold and prediction differ.

    Returns ``{"id", "text", "gold", "model"}`` with both labels already
    rendered — the caller decides which column each goes in.
    """
    out = []
    for row in rows:
        if not scoreable(head, row):
            continue
        if row["id"] not in predicted:
            raise ValueError(f"{row['id']} is in {INPUT_OF[head]} but the arm never scored it")
        gold = value(head, row, aliases)
        model = value(head, predicted[row["id"]], aliases)
        if gold != model:
            out.append(
                {
                    "id": row["id"],
                    "text": row["text"],
                    "gold": render(head, gold),
                    "model": render(head, model),
                }
            )
    return out


def agreements(
    head: str, rows: Iterable[dict], predicted: dict[str, dict], aliases: dict[str, str]
) -> list[dict]:
    """Scoreable rows where gold and prediction match — the control stratum's pool.

    This is the half of the test set no disagreement can reach: where model and
    gold are wrong the *same* way, nothing flags it, and the only way to see it
    is to sample and ask.
    """
    out = []
    for row in rows:
        if not scoreable(head, row):
            continue
        gold = value(head, row, aliases)
        if gold == value(head, predicted[row["id"]], aliases):
            out.append({"id": row["id"], "text": row["text"], "label": render(head, gold)})
    return out


def ceiling(
    total: int,
    disagreement_n: int,
    gold_wrong: int,
    disagreement_ambiguous: int,
    control_n: int,
    control_incorrect: int,
    control_ambiguous: int,
) -> dict:
    """A head's ceiling in accuracy units, from the two strata.

    A perfect model outputs the truth and is scored against gold, so it loses
    exactly the rows where gold is not the truth:

    - **disagreements** are fully observed — ``gold_wrong`` is a count, not a
      rate, and needs no extrapolation;
    - **agreements** are seen through ``control_n`` sampled rows, so their share
      is extrapolated over the whole stratum. This is the term that carries the
      estimate's uncertainty: the stratum is most of the test set and the sample
      is a few dozen rows.

    Ambiguous rows are reported as a band rather than folded into one number: a
    perfect model may lose all of them or none, and pretending to know which
    would put the audit's own uncertainty inside its point estimate.

    Returns the two bounds plus the extrapolated row counts they come from.
    """
    if control_n <= 0:
        raise ValueError("the agreement stratum needs a control sample: nothing to extrapolate")
    if disagreement_n > total:
        raise ValueError(f"{disagreement_n} disagreements in a stratum of {total} rows")
    agreement_n = total - disagreement_n
    lost_gold = gold_wrong + agreement_n * control_incorrect / control_n
    lost_ambiguous = disagreement_ambiguous + agreement_n * control_ambiguous / control_n
    return {
        "agreement_n": agreement_n,
        "lost_gold": lost_gold,
        "lost_ambiguous": lost_ambiguous,
        "high": 1 - lost_gold / total,
        "low": 1 - (lost_gold + lost_ambiguous) / total,
    }
