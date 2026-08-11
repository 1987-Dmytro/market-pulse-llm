"""What a record can honestly say about the code that produced it.

A results file can never name the commit that will contain it, so the honest record is the commit
the numbers were produced against **and** the list of files that were not in it. `dirty` naming
something under `src/` or `scripts/` means the commit does not reproduce the numbers.

There were five copies of this function — `run_baseline`, `eval_zero_shot`, `train_xlmr_baseline`,
`freeze_testsets_v3` and `build_audit_pack`, the last of which 51 scripts import from — and
they had drifted in two ways, not one: three sorted the dirty list and two did not, and each
excluded a different set of paths. That is invisible on a clean tree, where all five return
``dirty: []``, and it is why the collapse is a fix-on-touch (operator, 2026-08-11) rather than a
tidy-up: `git status --porcelain` emits tracked changes first and untracked after, each block
path-sorted, so on a tree with both the two readings genuinely differ.

Nothing here changes what any record holds. Both readings are kept and named, and the migrated
call sites pass the same ignore sets they always did — the equality test in
`tests/test_provenance.py` pins all five against outputs measured from the copies before they were
removed.

Not in `market_pulse.records`: that module states its own contract in its first paragraph — pure
functions over already-loaded data, and "the package is not the place that knows where the repo
is". This one shells out to git and has to know.
"""

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _rel(path, root: Path) -> str:
    """A path as `git status --porcelain` spells it: relative to the repo, else as given.

    Callers pass both shapes — `RESULTS` is an absolute `Path` and `train_xlmr_baseline`'s two
    ignores were written as repo-relative strings — and both have to compare against the same
    porcelain output.
    """
    candidate = Path(path)
    return str(candidate.relative_to(root)) if candidate.is_relative_to(root) else str(path)


def git_state(*ignore, sort: bool = False, root: Path | None = None) -> dict:
    """HEAD plus every path that differs from it — provenance, not a boolean.

    ``ignore`` is the record being written and anything else that is dirty by construction: a
    file that is dirty on every rerun and absent on the first would make the field say more about
    how often this ran than about what it ran against.

    ``sort`` is the difference between the two readings that existed, exposed rather than
    resolved. Porcelain order is "tracked, then untracked", so an untracked file sorts into the
    middle of the list under ``sort=True`` and lands at the end under ``sort=False``. Which one a
    record uses is not a preference to standardise away — every past record on disk was written
    under one of them, and quietly re-sorting a producer would make its next row incomparable to
    its own history for a reason no reader could see.
    """

    # read at CALL time, not bound as a default: the tests point it at a throwaway repo, and a
    # default evaluated at import would make every one of them a measurement of this checkout.
    root = REPO_ROOT if root is None else root

    def run(*args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=root, capture_output=True, text=True, check=True
        ).stdout

    excluded = {_rel(path, root) for path in ignore if path is not None}
    # `XY <path>`, and the X of an unstaged change is a space — stripping the output first eats
    # it and the first path loses a character.
    dirty = [line.split(maxsplit=1)[1] for line in run("status", "--porcelain").splitlines()]
    kept = [path for path in dirty if path not in excluded]
    return {"commit": run("rev-parse", "HEAD").strip(), "dirty": sorted(kept) if sort else kept}
