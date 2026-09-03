#!/usr/bin/env python3
"""`make tick` — S4 of the phase spec. $0, idempotent, and it buys nothing.

    make tick            # promote what is on disk into the six promo tables, then export the screen
    make tick && make tick

**What a tick IS.** Everything the paid legs already wrote is on disk in its own file: positions in
`data/derived/pulse.db`, screened promo-signal answers under `results/promo_signals/`. A tick reads
those, derives the six promo tables from them, and writes the screen's fuel. It calls no model,
opens no endpoint and touches no money — the guard is not even imported, because there is nothing
here to guard.

**Idempotence is the id, not a flag.** Every row's id is `uuid5` over the row's own normalised key
(`aggregates.PROMO_KEYS`), so a second tick over an unchanged store recomputes the same ids and
`INSERT OR IGNORE` drops all of them: zero new rows, per table, which is K10. The one row that is
UPDATED rather than ignored is `digest` — a late comment changes a thread's digest without changing
its identity — and `aggregates.upsert_digest` rewrites it only when a field actually moved.

**The clock is an argument, and it is not in the export.** `--now` defaults to the wall clock and
the cooled-thread queue is the only thing that reads it. The screen's export carries no timestamp at
all (plan §5.12a: a clock in a derived export makes a determinism check unrunnable), so two ticks
over an unchanged store produce a byte-identical `results/promo_screen_data.json`. The clock lives
one file over, in `results/promo_tick.json`, which is the tick's own state and which the screen does
not read.

**What it does NOT do. It does not collect, it does not extract and it does not schedule itself.**
`data/schedule.json` is READ (min interval 1 h, default 6 h) and reported as a due time; the
schedule UI is out of scope (phase spec §6) and the file is created here once, with the defaults,
so a reader can see what the loop obeys. The interval gates a SCHEDULER, never this command: a tick
that refused to run twice in an hour would make «run twice on an unchanged store → zero new rows»
untestable, and the check would pass over a run that never happened
([[a_prefilter_cannot_certify_the_population]]). `--if-due` is there for the cron caller that does
want the refusal.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from market_pulse import aggregates, trends  # noqa: E402
from market_pulse.raw_store import ARCHIVE_ROOT, RawStore  # noqa: E402

DB = REPO_ROOT / "data" / "derived" / "pulse.db"
LIVE_ROOT = REPO_ROOT / "data" / "raw_r2"
SCHEDULE = REPO_ROOT / "data" / "schedule.json"
SIGNALS = REPO_ROOT / "results" / "promo_signals"
EXPORT = REPO_ROOT / "results" / "promo_screen_data.json"
STATE = REPO_ROOT / "results" / "promo_tick.json"

SCHEDULE_DEFAULT = {
    "min_interval_hours": 1,
    "default_interval_hours": 6,
    "note": "READ by scripts/tick.py and by nothing else. Phase spec §2 S4 fixes both numbers;"
    " the schedule UI is out of scope (§6), so this file is the whole of the loop's schedule.",
}

CHAINS = ("atb", "varus", "silpo", "novus", "fora", "megamarket", "auchan")
"""The chains SPEC amendment 3.20 names — `aggregates.promo_positions` flags a row's chain against
this list. Passed in rather than re-derived here so the screen and the dashboard agree."""



# --- the cooled thread, and the digest that lets a late comment join -----------------------------
#
# In `scripts/tick.py` and NOT in `src/market_pulse/loop.py`, which plan §3's S12 row names. The
# module is pinned by TEN sealed records (`results/dashboard_data_w1.json`, `gate_census_w1.json`,
# `window_summary_5c2.json`, the two pass-1 label packs, …) and moving it turns a $0 wiring step
# into a five-file claim through `tests/moved_pins.py`. Nothing here is the collection loop's
# business anyway: `loop.py` carries watermarks and paid passes, and a cooled thread is a fact about
# the promo tables. Dv15, the same manoeuvre and the same cause as Dv14 (S11 landed in
# `trends.py`), and no pin moved.

COOLED_HOURS = 24
"""«A thread is read when COOLED (24 h without new comments)» — phase spec §2 S4, plan §5.10.

A READ threshold and not a digest threshold: what cools is the conversation, and reading it earlier
buys an answer the next comment invalidates. A thread that cools, is read, and then receives a late
comment does not become uncooled — the late comment joins through the digest below."""


def thread_root(comment: dict) -> int:
    """The post a comment hangs under. `parent_msg_id` is the CHANNEL's id space and `msg_id` the
    discussion group's; only the first is comparable to a post id."""
    return int(comment["parent_msg_id"])


def threads(comments) -> dict:
    """Comments grouped under (channel, thread root), each thread sorted by its own msg_id."""
    out: dict = {}
    for row in comments:
        out.setdefault((row["channel"], thread_root(row)), []).append(row)
    for thread in out.values():
        thread.sort(key=lambda row: int(row["msg_id"]))
    return out


def cooled_threads(comments, now: datetime, hours: int = COOLED_HOURS) -> list[dict]:
    """The read queue: threads whose NEWEST comment is at least `hours` old.

    `now` is passed in and never read from the clock here. A queue that read the clock would answer
    a different question on every call, and the tick's idempotence is measured by calling it twice
    ([[a_paced_log_is_an_interleavable_clock]]).
    """
    out = []
    for (channel, root), thread in sorted(threads(comments).items()):
        newest = max(datetime.fromisoformat(row["date"]) for row in thread)
        if (now - newest).total_seconds() >= hours * 3600:
            out.append(
                {
                    "channel": channel,
                    "thread_root": root,
                    "comment_ids": [int(row["msg_id"]) for row in thread],
                    "cooled_at": newest.isoformat(),
                }
            )
    return out


def digest_text(signals: list[dict]) -> str:
    """What the thread said, as its signal types and their counts — derived, never typed.

    Deterministic by construction (sorted, counted), because the digest is compared field by field
    on the next tick and a rendering that reordered itself would bump the version on a thread
    nothing happened to. A SUMMARY OF THE SIGNALS and not a second reading of the comments: the
    thread's own words live in `evidence.quote`, and a digest that paraphrased them would be a place
    for a claim no hook checked.
    """
    counts: dict[str, int] = {}
    for signal in signals:
        counts[signal["type"]] = counts.get(signal["type"], 0) + 1
    return " · ".join(f"{kind}×{counts[kind]}" for kind in sorted(counts))


def digest_row(thread: dict, signals: list[dict]) -> dict:
    """One `digest` row for a cooled thread that HAS been read.

    A cooled thread with no signals is not digested — it is the queue. An empty digest for it would
    make «read and said nothing» and «not read» the same row
    ([[empty_field_hides_several_states]]), and the next tick would never ask.

    `children_ids` and `covers_up_to_msg_id` are the late-comment delta's two halves: what the
    digest already covers, and the watermark a later comment is compared against. That is what
    «late comments join via the thread digest, never by re-reading raw» buys.
    """
    ids = sorted(thread["comment_ids"])
    return {
        "channel": thread["channel"],
        "thread_root": thread["thread_root"],
        "version": 1,
        "text": digest_text(signals),
        "children_ids": json.dumps(ids, separators=(",", ":")),
        "supporting_signal_ids": json.dumps(
            sorted(signal["signal_id"] for signal in signals), separators=(",", ":")
        ),
        "covers_up_to_msg_id": ids[-1] if ids else 0,
        "cooled_at": thread["cooled_at"],
    }


def late_comments(digest_children: str, comment_ids) -> list[int]:
    """Comment ids the digest does not already carry — the delta, computed off the digest alone.

    Off `children_ids` and not off the watermark: a comment can arrive with an id BELOW
    `covers_up_to_msg_id` (the discussion group's ids are not gapless per thread) and a watermark
    comparison would silently drop it. The watermark answers «how far did we read», the children
    answer «what exactly did we read», and only the second can find a hole.
    """
    covered = set(json.loads(digest_children))
    return sorted(int(msg_id) for msg_id in comment_ids if int(msg_id) not in covered)


def rel(path: Path) -> str:
    """The path as a reader of this repo names it, and the absolute one when it is outside."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)

def schedule(path: Path = SCHEDULE) -> dict:
    """The loop's schedule, created once with the phase spec's numbers and READ ever after."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(SCHEDULE_DEFAULT, indent=2) + "\n", encoding="utf-8")
    return json.loads(path.read_text(encoding="utf-8"))


def due(schedule_doc: dict, last: str | None, now: datetime) -> tuple[bool, str]:
    """Is a tick due under `data/schedule.json`, and the sentence that says why.

    A reading, not a gate — see the docstring. `last` is the previous tick's own `at`, so the
    interval is measured between the runs that did work. Returned as a pair because the reason is
    what a cron log needs; the bool alone cannot say whether it is the minimum or the default that
    is speaking.
    """
    if last is None:
        return True, "no previous tick"
    hours = (now - datetime.fromisoformat(last)).total_seconds() / 3600
    if hours < schedule_doc["min_interval_hours"]:
        return False, (
            f"{hours:.2f} h since the last tick, below the {schedule_doc['min_interval_hours']} h"
            " minimum"
        )
    if hours < schedule_doc["default_interval_hours"]:
        return True, (
            f"{hours:.2f} h since the last tick — past the minimum, before the"
            f" {schedule_doc['default_interval_hours']} h default interval"
        )
    return True, f"{hours:.2f} h since the last tick, at or past the default interval"


def signal_records(root: Path = SIGNALS) -> list[dict]:
    """The screened promo-signal answers on disk, oldest file first.

    Each file is one thread as `market_pulse.promo_hooks.screen` returned it, plus the three fields
    the screen function does not know: `channel`, `thread_root`, `extractor_version`. The directory
    is empty until C3's paid leg runs, and an empty directory is a legitimate state — a tick over no
    answers writes no signal rows and says so, rather than failing.
    """
    if not root.exists():
        return []
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(root.glob("*.json"))]


def promote(conn, records: list[dict]) -> dict[str, int]:
    """The screened answers into `attribution` / `signal` / `evidence` / `unsure`.

    `signal_id` is recomputed here, with the same key `add_promo` uses, because `evidence` is keyed
    on it: an evidence row whose `signal_id` was invented separately would point at nothing, and the
    join would be silently empty rather than loudly wrong.
    """
    written = dict.fromkeys(("attribution", "signal", "evidence", "unsure"), 0)
    for record in records:
        channel, root = record["channel"], record["thread_root"]
        kept = record.get("kept") or {}
        written["attribution"] += aggregates.add_promo(
            conn,
            "attribution",
            [
                {
                    "channel": channel,
                    "msg_id": int(row["msg_id"]),
                    "subject_id": aggregates.subject_id(row["subject_type"], row["subject"]),
                    "subject_type": row["subject_type"],
                    "subject": row["subject"],
                    "role": row.get("role"),
                    "source": row["source"],
                    "confidence": row.get("confidence"),
                }
                for row in kept.get("about") or []
            ],
        )
        for row in kept.get("signal") or []:
            subject = aggregates.subject_id(row["subject_type"], row["subject"])
            signal_id = aggregates.promo_id(channel, root, row["type"], subject)
            written["signal"] += aggregates.add_promo(
                conn,
                "signal",
                [
                    {
                        "channel": channel,
                        "thread_root": int(root),
                        "type": row["type"],
                        "subject_id": subject,
                        "confidence": row.get("confidence"),
                        "extractor_version": record["extractor_version"],
                    }
                ],
            )
            written["evidence"] += aggregates.add_promo(
                conn,
                "evidence",
                [
                    {
                        "signal_id": signal_id,
                        "msg_id": int(row["msg_id"]),
                        "quote": row["quote"],
                        "span": json.dumps(row["span"]) if row.get("span") else None,
                    }
                ],
            )
        written["unsure"] += aggregates.add_promo(
            conn,
            "unsure",
            [
                {
                    "channel": channel,
                    "msg_id": int(row["msg_id"]),
                    "candidates": json.dumps(row.get("candidates") or [], ensure_ascii=False),
                    "reason": row["reason"],
                }
                for row in record.get("unsure") or []
            ],
        )
    return written


def comments(store: RawStore) -> list[dict]:
    """Every stored comment across both raw roots — the union of plan §5.14, r2 winning."""
    channels = sorted(
        {path.stem for root in (*store.archives, store.root) for path in (root / "comments").glob("*.jsonl")}
    )
    return [row for channel in channels for row in store.rows("comment", channel)]


def digests(conn, store: RawStore, now: datetime) -> dict[str, int]:
    """A digest per COOLED thread that has been read — and the late-comment delta on the rest.

    A cooled thread with no `signal` row has not been read yet: it is the queue the next paid pass
    asks, not a digest. See `loop.digest_row` — writing an empty digest for it would make «read and
    said nothing» and «never read» the same row.
    """
    conn.row_factory = sqlite3.Row
    counts = {"inserted": 0, "updated": 0, "unchanged": 0, "queued": 0, "late": 0}
    for thread in cooled_threads(comments(store), now):
        signals = [
            dict(row)
            for row in conn.execute(
                "SELECT signal_id, type FROM signal WHERE channel = ? AND thread_root = ?",
                (thread["channel"], thread["thread_root"]),
            )
        ]
        if not signals:
            counts["queued"] += 1
            continue
        live = conn.execute(
            "SELECT children_ids FROM digest WHERE digest_id = ?",
            (aggregates.promo_id(thread["channel"], thread["thread_root"]),),
        ).fetchone()
        if live is not None:
            counts["late"] += len(late_comments(live["children_ids"], thread["comment_ids"]))
        counts[aggregates.upsert_digest(conn, digest_row(thread, signals))] += 1
    return counts


def rollups(conn, window_id: str, weeks: dict) -> list[dict]:
    """`rollup` rows from S3's trends — per week × chain × brand, and every metric named for what
    it counts. `depth_mean` is the window aggregate SPEC 3.22 (1) allows; it never travels beside a
    row's own promo price, which is why it lives here and not in the screen's position rows.

    `weeks` is passed in and never defaulted: `trends.post_weeks()` reads the repo's own two raw
    roots, so a tick pointed at a temporary store would silently date its rollups from the live
    corpus and the test would be measuring the wrong store."""
    reading = trends.build(conn, window_id, weeks)
    rows = []
    for week, by_week in sorted(reading["sku_price_by_week"].items()):
        per_brand: dict[tuple[str, str], list[dict]] = {}
        for row in by_week:
            per_brand.setdefault((row["chain"], row["brand_raw"]), []).append(row)
        for (chain, brand), skus in sorted(per_brand.items(), key=lambda kv: (kv[0][0], kv[0][1] or "")):
            rows.append({"week": week, "chain": chain, "brand": brand,
                         "metric": "priced_positions", "value": float(sum(s["n"] for s in skus))})
            rows.append({"week": week, "chain": chain, "brand": brand,
                         "metric": "sku_count", "value": float(len(skus))})
    for week, by_week in sorted(reading["depth_by_week"].items()):
        for row in sorted(by_week, key=lambda r: (r["chain"], r["brand"] or "")):
            rows.append({"week": week, "chain": row["chain"], "brand": row["brand"],
                         "metric": "depth_mean", "value": row["depth_mean"]})
    return rows


def feed(conn, limit: int | None = None) -> list[dict]:
    """The reaction feed — signal · quote · msg_id · thread, the four fields §1 names."""
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT s.channel, s.thread_root, s.type, e.msg_id, e.quote"
        " FROM signal s JOIN evidence e ON e.signal_id = s.signal_id"
        " ORDER BY s.channel, s.thread_root, s.type, e.msg_id"
    ).fetchall()
    return [dict(row) for row in (rows[:limit] if limit else rows)]


def export(conn, window_id: str, counts: dict) -> dict:
    """The screen's only fuel — a derived export in the envelope of plan §5.12a.

    Sorted keys, no git block and NO CLOCK: two ticks over an unchanged store write this file
    byte for byte the same, which is a determinism check anybody can run with `shasum`. The tick's
    own timestamp lives in `results/promo_tick.json`.
    """
    return {
        "contract": "docs/PHASE-promo-pulse-1.md §2 S4/C5 — `make tick` writes this, `make"
        " promo-screen` renders it and reads nothing else.",
        "window_id": window_id,
        "screen": {
            "positions": aggregates.promo_positions(conn, window_id, CHAINS),
            "depth_by_chain_and_brand": [
                dict(row)
                for row in conn.execute(
                    "SELECT week, chain, brand, value AS depth_mean FROM rollup"
                    " WHERE metric = 'depth_mean' ORDER BY week, chain, brand"
                )
            ],
            "weeks": sorted({row[0] for row in conn.execute("SELECT DISTINCT week FROM rollup")}),
            "rollup": [
                dict(row)
                for row in conn.execute(
                    "SELECT week, chain, brand, metric, value FROM rollup"
                    " ORDER BY week, chain, brand, metric"
                )
            ],
            "feed": feed(conn),
            "table_rows": counts,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DB)
    parser.add_argument("--store", type=Path, default=LIVE_ROOT)
    parser.add_argument(
        "--archive", type=Path, default=ARCHIVE_ROOT,
        help="the read-only v1 root unioned under --store (plan §5.14). A test points it at an"
        " empty directory; production leaves it alone.",
    )
    parser.add_argument("--signals", type=Path, default=SIGNALS)
    parser.add_argument("--out", type=Path, default=EXPORT)
    parser.add_argument("--schedule", type=Path, default=SCHEDULE)
    parser.add_argument("--state", type=Path, default=STATE)
    parser.add_argument(
        "--window",
        default="w2",
        help="the aggregate window the screen is built from. w2 is the C2 window"
        " (results/prereg_promo_c2.json :: addendum[0].window_id): ruling 02.09 (d) refuses the"
        " shape that leaves the screen on w1 «because the phase's artifact IS the C2 screen».",
    )
    parser.add_argument("--now", help="ISO timestamp; the cooled queue's clock (default: now)")
    parser.add_argument(
        "--if-due", action="store_true",
        help="for a scheduler: do nothing when data/schedule.json's minimum interval has not passed",
    )
    args = parser.parse_args(argv)

    now = datetime.fromisoformat(args.now) if args.now else datetime.now(UTC)
    if not args.db.exists():
        print(f"tick: no store at {args.db} — nothing to promote, nothing written", file=sys.stderr)
        return 0

    schedule_doc = schedule(args.schedule)
    last = None
    if args.state.exists():
        last = json.loads(args.state.read_text(encoding="utf-8"))["at"]
    is_due, why = due(schedule_doc, last, now)
    print(f"schedule: {'due' if is_due else 'not due'} — {why}")
    if args.if_due and not is_due:
        print("tick: --if-due and not due; nothing written")
        return 0

    conn = sqlite3.connect(args.db)
    aggregates.ensure_promo_tables(conn)
    before = aggregates.promo_counts(conn)

    written = promote(conn, signal_records(args.signals))
    weeks = trends.post_weeks((args.archive / "posts", args.store / "posts"))
    written["rollup"] = aggregates.add_promo(conn, "rollup", rollups(conn, args.window, weeks))
    digest = digests(conn, RawStore(args.store, archives=(args.archive,)), now)
    written["digest"] = digest["inserted"]
    conn.commit()

    after = aggregates.promo_counts(conn)
    for table in aggregates.PROMO_TABLES:
        print(f"{table:14s} {before[table]:6d} -> {after[table]:6d}   new {after[table] - before[table]}")
    print(
        f"digest: {digest['inserted']} inserted · {digest['updated']} updated ·"
        f" {digest['unchanged']} unchanged · {digest['queued']} cooled and not yet read ·"
        f" {digest['late']} late comments joined"
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(export(conn, args.window, after), indent=2, ensure_ascii=False, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    args.state.write_text(
        json.dumps({"at": now.isoformat(), "new_rows": written, "table_rows": after,
                    "digest": digest, "schedule": why}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {rel(args.out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
