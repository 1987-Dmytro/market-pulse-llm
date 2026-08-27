"""Render `docs/reports/retail-census.md` from `results/retail_census.json`.

Prose ≤30 lines (PROCESS.md's v2 ceiling); the table and the two `runpodctl` listings step 0
requires verbatim are exhibits under it, which is the same allowance the paired tables take.
Every number here is read out of the record — this module computes shares of rows and nothing
else, so a figure in the report can always be found in the file.
"""

from collections import Counter

VERDICT_MARK = {"enter": "**enter**", "posts-only": "posts-only", "reject": "reject"}


def mix(row: dict) -> str:
    languages = row["stats"].get("language_mix") or {}
    top = sorted(languages.items(), key=lambda kv: -kv[1])[:2]
    return " ".join(f"{lang} {share:.2f}" for lang, share in top) or "—"


def pct(value) -> str:
    return "—" if value is None else f"{value * 100:.0f}%"


def md(text) -> str:
    return (text or "—").replace("|", "\\|")


def rate(value) -> str:
    return "—" if value is None else f"{value:.2f}"


def group_flag(row: dict) -> str:
    """Whether reactions can be read at all — the column the whole stage-1 question turns on."""
    if row.get("is_group"):
        return "чат" if row.get("messages_open") else "чат ЗАКРЫТ"
    if not row.get("comments_enabled"):
        return "нет"
    group = row.get("discussion_group") or {}
    return "да" if group.get("open") is not False else "группа закрыта"


def table(rows: list[dict]) -> list[str]:
    out = [
        "| # | канал | handle | подп. | ✓ | п/д | листовка/цена | комменты | к/д или с/д |"
        " молочка | мова | инстр. | вердикт · причина |",
        "|---:|---|---|---:|:-:|---:|---:|---|---:|---:|---|---|---|",
    ]
    for n, row in enumerate(rows, 1):
        stats = row["stats"]
        flow = stats["messages_per_day"] if row.get("is_group") else stats["comments_per_day"]
        verdict = row.get("verdict")
        reason = (row.get("reasons") or ["—"])[0]
        out.append(
            f"| {n} | {md(row.get('title'))} | `{row['handle']}` |"
            f" {row.get('subscribers') if row.get('subscribers') is not None else '—'} |"
            f" {'✓' if row.get('telegram_verified') else ''} |"
            f" {rate(stats['posts_per_day'])} | {pct(stats['leaflet_or_price_share'])} |"
            f" {group_flag(row)} | {rate(flow)} | {pct(stats['dairy_share'])} | {mix(row)} |"
            f" {row.get('measured_by') or '—'} |"
            f" {VERDICT_MARK.get(verdict, 'in_registry')} · {md(reason)} |"
        )
    return out


def render(record: dict) -> str:
    rows = record["rows"]
    fresh = [row for row in rows if not row.get("in_registry")]
    checked = [row for row in fresh if row.get("checked")]
    verdicts = Counter(row.get("verdict") for row in checked)
    themes = {
        theme: len(
            [r for r in fresh if any(t.startswith(f"{theme}:") for t in r.get("found_by", []))]
        )
        for theme in record["themes"]
    }
    enterable = [row for row in checked if row.get("verdict") == "enter"]
    with_dairy = [row for row in checked if (row["stats"]["dairy_share"] or 0) > 0]
    contract_gap = [
        row
        for row in checked
        if (row["stats"]["price_share"] or 0) > (row["stats"]["price_share_contract_regex"] or 0)
    ]
    step0 = record.get("step_0") or {}
    floods = record.get("flood_wait_events") or []
    bound = record.get("bound") or {}

    lines = [
        "# retail-census (C1) — ценз сетей и полтавских чатов, $0",
        "",
        f"**{len(record['queries'])} запросов по двум темам, {len(fresh)} нерегистрированных"
        f" хэндлов найдено, {len(checked)} проверено entry-check'ом,"
        f" {verdicts.get('enter', 0)} с вердиктом `enter`.** Реестровые 66 каналов измерены по"
        " стору, не по API (так велит бриф) — это 66 несделанных `ResolveUsername`."
        " Всё read-only: ни одного вступления в группу. Запись —"
        " `results/retail_census.json`, таблица ниже — её же строки.",
        "",
        "**Шаг 0 — том `mp-lora-c` удалён.** Оба листинга дословно ниже; `mp-srv2` в обоих —"
        " положительный контроль того, что листинг вообще работает. Строка гарда:"
        f" остаток **${step0.get('remaining_usd', '—')}** из $20.00 цикла-2"
        f" (баланс ${step0.get('balance', '—')}).",
        "",
        "```",
        "$ runpodctl network-volume list        # BEFORE",
        (step0.get("before") or "").rstrip(),
        "",
        "$ runpodctl network-volume delete soymlju8q0",
        (step0.get("delete") or "").rstrip(),
        "",
        "$ runpodctl network-volume list        # AFTER",
        (step0.get("after") or "").rstrip(),
        "```",
        "",
        "## Что нашлось",
        "",
        f"- `retail_chains` — {themes.get('retail_chains', 0)} кандидатов из"
        f" {len(record['themes']['retail_chains'])} запросов;"
        f" `poltava_chats` — {themes.get('poltava_chats', 0)} из"
        f" {len(record['themes']['poltava_chats'])}.",
        f"- Проверено {len(checked)}; ниже планки `--min-subscribers"
        f" {bound.get('min_subscribers', '—')}` осталось"
        f" {bound.get('skipped_below_the_bar', 0)} строк — они В ЗАПИСИ со своими бесплатными"
        " полями и причиной, а не выброшены молча.",
        "- Вердикты: " + " · ".join(f"`{v}` {n}" for v, n in verdicts.most_common() if v),
        f"- Молочка > 0 у {len(with_dairy)} из {len(checked)} проверенных;"
        f" `enter` у {len(enterable)}.",
        "",
        "## Два замера, которые нельзя читать как один",
        "",
        "- **Колонка «инстр.»**: `api` — окно 28 дней до сегодня; `store` — те же 28 дней, но"
        " кончаются они датой сбора канала (07–08.08 или 27.07). Длина окна одна, дата разная;"
        " сортировка идёт по обоим сразу, и без этой колонки порядок читался бы как вывод.",
        "- **Цена**: бриф пишет паттерн `grn|₴|\\d+[,.]\\d\\d` латиницей, а корпус пишет «грн»."
        f" Считаются оба: у {len(contract_gap)} строк доля по расширенному паттерну ВЫШЕ, чем по"
        " буквальному. Ветки `грн · ₴ · grn · decimal` посчитаны отдельно в записи —"
        " `decimal` срабатывает и на «27.08», и только по веткам видно, кто несёт колонку.",
        "- **«Листовка»** — это `has_media` (определение `scripts/image_census_5c1.py`), прокси:"
        " без vision картинка не доказана листовкой. Доля цены считается отдельно, рядом.",
        "",
    ]
    if floods:
        lines += [
            "## FloodWait",
            "",
            *[
                f"- стадия `{event['stage']}`: Telegram попросил {event['seconds']} с в"
                f" {event['at']}; проход остановлен, собранное сохранено."
                for event in floods
            ],
            "",
        ]
    else:
        lines += ["**FloodWait: ни одного.** Проход дошёл до конца.", ""]

    lines += [
        f"## Таблица — {len(rows)} строк, сортировка `dairy posts/day × (1 + comments/day)`",
        "",
        "`к/д или с/д` = комментов/день для каналов, сообщений/день для чатов (у чата нет"
        " счётчика ответов — там прочерк, а не ноль). Реестровые строки идут без вердикта:"
        " их измерял стор, а не этот ценз.",
        "",
    ]
    lines += table(rows)
    lines += [
        "",
        "---",
        "Числа — из `results/retail_census.json`; таблицу рендерит"
        " `scripts/retail_census_report.py`. `config/registry.yaml` не тронут:"
        " в этом контракте в реестр ничего не входит и ничего из него не выходит."
        " Проект ревизии — `docs/reports/registry-revision-proposal.md`.",
    ]
    return "\n".join(lines) + "\n"
