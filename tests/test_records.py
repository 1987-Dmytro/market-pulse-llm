"""The results file read as a gate reads it: one anchor, or a refusal.

Every number in these tests either comes out of the committed
`results/baselines.json` or is invented for a fixture. None is typed from the
record — amendment 3.5 (1) says the anchors are read programmatically, and a
test that pasted them would be the copy that drifts.
"""

import json
from hashlib import sha256
from pathlib import Path

import pytest
from market_pulse import prompts, records, scorer

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS = REPO_ROOT / "results" / "baselines.json"

HISTORY = json.loads(RESULTS.read_text(encoding="utf-8"))
ANCHOR = records.anchor(HISTORY)
SLICE_TEXT = (REPO_ROOT / ANCHOR["config"]["g1b_slice_path"]).read_text(encoding="utf-8")


def row(**config) -> dict:
    """A record with just enough shape for the anchor selector to judge it."""
    return {
        "model": config.pop("model", "m"),
        "timestamp": config.pop("timestamp", "2026-08-01T00:00:00+00:00"),
        "diagnostics": {"gate_anchor_valid": config.pop("valid", True)},
        "config": {
            "backend": "local",
            "train_sources": records.ANCHOR_TRAIN_SOURCES,
            **config,
        },
    }


def test_every_recorded_run_still_verifies_against_this_checkout_s_prompts():
    """Taxonomy v2 added two prompts; the records were measured under the two that
    were here before. This reads the real maps out of the real file — nothing is
    typed, and `prompt_sha256 == prompt_sha256` would prove nothing."""
    checked = {
        model: len(stored)
        for model in HISTORY
        if (stored := records.prompt_sha_history(HISTORY, model))
        and records.assert_prompt_sha(stored, model)
    }
    assert len(checked) >= 3 and sum(checked.values()) >= 6, checked


def test_a_sixth_prompt_joining_TASKS_would_break_every_one_of_them(monkeypatch):
    """The negative control for the test above: it passes because TASKS is frozen,
    not because the comparison is loose."""
    monkeypatch.setattr(prompts, "TASKS", (*prompts.TASKS, "T1v2"))
    model = next(model for model in HISTORY if records.prompt_sha_history(HISTORY, model))
    with pytest.raises(ValueError, match="prompt SHA256 differs"):
        records.assert_prompt_sha(records.prompt_sha_history(HISTORY, model), model)


def test_anchor_is_the_own_pod_zero_shot_row_of_the_real_results_file():
    assert ANCHOR["config"]["backend"] == "local"
    assert ANCHOR["config"]["train_sources"] == records.ANCHOR_TRAIN_SOURCES
    assert ANCHOR["config"]["quantization"]["bnb_4bit_quant_type"] == "nf4"


def test_anchor_refuses_two_candidates_rather_than_picking_one():
    """4c's fine-tuned runs are `backend: local` too — the realistic failure."""
    with pytest.raises(ValueError, match="exactly one record, found 2"):
        records.anchor({"m": [row(), row(timestamp="2026-08-02T00:00:00+00:00")]})


def test_anchor_ignores_a_local_row_that_trained_on_something():
    """The narrowing that training cannot fake: a zero-shot row trained on nothing."""
    tuned = row(train_sources={"data/frozen/comments_train.jsonl": 1446})
    assert records.anchor({"m": [row(), tuned]})["config"]["train_sources"] == (
        records.ANCHOR_TRAIN_SOURCES
    )


def test_anchor_ignores_a_row_whose_run_disowned_its_own_numbers():
    with pytest.raises(ValueError, match="found 0"):
        records.anchor({"m": [row(valid=False)]})


def test_anchor_values_carries_every_gated_head_and_no_g1b():
    values = records.anchor_values(ANCHOR)
    assert set(values) == {"G1a", "G1c", "G1d", "G1e"}
    assert {"overall", *scorer.GATED_LANGUAGES} <= set(values["G1a"])


def test_anchor_values_takes_the_gated_g1d_and_not_the_one_reported_beside_it():
    """The record holds two G1d rows: post_type, which gates, and relevance,
    which amendment 3.3 puts beside the gate and never inside it. A dict keyed by
    gate id hands out whichever came last — here the ungated, higher number."""
    relevance = [
        g for g in ANCHOR["gates"] if g["gate"] == "G1d" and g["metric"].startswith("relevance")
    ]
    assert len(relevance) == 1, "the fixture only means something while both rows exist"
    assert records.anchor_values(ANCHOR)["G1d"] != relevance[0]["value"]


def test_anchor_values_refuses_a_record_missing_a_gate():
    stripped = dict(ANCHOR, gates=[g for g in ANCHOR["gates"] if g["gate"] != "G1e"])
    with pytest.raises(ValueError, match="holds 0 rows for G1e"):
        records.anchor_values(stripped)


def test_slice_ids_reads_the_file_the_anchor_measured():
    ids = records.slice_ids(SLICE_TEXT, ANCHOR)
    assert len(ids) == len(set(ids)) == json.loads(SLICE_TEXT)["n"]


def test_slice_ids_refuses_a_tampered_file():
    """The negative control. Without it the check above proves only that a file exists.

    One id swapped for another real holdout id: the count, the shape and every
    other field survive, and only the hash notices.
    """
    tampered = SLICE_TEXT.replace(json.loads(SLICE_TEXT)["ids"][0], "@VARUS_channel:99999", 1)
    assert tampered != SLICE_TEXT
    with pytest.raises(ValueError, match="does not match the anchor record"):
        records.slice_ids(tampered, ANCHOR)


def test_slice_ids_refuses_a_file_whose_hash_was_recomputed_after_the_edit():
    """Regenerating the slice is the other way to lose the pre-registered one."""
    edited = json.loads(SLICE_TEXT)
    edited["ids"] = edited["ids"][:10]
    text = json.dumps(edited, ensure_ascii=False, indent=2) + "\n"
    forged = dict(ANCHOR, config=dict(ANCHOR["config"]))
    forged["config"]["g1b_slice_sha256"] = sha256(text.encode("utf-8")).hexdigest()
    assert records.slice_ids(text, forged) == edited["ids"]  # a self-consistent pair passes...
    with pytest.raises(ValueError, match="does not match"):
        records.slice_ids(text, ANCHOR)  # ...and the record that anchors the gate does not


def test_the_real_anchor_and_the_real_slice_produce_a_reachable_bar_for_every_gate():
    """The end-to-end shape of amendment 3.5, with nothing typed.

    Each bar is checked against its own anchor by direction, not by value: the
    two +5 pp gates must sit above it, the two no-regression gates below it, and
    G1b's count must be reachable within its own n.
    """
    values = records.anchor_values(ANCHOR)
    ids = records.slice_ids(SLICE_TEXT, ANCHOR)
    bars = scorer.gate_thresholds(values, len(ids))
    assert bars["G1a"]["min"] > values["G1a"]["overall"]
    assert bars["G1c"]["min"] > values["G1c"]
    assert bars["G1d"]["min"] < values["G1d"]
    assert bars["G1e"]["min"] < values["G1e"]
    assert 0 < bars["G1b"]["min_fixed"] <= len(ids)
    for language in scorer.GATED_LANGUAGES:
        assert bars["G1a"]["floors"][language] < values["G1a"][language]


# --- the adapter's hash, in one implementation --------------------------------


def adapter(root: Path, files: dict[str, bytes]) -> Path:
    for name, payload in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    return root


def test_artifact_sha256_is_the_content_and_not_the_walk_order(tmp_path):
    """The pod writes this number into a gate record and the Mac re-checks it
    after the sync. It has to hash the adapter, not the order a filesystem
    happened to hand the files over."""
    files = {"adapter_config.json": b"{}", "nested/adapter_model.safetensors": b"weights"}
    first = records.artifact_sha256(adapter(tmp_path / "a", files))
    second = records.artifact_sha256(adapter(tmp_path / "b", dict(reversed(files.items()))))
    assert first == second
    assert len(first) == 64


def test_artifact_sha256_notices_a_renamed_file_as_well_as_a_changed_one(tmp_path):
    """A hash over bytes alone would call two different adapters equal the day
    one of them ships its weights under a different name."""
    base = records.artifact_sha256(adapter(tmp_path / "a", {"w.safetensors": b"weights"}))
    renamed = records.artifact_sha256(adapter(tmp_path / "b", {"x.safetensors": b"weights"}))
    edited = records.artifact_sha256(adapter(tmp_path / "c", {"w.safetensors": b"weightz"}))
    assert base != renamed
    assert base != edited


# --- two anchors, one file (4.5h2) --------------------------------------------


def test_the_default_version_is_what_a_record_that_names_none_was_measured_on():
    """Every Phase 4 record predates the field, so the default has to reproduce
    today's answer exactly — not approximately, and not by re-deriving it."""
    assert records.anchor(HISTORY) is records.anchor(HISTORY, records.DEFAULT_TESTSET_VERSION)
    assert "testset_version" not in ANCHOR["config"]


def test_a_v4_anchor_does_not_collide_with_the_phase_4_one():
    """The realistic failure of 4.5h2: the fresh anchor is a zero-shot own-pod row with
    valid gate anchoring, exactly like 4a's. Without the version narrowing, appending it
    makes `gate_bars.py` and `gate_verdict.py` refuse — after the pod money is spent."""
    history = {"m": [row(), row(timestamp="2026-08-04T00:00:00+00:00", testset_version="v4")]}
    with pytest.raises(ValueError, match="found 2"):
        records.anchor({"m": [row(), row(timestamp="2026-08-04T00:00:00+00:00")]})
    assert records.anchor(history, "v2")["timestamp"] == "2026-08-01T00:00:00+00:00"
    assert records.anchor(history, "v4")["timestamp"] == "2026-08-04T00:00:00+00:00"


def test_a_version_nothing_has_scored_yet_is_a_refusal_that_names_it():
    with pytest.raises(ValueError, match="test set v4 must be exactly one record, found 0"):
        records.anchor(HISTORY, "v4")
