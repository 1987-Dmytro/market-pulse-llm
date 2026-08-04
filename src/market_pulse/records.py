"""Reading `results/baselines.json` the way a gate has to read it.

Three things are asked of that file once a fine-tune exists, and all three are
refusals rather than lookups:

- **which row is the anchor.** Amendment 3.5 (1) makes the own-pod zero-shot row
  baseline (c) for every gate and says the anchors are read programmatically,
  never typed. The trap is that Phase 4's *fine-tuned* runs are also
  ``backend: "local"`` — a first-match lookup would hand a model itself as its
  own baseline and every verdict would be quietly wrong. So the selector refuses
  ambiguity instead of picking, and narrows on something training cannot fake:
  a zero-shot row declares it trained on nothing.
- **whether the prompts still hash to what the record measured.** The prompt is
  part of the measurement (SPEC §7): a training set built from a moved prompt
  trains for a different task than the gate scores.
- **whether the G1b slice file is the one the anchor measured.** Amendment
  3.5 (3) makes the persisted 44 ids the slice; a regenerated or edited file
  would change the gate's denominator without changing a single number in the
  record, so the SHA256 the record stores is checked before the ids are used.

Pure: every function takes already-loaded data. The scripts own the paths — the
package is not the place that knows where the repo is.
"""

import json
from hashlib import sha256
from pathlib import Path

from market_pulse import prompts

ANCHOR_TRAIN_SOURCES = {"zero-shot": "no training data"}
"""What ``build_record`` writes for a run with no training data at all."""


def prompt_sha_history(history: dict, model: str) -> list[dict]:
    """Every ``prompt_sha256`` map the results file already holds for a model."""
    return [
        record["config"]["prompt_sha256"]
        for record in history.get(model, [])
        if not record.get("reference_only") and "prompt_sha256" in record["config"]
    ]


def assert_prompt_sha(recorded: list[dict], model: str) -> dict:
    """Refuse to proceed unless this checkout's fixed prompts hash to the recorded ones.

    Compared against the hashes **stored in the records**, never against
    `prompts.prompt_sha256` on both sides of the equals sign — that assertion
    passes forever and proves nothing. What the hash covers is exactly
    ``prompts.PROMPTS``; the row wrapper and the single ``user`` role come from
    ``prompts.build_messages``, which every caller shares, so widening the hash
    would make new runs incomparable to the rows they exist to match.
    """
    if not recorded:
        raise ValueError(
            f"{model}: no record carries a prompt_sha256 to check against — this run"
            " would have nothing to be identical to. Stop and report."
        )
    current = {task: prompts.prompt_sha256(task) for task in prompts.TASKS}
    for stored in recorded:
        if stored != current:
            differ = sorted(task for task in current if stored.get(task) != current[task])
            raise ValueError(
                f"{model}: prompt SHA256 differs from the recorded run on {differ} — recorded"
                f" {stored}, now {current}. The prompt is part of the measurement (SPEC §7);"
                " stop and report rather than re-baselining silently."
            )
    return current


DEFAULT_TESTSET_VERSION = "v2"
"""What a record that names no test-set version was measured on.

Every Phase 4 record predates the field, and all of them scored the v2 files. Read as a
default rather than back-filled into the file: a record is what a run wrote."""


def anchor(history: dict, version: str = DEFAULT_TESTSET_VERSION) -> dict:
    """The one zero-shot own-pod record a version's bars are measured from.

    Raises unless exactly one row qualifies. Zero means the anchor was never
    appended; more than one means two rows claim the same job and picking either
    is a guess — 4c's fine-tuned rows share the ``local`` backend, so this is the
    realistic failure and it must be loud.

    ``version`` is the fourth narrowing and it was added when the second anchor
    existed: 4.5h2's v4 anchor is a zero-shot own-pod row with valid gate anchoring,
    exactly like 4a's, so without it the two are indistinguishable and every Phase 4
    bar would start refusing the moment the new row landed.
    """
    rows = [
        record
        for records in history.values()
        for record in records
        if record.get("config", {}).get("backend") == "local"
        and record["config"].get("train_sources") == ANCHOR_TRAIN_SOURCES
        and record["config"].get("testset_version", DEFAULT_TESTSET_VERSION) == version
        and record.get("diagnostics", {}).get("gate_anchor_valid") is True
        and not record.get("reference_only")
    ]
    if len(rows) != 1:
        found = [f"{record['model']} @ {record['timestamp']}" for record in rows]
        raise ValueError(
            f"the zero-shot own-pod anchor for test set {version} must be exactly one record,"
            f" found {len(rows)}: {found}."
            " A gate anchored on a guess is not anchored (SPEC amendment 3.5 (1))."
        )
    return rows[0]


GATED_METRICS = {
    "G1a": "sentiment macro-F1",
    "G1c": "intents micro-F1",
    "G1d": "post_type macro-F1",
    "G1e": "brand extraction F1",
}
"""Which metric each gate reads, because the gate id alone does not say.

**G1d appears twice in a record.** Amendment 3.3 settled that G1d gates the
3-class post type alone and that relevance is *reported beside it, never inside
it* — and `build_gates` writes both rows under the id `G1d`, the second one
carrying a note. Keying a record by its gate ids therefore hands out the
relevance number, which is the ungated one and the higher one. Selecting on the
metric is what makes the choice visible instead of positional.
"""


def anchor_values(record: dict) -> dict:
    """The anchor's gated numbers, in the shape :func:`scorer.gate_thresholds` reads.

    G1b is deliberately absent: its bar is a count over the slice, not a margin
    over a baseline, and the anchor's G1b value is ``null`` by construction — a
    fix-rate needs a fine-tune.
    """
    values = {}
    for gate, metric in GATED_METRICS.items():
        matched = [
            entry
            for entry in record["gates"]
            if entry["gate"] == gate and entry["metric"].startswith(metric)
        ]
        if len(matched) != 1:
            raise ValueError(
                f"the anchor record holds {len(matched)} rows for {gate} '{metric}' — it anchors"
                f" {gate} only if exactly one does"
            )
        values[gate] = matched[0]["values"] if gate == "G1a" else matched[0]["value"]
    return values


def arm_record(history: dict, arm: str) -> dict:
    """The one record of an ablation arm, or a refusal — :func:`anchor`'s sibling.

    Selected on ``config.fine_tune.arm``, which only a run that loaded an adapter
    writes. Two rows for one arm would mean the arm was scored twice, and 4c's
    contract is that it is scored once: picking either would be choosing a gate
    verdict by position in a file.
    """
    rows = [
        record
        for runs in history.values()
        for record in runs
        if record.get("config", {}).get("fine_tune", {}).get("arm") == arm
        and not record.get("reference_only")
    ]
    if len(rows) != 1:
        found = [f"{record['model']} @ {record['timestamp']}" for record in rows]
        raise ValueError(
            f"the {arm!r} arm must be exactly one record, found {len(rows)}: {found}."
            " Each arm is trained once and scored once (SPEC amendment 3.4 (3))."
        )
    return rows[0]


def arm_values(record: dict) -> dict:
    """An arm's gated numbers, G1b included — what the rule and the bars read.

    :func:`anchor_values` covers the four heads that are margins over a baseline;
    G1b is the one gate whose value is a count over a pre-registered slice, so it
    is read here with the guard delta that is the other half of it.
    """
    values = anchor_values(record)
    matched = [entry for entry in record["gates"] if entry["gate"] == "G1b"]
    if len(matched) != 1 or matched[0].get("value") is None:
        raise ValueError(
            f"an arm record must carry exactly one scored G1b, found {len(matched)}"
            f" ({[entry.get('value') for entry in matched]}) — a fix-rate needs a fine-tune"
        )
    entry = matched[0]
    values["G1b"] = {
        "rate": entry["value"],
        "fixed": entry["fixed"],
        "n": entry["n"]["slice"],
        "guard_delta": entry["guard"]["delta"],
    }
    return values


def slice_ids(text: str, record: dict) -> list[str]:
    """The G1b slice ids, or a refusal — the file has to be the anchor's file.

    ``text`` is the raw file, hashed exactly as ``write_slice`` hashed it when
    the anchor run persisted it.
    """
    expected = record["config"]["g1b_slice_sha256"]
    digest = sha256(text.encode("utf-8")).hexdigest()
    if digest != expected:
        raise ValueError(
            f"the G1b slice file does not match the anchor record: expected {expected},"
            f" got {digest}. The slice is pre-registered (amendment 3.5 (3)) — a"
            " regenerated or edited file is a different gate, not a fresher one."
        )
    return json.loads(text)["ids"]


def artifact_sha256(root: Path) -> str:
    """Content hash of a directory — the adapter, in exactly one implementation.

    The one function here that takes a path instead of loaded data, and
    deliberately: the pod writes this number into a gate record and the Mac
    re-checks it after the sync, so a second implementation would produce a
    mismatch that means nothing about the artefact. Every file under ``root``
    contributes its POSIX-relative path and its bytes in sorted order, so the
    digest is of the adapter and not of the order a filesystem walked it.
    """
    digest = sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8") + b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()
