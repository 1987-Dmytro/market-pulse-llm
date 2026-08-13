"""The D cut of SPEC 3.18 (7)(g): the rule on a census whose answer is known by hand, and then the
shipped record re-derived from the shipped census.

The fixture half is where the RULE is tested — a union of two halves, over a carrier field that is
the channel's and not the row's — because a nine-row census can be counted by a reader and 349 rows
cannot. The shipped half re-computes every headline from `results/census_c3a_posts.json` with code
that does not import the producer's own helpers where it can avoid them, so a number in the record
and a number in this file are two readings and not one.
"""

import ast
import hashlib
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import postcut_c3b as cut  # noqa: E402

SHIPPED = json.loads((REPO_ROOT / "results" / "postcut_c3b.json").read_text(encoding="utf-8"))
CENSUS = json.loads((REPO_ROOT / "results" / "census_c3a_posts.json").read_text(encoding="utf-8"))

PRICED = "Молоко Яготинське 2,5% 900 г — 39,90 грн"
"""A line with a currency marker on it — `39,90 грн`."""

RECIPE = "Сир 200 г, яйця 2 шт, борошно — змішати і випікати 40 хвилин"
"""A line with a size and no price at all: the class the ruling exists to remove."""


def a_row(row_id: str, channel: str, line: str, kinds: list[str]) -> dict:
    return {
        "id": row_id,
        "channel": channel,
        "date": "2026-07-20T10:00:00+00:00",
        "line": line,
        "hit": "category:dairy:сир",
        "matched": "сир",
        "pattern": "200 г",
        "pattern_kinds": kinds,
        "carrier": "post_text",
    }


CHANNELS = [
    {"handle": "@retail", "source_type": "official_retail", "audience": "retail_official"},
    {"handle": "@agg", "source_type": "aggregator", "audience": "supermarket_deals"},
    {"handle": "@cook", "source_type": "community", "audience": "cooking_recipes"},
]

ROWS = [
    a_row("@retail:1", "@retail", RECIPE, ["size"]),  # carrier only
    a_row("@retail:2", "@retail", PRICED, ["currency", "size"]),  # both
    a_row("@agg:1", "@agg", RECIPE, ["size"]),  # carrier only
    a_row("@cook:1", "@cook", PRICED, ["currency", "size"]),  # currency only
    a_row("@cook:2", "@cook", RECIPE, ["size"]),  # dropped
    a_row("@cook:3", "@cook", RECIPE, ["size", "percent"]),  # dropped
]
"""Six rows: three kept by the carrier half (two of them, plus one that is also priced), one kept by
the currency half alone, two dropped. Counted by hand — 4 kept, and `carrier_only` 2, `currency_only`
1, `both` 1."""


def wire(monkeypatch, tmp_path, rows=ROWS, channels=CHANNELS) -> Path:
    """A census with the fixture's rows in it, written where the producer will read it."""
    census = {
        "anchor": {"anchor": "2026-08-09T00:00:00+00:00"},
        "totals": {"passed": len(rows)},
        "frame": {"ids_sha256": "fixture"},
        "channels": [
            {**channel, "passed": sum(1 for row in rows if row["channel"] == channel["handle"])}
            for channel in channels
        ],
        "rows": rows,
    }
    path = tmp_path / "census.json"
    path.write_text(json.dumps(census, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    monkeypatch.setattr(cut, "CENSUS", path)
    return path


def run(tmp_path, out="cut.json", expect=0) -> dict:
    assert cut.main(["--out", str(tmp_path / out)]) == expect
    return json.loads((tmp_path / out).read_text(encoding="utf-8"))


# --- the rule, on a census a reader can count -------------------------------------------------


def test_the_cut_keeps_exactly_the_rows_the_ruling_names(monkeypatch, tmp_path):
    wire(monkeypatch, tmp_path)

    record = run(tmp_path)

    assert [row["id"] for row in record["rows"]] == [
        "@retail:1",
        "@retail:2",
        "@agg:1",
        "@cook:1",
    ]
    assert record["kept"]["rows"] == 4
    assert record["kept"]["by_reason"] == {"carrier_only": 2, "currency_only": 1, "both": 1}


def test_the_rule_is_a_union_and_not_an_intersection(monkeypatch, tmp_path):
    """The negative control for the shape of the rule. Under an intersection only `@retail:2` — the
    one row that is both — would survive, and the count would be 1 rather than 4."""
    wire(monkeypatch, tmp_path)

    record = run(tmp_path)

    both = [row for row in record["rows"] if len(row["kept_by"]) == 2]
    assert [row["id"] for row in both] == ["@retail:2"]
    assert record["kept"]["rows"] > len(both)
    assert {tuple(row["kept_by"]) for row in record["rows"]} == {
        ("carrier",),
        ("currency",),
        ("carrier", "currency"),
    }


def test_the_carrier_read_is_the_channels_type_and_not_the_rows_own_carrier_field(
    monkeypatch, tmp_path
):
    """Every census row carries `carrier: post_text` — the EVIDENCE carrier, where the text was
    read. The ruling asks who is SPEAKING, which only the channel's registry type answers.

    The control: give one channel a `source_type` the rule does not keep and watch its unpriced row
    leave, while its own `carrier` field never changes. A producer reading the row's field would
    keep all six or none, and the count would not move at all.
    """
    wire(monkeypatch, tmp_path)
    baseline = run(tmp_path)
    assert {row["carrier"] for row in ROWS} == {"post_text"}

    demoted = [{**channel} for channel in CHANNELS]
    demoted[0]["source_type"] = "community"
    wire(monkeypatch, tmp_path, channels=demoted)
    record = run(tmp_path, "demoted.json")

    assert baseline["kept"]["rows"] == 4 and record["kept"]["rows"] == 3
    assert "@retail:1" not in {row["id"] for row in record["rows"]}
    assert "@retail:2" in {row["id"] for row in record["rows"]}, "still kept — by its price"


def test_a_population_whose_two_readings_disagree_is_reported_and_the_run_refuses(
    monkeypatch, tmp_path
):
    """`pattern_kinds` is the ANYWHERE reading and SPEC's wording is the matched-LINE one. A row
    whose currency sits somewhere OTHER than the line that fired is where they part, and the
    producer's exit code is what makes that visible instead of quietly choosing."""
    split = [*ROWS, a_row("@cook:4", "@cook", RECIPE, ["size", "currency"])]
    wire(monkeypatch, tmp_path, rows=split)

    record = run(tmp_path, expect=1)

    readings = record["rule"]["two_readings"]
    assert readings["agree"] is False
    assert readings["rows_only_one_reading_keeps"] == ["@cook:4"]
    assert readings["cut_under_the_anywhere_reading"] == 5
    assert readings["cut_under_the_matched_line_reading"] == 4


def test_the_three_declined_alternatives_are_recounted_from_the_same_rows(monkeypatch, tmp_path):
    wire(monkeypatch, tmp_path)

    record = run(tmp_path)

    assert record["alternatives_declined"]["counts"] == {
        "all_that_pass": 6,
        "carriers_only": 3,
        "currency_only": 2,
    }
    priced = record["alternatives_declined"]["usd_with_drift"]
    assert priced["all_that_pass"] > priced["carriers_only"] > 0


def test_the_same_census_reproduces_the_artifact_byte_for_byte(monkeypatch, tmp_path):
    wire(monkeypatch, tmp_path)

    run(tmp_path, "first.json")
    run(tmp_path, "second.json")

    assert (tmp_path / "first.json").read_bytes() == (tmp_path / "second.json").read_bytes()


def test_the_record_carries_no_clock_and_no_git_state_and_names_its_producer(monkeypatch, tmp_path):
    """`census_c3a_posts`' pair of hygiene checks, on this producer: byte-identity under one input
    is this record's gate, and both a clock and `git status --porcelain` void it."""
    wire(monkeypatch, tmp_path)
    record = run(tmp_path)

    assert "generated_at" not in record and "timestamp" not in record and "git" not in record
    assert (
        record["producer"]["sha256"] == hashlib.sha256(Path(cut.__file__).read_bytes()).hexdigest()
    )
    tree = ast.parse(Path(cut.__file__).read_text(encoding="utf-8"))
    called = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert not called & {"now", "utcnow", "today", "time"}
    assert not [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "git_state"
    ]


# --- the shipped record, re-derived from the shipped census -------------------------------------


def recompute() -> list[dict]:
    """The cut, computed here with a second implementation of the same sentence."""
    types = {row["handle"]: row["source_type"] for row in CENSUS["channels"]}
    return [
        row
        for row in CENSUS["rows"]
        if types[row["channel"]] in ("official_retail", "aggregator")
        or "currency" in row["pattern_kinds"]
    ]


def test_the_shipped_cut_is_the_shipped_census_run_through_the_rule():
    mine = recompute()

    assert SHIPPED["kept"]["rows"] == len(mine) == 44
    assert [row["id"] for row in SHIPPED["rows"]] == [row["id"] for row in mine]
    assert (
        SHIPPED["input"]["sha256"]
        == hashlib.sha256(
            (REPO_ROOT / "results" / "census_c3a_posts.json").read_bytes()
        ).hexdigest()
    )
    assert SHIPPED["input"]["passed"] == CENSUS["totals"]["passed"] == 349


def test_the_kept_ids_hash_to_the_pin_the_preregistration_will_read():
    """A count pins the size; the hash pins WHICH rows, which is what a run has to reproduce."""
    rebuilt = hashlib.sha256(
        "\n".join(row["id"] for row in SHIPPED["rows"]).encode("utf-8")
    ).hexdigest()

    assert SHIPPED["kept"]["ids_sha256"] == rebuilt
    assert rebuilt != CENSUS["frame"]["ids_sha256"], "a subset of a frame is not that frame"


def test_the_by_reason_split_accounts_for_every_kept_row():
    split = SHIPPED["kept"]["by_reason"]

    assert sum(split.values()) == SHIPPED["kept"]["rows"]
    assert split == {"carrier_only": 15, "currency_only": 13, "both": 16}
    # the overlap is what makes 31 + 29 land at 44 and not near 60 — the record's own explanation
    counts = SHIPPED["alternatives_declined"]["counts"]
    assert counts["carriers_only"] + counts["currency_only"] - split["both"] == 44


def test_the_three_declined_alternatives_are_the_numbers_the_ruling_states():
    """Grepped back out of the law, not copied from a brief that summarised it."""
    spec = (REPO_ROOT / "docs" / "SPEC.md").read_text(encoding="utf-8")
    counts = SHIPPED["alternatives_declined"]["counts"]

    assert "(all 349 / carriers-only 31 / currency-only 29)" in spec
    assert (counts["all_that_pass"], counts["carriers_only"], counts["currency_only"]) == (
        349,
        31,
        29,
    )


def test_every_quoted_line_of_the_rule_is_in_the_spec_verbatim():
    spec = (REPO_ROOT / "docs" / "SPEC.md").read_text(encoding="utf-8").splitlines()
    stripped = [line.strip() for line in spec]

    for quote in SHIPPED["rule"]["verbatim"]:
        assert stripped.count(quote) == 1, quote
    assert "a row is kept iff its channel's carrier" in " ".join(SHIPPED["rule"]["verbatim"])


def test_no_cooking_channel_survives_the_cut():
    """What the ruling was FOR — and the two numbers for it, which are not the same number.

    3.18 (7)(g) says "250 of 349 rows from four cooking channels". Counted here, the
    `cooking_recipes` audience holds 270 rows across SIX channels with a pass; the ruling's 250 is
    the top four of the concentration table. The cut removes all 270, so the clause understates the
    population it removes — a floor, not a disagreement, and the record prints both.
    """
    audiences = {row["handle"]: row["audience"] for row in CENSUS["channels"]}
    removed = SHIPPED["removed_recipes"]

    assert SHIPPED["kept"]["recipe_channels_kept"] == [] and removed["kept_from_them"] == 0
    assert {audiences[row["channel"]] for row in SHIPPED["rows"]} == {
        "retail_official",
        "supermarket_deals",
        "regional",
    }
    cooking = [row for row in CENSUS["rows"] if audiences[row["channel"]] == "cooking_recipes"]
    assert len(cooking) == removed["cooking_recipes_rows"] == 270
    assert removed["the_rulings_four"] == 250 and len(removed["the_rulings_four_are"]) == 4
    assert len(removed["cooking_recipes_channels_with_a_pass"]) == 6
    assert "250 of 349 rows from four cooking channels" in (
        REPO_ROOT / "docs" / "SPEC.md"
    ).read_text(encoding="utf-8").replace("\n", " ")


def test_the_two_readings_of_the_rulings_wording_agree_on_this_population():
    """The ambiguity, closed by measurement: no row's currency sits off the line that fired."""
    readings = SHIPPED["rule"]["two_readings"]

    assert readings["agree"] is True
    assert readings["rows_only_one_reading_keeps"] == []
    assert (
        readings["carrying_currency_anywhere"]
        == readings["carrying_currency_on_the_matched_line"]
        == CENSUS["totals"]["passed_carrying"]["currency"]
        == 29
    )


def test_the_price_is_the_kept_count_times_the_paid_marginal_plus_one_idle_tail():
    priced = SHIPPED["priced"]
    seconds = 44 * priced["seconds_per_row"] + 60.0

    assert priced["rows"] == 44 and priced["seconds_per_row"] == 2.8132
    assert priced["billed_seconds"] == round(seconds, 1)
    assert priced["usd_with_drift"] == round(seconds * SHIPPED["rate"]["value"] * 1.03, 4)
    assert priced["usd_with_drift"] == 0.0581


def test_the_magnitude_check_reports_the_miss_instead_of_hiding_it():
    """The contract expects 50–55 and the cut is 44. What the range protects is the registered cap,
    and the check has to say so with the arithmetic rather than with a reassurance."""
    check = SHIPPED["magnitude_check"]

    assert check["measured_rows"] == 44 and check["expected_rows"] == [50, 55]
    assert check["inside_the_expected_range"] is False
    # the claim the check makes, re-derived: 44 and 55 rows differ by under two cents
    at_55 = (55 * 2.8132 + 60.0) * SHIPPED["rate"]["value"] * 1.03
    assert at_55 - check["measured_usd_with_drift"] < 0.02


def test_the_producer_names_every_module_it_is_built_out_of_by_sha():
    """9c723a7's finding, carried forward: this producer copies another module's arithmetic into the
    record, so its own sha does not cover what produced the numbers."""
    borrows = SHIPPED["producer"]["borrows"]

    assert set(borrows) == {
        "scripts/census_5c2.py",
        "scripts/census_c3a_posts.py",
        "scripts/projection_5c2.py",
        "scripts/sku_prefilter_census.py",
        "scripts/write_sku_projection_b2.py",
    }
    for path, digest in borrows.items():
        assert hashlib.sha256((REPO_ROOT / path).read_bytes()).hexdigest() == digest, path


def test_the_cut_does_not_write_the_census_it_reads():
    """The DO NOT, asserted where it can be seen: the producer's only write is its own `--out`."""
    tree = ast.parse(Path(cut.__file__).read_text(encoding="utf-8"))
    written = {
        ast.unparse(node.func.value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in ("write_text", "write_bytes", "open")
    }

    assert written == {"args.out"}


@pytest.mark.parametrize("field", ["kept", "priced", "magnitude_check", "alternatives_declined"])
def test_the_headline_blocks_are_all_present(field):
    assert field in SHIPPED
