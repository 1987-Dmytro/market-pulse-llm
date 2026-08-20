#!/usr/bin/env python3
"""The pass-1 SFT datasets — one prompt→target pair per labelled comment, for arms A and B.

**What this builds.** `docs/PROMPT-lora-b.md` D1: arm A is r1's 500 labelled units, arm B is r1 and
r2's 650. Each row is the request the TRANSPORT sends — `prompts.pass1_messages_gm4` under the
frozen `PASS1_TASK`, whose sha is on the may-not-move list — and the answer the team lead's label
makes, serialized in the schema `prompts.parse_pass1` reads back. Every target here goes through
that parser before it ships. Nothing is trained, nothing is spent and no cloud call is made.

**The supervised span, and why it is not the whole target.** The team lead labelled ONE field:
`subject_type`. The answer the parser demands has four — `msg_id`, `subject_type`, `subject_id`,
`stance` — so the other two have to appear in the string and there is no gold for them. Filling
them with `null` and training on it teaches «stance is always null», and that is not a preference,
it is disqualifying: of the fourteen sealed gold rows the bar is scored on, THREE score `stance`
against a non-null gold value (21626, 21629, 580124), so with stance ≡ null not one of them can
agree whatever it answers about the subject. The reachable maximum is then 11 of 14 against a
threshold of 12 — the gate would be unreachable before the pod is created. So each row carries `learn_chars`: the
target is written whole, and only its head — through the `subject_type` value and the one separator
character that closes it — is supervised. The tail is context the model conditions on and is never
scored ([[an_absolute_bar_needs_a_reachability_state]]). The separator is D3a's tightening and its
reason is in :func:`target_for`: the mask is applied on token END offsets, so a boundary that
stopped ON the value let a `",` merge straddle out and erode the tail of the one field the gate
scores.

**The context these prompts can carry, and what that costs.** A pass-1 request holds the thread's
`<topic>` and its `<entities>`, both of which come from a reader verdict that has been PAID FOR. 15
of the 120 labelled threads have one. For the rest this renders the topic from the store's own post
text and the entity block empty — which the prompt has an explicit rendering for — and the census
block records exactly how many rows are in which state, because 12 of the 14 gate rows carry a real
entity block and a training set that mostly does not is a difference between train and eval that
belongs in the registration and not in a footnote ([[build_the_training_prompt_with_the_inference_call]]).

**Length, and the operator's branch-C ruling.** `config/qlora.yaml` is frozen law and its
`max_seq_len` is 1408. A row over it is a `SystemExit` inside the training loop, on a billed pod,
so every row is bounded HERE at the worst tokens-per-character ratio measured over probe-b's own 64
paid rows, and anything that still does not fit is dropped by name into the record rather than
discovered at $0.80/h.

The first build dropped 43 rows — one of them the second of the labelled set's two `молочный_бренд`
rows — and the cause was the substitute itself: a bought topic is a summary of 26–147 characters
and a raw post runs to thousands. The operator's ruling of 2026-08-19 takes branch C: a substituted
topic is CUT to the envelope a bought one occupies, at a word boundary, with an ellipsis where
something was removed. The envelope is measured from the bought summaries at every run
(:func:`envelope`) and never typed. It closes the length finding — nothing is dropped and both
brand rows survive — and it closes nothing else: the entity block is still empty wherever no
verdict was bought, and the census below still prints that against the gate's own rows.

    PYTHONPATH=src python3.11 scripts/build_pass1_sft.py --census   # measure, write nothing
    PYTHONPATH=src python3.11 scripts/build_pass1_sft.py
    PYTHONPATH=src python3.11 scripts/build_pass1_sft.py --outdir /tmp/again   # the pair
"""

import argparse
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_pass1_label_pack_r2 as r2pack  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

import yaml  # noqa: E402

from market_pulse import prompts  # noqa: E402

PACKS = {
    "r1": REPO_ROOT / "results" / "pass1_label_pack_r1.json",
    "r2": REPO_ROOT / "results" / "pass1_label_pack_r2.json",
}
LABELS = {
    "r1": REPO_ROOT / "results" / "labels_pass1_r1.jsonl",
    "r2": REPO_ROOT / "results" / "labels_pass1_r2.jsonl",
}
"""The FROZEN copies under results/, never the docs/ originals: training reads a frozen path, and
the two are asserted byte-identical by the seal tests that ship with each of them."""

PROVENANCE = {
    "r1": REPO_ROOT / "results" / "labels_pass1_r1_provenance.json",
    "r2": REPO_ROOT / "results" / "labels_pass1_r2_provenance.json",
}
V5B = REPO_ROOT / "results" / "reader_v5b_w1.jsonl"
TOPUP = REPO_ROOT / "results" / "reader_topup_w1.jsonl"
V4 = REPO_ROOT / "results" / "reader_v4_w1.jsonl"
PROBE_PACK = REPO_ROOT / "results" / "pass1_probe_b_pack.json"
PROBE_ROWS = REPO_ROOT / "results" / "pass1_probe_b_rows.jsonl"
GOLD = REPO_ROOT / "results" / "reader_gold_w1_r2.json"
QLORA = REPO_ROOT / "config" / "qlora.yaml"
HOLDOUT = REPO_ROOT / "results" / "pass1_holdout_100.json"
"""The hundred evaluation-only rows of `docs/PROMPT-pass1-fewshot.md` D0.1 — never trained on."""

ARMS = {"a": ("r1",), "b": ("r1", "r2")}
"""Arm A is r1 alone; arm B is r1 plus the r2 top-up. Arm A's rows are a SUBSET of arm B's, which
is what makes the ablation «does more data of the same population help» and not two experiments."""

RECORD_NAME = "results/pass1_sft.json"
ARM_NAMES = {"a": "results/pass1_sft_arm_a.jsonl", "b": "results/pass1_sft_arm_b.jsonl"}

SMOKE_NAME = "results/lora_b_smoke_pack.json"
"""The format smoke's pack — ONE training request, and never a gold or eval-pack row.

D3a rung 5: before an arm is evaluated, one TRAINING-set prompt goes through its adapter and the
reply has to parse as one balanced four-key object. Head-only supervision can in principle un-teach
the four-key shape, and this is what makes that a cheap KILL instead of an invisible zero at the
bar. It is a transport-format check and NOT a bar peek — the row is outside both the sealed
fourteen and the eval pack's sixty-four, and this file asserts it."""

SEPARATOR = ","
"""The one character `learn_chars` reaches PAST the `subject_type` value — the D3a tightening. It
is the schema's own field separator, so it carries no label and teaches nothing but structure."""

TEMPLATE_SLACK = 16
"""Tokens of margin over the measured bound, for the chat template the pod wraps each prompt in.

The measured ratio already carries that wrapper — it is tokens of the WHOLE served prompt over
characters of the rendered content — so this is margin on top of a bound that is already
conservative. It costs a handful of rows and it buys the difference between a row dropped here and
a `SystemExit` at $0.80/h."""


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in summary.read_text_or_refuse(path).splitlines() if line]


def verdicts() -> dict[str, tuple[str, dict]]:
    """Per thread, the BOUGHT reader verdict its topic and entity block come from, and its file.

    v5b first because it is the latest reading, v4 behind it — the precedence
    `scripts/write_pass1_prereg.py::entity_context` fixed when it built the probe pack's own
    context, restated by nobody: the same two files in the same order. The branch-B top-up sits
    between them and is DISJOINT from both by construction — it read exactly the threads that had
    no verdict — so its position is a statement of intent and not a tie-break that decides anything.

    The top-up file is read WHEN it exists. That is not an absence test wearing a different hat: a
    producer whose optional input is missing has to render something, and what it renders — the
    bounded post text — is the state the record already publishes. Which sources were read, and how
    many verdicts each one supplied, goes into the record so the rendering can be traced to them.
    """
    found: dict[str, tuple[str, dict]] = {}
    for path in (V5B, TOPUP, V4):
        if not path.exists():
            continue
        for row in jsonl(path):
            key = f"{row.get('channel')}:{row.get('post_id')}"
            if row.get("parsed") and key not in found:
                found[key] = (summary.rel(path), row["parsed"])
    return found


def verdict_sources() -> list[dict]:
    """Which reader evidence files the rendering read, and what each one supplied."""
    found = verdicts()
    out = []
    for path in (V5B, TOPUP, V4):
        name = summary.rel(path)
        used = sum(1 for source, _ in found.values() if source == name)
        out.append(
            {
                "record": name,
                "exists": path.exists(),
                "sha256": summary.sha256_of(path) if path.exists() else None,
                "threads_it_supplied": used,
            }
        )
    return out


def labelled_units() -> list[dict]:
    """Every labelled unit of both packs, joined to its label and to its comment in the store.

    The join is on `(thread, msg_id)` and it is total in both directions: a label with no unit or a
    unit with no label is a stop, not a filtered row.
    """
    threads = r2pack.raw_threads()
    exam = set(r2pack.excluded_threads(json.loads(summary.read_text_or_refuse(PACKS["r1"]))))
    gold = set(r2pack.gold_msg_ids())
    out = []
    for name, path in LABELS.items():
        pack = json.loads(summary.read_text_or_refuse(PACKS[name]))
        units = {(one["thread"], int(one["msg_id"])) for one in pack["units"]}
        rows = jsonl(path)
        answered = {(one["thread"], int(one["msg_id"])): one for one in rows}
        if set(answered) != units or len(rows) != len(units):
            raise SystemExit(
                f"{summary.rel(path)} answers {len(rows)} rows against {len(units)} drawn units of"
                f" {summary.rel(PACKS[name])} — the labels and the pack have parted. Stop."
            )
        for (thread, msg_id), row in sorted(answered.items()):
            if thread in exam:
                raise SystemExit(f"{thread}:{msg_id} sits in an EXAM thread — stop and report.")
            if msg_id in gold:
                raise SystemExit(f"{msg_id} is a GOLD row and may not be trained on — stop.")
            store = threads[thread]
            comment = next((one for one in store["comments"] if int(one["msg_id"]) == msg_id), None)
            if comment is None:
                raise SystemExit(f"{thread}:{msg_id} is not in the store's thread — stop.")
            out.append(
                {
                    "pack": name,
                    "thread": thread,
                    "msg_id": msg_id,
                    "subject_type": row.get("subject_type"),
                    "text": summary.comment_text(comment),
                    "store": store,
                }
            )
    return out


def target_for(msg_id: int, subject_type: str | None) -> tuple[str, int]:
    """The answer string and how much of it is SUPERVISED.

    Field order is the prompt's own schema order. `subject_id` and `stance` are written `null` —
    they have to be something, the parser demands all four keys — and `learn_chars` stops the loss
    before them, so nothing here teaches the model what a stance is.

    **The boundary runs one character PAST the value's closing delimiter, and that +1 is the whole
    of the D3a tightening.** `scripts/train_qlora.py` masks on token END offsets — a token that
    reaches past `learn_chars` is dropped from the loss — so where the tokenizer merges the value's
    closing `"` with the `,` that follows it (`",`, and on some merges the value's last character
    with them), that token ENDS at `learn_chars + 1` and the whole merge falls out of supervision.
    The erosion lands on the tail of `subject_type`, which is the one field the gate scores. Taking
    the boundary through the separator makes the merged token end exactly ON it, so it is supervised
    whole; a token reaching past the separator is still masked, so the two unlabelled fields are as
    untaught as they were. The separator itself is structure the parser demands and carries no
    label ([[the_guard_hashes_the_half_that_cannot_move]]).
    """
    head = json.dumps(
        {"msg_id": msg_id, "subject_type": subject_type}, ensure_ascii=False, sort_keys=False
    )
    learned = head[:-1]  # everything up to, but not including, the object's closing brace
    target = learned + ', "subject_id": null, "stance": null}'
    parsed = prompts.parse_pass1(target, msg_id=msg_id)
    if parsed["subject_type"] != subject_type or parsed["msg_id"] != msg_id:
        raise SystemExit(f"{msg_id}: the parser does not read this target back — {parsed}")
    if target[len(learned)] != SEPARATOR:
        raise SystemExit(
            f"{msg_id}: the character after the supervised value is {target[len(learned)]!r} and"
            f" not {SEPARATOR!r}. The +1 boundary assumes the separator sits there — stop."
        )
    return target, len(learned) + 1


def ratio() -> dict:
    """The worst tokens-per-character this prompt family has actually shown, and where.

    Measured over probe-b's own 64 paid rows: the pack's `rendered_chars` against the usage block's
    `prompt_tokens`, which counts the served prompt WITH its chat template. The maximum and not the
    mean — a mean bound would be right on average and wrong on the longest row, which is the only
    one that matters here ([[the_smokes_rate_carries_the_smokes_transport]]).
    """
    pack = json.loads(summary.read_text_or_refuse(PROBE_PACK))
    chars = {one["id"]: int(one["rendered_chars"]) for one in pack["items"]}
    pairs = []
    for row in jsonl(PROBE_ROWS):
        usage = row.get("usage") or {}
        if usage.get("prompt_tokens") and row["id"] in chars:
            pairs.append((int(usage["prompt_tokens"]) / chars[row["id"]], row["id"]))
    if len(pairs) < 60:
        raise SystemExit(
            f"only {len(pairs)} probe rows carry both a size and a usage block — stop."
        )
    worst, where = max(pairs)
    return {
        "tokens_per_char_max": round(worst, 6),
        "measured_on": where,
        "rows": len(pairs),
        "source": {"pack": summary.rel(PROBE_PACK), "evidence": summary.rel(PROBE_ROWS)},
        "rule": (
            "the maximum over probe-b's 64 paid rows of prompt_tokens / rendered_chars. The"
            " numerator counts the chat template the pod wraps the request in, so the bound is"
            " conservative by construction"
        ),
    }


def bound_tokens(prompt: str, target: str, per_char: float) -> int:
    return math.ceil((len(prompt) + len(target)) * per_char) + TEMPLATE_SLACK


def envelope(context: dict[str, tuple[str, dict]]) -> dict:
    """The character budget a substituted topic gets: the longest topic a BOUGHT one occupies.

    Measured at every run over the reader verdicts themselves, so the bound is a property of the
    population and not a number somebody liked. It is the eval's own envelope — every request the
    gate is answered under carries a topic inside it — which is the whole point of cutting to it
    rather than to a round number.
    """
    lengths = sorted(
        len((verdict.get("post_summary") or "").strip())
        for _, verdict in context.values()
        if (verdict.get("post_summary") or "").strip()
    )
    if not lengths:
        raise SystemExit(
            "no bought verdict carries a post_summary — there is no envelope to cut to"
        )
    return {
        "limit": lengths[-1],
        "measured_over": len(lengths),
        "shortest": lengths[0],
        "median": lengths[len(lengths) // 2],
        "rule": (
            "the longest post_summary any bought reader verdict carries. A substituted topic is cut"
            " to it at a word boundary, with an ellipsis where anything was removed; a bought topic"
            " is never cut, because it is already inside its own envelope"
        ),
    }


def bound_topic(text: str, limit: int) -> str:
    """A post's opening, cut to `limit` characters at a word boundary. Marked where it was cut.

    The ellipsis is deliberate. A cut advertisement presented whole is a claim that the topic ends
    there; the marker says the sentence continues and the model has seen that shape a million
    times. The word-boundary search gives up when the only whitespace sits in the first half —
    cutting a 147-character budget down to 20 to avoid splitting a word is the worse trade.
    """
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    head = text[:limit]
    boundary = max(head.rfind(one) for one in (" ", "\n", "\t"))
    kept = head[:boundary] if boundary > limit // 2 else head
    return kept.rstrip() + "…"


def request(unit: dict, context: dict[str, tuple[str, dict]], limit: int) -> dict:
    """The transport's own fields for one unit, and the request they render to.

    Split out of :func:`rendered` because the smoke pack needs the FIELDS — the pod re-renders each
    item from them and refuses unless its sha matches — while the SFT row needs the rendered string.
    One function producing both is what keeps the smoke's request the training request rather than
    a second spelling of it ([[build_the_training_prompt_with_the_inference_call]]).
    """
    store = unit["store"]
    source, verdict = context.get(unit["thread"], (None, {}))
    topic = (verdict.get("post_summary") or "").strip()
    topic_source = "reader verdict"
    if not topic:
        topic_source = "the store's post text, bounded"
        topic = bound_topic(store["post_text"] or "", limit)
    entities = verdict.get("entities") or []
    fields = {
        "id": f"{unit['thread']}#{unit['msg_id']}",
        "thread": unit["thread"],
        "channel": store["channel"],
        "post_id": int(store["post_id"]),
        "topic": topic,
        "entities": entities,
        "msg_id": unit["msg_id"],
        "text": unit["text"],
    }
    prompt = prompts.pass1_messages_gm4(
        fields["channel"],
        fields["post_id"],
        fields["topic"],
        fields["entities"],
        fields["msg_id"],
        fields["text"],
        task=prompts.PASS1_TASK,
    )[0]["content"]
    return {
        "fields": fields,
        "prompt": prompt,
        "topic_source": topic_source,
        "verdict_source": source,
    }


def rendered(unit: dict, context: dict[str, tuple[str, dict]], limit: int) -> dict:
    """One SFT row: the transport's own request, the team lead's answer, and where its context came
    from."""
    built = request(unit, context, limit)
    prompt, topic_source, source = built["prompt"], built["topic_source"], built["verdict_source"]
    entities = built["fields"]["entities"]
    topic = built["fields"]["topic"]
    target, learn_chars = target_for(unit["msg_id"], unit["subject_type"])
    return {
        "id": f"{unit['thread']}#{unit['msg_id']}",
        "thread": unit["thread"],
        "msg_id": unit["msg_id"],
        "pack": unit["pack"],
        "subject_type": unit["subject_type"],
        "task": prompts.PASS1_TASK,
        "prompt": prompt,
        "target": target,
        "learn_chars": learn_chars,
        "context": {
            "topic_from": topic_source,
            "topic_cut": topic.endswith("…"),
            "entities": len(entities),
            "verdict": source,
        },
    }


def smoke_pack(state: dict) -> dict:
    """The one-item pack rung 5 sends, built from the SAME request the training row was rendered
    from.

    The row is arm A's first, which makes it a training row of BOTH arms (A ⊂ B) and keeps the
    choice deterministic — a smoke that drew a different row on each run would be a different
    instrument each time. The pod re-renders the item from its fields and refuses unless the sha
    matches, so what is asserted here is the other half: that the fields render to the string the
    dataset trained on ([[the_fixture_and_the_artifact_share_anchors]]).

    `instruments` and `serving` are READ out of probe-b's own pack rather than retyped — the smoke
    has to be the same transport the eval is, and a second spelling of a serving block is a second
    configuration nobody diffed.
    """
    probe = json.loads(summary.read_text_or_refuse(PROBE_PACK))
    gold = json.loads(summary.read_text_or_refuse(GOLD))
    barred_ids = {int(row["msg_id"]) for row in gold["per_comment"]}
    barred_ids |= {int(one["msg_id"]) for one in probe["items"]}
    barred_keys = {one["id"] for one in probe["items"]}

    row = arm_rows(state, "a")[0]
    unit = next(one for one in state["units"] if f"{one['thread']}#{one['msg_id']}" == row["id"])
    if int(row["msg_id"]) in barred_ids or row["id"] in barred_keys:
        raise SystemExit(
            f"{row['id']} is a gold row or an eval-pack row. The smoke would then be a peek at the"
            " bar's own population and the attempt would be spent on it — stop and report."
        )
    built = request(unit, state["context"], state["envelope"]["limit"])
    if built["prompt"] != row["prompt"]:
        raise SystemExit(
            f"{row['id']}: the smoke item's fields render a request the dataset row does not carry."
            " The smoke would check a format the arm was never trained on — stop and report."
        )
    mine = {
        prompts.PASS1_TASK: prompts.prompt_sha256(prompts.PASS1_TASK),
    }
    if probe["instruments"]["prompt_sha256"] != mine:
        raise SystemExit(
            f"probe-b's pack pins {probe['instruments']['prompt_sha256']} and this checkout renders"
            f" {mine}. The smoke cannot borrow a serving block from a pack it does not agree with."
        )
    item = {
        **built["fields"],
        "leg": "smoke",
        "part": None,
        "payable_comments": 1,
        "rendered_chars": len(built["prompt"]),
        "rendering_sha256": sha_text(built["prompt"]),
    }
    return {
        "phase": "lora-b-smoke",
        "task": probe["task"],
        "instruments": probe["instruments"],
        "serving": probe["serving"],
        "items": [item],
        "registration": {"record": "results/prereg_lora_b.json"},
        "borrowed": {
            "results/pass1_probe_b_pack.json": summary.sha256_of(PROBE_PACK),
            "rule": "the instruments and the serving block are read out of the eval's own pack, so"
            " the smoke and the eval are one transport and not two",
        },
        "reading": (
            "ONE training request, chosen as arm A's first row and therefore a training row of both"
            " arms. It is in NEITHER the sealed fourteen nor the eval pack's sixty-four — asserted"
            " by the producer — so a reply to it is not an eval output and the one attempt is not"
            " spent by seeing it. The attempt is SPENT at the first GOLD-row reply generated"
        ),
    }


def measure() -> dict:
    """Everything the record needs, computed once: the rows, the bound, and what does not fit."""
    context = verdicts()
    per = ratio()
    budget = envelope(context)
    config = yaml.safe_load(QLORA.read_text(encoding="utf-8"))
    max_seq_len = int(config["training"]["max_seq_len"])
    units = labelled_units()
    rows, dropped = [], []
    for unit in units:
        row = rendered(unit, context, budget["limit"])
        row["bound_tokens"] = bound_tokens(row["prompt"], row["target"], per["tokens_per_char_max"])
        if row["bound_tokens"] > max_seq_len:
            dropped.append(row)
        else:
            rows.append(row)
    return {
        "context": context,
        "envelope": budget,
        "ratio": per,
        "max_seq_len": max_seq_len,
        "rows": rows,
        "dropped": dropped,
        "units": units,
    }


def arm_rows(state: dict, arm: str) -> list[dict]:
    packs = ARMS[arm]
    return [row for row in state["rows"] if row["pack"] in packs]


def distribution(rows: list[dict]) -> dict[str, int]:
    """Every value of the taxonomy, zeros included — an empty class is an answer."""
    counts = Counter("null" if row["subject_type"] is None else row["subject_type"] for row in rows)
    return {
        ("null" if value is None else value): counts.get("null" if value is None else value, 0)
        for value in (*prompts.PASS1_SUBJECT_TYPES, None)
    }


def sampler_weights(rows: list[dict], k: int = 5, cap: float = 8.0) -> dict[str, float]:
    """`w_c = N / (K · n_c)`, capped — the pre-registered formula of docs/PROMPT-lora-b.md D1.

    Computed on the arm's OWN dataset, so the two arms carry different weights by construction. A
    class with no rows has no weight rather than an infinite one: it cannot be sampled either way,
    and a division by zero here would be a crash in the one place the record is supposed to explain
    itself.
    """
    counts = {name: n for name, n in distribution(rows).items() if n}
    total = sum(counts.values())
    return {name: round(min(total / (k * n), cap), 6) for name, n in sorted(counts.items())}


def steps(n: int, config: dict) -> dict:
    training = config["training"]
    batch = int(training["micro_batch_size"]) * int(training["grad_accum"])
    per_epoch = -(-n // batch)
    return {
        "n": n,
        "effective_batch": batch,
        "steps_per_epoch": per_epoch,
        "epochs": int(training["epochs"]),
        "steps": per_epoch * int(training["epochs"]),
    }


def census(state: dict) -> dict:
    """What the two arms are made of, and the two states the registration has to know about."""
    config = yaml.safe_load(QLORA.read_text(encoding="utf-8"))
    gold = json.loads(summary.read_text_or_refuse(GOLD))
    probe = json.loads(summary.read_text_or_refuse(PROBE_PACK))
    gold_ids = {int(row["msg_id"]) for row in gold["per_comment"]}
    gold_items = [one for one in probe["items"] if int(one["msg_id"]) in gold_ids]

    def context_counts(rows: list[dict]) -> dict:
        return {
            "with_an_entity_block": sum(1 for row in rows if row["context"]["entities"]),
            "with_a_bought_topic": sum(
                1 for row in rows if row["context"]["topic_from"] == "reader verdict"
            ),
            # how far the branch-C cut actually reaches: a substituted topic already inside the
            # envelope is rendered whole, so «bounded» is not the same as «cut»
            "with_a_topic_the_cut_shortened": sum(
                1 for row in rows if row["context"].get("topic_cut")
            ),
            "of": len(rows),
        }

    return {
        "topic_rule": (
            "a topic from a bought reader verdict is rendered whole; a substituted one is the"
            f" post's opening cut to {state['envelope']['limit']} characters — the longest bought"
            " topic — at a word boundary, marked with an ellipsis. Operator ruling of 2026-08-19,"
            " branch C: it closes the length finding and leaves the entity-block one open"
        ),
        "arms": {
            arm: {
                **steps(len(arm_rows(state, arm)), config),
                "distribution": distribution(arm_rows(state, arm)),
                "sampler_weights": sampler_weights(arm_rows(state, arm)),
                "context": context_counts(arm_rows(state, arm)),
                "file": ARM_NAMES[arm],
            }
            for arm in sorted(ARMS)
        },
        "dropped_for_length": {
            "rule": (
                f"bound_tokens > max_seq_len ({state['max_seq_len']}, config/qlora.yaml, frozen"
                " law). The bound is the worst measured tokens-per-character times the request's"
                f" characters, plus {TEMPLATE_SLACK} tokens of template slack"
            ),
            "n": len(state["dropped"]),
            "by_pack": dict(Counter(row["pack"] for row in state["dropped"])),
            "ids": sorted(row["id"] for row in state["dropped"]),
            "longest_kept": max((row["bound_tokens"] for row in state["rows"]), default=0),
            "shortest_dropped": min((row["bound_tokens"] for row in state["dropped"]), default=0),
        },
        "the_gate_s_own_rows": {
            "n": len(gold_items),
            "with_an_entity_block": sum(1 for one in gold_items if one.get("entities")),
            "reading": (
                "the 14 rows the sealed bar is scored on, counted in the probe-b pack that serves"
                " them. This is the number the training set's own context census is compared"
                " against: the gate is answered under a rich entity block and the training rows"
                " mostly are not"
            ),
        },
        "eval_pack": {
            "record": summary.rel(PROBE_PACK),
            "sha256": summary.sha256_of(PROBE_PACK),
            "items": len(probe["items"]),
            "with_an_entity_block": sum(1 for one in probe["items"] if one.get("entities")),
        },
    }


def holdout_units() -> set[tuple[str, int]]:
    """The registered evaluation-only rows, as `(thread, msg_id)`. Absent file → a STOP.

    Not an optional input with a quiet empty default: a producer whose exclusion list is missing
    builds a dataset with no exclusion applied and says nothing about it, which is the one failure
    this guard exists to make impossible ([[a_checker_whose_failure_is_silence]]).
    """
    record = json.loads(summary.read_text_or_refuse(HOLDOUT))
    if not record.get("evaluation_only"):
        raise SystemExit(
            f"{summary.rel(HOLDOUT)} does not declare itself evaluation-only. Either it is another"
            " record or the rule has been edited out of it — stop and report."
        )
    return {(one["thread"], int(one["msg_id"])) for one in record["units"]}


def sealed_arm_shas() -> dict[str, str]:
    """The dataset shas `results/pass1_sft.json` pins — the ONLY exemption from the holdout rule.

    Line B's two arms were built, trained and spent BEFORE the holdout existed, and their bytes are
    pinned by `results/prereg_lora_b.json` and `results/lora_b_verdict.json`. Refusing to rebuild
    them would refuse the reproduction of sealed evidence; carrying them past the rule by NAME would
    let the day someone changes what arm A is made of pass unnoticed. So the exemption is keyed on
    the bytes: an arm is exempt exactly while it rebuilds to the sha the record pins, and the moment
    its composition moves the exemption is gone and the rule applies to it
    ([[the_guard_hashes_the_half_that_cannot_move]]).
    """
    record = json.loads(summary.read_text_or_refuse(REPO_ROOT / RECORD_NAME))
    return {arm: block["sha256"] for arm, block in record["datasets"].items()}


def assert_no_holdout(arm: str, rows: list[dict], built_sha: str, sealed: dict[str, str]) -> str:
    """Refuse an arm that trains on a holdout row, unless it IS a sealed line-B dataset.

    Returns the exemption state so the record can publish it — a rule that was not applied and a
    rule that found nothing must never read the same in a file.
    """
    if sealed.get(arm) == built_sha:
        return "sealed-before-the-holdout"
    inside = sorted(
        f"{row['thread']}#{row['msg_id']}"
        for row in rows
        if (row["thread"], int(row["msg_id"])) in holdout_units()
    )
    if inside:
        raise SystemExit(
            f"arm {arm} carries {len(inside)} of the {len(holdout_units())} rows registered as"
            f" EVALUATION ONLY by {summary.rel(HOLDOUT)} — {inside[:3]}. They are never in any"
            " training set of any future line. Draw the arm without them, or register a new"
            " holdout; do not train on these."
        )
    return "checked-and-clear"


def build(state: dict | None = None) -> tuple[dict, dict[str, str]]:
    state = state or measure()
    smoke = smoke_pack(state)
    smoke_text = json.dumps(smoke, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    files = {
        arm: "".join(
            json.dumps(
                {key: value for key, value in row.items() if key != "bound_tokens"},
                ensure_ascii=False,
                sort_keys=True,
            )
            + "\n"
            for row in arm_rows(state, arm)
        )
        for arm in sorted(ARMS)
    }
    sealed = sealed_arm_shas()
    holdout = {
        arm: assert_no_holdout(arm, arm_rows(state, arm), sha_text(files[arm]), sealed)
        for arm in sorted(files)
    }
    record = {
        "arms": ARMS,
        "census": census(state),
        "contract": "docs/PROMPT-lora-b.md D1",
        "datasets": {
            arm: {
                "file": ARM_NAMES[arm],
                "rows": len(arm_rows(state, arm)),
                "sha256": sha_text(files[arm]),
            }
            for arm in sorted(files)
        },
        "instruments": {
            "parser": {
                "entry_point": "market_pulse.prompts.parse_pass1",
                "module": "src/market_pulse/prompts.py",
                "rule": "every target in both files is read back by it at build time",
                "sha256": summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "prompts.py"),
            },
            "prompt_sha256": {
                prompts.PASS1_TASK: prompts.prompt_sha256(prompts.PASS1_TASK),
            },
            "renderer": "market_pulse.prompts.pass1_messages_gm4",
        },
        "context_sources": verdict_sources(),
        "holdout": {
            "record": summary.rel(HOLDOUT),
            "sha256": summary.sha256_of(HOLDOUT),
            "units": len(holdout_units()),
            "rule": (
                "the rows registered EVALUATION ONLY by docs/PROMPT-pass1-fewshot.md D0.1 are never"
                " in any training set of any future line. The two arms below are exempt only while"
                " they rebuild to the sha this record pins — they were sealed before the holdout"
                " existed — and an arm whose composition moves loses the exemption with it"
            ),
            "arms": holdout,
        },
        "labels": {
            name: {
                "file": summary.rel(LABELS[name]),
                "labelled_by": json.loads(summary.read_text_or_refuse(PROVENANCE[name]))["labels"][
                    "labelled_by"
                ],
                "sha256": summary.sha256_of(LABELS[name]),
            }
            for name in sorted(LABELS)
        },
        "length": {
            "bound": state["ratio"],
            "topic_envelope": state["envelope"],
            "max_seq_len": state["max_seq_len"],
            "template_slack_tokens": TEMPLATE_SLACK,
            "config": "config/qlora.yaml",
            "config_sha256": summary.sha256_of(QLORA),
        },
        "packs": {
            name: {"file": summary.rel(PACKS[name]), "sha256": summary.sha256_of(PACKS[name])}
            for name in sorted(PACKS)
        },
        "producer": {"script": "scripts/build_pass1_sft.py"},
        "smoke": {
            "file": SMOKE_NAME,
            "row": smoke["items"][0]["id"],
            "sha256": sha_text(smoke_text),
            "rule": smoke["reading"],
        },
        "supervision": {
            "field": "subject_type",
            "learn_chars": (
                "each row's target is written whole and only its head — through the subject_type"
                " value AND the one separator character that closes it — is supervised."
                " `scripts/train_qlora.py` masks the rest out of the loss. The separator is inside"
                " the boundary because the mask is applied on token END offsets: with the boundary"
                " ON the value, a tokenizer that merges the closing quote with the comma produces a"
                " token ending one character past it, and that whole merge — the value's tail with"
                " it — falls out of supervision. It teaches structure the parser demands and no"
                " label; the two unlabelled fields are as untaught as they were"
            ),
            "boundary_char": SEPARATOR,
            "unsupervised_fields": ["subject_id", "stance"],
            "why": (
                "the team lead labelled subject_type and nothing else. Training the two unlabelled"
                " fields as null would teach «stance is always null», and three of the fourteen"
                " sealed gold rows score stance — the reachable maximum would fall to 11 against a"
                " threshold of 12 and the gate would be unreachable by construction"
            ),
        },
    }
    files[SMOKE_NAME] = smoke_text
    return record, files


def print_census(state: dict) -> None:
    table = census(state)
    print(
        f"\nPASS-1 SFT — the two arms, bound at max_seq_len {state['max_seq_len']};"
        f" substituted topics cut to {state['envelope']['limit']} chars"
        f" (the longest of {state['envelope']['measured_over']} bought ones)\n"
    )
    print(
        f"{'arm':>4}  {'rows':>5}  {'steps':>6}  {'бренд':>6} {'кат':>5} {'сеть':>5}"
        f" {'нн':>5} {'null':>5}   {'entities':>9} {'topic':>6}"
    )
    for arm, block in table["arms"].items():
        dist = block["distribution"]
        print(
            f"{arm:>4}  {block['n']:>5}  {block['steps']:>6}"
            f"  {dist['молочный_бренд']:>6} {dist['категория_личное']:>5}"
            f" {dist['сеть_ритейлер']:>5} {dist['не_наш_рынок']:>5} {dist['null']:>5}"
            f"   {block['context']['with_an_entity_block']:>9}"
            f" {block['context']['with_a_bought_topic']:>6}"
        )
    for arm, block in table["arms"].items():
        print(f"  arm {arm} sampler weights: {block['sampler_weights']}")
    dropped = table["dropped_for_length"]
    tail = (
        f" — longest kept {dropped['longest_kept']} tokens, shortest dropped"
        f" {dropped['shortest_dropped']}"
        if dropped["n"]
        else f" — every row fits; the longest is {dropped['longest_kept']} tokens"
    )
    print(f"\nDROPPED FOR LENGTH  {dropped['n']} rows{tail}")
    gate = table["the_gate_s_own_rows"]
    print(
        f"CONTEXT             the gate's {gate['n']} rows carry"
        f" {gate['with_an_entity_block']} entity blocks; the eval pack's"
        f" {table['eval_pack']['items']} items carry {table['eval_pack']['with_an_entity_block']}"
    )
    print(
        f"                    arm b's {table['arms']['b']['context']['of']} rows carry"
        f" {table['arms']['b']['context']['with_an_entity_block']}"
    )
    print(
        f"TOPIC               {table['arms']['b']['context']['with_a_bought_topic']} bought ·"
        f" {table['arms']['b']['context']['with_a_topic_the_cut_shortened']} cut to the envelope ·"
        f" {table['arms']['b']['context']['of'] - table['arms']['b']['context']['with_a_bought_topic'] - table['arms']['b']['context']['with_a_topic_the_cut_shortened']}"
        " substituted and already inside it"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=REPO_ROOT)
    parser.add_argument("--census", action="store_true", help="measure and print; write nothing")
    args = parser.parse_args(argv)

    state = measure()
    print_census(state)
    if args.census:
        return 0

    record, files = build(state)
    for key, text in files.items():
        path = args.outdir / ARM_NAMES.get(key, key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    record["producer"]["sha256"] = summary.sha256_of(Path(__file__))
    out = args.outdir / RECORD_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    out.write_text(payload, encoding="utf-8")
    for arm in sorted(ARM_NAMES):
        print(f"\nwrote {ARM_NAMES[arm]}  sha256 {record['datasets'][arm]['sha256'][:16]}…")
    print(
        f"wrote {SMOKE_NAME}  sha256 {record['smoke']['sha256'][:16]}…"
        f"  row {record['smoke']['row']}"
    )
    print(f"wrote {RECORD_NAME}  sha256 {sha_text(payload)[:16]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
