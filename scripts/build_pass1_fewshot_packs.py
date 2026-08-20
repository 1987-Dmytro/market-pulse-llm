#!/usr/bin/env python3
"""The two packs of pass1-fewshot — the dev-200 in both legs, and the sealed fourteen under v2.

**What this builds.** `docs/PROMPT-pass1-fewshot.md` D0.3 and D0.4, at $0, with no cloud call:

- `results/pass1_dev_pack.json` — 200 labelled rows, each rendered TWICE. Leg `base` is the frozen
  v1 request with no examples; leg `v2` is the same row under `pass1_comment_gm4_v2` with five
  labelled neighbours. The two legs are the paired instrument: same rows, same context, one
  difference.
- `results/pass1_probe_b_pack_v2.json` — probe-b's 64 units, identity and ORDER unchanged, under v2
  with the same five-neighbour block. The sealed `results/pass1_probe_b_pack.json` is read and never
  touched, and the base's per-row verdicts are never re-run.

**One example per class, and that is the whole design.** Nearest-k over the 650 labels would hand
the model the same 52% `не_наш_рынок` prior the LoRA of line B learned instead of the decision
([[an_identical_count_is_not_an_identical_model]]). Balance is by CONSTRUCTION: for each of the five
readings — the four subject types and the null — the single nearest labelled comment by Jaccard
similarity over lower-cased character 3-grams, ties to the smaller `msg_id`. The pool is the 650
labels MINUS every row of the query's own thread, so a query is never shown its own neighbourhood.

**Every rendering is pinned per item.** `rendering_sha256` is the sha of the request the pod will
rebuild from the item's own fields, and the five chosen `(thread, msg_id, label)` are written down
beside it, so the shot is reproducible from the file and not from this script's mood.

**Contamination is printed as four EMPTY lists** — neighbour ids and neighbour threads against the
sealed fourteen and against the eval pack's sixty-four. It is empty by construction (no label
shares a thread with a probe unit: `build_pass1_label_pack.py::excluded_threads` removed those
threads whole) and it is re-asserted here rather than assumed.

    PYTHONPATH=src python3.11 scripts/build_pass1_fewshot_packs.py
    PYTHONPATH=src python3.11 scripts/build_pass1_fewshot_packs.py --outdir /tmp/again   # the pair
"""

import argparse
import hashlib
import json
import random
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_pass1_sft as sft  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import prompts  # noqa: E402

DEV_NAME = "results/pass1_dev_pack.json"
SHOT_NAME = "results/pass1_probe_b_pack_v2.json"

PROBE_PACK = REPO_ROOT / "results" / "pass1_probe_b_pack.json"
GOLD = REPO_ROOT / "results" / "reader_gold_w1_r2.json"
HOLDOUT = REPO_ROOT / "results" / "pass1_holdout_100.json"

SEED = 20260820
"""The operator's ruling date, and the only randomness here — the same constant the holdout draws
under, on its own stream. No `--seed`: an option to draw a different dev set is an option to draw
the one that flatters the prompt."""

DEV_TARGET = 200
DEV_TOPPED_UP = 151
"""The rows drawn from the 601 that are not «ours». All 49 «our» rows are taken WHOLE — the gate
counts correct rows among them, and sampling the class the bar is about would put noise in the
numerator ([[measure_on_the_rows_the_gate_scores]])."""

OUR = ("категория_личное", "молочный_бренд")
"""The two readings the dev gate's first inequality counts. `категория_личное` is the class of all
four «категория» misses of the base and `молочный_бренд` is the class beside it in the taxonomy."""

CLASSES = (*prompts.PASS1_SUBJECT_TYPES, None)
GRAM = 3

DEV_LEGS = {"base": "pass1_dev_base.jsonl", "v2": "pass1_dev_v2.jsonl"}
SHOT_LEG = {"shot": "pass1_fewshot_shot.jsonl"}
"""Each leg names the out-file it is answered into, IN THE PACK. The shot's file is its own and
never a dev one: the shipped runner's resume skips every unit already answered, so a shot written
into a dev file would answer fewer units and look complete (Dv560)."""


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def key(label: str | None) -> str:
    return "null" if label is None else label


def grams(text: str) -> frozenset[str]:
    """Lower-cased character 3-grams. A text under three characters has NONE, and says so.

    Not padded to force a gram out of a one-character comment: padding would make «)» and «(»
    similar through the padding rather than through themselves. An empty set scores 0.0 against
    everything and the tie-break decides — which is a stated outcome, not a silent one.
    """
    flat = (text or "").casefold()
    return frozenset(flat[at : at + GRAM] for at in range(len(flat) - GRAM + 1))


def jaccard(left: frozenset[str], right: frozenset[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def pool() -> list[dict]:
    """The 650 labelled rows with their comment text, off the SFT producer's own join.

    `build_pass1_sft.labelled_units()` is called rather than re-implemented: it is the join that
    already refuses a label with no unit, a unit in an exam thread and a gold msg_id, and a second
    spelling of it here would be a second population nobody diffed.
    """
    return [
        {
            "thread": one["thread"],
            "msg_id": int(one["msg_id"]),
            "subject_type": one["subject_type"],
            "text": one["text"],
            "grams": grams(one["text"]),
        }
        for one in sft.labelled_units()
    ]


def neighbours(query_thread: str, query_grams: frozenset[str], labels: list[dict]) -> list[dict]:
    """One nearest labelled comment per class, from every thread but the query's own.

    Ties — and a query whose own 3-gram set is empty ties everything at 0.0 — go to the smaller
    `msg_id`, then to the thread name, so the key is TOTAL and two runs cannot order two equal
    similarities differently ([[an_order_key_that_is_not_total]]).
    """
    chosen = []
    for value in CLASSES:
        candidates = [
            one for one in labels if one["thread"] != query_thread and one["subject_type"] == value
        ]
        if not candidates:
            raise SystemExit(
                f"no labelled {key(value)} comment outside {query_thread}: this query cannot be"
                " given one example of each class, and a four-example block is a different"
                " instrument from a five-example one — stop and report."
            )
        best = min(
            candidates,
            key=lambda one: (-jaccard(query_grams, one["grams"]), one["msg_id"], one["thread"]),
        )
        chosen.append(
            {
                "thread": best["thread"],
                "msg_id": best["msg_id"],
                "label": value,
                "text": best["text"],
                "similarity": round(jaccard(query_grams, best["grams"]), 6),
            }
        )
    return chosen


def examples_of(chosen: list[dict]) -> list[dict]:
    """What the renderer is given: the text and the label, never the ids."""
    return [{"text": one["text"], "label": one["label"]} for one in chosen]


def rendered_item(fields: dict, task: str, chosen: list[dict] | None) -> dict:
    """One pack item — the fields the pod re-renders from, and the sha it must reproduce."""
    content = prompts.pass1_messages_gm4(
        fields["channel"],
        fields["post_id"],
        fields["topic"],
        fields["entities"],
        fields["msg_id"],
        fields["text"],
        task=task,
        examples=None if chosen is None else examples_of(chosen),
    )[0]["content"]
    item = {
        **fields,
        "task": task,
        "rendered_chars": len(content),
        "rendering_sha256": sha_text(content),
    }
    if chosen is not None:
        item["examples"] = examples_of(chosen)
        item["examples_chosen"] = [
            {
                "thread": one["thread"],
                "msg_id": one["msg_id"],
                "label": key(one["label"]),
                "similarity": one["similarity"],
            }
            for one in chosen
        ]
    return item


def dev_units(labels: list[dict], rng: random.Random) -> tuple[list[dict], dict]:
    """All 49 «our» rows, then 151 of the other 601 by largest remainder on the class counts."""
    ours = sorted(
        (one for one in labels if one["subject_type"] in OUR),
        key=lambda one: (one["thread"], one["msg_id"]),
    )
    rest = [one for one in labels if one["subject_type"] not in OUR]
    counts = Counter(key(one["subject_type"]) for one in rest)
    total = sum(counts.values())
    base = {name: DEV_TOPPED_UP * n // total for name, n in counts.items()}
    remainder = {name: DEV_TOPPED_UP * counts[name] / total - base[name] for name in counts}
    order = sorted(counts, key=lambda name: (-remainder[name], name))
    for name in order[: DEV_TOPPED_UP - sum(base.values())]:
        base[name] += 1
    if sum(base.values()) != DEV_TOPPED_UP or any(base[n] > counts[n] for n in counts):
        raise SystemExit(f"the top-up allocation {base} does not fit {dict(counts)} — stop.")

    drawn = []
    for value in CLASSES:
        name = key(value)
        take = base.get(name, 0)
        if not take:
            continue
        candidates = sorted(
            (one for one in rest if key(one["subject_type"]) == name),
            key=lambda one: (one["thread"], one["msg_id"]),
        )
        drawn += rng.sample(candidates, take)
    units = sorted(ours + drawn, key=lambda one: (one["thread"], one["msg_id"]))
    if (
        len(units) != DEV_TARGET
        or len({(one["thread"], one["msg_id"]) for one in units}) != DEV_TARGET
    ):
        raise SystemExit(f"{len(units)} dev rows drawn against a target of {DEV_TARGET} — stop.")
    return units, {
        "ours_taken_whole": len(ours),
        "ours_rule": (
            f"every labelled row of {' and '.join(OUR)} — the classes the dev gate's first"
            " inequality counts. Sampling them would put draw noise in the gate's own numerator"
        ),
        "rest_population": dict(sorted(counts.items())),
        "rest_allocation": dict(sorted(base.items())),
        "rest_formula": (
            f"largest remainder of {DEV_TOPPED_UP} over the class counts of the other"
            f" {total} labelled rows, tie-broken on (−remainder, class), drawn off one"
            " random.Random(SEED) stream in the prompt's own schema order with null last"
        ),
    }


def context() -> tuple[dict, int]:
    """The topic and entity block every dev request carries — the SFT producer's own rendering.

    `verdicts()` and `envelope()` are that producer's, called and not copied: the dev leg has to be
    the base's request as `results/pass1_sft.json` records it, and a second implementation of the
    substitution rule would be a second context nobody diffed
    ([[build_the_training_prompt_with_the_inference_call]]).
    """
    found = sft.verdicts()
    return found, int(sft.envelope(found)["limit"])


def instruments() -> dict:
    """probe-b's instruments, with the two shas that MOVED recomputed and nothing else touched.

    `parser.sha256` is `src/market_pulse/prompts.py`'s module sha and it moved when v2 was added;
    `prompt_sha256` has to cover the WHOLE `prompts.PASS1` family, because that is the map
    `scripts/pass1_pod_runner.py::check_instrument` compares against on the pod. Copying the sealed
    block verbatim would ship a handshake this checkout cannot pass.
    """
    probe = json.loads(summary.read_text_or_refuse(PROBE_PACK))
    block = json.loads(json.dumps(probe["instruments"]))
    block["parser"]["sha256"] = summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "prompts.py")
    block["prompt_sha256"] = {task: prompts.prompt_sha256(task) for task in sorted(prompts.PASS1)}
    block["moved_from_the_sealed_pack"] = {
        "parser.sha256": probe["instruments"]["parser"]["sha256"],
        "prompt_sha256": probe["instruments"]["prompt_sha256"],
        "why": (
            "prompts.py grew pass1_comment_gm4_v2, so its module sha moved and the served pass-1"
            " family became two texts. The pod's handshake compares the whole family map, so a"
            " verbatim copy of the sealed block would refuse this checkout. v1's own sha is"
            " UNCHANGED and is in the map beside v2 — that is what makes the paired legs comparable"
        ),
    }
    return block


def ceiling_check(items: list[dict]) -> dict:
    """The rendered length against `prompts.PASS1_MAX_INPUT_CHARS`, measured over every item.

    The renderer REFUSES a request over the ceiling rather than truncating it, so a breach would be
    a `ValueError` above and never a quiet short request. This is the number that says how much
    room the five-example block actually left ([[compute_the_ceiling_first]]).
    """
    widest = max(items, key=lambda one: (one["rendered_chars"], one["id"]))
    return {
        "ceiling_chars": prompts.PASS1_MAX_INPUT_CHARS,
        "widest_request_chars": widest["rendered_chars"],
        "widest_request": widest["id"],
        "headroom_chars": prompts.PASS1_MAX_INPUT_CHARS - widest["rendered_chars"],
        "median_chars": sorted(one["rendered_chars"] for one in items)[len(items) // 2],
    }


def contamination(items: list[dict]) -> dict:
    """The four lists, EMPTY in a correct pack — neighbour ids and threads against both exams."""
    gold = json.loads(summary.read_text_or_refuse(GOLD))
    gold_ids = {int(row["msg_id"]) for row in gold["per_comment"]}
    gold_threads = {
        f"{row['channel']}:{(row.get('evidence_row') or {}).get('post_id_in_the_store')}"
        for row in gold["per_comment"]
    }
    probe = json.loads(summary.read_text_or_refuse(PROBE_PACK))
    probe_ids = {int(one["msg_id"]) for one in probe["items"]}
    probe_threads = {one["thread"] for one in probe["items"]}

    used_ids, used_threads = set(), set()
    for item in items:
        for one in item.get("examples_chosen") or ():
            used_ids.add(int(one["msg_id"]))
            used_threads.add(one["thread"])
    own = sorted(
        item["id"]
        for item in items
        if any(one["thread"] == item["thread"] for one in (item.get("examples_chosen") or ()))
    )
    return {
        "rule": "all four lists are EMPTY in a correct pack",
        "neighbour_ids_in_the_gold_14": sorted(used_ids & gold_ids),
        "neighbour_threads_in_the_gold_threads": sorted(used_threads & gold_threads),
        "neighbour_ids_in_the_eval_pack_64": sorted(used_ids & probe_ids),
        "neighbour_threads_in_the_eval_pack_threads": sorted(used_threads & probe_threads),
        "items_shown_a_neighbour_from_their_own_thread": own,
        "distinct_neighbours_used": len(used_ids),
        "why_it_is_empty": (
            "no label shares a thread with a probe unit — build_pass1_label_pack.py::excluded_"
            "threads removed those 7 threads WHOLE from the labelling population — so the pool the"
            " neighbours are drawn from is disjoint from both exams by construction"
        ),
    }


def balance(items: list[dict]) -> dict:
    """What the example blocks are made of, so «one per class» is a measured claim."""
    per_item = Counter(len(item.get("examples_chosen") or ()) for item in items)
    labels = Counter(one["label"] for item in items for one in (item.get("examples_chosen") or ()))
    return {
        "examples_per_item": dict(sorted(per_item.items())),
        "label_totals": {key(value): labels.get(key(value), 0) for value in CLASSES},
        "rule": (
            "exactly five per item, one of each reading. The totals are equal BY CONSTRUCTION and"
            " that is the point: nearest-k would have reproduced the 52% не_наш_рынок prior the"
            " adapter of line B learned instead of the decision"
        ),
    }


def build() -> tuple[dict, dict]:
    labels = pool()
    if len(labels) != 650:
        raise SystemExit(f"{len(labels)} labelled rows, and the contract registers 650 — stop.")
    found, limit = context()
    rng = random.Random(SEED)
    units, draw = dev_units(labels, rng)

    by_key = {(one["thread"], one["msg_id"]): one for one in labels}
    sources = {(one["thread"], int(one["msg_id"])): one for one in sft.labelled_units()}
    dev_base, dev_v2 = [], []
    for unit in units:
        at = (unit["thread"], unit["msg_id"])
        fields = sft.request(sources[at], found, limit)["fields"]
        chosen = neighbours(unit["thread"], by_key[at]["grams"], labels)
        dev_base.append(rendered_item(fields, prompts.PASS1_TASK, None))
        dev_v2.append(rendered_item(fields, prompts.PASS1_TASK_V2, chosen))

    probe = json.loads(summary.read_text_or_refuse(PROBE_PACK))
    shot = []
    for item in probe["items"]:
        fields = {
            name: item[name]
            for name in (
                "id",
                "thread",
                "channel",
                "post_id",
                "topic",
                "entities",
                "msg_id",
                "text",
            )
        }
        chosen = neighbours(item["thread"], grams(item["text"]), labels)
        one = rendered_item(fields, prompts.PASS1_TASK_V2, chosen)
        one["leg"] = item["leg"]
        one["part"] = item.get("part")
        one["payable_comments"] = item["payable_comments"]
        shot.append(one)

    if [one["id"] for one in shot] != [one["id"] for one in probe["items"]]:
        raise SystemExit("the shot pack's identity or order left the sealed pack's — stop.")

    common = {
        "phase": "pass1-fewshot",
        "contract": "docs/PROMPT-pass1-fewshot.md D0.4",
        "instruments": instruments(),
        "serving": probe["serving"],
        "registration": {"record": "results/prereg_pass1_fewshot.json"},
        "neighbours": {
            "rule": (
                "for each of the five readings — the four subject types and the null — the single"
                " nearest labelled comment by Jaccard similarity over lower-cased character"
                f" {GRAM}-grams of the comment text, from the 650 labels MINUS every row of the"
                " query's own thread. Ties to the smaller msg_id, then to the thread"
            ),
            "pool": {
                "rows": len(labels),
                "files": {
                    name: summary.sha256_of(path) for name, path in sorted(sft.LABELS.items())
                },
            },
            "why_one_per_class": (
                "balance by construction. Nearest-k over this pool is 52% не_наш_рынок, which is"
                " the marginal the LoRA of line B learned instead of the decision, and a block that"
                " carried it would teach the same prior with none of the training"
            ),
        },
        "reading": probe["reading"],
        "order_rule": probe["order_rule"],
    }

    dev = {
        **common,
        "population": {
            "rows": len(units),
            "distribution": {
                key(value): sum(1 for one in units if key(one["subject_type"]) == key(value))
                for value in CLASSES
            },
            "our_rows": sum(1 for one in units if one["subject_type"] in OUR),
        },
        "draw": {"seed": SEED, "target": DEV_TARGET, **draw},
        "legs": [
            {
                "name": "base",
                "task": prompts.PASS1_TASK,
                "out": DEV_LEGS["base"],
                "reading": "the frozen v1 request, no examples — the base arm of the paired dev run",
                "items": dev_base,
            },
            {
                "name": "v2",
                "task": prompts.PASS1_TASK_V2,
                "out": DEV_LEGS["v2"],
                "reading": "the same 200 rows, same context, under v2 with five labelled neighbours",
                "items": dev_v2,
            },
        ],
        "paired": {
            "rule": (
                "the two legs carry the SAME 200 (thread, msg_id) rows in the same order, and the"
                " only difference between a base item and its v2 twin is the task and the examples"
                " block. Asserted below rather than intended"
            ),
            "same_rows": [one["id"] for one in dev_base] == [one["id"] for one in dev_v2],
            "same_context": all(
                base["topic"] == v2["topic"] and base["entities"] == v2["entities"]
                for base, v2 in zip(dev_base, dev_v2)
            ),
        },
        "balance": balance(dev_v2),
        "contamination": contamination(dev_v2),
        "length": ceiling_check(dev_base + dev_v2),
        "holdout": {
            "record": summary.rel(HOLDOUT),
            "sha256": summary.sha256_of(HOLDOUT),
            "dev_rows_that_are_holdout_rows": len(
                {(one["thread"], one["msg_id"]) for one in units}
                & {
                    (one["thread"], int(one["msg_id"]))
                    for one in json.loads(summary.read_text_or_refuse(HOLDOUT))["units"]
                }
            ),
            "rule": (
                "this line TRAINS NOTHING, so a dev row may also be a holdout row and the overlap is"
                " published rather than avoided. It would disqualify a line that trained"
            ),
        },
    }

    shot_pack = {
        **common,
        "contract": "docs/PROMPT-pass1-fewshot.md D0.4(b)",
        "legs": [
            {
                "name": "shot",
                "task": prompts.PASS1_TASK_V2,
                "out": SHOT_LEG["shot"],
                "reading": (
                    "the ONE shot: probe-b's 64 units, identity and order unchanged, under v2. Its"
                    " OWN out-file — never a dev leg's, whose answered ids the resume would skip"
                ),
                "items": shot,
            }
        ],
        "sealed_source": {
            "pack": summary.rel(PROBE_PACK),
            "sha256": summary.sha256_of(PROBE_PACK),
            "items": len(probe["items"]),
            "identity_and_order": "unchanged — asserted id by id, in order",
            "rule": (
                "the sealed pack, the sealed base verdict and the gold are READ and never written."
                " The base is not re-run on the fourteen: its answers are the ones"
                " results/pass1_probe_b_verdict.json already holds"
            ),
        },
        "balance": balance(shot),
        "contamination": contamination(shot),
        "length": ceiling_check(shot),
    }
    return dev, shot_pack


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    dev, shot = build()
    written = {}
    for name, record in ((DEV_NAME, dev), (SHOT_NAME, shot)):
        record["producer"] = {
            "script": summary.rel(Path(__file__)),
            "sha256": summary.sha256_of(Path(__file__)),
            "borrowed": {
                one: summary.sha256_of(REPO_ROOT / one)
                for one in (
                    "scripts/build_pass1_sft.py",
                    "scripts/window_summary_5c2.py",
                    "src/market_pulse/prompts.py",
                )
            },
        }
        path = args.outdir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        path.write_text(payload, encoding="utf-8")
        written[name] = sha_text(payload)
        print(f"wrote {name}  sha256 {written[name][:16]}…")

    print(
        f"  dev: {dev['population']['rows']} rows ({dev['population']['our_rows']} «our») ×"
        f" 2 legs = {sum(len(leg['items']) for leg in dev['legs'])} items · seed {SEED}"
    )
    print(f"       distribution {dev['population']['distribution']}")
    print(f"       top-up {dev['draw']['rest_allocation']} of {dev['draw']['rest_population']}")
    print(
        f"       paired: same rows {dev['paired']['same_rows']} · same context {dev['paired']['same_context']}"
    )
    print(
        f"       holdout overlap {dev['holdout']['dev_rows_that_are_holdout_rows']} of 200 — declared"
    )
    print(
        f"  shot: {len(shot['legs'][0]['items'])} units, order unchanged from {summary.rel(PROBE_PACK)}"
    )
    for name, record in (("dev", dev), ("shot", shot)):
        block, con = record["length"], record["contamination"]
        print(
            f"  {name} length: widest {block['widest_request_chars']} chars"
            f" ({block['widest_request']}) · median {block['median_chars']} · headroom"
            f" {block['headroom_chars']} of {block['ceiling_chars']}"
        )
        print(
            f"  {name} contamination: gold ids {len(con['neighbour_ids_in_the_gold_14'])} ·"
            f" gold threads {len(con['neighbour_threads_in_the_gold_threads'])} ·"
            f" eval ids {len(con['neighbour_ids_in_the_eval_pack_64'])} ·"
            f" eval threads {len(con['neighbour_threads_in_the_eval_pack_threads'])} ·"
            f" own-thread {len(con['items_shown_a_neighbour_from_their_own_thread'])}"
        )
        print(f"  {name} balance: {record['balance']['label_totals']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
