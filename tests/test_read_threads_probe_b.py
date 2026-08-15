"""probe-b's driver, driven end to end by a fake endpoint — every branch that decides money.

An import proves nothing about a driver ([[stub_driven_script_verification]]). What is exercised
here is the handshake's refusal on either registered prompt, the corrected go/no-go arithmetic on
both sides of its threshold, the refusal to open a run the gate said STOP to, the per-thread request
sha, and the rule that a thread already in the evidence file is never bought twice.

The arithmetic test is the one that matters most: v1's driver projected the WHOLE population against
the cap's leftover and counted the warm-up twice. The numbers below are hand-computed for the
corrected rule, and one of them is a case v1 would have called STOP.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import read_threads_probe_b as driver  # noqa: E402
import runpod_guard as guard  # noqa: E402

from market_pulse import prompts  # noqa: E402

RECORD = json.loads((REPO_ROOT / "results" / "prereg_reader_probe_v2.json").read_text("utf-8"))
RATE = RECORD["money"]["arithmetic"]["rate_usd_per_second"]
SETUP = RECORD["money"]["arithmetic"]["setup_usd"]

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
            "reader_prompt_sha256": {
                task: prompts.prompt_sha256(task) for task in sorted(prompts.READER)
            },
            "repo_commit": "cafebabe",
            "runtime": {"gpu_name": "NVIDIA GeForce RTX 4090"},
        }

    def read(self, task, threads):
        assert task == prompts.READER_TASK_V2
        self.asked += [f"{one['channel']}:{one['post_id']}" for one in threads]
        self.worker_seconds += self.seconds_per_thread * len(threads)
        return [{"content": self.reply, "finish_reason": "stop", "usage": {}} for _ in threads]

    def timing(self) -> dict:
        return {"worker_seconds": self.worker_seconds, "wall_seconds": self.worker_seconds}


@pytest.fixture
def bench(tmp_path, monkeypatch):
    """The driver with its three files in a temp directory and no balance call to RunPod."""
    monkeypatch.setattr(driver, "EVIDENCE", tmp_path / "reader_probe_b_w1.jsonl")
    monkeypatch.setattr(driver, "LEDGER", tmp_path / "spend_probe_b.json")
    monkeypatch.setattr(driver, "RECORD", tmp_path / "reader_probe_b_run.json")
    monkeypatch.setattr(guard, "balance", lambda: 22.99)
    return tmp_path


def run(argv, endpoint):
    return driver.main(argv, client_factory=lambda: endpoint)


def test_the_handshake_refuses_a_worker_that_is_behind_on_either_registered_prompt(bench):
    """Two registered reader texts, and a worker that matched only the one this run reads with could
    still be a session behind on the other — which is exactly the state a half-applied volume fetch
    leaves. The whole dict is compared, and the message names the task that disagrees."""
    ok = FakeEndpoint()
    assert run(["--endpoint", "x", "--handshake"], ok) == 0

    for stale_task in sorted(prompts.READER):
        shas = {**ok.info()["reader_prompt_sha256"], stale_task: "0" * 64}
        stale = FakeEndpoint(info={**ok.info(), "reader_prompt_sha256": shas})
        with pytest.raises(SystemExit, match="not at this session's commit") as err:
            run(["--endpoint", "x", "--handshake"], stale)
        assert stale_task in str(err.value)

    # a scalar is what v1's worker answered with, and it is no longer a registered shape: the
    # message says so rather than diffing a string key by key
    scalar = FakeEndpoint(
        info={**ok.info(), "reader_prompt_sha256": prompts.prompt_sha256(prompts.READER_TASK_V2)}
    )
    with pytest.raises(SystemExit, match="the field is not a per-task map"):
        run(["--endpoint", "x", "--handshake"], scalar)

    # and the config itself, which `assert_serving` refuses one layer later
    wrong = FakeEndpoint(info={**ok.info(), "serving_config": "CAPTION"})
    with pytest.raises(SystemExit, match="not serving the registered configuration"):
        run(["--endpoint", "x", "--handshake"], wrong)


def test_the_warm_up_buys_the_registered_draw_and_nothing_else(bench):
    endpoint = FakeEndpoint(seconds_per_thread=2.0)
    assert run(["--endpoint", "x", "--warm-up"], endpoint) == 0
    drawn = list(RECORD["go_no_go"]["warm_up"]["threads"])
    assert sorted(endpoint.asked) == sorted(drawn)
    rows = [json.loads(line) for line in driver.EVIDENCE.read_text("utf-8").splitlines()]
    assert sorted(row["thread"] for row in rows) == sorted(drawn)
    assert all(row["parsed"] and row["parse_error"] is None for row in rows)
    assert all(row["task"] == prompts.READER_TASK_V2 for row in rows)
    assert all(len(row["rendering_sha256"]) == 64 for row in rows)
    assert all(row["injected"] is False for row in rows), "the draw is inside the census cell"
    # a second warm-up buys nothing: the evidence file is what says a thread was already read —
    # and the gate it recomputes reads its seconds from those rows, because a fresh client reports
    # zero billed seconds and a projection over zero would say GO on a run nobody priced
    again = FakeEndpoint(seconds_per_thread=2.0)
    assert run(["--endpoint", "x", "--warm-up"], again) == 0
    assert again.asked == []
    gate = json.loads(driver.RECORD.read_text("utf-8"))["go_no_go"]
    assert gate["warm_up"]["billed_seconds"] == 6.0
    assert gate["warm_up"]["seconds_per_thread"] == 2.0


def test_the_gate_projects_the_remainder_and_the_pessimistic_projection_binds(bench):
    """Hand-computed, and the case v1's arithmetic would have got wrong.

    The draw is 3 threads carrying 11 payable comments; at 12 s a thread the warm-up bills 36 s.
    The REMAINDER is 20 threads and 123 payable comments, so per thread 12 s → 240 s, and per
    payable comment 36/11 s → 402.5 s. The larger binds: 402.5 s × $0.00030669 = $0.1234, plus the
    warm-up's own $0.0110 and the registered setup $0.0440 → $0.1784 of $0.35. GO.

    v1's rule would have projected all 23 threads by payable comment — 134 × 36/11 = 438.5 s — and
    compared it against the cap MINUS the warm-up, double-counting the three threads it had just
    bought.
    """
    endpoint = FakeEndpoint(seconds_per_thread=12.0)
    assert run(["--endpoint", "x", "--warm-up"], endpoint) == 0
    gate = json.loads(driver.RECORD.read_text("utf-8"))["go_no_go"]

    assert gate["warm_up"]["threads"] == 3
    assert gate["warm_up"]["payable_comments"] == 11
    assert gate["warm_up"]["billed_seconds"] == 36.0
    assert gate["remainder"] == {"threads": 20, "payable_comments": 123}
    assert gate["projections"]["by_thread"]["seconds"] == 240.0
    assert gate["projections"]["by_payable_comment"]["seconds"] == pytest.approx(402.5, abs=0.1)
    assert gate["projections"]["binding"]["which"] == "by_payable_comment"
    assert gate["projections"]["binding"]["usd"] == pytest.approx(402.5 * RATE, abs=0.0005)

    money = gate["money"]
    assert money["setup_usd"] == SETUP
    assert money["warm_up_usd"] == pytest.approx(36.0 * RATE, abs=0.0005)
    assert money["projected_total_usd"] == pytest.approx(SETUP + (36.0 + 402.5) * RATE, abs=0.0005)
    assert money["projected_total_usd"] < money["cap_usd_all_in"]
    assert gate["verdict"] == "GO"

    # the speedup the registration asked the warm-up to measure, computed against probe-a's L4
    speed = gate["warm_up"]["probe_a_on_an_l4"]
    assert speed["speedup_per_thread"] == pytest.approx(54.806 / 12.0, abs=0.001)
    assert speed["break_even_registered"] == RECORD["money"]["arithmetic"]["break_even_speedup"]


def test_a_projection_over_the_cap_stops_the_run_and_the_run_refuses_to_open(bench):
    """The same draw at 40 s a thread: 120 s billed, the remainder 123 payable × 120/11 = 1341.8 s,
    $0.4115 — plus $0.0368 of warm-up and $0.0440 of setup is $0.4923, over the $0.35 cap. STOP, the
    exit code says STOP, and `--run` refuses to open on it."""
    endpoint = FakeEndpoint(seconds_per_thread=40.0)
    assert run(["--endpoint", "x", "--warm-up"], endpoint) == 2
    gate = json.loads(driver.RECORD.read_text("utf-8"))["go_no_go"]
    assert gate["projections"]["binding"]["seconds"] == pytest.approx(1341.8, abs=0.2)
    assert gate["money"]["projected_total_usd"] > gate["money"]["cap_usd_all_in"]
    assert gate["verdict"] == "STOP"
    with pytest.raises(SystemExit, match="the go/no-go verdict is STOP"):
        run(["--endpoint", "x", "--run"], FakeEndpoint())


def test_after_a_go_the_run_reads_the_rest_including_the_injected_threads(bench):
    endpoint = FakeEndpoint(seconds_per_thread=2.0)
    assert run(["--endpoint", "x", "--warm-up"], endpoint) == 0
    rest = FakeEndpoint(seconds_per_thread=2.0)
    assert run(["--endpoint", "x", "--run"], rest) == 0

    drawn = set(RECORD["go_no_go"]["warm_up"]["threads"])
    assert len(rest.asked) == RECORD["population"]["threads"] - len(drawn)
    assert not drawn & set(rest.asked)
    rows = [json.loads(line) for line in driver.EVIDENCE.read_text("utf-8").splitlines()]
    assert len(rows) == RECORD["population"]["threads"] == 23
    assert len({row["thread"] for row in rows}) == 23
    # the four the gate does not deliver are bought, marked, and carry the case they exist for
    injected = [row for row in rows if row["injected"]]
    assert len(injected) == 4
    assert {case for row in injected for case in row["cases"]} >= {"E1", "E4a", "E4b", "N3"}


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
        driver.subset,
        "population",
        lambda: [
            {
                "channel": "@x",
                "post_id": 1,
                "post_text": "",
                "comments": [],
                "injected": False,
                "cases": [],
                "silenced": 0,
                "text_less": 0,
            }
        ],
    )
    with pytest.raises(SystemExit, match="the registration pinned"):
        run(["--endpoint", "x", "--handshake"], FakeEndpoint())


def test_a_thread_whose_text_moved_is_refused_even_when_the_digest_holds(bench, monkeypatch):
    """The digest says WHICH threads and the per-thread sha says WHAT each of them is. A comment
    edited in the store since the registration leaves the digest alone — it hashes msg_ids — and
    would otherwise reach the model as a request nobody registered."""
    real = driver.subset.population()
    edited = [{**real[0], "post_text": real[0]["post_text"] + " (edited)"}, *real[1:]]
    monkeypatch.setattr(driver.subset, "population", lambda: edited)
    monkeypatch.setattr(
        driver.subset, "digest", lambda kept: RECORD["population"]["enumeration"]["digest"]
    )
    with pytest.raises(SystemExit, match="The thread's text moved since the registration"):
        run(["--endpoint", "x", "--handshake"], FakeEndpoint())


def test_the_ledger_is_anchored_before_the_first_request_and_never_regenerated(bench):
    endpoint = FakeEndpoint()
    run(["--endpoint", "x", "--handshake"], endpoint)
    first = json.loads(driver.LEDGER.read_text("utf-8"))
    assert first["runpod_balance_at_probe-b_start"] == 22.99
    assert first["probe-b_cap_usd"] == RECORD["money"]["cap_usd_all_in"] == 0.35
    run(["--endpoint", "x", "--handshake"], endpoint)
    again = json.loads(driver.LEDGER.read_text("utf-8"))
    assert again["anchored_at"] == first["anchored_at"], "the anchor must survive a second run"
