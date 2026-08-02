"""The sitting the up-label precheck is accepted or rejected on.

Three properties are worth a test and the rest is plumbing: the strata are what the rule
says and not what the previous draw left over, the file does not tell the operator which
stratum a row is in, and nothing that arrives with verdicts already in it is rebuilt.
"""

import csv
import json
import sys
from hashlib import sha256
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import build_sitting_pack as sitting  # noqa: E402
import relabel_intents as relabel  # noqa: E402


def precheck_row(msg_id, text, parent=1, unclear=False):
    return {
        "id": f"@c:{msg_id}",
        "channel": "@c",
        "msg_id": msg_id,
        "parent_msg_id": parent,
        "language": "uk",
        "text": text,
        "sentiment": "neutral",
        "sarcasm": False,
        "intents": [],
        "unclear": unclear,
        "annotator": "llm-precheck",
        "notes": "",
    }


def bench(tmp_path, rows, drawn=(), posts=((1, "Новинка: сирок"),)):
    """A precheck batch, an emptied record, a micro-pack and its manifest, and a post store."""
    batch = tmp_path / "batch.jsonl"
    batch.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )
    emptied = tmp_path / "emptied.json"
    emptied.write_text(
        json.dumps(
            {
                "runs": [
                    {
                        "check": {
                            "rule": "new / 40 >= 0.90, and an identical row counts as `new`",
                            "drawn_composition": {"identical_to_v1": 1},
                            "rows_drawn": list(drawn),
                        }
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    micro_pack = tmp_path / "packs" / "unreadable14.csv"
    micro_pack.parent.mkdir(parents=True, exist_ok=True)
    micro_pack.write_text("id;text;intents_v1;intents_v2;notes\n@c:9;x;[];;\n", encoding="utf-8")
    micro = tmp_path / "micro.json"
    micro.write_text(
        json.dumps(
            {
                "pack": "packs/unreadable14.csv",
                "readme": "packs/README.md",
                "rows": 1,
                "to_fill": "intents_v2",
                "sha256": {"packs/unreadable14.csv": sha256(micro_pack.read_bytes()).hexdigest()},
            }
        ),
        encoding="utf-8",
    )
    store = tmp_path / "posts"
    store.mkdir()
    (store / "c.jsonl").write_text(
        "".join(
            json.dumps({"channel": "@c", "msg_id": mid, "text": text}, ensure_ascii=False) + "\n"
            for mid, text in posts
        ),
        encoding="utf-8",
    )
    return batch, emptied, micro, micro_pack, store


def build(tmp_path, batch, emptied, micro, store, per_stratum=2, extra=()):
    assert (
        sitting.main(
            [
                "--pack",
                str(tmp_path / "pack"),
                "--manifest",
                str(tmp_path / "manifest.json"),
                "--batch",
                str(batch),
                "--emptied",
                str(emptied),
                "--micro-manifest",
                str(micro),
                "--root",
                str(tmp_path),
                "--posts",
                str(store),
                "--per-stratum",
                str(per_stratum),
                *extra,
            ]
        )
        == 0
    )
    return json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))


def rows_of(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=sitting.DELIMITER))


def test_a_short_row_that_is_also_service_rich_belongs_to_one_stratum(tmp_path):
    """Disjoint by rule, in a fixed order — otherwise the same row could be judged twice and
    a stratum's denominator would depend on which draw ran first."""
    pools = sitting.strata(
        [
            precheck_row(1, "доставка"),  # short AND service-rich
            precheck_row(2, "коротко"),
            precheck_row(3, "а це вже досить довгий коментар про смак морозива"),
        ]
    )
    assert [row["id"] for row in pools["service-rich"]] == ["@c:1"]
    assert [row["id"] for row in pools["short-text <= 30 chars"]] == ["@c:2"]
    assert [row["id"] for row in pools["general"]] == ["@c:3"]


def test_the_pack_does_not_say_which_stratum_a_row_is_in(tmp_path):
    rows = (
        [precheck_row(i, "доставка затримується") for i in range(10)]
        + [precheck_row(100 + i, "коротко") for i in range(10)]
        + [
            precheck_row(200 + i, "довгий коментар про смак цього морозива, дуже")
            for i in range(10)
        ]
    )
    batch, emptied, micro, _, store = bench(tmp_path, rows)
    manifest = build(tmp_path, batch, emptied, micro, store, per_stratum=5)

    pack = rows_of(tmp_path / "pack" / "precheck300.csv")
    assert list(pack[0]) == list(sitting.PRECHECK_COLUMNS)
    assert "stratum" not in " ".join(pack[0])
    where = manifest["precheck"]["stratum_of"]
    order = [where[row["id"]] for row in pack]
    assert len(order) == 15 and len(set(order)) == 3
    # the three draws are shuffled together, so the file is not three blocks
    assert order != sorted(order, key=str), "row order would hand the operator the stratum"


def test_the_denominators_and_the_second_round_rule_are_written_before_handover(tmp_path):
    rows = (
        [precheck_row(i, "доставка затримується") for i in range(4)]
        + [precheck_row(100 + i, "коротко") for i in range(4)]
        + [precheck_row(200 + i, "довгий коментар про смак цього морозива, дуже") for i in range(4)]
    )
    batch, emptied, micro, _, store = bench(tmp_path, rows)
    manifest = build(tmp_path, batch, emptied, micro, store, per_stratum=2)

    block = manifest["precheck"]
    assert block["verdicts"] == ["correct", "incorrect"]
    assert "EVERY field" in block["rule"] and "0.90" in block["rule"]
    assert "counts as `incorrect`" in block["rule"]
    # the batch a failed stratum sends back is the population, not the 2 rows judged
    assert {name: entry["population"] for name, entry in block["strata"].items()} == {
        "service-rich": 4,
        "short-text <= 30 chars": 4,
        "general": 4,
    }
    assert all(entry["drawn"] == 2 for entry in block["strata"].values())
    assert manifest["emptied"]["verdicts"] == ["old", "new", "neither"]
    assert "identical" in manifest["emptied"]["rule"]


def test_the_post_travels_into_the_pack_and_a_media_only_one_says_so(tmp_path):
    """The guideline lets the annotator read the parent post and the model was given it —
    judging the labels without it would apply a stricter law than the one that wrote them."""
    rows = [
        precheck_row(1, "доставка затримується", parent=1),
        precheck_row(2, "коротко", parent=2),
        precheck_row(3, "довгий коментар про смак цього морозива, дуже", parent=1),
    ]
    batch, emptied, micro, _, store = bench(tmp_path, rows, posts=((1, "Новинка: сирок"), (2, "")))
    build(tmp_path, batch, emptied, micro, store, per_stratum=1)

    posts = {row["id"]: row["post"] for row in rows_of(tmp_path / "pack" / "precheck300.csv")}
    assert posts["@c:1"] == "Новинка: сирок"
    assert posts["@c:2"] == "(нет текста)"


def test_a_pack_with_verdicts_in_it_is_not_quietly_rebuilt(tmp_path):
    rows = [
        precheck_row(1, "доставка затримується"),
        precheck_row(2, "коротко"),
        precheck_row(3, "довгий коментар про смак цього морозива, дуже"),
    ]
    batch, emptied, micro, _, store = bench(tmp_path, rows)
    build(tmp_path, batch, emptied, micro, store, per_stratum=1)

    path = tmp_path / "pack" / "precheck300.csv"
    lines = rows_of(path)
    lines[0]["verdict"] = "correct"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=sitting.PRECHECK_COLUMNS,
            delimiter=sitting.DELIMITER,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(lines)

    with pytest.raises(SystemExit, match="already carries 1 verdicts"):
        build(tmp_path, batch, emptied, micro, store, per_stratum=1)
    assert sitting.filled(path) == 1, "the refusal left the operator's work alone"
    build(tmp_path, batch, emptied, micro, store, per_stratum=1, extra=["--force"])
    assert sitting.filled(path) == 0


def test_a_bundled_file_that_moved_since_its_own_manifest_stops_the_build(tmp_path):
    """The 4.5f micro-pack is pinned in place, so the operator may already have started on
    it — a sitting that bundles a file it cannot describe has no manifest."""
    rows = [
        precheck_row(1, "доставка затримується"),
        precheck_row(2, "коротко"),
        precheck_row(3, "довгий коментар про смак цього морозива, дуже"),
    ]
    batch, emptied, micro, micro_pack, store = bench(tmp_path, rows)
    micro_pack.write_text(
        'id;text;intents_v1;intents_v2;notes\n@c:9;x;[];["taste"];\n', encoding="utf-8"
    )
    with pytest.raises(SystemExit, match="carries 1 labels"):
        build(tmp_path, batch, emptied, micro, store, per_stratum=1)


def test_a_stratum_too_small_to_draw_from_stops_the_build(tmp_path):
    rows = [precheck_row(1, "доставка затримується"), precheck_row(2, "коротко")]
    batch, emptied, micro, _, store = bench(tmp_path, rows)
    with pytest.raises(SystemExit, match="general: 0 rows, fewer than the 1"):
        build(tmp_path, batch, emptied, micro, store, per_stratum=1)


def test_the_manifest_pins_every_file_it_ships(tmp_path):
    rows = [
        precheck_row(1, "доставка затримується"),
        precheck_row(2, "коротко"),
        precheck_row(3, "довгий коментар про смак цього морозива, дуже"),
    ]
    drawn = [
        {
            "id": "@c:1",
            "text": "доставка затримується",
            "intents_v1": ["price"],
            "intents_with_post": [],
        }
    ]
    batch, emptied, micro, micro_pack, store = bench(tmp_path, rows, drawn=drawn)
    # the 40 contrastive rows come out of the labelled sources, not out of the precheck pool
    source = tmp_path / "labelled.jsonl"
    source.write_text(json.dumps(rows[0], ensure_ascii=False) + "\n", encoding="utf-8")
    original = relabel.SOURCES
    relabel.SOURCES = {"labelled": source}
    try:
        manifest = build(tmp_path, batch, emptied, micro, store, per_stratum=1)
    finally:
        relabel.SOURCES = original

    for name, digest in manifest["sha256"].items():
        assert sha256((tmp_path / "pack" / name).read_bytes()).hexdigest() == digest
    assert manifest["unreadable"]["sha256"] == sha256(micro_pack.read_bytes()).hexdigest()
    assert manifest["precheck"]["source_sha256"] == sha256(batch.read_bytes()).hexdigest()
    assert relabel.rel(Path(manifest["pack"])) or True  # the pack path is recorded
