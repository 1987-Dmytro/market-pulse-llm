"""pass1-fewshot's Mac-side clock, DRIVEN — every rung, both verdicts, at $0 and with no pod.

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

RECORD = json.loads((REPO_ROOT / "results" / "prereg_pass1_fewshot.json").read_text("utf-8"))
DEV = json.loads((REPO_ROOT / packs.DEV_NAME).read_text("utf-8"))
SHOT = json.loads((REPO_ROOT / packs.SHOT_NAME).read_text("utf-8"))
LABELS = None
CREATE = "2026-08-21T09:00:00+00:00"


def at(seconds: float, created: str = CREATE):
    return gate.stamp(created) + timedelta(seconds=seconds)


@pytest.fixture
def run(tmp_path, monkeypatch):
    monkeypatch.setattr(gate, "RECORD", tmp_path / "pass1_fewshot_run.json")
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
    assert opened(run) == gate.GO
    closed_at = at(1200).isoformat(timespec="seconds")
    assert run.main(
        ["--close", "--deleted-at", closed_at, "--outcome", "rung 5"], now=at(1201)
    ) == (gate.GO)
    second = "2026-08-21T10:00:00+00:00"
    assert opened(run, created=second, pod_id="pod-2") == gate.GO
    state = json.loads(run.RECORD.read_text("utf-8"))
    window = gate.stamp(state["pods"][1]["terminate_after_computed"]) - gate.stamp(second)
    stop = RECORD["money"]["arithmetic"]["cumulative"]["hard_stop_seconds"]
    assert window.total_seconds() == stop - 1200


def test_pre_create_check_refuses_a_second_billing_endpoint(run):
    assert run.main(["--pre-create-check"]) == gate.GO
    assert opened(run) == gate.GO
    assert run.main(["--pre-create-check"]) == gate.KILL


# --- rungs 2 and 3 ---------------------------------------------------------------------------------


def test_the_ssh_dead_man_waits_then_kills_and_goes_when_the_endpoint_answers(run):
    assert opened(run) == gate.GO
    assert run.main(["--gate0"], now=at(60)) == gate.WAIT
    assert run.main(["--gate0", "--ssh-ok"], now=at(60)) == gate.GO
    assert run.main(["--gate0"], now=at(181)) == gate.KILL


def test_the_boot_gate_has_three_outcomes_and_measures_to_the_first_REPLY(run):
    assert opened(run) == gate.GO
    assert run.main(["--boot"], now=at(200)) == gate.WAIT
    assert (
        run.main(["--boot", "--first-reply-at", at(300).isoformat(timespec="seconds")], now=at(310))
        == gate.GO
    )
    assert run.main(["--boot"], now=at(451)) == gate.KILL
    # a reply that lands AFTER the ceiling is a KILL even though a reply exists
    assert (
        run.main(["--boot", "--first-reply-at", at(460).isoformat(timespec="seconds")], now=at(470))
        == gate.KILL
    )


# --- rung 4, the projection ------------------------------------------------------------------------


def answered(where: Path, leg: dict, n: int, seconds: float) -> None:
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
        }
        for item in leg["items"][:n]
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

    verdict = watch(500)  # 500 s of create-elapsed, not one reply
    assert verdict["verdict"] == "KILL" and verdict["cause"].startswith("rung 3")
    assert verdict["boot_ceiling_armed"] is True
    assert killed == ["deleted"]

    # once rung 3 has gone GO on this pod the ceiling is NOT re-armed: the same state, an hour in,
    # dies on the liveness rung instead — which is the correct rung for a pod that has stopped
    assert (
        run.main(["--boot", "--first-reply-at", at(300).isoformat(timespec="seconds")], now=at(310))
        == gate.GO
    )
    killed.clear()
    later = watch(3600)
    assert later["boot_ceiling_armed"] is False
    assert later["verdict"] == "KILL" and later["cause"].startswith("rung 5")


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
    assert gate.first_number(gate.rung(RECORD, 2)["rule"]) == 180
    assert gate.first_number(gate.rung(RECORD, 3)["rule"]) == 450
    assert gate.first_number(gate.rung(RECORD, 5)["rule"]) == 600
    assert gate.first_number(gate.rung(RECORD, 6)["rule"]) == 6300
    assert RECORD["bars"]["dev_gate"]["our_delta_minimum"] == 10
    assert RECORD["bars"]["dev_gate"]["agreement_delta_minimum"] == -5
    assert RECORD["bars"]["P1_per_comment_agreement"]["minimum_agreed"] == 12
    assert RECORD["money"]["cap_usd_all_in"] == 1.50
    assert RECORD["money"]["meter"]["price_ceiling_usd_per_hour"] == 0.80
    # the gate types none of them: no threshold appears as a literal in its source
    source = (REPO_ROOT / "scripts" / "gate_pass1_fewshot.py").read_text("utf-8")
    for value in ("180", "450", "600", "6300", "1.50", "0.80"):
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
