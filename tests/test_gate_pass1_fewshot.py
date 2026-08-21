"""pass1-fewshot r2's Mac-side clock, DRIVEN — every rung, both verdicts, at $0 and with no pod.

The gates are the only thing between a registration and a bill, so they are exercised the way the
session will use them: one fabricated pod at a time, `now` injected, the state file redirected into
`tmp_path`. Three properties carry the money.

* **Rung 5 fires.** A frozen out-file is KILLED after the registered deadline and a pod that is
  DELETED by that KILL; an out-file that keeps advancing is not. A liveness rung nobody has watched
  fire is a rung nobody has ([[guard_selftest_negative_control]]) — and this one exists because
  lora-b billed 9 720 idle seconds under a registration whose every rung read a log that had
  stopped growing.
* **The watch loop cannot end quietly.** Whatever ends it — an exception inside it, Ctrl-C — leaves
  a recorded gate and a printed instruction naming the pod, and then re-raises: swallowing the
  cause in the cleanup arm is how a crash becomes a silent bill.
* **Rung 7 is checked for REACHABILITY as well as for its verdict.** `our_v2 − our_base ≥ 10` over
  49 rows cannot be met when the base already answers 40 of them, and that has to be a STOP the
  registration named rather than a RED discovered on a live pod.

r2 adds three properties to the same list. **Rung 3 is anchored on the runner's own launch**, so it
is driven on BOTH axes: 451 s past a launch stamp with a tiny create-elapsed dies, a fresh launch
stamp at 1 101 s of create-elapsed dies on the backstop, and a first reply with NO stamp beside it
cannot report GO — a deadline that cannot be demonstrated has not been passed. **The recovery clause
is a gate now**: `--pre-create-check` refuses the create that will not fit, and the knife-edge is
computed from the registration rather than typed. **The overshoot tolerance is READ**, and a record
without it is a refusal rather than a default.
"""

import json
import sys
from datetime import timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_pass1_fewshot_packs as packs  # noqa: E402
import gate_pass1_fewshot as gate  # noqa: E402

from market_pulse import prompts  # noqa: E402

RECORD = json.loads((REPO_ROOT / "results" / "prereg_pass1_fewshot_r2.json").read_text("utf-8"))
RUNG3 = next(one for one in RECORD["kill_clock"] if one["rung"] == 3)
CEILING = gate.first_number(RUNG3["rule"])
BACKSTOP = float(RUNG3["backstop_seconds"])
SSH_DEADMAN = gate.first_number(gate.rung(RECORD, 2)["rule"])
DEV = json.loads((REPO_ROOT / packs.DEV_NAME).read_text("utf-8"))
SHOT = json.loads((REPO_ROOT / packs.SHOT_NAME).read_text("utf-8"))
LABELS = None
CREATE = "2026-08-21T09:00:00+00:00"


def at(seconds: float, created: str = CREATE):
    return gate.stamp(created) + timedelta(seconds=seconds)


@pytest.fixture
def run(tmp_path, monkeypatch):
    monkeypatch.setattr(gate, "RECORD", tmp_path / "pass1_fewshot_r2_run.json")
    monkeypatch.setattr(gate, "POD_LOG", tmp_path / "pod.log")
    monkeypatch.setattr(gate, "registration", lambda: RECORD)
    return gate


def backstop_for(run, created: str) -> str:
    state = json.loads(run.RECORD.read_text("utf-8")) if run.RECORD.exists() else {}
    left = (
        RECORD["money"]["arithmetic"]["cumulative"]["hard_stop_seconds"]
        - gate.billed_before(state)[0]
    )
    return (gate.stamp(created) + timedelta(seconds=left)).isoformat(timespec="seconds")


def opened(run, *, usd_per_hour=0.74, created=CREATE, pod_id="pod-1", terminate_after=None):
    code = run.main(
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
    return code


def small(pack: dict, per_leg: int = 4) -> dict:
    return {**pack, "legs": [{**leg, "items": leg["items"][:per_leg]} for leg in pack["legs"]]}


def launch_stamp(where: Path, seconds: float, created: str = CREATE) -> Path:
    """What the POD writes into its run directory the moment the runner starts, copied back."""
    where.mkdir(parents=True, exist_ok=True)
    path = where / gate.LAUNCH_STAMP
    path.write_text(at(seconds, created).isoformat(timespec="seconds") + "\n", encoding="utf-8")
    return path


def replied(where: Path, at_launch: float, leg: str = "pass1_dev_base.jsonl") -> None:
    """ONE row in a dev out-file, carrying the launch-relative stamp the runner itself writes.

    `elapsed_since_start` is the runner's own monotonic seconds from its start to that row, so it IS
    «launch -> this reply». The gate reads it; nothing types a stamp.
    """
    where.mkdir(parents=True, exist_ok=True)
    (where / leg).write_text(
        json.dumps({"id": "x", "elapsed_since_start": at_launch, "seconds": 5.0}) + "\n",
        encoding="utf-8",
    )


def closed_pod(run, *, created: str, pod_id: str, seconds: float) -> None:
    """One pod opened and deleted after `seconds` — what a rung-2 KILL leaves behind."""
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


# --- rung 1, the price and the platform-held backstop ----------------------------------------------


def test_the_price_gate_records_the_pod_and_refuses_a_window_longer_than_the_hard_stop(run):
    assert opened(run) == gate.GO
    state = json.loads(run.RECORD.read_text("utf-8"))
    assert state["pods"][0]["pod_id"] == "pod-1"
    assert state["gates"][0]["rung"] == 1 and state["gates"][0]["verdict"] == "GO"
    # a pod over the ceiling is a KILL with no generation of any kind
    run.RECORD.unlink()
    assert opened(run, usd_per_hour=0.95, pod_id="pod-hot") == gate.KILL

    run.RECORD.unlink()
    too_long = (gate.stamp(CREATE) + timedelta(seconds=99_999)).isoformat(timespec="seconds")
    with pytest.raises(SystemExit, match="beyond the"):
        opened(run, terminate_after=too_long)


def test_a_second_pod_gets_what_the_hard_stop_has_LEFT_and_not_a_fresh_window(run):
    closed_pod(run, created=CREATE, pod_id="pod-1", seconds=SSH_DEADMAN)
    second = "2026-08-21T10:00:00+00:00"
    assert opened(run, created=second, pod_id="pod-2") == gate.GO
    state = json.loads(run.RECORD.read_text("utf-8"))
    window = gate.stamp(state["pods"][1]["terminate_after_computed"]) - gate.stamp(second)
    stop = RECORD["money"]["arithmetic"]["cumulative"]["hard_stop_seconds"]
    assert window.total_seconds() == stop - SSH_DEADMAN


def test_pre_create_check_refuses_a_second_billing_endpoint(run):
    assert run.main(["--pre-create-check"]) == gate.GO
    assert opened(run) == gate.GO
    assert run.main(["--pre-create-check"]) == gate.KILL


def test_pre_create_check_IS_the_recovery_clause_and_computes_its_own_knife_edge(run):
    """r1 pasted this arithmetic by hand before its second create. Here the gate refuses the create.

    The registration is built so that ONE dead pod at rung 2 (500 s) still leaves the whole worst
    case inside the hard stop; a dead pod one second past the computed edge does not. The edge is
    `hard_stop − total_seconds`, computed — never a number anybody typed.
    """
    sums = RECORD["money"]["arithmetic"]
    edge = sums["cumulative"]["hard_stop_seconds"] - sums["total_seconds"]
    assert edge == pytest.approx(
        sums["recovery_arithmetic"]["widest_dead_pod_that_still_fits_seconds"]
    )
    assert SSH_DEADMAN < edge < SSH_DEADMAN + 200, "a rung-2 death has to leave the recovery open"

    closed_pod(run, created=CREATE, pod_id="pod-dead", seconds=SSH_DEADMAN)
    allowed = run.main(["--pre-create-check"])
    assert allowed == gate.GO

    run.RECORD.unlink()
    closed_pod(run, created=CREATE, pod_id="pod-dead", seconds=edge + 1)
    assert run.main(["--pre-create-check"]) == gate.KILL


def test_pre_create_check_refuses_a_THIRD_pod_even_when_the_seconds_would_fit(run):
    """Two CHEAP deaths leave the seconds fitting, and only the registered count says no."""
    closed_pod(run, created=CREATE, pod_id="pod-1", seconds=60)
    assert run.main(["--pre-create-check"]) == gate.GO
    closed_pod(run, created="2026-08-21T10:00:00+00:00", pod_id="pod-2", seconds=60)
    state = json.loads(run.RECORD.read_text("utf-8"))
    gate_reading = gate.pre_create(RECORD, state)
    assert gate_reading["fits_the_hard_stop"] and gate_reading["fits_the_cap"]
    assert gate_reading["fits_the_re_creation_count"] is False
    assert gate_reading["verdict"] == "KILL"
    assert run.main(["--pre-create-check"]) == gate.KILL
    # and `--price` runs the SAME check, so a third pod created without step 0 is recorded (a pod
    # nothing counts is worse than a pod that should not exist) and then refused with its verdict
    assert opened(run, created="2026-08-21T11:00:00+00:00", pod_id="pod-3") == gate.KILL
    last = json.loads(run.RECORD.read_text("utf-8"))["gates"][-1]
    assert last["kind"] == "price" and last["verdict"] == "KILL"
    assert last["recovery"]["fits_the_re_creation_count"] is False
    assert "DELETE the pod now" in last["next_step"]


def test_the_overshoot_tolerance_is_READ_from_the_registration_and_its_absence_is_a_refusal():
    """Dv603: a number the gate ACTS on that lived in the gate's source. It lives in the record now.

    Driven in both directions — the registered value is what `terminate_after` forgives, and a
    registration without the field is a `SystemExit`, never a fallback to something typed here.
    """
    assert gate.tolerance(RECORD) == 60.0
    bent = json.loads(json.dumps(RECORD))
    del bent["money"]["arithmetic"]["cumulative"]["backstop_tolerance_seconds"]
    with pytest.raises(SystemExit, match="backstop_tolerance_seconds"):
        gate.tolerance(bent)
    assert "BACKSTOP_TOLERANCE_SECONDS" not in (
        REPO_ROOT / "scripts" / "gate_pass1_fewshot.py"
    ).read_text("utf-8"), "the constant left the source; it may not come back as a default"


# --- rungs 2 and 3 ---------------------------------------------------------------------------------


def test_the_ssh_dead_man_waits_then_kills_on_r2s_own_ceiling(run):
    """180 s was pass1-probe's reading of one night and it failed twice on 2026-08-20 (Dv602).

    Both directions on the ceiling the record now carries, one second either side of it.
    """
    assert SSH_DEADMAN == 500.0
    assert opened(run) == gate.GO
    assert run.main(["--gate0"], now=at(SSH_DEADMAN - 1)) == gate.WAIT
    assert run.main(["--gate0", "--ssh-ok"], now=at(SSH_DEADMAN - 1)) == gate.GO
    assert run.main(["--gate0"], now=at(SSH_DEADMAN + 1)) == gate.KILL


def test_rung_3_is_anchored_on_the_LAUNCH_and_backstopped_on_create(run, tmp_path):
    """Dv605: r1 derived the ceiling from the model LOAD and measured it from create.

    Four readings, each with a different pair of elapsed spans, so neither axis can be the only one
    that ever fires: a launch that is 451 s old with a create-elapsed nowhere near the backstop; a
    launch stamp one poll old at 1 101 s of create-elapsed; a reply inside both; and a reply outside
    the launch ceiling.
    """
    where = tmp_path / "out"
    assert opened(run) == gate.GO
    boot = ["--boot", "--outdir", str(where)]

    launch_stamp(where, 5)
    assert run.main(boot, now=at(200)) == gate.WAIT
    # the ANCHOR: 451 s since the runner launched, and only 456 s of create-elapsed
    assert run.main(boot, now=at(5 + CEILING + 1)) == gate.KILL
    assert at(5 + CEILING + 1) < at(BACKSTOP), "the backstop is nowhere near — the anchor fired"

    # a reply inside BOTH spans is the only GO — and the gate READS it off the out-file
    run.RECORD.unlink()
    assert opened(run) == gate.GO
    launch_stamp(where, 5)
    replied(where, 295.0)
    assert run.main(boot, now=at(310)) == gate.GO
    recorded = json.loads(run.RECORD.read_text("utf-8"))["gates"][-1]
    assert recorded["first_reply_at_launch_elapsed_seconds"] == 295.0
    assert recorded["first_reply_at_create_elapsed_seconds"] == 300.0
    # and a reply outside the LAUNCH ceiling is a KILL even though one exists
    replied(where, CEILING + 10)
    assert run.main(boot, now=at(5 + CEILING + 20)) == gate.KILL


def test_the_create_anchored_BACKSTOP_kills_a_pod_with_a_FRESH_launch_stamp(run, tmp_path):
    """The bound on the anchor. A stamp taken late cannot buy a window the registration never priced."""
    where = tmp_path / "out"
    assert opened(run) == gate.GO
    launch_stamp(where, BACKSTOP - 10)  # launched ten seconds ago by the anchor's own clock
    gate_reading = gate.gate_boot(
        RECORD,
        run.run_state(),
        gate.elapsed_since(CREATE, at(BACKSTOP + 1)),
        None,
        gate.launched_at_of(RECORD, run.run_state(), where, at(BACKSTOP + 1)),
        at(BACKSTOP + 1),
    )
    assert gate_reading["seconds_since_launch"] == 11.0 < CEILING
    assert gate_reading["verdict"] == "KILL"
    assert "since create" in gate_reading["cause"]

    # and the branch that is the whole point of having TWO spans: a reply well inside the launch
    # ceiling that is nonetheless past the create backstop. Without it the `and at_create <=
    # backstop` conjunct could be deleted and the suite would stay green
    replied(where, 12.0)
    late = gate.gate_boot(
        RECORD,
        run.run_state(),
        gate.elapsed_since(CREATE, at(BACKSTOP + 3)),
        gate.first_reply_after_launch(RECORD, where),
        gate.launched_at_of(RECORD, run.run_state(), where, at(BACKSTOP + 3)),
        at(BACKSTOP + 3),
    )
    assert late["first_reply_at_launch_elapsed_seconds"] == 12.0 <= CEILING
    assert late["first_reply_at_create_elapsed_seconds"] == BACKSTOP + 2 > BACKSTOP
    assert late["verdict"] == "KILL" and "after create" in late["cause"]


def test_a_run_record_without_a_launch_stamp_can_NEVER_report_GO(run, tmp_path):
    """A rung whose deadline cannot be demonstrated has not been passed — r1's own ruling, Dv601."""
    where = tmp_path / "out"
    where.mkdir(parents=True, exist_ok=True)
    assert opened(run) == gate.GO
    boot = ["--boot", "--outdir", str(where)]
    assert run.main(boot, now=at(200)) == gate.WAIT  # no stamp yet, and inside the backstop
    # a first reply that would have passed r1's create-anchored rung is NOT a GO without the anchor
    replied(where, 295.0)
    assert run.main(boot, now=at(310)) == gate.KILL
    state = json.loads(run.RECORD.read_text("utf-8"))
    last = state["gates"][-1]
    assert last["rung"] == 3 and last["launched_at"] is None
    assert "NO launch anchor" in last["cause"]
    assert "launched_at" not in state["pods"][-1]


def test_a_launch_stamp_that_predates_the_pod_or_sits_in_the_future_is_REFUSED(run, tmp_path):
    """The run directory is cleared before every launch; a stamp older than the pod means it was not."""
    where = tmp_path / "out"
    assert opened(run) == gate.GO
    launch_stamp(where, -3600)
    with pytest.raises(SystemExit, match="BEFORE"):
        gate.launched_at_of(RECORD, run.run_state(), where, at(200))
    launch_stamp(where, 9000)
    with pytest.raises(SystemExit, match="FUTURE"):
        gate.launched_at_of(RECORD, run.run_state(), where, at(200))
    (where / gate.LAUNCH_STAMP).write_text("not a stamp at all\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="not a UTC ISO8601 stamp"):
        gate.launched_at_of(RECORD, run.run_state(), where, at(200))


def test_the_launch_stamp_is_written_into_the_pod_ONCE_and_never_moved_forward(run, tmp_path):
    """A stamp that moved forward would push out the very deadline it places (v4's own rule)."""
    where = tmp_path / "out"
    assert opened(run) == gate.GO
    launch_stamp(where, 5)
    first = gate.launched_at_of(RECORD, run.run_state(), where, at(200))
    assert first == at(5).isoformat(timespec="seconds")
    launch_stamp(where, 400)  # the pod re-stamped, or a stale copy landed
    assert gate.launched_at_of(RECORD, run.run_state(), where, at(500)) == first


# --- rung 4, the projection ------------------------------------------------------------------------


def answered(where: Path, leg: dict, n: int, seconds: float, elapsed0: float = 300.0) -> None:
    where.mkdir(parents=True, exist_ok=True)
    rows = [
        {
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
        }
        for index, item in enumerate(leg["items"][:n])
    ]
    (where / leg["out"]).write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )


def test_the_projection_prices_every_leg_still_owed_and_kills_a_run_that_leaves_the_cap(
    run, tmp_path
):
    assert opened(run) == gate.GO
    where = tmp_path / "out"
    base = next(one for one in DEV["legs"] if one["name"] == "base")
    answered(where, base, 20, 5.0)
    state = run.run_state()
    legs = gate.leg_state(RECORD, [DEV, SHOT], where)
    good = gate.projection(RECORD, state, legs, now=at(600))
    assert good["verdict"] == "GO"
    assert good["calls_answered"] == 20
    assert good["calls_remaining"] == 180 + 200 + 64
    # the shot's own 64 calls ARE in the forecast — a projection over the running leg alone
    # would price 180 calls and open a run the cap closes
    assert good["legs"][-1]["name"] == "shot" and good["legs"][-1]["remaining"] == 64

    answered(where, base, 20, 60.0)  # the same 20 calls, six times slower
    slow = gate.projection(RECORD, state, gate.leg_state(RECORD, [DEV, SHOT], where), now=at(600))
    assert slow["verdict"] == "KILL"
    assert slow["over_the_cap"] or slow["over_the_hard_stop"]
    # and an unstarted leg is priced at the worst rate SEEN, not at its cheaper registered bound
    assert slow["legs"][-1]["seconds_per_call_used"] >= 60.0


# --- rung 5, the liveness loop ---------------------------------------------------------------------


class Ticker:
    """A clock the test advances by hand, so no test sleeps and no deadline is wall-clock."""

    def __init__(self):
        self.at = 0.0

    def __call__(self):
        return self.at

    def sleep(self, seconds):
        self.at += seconds


def test_the_watch_loop_KILLS_a_pod_whose_out_file_has_stopped_growing(run, tmp_path):
    assert opened(run) == gate.GO
    where = tmp_path / "out"
    log = tmp_path / "pod.log"
    pack = small(DEV)
    answered(where, pack["legs"][0], 2, 5.0)
    log.write_text("boot\nready\n", encoding="utf-8")
    tick = Ticker()
    killed = []
    verdict = gate.watch(
        RECORD,
        run.run_state(),
        [pack],
        where=where,
        log=log,
        pull=lambda: None,
        kill=lambda: killed.append("deleted") or {"returncode": 0},
        sleep=tick.sleep,
        clock_now=tick,
        now=at(900),
        poll_seconds=30.0,
    )
    assert verdict["verdict"] == "KILL"
    assert "no new row and no new log line" in verdict["cause"]
    assert verdict["idle_seconds"] >= RECORD["kill_clock"][4]["rule"].count("") * 0  # sanity
    assert verdict["idle_seconds"] >= 600
    assert killed == ["deleted"], "the rung DELETES the pod, it does not merely say so"


def test_the_watch_arms_rung_3_itself_and_does_not_re_arm_it_for_the_shot(run, tmp_path):
    """A pod that answers NOTHING inside the boot ceiling is killed by the loop the executor is
    already inside — so rung 3 does not need hand-polling, which is the habit rung 5 was bought to
    remove. And it is armed ONCE per pod: the shot is a second launch on a model already loaded, so
    a create-anchored ceiling re-armed there would kill a healthy pod on its way to the bar."""
    assert opened(run) == gate.GO
    where, log = tmp_path / "out", tmp_path / "pod.log"
    log.write_text("boot\n", encoding="utf-8")
    launch_stamp(where, 5)  # the pod stamped its own launch and --watch pulled it back
    pack = small(DEV)
    tick, killed = Ticker(), []

    def watch(now_at):
        return gate.watch(
            RECORD,
            run.run_state(),
            [pack],
            where=where,
            log=log,
            pull=lambda: None,
            kill=lambda: killed.append("deleted") or {"returncode": 0},
            sleep=tick.sleep,
            clock_now=tick,
            now=at(now_at),
            poll_seconds=30.0,
        )

    verdict = watch(5 + CEILING + 1)  # 451 s since the runner launched, not one reply
    assert verdict["verdict"] == "KILL" and verdict["cause"].startswith("rung 3")
    assert "since the runner's own launch" in verdict["cause"]
    assert verdict["boot_ceiling_armed"] is True
    assert verdict["seconds_since_launch"] == CEILING + 1
    assert killed == ["deleted"]

    # once rung 3 has gone GO on this pod the ceiling is NOT re-armed: the same state, an hour in,
    # dies on the liveness rung instead — which is the correct rung for a pod that has stopped
    answered(where, pack["legs"][0], 1, 5.0, elapsed0=295.0)
    assert run.main(["--boot", "--outdir", str(where)], now=at(310)) == gate.GO
    killed.clear()
    later = watch(3600)
    assert later["boot_ceiling_armed"] is False
    assert later["verdict"] == "KILL" and later["cause"].startswith("rung 5")


def test_the_watch_kills_on_the_create_anchored_BACKSTOP_when_no_stamp_ever_arrives(run, tmp_path):
    """The launch stamp is a file on a pod that may never have got as far as writing one.

    With no anchor the loop has only the backstop, and the backstop is what has to fire — otherwise
    a pod that dies during staging is watched by nothing until the liveness deadline, and rung 3
    would be a rung that only ever fires when the transport already worked.
    """
    assert opened(run) == gate.GO
    where, log = tmp_path / "out", tmp_path / "pod.log"
    log.write_text("boot\n", encoding="utf-8")
    tick, killed = Ticker(), []
    verdict = gate.watch(
        RECORD,
        run.run_state(),
        [small(DEV)],
        where=where,
        log=log,
        pull=lambda: None,
        kill=lambda: killed.append("deleted") or {"returncode": 0},
        sleep=tick.sleep,
        clock_now=tick,
        now=at(BACKSTOP + 1),
        poll_seconds=30.0,
    )
    assert verdict["verdict"] == "KILL" and verdict["cause"].startswith("rung 3's create-anchored")
    assert verdict["launched_at"] is None
    assert "no launch stamp has been copied back at all" in verdict["cause"]
    assert killed == ["deleted"]


def test_a_FLAPPING_copy_does_not_keep_a_dead_pod_alive(run, tmp_path):
    """The asymmetry, driven. `pull` is scp and scp fails; a failed copy leaves the local file
    SHORTER, and a deadline that refreshed on any change would read N → 0 → N → 0 as four events and
    never expire. The pod in this test has stopped working and the link is flapping — which is the
    exact state rung 5 was bought for, and it must still die on schedule."""
    assert opened(run) == gate.GO
    where = tmp_path / "out"
    log = tmp_path / "pod.log"
    pack = small(DEV)
    tick = Ticker()
    killed = []
    state = {"n": 0}

    def pull():
        state["n"] += 1
        if state["n"] % 2:
            answered(where, pack["legs"][0], 2, 5.0)  # the same two rows, over and over
            log.write_text("boot\nready\n", encoding="utf-8")
        else:
            answered(where, pack["legs"][0], 0, 5.0)  # the copy failed: a truncated local file
            log.write_text("", encoding="utf-8")

    verdict = gate.watch(
        RECORD,
        run.run_state(),
        [pack],
        where=where,
        log=log,
        pull=pull,
        kill=lambda: killed.append("deleted") or {"returncode": 0},
        sleep=tick.sleep,
        clock_now=tick,
        now=at(900),
        poll_seconds=30.0,
    )
    assert verdict["verdict"] == "KILL"
    assert verdict["cause"].startswith("rung 5")
    assert verdict["idle_seconds"] >= 600
    assert killed == ["deleted"]
    # the high-water mark held: the loop never counted the truncated copy as progress
    assert verdict["answered"] == 2


def test_the_watch_loop_returns_GO_when_every_unit_is_answered_and_never_kills_a_working_pod(
    run, tmp_path
):
    assert opened(run) == gate.GO
    where = tmp_path / "out"
    log = tmp_path / "pod.log"
    pack = small(DEV, per_leg=4)
    tick = Ticker()
    killed = []
    state = {"n": 0}

    def pull():
        """A pod that answers one more unit every poll — the positive control."""
        state["n"] += 1
        done = state["n"]
        answered(where, pack["legs"][0], min(done, 4), 5.0)
        if done > 4:
            answered(where, pack["legs"][1], min(done - 4, 4), 7.0)
        log.write_text("\n".join(f"line {one}" for one in range(done)) + "\n", encoding="utf-8")

    verdict = gate.watch(
        RECORD,
        run.run_state(),
        [pack],
        where=where,
        log=log,
        pull=pull,
        kill=lambda: killed.append("deleted"),
        sleep=tick.sleep,
        clock_now=tick,
        now=at(900),
        poll_seconds=30.0,
    )
    assert verdict["verdict"] == "GO"
    assert verdict["answered"] == verdict["owed"] == 8
    assert killed == []


def test_the_watch_loop_kills_on_the_projection_from_INSIDE_the_loop(run, tmp_path):
    assert opened(run) == gate.GO
    where = tmp_path / "out"
    log = tmp_path / "pod.log"
    pack = {**DEV, "legs": [{**leg, "items": leg["items"][:30]} for leg in DEV["legs"]]}
    tick = Ticker()
    killed = []
    state = {"n": 0}

    def pull():
        state["n"] += 1
        answered(where, pack["legs"][0], min(state["n"], 30), 90.0)  # every call is glacial
        log.write_text(
            "\n".join(f"line {one}" for one in range(state["n"])) + "\n", encoding="utf-8"
        )

    verdict = gate.watch(
        RECORD,
        run.run_state(),
        [pack, SHOT],
        where=where,
        log=log,
        pull=pull,
        kill=lambda: killed.append("deleted") or {"returncode": 0},
        sleep=tick.sleep,
        clock_now=tick,
        now=at(900),
        poll_seconds=1.0,
    )
    assert verdict["verdict"] == "KILL"
    assert verdict["cause"].startswith("rung 4")
    assert verdict["projection"]["verdict"] == "KILL"
    assert killed == ["deleted"]


def test_a_watch_that_ENDS_leaves_a_record_and_an_instruction_and_re_raises(run, tmp_path, capsys):
    assert opened(run) == gate.GO
    boom = RuntimeError("the ssh pipe went away")

    def explode(*args, **kwargs):
        raise boom

    original = gate.watch
    gate.watch = explode
    try:
        with pytest.raises(RuntimeError, match="ssh pipe"):
            run.main(
                [
                    "--watch",
                    "--pack",
                    str(REPO_ROOT / packs.DEV_NAME),
                    "--ssh",
                    "root@nowhere",
                    "--ssh-port",
                    "1",
                    "--outdir",
                    str(tmp_path),
                ]
            )
    finally:
        gate.watch = original
    printed = capsys.readouterr().out
    assert "STILL BILLING" in printed and "runpodctl pod delete pod-1" in printed
    last = json.loads(run.RECORD.read_text("utf-8"))["gates"][-1]
    assert last["kind"] == "watch-ended" and last["verdict"] == "KILL"
    assert "pod-1" in last["next_step"]


# --- rung 7, the dev gate --------------------------------------------------------------------------


def dev_files(where: Path, pack: dict, base_answers: dict, v2_answers: dict) -> None:
    for name, answers in (("base", base_answers), ("v2", v2_answers)):
        leg = next(one for one in pack["legs"] if one["name"] == name)
        rows = []
        for item in leg["items"]:
            said = answers.get(item["id"], "не_наш_рынок")
            rows.append(
                {
                    "id": item["id"],
                    "rendering_sha256": item["rendering_sha256"],
                    "reply": json.dumps(
                        {
                            "msg_id": int(item["msg_id"]),
                            "subject_type": said,
                            "subject_id": None,
                            "stance": None,
                        },
                        ensure_ascii=False,
                    ),
                    "balanced": True,
                    "seconds": 5.0,
                }
            )
        where.mkdir(parents=True, exist_ok=True)
        (where / leg["out"]).write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
        )


def truth() -> dict:
    labels = gate.labels()
    leg = next(one for one in DEV["legs"] if one["name"] == "base")
    return {item["id"]: labels[(item["thread"], int(item["msg_id"]))] for item in leg["items"]}


def test_the_dev_gate_needs_BOTH_inequalities_and_calls_a_shortfall_RED(run, tmp_path):
    assert opened(run) == gate.GO
    where = tmp_path / "out"
    gold = truth()
    our = {name: value for name, value in gold.items() if value in packs.OUR}
    assert len(our) == 49

    # v2 answers every «our» row correctly and the base answers none of them: delta 49 ≥ 10,
    # and v2's overall agreement is 49 above the base's, so both inequalities hold
    dev_files(where, DEV, {}, gold)
    green = gate.dev_gate(RECORD, run.run_state(), DEV, where, now=at(3000))
    assert green["verdict"] == "GO"
    assert green["our_delta"] == 49 and green["our_delta_passed"]
    assert green["agreement_delta_passed"]

    # the same «our» gain of 49, bought by breaking 55 rows the base had right: 49 - 55 = -6,
    # past the −5 the second inequality allows. The FIRST holds, and the gate is RED on the other
    # one alone — which is the whole reason there are two of them
    spoiled = dict(gold)
    for name in [one for one, value in gold.items() if value not in packs.OUR][:55]:
        spoiled[name] = "молочный_бренд"
    dev_files(
        where, DEV, {name: value for name, value in gold.items() if value not in packs.OUR}, spoiled
    )
    red = gate.dev_gate(RECORD, run.run_state(), DEV, where, now=at(3000))
    assert red["base"]["agreed"] == 151 and red["base"]["our_agreed"] == 0
    assert red["v2"]["agreed"] == 145 and red["v2"]["our_agreed"] == 49
    assert red["our_delta"] == 49 and red["agreement_delta"] == -6
    assert red["our_delta_passed"] and not red["agreement_delta_passed"]
    assert red["verdict"] == "RED"
    assert "NOT spent" in red["next_step"]


def test_an_unreachable_delta_is_a_STOP_the_registration_named_and_not_a_RED(run, tmp_path):
    """The base's dev number is measured on a billed pod. If it comes back above 39 the +10 delta
    cannot exist for ANY v2, and that branch has to be registered before the money starts."""
    assert opened(run) == gate.GO
    where = tmp_path / "out"
    gold = truth()
    almost = dict(gold)
    for name in [one for one, value in gold.items() if value in packs.OUR][:9]:
        almost[name] = "не_наш_рынок"  # the base gets 40 of the 49 «our» rows right
    dev_files(where, DEV, almost, gold)
    stopped = gate.dev_gate(RECORD, run.run_state(), DEV, where, now=at(3000))
    assert stopped["base"]["our_agreed"] == 40
    assert stopped["reachability"]["reachable"] is False
    assert stopped["reachability"]["highest_base_that_leaves_the_delta_reachable"] == 39
    assert stopped["verdict"] == "STOP"


def test_a_refusal_counts_as_a_disagreement_and_is_named_by_cause(run, tmp_path):
    assert opened(run) == gate.GO
    where = tmp_path / "out"
    gold = truth()
    dev_files(where, DEV, gold, gold)
    leg = next(one for one in DEV["legs"] if one["name"] == "v2")
    path = where / leg["out"]
    lines = path.read_text("utf-8").splitlines()
    broken = json.loads(lines[0])
    broken["reply"] = "I am not going to answer that."
    lines[0] = json.dumps(broken, ensure_ascii=False)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    table = gate.leg_table(RECORD, DEV, "v2", where)
    assert len(table["refused"]) == 1
    assert table["answered"] == 199
    assert (
        table["absent"] == 1
    )  # the row was asked and has no readable answer: a miss, not an exempt
    assert table["agreed"] == 199


def test_a_reply_whose_request_sha_is_not_the_packs_is_refused(run, tmp_path):
    assert opened(run) == gate.GO
    where = tmp_path / "out"
    dev_files(where, DEV, truth(), truth())
    leg = next(one for one in DEV["legs"] if one["name"] == "base")
    path = where / leg["out"]
    lines = path.read_text("utf-8").splitlines()
    row = json.loads(lines[0])
    row["rendering_sha256"] = "0" * 64
    lines[0] = json.dumps(row, ensure_ascii=False)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="not the pack's"):
        gate.leg_table(RECORD, DEV, "base", where)


# --- the registration is the law -------------------------------------------------------------------


def test_every_threshold_the_gate_acts_on_is_READ_out_of_the_registration():
    assert gate.first_number(gate.rung(RECORD, 2)["rule"]) == 500
    assert gate.first_number(gate.rung(RECORD, 3)["rule"]) == 450
    assert float(gate.rung(RECORD, 3)["backstop_seconds"]) == 1100
    assert gate.first_number(gate.rung(RECORD, 5)["rule"]) == 600
    assert gate.first_number(gate.rung(RECORD, 6)["rule"]) == 6100
    assert gate.tolerance(RECORD) == 60.0
    assert RECORD["bars"]["dev_gate"]["our_delta_minimum"] == 10
    assert RECORD["bars"]["dev_gate"]["agreement_delta_minimum"] == -5
    assert RECORD["bars"]["P1_per_comment_agreement"]["minimum_agreed"] == 12
    assert RECORD["money"]["cap_usd_all_in"] == 1.38
    assert RECORD["money"]["meter"]["price_ceiling_usd_per_hour"] == 0.80
    # rung 3's rule carries TWO numbers now, and `first_number` reads positionally: the ceiling has
    # to be the first one in the sentence, or a reordered clause silently makes 1 100 the ceiling
    assert gate.first_number(gate.rung(RECORD, 3)["rule"]) != 1100
    # the gate types none of them: no threshold appears as a literal in its source
    source = (REPO_ROOT / "scripts" / "gate_pass1_fewshot.py").read_text("utf-8")
    for value in (
        "180",
        "500",
        "450",
        "1100",
        "600",
        "6100",
        "6300",
        "1.38",
        "1.50",
        "0.80",
        "60.0",
    ):
        assert f"= {value}" not in source, value


def test_the_registration_is_refused_when_it_is_not_committed(tmp_path, monkeypatch):
    monkeypatch.setattr(gate, "PREREG", tmp_path / "untracked.json")
    (tmp_path / "untracked.json").write_text("{}", encoding="utf-8")
    with pytest.raises(SystemExit, match="not tracked by git"):
        gate.registration()


def test_the_gate_and_the_registration_agree_about_the_leg_names_and_their_files():
    registered = {one["name"]: one["out"] for one in RECORD["population"]["dev"]["legs"]}
    assert registered == packs.DEV_LEGS
    assert RECORD["population"]["shot"]["out"] == packs.SHOT_LEG["shot"]
    assert set(RECORD["money"]["arithmetic"]["seconds_per_call"]) >= {"base", "v2", "shot"}
    assert set(RECORD["instruments"]["prompt_sha256"]) == set(prompts.PASS1)
