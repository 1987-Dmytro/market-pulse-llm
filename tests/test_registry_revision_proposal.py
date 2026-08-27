"""Offline tests for C1's registry-revision proposal — no Telegram, no session."""

import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import registry_revision_proposal as proposal  # noqa: E402


class FakeSource:
    def __init__(self, **kw):
        self.id = kw.get("id", "x")
        self.name = kw.get("name", "X")
        self.source_type = kw.get("source_type", "community")
        self.audience = kw.get("audience", "mothers_kids")
        self.comments_enabled = kw.get("comments_enabled", False)
        self.watch = kw.get("watch", False)


def post(day: str, collected: str) -> dict:
    return {
        "date": f"{day}T09:00:00+00:00",
        "provenance": {"collected_at": f"{collected}T10:00:00+00:00"},
    }


# --- the three lists are SPEC v2 §3's own division ---------------------------------------------


def test_a_is_the_retail_source_types_plus_the_names_spec_v2_adds():
    """§3 counts 9 «сейчас», which is exactly the two retail source_types.

    «Копійочка» is registered `community`/`supermarket_deals` and §3 lists it among the promo
    aggregators, so the tenth row is placed BY NAME and the row says so. A classifier that
    silently disagreed with the section it implements would be the alternative.
    """
    assert proposal.bucket(FakeSource(source_type="official_retail")) == "A"
    assert proposal.bucket(FakeSource(source_type="aggregator")) == "A"
    assert proposal.bucket(FakeSource(id="kopiyochka1", audience="supermarket_deals")) == "A"
    assert proposal.SPEC_V2_AGGREGATORS == {"kopiyochka1"}


def test_marketopt_is_retail_not_regional_which_is_why_b_is_17_and_not_18():
    """§3's prose calls 18 channels regional; its own chain list names Маркетопт in category A."""
    marketopt = FakeSource(id="marketopt_promo", source_type="official_retail", audience="regional")
    assert proposal.bucket(marketopt) == "A"
    assert proposal.bucket(FakeSource(audience="regional")) == "B"


def test_everything_else_is_paused():
    for audience in ("mothers_kids", "health_fitness", "cooking_recipes", "baby_food"):
        assert proposal.bucket(FakeSource(audience=audience)) == "PAUSED"


# --- the window is the store's instrument, not today's -----------------------------------------


def test_the_window_is_anchored_on_the_collection_date_not_the_last_post():
    """A channel quiet for a fortnight before the collector reached it was still READ.

    Anchoring on its last post would divide its posts by the span between them and call the
    result a rate: two posts a fortnight apart would read 1.0/day.
    """
    rows = [post("2026-07-12", "2026-08-08"), post("2026-07-26", "2026-08-08")]
    assert proposal.window_of(rows) == (date(2026, 7, 12), date(2026, 8, 8))
    assert len(proposal.in_window(rows, proposal.window_of(rows))) == 2


def test_a_post_older_than_the_window_is_out_of_the_rate():
    rows = [post("2026-07-10", "2026-08-07")]
    window = proposal.window_of(rows)
    assert window == (date(2026, 7, 11), date(2026, 8, 7))
    assert proposal.in_window(rows, window) == [], "the only post predates the collected window"


def test_the_denominator_is_the_stores_own_28_days():
    assert proposal.WINDOW_DAYS == 28


# --- a missing comment rate is not a zero ------------------------------------------------------


def test_comments_disabled_reads_as_a_cause_and_never_as_zero():
    rate, cause = proposal.comment_rate(
        FakeSource(comments_enabled=False), "@a", "no-such-file", None, set()
    )
    assert rate is None and cause == "comments_disabled"


def test_a_group_never_joined_is_told_apart_from_one_that_produced_nothing():
    """Both would be `0.0`, and they are two different operator decisions."""
    open_source = FakeSource(comments_enabled=True)
    _, never = proposal.comment_rate(open_source, "@a", "no-such-file", None, set())
    _, joined = proposal.comment_rate(open_source, "@a", "no-such-file", None, {"@a"})
    assert never == "group_never_joined"
    assert joined == "joined_no_comments_collected"
    assert set(proposal.COMMENT_CAUSES) == {never, joined, "measured", "comments_disabled"}


# --- the table cannot be broken by the data ----------------------------------------------------


def test_a_pipe_in_a_channel_name_is_escaped():
    """«Полтава ІНФО | Новини Світло» is a registered name; unescaped it shifts every column."""
    assert proposal.md("Полтава ІНФО | Новини Світло") == r"Полтава ІНФО \| Новини Світло"
