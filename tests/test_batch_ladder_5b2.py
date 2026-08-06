"""The ladder's three decisions: what shares a call, what counts as identical, and which N wins.

Nothing here talks to a pod. What is tested is the part that decides something — the rule
SPEC amendment 3.11 (2) pre-registered, applied as code, including the two readings that a
"largest identical N" one-liner gets wrong: an arm that lost rows, and an arm whose N was
never actually exercised because the carve does not hold that many rows of one rendering.
"""

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
spec = importlib.util.spec_from_file_location(
    "batch_ladder_5b2", REPO_ROOT / "scripts" / "batch_ladder_5b2.py"
)
ladder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ladder)

ROWS = [{"id": f"t1:{n}", "task": "T1v2_with_post", "text": f"row {n}"} for n in range(19)] + [
    {"id": f"t2:{n}", "task": "T2", "text": f"post {n}"} for n in range(5)
]


def arm(size: int, contents: dict, scored: int | None = None, failed=None) -> dict:
    rows = [
        {"id": row["id"], "task": row["task"], "content": contents.get(row["id"], "same")}
        for row in ROWS[: scored if scored is not None else len(ROWS)]
    ]
    return {"batch_size": size, "scored": len(rows), "rows": rows, "failed": failed}


def test_a_call_never_straddles_the_two_renderings():
    """One call carries one task, so a batch that mixed them could not be sent at all —
    and grouping first is what makes N mean the same thing for both renderings."""
    cut = ladder.chunks(ROWS, 8)
    assert all(len({row["task"] for row in chunk}) == 1 for chunk in cut)
    assert [len(chunk) for chunk in cut] == [8, 8, 3, 5]


def test_what_each_n_actually_exercised_is_not_what_it_asked_for():
    """The carve holds 5 T2 rows. At N=16 the T2 arm batches 5, and a record that only
    said "16" would claim evidence for a batch size no call ever ran."""
    sizes = {}
    for chunk in ladder.chunks(ROWS, 16):
        sizes[chunk[0]["task"]] = max(sizes.get(chunk[0]["task"], 0), len(chunk))
    assert sizes == {"T1v2_with_post": 16, "T2": 5}


def test_identity_is_byte_identity_keyed_by_row():
    reference = arm(1, {})
    assert ladder.compare(reference, arm(8, {}))["identical"] is True
    off = ladder.compare(reference, arm(8, {"t1:3": "different"}))
    assert off["identical"] is False
    assert off["differing_ids"] == ["t1:3"]
    assert off["first_difference"]["batch_1"] == "same"
    assert off["first_difference"]["batch_8"] == "different"


def test_an_arm_that_lost_rows_is_not_identical_however_identical_its_rows_are():
    """The reading that would silently pass: comparing over the intersection reports the
    missing rows as agreement, and an out-of-memory at N=16 would adopt 16."""
    reference = arm(1, {})
    short = ladder.compare(reference, arm(16, {}, scored=12))
    assert short["identical"] is False
    assert "cannot be identical" in short["why"]

    died = ladder.compare(reference, arm(16, {}, failed="chunk 0: OutOfMemoryError"))
    assert died["identical"] is False
    assert "OutOfMemoryError" in died["why"]


def test_the_largest_identical_n_wins():
    verdicts = {16: {"identical": False}, 8: {"identical": True}, 4: {"identical": True}}
    picked = ladder.candidate(verdicts)
    assert picked["candidate"] == 8
    assert picked["identical_to_batch_1"] == [8, 4]
    assert picked["by"] == "largest-identical"


def test_none_identical_falls_back_to_eight_because_spec_says_so():
    """Greedy is already MEASURED non-invariant on this stack (ADR phase4-own-pod-anchor
    §(c)), so this is the expected path — the paid run is what decides adoption, not this."""
    verdicts = {size: {"identical": False} for size in ladder.LADDER}
    picked = ladder.candidate(verdicts)
    assert picked["candidate"] == 8 == ladder.FALLBACK_N
    assert picked["identical_to_batch_1"] == []
    assert picked["by"] == "spec-fallback-none-identical"


def test_the_ladder_is_the_one_spec_pre_registered():
    assert ladder.LADDER == (16, 8, 4)
    assert "byte-identical" in ladder.SELECTION_RULE
    assert "3.11 (2)" in ladder.SELECTION_RULE


def smoke_row(row_id: str, task: str, tokens=(700, 20), finish="stop", parsed=True) -> dict:
    return {
        "id": row_id,
        "task": task,
        "finish_reason": finish,
        "parsed": parsed,
        "usage": {"prompt_tokens": tokens[0], "completion_tokens": tokens[1]},
    }


def smoke_record(tmp_path, rows) -> Path:
    path = tmp_path / "serving_5b.json"
    path.write_text(
        json.dumps({"step": "5b smoke", "batch_size": 1, "rows": rows}), encoding="utf-8"
    )
    return path


def test_the_batch_one_arm_is_regressed_against_the_5b1_smoke_by_id(tmp_path):
    """The smoke stores its rows round-robin across renderings and the ladder groups them
    by rendering — a positional comparison would call every row changed."""
    rows = [smoke_row("t1:0", "T1v2_with_post"), smoke_row("t2:0", "T2", tokens=(600, 18))]
    path = smoke_record(tmp_path, list(reversed(rows)))
    arm = {"rows": rows}
    out = ladder.regression_vs_smoke(arm, path)
    assert out["compared"] == 2
    assert out["unchanged"] == 2
    assert out["moved"] == {}
    assert "NOT byte-for-byte" in out["limit"]


def test_a_row_whose_tokens_moved_is_named_with_both_readings(tmp_path):
    path = smoke_record(tmp_path, [smoke_row("t1:0", "T1v2_with_post", tokens=(700, 20))])
    arm = {"rows": [smoke_row("t1:0", "T1v2_with_post", tokens=(700, 21))]}
    out = ladder.regression_vs_smoke(arm, path)
    assert out["unchanged"] == 0
    assert out["moved"]["t1:0"]["was"]["completion_tokens"] == 20
    assert out["moved"]["t1:0"]["now"]["completion_tokens"] == 21


def test_the_regression_compares_only_what_the_smoke_record_holds():
    """The brief asks for byte-for-byte and the committed artifact cannot answer that:
    `results/serving_5b.json` stores no reply text. Saying so is the deliverable."""
    assert ladder.COMPARABLE == ("finish_reason", "parsed", "prompt_tokens", "completion_tokens")
