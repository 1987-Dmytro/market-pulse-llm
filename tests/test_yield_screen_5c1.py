"""Offline tests for the yield screen — no Telegram, no store writes.

The screen's risk is the same one every keyword instrument has: it can be too loose (a news feed
"yields dairy" because a minister is called Маслов) or too tight (a channel full of «Гармонію»
reads as empty). It cannot be tuned away here — the lexicon says `draft-not-law` and the watchlist
is the operator's — so what is guarded is that the looseness is VISIBLE: every count breaks down
to the term that made it, and every term carries a line.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

import yield_screen_5c1 as screen  # noqa: E402

from market_pulse import yield_screen as core  # noqa: E402
from market_pulse.brands import find_watchlist_brands, watchlist_aliases  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

REGISTRY = load_registry(REPO_ROOT / "config" / "registry.yaml")
LEXICON = json.loads((REPO_ROOT / "data" / "category_lexicon_draft.json").read_text("utf-8"))
ALIAS_TABLE = watchlist_aliases(REGISTRY.watchlist)
CATS = core.compile_categories(LEXICON)
ALIASES = core.compile_aliases(ALIAS_TABLE)
BARS = json.loads(screen.PREREGISTRATION.read_text(encoding="utf-8"))


# --- the two matchers, as shipped -----------------------------------------------------------------


def test_only_the_tracked_half_of_the_lexicon_is_read():
    """dairy and ice-cream are the taxonomy. `bakery`, `meat` and the rest are food, not our
    food — reading them would make every recipe feed look like a dairy source."""
    assert set(CATS) == {"dairy", "ice-cream"}
    assert core.category_hits("Свіжий хліб і ковбаса", CATS) == []
    assert core.category_hits("Кефір і морозиво", CATS) == ["dairy", "ice-cream"]


def test_the_endings_are_the_lexicons_own_and_the_set_is_closed():
    """`молок` + a case ending is milk; `молок` + «озавод» is a dairy PLANT and not an ending in
    the list. Keeping the set closed is the whole reason the lexicon ships one."""
    assert core.category_hits("Молоко 2,5%", CATS) == ["dairy"]
    assert core.category_hits("Молока не було", CATS) == ["dairy"]
    assert core.category_hits("Молокозавод у Лубнах", CATS) == []


def test_the_known_collision_is_still_here_and_is_not_patched_away():
    """The lexicon names it itself: «сир» + «ий» reads «креветка сира» as curd. It stays, and the
    record carries the sentence that says so — a stop-list of forms is where a draft lexicon
    starts pretending to be law."""
    assert "сир" in LEXICON["known_collision"]
    assert core.category_hits("креветка сира", CATS) == ["dairy"]


def test_the_brand_matcher_is_the_scorers_and_the_nesting_is_the_one_difference():
    """G1e is scored on `market_pulse.brands`, so "a brand hit" has to mean the same thing here.
    The one place the two part company is the watchlist's new nested pair."""
    for text in ("Масло «Ферма» 82%", "Морозиво Рудь", "Молоко Своя Лінія 2,5%", "нічого"):
        shipped = [hit["brand_id"] for hit in find_watchlist_brands(text, ALIAS_TABLE)]
        assert core.brand_hits(text, ALIASES) == shipped, text


def test_the_baby_food_line_does_not_pay_its_parent_brand():
    """«Яготинське для дітей» contains «Яготинське». The operator tracks them separately, so the
    longer span wins — otherwise every mention of the child credits the parent too, and the
    shipped matcher does exactly that."""
    text = "Новинка: Яготинське для дітей, сирок 100 г"
    assert core.brand_hits(text, ALIASES) == ["yahotynske-dlia-ditei"]
    assert {hit["brand_id"] for hit in find_watchlist_brands(text, ALIAS_TABLE)} == {
        "yagotynske",
        "yahotynske-dlia-ditei",
    }
    # The parent alone is untouched: this drops a CONTAINED span, not a brand.
    assert core.brand_hits("Молоко Яготинське 2,5%", ALIASES) == ["yagotynske"]


def test_the_negative_control_a_post_with_no_taxonomy_produces_nothing():
    """The brief's own negative control. Without it, "0 hits here" and "0 hits ever" look the
    same — and this fixture is deliberately food-adjacent, with a discount and a percentage in
    it, because those are what a retail post looks like from a distance."""
    assert core.category_hits(screen.NEGATIVE_CONTROL, CATS) == []
    assert core.brand_hits(screen.NEGATIVE_CONTROL, ALIASES) == []
    assert core.evidence_line(screen.NEGATIVE_CONTROL, CATS, ALIASES) is None


def test_the_evidence_is_a_quoted_line_carrying_the_term_that_fired():
    found = core.evidence_line("Заголовок\n🧀Сир Гауда 48%, 100 г\nхвіст", CATS, ALIASES)
    assert found == {
        "kind": "category",
        "name": "dairy:сир",
        "matched": "сир",
        "line": "🧀Сир Гауда 48%, 100 г",
    }


# --- the two bars, in their own currencies ---------------------------------------------------------


def test_a_channel_with_no_comment_source_gets_na_and_a_read_one_gets_a_verdict():
    """ "We did not look" and "we looked and it is empty" are different findings, and the operator
    is being asked to rule on the second. Only the first is N/A."""
    silent = core.bar_verdicts(9, 0, has_comment_source=False, bars=BARS)
    assert (silent["bar_A"], silent["bar_B"], silent["below_both"]) == ("PASS", "N/A", False)
    measured = core.bar_verdicts(0, 0, has_comment_source=True, bars=BARS)
    assert (measured["bar_A"], measured["bar_B"], measured["below_both"]) == ("FAIL", "FAIL", True)


def test_below_both_means_neither_currency_was_earned():
    """A channel that fails on posts but earns on comments is not below both — that is what
    "separate currencies" buys, and the audience segments are supposed to earn there."""
    assert core.bar_verdicts(0, 40, True, BARS)["below_both"] is False
    assert core.bar_verdicts(0, 0, False, BARS)["below_both"] is True


def test_sole_carriers_name_the_terms_a_pass_hangs_on():
    """Leverage, not judgement: a row carried only by «варто» — an ATB private label and the
    ordinary Ukrainian word for "it is worth" — reads identically in the counts to a row carried
    by «сир»."""
    only_varto = [{"brand:varto"} for _ in range(4)]
    assert core.sole_carriers(only_varto, 4) == ["brand:varto"]
    # Nothing is load-bearing when every post carries a second term: strike either one and the
    # four posts are still relevant.
    doubled = [{"dairy:сир", "dairy:молок"} for _ in range(4)]
    assert core.sole_carriers(doubled, 4) == []
    # And a term IS load-bearing when the posts it alone carries are what reach the bar.
    thin = [{"brand:varto"}, {"dairy:сир"}, {"dairy:сир"}, {"dairy:молок"}, {"ice-cream:морозив"}]
    assert core.sole_carriers(thin, 4) == ["dairy:сир"]
    # Below the bar there is nothing to hang on.
    assert core.sole_carriers([{"brand:varto"}], 4) == []


# --- the window, and the join --------------------------------------------------------------------


def test_the_four_originals_are_screened_over_their_own_28_days():
    """Amendment 3.12 says "a channel's collected 28-day window". The raw v1 store was pinned
    weeks before `collect_5c1.json`'s `since` existed and stops on 2026-07-23…27, so the shared
    window would give these four 13 to 17 days against everyone else's 28 while bar A counts
    absolutely."""
    shared = screen.collect_window()
    collected = screen.collected_handles()
    assert "@atb_market_official" not in collected and "@matusi_ukr" in collected

    posts = screen.load_jsonl(screen.POSTS / "atb_market_official.jsonl")
    own = screen.window_for("@atb_market_official", posts, shared, collected)
    assert own["source"] == "raw_v1_own_last_28d"
    assert own["since"] < own["until"]
    span = screen.datetime.fromisoformat(own["until"]) - screen.datetime.fromisoformat(own["since"])
    assert span.days == screen.WINDOW_DAYS

    theirs = screen.window_for("@matusi_ukr", posts, shared, collected)
    assert (theirs["source"], theirs["since"], theirs["until"]) == ("collect_5c1", *shared)


def test_comments_join_on_the_channel_post_id_and_never_on_reply_to(tmp_path, monkeypatch):
    """`parent_msg_id` is the CHANNEL post's id; `reply_to_msg_id` lives in the discussion group's
    own id space and only looks comparable. The fixture makes the two collide on purpose: a reply
    inside a thread whose `reply_to_msg_id` equals a real post id must not be counted."""
    monkeypatch.setattr(screen, "POSTS", tmp_path / "posts")
    monkeypatch.setattr(screen, "COMMENTS", tmp_path / "comments")
    (tmp_path / "posts").mkdir()
    (tmp_path / "comments").mkdir()
    (tmp_path / "posts" / "chan.jsonl").write_text(
        json.dumps({"msg_id": 100, "date": "2026-07-15T00:00:00+00:00", "text": "Сир 200 г"})
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "comments" / "chan.jsonl").write_text(
        "\n".join(
            json.dumps(row)
            for row in (
                {"msg_id": 5001, "parent_msg_id": 100, "reply_to_msg_id": 4999, "text": "смачно"},
                {"msg_id": 5002, "parent_msg_id": 777, "reply_to_msg_id": 100, "text": "не сюди"},
            )
        )
        + "\n",
        encoding="utf-8",
    )
    window = {"since": "2026-07-01", "until": "2026-08-01", "source": "test"}
    row = screen.screen_channel("@chan", window, CATS, ALIASES, BARS)
    assert row["relevant_posts"] == 1
    assert row["comments"]["in_store"] == 2
    assert row["comments"]["under_relevant"] == 1, "reply_to_msg_id was counted as a parent"


def test_a_post_without_text_is_counted_apart_from_an_off_category_one(tmp_path, monkeypatch):
    """The project already excludes channels as TEXT-FREE — «on topic and unreadable». A bar over
    all window posts cannot tell that class from an off-category one, and they are different
    operator rulings, so the split is in the row."""
    monkeypatch.setattr(screen, "POSTS", tmp_path / "posts")
    monkeypatch.setattr(screen, "COMMENTS", tmp_path / "comments")
    (tmp_path / "posts").mkdir()
    (tmp_path / "posts" / "chan.jsonl").write_text(
        "\n".join(
            json.dumps(row)
            for row in (
                {"msg_id": 1, "date": "2026-07-15T00:00:00+00:00", "text": "", "has_media": True},
                {"msg_id": 2, "date": "2026-07-16T00:00:00+00:00", "text": "знижки на все"},
            )
        )
        + "\n",
        encoding="utf-8",
    )
    row = screen.screen_channel(
        "@chan", {"since": "2026-07-01", "until": "2026-08-01", "source": "t"}, CATS, ALIASES, BARS
    )
    assert row["posts"] == {"in_window": 2, "with_text": 1, "without_text": 1}
    assert row["comments"]["source"] == "none" and row["bar_B"] == "N/A"


# --- the run: pre-registration, controls, and the refusal to overwrite -------------------------------


def test_the_bars_must_be_the_ones_registered_first(monkeypatch):
    """A bar moved to make the answer nicer has to be moved in the pre-registration file first,
    in writing, beside the original."""
    sha, bars = screen.check_preregistration()
    assert bars["bar_A_relevant_posts_28d"] == screen.BAR_A
    assert bars["currencies"].startswith("posts and comments are separate")
    assert len(sha) == 64
    monkeypatch.setattr(screen, "BAR_A", 1)
    with pytest.raises(SystemExit, match="not the ones registered"):
        screen.check_preregistration()


def test_a_failed_control_makes_the_verdicts_unreportable(tmp_path, monkeypatch):
    """A screen that cannot find the tracked category in the channels the project was built on
    has nothing to say about an unknown one. The record is still written — the numbers ARE the
    evidence for whatever went wrong — and the run exits non-zero."""
    monkeypatch.setattr(screen, "POSITIVE_CONTROLS", ("@dpssgovua", "@KarlivkaLive"))
    out = tmp_path / "screen.json"
    assert screen.main(["--out", str(out)]) == 1
    record = json.loads(out.read_text(encoding="utf-8"))
    assert record["verdicts_reportable"] is False
    assert record["controls"]["@KarlivkaLive"]["ok"] is False
    assert record["sources"], "the evidence still has to be written down"


def test_the_screen_refuses_to_overwrite_the_record_the_signature_cites(tmp_path):
    """Amendment 3.12's rider: the registry diff stays provisional until the operator reads THIS
    file and signs. A later pass under a moved registry must not land under that name."""
    with pytest.raises(SystemExit, match="already exists"):
        screen.main([])
    out = tmp_path / "elsewhere.json"
    assert screen.main(["--out", str(out), "--only", "@VARUS_channel"]) in (0, 1)
    assert out.exists()


def test_only_narrows_the_sweep_and_refuses_a_handle_the_registry_lacks(tmp_path):
    out = tmp_path / "screen.json"
    screen.main(["--out", str(out), "--only", "@VARUS_channel"])
    record = json.loads(out.read_text(encoding="utf-8"))
    assert [row["handle"] for row in record["sources"]] == ["@VARUS_channel"]
    with pytest.raises(SystemExit, match="does not carry"):
        screen.main(["--out", str(out), "--only", "@nosuchchannel"])


# --- the shipped record ---------------------------------------------------------------------------


def test_the_shipped_record_covers_the_whole_registry_and_cites_what_it_read():
    """ "Retroactively over the whole current registry" is the amendment's words, and the record
    has to be able to say WHICH registry and WHICH lexicon revision it read."""
    import hashlib

    record = json.loads((REPO_ROOT / "results" / "yield_screen_5c1.json").read_text("utf-8"))
    live = {handle for source in REGISTRY.sources for handle in source.telegram_channels}
    assert {row["handle"] for row in record["sources"]} == live
    assert record["summary"]["n"] == len(live) == 66
    assert (
        record["preregistration"]["sha256"]
        == hashlib.sha256(screen.PREREGISTRATION.read_bytes()).hexdigest()
    )
    assert record["registry"]["sha256"] == screen.sha256_of(screen.REGISTRY)
    assert record["lexicon"]["sha256"] == screen.sha256_of(screen.LEXICON)
    assert record["lexicon"]["status"] == "draft-not-law"
    assert record["registry"]["watchlist_brands"] == len(REGISTRY.watchlist)


def test_the_shipped_record_is_not_reportable_because_atb_yields_nothing():
    """The pre-registered positive control failed, and it failed on a real measurement: in its own
    28 days @atb_market_official posted 25 times, 19 of them image-only, and not one of the six
    texted posts names dairy, ice cream or a watchlist brand. The instrument reads that channel
    fine elsewhere — over its whole 777-post history it finds the category 34 times — so the zero
    is the window's, not the matcher's, and the refusal is the pre-registered one firing.
    """
    record = json.loads((REPO_ROOT / "results" / "yield_screen_5c1.json").read_text("utf-8"))
    assert record["verdicts_reportable"] is False
    failed = [name for name, control in record["controls"].items() if not control["ok"]]
    assert failed == ["@atb_market_official"]
    atb = next(row for row in record["sources"] if row["handle"] == "@atb_market_official")
    assert atb["relevant_posts"] == 0
    assert atb["posts"]["without_text"] > atb["posts"]["with_text"]
    assert atb["evidence"] is None
    # And the other three cleared it, so "the screen finds nothing" is not what happened.
    assert [name for name, c in record["controls"].items() if c["ok"]] == [
        "@silposilpo",
        "@VARUS_channel",
        "@msuaaaa",
        "negative control :: a fitness post with no taxonomy",
    ]


def test_the_shipped_record_names_the_terms_its_passes_hang_on():
    """The screen's own headline: two rows clear bar A on a term that is an ordinary word.
    @polyakova_fitness on «варто» («Про що варто пам'ятати»), @myrhorodtown on «Президент»
    (Zelensky). Pinned so the pass list cannot be read as 29 channels that carry the category."""
    record = json.loads((REPO_ROOT / "results" / "yield_screen_5c1.json").read_text("utf-8"))
    hangs = {
        row["handle"]: row["bar_A_sole_carriers"]
        for row in record["sources"]
        if row["bar_A_sole_carriers"]
    }
    assert hangs["@polyakova_fitness"] == ["brand:varto"]
    assert hangs["@myrhorodtown"] == ["brand:president"]
    varto = record["term_evidence"]["brand:varto"]
    assert varto["posts"] > 50 and varto["channels"] > 20
    assert varto["example"]["line"], "a term without a quoted line cannot be audited"


def test_the_shipped_record_publishes_the_originals_second_window_reading():
    """The window rule for the four originals is favourable to them, so the alternative is
    published rather than described: @msuaaaa clears bar A on its own 28 days and would not on the
    shared one."""
    record = json.loads((REPO_ROOT / "results" / "yield_screen_5c1.json").read_text("utf-8"))
    alternatives = {
        row["handle"]: row["alternative_window"]
        for row in record["sources"]
        if "alternative_window" in row
    }
    assert set(alternatives) == set(screen.POSITIVE_CONTROLS)
    assert alternatives["@msuaaaa"]["bar_A"] == "FAIL"
    msuaaaa = next(row for row in record["sources"] if row["handle"] == "@msuaaaa")
    assert msuaaaa["bar_A"] == "PASS"
    assert alternatives["@atb_market_official"]["relevant_posts"] == 0, "zero under both rules"


def test_a_bar_of_four_cannot_be_read_as_a_verdict_on_three_readable_posts():
    """A refusal to rule, not a verdict. Bar A is an absolute count over a denominator that runs
    from 0 to 1,535 across this registry, so a channel with fewer readable posts than the bar
    fails it by arithmetic whatever it publishes — and the census draws exactly this line with
    NO_POSTS_IN_WINDOW and TOO_FEW_DECIDABLE."""
    assert core.bar_A_reach(0, 0, 4) == "NO_POSTS_IN_WINDOW"
    assert core.bar_A_reach(9, 3, 4) == "TOO_FEW_TEXTED_POSTS"
    assert core.bar_A_reach(4, 4, 4) == "gradeable"


def test_the_whole_watch_bucket_is_below_both_and_none_of_it_is_a_content_finding():
    """The bug this split exists for. `watch` means "silent, posts collected, the group NEVER
    joined, revisited when it speaks again" — the operator ruled that ONCE, on the same zero. All
    seven are below both bars on 0 posts in the window, and putting them on a removal list would
    re-decide a decision on evidence that measures nothing."""
    record = json.loads((REPO_ROOT / "results" / "yield_screen_5c1.json").read_text("utf-8"))
    watch = {
        handle for source in REGISTRY.sources if source.watch for handle in source.telegram_channels
    }
    assert len(watch) == 7
    summary = record["summary"]
    assert watch <= set(summary["below_both"])
    assert watch <= set(summary["below_both_not_gradeable"])
    assert all(summary["below_both_not_gradeable"][h] == "NO_POSTS_IN_WINDOW" for h in watch)
    # The split covers the flag exactly — no row is in both halves and none is in neither.
    assert set(summary["below_both"]) == set(summary["below_both_gradeable"]) | set(
        summary["below_both_not_gradeable"]
    )
    assert not set(summary["below_both_gradeable"]) & set(summary["below_both_not_gradeable"])
    assert (len(summary["below_both_gradeable"]), len(summary["below_both_not_gradeable"])) == (
        24,
        12,
    )


# --- the rulings, written onto rows the screen already measured -----------------------------------


def test_close_rules_two_rows_below_the_bar_without_moving_what_was_measured(tmp_path):
    """The operator's read of a pass belongs beside the pass, and only beside it.

    The two rows cleared bar A on one ordinary word each, and the ruling says that does not count.
    What it must NOT do is rewrite `bar_A`: PASS is what the instrument found, and a record
    showing only the ruling could never be re-read as evidence about the instrument. The copy is
    made from the shipped record rather than a fixture, so the test sees the writer move.
    """
    out = tmp_path / "screen.json"
    out.write_text(
        (REPO_ROOT / "results" / "yield_screen_5c1.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    before = json.loads(out.read_text(encoding="utf-8"))

    assert screen.main(["--out", str(out), "--close"]) == 0
    after = json.loads(out.read_text(encoding="utf-8"))

    ruled = {row["handle"]: row for row in after["sources"] if "ruling" in row}
    assert set(ruled) == set(screen.RULINGS) == {"@polyakova_fitness", "@myrhorodtown"}
    for handle, row in ruled.items():
        assert row["bar_A"] == "PASS", handle
        assert len(row["bar_A_sole_carriers"]) == 1, handle
        assert "COUNTS AS BELOW bar A" in row["ruling"]

    def without_rulings(rows: list[dict]) -> list[dict]:
        return [{k: v for k, v in row.items() if k != "ruling"} for row in rows]

    assert without_rulings(after["sources"]) == without_rulings(before["sources"])
    # The measurement's provenance is not the ruling's. Overwriting the git block would replace
    # the commit the operator signed against with the commit of a pass that measured nothing.
    assert after["git"] == before["git"]
    assert after["rulings"]["git"]["commit"]
    assert after["summary"]["pass_A_ruled_below_bar_A"] == sorted(screen.RULINGS)
    assert after["summary"]["pass_A"] == before["summary"]["pass_A"]


def test_close_refuses_when_a_ruling_names_a_row_the_record_does_not_carry(tmp_path):
    """The negative control: without it, closing against a record that lacks the rows writes
    nothing at all and looks exactly like success."""
    record = json.loads(
        (REPO_ROOT / "results" / "yield_screen_5c1.json").read_text(encoding="utf-8")
    )
    record["sources"] = [row for row in record["sources"] if row["handle"] not in screen.RULINGS]
    out = tmp_path / "thinned.json"
    out.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(SystemExit, match="refusing to write a ruling to no one"):
        screen.main(["--out", str(out), "--close"])
