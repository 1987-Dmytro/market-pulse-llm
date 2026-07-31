"""The parts of the OpenRouter harness that decide a number or a dollar.

No network: the client is a callable and every test hands it a fake one. What is
pinned here is the routing block (a silent reroute would swap the model under the
number), the budget arithmetic (the cap is arithmetic, not discipline), the retry
policy, and the one invariant a reference row must not be able to break.
"""

import pytest

from market_pulse import zero_shot


def test_routing_pins_one_endpoint_with_fallbacks_off():
    assert zero_shot.routing("venice/fp8", "fp8") == {
        "order": ["venice/fp8"],
        "allow_fallbacks": False,
        "quantizations": ["fp8"],
    }


def test_routing_omits_quantization_only_when_there_is_none_to_pin():
    """The Anthropic reference row reports no quantization; candidates always do."""
    block = zero_shot.routing("anthropic", None)
    assert block == {"order": ["anthropic"], "allow_fallbacks": False}
    assert "quantizations" not in block


def test_request_body_is_identical_but_for_model_and_messages():
    common = dict(tag="venice/fp8", quantization="fp8", max_tokens=256)
    a = zero_shot.request_body(model="m1", messages=[{"role": "user", "content": "a"}], **common)
    b = zero_shot.request_body(model="m2", messages=[{"role": "user", "content": "b"}], **common)
    assert {k: v for k, v in a.items() if k not in ("model", "messages")} == {
        k: v for k, v in b.items() if k not in ("model", "messages")
    }
    assert a["temperature"] == 0.0
    assert a["seed"] == 42
    assert a["reasoning"] == {"enabled": False}, "hybrid-reasoning models must not think"
    assert a["usage"] == {"include": True}, "the budget guard reads cost off the response"
    assert a["provider"]["allow_fallbacks"] is False


def test_request_body_drops_the_seed_where_an_endpoint_refuses_it():
    body = zero_shot.request_body(
        model="m", messages=[], tag="t", quantization="fp8", max_tokens=8, seed=None
    )
    assert "seed" not in body


class TestBudget:
    def test_run_cap_trips_before_the_phase_cap(self):
        budget = zero_shot.Budget(total_cap=8.0, run_cap=0.10)
        budget.add(0.09)
        with pytest.raises(zero_shot.BudgetExceeded, match="per-run cap"):
            budget.add(0.02)

    def test_phase_cap_counts_what_earlier_runs_spent(self):
        budget = zero_shot.Budget(total_cap=8.0, run_cap=5.0, spent_before=7.95)
        with pytest.raises(zero_shot.BudgetExceeded, match=r"3b cap"):
            budget.add(0.06)

    def test_reconcile_only_ever_raises_the_number(self):
        """A row whose response was lost still cost money; the local sum under-counts
        exactly the rows it failed to record, so the provider's number wins upwards."""
        budget = zero_shot.Budget(total_cap=8.0, run_cap=5.0, spent_before=1.0)
        budget.add(0.20)
        budget.reconcile(1.50)  # provider says 0.50 spent this run
        assert budget.run_spend == pytest.approx(0.50)
        budget.reconcile(1.10)  # a stale, smaller reading must not give money back
        assert budget.run_spend == pytest.approx(0.50)

    def test_reconcile_can_trip_the_cap_on_its_own(self):
        budget = zero_shot.Budget(total_cap=8.0, run_cap=1.0, spent_before=0.0)
        with pytest.raises(zero_shot.BudgetExceeded):
            budget.reconcile(1.01)

    def test_headroom_is_the_tighter_of_the_two_caps(self):
        budget = zero_shot.Budget(total_cap=8.0, run_cap=1.5, spent_before=7.0)
        assert budget.headroom() == pytest.approx(1.0)


class TestRetry:
    def test_retries_a_transient_status_then_succeeds(self):
        calls, slept = [], []
        statuses = [429, 503]

        def caller():
            calls.append(1)
            if statuses:
                raise zero_shot.ApiError(statuses.pop(0), "busy")
            return "ok"

        assert zero_shot.call_with_retry(caller, sleeper=slept.append) == "ok"
        assert len(calls) == 3
        assert slept == [1.5, 3.0], "exponential backoff, not a tight loop"

    def test_does_not_retry_a_permanent_status(self):
        calls = []

        def caller():
            calls.append(1)
            raise zero_shot.ApiError(400, "bad request")

        with pytest.raises(zero_shot.ApiError):
            zero_shot.call_with_retry(caller, sleeper=lambda _: None)
        assert len(calls) == 1, "a 400 will not fix itself"

    def test_gives_up_after_the_last_attempt(self):
        calls = []

        def caller():
            calls.append(1)
            raise zero_shot.ApiError(503, "down")

        with pytest.raises(zero_shot.ApiError):
            zero_shot.call_with_retry(caller, attempts=3, sleeper=lambda _: None)
        assert len(calls) == 3

    def test_retries_a_dropped_connection(self):
        calls = []

        def caller():
            calls.append(1)
            if len(calls) < 2:
                raise ConnectionResetError("peer went away")
            return "ok"

        assert zero_shot.call_with_retry(caller, sleeper=lambda _: None) == "ok"


def test_estimate_cost_scales_with_rows_and_price():
    pricing = {"prompt": "0.0000001", "completion": "0.00000015"}
    one = zero_shot.estimate_cost(
        rows=["текст"], prompt_chars=1738, pricing=pricing, completion_tokens=60
    )
    ten = zero_shot.estimate_cost(
        rows=["текст"] * 10, prompt_chars=1738, pricing=pricing, completion_tokens=60
    )
    assert ten["requests"] == 10
    assert ten["usd"] == pytest.approx(one["usd"] * 10)
    assert one["usd"] > 0


RECORD = dict(
    timestamp="2026-07-31T00:00:00+00:00",
    git={"commit": "0" * 40, "dirty": []},
    config={"seed": 42},
    diagnostics={"note": "diagnostics, not gates."},
)


def test_build_record_keeps_a_candidate_row_gated():
    record = zero_shot.build_record(
        model="qwen/qwen3.5-9b",
        gates=[{"gate": "G1d", "metric": "post_type macro-F1", "value": 0.5, "n": {}}],
        reference_only=False,
        **RECORD,
    )
    assert record["reference_only"] is False
    assert record["gates"][0]["gate"] == "G1d"


def test_build_record_makes_a_reference_row_unfindable_as_a_gate():
    """[[frontier-api-reference-baseline]]: the reference row never anchors a gate.
    The cheapest guarantee is a record that cannot claim one, whatever reads it."""
    record = zero_shot.build_record(
        model="anthropic/claude-haiku-4.5:batch",
        gates=[
            {"gate": "G1d", "metric": "post_type macro-F1", "value": 0.9, "n": {}},
            {"gate": "G1e", "metric": "brand extraction F1", "value": 0.4, "n": {}},
        ],
        reference_only=True,
        **RECORD,
    )
    assert record["reference_only"] is True
    assert {entry["gate"] for entry in record["gates"]} == {"ref"}
    assert [entry["reference_metric"] for entry in record["gates"]] == ["G1d", "G1e"]
    assert [entry["metric"] for entry in record["gates"]] == [
        "post_type macro-F1",
        "brand extraction F1",
    ], "the metric names survive so the row still reads next to the others"
    assert record["diagnostics"]["note"].startswith("REFERENCE ONLY")


def test_build_record_carries_the_fields_show_results_reads():
    record = zero_shot.build_record(model="m", gates=[], reference_only=False, **RECORD)
    for field in ("model", "timestamp", "git", "config", "gates", "diagnostics"):
        assert field in record
    assert "note" in record["diagnostics"]
