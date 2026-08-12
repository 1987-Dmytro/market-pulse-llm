"""The sku-b bar producer: hand-computed arithmetic, and the refusals that guard it.

Every fixture here is synthetic and small enough to check on paper. The one thing that cannot be
checked on paper is the key space the two halves of bar 1 arrive in — the gold carries the
reviewer's brands and the dump carries the model's — so that gets its own test with a control.
"""

import csv
import hashlib
import json
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

ALIASES = watchlist_aliases(load_registry(REPO_ROOT / "config" / "registry.yaml").watchlist)

PREREG = {
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
#   @a:1  gold {raw:rud, raw:каштан}   model reads Рудь on page 1, Каштан on page 2 -> 2/2 = 1.0
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
            "item": "@a:1",
            "brands_visible": {"gold_keys": ["raw:rud", "raw:каштан"]},
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
    assert probe[0]["false_positives"] == ["raw:limo"]


def test_bar_one_puts_a_resolved_watchlist_brand_in_the_reviewers_key_space():
    """The trap: the reviewer names ids, the model names printed text, and both go through
    `gold_key`. «Рудь» resolves to the watchlist id `rud`, whose gold key is `raw:rud` — because
    `rud` is not a display name and the alias table is keyed on display names.

    The control is a brand OFF the watchlist: «Каштан» never resolves, and its key is built from
    the printed name. Two different routes into one space; if either changed, one of these two
    posts would silently read 0.5 instead of 1.0.
    """
    bar = verdicts.bar_one(RECORD, DUMP, PREREG, REFERENCE, ALIASES)
    found = bar["per_post"][0]
    assert positions.resolve_brand("Рудь", ALIASES) == "rud"  # resolved…
    assert positions.resolve_brand("Каштан", ALIASES) is None  # …and not resolved
    assert found["extracted"] == ["raw:rud", "raw:каштан"] == found["found"]
    assert found["missed"] == [] and found["not_in_gold"] == []


def test_bar_one_refuses_when_the_reference_and_the_ratified_exclusions_disagree():
    prereg = json.loads(json.dumps(PREREG))
    prereg["bars"]["leaflet_brand_recall"]["excluded"]["posts"] = ["@a:1"]
    with pytest.raises(SystemExit, match="not the ones R3 excludes"):
        verdicts.bar_one(RECORD, DUMP, prereg, REFERENCE, ALIASES)


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


def test_bar_two_counts_leaflet_pairs_only_and_never_scores_them():
    bar = verdicts.bar_two(RECORD, DUMP, PREREG)
    assert bar["n_pairs"] == 2  # the text row's price_old is not a leaflet pair
    assert bar["value"] is None and bar["verdict"] == "PENDING_TEAM_LEAD"
    assert bar["reachability"]["class"] == "REPORTED_NOT_SCORED"
    assert verdicts.bar_two(RECORD, DUMP * 5, PREREG)["reachability"]["class"] == "SCOREABLE"
    assert verdicts.bar_two(RECORD, [], PREREG)["reachability"]["class"] == "NOT_REACHABLE"


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


def fixture_tree(tmp_path: Path, **record_overrides) -> dict:
    """Every file `main` reads, written to `tmp_path` with its shas wired up."""
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
        "out": tmp_path / "verdicts.json",
    }


def run(tree: dict, **extra) -> int:
    argv = [
        "--record", str(tree["record"]),
        "--prereg", str(tree["prereg"]),
        "--reference", str(tree["reference"]),
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


def test_the_defaults_and_the_provenance_string_name_the_v4_session(tmp_path):
    """Dv170: this producer named v3 in three places and one of them was unguarded.

    `--prereg` and `--record` are loud — a record bought under another registration is refused by
    name. The `contract` string is not: it is written INTO the verdict record the team lead opens
    at acceptance and nothing re-derives it. So it is pinned against the registration it claims
    (the v4 one, whose own `attempts.phase` says which session bought the second half of the
    population) and against the contract file being in the tree, not restated as a literal.
    """
    prereg = json.loads(verdicts.PREREG.read_text(encoding="utf-8"))
    assert prereg["attempts"]["phase"] == "sku-b-v4"
    assert verdicts.PREREG.name == "sku_pilot_prereg_v4.json"
    assert verdicts.RECORD.name == "sku_b_positions_v4.json"

    named = verdicts.CONTRACT.split()[0]
    assert (REPO_ROOT / named).exists(), f"the provenance string names {named}, which is not here"
    # (12) is the amendment the 121 are bought under and the one the v3 string was missing; the
    # superseded contract must not still be the one the record cites.
    assert all(part in verdicts.CONTRACT for part in ("(6)", "(11)", "(12)"))
    assert "v3" not in verdicts.CONTRACT

    tree = fixture_tree(tmp_path)
    assert run(tree) == 0
    assert json.loads(tree["out"].read_text(encoding="utf-8"))["contract"] == verdicts.CONTRACT


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
