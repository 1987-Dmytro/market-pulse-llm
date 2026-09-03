<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-03 14:23:23 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
978b884 knowledge(log): session 5 closes at the fifth STOP
1b99409 knowledge(hot): curated block back to its budget
a5326ed knowledge(hot): the grader is proven at $0, and 4 268 passed at 6b6fe44
dfeaa6d docs(stop,report): 4 268 passed at 6b6fe44, and the grader is proven against the shipped gold
6b6fe44 tests(k8): the grader is proven against the SHIPPED gold, four directions, at $0
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `the-schedule-reports-it-does-not-gate-the-tick.md` — `data/schedule.json` reports whether a tick is due; it does not refuse one — because a gate there would make the idempotence check untestable
- `the-goal-loop-never-engaged.md` — The `/goal` loop never engaged — §8's resume protocol rests on an unverified mechanism

## 📅 Recent daily logs

- `2026-09-03.md`
- `2026-09-02.md`
- `2026-09-01.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->
# Hot Cache — curated
**Last update:** 2026-09-03 (сессия 6, ОБЕ ВИЛКИ ЗАКРЫТЫ). Этап 1 `SPEC-v2-promo-pulse.md`, карта `STATUS.md`, цикл `PROCESS.md` v2.1. Руками, ≤40 строк; археология — в логах дня.

## 🔥 What's Hot
**⏸️ `promo-pulse-1` — ШЕСТАЯ ПАУЗА. НЕ ПРО ДЕНЬГИ: платной ноги S9 ПРОСТО НЕТ.** У
`promo_dev_pass.py` только `--render` и `--dry-run` — ни `--smoke`, ни `--register`, ни `--run`;
проверено по всему репо (`promo_prompts` не импортирует ни один скрипт, поднимающий под). Рулинг
03.09 (b) санкционирует ЗАПУСК, плана на СБОРКУ нет → `docs/plans/promo-pulse-1.STOP.md`.

**✅ Вилка 1 — раскол стора.** Точка раздела найдена САМОЙ печатью (префиксный sha256 = дайджест):
**38/38**, 23 целых · 15 префиксов · 35 файлов целиком. `data/derived/` = w1, заморожен;
**`data/derived_w2/` = живой** (3008/1093/15/385). Экспорт w1: **55 листьев → 5**, ноль под
`provenance.evidence`, 4 474 листа данных идентичны; пятый пин `build_aggregates.py` ЗАЯВЛЕН как
`MOVED_BY_THE_SECOND_WINDOW` @ `58ff037`. 19 редов зелёные, ни один assert не тронут.

**✅ Вилка 2 + кодбук + K6.** `carrier` в ключе: 7 row_id под обоими носителями, 6 сообщений, ровно
**1** тройка обеими ногами (`@forainfo:6056`), в w1 — 0 → дедуп трендов по (window, channel, msg_id,
SKU), приоритет `leaflet_page`. `codebook_version()` = **`a694d005972d3a66…`**; эталон через четыре
хука: **140 about · 84 signal · 0 отказов**. K6 ПО СТРАНИЦАМ: **46**, `positions_50_predicted.jsonl`
= **205** строк обеих ног (`781b02b4…`), `image` у 45 из 46. **Дро НЕ сдвинулось:**
`rows_sha256_as_drawn` **`fe3f5841175a3953…`** — эталон-50 должен против НЕГО, а `61b4fda7…` был sha
ФАЙЛА и сдвинулся от добавленного поля.

## ⏭️ Next / 🚧 Blockers
START RITUAL → рулинг по трём вопросам: (1) сборка платной ноги S9, (2) линия расхода шага —
**$2.9867** (осадка гарда) или $3.1909 (дельта рулинга), (3) эталон positions-50. Шаг ЗАКРЫТ:
`PROMO-PULSE-1 $2.9867 of $3.95` · `CYCLE 3 $3.5117 of $7.00` · `REMAINING $3.4883`; dev-петля
держит полные $2.50 (пол $2.00 чист). **⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ** (`:366/:171/:153`).
**⛔ `1925810730` и инвайт-хэш неадресуемы.** **⚠️ Фоновые задачи харнеса убивают друг друга** —
платный ран отцеплённым (`os.setsid()`), Dv904. **⚠️ Фикстура, пишущая в стор, ДОЛЖНА патчить ВСЕ
derived-корни** (`stage()` дописала 13 строк в живой корень). **⚠️ `volume_calc_5c1.py` НЕ ЗАПУСКАТЬ
просто так** — перезаписывает `generated_at`, из которого берётся граница обхода, и роняет свой тест.

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list` показывает только running, смотри `pod list -a`.
