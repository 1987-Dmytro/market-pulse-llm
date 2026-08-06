"""Config B's builder: the preflight that has to refuse before an hour of GPU time.

The merge itself needs 62 GB of weights and the `gpu` extra, so what is tested is the
arithmetic that decides whether to start it at all — and it is tested at the boundary,
because "does it fit" is the whole question.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
spec = importlib.util.spec_from_file_location(
    "merge_requantize", REPO_ROOT / "scripts" / "merge_requantize.py"
)
merge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(merge)


#   62 GB of bf16 weights x 1.15 headroom = 71.3 GB
def test_the_ram_bar_is_the_weights_plus_headroom():
    assert merge.enough_ram(71.3) is True
    assert merge.enough_ram(71.2) is False
    assert merge.enough_ram(62.0) is False, "the weights alone are not enough — peft holds more"


def test_an_a6000_pods_typical_ram_does_not_fit_a_bf16_merge():
    """The realistic failure: the card is big enough and the host is not."""
    assert merge.enough_ram(50.0) is False


def test_an_unreadable_ram_reading_refuses_rather_than_passing():
    """0.0 GB is what `available_ram_gb` returns off Linux — it must not read as 'fits'."""
    assert merge.enough_ram(0.0) is False


def test_a_directory_without_an_adapter_config_is_not_an_adapter(tmp_path):
    with pytest.raises(SystemExit, match="not a peft adapter directory"):
        merge.main(
            [
                "--adapter",
                str(tmp_path),
                "--out",
                str(tmp_path / "out"),
                "--bf16-scratch",
                str(tmp_path / "scratch"),
                "--sidecar",
                str(tmp_path / "sidecar.json"),
                "--check-only",
            ]
        )


def test_the_shipped_arm_a_adapter_is_a_peft_directory():
    """The positive control for the check above, on the artifact 5b actually merges."""
    adapter = REPO_ROOT / "results" / "train" / "45h2-arm-a" / "adapter"
    assert (adapter / "adapter_config.json").exists()
