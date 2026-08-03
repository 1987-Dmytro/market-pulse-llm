#!/usr/bin/env python3
"""The gate on the second round: 100 rows of the re-labelled batch, sealed and blind (4.5g3).

All three strata failed the first sitting, so the whole batch went back and was re-labelled
under `precheck_v2.1_with_post`. This seals the pack that decides whether that worked. It is
built and not judged: the verdicts belong to the operator's next sitting.

One hundred rows in one draw, not three hundreds. The first sitting's three strata were what
told it which part of the batch was weak; the question now is whether the batch as a whole
clears the bar, and a single frame answers that with a third of the evening. The cost is named
in the manifest rather than hidden: a pass here can still hold one class below 0.90, and the
strata table of the sitting it replaces is where a reader looks for that.

What it refuses:

- **judging a row whose right answer wrote the prompt.** The 300 the sitting judged are
  excluded from the frame. The v2.1 rulings were distilled from those verdicts, so scoring the
  second round on them would measure the prompt against its own source.
- **a batch that is not the one the re-run wrote.** `results/rerun_45g3.json` pins its sha256
  and the pack is built from that file or from none.
- **saying which stratum a row came from.** Same discipline as the first pack: no column, no
  order to read it off, and the map stays in the manifest.
- **overwriting an evening's work.** A pack already carrying verdicts is not rebuilt without
  `--force`, and `verdicts_present` records what was there at rebuild time.

    python3.11 scripts/build_wave2_pack.py

Writes `data/annotation/wave2_45g3/` (gitignored, like every pack) and the committed manifest
`results/wave2_45g3_manifest.json`.
"""

import argparse
import json
import random
import re
import sys
from collections import Counter
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_sitting_pack as builder  # noqa: E402
import relabel_intents as relabel  # noqa: E402
from build_audit_pack import git_state  # noqa: E402
from market_pulse import parents, prompts  # noqa: E402

PACK = REPO_ROOT / "data" / "annotation" / "wave2_45g3"
MANIFEST = REPO_ROOT / "results" / "wave2_45g3_manifest.json"
BATCH = REPO_ROOT / "data" / "annotation" / "uplabel_precheck_45g3.jsonl"
RERUN = REPO_ROOT / "results" / "rerun_45g3.json"
GATES = REPO_ROOT / "results" / "sitting_45g_gates.json"
CAPTIONS = REPO_ROOT / "data" / "annotation" / "post_captions.jsonl"
POSTS = REPO_ROOT / "data" / "raw" / "posts"

SEED = builder.SEED
BAR = builder.BAR
ROWS = 100
TASK = "precheck_v2.1_with_post"

RULE = (
    "agreement = rows marked `correct` / {rows} rows shipped. A row is `correct` only if EVERY"
    " field is right — sentiment, sarcasm, intents and unclear together; one wrong field makes"
    " the row `incorrect`. A blank cell or any other value counts as `incorrect`. The bar is"
    " >= {bar:.2f} on this one hundred. Registered before the pack was handed over and not"
    " recomputed on any other denominator."
)

README = """# Вторая волна 4.5g3 — один файл, 100 строк (~40 мин)

## ⚠️ ПРОЧТИ ПЕРВЫМ: переразметка, скорее всего, стала ХУЖЕ

Пакет собран, потому что этого требует бриф, но перед тем как тратить на него вечер,
посмотри на замеры прогона (`results/rerun_45g3.json`, `batch_health` в манифесте):

- **{changed} строк из {relabelled} ({changed_rate:.0%}) сменили поле** — это не точечная
  правка, это другая разметка;
- **из {stated} строк, где вердикт прямо назвал правильный ответ, промпт теперь верен
  на {landed}**;
- распределение интенций перевернулось: `service` {service_before} → {service_after},
  строк без интенции {none_before} → {none_after}, `price` {price_before} → {price_after};
- на строках, которые ты в прошлой сессии признал(а) верными, сменилось {kept_moved}
  из {kept} — это ровно тот знак, которого быть не должно.

Похоже, что виноват не смысл решений, а форма: блок v2.1 в промпте написан отрицаниями
(«не реакция», «never price», «carries no intent») и стоит последним перед форматом
ответа. Фаза стоила ${phase_spend:.4f} из ${cap:.2f}.

**Решение твоё**: поднять лимит и переписать блок v2.1 перед новой волной — или судить
эту сотню как есть. Пакет никуда не денется; если промпт починят, он будет замещён по
имени, как это уже делалось с `emptied40.csv`.

---

Первая сессия дала три страты ниже планки — 88% / 89% / 81% при планке 90%
(`results/sitting_45g_gates.json`). По зарегистрированному правилу страта ниже планки
отправляет назад **весь свой пласт**, а не показанную сотню, так что назад ушли все
{pool} строк. Их переразметили тем же моделью и тем же эндпоинтом, изменилось одно:
в промпт добавлены твои решения из той сессии (v2.1, `docs/annotation/comments.md`,
раздел «v2.1 changelog»).

Этот файл — гейт на переразметку. Заполняешь только `verdict` и `notes`; остальные
колонки не трогай, по ним harness сверяет вернувшийся файл.

| `verdict` | когда ставить |
|---|---|
| `correct` | верны ВСЕ четыре поля — `sentiment`, `sarcasm`, `intents`, `unclear` |
| `incorrect` | хотя бы одно поле неверно (напиши в `notes`, какое) |

**Формат интенций** — JSON-список: `["taste","service"]`. **`[]` — полноценный ответ.**
Шесть интенций v2: `taste`, `price`, `packaging`, `quality`, `availability`, `service`.

Колонка `post` показывает пост, под которым висит комментарий, с теми же пометками,
что видела модель: обычный текст — собственный текст поста, `[опрос] …` — вопрос опроса
из Telegram, `[картинка] …` — описание картинки vision-моделью, `(нет текста…)` — поста
не слышно вовсе.

**Сотня одна, а не три по сто.** Страты сделали свою работу в прошлой сессии: они
показали, где батч слабый. Здесь вопрос другой — вытянул ли батч целиком, — и на него
отвечает одна выборка. Плата за это записана в манифесте: сотня может пройти, а один
класс остаться ниже планки.

**Из выборки исключены 300 строк, которые ты уже судил(а)**: правила v2.1 выведены
именно из тех вердиктов, и мерить промпт на них — мерить его собственным источником.
Рамка выборки — {frame} строк, seed {seed}.
"""


ANNOTATOR = "llm-precheck-v2.1"
"""What a row this pack may gate has to say produced it. A row the re-run could not answer keeps
its previous labels and its previous annotator, and a hundred that quietly included one would
gate the old prompt under the new prompt's name."""

RULING = re.compile(
    r"(?:^|[;—-]\s*|\b)(sentiment|sarcasm|intents|unclear)\s+should be\s+"
    r"(true|false|positive|negative|neutral|\[[^\]]*\])",
    re.IGNORECASE,
)
"""The verdict notes that state the right answer outright. Only these are checkable — a note
saying a label is "unsupported by text" names the error and not the value."""


def frame(rows: list[dict], judged: set[str]) -> tuple[list[dict], list[str]]:
    """The rows this hundred may be drawn from, and the ones the re-run never answered.

    Two exclusions, both by id. The 300 the sitting judged are out because the v2.1 rulings were
    distilled from their verdicts, so a gate over them measures the prompt against its own
    source. A row the re-run could not answer is out because it still carries the labels the
    previous prompt produced.
    """
    stale = sorted(row["id"] for row in rows if row.get("annotator") != ANNOTATOR)
    keep = set(stale)
    return [row for row in rows if row["id"] not in judged and row["id"] not in keep], stale


def expected(note: str) -> dict:
    """The values a verdict note states outright, as a label dict — `{}` when it states none."""
    out = {}
    for field, value in RULING.findall(note):
        field = field.lower()
        raw = value.strip()
        if raw.startswith("["):
            try:
                out["intents"] = sorted(json.loads(raw))
            except ValueError:
                continue
        elif raw.lower() in ("true", "false"):
            out[field] = raw.lower() == "true"
        else:
            out[field] = raw.lower()
    return out


def rulings_landed(gates: dict, after: dict) -> dict:
    """Of the rows whose right answer the sitting wrote down, how many the re-run now gets.

    In-sample and named as such: these are the verdicts the v2.1 rulings were distilled from, so
    this is a check that the revision does what it says, not evidence that it generalises. It is
    the sharpest one available before the fresh hundred comes back — a revision that cannot fix
    the rows it was written for has nothing to offer the ones it was not.
    """
    hit, missed = [], []
    for row in gates["rows"]:
        if row["verdict"] == "correct" or row["id"] not in after:
            continue
        want = expected(row["notes"])
        if not want:
            continue
        got = after[row["id"]]
        ok = all(
            sorted(got["intents"]) == value if field == "intents" else got[field] == value
            for field, value in want.items()
        )
        (hit if ok else missed).append(row["id"])
    return {
        "rows_with_a_stated_answer": len(hit) + len(missed),
        "now_right": len(hit),
        "still_wrong": sorted(missed),
        "note": (
            "In-sample: the v2.1 rulings were written from these very verdicts. A revision that"
            " does not fix the rows it was written for has nothing to offer the ones it was not."
        ),
    }


def health(run: dict, before: list[dict], after: list[dict]) -> dict:
    """What the re-run did to the batch as a whole — read before the hundred is worth judging.

    A gate pack is a pre-registration, and pre-registering a gate over labels that already
    measure as a regression would pre-register a failure. The evidence is derived here rather
    than described, so nobody can open the pack without it.
    """

    def spread(rows):
        return {
            "intents": dict(
                Counter(intent for row in rows for intent in row["intents"]).most_common()
            ),
            "no_intent": sum(1 for row in rows if not row["intents"]),
            "unclear": sum(1 for row in rows if row["unclear"]),
            "sarcasm": sum(1 for row in rows if row["sarcasm"]),
        }

    kept = run["in_sample"]["judged_rows_re_asked"].get("correct", 0)
    spend = run["cost"]
    return {
        "phase_spend_usd": spend["phase_spend_usd"],
        "cap_usd": spend["cap_usd"],
        "headroom_usd": spend["cap_usd"] - spend["phase_spend_usd"],
        "read_this_first": (
            "The re-run moved a field in"
            f" {run['diff']['changed_any_field']} of {run['scope']['relabelled']} rows"
            f" ({run['diff']['changed_rate']:.0%}), and"
            f" {run['in_sample']['moved_a_field'].get('correct', 0)} of the {kept} rows the first"
            " sitting called CORRECT moved with them. That is the sign that should not appear:"
            " the v2.1 revision was meant to fix what the sitting refused, not to relabel what it"
            " accepted. Judge this hundred only after deciding that the re-run is worth gating."
        ),
        "changed_any_field": run["diff"]["changed_any_field"],
        "changed_rate": run["diff"]["changed_rate"],
        "per_field": run["diff"]["per_field"],
        "in_sample": run["in_sample"],
        "distribution_before": spread(before),
        "distribution_after": spread(after),
    }


def draw(pool: list[dict], rows: int) -> list[dict]:
    """`rows` from an id-sorted pool, then shuffled — the house convention, one frame."""
    if len(pool) < rows:
        raise SystemExit(f"the frame holds {len(pool)} rows, fewer than the {rows} asked for")
    picked = random.Random(SEED).sample(sorted(pool, key=lambda row: row["id"]), rows)
    random.Random(SEED).shuffle(picked)
    return picked


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, default=PACK)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--batch", type=Path, default=BATCH)
    parser.add_argument("--rerun", type=Path, default=RERUN)
    parser.add_argument("--gates", type=Path, default=GATES)
    parser.add_argument("--captions", type=Path, default=CAPTIONS)
    parser.add_argument("--posts", type=Path, default=POSTS)
    parser.add_argument("--rows", type=int, default=ROWS)
    parser.add_argument("--force", action="store_true", help="overwrite a pack being filled in")
    args = parser.parse_args(argv)

    gate_csv = args.pack / "wave2_100.csv"
    verdicts = builder.filled(gate_csv)
    if verdicts and not args.force:
        raise SystemExit(
            f"{relabel.rel(args.pack)} already carries {verdicts} verdicts — rebuilding would"
            " destroy them. --force if that is really what you want."
        )

    run = json.loads(args.rerun.read_text(encoding="utf-8"))["runs"][-1]
    found = sha256(args.batch.read_bytes()).hexdigest()
    if found != run["scope"]["batch_sha256"]:
        raise SystemExit(
            f"{relabel.rel(args.batch)}: sha256 {found[:16]}…, and {relabel.rel(args.rerun)}"
            f" recorded {run['scope']['batch_sha256'][:16]}…. This is not the batch the re-run"
            " wrote, so a pack drawn from it would gate a different set of labels."
        )
    if run["task"] != TASK or run["smoke"]:
        raise SystemExit(f"{relabel.rel(args.rerun)}: task {run['task']}, smoke {run['smoke']}")

    gates = json.loads(args.gates.read_text(encoding="utf-8"))
    judged = {row["id"] for row in gates["rows"]}
    rows = builder.load_batch(args.batch)
    was = builder.load_batch(REPO_ROOT / run["scope"]["source"])
    state = health(run, was, rows)
    state["rulings_landed"] = rulings_landed(gates, {row["id"]: row for row in rows})
    pool, stale = frame(rows, judged)
    state["rows_the_rerun_never_answered"] = stale
    drawn = draw(pool, args.rows)
    posts = parents.load(args.posts)
    captions = parents.load_captions(args.captions)

    shas = {
        "wave2_100.csv": builder.write_csv(
            gate_csv,
            builder.PRECHECK_COLUMNS,
            [
                {
                    "id": row["id"],
                    "post": builder.post_of(posts, captions, row),
                    "text": row["text"],
                    "sentiment": row["sentiment"],
                    "sarcasm": str(row["sarcasm"]).lower(),
                    "intents": builder.as_label(row["intents"]),
                    "unclear": str(row["unclear"]).lower(),
                    "verdict": "",
                    "notes": "",
                }
                for row in drawn
            ],
        )
    }
    readme = args.pack / "README-wave2.md"
    readme.write_text(
        README.format(
            pool=len(rows),
            frame=len(pool),
            seed=SEED,
            changed=state["changed_any_field"],
            relabelled=run["scope"]["relabelled"],
            changed_rate=state["changed_rate"],
            service_before=state["distribution_before"]["intents"].get("service", 0),
            service_after=state["distribution_after"]["intents"].get("service", 0),
            none_before=state["distribution_before"]["no_intent"],
            none_after=state["distribution_after"]["no_intent"],
            price_before=state["distribution_before"]["intents"].get("price", 0),
            price_after=state["distribution_after"]["intents"].get("price", 0),
            kept=state["in_sample"]["judged_rows_re_asked"].get("correct", 0),
            kept_moved=state["in_sample"]["moved_a_field"].get("correct", 0),
            stated=state["rulings_landed"]["rows_with_a_stated_answer"],
            landed=state["rulings_landed"]["now_right"],
            phase_spend=state["phase_spend_usd"],
            cap=state["cap_usd"],
        ),
        encoding="utf-8",
    )
    shas["README-wave2.md"] = sha256(readme.read_bytes()).hexdigest()

    manifest = {
        "pack": relabel.rel(args.pack),
        "seed": SEED,
        "bar": BAR,
        "delimiter": builder.DELIMITER,
        "verdicts_present": verdicts,
        "sha256": shas,
        "precheck": {
            "source": relabel.rel(args.batch),
            "source_sha256": found,
            "rows": len(drawn),
            "rule": RULE.format(rows=args.rows, bar=BAR),
            "verdicts": ["correct", "incorrect"],
            "frame": {
                "rows": len(pool),
                "of": len(rows),
                "excluded": sorted(judged),
                "why": (
                    "The 300 rows the first sitting judged are out of the frame. The v2.1"
                    " rulings were distilled from those verdicts, so a second round scored on"
                    " them would be measured against its own source. Excluded by id, because"
                    " what disqualifies a row is its verdict having been an input."
                ),
            },
            "one_frame_not_three": (
                "One hundred in one draw, unlike the 3x100 of results/sitting_45g2_manifest.json."
                " The strata did their work there — they located the weakness — and the question"
                " now is whether the batch as a whole clears the bar. The cost is real and named:"
                " a pass here can still hold one class below 0.90, and the per-stratum table of"
                " results/sitting_45g_gates.json is where a reader goes for that."
            ),
        },
        "prompt": {
            "task": TASK,
            "sha256": prompts.prompt_sha256(TASK),
            "registered_beside": {
                "precheck_v2_with_post": prompts.prompt_sha256("precheck_v2_with_post"),
                "T1v2.1": prompts.prompt_sha256("T1v2.1"),
            },
            "law": "docs/annotation/comments.md, section `v2.1 changelog`",
        },
        "batch_health": state,
        "sent_back_by": {
            "record": relabel.rel(args.gates),
            "bar": gates["bar"],
            "failed": gates["failed"],
            "strata": {name: block["agreement"] for name, block in gates["strata"].items()},
            "rows": gates["second_round_rows"],
        },
        "note": (
            "Built, not judged. The verdicts belong to the operator's next sitting, and nothing"
            " from the 1,912 rows merges into a train or candidates file until this hundred"
            " comes back at or above the bar. `verdicts_present` is measured at rebuild time:"
            " it is the evidence for `sealed before a single verdict existed`."
        ),
        "git": git_state(args.manifest),
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"{relabel.rel(args.pack)}")
    for name, digest in shas.items():
        print(f"  {name:<18} {digest}")
    print(f"\n  {state['read_this_first']}\n")
    print(
        f"  frame {len(pool)} of {len(rows)} rows ({len(judged)} already judged, excluded)"
        f"\n  drawn {len(drawn)} · seed {SEED} · bar {BAR:.0%}"
        f"\n  prompt {TASK} {manifest['prompt']['sha256'][:16]}…"
        f"\n  verdicts present at rebuild: {verdicts}"
        f"\nwrote {relabel.rel(args.manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
