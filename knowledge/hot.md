<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-02 10:32:46 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
11bdbf6 docs(report): the anchor paragraph follows the STOP — one question, not a contradiction
6209166 docs(stop): the anchor is one question, not a fork
4137c63 docs(report,stop): the instrument is finished and the money line refuses
97e84e6 fix(guard,tripwire): the two BLOCKING findings of the pre-paid-leg /code-review
4950856 feat(draw): S1's 50 positions — seed 42, stratified by chain, two runs one sha
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `the-schedule-reports-it-does-not-gate-the-tick.md` — `data/schedule.json` reports whether a tick is due; it does not refuse one — because a gate there would make the idempotence check untestable
- `the-goal-loop-never-engaged.md` — The `/goal` loop never engaged — §8's resume protocol rests on an unverified mechanism

## 📅 Recent daily logs

- `2026-09-02.md`
- `2026-09-01.md`
- `2026-08-30.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->
# Hot Cache — curated
**Last update:** 2026-09-02 (session 2). Этап 1 `SPEC-v2-promo-pulse.md`, карта `STATUS.md`, цикл
`PROCESS.md` v2.1. Руками, ≤40 строк; археология — в логах дня.

## 🔥 What's Hot
**⏸️ `promo-pulse-1` ЖДЁТ ОДНОГО «ДА/НЕТ» ПО КЭПУ ШАГА.** Якорь сдвинут как велено (`bf1665d`): гард
**exit 0**, anchor $14.48, `CYCLE 3 SPENT $0.2528 of $7.00`, `REMAINING $6.7472`. Но рунг 0 на ВЕСЬ шаг
S4 (3 008 стр. + 405 текст-постов + буты + хвост), `results/prereg_promo_c2.json :: rung_0`: cheap $2.6041
(влезает), priced $3.5241, **dear $3.6059 против кэпа 3.20 (+12.7 %)** — кэп выведен из `c2_priced_usd`
$3.1563, цены ОДНОЙ (vision) ноги. `docs/plans/promo-pulse-1.STOP.md` — один вопрос: `--step-cap 3.95`
(комната цикла после кэпов C3; dear + резерв cap-gate $0.2843 = $3.8902)?

**S4 ГОТОВ на $0:** 3 008 страниц на диске + `results/post_media_promo_c2.json` (`fetch_promo_media_c2.py`,
сверка с pagecount по каналам); драйвер `scripts/run_promo_c2.py` (транспорт/гейты/ноги — импорт из
`run_5c2`; текст-нога по id; порядок — список §3 спеки; репроекция после каждого канала; `--run` отказывает
при `rung_0.fits: false`); 12 тестов на стабе; ранбук `knowledge/runbooks/promo_c2_paid_leg.md`.

**НЕ выводить заново.** Vision маргинал **2.623…3.369 с/стр.**, текст 0.947 / 2.8132 с, буты 157.449 /
212.041 с, $0.00030669/с. Дро позиций `a3f659f9a8d73f5e` (ДО-C2 — переснять после S4), дро-20
`3d80c81a9c353130`, экран `28fffc93c723ab8d`. Куплено НИЧЕГО; эндпоинта нет, том `mp-srv2` жив.

## ⏭️ Next
START RITUAL → рулинг по кэпу → `STEP_CAP_USD` + `--register` → ранбук §1–§5 (гард `--step`, create,
`--run`, teardown листингом, `--close` после оседания биллинга) → `make tick` → **дро-50 переснять** →
`make promo-screen` → отчёт. Разметки тимлида (dev-40, positions-50) — батчами по 10.

## 🚧 Blockers
**⛔ РУНГ 0 НА S4: dear $3.61 > кэп $3.20** — единственный блокер платной ноги. **⏳ Комната цикла — часы:**
$0.2333/день; «да» завтра оставит C3 без ≈$0.23. **⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ** (`:366/:171/:153`).
**⛔ `1925810730` и инвайт-хэш неадресуемы.** **⚠️ `/goal` НЕ ПРОВЕРЕН** → [[the-goal-loop-never-engaged]].
MEMORY.md сжат до 81 строки (02.09), ничего не выкинуто.

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт
обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list` показывает только running, смотри `pod list -a`.
