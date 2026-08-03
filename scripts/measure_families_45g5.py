#!/usr/bin/env python3
"""How big the two error families are, and what a naive rule over them would cost (4.5g5, Task 4).

The v2.2 probe closed the prompt-form track: the rows the sitting refused are not rows a better
sentence reaches, because the evidence a reader would need is not in them. Two candidate features
are: who wrote the comment, and what it replies to. This measures both — sizes, and the price of
acting on them — so the next probe is registered against numbers instead of intuition.

Two discriminators for "this replies to another comment, not to the post", reported side by side
because one agreeing with the other is a much stronger claim than either alone:

- **by head** — `reply_to_msg_id` lives in the discussion group's id space, where every message
  of a thread replies to the group's mirror of the post or to another comment. The mirror is
  created before any comment, so it is the smallest reply target in the thread; anything else is
  a comment, deleted since or not.
- **by membership** — the target is itself a comment this repo collected. Blind to a target that
  has since been deleted, which is exactly why it is the cross-check and not the measure.

    PYTHONPATH=src python3 scripts/measure_families_45g5.py

Writes `results/features_45g5.json`. Reads no model and calls nothing.
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))

import relabel_intents as relabel  # noqa: E402
from build_audit_pack import git_state  # noqa: E402
from fetch_comments_v2 import CHANNELS, read_jsonl, v2_path  # noqa: E402

BATCH = REPO_ROOT / "data" / "annotation" / "uplabel_precheck_45g2.jsonl"
GATES = REPO_ROOT / "results" / "sitting_45g_gates.json"
RECORD = REPO_ROOT / "results" / "features_45g5.json"

HYPERACTIVE = 2
"""How many senders the channel-identity family covers. The team lead's reading, and the corpus
agrees with it sharply: the two busiest write 876 and 3,761 comments, the next-busiest 81."""


def rel(path: Path) -> str:
    return relabel.rel(path)


def row_id(row: dict) -> str:
    return f"{row['channel']}:{row['msg_id']}"


def heads(rows: list[dict]) -> dict[tuple[str, int], int]:
    """Each thread's head: the smallest reply target seen in it.

    The head is the discussion group's mirror of the post, posted before any comment on it, so
    it is smaller than every comment id in the thread — including a comment that has since been
    deleted and is still someone's reply target.
    """
    targets = defaultdict(set)
    for row in rows:
        target = row.get("reply_to_msg_id")
        if target is not None:
            targets[(row["channel"], row["parent_msg_id"])].add(target)
    return {thread: min(seen) for thread, seen in targets.items() if seen}


def replies_to_comments(rows: list[dict]) -> dict:
    """Ids that reply to another comment, by both discriminators, and what neither can see."""
    head_of = heads(rows)
    collected = {(row["channel"], row["msg_id"]) for row in rows}

    by_head, by_membership, unfetched = set(), set(), set()
    for row in rows:
        if "reply_to_msg_id" not in row:
            unfetched.add(row_id(row))
            continue
        target = row["reply_to_msg_id"]
        if target is None:
            continue
        if target != head_of.get((row["channel"], row["parent_msg_id"])):
            by_head.add(row_id(row))
        if (row["channel"], target) in collected:
            by_membership.add(row_id(row))

    # A thread nobody answered at the top level has no observed head, so its smallest target is
    # a comment and the rows pointing at it are read as top-level. Counted, never silently held.
    headless = sorted(
        f"{channel}:{parent}"
        for (channel, parent), head in head_of.items()
        if (channel, head) in collected
    )
    return {
        "ids": sorted(by_head),
        "by_membership": sorted(by_membership),
        "disagree": sorted(by_head ^ by_membership),
        "threads_with_no_observed_head": headless,
        "rows_not_refetched": sorted(unfetched),
    }


def hyperactive(rows: list[dict], n: int = HYPERACTIVE) -> dict:
    """The n busiest pseudonyms and the rows they wrote, with the gap to the next one."""
    per_sender = Counter(row["sender_anon_id"] for row in rows if row.get("sender_anon_id"))
    ranked = per_sender.most_common(n + 1)
    top = {sender for sender, _ in ranked[:n]}
    return {
        "senders": [{"sender_anon_id": s[:12], "comments": c} for s, c in ranked[:n]],
        "next_busiest": ranked[n][1] if len(ranked) > n else None,
        "ids": sorted(row_id(row) for row in rows if row.get("sender_anon_id") in top),
        "per_sender_ids": {
            sender[:12]: sorted(row_id(row) for row in rows if row.get("sender_anon_id") == sender)
            for sender, _ in ranked[:n]
        },
    }


def spread(ids: set[str], population: dict) -> dict:
    """One family against the four denominators the phase cares about."""
    batch, judged, labels = population["batch"], population["judged"], population["labels"]
    correct = {i for i, verdict in judged.items() if verdict == "correct"}
    wrong = set(judged) - correct
    in_correct = ids & correct
    return {
        "all_comments": {"n": len(ids), "of": population["comments"]},
        "batch": {"n": len(ids & batch), "of": len(batch)},
        "errors": {"n": len(ids & wrong), "of": len(wrong)},
        "judged": {
            "correct": {"n": len(in_correct), "of": len(correct)},
            "incorrect": {"n": len(ids & wrong), "of": len(wrong)},
        },
        # What a rule reading this feature as "the retailer speaking" would cost: rows the
        # sitting called right, whose `unclear` such a rule would flip.
        "judged_correct_with_unclear_false": sum(1 for i in in_correct if not labels[i]["unclear"]),
    }


def population(batch_rows: list[dict], gates: dict, comments: int) -> dict:
    return {
        "batch": {row["id"] for row in batch_rows},
        "labels": {row["id"]: row for row in batch_rows},
        "judged": {row["id"]: row["verdict"] for row in gates["rows"]},
        "comments": comments,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, default=RECORD)
    args = parser.parse_args()

    rows = [row for channel in CHANNELS for row in read_jsonl(v2_path(channel))]
    if not rows:
        raise SystemExit(f"{rel(v2_path(CHANNELS[0])).rsplit('/', 1)[0]} is empty — run the fetch")
    batch_rows = [json.loads(line) for line in BATCH.read_text(encoding="utf-8").splitlines()]
    gates = json.loads(GATES.read_text(encoding="utf-8"))
    pop = population(batch_rows, gates, len(rows))

    # The 35 rows 4.5g5 adjudicated are all refusals, so no judged-correct label moved under
    # them — the "what a naive rule would cost" counts read the same batch the sitting judged.
    moved = {row["id"] for row in batch_rows if row["annotator"] == "sitting-45g-verdicts"}
    correct = {i for i, verdict in pop["judged"].items() if verdict == "correct"}
    if moved & correct:
        raise SystemExit(f"{len(moved & correct)} judged-correct rows carry an applied verdict")

    replies = replies_to_comments(rows)
    identity = hyperactive(rows)
    reply_ids, identity_ids = set(replies["ids"]), set(identity["ids"])

    record = {
        "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
        "measured_by": "scripts/measure_families_45g5.py",
        "sources": {
            "comments": [rel(v2_path(channel)) for channel in CHANNELS],
            "batch": rel(BATCH),
            "gates": rel(GATES),
        },
        "corpus": {
            "comments": len(rows),
            "batch_rows": len(pop["batch"]),
            "judged": len(pop["judged"]),
            "errors": sum(1 for v in pop["judged"].values() if v == "incorrect"),
            "rows_not_refetched": len(replies["rows_not_refetched"]),
        },
        "families": {
            "replies_to_comments": {
                "discriminator": "reply_to_msg_id is not the thread's smallest reply target",
                **spread(reply_ids, pop),
                "cross_check_by_membership": len(replies["by_membership"]),
                "discriminators_disagree_on": len(replies["disagree"]),
                "threads_with_no_observed_head": len(replies["threads_with_no_observed_head"]),
            },
            "channel_identity": {
                "discriminator": f"one of the {HYPERACTIVE} busiest sender_anon_ids",
                "senders": identity["senders"],
                "next_busiest": identity["next_busiest"],
                **spread(identity_ids, pop),
                "per_sender": {
                    sender: spread(set(ids), pop)
                    for sender, ids in identity["per_sender_ids"].items()
                },
            },
            "overlap": {
                **spread(reply_ids & identity_ids, pop),
                "note": "rows in both families — a rule for either has to say what happens here",
            },
        },
        "errors_in_neither_family": sorted(
            i
            for i, verdict in pop["judged"].items()
            if verdict == "incorrect" and i not in reply_ids and i not in identity_ids
        ),
        "git": git_state(args.record),
    }
    relabel.append_record(args.record, record)

    for name, family in record["families"].items():
        print(
            f"{name}: {family['all_comments']['n']} comments · {family['batch']['n']} of "
            f"{family['batch']['of']} batch · {family['errors']['n']} of "
            f"{family['errors']['of']} errors · "
            f"{family['judged']['correct']['n']} of {family['judged']['correct']['of']} "
            f"judged-correct ({family['judged_correct_with_unclear_false']} of them "
            f"unclear=false)"
        )
    print(f"errors in neither family: {len(record['errors_in_neither_family'])}")
    print(f"wrote {rel(args.record)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
