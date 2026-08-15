"""`scripts/score_reader_probe_b.py` — the five bars, driven over verdicts built for the purpose.

probe-a's scorer never computed a bar: its go/no-go stopped the run before any bar's threads were
read, so every cell said UNSCORED and the arithmetic behind them had never run against a verdict.
That is the one failure this contract cannot absorb — a bar computation that raises after the money
is spent — so the whole path is driven here, at $0, before the endpoint exists.

Two subjects, and both are needed:

- a synthetic PERFECT reader built out of the gold, then broken one field at a time, so each bar is
  shown to pass and to fail for its own reason;
- probe-a's three REAL paid replies, coerced to v2's container shape, so the plumbing that turns a
  raw reply into a scored entity — the parser, the watchlist matcher, the brand resolution — is
  exercised on model output rather than on a fixture the test wrote itself.
"""

import json
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import probe_b_population as subset  # noqa: E402
import score_reader_probe_b as scoring  # noqa: E402

from market_pulse import prompts  # noqa: E402

GOLD = json.loads((REPO_ROOT / "results" / "reader_gold_w1.json").read_text(encoding="utf-8"))
PREREG = json.loads(
    (REPO_ROOT / "results" / "prereg_reader_probe_v2.json").read_text(encoding="utf-8")
)
PROBE_A_EVIDENCE = REPO_ROOT / "results" / "reader_probe_w1.jsonl"

# names the watchlist matcher really resolves — checked in the first test below, so a registry
# change makes the fixture fail loudly instead of scoring a bar against a brand nobody matches
BRAND_NAMES = {
    "garmonija": "Гармонія",
    "selianske": "Селянське",
    "varus-pl": "Varus",
    "varto": "варто",
}


def empty(thread: str) -> dict:
    channel, post_id = thread.rsplit(":", 1)
    return {
        "thread": {"channel": channel, "post_id": int(post_id)},
        "post_summary": "п",
        "discussion_summary": "д",
        "entities": [],
        "signals": [],
        "per_comment": [],
        "noise": [],
    }


def perfect() -> dict[str, dict]:
    """A reader that answers every gold case exactly — the fixture every failing case is built from."""
    verdicts = {
        subset.key(one["channel"], one["post_id"]): empty(
            subset.key(one["channel"], one["post_id"])
        )
        for one in subset.population()
    }
    for case in GOLD["flagships"]:
        body = verdicts[subset.key(case["channel"], case["post_id"])]
        for signal in case["signals"]:
            body["signals"].append(
                {
                    "signal_type": signal["signal_type"],
                    "proposed": False,
                    "from_post": False,
                    "subject_type": signal["subject_type"],
                    "subject_id": None,
                    "aspect": signal["aspect"],
                    "stance": signal.get("stance"),
                    "reading": "читання",
                    "evidence": list(signal["evidence"]),
                    "quote": "цитата",
                }
            )
    for case in GOLD["entity_cases"]:
        if case["subject_type"] is None:  # E4: the ruling is that NOTHING is reported
            continue
        body = verdicts[subset.key(case["channel"], case["post_id"])]
        body["entities"].append(
            {
                "name": BRAND_NAMES[case["brand_id"]],
                "msg_id": case["msg_id"],
                "subject_type": case["subject_type"],
                "reading": "читання",
                "quote": BRAND_NAMES[case["brand_id"]],
            }
        )
    for row in GOLD["per_comment"]:
        body = verdicts[subset.key(row["channel"], row["evidence_row"]["post_id_in_the_store"])]
        body["per_comment"].append(
            {
                "msg_id": row["msg_id"],
                "subject_type": row["subject_type"],
                "subject_id": row.get("subject_id"),
                "stance": row.get("stance"),
                "aspects": [],
                "note": None,
            }
        )
    return verdicts


def evidence_file(path: Path, verdicts: dict[str, dict], *, only: set[str] | None = None) -> Path:
    kept = {subset.key(one["channel"], one["post_id"]): one for one in subset.population()}
    lines = []
    for thread, body in verdicts.items():
        if only is not None and thread not in only:
            continue
        one = kept[thread]
        lines.append(
            {
                "thread": thread,
                "channel": one["channel"],
                "post_id": one["post_id"],
                "injected": one["injected"],
                "cases": one["cases"],
                "payable_comments": len(one["comments"]),
                "task": prompts.READER_TASK_V2,
                "reply": json.dumps(body, ensure_ascii=False),
                "finish_reason": "stop",
                "usage": {},
                "parsed": body,
                "parse_error": None,
                "seconds": {"wall": 1.0, "worker": 1.0},
            }
        )
    path.write_text(
        "\n".join(json.dumps(one, ensure_ascii=False) for one in lines) + "\n", encoding="utf-8"
    )
    return path


@pytest.fixture
def score(tmp_path, monkeypatch):
    """`build()` over an evidence file this test wrote, with no run record beside it."""

    def run(verdicts, *, only=None):
        monkeypatch.setattr(
            scoring, "EVIDENCE", evidence_file(tmp_path / "evidence.jsonl", verdicts, only=only)
        )
        monkeypatch.setattr(scoring, "RUN", tmp_path / "no-such-run.json")
        return scoring.build()

    return run


def test_the_fixture_names_brands_the_matcher_really_resolves():
    """The premise of every bar-2 assertion below. A registry change that stopped resolving one of
    these would otherwise turn into «the reader missed the case»
    ([[the_control_whose_premise_stopped_being_true]])."""
    table = scoring.aliases()
    for brand_id, name in BRAND_NAMES.items():
        entity = scoring.resolved([{"name": name, "quote": name}], table)[0]
        assert entity["brand_ids"] == [brand_id], name


def test_a_perfect_reader_passes_every_bar(score):
    record = score(perfect())
    assert record["evidence"]["threads_read"] == 23
    assert record["evidence"]["injected_read"] == 4
    for name, state in record["bars"].items():
        assert state["verdict"] == "SCORED", name
        assert state["result"]["passed"] is True, name
    assert record["bars"]["1_flagships"]["result"]["cases_answered"] == 5
    assert record["bars"]["2_entity_cases"]["result"]["cases_answered"] == 4
    assert record["bars"]["3_noise"]["result"]["signals"] == 0
    agreement = record["bars"]["4_per_comment_agreement"]["result"]
    assert (agreement["n"], agreement["agreed"], agreement["absent"]) == (14, 14, 0)
    assert agreement["rate"] == 1.0


@pytest.mark.parametrize(
    ("bar", "break_it"),
    [
        (
            "1_flagships",
            lambda v: v["@VARUS_channel:10613"]["signals"].pop(0),
        ),
        (
            "2_entity_cases",
            lambda v: v["@VARUS_channel:10360"]["entities"].clear(),
        ),
        (
            "3_noise",
            lambda v: v["@retsepty:7312"]["signals"].append(
                {
                    "signal_type": "жалоба",
                    "proposed": False,
                    "from_post": False,
                    "subject_type": "категория",
                    "subject_id": None,
                    "aspect": "price",
                    "stance": "negative",
                    "reading": "читання",
                    "evidence": [1],
                    "quote": "ц",
                }
            ),
        ),
        (
            "4_per_comment_agreement",
            lambda v: [v["@VARUS_channel:10613"]["per_comment"].pop() for _ in range(3)],
        ),
    ],
)
def test_each_bar_fails_for_its_own_reason(score, bar, break_it):
    """The negative control, one bar at a time: a suite where only the passing case is exercised
    cannot tell a computed bar from a constant."""
    verdicts = perfect()
    break_it(verdicts)
    record = score(verdicts)
    assert record["bars"][bar]["result"]["passed"] is False, bar
    others = [
        name
        for name, state in record["bars"].items()
        if name != bar and state["result"]["passed"] is not True
    ]
    assert others == [], others


def test_e4_is_answered_only_when_neither_thread_names_varto(score):
    """One ruling about two threads: «чи варто» is the adverb, so the case is answered when NO
    entity in EITHER thread resolves to varto."""
    verdicts = perfect()
    verdicts["@mandziak:3684"]["entities"].append(
        {
            "name": "варто",
            "msg_id": 48099,
            "subject_type": "молочный_бренд",
            "reading": "читання",
            "quote": "чи варто",
        }
    )
    record = score(verdicts)
    entity = record["bars"]["2_entity_cases"]["result"]
    assert entity["per_case"]["E4"] is False
    assert entity["cases_answered"] == 3 and entity["passed"] is False


def test_a_bar_whose_threads_were_not_read_is_unscored_and_never_zero(score):
    """The rule probe-a's run made real: a rate over the threads that happened to be read is a
    number about another sample."""
    verdicts = perfect()
    warm = set(PREREG["go_no_go"]["warm_up"]["threads"])
    record = score(verdicts, only=warm)
    assert record["evidence"]["threads_read"] == 3
    for name, state in record["bars"].items():
        assert state["verdict"] == "UNSCORED", name
        assert state["result"] is None
        assert "another sample" in state["reason"]


def test_the_collapsed_vocabulary_reading_is_reported_and_never_gates(score):
    """A reader that answers «категория_личное» where the reference says «категория» disagrees on a
    word the two authorities disagree about. The bar is scored as registered — it fails — and the
    collapsed reading beside it says the reading itself was right."""
    verdicts = perfect()
    for body in verdicts.values():
        for row in body["per_comment"]:
            if row["subject_type"] == "категория":
                row["subject_type"] = "категория_личное"
        for row in body["signals"]:
            if row["subject_type"] == "категория":
                row["subject_type"] = "категория_личное"
    record = score(verdicts)

    assert record["bars"]["4_per_comment_agreement"]["result"]["passed"] is False
    assert record["bars"]["4_per_comment_agreement"]["result"]["rate"] == pytest.approx(6 / 14)
    assert record["bars"]["1_flagships"]["result"]["passed"] is False

    beside = record["collapsed_vocabulary_reading"]["bars"]
    assert beside["4_per_comment_agreement"]["as_registered"] == pytest.approx(6 / 14)
    assert beside["4_per_comment_agreement"]["collapsed"] == 1.0
    assert beside["1_flagships"]["as_registered"] < beside["1_flagships"]["collapsed"] == 5
    # and the collapse is never applied to the gating cells
    assert record["bars"]["4_per_comment_agreement"]["result"]["rate"] != 1.0


def test_the_whole_path_runs_on_probe_a_s_real_replies_coerced_to_v2(score, tmp_path, monkeypatch):
    """The plumbing, on model output rather than on a fixture this test wrote.

    probe-a bought three verdicts and the parser refused all three: `entities` came back as a map
    keyed by the name (Dv393) and one signal carried `evidence: [null]` (Dv394). Coerced to the
    shape v2's wording now asks for — and ONLY the container and that one field — all three parse,
    the `from_post` signal among them, which is the cheapest evidence there is that the two wording
    changes address the defects that were measured rather than defects that were guessed.
    """
    coerced = {}
    for line in PROBE_A_EVIDENCE.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        row = json.loads(line)
        body = json.loads(re.sub(r"^[^{]*", "", row["reply"], count=1))
        if isinstance(body.get("entities"), dict):
            body["entities"] = [{"name": name, **one} for name, one in body["entities"].items()]
        for signal in body.get("signals") or []:
            if signal.get("evidence") == [None]:
                signal["evidence"], signal["from_post"] = [], True
        coerced[row["thread"]] = prompts.parse_reply(
            prompts.READER_TASK_V2, json.dumps(body, ensure_ascii=False)
        )

    assert len(coerced) == 3
    record = score(coerced, only=set(coerced))
    assert record["replies"]["parsed"] == 3 and record["replies"]["refused"] == 0
    assert record["replies"]["from_post_signals"] == 1
    assert record["replies"]["signal_bearing"] == 2 and record["replies"]["no_signal"] == 1
    # the bars live in the other twenty threads and say so rather than scoring these three
    assert all(state["verdict"] == "UNSCORED" for state in record["bars"].values())
