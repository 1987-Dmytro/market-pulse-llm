#!/usr/bin/env python3
"""The schema check every Opus returns file passes before it is read (SPEC 3.16).

A review session hands back one JSON row per pack item. This is what stands between
those rows and `scripts/read_opus_audit.py`, and it refuses rather than repairs:

- **the pack is the pack that went out.** Every returns file is checked against its
  own `pack_NN.md`'s sha256 in `results/opus_audit_manifest.json`. A pack edited
  after the session — a stray note, a fixed typo — means the rows were written
  against a different artifact than the one the manifest describes.
- **a row names an item of THAT pack.** An id from another pack is not a smaller
  defect than an invented one, and the two are reported apart: the first is a
  session that opened the wrong file, the second is a row about nothing.
- **one row per item.** Two rows for one id are not merged and the later one does
  not win: which of them is the reviewer's answer is not knowable from the file.
- **a brand is a brand_id.** The protocol tells the session to *list the watchlist
  brands*, not to emit ids, so a display name comes back as often as an id and both
  are accepted through the registry's own alias table. A string that is neither is
  refused rather than guessed at — the aggregate would silently lose it.
- **`n/a` where there is nothing to judge.** A poll transcription and a caption-less
  post have no image for a faithfulness verdict; the pack pre-fills `n/a` and this
  refuses anything else there. The other direction — a judgeable caption answered
  `n/a` — is counted as unjudged and reported, never refused: an honest refusal to
  rule is a finding, and charging for it would buy guesses.

    PYTHONPATH=src python3 scripts/validate_opus_returns.py

With no arguments it validates every `returns_NN.jsonl` in the pack directory and
prints the coverage table. Nothing is written to; the returns are the operator's.
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_opus_audit_packs import MANIFEST, PACK_DIR, digest, rel  # noqa: E402

from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

FIELDS = (
    "pack",
    "item",
    "watchlist_hits",
    "other_dairy_brands",
    "caption_verdict",
    "brands_visible_missed",
    "note",
)
"""Exactly the keys the pack's empty row shows. A row with more is a row whose extra
cell nothing reads; a row with fewer lost a question rather than answered it empty."""

VERDICTS = ("faithful", "partial", "wrong", "n/a")
BRAND_LISTS = ("watchlist_hits", "brands_visible_missed")
RETURNS = re.compile(r"^returns_(\d+)\.jsonl$")


def aliases(manifest: dict) -> dict[str, str]:
    """The registry's alias table, from the registry the packs were built against.

    Pinned, because the canon table printed at the top of every pack came out of that
    file: resolving a returned display name through a moved watchlist would answer a
    question the reviewer was never shown.
    """
    name = "config/registry.yaml"
    expected = manifest["pinned_inputs"].get(name)
    found = digest(REPO_ROOT / name)
    if expected and found != expected:
        raise SystemExit(
            f"{name}: sha256 {found[:16]}…, the manifest pins {expected[:16]}…. The canon table in"
            " the packs is that watchlist, so a returned display name cannot be resolved here."
        )
    return watchlist_aliases(load_registry(REPO_ROOT / name).watchlist)


def brand_of(value: str, table: dict[str, str], known: set[str]) -> str | None:
    """A returned brand as its `brand_id` — an id, or a display name through the table."""
    text = " ".join(str(value).split())
    if text in known:
        return text
    return table.get(text.casefold())


def pack_of(path: Path) -> str | None:
    match = RETURNS.match(path.name)
    return f"pack_{match.group(1)}" if match else None


def validate(manifest: dict, path: Path, table: dict[str, str]) -> tuple[list[dict], list[str]]:
    """One returns file's rows and everything wrong with it. Rows are only safe if empty defects."""
    defects: list[str] = []
    pack_id = pack_of(path)
    if pack_id is None:
        return [], [f"{rel(path)}: not named returns_NN.jsonl, so it names no pack"]
    packs = {entry["pack"]: entry for entry in manifest["packs"]}
    if pack_id not in packs:
        return [], [f"{rel(path)}: the manifest has no {pack_id}"]
    pack_file = REPO_ROOT / packs[pack_id]["path"]
    if not pack_file.exists():
        defects.append(f"{packs[pack_id]['path']}: missing — the rows cannot be checked against it")
    elif (found := digest(pack_file)) != packs[pack_id]["sha256"]:
        defects.append(
            f"{packs[pack_id]['path']}: sha256 {found[:16]}…, the manifest pins"
            f" {packs[pack_id]['sha256'][:16]}…. The pack moved after it went out, so these rows"
            " were written against a different artifact"
        )

    items = {entry["item"]: entry for entry in manifest["items"]}
    mine = {item for item, entry in items.items() if entry["pack"] == pack_id}
    known = {brand_id for brand_id in table.values()}
    rows, seen = [], set()
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        where = f"{rel(path)}:{number}"
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            defects.append(
                f"{where}: not JSON ({error.msg}). An unreadable row is not an empty one"
            )
            continue
        if not isinstance(row, dict):
            defects.append(f"{where}: {type(row).__name__}, not an object")
            continue
        if missing := [field for field in FIELDS if field not in row]:
            defects.append(f"{where}: missing {missing}")
            continue
        if extra := sorted(set(row) - set(FIELDS)):
            defects.append(f"{where}: unknown field(s) {extra} — nothing reads them")
            continue
        if row["pack"] != pack_id:
            defects.append(f"{where}: says pack {row['pack']!r} in {path.name}")
            continue
        item = row["item"]
        if item not in mine:
            defects.append(
                f"{where}: item {item!r} is {'in ' + items[item]['pack'] if item in items else 'in'}"
                f"{'' if item in items else ' no pack in the manifest'}, not {pack_id}"
            )
            continue
        if item in seen:
            defects.append(
                f"{where}: {item} answered twice. Which row is the verdict is not knowable here"
            )
            continue
        seen.add(item)

        entry = items[item]
        clean, bad = {}, False
        for field in BRAND_LISTS:
            if not isinstance(row[field], list):
                defects.append(f"{where}: {field} is {type(row[field]).__name__}, not a list")
                bad = True
                continue
            resolved = []
            for value in row[field]:
                brand_id = brand_of(value, table, known) if isinstance(value, str) else None
                if brand_id is None:
                    defects.append(
                        f"{where}: {field} names {value!r}, which is neither a brand_id nor a"
                        " display name on the canon table. An open-extraction find belongs in"
                        " other_dairy_brands"
                    )
                    bad = True
                    continue
                resolved.append(brand_id)
            clean[field] = sorted(set(resolved))
        if not isinstance(row["other_dairy_brands"], list) or any(
            not isinstance(value, str) or not value.strip() for value in row["other_dairy_brands"]
        ):
            defects.append(f"{where}: other_dairy_brands must be a list of non-empty strings")
            bad = True
        if not isinstance(row["note"], str):
            defects.append(f"{where}: note must be a string")
            bad = True
        verdict = row["caption_verdict"]
        if verdict not in VERDICTS:
            defects.append(f"{where}: caption_verdict {verdict!r} is not one of {list(VERDICTS)}")
            bad = True
        elif not entry["judgeable_caption"] and verdict != "n/a":
            defects.append(
                f"{where}: caption_verdict {verdict!r} on an item with no model caption over"
                " sha-matched images. The pack pre-filled n/a there — there is nothing for the"
                " caption to be faithful to"
            )
            bad = True
        if not entry["images"]["named"] and clean.get("brands_visible_missed"):
            defects.append(
                f"{where}: brands_visible_missed on an item with no image. Nothing is visible here"
            )
            bad = True
        if bad:
            continue
        rows.append(
            {
                "pack": pack_id,
                "item": item,
                "channel": entry["channel"],
                "strata": entry["strata"],
                **clean,
                "other_dairy_brands": [
                    " ".join(value.split()) for value in row["other_dairy_brands"]
                ],
                "caption_verdict": verdict,
                "note": row["note"].strip(),
            }
        )
    return rows, defects


def coverage(manifest: dict, pack_id: str, rows: list[dict]) -> dict:
    """What the file answered, what it left, and what it declined to rule on.

    The four are reported apart on purpose: a pack nobody ran and a pack whose every
    caption came back `n/a` are the same number of judgements and completely different
    facts, and «rows returned» alone cannot tell them apart.
    """
    items = [entry for entry in manifest["items"] if entry["pack"] == pack_id]
    answered = {row["item"] for row in rows}
    judgeable = {entry["item"] for entry in items if entry["judgeable_caption"]}
    return {
        "pack": pack_id,
        "items": len(items),
        "rows": len(rows),
        "unanswered": sorted(entry["item"] for entry in items if entry["item"] not in answered),
        "captions_judgeable": len(judgeable),
        "captions_judged": sum(
            1 for row in rows if row["item"] in judgeable and row["caption_verdict"] != "n/a"
        ),
        "captions_declined": sorted(
            row["item"]
            for row in rows
            if row["item"] in judgeable and row["caption_verdict"] == "n/a"
        ),
    }


def collect(
    manifest: dict, paths: list[Path]
) -> tuple[dict[str, list[dict]], list[str], list[dict]]:
    table = aliases(manifest)
    by_pack, defects, covered = {}, [], []
    for path in paths:
        rows, found = validate(manifest, path, table)
        defects += found
        if found:
            continue
        by_pack[pack_of(path)] = rows
        covered.append(coverage(manifest, pack_of(path), rows))
    return by_pack, defects, covered


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--pack", type=Path, default=PACK_DIR)
    parser.add_argument("returns", type=Path, nargs="*", help="default: every returns_NN.jsonl")
    args = parser.parse_args(argv)

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    paths = args.returns or sorted(args.pack.glob("returns_*.jsonl"))
    if not paths:
        print(f"no returns files in {rel(args.pack)} yet — nothing to validate")
        return 0

    _, defects, covered = collect(manifest, list(paths))
    header = f"{'pack':<10}{'items':>6}{'rows':>6}{'unanswered':>12}{'judgeable':>11}{'judged':>8}{'declined':>10}"
    print(header)
    print("-" * len(header))
    for entry in covered:
        print(
            f"{entry['pack']:<10}{entry['items']:>6}{entry['rows']:>6}"
            f"{len(entry['unanswered']):>12}{entry['captions_judgeable']:>11}"
            f"{entry['captions_judged']:>8}{len(entry['captions_declined']):>10}"
        )
    if defects:
        print(f"\n{len(defects)} defect(s) — these files are not readable:")
        for defect in defects:
            print(f"  {defect}")
        return 1
    print(f"\n{len(covered)} file(s) validate. Nothing here is a measurement (SPEC 3.16 (1)).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
