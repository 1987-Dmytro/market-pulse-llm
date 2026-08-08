"""Offline tests for the image census — no Telegram, no spend, no store writes.

The census exists to price a purchase, so its risk is not that a count is off by one: it is that
the count silently measures a different population than the record the operator is reading. Two
things are therefore pinned here — that the census agrees with the signed yield screen about which
posts are readable, and that the caption file it loads can actually change an answer. The second
matters because the shipped census reports zero captioned posts, and "loaded and empty" looks
exactly like "never loaded" in a record.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

import image_census_5c1 as census  # noqa: E402

from market_pulse import parents  # noqa: E402

RECORD = json.loads((REPO_ROOT / "results" / "image_census_5c1.json").read_text("utf-8"))
SCREEN = json.loads((REPO_ROOT / "results" / "yield_screen_5c1.json").read_text("utf-8"))


# --- the state vocabulary is not this file's ------------------------------------------------------


def test_the_four_states_are_the_ones_the_shared_rule_can_return():
    """`parents.context` decides what stands in for a post's missing text for every labelling pass
    in the repo. A census with its own vocabulary would be a second opinion about the corpus."""
    assert set(census.STATES) == {"post_text", *parents.STATE_OF.values(), "no_text_and_no_caption"}
    assert set(RECORD["totals"]) == {*census.STATES, "posts_in_window"}


def test_a_caption_inside_a_window_moves_a_post_out_of_the_unreadable_class(tmp_path):
    """The control for the shipped zero: the caption file is read, and a row in it counts.

    Without this, `image_caption: 0` proves nothing — passing an empty dict would produce the
    identical record. @atb_market_official 4519 is one of the 19 silent posts of the window the
    pilot is about, so the fixture is a real row of the real population.
    """
    caps = tmp_path / "captions.jsonl"
    caps.write_text(
        json.dumps(
            {
                "channel": "@atb_market_official",
                "msg_id": 4519,
                "kind": "image",
                "caption": "Акційна листівка АТБ: молочна полиця, ціни тижня.",
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    out = tmp_path / "census.json"
    assert census.main(["--out", str(out), "--captions", str(caps)]) == 0
    record = json.loads(out.read_text(encoding="utf-8"))
    atb = next(row for row in record["sources"] if row["handle"] == "@atb_market_official")

    assert atb["states"]["image_caption"] == 1
    assert atb["states"]["no_text_and_no_caption"] == 18
    assert 4519 not in atb["uncaptioned_msg_ids"]
    # And the reconciliation still holds: a caption changes what a reader has, never what the
    # store contains. The screen counts 19 posts without text of their own either way.
    assert atb["posts_in_window"] == 25 and atb["states"]["post_text"] == 6


def test_the_census_refuses_when_it_disagrees_with_the_signed_screen(tmp_path, monkeypatch):
    """The negative control on the reconciliation. A census that quietly diverged from the record
    the operator signed against would price a population nobody has seen."""
    doctored = json.loads(json.dumps(SCREEN))
    doctored["sources"][0]["posts"]["with_text"] += 1
    path = tmp_path / "screen.json"
    path.write_text(json.dumps(doctored, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(census, "YIELD_RECORD", path)
    with pytest.raises(SystemExit, match="does not read the same window as the screen"):
        census.main(["--out", str(tmp_path / "census.json")])


def test_the_census_will_not_overwrite_its_own_dated_record():
    """D68, the refusal the screen and the market screen carry: a later pass over moved windows
    must not be able to land under the name the price was quoted from."""
    with pytest.raises(SystemExit, match="already exists"):
        census.main([])


# --- the shipped record ---------------------------------------------------------------------------


def test_the_shipped_census_covers_the_same_66_channels_as_the_screen():
    assert {row["handle"] for row in RECORD["sources"]} == {
        row["handle"] for row in SCREEN["sources"]
    }
    assert len(RECORD["sources"]) == 66
    for row in RECORD["sources"]:
        other = next(r for r in SCREEN["sources"] if r["handle"] == row["handle"])
        assert row["posts_in_window"] == other["posts"]["in_window"], row["handle"]
        assert row["states"]["post_text"] == other["posts"]["with_text"], row["handle"]


def test_the_shipped_census_carries_the_nineteen_posts_the_pilot_is_for():
    """The pilot's population is named by id, not by count — the fetch reads these ids."""
    atb = next(row for row in RECORD["sources"] if row["handle"] == "@atb_market_official")
    assert atb["states"]["no_text_and_no_caption"] == 19
    assert atb["uncaptioned_with_media"] == 19
    assert len(atb["uncaptioned_msg_ids"]) == 19
    assert atb["uncaptioned_msg_ids"] == sorted(set(atb["uncaptioned_msg_ids"]))


def test_the_projection_is_the_45g2_rate_times_the_population_and_says_so():
    """The number the operator's full-run decision reads. It must be re-derivable from the record
    it cites, and it must not be one number: offline nothing here can tell a poll from a photo."""
    rate = json.loads((REPO_ROOT / "results" / "captions_45g2.json").read_text("utf-8"))["runs"][0]
    projected = RECORD["projection"]
    assert projected["rate"]["source"] == "results/captions_45g2.json"
    assert projected["rate"]["model"] == rate["model"]
    assert projected["rate"]["usd_per_post"] == round(
        rate["cost"]["usd"] / rate["cost"]["requests"], 8
    )
    targets = sum(row["uncaptioned_with_media"] for row in RECORD["sources"])
    assert projected["captionable_posts_upper_bound"] == targets
    assert projected["usd_upper_bound"] == round(targets * projected["rate"]["usd_per_post"], 4)
    # The discounted reading is strictly smaller and is labelled as an expectation, not a price.
    assert 0 < projected["usd_expected"] < projected["usd_upper_bound"]
    assert projected["expected_image_share"] == round(21 / 41, 3)


def test_the_zero_caption_states_are_explained_rather_than_left_to_read_as_a_bug():
    """`image_caption: 0` with a 37-row caption file loaded is a claim that needs its reason in
    the record: those rows are dated before every window censused here."""
    assert RECORD["captions_read"]["rows"] == 37
    assert RECORD["captions_read"]["rows_inside_a_censused_window"] == 0
    assert RECORD["totals"]["image_caption"] == RECORD["totals"]["poll_text"] == 0
    assert "dated 2025-06-17" in RECORD["captions_read"]["note"]
