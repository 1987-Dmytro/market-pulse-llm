#!/usr/bin/env python3
"""`scripts/train_qlora.py` with two guards re-bound for the lora-c line — a sibling, not a fork.

`docs/PROMPT-lora-c-run.md` D1. The trainer is PINNED by `results/prereg_lora_b.json` and
`results/lora_b_verdict.json`: line B's numbers rest on its bytes, so it may not be edited. It also
refuses this line's dataset twice, by name:

- `load_sft` demands `row["task"] == prompts.PASS1_TASK`, which is `pass1_comment_gm4_v1`, and
  every row of `results/pass1_sft_v3_train.jsonl` says `pass1_comment_gm4_v3`;
- `build_pass1` demands the dataset's sha appear in `results/pass1_sft.json`, which registers line
  B's two files and knows nothing of this line's.

**Exactly those two are re-bound and everything else is CALLED.** `load_sft`, `class_weights`,
`content_hash`, `load_for_training`, `encode_pass1`, `collate`, `train`, `save` and `main` are the
pinned implementations, reached through the module object — this file holds no second copy of any
of them. Guard 1 moves by swapping the constant it reads, inside a contextmanager that puts it back,
because a module-level guard cannot be told anything by a parameter
([[a_self_pinning_producer_cannot_grow_a_parameter]]). Guard 2 moves by :func:`build_pass1_v3`,
which reads the sha list out of `results/prereg_lora_c.json`.

The one thing written here rather than reached for is the provenance dict. `build_pass1`'s names
`results/pass1_sft.json`, `pass1_comment_gm4_v1` and that record's `supervision` block; a v3 run
publishing it would be describing another line's dataset in its own record
([[the_old_record_with_one_field_replaced]]).

    PYTHONPATH=src python3.11 scripts/train_qlora_v3.py --census \\
        --data results/pass1_sft_v3_arm_b.jsonl --out results/lora_c_encode_census_arm_b.json
    PYTHONPATH=src python3.11 scripts/train_qlora_v3.py --build-only --class-weights \\
        --data results/pass1_sft_v3_train.jsonl
    PYTHONPATH=src python3.11 scripts/train_qlora_v3.py --class-weights --max-steps 6 \\
        --data results/pass1_sft_v3_train.jsonl --out results/lora_c_smoke_a
"""

import argparse
import contextlib
import hashlib
import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import train_qlora as trainer  # noqa: E402
from market_pulse import local_llm, pass1_v3, prompts  # noqa: E402

REGISTRATION = REPO_ROOT / "results" / "prereg_lora_c.json"
"""Guard 2's new home. `results/pass1_sft.json` registers line B's `a` and `b` datasets and is
itself pinned by line B's sealed records; this line's datasets are registered here."""

CONFIG = REPO_ROOT / "config" / "qlora.yaml"
CENSUS_OUT = REPO_ROOT / "results" / "lora_c_encode_census.json"

TASK = pass1_v3.PASS1_TASK_V3


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@contextlib.contextmanager
def the_task_is_v3():
    """`prompts.PASS1_TASK` reads v3 for the length of one call, and v1 again after it.

    Guard 1 keys on a module constant of a PINNED module, so nothing a caller passes can reach it;
    the swap is the re-bind and the `finally` is what keeps the pin true for every other caller in
    the same process. `prompts.py` itself is never written.
    """
    was = prompts.PASS1_TASK
    prompts.PASS1_TASK = TASK
    try:
        yield
    finally:
        prompts.PASS1_TASK = was


def registered_training_shas() -> dict[str, str]:
    """The sha list guard 2 now reads — this line's registration, not line B's SFT record.

    The registration declares its training datasets under `population.train.files` — arm A's 506
    rows and arm B's 666 — and that list is the whole list. A dataset the record does not name is
    refused whatever else is on disk beside it.
    """
    record = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    return {one["file"]: one["sha256"] for one in record["population"]["train"]["files"]}


def registered_first() -> str:
    """The one registered dataset — a REFUSAL when there is more than one.

    `population.train` named a single file until `lora-c-armb` rendered arm B; with both files
    registered, «the first one» would silently pick an arm and the census would describe 506 rows
    under a report that says 666 ([[select_one_row_refuse_ambiguity]]).
    """
    files = sorted(registered_training_shas())
    if len(files) != 1:
        raise SystemExit(
            f"{REGISTRATION.name} registers {files} — name the one you mean with --data rather than"
            " let a default choose an arm."
        )
    return files[0]


def arm_of(rows: int) -> str:
    """Which registered leg a dataset of this size is — refusing a tie rather than picking one.

    The row count is registered per leg (`legs.arm_a.train_rows`), so the arm a run belongs to is a
    READING of the record and not a flag the caller asserts ([[a_flag_that_asserts_turns_a_poll_into_a_verdict]]).
    """
    record = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    named = [leg for leg, block in record["legs"].items() if block.get("train_rows") == rows]
    if len(named) != 1:
        raise SystemExit(
            f"{rows} rows match the legs {named} of {REGISTRATION.name} — a training run whose arm"
            " the registration cannot name is a run nobody registered. Stop."
        )
    return named[0]


def build_pass1_v3(config: dict, path: Path, weighted: bool) -> tuple[dict, dict]:
    """`train_qlora.build_pass1` with guard 2 on this line's registration.

    No carve, for `build_pass1`'s own reason: every labelled row of this line is trained on.
    """
    with the_task_is_v3():
        rows = trainer.load_sft(path)
    registered = registered_training_shas()
    got = sha256_of(path)
    named = [file for file, sha in registered.items() if sha == got]
    if not named:
        raise SystemExit(
            f"{path} hashes {got[:16]}… and {REGISTRATION.name} registers"
            f" {sorted((file, sha[:16]) for file, sha in registered.items())} — this is not a"
            " registered dataset of this line. Stop rather than train on bytes nobody"
            " pre-registered."
        )
    arm = arm_of(len(rows))
    weights = trainer.class_weights(rows)
    provenance = {
        "arm": arm,
        "dataset": {"file": named[0], "rows": len(rows), "sha256": got},
        "registration": {
            "file": "results/prereg_lora_c.json",
            "sha256": sha256_of(REGISTRATION),
        },
        "labelled_by": "the TEAM LEAD — results/labels_pass1_r*_provenance.json",
        "class_weights": weights if weighted else None,
        "sampler": (
            f"weighted with replacement, {len(rows)} draws per epoch, w_c ="
            f" N/({trainer.PASS1_K}·n_c) capped at {trainer.PASS1_WEIGHT_CAP}"
            if weighted
            else "uniform shuffle — the default, unchanged"
        ),
        "supervision": {
            "field": "subject_type",
            "boundary_char": trainer.SUPERVISED_SEPARATOR,
            "enforced_by": "train_qlora.load_sft, called — not asserted a second time here",
        },
        "n_train": len(rows),
        "n_carve": 0,
        "train_sha256": trainer.content_hash(rows),
        "task": TASK,
        "prompt_sha256": {TASK: pass1_v3.prompt_sha256(TASK)},
        "quantization": local_llm.QUANTIZATION,
        "chat_template": local_llm.CHAT_TEMPLATE,
        "config": config,
    }
    return {"train": rows, "carve": [], "kind": "pass1", "weighted": weighted}, provenance


def tokenizer_at_the_pinned_revision():
    """The real tokenizer, at the revision `config/qlora.yaml` pins — $0 and no GPU.

    The control is `tokenize_lora_c_rows.templates_of`, CALLED: it already distinguishes a template
    that is present, one proven absent and one nobody has ever asked for, and only the middle
    answer licenses reading the pod's template through the tokenizer rather than the processor
    ([[unreadable_now_versus_never]]). A second copy of that three-way test would be a second
    answer the day one of them moved.
    """
    import transformers

    import tokenize_lora_c_rows as census_of_tokens

    rev = census_of_tokens.revision()
    found = census_of_tokens.templates_of(local_llm.MODEL_ID, rev)
    if found["chat_template.json"] != "PROVEN-ABSENT" or not found[
        "chat_template.jinja"
    ].startswith("/"):
        raise SystemExit(
            f"the cached snapshot reads {found} — the tokenizer's template is not provably the"
            " pod's. Stop rather than count with a substitute."
        )
    return transformers.AutoTokenizer.from_pretrained(local_llm.MODEL_ID, revision=rev)


def census(path: Path, loaded=None) -> dict:
    """Every row of `path` through `train_qlora.encode_pass1` at the frozen ceiling.

    The refusal this reports is the POD's refusal: the same function, the same tokenizer and the
    same ceiling the training run will use, run here at $0 so a row too wide is a finding on a Mac
    and not a dead pod ([[a_frozen_record_is_an_input_to_shipped_code]]).
    """
    path = Path(path).resolve()
    ceiling = int(yaml.safe_load(CONFIG.read_text(encoding="utf-8"))["training"]["max_seq_len"])
    loaded = loaded if loaded is not None else tokenizer_at_the_pinned_revision()
    with the_task_is_v3():
        rows = trainer.load_sft(path)
    widths, refused = [], []
    for row in rows:
        try:
            encoded = trainer.encode_pass1(loaded, row, ceiling)
        except SystemExit as refusal:
            refused.append({"id": row["id"], "why": str(refusal)})
            continue
        widths.append({"id": row["id"], "tokens": len(encoded["input_ids"])})
    widths.sort(key=lambda one: one["tokens"])
    return {
        "file": str(path.relative_to(REPO_ROOT)),
        "sha256": sha256_of(path),
        "rows": len(rows),
        "max_seq_len": ceiling,
        "refused": refused,
        "encoded": len(widths),
        "tokens": {
            "min": widths[0]["tokens"] if widths else None,
            "median": widths[len(widths) // 2]["tokens"] if widths else None,
            "max": widths[-1]["tokens"] if widths else None,
            "widest_row": widths[-1]["id"] if widths else None,
            "narrowest_row": widths[0]["id"] if widths else None,
        },
        "headroom": ceiling - widths[-1]["tokens"] if widths else None,
        "quantity": (
            "len(apply_chat_template(prompt)) + len(target) — train_qlora.encode_pass1's own"
            " expression, called, not re-implemented"
        ),
    }


def main(argv: list[str] | None = None) -> int:
    """`train_qlora.main`, with guard 2 re-bound for the length of the call.

    `--census` is answered here because it needs the tokenizer and no GPU, and because the trainer's
    own `--build-only` stops before `encode_pass1` — the very function whose refusal this buys
    ([[exercise_the_write_path_not_just_the_compute]]).
    """
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--census" in argv:
        parser = argparse.ArgumentParser(description="the encode census, at $0")
        parser.add_argument("--census", action="store_true")
        parser.add_argument("--data", type=Path, default=None)
        parser.add_argument("--out", type=Path, default=CENSUS_OUT)
        args = parser.parse_args(argv)
        record = census(args.data or REPO_ROOT / registered_first())
        args.out.write_text(
            json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False))
        return 1 if record["refused"] else 0
    was = trainer.build_pass1
    trainer.build_pass1 = build_pass1_v3
    try:
        return trainer.main(argv)
    finally:
        trainer.build_pass1 = was


if __name__ == "__main__":
    raise SystemExit(main())
