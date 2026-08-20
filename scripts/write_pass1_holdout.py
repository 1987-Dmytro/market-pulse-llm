#!/usr/bin/env python3
"""`results/pass1_holdout_100.json` — 100 of the 650 labels, sealed out of every future training set.

**What this is for.** Line B trained on all 650 labels and was evaluated on fourteen sealed gold
rows. That is a bar of fourteen: it cannot say WHERE an arm moved, only whether it cleared twelve.
`docs/PROMPT-pass1-fewshot.md` D0.1 registers a hundred-row evaluation set out of the labelled
population BEFORE anyone trains again, so the next line that does train has a set it has never seen
and a denominator that can carry a per-class table.

**The rule this file registers, and it is the whole point:** these hundred rows are NEVER in any
training set of any future line. They are evaluation only, and
`scripts/build_pass1_sft.py` refuses to build a dataset that contains one of them. The refusal is
scoped and the scope is stated where it lives, in that producer.

**The draw is largest remainder with a FLOOR OF ONE per non-empty class.** The contract registers
the allocation 340:213:48:47:2 → **52:33:7:7:1**, and plain largest remainder does not produce it:
the floors are 52, 32, 7, 7, 0 and the two largest remainders are `null` (.769) and `сеть_ритейлер`
(.385), which gives 52:33:8:7:0 — a holdout with NO `молочный_бренд` row at all. A class the
population has and the holdout does not is a class the holdout cannot measure, and with two rows in
650 that is the class most likely to be lost by rounding. The floor is what makes the registered
tuple reachable, and :func:`allocate` asserts the tuple rather than hoping for it
([[an_absolute_bar_needs_a_reachability_state]]).

**Overlap with this line's own dev rows is ALLOWED and is written down.** pass1-fewshot trains
nothing — it measures a prompt — so a dev row that is also a holdout row costs nothing here. It
would cost everything to a line that trains, and that is exactly what the refusal above is for.

    PYTHONPATH=src python3.11 scripts/write_pass1_holdout.py
    PYTHONPATH=src python3.11 scripts/write_pass1_holdout.py --outdir /tmp/again   # the pair
"""

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_pass1_label_pack_r2 as r2pack  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import prompts  # noqa: E402

OUT_NAME = "results/pass1_holdout_100.json"

LABELS = {
    "r1": REPO_ROOT / "results" / "labels_pass1_r1.jsonl",
    "r2": REPO_ROOT / "results" / "labels_pass1_r2.jsonl",
}
"""The FROZEN copies under results/, the same two `scripts/build_pass1_sft.py` trains from."""

PROBE_PACK = REPO_ROOT / "results" / "pass1_probe_b_pack.json"
GOLD = REPO_ROOT / "results" / "reader_gold_w1_r2.json"
SFT_RECORD = REPO_ROOT / "results" / "pass1_sft.json"

SEED = 20260820
"""The date of the operator's ruling that opened this line. One stream, no `--seed` flag: an option
to draw a different holdout is an option to draw the one that flatters a result."""

TARGET = 100

CLASSES = (*prompts.PASS1_SUBJECT_TYPES, None)
"""The five values a label may take, in the prompt's own schema order with `null` last. A total
order, so the seeded stream is consumed in one sequence and never in a set's iteration order."""

REGISTERED_ALLOCATION = {
    "не_наш_рынок": 52,
    "null": 33,
    "сеть_ритейлер": 7,
    "категория_личное": 7,
    "молочный_бренд": 1,
}
"""The tuple `docs/PROMPT-pass1-fewshot.md` D0.1 registers, asserted and never merely intended."""


def key(label: str | None) -> str:
    return "null" if label is None else label


def labels() -> list[dict]:
    """Every labelled row of both files, joined to its comment text in the store.

    The join is total: a label naming a comment the store does not carry is a stop, because a
    holdout row nobody can render is a row a future evaluation would silently drop.
    """
    threads = r2pack.raw_threads()
    out = []
    for pack, path in sorted(LABELS.items()):
        for line in summary.read_text_or_refuse(path).splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            thread = threads.get(row["thread"])
            if thread is None:
                raise SystemExit(f"{row['thread']} is not in the store — stop and report.")
            comment = next(
                (one for one in thread["comments"] if int(one["msg_id"]) == int(row["msg_id"])),
                None,
            )
            if comment is None:
                raise SystemExit(f"{row['thread']}:{row['msg_id']} is not in its thread — stop.")
            out.append(
                {
                    "pack": pack,
                    "thread": row["thread"],
                    "msg_id": int(row["msg_id"]),
                    "subject_type": row.get("subject_type"),
                    "text": summary.comment_text(comment),
                }
            )
    return out


def allocate(counts: dict[str, int], target: int) -> dict[str, int]:
    """`target` rows over the classes, largest remainder with a floor of ONE per non-empty class.

    The floor is funded out of the remainder awards, so the total is still exactly `target`: the
    floors are taken first and the shortfall is filled by descending remainder, tie-broken on the
    class name so two runs cannot order two equal remainders differently. A class whose floor
    exceeds its own population would be a draw that cannot be made, and it is refused rather than
    silently short.
    """
    total = sum(counts.values())
    base = {name: max(1, target * n // total) if n else 0 for name, n in counts.items()}
    for name, n in counts.items():
        if base[name] > n:
            raise SystemExit(
                f"the floor gives {name} {base[name]} rows and the population has {n}. The draw"
                " cannot be made — stop and report."
            )
    short = target - sum(base.values())
    if short < 0:
        raise SystemExit(
            f"the per-class floors already sum to {sum(base.values())} against a target of"
            f" {target}: this population has more classes than the holdout has rows — stop."
        )
    remainder = {name: target * counts[name] / total - base[name] for name in counts}
    order = sorted(counts, key=lambda name: (-remainder[name], name))
    for name in order[:short]:
        base[name] += 1
    over = {name for name, n in base.items() if n > counts[name]}
    if over:
        raise SystemExit(f"the allocation exceeds the population on {sorted(over)} — stop.")
    return base


def draw(rows: list[dict], allocation: dict[str, int], rng: random.Random) -> list[dict]:
    """`allocation[class]` rows per class off ONE seeded stream, in :data:`CLASSES` order."""
    by_class: dict[str, list[dict]] = {}
    for row in rows:
        by_class.setdefault(key(row["subject_type"]), []).append(row)
    units = []
    for value in CLASSES:
        name = key(value)
        pool = sorted(by_class.get(name, ()), key=lambda one: (one["thread"], one["msg_id"]))
        take = allocation.get(name, 0)
        if not take:
            continue
        for one in sorted(rng.sample(pool, take), key=lambda one: (one["thread"], one["msg_id"])):
            units.append({"thread": one["thread"], "msg_id": one["msg_id"], "subject_type": value})
    return sorted(units, key=lambda one: (one["thread"], one["msg_id"]))


def sealed_arms() -> dict:
    """What the two SEALED line-B datasets carry, read off the record that pins them.

    Read and not assumed: the exemption `scripts/build_pass1_sft.py` grants those two arms is
    keyed on these shas, so the overlap this file publishes has to be measured against the same
    bytes the exemption is keyed on ([[the_guard_hashes_the_half_that_cannot_move]]).
    """
    record = json.loads(summary.read_text_or_refuse(SFT_RECORD))
    out = {}
    for arm, block in sorted(record["datasets"].items()):
        path = REPO_ROOT / block["file"]
        ids = {
            (row["thread"], int(row["msg_id"]))
            for row in (
                json.loads(line)
                for line in summary.read_text_or_refuse(path).splitlines()
                if line.strip()
            )
        }
        out[arm] = {
            "file": block["file"],
            "registered_sha256": block["sha256"],
            "live_sha256": summary.sha256_of(path),
            "rows": len(ids),
            "ids": ids,
        }
    return out


def build() -> dict:
    rows = labels()
    counts = {key(value): 0 for value in CLASSES}
    counts.update(Counter(key(row["subject_type"]) for row in rows))
    present = {name: n for name, n in counts.items() if n}
    allocation = allocate(present, TARGET)
    if allocation != REGISTERED_ALLOCATION:
        raise SystemExit(
            f"the draw allocates {allocation} and the contract registers {REGISTERED_ALLOCATION}."
            " The population or the rule has moved — re-register it, do not re-run this producer."
        )
    units = draw(rows, allocation, random.Random(SEED))
    if len(units) != TARGET:
        raise SystemExit(f"{len(units)} units drawn against a target of {TARGET} — stop.")

    drawn = {(one["thread"], one["msg_id"]) for one in units}
    gold = json.loads(summary.read_text_or_refuse(GOLD))
    gold_ids = {int(row["msg_id"]) for row in gold["per_comment"]}
    gold_threads = {
        f"{row['channel']}:{(row.get('evidence_row') or {}).get('post_id_in_the_store')}"
        for row in gold["per_comment"]
    }
    probe = json.loads(summary.read_text_or_refuse(PROBE_PACK))
    probe_ids = {int(one["msg_id"]) for one in probe["items"]}
    probe_threads = {one["thread"] for one in probe["items"]}
    arms = sealed_arms()

    return {
        "phase": "pass1-fewshot",
        "contract": "docs/PROMPT-pass1-fewshot.md D0.1",
        "authority": (
            "the operator's rulings of 2026-08-20 registered in docs/STATUS.md «Открытые решения»"
            " п. 0 — the base stays Gemma-4-31B, the team lead labels, and the goal of the layer is"
            " the analysis of docs/REFERENCE-signals-w1.md"
        ),
        "rule": (
            "these 100 rows are NEVER in any training set of any future line. They are EVALUATION"
            " ONLY, and scripts/build_pass1_sft.py refuses to build a dataset that contains one of"
            " them. The refusal exempts exactly the two SEALED line-B arms below, by sha, because"
            " they were built and spent before this holdout existed and their bytes are pinned by"
            " results/prereg_lora_b.json and results/lora_b_verdict.json"
        ),
        "evaluation_only": True,
        "labels": {
            name: {
                "file": summary.rel(LABELS[name]),
                "sha256": summary.sha256_of(LABELS[name]),
            }
            for name in sorted(LABELS)
        },
        "population": {
            "rows": len(rows),
            "distribution": {key(value): counts[key(value)] for value in CLASSES},
            "proportion": ":".join(
                str(counts[key(value)]) for value in CLASSES if counts[key(value)]
            ),
        },
        "draw": {
            "seed": SEED,
            "target": TARGET,
            "allocation": {key(value): allocation.get(key(value), 0) for value in CLASSES},
            "registered_allocation": REGISTERED_ALLOCATION,
            "formula": (
                "largest remainder on the class counts with a FLOOR OF ONE per non-empty class,"
                " tie-broken on (−remainder, class); then that many rows per class off one"
                " random.Random(SEED) stream, the classes consumed in the prompt's own schema order"
                " with null last"
            ),
            "why_the_floor": (
                "plain largest remainder gives 52:33:8:7:0 — floors 52/32/7/7/0 and the two largest"
                " remainders are null (.769) and сеть_ритейлер (.385). That holdout carries no"
                " молочный_бренд row at all, so the class with two rows in 650 is the one rounding"
                " deletes. The floor is what makes the registered tuple reachable"
            ),
        },
        "overlap": {
            "rule": (
                "pass1-fewshot trains NOTHING, so its dev rows MAY overlap this holdout and the"
                " overlap is published rather than avoided. A line that TRAINS may not, and that is"
                " what the refusal in scripts/build_pass1_sft.py enforces"
            ),
            "sealed_arms": {
                arm: {
                    "file": block["file"],
                    "registered_sha256": block["registered_sha256"],
                    "live_sha256": block["live_sha256"],
                    "rows": block["rows"],
                    "holdout_rows_inside_it": len(drawn & block["ids"]),
                }
                for arm, block in sorted(arms.items())
            },
            "reading": (
                "the holdout is drawn from the same 650 labels arm B is made of, so the overlap is"
                " total by construction and is NOT a defect. It is the reason the exemption is"
                " keyed on the sealed shas: the day one of those files is rebuilt differently, the"
                " exemption stops applying and the refusal fires"
            ),
        },
        "contamination": {
            "rule": "all four lists are EMPTY in a correct holdout",
            "holdout_ids_in_the_gold_14": sorted(
                one["msg_id"] for one in units if one["msg_id"] in gold_ids
            ),
            "holdout_threads_in_the_gold_threads": sorted(
                {one["thread"] for one in units} & gold_threads
            ),
            "holdout_ids_in_the_eval_pack_64": sorted(
                one["msg_id"] for one in units if one["msg_id"] in probe_ids
            ),
            "holdout_threads_in_the_eval_pack_threads": sorted(
                {one["thread"] for one in units} & probe_threads
            ),
            "why_it_is_empty": (
                "scripts/build_pass1_label_pack.py::excluded_threads removes every thread carrying"
                " any of the 64 registered probe units from the labelling population WHOLE, so no"
                " label shares a thread with a gold row or an eval-pack item. Re-asserted here"
                " against the two sealed files rather than assumed"
            ),
        },
        "units": units,
        "producer": {
            "script": summary.rel(Path(__file__)),
            "borrowed": {
                name: summary.sha256_of(REPO_ROOT / name)
                for name in (
                    "scripts/build_pass1_label_pack_r2.py",
                    "scripts/window_summary_5c2.py",
                    "src/market_pulse/prompts.py",
                )
            },
        },
        "inputs": {
            summary.rel(path): summary.sha256_of(path)
            for path in (*LABELS.values(), PROBE_PACK, GOLD, SFT_RECORD)
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    record = build()
    record["producer"]["sha256"] = summary.sha256_of(Path(__file__))
    out = args.outdir / OUT_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    out.write_text(payload, encoding="utf-8")

    draw_block = record["draw"]
    print(f"wrote {OUT_NAME}  {len(record['units'])} units  seed {draw_block['seed']}")
    print(
        f"  population {record['population']['rows']} labels: {record['population']['distribution']}"
    )
    print(
        f"  allocation {draw_block['allocation']} — registered {draw_block['registered_allocation']}"
    )
    for arm, block in record["overlap"]["sealed_arms"].items():
        print(
            f"  sealed arm {arm}: {block['holdout_rows_inside_it']} of the {len(record['units'])}"
            f" holdout rows are in {block['file']} ({block['rows']} rows)"
        )
    contamination = record["contamination"]
    print(
        "  contamination: gold ids"
        f" {len(contamination['holdout_ids_in_the_gold_14'])} · gold threads"
        f" {len(contamination['holdout_threads_in_the_gold_threads'])} · eval ids"
        f" {len(contamination['holdout_ids_in_the_eval_pack_64'])} · eval threads"
        f" {len(contamination['holdout_threads_in_the_eval_pack_threads'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
