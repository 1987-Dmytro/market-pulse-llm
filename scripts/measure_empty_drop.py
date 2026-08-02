#!/usr/bin/env python3
"""The rows the re-label emptied: how many, how short, how much of the drift (4.5f).

Two of the three operator rulings are the same failure. `Картопля з печінкою` and
`З вишнею` are replies under a poll-style post; their intent is in the parent, the
re-labeller is handed the comment text and nothing else, and it answered `[]`. This
measures the size of that class — non-empty under v1, `[]` under v2 — against the
part of the drift the taxonomy does not explain (`changed_without_service`).

No requests: every number comes from rows a paid run already wrote.

Three things it insists on:

- **the measurement is of the re-labeller, not of the corrected corpus.** The three
  4.5f rulings are reversed before counting, so the number does not move depending
  on which side of `apply_calibration_rulings.py` this runs on. How many were
  reversed is printed and recorded.
- **the containment is checked, not assumed.** A row that lost every label and
  gained no `service` must be inside `changed_without_service` — as a set of ids,
  because a count that merely fits would pass for the wrong reason.
- **the premise is measured too.** The hypothesis rests on the model seeing no
  parent post, so the rendered prompt is checked against the row's other fields:
  if a future change starts threading `parent_msg_id` or the channel into it, this
  stops instead of reporting a stale explanation.

    PYTHONPATH=src python3 scripts/measure_empty_drop.py

Writes `results/drop_45f.json`. Nothing else is written.
"""

import argparse
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))  # the staging convention lives there

import relabel_intents as relabel  # noqa: E402
from build_audit_pack import git_state  # noqa: E402
from market_pulse import prompts  # noqa: E402

RECORD = REPO_ROOT / "results" / "drop_45f.json"
RUN = REPO_ROOT / "results" / "relabel_45e.json"

CONTEXT_FIELDS = ("parent_msg_id", "msg_id", "channel", "date")
"""Row fields that would be context if the prompt carried them. It carries none."""


def pairs(sources: dict[str, Path], fixes: dict[str, list[str]]) -> list[dict]:
    """Every staged row beside its v1 label, with the 4.5f rulings put back."""
    rows = []
    for name, source in sources.items():
        staged = relabel.staged(source)
        before = {row["id"]: row for row in relabel.load(source)[0]}
        for row in relabel.load(staged)[0]:
            after = fixes.get(row["id"], row["intents"])
            old = before[row["id"]]
            rows.append(
                {
                    "id": row["id"],
                    "source": name,
                    "text": row["text"],
                    "unclear": row["unclear"],
                    "parent_msg_id": old.get("parent_msg_id"),
                    "before": sorted(old["intents"]),
                    "after": sorted(after),
                }
            )
    return rows


def reversals(record: Path) -> dict[str, list[str]]:
    """id -> the label the re-labeller produced, for every row a ruling has moved since."""
    if not record.exists():
        return {}
    history = json.loads(record.read_text(encoding="utf-8"))
    return {row["id"]: row["old"] for fix in history.get("fixes", []) for row in fix["rows"]}


def premise(rows: list[dict], sources: dict[str, Path]) -> dict:
    """What of a row reaches the model. The hypothesis is void if it is more than text.

    One row settles it, because the prompt is a template and not a per-row decision —
    but it has to be a row that actually carries the fields, or the check passes by
    having nothing to look for.

    Deliberately still ``relabel.TASK``, the prompt that produced the staged corpus. 4.5g
    registered `relabel_intents_v2_with_post` beside it, and rendering *that* one here
    would raise from :func:`prompts.build_messages` (a with-post task without a post) —
    which would be a re-run of this measurement reading the new prompt's guard as a
    regression in the old one's finding.
    """
    full = {row["id"] for row in rows if row["parent_msg_id"] is not None}
    raw = next(
        (
            row
            for source in sources.values()
            for row in relabel.load(source)[0]
            if row["id"] in full and all(row.get(field) is not None for field in CONTEXT_FIELDS)
        ),
        None,
    )
    if raw is None:
        raise SystemExit(
            "no re-labelled row carries a parent post, so the claim that the model never sees"
            " one cannot be checked against anything"
        )
    rendered = "\n".join(
        message["content"] for message in prompts.build_messages(relabel.TASK, raw["text"])
    )
    leaked = [field for field in CONTEXT_FIELDS if str(raw[field]) in rendered]
    if leaked:
        raise SystemExit(
            f"{raw['id']}: {leaked} reach the prompt. The re-labeller now sees more than the"
            " comment text, so 'it never sees the parent post' is no longer the explanation."
        )
    return {
        "checked_on": raw["id"],
        "row_fields_in_the_prompt": ["text"],
        "absent_from_the_prompt": list(CONTEXT_FIELDS),
        "replies_among_the_relabelled": len(full),
    }


def spread(rows: list[dict]) -> dict:
    """Text length, described by quantiles — the distribution is long-tailed, a mean lies."""
    lengths = sorted(len(row["text"]) for row in rows)
    if not lengths:
        return {"rows": 0}
    quarters = statistics.quantiles(lengths, n=4) if len(lengths) > 1 else [lengths[0]] * 3
    return {
        "rows": len(lengths),
        "chars_p25": round(quarters[0], 1),
        "chars_median": round(statistics.median(lengths), 1),
        "chars_p75": round(quarters[2], 1),
        "chars_max": lengths[-1],
        "reply_share": round(sum(row["parent_msg_id"] is not None for row in rows) / len(rows), 4),
    }


def measure(rows: list[dict]) -> dict:
    """The drop class inside one population, and the drift it accounts for."""
    dropped = {row["id"] for row in rows if row["before"] and not row["after"]}
    unexplained = {
        row["id"] for row in rows if row["before"] != row["after"] and "service" not in row["after"]
    }
    if not dropped <= unexplained:
        raise SystemExit(
            f"{len(dropped - unexplained)} emptied rows are outside changed_without_service."
            " A row that lost every label gained no `service`, so the two sets disagree about"
            " what the drift is and neither share means anything."
        )
    changed = sum(1 for row in rows if row["before"] != row["after"])
    return {
        "rows": len(rows),
        "changed": changed,
        "changed_without_service": len(unexplained),
        "changed_without_service_rate": len(unexplained) / len(rows) if rows else 0.0,
        "emptied": len(dropped),
        "share_of_rows": len(dropped) / len(rows) if rows else 0.0,
        "share_of_changed_without_service": len(dropped) / len(unexplained) if unexplained else 0.0,
        "emptied_from": dict(
            sorted(
                Counter(", ".join(row["before"]) for row in rows if row["id"] in dropped).items(),
                key=lambda kv: -kv[1],
            )
        ),
        "emptied_text": spread([row for row in rows if row["id"] in dropped]),
        "rest_text": spread([row for row in rows if row["id"] not in dropped]),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=RUN)
    parser.add_argument("--record", type=Path, default=RECORD)
    args = parser.parse_args(argv)

    reversed_rows = reversals(args.run)
    rows = pairs(relabel.SOURCES, reversed_rows)
    populations = {
        "all": rows,
        "scoreable": [row for row in rows if not row["unclear"]],
        "unclear": [row for row in rows if row["unclear"]],
    }
    found = {name: measure(part) for name, part in populations.items()}
    record = {
        "measured_by": "scripts/measure_empty_drop.py",
        "question": (
            "How many rows carried an intent under v1 and none under v2, how short they are,"
            " and how much of `changed_without_service` — the drift the taxonomy does not"
            " explain — they account for."
        ),
        "rulings_reversed": sorted(reversed_rows),
        "reversal_note": (
            "The 4.5f operator rulings are put back to what the re-labeller produced. This"
            " measures the model, and two of the three ruled rows are the clearest instances"
            " of the class being measured — leaving them corrected would understate it."
        ),
        "premise": premise(rows, relabel.SOURCES),
        "populations": found,
        "git": git_state(args.record),
    }
    args.record.parent.mkdir(parents=True, exist_ok=True)
    args.record.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"{len(reversed_rows)} ruling(s) reversed: {', '.join(sorted(reversed_rows)) or '—'}")
    print(f"the prompt carries {record['premise']['row_fields_in_the_prompt']} of a row\n")
    head = f"{'population':<11}{'rows':>6}{'changed':>9}{'no service':>12}{'emptied':>9}{'of those':>10}"
    print(head)
    for name, block in found.items():
        print(
            f"{name:<11}{block['rows']:>6}{block['changed']:>9}"
            f"{block['changed_without_service']:>12}{block['emptied']:>9}"
            f"{block['share_of_changed_without_service']:>9.1%}"
        )
    print(f"\n{'':<11}{'n':>6}{'p25':>7}{'median':>8}{'p75':>7}{'max':>7}{'replies':>9}")
    for name, block in found.items():
        for kind in ("emptied_text", "rest_text"):
            shape = block[kind]
            print(
                f"{name + '/' + kind.split('_')[0]:<11}{shape['rows']:>6}{shape['chars_p25']:>7.0f}"
                f"{shape['chars_median']:>8.0f}{shape['chars_p75']:>7.0f}{shape['chars_max']:>7}"
                f"{shape['reply_share']:>9.1%}"
            )
    print(f"\nwrote {relabel.rel(args.record)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
