"""The aggregates the sitting's rows wear — re-derived, not trusted.

The load-bearing test is the first one: the committed record is REGENERATED from `data/derived/`
and compared byte for byte. It is the determinism pair and the re-derivation gate at once, and it
is why nothing downstream of this record may carry a hand-typed number — every one of them comes
back from the evidence or the test goes red.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import window_summary_5c2 as summary  # noqa: E402

from market_pulse import loop, prompts  # noqa: E402

RECORD = REPO_ROOT / "results" / "window_summary_5c2.json"

SEALING_COMMIT = "d69c812b206faff15f5a12adff113a5ef1335154"
"""The commit that carries the bytes this record — and `results/validate_5c2_pack.json` — name.

Written out in full and not as `d69c812`: an abbreviation is valid until the day a seventh hex digit
collides, and on that day this test errors for a reason nobody would connect to a sealed summary.
`tests/test_prereg_5c2.py` is the precedent, one contract old.

The cycle-2 prep landed SPEC 3.19 (1)'s queue rule and moved two files this record pins — the
producer itself and `src/market_pulse/loop.py`, whose `has_text` the producer now calls instead of
its own inline `not text.strip()`. **Neither record is re-pinned**: a sealed artifact is never
rewritten to make a test green, and the 5 075 rows it describes did not move — the amendment's own
(3) says nothing is re-scored. What keeps `producer.sha256` a checkable claim rather than a dead
literal is that the bytes are RECOVERABLE:

    git show d69c812:scripts/window_summary_5c2.py
    git show d69c812:src/market_pulse/loop.py
"""

MOVED_BY_THE_SKIP = ("scripts/window_summary_5c2.py", "src/market_pulse/loop.py")
"""The two pinned files SPEC 3.19 (1)'s skip rule moved. Everything else this record names is
hashed LIVE, and the day a third file joins this tuple is a day to look at it rather than relax it.
"""

MOVED_BY_R1 = ("src/market_pulse/brands.py",)
"""The one pinned file SPEC 3.21 (1) moved — and it is a SECOND tuple rather than a third entry in
the first, because the two amendments are checked by different witnesses and a shared branch would
assert 3.19's about a file that never met it (`an_invariant_the_new_member_cannot_satisfy`).

3.21 (1) makes the watchlist's text rules law in `config/watchlist_rules.yaml` and teaches the
matcher to read them. The rules are OPT-IN — `find_watchlist_brands` without them matches what it
matched when this record was sealed — so the record's brand attribution does not move and is not
re-pinned. What moved is the module's bytes, and they stay RECOVERABLE:

    git show d69c812:src/market_pulse/brands.py
"""

MOVED = MOVED_BY_THE_SKIP + MOVED_BY_R1

WITNESS = {
    **dict.fromkeys(MOVED_BY_THE_SKIP, "has_text"),
    **dict.fromkeys(MOVED_BY_R1, "watchlist_rules"),
}
"""What each moved file learned, by amendment. The token is read BOTH ways below — absent from the
sealed blob, present on disk — so a recovery from the wrong commit is a failure rather than a pass.
"""


def sealed_blob(path: str) -> bytes:
    """`path` as :data:`SEALING_COMMIT` carried it — git, and nothing on disk."""
    return subprocess.run(
        ["git", "show", f"{SEALING_COMMIT}:{path}"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=True,
    ).stdout


def sealed_sha256(path: str) -> str:
    return hashlib.sha256(sealed_blob(path)).hexdigest()


@pytest.fixture(scope="module")
def record() -> dict:
    return json.loads(RECORD.read_text(encoding="utf-8"))


def test_the_committed_record_is_what_the_producer_writes_today(tmp_path):
    """Byte-identical, so the record IS the determinism pair and every number re-derives.

    No clock and no git block is what makes this possible; `scripts/build_sitting_pack.py` writes
    a `git_state()` and could not have this test.

    Since SPEC 3.19 (1) some of the shas in `producer` are the only bytes allowed to differ, and
    each one is put back to what :data:`SEALING_COMMIT` carries before the comparison — so the claim
    is still "every byte of this record re-derives", with those digests answered by `git show`
    instead of by the disk. Each substitution must FIRE (`count == 1`): a swap that matched nothing
    would leave the comparison passing for a file that had silently gone back to the sealed bytes.

    3.21 (1) put a third file in that list and NOT a third number in the record: the matcher's rules
    are opt-in, this producer does not ask for them, and every brand count below is the one the
    sitting was shown. That is what the byte comparison after the swaps proves.
    """
    out = tmp_path / "again.json"
    assert summary.main(["--out", str(out)]) == 0

    produced = out.read_bytes()
    for path in MOVED:
        live, sealed = summary.sha256_of(REPO_ROOT / path), sealed_sha256(path)
        assert live != sealed, f"{path} never learned {WITNESS[path]}"
        assert produced.count(live.encode()) == 1, path
        produced = produced.replace(live.encode(), sealed.encode())

    assert produced == RECORD.read_bytes()


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
    of them is. The walk is over the WHOLE record and not over the blocks today's producer writes:
    a future field that leaked a price would pass a check aimed at this shape, which is the defect
    an earlier version of this test had.

    What it enforces: every `price_old` key in the record is a COUNT (an int), and no float in the
    record is one of the 95 old prices the evidence carries. The second half is what a count-shaped
    check cannot do — a leak under any other key name is still a leak.
    """
    leaked = [
        (path, value)
        for path, value in _walk(record)
        if path.endswith("price_old") and not isinstance(value, int)
    ]
    assert not leaked, f"price_old is a count in this record and these are not: {leaked}"

    prices = {
        row["position"]["price_old"]
        for path in summary.leg_files(summary.DERIVED, loop.POSITION_RECORD_TYPE)
        for row in summary.read_rows(path)
        if row["position"]["price_old"] is not None
    }
    assert prices, "the fixture is only meaningful while some row carries an old price"
    values = {value for _, value in _walk(record) if isinstance(value, float)}
    assert not (values & prices), f"an old price reached the record as a value: {values & prices}"

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


def _walk(node, path: str = ""):
    """Every (dotted path, leaf) in the record — the whole thing, not the blocks it happens to have."""
    if isinstance(node, dict):
        for key, value in node.items():
            yield from _walk(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _walk(value, f"{path}[{index}]")
    else:
        yield path, node


def test_the_whole_record_walk_would_see_a_leak():
    """The control: the walk above is only worth anything if it can go red."""
    leaked = [
        (path, value)
        for path, value in _walk({"position_row": {"sample": {"price_old": 264.5}}})
        if path.endswith("price_old") and not isinstance(value, int)
    ]

    assert leaked == [(".position_row.sample.price_old", 264.5)]


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
    """A summary that cannot say which bytes it read is a claim, not evidence.

    The files SPEC 3.19 (1) and 3.21 (1) moved are checked BOTH ways, because either leg alone
    passes for the wrong reason: a live hash equal to the pin would mean the amendment never landed,
    and the recovered hash equal to the pin is what proves the record names the bytes that wrote it.
    The recovered blobs are read for the new name too — a recovery that already carried the witness
    would mean this is checking the wrong commit.

    The witness is per amendment (:data:`WITNESS`) and not one shared token: `brands.py` never
    learned `has_text` and never will, so a single branch would have failed it for a reason that has
    nothing to do with its pin.
    """
    assert record["producer"]["sha256"] == sealed_sha256(record["producer"]["script"])
    assert set(record["producer"]["borrowed"]) == set(summary.BORROWED)
    for name, digest in record["producer"]["borrowed"].items():
        if name in MOVED:
            witness = WITNESS[name]
            assert summary.sha256_of(REPO_ROOT / name) != digest, f"{name} never learned {witness}"
            assert sealed_sha256(name) == digest
            assert witness.encode() not in sealed_blob(name), f"{name}: wrong commit recovered"
            assert witness in (REPO_ROOT / name).read_text(encoding="utf-8")
        else:
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
