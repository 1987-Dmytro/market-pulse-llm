"""The Opus audit's three scripts (SPEC 3.16): the draw, the schema check, the reader.

The packs are a REVIEW instrument, so what is tested is the instrument's refusals. A
validator that accepts a row it should refuse launders a defect into a candidate number
the operator's sitting then rules on, and every one of the refusals below is a way that
can happen quietly.

Nothing here reads the real packs or the real manifest: those are rebuilt whenever the
screen moves, and a suite that depends on them goes red for a reason that is not a
defect. The registry and the protocol ARE read — they are committed, the validator pins
them on purpose, and the fixture takes their live shas so the pin is exercised rather
than frozen.
"""

import json
import sys
from hashlib import sha256
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import build_opus_audit_packs as builder  # noqa: E402
import read_opus_audit as reader  # noqa: E402
import validate_opus_returns as validator  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY = "config/registry.yaml"


def item(name, pack="pack_01", brands=(), judgeable=True, images=1, channel="@chan"):
    return {
        "item": name,
        "pack": pack,
        "channel": channel,
        "msg_id": int(name.split(":")[1]),
        "date": "2026-07-20T00:00:00+00:00",
        "strata": ["S2"] if brands else ["S3"],
        "has_text": True,
        "has_caption": bool(images),
        "caption_source": "gm4-nf4-base" if judgeable else None,
        "judgeable_caption": judgeable,
        "images": {"named": images, "sha_matched": images},
        "matcher": {
            "watchlist_brands": list(brands),
            "category_groups": ["dairy"],
            "relevant": True,
        },
    }


@pytest.fixture
def manifest(tmp_path):
    """A two-item pack and the manifest that pins it, with the live registry sha."""
    pack = tmp_path / "pack_01.md"
    pack.write_text("# a pack the rows were written against\n", encoding="utf-8")
    items = [
        item("@chan:1", brands=["rud"]),
        item("@chan:2", brands=[], judgeable=False, images=0),
        item("@chan:3", brands=["varto"], pack="pack_02"),
    ]
    return {
        "seed": 42,
        "protocol": {
            "path": "docs/PROMPT-opus-audit-protocol.md",
            "sha256": sha256(
                (REPO_ROOT / "docs/PROMPT-opus-audit-protocol.md").read_bytes()
            ).hexdigest(),
        },
        "pinned_inputs": {
            REGISTRY: sha256((REPO_ROOT / REGISTRY).read_bytes()).hexdigest(),
        },
        "packs": [
            {
                "pack": "pack_01",
                "path": str(pack),
                "sha256": sha256(pack.read_bytes()).hexdigest(),
                "items": 2,
            },
            {"pack": "pack_02", "path": str(pack), "sha256": "0" * 64, "items": 1},
        ],
        "items": items,
        "items_total": len(items),
    }


def returns(tmp_path, *rows, name="returns_01.jsonl"):
    path = tmp_path / name
    path.write_text(
        "".join(
            (row if isinstance(row, str) else json.dumps(row, ensure_ascii=False)) + "\n"
            for row in rows
        ),
        encoding="utf-8",
    )
    return path


def row(name="@chan:1", **overrides):
    return {
        "pack": "pack_01",
        "item": name,
        "watchlist_hits": [],
        "other_dairy_brands": [],
        "caption_verdict": "faithful",
        "brands_visible_missed": [],
        "note": "",
    } | overrides


def check(manifest, path):
    return validator.validate(manifest, path, validator.aliases(manifest))


# ---------------------------------------------------------------- the draw


def derived(channels):
    """`{handle: [item]}` in the shape `draw` reads, from `(brands, caption)` tuples."""
    out = {}
    for handle, posts in channels.items():
        out[handle] = [
            {
                "item": f"{handle}:{msg_id}",
                "channel": handle,
                "msg_id": msg_id,
                "date": "2026-07-20T00:00:00+00:00",
                "text": "" if caption else "text",
                "caption": caption,
                "caption_kind": "image" if caption else None,
                "caption_source": "gm4-nf4-base" if caption else None,
                "read_as": caption or "text",
                "images": {
                    "files": [],
                    "named": 1,
                    "sha_matched": 1,
                    "missing": [],
                    "sha_differs": [],
                },
                "matcher": {
                    "watchlist_brands": list(brands),
                    "category_groups": ["dairy"],
                    "relevant": True,
                },
                "judgeable_caption": bool(caption),
            }
            for msg_id, brands, caption in posts
        ]
    return out


def test_draw_is_a_function_of_the_seed():
    pool = derived({"@a": [(n, ["rud"] if n % 2 else [], "") for n in range(1, 40)]})
    first, _ = builder.draw(pool, 42, 10)
    again, _ = builder.draw(pool, 42, 10)
    assert [entry["item"] for entry in first] == [entry["item"] for entry in again]


def test_the_per_channel_cap_binds_each_stratum():
    pool = derived({"@a": [(n, ["rud"] if n % 2 else [], "") for n in range(1, 60)]})
    _, members = builder.draw(pool, 42, 10)
    assert len(members["S2"]) == 10
    assert len(members["S3"]) == 10


def test_an_item_in_two_strata_is_written_once():
    """A caption-decided brand hit is S1, S2 and S4 — and one judgement, not three."""
    pool = derived({"@a": [(1, ["rud"], "a caption")]})
    items, members = builder.draw(pool, 42, 10)
    assert len(items) == 1
    assert items[0]["strata"] == ["S1", "S2", "S4"]
    assert [len(members[name]) for name in ("S1", "S2", "S3", "S4")] == [1, 1, 0, 1]


def test_a_transcription_is_in_S4_but_is_not_judgeable():
    """It is a committed caption row, so it is reviewed; no model wrote it, so its
    faithfulness is not asked about. A row in no pack is a row nobody reviews."""
    pool = derived({"@a": [(1, [], "the poll, transcribed")]})
    for entry in pool["@a"]:
        entry["caption_source"] = None
        entry["images"] = {
            "files": [],
            "named": 0,
            "sha_matched": 0,
            "missing": [],
            "sha_differs": [],
        }
        entry["judgeable_caption"] = builder.judgeable(entry)
    items, members = builder.draw(pool, 42, 10)
    assert members["S4"] == ["@a:1"]
    assert items[0]["strata"] == ["S1", "S3", "S4"]
    assert not items[0]["judgeable_caption"]


def test_judgeable_needs_a_model_and_every_image():
    base = {
        "caption": "a caption",
        "caption_source": "gm4-nf4-base",
        "images": {"named": 2, "sha_matched": 2},
    }
    assert builder.judgeable(base)
    assert not builder.judgeable({**base, "caption": ""})
    assert not builder.judgeable({**base, "caption_source": None})
    assert not builder.judgeable({**base, "images": {"named": 2, "sha_matched": 1}})
    assert not builder.judgeable({**base, "images": {"named": 0, "sha_matched": 0}})


@pytest.mark.parametrize("count", [15, 20, 30, 39, 40, 60, 468])
def test_packs_stay_inside_the_contract(count):
    packs = builder.compose(list(range(count)))
    assert sum(len(pack) for pack in packs) == count
    assert all(builder.PACK_MIN <= len(pack) <= builder.PACK_MAX for pack in packs)


@pytest.mark.parametrize("count", [21, 29, 41])
def test_the_ceiling_is_the_half_that_is_kept(count):
    """21 items are one pack of 21 or two of 11: inside that band no split holds both
    bounds, and a session longer than the contract sized is the worse break."""
    packs = builder.compose(list(range(count)))
    assert sum(len(pack) for pack in packs) == count
    assert max(len(pack) for pack in packs) <= builder.PACK_MAX
    assert max(len(pack) for pack in packs) - min(len(pack) for pack in packs) <= 1


def test_the_protocol_must_be_tracked(tmp_path):
    loose = tmp_path / "PROMPT-not-committed.md"
    loose.write_text("rules nobody committed\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="not tracked"):
        builder.protocol_pin(loose)


def test_a_tracked_but_edited_protocol_is_refused(monkeypatch):
    monkeypatch.setattr(builder, "git", lambda *args: "docs/PROMPT-opus-audit-protocol.md\n")
    with pytest.raises(SystemExit, match="modified against HEAD"):
        builder.protocol_pin()


def test_the_screen_must_reproduce():
    record = {
        "sources": [
            {
                "handle": "@a",
                "posts": {"in_window": 9},
                "relevant_posts": 1,
                "brand_hits": {"posts": 1},
                "category_hits": {"posts": 1},
                "captions": {"graded": 1, "graded_on_a_caption": 0},
            }
        ]
    }
    with pytest.raises(SystemExit, match="does not reproduce screen v2"):
        builder.reproduction(record, derived({"@a": [(1, ["rud"], "")]}))


# ---------------------------------------------------------------- the validator


def test_a_clean_file_validates(manifest, tmp_path):
    rows, defects = check(manifest, returns(tmp_path, row(), row("@chan:2", caption_verdict="n/a")))
    assert defects == []
    assert [entry["item"] for entry in rows] == ["@chan:1", "@chan:2"]
    assert rows[0]["channel"] == "@chan" and rows[0]["strata"] == ["S2"]


def test_a_display_name_resolves_to_its_brand_id(manifest, tmp_path):
    """The protocol says «list the watchlist brands», never «emit ids»."""
    rows, defects = check(manifest, returns(tmp_path, row(watchlist_hits=["Рудь", "varto"])))
    assert defects == []
    assert rows[0]["watchlist_hits"] == ["rud", "varto"]


def test_an_unknown_brand_is_refused_not_dropped(manifest, tmp_path):
    _, defects = check(manifest, returns(tmp_path, row(watchlist_hits=["Dziugas"])))
    assert "neither a brand_id nor a" in defects[0]
    assert "other_dairy_brands" in defects[0]


def test_a_modified_pack_is_refused(manifest, tmp_path):
    Path(manifest["packs"][0]["path"]).write_text("# edited after it went out\n", encoding="utf-8")
    _, defects = check(manifest, returns(tmp_path, row()))
    assert "the manifest pins" in defects[0]


def test_an_item_from_another_pack_and_an_invented_one_read_apart(manifest, tmp_path):
    _, defects = check(manifest, returns(tmp_path, row("@chan:3"), row("@nowhere:9")))
    assert "is in pack_02, not pack_01" in defects[0]
    assert "no pack in the manifest" in defects[1]


def test_one_row_per_item(manifest, tmp_path):
    _, defects = check(manifest, returns(tmp_path, row(), row(note="second thoughts")))
    assert "answered twice" in defects[0]


def test_an_unreadable_row_is_not_an_empty_one(manifest, tmp_path):
    rows, defects = check(manifest, returns(tmp_path, "{not json", row()))
    assert "not JSON" in defects[0]
    assert [entry["item"] for entry in rows] == ["@chan:1"]


@pytest.mark.parametrize(
    "overrides, expected",
    [
        ({"caption_verdict": "probably"}, "is not one of"),
        ({"watchlist_hits": "rud"}, "not a list"),
        ({"other_dairy_brands": [""]}, "non-empty strings"),
        ({"note": 7}, "note must be a string"),
        ({"pack": "pack_02"}, "says pack"),
    ],
)
def test_the_schema_is_refused_field_by_field(manifest, tmp_path, overrides, expected):
    _, defects = check(manifest, returns(tmp_path, row(**overrides)))
    assert expected in defects[0]


def test_a_missing_and_an_extra_field_both_stop_the_row(manifest, tmp_path):
    short = {key: value for key, value in row().items() if key != "note"}
    _, defects = check(manifest, returns(tmp_path, short, row(**{"confidence": 0.9})))
    assert "missing ['note']" in defects[0]
    assert "unknown field(s) ['confidence']" in defects[1]


def test_a_verdict_where_there_is_nothing_to_judge(manifest, tmp_path):
    _, defects = check(manifest, returns(tmp_path, row("@chan:2", caption_verdict="faithful")))
    assert "no model caption over" in defects[0]


def test_nothing_is_visible_without_an_image(manifest, tmp_path):
    _, defects = check(
        manifest,
        returns(tmp_path, row("@chan:2", caption_verdict="n/a", brands_visible_missed=["rud"])),
    )
    assert "Nothing is visible here" in defects[0]


def test_a_moved_registry_stops_the_resolution(manifest, tmp_path):
    manifest["pinned_inputs"][REGISTRY] = "f" * 64
    with pytest.raises(SystemExit, match="canon table in"):
        check(manifest, returns(tmp_path, row()))


def test_a_file_that_names_no_pack(manifest, tmp_path):
    _, defects = check(manifest, returns(tmp_path, row(), name="answers.jsonl"))
    assert "names no pack" in defects[0]


def test_coverage_separates_unanswered_from_declined(manifest, tmp_path):
    rows, _ = check(manifest, returns(tmp_path, row(caption_verdict="n/a")))
    found = validator.coverage(manifest, "pack_01", rows)
    assert found["items"] == 2 and found["rows"] == 1
    assert found["unanswered"] == ["@chan:2"]
    assert found["captions_judgeable"] == 1 and found["captions_judged"] == 0
    assert found["captions_declined"] == ["@chan:1"]


# ---------------------------------------------------------------- the reader


def read(manifest, tmp_path, *rows):
    """The reader driven to its file — a return value proves nothing about what is written."""
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    record = tmp_path / "opus_audit.json"
    assert (
        reader.main(
            [
                "--manifest",
                str(path),
                "--record",
                str(record),
                str(returns(tmp_path, *rows)),
            ]
        )
        == 0
    )
    return json.loads(record.read_text(encoding="utf-8"))


def test_the_reader_writes_candidates_not_measurements(manifest, tmp_path):
    found = read(
        manifest,
        tmp_path,
        row(watchlist_hits=["rud"], other_dairy_brands=["Дольче"], note="in the image only"),
        row("@chan:2", caption_verdict="n/a", watchlist_hits=["halychyna"]),
    )
    matcher = found["matcher_candidates"]
    assert matcher["label"] == "review, not measurement"
    assert matcher["overall"]["tp"] == 1 and matcher["overall"]["fp"] == 0
    assert matcher["overall"]["fn"] == 1  # @chan:2, where the matcher found nothing
    assert matcher["overall"]["precision_candidate"] == 1.0
    assert matcher["overall"]["recall_candidate"] == 0.5
    assert matcher["missed_brand_candidates"]["halychyna"]["items"] == ["@chan:2"]
    assert matcher["by_channel"]["@chan"]["fn"] == 1
    assert found["open_extraction_candidates"]["names"]["дольче"]["as_written"] == ["Дольче"]
    assert found["notes"] == [{"item": "@chan:1", "channel": "@chan", "note": "in the image only"}]
    assert found["instrument"]["model"] == "claude-opus-5"
    assert found["instrument"]["protocol_sha"] == manifest["protocol"]["sha256"]
    assert "never measurement" in found["class"]


def test_the_caption_rate_is_over_what_could_be_judged(manifest, tmp_path):
    found = read(
        manifest, tmp_path, row(caption_verdict="partial"), row("@chan:2", caption_verdict="n/a")
    )
    captions = found["caption_candidates"]
    assert captions["judgeable"] == 1  # @chan:2 has no model caption and no image
    assert captions["judged"] == 1
    assert captions["tally"] == {"partial": 1}
    assert captions["faithful_rate_candidate"] == 0.0
    assert found["coverage"]["unanswered"] == []


def test_a_declined_caption_is_not_a_wrong_one(manifest, tmp_path):
    found = read(manifest, tmp_path, row(caption_verdict="n/a"))
    captions = found["caption_candidates"]
    assert captions["judgeable"] == 1 and captions["judged"] == 0
    assert captions["declined_n_a"] == 1
    assert captions["faithful_rate_candidate"] is None


def test_the_reader_refuses_a_defective_file(manifest, tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(SystemExit, match="would launder a bad row"):
        reader.main(
            [
                "--manifest",
                str(path),
                "--record",
                str(tmp_path / "record.json"),
                str(returns(tmp_path, row(watchlist_hits=["Dziugas"]))),
            ]
        )


def test_the_reader_refuses_a_protocol_that_moved(manifest, tmp_path):
    manifest["protocol"]["sha256"] = "a" * 64
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(SystemExit, match="instructions nobody"):
        reader.main(
            [
                "--manifest",
                str(path),
                "--record",
                str(tmp_path / "record.json"),
                str(returns(tmp_path, row())),
            ]
        )


def test_the_reader_refuses_to_aggregate_nothing(manifest, tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(SystemExit, match="aggregate over nothing"):
        reader.main(
            ["--manifest", str(path), "--pack", str(tmp_path / "empty"), "--record", str(tmp_path)]
        )


# ---------------------------------------------------------------- the blind


def a_pack(items, watchlist=None):
    from market_pulse.registry import load_registry

    brands = watchlist or load_registry(REPO_ROOT / REGISTRY).watchlist
    return builder.render_pack("pack_01", items, brands, {"path": "p.md", "sha256": "0" * 64})


def blind_items(**overrides):
    pool = derived({"@a": [(1, ["rud"], "a caption")]})
    item = {**pool["@a"][0], "strata": ["S1", "S2", "S4"], **overrides}
    return [item]


def test_the_pack_never_names_the_matcher_or_a_stratum():
    """The addendum's ruling, checked on the bytes that ship rather than on the diff."""
    assert builder.blinding_sweep(a_pack(blind_items())) == []


def test_the_sweep_fires_when_the_verdict_is_put_back():
    """The negative control. A sweep that never fires proves nothing about what it guards."""
    leaked = a_pack(blind_items()) + "\n**matcher's answer:** watchlist brands `rud`\n"
    assert builder.blinding_sweep(leaked)
    assert builder.blinding_sweep(a_pack(blind_items()) + "\n- strata: **S3**\n")


def test_a_post_may_say_anything_the_scaffolding_may_not():
    """Source text is quoted verbatim inside a fence and is not the pack's own voice."""
    inside = a_pack(blind_items(text="S3 matcher strata", caption=""))
    assert "S3 matcher strata" in inside
    assert builder.blinding_sweep(inside) == []


def test_the_shuffle_breaks_the_stratum_blocks():
    pool = derived({"@a": [(n, ["rud"] if n <= 40 else [], "") for n in range(1, 81)]})
    items, _ = builder.draw(pool, 42, 40)
    order = [entry["strata"][0] for entry in items]
    assert set(order) == {"S2", "S3"}
    assert order != sorted(order)  # stratum-major would have been every S2 then every S3
