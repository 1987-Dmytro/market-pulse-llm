"""Offline tests for the day-2 harvest of Telegram's "similar channels" — no Telegram, no session.

The record this writes is a CANDIDATE list the operator reads at the next sitting, so what is
guarded is the pair of promises it makes: nothing enters the registry from here, and nothing is
silently dropped from what Telegram returned.
"""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from telethon.errors import FloodWaitError

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import harvest_similar_5c1 as harvest  # noqa: E402


class FakeClient:
    """Enough of a Telethon client to drive `main` end to end: the two calls that would reach the
    network are `get_entity` and the request itself, and both are answered here."""

    def __init__(self, replies):
        self.replies = replies
        self.asked = []

    async def connect(self):
        return None

    async def is_user_authorized(self):
        return True

    async def disconnect(self):
        return None

    async def get_entity(self, handle):
        return SimpleNamespace(username=handle.lstrip("@"))

    async def __call__(self, request):
        seed = f"@{request.channel.username}"
        self.asked.append(seed)
        reply = self.replies[seed]
        if isinstance(reply, Exception):
            raise reply
        return SimpleNamespace(chats=reply, count=len(reply))


def chat(username, title, subscribers, *, broadcast=True, megagroup=False):
    return SimpleNamespace(
        username=username,
        title=title,
        participants_count=subscribers,
        verified=False,
        broadcast=broadcast,
        megagroup=megagroup,
    )


@pytest.fixture
def wired(tmp_path, monkeypatch):
    """The script pointed at a scratch record, with the handles it calls "already ours" fixed."""
    monkeypatch.setattr(harvest, "RECORD", tmp_path / "harvest_mothers_ua.json")
    monkeypatch.setattr(harvest, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(harvest.entry_check, "PAUSE_SECONDS", 0)
    monkeypatch.setattr(harvest, "known_handles", lambda: {"@tarilka_malyuka": "registry"})
    monkeypatch.setattr(harvest, "git_state", lambda path: {"commit": "test"})
    return tmp_path / "harvest_mothers_ua.json"


def test_the_record_is_written_and_says_it_authorises_nothing(wired, monkeypatch):
    """Rider clause 3 of amendment 3.12 in one sentence: candidates only, gate plus yield floor.
    A record that merely LISTED channels would be read six weeks later as a shortlist."""
    replies = {seed: [chat("found_one", "Знайдений", 1000)] for seed in harvest.SEEDS}
    monkeypatch.setattr(harvest, "build_client", lambda: FakeClient(replies))

    assert harvest.main([]) == 0
    record = json.loads(wired.read_text(encoding="utf-8"))
    assert "CANDIDATES ONLY" in record["status"]
    assert "yield floor" in record["status"] and "No join" in record["status"]
    assert record["summary"]["seeds_asked"] == 3
    assert record["flood_wait_seconds"] is None


def test_a_channel_we_already_hold_is_marked_and_not_dropped(wired, monkeypatch):
    """A seed recommending what we already collect is a fact about the seed. Dropping the row
    would make a well-covered segment look like an empty answer."""
    replies = {
        harvest.SEEDS[0]: [
            chat("tarilka_malyuka", "Тарілка Малюка", 5000),
            chat("brand_new", "Новий канал", 9000),
        ],
        harvest.SEEDS[1]: [],
        harvest.SEEDS[2]: [],
    }
    monkeypatch.setattr(harvest, "build_client", lambda: FakeClient(replies))

    assert harvest.main([]) == 0
    rows = json.loads(wired.read_text(encoding="utf-8"))["seeds"][0]["rows"]
    assert [row["handle"] for row in rows] == ["@tarilka_malyuka", "@brand_new"]
    assert rows[0]["known"] == "registry"
    assert rows[1]["known"] is None
    summary = json.loads(wired.read_text(encoding="utf-8"))["summary"]
    assert summary["rows_returned"] == 2
    assert summary["distinct_not_already_ours"] == 1


def test_a_recommended_chat_is_told_apart_from_a_recommended_channel(wired, monkeypatch):
    """The day-2 sitting threw out three "city feeds" that were supergroups. A harvest that could
    not say which is which would hand the same class straight back to the operator."""
    replies = {
        harvest.SEEDS[0]: [
            chat("a_feed", "Канал", 100),
            chat("a_chat", "Чат", 200, broadcast=False, megagroup=True),
        ],
        harvest.SEEDS[1]: [],
        harvest.SEEDS[2]: [],
    }
    monkeypatch.setattr(harvest, "build_client", lambda: FakeClient(replies))

    assert harvest.main([]) == 0
    record = json.loads(wired.read_text(encoding="utf-8"))
    rows = {row["handle"]: row for row in record["seeds"][0]["rows"]}
    assert rows["@a_feed"]["broadcast"] is True and rows["@a_feed"]["megagroup"] is False
    assert rows["@a_chat"]["broadcast"] is False and rows["@a_chat"]["megagroup"] is True
    assert record["summary"]["distinct_not_already_ours"] == 2
    assert record["summary"]["broadcast_channels_among_them"] == 1


def test_a_flood_wait_keeps_the_seeds_already_answered(wired, monkeypatch):
    """Each seed costs a ResolveUsernameRequest — the limit that cost this account twenty hours on
    2026-08-07. The record says how far it got instead of losing the part that succeeded."""
    replies = {
        harvest.SEEDS[0]: [chat("first", "Перший", 10)],
        harvest.SEEDS[1]: FloodWaitError(request=None),
        harvest.SEEDS[2]: [chat("never_asked", "Не питали", 10)],
    }
    client = FakeClient(replies)
    monkeypatch.setattr(harvest, "build_client", lambda: client)

    assert harvest.main([]) == 0
    record = json.loads(wired.read_text(encoding="utf-8"))
    assert record["flood_wait_seconds"] is not None
    assert [found["seed"] for found in record["seeds"]] == [harvest.SEEDS[0]]
    assert client.asked == list(harvest.SEEDS[:2]), "it walked into a third seed inside the wall"


def test_plan_asks_telegram_nothing(wired, monkeypatch):
    def refuse():
        raise AssertionError("--plan built a client")

    monkeypatch.setattr(harvest, "build_client", refuse)
    assert harvest.main(["--plan"]) == 0
    assert not wired.exists()


def test_the_seeds_are_the_briefs_own():
    """The three are named in PROMPT-5c1-day2 step 9, and the brief is a team-lead file this
    session commits unedited — so the list is grepped back to it rather than trusted."""
    brief = (REPO_ROOT / "docs" / "PROMPT-5c1-day2.md").read_text(encoding="utf-8")
    line = " ".join(brief[brief.index("HARVEST similar-channels") :][:220].split())
    for seed in harvest.SEEDS:
        assert seed in line, seed
