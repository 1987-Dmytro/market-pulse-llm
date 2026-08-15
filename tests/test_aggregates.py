"""The aggregate layer: it converges with the seal, it can fail, and it holds two populations."""

import ast
import json
import sqlite3
import statistics
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_aggregates as builder  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import aggregates  # noqa: E402

ANCHOR = json.loads(builder.ANCHOR.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def conn(tmp_path_factory):
    """The whole window, built once.

    `pulse.db` is gitignored, so no test may read the one `scripts/build_aggregates.py` leaves in
    `data/derived/` — a bare checkout has no such file and the suite has to pass on it. Built into
    `tmp_path` instead, and module-scoped because filling it re-renders 5 075 prompts through
    `prompts.build_messages` to recover what was sent.
    """
    out = tmp_path_factory.mktemp("pulse") / "pulse.db"
    return builder.build(builder.DERIVED, builder.PREREG, builder.REGISTRY, out)


def test_every_number_of_the_sealed_window_summary_is_re_derived_from_sql(conn):
    """The gate of this contract: 902 numeric leaves, both sides READ, none typed here.

    The anchor was written by a different program over the same evidence, so agreeing with it on
    every number — not on four spot checks — is what says the database holds the window rather than
    something shaped like it. `missing` and `extra` are asserted too: a mirror that answered nothing
    would have an empty disagreement list.
    """
    verdict = aggregates.converge(ANCHOR, aggregates.mirror(conn, builder.WINDOW_ID))

    assert verdict["disagreed"] == {}
    assert verdict["missing"] == []
    assert verdict["extra"] == []
    assert len(verdict["agreed"]) == verdict["leaves"] > 900


def test_a_single_flipped_row_reddens_the_gate(tmp_path):
    """The negative control. Built again into its own file — the module fixture is shared and this
    test moves a row.

    One comment's sentiment changes and the disagreement has to reach the TOTAL, the language cut
    and that channel's own block, because a gate that only compared totals would pass on a window
    whose per-channel numbers had been shuffled.
    """
    out = tmp_path / "pulse.db"
    conn = builder.build(builder.DERIVED, builder.PREREG, builder.REGISTRY, out)
    conn.execute(
        "UPDATE comments SET sentiment = 'negative' WHERE rowid ="
        " (SELECT MIN(rowid) FROM comments WHERE sentiment = 'positive')"
    )

    verdict = aggregates.converge(ANCHOR, aggregates.mirror(conn, builder.WINDOW_ID))
    disagreed = verdict["disagreed"]

    assert disagreed["comment.total.sentiment.positive"] == {"anchor": 661, "database": 660}
    assert "comment.total.language.sentiment.ua.positive" in disagreed
    assert any(path.startswith("comment.per_channel.") for path in disagreed)
    with pytest.raises(SystemExit, match="does not converge"):
        builder.check_convergence(conn, builder.ANCHOR)


def test_the_window_row_holds_both_populations_labelled(conn):
    """Collected is not payable — prep-a §1.5 — and the schema says so in two columns.

    Every one of the three numbers is read: the bought count off the sealed registration, the
    text-less count off the anchor, and the payable count out of the database. `3 714` is nowhere in
    this file, because it is nowhere in an artifact either — it is a subtraction.
    """
    bought, payable, text_less = conn.execute(
        "SELECT bought, payable, text_less FROM windows WHERE window_id = ?",
        (builder.WINDOW_ID,),
    ).fetchone()
    seal = json.loads(builder.PREREG.read_text(encoding="utf-8"))

    assert bought == seal["populations"]["comment"]["rows"]
    assert text_less == ANCHOR["comment"]["total"]["empty_text"]["rows"]
    assert payable == bought - text_less
    assert payable == conn.execute("SELECT COUNT(*) FROM comments WHERE has_text = 1").fetchone()[0]


def test_the_two_samples_are_different_distributions(conn):
    """SPEC 3.19 (2): a distribution about words is stated on rows that had words.

    The bought sample is the anchor's and must equal it; the payable one is what the next cycle
    buys. They differ by exactly the text-less rows, and the sentiment of those rows is a real
    answer about nothing — which is why the two blocks are kept apart rather than one corrected.
    """
    bought = aggregates.comment_block(conn, builder.WINDOW_ID, sample="bought")
    payable = aggregates.comment_block(conn, builder.WINDOW_ID, sample="payable")

    assert bought["sentiment"] == ANCHOR["comment"]["total"]["sentiment"]
    assert bought["rows"] - payable["rows"] == bought["empty_text"]["rows"]
    assert payable["empty_text"]["rows"] == 0
    assert payable["sentiment"] != bought["sentiment"]
    assert sum(payable["sentiment"].values()) == payable["scored"]
    with pytest.raises(aggregates.Refusal, match="unknown sample"):
        aggregates.comment_block(conn, builder.WINDOW_ID, sample="all")


def test_the_segment_join_refuses_a_channel_the_registry_does_not_carry(conn):
    """SPEC 3.20 (1)'s loud failure, on the one join that could silently produce a null column."""
    segments = builder.segments_of(summary.load_registry(builder.REGISTRY))

    assert (
        builder.segment_for(segments, {"@matusi_ukr"})["@matusi_ukr"]["segment"] == "mothers_kids"
    )
    with pytest.raises(SystemExit, match=r"\['@nobody'\] carry evidence rows"):
        builder.segment_for(segments, {"@matusi_ukr", "@nobody"})

    everyone = conn.execute("SELECT COUNT(*) FROM channels WHERE segment IS NULL").fetchone()[0]
    assert everyone == 0


def test_a_plan_section_3_cut_is_answered_by_sql(conn):
    """Tonality × segment — the T3 screen's own query, run against the database.

    Demonstrated rather than asserted: the row set is checked to cover the window (its counts sum
    to the scored population) and to carry more than one segment, so a query that had silently
    filtered down to one channel could not pass.
    """
    rows = conn.execute(
        """
        SELECT ch.segment, c.sentiment, COUNT(*) AS rows
          FROM comments c JOIN channels ch USING (window_id, channel)
         WHERE c.window_id = ? AND c.scored = 1
         GROUP BY ch.segment, c.sentiment
         ORDER BY ch.segment, c.sentiment
        """,
        (builder.WINDOW_ID,),
    ).fetchall()

    assert len({segment for segment, _, _ in rows}) >= 5
    assert sum(number for _, _, number in rows) == ANCHOR["comment"]["total"]["scored"]
    per_sentiment: dict[str, int] = {}
    for _, sentiment, number in rows:
        per_sentiment[sentiment] = per_sentiment.get(sentiment, 0) + number
    assert per_sentiment == ANCHOR["comment"]["total"]["sentiment"]


def test_the_spread_is_the_anchor_producers_own_median(conn):
    """One median, two callers. A second implementation is a second answer waiting to happen."""
    values = [0.2, 0.4, 0.41, 0.9]

    assert aggregates.spread(values) == summary._spread(values)
    assert aggregates.spread([]) == {"n": 0, "min": None, "median": None, "max": None}
    assert aggregates.spread(values)["median"] == round(statistics.median(values), 4)


def test_the_layer_reads_nothing_and_parses_nothing(conn):
    """One reader and one parser, checked as a property of the two new files.

    `src/market_pulse/aggregates.py` is handed rows and never opens a path; the driver's readers are
    the summary's own function objects, not copies with the same names. Neither file CALLS a reply
    parser, because the only one is `market_pulse.prompts.parse_reply` and it is reached through
    `window_summary_5c2.comment_verdicts`.

    Checked over the parsed syntax and not over the text: both files NAME `parse_reply` in prose —
    saying where the one parser lives is the point of the docstrings — and a substring test would
    make the documentation the violation.
    """

    def called(path: Path) -> set[str]:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                names.add(node.attr)
            elif isinstance(node, ast.Name):
                names.add(node.id)
        return names

    module = called(REPO_ROOT / "src" / "market_pulse" / "aggregates.py")
    driver = called(REPO_ROOT / "scripts" / "build_aggregates.py")

    assert module & {"open", "read_text", "read_bytes", "parse_reply", "loads"} == set()
    assert "parse_reply" not in driver
    assert "json" in module, "the control: the module does import json, so the check can see it"
    assert builder.summary.read_rows is summary.read_rows
    assert builder.summary.comment_verdicts is summary.comment_verdicts
    assert isinstance(conn, sqlite3.Connection)
