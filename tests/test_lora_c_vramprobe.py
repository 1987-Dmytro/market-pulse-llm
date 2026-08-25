"""The vramprobe's rungs, DRIVEN — every outcome, at $0 and with no pod.

`results/prereg_lora_c_vramprobe.json` is hand-written: ~40 constants and two formulas, with no
generator. This file is what stops it drifting. It does three jobs:

* **every registered threshold is greppable back into `docs/PROMPT-lora-c-vramprobe.md`** — the
  contract is where those numbers came from, and a registration free to hold a different one is a
  plan nobody agreed to ([[preregistration_is_a_file_not_a_constant]]);
* **every rung fires, both ways**, including the two the r2 gate could not answer: the hard stop
  re-solved at the observed price, and a smoke whose verdict is READ out of the pod's log rather
  than asserted by its caller ([[guard_selftest_negative_control]]);
* **the frozen registration is untouched.** `results/prereg_lora_c.json` is an INPUT to this probe —
  `scripts/train_qlora_v3.py` reads its dataset sha list — and its sha is pinned here.
"""

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import gate_lora_c as parent  # noqa: E402
import gate_lora_c_vramprobe as gate  # noqa: E402

PREREG = json.loads((REPO_ROOT / "results" / "prereg_lora_c_vramprobe.json").read_text("utf-8"))
CONTRACT = " ".join((REPO_ROOT / "docs" / "PROMPT-lora-c-vramprobe.md").read_text("utf-8").split())
"""Whitespace-normalised: the contract wraps «the smoke = 6 optimizer\nsteps» across a line, and a
raw grep for a quotation that the source hyphenates or wraps finds nothing and says «absent»
([[verbatim_quotes_must_be_grepped]])."""
CREATE = "2026-08-25T15:00:00+00:00"


def at(seconds: float, created: str = CREATE) -> datetime:
    return gate.stamp(created) + timedelta(seconds=seconds)


def a_pod(created: str = CREATE, usd_per_hour: float = 0.72) -> dict:
    return {"pods": [{"pod_id": "probe-1", "created_at": created, "usd_per_hour": usd_per_hour}]}


@pytest.fixture
def run(tmp_path, monkeypatch):
    """The probe's record redirected into `tmp_path`, the registration handed over directly.

    `gate.RECORD` and not `parent.RECORD`: the contextmanager copies THIS module's globals into the
    parent's on every call, so patching the parent's would be undone a microsecond later and the
    test would write into `results/`.
    """
    monkeypatch.setattr(gate, "RECORD", tmp_path / "lora_c_vramprobe.json")
    monkeypatch.setattr(parent, "registration", lambda: parent.as_the_sibling_reads_it(PREREG))
    return gate


def view() -> dict:
    return parent.as_the_sibling_reads_it(PREREG)


def backstop_for(created: str = CREATE) -> str:
    left = PREREG["money"]["pre_pod_arithmetic"]["hard_stop_seconds"]
    return (gate.stamp(created) + timedelta(seconds=left)).isoformat(timespec="seconds")


def opened(run, *, usd_per_hour=0.72, card="RTX PRO 4500", created=CREATE):
    return run.main(
        [
            "--open",
            "--pod-id",
            "probe-1",
            "--created-at",
            created,
            "--usd-per-hour",
            str(usd_per_hour),
            "--card",
            card,
            "--terminate-after",
            backstop_for(created),
        ],
        now=at(1, created),
    )


# --- the registration is the contract's ----------------------------------------------------------


def test_every_registered_threshold_is_the_first_number_of_its_own_rule():
    for entry in PREREG["kill_clock"]:
        assert gate.first_number(entry["rule"]) == pytest.approx(entry["threshold"]), entry["rung"]


def test_every_registered_threshold_is_greppable_in_the_contract():
    """The numbers came out of `docs/PROMPT-lora-c-vramprobe.md`; each must still be findable there.

    Written as the digits the contract prints, not as a float: the contract says «6 × 181.5 s» and
    «cap $0.30», and a registration free to say 181.6 would be a plan nobody agreed to.
    """
    spelled = {
        0.80: "0.80",
        500.0: "500 s",
        600.0: "600 s",
        181.5: "181.5",
        1500.0: "1 500 s",
        1.0: "one pod",
    }
    for entry in PREREG["kill_clock"]:
        assert spelled[entry["threshold"]] in CONTRACT, entry["rung"]
    assert "cap $0.30" in CONTRACT
    assert str(PREREG["money"]["cap_usd_all_in"]) == "0.3"
    assert "6 optimizer steps" in CONTRACT
    assert gate.rung(PREREG, 3)["steps"] == 6
    assert "load 300 s" in CONTRACT
    assert gate.rung(PREREG, 3)["load_allowance_seconds"] == 300.0


def test_the_env_var_the_registration_names_is_the_contracts():
    assert PREREG["instrument"]["env"] in CONTRACT
    assert PREREG["instrument"]["env"] in PREREG["instrument"]["command"]


def test_the_frozen_lora_c_registration_is_an_input_and_is_unchanged():
    """The probe reads it and never writes it — `train_qlora_v3` needs its dataset sha list."""
    frozen = REPO_ROOT / "results" / "prereg_lora_c.json"
    digest = hashlib.sha256(frozen.read_bytes()).hexdigest()
    assert digest == PREREG["this_is_not_the_registered_attempt"]["sha256"]


def test_log_every_matches_the_config_the_probe_will_actually_run():
    """The two-lines-not-six finding rests on this number; a config revision must break this test."""
    config = (REPO_ROOT / "config" / "qlora.yaml").read_text("utf-8")
    assert f"log_every: {gate.rung(PREREG, 3)['log_every']}" in config
    assert "micro_batch_size: 2" in config
    assert "max_seq_len: 3072" in config


# --- rung 3's arithmetic -------------------------------------------------------------------------


def test_six_steps_at_log_every_five_write_two_loss_lines_not_six():
    """The reason this rung is written here at all: the r2 gate waits for six of them."""
    assert gate.expected_log_steps(6, 5) == [5, 6]
    assert gate.expected_log_steps(6, 1) == [1, 2, 3, 4, 5, 6]


def test_the_cap_binds_and_the_registered_ceiling_does_not_on_any_real_pod():
    """Below the crossover the 181.5 ceiling binds; above it the $0.30 cap does, and it always is.

    The registration computes the crossover at s = 21.0 s. The paired pod's ssh answered at 23.2 s
    and staging a 14 MB bundle takes longer than nothing, so the ceiling can never fire
    ([[an_absolute_bar_needs_a_reachability_state]]).
    """
    cross = PREREG["reachability"]["s_at_which_the_two_bounds_cross_seconds"]
    pod = a_pod()["pods"][0]
    early = gate.budget(view(), pod, at(cross - 5).isoformat())
    late = gate.budget(view(), pod, at(cross + 5).isoformat())
    assert early["what_binds"] == "the registered 181.5 ceiling"
    assert early["binding_seconds_per_step"] == 181.5
    assert late["what_binds"] == "the $0.30 cap"
    assert late["binding_seconds_per_step"] < 181.5
    real = gate.budget(view(), pod, at(200).isoformat())
    assert real["binding_seconds_per_step"] == pytest.approx((1110 - 200) / 6, abs=0.01)


def test_every_registered_price_column_solves_to_the_registered_hard_stop():
    """The anti-drift property of a hand-written record: the two literals still follow from each."""
    block = PREREG["money"]["pre_pod_arithmetic"]
    for price, column in block["at_each_price"].items():
        assert float(price) == column["usd_per_hour"]
        solved = PREREG["money"]["cap_usd_all_in"] / float(price) * 3600
        assert solved == pytest.approx(block["hard_stop_seconds"], abs=1.0)
        assert solved == pytest.approx(column["hard_stop_seconds"], abs=1.0)


def test_the_hard_stop_is_re_solved_at_the_price_the_create_returned():
    solved = gate.the_hard_stop_is_solved_at_the_observed_price(view(), 0.72)
    assert solved["hard_stop_solved_seconds"] == 1500.0
    assert solved["drift_seconds"] == 0.0
    with pytest.raises(SystemExit, match="1367"):
        gate.the_hard_stop_is_solved_at_the_observed_price(view(), 0.79)


# --- rung 3's five outcomes, each on a reading ---------------------------------------------------


def smoke(tmp_path, *, log="", loss=None, provenance=None, environ=None, seconds=400.0):
    files = {}
    for name, body in (
        ("log", log),
        ("environ", environ),
    ):
        if body is not None:
            path = tmp_path / f"{name}.txt"
            path.write_text(body, encoding="utf-8")
            files[name] = path
    if loss is not None:
        path = tmp_path / "loss.jsonl"
        path.write_text("".join(json.dumps(one) + "\n" for one in loss), encoding="utf-8")
        files["loss"] = path
    if provenance is not None:
        path = tmp_path / "provenance.json"
        path.write_text(json.dumps(provenance), encoding="utf-8")
        files["provenance"] = path
    started = at(200).isoformat()
    return gate.smoke_gate(
        view(),
        a_pod(),
        started,
        files["log"],
        files.get("loss"),
        files.get("provenance"),
        files.get("environ"),
        now=at(200 + seconds),
    )


def test_an_out_of_memory_in_the_log_is_read_not_asserted(tmp_path):
    gate_out = smoke(tmp_path, log="OOM: micro_batch -> 1\ntorch.OutOfMemoryError: CUDA out of\n")
    assert gate_out["verdict"] == "KILL"
    assert gate_out["answer"]["outcome"] == "OOM"
    assert gate_out["the_trainers_own_halving_fired"] is True


def test_a_traceback_that_is_not_an_oom_is_its_own_outcome(tmp_path):
    gate_out = smoke(tmp_path, log="Traceback (most recent call last):\nRuntimeError: bnb\n")
    assert gate_out["verdict"] == "KILL"
    assert gate_out["answer"]["outcome"] == "OTHER"


def test_six_logged_steps_and_a_provenance_file_are_SURVIVED(tmp_path):
    rows = [
        {"step": 5, "seconds_per_step": 70.0, "gpu_gb": 29.1},
        {"step": 6, "seconds_per_step": 14.0, "gpu_gb": 29.4},
    ]
    gate_out = smoke(
        tmp_path,
        log="{'step': 6}\n",
        loss=rows,
        provenance={"run": {"steps": 6, "seconds_per_step": 71.5, "gpu_gb_peak": 29.4}},
        environ="PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True\n",
        seconds=740.0,
    )
    assert gate_out["verdict"] == "GO"
    assert gate_out["answer"]["outcome"] == "SURVIVED"
    assert gate_out["answer"]["the_env_var_reached_the_training_process"] is True
    assert gate_out["answer"]["seconds_per_step_whole_loop"] == 71.5
    assert gate_out["answer"]["seconds_per_step_step_5_line"] == 70.0


def test_the_step_6_line_is_never_averaged_into_the_reported_rate(tmp_path):
    """14.0 is one step's time over five; the reported number is the whole loop's, unmixed."""
    rows = [
        {"step": 5, "seconds_per_step": 70.0},
        {"step": 6, "seconds_per_step": 14.0},
    ]
    answer = smoke(
        tmp_path,
        log="",
        loss=rows,
        provenance={"run": {"steps": 6, "seconds_per_step": 71.5}},
        seconds=740.0,
    )["answer"]
    assert answer["seconds_per_step_whole_loop"] != pytest.approx((70.0 + 14.0) / 2)
    assert "one step's time divided by five" in answer["the_two_rates_are_not_averaged"]


def test_the_clock_kills_a_run_that_is_alive_but_too_slow(tmp_path):
    """Step 5 landed, step 6 is late — the memory question is answered, the rate is not bought."""
    rows = [{"step": 5, "seconds_per_step": 200.0}]
    gate_out = smoke(tmp_path, log="", loss=rows, seconds=1400.0)
    assert gate_out["verdict"] == "KILL"
    assert gate_out["answer"]["outcome"] == "SURVIVED_NO_RATE"
    assert gate_out["answer"]["optimizer_steps_logged"] == 5


def test_the_clock_before_the_first_loss_line_resolves_nothing(tmp_path):
    gate_out = smoke(tmp_path, log="", seconds=1400.0)
    assert gate_out["verdict"] == "KILL"
    assert gate_out["answer"]["outcome"] == "UNRESOLVED"
    assert "NOT answered" in gate_out["answer"]["what_it_means"]


def test_a_smoke_still_inside_its_deadline_WAITs(tmp_path):
    gate_out = smoke(tmp_path, log="Loading weights: 40%\n", seconds=250.0)
    assert gate_out["verdict"] == "WAIT"
    assert gate_out["answer"]["outcome"] is None


def test_an_absent_environ_proof_is_reported_as_absent_not_assumed(tmp_path):
    answer = smoke(
        tmp_path,
        log="",
        provenance={"run": {"steps": 6, "seconds_per_step": 71.5}},
        seconds=740.0,
    )["answer"]
    assert answer["the_env_var_reached_the_training_process"] is False
    assert answer["environ_proof"] is None


def test_a_shell_that_exported_a_DIFFERENT_value_does_not_pass_as_proof(tmp_path):
    answer = smoke(
        tmp_path,
        log="",
        provenance={"run": {"steps": 6}},
        environ="PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128\n",
        seconds=740.0,
    )["answer"]
    assert answer["the_env_var_reached_the_training_process"] is False


# --- the rungs the parent owns, driven THROUGH this module ---------------------------------------


def test_rung_0_takes_the_registered_card_and_price_and_refuses_the_others(run):
    assert opened(run) == gate.GO
    state = json.loads(run.RECORD.read_text("utf-8"))
    assert state["gates"][-1]["verdict"] == "GO"
    assert state["gates"][-1]["card_is_authorised"] is True


def test_rung_0_refuses_the_4090_the_r2_contract_pre_authorised(run):
    """24 GB cannot answer a question about 32 GB, so this probe carries no fallback card."""
    assert opened(run, usd_per_hour=0.74, card="RTX 4090") == gate.KILL


def test_rung_0_refuses_a_price_with_no_column_even_a_cheaper_one(run):
    """$0.53 is the A6000's price today. Cheaper is not the same as planned for."""
    assert opened(run, usd_per_hour=0.53) == gate.KILL


def test_rung_1_waits_then_kills_then_goes(run):
    opened(run)
    assert run.main(["--gate0"], now=at(100)) == gate.WAIT
    assert run.main(["--gate0", "--ssh-ok"], now=at(100)) == gate.GO
    assert run.main(["--gate0"], now=at(501)) == gate.KILL


def test_rung_2_measures_silence_from_the_last_log_line(run):
    opened(run)
    quiet = at(100).isoformat()
    assert run.main(["--liveness", "--last-event", quiet], now=at(200)) == gate.GO
    assert run.main(["--liveness", "--last-event", quiet], now=at(750)) == gate.KILL


def test_close_pod_prices_the_pod_on_its_own_clock(run):
    opened(run)
    assert run.main(["--close-pod", "--deleted-at", at(900).isoformat(), "--outcome", "done"]) == (
        gate.GO
    )
    pod = json.loads(run.RECORD.read_text("utf-8"))["pods"][-1]
    assert pod["billed_seconds"] == 900.0
    assert pod["billed_usd"] == pytest.approx(900 * 0.72 / 3600, abs=1e-6)
    assert pod["billed_usd"] < PREREG["money"]["cap_usd_all_in"]


def test_rung_7_refuses_a_second_pod_while_one_is_open(run):
    opened(run)
    assert run.main(["--pre-create-check"]) == gate.KILL


def test_the_gate_is_driven_end_to_end_as_a_command():
    """The entry point's preamble is untested code until something runs it as a COMMAND.

    Either answer is a pass: the rung's, or the registration guard's refusal while the record is
    uncommitted. A crash is not ([[the_entry_points_preamble_is_untested_code]]).
    """
    got = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "gate_lora_c_vramprobe.py"),
            "--pre-create-check",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={"PYTHONPATH": "src", "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"},
    )
    assert got.returncode in (gate.GO, gate.KILL, 1), got.stderr
    assert "Traceback" not in got.stderr


def test_the_probe_leaves_lora_c_s_own_gates_reading_lora_c(run):
    """The contextmanager's `finally` — line C's files must still be line C's after a probe call."""
    before = (parent.PHASE, parent.PREREG, parent.RECORD)
    with gate.the_gate_reads_the_probe():
        assert parent.PREREG == gate.PREREG
    assert (parent.PHASE, parent.PREREG, parent.RECORD) == before
