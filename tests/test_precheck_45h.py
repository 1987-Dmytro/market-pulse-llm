"""What the 4.5h precheck is allowed to claim.

The record is read by a team lead deciding whether to amend SPEC, so the two
numbers that decide it are pinned against the runs that already happened: the
step formula has to reproduce 4c's recorded step counts on 4c's recorded row
counts, and arm A has to come out at the row count arm A actually trained on.
A projection that cannot re-derive the past is not a projection.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import precheck_45h as pre  # noqa: E402

CONFIG = {"epochs": 2, "micro_batch_size": 2, "grad_accum": 8, "carve_rows": 24}


def test_scoreable_drops_exactly_the_unclear_rows():
    rows = [
        {"unclear": False, "id": "a"},
        {"unclear": True, "id": "b"},
        {"unclear": False, "id": "c"},
    ]
    assert [row["id"] for row in pre.scoreable(rows)] == ["a", "c"]


@pytest.mark.parametrize("rows,steps", [(2171, 270), (2771, 346)])
def test_the_step_formula_reproduces_what_4c_ran(rows, steps):
    """floor, not ceil: the trailing micro-batches of an epoch never complete a step,
    which is why 4c planned 272 and ran 270. A ceil here would overstate arm B's hours
    by two steps and understate nothing — but it would be a different run."""
    assert pre.steps_for(rows, CONFIG) == steps


def test_the_recorded_runs_still_say_what_the_projection_reads():
    for arm, steps, rows in (("4c-arm-a", 270, 2171), ("4c-arm-b", 346, 2771)):
        record = json.loads((pre.RESULTS / "train" / arm / "provenance.json").read_text())
        assert record["run"]["steps"] == steps
        assert record["n_train"] == rows


def test_arm_a_comes_out_at_the_row_count_arm_a_trained_on():
    arms = pre.arms()
    assert arms["arm_a_train_rows"] == arms["arm_a_4c_recorded_n_train"]
    assert arms["arm_a_matches_4c"]


def test_the_plast_is_additive_and_the_record_says_so():
    """B = A + пласт only if the ids are disjoint. If a пласт id ever lands in a
    training source, arm B is a relabel and not an addition, and every hour in the
    projection is wrong."""
    arms = pre.arms()
    assert arms["plast_ids_already_in_training"] == 0
    assert arms["additive"]
    assert arms["arm_b_scoreable_pool"] == arms["arm_a_scoreable_pool"] + arms["plast_scoreable"]


def test_the_54_have_no_training_side_home():
    assert sum(pre.dual_home()["training_side_hits"].values()) == 0


def test_the_plast_shares_no_thread_with_a_frozen_set():
    """The standing invariant of docs/frozen-testsets.md, re-checked against rows that
    did not exist when it was last checked."""
    leak = pre.leakage()
    assert set(leak["thread_overlap"].values()) == {0}
    assert set(leak["id_overlap"].values()) == {0}
    assert set(leak["verbatim_text_overlap"].values()) == {0}


def test_no_gold_row_carries_a_v2_intents_value():
    migration = pre.migration()
    assert migration["rows_carrying_a_v2_intents_value_today"] == 0
    assert migration["rows_needing_a_fresh_pass"] == migration["gold_rows"] == 508


def test_the_intents_guards_are_where_the_report_says():
    """Three of the four inventoried places still exist and are still where the record
    says. The fourth is gone by design — see below."""
    record = json.loads((REPO_ROOT / "results" / "precheck_45h.json").read_text(encoding="utf-8"))
    guards = {guard["name"]: guard for guard in record["guards"]}
    assert set(guards) == {"LAW_PENDING", "NEVER / forbidden_ids", "NEVER_READ", "SOURCES"}
    markers = {
        "LAW_PENDING": 'LAW_PENDING = ("intents",)',
        "NEVER / forbidden_ids": "NEVER = (",
        "NEVER_READ": "NEVER_READ = (",
    }
    for name, marker in markers.items():
        path = REPO_ROOT / guards[name]["file"]
        assert pre.line_of(path, marker) > 0, name


def test_a_vanished_guard_marker_stops_the_run(tmp_path):
    """The failure mode a hand-typed line number has: the report keeps printing a
    number that no longer points at a guard."""
    path = tmp_path / "guard.py"
    path.write_text("NOTHING = ()\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="marker"):
        pre.line_of(path, "NEVER = (")


def test_the_eval_rate_is_read_from_the_ledger_note_not_typed():
    observed = pre.eval_budget()["observed_4a"]
    assert (observed["rows"], observed["batch_size"], observed["minutes"]) == (758, 1, 39)
    assert observed["seconds_per_row"] == pytest.approx(39 * 60 / 758)


def test_the_record_can_no_longer_be_re_derived_and_that_is_the_finding_landing():
    """It WAS byte-reproducible, twice, on 2026-08-03 — and it stopped being so the
    moment 4.5h2 executed the amendment it argued for.

    `guards()` reads `train_qlora.SOURCES` by a marker naming the v1 files, and amendment
    3.9 (1) moved that constant to the `_tax2` siblings. The refusal is the mechanism
    working: a report whose marker vanished stops instead of printing a stale line number.
    The record itself is frozen evidence the amendment cites and is never regenerated."""
    with pytest.raises(SystemExit, match="the guard marker .* is gone"):
        pre.guards()


def test_the_two_arms_would_not_be_trained_on_the_same_taxonomy():
    """The confound the precheck exists to catch: `train_qlora.SOURCES` reads the v1
    files, which hold no `service` row at all, while the пласт holds hundreds — and G1c
    is scored against a v4 test that is taxonomy v2. Arm B would win the selection rule
    by exposure and the phase would read it as volume."""
    exposure = pre.arms()["taxonomy_exposure"]
    assert set(exposure["service_rows_in_arm_a_sources"].values()) == {0}
    assert exposure["service_rows_in_the_plast"] > 0
    assert all(exposure["rows_match_between_v1_and_tax2"].values())


def test_the_source_list_finding_was_acted_on():
    """The one inventoried place that is not a guard — nothing refused when it was wrong —
    is the one the phase changed. Both halves are checked: the record still says what was
    true when it was written, and the code no longer is."""
    record = json.loads((REPO_ROOT / "results" / "precheck_45h.json").read_text(encoding="utf-8"))
    finding = next(g for g in record["guards"] if g["name"] == "SOURCES")
    assert "training reads the v1 files" in finding["holds"]
    trainer = importlib.util.module_from_spec(
        importlib.util.spec_from_file_location("t", REPO_ROOT / "scripts" / "train_qlora.py")
    )
    importlib.util.spec_from_file_location(
        "t", REPO_ROOT / "scripts" / "train_qlora.py"
    ).loader.exec_module(trainer)
    assert [path.name for path in trainer.SOURCES["T1"]] == [
        "comments_train_tax2.jsonl",
        "sarcasm_candidates_tax2.jsonl",
    ]
