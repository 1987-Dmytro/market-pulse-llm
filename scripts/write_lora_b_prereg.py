#!/usr/bin/env python3
"""`results/prereg_lora_b.json` — the registration D3 is not allowed to start without.

**What this registers.** Two arms of one QLoRA fine-tune, ONE attempt at a sealed bar, a cap, and
the clock that kills the pod at every rung before its milestone. It is written and COMMITTED before
`pod create`, so the git clock — not a sentence in a report — is what proves the plan predates the
money. Nothing here is typed twice: the bar block, the gold rows and the per-call readings are READ
out of `results/prereg_pass1_probe_b.json` and the gold record, and the arms are read out of
`results/pass1_sft.json`, which is itself self-pinned.

**H6.** `docs/PROMPT-lora-b.md` D1 asks for a refusal gate: every number the contract registers,
re-derived from its formula, with a mismatch a finding BEFORE the money. The table is a block of
this record rather than a paragraph of a report, because a gate whose verdict lives only in prose
is a gate nobody can re-run ([[gate_verdicts_need_an_artifact]]). Three of its rows come out RED —
the dataset the contract sized at 500 and 650 rows is 464 and 607 once every row that cannot fit
`config/qlora.yaml`'s frozen `max_seq_len` is dropped — and the arithmetic downstream of them moves
with them. Every mismatch here makes the run CHEAPER, and none of them was silently fixed.

    PYTHONPATH=src python3.11 scripts/write_lora_b_prereg.py
    PYTHONPATH=src python3.11 scripts/write_lora_b_prereg.py --outdir /tmp/again   # the pair
"""

import argparse
import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import window_summary_5c2 as summary  # noqa: E402

import yaml  # noqa: E402

from market_pulse import prompts  # noqa: E402

PROBE_PREREG = REPO_ROOT / "results" / "prereg_pass1_probe_b.json"
PROBE_PACK = REPO_ROOT / "results" / "pass1_probe_b_pack.json"
PROBE_VERDICT = REPO_ROOT / "results" / "pass1_probe_b_verdict.json"
GOLD = REPO_ROOT / "results" / "reader_gold_w1_r2.json"
SFT = REPO_ROOT / "results" / "pass1_sft.json"
QLORA = REPO_ROOT / "config" / "qlora.yaml"
OUT_NAME = "results/prereg_lora_b.json"

SECONDS_PER_STEP = 61.047
"""The worst step this stack has measured — 4.5h2 / probe-b, A6000, seq 1408, micro 2 × accum 8.
A BOUND and not a forecast: a projection built on the best of two measurements is a projection that
has already spent its margin."""

SECONDS_PER_CALL = 5.162
"""The measured pass-1 transport call (probe-b). Both arms' evals are priced with it."""

PRICE_CEILING_USD_PER_HOUR = 0.80
"""The kill-clock's own first rung: above this at `pod create` there is no endpoint. Every figure
below is worked at it, so the arithmetic is the WORST affordable machine and not a lucky one."""

CAP_USD = 6.00
MILESTONE_USD = 2.50
BOOT_CEILING_SECONDS = 450
"""The boot-to-training-start rung — 293 s (the worst boot measured) × 1.5. It is also what the
worst case charges for boot: a leg cannot cost more than the clock that kills it."""

OVERHEAD_HOURS = 0.5
"""Staging, the scp of everything, and the deletion. Registered, not hoped for."""

REGISTERED = {
    "arm_a_rows": (500, "the r1 labels, 500 units", "equals"),
    "arm_b_rows": (650, "r1 + r2, 500 + 150 units", "equals"),
    "arm_a_steps": (64, "ceil(n/16) × 2 epochs", "equals"),
    "arm_b_steps": (82, "ceil(n/16) × 2 epochs", "equals"),
    "arm_a_seconds": (3907, "steps × 61.047 s/step", "equals"),
    "arm_b_seconds": (5006, "steps × 61.047 s/step", "equals"),
    "eval_seconds": (660, "2 adapters × 64 units × 5.162 s", "equals"),
    "worst_case_usd": (2.63, "(train + eval + boot + 0.5 h overhead) × $0.80/h", "equals"),
    "session_ceiling_hours": (7.5, "cap / price ceiling", "equals"),
    "boot_gate_seconds": (450, "the worst boot measured (293 s) × 1.5", "at_least"),
    "step_watchdog_seconds": (122, "2 × the measured s/step", "at_most"),
    "census_50_baseline_none": (
        25,
        "the base model's None count over the 50 census rows",
        "equals",
    ),
    "base_bar": (9, "the base model's agreed rows over the sealed fourteen", "equals"),
    "combined_distribution": (
        {
            "не_наш_рынок": 340,
            "null": 213,
            "сеть_ритейлер": 48,
            "категория_личное": 47,
            "молочный_бренд": 2,
        },
        "the two labels files counted together",
        "equals",
    ),
}
"""Every number `docs/PROMPT-lora-b.md` registers, with the formula it names for it and the way the
two are allowed to differ. The value is the contract's; the formula is what H6 runs
([[trace_the_producer_not_the_result]]).

The mode is not a loophole and it is spelled out per row. `equals` is 1% relative — a rounding is
not a finding and 0.7 s on 660 is a rounding. A **kill** threshold is different in kind: a boot gate
of 450 s over a derivation of 439.5 s is MARGIN, and a watchdog set at 122 s under a derived 122.09
fires slightly early, which is also margin. Both are only allowed to be conservative, and a rung on
the wrong side of its own formula comes out red."""


def read(path: Path) -> dict:
    return json.loads(summary.read_text_or_refuse(path))


def gold_rows() -> list[dict]:
    """The fourteen, derived from the gold record and held to the probe-b registration's list."""
    gold = read(GOLD)
    pack = read(PROBE_PACK)
    thread_of = {int(one["msg_id"]): one["thread"] for one in pack["items"]}
    rows = sorted(
        (
            {"thread": thread_of[int(one["msg_id"])], "msg_id": int(one["msg_id"])}
            for one in gold["per_comment"]
        ),
        key=lambda one: (one["thread"], one["msg_id"]),
    )
    registered = sorted(
        (
            {"thread": one["thread"], "msg_id": int(one["msg_id"])}
            for one in read(PROBE_PREREG)["population"]["gold"]["rows"]
        ),
        key=lambda one: (one["thread"], one["msg_id"]),
    )
    if rows != registered:
        raise SystemExit(
            "the fourteen gold rows derived from the gold record are not the fourteen probe-b"
            " registered. The bar would be scored on a different population than the base was."
        )
    return rows


def labels_distribution() -> dict[str, int]:
    """r1 and r2 counted together, off the frozen files — the arm-B set before any length bound."""
    counts: dict[str, int] = {}
    for name in ("r1", "r2"):
        path = REPO_ROOT / "results" / f"labels_pass1_{name}.jsonl"
        for line in summary.read_text_or_refuse(path).splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            key = "null" if row.get("subject_type") is None else row["subject_type"]
            counts[key] = counts.get(key, 0) + 1
    for value in (*prompts.PASS1_SUBJECT_TYPES, None):
        counts.setdefault("null" if value is None else value, 0)
    return dict(sorted(counts.items()))


def arithmetic(sft: dict) -> dict:
    arms = sft["census"]["arms"]
    train = {arm: round(arms[arm]["steps"] * SECONDS_PER_STEP, 1) for arm in sorted(arms)}
    evaluation = round(2 * len(read(PROBE_PACK)["items"]) * SECONDS_PER_CALL, 1)
    hours = (sum(train.values()) + evaluation + BOOT_CEILING_SECONDS) / 3600 + OVERHEAD_HOURS
    after_arm_a = (BOOT_CEILING_SECONDS + train["a"]) / 3600 * PRICE_CEILING_USD_PER_HOUR
    return {
        "seconds_per_step": SECONDS_PER_STEP,
        "seconds_per_call": SECONDS_PER_CALL,
        "steps": {arm: arms[arm]["steps"] for arm in sorted(arms)},
        "steps_rule": "ceil(n / (micro_batch_size × grad_accum)) × epochs, all three from config/qlora.yaml",
        "train_seconds": train,
        "eval_seconds": evaluation,
        "eval_rule": "2 adapters × the eval pack's 64 units × the measured seconds per call",
        "boot_seconds_charged": BOOT_CEILING_SECONDS,
        "overhead_hours": OVERHEAD_HOURS,
        "hours": round(hours, 4),
        "worst_case_usd": round(hours * PRICE_CEILING_USD_PER_HOUR, 4),
        "cap_headroom_usd": round(CAP_USD - hours * PRICE_CEILING_USD_PER_HOUR, 4),
        "projected_usd_at_the_arm_a_milestone": round(after_arm_a, 4),
        "milestone_rule": (
            f"the guard reading after arm A must be ≤ ${MILESTONE_USD:.2f} or arm B does not start."
            " The projection above is boot + arm A at the price ceiling; the STOP is on the READING,"
            " never on the projection"
        ),
    }


def h6(sft: dict, sums: dict) -> dict:
    """Every registered number, re-derived. A mismatch is a finding BEFORE the money."""
    arms = sft["census"]["arms"]
    verdict = read(PROBE_VERDICT)
    derived = {
        "arm_a_rows": arms["a"]["n"],
        "arm_b_rows": arms["b"]["n"],
        "arm_a_steps": arms["a"]["steps"],
        "arm_b_steps": arms["b"]["steps"],
        "arm_a_seconds": sums["train_seconds"]["a"],
        "arm_b_seconds": sums["train_seconds"]["b"],
        "eval_seconds": sums["eval_seconds"],
        "worst_case_usd": sums["worst_case_usd"],
        "session_ceiling_hours": round(CAP_USD / PRICE_CEILING_USD_PER_HOUR, 4),
        "boot_gate_seconds": 293 * 1.5,
        "step_watchdog_seconds": 2 * SECONDS_PER_STEP,
        "census_50_baseline_none": verdict["census"]["subject_type_distribution"]["None"],
        "base_bar": verdict["bars"]["P1_per_comment_agreement"]["agreed"],
        "combined_distribution": {
            key: value for key, value in labels_distribution().items() if value
        },
    }
    rows = []
    for name, (registered, formula, mode) in sorted(REGISTERED.items()):
        got = derived[name]
        if mode == "at_least":
            agrees = float(registered) >= float(got)
        elif mode == "at_most":
            agrees = float(registered) <= float(got)
        elif isinstance(registered, (int, float)) and isinstance(got, (int, float)):
            agrees = abs(float(got) - float(registered)) <= abs(registered) * 0.01
        else:
            agrees = got == registered
        rows.append(
            {
                "name": name,
                "registered": registered,
                "formula": formula,
                "mode": mode,
                "re_derived": got,
                "agrees": agrees,
            }
        )
    red = [row["name"] for row in rows if not row["agrees"]]
    return {
        "rule": (
            "every number docs/PROMPT-lora-b.md registers, re-derived from the formula the contract"
            " names for it. `equals` allows 1% — a rounding is not a finding; a kill threshold is"
            " checked for the direction of its margin instead, and is red on the wrong side of its"
            " own derivation"
        ),
        "rows": rows,
        "mismatches": red,
        "reading": (
            "the arm sizes and everything derived from them moved because the contract sized the"
            " arms at 500 and 650 LABELS and the trainable set is what fits config/qlora.yaml's"
            " frozen max_seq_len: 43 rows render past it and are dropped by name in"
            " results/pass1_sft.json. Every mismatch makes the run CHEAPER than registered and none"
            " was silently fixed"
        )
        if red
        else "every registered number re-derives",
    }


def reachability(sft: dict) -> dict:
    """What the arms can and cannot reach, priced BEFORE the attempt is spent."""
    gold = read(GOLD)
    verdict = read(PROBE_VERDICT)
    bar = verdict["bars"]["P1_per_comment_agreement"]
    missed = [row for row in bar["rows"] if not row["agreed"]]
    by_class: dict[str, int] = {}
    for row in missed:
        told = row["disagreed_on"]["subject_type"]["gold"]
        by_class[told] = by_class.get(told, 0) + 1
    arms = sft["census"]["arms"]
    envelope = sft["length"]["topic_envelope"]
    stance_rows = [one for one in gold["per_comment"] if "stance" in one["scored_fields"]]
    return {
        "to_pass": {
            "agreed_now": bar["agreed"],
            "minimum_agreed": bar["minimum_agreed"],
            "rows_the_arm_must_turn": bar["minimum_agreed"] - bar["agreed"],
            "the_five_missed": {
                str(row["msg_id"]): row["disagreed_on"]["subject_type"] for row in missed
            },
            "by_gold_class": by_class,
            "training_rows_behind_them": {
                "категория_личное": arms["b"]["distribution"]["категория_личное"],
                "молочный_бренд": arms["b"]["distribution"]["молочный_бренд"],
            },
            "reading": (
                "four of the five rows the arms must turn are gold «категория» and one is"
                f" «молочный_бренд». Arm B carries {arms['b']['distribution']['категория_личное']}"
                f" rows of the first class and {arms['b']['distribution']['молочный_бренд']} of the"
                " second, and the sampler's cap of 8.0 is what the second one gets. The numbers are"
                " read off the dataset record rather than written here: this sentence has already"
                " been wrong once, when the length bound dropped one of the two brand rows"
            ),
        },
        "stance_is_not_trained": {
            "gold_rows_scoring_stance": len(stance_rows),
            "reachable_maximum_if_stance_were_taught_null": len(gold["per_comment"])
            - len(stance_rows),
            "rule": (
                "the team lead labelled subject_type alone. Writing null into the two unlabelled"
                " fields AND training on it would put every stance-scoring row out of reach and cap"
                " the bar at 11 of 14 — under the threshold, before the pod exists. The SFT builder"
                " masks them out of the loss instead, and this is the arithmetic that decided it"
            ),
        },
        "the_context_the_gate_carries": {
            "gate_rows_with_an_entity_block": sft["census"]["the_gate_s_own_rows"][
                "with_an_entity_block"
            ],
            "gate_rows": sft["census"]["the_gate_s_own_rows"]["n"],
            "eval_pack_items_with_an_entity_block": sft["census"]["eval_pack"][
                "with_an_entity_block"
            ],
            "eval_pack_items": sft["census"]["eval_pack"]["items"],
            "arm_b_rows_with_an_entity_block": arms["b"]["context"]["with_an_entity_block"],
            "arm_b_rows": arms["b"]["n"],
            "topic_envelope_chars": envelope["limit"],
            "the_cut_marker": {
                "training_rows_marked": arms["b"]["context"]["with_a_topic_the_cut_shortened"],
                "of": arms["b"]["n"],
                "eval_items_marked": sum(
                    1 for one in read(PROBE_PACK)["items"] if one["topic"].rstrip().endswith("…")
                ),
                "eval_items": len(read(PROBE_PACK)["items"]),
                "reading": (
                    "branch C marks a shortened topic with an ellipsis, and a BOUGHT topic is never"
                    " cut — so the marker appears on most of the training set and on none of the"
                    " eval prompts. It is the same class as the finding it was fixing, one size"
                    " smaller, and it is registered here rather than discovered afterwards: after"
                    " the one attempt it would be an uncontrolled variable nobody wrote down"
                ),
            },
            "cause": (
                "a pass-1 request carries the thread's topic and entity block, and both come from a"
                " reader verdict that was PAID FOR. 15 of the 120 labelled threads have one; the"
                " rest render the topic from the store's own post text, cut to the envelope a"
                f" bought topic occupies ({envelope['limit']} characters, the longest of"
                f" {envelope['measured_over']}), and an EMPTY entity block. The cut is the"
                " operator's branch-C ruling of 2026-08-19: it put every row back under max_seq_len"
                " — nothing is dropped now and both молочный_бренд rows train — and it bought no"
                " verdict, so the entity block is exactly as empty as it was"
            ),
            "the_open_ruling": (
                "REGISTERED AS A RISK, not as a defect: the arms are trained on requests whose"
                " entity block is almost always empty and graded on requests where it is almost"
                " always full. Removing it costs a reader pass over the 105 uncovered threads —"
                " 105 × 51.3 s = ~5 390 s ≈ $1.20 at the price ceiling, in a SEPARATE session,"
                " because a dataset built during the paid session could not have been"
                " pre-registered. The operator ruled branch C, which closes the length half and"
                " leaves this one open and named; this record says what was known before the"
                " attempt"
            ),
        },
    }


def build() -> dict:
    sft = read(SFT)
    probe = read(PROBE_PREREG)
    config = yaml.safe_load(QLORA.read_text(encoding="utf-8"))
    sums = arithmetic(sft)
    arms = sft["census"]["arms"]
    return {
        "attempt": (
            "ONE. No retry, no second draw, and no tuning after any eval output is seen. The"
            " multiplicity of running two arms against one bar is named below and was accepted by"
            " the sitting; it is not re-decided once the number is in"
        ),
        "authority": (
            "sitting-2 of 2026-08-19 (LoRA, line B) and its r2 ruling — docs/STATUS.md «День"
            " 19.08», ADR knowledge/decisions/sitting-b-line-b-and-the-team-lead-labels.md"
        ),
        "arms": {
            arm: {
                "dataset": sft["datasets"][arm],
                "n": arms[arm]["n"],
                "distribution": arms[arm]["distribution"],
                "sampler_weights": arms[arm]["sampler_weights"],
                "steps": arms[arm]["steps"],
                "command": (
                    "PYTHONPATH=/workspace/repo/src /workspace/venv/bin/python -u"
                    " /workspace/repo/scripts/train_qlora.py --data"
                    f" {sft['datasets'][arm]['file']} --class-weights --out /workspace/run/arm_{arm}"
                ),
                "eval_command": (
                    "PYTHONPATH=/workspace/repo/src /workspace/venv/bin/python -u"
                    " /workspace/repo/scripts/pass1_pod_runner.py --pack"
                    " results/pass1_probe_b_pack.json --repo /workspace/repo --out"
                    f" /workspace/run/eval_arm_{arm}.jsonl --adapter /workspace/run/arm_{arm}/adapter"
                ),
            }
            for arm in sorted(arms)
        },
        "ablation": (
            "arm A's rows are a SUBSET of arm B's, so the one variable is the r2 top-up. After the"
            " pass1-redraw census the question is «does more data of the same population help», not"
            " «does targeting help» — the targeted-re-draw premise died there and the arm keeps the"
            " name top-up"
        ),
        "bars": {
            "P1_per_comment_agreement": {
                **probe["bars"]["P1_per_comment_agreement"],
                "arm_rule": "max(gold14(arm A), gold14(arm B)) ≥ 12 of 14",
                "borrowed_from": "results/prereg_pass1_probe_b.json — the same block, read and never retyped",
                "multiplicity": (
                    "TWO shots at one bar is approximately double the false-pass odds of one, and"
                    " it is accepted by the sitting-2 ruling rather than hidden: with two"
                    " independent arms at a false-pass rate p the probability that at least one"
                    " passes is 1-(1-p)² ≈ 2p. Registered here so the verdict cannot be read later"
                    " as if one arm had been run"
                ),
                "tie": "a tie ships arm B — named before the numbers exist",
                "red": (
                    "line B is CLOSED and the question returns to the sitting (option C, a"
                    " different base). A red bar is an ANSWER, not a bug to fix in-session"
                ),
                "scored_by": "scripts/score_pass1_probe.py through score_lora_b's file swap — probe-b's own scorer",
            },
            "census_50": {
                "gating": False,
                "n": 50,
                "baseline_none": read(PROBE_VERDICT)["census"]["subject_type_distribution"]["None"],
                "rule": (
                    "OBSERVATION ONLY. The base answered None on 25 of the 50 neighbour rows; an"
                    " arm that moves that profile is interesting and moves no bar"
                ),
            },
        },
        "contract": "docs/PROMPT-lora-b.md D2",
        "frozen_when_the_pod_exists": [
            "config/qlora.yaml",
            "src/market_pulse/local_llm.py",
            "src/market_pulse/prompts.py",
            "results/reader_gold_w1_r2.json",
            "results/pass1_probe_b_verdict.json",
            "results/pass1_probe_b_pack.json",
            "results/pass1_sft_arm_a.jsonl",
            "results/pass1_sft_arm_b.jsonl",
            OUT_NAME,
        ],
        "h6": h6(sft, sums),
        "dropped_for_length": sft["census"]["dropped_for_length"],
        "instruments": {
            "config_sha256": summary.sha256_of(QLORA),
            "parser": {
                "entry_point": "market_pulse.prompts.parse_pass1",
                "module": "src/market_pulse/prompts.py",
                "sha256": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "prompts.py"),
            },
            "prompt_sha256": {prompts.PASS1_TASK: prompts.prompt_sha256(prompts.PASS1_TASK)},
            "scorer": {
                "module": "src/market_pulse/scorer.py",
                "sha256": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "scorer.py"),
            },
            "sft_record": {"file": "results/pass1_sft.json", "sha256": summary.sha256_of(SFT)},
            "trainer": {
                "script": "scripts/train_qlora.py",
                "sha256": summary.sha256_of(REPO_ROOT / "scripts" / "train_qlora.py"),
            },
            "transport": {
                "script": "scripts/pass1_pod_runner.py",
                "sha256": summary.sha256_of(REPO_ROOT / "scripts" / "pass1_pod_runner.py"),
                "adapter_flag": (
                    "--adapter mounts the arm's adapter AROUND the model local_llm builds and"
                    " writes <out>.adapter.json beside the evidence BEFORE the first reply. Each"
                    " arm evaluates into its OWN out file: the shipped runner's resume skips every"
                    " unit already answered, so a second arm sharing one file would answer nothing"
                    " and look complete"
                ),
            },
        },
        "kill_clock": [
            {
                "rung": 1,
                "before": "the endpoint exists",
                "rule": f"live A6000-class price > ${PRICE_CEILING_USD_PER_HOUR:.2f}/h at create → STOP, no endpoint",
                "read": "costPerHr in the create response is the meter of record (Dv448)",
            },
            {
                "rung": 2,
                "before": "the model is loaded",
                "rule": "ssh dead-man ≤ 180 s or KILL — the proven gate-0 of pass1-probe",
            },
            {
                "rung": 3,
                "before": "the first optimizer step",
                "rule": f"boot-to-training-start ≤ {BOOT_CEILING_SECONDS} s or KILL (the worst boot measured, 293 s, × 1.5)",
            },
            {
                "rung": 4,
                "before": "the run is allowed to continue",
                "rule": f"s/step > {math.floor(2 * SECONDS_PER_STEP)} s over 5 consecutive log lines → KILL",
            },
            {
                "rung": 5,
                "before": "arm B starts",
                "rule": f"guard reading ≤ ${MILESTONE_USD:.2f} else STOP — arm B does not start and the session closes with arm A",
            },
            {
                "rung": 6,
                "before": "anything",
                "rule": f"absolute session ceiling {CAP_USD / PRICE_CEILING_USD_PER_HOUR} h = cap / price ceiling; `runpod_guard --until` bounds the window",
            },
        ],
        "money": {
            "arithmetic": sums,
            "cap_rule": (
                f"${CAP_USD:.2f} all-in, frozen at the FIRST `pod create`. Raising it is the"
                " operator's word BEFORE any endpoint exists, never after a reading"
            ),
            "cap_usd_all_in": CAP_USD,
            "guard": (
                "PYTHONPATH=src python3.11 scripts/runpod_guard.py --step lora-b --step-cap 6.00"
                " --until <ISO> — read at every milestone, and the reading is what the rungs act on"
            ),
            "meter": {
                **probe["money"]["meter"],
                "worked_example_usd_per_hour": PRICE_CEILING_USD_PER_HOUR,
                "worked_example_rule": (
                    "the kill-clock's own price CEILING, used as the worked example so every figure"
                    " here prices the worst machine this run is allowed to rent. probe-b's own"
                    " example was $0.74/h on a 4090; this run needs an A6000-class card"
                ),
            },
            "reading": probe["money"]["reading"],
            "recovery": {
                "rule": (
                    "ONE pod re-creation, and only after a deletion PROVEN by listing. Never two"
                    " billing endpoints at once — the goal is no parallel spend, whatever the"
                    " letter. Pods, not serverless (16.08)"
                ),
                "there_is_no_mid_arm_checkpoint": {
                    "save_every": int(config["training"]["save_every"]),
                    "arm_steps": {arm: arms[arm]["steps"] for arm in sorted(arms)},
                    "reading": (
                        "`step % save_every` never fires — the arms are"
                        f" {arms['a']['steps']} and {arms['b']['steps']} steps against a"
                        f" save_every of {config['training']['save_every']} — so the only adapter"
                        " written is the one after the loop. A KILL at any rung DURING an arm"
                        " loses that arm whole, and the single re-creation this clause allows"
                        " restarts it from step 0. config/qlora.yaml is frozen law and is not"
                        " edited for this; the fact is registered so the clause is read with it"
                    ),
                },
            },
        },
        "phase": "lora-b",
        "population": {
            "gold": {
                "n": 14,
                "record": "results/reader_gold_w1_r2.json",
                "revision": "r2",
                "rows": gold_rows(),
                "sha256": summary.sha256_of(GOLD),
            },
            "eval_pack": {
                "record": "results/pass1_probe_b_pack.json",
                "sha256": summary.sha256_of(PROBE_PACK),
                "items": len(read(PROBE_PACK)["items"]),
                "rule": (
                    "probe-b's own 64-unit pack, unchanged: 14 gold and 50 census rows. The base's"
                    " per-row verdicts were measured on it and are NOT re-run — the arms are paired"
                    " against a sealed record, on identical instances and the same prompt sha"
                ),
            },
            "base": {
                "record": "results/pass1_probe_b_verdict.json",
                "sha256": summary.sha256_of(PROBE_VERDICT),
                "agreed": read(PROBE_VERDICT)["bars"]["P1_per_comment_agreement"]["agreed"],
                "of": 14,
            },
        },
        "producer": {
            "script": "scripts/write_lora_b_prereg.py",
            "borrowed": {
                "results/prereg_pass1_probe_b.json": summary.sha256_of(PROBE_PREREG),
                "results/pass1_sft.json": summary.sha256_of(SFT),
            },
        },
        "reachability": reachability(sft),
        "return_to_sitting": probe["return_to_sitting"],
        "training": {
            "config": "config/qlora.yaml",
            "config_is_frozen_law": (
                "never edited. The arms differ by a data path and a sampler flag, both of them CLI"
                " arguments recorded here; a hyperparameter moved between the arms would make the"
                " comparison meaningless rather than merely wrong"
            ),
            "epochs": config["training"]["epochs"],
            "effective_batch": config["training"]["micro_batch_size"]
            * config["training"]["grad_accum"],
            "max_seq_len": config["training"]["max_seq_len"],
            "sampler": (
                "class-weighted, w_c = N/(5·n_c) capped at 8.0, computed on the arm's own dataset."
                " Both arms weighted: the ablation is the data, not the sampler. The epoch draws"
                " the dataset's own size WITH replacement, so steps/epoch is unchanged"
            ),
            "seed": config["training"]["seed"],
            "supervision": read(SFT)["supervision"],
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    record = build()
    record["producer"]["sha256"] = summary.sha256_of(Path(__file__))
    out = args.outdir / OUT_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    out.write_text(payload, encoding="utf-8")
    print(f"wrote {OUT_NAME}  sha256 {summary.sha256_of(out)[:16]}…")

    table = record["h6"]
    print(f"\nH6 — {len(table['rows'])} registered numbers re-derived from their formulas\n")
    for row in table["rows"]:
        mark = "ok  " if row["agrees"] else "RED "
        print(
            f"  {mark}{row['name']:28s} registered {str(row['registered'])[:44]:46s} -> {str(row['re_derived'])[:44]}"
        )
    print(f"\n  mismatches: {table['mismatches'] or 'none'}")

    sums = record["money"]["arithmetic"]
    print(
        f"\nWORST CASE {sums['hours']:.3f} h × ${PRICE_CEILING_USD_PER_HOUR:.2f}/h ="
        f" ${sums['worst_case_usd']:.4f} against a cap of ${CAP_USD:.2f}"
        f"  (headroom ${sums['cap_headroom_usd']:.4f})"
    )
    reach = record["reachability"]
    print(
        f"REACH      {reach['to_pass']['agreed_now']} of 14 today; the arm must turn"
        f" {reach['to_pass']['rows_the_arm_must_turn']} of the 5 missed —"
        f" {reach['to_pass']['by_gold_class']}"
    )
    context = reach["the_context_the_gate_carries"]
    print(
        f"CONTEXT    the gate's rows carry {context['gate_rows_with_an_entity_block']}/"
        f"{context['gate_rows']} entity blocks; arm B's training rows carry"
        f" {context['arm_b_rows_with_an_entity_block']}/{context['arm_b_rows']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
