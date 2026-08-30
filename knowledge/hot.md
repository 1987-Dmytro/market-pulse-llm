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

**Last update:** 2026-08-30 (r2+r3+пробы) — этап 1 = `docs/SPEC-v2-promo-pulse.md`; карта `docs/STATUS.md`;
цикл `docs/PROCESS.md` v2.1. Блок курируется руками, **≤40 строк**: археология — в отчётах и логах.

## 🔥 What's Hot
**✅ `retail-census` r2+r3+пробы ИСПОЛНЕНЫ, ждут приёмки ($0).** `docs/reports/retail-census-r2.md`
перестроен по двум блокам оператора; **Dv880–Dv901**. Артефакты: `results/working_set.md` ·
`retail_chains_table.md` · `promo_comment_yield.json` · `poltava_brand_probe.json`.

**⚠️ БЛОК 1 — «КОММЕНТЫ» = ТОЛЬКО ПОД ЦЕНОВЫМ ПРОМО** (рулинг 30.08). По сырому стору: **16 324
коммента · 4 718 под ценой в 678 тредах · 71% — шум**; живут в `msuaaaa` (3 407) и `@VARUS_channel`
(1 210). **Varus — единственная СЕТЬ с молочкой под живыми комментами.** `@ATB_FANatik` — 0.25/день,
сноска. Свой канал АТБ (41 858) КОРПОРАТИВНЫЙ: промо 0.000.

**⛔ БЛОК 2 — ПРЕМИСА НЕ ПОДТВЕРДИЛАСЬ, ПРОВЕРЕНО ТРИЖДЫ.** 4 507 сообщений из 4 самых живых чатов —
**НОЛЬ реальных упоминаний брендов**, все 4 срабатывания ложные («третій **президент** України»,
трижды «**Ферма** клубники» из вакансий, Dv898). 61 чат = **≈78 молочных сообщений/мес** на область,
и это КАТЕГОРИЯ. По 16 324 комментам watchlist 228, из них **198 `varus-pl` в своём же канале**,
**Гармонія 0** (Dv899). **Жанр запроса определяет популяцию (Dv900):** `CHAT_TERMS` — только
барахолки; свип по 24 центрам дал «типове» 0 везде и один городской `@svitlo5s` (1 865) с
**0.107 комм./день и молочкой 0.000**; Чутове 0 и здесь. **Геопоиск мёртв (Dv901):**
`contacts.getLocated` — 0 чатов по двум крупнейшим городам, и он ищет только ГЕОЧАТЫ.

## ⏭️ Next
1. **РУЛИНГ ТИМЛИДА:** покупать ли оставшийся **81** полтавский кандидат при выходе 78 категорийных
   сообщений/мес и нуле брендовых. Не проверено: говорят ли о молочке БЕЗ имени бренда (это ловит
   лексикон, watchlist — нет). 2. **C2 `positions-scale`** — цены в листовках, работа vision 5c2.

## 🚧 Blockers
**⛔ БЮДЖЕТЫ РАЗДЕЛЬНЫ.** Контрактные ≤40 шага 2 ВЫБРАНЫ, `would_exceed` отказывает. r3 41/80,
проба брендов 52/60, свип жанра 48/60. Новая цель = новая строка (Dv894).

**⛔ ЦЕНЗ НЕ READ-ONLY НА ОДНУ СТРОКУ.** Вступили в канал Маркетопта (42 378, `joins_5c1.jsonl`,
обратимо `--leave`): `media_share` 1.000, ноль `грн` — **цены в листовках**, vision 5c2 (Dv897).

**⛔ ЧАТ МОЖЕТ МОЛЧАТЬ:** Диканька и Козельщина открыты, НОЛЬ сообщений за 28 дней. **`MEMORY.md`**: 208 строк, доезжает 186.

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт
обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list` показывает только running, смотри `pod list -a`.
