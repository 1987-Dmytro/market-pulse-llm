"""The two BEFORE columns the paid session bought — re-derived, not re-read.

`lora-c-run r2` STOPped at rung 4 with no adapter, so the only readings it produced are base v2's
and base v3's. They are the columns every later contract of this line is measured against, so the
verdict file is checked against the replies it was computed from rather than trusted.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import score_lora_c_bases as bases  # noqa: E402

from market_pulse import pass1_v3, prompts  # noqa: E402

VERDICT = json.loads((REPO_ROOT / "results" / "lora_c_bases_verdict.json").read_text("utf-8"))


def test_no_bar_is_scored_because_no_arm_exists():
    """The registered three are per ARM, and the smoke OOMed before a single optimizer step."""
    assert "bars" not in VERDICT
    assert "no arm exists" in VERDICT["contract"]
    assert "neither arm exists" in VERDICT["no_bar_is_scored"]


def test_every_reply_parsed_under_the_parser_that_owns_its_task():
    """198 per leg, zero refusals — and the v3 leg is parsed by v3's parser, not v1's."""
    for name, leg in VERDICT["legs"].items():
        assert leg["replies"] == 198, name
        assert leg["parsed"] == 198, name
        assert leg["refused"] == [], name
    assert VERDICT["legs"]["base_v2"]["task"] == prompts.PASS1_TASK_V2
    assert VERDICT["legs"]["base_v3"]["task"] == pass1_v3.PASS1_TASK_V3


def test_the_agreement_is_the_shipped_judges_own_arithmetic():
    """Re-derived from the rows the judge returned — a rate is `agreed / n` or it is a second one."""
    for name, leg in VERDICT["legs"].items():
        for key in ("agreement_on_every_labelled_row_of_E", "agreement_on_the_holdout_rows_of_E"):
            one = leg[key]
            assert one["agreed"] + one["disagreed"] + one["absent"] == one["n"], (name, key)
            assert one["rate"] == one["agreed"] / one["n"], (name, key)
            assert sum(row["agreed"] for row in one["rows"]) == one["agreed"], (name, key)
            assert len(one["rows"]) == one["n"], (name, key)


def test_the_join_is_on_the_thread_and_the_msg_id():
    """E draws from eight channels and a Telegram id is unique inside one, not across them.

    Measured rather than asserted: if a bare `msg_id` were a key here, these rows would collide.
    """
    pack = json.loads((REPO_ROOT / "results" / "lora_c_eval_pack.json").read_text("utf-8"))
    items = pack["legs"][0]["items"]
    channels = {one["channel"] for one in items}
    assert len(channels) > 1
    assert VERDICT["population"]["join"].startswith("(thread, msg_id)")
    assert VERDICT["population"]["eval_set_E"] == len(items) == 198


def test_base_v3_is_the_control_and_it_moved():
    """The reading the control column exists for, stated as the two numbers rather than as a claim.

    Without base v3 nothing separates «the adapter learned» from «a sentence of reasoning helped».
    The pair is what this session bought before it stopped, so the direction is asserted here — and
    the bar's own integer is quoted beside it as CONTEXT, never as a verdict: base v3 takes no bar.
    """
    v2 = VERDICT["legs"]["base_v2"]["agreement_on_the_holdout_rows_of_E"]
    v3 = VERDICT["legs"]["base_v3"]["agreement_on_the_holdout_rows_of_E"]
    assert v2["n"] == v3["n"] == 98, "the reachable maximum — two holdout rows cannot be rendered"
    assert v3["agreed"] > v2["agreed"]
    registration = json.loads((REPO_ROOT / "results" / "prereg_lora_c.json").read_text("utf-8"))
    assert registration["bars"]["P1_holdout_agreement"]["minimum_agreed"] == 64
    assert registration["legs"]["base_v3"]["bar"] is None


def test_the_producer_is_driven_end_to_end_and_rebuilds_its_bytes(tmp_path):
    """The record on disk is what today's producer emits, or it describes a producer that moved."""
    out = tmp_path / "again.json"
    done = subprocess.run(
        [sys.executable, "scripts/score_lora_c_bases.py", "--out", str(out)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={"PYTHONPATH": "src", "PATH": "/usr/bin:/bin:/usr/local/bin"},
    )
    assert done.returncode == 0, done.stderr[-2000:]
    assert out.read_bytes() == (REPO_ROOT / "results" / "lora_c_bases_verdict.json").read_bytes()


def test_a_thread_keyed_call_is_what_the_shipped_judge_gets(monkeypatch):
    """`reader_comment_agreement` keys on `msg_id`, so it is called once per thread — driven."""
    seen = []
    real = bases.scorer.reader_comment_agreement

    def spy(gold, per_comment):
        seen.append({one["msg_id"] for one in gold})
        return real(gold, per_comment)

    monkeypatch.setattr(bases.scorer, "reader_comment_agreement", spy)
    labels = {("@a:1", 10): "не_наш_рынок", ("@b:2", 10): "сеть_ритейлер"}
    answers = {("@a:1", 10): {"subject_type": "не_наш_рынок"}, ("@b:2", 10): {"subject_type": None}}
    got = bases.agreement(answers, labels)
    assert len(seen) == 2, "one call per thread — a single call would collide on msg_id 10"
    assert got["n"] == 2 and got["agreed"] == 1
