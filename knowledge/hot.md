<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-03 15:35:29 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
e8f56e3 knowledge(decision): §8's PAUSE branch is unsatisfiable as worded, and the fix is four words
aa5a3a1 docs(stop): no $0 route to (e) either — local_llm runs on the RENTED card, checked
6427fbf docs(stop): option (1) is written — plan §9 rev 9, $0, awaiting one read
d33c5a3 plan(rev 9): S9's paid instrument, PROPOSED for review — not implemented, no pod
cbd0522 docs(stop): (e) is UNREACHABLE at $0, shown by the grader's own refusal
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `the-pause-branch-is-unsatisfiable-as-worded.md` — §8's PAUSE branch is unsatisfiable as worded — the evaluator agrees and still returns «not met»
- `the-schedule-reports-it-does-not-gate-the-tick.md` — `data/schedule.json` reports whether a tick is due; it does not refuse one — because a gate there would make the idempotence check untestable

## 📅 Recent daily logs

- `2026-09-03.md`
- `2026-09-02.md`
- `2026-09-01.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->
# Hot Cache — curated
**Last update:** 2026-09-03 (сессия 7, S9 ПОСТРОЕН и ОЦЕНЁН, под НЕ создавался). Этап 1 `SPEC-v2-promo-pulse.md`, карта `STATUS.md`, цикл `PROCESS.md` v2.1. Руками, ≤40 строк.

## 🔥 What's Hot
**⏸️ `promo-pulse-1` — СЕДЬМАЯ ПАУЗА, на границе денег.** $0-половина S9 ГОТОВА и доказана; под не
создавался, `pod list -a` и `serverless list` — `[]`. **Рунг 0 ПРОХОДИТ: дорогой угол $1.3193 из
$2.5000** (`results/prereg_promo_dev_loop.json`; дешёвый 0.2766, средний 0.3340). Цена в единице
ПОДА: секунды существования × $/ч, а не serverless-ставка чужого транспорта.

**Транспорт = ПОД, факт а не выбор:** `local_llm.batch` рендерит из ЗАПИНЕННОГО `prompts.py` →
serverless не обслужит этот промт, не сдвинув его. Сложено в план §9a. **Что построено ($0):** `--register` (кап из строки гарда `REMAINING $3.4591` − $0.30 холдаута;
$0.74/ч из `runpodctl gpu list`, EU-RO-1, RTX 4090, stock Medium, ДОРОЖАЙШЕЕ из двух облаков;
оверхед 279 с из брата, который РАСЧИТАЛСЯ — `pass2_signals_r2_run.json :: pods[0]` 2 061 с на 75
тредов; гейты транспорта из замороженного v5b, 180 с dead-man ВЫВЕДЕН из двух его полей) ·
`--pack` (**56** юнитов: 40 тредов + 16 постов ноги B, смок первым — `@msuaaaa:6523`,
`@VARUS_channel:9006`, `@VARUS_channel:6009`) · `--open`/`--close-segment` (рунг 1 на ответе
create, «никогда два пода» ДО создания, счёт сегмента по ЕГО цене) · `promo_dev_pod_runner.py`
(меняет ОДНУ функцию `reader_v5_pod_runner` — рендер — и диспатчит по задаче ЮНИТА, обе ноги на
одном буте, GO между ними) · `scripts/runbook_promo_dev_1.md` — сессия пода целиком.

**🎯 Сухой контакт окупился.** Преамбула пода прогнана НА МАКЕ без GPU по настоящему паку и ОТКАЗАЛА
на `@ekomarket_shop:1457`: пак пинил sha ПЭЙЛОАДА, под передеривает ОТРЕНДЕРЕННЫЙ запрос. На живом
поде это выброшенный бут. Исправлено, стало тестом.

## ⏭️ Next / 🚧 Blockers
START RITUAL → рулинг: (1) следующая сессия гоняет ранбук как написан, или (2) что-то в $0-половине
двигать. **Одно нужно словом оператора ДО create: `--image-name` — ни одна запись репо его не
несёт.** Деньги: `CYCLE 3 SPENT $3.5409 of $7.00 · REMAINING $3.4591`; кап dev-петли полные $2.50,
пол $2.00 чист, холдаут $0.30 не тронут; шаг `promo-dev-loop` ещё без якоря (пишется первым `--note`).
**⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ** (`:366/:171/:153`). **⛔ `1925810730` и инвайт-хэш неадресуемы.**
**⚠️ Платный ран — отцеплённым (`setsid`), Dv904.** **⚠️ Фикстура, пишущая в стор, ДОЛЖНА патчить
ВСЕ derived-корни.** **⚠️ `volume_calc_5c1.py` НЕ ЗАПУСКАТЬ просто так.**

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list` показывает только running, смотри `pod list -a`.
