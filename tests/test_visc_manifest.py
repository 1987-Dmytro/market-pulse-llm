"""`scripts/fetch_visc_media.py`: the three states, and that a post is in exactly one.

The expensive thing to discover on a 25-channel Telegram sweep is that a FloodWait stop was
filed as `blind` — that puts a transport failure into the yield screen's denominator as a fact
about the corpus. So `main` is driven end to end against a fake fetch, with a wall injected.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))


def _script(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fetcher = _script("fetch_visc_media")
pattern = _script("caption_posts")

CENSUS = json.loads((REPO_ROOT / "results" / "image_census_5c1.json").read_text(encoding="utf-8"))


def test_the_population_is_the_census_minus_the_channel_vis_b_already_bought():
    wanted = fetcher.population(CENSUS)
    assert fetcher.ALREADY_BOUGHT not in wanted
    rows = {row["handle"]: row for row in CENSUS["sources"]}
    # `uncaptioned_msg_ids` names only the posts that HAVE media; the census counts the rest
    # without naming them, and the manifest has to close on the whole unreadable population.
    named = sum(len(ids) for ids in wanted.values())
    unnamed = fetcher.unnamed_without_media(CENSUS)
    assert named == sum(
        row["uncaptioned_with_media"]
        for handle, row in rows.items()
        if handle != fetcher.ALREADY_BOUGHT
    )
    assert named + sum(unnamed.values()) == sum(
        row["states"]["no_text_and_no_caption"]
        for handle, row in rows.items()
        if handle != fetcher.ALREADY_BOUGHT
    )
    assert fetcher.ALREADY_BOUGHT not in unnamed
    # the ids are the census's own, not re-derived
    for handle, ids in wanted.items():
        assert ids == sorted(rows[handle]["uncaptioned_msg_ids"])


def fake_store(tmp_path: Path) -> Path:
    """Three silent posts of two channels: one album with images, one single, one with no media."""
    posts = tmp_path / "posts"
    posts.mkdir()
    rows = [
        {
            "channel": "@a",
            "msg_id": 1,
            "date": "2026-07-11T00:00:00+00:00",
            "text": "",
            "has_media": True,
            "grouped_id": 77,
        },
        {
            "channel": "@a",
            "msg_id": 9,
            "date": "2026-07-12T00:00:00+00:00",
            "text": "",
            "has_media": True,
            "grouped_id": None,
        },
        {
            "channel": "@b",
            "msg_id": 5,
            "date": "2026-07-13T00:00:00+00:00",
            "text": "",
            "has_media": False,
            "grouped_id": None,
        },
    ]
    (posts / "all.jsonl").write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8"
    )
    return posts


def fake_census(tmp_path: Path) -> Path:
    # The real census's keys: `uncaptioned_msg_ids` names only the with-media posts, and @c is
    # the shape four real channels have — counted as unreadable, never named, no media at all.
    census = {
        "sources": [
            {
                "handle": "@a",
                "states": {"no_text_and_no_caption": 2},
                "uncaptioned_with_media": 2,
                "uncaptioned_without_media": 0,
                "uncaptioned_msg_ids": [9, 1],
            },
            {
                "handle": "@b",
                "states": {"no_text_and_no_caption": 1},
                "uncaptioned_with_media": 1,
                "uncaptioned_without_media": 0,
                "uncaptioned_msg_ids": [5],
            },
            {
                "handle": "@c",
                "states": {"no_text_and_no_caption": 2},
                "uncaptioned_with_media": 0,
                "uncaptioned_without_media": 2,
                "uncaptioned_msg_ids": [],
            },
        ]
    }
    path = tmp_path / "census.json"
    path.write_text(json.dumps(census), encoding="utf-8")
    return path


def drive(tmp_path: Path, runner) -> dict:
    manifest = tmp_path / "m.json"
    code = fetcher.main(
        [
            "--census",
            str(fake_census(tmp_path)),
            "--posts",
            str(fake_store(tmp_path)),
            "--media",
            str(tmp_path / "media"),
            "--manifest",
            str(manifest),
        ],
        runner=runner,
    )
    written = json.loads(manifest.read_text(encoding="utf-8"))
    written["_exit"] = code
    return written


def test_every_post_lands_in_exactly_one_state_and_blind_says_why(tmp_path):
    image = {"msg_id": 1, "file": "x.jpg", "sha256": "ab" * 32, "bytes": 10}
    fetched = {
        ("@a", 1): {"items": [image], "poll": None},
        ("@a", 9): {
            "items": [{"msg_id": 9, "missing": "media is video/mp4, not an image"}],
            "poll": None,
        },
        ("@b", 5): {"items": [], "poll": None},
    }
    written = drive(tmp_path, lambda: (fetched, []))
    assert written["_exit"] == 0
    assert written["states"] == {
        "fetchable": 1,
        "blind": 2,
        "owed": 0,
        "blind_unnamed_no_media": 2,
    }
    # 3 asked + the 2 the census counted and never named = the whole unreadable population
    assert written["unreadable_population"] == 5
    assert written["blind_unnamed_no_media"] == {"@c": 2}
    assert written["by_channel"]["@c"] == {
        "asked": 0,
        "fetchable": 0,
        "blind": 0,
        "owed": 0,
        "blind_unnamed_no_media": 2,
        "images": 0,
    }
    assert written["fetchable"] == ["@a:1"]
    assert set(written["blind"]) == {"@a:9", "@b:5"}
    # blind is not one thing: nothing was ever there, vs the media is there and unusable
    assert written["blind_reasons"]["@b:5"] == "no media in the store"
    assert "video/mp4" in written["blind_reasons"]["@a:9"]
    assert written["by_channel"]["@a"] == {
        "asked": 2,
        "fetchable": 1,
        "blind": 1,
        "owed": 0,
        "blind_unnamed_no_media": 0,
        "images": 1,
    }
    # and the shape the paid driver reads is the shape that was written
    images, polls, blind = pattern.population(written)
    assert [entry["name"] for entry in images] == ["@a:1"]
    assert polls == [] and sorted(blind) == ["@a:9", "@b:5"]


def test_a_floodwait_stop_is_owed_and_never_blind(tmp_path):
    """The whole reason this file exists. `@b:5` has no media and IS blind; `@a:9` was never
    asked, and filing it as blind would tell the screen the corpus lacks something it may have."""
    fetched = {
        ("@a", 1): {
            "items": [{"msg_id": 1, "file": "x.jpg", "sha256": "c" * 64, "bytes": 3}],
            "poll": None,
        }
    }
    written = drive(tmp_path, lambda: (fetched, ["@a:9", "@b:5"]))
    assert written["_exit"] == 3, "an incomplete sweep does not exit 0"
    assert written["states"] == {
        "fetchable": 1,
        "blind": 0,
        "owed": 2,
        "blind_unnamed_no_media": 2,
    }
    assert written["still_owed"] == ["@a:9", "@b:5"]
    assert written["blind"] == [] and written["blind_reasons"] == {}


def test_it_refuses_to_overwrite_a_manifest_a_sweep_already_wrote(tmp_path):
    manifest = tmp_path / "m.json"
    manifest.write_text("{}", encoding="utf-8")
    with pytest.raises(SystemExit, match="never overwrite"):
        fetcher.main(
            [
                "--census",
                str(fake_census(tmp_path)),
                "--posts",
                str(fake_store(tmp_path)),
                "--manifest",
                str(manifest),
            ],
            runner=lambda: ({}, []),
        )


def test_a_post_with_text_of_its_own_is_refused_not_captioned(tmp_path):
    posts = fake_store(tmp_path)
    rows = [json.loads(line) for line in (posts / "all.jsonl").read_text().splitlines()]
    rows[0]["text"] = "Акція на сир"
    (posts / "all.jsonl").write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8"
    )
    with pytest.raises(SystemExit, match="has text of its own"):
        fetcher.main(
            [
                "--census",
                str(fake_census(tmp_path)),
                "--posts",
                str(posts),
                "--manifest",
                str(tmp_path / "n.json"),
            ],
            runner=lambda: ({}, []),
        )
