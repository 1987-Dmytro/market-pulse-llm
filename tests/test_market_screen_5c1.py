"""Offline tests for the market-origin screen — no Telegram, no store writes.

The screen's whole risk is a term list: too loose and it calls a recipe an RF shop, too tight and
it certifies a market it never saw. So the fixtures are the four cases whose answer is already
known, the trap that made the rule, and the two mentions a Ukrainian channel makes about the war
rather than about a market.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import market_screen_5c1 as screen  # noqa: E402


# --- the rule ------------------------------------------------------------------------------------


def test_rf_evidence_outranks_ua_evidence_and_nothing_passes_silently():
    """SPEC §3.11 (4): RF-market channels are excluded regardless of language and ambiguity goes
    to the operator, so a source carrying both is flagged rather than averaged."""
    hit = [{"term": "x", "line": "y"}]
    assert screen.verdict_for(hit, []) == "RF_FLAG"
    assert screen.verdict_for(hit, hit) == "RF_FLAG"
    assert screen.verdict_for([], hit) == "UA_EVIDENCE"
    assert screen.verdict_for([], []) == "NO_EVIDENCE"


def test_every_hit_carries_the_line_it_came_from():
    """ "The evidence is a quoted line, never a counter" — a count cannot be checked by a human,
    and this screen's findings go to a sitting."""
    found = screen.hits_in("Ціна 250 грн у Сільпо\nдруга строка")
    assert found["rf"] == []
    assert {hit["term"] for hit in found["ua"]} == {"грн", "Сільпо"}
    for hit in found["ua"]:
        assert hit["line"] == "Ціна 250 грн у Сільпо"
        assert hit["matched"] in hit["line"]


# --- the trap that made the rule -------------------------------------------------------------------


def test_prosochivsya_is_not_sochi():
    """`grep -i "сочи"` matches «просочився» — *soaked through* — in three innocent recipe feeds.
    The word boundary is the whole difference, and this is the line it was found on."""
    assert screen.hits_in(screen.TRAP_LINE)["rf"] == []
    flagged = screen.hits_in("Мы с Миланой прилетели в Сочи, на Красную Поляну")["rf"]
    assert {hit["term"] for hit in flagged} == {"Сочи", "Красная Поляна"}


def test_a_war_mention_is_not_a_market_fact():
    """A Ukrainian channel writes «РФ» and «Росія» constantly, about the war. A screen that
    flagged those would answer a different question than the one SPEC asks — so the country's own
    name is deliberately not a signal, and this is the negative control for that choice."""
    assert screen.hits_in("Вночі війська РФ атакували Харків")["rf"] == []
    assert screen.hits_in("Росія знову обстріляла порт")["rf"] == []
    # And the concrete facts in the same sentence still count for the UA side.
    assert {hit["term"] for hit in screen.hits_in("Вночі війська РФ атакували Харків")["ua"]} == {
        "Харків"
    }


def test_a_cauldron_and_a_ribbon_do_not_flag():
    """Two RF retailer/city names that are ordinary words in a recipe. `Лента` is left out of the
    table entirely; `казан` was never in it. If either ever gets added, this reddens."""
    assert screen.hits_in("Викладіть м'ясо в казан і накрийте кришкою")["rf"] == []
    assert screen.hits_in("Перев'яжіть стрічкою — лента має бути широкою")["rf"] == []


# --- the four known controls, against the real store ------------------------------------------------


def test_the_four_controls_behave_and_the_screen_says_so_in_its_record():
    """The pre-registered exam: @offspringrus is an RF shop, @dpssgovua is the Ukrainian state
    service, and the two rows the operator cited at the sitting must flag on their own text."""
    record = json.loads((REPO_ROOT / "results" / "market_screen_5c1.json").read_text("utf-8"))
    controls = record["controls"]

    assert controls["@offspringrus"]["measured"] == "RF_FLAG"
    assert controls["@dpssgovua"]["measured"] == "UA_EVIDENCE"
    for name in ("@tretyakovaele :: Сочи", "@retsepty5 :: Яндекс"):
        assert controls[name]["rows_found"] >= 1, name
        assert controls[name]["evidence"], f"{name} found the row and no evidence in it"
    assert controls["negative control :: просочився"]["evidence"] == []
    assert all(control["ok"] for control in controls.values())
    assert record["verdicts_reportable"] is True
    assert record["report_only"].startswith("no exclusion")


def test_a_failed_control_makes_the_verdicts_unreportable(tmp_path, monkeypatch):
    """A screen that gets a known channel wrong cannot rule on unknown ones. The record is still
    written — the lines are the evidence for whatever went wrong — and the run exits non-zero."""
    monkeypatch.setattr(screen, "CONTROLS", {"@dpssgovua": "RF_FLAG"})  # it is the state service
    out = tmp_path / "screen.json"
    assert screen.main(["--out", str(out)]) == 1

    record = json.loads(out.read_text(encoding="utf-8"))
    assert record["verdicts_reportable"] is False
    assert record["controls"]["@dpssgovua"]["ok"] is False
    assert record["sources"], "the evidence still has to be written down"


def test_the_shipped_record_covers_the_live_registry_and_flags_nothing_yet(tmp_path):
    """Wave 3 removed the RF-market sources, so a clean sweep here is the expected shape — and it
    is only meaningful BECAUSE the controls fire on the excluded ones. A screen that flagged
    nothing and had no working control would be indistinguishable from a broken one."""
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from market_pulse.registry import load_registry

    record = json.loads((REPO_ROOT / "results" / "market_screen_5c1.json").read_text("utf-8"))
    live = {
        handle
        for s in load_registry(REPO_ROOT / "config" / "registry.yaml").sources
        for handle in s.telegram_channels
    }
    assert {row["handle"] for row in record["sources"]} == live
    assert record["summary"]["by_verdict"].get("RF_FLAG", 0) == 0


def test_only_narrows_the_sweep_and_refuses_a_handle_the_registry_lacks(tmp_path):
    out = tmp_path / "screen.json"
    assert screen.main(["--out", str(out), "--only", "@dpssgovua"]) == 0
    record = json.loads(out.read_text(encoding="utf-8"))
    assert [row["handle"] for row in record["sources"]] == ["@dpssgovua"]
    with pytest.raises(SystemExit, match="does not carry"):
        screen.main(["--out", str(out), "--only", "@nosuchchannel"])
