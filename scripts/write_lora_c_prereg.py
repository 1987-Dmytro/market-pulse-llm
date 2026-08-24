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
ARM_B_FILE = REPO_ROOT / "results" / "pass1_sft_v3_arm_b.jsonl"
ARM_B_RECORD = REPO_ROOT / "results" / "lora_c_arm_b.json"
STOCK_PROBE = REPO_ROOT / "results" / "lora_c_stock_probe.json"
MARKER_CENSUS_PACK = REPO_ROOT / "results" / "lora_c_marker_census_pack.json"
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

RULING_N_RENDERING = (
    "синтетический запрос рендерится ТЕМ ЖЕ правилом на ТОМ ЖЕ пуле 515 (закон уже запрещает"
    " синтетику только как СОСЕДА; запрет двойника действует)"
)
RULING_N_PASS_2 = (
    "проход-2 в ране — ТОЛЬКО для армов (2 ноги, не 4): база v2 сквозной уже измерена (r2: 4/5 ·"
    " 2), база v3 бара не берёт — экономия ~$0.47 по заряду."
)
"""The team lead's two design rulings of 2026-08-24, `docs/STATUS.md` п. 1 (н). Both are grepped
back into that file by :func:`quoted` on every build; the first is what makes arm B renderable at
all, the second is what this money block is re-derived under."""

RULING_O_CAP = (
    "кап lora-c-run **остаётся $4.00** (оба существующих замера s/step влезают по фактической цене;"
    " смок решает, рунг проекции убивает честно)"
)
RULING_O_CARD = (
    "карта — **RTX PRO 4500, 32 GB, $0.72/ч, EU-RO-1** (A6000 в датацентре тома none; 32 GB —"
    " запас против OOM при замороженном micro_batch; фолбэк 4090 преавторизован)"
)
RULING_O_MARKER = (
    "ложная строка топика в синтетических заголовках заменяется выделенной константой (продовая"
    " строка NO_POST_TEXT в синтетике запрещена); конфаунд маркера принят и именован; в ран"
    " добавлен отчётный маркер-ценз (~$0.05) — отделяет «не помогло» от «выучил маркер»"
)
"""Ruling (о) of 2026-08-24, `docs/STATUS.md` п. 1, taken at the acceptance of `lora-c-armb` and on
the numbers that contract derived. Three clauses, each grepped back into STATUS by :func:`quoted`:
the cap stands at $4.00, the card is named with its price and its region, and the false production
string is forbidden inside a synthetic header. It is the ruling this r2 registration exists to
record, and the first one in this line that names a card the repo has never measured."""

CAP_USD = 4.00
"""The ruling's own number, and the only money figure this record may carry."""

HOLDOUT_BAR = 64
"""«холдаут-100 ≥ 64». The BEFORE column is base v2 re-measured on the shared pool; the bar is this
registered integer regardless of what that column says ([[a_published_ratio_is_not_the_gates]])."""

PASS_1_SECONDS_PER_CALL = 6.14
PASS_2_SECONDS_PER_THREAD = 97
PASS_2_LEGS = 2
"""Ruling (н) of 24.08: pass 2 runs for the two ARMS only. `lora-c-run` charged four and said so —
the contract's fixed part summed `4 × 11 × 97` while its order of operations named pass 2 twice —
and named the difference rather than choosing quietly. The team lead ruled the ambiguity: base v2's
end-to-end BEFORE column is `pass2-signals-r2`'s registered 4/5 · 2 signals and is not re-bought,
and base v3 takes no bar ([[two_values_for_one_input_get_quoted_kindly]] closed by a ruling)."""
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

AMENDMENT_325_1_PRICE = (
    "Price consequences are derived in `lora-c-run` at the stack's worst measured rates; the cap"
    " stays $4.00 until that derivation reports — raising a cap is a separate operator word."
)
"""The sentence of 3.25 (1) that makes the cap conditional on this contract's own derivation. Kept
apart from `AMENDMENT_325_1` because the derivation quotes it and the ceiling clause does not."""

AMENDMENT_326_1 = (
    "**`training.max_seq_len` is 3 072** — «поднимай max_seq_len до 3072», the rung 3.25 (1)"
    " named in advance. `config/qlora.yaml` is at revision 3; line B's pins stay on revision 1"
    " and are never re-taken."
)
AMENDMENT_326_2 = (
    "**The 2 800 STOP threshold reads the TRUE count** — the tokenizer's own number, with no"
    " `TEMPLATE_SLACK` added"
)
AMENDMENT_326_3 = "**The ratio model stays retired for ceilings.**"


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
            "train_file": "results/pass1_sft_v3_train.jsonl",
            "bar": "the registered three, all-or-RED",
        },
        "arm_b": {
            "adapter": "QLoRA on arm A's rows PLUS the synthetic rows",
            "prompt": pass1_v3.PASS1_TASK_V3,
            "reads": "results/lora_c_eval_pack.json::legs.v3",
            "eval_calls": calls,
            "train_rows": train_rows + synthetic_rows,
            "train_file": "results/pass1_sft_v3_arm_b.jsonl",
            "produced_by": "scripts/build_lora_c_data.py --arm-b-out (lora-c-armb D1)",
            "record": "results/lora_c_arm_b.json",
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


BOOT_SECONDS = 500
"""`docs/PROMPT-lora-c-run.md` D2's boot gate — «ssh ≤500 s from create, else kill+recreate»."""

LOAD_SECONDS = 300
"""«load (worst measured 300 s)», the contract's own term."""

SMOKE_STEPS = 6
SMOKE_KILL_CLOCK_MULTIPLIER = 1.5
"""«Smoke bound for its kill-clock only: 121 s/step × 1.5». A CEILING for the smoke's own six
steps, and explicitly not a rate: the contract forbids projecting one at 3 072."""

USD_PER_HOUR_WORST = 0.80
"""lora-b's rung 1, registered: «live A6000-class price > $0.80/h at create → STOP, no endpoint»
(results/prereg_lora_b.json::kill_clock). The worst price this line may meet and still create."""

SIBLING_SECONDS_PER_CALL = 2.694083
"""What pass1-window r2's own pod REALISED per pass-1 call, against 6.14 charged. A reading of this
stack on this decode, and 0.439 of the charge."""

SIBLING_SECONDS_PER_THREAD = 23.760
"""What pass2-signals r2's pod REALISED per pass-2 thread, against 97 charged — 0.245 of it, with
r2's own caveat: the pod-class spread was measured at 1.008 on n = 1, the shortest of five replies."""

USD_PER_HOUR_LAST_FIVE_PODS = 0.74
"""What the last five pods of this stack actually billed, on a 4090 24 GB in EU-RO-1. A second
reading of the same quantity, never a substitute for the worst one under a cap."""

USD_PER_HOUR_THE_RULED_CARD = 0.72
"""RTX PRO 4500 32 GB in EU-RO-1 — the card ruling (о) names, at the price the stock probe listed.

A LISTED price, not a billed one: the create response's `costPerHr` is the reading, and rung 0
refuses a create whose price this record holds no column for. Registered because every projection
rung after the create divides by a price, and a price nobody registered is a projection nobody can
check ([[a_published_ratio_is_not_the_gates]])."""

MARKER_CENSUS_ROWS = 20
MARKER_CENSUS_VARIANTS = 2
"""The report-only marker census of ruling (о): ~20 E requests, each bought TWICE from arm B's
adapter — as-is, and with the synthetic header block substituted in. It separates «synthetic did not
help» from «the adapter learned the marker», and it is never a bar."""


def pre_pod_arithmetic(
    calls: int, steps: dict, pass2_threads: int, pass2_legs: int, stock: dict
) -> dict:
    """lora-c-run's price derivation, at the CHARGED rates, before any pod exists.

    SPEC amendment 3.25 (1) and `docs/STATUS.md` п. 1 (л) both end the same way — «the cap stays
    $4.00 until that derivation reports». This is that derivation.

    It registers no s/step, because none exists at 3 072 and the contract buys it with the smoke.
    What it registers instead is the inequality solved BACKWARDS: the largest s/step the cap can
    pay for once every other term is charged, in the unit the smoke will measure
    ([[a_published_ratio_is_not_the_gates]]). Beside it stand the only two readings this repo has,
    with the sequence length they were taken at — a reachability statement about the acceptance
    criterion, never a projected rate ([[the_expectation_no_reading_reaches]]).
    """
    total_steps = steps["arm_a"] + steps["arm_b"]
    smoke = SMOKE_STEPS * SECONDS_PER_STEP_COMPLIANT_SLOW * SMOKE_KILL_CLOCK_MULTIPLIER
    fixed = {
        "boot": BOOT_SECONDS,
        "load": LOAD_SECONDS,
        "base_legs": round(2 * calls * PASS_1_SECONDS_PER_CALL, 2),
        "pass_1_evals_of_the_two_adapters": round(2 * calls * PASS_1_SECONDS_PER_CALL, 2),
        "pass_2": round(pass2_legs * pass2_threads * PASS_2_SECONDS_PER_THREAD, 2),
        "training_smoke": round(smoke, 2),
    }
    fixed["total"] = round(sum(fixed.values()), 2)
    at = {}
    for price in (USD_PER_HOUR_WORST, USD_PER_HOUR_THE_RULED_CARD, USD_PER_HOUR_LAST_FIVE_PODS):
        budget = CAP_USD / price * 3600
        left = budget - fixed["total"]
        at[f"{price:.2f}"] = {
            "budget_seconds": round(budget, 1),
            "fixed_usd": round(fixed["total"] / 3600 * price, 4),
            "left_for_training_seconds": round(left, 1),
            "break_even_seconds_per_step": round(left / total_steps, 2),
        }
    marker_seconds = MARKER_CENSUS_ROWS * MARKER_CENSUS_VARIANTS * PASS_1_SECONDS_PER_CALL
    marker_break_even = {
        price: round(
            (cell["left_for_training_seconds"] - marker_seconds) / total_steps,
            2,
        )
        for price, cell in at.items()
    }
    readings = {
        "registered_by_lora_b": SECONDS_PER_STEP_REGISTERED,
        "measured_on_lora_b_arm_a": SECONDS_PER_STEP_MEASURED,
    }
    covered = {
        price: sorted(
            name for name, value in readings.items() if value <= cell["break_even_seconds_per_step"]
        )
        for price, cell in at.items()
    }
    sibling_fixed = round(
        BOOT_SECONDS
        + LOAD_SECONDS
        + 4 * calls * SIBLING_SECONDS_PER_CALL
        + pass2_legs * pass2_threads * SIBLING_SECONDS_PER_THREAD
        + smoke,
        1,
    )
    return {
        "state": (
            "DERIVED and REPORTED, not sealed — no pod exists, so the record is still the DRAFT"
            " `frozen_when_the_pod_exists` describes"
        ),
        "authority": {
            "record": "docs/SPEC.md, the `amendment-3.25` marked block, clause (1)",
            "clause": quoted_spec(AMENDMENT_325_1_PRICE),
        },
        "rates_used": {
            "pass_1_seconds_per_call": PASS_1_SECONDS_PER_CALL,
            "pass_2_seconds_per_thread": PASS_2_SECONDS_PER_THREAD,
            "training_seconds_per_step": (
                "NONE. No reading exists at 3 072 and the contract forbids projecting one from"
                " lora-b's ≤1 222-token readings — the smoke buys it"
            ),
        },
        "price_usd_per_hour": {
            "worst": USD_PER_HOUR_WORST,
            "worst_source": "results/prereg_lora_b.json::kill_clock rung 1 — the create refuses above it",
            "the_ruled_card": USD_PER_HOUR_THE_RULED_CARD,
            "the_ruled_card_source": (
                "ruling (о) of 24.08 names RTX PRO 4500 32 GB at $0.72/h in EU-RO-1; the stock probe"
                " of 2026-08-24T08:24Z listed that price and read the card «High». A LISTING is not"
                " a create and the create response's costPerHr is the reading rung 0 grades"
            ),
            "last_five_pods": USD_PER_HOUR_LAST_FIVE_PODS,
            "rule": (
                "a create whose costPerHr matches no column here is a STOP: every projection rung"
                " divides by a price, and one nobody registered cannot be checked"
            ),
        },
        "hard_stop_seconds": round(CAP_USD / USD_PER_HOUR_WORST * 3600, 1),
        "hard_stop_rule": "cap / worst rate, stamped on `--terminate-after` at create",
        "fixed_seconds": fixed,
        "steps": {**steps, "total": total_steps},
        "at_each_price": at,
        "readings_this_repo_holds": readings,
        "readings_under_the_break_even": covered,
        "readings_under_the_break_even_rule": (
            "which of the s/step readings this repo holds sit at or below the break-even, per"
            " price. A MACHINE-READABLE form of the verdict below, so a test can check the finding"
            " instead of parsing the sentence ([[gate_verdicts_need_an_artifact]]). Neither list"
            " licenses a rate: both readings were taken at ≤1 222 tokens and this line runs at"
            " 1 445–2 975"
        ),
        "verdict": (
            f"at the scope ruling (н) fixes — four eval legs and {pass2_legs} pass-2 legs — the"
            f" fixed part is {fixed['total']:.2f} s ="
            f" ${at[f'{USD_PER_HOUR_WORST:.2f}']['fixed_usd']:.4f} at the worst price a create is"
            " allowed at, and what is left pays for at most"
            f" {at[f'{USD_PER_HOUR_WORST:.2f}']['break_even_seconds_per_step']:.2f} s/step over the"
            f" {total_steps} optimizer steps"
            f" ({at[f'{USD_PER_HOUR_LAST_FIVE_PODS:.2f}']['break_even_seconds_per_step']:.2f} at the"
            " price the last five pods billed). The only two s/step READINGS this repo holds are"
            f" {SECONDS_PER_STEP_REGISTERED} and {SECONDS_PER_STEP_MEASURED}. Under the break-even"
            f" at ${USD_PER_HOUR_WORST:.2f}/h: {covered[f'{USD_PER_HOUR_WORST:.2f}'] or 'NEITHER'};"
            f" at ${USD_PER_HOUR_LAST_FIVE_PODS:.2f}/h:"
            f" {covered[f'{USD_PER_HOUR_LAST_FIVE_PODS:.2f}'] or 'NEITHER'}. Both were taken on"
            " sequences of at most 1 222 tokens against this line's 1 445–2 975, so neither is this"
            " line's rate and neither is registered as one — the smoke buys it. What amendment"
            " 3.25 (1) made the cap conditional on is this table; the word on the cap is the"
            " operator's, on these numbers, and it is due BEFORE a create and never after a reading"
        ),
        "what_changed_since_lora_c_run_reported_this": (
            "nothing but the pass-2 leg count, which ruling (н) fixed at"
            f" {pass2_legs}. lora-c-run charged four and reported the plan SHORT: 11 019.88 s fixed"
            " and a break-even of 48.47–58.61 s/step against readings of 61.047 and 68.442. The"
            f" {(4 - pass2_legs) * pass2_threads * PASS_2_SECONDS_PER_THREAD} s that came off is the"
            " whole of the difference — no rate moved, no term was re-estimated, and the row count"
            " of both arms was registered before either contract"
        ),
        "what_the_projection_rung_would_see": {
            "why_this_column_exists": (
                "the rung fires at MEASURED rates, and both charged rates have a direct sibling"
                f" measurement: {SIBLING_SECONDS_PER_CALL} s/call (pass1-window r2's own pod) and"
                f" {SIBLING_SECONDS_PER_THREAD} s/thread (pass2-signals r2's). They are"
                f" {SIBLING_SECONDS_PER_CALL / PASS_1_SECONDS_PER_CALL:.3f} and"
                f" {SIBLING_SECONDS_PER_THREAD / PASS_2_SECONDS_PER_THREAD:.3f} of the charge. This"
                " column is what"
                " the session's own instruments would compute after the base legs and the smoke —"
                " it is a SCENARIO and no part of it is registered as a rate"
            ),
            "fixed_seconds_at_sibling_rates": sibling_fixed,
            "break_even_seconds_per_step": {
                f"{price:.2f}": round((CAP_USD / price * 3600 - sibling_fixed) / total_steps, 2)
                for price in (
                    USD_PER_HOUR_WORST,
                    USD_PER_HOUR_THE_RULED_CARD,
                    USD_PER_HOUR_LAST_FIVE_PODS,
                )
            },
            "one_accounting_for_the_smoke": (
                f"the smoke's {SMOKE_STEPS} steps are charged at"
                f" {SECONDS_PER_STEP_COMPLIANT_SLOW} × {SMOKE_KILL_CLOCK_MULTIPLIER} in BOTH"
                f" columns and divided out of NEITHER: the divisor is {total_steps} in both, the"
                " two arms' optimizer steps. lora-c-run's version charged the smoke in the table"
                f" above and divided by {total_steps} + {SMOKE_STEPS} here, which priced one"
                " quantity two ways ([[two_values_for_one_input_get_quoted_kindly]])"
            ),
            "reading": (
                "under the sibling-measured rates the break-even rises above both lora-b readings,"
                " so the session is not arithmetically hopeless — it is UNDECIDED until the smoke"
                " measures s/step at 3 072. That is the decision the operator is owed, and it is"
                " not the executor's to take under a cap the derivation just reported short"
            ),
        },
        "the_pass_2_leg_count_was_ruled": {
            "was": (
                "lora-c-run charged FOUR legs and said so: its fixed part summed 4 × 11 × 97 while"
                " its order of operations named pass 2 only under «eval A» and «eval B likewise»,"
                " which is two. Four was the conservative charge under a cap and it was named"
                " rather than chosen quietly (Dv788)"
            ),
            "ruling": quoted(RULING_N_PASS_2),
            "now": pass2_legs,
            "saved_seconds": round((4 - pass2_legs) * pass2_threads * PASS_2_SECONDS_PER_THREAD, 2),
            "saved_usd_at_the_worst_price": round(
                (4 - pass2_legs)
                * pass2_threads
                * PASS_2_SECONDS_PER_THREAD
                / 3600
                * USD_PER_HOUR_WORST,
                4,
            ),
            "what_bars_report_only_still_says": (
                "`bars.report_only.pass_2_tables` says «per leg» and this contract may not touch"
                " `bars`. The two are reconciled HERE and nowhere else: the tables are per leg for"
                f" the legs that RUN, and ruling (н) says those are the {pass2_legs} arms. Base"
                " v2's end-to-end BEFORE column is pass2-signals-r2's registered 4 of 5 on two"
                " signals, already bought; base v3 takes no bar and therefore needs no pass 2"
            ),
        },
        "the_marker_census_is_not_inside_the_fixed_part": {
            "what": (
                f"ruling (о) buys a report-only marker census: {MARKER_CENSUS_ROWS} E requests, each"
                f" answered {MARKER_CENSUS_VARIANTS}× by arm B's adapter — as-is and with the"
                " synthetic header block substituted in — so «synthetic did not help» and «the"
                " adapter learned the marker» stop being the same reading"
            ),
            "the_contract_says_inside_the_fixed_part": (
                "`docs/PROMPT-lora-c-run-r2.md` amendment 4 prices it «~$0.05, inside the fixed"
                f" part», and amendment 1 pins that fixed part at {fixed['total']:.2f} s. The two"
                " cannot both be literal: the sum above decomposes exactly into boot + load + two"
                " base legs + pass 2 + smoke + two adapter evals, with no term for"
                f" {MARKER_CENSUS_ROWS * MARKER_CENSUS_VARIANTS} calls. So the census is charged"
                " HERE, beside the registered total rather than silently inside it — a new leg"
                " joining the denominator moves the knife-edge even when the rule does not move"
                " ([[a_new_leg_joins_the_gates_denominator]])"
            ),
            "seconds": round(marker_seconds, 2),
            "arithmetic": (
                f"{MARKER_CENSUS_ROWS} × {MARKER_CENSUS_VARIANTS} ="
                f" {MARKER_CENSUS_ROWS * MARKER_CENSUS_VARIANTS} calls ×"
                f" {PASS_1_SECONDS_PER_CALL} s/call charged"
            ),
            "usd_at_each_price": {
                price: round(marker_seconds / 3600 * float(price), 4) for price in at
            },
            "break_even_seconds_per_step_with_it_charged": marker_break_even,
            "what_it_costs_the_decision": (
                "nothing at the card ruling (о) names — at"
                f" ${USD_PER_HOUR_THE_RULED_CARD:.2f}/h the break-even falls"
                f" {at[f'{USD_PER_HOUR_THE_RULED_CARD:.2f}']['break_even_seconds_per_step']:.2f} →"
                f" {marker_break_even[f'{USD_PER_HOUR_THE_RULED_CARD:.2f}']:.2f} s/step and both"
                " readings this repo holds stay under it. At the WORST price a create is allowed at"
                f" it falls {at[f'{USD_PER_HOUR_WORST:.2f}']['break_even_seconds_per_step']:.2f} →"
                f" {marker_break_even[f'{USD_PER_HOUR_WORST:.2f}']:.2f}, which sits"
                f" {marker_break_even[f'{USD_PER_HOUR_WORST:.2f}'] - SECONDS_PER_STEP_REGISTERED:.2f}"
                f" s/step above lora-b's registered {SECONDS_PER_STEP_REGISTERED} — a real margin"
                " and a thin one. Carried as a BOUND, not as a blocker: the census is the LAST thing"
                " the session buys, after every bar is already scored, so a projection rung that"
                " cannot afford it drops it and loses a report-only table"
            ),
            "when": (
                "after arm B's eval leg, which is after both arms' bars are answered. It is"
                " report-only and it is never a bar"
            ),
            "ruling": quoted(RULING_O_MARKER),
        },
        "stock_probe": {
            "record": "results/lora_c_stock_probe.json",
            "read_at": stock["read_at"],
            "region": stock["region"],
            "region_source": "the network volume's datacenter — results/d7_reread_srv2b.json",
            "read_only": stock["creates_nothing"],
            "caveat": stock["caveat"],
            "reading": stock["reading"],
            "the_card_the_ruling_names": stock["wanted_in_the_volumes_region"],
            "in_the_volumes_region": stock["with_stock_in_the_volumes_region"],
            "nothing_is_chosen": (
                "ruling (к) says «один A6000» and the probe reads it as `none` in the volume's own"
                " datacenter, as it was when knowledge/hot.md recorded it — this reading DATES that"
                " sentence rather than repeating it. The alternatives above are listed with their"
                " prices and NONE is picked: the card is part of what the operator is being asked,"
                " beside the cap, and a create is the only free test of stock"
                " ([[a_stock_window_needs_the_create_not_a_poll]]). A create is also this record's"
                " freeze, so the two cannot be separated"
            ),
            "what_a_different_card_would_move": (
                f"every second in `fixed_seconds` was measured on a 4090 or charged from one, and"
                f" the break-even above is priced at ${USD_PER_HOUR_WORST:.2f}/h and"
                f" ${USD_PER_HOUR_LAST_FIVE_PODS:.2f}/h. A card at another price re-prices the"
                " budget but not the seconds; a card of another CLASS re-prices the seconds too,"
                " and this record holds no reading of any of them"
            ),
        },
    }


def money(
    eval_pack: dict,
    data_record: dict,
    train_rows: int,
    synthetic_rows: int,
    counted: dict,
    pass2_threads: int,
    stock: dict,
) -> dict:
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
    arithmetic = pre_pod_arithmetic(calls, steps, pass2_threads, PASS_2_LEGS, stock)
    return {
        "state": (
            "RE-DERIVED by lora-c-armb at the charged rates, for the scope ruling (н) fixes, and"
            " REPORTED to the operator — see `pre_pod_arithmetic`. lora-c-run derived it first at"
            " four pass-2 legs and reported the plan short; the ruling took two of those legs off"
            " and nothing else moved. Still not SEALED: sealing is the first `pod create` and no"
            " pod exists"
        ),
        "pre_pod_arithmetic": arithmetic,
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
                    f" {counted['pod_count']['min']}–{counted['pod_count']['max']} tokens by the"
                    " TOKENIZER'S OWN COUNT (results/lora_c_tokens.json) — not the ratio model's"
                    f" {data_record['tokens']['by_ratio']['min_observed']['min']}–"
                    f"{data_record['tokens']['by_ratio']['registered_bound_max']['max']}, which"
                    " under-predicts the widest row by 228 tokens. config/qlora.yaml's own comment"
                    " says raising"
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


LIVENESS_SECONDS = 600
"""«Liveness: deadline 600 s from the LAST log line or event, at every stage» — the contract's own
term, and the one rung that applies while nothing is happening."""

BOOT_GATE_RETRIES = 1
"""«ssh ≤500 s from create, else kill+recreate (once; third pod = STOP)»."""


def rungs(fixed: dict, at: dict, steps: dict, pass2_threads: int) -> list[dict]:
    """The session's GO/KILL conditions, as CONDITIONS with an instrument that evaluates them.

    `docs/PROMPT-lora-c-run.md` D2 registers rungs and not numbers, and a rung with no producer is
    not a rung ([[a_registered_bar_may_have_no_producer]]). `scripts/gate_lora_c.py` is that
    producer; the runbook copies its commands from the `flag` field here rather than restating them.

    **The shape is lora-b's on purpose** — a list of `{rung, rule, …}` — because `gate_lora_c.py`
    is a SIBLING of `scripts/gate_lora_b.py` and CALLS its clock, its backstop check and its
    dead-man unchanged. A second shape would have meant a second copy of all three.

    Every rung carries `threshold` as a NUMBER beside its prose rule, and every rule is worded so
    its FIRST number is that threshold. `gate_lora_b.first_number` reads thresholds out of prose,
    and a rule with four words in front of its figure once turned a 600 s deadline into 5 s
    ([[a_threshold_that_lives_in_prose]]); `tests/test_lora_c_run_r2.py` asserts the two agree for
    every rung here, so the parse can never quietly disagree with the number.

    Rung 0 exists because ruling (о) names a card this repo has NEVER billed. Every second in
    `fixed_seconds` was measured on a 4090 or charged from one, and every projection rung divides by
    a price — so the create response's own `costPerHr` is graded against the price columns this
    record holds ([[a_rate_is_a_property_of_the_pod]]).

    Rung 3 is the one lora-b did not have. Its first spend decision fired at the arm-A milestone;
    here the first projection rung is after the SMOKE — boot + load + two base legs + the smoke.
    On a card whose s/call this repo has never read, a slow pod
    would be discovered two eval legs late, so the base legs are graded on their OWN realised rate
    while they are being paid for ([[two_instruments_two_inputs]]).
    """
    total_steps = steps["arm_a"] + steps["arm_b"]
    smoke_ceiling = SECONDS_PER_STEP_COMPLIANT_SLOW * SMOKE_KILL_CLOCK_MULTIPLIER
    before_the_first_projection = (
        fixed["boot"] + fixed["load"] + fixed["base_legs"] + fixed["training_smoke"]
    )
    return [
        {
            "rung": 0,
            "name": "the price and the card at create",
            "before": "anything is trained",
            "rule": (
                f"${USD_PER_HOUR_WORST:.2f}/h is the ceiling a create is allowed at, and costPerHr"
                f" must equal one of the registered price columns {sorted(at)} — a price this"
                " record holds no column for is a STOP"
            ),
            "threshold": USD_PER_HOUR_WORST,
            "unit": "usd_per_hour",
            "read": "costPerHr and gpu displayName, out of the create response",
            "registered_prices": sorted(at),
            "on_failure": "delete the pod, prove it by listing, STOP. Nothing is trained.",
            "flag": "--open --pod-id <id> --created-at <ISO> --usd-per-hour <costPerHr> --card <name> --terminate-after <stamp>",
            "why": (
                "ruling (о) names RTX PRO 4500 32 GB — a card this stack has never billed. Every"
                " projection rung divides by the price, so an unregistered one makes every rung"
                " after it uncheckable"
            ),
        },
        {
            "rung": 1,
            "name": "the boot gate",
            "before": "the model is loaded",
            "rule": (
                f"{BOOT_SECONDS} s from create to the first ssh that answers, else kill and"
                f" recreate — {BOOT_GATE_RETRIES} re-creation is authorised and a third pod is a STOP"
            ),
            "threshold": BOOT_SECONDS,
            "unit": "seconds",
            "flag": "--gate0 [--ssh-ok]",
        },
        {
            "rung": 2,
            "name": "liveness",
            "before": "every stage, while it runs",
            "rule": (
                f"{LIVENESS_SECONDS} s since the LAST log line or event is a KILL, at every stage"
            ),
            "threshold": LIVENESS_SECONDS,
            "unit": "seconds",
            "flag": "--liveness --last-event <ISO>",
            "why_it_is_not_a_poll_interval": (
                "the deadline is measured from the last thing that HAPPENED, not from the last time"
                " anyone looked. A run quiet because it died and a run quiet because nothing prints"
                " look identical to a poll ([[no_rung_watches_an_idle_pod]])"
            ),
        },
        {
            "rung": 3,
            "name": "the realised rate of the base legs",
            "before": "the second base leg, and the smoke",
            "rule": (
                f"${CAP_USD:.2f} all-in must still cover the plan when the base leg's OWN realised"
                " s/call is extended over every remaining charged call and the 150 optimizer steps"
                f" are charged at {SECONDS_PER_STEP_REGISTERED} s/step"
            ),
            "threshold": CAP_USD,
            "unit": "usd",
            "steps_charged_at_seconds_per_step": SECONDS_PER_STEP_REGISTERED,
            "why_that_number_and_not_the_smoke_ceiling": (
                f"{SECONDS_PER_STEP_REGISTERED} is the CHEAPEST s/step any pod of this stack has"
                " ever been registered at, and this rung is not projecting the run's rate — the"
                " contract forbids that and the smoke buys it. It asks a BOUND: after the"
                " generation this card is realising, is there still room for the cheapest training"
                " anyone has measured? If not, no plausible s/step fits and the session is already"
                " over ([[bound_instead_of_recompute]]). Charging the smoke's"
                f" {smoke_ceiling:.1f} s/step kill-clock instead would refuse EVERY session at the"
                f" first base leg: 150 × {smoke_ceiling:.1f} s alone is more than the cap buys"
            ),
            "read": "rows answered ÷ elapsed, off the growing out-file DURING the leg",
            "on_failure": (
                "KILL before the next leg — the finding is the card, and a card that cannot pay for"
                " the plan is an answer"
            ),
            "flag": "--rate --leg <name> --replies <file> --started-at <ISO>",
            "why_this_rung_exists": (
                f"the charged {PASS_1_SECONDS_PER_CALL} s/call was measured on a 4090 and ruling (о)"
                " names a card this repo has never run. The first projection rung fires after the"
                f" smoke — about {before_the_first_projection:.0f} charged seconds in — and a card"
                " 1.65× slower on identical work is inside this stack's own measured spread"
            ),
        },
        {
            "rung": 4,
            "name": "the smoke buys s/step and tests the VRAM",
            "before": "arm A",
            "rule": (
                f"{smoke_ceiling:.1f} s/step is the ceiling for the smoke's {SMOKE_STEPS} optimizer"
                " steps at 3 072, and an OOM there is a KILL and a STOP"
            ),
            "threshold": smoke_ceiling,
            "unit": "seconds_per_step",
            "steps": SMOKE_STEPS,
            "on_failure": (
                "an OOM at 3 072 is a KILL and a STOP, not a retry: `micro_batch_size` is frozen law"
                " in config/qlora.yaml and is NOT edited on a pod. Ruling (о) makes the smoke the"
                " VRAM test, and 32 GB against the 48 GB every prior reading was taken on is why"
            ),
            "flag": "--smoke --loss <file>",
            "what_it_buys": (
                "the ONLY s/step this line may use. No reading at 3 072 exists and neither lora-b"
                " reading is one — both were taken at ≤1 222 tokens against this line's 1 445–2 975"
            ),
        },
        {
            "rung": 5,
            "name": "the projection",
            "before": "after the smoke and after EVERY leg",
            "rule": (
                f"${CAP_USD:.2f} all-in: cumulative spend on the pod clock plus the remainder"
                " projected at the rates this session MEASURED must not pass the cap"
            ),
            "threshold": CAP_USD,
            "unit": "usd",
            "on_failure": (
                "KILL, pull every artifact, prove the teardown by listing, STOP to the team lead"
                " with the ledger. A KILL here is compliance, not failure"
            ),
            "flag": "--projection --after <milestone> --reading <the guard's USD>",
            "remaining_work_after_each_milestone": {
                "smoke": (
                    f"{total_steps} steps + 2 adapter eval legs + 2 × {pass2_threads} pass-2 threads"
                ),
                "arm_a": f"{steps['arm_b']} steps + 2 eval legs + 2 × {pass2_threads} threads",
                "eval_a": f"{steps['arm_b']} steps + 1 eval leg + {pass2_threads} threads",
                "arm_b": f"1 eval leg + {pass2_threads} threads + the marker census",
                "eval_b": "the marker census only",
            },
        },
        {
            "rung": 6,
            "name": "the hard stop",
            "before": "it is stamped at create and enforced by the platform",
            "rule": (
                f"{round(CAP_USD / USD_PER_HOUR_WORST * 3600, 1)} s from create, LESS whatever a"
                " closed pod of this attempt already billed, stamped on `--terminate-after`"
            ),
            "threshold": round(CAP_USD / USD_PER_HOUR_WORST * 3600, 1),
            "unit": "seconds",
            "derivation": "cap ÷ the worst price a create is allowed at — the shortest window, deliberately",
            "why_not_the_ruled_cards_price": (
                f"at ${USD_PER_HOUR_THE_RULED_CARD:.2f}/h the cap would pay for"
                f" {round(CAP_USD / USD_PER_HOUR_THE_RULED_CARD * 3600, 1)} s. The stop is stamped"
                " at the WORST price because a backstop that assumes the good case is not one, and"
                " the runbook already accepts rounding the window down"
            ),
            "flag": "--open … --terminate-after '<the stamp pod create was given>'",
        },
        {
            "rung": 7,
            "name": "one billing resource",
            "before": "every create",
            "rule": (
                "1 billing resource at a time: never a second pod while one exists, never a"
                " serverless endpoint, and the network volume is beside the run and not inside it"
            ),
            "threshold": 1,
            "unit": "resources",
            "read": "`runpodctl pod list -a`, `serverless list`, `network-volume list`",
            "flag": "--pre-create-check",
            "on_failure": "STOP before the create — never a refusal after the second meter starts",
        },
        {
            "rung": 8,
            "name": "the attempt",
            "before": "it is spent",
            "rule": (
                "1 attempt, SPENT at the first reply generated against eval set E by an ADAPTER leg."
                " The base legs are the BEFORE column and spend nothing; the smoke trains and"
                " generates no eval reply"
            ),
            "threshold": 1,
            "unit": "attempts",
            "consequence": "no retry, no second draw, no tuning after any eval output is seen",
        },
    ]


def transport() -> dict:
    """The four things that RUN on the pod, with the shas the pod's own handshakes check.

    A registered leg whose runner cannot serve its pack is a leg with no producer, and this line had
    four of them until `lora-c-run r2` drove the shipped chain against the frozen packs at $0: the
    pass-1 handshake refused the v3 family, the pass-1 render sent a v3 item to the READER's
    renderer, the leg runner had no `--adapter`, and the pass-2 pack carried neither the instrument
    block nor the `carried` block nor the `serving` block its runner reads. Every one of them would
    have fired on a billed pod with the model loaded
    ([[a_frozen_record_is_an_input_to_shipped_code]]).
    """
    files = {
        "scripts/train_qlora_v3.py": "the two guards re-bound; everything else CALLED",
        "scripts/pass1_v3_pod_runner.py": "the v3 family served and --adapter carried",
        "scripts/pass2_r2_pod_runner.py": "pass2-signals-r2's own runner, unchanged",
        "scripts/gate_lora_c.py": "the nine rungs, graded on the Mac",
    }
    return {
        "rule": (
            "each was DRIVEN against this line's frozen packs with a fake client before any pod"
            " existed — the handshake, and every per-item rendering sha"
        ),
        "files": {
            name: {
                "sha256": data.sha_text((REPO_ROOT / name).read_text(encoding="utf-8")),
                "what": why,
            }
            for name, why in files.items()
        },
        "what_the_drive_proved": {
            "pass_1": "198 requests per leg re-rendered and matched against the pack's own shas",
            "pass_2": "11 threads, the handshake and the carried-row guard",
            "marker_census": "40 requests, 20 pairs, differing in the header alone",
        },
    }


def the_marker_fix(arm_b_record: dict) -> dict:
    """Ruling (о)'s step 0.75, registered as the two counts it turns on — not as a sentence.

    Dv795 found five header lines carried by 160 of the synthetic rows and by 0 of the 506 real
    ones, and the loudest was `prompts.NO_POST_TEXT` — a sentence about an IMAGE post, false on a
    synthetic row and true on the real image posts the eval genuinely contains. The team lead's
    ruling forbids it there. `build_lora_c_data.SYNTHETIC_NO_POST` replaces it.

    What the fix does NOT do is remove the marker, and the record says so in the same breath it
    reports the fix: a synthetic row has no post, every honest topic line saying so is a line no
    real row of this pool renders, and all 32 `молочный_бренд` targets in this line sit behind it.
    That confound is ACCEPTED and measured by the report-only marker census
    ([[a_default_is_a_marker_when_nothing_takes_it]]).
    """
    tell = arm_b_record["isolation"]["5_the_header_tell"]
    lines = {cell["line"]: cell for cell in tell["header_lines_of_the_160"]}
    false_line = lines.get(prompts.NO_POST_TEXT)
    registered = lines.get(data.SYNTHETIC_NO_POST)
    return {
        "ruling": quoted(RULING_O_MARKER),
        "constant": {
            "name": "scripts/build_lora_c_data.py::SYNTHETIC_NO_POST",
            "value": data.SYNTHETIC_NO_POST,
        },
        "the_false_string_it_replaces": {
            "name": "src/market_pulse/prompts.py::NO_POST_TEXT",
            "value": prompts.NO_POST_TEXT,
            "in_the_160": false_line["synthetic_rows_carrying_it"] if false_line else 0,
            "in_the_506": false_line["real_rows_carrying_it"] if false_line else 0,
            "was_before_the_fix": {"in_the_160": 160, "in_the_506": 0},
        },
        "the_registered_string": {
            "in_the_160": registered["synthetic_rows_carrying_it"] if registered else 0,
            "in_the_506": registered["real_rows_carrying_it"] if registered else 0,
        },
        "why_prompts_py_is_not_edited": (
            "it is pinned by every sealed record of this stack and it is on the contract's DO-NOT"
            " list. The constant is passed AS the topic, so `topic.strip()` is truthy and"
            " `pass1_v3.pass1_messages_gm4_v3` takes its ordinary branch — no renderer moved"
        ),
        "the_prefix_did_not_move": (
            "the 506 real rows re-render BYTE-IDENTICAL against the shipped file; the producer"
            " refuses to write otherwise. Only the 160 synthetic prompts changed, and with them"
            " arm B's sha above"
        ),
        "the_marker_that_remains": {
            "tells": tell["tells"],
            "synthetic_rows_marked_by_at_least_one_tell": tell[
                "synthetic_rows_marked_by_at_least_one_tell"
            ],
            "state": "ACCEPTED and NAMED by ruling (о); measured by the report-only marker census",
            "why_it_cannot_be_removed": (
                "a synthetic row has no post and no resolved entity. Any topic line that says so"
                " truthfully is a line none of the 506 renders, and any line that does NOT say so"
                " would be a fabricated provenance inside training data. The thread tag carries the"
                " error class by the same argument. The confound is priced, not argued away"
            ),
        },
    }


def reachability(data_record: dict, counted: dict) -> dict:
    """Three things this line cannot reach as registered, each with its arithmetic and its remedies."""
    tokens = data_record["tokens"]
    return {
        "the_smallest_class_has_no_fifth_neighbour": data_record["unreachable"],
        "max_seq_len_RESOLVED_by_the_operators_ruling": {
            "state": (
                "amendment 3.25 (1) raised the ceiling 1 408 -> 2 816 and ordered a reality check"
                " before `lora-c-run` buys anything. The check RAN, at $0, through the model's own"
                " tokenizer at the pinned revision, and it came back ABOVE the amendment's own"
                f" 2 800 stop — so the line went back to the operator, who ruled"
                f" {counted['ruling']['ceiling_after']} on {counted['ruling']['date']}"
                " («поднимай max_seq_len до 3072»), the rung 3.25 (1) had named in advance."
                " config/qlora.yaml is at revision 3 and NO row is over it. **This block is kept"
                " as the history of a threshold that fired and was answered**, not as an open"
                " unreachability — the three beside it are still open"
            ),
            "resolved": True,
            "headroom": counted["headroom_under_the_ceiling"],
            "where_the_authority_lives": counted["ruling"]["recorded_in_the_spec_by"],
            "counted": counted,
            "what_the_model_said_and_the_count_says": (
                f"the three-ratio model puts the widest row at"
                f" {tokens['by_ratio']['registered_bound_max']['max']} tokens and reports"
                f" {tokens['by_ratio']['registered_bound_max']['over_max_seq_len']} of"
                f" {tokens['by_ratio']['registered_bound_max']['of']} over {tokens['max_seq_len']}."
                f" The TOKENIZER counts {counted['pod_count']['max']}"
                f" ({counted['pod_count_plus_template_slack']['max']} with TEMPLATE_SLACK):"
                f" {counted['rows_over_the_stop_threshold']['by_the_true_count']} rows over the"
                " amendment's 2 800 stop by the TRUE count, which is the reading its own words name"
                f" ({counted['rows_over_the_stop_threshold']['with_template_slack']} with slack —"
                f" {', '.join(counted['rows_over_the_stop_threshold']['the_difference'])} sits"
                " between the two readings), and"
                f" {len(counted['rows_over_max_seq_len']['by_the_true_count'])} over max_seq_len"
                " itself under BOTH readings, which is what makes the STOP invariant to the"
                " question."
                " The model under-predicts by"
                f" {counted['the_model_this_replaces']['the_model_underpredicts_by']} tokens on the"
                " widest row, which is exactly the hazard 3.25 (1) ordered the check against"
                " (Dv757: a ratio is a MODEL carried across a change of row length)"
            ),
            "not_caused_by_this_contract": (
                "measured on the rows as they stood at 97548df — before the gate-1 rewrites and"
                " before amendment 3.25 (2)'s neighbour refusal — the same tokenizer counts 2 974,"
                " with TWO rows over 2 800 under BOTH readings and two over max_seq_len. So the"
                " TRUE-count answer is 2 at both shas and this rebuild did not move it; what moved"
                " is the with-slack answer, 2 -> 3, because @matusi_ukr:22327#580336 went 2 784 ->"
                " 2 785 and crossed the slack boundary by ONE token. The finding predates the"
                " contract that reports it"
            ),
            "the_rung_the_operator_took": (
                "3.25 (1)'s own words: «the next rung is 3 072 and it is one word, not a redesign»,"
                " and that is the word given on 2026-08-23."
                f" {counted['pod_count_plus_template_slack']['max']} fits under"
                f" {counted['headroom_under_the_ceiling']['ceiling']} with"
                f" {counted['headroom_under_the_ceiling']['with_template_slack']} tokens to spare on"
                " the CONSERVATIVE reading and"
                f" {counted['headroom_under_the_ceiling']['by_the_true_count']} on the true count."
                " Both are published because one number in prose is the trap the 2 800 split was."
                " The margin is thin — under 4 % of the ceiling — and it is a COUNT rather than a"
                " projection, which is the whole difference from how 2 816 was set"
            ),
            "rows_over": counted["over"],
            "rows_over_max_seq_len": counted["rows_over_max_seq_len"],
            "the_threshold_has_two_readings": counted["rows_over_the_stop_threshold"],
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
            "state": "CLOSED-BY-SIBLING",
            "the_sibling_that_closes_it": {
                "path": "scripts/train_qlora_v3.py",
                "sha256": data.sha_text(
                    (REPO_ROOT / "scripts" / "train_qlora_v3.py").read_text(encoding="utf-8")
                ),
                "built_by": "lora-c-run D1, at $0",
                "how": (
                    "it IMPORTS train_qlora and re-binds exactly the two guards above — guard 1 by"
                    " swapping `prompts.PASS1_TASK` inside a contextmanager that puts it back"
                    " (a module-level guard cannot be told anything by a parameter), guard 2 by"
                    " reading this record's `population.train.files`. load_sft, class_weights,"
                    " content_hash, load_for_training, encode_pass1, collate, train, save and main"
                    " are the PINNED implementations, reached through the module object"
                ),
                "what_did_not_move": (
                    "scripts/train_qlora.py itself. Its sha above is the sha lora-b's sealed records"
                    " pin, and this block is kept — not deleted — because the refusals are still"
                    " true of the pinned file and a reader has to be able to see WHY a second"
                    " trainer exists ([[a_moved_guard_that_left_its_copy]])"
                ),
            },
            "why_the_block_stays": (
                "the unreachability was real and it was answered by building something, not by"
                " re-reading the record. Deleting it would leave the sibling looking like a fork"
                " someone made for convenience. Ruling (о)'s amendment 5 is this wording"
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
    arm_b_record = json.loads(ARM_B_RECORD.read_text(encoding="utf-8"))
    stock = json.loads(STOCK_PROBE.read_text(encoding="utf-8"))
    train_rows = data_record["rows"]["rendered"]
    synthetic_rows = synthetic_record["rows"]
    rows = [json.loads(one) for one in TRAIN_FILE.read_text(encoding="utf-8").splitlines() if one]

    money_block = money(
        eval_pack,
        data_record,
        train_rows,
        synthetic_rows,
        counted,
        pass2_pack["population"]["threads_with_at_least_one_filtered_row"],
        stock,
    )
    arithmetic = money_block["pre_pod_arithmetic"]
    session_rungs = rungs(
        arithmetic["fixed_seconds"],
        arithmetic["at_each_price"],
        money_block["formulas"]["steps"],
        pass2_pack["population"]["threads_with_at_least_one_filtered_row"],
    )

    return {
        "phase": "lora-c",
        "state": "DRAFT — frozen only by lora-c-run's first `pod create`",
        "kill_clock": session_rungs,
        "contract": "docs/PROMPT-lora-c-prep.md",
        "authority": {
            "record": "docs/STATUS.md «Открытые решения» п. 1",
            "ruling_v": quoted(RULING_V),
            "ruling_k": quoted(RULING_K),
            "ruling_n_rendering": quoted(RULING_N_RENDERING),
            "ruling_n_pass_2": quoted(RULING_N_PASS_2),
            "ruling_o_cap": quoted(RULING_O_CAP),
            "ruling_o_card": quoted(RULING_O_CARD),
            "ruling_o_marker": quoted(RULING_O_MARKER),
            "ruling_o_what_it_settled": (
                "(о) of 24.08, taken at the acceptance of lora-c-armb and ON the numbers that"
                " contract derived, answers the three things it STOPPED on. The cap stays $4.00"
                " because the re-derived break-even now covers both s/step readings this repo"
                " holds. The card is named — RTX PRO 4500 32 GB at $0.72/h in EU-RO-1, the volume's"
                " own datacenter, because the probe read A6000 as `none` there — with a 4090"
                " fallback pre-authorised and anything else a STOP. And the header marker Dv795"
                " found is answered in two parts: the FALSE production string comes out of the"
                " synthetic header (see `the_marker_fix`), and the marker that remains is accepted,"
                " named, and measured by a report-only census"
            ),
            "ruling_n_what_it_settled": (
                "(н) of 24.08 answers the two questions lora-c-run STOPPED on. The first makes a"
                " synthetic row a v3 QUERY under the rules a real one obeys, which is what makes"
                " arm B a file rather than an arithmetic; the second fixes the pass-2 leg count at"
                " two, which is the only term of the money block that moved"
            ),
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
                "1_max_seq_len_SUPERSEDED": (
                    "the clause above names 2 816 and the config is at 3 072. The quotation is"
                    " verbatim law and is not edited; what superseded it is the operator's ruling"
                    f" of {counted['ruling']['date']}, which 3.25 (1) pre-authorised by naming"
                    " 3 072 as the next rung. That ruling is now REGISTERED — `amendment_3_26`"
                    " below quotes the block that carries it, so a contract grepping docs/SPEC.md"
                    " for the ceiling in force reads 3 072 from the law itself and not from a"
                    " field beside it"
                ),
            },
            "amendment_3_26": {
                "record": "docs/SPEC.md, the `amendment-3.26` marked block",
                "1_max_seq_len": quoted_spec(AMENDMENT_326_1),
                "2_the_stop_threshold_reads_the_true_count": quoted_spec(AMENDMENT_326_2),
                "3_the_ratio_model_retires_for_ceilings": quoted_spec(AMENDMENT_326_3),
                "supersedes": "3.25 (1) — 2 816. The superseded clause stays quoted above verbatim",
                "why_this_block_is_quoted_and_not_asserted": (
                    "until this block existed the field above SAID the ruling was unregistered,"
                    " which was true the hour it was written and false the hour the team lead"
                    " wrote 3.26. A quotation cannot outlive its state: `quoted_spec` refuses the"
                    " build if the text leaves docs/SPEC.md"
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
                "files": [
                    {
                        "arm": "arm_a",
                        "file": "results/pass1_sft_v3_train.jsonl",
                        "rows": train_rows,
                        "sha256": sha(TRAIN_FILE),
                        "distribution": data_record["rows"]["distribution"],
                    },
                    {
                        "arm": "arm_b",
                        "file": "results/pass1_sft_v3_arm_b.jsonl",
                        "rows": arm_b_record["rows"]["total"],
                        "sha256": sha(ARM_B_FILE),
                        "distribution": arm_b_record["rows"]["distribution"],
                    },
                ],
                "rule": (
                    "arm A's file is arm B's BYTE-IDENTICAL prefix — the 506 real rows, then the"
                    " 160 rendered synthetic ones — so the ablation's one variable is the top-up"
                    " and nothing else. `scripts/build_lora_c_data.py` re-renders the 506 and"
                    " refuses to write when they do not reproduce the shipped bytes"
                ),
                "refused": data_record["rows"]["refused"],
                "record": "results/lora_c_arm_b.json",
                "rendering_ruling": quoted(RULING_N_RENDERING),
                "the_marker_fix": the_marker_fix(arm_b_record),
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
            "config_revision": 3,
            "config_revision_history": {
                "1": "1 408 — operator, 2026-08-04. Line B registered under it and its pins stay on it",
                "2": "2 816 — amendment 3.25 (1), derived from the tokens-per-character MODEL",
                "3": (
                    f"{counted['ruling']['ceiling_after']} — {counted['ruling']['by']},"
                    f" {counted['ruling']['date']}, on the strength of the tokenizer COUNT"
                ),
            },
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
                "rows_over_max_seq_len": counted["rows_over_max_seq_len"],
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
                "results/lora_c_marker_census_pack.json": sha(MARKER_CENSUS_PACK),
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
        "money": money_block,
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
        "transport": transport(),
        "frozen_when_the_pod_exists": [
            "results/prereg_lora_c.json",
            "results/lora_c_data.json",
            "results/lora_c_synthetic.json",
            "results/pass1_sft_v3_train.jsonl",
            "results/pass1_sft_v3_arm_b.jsonl",
            "results/lora_c_arm_b.json",
            "results/rationales_pass1_v1.jsonl",
            "results/synthetic_pass1_v1.jsonl",
            "results/lora_c_eval_pack.json",
            "results/lora_c_pass2_pack.json",
            "results/lora_c_marker_census_pack.json",
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
