<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-03 21:27:47 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
6104455 knowledge(decision): the PAUSE branch is unreachable, not just unhonoured — the evaluator's own third block says so
d7e7810 docs(check): make check green at 49860d1 — 4 313 passed, 2 skipped, exit 0
49860d1 docs(stop,report): the pod was REACHED, and the unused recreate is refused on the record
9c5af91 knowledge: session 8 — the paid attempt, the dead-man that is set below its own span
e4340e1 s9(paid,stop): two pods bought and killed by my own ssh dead-man — 180 s from a PROBE where the settled sibling registers 500 s
```

## 📋 Recent decisions

- `the-pause-branch-is-unsatisfiable-as-worded.md` — §8's PAUSE branch is unsatisfiable as worded — the evaluator agrees and still returns «not met»
- `INDEX.md` — Decision records
- `the-schedule-reports-it-does-not-gate-the-tick.md` — `data/schedule.json` reports whether a tick is due; it does not refuse one — because a gate there would make the idempotence check untestable

## 📅 Recent daily logs

- `2026-09-03.md`
- `2026-09-02.md`
- `2026-09-01.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->
# Hot Cache — curated
**Last update:** 2026-09-03 (сессия 8, ПЕРВЫЙ ПЛАТНЫЙ заход S9 — два пода куплены и убиты моим же
dead-man). Этап 1 `SPEC-v2-promo-pulse.md`, карта `STATUS.md`, цикл `PROCESS.md` v2.1. Руками, ≤40 строк.

## 🔥 What's Hot
**⏸️ `promo-pulse-1` — ВОСЬМАЯ ПАУЗА, сработал РУНГ.** Рулинг (d) исполнен §0→§2: листинги `[]`,
гард, цена ($0.74 secure / $0.34 community — как в регистрации), **create ДВАЖДЫ**, рунг 1 GO оба
раза. Оба пода `RUNNING`, а `runpodctl ssh info` — `{"error": "pod not ready"}`; ssh dead-man убил
обоих. `ocnsveqetsve8w` 215 с $0.044194 · `gxuil044h61fkx` 221 с $0.045428 →
`results/promo_dev_loop_run.json` **$0.089622 из $2.50, осталось $2.410378**. Ничего не
сгенерировано, ни одного токена, ни одна нога не стейджилась. Листинги `[]` после каждого delete.

**🎯 ДЕФЕКТ — сам гейт.** `prereg_promo_dev_loop.json :: gates.ssh_deadman_seconds` = **180 с**, взяты
из ЗОНДА `prereg_reader_probe_v5b.json`. Продакшн-сиблинг `prereg_pass2_signals_r2.json ::
kill_clock[рунг 2]` = **500 с** для ТОГО ЖЕ рунга/образа/карты/ДЦ, и в его `rule` — **шесть замеров
14.5 → 262.5 с**. Гейт НИЖЕ наблюдённого максимума ⇒ KILL раньше, чем возможен замер. Корень: оверхед
рунга 0 занят у сиблинга, который РАСЧИТАЛСЯ, а гейт — у зонда. Починка $0 и посчитана: 500 с →
мёртвый сегмент 560 с = $0.1151, два = $0.2302, дорогой угол + два = **$1.5495 из $2.50**. НЕ ДВИГАЛ:
это зарегистрированное число в преregister'е, чьи деньги уже пошли → заходу 2 нужна НОВАЯ запись.

**✅ Строка create рулинга (d) ОПРАВДАНА.** `--image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`,
EU-RO-1/SECURE/`--ssh`/диск 30 — распарсилось, оба пода по **$0.74/ч**. `--terminate-after` —
**ДАТА-ВРЕМЯ** (`pod create --help`), т.е. `90m` вообще не значение этого флага; из капа вышло
`2026-09-03T19:59:22Z`. `make check` на `5d0386b` (HEAD бандла): **4 313 passed, exit 0**.

## ⏭️ Next / 🚧 Blockers
START RITUAL → рулинг по восьмой паузе: dead-man 500 с в НОВОЙ регистрации, и два денежных вопроса —
(1) несёт ли леджер шага `promo-dev-loop` $0.089622 как открывающий баланс (якорь ПОСЛЕ траты соврал
бы), (2) гард: delta $3.5506 → **$3.6322**, а walk всё ещё $3.5409 — лаг 30–40 мин.
Деньги цикла: `CYCLE 3 SPENT $3.6322 of $7.00 · REMAINING $3.3678`; холдаут $0.30 не тронут.
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
