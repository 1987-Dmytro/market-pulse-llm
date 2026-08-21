#!/usr/bin/env python3
"""`results/pass1_window_r2_pack.json` — the 901 comments window-1 still owes, and NOTHING re-rendered.

**What this is.** `docs/PROMPT-pass1-window-r2.md` §1: the r1 pack's leg MINUS the ids the r1 pod
answered. It is a THIN SIBLING of `scripts/build_pass1_window_pack.py`: it reads that build's output
and never runs the renderer. A re-render would produce its own `rendering_sha256` values, and the
pod's handshake, rung 7 and D2's union census all compare a reply's sha against the pack's — so a
pack rebuilt from the population rather than copied from the r1 pack would silently be a DIFFERENT
instrument answering the same question ([[the_fixture_and_the_artifact_share_anchors]]).

**Every item below is the r1 item, byte for byte.** The order is the r1 order with 131 rows removed;
the fields, the five neighbours, the entity block and the sha are the ones the r1 pack registered and
the r1 pod verified on all 1 032 before its first call.

**What it refuses.**

* the r1 pack whose sha is not the one `results/prereg_pass1_window.json` pins — the sealed record's
  own population, not whatever is on disk;
* an out-file row the r1 pack never asked, or one whose `rendering_sha256` is not its pack item's:
  every one of the 131 is verified BEFORE it is subtracted, because subtracting an id on trust would
  drop a paid-for comment out of the population on the strength of a line in a file;
* a duplicate id on either side — `id` is `channel:post#msg_id` and is the PAIR, which is what makes
  the subtraction well defined at all (a msg_id alone is not unique in this window: seven of them
  live in two threads each, see the ADDENDUM of `docs/reports/pass1-window.md`);
* a remainder that is not exactly `1 032 − 131`.

    PYTHONPATH=src python3.11 scripts/build_pass1_window_r2_pack.py
    PYTHONPATH=src python3.11 scripts/build_pass1_window_r2_pack.py --out /tmp/again.json  # the pair
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_pass1_fewshot_packs as fewshot  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

R1_PACK = REPO_ROOT / "results" / "pass1_window_pack.json"
R1_PREREG = REPO_ROOT / "results" / "prereg_pass1_window.json"
R1_OUT = REPO_ROOT / "results" / "pass1_window_v2.jsonl"
OUT = REPO_ROOT / "results" / "pass1_window_r2_pack.json"
OUT_NAME = "results/pass1_window_r2_pack.json"
LEG_OUT = "pass1_window_r2_v2.jsonl"


def r1_pack() -> dict:
    """The r1 pack, held to the sha its own sealed registration pins."""
    record = json.loads(summary.read_text_or_refuse(R1_PREREG))
    live = summary.sha256_of(R1_PACK)
    pinned = record["population"]["sha256"]
    if live != pinned:
        raise SystemExit(
            f"{summary.rel(R1_PACK)} hashes {live} and {summary.rel(R1_PREREG)} pins {pinned}. The"
            " r1 pack is a sealed input of this build — the 901 would be subtracted from a"
            " population nobody registered. Stop and report."
        )
    return json.loads(summary.read_text_or_refuse(R1_PACK))


def answered(pack: dict) -> list[dict]:
    """The r1 replies, each held to its pack item's sha BEFORE its id is subtracted."""
    leg = pack["legs"][0]
    by_id = {one["id"]: one for one in leg["items"]}
    if len(by_id) != len(leg["items"]):
        raise SystemExit(
            f"{summary.rel(R1_PACK)} carries {len(leg['items'])} items under {len(by_id)} distinct"
            " ids. The subtraction is keyed on the id and an id that names two items makes it"
            " ambiguous — stop and report."
        )
    rows, seen = [], set()
    for line in summary.read_text_or_refuse(R1_OUT).splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        item = by_id.get(row.get("id"))
        if item is None:
            raise SystemExit(
                f"{summary.rel(R1_OUT)} carries {row.get('id')!r}, which the r1 leg never asked."
                " Subtracting it would remove nothing and hide a row nobody can place — stop."
            )
        if row["id"] in seen:
            raise SystemExit(f"{summary.rel(R1_OUT)} carries {row['id']} twice — stop and report.")
        if row.get("rendering_sha256") != item["rendering_sha256"]:
            raise SystemExit(
                f"{row['id']}: the reply carries rendering_sha256 {row.get('rendering_sha256')} and"
                f" the pack item is {item['rendering_sha256']}. That row answered a request this"
                " pack did not register, so it is not evidence that this comment was bought — stop."
            )
        seen.add(row["id"])
        rows.append(row)
    return rows


def membership(items: list[dict]) -> dict:
    """The four sets, over THIS leg — so D2's census rows are derived from the pack, not re-joined."""
    out = {}
    for name in ("gold_14", "probe_64", "labelled_650", "dev_200"):
        ids = sorted(one["id"] for one in items if one["membership"][name])
        out[name] = {"n": len(ids), "ids": ids}
    out["rule"] = (
        "the r1 pack's own per-item flags, filtered to the 901 this leg asks. Each set is now a"
        " PART of its window-wide self: D2 censuses the UNION 131 + 901 and takes each reading over"
        " the whole membership, so `population.membership_of_the_whole_window` below"
        " carries the other half's counts beside these"
    )
    return out


def self_exclusion(items: list[dict]) -> dict:
    """0 items shown a neighbour from their own thread — re-checked on the 901, not inherited."""
    offenders = sorted(
        one["id"]
        for one in items
        if any(near["thread"] == one["thread"] for near in one["examples_chosen"])
    )
    used = {(near["thread"], near["msg_id"]) for one in items for near in one["examples_chosen"]}
    return {
        "items_shown_a_neighbour_from_their_own_thread": offenders,
        "distinct_neighbours_used": len(used),
        "rule": "0 items are shown a neighbour from their own thread — re-derived over these 901",
        "the_withheld_count_is_the_window_s": (
            "`labels_withheld_from_those_items` is a property of the whole window and is not"
            " recomputed here: the neighbour pool and the withholding happened at r1 build time and"
            " these items carry its RESULT. The r1 pack's self_exclusion block is the one to quote"
            " for the window; this block re-checks the only property that could differ on a subset"
        ),
    }


def per_thread(r1_rows: list[dict], items: list[dict]) -> list[dict]:
    """Each thread's shape for the 901 — counts recomputed, the rendered sizes carried from r1.

    `entity_block_chars` and `topic_chars` are properties of the THREAD and not of the subset, and
    measuring them again would mean rendering an item with and without its entity block. This build
    does not render. The counts that DO change with the subset — payable comments and their
    characters — are recomputed from the items.
    """
    by_thread: dict[str, list[dict]] = {}
    for one in items:
        by_thread.setdefault(one["thread"], []).append(one)
    out = []
    for row in r1_rows:
        rows = by_thread.get(row["thread"], [])
        out.append(
            {
                **row,
                "payable_comments": len(rows),
                "comment_chars": sum(len(one["text"]) for one in rows),
                "payable_comments_in_the_window": row["payable_comments"],
                "answered_by_r1": row["payable_comments"] - len(rows),
            }
        )
    return out


def build() -> dict:
    pack = r1_pack()
    leg = pack["legs"][0]
    replies = answered(pack)
    bought = {row["id"] for row in replies}
    items = [one for one in leg["items"] if one["id"] not in bought]

    owed = len(leg["items"]) - len(bought)
    if len(items) != owed:
        raise SystemExit(f"the remainder is {len(items)} and {owed} was subtracted — stop.")
    expected = pack["population"]["payable_comments"] - len(replies)
    if len(items) != expected:
        raise SystemExit(
            f"the leg holds {len(items)} items and the population minus the answered rows is"
            f" {expected}. The pack would ask a number nobody priced — stop and report."
        )

    # a positive control on the length arithmetic: run the SAME function over all 1 032 and it must
    # reproduce the r1 pack's own block. If it does not, the measurement moved and the 901's numbers
    # below are a different instrument's ([[the_fixture_and_the_artifact_share_anchors]])
    control = fewshot.ceiling_check(leg["items"])
    registered = {key: pack["length"][key] for key in control}
    if control != registered:
        raise SystemExit(
            f"re-measuring the r1 pack's own length gives {control} against the registered"
            f" {registered} — the measurement moved, so nothing derived from it can be trusted."
        )
    length = fewshot.ceiling_check(items)

    threads = sorted({one["thread"] for one in items})
    return {
        "phase": "pass1-window-r2",
        "contract": "docs/PROMPT-pass1-window-r2.md D0′",
        "registration": {"record": "results/prereg_pass1_window_r2.json"},
        "what_this_run_is": (
            "the REMAINDER of the r1 production pass: the payable comments of window-1 that the"
            " killed pod never reached. Same population, same prompt v2, same rendering, same"
            " neighbours — a smaller leg of the same run and not a new question. Nothing in it is a"
            " bar on v2's quality"
        ),
        "derived_from": {
            "pack": summary.rel(R1_PACK),
            "pack_sha256": summary.sha256_of(R1_PACK),
            "pack_pinned_by": f"{summary.rel(R1_PREREG)}::population.sha256",
            "out_file": summary.rel(R1_OUT),
            "out_file_sha256": summary.sha256_of(R1_OUT),
            "rule": (
                "items are COPIED from the r1 pack and never re-rendered. Every one of the"
                f" {len(replies)} subtracted ids was verified against its pack item's"
                " rendering_sha256 before it was removed"
            ),
            "subtracted": {
                "n": len(replies),
                "every_one_verified_by_rendering_sha256": True,
                "ids": sorted(bought),
            },
        },
        "population": {
            "cell": pack["population"]["cell"],
            "payable_comments": len(items),
            "payable_comments_in_the_window": pack["population"]["payable_comments"],
            "answered_by_r1": len(replies),
            "threads": len(threads),
            "threads_in_the_cell": pack["population"]["threads"],
            "threads_r1_finished": sorted({one["thread"] for one in leg["items"]} - set(threads)),
            "membership_of_the_whole_window": {
                name: pack["membership"][name]["n"]
                for name in ("gold_14", "probe_64", "labelled_650", "dev_200")
            },
            "producer": pack["population"]["producer"],
            "producer_sha256": pack["population"]["producer_sha256"],
            "producer_rule": (
                "the CELL was enumerated by gate_census_w1_reader.population() at r1 build time and"
                " this pack does not call it again: these items ARE r1's items, and re-enumerating"
                " could only disagree with the population the sealed r1 record registered"
            ),
            "rule": (
                "`payable_comments` is what THIS leg asks — the 901 the r1 pod never reached — and"
                " it is the number the gate holds its own registration to. The window's own 1 032"
                " is beside it, with what r1 bought, because D2 censuses the UNION 131 + 901 keyed"
                " on the PAIR (thread, msg_id): this block is what makes that union derivable from"
                " the pack instead of re-joined by hand after the money is spent"
            ),
        },
        "legs": [
            {
                "name": leg["name"],
                "task": leg["task"],
                "out": LEG_OUT,
                "reading": (
                    "the ONE leg, as r1's was. The base was measured in the r2 dev registration and"
                    " is not re-run: no second leg, no dev gate, no paired arm"
                ),
                "items": items,
            }
        ],
        "membership": membership(items),
        "length": length,
        "self_exclusion": self_exclusion(items),
        "per_thread": per_thread(pack["per_thread"], items),
        "order_rule": pack["order_rule"],
        "reading": pack["reading"],
        "balance": pack["balance"],
        "context": pack["context"],
        "neighbours": pack["neighbours"],
        "serving": pack["serving"],
        "instruments": pack["instruments"],
        "gold_id_collisions": pack["gold_id_collisions"],
        "gold_threads_in_the_population": pack["gold_threads_in_the_population"],
        "carried_verbatim_from_r1": [
            "order_rule",
            "reading",
            "balance",
            "context",
            "neighbours",
            "serving",
            "instruments",
            "gold_id_collisions",
            "gold_threads_in_the_population",
        ],
        "carried_verbatim_rule": (
            "these blocks describe the RENDERING and the serving, and neither moved: the items are"
            " the r1 items. Recomputing them would either re-render (forbidden — it moves the shas)"
            " or re-measure something that cannot have changed. The blocks that ARE recomputed over"
            " the 901 are membership, length, self_exclusion and per_thread"
        ),
        "producer": {
            "script": summary.rel(Path(__file__)),
            "sha256": summary.sha256_of(Path(__file__)),
            "borrowed": {
                "scripts/build_pass1_fewshot_packs.py": summary.sha256_of(
                    REPO_ROOT / "scripts" / "build_pass1_fewshot_packs.py"
                ),
            },
            "borrowed_rule": "ceiling_check only — it reads `rendered_chars` and renders nothing",
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)

    pack = build()
    args.out.write_text(
        json.dumps(pack, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    leg = pack["legs"][0]
    window = pack["population"]
    print(f"wrote {summary.rel(args.out)}  sha256 {summary.sha256_of(args.out)[:16]}…")
    print(
        f"  owed: {window['payable_comments']} of"
        f" {window['payable_comments_in_the_window']} payable comments —"
        f" {window['answered_by_r1']} answered by r1 and subtracted by id, each verified by sha"
    )
    print(
        f"  one leg {leg['name']} → {leg['out']} · {len(leg['items'])} items ·"
        f" {window['threads']} threads carry one"
        f" ({len(window['threads_r1_finished'])} finished by r1)"
    )
    print(
        f"  length: widest {pack['length']['widest_request_chars']} chars"
        f" ({pack['length']['widest_request']}) · median {pack['length']['median_chars']} ·"
        f" headroom {pack['length']['headroom_chars']} of {pack['length']['ceiling_chars']}"
    )
    print(
        "  self-exclusion:"
        f" {len(pack['self_exclusion']['items_shown_a_neighbour_from_their_own_thread'])} items"
        f" shown their own thread · {pack['self_exclusion']['distinct_neighbours_used']} distinct"
        " neighbours used"
    )
    print(
        "  membership here: "
        + " · ".join(
            f"{name} {pack['membership'][name]['n']} of"
            f" {window['membership_of_the_whole_window'][name]}"
            for name in ("gold_14", "probe_64", "labelled_650", "dev_200")
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
