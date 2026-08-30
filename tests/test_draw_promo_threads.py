"""The C3 step-0 draw: the population the ruling names, the queue rule it applies, and a seed that
is not the same seed in both strata.

K7 is «run it twice, identical sha», so determinism is asserted on BYTES here and not on a parsed
record — a record that sorted differently between runs would still compare equal as a dict.
"""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))


def _module(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


draw = _module("draw_promo_threads")

STRATA = ("currency", "decimal_only")


@pytest.fixture(scope="module")
def record(tmp_path_factory) -> dict:
    out = tmp_path_factory.mktemp("draw") / "promo_threads_draw.json"
    assert draw.main(["--out", str(out)]) == 0
    return json.loads(out.read_text(encoding="utf-8"))


def test_two_runs_are_byte_identical(tmp_path):
    """K7. The record carries no clock and no git block, so the only way the bytes can move is a
    draw that moved — which is what the team lead re-runs this for."""
    first, second = tmp_path / "one.json", tmp_path / "two.json"
    for out in (first, second):
        assert draw.main(["--out", str(out)]) == 0
    assert first.read_bytes() == second.read_bytes()
    assert b'"at"' not in first.read_bytes(), "no clock in the body"
    assert hashlib.sha256(first.read_bytes()).hexdigest()


def test_the_population_is_the_one_the_ruling_names(record):
    """«Все 678» — and the two strata partition it, measured rather than asserted: a split that
    lost or double-counted a thread would still print two plausible numbers."""
    population = record["population"]
    assert population["threads"] == 678
    assert population["by_stratum"] == {"currency": 229, "decimal_only": 449}
    assert sum(population["by_stratum"].values()) == population["threads"]
    assert population["ids_sha256"]


def test_the_queue_rule_is_applied_and_its_count_is_printed(record):
    """SPEC 3.19 is a QUEUE rule: the wordless comments are counted, not deleted, and a thread with
    nothing but wordless comments is not drawn because there is nothing in it to annotate. Both
    numbers are in the record — «the volume of wordless reactions is itself a signal»."""
    queue = record["queue_rule"]
    assert queue["wordless_comments"] > 0
    assert queue["comments"] == 4718
    assert queue["eligible_threads"] + queue["threads_with_nothing_but_wordless_comments"] == 678
    assert queue["eligible_threads"] == sum(block["eligible"] for block in record["draw"].values())
    for block in record["draw"].values():
        for row in block["dev"] + block["holdout"]:
            assert row["n_comments"] > row["n_wordless"], row


def test_dev_and_holdout_are_twenty_each_per_stratum_and_disjoint(record):
    """«дро 20/20 по типу», and the disjointness the holdout's one shot depends on."""
    seen = []
    for stratum in STRATA:
        block = record["draw"][stratum]
        assert len(block["dev"]) == len(block["holdout"]) == 20
        for arm in ("dev", "holdout"):
            for row in block[arm]:
                assert row["stratum"] == stratum
                seen.append((row["store_file"], row["thread_root"]))
    assert len(seen) == 80
    assert len(set(seen)) == 80, "dev-40 and holdout-40 are disjoint across both strata"


def test_the_two_strata_are_not_drawn_on_the_same_ranks(record):
    """`.claude/rules/registrations-and-draws.md`: measure the RANKS, never the ids.

    Five strata under one `Random(42)` once put three draws on rank 163 of their pools — reproducible
    and correlated. The seed carries the stratum here, so the two rank vectors must differ, and each
    must be spread across its pool rather than sitting in one corner of it.
    """
    vectors = {stratum: record["draw"][stratum]["dev_ranks"] for stratum in STRATA}
    assert vectors["currency"] != vectors["decimal_only"]
    for stratum, ranks in vectors.items():
        pool = record["draw"][stratum]["eligible"]
        assert len(set(ranks)) == 20, stratum
        assert min(ranks) < pool // 4, stratum
        assert max(ranks) > 3 * pool // 4, stratum


def test_a_quota_that_cannot_be_filled_is_a_refusal(record):
    """The negative control. A short draw reads like a complete one, so the script refuses instead —
    and the refusal names the stratum and both numbers."""
    with pytest.raises(SystemExit, match="a quota that cannot be filled is a refusal"):
        draw.draw([{"store_file": "x", "thread_root": "1"}], "currency")


def test_the_record_names_its_instrument_and_what_it_could_not_reach(record):
    """A draw whose predicate is not written down cannot be shown to measure what the census did."""
    assert record["predicate"]["name"] == "retail_census.PRICE_BRANCHES"
    assert record["predicate"]["branches"]["decimal"] == r"\d+[,.]\d\d"
    assert record["seed"] == 42
    assert "42:<stratum>" in record["seeded_per_stratum"]
    assert record["quotas"] == {"dev": 20, "holdout": 20}
    assert record["could_not_reach"]
    # channel is a recorded field on every drawn thread, and never a stratum
    channels = {row["channel"] for block in record["draw"].values() for row in block["dev"]}
    assert channels <= set(record["population"]["by_channel"])
