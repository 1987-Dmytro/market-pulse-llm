"""The sitting the up-label precheck is accepted or rejected on.

Four properties are worth a test and the rest is plumbing: the strata are what the rule says
and not what the previous draw left over, the file does not tell the operator which stratum a
row is in, a post with no text of its own reaches the operator tagged exactly as it reached the
model, and nothing that arrives with verdicts already in it is rebuilt. The reseal adds a fifth:
"the same 300 ids" is asserted against the manifest it supersedes rather than reasoned about.
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


def write_lines(path: Path, rows) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )
    return path


def bench(tmp_path, rows, posts=((1, "Новинка: сирок"),), captions=(), per_stratum=2):
    """A precheck batch, its captions and media, an empty redo population, and a micro-pack."""
    paths = {
        "batch": write_lines(tmp_path / "batch.jsonl", rows),
        "captions": write_lines(tmp_path / "captions.jsonl", captions),
        "redo_rows": write_lines(tmp_path / "redo_rows.jsonl", []),
        "source": write_lines(tmp_path / "source.jsonl", rows),
        "staged": write_lines(tmp_path / "source_tax2.jsonl", rows),
    }
    (tmp_path / "media.json").write_text(json.dumps({"entries": {}}), encoding="utf-8")
    (tmp_path / "quiz.json").write_text(
        json.dumps({"runs": [{"applied": [], "unchanged": [], "held": []}]}), encoding="utf-8"
    )
    (tmp_path / "drop.json").write_text(
        json.dumps({"populations": {"all": {"emptied": 0, "emptied_from": {}}}}), encoding="utf-8"
    )
    (tmp_path / "relabel.json").write_text(json.dumps({"runs": [], "fixes": []}), encoding="utf-8")

    micro_pack = tmp_path / "packs" / "unreadable14.csv"
    micro_pack.parent.mkdir(parents=True, exist_ok=True)
    micro_pack.write_text("id;text;intents_v1;intents_v2;notes\n", encoding="utf-8")
    (tmp_path / "micro.json").write_text(
        json.dumps(
            {
                "pack": "packs/unreadable14.csv",
                "readme": "packs/README.md",
                "rows": 0,
                "to_fill": "intents_v2",
                "sha256": {"packs/unreadable14.csv": sha256(micro_pack.read_bytes()).hexdigest()},
            }
        ),
        encoding="utf-8",
    )
    paths["micro_pack"] = micro_pack

    store = tmp_path / "posts"
    store.mkdir(exist_ok=True)
    write_lines(
        store / "c.jsonl",
        [{"channel": "@c", "msg_id": mid, "text": text} for mid, text in posts],
    )
    paths["posts"] = store

    # the manifest this rebuild supersedes: the same draw, computed with the same functions.
    # A bench built for the too-small-stratum case cannot draw at all, and that is the case
    # under test rather than a broken fixture.
    try:
        _, where = sitting.draw(sitting.strata(rows), per_stratum)
    except SystemExit:
        where = {}
    (tmp_path / "sealed.json").write_text(
        json.dumps({"sha256": {"precheck300.csv": "0" * 64}, "precheck": {"stratum_of": where}}),
        encoding="utf-8",
    )
    return paths


def build(tmp_path, paths, monkeypatch, per_stratum=2, extra=()):
    monkeypatch.setattr(relabel, "SOURCES", {"comments_train": paths["source"]})
    assert (
        sitting.main(
            [
                "--pack",
                str(tmp_path / "pack"),
                "--manifest",
                str(tmp_path / "manifest.json"),
                "--batch",
                str(paths["batch"]),
                "--captions",
                str(paths["captions"]),
                "--media-manifest",
                str(tmp_path / "media.json"),
                "--redo-rows",
                str(paths["redo_rows"]),
                "--quiz-record",
                str(tmp_path / "quiz.json"),
                "--drop",
                str(tmp_path / "drop.json"),
                "--relabel-record",
                str(tmp_path / "relabel.json"),
                "--supersedes",
                str(tmp_path / "sealed.json"),
                "--micro-manifest",
                str(tmp_path / "micro.json"),
                "--root",
                str(tmp_path),
                "--posts",
                str(paths["posts"]),
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


def spread(count, parent=1):
    """`count` rows of each stratum, so a draw of any size up to `count` is possible."""
    return (
        [precheck_row(i, "доставка затримується", parent=parent) for i in range(count)]
        + [precheck_row(100 + i, "коротко", parent=parent) for i in range(count)]
        + [
            precheck_row(200 + i, "довгий коментар про смак цього морозива, дуже", parent=parent)
            for i in range(count)
        ]
    )


def test_a_short_row_that_is_also_service_rich_belongs_to_one_stratum():
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


def test_the_pack_does_not_say_which_stratum_a_row_is_in(tmp_path, monkeypatch):
    rows = spread(10)
    manifest = build(tmp_path, bench(tmp_path, rows, per_stratum=5), monkeypatch, per_stratum=5)

    pack = rows_of(tmp_path / "pack" / "precheck300.csv")
    assert list(pack[0]) == list(sitting.PRECHECK_COLUMNS)
    assert "stratum" not in " ".join(pack[0])
    where = manifest["precheck"]["stratum_of"]
    order = [where[row["id"]] for row in pack]
    assert len(order) == 15 and len(set(order)) == 3
    # the three draws are shuffled together, so the file is not three blocks
    assert order != sorted(order, key=str), "row order would hand the operator the stratum"


def test_the_denominators_and_the_second_round_rule_are_written_before_handover(
    tmp_path, monkeypatch
):
    rows = spread(4)
    manifest = build(tmp_path, bench(tmp_path, rows), monkeypatch)

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
    assert manifest["verdicts_present"] == 0, "the evidence for `rebuilt before a verdict existed`"


@pytest.mark.parametrize(
    "post,caption,shown",
    [
        ("Новинка: сирок", (), "Новинка: сирок"),
        (
            "",
            ({"channel": "@c", "msg_id": 1, "caption": "Полиця", "kind": "image"},),
            "[картинка] Полиця",
        ),
        (
            "",
            ({"channel": "@c", "msg_id": 1, "caption": "З чим?", "kind": "poll"},),
            "[опрос] З чим?",
        ),
        ("", (), "(нет текста — ни картинки, ни опроса)"),
    ],
)
def test_the_post_reaches_the_operator_tagged_as_it_reached_the_model(
    tmp_path, monkeypatch, post, caption, shown
):
    """A vision model's description is not the post's own words, and a poll question is not a
    description. Judging one as the other is the same error on either side of the table."""
    rows = spread(2)
    paths = bench(tmp_path, rows, posts=((1, post),), captions=caption)
    build(tmp_path, paths, monkeypatch)
    assert {row["post"] for row in rows_of(tmp_path / "pack" / "precheck300.csv")} == {shown}


def test_a_pack_with_verdicts_in_it_is_not_quietly_rebuilt(tmp_path, monkeypatch):
    rows = spread(2)
    paths = bench(tmp_path, rows)
    build(tmp_path, paths, monkeypatch)

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
        build(tmp_path, paths, monkeypatch)
    assert sitting.filled(path) == 1, "the refusal left the operator's work alone"
    manifest = build(tmp_path, paths, monkeypatch, extra=["--force"])
    assert sitting.filled(path) == 0
    assert manifest["verdicts_present"] == 1, "a forced rebuild says what it destroyed"


def test_a_draw_that_moved_stops_the_reseal(tmp_path, monkeypatch):
    """ "Same 300 ids" is the claim the whole reseal rests on: refreshed labels were supposed to
    leave the sample alone, so a draw that moved means something upstream of it changed."""
    rows = spread(4)
    paths = bench(tmp_path, rows)
    sealed = json.loads((tmp_path / "sealed.json").read_text(encoding="utf-8"))
    moved = dict(sealed["precheck"]["stratum_of"])
    moved["@c:999"] = "general"
    sealed["precheck"]["stratum_of"] = moved
    (tmp_path / "sealed.json").write_text(json.dumps(sealed), encoding="utf-8")
    monkeypatch.setattr(relabel, "SOURCES", {"comments_train": paths["source"]})
    with pytest.raises(SystemExit, match="the draw moved"):
        build(tmp_path, paths, monkeypatch)


def test_a_bundled_file_that_moved_since_its_own_manifest_stops_the_build(tmp_path, monkeypatch):
    """The 4.5f micro-pack is pinned in place, so the operator may already have started on
    it — a sitting that bundles a file it cannot describe has no manifest."""
    rows = spread(2)
    paths = bench(tmp_path, rows)
    paths["micro_pack"].write_text(
        'id;text;intents_v1;intents_v2;notes\n@c:9;x;[];["taste"];\n', encoding="utf-8"
    )
    with pytest.raises(SystemExit, match="carries 1 labels"):
        build(tmp_path, paths, monkeypatch)


def test_a_stratum_too_small_to_draw_from_stops_the_build(tmp_path, monkeypatch):
    rows = [precheck_row(1, "доставка затримується"), precheck_row(2, "коротко")]
    paths = bench(tmp_path, rows, per_stratum=1)
    with pytest.raises(SystemExit, match="general: 0 rows, fewer than the 1"):
        build(tmp_path, paths, monkeypatch, per_stratum=1)


def test_the_manifest_pins_every_file_it_ships_and_names_the_one_it_supersedes(
    tmp_path, monkeypatch
):
    rows = spread(2)
    paths = bench(tmp_path, rows)
    manifest = build(tmp_path, paths, monkeypatch)

    for name, digest in manifest["sha256"].items():
        assert sha256((tmp_path / "pack" / name).read_bytes()).hexdigest() == digest
    assert set(manifest["sha256"]) == {
        "precheck300.csv",
        "emptied_redo.csv",
        "media_map.csv",
        "README-sitting.md",
    }
    assert manifest["precheck"]["source_sha256"] == sha256(paths["batch"].read_bytes()).hexdigest()
    assert manifest["supersedes"]["manifest"].endswith("sealed.json")
    assert "not edited and not deleted" in manifest["supersedes"]["what_moved"]
