"""Offline tests for the 5c1 addendum — no Telegram, no session.

Two things here can quietly destroy a result: a re-run of the search overwriting the human
judgement that closed the Хвилинка question, and a scan ledger that counts a channel nobody can
collect from. Both are what these tests are about.
"""

import json
import sys
from pathlib import Path

import pytest
from telethon.errors import FloodWaitError

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import late_batch_5c1 as late  # noqa: E402

CANON = REPO_ROOT / "docs" / "CHANNELS-launch.md"


def match(username, title="Хвилинка"):
    return {"username": username, "title": title, "telegram_verified": False, "subscribers": 1}


def found_with(*usernames):
    rows = [match(name) for name in usernames]
    return {"queries": list(late.HVYLYNKA_QUERIES), "results": {"q": rows}, "name_matches": rows}


def gate_record(tmp_path, note=None):
    path = tmp_path / "entry_gate_5c1.json"
    body = {"candidates": [], "notes": {"hvylynka_search": note}} if note else {"candidates": []}
    path.write_text(json.dumps(body, ensure_ascii=False), encoding="utf-8")
    return path


# --- the towns and the queries are the canon's ---------------------------------------------------


def test_the_scanned_towns_are_the_canons_own():
    """ "only these towns were searched" has to be checkable, not trusted."""
    section = CANON.read_text(encoding="utf-8")
    section = section[section.index("## Дозаявка №2") :]
    for city in late.CITIES:
        assert city in section, city
    assert len(late.CITIES) == 16


def test_the_search_queries_are_the_canons_own():
    section = CANON.read_text(encoding="utf-8")
    section = section[section.index("## Дозаявка №2") :]
    for query in late.HVYLYNKA_QUERIES:
        assert query in section, query


def canon_brands() -> list[str]:
    """The chains the master list sends to a Telegram-side check, read out of its own sentence.

    «Проверить внутри Telegram (вебом не найдено): потребительские каналы Novus (…), Velmart,
    Fozzy C&C, Auchan (…), METRO.» — the parentheticals say what the web pass found and are
    stripped, because they are evidence about a brand, not another brand.
    """
    import re

    text = CANON.read_text(encoding="utf-8")
    block = text[text.index("Проверить внутри Telegram") :]
    block = block[block.index(":**") + 3 : block.index("\n**")]
    block = re.sub(r"\([^)]*\)", "", " ".join(block.split())).replace("потребительские каналы", "")
    return [brand.strip(" .") for brand in block.split(",")]


def test_the_searched_brands_are_the_canons_own_in_its_own_order():
    """Five chains, five notes. A brand quietly dropped here is a question that reads as unasked
    rather than as answered — which is the whole reason a negative gets recorded at all."""
    brands = canon_brands()
    assert brands == ["Novus", "Velmart", "Fozzy C&C", "Auchan", "METRO"], brands
    subjects = [spec["subject"] for spec in late.RETAIL_SEARCHES.values()]
    assert len(subjects) == len(brands)
    for subject, brand in zip(subjects, brands, strict=True):
        assert subject.startswith(brand), (subject, brand)


def test_every_query_is_caught_by_the_markers_of_its_own_search():
    """A marker that does not match the query it was written for silently turns every hit into a
    non-match, and the search then reports a clean negative on a chain it did find."""
    for key, spec in late.SEARCHES.items():
        for query in spec["queries"]:
            assert any(marker in query.casefold() for marker in spec["markers"]), (key, query)


# --- the judgement survives a re-run ---------------------------------------------------------------


def test_a_re_run_of_the_search_does_not_reopen_a_closed_question(tmp_path, monkeypatch):
    """The failure this exists for: someone re-runs --search, the name markers match the same
    unrelated channels again, and a human's "none of these is the chain" is silently gone."""
    judged = {
        "name_matches": [match("khvylynka"), match("englishbrend")],
        "judgement": late.HVYLYNKA_JUDGEMENT,
        "closed": True,
    }
    monkeypatch.setattr(late, "GATE_RECORD", gate_record(tmp_path, judged))

    note = late.record_search("hvylynka_search", found_with("englishbrend", "khvylynka"))
    assert note["closed"] is True
    assert note["judgement"] == late.HVYLYNKA_JUDGEMENT
    assert note["judgement_stale"] is False
    assert note["finding"].startswith("NEGATIVE")


def test_a_judgement_about_different_rows_reopens_instead_of_standing(tmp_path, monkeypatch):
    """A carried judgement is only worth carrying while it is about the rows in front of it."""
    judged = {
        "name_matches": [match("khvylynka")],
        "judgement": late.HVYLYNKA_JUDGEMENT,
        "closed": True,
    }
    monkeypatch.setattr(late, "GATE_RECORD", gate_record(tmp_path, judged))

    note = late.record_search("hvylynka_search", found_with("khvylynka", "hvylynka_nova_merezha"))
    assert note["judgement_stale"] is True
    assert note["closed"] is False
    assert note["finding"].startswith("REOPENED")


def test_a_search_that_matched_nothing_closes_itself(tmp_path, monkeypatch):
    """The negative finding is the result. An absent note reads like an unasked question."""
    monkeypatch.setattr(late, "GATE_RECORD", gate_record(tmp_path))
    note = late.record_search(
        "hvylynka_search",
        {"queries": list(late.HVYLYNKA_QUERIES), "results": {"q": []}, "name_matches": []},
    )
    assert note["closed"] is True
    assert note["finding"].startswith("NEGATIVE")
    assert "does not prove absence" in note["finding"] or "not proven" in note["finding"]


def test_matches_with_no_judgement_stay_open(tmp_path, monkeypatch):
    """The script does not decide what is convincing — that is the whole point of --close."""
    monkeypatch.setattr(late, "GATE_RECORD", gate_record(tmp_path))
    note = late.record_search("hvylynka_search", found_with("khvylynka"))
    assert note["closed"] is False
    assert note["finding"].startswith("MATCHES FOUND")


def test_five_chains_asked_in_one_pass_are_five_findings(tmp_path, monkeypatch):
    """One note per question: a chain that turns up must not close the four that did not, and a
    chain that is absent must not be reopened by a hit on another."""
    monkeypatch.setattr(late, "GATE_RECORD", gate_record(tmp_path))
    novus = late.record_search(
        "novus_consumer_search",
        {"queries": ["Novus"], "results": {"Novus": []}, "name_matches": []},
    )
    hit = match("auchan_ua", title="Ашан Україна")
    auchan = late.record_search(
        "auchan_consumer_search",
        {"queries": ["Auchan"], "results": {"Auchan": [hit]}, "name_matches": [hit]},
    )

    assert novus["closed"] is True and novus["finding"].startswith("NEGATIVE")
    assert "Novus" in novus["finding"] and novus["asked"].startswith("does Novus")
    assert auchan["closed"] is False and auchan["finding"].startswith("MATCHES FOUND")

    notes = json.loads((tmp_path / "entry_gate_5c1.json").read_text(encoding="utf-8"))["notes"]
    assert set(notes) == {"novus_consumer_search", "auchan_consumer_search"}
    assert notes["novus_consumer_search"]["closed"] is True


def test_the_search_pass_stops_on_a_flood_wait_and_keeps_what_it_answered(tmp_path, monkeypatch):
    """Ten queries is the longest search pass of the phase, and a retry inside the window
    lengthens it. What was already asked is written; what was not is named."""
    monkeypatch.setattr(late, "GATE_RECORD", gate_record(tmp_path))
    monkeypatch.setattr(late, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(late.entry_check, "PAUSE_SECONDS", 0)
    asked = []

    async def suggest(client, query):
        asked.append(query)
        if len(asked) > 2:
            raise FloodWaitError(request=None)
        return []

    monkeypatch.setattr(late.entry_check, "suggest", suggest)
    monkeypatch.setattr(late, "build_client", lambda: FakeClient())

    assert late.main(["--search-retail"]) == 1
    notes = json.loads((tmp_path / "entry_gate_5c1.json").read_text(encoding="utf-8"))["notes"]
    assert set(notes) == {"novus_consumer_search"}, "only the completed search is recorded"
    assert len(asked) == 3, "the pass stopped at the refusal instead of walking into the next"


class FakeClient:
    """Enough of a Telethon client for the search pass: it never reaches the network because
    `entry_check.suggest` is the only thing that would, and that is stubbed."""

    async def connect(self):
        return None

    async def is_user_authorized(self):
        return True

    async def disconnect(self):
        return None


# --- the ledger ------------------------------------------------------------------------------------


def row(handle, *, subscribers, verdict="usable", ppw=1.0, group=True):
    return {
        "handle": handle,
        "title": handle,
        "subscribers": subscribers,
        "discussion_group": group,
        "posts_per_week": ppw,
        "verdict": verdict,
    }


def test_the_ledger_ranks_by_subscribers_and_runs_a_total():
    led = late.ledger([row("@a", subscribers=100), row("@b", subscribers=900)])
    assert [r["handle"] for r in led["ranked"]] == ["@b", "@a"]
    assert [r["cumulative_subscribers"] for r in led["ranked"]] == [900, 1000]
    assert led["subscribers_total"] == 1000


def test_a_channel_nothing_can_collect_from_adds_nothing():
    """`unresolved`, `rejected` and `error` rows are listed with the rest and counted in none of
    it: a pick list may not be inflated by a channel that cannot be collected."""
    led = late.ledger(
        [row("@dead", subscribers=5000, verdict="unresolved"), row("@ok", subscribers=10)]
    )
    assert led["candidates_found"] == 2
    assert led["candidates_counted"] == 1
    assert led["subscribers_total"] == 10


def test_the_ledger_splits_the_silent_channels_out():
    led = late.ledger(
        [row("@live", subscribers=10, ppw=3.0), row("@quiet", subscribers=90, ppw=0.0)]
    )
    assert led["live_in_the_window"] == 1 and led["silent_in_the_window"] == 1
    assert led["live_subscribers"] == 10
    assert led["subscribers_total"] == 100, "the total still counts both — the split is beside it"


def test_the_two_caveats_ride_with_the_ledger():
    """Summed subscribers != unique reach, and subscribers != comment flow. A pick list without
    them invites the operator to read a sum as an audience."""
    assert late.ledger([row("@a", subscribers=1)])["caveats"] == [
        "summed subscribers != unique reach",
        "subscribers != comment flow",
    ]


def test_handles_already_spoken_for_are_not_re_measured():
    """The registry and everything the gate already measured. Re-measuring spends rate limit on
    an answered question, and listing them invites a pick the operator already has."""
    known = late.known_handles()
    assert "@varus_channel" in known and known["@varus_channel"] == "registry"
    assert "@kolyastravinsky" in known, "an excluded channel must not come back through a scan"
    assert known["@kolyastravinsky"].startswith("gated 5c1")


def test_the_close_flag_needs_a_search_to_judge(tmp_path, monkeypatch):
    monkeypatch.setattr(late, "GATE_RECORD", gate_record(tmp_path))
    with pytest.raises(SystemExit, match="run --search first"):
        late.main(["--close-hvylynka"])


def test_the_food_quality_search_is_one_question_asked_five_ways():
    """Addendum 9 asks whether ONE channel exists, under five names. The retail five were five
    chains and therefore five notes; collapsing that distinction would let one match close four
    questions nobody answered, or five empty queries read as five separate negatives."""
    assert list(late.FOOD_QUALITY_SEARCH) == ["food_quality_search"]
    spec = late.FOOD_QUALITY_SEARCH["food_quality_search"]
    assert spec["queries"] == (
        "Макс Контроль",
        "MaxControl",
        "Несміянов",
        "Союз споживачів України",
        "фальсифікат",
    ), "the queries are the operator's own, in the order they were given"
    assert late.SEARCHES["food_quality_search"] is spec


def test_the_topic_marker_is_loose_on_purpose_and_the_name_markers_are_not():
    """«фальсифікат» matches any channel about counterfeit food, which is the point: a near miss
    is a human's call. The name markers must still catch the RU spelling of the surname, because a
    channel titled «Несмиянов» is the same person under a different transliteration."""
    markers = late.SEARCHES["food_quality_search"]["markers"]
    assert "фальсифікат" in markers
    assert {"несміянов", "несмиянов"} <= set(markers)
    assert "макс контроль" in markers and "maxcontrol" in markers
