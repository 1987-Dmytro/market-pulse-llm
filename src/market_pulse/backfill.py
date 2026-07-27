"""Backfill bookkeeping: the resume cursor and the end-of-run gate summary.

Kept apart from ``scripts/backfill.py``, which does the talking to Telegram, so
both halves stay testable without a session — the same split as the entry check.
"""

import json
import os
from pathlib import Path

# Pre-registered by the team lead before the run. One attempt, and the window is
# not tuned to reach it (docs/SPEC.md §5 discipline).
GATE_COMMENTS = 5000

# A walk that ended for any other reason left history unread, and an unfinished
# walk is indistinguishable from a small corpus once you only look at the totals.
COMPLETE = ("since", "exhausted")


def load_cursor(path: str | Path) -> dict:
    """Resume state per channel: ``{handle: {"newest": id, "oldest": id}}``."""
    cursor = Path(path)
    if not cursor.exists():
        return {}
    try:
        return json.loads(cursor.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        # Restarting the walk costs time; refusing to start costs the whole run.
        # Nothing is duplicated either way — the store dedupes on (channel, msg_id).
        return {}


def save_cursor(path: str | Path, cursor: dict) -> None:
    """Write atomically: a kill mid-write must not lose the position in the walk."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.parent / (target.name + ".tmp")
    tmp.write_text(json.dumps(cursor, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, target)


def channel_row(store, source, handle: str, stopped: str) -> dict:
    """One summary line, counted from the store rather than from this run.

    A resumed run collects a fraction of the corpus; the gate is about how much
    has been collected in total, not about how much the last attempt added.
    """
    posts = store.index("post", handle)
    comments = store.index("comment", handle)
    return {
        "channel": handle,
        "source_id": source.id,
        "comments_enabled": source.comments_enabled,
        "n_posts": posts.count,
        "n_comments": comments.count,
        "first_post": posts.first_date,
        "last_post": posts.last_date,
        "stopped": stopped,
    }


def total_comments(rows: list[dict]) -> int:
    return sum(row["n_comments"] for row in rows)


def render_summary(rows: list[dict], threshold: int = GATE_COMMENTS) -> str:
    header = (
        f"{'channel':<24}{'source':<12}{'posts':>8}{'comments':>10}"
        f"{'oldest':>12}{'newest':>12}  walk"
    )
    lines = [header, "-" * (len(header) + 10)]
    for row in rows:
        lines.append(
            f"{row['channel'][:23]:<24}{row['source_id'][:11]:<12}"
            f"{row['n_posts']:>8}{row['n_comments']:>10}"
            f"{(row['first_post'] or '—')[:10]:>12}{(row['last_post'] or '—')[:10]:>12}"
            f"  {row['stopped']}"
        )

    total = total_comments(rows)
    lines.append("")
    lines.append(f"TOTAL comments: {total} / {threshold} (pre-registered gate)")

    unfinished = [row["channel"] for row in rows if row["stopped"] not in COMPLETE]
    if total >= threshold:
        lines.append("GATE PASSED — corpus sufficient, proceed to annotation (2d).")
    elif unfinished:
        lines.append(
            f"GATE FAILED — but {len(unfinished)} channel(s) did not finish the walk "
            f"({', '.join(unfinished)}): rerun to completion before judging the corpus."
        )
    else:
        lines.append(
            "GATE FAILED — every channel was walked to the end and the corpus is still "
            "short. Stop here and report; the team lead escalates to the operator."
        )
    return "\n".join(lines)
