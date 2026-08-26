#!/usr/bin/env python3
"""`results/prereg_think_zero_shot.json` — ruling (ф)'s registration. READINGS, not bars.

The deliverable of this contract is a paired table and the operator decides on it, so this record
registers no threshold and grades nothing. What it fixes before the pod exists is the four things a
table can be wrong about: WHICH instrument, WHICH rows, WHAT the BEFORE column already says, and
what one attempt means.

**Every BEFORE number is DERIVED here and the contract's transcription is checked against it.** The
contract cites 87/200, 136/200, «our» 31/49 and 38/49, bars 4/5 · 3/4 · red and 64/100. Each is
recomputed from the reply files through the shipped scorer, and a disagreement is a refusal — a
number typed into its own checker checks nothing ([[a_number_typed_into_its_own_checker]]).

    PYTHONPATH=src python3 scripts/write_think_zero_shot_prereg.py --out results
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_think_packs as packs  # noqa: E402
import gate_pass1_fewshot as pass1gate  # noqa: E402
import score_reader_probe_b as probe_b  # noqa: E402

from market_pulse import prompts, scorer  # noqa: E402

RESULTS = REPO_ROOT / "results"
STATUS = REPO_ROOT / "docs" / "STATUS.md"
CONTRACT = REPO_ROOT / "docs" / "PROMPT-think-zero-shot.md"
OUT_NAME = "prereg_think_zero_shot.json"

CAP_USD = 8.00
"""`docs/PROMPT-think-zero-shot.md` D2, transcribed. The cycle-2 remainder is $9.5079, so the cap is
what stands between this reading and the rest of the cycle."""


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def quoted(text: str, where: Path) -> str:
    """A ruling checked back into the file that carries it, before it is written into a record.

    A quotation nobody grepped is a paraphrase with quotation marks around it, and this record's
    whole authority is ruling (ф) ([[verbatim_quotes_must_be_grepped]]).
    """
    if " ".join(text.split()) not in " ".join(where.read_text(encoding="utf-8").split()):
        raise SystemExit(
            f"this quotation is not in {where.name}: {text[:80]!r}… Either the team lead has"
            " edited it or this record is paraphrasing it. Stop."
        )
    return text


def agrees(name: str, derived, transcribed) -> object:
    """The derived number, refused if the contract's transcription of it disagrees."""
    if derived != transcribed:
        raise SystemExit(
            f"{name}: the files say {derived} and docs/PROMPT-think-zero-shot.md says"
            f" {transcribed}. One of the two is wrong and this record may not choose — stop."
        )
    return derived


def dev_before() -> dict:
    """dev-200's two BEFORE columns, through the gate's own `leg_table` and nothing else."""
    record = json.loads((RESULTS / "prereg_pass1_fewshot_r2.json").read_text(encoding="utf-8"))
    pack = json.loads((RESULTS / "pass1_dev_pack.json").read_text(encoding="utf-8"))
    out = {}
    for leg, transcribed in (("base", (87, 31)), ("v2", (136, 38))):
        table = pass1gate.leg_table(record, pack, leg, RESULTS)
        agreed = agrees(f"dev-200 {leg} agreement", table["agreed"], transcribed[0])
        ours = agrees(f"dev-200 {leg} «our»", table["our_agreed"], transcribed[1])
        out[leg] = {
            "file": table["file"],
            "sha256": sha256_of(REPO_ROOT / table["file"]),
            "task": table["task"],
            "n": table["n"],
            "agreed": agreed,
            "our_n": table["our_n"],
            "our_agreed": ours,
            "parse_refusals": len(table["refused"]),
            "per_class": table["per_class"],
            "scorer": "market_pulse.scorer.reader_comment_agreement, through"
            " gate_pass1_fewshot.leg_table — the comparison the BEFORE column itself was read with",
        }
    return out


def holdout_before() -> dict:
    """The holdout's v2 column, TRACED: two reply files, 88 + 12 rows, 56 + 8 agreed.

    The contract cites «64/100 as cited by docs/reports/pass1-window-r2.md». That report does not
    carry the fraction, so it is recomputed here from the labels and the two window runs — which is
    also what says the thinking column can be over the same hundred rows
    ([[trace_the_producer_not_the_result]]).
    """
    labels = json.loads((RESULTS / "pass1_holdout_100.json").read_text(encoding="utf-8"))
    gold = {(one["thread"], int(one["msg_id"])): one["subject_type"] for one in labels["units"]}
    per_file, wanted, said, seen = {}, [], [], set()
    for pack_path, replies_path in packs.HOLDOUT_SOURCES:
        pack = json.loads((REPO_ROOT / pack_path).read_text(encoding="utf-8"))
        leg = next(one for one in pack["legs"] if one["name"] == "v2")
        by_id = {one["id"]: one for one in leg["items"]}
        rows = 0
        for line in (REPO_ROOT / replies_path).read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            item = by_id.get(row["id"])
            key = item and (item["thread"], int(item["msg_id"]))
            if key not in gold or key in seen:
                continue
            seen.add(key)
            rows += 1
            wanted.append(
                {
                    "msg_id": int(item["msg_id"]),
                    "subject_type": probe_b.collapse(gold[key]),
                    "scored_fields": ["subject_type"],
                }
            )
            try:
                answer = prompts.parse_pass1(row["reply"], msg_id=int(item["msg_id"]))
            except Exception:  # a refusal is a row the model did not answer, not a crash
                continue
            said.append(
                {
                    "msg_id": int(item["msg_id"]),
                    "subject_type": probe_b.collapse(answer["subject_type"]),
                }
            )
        per_file[replies_path] = {"rows": rows, "sha256": sha256_of(REPO_ROOT / replies_path)}
    result = scorer.reader_comment_agreement(wanted, said)
    return {
        "labels": "results/pass1_holdout_100.json",
        "labels_sha256": sha256_of(RESULTS / "pass1_holdout_100.json"),
        "answered_by": per_file,
        "n": agrees("holdout n", result["n"], 100),
        "agreed": agrees("holdout v2 agreement", result["agreed"], 64),
        "rule": (
            "the two window runs are disjoint over these rows and cover all hundred; the fraction"
            " is recomputed here because docs/reports/pass1-window-r2.md does not carry it"
        ),
    }


def pass2_before() -> dict:
    """The three bars as the shipped gate wrote them — 4/5 · 3/4 · red, read off the verdict."""
    verdict = json.loads((RESULTS / "pass2_signals_r2_verdict.json").read_text(encoding="utf-8"))
    bars = verdict["bars"]
    flag = bars["1_flagships"]["collapsed"]
    entity = bars["2_entity_cases"]["result"]
    noise = bars["3_noise"]["result"]
    return {
        "verdict": "results/pass2_signals_r2_verdict.json",
        "verdict_sha256": sha256_of(RESULTS / "pass2_signals_r2_verdict.json"),
        "replies": "results/pass2_signals_r2_v1.jsonl",
        "replies_sha256": sha256_of(RESULTS / "pass2_signals_r2_v1.jsonl"),
        "gate": "scripts/gate_pass2_signals_r2.py",
        "gate_sha256": sha256_of(REPO_ROOT / "scripts" / "gate_pass2_signals_r2.py"),
        "1_flagships": {
            "cases_answered": agrees("bar 1", flag["cases_answered"], 4),
            "cases": agrees("bar 1 denominator", flag["cases"], 5),
            "passed": flag["passed"],
        },
        "2_entity_cases": {
            "cases_answered": agrees("bar 2", entity["cases_answered"], 3),
            "cases": agrees("bar 2 denominator", entity["cases"], 4),
            "passed": entity["passed"],
            "unreachable": (
                "E1 (@matusi_ukr:22242) is outside this pack's 79 and no run has read its thread;"
                " the thinking column cannot move it either"
            ),
        },
        "3_noise": {
            "signals": noise["signals"],
            "threshold": bars["3_noise"]["threshold"],
            "passed": noise["passed"],
            "scored_over": noise["scored_over"],
        },
    }


STAGES = [
    (
        "smoke",
        "pass2_r2_pack_think_smoke.json",
        "the longest thread — s/call, thought tokens, VRAM",
    ),
    ("smoke", "pass1_dev_smoke_think.json", "three dev rows, into the v2 leg's own out-file"),
    ("v2 + think on dev-200", "pass1_dev_pack_think.json", "--only v2"),
    ("pass 2 + think, reference", "pass2_r2_pack_think_reference.json", "the bars re-read"),
    ("v1 + think on dev-200", "pass1_dev_pack_think.json", "--only base"),
    ("v2 + think on holdout-100", "pass1_holdout_100_think.json", "the frozen hundred"),
    ("pass 2 + think, remainder", "pass2_r2_pack_think_remainder.json", "the other 68 threads"),
]
"""The contract's VALUE order, transcribed. Each completed stage is a paired number, so a pod that
dies after stage three has bought three columns rather than nothing."""


def stage_rows(where: Path) -> list[dict]:
    rows = []
    for index, (stage, pack_name, note) in enumerate(STAGES, start=1):
        pack = json.loads((where / pack_name).read_text(encoding="utf-8"))
        legs = pack["legs"]
        rows.append(
            {
                "order": index,
                "stage": stage,
                "pack": f"results/{pack_name}",
                "sha256": sha256_of(where / pack_name),
                "serving_config": pack["serving"]["serving_config"],
                "output_tokens": pack["serving"]["output_tokens"],
                "legs": [
                    {"name": leg["name"], "units": len(leg["items"]), "out": leg["out"]}
                    for leg in legs
                ],
                "note": note,
            }
        )
    return rows


def build(where: Path = RESULTS) -> dict:
    instruments = {
        path: sha256_of(REPO_ROOT / path)
        for path in (
            "src/market_pulse/prompts.py",
            "src/market_pulse/local_llm.py",
            "src/market_pulse/reader_v5.py",
            "src/market_pulse/pass2.py",
            "src/market_pulse/pass2_r2.py",
            "scripts/reader_v5_pod_runner.py",
            "scripts/pass1_pod_runner.py",
            "scripts/pass1_fewshot_pod_runner.py",
            "scripts/pass2_r2_pod_runner.py",
            "scripts/build_think_packs.py",
            "scripts/gate_pass1_fewshot.py",
            "scripts/gate_pass2_signals_r2.py",
        )
    }
    return {
        "phase": "6t",
        "contract": "think-zero-shot",
        "what_this_is": (
            "READINGS, not bars. This record registers no threshold and grades nothing: the"
            " deliverable is a paired table and the operator decides on it"
        ),
        "authority": {
            "ruling": "(ф), 2026-08-26",
            "file": "docs/STATUS.md",
            "sha256": sha256_of(STATUS),
            "quoted": [
                quoted(
                    "Система бесполезна, пока не находит сигналы в комментах и тредах на уровне"
                    " ручного разбора тимлида; **только локальная Gemma-4-31B, thinking"
                    " ОБЯЗАТЕЛЬНО**; API-модели отклонены.",
                    STATUS,
                ),
                quoted(
                    "читатель с thinking ON ни разу не измерен; регистрации сами пишут"
                    " «thinking-ON reader = НОВАЯ регистрация»",
                    STATUS,
                ),
                quoted("Решение о дальнейшем пути — на этой таблице.", STATUS),
            ],
            "contract_file": "docs/PROMPT-think-zero-shot.md",
            "contract_sha256": sha256_of(CONTRACT),
        },
        "instrument": {
            "serving_config": packs.CONFIG,
            "chat_template": {"add_generation_prompt": True, "enable_thinking": True},
            "was": {"add_generation_prompt": True, "enable_thinking": False},
            "what_changes": quoted(
                "the same registered prompts, the same instances, Gemma-4-31B thinking ON",
                CONTRACT,
            ),
            "what_does_not": quoted(
                "Nothing is tuned:\nno prompt edit, no pack edit, no adapter.", CONTRACT
            ),
            "selected_by": (
                "scripts/reader_v5_pod_runner.SERVING_TEMPLATES, a closed table read by the pack's"
                " own `serving.serving_config`. READER_THINK is deliberately not in"
                " market_pulse.serving.CONFIGS: no HTTP worker serves it, and settings() refusing"
                " an unknown name is the correct guard until one does"
            ),
            "shas": instruments,
        },
        "before_columns": {
            "dev_200": dev_before(),
            "holdout_100": holdout_before(),
            "pass_2": pass2_before(),
        },
        "stages": stage_rows(where),
        "one_attempt": quoted("ONE attempt per stage; no re-runs.", CONTRACT),
        "money": {
            "cap_usd": CAP_USD,
            "quoted": quoted(
                "ONE pod (RTX PRO 4500 32 GB, EU-RO-1, `mp-srv2`; fallback 4090 $0.74), cap $8.00",
                CONTRACT,
            ),
            "rungs": [
                quoted("(0) price ≤$0.80/h at create", CONTRACT),
                quoted(
                    "(1) liveness — 900 s from the LAST reply or\n`nvidia-smi` activity (thinking"
                    " is silent longer than JSON)",
                    CONTRACT,
                ),
                quoted(
                    "(2) projection after the smoke and\nafter every stage at MEASURED s/call —"
                    " over the cap by ≤20% → **ASK**: hold the pod ≤10 min for the\noperator's"
                    " typed word (quoted verbatim in the report), silence = KILL; over by more →"
                    " KILL;",
                    CONTRACT,
                ),
                quoted("(3) platform hard stop from the cap at the observed price", CONTRACT),
            ],
            "measurements": "results/measurements.jsonl — the smoke's s/call, thought length and"
            " peak VRAM are written there, one row each, with the source that produced them",
        },
        "producer": {
            "script": "scripts/write_think_zero_shot_prereg.py",
            "sha256": sha256_of(Path(__file__).resolve()),
            "rule": "this record rebuilds byte for byte from the files it names",
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=RESULTS)
    args = parser.parse_args(argv)
    record = build(args.out)
    target = args.out / OUT_NAME
    target.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(f"{target}  {len(record['stages'])} stages · cap ${CAP_USD:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
