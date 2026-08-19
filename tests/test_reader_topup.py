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
    assert gates["0_transport_ssh_deadman"]["kill_at_seconds"] == 180
    assert gates["1_first_reply"]["ceiling_since_generation_started_seconds"] == 720
    affordability = gates["1_first_reply"]["affordability_deadline_since_create_seconds"]
    usable = 2.00 / 0.74 * 3600 - 60.0
    assert affordability == pytest.approx(
        usable - PREREG["money"]["arithmetic"]["generation_projection_seconds"], abs=0.1
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


# --- the driver's swaps -----------------------------------------------------


def test_the_swap_puts_every_borrowed_name_back():
    before = {name: getattr(v5b, name) for name in driver.SWAPPED}
    before_pack = v5.build_pack
    with driver.as_this_phase():
        assert v5b.PHASE == "reader-topup"
        assert v5b.PREREG == driver.PREREG
        assert v5.build_pack is driver.build_pack
    assert {name: getattr(v5b, name) for name in driver.SWAPPED} == before
    assert v5.build_pack is before_pack


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
