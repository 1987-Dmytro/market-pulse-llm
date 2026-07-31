#!/usr/bin/env python3
"""Baseline (b) for Phase 3: a fine-tuned XLM-R encoder, scored by the scorer.

SPEC §7 pre-registers three baselines and this is the middle one: a real
supervised model, trained here on this Mac's GPU (Apple MPS), $0, no pod rented.
It is deliberately untuned — one pre-registered config, seed 42, no search — for
the same reason `scripts/run_baseline.py` is: a baseline you tuned is not the
number the fine-tune has to beat.

**Gate coverage, stated rather than implied.** XLM-R here is a sequence
classifier, so it covers G1a (sentiment), G1c (intents) and G1d (post type, with
relevance reported beside it). It does **not** cover G1e: brand-mention
extraction is span extraction, and no token-classification head was trained for
it. That cell is written as an explicit "not covered", never as a blank or a
zero — a blank that reads as "scored badly" when it means "was never attempted"
is a reporting bug. G1b is `null` here for the same reason it is `null` for
TF-IDF: amendment 3.2 defines the slice by the *zero-shot* base LLM's errors, and
a fix-rate needs a fine-tune.

Nine independent heads, mirroring how the TF-IDF baseline fits one classifier per
head: sentiment, sarcasm and five intents on comments; relevance and post type on
posts. A timed smoke runs first and refuses to start the full run if it projects
past the operator's wall-clock ceiling.

    pip install -e '.[xlmr]'      # or just: pip install 'transformers>=4.44'
    python3.11 scripts/train_xlmr_baseline.py --smoke
    python3.11 scripts/train_xlmr_baseline.py
"""

import argparse
import gc
import json
import math
import random
import subprocess
import sys
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed

from market_pulse import scorer  # noqa: E402
from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

FROZEN = REPO_ROOT / "data" / "frozen"
ANNOTATION = REPO_ROOT / "data" / "annotation"
RESULTS = REPO_ROOT / "results" / "baselines.json"

MODEL = "xlm-roberta-base"
SEED = 42
EPOCHS = 3
BATCH_SIZE = 16
EVAL_BATCH_SIZE = 32
LEARNING_RATE = 2e-5
MAX_LENGTH = 256
WARMUP_SHARE = 0.1
SMOKE_STEPS = 12
DEFAULT_TIME_BUDGET_MIN = 60.0
# CPU, not MPS, and that is measured rather than assumed. On this Mac (torch
# 2.13.0, macOS 25.6) an xlm-roberta-base training step takes 3.5 s on the CPU
# and 33-114 s on MPS — ten to thirty times slower, and MPS additionally OOMs at
# its 9.07 GiB allocator ceiling unless the 250k x 768 word-embedding matrix is
# frozen (which it is, see Trainer.train_head). `--device mps` is still there for
# a machine where the backend behaves.
DEFAULT_DEVICE = "cpu"


def load(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"{path}: not found")
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def scoreable(rows: list[dict]) -> list[dict]:
    return [row for row in rows if not row["unclear"]]


def normalised(text: str) -> str:
    return " ".join(text.split()).lower()


def gold(rows: list[dict], field: str, unclear=scorer.UNCLEAR):
    return [unclear if row["unclear"] else row[field] for row in rows]


def git_state() -> dict:
    def run(*args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=True
        ).stdout

    dirty = [line.split(maxsplit=1)[1] for line in run("status", "--porcelain").splitlines()]
    ignore = {"results/baselines.json", "results/spend_3b.json"}
    return {
        "commit": run("rev-parse", "HEAD").strip(),
        "dirty": sorted(path for path in dirty if path not in ignore),
    }


def append(record: dict) -> None:
    """Append-only: a model's runs accumulate, none is ever overwritten."""
    RESULTS.parent.mkdir(exist_ok=True)
    history = json.loads(RESULTS.read_text(encoding="utf-8")) if RESULTS.exists() else {}
    history.setdefault(record["model"], []).append(record)
    RESULTS.write_text(json.dumps(history, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def steps_for(rows: int, epochs: int = EPOCHS) -> int:
    return epochs * math.ceil(rows / BATCH_SIZE)


class Trainer:
    """One tokenizer, one device, a fresh encoder per head.

    `transformers.Trainer` is not used: it pulls `accelerate` in and hides the
    handful of decisions that matter (class weights, schedule, seeding) behind a
    config surface. Forty lines of loop keep them visible and pinned.
    """

    def __init__(self, device: str):
        import torch
        from transformers import AutoTokenizer

        self.torch = torch
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL)
        self.step_seconds: list[float] = []
        self.eval_seconds: list[tuple[int, float]] = []

    def _batches(self, size: int, count: int, shuffle: bool, seed: int):
        order = list(range(count))
        if shuffle:
            random.Random(seed).shuffle(order)
        for start in range(0, count, size):
            yield order[start : start + size]

    def _encode(self, texts: list[str]):
        batch = self.tokenizer(
            texts, truncation=True, max_length=MAX_LENGTH, padding=True, return_tensors="pt"
        )
        return {key: value.to(self.device) for key, value in batch.items()}

    def train_head(self, texts: list[str], labels: list[int], classes: int, max_steps=None):
        from transformers import AutoModelForSequenceClassification

        torch = self.torch
        torch.manual_seed(SEED)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL, num_labels=classes)
        # The word-embedding matrix is 250k x 768 — 192M of the model's 278M
        # parameters — and AdamW would keep two fp32 moments for every one of
        # them. That is what a 9 GB MPS allocator refuses, and it buys nothing:
        # 1,446 training rows cannot meaningfully move a 250k-row vocabulary.
        # Frozen before the first number was produced, recorded in the config.
        model.get_input_embeddings().weight.requires_grad_(False)
        model.to(self.device).train()

        # Inverse-frequency weights, the encoder's answer to `class_weight="balanced"`
        # in the TF-IDF baseline: macro-averaged gates with classes at n=19 and n=26
        # otherwise let the rare ones vanish. Chosen before the run, not after.
        counts = Counter(labels)
        weights = torch.tensor(
            [len(labels) / (classes * max(counts[index], 1)) for index in range(classes)],
            dtype=torch.float32,
            device=self.device,
        )
        loss_fn = torch.nn.CrossEntropyLoss(weight=weights)
        trainable = [p for p in model.parameters() if p.requires_grad]
        optimiser = torch.optim.AdamW(trainable, lr=LEARNING_RATE)
        total = max_steps or steps_for(len(texts))
        schedule = torch.optim.lr_scheduler.OneCycleLR(
            optimiser,
            max_lr=LEARNING_RATE,
            total_steps=total,
            pct_start=WARMUP_SHARE,
            anneal_strategy="linear",
            cycle_momentum=False,  # AdamW: cycling betas is a knob nobody asked for
        )

        done = 0
        for epoch in range(EPOCHS):
            for rows in self._batches(BATCH_SIZE, len(texts), shuffle=True, seed=SEED + epoch):
                started = time.perf_counter()
                batch = self._encode([texts[i] for i in rows])
                target = torch.tensor([labels[i] for i in rows], device=self.device)
                loss = loss_fn(model(**batch).logits, target)
                loss.backward()
                optimiser.step()
                schedule.step()
                optimiser.zero_grad(set_to_none=True)
                self.step_seconds.append(time.perf_counter() - started)
                done += 1
                if done >= total:
                    return model
        return model

    def release(self, model) -> None:
        """Nine encoders in one process: hand each one back before the next."""
        del model
        gc.collect()
        if self.device == "mps":
            self.torch.mps.empty_cache()

    def predict(self, model, texts: list[str]) -> list[int]:
        torch = self.torch
        model.eval()
        started = time.perf_counter()
        out: list[int] = []
        with torch.no_grad():
            for rows in self._batches(EVAL_BATCH_SIZE, len(texts), shuffle=False, seed=0):
                logits = model(**self._encode([texts[i] for i in rows])).logits
                out.extend(int(value) for value in logits.argmax(dim=-1).cpu())
        self.eval_seconds.append((len(texts), time.perf_counter() - started))
        return out


def fit_predict(trainer, train_rows, labels, label_names, eval_sets):
    """One head: fit on the training rows, predict each eval set, return labels."""
    index = {name: position for position, name in enumerate(label_names)}
    model = trainer.train_head(
        [row["text"] for row in train_rows], [index[value] for value in labels], len(label_names)
    )
    predictions = [
        [label_names[value] for value in trainer.predict(model, [row["text"] for row in rows])]
        if rows
        else []
        for rows in eval_sets
    ]
    trainer.release(model)
    return predictions


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true", help="time a few steps, project, stop")
    parser.add_argument("--time-budget-min", type=float, default=DEFAULT_TIME_BUDGET_MIN)
    parser.add_argument("--device", default=DEFAULT_DEVICE, help="cpu | mps")
    args = parser.parse_args(argv)

    device = args.device

    comments_train = load(FROZEN / "comments_train.jsonl")
    mined = load(ANNOTATION / "sarcasm_candidates.jsonl")
    posts_train = load(FROZEN / "posts_train.jsonl")
    comments_test = load(FROZEN / "comments_test.jsonl")
    posts_test = load(FROZEN / "posts_test.jsonl")
    holdout = load(FROZEN / "sarcasm_holdout.jsonl")

    # Real sources only. synthetic_sarcasm.jsonl is ablation-gated for Phase 4 and
    # is not opened here; sarcasm_holdout_pool.jsonl is not training data at all.
    t1_train = scoreable(comments_train) + scoreable(mined)
    t2_train = scoreable(posts_train)

    train_texts = {normalised(row["text"]) for row in t1_train}
    leaked = [row["id"] for row in holdout if normalised(row["text"]) in train_texts]
    assert not leaked, f"holdout text present in the training pool: {leaked[:3]}"

    print(f"device {device} · {MODEL} · seed {SEED} · {EPOCHS} epochs · batch {BATCH_SIZE}")
    print(f"T1 train: {len(t1_train)} scoreable rows")
    print(f"  comments_train        {len(scoreable(comments_train)):>5} of {len(comments_train)}")
    print(f"  sarcasm_candidates    {len(scoreable(mined)):>5} of {len(mined)} (sarcasm-enriched)")
    print(f"T2 train: {len(t2_train)} of {len(posts_train)} scoreable posts")

    t1_steps, t2_steps = steps_for(len(t1_train)), steps_for(len(t2_train))
    plan = {
        "sentiment": (t1_steps, len(comments_test) + len(holdout)),
        "sarcasm": (t1_steps, len(comments_test) + len(holdout)),
        **{f"intent:{name}": (t1_steps, len(comments_test)) for name in scorer.INTENTS},
        "relevance": (t2_steps, len(posts_test)),
        "post_type": (t2_steps, len(posts_test)),
    }
    total_steps = sum(steps for steps, _ in plan.values())
    total_eval = sum(rows for _, rows in plan.values())
    print(f"\nplan: {len(plan)} heads · {total_steps} training steps · {total_eval} eval rows")

    trainer = Trainer(device)
    print(f"\nsmoke: timing {SMOKE_STEPS} steps + one eval pass…")
    started = time.perf_counter()
    model = trainer.train_head(
        [row["text"] for row in t1_train],
        [scorer.SENTIMENT_LABELS.index(row["sentiment"]) for row in t1_train],
        len(scorer.SENTIMENT_LABELS),
        max_steps=SMOKE_STEPS,
    )
    trainer.predict(model, [row["text"] for row in comments_test[:64]])
    smoke_seconds = time.perf_counter() - started
    trainer.release(model)

    # Drop the first step: it carries lazy kernel compilation, not the steady rate.
    per_step = sum(trainer.step_seconds[1:]) / max(len(trainer.step_seconds) - 1, 1)
    rows, seconds = trainer.eval_seconds[0]
    per_eval_row = seconds / rows
    projected = (total_steps * per_step + total_eval * per_eval_row) / 60
    print(
        f"  smoke took {smoke_seconds:.1f}s · {per_step:.3f}s/step · {per_eval_row * 1000:.1f}ms/row"
    )
    print(f"  PROJECTED FULL RUN: {projected:.1f} min (budget {args.time_budget_min:.0f} min)")

    if args.smoke:
        print("\n--smoke: nothing trained, nothing written")
        return 0
    if projected > args.time_budget_min:
        print(
            f"\nSTOP: {projected:.1f} min exceeds the {args.time_budget_min:.0f}-minute ceiling."
            " Reporting the estimate instead of starting the run — the operator moves it to a pod."
        )
        return 3

    trainer.step_seconds.clear()
    trainer.eval_seconds.clear()
    run_started = time.perf_counter()

    print("\nfitting T1 heads (sentiment · sarcasm · 5 intents)…")
    sentiment_pred, holdout_sentiment = fit_predict(
        trainer,
        t1_train,
        [row["sentiment"] for row in t1_train],
        list(scorer.SENTIMENT_LABELS),
        [comments_test, holdout],
    )
    sarcasm_pred, holdout_sarcasm = fit_predict(
        trainer,
        t1_train,
        [row["sarcasm"] for row in t1_train],
        [False, True],
        [comments_test, holdout],
    )
    intent_pred: list[set[str]] = [set() for _ in comments_test]
    for intent in scorer.INTENTS:
        print(f"  intent {intent}…")
        (flags,) = fit_predict(
            trainer,
            t1_train,
            [intent in row["intents"] for row in t1_train],
            [False, True],
            [comments_test],
        )
        for row, flag in zip(intent_pred, flags):
            if flag:
                row.add(intent)

    print("fitting T2 heads (relevance · post_type)…")
    (relevance_pred,) = fit_predict(
        trainer, t2_train, [row["relevant"] for row in t2_train], [False, True], [posts_test]
    )
    (post_type_pred,) = fit_predict(
        trainer,
        t2_train,
        [row["post_type"] for row in t2_train],
        list(scorer.POST_TYPES),
        [posts_test],
    )
    wall_minutes = (time.perf_counter() - run_started) / 60
    print(f"\nfull run took {wall_minutes:.1f} min (projected {projected:.1f})")

    aliases = watchlist_aliases(load_registry(REPO_ROOT / "config" / "registry.yaml").watchlist)
    languages = [row["language"] for row in comments_test]
    sentiment = scorer.sentiment_macro_f1(
        gold(comments_test, "sentiment"), sentiment_pred, languages
    )
    holdout_sentiment_f1 = scorer.sentiment_macro_f1(
        gold(holdout, "sentiment"), holdout_sentiment, [row["language"] for row in holdout]
    )
    base_errors = [
        row["id"]
        for row, pred in zip(holdout, holdout_sentiment)
        if not row["unclear"] and row["sentiment"] != pred
    ]

    gates = [
        {
            "gate": "G1a",
            "metric": "sentiment macro-F1 (comments_test)",
            "values": sentiment,
            "n": {"overall": len(comments_test), **Counter(languages)},
            "gated_languages": list(scorer.GATED_LANGUAGES),
        },
        {
            "gate": "G1b",
            "metric": "sarcasm slice fix-rate (sarcasm_holdout)",
            "value": None,
            "n": {"holdout": len(holdout)},
            "note": (
                "not computable for a baseline: amendment 3.2 defines the slice by the"
                " zero-shot base LLM's errors and the fix-rate needs a fine-tune (Phase 4)."
            ),
        },
        {
            "gate": "G1c",
            "metric": "intents micro-F1 (comments_test)",
            "value": scorer.intents_micro_f1(
                gold(comments_test, "intents", unclear=None), intent_pred
            ),
            "n": {"overall": len(comments_test)},
        },
        {
            "gate": "G1d",
            "metric": "post_type macro-F1 (posts_test)",
            "value": scorer.launch_detection_macro_f1(
                gold(posts_test, "post_type"), post_type_pred
            ),
            "n": {"overall": len(posts_test), **Counter(row["post_type"] for row in posts_test)},
        },
        {
            "gate": "G1d",
            "metric": "relevance macro-F1 (posts_test)",
            "value": scorer.relevance_macro_f1(gold(posts_test, "relevant"), relevance_pred),
            "n": {
                "overall": len(posts_test),
                "relevant": sum(1 for row in posts_test if row["relevant"]),
            },
            "note": "second head of G1d; reported beside it and not gated (amendment 3.3)",
        },
        {
            "gate": "G1e",
            "metric": "brand extraction F1 (posts_test) — NOT COVERED",
            "value": None,
            "n": {
                "overall": len(posts_test),
                "gold_entities": sum(
                    len({scorer.normalise_brand(b, aliases) for b in row["brands"]})
                    for row in posts_test
                ),
            },
            "note": (
                "NOT COVERED BY THIS BASELINE, not scored badly: brand extraction is span"
                " extraction and this baseline is a sequence classifier — no token-classification"
                " head was trained for it. Read this cell as 'not attempted'. The G1e anchor is"
                " the zero-shot base LLM (SPEC §5); TF-IDF's watchlist matcher is the other"
                " reported number."
            ),
        },
    ]
    diagnostics = {
        "sarcasm_binary_macro_f1_comments_test": scorer.macro_f1(
            gold(comments_test, "sarcasm"), sarcasm_pred
        ),
        "holdout_sentiment_macro_f1": holdout_sentiment_f1,
        "holdout_sentiment_errors": len(base_errors),
        "holdout_sarcasm_detected": sum(1 for flag in holdout_sarcasm if flag),
        "wall_clock_minutes": round(wall_minutes, 2),
        "projected_minutes": round(projected, 2),
        "gate_coverage": {
            "G1a": "covered",
            "G1b": "not computable for a baseline (amendment 3.2 + needs a fine-tune)",
            "G1c": "covered",
            "G1d": "covered (post_type gated, relevance reported)",
            "G1e": "NOT COVERED — span extraction, no token-classification head trained",
        },
        "note": (
            "diagnostics, not gates. The holdout error count is this baseline's error set,"
            " NOT the G1b slice — amendment 3.2 defines that one by the zero-shot base LLM."
            " 107 of 108 holdout rows are negative, so a model trained on a sarcasm-enriched"
            " pool scores well there by leaning negative rather than by reading irony."
        ),
    }

    record = {
        "model": "xlm-roberta-base",
        "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
        "git": git_state(),
        "config": {
            "seed": SEED,
            "base_model": MODEL,
            "device": device,
            "epochs": EPOCHS,
            "batch_size": BATCH_SIZE,
            "learning_rate": LEARNING_RATE,
            "max_length": MAX_LENGTH,
            "warmup_share": WARMUP_SHARE,
            "class_weights": "inverse frequency per head",
            "frozen_parameters": "word embeddings (192M of 278M) — fits a 9 GB MPS allocator",
            "heads": {
                "T1": "sentiment 3-class · sarcasm binary · intents 5x binary",
                "T2": "relevance binary · post_type 3-class · brands NOT MODELLED",
            },
            "train_sources": {
                "data/frozen/comments_train.jsonl": len(scoreable(comments_train)),
                "data/annotation/sarcasm_candidates.jsonl": len(scoreable(mined)),
                "data/frozen/posts_train.jsonl": len(t2_train),
            },
            "train_note": (
                "real sources only — synthetic_sarcasm.jsonl is ablation-gated for Phase 4 and"
                " was not read. Nine independent fine-tunes, one per head, mirroring the TF-IDF"
                " baseline; no shared encoder."
            ),
            "determinism_note": (
                "seeded, but Apple MPS does not guarantee bitwise-reproducible kernels;"
                " a re-run may differ in the last decimals."
            ),
        },
        "gates": gates,
        "diagnostics": diagnostics,
    }
    append(record)
    print(f"\nwrote {RESULTS.relative_to(REPO_ROOT)} — read it with scripts/show_results.py")
    code = [p for p in record["git"]["dirty"] if p.startswith(("src/", "scripts/", "config/"))]
    if code:
        print(
            f"WARNING: uncommitted code — {record['git']['commit'][:9]} does not reproduce: {code}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
