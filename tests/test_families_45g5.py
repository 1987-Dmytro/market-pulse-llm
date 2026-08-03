"""The two families are counted, and both discriminators are shown their blind spot (4.5g5)."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import measure_families_45g5 as families  # noqa: E402


def comment(msg_id, *, parent=100, reply_to=..., sender="s1", channel="@c"):
    row = {
        "channel": channel,
        "msg_id": msg_id,
        "parent_msg_id": parent,
        "sender_anon_id": sender,
    }
    if reply_to is not ...:
        row["reply_to_msg_id"] = reply_to
    return row


# --- the discriminator ------------------------------------------------------------------


def test_the_thread_head_is_the_smallest_reply_target():
    """The group's mirror of the post exists before any comment on it."""
    rows = [comment(20, reply_to=10), comment(21, reply_to=10), comment(22, reply_to=20)]

    assert families.heads(rows) == {("@c", 100): 10}


def test_a_reply_to_the_head_is_not_a_reply_to_a_comment():
    rows = [comment(20, reply_to=10), comment(21, reply_to=20)]
    found = families.replies_to_comments(rows)

    assert found["ids"] == ["@c:21"]
    assert found["by_membership"] == ["@c:21"]
    assert found["disagree"] == []


def test_a_reply_to_a_deleted_comment_is_still_a_reply_to_a_comment():
    """Membership cannot see it — the target is gone from the store. The head test can."""
    rows = [comment(20, reply_to=10), comment(21, reply_to=15)]
    found = families.replies_to_comments(rows)

    assert found["ids"] == ["@c:21"]
    assert found["by_membership"] == []
    assert found["disagree"] == ["@c:21"]


def test_threads_are_kept_apart():
    rows = [comment(20, parent=100, reply_to=10), comment(40, parent=200, reply_to=30)]

    assert families.replies_to_comments(rows)["ids"] == []


def test_a_thread_whose_head_nobody_answered_is_reported_not_guessed():
    """Every target is a collected comment, so the smallest one is not the head. Those rows read
    as top-level and the thread is named rather than quietly counted."""
    rows = [comment(20, reply_to=21), comment(21, reply_to=22), comment(22, reply_to=20)]
    found = families.replies_to_comments(rows)

    assert found["threads_with_no_observed_head"] == ["@c:100"]


def test_a_row_that_was_not_refetched_is_counted_apart():
    rows = [comment(20, reply_to=10), comment(21)]
    found = families.replies_to_comments(rows)

    assert found["rows_not_refetched"] == ["@c:21"]
    assert found["ids"] == []


def test_a_null_target_is_neither_a_reply_nor_missing():
    rows = [comment(20, reply_to=10), comment(21, reply_to=None)]
    found = families.replies_to_comments(rows)

    assert found["ids"] == []
    assert found["rows_not_refetched"] == []


# --- the sender family ------------------------------------------------------------------


def test_the_busiest_senders_and_the_gap_to_the_next():
    rows = (
        [comment(i, sender="a") for i in range(10)]
        + [comment(100 + i, sender="b") for i in range(5)]
        + [comment(200 + i, sender="c") for i in range(2)]
    )
    found = families.hyperactive(rows, n=2)

    assert [s["sender_anon_id"] for s in found["senders"]] == ["a", "b"]
    assert found["next_busiest"] == 2
    assert len(found["ids"]) == 15
    assert set(found["per_sender_ids"]) == {"a", "b"}


def test_a_sender_telegram_never_gave_us_is_not_a_family():
    rows = [comment(1, sender=None), comment(2, sender=None), comment(3, sender="a")]

    assert [s["sender_anon_id"] for s in families.hyperactive(rows, n=1)["senders"]] == ["a"]


# --- the counts -------------------------------------------------------------------------


def test_a_family_is_counted_against_every_denominator():
    pop = {
        "batch": {"@c:1", "@c:2", "@c:3"},
        "labels": {
            "@c:1": {"unclear": False},
            "@c:2": {"unclear": True},
            "@c:3": {"unclear": False},
        },
        "judged": {"@c:1": "correct", "@c:2": "correct", "@c:3": "incorrect"},
        "comments": 50,
    }
    out = families.spread({"@c:1", "@c:2", "@c:9"}, pop)

    assert out["all_comments"] == {"n": 3, "of": 50}
    assert out["batch"] == {"n": 2, "of": 3}
    assert out["errors"] == {"n": 0, "of": 1}
    assert out["judged"]["correct"] == {"n": 2, "of": 2}
    assert out["judged_correct_with_unclear_false"] == 1
