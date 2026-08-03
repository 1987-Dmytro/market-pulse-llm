"""The v2.2 probe's definitions, exercised before the probe is bought.

The thresholds are pre-registered and unrepeatable — one attempt, no retry — so the arithmetic
that applies them has to be right the first time. What is checked here is the part a re-run
cannot rescue: which rows count towards which denominator, what "fixed" means when a ruling
names one field out of four, and what an unanswered row does to a rate.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import plan_v22_probe as plan  # noqa: E402

PLAN = REPO_ROOT / "results" / "v22_probe_plan.json"
GATES = REPO_ROOT / "results" / "sitting_45g_gates.json"

PACK = {"sentiment": "neutral", "sarcasm": False, "intents": ["price"], "unclear": False}


def row(row_id, gated_as, reference=None, ruling=None):
    return {
        "id": row_id,
        "gated_as": gated_as,
        "reference": dict(reference or PACK),
        "ruling": dict(ruling or {}),
    }


def test_a_fixed_row_needs_the_ruling_and_the_rest_of_the_pack():
    """The whole point of scoring the unnamed fields too. A revision that answers the ruling
    and relabels something else on the way past is the 4.5g3 failure in miniature."""
    rows = [row("@c:1", "fixed", ruling={"unclear": True})]
    want = plan.target(PACK, {"unclear": True})
    assert want == {**PACK, "unclear": True}

    landed = plan.score(rows, {"@c:1": want})
    assert landed["fixed"] == {"n": 1, "landed": 1} and landed["named_field_only"] == []

    drifted = plan.score(rows, {"@c:1": {**want, "intents": ["service"]}})
    assert drifted["fixed"] == {"n": 1, "landed": 0}, "the ruling landed, the row still moved"
    assert drifted["named_field_only"] == ["@c:1"], "and the secondary counter has to see it"

    wrong = plan.score(rows, {"@c:1": {**PACK, "intents": ["service"]}})
    assert wrong["fixed"]["landed"] == 0 and wrong["named_field_only"] == []


def test_an_unanswered_row_is_not_a_preserved_one():
    """A rate over the rows that happened to come back is a rate over a sample chosen after
    the fact. The denominator is the one the plan registered."""
    rows = [row("@c:1", "preserved"), row("@c:2", "preserved")]
    counts = plan.score(rows, {"@c:1": PACK})
    assert counts["preserved"] == {"n": 2, "kept": 1}
    assert counts["preserved_lost"] == ["@c:2"] and counts["answered"] == 1


def test_intents_compare_as_a_set_and_every_other_field_as_itself():
    rows = [row("@c:1", "preserved", reference={**PACK, "intents": ["price", "taste"]})]
    assert plan.score(rows, {"@c:1": {**PACK, "intents": ["taste", "price"]}})["preserved"]["kept"]
    assert not plan.score(rows, {"@c:1": {**PACK, "intents": ["price"]}})["preserved"]["kept"]


def test_a_reported_only_row_gates_nothing_and_is_still_counted():
    """Thirteen refusals name the error without naming the value. They cannot be scored — but
    a row that vanishes from the report is a row nobody notices moved."""
    rows = [row("@c:1", "reported_only"), row("@c:2", "reported_only")]
    counts = plan.score(rows, {"@c:1": {**PACK, "unclear": True}, "@c:2": PACK})
    assert counts["ungated_moved"] == ["@c:1"] and counts["ungated_unmoved"] == ["@c:2"]
    assert counts["preserved"]["n"] == 0 and counts["fixed"]["n"] == 0


@pytest.mark.parametrize(
    "preserved,fixed,expected",
    [
        (58, 29, "PASS"),
        (55, 24, "PASS"),  # both thresholds exactly met
        (54, 29, "OPERATOR-DECIDES"),  # one short of PASS, above KILL
        (55, 23, "OPERATOR-DECIDES"),
        (52, 20, "OPERATOR-DECIDES"),  # the KILL line is strict: below, not at
        (51, 29, "KILL"),
        (58, 19, "KILL"),
    ],
)
def test_the_gate_bands_are_read_off_the_thresholds_as_written(preserved, fixed, expected):
    counts = {"preserved": {"kept": preserved}, "fixed": {"landed": fixed}}
    assert plan.verdict(counts) == expected


def test_the_committed_plan_samples_every_refused_row_and_a_seeded_58():
    """The sample is the one thing the run cannot be allowed to choose. Re-derived from the
    gate record rather than trusted, because a plan that quietly listed 99 ids would still
    produce a table that looks like a gate."""
    committed = json.loads(PLAN.read_text(encoding="utf-8"))
    gates = json.loads(GATES.read_text(encoding="utf-8"))
    refused, accepted = plan.sample(gates)
    assert [r["id"] for r in committed["rows"]] == refused + accepted
    assert len(refused) == 42 and len(accepted) == 58
    assert set(refused) == {r["id"] for r in gates["rows"] if r["verdict"] == "incorrect"}
    assert set(refused) & set(accepted) == set()
    counts = {"preserved": 0, "fixed": 0, "reported_only": 0}
    for entry in committed["rows"]:
        counts[entry["gated_as"]] += 1
    assert counts == {"preserved": 58, "fixed": 29, "reported_only": 13}
    assert sum(committed["sample"]["by_stratum"].values()) == 100


def test_the_plan_scores_its_own_reference_labels_as_a_perfect_preserve():
    """The control on the scorer: v2's labels ARE the reference, so they must preserve every
    accepted row and fix none of the refused ones. A scorer that cannot reproduce that is
    measuring something other than agreement with the pack."""
    committed = json.loads(PLAN.read_text(encoding="utf-8"))
    v2 = committed["reference_runs"]["v2 (the labels the sitting judged)"]
    assert v2["preserved"] == {"n": 58, "kept": 58}
    assert v2["fixed"] == {"n": 29, "landed": 0}
    assert v2["ungated_moved"] == []


def test_the_plan_carries_the_thresholds_the_run_will_be_read_against():
    committed = json.loads(PLAN.read_text(encoding="utf-8"))
    assert committed["gate"]["preserved"] == {"n": 58, "pass_at": 55, "kill_below": 52}
    assert committed["gate"]["fixed"] == {"n": 29, "pass_at": 24, "kill_below": 20}
    assert committed["gate"]["attempts"] == 1
    assert committed["in_sample"] is True
    # the reference labels come off a rebuild that reproduced the sealed hash, not off a file
    assert committed["source"]["rebuilt_sha256"] == committed["source"]["sealed_sha256"]
    assert committed["source"]["sealed_sha256"].startswith("c0d7656f")
