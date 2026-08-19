"""Branch B — the projection that prices the buy, the registration, and the driver's two swaps.

Everything here runs at $0 on a bare checkout. The three properties worth the file: the projection
is honest about which of its numbers carry information, the registration's units PARTITION each
thread's payable comments exactly once (the property `reader_v5.merge` rests on), and the driver
puts every borrowed name back.
"""

import hashlib
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import project_reader_topup as projector  # noqa: E402
import read_threads_reader_topup as driver  # noqa: E402
import read_threads_reader_v5 as v5  # noqa: E402
import read_threads_reader_v5b as v5b  # noqa: E402
import write_reader_topup_prereg as producer  # noqa: E402

PROJECTION = json.loads((REPO_ROOT / "results" / "reader_topup_projection.json").read_text("utf-8"))
PREREG = json.loads((REPO_ROOT / "results" / "reader_topup_prereg.json").read_text("utf-8"))
"""ATTEMPT A's registration — the one whose own gate STOPped its run. Not superseded as history:
the population, the cap, the meter and every unit in it are what attempt B inherits unchanged."""

PREREG_B = json.loads((REPO_ROOT / "results" / "reader_topup_prereg_b.json").read_text("utf-8"))


# --- the projection ---------------------------------------------------------


def test_the_projection_rebuilds_byte_identical_and_is_what_shipped(tmp_path):
    first, second = tmp_path / "a", tmp_path / "b"
    assert projector.main(["--outdir", str(first)]) == 0
    assert projector.main(["--outdir", str(second)]) == 0
    name = projector.OUT_NAME
    assert (first / name).read_bytes() == (second / name).read_bytes()
    assert (first / name).read_bytes() == (REPO_ROOT / name).read_bytes()


def test_the_in_sample_total_is_named_as_arithmetic_not_as_accuracy():
    """The trap this record exists to avoid quoting: least squares with an intercept forces the
    residuals to sum to zero, so «the fit reproduces the total» is true of any such fit."""
    model = PROJECTION["instrument"]["model"]
    assert "forces the residuals to sum to zero" in model["in_sample_total_is_not_evidence"]
    out = PROJECTION["instrument"]["out_of_sample"]
    assert out["run"] == "reader-v4" and out["items"] > 15
    assert 1.0 < out["ratio"] < 1.2


def test_the_projection_is_priced_on_units_and_not_on_threads():
    proj = PROJECTION["projection"]
    assert proj["items"] == 132 > PROJECTION["population"]["threads_needing_a_verdict"] == 105
    published = proj["what_the_report_published"]
    assert published["usd"] == 1.2
    assert "MEAN" in published["how"]
    assert proj["usd"]["ceiling"] > published["usd"]  # the correction is upward and says so
    assert proj["all_in_seconds"] == pytest.approx(
        proj["generation_seconds"] + proj["boot_seconds_charged"]
    )
    for name, rate in (("ceiling", 0.80), ("reader_card_example", 0.74)):
        assert proj["usd"][name] == pytest.approx(proj["all_in_hours"] * rate, abs=0.005)


def test_the_record_says_which_half_of_the_finding_the_buy_closes():
    buys = PROJECTION["buys"]
    assert buys["topic"]["this_is_the_half_the_buy_closes_completely"] is True
    assert buys["entity_block"]["this_is_the_half_the_buy_closes_PARTIALLY"] is True
    entity = buys["entity_block"]
    expected = (
        entity["rows_with_one_today"]
        + (entity["of"] - 91) * entity["rate_inside_the_threads_already_bought"]
    )
    assert entity["expected_after"] == round(expected)
    assert entity["expected_after"] < entity["of"]  # nothing here promises 650 of 650


def test_the_projection_authorises_nothing():
    assert "NO cap" in PROJECTION["authorises_nothing"]
    assert "cap" not in json.dumps(PROJECTION["projection"], ensure_ascii=False).lower()


# --- the registration -------------------------------------------------------


def test_the_registration_rebuilds_byte_identical_and_is_what_shipped(tmp_path):
    first, second = tmp_path / "a", tmp_path / "b"
    assert producer.main(["--outdir", str(first)]) == 0
    assert producer.main(["--outdir", str(second)]) == 0
    name = producer.OUT_NAME
    assert (first / name).read_bytes() == (second / name).read_bytes()
    assert (first / name).read_bytes() == (REPO_ROOT / name).read_bytes()


def test_the_units_partition_every_threads_payable_comments_exactly_once():
    """What `reader_v5.merge` rests on: chunks tile the comment list, no overlap and no gap."""
    sizes = PROJECTION["population"]["sizes"]
    seen: dict[str, list[int]] = {}
    for unit in PREREG["population"]["units"]:
        seen.setdefault(unit["thread"], []).extend(unit["msg_ids"])
    assert sorted(seen) == sorted(sizes)
    for thread, ids in seen.items():
        assert len(ids) == len(set(ids)) == sizes[thread], thread


def test_a_chunked_thread_carries_its_part_numbers_and_a_whole_one_does_not():
    by_thread: dict[str, list[dict]] = {}
    for unit in PREREG["population"]["units"]:
        by_thread.setdefault(unit["thread"], []).append(unit)
    chunked = {name: parts for name, parts in by_thread.items() if len(parts) > 1}
    assert len(chunked) == 10
    for name, parts in chunked.items():
        assert [one["part"] for one in parts] == [[i, len(parts)] for i in range(1, len(parts) + 1)]
        assert all(one["id"] == f"{name}#{one['part'][0]}of{len(parts)}" for one in parts)
        assert all(one["payable_comments"] <= producer.CHUNK for one in parts)
    for name, parts in by_thread.items():
        if len(parts) == 1:
            assert parts[0]["part"] is None and parts[0]["id"] == name


def test_the_units_are_ordered_expensive_first():
    """THREADS descend by payable count and a thread's chunks stay in order inside it.

    Not the units' own counts: a 125-comment thread's last chunk is 13, so a monotone per-unit
    list would be the wrong property and would pass only by accident on a population with no
    chunks in it.
    """
    sizes = PROJECTION["population"]["sizes"]
    order, chunks = [], {}
    for unit in PREREG["population"]["units"]:
        if unit["thread"] not in chunks:
            order.append(unit["thread"])
        chunks.setdefault(unit["thread"], []).append(unit["part"][0] if unit["part"] else 1)
    assert order == sorted(order, key=lambda name: (-sizes[name], name))
    for name, parts in chunks.items():
        assert parts == sorted(parts), name


def test_no_request_comes_near_the_registered_input_ceiling():
    widest = max(one["rendered_chars"] for one in PREREG["population"]["units"])
    assert widest < 40_000
    assert widest == 16439


def test_every_units_sha_re_renders_from_the_store():
    """The pack builder's own check, run here so a moved comment is a $0 finding."""
    pack = driver.build_pack(PREREG)
    assert len(pack["items"]) == len(PREREG["population"]["units"]) == 132
    pinned = {one["id"]: one["rendering_sha256"] for one in PREREG["population"]["units"]}
    for item in pack["items"]:
        assert item["rendering_sha256"] == pinned[item["id"]]


def test_the_pack_marks_chunked_units_leg_B_so_the_ingest_merges_them():
    """v5's ingest merges by `leg == "B"`, and that is the whole of what this phase needed."""
    pack = driver.build_pack(PREREG)
    legs = {one["id"]: one["leg"] for one in pack["items"]}
    for unit in PREREG["population"]["units"]:
        assert legs[unit["id"]] == ("A" if unit["part"] is None else "B"), unit["id"]
    assert sorted({one["leg"] for one in pack["items"]}) == ["A", "B"]
    source = Path(v5.__file__).read_text(encoding="utf-8")
    assert 'if item["leg"] == "B":' in source  # the branch this rests on


def test_build_pack_refuses_a_unit_whose_request_has_moved():
    stale = json.loads(json.dumps(PREREG))
    stale["population"]["units"][0]["rendering_sha256"] = "0" * 64
    with pytest.raises(SystemExit, match="the request moved since the registration"):
        driver.build_pack(stale)


def test_the_cap_survives_the_worst_boot_on_record_at_the_worse_price():
    table = PREREG["money"]["arithmetic"]["at_each_boot"]
    assert all(row["fits"] for row in table)
    worst = min(row["times_the_projection_that_fits"] for row in table)
    assert worst == PREREG["money"]["arithmetic"]["worst_case_that_still_fits"] > 1.2
    at_the_worst = [
        row for row in table if row["boot_seconds"] == 1200.0 and row["price_usd_per_hour"] == 0.80
    ]
    assert len(at_the_worst) == 1 and at_the_worst[0]["fits"]
    for row in table:
        usable = PREREG["money"]["cap_usd_all_in"] / row["price_usd_per_hour"] * 3600 - 60.0
        assert row["usable_seconds"] == pytest.approx(usable, abs=0.05)


def test_the_cap_says_whose_derivation_it_is():
    rule = PREREG["money"]["cap_rule"]
    assert "EXECUTOR's" in rule and "the operator's word BEFORE any endpoint" in rule
    assert PREREG["money"]["cap_usd_all_in"] == 2.00
    assert "выполни ветку B" in PREREG["authority"]


def test_the_gates_are_the_proven_ones_and_the_binding_deadline_is_named():
    gates = PREREG["go_no_go"]["gates"]
    assert gates["0_transport_ssh_deadman"]["threshold_seconds"] == 180
    assert gates["1_first_reply"]["ceiling_since_generation_started_seconds"] == 720
    affordability = gates["1_first_reply"]["affordability_deadline_since_create_seconds"]
    usable = 2.00 / 0.74 * 3600 - 60.0
    assert affordability == pytest.approx(
        usable - PREREG["money"]["arithmetic"]["reading_projection_seconds"], abs=0.1
    )
    assert affordability > 720  # which is why the twelve-minute ceiling binds, as the record says
    assert "PESSIMISTIC" in gates["2_full_pass"]["rule"]


def test_a_stop_leaves_a_usable_partial_buy_and_the_record_says_so():
    assert "USABLE partial buy" in PREREG["go_no_go"]["partial_is_a_result"]
    assert "renders whatever verdicts exist" in PREREG["go_no_go"]["partial_is_a_result"]


def test_the_population_digest_is_the_projections_and_the_producer_pins_what_it_read():
    assert (
        PREREG["population"]["enumeration_sha256"] == PROJECTION["population"]["enumeration_sha256"]
    )
    for path, sha in PREREG["producer"]["borrowed"].items():
        assert hashlib.sha256((REPO_ROOT / path).read_bytes()).hexdigest() == sha, path
    live = hashlib.sha256(
        (REPO_ROOT / "scripts" / "write_reader_topup_prereg.py").read_bytes()
    ).hexdigest()
    assert PREREG["producer"]["sha256"] == live


# --- every command, driven at $0 --------------------------------------------
#
# This block is the one that was missing when the first pod was created, and the pod was deleted
# 23 s later because `--open` raised a KeyError on a field the registration spelled its own way.
# Dv486's rule, restated: a registered field no shipped command can read is a red gate HERE.


@pytest.fixture
def synthetic(tmp_path, monkeypatch):
    """The driver pointed at throwaway state, with a ledger that exists."""
    ledger = tmp_path / "spend.json"
    ledger.write_text(json.dumps({"runpod_balance_at_reader-topup_start": 20.0}), "utf-8")
    monkeypatch.setattr(driver, "RECORD", tmp_path / "run.json")
    monkeypatch.setattr(driver, "RAW", tmp_path / "pod.jsonl")
    monkeypatch.setattr(driver, "LEDGER", ledger)
    return tmp_path


def said(capsys) -> dict:
    """The FIRST JSON object a gate prints, without the human lines it prints around it.

    `raw_decode` and not a slice on the last brace: a KILL prints a verdict sentence after the
    object and that sentence has braces of its own in it.
    """
    out = capsys.readouterr().out
    return json.JSONDecoder().raw_decode(out[out.index("{") :])[0]


def open_a_segment(now_minus_seconds: float = 30.0) -> str:
    from datetime import UTC, datetime, timedelta

    created = datetime.now(UTC) - timedelta(seconds=now_minus_seconds)
    stamp = created.isoformat(timespec="seconds").replace("+00:00", "Z")
    assert (
        driver.main(
            [
                "--open",
                "--pod-id",
                "SYNTHETIC",
                "--created-at",
                stamp,
                "--usd-per-hour",
                "0.74",
                "--card",
                "NVIDIA GeForce RTX 4090",
            ]
        )
        == 0
    )
    return stamp


def test_pre_create_check_answers_before_anything_exists(synthetic, capsys):
    assert driver.main(["--pre-create-check"]) == 0
    answer = said(capsys)
    assert answer["may_create"] is True
    assert answer["cap_usd_all_in"] == 2.00 and answer["segments_allowed"] == 3


def test_open_records_the_segment_and_reads_every_field_it_needs(synthetic, capsys):
    """The command that failed on a live meter. It reads the meter block and gate 0's threshold."""
    open_a_segment()
    out = capsys.readouterr().out
    state = json.loads((synthetic / "run.json").read_text("utf-8"))
    assert len(state["segments"]) == 1
    assert state["segments"][0]["usd_per_hour"] == 0.74
    assert "gate0" in out or "threshold" in out or state["gates"]


def test_a_second_open_is_refused_because_two_meters_never_run_at_once(synthetic):
    open_a_segment()
    with pytest.raises(SystemExit, match="Never two pods at once"):
        open_a_segment()


def test_gate_zero_waits_inside_the_threshold_and_kills_past_it(synthetic, capsys):
    open_a_segment(now_minus_seconds=10.0)
    assert driver.main(["--gate0"]) == 3  # WAIT
    capsys.readouterr()
    assert driver.main(["--gate0", "--ssh-ok"]) == 0  # GO
    answer = said(capsys)
    assert answer["threshold_seconds"] == 180.0 and answer["verdict"] == "GO"


def test_gate_zero_kills_once_the_deadman_is_past(synthetic, capsys):
    open_a_segment(now_minus_seconds=400.0)
    capsys.readouterr()  # `--open` prints its segment AND a gate; both are drained
    assert driver.main(["--gate0"]) == 2  # KILL
    answer = said(capsys)
    assert answer["verdict"] == "KILL" and answer["seconds_left"] < 0


def test_the_deadline_gate_reads_the_boot_and_reading_projections(synthetic, capsys):
    open_a_segment(now_minus_seconds=60.0)
    capsys.readouterr()
    driver.main(["--deadlines"])
    answer = said(capsys)
    assert answer["contract_ceiling_seconds"] == 720.0
    assert answer["usable_seconds"] > 9000  # $2.00 at $0.74/h less the deletion margin
    assert answer["first_reply_must_land_by_create_elapsed"] > 0


def test_the_gate_with_no_reply_yet_takes_the_boot_branch(synthetic, capsys):
    open_a_segment(now_minus_seconds=60.0)
    capsys.readouterr()
    assert driver.main(["--gate", "--raw", str(synthetic / "pod.jsonl")]) == 3
    assert said(capsys)["verdict"] == "WAIT"


def test_the_gate_with_replies_takes_the_projection_branch(synthetic, capsys):
    """The full-pass inequality, over units this pack really has."""
    pack = json.loads((REPO_ROOT / "results" / "reader_topup_pack.json").read_text("utf-8"))
    rows = [
        {
            "id": one["id"],
            "seconds": 40.0,
            "rendering_sha256": one["rendering_sha256"],
            "reply": "{}",
        }
        for one in pack["items"][:3]
    ]
    (synthetic / "pod.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), "utf-8"
    )
    open_a_segment(now_minus_seconds=300.0)
    capsys.readouterr()
    code = driver.main(["--gate", "--raw", str(synthetic / "pod.jsonl")])
    answer = said(capsys)
    assert code in (0, 2)
    assert answer["units_read"] == 3 and answer["units_unread"] == 129
    assert answer["binding"]["which"] == "fitted_model"
    assert sorted(answer["reported_and_not_binding"]) == ["by_payable_comment", "by_unit", "why"]
    assert answer["usd"]["cap_usd_all_in"] == 2.00


def test_close_segment_writes_the_billed_end(synthetic, capsys):
    from datetime import UTC, datetime

    open_a_segment(now_minus_seconds=120.0)
    capsys.readouterr()
    assert (
        driver.main(
            [
                "--close-segment",
                "--deleted-at",
                datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
                "--outcome",
                "synthetic",
            ]
        )
        == 0
    )
    state = json.loads((synthetic / "run.json").read_text("utf-8"))
    assert state["segments"][0]["deleted_at"]
    assert state["segments"][0]["billed_seconds"] > 100


def test_the_ingest_parses_merges_the_chunks_and_names_its_refusals(synthetic, tmp_path):
    """A chunked thread's parts become one merged row — the property the population rests on."""
    pack = json.loads((REPO_ROOT / "results" / "reader_topup_pack.json").read_text("utf-8"))
    chunks = [one for one in pack["items"] if one["thread"] == "@matusi_ukr:22058"]
    assert len(chunks) == 8
    rows = []
    for one in chunks:
        verdict = {
            "thread": {"channel": one["channel"], "post_id": one["post_id"]},
            "post_summary": "проба",
            "discussion_summary": "проба",
            "entities": [],
            "signals": [],
            "per_comment": [],
            "noise": [],
        }
        rows.append(
            {
                "id": one["id"],
                "seconds": 40.0,
                "rendering_sha256": one["rendering_sha256"],
                "reply": json.dumps(verdict, ensure_ascii=False),
                "balanced": True,
            }
        )
    raw = tmp_path / "pod.jsonl"
    raw.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), "utf-8")
    evidence = tmp_path / "evidence.jsonl"
    import read_threads_reader_v5b as v5b_module

    with driver.as_this_phase():
        v5b_module.EVIDENCE = evidence
        v5.EVIDENCE = evidence
        assert v5b_module.main(["--ingest", "--raw", str(raw)]) == 0
    out = [json.loads(line) for line in evidence.read_text("utf-8").splitlines() if line]
    merged = [row for row in out if row["id"].endswith("#merged")]
    assert len(merged) == 1
    assert merged[0]["parsed"] is not None and merged[0]["merge_error"] is None
    assert merged[0]["payable_comments"] == 125


def fitted(payable: int) -> float:
    model = PROJECTION["instrument"]["model"]
    return model["intercept_seconds"] + model["slope_seconds_per_payable"] * payable


def rows_at(pack: dict, count: int, speed: float = 1.0) -> list[dict]:
    """The first `count` units answered at `speed` × their fitted seconds."""
    return [
        {
            "id": one["id"],
            "seconds": round(fitted(one["payable_comments"]) * speed, 3),
            "rendering_sha256": one["rendering_sha256"],
            "reply": "{}",
        }
        for one in pack["items"][:count]
    ]


def the_pack() -> dict:
    return json.loads((REPO_ROOT / "results" / "reader_topup_pack.json").read_text("utf-8"))


RATE = 0.74 / 3600
"""USD per SECOND. `usable_seconds` divides the cap by it, and `read_threads_reader_v5b.rate_of`
hands it the segment's `usd_per_second` — passing $/h here reads the cap as 2.7 seconds of pod and
turns every projection negative, which is how this constant earned a name."""


def test_ATTEMPT_A_s_gate_stops_at_its_own_fitted_first_reading():
    """The $0 question nobody asked before the create, kept as arithmetic.

    Substitute the registration's OWN fitted seconds for the first unit and ask what ATTEMPT A's
    gate prints at n=1. It prints STOP — not because the run is unaffordable but because
    `max(unread units ÷ read, unread payable ÷ read payable)` extrapolates the largest unit across
    all 132, and the units are ordered expensive-first. The run's one real measurement (77.5 s
    against a fitted 80.4 s) confirms the model; the estimator is what does not survive a
    population whose unit sizes span 1 to 16 with a median of 2.

    Attempt B's gate is asserted to GO on exactly this input in the test below. The two beside
    each other ARE the correction ([[a_new_leg_joins_the_gates_denominator]]).
    """
    pack = the_pack()
    first = pack["items"][0]
    assert first["payable_comments"] == 16  # expensive first, and this is the largest unit
    answer = v5.projection(PREREG, RATE, rows_at(pack, 1), 460.0, pack)

    assert answer["verdict"] == "STOP"
    assert answer["units_read"] == 1 and answer["projections"]["binding"]["which"] == "by_unit"
    assert answer["projections"]["by_unit"]["seconds"] > answer["usable_seconds"]


def test_ATTEMPT_B_s_gate_goes_on_the_same_reading(synthetic, capsys):
    """The correction, driven through the whole command and not only the function."""
    pack = the_pack()
    (synthetic / "pod.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows_at(pack, 1)), "utf-8"
    )
    open_a_segment(now_minus_seconds=460.0)
    capsys.readouterr()
    code = driver.main(["--gate", "--raw", str(synthetic / "pod.jsonl")])
    answer = said(capsys)

    assert code == 0 and answer["verdict"] == "GO"
    assert answer["binding"]["which"] == "fitted_model"
    assert answer["headroom_seconds"] > 2000
    legs = answer["reported_and_not_binding"]
    assert legs["by_unit"]["seconds"] > answer["usable_seconds"]
    assert legs["by_payable_comment"]["seconds"] < answer["usable_seconds"]


def test_the_calibration_floors_at_the_fit_so_a_fast_start_buys_nothing():
    pack = the_pack()
    quick = driver.projection(PREREG_B, RATE, rows_at(pack, 3, speed=0.5), 460.0, pack)
    exact = driver.projection(PREREG_B, RATE, rows_at(pack, 3, speed=1.0), 460.0, pack)
    assert quick["binding"]["measured_over_fitted"] < 1.0
    assert quick["binding"]["calibration_used"] == 1.0 == exact["binding"]["calibration_used"]
    assert quick["binding"]["seconds"] == exact["binding"]["seconds"]


def test_a_pod_slower_than_the_fit_stretches_the_projection_and_stops():
    pack = the_pack()
    verdicts = {
        speed: driver.projection(PREREG_B, RATE, rows_at(pack, 3, speed=speed), 460.0, pack)
        for speed in (1.0, 1.5, 2.0, 3.0)
    }
    assert verdicts[1.0]["verdict"] == "GO"
    assert verdicts[3.0]["verdict"] == "STOP"
    seconds = [verdicts[speed]["projected_total_seconds"] for speed in (1.0, 1.5, 2.0, 3.0)]
    assert seconds == sorted(seconds)  # slower pod, longer projection, monotonically
    for speed, gate in verdicts.items():
        assert gate["binding"]["calibration_used"] == pytest.approx(max(speed, 1.0), abs=0.05)


def test_the_whole_pack_at_fitted_seconds_never_stops():
    """The sweep attempt A could not survive: every n, on a run that fits."""
    pack = the_pack()
    stops = []
    elapsed = 285.0
    for count in range(1, len(pack["items"]) + 1):
        rows = rows_at(pack, count)
        elapsed = 285.0 + sum(row["seconds"] for row in rows)
        gate = driver.projection(PREREG_B, RATE, rows, elapsed, pack)
        if gate["verdict"] != "GO":
            stops.append((count, gate["projected_total_seconds"], gate["usable_seconds"]))
    assert stops == []
    final = driver.projection(PREREG_B, RATE, rows_at(pack, len(pack["items"])), elapsed, pack)
    assert final["units_unread"] == 0 and final["binding"]["seconds"] == 0.0
    assert final["projected_total_seconds"] < final["usable_seconds"]


def test_attempt_b_differs_from_attempt_a_only_where_the_ruling_says():
    """Re-derived here, and not read off the producer's own printout."""
    import write_reader_topup_prereg_b as producer_b

    left, right = dict(producer_b.flat(PREREG)), dict(producer_b.flat(PREREG_B))
    moved = sorted(
        {key for key in left.keys() & right.keys() if left[key] != right[key]}
        | (set(left) ^ set(right))
    )
    assert moved  # something DID change, or this test asserts nothing
    for key in moved:
        assert any(
            key == one or key.startswith(one + ".") or key.startswith(one + "[")
            for one in producer_b.MAY_MOVE
        ), key
    assert PREREG_B["money"]["cap_usd_all_in"] == PREREG["money"]["cap_usd_all_in"] == 2.00
    assert PREREG_B["population"] == PREREG["population"]
    assert PREREG_B["instruments"] == PREREG["instruments"]
    assert (
        PREREG_B["money"]["arithmetic"]["reading_projection_seconds"]
        == PREREG["money"]["arithmetic"]["reading_projection_seconds"]
    )
    assert (
        PREREG_B["supersedes"]["sha256"]
        == hashlib.sha256(
            (REPO_ROOT / "results" / "reader_topup_prereg.json").read_bytes()
        ).hexdigest()
    )


def test_the_b_registration_rebuilds_byte_identical(tmp_path):
    import write_reader_topup_prereg_b as producer_b

    first, second = tmp_path / "a", tmp_path / "b"
    assert producer_b.main(["--outdir", str(first)]) == 0
    assert producer_b.main(["--outdir", str(second)]) == 0
    name = producer_b.OUT_NAME
    assert (first / name).read_bytes() == (second / name).read_bytes()
    assert (first / name).read_bytes() == (REPO_ROOT / name).read_bytes()


def test_the_b_producer_refuses_a_change_nobody_ruled():
    import write_reader_topup_prereg_b as producer_b

    tampered = json.loads(json.dumps(PREREG_B))
    tampered["money"]["cap_usd_all_in"] = 3.00
    with pytest.raises(SystemExit, match="nobody ruled"):
        producer_b.assert_only_the_gate_moved(PREREG, tampered)


# --- the driver's swaps -----------------------------------------------------


def test_the_swap_puts_every_borrowed_name_back():
    before = {name: getattr(v5b, name) for name in driver.SWAPPED}
    before_pack, before_projection = v5.build_pack, v5.projection
    with driver.as_this_phase():
        assert v5b.PHASE == "reader-topup"
        assert v5b.PREREG == driver.PREREG
        assert v5.build_pack is driver.build_pack
        assert v5.projection is driver.projection
    assert {name: getattr(v5b, name) for name in driver.SWAPPED} == before
    assert v5.build_pack is before_pack and v5.projection is before_projection


def test_the_swap_refuses_a_name_v5b_no_longer_has(monkeypatch):
    monkeypatch.delattr(v5b, "EVIDENCE")
    with pytest.raises(SystemExit, match="no longer exists"):
        with driver.as_this_phase():
            pass


def test_the_driver_points_at_this_phases_files_and_not_v5bs():
    for name in driver.SWAPPED:
        ours = getattr(driver, name)
        if isinstance(ours, Path):
            assert "topup" in ours.name, name
    assert driver.PHASE == "reader-topup"
    assert driver.LEDGER.name == "spend_reader_topup.json"
