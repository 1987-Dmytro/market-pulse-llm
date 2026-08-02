#!/usr/bin/env python3
"""The intents law-review pack: the guideline's empty-set rules beside the rows they decided.

Gate 4.5 left one question open. The audit's control sample says 22 of 40 `intents`
rows where both sides agreed carry a label the operator ruled wrong, and 19 of those
22 agreed on the **empty** set — which is not obviously a labelling error, because
the Phase-2 guideline sends several whole classes of comment to `[]` on purpose. Two
readings of the same rows, and choosing between them is a law decision, not a
measurement.

So this pack informs that decision and argues nothing:

- **the rules are sliced out of the guideline, never retyped.** Every quote is a
  span of ``docs/annotation/comments.md`` located by an anchor string and printed
  with the line numbers it came from. A paraphrase of a rule under review is an
  argument about it.
- **the rows carry their text and the label both sides agreed on, nothing else.**
  No counts by verdict inside a block, no ordering by anything but the pack's own,
  no note on why a row might go either way.
- **nothing names a side.** The finished file is swept for attribution vocabulary
  outside the quoted texts, the same rule the audit pack was built under.

    python3.11 scripts/build_intents_law_pack.py

Reads the filled control CSV and the guideline, writes
``data/annotation/audit_45a/intents-law-review.md``. Russian, because the operator
reads it — the sanctioned exception of docs/PROMPT-4.5c.md.
"""

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed

from market_pulse import audit  # noqa: E402

GUIDELINE = REPO_ROOT / "docs" / "annotation" / "comments.md"
GUIDELINE_REV = "0906de6"
"""The guideline revision this pack quotes — the law that was under review.

The pack asked one question: do these rules stay? The answer (SPEC amendment 3.8)
was that they largely do and that the taxonomy gains a sixth intent, which rewrote
the very spans quoted here. Reading the working tree would therefore re-issue a
pack quoting the law that *replaced* the one the operator ruled on. Pass
``--guideline-rev ''`` to quote the working tree instead."""
CONTROL = REPO_ROOT / "data" / "annotation" / "audit_45a" / "control.csv"
OUT = REPO_ROOT / "data" / "annotation" / "audit_45a" / "intents-law-review.md"
EMPTY = "[]"

QUOTES = (
    ("Схема поля", "| `intents` |", "\n"),
    ("Заполнение при `unclear`", "Fill `sentiment`, `sarcasm` and `intents`", "\n\n"),
    ("Раздел `## intents` целиком", "## intents", "\n## "),
    ("Правило: только эмодзи", "**Emoji-only comments.**", "\n\n"),
    ("Правило: боты и розыгрыши", "**Bot spam and giveaway noise.**", "\n\n"),
    ("Правило: сервисные жалобы не про товар", "**Off-topic replies.**", "\n\n"),
)
"""Which spans of the guideline are the law here, as (title, first line, stop at).

Anchors rather than line numbers: a line number in a script is a claim about a file
that nothing checks, and the guideline is a living document. The stop marker is
exclusive, so a paragraph ends at its blank line and a section at the next heading."""

HEADER = """# Интенции: сверка закона (4.5c)

**Что это.** Слепой арбитраж 4.5a закончен. По интенциям остался один вопрос, и он
не про числа: в контрольной выборке (строки, где обе стороны сошлись на одной метке)
{incorrect_empty} строк с меткой `{empty}` ты пометил как неверные. Гайдлайн Phase 2
отправляет в `{empty}` несколько классов комментариев намеренно — ниже его правила
**дословно**, а рядом сами строки.

**Что с этим делать.** Прочитать правила, прочитать строки, решить на следующем
гейте: правила остаются как есть (и тогда часть этих строк размечена по правилам) или
правила меняются (и тогда меняется разметка). Документ ничего не предлагает и ничего
не рекомендует — в нём нет ни выводов, ни счётчиков «за» и «против».

**Как читать блоки.** В каждом блоке — текст комментария и метка, на которой сошлись
обе стороны. Больше в блоке нет ничего: ни кто её поставил, ни как её оценили.

Всего блоков: {total} ({incorrect_empty} + {correct_empty} + {incorrect_other}).
"""

SECTIONS = (
    (
        "incorrect_empty",
        "Строки с меткой `[]`, помеченные как неверные",
        "Обе стороны сошлись на пустом наборе; твой вердикт — метка неверна.",
    ),
    (
        "correct_empty",
        "Для контраста: строки с меткой `[]`, помеченные как верные",
        "Тот же пустой набор, тот же вопрос — здесь вердикт был «метка верна».",
    ),
    (
        "incorrect_other",
        "Строки с непустой меткой, помеченные как неверные",
        "Здесь набор не пуст; блоки приведены полностью, как и остальные.",
    ),
)


def span(text: str, first: str, stop: str) -> tuple[str, int, int]:
    """One verbatim slice of the guideline, with the line numbers it occupies."""
    start = text.find(first)
    if start < 0:
        raise SystemExit(
            f"{GUIDELINE.name}: the anchor {first!r} is gone, so the rule it quotes cannot be"
            " quoted verbatim. Re-point the anchor at the text that replaced it."
        )
    end = text.find(stop, start + len(first))
    body = text[start : end if end > 0 else len(text)].rstrip()
    return body, text[:start].count("\n") + 1, text[:start].count("\n") + body.count("\n") + 1


def guideline_text(path: Path, rev: str) -> str:
    """The guideline as of ``rev``, or the working tree when ``rev`` is empty."""
    if not rev:
        return path.read_text(encoding="utf-8")
    where = path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path
    done = subprocess.run(
        ["git", "show", f"{rev}:{where.as_posix()}"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if done.returncode:
        raise SystemExit(f"git show {rev}:{where}: {done.stderr.strip()}")
    return done.stdout


def groups(rows: list[dict]) -> dict[str, list[dict]]:
    """The three groups the pack shows, in the pack's own row order."""
    intents = [row for row in rows if row["head"] == "intents"]
    return {
        "incorrect_empty": [
            r for r in intents if r["verdict"] == "incorrect" and r["label"] == EMPTY
        ],
        "correct_empty": [r for r in intents if r["verdict"] == "correct" and r["label"] == EMPTY],
        "incorrect_other": [
            r for r in intents if r["verdict"] == "incorrect" and r["label"] != EMPTY
        ],
    }


def render(rows: list[dict], guideline: str) -> str:
    """The finished pack."""
    found = groups(rows)
    counts = {name: len(rows) for name, rows in found.items()}
    out = [
        HEADER.format(empty=EMPTY, total=sum(counts.values()), **counts),
        "## 1. Правила — дословно из гайдлайна\n",
    ]
    for title, first, stop in QUOTES:
        body, start, end = span(guideline, first, stop)
        out.append(f"**{title}** — `docs/annotation/comments.md`, строки {start}–{end}:\n")
        out.append("```markdown\n" + body + "\n```\n")

    for index, (name, title, lead) in enumerate(SECTIONS, start=2):
        rows_here = found[name]
        out.append(f"## {index}. {title} ({len(rows_here)})\n")
        out.append(lead + "\n")
        for number, row in enumerate(rows_here, start=1):
            out.append(f"### {number}/{len(rows_here)} · `{row['id']}`\n")
            out.append("```text\n" + row["text"].replace("```", "'''") + "\n```\n")
            out.append(f"Метка, на которой сошлись обе стороны: `{row['label']}`\n")
    return "\n".join(out)


def attribution(page: str) -> list[str]:
    """Attribution words outside the quoted row texts — the audit pack's own rule.

    A comment may contain any of these and dropping such a row would bias the pack,
    so the fenced blocks are skipped and everything else is checked.
    """
    outside, fenced = [], False
    for line in page.splitlines():
        if line.startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            outside.append(line.casefold())
    return sorted({word for word in audit.ATTRIBUTION if any(word in line for line in outside)})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control", type=Path, default=CONTROL)
    parser.add_argument("--guideline", type=Path, default=GUIDELINE)
    parser.add_argument("--guideline-rev", default=GUIDELINE_REV)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)

    with args.control.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != audit.CONTROL_COLUMNS:
            raise SystemExit(f"{args.control}: not the pack's control CSV")
        rows = list(reader)
    if empty := [
        row["id"] for row in rows if row["head"] == "intents" and not row["verdict"].strip()
    ]:
        raise SystemExit(f"{len(empty)} intents control rows are unruled ({empty[:3]}) — no pack")

    page = render(rows, guideline_text(args.guideline, args.guideline_rev))
    if leaked := attribution(page):
        raise SystemExit(
            f"{args.out.name}: the prose outside the quoted texts carries {leaked}."
            " The pack informs a law decision and may not say which side produced a label."
        )
    args.out.write_text(page, encoding="utf-8")

    counts = {name: len(rows) for name, rows in groups(rows).items()}
    where = args.out.relative_to(REPO_ROOT) if args.out.is_relative_to(REPO_ROOT) else args.out
    print(f"{where}  ({len(page.encode('utf-8'))} bytes)")
    print(f"  rows: {json.dumps(counts)} · quotes: {len(QUOTES)} spans, sliced from the guideline")
    print("  attribution sweep outside the quoted texts: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
