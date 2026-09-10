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

**The SECOND leg, ruling 08.09 (dd) item 5: the same three sets through the PRODUCT's own
pipeline.** Every reading above graded `promo_dev_pass.predicted_rows` built from the model's RAW
answer, while the product screens each answer through the four hooks of §2 S4 before P1 ever sees
it — so the number the screen ships is the product's, measured end to end by the product's own
functions: `promo_prompts.parse` -> `promo_hooks.screen` -> a record shaped exactly as
`tick.signal_records` reads it -> `tick.p1_rows` -> `promo_dev_pass.predicted_rows` -> K8 v2. It
goes to `results/grade_promo_loop_readings.json`, beside the readings and never over them: the
pre-registered readings stay the bar's record and no record of theirs is widened (PHASE v20 §6.7).

Both records carry no clock and no git block: two runs are byte-identical.

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
import promo_dev_pass  # noqa: E402
import tick  # noqa: E402
from market_pulse import promo_hooks, promo_post, promo_prompts  # noqa: E402
from market_pulse.registry import chain_spellings, load_registry  # noqa: E402

REGISTRY = REPO_ROOT / "config" / "registry.yaml"
P1 = REPO_ROOT / "src" / "market_pulse" / "promo_post.py"
HOOKS = REPO_ROOT / "src" / "market_pulse" / "promo_hooks.py"
DRAW_3 = REPO_ROOT / "results" / "promo_threads_draw_3.json"
OUT = REPO_ROOT / "results" / "grade_promo_p1_readings.json"
LOOP_OUT = REPO_ROOT / "results" / "grade_promo_loop_readings.json"

SETS = {
    "dev40": {
        "read_as": "dev-40 — iteration 5's BAR set: 139 gold rows over the first draw's dev arm",
        "predicted": "results/promo_dev40_predicted_iter5.jsonl",
        "gold": "docs/labels-promo-dev.jsonl",
        "draw": "results/promo_threads_draw.json",
        "part": "dev",
        "pack": "results/promo_dev40_pack.json",
        "replies": "results/promo_dev40_iter5.jsonl",
    },
    "dev2": {
        "read_as": "dev-2 — the spent holdout-40, a reading: 188 gold rows over the first draw's"
        " holdout arm",
        "predicted": "results/promo_dev2_predicted_iter5.jsonl",
        "gold": "docs/labels-promo-dev2.jsonl",
        "draw": "results/promo_threads_draw.json",
        "part": "holdout",
        "pack": "results/promo_dev40_pack.json",
        "replies": "results/promo_dev40_iter5.jsonl",
    },
    "dev3": {
        "read_as": "dev-3 — the spent holdout-2, the set the decision table reads: 112 gold rows"
        " over the second draw's holdout arm",
        "predicted": "results/promo_holdout2_predicted.jsonl",
        "gold": "docs/labels-promo-holdout2.jsonl",
        "draw": "results/promo_threads_draw_2.json",
        "part": "holdout",
        "pack": "results/promo_holdout2_pack.json",
        "replies": "results/promo_holdout2.jsonl",
    },
}
"""The three sets the addendum names, each with the gold, draw arm and pack ITS reading was taken
over — the same triple `promo_dev_pass.py --score` graded, so «before» here is the committed number.
`replies` is the pod out-file those predictions were parsed out of: the loop leg starts one step
earlier than the reading did, at the RAW answer, and both legs must start from the same one."""

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


def graded(name: str, spec: dict, before_rows: list[dict], after_rows: list[dict]) -> dict:
    """K8 v2 over one set's rows before and after P1 — the block BOTH legs of this script write.

    One grader, one denominator, one miss predicate for the reading and for the loop alike: two
    gates over one spend that read different corners is how a record ends up disagreeing with
    itself ([[two_gates_on_one_spend_read_different_corners]]). `before` and `after` mean the same
    thing in both legs — before and after P1 — and in the loop leg the hooks have already run on
    both sides, so «the signal reading may not move» stays P1's own invariant and is refused here.
    """
    gold_path, draw_path = REPO_ROOT / spec["gold"], REPO_ROOT / spec["draw"]
    gold = k8.rows(gold_path)
    strata = k8.strata_of(draw_path, spec["part"])
    before, after = k8.grade(gold, before_rows, strata), k8.grade(gold, after_rows, strata)
    if after["whole_40"]["signal_type_agreement"] != before["whole_40"]["signal_type_agreement"]:
        raise SystemExit(
            f"{name}: the signal reading moved under P1 — the layer touched a field it may not"
        )
    missed = {"before": misses(gold, before_rows), "after": misses(gold, after_rows)}
    for leg, grade in (("before", before), ("after", after)):
        whole = grade["whole_40"]
        if missed[leg]["total"] != whole["subject_comments"] - whole["subject_agreed"]:
            raise SystemExit(
                f"{name}: the {leg} miss count {missed[leg]['total']} is not the grade's own"
                f" {whole['subject_comments']} - {whole['subject_agreed']} — two readings of one"
                " predicate disagree"
            )
    return {
        "gold": {"path": spec["gold"], "sha256": sha256(gold_path)},
        "draw": {"path": spec["draw"], "part": spec["part"]},
        "rows": len(before_rows),
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


def rewrite(name: str, spec: dict, registry, spellings) -> tuple[dict, set[tuple[str, str]]]:
    """One set through P1: the after-file written, both grades taken, the rules counted."""
    predicted = REPO_ROOT / spec["predicted"]
    pack_path = REPO_ROOT / spec["pack"]
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

    fired = Counter(rule for one in after_rows for rule in one.get("p1", []))
    opened = {(item["channel"], str(item["post_id"])) for item in pack["items"]}
    block = {
        "read_as": spec["read_as"],
        "pack": {"path": spec["pack"], "sha256": sha256(pack_path), "threads": len(opened)},
        "predicted_before": {"path": spec["predicted"], "sha256": sha256(predicted)},
        "predicted_after": {"path": str(out.relative_to(REPO_ROOT)), "sha256": sha256(out)},
        "rewritten_rows": sum(1 for one in after_rows if one.get("p1")),
        "fired": {rule: fired.get(rule, 0) for rule in ("R1", "R2", "R3")},
        **graded(name, spec, rows, after_rows),
    }
    return block, opened


def comments_of(item: dict) -> list[dict]:
    """The pack's comments in the shape `promo_hooks.screen` reads — the rows the model was shown."""
    return [{"msg_id": str(msg_id), "text": text} for msg_id, text, *_ in item["comments"]]


def arm_units(spec: dict) -> dict:
    """The pack items of THIS set's arm, by unit id.

    The ARM, never the whole pack: one out-file carries both arms of a leg since iteration 4, and
    grading 80 answers against a key covering 40 would call the result the leg's
    ([[measure_on_the_rows_the_gate_scores]]).
    """
    pack = json.loads((REPO_ROOT / spec["pack"]).read_text(encoding="utf-8"))
    arm = k8.strata_of(REPO_ROOT / spec["draw"], spec["part"])
    return {
        item["id"]: item
        for item in pack["items"]
        if item["leg"] == "a" and (item["channel"], str(item["post_id"])) in arm
    }


def screened(spec: dict, brand_ids: set, vocabulary: dict):
    """Every answered thread of one set's arm, as `tick.signal_records` reads one.

    `(item, answer, record)` per thread: the pack item the reader was served, the parsed raw answer,
    and the record — the screen function's own return plus the three fields it does not know
    (`channel`, `thread_root`, `extractor_version`).

    Lifted out of :func:`loop` so that the producer which PROMOTES these records into
    `results/promo_signals/` writes the very rows the loop leg grades. A second spelling of the
    parse → screen → record path would measure a third thing
    ([[a_moved_guard_that_left_its_copy]]).
    """
    units = arm_units(spec)
    for reply in promo_dev_pass.reply_rows(REPO_ROOT / spec["replies"]):
        item = units.get(reply.get("id"))
        if item is None:
            continue  # the other arm of this out-file, and the leg's gold does not cover it
        if promo_dev_pass.died(reply):
            continue  # a unit that DIED is unanswered, not an answer that failed to parse
        answer = promo_prompts.parse(reply["reply"])
        record = {
            **promo_hooks.screen(answer, comments_of(item), brand_ids, vocabulary),
            "channel": item["channel"],
            "thread_root": str(item["post_id"]),
            "extractor_version": reply["rendering_sha256"],
        }
        yield item, answer, record


def loop(name, spec, registry, spellings, brand_ids, vocabulary) -> tuple[dict, set[tuple[str, str]]]:
    """One set through the PRODUCT's pipeline — ruling 08.09 (dd) item 5, at $0.

    The reading above graded the model's RAW answer; the product screens that answer through the
    four hooks of §2 S4 first, so a row whose quote is not a substring of its comment never reaches
    P1 and its signal type never reaches the rows P1 reads. Every step here is the shipped function
    CALLED — `promo_prompts.parse`, `promo_hooks.screen`, `tick.p1_rows`,
    `promo_dev_pass.predicted_rows`, the grader — never a second spelling of it, because a second
    spelling measures a third thing ([[a_moved_guard_that_left_its_copy]]).

    The record a thread builds here is shaped exactly as `tick.signal_records` reads one: the screen
    function's own return plus the three fields it does not know (`channel`, `thread_root`,
    `extractor_version`). The `unsure` comments it carries are NOT graded rows — the tick writes
    them to its own table — and they are counted so the class is visibly empty rather than silently
    dropped ([[empty_class_eats_the_parse_failures]]).
    """
    pack_path, replies_path = REPO_ROOT / spec["pack"], REPO_ROOT / spec["replies"]
    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    units = arm_units(spec)
    counts: Counter = Counter()
    rows_in: Counter = Counter()
    rows_kept: Counter = Counter()
    dropped: list[dict] = []
    p1 = dict.fromkeys(("R1", "R2", "R3", "rows_seen", "rows_rewritten"), 0)
    before_rows, after_rows, answered = [], [], []
    parse_failures, unsure_comments = 0, 0
    for item, answer, record in screened(spec, brand_ids, vocabulary):
        answered.append(item["id"])
        parse_failures += 1 if answer["parse_failure"] else 0
        unsure_comments += len(record["unsure"])
        for kind, key in (("about", "about"), ("signal", "signals")):
            rows_in[kind] += len(answer[key])
            rows_kept[kind] += len(record["kept"][kind])
        counts.update(record["counts"])
        dropped += [
            {
                "channel": item["channel"],
                "thread_root": str(item["post_id"]),
                "msg_id": str(failure["msg_id"]),
                "kind": failure["kind"],
                "hook": failure["hook"],
            }
            for failure in record["failures"]
        ]
        about, signal = tick.p1_rows(record, thread_of(item), registry, spellings)
        for row in about + signal:
            p1["rows_seen"] += 1
            p1["rows_rewritten"] += 1 if row.get("p1") else 0
            for rule in row.get("p1") or []:
                p1[rule] += 1
        where = {"channel": item["channel"], "thread_root": item["post_id"]}
        stamp = {"extractor_version": record["extractor_version"]}
        kept = record["kept"]
        before_rows += [
            one | stamp
            for one in promo_dev_pass.predicted_rows(
                where, {"about": kept["about"], "signals": kept["signal"]}
            )
        ]
        after_rows += [
            one | stamp
            for one in promo_dev_pass.predicted_rows(where, {"about": about, "signals": signal})
        ]

    opened = {(item["channel"], str(item["post_id"])) for item in pack["items"]}
    block = {
        "read_as": spec["read_as"],
        "replies": {"path": spec["replies"], "sha256": sha256(replies_path)},
        "pack": {"path": spec["pack"], "sha256": sha256(pack_path), "threads": len(opened)},
        "answers": {
            "units_registered": len(units),
            "units_answered": len(answered),
            "units_dead": [one for one in promo_dev_pass.dead_units(replies_path) if one in units],
            "parse_failures": parse_failures,
            "unsure_comments": unsure_comments,
            "unsure_note": "an `unsure` comment is not a graded row here: the tick routes it to its"
            " own table, and the count says the class is empty rather than ignored",
        },
        "hooks": {
            "module": str(HOOKS.relative_to(REPO_ROOT)),
            "sha256": sha256(HOOKS),
            "counts": {hook: counts.get(hook, 0) for hook in promo_hooks.HOOKS},
            "rows_in": {kind: rows_in[kind] for kind in ("about", "signal")},
            "rows_kept": {kind: rows_kept[kind] for kind in ("about", "signal")},
            "rows_dropped": {kind: rows_in[kind] - rows_kept[kind] for kind in ("about", "signal")},
            "dropped": sorted(dropped, key=lambda one: tuple(sorted(one.items()))),
        },
        "p1": p1,
        **graded(name, spec, before_rows, after_rows),
    }
    return block, opened


def holdout3_disjoint(draw_3: Path, opened: set[tuple[str, str]], files: list[str]) -> dict:
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
    }


def leak_check(draw_3: Path, opened: set[tuple[str, str]], files: list[str]) -> dict:
    """The disjointness above, plus where P1's lexicon came from — the READING leg's block.

    Split from :func:`holdout3_disjoint` so the loop leg can make the same claim over its own files
    (it opens the pod out-files the reading did not) without growing this one: the reading's record
    is an accepted artifact whose sha ruling 06.09 (cc) quotes, and a re-emission that moved it
    would rewrite an accepted number's provenance ([[a_frozen_record_is_a_live_input]]).
    """
    return holdout3_disjoint(draw_3, opened, files) | {
        "lexicon": {
            "words": list(promo_post.STORE_STOCK_LEXICON),
            "match": "at a word start, as a prefix, on the comment's text after aggregates.promo_key",
            "from": "ruling 06.09 (bb) addendum item (3), verbatim — the codebook's words (§3"
            " «наличие в магазине») and the three DEV error tables; no holdout-3 thread was read",
            "error_tables": {path: sha256(REPO_ROOT / path) for path in ERROR_TABLES},
        }
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


def p1_counts(block: dict) -> tuple[dict, str]:
    """(rules fired, rows rewritten) for one set's block, whichever leg wrote it.

    The reading counts GOLD-SHAPED rows (one per comment the model placed, which is the `rows`
    column beside it); the loop counts the READER rows the tick hands P1 — the `about` rows and the
    `signal` rows alike, which is a different and larger space. So the loop's count is printed OVER
    its own denominator: `7` beside `112` reads as «7 of 112» and would say the layer rewrote more
    here than in the reading, when it rewrote fewer gold rows
    ([[one_constant_answering_two_questions]])."""
    if "fired" in block:
        return block["fired"], str(block["rewritten_rows"])
    fired = {rule: block["p1"][rule] for rule in ("R1", "R2", "R3")}
    return fired, f"{block['p1']['rows_rewritten']}/{block['p1']['rows_seen']}"


def print_sets(sets: dict) -> None:
    """The per-set table — the same columns for the reading and for the loop, from the same block."""
    print(
        f"{'set':<6} {'rows':>4}  {'subject before → after':<28} {'signal':<16} R1  R2  R3  rewritten"
    )
    for name, block in sets.items():
        b, a, d = block["before"], block["after"], block["delta"]
        fired, rewritten = p1_counts(block)
        print(
            f"{name:<6} {block['rows']:>4}  {b['subject_agreement']:.4f} → {a['subject_agreement']:.4f}"
            f" ({d['subject_agreement']:+.4f})      {b['signal_type_agreement']:.4f} → "
            f"{a['signal_type_agreement']:.4f}  "
            + "  ".join(f"{fired[rule]:>2}" for rule in ("R1", "R2", "R3"))
            + f"  {rewritten:>7}"
        )
        if "hooks" in block:
            hooks = block["hooks"]
            caught = ", ".join(f"{hook} {n}" for hook, n in hooks["counts"].items() if n) or "none"
            print(
                f"       hooks dropped {hooks['rows_dropped']['about']} about /"
                f" {hooks['rows_dropped']['signal']} signal rows of"
                f" {hooks['rows_in']['about']} / {hooks['rows_in']['signal']} — caught by: {caught}"
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draw3", type=Path, default=DRAW_3)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--loop-out", type=Path, default=LOOP_OUT)
    args = parser.parse_args(argv)

    registry = load_registry(REGISTRY)
    spellings = chain_spellings()
    p1_module = {
        "module": str(P1.relative_to(REPO_ROOT)),
        "sha256": sha256(P1),
        "rules": "R1 post => subject = thread root · R2 own channel: post with signals => chain"
        " = owner · R3 sku/brand with жалоба on the store-stock lexicon => chain = the thread's"
        " retailer — nothing else",
    }
    sets, opened, files = {}, set(), []
    for name, spec in SETS.items():
        sets[name], threads = rewrite(name, spec, registry, spellings)
        opened |= threads
        files += [spec["predicted"], spec["gold"], spec["pack"], spec["draw"]]
    record = {
        "contract": "docs/PHASE-promo-pulse-1.md §6.2 v18 · ruling 06.09 (bb) addendum item (4) —"
        " P1 measured at $0 on the three dev sets, K8 v2 before and after",
        "k8_version": k8.K8_VERSION,
        "p1": p1_module,
        "sets": sets,
        "leak_check": leak_check(args.draw3, opened, sorted(set(files))),
        "decision_table": decision_table(sets),
    }

    brand_ids = {brand.brand_id for brand in registry.watchlist}
    vocabulary = promo_prompts.vocabulary()
    loops, loop_opened, loop_files = {}, set(), []
    for name, spec in SETS.items():
        loops[name], threads = loop(name, spec, registry, spellings, brand_ids, vocabulary)
        loop_opened |= threads
        loop_files += [spec["replies"], spec["gold"], spec["pack"], spec["draw"]]
    loop_record = {
        "contract": "docs/PHASE-promo-pulse-1.md §2 v20 · ruling 08.09 (dd) item 5 — the SHIPPED"
        " number, measured at $0 on the PRODUCT's pipeline end to end (the four hooks of §2 S4,"
        " then P1) by the product's own functions; the pre-registered readings above stay the"
        " bar's record and no record of theirs is widened",
        "k8_version": k8.K8_VERSION,
        "pipeline": [
            "market_pulse.promo_prompts.parse — the raw answer of the pod out-file this set names",
            "market_pulse.promo_hooks.screen — the four hooks of §2 S4, over the pack's comments,"
            " the registry's brand ids and promo_prompts.vocabulary()",
            "scripts/tick.py :: p1_rows — the kept rows through market_pulse.promo_post.apply, each"
            " handed its comment's KEPT signal types, exactly as `make tick` runs it",
            "scripts/promo_dev_pass.py :: predicted_rows — the gold shape the grader scores",
            "scripts/grade_promo_signals.py :: grade — K8 v2, the same judge as every reading",
        ],
        "p1": p1_module,
        "sets": loops,
        "leak_check": holdout3_disjoint(args.draw3, loop_opened, sorted(set(loop_files))),
    }

    for path, body in ((args.out, record), (args.loop_out, loop_record)):
        path.write_text(
            json.dumps(body, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    print("READING — P1 over the raw answer's rows (the bar's record, ruling (bb)/(cc)):")
    print_sets(sets)
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
    print("\nLOOP — the PRODUCT's pipeline: the same raw answers through the hooks, then P1 (SHIPPED):")
    print_sets(loops)
    loop_leak = loop_record["leak_check"]
    print(
        f"leak check: holdout-3 {loop_leak['holdout3_draw']['threads']} threads,"
        f" {loop_leak['holdout3_threads_shared_with_them']} shared with the"
        f" {loop_leak['threads_opened']} threads this leg opened"
    )
    for path in (args.out, args.loop_out):
        print(f"wrote {path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
