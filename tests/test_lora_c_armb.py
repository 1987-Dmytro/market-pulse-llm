"""`docs/PROMPT-lora-c-armb.md` — the stamped verifier, arm B's dataset, and the re-derived money.

Everything here is $0. The heavy readings — the encode census over 666 rows and the rendering of
the 160 synthetic queries — are bought once by the producers and asserted here from their result
files; a test that re-rendered them would be a second answer the day one of them moved.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_stamped  # noqa: E402

ARM_B_RECORD = REPO_ROOT / "results" / "lora_c_arm_b.json"
ARM_B_FILE = REPO_ROOT / "results" / "pass1_sft_v3_arm_b.jsonl"
TRAIN_FILE = REPO_ROOT / "results" / "pass1_sft_v3_train.jsonl"
CENSUS = REPO_ROOT / "results" / "lora_c_encode_census_arm_b.json"
REGISTRATION = REPO_ROOT / "results" / "prereg_lora_c.json"


def record() -> dict:
    return json.loads(ARM_B_RECORD.read_text(encoding="utf-8"))


def registration() -> dict:
    return json.loads(REGISTRATION.read_text(encoding="utf-8"))


# --- step 0.5: the moving-tree verifier as an instrument -----------------------------------------


def test_the_whitelisted_directory_is_read_by_no_test():
    """The check that licenses the whitelist, RUN rather than written down beside it.

    `scripts/check_stamped.py` lets `knowledge/daily_logs/` move under a suite because no test opens
    it. That is an assertion about a directory that grows every week, so it is measured here
    ([[a_claim_no_number_can_check]]). A plain grep cannot do it — this file names the directory in
    its own prose — so every test module is parsed and only string constants that are NOT docstrings
    are counted: a path literal is caught, a sentence is not.

    What counts as reading it is a CALL that carries the name — `open(...)`, `Path(...)`,
    `subprocess.run([... ])` — and not a string that merely spells it: the test below this one uses
    day-log paths as porcelain fixtures, which is naming the directory, not opening it.

    Its ceiling, named rather than hidden: a test that assembled the path from parts, or bound it to
    a name first, would evade this exactly as it would evade a grep. What it does catch is the way
    anyone actually writes it.

    The two files in the repo that DO read the directory — `scripts/refresh-hot-cache.py` and
    `scripts/brain-session-end.py` — are hooks, and the second half of this test is that no test
    drives either of them. That is the caveat `check_stamped.py` carries: the whitelist licenses the
    day-log file appearing, never a cache refresh mid-run.
    """
    import ast

    # Spelled in halves so this file's own assertions are not what the scan finds.
    needles = ("daily" + "_logs", "refresh-hot" + "-cache", "brain-session" + "-end")
    for path in sorted((REPO_ROOT / "tests").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        docstrings = {
            id(node.body[0].value)
            for node in ast.walk(tree)
            if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef)
            and node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        }
        opened = [
            inner.value
            for call in ast.walk(tree)
            if isinstance(call, ast.Call)
            for inner in ast.walk(call)
            if isinstance(inner, ast.Constant)
            and isinstance(inner.value, str)
            and any(needle in inner.value for needle in needles)
            and id(inner) not in docstrings
        ]
        assert opened == [], (
            f"{path.name} passes {opened} to a call — the whitelisted directory, or a hook that"
            " reads it and writes hot.md, is now a suite input and may not move under a reading"
        )


def test_the_stamped_verifier_voids_a_reading_when_a_suite_input_moves():
    """The whitelist accepts the Stop hook's day log and refuses `hot.md` — both directions.

    `knowledge/hot.md` is the case the instrument exists for: `scripts/volume_calc_5c1.py` greps a
    price literal out of it and nine tests read the result, so a mid-run edit there is exactly the
    move that voided Dv785 and Dv792 ([[while_a_verifier_runs_the_repo_is_read_only]]).
    """
    before = [" M docs/STATUS.md"]
    day_log_appeared = before + ["?? knowledge/daily_logs/2026-08-24.md"]
    day_log_changed = before + [" M knowledge/daily_logs/2026-08-24.md"]
    hot_changed = before + [" M knowledge/hot.md"]
    index_changed = before + [" M knowledge/index.md"]

    assert check_stamped.moved(before, day_log_appeared) == []
    assert check_stamped.moved(before, day_log_changed) == []
    assert check_stamped.moved(before, hot_changed) == [" M knowledge/hot.md"]
    assert check_stamped.moved(before, index_changed) == [" M knowledge/index.md"]
    assert check_stamped.moved(before, before) == []
    assert check_stamped.moved(day_log_appeared, before) == [], "a line DISAPPEARING is also a move"


def test_the_stamped_verifier_reports_the_suites_own_exit_code():
    """Driven end to end on a trivial command, both directions.

    The instrument is worth nothing if it swallows a red suite, so it is run for real — twice, on
    `true` and on `false` — rather than reasoned about ([[guard_selftest_negative_control]]). The
    tree does not move under either, so both readings HOLD and the exit code is the command's own.
    """
    assert check_stamped.main(["true"]) == 0
    assert check_stamped.main(["false"]) == 1


def test_the_stamped_verifier_parses_a_rename_and_a_quoted_path():
    """`path_of` reads the porcelain line's TARGET, which is what a whitelist is about."""
    lines = {
        " M knowledge/hot.md": "knowledge/hot.md",
        "?? knowledge/daily_logs/2026-08-24.md": "knowledge/daily_logs/2026-08-24.md",
        'R  a.md -> "knowledge/hot.md"': "knowledge/hot.md",
    }
    for line, want in lines.items():
        assert check_stamped.path_of(line) == want
