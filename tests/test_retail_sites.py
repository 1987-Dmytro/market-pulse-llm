"""The r2 site reader, both directions — every case here is a reading the first pass got wrong.

A census row says «this chain's own site links this channel». Each function below decides what
gets written into that sentence, and each one shipped a false version of it during C1 r2:
a support phone counted as a group invite, two bots counted as channels, and a domain-squatter's
parking page counted as a chain's website.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from retail_sites import extract, kind_of, names_the_chain, read_site  # noqa: E402


def test_a_phone_deep_link_is_not_an_invite():
    # `t.me/+380675178085` on tavriav.ua is "write to us", not a group. It has no username to
    # resolve, so counting it as an invite spends a resolve on a support phone number.
    assert kind_of("+380675178085") == "contact"
    assert kind_of("+Gpo70IWKXOE1NzZi") == "invite"


def test_a_bot_without_an_underscore_is_still_a_bot():
    # Telegram reserves every username ending in `bot`. An `_bot` suffix test called these two
    # channels and would have put them in the resolve budget as collectable sources.
    assert kind_of("@VelmartUaBot") == "bot"
    assert kind_of("@sim23_chatbot") == "bot"
    assert kind_of("@novus_ai_assistant_bot") == "bot"
    assert kind_of("@silposilpo") == "channel"
    assert kind_of("@foraINFO") == "channel"


def test_a_parking_page_is_not_the_chains_site():
    # The live body of https://gurman.ua/ on 2026-08-30. Accepting it wrote «Гурман's site
    # carries no Telegram link» — a fact about a domain squatter wearing a chain's name.
    parked = "<title>Это доменное имя продается</title>Доменное имя <b>gurman.ua</b> продается!"
    assert not names_the_chain(parked, "Гурман")
    assert names_the_chain("<h1>Файно маркет — мережа супермаркетів</h1>", "Файно маркет")
    # «маркет» alone must not carry the match: it appears on every supermarket page in Ukraine.
    assert not names_the_chain("<h1>Продуктовий маркет</h1>", "Файно маркет")


def test_share_widgets_are_not_channels():
    html = '<a href="https://t.me/share/url?url=x">share</a><a href="https://t.me/foraINFO">us</a>'
    assert extract(html) == ["@foraINFO"]


def test_one_shell_served_to_every_path_is_not_evidence_of_no_channel(monkeypatch):
    # thrash.ua returns the same 20422-byte shell for /, /contacts and /about: curl never saw a
    # footer, so "no-link" would be a claim about the instrument dressed as a claim about Thrash.
    import retail_sites

    monkeypatch.setattr(retail_sites, "fetch", lambda url, timeout=25: (200, "<div id=app></div>"))
    monkeypatch.setattr(retail_sites.time, "sleep", lambda _s: None)
    assert read_site("thrash.ua")["status"] == "shell"

    pages = iter([(200, "<p>a</p>"), (200, "<p>bb</p>"), (404, "")])
    monkeypatch.setattr(retail_sites, "fetch", lambda url, timeout=25: next(pages))
    # Different bytes per path: the pages really were read, and really carry no link.
    assert read_site("blyzenko.ua")["status"] == "no-link"


def test_a_page_that_was_never_read_is_not_a_page_without_a_link(monkeypatch):
    import retail_sites

    monkeypatch.setattr(retail_sites, "fetch", lambda url, timeout=25: (403, "<html>denied"))
    monkeypatch.setattr(retail_sites.time, "sleep", lambda _s: None)
    assert read_site("zakaz.ua")["status"] == "blocked"

    monkeypatch.setattr(retail_sites, "fetch", lambda url, timeout=25: (0, "could not resolve"))
    assert read_site("delikat.ua")["status"] == "dns"
