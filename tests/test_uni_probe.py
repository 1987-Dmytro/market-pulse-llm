"""The universality probe's two invariants: it writes beside uni-a's run, and it measures.

The probe itself is a one-shot instrument and is not re-tested here — what is guarded is the pair
of things a later session could break by accident: overwriting a dated measurement that cannot be
re-derived, and a record whose verdicts stopped being computed.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

import uni_probe as probe  # noqa: E402


def test_uni_a_s_record_cannot_be_written_over():
    """`results/uni_probe.json` measured the code BEFORE SPEC 3.17 (8): its step 2 read a draft
    lexicon that is no longer what the pre-filter loads, and its schema field was `fat`. Re-running
    today would not reproduce it, so the default `--out` refuses it by name."""
    assert probe.SEALED.exists()
    with pytest.raises(SystemExit, match="never over it"):
        probe.main(["--out", str(probe.SEALED)])
    assert probe.RECORD.name == "uni_probe_v2.json"


def test_the_shipped_v2_record_carries_the_verdicts_uni_b_was_run_for():
    """The regression the brief asks for, read off the artifact rather than re-run: step 2 moved
    from hard-coded to follows-registry(law), and the other four did not move at all."""
    record = json.loads(probe.RECORD.read_text(encoding="utf-8"))
    verdicts = {name.split(" · ")[0]: verdict for name, verdict in record["verdicts"].items()}
    assert verdicts == {
        "1": probe.FOLLOWS,
        "2": probe.FOLLOWS_LAW,
        "3": probe.FOLLOWS,
        "4": probe.FOLLOWS,
        "5": probe.NEEDS_REGISTRATION,
    }
    uni_a = json.loads(probe.SEALED.read_text(encoding="utf-8"))
    was = {name.split(" · ")[0]: verdict for name, verdict in uni_a["verdicts"].items()}
    assert was["2"] == probe.HARD_CODED, "uni-a's reading is what this run was meant to move"
    assert {k: v for k, v in was.items() if k != "2"} == {
        k: v for k, v in verdicts.items() if k != "2"
    }

    step2 = record["steps"]["2 · the deterministic pre-filter over the corpus"]
    assert step2["the_law_refuses_a_taxonomy_its_stems_do_not_name"]["refused"] is True
    assert step2["controls_ok"] is True
    assert record["supersedes"]["record"] == "results/uni_probe.json"
