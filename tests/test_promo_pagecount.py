"""The exact page count — offline tests of the four things that could make it wrong.

The number C2 is priced on is 3 008, and every way it could be wrong is a way to buy the wrong
population: counting a video as a page, folding an album onto the wrong id, letting a post that has
been deleted since the census froze fall to zero pages, or re-deriving the window instead of
reading the pinned ids.
"""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import promo_pagecount_c2 as pc  # noqa: E402


def message(msg_id, *, grouped_id=None, kind="photo"):
    """A Telethon message as `page_kind` reads one: `media` set, plus the kind's own accessor."""
    fields = {"photo": None, "video": None, "poll": None, "document": None}
    if kind != "none":
        fields[kind] = object()
    return SimpleNamespace(
        id=msg_id, grouped_id=grouped_id, media=None if kind == "none" else 1, **fields
    )


# --- a page is a photo ---------------------------------------------------------------------------


def test_only_a_photo_is_a_page():
    """`post_record` stores `has_media = message.media is not None`, which is true of a video, a
    poll and a PDF alike. The census's 968 media posts are counted through that bool; the paid leg
    is billed per image. The corpus has 146 videos and 3 polls in the window, so a count that
    inherited the bool would buy 149 pages that carry no leaflet."""
    assert pc.page_kind(message(1, kind="photo")) == "photo"
    assert pc.page_kind(message(2, kind="video")) == "video"
    assert pc.page_kind(message(3, kind="poll")) == "poll"
    assert pc.page_kind(message(4, kind="document")) == "document"
    assert pc.page_kind(message(5, kind="none")) == "none"


def test_an_album_of_photos_and_one_video_counts_only_the_photos():
    folded = pc.fold(
        [
            message(10, grouped_id=77),
            message(11, grouped_id=77),
            message(12, grouped_id=77, kind="video"),
        ]
    )
    assert folded[10]["pages"] == 2
    assert folded[10]["kinds"] == {"photo": 2, "video": 1}


# --- the fold's join key -------------------------------------------------------------------------


def test_an_album_folds_onto_its_lowest_id_because_that_is_what_the_store_kept():
    """`RawStore.collapse_albums` sets `album["msg_id"] = min(...)`, so the census's pinned id IS
    the album's lowest. Fold onto any other member and every album row misses its pin, is counted
    `unreachable`, and the exact count silently becomes the gap bound."""
    folded = pc.fold(
        [message(31, grouped_id=5), message(29, grouped_id=5), message(30, grouped_id=5)]
    )
    assert list(folded) == [29]
    assert folded[29]["pages"] == 3


def test_two_ungrouped_photos_are_two_posts_not_one_album():
    folded = pc.fold([message(41), message(42)])
    assert sorted(folded) == [41, 42]
    assert all(row["pages"] == 1 for row in folded.values())


# --- a deleted post is a third state, not zero ---------------------------------------------------


def test_a_pinned_post_the_reread_did_not_see_is_priced_at_the_bound_never_at_zero():
    """The census froze on 31.08 and the re-read runs later, so a pinned post can have been
    deleted. Falling to 0 would understate C2 and the overrun would surface after the money was
    spent ([[the_empty_row_is_the_answer]])."""
    row = {"channel": "@x", "source_id": "x", "pinned": [100, 200], "bound": {100: 1, 200: 6}}
    priced = pc.price(row, {100: {"msg_id": 100, "pages": 4, "kinds": {"photo": 4}}})
    assert priced["rows_exact"] == 1 and priced["rows_unreachable"] == 1
    assert priced["unreachable_msg_ids"] == ["200"]
    assert priced["pages_exact"] == 4
    assert priced["pages_unreachable_bound"] == 6
    assert priced["pages"] == 10


def test_every_row_reached_leaves_the_bound_out_of_the_number():
    """The other direction: with nothing unreachable the total is the count and no bound leaks
    into it — which is the state the shipped record is in, and the assertion that says so."""
    row = {"channel": "@x", "source_id": "x", "pinned": [100], "bound": {100: 9}}
    priced = pc.price(row, {100: {"msg_id": 100, "pages": 4, "kinds": {"photo": 4}}})
    assert priced["pages"] == 4 and priced["pages_unreachable_bound"] == 0
    assert priced["pages_store_upper_bound"] == 9


# --- the store's bound can only over-count -------------------------------------------------------


def test_the_gap_bound_is_the_distance_to_the_next_stored_id_and_never_below_one():
    assert pc.gap_bound([10, 14, 20], 10) == 4
    assert pc.gap_bound([10, 11], 10) == 1
    assert pc.gap_bound([10], 10) == 1, "the newest post has no next id and is worth one page"


# --- the shipped record --------------------------------------------------------------------------


def test_the_shipped_count_is_over_the_census_s_pinned_population_and_holds_its_bound():
    """The population must be the census's pinned ids, not a window re-evaluated now: a re-derived
    `since <= date < anchor` would pick up everything published after the census froze and widen
    what C2 pays for, against SPEC 3.18 (4). And the counted total has to sit inside the two bounds
    that were derived without Telegram — under the store's gap bound, which can only over-count,
    and inside the census's own floor..ceiling."""
    record = json.loads((REPO_ROOT / "results" / "promo_pagecount_c2.json").read_text("utf-8"))
    census = json.loads((REPO_ROOT / "results" / "promo_census_c2.json").read_text("utf-8"))
    assert record["selection"]["ids_sha256"] == census["selection"]["ids_sha256"]
    leaflet = census["selection"]["leaflet_page"]
    totals = record["totals"]
    assert totals["pinned_media_posts"] == leaflet["posts"]
    assert totals["rows_exact"] + totals["rows_unreachable"] == leaflet["posts"]
    assert totals["pages"] <= totals["pages_store_upper_bound"]
    assert leaflet["pages_floor"] <= totals["pages"] <= leaflet["pages_ceiling"]
    assert "document" not in totals["kinds"], (
        "no leaflet page in this corpus was sent as an uncompressed file, which is what makes the"
        " photo-only rule safe here — if that ever stops being true the rule has to be revisited"
    )
