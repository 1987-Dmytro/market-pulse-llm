"""`results/prereg_pass1_fewshot_r2.json` — the SAME line re-registered, and what «same» has to mean.

Four things carry this record, and each of them is driven rather than asserted in prose.

* **The copied half is r1's, and the producer REFUSES when it stops being.** The question, the bars,
  the packs, the prompt, the holdout, the dev gate, the attempt and its multiplicity are copied out
  of the sealed r1 file, so «byte-identical» is true by construction — and every pin inside them is
  compared to the live file it names, with a bent copy driven through the refusal so the check is
  known to fire ([[guard_selftest_negative_control]]).
* **H6 still refuses.** Every figure `docs/PROMPT-pass1-fewshot-r2.md` prints re-derives, including
  the three the contract states as REASONS rather than numbers: why 500 and not 600, that the
  overhead cut is paid for by the lines that replaced it, and what the 464 copied-back rows are.
* **Rung 3's rule now carries TWO numbers**, and `gate_pass1_fewshot.first_number` reads
  positionally. The ceiling has to be the first number in that sentence, and the backstop has to sit
  in a field of its own — a reordered clause must not be able to make 1 100 the ceiling
  ([[a_gate_that_checks_position_not_presence]]).
* **The recovery clause is reachable, and that is what fixed rung 2 at 500.** One dead pod plus the
  whole worst case fits the hard stop and the cap; at 600 it does not, and the counterfactual is a
  registered row rather than a sentence.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_pass1_fewshot_packs as packs  # noqa: E402
import gate_pass1_fewshot as gate  # noqa: E402
import write_pass1_fewshot_prereg as r1_prereg  # noqa: E402
import write_pass1_fewshot_prereg_r2 as prereg  # noqa: E402
import write_pass1_prereg_b as prereg_b  # noqa: E402

RECORD = json.loads((REPO_ROOT / prereg.OUT_NAME).read_text("utf-8"))
R1 = json.loads((REPO_ROOT / r1_prereg.OUT_NAME).read_text("utf-8"))
RUNG = {one["rung"]: one for one in RECORD["kill_clock"]}
SUMS = RECORD["money"]["arithmetic"]


MOVED_BY_RULING_F = ("instruments.parser.sha256", "instruments.transport.sha256")
"""The two copied pins ruling (ф) moved: `src/market_pulse/prompts.py` (the parser now reads past a
closed thinking channel) and `scripts/pass1_fewshot_pod_runner.py` (the `--serving` switch).

r2 re-registers a line that is already spent, so it is never re-pinned and its producer's copy guard
REFUSES today by name — asserted below. Everything that drives `build()` therefore runs under the
pins the record was SEALED with, which is what keeps those tests about what they are about."""


@pytest.fixture
def sealed_pins():
    """`live_pins()` as it read the day this record was written — the record's own values.

    Set on the module directly rather than through `monkeypatch`: three of the tests below call
    `monkeypatch.undo()` mid-test to prove the unbent producer builds, and an undo that also put
    ruling (ф)'s moved pins back would make the second half of each of them fail for the reason the
    first half is not about.
    """
    keep = prereg.live_pins
    pins = {path: prereg.dig(RECORD, path) for path in keep()}
    prereg.live_pins = lambda: pins
    try:
        yield pins
    finally:
        prereg.live_pins = keep


def test_the_copy_REFUSES_today_and_names_exactly_the_pins_ruling_f_moved():
    """The guard FIRES, and what it names is the list — so a third pin moving cannot pass quietly
    ([[an_enumerated_diff_is_asserted_in_both_directions]])."""
    with pytest.raises(SystemExit, match="no longer describes this checkout") as raised:
        prereg.build()
    named = json.loads(
        str(raised.value).split("checkout: ", 1)[1].rsplit("\nr2 re-registers", 1)[0]
    )
    assert sorted(named) == sorted(MOVED_BY_RULING_F)


def test_the_shipped_r2_registration_is_what_the_producer_writes_today(tmp_path, sealed_pins):
    """Under the pins this record was SEALED with — the two ruling (ф) moved are put back first."""
    assert prereg.main(["--outdir", str(tmp_path)]) == 0
    assert (tmp_path / prereg.OUT_NAME).read_bytes() == (REPO_ROOT / prereg.OUT_NAME).read_bytes()
    assert "generated_at" not in (REPO_ROOT / prereg.OUT_NAME).read_text("utf-8")


# --- the half that must be r1's -------------------------------------------------------------------


def test_every_block_the_contract_freezes_is_r1s_byte_for_byte():
    """The eight blocks, diffed against the sealed record — with the two declared exceptions named."""
    for name in prereg.COPIED:
        if name == "instruments":
            continue
        assert RECORD[name] == R1[name], name
    moved = set(prereg_b.moved_paths(R1["instruments"], RECORD["instruments"], opaque=()))
    assert moved == {
        "gate.sha256",
        "gate.moved_since_r1",
        "gate.rule",
        "scorer_pass1_fewshot",
    }
    # the two exceptions, each for its own registered reason
    assert RECORD["instruments"]["gate"]["sha256"] == packs.summary.sha256_of(prereg.GATE)
    assert RECORD["instruments"]["gate"]["sha256"] != R1["instruments"]["gate"]["sha256"]
    assert RECORD["instruments"]["scorer_pass1_fewshot"]["sha256"] == packs.summary.sha256_of(
        prereg.SCORER
    )
    # and the prompt, the packs and the gold did NOT move: this is the same question
    assert RECORD["instruments"]["prompt_sha256"] == R1["instruments"]["prompt_sha256"]
    assert RECORD["population"]["shot"]["sha256"] == packs.summary.sha256_of(
        REPO_ROOT / packs.SHOT_NAME
    )
    assert RECORD["bars"]["dev_gate"]["our_delta_minimum"] == 10
    assert RECORD["bars"]["P1_per_comment_agreement"]["minimum_agreed"] == 12


def test_the_copy_REFUSES_when_a_copied_pin_stops_describing_this_checkout(
    monkeypatch, sealed_pins
):
    """The negative control. A copied block that no longer matches the live file is a STOP.

    Both directions: bent, the producer refuses and names the path; unbent, it builds. Without this
    the copy would be a way of carrying yesterday's world forward under today's name.
    """
    bent = json.loads(json.dumps(R1))
    bent["population"]["dev"]["sha256"] = "0" * 64
    monkeypatch.setattr(prereg, "sealed_r1", lambda: bent)
    with pytest.raises(SystemExit, match="no longer describes this checkout") as refusal:
        prereg.build()
    assert "population.dev.sha256" in str(refusal.value)
    monkeypatch.undo()
    assert prereg.build()["h6"]["mismatches"] == []


def test_r2_names_what_it_supersedes_and_the_state_r1_closed_in():
    supersedes = RECORD["supersedes"]
    assert supersedes["record"] == r1_prereg.OUT_NAME
    assert supersedes["sha256"] == packs.summary.sha256_of(REPO_ROOT / r1_prereg.OUT_NAME)
    assert supersedes["r1_closing_state"] == (
        "closed at rung 2 twice, attempt NOT spent, recovery used"
    )
    assert supersedes["r1_pods"] == {
        "pods": 2,
        "billed_seconds": 573.0,
        "billed_usd": 0.117783,
    }
    assert RECORD["contract"] == "docs/PROMPT-pass1-fewshot-r2.md"
    assert RECORD["run_record"] == "results/pass1_fewshot_r2_run.json"
    assert RECORD["money"]["reading"]["step"] == "pass1-fewshot-r2"


# --- the four amendments ---------------------------------------------------------------------------


def test_rung_2s_ceiling_is_a_SPREAD_derived_from_the_two_readings_of_the_20th():
    assert gate.first_number(RUNG[2]["rule"]) == 500.0
    readings = SUMS["ssh_readings_2026_08_20"]
    assert sorted(readings.values()) == [231.9, 262.5]
    assert all("juupgp6y77jvuz" in one or "7spsy61lpjumrz" in one for one in readings)
    assert SUMS["ssh_seconds_charged"] >= max(readings.values())
    assert SUMS["ssh_observed_ready"] == {"pass1-probe-b, 2026-08-18, the same card": 14.5}
    assert "LOWER bounds" in SUMS["ssh_rule"]


def test_rung_3_keeps_its_ceiling_and_moves_its_ANCHOR_with_a_backstop_beside_it():
    """The ceiling is r1's 450 s. What r2 changes is the span it is measured over (Dv605)."""
    assert RUNG[3]["anchor"] == "launched_at"
    assert gate.first_number(RUNG[3]["rule"]) == 450.0 == SUMS["boot_seconds_charged"]
    assert RUNG[3]["backstop_seconds"] == 1100.0 == SUMS["pre_generation_seconds"]
    # the backstop is DERIVED, not typed: ssh + stage/launch + load
    assert RUNG[3]["backstop_seconds"] == (
        SUMS["ssh_seconds_charged"]
        + SUMS["stage_launch_seconds_charged"]
        + SUMS["boot_seconds_charged"]
    )
    # `first_number` reads positionally, so the ceiling must be the FIRST number of that sentence
    assert gate.first_number(RUNG[3]["rule"]) != RUNG[3]["backstop_seconds"]
    assert "launched_at" in RUNG[3]["read"]
    assert "450" in RUNG[3]["rule"] and "1100" in RUNG[3]["backstop_rule"]


def test_the_two_pins_r1_could_not_absorb_are_registered_here():
    """Dv606 — the bar named its judge and never pinned it. Dv603 — a gate threshold in the source."""
    assert RECORD["instruments"]["scorer_pass1_fewshot"]["script"] == (
        "scripts/score_pass1_fewshot.py"
    )
    assert SUMS["cumulative"]["backstop_tolerance_seconds"] == 60.0
    assert gate.tolerance(RECORD) == 60.0


def test_the_money_is_re_derived_for_the_new_allowances_and_the_step_sum_holds():
    assert RECORD["money"]["cap_usd_all_in"] == 1.38
    assert SUMS["total_seconds"] == pytest.approx(
        500 + 150 + 450 + SUMS["generation_seconds"] + 1300
    )
    assert SUMS["generation_seconds"] == pytest.approx(1032.4 + 1548.6 + 495.552)
    assert SUMS["generation_seconds"] == pytest.approx(
        sum(R1["money"]["arithmetic"]["leg_seconds"].values())
    ), "the generation legs are r1's — the packs did not move"
    assert round(SUMS["total_seconds"], 3) == 5476.552
    assert round(SUMS["hours"], 4) == 1.5213
    assert round(SUMS["worst_case_usd_at_the_price_ceiling"], 4) == 1.2170
    stop = SUMS["cumulative"]
    assert stop["hard_stop_seconds"] == 6100.0
    assert stop["hard_stop_usd_at_the_price_ceiling"] == 1.3556 < 1.38
    assert stop["session_ceiling_seconds"] == 6210.0 >= stop["hard_stop_seconds"]
    step = RECORD["money"]["step_sum"]
    assert step["r1_pods_usd"] == 0.117783
    assert step["sum_usd"] == pytest.approx(1.497783)
    assert step["sum_usd"] <= step["step_budget_usd"] == 1.50
    # the overhead fell only because ssh and staging bought their own lines
    assert SUMS["overhead_seconds"] == 1300.0
    assert (
        SUMS["ssh_seconds_charged"] + SUMS["stage_launch_seconds_charged"]
        >= prereg.R1_OVERHEAD_SECONDS - SUMS["overhead_seconds"]
    )
    assert SUMS["rows_copied_back"] == 200 + 200 + 64 == 464


def test_the_recovery_clause_is_REACHABLE_and_that_is_why_rung_2_is_500_and_not_600():
    recovery = SUMS["recovery_arithmetic"]
    stop = SUMS["cumulative"]["hard_stop_seconds"]
    assert recovery["one_dead_pod_at_rung_2_seconds"] == 500.0
    assert round(recovery["one_dead_pod_at_rung_2_usd"], 4) == 0.1111
    assert recovery["then_the_full_worst_case_seconds"] == pytest.approx(5976.552)
    assert recovery["then_the_full_worst_case_seconds"] <= stop
    assert round(recovery["then_the_full_worst_case_usd"], 4) == 1.3281
    assert recovery["then_the_full_worst_case_usd"] <= RECORD["money"]["cap_usd_all_in"]
    assert recovery["widest_dead_pod_that_still_fits_seconds"] == pytest.approx(
        stop - SUMS["total_seconds"]
    )
    # the counterfactual: at 600 the worst case ITSELF grows, and the recovery leaves the stop
    assert recovery["counterfactual_600_total_seconds"] == pytest.approx(5576.552)
    assert recovery["counterfactual_600_with_one_dead_pod_seconds"] == pytest.approx(6176.552)
    assert recovery["counterfactual_600_with_one_dead_pod_seconds"] > stop
    assert recovery["re_creations_allowed"] == 1
    assert "THIRD pod" in recovery["a_second_dead_pod"]


# --- H6, driven ------------------------------------------------------------------------------------


def test_every_number_the_r2_contract_prints_re_derives():
    h6 = RECORD["h6"]
    assert h6["mismatches"] == []
    assert all(row["agrees"] for row in h6["rows"])
    assert len(h6["rows"]) >= 30
    named = {row["name"] for row in h6["rows"]}
    for reason in (
        "a_600_s_rung_2_would_put_the_recovery_past_the_hard_stop",
        "the_overhead_reduction_is_covered_by_the_new_lines",
        "rows_copied_back",
        "the_step_sum_is_inside_the_step_budget",
        "the_create_anchored_backstop",
        "the_live_packs_still_carry_r1s_call_counts",
    ):
        assert reason in named, reason


def test_H6_REFUSES_a_number_that_stops_re_deriving(monkeypatch, sealed_pins):
    """Every mode exercised — an equality, a `below` and an `at_least` — and then the premise."""
    for name, bent in (
        ("total_seconds", 999.0),
        ("ssh_deadman_multiplier", 99.0),
        ("step_sum_usd", 99.0),
    ):
        monkeypatch.setitem(prereg.CONTRACT_PRINTS, name, bent)
        with pytest.raises(SystemExit, match="H6 is the step-1 refusal gate"):
            prereg.build()
        monkeypatch.undo()
    # `below`: a cap under the worst case is refused
    monkeypatch.setattr(prereg, "CAP_USD", 0.50)
    with pytest.raises(SystemExit, match="H6 is the step-1 refusal gate"):
        prereg.build()
    monkeypatch.undo()
    # `at_least`: an ssh ceiling under the widest reading is refused
    monkeypatch.setattr(prereg, "SSH_DEADMAN_SECONDS", 200.0)
    with pytest.raises(SystemExit, match="H6 is the step-1 refusal gate"):
        prereg.build()
    monkeypatch.undo()
    # and the one that would have shipped: a hard stop too small for the recovery clause
    monkeypatch.setattr(prereg, "HARD_STOP_SECONDS", 5900.0)
    with pytest.raises(SystemExit, match="H6 is the step-1 refusal gate"):
        prereg.build()
    monkeypatch.undo()
    assert prereg.build()["h6"]["mismatches"] == []


def test_the_call_counts_are_re_derived_from_the_LIVE_packs_and_not_copied(
    monkeypatch, sealed_pins
):
    """Two independent derivations that agree — the live packs, and what r1 registered.

    A copied count would have made the generation legs a quotation of r1 rather than a reading of
    the packs, and a pack that moved would have gone on being priced at yesterday's size.
    """
    assert prereg.r1_producer.counts() == R1["money"]["arithmetic"]["calls"] == SUMS["calls"]
    monkeypatch.setattr(prereg.r1_producer, "counts", lambda: {**SUMS["calls"], "shot": 63})
    with pytest.raises(SystemExit, match="the live packs carry"):
        prereg.build()
    monkeypatch.undo()
    assert prereg.build()["h6"]["mismatches"] == []


def test_the_readings_the_amendments_rest_on_are_taken_from_r1s_OWN_gate_record():
    """Not typed. The two rung-2 KILLs are read out of the record the r1 session appended to."""
    run = json.loads((REPO_ROOT / prereg.R1_RUN_NAME).read_text("utf-8"))
    assert prereg.ssh_readings(run) == SUMS["ssh_readings_2026_08_20"]
    bent = json.loads(json.dumps(run))
    bent["gates"] = [one for one in bent["gates"] if one.get("verdict") != "KILL"]
    with pytest.raises(SystemExit, match="rung-2 KILLs"):
        prereg.ssh_readings(bent)
    assert prereg.r1_pods(run)["billed_usd"] == 0.117783


def test_the_kill_clock_still_has_eight_rungs_and_only_two_of_them_moved():
    assert sorted(RUNG) == list(range(1, 9))
    r1_rungs = {one["rung"]: one for one in R1["kill_clock"]}
    for number in (1, 4, 5, 8):
        assert RUNG[number] == r1_rungs[number], number
    assert RUNG[2] != r1_rungs[2] and RUNG[3] != r1_rungs[3]
    # rung 6 keeps its shape and moves only the number the money moved
    assert gate.first_number(RUNG[6]["rule"]) == 6100.0
    assert "no THIRD pod" in " ".join(RECORD["do_not"])
    assert prereg.OUT_NAME in RECORD["frozen_when_the_pod_exists"]
    assert r1_prereg.OUT_NAME in RECORD["frozen_when_the_pod_exists"]


def test_rung_4_prices_the_run_with_r2s_overhead_and_not_r1s():
    """The block the gate ACTS on, not the block a human reads.

    `projection()` adds `cumulative.projection_gate.overhead_seconds` on every poll of the watch. r1
    charged 1 800 s there because r1's overhead covered the staging; r2 gave ssh and staging their
    own budget lines and cut the overhead to 1 300. Carried across whole, the stale copy over-charges
    every projection by 500 s against a hard stop r2 also LOWERED — and rung 4 deletes a healthy pod
    at the shot, on the very path the recovery clause exists to keep reachable.
    """
    projection = SUMS["cumulative"]["projection_gate"]
    assert projection["overhead_seconds"] == SUMS["overhead_seconds"] == 1300.0
    assert "1.38" in projection["verdict"] and "6100" in projection["verdict"]
    assert "1.50" not in projection["verdict"] and "6300" not in projection["verdict"]
    # the interval, the formula and «why every leg» did NOT move — the algorithm is r1's
    r1_projection = R1["money"]["arithmetic"]["cumulative"]["projection_gate"]
    for name in ("every", "formula", "why_every_leg"):
        assert projection[name] == r1_projection[name], name
    row = next(
        one
        for one in RECORD["h6"]["rows"]
        if one["name"] == "the_projection_gate_charges_the_registered_overhead"
    )
    assert row["agrees"] and row["re_derived"] == row["registered"] == 1300.0


def test_no_number_r2_REPEALED_survives_anywhere_in_its_money_block():
    """A sweep, not a spot check: r1's overhead, r1's hard stop and r1's cap, hunted as VALUES.

    Every r2 number was re-derived, so any leaf still holding one of r1's is a block that was copied
    and not read. The one legitimate 1.50 is the STEP budget the ruling kept, and it is named.
    """

    def leaves(node, path=""):
        if isinstance(node, dict):
            for key, item in node.items():
                yield from leaves(item, f"{path}.{key}")
        elif isinstance(node, list):
            for index, item in enumerate(node):
                yield from leaves(item, f"{path}.{index}")
        elif isinstance(node, (int, float)) and not isinstance(node, bool):
            yield path, float(node)

    found = {}
    for path, value in leaves(RECORD["money"], "money"):
        if value in (1800.0, 6300.0, 180.0, 1.5):
            found.setdefault(value, []).append(path)
    assert found == {1.5: ["money.step_sum.step_budget_usd"]}, found
    # and the premise: those values really are r1's, so the sweep is not vacuous
    r1_sums = R1["money"]["arithmetic"]
    assert r1_sums["overhead_seconds"] == 1800.0
    assert r1_sums["cumulative"]["hard_stop_seconds"] == 6300.0
    assert R1["money"]["cap_usd_all_in"] == 1.5


def test_the_gate_REFUSES_a_rung_3_that_carries_no_backstop():
    """The launch anchor is only safe because a create-anchored backstop bounds it.

    A registration without the field is a refusal, never a default — the same rule the overshoot
    tolerance now lives under, driven so it is known to fire.
    """
    bent = json.loads(json.dumps(RECORD))
    del next(one for one in bent["kill_clock"] if one["rung"] == 3)["backstop_seconds"]
    state = {
        "pods": [{"pod_id": "p", "created_at": "2026-08-21T09:00:00+00:00", "usd_per_hour": 0.74}]
    }
    with pytest.raises(SystemExit, match="backstop_seconds"):
        gate.gate_boot(bent, state, 100.0, None, None)
    # unbent, the same call is a WAIT and not a refusal
    assert gate.gate_boot(RECORD, state, 100.0, None, None)["verdict"] == "WAIT"
