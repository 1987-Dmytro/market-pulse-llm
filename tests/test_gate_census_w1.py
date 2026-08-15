"""`results/gate_census_w1.json` — the gate priced, and every claim in it re-derived here."""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import gate_census_w1 as census  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

RECORD_PATH = REPO_ROOT / "results" / "gate_census_w1.json"
RECORD = json.loads(RECORD_PATH.read_text(encoding="utf-8"))
CELLS = ("narrow|silencers_off", "narrow|silencers_on", "wide|silencers_off", "wide|silencers_on")


def test_the_committed_census_is_what_the_producer_writes_today(tmp_path):
    """Byte-identical: no clock, no git block, sorted keys — so every number below re-derives."""
    out = tmp_path / "again.json"
    assert census.main(["--out", str(out)]) == 0
    assert out.read_bytes() == RECORD_PATH.read_bytes()


def test_it_writes_no_pre_registration():
    """The contract says so and the record has to be checkable against it.

    A census that proposed the probe's bars would be a registration written by its own executor —
    plan §5 puts those words with the operator, before any paid reading.
    """
    assert set(RECORD) & {"bars", "gates", "thresholds", "stop_rules", "ratification"} == set()
    assert "operator" in RECORD["authority"]
    assert "No pre-registration is written" in RECORD["authority"]


def test_the_thread_join_is_complete_and_says_so():
    """The unit of D3 exists only if every comment's parent post does. Measured, not assumed."""
    assert RECORD["window"]["threads_with_no_post_in_the_raw_store"] == []
    assert RECORD["window"]["threads"] == 514
    assert RECORD["window"]["comments"] == 5075
    assert RECORD["window"]["comments_text_less"] == 1361


@pytest.mark.parametrize("name", CELLS)
def test_every_cell_prices_itself_from_its_own_unit(name):
    """The two ends of the interval are the record's own arithmetic, re-done here.

    Both are checked because they answer different questions: the lower end is threads × the unit
    and the upper is payable comments × the unit, and a cell that had silently priced one of them
    off the other's count would still look like a plausible interval.
    """
    cell = RECORD["grid"][name]
    cost = cell["cost"]
    unit = cost["unit_seconds"] * cost["rate_usd_per_second"]

    assert cost["lower_usd"] == round(cell["threads"] * unit, 4)
    assert cost["upper_usd"] == round(cell["comments_payable"] * unit, 4)
    assert cost["lower_usd"] < cost["upper_usd"]
    assert "NOT one thread" in cost["unit"]
    assert "comment rows in" in cost["sample"] and "endpoint" in cost["sample"]


def test_the_price_unit_is_the_one_the_measured_record_carries():
    """The rate is READ from `results/run_5c2_comments.json`, never typed — and its sample with it."""
    prices = json.loads((REPO_ROOT / "results" / "run_5c2_comments.json").read_text("utf-8"))
    for name in CELLS:
        cost = RECORD["grid"][name]["cost"]
        assert cost["rate_usd_per_second"] == prices["rate_usd_per_second"]
        assert cost["unit_seconds"] == prices["timing"]["seconds_per_row"]
        assert str(prices["timing"]["rows"]) in cost["sample"]


def test_the_grid_moves_the_way_a_gate_has_to():
    """Wider vocabulary lets more through; silencers only ever take away.

    A monotonicity check and not a value check: it holds for any window, and it is the one property
    that would catch a cell wired to the wrong lexicon or the wrong silencer set.
    """
    grid = RECORD["grid"]
    for silencers in ("off", "on"):
        assert (
            grid[f"wide|silencers_{silencers}"]["threads"]
            >= (grid[f"narrow|silencers_{silencers}"]["threads"])
        )
    for width in ("narrow", "wide"):
        assert grid[f"{width}|silencers_on"]["threads"] <= grid[f"{width}|silencers_off"]["threads"]
        assert (
            grid[f"{width}|silencers_on"]["comments_payable"]
            <= grid[f"{width}|silencers_off"]["comments_payable"]
        )


def test_the_silencers_are_decomposed_and_the_overlap_is_measured():
    """The 2×2 alone would read as four disjoint buckets. Each silencer also runs on its own."""
    one_by_one = RECORD["silencer_decomposition"]
    assert set(one_by_one["each_alone"]) == set(census.SILENCERS)
    assert one_by_one["all_three_together"]["threads_removed"] == 18
    # equal in THIS window: the varto rule accounts for all eighteen and the other two remove
    # comments without dropping a thread below the gate. The record carries both numbers so a
    # window where they differ shows its overlap instead of hiding it.
    assert (
        one_by_one["all_three_together"]["sum_of_the_singles"]
        == (one_by_one["all_three_together"]["threads_removed"])
    )
    assert one_by_one["each_alone"]["varto_rule"]["threads_removed"] == 18
    assert one_by_one["each_alone"]["plus_spam"]["comments_silenced_window_wide"]["plus_spam"] > 0
    assert one_by_one["each_alone"]["scam"]["comments_silenced_window_wide"]["scam"] > 0


def test_the_fourth_silencer_is_declared_absent_with_its_reason_and_unlock():
    """`an_absolute_bar_needs_a_reachability_state`: a rule with no input is not a rule that fired.

    Reporting «giveaway threads removed: 0» beside three working silencers would read as "there
    were none". There is no post-type label in this window at all, and the record says which
    instrument would have to run before the number means anything.
    """
    fourth = RECORD["silencers"]["giveaway_threads"]
    assert fourth["implemented"] is False
    assert fourth["why_not"] and fourth["unlock"]
    assert "post-type label" in fourth["why_not"]
    for name in census.SILENCERS:
        assert RECORD["silencers"][name]["implemented"] is True
        assert RECORD["silencers"][name]["authority"]


def test_the_narrow_lexicon_is_the_law_and_the_wide_one_is_the_draft_beside_it():
    """Two vocabularies, each named with the file it came from and that file's sha."""
    narrow, wide = RECORD["lexicons"]["narrow"], RECORD["lexicons"]["wide"]
    assert set(narrow["groups"]) == {"dairy", "ice-cream"}
    assert set(wide["groups"]) > set(narrow["groups"])
    assert narrow["sha256"] == summary.sha256_of(REPO_ROOT / "config" / "lexicon.yaml")
    assert wide["sha256"] == summary.sha256_of(REPO_ROOT / "data" / "category_lexicon_draft.json")
    for group, stems in narrow["groups"].items():
        assert wide["groups"][group] == stems, group


def test_a_thread_is_two_carriers_and_the_gate_is_told_which():
    """SPEC 3.21 (1) scopes the `garmonija` rule to comment text, and a thread has post text in it.

    Passing one carrier for the whole thread would have applied the comment rule to the post — a
    channel's own post naming Гармонія is a trade mark printed by a retailer, which is exactly the
    situation `applies_to` exempts. In window-1 the two readings give the same grid, which is why
    this is asserted on the matcher rather than inferred from a thread count that did not move.
    """
    from market_pulse import brands
    from market_pulse.registry import load_registry

    aliases = brands.watchlist_aliases(
        load_registry(REPO_ROOT / "config" / "registry.yaml").watchlist
    )
    rules = brands.load_watchlist_rules(REPO_ROOT / "config" / "watchlist_rules.yaml")
    categories = census.compiled(wide=False)
    bare = "Гармонія — нові смаки вже у магазинах"

    assert census.hits(bare, categories, aliases, rules, census.POST_CARRIER)["brands"] == [
        "garmonija"
    ]
    assert census.hits(bare, categories, aliases, rules, census.CARRIER)["brands"] == []
    assert census.POST_CARRIER != census.CARRIER


def test_the_posts_are_pinned_by_what_was_read_and_not_by_a_live_store():
    """`data/raw/posts` keeps growing — the next contract collects into it.

    Hashing its 75 files would put a dated expiry on `make check`: the first appended post would
    redden this suite for a reason nobody would connect to a gate census. The pin is over the 514
    posts this record actually read, so a new post moves nothing and an EDIT to one of these moves
    the digest — which is the only change that could move a number here.
    """
    pin = RECORD["posts_read"]
    assert pin["posts"] == RECORD["window"]["threads"]
    assert not any(name.startswith("data/raw/") for name in RECORD["sources"])

    posts = census.raw_posts()
    threads, orphans = census.threads(
        [
            row
            for path in summary.leg_files(REPO_ROOT / "data" / "derived", "inference")
            for row in summary.read_rows(path)
        ],
        posts,
    )
    assert orphans == []
    assert census.posts_pin(threads)["sha256"] == pin["sha256"]


def test_the_record_names_every_byte_it_read():
    for name, digest in RECORD["sources"].items():
        assert summary.sha256_of(REPO_ROOT / name) == digest, name
    for name, digest in RECORD["inputs"].items():
        assert summary.sha256_of(REPO_ROOT / name) == digest, name
    for name, digest in RECORD["producer"]["borrowed"].items():
        assert summary.sha256_of(REPO_ROOT / name) == digest, name
    assert RECORD["producer"]["sha256"] == summary.sha256_of(
        REPO_ROOT / RECORD["producer"]["script"]
    )
    assert "config/watchlist_rules.yaml" in RECORD["inputs"]


def test_the_two_text_silencers_fire_on_the_marker_and_not_on_a_sentence():
    """The narrow reading is deliberate: «+» inside a sentence is a person writing, not a bot."""
    assert census.PLUS_SPAM.fullmatch("+")
    assert census.PLUS_SPAM.fullmatch("++ ")
    assert census.PLUS_SPAM.fullmatch("Тест")
    assert not census.PLUS_SPAM.fullmatch("+ дуже смачно")
    assert not census.PLUS_SPAM.fullmatch("тестували цей сир")

    assert census.MONEY.search("100 грн") and census.CONTACT.search("пишіть @fast_money_bot")
    assert not census.CONTACT.search("сир коштує 100 грн")
    assert not census.MONEY.search("пишіть у @support_bot")


def test_the_silenced_rows_are_real_rows_of_this_window():
    """Counted off the evidence through the ONE reader, and held against the record's own totals.

    Not a hand-built row: `window_summary_5c2.comment_text` recovers what was SENT by re-rendering
    the split and proving it, so a fixture shaped like a row would not survive that reader — and a
    silencer tested on a shape the store does not hold is a silencer nobody has run.
    """
    from market_pulse import loop

    rows = []
    for path in summary.leg_files(REPO_ROOT / "data" / "derived", loop.RECORD_TYPE):
        rows += summary.read_rows(path)
    fired = [census.silenced_comment(row, census.SILENCERS) for row in rows]

    window_wide = RECORD["silencer_decomposition"]["each_alone"]
    assert (
        fired.count("plus_spam")
        == (window_wide["plus_spam"]["comments_silenced_window_wide"]["plus_spam"])
    )
    assert fired.count("scam") == window_wide["scam"]["comments_silenced_window_wide"]["scam"]
    assert fired.count("plus_spam") > 0 and fired.count("scam") > 0
