"""The export: it equals the anchor where they meet, it is deterministic, and it names its samples.

The committed `results/dashboard_data_w1.json` is read here, and it is the file the dashboard will
be built on. Every check that could be made against a freshly built record is made against the
COMMITTED bytes too, because what ships is what a screen renders.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_aggregates as builder  # noqa: E402
import export_dashboard_data as exporter  # noqa: E402
from test_prompts import (  # noqa: E402
    MOVED_BY_R2,
    MOVED_BY_THE_PROMO_TABLES,
    MOVED_BY_THE_SECOND_WINDOW,
    SEALED_AT_R2,
    assert_pinned,
    put_the_sealed_shas_back,
    sealed_sha256,
)

from market_pulse import aggregates  # noqa: E402
from market_pulse.registry import load_registry, registry_before_r2  # noqa: E402

RECORD = json.loads(exporter.OUT.read_text(encoding="utf-8"))
ANCHOR = json.loads(builder.ANCHOR.read_text(encoding="utf-8"))

REGISTRY = REPO_ROOT / "config" / "registry.yaml"


def r1_registry_sha() -> str:
    """`config/registry.yaml` as revision r1 — the bytes this export was built over.

    Revision r2 (2026-08-30) appended eight A1 sources and took 39 rows out of collection. This
    record is window 1's, computed under r1, and `build_aggregates` reads the registry THROUGH the
    5c2 seal, so its NUMBERS are still r1's — the one thing that moves in a rebuild is the live sha
    the provenance block stamps. Recomputed from the file by the undo the sealed pins are reached
    through, and checked against `git show 58ff037:` — two independent routes to one sha, so a
    broken undo cannot agree with itself."""
    recomputed = hashlib.sha256(registry_before_r2(REGISTRY)).hexdigest()
    assert recomputed == sealed_sha256("config/registry.yaml", SEALED_AT_R2)
    return recomputed


@pytest.fixture(scope="module")
def rebuilt(tmp_path_factory) -> dict:
    """The export, produced again into `tmp_path` — never over the committed file."""
    out = tmp_path_factory.mktemp("export")
    assert exporter.main(["--out", str(out / "again.json"), "--db", str(out / "pulse.db")]) == 0
    return json.loads((out / "again.json").read_text(encoding="utf-8"))


def test_every_shared_figure_equals_the_anchor():
    """The gate: each declared pair resolved from BOTH files, here, in this test.

    The record carries its own verdict, but a record that asserts its own correctness proves
    nothing — so the anchor is re-read and every pair is re-resolved. `shared_figures` and
    :data:`export_dashboard_data.SHARED` are checked to be the same set as well: a producer that
    quietly stopped declaring a pair would otherwise pass with a shorter list.
    """
    declared = RECORD["convergence"]["shared_figures"]

    assert set(declared) == {here for here, _ in exporter.SHARED}
    assert len(declared) == len(exporter.SHARED) > 25
    for here, there in exporter.SHARED:
        assert declared[here]["anchor_field"] == there
        assert exporter.dig(RECORD, here) == exporter.dig(ANCHOR, there), here

    # the four the contract names, spelled out so a reader can see them without the loop
    assert exporter.dig(RECORD, "metrics.nsr.by_sample.bought.neutral") == 4144
    assert exporter.dig(RECORD, "metrics.aspect_share.by_sample.bought.labels.price") == 553
    assert RECORD["window"]["populations"]["bought"] == 5075
    assert RECORD["window"]["populations"]["payable"] == 3714
    assert RECORD["window"]["populations"]["text_less"] == 1361
    assert exporter.dig(RECORD, "metrics.promo_depth.readings.from_price_pair.median") == 0.4206


def test_a_shared_figure_that_moved_stops_the_export():
    """The negative control for the pair check — planted on a copy of the anchor."""
    forged = json.loads(json.dumps(ANCHOR))
    forged["comment"]["total"]["sentiment"]["neutral"] += 1

    with pytest.raises(SystemExit, match="disagrees with the convergence anchor on 1 shared"):
        exporter.check_shared(RECORD, forged)


def test_the_whole_anchor_re_derives_and_the_record_says_by_how_much(rebuilt):
    """The exhaustive half, re-run: every numeric leaf of the anchor's five blocks out of SQL."""
    verdict = RECORD["convergence"]["whole_record"]

    assert verdict["disagreed"] == {} and verdict["missing"] == [] and verdict["extra"] == []
    assert verdict["agreed"] == verdict["leaves"]
    assert verdict["leaves"] == len(
        aggregates.numeric_leaves({name: ANCHOR[name] for name in verdict["blocks"]})
    )
    assert rebuilt["convergence"]["whole_record"] == verdict


def test_two_exports_are_byte_identical_and_the_committed_one_is_that_record(tmp_path):
    """Determinism, and the committed file IS what the producer writes today.

    Sorted keys, no clock, no git block — so the pair is byte-identical and the shipped record can
    be regenerated by anyone. The second half is what makes the first half load-bearing: a
    deterministic producer whose output nobody compared to the committed bytes would drift.
    """
    first, second = tmp_path / "one.json", tmp_path / "two.json"
    for out in (first, second):
        assert exporter.main(["--out", str(out), "--db", str(tmp_path / "pulse.db")]) == 0

    assert first.read_bytes() == second.read_bytes()
    # `provenance.producers` is hashed LIVE and `src/market_pulse/prompts.py` moved when the v5
    # reader text was registered. The shipped export is the file a screen renders and is NOT
    # re-pinned by a reader contract: the one byte range allowed to differ is put back to the
    # sealing commit's, and the swap must fire
    # Three moved groups, each put back at ITS OWN sealing moment: the v5 reader moved
    # `prompts.py`, r2 moved the registry and the producer that reads it through the seal, and S6
    # moved `aggregates.py` by adding the six promo tables. The last two seal at one commit for two
    # unrelated reasons, so they are two calls and not one list. Every swap must fire, or a record
    # that had quietly gone back to the sealed bytes would pass this comparison.
    produced = put_the_sealed_shas_back(first.read_bytes(), times=1)
    produced = put_the_sealed_shas_back(produced, times=1, moved=MOVED_BY_R2, at=SEALED_AT_R2)
    produced = put_the_sealed_shas_back(
        produced, times=1, moved=MOVED_BY_THE_PROMO_TABLES, at=SEALED_AT_R2
    )
    produced = put_the_sealed_shas_back(
        produced, times=1, moved=MOVED_BY_THE_SECOND_WINDOW, at=SEALED_AT_R2
    )
    assert produced == exporter.OUT.read_bytes()
    assert b'"at"' not in first.read_bytes(), "no clock in the body"
    diff = subprocess.run(
        ["diff", str(first), str(second)], capture_output=True, text=True, cwd=REPO_ROOT
    )
    assert diff.returncode == 0 and diff.stdout == ""


def test_every_metric_and_every_cut_names_the_sample_it_was_measured_on():
    """`.claude/rules/registrations-and-draws.md`, mechanised.

    A rate is a property of its sample, so every metric node carries a `sample` block with the
    sample's name, its size and a reading. The two-sample metrics carry one per sample as well, and
    the headline the dashboard shows is NAMED rather than left to the reader to infer.
    """
    for name, metric in RECORD["metrics"].items():
        assert "sample" in metric, name
        assert metric["sample"]["reading"], name
        for sample, block in metric.get("by_sample", {}).items():
            assert block["sample"]["name"] == sample
            assert block["sample"]["rows"] > 0
        if "by_sample" in metric:
            assert metric["headline_sample"] == exporter.HEADLINE

    # three and not eleven since SPEC 3.21 (1): the sample is the rows the matcher found a brand in
    # under revision r1, and the eight the rules removed were «варто» the adverb ×7 and a children's
    # centre named Гармонія. The sample block says which revision it counted under, right here.
    assert RECORD["metrics"]["sov"]["sample"]["rows"] == 3
    assert RECORD["metrics"]["sov"]["sample"]["of"] == 5075
    assert RECORD["metrics"]["sov"]["sample"]["watchlist_rules"] == "r1"
    assert RECORD["cuts"]["brand_by_sentiment"]["sample"]["name"] == "payable"
    assert RECORD["cuts"]["brand_by_sentiment"]["sample"]["watchlist_rules"] == "r1"


def test_the_payable_sample_is_the_headline_and_differs_from_the_bought_one():
    """SPEC 3.19 (2) is visible in the numbers, not only in the prose beside them."""
    nsr = RECORD["metrics"]["nsr"]["by_sample"]

    assert nsr["bought"]["scored"] == 5075
    assert nsr["payable"]["scored"] == 3714
    assert nsr["payable"]["nsr"] != nsr["bought"]["nsr"]
    assert exporter.HEADLINE == "payable"


def test_the_segment_cut_carries_every_audience_the_registry_holds():
    """Eight cards, not "however many segments happened to talk" — plan §3 T3.

    `food_quality` has one registry channel and produced no row of any kind this window, so it never
    reaches the `channels` table; a cut driven off the evidence renders seven. It is here with zeros
    and with `registry_channels: 1`, because an audience that said nothing is a finding and a
    missing card is not.

    The trap the fix had to avoid is asserted on the line below the key set: `channels` must still
    hold ONLY the channels that produced a row, or `coverage.channels.with_a_row` would read 66/66
    and the metric would be destroyed by its own denominator.
    """
    registry = load_registry(builder.REGISTRY)
    audiences = {source.audience for source in registry.sources if source.audience}
    cut = RECORD["cuts"]["comment_by_segment"]

    assert set(cut) == audiences
    assert len(cut) == RECORD["metrics"]["coverage"]["segments"]["in_registry"] == 8
    assert RECORD["metrics"]["coverage"]["segments"]["with_a_row"] == 7
    assert RECORD["metrics"]["coverage"]["channels"]["with_a_row"] == 28
    assert RECORD["metrics"]["coverage"]["channels"]["in_registry"] == 66

    silent = cut["food_quality"]
    assert silent["channels_with_a_row"] == []
    assert silent["registry_channels"] == 1
    assert silent["payable"]["rows"] == 0 and silent["bought"]["rows"] == 0
    assert silent["payable"]["sarcasm"]["rate"] is None, "a rate over no rows is null, never 0.0"

    # and the one that has evidence but no conversation is a different state again
    quiet = cut["regional"]
    assert quiet["channels_with_a_row"] and quiet["bought"]["rows"] == 0


def test_the_promo_surface_carries_every_chain_the_amendment_names():
    """SPEC 3.20 (6): Маркетопт beside АТБ, Сільпо and Varus — present, not conditional on rows.

    The amendment's own text is grepped for the handle, so the list in the producer cannot drift
    from the law that put it there, and every id is checked to be a real registry source.
    """
    spec = (REPO_ROOT / "docs" / "SPEC.md").read_text(encoding="utf-8")
    block = spec.split("<!-- amendment-3.20 begin")[1].split("<!-- amendment-3.20 end")[0]
    chains = RECORD["metrics"]["promo_pressure"]["by_chain"]
    registry = load_registry(builder.REGISTRY)
    ids = {source.id for source in registry.sources}

    assert "@marketopt_promo" in block
    assert "marketopt_promo" in exporter.PROMO_CHAINS
    for source_id in exporter.PROMO_CHAINS:
        assert source_id in ids, source_id
        assert chains[source_id]["named_by_amendment_3_20"] is True
    assert chains["marketopt_promo"]["position_rows"] > 0
    assert set(chains["atb"]["by_carrier"]) == {"leaflet_page"}
    assert set(chains["marketopt_promo"]["by_carrier"]) == {"post_text"}


def test_the_positions_table_answers_for_the_whole_window_and_carries_no_old_price():
    """SPEC 3.21 (4): the promo answer, whole — and the price 3.17 (3) keeps off every surface.

    Three claims, and the third is the one that needed a decision. The table is the WINDOW's
    population and not a draw from it; its own count is the shared figure the anchor checks. Every
    field it carries is one the contract names. And `depth` is the printed badge's reading, never
    the arithmetic depth of the price pair: the substring check on the block's own JSON is the blunt
    half, and the row-by-row identity `depth == printed_pct / 100` is the half that would catch the
    arithmetic reading arriving under the right key.
    """
    table = RECORD["promo"]["positions_table"]
    rows = table["rows"]
    fields = {name for row in rows for name in row}

    assert len(rows) == table["sample"]["rows"] == RECORD["window"]["populations"]["position_rows"]
    assert len(rows) == 145
    assert table["window"] == builder.WINDOW_ID and table["sample"]["reading"]
    assert fields == {
        "row_id",
        "brand",
        "item",
        "chain",
        "carrier",
        "promo_price",
        "printed_pct",
        "depth",
        "tier",
        "evidence",
    }
    # the ROWS, not the block: `law` explains in prose which price is absent and why, and a
    # substring check over the explanation would forbid the record from saying what it forbids
    assert "price_old" not in json.dumps(rows, ensure_ascii=False)
    assert "price_old" in table["law"] and "3.17 (3)" in table["law"]
    assert {name for row in rows for name in row["item"]} <= {
        "line",
        "category",
        "size_value",
        "size_unit",
        "pack_count",
        "attribute_pct",
    }
    for row in rows:
        assert ("depth" in row) == ("printed_pct" in row)
        if "depth" in row:
            assert row["depth"] == round(row["printed_pct"] / 100, 4)
        assert ("own" in row["brand"]) == ("id" in row["brand"])
        assert row["brand"]["display"] and row["evidence"]["channel"].startswith("@")

    # what the window actually holds, so a table that silently lost its unresolved half or its
    # second carrier would fail here rather than look tidy
    assert sum(1 for row in rows if "id" in row["brand"]) == 80
    assert sum(1 for row in rows if row["brand"].get("own")) == 0
    assert sum(1 for row in rows if "promo_price" in row) == 138
    assert sum(1 for row in rows if "depth" in row) == 128
    assert {row["carrier"] for row in rows} == {"leaflet_page", "post_text"}


def test_a_position_the_registry_join_drops_stops_the_export(tmp_path):
    """The negative control for the table's own refusal — a row lost on a join, not in the data.

    The chain column is a JOIN to `channels`, so a channel that is not there takes its positions out
    of the table while `positions` still holds them. That is the failure the count check exists for:
    the table would still look like a complete answer, one chain shorter.
    """
    conn = builder.build(builder.DERIVED, builder.PREREG, builder.REGISTRY, tmp_path / "pulse.db")[
        0
    ]
    conn.execute(
        "DELETE FROM channels WHERE window_id = ? AND channel = ?",
        (builder.WINDOW_ID, "@marketopt_promo"),
    )

    with pytest.raises(SystemExit, match="holds 141 rows and the window has 145 positions"):
        exporter.promo_block(conn, builder.WINDOW_ID)


def test_what_cannot_be_computed_says_so_with_its_unlock_condition():
    """Honest stubs, never zeros — and each one names the surface and what would unlock it."""
    stubs = RECORD["not_computable"]

    assert set(stubs) >= {
        "trend_vs_previous_window",
        "alert_baselines",
        "category_layer",
        "leaflet_depth_for_silpo_varus_marketopt",
        "reach",
    }
    for name, stub in stubs.items():
        assert stub["reason"] and stub["unlock"] and stub["surface"], name
        assert not aggregates.numeric_leaves(stub), f"{name} carries a number, which is a value"


def test_the_provenance_block_pins_its_inputs_and_its_producers():
    """Inputs + shas + producer shas, and no wall-clock anywhere in the record."""
    provenance = RECORD["provenance"]

    for name, digest in provenance["producers"].items():
        assert_pinned(name, digest)
    for name, digest in provenance["inputs"].items():
        if name == "config/registry.yaml":
            # Pinned at r1, not at today's bytes: revision r2 moved the file and a sealed export is
            # never re-pinned by a later revision. The undo is what makes the pin reachable.
            assert builder.summary.sha256_of(REPO_ROOT / name) != digest, name
            assert r1_registry_sha() == digest, name
            continue
        assert builder.summary.sha256_of(REPO_ROOT / name) == digest, name
    for name, digest in provenance["evidence"].items():
        assert builder.summary.sha256_of(REPO_ROOT / name) == digest, name
    assert len(provenance["evidence"]) > 20
    assert "scripts/export_dashboard_data.py" in provenance["producers"]
    assert "results/window_summary_5c2.json" in provenance["inputs"]
