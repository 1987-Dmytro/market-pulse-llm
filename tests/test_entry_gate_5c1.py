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
    """Handles the rulings table sends to the gate after the original tables were written.

    The operator amended `docs/CHANNELS-launch.md` rather than rewriting it: the four bucket
    tables still hold all 62, and the 2026-08-07 section rules on them. A handle marked
    "НА ГЕЙТ" there is a candidate the tables never carried.
    """
    text = CANON.read_text(encoding="utf-8")
    section = text[text.index("## Рулинги гейта 5c1") :]
    return [
        line.split("|")[1].strip()
        for line in section.splitlines()
        if line.startswith("|") and "НА ГЕЙТ" in line
    ]


def test_the_candidate_list_is_the_canons_own():
    """A hand-copied handle list is a list that silently stops matching the file it came from.

    Not a set comparison: the bucket is what the gate holds each channel to, so a channel in the
    right list and the wrong bucket would be verified against expectations nobody chose. The
    gate's input only grows — a channel the operator later excluded was still measured, and
    deleting its row would rewrite what the pass found.
    """
    late = [(handle, "late") for handle in canon_sent_to_the_gate()]
    assert list(gate.CANDIDATES) == canon_buckets() + late


def test_the_composition_is_the_62_plus_what_the_rulings_added():
    counts = {
        b: sum(1 for _, bucket in gate.CANDIDATES if bucket == b)
        for b in ("comments", "posts", "watch", "late")
    }
    assert counts == {"comments": 29, "posts": 18, "watch": 14, "late": 2}
    assert len(gate.CANDIDATES) == 63
    assert len({handle for handle, _ in gate.CANDIDATES}) == 63


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
