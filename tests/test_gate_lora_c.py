"""lora-c's nine session rungs, DRIVEN — every one, both verdicts, at $0 and with no pod.

`results/prereg_lora_c.json::kill_clock` registers nine CONDITIONS and `scripts/gate_lora_c.py`
grades them. A registered rung nobody has watched fire is not a rung
([[a_registered_bar_may_have_no_producer]], [[guard_selftest_negative_control]]), so each one is
exercised the way the session will use it: one fabricated pod, `now` injected, and the state file
the run appends to redirected into `tmp_path`.

Two properties this file exists for beyond «it runs»:

* **rung 0 refuses a price with no registered column**, including one CHEAPER than every column.
  Ruling (о) names a card this repo has never billed, and every projection rung divides by a price.
* **rung 3 is a bound, not a projection.** Its first version charged the remaining steps at the
  smoke's kill-clock ceiling and would have KILLED every session at the first base leg.
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import gate_lora_b as sibling  # noqa: E402
import gate_lora_c as gate  # noqa: E402

PREREG = json.loads((REPO_ROOT / "results" / "prereg_lora_c.json").read_text("utf-8"))
CREATE = "2026-08-24T21:00:00+00:00"


def at(seconds: float, created: str = CREATE) -> datetime:
    return gate.stamp(created) + timedelta(seconds=seconds)


@pytest.fixture
def run(tmp_path, monkeypatch):
    """The state file redirected and the registration read from the committed one.

    The gate refuses an untracked or dirty registration by design, so the test hands it the
    committed record directly — what is being driven here is the arithmetic, not the git clock,
    and `tests/test_gate_lora_b.py` already drives that refusal on the sibling.
    """
    monkeypatch.setattr(gate, "RECORD", tmp_path / "lora_c_run.json")
    monkeypatch.setattr(gate, "registration", lambda: gate.as_the_sibling_reads_it(PREREG))
    monkeypatch.setattr(sibling, "RECORD", tmp_path / "lora_c_run.json")
    return gate


def backstop_for(run, created: str = CREATE) -> str:
    state = json.loads(run.RECORD.read_text("utf-8")) if run.RECORD.exists() else {}
    left = (
        PREREG["money"]["pre_pod_arithmetic"]["hard_stop_seconds"] - sibling.billed_before(state)[0]
    )
    return (gate.stamp(created) + timedelta(seconds=left)).isoformat(timespec="seconds")


def opened(run, *, usd_per_hour=0.72, card="RTX PRO 4500", created=CREATE, pod_id="pod-1"):
    return run.main(
        [
            "--open",
            "--pod-id",
            pod_id,
            "--created-at",
            created,
            "--usd-per-hour",
            str(usd_per_hour),
            "--card",
            card,
            "--terminate-after",
            backstop_for(run, created),
        ],
        now=at(1, created),
    )


def test_every_registered_threshold_is_the_first_number_of_its_own_rule():
    """`first_number` reads thresholds out of prose, and prose is where a threshold goes to die.

    Four words in front of a figure once turned a 600 s deadline into 5 s
    ([[a_threshold_that_lives_in_prose]]). Every rung of this registration carries its threshold as
    a NUMBER as well, and this is the check that the two can never disagree.
    """
    assert [one["rung"] for one in PREREG["kill_clock"]] == list(range(9))
    for one in PREREG["kill_clock"]:
        assert sibling.first_number(one["rule"]) == pytest.approx(float(one["threshold"])), one[
            "name"
        ]


def test_the_plan_table_is_derived_and_sums_to_the_registered_work():
    """Every quantity the projection prices, re-derived from the registration it was read out of."""
    record = gate.as_the_sibling_reads_it(PREREG)
    table = gate.plan(record)
    assert sorted(table) == sorted(gate.ORDER)
    calls = sum(one.get("pass_1_calls", 0) for one in table.values())
    assert calls == 4 * 198 + 40, "four eval legs of 198, plus the marker census's 40"
    assert sum(one.get("steps", 0) for one in table.values()) == 144 + 6
    assert sum(one.get("pass_2_threads", 0) for one in table.values()) == 22, "2 legs × 11 threads"
    # and nothing is left after the last milestone
    assert gate.remaining_after(record, "marker_census") == {
        "pass_1_calls": 0,
        "steps": 0,
        "pass_2_threads": 0,
    }
    assert gate.remaining_after(record, "base_v2")["pass_1_calls"] == 3 * 198 + 40


@pytest.mark.parametrize(
    "price, card, want",
    (
        (0.72, "RTX PRO 4500", 0),
        (0.72, "NVIDIA RTX PRO 4500 Blackwell", 0),
        (0.74, "RTX 4090", 0),
        (0.74, "NVIDIA GeForce RTX 4090", 0),
        (0.69, "RTX 2000 Ada", 2),
        (0.89, "RTX PRO 6000", 2),
        (0.80, "RTX A6000", 2),
        (0.72, "RTX PRO 4000", 2),
        (0.74, "L4", 2),
    ),
)
def test_rung_0_refuses_an_unregistered_price_and_an_unauthorised_card(run, price, card, want):
    """Three failure modes, and the two that a price-only rung would miss.

    $0.69/h is CHEAPER than every column and is still a KILL: the break-even was never solved at
    it, so every projection rung after the create would divide by a price this record does not hold
    ([[a_rate_is_a_property_of_the_pod]]).

    The last three are the card. `RTX A6000` is what ruling (к) originally named and ruling (о)
    replaced — an authorised PRICE on a card nobody authorised. `RTX PRO 4000` is 24 GB at exactly
    $0.72, and `L4` is 24 GB at a listed price the plan happens to hold a column for. Every one of
    them would pass a rung that graded the number alone, and the seconds this plan is charged in
    are a property of the CARD ([[capability_gate_is_not_a_theme_gate]]).

    Both spellings of each authorised card are accepted: the create response names the platform's
    own `gpuId`, and the record carries the short displayName beside it.
    """
    assert opened(run, usd_per_hour=price, card=card) == want


@pytest.mark.parametrize(
    "elapsed, ssh_ok, want", ((120, False, 3), (499, False, 3), (500, False, 2), (120, True, 0))
)
def test_rung_1_waits_then_kills_and_an_answer_is_a_go(run, elapsed, ssh_ok, want):
    """Three outcomes on the registered 500 s, not two: WAIT is what a poll before the deadline is."""
    opened(run)
    argv = ["--gate0"] + (["--ssh-ok"] if ssh_ok else [])
    assert run.main(argv, now=at(elapsed)) == want


def test_rung_1_reads_its_own_threshold_and_not_the_siblings():
    """The boot gate is written here because lora-b's reads ITS rung 2, and ours is liveness.

    Reusing `gate_lora_b.gate_zero` would have graded a 500 s boot against a 600 s deadline that
    means something else entirely ([[a_borrowed_rule_carries_an_unstated_population]]).
    """
    assert sibling.first_number(sibling.rung(PREREG, 1)["rule"]) == 500
    assert sibling.first_number(sibling.rung(PREREG, 2)["rule"]) == 600
    lora_b = json.loads((REPO_ROOT / "results" / "prereg_lora_b.json").read_text("utf-8"))
    assert sibling.first_number(sibling.rung(lora_b, 2)["rule"]) == 180


@pytest.mark.parametrize("quiet, want", ((300, 0), (599, 0), (600, 2), (900, 2)))
def test_rung_2_kills_on_silence_measured_from_the_last_EVENT(run, quiet, want):
    """The deadline runs from the last thing that happened, never from the last poll."""
    opened(run)
    last = at(1000).isoformat(timespec="seconds")
    assert run.main(["--liveness", "--last-event", last], now=at(1000 + quiet)) == want


def test_rung_3_prices_the_remainder_at_the_rate_the_leg_is_realising(run, tmp_path):
    """The base leg graded while it is paid for — the first spend decision, not the fourth.

    At the charged 6.14 s/call the plan fits; at 12 s/call on a card this repo has never billed it
    does not, and the difference is discovered during the FIRST leg instead of after the smoke.
    """
    opened(run)
    replies = tmp_path / "base_v2.jsonl"

    replies.write_text("".join(json.dumps({"id": n}) + "\n" for n in range(100)), encoding="utf-8")
    started = at(300).isoformat(timespec="seconds")
    fast = run.main(
        ["--rate", "--leg", "base_v2", "--replies", str(replies), "--started-at", started],
        now=at(300 + 100 * 6.14),
    )
    assert fast == 0

    slow = run.main(
        ["--rate", "--leg", "base_v2", "--replies", str(replies), "--started-at", started],
        now=at(300 + 100 * 20.0),
    )
    assert slow == 2


def test_rung_3_waits_while_no_reply_has_landed(run, tmp_path):
    """A leg that has answered nothing has no rate, and a rate from zero rows is a division."""
    opened(run)
    replies = tmp_path / "base_v2.jsonl"
    replies.write_text("", encoding="utf-8")
    assert (
        run.main(
            ["--rate", "--leg", "base_v2", "--replies", str(replies), "--started-at", CREATE],
            now=at(400),
        )
        == 3
    )


def loss_log(path: Path, seconds_per_step: list[float]) -> Path:
    path.write_text(
        "".join(
            json.dumps({"step": n, "seconds_per_step": one}) + "\n"
            for n, one in enumerate(seconds_per_step, start=1)
        ),
        encoding="utf-8",
    )
    return path


def test_rung_4_buys_the_only_s_per_step_this_line_may_use(run, tmp_path):
    """Six steps under the ceiling is a GO, and the measurement is kept on the state."""
    opened(run)
    log = loss_log(tmp_path / "smoke.jsonl", [70.0] * 6)
    assert run.main(["--smoke", "--loss", str(log)], now=at(2000)) == 0
    state = json.loads(run.RECORD.read_text("utf-8"))
    assert state["measured_seconds_per_step"] == pytest.approx(70.0)


def test_rung_4_waits_until_all_six_steps_have_logged(run, tmp_path):
    opened(run)
    log = loss_log(tmp_path / "smoke.jsonl", [70.0] * 3)
    assert run.main(["--smoke", "--loss", str(log)], now=at(2000)) == 3


def test_rung_4_kills_over_the_ceiling_and_on_an_OOM(run, tmp_path):
    """Both KILL paths, and the OOM one has no branch: micro_batch is frozen law.

    32 GB against the 48 GB every prior reading of this stack was taken on is why ruling (о) makes
    the smoke the VRAM test at all ([[a_kill_threshold_from_one_passing_run]] — the shape this
    avoids by taking the ceiling from the registration and not from one passing run).
    """
    opened(run)
    over = loss_log(tmp_path / "slow.jsonl", [200.0] * 6)
    assert run.main(["--smoke", "--loss", str(over)], now=at(3000)) == 2

    fine = loss_log(tmp_path / "fine.jsonl", [70.0] * 6)
    assert run.main(["--smoke", "--loss", str(fine), "--oom"], now=at(3000)) == 2


def test_rung_5_projects_every_milestone_and_falls_back_LOUDLY(run, tmp_path):
    """The remainder shrinks milestone by milestone, and an unmeasured rate says it is unmeasured."""
    opened(run)
    seen = []
    for after in gate.ORDER:
        record = gate.as_the_sibling_reads_it(PREREG)
        state = json.loads(run.RECORD.read_text("utf-8"))
        one = gate.projection(record, state, after, 0.5, now=at(2000))
        seen.append(one["seconds_ahead"])
        assert one["seconds_per_step_is_measured"] is False
        assert one["seconds_per_call_is_measured"] is False
    assert seen == sorted(seen, reverse=True), "each milestone leaves strictly less to buy"
    assert seen[-1] == 0.0


def test_rung_5_kills_when_the_reading_plus_the_remainder_passes_the_cap(run, tmp_path):
    """The rung acts on the guard's READING plus the forecast, never on this clock alone."""
    opened(run)
    log = loss_log(tmp_path / "smoke.jsonl", [70.0] * 6)
    run.main(["--smoke", "--loss", str(log)], now=at(2000))
    assert run.main(["--projection", "--after", "smoke", "--reading", "0.50"], now=at(2100)) == 0
    assert run.main(["--projection", "--after", "smoke", "--reading", "3.60"], now=at(2100)) == 2


def test_rung_5_uses_the_smokes_measurement_once_it_exists(run, tmp_path):
    """A projection that quietly kept the charged rate would be the failure this ladder prevents."""
    opened(run)
    log = loss_log(tmp_path / "smoke.jsonl", [95.0] * 6)
    run.main(["--smoke", "--loss", str(log)], now=at(2000))
    record = gate.as_the_sibling_reads_it(PREREG)
    state = json.loads(run.RECORD.read_text("utf-8"))
    one = gate.projection(record, state, "smoke", 0.5, now=at(2100))
    assert one["seconds_per_step_is_measured"] is True
    assert one["seconds_per_step_used"] == pytest.approx(95.0)
    assert one["seconds_ahead"] == pytest.approx(
        144 * 95.0 + (2 * 198 + 40) * 6.14 + 22 * 97, abs=1
    )


def test_rung_6_a_second_pods_backstop_is_the_stop_LESS_what_the_first_billed(run):
    """The cumulative clock, on this line's registration — a fresh window per pod is the defect."""
    opened(run)
    deleted = at(4000).isoformat(timespec="seconds")
    run.main(["--close-pod", "--deleted-at", deleted, "--outcome", "rung 3"], now=at(4001))
    second = "2026-08-24T23:00:00+00:00"
    assert opened(run, created=second, pod_id="pod-2") == 0
    state = json.loads(run.RECORD.read_text("utf-8"))
    left = PREREG["money"]["pre_pod_arithmetic"]["hard_stop_seconds"] - 4000
    assert state["pods"][1]["terminate_after_computed"] == (
        gate.stamp(second) + timedelta(seconds=left)
    ).isoformat(timespec="seconds")


def test_rung_6_refuses_a_window_longer_than_the_cumulative_stop_allows(run):
    """The flag is the only thing enforcing the stop, so the caller has to SAY what it gave."""
    opened(run)
    deleted = at(4000).isoformat(timespec="seconds")
    run.main(["--close-pod", "--deleted-at", deleted, "--outcome", "rung 3"], now=at(4001))
    second = "2026-08-24T23:00:00+00:00"
    fresh = (gate.stamp(second) + timedelta(seconds=18000)).isoformat(timespec="seconds")
    with pytest.raises(SystemExit, match="beyond the"):
        run.main(
            [
                "--open",
                "--pod-id",
                "pod-2",
                "--created-at",
                second,
                "--usd-per-hour",
                "0.72",
                "--card",
                "RTX PRO 4500",
                "--terminate-after",
                fresh,
            ],
            now=at(1, second),
        )


def test_rung_7_refuses_a_second_pod_while_one_is_live(run, capsys):
    """Never two billing resources — refused BEFORE the create, not after the second meter starts."""
    assert run.main(["--pre-create-check"], now=at(0)) == 0
    opened(run)
    assert run.main(["--pre-create-check"], now=at(100)) == 2
    assert "is OPEN" in capsys.readouterr().out


def test_the_gate_puts_the_siblings_own_files_back(run):
    """The re-bind is for the length of a call — line B's gates keep reading line B's files."""
    before = (sibling.PHASE, sibling.PREREG)
    with gate.the_gate_reads_lora_c():
        assert sibling.PREREG == gate.PREREG
        assert sibling.PHASE == "lora-c"
    assert (sibling.PHASE, sibling.PREREG) == before


def test_the_view_moves_the_reference_and_never_the_number():
    """The hard stop has ONE home; the sibling's clock just reads it at a different path."""
    view = gate.as_the_sibling_reads_it(PREREG)
    assert (
        view["money"]["arithmetic"]["cumulative"]["hard_stop_seconds"]
        is PREREG["money"]["pre_pod_arithmetic"]["hard_stop_seconds"]
    )
    assert view["money"]["cap_usd_all_in"] == PREREG["money"]["cap_usd_all_in"]
    assert view["kill_clock"] is PREREG["kill_clock"]


def test_the_gate_is_driven_end_to_end_as_a_command():
    """The entry point RUN, not imported — a preamble is untested code until something executes it.

    `--pre-create-check` is the one rung that is meaningful with no pod and no state. TWO outcomes
    are accepted and they are both proofs that the preamble ran: the rung's own answer on a
    committed registration, and the registration guard's refusal while the record is dirty in the
    working tree. What neither of them can be is a crash — an ImportError or a broken preamble
    produces a third exit code and neither string, so this does not go green on silence
    ([[a_checker_whose_failure_is_silence]]).
    """
    done = subprocess.run(
        [sys.executable, "scripts/gate_lora_c.py", "--pre-create-check"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={"PYTHONPATH": "src", "PATH": "/usr/bin:/bin:/usr/local/bin"},
    )
    said = done.stdout + done.stderr
    if done.returncode == 0:
        assert "no pod is open" in said
    else:
        assert "prereg_lora_c.json" in said and "HEAD" in said, said
