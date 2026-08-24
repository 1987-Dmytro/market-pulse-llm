#!/usr/bin/env python3
"""`make check`, with a proof that the tree did not move under it.

Twice — Dv785 in `lora-c-close` and Dv792 in `lora-c-run` — a ten-minute suite had to be KILLED
rather than quoted, because something arrived mid-run and got written down. Neither offending edit
was code: one was a fix just decided on, the other the operator's ruling landing in
`knowledge/hot.md`, which `scripts/volume_calc_5c1.py` greps a price literal out of. A reading taken
across a moving tree describes neither tree, and the failure is invisible in the reading itself —
`3 682 passed` looks the same either way ([[while_a_verifier_runs_the_repo_is_read_only]]).

So the stamp stops being a habit and becomes the instrument: `HEAD` and `git status --porcelain`
are taken BEFORE and AFTER the suite, and a move makes this target exit non-zero with «reading VOID
— the tree moved». The suite's own exit code is reported beside it and never replaces it: a green
suite over a moved tree is still VOID.

**The whitelisted paths.** Both are written by the Stop hook, `scripts/brain-session-end.py`, on
its own schedule and not by anything a contract does: `knowledge/daily_logs/` (it appends a
`- HH:MM: session ended (auto)` line, so the day file may appear as `??` mid-run) and
`knowledge/index.md` (it regenerates the vault index whenever a vault file is added — which is what
voided Dv802's first closing reading, over a GREEN suite). Both are whitelisted for ONE registered
reason: NO TEST OPENS EITHER. That is a check, not a belief —
`tests/test_lora_c_armb.py::test_the_whitelisted_directory_is_read_by_no_test` parses every test
module and fails the day one of these names is passed to a call, so the whitelist stops being true
the moment its licence stops being true.

`knowledge/index.md` joined the list by the team lead's ruling (о) of 2026-08-24, on that criterion
and after re-running it — an inherited claim about a directory that grows every week is the shape
this instrument exists to refuse ([[a_claim_no_number_can_check]]).

**What the whitelist does NOT license.** `scripts/refresh-hot-cache.py` reads `knowledge/daily_logs/`
and WRITES `knowledge/hot.md`. The whitelist covers the two hook outputs appearing; it covers no
cache refresh, and `knowledge/hot.md` stays outside it BY NAME — `scripts/volume_calc_5c1.py` greps
a price literal out of that file and nine tests read the result, so it is a suite input and a
mid-run edit there is precisely the move that voided Dv785 and Dv792.

Nothing is written to the repository: the reading is this command's own output, and a stamp file
under a tracked path would be the very move it is checking for.

    make check-stamped
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

WHITELIST = ("knowledge/daily_logs/", "knowledge/index.md")
"""Path prefixes whose porcelain lines may appear or change while the suite runs.

Both are Stop-hook outputs that no test reads. `knowledge/hot.md` is deliberately absent: it IS a
suite input, and a whitelist wide enough to be convenient is a whitelist that licenses the move it
was built to catch."""


def head() -> str:
    return run(["git", "rev-parse", "--short", "HEAD"]).strip()


def porcelain() -> list[str]:
    return [line for line in run(["git", "status", "--porcelain"]).splitlines() if line.strip()]


def run(command: list[str]) -> str:
    return subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, check=True).stdout


def stamp(when: str, at: str, lines: list[str]) -> None:
    """One side's reading, FLUSHED before the next thing writes to the terminal.

    The suite is a subprocess writing straight to the inherited file descriptor, so a buffered
    `print` here lands after ten minutes of pytest output and the line that says BEFORE appears
    below the run it was taken before. The stamps are correct either way; the ORDER is the whole
    legibility of the proof, and a reader who has to reconstruct it will not.
    """
    print(f"{when:<7} HEAD {at}", flush=True)
    for line in lines:
        print(f"        {line}", flush=True)
    if not lines:
        print("        (working tree clean)", flush=True)


def path_of(line: str) -> str:
    """The path a porcelain line is about — the rename target where there is one."""
    return line[3:].split(" -> ")[-1].strip().strip('"')


def moved(before: list[str], after: list[str]) -> list[str]:
    """The porcelain lines that are not in both readings and are not whitelisted."""
    difference = sorted(set(before) ^ set(after))
    return [line for line in difference if not path_of(line).startswith(WHITELIST)]


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    command = argv or ["make", "check"]

    head_before, porcelain_before = head(), porcelain()
    stamp("BEFORE", head_before, porcelain_before)

    suite = subprocess.run(command, cwd=REPO_ROOT)

    head_after, porcelain_after = head(), porcelain()
    stamp("AFTER", head_after, porcelain_after)
    print(f"suite   {' '.join(command)} → exit {suite.returncode}", flush=True)

    drifted = moved(porcelain_before, porcelain_after)
    if head_before != head_after or drifted:
        print(
            f"reading VOID — the tree moved: HEAD {head_before} → {head_after},"
            f" porcelain {drifted or 'unchanged outside the whitelist'}."
            " The suite's exit code above describes neither tree and may not be quoted.",
            flush=True,
        )
        return 2
    print(
        f"reading HOLDS — HEAD {head_after}, tree unmoved outside {list(WHITELIST)}",
        flush=True,
    )
    return suite.returncode


if __name__ == "__main__":
    raise SystemExit(main())
