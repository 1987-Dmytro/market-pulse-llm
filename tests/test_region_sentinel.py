"""The two directions PHASE-ship-1 §2 «region-collect» (iii) asks of the sentinel.

Forward: a mention planted in a fixture store is FOUND, with the fields the check names — channel,
msg_id, kind, date, brand and a quote — and the baseline counts it, including the brand nothing
names, whose zero is the point of the file.

Backward: a dictionary naming no brands exits ≠ 0 and writes NOTHING. That direction is asserted on
the BYTES of a previous reading rather than on the absence of a file: the failure this guards is a
run that truncates its own output and then discovers it had nothing to look for, and a test that
only checked `not path.exists()` would pass against exactly that bug on the second run.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import region_sentinel as sentinel  # noqa: E402

BRANDS = """
brands:
  - brand_id: garmonija
    own: true
    display_names: ["Гармонія", "ТМ Гармонія"]
  - brand_id: zarih
    own: false
    display_names: ["Заріг"]
"""

CHANNELS = """
channels:
  - handle: "@zinkivnews"
    note: "fixture"
"""


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
                "text": "гармонія норм, а от Заріг дорожчий",
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
        (900, "comment", "garmonija"),
        (900, "comment", "zarih"),
    ], "the post's brand, and BOTH brands of the comment that names two"

    post = rows[0]
    assert post["channel"] == "@zinkivnews"
    assert post["date"] == "2026-07-20T08:00:00+00:00"
    assert "Гармонія" in post["quote"] and len(post["quote"]) <= sentinel.QUOTE_CHARS
    # The post says «ТМ Гармонія»: one row, not one per spelling that matches it.
    assert sum(1 for row in rows if row["msg_id"] == 11) == 1

    read = json.loads(baseline.read_text(encoding="utf-8"))
    assert read["mentions_per_brand"] == {"garmonija": 2, "zarih": 1}
    assert read["totals"] == {"channels": 1, "posts": 2, "comments": 1, "mentions": 3}
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
