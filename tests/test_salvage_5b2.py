"""The salvage's one job: say what survived without letting it read as the measurement.

The heads are computed here from the repository's own frozen inputs and the committed
checkpoint, so this suite re-derives the numbers the report quotes rather than pinning
copies of them — the check that a hand-edit of the record would fail.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
spec = importlib.util.spec_from_file_location(
    "salvage_5b2", REPO_ROOT / "scripts" / "salvage_5b2.py"
)
salvage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(salvage)


def checkpoint(tmp_path: Path, rows, header=None) -> Path:
    path = tmp_path / "ckpt.jsonl"
    lines = [json.dumps({"header": header or {"batch_size": 16}})]
    lines += [json.dumps({"input": name, "outcome": outcome}) for name, outcome in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_a_failed_row_carries_no_labels_and_is_not_counted_as_one(tmp_path):
    path = checkpoint(
        tmp_path,
        [
            ("comments_test", {"id": "@ch:1", "labels": {"sentiment": "neutral"}}),
            ("comments_test", {"id": "@ch:2", "failure": "parse", "reason": "no JSON"}),
        ],
    )
    header, labels = salvage.scored(path)
    assert header["batch_size"] == 16
    assert list(labels) == [("comments_test", "@ch:1")]


def test_a_checkpoint_with_no_header_cannot_say_what_produced_it(tmp_path):
    path = tmp_path / "bare.jsonl"
    path.write_text(json.dumps({"input": "comments_test", "outcome": {"id": "@ch:1"}}), "utf-8")
    with pytest.raises(SystemExit, match="no header"):
        salvage.scored(path)


def test_a_row_scored_twice_is_refused(tmp_path):
    row = ("comments_test", {"id": "@ch:1", "labels": {"sentiment": "neutral"}})
    with pytest.raises(SystemExit, match="twice"):
        salvage.scored(checkpoint(tmp_path, [row, row]))


def test_a_partial_input_yields_no_head_at_all():
    """The failure this exists to prevent: a head computed over the rows that happened to
    finish is a different measurement wearing the same name."""
    runner = salvage.script("eval_zero_shot")
    with pytest.raises(SystemExit, match="were never scored"):
        salvage.paired(runner, "sarcasm_holdout", "sarcasm_holdout_v4.jsonl", {})


def test_the_committed_checkpoint_is_the_run_the_verdict_describes():
    """Provenance: the record names batch 16 and the arm-A adapter, and so does the file."""
    header, labels = salvage.scored(salvage.CHECKPOINT)
    verdict = json.loads(salvage.VERDICT.read_text(encoding="utf-8"))
    assert header["batch_size"] == 16 == verdict["attempt"]["batch_size"]
    assert header["adapter_sha256"] == verdict["attempt"]["adapter_sha256"]
    assert header["adapter_sha256"].startswith("b3ca6308")
    assert len(labels) == sum(verdict["attempt"]["rows_scored"].values()) == 666


def test_the_verdict_says_the_measurement_failed_before_it_says_anything_else():
    """A table of heads under a familiar name reads as a result. The outcome, the adopted
    batch and the reason the rule could not run all sit above the salvage, and G1b is
    reported as missing rather than left out."""
    verdict = json.loads(salvage.VERDICT.read_text(encoding="utf-8"))
    assert verdict["outcome"] == "failed-measurement-oom"
    assert verdict["adopted_batch_size"] == 1
    assert "G1b" in verdict["rule_could_not_run"]
    assert "not computable" in verdict["salvage"]["g1b"]
    assert "G1b" not in verdict["salvage"]["heads"]["batch_16"]
    assert list(verdict["salvage"]["complete_inputs"]) == ["comments_test", "posts_test"]
    assert verdict["attempt"]["record_written"] is False


def test_the_salvaged_heads_rederive_from_the_committed_checkpoint():
    """Every number the report quotes, recomputed through the scorer from files in the repo."""
    runner = salvage.script("eval_zero_shot")
    _, labels = salvage.scored(salvage.CHECKPOINT)
    resolved = {name: filename for name, _, filename in runner.inputs_for("v4")}
    inputs = {
        name: salvage.paired(runner, name, resolved[name], labels) for name in salvage.COMPLETE
    }
    aliases = runner.watchlist_aliases(
        runner.load_registry(REPO_ROOT / "config" / "registry.yaml").watchlist
    )
    recomputed = salvage.heads(runner, inputs, aliases)
    recorded = json.loads(salvage.VERDICT.read_text(encoding="utf-8"))["salvage"]["heads"]
    assert recomputed["G1c"] == pytest.approx(recorded["batch_16"]["G1c"])
    assert recomputed["G1a"]["overall"] == pytest.approx(recorded["batch_16"]["G1a"]["overall"])
    # posts_test agreed row for row, so these two are the batch-1 numbers by construction
    assert recomputed["G1d"] == pytest.approx(recorded["batch_1"]["G1d"])
    assert recomputed["G1e"] == pytest.approx(recorded["batch_1"]["G1e"])


def test_the_six_rows_that_moved_are_named_not_counted():
    """A rate hides which rows; the ids are what a later phase would re-examine."""
    verdict = json.loads(salvage.VERDICT.read_text(encoding="utf-8"))
    rows = verdict["salvage"]["row_agreement_vs_batch_1"]
    assert rows["agree"] == 660
    assert rows["compared"] == 666
    assert len(rows["disagreeing"]) == 6
    assert rows["per_input"]["posts_test"]["rate"] == 1.0
    assert all({"input", "id", "batch_1", "batch_16"} <= set(row) for row in rows["disagreeing"])


def test_what_5c_reads_says_batch_one_and_names_the_failed_measurement():
    served = json.loads((REPO_ROOT / "results" / "serving_5b.json").read_text(encoding="utf-8"))
    assert served["adopted"]["batch_size"] == 1
    assert served["adopted"]["adopted"] is False
    assert served["adopted"]["measured_at_batch_size"] == 16
    assert "FAILED" in served["adopted"]["source"]
    assert served["cost"]["usd"] == 0.0226, "the 5b.1 smoke's own record survives beside it"
    assert len(served["rows"]) == 24
