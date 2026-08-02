#!/usr/bin/env python3
"""The 14 rows the model would not label, for the operator to label himself (4.5f).

Four passes over the corpus left 14 rows without an `intents` field — 66 → 29 → 18
→ 14, the same ids coming back each time, so it is the model and not the transport.
They were deliberately not coerced to `[]`: 13 of the 14 carried `[]` under v1, and
handing the majority answer to the rows that are hardest to read is how the empty
class inflates itself.

So nothing is proposed here. `intents_v2` ships blank, the operator fills it, and
the rows stay on their v1 labels until he does.

What this refuses:

- **a list that names itself.** The 14 are derived as *source minus staged minus
  frozen* and then checked against the unusable ids the paid runs recorded. Two
  independent derivations, because "the ones that failed" is exactly the kind of
  set that quietly becomes "the ones I happened to collect".
- **a proposal.** Every `intents_v2` cell must be empty when the file is written.
- **overwriting an evening's work.** A micro-pack already carrying labels is not
  rebuilt without `--force`.
- **touching the sealed manifest.** This writes its own,
  `results/calib_45e_micro_manifest.json`.

    PYTHONPATH=src python3 scripts/build_micro_pack.py

Writes `data/annotation/calib_45e/unreadable14.csv` (semicolon-delimited, the
dialect the returns came back in) and its manifest.
"""

import argparse
import csv
import json
import sys
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))  # the staging convention lives there

import relabel_intents as relabel  # noqa: E402
from build_audit_pack import git_state  # noqa: E402

PACK = REPO_ROOT / "data" / "annotation" / "calib_45e" / "unreadable14.csv"
MANIFEST = REPO_ROOT / "results" / "calib_45e_micro_manifest.json"
RUN = REPO_ROOT / "results" / "relabel_45e.json"

COLUMNS = ("id", "text", "intents_v1", "intents_v2", "notes")
DELIMITER = ";"

README = """# 14 нечитаемых строк — размечает оператор

Модель четыре прохода подряд не отдавала поле `intents` для этих строк
(66 → 29 → 18 → 14, id повторялись — значит модель, не транспорт). К `[]` их не
приводили: 13 из 14 были `[]` в v1, и выдать таким строкам ответ большинства
означало бы раздуть именно тот класс, о котором спрашивает таксономия.

Заполни колонку **`intents_v2`** по гайдлайну v2 (шесть интенций, `service`
включён). `intents_v1` показан как справка — это старая метка, а не предложение.
Пустой набор `[]` — полноценный ответ. Формат ячейки: `["taste", "service"]`.

Разделитель `;`. Не трогай `id`, `text` и `intents_v1` — по ним пакет сверяется
с манифестом `results/calib_45e_micro_manifest.json`.

На гейт эти 14 строк не влияют: гейт ≥90% посчитан на сотне из `gated.csv`.
Пока колонка пуста, строки остаются на метках v1 и в `_tax2`-файлы не попадают.
"""


def unreadable(sources: dict[str, Path]) -> list[dict]:
    """Rows a source has and its staged copy does not, minus the ids this phase never asked."""
    forbidden = relabel.forbidden_ids()
    rows = []
    for name, source in sources.items():
        staged = {row["id"] for row in relabel.load(relabel.staged(source))[0]}
        for row in relabel.load(source)[0]:
            if row["id"] not in staged and row["id"] not in forbidden:
                rows.append({**row, "source": name})
    return rows


def recorded(run: Path) -> set[str]:
    """The ids the paid runs last reported unusable — the second derivation.

    Each resume pass re-asked only the rows still without an answer, so the *last*
    run per source is that source's residual and the earlier passes are history.
    """
    history = json.loads(run.read_text(encoding="utf-8"))
    last: dict[str, list] = {}
    for entry in history["runs"]:
        if entry.get("per_file"):  # the `--from-rows` re-derivation, which asked nothing
            continue
        last[entry["source"]] = entry["drift"]["unusable"]
    return {out["id"] for outcomes in last.values() for out in outcomes}


def as_label(intents: list[str]) -> str:
    return json.dumps(sorted(intents), ensure_ascii=False)


def write_csv(path: Path, rows: list[dict]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=COLUMNS, delimiter=DELIMITER, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    return sha256(path.read_bytes()).hexdigest()


def filled(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=DELIMITER)
        return sum(1 for row in reader if (row.get("intents_v2") or "").strip())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, default=PACK)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--run", type=Path, default=RUN)
    parser.add_argument("--force", action="store_true", help="overwrite a pack being filled in")
    args = parser.parse_args(argv)

    if not args.force and (already := filled(args.pack)):
        raise SystemExit(
            f"{relabel.rel(args.pack)} already carries {already} labels — rebuilding would"
            " destroy them. --force if that is really what you want."
        )

    rows = unreadable(relabel.SOURCES)
    ids = {row["id"] for row in rows}
    said = recorded(args.run)
    if ids != said:
        raise SystemExit(
            f"{len(ids)} rows are in a source but not in its staged copy, and the runs in"
            f" {relabel.rel(args.run)} name {len(said)} unusable. The two derivations disagree"
            f" on {sorted(ids ^ said)}, so neither says what this pack is."
        )

    sha = write_csv(
        args.pack,
        [
            {
                "id": row["id"],
                "text": row["text"],
                "intents_v1": as_label(row["intents"]),
                "intents_v2": "",
                "notes": "",
            }
            for row in rows
        ],
    )
    readme = args.pack.with_name("README-unreadable14.md")
    readme.write_text(README, encoding="utf-8")

    manifest = {
        "pack": relabel.rel(args.pack),
        "readme": relabel.rel(readme),
        "rows": len(rows),
        "columns": list(COLUMNS),
        "delimiter": DELIMITER,
        "to_fill": "intents_v2",
        "gated": False,
        "sha256": {
            relabel.rel(args.pack): sha,
            relabel.rel(readme): sha256(readme.read_bytes()).hexdigest(),
        },
        "ids": [row["id"] for row in rows],
        "carried_empty_under_v1": sum(1 for row in rows if not row["intents"]),
        "by_source": {
            name: sum(1 for row in rows if row["source"] == name) for name in relabel.SOURCES
        },
        "sources": {
            relabel.rel(path): sha256(path.read_bytes()).hexdigest()
            for path in relabel.SOURCES.values()
        },
        "staged": {
            relabel.rel(relabel.staged(path)): sha256(relabel.staged(path).read_bytes()).hexdigest()
            for path in relabel.SOURCES.values()
        },
        "note": (
            "The rows four paid passes could not read. Derived as source-minus-staged and"
            " cross-checked against the unusable ids in results/relabel_45e.json. Nothing is"
            " proposed: `intents_v2` ships blank, and until it comes back these rows keep their"
            " v1 labels and are absent from every `_tax2` file. This manifest is its own —"
            " results/calib_45e_manifest.json seals the gated pack and is never rewritten."
        ),
        "git": git_state(args.manifest),
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"{relabel.rel(args.pack)}  {len(rows)} rows · {sha[:16]}…")
    print(f"  by source: {manifest['by_source']}")
    print(f"  {manifest['carried_empty_under_v1']} of them carried [] under v1")
    print(f"  both derivations agree on the same {len(ids)} ids")
    print(f"wrote {relabel.rel(args.manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
