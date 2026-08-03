"""The v2ctx probe's two denominators, its rendering table and the gate they feed.

The revision this phase measures is invisible to every field a record normally verifies: the
prompt text does not move, so the prompt hash does not move. What identifies the run is the
committed plan — which rows render which line, and which rulings the gate is allowed to count.
So the tests here are about *membership* more than about arithmetic: the gated denominator has
to be the refusals a feature explains, not the larger set it co-occurs with, and the 60 rows no
verdict ever touched have to still equal the labels the sitting judged.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import plan_v2ctx_probe as plan  # noqa: E402

from market_pulse import prompts  # noqa: E402

PLAN = REPO_ROOT / "results" / "v2ctx_probe_plan.json"
FEATURES = REPO_ROOT / "results" / "features_45g5.json"
V22_PLAN = REPO_ROOT / "results" / "v22_probe_plan.json"

PACK = {"sentiment": "neutral", "sarcasm": False, "intents": ["price"], "unclear": False}


def row(row_id, gated_as, *, ruling=None, feature=False, reply=False, sender=None):
    return {
        "id": row_id,
        "gated_as": gated_as,
        "reference": dict(PACK),
        "ruling": dict(ruling or {}),
        "feature_named": feature,
        "reply": reply,
        "sender": sender,
    }


@pytest.fixture(scope="module")
def committed():
    return json.loads(PLAN.read_text(encoding="utf-8"))


def test_the_gated_denominator_is_explanation_and_the_rest_is_reported():
    """Two rows, one ruling each, one of them explained by a feature. The gate sees one."""
    rows = [
        row("@c:1", "fixed", ruling={"unclear": True}, feature=True, reply=True),
        row("@c:2", "fixed", ruling={"unclear": True}, feature=False, reply=True),
    ]
    got = plan.by_feature(rows, {"@c:1": {**PACK, "unclear": True}})
    assert got["feature_named"] == {
        "n": 1,
        "landed": 1,
        "landed_ids": ["@c:1"],
        "missed_ids": [],
    }
    assert got["not_feature_named"]["n"] == 1 and got["not_feature_named"]["landed"] == 0
    assert got["not_feature_named"]["missed_ids"] == ["@c:2"]


def test_an_unanswered_row_is_a_miss_and_not_a_dropped_row():
    """A row the run could not read counts against the denominator it was registered on."""
    rows = [row("@c:1", "fixed", ruling={"unclear": True}, feature=True)]
    got = plan.by_feature(rows, {})
    assert got["feature_named"]["n"] == 1 and got["feature_named"]["landed"] == 0
    assert got["feature_named"]["missed_ids"] == ["@c:1"]


def test_a_ruling_landed_while_another_field_moved_is_not_fixed():
    """4.5g4's definition, unchanged: the named fields are the ruling and the rest is the pack."""
    rows = [row("@c:1", "fixed", ruling={"unclear": True}, feature=True)]
    partial = {**PACK, "unclear": True, "sentiment": "positive"}
    assert plan.by_feature(rows, {"@c:1": partial})["feature_named"]["landed"] == 0


def test_the_family_split_names_the_feature_that_explains_each_row():
    rows = [
        row("@c:1", "fixed", ruling={"unclear": True}, feature=True, reply=True),
        row("@c:2", "fixed", ruling={"unclear": True}, feature=True, sender="@msuaaaa"),
        row("@c:3", "fixed", ruling={"unclear": True}, feature=True, reply=True, sender="@msuaaaa"),
        row("@c:4", "fixed", ruling={"unclear": True}, feature=False, reply=True),
    ]
    split = plan.per_family(rows, {"@c:1": {**PACK, "unclear": True}})
    assert sorted(split) == ["both", "reply", "sender"]
    assert split["reply"] == {"n": 1, "landed": 1, "ids": ["@c:1"]}
    assert split["sender"]["landed"] == 0 and split["both"]["ids"] == ["@c:3"]
    assert sum(block["n"] for block in split.values()) == 3, "the unexplained row is not in here"


@pytest.mark.parametrize(
    ("preserved", "fixed", "expected"),
    [
        (58, 17, "PASS"),
        (55, 12, "PASS"),
        (54, 12, "OPERATOR-DECIDES"),
        (55, 11, "OPERATOR-DECIDES"),
        (51, 17, "KILL"),
        (58, 8, "KILL"),
        (52, 9, "OPERATOR-DECIDES"),
    ],
)
def test_the_gate_bands_are_read_off_the_committed_thresholds(
    preserved, fixed, expected, committed
):
    counts = {"preserved": {"kept": preserved}, "feature_named": {"landed": fixed}}
    assert plan.verdict(counts, committed["gate"]) == expected


def test_the_committed_plan_is_the_same_hundred_ids_as_the_v22_probe(committed):
    """A fifth paired column is only paired while the ids are the ones the other four asked."""
    assert [row["id"] for row in committed["rows"]] == [
        row["id"] for row in json.loads(V22_PLAN.read_text(encoding="utf-8"))["rows"]
    ]
    assert committed["sample"]["rows"] == 100
    assert (committed["sample"]["refused"], committed["sample"]["accepted"]) == (42, 58)
    assert committed["source"]["sample_from_sha256"], "the plan it drew from is pinned"


def test_the_committed_plan_gates_seventeen_and_reports_twenty_three(committed):
    """The number the whole phase turns on. `feature_named` is `refusals_explained_by_a_feature`
    intersected with the rows that state a value — 17 — and not family membership, which is 23
    and would price co-occurrence as explanation."""
    explained = set(
        json.loads(FEATURES.read_text(encoding="utf-8"))["runs"][-1][
            "refusals_explained_by_a_feature"
        ]
    )
    named = {row["id"] for row in committed["rows"] if row["gated_as"] == "fixed"}
    gated = {row["id"] for row in committed["rows"] if row["feature_named"]}
    assert len(named) == 40 and gated == explained & named and len(gated) == 17
    assert gated <= named, "a gated row without a stated value has no right answer to hit"
    assert committed["gate"]["feature_fixed"]["n"] == 17
    assert committed["gate"]["preserved"]["n"] == 58
    # ceil(0.70*17) = 12, ceil(0.50*17) = 9 — written as integers before the run
    assert committed["gate"]["feature_fixed"]["pass_at"] == 12
    assert committed["gate"]["feature_fixed"]["kill_below"] == 9
    assert committed["gate"]["preserved"] == {"n": 58, "pass_at": 55, "kill_below": 52}
    assert committed["gate"]["attempts"] == 1
    assert "12/17" in committed["gate"]["rule"] and "55/58" in committed["gate"]["rule"]


def test_the_two_rows_no_ruling_reaches_are_ungated(committed):
    ungated = sorted(row["id"] for row in committed["rows"] if row["gated_as"] == "reported_only")
    assert ungated == ["@VARUS_channel:7555", "@msuaaaa:11876"]
    assert all(not row["feature_named"] for row in committed["rows"] if row["gated_as"] != "fixed")


def test_the_plan_scores_its_own_reference_as_a_perfect_preserve_and_no_fix(committed):
    """The control on the scorer: v2 *is* the reference, so it keeps every accepted row and
    lands none of the rulings — those rows were refused precisely because v2 got them wrong."""
    v2 = committed["reference_runs"]["v2 (the labels the sitting judged)"]
    assert v2["preserved"] == {"n": 58, "kept": 58}
    assert v2["feature_named"]["landed"] == 0 and v2["not_feature_named"]["landed"] == 0
    assert (
        committed["reference_points"]["on_feature_named_rulings"][
            "v2 (the labels the sitting judged)"
        ]
        == 0
    )


def test_the_briefings_reference_point_is_reconciled_rather_than_repeated(committed):
    """The briefing says v2.2 scored 2 on the feature-named rulings; under this plan's own
    definitions it scores 3. The extra row is real and the disagreement is written down."""
    v22 = committed["reference_runs"]["v2.2 (results/v22_probe_rows.jsonl)"]
    assert v22["feature_named"]["landed"] == 3
    assert committed["reference_points"]["briefing_said"]["v2.2"] == 2
    assert "6239" in committed["reference_points"]["briefing_said"]["computed_here"]


def test_the_rendering_is_pinned_because_the_prompt_hash_cannot_see_it(committed):
    """`precheck_v2ctx_with_post` hashes to `precheck_v2_with_post`. The templates hash and the
    per-row flags are the only things in the record that identify this run."""
    assert committed["rendering"]["prompt_sha256"] == prompts.prompt_sha256("precheck_v2_with_post")
    assert committed["rendering"]["templates"] == list(prompts.CONTEXT_TEMPLATES)
    counts = committed["rendering"]
    flags = committed["rows"]
    assert counts["rows_with_reply"] == sum(1 for row in flags if row["reply"])
    assert counts["rows_with_sender"] == sum(1 for row in flags if row["sender"])
    assert counts["rows_with_neither"] == sum(
        1 for row in flags if not row["reply"] and not row["sender"]
    )
    assert counts["rows_with_reply"] + counts["rows_with_sender"] - counts["rows_with_both"] == (
        100 - counts["rows_with_neither"]
    )
    for row in flags:
        assert row["sender"] in (None, "@VARUS_channel", "@msuaaaa")


def test_the_byte_identity_row_carries_no_feature(committed):
    """The check the plan ran is only worth having on a row that would actually render nothing."""
    checked = committed["rendering"]["byte_identity_checked_on"]
    row = next(item for item in committed["rows"] if item["id"] == checked)
    assert not row["reply"] and row["sender"] is None


def test_the_batch_the_plan_measured_is_the_one_the_verdicts_left(committed):
    """The chain, in place of a rebuild that can no longer reproduce the sealed sha."""
    chain = json.loads((REPO_ROOT / "results" / "verdicts_45g6.json").read_text())["runs"][-1]
    assert committed["source"]["batch_sha256"] == chain["batch_sha256_after"]
    assert committed["sample"]["unadjudicated_and_unmoved"] == plan.UNTOUCHED_ROWS == 60
    assert committed["source"]["sealed_sha256"], "the pack the reference labels came from"


def test_the_rulings_of_both_phases_merge_per_row():
    """9271 is adjudicated twice — `unclear` in 4.5g5, `intents` in 4.5g6 — and the row it is
    scored against has to carry both, or the newer ruling would score against a stale target."""
    merged = plan.rulings()
    assert len(merged) == 40
    assert merged["@VARUS_channel:9271"] == {"unclear": False, "intents": ["service"]}
    assert "@VARUS_channel:7555" not in merged and "@msuaaaa:11876" not in merged
