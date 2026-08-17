"""`prompts.PASS1_COMMENT_PROMPT`, its renderer and its parser — architecture D's pass 1.

Three things are proved here that no other test can. That the attribution law pass 1 asks with is
the SAME BYTES the reader was asked with, so a finding is about the decomposition and not about a
re-worded law; that the new text carries no example the model has ever seen and no gold VALUE of any
kind; and that the parser refuses the one failure a single-object schema cannot see on its own — an
answer about a different comment than the one that was sent.

The contamination check carries the same negative control `tests/test_reader_prompt_v5.py` uses: a
phrase taken out of the store must be FOUND by both comparisons, or «not found» could be the matcher
([[guard_selftest_negative_control]], [[run_the_instrument_on_the_named_example]]).
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import window_summary_5c2 as summary  # noqa: E402
import write_reader_gold as gold  # noqa: E402

from market_pulse import prompts  # noqa: E402

TEXT = prompts.PASS1_COMMENT_PROMPT
GOLD_R2 = json.loads((REPO_ROOT / "results" / "reader_gold_w1_r2.json").read_text(encoding="utf-8"))

CORPUS_DIRS = (
    "data/raw/comments",
    "data/raw/comments_v2",
    "data/raw/posts",
    "data/derived/inferences",
    "data/derived/post_texts",
)
CORPUS_FILES = (
    "results/reader_gold_w1.json",
    "results/reader_gold_w1_r2.json",
    "docs/REFERENCE-signals-w1.md",
)


@pytest.fixture(scope="module")
def corpus() -> tuple[str, str]:
    """Everything pass 1 could have been shown, raw and normalised — the v5 fixture's population."""
    parts = []
    for name in CORPUS_DIRS:
        directory = REPO_ROOT / name
        if directory.is_dir():
            parts += [
                path.read_text(encoding="utf-8", errors="replace")
                for path in sorted(directory.rglob("*.jsonl"))
            ]
    parts += [(REPO_ROOT / name).read_text(encoding="utf-8") for name in CORPUS_FILES]
    raw = "\n".join(parts)
    return raw, gold.normalise(raw)


# --- the law, shared rather than copied -----------------------------------------------------------


def test_the_attribution_law_is_the_readers_own_bytes_and_the_v5_text_did_not_move():
    """The split that made the sharing possible must not have moved a byte of what it split.

    `results/prereg_reader_probe_v5b.json` pins the v5 text's sha and 26 paid verdicts were produced
    under it; the constant was cut in two so pass 1 could carry the law without inheriting a sentence
    about "signals" and "per_comment", and the pinned number is the proof it was a cut and not an
    edit ([[a_comment_only_edit_moves_the_files_hash]]).
    """
    pinned = json.loads(
        (REPO_ROOT / "results" / "prereg_reader_probe_v5b.json").read_text(encoding="utf-8")
    )["instruments"]["prompt_sha256"]["reader_thread_gm4_v5"]
    assert prompts.prompt_sha256(prompts.READER_TASK_V5) == pinned
    assert prompts.READER_ATTRIBUTION_V5 == (
        prompts.READER_DUTY_THREE_V3
        + "\n\n"
        + prompts.READER_ATTRIBUTION_HEAD_V5
        + prompts.READER_ATTRIBUTION_LAW_V5
    )
    # and pass 1 really carries those bytes, in one piece
    assert prompts.READER_ATTRIBUTION_LAW_V5 in TEXT
    assert prompts.READER_ATTRIBUTION_LAW_V5 in prompts.READER_THREAD_PROMPT_V5
    # the half it deliberately does NOT carry — pass 1 has neither list
    assert prompts.READER_ATTRIBUTION_HEAD_V5 not in TEXT
    assert '"per_comment"' not in TEXT and '"signals"' not in TEXT


def test_the_swap_test_and_all_three_confusion_pairs_travel_with_it():
    """The law is the reason to run this probe at all: if the same words in a shorter task read
    better, the finding is about the task shape. So the words have to be THERE."""
    assert "would the complaint or the praise still stand if the chain were a different chain" in (
        " ".join(TEXT.split())
    )
    for word in ("«категория_личное»", "«сеть_ритейлер»", "«молочный_бренд»"):
        assert word in TEXT, word


# --- no example the model has seen, and no gold value at all --------------------------------------


def test_the_corpus_matcher_finds_a_phrase_that_IS_in_the_store(corpus):
    """The negative control. Without it, «not found» below could be the matcher."""
    raw, flat = corpus
    assert len(raw) > 1_000_000, "the corpus is not on this machine — the check would prove nothing"
    planted = next(
        text[:40]
        for text in (summary.comment_text(row) for row in gold.evidence_index().values())
        if text and len(text) > 40
    )
    assert planted in raw
    assert gold.normalise(planted) in flat


def test_no_example_in_the_pass1_prompt_occurs_anywhere_in_the_corpus(corpus):
    """Every «…» quotation the text carries, driven from the TEXT and not from a hand list — an
    example added later without joining a constant would still have to clear this."""
    raw, flat = corpus
    quoted = {
        piece
        for chunk in TEXT.split("«")[1:]
        for piece in (chunk.split("»")[0],)
        if len(piece.split()) >= 3
    }
    assert len(quoted) >= 3, quoted
    for sentence in quoted:
        assert sentence not in raw, sentence
        assert gold.normalise(sentence) not in flat, sentence


def test_the_prompt_names_no_gold_msg_id_no_gold_thread_and_no_gold_answer():
    """The contract's own red gate: the prompt states RULES, never a specific row.

    Every gold msg_id, every gold thread key and — the one a word-grep would miss — every gold
    `subject_id`, which is the only gold VALUE spelled in a vocabulary the prompt also uses.
    """
    rows = GOLD_R2["per_comment"]
    ids, threads, subjects, texts = set(), set(), set(), set()
    for row in rows:
        ids.add(str(row["msg_id"]))
        evidence = row.get("evidence_row") or {}
        threads.add(f"{row['channel']}:{evidence.get('post_id_in_the_store')}")
        if row.get("subject_id"):
            subjects.add(str(row["subject_id"]))
        if evidence.get("evidence_text"):
            texts.add(evidence["evidence_text"])
    # every population is non-empty, or the loops below would pass over nothing
    assert len(ids) == 14 and len(threads) == 7 and subjects and texts, (
        len(ids),
        len(threads),
        len(subjects),
        len(texts),
    )
    flat = TEXT.casefold()
    for value in ids:
        assert value not in TEXT, value
    for value in threads | subjects:
        assert value.casefold() not in flat, value
    # and no gold comment's own words: the longest run of any of them that the prompt repeats
    for value in texts:
        for start in range(0, max(1, len(value) - 24)):
            assert value[start : start + 24].casefold() not in flat, value[start : start + 24]


# --- the renderer ---------------------------------------------------------------------------------

REQUEST = {
    "channel": "@klopotenkofood",
    "post_id": 6040,
    "topic": "Пост про сирки.",
    "entities": [
        {"name": "Лімо", "subject_type": "молочный_бренд", "reading": "бренд морозива"},
        {"name": "VARUS", "subject_type": "сеть_ритейлер", "reading": None},
    ],
    "msg_id": 21231,
    "text": "Кабачкову ікру)",
}


def test_the_request_carries_the_topic_the_entities_and_exactly_one_comment():
    content = prompts.pass1_messages_gm4(**REQUEST)[0]["content"]
    assert content.startswith(TEXT)
    assert content.count("<comment ") == 1
    assert '<comment msg_id="21231">' in content
    assert "Лімо → молочный_бренд → бренд морозива" in content
    # a row with no reading renders with the name and the type alone rather than a dangling arrow
    assert "VARUS → сеть_ритейлер\n" in content
    assert content.index("<topic>") < content.index("<entities>") < content.index("<comment ")


def test_an_empty_entity_block_says_so_instead_of_rendering_nothing():
    """`@mandziak:3703`'s bought verdict resolves NO entity, and «this thread resolved none» must not
    look to the model like «the block was forgotten» ([[an_empty_field_hides_several_states]])."""
    content = prompts.pass1_messages_gm4(**REQUEST | {"entities": []})[0]["content"]
    assert "<entities>\n(this thread resolved no entity)\n</entities>" in content


def test_the_renderer_refuses_a_nameless_entity_and_an_empty_comment():
    with pytest.raises(ValueError, match="an entity with no name"):
        prompts.pass1_messages_gm4(**REQUEST | {"entities": [{"subject_type": "категория_личное"}]})
    with pytest.raises(ValueError, match="nothing to read"):
        prompts.pass1_messages_gm4(**REQUEST | {"text": "   "})
    # the premise: the same call unchanged does not raise
    assert prompts.pass1_messages_gm4(**REQUEST)


def test_a_request_over_the_ceiling_is_refused_rather_than_truncated():
    with pytest.raises(ValueError, match="over the registered ceiling"):
        prompts.pass1_messages_gm4(**REQUEST | {"text": "я" * prompts.PASS1_MAX_INPUT_CHARS})


def test_the_reader_renderer_is_not_touched_and_neither_renders_the_others_task():
    with pytest.raises(ValueError, match="not a registered pass-1 prompt"):
        prompts.pass1_messages_gm4(**REQUEST, task=prompts.READER_TASK_V5)
    with pytest.raises(ValueError, match="not a registered reader prompt"):
        prompts.reader_messages_gm4("@c", 1, "post", [(2, "text")], task=prompts.PASS1_TASK)
    with pytest.raises(ValueError, match="use pass1_messages_gm4"):
        prompts.build_messages(prompts.PASS1_TASK, "text")


# --- the parser -----------------------------------------------------------------------------------


def answer(**over) -> str:
    row = {
        "msg_id": 21231,
        "subject_type": "молочный_бренд",
        "subject_id": "Лімо",
        "stance": "positive",
    } | over
    return json.dumps(row, ensure_ascii=False)


def test_a_clean_answer_parses_to_the_four_fields():
    assert prompts.parse_pass1(answer(), msg_id=21231) == {
        "msg_id": 21231,
        "subject_type": "молочный_бренд",
        "subject_id": "Лімо",
        "stance": "positive",
    }
    # nulls are answers, not omissions
    assert prompts.parse_pass1(
        answer(subject_type=None, subject_id=None, stance=None), msg_id=21231
    ) == {"msg_id": 21231, "subject_type": None, "subject_id": None, "stance": None}


def test_an_answer_about_another_comment_is_REFUSED_by_name():
    """The failure a single-object schema cannot see: the object is valid, the row is simply about
    the wrong comment, and nothing downstream could tell — it would be scored against the wrong
    gold."""
    with pytest.raises(prompts.ParseError, match="msg_id echoes 21232, not the 21231"):
        prompts.parse_pass1(answer(msg_id=21232), msg_id=21231)
    # the id may arrive as the string the request's attribute showed it as
    assert prompts.parse_pass1(answer(msg_id="21231"), msg_id=21231)["msg_id"] == 21231


def test_the_subject_type_domain_is_the_FOUR_and_kategoria_is_not_one_of_them():
    """The narrow domain the contract fixes, and the measurement behind it: over v5b's 195
    `per_comment` rows the fifth word «категория» never appears once."""
    assert prompts.PASS1_SUBJECT_TYPES == prompts.READER_ENTITY_TYPES
    assert len(prompts.PASS1_SUBJECT_TYPES) == 4
    assert "категория" in prompts.READER_SUBJECT_TYPES
    with pytest.raises(prompts.ParseError, match="subject_type outside its domain"):
        prompts.parse_pass1(answer(subject_type="категория"), msg_id=21231)
    rows = [
        row
        for line in (REPO_ROOT / "results" / "reader_v5b_w1.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line
        for parsed in (json.loads(line).get("parsed"),)
        if parsed
        for row in parsed.get("per_comment", [])
    ]
    assert len(rows) > 100, "the v5b evidence was not read — the measurement below would be empty"
    assert {row["subject_type"] for row in rows} <= {None, *prompts.PASS1_SUBJECT_TYPES}


def test_every_other_shape_is_a_refusal_and_none_of_them_is_repaired():
    for reply, reason in (
        ("", "empty reply"),
        ("no braces here", "no JSON object"),
        ('{"msg_id": 21231, "subject_type": "молочный_бренд"', "malformed JSON"),
        ('{"msg_id": 21231, "subject_type": null, "subject_id": null}', "missing field: stance"),
        (answer(stance="ambivalent"), "stance outside its domain"),
        (answer(subject_id=""), "subject_id is not a non-empty string"),
        (answer(msg_id="not a number"), "msg_id is not a msg_id"),
    ):
        with pytest.raises(prompts.ParseError, match=reason):
            prompts.parse_pass1(reply, msg_id=21231)
    # a fence is formatting, not a different answer — the one tolerance `_object` has always had
    assert prompts.parse_pass1(f"```json\n{answer()}\n```", msg_id=21231)["stance"] == "positive"
    # and a SECOND object is not merged the way the reader's is: the first one is the answer
    assert (
        prompts.parse_pass1(f"{answer()}\n{answer(stance='negative')}", msg_id=21231)["stance"]
        == "positive"
    )


def test_parse_reply_refuses_the_task_by_name_and_points_at_the_parser_that_can():
    with pytest.raises(ValueError, match=r"use parse_pass1\(reply, msg_id="):
        prompts.parse_reply(prompts.PASS1_TASK, answer())
