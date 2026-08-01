#!/usr/bin/env python3
"""QLoRA fine-tune of the Phase 4 base, in the precision every gate is scored in.

The invariant this script exists to hold is **train/eval format identity**: a
training example is the same fixed prompt the eval path sends (T1 or T2, hashed
into every record) plus the gold answer serialized in the exact JSON schema
`prompts.parse_reply` reads back. Both halves are asserted rather than trusted —
the prompt SHA256 against the recorded runs, and every target through the parser
itself. A fine-tune trained on a prompt that moved is trained for a different
task than the one the gates score.

Everything about precision comes from `market_pulse.local_llm`: the same NF4
dict that 4a's zero-shot anchor was measured through, that this trains adapters
against, and that production serves. The deliverable is the 4-bit base plus the
UNMERGED adapter (SPEC amendment 3.4 (1)).

The two ablation arms differ by exactly one data path — `--with-synthetic` adds
`synthetic_sarcasm.jsonl` and nothing else, and the assertion that says so is
not optional (amendment 3.4 (3)).

    PYTHONPATH=src python3 scripts/train_qlora.py --build-only
    PYTHONPATH=src python3 scripts/train_qlora.py --out results/train/smoke --max-steps 50

torch, transformers, peft and bitsandbytes live in the `gpu` extra and are
imported inside functions, never at module scope: `--build-only` is the whole
dataset contract and it has to run on a bare checkout, which is also where the
tests run.
"""

import argparse
import json
import random
import sys
import time
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed

import yaml  # noqa: E402

from market_pulse import local_llm, prompts, records, scorer  # noqa: E402

FROZEN = REPO_ROOT / "data" / "frozen"
ANNOTATION = REPO_ROOT / "data" / "annotation"
RESULTS = REPO_ROOT / "results" / "baselines.json"
CONFIG = REPO_ROOT / "config" / "qlora.yaml"

SOURCES = {
    "T1": (FROZEN / "comments_train.jsonl", ANNOTATION / "sarcasm_candidates.jsonl"),
    "T2": (FROZEN / "posts_train.jsonl",),
}
SYNTHETIC = ANNOTATION / "synthetic_sarcasm.jsonl"

NEVER_READ = (
    FROZEN / "comments_test.jsonl",
    FROZEN / "posts_test.jsonl",
    FROZEN / "sarcasm_holdout.jsonl",
    ANNOTATION / "sarcasm_holdout_pool.jsonl",
)
"""The files no training run may open, named one by one rather than by folder.

`docs/PROMPT-4b.md` says "never read `data/frozen/*`" and in the same breath
names `comments_train.jsonl` and `posts_train.jsonl` as the training sources —
and both of those live in `data/frozen/`. The rule the sentence means is the
one enforced here: the frozen *test* sets and the holdout, plus the holdout pool
whose non-sarcastic rows share threads with the holdout. A folder rule would
either forbid the training data or, written loosely, permit the test sets.
"""


# --- the dataset ------------------------------------------------------------
def load(path: Path) -> list[dict]:
    if path.resolve() in {p.resolve() for p in NEVER_READ}:
        raise SystemExit(f"{path.name} is a frozen test input — training must never open it")
    if not path.exists():
        raise SystemExit(f"{path}: not found")
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def answer(task: str, row: dict) -> str:
    """The gold labels of one row, written the way the model must write them.

    Serialized in `parse_reply`'s schema and normalised the way `parse_reply`
    normalises: intents deduplicated and sorted, brand mentions reduced to a
    ``mention`` with collapsed whitespace and no ``brand_id`` (a model cannot
    know an id the annotator assigned). :func:`assert_format_identity` sends
    every one of these back through the parser.
    """
    if task == "T1":
        payload = {
            "sentiment": row["sentiment"],
            "sarcasm": row["sarcasm"],
            "intents": sorted(set(row["intents"])),
        }
    else:
        payload = {
            "relevant": row["relevant"],
            "post_type": row["post_type"],
            "brands": [{"mention": " ".join(b["mention"].split())} for b in row["brands"]],
        }
    return json.dumps(payload, ensure_ascii=False)


def examples(task: str, path: Path) -> list[dict]:
    """Scoreable rows of one file as training examples.

    ``unclear`` rows are dropped. The assumption, stated because the brief asks
    for it: a row the annotator could not decide has no right answer to teach,
    and SPEC §4 already excludes it from every gate — training on it would put a
    label into the model that the scorer refuses to score. It is a large drop
    (694 of 1 600 comments, 206 of 746 candidates) and the counts are printed.
    """
    return [
        {
            "task": task,
            "id": row["id"],
            "source": path.name,
            "text": row["text"],
            "target": answer(task, row),
        }
        for row in load(path)
        if not row["unclear"]
    ]


def order(example: dict) -> tuple[str, str]:
    return example["task"], example["id"]


def assemble(with_synthetic: bool, carve_rows: int, seed: int) -> dict:
    """The training set and the carve, both deterministic.

    The carve is drawn from the REAL pool before the synthetic rows join, so both
    arms hold out the same rows and still differ by exactly the synthetic ids.
    """
    real = sorted(
        (row for task, paths in SOURCES.items() for path in paths for row in examples(task, path)),
        key=order,
    )
    # (task, id) is the key every arm comparison is a set over, and a post and a
    # comment can carry the same `@channel:msg_id` (18 of them do) — a duplicate
    # inside one task would collapse in those sets and hide a difference.
    keys = [order(row) for row in real]
    if len(set(keys)) != len(keys):
        repeated = sorted({key for key in keys if keys.count(key) > 1})
        raise SystemExit(f"the training sources repeat {len(repeated)} rows: {repeated[:5]}")
    held = sorted(random.Random(seed).sample(real, carve_rows), key=order)
    held_ids = {order(row) for row in held}
    train = [row for row in real if order(row) not in held_ids]
    if with_synthetic:
        train += examples("T1", SYNTHETIC)
    train.sort(key=order)
    return {"train": train, "carve": held}


def content_hash(rows: list[dict]) -> str:
    """A hash of the assembled data, not of the order it was assembled in."""
    lines = sorted(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows)
    return sha256("\n".join(lines).encode("utf-8")).hexdigest()


def assert_format_identity(rows: list[dict]) -> None:
    """Every target must parse back to the labels it was built from.

    The eval path's parser is the only thing allowed to decide whether an answer
    is an answer; a target it cannot read is a target the model would be trained
    to produce and the scorer would count as a parse failure.
    """
    for row in rows:
        parsed = prompts.parse_reply(row["task"], row["target"])
        if json.dumps(parsed, ensure_ascii=False, sort_keys=True) != json.dumps(
            json.loads(row["target"]), ensure_ascii=False, sort_keys=True
        ):
            raise SystemExit(f"{row['id']}: the parser does not read this target back: {parsed}")


def assert_arm_identity(real: list[dict], synthetic: list[dict]) -> list[str]:
    """The two arms differ by exactly the synthetic rows, in both directions."""
    real_ids = {order(row) for row in real}
    synthetic_ids = {order(row) for row in synthetic}
    added = synthetic_ids - real_ids
    removed = real_ids - synthetic_ids
    expected = {order(row) for row in examples("T1", SYNTHETIC)}
    if removed or added != expected:
        raise SystemExit(
            f"the arms differ by more than the synthetic source: {len(added)} added,"
            f" {len(removed)} removed, {len(expected)} expected added and 0 removed."
            " One data path is the whole ablation (SPEC amendment 3.4 (3))."
        )
    return sorted(row_id for _, row_id in added)


def provenance(config: dict, arm: str, built: dict, ids: list[str]) -> dict:
    counts: dict[str, int] = {}
    for row in built["train"]:
        counts[row["source"]] = counts.get(row["source"], 0) + 1
    return {
        "arm": arm,
        "n_train": len(built["train"]),
        "n_carve": len(built["carve"]),
        "rows_per_source": counts,
        "train_sha256": content_hash(built["train"]),
        "carve_sha256": content_hash(built["carve"]),
        "synthetic_ids_added": len(ids),
        "prompt_sha256": {task: prompts.prompt_sha256(task) for task in prompts.TASKS},
        "quantization": local_llm.QUANTIZATION,
        "chat_template": local_llm.CHAT_TEMPLATE,
        "config": config,
    }


def build(config: dict, with_synthetic: bool) -> tuple[dict, dict]:
    """Both arms, asserted against each other, and the one this run trains on."""
    training = config["training"]
    real = assemble(False, training["carve_rows"], training["seed"])
    other = assemble(True, training["carve_rows"], training["seed"])
    added = assert_arm_identity(real["train"], other["train"])
    built = other if with_synthetic else real
    assert_format_identity(built["train"] + built["carve"])
    history = json.loads(RESULTS.read_text(encoding="utf-8"))
    try:
        records.assert_prompt_sha(
            records.prompt_sha_history(history, local_llm.MODEL_ID), local_llm.MODEL_ID
        )
    except ValueError as err:
        raise SystemExit(str(err)) from None
    arm = "with-synthetic" if with_synthetic else "real-only"
    return built, provenance(config, arm, built, added)


# --- training ---------------------------------------------------------------
def rendered(tokenizer, example: dict) -> tuple[str, str]:
    """The prompt as the eval path sends it, and the completion that must follow.

    The prompt is the **generation** prompt, byte-identical to what
    `LocalClient.render` sends at gate time: with `enable_thinking=False` Gemma 4
    ends it with an already-closed `<|channel>thought<channel|>`, and the model
    answers from there.

    Rendering the whole assistant turn instead — the obvious way to build a
    training example — produces a *different* prefix: measured on this exact
    template revision, the turn form drops the thought channel entirely. Training
    on that would condition the model on a context the eval path never sends,
    which is the quiet kind of train/serve skew that shows up only as gates that
    came out lower than the smoke suggested. So the prompt comes from the eval
    call and only the end-of-turn marker is taken from the turn form — derived
    from the template rather than typed here, because it is the token that stops
    generation and `_trim` reads it back.
    """
    messages = prompts.build_messages(example["task"], example["text"])
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, **local_llm.CHAT_TEMPLATE)
    turn = tokenizer.apply_chat_template(
        [*messages, {"role": "assistant", "content": example["target"]}],
        tokenize=False,
        add_generation_prompt=False,
        enable_thinking=False,
    )
    head, _, tail = turn.partition(example["target"])
    tail = tail.rstrip("\n")  # generation stops at the marker; what follows is unreachable
    if not head.endswith("\n") or not tail or "<|" in tail or len(tail) > 32:
        raise SystemExit(
            "the chat template does not close an assistant turn the way this trainer reads"
            f" it — tail {tail!r}. The completion must be the answer plus one end-of-turn"
            " marker; stop and report rather than training on a guessed suffix."
        )
    return prompt, example["target"] + tail


def encode(tokenizer, example: dict, max_seq_len: int) -> dict:
    """One example as ids plus labels, with the prompt masked out of the loss."""
    prompt, completion = rendered(tokenizer, example)
    context = tokenizer(prompt, add_special_tokens=False)["input_ids"]
    target = tokenizer(completion, add_special_tokens=False)["input_ids"]
    if len(context) + len(target) > max_seq_len:
        raise SystemExit(
            f"{example['id']} needs {len(context) + len(target)} tokens against a"
            f" max_seq_len of {max_seq_len}. Raise the cap in config/qlora.yaml and"
            " re-freeze it — truncating teaches a cut-off label."
        )
    return {"input_ids": context + target, "labels": [-100] * len(context) + target}


def collate(rows: list[dict], pad_id: int, device=None) -> dict:
    """Right-padded tensors; padding is masked out of both attention and loss."""
    import torch

    width = max(len(row["input_ids"]) for row in rows)
    batch = {
        "input_ids": torch.tensor(
            [row["input_ids"] + [pad_id] * (width - len(row["input_ids"])) for row in rows]
        ),
        "attention_mask": torch.tensor(
            [[1] * len(row["input_ids"]) + [0] * (width - len(row["input_ids"])) for row in rows]
        ),
        "labels": torch.tensor(
            [row["labels"] + [-100] * (width - len(row["labels"])) for row in rows]
        ),
    }
    # a plain dict, so the move is explicit: `BatchEncoding.to` is the tokenizer's,
    # and this collator does not build one
    return batch if device is None else {key: value.to(device) for key, value in batch.items()}


def adapter_targets(model, lora: dict) -> list[str]:
    """The concrete module names LoRA attaches to, resolved on the real model.

    A list of suffixes is a wish; this is the answer, and it is recorded. The
    vision tower is excluded by prefix because we train on text only — an
    adapter there would be untrained weights on the serving path.
    """
    names = sorted(
        {
            name
            for name, _ in model.named_modules()
            if name.split(".")[-1] in lora["target_suffixes"]
            and not any(part in lora["exclude_prefixes"] for part in name.split("."))
        }
    )
    if not names:
        raise SystemExit(
            f"no module matches {lora['target_suffixes']} outside {lora['exclude_prefixes']}:"
            " this base names its projections differently. Stop and report."
        )
    return names


def load_for_training(config: dict, resume: Path | None = None):
    """The NF4 base of `local_llm`, prepared for k-bit training, plus adapters."""
    from peft import LoraConfig, PeftModel, get_peft_model, prepare_model_for_kbit_training

    tokenizer, model = local_llm.load(
        revision=config["base"]["revision"], seed=config["training"]["seed"]
    )
    model = prepare_model_for_kbit_training(
        model, use_gradient_checkpointing=config["training"]["gradient_checkpointing"]
    )
    lora = config["lora"]
    targets = adapter_targets(model, lora)
    if resume:
        model = PeftModel.from_pretrained(model, str(resume / "adapter"), is_trainable=True)
    else:
        model = get_peft_model(
            model,
            LoraConfig(
                r=lora["r"],
                lora_alpha=lora["alpha"],
                lora_dropout=lora["dropout"],
                target_modules=targets,
                bias="none",
                task_type="CAUSAL_LM",
            ),
        )
    model.config.use_cache = False  # incompatible with gradient checkpointing
    print(f"LoRA on {len(targets)} modules, e.g. {targets[:2]}")
    return tokenizer, model


def assert_resumable(state: dict, trainable: int) -> None:
    """A resumed optimizer state must cover exactly the parameters that train.

    ``load_state_dict`` maps state onto parameters **by index**. If the trainable
    reload yields a different parameter list than the run that saved the state —
    a different LoRA config, a different target set, an adapter from another arm
    — the wrong momentum lands on the wrong tensor and nothing raises. The loss
    curve is what would eventually show it; this shows it in the first second,
    which is the difference between losing a resume and losing an arm.
    """
    loaded = len(state["optimizer"]["state"])
    if loaded != trainable:
        raise SystemExit(
            f"the checkpoint carries optimizer state for {loaded} parameters and this model has"
            f" {trainable} trainable ones. Resuming would map momentum onto the wrong tensors"
            " silently — stop and report rather than continuing from a state that does not fit."
        )


def carve_loss(model, batches) -> float:
    """Mean loss over the held-out carve. A thermometer: it selects nothing."""
    import torch

    model.eval()
    with torch.no_grad():
        losses = [float(model(**batch).loss) for batch in batches]
    model.train()
    return sum(losses) / len(losses)


def train(config: dict, built: dict, out: Path, max_steps: int | None, resume: Path | None) -> dict:
    """The loop. Fixed epochs, no early stopping, nothing selected against an eval."""
    import torch
    from bitsandbytes.optim import PagedAdamW8bit
    from transformers import get_cosine_schedule_with_warmup

    settings, tuning = config["training"], config["optimizer"]
    tokenizer, model = load_for_training(config, resume)
    encoded = [encode(tokenizer, row, settings["max_seq_len"]) for row in built["train"]]
    carve = [
        collate(
            [encode(tokenizer, row, settings["max_seq_len"])], tokenizer.pad_token_id, model.device
        )
        for row in built["carve"]
    ]

    micro, accum = settings["micro_batch_size"], settings["grad_accum"]
    per_epoch = -(-len(encoded) // (micro * accum))
    planned = per_epoch * settings["epochs"]
    # The schedule is always the FULL run's, and `--max-steps` only stops early:
    # a smoke whose cosine decayed to zero in 50 steps would preview a different
    # trajectory than the run it is supposed to project.
    total = min(planned, max_steps or planned)
    optimizer = PagedAdamW8bit(
        [p for p in model.parameters() if p.requires_grad], lr=tuning["learning_rate"]
    )
    scheduler = get_cosine_schedule_with_warmup(
        optimizer, int(tuning["warmup_ratio"] * planned), planned
    )
    start_epoch, start_index, step = 0, 0, 0
    if resume:
        # tensors and plain containers only, so the safe loader reads it
        state = torch.load(resume / "state.pt", map_location="cpu", weights_only=True)
        assert_resumable(state, sum(1 for p in model.parameters() if p.requires_grad))
        optimizer.load_state_dict(state["optimizer"])
        scheduler.load_state_dict(state["scheduler"])
        start_epoch, start_index, step = state["epoch"], state["index"], state["step"]
        print(f"resumed at epoch {start_epoch} row {start_index}, optimizer step {step}")

    out.mkdir(parents=True, exist_ok=True)
    curve = out / "loss.jsonl"
    model.train()
    began, window, since = time.time(), [], time.time()
    epoch, index = start_epoch, start_index
    for epoch in range(start_epoch, settings["epochs"]):
        rows = list(range(len(encoded)))
        random.Random(settings["seed"] + epoch).shuffle(rows)
        index = start_index if epoch == start_epoch else 0
        seen = 0
        while index < len(rows) and step < total:
            chunk = [encoded[i] for i in rows[index : index + micro]]
            try:
                loss = model(**collate(chunk, tokenizer.pad_token_id, model.device)).loss
                (loss / accum).backward()
            except torch.cuda.OutOfMemoryError:
                if micro == 1:
                    raise
                micro, accum = micro // 2, accum * 2
                optimizer.zero_grad(set_to_none=True)
                torch.cuda.empty_cache()
                print(f"OOM: micro_batch -> {micro}, grad_accum -> {accum} (effective batch held)")
                continue
            window.append(float(loss.detach()))
            index += len(chunk)
            seen += 1
            if seen % accum:
                continue
            torch.nn.utils.clip_grad_norm_(model.parameters(), tuning["max_grad_norm"])
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad(set_to_none=True)
            step += 1
            if step % settings["log_every"] == 0 or step == total:
                line = {
                    "step": step,
                    "epoch": epoch,
                    "loss": sum(window) / len(window),
                    "lr": scheduler.get_last_lr()[0],
                    "seconds_per_step": (time.time() - since) / settings["log_every"],
                    "micro_batch": micro,
                    "gpu_gb": round(torch.cuda.max_memory_allocated() / 2**30, 2),
                }
                if step % settings["carve_every"] == 0 or step == total:
                    line["carve_loss"] = carve_loss(model, carve)
                with curve.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(line) + "\n")
                print(json.dumps(line))
                window, since = [], time.time()
            if step % settings["save_every"] == 0:
                save(model, optimizer, scheduler, out, epoch, index, step)
    save(model, optimizer, scheduler, out, epoch, index, step)
    return {
        "steps": step,
        "steps_per_epoch": per_epoch,
        "seconds": round(time.time() - began, 1),
        "seconds_per_step": round((time.time() - began) / max(step, 1), 3),
        "micro_batch_final": micro,
        "grad_accum_final": accum,
        "gpu_gb_peak": round(torch.cuda.max_memory_allocated() / 2**30, 2),
        "adapter": str((out / "adapter").relative_to(REPO_ROOT))
        if out.is_relative_to(REPO_ROOT)
        else str(out / "adapter"),
    }


def save(model, optimizer, scheduler, out: Path, epoch: int, index: int, step: int) -> None:
    """Adapter-only, plus what a resume needs. The base is never written."""
    import torch

    model.save_pretrained(str(out / "adapter"))
    torch.save(
        {
            "optimizer": optimizer.state_dict(),
            "scheduler": scheduler.state_dict(),
            "epoch": epoch,
            "index": index,
            "step": step,
        },
        out / "state.pt",
    )


def carve_mechanics(config: dict, built: dict, adapter: Path) -> dict:
    """Reload the adapter and run the local EVAL path over the carve.

    Mechanics only: that prompts render, replies parse and the scorer accepts
    the labels. Every number here is measured on rows the model trained beside,
    at a fraction of an epoch — they say nothing about quality and are labelled
    so. The frozen sets and the holdout are not opened; the ids come from the
    training pool.
    """
    import gc

    import torch
    from peft import PeftModel

    gc.collect()  # the training model is out of scope; the card is not 62 GB of spare
    torch.cuda.empty_cache()
    tokenizer, model = local_llm.load(revision=config["base"]["revision"])
    model = PeftModel.from_pretrained(model, str(adapter))
    model.eval()
    client = local_llm.LocalClient(tokenizer, model)
    parsed, failures = {}, []
    for row in built["carve"]:  # batch size 1: 4a measured that batching moves outputs
        reply = client.batch(row["task"], [row["text"]])[0]
        try:
            parsed[row["id"]] = prompts.parse_reply(row["task"], reply["content"])
        except prompts.ParseError as err:
            failures.append({"id": row["id"], "reason": err.reason})
    gold = {row["id"]: json.loads(row["target"]) for row in built["carve"]}
    scored = {
        "n": len(built["carve"]),
        "parse_failures": failures,
        "meaning": "MECHANICS ONLY — rows from the training pool, scored to prove the path runs."
        " These numbers measure nothing about the model and enter no gate.",
    }
    for task, field in (("T1", "sentiment"), ("T2", "post_type")):
        ids = [row["id"] for row in built["carve"] if row["task"] == task and row["id"] in parsed]
        if ids:
            scored[f"{task}_{field}_macro_f1"] = scorer.macro_f1(
                [gold[i][field] for i in ids], [parsed[i][field] for i in ids]
            )
            scored[f"{task}_n_parsed"] = len(ids)
    return scored


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=CONFIG)
    parser.add_argument("--with-synthetic", action="store_true", help="the ablation's second arm")
    parser.add_argument("--build-only", action="store_true", help="assemble and assert; no GPU")
    parser.add_argument("--out", type=Path, help="run directory: adapter, loss curve, provenance")
    parser.add_argument("--max-steps", type=int, help="stop after N optimizer steps (smoke)")
    parser.add_argument("--resume-from", type=Path)
    parser.add_argument("--carve-eval", action="store_true", help="mechanics check after training")
    args = parser.parse_args(argv)

    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    built, record = build(config, args.with_synthetic)
    print(json.dumps({k: v for k, v in record.items() if k != "config"}, indent=2, sort_keys=True))
    if args.build_only:
        return 0
    if not args.out:
        raise SystemExit("--out is required for a training run")

    record["run"] = train(config, built, args.out, args.max_steps, args.resume_from)
    if args.carve_eval:
        record["carve_mechanics"] = carve_mechanics(config, built, args.out / "adapter")
    record["environment"] = local_llm.environment(revision=config["base"]["revision"])
    (args.out / "provenance.json").write_text(
        json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(record["run"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
