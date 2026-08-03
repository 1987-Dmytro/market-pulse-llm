#!/usr/bin/env python3
"""The v2ctx probe's sample, its rendering and its gate, written down before a row is bought.

Fifth paired column on one hundred rows the operator already ruled on. v2, v2.1 and v2.2 asked
those rows under three different prompt texts and all three lost accepted rows faster than they
landed rulings; this revision changes no text at all and hands the model two **facts** instead
(`docs/annotation/comments.md`, section `v2ctx changelog`).

What this file fixes before the run:

- **the same hundred ids** as `results/v22_probe_plan.json`, which is committed. The reference
  labels come from that plan rather than from a fresh rebuild of the sealed pack: 4.5g5 and
  4.5g6 wrote 41 adjudicated values into the batch the pack was built from, so the pack no
  longer rebuilds to the sha it was sealed with — deliberately, and recorded in
  `results/verdicts_45g5.json`. What is checked instead is the whole chain: the batch's sha256
  is the one 4.5g6 left, and every row neither run touched still equals the plan's reference.
- **the rulings**, merged from both verdict records: the 35 of 4.5g5 and the 6 of 4.5g6, 40 rows
  in all (`@VARUS_channel:9271` is in both, with a different field each time).
- **what renders for which row.** The two discriminators of `results/features_45g5.json`,
  re-derived here and written out per row, so the run cannot render a context line the plan did
  not pre-register.
- **two denominators and one gate.** `preserved` is the 58 accepted rows. `feature_named` is the
  named-value rulings whose refusal `results/features_45g5.json` says a feature *explains* —
  not merely co-occurs with, which is a larger set and the reading the 4.5g5 ADR refused.

    PYTHONPATH=src python3 scripts/plan_v2ctx_probe.py

Writes `results/v2ctx_probe_plan.json`. Constructs no client, reads no key and spends nothing.
"""

import argparse
import json
import math
import sys
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))

import measure_families_45g5 as families  # noqa: E402
import plan_v22_probe as planner  # noqa: E402  — `same`, `target` and `score`, one implementation
import relabel_intents as relabel  # noqa: E402
from build_audit_pack import git_state  # noqa: E402
from fetch_comments_v2 import CHANNELS, read_jsonl, v2_path  # noqa: E402

from market_pulse import parents, prompts  # noqa: E402

V22_PLAN = REPO_ROOT / "results" / "v22_probe_plan.json"
V22_ROWS = REPO_ROOT / "results" / "v22_probe_rows.jsonl"
FEATURES = REPO_ROOT / "results" / "features_45g5.json"
VERDICTS_45G5 = REPO_ROOT / "results" / "verdicts_45g5.json"
VERDICTS_45G6 = REPO_ROOT / "results" / "verdicts_45g6.json"
BATCH = REPO_ROOT / "data" / "annotation" / "uplabel_precheck_45g2.jsonl"
V21_BATCH = REPO_ROOT / "data" / "annotation" / "uplabel_precheck_45g3.jsonl"
POSTS = REPO_ROOT / "data" / "raw" / "posts"
CAPTIONS = REPO_ROOT / "data" / "annotation" / "post_captions.jsonl"
PLAN = REPO_ROOT / "results" / "v2ctx_probe_plan.json"

PHASE = "45g6"
TASK = "precheck_v2ctx_with_post"
FIELDS = planner.FIELDS

PRESERVED_PASS, PRESERVED_KILL = 55, 52
FIXED_PASS_RATE, FIXED_KILL_RATE = 0.70, 0.50
"""`docs/PROMPT-4.5g6.md` §Task 4. The preserved bar is the number 4.5g4 used, unchanged; the
feature bar is a rate over a denominator this file computes, so both land in the plan as
integers before the run and neither can be re-read afterwards."""

UNTOUCHED_ROWS = 60
"""The plan rows no verdict has moved — 100 sampled minus the 40 that now carry a value.

Asserted as a literal rather than derived from the same sets it is checking: this is the count
that makes "the reference labels are still the labels the sitting judged" a measured claim."""


def rel(path: Path) -> str:
    return relabel.rel(path)


def rulings() -> dict[str, dict]:
    """Every named value on a refused row, from both verdict records, merged per row."""
    merged: dict[str, dict] = {}
    for record in (VERDICTS_45G5, VERDICTS_45G6):
        for row in json.loads(record.read_text(encoding="utf-8"))["runs"][-1]["rows"]:
            merged.setdefault(row["id"], {}).update(
                {field: row["after"][field] for field in row["fields"]}
            )
    return merged


def features(rows: list[dict]) -> dict[str, dict]:
    """Per comment id: which of the two discriminators fires, and the channel for the sender one.

    Re-derived from `data/raw/comments_v2/` with the 4.5g5 functions rather than read off a
    stored list, because a stored list is a second copy of a measurement — but the two files it
    reads are pinned in the plan, so "re-derived" cannot quietly mean "from other data".
    """
    reply = set(families.replies_to_comments(rows)["ids"])
    identity = families.hyperactive(rows)
    channel_of = {
        row_id: sender["channel"]
        for sender in identity["senders"]
        for row_id in identity["per_sender_ids"][sender["sender_anon_id"]]
    }
    return {
        row_id: {"reply": row_id in reply, "sender": channel_of.get(row_id)}
        for row_id in set(reply) | set(channel_of)
    }


def by_feature(rows: list[dict], produced: dict[str, dict]) -> dict:
    """The gated counter and the ungated remainder, over the rows that state a value.

    `feature_named` is the gate's denominator: a ruling whose row carries a feature the refusal
    is *about*. The rest of the named-value rulings are reported and never gated — a food-poll
    `taste` ruling on a row that happens to reply to somebody is not a thing context can fix,
    and counting it would price co-occurrence as explanation (4.5g5).
    """
    landed, missed = {}, {}
    for row in rows:
        if row["gated_as"] != "fixed":
            continue
        got = produced.get(row["id"])
        hit = got is not None and planner.same(got, planner.target(row["reference"], row["ruling"]))
        (landed if hit else missed).setdefault(row["feature_named"], []).append(row["id"])
    return {
        group: {
            "n": sum(
                1 for row in rows if row["gated_as"] == "fixed" and row["feature_named"] is on
            ),
            "landed": len(landed.get(on, [])),
            "landed_ids": sorted(landed.get(on, [])),
            "missed_ids": sorted(missed.get(on, [])),
        }
        for group, on in (("feature_named", True), ("not_feature_named", False))
    }


def per_family(rows: list[dict], produced: dict[str, dict]) -> dict:
    """The gated rows split by which feature explains them — sizes and landings side by side."""
    out: dict[str, dict] = {}
    for row in rows:
        if row["gated_as"] != "fixed" or not row["feature_named"]:
            continue
        name = "both" if row["reply"] and row["sender"] else ("reply" if row["reply"] else "sender")
        got = produced.get(row["id"])
        hit = got is not None and planner.same(got, planner.target(row["reference"], row["ruling"]))
        block = out.setdefault(name, {"n": 0, "landed": 0, "ids": []})
        block["n"] += 1
        block["landed"] += hit
        block["ids"].append(row["id"])
    return {name: {**block, "ids": sorted(block["ids"])} for name, block in sorted(out.items())}


def counters(rows: list[dict], produced: dict[str, dict]) -> dict:
    """Everything one column of the paired table holds — 4.5g4's counters plus this gate's."""
    return {**planner.score(rows, produced), **by_feature(rows, produced)}


def verdict(counts: dict, gate: dict) -> str:
    """PASS needs both counters; KILL needs either. The thresholds come from the committed plan."""
    preserved, fixed = counts["preserved"]["kept"], counts["feature_named"]["landed"]
    if preserved < gate["preserved"]["kill_below"] or fixed < gate["feature_fixed"]["kill_below"]:
        return "KILL"
    if preserved >= gate["preserved"]["pass_at"] and fixed >= gate["feature_fixed"]["pass_at"]:
        return "PASS"
    return "OPERATOR-DECIDES"


def as_labels(row: dict) -> dict:
    return {field: row[field] for field in FIELDS}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=PLAN)
    args = parser.parse_args(argv)

    prior = json.loads(V22_PLAN.read_text(encoding="utf-8"))
    batch_rows = {row["id"]: row for row in relabel.load(BATCH)[0]}
    batch_sha = sha256(BATCH.read_bytes()).hexdigest()
    chain = json.loads(VERDICTS_45G6.read_text(encoding="utf-8"))["runs"][-1]
    if batch_sha != chain["batch_sha256_after"]:
        raise SystemExit(
            f"{rel(BATCH)} is {batch_sha[:16]}… and {rel(VERDICTS_45G6)} left it at"
            f" {chain['batch_sha256_after'][:16]}… — the rows this plan samples are not the rows"
            " the verdicts landed on. Stop and report."
        )

    stated = rulings()
    comments = [row for channel in CHANNELS for row in read_jsonl(v2_path(channel))]
    feature_of = features(comments)
    explained = set(
        json.loads(FEATURES.read_text(encoding="utf-8"))["runs"][-1][
            "refusals_explained_by_a_feature"
        ]
    )

    rows, unmoved = [], 0
    for prior_row in prior["rows"]:
        row_id = prior_row["id"]
        ruling = stated.get(row_id, {}) if prior_row["verdict"] == "incorrect" else {}
        if row_id not in stated:
            # nothing adjudicated it, so the batch must still hold what the sitting judged
            if not planner.same(as_labels(batch_rows[row_id]), prior_row["reference"]):
                raise SystemExit(f"{row_id}: the batch moved under a row no verdict ever touched")
            unmoved += 1
        found = feature_of.get(row_id, {"reply": False, "sender": None})
        rows.append(
            {
                "id": row_id,
                "stratum": prior_row["stratum"],
                "verdict": prior_row["verdict"],
                "gated_as": "preserved"
                if prior_row["verdict"] == "correct"
                else ("fixed" if ruling else "reported_only"),
                "reference": prior_row["reference"],
                "ruling": ruling,
                "feature_named": row_id in explained,
                "reply": found["reply"],
                "sender": found["sender"],
                "note": prior_row["note"],
            }
        )
    if unmoved != UNTOUCHED_ROWS:
        raise SystemExit(f"{unmoved} sampled rows are unadjudicated, expected {UNTOUCHED_ROWS}")

    preserved_n = sum(1 for row in rows if row["gated_as"] == "preserved")
    feature_n = sum(1 for row in rows if row["gated_as"] == "fixed" and row["feature_named"])
    gate = {
        "attempts": 1,
        "no_retry": "One probe. No re-prompting, no second sample, no threshold edit.",
        "preserved": {"n": preserved_n, "pass_at": PRESERVED_PASS, "kill_below": PRESERVED_KILL},
        "feature_fixed": {
            "n": feature_n,
            "pass_at": math.ceil(FIXED_PASS_RATE * feature_n),
            "kill_below": math.ceil(FIXED_KILL_RATE * feature_n),
            "rates": {"pass": FIXED_PASS_RATE, "kill": FIXED_KILL_RATE},
        },
    }
    gate["rule"] = (
        f"PASS = preserved >= {PRESERVED_PASS}/{preserved_n} AND feature-fixed >="
        f" {gate['feature_fixed']['pass_at']}/{feature_n}. KILL = preserved <"
        f" {PRESERVED_KILL}/{preserved_n} OR feature-fixed <"
        f" {gate['feature_fixed']['kill_below']}/{feature_n}. Between the two: the operator"
        " decides on the numbers."
    )

    # the byte-identity guard, on a real featureless row of this very sample rather than on a
    # made-up pair: with no feature the request the run sends is the request v2 sent
    posts = parents.load(POSTS)
    captions = parents.load_captions(CAPTIONS)
    featureless = next(row for row in rows if not row["reply"] and not row["sender"])
    found = parents.context(posts, captions, batch_rows[featureless["id"]])
    rendered = [
        prompts.build_messages(
            task,
            batch_rows[featureless["id"]]["text"],
            parent=found["parent"],
            caption=found["caption"],
            caption_kind=found["caption_kind"] or "image",
        )[0]["content"]
        for task in (TASK, "precheck_v2_with_post")
    ]
    if rendered[0] != rendered[1]:
        raise SystemExit(
            f"{featureless['id']} carries no feature and renders differently under {TASK} than"
            " under precheck_v2_with_post. The probe would be measuring two prompts at once."
        )

    v21 = {row["id"]: row for row in relabel.load(V21_BATCH)[0]}
    v22 = {
        json.loads(line)["id"]: json.loads(line)["labels"]
        for line in V22_ROWS.read_text().splitlines()
    }
    reference = {row["id"]: row["reference"] for row in rows}
    priors = {
        "v2 (the labels the sitting judged)": counters(rows, reference),
        "v2.1 (data/annotation/uplabel_precheck_45g3.jsonl)": counters(
            rows, {row_id: as_labels(v21[row_id]) for row_id in reference if row_id in v21}
        ),
        "v2.2 (results/v22_probe_rows.jsonl)": counters(rows, v22),
    }

    plan = {
        "written_by": "scripts/plan_v2ctx_probe.py",
        "phase": PHASE,
        "task": TASK,
        "hypothesis": (
            "The rows the sitting refused are not rows a better sentence reaches: 17 of the 42"
            " are explained by a fact that is not in the text — who wrote the comment, and what"
            " it replies to. v2.2 restated the rulings affirmatively and was KILLed, so the"
            " prompt-form track is closed by pre-registration. This changes no prompt text at"
            " all and renders those two facts beside the post. If the labels do not come back"
            " closer to the verdicts, the evidence hypothesis is closed too, and what is left is"
            " a rule over the features — priced at 62 accepted rows to fix 10."
        ),
        "in_sample": True,
        "in_sample_caveat": (
            "The same hundred rows the v2.2 probe used, and the rulings scored against were"
            " distilled from these very verdicts, so every number here is optimistic by"
            " construction. This probe authorises the next purchase and never batch acceptance:"
            " only a fresh blind hundred drawn outside the judged 300 can accept a re-labelled"
            " batch. Six of the 40 rulings are newer than the v2.2 run and were never available"
            " to it — its column below is recomputed under today's rulings for that reason."
        ),
        "source": {
            "sample_from": rel(V22_PLAN),
            "sample_from_sha256": sha256(V22_PLAN.read_bytes()).hexdigest(),
            "batch": rel(BATCH),
            "batch_sha256": batch_sha,
            "sealed_sha256": prior["source"]["sealed_sha256"],
            "verdicts": [rel(VERDICTS_45G5), rel(VERDICTS_45G6)],
            "comments": {
                rel(v2_path(channel)): sha256(v2_path(channel).read_bytes()).hexdigest()
                for channel in CHANNELS
            },
            "chain_note": (
                "The reference labels are the ones results/v22_probe_plan.json read off a"
                " rebuild of the sealed pack that reproduced sealed_sha256. That rebuild is no"
                " longer possible: 4.5g5 and 4.5g6 wrote 41 adjudicated values into the batch"
                " the pack is built from, and results/sitting_45g2_manifest.json is stale by"
                f" design and must not be re-pinned. What is checked instead: {UNTOUCHED_ROWS} of"
                " the 100 sampled rows carry no verdict and still equal the plan's reference"
                " field for field, and the batch's sha256 is the one the 4.5g6 record left."
            ),
        },
        "rendering": {
            "templates": list(prompts.CONTEXT_TEMPLATES),
            "templates_sha256": sha256("\n".join(prompts.CONTEXT_TEMPLATES).encode()).hexdigest(),
            "prompt_sha256": prompts.prompt_sha256(TASK),
            "prompt_sha256_note": (
                "Identical to precheck_v2_with_post by construction — the revision is the"
                " rendering, and a prompt hash cannot see it. The templates hash above and the"
                " per-row flags below are what identifies this run in a record."
            ),
            "reply_discriminator": "reply_to_msg_id is not the thread's smallest reply target",
            "sender_discriminator": "one of the 2 busiest sender_anon_ids, per channel",
            "rows_with_reply": sum(1 for row in rows if row["reply"]),
            "rows_with_sender": sum(1 for row in rows if row["sender"]),
            "rows_with_both": sum(1 for row in rows if row["reply"] and row["sender"]),
            "rows_with_neither": sum(1 for row in rows if not row["reply"] and not row["sender"]),
            "byte_identity_checked_on": featureless["id"],
            "byte_identity_note": (
                "That row carries neither feature, and the request this plan renders for it under"
                f" {TASK} is byte-identical to the one precheck_v2_with_post renders. Checked"
                " here on a real row of the sample; a unit test holds the same property on a"
                " literal pair, because the batch text a row needs is not what a checkout of the"
                " tests can assume."
            ),
        },
        "sample": {
            "rows": len(rows),
            "refused": sum(1 for row in rows if row["verdict"] == "incorrect"),
            "accepted": sum(1 for row in rows if row["verdict"] == "correct"),
            "unadjudicated_and_unmoved": unmoved,
            "seed": prior["sample"]["seed"],
            "draw": f"the ids of {rel(V22_PLAN)}, unchanged — the fifth paired column",
            "by_stratum": {
                name: sum(1 for row in rows if row["stratum"] == name)
                for name in sorted({row["stratum"] for row in rows})
            },
        },
        "definitions": {
            "preserved": prior["definitions"]["preserved"],
            "fixed": (
                "A refused row whose right answer is written down: the 35 rulings 4.5g5 applied"
                " plus the 6 4.5g6 dictated, 40 rows. It counts as fixed when every field the"
                " ruling names matches the ruling AND every field it does not name equals the"
                " reference — 4.5g4's definition, unchanged."
            ),
            "feature_named": (
                "Of those 40, the rows results/features_45g5.json lists in"
                " `refusals_explained_by_a_feature`: the 10 whose verdict note names a commenter"
                " addressee, plus all 7 refusals written by a channel identity. This is the"
                " gate's denominator. The larger reading — every refusal that merely *belongs*"
                " to a family — is 23 and is reported below, never gated: a food-poll `taste`"
                " ruling on a row that happens to reply to somebody is not a thing a [reply]"
                " line can fix, and gating it would price co-occurrence as explanation."
            ),
            "reported_only": (
                "A refused row with no stated value: @VARUS_channel:7555 (the note names the"
                " error, not the answer) and @msuaaaa:11876 (pending law, operator decision of"
                " 03.08). Two rows, ungated, moved/unmoved reported."
            ),
            "unanswered": prior["definitions"]["unanswered"],
        },
        "gate": gate,
        "reference_points": {
            "on_feature_named_rulings": {
                name: block["feature_named"]["landed"] for name, block in priors.items()
            },
            "briefing_said": {
                "v2": 0,
                "v2.2": 2,
                "computed_here": (
                    "v2 = 0 as stated. v2.2 lands 3 under this plan's definitions, not 2: the"
                    " third is @VARUS_channel:6239, whose value comes from the P5 family rather"
                    " than from its own note, so it was `reported_only` in the 4.5g4 plan and"
                    " falls inside `fixed` here. The gate is unaffected — the denominator is 17"
                    " either way — but the bar v2ctx has to beat is 3, not 2."
                ),
            },
        },
        "reference_runs": priors,
        "reference_note": (
            "The same scorer over the same rows. v2 is the reference labels themselves, so its"
            " preserved count is the denominator and its fixed count is zero by construction."
            " v2.2's answers are the 100 replies results/v22_probe_rows.jsonl holds, re-scored"
            " here under the 40 rulings rather than the 29 its own plan knew."
        ),
        "secondary_reported_never_gated": {
            "not_feature_named": (
                "The 23 named-value rulings no feature explains. Reported per column so that a"
                " revision which fixed them by accident is visible, and never gated."
            ),
            "per_family": "The gated rows split into reply-only, sender-only and both.",
            "named_field_only": prior["secondary_reported_never_gated"]["named_field_only"],
            "per_field_moves": "How many of the 100 moved each of the four fields.",
        },
        "cap_usd": 1.50,
        "ledger": "results/spend_45g6.json",
        "rows": rows,
        "git": git_state(args.plan),
    }
    args.plan.parent.mkdir(parents=True, exist_ok=True)
    args.plan.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"{rel(args.plan)}")
    print(f"  {unmoved} unadjudicated rows still equal the reference; batch {batch_sha[:16]}…")
    print(
        f"  renders: {plan['rendering']['rows_with_reply']} reply ·"
        f" {plan['rendering']['rows_with_sender']} sender ·"
        f" {plan['rendering']['rows_with_both']} both ·"
        f" {plan['rendering']['rows_with_neither']} neither"
        f" (byte-identity checked on {featureless['id']})"
    )
    print(
        f"  gated: {preserved_n} preserved · {feature_n} feature-named of"
        f" {sum(1 for row in rows if row['gated_as'] == 'fixed')} named-value rulings ·"
        f" {sum(1 for row in rows if row['gated_as'] == 'reported_only')} reported only"
    )
    print(f"  {gate['rule']}")
    for name, block in priors.items():
        print(
            f"  {name:<52} preserved {block['preserved']['kept']:>2}/{block['preserved']['n']}"
            f" · feature-fixed {block['feature_named']['landed']:>2}/{block['feature_named']['n']}"
            f" · other named {block['not_feature_named']['landed']:>2}/"
            f"{block['not_feature_named']['n']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
