#!/usr/bin/env python3
"""Stage-2 regional sentinel: who is named in the Poltava oblast's own channels ($0, no model).

PHASE-ship-1 §2 «region-collect» (iii), ruling (ggg). Reads the brand dictionary of
`config/region_brands.yaml` over the eighteen channels of `config/region_channels.yaml` — their
frozen v1 archive (`data/raw/`) UNION whatever `scripts/collect_region.py` has put in
`data/raw_region/` — and writes two files:

    results/region_mentions.jsonl   one row per mention: channel · msg_id · kind · date · brand ·
                                    quote (≤200 chars, the text around the match)
    results/region_baseline.json    the window's dates, per-channel post and comment counts, and
                                    the mentions per brand — ZERO included, because a zero IS the
                                    stage-2 baseline and the product's point of reference.

No model reads anything here: the matcher is `re`, and that is the whole instrument. A paid reading
of this field is stage 2's decision and stays post-gate.

`data/raw_r2/` is deliberately NOT read (ruling (ggg) 4): it carries the promo pipeline's
collection and no regional row, and a sentinel that walked it would count a promo channel's
comments into a regional baseline.

    PYTHONPATH=src python3.11 scripts/region_sentinel.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from market_pulse.raw_store import ARCHIVE_ROOT, RawStore  # noqa: E402

BRANDS_FILE = REPO_ROOT / "config" / "region_brands.yaml"
CHANNELS_FILE = REPO_ROOT / "config" / "region_channels.yaml"
REGION_ROOT = REPO_ROOT / "data" / "raw_region"
MENTIONS = REPO_ROOT / "results" / "region_mentions.jsonl"
BASELINE = REPO_ROOT / "results" / "region_baseline.json"

QUOTE_CHARS = 200
QUOTE_LEAD = 80
"""The quote is a window around the match, not the head of the post: a brand named in the fourth
sentence of a 900-character announcement would otherwise be quoted by text that does not contain
it."""

APOSTROPHES = "’ʼ‘´`"
"""The five spellings Telegram text actually carries for the Ukrainian apostrophe, folded onto the
ASCII one on BOTH sides of the comparison — «м'ясо», «м’ясо» and «мʼясо» are one word."""


def prepare(text: str) -> str:
    """The one normaliser both sides go through — and the string the quote is cut from.

    NFC first: a Telegram client may send «ї» as i + U+0308, and a dictionary typed in an editor
    sends the single code point. Unnormalised, the two never match and the miss is invisible.

    Case is NOT folded here, and that is the point. `str.casefold()` is not length-preserving
    (`ẞ` → `ss`, `İ` → `i̇`), so a match offset taken on a casefolded string and used to slice the
    original drifts by one character per such code point — a published quote that does not contain
    the brand it is evidence for. Matching is case-insensitive through `re.IGNORECASE` instead, on
    THIS string, and the quote is cut from THIS string: one text, one index space, no drift
    possible. (Measured before the change: 0 of 42 184 stored records change length under
    `casefold`, so the defect was latent rather than live — the fix removes the class.)
    """
    text = unicodedata.normalize("NFC", text)
    for mark in APOSTROPHES:
        text = text.replace(mark, "'")
    return text


def compile_names(display_names: list[str]) -> list[tuple[str, re.Pattern]]:
    r"""One bounded pattern per spelling, over the prepared text.

    The boundary is `(?<!\w)…(?!\w)`, which is NOT a stylistic variant of `\b`: it is the idiom
    `market_pulse.brands.find_watchlist_brands` already uses for exactly this job, and the two must
    not drift. It also behaves where `\b` cannot — the operator edits this dictionary freely and
    may add a spelling as the pack prints it («Гармонія®», «ТМ «Гармонія»»), and a trailing `\b`
    after `®` inverts to «the next character MUST be a word character», so such a spelling is
    loaded, listed, scanned for, and can never produce a hit.

    Bounded either way it is NOT stemmed: «миргородської корівки» is not a hit for «Миргородська
    корівка». PHASE §2 (iii) names word boundaries and that is what this is; the cost of the
    missing stemmer is measured in `docs/plans/ship-1.PROGRESS.md`, not quietly paid.
    """
    return [
        (name, re.compile(rf"(?<!\w){re.escape(prepare(name))}(?!\w)", re.IGNORECASE))
        for name in display_names
    ]


def load_brands(path: Path = BRANDS_FILE) -> list[dict]:
    """The dictionary, or a refusal by name — and the refusal happens BEFORE any output is opened.

    §2 (iii)'s second direction is «a dictionary naming no brands → exit ≠ 0, nothing written». A
    scan that truncated `region_mentions.jsonl` and then discovered it had nothing to look for
    would have destroyed the previous reading to report that it could not take a new one
    ([[a_rebuild_deletes_its_output_before_it_can_refuse]]).
    """
    if not path.exists():
        raise SystemExit(f"{path}: the brand dictionary is missing — nothing to watch for")
    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries = loaded.get("brands") or []
    # A brand with no spelling is REFUSED, not skipped. Skipped, it is absent from
    # `mentions_per_brand` entirely — and this file's whole product is a printed zero, so a brand
    # the operator added with a typo'd key would read as «not mentioned» when it was never looked
    # for. The two are different facts and only one of them is this file's answer.
    nameless = [
        entry.get("brand_id", "<no brand_id>")
        for entry in entries
        if not entry.get("display_names")
    ]
    if nameless:
        raise SystemExit(
            f"{path}: {', '.join(nameless)} carries no `display_names` — a brand with no spelling"
            " would be scanned for nothing and reported as a zero it never earned. Add the"
            " spellings or remove the block. Nothing written."
        )
    brands = [
        {
            "brand_id": entry["brand_id"],
            "own": bool(entry.get("own", False)),
            "names": compile_names(entry["display_names"]),
        }
        for entry in entries
    ]
    if not brands:
        raise SystemExit(
            f"{path}: no brand carries a display name — the sentinel would scan for nothing and"
            " report a zero that means «not looked for», not «not mentioned». Nothing written."
        )
    return brands


def load_channels(path: Path = CHANNELS_FILE) -> list[str]:
    """The handles, refusing a duplicate on the STORE KEY — the same refusal the collector makes.

    `scripts/collect_region.py :: side_channels` refuses a repeated handle because it would be one
    store file written twice; here the same repetition would scan one channel's rows twice and
    publish its posts, comments and mentions doubled in `region_baseline.json`. Two readers of one
    file, and the drift between them is the defect — so both compare the key the store actually
    uses (`@` stripped, case-insensitive, which is what `RawStore.path` and a case-insensitive
    filesystem resolve to), not the literal spelling.
    """
    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    handles = [entry["handle"] for entry in (loaded.get("channels") or [])]
    if not handles:
        raise SystemExit(f"{path}: no channel listed — nothing to scan. Nothing written.")
    keys = [one.lstrip("@").casefold() for one in handles]
    if len(set(keys)) != len(keys):
        doubled = sorted({key for key in keys if keys.count(key) > 1})
        raise SystemExit(
            f"{path}: {', '.join(doubled)} listed more than once — one channel's rows would be"
            " counted twice in the published baseline. Nothing written."
        )
    return handles


def quote_around(text: str, start: int, end: int) -> str:
    """`QUOTE_CHARS` of the PREPARED text around the match, on one line.

    `text` here is the same string the match offsets were taken on — see :func:`prepare`. A quote
    cut from a differently-indexed copy of the post is evidence that need not contain the brand it
    is evidence for.
    """
    head = max(0, start - QUOTE_LEAD)
    tail = min(len(text), max(end, head + QUOTE_CHARS))
    return " ".join(text[head:tail].split())


def mentions_in(record: dict, kind: str, brands: list[dict]) -> list[dict]:
    """Every (brand, spelling) that names this record, at most one row per brand.

    One row per brand and not per spelling: «Гармонія» and «ТМ Гармонія» are the same brand in the
    same sentence, and two rows would make one mention read as two in the baseline's count.
    """
    text = prepare(record.get("text") or "")
    if not text:
        return []
    out = []
    for brand in brands:
        for name, pattern in brand["names"]:
            found = pattern.search(text)
            if found is None:
                continue
            out.append(
                {
                    "channel": record["channel"],
                    "msg_id": record["msg_id"],
                    "kind": kind,
                    "date": record["date"],
                    "brand": brand["brand_id"],
                    "matched": name,
                    "quote": quote_around(text, found.start(), found.end()),
                }
            )
            break
    return out


def scan(handles: list[str], brands: list[dict]) -> tuple[list[dict], dict]:
    """The rows, and the per-channel counts the baseline publishes."""
    store = RawStore(REGION_ROOT, archives=(ARCHIVE_ROOT,))
    rows: list[dict] = []
    channels: list[dict] = []
    for handle in handles:
        counts = {"channel": handle, "posts": 0, "comments": 0, "mentions": 0}
        first = last = None
        for kind in ("post", "comment"):
            for record in store.rows(kind, handle):
                counts[f"{kind}s"] += 1
                date = record.get("date")
                if date:
                    first = min(first or date, date)
                    last = max(last or date, date)
                hits = mentions_in(record, kind, brands)
                counts["mentions"] += len(hits)
                rows.extend(hits)
        channels.append(counts | {"first_date": first, "last_date": last})
    return rows, {"channels": channels}


def rel(path: Path) -> str:
    """Repo-relative where that is what the path is, and honest about it where it is not.

    The baseline names the files it was read from, and a test drives this script against a fixture
    store outside the repo: `Path.relative_to` raises there, and a published record that cannot be
    written at all is worse than one that names an absolute path.
    """
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def baseline_of(
    rows: list[dict], brands: list[dict], scanned: dict, brands_path: Path, channels_path: Path
) -> dict:
    """Every brand gets a line, including the ones nothing named.

    The two input paths are ARGUMENTS, not the module's defaults: a reading taken over a different
    dictionary must say which dictionary it was ([[provenance_cannot_name_itself]] is the same
    shape — a record that names the file it «should» have read proves nothing about the run).
    """
    per_brand = {brand["brand_id"]: 0 for brand in brands}
    for row in rows:
        per_brand[row["brand"]] += 1
    dates = [one["first_date"] for one in scanned["channels"] if one["first_date"]]
    ends = [one["last_date"] for one in scanned["channels"] if one["last_date"]]
    return {
        "contract": "PHASE-ship-1 §2 «region-collect» (iii) — stage-2 regional baseline ($0)",
        "sources": {
            "channels": rel(channels_path),
            "brands": rel(brands_path),
            "roots": [rel(ARCHIVE_ROOT), rel(REGION_ROOT)],
        },
        "window": {
            "first_date": min(dates) if dates else None,
            "last_date": max(ends) if ends else None,
        },
        "totals": {
            "channels": len(scanned["channels"]),
            "posts": sum(one["posts"] for one in scanned["channels"]),
            "comments": sum(one["comments"] for one in scanned["channels"]),
            "mentions": len(rows),
        },
        "mentions_per_brand": per_brand,
        "channels": scanned["channels"],
    }


def write(rows: list[dict], baseline: dict, mentions_path: Path, baseline_path: Path) -> None:
    # BOTH parents before EITHER write: a baseline that fails on a missing directory after the
    # mentions file is already rewritten leaves the pair disagreeing, and the pair IS the
    # reading ([[a_crash_must_write_into_the_file_its_reader_opens]]).
    mentions_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    mentions_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )
    baseline_path.write_text(
        json.dumps(baseline, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def render(baseline: dict) -> str:
    lines = [
        f"window {baseline['window']['first_date']} .. {baseline['window']['last_date']}",
        f"{baseline['totals']['channels']} channels · {baseline['totals']['posts']} posts ·"
        f" {baseline['totals']['comments']} comments",
        "",
        f"{'brand':<24}{'mentions':>9}",
        "-" * 33,
    ]
    for brand, count in baseline["mentions_per_brand"].items():
        lines.append(f"{brand:<24}{count:>9}")
    lines += ["", f"{'channel':<22}{'posts':>7}{'comments':>10}{'mentions':>10}", "-" * 49]
    for one in baseline["channels"]:
        lines.append(
            f"{one['channel']:<22}{one['posts']:>7}{one['comments']:>10}{one['mentions']:>10}"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brands", type=Path, default=BRANDS_FILE)
    parser.add_argument("--channels", type=Path, default=CHANNELS_FILE)
    parser.add_argument("--mentions-out", type=Path, default=MENTIONS)
    parser.add_argument("--baseline-out", type=Path, default=BASELINE)
    args = parser.parse_args(argv)

    # Both inputs before either output: a refusal must leave the previous reading intact.
    brands = load_brands(args.brands)
    handles = load_channels(args.channels)

    rows, scanned = scan(handles, brands)
    baseline = baseline_of(rows, brands, scanned, args.brands, args.channels)
    write(rows, baseline, args.mentions_out, args.baseline_out)
    print(render(baseline))
    print(f"\n{rel(args.mentions_out)} · {rel(args.baseline_out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
