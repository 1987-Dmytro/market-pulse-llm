"""Offline tests for the market screen — no Telegram, no store writes.

One thing here can quietly destroy a result: a second pass overwriting the first. The pass-1
record is the evidence behind five theme exclusions and cannot be re-derived, because the
composition it measured no longer exists.
"""

import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

import measure_categories as cat  # noqa: E402
import theme_screen_5c1 as screen  # noqa: E402

from market_pulse.registry import Taxonomy, load_registry  # noqa: E402


def test_a_second_pass_refuses_to_overwrite_the_first():
    """The five exclusions of 2026-08-07 cite this file. A re-run over today's registry writes a
    table that cannot contain their rows — the channels left it — so the default path is closed."""
    assert screen.RECORD.exists(), "the pass-1 record is the thing being protected"
    with pytest.raises(SystemExit, match="already exists"):
        screen.main([])


def test_a_named_path_runs_the_screen_and_writes_there(tmp_path):
    """The escape hatch has to actually work, and the record it writes has to be a record: the
    guard is only acceptable because a later pass has somewhere to go."""
    out = tmp_path / "theme_screen_pass2.json"
    assert screen.main(["--out", str(out)]) == 0

    record = json.loads(out.read_text(encoding="utf-8"))
    assert record["channels"], "a screen with no channels measured nothing"
    registry = load_registry(REPO_ROOT / "config" / "registry.yaml")
    assert record["tracked_groups"] == sorted(registry.taxonomy.tracked_groups)
    assert json.loads(screen.RECORD.read_text(encoding="utf-8"))["channels"], "pass 1 untouched"


def test_the_tracked_groups_come_from_the_registry_and_not_from_a_literal():
    """uni-a's LEAK L2: `TRACKED = ("dairy", "ice-cream")` sat under a docstring calling it "the
    tracked groups of config/registry.yaml". The sentence was true and the code was not."""
    registry = load_registry(REPO_ROOT / "config" / "registry.yaml")
    compiled = cat.patterns(cat.build_lexicon(registry))
    assert screen.tracked_groups(registry, compiled) == ("dairy", "ice-cream")
    assert not hasattr(screen, "TRACKED"), "the literal is gone, not shadowed"


def test_a_taxonomy_the_lexicon_cannot_see_is_a_refusal_and_not_a_zero():
    """The loud half. Every channel would score `tracked_share: 0.0` and the table would read as
    "no source carries the category" when it means "nothing here can see the category at all" —
    the same silent zero uni-a found in three other places."""
    registry = load_registry(REPO_ROOT / "config" / "registry.yaml")
    compiled = cat.patterns(cat.build_lexicon(registry))
    coffee = replace(registry, taxonomy=Taxonomy({"coffee": {"name": "Кава", "subcategories": {}}}))
    with pytest.raises(SystemExit, match="no group is in both"):
        screen.tracked_groups(coffee, compiled)
