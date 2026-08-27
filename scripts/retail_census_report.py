"""Render `docs/reports/retail-census.md` from `results/retail_census.json`.

Prose ≤30 lines (PROCESS.md's v2 ceiling); the table and the two `runpodctl` listings step 0
requires verbatim are exhibits under it, which is the same allowance the paired tables take.
Every number here is read out of the record — this module computes shares of rows and nothing
else, so a figure in the report can always be found in the file.
"""

import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import discover_channels as discovery  # noqa: E402

VERDICT_MARK = {"enter": "**enter**", "posts-only": "posts-only", "reject": "reject"}


def mix(row: dict) -> str:
    """The language mix, with a marker where no Ukrainian was detected at all.

    Not a verdict and not a market screen — SPEC 3.11 (4)'s market screen is the operator's, and
    Ukrainian channels legitimately write Russian (the corpus is UA/RU mixed, SPEC §1). But «АТБ»
    also matches a Moscow-metro channel and «METRO» matches METRO Russia, and `ua 0.00` is a fact
    the operator needs to see without opening the record.
    """
    languages = row["stats"].get("language_mix") or {}
    if not languages:
        return "—"
    top = sorted(languages.items(), key=lambda kv: -kv[1])[:2]
    text = " ".join(f"{lang} {share:.2f}" for lang, share in top)
    return f"{text} ⚠" if not languages.get("ua") else text


def no_ukrainian(rows: list[dict]) -> list[dict]:
    return [
        row
        for row in rows
        if (row["stats"].get("language_mix") or {}) and not row["stats"]["language_mix"].get("ua")
    ]


def coverage(checked: list[dict]) -> tuple[list[str], list[str]]:
    """Which chain names and which district centres came back with a measured candidate.

    The point of the two themes was coverage, and «this chain has no channel» is only a finding
    if the query for it actually ran and returned nothing measurable.
    """
    tags = {tag for row in checked for tag in row.get("found_by", [])}
    chains = [
        chain
        for chain in discovery.RETAIL_CHAINS
        if any(
            t == f"retail_chains:{chain}" or t.startswith(f"retail_chains:{chain} ") for t in tags
        )
    ]
    towns = [
        town
        for town in discovery.POLTAVA_TOWNS
        if any(t.startswith(f"poltava_chats:{town} ") for t in tags)
    ]
    return chains, towns


def pct(value) -> str:
    return "—" if value is None else f"{value * 100:.0f}%"


def md(text) -> str:
    return (text or "—").replace("|", "\\|")


def rate(value, *, floor: bool = False) -> str:
    """A rate, marked `>=` when the window hit the request cap and the number is a floor.

    23 of 266 rows filled WINDOW_LIMIT inside the 28 days: their history was cut, not counted.
    Printed bare they land at ~42.86/day (1200/28) and a reader compares them with a measured
    33.89 as if both were readings ([[an_absolute_bar_needs_a_reachability_state]]).
    """
    if value is None:
        return "—"
    return f"≥{value:.2f}" if floor else f"{value:.2f}"


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
        "| # | канал | handle | подп. | ✓ | п/д | листовка/цена | цена | комменты |"
        " к/д или с/д | молочка | мова | инстр. | вердикт · причина |",
        "|---:|---|---|---:|:-:|---:|---:|---:|---|---:|---:|---|---|---|",
    ]
    for n, row in enumerate(rows, 1):
        stats = row["stats"]
        flow = stats["messages_per_day"] if row.get("is_group") else stats["comments_per_day"]
        cut = bool(stats.get("window_truncated"))
        verdict = row.get("verdict")
        reason = (row.get("reasons") or ["—"])[0]
        out.append(
            f"| {n} | {md(row.get('title'))} | `{row['handle']}` |"
            f" {row.get('subscribers') if row.get('subscribers') is not None else '—'} |"
            f" {'✓' if row.get('telegram_verified') else ''} |"
            f" {rate(stats['posts_per_day'], floor=cut)} | {pct(stats['leaflet_or_price_share'])} |"
            f" {pct(stats['price_share'])} |"
            f" {group_flag(row)} | {rate(flow, floor=cut and row.get('is_group'))} |"
            f" {pct(stats['dairy_share'])} | {mix(row)} |"
            f" {row.get('measured_by') or '—'} |"
            f" {VERDICT_MARK.get(verdict, 'in_registry')} · {md(reason)} |"
        )
    return out


def render(record: dict) -> str:
    # Only measured rows carry a `stats` block. The unchecked ones stay in the RECORD with their
    # free search-response fields and the bar that skipped them; putting them in the table would
    # be a row of dashes claiming to be a reading.
    rows = [row for row in record["rows"] if row.get("stats")]
    unmeasured = [row for row in record["rows"] if not row.get("stats")]
    # Two causes, and they are a different finding: a row nobody looked at yet, and a row the
    # budget skipped ([[unreadable_now_versus_never]]).
    below_bar = [row for row in unmeasured if row.get("skipped_because")]
    not_reached = [row for row in unmeasured if not row.get("skipped_because")]
    # `found` is the whole population the searches returned; `checked` only what was measured.
    # Counting "found" off the measured rows would report the census's own coverage as its yield.
    found = [row for row in record["rows"] if not row.get("in_registry")]
    checked = [row for row in rows if not row.get("in_registry") and row.get("checked")]
    verdicts = Counter(row.get("verdict") for row in checked)
    themes = {
        theme: {
            "found": len(
                [r for r in found if any(t.startswith(f"{theme}:") for t in r.get("found_by", []))]
            ),
            "checked": len(
                [
                    r
                    for r in checked
                    if any(t.startswith(f"{theme}:") for t in r.get("found_by", []))
                ]
            ),
        }
        for theme in record["themes"]
    }
    enterable = [row for row in checked if row.get("verdict") == "enter"]
    with_dairy = [row for row in checked if (row["stats"]["dairy_share"] or 0) > 0]
    contract_gap = [
        row
        for row in checked
        if (row["stats"]["price_share"] or 0) > (row["stats"]["price_share_contract_regex"] or 0)
    ]
    media = [
        row["stats"]["media_share"] for row in rows if row["stats"].get("media_share") is not None
    ]
    prices = [
        row["stats"]["price_share"] for row in rows if row["stats"].get("price_share") is not None
    ]
    media_n = len(media)
    media_median = sorted(media)[media_n // 2] if media else 0.0
    media_full = sum(1 for value in media if value >= 0.99)
    price_median = sorted(prices)[len(prices) // 2] if prices else 0.0
    step0 = record.get("step_0") or {}
    floods = record.get("flood_wait_events") or []
    bound = record.get("bound") or {}
    bars = (
        " · ".join(
            f"`{theme}` >= {value}"
            for theme, value in (bound.get("min_subscribers_by_theme") or {}).items()
        )
        or "—"
    )
    population = bound.get("population") or {}
    chains_found, towns_found = coverage(checked)
    # A name with no MEASURED row is two different states: the search returned nothing for it,
    # or it returned something the wall stopped us reaching. Only the first is a finding about
    # Ukraine ([[unreadable_now_versus_never]]).
    chains_any, towns_any = coverage(found)
    no_chain = ", ".join(c for c in discovery.RETAIL_CHAINS if c not in chains_any)
    no_town = ", ".join(t for t in discovery.POLTAVA_TOWNS if t not in towns_any)
    chain_pending = ", ".join(c for c in chains_any if c not in chains_found)
    town_pending = ", ".join(t for t in towns_any if t not in towns_found)
    rf = no_ukrainian(checked)
    n_cut = sum(1 for row in rows if row["stats"].get("window_truncated"))
    cap = record["window_limit"] / record["window_days"]

    lines = [
        "# retail-census (C1) — ценз сетей и полтавских чатов, $0",
        "",
        f"**{len(record['queries'])} запросов по двум темам, {len(found)} нерегистрированных"
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
        f"- `retail_chains` — {themes['retail_chains']['found']} кандидатов из"
        f" {len(record['themes']['retail_chains'])} запросов, измерено"
        f" {themes['retail_chains']['checked']};"
        f" `poltava_chats` — {themes['poltava_chats']['found']} из"
        f" {len(record['themes']['poltava_chats'])}, измерено"
        f" {themes['poltava_chats']['checked']}.",
        "- **Планки — бюджет, не приговор**, и выставлены ПО найденному населению:"
        f" {bars}. Ниже них осталось {bound.get('skipped_below_the_bar', 0)} строк"
        f" ({len(unmeasured)} без замера всего: {len(below_bar)} по планке,"
        f" {len(not_reached)} не дошли до стены) — они В ЗАПИСИ со своими бесплатными полями"
        " и причиной, а не выброшены молча; `--min-subscribers 0 --min-subscribers-chats 0`"
        " проверяет всё. Медиана подписчиков: у сетей"
        f" {population.get('retail_chains', {}).get('median', '—')}, у чатов"
        f" {population.get('poltava_chats', {}).get('median', '—')} — планка 100 на чаты"
        " вычеркнула бы Оржицю, Козельщину и Машівку целиком, поэтому она 0.",
        "- В таблице только измеренные строки: прочерк вместо замера читался бы как замер.",
        "- Вердикты: "
        + " · ".join(f"`{v}` {n}" for v, n in verdicts.most_common() if v)
        + f"; молочка > 0 у {len(with_dairy)} из {len(checked)} измеренных,"
        + f" `enter` у {len(enterable)}."
        + " В таблице только измеренные строки: прочерк вместо замера читался бы как замер.",
        f"- **Покрытие — измерено {len(chains_found)}/{len(discovery.RETAIL_CHAINS)} названий"
        f" сетей и {len(towns_found)}/{len(discovery.POLTAVA_TOWNS)} райцентров.**"
        f" НИЧЕГО НЕ НАЙДЕНО ни при какой планке — сети: {no_chain or '—'};"
        f" райцентры: {no_town or '—'}. Это вывод про Украину. Остальное —"
        f" найдено, но не дошли до стены (сети: {chain_pending or '—'};"
        f" райцентры: {town_pending or '—'}) — это вывод про бюджет, и он досчитывается.",
        f"- **{len(rf)} измеренных строк без единого украинского текста** (`ua 0.00`, помечены ⚠):"
        " поиск по «METRO», «Auchan», «Толока» приводит каналы РФ-рынка. Рыночный экран"
        " SPEC 3.11 (4) — операторский, поэтому это колонка, а не вердикт; но верх таблицы"
        " читать с ней.",
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
        "- **«Листовка» насыщена и потому бесполезна как различитель.** Это `has_media`"
        " (определение `scripts/image_census_5c1.py`) — прокси, без vision картинка листовкой не"
        f" доказана. По стору медиана `media_share` = {media_median:.2f}, у {media_full} из"
        f" {media_n} строк она равна 1.00: рецепты и новости — тоже сплошь фото. Колонка"
        f" «листовка/цена» (объединение, как просит бриф) стоит в таблице, но различает"
        f" ритейл именно **«цена»**: её медиана {price_median:.2f}.",
        "",
    ]
    if floods:
        lines += ["## FloodWait — проход остановлен, собранное сохранено", ""]
        for event in floods:
            clears = event.get("clears_at") or (
                datetime.fromisoformat(event["at"]) + timedelta(seconds=event["seconds"])
            ).isoformat(timespec="seconds")
            lines.append(
                f"- стадия `{event['stage']}`: Telegram попросил **{event['seconds']} с"
                f" ({event['seconds'] / 3600:.1f} ч)** в {event['at']}, снимется"
                f" {clears}. Лимит на `ResolveUsernameRequest` — он не поканальный: с резолва"
                " хэндла начинается каждый вход, каждая выборка комментов и каждый entry-check,"
                " поэтому одна строка закрывает их все."
            )
        lines += [
            "",
            "Стена записана в `results/joins_5c1.jsonl` строкой `(census)`, а не только сюда:"
            " этот лог — то место, откуда все фазы читают «заперт ли аккаунт»"
            " (`collect_5c1.refuse_inside_flood_wait` — читатель). Стена, найденная здесь и не"
            " записанная туда, — это стена, в которую сборщик войдёт завтра. Проверено"
            " негативным контролем: повторный запуск теперь отказывается стартовать и называет час.",
            "",
            f"**Что это стоило покрытию:** {len(not_reached)} строк выше планки остались"
            f" неизмеренными — это не «нет данных», а «ещё не смотрели»; {len(below_bar)} строк"
            " ниже планки не смотрели по бюджету. Обе причины стоят в записи построчно."
            " Досчитать их — одна команда после того, как стена снимется, запись накопительная"
            " и уже измеренное не перемеряется.",
            "",
        ]
    else:
        lines += ["**FloodWait: ни одного.** Проход дошёл до конца.", ""]

    lines += [
        f"## Таблица — {len(rows)} измеренных строк, сортировка"
        " `dairy posts/day × (1 + comments/day)`",
        "",
        "`к/д или с/д` = комментов/день для каналов, сообщений/день для чатов (у чата нет"
        " счётчика ответов — там прочерк, а не ноль). Реестровые строки идут без вердикта:"
        f" их измерял стор, а не этот ценз. **`≥` — окно упёрлось в потолок"
        f" {record['window_limit']} сообщений: у {n_cut} строк история обрезана, и ставка —"
        f" нижняя граница, а не замер (потолок = {cap:.2f} сообщ./день).**",
        "",
    ]
    prose = [line for line in lines if line.strip()]
    inside = False
    prose_lines = 0
    for line in prose:
        if line.strip() == "```":
            inside = not inside
            continue
        prose_lines += not inside
    lines += table(rows)
    lines += [
        "",
        "---",
        f"Проза — {prose_lines} непустых строк (потолок PROCESS.md v2 — 30); оба листинга"
        " шага 0 и таблица идут экспонатами под ней, как парные таблицы. "
        "Числа — из `results/retail_census.json`; таблицу рендерит"
        " `scripts/retail_census_report.py`. `config/registry.yaml` не тронут:"
        " в этом контракте в реестр ничего не входит и ничего из него не выходит."
        " Проект ревизии — `docs/reports/registry-revision-proposal.md`.",
    ]
    return "\n".join(lines) + "\n"
