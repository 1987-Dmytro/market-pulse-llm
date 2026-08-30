"""`results/gate_census_w1_reader.json` — the reader's own cell, and the proof it was MEASURED.

Ruling 3 of the 2026-08-16 sitting says this cell is never derived, so the test that matters is the
one that would fail if it had been: the enumeration is held to `gate_census_w1.cell`'s own
measurement on both numbers, and the payable count is checked against the shipped grid's — because
the THREAD count alone does not distinguish this cell from one nobody meant.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from test_prompts import with_r2_put_back  # noqa: E402

import gate_census_w1 as census  # noqa: E402
import gate_census_w1_reader as reader_cell  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

RECORD_PATH = REPO_ROOT / "results" / "gate_census_w1_reader.json"
RECORD = json.loads(RECORD_PATH.read_text(encoding="utf-8"))
SHIPPED = json.loads(reader_cell.SHIPPED.read_text(encoding="utf-8"))


def test_the_committed_cell_is_what_the_producer_writes_today(tmp_path):
    out = tmp_path / "again.json"
    assert reader_cell.main(["--out", str(out)]) == 0
    assert with_r2_put_back(out.read_bytes()) == RECORD_PATH.read_bytes()
    assert "generated_at" not in RECORD_PATH.read_text(encoding="utf-8")


def test_the_cell_is_the_census_producers_own_measurement_and_not_an_arithmetic():
    """The clause, tested where it can fail. `cell()` is imported from the shipped producer and run
    over the same window; the enumeration beside it has to agree on the threads AND on the payable
    comments, which is what would catch a restatement that dropped a comment inside a thread it
    still kept."""
    kept = reader_cell.population()  # refuses inside if the two disagree
    assert (len(kept), sum(len(one["comments"]) for one in kept)) == (
        RECORD["measured"]["threads"],
        RECORD["measured"]["comments_payable"],
    )
    assert RECORD["cell"] == "narrow|varto_off|plus_spam+scam"
    assert reader_cell.SILENCERS == ("plus_spam", "scam")
    assert "varto_rule" not in reader_cell.SILENCERS
    assert RECORD["silencers"]["varto_rule"]["active"] is False


def test_the_thread_count_alone_could_not_have_identified_this_cell():
    """The reason the payable number is the discriminator, measured rather than asserted: this cell
    and `narrow|silencers_off` keep the SAME 129 threads, because plus_spam and scam remove comments
    and in this window never take a thread's last lexicon hit. A record that reported only «129»
    would be indistinguishable from a cell with the silencers off
    ([[a_new_gate_can_subsume_the_old_one]])."""
    off = SHIPPED["grid"]["narrow|silencers_off"]
    assert RECORD["measured"]["threads"] == off["threads"] == 129
    assert RECORD["measured"]["comments_payable"] == 1032
    assert off["comments_payable"] == 1116
    assert RECORD["measured"]["comments_payable"] < off["comments_payable"]
    # and the difference IS what the two silencers took out of the kept threads
    silenced = RECORD["measured"]["comments_silenced_window_wide"]
    assert set(silenced) == {"plus_spam", "scam"}
    assert (
        str(off["comments_payable"] - RECORD["measured"]["comments_payable"])
        in (RECORD["beside_the_shipped_grid"]["the_thread_count_alone_cannot_identify_this_cell"])
    )


def test_the_operators_expectation_is_carried_beside_the_measurement_and_not_as_it():
    expectation = RECORD["expectation"]
    assert expectation["threads"] == reader_cell.EXPECTED_THREADS == 129
    assert expectation["agrees"] is (RECORD["measured"]["threads"] == expectation["threads"])
    assert "never as the source of the number" in expectation["reading"]


def test_the_price_is_probe_bs_measured_rate_re_summed_from_its_own_rows():
    """`gate_census_w1.price()` reads an L4-era per-COMMENT rate from a different job, and this cell
    is priced on the only pass this repo owns that measured the reader's actual job. The two rates
    are re-derived here from the evidence rather than compared against a literal
    ([[a_price_is_as_representative_as_its_sample]])."""
    rows = [
        json.loads(line)
        for line in reader_cell.PROBE_B_EVIDENCE.read_text(encoding="utf-8").splitlines()
        if line
    ]
    worker = sum(row["seconds"]["worker"] for row in rows)
    payable_read = sum(row["payable_comments"] for row in rows)
    money = RECORD["price"]
    assert money["seconds_per_thread"] == round(worker / len(rows), 4)
    assert money["seconds_per_payable_comment"] == round(worker / payable_read, 4)
    assert f"{len(rows)} threads and {payable_read} payable comments" in money["sample"]
    assert "RTX 4090" in money["sample"]

    threads = RECORD["measured"]["threads"]
    payable = RECORD["measured"]["comments_payable"]
    rate = money["rate_usd_per_second"]
    assert money["by_thread"]["usd"] == round(threads * money["seconds_per_thread"] * rate, 4)
    assert money["by_payable_comment"]["usd"] == round(
        payable * money["seconds_per_payable_comment"] * rate, 4
    )
    assert money["binding_usd"] == max(
        money["by_thread"]["usd"], money["by_payable_comment"]["usd"]
    )
    assert money["binding"] == "by_payable_comment"
    # the L4 rate this producer refused to inherit
    l4 = json.loads(census.PRICES.read_text(encoding="utf-8"))
    assert money["seconds_per_thread"] != l4["timing"]["seconds_per_row"]


def test_the_shipped_census_is_quoted_and_never_rewritten():
    quoted = RECORD["beside_the_shipped_grid"]
    assert quoted["record"] == "results/gate_census_w1.json"
    assert quoted["sha256"] == summary.sha256_of(reader_cell.SHIPPED)
    for name in ("narrow|silencers_off", "narrow|silencers_on"):
        assert quoted[name]["threads"] == SHIPPED["grid"][name]["threads"]
        assert quoted[name]["comments_payable"] == SHIPPED["grid"][name]["comments_payable"]
    assert (
        quoted["varto_rule_alone"] == SHIPPED["silencer_decomposition"]["each_alone"]["varto_rule"]
    )


def test_the_output_ceiling_risk_is_reported_with_the_numbers_that_make_it_one():
    """v3 asks for a `per_comment` row for EVERY comment shown, so output length now scales with the
    thread's payable count. The probe cannot reach the ceiling and a window pass might — that is a
    reported risk with two measured numbers, not a worry ([[the_transport_fixes_the_job_shape]])."""
    from market_pulse import local_llm

    risk = RECORD["reported_risk"]
    assert risk["probe_population_max_payable"] == 15
    assert risk["this_cell_max_payable"] == RECORD["population"]["payable_per_thread"]["max"] == 125
    assert str(local_llm.READER_MAX_NEW_TOKENS) in risk["ceiling"]
    assert risk["this_cell_max_payable"] > risk["probe_population_max_payable"]
    assert "WINDOW risk and not a probe risk" in risk["measured_so_far"]
