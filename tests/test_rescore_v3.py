"""Re-scoring against v3: from dumps only, both G1b readings, and nothing overwritten.

The numbers here are not gate results and the file they land in is not the gate file,
so what has to hold is provenance rather than arithmetic (`build_gates` is tested in
tests/test_eval_zero_shot.py): the dump is the audited one, a run without a dump is
named rather than dropped, the two G1b denominators stay apart, and a second run adds
nothing. `results/baselines.json` is read and never written — a v3 row appearing in
the gate file would be a Phase 4 verdict nobody decided.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import rescore_v3 as rescorer  # noqa: E402
import show_results  # noqa: E402

COMMENTS = [
    {
        "id": "@c:1",
        "sentiment": "negative",
        "sarcasm": False,
        "intents": ["price"],
        "unclear": False,
        "language": "ua",
    },
    {
        "id": "@c:2",
        "sentiment": "neutral",
        "sarcasm": False,
        "intents": [],
        "unclear": False,
        "language": "ru",
    },
]
POSTS = [{"id": "@p:1", "relevant": True, "post_type": "promo", "brands": [], "unclear": False}]
HOLDOUT = [
    {"id": "@h:1", "sentiment": "negative", "sarcasm": True, "unclear": False, "language": "ua"},
    {"id": "@h:2", "sentiment": "negative", "sarcasm": True, "unclear": False, "language": "ua"},
]
BASE_PRED = {
    "comments_test": {
        "@c:1": {"sentiment": "neutral", "sarcasm": False, "intents": ["price"]},
        "@c:2": {"sentiment": "neutral", "sarcasm": False, "intents": []},
    },
    "posts_test": {"@p:1": {"relevant": True, "post_type": "other", "brands": []}},
    # right on @h:1, wrong on both labels of @h:2 — so the base model's v3 error union
    # is one row, and the pre-registered slice below is two: the denominators differ.
    "sarcasm_holdout": {
        "@h:1": {"sentiment": "negative", "sarcasm": True, "intents": []},
        "@h:2": {"sentiment": "positive", "sarcasm": False, "intents": []},
    },
}
ARM_PRED = {
    "comments_test": {
        "@c:1": {"sentiment": "negative", "sarcasm": False, "intents": ["price"]},
        "@c:2": {"sentiment": "neutral", "sarcasm": False, "intents": []},
    },
    "posts_test": {"@p:1": {"relevant": True, "post_type": "promo", "brands": []}},
    "sarcasm_holdout": {
        "@h:1": {"sentiment": "negative", "sarcasm": True, "intents": []},
        "@h:2": {"sentiment": "positive", "sarcasm": False, "intents": []},
    },
}
GATES = [
    {
        "gate": "G1a",
        "metric": "sentiment macro-F1 (comments_test)",
        "values": {"overall": 0.5},
        "n": {"overall": 2},
    }
]


def write_dump(path: Path, predictions: dict) -> None:
    path.write_text(
        "".join(
            json.dumps({"id": row_id, "input": name, "pred": pred}) + "\n"
            for name, rows in predictions.items()
            for row_id, pred in rows.items()
        ),
        encoding="utf-8",
    )


def case(tmp_path, drop=None):
    """A base run, an arm and a dumpless row, over a three-file v3 set."""
    frozen = tmp_path / "frozen"
    frozen.mkdir()
    gold = {"comments_test": COMMENTS, "posts_test": POSTS, "sarcasm_holdout": HOLDOUT}
    for name, rows in gold.items():
        (frozen / f"{name}_v3.jsonl").write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
        )
    base_dump, arm_dump = tmp_path / "base.jsonl", tmp_path / "arm.jsonl"
    write_dump(base_dump, BASE_PRED)
    write_dump(
        arm_dump,
        {name: {k: v for k, v in rows.items() if k != drop} for name, rows in ARM_PRED.items()},
    )

    def run(stamp, dump, arm=None):
        return {
            "model": "m",
            "timestamp": stamp,
            "gates": GATES,
            "diagnostics": {},
            "config": {
                "predictions_path": str(dump),
                "predictions_sha256": rescorer.digest(dump),
                "fine_tune": {"arm": arm} if arm else None,
            },
        }

    results = tmp_path / "baselines.json"
    results.write_text(
        json.dumps(
            {
                "m": [
                    run("t-base", base_dump),
                    run("t-arm", arm_dump, "real-only"),
                    {
                        "model": "m",
                        "timestamp": "t-nodump",
                        "gates": [],
                        "diagnostics": {},
                        "config": {"seed": 42},
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    frozen_v3 = tmp_path / "frozen_v3.json"
    frozen_v3.write_text(
        json.dumps(
            {
                "v2_sha256": {},
                "v3_sha256": {
                    f"{name}_v3.jsonl": rescorer.digest(frozen / f"{name}_v3.jsonl")
                    for name in gold
                },
            }
        ),
        encoding="utf-8",
    )
    slice_path = tmp_path / "g1b_slice.json"
    slice_path.write_text(json.dumps({"ids": ["@h:1", "@h:2"]}), encoding="utf-8")
    out = tmp_path / "rescores_v3.json"
    return {
        "out": out,
        "results": results,
        "argv": [
            "--results",
            str(results),
            "--frozen-v3",
            str(frozen_v3),
            "--frozen",
            str(frozen),
            "--slice",
            str(slice_path),
            "--out",
            str(out),
        ],
        "arm_dump": arm_dump,
    }


def test_every_dumped_run_is_rescored_and_the_dumpless_one_is_named(tmp_path, capsys):
    it = case(tmp_path)
    assert rescorer.main(it["argv"]) == 0

    printed = capsys.readouterr().out
    assert "SKIPPED, no per-row dump: m @ t-nodump" in printed
    records = json.loads(it["out"].read_text())
    assert [record["source"]["record_timestamp"] for record in records] == ["t-base", "t-arm"]
    assert {record["gold_version"] for record in records} == {"v3"}


def test_the_two_g1b_readings_keep_their_own_denominators(tmp_path):
    it = case(tmp_path)
    rescorer.main(it["argv"])

    arm = json.loads(it["out"].read_text())[1]
    assert arm["g1b"]["original_slice"]["n"] == 2  # the pre-registered ids
    assert arm["g1b"]["v3_slice"]["ids"] == ["@h:2"]  # the base model's own v3 errors
    assert arm["g1b"]["v3_slice"]["n"] == 1
    assert arm["g1b"]["original_slice"]["entry"]["fixed"] == 1  # @h:1 fixed, @h:2 not
    assert arm["g1b"]["v3_slice"]["entry"]["fixed"] == 0


def test_a_dump_that_moved_stops_the_run(tmp_path):
    it = case(tmp_path)
    it["arm_dump"].write_text(
        it["arm_dump"].read_text().replace("promo", "other"), encoding="utf-8"
    )
    with pytest.raises(SystemExit, match="not the predictions that were scored"):
        rescorer.main(it["argv"])


def test_a_gold_row_the_dump_never_scored_stops_the_run(tmp_path):
    it = case(tmp_path, drop="@c:2")
    with pytest.raises(SystemExit, match="rows of comments_test are not in the dump"):
        rescorer.main(it["argv"])


def test_a_second_run_appends_nothing_and_never_writes_the_gate_file(tmp_path, capsys):
    it = case(tmp_path)
    rescorer.main(it["argv"])
    before = (it["out"].read_bytes(), it["results"].read_bytes())

    assert rescorer.main(it["argv"]) == 0
    assert "0 record(s) appended" in capsys.readouterr().out
    assert (it["out"].read_bytes(), it["results"].read_bytes()) == before


def test_show_results_v3_prints_both_columns(tmp_path, capsys):
    it = case(tmp_path)
    rescorer.main(it["argv"])
    capsys.readouterr()

    history = json.loads(it["results"].read_text())
    assert show_results.show_v3(json.loads(it["out"].read_text()), history) == 0
    printed = capsys.readouterr().out
    assert "0.5000 -> " in printed  # the v2 value beside the v3 one
    assert "never a gate result" in printed
