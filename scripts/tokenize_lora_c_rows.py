#!/usr/bin/env python3
"""`results/lora_c_tokens.json` — the 506 v3 SFT rows through the REAL tokenizer, at $0.

Amendment 3.25 (1) orders this before `lora-c-run` buys anything: the three-ratio table in
`results/lora_c_data.json` is a MODEL — tokens-per-character measured on probe-b's 2 778–3 923
character rows and applied to rows of 5 262–9 402 (Dv757) — and a model is what the raise from
1 408 to 2 816 was derived from. This replaces it with a count.

**The quantity is the pod's own**, not a second definition of it: `train_qlora.encode_pass1`
refuses on `len(context) + len(target)` where `context` is `apply_chat_template(...)` under
`local_llm.CHAT_TEMPLATE` and `target` is the answer string. Both are tokenized here by the same
calls in the same order.

**Why `AutoTokenizer` and not `AutoProcessor`.** The pod loads the PROCESSOR and
`train_qlora.text_tokenizer` unwraps it, and that module's own docstring warns the two chat
templates are not guaranteed equal. `AutoProcessor` will not import on this machine —
`Gemma4ImageProcessor` needs `torchvision`, which is an image dependency this text-only measurement
has no use for. So the equality is PROVEN from the repository instead of assumed: the snapshot
carries exactly one template, `chat_template.jinja`, and the processor-specific `chat_template.json`
is absent (Hugging Face records it under `.no_exist/`). One file, one template, both loaders.
The check below re-derives that at every run and refuses if a second template ever appears
([[a_report_only_field_can_refuse_the_whole_row]] read forward: prove the instrument, then measure).

    PYTHONPATH=src python3.11 scripts/tokenize_lora_c_rows.py
"""

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_pass1_sft as sft  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402
import yaml  # noqa: E402

from market_pulse import local_llm  # noqa: E402

TRAIN = REPO_ROOT / "results" / "pass1_sft_v3_train.jsonl"
OUT = REPO_ROOT / "results" / "lora_c_tokens.json"
QLORA = REPO_ROOT / "config" / "qlora.yaml"
STOP_AT = 2800
"""Amendment 3.25 (1): «a **true count** above 2 800 STOPS the line back to the operator». It is not
`max_seq_len` — it is the margin the operator kept under 2 816 for the run to live in.

**The threshold has two readings and this record publishes both**, because one row sits between
them. «True count» is the tokenizer's own number, and `TEMPLATE_SLACK` existed to correct a
CHARACTER-RATIO estimate for the chat template — which `apply_chat_template` here already counts, so
adding it back double-counts the template. On the amendment's own words the count is the raw one;
with slack it is one row larger. Naming one and hiding the other is how one input gets two values
quoted kindly ([[two_values_for_one_input_get_quoted_kindly]])."""


def revision() -> str:
    return yaml.safe_load(QLORA.read_text(encoding="utf-8"))["base"]["revision"]


def templates_of(model_id: str, rev: str) -> dict:
    """Which chat templates the cached snapshot carries — the control on using the tokenizer.

    `try_to_load_from_cache` has THREE outcomes and they are not two: a path means present, a bare
    sentinel object means the Hub was asked and answered «this file does not exist» (recorded under
    `.no_exist/`), and `None` means nobody has ever asked. Absent and unasked are different answers
    and only one of them licenses this measurement ([[unreadable_now_versus_never]]).
    """
    from huggingface_hub import try_to_load_from_cache

    found = {}
    for name in ("chat_template.jinja", "chat_template.json"):
        hit = try_to_load_from_cache(model_id, name, revision=rev)
        found[name] = (
            str(hit) if isinstance(hit, str) else "UNASKED" if hit is None else "PROVEN-ABSENT"
        )
    return found


def measure(rows: list[dict]) -> dict:
    import transformers

    rev = revision()
    found = templates_of(local_llm.MODEL_ID, rev)
    if found["chat_template.json"] != "PROVEN-ABSENT":
        raise SystemExit(
            "the snapshot carries a processor-specific chat_template.json beside"
            " chat_template.jinja, or the cache has never been asked for it, so the tokenizer's"
            " template is no longer PROVABLY the pod's. Install the processor and measure through"
            " it, or stop — a substitute template would look like a measurement."
        )
    if not found["chat_template.jinja"].startswith("/"):
        raise SystemExit("no chat_template.jinja in the cached snapshot — nothing to measure with.")

    loaded = transformers.AutoTokenizer.from_pretrained(local_llm.MODEL_ID, revision=rev)
    counts = []
    for row in rows:
        prompt = loaded.apply_chat_template(
            [{"role": "user", "content": row["prompt"]}], tokenize=False, **local_llm.CHAT_TEMPLATE
        )
        context = loaded(prompt, add_special_tokens=False)["input_ids"]
        target = loaded(row["target"], add_special_tokens=False)["input_ids"]
        counts.append(
            {
                "id": row["id"],
                "chars": len(row["prompt"]) + len(row["target"]),
                "context": len(context),
                "target": len(target),
                "pod_count": len(context) + len(target),
            }
        )
    pod = sorted(one["pod_count"] for one in counts)
    with_slack = [one + sft.TEMPLATE_SLACK for one in pod]
    over_true = [one for one in counts if one["pod_count"] > STOP_AT]
    over_slack = [one for one in counts if one["pod_count"] + sft.TEMPLATE_SLACK > STOP_AT]
    ceiling = int(yaml.safe_load(QLORA.read_text(encoding="utf-8"))["training"]["max_seq_len"])
    over_ceiling = [one for one in counts if one["pod_count"] > ceiling]
    over_ceiling_slack = [one for one in counts if one["pod_count"] + sft.TEMPLATE_SLACK > ceiling]
    return {
        "instrument": {
            "model_id": local_llm.MODEL_ID,
            "revision": rev,
            "tokenizer": type(loaded).__name__,
            "chat_template": local_llm.CHAT_TEMPLATE,
            "templates_in_the_snapshot": found,
            "quantity": (
                "len(apply_chat_template(prompt)) + len(target) — `train_qlora.encode_pass1`'s own"
                " refusal expression, the same calls in the same order"
            ),
            "why_not_the_processor": (
                "AutoProcessor needs torchvision for Gemma4ImageProcessor and this is a text-only"
                " count; the snapshot carries one template file and no processor-specific one, so"
                " the two loaders read the same bytes"
            ),
        },
        "rows": len(counts),
        "pod_count": {"min": pod[0], "median": statistics.median(pod), "max": pod[-1]},
        "pod_count_plus_template_slack": {
            "slack": sft.TEMPLATE_SLACK,
            "min": with_slack[0],
            "median": statistics.median(with_slack),
            "max": with_slack[-1],
        },
        "max_seq_len": int(
            yaml.safe_load(QLORA.read_text(encoding="utf-8"))["training"]["max_seq_len"]
        ),
        "config_sha256": summary.sha256_of(QLORA),
        "stop_threshold": STOP_AT,
        "rows_over_the_stop_threshold": {
            "by_the_true_count": len(over_true),
            "with_template_slack": len(over_slack),
            "which_the_amendment_names": "by_the_true_count — «a true count above 2 800»",
            "the_difference": [one["id"] for one in over_slack if one not in over_true],
            "why_they_differ": (
                f"TEMPLATE_SLACK = {sft.TEMPLATE_SLACK} corrected a CHARACTER-RATIO estimate for the"
                " chat template; apply_chat_template already counts it here, so adding it back"
                " double-counts. One row sits inside that margin"
            ),
        },
        "over": {
            "by_the_true_count": [one["id"] for one in over_true],
            "with_template_slack": [one["id"] for one in over_slack],
        },
        "rows_over_max_seq_len": {
            "ceiling": ceiling,
            "by_the_true_count": [one["id"] for one in over_ceiling],
            "with_template_slack": [one["id"] for one in over_ceiling_slack],
            "reading": (
                "these are the rows train_qlora.encode_pass1 would REFUSE on the pod, and the two"
                " readings agree on them — which is what makes the STOP invariant to the question"
                " above"
            ),
        },
        "verdict": (
            "STOP — a true count above 2 800 on"
            f" {len(over_true)} of {len(counts)} rows, and {len(over_ceiling)} of them are over"
            f" max_seq_len {ceiling} itself. The STOP fires under BOTH readings of the threshold."
            " Back to the operator; the next rung is 3 072"
            if over_true or over_ceiling
            else "the amendment's reality check PASSES: every row is at or under 2 800"
        ),
        "the_model_this_replaces": {
            "why": (
                "amendment 3.25 (1) derived 2 816 from 2 759 — the widest row at the registered"
                " worst tokens-per-character. That is a MODEL measured on probe-b's 2 778-3 923"
                " character rows and applied to rows of 5 262-9 415 (Dv757). Here is what it"
                " predicts against what the tokenizer counts, on the SAME rows"
            ),
            "predicted_max_with_slack": {
                name: max(math.ceil(one["chars"] * ratio) + sft.TEMPLATE_SLACK for one in counts)
                for name, ratio in (
                    ("registered_worst_0.291741", 0.291741),
                    ("median_0.282802", 0.282802),
                    ("minimum_0.269618", 0.269618),
                )
            },
            "true_max_with_slack": with_slack[-1],
            "the_model_underpredicts_by": with_slack[-1]
            - max(math.ceil(one["chars"] * 0.291741) + sft.TEMPLATE_SLACK for one in counts),
        },
        "widest_rows": sorted(counts, key=lambda one: -one["pod_count"])[:5],
        "source": {"file": summary.rel(TRAIN), "sha256": summary.sha256_of(TRAIN)},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    rows = [
        json.loads(one) for one in TRAIN.read_text(encoding="utf-8").splitlines() if one.strip()
    ]
    record = measure(rows)
    args.out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {summary.rel(args.out)}  {record['rows']} rows")
    print(
        f"  pod count      min {record['pod_count']['min']}"
        f"  median {record['pod_count']['median']}  max {record['pod_count']['max']}"
    )
    print(
        f"  + TEMPLATE_SLACK {record['pod_count_plus_template_slack']['slack']}:"
        f"  max {record['pod_count_plus_template_slack']['max']}"
        f"  against max_seq_len {record['max_seq_len']} and the STOP at {record['stop_threshold']}"
    )
    over = record["rows_over_the_stop_threshold"]
    print(
        f"  over {record['stop_threshold']}:  {over['by_the_true_count']} by the TRUE count,"
        f"  {over['with_template_slack']} with slack"
        f"  ({', '.join(over['the_difference']) or 'no row between the readings'})"
    )
    print(
        f"  over max_seq_len {record['max_seq_len']}:"
        f"  {len(record['rows_over_max_seq_len']['by_the_true_count'])} under BOTH readings"
    )
    print(f"  {record['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
