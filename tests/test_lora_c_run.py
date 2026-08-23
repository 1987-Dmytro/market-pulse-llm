"""`lora-c-run`: the close debts, the sibling trainer, and the pre-pod arithmetic.

Every guard is driven in BOTH directions. The two step-0.5 tests exist because
`docs/reports/lora-c-close.md` §«Open» named them as the shape a test replaces: a quotation guard
nobody had watched refuse, and a threshold living as a module constant beside the law that fixed it.
"""

import json
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import tokenize_lora_c_rows as tokens  # noqa: E402
import write_lora_c_prereg as prereg  # noqa: E402

PREREG = REPO_ROOT / "results" / "prereg_lora_c.json"
TOKENS = REPO_ROOT / "results" / "lora_c_tokens.json"
STATUS = REPO_ROOT / "docs" / "STATUS.md"


# ---------------------------------------------------------------- step 0.5 (1)


@pytest.mark.parametrize("name", ("RULING_V", "RULING_K"))
def test_the_status_quotation_refuses_a_paraphrase(name, tmp_path, monkeypatch):
    """`quoted`'s twin of the control `quoted_spec` got in Dv783.

    The two rulings are this registration's entire authority, and until now the grep that holds them
    had only ever been driven on text that satisfies it — a guard nobody has seen refuse is a guard
    nobody has tested ([[guard_selftest_negative_control]]). The planted paraphrase swaps the
    guillemets both rulings quote inside, which is exactly the class of drift a verbatim grep exists
    to catch and which whitespace normalisation cannot forgive.
    """
    ruling = getattr(prereg, name)
    assert "«" in ruling
    copy = tmp_path / "STATUS.md"
    copy.write_text(STATUS.read_text(encoding="utf-8").replace("«", '"'), encoding="utf-8")
    monkeypatch.setattr(prereg, "STATUS", copy)
    with pytest.raises(SystemExit, match="this quotation is not in STATUS.md"):
        prereg.quoted(ruling)
    monkeypatch.setattr(prereg, "STATUS", STATUS)
    assert prereg.quoted(ruling) == ruling


# ---------------------------------------------------------------- step 0.5 (2)


def threshold_in(quotation: str) -> int:
    """The one number inside a quotation of law, digit groups and their spaces joined.

    Parsed rather than typed: a second literal here would be a second home for the threshold, which
    is the very thing this test exists to close ([[a_threshold_that_lives_in_prose]]).
    """
    found = {int(re.sub(r"\s", "", one)) for one in re.findall(r"\d[\d\s]*\d|\d", quotation)}
    if len(found) != 1:
        raise AssertionError(f"{sorted(found)} numbers in {quotation!r} — the quote names one")
    return found.pop()


def test_the_stop_threshold_constant_equals_the_law_it_quotes():
    """`STOP_AT` against amendment 3.26 (2), through the registration's own quotation of it.

    `docs/reports/lora-c-close.md` §«Open» 2: the bar's law lives in `docs/SPEC.md` and its number
    lives as a module constant in `scripts/tokenize_lora_c_rows.py`, with nothing between them. The
    quotation is `quoted_spec`-checked on every build of the record, so binding the constant to the
    quotation binds it to the law ([[a_registered_threshold_that_is_really_a_function]]).
    """
    record = json.loads(PREREG.read_text(encoding="utf-8"))
    quotation = record["authority"]["amendment_3_26"]["2_the_stop_threshold_reads_the_true_count"]
    law = threshold_in(quotation)
    assert tokens.STOP_AT == law
    # the parse is a real reading and not a constant that happens to agree
    assert threshold_in(quotation.replace("8", "9")) != law

    census = json.loads(TOKENS.read_text(encoding="utf-8"))
    assert census["stop_threshold"] == law
    over = census["rows_over_the_stop_threshold"]
    assert over["which_the_amendment_names"].startswith("by_the_true_count")
    # every row over the threshold is among the widest five, so the count is re-derivable here
    assert sum(one["pod_count"] > law for one in census["widest_rows"]) == over["by_the_true_count"]
    assert str(law)[0] in census["verdict"] and census["max_seq_len"] > law
