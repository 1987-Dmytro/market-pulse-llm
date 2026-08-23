#!/usr/bin/env python3
"""`results/prereg_lora_c.json` — the DRAFT registration of the rationale-supervised LoRA line.

`docs/PROMPT-lora-c-prep.md`, the operator's rulings (в) and (к) of 2026-08-22. **A draft, not a
seal:** it is frozen by `lora-c-run`'s first `pod create` and by nothing before it, and the two
review gates are still open, so the rationale and synthetic shas in here will move once the team
lead's verdicts land. Every field says which state it is in.

**No price is registered here.** The money block carries FORMULAS over rates this repo has measured,
the cap the ruling set, and — for every rate — the condition that would invalidate it. r1 of
`pass1-window` is what that rule is made of: a number without a run behind it reads as a
measurement forever after ([[projected_rate_versus_measured_rate]]).

**Four reachability blocks, because four things are unreachable as registered** — the smallest class
has no fifth neighbour; no v3 row fits the frozen `max_seq_len`; ARM A has no `молочный_бренд`
target at all, which is what bar 1 turns on; and the pinned trainer refuses a v3 dataset by name.
Each carries its arithmetic and its remedies, and takes none of them: they are the operator's
([[a_registered_bar_may_have_no_producer]], [[an_absolute_bar_needs_a_reachability_state]]).

    PYTHONPATH=src python3.11 scripts/write_lora_c_prereg.py
"""

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_lora_c_data as data  # noqa: E402
import build_lora_c_eval_pack as evalpack  # noqa: E402
import train_qlora as trainer  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402
from market_pulse import pass1_v3, pass2_r2, prompts  # noqa: E402

OUT = REPO_ROOT / "results" / "prereg_lora_c.json"
STATUS = REPO_ROOT / "docs" / "STATUS.md"
SPEC = REPO_ROOT / "docs" / "SPEC.md"

DATA_RECORD = REPO_ROOT / "results" / "lora_c_data.json"
SYNTHETIC_RECORD = REPO_ROOT / "results" / "lora_c_synthetic.json"
EVAL_PACK = REPO_ROOT / "results" / "lora_c_eval_pack.json"
PASS2_PACK = REPO_ROOT / "results" / "lora_c_pass2_pack.json"
TRAIN_FILE = REPO_ROOT / "results" / "pass1_sft_v3_train.jsonl"
RATIONALES = REPO_ROOT / "results" / "rationales_pass1_v1.jsonl"
SYNTHETIC_FILE = REPO_ROOT / "results" / "synthetic_pass1_v1.jsonl"
TOKENS = REPO_ROOT / "results" / "lora_c_tokens.json"
LABELS_R3 = REPO_ROOT / "results" / "labels_pass1_r3.jsonl"
LORA_B = REPO_ROOT / "results" / "prereg_lora_b.json"
PASS2_R2 = REPO_ROOT / "results" / "prereg_pass2_signals_r2.json"
WINDOW_R2 = REPO_ROOT / "results" / "prereg_pass1_window_r2.json"
GOLD = REPO_ROOT / "results" / "reader_gold_w1_r2.json"
HOLDOUT = REPO_ROOT / "results" / "pass1_holdout_100.json"
QLORA = REPO_ROOT / "config" / "qlora.yaml"

RULING_V = (
    "(в) **Затем — (4) LoRA «рассуждение→метка» поверх v2 с (3) синтетикой как армом B** одной"
    " регистрации; цель обучения — из (б)."
)
RULING_K = (
    "(к) **РУЛИНГ 22.08 (вечер) — дизайн `lora-c`:** промпт v3 = v2 + поле `rationale` ПЕРЕД"
    " меткой, одним рендерингом для обучения и инференса; таблица парно в четыре колонки (база v2 ·"
    " база v3 · адаптер A · адаптер B) на одном пуле соседей; рационали для обучающих строк пишет"
    " Claude Code по кодбуку и метке тимлида, тимлид ревьюит все «наши» + ~40 пограничных;"
    " синтетика ~160 (по 40 на класс ошибки) — арм B, тег в provenance, абляция армом A, никогда в"
    " холдаут/голд; из обучения и из пула соседей исключены холдаут-100 и ВСЕ строки 16 референсных"
    " тредов; **бар на арм (один выстрел): холдаут-100 ≥ 64 И сквозной бар 1 = 5/5 И бар 3 = 0 —"
    " все три или КРАСНЫЙ**; отчётно: ячейка «упоминание → категория» на холдауте (18 → ?), dev-200"
    " (fit), 14 золотых (шестой взгляд). Два контракта: `lora-c-prep` ($0, с ревью-гейтом тимлида)"
    " → `lora-c-run` (один A6000, кап **$4.00**)."
)

CAP_USD = 4.00
"""The ruling's own number, and the only money figure this record may carry."""

HOLDOUT_BAR = 64
"""«холдаут-100 ≥ 64». The BEFORE column is base v2 re-measured on the shared pool; the bar is this
registered integer regardless of what that column says ([[a_published_ratio_is_not_the_gates]])."""

PASS_1_SECONDS_PER_CALL = 6.14
PASS_2_SECONDS_PER_THREAD = 97
SECONDS_PER_STEP_REGISTERED = 61.047
SECONDS_PER_STEP_MEASURED = 68.442
SECONDS_PER_STEP_COMPLIANT_SLOW = 121.0


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


AMENDMENT_325_1 = (
    "**`training.max_seq_len` rises 1 408 → 2 816 by a NEW REVISION of `config/qlora.yaml`**"
    " (frozen law; precedent: 1 024 → 1 408, operator, 2026-08-04)."
)
AMENDMENT_325_2 = (
    "**The neighbour-selection rule gains ONE refusal:** a candidate whose whitespace-collapsed,"
    " casefolded text EQUALS the query's own text is refused"
)
AMENDMENT_325_3 = (
    "**STOP 1 is accepted AS BUILT:** 506 rendered training rows, zero real `молочный_бренд`"
    " positives in arm A, the holdout's reachable maximum 98 of 100 with the bar's integer"
    " unchanged, and the nine rows of `@VARUS_channel:10367` stay unrendered"
)


def quoted_spec(text: str) -> str:
    """The same rule as `quoted`, against `docs/SPEC.md` — amendment 3.25 is law, not a briefing.

    The amendment arrived in its own marked block AFTER every sealed pre-registration pin, and
    `write_sku_prereg.registered_law()` strips those blocks before hashing. So the text below is
    read from a part of the file no pin covers, and the only thing standing between this record and
    a paraphrase is this grep ([[verbatim_quotes_must_be_grepped]]).
    """
    if " ".join(text.split()) not in " ".join(SPEC.read_text(encoding="utf-8").split()):
        raise SystemExit(
            f"this quotation is not in {SPEC.name}: {text[:80]!r}… Either the amendment moved or"
            " this record is paraphrasing law. Stop."
        )
    return text


def quoted(text: str) -> str:
    """A ruling, checked back into `docs/STATUS.md` before it is written into a record.

    A quotation nobody grepped is a paraphrase with quotation marks around it, and this record's
    whole authority is those two paragraphs ([[verbatim_quotes_must_be_grepped]]).
    """
    if " ".join(text.split()) not in " ".join(STATUS.read_text(encoding="utf-8").split()):
        raise SystemExit(
            f"this quotation is not in {STATUS.name}: {text[:80]!r}… Either the team lead has"
            " edited the ruling or this record is paraphrasing it. Stop."
        )
    return text


def legs(eval_pack: dict, train_rows: int, synthetic_rows: int) -> dict:
    """Four legs, paired on identical instances. Only two of them take a bar."""
    calls = evalpack.leg_of(eval_pack, "v2")["n"]
    return {
        "base_v2": {
            "adapter": None,
            "prompt": prompts.PASS1_TASK_V2,
            "reads": "results/lora_c_eval_pack.json::legs.v2",
            "eval_calls": calls,
            "bar": None,
            "role": (
                "the BEFORE column, RE-MEASURED on the shared pool. The window's v2 numbers were"
                " taken on the FULL 650-row pool and are report-only context here — a different"
                " neighbour set is a different instrument"
            ),
        },
        "base_v3": {
            "adapter": None,
            "prompt": pass1_v3.PASS1_TASK_V3,
            "reads": "results/lora_c_eval_pack.json::legs.v3",
            "eval_calls": calls,
            "bar": None,
            "role": (
                "the CONTROL. Without it nothing separates «the adapter learned» from «a sentence"
                " of reasoning helped», and the two have different consequences for the next line"
            ),
        },
        "arm_a": {
            "adapter": "QLoRA on the real rows with their rationales",
            "prompt": pass1_v3.PASS1_TASK_V3,
            "reads": "results/lora_c_eval_pack.json::legs.v3",
            "eval_calls": calls,
            "train_rows": train_rows,
            "bar": "the registered three, all-or-RED",
        },
        "arm_b": {
            "adapter": "QLoRA on arm A's rows PLUS the synthetic rows",
            "prompt": pass1_v3.PASS1_TASK_V3,
            "reads": "results/lora_c_eval_pack.json::legs.v3",
            "eval_calls": calls,
            "train_rows": train_rows + synthetic_rows,
            "bar": "the registered three, all-or-RED",
            "ablation": (
                "arm A's rows are a SUBSET of arm B's, so the one variable is the synthetic top-up"
                " — the same shape lora-b used for its r2 top-up. And the asymmetry is the OPPOSITE"
                " of what it looks like: the synthetic rows carry 32 молочный_бренд targets (8 in"
                " each of the four error classes), so synthetic is the ONLY positive supervision"
                " that class gets anywhere in this line. Arm A has none — see"
                " reachability.arm_a_has_no_молочный_бренд_target"
            ),
        },
    }


def bars(data_record: dict) -> dict:
    """The bar per arm — three conditions, one attempt, all of them or RED."""
    return {
        "rule": (
            "holdout-100 agreement ≥ 64 AND end-to-end bar 1 = 5 of 5 AND bar 3 = 0 signals."
            " ALL THREE or RED. Registered per ARM; base v3 takes no bar and is a control column"
        ),
        "attempt": (
            "ONE. No retry, no second draw, no tuning after any eval output is seen. Two arms"
            " against one bar is the multiplicity, and it is the multiplicity the ruling accepted"
        ),
        "P1_holdout_agreement": {
            "threshold": f"≥ {HOLDOUT_BAR} of 100",
            "minimum_agreed": HOLDOUT_BAR,
            "n": 100,
            "scored_field": "subject_type",
            "population": "results/pass1_holdout_100.json",
            "population_sha256": sha(HOLDOUT),
            "before_column": (
                "base v2 RE-MEASURED on the shared pool. The 64/100 the ruling names was read on"
                " the WINDOW pool; the bar is the registered integer regardless of what the"
                " re-measurement says, and both numbers are reported"
            ),
            "gating": True,
            "reachable_maximum": (
                "98 of 100 as this pack stands: two holdout rows of @VARUS_channel:10367 cannot be"
                " rendered (see reachability.the_smallest_class_has_no_fifth_neighbour), so a"
                " perfect run scores 98 and the bar of 64 is still reachable with 34 to spare"
            ),
        },
        "P2_bar_1_flagships": {
            "threshold": "5 of 5 cases",
            "gating": True,
            "scored_by": "score_pass2_signals.bar_states, through results/prereg_pass2_signals_r2.json",
            "input": "results/lora_c_pass2_pack.json, rebuilt per leg from that leg's pass-1 out-file",
            "before": "4 of 5 — pass2-signals-r2, and the one miss is F2a",
            "reachability": (
                "F2a was UNREACHABLE in r2 by construction: pass 1 labelled its only cited row"
                " `сеть_ритейлер`, so the filter never handed pass 2 the comment the signal is"
                " made of. THIS line is the one that can move it — a pass-1 adapter that relabels"
                " that row is exactly what would make 5 of 5 reachable. That is why the bar is"
                " registered at 5 and not at 4"
            ),
        },
        "P2_bar_3_noise": {
            "threshold": "0 signals",
            "gating": True,
            "scored_by": "score_pass2_signals.bar_states, through results/prereg_pass2_signals_r2.json",
            "before": "2 signals — pass2-signals-r2, both from @VARUS_channel:10366",
            "the_case": (
                "N2 carries four rows pass 1 labelled `сеть_ритейлер` in a giveaway thread. Pass 2"
                " under strict authority cannot drop them, so the bar is a reading of PASS 1 —"
                " which is what makes it a legitimate bar for this line and not for the last one"
            ),
        },
        "bar_2_entity_cases": {
            "gating": False,
            "state": "INHERITED and reported «held»",
            "why": (
                "its cases are resolved from the READER's bought verdicts, which no pass-1 adapter"
                " moves. Re-scoring it would publish a number this line did not measure"
            ),
        },
        "report_only": {
            "the_mention_cell": {
                "what": (
                    "`не_наш_рынок → категория_личное` on holdout-100 — the cell this whole line"
                    " targets. REPORTED, never gated"
                ),
                "before": "18 of 52",
                "after_is_out_of_50_and_not_52": (
                    "BOTH holdout rows that cannot be rendered — @VARUS_channel:10367:20985 and"
                    " :21005 — are labelled `не_наш_рынок`, so the AFTER column is answered on 50"
                    " of the 52 and the two columns have different denominators. The gated bar got"
                    " its reachability note (98 of 100) and this cell had none; quoting «18 → X»"
                    " without it would compare a rate to a count"
                    " ([[the_fix_widened_the_denominator]], [[correcting_gold_moves_the_denominator]])"
                ),
                "denominator_before": 52,
                "denominator_after": 50,
            },
            "our_on_holdout": (
                "6 of 8 before, and the denominator does NOT move — neither unrenderable row is"
                " «our», both are `не_наш_рынок`"
            ),
            "dev_200": (
                "TRAINING FIT only. dev-200's «our» rows are the training set's «our» rows now, so"
                " its agreement is not an eval reading and may never be quoted as one"
            ),
            "gold_14": (
                "the SIXTH look. A census row with multiplicity, NEVER a bar — docs/STATUS.md"
                " п. 1 (д). All 14 are inside E because they are inside the reference threads"
            ),
            "per_class_tables": "agreement by subject_type, both arms and both bases",
            "pass_2_tables": "the DROP table and the subject_doubt table, per leg",
            "arm_a_vs_arm_b": "the ablation, on the same instruments",
        },
        "consequence": (
            "a red bar is an ANSWER. If no arm takes all three, the line closes on the"
            " pre-registered consequence and nothing ships — the shape lora-b's registration used"
        ),
        "reachability_note": data_record["unreachable"]["cause"],
    }


def money(eval_pack: dict, data_record: dict, train_rows: int, synthetic_rows: int) -> dict:
    """LEFT OPEN by the contract: formulas, named rates, and no sum.

    Every rate here was measured on something, and for two of the three the thing it was measured on
    is NOT what this line will run. Those two carry the condition that invalidates them rather than
    a correction — a corrected rate would be a price, and this record may not register one.
    """
    config = yaml.safe_load(trainer.CONFIG.read_text(encoding="utf-8"))
    settings = config["training"]
    micro, accum, epochs = (
        settings["micro_batch_size"],
        settings["grad_accum"],
        settings["epochs"],
    )
    calls = evalpack.leg_of(eval_pack, "v2")["n"]
    steps = {
        "arm_a": math.floor(math.ceil(train_rows / micro) / accum) * epochs,
        "arm_b": math.floor(math.ceil((train_rows + synthetic_rows) / micro) / accum) * epochs,
    }
    return {
        "state": "OPEN — no price is registered here. lora-c-run derives it and seals it",
        "cap_usd_all_in": CAP_USD,
        "cap_rule": (
            "the operator's ruling (к): «один A6000, кап $4.00». Raising it is the operator's word"
            " BEFORE any endpoint exists, never after a reading"
        ),
        "hard_stop_seconds": (
            "TO BE DERIVED in lora-c-run's contract, from the cap and the live price at create."
            " Registering one here would be a number with no run behind it"
        ),
        "formulas": {
            "eval_seconds_per_leg": f"{calls} calls × <pass-1 s/call>",
            "pass_2_seconds_per_leg": (
                f"<threads with at least one filtered row> × {PASS_2_SECONDS_PER_THREAD} s/thread"
            ),
            "training_seconds_per_arm": "<steps> × <s/step>",
            "steps_rule": (
                "floor(ceil(n / micro_batch_size) / grad_accum) × epochs — the number of"
                " optimizer.step() calls. `train_qlora.train` steps only when `seen % accum == 0`"
                " over MICRO-batches, so each epoch's leftover micro-batches never complete a group"
                " and their gradients carry into the next epoch's first step (lora-b's Dv576: 62"
                " run against 64 registered)"
            ),
            "steps": steps,
            "steps_the_other_number": {
                "value": {
                    "arm_a": math.ceil(train_rows / (micro * accum)) * epochs,
                    "arm_b": math.ceil((train_rows + synthetic_rows) / (micro * accum)) * epochs,
                },
                "rule": "ceil(n / (micro × accum)) × epochs — `train_qlora.train`'s own `planned`",
                "what_it_drives": (
                    "the cosine schedule's total and its warmup, and the progress display. It is a"
                    " REAL number of this run and it is NOT the step count the money formula wants"
                ),
                "why_both_are_here": (
                    "one input with two values gets quoted kindly, and this line has already made"
                    " that mistake five times. Both are named so no reader has to choose"
                    " ([[two_values_for_one_input_get_quoted_kindly]])"
                ),
            },
            "eval_calls_per_leg": calls,
            "legs": 4,
        },
        "rates_and_what_would_invalidate_them": {
            "pass_1_seconds_per_call": {
                "value": PASS_1_SECONDS_PER_CALL,
                "source": "results/prereg_pass1_window_r2.json::money.arithmetic.seconds_per_call.charged",
                "derivation": "mean(probe-b) × mean(dev v2) / mean(dev base) = 6.135572, rounded up",
                "measured_on": (
                    "NOT v2. The level comes from pass1-probe-b's 64 paid rows at base V1"
                    " (5.161578 s/call); only the UPLIFT ratio 2.72578/2.293075 is a v2"
                    " measurement, and 5.161578 × that = 6.135572 re-derives exactly. No v2 request"
                    " was ever measured near 6.14 ([[a_smoke_drawn_from_the_exam_is_not_a_rate_sample]])"
                ),
                "the_window_pod_measured": 2.694083,
                "invalidating_condition": (
                    "this rate was measured on v2 requests. Three of the four legs send V3, whose"
                    " widest E request is"
                    f" {eval_pack['length']['v3']['widest']} characters against v2's"
                    f" {eval_pack['length']['v2']['widest']}. Carrying it unchanged for v3 is the"
                    " same class of error as the training rate below"
                    " ([[the_smokes_rate_carries_the_smokes_transport]]). It is safe as a"
                    " conservative CEILING and wrong as a ratio — an earlier version of this field"
                    " said «floor», which is the dangerous direction under a cap. Empirically it"
                    " behaves as a ceiling: 6.14 is 2.279× the window pod's direct v2 reading of"
                    " 2.694083, and about 2× a width-scaled estimate for v3 (2.694083 × 8894/7781"
                    " = 3.079). The pod-class headroom already inside the charge is an order of"
                    " magnitude larger than the 14 % width growth this condition is about"
                ),
            },
            "pass_2_seconds_per_thread": {
                "value": PASS_2_SECONDS_PER_THREAD,
                "source": "results/prereg_pass2_signals_r2.json::money.arithmetic.seconds_per_call",
                "derivation": "ceil(58.07 × 1.67) = 97 — the smoke MAX × pass 1's pod-class spread",
                "the_run_measured": 23.760,
                "invalidating_condition": (
                    "r2 realised 23.760 s/thread against 97 charged — 0.245 of the charge — and it"
                    " measured the pod-class spread on this decode DIRECTLY at 1.008, not the 1.67"
                    " borrowed from pass 1. lora-c-run has a direct reading available and should"
                    " use it — **with r2's own caveat attached: n = 1, and it is the shortest of"
                    " the five replies** (docs/reports/pass2-signals-r2.md, Dv722). 97 is carried"
                    " here because it is what is REGISTERED, and a lower charge is a decision that"
                    " belongs in that contract"
                ),
            },
            "training_seconds_per_step": {
                "registered_by_lora_b": SECONDS_PER_STEP_REGISTERED,
                "measured_on_arm_a": SECONDS_PER_STEP_MEASURED,
                "compliant_slow_ceiling": SECONDS_PER_STEP_COMPLIANT_SLOW,
                "compliant_slow_rule": (
                    "121.0 s/step never trips lora-b's registered 122 s watchdog (kill_clock rung"
                    " 4, «s/step > 122 s over 5 consecutive log lines»). **It is NOT a rate at"
                    " which every rung says GO:** in lora-b's own worked examples the entry at"
                    " 121.0 carries verdict KILL, and the GO belongs to"
                    " `compliant_slow_by_the_contracts_letter`, which lora-b describes as «the path"
                    " the rung exists to close». So 121.0 is the rate that slips the WATCHDOG and"
                    " is caught by the PROJECTION — and lora-c has no 122 s watchdog of its own,"
                    " which is the real reason it cannot be carried unexamined"
                ),
                "sources": {
                    "61.047": "results/prereg_lora_b.json::money.arithmetic.seconds_per_step",
                    "68.442": "results/lora_b_run.json::measured_seconds_per_step — NOT the prereg;"
                    " grep for it there returns zero",
                    "121.0": "results/prereg_lora_b.json::money.arithmetic.cumulative"
                    ".projection_gate.worked_examples.compliant_slow",
                },
                "invalidating_condition": (
                    "TWO of the three are readings, and both on sequences of at most 1 222 tokens;"
                    " 121.0 is not a reading at all but a worked example constructed from the 122 s"
                    " watchdog. The length condition binds on 61.047 and 68.442"
                    " (results/prereg_lora_b.json::dropped_for_length.longest_kept). v3's rows are"
                    f" {data_record['tokens']['by_ratio']['min_observed']['min']}–"
                    f"{data_record['tokens']['by_ratio']['registered_bound_max']['max']} tokens at"
                    " the measured ratio range. config/qlora.yaml's own comment says raising"
                    " max_seq_len «changes no step time and no memory except on the batches that"
                    " need it» — here EVERY batch needs it, so none of the three is this line's"
                    " rate. Named as inherited readings, never used as the formula's input"
                ),
            },
        },
        "what_this_record_deliberately_does_NOT_carry": (
            "a worst_case_usd, a total_seconds and a projected price. r1 of pass1-window registered"
            " a rate it had not measured and the number outlived the correction"
        ),
    }


def reachability(data_record: dict, counted: dict) -> dict:
    """Three things this line cannot reach as registered, each with its arithmetic and its remedies."""
    tokens = data_record["tokens"]
    return {
        "the_smallest_class_has_no_fifth_neighbour": data_record["unreachable"],
        "three_rows_do_not_fit_max_seq_len": {
            "state": (
                "amendment 3.25 (1) raised the ceiling 1 408 -> 2 816 and ordered a reality check"
                " before `lora-c-run` buys anything. The check RAN, at $0, through the model's own"
                " tokenizer at the pinned revision — and it STOPS the line back to the operator"
            ),
            "counted": counted,
            "what_the_model_said_and_the_count_says": (
                f"the three-ratio model puts the widest row at"
                f" {tokens['by_ratio']['registered_bound_max']['max']} tokens and reports"
                f" {tokens['by_ratio']['registered_bound_max']['over_max_seq_len']} of"
                f" {tokens['by_ratio']['registered_bound_max']['of']} over {tokens['max_seq_len']}."
                f" The TOKENIZER counts {counted['pod_count']['max']}"
                f" ({counted['pod_count_plus_template_slack']['max']} with TEMPLATE_SLACK) and"
                f" {counted['rows_over_the_stop_threshold']} rows over the amendment's 2 800 stop."
                " The model under-predicts by"
                f" {counted['the_model_this_replaces']['the_model_underpredicts_by']} tokens on the"
                " widest row, which is exactly the hazard 3.25 (1) ordered the check against"
                " (Dv757: a ratio is a MODEL carried across a change of row length)"
            ),
            "not_caused_by_this_contract": (
                "measured on the rows as they stood at 97548df — before the gate-1 rewrites and"
                " before amendment 3.25 (2)'s neighbour refusal — the same tokenizer counts 2 974"
                " with TWO rows over 2 800. The rebuild moved the widest row by one token"
            ),
            "the_operators_own_next_rung": (
                "3.25 (1)'s own words: «the next rung is 3 072 and it is one word, not a redesign»."
                f" {counted['pod_count_plus_template_slack']['max']} fits under 3 072 with"
                f" {3072 - counted['pod_count_plus_template_slack']['max']} tokens to spare. This"
                " registration does NOT take that rung: raising frozen law is the operator's word"
            ),
            "rows_over": counted["over"],
            "the_model_this_ceiling_was_derived_from": {
                **{
                    key: tokens[key]
                    for key in (
                        "max_seq_len",
                        "max_seq_len_source",
                        "chars_prompt_plus_target",
                        "lora_b_v1_rows_for_comparison",
                        "by_ratio",
                        "remedies_named_none_taken",
                    )
                },
                "superseded_by": (
                    "results/lora_c_tokens.json — a count, not a model. Kept because 2 816 was"
                    " DERIVED from this table and a reader has to be able to see what was derived"
                    " from what"
                ),
                "what_it_gets_wrong": (
                    "measured on probe rows of 2 778–3 923 characters and applied to rows of"
                    f" {tokens['chars_prompt_plus_target']['min']}–"
                    f"{tokens['chars_prompt_plus_target']['max']}, so the chat template's fixed"
                    " part scales with content it should not scale with. On the widest row it is"
                    f" {counted['the_model_this_replaces']['the_model_underpredicts_by']} tokens"
                    " LOW, and the direction was called ambiguous when it was only a model"
                    " ([[a_reproducible_probe_can_be_unrepresentative]])"
                ),
                "the_pods_own_count": (
                    "train_qlora.encode_pass1 tokenizes apply_chat_template(...) and refuses on"
                    " len(context) + len(target). That expression is what"
                    " results/lora_c_tokens.json now evaluates directly, by the same calls in the"
                    " same order, so the projection and the count measure one quantity. The"
                    " pod-side refusal still has not RUN — `load_sft` refuses on the task name"
                    " first, which is STOP 3's own evidence — and the mood stays WOULD"
                ),
            },
        },
        "arm_a_has_no_молочный_бренд_target": {
            "cause": (
                "the pool's single молочный_бренд row is one of the nine that cannot be rendered"
                " (see the_smallest_class_has_no_fifth_neighbour), so arm A's 506 rows carry ZERO"
                " targets of that class and `train_qlora.class_weights` does not even contain the"
                " key — `sampling_order` can never draw one"
            ),
            "arm_a_targets": 0,
            "arm_b_targets": 32,
            "arm_b_rule": "8 in each of the four error classes, by the ±2 balance rule",
            "arm_a_class_weights": "null · категория_личное · не_наш_рынок · сеть_ритейлер — FOUR",
            "arm_b_weight_on_the_class": round(666 / (5 * 32), 6),
            "what_it_does_to_bar_1": (
                "bar 1 = 5 of 5 turns on F2a, and F2a turns on relabelling msg 580124 from"
                " `сеть_ритейлер` to `молочный_бренд` — the reading the gold gives it. An adapter"
                " with no training target carrying that label cannot learn to emit it, so **bar 1"
                " is near-unreachable for arm A and reachable for arm B**, by the same arithmetic."
                " The bar is NOT lowered for arm A: it is registered per arm at 5 of 5 and this"
                " block is why a RED there would say something different from a RED on arm B"
                " ([[an_absolute_bar_needs_a_reachability_state]])"
            ),
            "reported_not_remedied": (
                "the remedies are the ones listed under the_smallest_class_has_no_fifth_neighbour"
                " — this is that fact read forward into the bars, not a second decision"
            ),
        },
        "the_pinned_trainer_refuses_a_v3_dataset": {
            "instrument": "scripts/train_qlora.py",
            "sha256": data.sha_text(
                (REPO_ROOT / "scripts" / "train_qlora.py").read_text(encoding="utf-8")
            ),
            "pinned_by": [
                "results/prereg_lora_b.json::instruments.trainer.sha256",
                "results/lora_b_verdict.json",
            ],
            "refusals_driven_at_zero_dollars": [
                {
                    "where": "train_qlora.load_sft",
                    "message": (
                        "@VARUS_channel:10349#20649: task 'pass1_comment_gm4_v3' is not"
                        " 'pass1_comment_gm4_v1' — the FIRST row of the shipped file, driven today"
                    ),
                },
                {
                    "where": "train_qlora.build_pass1",
                    "message": (
                        "«…is not a registered dataset. Stop rather than train on bytes nobody"
                        " pre-registered.» — reached only by giving the row v1's task name first,"
                        " because build_pass1 calls load_sft BEFORE its own sha check, so the"
                        " task-name guard always fires first on the shipped file. Stated because"
                        " lora-c-run's sibling trainer is scoped by these two messages and a"
                        " message quoted without the state that produces it is not evidence"
                    ),
                },
            ],
            "what_PASSES": (
                "the learn_chars guard and the prompt_sha256 equality both pass. The v3 target's"
                " supervised head still ends at the subject_type value plus its separator — the"
                " prefix arithmetic in build_lora_c_data.target_v3 preserves the +1 END-offset rule"
                " — and the sha the trainer compares is v1's prompt, which has not moved"
            ),
            "remedy_named_not_taken": (
                "a SIBLING trainer that imports train_qlora and re-binds the two guards, the way"
                " scripts/gate_pass2_signals_r2.py is a sibling of the r1 gate. Editing the pinned"
                " file turns `make check` red on lora-b's own sealed artifacts. lora-c-run's FIRST"
                " $0 deliverable, and registering train_qlora.py as THE trainer without saying this"
                " would be a bar with no producer"
            ),
        },
    }


def build() -> dict:
    data_record = json.loads(DATA_RECORD.read_text(encoding="utf-8"))
    counted = json.loads(TOKENS.read_text(encoding="utf-8"))
    synthetic_record = json.loads(SYNTHETIC_RECORD.read_text(encoding="utf-8"))
    eval_pack = json.loads(EVAL_PACK.read_text(encoding="utf-8"))
    pass2_pack = json.loads(PASS2_PACK.read_text(encoding="utf-8"))
    lora_b = json.loads(LORA_B.read_text(encoding="utf-8"))
    train_rows = data_record["rows"]["rendered"]
    synthetic_rows = synthetic_record["rows"]
    rows = [json.loads(one) for one in TRAIN_FILE.read_text(encoding="utf-8").splitlines() if one]

    return {
        "phase": "lora-c",
        "state": "DRAFT — frozen only by lora-c-run's first `pod create`",
        "contract": "docs/PROMPT-lora-c-prep.md",
        "authority": {
            "record": "docs/STATUS.md «Открытые решения» п. 1",
            "ruling_v": quoted(RULING_V),
            "ruling_k": quoted(RULING_K),
            "amendment_3_25": {
                "record": "docs/SPEC.md, the `amendment-3.25` marked block",
                "sha256_of_the_spec": sha(SPEC),
                "1_max_seq_len": quoted_spec(AMENDMENT_325_1),
                "2_the_neighbour_refusal": quoted_spec(AMENDMENT_325_2),
                "3_stop_1_as_built": quoted_spec(AMENDMENT_325_3),
                "quotation_rule": (
                    "all three clauses are grepped back into docs/SPEC.md on every build of this"
                    " file, whitespace-normalised, by `quoted_spec`"
                ),
            },
            "quotation_rule": (
                "both strings are grepped back into docs/STATUS.md on every build of this file,"
                " whitespace-normalised. A ruling quoted from memory is a paraphrase in quotation"
                " marks"
            ),
        },
        "question": (
            "does rationale-supervised QLoRA on pass 1 fix the subject-attribution errors pass 2"
            " measured — brand ↔ retailer, a retailer in a non-dairy context, non-dairy «brands»,"
            " and mention-vs-about — WITHOUT learning the prior the way line B did"
        ),
        "population": {
            "pool": {
                "rows": data_record["population"]["pool"],
                "arithmetic": data_record["population"]["arithmetic"],
                "distribution": data_record["population"]["distribution"],
                "rule": "ONE pool for every leg — the paired table compares prompts and adapters",
                "record": "results/lora_c_data.json",
            },
            "train": {
                "rows": train_rows,
                "refused": data_record["rows"]["refused"],
                "distribution": data_record["rows"]["distribution"],
                "file": "results/pass1_sft_v3_train.jsonl",
                "sha256": sha(TRAIN_FILE),
            },
            "synthetic": {
                "rows": synthetic_rows,
                "file": "results/synthetic_pass1_v1.jsonl",
                "sha256": sha(SYNTHETIC_FILE),
                "balance": synthetic_record["balance"]["by_class"],
                "contamination_is_empty": all(
                    not synthetic_record["contamination"][name]
                    for name in (
                        "labelled_rows",
                        "holdout_rows",
                        "reference_thread_comments",
                        "gold_quotes",
                    )
                ),
            },
            "eval_set_E": {
                "n": eval_pack["made"]["e"],
                "rendered": evalpack.leg_of(eval_pack, "v2")["n"],
                "arithmetic": eval_pack["made"]["arithmetic"],
                "file": "results/lora_c_eval_pack.json",
                "sha256": sha(EVAL_PACK),
            },
            "reference_threads": data_record["population"]["reference_threads"],
            "reference_threads_carrying_labelled_rows": data_record["population"][
                "reference_threads_carrying_labelled_rows"
            ],
        },
        "legs": legs(eval_pack, train_rows, synthetic_rows),
        "bars": bars(data_record),
        "reachability": reachability(data_record, counted),
        "training": {
            "inherited_from": "results/prereg_lora_b.json — by NAME, and every number says so",
            "config": "config/qlora.yaml — FROZEN law",
            "config_sha256": sha(QLORA),
            "config_revision": 2,
            "config_agrees_with_lora_b": sha(QLORA) == lora_b["instruments"]["config_sha256"],
            "config_agrees_with_lora_b_reading": (
                "FALSE ON PURPOSE, and the field publishes the false value rather than being"
                " deleted. Amendment 3.25 (1) revised config/qlora.yaml in place — max_seq_len"
                " 1 408 -> 2 816 — and line B's pin on revision 1 is NEVER re-taken, so"
                " results/prereg_lora_b.json, results/lora_b_verdict.json and"
                " results/pass1_sft.json now describe a revision that is no longer on disk. That is"
                " what a sealed record doing its job looks like. Line B's DATA does not move with"
                " the number: driving build_pass1_sft.py at revision 2 rebuilds both sealed arms"
                " and the smoke pack BYTE-IDENTICAL, because its longest kept row is 1 222 tokens"
                " and it dropped 0 rows for length at 1 408"
            ),
            "config_lora_b_revision_1_sha256": lora_b["instruments"]["config_sha256"],
            "tokenizer_reality_check": {
                "authority": "docs/SPEC.md amendment 3.25 (1)",
                "file": "results/lora_c_tokens.json",
                "sha256": sha(TOKENS),
                "ran": True,
                "instrument": counted["instrument"],
                "pod_count": counted["pod_count"],
                "with_template_slack": counted["pod_count_plus_template_slack"],
                "stop_threshold": counted["stop_threshold"],
                "rows_over": counted["rows_over_the_stop_threshold"],
                "verdict": counted["verdict"],
            },
            "rank": yaml.safe_load(QLORA.read_text(encoding="utf-8"))["lora"]["r"],
            "alpha": yaml.safe_load(QLORA.read_text(encoding="utf-8"))["lora"]["alpha"],
            "learning_rate": yaml.safe_load(QLORA.read_text(encoding="utf-8"))["optimizer"][
                "learning_rate"
            ],
            "epochs": yaml.safe_load(QLORA.read_text(encoding="utf-8"))["training"]["epochs"],
            "read_not_typed": (
                "every one of these is READ from config/qlora.yaml at build time. lora-b's record"
                " quotes the same file, and two spellings of a frozen constant are two answers the"
                " day one of them moves ([[a_moved_constant_fails_green]])"
            ),
            "sampler": data_record["sampler"],
            "supervision": {
                "field": "the rationale AND `subject_type`",
                "boundary": (
                    "build_pass1_sft.target_for, CALLED. The rationale is written FIRST and the"
                    " supervised span runs from the object's opening brace through the separator"
                    " after the subject_type value — so the loss lands on the reasoning before it"
                    " lands on the class, which is the whole of the line"
                ),
                "not_supervised": "subject_id and stance — the team lead labelled neither",
                "vs_lora_b": (
                    "line B supervised `subject_type` ALONE on a set that is 52 % `не_наш_рынок`"
                    " and the adapter learned the marginal. That is the failure this design is a"
                    " response to, and the cue-in-text rule is what keeps the rationale from being"
                    " the label wearing a sentence"
                ),
            },
        },
        "instruments": {
            "module_v3": {
                "path": "src/market_pulse/pass1_v3.py",
                "sha256": data.sha_text(
                    (REPO_ROOT / "src" / "market_pulse" / "pass1_v3.py").read_text(encoding="utf-8")
                ),
            },
            "prompt_sha256": {
                prompts.PASS1_TASK: prompts.prompt_sha256(prompts.PASS1_TASK),
                prompts.PASS1_TASK_V2: prompts.prompt_sha256(prompts.PASS1_TASK_V2),
                pass1_v3.PASS1_TASK_V3: pass1_v3.prompt_sha256(pass1_v3.PASS1_TASK_V3),
            },
            "v3_extends_v2": pass1_v3.PASS1_COMMENT_PROMPT_V3.startswith(
                prompts.PASS1_COMMENT_PROMPT_V2
            ),
            "parser": {
                "path": "src/market_pulse/prompts.py",
                "sha256": data.sha_text(
                    (REPO_ROOT / "src" / "market_pulse" / "prompts.py").read_text(encoding="utf-8")
                ),
                "note": "PINNED and untouched — parse_pass1_v3 wraps it, never edits it",
            },
            "scorer": {
                "path": "src/market_pulse/scorer.py",
                "sha256": data.sha_text(
                    (REPO_ROOT / "src" / "market_pulse" / "scorer.py").read_text(encoding="utf-8")
                ),
            },
            "trainer": {
                "path": "scripts/train_qlora.py",
                "sha256": data.sha_text(
                    (REPO_ROOT / "scripts" / "train_qlora.py").read_text(encoding="utf-8")
                ),
                "state": "PINNED and it REFUSES a v3 dataset — see reachability",
            },
            "packs": {
                "results/lora_c_data.json": sha(DATA_RECORD),
                "results/lora_c_synthetic.json": sha(SYNTHETIC_RECORD),
                "results/lora_c_eval_pack.json": sha(EVAL_PACK),
                "results/lora_c_pass2_pack.json": sha(PASS2_PACK),
                "results/pass1_sft_v3_train.jsonl": sha(TRAIN_FILE),
            },
            "written_inputs": {
                "results/rationales_pass1_v1.jsonl": {
                    "sha256": sha(RATIONALES),
                    "author": "claude-code",
                    "reviewed": data_record["rationales"]["reviewed"],
                    "review_gate": "docs/reviews/lora-c-rationales-verdict.md",
                    "verdict_present": (
                        REPO_ROOT / "docs" / "reviews" / "lora-c-rationales-verdict.md"
                    ).exists(),
                },
                "results/synthetic_pass1_v1.jsonl": {
                    "sha256": sha(SYNTHETIC_FILE),
                    "author": "claude-code",
                    "reviewed": synthetic_record["reviewed"],
                    "review_gate": "docs/reviews/lora-c-synthetic-verdict.md",
                    "verdict_present": (
                        REPO_ROOT / "docs" / "reviews" / "lora-c-synthetic-verdict.md"
                    ).exists(),
                },
                "results/labels_pass1_r3.jsonl": {
                    "sha256": sha(LABELS_R3),
                    "author": "the TEAM LEAD — the fifth named ruling of the gate-1 verdict",
                    "reviewed": [True],
                    "review_gate": "docs/reviews/lora-c-rationales-verdict.md",
                    "verdict_present": (
                        REPO_ROOT / "docs" / "reviews" / "lora-c-rationales-verdict.md"
                    ).exists(),
                    "rows": 1,
                    "kind": (
                        "a DELTA over r1+r2 on the (thread, msg_id) key, last wins. It draws no"
                        " unit, so it has no pack and build_pass1_sft.labelled_units's"
                        " pack-equals-labels refusal never sees it"
                    ),
                    "scope": (
                        "the lora-c shared pool ONLY. results/pass1_sft_arm_a.jsonl and"
                        " results/pass1_sft_arm_b.jsonl are sealed at bytes taken before this"
                        " correction existed and are never re-derived to follow a later ruling"
                    ),
                    "provenance": "results/labels_pass1_r3_provenance.json",
                    "moved": data_record["population"]["labels_r3"]["moved"],
                },
            },
            "pass_2": {
                "module": "src/market_pulse/pass2_r2.py",
                "sha256": data.sha_text(
                    (REPO_ROOT / "src" / "market_pulse" / "pass2_r2.py").read_text(encoding="utf-8")
                ),
                "prompt_sha256": {
                    pass2_r2.PASS2_TASK_V1: pass2_r2.prompt_sha256(pass2_r2.PASS2_TASK_V1)
                },
                "registration": "results/prereg_pass2_signals_r2.json",
                "registration_sha256": sha(PASS2_R2),
                "scorer": "scripts/score_pass2_signals.py::bar_states",
            },
            "gold": {"record": "results/reader_gold_w1_r2.json", "sha256": sha(GOLD)},
            "holdout": {"record": "results/pass1_holdout_100.json", "sha256": sha(HOLDOUT)},
        },
        "money": money(eval_pack, data_record, train_rows, synthetic_rows),
        "ready_to_price": {
            "rule": "every number here comes from a file this contract built, at $0",
            "train_rows": train_rows,
            "train_rows_arm_b": train_rows + synthetic_rows,
            "eval_calls_per_leg": evalpack.leg_of(eval_pack, "v2")["n"],
            "legs": 4,
            "pass_2_threads_per_leg": pass2_pack["population"][
                "threads_with_at_least_one_filtered_row"
            ],
            "pass_2_threads_rule": (
                "measured on the WINDOW's own out-file. Each leg rebuilds its own pack, so an arm"
                " that relabels a thread into or out of the filter moves this number"
            ),
            "tokens_per_sft_row": {
                "median": data_record["tokens"]["by_ratio"]["registered_bound_max"]["median"],
                "max": data_record["tokens"]["by_ratio"]["registered_bound_max"]["max"],
                "min": data_record["tokens"]["by_ratio"]["registered_bound_max"]["min"],
                "bound": "build_pass1_sft.bound_tokens at the worst measured tokens-per-character",
            },
            "chars_per_sft_row": {
                "median": sorted(len(one["prompt"]) + len(one["target"]) for one in rows)[
                    len(rows) // 2
                ],
                "max": max(len(one["prompt"]) + len(one["target"]) for one in rows),
            },
        },
        "frozen_when_the_pod_exists": [
            "results/prereg_lora_c.json",
            "results/lora_c_data.json",
            "results/lora_c_synthetic.json",
            "results/pass1_sft_v3_train.jsonl",
            "results/rationales_pass1_v1.jsonl",
            "results/synthetic_pass1_v1.jsonl",
            "results/lora_c_eval_pack.json",
            "results/lora_c_pass2_pack.json",
            "src/market_pulse/pass1_v3.py",
            "config/qlora.yaml",
        ],
        "producer": {
            "script": "scripts/write_lora_c_prereg.py",
            "sha256": data.sha_text(Path(__file__).read_text(encoding="utf-8")),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    record = build()
    args.out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {summary.rel(args.out)}  sha256 {sha(args.out)[:16]}…  DRAFT")
    print(
        f"  cap ${record['money']['cap_usd_all_in']:.2f} · money block {record['money']['state']}"
    )
    print(f"  bars: {record['bars']['rule']}")
    print(f"  steps: {record['money']['formulas']['steps']}")
    for name in record["reachability"]:
        print(f"  reachability: {name}")
    gates = record["instruments"]["written_inputs"]
    for path, cell in gates.items():
        print(f"  {path}: reviewed={cell['reviewed']} verdict_present={cell['verdict_present']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
