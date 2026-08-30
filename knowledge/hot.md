<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-08-30 08:19:23 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
80e32b9 docs(report): harness-v2.1 -- the deny refusal isolated to the glob, one hyphen apart
a7fe8bb docs(report): harness-v2.1 final -- the verifier read twice, and the deviations join the ledger
25b9931 fix(harness-v2.1): five prompts back out of the archive, and hot.md stops claiming a fix that did not happen
a607909 docs(report): harness-v2.1 -- every guard seen refusing and accepting, 12.6K -> 9.3K boot tax
abe56bb chore(harness-v2.1): 28 spent contracts move to docs/archive/prompts/, 87 stay and say why
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `harness-guard-v2-behaviour-not-spelling.md` — The PreToolUse guard judges behaviour, not spelling
- `lora-c-the-line-trains-at-90-seconds-a-step.md` — The line trains at 89.961 s/step — and the gate that would have hidden it

## 📅 Recent daily logs

- `2026-08-30.md`
- `2026-08-27.md`
- `2026-08-26.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->
# Hot Cache — curated

**Last update:** 2026-08-30 (r2 исполнен) — этап 1 = `docs/SPEC-v2-promo-pulse.md`. Карта и деньги —
`docs/STATUS.md`; цикл фазы — `docs/PROCESS.md` v2.1: `/plan-phase` → «go» → `/report`. Блок
курируется руками, **≤40 строк**: у археологии есть дом — отчёты, ADR, логи дня.

## 🔥 What's Hot
**✅ `retail-census-r2` ИСПОЛНЕН, ждёт приёмки ($0).** `docs/reports/retail-census-r2.md` · запись
`results/retail_chains.json` · таблица 36 строк `results/retail_chains_table.md` · категория B
(47 чатов, НЕ переизмерялись) `results/poltava_chats_b.md`. Отклонения **Dv880–Dv888**. Ответ: канал
у **13 из 36**, комменты открыты у **7**; молочка + открытые комменты + живой трафик — **только
Varus** `@VARUS_channel` (16.643 ком./день, цена .246, молочка .194). **Шесть сетей вешают БОТА и
никакого канала** (АТБ, Novus, Auchan, Велмарт, Рукавичка, Копійка).

**⚠️ ОДНОГО ИНСТРУМЕНТА НЕ ХВАТИЛО, И ЭТО ИЗМЕРЕНО:** curl нашёл **1 из 6** хэндлов, уже известных
r1. Отсюда три инструмента и колонка `method` — `curl` · `curl+bundle` (футер клиентского рендера
лежит в его же JS: так нашёлся `@foraINFO`) · `browser` (мимо Cloudflare 403). «Страницу не
прочитали» ≠ «ссылки нет». Урок → [[a_new_instrument_needs_the_old_ones_answers]].

## ⏭️ Next
1. **Приёмка r2 тимлидом** — и выбор оператором сетей под C2 из таблицы.
2. **C2 `positions-scale` (≤$1)** · **`phase7-a1` ($0)** · **`money-anchors` ($0)**.

## 🚧 Blockers
**⛔ 2 строки не прочитаны вообще:** `zakaz.ua` (Cloudflare 403 + домен не разрешён Chrome) и
`thrash.ua` (JS-оболочка, бандл пуст). Это НЕ «канала нет». Разрешение домена — ручной шаг оператора.

**⛔ БЮДЖЕТ ШАГА 2 ВЫБРАН: 40/40** запросов MTProto (клиент обёрнут, счёт настоящий). Кандидат стоит
**4–9**, не один: resolve + GetFullChannel + ДВА GetHistory (Dv881). Новый резолв — уже за контрактом.

**⛔ `MEMORY.md` УПЁРСЯ В ОБА ПОТОЛКА ЗАГРУЗЧИКА** (первые 200 строк → отрез по 25 000 UTF-16
units): 208 строк, доезжает **186**. Новый указатель вставлен В ГОЛОВУ Feedback, иначе не грузился
бы. Рычаг — убрать строки, **решение оператора**; мерить `context-census.py::loaded_memory`.

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт
обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list` показывает только running, смотри `pod list -a`.
