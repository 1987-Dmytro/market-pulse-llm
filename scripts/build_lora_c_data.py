#!/usr/bin/env python3
"""`results/pass1_sft_v3_train.jsonl` + `results/lora_c_data.json` — the shared pool and arm A's rows.

`docs/PROMPT-lora-c-prep.md` D0. The population is the 650 team-lead labels MINUS holdout-100 MINUS
every row of the 16 reference threads, and the SAME set is both the training set and the neighbour
pool: base v2, base v3, arm A and arm B are all rendered against it, so the paired table compares
prompts and adapters and never neighbours.

**Nothing here is re-implemented.** `build_pass1_sft.labelled_units` is the join (it already refuses
a label with no unit, an exam thread and a gold msg_id), `build_pass1_sft.holdout_units` is the
holdout, `build_pass1_fewshot_packs.neighbours` is the Jaccard rule, `build_pass1_sft.request`
builds the transport fields, and `build_pass1_sft.target_for` decides the supervised boundary. What
this file adds is the v3 rendering, the rationale join and the census
([[a_fact_is_the_rule_when_the_law_keys_on_it]]).

**The SFT prompt IS the v3 inference request, byte for byte.** One function renders both, and a test
drives THIS builder and re-renders every row through `pass1_v3.pass1_messages_gm4_v3` from the
fields it kept, comparing the string and not only its sha
([[build_the_training_prompt_with_the_inference_call]]).

The shipped row keeps `examples_chosen` — the five `(thread, msg_id, label, similarity)` the pack
convention records — and NOT the five example texts: those are already inside `prompt`, and a second
copy is 1.5 MB of the same bytes with nothing holding the two together.

    PYTHONPATH=src python3.11 scripts/build_lora_c_data.py
    PYTHONPATH=src python3.11 scripts/build_lora_c_data.py --sample   # review gate 1's file
"""

import argparse
import hashlib
import json
import math
import random
import re
import sys

import yaml
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_pass1_fewshot_packs as fewshot  # noqa: E402
import build_pass1_label_pack as labelpack  # noqa: E402
import build_pass1_sft as sft  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402
import train_qlora as trainer  # noqa: E402
from market_pulse import brands, pass1_v3, prompts  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

GOLD = REPO_ROOT / "results" / "reader_gold_w1_r2.json"
RATIONALES = REPO_ROOT / "results" / "rationales_pass1_v1.jsonl"
TRAIN_OUT = REPO_ROOT / "results" / "pass1_sft_v3_train.jsonl"
RECORD_OUT = REPO_ROOT / "results" / "lora_c_data.json"
SAMPLE_OUT = REPO_ROOT / "docs" / "reviews" / "lora-c-rationales-sample.md"
VERDICT = REPO_ROOT / "docs" / "reviews" / "lora-c-rationales-verdict.md"
WATCHLIST_RULES = REPO_ROOT / "config" / "watchlist_rules.yaml"

OUR = ("категория_личное", "молочный_бренд")
BOUNDARY_SEED = 20260822
BOUNDARY_TARGET = 40
PROBE_RATIO_MIN = 0.269618
PROBE_RATIO_MEDIAN = 0.282802
"""The minimum and the median of the same 64 paid probe-b rows `build_pass1_sft.ratio()` takes its
maximum from. Carried so the STOP above can be stated at the ratio most FAVOURABLE to the run and
not only at the conservative one — a ceiling that only binds under the pessimistic bound would be a
weaker finding than this one is."""

MIN_PER_EPOCH = 8
SAMPLER_EPOCHS = 60
"""How many epochs the sampler is driven for to MEASURE its draw. Sixty is enough that the four
class means sit within 1 % of the analytic N/4 and cheap enough to run on every build."""
"""The contract's floor: no class may draw fewer than this per epoch-equivalent."""

MAX_SEQ_LEN = int(
    yaml.safe_load((REPO_ROOT / "config" / "qlora.yaml").read_text(encoding="utf-8"))["training"][
        "max_seq_len"
    ]
)
"""`config/qlora.yaml` `training.max_seq_len`, FROZEN law — READ and never typed, so the token
table and the trainer's own refusal cannot part ([[a_moved_constant_fails_green]])."""


def norm(text: str) -> str:
    """Whitespace-collapsed, case-folded — the form every cue is checked against.

    The comments carry doubled internal spaces and newlines: nine of the 515 cues are phrases a
    human can point at in the comment and are not raw substrings of it, differing by one space.
    A check that compared raw bytes would be checking the store's whitespace, not the rationale
    ([[verbatim_quotes_must_be_grepped]] answered on the axis it is actually about).
    """
    return " ".join(text.split()).casefold()


sha_text = sft.sha_text
"""One implementation, called: a second spelling of a hash is a second answer."""


def reference_threads() -> list[str]:
    """The 16 threads of `docs/REFERENCE-signals-w1.md`, DERIVED from the sealed gold.

    flagships + entity_cases + noise_threads, keyed `channel:post_id`. E4a/E4b are two threads and
    one case, so the 5 + 5 + 6 rows resolve to 16 distinct threads.
    """
    gold = json.loads(GOLD.read_text(encoding="utf-8"))
    return sorted(
        {
            f"{one['channel']}:{one['post_id']}"
            for key in ("flagships", "entity_cases", "noise_threads")
            for one in gold[key]
        }
    )


def shared_pool() -> tuple[list[dict], dict]:
    """The 515 rows every leg is rendered against, and the census of what was removed.

    The two exclusions OVERLAP — six holdout rows sit inside reference threads — so the count is
    `650 − 100 − 41 + 6`, not `650 − 100 − 41`. Stated as the arithmetic rather than as a number,
    because the contract expects ~430 and the measurement is 515
    ([[a_count_in_prose_is_not_the_enumeration]]).
    """
    reference = set(reference_threads())
    holdout = sft.holdout_units()
    everything = [{**one, "grams": fewshot.grams(one["text"])} for one in sft.labelled_units()]
    in_reference = [one for one in everything if one["thread"] in reference]
    kept = [
        one
        for one in everything
        if one["thread"] not in reference and (one["thread"], one["msg_id"]) not in holdout
    ]
    kept.sort(key=lambda one: (one["thread"], one["msg_id"]))
    census = {
        "labels": len(everything),
        "holdout_rows": len(holdout),
        "reference_threads": sorted(reference),
        "reference_threads_carrying_labelled_rows": sorted({one["thread"] for one in in_reference}),
        "reference_rows": len(in_reference),
        "holdout_rows_inside_reference_threads": len(
            [key for key in holdout if key[0] in reference]
        ),
        "pool": len(kept),
        "arithmetic": (
            f"{len(everything)} − {len(holdout)} − {len(in_reference)}"
            f" + {len([key for key in holdout if key[0] in reference])} = {len(kept)}"
            " — the two exclusions overlap and the overlap is added back once"
        ),
        "distribution": dict(
            sorted(Counter(fewshot.key(one["subject_type"]) for one in kept).items())
        ),
        "our_rows": len([one for one in kept if one["subject_type"] in OUR]),
        "our_share": round(
            100 * len([one for one in kept if one["subject_type"] in OUR]) / len(kept), 2
        ),
    }
    return kept, census


def rationales() -> dict[tuple[str, int], dict]:
    """The hand-written rationale of every pool row, keyed on the PAIR and refusing a duplicate.

    Seven msg_ids of this window live in two threads each, so a dict keyed on the id alone would be
    last-wins and one thread's rationale would silently answer for another's
    ([[select_one_row_refuse_ambiguity]], [[id_spaces_that_look_comparable]]).
    """
    rows: dict[tuple[str, int], dict] = {}
    for number, line in enumerate(RATIONALES.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        one = json.loads(line)
        key = (one["thread"], int(one["msg_id"]))
        if key in rows:
            raise SystemExit(
                f"{RATIONALES.name} line {number}: {key} appears twice. A rationale file keyed on"
                " the pair may not carry two answers for one comment — stop."
            )
        rows[key] = one
    return rows


def joined(pool: list[dict]) -> list[dict]:
    """Every pool row with its rationale, held to the label and the text the JOIN produced.

    The rationale file carries `subject_type` and `text` of its own, and both are CHECKED rather
    than trusted: a label that drifted from the team lead's file would otherwise train a row under
    a reading nobody wrote ([[correcting_gold_moves_the_denominator]]).
    """
    written = rationales()
    out = []
    for unit in pool:
        key = (unit["thread"], unit["msg_id"])
        one = written.get(key)
        if one is None:
            raise SystemExit(f"{key} is in the pool and has no rationale — stop rather than train.")
        if one["subject_type"] != unit["subject_type"]:
            raise SystemExit(
                f"{key}: the rationale file says {one['subject_type']!r} and the team lead's label"
                f" is {unit['subject_type']!r}. Stop."
            )
        if norm(one["text"]) != norm(unit["text"]):
            raise SystemExit(f"{key}: the rationale file's text is not the store's — stop.")
        if norm(one["cue"]) not in norm(unit["text"]):
            raise SystemExit(
                f"{key}: the cue {one['cue']!r} does not occur in the comment. A rationale whose"
                " cue is not in the text was written from the LABEL, which is the failure this"
                " line exists to avoid — stop."
            )
        if f"(cue: «{one['cue']}»)" not in one["rationale"]:
            raise SystemExit(f"{key}: the rationale does not quote its own cue — stop.")
        if len(one["rationale"]) > pass1_v3.RATIONALE_MAX_CHARS:
            raise SystemExit(
                f"{key}: the rationale is {len(one['rationale'])} characters against the"
                f" registered {pass1_v3.RATIONALE_MAX_CHARS} — stop."
            )
        out.append({**unit, "rationale": one["rationale"], "cue": one["cue"]})
    return out


def examples_for(unit: dict, pool: list[dict], by_key: dict) -> tuple[list[dict], list[dict]]:
    """The five neighbours of one query, each carrying ITS OWN rationale.

    `fewshot.neighbours` is CALLED — same Jaccard over character 3-grams, same total tie key, same
    «never the query's own thread» rule — and the rationale is looked up afterwards, so the choice
    of neighbour is decided by exactly the instrument the window was measured with.
    """
    chosen = fewshot.neighbours(unit["thread"], unit["grams"], pool)
    shown = []
    for one in chosen:
        source = by_key[(one["thread"], one["msg_id"])]
        shown.append({"text": one["text"], "label": one["label"], "rationale": source["rationale"]})
    return chosen, shown


def render_v3(fields: dict, examples: list[dict]) -> str:
    """The v3 request for one comment — the string the pod sends and the string the row trains on."""
    return pass1_v3.pass1_messages_gm4_v3(
        fields["channel"],
        fields["post_id"],
        fields["topic"],
        fields["entities"],
        fields["msg_id"],
        fields["text"],
        examples=examples,
    )[0]["content"]


def target_v3(msg_id: int, subject_type: str | None, rationale: str) -> tuple[str, int]:
    """v1's target with the rationale written FIRST, and the supervised boundary moved with it.

    `build_pass1_sft.target_for` is CALLED, not copied: it owns the +1 END-offset rule that carries
    the boundary one character past the `subject_type` value's closing quote, and
    `train_qlora.load_sft` re-derives that same boundary from the label. Prefixing the rationale
    shifts every offset of the head by `len(prefix) - 1` (the head's own `{` is replaced), so the
    supervised span is the rationale AND the label — which is the whole point of the line: the loss
    lands on the reasoning before it lands on the class.
    """
    head, learn = sft.target_for(msg_id, subject_type)
    prefix = '{"rationale": ' + json.dumps(rationale, ensure_ascii=False) + ", "
    target = prefix + head[1:]
    return target, len(prefix) - 1 + learn


def sampler(rows: list[dict]) -> dict:
    """lora-b's weighting rule, INHERITED by call, plus the per-class draws it implies.

    `train_qlora.class_weights` is `w_c = N/(5·n_c)` capped at 8.0 and it is the same function the
    trainer samples with. The contract asks for a SECOND rule — «cap the majority class by sampling
    so no class is under 8 rows per epoch-equivalent» — and the arithmetic says the first rule
    already delivers it: expected draws per class are `n_c · w_c = min(N/5, 8·n_c)`, so the majority
    class is capped at a fifth of the epoch by construction and the floor binds only on a class
    under 8 rows. Reported as the table rather than applied as a second knob, because a second
    sampler nobody needs is a second answer the day one of them is edited.
    """
    weights = trainer.class_weights(rows)
    counts = Counter(fewshot.key(one["subject_type"]) for one in rows)
    # DRIVEN, not multiplied. `sampling_order` calls `random.choices`, which NORMALISES the weight
    # vector — so `n_c · w_c` is only the expected draw when the weights sum to the row count, and
    # here they sum to 404.8 against 506 because the rule `w_c = N/(5·n_c)` expects FIVE classes and
    # the rendered set has four (молочный_бренд has zero rows). The product under-reports by 25 %
    # ([[a_borrowed_rule_carries_an_unstated_population]])
    per_row = [weights[fewshot.key(one["subject_type"])] for one in rows]
    seen: Counter = Counter()
    for epoch in range(SAMPLER_EPOCHS):
        for index in trainer.sampling_order(len(rows), per_row, 42 + epoch):
            seen[fewshot.key(rows[index]["subject_type"])] += 1
    draws = {name: round(seen[name] / SAMPLER_EPOCHS, 2) for name in sorted(weights)}
    product = {name: round(counts[name] * weight, 2) for name, weight in sorted(weights.items())}
    return {
        "rule": (
            f"w_c = N/({trainer.PASS1_K}·n_c) capped at {trainer.PASS1_WEIGHT_CAP} —"
            " results/prereg_lora_b.json's arms.*.sampler_weights, by calling"
            " train_qlora.class_weights, the function the trainer samples with"
        ),
        "second_rule": (
            f"«no class under {MIN_PER_EPOCH} rows per epoch-equivalent». Expected draws are"
            " n_c·w_c = min(N/5, 8·n_c), so the majority class is capped at N/5 by the first rule"
            " and the floor can only bind on a class with fewer than 8 rows. APPLIED: none — the"
            " first rule already satisfies it, and the smallest class lands exactly on the floor"
        ),
        "weights": weights,
        "rows_per_class": dict(sorted(counts.items())),
        "draws_per_epoch_MEASURED": draws,
        "draws_rule": (
            f"the sampler itself, driven over {SAMPLER_EPOCHS} epochs of the real rows."
            " train_qlora.sampling_order calls random.choices, which NORMALISES the weights, so the"
            " naive product n_c·w_c is NOT the expected draw here"
        ),
        "the_naive_product_and_why_it_is_wrong": {
            "value": product,
            "weights_sum_to": round(sum(product.values()), 2),
            "against_row_count": len(rows),
            "why": (
                "w_c = N/(5·n_c) is written for FIVE classes; the rendered set has FOUR because"
                " молочный_бренд has zero rows, so the vector sums to 404.8 of 506 and"
                " normalisation scales every class up by 506/404.8 = 1.25. The product under-reports"
                " the real draw by 25 %, and one section of this record naming that missing class"
                " beside another publishing a number that assumes it is exactly the shape this"
                " contract keeps finding"
            ),
        },
        "the_majority_cap_is_N_over_4_not_N_over_5": (
            "with four classes in the sampler the cap lands at N/4 = 126.5, not N/5 = 101.2"
        ),
        "floor": MIN_PER_EPOCH,
        "classes_under_the_floor": sorted(
            name for name, value in draws.items() if value < MIN_PER_EPOCH
        ),
        "classes_under_the_floor_rule": (
            "measured draws, not the product — and the class that WOULD have landed on the floor"
            " (молочный_бренд, one pool row) is absent from this table entirely because it has zero"
            " rendered rows. The floor binds on nothing here, and not because every class clears it"
        ),
    }


def unreachable(pool: list[dict]) -> dict:
    """The queries `fewshot.neighbours` CANNOT serve, and why — this contract's STOP.

    The pool holds exactly ONE `молочный_бренд` row: the 650 hold two, and the holdout took the
    other. `neighbours` refuses a query whose own thread is the only place a class occurs, because
    a four-example block is a different instrument from a five-example one. So every row of that
    one thread is unrenderable under v3 AND under v2 on this pool — nine training rows and two
    eval rows — and the cause is the exclusion the ruling itself demands.
    """
    smallest = [one for one in pool if one["subject_type"] == "молочный_бренд"]
    threads = {one["thread"] for one in smallest}
    blocked = sorted(
        (one["thread"], one["msg_id"], fewshot.key(one["subject_type"]))
        for one in pool
        if one["thread"] in threads
    )
    return {
        "cause": (
            "build_pass1_fewshot_packs.neighbours raises when a class has no candidate outside the"
            " query's own thread. The shared pool holds ONE молочный_бренд row and the exclusion"
            " that removed the other is holdout-100, which the ruling puts out of the pool"
        ),
        "smallest_class": "молочный_бренд",
        "rows_in_the_pool": len(smallest),
        "rows_in_the_650": 2,
        "the_other_one": "@mandziak:3721:48445 — a holdout row",
        "threads": sorted(threads),
        "blocked_pool_rows": blocked,
        "blocked_pool_rows_n": len(blocked),
        "remedies_named_none_taken": [
            "render those rows with FOUR examples — neighbours() itself says a four-example block"
            " is a different instrument, so the arm would be two instruments",
            "allow the query's own thread as a candidate for that class alone — a per-class rule,"
            " and for the молочный_бренд row itself it would hand the model its own answer",
            "draw the example from the EXCLUDED set — and for THIS class it is not a disjunction:"
            " the only other молочный_бренд row is @mandziak:3721:48445, a HOLDOUT row whose thread"
            " is not among the 16, so the remedy is necessarily «show a holdout comment WITH ITS"
            " GOLD LABEL inside every request of the run that scores the holdout-100 bar»",
            "drop the eleven rows — arm A then has ZERO real молочный_бренд positives and the"
            " holdout denominator moves off the registered 100, taking the ≥64 bar with it",
        ],
        "ruling": "the operator's — this file renders what it can and names the rest",
    }


def build() -> dict:
    pool, census = shared_pool()
    rows = joined(pool)
    by_key = {(one["thread"], one["msg_id"]): one for one in rows}
    blocked = unreachable(pool)
    blocked_keys = {(thread, msg_id) for thread, msg_id, _ in blocked["blocked_pool_rows"]}
    context = sft.verdicts()
    limit = sft.envelope(context)["limit"]
    trained, refused = [], []
    for unit in rows:
        key = (unit["thread"], unit["msg_id"])
        if key in blocked_keys:
            refused.append(
                {"id": f"{unit['thread']}#{unit['msg_id']}", "why": "no fifth neighbour"}
            )
            continue
        chosen, examples = examples_for(unit, pool, by_key)
        built = sft.request(unit, context, limit)
        fields = built["fields"]
        prompt = render_v3(fields, examples)
        target, learn_chars = target_v3(unit["msg_id"], unit["subject_type"], unit["rationale"])
        trained.append(
            {
                "id": f"{unit['thread']}#{unit['msg_id']}",
                "thread": unit["thread"],
                "msg_id": unit["msg_id"],
                "pack": unit["pack"],
                "subject_type": unit["subject_type"],
                "rationale": unit["rationale"],
                "cue": unit["cue"],
                "task": pass1_v3.PASS1_TASK_V3,
                "prompt": prompt,
                "target": target,
                "learn_chars": learn_chars,
                "fields": fields,
                "examples": examples,
                "examples_chosen": [
                    {
                        "thread": one["thread"],
                        "msg_id": one["msg_id"],
                        "label": fewshot.key(one["label"]),
                        "similarity": one["similarity"],
                    }
                    for one in chosen
                ],
                "rendering_sha256": sha_text(prompt),
                "context": {
                    "topic_from": built["topic_source"],
                    "entities": len(fields["entities"]),
                    "verdict": built["verdict_source"],
                },
            }
        )
    widest = max(trained, key=lambda one: len(one["prompt"]))
    return {
        "phase": "lora-c-prep",
        "contract": "docs/PROMPT-lora-c-prep.md D0",
        "authority": "docs/STATUS.md «Открытые решения» п. 1 (в) and (к), 2026-08-22",
        "population": census,
        "pool_is_the_training_set": (
            "one pool for every leg: base v2, base v3, arm A and arm B are rendered against the"
            " same 515 rows, so the paired table compares prompts and adapters, never neighbours"
        ),
        "rows": {
            "rendered": len(trained),
            "refused": refused,
            "distribution": dict(
                sorted(Counter(fewshot.key(one["subject_type"]) for one in trained).items())
            ),
            "our_rows": len([one for one in trained if one["subject_type"] in OUR]),
        },
        "unreachable": blocked,
        "sampler": sampler(trained),
        "rationales": {
            "file": "results/rationales_pass1_v1.jsonl",
            "sha256": hashlib.sha256(RATIONALES.read_bytes()).hexdigest(),
            "author": "claude-code",
            "reviewed": sorted({one["rationale_reviewed"] for one in rationales().values()}),
            "n": len(rationales()),
            "codebook": (
                "scripts/build_pass1_label_pack.py::codebook() — the labeller's own text, law v5 +"
                " the F2a carve-out + the gold r2 adjudication"
            ),
            "codebook_sha256": sha_text(labelpack.codebook()),
            "cue_rule": (
                "every rationale names a cue that occurs in ITS OWN comment, compared on"
                " whitespace-collapsed case-folded text. A rationale derivable from the label alone"
                " is the label wearing a sentence, and the target would still be a deterministic"
                " function of the class — line B's failure in a new costume"
            ),
            "distinct": {
                "rationales": len({one["rationale"] for one in rows}),
                "cues": len({one["cue"] for one in rows}),
                "per_class": {
                    name: {
                        "rows": len(group),
                        "distinct_rationales": len({one["rationale"] for one in group}),
                        "distinct_cues": len({one["cue"] for one in group}),
                    }
                    for name, group in sorted(
                        (
                            (
                                name,
                                [one for one in rows if fewshot.key(one["subject_type"]) == name],
                            )
                            for name in {fewshot.key(one["subject_type"]) for one in rows}
                        )
                    )
                },
            },
            "shapes": dict(
                sorted(
                    Counter(
                        "лише ЗГАДУЄ"
                        if one["rationale"].startswith("лише ЗГАДУЄ")
                        else "коментар ні про кого"
                        if one["rationale"].startswith("коментар ні про кого")
                        else "коментар ПРО"
                        for one in rows
                    ).items()
                )
            ),
        },
        "instruments": {
            "module": "src/market_pulse/pass1_v3.py",
            "module_sha256": sha_text(
                (REPO_ROOT / "src" / "market_pulse" / "pass1_v3.py").read_text(encoding="utf-8")
            ),
            "prompt_sha256": {
                pass1_v3.PASS1_TASK_V3: pass1_v3.prompt_sha256(pass1_v3.PASS1_TASK_V3),
                prompts.PASS1_TASK_V2: prompts.prompt_sha256(prompts.PASS1_TASK_V2),
                prompts.PASS1_TASK: prompts.prompt_sha256(prompts.PASS1_TASK),
            },
            "v3_extends_v2": pass1_v3.PASS1_COMMENT_PROMPT_V3.startswith(
                prompts.PASS1_COMMENT_PROMPT_V2
            ),
            "neighbours": "build_pass1_fewshot_packs.neighbours, CALLED",
            "target": "build_pass1_sft.target_for, CALLED — the +1 END-offset boundary",
            "renderer": (
                "src/market_pulse/pass1_v3.py::pass1_messages_gm4_v3 — a SIBLING renderer."
                " build_pass1_fewshot_packs.rendered_item cannot take v3:"
                " prompts.pass1_messages_gm4 raises `not a registered pass-1 prompt` for any task"
                " outside prompts.PASS1, and prompts.py is pinned by 38 records"
            ),
        },
        "length": {
            "ceiling_chars": prompts.PASS1_MAX_INPUT_CHARS,
            "widest_request": widest["id"],
            "widest_request_chars": len(widest["prompt"]),
            "headroom_chars": prompts.PASS1_MAX_INPUT_CHARS - len(widest["prompt"]),
            "median_chars": sorted(len(one["prompt"]) for one in trained)[len(trained) // 2],
        },
        "tokens": token_table(trained),
        "produced_by": {
            "script": "scripts/build_lora_c_data.py",
            "sha256": sha_text(Path(__file__).read_text(encoding="utf-8")),
        },
        "train_file": "results/pass1_sft_v3_train.jsonl",
        "rows_data": trained,
    }


def fewer_examples(trained: list[dict]) -> dict:
    """The same rows RE-RENDERED with fewer neighbours — computed here, never typed.

    The first version of this block carried `484` and `62` as literals under a `rule` that said
    «measured rather than argued». They were true and they had no producer, which is the same defect
    the remedy they support was written to correct ([[a_claim_no_number_can_check]]). Worse, «one
    example» has no meaning until the block says WHICH example survives: keeping the
    `молочный_бренд` neighbour leaves 62 rows over and keeping a different one leaves 87–125. So
    every drop-choice is enumerated and the rule is the label, not a position.
    """
    ratio = sft.ratio()["tokens_per_char_max"]
    labels = [fewshot.key(one["label"]) for one in trained[0]["examples"]]

    def over(rows: list[dict], per_char: float) -> int:
        return len(
            [one for one in rows if math.ceil(one * per_char) + sft.TEMPLATE_SLACK > MAX_SEQ_LEN]
        )

    def sizes_without(dropped: tuple[str, ...]) -> list[int]:
        out = []
        for one in trained:
            kept = [
                example
                for example in one["examples"]
                if fewshot.key(example["label"]) not in dropped
            ]
            out.append(len(render_v3(one["fields"], kept)) + len(one["target"]))
        return out

    table = {}
    for name, dropped in [("four_examples__drop_" + label, (label,)) for label in labels] + [
        ("one_example__keep_" + label, tuple(one for one in labels if one != label))
        for label in labels
    ]:
        rows = sizes_without(dropped)
        table[name] = {
            "over_at_the_min_ratio": over(rows, PROBE_RATIO_MIN),
            "over_at_the_registered_ratio": over(rows, ratio),
            "median_tokens_at_the_min_ratio": sorted(
                math.ceil(one * PROBE_RATIO_MIN) + sft.TEMPLATE_SLACK for one in rows
            )[len(rows) // 2],
            "of": len(rows),
        }
    return {
        "rule": (
            "every drop-choice re-rendered through pass1_v3.pass1_messages_gm4_v3 and bounded the"
            " same way. COMPUTED here — the remedy this supports is the sentence the operator would"
            " act on, and it may not rest on a literal"
        ),
        "the_choice_matters": (
            "«four examples» and «one example» are not single numbers. Dropping the smallest class's"
            " neighbour is the choice remedy 1 implies and it leaves the most rows over; keeping a"
            " different one moves the count by tens. Named per label rather than per position"
        ),
        "zero_examples_is_not_an_option": (
            "pass1_v3.pass1_messages_gm4_v3 refuses an empty block by name — v3 has no"
            " no-examples arm, so the floor of this table is ONE"
        ),
        "by_choice": table,
        "best_case_over": min(cell["over_at_the_min_ratio"] for cell in table.values()),
        "best_case_over_rule": (
            "the most favourable drop-choice at the most favourable measured ratio. Even there the"
            " count is not zero, which is what makes STOP 2 a property of the population and not of"
            " the block"
        ),
    }


def token_table(trained: list[dict]) -> dict:
    """Tokens per SFT row against `max_seq_len` — and this line's second STOP.

    `build_pass1_sft.ratio()` measured tokens-per-character on probe-b's own 64 paid rows: the
    pack's `rendered_chars` against the served `prompt_tokens`, which counts the chat template the
    pod wraps the request in. `train_qlora.encode_pass1` measures the SAME quantity — it tokenizes
    `apply_chat_template(...)` and refuses on `len(context) + len(target)` — so the pod's own count
    is this bound minus `build_pass1_sft.TEMPLATE_SLACK`, and the producer's drop rule and the pod's
    refusal are two readings of one number ([[drive_the_consumer_not_only_the_producer]]).

    **The reading: every v3 row is over the frozen ceiling, at every ratio the repo has measured.**
    Not a bound artefact — at the MINIMUM observed ratio the SHORTEST row still needs 1 419 tokens
    of the pod's own count against 1 408. The cause is size: v3's request is 5 262–9 402 characters
    where lora-b's v1 rows were 2 950 median and 4 132 max, because the five-neighbour block now
    carries a rationale per example on top of v2's two extra paragraphs. `config/qlora.yaml` is
    FROZEN law and pinned by `results/prereg_lora_b.json::instruments.config_sha256`, so this is a
    ruling and not an edit ([[compute_the_ceiling_first]]).
    """
    ratio = sft.ratio()
    sizes = sorted(len(one["prompt"]) + len(one["target"]) for one in trained)
    table = {}
    for name, per_char in (
        ("registered_bound_max", ratio["tokens_per_char_max"]),
        ("median_observed", PROBE_RATIO_MEDIAN),
        ("min_observed", PROBE_RATIO_MIN),
    ):
        bounds = sorted(math.ceil(size * per_char) + sft.TEMPLATE_SLACK for size in sizes)
        table[name] = {
            "tokens_per_char": per_char,
            "min": bounds[0],
            "median": bounds[len(bounds) // 2],
            "max": bounds[-1],
            "over_max_seq_len": len([one for one in bounds if one > MAX_SEQ_LEN]),
            "of": len(bounds),
            "pods_own_count_of_the_shortest": bounds[0] - sft.TEMPLATE_SLACK,
        }
    return {
        "rule": ratio["rule"],
        "measured_on": ratio["measured_on"],
        "observed_ratio_range": [PROBE_RATIO_MIN, PROBE_RATIO_MEDIAN, ratio["tokens_per_char_max"]],
        "max_seq_len": MAX_SEQ_LEN,
        "max_seq_len_source": "config/qlora.yaml training.max_seq_len — FROZEN law",
        "chars_prompt_plus_target": {
            "min": sizes[0],
            "median": sizes[len(sizes) // 2],
            "max": sizes[-1],
        },
        "lora_b_v1_rows_for_comparison": {
            "chars_median": 2950,
            "chars_max": 4132,
            "longest_kept_tokens": 1222,
            "source": "results/pass1_sft_arm_b.jsonl and results/prereg_lora_b.json"
            "::dropped_for_length.longest_kept",
        },
        "by_ratio": table,
        "verdict": (
            f"EVERY one of the {len(sizes)} rows is over max_seq_len {MAX_SEQ_LEN} at all three"
            " measured ratios. build_pass1_sft's own drop rule (bound > max_seq_len) would drop the"
            " whole dataset, and train_qlora.encode_pass1 would refuse every row on the pod. This"
            " is the contract's STOP and it returns to the operator"
        ),
        "the_text_and_the_block_BOTH_matter": {
            "v3_prompt_chars": len(pass1_v3.PASS1_COMMENT_PROMPT_V3),
            "v2_prompt_chars": len(prompts.PASS1_COMMENT_PROMPT_V2),
            "v3_prompt_tokens_at_the_worst_ratio": math.ceil(
                len(pass1_v3.PASS1_COMMENT_PROMPT_V3) * ratio["tokens_per_char_max"]
            ),
            "v3_prompt_tokens_at_the_min_ratio": math.ceil(
                len(pass1_v3.PASS1_COMMENT_PROMPT_V3) * PROBE_RATIO_MIN
            ),
            "share_of_max_seq_len": (
                "the prompt TEXT alone occupies 79–85 % of the ceiling — 1 109 to 1 200 tokens of"
                " 1 408 — before a single neighbour, the topic, the entity block, the comment or"
                " the target. That leaves 208–299 tokens for all of them together"
            ),
            "the_dichotomy_is_FALSE_and_this_is_the_correction": (
                "an earlier version of this record said «the cause is the TEXT, not the block». The"
                " record's own table refutes it: the MEDIAN row exceeds the ceiling by 159 tokens"
                " and the five-example block is worth ~223 median tokens, so the block weighs more"
                " than the median row's excess and at ONE example the median row FITS. What is"
                " true is narrower and still closes the STOP: no LEGAL neighbour count makes ALL"
                " rows fit — the widest rows are over at every choice — and zero neighbours is"
                " refused by the renderer. The text is why the margin is thin; the tail is why no"
                " count is enough ([[co_occurrence_is_not_explanation]])"
            ),
        },
        "measured_at_other_neighbour_counts": fewer_examples(trained),
        "remedies_named_none_taken": [
            "raise config/qlora.yaml training.max_seq_len — FROZEN law, pinned by"
            " results/prereg_lora_b.json::instruments.config_sha256 and by lora-b's verdict; there"
            " is precedent (1024 → 1408 by operator decision of 2026-08-04) and it is the"
            " operator's word, never the executor's",
            "shrink the examples block — MEASURED, and it does NOT close this STOP. With FOUR"
            " examples (the smallest class's dropped) 484 of 506 rows are still over at the most"
            " favourable measured ratio and 506 of 506 at the registered one; with ONE example 62"
            " rows are still over. It DOES dissolve the молочный_бренд blockage above, but that is"
            " a SCOPED change to nine rows of one thread and this would be a global one — two"
            " decisions, not one ([[a_claim_no_number_can_check]])",
            "drop the rationale from the neighbour examples — the model then never sees the shape"
            " it is asked to produce, which is the clause's own reason for existing",
            "drop rows over the limit — that is all 506",
        ],
    }


WINDOW_REPLIES = (
    REPO_ROOT / "results" / "pass1_window_v2.jsonl",
    REPO_ROOT / "results" / "pass1_window_r2_v2.jsonl",
)
"""Pass 1's own answers over the paid window. All 506 rendered rows are in there, so `subject_id` —
«the subject's name as the comment writes it» — is available for every one of them at $0."""

NAMED_SUBJECTS = ("сеть_ритейлер", "молочный_бренд")
"""The two readings that mean «pass 1 saw a retailer or a dairy brand here»."""


def window_answers() -> dict[str, dict]:
    """`id -> parsed reply` over the window's two out-files, by the PINNED parser.

    `prompts.parse_pass1` is strict and is called with the row's own `msg_id`, so a reply that
    echoed another comment's id is refused rather than joined to the wrong row.
    """
    out: dict[str, dict] = {}
    for path in WINDOW_REPLIES:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                one = json.loads(line)
                out[one["id"]] = one
    return out


def word_in(needle: str, haystack: str) -> bool:
    """Word-bounded, whitespace-collapsed, casefolded — `brands.find_watchlist_brands`'s own rule.

    Bounded rather than a bare substring test for that function's stated reason: `Ферма` would
    otherwise be read out of `фермерське`, and a boundary sample built on free false positives is a
    sample of the matcher rather than of the population.
    """
    return bool(re.search(rf"(?<!\w){re.escape(norm(needle))}(?!\w)", norm(haystack)))


def mentions(text: str, aliases, rules, answers: dict, row_id: str, msg_id: int) -> tuple | None:
    """Whether this comment NAMES something, and at which tier — two instruments, both shipped.

    **Tier A — a retailer or a brand.** `brands.find_watchlist_brands` over the sealed watchlist
    with the ruled revision and `carrier="comment"` (SPEC 3.21 (1) scopes one of its rules to
    comment text, so the carrier is stated); failing that, pass 1's OWN answer for this row, when it
    read `сеть_ритейлер` or `молочный_бренд` AND the `subject_id` it wrote occurs in the comment.
    The occurrence check is what keeps this a MENTION test: without it a hallucinated name would
    select a row that never carried one.

    **Tier B — a name of any other kind**, by the same rule with the reading unrestricted.

    Why pass 1's answer is in a selection instrument at all: the shipped registry-and-watchlist
    matchers find **zero** retailer or brand mentions across all 466 non-«our» rows, because the
    comments write «Варус», «варусі», «Варусу» and the registry spells that source `Varus` in Latin
    — a spelling no registry, watchlist or lexicon file in this repo carries in Cyrillic. A cell
    that came back empty under one instrument is a reading about the instrument
    ([[run_the_instrument_on_the_named_example]]), so the second one is named beside it rather than
    substituted for it.
    """
    found = brands.find_watchlist_brands(text, aliases, rules, carrier="comment")
    if found:
        return ("A", f"watchlist: `{found[0]['brand_id']}`")
    reply = answers.get(row_id)
    if reply is None:
        return None
    try:
        parsed = prompts.parse_pass1(reply["reply"], msg_id=msg_id)
    except prompts.ParseError:
        return None
    name = parsed["subject_id"]
    if not name or not word_in(name, text):
        return None
    tier = "A" if parsed["subject_type"] in NAMED_SUBJECTS else "B"
    return (tier, f"pass 1 read `{fewshot.key(parsed['subject_type'])}` — «{name}»")


def boundary_rows(record: dict) -> tuple[list[dict], dict]:
    """The 40 rows review gate 1 sees beside every «our» row, drawn under a recorded seed.

    Over `не_наш_рынок` / `сеть_ритейлер` / `null` rows whose text NAMES something — the cell where
    a name is present and the reading is not that name, which is the whole of the four error
    classes `docs/reports/pass2-signals-r2.md` returned. **Tier A is taken whole** (it is smaller
    than the target and every row in it is the target cell itself); tier B is sampled under
    :data:`BOUNDARY_SEED` to make up the 40.
    """
    loaded = load_registry(REPO_ROOT / "config" / "registry.yaml")
    aliases = brands.watchlist_aliases(loaded.watchlist)
    rules = brands.load_watchlist_rules(WATCHLIST_RULES)
    answers = window_answers()
    tiers: dict[str, list[dict]] = {"A": [], "B": []}
    for one in record["rows_data"]:
        if one["subject_type"] in OUR:
            continue
        hit = mentions(one["fields"]["text"], aliases, rules, answers, one["id"], one["msg_id"])
        if hit:
            tiers[hit[0]].append({**one, "mention": hit[1], "tier": hit[0]})
    for group in tiers.values():
        group.sort(key=lambda one: (one["thread"], one["msg_id"]))
    stream = random.Random(BOUNDARY_SEED)
    want = max(0, BOUNDARY_TARGET - len(tiers["A"]))
    drawn = tiers["B"] if len(tiers["B"]) <= want else stream.sample(tiers["B"], want)
    rows = sorted(tiers["A"] + drawn, key=lambda one: (one["tier"], one["thread"], one["msg_id"]))
    census = {
        "seed": BOUNDARY_SEED,
        "target": BOUNDARY_TARGET,
        "tier_a_rule": (
            "brands.find_watchlist_brands over the sealed watchlist (ruled revision,"
            " carrier=comment), else pass 1's own window answer read сеть_ритейлер or"
            " молочный_бренд with a subject_id that occurs in the comment"
        ),
        "tier_a_found": len(tiers["A"]),
        "tier_a_taken": len(tiers["A"]),
        "tier_b_rule": "the same, with pass 1's reading unrestricted — a name of any other kind",
        "tier_b_found": len(tiers["B"]),
        "tier_b_drawn": len(drawn),
        "watchlist_matcher_hits": 0
        if not any(one["mention"].startswith("watchlist") for one in rows)
        else len([one for one in rows if one["mention"].startswith("watchlist")]),
        "the_matcher_reading": (
            "the shipped registry-and-watchlist matchers find ZERO retailer or brand mentions in"
            " the 466 non-«our» rows. config/registry.yaml spells the chain `Varus` in Latin and"
            " the comments write «Варус» / «варусі» / «Варусу»; running the registry names through"
            " the lexicon's own stem+endings screen (yield_screen.compile_categories) reaches"
            " «Сільпо» and «АТБ» and still not «варусі». No file in this repo carries the Cyrillic"
            " spelling of that source"
        ),
        "total": len(rows),
    }
    return rows, census


def sample(record: dict) -> tuple[str, dict]:
    """`docs/reviews/lora-c-rationales-sample.md` — every «our» row and 40 boundary rows."""
    ours = [one for one in record["rows_data"] if one["subject_type"] in OUR]
    boundary, census = boundary_rows(record)
    tier_a = [one for one in boundary if one["tier"] == "A"]
    tier_b = [one for one in boundary if one["tier"] == "B"]
    lines = [
        "# lora-c — review gate 1: the rationales",
        "",
        "**This file is the EXECUTOR's. The verdict is the team lead's:"
        " `docs/reviews/lora-c-rationales-verdict.md`.**",
        "",
        "Written by Claude Code from the codebook"
        f" (`scripts/build_pass1_label_pack.py::codebook()`, sha256"
        f" `{record['rationales']['codebook_sha256'][:16]}…`) and the team lead's label."
        f" All {record['rationales']['n']} rows carry `rationale_reviewed: false` until the verdict"
        " lands.",
        "",
        "**What to write in the verdict:** the rows to rewrite and THE PATTERN behind each. Only"
        " the named rows and every other row matching a named pattern are rewritten; nothing else"
        " moves, and the counts go into `docs/reports/lora-c-prep.md`.",
        "",
        "**The rule each rationale was written under.** One Ukrainian sentence, ≤ 160 characters,"
        " naming a cue that occurs in the comment's own text, in one of two shapes —"
        " «коментар ПРО X (cue: …)» or «лише ЗГАДУЄ X; насправді про Y (cue: …)»; a third,"
        " «коментар ні про кого», is the `null` reading of the first. A rationale derivable from"
        " the label alone would make the target a deterministic function of the class, which is"
        " what line B already measured. Every cue below was checked back into its own comment"
        " before this file was written.",
        "",
        f"- **«our» rows: {len(ours)}** (категория_личное + молочный_бренд) — every one of them,"
        " no sampling.",
        f"- **boundary rows: {len(boundary)}**, seed `{BOUNDARY_SEED}`, in two tiers:",
        f"  - **tier A — {len(tier_a)}, taken WHOLE**: the comment names a retailer or a dairy"
        " brand. Instrument: `brands.find_watchlist_brands` over the sealed watchlist (ruled"
        ' revision, `carrier="comment"`), else pass 1\'s own window answer where it read'
        " `сеть_ритейлер` / `молочный_бренд` **and** the `subject_id` it wrote occurs in the"
        " comment.",
        f"  - **tier B — {len(tier_b)} of {census['tier_b_found']} drawn under the seed**: the same"
        " rule with pass 1's reading unrestricted — the comment names something else.",
        "",
        "> **Why pass 1's own answer is in the selection.** The shipped registry-and-watchlist"
        " matchers find **zero** retailer or brand mentions across all 466 non-«our» rows."
        " `config/registry.yaml` spells the chain `Varus` in Latin; the comments write «Варус»,"
        " «варусі», «Варусу». Running the registry names through the lexicon's own stem+endings"
        " screen reaches «Сільпо» and «АТБ» and still not «варусі» — no file in this repo carries"
        " the Cyrillic spelling of that source. Tier A is therefore named by two instruments, not"
        " one, and the count each contributed is above.",
        "",
    ]
    for title, group, extra in (
        ("Every «our» row", ours, False),
        (f"Boundary rows — tier A (all {len(tier_a)})", tier_a, True),
        (
            f"Boundary rows — tier B ({len(tier_b)} of {census['tier_b_found']}, seed"
            f" {BOUNDARY_SEED})",
            tier_b,
            True,
        ),
    ):
        lines += [
            f"## {title}",
            "",
            "| # | pair | label | comment | rationale | verdict |",
            "|---|---|---|---|---|---|",
        ]
        for number, one in enumerate(group, start=1):
            text = " ".join(one["fields"]["text"].split()).replace("|", "\\|")
            text = text if len(text) <= 240 else text[:237] + "…"
            label = fewshot.key(one["subject_type"])
            if extra:
                label = f"{label}<br>*names:* {one['mention']}"
            lines.append(
                f"| {number} | `{one['thread']}`<br>`{one['msg_id']}` | {label} | {text} |"
                f" {one['rationale'].replace('|', chr(92) + '|')} |  |"
            )
        lines.append("")
    return "\n".join(lines) + "\n", census


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", action="store_true", help="also write review gate 1's file")
    parser.add_argument("--train-out", type=Path, default=TRAIN_OUT)
    parser.add_argument("--record-out", type=Path, default=RECORD_OUT)
    parser.add_argument("--sample-out", type=Path, default=SAMPLE_OUT)
    args = parser.parse_args(argv)

    record = build()
    rows = record.pop("rows_data")
    args.train_out.write_text(
        "".join(
            json.dumps(
                {key: one[key] for key in one if key not in ("fields", "examples")},
                ensure_ascii=False,
                sort_keys=True,
            )
            + "\n"
            for one in rows
        ),
        encoding="utf-8",
    )
    record["train_sha256"] = hashlib.sha256(args.train_out.read_bytes()).hexdigest()
    args.record_out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    census = record["population"]
    print(f"wrote {summary.rel(args.train_out)}  {len(rows)} rows")
    print(f"wrote {summary.rel(args.record_out)}")
    print(f"  pool {census['arithmetic']}")
    print(f"  distribution {record['rows']['distribution']}  our {record['rows']['our_rows']}")
    print(f"  refused for want of a fifth neighbour: {len(record['rows']['refused'])}")
    print(
        f"  widest request {record['length']['widest_request_chars']} chars"
        f" (headroom {record['length']['headroom_chars']})"
    )
    if args.sample:
        record["rows_data"] = rows
        args.sample_out.parent.mkdir(parents=True, exist_ok=True)
        text, boundary_census = sample(record)
        record.pop("rows_data")
        args.sample_out.write_text(text, encoding="utf-8")
        stored = json.loads(args.record_out.read_text(encoding="utf-8"))
        stored["review_gate_1"] = {
            "sample": "docs/reviews/lora-c-rationales-sample.md",
            "verdict": "docs/reviews/lora-c-rationales-verdict.md",
            "verdict_present": VERDICT.exists(),
            "our_rows": len([one for one in rows if one["subject_type"] in OUR]),
            "boundary": boundary_census,
        }
        args.record_out.write_text(
            json.dumps(stored, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {summary.rel(args.sample_out)}")
        print(
            f"  REVIEW GATE 1 — STOP until {summary.rel(VERDICT)} exists"
            f" ({'present' if VERDICT.exists() else 'ABSENT'})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
