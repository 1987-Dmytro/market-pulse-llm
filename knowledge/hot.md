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

**Last update:** 2026-08-30 (r2 + r3) — этап 1 = `docs/SPEC-v2-promo-pulse.md`; карта `docs/STATUS.md`;
цикл `docs/PROCESS.md` v2.1. Блок курируется руками, **≤40 строк**: археология — в отчётах и логах.

## 🔥 What's Hot
**✅ `retail-census-r2` + r3 ИСПОЛНЕНЫ, ждут приёмки ($0).** `docs/reports/retail-census-r2.md` ·
рабочий набор `results/working_set.md` (A1 цены · A2 комменты · **A3 промо, которое сайты не
линкуют** · B райцентры) · `results/retail_chains.json` · `results/retail_chains_table.md`.
Отклонения **Dv880–Dv894**. Канал у **17 из 36**, комменты открыты у **7**; молочка + комменты +
покупатель — **только Varus**. Райцентров **21 из 24**, чатов **61** (планка языка снята).

**⚠️ ДВА ИНСТРУМЕНТА ДОПОЛНЯЮТ, А НЕ ЗАМЕНЯЮТ (Dv892).** Сайт отвечает «ЧЕЙ канал», поиск по имени —
«ЧТО существует»: `@blyzenkoua` — собственный канал Близенько, сайт его не линкует; промо АТБ с
комментами — в неофициальных каналах скидок. Объединение — A3. **АТБ:** `@atb_market_official`
(41 858) через сайт → Instagram → Telegram, но КОРПОРАТИВНЫЙ (цена 0.000, комменты закрыты).
**Маркетопт** `+Ejz6ubzm21IyMTQy` — 42 378, приватный инвайт: сбор только через вступление.
**Личность — по бесплатному `t.me/s/`:** так пойман `@ON_LINE_MO` — «служебна група», не промо (Dv893).

## ⏭️ Next
1. **Приёмка** + выбор сетей под C2 из `results/working_set.md`; **81** полтавский кандидат ещё не
   проверен — траншами. 2. **C2 `positions-scale` (≤$1)** · **`phase7-a1`** · **`money-anchors`**.

## 🚧 Blockers
**⛔ ДВА БЮДЖЕТА, НЕ ОДИН.** Контрактные ≤40 шага 2 ВЫБРАНЫ, `would_exceed` отказывает — не
поднимать. r3 по отдельной авторизации: **41 из 80**, зазор 3.05 с. Новый проход — новая (Dv894).

**⛔ ЧАТ МОЖЕТ СУЩЕСТВОВАТЬ И МОЛЧАТЬ.** Диканька и Козельщина: резолвятся, ОТКРЫТЫ, НОЛЬ сообщений
за 28 дней. Не «не нашли» и не «не измерили» — деньгами не лечится.

**⛔ `MEMORY.md` УПЁРСЯ В ОБА ПОТОЛКА** (200 строк → 25 000 UTF-16 units): 208 на диске, доезжает
**186**. Рычаг — убрать строки, **решение оператора**; мерить `context-census.py::loaded_memory`.

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт
обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list` показывает только running, смотри `pod list -a`.
