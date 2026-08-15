"""`scripts/reader_population.py` — the 111 threads the census counted, named one by one.

The census is the authority on how many; this is the authority on which. The two are held together
by `assert_is_the_census_cell`, and the negative control below is what says that assertion can fail.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import reader_population as population  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import loop, prompts  # noqa: E402

CENSUS = json.loads((REPO_ROOT / "results" / "gate_census_w1.json").read_text(encoding="utf-8"))
CELL = CENSUS["grid"]["narrow|silencers_on"]


@pytest.fixture(scope="module")
def kept() -> list[dict]:
    return population.population()


def test_the_enumeration_is_the_census_cell(kept):
    assert (len(kept), sum(len(one["comments"]) for one in kept)) == (
        CELL["threads"],
        CELL["comments_payable"],
    )
    assert (CELL["threads"], CELL["comments_payable"]) == (111, 912)
    assert population.census_sha256() == summary.sha256_of(population.CENSUS)


def test_an_enumeration_that_is_not_the_cell_is_refused(kept):
    """The negative control. A restatement of a keep predicate is worth exactly what the check
    holding it to the sealed one is worth, and a check that cannot fail is worth nothing.

    Both halves fire: a thread short, and a thread whose comments were quietly dropped — the second
    is the one a thread count alone would let through, and it changes what every thread costs.
    """
    with pytest.raises(SystemExit, match="110 threads and"):
        population.assert_is_the_census_cell(kept[:-1])
    thinner = [{**kept[0], "comments": kept[0]["comments"][:-1]}, *kept[1:]]
    with pytest.raises(SystemExit, match=f"111 threads and {CELL['comments_payable'] - 1}"):
        population.assert_is_the_census_cell(thinner)


def test_every_thread_carries_payable_comments_under_unique_ids(kept):
    """Text-less comments are counted and never sent — SPEC 3.19 (1) skips them before payment, and
    the census priced the payable population. A duplicate id inside one thread would make every
    evidence msg_id in that thread's verdict unresolvable."""
    for one in kept:
        ids = [row["msg_id"] for row in one["comments"]]
        assert len(set(ids)) == len(ids), one["post_id"]
        for row in one["comments"]:
            assert loop.has_text(row["text"])
    # one thread of the 111 has no payable comment at all: its POST carried the only category word
    empty = [one for one in kept if not one["comments"]]
    assert [(one["channel"], one["post_id"]) for one in empty] == [("@tarilka_malyuka", 829)]


def test_the_whole_population_renders_under_the_registered_input_ceiling(kept):
    """The guard of `prompts.READER_MAX_INPUT_CHARS` must not be able to fire on a thread the probe
    is registered to read: a refusal mid-run would eat the one attempt the contract allows
    ([[lifted_ceiling_is_not_lifted_code]]). So it is measured over all 111, through the rendering
    the run will use, and the largest is pinned — the number the constant's docstring quotes."""
    sizes = []
    for one in kept:
        content = prompts.reader_messages_gm4(
            one["channel"],
            one["post_id"],
            one["post_text"],
            [(row["msg_id"], row["text"]) for row in one["comments"]],
        )[0]["content"]
        sizes.append((len(content), one["channel"], one["post_id"]))
    biggest = max(sizes)
    assert biggest == (27593, "@matusi_ukr", 22058)
    assert biggest[0] < prompts.READER_MAX_INPUT_CHARS
    assert sorted(sizes)[len(sizes) // 2][0] == 6095
