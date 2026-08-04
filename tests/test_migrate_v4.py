"""The 4.5h2 migration pass: which rows it may touch, and what it may move on them.

The pass is the one authorised exception to `relabel_intents.NEVER`, so the tests that
matter are the ones about its edges — the permitted set, the single column, and the
refusal to coerce a reply it cannot read.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import migrate_intents_v4 as migrate  # noqa: E402
import precheck_45h as pre  # noqa: E402
import relabel_intents as relabel  # noqa: E402
import train_qlora  # noqa: E402
from market_pulse import prompts  # noqa: E402

ALLOWED = migrate.allowed()


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def test_the_permitted_set_is_the_508_gold_rows_and_is_read_not_listed():
    """A hand-kept id list would be a second source of truth for the one thing this
    script must not get wrong."""
    assert len(ALLOWED) == 508
    assert len(rows(migrate.GOLD[0])) == 400
    assert len(rows(migrate.GOLD[1])) == 108
    assert set(ALLOWED) == {row["id"] for path in migrate.GOLD for row in rows(path)}


def test_the_permitted_set_is_inside_what_the_standing_guard_forbids():
    """The mirror image: every row this pass may label is a row `relabel_intents`
    refuses, so the exception is contained rather than a hole in the guard."""
    assert set(ALLOWED) <= relabel.forbidden_ids()


def test_the_only_labelling_source_holding_a_permitted_id_is_the_holdout_pool():
    """The 54 dual-home rows of `results/precheck_45h.json`, and nothing else. They are the
    reason amendment 3.9 (3) materialises the pool at 917, and the pool is in
    `train_qlora.NEVER_READ` either way — no training run can open it."""
    overlap = {
        name: len(set(ALLOWED) & {row["id"] for row in rows(path)})
        for name, path in relabel.SOURCES.items()
    }
    assert overlap == {"comments_train": 0, "sarcasm_candidates": 0, "holdout_pool": 54}
    assert relabel.SOURCES["holdout_pool"] in train_qlora.NEVER_READ


def test_no_permitted_row_is_a_comment_training_row_under_either_arm():
    """Amendment 3.9 points arm A at the `_tax2` siblings and arm B at those plus the
    пласт. A gold id among their COMMENT rows would be leakage this pass would then
    relabel. `posts_train.jsonl` is a different namespace — a post and a comment can carry
    the same `@channel:msg_id`, which is why the trainer keys its arms on (task, id) — so
    its 11 shared ids are counted and named rather than asserted away."""
    comment_sources = [*train_qlora.SOURCES["T1"], pre.PLAST]
    for path in comment_sources:
        assert not set(ALLOWED) & {row["id"] for row in rows(path)}, path.name
    posts = set(ALLOWED) & {row["id"] for row in rows(train_qlora.SOURCES["T2"][0])}
    assert len(posts) == 11


def test_the_task_asks_for_intents_alone_and_requires_the_parent_post():
    assert prompts.COMMENT_FIELDS[migrate.TASK] == ("intents",)
    assert migrate.TASK in prompts.WITH_POST
    with pytest.raises(ValueError, match="requires parent post"):
        prompts.build_messages(migrate.TASK, "смачно")


def test_a_produced_line_is_its_v3_line_with_intents_moved_and_nothing_else():
    row, line = next(iter(ALLOWED.values()))
    produced = relabel.relabelled(row, line, ["service"])
    assert json.loads(produced)["intents"] == ["service"]
    assert {k: v for k, v in json.loads(produced).items() if k != "intents"} == {
        k: v for k, v in row.items() if k != "intents"
    }


def test_a_reply_the_parser_cannot_read_is_named_rather_than_emptied():
    """`[]` is the majority answer; coercing to it would flatter the drift and would
    quietly rewrite gold on the rows the model failed."""
    row = next(iter(ALLOWED.values()))[0]
    unusable = migrate.ask_one(row, lambda _: {"choices": [{"message": {"content": "sorry"}}]})
    assert unusable["intents"] is None
    assert unusable["unusable"].startswith("parse:")
    good = migrate.ask_one(
        row, lambda _: {"choices": [{"message": {"content": '{"intents": []}'}}]}
    )
    assert good["intents"] == []


def test_a_smoke_run_writes_the_rows_and_the_record_the_freeze_reads(tmp_path):
    """The write path, driven to the file: `--dry-run` stops before anything is written,
    and an import proves nothing about what lands on disk."""
    out, record = tmp_path / "rows.jsonl", tmp_path / "record.json"
    assert migrate.main(["--smoke", "--rows-out", str(out), "--record", str(record)]) == 0
    produced = rows(out)
    written = json.loads(record.read_text(encoding="utf-8"))["runs"][-1]
    assert len(produced) == written["accounting"]["written"]
    assert len(produced) + written["accounting"]["unusable"] == 508
    assert written["accounting"]["unusable_keep_v3"], "the smoke must exercise that branch"
    assert not (set(written["accounting"]["unusable_keep_v3"]) & {row["id"] for row in produced})
    assert written["task"] == migrate.TASK
    assert written["prompt_sha256"] == {migrate.TASK: prompts.prompt_sha256(migrate.TASK)}
    # the rows come back in the gold files' own order, so the two can be read side by side
    order = list(ALLOWED)
    assert [row["id"] for row in produced] == [i for i in order if i in {r["id"] for r in produced}]


def test_a_resume_refuses_a_file_holding_a_row_this_pass_never_drew(tmp_path):
    """Resuming on top of another run's file would mix two sets of rows into one pass."""
    out = tmp_path / "rows.jsonl"
    out.write_text(json.dumps({"id": "@nowhere:1", "intents": []}) + "\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="not in this source"):
        relabel.already_done(out, ALLOWED)


def test_the_cap_is_the_contract_s_and_the_ledger_is_this_phase_s():
    assert migrate.CAP_USD == 0.30
    assert migrate.LEDGER.name == "spend_45h2.json"
    assert relabel.anchor_key(migrate.PHASE) == "openrouter_total_usage_at_45h2_start"
