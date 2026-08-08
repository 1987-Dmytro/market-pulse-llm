#!/usr/bin/env python3
"""Per-source UA/RU post shares over the collected window ($0, offline, excludes nothing).

Canon: `docs/SPEC.md` §3.11 (4) "Language policy" (operator ruling 2026-08-08) — the composition
takes Ukrainian-language channels only, channel-level UA dominance of posts is an entry
requirement applied retroactively, and the shares are computed OFFLINE from the window already
collected. This script is the computing half and nothing else: it writes its own record, and no
source leaves the registry until the operator confirms the list.

The bars are NOT in this file's gift. They are written in
`results/language_census_5c1.preregistration.json` before any share existed, with their reasons,
and the constants below are checked against that file on every run — a threshold moved to make the
answer nicer would have to be moved there first, in writing, beside the original. The record cites
that file's sha256.

`market_pulse.langid.detect` is a heuristic built for stratifying comments, and this is the first
time it is pointed at posts. Two controls with their expected direction — @dpssgovua must read
Ukrainian, @offspringrus (excluded 07.08 as a Russian shop) must read Russian — decide whether the
verdict column is reportable at all.

    PYTHONPATH=src python3 scripts/language_census_5c1.py
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

from build_audit_pack import git_state  # noqa: E402

from market_pulse.langid import detect  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

REGISTRY = REPO_ROOT / "config" / "registry.yaml"
COLLECT_RECORD = REPO_ROOT / "results" / "collect_5c1.json"
PREREGISTRATION = REPO_ROOT / "results" / "language_census_5c1.preregistration.json"
STORE = REPO_ROOT / "data" / "raw" / "posts"
RECORD = REPO_ROOT / "results" / "language_census_5c1.json"

DOMINANCE = 0.70
MIN_DECIDABLE = 10
"""Pre-registered in PREREGISTRATION before the first share was computed; `check_preregistration`
refuses to run if these drift from it."""

CONTROLS = {"@dpssgovua": "ua", "@offspringrus": "ru"}
"""Known cases with their expected direction, stated before the run. @offspringrus is not a
registry source — it was excluded on 07.08 and its rows stayed in the store, which is exactly what
makes it a usable negative control."""

EXAMPLE_LIMIT = 3
EXAMPLE_CHARS = 160


def check_preregistration() -> str:
    """The constants must be the ones written down first. Returns the file's sha256."""
    raw = PREREGISTRATION.read_bytes()
    rule = json.loads(raw)["rule"]
    if (rule["dominance"], rule["min_decidable"]) != (DOMINANCE, MIN_DECIDABLE):
        raise SystemExit(
            f"the bars in this script ({DOMINANCE}, {MIN_DECIDABLE}) are not the ones registered in"
            f" {PREREGISTRATION.name} ({rule['dominance']}, {rule['min_decidable']}). Change that"
            " file first, keeping the original beside the move and saying why."
        )
    return hashlib.sha256(raw).hexdigest()


def window_since() -> str:
    """The window `collect_5c1.py` fixed on its first run — read back, never recomputed."""
    return json.loads(COLLECT_RECORD.read_text(encoding="utf-8"))["window"]["since"]


def posts_in_window(handle: str, since: str) -> list[dict]:
    path = STORE / f"{handle.lstrip('@')}.jsonl"
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue  # a damaged line is not a language; collect_5c1.json counts them
        if row.get("date", "") >= since:
            rows.append(row)
    return rows


def count_languages(posts: list[dict]) -> dict:
    """Every post's language, and the examples that let a human check the verdict."""
    counts = {"ua": 0, "ru": 0, "en": 0, "other": 0}
    examples = {"ua": [], "ru": []}
    for row in posts:
        text = (row.get("text") or "").strip()
        if not text:
            counts["other"] += 1  # no text at all: undecidable, and it is counted as such
            continue
        language = detect(text)
        counts[language] += 1
        if language in examples and len(examples[language]) < EXAMPLE_LIMIT:
            examples[language].append(" ".join(text.split())[:EXAMPLE_CHARS])
    return {"counts": counts, "examples": examples}


def verdict_for(counts: dict, posts: int) -> tuple[str, float | None, float | None]:
    """The pre-registered rule, and the two states it refuses to call a verdict."""
    decidable = counts["ua"] + counts["ru"]
    if posts == 0:
        return "NO_POSTS_IN_WINDOW", None, None
    if decidable < MIN_DECIDABLE:
        return "TOO_FEW_DECIDABLE", None, None
    ua_share = round(counts["ua"] / decidable, 3)
    ru_share = round(counts["ru"] / decidable, 3)
    if ua_share >= DOMINANCE:
        return "UA_DOMINANT", ua_share, ru_share
    if ru_share >= DOMINANCE:
        return "RU_DOMINANT", ua_share, ru_share
    return "MIXED", ua_share, ru_share


def census_row(source, handle: str, since: str) -> dict:
    posts = posts_in_window(handle, since)
    measured = count_languages(posts)
    counts = measured["counts"]
    verdict, ua_share, ru_share = verdict_for(counts, len(posts))
    decidable = counts["ua"] + counts["ru"]
    return {
        "handle": handle,
        "source_id": source.id,
        "audience": source.audience,
        "bucket": "watch" if source.watch else ("comments" if source.comments_enabled else "posts"),
        "posts_in_window": len(posts),
        "decidable": decidable,
        "counts": counts,
        # Reported beside every share: a source with 12 decidable posts out of 60 texted ones has
        # a share that clears the bar and still describes a fifth of what it posted.
        "undecidable_share": round((counts["en"] + counts["other"]) / len(posts), 3)
        if posts
        else None,
        "ua_share": ua_share,
        "ru_share": ru_share,
        "verdict": verdict,
        "ru_examples": measured["examples"]["ru"],
        "ua_examples": measured["examples"]["ua"],
    }


def run_controls(since: str) -> dict:
    """The detector's own exam, taken before it is allowed to rule on anything."""
    out = {}
    for handle, expected in CONTROLS.items():
        posts = posts_in_window(handle, since)
        counts = count_languages(posts)["counts"]
        decidable = counts["ua"] + counts["ru"]
        share = round(counts[expected] / decidable, 3) if decidable else None
        out[handle] = {
            "expected": expected,
            "posts_in_window": len(posts),
            "counts": counts,
            "share_of_expected_language": share,
            "ok": bool(decidable >= MIN_DECIDABLE and share is not None and share >= DOMINANCE),
        }
    return out


def summarise(rows: list[dict]) -> dict:
    by_verdict: dict[str, int] = {}
    by_audience: dict[str, dict[str, int]] = {}
    for row in rows:
        by_verdict[row["verdict"]] = by_verdict.get(row["verdict"], 0) + 1
        segment = by_audience.setdefault(row["audience"] or "—", {})
        segment[row["verdict"]] = segment.get(row["verdict"], 0) + 1
    return {"n": len(rows), "by_verdict": by_verdict, "by_audience": by_audience}


def sensitivity(rows: list[dict]) -> dict:
    """What other bars WOULD have said. Description only — the verdict is the registered bar."""
    out = {}
    for bar in (0.6, 0.7, 0.8, 0.9):
        counts = {"UA_DOMINANT": 0, "RU_DOMINANT": 0, "MIXED": 0}
        for row in rows:
            if row["ua_share"] is None:
                continue
            if row["ua_share"] >= bar:
                counts["UA_DOMINANT"] += 1
            elif row["ru_share"] >= bar:
                counts["RU_DOMINANT"] += 1
            else:
                counts["MIXED"] += 1
        out[f"dominance_{bar}"] = counts
    return out


def print_table(rows: list[dict]) -> None:
    header = (
        f"{'channel':<30}{'bucket':<9}{'audience':<18}{'posts':>6}{'dec':>5}"
        f"{'ua':>7}{'ru':>7}{'undec':>7}  verdict"
    )
    print(f"\n{header}\n{'-' * len(header)}")
    for row in rows:
        share = lambda value: f"{value:.2f}" if value is not None else "—"  # noqa: E731
        print(
            f"{row['handle'][:29]:<30}{row['bucket']:<9}{(row['audience'] or '—')[:17]:<18}"
            f"{row['posts_in_window']:>6}{row['decidable']:>5}"
            f"{share(row['ua_share']):>7}{share(row['ru_share']):>7}"
            f"{share(row['undecidable_share']):>7}  {row['verdict']}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=RECORD, help="where to write the record")
    args = parser.parse_args(argv)
    if args.out == RECORD and RECORD.exists():
        raise SystemExit(
            f"{RECORD.relative_to(REPO_ROOT)} already exists and is the evidence behind wave 3:"
            " @retsepty5 (ru 1.00 over 139 posts), @retsepty4 (115), @katyal55 (36) and"
            " @tretyakovaele left the registry on the strength of those rows, so a re-run over"
            " today's composition writes a table that CANNOT contain them. The census re-derives"
            " from the windows, but only for sources that are still in the registry — which is"
            " exactly the half a ruling never cites. Pass --out with another path."
        )

    registered = check_preregistration()
    since = window_since()
    registry = load_registry(REGISTRY)

    rows = [
        census_row(source, handle, since)
        for source in registry.sources
        for handle in source.telegram_channels
    ]
    # The brief asks for a table sorted by RU share. A source without a share has no place in that
    # order and is not silently ranked as zero: those sort last, loudest first by post count.
    ranked = sorted(
        rows,
        key=lambda r: (r["ru_share"] is None, -(r["ru_share"] or 0), -r["posts_in_window"]),
    )
    controls = run_controls(since)
    reportable = all(control["ok"] for control in controls.values())

    record = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "phase": "5c1 addendum 8",
        "asks": (
            "per registry source, the UA and RU shares of its own posts in the collected window,"
            " and the pre-registered verdict on them"
        ),
        "contract": "docs/SPEC.md §3.11 (4) 'Language policy' (operator ruling 2026-08-08)",
        "preregistration": {
            "path": str(PREREGISTRATION.relative_to(REPO_ROOT)),
            "sha256": registered,
            "dominance": DOMINANCE,
            "min_decidable": MIN_DECIDABLE,
        },
        "window": {
            "since": since,
            "source": "data/raw/posts/, the window of results/collect_5c1.json",
        },
        "read_only": "no registry edit, no store write, no exclusion, no Telegram — the operator"
        " confirms the list before anything leaves",
        "detector": {
            "module": "market_pulse.langid.detect",
            "note": "a heuristic built to stratify comments, validated here against two controls"
            " before its verdicts are read",
        },
        "controls": controls,
        "verdicts_reportable": reportable,
        "summary": summarise(rows),
        "sensitivity_description_only": sensitivity(rows),
        "sources": ranked,
        "git": git_state(args.out),
    }
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print_table(ranked)
    summary = record["summary"]
    print(
        f"\n{summary['n']} sources · "
        + " · ".join(f"{k} {v}" for k, v in summary["by_verdict"].items())
    )
    for handle, control in controls.items():
        mark = "OK" if control["ok"] else "FAILED"
        print(
            f"control {handle:<16}expects {control['expected']}, measured"
            f" {control['share_of_expected_language']} over {control['counts']} — {mark}"
        )
    shown = args.out.relative_to(REPO_ROOT) if args.out.is_relative_to(REPO_ROOT) else args.out
    print(f"\nwrote {shown}")
    if not reportable:
        print(
            "STOP: a control came back against its expectation, so the verdict column is not"
            " reportable. The counts are in the record; the detector is what needs answering for."
        )
        return 1
    print("EXCLUDES NOTHING: the operator confirms this list before any source leaves.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
