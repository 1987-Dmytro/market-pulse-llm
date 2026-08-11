#!/usr/bin/env python3
"""Build the blinded adjudication pack the operator rules on (SPEC amendment 3.7, 4.5a).

Every row where the deliverable arm and the frozen gold disagree, plus a control
sample of rows where they agree, written as CSVs whose two candidate labels are
in per-row random order with no attribution anywhere. The operator rules each
row; `scripts/audit_ceiling.py` turns the rulings into a per-head ceiling.

This step judges nothing. It reads the persisted per-row dump and the frozen
files, and writes nothing back to either.

    python3.11 scripts/build_audit_pack.py

Outputs (all gitignored data except the manifest):

    data/annotation/audit_45a/*.csv        the pack the operator opens
    data/annotation/audit_45a/README-audit.md
    data/annotation/audit_45a_key.json     the de-anonymization key, beside the pack
    results/audit_45a_manifest.json        committed provenance: the key's sha256
                                           and every CSV's, so a quiet rebuild shows
                                           up as a diff instead of as nothing

Deterministic: seed 42, and a rebuild reproduces the CSVs and the key byte for
byte. It refuses to overwrite a pack whose verdicts are already being filled in
(`--force` overrides) — the operator's evening is not a regenerable artifact.
"""

import argparse
import csv
import json
import random
import sys
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed

from market_pulse import audit, provenance, records  # noqa: E402
from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

FROZEN = REPO_ROOT / "data" / "frozen"
RESULTS = REPO_ROOT / "results" / "baselines.json"
SLICE = REPO_ROOT / "results" / "g1b_slice.json"
PACK = REPO_ROOT / "data" / "annotation" / "audit_45a"
KEY = REPO_ROOT / "data" / "annotation" / "audit_45a_key.json"
MANIFEST = REPO_ROOT / "results" / "audit_45a_manifest.json"

ARM = "real-only"
SEED = 42
BASE_CONTROL = 8
"""The accepted pack's per-head control draw, kept as the FIRST draw of the run.

Widening a stratum must not resample it: the operator accepted a pack, and rows
that silently changed underneath an accepted artifact would make "the same pack,
expanded" a claim nobody could check. Every head still draws its 8 before any
head draws its top-up, so the seeded stream up to that point is the stream that
produced the accepted 40 rows."""

N_CONTROL = {"sentiment": 40, "intents": 40, "sarcasm_pair": 8, "post_type": 8, "brands": 8}
"""Per-head control size (operator decision, 2026-08-02). Sentiment and intents
carry the two largest agreement strata and the two heads whose ceilings a phase
decision will be read off, so their gold-error rate stops resting on n=8."""

README = """# Аудит разногласий 4.5a — как заполнять

## Что это

Модель фазы 4 и «золотая» разметка расходятся на части строк. **Мы не знаем,
кто из них прав** — и именно это надо выяснить. Ты единственный арбитр
(SPEC §10). Результат: оценка потолка качества на этом тесте, то есть сколько
может набрать идеальная модель против нашей нынешней разметки.

**Всего строк: {total}.**

| файл | строк | что судим |
|---|---:|---|
| `comments_sentiment.csv` | {comments_sentiment} | тональность комментария |
| `comments_intents.csv` | {comments_intents} | набор интентов целиком |
| `slice_unfixed.csv` | {slice_unfixed} | пара `sentiment` + `sarcasm` |
| `posts.csv` | {posts} | тип поста и набор брендов |
| `control.csv` | {control} | согласие: права ли общая метка |

## Как это устроено

В каждой строке разногласия показаны две метки-кандидата: `label_A` и
`label_B`. Порядок в каждой строке случайный, и **нигде — ни в файлах, ни в
именах колонок — не написано, какая из них чья**. Так и задумано: если знать
автора метки, суждение перестаёт быть независимым.

> **Суди метку, не автора метки.**

## Что заполнять

Только колонки `verdict` и (по желанию) `notes`. Больше ничего не меняй:
ни `id`, ни `text`, ни сами метки — по ним harness сверяет файл с ключом и
откажется считать, если они разошлись.

### Файлы разногласий

`comments_sentiment.csv` · `comments_intents.csv` · `slice_unfixed.csv` ·
`posts.csv`

| `verdict` | когда ставить |
|---|---|
| `A` | правильная метка — `label_A` |
| `B` | правильная метка — `label_B` |
| `ambiguous` | обе защитимы, или текст не даёт решить |

### Контрольный файл

`control.csv` — здесь метка **одна**: обе стороны сошлись на ней. Вопрос
другой: сошлись ли они на правде.

| `verdict` | когда ставить |
|---|---|
| `correct` | метка верна |
| `incorrect` | метка неверна — оба ошиблись одинаково |
| `ambiguous` | не решается |

Этот файл — единственный, который измеряет ошибку разметки там, где никто не
спорит. Он не «на сдачу»: по нему считается бо́льшая часть потолка. Не пропускай.

## Правила

- `ambiguous` — не признак слабости. Это отдельный измеряемый класс: строки,
  которых идеальная модель тоже может не взять. Гадание вместо `ambiguous`
  портит оценку сильнее, чем честное «не решается».
- Пустых `verdict` быть не должно: harness откажется считать, пока есть хоть
  одна пустая ячейка.
- Спешки нет. Можно за несколько заходов — файлы просто сохраняй.
- Про `intents` (`comments_intents.csv`) и `brands` (строки `head=brands` в
  `posts.csv`) метка — это **весь набор** целиком, а не одна позиция. Верна
  та, что описывает текст полностью.
- В `slice_unfixed.csv` метка — **пара** `sentiment` + `sarcasm`. Верна та
  пара, где верны обе половины.

## Куда класть готовое

Туда же, где взял: `data/annotation/audit_45a/`, те же имена файлов.
Потом скажи — считаем потолок.
"""


def sizes(counts: dict[str, int]) -> dict[str, int]:
    """CSV row counts keyed for :data:`README`'s placeholders, plus their total."""
    return {path.removesuffix(".csv"): n for path, n in counts.items()} | {
        "total": sum(counts.values())
    }


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def git_state(mine: Path) -> dict:
    """`market_pulse.provenance.git_state`, kept under this name because 51 scripts do
    `from build_audit_pack import git_state` — this module became the repo's provenance helper by
    accident and the import is what every record's `git` block is written through.

    Unsorted, which is what this copy always was: porcelain order is "tracked, then untracked",
    and every record already on disk that names this function was written that way."""
    return provenance.git_state(mine)


def predictions(path: Path) -> dict[str, dict[str, dict]]:
    """The arm's dump as ``{input: {id: labels}}`` — the shape the heads read."""
    out: dict[str, dict[str, dict]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        row = json.loads(line)
        out.setdefault(row["input"], {})[row["id"]] = row["pred"]
    return out


def arm_dump() -> tuple[dict, Path, dict[str, dict[str, dict]]]:
    """The deliverable arm's record and its per-row dump, both verified.

    ``records.arm_record`` refuses if the arm is not exactly one row, and the
    dump is checked against the SHA256 the record stored: a re-scored or edited
    dump is a different measurement, and the audit would be of that one.
    """
    history = json.loads(RESULTS.read_text(encoding="utf-8"))
    record = records.arm_record(history, ARM)
    path = REPO_ROOT / record["config"]["predictions_path"]
    expected = record["config"]["predictions_sha256"]
    if digest(path) != expected:
        raise SystemExit(
            f"{path}: sha256 {digest(path)} but the {ARM} record says {expected}."
            " The audit reads the dump the gates were scored from, or it audits something else."
        )
    return record, path, predictions(path)


def has_verdicts(directory: Path) -> list[str]:
    """CSVs in an existing pack that already carry a filled verdict cell."""
    filled = []
    for path in sorted(directory.glob("*.csv")):
        with path.open(encoding="utf-8", newline="") as handle:
            if any(row.get("verdict") for row in csv.DictReader(handle)):
                filled.append(path.name)
    return filled


def build(rows: dict, predicted: dict, aliases: dict, slice_ids: list[str]) -> tuple[dict, dict]:
    """Every head's blinded disagreements and its control sample.

    Three passes over the heads, each in :data:`market_pulse.audit.HEADS` order
    and all drawing from one seeded generator, so the pack is a function of the
    seed and the inputs alone: blinding, then every head's :data:`BASE_CONTROL`
    draw, then the top-ups. The order is the point — the top-up pass runs last so
    it cannot move the stream that produced the accepted control rows.
    """
    rng = random.Random(SEED)
    universe = {
        head: (
            [row for row in rows["sarcasm_holdout"] if row["id"] in set(slice_ids)]
            if head == "sarcasm_pair"
            else rows[audit.INPUT_OF[head]]
        )
        for head in audit.HEADS
    }
    blinded, key = {}, {}
    for head in audit.HEADS:
        blinded[head] = []
        for row in audit.disagreements(
            head, universe[head], predicted[audit.INPUT_OF[head]], aliases
        ):
            model_column = audit.blind(rng)
            cell = {
                "head": head,
                "id": row["id"],
                "text": row["text"],
                "label_A": row["model"] if model_column == "A" else row["gold"],
                "label_B": row["gold"] if model_column == "A" else row["model"],
                "verdict": "",
                "notes": "",
            }
            blinded[head].append(cell)
            key[f"{head}|{row['id']}"] = {
                "model_column": model_column,
                "label_A": cell["label_A"],
                "label_B": cell["label_B"],
            }

    pools = {
        head: audit.agreements(head, universe[head], predicted[audit.INPUT_OF[head]], aliases)
        for head in audit.HEADS
    }
    picked = {
        head: rng.sample(pools[head], min(BASE_CONTROL, len(pools[head]))) for head in audit.HEADS
    }
    for head in audit.HEADS:
        already = {row["id"] for row in picked[head]}
        remaining = [row for row in pools[head] if row["id"] not in already]
        wanted = min(N_CONTROL[head] - len(picked[head]), len(remaining))
        if wanted > 0:
            picked[head] += rng.sample(remaining, wanted)

    control, strata = [], {}
    for head in audit.HEADS:
        rows_of_head = sorted(picked[head], key=lambda row: row["id"])
        control.extend({"head": head, **row, "verdict": "", "notes": ""} for row in rows_of_head)
        strata[head] = {
            "gate": audit.GATE_OF[head],
            "input": audit.INPUT_OF[head],
            "scoreable": len(blinded[head]) + len(pools[head]),
            "disagreements": len(blinded[head]),
            "agreements": len(pools[head]),
            "control": len(rows_of_head),
        }
    return {"blinded": blinded, "control": control, "key": key}, strata


def blinding_sweep(directory: Path) -> list[tuple[str, str]]:
    """Every structural cell of the pack that would say which side a label is from.

    Column names and every cell except ``text`` and ``notes`` — the row's own text
    is source data and may legitimately contain any of these words. Returns the
    offenders as ``(file, cell)``; an empty list is the pack being blind.
    """
    found = []
    for path in sorted(directory.glob("*.csv")):
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            cells = [path.name, *(reader.fieldnames or [])]
            for row in reader:
                cells += [v for k, v in row.items() if k not in ("text", "notes")]
        found += [
            (path.name, cell)
            for cell in cells
            if any(word in cell.casefold() for word in audit.ATTRIBUTION)
        ]
    return found


def write_csv(path: Path, columns: tuple[str, ...], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force", action="store_true", help="overwrite a pack that already has verdicts in it"
    )
    args = parser.parse_args(argv)

    if PACK.exists() and (filled := has_verdicts(PACK)) and not args.force:
        raise SystemExit(
            f"{PACK}: {', '.join(filled)} already carry verdicts. Rebuilding would discard the"
            " operator's adjudication — pass --force only if that is what you mean."
        )

    record, dump_path, predicted = arm_dump()
    slice_text = SLICE.read_text(encoding="utf-8")
    ids = records.slice_ids(slice_text, record)
    aliases = watchlist_aliases(load_registry(REPO_ROOT / "config" / "registry.yaml").watchlist)
    rows = {name: load(FROZEN / f"{name}.jsonl") for name in ("comments_test", "posts_test")}
    rows["sarcasm_holdout"] = load(FROZEN / "sarcasm_holdout.jsonl")

    pack, strata = build(rows, predicted, aliases, ids)

    PACK.mkdir(parents=True, exist_ok=True)
    by_csv: dict[str, list[dict]] = {}
    for head in audit.HEADS:
        by_csv.setdefault(audit.CSV_OF[head], []).extend(pack["blinded"][head])
    for name, cells in by_csv.items():
        write_csv(PACK / name, audit.COLUMNS, cells)
    write_csv(PACK / "control.csv", audit.CONTROL_COLUMNS, pack["control"])
    counts = {
        **{name: len(cells) for name, cells in by_csv.items()},
        "control.csv": len(pack["control"]),
    }
    (PACK / "README-audit.md").write_text(README.format(**sizes(counts)), encoding="utf-8")
    KEY.write_text(json.dumps(pack["key"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if leaks := blinding_sweep(PACK):
        raise SystemExit(
            f"the pack names a side in {len(leaks)} structural cell(s): {leaks[:3]}."
            " A blinded artifact that says whose label is whose measures attribution, not judgement."
        )

    manifest = {
        "built_by": "scripts/build_audit_pack.py",
        "seed": SEED,
        "arm": ARM,
        "arm_record_timestamp": record["timestamp"],
        "adapter_sha256": record["config"]["fine_tune"]["adapter_sha256"],
        "predictions_path": record["config"]["predictions_path"],
        "predictions_sha256": record["config"]["predictions_sha256"],
        "frozen_path": str(FROZEN.relative_to(REPO_ROOT)),
        "slice_path": str(SLICE.relative_to(REPO_ROOT)),
        "frozen_sha256": {
            path.name: digest(path) for path in sorted(FROZEN.glob("*.jsonl")) if path.is_file()
        },
        "g1b_slice_sha256": record["config"]["g1b_slice_sha256"],
        "key_path": str(KEY.relative_to(REPO_ROOT)),
        "key_sha256": digest(KEY),
        "pack_path": str(PACK.relative_to(REPO_ROOT)),
        "csv": {
            name: {"rows": sum(1 for _ in cells), "sha256": digest(PACK / name)}
            for name, cells in [*by_csv.items(), ("control.csv", pack["control"])]
        },
        "readme_sha256": digest(PACK / "README-audit.md"),
        "strata": strata,
        "git": git_state(MANIFEST),
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"arm {ARM} @ {record['timestamp']}  dump {dump_path.name}")
    print(f"{'head':<14}{'gate':>6}{'scoreable':>11}{'disagree':>10}{'agree':>8}{'control':>9}")
    for head, stratum in strata.items():
        print(
            f"{head:<14}{stratum['gate']:>6}{stratum['scoreable']:>11}"
            f"{stratum['disagreements']:>10}{stratum['agreements']:>8}{stratum['control']:>9}"
        )
    print()
    for name in sorted(manifest["csv"]):
        print(f"{PACK.relative_to(REPO_ROOT)}/{name}: {manifest['csv'][name]['rows']} rows")
    print(f"\nkey  {KEY.relative_to(REPO_ROOT)}  sha256 {manifest['key_sha256']}")
    print(f"manifest {MANIFEST.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
