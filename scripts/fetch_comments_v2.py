#!/usr/bin/env python3
"""A second pass over the comment threads, for the reply target v1 never stored (4.5g5, Task 3).

The collector learned `reply_to_msg_id` after the corpus was already collected and labelled, so
the field has to be backfilled from Telegram. Two steps, deliberately separate:

1. **fetch** every thread of both channels into `data/raw_fresh_45g5/comments/`, a scratch store
   that exists only to be joined. Resumable: the store dedupes on (channel, msg_id) and a rerun
   skips the threads it already holds.
2. **join** it onto v1 by (channel, msg_id) into `data/raw/comments_v2/`, where a record is the
   **v1 record** plus its reply target. v1 text is law — the labels were made on it — so a text
   that has since been edited keeps the v1 wording and is counted as drift, not applied.

`data/raw/comments/` is never opened for writing. A v2 row that was not re-fetched (the message
is gone from Telegram) carries **no `reply_to_msg_id` key at all**, so a reader that assumes one
raises instead of quietly reading `None` as "replies to the post".

    PYTHONPATH=src python3 scripts/fetch_comments_v2.py --plan       # what it would fetch
    PYTHONPATH=src python3 scripts/fetch_comments_v2.py              # fetch, then join
    PYTHONPATH=src python3 scripts/fetch_comments_v2.py --join-only  # join what is already there

Writes `data/raw/comments_v2/<channel>.jsonl` and `results/drift_45g5.json`.
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))

import relabel_intents as relabel  # noqa: E402
from build_audit_pack import git_state  # noqa: E402

from market_pulse.raw_store import RawStore, comment_record, load_salt, make_provenance  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402
from market_pulse.telegram_client import build_client  # noqa: E402

REGISTRY = REPO_ROOT / "config" / "registry.yaml"
V1_ROOT = REPO_ROOT / "data" / "raw"
FRESH_ROOT = REPO_ROOT / "data" / "raw_fresh_45g5"
V2_DIR = REPO_ROOT / "data" / "raw" / "comments_v2"
RECORD = REPO_ROOT / "results" / "drift_45g5.json"

CHANNELS = ("@VARUS_channel", "@msuaaaa")
"""The two channels the labelled corpus came from. No new channels in this phase."""

THREAD_PAUSE = 1.0
FLOOD_RETRIES = 3
PROGRESS_EVERY = 50

FROZEN = ("text", "sentiment", "sarcasm", "intents", "unclear")
"""What the join may never take from the fresh fetch. Only `text` is on a raw record; the rest
are named so that a future joiner over a labelled file cannot quietly widen this."""


def rel(path: Path) -> str:
    return relabel.rel(path)


def v2_path(channel: str, root: Path = V2_DIR) -> Path:
    return root / f"{channel.lstrip('@')}.jsonl"


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def todo(v1: RawStore, fresh: RawStore, channel: str) -> list[int]:
    """Threads still to fetch: every v1 thread the fresh store does not have yet.

    Read off the **fresh** store on purpose. Asking v1 which parents are done would answer "all
    of them" and walk away having fetched nothing, with a v2 directory that looks merely small.
    """
    return sorted(
        {row["parent_msg_id"] for row in read_jsonl(v1.path("comment", channel))}
        - fresh.index("comment", channel).parents,
        reverse=True,
    )


def joined(v1_rows: list[dict], fresh_rows: list[dict]) -> tuple[list[dict], dict]:
    """v1 records carrying the fresh reply target, and what the two fetches disagree about.

    Order and content follow v1: the corpus is what was labelled, and a message that appeared
    since is out of it. Drift is counted, never applied.
    """
    fresh = {row["msg_id"]: row for row in fresh_rows}
    out, deleted, edited = [], [], 0
    for row in v1_rows:
        found = fresh.get(row["msg_id"])
        if found is None:
            deleted.append(row["msg_id"])
            out.append(dict(row))  # no reply_to_msg_id key: absent, not None
            continue
        if found.get("text", "") != row.get("text", ""):
            edited += 1
        out.append({**row, "reply_to_msg_id": found["reply_to_msg_id"]})
    return out, {
        "v1_rows": len(v1_rows),
        "fresh_rows": len(fresh_rows),
        "missing_from_the_fresh_fetch": len(deleted),
        "text_differs": edited,
        "fresh_only": len(set(fresh) - {row["msg_id"] for row in v1_rows}),
    }


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )


async def fetch_thread(client, entity, job, parent: int) -> list[dict]:
    return [
        comment_record(message, job["source"], job["channel"], parent, job["salt"], job["prov"])
        async for message in client.iter_messages(entity, reply_to=parent)
        if message.action is None
    ]


async def fetch_channel(client, fresh: RawStore, job: dict, parents: list[int]) -> int:
    entity = await client.get_entity(job["channel"])
    written = 0
    for done, parent in enumerate(parents, start=1):
        for _ in range(FLOOD_RETRIES):
            try:
                written += fresh.append(await fetch_thread(client, entity, job, parent))
                break
            except Exception as exc:  # FloodWait sleeps and retries; a dead thread is skipped
                if type(exc).__name__ == "FloodWaitError":
                    print(f"  FloodWait: sleeping {exc.seconds}s", flush=True)
                    await asyncio.sleep(exc.seconds)
                    continue
                print(f"  thread {parent}: {type(exc).__name__}", flush=True)
                break
        if done % PROGRESS_EVERY == 0:
            print(f"  {done}/{len(parents)} threads, {written} comments", flush=True)
        await asyncio.sleep(THREAD_PAUSE)
    return written


async def fetch_all(plan: dict, fresh: RawStore, salt: str, session: str) -> dict:
    client = build_client()
    await client.connect()
    fetched = {}
    try:
        if not await client.is_user_authorized():
            raise SystemExit("No Telegram session. Run: python3 scripts/tg_login.py")
        for channel, job in plan.items():
            print(f"\n{channel}: {len(job['parents'])} threads to fetch", flush=True)
            fetched[channel] = await fetch_channel(client, fresh, job, job["parents"])
    finally:
        await client.disconnect()
    return fetched


def build_plan(registry, v1: RawStore, fresh: RawStore, salt: str, session: str) -> dict:
    by_handle = {
        handle: source for source in registry.sources for handle in source.telegram_channels
    }
    plan = {}
    for channel in CHANNELS:
        source = by_handle.get(channel)
        if source is None:
            raise SystemExit(f"{channel} is not in {rel(REGISTRY)}")
        plan[channel] = {
            "channel": channel,
            "source": source,
            "salt": salt,
            "prov": make_provenance(source, session),
            "parents": todo(v1, fresh, channel),
        }
    return plan


def join_all(v1: RawStore, fresh: RawStore) -> dict:
    drift = {}
    for channel in CHANNELS:
        rows, counts = joined(
            read_jsonl(v1.path("comment", channel)), read_jsonl(fresh.path("comment", channel))
        )
        write_jsonl(v2_path(channel), rows)
        with_target = sum(1 for row in rows if row.get("reply_to_msg_id") is not None)
        counts["v2_rows"] = len(rows)
        counts["with_a_reply_target"] = with_target
        drift[channel] = counts
        print(f"{rel(v2_path(channel))}: {len(rows)} rows, {with_target} carry a reply target")
        print(f"  {counts}")
    return drift


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--plan", action="store_true", help="print what would be fetched, then stop"
    )
    parser.add_argument("--join-only", action="store_true", help="skip Telegram, join what is here")
    args = parser.parse_args()

    registry = load_registry(REGISTRY)
    salt = load_salt()  # also loads .env, so the session name is available below
    session = os.environ["TELEGRAM_SESSION"]
    v1, fresh = RawStore(V1_ROOT), RawStore(FRESH_ROOT)
    plan = build_plan(registry, v1, fresh, salt, session)

    for channel, job in plan.items():
        held = fresh.index("comment", channel)
        print(f"{channel}: {len(job['parents'])} threads to fetch, {held.count} comments held")
    if args.plan:
        return 0

    fetched = {}
    if not args.join_only:
        fetched = asyncio.run(fetch_all(plan, fresh, salt, session))

    drift = join_all(v1, fresh)
    relabel.append_record(
        RECORD,
        {
            "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
            "fetched_by": "scripts/fetch_comments_v2.py",
            "channels": list(CHANNELS),
            "fresh_store": rel(FRESH_ROOT),
            "v2_dir": rel(V2_DIR),
            "join": (
                "v2 record = the v1 record plus reply_to_msg_id. v1 text is law; a row missing "
                "from the fresh fetch carries no reply_to_msg_id key at all."
            ),
            "frozen_fields": list(FROZEN),
            "comments_fetched_this_run": fetched,
            "drift": drift,
            "git": git_state(RECORD),
        },
    )
    print(f"wrote {rel(RECORD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
