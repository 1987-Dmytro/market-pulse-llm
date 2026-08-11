#!/usr/bin/env python3
"""30 pre-filtered text rows for the team lead to triage and the operator to adjudicate (sku-a 4(b)).

The 4.5f pattern: a semicolon CSV the operator opens in a spreadsheet, a Russian README beside it, and
a committed manifest that pins both shas and the ids. The pack itself lives under
`data/annotation/**` and is gitignored — paid or hand-made annotation never enters git, so the
manifest is the only committed witness to what was asked.

**Nothing is proposed.** The five tick columns ship blank, and the tier is computed from them by
`positions.tier_from_presence` — the SAME function that tiers a model's answer. Bar 3 of SPEC
3.17 (6) compares those two, so if the ladder moved between this build and the pilot the gold would
move with it and nothing downstream could see it. That is why the manifest pins
`positions.ladder_sha256()` and `results/sku_pilot_prereg.json` cites the same value.

The draw is seed 42 over `results/sku_prefilter_census.json`'s frame, re-derived and hash-checked
before anything is written: a pack drawn from a frame nobody can reproduce is not a sample.

    PYTHONPATH=src python3 scripts/build_sku_text_pack.py

Refuses to overwrite a pack whose ticks are being filled in (`--force` overrides, and says what it
destroyed).
"""

import argparse
import csv
import hashlib
import json
import random
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_audit_pack import git_state  # noqa: E402

from market_pulse import positions  # noqa: E402

CENSUS = REPO_ROOT / "results" / "sku_prefilter_census.json"
PACK = REPO_ROOT / "data" / "annotation" / "sku_a_text" / "text30.csv"
README = PACK.parent / "README-text30.md"
MANIFEST = REPO_ROOT / "results" / "sku_text_pack_manifest.json"

SEED = 42
DRAW = 30
DELIMITER = ";"
GIVEN = ("id", "channel", "carrier", "date", "hit", "pattern", "text")
TICKS = tuple(positions.wire_key(field) for field in positions.PRESENCE_FIELDS)
"""The tick COLUMNS — the dairy instruments' wire names, not the schema's.

SPEC 3.17 (8) renamed the schema's fifth presence field `fat` → `attribute`; the pack on disk was
built and adjudicated under `fat`, `data/annotation/**` is gitignored so there is no HEAD to restore
it from, and this manifest is the only committed witness to what was asked. A column list that
followed the schema would rebuild the header, read every filled tick as blank — `filled()` is what
stands between a rebuild and 26 adjudicated rows — and describe a CSV nobody has."""
COLUMNS = (*GIVEN, *TICKS, "notes")
TICK_VALUES = ("y", "")

README_TEXT = """# 30 текстовых строк — размечает оператор (sku-a, вопрос 7)

Это НЕ разметка тональности. Вопрос один: **что именно называет эта строка о товаре?**
Из твоих галочек код сам считает ярус (`position` / `product_mention` / `brand_mention`) —
руками ярус не пишем, это правило SPEC 3.17 (2).

## Что делать

По каждой строке смотри колонку `text` и ставь **`y`** в тех колонках, что строка реально
называет. Пустая ячейка = «не названо». Всего пять колонок:

| колонка | ставь `y`, если строка называет |
|---|---|
| `brand` | торговую марку («Рудь», «Своя Лінія», ТМ «Молокія») |
| `line` | название линейки/продукта рядом с маркой («Золотий Каштан», «Пломбір») |
| `category` | вид товара из нашей таксономии (молоко, кефір, сир, масло, сметана, йогурт, морозиво…) |
| `size` | объём/вес («450 г», «0,5 л», «1 кг») |
| `fat` | жирность («2,5%», «82,5%») |

**Если строка вообще не про товар нашей категории — оставь ВСЕ пять пустыми** и, если хочешь,
напиши слово в `notes`. Это нормальный и важный ответ: такие строки показывают, сколько
мусора пропускает префильтр, и это отдельное измерение.

Если в строке несколько товаров — размечай **самый подробно описанный** из них
(правило: ярус строки = максимум по её позициям). Остальное можно упомянуть в `notes`.

## Правила формата

- Разделитель `;`. Значения только `y` или пусто — ничего другого валидатор не примет.
- **Не трогай** колонки `id`, `channel`, `carrier`, `date`, `hit`, `pattern`, `text` — по ним
  пакет сверяется с манифестом `results/sku_text_pack_manifest.json`.
- Ничего не предзаполнено специально: подсказанный ярус — это уже не независимая разметка.

## Что это решает

Это ground truth для планки **«точность яруса ≥ 0.85»** (SPEC 3.17 (6)), которую пилот sku-b
будет мерить одной попыткой. `hit` и `pattern` показаны как справка: это то, за что строку
поймал детерминированный префильтр, а не предложение ответа.
"""


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def frame_from_census(census: Path) -> tuple[dict, list[dict]]:
    """The census's frame, with its own hash re-derived before a single row is drawn.

    A pack whose frame cannot be reproduced is not a sample, and the census refuses to be re-run
    over a moved corpus for the same reason. Both checks are cheap and both are here.
    """
    record = json.loads(census.read_text(encoding="utf-8"))
    rows = record["rows"]
    ids = [row["id"] for row in rows]
    digest = hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest()
    if digest != record["frame"]["ids_sha256"]:
        raise SystemExit(
            f"{rel(census)}: its rows hash to {digest[:16]}… and it pins"
            f" {record['frame']['ids_sha256'][:16]}… — the frame in the file is not the frame it"
            " describes, so a draw from it says nothing"
        )
    if len(set(ids)) != len(ids):
        raise SystemExit(f"{rel(census)}: an id appears twice, so one id does not select one row")
    return record, rows


def store_text(row: dict) -> str:
    """The row's text, read back from the raw store rather than copied from the census.

    The census keeps the matched LINE as evidence; the adjudicator needs the whole row, because the
    tier is about what the row names and a line is a fragment of it.
    """
    handle, msg_id = row["id"].rsplit(":", 1)
    folder = REPO_ROOT / "data" / "raw" / ("posts" if row["carrier"] == "post_text" else "comments")
    path = folder / f"{handle.lstrip('@')}.jsonl"
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        stored = json.loads(line)
        if stored["msg_id"] == int(msg_id):
            return " ".join((stored.get("text") or "").split())
    raise SystemExit(f"{row['id']}: the frame names a row {rel(path)} does not carry")


def draw(rows: list[dict], seed: int = SEED, size: int = DRAW) -> list[dict]:
    """A seeded sample over the frame in the census's own order.

    `random.Random(seed).sample` over a fixed order, so the draw is reproducible from the record.
    Deliberately NOT stratified by carrier: the contract says "seed-42 sample of 30 pre-filtered
    rows", and comments are 52 of the 769 rows — so the pack inherits that proportion and the
    manifest reports it. Making the comment leg visible would be a different sample answering a
    different question, and that is a team-lead ruling, not a builder's default.
    """
    if len(rows) < size:
        raise SystemExit(f"the frame has {len(rows)} rows and the draw is {size}")
    return random.Random(seed).sample(rows, size)


def filled(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=DELIMITER)
        return sum(1 for row in reader if any((row.get(tick) or "").strip() for tick in TICKS))


def write_csv(path: Path, rows: list[dict]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=COLUMNS, delimiter=DELIMITER, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    return sha256_of(path)


def given_sha256(rows: list[dict]) -> str:
    """A hash of the columns the operator must not touch — what the validator re-checks.

    The whole-file sha moves the moment a tick is entered, which is the point of the pack; this one
    covers the question and stands still while the answer is written.
    """
    payload = json.dumps(
        [{key: row[key] for key in GIVEN} for row in rows],
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--census", type=Path, default=CENSUS)
    parser.add_argument("--pack", type=Path, default=PACK)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--force", action="store_true", help="overwrite a pack being filled in")
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="rebuild the manifest from the same draw, leaving the pack on disk untouched",
    )
    args = parser.parse_args(argv)

    if (already := filled(args.pack)) and not (args.force or args.manifest_only):
        raise SystemExit(
            f"{rel(args.pack)} already carries ticks on {already} row(s) — rebuilding would destroy"
            " an evening of adjudication, and this directory is gitignored so there is no HEAD to"
            " restore from. --force if that is really what you want."
        )

    census, frame = frame_from_census(args.census)
    drawn = draw(frame)
    rows = [
        {
            "id": row["id"],
            "channel": row["channel"],
            "carrier": row["carrier"],
            "date": row["date"],
            "hit": row["hit"],
            "pattern": row["pattern"],
            "text": store_text(row),
            **dict.fromkeys(TICKS, ""),
            "notes": "",
        }
        for row in drawn
    ]
    rows.sort(key=lambda row: (row["carrier"], row["channel"], row["id"]))

    readme = args.pack.with_name(README.name)
    if args.manifest_only:
        # the ladder's sha is an INPUT to bar 3 and it moved with SPEC 3.17 (8)'s rename, so the
        # manifest has to be rebuilt — but the pack it describes is adjudicated and gitignored, and
        # `write_csv` would blank 26 rows of answers. The CSV is re-derived into a temp file for its
        # sha instead: same draw, same columns, so the sha the manifest pins is still the pack AS
        # BUILT and is still checkable against the one this run would have written.
        if readme.exists() and readme.read_text(encoding="utf-8") != README_TEXT:
            raise SystemExit(
                f"{rel(readme)} on disk is not what this script writes — a manifest rebuilt over it"
                " would pin a README nobody has"
            )
        with tempfile.TemporaryDirectory() as tmp:
            pack_sha = write_csv(Path(tmp) / args.pack.name, rows)
    else:
        pack_sha = write_csv(args.pack, rows)
        readme.write_text(README_TEXT, encoding="utf-8")

    by_carrier = {
        carrier: sum(1 for row in rows if row["carrier"] == carrier)
        for carrier in positions.CARRIERS
        if any(row["carrier"] == carrier for row in rows)
    }
    manifest = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "phase": "sku-a — the text leg's adjudication pack",
        "contract": "docs/PROMPT-sku-a.md deliverable 4(b); docs/SPEC.md amendment 3.17 (6)",
        "pack": rel(args.pack),
        "readme": rel(readme),
        "gitignored": (
            "data/annotation/** is gitignored, so this manifest is the only committed witness to"
            " what was asked. `git status` proves nothing about the pack itself"
        ),
        "rows": len(rows),
        "columns": list(COLUMNS),
        "delimiter": DELIMITER,
        "to_fill": list(TICKS),
        "tick_values": list(TICK_VALUES),
        "nothing_is_proposed": (
            "every tick column ships blank. A suggested tier is not independent adjudication, and"
            " the ladder is code's either way (SPEC 3.17 (2))"
        ),
        "ladder": {
            "function": "market_pulse.positions.tier_from_presence",
            "sha256": positions.ladder_sha256(),
            "why": (
                "bar 3 compares an adjudicated tier against a model's tier and BOTH come out of"
                " positions.tier. A ladder that moved between this build and the pilot would move"
                " the gold silently, so its 32-row table is hashed here and"
                " results/sku_pilot_prereg.json cites the same value"
            ),
            "table": positions.ladder_table(),
        },
        "draw": {
            "seed": SEED,
            "size": DRAW,
            "rule": (
                "random.Random(42).sample over the census frame in the record's own order. NOT"
                " stratified: the contract says a seed-42 sample of 30 pre-filtered rows, and the"
                " pack inherits the frame's carrier proportion"
            ),
            "frame": {
                "path": rel(args.census),
                "sha256": sha256_of(args.census),
                "rows": census["frame"]["rows"],
                "ids_sha256": census["frame"]["ids_sha256"],
            },
            "by_carrier": by_carrier,
            "carrier_share_of_the_frame": {
                carrier: cell["passed"] for carrier, cell in census["frame"]["by_carrier"].items()
            },
            "comment_leg_note": (
                "comments are 52 of the frame's 769 rows, so a proportional draw of 30 holds a"
                " handful. Bar 3 therefore prices the POST leg; whether the comment carrier needs a"
                " bar of its own is a team-lead ruling and is flagged in the pre-registration"
            ),
        },
        "sha256": {rel(args.pack): pack_sha, rel(readme): sha256_of(readme)},
        "csv_sha_note": (
            "the CSV's sha above is the pack AS BUILT and is expected to move on the first tick —"
            " that is what the pack is for. `given_sha256` is the one that must not: it covers only"
            " the columns the operator was told not to touch, so it stands still while the answer is"
            " written and `validate_sku_text_pack.py` re-checks it. The README's sha does not move"
            " either, because nothing is filled in there"
        ),
        "given_sha256": given_sha256(rows),
        "given_columns": list(GIVEN),
        "ids": [row["id"] for row in rows],
        "pattern_kinds": {
            kind: sum(1 for row in drawn if kind in row["pattern_kinds"])
            for kind in ("currency", "percent", "size")
        },
        "also_measures": (
            "the pre-filter's precision. A drawn row whose five ticks all come back empty names no"
            " position at all, which makes it a pre-filter false positive — the frame is dominated"
            " by recipe feeds (see results/sku_prefilter_census.json), and this pack is the only"
            " thing that prices that"
        ),
        "git": git_state(args.manifest),
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"{rel(args.pack)}  {len(rows)} rows · {pack_sha[:16]}…")
    print(f"  by carrier: {by_carrier}")
    print(f"  pattern kinds in the draw: {manifest['pattern_kinds']}")
    print(f"  ladder {positions.ladder_sha256()[:16]}… over {len(positions.ladder_table())} rows")
    print(f"  given columns hash {manifest['given_sha256'][:16]}…")
    if args.manifest_only:
        print(f"wrote {rel(args.manifest)} only — {rel(args.pack)} and its README were not touched")
    else:
        print(f"wrote {rel(args.manifest)} and {rel(readme)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
