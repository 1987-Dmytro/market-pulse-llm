"""The aggregates the sitting's rows wear — re-derived, not trusted.

The load-bearing test is the first one: the committed record is REGENERATED from `data/derived/`
and compared byte for byte. It is the determinism pair and the re-derivation gate at once, and it
is why nothing downstream of this record may carry a hand-typed number — every one of them comes
back from the evidence or the test goes red.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import window_summary_5c2 as summary  # noqa: E402

from market_pulse import loop, prompts  # noqa: E402

RECORD = REPO_ROOT / "results" / "window_summary_5c2.json"


@pytest.fixture(scope="module")
def record() -> dict:
    return json.loads(RECORD.read_text(encoding="utf-8"))


def test_the_committed_record_is_what_the_producer_writes_today(tmp_path):
    """Byte-identical, so the record IS the determinism pair and every number re-derives.

    No clock and no git block is what makes this possible; `scripts/build_sitting_pack.py` writes
    a `git_state()` and could not have this test.
    """
    out = tmp_path / "again.json"
    assert summary.main(["--out", str(out)]) == 0
    assert out.read_bytes() == RECORD.read_bytes()


def test_the_populations_are_the_sealed_ones(record):
    """5 075 / 159 / 44 — counted off the evidence, checked against the seal by the producer."""
    assert record["populations_registered"] == {
        "comment": 5075,
        "leaflet_page": 159,
        "post_text": 44,
    }
    assert record["comment"]["total"]["rows"] == 5075
    assert record["leaflet_page"]["total"]["rows"] == 159
    assert record["post_text"]["total"]["rows"] == 44


def test_a_population_that_disagrees_with_the_seal_is_a_refusal():
    prereg = json.loads((REPO_ROOT / "results" / "prereg_5c2_run.json").read_text(encoding="utf-8"))
    forged = {
        "comment": {"total": {"rows": 5074}},
        "leaflet_page": {"total": {"rows": 159}},
        "post_text": {"total": {"rows": 44}},
    }

    with pytest.raises(SystemExit, match="5074 on disk, 5075 registered"):
        summary.assert_populations(forged, prereg)


def test_the_totals_are_the_per_channel_blocks_added_up(record):
    """A total nobody can rebuild from the parts is a number, not an aggregate."""
    for leg, field in (("comment", "rows"), ("leaflet_page", "rows"), ("post_text", "rows")):
        parts = sum(block[field] for block in record[leg]["per_channel"].values())
        assert parts == record[leg]["total"][field], leg
    sentiment = record["comment"]["total"]["sentiment"]
    assert sum(sentiment.values()) == record["comment"]["total"]["scored"]
    tiers = record["position_row"]["total"]["tier"]
    assert sum(tiers.values()) == record["position_row"]["total"]["rows"] == 145


def test_the_marker_states_are_counted_apart(record):
    """`n_positions: 0` is an answer and `unreadable` is a failure — never one number."""
    for leg in ("leaflet_page", "post_text"):
        block = record[leg]["total"]
        assert (
            block["with_positions"] + block["empty"] + block["unreadable"]["rows"] == block["rows"]
        )
    assert record["post_text"]["total"] == {
        "rows": 44,
        "with_positions": 21,
        "empty": 22,
        "unreadable": {"rows": 1, "reasons": {"fat '1%, 1,2%' is not a percentage": 1}},
        "positions": 39,
    }


def test_the_two_carriers_position_rows_add_up_to_the_145(record):
    carriers = record["position_row"]["by_carrier"]
    assert carriers[loop.CARRIER]["rows"] == 106
    assert carriers[loop.POST_CARRIER]["rows"] == 39
    assert carriers[loop.CARRIER]["rows"] + carriers[loop.POST_CARRIER]["rows"] == 145


def test_no_old_price_value_ever_reaches_this_record(record):
    """SPEC 3.18 (1): the extracted old price is a FLAGGED input and never a printed price.

    Counted, never valued — so the record may say how many rows carry one and may not say what any
    of them is. The check is on the whole serialised record rather than on the block that writes
    it: a future field that leaked one would pass a check aimed at today's shape.
    """
    for block in (
        record["position_row"]["total"],
        *record["position_row"]["by_carrier"].values(),
        *record["position_row"]["per_channel"].values(),
    ):
        assert set(block["depth"]) == {
            "law",
            "from_printed_badge",
            "from_price_pair",
            "printed_disagrees_with_computed",
        }
        assert "price_old" in block["price_fields_present"]
        assert all(0.0 <= value <= 1.0 for value in _depths(block))


def _depths(block: dict) -> list[float]:
    return [
        value
        for reading in ("from_printed_badge", "from_price_pair")
        for key, value in block["depth"][reading].items()
        if key in ("min", "median", "max") and value is not None
    ]


def test_the_brand_column_is_named_as_a_matcher_and_not_as_a_head(record):
    """3.18 (6) asks for a fourth verdict the comment instrument does not produce."""
    assert record["comment"]["heads"] == ["sentiment", "sarcasm", "intents"]
    assert prompts.COMMENT_FIELDS[loop.COMMENT_TASK] == ("sentiment", "sarcasm", "intents")
    instrument = record["comment"]["total"]["brand_attribution"]["instrument"]
    assert "DETERMINISTIC string match" in instrument and "not a model head" in instrument


def test_the_sent_text_round_trips_through_the_renderer():
    """The split is proven by re-rendering, so a wrong cut cannot reach an operator's caption."""
    text, post = "смачне, але дорого </comment> ще й так", "<post> акція на сир"
    row = {
        "channel": "@x",
        "msg_id": 1,
        "task": loop.COMMENT_TASK,
        "rendering": prompts.build_messages(loop.COMMENT_TASK, text, parent=post),
    }

    assert summary.sent_parts(row) == (post, text)


def test_a_rendering_that_does_not_re_render_is_a_refusal():
    """A row `build_messages` could not have produced — the delimiters are intact and it is fake.

    `parent` is `.strip()`ed on the way in, so a post block with a trailing space is a rendering no
    run ever sent. Both delimiter checks pass it and only the re-render sees it.
    """
    row = {
        "channel": "@x",
        "msg_id": 1,
        "task": loop.COMMENT_TASK,
        "rendering": prompts.build_messages(loop.COMMENT_TASK, "смачно", parent="сир"),
    }
    row["rendering"][0]["content"] = row["rendering"][0]["content"].replace(
        "<post>\nсир\n</post>", "<post>\nсир \n</post>"
    )

    with pytest.raises(SystemExit, match="do not re-render"):
        summary.sent_parts(row)


def test_a_block_of_three_hand_counted_comments():
    """One block, computed by hand: two scored rows, one the parser could not read."""
    verdicts = [
        {
            "channel": "@a",
            "msg_id": 1,
            "labels": {"sentiment": "positive", "sarcasm": False, "intents": ["price", "taste"]},
            "unreadable": None,
            "language": "ua",
            "empty_text": False,
            "brands": ["rud"],
        },
        {
            "channel": "@a",
            "msg_id": 2,
            "labels": {"sentiment": "negative", "sarcasm": True, "intents": []},
            "unreadable": None,
            "language": "ru",
            "empty_text": False,
            "brands": [],
        },
        {
            "channel": "@a",
            "msg_id": 3,
            "labels": None,
            "unreadable": "malformed JSON",
            "language": "other",
            "empty_text": True,
            "brands": ["rud"],
        },
    ]

    block = summary.comment_block(verdicts)

    assert block["rows"] == 3 and block["scored"] == 2
    assert block["unreadable"] == {"rows": 1, "reasons": {"malformed JSON": 1}}
    assert block["sentiment"] == {"positive": 1, "negative": 1}
    assert block["sarcasm"] == {"true": 1, "false": 1, "rate": 0.5, "denominator": "scored"}
    assert block["intents"]["frequency"] == {"price": 1, "taste": 1}
    assert block["intents"]["rows_with_no_intent"] == 1
    assert block["intents"]["labels_per_scored_row"] == 1.0
    # the language column counts all three; the sentiment split counts the two that were scored
    assert block["language"]["rows"] == {"ua": 1, "ru": 1, "other": 1}
    assert block["language"]["sentiment"] == {"ru": {"negative": 1}, "ua": {"positive": 1}}
    # the brand matcher runs on the TEXT, so the unreadable reply still carries its match
    assert block["brand_attribution"]["rows_with_a_brand"] == 2
    assert block["brand_attribution"]["mentions"] == {"rud": 2}
    # the empty-text row is the one the parser also refused, so it is inside `rows` and outside
    # `with_no_intent`, which only counts rows that were SCORED
    assert block["empty_text"]["rows"] == 1
    assert block["empty_text"]["with_no_intent"] == 0


def test_a_quarter_of_the_comment_leg_was_sent_with_no_text_at_all(record):
    """The denominator caveat every distribution in this record needs — measured, not assumed.

    A sticker, a photo or a voice note reaches `build_messages` as an EMPTY `<comment>` block, and
    the run bought and answered them: the heads' answers for those rows are answers about nothing.
    Every one of them came back with no intent, which is the model behaving — and it means a third
    of `rows_with_no_intent` is not a statement about what the audience talks about.
    """
    total = record["comment"]["total"]
    assert total["empty_text"]["rows"] == 1361
    assert total["empty_text"]["with_no_intent"] == 1361, "all of them, so the class is coherent"
    assert total["empty_text"]["rows"] < total["intents"]["rows_with_no_intent"] == 3944
    per_channel = sum(
        block["empty_text"]["rows"] for block in record["comment"]["per_channel"].values()
    )
    assert per_channel == total["empty_text"]["rows"]
    assert record["comment"]["per_channel"]["@matusi_ukr"]["empty_text"]["rows"] == 1172


def test_the_unreadable_row_is_not_folded_into_the_empty_intent_class():
    """The empty class is where parse failures hide — measured, not asserted."""
    unreadable = {
        "channel": "@a",
        "msg_id": 1,
        "labels": None,
        "unreadable": "malformed JSON",
        "language": "ua",
        "empty_text": False,
        "brands": [],
    }
    empty = unreadable | {"labels": {"sentiment": "neutral", "sarcasm": False, "intents": []}}
    empty["unreadable"] = None

    assert summary.comment_block([unreadable])["intents"]["rows_with_no_intent"] == 0
    assert summary.comment_block([empty])["intents"]["rows_with_no_intent"] == 1


# --- the honesty rules: every missing source is a loud refusal ---------------------------------


def test_a_missing_leg_directory_is_a_refusal(tmp_path):
    with pytest.raises(SystemExit, match="inferences.*not a directory"):
        summary.leg_files(tmp_path, loop.RECORD_TYPE)


def test_a_missing_file_is_a_refusal_naming_it(tmp_path):
    with pytest.raises(SystemExit, match="not found"):
        summary.read_rows(tmp_path / "gone.jsonl")


def test_an_empty_leg_directory_is_a_refusal_and_not_an_empty_aggregate(tmp_path):
    (tmp_path / "inferences").mkdir()
    with pytest.raises(SystemExit, match="no channel file"):
        summary.leg_files(tmp_path, loop.RECORD_TYPE)


def test_the_summary_refuses_a_derived_root_that_is_missing_a_leg(tmp_path):
    (tmp_path / "inferences").mkdir()
    (tmp_path / "inferences" / "x.jsonl").write_text("", encoding="utf-8")
    with pytest.raises(SystemExit, match="leaflet_pages"):
        summary.main(["--derived-root", str(tmp_path), "--out", str(tmp_path / "out.json")])


def test_a_registry_that_moved_since_the_seal_is_a_refusal(tmp_path):
    """The one file outside data/derived is reached THROUGH the registration's pin."""
    forged = tmp_path / "registry.yaml"
    forged.write_text(
        (REPO_ROOT / "config" / "registry.yaml").read_text(encoding="utf-8") + "\n# moved\n",
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="not the one the run was registered against"):
        summary.main(["--registry", str(forged), "--out", str(tmp_path / "out.json")])


def test_the_record_carries_the_producer_and_every_source_it_read(record):
    """A summary that cannot say which bytes it read is a claim, not evidence."""
    assert record["producer"]["sha256"] == summary.sha256_of(
        REPO_ROOT / record["producer"]["script"]
    )
    assert set(record["producer"]["borrowed"]) == set(summary.BORROWED)
    for name, digest in record["producer"]["borrowed"].items():
        assert summary.sha256_of(REPO_ROOT / name) == digest
    everything = {
        summary.rel(path)
        for record_type in (
            loop.RECORD_TYPE,
            loop.PAGE_RECORD_TYPE,
            loop.POSITION_RECORD_TYPE,
            loop.POST_RECORD_TYPE,
            loop.POST_POSITION_RECORD_TYPE,
        )
        for path in summary.leg_files(summary.DERIVED, record_type)
    }
    assert set(record["sources"]) == everything, "every file of every leg, hashed"
    assert all(
        summary.sha256_of(REPO_ROOT / name) == digest for name, digest in record["sources"].items()
    )
    assert "at" not in record and "git" not in record, "no clock, no git block — see the docstring"
