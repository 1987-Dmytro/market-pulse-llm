"""The migrate probe, DRIVEN — and the registration that says why no pod was created.

`docs/PROMPT-lora-c-migrate.md` D2 is one paid step that never happened: EU-SE-1 does not support
network volumes, so the contract's first action is refused by the platform. This file does four
jobs:

* **the probe's readings are parsed from the platform's own strings**, including the one that
  decides everything — the refusal that enumerates the volume-capable datacenters. A parse that
  quietly yields an empty list would read as «no datacenter takes a volume», so the negative control
  is here beside it ([[a_checker_whose_failure_is_silence]]);
* **the intersection is a three-way filter** and each of the three is proved to bite on its own;
* **`results/prereg_lora_c_migrate.json` transcribes the contract faithfully** — every threshold it
  registers is greppable back into `docs/PROMPT-lora-c-migrate.md`
  ([[preregistration_is_a_file_not_a_constant]]);
* **the three findings the registration records about the plan's numbers are demonstrated**, not
  asserted: the equality guard that would have fired after the meter starts, the deadlines that do
  not fit inside the hard stop, and `first_number` reading a card name as a price.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import gate_lora_b as rungs  # noqa: E402
import gate_lora_c_vramprobe as vramprobe  # noqa: E402
import probe_lora_c_migrate_stock as probe  # noqa: E402

PREREG = json.loads((REPO_ROOT / "results" / "prereg_lora_c_migrate.json").read_text("utf-8"))
STOCK = json.loads((REPO_ROOT / "results" / "lora_c_migrate_stock.json").read_text("utf-8"))
CONTRACT = " ".join((REPO_ROOT / "docs" / "PROMPT-lora-c-migrate.md").read_text("utf-8").split())
"""Whitespace-normalised: the contract wraps «download deadline 2 400 s with liveness\n600 s» across
a line, and a raw grep for a wrapped quotation finds nothing and says «absent»
([[verbatim_quotes_must_be_grepped]])."""

REFUSAL = (
    '{"error":"failed to create volume: create network volume: Data center \\"NOPE\\" not found or'
    " does not support network volumes. Available data centers: AP-IN-2, AP-JP-1, CA-MTL-3,"
    " CA-MTL-4, EU-FR-1, EU-NL-1, EU-RO-1, EUR-IS-1, EUR-IS-3, EUR-IS-4, EUR-NO-1, EUR-NO-2,"
    " US-CA-2, US-CO-1, US-IL-1, US-KS-2, US-MO-2, US-NC-2, US-NE-1, US-TX-3,"
    ' US-WA-1.","code":"server_error","status":500}'
)
"""The message the platform actually returned on 2026-08-25, kept verbatim. It is the only reading
in this contract that could not be taken twice for free without a second refused create."""


class Done:
    def __init__(self, stdout: str = "", returncode: int = 0, stderr: str = ""):
        self.stdout, self.returncode, self.stderr = stdout, returncode, stderr


def faked(answers: dict):
    """A stand-in for `subprocess.run` that answers by the command's last meaningful word.

    The probe is nothing but four listings and a refusal, so driving `main` means driving the thing
    that shells out ([[stub_driven_script_verification]]).
    """

    def run(command, capture_output=True, text=True):
        key = "create" if "create" in command else command[1] + "-" + command[2]
        return answers[key]

    return run


# --- the refusal, which is the reading that decides the contract --------------------------------


def test_the_refusal_enumerates_the_volume_capable_datacenters():
    read = probe.refused_create(faked({"create": Done(stdout=REFUSAL)}))
    assert read["the_create_was_refused"] is True
    assert len(read["datacenters"]) == 21
    assert "EU-RO-1" in read["datacenters"]
    assert "CA-MTL-3" in read["datacenters"]


def test_EU_SE_1_is_not_among_them_which_is_the_whole_finding():
    read = probe.refused_create(faked({"create": Done(stdout=REFUSAL)}))
    assert "EU-SE-1" not in read["datacenters"]
    assert STOCK["the_rulings_datacenter"] == "EU-SE-1"
    assert STOCK["the_rulings_datacenter_takes_a_network_volume"] is False


def test_a_message_without_the_sentinel_yields_an_empty_list_and_SAYS_so():
    """The negative control. An empty list must never be mistaken for «none of them qualify»."""
    read = probe.refused_create(faked({"create": Done(stdout='{"error":"quota exceeded"}')}))
    assert read["the_create_was_refused"] is False
    assert read["datacenters"] == []


def test_the_probe_creates_nothing_and_the_volume_listing_is_the_control():
    assert STOCK["the_listing_did_not_move"] is True
    assert STOCK["network_volume_list_before"] == STOCK["network_volume_list_after"]
    names = {one["name"] for one in STOCK["network_volume_list_after"]}
    assert names == {"mp-srv2"}, "a volume was created or deleted by a probe that may do neither"


# --- the intersection, and each of its three conditions biting on its own ------------------------

CATALOGUE = [
    {
        "displayName": "RTX A6000",
        "gpuId": "NVIDIA RTX A6000",
        "memoryInGb": 48,
        "securePricePerHr": 0.53,
        "dataCenterAvailability": [
            {"dataCenterId": "EU-SE-1", "stockStatus": "Low"},
            {"dataCenterId": "EU-RO-1", "stockStatus": "none"},
        ],
    },
    {
        "displayName": "RTX A4000",
        "gpuId": "NVIDIA RTX A4000",
        "memoryInGb": 16,
        "securePricePerHr": 0.17,
        "dataCenterAvailability": [{"dataCenterId": "EU-RO-1", "stockStatus": "High"}],
    },
    {
        "displayName": "PRO 6000 MIG 48GB",
        "gpuId": "NVIDIA RTX PRO 6000 MIG 2g.48gb",
        "memoryInGb": 48,
        "securePricePerHr": 1.09,
        "dataCenterAvailability": [{"dataCenterId": "US-NE-1", "stockStatus": "Low"}],
    },
]
CAPABLE = ["EU-RO-1", "US-NE-1"]


def test_the_minimum_is_matched_on_memory_and_not_on_the_name():
    """«A40» is a substring of «RTX A4000», and a 16 GB card answering for a 48 GB one is the whole
    question wrong ([[run_the_instrument_on_the_named_example]])."""
    cards = probe.cards_at_or_above(CATALOGUE, 48)
    assert set(cards) == {"RTX A6000", "PRO 6000 MIG 48GB"}
    assert "A40" in "RTX A4000", "the substring hazard this test exists for has gone away"


def test_in_stock_but_in_a_datacenter_that_cannot_hold_a_volume_is_excluded():
    rows = probe.candidates(probe.cards_at_or_above(CATALOGUE, 48), CAPABLE)
    assert [one["card"] for one in rows] == ["PRO 6000 MIG 48GB"]
    assert all(one["datacenter"] != "EU-SE-1" for one in rows)


def test_volume_capable_but_out_of_stock_is_excluded():
    rows = probe.candidates(probe.cards_at_or_above(CATALOGUE, 48), ["EU-RO-1"])
    assert rows == []


def test_the_intersection_is_sorted_by_price_because_the_cap_divides_by_one():
    cards = probe.cards_at_or_above(CATALOGUE, 48)
    rows = probe.candidates(cards, ["EU-SE-1", "US-NE-1"])
    assert [one["secure_usd_per_hour"] for one in rows] == [0.53, 1.09]


def test_the_rulings_card_is_reported_datacenter_by_datacenter():
    where = probe.where_is(probe.cards_at_or_above(CATALOGUE, 48), "RTX A6000", CAPABLE)
    assert where["found"] is True
    assert where["in_stock_and_volume_capable"] == []
    rows = {one["datacenter"]: one for one in where["datacenters"]}
    assert rows["EU-SE-1"]["stock"] == "Low"
    assert rows["EU-SE-1"]["takes_a_network_volume"] is False
    assert rows["EU-RO-1"]["takes_a_network_volume"] is True


def test_a_card_the_catalogue_does_not_have_says_so_rather_than_returning_nothing():
    assert probe.where_is({}, "RTX A6000", CAPABLE) == {"card": "RTX A6000", "found": False}


# --- the two listings, which spell «out of stock» differently ------------------------------------


def test_the_two_spellings_of_out_of_stock_normalise_to_one():
    assert probe.normalise("") == probe.normalise("none") == probe.normalise(None) == "none"
    assert probe.normalise("Low") == "Low"


def test_a_disagreement_between_the_two_listings_is_a_row_and_not_a_warning():
    left = {("EU-RO-1", "RTX A6000"): "none"}
    right = {("EU-RO-1", "RTX A6000"): "Low"}
    read = probe.the_two_listings_agree(left, right)
    assert read["agree"] is False
    assert read["disagreements"] == [
        {
            "datacenter": "EU-RO-1",
            "card": "RTX A6000",
            "datacenter_list": "none",
            "gpu_list": "Low",
        }
    ]


def test_the_two_listings_agreed_on_every_shared_pair_when_the_reading_was_taken():
    assert STOCK["cross_check"]["agree"] is True
    assert STOCK["cross_check"]["pairs_compared"] > 100


def test_main_writes_the_record_it_read(tmp_path, monkeypatch):
    monkeypatch.setattr(probe, "OUT", tmp_path / "out.json")
    monkeypatch.setattr(probe, "REPO_ROOT", tmp_path)
    run = faked(
        {
            "create": Done(stdout=REFUSAL),
            "network-volume-list": Done(stdout="[]"),
            "datacenter-list": Done(stdout="[]"),
            "gpu-list": Done(stdout=json.dumps(CATALOGUE)),
        }
    )
    assert probe.main([], run) == 0
    written = json.loads((tmp_path / "out.json").read_text("utf-8"))
    assert written["the_rulings_datacenter_takes_a_network_volume"] is False
    assert [one["card"] for one in written["candidates"]] == ["PRO 6000 MIG 48GB"]


def test_a_listing_that_fails_is_recorded_and_not_silently_empty():
    read = probe.run_json(
        ["runpodctl", "gpu", "list"], faked({"gpu-list": Done(returncode=1, stderr="boom")})
    )
    assert read["failed"] == "runpodctl gpu list"
    assert read["stderr"] == "boom"


# --- the registration transcribes the contract ---------------------------------------------------


def test_the_registration_says_it_is_not_law():
    assert PREREG["state"].startswith("REFUSED BEFORE THE CREATE")
    assert "EVIDENCE, not law" in PREREG["state"]


@pytest.mark.parametrize(
    "quote",
    [
        "datacenter EU-SE-1",
        "volume 100 GB (parity with `mp-srv2`)",
        "card `RTX A6000` at ≤$0.60/h by EQUALITY",
        "boot ssh ≤500 s",
        "download deadline 2 400 s with liveness 600 s from the last progress line",
        "model-load proof deadline 600 s",
        "hard stop 3 600 s at create",
        "cap $1.00 all-in",
        "the pinned revision `842da379…`",
    ],
)
def test_every_clause_the_registration_transcribes_is_in_the_contract(quote):
    assert quote in CONTRACT, f"{quote!r} is not what docs/PROMPT-lora-c-migrate.md says"


def test_every_registered_threshold_is_the_number_its_own_rule_carries():
    """`first_number` is how every rung in this line reads its threshold; the two numbers may never
    disagree, the two rungs with no sibling equivalent included."""
    for entry in PREREG["registered_as_the_contract_wrote_it"]["kill_clock"]:
        if entry["rung"] == 0:
            continue  # a free refusal carries no number in its rule
        assert rungs.first_number(entry["rule"]) == entry["threshold"], entry["what"]


def test_the_contracts_own_numbers_are_the_registered_ones():
    registered = PREREG["registered_as_the_contract_wrote_it"]
    assert registered["cap_usd_all_in"] == 1.00
    assert registered["price_ceiling_usd_per_hour"] == 0.60
    assert registered["volume_gb"] == 100
    assert {one["rung"]: one["threshold"] for one in registered["kill_clock"]} == {
        0: 0.0,
        1: 500.0,
        2: 2400.0,
        3: 600.0,
        6: 3600.0,
        7: 1.0,
    }


def test_the_frozen_registration_is_untouched():
    frozen = REPO_ROOT / "results" / "prereg_lora_c.json"
    assert (
        hashlib.sha256(frozen.read_bytes()).hexdigest()
        == PREREG["this_is_not_the_registered_attempt"]["sha256"]
    )


# --- the three findings, demonstrated ------------------------------------------------------------


def test_the_vramprobes_equality_guard_would_have_fired_after_the_meter_starts():
    """The reason it is registered as a finding: at $1.00 and $0.53 the same helper raises, and the
    place it raises is `--open`, which runs when the pod already exists
    ([[one_constant_answering_two_questions]])."""
    found = PREREG["arithmetic_found_before_the_money"][
        "the_hard_stop_must_be_an_INEQUALITY_not_an_equality"
    ]
    record = {
        "money": {
            "cap_usd_all_in": found["cap_usd_all_in"],
            "pre_pod_arithmetic": {
                "hard_stop_seconds": found["hard_stop_seconds"],
                "hard_stop_formula": "cap_usd_all_in / usd_per_hour * 3600",
            },
        }
    }
    with pytest.raises(SystemExit):
        vramprobe.the_hard_stop_is_solved_at_the_observed_price(record, found["price_usd_per_hour"])


def test_the_inequality_that_generalises_holds_where_the_equality_does_not():
    found = PREREG["arithmetic_found_before_the_money"][
        "the_hard_stop_must_be_an_INEQUALITY_not_an_equality"
    ]
    buys = found["cap_usd_all_in"] / found["price_usd_per_hour"] * 3600
    assert round(buys, 2) == found["seconds_the_cap_buys"]
    assert buys >= found["hard_stop_seconds"]
    assert round(buys - found["hard_stop_seconds"], 2) == found["headroom_seconds"]


def test_the_three_deadlines_do_not_fit_inside_the_hard_stop():
    registered = {
        one["rung"]: one["threshold"]
        for one in PREREG["registered_as_the_contract_wrote_it"]["kill_clock"]
    }
    found = PREREG["arithmetic_found_before_the_money"][
        "the_four_deadlines_are_jointly_unreachable_at_their_bounds"
    ]
    spent = registered[1] + registered[2] + registered[3]
    assert registered[6] - spent == found["left_for_everything_else_seconds"]
    assert spent == 3500.0


def test_first_number_reads_a_card_name_as_a_price():
    """The hazard, run on the exact string a rung-0 rule would naturally carry."""
    assert rungs.first_number("the card RTX A6000 at ≤$0.60/h is authorised") == 6000.0
    assert rungs.first_number("$0.60 per hour is the ceiling; the card is graded by name") == 0.60


def test_both_formatter_drifted_files_are_pinned_by_a_record():
    drifted = PREREG["the_known_formatter_state"]["drifted_files"]
    assert set(drifted) == {
        "scripts/write_lora_c_prereg.py",
        "scripts/build_lora_c_marker_census.py",
    }
    for path in drifted:
        sha = hashlib.sha256((REPO_ROOT / path).read_bytes()).hexdigest()
        found = subprocess.run(
            ["grep", "-rl", sha, "results/"], cwd=REPO_ROOT, capture_output=True, text=True
        )
        assert found.stdout.strip(), f"{path} is named as pinned and no record in results/ holds it"


# --- the money table the operator is handed -------------------------------------------------------


def test_the_r3_table_re_derives_from_its_own_inputs():
    table = PREREG["what_the_remaining_r2_cap_buys_at_each_obtainable_price"]
    left, steps = table["remaining_r2_cap_usd"], table["steps"]
    for price, row in table["at_each_price"].items():
        seconds = left / float(price) * 3600
        assert round(seconds, 1) == row["seconds"]
        assert (
            round((seconds - table["fixed_seconds_cheapest"]) / steps, 2)
            == (row["seconds_per_step_cheapest"])
        )
        assert (
            round((seconds - table["fixed_seconds_richest"]) / steps, 2)
            == (row["seconds_per_step_richest"])
        )


def test_the_only_obtainable_price_that_reaches_the_measured_rate_is_out_of_stock():
    table = PREREG["what_the_remaining_r2_cap_buys_at_each_obtainable_price"]
    measured = table["the_only_step_rate_this_repo_has_measured"]
    reach = [
        price
        for price, row in table["at_each_price"].items()
        if row["seconds_per_step_cheapest"] >= measured
    ]
    assert reach == ["0.53"]
    assert table["at_each_price"]["0.53"]["in_stock_in_a_volume_capable_datacenter"] is False


def test_the_conclusion_survives_a_card_twice_as_fast():
    table = PREREG["what_the_remaining_r2_cap_buys_at_each_obtainable_price"]
    bound = table["the_conclusion_survives_a_faster_card"]
    charges = table["fixed_seconds_cheapest"] - 500 - 300
    halved = 500 + 300 + charges / 2
    assert round(halved, 1) == bound["fixed_seconds_with_the_model_dependent_charges_halved"]
    seconds = table["at_each_price"]["2.09"]["seconds"]
    assert (
        round((seconds - halved) / table["steps"], 2)
        == (bound["seconds_per_step_at_2.09_under_that_bound"])
    )
    assert (
        bound["seconds_per_step_at_2.09_under_that_bound"]
        < (table["the_only_step_rate_this_repo_has_measured"])
    )


def test_every_number_in_the_report_is_re_derived_from_the_file_that_owns_it():
    done = subprocess.run(
        [sys.executable, "scripts/check_lora_c_migrate_report.py"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert done.returncode == 0, done.stdout + done.stderr
