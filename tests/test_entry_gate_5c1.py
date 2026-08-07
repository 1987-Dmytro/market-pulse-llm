"""Offline tests for the Phase-5c1 track-R entry gate — no Telegram, no session.

The gate decides which of the operator's 62 chosen channels reach `config/registry.yaml`, so
every rule it applies is tested against the case it exists for. Two of them are the reason this
file is long: "dead" is canon's own conjunction rather than a rate test (eight launch channels
sit at 0.2-0.5 posts/week, where zero posts in 28 days is the EXPECTED reading), and the
language check keys on script presence rather than on `langid.detect`, whose `other` bucket
holds both "no letters" and "Cyrillic, ua/ru tied".
"""

import asyncio
import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from telethon.errors import FloodWaitError

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import entry_check as gate  # noqa: E402

from market_pulse.entry_check import gate_verdict, script_mix  # noqa: E402

CANON = REPO_ROOT / "docs" / "CHANNELS-launch.md"


# --- the composition is the operator's, not the script's ---------------------------------------


def canon_buckets() -> list[tuple[str, str]]:
    """`docs/CHANNELS-launch.md`'s tables as (handle, bucket) rows, in the canon's own order."""
    text = CANON.read_text(encoding="utf-8")
    sections = [
        ("comments", "## Запуск, посты+комменты — 29", "## Запуск, только посты — 18"),
        ("posts", "## Запуск, только посты — 18", "## Watch — 14"),
        ("watch", "## Watch — 14", "## Исключены — 12"),
        ("late", "## Дозаявка оператора", "Куст сети"),
    ]
    rows = []
    for bucket, start, end in sections:
        i = text.index(start)
        for line in text[i : text.index(end, i)].splitlines():
            if not line.startswith("|"):
                continue
            found = [
                c.strip() for c in line.split("|") if re.fullmatch(r"@[A-Za-z0-9_]+", c.strip())
            ]
            rows += [(handle, bucket) for handle in found]
    return rows


def canon_sent_to_the_gate() -> list[str]:
    """Handles the canon sends to the gate in sections written after the four bucket tables.

    The operator amends `docs/CHANNELS-launch.md` rather than rewriting it: the tables still hold
    all 62, and each later section rules on them or adds to them. A row whose first cell is a
    handle and whose action says "на гейт" is a candidate the tables never carried — the
    replacement of 2026-08-07 and the second late batch of that evening both arrive this way.

    Matched case-insensitively and in document order, so a new section needs no code change. The
    Хвилинка row of "Дозаявка №2" also says "на гейт" and is correctly not matched: its first
    cell is a chain's name, not a handle, because nobody knew a handle to write.
    """
    text = CANON.read_text(encoding="utf-8")
    section = text[text.index("## Рулинги гейта 5c1") :]
    found = []
    for line in section.splitlines():
        if not line.startswith("|") or "на гейт" not in line.casefold():
            continue
        first = line.split("|")[1].strip()
        if re.fullmatch(r"@[A-Za-z0-9_]+", first):
            found.append(first)
    return found


def canon_city_feeds() -> list[str]:
    """The city feeds "Дозаявка №3" sends to the gate, read out of its prose list.

    That section writes its picks as a sentence — «16 хендлов на гейт: @a · @b · …» — not as a
    table, so `canon_sent_to_the_gate` above cannot see them. Parsing the prose rather than
    retyping the handles is the point: a hardcoded list here would pass while the canon said
    something else, which is the failure this whole derivation exists to prevent.
    """
    text = CANON.read_text(encoding="utf-8")
    section = text[text.index("## Дозаявка №3") :]
    listing = section[section.index("хендлов на гейт:") :]
    return re.findall(r"@[A-Za-z0-9_]+", listing.split("\n\n")[0])


def canon_retail_5() -> list[str]:
    """The national chains "Дозаявка №5" sends to the gate, read out of the master list.

    Its paragraph runs straight into the next bold heading with no blank line between, so the
    listing ends at the next `**` and NOT at the next empty line: cutting on the blank line
    swallows the following sentence, whose @NovusNews is a channel the canon explicitly does not
    send to the gate.
    """
    text = CANON.read_text(encoding="utf-8")
    section = text[text.index("## МАСТЕР-ЛИСТ") :]
    listing = section[section.index("Дозаявка №5 на гейт:") :]
    return re.findall(r"@[A-Za-z0-9_]+", listing[: listing.index("\n**")])


def test_the_retail_addition_is_the_canons_own_and_carries_no_more_than_it_says():
    """Three handles, and the corporate channel named in the very next sentence is not one."""
    picks = canon_retail_5()
    assert picks == ["@forainfo", "@ekomarket_shop", "@tadaua"], picks
    assert "@NovusNews" not in picks
    assert [handle for handle, _ in gate.CANDIDATES[-3:]] == picks


def test_the_retail_addition_is_gated_late_not_posts():
    """The operator's word is "comments per the group finding" — `late` is the bucket that asserts
    neither, and `posts` would flag any of the three that turns out to have a group."""
    buckets = {handle: bucket for handle, bucket in gate.CANDIDATES}
    assert {buckets[handle] for handle in canon_retail_5()} == {"late"}
    assert gate.BUCKETS["late"]["group_expected"] is None


def test_only_narrows_the_loop_and_refuses_a_handle_the_gate_does_not_carry():
    """The batches are sequenced by the operator, and one gate pass over two of them merges their
    rulings: `final_bucket` refuses the whole apply run over a single unruled FLAG."""
    pending = [(handle, bucket) for handle, bucket in gate.CANDIDATES]
    assert gate.gate_todo(pending, None) == pending
    assert gate.gate_todo(pending, ["@forainfo", "@tadaua"]) == [
        ("@forainfo", "late"),
        ("@tadaua", "late"),
    ]
    with pytest.raises(SystemExit, match="@nosuchchannel"):
        gate.gate_todo(pending, ["@nosuchchannel"])


def test_the_city_feeds_are_the_canons_own_and_all_of_them():
    """The canon states its own count in the same sentence; if the two disagree the canon is
    wrong about itself and nothing should be gated on it."""
    picks = canon_city_feeds()
    assert len(picks) == 16, picks
    assert len(set(picks)) == 16, "a handle is listed twice"
    assert list(picks) == list(apply_rulings_city_feeds()), "the routing table drifted"


def apply_rulings_city_feeds():
    """`CITY_FEEDS` decides the registry bucket, so it has to be the same 16 in the same order."""
    import apply_gate_rulings_5c1 as apply

    return apply.CITY_FEEDS


def test_the_candidate_list_is_the_canons_own():
    """A hand-copied handle list is a list that silently stops matching the file it came from.

    Not a set comparison: the bucket is what the gate holds each channel to, so a channel in the
    right list and the wrong bucket would be verified against expectations nobody chose. The
    gate's input only grows — a channel the operator later excluded was still measured, and
    deleting its row would rewrite what the pass found.
    """
    late = [(handle, "late") for handle in canon_sent_to_the_gate()]
    city = [(handle, "city") for handle in canon_city_feeds()]
    retail = [(handle, "late") for handle in canon_retail_5()]
    assert list(gate.CANDIDATES) == canon_buckets() + late + city + retail


def test_the_composition_is_the_62_plus_what_the_rulings_added():
    counts = {
        b: sum(1 for _, bucket in gate.CANDIDATES if bucket == b)
        for b in ("comments", "posts", "watch", "late", "city")
    }
    # + the withdrawn "Дозаявка оператора" row, + the three national chains of "Дозаявка №5"
    late = len(canon_sent_to_the_gate()) + 1 + len(canon_retail_5())
    city = len(canon_city_feeds())
    assert counts == {"comments": 29, "posts": 18, "watch": 14, "late": late, "city": city}
    assert len(gate.CANDIDATES) == 62 + len(canon_sent_to_the_gate()) + city + len(canon_retail_5())
    assert len({handle for handle, _ in gate.CANDIDATES}) == len(gate.CANDIDATES)


def test_the_gate_never_re_checks_a_registry_channel_or_an_excluded_one():
    """The four registry channels passed the 27.07 check and are out of scope; the 12 the
    operator excluded must not walk back in through the candidate list."""
    text = CANON.read_text(encoding="utf-8")
    out_of_scope = set(
        re.findall(
            r"@[A-Za-z0-9_]+", text[text.index("## Реестр — 4") : text.index("## Запуск, посты")]
        )
    )
    out_of_scope |= set(
        re.findall(
            r"@[A-Za-z0-9_]+", text[text.index("## Исключены — 12") : text.index("Особая строка")]
        )
    )
    assert out_of_scope & {handle for handle, _ in gate.CANDIDATES} == set()


# --- helpers -----------------------------------------------------------------------------------


def channel(*, group=True, open_group=True, scam=False, fake=False, broadcast=True, comments=0.4):
    facts = {
        "resolved": True,
        "title": "t",
        "broadcast": broadcast,
        "megagroup": not broadcast,
        "scam": scam,
        "fake": fake,
        "comments_enabled": group,
        "discussion_group": (
            {
                "present": True,
                "read": True,
                "open": open_group,
                "closed_because": [] if open_group else ["join needs admin approval"],
                "min": False,
            }
            if group
            else None
        ),
        "traffic": {"n_posts": 50, "share_with_comments": comments, "median_comments": 3},
    }
    return facts


def window(n_posts=20):
    return {"n_posts": n_posts, "posts_per_week": round(n_posts / 4, 2), "window_days": 28}


def verdict_of(handle="@x", bucket="comments", *, record=None, posts=20, texts=None):
    texts = ["Дякую, дуже смачно"] * 20 if texts is None else texts
    return gate_verdict(
        handle=handle,
        bucket=bucket,
        record=channel() if record is None else record,
        window=window(posts),
        script=script_mix(texts),
    )


# --- the city bucket measures a group without asserting one -------------------------------------


def test_a_city_feed_is_not_flagged_for_the_group_the_ruling_already_accounted_for():
    """11 of the 16 picks carry a linked group, and the standing ruling puts them in posts-only
    anyway — the join is what 5c2 defers, not the group's existence. Held to `posts` the gate
    would raise that flag against 11 channels; the negative control is the same record in the
    `posts` bucket, which must still raise it, or this proves nothing about the bucket."""
    city = verdict_of(bucket="city", record=channel(group=True))
    assert city["verdict"] == "PASS"
    assert not any("posts-only bucket" in flag for flag in city["flags"])

    posts = verdict_of(bucket="posts", record=channel(group=True))
    assert any("posts-only bucket" in flag for flag in posts["flags"]), "the control does not fire"


def test_a_city_feed_still_answers_every_other_check():
    """ "Same checks" is the operator's instruction: only the bucket's group expectation moves."""
    assert verdict_of(bucket="city", record={"resolved": False, "error": "x"})["verdict"] == "FAIL"
    assert verdict_of(bucket="city", record=channel(scam=True))["verdict"] == "FAIL"
    assert verdict_of(bucket="city", posts=0, record=channel(group=False))["verdict"] == "FAIL"
    latin = verdict_of(bucket="city", texts=["Guten Morgen"] * 20)
    assert latin["verdict"] == "FAIL"


def test_a_silent_city_feed_with_a_group_takes_the_watch_shape_flag():
    """@LHVC_info's shape: 0.2 posts/week and last seen 2026-07-20, so a 28-day window opened on
    08.08 can hold zero of its posts. With a group that is a FLAG, not a FAIL, and it is a finding
    about the channel — the operator's "FLAG → report with evidence" covers it."""
    out = verdict_of(bucket="city", posts=0, record=channel(group=True))
    assert out["verdict"] == "FLAG"
    assert any("watch shape" in flag for flag in out["flags"])


# --- FAIL is a closed list ---------------------------------------------------------------------


def test_a_handle_that_does_not_resolve_fails():
    out = verdict_of(record={"resolved": False, "error": "UsernameNotOccupiedError: nobody"})
    assert out["verdict"] == "FAIL"
    assert "does not resolve" in out["fails"][0]


def test_telegrams_scam_mark_is_mapped_onto_fail():
    """Outside the brief's three FAIL reasons, so the mapping is explicit here and named in the
    record's `rules` block — a channel Telegram flags may not enter the registry by silence."""
    out = verdict_of(record=channel(scam=True))
    assert out["verdict"] == "FAIL"
    assert out["fails"] == ["Telegram flags this channel as scam"]


def test_a_latin_script_channel_fails_the_language_check():
    """@MAMIPEKER1's shape — the one true positive control in the 06.08 scan: 150 texts, no
    Cyrillic at all. Excluded by the operator as a Turkish channel."""
    out = verdict_of(texts=["Merhaba, bugun cok guzel bir tarif"] * 30)
    assert out["verdict"] == "FAIL"
    assert "non-UA/RU dominant" in out["fails"][0]
    assert "cyrillic_share 0.0" in out["fails"][0]


def test_short_cyrillic_posts_are_not_a_language_failure():
    """@Wellosophy_Lesya's shape: `langid.detect` calls half of these `other` (Cyrillic with no
    distinctive letter), which a detect-based threshold would read as non-UA/RU. They are UA."""
    texts = [
        "Дякую",
        "Смачно",
        "Так",
        "Гарно",
        "Дуже",
        "Добре",
        "Клас",
        "Супер",
        "Ок",
        "Так!",
        "Ага",
    ]
    mix = script_mix(texts)
    assert mix["cyrillic_share"] == 1.0
    assert verdict_of(texts=texts)["verdict"] == "PASS"


def test_a_language_share_under_the_minimum_sample_is_a_flag_not_a_fail():
    """Five Latin posts cannot carry a verdict — the operator gets the question, not the ruling."""
    out = verdict_of(texts=["Hello there friends"] * 5)
    assert out["verdict"] == "FLAG"
    assert any("not decisive" in flag for flag in out["flags"])
    assert out["fails"] == []


def test_a_channel_with_no_text_at_all_is_not_a_language_failure():
    """No posts means no language evidence. Silence is judged by the dead rule, not this one."""
    out = verdict_of(bucket="watch", posts=0, texts=[])
    assert out["verdict"] == "PASS"


# --- "dead" is canon's conjunction, not a rate test ---------------------------------------------


def test_silence_with_no_group_is_dead():
    """docs/CHANNELS-launch.md excluded six channels on exactly this pair of facts."""
    out = verdict_of(bucket="posts", record=channel(group=False), posts=0, texts=[])
    assert out["verdict"] == "FAIL"
    assert out["fails"] == ["dead against its bucket — no posts in 28 days and no discussion group"]


def test_silence_with_a_group_is_a_flag_not_a_fail():
    """The rule that protects eight operator-chosen channels. @tretyakovaele, @baby_broccoli_club,
    @eftforhealth, @intensiv_Mamiev, @anastasiiadavydiukfitness are canon 0.2/week — ONE post in
    the 28-day window of 06.08. A day later that post can age out, and a rate test would FAIL
    five channels the operator picked, on noise."""
    out = verdict_of(bucket="comments", posts=0, texts=[])
    assert out["verdict"] == "FLAG"
    assert out["fails"] == []
    assert any("watch shape" in flag for flag in out["flags"])


def test_a_watch_channel_is_expected_to_be_silent():
    """All fourteen were chosen BECAUSE they are silent (canon: 0 posts/week, group present)."""
    assert verdict_of(bucket="watch", posts=0, texts=[])["verdict"] == "PASS"


def test_a_watch_channel_that_posts_again_is_flagged():
    """SPEC 3.11 (4) holds the watch joins until the channel posts again — so that is the
    operator's decision, and the gate hands it over instead of taking it."""
    out = verdict_of(bucket="watch", posts=12)
    assert out["verdict"] == "FLAG"
    assert any("watch bucket expects silence" in flag for flag in out["flags"])


# --- evidence that contradicts the bucket --------------------------------------------------------


def test_a_comments_bucket_channel_without_a_group_is_flagged():
    """The brief's own example. Deliverable 2 would join a group that is not there."""
    out = verdict_of(bucket="comments", record=channel(group=False))
    assert out["verdict"] == "FLAG"
    assert "bucket expects a discussion group, none is linked" in out["flags"]


def test_a_posts_only_channel_that_has_a_group_is_flagged():
    """The upgrade case: a join is authorised per bucket, so a bucket change is a ruling."""
    out = verdict_of(bucket="posts", record=channel(group=True))
    assert out["verdict"] == "FLAG"
    assert "posts-only bucket, but a discussion group is linked" in out["flags"]


def test_a_group_that_is_not_open_is_flagged():
    out = verdict_of(bucket="comments", record=channel(open_group=False))
    assert out["verdict"] == "FLAG"
    assert any("not open" in flag and "admin approval" in flag for flag in out["flags"])


def test_a_comments_channel_whose_posts_carry_no_comments_is_flagged():
    out = verdict_of(bucket="comments", record=channel(comments=0.0))
    assert out["verdict"] == "FLAG"
    assert "group present but no comments on any of the sampled posts" in out["flags"]


def test_a_supergroup_where_a_channel_was_expected_is_flagged():
    out = verdict_of(bucket="posts", record=channel(group=False, broadcast=False))
    assert "supergroup, not a broadcast channel" in out["flags"]


def test_the_three_pre_registered_flags_fire_whatever_the_measurement_says():
    """The operator named these three; a clean measurement does not clear them."""
    for handle, bucket in (
        ("@kolyastravinsky", "comments"),
        ("@whowears", "comments"),
        ("@marketopt_official", "late"),
    ):
        out = verdict_of(handle, bucket)
        assert out["verdict"] == "FLAG", handle
        assert any("pre-registered" in flag for flag in out["flags"]), handle


def test_a_clean_channel_in_its_bucket_passes():
    """The negative control: without it, a rule set that flags everything would look strict."""
    assert verdict_of("@ordinary", "comments")["verdict"] == "PASS"
    assert verdict_of("@ordinary", "posts", record=channel(group=False))["verdict"] == "PASS"


# --- the discussion group, read without joining ---------------------------------------------------


def chat(**flags):
    base = dict(
        id=777,
        title="g",
        username="g",
        megagroup=True,
        min=False,
        join_request=False,
        join_to_send=True,
        restricted=False,
        left=True,
        participants_count=100,
        default_banned_rights=SimpleNamespace(send_messages=False),
    )
    return SimpleNamespace(**{**base, **flags})


def test_group_facts_read_openness_off_the_linked_chat():
    facts = gate.group_facts([chat()], 777)
    assert facts["open"] is True and facts["closed_because"] == []
    assert facts["already_member"] is False and facts["join_to_send"] is True


def test_every_way_a_group_can_be_closed_to_the_join():
    assert gate.group_facts([chat(join_request=True)], 777)["closed_because"] == [
        "join needs admin approval"
    ]
    assert gate.group_facts([chat(restricted=True)], 777)["closed_because"] == [
        "Telegram-restricted"
    ]
    banned = chat(default_banned_rights=SimpleNamespace(send_messages=True))
    assert gate.group_facts([banned], 777)["closed_because"] == ["everyone banned from sending"]


def test_a_group_telegram_did_not_return_is_recorded_as_unread():
    """`open: None` is not `open: False` — nothing was measured, and the record says so."""
    facts = gate.group_facts([chat(id=1)], 777)
    assert facts == {
        "present": True,
        "read": False,
        "open": None,
        "closed_because": ["not returned"],
    }


def test_a_min_object_is_recorded_rather_than_read_as_false():
    facts = gate.group_facts([chat(min=True)], 777)
    assert facts["min"] is True
    out = verdict_of(record={**channel(), "discussion_group": facts})
    assert any("min object" in flag for flag in out["flags"])


# --- the run, driven to the written record ----------------------------------------------------


class FakeClient:
    """Enough Telethon for `run_gate` to walk its loop. Nothing here reaches the network."""

    async def connect(self):
        pass

    async def is_user_authorized(self):
        return True

    async def disconnect(self):
        pass

    async def get_entity(self, handle):
        return SimpleNamespace(username=handle.lstrip("@"))


def drive(monkeypatch, tmp_path, candidates, *, blow_up_on=lambda handle: None, prior=None):
    """Run the gate over `candidates` with a stubbed client, returning the record it wrote."""
    import discover_channels as discovery

    record_path = tmp_path / "entry_gate_5c1.json"
    monkeypatch.setattr(gate, "GATE_RECORD", record_path)
    monkeypatch.setattr(gate, "PRIOR_SCAN", tmp_path / (prior or "absent.json"))
    monkeypatch.setattr(gate, "CANDIDATES", tuple(candidates))
    monkeypatch.setattr(gate, "PAUSE_SECONDS", 0)
    monkeypatch.setattr(gate, "build_client", lambda *a, **k: FakeClient())

    checked = []

    async def check(_client, _source, handle):
        checked.append(handle)
        if (exc := blow_up_on(handle)) is not None:
            raise exc
        return {"handle": handle, **channel()}

    async def sample(_client, _entity, _now):
        return [], ["Дуже смачно, дякую"] * 20, False

    monkeypatch.setattr(gate, "check_channel", check)
    monkeypatch.setattr(discovery, "window_sample", sample)
    monkeypatch.setattr(discovery, "window_stats", lambda *a, **k: window(20))

    code = asyncio.run(gate.run_gate())
    return code, json.loads(record_path.read_text(encoding="utf-8")), checked


def test_the_gate_writes_its_record_and_stops_before_the_registry(monkeypatch, tmp_path):
    """The write path end to end: an import proves nothing and a verdict in prose is not a gate."""
    code, record, checked = drive(
        monkeypatch, tmp_path, [("@a", "comments"), ("@b", "posts"), ("@c", "watch")]
    )

    assert code == 0
    assert checked == ["@a", "@b", "@c"]
    assert [row["handle"] for row in record["candidates"]] == ["@a", "@b", "@c"]
    assert record["summary"]["n"] == 3
    assert record["summary"]["FLAG"] == 2  # @b has a group it should not; @c posts while watched
    assert record["registry_written"] is False
    assert record["read_only"].startswith("no group joins")
    assert record["git"]["commit"]
    assert record["rules"]["fail_is_a_closed_list"]
    assert record["candidates"][0]["ruling"] is None
    assert record["candidates"][0]["checks"]["language"]["cyrillic_share"] == 1.0


def test_a_floodwait_stops_the_gate_and_the_re_run_resumes(monkeypatch, tmp_path):
    """A rate limit is a wait, not a verdict — and 62 channels is too many to re-resolve."""
    handles = [("@a", "comments"), ("@b", "comments"), ("@c", "comments")]
    code, record, checked = drive(
        monkeypatch,
        tmp_path,
        handles,
        blow_up_on=lambda h: FloodWaitError(request=None, capture=42) if h == "@b" else None,
    )
    assert code == 1
    assert record["flood_wait_seconds"] == 42
    assert record["complete"] is False
    assert [row["handle"] for row in record["candidates"]] == ["@a"]
    assert checked == ["@a", "@b"], "the gate kept hammering after the wait"

    _, resumed, checked_again = drive(monkeypatch, tmp_path, handles)
    assert checked_again == ["@b", "@c"], "a resume must not re-resolve what is already recorded"
    assert [row["handle"] for row in resumed["candidates"]] == ["@a", "@b", "@c"]
    assert resumed["complete"] is True


def test_gating_a_later_candidate_does_not_un_say_the_rulings(monkeypatch, tmp_path):
    """The interaction that stopped a live collection. Adding one late candidate re-ran the gate,
    which rewrote the record with a fresh `registry_written: false` — so the collector refused to
    collect, correctly, on a fact that had stopped being true. The rulings and the search notes
    went the same way. State the gate does not own is carried, not reset.
    """
    handles = [("@a", "comments")]
    _, first, _ = drive(monkeypatch, tmp_path, handles)
    assert first["registry_written"] is False, "a first gate run has none of this yet"

    record_path = tmp_path / "entry_gate_5c1.json"
    ruled = {
        **first,
        "registry_written": True,
        "rulings": {"counts": {"comments": 1}},
        "notes": {"hvylynka_search": {"closed": True}},
    }
    record_path.write_text(json.dumps(ruled, ensure_ascii=False), encoding="utf-8")

    _, after, checked = drive(monkeypatch, tmp_path, [*handles, ("@b", "comments")])
    assert checked == ["@b"], "the resume still only measures what is new"
    assert after["registry_written"] is True
    assert after["rulings"] == {"counts": {"comments": 1}}
    assert after["notes"] == {"hvylynka_search": {"closed": True}}


def test_a_batch_of_new_candidates_leaves_every_earlier_rows_ruling_alone(monkeypatch, tmp_path):
    """ "Дозаявка №3" appends 16 rows at once, and the carry-forward has only ever been exercised
    on one. A row's `ruling` and its `replaced` history are written by a later stage, so the
    rebuild must return them untouched — a reversal that a re-gate erased would be unrecoverable
    from anything but git."""
    held = [("@a", "comments"), ("@b", "posts")]
    _, first, _ = drive(monkeypatch, tmp_path, held)

    annotated = {**first, "registry_written": True}
    annotated["candidates"][0]["ruling"] = "EXCLUDED — off theme"
    annotated["candidates"][0]["replaced"] = [{"at": "2026-08-07T11:14:29+00:00", "ruling": "KEPT"}]
    annotated["candidates"][1]["ruling"] = "KEPT — measured"
    (tmp_path / "entry_gate_5c1.json").write_text(
        json.dumps(annotated, ensure_ascii=False), encoding="utf-8"
    )

    city = [(f"@city{i}", "city") for i in range(16)]
    _, after, checked = drive(monkeypatch, tmp_path, held + city)

    assert checked == [handle for handle, _ in city], "an earlier row was re-resolved"
    assert len(after["candidates"]) == 18
    kept = {row["handle"]: row for row in after["candidates"]}
    assert kept["@a"]["ruling"] == "EXCLUDED — off theme"
    assert kept["@a"]["replaced"] == [{"at": "2026-08-07T11:14:29+00:00", "ruling": "KEPT"}]
    assert kept["@b"]["ruling"] == "KEPT — measured"
    assert after["registry_written"] is True
    assert {row["bucket"] for row in after["candidates"] if row["handle"].startswith("@city")} == {
        "city"
    }
    assert after["summary"]["by_bucket"]["city"]["n"] == 16


def test_an_ordinary_failure_is_one_retryable_row_and_not_an_abort(monkeypatch, tmp_path):
    """The negative control for the FloodWait branch: only a rate limit stops the pass, and an
    ERROR row is not a verdict — the resume picks it up again."""
    handles = [("@a", "comments"), ("@b", "comments")]
    _, record, _ = drive(
        monkeypatch,
        tmp_path,
        handles,
        blow_up_on=lambda h: RuntimeError("boom") if h == "@b" else None,
    )
    assert [row["verdict"] for row in record["candidates"]] == ["PASS", "ERROR"]
    assert record["complete"] is False

    _, resumed, checked_again = drive(monkeypatch, tmp_path, handles)
    assert checked_again == ["@b"]
    assert [row["verdict"] for row in resumed["candidates"]] == ["PASS", "PASS"]
