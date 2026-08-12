"""The sku-b bar producer: hand-computed arithmetic, and the refusals that guard it.

Every fixture here is synthetic and small enough to check on paper. The one thing that cannot be
checked on paper is the key space the two halves of bar 1 arrive in — the gold carries the
reviewer's brands and the dump carries the model's — so that gets its own test with a control.
"""

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_sku_text_pack as builder  # noqa: E402
import sku_bar_verdicts as verdicts  # noqa: E402
import validate_sku_text_pack as pack  # noqa: E402

from market_pulse import positions  # noqa: E402
from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

REGISTRY = REPO_ROOT / "config" / "registry.yaml"
ALIASES = watchlist_aliases(load_registry(REGISTRY).watchlist)
LIVE_REGISTRY_SHA = hashlib.sha256(REGISTRY.read_bytes()).hexdigest()

PREREG = {
    # the alias table these synthetic bars are scored under, named the way a real registration
    # names it. SPEC 3.17 (13)(b) made the watchlist a moving part, so `registered_aliases` reads
    # the pin instead of the file and refuses a registration that pins neither.
    "pinned_inputs": {"config/registry.yaml": LIVE_REGISTRY_SHA},
    "bars": {
        "leaflet_brand_recall": {
            "verbatim": "leaflet brand-recall ≥ 0.75 per page vs audit-visible brands",
            "threshold": 0.75,
            "denominator": "per post, macro over the posts with a non-empty gold set",
            "gold": {"sha256": "set by the fixture"},
            "excluded": {"posts": ["@c:3"], "instead": "a precision probe"},
        },
        "price_pair_accuracy": {
            "verbatim": "price-pair accuracy ≥ 0.80 on positions carrying a crossed-out price",
            "threshold": 0.80,
            "denominator": "price_old is not None on a leaflet_page position",
            "reachability": {"rule": "n >= 10 scores; 1..9 reports; 0 is NOT_REACHABLE"},
            "procedure": "the team lead opens each cited page image",
        },
        "text_tier_accuracy": {
            "verbatim": "text tier-assignment accuracy ≥ 0.85 vs adjudicated rows",
            "threshold": 0.85,
            "denominator": "a row the operator left untouched is not gold and is not counted",
            "comparison": "per row, both tiers from positions.tier_from_presence",
            "unreadable_rows": "excluded and counted; over 10% the bar is NOT_SCORED",
            "reachability": {"rule": "n >= 20 rows scores"},
            "gold": {
                "manifest": "set by the fixture",
                "manifest_sha256": "set by the fixture",
                "ladder_sha256": positions.ladder_sha256(),
                "by_carrier": {"post_text": 2, "comment": 0},
            },
        },
    },
    "resume": {"population": {"registered": 0}},
    "ratification_required": [{"id": "R1"}],
    "attempts": {
        "phase": "fixture",
        "on_failure": "a failed bar closes B as 'instrument not ready' BY MEASUREMENT",
    },
}


def pair_read(dump_sha: str, verdicts: list[tuple[str, int]]) -> dict:
    """A synthetic `sku_b_pair_verdicts.json`: `(verdict, n)` per key, and the counts it states.

    The join to the dump is the applier's job and has its own suite; what bar 2 has to get right is
    the arithmetic, the threshold and the two things it refuses — a read over another dump and a
    read whose rows are not the bar's denominator.
    """
    rows = sum(n for _, n in verdicts)
    correct = sum(n for verdict, n in verdicts if verdict == "correct")
    return {
        "read_by": "the team lead",
        "read_on": "2026-01-02",
        "read_scope": "every pair against its page",
        "contract": "docs/PROMPT-fixture.md",
        "diagnosis": "the kopiyky are the whole error",
        "dump": {"sha256": dump_sha},
        "expected": {
            "keys": len(verdicts),
            "rows": rows,
            "correct_rows": correct,
            "wrong_rows": rows - correct,
            "accuracy_4dp": round(correct / rows, 4),
        },
        "keys": [{"verdict": verdict, "n": n} for verdict, n in verdicts],
    }


def page(item: str, n: int) -> dict:
    return {"item": item, "page": n, "file": f"{item}-{n}.jpg"}


def dump_row(item: str, page_no, brand_raw: str, price_old=None, tier: str = "position") -> dict:
    return {
        "item": item,
        "page": page_no,
        "brand_raw": brand_raw,
        "brand_id": positions.resolve_brand(brand_raw, ALIASES),
        "price_old": price_old,
        "tier": tier,
    }


def outcome(item: str, source: str, leg: str, carrier: str, unreadable=None, n=1) -> dict:
    return {
        "item": item,
        "source": source,
        "leg": leg,
        "carrier": carrier,
        "unreadable": unreadable,
        "n_positions": n,
    }


# --- bar 1 -------------------------------------------------------------------
#
#   @a:1  gold {rud, raw:каштан}       model reads Рудь on page 1, Каштан on page 2 -> 2/2 = 1.0
#   @b:2  gold {raw:svoia-liniia}      model reads Ласунка                          -> 0/1 = 0.0
#   @c:3  gold {}                      EXCLUDED by R3; its one brand is a precision probe
#   macro over the two scoreable posts = (1.0 + 0.0) / 2 = 0.5 -> FAIL against 0.75
REFERENCE = {
    "gold": {
        "definition": "the watchlist id when the name resolves to one, `raw:` + the name otherwise",
        "posts_with_an_empty_gold_set": ["@c:3"],
    },
    "posts": [
        {
            # `rud`, not `raw:rud`, since SPEC 3.17 (13)(b) — see the docstring of
            # `test_bar_one_puts_a_resolved_watchlist_brand_in_the_reviewers_key_space`, which
            # named this exact failure a session before it happened.
            "item": "@a:1",
            "brands_visible": {"gold_keys": ["rud", "raw:каштан"]},
            "pages_sent": [page("@a:1", 1), page("@a:1", 2)],
        },
        {
            "item": "@b:2",
            "brands_visible": {"gold_keys": ["raw:svoia-liniia"]},
            "pages_sent": [page("@b:2", 1)],
        },
        {"item": "@c:3", "brands_visible": {"gold_keys": []}, "pages_sent": [page("@c:3", 1)]},
    ],
}

# The SAME three posts as B′ carries them (Dv210): the gold is the registration's own re-scoped
# table, not the reference's. (13)(c) empties @b:2 — its one pair was ruled class b — so the macro
# is taken over @a:1 alone and comes out 1.0 where the reference's gold gives 0.5 over two posts.
# One set of files, two golds, two numbers: that difference is what the wiring is for.
#
# `gold_keys_v4` sits beside `gold_keys` in the real registration and is the trap: @a:1's «Рудь»
# keys `raw:rud` in the v4 space and `rud` under the (13)(b) table, and `rud` is what the PREDICTION
# side resolves to. Reading the wrong field costs a whole key on a post the instrument got right.
B_PRIME_PER_POST = [
    {
        "item": "@a:1",
        "gold_keys_v4": ["raw:rud", "raw:каштан"],
        "gold_keys": ["rud", "raw:каштан"],
    },
    {"item": "@b:2", "gold_keys_v4": ["raw:svoia-liniia"], "gold_keys": []},
    {"item": "@c:3", "gold_keys_v4": [], "gold_keys": []},
]

DUMP = [
    dump_row("@a:1", 1, "Рудь", price_old=75.9),
    dump_row("@a:1", 2, "Каштан"),
    dump_row("@b:2", 1, "Ласунка", price_old=41.0),
    dump_row("@c:3", 1, "Лімо"),
    dump_row("@t:1", None, "Рудь", price_old=99.0),  # a text row: bar 1 and bar 2 both ignore it
]

RECORD = {
    "population": {"unbought": 0, "asked": 5},
    "dump": {"path": "results/x.jsonl", "sha256": "…", "rows": 5, "columns": []},
    "outcomes": [
        outcome("@a:1", "@a:1-1.jpg", "page", "leaflet_page"),
        outcome("@a:1", "@a:1-2.jpg", "page", "leaflet_page"),
        outcome("@b:2", "@b:2-1.jpg", "page", "leaflet_page"),
        outcome("@c:3", "@c:3-1.jpg", "page", "leaflet_page"),
        outcome("@t:1", "@t:1", "text", "post_text"),
    ],
}


def test_bar_one_macro_averages_the_posts_with_gold_and_excludes_the_empty_ones():
    bar = verdicts.bar_one(RECORD, DUMP, PREREG, REFERENCE, ALIASES)
    assert [row["recall"] for row in bar["per_post"]] == [1.0, 0.0]
    assert bar["value"] == pytest.approx(0.5) and bar["verdict"] == "FAIL"
    # micro pools the pairs: 2 of 3 gold keys found, and precision is 2 of the 3 keys extracted
    # on the two scoreable posts — the fourth brand sits on the excluded post.
    assert bar["micro_reported_never_gated"] == pytest.approx(2 / 3)
    assert bar["precision_micro_reported_never_gated"] == pytest.approx(2 / 3)
    assert bar["n_posts"] == 2
    probe = bar["precision_probe"]["posts"]
    assert [row["item"] for row in probe] == ["@c:3"]
    # `limo` and not `raw:limo`, the second brand (13)(b) folded onto its own id — «LIMO» is a
    # display name now, so «Лімо» resolves and the key loses the prefix
    assert probe[0]["false_positives"] == ["limo"]


def test_bar_one_puts_a_resolved_watchlist_brand_in_the_reviewers_key_space():
    """The trap: the reviewer names ids, the model names printed text, and both go through
    `gold_key`. «Рудь» resolves to the watchlist id `rud`, and the id itself is now a display name
    — SPEC 3.17 (13)(b) added the Latin «Rud», which casefolds onto `rud` — so the gold key is
    `rud`. Until 2026-08-12 it was `raw:rud`, and this docstring said so, with the sentence «if
    either changed, one of these two posts would silently read 0.5 instead of 1.0». It changed, and
    that is exactly what this test read before the fixture was moved with it.

    Which is the standing hazard, written down: bar 1's GOLD half is stored and its PREDICTION half
    is recomputed, so the two agree only while the stored keys came from the same alias table. The
    sealed v4 gold is therefore recomputed through the table its pre-registration pins, and the B′
    gold is REBUILT under the amended table rather than filtered out of the v4 keys.

    The control is a brand OFF the watchlist: «Каштан» never resolves, and its key is built from
    the printed name. Two different routes into one space.
    """
    bar = verdicts.bar_one(RECORD, DUMP, PREREG, REFERENCE, ALIASES)
    found = bar["per_post"][0]
    assert positions.resolve_brand("Рудь", ALIASES) == "rud"  # resolved…
    assert positions.resolve_brand("Каштан", ALIASES) is None  # …and not resolved
    assert found["extracted"] == ["raw:каштан", "rud"] == found["found"]
    assert found["missed"] == [] and found["not_in_gold"] == []


def test_bar_one_refuses_when_the_reference_and_the_ratified_exclusions_disagree():
    prereg = json.loads(json.dumps(PREREG))
    prereg["bars"]["leaflet_brand_recall"]["excluded"]["posts"] = ["@a:1"]
    with pytest.raises(SystemExit, match="not the ones R3 excludes"):
        verdicts.bar_one(RECORD, DUMP, prereg, REFERENCE, ALIASES)


# --- Dv210: which gold bar 1 is scored against ------------------------------


def as_b_prime(prereg: dict, **gold_overrides) -> dict:
    """Move a v4-shaped registration into B′'s shape, in place.

    Three fields move and every one of them is a KeyError on the old reader: the gold becomes the
    registration's own `per_post` with the reference demoted to `derived_from`, the population
    leaves the resume block for the top level, and the resume block goes.
    """
    gold = prereg["bars"]["leaflet_brand_recall"]["gold"]
    gold["derived_from"] = {"path": "reference.json", "sha256": gold.pop("sha256")}
    gold.update(
        per_post=json.loads(json.dumps(B_PRIME_PER_POST)),
        posts_with_an_empty_gold_set=["@b:2", "@c:3"],
        posts_with_a_non_empty_gold_set=1,
        pairs=2,
    )
    gold.update(gold_overrides)
    prereg["bars"]["leaflet_brand_recall"]["excluded"]["posts"] = ["@b:2", "@c:3"]
    prereg["population"] = {"elements": prereg.pop("resume")["population"]["registered"]}
    return prereg


def b_prime_prereg(**gold_overrides) -> dict:
    return as_b_prime(json.loads(json.dumps(PREREG)), **gold_overrides)


def test_bar_one_scores_the_registrations_own_gold_when_it_carries_one():
    """The number moves: 0.5 over the reference's two posts, 1.0 over B′'s one.

    @a:1's gold is {rud, raw:каштан} on both sides and the model read both, so the post is 1.0
    either way. What (13)(c) changes is the DENOMINATOR — @b:2, where the model was wrong, leaves
    it — and a macro mean over a different set of posts is a different bar.
    """
    bar = verdicts.bar_one(RECORD, DUMP, b_prime_prereg(), REFERENCE, ALIASES)
    assert bar["value"] == pytest.approx(1.0) and bar["verdict"] == "PASS"
    assert [post["item"] for post in bar["per_post"]] == ["@a:1"]
    assert bar["n_posts"] == 1 and bar["n_gold_keys"] == 2
    assert "gold.per_post" in bar["key_space"]["gold_from"]
    # @b:2 joined the precision probe rather than vanishing: its wrong read is still reported
    assert [post["item"] for post in bar["precision_probe"]["posts"]] == ["@b:2", "@c:3"]
    assert bar["precision_probe"]["posts"][0]["false_positives"] == ["raw:lasunka"]

    # …and the sealed reference is still the gold when the registration pins it as one
    assert verdicts.bar_one(RECORD, DUMP, PREREG, REFERENCE, ALIASES)["value"] == pytest.approx(0.5)


def test_bar_one_reads_the_b_prime_keys_and_not_the_v4_ones():
    """The half of Dv210 that produces a number instead of an error.

    The control is the same fixture with the v4 space written into `gold_keys`: @a:1's «Рудь» keys
    `raw:rud` there, the prediction side resolves it to `rud` through the (13)(b) alias table, and
    one of two gold keys goes missing — 1.0 becomes 0.5 with nothing on screen to say why.
    """
    per_post = json.loads(json.dumps(B_PRIME_PER_POST))
    assert per_post[0]["gold_keys"] != per_post[0]["gold_keys_v4"]  # the fixture has both spaces
    bar = verdicts.bar_one(RECORD, DUMP, b_prime_prereg(), REFERENCE, ALIASES)
    assert (
        bar["per_post"][0]["gold"] == ["raw:каштан", "rud"] and bar["per_post"][0]["missed"] == []
    )

    # only @a:1: giving @b:2 its v4 keys back would UN-EMPTY it and the run would refuse on the
    # denominator instead, which is a different guard and would hide the one under test
    per_post[0]["gold_keys"] = per_post[0]["gold_keys_v4"]
    control = verdicts.bar_one(RECORD, DUMP, b_prime_prereg(per_post=per_post), REFERENCE, ALIASES)
    assert control["per_post"][0]["missed"] == ["raw:rud"]
    assert control["value"] == pytest.approx(0.5)


def test_a_registration_that_names_both_golds_or_neither_is_refused():
    both = b_prime_prereg()
    both["bars"]["leaflet_brand_recall"]["gold"]["sha256"] = "x"
    with pytest.raises(SystemExit, match="both `per_post` and `sha256`"):
        verdicts.bar_one(RECORD, DUMP, both, REFERENCE, ALIASES)

    neither = json.loads(json.dumps(PREREG))
    del neither["bars"]["leaflet_brand_recall"]["gold"]["sha256"]
    with pytest.raises(SystemExit, match="neither `per_post` nor `sha256`"):
        verdicts.bar_one(RECORD, DUMP, neither, REFERENCE, ALIASES)


def test_the_gold_is_joined_to_the_reference_by_item_and_refuses_a_post_it_cannot_find():
    """The reference supplies the post list and the sent-page counts, the registration the keys.
    Two lists indexed side by side would attribute one post's gold to another and still report a
    number, so the join is by `item` and a post on one side only stops it."""
    per_post = json.loads(json.dumps(B_PRIME_PER_POST))
    per_post[1]["item"] = "@b:22"
    with pytest.raises(SystemExit, match="cover different posts"):
        verdicts.bar_one(RECORD, DUMP, b_prime_prereg(per_post=per_post), REFERENCE, ALIASES)


def test_the_registrations_summary_counts_are_checked_against_its_own_rows():
    """10 posts and 37 pairs is the contract's checksum for the real file; here it is 1 and 2.
    Every one of the three is re-derived from `per_post`, because a summary field is a second way
    of saying what the rows say and only the rows are the thing."""
    for field, value, message in (
        ("pairs", 3, "gives pairs = 2 and the registration states 3"),
        ("posts_with_a_non_empty_gold_set", 2, "non_empty_gold_set = 1 and the registration"),
        ("posts_with_an_empty_gold_set", ["@c:3"], "empty_gold_set = ['@b:2', '@c:3']"),
    ):
        with pytest.raises(SystemExit, match=re.escape(message)):
            verdicts.bar_one(RECORD, DUMP, b_prime_prereg(**{field: value}), REFERENCE, ALIASES)


def test_the_shipped_b_prime_gold_is_the_37_over_10_the_contract_states():
    """The witness on the real files: no fixture can prove the shipped registration joins."""
    prereg = json.loads(verdicts.PREREG.read_text(encoding="utf-8"))
    reference = json.loads(verdicts.REFERENCE.read_text(encoding="utf-8"))
    empty, keys, source = verdicts.gold_source(prereg, reference)
    assert len(keys) == 19 and len(empty) == 9
    assert len(keys) - len(empty) == 10
    assert sum(len(gold) for gold in keys.values()) == 37
    assert "13" in source and "per_post" in source
    # the key space, on the one post where the two tables disagree
    assert keys["@atb_market_official:4340"] == {"rud", "raw:svoia-liniia", "raw:try-vedmedi"}
    assert (
        verdicts.reference_pin(prereg)
        == hashlib.sha256(verdicts.REFERENCE.read_bytes()).hexdigest()
    )


def test_the_shipped_verdict_record_is_the_closure_over_the_read_on_disk():
    """B′'s closure is a file, not a sentence in a report — and it is only true while the read it
    was taken over is the read on disk. Re-running the applier without re-running this producer
    would leave a closure pinned to a pair-verdicts file that no longer exists at that sha.

    This test reads a SHIPPED artifact, so it lives in the commit that ships it: put in the
    producer's commit it is red until the next one, which is how `3c1dc8a` in this session's first
    ordering came to fail its own suite (Dv240)."""
    out = json.loads((REPO_ROOT / "results" / "sku_bar_verdicts_skub2.json").read_text("utf-8"))
    two = out["bars"]["price_pair_accuracy"]
    assert (two["value"], two["verdict"], two["n_pairs"]) == (0.4125, "FAIL", 80)
    assert two["read"]["sha256"] == hashlib.sha256(verdicts.PAIRS.read_bytes()).hexdigest()
    assert out["closure"]["state"] == "CLOSED — instrument not ready, BY MEASUREMENT"
    assert out["closure"]["failed_bars"] == ["price_pair_accuracy"]
    assert out["closure"]["passed_bars"] == ["leaflet_brand_recall", "text_tier_accuracy"]
    assert out["closure"]["undecided_bars"] == []


def test_bar_one_counts_unreadable_pages_without_excluding_them():
    record = json.loads(json.dumps(RECORD))
    record["outcomes"][1]["unreadable"] = "malformed JSON"
    bar = verdicts.bar_one(
        record, [row for row in DUMP if row["page"] != 2], PREREG, REFERENCE, ALIASES
    )
    assert bar["unreadable_pages"]["n"] == 1
    assert bar["unreadable_pages"]["by_post"] == {"@a:1": ["@a:1-2.jpg"]}
    # the page's brand is simply absent from the union — recall 1/2, not an exclusion
    assert bar["per_post"][0]["recall"] == pytest.approx(0.5)


# --- bar 2 -------------------------------------------------------------------


def test_bar_two_counts_leaflet_pairs_only_and_waits_when_there_is_no_read():
    bar = verdicts.bar_two(RECORD, DUMP, PREREG)
    assert bar["n_pairs"] == 2  # the text row's price_old is not a leaflet pair
    assert bar["value"] is None and bar["verdict"] == "PENDING_TEAM_LEAD"
    assert bar["reachability"]["class"] == "REPORTED_NOT_SCORED"
    assert verdicts.bar_two(RECORD, DUMP * 5, PREREG)["reachability"]["class"] == "SCOREABLE"
    assert verdicts.bar_two(RECORD, [], PREREG)["reachability"]["class"] == "NOT_REACHABLE"


def test_bar_two_takes_its_value_from_the_read_and_states_it_against_the_threshold():
    sha = RECORD["dump"]["sha256"]
    pin = {"path": "results/pairs.json", "sha256": "abc"}
    failed = verdicts.bar_two(RECORD, DUMP, PREREG, pair_read(sha, [("correct", 1), ("wrong", 1)]))
    assert failed["value"] == pytest.approx(0.5) and failed["verdict"] == "FAIL"
    assert failed["stated"] == "0.5000 vs 0.80 — FAIL (n=2, read by the team lead 2026-01-02)"
    assert failed["why_no_value"] is None

    # the control: the same shape above the bar, so FAIL is a reading of the number and not the
    # only branch the code has
    passed = verdicts.bar_two(RECORD, DUMP, PREREG, pair_read(sha, [("correct", 2)]), pin)
    assert passed["value"] == 1.0 and passed["verdict"] == "PASS"
    assert passed["read"]["path"] == "results/pairs.json" and passed["read"]["sha256"] == "abc"
    assert passed["read"]["correct_rows"] == 2 and passed["read"]["accuracy_4dp"] == 1.0


def test_bar_two_refuses_a_read_taken_over_a_different_dump():
    read = pair_read("a-dump-that-is-not-this-one", [("correct", 1), ("wrong", 1)])
    with pytest.raises(SystemExit, match="two different sets of pairs"):
        verdicts.bar_two(RECORD, DUMP, PREREG, read)


def test_bar_two_refuses_a_read_that_is_not_the_whole_denominator():
    """The bar counts 2 pairs; a read of 1 of them would score a bar over a sample of a sample."""
    read = pair_read(RECORD["dump"]["sha256"], [("correct", 1)])
    with pytest.raises(SystemExit, match="the read covers 1 rows and the bar's denominator is 2"):
        verdicts.bar_two(RECORD, DUMP, PREREG, read)


def test_bar_two_refuses_a_read_whose_own_counts_do_not_add_up():
    """The applier's checksums run again here, so a hand-edited verdicts file is caught on read."""
    read = pair_read(RECORD["dump"]["sha256"], [("correct", 1), ("wrong", 1)])
    read["keys"][0]["verdict"] = "wrong"  # 0 correct now, and `expected` still says 1
    with pytest.raises(SystemExit, match="the read states correct_rows = 1"):
        verdicts.bar_two(RECORD, DUMP, PREREG, read)


# --- bar 3 -------------------------------------------------------------------


def text_fixture(n_rows: int, unreadable: int = 0, wrong: int = 0) -> tuple[dict, list, list]:
    """`n_rows` adjudicated rows, all gold `position`; the first `unreadable` refuse to parse and
    the next `wrong` come back a rung lower."""
    readings = [
        {"id": f"@t:{i}", "tier": "position", "ticks": {"brand": True}, "notes": ""}
        for i in range(n_rows)
    ]
    outcomes, dump = [], []
    for i in range(n_rows):
        reason = "malformed JSON" if i < unreadable else None
        outcomes.append(outcome(f"@t:{i}", f"@t:{i}", "text", "post_text", unreadable=reason))
        if reason:
            continue
        tier = "product_mention" if i < unreadable + wrong else "position"
        dump.append(dump_row(f"@t:{i}", None, "Рудь", tier=tier))
    record = json.loads(json.dumps(RECORD))
    record["outcomes"] = outcomes
    return record, dump, readings


def test_bar_three_scores_the_readable_rows_and_takes_the_highest_rung():
    record, dump, readings = text_fixture(20, wrong=3)
    dump.append(dump_row("@t:0", None, "Ласунка", tier="brand_mention"))  # same row, lower rung
    bar = verdicts.bar_three(record, dump, PREREG, readings)
    assert bar["n_scored"] == 20 and bar["unreadable"]["n"] == 0
    assert bar["value"] == pytest.approx(0.85) and bar["verdict"] == "PASS"
    assert bar["confusion"] == {"position -> position": 17, "position -> product_mention": 3}


def test_bar_three_excludes_unreadable_replies_and_counts_them_by_reason():
    record, dump, readings = text_fixture(22, unreadable=2)
    bar = verdicts.bar_three(record, dump, PREREG, readings)
    # 2 of 22 is 9.1%, under the 10% ceiling, and the 20 that answered are scored
    assert bar["unreadable"] == {
        "rule": PREREG["bars"]["text_tier_accuracy"]["unreadable_rows"],
        "n": 2,
        "share": pytest.approx(0.0909, abs=1e-4),
        "max_share": 0.10,
        "by_reason": {"malformed JSON": 2},
        "ids": ["@t:0", "@t:1"],
    }
    assert bar["n_scored"] == 20 and bar["verdict"] == "PASS" and bar["value"] == 1.0


def test_bar_three_is_not_scored_when_too_many_replies_were_unreadable():
    record, dump, readings = text_fixture(30, unreadable=4)
    bar = verdicts.bar_three(record, dump, PREREG, readings)
    assert bar["unreadable"]["share"] == pytest.approx(4 / 30, abs=1e-4)  # 0.1333, as recorded
    assert (
        bar["verdict"] == "NOT_SCORED" and "the instrument did not answer" in bar["why_not_scored"]
    )
    assert bar["value"] == 1.0  # still computed and reported, just not a verdict


def test_bar_three_is_not_scored_below_the_registered_floor_of_twenty_rows():
    record, dump, readings = text_fixture(19)
    bar = verdicts.bar_three(record, dump, PREREG, readings)
    assert bar["verdict"] == "NOT_SCORED" and "floor of 20" in bar["why_not_scored"]


def test_bar_three_refuses_a_text_row_that_is_not_in_the_adjudicated_pack():
    record, dump, readings = text_fixture(20)
    with pytest.raises(SystemExit, match="not in the adjudicated pack"):
        verdicts.bar_three(record, dump, PREREG, readings[:-1])


# --- the guards, and the whole write path ------------------------------------


def fixture_tree(tmp_path: Path, *, b_prime: bool = False, **record_overrides) -> dict:
    """Every file `main` reads, written to `tmp_path` with its shas wired up.

    `b_prime` switches the two files to the shape skub2 actually writes: a registration whose gold
    is its own `per_post` and whose population is not a resume, and a record with no resume block.
    Three things in `main` read those fields and every one of them would raise a KeyError.
    """
    rows = [
        {
            **{key: "" for key in builder.COLUMNS},
            "id": f"@t:{i}",
            "channel": "@t",
            "carrier": "post_text",
            "date": "2026-01-01T00:00:00+00:00",
            "hit": "brand:rud",
            "pattern": "5%",
            "text": f"row {i}",
            "brand": "y",
            "category": "y",
            "size": "y",
        }
        for i in range(20)
    ]
    pack_path = tmp_path / "text20.csv"
    with pack_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=builder.COLUMNS, delimiter=builder.DELIMITER)
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "pack": str(pack_path),
        "ids": [row["id"] for row in rows],
        "given_sha256": builder.given_sha256(rows),
        "ladder": {"sha256": positions.ladder_sha256()},
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    reference_path = tmp_path / "reference.json"
    reference_path.write_text(json.dumps(REFERENCE, ensure_ascii=False), encoding="utf-8")
    dump_path = tmp_path / "dump.jsonl"
    dump = DUMP[:-1] + [dump_row(f"@t:{i}", None, "Рудь") for i in range(20)]
    dump_path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in dump), "utf-8")

    prereg = json.loads(json.dumps(PREREG))
    prereg["bars"]["leaflet_brand_recall"]["gold"]["sha256"] = hashlib.sha256(
        reference_path.read_bytes()
    ).hexdigest()
    prereg["bars"]["text_tier_accuracy"]["gold"]["manifest"] = str(manifest_path)
    prereg["bars"]["text_tier_accuracy"]["gold"]["manifest_sha256"] = hashlib.sha256(
        manifest_path.read_bytes()
    ).hexdigest()
    prereg["resume"]["population"]["registered"] = 24
    if b_prime:
        as_b_prime(prereg)  # after the shas are wired: it moves the one it finds, never invents it
    prereg_path = tmp_path / "prereg.json"
    prereg_path.write_text(json.dumps(prereg, ensure_ascii=False), encoding="utf-8")

    record = json.loads(json.dumps(RECORD))
    record["outcomes"] = RECORD["outcomes"][:4] + [
        outcome(f"@t:{i}", f"@t:{i}", "text", "post_text") for i in range(20)
    ]
    record["population"] = {"unbought": 0, "asked": 24}
    record["prereg"] = {"path": str(prereg_path), "sha256": prereg["_sha"] if False else ""}
    record["dump"] = {
        "path": str(dump_path),
        "sha256": hashlib.sha256(dump_path.read_bytes()).hexdigest(),
        "rows": len(dump),
        "columns": [],
    }
    if not b_prime:
        record["resume"] = {"sessions": ["sku-b", "sku-b-v3"]}
    record["prereg"]["sha256"] = hashlib.sha256(prereg_path.read_bytes()).hexdigest()
    record.update(record_overrides)
    record_path = tmp_path / "record.json"
    record_path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
    return {
        "record": record_path,
        "prereg": prereg_path,
        "reference": reference_path,
        "dump": dump_path,
        # not written: every test below that wants a scored bar 2 writes it deliberately, so the
        # default `--pairs` can never reach the real read and score a synthetic dump with it
        "pairs": tmp_path / "pairs.json",
        "out": tmp_path / "verdicts.json",
    }


def run(tree: dict, **extra) -> int:
    argv = [
        "--record", str(tree["record"]),
        "--prereg", str(tree["prereg"]),
        "--reference", str(tree["reference"]),
        "--pairs", str(tree["pairs"]),
        "--out", str(tree["out"]),
    ]  # fmt: skip
    return verdicts.main(argv + [item for pair in extra.items() for item in pair])


def test_main_writes_all_three_bars_from_the_files_it_was_given(tmp_path, capsys):
    tree = fixture_tree(tmp_path)
    assert run(tree) == 0
    out = json.loads(tree["out"].read_text(encoding="utf-8"))
    assert set(out["bars"]) == {
        "leaflet_brand_recall",
        "price_pair_accuracy",
        "text_tier_accuracy",
    }
    assert out["bars"]["leaflet_brand_recall"]["value"] == pytest.approx(0.5)
    assert out["bars"]["text_tier_accuracy"]["verdict"] == "PASS"
    assert out["bars"]["price_pair_accuracy"]["verdict"] == "PENDING_TEAM_LEAD"
    assert out["record"]["sha256"] and out["pins"]["dump"]["sha256"]
    assert "FAIL" in capsys.readouterr().out


def test_main_writes_the_bars_from_a_registration_with_no_resume_block(tmp_path, capsys):
    """The shape skub2 writes, end to end (Dv210). Three readers used to assume a resume block.

    Bar 1 comes out 1.0 here against 0.5 on the same files under the reference's gold, which is the
    proof the re-scope reached the arithmetic and not just the file. The population count comes
    from `population.elements` instead of `resume.population.registered`, and `sessions` names the
    one session out of the registration rather than KeyError-ing on a record that has none.
    """
    tree = fixture_tree(tmp_path, b_prime=True)
    assert run(tree) == 0
    out = json.loads(tree["out"].read_text(encoding="utf-8"))
    assert out["bars"]["leaflet_brand_recall"]["value"] == pytest.approx(1.0)
    assert out["bars"]["leaflet_brand_recall"]["verdict"] == "PASS"
    assert out["bars"]["leaflet_brand_recall"]["n_posts"] == 1
    assert out["sessions"] == [
        {
            "phase": "fixture",
            "record": str(tree["record"]),
            "asked": 24,
            "note": out["sessions"][0]["note"],
        }
    ]
    assert "no resume block" in out["sessions"][0]["note"]
    assert out["closure"]["rule_source"].startswith(f"{tree['prereg']} attempts.on_failure")
    assert "PASS" in capsys.readouterr().out

    # and the count still has to be met: 24 registered, 24 asked, and 23 is a refusal
    (tmp_path / "short").mkdir()
    short = fixture_tree(tmp_path / "short", b_prime=True)
    record = json.loads(short["record"].read_text(encoding="utf-8"))
    record["outcomes"] = record["outcomes"][:-1]
    short["record"].write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(SystemExit, match="23 outcomes over 23 distinct sources against the"):
        run(short)


def test_main_refuses_a_gold_that_moved_under_the_registration(tmp_path):
    tree = fixture_tree(tmp_path)
    tree["reference"].write_text(json.dumps(REFERENCE, ensure_ascii=False) + "\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="leaflet gold .* hashes"):
        run(tree)


def test_main_refuses_a_dump_that_is_not_the_records_own(tmp_path):
    tree = fixture_tree(tmp_path)
    tree["dump"].write_text(tree["dump"].read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="dump .* hashes"):
        run(tree)


def test_main_refuses_a_population_that_is_still_half_bought(tmp_path):
    tree = fixture_tree(tmp_path, population={"unbought": 3, "asked": 24})
    with pytest.raises(SystemExit, match="3 element\\(s\\) are still unbought"):
        run(tree)


def test_main_refuses_a_population_whose_elements_do_not_land_exactly_once(tmp_path):
    tree = fixture_tree(tmp_path)
    record = json.loads(tree["record"].read_text(encoding="utf-8"))
    record["outcomes"].append(dict(record["outcomes"][-1]))
    tree["record"].write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(SystemExit, match="exactly once"):
        run(tree)


def test_a_smoke_record_cannot_be_written_to_the_paid_verdict_path(tmp_path):
    tree = fixture_tree(tmp_path, smoke=True)
    argv = [
        "--record", str(tree["record"]),
        "--prereg", str(tree["prereg"]),
        "--reference", str(tree["reference"]),
        "--out", str(verdicts.OUT),
    ]  # fmt: skip
    with pytest.raises(SystemExit, match="smoke record cannot be written to the paid verdict path"):
        verdicts.main(argv)


def test_the_defaults_and_the_provenance_string_name_the_skub2_session(tmp_path):
    """Dv170, third session running: this producer named v3 once and v4 once, and the string it
    writes into the record is the part nothing re-derives.

    `--prereg` and `--record` are loud — a record bought under another registration is refused by
    name. The `contract` string is not: it is written INTO the verdict record the team lead opens
    at acceptance. So it is pinned against the registration it claims (whose own `attempts.phase`
    says which session bought the population) and against the contract file being in the tree.

    The six defaults are checked together because they move together: a run scored with B′'s
    registration and v4's output path would overwrite the pilot's closure, and one scored with v4's
    pair read would refuse — the read is over another dump.
    """
    prereg = json.loads(verdicts.PREREG.read_text(encoding="utf-8"))
    assert prereg["attempts"]["phase"] == "skub2"
    assert verdicts.PREREG.name == "sku_pilot_prereg_b2.json"
    assert verdicts.RECORD.name == "sku_b_positions_skub2.json"
    assert verdicts.PAIRS.name == "sku_b_pair_verdicts_skub2.json"
    assert verdicts.OUT.name == "sku_bar_verdicts_skub2.json"
    assert verdicts.SMOKE_OUT.name == verdicts.OUT.name and verdicts.SMOKE_OUT != verdicts.OUT
    # the pilot's sealed evidence, which these defaults must not be able to reach
    for sealed in ("sku_bar_verdicts.json", "sku_b_pair_verdicts.json", "sku_b_positions_v4.json"):
        assert (REPO_ROOT / "results" / sealed).exists()
        assert sealed not in {path.name for path in (verdicts.OUT, verdicts.PAIRS, verdicts.RECORD)}

    # both contracts, because the record is now written under the second one: the run bought the
    # population and scored two bars, the close applied the third and took the closure
    for named in ("docs/PROMPT-skub2-close.md", "docs/PROMPT-skub2-run.md"):
        assert named in verdicts.CONTRACT
    named = verdicts.CONTRACT.split()[0]
    assert (REPO_ROOT / named).exists(), f"the provenance string names {named}, which is not here"
    # (13) and (14) are what this population is bought under; (11) is the resume reading and (12)
    # is v4's amendment, and a record that still cited them would be citing a superseded run.
    assert all(part in verdicts.CONTRACT for part in ("(6)", "(13)", "(14)"))
    assert not any(part in verdicts.CONTRACT for part in ("v3", "v4", "(11)", "(12)"))

    tree = fixture_tree(tmp_path)
    assert run(tree) == 0
    assert json.loads(tree["out"].read_text(encoding="utf-8"))["contract"] == verdicts.CONTRACT


def test_main_scores_bar_two_from_the_read_and_states_the_closure(tmp_path):
    """The whole write path with the read on disk: bar 2 gets a value and the closure fires.

    Bar 1 fails on this fixture and bar 3 passes, so writing a failing bar 2 beside them puts two
    FAILs in the record — the shape the pilot actually closed in — and the closure has to name both
    of them and neither of the others.
    """
    tree = fixture_tree(tmp_path)
    record = json.loads(tree["record"].read_text(encoding="utf-8"))
    read = pair_read(record["dump"]["sha256"], [("correct", 1), ("wrong", 1)])
    tree["pairs"].write_text(json.dumps(read, ensure_ascii=False), encoding="utf-8")

    assert run(tree) == 0
    out = json.loads(tree["out"].read_text(encoding="utf-8"))
    two = out["bars"]["price_pair_accuracy"]
    assert two["value"] == pytest.approx(0.5) and two["verdict"] == "FAIL"
    assert two["read"]["path"] == str(tree["pairs"])
    assert two["read"]["sha256"] == hashlib.sha256(tree["pairs"].read_bytes()).hexdigest()
    assert two["read"]["diagnosis"] == "the kopiyky are the whole error"

    assert out["closure"]["failed_bars"] == ["leaflet_brand_recall", "price_pair_accuracy"]
    assert out["closure"]["passed_bars"] == ["text_tier_accuracy"]
    assert out["closure"]["state"].startswith("CLOSED")
    assert out["closure"]["rule"] == PREREG["attempts"]["on_failure"]


def test_the_closure_names_the_bars_that_failed_and_waits_on_one_that_has_no_verdict():
    """Derived from the verdicts, not restated: the registration's rule says "a failed bar" in the
    singular and the pilot failed two, so the list has to come from the data. And two thirds of the
    evidence is not a closure — a bar still pending leaves the state UNDETERMINED."""
    bars = {"a": {"verdict": "FAIL"}, "b": {"verdict": "PASS"}, "c": {"verdict": "FAIL"}}
    closed = verdicts.closure(bars, PREREG, "results/fixture.json")
    assert closed["failed_bars"] == ["a", "c"] and closed["passed_bars"] == ["b"]
    assert closed["state"].startswith("CLOSED") and "2 of 3 bars failed" in closed["why"]
    assert closed["rule"] == PREREG["attempts"]["on_failure"]
    # the source is the registration that was read, not a literal — three of them have been live
    assert closed["rule_source"].startswith("results/fixture.json attempts.on_failure")

    waiting = verdicts.closure(
        {**bars, "c": {"verdict": "PENDING_TEAM_LEAD"}}, PREREG, "results/fixture.json"
    )
    assert waiting["state"] == "UNDETERMINED" and waiting["undecided_bars"] == ["c"]
    assert (
        verdicts.closure({"a": {"verdict": "PASS"}}, PREREG, "results/fixture.json")["state"]
        == "NOT CLOSED BY THIS RULE"
    )


def test_the_shipped_v4_run_has_a_read_to_score_and_does_not_fall_back_to_pending():
    """The v4 pilot's own read and closure, named by path rather than through the defaults.

    Bar 2 falls back to PENDING when its read is missing and still writes the record, so the
    existence of that file is the guard. It is spelled out here instead of read off
    `verdicts.PAIRS`/`verdicts.OUT` because those now point at skub2: this test guards the SEALED
    pilot, and a test that follows the defaults would have followed them to a file that does not
    exist yet and passed by moving.
    """
    pairs = REPO_ROOT / "results" / "sku_b_pair_verdicts.json"
    verdict_record = REPO_ROOT / "results" / "sku_bar_verdicts.json"
    assert pairs.exists(), f"{pairs} is the read v4's bar 2 is scored from"
    read = json.loads(pairs.read_text(encoding="utf-8"))
    assert read["checksums"] == {
        "keys": 45,
        "rows": 61,
        "correct_rows": 20,
        "wrong_rows": 41,
        "accuracy": pytest.approx(20 / 61),
        "accuracy_4dp": 0.3279,
    }
    shipped = json.loads(verdict_record.read_text(encoding="utf-8"))
    assert shipped["bars"]["price_pair_accuracy"]["verdict"] == "FAIL"
    assert shipped["closure"]["failed_bars"] == ["leaflet_brand_recall", "price_pair_accuracy"]


def test_highest_tier_takes_the_best_rung_and_names_an_empty_answer():
    assert verdicts.highest_tier(["brand_mention", "position", "product_mention"]) == "position"
    assert verdicts.highest_tier(["brand_mention", "product_mention"]) == "product_mention"
    assert verdicts.highest_tier([]) == "none"


def test_main_refuses_the_record_of_a_session_that_stopped_before_gold(tmp_path):
    """The likeliest record anyone will point this at, and it used to crash on `REPO_ROOT / None`.

    Measured on sku-b-v3: the (10)(a) go/no-go refused, so the session wrote a record with
    `dump.path: None` and no answers at all. A producer that dies with a TypeError there says
    nothing about why; the control below is the same record with the flag cleared, which gets past
    this guard and fails on the pins instead.
    """
    tree = fixture_tree(tmp_path, stopped_before_gold=True)
    with pytest.raises(SystemExit, match="stopped before the first gold call"):
        run(tree)
    assert run(fixture_tree(tmp_path, stopped_before_gold=False)) == 0


def test_bar_three_leaves_the_rows_the_operator_never_touched_out_of_the_denominator():
    """The bar's registered denominator: "a row the operator left untouched is not gold and is not
    counted". `tier_from_presence` reads five blank cells as `none`, which is ALSO a legitimate
    answer — so an unfinished pack would score its blanks as agreements with every empty model
    reply and read as a bar that passed. The validator returns 0 on an unfinished pack, so nothing
    upstream refuses either.

    The control is the same fixture fully adjudicated: 22 rows in, 22 scored."""
    record, dump, readings = text_fixture(22)
    for reading in readings[:2]:  # blank ticks, blank notes: never answered
        reading.update(ticks={"brand": False}, notes="", tier="none")
    bar = verdicts.bar_three(record, dump, PREREG, readings)
    assert bar["not_gold"]["n"] == 2 and bar["not_gold"]["ids"] == ["@t:0", "@t:1"]
    assert bar["n_scored"] == 20 and bar["n_asked"] == 20
    assert bar["unreadable"]["n"] == 0, "untouched is not unreadable — different exclusions"

    whole = verdicts.bar_three(*text_fixture(22)[:2], PREREG, text_fixture(22)[2])
    assert whole["not_gold"]["n"] == 0 and whole["n_scored"] == 22


def test_the_untouched_rule_is_the_validators_own_predicate():
    """One rule, two readers. A note with no tick is still an adjudication — the operator writing
    «пусто» has answered "this row names no position", which is what `none` means."""
    assert pack.is_adjudicated({"ticks": {"brand": True}, "notes": ""})
    assert pack.is_adjudicated({"ticks": {"brand": False}, "notes": "пусто"})
    assert not pack.is_adjudicated({"ticks": {"brand": False}, "notes": ""})
