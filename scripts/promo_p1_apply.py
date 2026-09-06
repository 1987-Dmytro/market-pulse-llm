#!/usr/bin/env python3
"""P1 over the EXISTING predictions of the three dev sets, K8 v2 before and after — $0, no pod.

Ruling 06.09 (bb) addendum (b), item (4): the layer `market_pulse.promo_post` is applied to the rows
the frozen reader already wrote — dev-40 (iteration 5, 139 rows), dev-2 (iteration 5, 188 rows)
and dev-3 (the spent holdout-2, 112 rows) — and each set is graded by K8 v2 twice, before and
after, over the SAME gold, the SAME draw arm and the same functions of
`scripts/grade_promo_signals.py`. The numbers are the grader's; this script invents none
([[a_number_typed_into_its_own_checker]]).

What the record says beyond the six numbers:

* which rule rewrote how many rows, per set — a rule that fires nowhere is a rule with no evidence;
  and a signal reading that MOVED would mean the layer touched a field it may not, so it is refused;
* the leak check — the lexicon and the rules were written from the codebook and the three DEV error
  tables, and the holdout-3 draw (`results/promo_threads_draw_3.json`) shares no thread with any
  file this script opened: its 40 threads were never read, here or anywhere;
* the decision table of PHASE v18 §6.2, evaluated: the holdout-3 shot is bought only if P1's dev-3
  subject reading ≥ 0.80 AND dev-40 and dev-2 stay ≥ their bars — otherwise the fork returns to the
  operator with these numbers, at $0.

The record carries no clock and no git block: two runs are byte-identical.

    PYTHONPATH=src python3.11 scripts/promo_p1_apply.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

import grade_promo_signals as k8  # noqa: E402
from market_pulse import promo_post  # noqa: E402
from market_pulse.registry import chain_spellings, load_registry  # noqa: E402

REGISTRY = REPO_ROOT / "config" / "registry.yaml"
P1 = REPO_ROOT / "src" / "market_pulse" / "promo_post.py"
DRAW_3 = REPO_ROOT / "results" / "promo_threads_draw_3.json"
OUT = REPO_ROOT / "results" / "grade_promo_p1_readings.json"

SETS = {
    "dev40": {
        "read_as": "dev-40 — iteration 5's BAR set: 139 gold rows over the first draw's dev arm",
        "predicted": "results/promo_dev40_predicted_iter5.jsonl",
        "gold": "docs/labels-promo-dev.jsonl",
        "draw": "results/promo_threads_draw.json",
        "part": "dev",
        "pack": "results/promo_dev40_pack.json",
    },
    "dev2": {
        "read_as": "dev-2 — the spent holdout-40, a reading: 188 gold rows over the first draw's"
        " holdout arm",
        "predicted": "results/promo_dev2_predicted_iter5.jsonl",
        "gold": "docs/labels-promo-dev2.jsonl",
        "draw": "results/promo_threads_draw.json",
        "part": "holdout",
        "pack": "results/promo_dev40_pack.json",
    },
    "dev3": {
        "read_as": "dev-3 — the spent holdout-2, the set the decision table reads: 112 gold rows"
        " over the second draw's holdout arm",
        "predicted": "results/promo_holdout2_predicted.jsonl",
        "gold": "docs/labels-promo-holdout2.jsonl",
        "draw": "results/promo_threads_draw_2.json",
        "part": "holdout",
        "pack": "results/promo_holdout2_pack.json",
    },
}
"""The three sets the addendum names, each with the gold, draw arm and pack ITS reading was taken
over — the same triple `promo_dev_pass.py --score` graded, so «before» here is the committed number."""

ERROR_TABLES = (
    "results/promo_dev40_errors_iter5.json",
    "results/promo_dev2_errors_iter5.json",
    "results/promo_holdout2_errors.json",
)
"""Where the lexicon's evidence came from — the three DEV error tables the addendum allows."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def thread_of(item: dict) -> dict:
    """What the reader saw, from the pack it was served: channel, root, post text, comment texts."""
    return {
        "channel": item["channel"],
        "thread_root": str(item["post_id"]),
        "post": item["post"],
        "comments": {str(msg_id): text for msg_id, text, *_ in item["comments"]},
    }


def reading(grade: dict) -> dict:
    """The grade's numbers, and only the numbers — the definitions live in the grader's record."""
    whole = grade["whole_40"]
    return {
        "subject_agreement": whole["subject_agreement"],
        "subject_agreed": whole["subject_agreed"],
        "subject_comments": whole["subject_comments"],
        "signal_type_agreement": whole["signal_type_agreement"],
        "by_stratum": {
            stratum: {
                "subject_agreement": block["subject_agreement"],
                "subject_agreed": block["subject_agreed"],
                "subject_comments": block["subject_comments"],
                "signal_type_agreement": block["signal_type_agreement"],
            }
            for stratum, block in grade["by_stratum"].items()
            if isinstance(block, dict) and "subject_agreement" in block
        },
    }


def misses(gold: list[dict], predicted: list[dict]) -> dict:
    """The gold comments the grader scores as misses, and how many the gold itself declared a tie.

    Ruling 06.09 (cc) item 2 and PHASE v19: «the numbers and the tie analysis on the screen and in
    the README from result files» — so the count lives in this record, taken with the grader's ONE
    predicate (`subjects_agree`) over the grader's own denominator, never re-derived by the screen.
    A tie is the GOLD row's `unsure` field — the team lead's «either reading is defensible», written
    blind when the gold was — and not a judgement of this script.
    """
    said = {(k8.thread_key(row), str(row.get("msg_id"))): row for row in predicted if row.get("msg_id")}
    missed = []
    for row in gold:
        if not row.get("msg_id"):
            continue
        found = said.get((k8.thread_key(row), str(row["msg_id"])))
        if found is None or not k8.subjects_agree(row, found):
            missed.append(row)
    return {
        "total": len(missed),
        "gold_unsure": sum(1 for row in missed if row.get("unsure")),
        "rule": "a miss is a gold comment `subjects_agree` refuses, or one the reader said nothing"
        " about — the grader's own predicate; `gold_unsure` counts the misses whose GOLD row carries"
        " `unsure`: the codebook's declared ties, where two readings are defensible",
    }


def rewrite(name: str, spec: dict, registry, spellings) -> tuple[dict, set[tuple[str, str]]]:
    """One set through P1: the after-file written, both grades taken, the rules counted."""
    predicted, gold_path = REPO_ROOT / spec["predicted"], REPO_ROOT / spec["gold"]
    pack_path, draw_path = REPO_ROOT / spec["pack"], REPO_ROOT / spec["draw"]
    rows = k8.rows(predicted)
    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    threads = {item["id"]: thread_of(item) for item in pack["items"] if item["leg"] == "a"}
    after_rows = []
    for row in rows:
        key = f"{row['channel']}:{row['thread_root']}"
        if key not in threads:
            raise SystemExit(
                f"{name}: row {key}/{row.get('msg_id')} has no thread in {spec['pack']} — P1 reads"
                " what the reader read, and this row's thread is not there"
            )
        after_rows += promo_post.apply([row], threads[key], registry, spellings)
    out = REPO_ROOT / "results" / f"promo_p1_predicted_{name}.jsonl"
    out.write_text(
        "".join(json.dumps(one, ensure_ascii=False, sort_keys=True) + "\n" for one in after_rows),
        encoding="utf-8",
    )

    gold = k8.rows(gold_path)
    strata = k8.strata_of(draw_path, spec["part"])
    before, after = k8.grade(gold, rows, strata), k8.grade(gold, after_rows, strata)
    if after["whole_40"]["signal_type_agreement"] != before["whole_40"]["signal_type_agreement"]:
        raise SystemExit(
            f"{name}: the signal reading moved under P1 — the layer touched a field it may not"
        )
    fired = Counter(rule for one in after_rows for rule in one.get("p1", []))
    missed = {"before": misses(gold, rows), "after": misses(gold, after_rows)}
    for leg, grade in (("before", before), ("after", after)):
        whole = grade["whole_40"]
        if missed[leg]["total"] != whole["subject_comments"] - whole["subject_agreed"]:
            raise SystemExit(
                f"{name}: the {leg} miss count {missed[leg]['total']} is not the grade's own"
                f" {whole['subject_comments']} - {whole['subject_agreed']} — two readings of one"
                " predicate disagree"
            )
    opened = {(item["channel"], str(item["post_id"])) for item in pack["items"]}
    block = {
        "read_as": spec["read_as"],
        "gold": {"path": spec["gold"], "sha256": sha256(gold_path)},
        "draw": {"path": spec["draw"], "part": spec["part"]},
        "pack": {"path": spec["pack"], "sha256": sha256(pack_path), "threads": len(opened)},
        "predicted_before": {"path": spec["predicted"], "sha256": sha256(predicted)},
        "predicted_after": {"path": str(out.relative_to(REPO_ROOT)), "sha256": sha256(out)},
        "rows": len(rows),
        "rewritten_rows": sum(1 for one in after_rows if one.get("p1")),
        "fired": {rule: fired.get(rule, 0) for rule in ("R1", "R2", "R3")},
        "before": reading(before),
        "after": reading(after),
        "misses_before": missed["before"],
        "misses_after": missed["after"],
        "delta": {
            key: round(after["whole_40"][key] - before["whole_40"][key], 4)
            for key in ("subject_agreement", "signal_type_agreement")
        },
        "bars_after": {
            key: {"bar": bar, "value": after["whole_40"][key], "held": after["bars"][key]["held"]}
            for key, bar in k8.BARS.items()
        },
    }
    return block, opened


def leak_check(draw_3: Path, opened: set[tuple[str, str]], files: list[str]) -> dict:
    """Holdout-3 was never opened: its threads share nothing with any file this reading read."""
    if not draw_3.exists():
        raise SystemExit(f"{draw_3} is missing — the leak check has nothing to check against")
    body = json.loads(draw_3.read_text(encoding="utf-8"))
    holdout3 = {
        (row["channel"], str(row["thread_root"]))
        for block in body["draw"].values()
        for row in block["holdout"]
    }
    shared = sorted(holdout3 & opened)
    if shared:
        raise SystemExit(
            f"LEAK: {len(shared)} holdout-3 threads were opened by this reading: {shared}"
        )
    return {
        "holdout3_draw": {
            "path": str(draw_3.relative_to(REPO_ROOT)),
            "sha256": sha256(draw_3),
            "threads": len(holdout3),
        },
        "files_opened": sorted(files),
        "threads_opened": len(opened),
        "holdout3_threads_shared_with_them": len(shared),
        "lexicon": {
            "words": list(promo_post.STORE_STOCK_LEXICON),
            "match": "at a word start, as a prefix, on the comment's text after aggregates.promo_key",
            "from": "ruling 06.09 (bb) addendum item (3), verbatim — the codebook's words (§3"
            " «наличие в магазине») and the three DEV error tables; no holdout-3 thread was read",
            "error_tables": {path: sha256(REPO_ROOT / path) for path in ERROR_TABLES},
        },
    }


def decision_table(sets: dict) -> dict:
    """PHASE v18 §6.2, evaluated on the after-readings — the pre-registered rule, not a new one."""
    bars = k8.BARS
    conditions = {
        "dev3 subject_agreement >= 0.80 after P1": (
            sets["dev3"]["after"]["subject_agreement"] >= bars["subject_agreement"]
        ),
        "dev40 stays >= its bars after P1": all(
            block["held"] for block in sets["dev40"]["bars_after"].values()
        ),
        "dev2 stays >= its bars after P1": all(
            block["held"] for block in sets["dev2"]["bars_after"].values()
        ),
    }
    failed = [name for name, held in conditions.items() if not held]
    return {
        "authority": "PHASE-promo-pulse-1.md §6.2 v18 / ruling 06.09 (bb) addendum: the holdout-3"
        " shot is bought only if P1's dev-3 subject reading >= 0.80 AND dev-40 / dev-2 stay >= their"
        " bars; otherwise the fork returns to the operator at $0 (ship as measured · codebook v1.3)",
        "conditions": conditions,
        "holdout3_shot": not failed,
        "reads": "BUY — every condition holds; the shot goes to its own registration"
        if not failed
        else "RETURN to the operator at $0 — failed: " + "; ".join(failed),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draw3", type=Path, default=DRAW_3)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)

    registry = load_registry(REGISTRY)
    spellings = chain_spellings()
    sets, opened, files = {}, set(), []
    for name, spec in SETS.items():
        sets[name], threads = rewrite(name, spec, registry, spellings)
        opened |= threads
        files += [spec["predicted"], spec["gold"], spec["pack"], spec["draw"]]
    record = {
        "contract": "docs/PHASE-promo-pulse-1.md §6.2 v18 · ruling 06.09 (bb) addendum item (4) —"
        " P1 measured at $0 on the three dev sets, K8 v2 before and after",
        "k8_version": k8.K8_VERSION,
        "p1": {
            "module": str(P1.relative_to(REPO_ROOT)),
            "sha256": sha256(P1),
            "rules": "R1 post => subject = thread root · R2 own channel: post with signals => chain"
            " = owner · R3 sku/brand with жалоба on the store-stock lexicon => chain = the thread's"
            " retailer — nothing else",
        },
        "sets": sets,
        "leak_check": leak_check(args.draw3, opened, sorted(set(files))),
        "decision_table": decision_table(sets),
    }
    args.out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(
        f"{'set':<6} {'rows':>4}  {'subject before → after':<28} {'signal':<16} R1  R2  R3  rewritten"
    )
    for name, block in sets.items():
        b, a, d = block["before"], block["after"], block["delta"]
        print(
            f"{name:<6} {block['rows']:>4}  {b['subject_agreement']:.4f} → {a['subject_agreement']:.4f}"
            f" ({d['subject_agreement']:+.4f})      {b['signal_type_agreement']:.4f} → "
            f"{a['signal_type_agreement']:.4f}  "
            + "  ".join(f"{block['fired'][rule]:>2}" for rule in ("R1", "R2", "R3"))
            + f"  {block['rewritten_rows']:>3}"
        )
        for stratum in sorted(a["by_stratum"]):
            print(
                f"       {stratum:<13} subject {b['by_stratum'][stratum]['subject_agreement']:.4f} →"
                f" {a['by_stratum'][stratum]['subject_agreement']:.4f}  (reading, no bar)"
            )
        mb, ma = block["misses_before"], block["misses_after"]
        print(
            f"       misses {mb['total']} → {ma['total']}, of them the gold's own ties (`unsure`)"
            f" {mb['gold_unsure']} → {ma['gold_unsure']}"
        )
    table = record["decision_table"]
    for name, held in table["conditions"].items():
        print(f"  [{'x' if held else ' '}] {name}")
    print(f"decision table: {table['reads']}")
    leak = record["leak_check"]
    print(
        f"leak check: holdout-3 {leak['holdout3_draw']['threads']} threads,"
        f" {leak['holdout3_threads_shared_with_them']} shared with the"
        f" {leak['threads_opened']} threads this reading opened"
    )
    print(
        f"wrote {args.out.relative_to(REPO_ROOT) if args.out.is_relative_to(REPO_ROOT) else args.out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
