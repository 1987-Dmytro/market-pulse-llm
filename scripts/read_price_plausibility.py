"""A $0 reading: which current-week unit prices sit far from their category's own middle, and why.

PHASE-ship-1 §2 «price-fix» asks for a listing, not a rule. **Nothing here is a product corridor**:
no shipped module imports this file, the export carries no threshold, and the screen keeps none.
The band below is the DIAGNOSTIC's own — it decides which rows a human looks at, and the answer to
each row is the leaflet page, never the band.

The reading calls `export_front_data`'s own `unit_price` and `on_the_current_week` and the
repository's one median (`aggregates.spread`), so a row is flagged on exactly the number the screen
publishes. For every flagged row it then names the file that BORE the figure: the stored answer of
the model that read the page, beside the page itself — which is the whole question the item asks
(a deterministic layer's defect is fixable; a misread page is the operator's decision).

    python3.11 scripts/read_price_plausibility.py            # the default band
    python3.11 scripts/read_price_plausibility.py --band 10  # «order of magnitude» literally
"""

import argparse
import glob
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "src"))

import export_front_data as efd  # noqa: E402
from market_pulse import aggregates  # noqa: E402

SCREEN = REPO / "results" / "promo_screen_data.json"
FRONT = REPO / "results" / "front_data.json"


def answers(row_ids: set[str]) -> dict[str, dict]:
    """The stored model answer behind each row — the first store that carries it, by row_id.

    The derived stores are local and gitignored; a row this cannot find is REPORTED as unfound
    rather than skipped, because "the answer file is not here" is itself the reading's answer.
    """
    found: dict[str, dict] = {}
    for path in sorted(glob.glob(str(REPO / "data" / "derived*" / "*position_rows" / "*.jsonl"))):
        for line in open(path, encoding="utf-8"):
            record = json.loads(line)
            if record.get("row_id") in row_ids and record["row_id"] not in found:
                found[record["row_id"]] = record | {"store": path}
    return found


def answered_object(record: dict) -> dict | str:
    """The one object of the model's JSON array this row was built from, or the failure as text."""
    content = (record.get("reply") or {}).get("content", "")
    body = content.strip().removeprefix("```json").removesuffix("```").strip()
    try:
        return json.loads(body)[record["ordinal"]]
    except Exception as failure:  # the answer is evidence even when it does not parse
        return f"<unreadable: {failure}> {body[:200]}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--band", type=float, default=3.0, help="flag x>band or x<1/band of median")
    options = parser.parse_args(argv)

    export = json.loads(SCREEN.read_text(encoding="utf-8"))
    front = json.loads(FRONT.read_text(encoding="utf-8"))
    week = efd.on_the_current_week(export, front["media"])

    groups: dict[tuple[str, str], list] = {}
    for position in week:
        reading = efd.unit_price(position)
        if reading is not None:
            groups.setdefault((position["item"]["category"], reading[0]), []).append(
                (reading[1], position)
            )

    flagged = []
    for key, members in sorted(groups.items()):
        middle = aggregates.spread([value for value, _ in members])["median"]
        for value, position in sorted(members, key=lambda member: member[0]):
            ratio = value / middle
            if ratio > options.band or ratio < 1 / options.band:
                flagged.append((key, middle, ratio, value, position))

    stored = answers({position["row_id"] for *_, position in flagged})
    print(f"# current-week positions {len(week)} · priced {sum(len(m) for m in groups.values())}")
    print(f"# band x{options.band:g} of the category x unit median — the diagnostic's own rule")
    for (category, unit), middle, ratio, value, position in flagged:
        item = position["item"]
        record = stored.get(position["row_id"])
        print(
            f"\n{position['row_id']}  {category} {unit}  {value:.2f} = x{ratio:.2f} of {middle:.2f}"
            f"\n  stored : price {position.get('promo_price')} size {item.get('size_value')}"
            f"{item.get('size_unit')} pack {item.get('pack_count')} — {item.get('line')}"
        )
        if record is None:
            print("  answer : NOT FOUND in any local derived store")
            continue
        print(f"  answer : {json.dumps(answered_object(record), ensure_ascii=False)}")
        print(f"  page   : {record.get('image_path')}   ({record['store']})")
    print(f"\n# flagged {len(flagged)} of {sum(len(m) for m in groups.values())} priced rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
