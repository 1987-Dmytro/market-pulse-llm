#!/usr/bin/env python3
"""The operator's sitting: 300 precheck rows, the emptied rows still open, 14 to label (4.5g2).

Three files, three questions, one manifest — and the denominators are written before the
pack is handed over, not after the verdicts come back.

- **`precheck300.csv`** is the gate. 100 rows from each of three strata, judged row by
  row: a row is `correct` only if **every** field is (sentiment, sarcasm, intents,
  unclear). A stratum below the bar sends its whole batch back — that batch is the whole
  stratum in the pool, whose size is in the manifest, not the 100 shown here.
- **`emptied_redo.csv`** is what is left of the 97 after the 11/20 quiz: the rows it did not
  close, decided by hand, with the post in front of the operator this time.
- **`unreadable14.csv`** is the 4.5f micro-pack, pinned where it already lives. It is not
  copied here: a second copy of a file the operator may already be filling in is how one
  evening's work ends up in the file nobody reads.

Beside them, `media_map.csv` and `posts_media/` — the images and poll questions 4.5g2 fetched
for the posts that had no text of their own.

What the pack refuses:

- **saying which stratum a row is in.** One file, one seeded shuffle over all 300 after the
  three draws, no stratum column and no order to read it off. The map lives in the manifest
  for the reader, exactly as `build_calibration_pack.py` keeps its composition out of the
  pack — a pack that describes itself is not blind.
- **judging under a stricter law than the one that wrote the labels.** The parent post is
  shown, because `docs/annotation/comments.md` §Unit lets the annotator read it and the
  model was given it — and where the post has no text of its own, the operator sees the same
  surrogate the model saw, tagged the same way.
- **a reseal that quietly redraws the sample.** The 300 ids and their strata are asserted
  against the manifest being superseded; that manifest is named in the new one and never
  edited, and `emptied40.csv` is left on disk byte-identical so its pinned sha still verifies.
- **overwriting an evening's work.** A pack already carrying verdicts is not rebuilt
  without `--force`, `verdicts_present` records what was there at rebuild time, and a bundled
  file whose sha256 has moved since its own manifest stops the build.

    python3.11 scripts/build_sitting_pack.py

Writes `data/annotation/sitting_45g/` (gitignored, like every pack) and the committed
manifest `results/sitting_45g2_manifest.json`.
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
from recheck_with_captions import closed_ids  # noqa: E402
from relabel_emptied import population as emptied_population  # noqa: E402
from market_pulse import parents  # noqa: E402

PACK = REPO_ROOT / "data" / "annotation" / "sitting_45g"
MANIFEST = REPO_ROOT / "results" / "sitting_45g2_manifest.json"
SUPERSEDES = REPO_ROOT / "results" / "sitting_45g_manifest.json"
BATCH = REPO_ROOT / "data" / "annotation" / "uplabel_precheck_45g2.jsonl"
CAPTIONS = REPO_ROOT / "data" / "annotation" / "post_captions.jsonl"
MEDIA_MANIFEST = REPO_ROOT / "results" / "post_media_45g2.json"
REDO_ROWS = REPO_ROOT / "results" / "redo_45g2_rows.jsonl"
QUIZ_RECORD = REPO_ROOT / "results" / "quiz_rulings_45g2.json"
DROP = REPO_ROOT / "results" / "drop_45f.json"
RELABEL_RECORD = REPO_ROOT / "results" / "relabel_45e.json"
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
REDO_COLUMNS = (
    "id",
    "post",
    "post_media",
    "caption",
    "text",
    "intents_v1",
    "intents_model",
    "intents_final",
    "notes",
)
"""`post` is not in the 4.5g2 brief's column list and is here anyway: 71 of the 75 redo rows
hang under a post that HAS text, and `caption` only ever speaks for the ones that do not.
Shipping the list as written would have handed the operator 71 rows to judge blind, which is
the defect this phase exists to remove."""

MEDIA_COLUMNS = ("id", "channel", "parent_msg_id", "kind", "caption", "images")

SHOWN = {
    "post_text": "{text}",
    "image_caption": "[картинка] {text}",
    "poll_text": "[опрос] {text}",
    "no_text_and_no_caption": "(нет текста — ни картинки, ни опроса)",
}
"""How a post reaches the operator, tagged exactly as it reached the model
(`prompts.POST_SURROGATE`). Judging a description as if it were the post's own words is the
same error on either side of the table."""

PRECHECK_RULE = (
    "Per stratum: agreement = rows marked `correct` / {rows} rows of that stratum shipped."
    " A row is `correct` only if EVERY field is right — sentiment, sarcasm, intents and"
    " unclear together; one wrong field makes the row `incorrect`. A blank cell or any other"
    " value counts as `incorrect`. Each stratum passes at >= {bar:.2f} on its own; a stratum"
    " below the bar sends its WHOLE batch back for re-labelling, not just the 100 shown."
    " Registered before the pack was handed over and not recomputed on any other denominator."
)

README = """# Сессия вердиктов 4.5g2 — три файла, ~2.5–3 ч

Пересобрано 03.08 ДО первого вердикта: старый пакет 4.5g никто не заполнял
(в манифесте это записано числом, `verdicts_present: 0`). `emptied40.csv`
лежит рядом и **СУПЕРСЕДЕД — не заполняй его**, вместо него `emptied_redo.csv`.

Разделитель во всех файлах — `;`. Заполняй только `verdict` / `intents_final` и
`notes`. Остальные колонки не трогай: по ним harness сверяет вернувшийся файл с
манифестом `results/sitting_45g2_manifest.json` и откажется считать, если они
разошлись.

**Формат интенций** — JSON-список: `["taste","service"]`, одна метка — `["taste"]`.
**`[]` — это полноценный ответ**, а не пропуск: комментарий ни о чём из шести.
Шесть интенций v2: `taste`, `price`, `packaging`, `quality`, `availability`,
`service`.

## Что теперь показывает колонка `post`

По гайдлайну (`docs/annotation/comments.md`, §Unit) пост читать можно и нужно
тогда, когда без него комментарий бессмыслен (`Так`, `+`, `А коли?`). Раньше у
41 поста текста не было вовсе. Теперь:

- обычный текст — это собственный текст поста;
- `[опрос] …` — вопрос опроса и варианты ответа, взяты из самого Telegram
  (16 постов; коллектор их не сохранял, поле в API было всё это время);
- `[картинка] …` — описание картинки vision-моделью `qwen/qwen3.5-flash-02-23`
  (21 пост). Это ОПИСАНИЕ, а не слова поста — читай с этой поправкой;
- `(нет текста — ни картинки, ни опроса)` — 4 поста: видео, голосовое и два
  розыгрыша. Этих строк мало, и они честно пустые.

Модель видела ровно то же самое и с теми же пометками.

**Сами картинки лежат рядом**: `posts_media/<канал>_<msg_id>.jpg`, а
`media_map.csv` сопоставляет строку с файлами её поста. Если описание кажется
подозрительным — открой картинку.

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
части выборки строка — так и задумано. Те же 300 id, что и в пакете 4.5g;
{refreshed} из них переспросили с постом-суррогатом, остальные не трогали.

Планка ≥ {bar:.0%} считается ОТДЕЛЬНО по трём стратам, их состав в манифесте. Страта
ниже планки отправляет назад весь свой пласт корпуса, а не эти сто строк.

## 2. `emptied_redo.csv` — {redo} строк, руками (~40 мин)

Это остаток тех 97 строк, у которых переразметка 4.5e сняла интенцию в ноль.
Квиз в чате дал 11/20 при планке 18/20 — автопочинка отклонена. {closed} строки
закрыты (11 твоих вердиктов + 9 по проверенному правилу «короткий ответ-начинка
под постом без текста» + 2 старых вердикта 4.5f), остальные — здесь, и теперь
уже с постом.

Заполняешь **`intents_final`** — правильный набор, JSON-списком. `intents_v1` —
старая ручная метка, `intents_model` — что говорит модель, увидев пост. Обе
колонки справочные; пустой `intents_model` значит, что модель не дала читаемый
ответ ({redo_blank} строк).

Твои прежние вердикты по 9 разошедшимся строкам сюда НЕ перенесены: они были
даны вслепую, без поста. Реши заново.

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


def post_of(posts: dict, captions: dict, row: dict) -> str:
    """What the operator is shown in the post's place, tagged as the model was shown it."""
    found = parents.context(posts, captions, row)
    return SHOWN[found["state"]].format(text=(found["caption"] or found["parent"]).strip())


def media_rows(posts: dict, captions: dict, media: dict, rows: list[dict]) -> list[dict]:
    """One line per row whose post has no text of its own: what spoke for it, and from where."""
    out = []
    for row in rows:
        found = parents.context(posts, captions, row)
        if found["state"] == "post_text":
            continue
        key = f"{row['channel']}:{row['parent_msg_id']}"
        entry = media["entries"].get(key, {})
        out.append(
            {
                "id": row["id"],
                "channel": row["channel"],
                "parent_msg_id": row["parent_msg_id"],
                "kind": found["caption_kind"] or "—",
                "caption": (found["caption"] or "").replace("\n", " ⏎ "),
                "images": "|".join(Path(item["file"]).name for item in entry.get("images", [])),
            }
        )
    return sorted(out, key=lambda entry: entry["id"])


def as_label(intents: list[str]) -> str:
    return json.dumps(sorted(intents), ensure_ascii=False)


def micro_rows(manifest: Path, labelled: dict, root: Path = REPO_ROOT) -> list[dict]:
    """The unreadable rows of the pinned micro-pack, as comment rows — ids only, never labels."""
    sealed = json.loads(manifest.read_text(encoding="utf-8"))
    with (root / sealed["pack"]).open(encoding="utf-8-sig", newline="") as handle:
        ids = [row["id"] for row in csv.DictReader(handle, delimiter=DELIMITER)]
    if missing := [row_id for row_id in ids if row_id not in labelled]:
        raise SystemExit(f"{sealed['pack']}: {missing} are not rows of the labelled sources")
    return [labelled[row_id] for row_id in ids]


def redo_population(drop: Path, run: Path, quiz: Path, labelled: dict) -> list[dict]:
    """The emptied rows the quiz did not close, each with its v1 label and its comment row.

    Derived, not listed: the 97 come back from `measure_empty_drop`'s own functions checked
    against `results/drop_45f.json`, and what is subtracted is exactly what the ruling record
    says it closed. A hand-written id list here would drift the day another ruling lands.
    """
    closed = closed_ids(quiz)
    return [
        {**labelled[row["id"]], "before": row["before"]}
        for row in emptied_population(drop, run)
        if row["id"] not in closed
    ]


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
    parser.add_argument("--captions", type=Path, default=CAPTIONS)
    parser.add_argument("--media-manifest", type=Path, default=MEDIA_MANIFEST)
    parser.add_argument("--redo-rows", type=Path, default=REDO_ROWS)
    parser.add_argument("--quiz-record", type=Path, default=QUIZ_RECORD)
    parser.add_argument("--drop", type=Path, default=DROP)
    parser.add_argument("--relabel-record", type=Path, default=RELABEL_RECORD)
    parser.add_argument("--supersedes", type=Path, default=SUPERSEDES)
    parser.add_argument("--micro-manifest", type=Path, default=MICRO_MANIFEST)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--posts", type=Path, default=POSTS)
    parser.add_argument("--per-stratum", type=int, default=PER_STRATUM)
    parser.add_argument("--force", action="store_true", help="overwrite a pack being filled in")
    args = parser.parse_args(argv)

    precheck_csv = args.pack / "precheck300.csv"
    redo_csv = args.pack / "emptied_redo.csv"
    # `emptied40.csv` is superseded, not rebuilt: it is left on disk byte-identical so that what
    # results/sitting_45g_manifest.json pinned still verifies, and the README says not to fill it.
    verdicts = (
        filled(precheck_csv)
        + filled(args.pack / "emptied40.csv")
        + filled(redo_csv, "intents_final")
    )
    if verdicts and not args.force:
        raise SystemExit(
            f"{relabel.rel(args.pack)} already carries {verdicts} verdicts — rebuilding would"
            " destroy them. --force if that is really what you want."
        )

    rows = load_batch(args.batch)
    posts = parents.load(args.posts)
    captions = parents.load_captions(args.captions)
    media = json.loads(args.media_manifest.read_text(encoding="utf-8"))
    pools = strata(rows)
    drawn, where = draw(pools, args.per_stratum)
    labelled = {
        row["id"]: row for source in relabel.SOURCES.values() for row in relabel.load(source)[0]
    }

    # The same 300, asserted rather than reasoned about: the population did not change, so the
    # seed-42 draw must not have either, and a manifest that claims "same draw" has to prove it.
    sealed = json.loads(args.supersedes.read_text(encoding="utf-8"))
    if where != sealed["precheck"]["stratum_of"]:
        raise SystemExit(
            "the draw moved: this pack does not hold the same 300 ids in the same strata as"
            f" {relabel.rel(args.supersedes)}. Refreshing labels was supposed to leave the sample"
            " alone, so something upstream of the draw changed and the two sittings are not"
            " comparable."
        )

    # verified before anything reads its rows: a bundled file whose bytes moved is a stop, and
    # a stop that fires after the pack has been rewritten is not a guard.
    unreadable = bundled(args.micro_manifest, args.root)
    redo = redo_population(args.drop, args.relabel_record, args.quiz_record, labelled)
    model_intents = (
        {row["id"]: row["intents"] for row in relabel.load(args.redo_rows)[0]}
        if args.redo_rows.exists()
        else {}
    )

    shas = {
        "precheck300.csv": write_csv(
            precheck_csv,
            PRECHECK_COLUMNS,
            [
                {
                    "id": row["id"],
                    "post": post_of(posts, captions, row),
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
        "emptied_redo.csv": write_csv(
            redo_csv,
            REDO_COLUMNS,
            [
                {
                    "id": row["id"],
                    "post": post_of(posts, captions, row),
                    "post_media": "|".join(
                        Path(item["file"]).name
                        for item in media["entries"]
                        .get(f"{row['channel']}:{row['parent_msg_id']}", {})
                        .get("images", [])
                    ),
                    "caption": (captions.get((row["channel"], row["parent_msg_id"])) or {})
                    .get("text", "")
                    .replace("\n", " ⏎ "),
                    "text": row["text"],
                    "intents_v1": as_label(row["before"]),
                    "intents_model": (
                        as_label(model_intents[row["id"]]) if row["id"] in model_intents else ""
                    ),
                    "intents_final": "",
                    "notes": "",
                }
                for row in redo
            ],
        ),
        "media_map.csv": write_csv(
            args.pack / "media_map.csv",
            MEDIA_COLUMNS,
            media_rows(
                posts,
                captions,
                media,
                drawn + redo + micro_rows(args.micro_manifest, labelled, args.root),
            ),
        ),
    }
    rule = PRECHECK_RULE.format(rows=args.per_stratum, bar=BAR)
    readme = args.pack / "README-sitting.md"
    readme.write_text(
        README.format(
            precheck=len(drawn),
            pool=len(rows),
            seed=SEED,
            bar=BAR,
            redo=len(redo),
            closed=len(closed_ids(args.quiz_record)),
            redo_blank=sum(1 for row in redo if row["id"] not in model_intents),
            refreshed=sum(
                1 for row in drawn if parents.context(posts, captions, row)["state"] != "post_text"
            ),
        ),
        encoding="utf-8",
    )
    shas["README-sitting.md"] = sha256(readme.read_bytes()).hexdigest()

    manifest = {
        "pack": relabel.rel(args.pack),
        "seed": SEED,
        "bar": BAR,
        "delimiter": DELIMITER,
        "verdicts_present": verdicts,
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
        "redo": {
            "rows": len(redo),
            "population": "the 97 the 4.5e re-label emptied",
            "closed_before_this": sorted(closed_ids(args.quiz_record)),
            "to_fill": "intents_final",
            "with_a_model_column": sum(1 for row in redo if row["id"] in model_intents),
            "model_source": relabel.rel(args.redo_rows),
            "rule": (
                "The 11/20 quiz failed its pre-registered 18/20, so these rows are decided by"
                " hand, one JSON list per row in `intents_final`. `[]` is an answer. The nine"
                " rows whose blind verdict diverged from the policy are in here unresolved on"
                " purpose: they were ruled without the post, which is the defect being fixed."
            ),
        },
        "media": {
            "captions": relabel.rel(args.captions),
            "captions_sha256": sha256(args.captions.read_bytes()).hexdigest(),
            "manifest": relabel.rel(args.media_manifest),
            "images": relabel.rel(args.root / "data/annotation/sitting_45g/posts_media"),
            "rows_with_a_surrogate": len(shas)
            and sum(
                1
                for row in drawn + redo
                if parents.context(posts, captions, row)["state"] != "post_text"
            ),
            "note": (
                "`[опрос] …` is Telegram's own poll question, `[картинка] …` a vision model's"
                " description — tagged for the operator exactly as prompts.POST_SURROGATE tags"
                " them for the model. media_map.csv maps a row to the image files of its post."
            ),
        },
        "unreadable": unreadable,
        "supersedes": {
            "manifest": relabel.rel(args.supersedes),
            "sha256": sealed["sha256"],
            "same_draw": "the same 300 ids in the same strata, asserted against stratum_of",
            "what_moved": (
                "precheck300.csv carries the labels of the caption-fed re-precheck;"
                " emptied40.csv is replaced by emptied_redo.csv and is left on disk unchanged so"
                " that the sha the old manifest pinned still verifies. The old manifest is not"
                " edited and not deleted — supersession is by naming."
            ),
        },
        "note": (
            "Three questions, one sitting. `precheck300.csv` is the gate on the up-label"
            " precheck and nothing merges into a train or candidates file until every stratum"
            " passes. Nothing in any pack file says which stratum a row is in; `stratum_of` is"
            " here because the reader needs it and the operator must not have it."
            " `verdicts_present` is measured at rebuild time: it is the evidence for `rebuilt"
            " before a single verdict existed`, which is otherwise only a sentence in a report."
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
        f"  emptied_redo.csv {len(redo)} rows, {manifest['redo']['with_a_model_column']} with a"
        f" model column\n  media_map.csv {manifest['media']['rows_with_a_surrogate']} rows whose"
        " post speaks through a surrogate"
        f"\n  bundled {manifest['unreadable']['pack']} ({manifest['unreadable']['rows']} rows,"
        f" {manifest['unreadable']['already_filled']} filled)"
        f"\n  verdicts present at rebuild: {verdicts}"
    )
    print(f"wrote {relabel.rel(args.manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
