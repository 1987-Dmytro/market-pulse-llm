"""gate_bars as a persisted artifact: a bar that only existed in a terminal is not
pre-registered (4.5h2)."""

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "gate_bars.py"
spec = importlib.util.spec_from_file_location("gate_bars", SCRIPT)
bars = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bars)


def test_the_bars_record_carries_the_anchor_it_was_derived_from(tmp_path):
    out = tmp_path / "bars.json"
    assert bars.main(["--out", str(out)]) == 0
    record = json.loads(out.read_text(encoding="utf-8"))
    assert record["testset_version"] == "v2"
    assert set(record["bars"]) == {"G1a", "G1b", "G1c", "G1d", "G1e"}
    assert record["anchor"]["g1b_slice_sha256"] and record["anchor"]["commit"]
    # every bar sits on the right side of its own anchor, by direction not by value
    assert record["bars"]["G1a"]["min"] > record["anchor_values"]["G1a"]["overall"]
    assert record["bars"]["G1c"]["min"] > record["anchor_values"]["G1c"]
    assert record["bars"]["G1d"]["min"] < record["anchor_values"]["G1d"]


def test_a_version_with_no_anchor_refuses_instead_of_falling_back():
    with pytest.raises(SystemExit, match="test set v4 must be exactly one record, found 0"):
        bars.main(["--version", "v4"])
