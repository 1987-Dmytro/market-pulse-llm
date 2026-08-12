#!/usr/bin/env python3
"""Write `results/sku_pilot_serving_v2.json` — what B′'s worker must answer, before it runs ($0).

Deliverable 2 of `docs/PROMPT-skub2-prep.md`, transcribing SPEC 3.17 (13)(a). The v1 pin
(`results/sku_pilot_serving.json`) is SEALED: it is what the v4 worker's `describe()` was held
against, it refuses to be regenerated, and it says 800. This is the pin BESIDE it, and exactly one
value differs — the positions ceiling, 800 → **1200**.

Why a second file rather than an edit. The v1 pin is the pre-run witness to what the paid v4
session's worker had to be; editing it would erase the configuration 121 bought elements were
extracted under. Same reasoning as the pre-registrations, and the same shape: a revision is a new
registration beside the old one, never an edit (SPEC 3.17 (5)).

What is NOT different, and is asserted rather than assumed:

* **the two registered prompt texts.** (13)(a) moves the parser, the ceiling and the alias table,
  and says «no new ML mechanism». The prompt shas are copied from `results/sku_pilot_prereg_v2.json`
  — the same source v1's pin copies them from — and this run refuses if the checkout renders
  anything else.
* **the base, the quantization, the template, greedy, batch 1, adapter OFF.** Every one of those is
  read from the same table v1 reads, so the two pins cannot drift apart on a value nobody moved.

The parser is not in here on purpose: `market_pulse.positions` runs on the CLIENT and a worker
cannot report it. Its sha belongs to the B′ pre-registration's pin set, beside this file's.

    PYTHONPATH=src python3 scripts/write_sku_serving_pin_v2.py
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

import serve_handler as handler  # noqa: E402
import write_sku_serving_pin as v1  # noqa: E402

from market_pulse import local_llm, prompts, provenance, serving  # noqa: E402

PREREG = v1.PREREG
V1_RECORD = v1.RECORD
RECORD = REPO_ROOT / "results" / "sku_pilot_serving_v2.json"

AUTHORITY = "docs/SPEC.md amendment 3.17 (13)(a) — instrument v2, ratified 2026-08-12"
CHANGED = "max_new_tokens"
"""The one field that differs from v1, named here so the check below can be a set comparison rather
than a reading of the diff. If a second value ever moves, this producer refuses until someone says
which — a serving pin whose divergence from its predecessor is unstated is not a pin."""


def expected_worker(prereg: dict) -> dict:
    """v1's block with the ceiling moved — built from v1's own function so nothing else can drift."""
    return v1.expected_worker(prereg) | {
        "max_new_tokens": handler.MAX_NEW_TOKENS[serving.POSITIONS_CONFIG]
    }


def check_exactly_one_knob_moved(pin: dict, previous: dict) -> list[str]:
    """v2 against the sealed v1, field by field. Anything but `max_new_tokens` stops the write."""
    moved = sorted(
        field
        for field in set(pin["expected_worker"]) | set(previous["expected_worker"])
        if pin["expected_worker"].get(field) != previous["expected_worker"].get(field)
    )
    if moved != [CHANGED]:
        raise SystemExit(
            f"v2 differs from {v1.rel(V1_RECORD)} on {moved}, and (13)(a) moves exactly [{CHANGED!r}]."
            " Either the amendment is wider than this producer knows or something drifted — stop"
            " and report rather than registering a configuration nobody ratified."
        )
    if pin["expected_worker"][CHANGED] <= previous["expected_worker"][CHANGED]:
        raise SystemExit(
            f"the v2 ceiling is {pin['expected_worker'][CHANGED]} against v1's"
            f" {previous['expected_worker'][CHANGED]} — (13)(a) RAISES it, and a lower one would"
            " truncate the pages the amendment exists to keep"
        )
    return moved


def build(prereg: dict, out: Path) -> dict:
    return {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "phase": "skub2 — instrument v2's serving configuration, pinned",
        "written_by": "skub2-prep (executor, $0), docs/PROMPT-skub2-prep.md deliverable 2",
        "authority": AUTHORITY,
        "class": (
            "SERVING PIN v2, registered BESIDE v1 and never in place of it. Committed before any"
            " skub2-run artifact exists; git history is the only witness to that ordering. Nothing"
            " here is a result and nothing is a preference — the one value that differs from v1 is"
            " the ceiling 3.17 (13)(a) raises, and this file refuses to write if a second one has"
        ),
        "supersedes": {
            "path": v1.rel(V1_RECORD),
            "sha256": hashlib.sha256(V1_RECORD.read_bytes()).hexdigest(),
            "reading": (
                "v1 stays SEALED and stays true: it is what the v4 worker's describe() was held"
                " against, and the 121 bought elements were extracted under it. This pin does not"
                " replace it, it stands beside it, and only skub2-run reads this one"
            ),
            "the_one_difference": CHANGED,
        },
        "serving": {
            "serving_config": serving.POSITIONS_CONFIG,
            "merge_state": serving.MERGE_STATE[serving.POSITIONS_CONFIG],
            "adapter": None,
            "adapter_note": (
                "the NF4 BASE with the adapter OFF, unchanged from v1. `serve_handler.settings`"
                " refuses the whole ADAPTER_ENV set before the model loads and `assert_no_adapter`"
                " refuses the loaded object — the environment and the model are two different checks"
            ),
            "model": local_llm.MODEL_ID,
            "model_revision": v1.pinned_revision(),
            "quantization": local_llm.QUANTIZATION,
            "chat_template": local_llm.CHAT_TEMPLATE,
            "decoding": "greedy",
            "do_sample": False,
            "forward_batch_size": 1,
            "max_new_tokens": handler.MAX_NEW_TOKENS[serving.POSITIONS_CONFIG],
            "max_new_tokens_was": v1.MAX_NEW_TOKENS,
            "max_new_tokens_note": (
                "still a CEILING against mid-JSON truncation and not a target length. It is raised"
                " because the v4 leaflet leg lost its DENSEST page to it: @atb_market_official:4401"
                " page 5 came back `malformed JSON` — a reply that used its whole budget — and that"
                " one page carried five of bar 1's 29 missed gold pairs. A reply that uses 1200 is"
                " still a PARSE FAILURE, counted by reason and excluded, never a shorter answer"
            ),
        },
        "instruments": v1.instruments(prereg)
        | {
            "source": f"{v1.rel(PREREG)} :: instruments",
            "note": (
                "UNCHANGED by (13)(a), which says «no new ML mechanism is authorised». Copied from"
                " the same pre-registration v1's pin copies them from, and a checkout rendering"
                " anything else stops this writer"
            ),
        },
        "expected_worker": expected_worker(prereg),
        "expected_worker_note": (
            "handed WHOLE to serving.assert_serving by the skub2-run driver before the first paid"
            " call. A worker still generating 800 is refused BY NAME on max_new_tokens, which is"
            " the whole reason the ceiling is a pinned field and not a client-side default"
        ),
        "pinned_inputs": {
            v1.rel(PREREG): hashlib.sha256(PREREG.read_bytes()).hexdigest(),
            v1.rel(V1_RECORD): hashlib.sha256(V1_RECORD.read_bytes()).hexdigest(),
        },
        "not_in_scope": {
            "the parser": (
                "market_pulse.positions runs on the CLIENT and no worker can report it, so its sha"
                " is pinned by results/sku_pilot_prereg_b2.json and not here. The two halves of"
                " instrument v2 are registered in the two files that can actually hold them"
            ),
            "the deployment": (
                "nothing is deployed and no RunPod resource is created. What is built here is the"
                " pin; standing a worker up against it is skub2-run's step"
            ),
        },
        "git": provenance.git_state(out),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prereg", type=Path, default=PREREG)
    parser.add_argument("--previous", type=Path, default=V1_RECORD)
    parser.add_argument("--out", type=Path, default=RECORD)
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite a pin the paid attempt may already have read",
    )
    args = parser.parse_args(argv)

    if args.out.exists() and not args.force:
        raise SystemExit(
            f"{v1.rel(args.out)} already exists. It is the pre-run witness to what B′'s worker has"
            " to be, and a regenerated copy would carry a timestamp and a git block from after the"
            " run — which is exactly what the artifact exists to rule out. --force if the pin has"
            " genuinely not been read yet."
        )

    prereg = json.loads(args.prereg.read_text(encoding="utf-8"))
    previous = json.loads(args.previous.read_text(encoding="utf-8"))
    record = build(prereg, args.out)
    moved = check_exactly_one_knob_moved(record, previous)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    served = record["serving"]
    print(f"wrote {v1.rel(args.out)}  (beside {v1.rel(args.previous)}, which stays sealed)")
    print(f"  config        {served['serving_config']} / {served['merge_state']}")
    print(f"  revision      {served['model_revision']}")
    print(
        f"  generation    {served['decoding']}, batch {served['forward_batch_size']},"
        f" max_new_tokens {served['max_new_tokens']} (v1: {served['max_new_tokens_was']})"
    )
    print(f"  moved         {moved} — every other expected_worker field is v1's")
    for task in sorted(prompts.POSITIONS):
        print(f"  {task:<20} {record['instruments'][task][:16]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
