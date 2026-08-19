#!/usr/bin/env python3
"""The r2 RE-DRAW pack — a targeted top-up of the labelling set, drawn from the dairy-signal threads.

**What this builds.** Sitting-2 of 2026-08-19 ruled that line B's class deficit (38 «our» rows of
500) is closed by WEIGHTING plus a TARGETED RE-DRAW, with two training arms — A = 500 weighted,
B = 500 + this re-draw. This producer draws the re-draw and renders it for a human:
`docs/label-pack-pass1-r2.md` and `results/pass1_label_pack_r2.json`. It trains nothing, spends
nothing and makes no cloud call. No blind subset: the operator's blind-40 option lives on r1.

**The candidate rule, and what the census found.** `docs/PROMPT-pass1-redraw.md` D1 defines a
CANDIDATE as a thread where the shipped matcher finds a watchlist hit — a dairy brand or a tracked
category — in the post or the comments, under DEFAULT matching (`rules=None`, the mode every sealed
record was measured under). That predicate is `gate_census_w1.hits`, and it is the same one the
reader cell was selected with, so it keeps **every thread of the tract**: 129 of 129, 122 after the
exam. The census is not vacuous for being total — it is the finding, and :func:`census_table`
prints the three narrower definitions beside it with what each one YIELDED on r1's 500 labels, so
the next ruling can be made on measured lift instead of on the word «targeted».

**What is subtracted.** The 7 exam threads (`results/pass1_label_pack_r1.json` `exclusion.threads`),
then the 500 units r1 already drew, then the 14 gold rows — the last of which removes nothing,
because every gold row lives inside an exam thread, and an empty class is an answer worth printing.

**The cap and the target, in that order.** The cap is the 90th percentile of the candidate threads'
payable counts, re-derived at every run; the weight is `min(available, CAP)`, because what r2 may
draw from a thread is what r1 left there. `sum(w)` is computed and PRINTED before
`target = min(150, available, sum(w))` freezes — an absolute number needs a reachability state, and
a target that quietly exceeds its own ceiling is a claim the draw cannot honour.

    PYTHONPATH=src python3.11 scripts/build_pass1_label_pack_r2.py --census   # D1, writes nothing
    PYTHONPATH=src python3.11 scripts/build_pass1_label_pack_r2.py
    PYTHONPATH=src python3.11 scripts/build_pass1_label_pack_r2.py --outdir /tmp/again   # the pair
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

from market_pulse import brands, loop, prompts  # noqa: E402

R1_PACK = REPO_ROOT / "results" / "pass1_label_pack_r1.json"
R1_LABELS = REPO_ROOT / "docs" / "labels-pass1-r1.jsonl"
PROBE_PACK = REPO_ROOT / "results" / "pass1_probe_b_pack.json"
GOLD_R2 = REPO_ROOT / "results" / "reader_gold_w1_r2.json"

PACK_NAME = "results/pass1_label_pack_r2.json"
RENDER_NAME = "docs/label-pack-pass1-r2.md"
LABELS_NAME = "docs/labels-pass1-r2.jsonl"

SEED = 20260819
"""The date of sitting-2, and the only source of randomness here.

A module constant and not a flag, for r1's reason: a `--seed` option is an option to produce a
different pack, and the pack is what every later contract joins against."""

TARGET = 150
"""The sitting's ceiling for the re-draw. `min(TARGET, available, sum(weights))` is what ships —
the `min` is what makes it a formula rather than a wish, and the third term is the one Dv520/Dv527
exist for: the cap can put the ceiling below the number somebody wrote down."""

OURS = ("молочный_бренд", "категория_личное")
"""The two classes sitting-2 calls «наши» — the deficit the re-draw is aimed at. Used only to
MEASURE what each candidate definition yielded on r1's labels; nothing is drawn on this basis."""

SUBJECT_TYPES = prompts.PASS1_SUBJECT_TYPES
"""The four readings, from the module the pass-1 prompt itself answers in. Never retyped here."""


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def thread_id(one: dict) -> str:
    return f"{one['channel']}:{one['post_id']}"


def percentile(values: list[int], q: float) -> int:
    ordered = sorted(values)
    return ordered[math.ceil(q * len(ordered)) - 1]


def r1_record() -> dict:
    return json.loads(summary.read_text_or_refuse(R1_PACK))


def excluded_threads(r1: dict) -> list[str]:
    """The 7 exam threads, READ from the r1 record and held to their own derivation.

    The contract names `exclusion.threads` of that record as the source. It is an enumeration and
    not prose, so it can be joined against — and it is checked here against the probe pack it was
    derived from, because a list copied forward is a list nobody re-derives
    ([[count_in_prose_is_not_the_enumeration]]).
    """
    named = sorted(r1["exclusion"]["threads"])
    pack = json.loads(summary.read_text_or_refuse(PROBE_PACK))
    derived = sorted({one["thread"] for one in pack["items"]})
    if named != derived:
        raise SystemExit(
            f"the r1 record names {len(named)} exam threads and the probe pack derives"
            f" {len(derived)}. One of the two is stale — stop and report."
        )
    return named


def gold_msg_ids() -> list[int]:
    """The 14 rows the sealed bar is scored on. They may appear nowhere in this pack."""
    gold = json.loads(summary.read_text_or_refuse(GOLD_R2))
    return sorted(int(row["msg_id"]) for row in gold["per_comment"])


def signals() -> list[dict]:
    """Every thread of the reader cell with what the SHIPPED matcher finds in it.

    The texts are the ones the cell's own gate read — the post plus the comments its two silencers
    leave — and the carrier is threaded per text, because SPEC 3.21 (1) scopes the `garmonija` rule
    to comment text. `rules=None` is the DEFAULT matching the contract fixes: the mode every sealed
    record was measured under, and the one the cell itself was selected with.
    """
    prereg = json.loads(summary.read_text_or_refuse(reader.builder.PREREG))
    registry = summary.registry_through_the_seal(prereg, reader.builder.REGISTRY)
    aliases = brands.watchlist_aliases(registry.watchlist)
    categories = census.compiled(wide=False)
    raw = {thread_id(one): one for one in reader.window()}

    out = []
    for one in cell.population():
        name = thread_id(one)
        full = raw[name]
        surviving = [
            row for row in full["comments"] if not census.silenced_comment(row, cell.SILENCERS)
        ]
        texts = [(full["post_text"], census.POST_CARRIER)] + [
            (summary.comment_text(row), census.CARRIER) for row in surviving
        ]
        found = {"brands": set(), "categories": set()}
        for text, carrier in texts:
            hit = census.hits(text, categories, aliases, None, carrier)
            found["brands"] |= set(hit["brands"])
            found["categories"] |= set(hit["categories"])
        out.append(
            {
                "thread": name,
                "brands": sorted(found["brands"]),
                "categories": sorted(found["categories"]),
                "payable": [int(row["msg_id"]) for row in one["comments"]],
            }
        )
    return sorted(out, key=lambda one: one["thread"])


def is_candidate(one: dict) -> bool:
    """D1's rule: a watchlist hit — a dairy brand OR a tracked category — anywhere in the thread."""
    return bool(one["brands"] or one["categories"])


def available_units(rows: list[dict], r1: dict, gold: set[int]) -> dict[str, list[int]]:
    """Per thread, the payable msg-ids r2 may draw: not drawn by r1, not a gold row."""
    drawn = {(unit["thread"], int(unit["msg_id"])) for unit in r1["units"]}
    return {
        one["thread"]: [
            msg_id
            for msg_id in sorted(one["payable"])
            if (one["thread"], msg_id) not in drawn and msg_id not in gold
        ]
        for one in rows
    }


def census_table(rows: list[dict], r1: dict, gold: set[int], excluded: set[str]) -> dict:
    """D1 — the dairy-signal census, and the three narrower definitions beside it.

    Each row is measured twice: how much of the tract it selects, and what it YIELDED on the 500
    labels r1 already carries. The second column is the one that decides whether «targeted» buys
    anything, and it can only be measured because r1's labels exist — a definition priced by the
    words in it is a definition nobody priced ([[price_the_incumbent_in_the_same_units]]).
    """
    labels = [
        json.loads(line)
        for line in R1_LABELS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    by_thread = {one["thread"]: one for one in rows}
    definitions = {
        "brand or category (D1's rule, = the shipped gate)": is_candidate,
        "watchlist brand only": lambda one: bool(one["brands"]),
        "tracked category only": lambda one: bool(one["categories"]),
        "category and no brand": lambda one: one["categories"] and not one["brands"],
    }
    available = available_units(rows, r1, gold)
    out = {}
    for name, keep in definitions.items():
        kept = [one for one in rows if keep(one)]
        after = [one for one in kept if one["thread"] not in excluded]
        payable = sum(len(one["payable"]) for one in after)
        free = sum(len(available[one["thread"]]) for one in after)
        answered = [row for row in labels if keep(by_thread[row["thread"]])]
        ours = sum(1 for row in answered if row["subject_type"] in OURS)
        out[name] = {
            "candidate_threads": len(kept),
            "threads_after_exam": len(after),
            "payable": payable,
            "already_drawn_by_r1": payable - free,
            "available": free,
            "r1_rows_in_them": len(answered),
            "r1_ours_in_them": ours,
            "r1_ours_share": round(ours / len(answered), 4) if answered else None,
        }
    out["_reading"] = (
        "«ours» is молочный_бренд + категория_личное, the two classes sitting-2 is short of. The"
        " share is measured on r1's own 500 labels, restricted to the rows the definition would"
        " have kept; the pack's own baseline is the first row, which is the whole tract"
    )
    return out


def assert_cap_is_the_derivation(sizes: list[int], cap: int) -> None:
    """Refuse unless ``cap`` still IS the 90th percentile it claims to be."""
    derived = percentile(sizes, 0.90)
    if derived != cap:
        raise SystemExit(
            f"the cap is {cap} and the 90th percentile of the candidate subset is {derived}. The"
            " constant claims to be a derivation and it has stopped being one — re-derive it, do"
            " not re-run this producer."
        )


def allocate(weights: dict[str, int], target: int) -> dict[str, int]:
    """`target` units over the threads by LARGEST REMAINDER on the capped weights — r1's rule.

    Largest remainder cannot exceed a weight here: `floor(target * w / W) + 1 <= w` for every
    `w >= 1` whenever `target < W`, and `W >= target` is asserted first. The tie-break is
    `(-remainder, thread)` — a total key, so two runs cannot order two equal remainders differently.
    """
    total = sum(weights.values())
    if total < target:
        raise SystemExit(
            f"the capped weights sum to {total} and the target is {target}: this population cannot"
            " fill the pack. Lower the target — do not let the draw come up short silently."
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


def draw(
    allocation: dict[str, int], available: dict[str, list[int]], rng: random.Random
) -> list[dict]:
    """`allocation[thread]` msg-ids per thread, in thread order, off ONE seeded stream."""
    units = []
    for name in sorted(allocation):
        take = allocation[name]
        if not take:
            continue
        for msg_id in sorted(rng.sample(available[name], take)):
            units.append({"thread": name, "msg_id": msg_id})
    return units


def raw_threads() -> dict[str, dict]:
    """Every thread of the window as the store holds it — silenced and text-less comments included.

    The rendering shows the FULL thread: a labeller reads a conversation, and a conversation with a
    third of its turns deleted is not the one the comment was written into.
    """
    return {thread_id(one): one for one in reader.window()}


def comment_state(row: dict) -> str:
    if census.silenced_comment(row, cell.SILENCERS):
        return "silenced"
    if not loop.has_text(summary.comment_text(row)):
        return "text-less"
    return "payable"


def quote(text: str) -> str:
    lines = (text or "").splitlines() or [""]
    return "\n".join(f"> {line}" if line else ">" for line in lines)


def r2_ruling() -> dict:
    """The gold-r2 adjudication, quoted — WITHOUT the sentence that names a gold row.

    `revision.ruling.reading` ends by naming msg 21599, its gold value and the bar it moved. That is
    exam material and the honesty frame forbids showing it to the labeller, so the quote stops at
    the rule and the elision is declared rather than silent (Dv519).
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
    return "\n".join(
        [
            "## Codebook",
            "",
            "You are labelling ONE field, `subject_type`, on the comments marked **TARGET** below."
            " Nothing else is asked: `stance` reads 3 of 3 already and is not this pack's business."
            " The law below is the SAME law r1 was labelled under, by the same bytes — a re-draw"
            " that changed the codebook would be a second instrument and not more of the first.",
            "",
            "### The four readings, and the null",
            "",
            f"{values} — and JSON `null`.",
            "",
            "`null` is an ANSWER and not a skip: it says «this comment is about nobody». The pass-1"
            " prompt spells it «or null where the comment is about nobody», and the instrument's"
            " own abstentions are exactly what line B exists to fix — so a comment you would have"
            " left blank is a comment that needs `null` written down.",
            "",
            "«категория» is NOT one of the four. It is the reference's word for the same class as"
            " `категория_личное` and only the second is offered here.",
            "",
            "### ATTRIBUTION — the law, by the same bytes",
            "",
            "> Source: `src/market_pulse/prompts.py` :: `READER_ATTRIBUTION_LAW_V5`, sha256"
            f" `{sha_text(law)[:16]}…` — the same string the pass-1 prompt carries by reference, so"
            " a label and an answer are decided by one law and not by two wordings of it.",
            "",
            "```",
            law.strip(),
            "```",
            "",
            "The three examples are SYNTHETIC and proven to occur in no stored comment, no post and"
            " no gold file (`tests/test_reader_prompt_v5.py`).",
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
            f"One JSON object per line into `{LABELS_NAME}`, one line per TARGET:",
            "",
            "```",
            '{"thread": "@example:1", "msg_id": 999999, "subject_type": "категория_личное"}',
            "```",
            "",
            "`subject_type` is one of the four strings above or JSON `null`. Every TARGET is"
            " answered exactly once and nothing else is answered. The gate is the r1 validator"
            " pointed at this pack — it refuses anything else and writes nothing:",
            "",
            "```",
            f"PYTHONPATH=src python3.11 scripts/validate_pass1_labels.py {LABELS_NAME}"
            f" --pack {PACK_NAME}",
            "```",
            "",
            f"Every unit is also in `{PACK_NAME}` in this order, if a skeleton is easier than"
            " typing. **This pack shares no unit with r1**: a comment you labelled there does not"
            " appear here.",
        ]
    )


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
            head = f"**`{msg_id}`**"
            if msg_id in marked:
                head += "  ⬛ **TARGET**"
            else:
                state = comment_state(row)
                if state != "payable":
                    head += f"  *({state})*"
            text = summary.comment_text(row)
            out += [head, "", quote(text) if text else "> *(no text)*", ""]
    return "\n".join(out).rstrip() + "\n"


def measure() -> dict:
    """Everything D1 asks for, and the reachability D2 must print BEFORE the target freezes."""
    r1 = r1_record()
    rows = signals()
    gold = set(gold_msg_ids())
    excluded = set(excluded_threads(r1))
    table = census_table(rows, r1, gold, excluded)

    candidates = [one for one in rows if is_candidate(one) and one["thread"] not in excluded]
    available = available_units(candidates, r1, gold)
    sizes = [len(one["payable"]) for one in candidates]
    cap = percentile(sizes, 0.90)
    assert_cap_is_the_derivation(sizes, cap)
    weights = {one["thread"]: min(len(available[one["thread"]]), cap) for one in candidates}
    free = sum(len(one) for one in available.values())
    target = min(TARGET, free, sum(weights.values()))
    return {
        "r1": r1,
        "rows": rows,
        "gold": gold,
        "excluded": excluded,
        "census": table,
        "candidates": candidates,
        "available": available,
        "sizes": sizes,
        "cap": cap,
        "weights": weights,
        "free": free,
        "target": target,
    }


def print_census(state: dict) -> None:
    """D1's table — read-only, and printed before anything is written."""
    print(
        f"D1 — the dairy-signal census (matcher: {summary.rel(REPO_ROOT / 'src/market_pulse')}"
        " brands ∪ tracked categories, DEFAULT matching)"
    )
    head = f"  {'definition':48} {'thr':>4} {'-exam':>6} {'payable':>8} {'drawn':>6} {'avail':>6}"
    print(head + f" {'r1 rows':>8} {'ours':>5} {'share':>7}")
    for name, row in state["census"].items():
        if name.startswith("_"):
            continue
        share = "—" if row["r1_ours_share"] is None else f"{row['r1_ours_share']:.1%}"
        print(
            f"  {name:48} {row['candidate_threads']:>4} {row['threads_after_exam']:>6}"
            f" {row['payable']:>8} {row['already_drawn_by_r1']:>6} {row['available']:>6}"
            f" {row['r1_rows_in_them']:>8} {row['r1_ours_in_them']:>5} {share:>7}"
        )
    picked = state["census"]["brand or category (D1's rule, = the shipped gate)"]
    print(
        f"\n  arithmetic (D1's rule): {picked['payable']} payable in the"
        f" {picked['threads_after_exam']} candidate threads left after the {len(state['excluded'])}"
        f" exam threads − {picked['already_drawn_by_r1']} drawn by r1 −"
        f" {sum(1 for one in state['candidates'] for i in one['payable'] if i in state['gold'])}"
        f" gold = {picked['available']} AVAILABLE"
    )
    sizes = state["sizes"]
    avail = sorted(len(one) for one in state["available"].values())
    print(
        f"  candidate threads: payable min {min(sizes)} · median {percentile(sizes, 0.5)} · p90"
        f" {percentile(sizes, 0.9)} · max {max(sizes)}   |   available min {avail[0]} · median"
        f" {percentile(avail, 0.5)} · p90 {percentile(avail, 0.9)} · max {avail[-1]}"
    )
    print(
        f"  REACHABILITY BEFORE THE TARGET: cap {state['cap']} (p90 of the candidates' payable"
        f" counts) → sum(min(available, cap)) = {sum(state['weights'].values())};"
        f" available {state['free']}; ceiling {TARGET}"
        f"  →  target = min({TARGET}, {state['free']}, {sum(state['weights'].values())})"
        f" = {state['target']}"
    )


def build(state: dict | None = None) -> tuple[dict, str]:
    """The record and the page. ``state`` is :func:`measure`'s, so a caller that has already
    printed the census does not pay for a second window pass."""
    state = state or measure()
    r1, gold, excluded = state["r1"], state["gold"], state["excluded"]
    candidates, available, cap = state["candidates"], state["available"], state["cap"]
    weights, target = state["weights"], state["target"]

    allocation = allocate(weights, target)
    units = draw(allocation, available, rng=random.Random(SEED))
    threads = raw_threads()
    rendering = render(
        units,
        threads,
        "Label pack — pass 1, r2 (the re-draw)",
        f"**{len(units)} comments to label**, drawn from"
        f" {sum(1 for one in allocation.values() if one)} threads under seed `{SEED}`. Every thread"
        " is printed WHOLE — post first, then every comment in the store's own order, whether it is"
        " payable or not — and only the comments marked **TARGET** are labelled. None of them was"
        " drawn for r1.",
    )

    r1_units = {(unit["thread"], int(unit["msg_id"])) for unit in r1["units"]}
    drawn_ids = {unit["msg_id"] for unit in units}
    picked = state["census"]["brand or category (D1's rule, = the shipped gate)"]
    record = {
        "phase": "pass1-redraw",
        "contract": "docs/PROMPT-pass1-redraw.md D2",
        "authority": (
            "sitting-2 of 2026-08-19, registered in docs/STATUS.md: the class deficit is closed by"
            " WEIGHTING plus a TARGETED RE-DRAW from dairy-signal threads (synthetic only if the"
            " gate later runs red), and the two training arms are A = 500 weighted and"
            " B = 500 + this re-draw, with the re-draw ablated at training time"
        ),
        "labels": {
            "field": "subject_type",
            "values": [*SUBJECT_TYPES, None],
            "file": LABELS_NAME,
            "written_by": (
                "the TEAM LEAD. It is a team-lead file from the moment it exists: the executor"
                " validates it and commits it verbatim, and never writes a label into it"
            ),
            "validator": (
                f"scripts/validate_pass1_labels.py {LABELS_NAME} --pack {PACK_NAME} — the r1 gate"
                " unchanged, pointed at this pack. Its refusals are pack-relative already, so a"
                " second validator would have been a second place for the taxonomy to drift"
            ),
            "provenance_debt": (
                "labelled_by, date, codebook and this record's sha are frozen into results/ by the"
                " NEXT contract, after the labels exist and validate — not here"
            ),
        },
        "census": state["census"],
        "population": {
            "cell": cell.CELL,
            "record": summary.rel(cell.OUT),
            "sha256": summary.sha256_of(cell.OUT),
            "candidate_rule": (
                "a thread where the shipped matcher finds a watchlist hit — a dairy brand or a"
                " tracked category — in the post or in the comments the cell's silencers leave,"
                " under DEFAULT matching (rules=None). That is gate_census_w1.hits, the predicate"
                " the cell itself was selected with"
            ),
            "matcher": {
                "brand_half": "market_pulse.brands.find_watchlist_brands (rules=None)",
                "category_half": (
                    "market_pulse.yield_screen.category_hits over gate_census_w1.compiled(wide="
                    "False) — config/lexicon.yaml's tracked groups, dairy and ice-cream"
                ),
                "reading": (
                    "the contract names market_pulse.brands as «the ONE matcher», quoting"
                    " config/watchlist_rules.yaml — whose header says it is the one matcher THAT"
                    " READS THAT FILE. The category half of a watchlist hit lives in yield_screen,"
                    " and D1's own parenthetical («dairy brand or category») requires it"
                ),
            },
            "threads_in_cell": len(state["rows"]),
            "candidate_threads": picked["candidate_threads"],
            "threads_after_exam": picked["threads_after_exam"],
            "payable_in_candidates": picked["payable"],
            "already_drawn_by_r1": picked["already_drawn_by_r1"],
            "gold_rows_inside_candidates": sum(
                1 for one in candidates for msg_id in one["payable"] if msg_id in gold
            ),
            "available": picked["available"],
            "arithmetic": (
                f"{picked['payable']} payable in the {picked['threads_after_exam']} candidate"
                f" threads that survive the {len(excluded)} exam threads −"
                f" {picked['already_drawn_by_r1']} already drawn by r1 − 0 gold rows (every gold"
                f" row lives inside an exam thread) = {picked['available']} available →"
                f" min({TARGET}, {picked['available']}, {sum(weights.values())}) = {target} drawn"
            ),
            "the_candidate_rule_selects_the_whole_tract": (
                picked["candidate_threads"] == len(state["rows"])
            ),
            "payable_per_candidate_thread": {
                "min": min(state["sizes"]),
                "median": percentile(state["sizes"], 0.50),
                "p90": percentile(state["sizes"], 0.90),
                "max": max(state["sizes"]),
            },
        },
        "exclusion": {
            "rule": (
                "the 7 exam threads of the r1 record leave the population WHOLE, then r1's 500"
                " units and the 14 gold rows leave it unit by unit. r2 and r1 therefore share no"
                " unit, and no labeller sees a comment twice"
            ),
            "threads": sorted(excluded),
            "r1_units": len(r1["units"]),
            "gold_msg_ids": sorted(gold),
            "proof": {
                "drawn_units_in_an_exam_thread": sorted(
                    unit["thread"] for unit in units if unit["thread"] in excluded
                ),
                "drawn_units_already_drawn_by_r1": sorted(
                    f"{unit['thread']}:{unit['msg_id']}"
                    for unit in units
                    if (unit["thread"], unit["msg_id"]) in r1_units
                ),
                "gold_msg_ids_drawn": sorted(drawn_ids & gold),
                "gold_msg_ids_in_the_candidate_population": sorted(
                    {msg_id for one in candidates for msg_id in one["payable"]} & gold
                ),
                "gold_msg_ids_rendered": sorted(one for one in gold if str(one) in rendering),
                "reading": (
                    "all five lists are empty in a correct pack. The last is checked against the"
                    " RENDERED text and not against the unit list, because the rendering shows"
                    " every comment of a thread and not only the drawn ones"
                ),
            },
        },
        "draw": {
            "seed": SEED,
            "target_rule": f"min({TARGET}, available, sum of the capped weights)",
            "target": target,
            "drawn": len(units),
            "cap": cap,
            "cap_rule": (
                "the 90th percentile of the CANDIDATE threads' payable counts, re-derived at every"
                " run and refused if it moves. The candidate subset is r1's remaining population"
                " thread for thread, so this is r1's cap re-derived and not r1's cap copied"
            ),
            "formula": (
                "weight w = min(units still available in the thread, cap) — what r2 may draw is"
                " what r1 left. Allocate the target over the threads by LARGEST REMAINDER on w,"
                " tie-broken on (−remainder, thread); take that many msg_ids from the thread's"
                " sorted available list off one random.Random(SEED) stream"
            ),
            "reachability": {
                "capped_weight_sum": sum(weights.values()),
                "available": state["free"],
                "ceiling": TARGET,
                "target": target,
                "reachable": sum(weights.values()) >= target,
                "binding": (
                    "ceiling"
                    if target == TARGET
                    else ("available" if target == state["free"] else "cap")
                ),
                "reading": (
                    "computed and printed BEFORE the target froze. An absolute number needs a"
                    " reachability state, and the cap can put the ceiling below the number"
                    " somebody wrote down"
                ),
            },
            "per_thread": [
                {
                    "thread": one["thread"],
                    "payable": len(one["payable"]),
                    "available": len(available[one["thread"]]),
                    "weight": weights[one["thread"]],
                    "allocated": allocation[one["thread"]],
                }
                for one in candidates
            ],
        },
        "blind": {
            "drawn": 0,
            "rule": (
                "NOT drawn for r2. The operator's blind-40 option lives on r1"
                " (docs/label-pack-pass1-r1-blind40.md) and this pack spends no row on it"
            ),
        },
        "rendering": {
            "file": RENDER_NAME,
            "sha256": sha_text(rendering),
            "chars": len(rendering),
            "threads_rendered": sum(1 for one in allocation.values() if one),
            "rule": (
                "each thread WHOLE — post first, then every comment in the store's own order,"
                " payable or not — with the drawn ones marked TARGET"
            ),
            "codebook": {
                "attribution_law": "src/market_pulse/prompts.py::READER_ATTRIBUTION_LAW_V5",
                "attribution_law_sha256": sha_text(prompts.READER_ATTRIBUTION_LAW_V5),
                "f2a_carve_out": "src/market_pulse/prompts.py::READER_CARRY_V5",
                "f2a_carve_out_sha256": sha_text(prompts.READER_CARRY_V5),
                "r2_adjudication": "results/reader_gold_w1_r2.json::revision",
                "same_law_as_r1": (
                    sha_text(prompts.READER_ATTRIBUTION_LAW_V5)
                    == r1["rendering"]["codebook"]["attribution_law_sha256"]
                ),
                "quoted_by": (
                    "the same bytes, read from the module the pass-1 prompt itself answers under —"
                    " never retyped, so r1 and r2 are one instrument and not two"
                ),
            },
        },
        "units": units,
        "producer": {
            "script": summary.rel(Path(__file__)),
            "sha256": summary.sha256_of(Path(__file__)),
            "r1_producer_untouched": (
                summary.sha256_of(REPO_ROOT / "scripts" / "build_pass1_label_pack.py")
                == r1["producer"]["sha256"]
            ),
            "borrowed": {
                name: summary.sha256_of(REPO_ROOT / name)
                for name in (
                    "scripts/gate_census_w1_reader.py",
                    "scripts/gate_census_w1.py",
                    "scripts/reader_population.py",
                    "scripts/window_summary_5c2.py",
                    "src/market_pulse/brands.py",
                    "src/market_pulse/prompts.py",
                    "src/market_pulse/loop.py",
                )
            },
        },
        "inputs": {
            summary.rel(path): summary.sha256_of(path)
            for path in (cell.OUT, R1_PACK, R1_LABELS, PROBE_PACK, GOLD_R2)
        },
    }
    return record, rendering


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--outdir",
        type=Path,
        default=REPO_ROOT,
        help="write the two files under this root instead of the repo (for the pair check)",
    )
    parser.add_argument(
        "--census",
        action="store_true",
        help="print D1's census and the reachability, write nothing",
    )
    args = parser.parse_args(argv)
    if args.census:
        print_census(measure())
        return 0

    state = measure()
    print_census(state)
    print()
    record, rendering = build(state)
    for name, text in (
        (RENDER_NAME, rendering),
        (PACK_NAME, json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n"),
    ):
        path = args.outdir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {name}  sha256 {sha_text(text)[:16]}…  {len(text)} chars")

    draw_block = record["draw"]
    print(f"  {record['population']['arithmetic']}")
    proof = record["exclusion"]["proof"]
    print(
        f"  contamination: in-exam {len(proof['drawn_units_in_an_exam_thread'])}"
        f" · already-drawn {len(proof['drawn_units_already_drawn_by_r1'])}"
        f" · gold drawn {len(proof['gold_msg_ids_drawn'])}"
        f" · gold in population {len(proof['gold_msg_ids_in_the_candidate_population'])}"
        f" · gold rendered {len(proof['gold_msg_ids_rendered'])}"
    )
    print(
        f"  seed {draw_block['seed']} · cap {draw_block['cap']} (p90) · capped weights"
        f" {draw_block['reachability']['capped_weight_sum']} >= target {draw_block['target']}"
        f" — reachable {draw_block['reachability']['reachable']}, binding"
        f" {draw_block['reachability']['binding']}"
    )
    print("  per-thread distribution (allocated → threads):")
    counts: dict[int, int] = {}
    for row in draw_block["per_thread"]:
        counts[row["allocated"]] = counts.get(row["allocated"], 0) + 1
    for allocated in sorted(counts):
        pool = [
            row["available"] for row in draw_block["per_thread"] if row["allocated"] == allocated
        ]
        print(
            f"    {allocated:>3} drawn × {counts[allocated]:>3} threads"
            f"   (available {min(pool)}–{max(pool)})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
