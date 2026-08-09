#!/usr/bin/env python3
"""The Opus review's rows, aggregated for the operator's sitting (SPEC 3.16 (3)).

Every number this writes is a CANDIDATE. 3.16 (1) puts the whole program in the
REVIEW class: the deterministic matcher stays the sole judge of screen and G1e
numbers, screen v2 verdicts are not re-scored, and nothing here may reach
`results/baselines.json`. So the record says `review, not measurement` in the fields
themselves rather than in a header a later reader can skip, and every ratio is
carried beside the enumeration it was computed from — a per-channel-capped sample
judged by one reviewer produces a ratio that is a prompt for a sitting, not a rate.

What it refuses:

- **unvalidated rows.** `scripts/validate_opus_returns.py` is imported, not
  reimplemented; a file with any defect stops the run instead of contributing.
- **a protocol that moved.** The sha in the manifest is what the sessions were given.
  If `docs/PROMPT-opus-audit-protocol.md` at HEAD no longer hashes to it, the rows
  were produced under different instructions than the record would claim.
- **a model nobody declared.** `--model` defaults to `claude-opus-5` and is recorded
  as a DECLARATION: the returns file cannot prove which model wrote it, and 3.16 (2)
  says so — the pin that is possible is mandatory, the rest is why the class is review.

    PYTHONPATH=src python3 scripts/read_opus_audit.py

Reads the manifest and every returns file, writes `results/opus_audit_5c1.json`.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate_opus_returns as validator  # noqa: E402
from build_audit_pack import git_state  # noqa: E402
from build_opus_audit_packs import MANIFEST, PACK_DIR, digest, protocol_pin, rel  # noqa: E402

RECORD = REPO_ROOT / "results" / "opus_audit_5c1.json"
MODEL = "claude-opus-5"

REVIEW = "review, not measurement"
"""The label 3.16 (1) requires on every candidate number, in the record itself."""


def protocol_at_head(manifest: dict) -> dict:
    """The protocol's sha at HEAD, and a stop if it is not the one the packs carry.

    `protocol_pin` is the same check the builder ran — tracked, and identical to HEAD —
    so the sha it returns IS the sha at HEAD, and the file is not read a second way to
    say so. What is new here is the comparison against the manifest: the protocol may
    move between building the packs and reading them, and the sessions were given the
    one the packs name.
    """
    pin = protocol_pin(REPO_ROOT / manifest["protocol"]["path"])
    if pin["sha256"] != manifest["protocol"]["sha256"]:
        raise SystemExit(
            f"{manifest['protocol']['path']}: sha256 {pin['sha256'][:16]}… at HEAD but the packs"
            f" were built against {manifest['protocol']['sha256'][:16]}…. The sessions were given"
            " the manifest's protocol; a record naming today's would describe instructions nobody"
            " ran under."
        )
    return pin


def brand_tallies(pairs: list[tuple[str, str]]) -> dict:
    """`{brand_id: {count, items}}` for a list of `(item, brand_id)`, biggest first."""
    out: dict[str, dict] = {}
    for item, brand_id in pairs:
        entry = out.setdefault(brand_id, {"count": 0, "items": []})
        entry["count"] += 1
        entry["items"].append(item)
    for entry in out.values():
        entry["items"] = sorted(entry["items"])
    return dict(sorted(out.items(), key=lambda pair: (-pair[1]["count"], pair[0])))


def ratio(numerator: int, denominator: int) -> float | None:
    """`None`, not 0.0, when there is nothing to divide by — the two are different findings."""
    return round(numerator / denominator, 4) if denominator else None


def matcher_candidates(manifest: dict, rows: list[dict]) -> dict:
    """The matcher against the reviewer, per channel, as (item, brand_id) pairs.

    Judged at the pair level rather than the post level: a post where the matcher found
    one of two brands is neither a hit nor a miss, and rolling it up to the post would
    have to decide which. Precision is over what the matcher emitted, recall over what
    the reviewer found, and both denominators are per-channel-capped samples — which is
    why every cell carries its enumeration and the label above.
    """
    items = {entry["item"]: entry for entry in manifest["items"]}
    by_channel: dict[str, dict] = {}
    false_positives: list[tuple[str, str]] = []
    missed: list[tuple[str, str]] = []
    by_stratum: dict[str, Counter] = {}
    for row in rows:
        matcher = set(items[row["item"]]["matcher"]["watchlist_brands"])
        reviewer = set(row["watchlist_hits"])
        entry = by_channel.setdefault(
            row["channel"],
            {"items_judged": 0, "tp": 0, "fp": 0, "fn": 0, "false_positives": [], "missed": []},
        )
        entry["items_judged"] += 1
        entry["tp"] += len(matcher & reviewer)
        for brand_id in sorted(matcher - reviewer):
            entry["fp"] += 1
            entry["false_positives"].append({"item": row["item"], "brand_id": brand_id})
            false_positives.append((row["item"], brand_id))
        for brand_id in sorted(reviewer - matcher):
            entry["fn"] += 1
            entry["missed"].append({"item": row["item"], "brand_id": brand_id})
            missed.append((row["item"], brand_id))
        for stratum in row["strata"]:
            tally = by_stratum.setdefault(stratum, Counter())
            tally["items_judged"] += 1
            tally["tp"] += len(matcher & reviewer)
            tally["fp"] += len(matcher - reviewer)
            tally["fn"] += len(reviewer - matcher)
    for entry in by_channel.values():
        entry["precision_candidate"] = ratio(entry["tp"], entry["tp"] + entry["fp"])
        entry["recall_candidate"] = ratio(entry["tp"], entry["tp"] + entry["fn"])
    totals = {key: sum(entry[key] for entry in by_channel.values()) for key in ("tp", "fp", "fn")}
    return {
        "label": REVIEW,
        "definition": (
            "one (item, brand_id) pair per brand. TP the matcher and the reviewer agree, FP the"
            " matcher emitted and the reviewer did not confirm, FN the reviewer named and the"
            " matcher did not. Precision over the matcher's emissions, recall over the reviewer's"
            " finds"
        ),
        "not_a_rate": (
            "S2 and S3 are per-channel samples capped at 10, drawn for leverage and not"
            " proportionally, and one reviewer judged them. These ratios are a prompt for the"
            " sitting of 3.16 (3); the matcher's own numbers are the screen's and do not move"
        ),
        "overall": {
            **totals,
            "items_judged": sum(entry["items_judged"] for entry in by_channel.values()),
            "precision_candidate": ratio(totals["tp"], totals["tp"] + totals["fp"]),
            "recall_candidate": ratio(totals["tp"], totals["tp"] + totals["fn"]),
        },
        "by_stratum": {
            name: {
                **dict(tally),
                "precision_candidate": ratio(tally["tp"], tally["tp"] + tally["fp"]),
                "recall_candidate": ratio(tally["tp"], tally["tp"] + tally["fn"]),
            }
            for name, tally in sorted(by_stratum.items())
        },
        "by_channel": dict(sorted(by_channel.items())),
        "false_positive_candidates": brand_tallies(false_positives),
        "missed_brand_candidates": brand_tallies(missed),
    }


def caption_candidates(manifest: dict, rows: list[dict]) -> dict:
    """GM4's faithfulness, over the items that had something to be faithful to."""
    items = {entry["item"]: entry for entry in manifest["items"]}
    judgeable = [row for row in rows if items[row["item"]]["judgeable_caption"]]
    judged = [row for row in judgeable if row["caption_verdict"] != "n/a"]
    tally = Counter(row["caption_verdict"] for row in judged)
    by_channel: dict[str, dict] = {}
    for row in judged:
        entry = by_channel.setdefault(
            row["channel"], {"judged": 0, **{v: 0 for v in ("faithful", "partial", "wrong")}}
        )
        entry["judged"] += 1
        entry[row["caption_verdict"]] += 1
    for entry in by_channel.values():
        entry["faithful_rate_candidate"] = ratio(entry["faithful"], entry["judged"])
    return {
        "label": REVIEW,
        "instrument_judged": "gm4-nf4-base captions over their sha-matched sent images",
        "denominator": (
            "items whose caption a model wrote over images that are on disk under the sha the"
            " caption row recorded. Poll transcriptions carry no image and no model and are not in"
            " it — they would otherwise put free deterministic rows into GM4's rate"
        ),
        "judgeable": len(judgeable),
        "judged": len(judged),
        "declined_n_a": len(judgeable) - len(judged),
        "tally": dict(sorted(tally.items())),
        "faithful_rate_candidate": ratio(tally.get("faithful", 0), len(judged)),
        "by_channel": dict(sorted(by_channel.items())),
        "brands_visible_missed": brand_tallies(
            [(row["item"], brand_id) for row in judged for brand_id in row["brands_visible_missed"]]
        ),
    }


def open_extraction(rows: list[dict]) -> dict:
    """Dairy and ice-cream names outside the watchlist, as the reviewer spelled them.

    Not normalised beyond whitespace and case: the spelling IS the finding when the
    question is whether the watchlist is missing an entity, and folding «Дольче» into
    «дольче» is as far as a script may go before the sitting has ruled.
    """
    out: dict[str, dict] = {}
    for row in rows:
        for name in row["other_dairy_brands"]:
            entry = out.setdefault(name.casefold(), {"count": 0, "as_written": [], "items": []})
            entry["count"] += 1
            entry["items"].append(row["item"])
            if name not in entry["as_written"]:
                entry["as_written"].append(name)
    for entry in out.values():
        entry["items"] = sorted(entry["items"])
    return dict(sorted(out.items(), key=lambda pair: (-pair[1]["count"], pair[0])))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--pack", type=Path, default=PACK_DIR)
    parser.add_argument("--record", type=Path, default=RECORD)
    parser.add_argument("--model", default=MODEL, help="the model the sessions declared")
    parser.add_argument("returns", type=Path, nargs="*", help="default: every returns_NN.jsonl")
    args = parser.parse_args(argv)

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    protocol = protocol_at_head(manifest)
    paths = args.returns or sorted(args.pack.glob("returns_*.jsonl"))
    if not paths:
        raise SystemExit(
            f"no returns_NN.jsonl in {rel(args.pack)}. The sessions are the operator's to run"
            " (docs/PROMPT-opus-audit-a.md), and an aggregate over nothing is not a finding"
        )

    by_pack, defects, covered = validator.collect(manifest, list(paths))
    if defects:
        raise SystemExit(
            f"{len(defects)} defect(s) in the returns — aggregating them would launder a bad row"
            f" into a candidate number. Run scripts/validate_opus_returns.py:\n  "
            + "\n  ".join(defects[:5])
        )
    rows = [row for pack in sorted(by_pack) for row in by_pack[pack]]

    record = {
        "read_by": "scripts/read_opus_audit.py",
        "class": (
            "REVIEW, never measurement (SPEC 3.16 (1)). Nothing in this file may enter a gate, the"
            " screen or results/baselines.json. The deterministic matcher remains the sole judge of"
            " screen and G1e numbers; screen v2 verdicts are not re-scored; the prereg bars do not"
            " move. These are candidates for the operator sitting of 3.16 (3)"
        ),
        "instrument": {
            "model": args.model,
            "protocol_sha": protocol["sha256"],
            "protocol_path": protocol["path"],
            "protocol_head": protocol["head"],
            "declared_not_verified": (
                "the model is what the session declared on its first line, per the protocol's rule"
                " 1 — a returns file cannot prove which model wrote it. Price is unpinnable"
                " (subscription). 3.16 (2): the pin that is possible is mandatory, and the rest is"
                " why the output class is review"
            ),
        },
        "manifest": {"path": rel(args.manifest), "sha256": digest(args.manifest)},
        "seed": manifest["seed"],
        "coverage": {
            "packs_in_manifest": len(manifest["packs"]),
            "packs_returned": sorted(by_pack),
            "items_in_returned_packs": sum(entry["items"] for entry in covered),
            "items_in_all_packs": manifest["items_total"],
            "rows_read": len(rows),
            "unanswered": sorted(item for entry in covered for item in entry["unanswered"]),
            "by_pack": covered,
            "note": (
                "packs the operator has not run are absent, not zero. Every rate below is over the"
                " rows that came back and names its own denominator"
            ),
        },
        "matcher_candidates": matcher_candidates(manifest, rows),
        "caption_candidates": caption_candidates(manifest, rows),
        "open_extraction_candidates": {
            "label": REVIEW,
            "asks": "dairy / ice-cream names present that the watchlist does not carry",
            "names": open_extraction(rows),
        },
        "notes": [
            {"item": row["item"], "channel": row["channel"], "note": row["note"]}
            for row in rows
            if row["note"]
        ],
        "git": git_state(args.record),
    }
    args.record.parent.mkdir(parents=True, exist_ok=True)
    args.record.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    matcher, captions = record["matcher_candidates"], record["caption_candidates"]
    print(f"{len(rows)} rows from {len(by_pack)} of {len(manifest['packs'])} packs")
    print(
        f"matcher candidates: tp {matcher['overall']['tp']} · fp {matcher['overall']['fp']} ·"
        f" fn {matcher['overall']['fn']} · precision {matcher['overall']['precision_candidate']}"
        f" · recall {matcher['overall']['recall_candidate']}   [{REVIEW}]"
    )
    print(
        f"captions: {captions['judged']}/{captions['judgeable']} judged · {captions['tally']}"
        f" · faithful rate {captions['faithful_rate_candidate']}   [{REVIEW}]"
    )
    print(f"missed-brand candidates: {len(matcher['missed_brand_candidates'])} brand(s)")
    print(f"open extraction: {len(record['open_extraction_candidates']['names'])} name(s)")
    print(f"\nwrote {rel(args.record)} — candidates for the sitting, never gate numbers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
