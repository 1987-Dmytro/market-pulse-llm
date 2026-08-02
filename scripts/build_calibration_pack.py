#!/usr/bin/env python3
"""The calibration pack the taxonomy-v2 re-label is accepted or rejected on (4.5e).

SPEC §8 gates a label set on **≥90% agreement**, measured by re-reading a random 100
rows. This builds those 100 — drawn from the rows a gate actually scores, per the
4.5d gate's own reading — plus 50 changed rows as a diagnostic stratum that is not
gated and cannot move the verdict.

What the pack refuses:

- **the denominator is pre-registered, here, before a single verdict comes back.**
  Agreement is `correct` divided by the full sample. A blank cell, or any other
  value, counts against the bar. Deciding what to do with an awkward cell after
  seeing it is how a 0.88 becomes a 0.91.
- **nothing in the gated file says whether a row changed.** No column, no ordering:
  the sample is drawn and presented in seeded random order, and an operator who
  could see which rows the model had moved would be judging the move and not the
  label.
- **the two strata are disjoint.** The diagnostic shows the old label beside the new
  one; a row that appeared in both files would have its gated verdict contaminated
  by the framing of the other.
- **a pack with verdicts in it is not regenerable.** `--force` exists and destroys
  an evening's work, exactly as it does in `build_audit_pack.py`.

    python3.11 scripts/build_calibration_pack.py

Writes `data/annotation/calib_45e/` (gitignored, like every pack) and the committed
manifest `results/calib_45e_manifest.json`, which pins each file's sha256.
"""

import argparse
import csv
import json
import random
import sys
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import relabel_intents as relabel  # noqa: E402

PACK = REPO_ROOT / "data" / "annotation" / "calib_45e"
MANIFEST = REPO_ROOT / "results" / "calib_45e_manifest.json"

SEED = 42
GATED_ROWS = 100
"""SPEC §8's own number. Pre-registered, so it is not resized here — and it does not
need to be: binomial precision depends on the sample and not on the 3,263 rows it is
drawn from. At the bar, 100 rows carry a ±5.9 pp 95% band."""
DIAGNOSTIC_ROWS = 50
BAR = 0.90

GATED_COLUMNS = ("id", "text", "intents", "verdict", "notes")
DIAGNOSTIC_COLUMNS = ("id", "text", "intents_before", "intents_after", "verdict", "notes")
GATED_VERDICTS = ("correct", "incorrect")
DIAGNOSTIC_VERDICTS = ("old", "new", "neither")

DENOMINATOR = (
    "agreement = rows marked `correct` / {rows} rows shipped. A blank cell or any"
    " other value counts as disagreement. Registered before the pack was handed over"
    " and not recomputed on any other denominator."
)

README = """# Калибровка переразметки интенций (4.5e) — как заполнять

## Что это

Все размеченные незамороженные строки переразмечены по таксономии v2 (шестая
интенция `service`, `docs/SPEC.md` поправка 3.8, закон — `docs/annotation/comments.md`).
Переразметку сделала модель; **принимается она твоими вердиктами**, а не тем, что
она отработала без ошибок.

**Два файла, разные роли.**

| файл | строк | что решает |
|---|---:|---|
| `gated.csv` | {gated} | **гейт**: переразметка принимается при согласии ≥ {bar:.0%} |
| `changed.csv` | {diagnostic} | диагностика дрейфа; на гейт НЕ влияет |

Строки в обоих файлах не пересекаются. Порядок строк случайный (seed {seed}) — по
нему нельзя понять, менялась строка или нет.

Ориентировочно ~1.0 ч на оба файла.

## Правило подсчёта — зафиксировано ДО вердиктов

{denominator}

## `gated.csv` — сотня, на которой стоит гейт

Показан текст комментария и **итоговый** набор интенций v2. Вопрос один: верен ли
этот набор по гайдлайну v2.

| `verdict` | когда ставить |
|---|---|
| `correct` | набор верен |
| `incorrect` | набор неверен — лишняя метка, недостающая метка, или обе |

Пустой набор записан как `[]` и это полноценный ответ: часть комментариев по
гайдлайну не несёт ни одной интенции.

Сотня взята только из строк, которые считает хоть один гейт (`unclear = false`):
строки с `unclear` исключены из всех метрик, и согласие по ним ничего не измеряет
(решение гейта 4.5d).

## `changed.csv` — полсотни изменённых, диагностика

Здесь показаны **обе** метки: `intents_before` (v1) и `intents_after` (v2). Это
единственное место, где видно, что именно двинулось.

| `verdict` | когда ставить |
|---|---|
| `old` | старая метка была ближе к правде |
| `new` | новая метка ближе |
| `neither` | обе мимо |

Эти строки **не входят** в гейт. Они отвечают на другой вопрос: та часть дрейфа,
которую таксономия не объясняет — это модель спорит с прежней разметкой или
прежняя разметка была неверна.

## Что не трогать

Заполняй только `verdict` и `notes`. `id`, `text` и сами метки менять нельзя — по
ним harness сверяет вернувшийся файл с манифестом (`results/calib_45e_manifest.json`)
и откажется считать, если они разошлись.
"""


def load_pairs() -> tuple[list[dict], dict]:
    """Every staged row beside the source row it came from, and what both files hash to.

    The provenance travels with the rows rather than being read again where the
    manifest is written: the pack and the hashes in its record have to describe the
    same bytes, and two independent reads of the same paths are two chances not to.
    """
    pairs = []
    for name, source in relabel.SOURCES.items():
        staged = relabel.staged(source)
        if not staged.exists():
            raise SystemExit(f"{relabel.rel(staged)}: not found — the re-label has not run")
        by_id = {row["id"]: row for row in relabel.load(source)[0]}
        for row in relabel.load(staged)[0]:
            before = by_id[row["id"]]
            pairs.append(
                {
                    "id": row["id"],
                    "source": name,
                    "text": row["text"],
                    "unclear": row["unclear"],
                    "before": before["intents"],
                    "after": row["intents"],
                    "changed": set(before["intents"]) != set(row["intents"]),
                }
            )
    provenance = {
        "staged": {
            relabel.rel(relabel.staged(path)): sha256(relabel.staged(path).read_bytes()).hexdigest()
            for path in relabel.SOURCES.values()
        },
        "sources": {
            relabel.rel(path): sha256(path.read_bytes()).hexdigest()
            for path in relabel.SOURCES.values()
        },
    }
    return pairs, provenance


def strata(pairs: list[dict], gated_rows: int, diagnostic_rows: int) -> dict[str, list[dict]]:
    """The gated sample first, the diagnostic out of what is left. Disjoint by build.

    The gated draw comes first because it is the one the gate reads: it must be a
    plain random sample of the scoreable rows, not of whatever the diagnostic
    happened to leave behind.
    """
    scoreable = [pair for pair in pairs if not pair["unclear"]]
    if len(scoreable) < gated_rows:
        raise SystemExit(f"{len(scoreable)} scoreable rows — fewer than the {gated_rows} SPEC asks")
    gated = random.Random(SEED).sample(scoreable, gated_rows)
    drawn = {pair["id"] for pair in gated}
    changed = [pair for pair in scoreable if pair["changed"] and pair["id"] not in drawn]
    if len(changed) < diagnostic_rows:
        raise SystemExit(f"{len(changed)} changed rows left outside the gated sample")
    return {"gated": gated, "changed": random.Random(SEED).sample(changed, diagnostic_rows)}


def as_label(intents: list[str]) -> str:
    return json.dumps(sorted(intents), ensure_ascii=False)


def write_csv(path: Path, columns: tuple[str, ...], rows: list[dict]) -> str:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return sha256(path.read_bytes()).hexdigest()


def gated_rows(pack: list[dict]) -> list[dict]:
    return [
        {
            "id": p["id"],
            "text": p["text"],
            "intents": as_label(p["after"]),
            "verdict": "",
            "notes": "",
        }
        for p in pack
    ]


def diagnostic_rows(pack: list[dict]) -> list[dict]:
    return [
        {
            "id": p["id"],
            "text": p["text"],
            "intents_before": as_label(p["before"]),
            "intents_after": as_label(p["after"]),
            "verdict": "",
            "notes": "",
        }
        for p in pack
    ]


def filled(path: Path, column: str = "verdict") -> int:
    """How many verdicts a pack on disk already carries."""
    if not path.exists():
        return 0
    with path.open(encoding="utf-8", newline="") as handle:
        return sum(1 for row in csv.DictReader(handle) if (row.get(column) or "").strip())


def composition(pack: list[dict]) -> dict:
    """What the gated sample is made of — provenance for reading the result later.

    It lives in the manifest and never in the pack: knowing that N of 100 changed
    identifies no row, and the analysis that follows the verdicts needs it.
    """
    return {
        "rows": len(pack),
        "changed": sum(1 for p in pack if p["changed"]),
        "carry_service": sum(1 for p in pack if "service" in p["after"]),
        "empty_after": sum(1 for p in pack if not p["after"]),
        "by_source": {
            name: sum(1 for p in pack if p["source"] == name) for name in relabel.SOURCES
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, default=PACK)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--gated", type=int, default=GATED_ROWS)
    parser.add_argument("--diagnostic", type=int, default=DIAGNOSTIC_ROWS)
    parser.add_argument("--force", action="store_true", help="overwrite a pack being filled in")
    args = parser.parse_args(argv)

    gated_csv = args.pack / "gated.csv"
    changed_csv = args.pack / "changed.csv"
    if not args.force and (already := filled(gated_csv) + filled(changed_csv)):
        raise SystemExit(
            f"{relabel.rel(args.pack)} already carries {already} verdicts — rebuilding would"
            " destroy them. --force if that is really what you want."
        )

    pairs, provenance = load_pairs()
    drawn = strata(pairs, args.gated, args.diagnostic)
    args.pack.mkdir(parents=True, exist_ok=True)
    shas = {
        "gated.csv": write_csv(gated_csv, GATED_COLUMNS, gated_rows(drawn["gated"])),
        "changed.csv": write_csv(
            changed_csv, DIAGNOSTIC_COLUMNS, diagnostic_rows(drawn["changed"])
        ),
    }
    denominator = DENOMINATOR.format(rows=args.gated)
    readme = args.pack / "README-calibration.md"
    readme.write_text(
        README.format(
            gated=args.gated,
            diagnostic=args.diagnostic,
            bar=BAR,
            seed=SEED,
            denominator=denominator,
        ),
        encoding="utf-8",
    )
    shas["README-calibration.md"] = sha256(readme.read_bytes()).hexdigest()

    manifest = {
        "pack": relabel.rel(args.pack),
        "seed": SEED,
        "bar": BAR,
        "rule": denominator,
        "gated_verdicts": list(GATED_VERDICTS),
        "diagnostic_verdicts": list(DIAGNOSTIC_VERDICTS),
        "gated_is_scoreable_only": True,
        "strata_are_disjoint": True,
        "sha256": shas,
        **provenance,
        "population": {
            "staged_rows": len(pairs),
            "scoreable": sum(1 for p in pairs if not p["unclear"]),
            "changed_scoreable": sum(1 for p in pairs if p["changed"] and not p["unclear"]),
        },
        "composition": {name: composition(rows) for name, rows in drawn.items()},
        "note": (
            "The gated sample decides the re-label under SPEC §8; the changed sample is a"
            " diagnostic and no reading of it moves the verdict. The composition block is"
            " provenance for the analysis that follows the verdicts — it is not in the pack,"
            " because a pack that says how many of its rows moved is not blind."
        ),
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"{relabel.rel(args.pack)}")
    for name, digest in shas.items():
        print(f"  {name:<24} {digest[:16]}…")
    print(
        f"  population: {manifest['population']['staged_rows']} staged,"
        f" {manifest['population']['scoreable']} scoreable,"
        f" {manifest['population']['changed_scoreable']} of those changed"
    )
    for name, block in manifest["composition"].items():
        print(
            f"  {name:<8} {block['rows']:>4} rows · {block['changed']:>3} changed ·"
            f" {block['carry_service']:>3} carry `service` · {block['by_source']}"
        )
    print(f"wrote {relabel.rel(args.manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
