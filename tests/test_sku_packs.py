"""The two ground-truth packs: the leaflet reference, and the 30-row pack with its validator.

What is guarded here is not the counts but the properties a bar rests on. The leaflet gold is a
6-page SLICE judged per POST, and four of its posts have an empty brand set — all three facts have to
survive in the record or bar 1 is computed over something nobody described. The text pack must
propose nothing, must be re-derivable from a hash-checked frame, and must tier its returns through
the SAME ladder that tiers the model.
"""

import csv
import hashlib
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

import build_sku_reference_leaflet as leaflet  # noqa: E402
import build_sku_text_pack as pack  # noqa: E402
import validate_sku_text_pack as validator  # noqa: E402

from market_pulse import positions  # noqa: E402
from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

ALIASES = watchlist_aliases(load_registry(REPO_ROOT / "config" / "registry.yaml").watchlist)


# --- the leaflet reference ------------------------------------------------------------------------


@pytest.fixture(scope="module")
def reference():
    return json.loads(leaflet.RECORD.read_text(encoding="utf-8"))


def test_the_reference_is_the_nineteen_atb_posts_of_the_audits_S4(reference):
    assert reference["population"] == {
        "channel": "@atb_market_official",
        "stratum": "S4",
        "posts": 19,
        "pages_sent": 108,
        "pages_available": 159,
        "posts_whose_pages_were_truncated": reference["population"][
            "posts_whose_pages_were_truncated"
        ],
    }
    assert len(reference["posts"]) == 19
    assert len({row["item"] for row in reference["posts"]}) == 19
    assert len(reference["population"]["posts_whose_pages_were_truncated"]) == 15


def test_every_page_the_reviewer_saw_is_on_disk_under_the_sha_it_was_sent_with(reference):
    """The pilot is scored against these pages. A moved page is a comparison against a picture
    nobody judged, so the builder verifies all 108 and refuses to write if one differs."""
    assert reference["images_verified"] == {
        "checked": 108,
        "sha_matched": 108,
        "missing": [],
        "sha_differs": [],
    }
    for row in reference["posts"]:
        assert [page["page"] for page in row["pages_sent"]] == list(
            range(1, len(row["pages_sent"]) + 1)
        )
        for page in row["pages_sent"]:
            path = REPO_ROOT / page["file"]
            assert path.exists(), page["file"]
            assert hashlib.sha256(path.read_bytes()).hexdigest() == page["sha256"]


def test_the_gold_is_per_post_and_the_record_says_so(reference):
    """Bar 1 says "per page" and this gold cannot be split that way — one reviewer judged the whole
    sent set. The fact lives in the record so the pre-registration can cite it instead of a reader
    assuming a per-page denominator exists."""
    assert "NOTHING here attributes a brand to a page" in reference["gold"]["per_post_not_per_page"]
    assert "sku_pilot_prereg" in reference["gold"]["per_post_not_per_page"]
    for row in reference["posts"]:
        assert set(row["brands_visible"]) == {
            "gold_keys",
            "watchlist",
            "other_dairy_brands",
            "missed_by_the_matcher",
            "n",
        }
        # no page index anywhere inside the brand block
        assert "page" not in json.dumps(row["brands_visible"])


def test_the_pages_are_a_slice_and_the_unsent_ones_are_named(reference):
    """15 of 19 posts sent 6 of a longer album, so a brand on page 7 is not in this gold and a
    pilot naming one is not wrong. `pages_not_sent` is what makes that checkable."""
    slices = [row for row in reference["posts"] if row["pages_not_sent"]]
    assert len(slices) == 15
    for row in reference["posts"]:
        assert len(row["pages_sent"]) + len(row["pages_not_sent"]) == row["pages_available"]
        assert len(row["pages_sent"]) <= 6
        sent = {page["file"] for page in row["pages_sent"]}
        assert not sent & set(row["pages_not_sent"]), "a page cannot be both sent and unsent"
    assert "pages_are_a_slice" in reference["gold"]


def test_four_posts_have_an_empty_gold_set_and_cannot_carry_a_recall(reference):
    """Recall over an empty denominator is undefined, and an absolute bar computed over one fails by
    arithmetic. So the four are named in the record and the pre-registration excludes them from the
    recall average, keeping them as a precision probe."""
    empty = [row["item"] for row in reference["posts"] if not row["brands_visible"]["n"]]
    assert reference["gold"]["posts_with_an_empty_gold_set"] == empty
    assert len(empty) == 4
    assert reference["gold"]["posts_with_a_non_empty_gold_set"] == 15
    assert "undefined" in reference["gold"]["empty_set_note"]
    for row in reference["posts"]:
        if row["item"] in empty:
            assert row["brands_visible"]["watchlist"] == []
            assert row["brands_visible"]["other_dairy_brands"] == []
            assert row["reviewer_note"], "an empty set still has to say what IS on the pages"


def test_the_gold_key_normalises_two_field_spaces_into_one(reference):
    """`watchlist_hits` arrive as brand_ids and `other_dairy_brands` as names as printed. Scoring
    them unnormalised would compare «Каштан» against a brand_id and call the match a miss."""
    for row in reference["posts"]:
        block = row["brands_visible"]
        expected = sorted(
            {leaflet.gold_key(name, ALIASES) for name in block["watchlist"]}
            | {leaflet.gold_key(name, ALIASES) for name in block["other_dairy_brands"]}
        )
        assert block["gold_keys"] == expected
        assert block["n"] == len(expected)
        for key in block["gold_keys"]:
            assert key in ALIASES.values() or key.startswith("raw:")
    assert reference["gold"]["pairs"] == 55
    assert reference["gold"]["from_the_watchlist"] == 34
    assert reference["gold"]["outside_the_watchlist"] == 21


def test_the_matchers_misses_are_a_subset_of_the_watchlist_brands_seen(reference):
    """The two audit fields describe one reading, and the builder refuses to write if they stop
    agreeing — this is that check standing on the shipped record."""
    for row in reference["posts"]:
        block = row["brands_visible"]
        assert set(block["missed_by_the_matcher"]) <= set(block["watchlist"]), row["item"]


def test_the_reference_pins_what_it_was_built_from(reference):
    for path, sha in reference["sources"].items():
        assert hashlib.sha256((REPO_ROOT / path).read_bytes()).hexdigest() == sha, path
    assert set(reference["sources"]) >= {
        "results/opus_audit_5c1.json",
        "results/opus_audit_manifest.json",
        "data/annotation/captions_5c1/gm4_atb19.jsonl",
        "config/registry.yaml",
    }
    assert reference["audit_instrument"]["model"] == "claude-opus-5"
    assert "declared_not_verified" in reference["audit_instrument"]
    assert reference["caption_verdicts"] == {
        "faithful": 9,
        "partial": 10,
        "wrong": 0,
        "n/a": 0,
    }


def test_the_reference_declares_itself_scoring_input(reference):
    """Dv87 in reverse: the audit packs went blind so a reviewer could not be anchored by the
    matcher's answer, and this file must never reach the pilot's request either."""
    assert "SCORING input, never model input" in reference["class"]
    assert "REVIEW class" in reference["provenance"]


def test_a_moved_population_stops_the_build(monkeypatch, tmp_path):
    """The negative control on the population check: 19 is the pre-registered leaflet leg, and a
    reference over a different count would not be what the bar was registered over."""
    monkeypatch.setattr(leaflet, "EXPECTED_POSTS", 18)
    with pytest.raises(SystemExit, match="audit population moved"):
        leaflet.main(["--out", str(tmp_path / "ref.json")])


def test_the_reference_rebuilds_byte_identically_apart_from_its_own_timestamp(tmp_path):
    out = tmp_path / "ref.json"
    assert leaflet.main(["--out", str(out)]) == 0
    a = json.loads(out.read_text(encoding="utf-8"))
    b = json.loads(leaflet.RECORD.read_text(encoding="utf-8"))
    for record in (a, b):
        record.pop("generated_at"), record.pop("git")
    assert a == b


# --- the text pack -------------------------------------------------------------------------------


@pytest.fixture(scope="module")
def manifest():
    return json.loads(pack.MANIFEST.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def rows():
    return validator.read_pack(pack.PACK)


def fresh_rows(tmp_path) -> list[dict]:
    """A blank pack built into a temp directory — the fixture every validator test mutates.

    Deliberately not the shipped CSV: once the operator starts ticking it, a test that mutated it
    would be asserting against somebody's half-finished evening. A fresh build carries the same
    GIVEN columns by construction, so it still verifies against the committed manifest.
    """
    out = tmp_path / "blank.csv"
    assert pack.main(["--pack", str(out), "--manifest", str(tmp_path / "blank.json")]) == 0
    return validator.read_pack(out)


def test_the_pack_is_thirty_rows_and_every_tick_ships_blank(rows, manifest):
    """Nothing is proposed: a suggested tier is not independent adjudication."""
    assert len(rows) == manifest["rows"] == 30
    assert list(rows[0]) == list(pack.COLUMNS)
    for row in rows:
        assert row["text"].strip(), "a row with no text cannot be adjudicated"
    if pack.filled(pack.PACK):
        pytest.skip(
            "adjudication has started — blankness is a build-time property, not an invariant"
        )
    for row in rows:
        for field in positions.PRESENCE_FIELDS:
            assert row[field] == "", (row["id"], field)
        assert row["notes"] == ""


def test_a_fresh_build_is_always_blank_whatever_the_shipped_pack_now_holds(tmp_path):
    """The half of the test above that must never be skipped.

    "Nothing is proposed" is a property of the BUILDER, and the builder is what a re-run uses. The
    shipped pack stops being blank the moment the operator starts, and a suite that went red for
    that would be a suite the next session loosens — the failure this repo has refused twice
    (`test_yield_screen_5c1`, `read_calibration_returns`).
    """
    out = tmp_path / "text30.csv"
    assert pack.main(["--pack", str(out), "--manifest", str(tmp_path / "m.json")]) == 0
    for row in validator.read_pack(out):
        for field in positions.PRESENCE_FIELDS:
            assert row[field] == "", (row["id"], field)
        assert row["notes"] == ""
    assert pack.filled(out) == 0


def test_the_pack_carries_the_columns_the_ladder_reads_and_no_price_column(rows):
    """Bar 3 is tier accuracy, and a price does not move a rung. Asking for one would be 30 rows of
    the operator's evening spent on a column nothing reads."""
    assert set(positions.PRESENCE_FIELDS) == {"brand", "line", "category", "size", "fat"}
    assert not {"price_promo", "price_old", "discount_pct_printed"} & set(rows[0])


def test_the_draw_is_reproducible_from_the_frame_it_names(manifest):
    """Seed 42 over the census frame in the record's own order. Re-derived here rather than trusted:
    a draw nobody can reproduce is not a sample."""
    census, frame = pack.frame_from_census(pack.CENSUS)
    assert manifest["draw"]["frame"]["ids_sha256"] == census["frame"]["ids_sha256"]
    assert manifest["draw"]["frame"]["sha256"] == pack.sha256_of(pack.CENSUS)
    drawn = pack.draw(frame)
    assert sorted(row["id"] for row in drawn) == sorted(manifest["ids"])
    # and a different seed draws a different sample, or the seed is not doing anything
    assert sorted(row["id"] for row in pack.draw(frame, seed=43)) != sorted(manifest["ids"])


def test_a_frame_whose_hash_does_not_match_is_refused(tmp_path):
    """The negative control: a census edited by hand must not be drawable from."""
    record = json.loads(pack.CENSUS.read_text(encoding="utf-8"))
    record["rows"] = record["rows"][:-1]
    broken = tmp_path / "census.json"
    broken.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(SystemExit, match="not the frame it describes"):
        pack.frame_from_census(broken)


def test_the_manifest_pins_the_ladder_the_gold_will_be_computed_by(manifest):
    """The gold tier and the model's tier come out of one function, so a ladder that moved between
    the build and the pilot would move the gold silently."""
    assert manifest["ladder"]["sha256"] == positions.ladder_sha256()
    assert manifest["ladder"]["table"] == positions.ladder_table()
    assert len(manifest["ladder"]["table"]) == 32
    assert manifest["ladder"]["function"] == "market_pulse.positions.tier_from_presence"


def test_the_manifest_pins_the_columns_that_must_not_move(rows, manifest):
    """`given_sha256` covers the QUESTION and stands still while the answer is written; the CSV's
    whole-file sha is expected to move on the first tick, which is why they are two fields and why
    only one of them is an invariant."""
    assert manifest["given_sha256"] == pack.given_sha256(rows)
    assert manifest["given_columns"] == list(pack.GIVEN)
    assert [row["id"] for row in rows] == manifest["ids"]
    readme = pack.PACK.parent / pack.README.name
    assert (
        hashlib.sha256(readme.read_bytes()).hexdigest() == manifest["sha256"][pack.rel(readme)]
    ), "the instructions are not filled in and their sha does not move"
    assert "expected to move" in manifest["csv_sha_note"]


def test_the_shipped_csv_still_hashes_to_the_manifest_while_it_is_blank(manifest):
    """A build-time property, and it says so. Once a tick is entered the file is a different
    artifact by design — skipping here rather than asserting is what stops the next session from
    loosening `given_sha256` along with it."""
    if pack.filled(pack.PACK):
        pytest.skip("adjudication has started — the CSV's whole-file sha is expected to have moved")
    assert (
        hashlib.sha256(pack.PACK.read_bytes()).hexdigest()
        == manifest["sha256"][pack.rel(pack.PACK)]
    )


def test_the_carrier_split_is_reported_rather_than_engineered(rows, manifest):
    """Comments are 52 of the frame's 769 rows, so a proportional draw holds a handful. That is the
    contract's draw as written, and the consequence — bar 3 prices the POST leg — is named."""
    counted = {}
    for row in rows:
        counted[row["carrier"]] = counted.get(row["carrier"], 0) + 1
    assert manifest["draw"]["by_carrier"] == counted
    assert counted["comment"] < counted["post_text"]
    assert "prices the POST leg" in manifest["draw"]["comment_leg_note"]
    assert manifest["draw"]["rule"].startswith("random.Random(42).sample")
    assert "NOT" in manifest["draw"]["rule"], "the absence of stratification is stated"


def test_the_pack_says_it_also_prices_the_prefilter(manifest):
    """A drawn row whose five ticks all come back empty names no position, which makes it a
    pre-filter false positive. The frame is dominated by recipe feeds, so this is the only artifact
    that prices that — and it has to be said before the returns arrive, not after."""
    assert "pre-filter false positive" in manifest["also_measures"]
    assert "recipe feeds" in manifest["also_measures"]


def test_the_readme_asks_for_ticks_and_forbids_writing_a_tier():
    readme = (pack.PACK.parent / pack.README.name).read_text(encoding="utf-8")
    assert "руками ярус не пишем" in readme
    for field in positions.PRESENCE_FIELDS:
        assert f"`{field}`" in readme, field
    assert "оставь ВСЕ пять пустыми" in readme, "the no-position answer is a legitimate one"
    assert "самый подробно описанный" in readme, "the max-tier rule for a multi-position row"
    assert "Не трогай" in readme
    assert "`;`" in readme


def test_a_filled_pack_reads_back_through_the_same_ladder_as_the_model(tmp_path, manifest):
    """The validator's own exam, on a pack filled in by hand. Three shapes: a full position, a bare
    brand mention, and a row that names nothing — which is a legitimate answer and not a gap."""
    rows = fresh_rows(tmp_path)
    rows[0].update({"brand": "y", "category": "y", "size": "y"})
    rows[1].update({"brand": "y"})
    rows[2].update({"notes": "не про товар"})
    filled = tmp_path / "filled.csv"
    with filled.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=pack.COLUMNS, delimiter=pack.DELIMITER, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    readings, defects = validator.check(validator.read_pack(filled), manifest)
    assert defects == []
    assert readings[0]["tier"] == "position"
    assert readings[1]["tier"] == "brand_mention"
    assert readings[2]["tier"] == "none"
    assert validator.main(["--pack", str(filled)]) == 0


def test_the_validator_refuses_a_cell_that_is_not_a_tick(tmp_path, manifest):
    rows = fresh_rows(tmp_path)
    rows[0]["brand"] = "так"
    _, defects = validator.check(rows, manifest)
    assert any("takes y or nothing" in defect for defect in defects)


def test_the_validator_catches_a_question_that_moved(tmp_path, manifest):
    """A row whose `text` was edited was adjudicated against something else, and the whole-file sha
    cannot see it — it moves the moment a tick is entered. The given-columns hash can."""
    rows = fresh_rows(tmp_path)
    rows[0]["text"] = rows[0]["text"] + " (edited)"
    _, defects = validator.check(rows, manifest)
    assert any("different question" in defect for defect in defects)
    dropped = rows[:-1]
    _, defects = validator.check(dropped, manifest)
    assert any("ids or their order moved" in defect for defect in defects)


def test_the_validator_catches_a_ladder_that_moved(monkeypatch, tmp_path, manifest):
    """The check the pre-registration exists for: the gold is computed from the operator's ticks by
    this code, so a changed ladder is a changed gold."""
    monkeypatch.setitem(manifest["ladder"], "sha256", "f" * 64)
    _, defects = validator.check(fresh_rows(tmp_path), manifest)
    assert any("the ladder moved" in defect for defect in defects)


def test_rebuilding_a_pack_that_carries_ticks_is_refused(tmp_path):
    """`data/annotation/**` is gitignored for everything except this pack, and --force takes an
    evening with it. The same footgun build_audit_pack and build_micro_pack carry."""
    rows = fresh_rows(tmp_path)
    rows[0]["brand"] = "y"
    target = tmp_path / "ticked.csv"
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=pack.COLUMNS, delimiter=pack.DELIMITER, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    assert pack.filled(target) == 1
    with pytest.raises(SystemExit, match="already carries ticks"):
        pack.main(["--pack", str(target), "--manifest", str(tmp_path / "m.json")])
    # and --force goes through, which is what makes the refusal above the only thing standing
    # between a rebuild and an evening of adjudication
    assert (
        pack.main(["--pack", str(target), "--manifest", str(tmp_path / "m.json"), "--force"]) == 0
    )
    assert pack.filled(target) == 0


def test_the_pack_rebuilds_to_the_same_thirty_questions(tmp_path):
    """The GIVEN columns, not the bytes: a rebuild reproduces the draw and its text forever, while a
    byte-comparison against the shipped file stops holding the moment a tick is entered."""
    out, manifest_path = tmp_path / "text30.csv", tmp_path / "m.json"
    assert pack.main(["--pack", str(out), "--manifest", str(manifest_path)]) == 0
    rebuilt = validator.read_pack(out)
    shipped = validator.read_pack(pack.PACK)
    assert pack.given_sha256(rebuilt) == pack.given_sha256(shipped)
    assert [row["id"] for row in rebuilt] == [row["id"] for row in shipped]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["given_sha256"] == json.loads(pack.MANIFEST.read_text("utf-8"))["given_sha256"]
