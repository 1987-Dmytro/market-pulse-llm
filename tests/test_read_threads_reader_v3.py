"""reader-v3's driver, driven end to end by a fake endpoint — every branch that decides money.

An import proves nothing about a driver ([[stub_driven_script_verification]]). What is exercised
here is the gate's REAL threshold from both sides, the reading of «billed» it takes and the audit it
leaves behind, the per-row evidence the sitting rule asks for (the rendered request and the repairs
that fired), and the refusal to open a run the gate said STOP to.

The threshold test is the one that matters. The registration carries `max_slowdown_vs_probe_b: 1.165`
and that number bounds the WHOLE pass; the predicate this gate stops on is stricter, because the
warm-up's own seconds are inside the total and the remainder is projected from them. Hand-computed
below: the warm-up may bill 69.592 s and no more, which is 1.117x probe-b's 62.276 s for the same
three threads. A test that only checked 1.165x would pass a run the cap cannot pay for.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import read_threads_reader_v3 as driver  # noqa: E402
import runpod_guard as guard  # noqa: E402
import write_reader_prereg_v2 as writer  # noqa: E402

from market_pulse import prompts  # noqa: E402

RECORD = json.loads((REPO_ROOT / "results" / "prereg_reader_probe_v3.json").read_text("utf-8"))
RATE = RECORD["money"]["arithmetic"]["rate_usd_per_second"]
SETUP = RECORD["money"]["arithmetic"]["setup_usd"]
CAP = RECORD["money"]["cap_usd_all_in"]

PROBE_B_WARM_UP_SECONDS = json.loads(
    (REPO_ROOT / "results" / "reader_probe_b_run.json").read_text("utf-8")
)["go_no_go"]["warm_up"]["billed_seconds"]

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

VERDICT_WITH_AN_EMPTY_OBJECT = VERDICT.replace('"noise": []', '"noise": {}')
"""probe-b's second shape — `{}` where the schema asks for a list. Repair 2 fires and says so."""


class FakeEndpoint:
    """A worker that answers what the registration expects, and bills what the test tells it to."""

    def __init__(
        self,
        *,
        seconds_per_thread: float = 2.0,
        reply: str = VERDICT,
        info=None,
        wall_bonus: float = 0.0,
    ):
        self.seconds_per_thread = seconds_per_thread
        self.reply = reply
        self.wall_bonus = wall_bonus
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
        assert task == prompts.READER_TASK_V3, "this contract reads with v3 and with nothing else"
        self.asked += [f"{one['channel']}:{one['post_id']}" for one in threads]
        self.worker_seconds += self.seconds_per_thread * len(threads)
        return [{"content": self.reply, "finish_reason": "stop", "usage": {}} for _ in threads]

    def timing(self) -> dict:
        return {
            "worker_seconds": self.worker_seconds,
            "wall_seconds": self.worker_seconds + self.wall_bonus,
        }


@pytest.fixture
def bench(tmp_path, monkeypatch):
    """The driver with its three files in a temp directory and no balance call to RunPod."""
    monkeypatch.setattr(driver, "EVIDENCE", tmp_path / "reader_v3_w1.jsonl")
    monkeypatch.setattr(driver, "LEDGER", tmp_path / "spend_reader_v3.json")
    monkeypatch.setattr(driver, "RECORD", tmp_path / "reader_v3_run.json")
    monkeypatch.setattr(guard, "balance", lambda: 22.50)
    return tmp_path


def run(argv, endpoint):
    return driver.main(argv, client_factory=lambda: endpoint)


def gate_of() -> dict:
    return json.loads(driver.RECORD.read_text("utf-8"))["go_no_go"]


def test_the_warm_up_buys_the_registered_draw_under_v3_and_nothing_else(bench):
    endpoint = FakeEndpoint(seconds_per_thread=2.0)
    assert run(["--endpoint", "x", "--warm-up"], endpoint) == 0
    drawn = list(RECORD["go_no_go"]["warm_up"]["threads"])
    assert sorted(endpoint.asked) == sorted(drawn)
    rows = [json.loads(line) for line in driver.EVIDENCE.read_text("utf-8").splitlines()]
    assert sorted(row["thread"] for row in rows) == sorted(drawn)
    assert all(row["task"] == prompts.READER_TASK_V3 for row in rows)
    assert all(
        row["prompt_sha256"] == RECORD["instruments"]["prompt_sha256"][prompts.READER_TASK_V3]
        for row in rows
    )
    # a second warm-up buys nothing, and the gate it recomputes reads its seconds from those rows
    again = FakeEndpoint(seconds_per_thread=2.0)
    assert run(["--endpoint", "x", "--warm-up"], again) == 0
    assert again.asked == []
    assert gate_of()["warm_up"]["billed_seconds"] == 6.0


def test_every_row_carries_the_rendered_request_and_the_repairs_that_fired(bench):
    """The contract's step 6: the request AND its sha, and the parse outcome with its repairs.

    The sha proves the request is the registered one; only the text itself lets a reader see what
    the model was shown when a verdict is argued about later. And `repairs` is the measurement half
    A of the instrument was bought for — a verdict that does not carry it cannot be told apart from
    one that parsed straight.
    """
    endpoint = FakeEndpoint(seconds_per_thread=1.0, reply=VERDICT_WITH_AN_EMPTY_OBJECT)
    assert run(["--endpoint", "x", "--warm-up"], endpoint) == 0
    rows = [json.loads(line) for line in driver.EVIDENCE.read_text("utf-8").splitlines()]
    population = {driver.probe_b.key_of(one): one for one in driver.probe_b.subset.population()}
    for row in rows:
        thread = population[row["thread"]]
        assert row["request"] == writer.rendering(thread, prompts.READER_TASK_V3)
        assert row["rendering_sha256"] == writer.rendering_sha256(thread, prompts.READER_TASK_V3)
        assert row["repairs"] == ["noise: empty object -> empty list"]
        assert row["parsed"]["repairs"] == row["repairs"]
        assert row["finish_reason"] == "stop"

    # and a refusal carries its reason and NO repairs, which is the distinction the census turns on
    driver.EVIDENCE.unlink()
    refused = FakeEndpoint(seconds_per_thread=1.0, reply="not json at all")
    assert run(["--endpoint", "x", "--warm-up"], refused) in (0, 2)
    rows = [json.loads(line) for line in driver.EVIDENCE.read_text("utf-8").splitlines()]
    assert {row["parse_error"] for row in rows} == {"no JSON object in reply"}
    assert all(row["parsed"] is None and row["repairs"] is None for row in rows)


def test_the_gate_projects_the_remainder_and_the_pessimistic_projection_binds(bench):
    """Hand-computed. The draw is 3 threads carrying 11 payable comments; at 20 s a thread the
    warm-up bills 60 s. The REMAINDER is 20 threads and 123 payable comments, so per thread 20 s →
    400 s, and per payable comment 60/11 s → 670.909 s. The larger binds: 670.909 × $0.00030669 =
    $0.2058, plus the warm-up's own $0.0184 and the registered setup $0.0900 → $0.3142 of $0.35. GO.
    """
    endpoint = FakeEndpoint(seconds_per_thread=20.0)
    assert run(["--endpoint", "x", "--warm-up"], endpoint) == 0
    gate = gate_of()

    assert gate["warm_up"]["threads"] == 3
    assert gate["warm_up"]["payable_comments"] == 11
    assert gate["warm_up"]["billed_seconds"] == 60.0
    assert gate["remainder"] == {"threads": 20, "payable_comments": 123}
    assert gate["projections"]["by_thread"]["seconds"] == 400.0
    assert gate["projections"]["by_payable_comment"]["seconds"] == pytest.approx(670.9, abs=0.1)
    assert gate["projections"]["binding"]["which"] == "by_payable_comment"

    money = gate["money"]
    assert money["setup_usd"] == SETUP == 0.09
    assert money["warm_up_usd"] == pytest.approx(60.0 * RATE, abs=0.0005)
    assert money["projected_total_usd"] == pytest.approx(
        SETUP + (60.0 + 670.909) * RATE, abs=0.0005
    )
    assert gate["verdict"] == "GO"

    # the paired comparison the registration asked this warm-up to make, against probe-b's own draw
    paired = gate["warm_up"]["probe_b_on_the_same_draw"]
    assert paired["billed_seconds"] == PROBE_B_WARM_UP_SECONDS == 62.276
    assert gate["warm_up"]["slowdown_vs_probe_bs_warm_up"] == pytest.approx(
        60.0 / 62.276, abs=0.001
    )


def test_the_stop_threshold_is_69_592_seconds_and_not_the_registered_1_165x(bench):
    """The gate's real predicate, from both sides, one thousandth of a second apart.

    (cap − setup) ÷ (rate × (1 + 11.1818)) = 69.5924 billed seconds. At 23.197 s a thread the
    warm-up bills 69.591 and the total is $0.34999 — GO. At 23.198 it bills 69.594 and the total is
    $0.35001 — STOP. And the ratio that room is worth against probe-b's same-draw 62.276 s is
    **1.117**, not the registration's 1.165: that number is the bound on the WHOLE pass and a gate
    checked against it would open a run $0.02 over the cap.
    """
    tight = FakeEndpoint(seconds_per_thread=23.197)
    assert run(["--endpoint", "x", "--warm-up"], tight) == 0
    gate = gate_of()
    assert gate["verdict"] == "GO"

    stop = gate["stop_threshold"]
    # the verdict re-derives from the SECONDS and not from the dollars: both sides of this boundary
    # publish `projected_total_usd: 0.35`, because $0.3500064 rounds to four decimals like $0.3499948
    assert gate["money"]["projected_total_usd"] == CAP, "the rounded dollars cannot tell them apart"
    assert gate["warm_up"]["billed_seconds"] <= stop["warm_up_billed_seconds_that_still_fit"], (
        "and the seconds can — this is the pair a reader checks the verdict against"
    )
    assert stop["warm_up_billed_seconds_that_still_fit"] == pytest.approx(69.592, abs=0.01)
    assert stop["binding_factor"] == pytest.approx(123 / 11, abs=0.0001)
    assert stop["as_a_ratio_to_probe_bs_warm_up"] == pytest.approx(1.117, abs=0.001)
    assert stop["registered_max_slowdown_vs_probe_b"] == 1.165
    assert stop["as_a_ratio_to_probe_bs_warm_up"] < stop["registered_max_slowdown_vs_probe_b"], (
        "the two numbers are different and the stricter one is what this gate stops on"
    )

    driver.EVIDENCE.unlink()
    over = FakeEndpoint(seconds_per_thread=23.198)
    assert run(["--endpoint", "x", "--warm-up"], over) == 2
    stopped = gate_of()
    assert stopped["verdict"] == "STOP"
    assert stopped["money"]["projected_total_usd"] == CAP, "the same rounded figure, the other side"
    assert (
        stopped["warm_up"]["billed_seconds"]
        > stopped["stop_threshold"]["warm_up_billed_seconds_that_still_fit"]
    )


def test_a_projection_over_the_cap_stops_the_run_and_the_run_refuses_to_open(bench):
    """25 s a thread: 75 s billed, the remainder 123 payable × 75/11 = 838.6 s → $0.2572, plus
    $0.0230 of warm-up and $0.0900 of setup is $0.3702, over the $0.35 cap. The exit code says STOP
    and `--run` refuses to open on it — the one attempt stays intact."""
    endpoint = FakeEndpoint(seconds_per_thread=25.0)
    assert run(["--endpoint", "x", "--warm-up"], endpoint) == 2
    gate = gate_of()
    assert gate["projections"]["binding"]["seconds"] == pytest.approx(838.6, abs=0.2)
    assert gate["money"]["projected_total_usd"] == pytest.approx(0.3702, abs=0.0005)
    assert gate["verdict"] == "STOP"
    with pytest.raises(SystemExit, match="the go/no-go verdict is STOP"):
        run(["--endpoint", "x", "--run"], FakeEndpoint())


def test_the_billed_reading_is_the_pessimistic_one_and_says_which_leg_it_took(bench):
    """`wall_seconds` starts at this process's first request, which is the handshake — so a cold
    endpoint puts its boot inside the window and the gate would STOP on a run that fits. The
    pessimistic maximum is kept, because it is probe-b's rule and the pairing rests on it; what the
    record must carry is all three legs and the gap, so the cause is visible in the artefact rather
    than arriving as an unexplained verdict."""
    endpoint = FakeEndpoint(seconds_per_thread=2.0, wall_bonus=180.0)
    assert run(["--endpoint", "x", "--warm-up"], endpoint) == 2
    billed = gate_of()["warm_up"]["billed_readings"]
    assert billed["persisted_worker_seconds"] == 6.0
    assert billed["live_worker_seconds"] == 6.0
    assert billed["live_wall_seconds"] == 186.0
    assert billed["taken"] == 186.0 and billed["which"] == "live_wall_seconds"
    assert billed["wall_ahead_of_the_jobs_by"] == 180.0 > driver.BOOT_IN_THE_WINDOW_S

    # and with no gap the three legs agree and the reading is unremarkable
    driver.EVIDENCE.unlink()
    warm = FakeEndpoint(seconds_per_thread=2.0)
    assert run(["--endpoint", "x", "--warm-up"], warm) == 0
    assert gate_of()["warm_up"]["billed_readings"]["wall_ahead_of_the_jobs_by"] == 0.0


def test_after_a_go_the_run_reads_the_rest_of_the_paired_population(bench):
    endpoint = FakeEndpoint(seconds_per_thread=2.0)
    assert run(["--endpoint", "x", "--warm-up"], endpoint) == 0
    rest = FakeEndpoint(seconds_per_thread=2.0)
    assert run(["--endpoint", "x", "--run"], rest) == 0

    drawn = set(RECORD["go_no_go"]["warm_up"]["threads"])
    assert len(rest.asked) == RECORD["population"]["threads"] - len(drawn)
    assert not drawn & set(rest.asked)
    rows = [json.loads(line) for line in driver.EVIDENCE.read_text("utf-8").splitlines()]
    assert len(rows) == len({row["thread"] for row in rows}) == 23
    # probe-b's four injected threads are bought again and still marked: the flag is probe-b's and
    # the digest carries it, while the reader census cell now holds all 23 (Dv427)
    assert sum(1 for row in rows if row["injected"]) == 4
    assert all(
        one["in_the_reader_census_cell"] for one in RECORD["population"]["enumeration"]["threads"]
    )


def test_the_registration_must_be_committed_and_unmodified(bench, monkeypatch):
    """The registration is FROZEN by its own clause, so the driver's message says restore rather
    than commit: a plan edited once the numbers are in is a plan the run wrote."""
    monkeypatch.setattr(driver, "PREREG", REPO_ROOT / "results" / "no_such_prereg.json")
    with pytest.raises(SystemExit, match="is not tracked by git"):
        run(["--endpoint", "x", "--handshake"], FakeEndpoint())


def test_a_thread_whose_text_moved_is_refused_even_when_the_digest_holds(bench, monkeypatch):
    """Imported from probe-b's driver and re-exercised under v3's task: the digest says WHICH
    threads and the per-thread sha says WHAT each of them is, and the second is what a comment
    edited in the store since the registration moves."""
    real = driver.probe_b.subset.population()
    edited = [{**real[0], "post_text": real[0]["post_text"] + " (edited)"}, *real[1:]]
    monkeypatch.setattr(driver.probe_b.subset, "population", lambda: edited)
    monkeypatch.setattr(
        driver.probe_b.subset,
        "digest",
        lambda kept: RECORD["population"]["enumeration"]["digest"],
    )
    with pytest.raises(SystemExit, match="The thread's text moved since the registration"):
        run(["--endpoint", "x", "--handshake"], FakeEndpoint())


def test_the_cap_lands_in_a_ledger_the_guard_anchored_first(bench):
    """The runbook's real order: `runpod_guard --step reader-v3 --step-cap 0.35` writes this file
    before the staging pod, so when the driver runs the anchor branch never fires. The anchor is
    never overwritten and the guard's own keys survive beside the driver's."""
    guard_written = {
        guard.step_anchor_key("reader-v3"): 22.50,
        "reader-v3_gpu_cap_usd": 0.35,
        "anchored_at": "2026-08-16T17:00:00+00:00",
        "gpu_note": "written by scripts/runpod_guard.py before the first pod",
        "gpu_sessions": [],
    }
    driver.LEDGER.write_text(json.dumps(guard_written), encoding="utf-8")

    run(["--endpoint", "x", "--handshake"], FakeEndpoint())
    after = json.loads(driver.LEDGER.read_text("utf-8"))
    assert after["reader-v3_cap_usd"] == CAP == 0.35
    assert after[guard.step_anchor_key("reader-v3")] == 22.50, "the anchor is never overwritten"
    assert after["anchored_at"] == guard_written["anchored_at"]
    assert after["gpu_sessions"] == [] and after["gpu_note"] == guard_written["gpu_note"]
