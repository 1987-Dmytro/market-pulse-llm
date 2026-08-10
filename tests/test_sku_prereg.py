"""The pre-registration: are the bars the law's own words, and does every ratio have a denominator?

sku-b is ONE paid attempt and a failed bar closes B by measurement, so the things that can go wrong
here are expensive and quiet: a bar paraphrased away from SPEC, a denominator that can come back
empty, an executor's reading passing as the contract's.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

import write_sku_prereg as prereg  # noqa: E402

from market_pulse import positions, prompts  # noqa: E402


@pytest.fixture(scope="module")
def record():
    return json.loads(prereg.RECORD.read_text(encoding="utf-8"))


def test_every_bar_is_quoted_out_of_the_spec_as_written(record):
    """A bar retyped is a bar that can drift from the law it claims to be. Checked whitespace-
    insensitively against docs/SPEC.md, which is where the amendment lives wrapped."""
    law = prereg.verbatim(prereg.SPEC)
    for name, bar in record["bars"].items():
        assert bar["verbatim"] in law, name
        assert bar["verbatim"] == prereg.BARS[name]
    assert record["attempts"]["verbatim"] in law
    assert record["attempts"]["on_success"] in law


def test_a_paraphrased_bar_stops_the_write(monkeypatch, tmp_path):
    """The negative control: the check is only worth having if it fires on a reworded bar."""
    monkeypatch.setitem(prereg.BARS, "text_tier_accuracy", "text tier accuracy at least 0.85")
    with pytest.raises(SystemExit, match="not in docs/SPEC.md as written"):
        prereg.main(["--out", str(tmp_path / "p.json")])


def test_the_three_thresholds_and_their_direction(record):
    assert {name: bar["threshold"] for name, bar in record["bars"].items()} == {
        "leaflet_brand_recall": 0.75,
        "price_pair_accuracy": 0.80,
        "text_tier_accuracy": 0.85,
    }
    for bar in record["bars"].values():
        assert bar["direction"] == ">="
        # a threshold on a ratio has to be reachable at all: none of these exceeds 1.0
        assert 0 < bar["threshold"] <= 1.0


def test_one_attempt_and_a_failure_closes_b(record):
    assert record["attempts"]["count"] == 1
    assert record["attempts"]["cap_usd"] == 0.35
    assert "BY MEASUREMENT" in record["attempts"]["on_failure"]
    assert "No retry" in record["attempts"]["on_failure"]


def test_every_bar_names_a_denominator_and_what_it_excludes(record):
    """The failure this exists to prevent: an absolute ratio whose denominator can be empty fails by
    arithmetic and reads as a measurement."""
    for name, bar in record["bars"].items():
        assert bar["denominator"], name
    leaflet = record["bars"]["leaflet_brand_recall"]
    assert len(leaflet["excluded"]["posts"]) == 4
    assert "undefined" in leaflet["excluded"]["why"]
    assert "PRECISION probe" in leaflet["excluded"]["instead"]
    assert "15 of 19" in leaflet["reachable"]
    price = record["bars"]["price_pair_accuracy"]
    assert "NOT_REACHABLE" in price["reachability"]["rule"]
    assert "NOT_SCORED" in price["reachability"]["rule"]
    text = record["bars"]["text_tier_accuracy"]
    assert "NOT_SCORED" in text["reachability"]["rule"]
    assert "NOT_SCORED" in text["unreadable_rows"]


def test_the_unreadable_reply_is_not_scored_as_an_empty_answer(record):
    """An unreadable reply and «nothing on this row» are different outcomes, and the empty class is
    where parse failures pile up if nobody separates them."""
    text = record["bars"]["text_tier_accuracy"]
    assert "NOT scored as `none`" in text["unreadable_rows"]
    assert "excluded from the denominator" in text["unreadable_rows"]
    assert "10%" in text["unreadable_rows"]


def test_the_per_page_reading_is_declared_the_executors_and_needs_a_word(record):
    """The most expensive thing in the file. The bar says «per page», the gold is per POST, and the
    session that would discover that is the one paid attempt."""
    leaflet = record["bars"]["leaflet_brand_recall"]
    assert "per page" in leaflet["verbatim"]
    assert "THE EXECUTOR'S READING" in leaflet["why_not_per_page"]
    assert "MACRO MEAN" in leaflet["denominator"]
    ids = {item["id"] for item in record["ratification_required"]}
    assert ids == {"R1", "R2", "R3", "R4", "R5"}
    r1 = next(item for item in record["ratification_required"] if item["id"] == "R1")
    assert "must NOT run until this line is ratified" in r1["if_refused"]
    for item in record["ratification_required"]:
        assert item["bar"] in record["bars"]
        assert item["question"] and item["if_refused"]


def test_the_page_set_is_the_pages_the_reviewer_saw(record):
    leaflet = record["bars"]["leaflet_brand_recall"]
    assert "108 pages" in leaflet["extraction_unit"]
    assert "not the 159 available" in leaflet["extraction_unit"]
    reference = json.loads((REPO_ROOT / leaflet["gold"]["path"]).read_text(encoding="utf-8"))
    assert reference["population"]["pages_sent"] == 108
    assert reference["population"]["pages_available"] == 159
    assert leaflet["gold"]["pairs"] == reference["gold"]["pairs"] == 55


def test_the_price_bar_names_the_dump_the_team_lead_reads(record):
    """SPEC's own wording puts a human between the run and the number, and the procedure has to say
    what that human opens. The executor never scores its own sample (SPEC §10)."""
    price = record["bars"]["price_pair_accuracy"]
    assert "team-lead read of the per-position dump against the images" in price["verbatim"]
    for field in ("page", "sha256", "price_promo", "price_old", "discount_pct_printed", "depth"):
        assert field in price["procedure"], field
    assert "never scores its own sample" in price["procedure"]
    assert "a right promo beside a wrong old price is a wrong pair" in price["numerator"]


def test_the_ladder_is_pinned_as_an_input_and_not_only_as_a_hash(record):
    """Bar 3's gold is computed from the operator's ticks by this ladder, so a ladder that moved
    between the pack build and the pilot would move the gold. Pinned as its whole table, so a future
    reader does not have to run this code to see what was registered."""
    assert record["ladder"]["sha256"] == positions.ladder_sha256()
    assert record["ladder"]["table"] == positions.ladder_table()
    assert len(record["ladder"]["table"]) == 32
    pack = json.loads((REPO_ROOT / "results" / "sku_text_pack_manifest.json").read_text("utf-8"))
    assert pack["ladder"]["sha256"] == record["ladder"]["sha256"]
    assert record["bars"]["text_tier_accuracy"]["gold"]["ladder_sha256"] == pack["ladder"]["sha256"]


def test_both_instruments_are_pinned_by_sha(record):
    assert record["instruments"]["positions_post_gm4"] == prompts.prompt_sha256(
        "positions_post_gm4"
    )
    assert record["instruments"]["positions_text_gm4"] == prompts.prompt_sha256(
        "positions_text_gm4"
    )
    assert set(prompts.POSITIONS) == {"positions_post_gm4", "positions_text_gm4"}


def test_every_pinned_input_still_hashes_to_what_it_says(record):
    for path, sha in record["pinned_inputs"].items():
        assert hashlib.sha256((REPO_ROOT / path).read_bytes()).hexdigest() == sha, path
    assert set(record["pinned_inputs"]) == {
        "docs/SPEC.md",
        "results/sku_reference_leaflet.json",
        "results/sku_text_pack_manifest.json",
        "results/sku_prefilter_census.json",
        "config/registry.yaml",
    }


def test_the_prereg_says_what_it_does_not_touch(record):
    """The 5c3 rulings are the loudest omission: «Варто» and «Селянське» are a named revision and
    applying them here would change what the leaflet gold means mid-contract."""
    out = record["not_in_scope"]
    assert "«Варто» text-matching OFF" in out["the 5c3 rulings"]
    assert "NOT applied" in out["the 5c3 rulings"]
    assert "symmetric" in out["the 141 names"]
    assert "baselines.json" in out["the frozen family"]
    assert "consumer quotes never enter" in out["aggregates"]


def test_the_prereg_was_committed_before_any_pilot_artifact(record):
    """A pre-registration written after the thing it judges is a rationalisation, and git history is
    the only witness to the ordering — so the claim is checked against history rather than against
    today's directory listing, which stops being evidence the moment sku-b writes its records.

    The same discipline `run_v22_probe.py` uses: shell out to git, and treat "not tracked" as a
    failure rather than a skip. An uncommitted pre-registration is not one.
    """
    assert "before any sku-b artifact exists" in record["class"]
    added = subprocess.run(
        ["git", "log", "--diff-filter=A", "--format=%H", "--", "results/sku_pilot_prereg.json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    assert len(added) == 1, "the pre-registration is added exactly once, or its ordering is unclear"
    tree = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", added[0], "results/"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    assert "results/sku_pilot_prereg.json" in tree
    # at the commit that added it, no other sku_pilot_* result existed. That is permanent.
    others = [
        name
        for name in tree
        if name.startswith("results/sku_pilot_") and name != "results/sku_pilot_prereg.json"
    ]
    assert others == [], others


def test_nothing_here_carries_a_bar_result(record):
    """The other half, and it holds after sku-b runs too: a pre-registration states thresholds and
    procedures, and a `measured` field in it would make the file its own scorer."""
    for name, bar in record["bars"].items():
        assert not {"measured", "value", "verdict", "result"} & set(bar), name
    assert "verdict" not in record
    for path in (REPO_ROOT / "results").glob("sku_*.json"):
        if path.name.startswith("sku_pilot_") and path.name != "sku_pilot_prereg.json":
            continue  # sku-b's own records are allowed to carry verdicts; sku-a's are not
        body = json.loads(path.read_text(encoding="utf-8"))
        assert "verdict" not in body, path.name


def test_the_record_rebuilds_identically_apart_from_its_timestamp(tmp_path):
    out = tmp_path / "prereg.json"
    assert prereg.main(["--out", str(out)]) == 0
    a, b = (json.loads(path.read_text(encoding="utf-8")) for path in (out, prereg.RECORD))
    for body in (a, b):
        body.pop("generated_at"), body.pop("git")
    assert a == b
