"""The two directions PHASE-ship-1 §2 «region-collect» (iii) asks of the sentinel, plus the three
product defects my own adversarial review of this diff caught (§3: a caught defect gets its test
both ways in the commit that fixes it).

Forward: a mention planted in a fixture store is FOUND, with the fields the check names — channel,
msg_id, kind, date, brand and a quote — and the baseline counts it. A brand nothing names is in the
fixture ON PURPOSE: «a ZERO is a printed number» is the item's whole product, and without a
zero-mention brand here a `per_brand` built only from the rows it saw would pass green while the
shipped baseline silently dropped every brand that was not mentioned — which today is all three.
(«Яготинське для дітей» is in the fixture beside «Галичина» on purpose too: it shows that an
overlapping dictionary yields a row per BRAND named, which is the keyword matcher behaving, not a
double count — the same phrase would name two brands to a human reader as well.)

Backward: a dictionary naming no brands exits ≠ 0 and writes NOTHING. That direction is asserted on
the BYTES of a previous reading rather than on the absence of a file: the failure this guards is a
run that truncates its own output and then discovers it had nothing to look for, and a test that
only checked `not path.exists()` would pass against exactly that bug on the second run.

The three caught defects, each both ways: a spelling that ends in a non-word character must match
(`\\b` could not); a brand block with no `display_names` must REFUSE rather than vanish from the
baseline; and the quote must contain its own match even when the text is NFD-encoded, which is the
case a fold-then-slice index space gets wrong.
"""

import json
import sys
import unicodedata
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import region_sentinel as sentinel  # noqa: E402

BRANDS = """
brands:
  - brand_id: garmonija
    own: true
    display_names: ["Гармонія", "ТМ Гармонія", "Гармонія®"]
  - brand_id: zarih
    own: false
    display_names: ["Заріг"]
  - brand_id: molokija
    own: false
    display_names: ["Молокія®"]
  - brand_id: halychyna
    own: false
    display_names: ["Галичина"]
  - brand_id: slovianochka
    own: false
    display_names: ["Слов'яночка"]
  - brand_id: yahotynske-dlia-ditei
    own: false
    display_names: ["Яготинське для дітей"]
"""

CHANNELS = """
channels:
  - handle: "@zinkivnews"
    note: "fixture"
"""

# Decomposed «й»/«ї» ahead of the brand: four combining marks per repetition, each two code points
# raw and one after NFC. 80 repetitions is a drift of 320 characters — MEASURED, and deliberately
# larger than QUOTE_LEAD + QUOTE_CHARS (80 + 200), because a smaller drift still leaves the brand
# inside the window and the assertion below would pass against the very bug it exists for.
NFD_LEAD = unicodedata.normalize("NFD", "Мій найкращий день, їдемо далі. ") * 80


def plant(root: Path, kind: str, handle: str, records: list[dict]) -> None:
    path = root / f"{kind}s" / f"{handle.lstrip('@')}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(one, ensure_ascii=False) + "\n" for one in records), encoding="utf-8"
    )


def fixture_store(tmp_path, monkeypatch) -> tuple[Path, Path]:
    archive, region = tmp_path / "raw", tmp_path / "raw_region"
    plant(
        archive,
        "post",
        "@zinkivnews",
        [
            {
                "record_type": "post",
                "channel": "@zinkivnews",
                "msg_id": 11,
                "date": "2026-07-20T08:00:00+00:00",
                "text": "У магазині з'явилась ТМ Гармонія, сметана 15%, беріть поки є",
            },
            {
                "record_type": "post",
                "channel": "@zinkivnews",
                "msg_id": 12,
                "date": "2026-07-21T08:00:00+00:00",
                "text": "Ремонт дороги триває, рух обмежено",
            },
            {
                "record_type": "post",
                "channel": "@zinkivnews",
                "msg_id": 13,
                "date": "2026-07-22T08:00:00+00:00",
                "text": NFD_LEAD + "акція: Заріг сметана",
            },
            {
                "record_type": "post",
                "channel": "@zinkivnews",
                "msg_id": 14,
                "date": "2026-07-23T08:00:00+00:00",
                "text": "Молокія® 2,5% знову в продажу",
            },
            {
                # The dictionary spells it with an ASCII apostrophe; Telegram sent U+2019.
                "record_type": "post",
                "channel": "@zinkivnews",
                "msg_id": 15,
                "date": "2026-07-24T08:00:00+00:00",
                "text": "завезли Слов\u2019яночка 9%",
            },
            {
                # «дітей» carries «й», one of the three code points that decompose in this script.
                # The dictionary spells the brand composed; this post is DECOMPOSED, so the two
                # meet only through the normaliser.
                "record_type": "post",
                "channel": "@zinkivnews",
                "msg_id": 16,
                "date": "2026-07-25T08:00:00+00:00",
                "text": unicodedata.normalize("NFD", "є Яготинське для дітей 3,2%"),
            },
        ],
    )
    plant(
        region,
        "comment",
        "@zinkivnews",
        [
            {
                "record_type": "comment",
                "channel": "@zinkivnews",
                "parent_msg_id": 11,
                "msg_id": 900,
                "date": "2026-09-01T09:30:00+00:00",
                "text": "брали гармонія вчора, норм",
            }
        ],
    )
    monkeypatch.setattr(sentinel, "ARCHIVE_ROOT", archive)
    monkeypatch.setattr(sentinel, "REGION_ROOT", region)
    return archive, region


def run(tmp_path, brands_text: str) -> tuple[Path, Path, list[str]]:
    brands = tmp_path / "region_brands.yaml"
    brands.write_text(brands_text, encoding="utf-8")
    channels = tmp_path / "region_channels.yaml"
    channels.write_text(CHANNELS, encoding="utf-8")
    mentions = tmp_path / "region_mentions.jsonl"
    baseline = tmp_path / "region_baseline.json"
    argv = [
        "--brands",
        str(brands),
        "--channels",
        str(channels),
        "--mentions-out",
        str(mentions),
        "--baseline-out",
        str(baseline),
    ]
    return mentions, baseline, argv


def test_a_planted_mention_is_found_with_its_fields(tmp_path, monkeypatch, capsys):
    fixture_store(tmp_path, monkeypatch)
    mentions, baseline, argv = run(tmp_path, BRANDS)

    assert sentinel.main(argv) == 0
    capsys.readouterr()

    rows = [json.loads(line) for line in mentions.read_text(encoding="utf-8").splitlines()]
    assert [(row["msg_id"], row["kind"], row["brand"]) for row in rows] == [
        (11, "post", "garmonija"),
        (13, "post", "zarih"),
        (14, "post", "molokija"),
        (15, "post", "slovianochka"),
        (16, "post", "yahotynske-dlia-ditei"),
        (900, "comment", "garmonija"),
    ]

    post = rows[0]
    assert post["channel"] == "@zinkivnews"
    assert post["date"] == "2026-07-20T08:00:00+00:00"
    assert "Гармонія" in post["quote"] and len(post["quote"]) <= sentinel.QUOTE_CHARS
    # The post says «ТМ Гармонія»: one row, not one per spelling that matches it.
    assert sum(1 for row in rows if row["msg_id"] == 11) == 1
    # `Молокія®` is the brand's ONLY spelling: under a `\b` boundary it can never match, so this
    # row existing at all is what the bounded-lookaround idiom buys.
    assert rows[2]["matched"] == "Молокія®" and "Молокія®" in rows[2]["quote"]
    # The NFD post: the quote is evidence, so it must contain the thing it is evidence for.
    assert "Заріг" in rows[1]["quote"] and len(rows[1]["quote"]) <= sentinel.QUOTE_CHARS
    # Apostrophe-tolerant: the dictionary's ASCII `'` finds the post's U+2019.
    assert rows[3]["matched"] == "Слов'яночка"
    # NFC-normalised: the decomposed post meets the composed dictionary only through `prepare`.
    assert rows[4]["msg_id"] == 16 and "дітей" in rows[4]["quote"]
    # Case-insensitive: the comment says «гармонія» in lower case.
    assert rows[5]["msg_id"] == 900 and rows[5]["brand"] == "garmonija"

    read = json.loads(baseline.read_text(encoding="utf-8"))
    # halychyna is named by nothing in the fixture and STILL has a line: the zero is the product.
    assert read["mentions_per_brand"] == {
        "garmonija": 2,
        "zarih": 1,
        "molokija": 1,
        "halychyna": 0,
        "slovianochka": 1,
        "yahotynske-dlia-ditei": 1,
    }
    assert read["totals"] == {"channels": 1, "posts": 6, "comments": 1, "mentions": 6}
    assert read["window"] == {
        "first_date": "2026-07-20T08:00:00+00:00",
        "last_date": "2026-09-01T09:30:00+00:00",
    }


def test_a_dictionary_naming_no_brands_refuses_and_writes_nothing(tmp_path, monkeypatch):
    fixture_store(tmp_path, monkeypatch)
    mentions, baseline, argv = run(tmp_path, "brands: []\n")
    mentions.write_text("previous reading\n", encoding="utf-8")
    baseline.write_text("{}\n", encoding="utf-8")

    with pytest.raises(SystemExit) as refusal:
        sentinel.main(argv)

    assert refusal.value.code != 0
    assert "no brand carries a display name" in str(refusal.value.code)
    assert mentions.read_text(encoding="utf-8") == "previous reading\n"
    assert baseline.read_text(encoding="utf-8") == "{}\n"


def test_a_brand_block_with_no_spellings_refuses_instead_of_vanishing(tmp_path, monkeypatch):
    """The other half of the zero: a brand that was never looked for must not read as «0 mentions»."""
    fixture_store(tmp_path, monkeypatch)
    mentions, baseline, argv = run(
        tmp_path, BRANDS + '  - brand_id: prostokvashyno\n    display_name: ["Простоквашино"]\n'
    )
    mentions.write_text("previous reading\n", encoding="utf-8")

    with pytest.raises(SystemExit) as refusal:
        sentinel.main(argv)

    assert "prostokvashyno" in str(refusal.value.code)
    assert "carries no `display_names`" in str(refusal.value.code)
    assert mentions.read_text(encoding="utf-8") == "previous reading\n"
    assert not baseline.exists()


def test_one_channel_listed_twice_refuses_before_its_rows_are_counted_twice(tmp_path, monkeypatch):
    """The guard the collector already makes, on the same store key, in the file's other reader."""
    fixture_store(tmp_path, monkeypatch)
    mentions, baseline, argv = run(tmp_path, BRANDS)
    channels = tmp_path / "region_channels.yaml"
    channels.write_text(CHANNELS + '  - handle: "zinkivnews"\n    note: "same channel"\n', "utf-8")
    mentions.write_text("previous reading\n", encoding="utf-8")

    with pytest.raises(SystemExit) as refusal:
        sentinel.main(argv)

    assert "zinkivnews" in str(refusal.value.code)
    assert "listed more than once" in str(refusal.value.code)
    assert mentions.read_text(encoding="utf-8") == "previous reading\n"
    assert not baseline.exists()
