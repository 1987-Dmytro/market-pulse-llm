<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-02 15:21:08 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
b61f6b8 docs(stop): the (10)(a) gate refused the whole step at a 13.466 s page warm-up — the ruling's table and three questions, cap unchanged
8b7b965 s4(run 1): the (10)(a) gate REFUSED — projected $12.5928 against $3.95 at a 13.466 s page warm-up; no gold call, $0.0579 billed
fba2d79 money(step): promo-pulse-1 anchored at $14.19, cap $3.95 (ruling 02.09 (b))
f17d966 s4: ruling 02.09 (b) applied — step cap $3.95, the text leg is stage 0, re-registered (rung 0 FITS at the dear corner)
76df8ec docs(status,reviews): ruling 02.09 (b) — S4's step cap is $3.95, the whole step, text leg first
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
**Last update:** 2026-09-02 15:40 (session 3). Этап 1 `SPEC-v2-promo-pulse.md`, карта `STATUS.md`, цикл
`PROCESS.md` v2.1. Руками, ≤40 строк; археология — в логах дня.

## 🔥 What's Hot
**⏸️ `promo-pulse-1` — ТРЕТЬЯ ПАУЗА 02.09: ГЕЙТ (10)(a) ОТКАЗАЛ ВЕСЬ ШАГ.** Рулинг (b) применён (`f17d966`: кэп
$3.95, текст-нога = stage 0, rung 0 FITS, dear $3.6059); шаг заякорен гардом ($14.19, `fba2d79`); эндпоинт
`1w2cn98hcikl7b` отслужил пин; прогрев: **страница 13.466 с** (`atb_market_official_4571.jpg`), текст 0.794 с →
проекция **$12.5928 против $3.95** (+218.8 %), `refuse: true`, ни одного gold-вызова. Куплено **$0.0579** (бут
149 с + два прогрева; `results/run_promo_c2.json :: runs[0]`). Снесено, доказано листингом. STOP с таблицей и
тремя вопросами (гейт по ногам? · какой маргинал страниц? · порядок при частичной покупке?) —
`docs/plans/promo-pulse-1.STOP.md`. Шаг-леджер `results/spend_promo_pulse_1.json` ОТКРЫТ: `--note`, без `--close`.

**Почему 13.5 с ≠ 3.4 с (файлы, не диагноз):** смок = ОДИН джоб на 30 стр. VARUS/atb_aktsiyi/msuaaaa (2.6–3.4 с/стр.);
5c2 на том же канале: прогрев 1.729 с, реализовано 10.408 с/строку (159 стр. ATB, 0.7 позиции/стр.). n = 1 × 3 008.
Комната после текста + резерва + рана: $3.514 → 851 стр. при 13.5 с · ≈1 160 при 10.4 · все 3 008 при 3.37.

**Проверки в транскрипте (s3):** (a)(b)(d)(f)(g)(h)(i) показаны; `make check-stamped` @ `b61f6b8` **4 279 · 2 skipped ·
HOLDS**. (10)(a)-отказ теперь пишет `outcome.unbought` (`8b7b965`). Дро-50 `a3f659f9a8d73f5e` (ДО-C2), экран `28fffc93c723ab8d`.

**НЕ выводить заново.** Маргинал смока **2.623…3.369 с/стр.**, текст 0.947 / 2.8132 с, буты 157.449 / 212.041 с,
$0.00030669/с. Гард 15:00: `CYCLE 3 SPENT $0.2917 of $7.00`, `REMAINING $6.7083`. Эндпоинта нет, `mp-srv2` жив.

## ⏭️ Next
START RITUAL → рулинг по трём вопросам STOP → правка гейта/константы + тест → `--register` → ранбук §2–§5 (один бут
в кэпе) → `make tick` → **дро-50 переснять** → `make promo-screen` → отчёт. Разметки тимлида (dev-40, positions-50) — по 10.

## 🚧 Blockers
**⛔ ГЕЙТ (10)(a): $12.59 > $3.95 при 13.466 с/стр.** — единственный блокер платной ноги; кэп не двигать (рулинг (b) п. 3).
**⏳ Комната — часы:** $0.2333/день. **⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ** (`:366/:171/:153`). **⛔ `1925810730` и инвайт-хэш
неадресуемы.** `/goal` дважды оценил паузу верно (02.09) → [[the-goal-loop-never-engaged]] закрыт для протокола запуска.

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт
обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list` показывает только running, смотри `pod list -a`.
