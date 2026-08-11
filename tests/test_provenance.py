"""The collapsed `git_state`: the same five answers, from one function.

Five copies existed and had drifted in TWO ways — three sorted the dirty list and two did not, and
each excluded a different set. A clean tree cannot see either: there, all five return `dirty: []`.
So the fixture below is deliberately dirty, and deliberately arranged so that porcelain order is
not sorted order — `git status --porcelain` emits tracked changes first and untracked after, each
block path-sorted, so one untracked file whose name sorts before the tracked ones separates the
two readings.

The expected values were MEASURED from the five copies before they were removed, by pointing each
module's `REPO_ROOT` at this same fixture. They are transcribed here as the specification the
collapse had to meet: a record's `git` block is provenance, and a producer whose output quietly
re-sorted would make its next row incomparable to its own history for a reason no reader could see.
"""

import subprocess
import sys
from pathlib import Path

import pytest
from market_pulse import provenance

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

TRACKED = (
    "zeta.py",
    "results/baselines.json",
    "results/spend_3b.json",
    "results/zero_shot.json",
    "results/spend_ledger.json",
    "mine.json",
)
UNTRACKED = "aaa_untracked.txt"
"""Sorts before every tracked path above and is emitted after all of them. Without it this whole
file passes with `sorted` deleted from the implementation."""


@pytest.fixture(scope="module")
def dirty_repo(tmp_path_factory) -> Path:
    root = tmp_path_factory.mktemp("dirty-repo")

    def run(*args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(root), *args], capture_output=True, text=True, check=True
        ).stdout

    run("init", "-q")
    run("config", "user.email", "t@example.invalid")
    run("config", "user.name", "t")
    for name in TRACKED:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("one\n", encoding="utf-8")
    run("add", "-A")
    run("commit", "-qm", "init")
    for name in TRACKED:
        (root / name).write_text("two\n", encoding="utf-8")
    (root / UNTRACKED).write_text("x\n", encoding="utf-8")
    return root


def head(root: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()


def test_the_fixture_really_separates_the_two_readings(dirty_repo):
    """The control on every expectation below. If porcelain ever came back globally sorted, the
    sorted and unsorted readings would be the same list and this file would prove nothing."""
    emitted = provenance.git_state(root=dirty_repo)["dirty"]
    assert emitted[-1] == UNTRACKED
    assert emitted != sorted(emitted)


# What each copy returned on this fixture, measured before it was deleted (2026-08-11).
MEASURED = {
    "run_baseline": [
        UNTRACKED,
        "mine.json",
        "results/spend_3b.json",
        "results/spend_ledger.json",
        "results/zero_shot.json",
        "zeta.py",
    ],
    "eval_zero_shot": [
        UNTRACKED,
        "mine.json",
        "results/baselines.json",
        "results/spend_3b.json",
        "zeta.py",
    ],
    "train_xlmr_baseline": [
        UNTRACKED,
        "mine.json",
        "results/spend_ledger.json",
        "results/zero_shot.json",
        "zeta.py",
    ],
    "freeze_testsets_v3": [
        "results/baselines.json",
        "results/spend_3b.json",
        "results/spend_ledger.json",
        "results/zero_shot.json",
        "zeta.py",
        UNTRACKED,
    ],
    "build_audit_pack": [
        "results/baselines.json",
        "results/spend_3b.json",
        "results/spend_ledger.json",
        "results/zero_shot.json",
        "zeta.py",
        UNTRACKED,
    ],
}


def test_run_baseline_s_reading(dirty_repo):
    state = provenance.git_state(
        dirty_repo / "results" / "baselines.json", sort=True, root=dirty_repo
    )
    assert state == {"commit": head(dirty_repo), "dirty": MEASURED["run_baseline"]}


def test_eval_zero_shot_s_reading(dirty_repo):
    state = provenance.git_state(
        dirty_repo / "results" / "zero_shot.json",
        dirty_repo / "results" / "spend_ledger.json",
        sort=True,
        root=dirty_repo,
    )
    assert state == {"commit": head(dirty_repo), "dirty": MEASURED["eval_zero_shot"]}


def test_train_xlmr_s_reading(dirty_repo):
    """Its two ignores were written as repo-relative STRINGS, not paths — both shapes have to
    compare against the same porcelain output, which is what `_rel` is for."""
    state = provenance.git_state(
        "results/baselines.json", "results/spend_3b.json", sort=True, root=dirty_repo
    )
    assert state == {"commit": head(dirty_repo), "dirty": MEASURED["train_xlmr_baseline"]}


@pytest.mark.parametrize("name", ["freeze_testsets_v3", "build_audit_pack"])
def test_the_two_unsorted_readings(dirty_repo, name):
    state = provenance.git_state(dirty_repo / "mine.json", root=dirty_repo)
    assert state == {"commit": head(dirty_repo), "dirty": MEASURED[name]}


def test_the_record_being_written_is_left_out_of_its_own_dirty_list(dirty_repo):
    """It is dirty on every rerun and absent on the first, so a field that kept it would say more
    about how often the producer ran than about what it ran against."""
    assert (
        "mine.json" not in provenance.git_state(dirty_repo / "mine.json", root=dirty_repo)["dirty"]
    )
    assert "mine.json" in provenance.git_state(root=dirty_repo)["dirty"]


def test_no_script_defines_its_own_copy_any_more():
    """The point of the collapse, and the thing that can silently come back: a sixth copy pasted
    into the next driver. Every `def git_state` left in `scripts/` must delegate."""
    for path in sorted((REPO_ROOT / "scripts").glob("*.py")):
        source = path.read_text(encoding="utf-8")
        if "def git_state(" not in source:
            continue
        body = source.split("def git_state(", 1)[1].split("\ndef ", 1)[0]
        assert "provenance.git_state(" in body, path.name
        assert "subprocess.run" not in body, f"{path.name} still shells out to git itself"


def test_the_five_migrated_producers_still_answer(dirty_repo, monkeypatch):
    """Driven through the modules themselves, not through the shared function: the collapse is
    only done if the names the forty importers use still return the same shape."""
    import build_audit_pack
    import eval_zero_shot
    import freeze_testsets_v3
    import run_baseline
    import train_xlmr_baseline

    monkeypatch.setattr(provenance, "REPO_ROOT", dirty_repo)
    monkeypatch.setattr(run_baseline, "RESULTS", dirty_repo / "results" / "baselines.json")
    monkeypatch.setattr(eval_zero_shot, "RESULTS", dirty_repo / "results" / "zero_shot.json")
    monkeypatch.setattr(eval_zero_shot, "LEDGER", dirty_repo / "results" / "spend_ledger.json")

    assert run_baseline.git_state()["dirty"] == MEASURED["run_baseline"]
    assert eval_zero_shot.git_state()["dirty"] == MEASURED["eval_zero_shot"]
    assert train_xlmr_baseline.git_state()["dirty"] == MEASURED["train_xlmr_baseline"]
    assert (
        freeze_testsets_v3.git_state(dirty_repo / "mine.json")["dirty"]
        == MEASURED["freeze_testsets_v3"]
    )
    assert (
        build_audit_pack.git_state(dirty_repo / "mine.json")["dirty"]
        == MEASURED["build_audit_pack"]
    )
