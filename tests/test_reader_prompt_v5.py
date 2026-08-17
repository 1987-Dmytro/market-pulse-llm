"""`prompts.READER_THREAD_PROMPT_V5` — seven pairs over v3, and no example the model has ever seen.

Two things are proved here that no other test can. That v5 is v3 plus SEVEN visible `_swap` calls
and nothing else, each one traceable to a miss reader-v4 PAID for; and that every example sentence
the new text carries is SYNTHETIC — absent from every stored comment, every stored post, both gold
files and the reference the gold transcribes. The sitting of 2026-08-17 makes the second a RED gate:
teaching the exam is worse than failing it.

The contamination check carries its own negative control. A matcher that found nothing because it
was broken would read exactly like a clean pass ([[guard_selftest_negative_control]]), so a phrase
taken out of the store must be FOUND by the same two comparisons that clear the examples.
"""

import difflib
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import window_summary_5c2 as summary  # noqa: E402
import write_reader_gold as gold  # noqa: E402

from market_pulse import prompts  # noqa: E402

V3 = prompts.READER_THREAD_PROMPT_V3
V5 = prompts.READER_THREAD_PROMPT_V5

PAIRS = (
    ("7 chunk header", prompts.READER_ONE_ANSWER_V3, prompts.READER_ONE_ANSWER_V5),
    ("1 attribution", prompts.READER_DUTY_THREE_V3, prompts.READER_ATTRIBUTION_V5),
    ("5 one vocabulary", prompts.READER_SIGNAL_SUBJECTS_V3, prompts.READER_SIGNAL_SUBJECTS_V5),
    ("2 aspect contrast", prompts.READER_ASPECT_V3, prompts.READER_ASPECT_V5),
    ("6 echo duty", prompts.READER_PER_COMMENT_V3, prompts.READER_PER_COMMENT_V5),
    ("4 F2a carve-out", prompts.READER_CARRY_V3, prompts.READER_CARRY_V5),
    ("3 exchange evidence", prompts.READER_EXCHANGE_V3, prompts.READER_EXCHANGE_V5),
)
"""The seven, in the order the `_swap` chain applies them. Listed here so the test can drive each
one instead of describing it — a pair written but never wired into the chain would pass on the
presence of its own constant, so both halves are checked against the assembled texts."""

SYNTHETIC = (
    "жирність у таких йогуртах давно вже не та",
    "на касі простояла сорок хвилин із повним візком",
    "сирки з родзинками ніхто вже не робить такі, як колись",
    "а є у вас кефір без лактози?",
    "партію відкликали, у продажу її більше немає",
)
"""Every example sentence pairs 1-4 add. Five, and the contract's rule is over exactly these: an
example that occurs in the corpus would be the instrument taught the answer to its own exam."""

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
    """Everything the reader could have been shown, raw and normalised, as one blob each.

    The stores under `data/` are gitignored, so this fixture is the reason the check runs on the
    machine that has them — the same reason `tests/test_reader_gold.py` reads the store rather than
    a fixture of it ([[a_fixture_on_disk_pins_yesterdays_schema]]).
    """
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


def test_the_corpus_matcher_finds_a_phrase_that_IS_in_the_store(corpus):
    """The negative control, and the premise everything below rests on: a sentence out of the
    evidence store is found by BOTH comparisons. Without it, «not found» could be the matcher."""
    raw, flat = corpus
    assert len(raw) > 1_000_000, "the corpus is not on this machine — the check would prove nothing"
    planted = next(
        text[:40]
        for text in (summary.comment_text(row) for row in gold.evidence_index().values())
        if text and len(text) > 40
    )
    assert planted in raw
    assert gold.normalise(planted) in flat


def test_no_example_in_the_v5_prompt_occurs_anywhere_in_the_corpus(corpus):
    """The sitting's red gate. Both readings: the sentence as written, and the sentence with
    whitespace collapsed and case folded — a paraphrase that only differs in capitals is still the
    exam."""
    raw, flat = corpus
    for sentence in SYNTHETIC:
        assert sentence in V5, sentence
        assert sentence not in raw, sentence
        assert gold.normalise(sentence) not in flat, sentence


def test_every_synthetic_example_is_declared_and_every_declared_one_is_used():
    """The list and the text, held together in both directions — a sixth example added to the prompt
    without joining :data:`SYNTHETIC` would never be checked for contamination."""
    quoted = {
        piece
        for chunk in V5.split("«")[1:]
        for piece in (chunk.split("»")[0],)
        if piece not in V3 and len(piece.split()) >= 4
    }
    # one «…» v5 adds is not an example at all: it is the chunk header the renderer writes, quoted
    # so the model can recognise it. Named rather than filtered by length, because a rule that let
    # a short example slip through would be a hole in the gate above
    header = "частина i з n"
    assert header in quoted and prompts.READER_PART_LINE.startswith(
        f"<part>{header.split(' i ')[0]}"
    )
    assert quoted - {header} == set(SYNTHETIC), (quoted - {header}) ^ set(SYNTHETIC)


def test_v5_is_v3_with_exactly_seven_pairs_and_every_one_of_them_fired():
    """SEVEN `_swap` calls, so «seven changes» is a property of `prompts.py` and not a claim in a
    report. Each pair is checked BOTH ways — its NEW text absent from v3 and present exactly once in
    v5 — because a constant that was written and never wired into the chain would otherwise pass on
    its own existence."""
    assert V3 != V5
    for name, before, after in PAIRS:
        assert V3.count(before) == 1, name
        assert after not in V3, name
        assert V5.count(after) == 1, name
    # five of the seven keep their old wording and grow it, so «the old text is gone» is asserted
    # only for the two that really replace one
    for name, before, _ in PAIRS:
        if name.startswith(("5 ", "7 ")):
            assert before not in V5, name

    # and the diff itself carries no deletion: v5 is v3 plus seven changes, never v3 with something
    # quietly dropped
    edits = [
        one
        for one in difflib.SequenceMatcher(
            None, V3.split("\n"), V5.split("\n"), autojunk=False
        ).get_opcodes()
        if one[0] != "equal"
    ]
    assert [one[0] for one in edits].count("delete") == 0, edits


def test_pair_one_states_the_swap_test_and_names_all_three_confusion_pairs():
    """The attribution block is the answer to bar 4's FOUR disagreements, and they are three
    confusion pairs: category read as the chain (21601, 48283), brand read as the chain (580124),
    category read as a brand (580129). One example each, and the RULE above them."""
    assert "ATTRIBUTION" in V5
    assert "read off THE COMMENT ITSELF" in V5
    assert "if the chain were a different chain, or the trade mark a different trade mark" in V5
    assert "the shop AS a shop is what is being talked about" in V5
    for reading in ("«категория_личное»", "«сеть_ритейлер»", "«молочный_бренд»"):
        assert reading in prompts.READER_ATTRIBUTION_V5, reading
    # the block belongs to duty (3) and therefore comes after it and before the schema
    assert V5.index("(3) THE SIGNALS") < V5.index("ATTRIBUTION")
    assert V5.index("ATTRIBUTION") < V5.index("Return ONE JSON object")


def test_pair_five_takes_the_word_out_of_the_TEXT_and_leaves_the_PARSER_alone():
    """«категория» stops being offered by the instrument and stays legal for the parser.

    Narrowing `READER_SUBJECT_TYPES` would refuse answers that v1, v2 and v3 runs were allowed to
    make, and 26 paid verdicts plus gold r2 were validated against it. So the domain does not move
    and the collapse stays a registered SCORING rule."""
    assert "категория_личное" in prompts.READER_SIGNAL_SUBJECTS_V5
    assert '"категория",' not in prompts.READER_SIGNAL_SUBJECTS_V5
    assert prompts.READER_SUBJECT_TYPES == (
        "молочный_бренд",
        "сеть_ритейлер",
        "категория",
        "категория_личное",
        "не_наш_рынок",
    )
    # and the parser still accepts the word the reference spells, under v5 as under v3
    reply = json.dumps(
        {
            "thread": {"channel": "@c", "post_id": 1},
            "post_summary": "п",
            "discussion_summary": "д",
            "entities": [],
            "signals": [],
            "per_comment": [{"msg_id": 1, "subject_type": "категория"}],
            "noise": [],
        },
        ensure_ascii=False,
    )
    for task in (prompts.READER_TASK_V3, prompts.READER_TASK_V5):
        assert prompts.parse_reply(task, reply)["per_comment"][0]["subject_type"] == "категория"


def test_pair_six_is_stated_over_BOTH_lists_because_that_is_what_v4_measured():
    """reader-v4 returned 93 `per_comment` rows of 111 requested and the other 18 are in `noise`:
    over its parsed threads `per_comment ∪ noise` covers 111 of 111. A duty demanding a `per_comment`
    row per id would refuse the answer the outranking rule obliges ([[count_the_kind_not_the_rows]]),
    so the duty names the pair and the census counts the three states apart."""
    assert "one object for EVERY comment id you were given" in V5
    assert (
        'The only ids that may be missing from this list are the ones you report in "noise"' in V5
    )
    assert "every id you were given is answered exactly once" in V5
    # the rule the duty must not contradict is still in the text, unedited
    assert '- A comment belongs to at most one of "per_comment" and "noise".' in V5


def test_pair_four_is_scoped_to_events_and_says_so_about_opinions():
    """Narrow by ruling. Widened to opinions it would re-open the defect the line above exists for —
    «Гармонія» the children's centre read as brand negative — and cost bar 3, currently a PASS."""
    assert "ONE narrow exception" in V5
    assert "AVAILABILITY or the STATUS" in V5
    assert "An opinion with no name in it is still never carried over" in V5
    assert prompts.READER_CARRY_V3 in V5, "the old law is kept, not replaced"


def test_pairs_two_and_three_close_the_two_halves_of_F1b():
    assert 'is "availability" and never "taste"' in V5
    assert '"evidence" carries BOTH msg_ids' in V5
    assert prompts.READER_EXCHANGE_V3 in V5, "the channel's-own-reply rule is kept and grown"


# --- the render -------------------------------------------------------------------------------

THREAD = {
    "channel": "@klopotenkofood",
    "post_id": 6040,
    "post": "Що готуєте сьогодні?",
    "comments": [(21231, "Кабачкову ікру)"), (21232, "Млинці з ягодами")],
}


def test_the_default_render_is_byte_identical_to_what_it_always_was():
    """`part` defaults to None and the header is a prefix that is the empty string, so no caller
    that never heard of chunking can be handed a different request
    ([[a_sealed_caller_forces_the_default]])."""
    for task in sorted(prompts.READER):
        default = prompts.reader_messages_gm4(**THREAD, task=task)
        assert default == prompts.reader_messages_gm4(**THREAD, task=task, part=None)
        assert "<part>" not in default[0]["content"]
    # and the DEFAULT task is still v2, which is the one every driver written so far passes nothing
    # for — v5 is opt-in and the run contract names it
    assert prompts.reader_messages_gm4(**THREAD) == prompts.reader_messages_gm4(
        **THREAD, task=prompts.READER_TASK_V2
    )


def test_a_part_adds_exactly_one_line_inside_the_fence_above_the_comments():
    whole = prompts.reader_messages_gm4(**THREAD, task=prompts.READER_TASK_V5)[0]["content"]
    part = prompts.reader_messages_gm4(**THREAD, task=prompts.READER_TASK_V5, part=(2, 3))[0][
        "content"
    ]
    assert part.count("\n") == whole.count("\n") + 1
    assert "<part>частина 2 з 3</part>\n" in part
    assert part.index("</post>") < part.index("<part>") < part.index('<comment msg_id="21231"')
    # the header the prompt names and the header the renderer writes are the same string
    assert "«частина i з n»" in prompts.READER_ONE_ANSWER_V5
    assert prompts.READER_PART_LINE.format(i=2, n=3).strip() == "<part>частина 2 з 3</part>"


def test_a_part_that_is_not_a_part_is_refused():
    """A header that told the model «part 4 of 3» would state something untrue about the request it
    is in, and the model has no way to see that it is untrue."""
    for bad in ((0, 3), (4, 3), (2, 1), (-1, 2)):
        with pytest.raises(ValueError, match="is not a part"):
            prompts.reader_messages_gm4(**THREAD, task=prompts.READER_TASK_V5, part=bad)
    # the premise: the same call with a legal part does not raise
    assert prompts.reader_messages_gm4(**THREAD, task=prompts.READER_TASK_V5, part=(3, 3))


def test_the_v5_text_never_lifts_a_thread_over_the_input_ceiling_it_would_have_fitted_under():
    """v5 is ~3 200 characters longer than v3, and the ceiling is a LOUD refusal rather than a
    truncation. The registered population's largest rendered thread has to stay well under it, or
    the instrument would refuse a thread the registration promises to read."""
    longest = 12524  # @matusi_ukr:22272 under v3, from results/prereg_reader_probe_v4.json
    grew = len(prompts.PROMPTS[prompts.READER_TASK_V5]) - len(
        prompts.PROMPTS[prompts.READER_TASK_V3]
    )
    assert 0 < grew < 4000
    assert longest + grew < prompts.READER_MAX_INPUT_CHARS
