#!/usr/bin/env python3
"""C1's second deliverable: the 66 registered sources in three lists, priced from the store.

SPEC v2 §3 splits the sources the operator will rule on into **A — retail chains and promo
aggregators** (stage 1), **B — Poltava region** (stage 2), and everything else — mothers,
health, recipes, fitness — which the revision PAUSES. This script writes that proposal, and
`config/registry.yaml` is not touched by it: the revision is a separate step, after the
operator rules.

Every number comes off `data/raw/`; nothing is typed. Two things make the rows readable:

* **The window is the store's own, not today's.** Each channel was backfilled 28 days back
  from its collection date (71 channels on 2026-08-07/08, the original four on 2026-07-27).
  So the denominator is 28 days per channel, ending where that channel was actually read —
  the same window length the live census uses, at an earlier date. A row that pretended to
  measure "the last four weeks from today" would read near-zero for every incumbent for a
  purely instrumental reason, and they would sort below every fresh candidate.
* **A missing comment rate is not a zero.** 66 sources, 23 joins, 20 comment files: about two
  thirds of the rows have no comment collection at all. `0.0` there says "nobody talks", and
  the truth is "nobody looked". Those rows carry ``None`` and a cause from `COMMENT_CAUSES`.

    PYTHONPATH=src python3 scripts/registry_revision_proposal.py
"""

import json
import sys
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed

from market_pulse.registry import load_registry  # noqa: E402

REGISTRY = REPO_ROOT / "config" / "registry.yaml"
STORE = REPO_ROOT / "data" / "raw"
JOIN_LOG = REPO_ROOT / "results" / "joins_5c1.jsonl"
REPORT = REPO_ROOT / "docs" / "reports" / "registry-revision-proposal.md"

WINDOW_DAYS = 28
"""The store's own backfill window (`scripts/collect_5c1.py::WINDOW_DAYS`), and the census's.
Both instruments measure over 28 days; only the date differs, and each row names its own."""

SPEC_V2_AGGREGATORS = {"kopiyochka1"}
"""Registered sources SPEC v2 §3 names in category A that `source_type` does not carry there.

«Копійочка» is listed among the promo aggregators of §3 and is registered `community` /
`supermarket_deals`. Named one by one, with the row saying which rule placed it: the alternative
is a classifier that quietly disagrees with the section it implements."""

COMMENT_CAUSES = (
    "measured",
    "comments_disabled",
    "group_never_joined",
    "joined_no_comments_collected",
)
"""Why a row has a comment rate, or has none. An empty class is several states
([[empty_field_hides_several_states]]): a channel whose group was never joined and one whose
joined group produced nothing are the same `0.0` and two different decisions."""


def store_rows(kind: str, stem: str) -> list[dict]:
    path = STORE / kind / f"{stem}.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def window_of(rows: list[dict]) -> tuple[date, date] | None:
    """The 28 days this channel was collected over: back from its own collection date.

    `provenance.collected_at` and not the last post date: a channel that went quiet a fortnight
    before the collector reached it was still READ over the full window, and anchoring on its
    last post would divide its posts by the span between them and call it a rate.
    """
    if not rows:
        return None
    end = max(row["provenance"]["collected_at"][:10] for row in rows)
    end_date = date.fromisoformat(end)
    return end_date - timedelta(days=WINDOW_DAYS - 1), end_date


def in_window(rows: list[dict], window: tuple[date, date]) -> list[dict]:
    start, end = window
    return [row for row in rows if start <= date.fromisoformat(row["date"][:10]) <= end]


def joined_groups() -> set[str]:
    """Channels whose discussion group this account is in — `results/joins_5c1.jsonl`."""
    if not JOIN_LOG.exists():
        return set()
    state: dict[str, str] = {}
    for line in JOIN_LOG.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            if row.get("outcome") in ("joined", "already_member", "left", "not_a_member"):
                state[row["channel"]] = row["outcome"]
    return {handle for handle, outcome in state.items() if outcome in ("joined", "already_member")}


def comment_rate(source, handle: str, stem: str, window, joined: set[str]) -> tuple:
    """(rate or None, cause). The cause is the point of the pair."""
    rows = store_rows("comments", stem)
    if rows:
        window = window or window_of(rows)
        return round(len(in_window(rows, window)) / WINDOW_DAYS, 2), "measured"
    if not source.comments_enabled:
        return None, "comments_disabled"
    if handle not in joined:
        return None, "group_never_joined"
    return None, "joined_no_comments_collected"


def bucket(source) -> str:
    """A · B · PAUSED, by SPEC v2 §3's own division."""
    if source.source_type in ("official_retail", "aggregator") or source.id in SPEC_V2_AGGREGATORS:
        return "A"
    if source.audience == "regional":
        return "B"
    return "PAUSED"


def row_for(source, handle: str, joined: set[str], today: date) -> dict:
    stem = handle.lstrip("@")
    posts = store_rows("posts", stem)
    window = window_of(posts)
    n_posts = len(in_window(posts, window)) if window else 0
    last_post = max((row["date"][:10] for row in posts), default=None)
    rate, cause = comment_rate(source, handle, stem, window, joined)
    return {
        "id": source.id,
        "name": source.name,
        "handle": handle,
        "bucket": bucket(source),
        "why": "SPEC v2 §3 names it" if source.id in SPEC_V2_AGGREGATORS else source.source_type,
        "audience": source.audience,
        "comments_enabled": source.comments_enabled,
        "posts_in_window": n_posts,
        "posts_per_day": round(n_posts / WINDOW_DAYS, 2) if window else None,
        "comments_per_day": rate,
        "comments_cause": cause,
        "watch": bool(getattr(source, "watch", False)),
        "window": f"{window[0]}..{window[1]}" if window else None,
        "last_post": last_post,
        "days_stale": (today - date.fromisoformat(last_post)).days if last_post else None,
    }


def md(text: str) -> str:
    """A cell that cannot break the row it sits in.

    Three registered channel names carry a literal «|» — «Полтава ІНФО | Новини Світло»,
    «КРЕМІНЬ | НОВИНИ | КРЕМЕНЧУК», «Катерина Ненька … | сон» — and an unescaped one silently
    shifts every column after it into the wrong header.
    """
    return text.replace("|", "\\|")


def table(rows: list[dict]) -> list[str]:
    out = [
        "| канал | handle | постов/день | комментов/день | окно стора | последний пост |"
        " простой, дн. |",
        "|---|---|---:|---:|---|---|---:|",
    ]
    for row in rows:
        comments = (
            f"{row['comments_per_day']:.2f}"
            if row["comments_per_day"] is not None
            else f"— _{row['comments_cause']}_"
        )
        posts = "—" if row["posts_per_day"] is None else f"{row['posts_per_day']:.2f}"
        out.append(
            f"| {md(row['name'])} | `{row['handle']}` | {posts} | {comments} |"
            f" {row['window'] or ('— watch, ни разу не собирался' if row['watch'] else '— нет в сторе')} | {row['last_post'] or '—'} |"
            f" {row['days_stale'] if row['days_stale'] is not None else '—'} |"
        )
    return out


def orphans(handles: set[str]) -> list[tuple[str, int, str]]:
    """Store files no registered source owns — measured channels the registry cannot reach.

    They are not part of the proposal's three lists and are printed beside it because two of
    them are SPEC v2 §3 names (`@znishkom` — Знижком) already carrying data.
    """
    stems = {handle.lstrip("@").lower() for handle in handles}
    found = []
    for path in sorted((STORE / "posts").glob("*.jsonl")):
        if path.stem.lower() in stems:
            continue
        rows = store_rows("posts", path.stem)
        last = max((row["date"][:10] for row in rows), default="—")
        found.append((f"@{path.stem}", len(rows), last))
    return sorted(found, key=lambda row: -row[1])


def render(rows: list[dict], today: date) -> str:
    counts = Counter(row["bucket"] for row in rows)
    causes = Counter(row["comments_cause"] for row in rows)
    handles = {row["handle"] for row in rows}
    lines = [
        "# Проект ревизии registry — 66 источников в трёх списках (контракт C1, SPEC v2 §3)",
        "",
        "**Правит только оператор.** Этот файл ничего не меняет в `config/registry.yaml`:"
        " ревизия — отдельный шаг после решения. Все числа сгенерированы"
        " `scripts/registry_revision_proposal.py` из `data/raw/` и `results/joins_5c1.jsonl`;"
        " ни одно не набрано руками.",
        "",
        f"**Окно — стора, а не сегодняшнее.** Каждый канал забэкфилен на {WINDOW_DAYS} дней назад"
        " от даты своего сбора (71 канал — 07–08.08.2026, первая четвёрка — 27.07.2026), поэтому"
        f" знаменатель у всех {WINDOW_DAYS} дней, но кончается окно там, где канал реально читали."
        f" Колонка «простой» — сколько дней прошло от последнего поста до {today.isoformat()}.",
        "",
        "**Пустая ставка комментов — не ноль.** 66 источников, 23 вступления"
        " (`results/joins_5c1.jsonl`), 20 файлов комментов. Там, где мерить было нечего, стоит"
        " прочерк с причиной, а не `0.00`: «в группу не входили» и «входили, комментов нет» —"
        " два разных решения.",
        "",
        "| список | каналов | что это | что предлагается |",
        "|---|---:|---|---|",
        f"| **A — торговые сети** | {counts['A']} | сети, их промо-каналы и агрегаторы скидок |"
        " остаются в сборе, этап 1 |",
        f"| **B — Полтавщина** | {counts['B']} | региональные каналы области |"
        " остаются в сборе, этап 2 (PR-мониторинг постов) |",
        f"| **PAUSED** | {counts['PAUSED']} | мамы · ЗОЖ · рецепты · фитнес · всё остальное |"
        " выводятся из сбора; данные и замороженные тесты остаются |",
        "",
        "Причины отсутствующей ставки комментов по всем 66: "
        + " · ".join(f"`{cause}` {n}" for cause, n in causes.most_common()),
        "",
    ]

    for name, title, note in (
        (
            "A",
            "A — торговые сети и агрегаторы промо (этап 1)",
            "SPEC v2 §3 считает здесь 9 «сейчас» — это ровно"
            " `source_type ∈ {official_retail, aggregator}`. Десятой строкой идёт «Копійочка»:"
            " §3 называет её среди промо-агрегаторов, а в registry она"
            " `community`/`supermarket_deals`. Колонка «правило» говорит, чем поставлена каждая"
            " строка. `@marketopt_promo` (Кременчук) стоит здесь, а не в B, потому что список"
            " сетей §3 сам называет Маркетопт/Толоку в категории A — из-за этого B ниже 17"
            " строк, а не 18, которые §3 называет «региональными».",
        ),
        (
            "B",
            "B — Полтавщина (этап 2)",
            "У всех комменты закрыты, 0 комментов в сторе — замер тимлида 27.08 подтверждается"
            " построчно ниже. Голос покупателя Полтавщины ищется темой `poltava_chats` в"
            " `docs/reports/retail-census.md`, а эти 17 остаются PR-мониторингом постов.",
        ),
        (
            "PAUSED",
            "PAUSED — мамы · ЗОЖ · рецепты · фитнес (выводятся из сбора)",
            "Ровно те, что не попали в A и B. Это те самые «~40 каналов» §3."
            " Семь строк с `watch, ни разу не собирался` — это `watch: true` из registry;"
            " комментарий самого registry обещает, что у них «posts are collected», а в сторе"
            " их файлов нет ни одного. Расхождение файла с миром, не дефект этого замера.",
        ),
    ):
        picked = [row for row in rows if row["bucket"] == name]
        picked.sort(key=lambda row: (-(row["posts_per_day"] or 0), row["handle"].lower()))
        lines += [f"## {title} — {len(picked)}", "", note, ""]
        if name == "A":
            lines.append(
                "Правило постановки: "
                + " · ".join(f"`{row['handle']}` → {row['why']}" for row in picked)
            )
            lines.append("")
        lines += table(picked)
        lines.append("")

    extra = orphans(handles)
    lines += [
        "## Вне трёх списков: файлы стора, которых нет в registry",
        "",
        "Каналы, измеренные гейтом 5c1 и не вошедшие (или выведённые) — они не часть ревизии,"
        " но `@znishkom` это «Знижком» из списка промо-агрегаторов SPEC v2 §3, и у него уже"
        f" {next((n for h, n, _ in extra if h.lower() == '@znishkom'), 0)} постов в сторе."
        " Оператору решать, входит ли он вместе с ревизией.",
        "",
        "| handle | постов в сторе | последний пост |",
        "|---|---:|---|",
    ]
    lines += [f"| `{handle}` | {n} | {last} |" for handle, n, last in extra]
    lines += [
        "",
        "---",
        f"Сгенерировано `scripts/registry_revision_proposal.py` {datetime.now().date()};"
        f" источник — `config/registry.yaml` ({len(rows)} источников), `data/raw/`,"
        " `results/joins_5c1.jsonl`. Ничего в registry не изменено.",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    today = date.fromisoformat((argv or [None])[0]) if argv else date.today()
    registry = load_registry(REGISTRY)
    joined = joined_groups()
    rows = [
        row_for(source, handle, joined, today)
        for source in registry.sources
        for handle in source.telegram_channels
    ]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(render(rows, today), encoding="utf-8")

    counts = Counter(row["bucket"] for row in rows)
    print(f"{len(rows)} sources: A {counts['A']} · B {counts['B']} · PAUSED {counts['PAUSED']}")
    for cause, n in Counter(row["comments_cause"] for row in rows).most_common():
        print(f"  {cause:<30}{n}")
    print(f"wrote {REPORT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
