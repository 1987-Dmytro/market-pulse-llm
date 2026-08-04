"""What v4 is allowed to be: v3 with one column moved, and the operator's word on top.

Everything here is re-derived from the files on disk. The record is the thing under
test, so a test that read its counts would be checking the record against itself.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import freeze_testsets_v4 as v4  # noqa: E402
from market_pulse import scorer  # noqa: E402

FROZEN = REPO_ROOT / "data" / "frozen"
RECORD = json.loads((REPO_ROOT / "results" / "frozen_v4.json").read_text(encoding="utf-8"))


def rows(path: Path) -> dict[str, dict]:
    return {
        json.loads(line)["id"]: json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


V3 = {name: rows(FROZEN / f"{name}_v3.jsonl") for name in v4.INPUTS}
V4 = {name: rows(FROZEN / f"{name}_v4.jsonl") for name in v4.INPUTS}


def test_v4_moves_intents_and_annotator_and_nothing_else():
    """Not "the script only writes those two" — that is the claim. This reads both
    versions off disk and compares every other field of all 758 rows."""
    for name in v4.INPUTS:
        assert set(V3[name]) == set(V4[name]), name
        for row_id, old in V3[name].items():
            new = V4[name][row_id]
            assert {k: v for k, v in new.items() if k not in ("intents", "annotator")} == {
                k: v for k, v in old.items() if k not in ("intents", "annotator")
            }, f"{name} {row_id}"


def test_posts_v4_is_its_v3_file_byte_for_byte():
    """Posts carry no `intents` column at all, so the intents law cannot reach them and
    the v4 name is the whole difference."""
    assert (FROZEN / "posts_test_v4.jsonl").read_bytes() == (
        FROZEN / "posts_test_v3.jsonl"
    ).read_bytes()
    assert RECORD["v4_sha256"]["posts_test_v4.jsonl"] == RECORD["v3_sha256"]["posts_test_v3.jsonl"]


def test_a_row_the_pass_could_not_read_keeps_exactly_its_v3_intents():
    """39 rows, and the honest failure mode: the model answered `{}` on them. Coercing
    that to `[]` — the majority answer — would rewrite gold where the instrument failed."""
    unread = RECORD["unread_by_the_pass"]
    assert len(unread) == v4.EXPECTED["migration_kept_v3"]
    migrated = set(v4.migrated())
    ruled = {*RECORD["audit_ruling_ids"], *RECORD["law_verdict_ids"]}
    # four of the unread rows carry an operator ruling, which supersedes the pass whether
    # or not it answered — calling all 39 "kept" would be wrong about gold on those four
    assert sorted(set(unread) & ruled) == RECORD["unread_but_ruled"]
    kept = RECORD["kept_v3_intents"]
    assert set(kept) == set(unread) - ruled
    for row_id in kept:
        assert row_id not in migrated
        name = "comments_test" if row_id in V3["comments_test"] else "sarcasm_holdout"
        assert V4[name][row_id]["intents"] == V3[name][row_id]["intents"]
        assert V4[name][row_id]["annotator"] == V3[name][row_id]["annotator"]


def test_an_operator_ruling_wins_over_the_pass_on_the_rows_it_covers():
    """Amendment 3.9 (3)'s "ON TOP". The 23 rows where the two disagree are the only
    place the order is observable, so they are what the test reads."""
    passed = v4.migrated()
    ruled = {**v4.ruled_intents()[0], **v4.law_values()}
    disagreed = [i for i, value in ruled.items() if i in passed and set(passed[i]) != set(value)]
    assert len(disagreed) == len(RECORD["superseded_by_a_ruling"])
    for row_id in disagreed:
        assert set(V4["comments_test"][row_id]["intents"]) == set(ruled[row_id])
        assert set(V4["comments_test"][row_id]["intents"]) != set(passed[row_id])


def test_every_ruled_row_carries_the_ruling_and_says_who_wrote_it():
    for row_id in RECORD["audit_ruling_ids"]:
        assert V4["comments_test"][row_id]["annotator"] == v4.ANNOTATOR["audit"]
    for row_id in RECORD["law_verdict_ids"]:
        assert V4["comments_test"][row_id]["annotator"] == v4.ANNOTATOR["law"]
        assert set(V4["comments_test"][row_id]["intents"]) == set(v4.law_values()[row_id])


def test_a_ruling_cannot_cross_the_comment_post_namespace():
    """11 gold comment ids are also post ids. A lookup by id alone wrote a comment's
    intents onto a post row the first time this ran, and the post has no `intents` key
    to overwrite — which is the only reason it raised instead of corrupting the file."""
    comments = set(V3["comments_test"]) | set(V3["sarcasm_holdout"])
    shared = comments & set(V3["posts_test"])
    assert len(shared) == 5
    for row_id in shared:
        assert "intents" not in V4["posts_test"][row_id]


def test_the_holdout_pool_is_single_home_and_the_pristine_file_is_untouched():
    pool = v4.lines_of(v4.POOL)
    pool_v4 = v4.lines_of(REPO_ROOT / RECORD["holdout_pool"]["v4"])
    holdout = set(V3["sarcasm_holdout"])
    assert len(pool) == 971 and len(pool_v4) == v4.EXPECTED["pool_rows"]
    assert not {json.loads(line)["id"] for line in pool_v4} & holdout
    assert len({json.loads(line)["id"] for line in pool} & holdout) == v4.EXPECTED["pool_dropped"]
    assert v4.digest(v4.POOL) == RECORD["holdout_pool"]["pristine_sha256"]


def test_the_older_versions_still_hash_to_what_their_own_records_say():
    """v4 is new files beside v2 and v3, so every published number keeps its meaning."""
    for name, expected in {**RECORD["v2_sha256"], **RECORD["v3_sha256"]}.items():
        assert v4.digest(FROZEN / name) == expected, name


def test_the_recorded_counts_are_what_the_files_say():
    changed = {
        name: sum(
            1
            for row_id, old in V3[name].items()
            if set(old["intents"] if "intents" in old else [])
            != set(V4[name][row_id].get("intents", []))
        )
        for name in v4.INPUTS
    }
    for name in v4.INPUTS:
        assert RECORD["rows"][f"{name}_v4.jsonl"]["rows_changed"] == changed[name], name
        assert RECORD["rows"][f"{name}_v4.jsonl"]["rows"] == len(V4[name])


def test_every_v4_intents_value_is_inside_taxonomy_v2():
    for name in ("comments_test", "sarcasm_holdout"):
        for row_id, row in V4[name].items():
            assert set(row["intents"]) <= set(scorer.INTENTS_V2), (name, row_id, row["intents"])


def test_the_sixth_class_reaches_gold_and_the_v3_files_never_had_it():
    """The whole reason v4 exists: G1c cannot be scored against a test set whose gold
    cannot say `service`."""
    new = sum(
        1
        for name in ("comments_test", "sarcasm_holdout")
        for r in V4[name].values()
        if "service" in r["intents"]
    )
    old = sum(
        1
        for name in ("comments_test", "sarcasm_holdout")
        for r in V3[name].values()
        if "service" in r["intents"]
    )
    assert old == 0 and new > 0


def test_a_derivation_that_lands_on_other_counts_stops_instead_of_writing(monkeypatch):
    """The negative control for every count above: they pass because the derivation
    matched the amendment, not because nothing is checked."""
    monkeypatch.setitem(v4.EXPECTED, "audit_rulings", 30)
    with pytest.raises(SystemExit, match="amendment 3.9 \\(3\\) says 30"):
        v4.main(["--record", "/dev/null"])


def test_the_doc_table_is_the_records_own():
    """docs/frozen-testsets.md quotes the record, or it is a second source of truth. The
    files it describes are hashed; a hand-edited count in the card would not disagree
    with anything."""
    doc = (REPO_ROOT / "docs" / "frozen-testsets.md").read_text(encoding="utf-8")
    assert v4.summary_table(RECORD) in doc
    for count in ("migration_unread", "migration_kept_v3", "rulings_over_the_pass"):
        assert f"{RECORD['counts'][count]}" in doc, count
    assert RECORD["holdout_pool"]["v4"] in doc
