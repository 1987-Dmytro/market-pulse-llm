#!/usr/bin/env python3
"""The report-only marker census — the same E requests, twice, with and without the marker.

Ruling (о) of 2026-08-24, `docs/PROMPT-lora-c-run-r2.md` amendment 4. Every one of the 160 synthetic
training rows carries a header line none of the 506 real ones does, and those 160 rows carry ALL 32
`молочный_бренд` targets in this line. So «arm B did not beat arm A» and «arm B learned to answer
`молочный_бренд` when it sees the marker» are the same reading, on the one comparison arm B exists
to make ([[a_default_is_a_marker_when_nothing_takes_it]]).

This buys the difference. Twenty E requests, drawn under a registered seed and stratified over the
label classes, each rendered TWICE by the same renderer with the same neighbours and the same
comment: once as the eval pack renders it, and once with the synthetic header substituted in. Both
are answered by arm B's adapter, after its bar is already scored. The reading is the prediction
FLIP — toward `молочный_бренд`, away from it, or unmoved.

**It is report-only and it is never a bar.** It cannot be: it is answered after every gating leg,
and a marker census that could move a verdict would be a second draw on a one-shot attempt.

**The substitution is exactly the marker and nothing else.** Two lines move — the thread tag and the
topic — and the entities block, the examples block and the comment are byte-identical between the
pair. `(this thread resolved no entity)` is NOT substituted: 284 of the 506 real rows already render
it, so it is not a tell, and moving it would change what the request SAYS rather than how it is
labelled ([[an_exclusion_by_id_is_not_an_exclusion_by_text]]).

    PYTHONPATH=src python3.11 scripts/build_lora_c_marker_census.py
"""

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_lora_c_data as data  # noqa: E402
import build_lora_c_synthetic as synth  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import pass1_v3  # noqa: E402

EVAL_PACK = REPO_ROOT / "results" / "lora_c_eval_pack.json"
ARM_B_RECORD = REPO_ROOT / "results" / "lora_c_arm_b.json"
LABELS = tuple(
    REPO_ROOT / "results" / f"labels_pass1_r{n}.jsonl" for n in (1, 2, 3)
)
OUT = REPO_ROOT / "results" / "lora_c_marker_census_pack.json"

SEED = 20260824
"""Registered here and hashed into the pack. The draw is the instrument, so it is a file and not a
constant somebody remembers ([[preregistration_is_a_file_not_a_constant]])."""

ROWS = 20
PER_CLASS = 4
"""Four per class over the five label values, topped up from the largest class where a class cannot
supply four. `молочный_бренд` has exactly ONE row in E — the same scarcity that left arm A with zero
positives — so an equal draw is unreachable and the top-up is named rather than silently taken."""


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def gold() -> dict:
    """The team lead's labels on the (thread, msg_id) key, r3 last — the delta rule, unchanged."""
    rows: dict[tuple[str, int], str | None] = {}
    for path in LABELS:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                one = json.loads(line)
                rows[(one["thread"], int(one["msg_id"]))] = one.get("subject_type")
    return rows


def drawn(items: list[dict], labels: dict) -> list[dict]:
    """Twenty rows, stratified over the label classes, under the registered seed.

    Unlabelled rows are excluded: the census reads a prediction FLIP and a row whose gold nobody
    wrote cannot say which direction is toward the class. `null` IS a class here and it is drawn
    from — it is the largest single answer in this pool and the marker could pull rows out of it.
    """
    by_class: dict[str, list[dict]] = {}
    for one in items:
        key = (one["thread"], int(one["msg_id"]))
        if key not in labels:
            continue
        by_class.setdefault(str(labels[key]), []).append(one)
    rng = random.Random(SEED)
    picked, leftovers = [], []
    for name in sorted(by_class):
        pool = sorted(by_class[name], key=lambda one: one["id"])
        rng.shuffle(pool)
        picked += pool[:PER_CLASS]
        leftovers += pool[PER_CLASS:]
    leftovers.sort(key=lambda one: one["id"])
    rng.shuffle(leftovers)
    picked += leftovers[: ROWS - len(picked)]
    return sorted(picked, key=lambda one: one["id"])[:ROWS]


def marked(one: dict, error_class: str) -> dict:
    """The same request with the synthetic HEADER — the thread tag and the topic, and nothing else."""
    return {**one, "channel": "synthetic", "post_id": error_class, "topic": data.SYNTHETIC_NO_POST}


def rendered(one: dict) -> str:
    return pass1_v3.pass1_messages_gm4_v3(
        one["channel"],
        one["post_id"],
        one["topic"],
        one["entities"],
        one["msg_id"],
        one["text"],
        examples=one["examples"],
    )[0]["content"]


def differs_only_in_the_header(before: str, after: str) -> list[str]:
    """The header lines that moved — REFUSING unless everything from `<entities>` on is identical.

    The whole census rests on the pair being one variable, so the pair is compared rather than
    asserted. A renderer that quietly re-ordered the examples for a different channel name would
    make «the adapter learned the marker» unfalsifiable ([[the_fixture_and_the_artifact_share_anchors]]).
    """
    marker = "<entities>"
    halves = [one.split(marker, 1) for one in (before, after)]
    if any(len(one) != 2 for one in halves):
        raise SystemExit(f"a rendering carries no {marker} block — this is not a v3 request. Stop.")
    (head_was, tail_was), (head_now, tail_now) = halves
    if tail_was != tail_now:
        raise SystemExit(
            "the two renderings differ AFTER the entities block — the entities, the examples or the"
            " comment moved. The pair is supposed to differ in the thread tag and the topic alone,"
            " so stop rather than publish a flip table whose two columns are two instruments."
        )
    was, now = head_was.splitlines(), head_now.splitlines()
    moved = [f"{one}  →  " for one in was if one not in now]
    moved += [f"  →  {one}" for one in now if one not in was]
    if not moved:
        raise SystemExit(
            "the two renderings are IDENTICAL. The marked variant carries no marker, so the census"
            " would report «no flip» for a substitution that never happened."
        )
    return sorted(moved)


def build() -> dict:
    pack = json.loads(EVAL_PACK.read_text(encoding="utf-8"))
    leg = next(one for one in pack["legs"] if one["task"] == pass1_v3.PASS1_TASK_V3)
    labels = gold()
    chosen = drawn(leg["items"], labels)
    classes = [name for name, _ in synth.CLASSES]
    items, pairs = [], []
    for index, one in enumerate(chosen):
        error_class = classes[index % len(classes)]
        both = {"as_is": one, "marked": marked(one, error_class)}
        texts = {name: rendered(row) for name, row in both.items()}
        moved = differs_only_in_the_header(texts["as_is"], texts["marked"])
        for name, row in both.items():
            items.append(
                {
                    **{key: value for key, value in row.items() if key != "rendering_sha256"},
                    "id": f"{one['id']}@{name}",
                    "unit": one["id"],
                    "variant": name,
                    "error_class": error_class if name == "marked" else None,
                    "rendered_chars": len(texts[name]),
                    "rendering_sha256": sha_text(texts[name]),
                }
            )
        pairs.append(
            {
                "unit": one["id"],
                "gold": labels[(one["thread"], int(one["msg_id"]))],
                "error_class": error_class,
                "header_lines_that_moved": moved,
            }
        )
    return {
        "phase": "lora-c",
        "contract": "docs/PROMPT-lora-c-run-r2.md amendment 4 — REPORT ONLY, never a bar",
        "what_this_is": (
            "twenty E requests, each answered TWICE by arm B's adapter — as the eval pack renders"
            " it, and with the synthetic header substituted in. It separates «synthetic did not"
            " help» from «the adapter learned the marker»"
        ),
        "when": "after arm B's eval leg, when both arms' bars are already scored",
        "draw": {
            "seed": SEED,
            "rows": len(chosen),
            "rule": (
                f"{PER_CLASS} per label class over the five values, topped up from the largest"
                " class. Unlabelled rows are excluded — a flip needs a gold to be a flip"
            ),
            "by_class": {
                name: sum(1 for one in pairs if str(one["gold"]) == name)
                for name in sorted({str(one["gold"]) for one in pairs})
            },
            "error_classes": {
                name: sum(1 for one in pairs if one["error_class"] == name)
                for name in sorted({one["error_class"] for one in pairs})
            },
        },
        "substitution": {
            "topic": data.SYNTHETIC_NO_POST,
            "channel": "synthetic",
            "post_id": "the error class, rotated over the four so all five tells are exercised",
            "not_substituted": (
                "the entities block. 284 of the 506 real rows already render «(this thread resolved"
                " no entity)», so it is not a tell, and moving it would change what the request says"
            ),
            "checked": "every pair differs in HEADER lines only, or this producer stops",
        },
        "instruments": pack["instruments"],
        "serving": pack["serving"],
        "legs": [
            {
                "name": "marker_census",
                "task": pass1_v3.PASS1_TASK_V3,
                "out": "lora_c_marker_census.jsonl",
                "n": len(items),
                "items": items,
            }
        ],
        "carried": {"ids": [], "units": 0, "from": None, "rule": "nothing is carried"},
        "pairs": pairs,
        "arm_b": {
            "record": "results/lora_c_arm_b.json",
            "sha256": summary.sha256_of(ARM_B_RECORD),
        },
        "produced_by": {
            "script": "scripts/build_lora_c_marker_census.py",
            "sha256": sha_text(Path(__file__).read_text(encoding="utf-8")),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    record = build()
    args.out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    leg = record["legs"][0]
    print(f"wrote {summary.rel(args.out)}  {leg['n']} requests = {len(record['pairs'])} pairs × 2")
    print(f"  seed {record['draw']['seed']} · by class {record['draw']['by_class']}")
    print(f"  error classes {record['draw']['error_classes']}")
    moved = {len(one["header_lines_that_moved"]) for one in record["pairs"]}
    print(f"  entities, examples and comment byte-identical in every pair · header lines moved:"
          f" {sorted(moved)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
