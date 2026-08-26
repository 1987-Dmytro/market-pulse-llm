#!/usr/bin/env python3
"""The packs `think-zero-shot` reads with, derived from the packs the BEFORE columns were read with.

Ruling (ф) buys the SAME prompts over the SAME rows with the thinking channel open. So nothing here
selects, samples or renders anything new: every item is copied from the shipped pack byte for byte,
and this file changes exactly three things.

**The instrument.** `serving.serving_config` becomes `READER_THINK`, `serving.chat_template` becomes
`local_llm.THINK_CHAT_TEMPLATE`, and `serving.output_tokens` becomes the ceiling the contract
registers — 4 000 for pass 1, 8 000 for pass 2. The template is derived FROM the config name through
the runner's own closed table, so the two fields cannot disagree.

**The pins.** `docs/PROMPT-think-zero-shot.md` D1.2 teaches `prompts.parse_reply` to read past a
closed thought, which moves `src/market_pulse/prompts.py`'s sha — and every handshake in this family
refuses a pack whose parser sha is not the live one, before the model is loaded. The shipped packs
are pinned inside sealed registrations and are NOT rebuilt; these carry the live shas and a
`moved_from_the_shipped_pack` block naming what moved and why, which is the idiom
`results/pass1_dev_pack.json` already uses one revision earlier.

**The legs.** Pass 2 is split into the reference threads and the remainder, because the contract
buys them as two stages with a projection rung between them, and `pass2_r2_pod_runner.main` answers
exactly one leg per pack. The smoke packs are one item and three items writing into the SAME
out-files their legs use, so a smoke row is a row the leg then resumes over instead of re-buying.

    PYTHONPATH=src python3 scripts/build_think_packs.py --outdir results
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pass1_fewshot_pod_runner as fewshot  # noqa: E402
import pass2_r2_pod_runner as pass2runner  # noqa: E402
import reader_v5_pod_runner as runner  # noqa: E402

from market_pulse import pass2, prompts  # noqa: E402

CONFIG = "READER_THINK"

PASS1_OUTPUT_TOKENS = 4000
PASS2_OUTPUT_TOKENS = 8000
"""The registered ceilings of `docs/PROMPT-think-zero-shot.md` D1.1, transcribed and not chosen.

They are the ONLY numbers in this file that are not copied from the shipped pack. A `length` finish
under them is a counted parse failure and never a retry — one attempt per stage — so the ceiling has
to sit above the longest honest answer, and the thinking channel is what makes 256 and 4 000 too
small: the working-out is generated before the first character of the verdict.
"""

SMOKE_DEV_ROWS = 3
"""The contract's smoke: the pack's longest thread (pass 2) plus THREE dev rows. Three and not one
because the smoke's job is a rate, and a rate off one call is a boot."""

SHIPPED = {
    "pass1": REPO_ROOT / "results" / "pass1_dev_pack.json",
    "pass2": REPO_ROOT / "results" / "pass2_r2_pack.json",
}


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_of(path: Path) -> dict:
    """Where every item in the derived pack came from, by path and sha.

    A derived pack that cannot name its source is a pack whose population nobody can check against
    the BEFORE column it is paired with ([[provenance_cannot_name_itself]]).
    """
    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "sha256": sha256_of(path),
        "rule": (
            "every item below is this file's item, unedited. Only serving, instruments and the leg"
            " split are this pack's own — the rows, their ids and their renderings are the shipped"
            " pack's, so the two columns of the paired table are the same population"
        ),
    }


def serving_block(shipped: dict, output_tokens: int) -> dict:
    """The shipped serving block with the instrument swapped — and the two fields kept in step.

    `chat_template` is read out of the runner's own table by the config NAME, so a pack saying
    `READER_THINK` cannot carry the closed-channel template: the record and the run pick their
    template from one place ([[a_shifted_constant_has_physical_consumers]]).
    """
    from market_pulse import local_llm

    return {
        **shipped,
        "serving_config": CONFIG,
        "chat_template": dict(runner.template_of(CONFIG, local_llm)),
        "output_tokens": output_tokens,
        "template_note": (
            "ruling (ф), 2026-08-26: the same registered prompts with the thinking channel OPEN."
            " The generation prompt ends at `<|turn>model` and the model writes its working-out"
            " before the verdict; `prompts.after_thought` is what the parser reads past it with,"
            " and `reader_v5_pod_runner.stops_here` is what keeps the transport stop out of it"
        ),
        "was": {
            "serving_config": shipped.get("serving_config"),
            "chat_template": shipped.get("chat_template"),
            "output_tokens": shipped.get("output_tokens"),
        },
    }


def moved(shipped_instruments: dict, live: dict) -> dict:
    """Which pinned shas this pack carries differently from the shipped one, and why.

    Named rather than silently re-stamped: `results/pass1_dev_pack.json` already carries a
    `moved_from_the_sealed_pack` block of exactly this shape, for exactly this reason one revision
    earlier. A derived pack that quietly re-pinned would be indistinguishable from a pack built
    against a checkout nobody registered.
    """
    was = {}
    for key, value in live.items():
        before = shipped_instruments.get(key)
        if isinstance(before, dict) and isinstance(value, dict):
            before = before.get("sha256", before)
            value = value.get("sha256", value)
        if before != value:
            was[key] = before
    return {
        "was": was,
        "why": (
            "docs/PROMPT-think-zero-shot.md D1.2 teaches prompts.parse_reply to read the answer"
            " AFTER a closed thought channel, so src/market_pulse/prompts.py's sha moved. The"
            " shipped packs and the registrations that pin them are NOT rebuilt — they describe"
            " runs that were already paid for; this pack carries the live shas because the pod's"
            " handshake compares them against this checkout before the model is loaded"
        ),
        "recover": "git show 74f4a81:src/market_pulse/prompts.py",
    }


def checked_renderings(items: list[dict], task: str, render) -> None:
    """Every item re-rendered by THIS checkout against the sha it carries — at $0, before the pod.

    The pod does this too (`check_requests`), and that is the point of doing it here: a renderer
    that moved is a whole billed boot to find out on the pod, and nothing about it needs a GPU.
    """
    for item in items:
        got = hashlib.sha256(render(prompts, item, task).encode("utf-8")).hexdigest()
        if got != item["rendering_sha256"]:
            raise SystemExit(
                f"{item['id']}: this checkout renders {got} and the shipped pack pinned"
                f" {item['rendering_sha256']}. The request moved, so the thinking column would not"
                " be over the same text as the BEFORE column — stop and report."
            )


def pass1_packs(shipped: dict, source: dict) -> dict:
    """The dev-200 pack under READER_THINK, and its three-row smoke.

    Both legs are kept in one pack because `pass1_fewshot_pod_runner` has `--only`: the contract
    buys v2 first and v1 later, and one pack answered twice is one boot's worth of legs, not two.
    """
    live = {
        "parser": {**shipped["instruments"]["parser"], "sha256": sha256_of(PROMPTS_PY)},
        "prompt_sha256": {task: prompts.prompt_sha256(task) for task in sorted(prompts.PASS1)},
    }
    for leg in shipped["legs"]:
        checked_renderings(leg["items"], leg["task"], fewshot.render)

    pack = {
        **shipped,
        "instruments": {**shipped["instruments"], **live},
        "moved_from_the_shipped_pack": moved(shipped["instruments"], live),
        "serving": serving_block(shipped["serving"], PASS1_OUTPUT_TOKENS),
        "source": source,
    }
    v2 = next(leg for leg in shipped["legs"] if leg["name"] == "v2")
    smoke = {
        **pack,
        "legs": [
            {
                **v2,
                "name": "smoke",
                "items": v2["items"][:SMOKE_DEV_ROWS],
                # the v2 leg's OWN out-file: these three rows are answers the leg then resumes
                # over, so the smoke measures the rate without buying a row twice
                "out": v2["out"],
            }
        ],
    }
    return {"pass1_dev_pack_think.json": pack, "pass1_dev_smoke_think.json": smoke}


HOLDOUT = REPO_ROOT / "results" / "pass1_holdout_100.json"
HOLDOUT_SOURCES = (
    ("results/pass1_window_r2_pack.json", "results/pass1_window_r2_v2.jsonl"),
    ("results/pass1_window_pack.json", "results/pass1_window_v2.jsonl"),
)
"""Where each holdout row's BEFORE cell came from, pack beside the replies that answered it.

The holdout is a hundred LABELS (`thread`, `msg_id`, `subject_type`) and not a pack, so its v2
column had to be traced rather than transcribed. It is two files: the r2 window answered 88 of the
100 and the r1 window the other 12, disjoint, 56 + 8 = the 64 the contract cites. Each row's item is
taken from the pack whose replies produced ITS cell, so the thinking column is over the same
rendered request the BEFORE column was — which is the whole meaning of «identical rows»
([[trace_the_producer_not_the_result]]).
"""


def holdout_pack(source: dict) -> dict:
    """The hundred holdout rows as ONE pass-1 leg, each item from the pack that answered it."""
    units = json.loads(HOLDOUT.read_text(encoding="utf-8"))["units"]
    wanted = {(one["thread"], int(one["msg_id"])) for one in units}
    items, seen, task, base, from_ = [], set(), None, None, {}
    for pack_path, replies_path in HOLDOUT_SOURCES:
        pack = json.loads((REPO_ROOT / pack_path).read_text(encoding="utf-8"))
        base = base or pack
        leg = next(one for one in pack["legs"] if one["name"] == "v2")
        task = task or leg["task"]
        if leg["task"] != task:
            raise SystemExit(f"{pack_path}: leg v2 renders {leg['task']}, not {task} — stop.")
        by_id = {one["id"]: one for one in leg["items"]}
        for line in (REPO_ROOT / replies_path).read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            item = by_id.get(json.loads(line)["id"])
            key = item and (item["thread"], int(item["msg_id"]))
            if key in wanted and key not in seen:
                seen.add(key)
                items.append(item)
                from_[item["id"]] = replies_path
    if len(items) != len(units):
        raise SystemExit(
            f"{len(items)} of {len(units)} holdout rows found in the two window packs — the BEFORE"
            " column and the thinking column would be over different populations. Stop and report."
        )
    checked_renderings(items, task, fewshot.render)
    live = {
        "parser": {**base["instruments"]["parser"], "sha256": sha256_of(PROMPTS_PY)},
        "prompt_sha256": {one: prompts.prompt_sha256(one) for one in sorted(prompts.PASS1)},
    }
    return {
        **base,
        "instruments": {**base["instruments"], **live},
        "moved_from_the_shipped_pack": moved(base["instruments"], live),
        "serving": serving_block(base["serving"], PASS1_OUTPUT_TOKENS),
        "source": source,
        "before_column": {
            "labels": "results/pass1_holdout_100.json",
            "labels_sha256": sha256_of(HOLDOUT),
            "answered_by": from_,
            "rule": (
                "each row's item comes from the pack whose replies produced its BEFORE cell, so"
                " both columns are over the same rendered request"
            ),
        },
        "legs": [
            {
                "name": "holdout",
                "task": task,
                "items": items,
                "out": "pass1_holdout_100_v2.jsonl",
            }
        ],
    }


def pass2_packs(shipped: dict, source: dict) -> dict:
    """The 79 threads under READER_THINK, split into the reference leg, the remainder and a smoke.

    The split is read off the pack's own `membership` and never retyped: a thread is a reference
    thread here exactly when the shipped pack says it carries an E, F or N case, which is the set
    the shipped gate reads its three bars from.
    """
    live = {
        "parser": {**shipped["instruments"]["parser"], "sha256": sha256_of(PROMPTS_PY)},
        "module": {**shipped["instruments"]["module"], "sha256": sha256_of(PASS2_PY)},
        "module_r2": {**shipped["instruments"]["module_r2"], "sha256": sha256_of(PASS2_R2_PY)},
        "prompt_sha256": {task: pass2.prompt_sha256(task) for task in sorted(pass2.PASS2)},
    }
    (leg,) = shipped["legs"]
    checked_renderings(leg["items"], leg["task"], pass2runner.render)

    def is_reference(item: dict) -> bool:
        return any(item["membership"][kind] for kind in ("E", "F", "N"))

    reference = [one for one in leg["items"] if is_reference(one)]
    remainder = [one for one in leg["items"] if not is_reference(one)]
    longest = max(leg["items"], key=lambda one: one["rendered_chars"])

    base = {
        **shipped,
        "instruments": {**shipped["instruments"], **live},
        "moved_from_the_shipped_pack": moved(shipped["instruments"], live),
        "serving": serving_block(shipped["serving"], PASS2_OUTPUT_TOKENS),
        "source": source,
        "carried": {
            "ids": [],
            "from": None,
            "units": 0,
            "rule": (
                "NOTHING is carried. r1's four rows were answered with the thought channel CLOSED,"
                " and seeding them into a thinking out-file would put four BEFORE-column replies"
                " into the thinking column of a paired table"
                " ([[a_retry_inherits_the_last_attempts_output]])"
            ),
        },
        "reference_split": {
            "rule": (
                "read off this pack's own `membership`: a thread is a reference thread when the"
                " shipped pack says it carries an E, F or N case"
            ),
            "reference": len(reference),
            "remainder": len(remainder),
            "sixteen": (
                "the contract's «16 reference threads» counts the 16 threads named in"
                " `membership.per_kind` AND `membership.cases_outside_the_population`; only"
                f" {len(reference)} of them are in this pack's 79 — the other five"
                " (@matusi_ukr:22242, @retsepty:7312/7325/7327, @sashafitnesslife:3939) were"
                " outside the r2 population and were never bought by the run this is paired"
                f" against either. So the split here is {len(reference)} + {len(remainder)} = 79,"
                " not 16 + 63"
            ),
        },
    }

    def one_leg(name: str, items: list[dict], out: str) -> dict:
        return {
            **base,
            "legs": [{**leg, "name": name, "items": items, "out": out}],
            "owed": {
                **shipped["owed"],
                "ids": [one["id"] for one in items],
                "units": len(items),
            },
        }

    reference_out, remainder_out = (
        "pass2_signals_r2_reference.jsonl",
        "pass2_signals_r2_remainder.jsonl",
    )
    smoke_out = reference_out if is_reference(longest) else remainder_out
    return {
        "pass2_r2_pack_think_reference.json": one_leg("reference", reference, reference_out),
        "pass2_r2_pack_think_remainder.json": one_leg("remainder", remainder, remainder_out),
        # one item, writing into the out-file of the leg it belongs to
        "pass2_r2_pack_think_smoke.json": one_leg("smoke", [longest], smoke_out),
    }


PROMPTS_PY = REPO_ROOT / "src" / "market_pulse" / "prompts.py"
PASS2_PY = REPO_ROOT / "src" / "market_pulse" / "pass2.py"
PASS2_R2_PY = REPO_ROOT / "src" / "market_pulse" / "pass2_r2.py"


def build() -> dict:
    packs = {}
    for family, path in SHIPPED.items():
        shipped = json.loads(path.read_text(encoding="utf-8"))
        source = source_of(path)
        packs |= (pass1_packs if family == "pass1" else pass2_packs)(shipped, source)
    packs["pass1_holdout_100_think.json"] = holdout_pack(
        {
            "path": [pack for pack, _ in HOLDOUT_SOURCES],
            "sha256": {pack: sha256_of(REPO_ROOT / pack) for pack, _ in HOLDOUT_SOURCES},
            "rule": (
                "TWO source packs, because the holdout's v2 column is two files: the r2 window"
                " answered 88 of the 100 rows and the r1 window the other 12"
            ),
        }
    )
    return packs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=REPO_ROOT / "results")
    args = parser.parse_args(argv)
    args.outdir.mkdir(parents=True, exist_ok=True)
    for name, pack in build().items():
        out = args.outdir / name
        out.write_text(json.dumps(pack, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
        legs = ", ".join(f"{leg['name']}={len(leg['items'])}→{leg['out']}" for leg in pack["legs"])
        print(f"{out}  {legs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
