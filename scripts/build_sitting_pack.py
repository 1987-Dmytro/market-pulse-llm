#!/usr/bin/env python3
"""The operator's sitting: 300 precheck rows, 40 contrastive rows, 14 to label (4.5g).

Three files, three questions, one manifest — and the denominators are written before the
pack is handed over, not after the verdicts come back.

- **`precheck300.csv`** is the gate. 100 rows from each of three strata, judged row by
  row: a row is `correct` only if **every** field is (sentiment, sarcasm, intents,
  unclear). A stratum below {bar:.0%} sends its whole batch back — that batch is the whole
  stratum in the pool, whose size is in the manifest, not the 100 shown here.
- **`emptied40.csv`** decides the 97 rows the with-post re-label just rewrote, under the
  rule `results/emptied_with_post_45g.json` registered before those requests went out.
- **`unreadable14.csv`** is the 4.5f micro-pack, pinned where it already lives. It is not
  copied here: a second copy of a file the operator may already be filling in is how one
  evening's work ends up in the file nobody reads.

What the pack refuses:

- **saying which stratum a row is in.** One file, one seeded shuffle over all 300 after the
  three draws, no stratum column and no order to read it off. The map lives in the manifest
  for the reader, exactly as `build_calibration_pack.py` keeps its composition out of the
  pack — a pack that describes itself is not blind.
- **judging under a stricter law than the one that wrote the labels.** The parent post is
  shown, because `docs/annotation/comments.md` §Unit lets the annotator read it and the
  model was given it.
- **overwriting an evening's work.** A pack already carrying verdicts is not rebuilt
  without `--force`, and a bundled file whose sha256 has moved since its own manifest stops
  the build.

    python3.11 scripts/build_sitting_pack.py

Writes `data/annotation/sitting_45g/` (gitignored, like every pack) and the committed
manifest `results/sitting_45g_manifest.json`.
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
sys.path.insert(0, str(Path(__file__).resolve().parent))

import relabel_intents as relabel  # noqa: E402
import uplabel_candidates as candidates  # noqa: E402
from build_audit_pack import git_state  # noqa: E402
from market_pulse import parents  # noqa: E402

PACK = REPO_ROOT / "data" / "annotation" / "sitting_45g"
MANIFEST = REPO_ROOT / "results" / "sitting_45g_manifest.json"
BATCH = REPO_ROOT / "data" / "annotation" / "uplabel_precheck_45g.jsonl"
EMPTIED = REPO_ROOT / "results" / "emptied_with_post_45g.json"
MICRO_MANIFEST = REPO_ROOT / "results" / "calib_45e_micro_manifest.json"
POSTS = REPO_ROOT / "data" / "raw" / "posts"

SEED = 42
PER_STRATUM = 100
BAR = 0.90
DELIMITER = ";"
SHORT_CHARS = 30

PRECHECK_COLUMNS = (
    "id",
    "post",
    "text",
    "sentiment",
    "sarcasm",
    "intents",
    "unclear",
    "verdict",
    "notes",
)
EMPTIED_COLUMNS = ("id", "post", "text", "intents_v1", "intents_with_post", "verdict", "notes")

PRECHECK_RULE = (
    "Per stratum: agreement = rows marked `correct` / {rows} rows of that stratum shipped."
    " A row is `correct` only if EVERY field is right — sentiment, sarcasm, intents and"
    " unclear together; one wrong field makes the row `incorrect`. A blank cell or any other"
    " value counts as `incorrect`. Each stratum passes at >= {bar:.2f} on its own; a stratum"
    " below the bar sends its WHOLE batch back for re-labelling, not just the 100 shown."
    " Registered before the pack was handed over and not recomputed on any other denominator."
)

README = """# Сессия вердиктов 4.5g — три файла, ~2.5 ч

Разделитель во всех файлах — `;`. Заполняй только `verdict` и `notes`. Остальные
колонки не трогай: по ним harness сверяет вернувшийся файл с манифестом
`results/sitting_45g_manifest.json` и откажется считать, если они разошлись.

Колонка `post` — текст поста, под которым висит комментарий. По гайдлайну
(`docs/annotation/comments.md`, §Unit) читать его можно и нужно тогда, когда без
него комментарий бессмыслен (`Так`, `+`, `А коли?`). Модель его тоже видела.
`(нет текста)` — пост состоит из картинки, текста у него нет.

## 1. `precheck300.csv` — {precheck} строк, ЭТО ГЕЙТ (~2.0 ч)

{pool} строк корпуса размечены моделью (`annotator: llm-precheck`) по всем четырём
полям. Ни одна из них ещё никуда не влита: их принимают твои вердикты.

Вопрос по строке один: **все ли четыре поля верны** — `sentiment`, `sarcasm`,
`intents` (шесть интенций v2), `unclear`.

| `verdict` | когда ставить |
|---|---|
| `correct` | верны ВСЕ четыре поля |
| `incorrect` | хотя бы одно поле неверно (напиши в `notes`, какое) |

Порядок строк случайный (seed {seed}). Внутри файла ничего не говорит, из какой
части выборки строка — так и задумано.

Планка ≥ {bar:.0%} считается ОТДЕЛЬНО по трём стратам, их состав в манифесте. Страта
ниже планки отправляет назад весь свой пласт корпуса, а не эти сто строк.

## 2. `emptied40.csv` — {emptied} строк, контраст (~15 мин)

97 строк, у которых переразметка 4.5e сняла интенцию в ноль. Их переспросили тем же
промптом, но уже С ПОСТОМ. Здесь показаны обе метки: `intents_v1` (старая, ручная) и
`intents_with_post` (новая).

| `verdict` | когда ставить |
|---|---|
| `old` | старая метка ближе к правде |
| `new` | новая ближе |
| `neither` | обе мимо |

Правило зафиксировано ДО запросов: `new` / {emptied} ≥ {bar:.0%} принимает все 97;
ниже планки все 97 идут к тебе руками. Если обе колонки совпали — модель воспроизвела
твою старую метку, это и проверяется: ставь `new`, если набор верен.

## 3. `unreadable14.csv` — 14 строк, разметить руками (~6 мин)

Лежит на месте, в `data/annotation/calib_45e/`, вместе со своим README. Модель
четыре прохода подряд не отдавала для них `intents`; заполни колонку `intents_v2`
сам. На гейт эти строки не влияют.
"""


def load_batch(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"{relabel.rel(path)}: not found — the precheck has not run")
    return relabel.load(path)[0]


def strata(rows: list[dict]) -> dict[str, list[dict]]:
    """Three disjoint classes, by rule and not by what the previous draw left over.

    `service-rich` first because it is the smallest and the most specific; `short` is the
    class 4.5f proved is the weak one (median 18 characters among the rows the re-label
    emptied); `general` is everything the other two do not describe.
    """
    service, short, general = [], [], []
    for row in rows:
        if any(pattern.search(row["text"]) for pattern in candidates.SERVICE.values()):
            service.append(row)
        elif len(row["text"]) <= SHORT_CHARS:
            short.append(row)
        else:
            general.append(row)
    return {
        "service-rich": service,
        f"short-text <= {SHORT_CHARS} chars": short,
        "general": general,
    }


def draw(pools: dict[str, list[dict]], per_stratum: int) -> tuple[list[dict], dict[str, str]]:
    """`per_stratum` from each class, then one shuffle over all of them together.

    Shuffled after the draws, so position in the file says nothing about the stratum — the
    blindness is in the file and the map is in the manifest.
    """
    drawn, where = [], {}
    for name, pool in pools.items():
        if len(pool) < per_stratum:
            raise SystemExit(f"{name}: {len(pool)} rows, fewer than the {per_stratum} asked for")
        picked = random.Random(SEED).sample(sorted(pool, key=lambda row: row["id"]), per_stratum)
        drawn += picked
        where |= {row["id"]: name for row in picked}
    random.Random(SEED).shuffle(drawn)
    return drawn, where


def post_of(posts: dict, row: dict) -> str:
    text = parents.text_for(posts, row)
    return text.strip() or "(нет текста)"


def as_label(intents: list[str]) -> str:
    return json.dumps(sorted(intents), ensure_ascii=False)


def write_csv(path: Path, columns: tuple[str, ...], rows: list[dict]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=columns, delimiter=DELIMITER, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    return sha256(path.read_bytes()).hexdigest()


def filled(path: Path, column: str = "verdict") -> int:
    if not path.exists():
        return 0
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=DELIMITER)
        return sum(1 for row in reader if (row.get(column) or "").strip())


def bundled(manifest: Path, root: Path = REPO_ROOT) -> dict:
    """The 4.5f micro-pack, pinned where it lives — never copied, and never re-derived.

    Its own manifest sealed it; if the bytes have moved since, the operator has started on
    it (or something else has), and a sitting that bundles a file it cannot describe is not
    a sitting with a manifest.
    """
    sealed = json.loads(manifest.read_text(encoding="utf-8"))
    path = root / sealed["pack"]
    if not path.exists():
        raise SystemExit(
            f"{sealed['pack']}: not found — the 4.5f micro-pack is part of this sitting"
        )
    now = sha256(path.read_bytes()).hexdigest()
    if now != sealed["sha256"][sealed["pack"]]:
        raise SystemExit(
            f"{sealed['pack']} no longer hashes to what {relabel.rel(manifest)} pinned"
            f" ({now[:16]}… against {sealed['sha256'][sealed['pack']][:16]}…). It carries"
            f" {filled(path, 'intents_v2')} labels; say what it is before bundling it."
        )
    return {
        "pack": sealed["pack"],
        "readme": sealed["readme"],
        "rows": sealed["rows"],
        "to_fill": sealed["to_fill"],
        "gated": False,
        "sha256": now,
        "already_filled": filled(path, "intents_v2"),
        "manifest": relabel.rel(manifest),
        "note": (
            "Pinned in place, not copied into this pack: a second copy of a file the operator"
            " may already be filling in is how one evening's work ends up in the file nobody"
            " reads. results/calib_45e_micro_manifest.json is its manifest and is not rewritten."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, default=PACK)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--batch", type=Path, default=BATCH)
    parser.add_argument("--emptied", type=Path, default=EMPTIED)
    parser.add_argument("--micro-manifest", type=Path, default=MICRO_MANIFEST)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--posts", type=Path, default=POSTS)
    parser.add_argument("--per-stratum", type=int, default=PER_STRATUM)
    parser.add_argument("--force", action="store_true", help="overwrite a pack being filled in")
    args = parser.parse_args(argv)

    precheck_csv = args.pack / "precheck300.csv"
    emptied_csv = args.pack / "emptied40.csv"
    if not args.force and (already := filled(precheck_csv) + filled(emptied_csv)):
        raise SystemExit(
            f"{relabel.rel(args.pack)} already carries {already} verdicts — rebuilding would"
            " destroy them. --force if that is really what you want."
        )

    rows = load_batch(args.batch)
    posts = parents.load(args.posts)
    pools = strata(rows)
    drawn, where = draw(pools, args.per_stratum)
    check = json.loads(args.emptied.read_text(encoding="utf-8"))["runs"][-1]["check"]
    # the 40 contrastive rows come out of the labelled sources, not out of the precheck pool
    labelled = {
        row["id"]: row for source in relabel.SOURCES.values() for row in relabel.load(source)[0]
    }

    shas = {
        "precheck300.csv": write_csv(
            precheck_csv,
            PRECHECK_COLUMNS,
            [
                {
                    "id": row["id"],
                    "post": post_of(posts, row),
                    "text": row["text"],
                    "sentiment": row["sentiment"],
                    "sarcasm": str(row["sarcasm"]).lower(),
                    "intents": as_label(row["intents"]),
                    "unclear": str(row["unclear"]).lower(),
                    "verdict": "",
                    "notes": "",
                }
                for row in drawn
            ],
        ),
        "emptied40.csv": write_csv(
            emptied_csv,
            EMPTIED_COLUMNS,
            [
                {
                    "id": row["id"],
                    "post": post_of(posts, labelled[row["id"]]),
                    "text": row["text"],
                    "intents_v1": as_label(row["intents_v1"]),
                    "intents_with_post": as_label(row["intents_with_post"]),
                    "verdict": "",
                    "notes": "",
                }
                for row in check["rows_drawn"]
            ],
        ),
    }
    rule = PRECHECK_RULE.format(rows=args.per_stratum, bar=BAR)
    readme = args.pack / "README-sitting.md"
    readme.write_text(
        README.format(
            precheck=len(drawn),
            emptied=len(check["rows_drawn"]),
            pool=len(rows),
            seed=SEED,
            bar=BAR,
        ),
        encoding="utf-8",
    )
    shas["README-sitting.md"] = sha256(readme.read_bytes()).hexdigest()

    manifest = {
        "pack": relabel.rel(args.pack),
        "seed": SEED,
        "bar": BAR,
        "delimiter": DELIMITER,
        "sha256": shas,
        "precheck": {
            "source": relabel.rel(args.batch),
            "source_sha256": sha256(args.batch.read_bytes()).hexdigest(),
            "rows": len(drawn),
            "per_stratum": args.per_stratum,
            "rule": rule,
            "verdicts": ["correct", "incorrect"],
            "second_round": (
                "A stratum below the bar sends its whole batch back — `population` below is"
                " that batch, and it is the number of rows re-labelled, not the 100 judged."
            ),
            "strata": {
                name: {"population": len(pool), "drawn": args.per_stratum}
                for name, pool in pools.items()
            },
            "stratum_of": where,
            "unclear_rows_included": True,
            "unclear_note": (
                "Drawn from all 1,912 rows, `unclear` ones included — unlike the 4.5e gated"
                " sample, which drew only scoreable rows. There the question was whether the"
                " intents were right and an unclear row answers nothing; here `unclear` is"
                " itself one of the four fields under judgement."
            ),
        },
        "emptied": {
            "source": relabel.rel(args.emptied),
            "rows": len(check["rows_drawn"]),
            "rule": check["rule"],
            "verdicts": ["old", "new", "neither"],
            "composition": check["drawn_composition"],
        },
        "unreadable": bundled(args.micro_manifest, args.root),
        "note": (
            "Three questions, one sitting. `precheck300.csv` is the gate on the up-label"
            " precheck and nothing merges into a train or candidates file until every stratum"
            " passes. Nothing in any pack file says which stratum a row is in; `stratum_of` is"
            " here because the reader needs it and the operator must not have it."
        ),
        "git": git_state(args.manifest),
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"{relabel.rel(args.pack)}")
    for name, digest in shas.items():
        print(f"  {name:<22} {digest[:16]}…")
    for name, block in manifest["precheck"]["strata"].items():
        print(f"  {name:<26} {block['drawn']:>4} of {block['population']:>5}")
    print(
        f"  emptied40.csv composition {manifest['emptied']['composition']}"
        f"\n  bundled {manifest['unreadable']['pack']} ({manifest['unreadable']['rows']} rows,"
        f" {manifest['unreadable']['already_filled']} filled)"
    )
    print(f"wrote {relabel.rel(args.manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
