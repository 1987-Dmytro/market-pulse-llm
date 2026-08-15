"""`results/reader_gold_w1.json` — the reference structured, and every claim in it re-derived.

Two things are checked that no other test in this repo can: that the gold carries the team lead's
words and not the executor's, and that every row it names is a row the evidence store really has.
The second is the one D2 asks for in so many words — «the reference could carry a typo; the store is
the truth» — and it is why the record carries both spellings wherever they differ.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import reader_population as population  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402
import write_reader_gold as gold  # noqa: E402

from market_pulse import prompts, scorer  # noqa: E402

RECORD_PATH = REPO_ROOT / "results" / "reader_gold_w1.json"
RECORD = json.loads(RECORD_PATH.read_text(encoding="utf-8"))
REFERENCE = " ".join(gold.REFERENCE.read_text(encoding="utf-8").split())


@pytest.fixture(scope="module")
def store() -> dict:
    return gold.evidence_index()


def test_the_committed_gold_is_what_the_producer_writes_today(tmp_path):
    """Byte-identical: the transcription is data, everything else re-derives from the stores."""
    out = tmp_path / "again.json"
    assert gold.main(["--out", str(out)]) == 0
    assert out.read_bytes() == RECORD_PATH.read_bytes()


def test_the_gold_names_only_msg_ids_the_reference_names(store):
    """D2's scope, and the reference's own closing rule: the per-comment bar is counted ONLY over
    the ids this file names. An id that is merely plausible would be the executor writing gold."""
    for row in RECORD["per_comment"]:
        assert str(row["msg_id"]) in REFERENCE, row["msg_id"]
        assert row["evidence_row"]["in_the_store"], row["msg_id"]
        assert (row["channel"], row["msg_id"]) in store
    # 14 rows, and the two «чи варто» ids are deliberately not among them: their gold claim is an
    # absence, which the entity bar scores and a per-comment row cannot
    assert len(RECORD["per_comment"]) == 14
    assert {48099, 48054} & {row["msg_id"] for row in RECORD["per_comment"]} == set()


def test_every_gold_row_carries_the_store_text_and_not_a_retyped_one(store):
    """The `evidence_text` of every named id is what `comment_text` returns today — the same
    recovery `window_summary_5c2` makes from the row's own rendering, so the gold quotes the string
    the model was actually sent."""
    seen = 0
    for row in RECORD["per_comment"]:
        text = summary.comment_text(store[(row["channel"], row["msg_id"])])
        assert row["evidence_row"]["evidence_text"] == text
        seen += 1
    for case in RECORD["flagships"]:
        for signal in case["signals"]:
            for one in signal["evidence_rows"]:
                assert one["evidence_text"] == summary.comment_text(
                    store[(case["channel"], one["msg_id"])]
                )
                seen += 1
    assert seen >= 14


def test_a_paraphrase_of_the_reference_is_refused():
    """The negative control of :func:`write_reader_gold.assert_transcribed`. The phrases in the
    producer are the team lead's; a word of the executor's must stop the build rather than land in
    a gold file nobody would re-read ([[verbatim_quotes_must_be_grepped]])."""
    gold.assert_transcribed("холодовая цепь", None, "наречие,\n  никакого бренда Varto")
    with pytest.raises(SystemExit, match="has been paraphrased"):
        gold.assert_transcribed("холодовая цепочка")


def test_the_reference_quotes_are_a_reading_aid_and_the_record_says_so():
    """Six of the reference's quotes cannot be grepped in the store as written — four of the five
    flagships among them. The state is RECOMPUTED on every build, so this is a measurement and not
    a note: `evidence_text` is what a quote check must run against."""
    states = {}
    for case in RECORD["flagships"]:
        for signal in case["signals"]:
            states[signal["quote"]["state"]] = states.get(signal["quote"]["state"], 0) + 1
    assert states == {"compressed": 4, "none": 3}
    compressed = next(one for one in RECORD["conflicts"] if one["kind"].startswith("quotes"))
    assert [one["case"] for one in compressed["cases"]] == ["F1a", "F3a", "F4a", "F5a", "E1", "E4b"]
    # and the two that do survive verbatim, so the check is not passing because it matches nothing
    assert RECORD["entity_cases"][1]["quote"]["state"] == "verbatim"
    assert RECORD["flagships"][1]["fork"]["quote"]["state"] == "verbatim"


@pytest.mark.parametrize(
    ("case", "quote", "state"),
    [
        ("F1a", "з нього просто тече вода, перемерзше… Повернення робив не один я", "compressed"),
        ("E4a", "чи варто…", "fragmented"),
        ("E3", "Зайшла в Varus на Деміївській", "verbatim"),
    ],
)
def test_the_quote_state_is_computed_from_the_store(case, quote, state, store):
    """Each of the three states, on a row that really wears it. `fragmented` is an elided quote
    whose every piece is present; `compressed` is one the store cannot show at all."""
    texts = {
        "F1a": [summary.comment_text(store[("@VARUS_channel", 21626)])],
        "E4a": [summary.comment_text(store[("@mandziak", 48099)])],
        "E3": [summary.comment_text(store[("@VARUS_channel", 20664)])],
    }[case]
    assert gold.quote_state(quote, texts)["state"] == state


def test_the_aspects_are_the_six_the_repo_already_labels_with():
    """A second aspect vocabulary would make the honesty column of plan §3 impossible: the stance
    layer ADDS a subject to the heads the model already has, and two vocabularies cannot disagree
    in a comparable way."""
    assert set(gold.ASPECT_OF.values()) == set(scorer.INTENTS_V2)
    product = (REPO_ROOT / "docs" / "PRODUCT.md").read_text(encoding="utf-8")
    assert "вкус · цена · упаковка · качество · наличие · сервис" in product
    for word in gold.ASPECT_OF:
        assert word in product
    assert set(RECORD["derivation"]["aspects"].values()) == set(scorer.INTENTS_V2)


def test_a_stance_is_derived_only_where_the_reference_states_one():
    """жалоба and похвала state an attitude; спрос, привычка and тренд do not, and a stance
    invented for them is the reinterpretation D2 forbids. `scored_fields` is what the scorer may
    compare, and a field the reference never stated is not in it."""
    assert gold.STANCE_OF == {"жалоба": "negative", "похвала": "positive"}
    by_id = {row["msg_id"]: row for row in RECORD["per_comment"]}
    assert by_id[21626]["stance"] == "negative" and by_id[21626]["scored_fields"] == [
        "subject_type",
        "stance",
    ]
    assert by_id[47899]["stance"] is None and by_id[47899]["scored_fields"] == ["subject_type"]
    # the one row the reference gives an aspect and a type and no subject at all
    assert by_id[21629]["subject_type"] is None and by_id[21629]["scored_fields"] == ["stance"]
    for row in RECORD["per_comment"]:
        for field in ("subject_type", "stance"):
            assert (field in row["scored_fields"]) == (row[field] is not None)


def test_the_population_is_the_census_cell_and_says_which_cases_it_cannot_carry():
    """The highest-value $0 measurement of this contract: three of the four obligatory entity cases
    and one of the six noise threads are OUTSIDE the population the contract pins, and the cause is
    the gate's own varto/garmonija rule — the thread's only lexicon hit is the one the marker rule
    takes away. A bar scored over them would fail by arithmetic
    ([[an_absolute_bar_needs_a_reachability_state]])."""
    assert RECORD["population"]["threads"] == 111
    assert RECORD["population"]["payable_comments"] == 912
    assert RECORD["population"]["sha256"] == population.census_sha256()
    reach = RECORD["reachability"]
    assert reach["flagships"] == {"reachable": ["F1", "F2", "F3", "F4", "F5"], "unreachable": []}
    assert reach["entity_cases"]["reachable"] == ["E2", "E3"]
    assert [one["id"] for one in reach["entity_cases"]["unreachable"]] == ["E1", "E4a", "E4b"]
    assert reach["noise_threads"]["reachable"] == ["N1", "N2", "N4", "N5", "N6"]
    assert [one["id"] for one in reach["noise_threads"]["unreachable"]] == ["N3"]
    for one in (*reach["entity_cases"]["unreachable"], *reach["noise_threads"]["unreachable"]):
        # each one passes the gate with no silencer running and is removed by the marker rule
        assert one["cause"]["passes_the_gate_with_no_silencer"] is True
        assert one["cause"]["removed_by"] == ["varto_rule"]
    assert len(reach["per_comment"]["inside_the_population"]) == 13
    assert reach["per_comment"]["outside_the_population"] == [578951]


def test_the_store_disagrees_with_the_reference_twice_and_the_record_names_both():
    """Neither is edited: `docs/REFERENCE-signals-w1.md` is a team-lead file. What the executor may
    do is measure the disagreement and carry it where the sitting will see it."""
    kinds = {one["kind"]: one for one in RECORD["conflicts"]}
    moved = kinds["a named msg-id the store puts under another post"]
    assert (moved["msg_id"], moved["post_id_in_the_reference"], moved["post_id_in_the_store"]) == (
        20916,
        10366,
        10375,
    )
    assert moved["evidence_text"] == "1"
    both = kinds["a noise thread the reference itself reads a signal in"]
    assert both["case"] == "N1" and both["secondary"] == ["S1"]


def test_the_gold_names_the_instrument_it_will_be_scored_against():
    """The gold and the prompt are frozen together the moment the endpoint exists, so the record
    carries the sha of the prompt it was built for."""
    assert RECORD["instrument"] == {
        "task": prompts.READER_TASK,
        "prompt_sha256": prompts.prompt_sha256(prompts.READER_TASK),
    }
    assert RECORD["producer"]["sha256"] == summary.sha256_of(
        REPO_ROOT / RECORD["producer"]["script"]
    )
    for name, digest in RECORD["producer"]["borrowed"].items():
        assert summary.sha256_of(REPO_ROOT / name) == digest, name
    for name, digest in RECORD["authority"].items():
        assert summary.sha256_of(REPO_ROOT / name) == digest, name
