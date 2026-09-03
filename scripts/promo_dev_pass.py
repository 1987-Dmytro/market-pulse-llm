#!/usr/bin/env python3
"""S9 — the dev-40 pass over the promo-signal instrument. $0 until `--run` exists.

The draw (`results/promo_threads_draw.json`, seed 42) named 40 dev threads; the team lead labelled
every comment of them WITH TEXT in `docs/labels-promo-dev.jsonl`. This script renders what the model
reads for those threads, and turns one answer back into the row shape the grader scores.

**The render is shown before anything is bought.** Ruling 03.09 asks for the RENDERED prompt of one
dev thread at $0, so the team lead reads the law the model will actually obey rather than the
module's source. `--render` is that command.

**The answer is joined back per comment, not per signal.** Gold is one row per comment with a
`signal_types` LIST; the model answers with an `about` row per comment and free-standing `signal`
rows. `predicted_rows` joins them on `msg_id` — a comment the model said nothing about produces no
row and the grader counts it as a miss, which is what
[[an_abstention_is_an_answer]] asks for: silence is scored, never dropped.

    python3.11 scripts/promo_dev_pass.py --render 6009
    python3.11 scripts/promo_dev_pass.py --render 6009 --channel @VARUS_channel
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

import draw_promo_threads as draw  # noqa: E402

from market_pulse import promo_prompts  # noqa: E402

DRAW = REPO_ROOT / "results" / "promo_threads_draw.json"


def dev_threads(path: Path = DRAW) -> list[dict]:
    """The draw's dev rows, both strata, in the record's own order."""
    body = json.loads(path.read_text(encoding="utf-8"))
    return [row for stratum in sorted(body["draw"]) for row in body["draw"][stratum]["dev"]]


def thread_of(row: dict) -> tuple[str, list[dict]]:
    """One thread's post text and its comments, from the frozen v1 archive the draw read.

    The join is the draw's own — `parent_msg_id` against the post's `msg_id`, both as strings — so
    a thread rendered here is the thread that was drawn and labelled, not a re-derived neighbour.
    """
    stem, root = row["store_file"], str(row["thread_root"])
    posts = {str(one.get("msg_id")): one for one in draw.rows(draw.POSTS / f"{stem}.jsonl")}
    if root not in posts:
        raise SystemExit(f"{row['channel']} root {root}: no post in data/raw/posts/{stem}.jsonl")
    comments = [
        one
        for one in draw.rows(draw.COMMENTS / f"{stem}.jsonl")
        if str(one.get("parent_msg_id")) == root
    ]
    return posts[root].get("text") or "", comments


def render_thread(row: dict) -> str:
    post, comments = thread_of(row)
    return promo_prompts.render(row["channel"], row["thread_root"], post, comments)


def predicted_rows(row: dict, answer: dict) -> list[dict]:
    """One model answer → gold-shaped rows, one per comment the model placed."""
    types: dict[str, set] = {}
    for signal in answer.get("signals") or []:
        types.setdefault(str(signal.get("msg_id")), set()).add(signal.get("type"))
    return [
        {
            "channel": row["channel"],
            "thread_root": str(row["thread_root"]),
            "msg_id": str(one.get("msg_id")),
            "subject_type": one.get("subject_type"),
            "subject": one.get("subject"),
            "source": one.get("source"),
            "signal_types": sorted(types.get(str(one.get("msg_id")), set()), key=str),
        }
        for one in (answer.get("about") or [])
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", metavar="THREAD_ROOT", required=True)
    parser.add_argument("--channel", default=None, help="disambiguate a root two channels share")
    args = parser.parse_args(argv)

    found = [
        row
        for row in dev_threads()
        if str(row["thread_root"]) == str(args.render)
        and (args.channel is None or row["channel"] == args.channel)
    ]
    if len(found) != 1:
        raise SystemExit(
            f"--render {args.render}: {len(found)} dev threads match"
            f"{' in ' + args.channel if args.channel else ''} — name --channel to pick one"
        )
    rendered = render_thread(found[0])
    print(rendered)
    print()
    print(f"--- codebook_version  {promo_prompts.codebook_version()}")
    print(f"--- extractor_version {promo_prompts.extractor_version(rendered)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
