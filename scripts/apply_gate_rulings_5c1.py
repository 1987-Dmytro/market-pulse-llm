#!/usr/bin/env python3
"""Apply the operator's 5c1 gate rulings, then write the registry (PROMPT-5c1 D1, second half).

The gate measured 63 candidates and stopped (`results/entry_gate_5c1.json`). The operator ruled
on its one FAIL and seven FLAGs on 2026-08-07 — the rulings are canon in
`docs/CHANNELS-launch.md`, section "Рулинги гейта 5c1". This script does the two things that
follow, and nothing else:

1. writes each ruling into its row's `ruling` field, so the record says what was decided about
   what was measured instead of leaving the measurement to be re-read by hand;
2. appends the surviving channels to `config/registry.yaml` under `sources:` — additive,
   `taxonomy:` and `watchlist:` untouched and checked byte-for-byte after the write.

The gate's rows are never edited or deleted. A channel the operator excluded was still measured,
and dropping its row would rewrite what the pass found; `ruling` is what says it is out.

    PYTHONPATH=src python3 scripts/apply_gate_rulings_5c1.py --plan   # print, write nothing
    PYTHONPATH=src python3 scripts/apply_gate_rulings_5c1.py
"""

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_audit_pack import git_state  # noqa: E402

from market_pulse.registry import SOURCE_TYPES, load_registry  # noqa: E402

REGISTRY = REPO_ROOT / "config" / "registry.yaml"
GATE_RECORD = REPO_ROOT / "results" / "entry_gate_5c1.json"
CANON = "docs/CHANNELS-launch.md, section 'Рулинги гейта 5c1 (2026-08-07)'"

EXCLUDED = {
    "@kolyastravinsky": "theme: a personal RU-language blog (Samara restaurants, ballet) — the"
    " pre-registered theme flag is confirmed",
    "@whowears": "theme: RU fashion and lifestyle, nothing in the tracked category",
    "@Mambabyua": "a supergroup, not a channel: its 280.75/week is member chat traffic. The"
    " chat-mining track is recorded as DEFERRED — nothing is built for it here",
    "@kulinariya_chat_a": "a supergroup, not a channel: 300/week of chat messages. Same deferred"
    " chat-mining track",
    "@marketopt_official": "late addition WITHDRAWN — the handle resolves to a dead"
    " 132-subscriber channel, and the canon's '41,518' had no source artifact behind it",
    "@akcii_skidki_plt": "late addition #2 EXCLUDED (operator, 2026-08-07 on the gate report):"
    " dead by canon's own conjunction — its ten sampled posts run 2024-04-19 to 2024-06-06, so"
    " 26 months of silence, and there is no discussion group. Same class as the six the operator"
    " excluded on 06.08",
}
"""Ruled out of the composition. Their gate rows stay in the record, carrying this text."""

MOVED = {
    "@maudau": (
        "posts",
        "moved to posts-only: the linked group bans everyone from sending, so 0 of 50 sampled"
        " posts carry comments and a join buys nothing. comments_enabled false, NO join",
    ),
}

KEPT = {
    "@discountua1": "kept in the comments bucket WITH a join: 0 of 7 sampled posts is a thin"
    " denominator, and the 28-day window measures the real flow. Demotion is a cycle-1 review"
    " question, not this phase's",
    "@prostetsofa": "stays in watch, recorded: its group admits by approval only. No watch join"
    " happens in this phase; this surfaces when the channel wakes up",
}

GATED_LATE = {
    "@marketopt_promo": "replaces the withdrawn late addition (operator, 2026-08-07)",
    "@akcii_skidki_plt": "late addition #2, a Poltava deals aggregator (canon 'Дозаявка №2')",
}
LATE_RULE = (
    "PASS with an open discussion group → comments bucket and the joins list; PASS without one →"
    " posts-only; FAIL or FLAG → stop and report before any further action on it."
)
"""The operator's routing rule for a late addition, written before its gate and applied after."""

SOURCE_TYPE_RULING = {
    "@uasaler": "aggregator",
    "@znishkom": "aggregator",
    "@whitecode_zny": "aggregator",
    "@atb_aktsiyi": "aggregator",
    "@ATB_FANatik": "aggregator",
    "@epicentrk_sale": "official_retail",
    "@dpssgovua": "government",
    # Operator amendment 2026-08-07, after the write: the ruling's "community — the rest" was
    # written while this channel was still at the gate, and it is the promo channel of the
    # Poltava/Kremenchuk chain whose official page the same ruling put in official_retail.
    "@marketopt_promo": "official_retail",
}
"""Team-lead ruling 2026-08-07; everything else is `community`, the ruling's own default."""


def final_bucket(row: dict) -> tuple[str | None, str | None]:
    """The bucket a channel enters the registry in, and the ruling that put it there.

    ``None`` means it does not enter. The replacement's bucket is not a ruling but a rule the
    operator wrote in advance, resolved against what the gate then measured.
    """
    handle, verdict = row["handle"], row["verdict"]
    if handle in EXCLUDED:
        return None, f"EXCLUDED — {EXCLUDED[handle]}"
    if handle in MOVED:
        bucket, text = MOVED[handle]
        return bucket, f"KEPT, bucket changed — {text}"
    if handle in GATED_LATE:
        if verdict != "PASS":
            raise SystemExit(
                f"{handle} came back {verdict}, and the operator's rule is to stop and report"
                f" before any further action on it. {LATE_RULE}"
            )
        group = row["checks"].get("discussion_group") or {}
        bucket = "comments" if group.get("open") else "posts"
        why = "an open discussion group" if group.get("open") else "no discussion group"
        return (
            bucket,
            f"LATE ADDITION — {GATED_LATE[handle]}; PASS with {why} → {bucket}. {LATE_RULE}",
        )
    if handle in KEPT:
        return row["bucket"], f"KEPT — {KEPT[handle]}"
    if verdict != "PASS":
        raise SystemExit(f"{handle} is {verdict} and no ruling covers it — refusing to guess")
    return row["bucket"], None


def source_entry(row: dict, bucket: str) -> dict:
    """One registry source, built from the gate's own measurement.

    `name` is the title Telegram returned at the gate, not the canon table's truncated cell:
    the record is the artifact, the table is a reading of it. `verified: true` is this
    registry's meaning of the word — the entry check passed — not Telegram's blue check, which
    most of these channels do not carry.
    """
    handle = row["handle"]
    return {
        "id": handle[1:].lower(),
        "name": row["checks"]["title"],
        "source_type": SOURCE_TYPE_RULING.get(handle, "community"),
        "telegram_channels": [handle],
        "verified": True,
        # The gate's group finding, except where a ruling overrode it (@maudau).
        "comments_enabled": bucket != "posts" and bool(row["checks"].get("discussion_group")),
        "watch": bucket == "watch",
    }


def render(entry: dict) -> str:
    """A YAML block in the file's own style. `json.dumps` doubles as a YAML string quoter."""
    lines = [
        f"  - id: {entry['id']}",
        f"    name: {json.dumps(entry['name'], ensure_ascii=False)}",
        f"    source_type: {entry['source_type']}",
        "    telegram_channels:",
        *[f"      - {json.dumps(channel)}" for channel in entry["telegram_channels"]],
        f"    verified: {str(entry['verified']).lower()}",
        f"    comments_enabled: {str(entry['comments_enabled']).lower()}",
    ]
    if entry["watch"]:
        lines.append("    watch: true")
    return "\n".join(lines)


def insert_sources(text: str, entries: list[dict]) -> str:
    """Put the new sources at the end of the `sources:` block and touch nothing else.

    Nothing to add means the file is already right, and returning it unchanged is the whole
    answer: an earlier version appended the section header anyway, so a re-run that added no
    source still dirtied the registry with a duplicate comment block.
    """
    if not entries:
        return text
    marker = "\ntaxonomy:\n"
    if marker not in text:
        raise SystemExit(f"{REGISTRY}: no `taxonomy:` block — refusing to guess where sources end")
    head, tail = text.split(marker, 1)
    block = "\n".join(render(entry) for entry in entries)
    return f"{head.rstrip()}\n\n{HEADER}\n{block}\n{marker}{tail}"


HEADER = """  # --- Phase 5c1 launch composition (operator verdict 2026-08-06, rulings 2026-08-07) ---
  # Every channel below entered through the track-R gate: results/entry_gate_5c1.json holds one
  # row per candidate with its checks, verdict and the ruling that placed it. Names and
  # comments_enabled come from that record, never typed here. `watch: true` = posts are
  # collected and the discussion group is NEVER joined until the channel posts again and the
  # operator says so (SPEC 3.11 (4)); those channels keep comments_enabled because the group
  # exists — the join is what they do not have."""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Apply the 5c1 gate rulings and write sources.")
    parser.add_argument("--plan", action="store_true", help="print the composition, write nothing")
    args = parser.parse_args(argv)

    record = json.loads(GATE_RECORD.read_text(encoding="utf-8"))
    before = load_registry(REGISTRY)
    held = {handle: source for source in before.sources for handle in source.telegram_channels}

    entries, buckets = [], {"comments": [], "posts": [], "watch": [], "excluded": []}
    for row in record["candidates"]:
        bucket, ruling = final_bucket(row)
        row["ruling"] = ruling
        if bucket is None:
            buckets["excluded"].append(row["handle"])
            continue
        buckets[bucket].append(row["handle"])
        expected = source_entry(row, bucket)
        if (existing := held.get(row["handle"])) is not None:
            # Written by an earlier run of this script. Re-derived and compared rather than
            # skipped on trust: if a ruling has changed since, the file is now wrong and saying
            # so is the whole point of running this again.
            drift = {
                field: (getattr(existing, field), expected[field])
                for field in ("name", "source_type", "comments_enabled", "watch")
                if getattr(existing, field) != expected[field]
            }
            if drift:
                raise SystemExit(
                    f"{row['handle']} is in the registry with different fields: {drift}"
                )
            continue
        entries.append(expected)

    for bucket, handles in buckets.items():
        print(f"{bucket:<10}{len(handles):>3}  {' '.join(handles)}")
    # `before.sources` already holds everything an earlier run wrote, so the four originals are
    # what is left once this composition is taken out of it — otherwise a re-run double-counts.
    entered = set(buckets["comments"]) | set(buckets["posts"]) | set(buckets["watch"])
    originals = sum(1 for src in before.sources if not entered & set(src.telegram_channels))
    print(
        f"\nlaunch {originals + len(buckets['comments']) + len(buckets['posts'])}"
        f" = registry {originals} + comments {len(buckets['comments'])}"
        f" + posts {len(buckets['posts'])} · watch {len(buckets['watch'])}"
        f" · excluded {len(buckets['excluded'])}"
    )
    joins = buckets["comments"]
    print(f"joins Deliverable 2 may make: {len(joins)}")
    if args.plan:
        return 0

    text = REGISTRY.read_text(encoding="utf-8")
    tail = text.split("\ntaxonomy:\n", 1)[1]
    REGISTRY.write_text(insert_sources(text, entries), encoding="utf-8")
    written = REGISTRY.read_text(encoding="utf-8")
    if written.split("\ntaxonomy:\n", 1)[1] != tail:
        raise SystemExit("taxonomy/watchlist changed — the write was supposed to be additive")

    after = load_registry(REGISTRY)
    if [s.id for s in after.sources][: len(before.sources)] != [s.id for s in before.sources]:
        raise SystemExit("the four existing sources moved or changed — refusing this write")
    if len(after.sources) != len(before.sources) + len(entries):
        raise SystemExit("source count does not match what was rendered")
    unknown = {s.source_type for s in after.sources} - set(SOURCE_TYPES)
    if unknown:
        raise SystemExit(f"unknown source_type written: {unknown}")

    record["registry_written"] = True
    record["rulings"] = {
        "applied_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "canon": CANON,
        "composition": {name: sorted(handles) for name, handles in buckets.items()},
        "counts": {
            "registry_before": len(before.sources),
            "comments": len(buckets["comments"]),
            "posts": len(buckets["posts"]),
            "watch": len(buckets["watch"]),
            "excluded": len(buckets["excluded"]),
            "sources_after": len(after.sources),
        },
        "joins_authorised": sorted(joins),
        "source_type_ruling": dict(SOURCE_TYPE_RULING),
        "note": (
            "The gate's rows are unchanged: an excluded channel was still measured, and its"
            " `ruling` is what says it is out. Registry names and comments_enabled are read off"
            " this record, not typed."
        ),
    }
    record["git"] = git_state(GATE_RECORD)
    GATE_RECORD.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"\nwrote {len(entries)} sources into config/registry.yaml; rulings into {GATE_RECORD.name}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
