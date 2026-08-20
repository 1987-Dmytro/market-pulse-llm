"""lora-b's Mac-side clock, DRIVEN — every rung, both verdicts, at $0 and with no pod.

The gates are the only thing between a registration and a bill, so they are exercised the way the
session will use them: one fabricated pod at a time, with `now` injected, and the state file the
run appends to redirected into `tmp_path`. What is asserted is not that the code runs — it is the
arithmetic each rung acts on, and in particular the two properties a second pod can break:

* the cumulative clock — a replacement pod's `--terminate-after` is its own create plus what the
  hard stop has LEFT, never a fresh window ([[a_budget_is_not_an_elapsed]]);
* the projection gate — a compliant-slow run that never trips the watchdog is KILLED by it, and the
  same run measured by the contract's letter alone is not.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import gate_lora_b as gate  # noqa: E402
import moved_pins  # noqa: E402
import pass1_pod_runner as podrunner  # noqa: E402
import reader_v5_pod_runner as shipped  # noqa: E402

from market_pulse import prompts  # noqa: E402

RECORD = json.loads((REPO_ROOT / "results" / "prereg_lora_b.json").read_text("utf-8"))
SMOKE = json.loads((REPO_ROOT / "results" / "lora_b_smoke_pack.json").read_text("utf-8"))
CREATE = "2026-08-21T09:00:00+00:00"


def at(seconds: float, created: str = CREATE) -> datetime:
    return gate.stamp(created) + timedelta(seconds=seconds)


@pytest.fixture
def run(tmp_path, monkeypatch):
    """The state file redirected, and the registration read from the committed one."""
    monkeypatch.setattr(gate, "RECORD", tmp_path / "lora_b_run.json")
    monkeypatch.setattr(gate, "registration", lambda: RECORD)
    return gate


def backstop_for(run, created: str) -> str:
    """The stamp a correct operator would hand `pod create`, computed the way the runbook says."""
    state = json.loads(run.RECORD.read_text("utf-8")) if run.RECORD.exists() else {}
    left = (
        RECORD["money"]["arithmetic"]["cumulative"]["hard_stop_seconds"]
        - gate.billed_before(state)[0]
    )
    return (gate.stamp(created) + timedelta(seconds=left)).isoformat(timespec="seconds")


def opened(run, *, usd_per_hour=0.74, created=CREATE, pod_id="pod-1", terminate_after=None):
    code = run.main(
        [
            "--open",
            "--pod-id",
            pod_id,
            "--created-at",
            created,
            "--usd-per-hour",
            str(usd_per_hour),
            "--card",
            "NVIDIA RTX A6000",
            "--terminate-after",
            terminate_after or backstop_for(run, created),
        ],
        now=at(0, created),
    )
    return code, json.loads(run.RECORD.read_text("utf-8"))


def losses(path: Path, seconds_per_step: float, steps: list[int]) -> Path:
    path.write_text(
        "".join(
            json.dumps({"step": step, "loss": 1.0, "seconds_per_step": seconds_per_step}) + "\n"
            for step in steps
        ),
        encoding="utf-8",
    )
    return path


# --- rung 1, the price ------------------------------------------------------


def test_a_price_over_the_ceiling_is_a_kill_and_the_pod_is_still_recorded(run):
    code, state = opened(run, usd_per_hour=0.95)
    assert code == gate.KILL
    assert state["gates"][-1]["verdict"] == "KILL"
    # recorded anyway: a pod that exists against no counter is a pod nothing is measuring
    assert state["pods"][-1]["pod_id"] == "pod-1"


def test_a_price_under_the_ceiling_is_a_go(run):
    code, state = opened(run)
    assert code == gate.GO
    assert state["gates"][-1]["rung"] == 1


# --- rung 2, the ssh dead-man ----------------------------------------------


@pytest.mark.parametrize(
    ("elapsed", "ssh_ok", "want"),
    [(60, False, "WAIT"), (179, False, "WAIT"), (181, False, "KILL"), (300, True, "GO")],
)
def test_gate_zero_waits_then_kills_and_an_answer_is_a_go(run, elapsed, ssh_ok, want):
    opened(run)
    state = json.loads(run.RECORD.read_text("utf-8"))
    verdict = run.gate_zero(RECORD, state, elapsed, ssh_ok, at(elapsed))
    assert verdict["verdict"] == want
    assert verdict["threshold_seconds"] == 180


# --- rung 3, the boot -------------------------------------------------------


def test_the_boot_gate_waits_kills_and_passes_on_the_registered_450(run):
    opened(run)
    state = json.loads(run.RECORD.read_text("utf-8"))
    assert run.gate_boot(RECORD, state, 300, None, at(300))["verdict"] == "WAIT"
    assert run.gate_boot(RECORD, state, 451, None, at(451))["verdict"] == "KILL"
    started = at(430).isoformat()
    passed = run.gate_boot(RECORD, state, 440, started, at(440))
    assert passed["verdict"] == "GO"
    assert passed["training_started_at_create_elapsed_seconds"] == 430
    assert passed["threshold_seconds"] == 450


# --- rung 4, the watchdog ---------------------------------------------------


def test_the_watchdog_needs_five_consecutive_lines_over_the_threshold(run, tmp_path):
    rows = [{"step": s, "seconds_per_step": 130.0} for s in (5, 10, 15, 20)]
    assert run.watchdog(RECORD, rows)["verdict"] == "GO"
    rows.append({"step": 25, "seconds_per_step": 130.0})
    assert run.watchdog(RECORD, rows)["verdict"] == "KILL"
    rows[-2]["seconds_per_step"] = 60.0  # one fast line inside the window and it is not consecutive
    assert run.watchdog(RECORD, rows)["verdict"] == "GO"
    assert run.watchdog(RECORD, rows)["threshold_seconds_per_step"] == 122


# --- rung 8, the projection gate --------------------------------------------


def test_the_measured_rate_projects_the_registered_worst_case_and_goes(run, tmp_path):
    opened(run, usd_per_hour=0.80)
    state = json.loads(run.RECORD.read_text("utf-8"))
    rows = [{"step": 5, "seconds_per_step": 61.047}]
    verdict = run.projection(RECORD, state, "a", rows, at(450 + 5 * 61.047))
    assert verdict["verdict"] == "GO"
    worst = RECORD["money"]["arithmetic"]["worst_case_usd"]
    assert verdict["projected_usd"] == pytest.approx(worst, abs=0.01)


def test_the_compliant_slow_run_is_killed_by_the_projection_and_not_by_the_watchdog(run):
    """121 s/step: under the 122 s watchdog, and this is the rung that closes it."""
    opened(run, usd_per_hour=0.80)
    state = json.loads(run.RECORD.read_text("utf-8"))
    rows = [{"step": step, "seconds_per_step": 121.0} for step in (5, 10, 15, 20, 25)]
    assert run.watchdog(RECORD, rows)["verdict"] == "GO"
    verdict = run.projection(RECORD, state, "a", rows, at(450 + 25 * 121.0))
    assert verdict["verdict"] == "KILL"
    assert verdict["over_the_hard_stop"] is True
    # and the registration's own worked example says the same at step 5
    example = RECORD["money"]["arithmetic"]["cumulative"]["projection_gate"]["worked_examples"]
    assert example["compliant_slow"]["verdict"] == "KILL"
    assert example["compliant_slow_by_the_contracts_letter"]["verdict"] == "GO"


def test_arm_b_is_priced_at_the_rate_the_pod_is_running_not_at_its_fitted_seconds(run):
    """The first of the two tightenings, isolated: the leg moves with the measured rate."""
    opened(run, usd_per_hour=0.80)
    state = json.loads(run.RECORD.read_text("utf-8"))
    fitted = RECORD["money"]["arithmetic"]["train_seconds"]["b"]
    slow = run.projection(
        RECORD, state, "a", [{"step": 5, "seconds_per_step": 121.0}], at(450 + 5 * 121)
    )
    assert slow["arm_b_leg_seconds"] > fitted
    assert slow["arm_b_leg_seconds"] == pytest.approx(82 * 121.0)
    fast = run.projection(
        RECORD, state, "a", [{"step": 5, "seconds_per_step": 61.047}], at(450 + 5 * 61)
    )
    assert fast["arm_b_leg_seconds"] == pytest.approx(fitted)
    # arm B's own training owes no arm-B leg
    during_b = run.projection(
        RECORD, state, "b", [{"step": 5, "seconds_per_step": 61.047}], at(450 + 5 * 61)
    )
    assert during_b["arm_b_leg_seconds"] == 0.0


def test_the_remaining_steps_are_priced_at_the_worse_of_the_mean_and_the_last(run):
    rows = [{"step": 5, "seconds_per_step": 60.0}, {"step": 10, "seconds_per_step": 200.0}]
    assert run.measured_step(rows) == 200.0
    rows.append({"step": 15, "seconds_per_step": 60.0})
    assert run.measured_step(rows) == pytest.approx(320 / 3)  # the mean, once the last line drops


# --- rung 5, the arm-A milestone --------------------------------------------


def test_the_milestone_stops_arm_b_on_the_reading_and_not_on_a_projection(run):
    opened(run)
    state = json.loads(run.RECORD.read_text("utf-8"))
    assert run.milestone(RECORD, state, 2.50, at(0))["verdict"] == "GO"
    stopped = run.milestone(RECORD, state, 2.51, at(0))
    assert stopped["verdict"] == "STOP"
    assert stopped["threshold_usd"] == 2.50
    assert "arm B does NOT start" in stopped["next_step"]


# --- rung 7, the CUMULATIVE clock -------------------------------------------


def test_a_second_pods_backstop_is_the_hard_stop_LESS_what_the_first_one_billed(run):
    """The defect rung 7 exists for: two pods each given a fresh window bill twice the stop."""
    stop = RECORD["money"]["arithmetic"]["cumulative"]["hard_stop_seconds"]
    opened(run)
    first = json.loads(run.RECORD.read_text("utf-8"))
    assert gate.stamp(first["pods"][0]["terminate_after_computed"]) == gate.stamp(
        CREATE
    ) + timedelta(seconds=stop)

    run.main(
        ["--close-pod", "--deleted-at", at(3600).isoformat(), "--outcome", "gate 3 KILL"],
        now=at(3600),
    )
    second_create = at(4000).isoformat()
    opened(run, pod_id="pod-2", created=second_create)
    state = json.loads(run.RECORD.read_text("utf-8"))
    assert state["pods"][0]["billed_seconds"] == 3600.0
    window = gate.stamp(state["pods"][1]["terminate_after_computed"]) - gate.stamp(second_create)
    assert window.total_seconds() == stop - 3600
    # the whole point, stated as the sum: two windows can never exceed the stop
    assert 3600 + window.total_seconds() == stop


def test_a_backstop_longer_than_the_cumulative_stop_allows_is_REFUSED(run):
    """Rung 7 is enforced by a platform flag this instrument cannot read back, so the caller has to
    SAY the stamp and a fresh 5.5 h window on a second pod is a refusal, not a silent recompute."""
    stop = RECORD["money"]["arithmetic"]["cumulative"]["hard_stop_seconds"]
    opened(run)
    run.main(
        ["--close-pod", "--deleted-at", at(3600).isoformat(), "--outcome", "gate 3 KILL"],
        now=at(3600),
    )
    second_create = at(4000).isoformat()
    fresh_window = (gate.stamp(second_create) + timedelta(seconds=stop)).isoformat(
        timespec="seconds"
    )
    with pytest.raises(SystemExit, match="beyond the"):
        opened(run, pod_id="pod-2", created=second_create, terminate_after=fresh_window)

    # rounding the window DOWN is always safe and is accepted
    shorter = (gate.stamp(second_create) + timedelta(seconds=stop - 3600 - 600)).isoformat(
        timespec="seconds"
    )
    code, state = opened(run, pod_id="pod-2", created=second_create, terminate_after=shorter)
    assert code == gate.GO
    assert state["pods"][1]["terminate_after"] == shorter
    assert state["gates"][-1]["backstop"]["overshoot_seconds"] == -600.0


def test_a_pod_cannot_be_opened_once_the_hard_stop_has_been_billed_away(run):
    stop = RECORD["money"]["arithmetic"]["cumulative"]["hard_stop_seconds"]
    opened(run)
    run.main(
        ["--close-pod", "--deleted-at", at(stop).isoformat(), "--outcome", "the whole window"],
        now=at(stop),
    )
    with pytest.raises(SystemExit, match="no window left"):
        opened(run, pod_id="pod-2", created=at(stop + 60).isoformat())
    assert run.main(["--pre-create-check"]) == gate.KILL


def test_the_clock_counts_a_closed_pods_dollars_at_that_pods_own_price(run):
    opened(run, usd_per_hour=0.74)
    run.main(
        ["--close-pod", "--deleted-at", at(1800).isoformat(), "--outcome", "closed"], now=at(1800)
    )
    state = json.loads(run.RECORD.read_text("utf-8"))
    assert state["pods"][0]["billed_usd"] == pytest.approx(1800 * 0.74 / 3600)
    reading = run.clock(RECORD, state, at(9999))
    assert reading["pod_is_live"] is False
    assert reading["cumulative_billed_seconds"] == 1800.0
    assert reading["elapsed_on_this_pod_seconds"] == 0.0  # a closed pod bills nothing further


def test_never_two_billing_endpoints(run, capsys):
    opened(run)
    assert run.main(["--pre-create-check"]) == gate.KILL
    assert "Never two billing endpoints" in capsys.readouterr().out
    run.main(
        ["--close-pod", "--deleted-at", at(600).isoformat(), "--outcome", "closed"], now=at(600)
    )
    assert run.main(["--pre-create-check"]) == gate.GO


def test_a_second_open_over_a_live_pod_is_refused(run):
    opened(run)
    with pytest.raises(SystemExit, match="still open"):
        opened(run, pod_id="pod-2", created="2026-08-21T10:00:00+00:00")


# --- rung 9, the re-creation budget check -----------------------------------


def test_the_recreation_is_refused_when_the_reading_plus_the_remaining_passes_the_cap(run):
    opened(run, usd_per_hour=0.80)
    run.main(
        ["--close-pod", "--deleted-at", at(3600).isoformat(), "--outcome", "arm B lost"],
        now=at(3600),
    )
    state = json.loads(run.RECORD.read_text("utf-8"))
    cheap = run.recreate_check(RECORD, state, 1.00, ["b"])
    assert cheap["verdict"] == "GO"
    assert cheap["reading_plus_remaining_usd"] <= RECORD["money"]["cap_usd_all_in"]
    dear = run.recreate_check(RECORD, state, 5.00, ["b"])
    assert dear["verdict"] == "STOP"
    assert "closes with what exists" in dear["next_step"]


def test_the_recreation_prices_the_remaining_at_the_MEASURED_rate(run, tmp_path):
    """A slow pod makes its own replacement dearer, and the CUMULATIVE seconds are what refuse it.

    At 110 s/step a full restart of both arms prices at 18 970.7 s — inside the cap on its own, and
    over the hard stop the moment a first pod has already billed an hour of it. The rung is refused
    by the clock, not by the dollars, which is the case a per-pod budget cannot see.
    """
    opened(run, usd_per_hour=0.80)
    losses(tmp_path / "loss.jsonl", 110.0, [5, 10])
    run.main(["--train", "--arm", "a", "--loss", str(tmp_path / "loss.jsonl")], now=at(1550))
    state = json.loads(run.RECORD.read_text("utf-8"))
    assert state["measured_seconds_per_step"] == 110.0
    fitted = RECORD["money"]["arithmetic"]["seconds_per_step"]
    assert fitted < 110.0

    priced = run.recreate_check(RECORD, state, 0.50, ["a", "b"])
    assert priced["measured_seconds_per_step"] == 110.0
    assert priced["worst_case_remaining_seconds"] == pytest.approx(
        450 + 146 * 110.0 + 660.7 + 1800, abs=0.5
    )
    assert priced["verdict"] == "GO"  # nothing has been billed yet, so the window is whole

    run.main(
        ["--close-pod", "--deleted-at", at(3600).isoformat(), "--outcome", "arm A lost"],
        now=at(3600),
    )
    after_an_hour = run.recreate_check(
        RECORD, json.loads(run.RECORD.read_text("utf-8")), 0.80, ["a", "b"]
    )
    assert after_an_hour["cumulative_seconds_after_it"] > after_an_hour["hard_stop_seconds"]
    assert after_an_hour["reading_plus_remaining_usd"] < RECORD["money"]["cap_usd_all_in"]
    assert after_an_hour["verdict"] == "STOP"  # refused by the CLOCK, not by the dollars


# --- rung 10, the format smoke ----------------------------------------------


def smoke_reply(reply: str, balanced: bool = True) -> dict:
    item = SMOKE["items"][0]
    return {
        "id": item["id"],
        "rendering_sha256": item["rendering_sha256"],
        "reply": reply,
        "balanced": balanced,
    }


def test_the_smoke_passes_on_a_balanced_four_key_object(run, tmp_path):
    opened(run)
    state = json.loads(run.RECORD.read_text("utf-8"))
    msg_id = SMOKE["items"][0]["msg_id"]
    good = (
        f'{{"msg_id": {msg_id}, "subject_type": "не_наш_рынок",'
        ' "subject_id": null, "stance": null}'
    )
    path = tmp_path / "smoke_a.jsonl"
    path.write_text(json.dumps(smoke_reply(good), ensure_ascii=False) + "\n", encoding="utf-8")
    verdict = run.smoke(RECORD, state, "a", path, at(0))
    assert verdict["verdict"] == "GO"
    assert verdict["parsed_keys"] == ["msg_id", "stance", "subject_id", "subject_type"]
    assert "SPENT at its first gold-row reply" in verdict["next_step"]


@pytest.mark.parametrize(
    ("reply", "balanced", "why"),
    [
        ('{"msg_id": 20651, "subject_type": "не_наш_рынок"', False, "never closed"),
        ('{"msg_id": 20651, "subject_type": "не_наш_рынок"}', True, "ParseError"),
        ('{"msg_id": 1, "subject_type": null, "subject_id": null, "stance": null}', True, "Parse"),
    ],
)
def test_the_smoke_kills_the_arm_on_an_unparseable_or_short_object(
    run, tmp_path, reply, balanced, why
):
    opened(run)
    state = json.loads(run.RECORD.read_text("utf-8"))
    path = tmp_path / "smoke_a.jsonl"
    path.write_text(
        json.dumps(smoke_reply(reply, balanced), ensure_ascii=False) + "\n", encoding="utf-8"
    )
    verdict = run.smoke(RECORD, state, "a", path, at(0))
    assert verdict["verdict"] == "KILL"
    assert why in verdict["failure"]
    assert "is NOT evaluated" in verdict["next_step"]


def test_the_smoke_refuses_a_reply_whose_request_is_not_the_packs(run, tmp_path):
    opened(run)
    state = json.loads(run.RECORD.read_text("utf-8"))
    row = smoke_reply('{"msg_id": 1, "subject_type": null, "subject_id": null, "stance": null}')
    row["rendering_sha256"] = "0" * 64
    path = tmp_path / "smoke_a.jsonl"
    path.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
    assert run.smoke(RECORD, state, "a", path, at(0))["failure"].startswith("the pod answered")


def test_the_smoke_pack_drives_the_real_transport_and_the_gate_reads_its_output(run, tmp_path):
    """The whole of rung 10 in one loop: the pack the builder wrote, through the runner the pod
    launches, into the gate that grades it — on a FAKE client, at $0.

    The producer alone proves nothing here. The pod re-renders the item from its fields and refuses
    unless the sha matches, so what this drives is the half that can fail on the pod
    ([[drive_the_consumer_not_only_the_producer]]).
    """

    class FakeClient:
        def read(self, task, items):
            (item,) = items
            content = shipped.render(prompts, item, task)
            msg_id = int(content.split('<comment msg_id="')[1].split('"')[0])
            answer = json.dumps(
                {
                    "msg_id": msg_id,
                    "subject_type": "категория_личное",
                    "subject_id": None,
                    "stance": None,
                },
                ensure_ascii=False,
            )
            return [
                {
                    "content": answer + "\ntrailing prose the stop cuts",
                    "finish_reason": "stop",
                    "usage": {"prompt_tokens": 900, "completion_tokens": 40},
                }
            ]

    out = tmp_path / "lora_b_smoke_a.jsonl"
    # the sealed smoke pack pins the `prompts.py` of the day it was written, and D0.2 moved that
    # module; the handshake refuses it now, for the right reason. The copy re-pins ONLY that, in
    # tmp_path — the sealed file is never written ([[tests/moved_pins.py]])
    servable = tmp_path / "smoke_pack.json"
    servable.write_text(
        json.dumps(moved_pins.servable(SMOKE), ensure_ascii=False), encoding="utf-8"
    )
    assert (
        podrunner.main(
            [
                "--pack",
                str(servable),
                "--out",
                str(out),
                "--repo",
                str(REPO_ROOT),
            ],
            loader=lambda pack, repo: FakeClient(),
        )
        == 0
    )
    rows = [json.loads(line) for line in out.read_text("utf-8").splitlines() if line]
    assert len(rows) == 1 and rows[0]["balanced"] is True

    opened(run)
    state = json.loads(run.RECORD.read_text("utf-8"))
    verdict = run.smoke(RECORD, state, "a", out, at(0))
    assert verdict["verdict"] == "GO"
    assert verdict["failure"] is None


def test_the_smoke_pack_renders_the_request_the_dataset_trained_on():
    """The other half of the same claim: the fields render to the prompt the arm was trained on."""
    item = SMOKE["items"][0]
    training = {
        json.loads(line)["id"]: json.loads(line)
        for line in (REPO_ROOT / "results" / "pass1_sft_arm_a.jsonl")
        .read_text("utf-8")
        .splitlines()
        if line
    }
    with podrunner.as_pass1():
        rendered = shipped.render(prompts, item, SMOKE["task"])
    assert rendered == training[item["id"]]["prompt"]


def test_the_smoke_row_is_in_neither_the_sealed_fourteen_nor_the_eval_pack():
    """The claim that makes «the attempt is not spent» true, asserted against both populations."""
    pack = json.loads((REPO_ROOT / "results" / "pass1_probe_b_pack.json").read_text("utf-8"))
    gold_ids = {int(one["msg_id"]) for one in RECORD["population"]["gold"]["rows"]}
    item = SMOKE["items"][0]
    assert int(item["msg_id"]) not in gold_ids
    assert int(item["msg_id"]) not in {int(one["msg_id"]) for one in pack["items"]}
    assert item["id"] not in {one["id"] for one in pack["items"]}
    training = [
        json.loads(line)
        for line in (REPO_ROOT / "results" / "pass1_sft_arm_a.jsonl")
        .read_text("utf-8")
        .splitlines()
        if line
    ]
    assert item["id"] in {row["id"] for row in training}


# --- the record itself ------------------------------------------------------


def test_every_gate_is_appended_and_none_is_overwritten(run, tmp_path):
    opened(run)
    state = json.loads(run.RECORD.read_text("utf-8"))
    run.append_gate(state, {"verdict": "GO"}, "one")
    run.append_gate(state, {"verdict": "KILL"}, "two")
    written = json.loads(run.RECORD.read_text("utf-8"))
    assert [one["kind"] for one in written["gates"]] == ["price", "one", "two"]
    assert written["latest"] == {"kind": "two", "verdict": "KILL", "pod": 1}


def test_the_thresholds_are_read_out_of_the_registration_and_never_typed():
    """Every rung's number, back out of the record the gates act on."""
    assert gate.first_number(gate.rung(RECORD, 2)["rule"]) == 180
    assert gate.first_number(gate.rung(RECORD, 3)["rule"]) == 450
    assert gate.first_number(gate.rung(RECORD, 4)["rule"]) == 122
    assert gate.first_number(gate.rung(RECORD, 5)["rule"]) == 2.50
    assert RECORD["money"]["arithmetic"]["cumulative"]["hard_stop_seconds"] == 5.5 * 3600


def test_a_torn_last_loss_line_is_dropped_and_a_torn_middle_one_is_refused(run, tmp_path):
    path = tmp_path / "loss.jsonl"
    path.write_text('{"step": 5, "seconds_per_step": 60.0}\n{"step": 10, "seco', encoding="utf-8")
    assert [row["step"] for row in run.log_lines(path)] == [5]
    path.write_text('{"step": 5, "seco\n{"step": 10, "seconds_per_step": 60.0}\n', encoding="utf-8")
    with pytest.raises(SystemExit, match="damaged file"):
        run.log_lines(path)
