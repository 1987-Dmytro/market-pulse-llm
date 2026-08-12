#!/usr/bin/env python3
"""Write `results/sku_pilot_serving.json` — what sku-b's worker must answer, before it runs ($0).

Deliverable 4 of `docs/PROMPT-sku-b-prep.md`, transcribing SPEC 3.17 (9). The amendment says the
configuration "is committed as its own artifact BEFORE the paid attempt and the driver stops before
the first paid call unless the worker's describe() matches it", and this is that artifact.

A FILE and not a constant, for the reason the pre-registration is a file: the identity stop is only
a stop if what it compares against was fixed before the run and can be read by someone who was not
in the session. `scripts/positions_gm4_skub.py` loads this record and hands
`serving.assert_serving` exactly its `expected_worker` block — it does not restate a single value —
so the pin cannot drift from the check, and `tests/test_sku_serving_pin.py` holds the record
against the code both ways so the code cannot drift from the pin.

Two things it does NOT do:

* **it invents nothing.** Every value is transcribed from SPEC 3.17 (9) or read out of an artifact:
  the two prompt shas are COPIED from `results/sku_pilot_prereg_v2.json :: instruments` and this
  run refuses if the checkout renders anything else, which is the case where a registered text was
  edited instead of re-registered.
* **it is not re-derivable after the fact.** It refuses to overwrite an existing pin (`--force`
  overrides and says so): once the paid attempt has read it, a regenerated file would carry a
  `generated_at` and a `git` block from after the run, and the ordering git history witnesses is
  the whole value of the artifact.

    PYTHONPATH=src python3 scripts/write_sku_serving_pin.py
"""

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))


from market_pulse import local_llm, prompts, provenance, serving  # noqa: E402

PREREG = REPO_ROOT / "results" / "sku_pilot_prereg_v2.json"
RECORD = REPO_ROOT / "results" / "sku_pilot_serving.json"

MODEL_REVISION = "842da3794eaa0b77d5f08bae87a17459d91ff475"
"""The pinned base revision, in full — the same weights config A, the 4.5h2 pod and both caption
sessions ran on. SPEC 3.17 (9) says "the NF4 BASE at the pinned revision" and `docs/SPEC.md:424`
writes the sha ABBREVIATED (`842da3794eaa…`), which is not something a worker can be held to. So
the full value is checked against a record that actually served it — see :func:`pinned_revision`."""

REVISION_SOURCE = REPO_ROOT / "results" / "captions_gm4_atb19.json"
"""The freshest PAID record on this base: vis-b's 19 ATB posts, whose worker reported the revision
it had resolved. A typed sha is a guess until something that ran on it agrees."""

MAX_NEW_TOKENS = 800
"""The ceiling THIS pin registered, transcribed rather than read off `serve_handler`.

SPEC 3.17 (13)(a) moved the live constant to 1200 on 2026-08-12. This file is v1's serving pin, it
is what the v4 worker's `describe()` was held against, and it refuses to be regenerated at all —
so following the code would make it claim a configuration no paid call ever ran under. The v2 pin
beside it reads the live table, which is the whole point of there being two."""


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def pinned_revision(path: Path = REVISION_SOURCE, spec: Path | None = None) -> str:
    """The full base revision, corroborated by a record whose worker served it.

    Two readings, and neither alone is enough: `docs/SPEC.md` names the revision but abbreviates
    it, and a past record holds the full string but is not the law. So the law's prefix has to be
    a prefix of the record's value, and the constant above has to equal the record — which is a
    check a mistyped sha fails and a copied one passes.
    """
    spec = REPO_ROOT / "docs" / "SPEC.md" if spec is None else spec
    served = json.loads(path.read_text(encoding="utf-8"))["endpoint"]["worker"][
        "revision_requested"
    ]
    if served != MODEL_REVISION:
        raise SystemExit(
            f"{rel(path)} was served at {served} and this pin says {MODEL_REVISION} — one of the"
            " two is not the base SPEC 3.17 (9) fixes. Stop and report."
        )
    if f"`{MODEL_REVISION[:12]}…`" not in spec.read_text(encoding="utf-8"):
        raise SystemExit(
            f"docs/SPEC.md does not name `{MODEL_REVISION[:12]}…` — the revision this pin holds is"
            " not the one the law abbreviates. Stop and report."
        )
    return MODEL_REVISION


def instruments(prereg: dict) -> dict:
    """The two prompt shas, copied from the pre-registration and checked against this checkout.

    Copied rather than recomputed, because the pre-registration is what the pilot is scored
    against: if the two ever disagree the answer is not to follow the code, it is to stop. A
    registered text is revised by registering a new one beside it (SPEC 3.17 (5)), never by editing.
    """
    registered = {task: prereg["instruments"][task] for task in sorted(prompts.POSITIONS)}
    live = {task: prompts.prompt_sha256(task) for task in sorted(prompts.POSITIONS)}
    if registered != live:
        moved = [task for task in registered if registered[task] != live[task]]
        raise SystemExit(
            f"{', '.join(moved)}: this checkout renders a text that is not the one"
            f" {rel(PREREG)} registered ({', '.join(live[t][:12] + '…' for t in moved)} against"
            f" {', '.join(registered[t][:12] + '…' for t in moved)}). A revised instrument is a new"
            " registration beside the old one, and the pilot's bars were written against these."
        )
    return registered


def expected_worker(prereg: dict) -> dict:
    """Exactly what the driver hands `serving.assert_serving` before the first paid call.

    Six fields, and each one is a way the run could be the wrong measurement while every reply
    still looked fine: another config, an adapter on the model, a text that moved, a shorter
    ceiling truncating the JSON, an unpinned base. `assert_serving` reads a field the worker does
    not report at all as `<absent>` and refuses, so asking is free.
    """
    return {
        "serving_config": serving.POSITIONS_CONFIG,
        "merge_state": serving.MERGE_STATE[serving.POSITIONS_CONFIG],
        "adapter_sha256": None,
        "positions_prompt_sha256": instruments(prereg),
        "max_new_tokens": MAX_NEW_TOKENS,
        "revision_requested": pinned_revision(),
    }


def build(prereg: dict, out: Path) -> dict:
    return {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "phase": "sku-b — the pilot's serving configuration, pinned",
        "written_by": "sku-b-prep (executor, $0), docs/PROMPT-sku-b-prep.md deliverable 4",
        "authority": "docs/SPEC.md amendment 3.17 (9)",
        "class": (
            "SERVING PIN. Committed in its own commit before any sku-b-run artifact exists in the"
            " repo; git history is the only witness to that ordering. Nothing here is a result, and"
            " nothing here is a preference — every value is transcription of 3.17 (9)"
        ),
        "serving": {
            "serving_config": serving.POSITIONS_CONFIG,
            "merge_state": serving.MERGE_STATE[serving.POSITIONS_CONFIG],
            "adapter": None,
            "adapter_note": (
                "the NF4 BASE with the adapter OFF. `serve_handler.settings` refuses the whole"
                " ADAPTER_ENV set before the model loads and `assert_no_adapter` refuses the loaded"
                " object — the environment and the model are two different checks"
            ),
            "model": local_llm.MODEL_ID,
            "model_revision": pinned_revision(),
            "quantization": local_llm.QUANTIZATION,
            "chat_template": local_llm.CHAT_TEMPLATE,
            "decoding": "greedy",
            "do_sample": False,
            "forward_batch_size": 1,
            "max_new_tokens": MAX_NEW_TOKENS,
            "max_new_tokens_note": (
                "a CEILING against mid-JSON truncation, not a target length. A reply that used its"
                " whole budget is a PARSE FAILURE here, counted by reason and excluded from bar 3's"
                " denominator — not a shorter answer"
            ),
        },
        "instruments": instruments(prereg)
        | {
            "source": f"{rel(PREREG)} :: instruments",
            "note": (
                "copied from the pre-registration, not recomputed: the bars were registered against"
                " these two texts, and a checkout rendering anything else stops this writer"
            ),
        },
        "expected_worker": expected_worker(prereg),
        "expected_worker_note": (
            "handed WHOLE to serving.assert_serving by scripts/positions_gm4_skub.py before the"
            " first paid call. The driver restates none of it, so this file is the identity stop"
        ),
        "pinned_inputs": {
            rel(PREREG): hashlib.sha256(PREREG.read_bytes()).hexdigest(),
        },
        "revision_corroborated_by": (
            f"{rel(REVISION_SOURCE)} :: endpoint.worker.revision_requested — the freshest PAID"
            " record on this base. docs/SPEC.md names the revision abbreviated, and a worker"
            " cannot be held to an abbreviation"
        ),
        "not_in_scope": {
            "the volume re-stage": (
                "deploying a worker that serves this configuration is sku-b-run's step, not this"
                " contract's. What is built here is the code and the pin; nothing is deployed and"
                " no RunPod resource of any kind is created"
            ),
            "the endpoint id": (
                "there is no default endpoint anywhere in this contract. A run against whatever id"
                " was last in a shell variable is a run against an unknown configuration"
            ),
        },
        "git": provenance.git_state(out),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prereg", type=Path, default=PREREG)
    parser.add_argument("--out", type=Path, default=RECORD)
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite a pin the paid attempt may already have read",
    )
    args = parser.parse_args(argv)

    if args.out.exists() and not args.force:
        raise SystemExit(
            f"{rel(args.out)} already exists. It is the pre-run witness to what the worker had to"
            " be, and a regenerated copy would carry a timestamp and a git block from after the"
            " run — which is exactly what the artifact exists to rule out. --force if the pin has"
            " genuinely not been read yet."
        )

    prereg = json.loads(args.prereg.read_text(encoding="utf-8"))
    record = build(prereg, args.out)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    served = record["serving"]
    print(f"wrote {rel(args.out)}")
    print(f"  config        {served['serving_config']} / {served['merge_state']}")
    print(f"  revision      {served['model_revision']}")
    print(
        f"  generation    {served['decoding']}, batch {served['forward_batch_size']},"
        f" max_new_tokens {served['max_new_tokens']}"
    )
    for task in sorted(prompts.POSITIONS):
        print(f"  {task:<20} {record['instruments'][task][:16]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
