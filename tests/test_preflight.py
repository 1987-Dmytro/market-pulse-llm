"""The preflight instrument, driven against a repo built for the purpose.

Every assertion is about a shape the REAL records use, but none of them reads the real
records: a test pinned to `results/prereg_5c2_run.json`'s current contents goes red the
next time a contract seals something, which is a shelf life, not a check
([[a_green_suite_can_have_a_shelf_life]]).
"""

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "preflight.py"
spec = importlib.util.spec_from_file_location("preflight", SCRIPT)
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """A git repo with one module, one note and one sealed record — the three channels."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "src").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "results").mkdir()
    (tmp_path / "src" / "money.py").write_text("CAP_USD = 20.00\n", encoding="utf-8")
    # The P1 consumer: it quotes the VALUE and never names the constant.
    (tmp_path / "docs" / "note.md").write_text("The line is $20.00 and it is enforced.\n", "utf-8")
    monkeypatch.setattr(preflight, "REPO_ROOT", tmp_path)
    return tmp_path


def seal(repo: Path, name: str, body: dict) -> None:
    (repo / "results" / name).write_text(json.dumps(body), encoding="utf-8")


def test_the_value_channel_finds_the_note_that_never_names_the_constant(repo):
    """The whole point of block 2: `git grep CAP_USD` cannot see this line, and it is a
    consumer. A preflight that only greps the name reports zero prose and is wrong."""
    assert preflight.literals_for("CAP_USD") == ["20.00"]
    assert preflight.git_grep("CAP_USD", ("docs/",)) == []
    assert [path for path, _, _ in preflight.git_grep("20.00", ("docs/",))] == ["docs/note.md"]


def test_all_three_pin_shapes_land_in_the_registry(repo):
    """Sibling-key, `borrowed` map, and a frozen list with no digest. The walk knew only
    the first when it was written and the STATUS control below is what caught that."""
    seal(
        repo,
        "prereg_one.json",
        {
            "instruments": {"scorer": {"module": "src/money.py", "sha256": "a" * 64}},
            "producer": {"borrowed": {"src/other.py": "b" * 64}},
            "frozen_when_the_pod_exists": ["docs/note.md"],
        },
    )
    registry = preflight.pin_registry()
    assert [f for _, f, _ in registry["src/money.py"]] == [".instruments.scorer.sha256"]
    assert registry["src/other.py"][0][2] == "b" * 64
    assert registry["docs/note.md"][0][2] is None, "a freeze is a pin even with no digest"


def test_a_git_dirty_list_is_not_a_pin(repo):
    """The negative control on the frozen-list rule. Records carry `git.dirty` — the
    files that happened to be uncommitted when the record was written — and reading
    those as pins would answer «may I edit this» with a yes-or-no about the past."""
    seal(repo, "run_one.json", {"git": {"commit": "c" * 40, "dirty": ["src/money.py"]}})
    assert preflight.pin_registry() == {}


def test_a_moved_file_reads_DIFFERS_and_an_unmoved_one_does_not(repo, capsys):
    """The digest block earns its place only if it can go both ways."""
    live = preflight.digest("src/money.py")
    seal(repo, "prereg_two.json", {"parser": {"module": "src/money.py", "sha256": live}})
    seal(repo, "prereg_three.json", {"parser": {"module": "docs/note.md", "sha256": "d" * 64}})
    registry = preflight.pin_registry()

    preflight.preflight("src/money.py", registry, limit=12)
    assert "1 of 1 pinned paths match every digest on them" in capsys.readouterr().out

    preflight.preflight("docs/note.md", registry, limit=12)
    out = capsys.readouterr().out
    assert "DIFFERS" in out and "0 of 1 pinned paths match" in out


def test_the_status_control_fires_when_the_walk_misses_a_named_pin(repo, capsys):
    """The control that caught this module's own first version, asserted as a REFUSAL and
    not as a warning nobody reads: `main()` returns 1 and the run is not clean. STATUS
    names four files as pinned, so a walk that finds none of them has stopped seeing
    pins — the failure mode is silent by construction ([[guard_selftest_negative_control]]).
    """
    monkey = "src/market_pulse/prompts.py"
    assert monkey in preflight.STATUS_NAMED_PINS, "the control is about the real STATUS list"
    assert preflight.main(["CAP_USD"]) == 1
    assert "STATUS names these as pinned and the walk missed them" in capsys.readouterr().err

    seal(
        repo,
        "prereg_all.json",
        {"producer": {"borrowed": dict.fromkeys(preflight.STATUS_NAMED_PINS, "e" * 64)}},
    )
    assert preflight.main(["CAP_USD"]) == 0, "and it clears once every named pin is found"


def test_the_real_repo_satisfies_its_own_control():
    """Driven against the production records, because that is the claim the instrument
    makes when a contract pastes its output: on THIS repo the four pins STATUS names are
    found. It is the one assertion here that is allowed to depend on the real tree."""
    registry = preflight.pin_registry()
    assert [p for p in preflight.STATUS_NAMED_PINS if p not in registry] == []
