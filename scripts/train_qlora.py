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

The two ablation arms differ by exactly one data path — `--with-plast` adds
`uplabel_precheck_45g2.jsonl` and nothing else, and the assertion that says so is
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

from market_pulse import local_llm, parents, prompts, records, scorer  # noqa: E402

FROZEN = REPO_ROOT / "data" / "frozen"
ANNOTATION = REPO_ROOT / "data" / "annotation"
RESULTS = REPO_ROOT / "results" / "baselines.json"
CONFIG = REPO_ROOT / "config" / "qlora.yaml"

TESTSET_VERSION = "v4"
"""Which frozen test set this training run is aimed at, and therefore which prompt
revision it renders (`prompts.REVISIONS`).

Not a flag. Train/eval format identity is the invariant this script exists to hold, and a
run that could be pointed at one rendering while the gate scored another would hold it by
convention. The version is written into the provenance and `eval_zero_shot.arm_preflight`
refuses an adapter whose rendering is not the one it is scoring through."""

SOURCES = {
    "T1": (FROZEN / "comments_train_tax2.jsonl", ANNOTATION / "sarcasm_candidates_tax2.jsonl"),
    "T2": (FROZEN / "posts_train.jsonl",),
}
"""SPEC amendment 3.9 (1): the taxonomy-v2 siblings, not the v1 files they were staged
beside. The v1 pair holds ZERO `service` rows while the gate scores against a test set
that is taxonomy v2 — an arm trained on them would be the only arm never shown the class
it is graded on, and the selection rule would measure taxonomy exposure and record it as
data volume (`results/precheck_45h.json`). The siblings hold the same 906 + 540 scoreable
rows, so no projected hour moves. `posts_train.jsonl` stays: posts carry no intents."""

PLAST = ANNOTATION / "uplabel_precheck_45g2.jsonl"
"""The ablation's one variable: the 1,912 up-labelled rows (v2 labels plus the operator's
verdicts) that 4.5h2 exists to price. It replaces `synthetic_sarcasm.jsonl`, which 4c's
own selection rule dropped (`knowledge/decisions/phase4-gate-verdict.md`) — keeping the
flag would offer a third arm no gate may run."""

ARM = {False: "without-plast", True: "with-plast"}
"""Distinct from 4c's `real-only` / `with-synthetic`: `records.arm_record` refuses two rows
for one arm name, and both phases append to the same results file."""

NEVER_READ = (
    FROZEN / "comments_test.jsonl",
    FROZEN / "comments_test_v3.jsonl",
    FROZEN / "comments_test_v4.jsonl",
    FROZEN / "posts_test.jsonl",
    FROZEN / "posts_test_v3.jsonl",
    FROZEN / "posts_test_v4.jsonl",
    FROZEN / "sarcasm_holdout.jsonl",
    FROZEN / "sarcasm_holdout_v3.jsonl",
    FROZEN / "sarcasm_holdout_v4.jsonl",
    ANNOTATION / "sarcasm_holdout_pool.jsonl",
    ANNOTATION / "sarcasm_holdout_pool_v4.jsonl",
)
"""The files no training run may open, named one by one rather than by folder.

`docs/PROMPT-4b.md` says "never read `data/frozen/*`" and in the same breath
names `comments_train.jsonl` and `posts_train.jsonl` as the training sources —
and both of those live in `data/frozen/`. The rule the sentence means is the
one enforced here: the frozen *test* sets and the holdout, plus the holdout pool
whose non-sarcastic rows share threads with the holdout. A folder rule would
either forbid the training data or, written loosely, permit the test sets.

Every version of each, because a list that names only v2 is a guard that stopped covering
the test set the moment v3 was frozen beside it."""

SFT_RECORD = REPO_ROOT / "results" / "pass1_sft.json"
"""The pass-1 datasets' own registration — `scripts/build_pass1_sft.py` writes it.

A training run reads a dataset by path, and a path is not an identity: the file at it can be
rebuilt, re-rendered or hand-edited between the registration and the pod. This record is what says
which bytes were registered, and :func:`build_pass1` refuses a dataset whose sha it does not name.
"""

PASS1_K = 5
"""The taxonomy's size — the four readings of `prompts.PASS1_SUBJECT_TYPES` plus `null`.

Not `len(the classes present)`: a dataset that happens to hold four of the five would silently
change every weight if K followed it, and the formula is pre-registered
(docs/PROMPT-lora-b.md D1)."""

PASS1_WEIGHT_CAP = 8.0
"""The cap on `w_c = N / (K · n_c)`. Uncapped, a class with two rows in six hundred asks for a
weight of 65 and the epoch becomes a loop over those two rows; the cap is what keeps a weighted
epoch an epoch of the dataset."""

SUPERVISED_SEPARATOR = ","
"""The one character the supervised head runs PAST the `subject_type` value — D3a's boundary.

`scripts/build_pass1_sft.py` writes it (its own `SEPARATOR`) and this reads it back, so the two
have to agree; `tests/test_train_qlora_pass1.py` asserts that they do rather than importing the
builder onto the pod, where it would drag a Mac-side dependency into the training process."""


def class_weights(rows: list[dict], k: int = PASS1_K, cap: float = PASS1_WEIGHT_CAP) -> dict:
    """`w_c = N / (K · n_c)`, capped — computed on the arm's OWN dataset.

    One implementation, called by both ends: the trainer samples with it and
    `scripts/build_pass1_sft.py` publishes it into the record the registration quotes. A second
    copy of a formula is a second answer the day one of them is edited.
    """
    counts: dict[str, int] = {}
    for row in rows:
        name = "null" if row.get("subject_type") is None else str(row["subject_type"])
        counts[name] = counts.get(name, 0) + 1
    total = sum(counts.values())
    return {name: round(min(total / (k * n), cap), 6) for name, n in sorted(counts.items())}


def sampling_order(count: int, weights: list[float] | None, seed: int) -> list[int]:
    """The row order of one epoch: a shuffle, or `count` weighted draws WITH replacement.

    The draw count is the dataset's own size in both branches, which is what keeps
    `steps_per_epoch = ceil(n / effective_batch)` true — and therefore keeps the registered step
    count, the projected seconds and the cap arithmetic true. A sampler that oversampled to balance
    the classes would silently lengthen the run it was registered under.
    """
    stream = random.Random(seed)
    if weights is None:
        order = list(range(count))
        stream.shuffle(order)
        return order
    return stream.choices(range(count), weights=weights, k=count)


def load_sft(path: Path) -> list[dict]:
    """A pre-rendered pass-1 dataset, with every target read back by the eval path's own parser.

    The phase-4 half of this file asserts format identity by re-parsing what it serialized; this
    asserts the same thing about a file it did not write, plus the property the masking rests on:
    the supervised head is EXACTLY the label and the one separator character that closes it. A
    `learn_chars` that stops short of the value supervises nothing and goes green; one that runs
    past the separator starts teaching the two fields the team lead never labelled, and both are
    silent failures on a billed pod. The old check asked only that the head END at the label, which
    was satisfied by every boundary at or before it — the D3a boundary moved one character and a
    guard that could not see the move is a guard that fails green ([[a_moved_constant_fails_green]]).
    """
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    if not rows:
        raise SystemExit(f"{path}: no rows")
    for row in rows:
        missing = {"id", "msg_id", "prompt", "target", "learn_chars", "subject_type", "task"} - set(
            row
        )
        if missing:
            raise SystemExit(f"{row.get('id', '?')}: the row has no {sorted(missing)}")
        if row["task"] != prompts.PASS1_TASK:
            raise SystemExit(f"{row['id']}: task {row['task']!r} is not {prompts.PASS1_TASK!r}")
        parsed = prompts.parse_pass1(row["target"], msg_id=int(row["msg_id"]))
        if parsed["subject_type"] != row["subject_type"]:
            raise SystemExit(f"{row['id']}: the parser reads {parsed['subject_type']!r} back")
        head = row["target"][: int(row["learn_chars"])]
        label = "null" if row["subject_type"] is None else f'"{row["subject_type"]}"'
        want = f"{label}{SUPERVISED_SEPARATOR}"
        if not 0 < int(row["learn_chars"]) < len(row["target"]) or not head.endswith(want):
            raise SystemExit(
                f"{row['id']}: the supervised head {head!r} does not end at {want!r}. A learn_chars"
                " that stops short of the value trains on nothing and reports green; one past the"
                " separator supervises fields nobody labelled."
            )
    ids = [row["id"] for row in rows]
    if len(set(ids)) != len(ids):
        raise SystemExit(f"{path}: {len(ids) - len(set(ids))} rows share an id")
    return rows


def build_pass1(config: dict, path: Path, weighted: bool) -> tuple[dict, dict]:
    """The dataset this run trains on, held to the record that registered it.

    No carve: the carve is phase 4's convergence thermometer, drawn from a pool this run does not
    have, and 24 rows held out of 464 would be 24 labels bought and not trained on.
    """
    rows = load_sft(path)
    record = json.loads(SFT_RECORD.read_text(encoding="utf-8"))
    named = {
        block["file"]: block
        for block in record["datasets"].values()
        if block["sha256"] == sha256(path.read_bytes()).hexdigest()
    }
    if not named:
        raise SystemExit(
            f"{path} hashes {sha256(path.read_bytes()).hexdigest()[:16]}… and"
            f" {SFT_RECORD.name} registers"
            f" {sorted(block['sha256'][:16] for block in record['datasets'].values())} — this is"
            " not a registered dataset. Stop rather than train on bytes nobody pre-registered."
        )
    arm = next(name for name, block in record["datasets"].items() if block["file"] in named)
    if record["instruments"]["prompt_sha256"] != {
        prompts.PASS1_TASK: prompts.prompt_sha256(prompts.PASS1_TASK)
    }:
        raise SystemExit(
            "the pass-1 prompt on this checkout is not the one the datasets were rendered under —"
            " a fine-tune trained on a prompt that moved is trained for another task"
        )
    weights = class_weights(rows)
    provenance = {
        "arm": arm,
        "dataset": {
            "file": record["datasets"][arm]["file"],
            "rows": len(rows),
            "sha256": record["datasets"][arm]["sha256"],
        },
        "sft_record": {
            "file": "results/pass1_sft.json",
            "sha256": sha256(SFT_RECORD.read_bytes()).hexdigest(),
        },
        "labelled_by": "the TEAM LEAD — results/labels_pass1_r*_provenance.json",
        "class_weights": weights if weighted else None,
        "sampler": (
            f"weighted with replacement, {len(rows)} draws per epoch, w_c = N/({PASS1_K}·n_c)"
            f" capped at {PASS1_WEIGHT_CAP}"
            if weighted
            else "uniform shuffle — the default, unchanged"
        ),
        "supervision": record["supervision"],
        "n_train": len(rows),
        "n_carve": 0,
        "train_sha256": content_hash(rows),
        "task": prompts.PASS1_TASK,
        "prompt_sha256": {prompts.PASS1_TASK: prompts.prompt_sha256(prompts.PASS1_TASK)},
        "quantization": local_llm.QUANTIZATION,
        "chat_template": local_llm.CHAT_TEMPLATE,
        "config": config,
    }
    return {"train": rows, "carve": [], "kind": "pass1", "weighted": weighted}, provenance


RAW_POSTS = REPO_ROOT / "data" / "raw" / "posts"
CAPTIONS = ANNOTATION / "post_captions.jsonl"
_POSTS: dict | None = None


def post_index() -> tuple[dict, dict]:
    """The parent-post index and the 4.5g2 captions, loaded once per process."""
    global _POSTS
    if _POSTS is None:
        _POSTS = (parents.load(RAW_POSTS), parents.load_captions(CAPTIONS))
    return _POSTS


def rendering(task: str) -> str:
    """Which registered prompt this run renders a task through — one lookup, one answer."""
    return prompts.REVISIONS[TESTSET_VERSION][task]


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
    """Scoreable rows of one file as training examples, each with what it renders through.

    ``unclear`` rows are dropped. The assumption, stated because the brief asks
    for it: a row the annotator could not decide has no right answer to teach,
    and SPEC §4 already excludes it from every gate — training on it would put a
    label into the model that the scorer refuses to score. It is a large drop
    (694 of 1 600 comments, 206 of 746 candidates) and the counts are printed.
    """
    with_post = rendering(task) in prompts.WITH_POST
    posts, captions = post_index() if with_post else ({}, {})
    return [
        {
            "task": task,
            "id": row["id"],
            "source": path.name,
            "text": row["text"],
            # Stored on the example rather than resolved at render time, so `content_hash`
            # covers the post the model actually sees: two runs whose raw store differed
            # would otherwise share a dataset hash and train on different requests.
            "post": parents.post_kwargs(parents.context(posts, captions, row))
            if with_post
            else None,
            "target": answer(task, row),
        }
        for row in load(path)
        if not row["unclear"]
    ]


def order(example: dict) -> tuple[str, str]:
    return example["task"], example["id"]


def assemble(with_plast: bool, carve_rows: int, seed: int) -> dict:
    """The training set and the carve, both deterministic.

    The carve is drawn from the REAL pool before the пласт joins, so both arms hold out the
    same rows and still differ by exactly the пласт's ids — the pairing discipline of
    amendment 3.4 (3), restated in 3.9 (2) because a пласт entering as a *source* would be
    drawn from and the two arms would hold out different rows.
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
    if with_plast:
        train += examples("T1", PLAST)
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
        parsed = prompts.parse_reply(rendering(row["task"]), row["target"])
        if json.dumps(parsed, ensure_ascii=False, sort_keys=True) != json.dumps(
            json.loads(row["target"]), ensure_ascii=False, sort_keys=True
        ):
            raise SystemExit(f"{row['id']}: the parser does not read this target back: {parsed}")


def assert_arm_identity(without: list[dict], with_plast: list[dict]) -> list[str]:
    """The two arms differ by exactly the пласт's rows, in both directions."""
    base_ids = {order(row) for row in without}
    other_ids = {order(row) for row in with_plast}
    added = other_ids - base_ids
    removed = base_ids - other_ids
    expected = {order(row) for row in examples("T1", PLAST)}
    if removed or added != expected:
        raise SystemExit(
            f"the arms differ by more than the пласт: {len(added)} added,"
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
        "added_source": PLAST.name if arm == ARM[True] else None,
        "added_ids": len(ids),
        "testset_version": TESTSET_VERSION,
        "prompt_revision": prompts.REVISIONS[TESTSET_VERSION],
        "prompt_revision_sha256": prompts.revision_sha256(TESTSET_VERSION),
        "prompt_sha256": {task: prompts.prompt_sha256(task) for task in prompts.TASKS},
        "quantization": local_llm.QUANTIZATION,
        "chat_template": local_llm.CHAT_TEMPLATE,
        "config": config,
    }


def build(config: dict, with_plast: bool) -> tuple[dict, dict]:
    """Both arms, asserted against each other, and the one this run trains on."""
    training = config["training"]
    real = assemble(False, training["carve_rows"], training["seed"])
    other = assemble(True, training["carve_rows"], training["seed"])
    added = assert_arm_identity(real["train"], other["train"])
    built = other if with_plast else real
    assert_format_identity(built["train"] + built["carve"])
    history = json.loads(RESULTS.read_text(encoding="utf-8"))
    try:
        records.assert_prompt_sha(
            records.prompt_sha_history(history, local_llm.MODEL_ID), local_llm.MODEL_ID
        )
    except ValueError as err:
        raise SystemExit(str(err)) from None
    return built, provenance(config, ARM[with_plast], built, added)


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
    messages = prompts.build_messages(
        rendering(example["task"]), example["text"], **(example["post"] or {})
    )
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


def text_tokenizer(loaded):
    """The thing that turns text into ids, whether `loaded` is a tokenizer or the processor.

    pass 1 trains through `local_llm.load_captioner` — the PROCESSOR — because that is what the
    eval path builds its client on, and the chat template a processor applies is not guaranteed to
    be the one its inner tokenizer would. Train/eval format identity is held by construction here
    rather than by an assertion after the fact.
    """
    return getattr(loaded, "tokenizer", loaded)


def pad_id_of(loaded) -> int:
    inner = text_tokenizer(loaded)
    return inner.pad_token_id if inner.pad_token_id is not None else inner.eos_token_id


def encode_pass1(loaded, example: dict, max_seq_len: int) -> dict:
    """One pre-rendered pass-1 request as ids, with the prompt AND the unlabelled tail masked.

    The team lead labelled `subject_type`. The answer the parser demands carries `subject_id` and
    `stance` beside it, and there is no gold for either — so they are written and NOT supervised.
    The cut is made on CHARACTER offsets and not by tokenizing the head separately: a merge across
    the boundary would move the cut by a token and nothing would say so. Any token that reaches
    past the boundary is masked, which errs toward supervising less.

    Nothing appends an end-of-turn marker. The transport stops at the first balanced object
    (`reader_v5.balanced_prefix`, installed by the pod runner), so the stop is the harness's and
    not a token this run has to teach — and teaching it would mean supervising the masked tail.
    """
    prompt = loaded.apply_chat_template(
        [{"role": "user", "content": example["prompt"]}],
        tokenize=False,
        **local_llm.CHAT_TEMPLATE,
    )
    tokenizer = text_tokenizer(loaded)
    context = tokenizer(prompt, add_special_tokens=False)["input_ids"]
    encoded = tokenizer(example["target"], add_special_tokens=False, return_offsets_mapping=True)
    offsets = encoded.get("offset_mapping")
    if not offsets:
        raise SystemExit(
            "this tokenizer returns no offset mapping, so the supervised span cannot be located"
            " without re-tokenizing the head and hoping the merges agree. Stop and report."
        )
    learn = int(example["learn_chars"])
    target = encoded["input_ids"]
    labels = [token if end <= learn else -100 for token, (_, end) in zip(target, offsets)]
    if all(label == -100 for label in labels):
        raise SystemExit(f"{example['id']}: every target token is masked — nothing would train")
    if len(context) + len(target) > max_seq_len:
        raise SystemExit(
            f"{example['id']} needs {len(context) + len(target)} tokens against a max_seq_len of"
            f" {max_seq_len}. config/qlora.yaml is frozen law — the dataset builder bounds every"
            " row before it ships, so a row arriving here means the bound and the tokenizer have"
            " parted. Stop and report."
        )
    return {"input_ids": context + target, "labels": [-100] * len(context) + labels}


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


def load_for_training(config: dict, resume: Path | None = None, pass1: bool = False):
    """The NF4 base of `local_llm`, prepared for k-bit training, plus adapters.

    `pass1` loads through :func:`local_llm.load_captioner` — the PROCESSOR the eval path builds its
    client on — so a training example is rendered through the same chat template the gate is
    answered through, by construction and not by an assertion made afterwards. Same weights, same
    pinned revision, same NF4 dict; what differs is which object applies the template.
    """
    from peft import LoraConfig, PeftModel, get_peft_model, prepare_model_for_kbit_training

    load = local_llm.load_captioner if pass1 else local_llm.load
    tokenizer, model = load(revision=config["base"]["revision"], seed=config["training"]["seed"])
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
    pass1 = built.get("kind") == "pass1"
    tokenizer, model = load_for_training(config, resume, pass1=pass1)
    encode_row = encode_pass1 if pass1 else encode
    encoded = [encode_row(tokenizer, row, settings["max_seq_len"]) for row in built["train"]]
    pad = pad_id_of(tokenizer)
    carve = [
        collate([encode_row(tokenizer, row, settings["max_seq_len"])], pad, model.device)
        for row in built["carve"]
    ]
    # One weight per ROW, resolved from the per-class table once: the sampler draws row indices and
    # a table lookup inside the epoch loop would recompute the same dict every epoch.
    weights = None
    if built.get("weighted"):
        table = class_weights(built["train"])
        weights = [
            table["null" if row.get("subject_type") is None else row["subject_type"]]
            for row in built["train"]
        ]
        print(f"weighted sampling ON — {table}")

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
        rows = sampling_order(len(encoded), weights, settings["seed"] + epoch)
        index = start_index if epoch == start_epoch else 0
        seen = 0
        while index < len(rows) and step < total:
            chunk = [encoded[i] for i in rows[index : index + micro]]
            try:
                loss = model(**collate(chunk, pad, model.device)).loss
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
                if carve and (step % settings["carve_every"] == 0 or step == total):
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
        task = rendering(row["task"])
        reply = client.batch(task, [row["text"]], [row["post"]] if row["post"] else None)[0]
        try:
            parsed[row["id"]] = prompts.parse_reply(task, reply["content"])
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
    parser.add_argument("--with-plast", action="store_true", help="the ablation's second arm")
    parser.add_argument("--build-only", action="store_true", help="assemble and assert; no GPU")
    parser.add_argument("--out", type=Path, help="run directory: adapter, loss curve, provenance")
    parser.add_argument("--max-steps", type=int, help="stop after N optimizer steps (smoke)")
    parser.add_argument("--resume-from", type=Path)
    parser.add_argument("--carve-eval", action="store_true", help="mechanics check after training")
    parser.add_argument("--data", type=Path, help="a pre-rendered pass-1 SFT dataset (lora-b D1)")
    parser.add_argument(
        "--class-weights",
        action="store_true",
        help="pass 1: sample each epoch by w_c = N/(K*n_c), capped. OFF by default",
    )
    args = parser.parse_args(argv)

    if args.data and args.with_plast:
        raise SystemExit(
            "--with-plast is phase 4's ablation and --data is pass 1's dataset: one run cannot be"
            " both arms of two experiments. Pick one."
        )
    if args.class_weights and not args.data:
        raise SystemExit(
            "--class-weights is the pass-1 sampler and needs the pass-1 dataset it weighs"
            " (--data). Phase 4's arms are not registered under a weighted sampler."
        )
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    built, record = (
        build_pass1(config, args.data, args.class_weights)
        if args.data
        else build(config, args.with_plast)
    )
    print(json.dumps({k: v for k, v in record.items() if k != "config"}, indent=2, sort_keys=True))
    if args.build_only:
        return 0
    if not args.out:
        raise SystemExit("--out is required for a training run")

    if args.carve_eval and not built["carve"]:
        raise SystemExit(
            "--carve-eval runs the local eval path over the carve, and a pass-1 dataset has none:"
            " every labelled row is trained on. Ask for the mechanics check another way."
        )
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
