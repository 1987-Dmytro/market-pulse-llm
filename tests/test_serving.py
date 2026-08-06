"""The 5b endpoint client: the transport, the guard, and the projection the abort rule reads.

Nothing here touches the network — `_post` is replaced by a stub that returns the RunPod job
payloads the real endpoint returns. What is being checked is the part that decides a number:
that a mispaired batch is a refusal rather than a silent relabelling, that a worker serving
the wrong configuration cannot be scored, and that the projection is arithmetic anyone can
redo on paper.
"""

import pytest
from market_pulse import serving
from market_pulse.zero_shot import ApiError


def reply(content: str = '{"ok": true}', prompt: int = 11, completion: int = 7) -> dict:
    return {
        "content": content,
        "finish_reason": "stop",
        "cost": 0.0,
        "usage": {"prompt_tokens": prompt, "completion_tokens": completion},
        "generation_id": None,
    }


def job(output: dict, *, execution_ms: int = 3000, delay_ms: int = 250) -> dict:
    return {
        "id": "job-1",
        "status": "COMPLETED",
        "executionTime": execution_ms,
        "delayTime": delay_ms,
        "workerId": "worker-a",
        "output": output,
    }


class Transport:
    """One canned answer per call, and every request it was asked."""

    def __init__(self, *answers):
        self.answers, self.seen = list(answers), []

    def __call__(self, url, key, payload, timeout):
        self.seen.append((url, payload))
        answer = self.answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return answer


@pytest.fixture
def client(monkeypatch):
    def make(*answers, **kwargs):
        transport = Transport(*answers)
        monkeypatch.setattr(serving, "_post", transport)
        monkeypatch.setattr(serving, "POLL_SECONDS", 0)
        instance = serving.EndpointClient("ep-1", "key", **kwargs)
        instance.transport = transport
        return instance

    return make


# --- the transport ----------------------------------------------------------


def test_batch_returns_one_reply_per_text_in_order(client):
    endpoint = client(job({"replies": [reply("a"), reply("b")], "n": 2}))
    replies = endpoint.batch("T1", ["one", "two"])
    assert [r["content"] for r in replies] == ["a", "b"]
    assert endpoint.usage == {"prompt_tokens": 22, "completion_tokens": 14}
    timing = endpoint.timing()
    assert timing["calls"] == 1
    assert timing["worker_seconds"] == 3.0
    assert timing["queue_seconds"] == 0.25
    assert timing["worker_ids"] == ["worker-a"]


def test_batch_sends_the_task_texts_and_posts_unrendered(client):
    """The worker renders. A client that built the prompt would measure two stacks."""
    endpoint = client(job({"replies": [reply()]}))
    endpoint.batch("T2", ["row"], [{"post_text": "parent"}])
    _, payload = endpoint.transport.seen[0]
    assert payload == {
        "input": {
            "op": "batch",
            "task": "T2",
            "texts": ["row"],
            "posts": [{"post_text": "parent"}],
        }
    }


def test_batch_refuses_a_short_answer(client):
    """Two texts, one reply: every label after the gap belongs to the wrong row."""
    endpoint = client(job({"replies": [reply()], "n": 1}))
    with pytest.raises(ApiError, match="mispaired"):
        endpoint.batch("T1", ["one", "two"])


def test_batch_refuses_mismatched_posts(client):
    endpoint = client(job({"replies": []}))
    with pytest.raises(ValueError, match="1 parent posts for 2 rows"):
        endpoint.batch("T1", ["one", "two"], [{"post_text": "p"}])


def test_a_failed_job_is_an_error_not_an_empty_output(client):
    endpoint = client(job({"replies": []}) | {"status": "FAILED"})
    with pytest.raises(ApiError, match="ended FAILED"):
        endpoint.batch("T1", ["one"])


def test_an_in_progress_job_is_polled_to_completion(client):
    endpoint = client(
        {"id": "job-9", "status": "IN_PROGRESS"},
        job({"replies": [reply()]}) | {"id": "job-9"},
    )
    assert len(endpoint.batch("T1", ["one"])) == 1
    assert endpoint.transport.seen[1][0].endswith("/status/job-9")


def test_the_phase_gets_one_attempt_by_default(client):
    """SPEC amendment 3.11 (2): no retry. A client that re-asked would hide a failed run."""
    endpoint = client(ApiError(503, "cold"), job({"replies": [reply()]}))
    with pytest.raises(ApiError, match="503"):
        endpoint.batch("T1", ["one"])
    assert len(endpoint.transport.seen) == 1


def test_retries_are_available_but_opt_in(client, monkeypatch):
    monkeypatch.setattr(serving.time, "sleep", lambda _s: None)
    endpoint = client(ApiError(503, "cold"), job({"replies": [reply()]}), retries=1)
    assert len(endpoint.batch("T1", ["one"])) == 1


def test_a_non_retryable_status_is_never_retried(client, monkeypatch):
    monkeypatch.setattr(serving.time, "sleep", lambda _s: None)
    endpoint = client(ApiError(401, "bad key"), job({"replies": [reply()]}), retries=3)
    with pytest.raises(ApiError, match="401"):
        endpoint.batch("T1", ["one"])
    assert len(endpoint.transport.seen) == 1


# --- the guard --------------------------------------------------------------

SERVED = {
    "serving_config": "A",
    "merge_state": "unmerged-adapter",
    "adapter_sha256": "b3ca6308",
    "quantization": {"load_in_4bit": True},
}


def test_assert_serving_passes_the_configuration_through():
    assert serving.assert_serving(SERVED | {"extra": 1}, SERVED) == SERVED | {"extra": 1}


@pytest.mark.parametrize(
    "wrong",
    [
        {"adapter_sha256": "d8ef92a5"},  # the OTHER 4.5h2 arm — the realistic mix-up
        {"merge_state": "merged-requantized"},
        {"serving_config": "B"},
        {"quantization": {"load_in_4bit": True, "bnb_4bit_quant_type": "fp4"}},
    ],
)
def test_assert_serving_refuses_a_worker_that_is_not_the_registered_config(wrong):
    with pytest.raises(SystemExit, match="not serving the registered configuration"):
        serving.assert_serving(SERVED | wrong, SERVED)


def test_assert_serving_refuses_a_worker_that_cannot_say_what_it_loaded():
    """An absent field is a refusal: an endpoint that names nothing is not a configuration."""
    with pytest.raises(SystemExit, match="adapter_sha256: worker says '<absent>'"):
        serving.assert_serving({k: v for k, v in SERVED.items() if k != "adapter_sha256"}, SERVED)


# --- the projection ---------------------------------------------------------
#
#   per run   = 10 rows x 3.0 s + 100 s cold start          = 130 s
#   scored    = 130 s x 2 runs x $0.001/s                   = $0.26
#   total     = $0.26 + $0.50 merge                         = $0.76
def test_project_pair_usd_matches_the_hand_computed_fixture():
    projection = serving.project_pair_usd(
        seconds_per_row=3.0,
        rows=10,
        runs=2,
        usd_per_second=0.001,
        cold_start_seconds=100,
        merge_usd=0.5,
    )
    assert projection["seconds_per_run"] == 130.0
    assert projection["scored_usd"] == pytest.approx(0.26)
    assert projection["projected_usd"] == pytest.approx(0.76)


def test_project_pair_usd_reports_every_input_it_used():
    """A projection whose inputs are not in the record cannot be re-derived."""
    projection = serving.project_pair_usd(
        seconds_per_row=2.0, rows=5, runs=2, usd_per_second=0.002, cold_start_seconds=0
    )
    assert projection["inputs"] == {
        "seconds_per_row": 2.0,
        "rows": 5,
        "runs": 2,
        "usd_per_second": 0.002,
        "cold_start_seconds": 0,
        "merge_usd": 0.0,
        "spent_usd": 0.0,
    }
    assert projection["projected_usd"] == pytest.approx(0.04)


#   the cap is on the phase, not on the pair: $0.04 of pair on top of $3.98 already
#   spent is $4.02, and the pair alone would have read as clearing
def test_the_projection_carries_what_the_phase_already_spent():
    projection = serving.project_pair_usd(
        seconds_per_row=2.0,
        rows=5,
        runs=2,
        usd_per_second=0.002,
        cold_start_seconds=0,
        spent_usd=3.98,
    )
    assert projection["projected_usd"] == pytest.approx(0.04)
    assert projection["total_usd"] == pytest.approx(4.02)


def test_endpoint_url_is_the_runpod_v2_shape():
    assert serving.endpoint_url("ep-1", "runsync") == "https://api.runpod.ai/v2/ep-1/runsync"


def test_a_pod_serves_the_same_job_at_the_root(client):
    """SPEC amendment 3.11 (1): the worker moved to a pod and the client did not.

    RunPod's API keys the endpoint in the path; the SDK's own server on the pod serves
    `/runsync` at the root and has no endpoint to key by. `endpoint_id` stays the label
    the record carries — the pod id — and must not leak into the URL.
    """
    pod = client(job({"replies": [reply()], "n": 1}), base_url="http://127.0.0.1:8000/")
    assert pod.url("runsync") == "http://127.0.0.1:8000/runsync"
    pod.batch("T1", ["a"])
    assert pod.transport.seen[0][0] == "http://127.0.0.1:8000/runsync"


def test_a_pod_polls_status_with_a_body_because_that_route_is_post_only(client, monkeypatch):
    """The one shape difference between the two servers, and it must fail on the job.

    RunPod answers `/status` on GET; the SDK registers it POST-only, so a GET there is a
    405 that reads like a dead worker rather than like a job that is still running.
    """
    monkeypatch.setattr(serving.time, "sleep", lambda _s: None)
    pod = client(
        {"id": "j-1", "status": "IN_PROGRESS"},
        job({"replies": [reply()], "n": 1}),
        base_url="http://127.0.0.1:8000",
    )
    pod.batch("T1", ["a"])
    url, payload = pod.transport.seen[1]
    assert url == "http://127.0.0.1:8000/status/j-1"
    assert payload == {}  # a body, so `_post` sends POST
    assert (
        client({"id": "j-1", "status": "IN_PROGRESS"}, job({"replies": [reply()], "n": 1})).base_url
        is None
    )


# --- the unit the bill is in -------------------------------------------------


def test_timing_reports_wall_clock_beside_the_executed_seconds(client, monkeypatch):
    """A worker bills while it is up. Summed executionTime is not that number, and an
    8-row smoke's idle share is nothing like a 758-row run's — so both travel."""
    ticks = iter([100.0, 100.0, 130.0, 130.0])
    monkeypatch.setattr(serving.time, "monotonic", lambda: next(ticks))
    endpoint = client(job({"replies": [reply()]}, execution_ms=6000))
    endpoint.batch("T1", ["one"])
    timing = endpoint.timing()
    assert timing["wall_seconds"] == 30.0
    assert timing["worker_seconds"] == 6.0
    assert timing["idle_share"] == 0.8
    assert timing["wall_per_call"] == 30.0


def test_timing_is_empty_rather_than_wrong_before_the_first_call(client):
    endpoint = client()
    assert endpoint.timing()["wall_seconds"] is None
    assert endpoint.timing()["idle_share"] is None


def test_the_handshake_waits_longer_than_a_row(client):
    """A 31 B cold start outlives the per-row budget, and `retries=0` would abort on it."""
    endpoint = client(job({"serving_config": "A"}))
    endpoint.info()
    assert endpoint.transport.seen[0][0].endswith("/runsync")
    assert serving.HANDSHAKE_TIMEOUT > serving.DEFAULT_TIMEOUT * 5


# --- the stack, not just the weights -----------------------------------------

ANCHOR_STACK = {
    "torch": "2.8.0+cu128",
    "transformers": "5.14.1",
    "bitsandbytes": "0.50.0",
    "gpu": "NVIDIA RTX A6000",
}


def test_the_4_5h2_stack_passes_itself():
    assert serving.assert_runtime_matches(ANCHOR_STACK, ANCHOR_STACK) == ANCHOR_STACK


def test_a_different_card_is_the_measurement_not_a_refusal():
    """Which GPU the worker got IS the runtime delta 5b reports. Pinning it would
    refuse the measurement instead of making it."""
    other = ANCHOR_STACK | {"gpu": "NVIDIA GeForce RTX 4090"}
    assert serving.assert_runtime_matches(other, ANCHOR_STACK) == other


@pytest.mark.parametrize(
    "drift", [{"transformers": "5.15.0"}, {"torch": "2.9.0+cu128"}, {"bitsandbytes": "0.51.0"}]
)
def test_a_library_that_moved_is_a_different_instrument(drift):
    with pytest.raises(SystemExit, match="not the one 4.5h2 measured"):
        serving.assert_runtime_matches(ANCHOR_STACK | drift, ANCHOR_STACK)


def test_a_worker_that_does_not_report_a_library_is_refused():
    with pytest.raises(SystemExit, match="transformers: worker '<absent>'"):
        serving.assert_runtime_matches(
            {k: v for k, v in ANCHOR_STACK.items() if k != "transformers"}, ANCHOR_STACK
        )
