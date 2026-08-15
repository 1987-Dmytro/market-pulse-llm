"""The probe's driver, driven end to end by a fake endpoint — every branch that decides money.

An import proves nothing about a driver ([[stub_driven_script_verification]]): what has to be
exercised here is the handshake's refusal, the go/no-go arithmetic on both sides of its threshold,
the refusal to open a run the gate said STOP to, and the rule that a thread already in the evidence
file is never bought twice.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import read_threads_probe as driver  # noqa: E402
import runpod_guard as guard  # noqa: E402

from market_pulse import prompts  # noqa: E402

RECORD = json.loads((REPO_ROOT / "results" / "prereg_reader_probe.json").read_text("utf-8"))

VERDICT = json.dumps(
    {
        "thread": {"channel": "@c", "post_id": 1},
        "post_summary": "п",
        "discussion_summary": "д",
        "entities": [],
        "signals": [],
        "per_comment": [],
        "noise": [],
    },
    ensure_ascii=False,
)


class FakeEndpoint:
    """A worker that answers what the registration expects, and bills what the test tells it to."""

    def __init__(self, *, seconds_per_thread: float = 2.0, reply: str = VERDICT, info=None):
        self.seconds_per_thread = seconds_per_thread
        self.reply = reply
        self.asked = []
        self.worker_seconds = 0.0
        self._info = info

    def info(self) -> dict:
        if self._info is not None:
            return self._info
        block = RECORD["instruments"]["serving"]
        return {
            "serving_config": block["serving_config"],
            "merge_state": block["merge_state"],
            "adapter_sha256": None,
            "quantization": block["quantization"],
            "chat_template": block["chat_template"],
            "max_new_tokens": RECORD["instruments"]["ceilings"]["output_tokens"],
            "model": block["model"],
            "revision_requested": block["model_revision"],
            "reader_prompt_sha256": prompts.prompt_sha256(prompts.READER_TASK),
            "repo_commit": "cafebabe",
        }

    def read(self, task, threads):
        assert task == prompts.READER_TASK
        self.asked += [f"{one['channel']}:{one['post_id']}" for one in threads]
        self.worker_seconds += self.seconds_per_thread * len(threads)
        return [{"content": self.reply, "finish_reason": "stop", "usage": {}} for _ in threads]

    def timing(self) -> dict:
        return {"worker_seconds": self.worker_seconds, "wall_seconds": self.worker_seconds}


@pytest.fixture
def bench(tmp_path, monkeypatch):
    """The driver with its three files in a temp directory and no balance call to RunPod."""
    monkeypatch.setattr(driver, "EVIDENCE", tmp_path / "reader_probe_w1.jsonl")
    monkeypatch.setattr(driver, "LEDGER", tmp_path / "spend_probe_a.json")
    monkeypatch.setattr(driver, "RECORD", tmp_path / "reader_probe_run.json")
    monkeypatch.setattr(guard, "balance", lambda: 23.08)
    return tmp_path


def run(argv, endpoint):
    return driver.main(argv, client_factory=lambda: endpoint)


def test_the_handshake_refuses_a_worker_that_is_not_what_was_registered(bench):
    ok = FakeEndpoint()
    assert run(["--endpoint", "x", "--handshake"], ok) == 0
    # the volume a session behind: every field right except the prompt it serves
    stale = FakeEndpoint(info={**ok.info(), "reader_prompt_sha256": "0" * 64})
    with pytest.raises(SystemExit, match="not at this session's commit"):
        run(["--endpoint", "x", "--handshake"], stale)
    # and the config itself, which `assert_serving` refuses one layer earlier
    wrong = FakeEndpoint(info={**ok.info(), "serving_config": "CAPTION"})
    with pytest.raises(SystemExit, match="not serving the registered configuration"):
        run(["--endpoint", "x", "--handshake"], wrong)


def test_the_warm_up_buys_the_registered_draw_and_nothing_else(bench):
    endpoint = FakeEndpoint(seconds_per_thread=2.0)
    assert run(["--endpoint", "x", "--warm-up"], endpoint) == 0
    drawn = [driver.key_of(one) for one in RECORD["go_no_go"]["warm_up"]["drawn"]]
    assert endpoint.asked == drawn
    rows = [json.loads(line) for line in driver.EVIDENCE.read_text("utf-8").splitlines()]
    assert [row["thread"] for row in rows] == drawn
    assert all(row["parsed"] and row["parse_error"] is None for row in rows)
    assert all(len(row["rendering_sha256"]) == 64 for row in rows)
    # a second warm-up buys nothing: the evidence file is what says a thread was already read
    again = FakeEndpoint(seconds_per_thread=2.0)
    assert run(["--endpoint", "x", "--warm-up"], again) == 0
    assert again.asked == []


def test_the_gate_projects_both_ways_and_the_pessimistic_one_binds(bench):
    """Hand-computed. The draw is 3 threads carrying 11 payable comments; at 2 s a thread the
    warm-up bills 6 s. Per thread that is 2 s → 222 s for 111; per payable comment 6/11 s →
    497.45 s for 912. The larger binds, and 497.45 s × $0.00030669 = $0.1526 — inside what the cap
    has left, so GO."""
    endpoint = FakeEndpoint(seconds_per_thread=2.0)
    assert run(["--endpoint", "x", "--warm-up"], endpoint) == 0
    gate = json.loads(driver.RECORD.read_text("utf-8"))["go_no_go"]
    assert gate["warm_up"] == {
        "threads": 3,
        "payable_comments": 11,
        "billed_seconds": 6.0,
        "seconds_per_thread": 2.0,
        "seconds_per_payable_comment": 0.545,
    }
    assert gate["projections"]["by_thread"]["seconds"] == 222.0
    assert gate["projections"]["by_payable_comment"]["seconds"] == pytest.approx(497.5, abs=0.1)
    assert gate["projections"]["binding"]["which"] == "by_payable_comment"
    assert gate["projections"]["binding"]["usd"] == pytest.approx(0.1526, abs=0.0005)
    assert gate["verdict"] == "GO"


def test_a_projection_over_the_cap_stops_the_run_and_the_run_refuses_to_open(bench):
    """The same draw at 10 s a thread: 30 s billed, 2 487 s projected by payable comment, $0.7628 —
    over what $0.45 has left. The gate says STOP, the exit code says STOP, and `--run` refuses."""
    endpoint = FakeEndpoint(seconds_per_thread=10.0)
    assert run(["--endpoint", "x", "--warm-up"], endpoint) == 2
    gate = json.loads(driver.RECORD.read_text("utf-8"))["go_no_go"]
    assert gate["projections"]["binding"]["usd"] == pytest.approx(0.7628, abs=0.001)
    assert gate["verdict"] == "STOP"
    with pytest.raises(SystemExit, match="the go/no-go verdict is STOP"):
        run(["--endpoint", "x", "--run"], FakeEndpoint())


def test_after_a_go_the_run_reads_the_rest_and_never_the_warm_up_again(bench):
    endpoint = FakeEndpoint(seconds_per_thread=2.0)
    assert run(["--endpoint", "x", "--warm-up"], endpoint) == 0
    rest = FakeEndpoint(seconds_per_thread=2.0)
    assert run(["--endpoint", "x", "--run"], rest) == 0
    drawn = {driver.key_of(one) for one in RECORD["go_no_go"]["warm_up"]["drawn"]}
    assert len(rest.asked) == RECORD["population"]["threads"] - len(drawn)
    assert not drawn & set(rest.asked)
    rows = [json.loads(line) for line in driver.EVIDENCE.read_text("utf-8").splitlines()]
    assert len(rows) == RECORD["population"]["threads"]
    assert len({row["thread"] for row in rows}) == RECORD["population"]["threads"]


def test_a_reply_that_cannot_be_parsed_is_kept_with_its_reason(bench):
    """An unreadable verdict is evidence too: the row is persisted, the reason is named, and the
    driver does not stop — «нет сигнала» and «could not be read» are two different answers."""
    endpoint = FakeEndpoint(seconds_per_thread=1.0, reply="not json at all")
    assert run(["--endpoint", "x", "--warm-up"], endpoint) in (0, 2)
    rows = [json.loads(line) for line in driver.EVIDENCE.read_text("utf-8").splitlines()]
    assert len(rows) == 3
    assert all(row["parsed"] is None for row in rows)
    assert {row["parse_error"] for row in rows} == {"no JSON object in reply"}


def test_a_population_that_moved_under_the_registration_is_refused(bench, monkeypatch):
    monkeypatch.setattr(
        driver.population,
        "population",
        lambda: [{"channel": "@x", "post_id": 1, "post_text": "", "comments": []}],
    )
    with pytest.raises(SystemExit, match="the registration pinned"):
        run(["--endpoint", "x", "--handshake"], FakeEndpoint())


def test_the_ledger_is_anchored_before_the_first_request_and_never_regenerated(bench):
    endpoint = FakeEndpoint()
    run(["--endpoint", "x", "--handshake"], endpoint)
    first = json.loads(driver.LEDGER.read_text("utf-8"))
    assert first["runpod_balance_at_probe-a_start"] == 23.08
    assert first["probe-a_cap_usd"] == RECORD["money"]["cap_usd_all_in"] == 0.45
    run(["--endpoint", "x", "--handshake"], endpoint)
    again = json.loads(driver.LEDGER.read_text("utf-8"))
    assert again["anchored_at"] == first["anchored_at"], "the anchor must survive a second run"
