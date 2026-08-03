"""The second round the failed strata require, and the pack that gates it (4.5g3).

Two scripts, one question each. The re-run must send back exactly what the gate refused — the
whole population of every failed stratum and not one row more — and the pack must not draw its
fresh hundred from the rows whose verdicts wrote the prompt being tested.
"""

import csv
import json
import sys
from hashlib import sha256
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import build_sitting_pack as sitting  # noqa: E402
import build_wave2_pack as wave2  # noqa: E402
import rerun_failed_strata as rerun  # noqa: E402
from market_pulse import zero_shot  # noqa: E402
from recheck_with_captions import FakeAsker  # noqa: E402

from test_sitting_pack import precheck_row, write_lines  # noqa: E402


def spread(count):
    """`count` rows of each of the three strata, so every population is known by construction."""
    return (
        [precheck_row(i, "доставка затримується") for i in range(count)]
        + [precheck_row(100 + i, "коротко") for i in range(count)]
        + [
            precheck_row(200 + i, "довгий коментар про смак цього морозива, дуже")
            for i in range(count)
        ]
    )


def bench(tmp_path, rows, failed=("general",), judged=()):
    """A re-labelled batch, the gate record that sent part of it back, and a store."""
    batch = write_lines(tmp_path / "batch.jsonl", rows)
    captions = write_lines(tmp_path / "captions.jsonl", [])
    store = tmp_path / "posts"
    store.mkdir(exist_ok=True)
    write_lines(store / "c.jsonl", [{"channel": "@c", "msg_id": 1, "text": "Новинка: сирок"}])

    pools = sitting.strata(rows)
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
                "precheck": {
                    "strata": {
                        name: {"population": len(pool), "drawn": 2} for name, pool in pools.items()
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "gates.json").write_text(
        json.dumps(
            {
                "manifest": str(tmp_path / "manifest.json"),
                "bar": 0.9,
                "passed": sorted(set(pools) - set(failed)),
                "failed": sorted(failed),
                "second_round_rows": sum(len(pools[name]) for name in failed),
                "strata": {name: {"agreement": 0.81} for name in pools},
                "rows": [
                    {"id": row_id, "verdict": verdict, "notes": ""} for row_id, verdict in judged
                ],
            }
        ),
        encoding="utf-8",
    )
    return {"batch": batch, "captions": captions, "posts": store}


def run_rerun(tmp_path, paths, extra=()):
    return rerun.main(
        [
            "--batch-in",
            str(paths["batch"]),
            "--batch-out",
            str(tmp_path / "out.jsonl"),
            "--gates",
            str(tmp_path / "gates.json"),
            "--manifest",
            str(tmp_path / "manifest.json"),
            "--captions",
            str(paths["captions"]),
            "--posts",
            str(paths["posts"]),
            "--outcomes",
            str(tmp_path / "outcomes.jsonl"),
            "--record",
            str(tmp_path / "rerun.json"),
            "--ledger",
            str(tmp_path / "ledger.json"),
            *extra,
        ],
        asker=FakeAsker(zero_shot.Budget(rerun.CAP_USD, rerun.CAP_USD)),
    )


def out_rows(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def test_the_whole_population_of_a_failed_stratum_goes_back_and_nothing_else_moves(tmp_path):
    """A stratum below the bar sends back its whole population, not the hundred that were
    judged — the rule the manifest registered before the pack went out."""
    rows = spread(4)
    paths = bench(tmp_path, rows, failed=("general",))
    before = paths["batch"].read_text(encoding="utf-8").splitlines()
    assert run_rerun(tmp_path, paths) == 0

    record = json.loads((tmp_path / "rerun.json").read_text(encoding="utf-8"))["runs"][-1]
    assert record["scope"]["re_asked"] == 4, "general holds 4 rows and all four go back"
    assert record["scope"]["copied_unchanged"] == 8
    after = (tmp_path / "out.jsonl").read_text(encoding="utf-8").splitlines()
    moved = [old != new for old, new in zip(before, after, strict=True)]
    general = {row["id"] for row in sitting.strata(rows)["general"]}
    assert {json.loads(new)["id"] for new, changed in zip(after, moved) if changed} <= general
    assert sum(1 for new in after if json.loads(new)["id"] not in general) == 8
    for old, new in zip(before, after, strict=True):
        if json.loads(old)["id"] not in general:
            assert old == new, "a passed stratum's row is copied byte for byte"


def test_two_failed_strata_send_back_both_populations(tmp_path):
    rows = spread(4)
    paths = bench(tmp_path, rows, failed=("general", "service-rich"))
    assert run_rerun(tmp_path, paths) == 0
    record = json.loads((tmp_path / "rerun.json").read_text(encoding="utf-8"))["runs"][-1]
    scope = record["scope"]
    assert scope["re_asked"] == 8, "both populations, not one"
    # a row the model answered unreadably is not rewritten, so it is copied like a passed one
    assert scope["copied_unchanged"] == 12 - scope["relabelled"]


def test_a_gate_record_with_nothing_failed_stops_the_run(tmp_path):
    rows = spread(4)
    paths = bench(tmp_path, rows, failed=())
    with pytest.raises(SystemExit, match="every stratum passed the bar"):
        run_rerun(tmp_path, paths)


def test_a_population_that_no_longer_derives_stops_the_run(tmp_path):
    """`the whole population` names a set of rows. If the batch moved, that phrase points at a
    different set than the one the gate refused."""
    rows = spread(4)
    paths = bench(tmp_path, rows)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    manifest["precheck"]["strata"]["general"]["population"] = 9
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(SystemExit, match="derives as 4 rows and the sealed manifest recorded 9"):
        run_rerun(tmp_path, paths)


def test_a_gate_record_about_another_sitting_is_refused(tmp_path):
    rows = spread(4)
    paths = bench(tmp_path, rows)
    gates = json.loads((tmp_path / "gates.json").read_text(encoding="utf-8"))
    gates["manifest"] = "results/sitting_45f_manifest.json"
    (tmp_path / "gates.json").write_text(json.dumps(gates), encoding="utf-8")
    with pytest.raises(SystemExit, match="a stratum's verdict does not transfer"):
        run_rerun(tmp_path, paths)


def test_the_in_sample_signal_is_split_by_the_verdict_it_came_from(tmp_path):
    """Movement on a row the sitting called `incorrect` is the prompt doing what it was told;
    movement on a `correct` one is what that cost. Reported apart, and labelled in-sample."""
    rows = spread(4)
    general = sorted(row["id"] for row in sitting.strata(rows)["general"])
    paths = bench(
        tmp_path,
        rows,
        judged=[(general[0], "incorrect"), (general[1], "correct")],
    )
    assert run_rerun(tmp_path, paths) == 0
    block = json.loads((tmp_path / "rerun.json").read_text(encoding="utf-8"))["runs"][-1]
    assert block["in_sample"]["judged_rows_re_asked"] == {"incorrect": 1, "correct": 1}
    assert "In-sample" in block["in_sample"]["note"]


# --- the pack ------------------------------------------------------------------------------


def seal(tmp_path, rows, judged=()):
    """A batch, its re-run record, and the gate record — everything the pack builder reads."""
    paths = bench(tmp_path, rows, judged=judged)
    (tmp_path / "rerun.json").write_text(
        json.dumps(
            {
                "runs": [
                    {
                        "task": wave2.TASK,
                        "smoke": False,
                        "scope": {
                            "batch_sha256": sha256(paths["batch"].read_bytes()).hexdigest(),
                            # the pack reads the previous batch back to measure the shift; here
                            # the two are the same file, so the shift is zero by construction
                            "source": str(paths["batch"]),
                            "relabelled": len(rows),
                        },
                        "diff": {
                            "changed_any_field": 3,
                            "changed_rate": 3 / len(rows),
                            "per_field": {"intents": 3},
                        },
                        "in_sample": {
                            "judged_rows_re_asked": {"correct": len(judged)},
                            "moved_a_field": {"correct": 1},
                            "note": "In-sample.",
                        },
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    return paths


def build(tmp_path, paths, rows=4, extra=()):
    assert (
        wave2.main(
            [
                "--pack",
                str(tmp_path / "pack"),
                "--manifest",
                str(tmp_path / "wave2.json"),
                "--batch",
                str(paths["batch"]),
                "--rerun",
                str(tmp_path / "rerun.json"),
                "--gates",
                str(tmp_path / "gates.json"),
                "--captions",
                str(paths["captions"]),
                "--posts",
                str(paths["posts"]),
                "--rows",
                str(rows),
                *extra,
            ]
        )
        == 0
    )
    return json.loads((tmp_path / "wave2.json").read_text(encoding="utf-8"))


def pack_rows(tmp_path):
    with (tmp_path / "pack" / "wave2_100.csv").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=sitting.DELIMITER))


def test_the_rows_whose_verdicts_wrote_the_prompt_are_out_of_the_frame(tmp_path):
    """The v2.1 rulings were distilled from the first sitting's verdicts. Drawing the fresh
    hundred from those rows would score the prompt against its own source."""
    rows = spread(6)
    already = [(row["id"], "correct") for row in rows[:10]]
    paths = seal(tmp_path, rows, judged=already)
    manifest = build(tmp_path, paths, rows=4)

    drawn = {row["id"] for row in pack_rows(tmp_path)}
    assert not drawn & {row_id for row_id, _ in already}
    assert manifest["precheck"]["frame"]["rows"] == len(rows) - 10
    assert manifest["precheck"]["frame"]["excluded"] == sorted(row_id for row_id, _ in already)
    assert "its own source" in manifest["precheck"]["frame"]["why"]


def test_the_pack_is_blind_and_says_so_in_no_column(tmp_path):
    rows = spread(6)
    paths = seal(tmp_path, rows)
    build(tmp_path, paths, rows=6)

    shipped = pack_rows(tmp_path)
    assert list(shipped[0]) == list(sitting.PRECHECK_COLUMNS)
    assert "annotator" not in shipped[0] and "stratum" not in shipped[0]
    assert all(row["verdict"] == "" and row["notes"] == "" for row in shipped)


def test_a_batch_that_is_not_the_one_the_rerun_wrote_stops_the_build(tmp_path):
    rows = spread(6)
    paths = seal(tmp_path, rows)
    paths["batch"].write_text(
        paths["batch"].read_text(encoding="utf-8").replace("коротко", "коротшe"), encoding="utf-8"
    )
    with pytest.raises(SystemExit, match="not the batch the re-run wrote"):
        build(tmp_path, paths, rows=4)


def test_a_pack_with_verdicts_in_it_is_not_quietly_rebuilt(tmp_path):
    rows = spread(6)
    paths = seal(tmp_path, rows)
    build(tmp_path, paths, rows=4)
    path = tmp_path / "pack" / "wave2_100.csv"
    shipped = pack_rows(tmp_path)
    shipped[0]["verdict"] = "correct"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=sitting.PRECHECK_COLUMNS,
            delimiter=sitting.DELIMITER,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(shipped)

    with pytest.raises(SystemExit, match="already carries 1 verdicts"):
        build(tmp_path, paths, rows=4)
    manifest = build(tmp_path, paths, rows=4, extra=["--force"])
    assert manifest["verdicts_present"] == 1, "a forced rebuild says what it destroyed"


def test_the_manifest_pins_its_files_the_prompt_and_the_gate_that_sent_the_rows_back(tmp_path):
    rows = spread(6)
    paths = seal(tmp_path, rows)
    manifest = build(tmp_path, paths, rows=4)

    for name, digest in manifest["sha256"].items():
        assert sha256((tmp_path / "pack" / name).read_bytes()).hexdigest() == digest
    assert manifest["verdicts_present"] == 0, "sealed before a single verdict existed"
    assert manifest["bar"] == 0.9 and "EVERY field" in manifest["precheck"]["rule"]
    assert manifest["prompt"]["task"] == "precheck_v2.1_with_post"
    assert set(manifest["prompt"]["registered_beside"]) == {"precheck_v2_with_post", "T1v2.1"}
    assert manifest["sent_back_by"]["failed"] == ["general"]
    assert "can still hold one class below 0.90" in manifest["precheck"]["one_frame_not_three"]


def test_the_same_seed_draws_the_same_hundred(tmp_path):
    rows = spread(6)
    paths = seal(tmp_path, rows)
    build(tmp_path, paths, rows=4)
    first = [row["id"] for row in pack_rows(tmp_path)]
    build(tmp_path, paths, rows=4, extra=["--force"])
    assert [row["id"] for row in pack_rows(tmp_path)] == first


def test_the_rewritten_rows_say_which_revision_labelled_them(tmp_path):
    """A batch whose provenance lives only in the record beside it cannot be read on its own,
    and this one is the input to a gate pack and, later, to a merge."""
    rows = spread(4)
    paths = bench(tmp_path, rows, failed=("general",))
    assert run_rerun(tmp_path, paths) == 0

    after = {row["id"]: row for row in out_rows(tmp_path / "out.jsonl")}
    general = {row["id"] for row in sitting.strata(rows)["general"]}
    touched = {row_id for row_id in general if after[row_id]["annotator"] == rerun.ANNOTATOR}
    assert touched, "the re-labelled rows carry the v2.1 annotator"
    for row_id, row in after.items():
        if row_id not in touched:
            assert row["annotator"] == "llm-precheck", "and nothing else moved"


def test_a_line_that_moved_a_sixth_field_stops_the_run(tmp_path):
    """The byte proof, and its negation: five fields may move and a sixth may not."""
    row = {
        "id": "@c:1",
        "text": "x",
        "sentiment": "neutral",
        "sarcasm": False,
        "intents": [],
        "unclear": False,
        "annotator": "llm-precheck",
    }
    line = json.dumps(row, ensure_ascii=False)
    labels = {"sentiment": "positive", "sarcasm": False, "intents": ["taste"], "unclear": False}
    assert json.loads(rerun.rewritten(row, line, labels))["annotator"] == rerun.ANNOTATOR
    with pytest.raises(SystemExit, match="more than the five fields it names"):
        rerun.rewritten({**row, "text": "інше"}, line, labels)


def test_the_pack_carries_what_the_rerun_did_to_the_batch_it_is_drawn_from(tmp_path):
    """A gate pack is a pre-registration. Sealing one over labels that already measure as a
    regression would pre-register a failure, so the measurement travels with the pack."""
    rows = spread(6)
    paths = seal(tmp_path, rows, judged=[(row["id"], "correct") for row in rows[:2]])
    manifest = build(tmp_path, paths, rows=4)

    state = manifest["batch_health"]
    assert "should not appear" in state["read_this_first"]
    assert state["changed_any_field"] == 3
    assert state["in_sample"]["moved_a_field"] == {"correct": 1}
    assert set(state["distribution_before"]) == {"intents", "no_intent", "unclear", "sarcasm"}
    readme = (tmp_path / "pack" / "README-wave2.md").read_text(encoding="utf-8")
    assert readme.index("ПРОЧТИ ПЕРВЫМ") < readme.index("Заполняешь"), "the warning comes first"
    assert "3 строк из 18" in readme and "сменилось 1" in readme
