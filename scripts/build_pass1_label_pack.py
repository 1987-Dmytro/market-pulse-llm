#!/usr/bin/env python3
"""The labelling pack of line B — 500 units drawn from the reader cell under a recorded seed.

**What this builds.** The sitting of 2026-08-18 ruled line B and put the labelling in the TEAM
LEAD's hands ([[sitting-b-line-b-and-the-team-lead-labels]]). This producer draws what they label
and renders it for a human: `docs/label-pack-pass1-r1.md` (the pack), its 40-unit blind subset, and
`results/pass1_label_pack_r1.json` (the machine record). It trains nothing, spends nothing and
makes no cloud call.

**The population is the reader cell MINUS the exam.** `narrow|varto_off|plus_spam+scam` is 129
threads and 1 032 payable comments, re-derived here by calling
`gate_census_w1_reader.population()` — which holds its own enumeration to the census on BOTH
numbers. Removed from it: every thread carrying any of the 64 registered units of
`results/pass1_probe_b_pack.json`, which is 7 threads and exactly 64 payable comments, because
those 64 ARE the payable set of those threads. The honesty frame's contamination clause is scoped
to the 14 gold rows and their threads; this is strictly larger and it is the one the pack is built
under. 1 032 − 64 = **968** remain, and the target is `min(500, 968)` = **500**.

**The draw is stratified by thread and capped, and the cap is derived rather than picked.** Weight
`w = min(payable, CAP)` with `CAP = 14`, the 90th percentile of the remaining threads' payable
counts — :func:`assert_cap_is_the_derivation` recomputes it and refuses if the population ever
moves. 500 units are allocated by largest remainder over `w` and drawn from each thread's msg-id
order under one seeded stream. Two properties are asserted rather than hoped for: no thread is
allocated more than its own weight (so the cap holds), and `sum(w) = 572 >= 500` (so the target is
REACHABLE — at `CAP = 9` it is not, which is what makes the check worth running).

**Everything is deterministic from :data:`SEED`.** No clock, no set iteration, no output path in
the record: `--outdir` writes the same three files elsewhere for the pair check, and what the
record names is always the registered relative path.

    PYTHONPATH=src python3.11 scripts/build_pass1_label_pack.py
    PYTHONPATH=src python3.11 scripts/build_pass1_label_pack.py --outdir /tmp/again   # the pair
"""

import argparse
import hashlib
import json
import math
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gate_census_w1 as census  # noqa: E402
import gate_census_w1_reader as cell  # noqa: E402
import reader_population as reader  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import loop, prompts  # noqa: E402

PROBE_PACK = REPO_ROOT / "results" / "pass1_probe_b_pack.json"
GOLD_R2 = REPO_ROOT / "results" / "reader_gold_w1_r2.json"

PACK_NAME = "results/pass1_label_pack_r1.json"
RENDER_NAME = "docs/label-pack-pass1-r1.md"
BLIND_NAME = "docs/label-pack-pass1-r1-blind40.md"

SEED = 20260818
"""The date of the sitting that ruled line B, and the only source of randomness here.

Fixed as a module constant and not a flag on purpose: a `--seed` option is an option to produce a
different pack, and the pack is the thing every later contract joins against. The draw below was
run once under this value and never re-rolled."""

TARGET = 500
"""`min(500, payable remaining)`. 500 is precedent-sized against the intents pass's 508 rows and it
is the sitting's «~500»; the `min` is what makes it a formula rather than a wish, and it is
evaluated against the measured remainder in :func:`build`."""

CAP = 14
"""The per-thread ceiling: the 90th percentile of the remaining threads' payable counts.

DERIVED, and re-derived at every run by :func:`assert_cap_is_the_derivation`. A cap exists because
this population has three threads of 105, 108 and 125 payable comments against a median of 3 —
proportional allocation with no cap would put 65 units (13% of the pack) in one thread and 175 in
the top three. At 14 the largest thread takes 12 of 500 (2.4%)."""

BLIND = 40
"""The unlabelled control subset the operator MAY label later. Nothing depends on whether they do."""

SUBJECT_TYPES = prompts.PASS1_SUBJECT_TYPES
"""The four readings, from the module the pass-1 prompt itself answers in. Never retyped here."""


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def thread_id(one: dict) -> str:
    return f"{one['channel']}:{one['post_id']}"


def excluded_threads() -> list[str]:
    """Every thread carrying any of the 64 registered probe units — DERIVED from the pack's items.

    Not copied from the contract's list: a list in prose cannot be joined against, and the whole
    point of the exclusion is that it is provable ([[count_in_prose_is_not_the_enumeration]]).
    """
    pack = json.loads(summary.read_text_or_refuse(PROBE_PACK))
    return sorted({one["thread"] for one in pack["items"]})


def probe_units() -> list[tuple[str, int]]:
    pack = json.loads(summary.read_text_or_refuse(PROBE_PACK))
    return sorted((one["thread"], int(one["msg_id"])) for one in pack["items"])


def gold_msg_ids() -> list[int]:
    """The 14 rows the sealed bar is scored on. They may appear nowhere in this pack."""
    gold = json.loads(summary.read_text_or_refuse(GOLD_R2))
    return sorted(int(row["msg_id"]) for row in gold["per_comment"])


def remaining_population() -> list[dict]:
    """The reader cell, re-derived from its producer, minus the excluded threads."""
    excluded = set(excluded_threads())
    kept = cell.population()
    return sorted(
        (one for one in kept if thread_id(one) not in excluded),
        key=lambda one: (one["channel"], one["post_id"]),
    )


def percentile(values: list[int], q: float) -> int:
    ordered = sorted(values)
    return ordered[math.ceil(q * len(ordered)) - 1]


def assert_cap_is_the_derivation(sizes: list[int]) -> None:
    """Refuse unless :data:`CAP` still IS the 90th percentile it claims to be."""
    derived = percentile(sizes, 0.90)
    if derived != CAP:
        raise SystemExit(
            f"CAP is {CAP} and the 90th percentile of this population is {derived}. The constant"
            " claims to be a derivation and it has stopped being one — re-derive it, do not"
            " re-run this producer."
        )


def allocate(weights: dict[str, int], target: int) -> dict[str, int]:
    """`target` units over the threads by LARGEST REMAINDER on the capped weights.

    Largest remainder rather than a redistribute loop because it cannot exceed a weight here:
    `floor(target * w / W) + 1 <= w` for every `w >= 1` whenever `target < W`, and `W >= target`
    is asserted by the caller. The tie-break is `(-remainder, thread)` — a total key, so two runs
    cannot order two equal remainders differently ([[an_order_key_that_is_not_total]]).
    """
    total = sum(weights.values())
    if total < target:
        raise SystemExit(
            f"the capped weights sum to {total} and the target is {target}: at CAP={CAP} this"
            " population cannot fill the pack. Raise the cap or lower the target — do not let the"
            " draw come up short silently."
        )
    base = {name: target * weight // total for name, weight in weights.items()}
    short = target - sum(base.values())
    order = sorted(weights, key=lambda name: (-(target * weights[name] / total - base[name]), name))
    for name in order[:short]:
        base[name] += 1
    over = [name for name, count in base.items() if count > weights[name]]
    if over:
        raise SystemExit(f"the allocation exceeds its own cap on {len(over)} threads: {over[:3]}")
    return base


def draw(threads: list[dict], allocation: dict[str, int], rng: random.Random) -> list[dict]:
    """`allocation[thread]` msg-ids per thread, in thread order, off ONE seeded stream."""
    units = []
    for one in threads:
        name = thread_id(one)
        take = allocation[name]
        if not take:
            continue
        ids = sorted(int(row["msg_id"]) for row in one["comments"])
        for msg_id in sorted(rng.sample(ids, take)):
            units.append({"thread": name, "msg_id": msg_id})
    return units


def raw_threads() -> dict[str, dict]:
    """Every thread of the window as the store holds it — silenced and text-less comments included.

    The rendering shows the FULL thread and `cell.population()` carries only the payable comments,
    which are what is DRAWN. Two different lists on purpose: the labeller reads a conversation, and
    a conversation with a third of its turns deleted is not the one the comment was written into.
    """
    return {thread_id(one): one for one in reader.window()}


def comment_state(row: dict) -> str:
    if census.silenced_comment(row, cell.SILENCERS):
        return "silenced"
    if not loop.has_text(summary.comment_text(row)):
        return "text-less"
    return "payable"


def quote(text: str) -> str:
    """A comment as a blockquote — multi-line text stays inside one block."""
    lines = (text or "").splitlines() or [""]
    return "\n".join(f"> {line}" if line else ">" for line in lines)


def r2_ruling() -> dict:
    """The gold-r2 adjudication, quoted from the record — WITHOUT the sentence that names a gold row.

    `revision.ruling.reading` ends by naming msg 21599, its gold value and the bar it moved. That is
    exam material and the honesty frame's first point forbids showing it to the labeller, so the
    quote stops at the rule and the elision is declared rather than silent.
    """
    revision = json.loads(summary.read_text_or_refuse(GOLD_R2))["revision"]
    marker = ", and probe-b measured"
    head, _, tail = revision["ruling"]["reading"].partition(marker)
    if not tail:
        raise SystemExit(
            "the r2 ruling's `reading` no longer carries the sentence this elision cuts at."
            f" Re-read {summary.rel(GOLD_R2)} and decide what the labeller may see."
        )
    return {
        "operator_words": list(revision["ruling"]["operator_words"]),
        "which": revision["ruling"]["which"],
        "change": revision["change"],
        "rule": head + ".",
        "elided": (
            "the rest of `revision.ruling.reading` names a gold msg_id, its gold value and the bar"
            " it moved. It is exam material and the labeller does not see it"
        ),
    }


def codebook() -> str:
    """The header every rendering carries — the law by the same bytes, and its sources named."""
    law = prompts.READER_ATTRIBUTION_LAW_V5
    carve = prompts.READER_CARRY_V5
    ruling = r2_ruling()
    values = " · ".join(f"`{one}`" for one in SUBJECT_TYPES)
    lines = [
        "## Codebook",
        "",
        "You are labelling ONE field, `subject_type`, on the comments marked **TARGET** below."
        " Nothing else is asked: `stance` reads 3 of 3 already and is not this pack's business.",
        "",
        "### The four readings, and the null",
        "",
        f"{values} — and JSON `null`.",
        "",
        "`null` is an ANSWER and not a skip: it says «this comment is about nobody». The pass-1"
        " prompt spells it «or null where the comment is about nobody», and the instrument's own"
        " abstentions are exactly what line B exists to fix — so a comment you would have left"
        " blank is a comment that needs `null` written down.",
        "",
        "«категория» is NOT one of the four. It is the reference's word for the same class as"
        " `категория_личное` and only the second is offered here.",
        "",
        "### ATTRIBUTION — the law, by the same bytes",
        "",
        "> Source: `src/market_pulse/prompts.py` :: `READER_ATTRIBUTION_LAW_V5`, sha256"
        f" `{sha_text(law)[:16]}…` — the same string the pass-1 prompt carries by reference, so a"
        " label and an answer are decided by one law and not by two wordings of it.",
        "",
        "```",
        law.strip(),
        "```",
        "",
        "The three examples are SYNTHETIC and proven to occur in no stored comment, no post and no"
        " gold file (`tests/test_reader_prompt_v5.py`).",
        "",
        "### The F2a carve-out — by the same bytes",
        "",
        "> Source: `src/market_pulse/prompts.py` :: `READER_CARRY_V5`, sha256"
        f" `{sha_text(carve)[:16]}…`",
        "",
        "```",
        carve.strip(),
        "```",
        "",
        "### The gold r2 adjudication",
        "",
        f"> Source: `results/reader_gold_w1_r2.json` :: `revision` — {ruling['which']}.",
        "",
        *[f"- «{word}»" for word in ruling["operator_words"]],
        "",
        f"**The rule.** {ruling['rule']}",
        "",
        f"**What r2 changed.** {ruling['change']}",
        "",
        f"*(Elided: {ruling['elided']}.)*",
        "",
        "### How to write the labels",
        "",
        "One JSON object per line into `docs/labels-pass1-r1.jsonl`, one line per TARGET:",
        "",
        "```",
        '{"thread": "@example:1", "msg_id": 999999, "subject_type": "категория_личное"}',
        "```",
        "",
        "`subject_type` is one of the four strings above or JSON `null`. Every TARGET is answered"
        " exactly once and nothing else is answered."
        f" `PYTHONPATH=src python3.11 scripts/validate_pass1_labels.py docs/labels-pass1-r1.jsonl`"
        " refuses anything else and writes nothing. Every unit is also in"
        f" `{PACK_NAME}` in this order, if a skeleton is easier than typing.",
    ]
    return "\n".join(lines)


def render(units: list[dict], threads: dict[str, dict], title: str, lead: str) -> str:
    """The labeller's document: the codebook, then each thread in FULL with its targets marked."""
    targets: dict[str, set[int]] = {}
    for unit in units:
        targets.setdefault(unit["thread"], set()).add(unit["msg_id"])
    out = [f"# {title}", "", lead, "", codebook(), "", "## Threads", ""]
    for index, name in enumerate(sorted(targets), start=1):
        raw = threads[name]
        marked = targets[name]
        out += [
            f"### {index}. `{name}` — {len(marked)} target"
            f"{'s' if len(marked) != 1 else ''} among {len(raw['comments'])} comment"
            f"{'s' if len(raw['comments']) != 1 else ''}",
            "",
            "**POST**",
            "",
            quote(raw["post_text"]),
            "",
        ]
        for row in raw["comments"]:
            msg_id = int(row["msg_id"])
            state = comment_state(row)
            head = f"**`{msg_id}`**"
            if msg_id in marked:
                head += "  ⬛ **TARGET**"
            elif state != "payable":
                head += f"  *({state})*"
            text = summary.comment_text(row)
            out += [head, "", quote(text) if text else "> *(no text)*", ""]
    return "\n".join(out).rstrip() + "\n"


def largest_thread_share(
    population: list[dict],
    weights: dict[str, int],
    allocation: dict[str, int],
    sizes: list[int],
    target: int,
) -> dict:
    """What the cap did to the BIGGEST thread — the one it exists for, named by its own size.

    Keyed on the payable count and never on the allocation: thirteen threads share the top
    allocation of 12 and only one of them is the 125-comment thread the cap is about, so a block
    that picked the largest ALLOCATION would print one thread's name beside another's size
    ([[co_occurrence_is_not_explanation]]).
    """
    biggest = max(population, key=lambda one: (len(one["comments"]), thread_id(one)))
    name = thread_id(biggest)
    return {
        "thread": name,
        "payable": len(biggest["comments"]),
        "weight": weights[name],
        "allocated": allocation[name],
        "share_of_pack": round(allocation[name] / target, 4),
        "uncapped_would_be": round(len(biggest["comments"]) * target / sum(sizes)),
        "rule": (
            "the thread with the most payable comments, and what the draw gave it. Uncapped"
            " proportional allocation is the counterfactual beside it"
        ),
    }


def build() -> tuple[dict, str, str]:
    population = remaining_population()
    sizes = [len(one["comments"]) for one in population]
    assert_cap_is_the_derivation(sizes)

    cell_record = json.loads(summary.read_text_or_refuse(cell.OUT))
    in_cell = cell_record["measured"]["comments_payable"]
    excluded = excluded_threads()
    removed = in_cell - sum(sizes)
    target = min(TARGET, sum(sizes))

    weights = {thread_id(one): min(len(one["comments"]), CAP) for one in population}
    allocation = allocate(weights, target)
    rng = random.Random(SEED)
    units = draw(population, allocation, rng)
    blind = sorted(rng.sample(units, BLIND), key=lambda one: (one["thread"], one["msg_id"]))

    threads = raw_threads()
    rendering = render(
        units,
        threads,
        "Label pack — pass 1, r1",
        f"**{len(units)} comments to label**, drawn from {sum(1 for v in allocation.values() if v)}"
        f" threads under seed `{SEED}`. Every thread is printed WHOLE — post first, then every"
        " comment in the store's own order, whether it is payable or not — and only the comments"
        " marked **TARGET** are labelled.",
    )
    blind_rendering = render(
        blind,
        threads,
        "Label pack — pass 1, r1 — blind 40",
        f"**{len(blind)} of the {len(units)} drawn comments**, under the same seed `{SEED}`,"
        " emitted UNLABELLED. It exists so a second reader can label the same units blind and the"
        " agreement can be measured; nothing depends on whether they do.",
    )

    gold = gold_msg_ids()
    drawn_ids = {unit["msg_id"] for unit in units}
    excluded_set = set(excluded)
    record = {
        "phase": "pass1-data-prep",
        "contract": "docs/PROMPT-pass1-data-prep.md D1",
        "authority": (
            "the sitting of 2026-08-18 (evening): line B, and the TEAM LEAD labels"
            " — knowledge/decisions/sitting-b-line-b-and-the-team-lead-labels.md, registered in"
            " docs/STATUS.md. Labels are TRAINING data and are ablated at training time; the"
            " judge does not move and the labeller never touches exam material"
        ),
        "labels": {
            "field": "subject_type",
            "values": [*SUBJECT_TYPES, None],
            "file": "docs/labels-pass1-r1.jsonl",
            "written_by": (
                "the TEAM LEAD. It is a team-lead file from the moment it exists: the executor"
                " validates it and commits it verbatim, and never writes a label into it"
            ),
            "validator": "scripts/validate_pass1_labels.py",
            "provenance_debt": (
                "labelled_by, date, codebook and this record's sha are frozen into results/ by the"
                " NEXT contract, after the labels exist and validate — not here"
            ),
        },
        "population": {
            "cell": cell.CELL,
            "record": summary.rel(cell.OUT),
            "sha256": summary.sha256_of(cell.OUT),
            "threads_in_cell": cell_record["measured"]["threads"],
            "payable_in_cell": in_cell,
            "threads_after_exclusion": len(population),
            "payable_after_exclusion": sum(sizes),
            "arithmetic": (
                f"{in_cell} payable in cell − {removed} payable in the {len(excluded)} excluded"
                f" threads = {sum(sizes)} remaining → min({TARGET}, {sum(sizes)}) = {target} drawn"
            ),
            "payable_per_thread": {
                "min": min(sizes),
                "median": percentile(sizes, 0.50),
                "p90": percentile(sizes, 0.90),
                "max": max(sizes),
            },
        },
        "exclusion": {
            "rule": (
                "every thread carrying ANY of the 64 registered units of"
                " results/pass1_probe_b_pack.json leaves the population WHOLE. The sitting's"
                " contamination clause names the 14 gold rows and their threads; this is strictly"
                " larger, and it is what the pack is built under"
            ),
            "threads": excluded,
            "probe_units": len(probe_units()),
            "payable_removed": removed,
            "the_units_are_the_payable_set": sorted(
                (name, msg_id) for name, msg_id in probe_units()
            )
            == sorted(
                (thread_id(one), int(row["msg_id"]))
                for one in cell.population()
                if thread_id(one) in excluded_set
                for row in one["comments"]
            ),
            "proof": {
                "drawn_units_sharing_a_thread_with_a_probe_unit": sorted(
                    unit["thread"] for unit in units if unit["thread"] in excluded_set
                ),
                "gold_msg_ids": gold,
                "gold_msg_ids_drawn": sorted(drawn_ids & set(gold)),
                "gold_msg_ids_in_the_remaining_population": sorted(
                    {int(row["msg_id"]) for one in population for row in one["comments"]}
                    & set(gold)
                ),
                "gold_msg_ids_rendered": sorted(
                    one for one in gold if f"`{one}`" in rendering or f"`{one}`" in blind_rendering
                ),
                "reading": (
                    "all four lists are empty in a correct pack. The last one is checked against"
                    " the RENDERED text and not against the unit list, because the rendering shows"
                    " every comment of a thread and not only the drawn ones"
                ),
            },
        },
        "draw": {
            "seed": SEED,
            "target_rule": f"min({TARGET}, payable remaining after the exclusion)",
            "target": target,
            "drawn": len(units),
            "cap": CAP,
            "cap_rule": (
                "the 90th percentile of the remaining threads' payable counts, re-derived at every"
                " run and refused if it moves"
            ),
            "formula": (
                "weight w = min(payable, CAP); allocate the target over the threads by LARGEST"
                " REMAINDER on w, tie-broken on (−remainder, thread); take that many msg_ids from"
                " the thread's msg-id-sorted payable list off one random.Random(SEED) stream"
            ),
            "reachability": {
                "capped_weight_sum": sum(weights.values()),
                "target": target,
                "reachable": sum(weights.values()) >= target,
                "reading": (
                    "the cap must leave the target REACHABLE or min(500, remaining) becomes a"
                    f" claim the draw cannot honour. At CAP={CAP} the ceiling is"
                    f" {sum(weights.values())}; at CAP=9 it is"
                    f" {sum(min(one, 9) for one in sizes)}, below the target"
                ),
            },
            "largest_thread_share": largest_thread_share(
                population, weights, allocation, sizes, target
            ),
            "per_thread": [
                {
                    "thread": thread_id(one),
                    "payable": len(one["comments"]),
                    "weight": weights[thread_id(one)],
                    "allocated": allocation[thread_id(one)],
                }
                for one in population
            ],
        },
        "blind": {
            "file": BLIND_NAME,
            "units": BLIND,
            "rule": (
                f"{BLIND} of the drawn units, sampled off the SAME seeded stream immediately after"
                " the draw. Emitted UNLABELLED so a second reader can label them blind; no contract"
                " depends on whether anyone does"
            ),
            "sha256": sha_text(blind_rendering),
        },
        "rendering": {
            "file": RENDER_NAME,
            "sha256": sha_text(rendering),
            "chars": len(rendering),
            "threads_rendered": sum(1 for one in allocation.values() if one),
            "threads_with_no_target": sorted(
                name for name, count in allocation.items() if not count
            ),
            "rule": (
                "each thread WHOLE — post first, then every comment in the store's own order,"
                " payable or not — with the drawn ones marked TARGET. Threads allocated no target"
                " are not rendered: the two listed above carry zero payable comments and cannot"
                " contribute one"
            ),
            "codebook": {
                "attribution_law": "src/market_pulse/prompts.py::READER_ATTRIBUTION_LAW_V5",
                "attribution_law_sha256": sha_text(prompts.READER_ATTRIBUTION_LAW_V5),
                "f2a_carve_out": "src/market_pulse/prompts.py::READER_CARRY_V5",
                "f2a_carve_out_sha256": sha_text(prompts.READER_CARRY_V5),
                "r2_adjudication": "results/reader_gold_w1_r2.json::revision",
                "quoted_by": (
                    "the same bytes, read from the module the pass-1 prompt itself answers under —"
                    " never retyped, so a label and an answer are decided by one law"
                ),
            },
        },
        "units": units,
        "blind_units": blind,
        "producer": {
            "script": summary.rel(Path(__file__)),
            "sha256": summary.sha256_of(Path(__file__)),
            "borrowed": {
                name: summary.sha256_of(REPO_ROOT / name)
                for name in (
                    "scripts/gate_census_w1_reader.py",
                    "scripts/gate_census_w1.py",
                    "scripts/reader_population.py",
                    "scripts/window_summary_5c2.py",
                    "src/market_pulse/prompts.py",
                    "src/market_pulse/loop.py",
                )
            },
        },
        "inputs": {
            summary.rel(path): summary.sha256_of(path) for path in (cell.OUT, PROBE_PACK, GOLD_R2)
        },
    }
    return record, rendering, blind_rendering


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--outdir",
        type=Path,
        default=REPO_ROOT,
        help="write the three files under this root instead of the repo (for the pair check)",
    )
    args = parser.parse_args(argv)
    record, rendering, blind_rendering = build()

    for name, text in (
        (RENDER_NAME, rendering),
        (BLIND_NAME, blind_rendering),
        (PACK_NAME, json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n"),
    ):
        path = args.outdir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {name}  sha256 {sha_text(text)[:16]}…  {len(text)} chars")

    pop = record["population"]
    draw_block = record["draw"]
    print(f"  {pop['arithmetic']}")
    print(
        f"  cell {pop['cell']}: {pop['threads_in_cell']} threads · {pop['payable_in_cell']} payable"
        f"  →  {pop['threads_after_exclusion']} threads · {pop['payable_after_exclusion']} payable"
    )
    print(
        f"  excluded {len(record['exclusion']['threads'])} threads carrying"
        f" {record['exclusion']['probe_units']} probe units"
        f" ({record['exclusion']['payable_removed']} payable removed);"
        f" the units ARE that payable set: {record['exclusion']['the_units_are_the_payable_set']}"
    )
    proof = record["exclusion"]["proof"]
    print(
        f"  contamination: drawn-in-excluded {len(proof['drawn_units_sharing_a_thread_with_a_probe_unit'])}"
        f" · gold drawn {len(proof['gold_msg_ids_drawn'])}"
        f" · gold in population {len(proof['gold_msg_ids_in_the_remaining_population'])}"
        f" · gold rendered {len(proof['gold_msg_ids_rendered'])}"
    )
    reach = draw_block["reachability"]
    print(
        f"  seed {draw_block['seed']} · cap {draw_block['cap']} (p90) ·"
        f" capped weights {reach['capped_weight_sum']} >= target {reach['target']}"
        f" — reachable {reach['reachable']}"
    )
    share = draw_block["largest_thread_share"]
    print(
        f"  largest thread {share['thread']}: {share['payable']} payable →"
        f" {share['allocated']} drawn ({share['share_of_pack']:.1%} of the pack;"
        f" uncapped it would have taken {share['uncapped_would_be']})"
    )
    print("  per-thread distribution (allocated → threads):")
    counts: dict[int, int] = {}
    for row in draw_block["per_thread"]:
        counts[row["allocated"]] = counts.get(row["allocated"], 0) + 1
    for allocated in sorted(counts):
        payable = [
            row["payable"] for row in draw_block["per_thread"] if row["allocated"] == allocated
        ]
        print(
            f"    {allocated:>3} drawn × {counts[allocated]:>3} threads"
            f"   (payable {min(payable)}–{max(payable)})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
