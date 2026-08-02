"""The law-review pack: quoted verbatim, grouped by verdict, and saying nothing else.

The pack goes to the operator before a decision about the annotation law, so the two
ways it could be wrong are both silent ones — a rule paraphrased into an argument, or
a word in the prose that says which side produced a label. Both are checked here, and
the end-to-end test runs against the REAL guideline: an anchor that stops matching is
a rule that would be quoted from somewhere else, and nothing downstream would notice.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import build_audit_pack  # noqa: E402
import build_intents_law_pack as law  # noqa: E402
from market_pulse import audit  # noqa: E402

GUIDELINE = Path(__file__).resolve().parents[1] / "docs" / "annotation" / "comments.md"


def control(head, row_id, label, verdict, text="a comment"):
    return {
        "head": head,
        "id": row_id,
        "text": text,
        "label": label,
        "verdict": verdict,
        "notes": "",
    }


ROWS = [
    control("intents", "@c:1", "[]", "incorrect"),
    control("intents", "@c:2", "[]", "correct"),
    control("intents", "@c:3", '["price"]', "incorrect"),
    control("intents", "@c:4", '["taste"]', "correct"),
    control("sentiment", "@c:5", "negative", "incorrect"),
]


def test_the_three_groups_are_verdict_by_label_shape():
    found = law.groups(ROWS)
    assert [row["id"] for row in found["incorrect_empty"]] == ["@c:1"]
    assert [row["id"] for row in found["correct_empty"]] == ["@c:2"]
    assert [row["id"] for row in found["incorrect_other"]] == ["@c:3"]
    # a ruled-correct non-empty row is in no group, and no other head is either
    assert sum(len(rows) for rows in found.values()) == 3


def test_a_span_is_the_source_text_and_its_line_numbers():
    text = "one\ntwo\n\n**Rule.** first\nsecond\n\nthree\n"
    body, start, end = law.span(text, "**Rule.**", "\n\n")
    assert body == "**Rule.** first\nsecond"
    assert (start, end) == (4, 5)


def test_a_missing_anchor_stops_the_run():
    with pytest.raises(SystemExit, match="cannot be quoted verbatim"):
        law.span("nothing to quote here", "**Rule.**", "\n\n")


def test_the_sweep_reads_the_prose_and_not_the_quoted_texts():
    assert law.attribution("plain prose\n```text\nмодель сказала gold\n```\nmore prose") == []
    assert law.attribution("this is the gold label\n") == ["gold"]


def test_the_pack_quotes_the_real_guideline_and_groups_the_real_rows(tmp_path):
    pack = tmp_path / "control.csv"
    build_audit_pack.write_csv(pack, audit.CONTROL_COLUMNS, ROWS)
    out = tmp_path / "intents-law-review.md"
    assert law.main(["--control", str(pack), "--guideline", str(GUIDELINE), "--out", str(out)]) == 0

    page = out.read_text(encoding="utf-8")
    guideline = GUIDELINE.read_text(encoding="utf-8")
    for _, first, stop in law.QUOTES:
        body, _, _ = law.span(guideline, first, stop)
        assert body in page  # verbatim, not paraphrased
    assert "Всего блоков: 3 (1 + 1 + 1)" in page
    assert page.count("### 1/1 · ") == 3
    assert law.attribution(page) == []


def test_an_unruled_intents_row_stops_the_run(tmp_path):
    pack = tmp_path / "control.csv"
    build_audit_pack.write_csv(
        pack, audit.CONTROL_COLUMNS, [*ROWS, control("intents", "@c:6", "[]", "")]
    )
    with pytest.raises(SystemExit, match="unruled"):
        law.main(
            [
                "--control",
                str(pack),
                "--guideline",
                str(GUIDELINE),
                "--out",
                str(tmp_path / "out.md"),
            ]
        )
