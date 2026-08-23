#!/usr/bin/env python3
"""`results/lora_c_eval_pack.json` — eval set E, rendered under v2 AND v3 against the shared pool.

`docs/PROMPT-lora-c-prep.md` D0. E is holdout-100 plus every payable comment of the 16 reference
threads. The two sets OVERLAP by six rows — six holdout rows sit inside reference threads — so E is
a UNION and its size is `100 + 106 − 6 = 200`, not 206 ([[a_count_in_prose_is_not_the_enumeration]]).

**Two legs, one pack, paired on identical instances**, the way `results/pass1_dev_pack.json` carries
`base` and `v2`: the same item is rendered twice, once per prompt family, and the pack records both
`rendering_sha256`. Nothing here is bought — `lora-c-run` sends this file.

**The neighbours come from the SHARED pool of 515 and not from the 650.** That is the whole point of
the pool rule: base v2, base v3, arm A and arm B are answered against one neighbour set, so the
paired table compares prompts and adapters and never neighbours. It keeps every E row's own ID out
of its own examples — the pool excludes holdout and reference-thread rows by construction — but
**not its own TEXT**: see :func:`own_text_in_examples`, which counts 22 of 198 and 5 of the 98 rows
the gating bar is scored on.

**The fourteen are inside E and take no bar.** They are answered as part of the reference threads and
scored as a REPORT-ONLY census row — the SIXTH look at the sealed gold. `docs/STATUS.md` п. 1 (д):
«14 золотых в окне — строка ценза с множественностью, НИКОГДА не бар».

    PYTHONPATH=src python3.11 scripts/build_lora_c_eval_pack.py
"""

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_lora_c_data as data  # noqa: E402
import build_pass1_fewshot_packs as fewshot  # noqa: E402
import build_pass1_label_pack_r2 as r2pack  # noqa: E402
import build_pass1_sft as sft  # noqa: E402
import gate_census_w1_reader as reader_gate  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402
from market_pulse import pass1_v3, prompts  # noqa: E402

OUT = REPO_ROOT / "results" / "lora_c_eval_pack.json"
PROBE_PACK = REPO_ROOT / "results" / "pass1_probe_b_pack.json"
DEV_PACK = REPO_ROOT / "results" / "pass1_dev_pack.json"

LEGS = {"v2": "lora_c_eval_v2.jsonl", "v3": "lora_c_eval_v3.jsonl"}


def leg_of(pack: dict, name: str) -> dict:
    """One named leg of a pack whose `legs` is a LIST.

    A list and not a dict because every pack in this repo carries one — `pass1_dev_pack.json`, the
    window packs, the pass-2 packs — and every pod runner reaches for `pack["legs"][0]` or unpacks
    it positionally. A dict here would be a shape only this file knows, and `lora-c-run`'s runner
    would be the thing that discovered it ([[a_fixture_on_disk_pins_yesterdays_schema]]).
    """
    return next(one for one in pack["legs"] if one["name"] == name)


def texts() -> dict[tuple[str, int], str]:
    """The comment text of every E row, from the file that owns each half.

    Reference-thread rows come from `gate_census_w1_reader.population()`, whose comments already
    carry the cell's own `text`; holdout rows come from `build_pass1_sft.labelled_units()`, which
    reads them through `window_summary_5c2.comment_text` — the same reader the label packs used. Two
    sources because E is a union of two populations, and taking both from one of them would be a
    second spelling of a text somebody already read ([[a_fixture_on_disk_pins_yesterdays_schema]]).
    """
    reference = set(data.reference_threads())
    out = {
        (f"{thread['channel']}:{thread['post_id']}", int(one["msg_id"])): one["text"]
        for thread in reader_gate.population()
        if f"{thread['channel']}:{thread['post_id']}" in reference
        for one in thread["comments"]
    }
    for one in sft.labelled_units():
        out.setdefault((one["thread"], one["msg_id"]), one["text"])
    return out


def payable_of_reference() -> list[tuple[str, int]]:
    """Every payable comment of the 16 reference threads, from `gate_census_w1_reader.population()`.

    Called and not re-derived: that function is the cell's own enumeration and it asserts itself
    against the census record before it returns.
    """
    reference = set(data.reference_threads())
    out = []
    for thread in reader_gate.population():
        name = f"{thread['channel']}:{thread['post_id']}"
        if name in reference:
            out += [(name, int(one["msg_id"])) for one in thread["comments"]]
    return sorted(out)


def eval_pairs() -> tuple[list[tuple[str, int]], dict]:
    """E, and the census of how it was made."""
    holdout = sft.holdout_units()
    reference = payable_of_reference()
    union = sorted(set(holdout) | set(reference))
    overlap = sorted(set(holdout) & set(reference))
    return union, {
        "rule": (
            "holdout-100 ∪ every payable comment of the 16 reference threads. **dev-200 is NOT a"
            " CRITERION of E and it is not disjoint from it either**: 80 of its 200 rows land in E"
            " because they are holdout or reference-thread rows, 115 land in the training set and 5"
            " in the refused thread. An earlier version of this field said «dev-200 is NOT in E»"
            " while the same document's membership.dev_200_in_e listed those 80"
            " ([[a_count_in_prose_is_not_the_enumeration]])"
        ),
        "holdout": len(holdout),
        "reference_payable": len(reference),
        "overlap": len(overlap),
        "overlap_rows": [f"{thread}:{msg_id}" for thread, msg_id in overlap],
        "arithmetic": f"{len(holdout)} + {len(reference)} − {len(overlap)} = {len(union)}",
        "e": len(union),
    }


def render_pair(fields: dict, chosen: list[dict], by_key: dict) -> dict:
    """One instance under BOTH prompt families, from one set of fields and one set of neighbours."""
    v2 = fewshot.rendered_item(fields, prompts.PASS1_TASK_V2, chosen)
    examples = [
        {
            "text": one["text"],
            "label": one["label"],
            "rationale": by_key[(one["thread"], one["msg_id"])]["rationale"],
        }
        for one in chosen
    ]
    content = pass1_v3.pass1_messages_gm4_v3(
        fields["channel"],
        fields["post_id"],
        fields["topic"],
        fields["entities"],
        fields["msg_id"],
        fields["text"],
        examples=examples,
    )[0]["content"]
    return {
        "v2": v2,
        "v3": {
            **fields,
            "task": pass1_v3.PASS1_TASK_V3,
            "rendered_chars": len(content),
            "rendering_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            "examples": examples,
            "examples_chosen": v2["examples_chosen"],
        },
    }


def own_text_in_examples(items: list[dict], holdout: set) -> dict:
    """E rows shown a BYTE-IDENTICAL copy of their own comment, labelled, inside their own block.

    **This is a real leak and it lands on the gating bar.** The own-thread rule blocks
    `pick["thread"] == one["thread"]` and nothing else, while `fewshot.neighbours` picks on maximum
    Jaccard over character 3-grams — an identical string scores exactly 1.0, so where the window
    reposts a comment verbatim across threads the duplicate is not merely eligible, it is chosen
    FIRST, deterministically. The window is full of spam and boilerplate reposted word for word,
    which is why this has volume.

    It is neutral to arm-vs-base and to the A/B ablation — `render_pair` builds both legs from ONE
    `chosen` and the adapter is a runner flag, so every leg sees the same contaminated block — and
    it is NOT neutral to the absolute reading `P1_holdout_agreement ≥ 64 of 100` stands on.

    **CLOSED by amendment 3.25 (2)** (operator, 2026-08-23), which gave the neighbour rule its one
    refusal: a candidate whose whitespace-collapsed casefolded text equals the query's. This block
    stays, and it stays a MEASUREMENT rather than a claim that the leak is gone — the count is
    recomputed over the rebuilt pack at every build, so a selection rule that ever stopped refusing
    would show up here as a number and not as a missing guard
    ([[a_prefilter_cannot_certify_the_population]] answered: the filter does not certify the
    population, this scan of the population does).
    """
    hits = []
    for one in items:
        for example in one["examples"]:
            if data.norm(example["text"]) == data.norm(one["text"]):
                hits.append(
                    {
                        "id": one["id"],
                        "thread": one["thread"],
                        "msg_id": one["msg_id"],
                        "the_twins_label": fewshot.key(example["label"]),
                        "in_holdout_100": (one["thread"], one["msg_id"]) in holdout,
                    }
                )
                break
    gating = [one for one in hits if one["in_holdout_100"]]
    return {
        "what": (
            "the item is shown a byte-identical copy of its own comment, carrying a label, inside"
            " its own <examples> block"
        ),
        "mechanism": (
            "the own-thread rule blocks the query's THREAD, not its TEXT; neighbours() maximises"
            " Jaccard over character 3-grams and an identical string scores 1.0, so the duplicate is"
            " chosen first and deterministically wherever the window reposts a comment verbatim"
        ),
        "n": len(hits),
        "of": len(items),
        "on_the_gating_bar": len(gating),
        "gating_bar_denominator": 98,
        "severity": (
            f"{len(gating)} of the 98 rows the registered bar «holdout-100 agreement ≥ 64 of 100»"
            " is scored on are shown their own answer"
            + (
                ". That INFLATES the absolute reading the bar stands on. It is neutral to"
                " arm-vs-base and to the A/B ablation, because every leg is rendered from one"
                " `chosen`"
                if gating
                else " — the reading the bar stands on carries none of this leak"
            )
        ),
        "rows": hits,
        "remedy": {
            "rule": (
                "refuse a neighbour whose whitespace-collapsed casefolded text equals the query's."
                " Equality and nothing below it"
            ),
            "authority": "docs/SPEC.md amendment 3.25 (2), operator, 2026-08-23",
            "applied_by": "build_lora_c_data.neighbours_v3, as a pre-filter on the candidate pool",
            "measured_at_97548df": {
                "e_items": 22,
                "of": 198,
                "on_the_gating_bar": 5,
                "training_rows": 13,
                "of_training": 506,
            },
            "state": "CLOSED" if not hits else "OPEN — the refusal is not reaching this pack",
        },
    }


def build() -> dict:
    pool, census = data.shared_pool()
    # FIRST, because `data.joined` would otherwise refuse a synthetic row for want of a rationale
    # and the isolation guard below could never fire. A guard placed after a stricter one is a
    # guard nobody can see ([[an_empty_class_is_the_definitions_answer]])
    reached = sorted({one["thread"] for one in pool if one["thread"].startswith("synthetic:")})
    if reached:
        raise SystemExit(f"synthetic threads reached the neighbour pool: {reached}. Stop.")
    joined = data.joined(pool)
    by_key = {(one["thread"], one["msg_id"]): one for one in joined}
    pairs, made = eval_pairs()
    store = r2pack.raw_threads()
    text_of = texts()
    context = sft.verdicts()
    limit = sft.envelope(context)["limit"]
    gold = set(r2pack.gold_msg_ids())
    dev = {
        (one["thread"], int(one["msg_id"]))
        for leg in json.loads(DEV_PACK.read_text(encoding="utf-8"))["legs"]
        for one in leg["items"]
    }
    probe = {
        (one["thread"], int(one["msg_id"]))
        for one in json.loads(PROBE_PACK.read_text(encoding="utf-8"))["items"]
    }
    holdout = sft.holdout_units()
    reference = set(data.reference_threads())

    items: dict[str, list[dict]] = {"v2": [], "v3": []}
    refused = []
    for thread, msg_id in pairs:
        held = store.get(thread)
        if held is None:
            raise SystemExit(f"{thread} is in E and not in the store — stop.")
        text = text_of.get((thread, msg_id))
        if not text:
            raise SystemExit(
                f"{thread}:{msg_id} is in E and neither source carries its text — stop."
            )
        unit = {"thread": thread, "msg_id": msg_id, "text": text, "store": held}
        built = sft.request(unit, context, limit)
        try:
            chosen = data.neighbours_v3(thread, text, fewshot.grams(text), pool)
        except SystemExit:
            refused.append(
                {
                    "id": f"{thread}#{msg_id}",
                    "why": "no fifth neighbour — see results/lora_c_data.json::unreachable",
                }
            )
            continue
        both = render_pair(built["fields"], chosen, by_key)
        membership = {
            "gold_14": msg_id in gold,
            "holdout_100": (thread, msg_id) in holdout,
            "reference_thread": thread in reference,
            "dev_200": (thread, msg_id) in dev,
            "probe_64": (thread, msg_id) in probe,
        }
        for leg, one in both.items():
            items[leg].append(
                {**one, "membership": membership, "topic_source": built["topic_source"]}
            )

    if [one["id"] for one in items["v2"]] != [one["id"] for one in items["v3"]]:
        raise SystemExit(
            "the two legs do not carry the same instances in the same order. The table is PAIRED —"
            " a leg that answers a different set is a different measurement. Stop."
        )
    # INVARIANT ASSERTION, not a guard: v3's text is v2's plus a whole paragraph, so two renderings
    # of one item cannot collide. Kept because it is the property the paired table RESTS on and it
    # costs one comparison — but it has never fired and cannot, and saying so is the difference
    # between a guard and an assertion ([[an_empty_class_is_the_definitions_answer]])
    if any(
        one["rendering_sha256"] == other["rendering_sha256"]
        for one, other in zip(items["v2"], items["v3"])
    ):
        raise SystemExit(
            "an item renders identically under v2 and v3, so the two legs would be one"
            " measurement wearing two names. Stop."
        )
    own = [
        one["id"]
        for one in items["v2"]
        for chosen in [one["examples_chosen"]]
        if any(pick["thread"] == one["thread"] for pick in chosen)
    ]
    if own:
        raise SystemExit(f"{len(own)} items are shown a neighbour from their own thread — stop.")
    # the pool-isolation guard used to be repeated here as well. It was a word-for-word DUPLICATE of
    # the one at the top of this function and it was DEAD: nothing between the two mutates `pool`,
    # so the first copy always fires first. Moving a guard and leaving the old copy behind is how a
    # file grows a check nobody can ever see run ([[an_empty_class_is_the_definitions_answer]])
    # INVARIANT ASSERTION and NOT a guard, unlike its twin above the rationale join: E is built from
    # `sft.holdout_units()` ∪ `payable_of_reference()` and neither enumeration can yield a
    # `synthetic:` thread, so this cannot fire as the pack stands. It becomes a real guard the day E
    # draws from anything else — which is exactly when someone would need it
    synthetic_in_e = sorted(
        one["id"] for one in items["v2"] if one["thread"].startswith("synthetic:")
    )
    if synthetic_in_e:
        raise SystemExit(f"synthetic rows reached E: {synthetic_in_e}. Stop.")

    probe_pack = json.loads(PROBE_PACK.read_text(encoding="utf-8"))
    return {
        "phase": "lora-c-prep",
        "contract": "docs/PROMPT-lora-c-prep.md D0 — eval packs",
        "what_this_is": (
            "eval set E under two prompt families, built at $0 and BOUGHT by lora-c-run. Four legs"
            " of that run read this one pack: base v2 and base v3 with no adapter, arm A and arm B"
            " with one — the adapter is a runner flag, not a rendering"
        ),
        "made": made,
        "pool": {
            "rows": census["pool"],
            "arithmetic": census["arithmetic"],
            "rule": "the SHARED pool — one neighbour set for every leg of every arm",
            "record": "results/lora_c_data.json",
        },
        "legs": [
            {
                "name": name,
                "task": items[name][0]["task"],
                "out": LEGS[name],
                "items": items[name],
                "n": len(items[name]),
            }
            for name in ("v2", "v3")
        ],
        "refused": refused,
        "own_text_in_examples": own_text_in_examples(items["v3"], holdout),
        "membership": {
            "gold_14": sorted(one["id"] for one in items["v2"] if one["membership"]["gold_14"]),
            "gold_14_rule": (
                "REPORT-ONLY, the SIXTH look. docs/STATUS.md п. 1 (д): a census row with"
                " multiplicity, NEVER a bar. They are answered because they are inside the"
                " reference threads, not because anything scores them"
            ),
            "holdout_100": len([one for one in items["v2"] if one["membership"]["holdout_100"]]),
            "reference_thread": len(
                [one for one in items["v2"] if one["membership"]["reference_thread"]]
            ),
            "dev_200_in_e": sorted(
                one["id"] for one in items["v2"] if one["membership"]["dev_200"]
            ),
            "dev_200_rule": (
                "dev-200 is SPLIT, and the split is what decides which reading a row gives. 115 of"
                " its 200 are in the training set and their agreement is training FIT; 80 are in E"
                " and their agreement is a legitimate EVAL reading; 5 are in the refused thread and"
                " give neither. Of dev's 49 «our» rows only 40 are in train — 8 are in E and not in"
                " train, so «its «our» rows ARE the training set's «our» rows» was false and the"
                " blanket «may never be quoted as an eval reading» forbade a reading that is valid"
            ),
            "dev_200_split": {"in_train": 115, "in_E": 80, "in_neither": 5, "of": 200},
        },
        "instruments": {
            **fewshot.instruments(),
            "prompt_sha256": {
                prompts.PASS1_TASK_V2: prompts.prompt_sha256(prompts.PASS1_TASK_V2),
                pass1_v3.PASS1_TASK_V3: pass1_v3.prompt_sha256(pass1_v3.PASS1_TASK_V3),
            },
            "module_v3": "src/market_pulse/pass1_v3.py",
            "module_v3_sha256": data.sha_text(
                (REPO_ROOT / "src" / "market_pulse" / "pass1_v3.py").read_text(encoding="utf-8")
            ),
            "rationales_sha256": hashlib.sha256(data.RATIONALES.read_bytes()).hexdigest(),
        },
        "serving": probe_pack["serving"],
        "reading": probe_pack["reading"],
        "length": {
            name: {
                "widest": max(one["rendered_chars"] for one in items[name]),
                "median": sorted(one["rendered_chars"] for one in items[name])[
                    len(items[name]) // 2
                ],
                "ceiling": prompts.PASS1_MAX_INPUT_CHARS,
                "headroom": prompts.PASS1_MAX_INPUT_CHARS
                - max(one["rendered_chars"] for one in items[name]),
            }
            for name in ("v2", "v3")
        },
        "calls": {
            "per_leg": len(items["v2"]),
            "legs_bought_by_lora_c_run": 4,
            "rule": (
                "base v2 reads the v2 leg; base v3, arm A and arm B read the v3 leg. Four readings"
                " of a 198-item pack — the money block of results/prereg_lora_c.json prices it as a"
                " formula and registers no number"
            ),
        },
        "produced_by": {
            "script": "scripts/build_lora_c_eval_pack.py",
            "sha256": data.sha_text(Path(__file__).read_text(encoding="utf-8")),
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
    print(
        f"wrote {summary.rel(args.out)}  sha256"
        f" {hashlib.sha256(args.out.read_bytes()).hexdigest()[:16]}…"
    )
    print(f"  E: {record['made']['arithmetic']}")
    print(f"  rendered {leg_of(record, 'v2')['n']} per leg · refused {len(record['refused'])}")
    for name in ("v2", "v3"):
        cell = record["length"][name]
        print(f"  {name}: widest {cell['widest']} chars, headroom {cell['headroom']}")
    counts = Counter(
        "gold_14" if one["membership"]["gold_14"] else "other"
        for one in leg_of(record, "v2")["items"]
    )
    print(f"  gold-14 inside E: {counts['gold_14']} — REPORT-ONLY, the sixth look")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
