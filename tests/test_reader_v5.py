"""`market_pulse.reader_v5` — the transport stop, the echo census and the chunk merge, driven.

Every test here runs at $0 and none of them loads a model: the balanced-prefix scanner is a pure
function over text, so the crafted cases the contract names — braces inside strings, escaped quotes,
a second object after the first, a reply that never balances — are exercised where they cost
nothing. A stop rule tested only on a pod is a stop rule tested once, after the money.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from market_pulse import prompts, reader_v5  # noqa: E402


def verdict(**moves) -> dict:
    body = {
        "thread": {"channel": "@c", "post_id": 1},
        "post_summary": "п",
        "discussion_summary": "д",
        "entities": [],
        "signals": [],
        "per_comment": [],
        "noise": [],
        "repairs": [],
    }
    return body | moves


# --- the transport stop -----------------------------------------------------------------------


def test_the_prefix_ends_at_the_first_balanced_object():
    assert reader_v5.balanced_prefix('{"a": 1}') == '{"a": 1}'
    assert reader_v5.balanced_prefix('{"a": {"b": 2}} trailing') == '{"a": {"b": 2}}'


def test_a_brace_inside_a_string_does_not_count():
    """A reader's answer is Ukrainian prose copied out of retail threads, and `{` is an ordinary
    character in one. Counting it would cut the reply in half at a quote."""
    assert reader_v5.balanced_prefix('{"a": "}"}') == '{"a": "}"}'
    assert reader_v5.balanced_prefix('{"quote": "смачно {дуже}"}') == '{"quote": "смачно {дуже}"}'
    assert reader_v5.balanced_prefix('{"a": "{{{"}') == '{"a": "{{{"}'


def test_an_escaped_quote_does_not_end_the_string_and_an_escaped_backslash_does():
    r"""`"a\""` is one string containing a quote; `"a\\"` is one string ending in a backslash. Get
    the second wrong and every reply carrying a Windows path or a LaTeX-ish quote is mis-cut."""
    assert reader_v5.balanced_prefix(r'{"a": "x\"}", "b": 1}') == r'{"a": "x\"}", "b": 1}'
    assert reader_v5.balanced_prefix(r'{"a": "x\\"}') == r'{"a": "x\\"}'
    assert reader_v5.balanced_prefix(r'{"a": "x\\\"}", "b": 2}') == r'{"a": "x\\\"}", "b": 2}'
    # and the cut prefix really is valid JSON in every one of them
    for text in (r'{"a": "x\"}", "b": 1}', r'{"a": "x\\"}', r'{"a": "x\\\"}", "b": 2}'):
        assert json.loads(reader_v5.balanced_prefix(text)) is not None


def test_a_second_object_after_the_first_is_CUT_and_that_is_the_whole_ruling():
    """reader-v4's two `two disagreeing objects` refusals, killed in the transport. The parser's
    refuse-on-conflict clause stays as defence and is never reached, because the second object is
    never generated."""
    text = '{"thread": {"channel": "@c", "post_id": 1}}{"entities": []}'
    assert reader_v5.balanced_prefix(text) == '{"thread": {"channel": "@c", "post_id": 1}}'
    # the control: the same parser refuses the WHOLE text and accepts nothing about it
    with pytest.raises(prompts.ParseError, match="two disagreeing objects|missing field"):
        prompts.parse_reply(prompts.READER_TASK_V5, text)


def test_a_reply_that_never_balances_returns_None_and_is_left_to_the_ceiling():
    """Inventing the closing brace here would be the transport writing the answer."""
    assert reader_v5.balanced_prefix('{"a": 1') is None
    assert reader_v5.balanced_prefix('{"a": "unterminated') is None
    assert reader_v5.balanced_prefix("") is None
    assert reader_v5.balanced_prefix("no braces at all") is None


def test_noise_BEFORE_the_first_brace_is_kept_because_the_prefix_is_what_was_emitted():
    """The cut is on the TAIL: what is persisted has to be exactly the tokens the model produced up
    to the closing brace, or the raw reply stops being the raw reply. A fence, a sentence or a stray
    `}` in front of the object is formatting the parser already unwraps, and dropping it here would
    make the two machines disagree about what was said."""
    for text in ('```json\n{"a": 1}\n```', 'here you go: {"a": 1}', '}{"a": 1}'):
        prefix = reader_v5.balanced_prefix(text)
        assert prefix.endswith('{"a": 1}') and text.startswith(prefix)
        assert prompts._object(prefix) == {"a": 1}


def test_the_scanner_agrees_with_the_parser_on_every_reply_reader_v4_actually_got():
    """The strongest available control: 23 replies this repo PAID for. Every one that parses under
    the reader parser must have a balanced prefix, and parsing the prefix must give the same
    verdict as parsing the whole reply — the stop may not change an answer, only shorten it."""
    rows = [
        json.loads(line)
        for line in (REPO_ROOT / "results" / "reader_v4_w1.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line
    ]
    cut = 0
    for row in rows:
        prefix = reader_v5.balanced_prefix(row["reply"])
        if row["parsed"] is None:
            continue
        assert prefix is not None, row["thread"]
        assert prompts.parse_reply(row["task"], prefix) == prompts.parse_reply(
            row["task"], row["reply"]
        ), row["thread"]
        cut += len(row["reply"]) - len(prefix) > 0
    assert len(rows) == 23
    # and it really does cut something on this evidence, or the control is vacuous
    assert cut >= 1


# --- the echo census --------------------------------------------------------------------------


def test_the_census_counts_three_states_and_only_absent_is_a_shortfall():
    census = reader_v5.echo(
        [1, 2, 3, 4],
        verdict(
            per_comment=[{"msg_id": 1}, {"msg_id": 2}],
            noise=[{"msg_id": 3}],
        ),
    )
    assert census["in_per_comment"] == [1, 2]
    assert census["in_noise"] == [3]
    assert census["absent"] == [4]
    assert census["covered"] == 3 and census["requested"] == 4
    assert census["extra"] == [] and census["duplicated"] == []


def test_reader_v4s_own_replies_come_back_111_of_111_which_is_why_the_duty_names_both_lists():
    """The measurement that shaped pair 6, recomputed here from the paid rows rather than quoted.

    v4's report reads 93 `per_comment` of 111 requested as one row in six not written. Over the
    parsed threads the union covers everything, so the shortfall the echo duty exists to close is
    ZERO on this evidence and what is left is a CLASSIFICATION question — one thread answered wholly
    as noise ([[count_the_kind_not_the_rows]]).
    """
    import re

    rows = [
        json.loads(line)
        for line in (REPO_ROOT / "results" / "reader_v4_w1.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line
    ]
    requested = covered = in_pc = in_noise = 0
    absent, wholly_noise = [], []
    for row in rows:
        if row["parsed"] is None:
            continue
        ids = [int(one) for one in re.findall(r'<comment msg_id="(\d+)"', row["request"])]
        census = reader_v5.echo(ids, row["parsed"])
        requested += census["requested"]
        covered += census["covered"]
        in_pc += len(census["in_per_comment"])
        in_noise += len(census["in_noise"])
        absent += [(row["thread"], one) for one in census["absent"]]
        assert census["extra"] == [], row["thread"]
        if census["requested"] and not census["in_per_comment"]:
            wholly_noise.append(row["thread"])
    assert (requested, covered) == (111, 111)
    assert (in_pc, in_noise) == (93, 18)
    assert absent == []
    assert wholly_noise == [
        "@matusi_ukr:22242",  # the one that is a miss: E1's thread, and pc:578951 lives in it
        "@retsepty:7312",  # N4 — a registered NOISE thread, so this is the right answer
        "@retsepty:7325",  # N5
        "@retsepty:7327",  # N6
    ]


def test_an_id_answered_twice_and_an_id_nobody_asked_for_are_different_defects():
    census = reader_v5.echo(
        [1, 2],
        verdict(per_comment=[{"msg_id": 1}, {"msg_id": 1}], noise=[{"msg_id": 9}]),
    )
    assert census["duplicated"] == [1]
    assert census["extra"] == [9]
    assert census["absent"] == [2]


def test_out_of_order_rows_are_reported_and_not_repaired():
    assert reader_v5.echo([1, 2], verdict(per_comment=[{"msg_id": 1}, {"msg_id": 2}]))[
        "in_list_order"
    ]
    assert not reader_v5.echo([1, 2], verdict(per_comment=[{"msg_id": 2}, {"msg_id": 1}]))[
        "in_list_order"
    ]


# --- the merge --------------------------------------------------------------------------------


def signal(**moves) -> dict:
    body = {
        "signal_type": "спрос",
        "proposed": False,
        "from_post": False,
        "subject_type": "категория_личное",
        "subject_id": "морозиво",
        "aspect": "availability",
        "stance": None,
        "reading": "р",
        "evidence": [1],
        "quote": "ц",
    }
    return body | moves


def test_the_chunks_partition_the_comment_list():
    assert reader_v5.chunks(list(range(43)), 16) == [
        list(range(0, 16)),
        list(range(16, 32)),
        list(range(32, 43)),
    ]
    assert [len(one) for one in reader_v5.chunks(list(range(43)), 16)] == [16, 16, 11]
    assert reader_v5.chunks([], 16) == [[]]
    with pytest.raises(ValueError, match="not a chunk"):
        reader_v5.chunks([1], 0)


def test_per_comment_is_concatenated_in_chunk_order_and_noise_with_it():
    merged = reader_v5.merge(
        [
            verdict(per_comment=[{"msg_id": 1}], noise=[{"msg_id": 2, "class": "оффтоп"}]),
            verdict(per_comment=[{"msg_id": 3}, {"msg_id": 4}]),
        ]
    )
    assert [row["msg_id"] for row in merged["per_comment"]] == [1, 3, 4]
    assert [row["msg_id"] for row in merged["noise"]] == [2]
    assert merged["merged_from"] == 2


def test_a_msg_id_in_two_chunks_is_a_MergeError_and_never_a_row_kept_twice():
    """«Disjoint by construction» is verified, not assumed: the construction is a partition and this
    is what says the answer respected it."""
    with pytest.raises(reader_v5.MergeError, match="chunk 1 and chunk 2"):
        reader_v5.merge(
            [verdict(per_comment=[{"msg_id": 7}]), verdict(per_comment=[{"msg_id": 7}])]
        )


def test_one_signal_read_in_two_chunks_becomes_one_with_its_evidence_UNIONED():
    """The post's subject can legitimately be discussed in every part, so the same finding comes
    back per chunk with different msg_ids. Keying on evidence would keep both copies, which is the
    merge failing to merge."""
    merged = reader_v5.merge(
        [
            verdict(signals=[signal(evidence=[1, 2])]),
            verdict(signals=[signal(evidence=[2, 9], quote="інша")]),
        ]
    )
    assert len(merged["signals"]) == 1
    assert merged["signals"][0]["evidence"] == [1, 2, 9]
    assert reader_v5.SIGNAL_KEY == (
        "signal_type",
        "subject_type",
        "subject_id",
        "aspect",
        "stance",
    )
    # the control: a signal differing on ONE key field stays two signals
    two = reader_v5.merge([verdict(signals=[signal()]), verdict(signals=[signal(aspect="taste")])])
    assert len(two["signals"]) == 2


def test_from_post_survives_the_merge_if_any_chunk_read_it_in_the_post():
    merged = reader_v5.merge(
        [
            verdict(signals=[signal(evidence=[1])]),
            verdict(signals=[signal(evidence=[], from_post=True)]),
        ]
    )
    assert merged["signals"][0]["from_post"] is True


def test_entities_dedupe_on_name_and_msg_id():
    one = {
        "name": "Рудь",
        "msg_id": None,
        "subject_type": "молочный_бренд",
        "reading": "р",
        "quote": "ц",
    }
    merged = reader_v5.merge([verdict(entities=[one]), verdict(entities=[dict(one)])])
    assert len(merged["entities"]) == 1
    both = reader_v5.merge([verdict(entities=[one]), verdict(entities=[dict(one, msg_id=5)])])
    assert len(both["entities"]) == 2


def test_the_prose_fields_keep_the_post_once_and_every_chunks_reading_of_its_own_comments():
    merged = reader_v5.merge(
        [
            verdict(post_summary="про морозиво", discussion_summary="перша частина."),
            verdict(post_summary="про морозиво", discussion_summary="друга частина."),
        ]
    )
    assert merged["post_summary"] == "про морозиво"
    assert merged["discussion_summary"] == "перша частина. друга частина."


def test_chunks_that_name_different_threads_are_refused():
    with pytest.raises(reader_v5.MergeError, match="different threads"):
        reader_v5.merge(
            [verdict(), verdict(thread={"channel": "@c", "post_id": 2})],
        )
    with pytest.raises(reader_v5.MergeError, match="nothing to merge"):
        reader_v5.merge([])


def test_the_merged_verdict_is_the_shape_the_scorer_reads():
    """A merge that produced a different shape would be a second answer format nothing downstream
    could score, so the keys are held against what `parse_reply` returns for one whole thread."""
    whole = prompts.parse_reply(prompts.READER_TASK_V5, json.dumps(verdict(), ensure_ascii=False))
    merged = reader_v5.merge([verdict(), verdict()])
    assert set(whole) <= set(merged)
    assert merged["repairs"] == []
