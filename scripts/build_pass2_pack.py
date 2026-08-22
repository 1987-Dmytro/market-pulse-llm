#!/usr/bin/env python3
"""`results/pass2_pack.json` — the 79 pass-2 units, DERIVED and never typed.

**The population is the census's own filter, CALLED.** `docs/PROMPT-pass2-signals.md`: the 79 threads
with at least one row pass 1 labelled `категория_личное` / `молочный_бренд` / `сеть_ритейлер`, over
the UNION of `results/pass1_window_v2.jsonl` (131) and `results/pass1_window_r2_v2.jsonl` (901)
against the WINDOW's pack. So this file builds the union the way the r2 census builds it —
`census_pass1_window_r2.union_view`, a scratch copy under the r1 pack's own leg name, never a merge
on disk — parses it with `census_pass1_window.answers`, and asks
`census_pass1_window.pass_2_filter` for the table. The units are then held to that table thread by
thread and count by count: the filter is the authority and this builder's selection is the thing
being checked ([[a_count_in_prose_is_not_the_enumeration]]).

**Keyed on the PAIR `(thread, msg_id)`, and this is the registration the ADR demanded.** Seven
msg_ids of the window live in two threads each. A unit keyed on the msg_id alone would carry a
namesake's comment out of another channel into this thread's request, and the merge would be silent.

**What the pod sees is not what the pack knows.** The renderer reads five fields — channel, post_id,
post, entities, comments — and the F/E/N membership flags are not among them. `contamination()`
re-renders every item with those flags stripped and refuses if one sha moves, so «the pack carries no
gold» is a measurement rather than an intention.

**Nothing here is re-purchased.** The post is the store's own text
(`build_pass1_label_pack_r2.raw_threads()`), the entity block is the one pass 1 was rendered with
(the r1 pack's own `entities`, cross-checked against `build_pass1_sft.verdicts()` live), and the
labels are pass 1's replies parsed by pass 1's parser.

    PYTHONPATH=src python3.11 scripts/build_pass2_pack.py
    PYTHONPATH=src python3.11 scripts/build_pass2_pack.py --out /tmp/again.json   # the pair
"""

import argparse
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_pass1_fewshot_packs as fewshot  # noqa: E402
import build_pass1_label_pack_r2 as r2pack  # noqa: E402
import build_pass1_sft as sft  # noqa: E402
import build_pass1_window_r2_pack as r2builder  # noqa: E402
import census_pass1_window as r1census  # noqa: E402
import census_pass1_window_r2 as r2census  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import pass2  # noqa: E402

OUT = REPO_ROOT / "results" / "pass2_pack.json"
GOLD = REPO_ROOT / "results" / "reader_gold_w1_r2.json"
CENSUS = REPO_ROOT / "results" / "pass1_window_r2_census.json"
LEG_OUT = "pass2_signals_v1.jsonl"
TASK = pass2.PASS2_TASK_V1

SMOKE = ("F1", "F2", "F3", "F4", "F5")
"""The smoke leg, named by the reference's own case ids and resolved to threads through the gold.

Five thread keys typed here instead would be five chances to type one wrong, and the contract's «the
five F threads» is a statement about `docs/REFERENCE-signals-w1.md`, not about five strings."""


def gold() -> dict:
    return json.loads(summary.read_text_or_refuse(GOLD))


def thread_key(one: dict) -> str:
    return f"{one['channel']}:{one['post_id']}"


def filtered(pack: dict) -> tuple[dict, dict, dict]:
    """The census's filter, CALLED — the parsed union, the per-thread table, and the refusals.

    `pass_2_filter` is what `results/pass1_window_r2_census.json` published and what this contract
    is priced from, so it is the function that decides which rows are in. Running it here rather
    than reading its output means the pack and the census cannot drift: if a reply were re-parsed
    differently tomorrow, the table below moves with the units and the check further down fires.
    """
    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp)
        _, where = r2census.union_view(scratch)
        parsed, refused = r1census.answers(pack, where)
    refused_ids = {one["id"] for one in refused}
    table = r1census.pass_2_filter(pack, parsed, refused_ids, pack["population"]["threads"])
    return parsed, table, {"refused": refused, "refused_ids": refused_ids}


def entity_block(pack: dict) -> dict[str, list[dict]]:
    """Per thread, the block pass 1 was RENDERED with — read off the pack, not re-derived.

    Every item of a thread carries the same block, which is asserted rather than assumed: the r1
    pack is one artefact and a thread whose items disagreed about their context would mean two
    renderings under one thread name. Then the live `build_pass1_sft.verdicts()` is asked the same
    question, and a disagreement REFUSES — a verdict file that moved since the window was rendered
    would put a block in pass 2's request that pass 1 never saw
    ([[a_fixture_on_disk_pins_yesterdays_schema]] read the other way: the pinned pack is the
    producer's own output, and the live producer is the control).
    """
    blocks: dict[str, list[dict]] = {}
    for item in pack["legs"][0]["items"]:
        held = blocks.setdefault(item["thread"], item["entities"])
        if held != item["entities"]:
            raise SystemExit(
                f"{item['thread']}: two items of one thread carry different entity blocks in"
                f" {summary.rel(r2builder.R1_PACK)} — stop and report."
            )
    live = sft.verdicts()
    for name, block in blocks.items():
        _, verdict = live.get(name, (None, {}))
        if (verdict.get("entities") or []) != block:
            raise SystemExit(
                f"{name}: the entity block in the r1 pack and the one build_pass1_sft.verdicts()"
                " resolves today are not the same. pass 2 would show the model a context pass 1"
                " never saw — stop and report."
            )
    return blocks


def unit(thread: str, rows: list[dict], store: dict, block: list[dict], flags: dict) -> dict:
    """One thread's request, rendered here and re-rendered on the pod against this sha."""
    held = store[thread]
    comments = [
        {
            "msg_id": int(row["msg_id"]),
            "text": row["text"],
            "subject_type": row["subject_type"],
            "subject_id": row["subject_id"],
            "stance": row["stance"],
        }
        for row in sorted(rows, key=lambda one: int(one["msg_id"]))
    ]
    content = pass2.pass2_messages_gm4(
        held["channel"], int(held["post_id"]), held["post_text"] or "", block, comments, task=TASK
    )[0]["content"]
    return {
        "id": thread,
        "thread": thread,
        "channel": held["channel"],
        "post_id": int(held["post_id"]),
        "post": held["post_text"] or "",
        "entities": block,
        "comments": comments,
        "task": TASK,
        "membership": flags,
        "rendered_chars": len(content),
        "rendering_sha256": fewshot.sha_text(content),
    }


def membership(record: dict) -> dict[str, dict]:
    """Which threads carry a flagship, an entity case or a noise case — from the GOLD, never typed.

    A pack field and nothing else: `contamination()` proves the renderer cannot read it. It is here
    because the smoke leg IS the F threads and because the report's scorecard has to be able to say
    which units the bars live in without joining two files by hand.
    """
    flags: dict[str, dict] = {}
    for kind, key in (("F", "flagships"), ("E", "entity_cases"), ("N", "noise_threads")):
        for case in record[key]:
            flags.setdefault(thread_key(case), {"F": [], "E": [], "N": []})[kind].append(case["id"])
    return flags


def contamination(items: list[dict], store: dict) -> dict:
    """Four lists, EMPTY in a correct pack — and the third one is the whole claim.

    (1) no comment carries a label outside the pass-2 filter, so no gold answer rode in on a row;
    (2) no comment's text differs from the store's, so nothing was edited into a request;
    (3) **stripping the F/E/N flags moves no rendering sha** — the pod is shown five fields and the
        exam's own membership is not one of them;
    (4) no unit's rendered request names a case id.
    """
    outside, edited, moved, named = [], [], [], []
    for item in items:
        held = store[item["thread"]]
        texts = {int(row["msg_id"]): summary.comment_text(row) for row in held["comments"]}
        for row in item["comments"]:
            if row["subject_type"] not in pass2.PASS2_SUBJECT_TYPES:
                outside.append(f"{item['thread']}#{row['msg_id']}")
            if texts.get(row["msg_id"]) != row["text"]:
                edited.append(f"{item['thread']}#{row['msg_id']}")
        content = pass2.pass2_messages_gm4(
            item["channel"], item["post_id"], item["post"], item["entities"], item["comments"]
        )[0]["content"]
        if fewshot.sha_text(content) != item["rendering_sha256"]:
            moved.append(item["id"])
        for case in sum(item["membership"].values(), []):
            if case in content:
                named.append(f"{item['id']}:{case}")
    return {
        "labels_outside_the_filter": outside,
        "comments_edited_against_the_store": edited,
        "renderings_that_move_without_the_membership_flags": moved,
        "requests_naming_a_case_id": named,
        "fields_the_render_reads": ["channel", "post_id", "post", "entities", "comments"],
        "fields_the_pod_never_reads": ["membership", "rendered_chars", "id"],
        "rule": (
            "the pack carries NO labels and NO gold: the pod sees pass-1's own fields and the"
            " store's own text. `membership` is a pack field the renderer has no argument for, and"
            " list (3) is that sentence measured rather than asserted"
        ),
    }


def order(items: list[dict], smoke: list[str]) -> list[dict]:
    """The five F threads first, then the rest in `channel:post_id` order.

    The smoke leg is a PREFIX and not a second pack: the runner answers a pack in order, so «the
    five F threads FIRST» is the whole mechanism by which `--smoke` and the go/no-go can name the
    same five units without a number being typed anywhere."""
    rank = {name: index for index, name in enumerate(smoke)}
    return sorted(items, key=lambda one: (rank.get(one["id"], len(rank)), one["id"]))


def build() -> dict:
    record = gold()
    pack = r2builder.r1_pack()
    parsed, table, refusals = filtered(pack)
    store = r2pack.raw_threads()
    blocks = entity_block(pack)
    flags = membership(record)

    rows: dict[str, list[dict]] = {}
    for item in pack["legs"][0]["items"]:
        answer = parsed.get(item["id"])
        if answer is None or answer.get("subject_type") not in pass2.PASS2_SUBJECT_TYPES:
            continue
        rows.setdefault(item["thread"], []).append({**item, **answer})

    items = order(
        [
            unit(
                thread,
                found,
                store,
                blocks[thread],
                flags.get(thread, {"F": [], "E": [], "N": []}),
            )
            for thread, found in rows.items()
        ],
        [thread_key(one) for one in record["flagships"]],
    )

    # the filter is the AUTHORITY and the selection above is what is being checked: thread by
    # thread, count by count, against the table `results/pass1_window_r2_census.json` published
    counted = {one["thread"]: one["filtered_rows"] for one in table["per_thread"]}
    mine = {one["id"]: len(one["comments"]) for one in items}
    wanted = {name: n for name, n in counted.items() if n}
    if mine != wanted:
        disagree = sorted(set(mine) ^ set(wanted)) or sorted(
            name for name in mine if mine[name] != wanted[name]
        )
        raise SystemExit(
            f"this build selects {len(mine)} threads and census_pass1_window.pass_2_filter counts"
            f" {len(wanted)} — first disagreement {disagree[:3]}. The filter is the authority and"
            " the selection is the thing being checked. Stop and report."
        )
    if sum(mine.values()) != table["filtered_rows_total"]:
        raise SystemExit(
            f"{sum(mine.values())} rows selected against the table's"
            f" {table['filtered_rows_total']} — stop and report."
        )

    smoke = [one["id"] for one in items[: len(record["flagships"])]]
    wanted_smoke = [thread_key(one) for one in record["flagships"]]
    if smoke != wanted_smoke:
        raise SystemExit(
            f"the leg's first {len(wanted_smoke)} units are {smoke} and the reference's flagship"
            f" threads are {wanted_smoke}. The smoke leg is a PREFIX of the leg — stop and report."
        )
    return {
        "phase": "pass2-signals",
        "contract": "docs/PROMPT-pass2-signals.md D0",
        "registration": {"record": "results/prereg_pass2_signals.json"},
        "task": TASK,
        "what_this_run_is": (
            "the assembly pass: ONE call per THREAD over the comments pass 1 attributed, in the"
            " reader's schema, scored by the reader's own scorer against the reader's gold r2. It"
            " is not the closed one-shot reader — no per-comment attribution from a raw thread, and"
            " no raw unfiltered comment in any request"
        ),
        "population": {
            "units": len(items),
            "payable_comments": len(items),
            "payable_comments_is_the_UNIT_count": (
                "pass 1's word for «how many things this pack asks», carried because"
                " `gate_pass1_window.main` compares this key in the pack against the same key in"
                " the record before every rung that reads a pack. A pass-2 unit is a THREAD and not"
                " a comment, so the NAME is pass 1's and the number is this pack's units. The"
                " inherited guard is pinned by a sealed record and cannot be renamed"
            ),
            "filtered_rows": sum(mine.values()),
            "filtered_chars": sum(len(row["text"]) for one in items for row in one["comments"]),
            "threads_carrying_a_payable_comment": table["threads_carrying_a_payable_comment"],
            "threads_pass_2_would_not_call": table["threads_pass_2_would_not_call"],
            "no_signal_by_construction": sorted(
                one["thread"] for one in table["per_thread"] if not one["filtered_rows"]
            ),
            "filter": list(pass2.PASS2_SUBJECT_TYPES),
            "keyed_on": (
                "the PAIR (thread, msg_id). Seven msg_ids of the window live in two threads each,"
                " so a unit keyed on the msg_id alone would carry another channel's comment into"
                " this thread's request and the merge would be silent"
            ),
            "producer": "census_pass1_window.pass_2_filter, CALLED over the union view",
            "producer_sha256": summary.sha256_of(REPO_ROOT / "scripts" / "census_pass1_window.py"),
            "derived_from": {
                "pack": summary.rel(r2builder.R1_PACK),
                "pack_sha256": summary.sha256_of(r2builder.R1_PACK),
                "pack_pinned_by": f"{summary.rel(r2builder.R1_PREREG)}::population.sha256",
                "out_files": {
                    summary.rel(one): summary.sha256_of(one)
                    for one in (
                        r2builder.R1_OUT,
                        REPO_ROOT / "results" / "pass1_window_r2_v2.jsonl",
                    )
                },
                "census": {
                    "record": summary.rel(CENSUS),
                    "sha256": summary.sha256_of(CENSUS),
                    "reading": (
                        "the published table this contract was priced from. It is not READ here —"
                        " the filter is re-run — and this sha is what a reader compares against"
                    ),
                },
            },
            "parse": {
                "answered": len(parsed),
                "refused": len(refusals["refused"]),
                "refusals_by_cause": dict(
                    sorted(Counter(one["cause"] for one in refusals["refused"]).items())
                ),
                "rule": (
                    "a pass-1 reply that could not be read carries no label, so its row is not in"
                    " the filter and its thread is called only if another row of it is. That is a"
                    " state of the INPUT and it is counted here rather than discovered later"
                ),
            },
        },
        "legs": [
            {
                "name": "v1",
                "task": TASK,
                "out": LEG_OUT,
                "reading": (
                    "the ONE leg. The smoke is its first five units and not a second leg: two legs"
                    " would be two out-files, and the whole point of the go/no-go is that the"
                    " remaining 74 land in the same file the smoke did"
                ),
                "items": items,
            }
        ],
        "smoke": {
            "cases": list(SMOKE),
            "ids": smoke,
            "units": len(smoke),
            "rule": (
                "the reference's five flagship threads, resolved through the gold and placed FIRST"
                " in the leg. `scripts/pass2_pod_runner.py --smoke` answers exactly these and then"
                " WAITS; rung S′ reads their seconds off the out-file and writes the go"
            ),
            "not_a_sample": (
                "these five carry 30 of the 281 filtered rows — 6.0 rows a thread against the"
                " population's 3.56. The rate they measure is charged on the remaining 74 as"
                " registered, and the row-weighted reading is published beside it, never gating"
            ),
        },
        "serving": {
            **{
                key: value
                for key, value in pack["serving"].items()
                if key not in ("output_tokens", "template_note")
            },
            "output_tokens": pass2.PASS2_MAX_OUTPUT_TOKENS,
            "template_note": (
                "the window pack's serving block, with the reader's own output ceiling in place of"
                " pass 1's 256: a pass-2 reply is a list of signals and per-comment rows, and 256"
                " tokens is a third of what v5b's replies took. TOKENS, not characters"
            ),
        },
        "instruments": {
            "prompt_sha256": {TASK: pass2.prompt_sha256(TASK)},
            "module": {
                "path": "src/market_pulse/pass2.py",
                "sha256": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "pass2.py"),
            },
            "parser": {
                "entry_point": "market_pulse.pass2.parse_pass2",
                "module": "src/market_pulse/prompts.py",
                "sha256": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "prompts.py"),
                "rule": (
                    "the reader's own two halves, `prompts._reader_object` then `prompts._reader` —"
                    " the exact pair `prompts.parse_reply` binds for a reader task — with the"
                    " thread's bought entity block placed into the payload between them, and four"
                    " refusals of pass 2's own on top: the thread echo, an id that was not in the"
                    " request, a signal citing no comment, and a RELABELLING"
                ),
            },
        },
        "length": fewshot.ceiling_check(items),
        "membership": {
            "rule": "from results/reader_gold_w1_r2.json; a PACK field the renderer cannot read",
            "per_kind": {
                kind: sorted(one["id"] for one in items if one["membership"][kind])
                for kind in ("F", "E", "N")
            },
            "cases_outside_the_population": {
                kind: sorted(
                    thread_key(case)
                    for case in record[key]
                    if thread_key(case) not in {one["id"] for one in items}
                )
                for kind, key in (
                    ("F", "flagships"),
                    ("E", "entity_cases"),
                    ("N", "noise_threads"),
                )
            },
        },
        "contamination": contamination(items, store),
        "producer": {
            "script": summary.rel(Path(__file__)),
            "sha256": summary.sha256_of(Path(__file__)),
            "borrowed": {
                name: summary.sha256_of(REPO_ROOT / name)
                for name in (
                    "scripts/census_pass1_window.py",
                    "scripts/census_pass1_window_r2.py",
                    "scripts/build_pass1_window_r2_pack.py",
                    "scripts/build_pass1_label_pack_r2.py",
                    "scripts/build_pass1_sft.py",
                    "scripts/build_pass1_fewshot_packs.py",
                )
            },
            "borrowed_rule": (
                "the filter, the union view, the sealed-pack guard, the store, the bought verdicts"
                " and the ceiling check. Everything this pack is made of already existed"
            ),
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
    people = pack["population"]
    print(f"wrote {summary.rel(args.out)}  sha256 {summary.sha256_of(args.out)[:16]}…")
    print(
        f"  {people['units']} units · {people['filtered_rows']} filtered rows ·"
        f" {people['filtered_chars']} chars ·"
        f" {people['threads_pass_2_would_not_call']} callable threads with no signal by construction"
    )
    print(f"  smoke leg: {' · '.join(pack['smoke']['ids'])}")
    print(
        f"  length: widest {pack['length']['widest_request_chars']} chars"
        f" ({pack['length']['widest_request']}) · median {pack['length']['median_chars']} ·"
        f" headroom {pack['length']['headroom_chars']} of {pack['length']['ceiling_chars']}"
    )
    print(
        "  membership: "
        + " · ".join(
            f"{kind} {len(pack['membership']['per_kind'][kind])} in,"
            f" {len(pack['membership']['cases_outside_the_population'][kind])} out"
            for kind in ("F", "E", "N")
        )
    )
    print(
        f"  contamination: {json.dumps({k: v for k, v in pack['contamination'].items() if isinstance(v, list)}, ensure_ascii=False)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
