"""Offline tests for the post leg's pre-filter census — a fake corpus, and the shipped record.

Two halves, and they check different things. The FIXTURE half drives `main` over a throwaway store
where every count is known by hand, so the arithmetic and the refusals can be measured. The SHIPPED
half walks `results/census_c3a_posts.json` itself — every citation re-resolved, every quote grepped
back, every total re-derived — which is the only way the file the pre-registration will read is held
to the sources it names.
"""

import ast
import hashlib
import json
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import census_c3a_posts as census  # noqa: E402
import yield_screen_5c1 as screen  # noqa: E402

from market_pulse.registry import Source, load_registry  # noqa: E402

ANCHOR = "2026-02-01T00:00:00+00:00"
INSIDE = "2026-01-20T12:00:00+00:00"
OUTSIDE = "2025-12-31T12:00:00+00:00"

ATB = Source("atb", "АТБ", "official_retail", ("@atb",), True, False)
VARUS = Source("varus", "Varus", "official_retail", ("@varus",), True, False)
SILENT = Source("silpo", "Сільпо", "official_retail", ("@silpo",), True, False)

PRICED = "Молоко Яготинське 2,5% 900 г — 39,90 грн"
"""A retail offer: a watchlist brand, a category term, a size, a fat percentage AND a price."""

RECIPE = "Сир 200 г, яйця 2 шт, борошно — змішати і випікати 40 хвилин"
"""The same conjunction with no money in it — a category term beside a size, in an ingredient list.
The filter cannot tell it from an offer, which is why `passed_carrying` counts currency separately;
this row is what makes that column mean something in the tests below."""

NOISE = "Графік роботи магазинів у святкові дні. Дякуємо, що ви з нами!"

RULING_LINE = "(`results/post_media_5c1.json`: today 159 pages under 19 posts, all"


def jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )


def post(msg_id: int, date: str, text: str) -> dict:
    return {"record_type": "post", "msg_id": msg_id, "date": date, "text": text}


def wire(monkeypatch, tmp_path, *, sources=(ATB, VARUS, SILENT), pins=None, ruling=RULING_LINE):
    """A throwaway corpus of three channels, with the ratified census's pin faked to match.

    `@silpo` has no posts file at all — the CANNOT ANSWER control, so "never walked" and "walked
    and passed nothing" cannot collapse into one cell. The lexicon and the watchlist are the REAL
    ones: the pre-filter is the instrument under test and a fixture vocabulary would test a
    different one.
    """
    real = load_registry(screen.REGISTRY)
    jsonl(
        tmp_path / "posts" / "atb.jsonl",
        [
            post(1, INSIDE, PRICED),
            post(2, INSIDE, RECIPE),
            post(3, INSIDE, NOISE),
            post(4, OUTSIDE, PRICED),
        ],
    )
    jsonl(tmp_path / "posts" / "varus.jsonl", [post(10, INSIDE, RECIPE)])
    if pins is None:
        pins = {"@atb": census.ids_sha256([1, 2, 3]), "@varus": census.ids_sha256([10])}
    (tmp_path / "census_5c2.json").write_text(
        json.dumps(
            {
                "channels": [
                    {"handle": handle, "posts": {"ids_sha256": sha}} for handle, sha in pins.items()
                ]
                + [{"handle": "@silpo", "posts": census.c2.CANNOT_ANSWER}]
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "post_media.json").write_text(
        json.dumps(
            {
                "entries": {
                    "@atb:1": {
                        "channel": "@atb",
                        "msg_id": 1,
                        "date": INSIDE,
                        "images": [{"msg_id": 1, "file": "a.jpg"}, {"msg_id": 2, "file": "b.jpg"}],
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "SPEC.md").write_text(f"a clause\n{ruling}\nanother line\n", encoding="utf-8")
    monkeypatch.setattr(census, "POSTS", tmp_path / "posts")
    monkeypatch.setattr(census, "CENSUS_5C2", tmp_path / "census_5c2.json")
    monkeypatch.setattr(census, "POST_MEDIA", tmp_path / "post_media.json")
    monkeypatch.setattr(census, "SPEC", tmp_path / "SPEC.md")
    monkeypatch.setattr(
        census,
        "load_registry",
        lambda _: type(
            "R",
            (),
            {"sources": list(sources), "taxonomy": real.taxonomy, "watchlist": real.watchlist},
        )(),
    )


def run(tmp_path, out="census.json", anchor=ANCHOR, expect=0) -> dict:
    assert census.main(["--anchor", anchor, "--out", str(tmp_path / out)]) == expect
    return json.loads((tmp_path / out).read_text(encoding="utf-8"))


def channel(record: dict, handle: str) -> dict:
    return next(row for row in record["channels"] if row["handle"] == handle)


# --- the fixture half: counts known by hand ---------------------------------------------------


def test_only_the_rows_the_conjunction_passes_are_counted(monkeypatch, tmp_path):
    """Four ATB posts, one of them outside the window, one of them noise: two pass."""
    wire(monkeypatch, tmp_path)
    record = run(tmp_path)

    assert record["totals"]["posts_in_window"] == 4  # three ATB + one VARUS
    assert record["totals"]["passed"] == 3
    assert sorted(entry["id"] for entry in record["rows"]) == ["@atb:1", "@atb:2", "@varus:10"]
    assert channel(record, "@atb")["passed"] == 2


def test_a_priced_row_and_a_recipe_row_are_told_apart_by_the_currency_column(monkeypatch, tmp_path):
    """The filter passes both — a category term beside a size is its whole rule — and only
    `passed_carrying.currency` says which one has money in it. Without this column «349 posts
    pass» reads as «349 retail offers»."""
    wire(monkeypatch, tmp_path)
    record = run(tmp_path)

    assert record["totals"]["passed_carrying"] == {"currency": 1, "percent": 1, "size": 3}
    assert record["totals"]["passed"] == 3


def test_the_evidence_line_is_kept_for_every_passing_row(monkeypatch, tmp_path):
    """SPEC 3.18 (7)(e) names the frame as "the matched line kept as evidence" — so a row that
    cannot show the line that fired is not one of these rows."""
    wire(monkeypatch, tmp_path)
    record = run(tmp_path)

    for entry in record["rows"]:
        assert set(entry) >= {"id", "date", "line", "hit", "matched", "pattern", "carrier"}
        # casefolded: `yield_screen`'s matchers lower-case what they return, and the line is
        # kept as it was written — the point of the evidence is that a human can read it
        assert entry["matched"] in entry["line"].casefold()
        assert entry["carrier"] == "post_text"


def test_a_channel_with_no_posts_file_says_cannot_answer_and_is_not_zero(monkeypatch, tmp_path):
    wire(monkeypatch, tmp_path)
    record = run(tmp_path)

    assert record["cannot_answer"]["channels"] == ["@silpo"]
    assert "@silpo" not in {row["handle"] for row in record["channels"]}


def test_the_selection_pin_agrees_with_the_ratified_census(monkeypatch, tmp_path):
    wire(monkeypatch, tmp_path)
    record = run(tmp_path)

    assert record["selection_pin"]["agrees"] is True
    assert record["selection_pin"]["disagreements"] == []
    assert all(row["matches_census_5c2"] for row in record["channels"])


def test_a_pin_that_names_other_rows_is_reported_and_the_run_refuses(monkeypatch, tmp_path):
    """The negative control for the test above, and the reason the pin is a HASH and not a count:
    the same number of posts, a different set of them, and only the sha can see it."""
    wire(monkeypatch, tmp_path, pins={"@atb": census.ids_sha256([1, 2, 99]), "@varus": "nope"})
    record = run(tmp_path, expect=1)

    assert record["selection_pin"]["agrees"] is False
    assert record["selection_pin"]["disagreements"] == ["@atb", "@varus"]


def test_the_same_anchor_reproduces_the_artifact_byte_for_byte(monkeypatch, tmp_path):
    """This record's own gate — it holds only because nothing here reads the clock."""
    wire(monkeypatch, tmp_path)
    run(tmp_path, "first.json")
    run(tmp_path, "second.json")

    assert (tmp_path / "first.json").read_bytes() == (tmp_path / "second.json").read_bytes()


def test_the_record_carries_no_clock_of_its_own(monkeypatch, tmp_path):
    """Both halves, `census_5c2`'s pattern: no `generated_at` in the record, and no clock CALL in
    the module. Read off the AST because the docstrings argue about `datetime.now()` in prose."""
    wire(monkeypatch, tmp_path)
    record = run(tmp_path)

    assert "generated_at" not in record and "timestamp" not in record
    tree = ast.parse(Path(census.__file__).read_text(encoding="utf-8"))
    called = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert not called & {"now", "utcnow", "today", "time"}


def test_the_record_carries_no_git_state_and_names_its_producer(monkeypatch, tmp_path):
    """`git_state` embeds `git status --porcelain`, so a record carrying it moves when an unrelated
    file is committed — which is the byte-identity gate above, voided. Note this module IMPORTS
    `sku_prefilter_census`, which calls `git_state` in its own record; what has to hold is that
    THIS module does not."""
    wire(monkeypatch, tmp_path)
    record = run(tmp_path)

    assert "git" not in record
    assert (
        record["producer"]["sha256"]
        == hashlib.sha256(Path(census.__file__).read_bytes()).hexdigest()
    )
    tree = ast.parse(Path(census.__file__).read_text(encoding="utf-8"))
    assert not [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "git_state"
    ]


def test_a_rerun_under_another_anchor_refuses_to_take_the_records_name(monkeypatch, tmp_path):
    """D68 narrowed to the anchor: a re-run under the SAME one is the determinism gate and must be
    allowed; a different window under the name the ruling cites is what gets stopped."""
    wire(monkeypatch, tmp_path)
    run(tmp_path)

    with pytest.raises(SystemExit, match="A different window is a different population"):
        run(tmp_path, anchor="2026-03-01T00:00:00+00:00")
    assert run(tmp_path)["anchor"]["anchor"] == ANCHOR


def test_the_leaflet_corpus_is_counted_from_the_manifest_and_agrees_with_the_clause(
    monkeypatch, tmp_path
):
    """Two readings of one population: the manifest counted, and 3.18 (7)(d)'s own sentence quoted
    beside it. The clause is the authority on the RULE and the file is the authority on the NUMBER."""
    wire(monkeypatch, tmp_path)
    record = run(tmp_path)

    assert record["leaflet_corpus"]["pages"] == 2 and record["leaflet_corpus"]["posts"] == 1
    assert record["leaflet_corpus"]["ruling"]["quote"] == RULING_LINE.strip()


def test_a_ruling_line_that_moved_stops_the_run_instead_of_being_quoted_loosely(
    monkeypatch, tmp_path
):
    """`quote_line` refuses on anything but exactly one match — the defect that shipped once in
    prep-c2, where a loose needle quoted a true line about something else."""
    wire(monkeypatch, tmp_path, ruling="a clause with no page count in it")

    with pytest.raises(SystemExit, match="a quote is one line"):
        run(tmp_path)


def test_the_price_is_the_count_times_the_paid_marginal_plus_one_idle_tail(monkeypatch, tmp_path):
    """Recomputed by hand from the record's own three inputs. No boot: 3.18 (7)(c) buys the window
    in ONE session and results/projection_5c2.json already pays for one."""
    wire(monkeypatch, tmp_path)
    record = run(tmp_path)

    priced, rate = record["priced"], record["rate"]["value"]
    seconds = priced["rows"] * priced["seconds_per_row"] + 60.0
    assert priced["rows"] == record["totals"]["passed"]
    assert priced["billed_seconds"] == round(seconds, 1)
    assert priced["usd_with_drift"] == round(seconds * rate * 1.03, 4)


def test_the_controls_are_taken_before_the_yield_is_read(monkeypatch, tmp_path):
    """One positive and three negatives from `sku_prefilter_census`, reused rather than rewritten:
    without them «this channel passed 0 rows» and «the filter passes nothing» look the same."""
    wire(monkeypatch, tmp_path)
    record = run(tmp_path)

    assert record["population_reportable"] is True
    assert len(record["controls"]) == 4
    assert all(control["ok"] for control in record["controls"].values())
    assert sum(1 for c in record["controls"].values() if c["kind"] == "negative") == 3


# --- the shipped half: the record the pre-registration will read ------------------------------

RECORD = json.loads(census.RECORD.read_text(encoding="utf-8"))


def dig(data, dotted: str):
    """A second implementation of `projection.dig`, on purpose: two readers, one source string."""
    for step in re.findall(r"[^.\[\]]+|\[-?\d+\]", dotted):
        data = data[int(step[1:-1])] if step.startswith("[") else data[step]
    return data


def walk(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk(value)


def test_the_shipped_record_cites_and_quotes_at_all():
    """The negative control for the two loops below: an empty walk would pass them both."""
    assert len([n for n in walk(RECORD) if "source" in n and "value" in n]) >= 1
    assert len([n for n in walk(RECORD) if "source" in n and "quote" in n]) >= 2


def test_every_cited_number_in_the_shipped_record_is_the_one_its_file_holds():
    for node in walk(RECORD):
        if "source" in node and "value" in node:
            path, _, dotted = node["source"].partition(" :: ")
            assert (REPO_ROOT / path).exists(), f"{path} is cited and not on disk"
            found = dig(json.loads((REPO_ROOT / path).read_text(encoding="utf-8")), dotted)
            assert found == node["value"], f"{node['source']}: record {node['value']}, file {found}"


def test_every_quoted_line_in_the_shipped_record_is_in_the_file_it_names():
    for node in walk(RECORD):
        if "source" in node and "quote" in node:
            path = REPO_ROOT / node["source"]
            assert path.exists(), f"{node['source']} is quoted and not on disk"
            lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
            assert node["quote"] in lines, f"{node['source']} no longer holds: {node['quote']}"


def test_the_shipped_record_is_the_ratified_window_and_says_so_by_sha():
    """The pin, on the real pair: same anchor, and every channel's in-window post ids hashing to
    what census_5c2 recorded. A count would not see a store that moved under a later re-run."""
    ratified = json.loads(census.CENSUS_5C2.read_text(encoding="utf-8"))

    assert RECORD["anchor"]["anchor"] == ratified["anchor"]["anchor"] == "2026-08-09T00:00:00+00:00"
    assert (
        RECORD["selection_pin"]["census_5c2_sha256"]
        == hashlib.sha256(census.CENSUS_5C2.read_bytes()).hexdigest()
    )
    assert RECORD["selection_pin"]["agrees"] is True
    assert RECORD["totals"]["posts_in_window"] == ratified["totals"]["posts_in_window"] == 9158


def test_the_shipped_totals_are_the_sum_of_the_shipped_rows():
    """The table and the enumeration, checked against each other — a total in a record is a claim
    until something adds the rows up."""
    rows = RECORD["channels"]

    assert sum(row["passed"] for row in rows) == RECORD["totals"]["passed"] == len(RECORD["rows"])
    assert sum(row["posts_in_window"] for row in rows) == RECORD["totals"]["posts_in_window"]
    assert (
        RECORD["frame"]["ids_sha256"]
        == hashlib.sha256(
            "\n".join(entry["id"] for entry in RECORD["rows"]).encode("utf-8")
        ).hexdigest()
    )
    assert RECORD["totals"]["channels_with_a_pass"] == sum(1 for row in rows if row["passed"])


def test_the_shipped_leaflet_corpus_is_the_population_3_18_7_d_names():
    """159 pages under 19 posts, ATB only — re-counted from the manifest, not restated from the
    clause. The clause is quoted in the same block and this is what holds the two together."""
    corpus = RECORD["leaflet_corpus"]
    manifest = json.loads((REPO_ROOT / corpus["manifest"]["path"]).read_text(encoding="utf-8"))
    entries = list(manifest["entries"].values())

    assert corpus["pages"] == sum(len(entry["images"]) for entry in entries) == 159
    assert corpus["posts"] == len(entries) == 19
    assert corpus["channels"] == ["@atb_market_official"]
    assert "159 pages under 19 posts" in corpus["ruling"]["quote"]


def test_the_shipped_price_is_skub2s_own_text_marginal():
    """Derived through the house function, never typed — `write_sku_projection_b2.text_marginal`
    over skub2's record, which is the rate SPEC 3.18 (7)(e) names for this leg."""
    import write_sku_projection_b2 as b2

    priced = RECORD["priced"]
    assert priced["seconds_per_row"] == b2.text_marginal(
        json.loads((REPO_ROOT / "results" / "sku_b_positions_skub2.json").read_text("utf-8"))
    )
    assert "value" not in priced["derivation"], "a derived number may not wear the citation shape"
    assert priced["rows"] == RECORD["totals"]["passed"]


def test_the_shipped_population_is_mostly_unpriced_lines_and_the_record_shows_it():
    """The finding, pinned so it cannot quietly change: the pre-filter's rule is «a category term
    or a brand AND a size/price pattern», and on THIS window it is satisfied overwhelmingly by
    recipe ingredient lines — 328 of 349 rows carry a size and 29 carry a currency marker. Four
    cooking channels are 71.6% of the population. A pre-registration that reads «349 posts» without
    this column would be buying a recipe corpus.
    """
    carrying = RECORD["totals"]["passed_carrying"]
    top4 = RECORD["concentration"][:4]

    assert RECORD["totals"]["passed"] == 349
    assert carrying["size"] == 328 and carrying["currency"] == 29
    assert carrying["currency"] < RECORD["totals"]["passed"] / 4
    assert top4[-1]["cumulative_share"] == 0.7163
    assert [row["handle"] for row in top4] == [
        "@recepti",
        "@mameni_recepti",
        "@korolevakuchni",
        "@retsepty",
    ]


def test_the_shipped_record_reads_the_same_prefilter_the_pass_answers():
    """The census counts a population and `run_loop.posts_of` queues one. Two instruments would
    make the pre-registration's number and the paid session's queue different sets."""
    import run_loop as runner

    from market_pulse import positions

    assert census.LEXICON == runner.LEXICON
    assert "positions.prefilter" in RECORD["instrument"]["prefilter"]
    tree = ast.parse(Path(runner.__file__).read_text(encoding="utf-8"))
    called = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert "prefilter" in called and callable(positions.prefilter)


def test_the_producer_names_every_module_whose_bytes_reach_the_record():
    """`producer.sha256` hashes THIS script and the record copies another module's docstring into
    `rule` — so the four modules it is built out of are hashed beside it, or an edit in any of them
    moves these bytes with the producer hash sitting still. The class is old: a pin that guards the
    half that cannot move.
    """
    borrows = RECORD["producer"]["borrows"]

    assert set(borrows) == {
        "scripts/census_5c2.py",
        "scripts/sku_prefilter_census.py",
        "scripts/projection_5c2.py",
        "scripts/write_sku_projection_b2.py",
    }
    for path, sha in borrows.items():
        assert hashlib.sha256((REPO_ROOT / path).read_bytes()).hexdigest() == sha, path
    # and the borrowed docstring really is in the record, so this is not a hypothetical
    import sku_prefilter_census as frame_module

    assert RECORD["rule"] == frame_module.__doc__.split("\n\n")[0].strip()


def test_the_cursor_key_is_pinned_independently_of_the_carrier_name():
    """`loop.POST_TEXT` (a cursor key) and `loop.POST_CARRIER` (SPEC 3.17 (4)'s carrier) are the
    same string today and are not the same thing. The module's own docstring says a wrong cursor
    key "does not raise, it silently starts the channel over from nothing" — so a future carrier
    rename must not be able to reset every channel's extraction watermark by sharing a literal.
    """
    from market_pulse import loop

    assert loop.POST_TEXT == "post_text"
    assert loop.POST_CARRIER == "post_text"
    assert loop.POST_TEXT not in (loop.POSTS, loop.INFERENCE, loop.LEAFLET)
