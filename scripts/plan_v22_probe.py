#!/usr/bin/env python3
"""The v2.2 probe's sample and its gate, written down before a single row is bought (4.5g4).

4.5g3 bought 1,912 rows to discover that a prompt revision is an instrument change. This phase
buys a hundred. The hundred is in-sample by construction — the rulings were distilled from
these very verdicts — so the thresholds have to exist before the numbers do, or the reading of
those numbers is chosen after seeing them.

What this file is for:

- **the sample, by id.** All 42 rows the sitting called `incorrect`, plus 58 of the 258 it
  called `correct`, drawn with `random.Random(42)` over the id-sorted list. Every id and the
  stratum it came from is written out, so the run cannot quietly ask about a different hundred.
- **the reference labels.** The four fields the operator ruled on, read off the sealed sitting
  pack — and only after a rebuild of that pack reproduces the sha256 it was sealed with. The
  same machinery `read_sitting_returns` uses, for the same reason: labels scored against have
  to be provably the ones that were judged.
- **the gate, one attempt.** PASS, KILL and the band between them, with the denominator each
  is measured on.
- **the paired baseline.** What v2 and v2.1 score on these identical rows under these identical
  definitions, so the probe reads as a comparison and not as a number against an average.

Nothing here constructs a client, reads an API key or spends: it is the artifact that has to be
committed before `run_v22_probe.py` is allowed to start, and that script checks git for it.

    PYTHONPATH=src python3 scripts/plan_v22_probe.py

Writes `results/v22_probe_plan.json`.
"""

import argparse
import json
import random
import sys
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_sitting_pack as builder  # noqa: E402
import read_sitting_returns as returns  # noqa: E402
import relabel_intents as relabel  # noqa: E402
from build_audit_pack import git_state  # noqa: E402
from build_wave2_pack import expected  # noqa: E402  — the 4.5g3 stated-ruling parser, reused

GATES = REPO_ROOT / "results" / "sitting_45g_gates.json"
MANIFEST = REPO_ROOT / "results" / "sitting_45g2_manifest.json"
POSTS = REPO_ROOT / "data" / "raw" / "posts"
V21_BATCH = REPO_ROOT / "data" / "annotation" / "uplabel_precheck_45g3.jsonl"
PLAN = REPO_ROOT / "results" / "v22_probe_plan.json"

PHASE = "45g4"
TASK = "precheck_v2.2_with_post"
FIELDS = ("sentiment", "sarcasm", "intents", "unclear")
"""The four fields the sitting judged. Spelled out here rather than imported from the asking
script, so this module depends on nothing that can make a request."""

SEED = 42
CORRECT_ROWS = 58
"""How many of the 258 accepted rows join the 42 refused ones. The refused rows are all of
them: they are what the revision was written for, and a sample of them would be a sample of
the thing being measured."""

PRESERVED_PASS, PRESERVED_KILL = 55, 52
FIXED_PASS, FIXED_KILL = 24, 20
"""The gate of `docs/PROMPT-4.5g4.md`, one attempt and no retry. PASS needs both; KILL needs
either; the band between them is the operator's call on the numbers."""


def typed(row: dict) -> dict:
    """One sealed CSV row as labels — the pack stores every cell as text."""
    return {
        "sentiment": row["sentiment"],
        "sarcasm": row["sarcasm"] == "true",
        "intents": sorted(json.loads(row["intents"])),
        "unclear": row["unclear"] == "true",
    }


def same(got: dict, want: dict, fields=FIELDS) -> bool:
    """Field-for-field equality, with `intents` compared as a set in list clothing."""
    return all(
        sorted(got[field]) == sorted(want[field])
        if field == "intents"
        else got[field] == want[field]
        for field in fields
        if field in want
    )


def target(reference: dict, ruling: dict) -> dict:
    """What a fixed row has to answer: the pack's labels, overridden where the ruling speaks.

    Both halves matter. The named fields are the ruling — that is what the revision was written
    to change. The unnamed ones are the pack — a row is not fixed by getting the ruling right
    and relabelling something else on the way past.
    """
    return {**reference, **ruling}


def sample(gates: dict) -> tuple[list[str], list[str]]:
    """The 42 refused rows, and 58 of the accepted ones drawn from a sorted list."""
    refused = sorted(row["id"] for row in gates["rows"] if row["verdict"] != "correct")
    accepted = sorted(row["id"] for row in gates["rows"] if row["verdict"] == "correct")
    drawn = random.Random(SEED).sample(accepted, CORRECT_ROWS)
    return refused, sorted(drawn)


def score(rows: list[dict], produced: dict[str, dict]) -> dict:
    """The gate's two counters over whatever a run produced, plus what it cannot gate.

    Lives here rather than in the runner so that the definitions being applied are the ones
    this file committed. A row the run never answered counts against the denominator it was
    registered on: an unanswered row is not a preserved one.
    """
    preserved = [row for row in rows if row["gated_as"] == "preserved"]
    fixed = [row for row in rows if row["gated_as"] == "fixed"]
    kept = [
        row["id"]
        for row in preserved
        if row["id"] in produced and same(produced[row["id"]], row["reference"])
    ]
    landed, named_only = [], []
    for row in fixed:
        got = produced.get(row["id"])
        if got is None:
            continue
        if same(got, target(row["reference"], row["ruling"])):
            landed.append(row["id"])
        elif same(got, row["ruling"], fields=tuple(row["ruling"])):
            named_only.append(row["id"])
    reported = [row for row in rows if row["gated_as"] == "reported_only"]
    moved = [
        row["id"]
        for row in reported
        if row["id"] in produced and not same(produced[row["id"]], row["reference"])
    ]
    return {
        "preserved": {"n": len(preserved), "kept": len(kept)},
        "fixed": {"n": len(fixed), "landed": len(landed)},
        "named_field_only": sorted(named_only),
        "preserved_lost": sorted(row["id"] for row in preserved if row["id"] not in kept),
        "fixed_missed": sorted(row["id"] for row in fixed if row["id"] not in landed),
        "ungated_moved": sorted(moved),
        "ungated_unmoved": sorted(row["id"] for row in reported if row["id"] not in moved),
        "answered": sum(1 for row in rows if row["id"] in produced),
    }


def verdict(counts: dict) -> str:
    """PASS needs both counters; KILL needs either. Everything else is the operator's."""
    preserved, fixed = counts["preserved"]["kept"], counts["fixed"]["landed"]
    if preserved < PRESERVED_KILL or fixed < FIXED_KILL:
        return "KILL"
    if preserved >= PRESERVED_PASS and fixed >= FIXED_PASS:
        return "PASS"
    return "OPERATOR-DECIDES"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gates", type=Path, default=GATES)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--posts", type=Path, default=POSTS)
    parser.add_argument("--v21-batch", type=Path, default=V21_BATCH)
    parser.add_argument("--plan", type=Path, default=PLAN)
    args = parser.parse_args(argv)

    gates = json.loads(args.gates.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    batch = REPO_ROOT / manifest["precheck"]["source"]
    sealed = returns.rebuild(manifest, batch, REPO_ROOT / manifest["media"]["captions"], args.posts)
    rebuilt = sha256(returns.serialize(builder.PRECHECK_COLUMNS, sealed)).hexdigest()
    if rebuilt != gates["sealed_sha256"]:  # rebuild() already refused; this names the record too
        raise SystemExit(
            f"the rebuild is {rebuilt[:16]}… and {relabel.rel(args.gates)} pins "
            f"{gates['sealed_sha256'][:16]}… — two different sealed packs"
        )
    reference = {row["id"]: typed(row) for row in sealed}
    stratum_of = manifest["precheck"]["stratum_of"]
    notes = {row["id"]: row["notes"] for row in gates["rows"]}

    refused, accepted = sample(gates)
    rows = []
    for row_id in refused + accepted:
        ruling = expected(notes[row_id]) if row_id in set(refused) else {}
        rows.append(
            {
                "id": row_id,
                "stratum": stratum_of[row_id],
                "verdict": "incorrect" if row_id in set(refused) else "correct",
                "gated_as": "preserved"
                if row_id in set(accepted)
                else ("fixed" if ruling else "reported_only"),
                "reference": reference[row_id],
                "ruling": ruling,
                "note": notes[row_id],
            }
        )

    # the paired baseline: what the two earlier prompts score on these same rows, under these
    # same definitions. v2 is the reference itself, so its counters are what the definitions
    # produce when nothing moved — a control on the scorer as much as a baseline.
    v21 = {row["id"]: row for row in relabel.load(args.v21_batch)[0]}
    priors = {
        "v2 (the labels the sitting judged)": score(rows, reference),
        "v2.1 (data/annotation/uplabel_precheck_45g3.jsonl)": score(
            rows, {row_id: {field: v21[row_id][field] for field in FIELDS} for row_id in v21}
        ),
    }

    plan = {
        "written_by": "scripts/plan_v22_probe.py",
        "phase": PHASE,
        "task": TASK,
        "hypothesis": (
            "The eight rulings of guideline v2.1 are right and the sentences carrying them to"
            " the model were backwards. v2.2 restates them affirmatively — condition, field,"
            " value — and changes nothing else: not the `unclear` wording, not the position of"
            " the block. If the labels do not come back closer to the sitting's verdicts, the"
            " form-only hypothesis is closed and the next variable is position."
        ),
        "in_sample": True,
        "in_sample_caveat": (
            "These 100 rows are the verdicts the v2.1 AND v2.2 rulings were both distilled"
            " from, so every number here is optimistic by construction. This probe authorises"
            " the next purchase and never batch acceptance: only a fresh blind hundred, drawn"
            " outside the judged 300, can accept a re-labelled batch. For scale, v2.1 scored"
            " 10 of these same 29 stated rulings and moved 172 of the 258 accepted rows"
            " corpus-wide (results/rerun_45g3.json)."
        ),
        "source": {
            "gates": relabel.rel(args.gates),
            "manifest": relabel.rel(args.manifest),
            "batch": relabel.rel(batch),
            "batch_sha256": sha256(batch.read_bytes()).hexdigest(),
            "sealed_sha256": gates["sealed_sha256"],
            "rebuilt_sha256": rebuilt,
            "rebuild_note": (
                "The reference labels are read off a rebuild of the sealed pack, and the rebuild"
                " reproduces the sha256 the pack was sealed with before a label is read. The"
                " returned CSV is gitignored; this is how the run proves it is scoring against"
                " what the operator ruled on."
            ),
        },
        "sample": {
            "rows": len(rows),
            "all_refused": len(refused),
            "drawn_from_accepted": len(accepted),
            "of_accepted": sum(1 for row in gates["rows"] if row["verdict"] == "correct"),
            "seed": SEED,
            "draw": "random.Random(42).sample(sorted(accepted_ids), 58)",
            "by_stratum": {
                name: sum(1 for row in rows if row["stratum"] == name)
                for name in sorted({row["stratum"] for row in rows})
            },
        },
        "definitions": {
            "preserved": (
                "A row the sitting called `correct`: its four fields are the right answer, so"
                " v2.2 has to return all four unchanged. Anything else is the revision"
                " relabelling what the operator accepted — the failure 4.5g3 measured."
            ),
            "fixed": (
                "A row the sitting called `incorrect` whose note states the right value in a"
                " form the 4.5g3 parser reads. It counts as fixed when every field the ruling"
                " names matches the ruling AND every field it does not name equals the pack."
            ),
            "reported_only": (
                "A refused row whose note names the error without naming the value ('«что"
                " попало?» asks box contents, not presence'). Ungated by design: scoring it"
                " would need a right answer that was never written down. Moved/unmoved is"
                " reported. The P5 and P6 families are here."
            ),
            "unanswered": (
                "A row the run could not read an answer for counts against its denominator. An"
                " unanswered row is not a preserved one, and a probe that dropped it would"
                " report a rate over a sample it chose after the fact."
            ),
        },
        "gate": {
            "attempts": 1,
            "no_retry": "One probe. No re-prompting, no second sample, no threshold edit.",
            "preserved": {
                "n": len(accepted),
                "pass_at": PRESERVED_PASS,
                "kill_below": PRESERVED_KILL,
            },
            "fixed": {
                "n": sum(1 for row in rows if row["gated_as"] == "fixed"),
                "pass_at": FIXED_PASS,
                "kill_below": FIXED_KILL,
            },
            "rule": (
                f"PASS = preserved >= {PRESERVED_PASS}/{len(accepted)} AND fixed >="
                f" {FIXED_PASS}/29. KILL = preserved < {PRESERVED_KILL}/{len(accepted)} OR fixed"
                f" < {FIXED_KILL}/29. Between the two: the operator decides on the numbers."
            ),
            "on_pass": (
                "Pin v2.2's answers for the hundred ids of data/annotation/wave2_45g3/ into"
                " results/wave2_45g3_v22_labels.json, before any verdict on that pack exists."
            ),
            "on_fail": "The form-only hypothesis is closed. Task 4 is skipped and the phase reports.",
        },
        "secondary_reported_never_gated": {
            "named_field_only": (
                "Of the fixed rows: how many match every field the ruling NAMES while moving a"
                " field it does not. 19 of the 29 rulings are `unclear: true`, and an unclear"
                " row's other labels are excluded from scoring by the guideline — so this class"
                " is real and the pre-registered rule counts it as a miss anyway. Registered"
                " here, before the numbers exist, because 'the rulings did not land' and 'the"
                " rulings landed and the row moved elsewhere' are different findings."
            ),
            "per_field_moves": "How many of the 100 moved each of the four fields, against the pack.",
        },
        "reference_runs": priors,
        "reference_note": (
            "The same scorer over the same rows. v2 is the reference labels themselves, so its"
            " preserved count is the denominator and its fixed count is zero by construction:"
            " those rows were refused precisely because v2 got them wrong. That row is a control"
            " on the scorer. v2.1's counters are the number v2.2 has to beat."
        ),
        "cap_usd": 1.50,
        "ledger": "results/spend_45g4.json",
        "rows": rows,
        "git": git_state(args.plan),
    }
    args.plan.parent.mkdir(parents=True, exist_ok=True)
    args.plan.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"{relabel.rel(args.plan)}")
    print(f"  rebuild reproduces {rebuilt[:16]}… of the sealed pack before a label is read")
    print(f"  sample {len(rows)}: {len(refused)} refused + {len(accepted)} accepted, seed {SEED}")
    print(f"  by stratum {plan['sample']['by_stratum']}")
    print(
        f"  gated: {plan['gate']['preserved']['n']} preserved · {plan['gate']['fixed']['n']}"
        f" fixed · {sum(1 for row in rows if row['gated_as'] == 'reported_only')} reported only"
    )
    print(f"  {plan['gate']['rule']}")
    for name, counts in priors.items():
        print(
            f"  {name:<52} preserved {counts['preserved']['kept']:>2}/{counts['preserved']['n']}"
            f" · fixed {counts['fixed']['landed']:>2}/{counts['fixed']['n']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
