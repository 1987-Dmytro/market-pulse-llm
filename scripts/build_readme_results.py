#!/usr/bin/env python3
"""The README's «Results» block, from result files — regenerated, never typed.

    PYTHONPATH=src python3.11 scripts/build_readme_results.py        # rewrites README.md between the markers

Ruling 06.09 (cc) addendum, «ship as measured»: the S2 numbers go into the README with their files,
and the README fails loudly when a file is missing. The block is the same three holdout readings
the screen prints, read by the same function — `build_promo_screen.s2_readings` — so the README and
the screen cannot disagree, and a missing source is that reader's own named refusal. Missing markers
are this script's. Running it twice writes the same bytes: nothing here reads a clock.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_promo_screen as screen  # noqa: E402

README = REPO_ROOT / "README.md"
START = (
    "<!-- S2 READINGS — written by scripts/build_readme_results.py from the result files each row"
    " names; regenerate, never edit -->"
)
END = "<!-- /S2 READINGS -->"


def block(rows: list[dict]) -> str:
    """The markdown the markers enclose: one row per reading, then the tie count the P1 record carries.

    The two bars in the opening sentence are READ off the first reading's record like every other
    number here — typing «0.80» would put a threshold in prose, where no file can move it
    ([[a_threshold_that_lives_in_prose]]); each row's own cell still carries its own file's bar.
    """
    bars = rows[0]["bars"]
    lines = [
        "**S2 — reactions under promo posts, graded on the frozen holdouts.** Per comment: what it"
        f" is about (subject, bar {bars['subject_agreement']['bar']:.2f}); per thread: what it says"
        f" (signal types, bar {bars['signal_type_agreement']['bar']:.2f}). Shipped as"
        " measured (ruling 06.09 (cc)); every number below is the named file's.",
        "",
        "| reading | subject | signal | file |",
        "|---|---|---|---|",
    ]
    for row in rows:
        sub, sig = row["bars"]["subject_agreement"], row["bars"]["signal_type_agreement"]
        lines.append(
            f"| {row['label']} | {sub['value']:.4f} ({row['agreed']}/{row['comments']})"
            f" {'✅' if sub['held'] else '❌'} bar {sub['bar']:.2f}"
            f" | {sig['value']:.4f} {'✅' if sig['held'] else '❌'} bar {sig['bar']:.2f}"
            f" | `{row['file']}` :: {row['block']} |"
        )
    for row in rows:
        if row["misses"]:
            lines += [
                "",
                f"Of the {row['misses']['total']} comments still missed with P1,"
                f" {row['misses']['gold_unsure']} are rows the gold itself marked `unsure` — the"
                " codebook allows two readings there (a store-stock complaint: the chain or the"
                " product; a post in the chain's own channel: the chain or the post).",
            ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readme", type=Path, default=README)
    parser.add_argument("--results", type=Path, default=screen.RESULTS)
    args = parser.parse_args(argv)

    text = args.readme.read_text(encoding="utf-8")
    if START not in text or END not in text or text.index(START) > text.index(END):
        raise SystemExit(
            f"build-readme REFUSED: {args.readme} carries no `{END}` block to write into — the"
            " markers are the contract, and a README without them is not edited blind"
        )
    rows = screen.s2_readings(args.results)
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    args.readme.write_text(f"{head}{START}\n{block(rows)}\n{END}{tail}", encoding="utf-8")
    print(f"wrote the S2 block of {args.readme}: {len(rows)} readings from {args.results}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
