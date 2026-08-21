"""pass1-window's Mac-side clock, DRIVEN — every rung, both verdicts, at $0 and with no pod.

The gates are the only thing between a registration and a bill, so they are exercised the way the
session will use them: one fabricated pod at a time, `now` injected, the state file redirected into
`tmp_path`. What this contract adds to r2's list is three properties of its own.

* **The sibling never touches r2's state.** r2's record is sealed and its launch stamp and pod log
  are still on disk in `results/` from the closed session. A watch loop that resolved
  `launched_at_of` in r2's module would write window state into a closed record and read a dead
  pod's clock ([[rewriting_a_record_resets_state_you_do_not_own]]). There is a negative control for
  it: r2's record path is redirected to a sentinel file and the whole flow is driven over it.
* **Rung 7 COUNTS what r2's gate refuses on.** The bar's third number is the sha-mismatch count, so
  a mismatch has to be a RED with a number beside it and not a stack trace. Both directions.
* **The bar's two numbers are jointly reachable.** `answered == 1032` and `refusals ≤ 10` are only
  satisfiable together because a refusal is an ANSWERED row — so ten refusals is a GO and eleven is
  a RED, and both are driven ([[an_expectation_no_reading_reaches]]).

r2's own three carry over unchanged and are driven here on this record's numbers: rung 5 FIRES on a
frozen out-file and does not on an advancing one; the watch loop cannot end quietly; rung 3 is
anchored on the runner's launch with a create-anchored backstop beside it.
"""

import json
import sys
from datetime import timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import gate_pass1_fewshot as r2gate  # noqa: E402
import gate_pass1_window as gate  # noqa: E402
import pass1_fewshot_pod_runner as transport  # noqa: E402

from market_pulse import prompts  # noqa: E402

RECORD = json.loads((REPO_ROOT / "results" / "prereg_pass1_window.json").read_text("utf-8"))
PACK = json.loads((REPO_ROOT / "results" / "pass1_window_pack.json").read_text("utf-8"))
RUNG3 = next(one for one in RECORD["kill_clock"] if one["rung"] == 3)
CEILING = gate.first_number(RUNG3["rule"])
BACKSTOP = float(RUNG3["backstop_seconds"])
SSH_DEADMAN = gate.first_number(gate.rung(RECORD, 2)["rule"])
IDLE = gate.first_number(gate.rung(RECORD, 5)["rule"])
HARD_STOP = RECORD["money"]["arithmetic"]["cumulative"]["hard_stop_seconds"]
LEG_OUT = RECORD["population"]["out_file"]
CREATE = "2026-08-21T09:00:00+00:00"


def at(seconds: float, created: str = CREATE):
    return gate.stamp(created) + timedelta(seconds=seconds)


@pytest.fixture
def run(tmp_path, monkeypatch):
    """The window gate with its state in tmp_path — and r2's record redirected to a SENTINEL.

    The sentinel is the negative control for the whole sibling: if any imported function still
    resolved r2's module state, this file would move.
    """
    monkeypatch.setattr(gate, "RECORD", tmp_path / "pass1_window_run.json")
    monkeypatch.setattr(gate, "POD_LOG", tmp_path / "pod.log")
    monkeypatch.setattr(gate, "registration", lambda: RECORD)
    sentinel = tmp_path / "r2_must_not_move.json"
    sentinel.write_text('{"sealed": true}\n', encoding="utf-8")
    monkeypatch.setattr(r2gate, "RECORD", sentinel)
    monkeypatch.setattr(r2gate, "POD_LOG", tmp_path / "r2_pod.log")
    gate.SENTINEL = sentinel
    return gate


def sealed_is_untouched(run) -> bool:
    return run.SENTINEL.read_text("utf-8") == '{"sealed": true}\n'


def backstop_for(run, created: str) -> str:
    state = json.loads(run.RECORD.read_text("utf-8")) if run.RECORD.exists() else {}
    left = HARD_STOP - gate.billed_before(state)[0]
    return (gate.stamp(created) + timedelta(seconds=left)).isoformat(timespec="seconds")


def opened(run, *, usd_per_hour=0.74, created=CREATE, pod_id="pod-1", terminate_after=None):
    return run.main(
        [
            "--price",
            "--pod-id",
            pod_id,
            "--created-at",
            created,
            "--usd-per-hour",
            str(usd_per_hour),
            "--card",
            "NVIDIA GeForce RTX 4090",
            "--terminate-after",
            terminate_after or backstop_for(run, created),
        ],
        now=at(5, created),
    )


def small(pack: dict = PACK, units: int = 4) -> dict:
    leg = pack["legs"][0]
    return {
        **pack,
        "legs": [{**leg, "items": leg["items"][:units]}],
        "population": {**pack["population"], "payable_comments": units},
    }


def pack_file(tmp_path: Path, pack: dict) -> Path:
    path = tmp_path / "pack.json"
    path.write_text(json.dumps(pack, ensure_ascii=False), encoding="utf-8")
    return path


def registered_for(pack: dict) -> dict:
    """The record with its population count matched to a cut-down pack — the gate compares them."""
    return {
        **RECORD,
        "population": {
            **RECORD["population"],
            "payable_comments": pack["population"]["payable_comments"],
        },
        "bars": {
            **RECORD["bars"],
            "completeness": {
                **RECORD["bars"]["completeness"],
                "owed": pack["population"]["payable_comments"],
                "answered_minimum": pack["population"]["payable_comments"],
            },
        },
    }


def launch_stamp(where: Path, seconds: float, created: str = CREATE) -> Path:
    """What the POD writes into its run directory the moment the runner starts, copied back."""
    where.mkdir(parents=True, exist_ok=True)
    path = where / gate.LAUNCH_STAMP
    path.write_text(at(seconds, created).isoformat(timespec="seconds") + "\n", encoding="utf-8")
    return path


def replied(where: Path, at_launch: float, name: str = LEG_OUT) -> None:
    """ONE row in the out-file, carrying the launch-relative stamp the runner itself writes."""
    where.mkdir(parents=True, exist_ok=True)
    (where / name).write_text(
        json.dumps({"id": "x", "elapsed_since_start": at_launch, "seconds": 5.0}) + "\n",
        encoding="utf-8",
    )


def answered(where: Path, leg: dict, n: int, seconds: float, elapsed0: float = 300.0) -> None:
    """`n` answered rows of a leg, each priced at `seconds` and stamped off the runner's clock."""
    where.mkdir(parents=True, exist_ok=True)
    lines = []
    for index, item in enumerate(leg["items"][:n]):
        lines.append(
            json.dumps(
                {
                    "index": index,
                    "id": item["id"],
                    "rendering_sha256": item["rendering_sha256"],
                    "reply": json.dumps(
                        {
                            "msg_id": int(item["msg_id"]),
                            "subject_type": "не_наш_рынок",
                            "subject_id": None,
                            "stance": None,
                        },
                        ensure_ascii=False,
                    ),
                    "balanced": True,
                    "seconds": seconds,
                    "elapsed_since_start": elapsed0 + index * seconds,
                    "boot_seconds": elapsed0,
                },
                ensure_ascii=False,
            )
        )
    (where / leg["out"]).write_text("\n".join(lines) + "\n", encoding="utf-8")


def closed_pod(run, *, created: str, pod_id: str, seconds: float) -> None:
    assert opened(run, created=created, pod_id=pod_id) == gate.GO
    assert (
        run.main(
            [
                "--close",
                "--deleted-at",
                at(seconds, created).isoformat(timespec="seconds"),
                "--outcome",
                "rung 2",
            ],
            now=at(seconds + 1, created),
        )
        == gate.GO
    )


# --- the sibling itself: nothing of r2's moves -------------------------------------------------------


def test_the_window_gate_names_its_OWN_record_stamp_and_log():
    assert gate.RECORD != r2gate.RECORD
    assert gate.LAUNCH_STAMP != r2gate.LAUNCH_STAMP
    assert gate.POD_LOG != r2gate.POD_LOG
    assert gate.PREREG != r2gate.PREREG
    # and r2's two are really on disk in results/, so a shared name would read a dead pod's clock
    assert (REPO_ROOT / "results" / r2gate.LAUNCH_STAMP).exists()
    assert r2gate.POD_LOG.exists()


def test_a_whole_flow_leaves_r2s_sealed_record_byte_identical(run, tmp_path):
    where = tmp_path / "run"
    assert opened(run) == gate.GO
    launch_stamp(where, 200.0)
    replied(where, 100.0)
    assert (
        run.main(["--boot", "--outdir", str(where)], now=at(400)) == gate.GO
    )  # rung 3 reads and WRITES launched_at into the state
    assert sealed_is_untouched(run)
    state = json.loads(run.RECORD.read_text("utf-8"))
    assert state["pods"][-1]["launched_at"] == at(200.0).isoformat(timespec="seconds")


# --- rung 1, the price and the platform-held backstop ------------------------------------------------


def test_the_price_gate_records_the_pod_and_refuses_a_window_longer_than_the_hard_stop(run):
    assert opened(run) == gate.GO
    state = json.loads(run.RECORD.read_text("utf-8"))
    assert state["pods"][-1]["pod_id"] == "pod-1"
    assert state["gates"][-1]["backstop"]["window_seconds"] == HARD_STOP
    run.RECORD.unlink()
    with pytest.raises(SystemExit, match="beyond the"):
        opened(
            run,
            terminate_after=at(HARD_STOP + gate.tolerance(RECORD) + 1).isoformat(
                timespec="seconds"
            ),
        )


def test_a_REFUSED_terminate_after_still_leaves_the_billing_pod_RECORDED(run):
    """The refusal fires when the pod already exists. Recording after it loses a live endpoint.

    `terminate_after` raises on an overshooting window — and by then `pod create` has returned, the
    meter is running and nothing in `results/pass1_window_run.json` knows the pod is there. So the
    pod is written FIRST, the refusal is recorded as a rung-1 KILL carrying the delete command, and
    only then does it re-raise.
    """
    over = at(HARD_STOP + gate.tolerance(RECORD) + 1).isoformat(timespec="seconds")
    with pytest.raises(SystemExit, match="beyond the"):
        opened(run, terminate_after=over, pod_id="pod-live")
    state = json.loads(run.RECORD.read_text("utf-8"))
    assert [one["pod_id"] for one in state["pods"]] == ["pod-live"]
    assert state["pods"][-1]["terminate_after"] == over
    assert "terminate_after_computed" not in state["pods"][-1]
    assert state["gates"][-1]["kind"] == "price-refused"
    assert state["gates"][-1]["verdict"] == "KILL"
    assert "runpodctl pod delete pod-live" in state["gates"][-1]["next_step"]
    # and the pod is LIVE in the record, so the next --pre-create-check refuses a second endpoint
    assert gate.live_pod(state)["pod_id"] == "pod-live"
    assert run.main(["--pre-create-check"]) == gate.KILL


def test_a_price_over_the_registered_ceiling_is_a_KILL_and_the_pod_is_still_recorded(run):
    ceiling = RECORD["money"]["meter"]["price_ceiling_usd_per_hour"]
    assert opened(run, usd_per_hour=ceiling + 0.01) == gate.KILL
    state = json.loads(run.RECORD.read_text("utf-8"))
    assert state["pods"][-1]["usd_per_hour"] == ceiling + 0.01
    assert "DELETE the pod now" in state["gates"][-1]["next_step"]


def test_a_second_pod_gets_what_the_hard_stop_has_LEFT_and_not_a_fresh_window(run):
    closed_pod(run, created=CREATE, pod_id="pod-1", seconds=SSH_DEADMAN)
    second = "2026-08-21T09:20:00+00:00"
    assert opened(run, created=second, pod_id="pod-2") == gate.GO
    state = json.loads(run.RECORD.read_text("utf-8"))
    assert state["gates"][-1]["backstop"]["window_seconds"] == HARD_STOP - SSH_DEADMAN


# --- rung 0, the recovery clause ---------------------------------------------------------------------


def test_pre_create_check_refuses_a_second_billing_endpoint(run):
    assert opened(run) == gate.GO
    assert run.main(["--pre-create-check"]) == gate.KILL


def test_pre_create_check_IS_the_recovery_clause_and_computes_its_own_knife_edge(run):
    sums = RECORD["money"]["arithmetic"]
    assert run.main(["--pre-create-check"]) == gate.GO
    gateway = gate.pre_create(RECORD, {})
    assert gateway["widest_dead_pod_that_still_fits_seconds"] == pytest.approx(
        HARD_STOP - sums["total_seconds"]
    )
    # the registered knife edge and the computed one are the same number, and it is WIDER than
    # rung 2's ceiling — so a pod killed by rung 2 can never close the recovery clause
    assert gateway["widest_dead_pod_that_still_fits_seconds"] == pytest.approx(
        sums["recovery_arithmetic"]["widest_dead_pod_that_still_fits_seconds"]
    )
    assert gateway["widest_dead_pod_that_still_fits_seconds"] > SSH_DEADMAN

    closed_pod(run, created=CREATE, pod_id="pod-1", seconds=SSH_DEADMAN)
    assert run.main(["--pre-create-check"]) == gate.GO
    # a dead pod one second wider than the knife edge closes it
    run.RECORD.unlink()
    closed_pod(
        run,
        created=CREATE,
        pod_id="pod-wide",
        seconds=gateway["widest_dead_pod_that_still_fits_seconds"] + 1,
    )
    assert run.main(["--pre-create-check"]) == gate.KILL


def test_pre_create_check_refuses_a_THIRD_pod_even_when_the_seconds_would_fit(run):
    closed_pod(run, created=CREATE, pod_id="pod-1", seconds=10.0)
    closed_pod(run, created="2026-08-21T09:10:00+00:00", pod_id="pod-2", seconds=10.0)
    gateway = gate.pre_create(RECORD, json.loads(run.RECORD.read_text("utf-8")))
    assert gateway["fits_the_hard_stop"] and gateway["fits_the_cap"]
    assert not gateway["fits_the_re_creation_count"]
    assert run.main(["--pre-create-check"]) == gate.KILL


def test_the_overshoot_tolerance_is_READ_from_the_registration_and_its_absence_is_a_refusal():
    assert gate.tolerance(RECORD) == 60.0
    stripped = json.loads(json.dumps(RECORD))
    stripped["money"]["arithmetic"]["cumulative"].pop("backstop_tolerance_seconds")
    with pytest.raises(SystemExit, match="backstop_tolerance_seconds"):
        gate.tolerance(stripped)


# --- rung 2, the ssh dead-man ------------------------------------------------------------------------


def test_the_ssh_dead_man_waits_then_kills_on_this_records_ceiling(run):
    assert opened(run) == gate.GO
    assert run.main(["--gate0"], now=at(SSH_DEADMAN - 1)) == gate.WAIT
    assert run.main(["--gate0"], now=at(SSH_DEADMAN + 1)) == gate.KILL
    run.RECORD.unlink()
    assert opened(run) == gate.GO
    assert run.main(["--gate0", "--ssh-ok"], now=at(SSH_DEADMAN + 1)) == gate.GO


# --- rung 3, the launch anchor and its create-anchored backstop ---------------------------------------


def test_rung_3_is_anchored_on_the_LAUNCH_and_backstopped_on_create(run, tmp_path):
    where = tmp_path / "run"
    assert opened(run) == gate.GO
    launch_stamp(where, 200.0)
    replied(where, CEILING - 1)
    assert run.main(["--boot", "--outdir", str(where)], now=at(600)) == gate.GO
    run.RECORD.unlink()
    assert opened(run) == gate.GO
    replied(where, CEILING + 1)
    assert run.main(["--boot", "--outdir", str(where)], now=at(600)) == gate.KILL


def test_rung_3_reads_the_leg_the_RECORD_names_and_not_whatever_is_in_the_directory(run, tmp_path):
    """Dv620's class, on a one-leg pack: the reading is BY NAME and never a scan.

    `results/` carries r2's own out-files, and a gate that took the smallest
    `elapsed_since_start` in the directory would read the v2 dev leg's re-zeroed 2.72 s and report
    GO on any load whatever.
    """
    where = tmp_path / "run"
    assert opened(run) == gate.GO
    launch_stamp(where, 200.0)
    replied(where, CEILING + 100)  # the leg this record NAMES: over the ceiling
    replied(where, 2.72, name="pass1_dev_v2.jsonl")  # r2's leg, tiny — must be invisible
    replied(where, 2.72, name="pass1_dev_base.jsonl")
    assert gate.first_reply_after_launch(RECORD, where) == CEILING + 100
    assert run.main(["--boot", "--outdir", str(where)], now=at(600)) == gate.KILL


def test_rung_3_reads_the_FIRST_reply_and_not_the_last(run, tmp_path):
    """`min` and `max` over `elapsed_since_start` differ only when the file has more than one row.

    Every other test here writes ONE row, so `min -> max` survives all of them — and `max` is the
    permissive direction on a long run: an out-file 400 rows deep would report the LAST reply's
    elapsed against a 450 s ceiling and KILL a pod that booted in 140 s. Three rows decide it.
    """
    where = tmp_path / "run"
    where.mkdir(parents=True, exist_ok=True)
    (where / LEG_OUT).write_text(
        "\n".join(
            json.dumps({"id": f"x{i}", "elapsed_since_start": e, "seconds": 2.7})
            for i, e in enumerate((140.0, 260.0, 900.0))
        )
        + "\n",
        encoding="utf-8",
    )
    assert gate.first_reply_after_launch(RECORD, where) == 140.0

    assert opened(run) == gate.GO
    launch_stamp(where, 200.0)
    # the boot was 140 s of a 450 s ceiling — GO. Under `max` this same file reads 900 s and KILLs
    assert run.main(["--boot", "--outdir", str(where)], now=at(1200)) == gate.GO
    state = json.loads(run.RECORD.read_text("utf-8"))
    assert state["gates"][-1]["first_reply_at_launch_elapsed_seconds"] == 140.0


def test_the_create_anchored_BACKSTOP_kills_a_pod_with_a_FRESH_launch_stamp(run, tmp_path):
    where = tmp_path / "run"
    assert opened(run) == gate.GO
    # a stamp taken just now, so the launch anchor has all its seconds left — and create-elapsed is
    # already past the backstop. The backstop is what refuses to let a late stamp buy a new window
    launch_stamp(where, BACKSTOP - 10)
    gateway = gate.gate_boot(
        RECORD,
        json.loads(run.RECORD.read_text("utf-8")),
        BACKSTOP + 1,
        None,
        at(BACKSTOP - 10).isoformat(timespec="seconds"),
        at(BACKSTOP + 1),
    )
    assert gateway["verdict"] == "KILL"
    assert "after create" in gateway["cause"] or "since create" in gateway["cause"]
    assert run.main(["--boot", "--outdir", str(where)], now=at(BACKSTOP + 1)) == gate.KILL


def test_a_run_record_without_a_launch_stamp_can_NEVER_report_GO(run, tmp_path):
    where = tmp_path / "run"
    assert opened(run) == gate.GO
    replied(where, 10.0)  # a reply, and no stamp beside it
    gateway = gate.gate_boot(
        RECORD, json.loads(run.RECORD.read_text("utf-8")), 300.0, 10.0, None, at(300)
    )
    assert gateway["verdict"] == "KILL"
    assert "NO launch anchor" in gateway["cause"]
    assert run.main(["--boot", "--outdir", str(where)], now=at(300)) == gate.KILL


def test_a_launch_stamp_that_predates_the_pod_or_sits_in_the_future_is_REFUSED(run, tmp_path):
    where = tmp_path / "run"
    assert opened(run) == gate.GO
    state = json.loads(run.RECORD.read_text("utf-8"))
    launch_stamp(where, -(gate.tolerance(RECORD) + 10))
    with pytest.raises(SystemExit, match="BEFORE"):
        gate.launched_at_of(RECORD, state, where, at(300))
    launch_stamp(where, 300 + gate.tolerance(RECORD) + 10)
    with pytest.raises(SystemExit, match="FUTURE"):
        gate.launched_at_of(RECORD, state, where, at(300))


def test_the_launch_stamp_is_written_into_the_pod_ONCE_and_never_moved_forward(run, tmp_path):
    where = tmp_path / "run"
    assert opened(run) == gate.GO
    state = json.loads(run.RECORD.read_text("utf-8"))
    launch_stamp(where, 100.0)
    first = gate.launched_at_of(RECORD, state, where, at(200))
    launch_stamp(where, 900.0)
    assert gate.launched_at_of(RECORD, state, where, at(1000)) == first


# --- rung 4, the projection --------------------------------------------------------------------------


def test_the_projection_prices_the_leg_still_owed_and_kills_a_run_that_leaves_the_cap(
    run, tmp_path
):
    where = tmp_path / "run"
    pack = small(units=200)
    assert opened(run) == gate.GO
    state = json.loads(run.RECORD.read_text("utf-8"))
    answered(where, pack["legs"][0], 20, seconds=2.7)
    healthy = gate.projection(RECORD, state, gate.leg_state(RECORD, [pack], where), at(400))
    assert healthy["verdict"] == "GO"
    assert healthy["legs"][0]["rate_source"] == "measured"
    assert healthy["calls_remaining"] == 180
    # the same rows at a rate the cap cannot pay for
    answered(where, pack["legs"][0], 20, seconds=90.0)
    sick = gate.projection(RECORD, state, gate.leg_state(RECORD, [pack], where), at(400))
    assert sick["verdict"] == "KILL"
    assert sick["over_the_cap"] or sick["over_the_hard_stop"]


def test_a_leg_with_no_reply_is_priced_at_the_REGISTERED_rate_and_never_lower(run, tmp_path):
    where = tmp_path / "run"
    pack = small(units=50)
    registered = RECORD["money"]["arithmetic"]["seconds_per_call"]["v2"]
    legs = gate.leg_state(RECORD, [pack], where)
    assert legs[0]["rate_source"] == "registered"
    assert legs[0]["seconds_per_call_used"] == registered
    assert legs[0]["remaining"] == 50


# --- rung 5, the liveness loop -----------------------------------------------------------------------


class Clock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


def test_the_watch_loop_KILLS_a_pod_whose_out_file_has_stopped_growing(run, tmp_path):
    where = tmp_path / "run"
    pack = small(units=8)
    assert opened(run) == gate.GO
    state = json.loads(run.RECORD.read_text("utf-8"))
    answered(where, pack["legs"][0], 3, seconds=2.7)
    launch_stamp(where, 200.0)
    clock = Clock()
    killed = []
    gateway = gate.watch(
        RECORD,
        state,
        [pack],
        where=where,
        log=tmp_path / "pod.log",
        pull=lambda: None,
        kill=lambda: killed.append("deleted") or {"deleted": True},
        sleep=clock.sleep,
        now=at(600),
        clock_now=clock,
        poll_seconds=60.0,
    )
    assert gateway["verdict"] == "KILL"
    assert "rung 5" in gateway["cause"]
    assert gateway["idle_seconds"] >= IDLE
    assert killed == ["deleted"]
    assert sealed_is_untouched(run)


def test_the_watch_loop_returns_GO_when_every_unit_is_answered_and_never_kills_a_working_pod(
    run, tmp_path
):
    where = tmp_path / "run"
    pack = small(units=8)
    assert opened(run) == gate.GO
    state = json.loads(run.RECORD.read_text("utf-8"))
    launch_stamp(where, 200.0)
    clock = Clock()
    grown = {"n": 0}

    def pull():
        grown["n"] += 2
        answered(where, pack["legs"][0], min(grown["n"], 8), seconds=2.7)

    killed = []
    gateway = gate.watch(
        RECORD,
        state,
        [pack],
        where=where,
        log=tmp_path / "pod.log",
        pull=pull,
        kill=lambda: killed.append("deleted"),
        sleep=clock.sleep,
        now=at(600),
        clock_now=clock,
        poll_seconds=20.0,
    )
    assert gateway["verdict"] == "GO"
    assert gateway["answered"] == 8 == gateway["owed"]
    assert killed == []
    assert sealed_is_untouched(run)


def test_a_FLAPPING_copy_does_not_keep_a_dead_pod_alive(run, tmp_path):
    """N → 0 → N → 0 is four changes and no work. The fingerprint is a HIGH-WATER mark."""
    where = tmp_path / "run"
    pack = small(units=8)
    assert opened(run) == gate.GO
    state = json.loads(run.RECORD.read_text("utf-8"))
    launch_stamp(where, 200.0)
    clock = Clock()
    flap = {"n": 0}

    def pull():
        flap["n"] += 1
        answered(where, pack["legs"][0], 3 if flap["n"] % 2 else 0, seconds=2.7)

    killed = []
    gateway = gate.watch(
        RECORD,
        state,
        [pack],
        where=where,
        log=tmp_path / "pod.log",
        pull=pull,
        kill=lambda: killed.append("deleted"),
        sleep=clock.sleep,
        now=at(600),
        clock_now=clock,
        poll_seconds=60.0,
    )
    assert gateway["verdict"] == "KILL"
    assert "rung 5" in gateway["cause"]
    assert killed == ["deleted"]


def test_the_watch_kills_on_the_create_anchored_BACKSTOP_when_no_stamp_ever_arrives(run, tmp_path):
    where = tmp_path / "run"
    where.mkdir(parents=True, exist_ok=True)
    pack = small(units=8)
    assert opened(run) == gate.GO
    state = json.loads(run.RECORD.read_text("utf-8"))
    clock = Clock()
    killed = []
    gateway = gate.watch(
        RECORD,
        state,
        [pack],
        where=where,
        log=tmp_path / "pod.log",
        pull=lambda: None,
        kill=lambda: killed.append("deleted") or {"deleted": True},
        sleep=clock.sleep,
        now=at(BACKSTOP + 1),
        clock_now=clock,
        poll_seconds=20.0,
    )
    assert gateway["verdict"] == "KILL"
    assert "BACKSTOP" in gateway["cause"]
    assert "no launch stamp has been copied back at all" in gateway["cause"]
    assert killed == ["deleted"]


def test_the_watch_loop_kills_on_the_projection_from_INSIDE_the_loop(run, tmp_path):
    where = tmp_path / "run"
    pack = small(units=1000)
    assert opened(run) == gate.GO
    state = json.loads(run.RECORD.read_text("utf-8"))
    launch_stamp(where, 200.0)
    clock = Clock()
    killed = []
    grown = {"n": 20}

    def pull():
        grown["n"] += 1
        answered(where, pack["legs"][0], grown["n"], seconds=90.0)

    gateway = gate.watch(
        RECORD,
        state,
        [pack],
        where=where,
        log=tmp_path / "pod.log",
        pull=pull,
        kill=lambda: killed.append("deleted") or {"deleted": True},
        sleep=clock.sleep,
        now=at(600),
        clock_now=clock,
        poll_seconds=20.0,
    )
    assert gateway["verdict"] == "KILL"
    assert "rung 4" in gateway["cause"] or "rung 6" in gateway["cause"]
    assert killed == ["deleted"]


def test_a_watch_that_ENDS_leaves_a_record_and_an_instruction_and_re_raises(
    run, tmp_path, capsys, monkeypatch
):
    where = tmp_path / "run"
    where.mkdir(parents=True, exist_ok=True)
    pack = small(units=8)
    assert opened(run) == gate.GO
    monkeypatch.setattr(gate, "registration", lambda: registered_for(pack))
    path = pack_file(tmp_path, pack)

    def explode(*args, **kwargs):
        raise KeyboardInterrupt("the operator pressed ctrl-c")

    original = gate.watch
    gate.watch = explode
    try:
        with pytest.raises(KeyboardInterrupt):
            run.main(
                [
                    "--watch",
                    "--pack",
                    str(path),
                    "--ssh",
                    "root@nowhere",
                    "--ssh-port",
                    "22",
                    "--outdir",
                    str(where),
                ],
                now=at(600),
            )
    finally:
        gate.watch = original
    state = json.loads(run.RECORD.read_text("utf-8"))
    assert state["gates"][-1]["kind"] == "watch-ended"
    assert state["gates"][-1]["verdict"] == "KILL"
    assert "runpodctl pod delete pod-1" in state["gates"][-1]["next_step"]
    assert "STILL BILLING" in capsys.readouterr().out


# --- rung 7, the completeness bar --------------------------------------------------------------------


def test_a_complete_out_file_is_a_GO_and_one_row_short_is_a_RED(run, tmp_path):
    where = tmp_path / "run"
    pack = small(units=20)
    record = registered_for(pack)
    assert opened(run) == gate.GO
    state = json.loads(run.RECORD.read_text("utf-8"))
    answered(where, pack["legs"][0], 20, seconds=2.7)
    gateway = gate.completeness(record, state, pack, where, at(4000))
    assert gateway["verdict"] == "GO"
    assert (gateway["answered"], gateway["owed"], gateway["parsed"]) == (20, 20, 20)
    assert gateway["sha_mismatches"] == 0 and gateway["parse_refusals"] == 0

    answered(where, pack["legs"][0], 19, seconds=2.7)
    short = gate.completeness(record, state, pack, where, at(4000))
    assert short["verdict"] == "RED"
    assert short["answered"] == 19 and short["unanswered"] == 1
    assert short["unanswered_ids"] == [pack["legs"][0]["items"][19]["id"]]


def test_a_sha_mismatch_is_COUNTED_and_RED_and_never_an_exception(run, tmp_path):
    """r2's `answers_of` RAISES here. The bar's third number is the count, so this one reports it."""
    where = tmp_path / "run"
    pack = small(units=20)
    record = registered_for(pack)
    assert opened(run) == gate.GO
    state = json.loads(run.RECORD.read_text("utf-8"))
    answered(where, pack["legs"][0], 20, seconds=2.7)
    lines = (where / LEG_OUT).read_text("utf-8").splitlines()
    row = json.loads(lines[7])
    row["rendering_sha256"] = "0" * 64
    lines[7] = json.dumps(row, ensure_ascii=False)
    (where / LEG_OUT).write_text("\n".join(lines) + "\n", encoding="utf-8")

    gateway = gate.completeness(record, state, pack, where, at(4000))
    assert gateway["verdict"] == "RED"
    assert gateway["sha_mismatches"] == 1
    assert gateway["sha_mismatch_ids"] == [row["id"]]
    assert gateway["answered"] == 20  # it ANSWERED — it answered the wrong request
    # and r2's own reader, on the same file, refuses instead of counting
    with pytest.raises(SystemExit, match="not the pack's"):
        r2gate.answers_of(where / LEG_OUT, pack["legs"][0]["items"])


def test_the_refusal_allowance_is_reachable_and_one_over_it_is_RED(run, tmp_path):
    """`answered == owed` AND `refusals ≤ 10` are jointly satisfiable, and both edges are driven."""
    where = tmp_path / "run"
    pack = small(units=1000)
    record = registered_for(pack)
    assert opened(run) == gate.GO
    state = json.loads(run.RECORD.read_text("utf-8"))
    allowance = int(record["bars"]["completeness"]["parse_refusals_maximum"])

    def with_refusals(n: int) -> dict:
        answered(where, pack["legs"][0], 1000, seconds=2.7)
        lines = (where / LEG_OUT).read_text("utf-8").splitlines()
        for index in range(n):
            row = json.loads(lines[index])
            row["reply"] = '{"msg_id": ' + str(index)  # a reply that never closed its object
            row["balanced"] = False
            lines[index] = json.dumps(row, ensure_ascii=False)
        (where / LEG_OUT).write_text("\n".join(lines) + "\n", encoding="utf-8")
        return gate.completeness(record, state, pack, where, at(4000))

    edge = with_refusals(allowance)
    assert edge["verdict"] == "GO"
    assert edge["answered"] == 1000 == edge["owed"]
    assert edge["parse_refusals"] == allowance
    assert edge["parsed"] == 1000 - allowance
    assert edge["replies_that_never_closed_their_object"] == allowance

    over = with_refusals(allowance + 1)
    assert over["verdict"] == "RED"
    assert over["parse_refusals"] == allowance + 1
    assert over["answered"] == 1000  # a refusal is an ANSWERED row and the count says so


def test_refusals_are_counted_BY_CAUSE_and_never_summed_into_one_class(run, tmp_path):
    where = tmp_path / "run"
    pack = small(units=20)
    record = registered_for(pack)
    assert opened(run) == gate.GO
    state = json.loads(run.RECORD.read_text("utf-8"))
    answered(where, pack["legs"][0], 20, seconds=2.7)
    lines = (where / LEG_OUT).read_text("utf-8").splitlines()
    broken = {0: "not json at all", 1: "{}", 2: '{"msg_id": 999999, "subject_type": null}'}
    for index, reply in broken.items():
        row = json.loads(lines[index])
        row["reply"] = reply
        lines[index] = json.dumps(row, ensure_ascii=False)
    (where / LEG_OUT).write_text("\n".join(lines) + "\n", encoding="utf-8")

    gateway = gate.completeness(record, state, pack, where, at(4000))
    assert gateway["parse_refusals"] == 3
    assert len(gateway["parse_refusals_by_cause"]) >= 2, gateway["parse_refusals_by_cause"]
    assert sum(gateway["parse_refusals_by_cause"].values()) == 3


def test_a_duplicate_id_and_an_id_the_leg_never_asked_are_both_RED(run, tmp_path):
    where = tmp_path / "run"
    pack = small(units=20)
    record = registered_for(pack)
    assert opened(run) == gate.GO
    state = json.loads(run.RECORD.read_text("utf-8"))
    answered(where, pack["legs"][0], 20, seconds=2.7)
    lines = (where / LEG_OUT).read_text("utf-8").splitlines()
    (where / LEG_OUT).write_text("\n".join(lines + [lines[0]]) + "\n", encoding="utf-8")
    duplicated = gate.completeness(record, state, pack, where, at(4000))
    assert duplicated["verdict"] == "RED"
    assert duplicated["answered"] == 20 and duplicated["rows_in_the_file"] == 21
    assert duplicated["duplicate_ids"] == [json.loads(lines[0])["id"]]

    stray = json.loads(lines[0])
    stray["id"] = "@nobody:1#1"
    (where / LEG_OUT).write_text("\n".join(lines + [json.dumps(stray)]) + "\n", encoding="utf-8")
    unknown = gate.completeness(record, state, pack, where, at(4000))
    assert unknown["verdict"] == "RED"
    assert unknown["ids_the_leg_never_asked"] == ["@nobody:1#1"]


def test_the_gate_holds_the_shipped_pack_to_the_SHA_the_record_pins(run, tmp_path, monkeypatch):
    """A count is not an identity, and neither is a path spelling.

    The population check compares one integer, and a pack rebuilt with the same 1 032 rows and a
    different rendering would pass it while silently becoming the reference rung 7 reads every reply
    against ([[the_guard_hashes_the_half_that_cannot_move]]). Both halves are driven: a tampered
    pack refuses, and it refuses through a path that is NOT `==` the module constant — `--pack
    results/pass1_window_pack.json` typed from the repo root is a RELATIVE Path, which is the
    spelling a guard written on `==` skips.
    """
    shipped = REPO_ROOT / "results" / "pass1_window_pack.json"
    assert gate.PACK == shipped
    assert RECORD["population"]["sha256"] == gate.summary.sha256_of(shipped)

    impostor = tmp_path / "pass1_window_pack.json"
    impostor.write_text(
        json.dumps({**PACK, "self_exclusion": {"tampered": True}}, ensure_ascii=False), "utf-8"
    )
    monkeypatch.setattr(gate, "PACK", impostor)
    assert opened(run) == gate.GO
    with pytest.raises(SystemExit, match="have parted"):
        run.main(["--completeness", "--pack", str(impostor), "--outdir", str(tmp_path)], now=at(1))

    detour = impostor.parent / ".." / impostor.parent.name / impostor.name
    assert detour != impostor and detour.resolve() == impostor.resolve()
    with pytest.raises(SystemExit, match="have parted"):
        run.main(["--completeness", "--pack", str(detour), "--outdir", str(tmp_path)], now=at(1))


def test_the_gate_refuses_a_pack_that_is_not_the_registered_population(run, tmp_path):
    assert opened(run) == gate.GO
    path = pack_file(tmp_path, small(units=8))
    with pytest.raises(SystemExit, match="population nobody priced"):
        run.main(["--completeness", "--pack", str(path), "--outdir", str(tmp_path)], now=at(4000))


# --- the registration is the only place a threshold lives ---------------------------------------------


def test_every_threshold_the_gate_acts_on_is_READ_out_of_the_registration():
    assert gate.first_number(gate.rung(RECORD, 2)["rule"]) == 500
    assert gate.first_number(gate.rung(RECORD, 3)["rule"]) == 450
    assert float(gate.rung(RECORD, 3)["backstop_seconds"]) == 1100
    assert gate.first_number(gate.rung(RECORD, 5)["rule"]) == 600
    assert gate.first_number(gate.rung(RECORD, 6)["rule"]) == 6500
    assert gate.tolerance(RECORD) == 60.0
    assert RECORD["bars"]["completeness"]["owed"] == 1032
    assert RECORD["bars"]["completeness"]["answered_minimum"] == 1032
    assert RECORD["bars"]["completeness"]["sha_mismatches_maximum"] == 0
    assert RECORD["bars"]["completeness"]["parse_refusals_maximum"] == 10
    assert RECORD["money"]["cap_usd_all_in"] == 1.50
    assert RECORD["money"]["meter"]["price_ceiling_usd_per_hour"] == 0.80
    # rung 3's rule carries TWO numbers and `first_number` reads positionally: the ceiling has to be
    # the first one in the sentence, or a reordered clause silently makes 1 100 the ceiling
    assert gate.first_number(gate.rung(RECORD, 3)["rule"]) != 1100
    # the sibling COPIED r2's rungs, so it is r2's NUMBERS that must not have come with them
    # ([[an_audit_of_pins_is_not_an_audit_of_thresholds]])
    assert gate.first_number(gate.rung(RECORD, 6)["rule"]) != 6100
    assert RECORD["money"]["cap_usd_all_in"] != 1.38
    # and the gate types none of them: no threshold appears as a literal in its source
    source = (REPO_ROOT / "scripts" / "gate_pass1_window.py").read_text("utf-8")
    for value in ("180", "500", "450", "1100", "600", "6100", "6500", "1.38", "1.50", "0.80"):
        assert f"= {value}" not in source, value
    # the bar's own three numbers are the ones rung 7 acts on, and a grep for `= <value>` would miss
    # them entirely — they reach the gate as `int(bar[...])` and never as a literal. Assert the
    # SHAPE instead: every number rung 7 compares is read out of the record's bar
    for name in ("owed", "answered_minimum", "sha_mismatches_maximum", "parse_refusals_maximum"):
        assert f'bar["{name}"]' in source, name
    for value in ("1032", "10", "0.01"):
        assert f"= {value}" not in source, value


def test_the_registration_is_refused_when_it_is_not_committed(tmp_path, monkeypatch):
    monkeypatch.setattr(gate, "PREREG", tmp_path / "untracked.json")
    (tmp_path / "untracked.json").write_text("{}", encoding="utf-8")
    with pytest.raises(SystemExit, match="not tracked by git"):
        gate.registration()


def test_the_gate_the_record_and_the_pack_agree_about_the_ONE_leg():
    (leg,) = PACK["legs"]
    assert leg["name"] == RECORD["population"]["leg"] == "v2"
    assert leg["out"] == RECORD["population"]["out_file"]
    assert leg["task"] == prompts.PASS1_TASK_V2
    assert len(leg["items"]) == RECORD["population"]["payable_comments"] == 1032
    assert RECORD["money"]["arithmetic"]["seconds_per_call"]["v2"] > 0
    assert set(RECORD["instruments"]["prompt_sha256"]) == set(prompts.PASS1)
    assert RECORD["instruments"]["packs"]["sha256"] == PACK["producer"]["sha256"]


# --- the transport, on THIS pack ---------------------------------------------------------------------


class FakeClient:
    def __init__(self):
        self.model = "the base model local_llm built"
        self.tasks = []

    def read(self, task, items):
        (item,) = items
        self.tasks.append(task)
        return [
            {
                "content": json.dumps(
                    {
                        "msg_id": int(item["msg_id"]),
                        "subject_type": "не_наш_рынок",
                        "subject_id": None,
                        "stance": None,
                    },
                    ensure_ascii=False,
                ),
                "finish_reason": "stop",
                "usage": {"prompt_tokens": 1400, "completion_tokens": 40},
            }
        ]


def test_the_shipped_runner_answers_a_ONE_leg_pack_unchanged(tmp_path):
    """The contract pre-authorised a finding here. There is none: `--only` already narrows.

    What is proved is that the one-leg pack runs through the SHIPPED runner with no edit — the
    handshake passes on this checkout, every item re-renders to the sha the pack pinned, and the
    replies land in the file the leg names.
    """
    pack = small(units=5)
    path = pack_file(tmp_path, pack)
    client = FakeClient()
    assert (
        transport.main(
            [
                "--pack",
                str(path),
                "--outdir",
                str(tmp_path / "run"),
                "--repo",
                str(REPO_ROOT),
                "--only",
                "v2",
            ],
            loader=lambda p, r: client,
        )
        == 0
    )
    rows = [
        json.loads(line)
        for line in (tmp_path / "run" / LEG_OUT).read_text("utf-8").splitlines()
        if line
    ]
    assert [row["id"] for row in rows] == [one["id"] for one in pack["legs"][0]["items"]]
    assert [row["rendering_sha256"] for row in rows] == [
        one["rendering_sha256"] for one in pack["legs"][0]["items"]
    ]
    assert client.tasks == [prompts.PASS1_TASK_V2] * 5
    assert all(row["balanced"] for row in rows)


def test_the_runner_REFUSES_the_pack_when_this_checkout_renders_something_else(tmp_path):
    pack = small(units=3)
    pack["legs"][0]["items"][1] = {**pack["legs"][0]["items"][1], "rendering_sha256": "0" * 64}
    with pytest.raises(SystemExit, match="The request moved"):
        transport.main(
            [
                "--pack",
                str(pack_file(tmp_path, pack)),
                "--outdir",
                str(tmp_path / "run"),
                "--repo",
                str(REPO_ROOT),
                "--only",
                "v2",
            ],
            loader=lambda p, r: FakeClient(),
        )


# --- D2's clause, verified at D0 on r2's own replies ---------------------------------------------------


def test_the_window_renders_the_dev_200_byte_for_byte_as_the_dev_pack_did():
    """The 200 rows r2 measured are IN this population, and they are asked the same request.

    Not a convenience: the report-only reading D2 owes — «the dev-200 should reproduce r2's 136/200
    and 38/49 up to decoding noise» — only means anything if the request did not move. It did not,
    for all 200, sha for sha ([[the_fixture_and_the_artifact_share_anchors]]).
    """
    dev = json.loads((REPO_ROOT / "results" / "pass1_dev_pack.json").read_text("utf-8"))
    v2 = {
        one["id"]: one for one in next(one for one in dev["legs"] if one["name"] == "v2")["items"]
    }
    window = {one["id"]: one for one in PACK["legs"][0]["items"]}
    common = set(v2) & set(window)
    assert len(common) == 200 == len(v2)
    assert all(v2[one]["rendering_sha256"] == window[one]["rendering_sha256"] for one in common)


def test_rung_7_and_D2s_reading_are_driven_on_r2s_REAL_replies(run, tmp_path):
    """The completeness bar and the report-only reading, on 200 replies a pod actually generated.

    Fabricated rows prove the gate's branches; these prove the gate against the transport. r2's
    `results/pass1_dev_v2.jsonl` is 200 real replies to requests this pack asks byte for byte, so
    they are valid rows of this contract's out-file — and D2's own clause («scored through
    scorer.reader_comment_agreement exactly as gate_pass1_fewshot.py::leg_table does») is checked
    HERE, at $0, rather than discovered after the money.
    """
    where = tmp_path / "run"
    where.mkdir(parents=True, exist_ok=True)
    dev_ids = set(PACK["membership"]["dev_200"]["ids"])
    leg = PACK["legs"][0]
    subset = {
        **PACK,
        "legs": [{**leg, "items": [one for one in leg["items"] if one["id"] in dev_ids]}],
        "population": {**PACK["population"], "payable_comments": 200},
    }
    assert len(subset["legs"][0]["items"]) == 200
    (where / leg["out"]).write_text(
        (REPO_ROOT / "results" / "pass1_dev_v2.jsonl").read_text("utf-8"), encoding="utf-8"
    )

    record = registered_for(subset)
    assert opened(run) == gate.GO
    state = json.loads(run.RECORD.read_text("utf-8"))
    bar = gate.completeness(record, state, subset, where, at(4000))
    assert bar["verdict"] == "GO"
    assert (bar["answered"], bar["parsed"], bar["sha_mismatches"], bar["parse_refusals"]) == (
        200,
        200,
        0,
        0,
    )

    # the report-only reading, through r2's OWN leg_table — the function D2's clause names. It reads
    # `bars.dev_gate.our_readings`, a key this record does not carry because this contract has no dev
    # gate, so D2 hands it the readings the record DOES carry under `bars.report_only.our_readings`
    ours = RECORD["bars"]["report_only"]["our_readings"]
    view = {**record, "bars": {**record["bars"], "dev_gate": {"our_readings": ours}}}
    table = r2gate.leg_table(view, subset, "v2", where)
    assert (table["agreed"], table["n"]) == (136, 200)
    assert (table["our_agreed"], table["our_n"]) == (38, 49)
    assert table["refused"] == [] and table["absent"] == 0
