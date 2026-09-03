<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-03 10:58:08 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
168ecc8 docs(stop,report): the full make check tail — 18 failed, 4 247 passed, 17 errors; 32 of 35 are the fork
4707516 docs(stop): the fork's blast radius on the suite, measured — 8 failed, 26 passed, 10 errors
379fcfa docs(report): 30 lines — the population is bought, the phase stops on the seal's fork
218e027 s4(run 2): the WHOLE C2 population bought — 3 008 pages + 385 posts, $3.0335 of $3.95
b2af6c7 tools(rank): the $0 remainder ranker, MEASURED — the bar buys nothing, the usable cut is score >= 1
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
**Last update:** 2026-09-03 (сессия 4, платная нога S4 ЗАКРЫТА). Этап 1 `SPEC-v2-promo-pulse.md`, карта `STATUS.md`,
цикл `PROCESS.md` v2.1. Руками, ≤40 строк; археология — в логах дня.

## 🔥 What's Hot
**⏸️ `promo-pulse-1` — ПЯТАЯ ПАУЗА, НЕ ПРО ДЕНЬГИ. ОКНО C2 В БАЗЕ.** Рулинг 02.09 (d) shape 1 (`1161187`): две
запечатанные витрины в одном `pulse.db`, каждая через СВОЙ seal, живой реестр не читается нигде. `w1` пересобирает
**902/902** листа запечатанного `window_summary_5c2.json`; `w2` — **17 каналов · 3 397 маркеров · 1 113 позиций**.
`--register-addendum` добавил `registry.yaml = eff8ba5b…` и `window_id = w2` (12 вставок / 0 удалений, повтор
ОТКАЗЫВАЕТ). Строки — по ЗАКРЕПЛЁННЫМ id: w1 = манифест по `selection_pin` + D-cut, ПЕРЕСЧИТАННЫЙ и сверенный
с `postcut_c3b :: kept.ids_sha256`; 20 постов D-cut — в ОБОИХ окнах.

**⛔ ДВЕ ВИЛКИ (`docs/plans/promo-pulse-1.STOP.md`) — ЖДУТ РУЛИНГА.** (1) shape 1 НЕ восстанавливает ЗАПЕЧАТАННЫЕ
артефакты w1: ран C2 дописывал в ТЕ ЖЕ файлы. ИЗМЕРЕНО по листьям: `dashboard_data_w1.json` расходится в **55 листьях,
КАЖДЫЙ под `provenance.*`** (evidence/inputs/producers), **ни одного снаружи**, все 4 474 листа данных идентичны →
проверка самого рулинга «w1 export sha byte-identical» НЕВЫПОЛНИМА при одном общем `data/derived/`. Раскол корня
восстановил бы всё ровно: **23 файла не тронуты · 15 точный байтовый ПРЕФИКС · 0 разошлись**. (2) `positions` не
различает картинку и текст (7 постов C2 прочитаны ОБЕИМИ ногами): `carrier` добавлен в PRIMARY KEY,
`test_positions_is_untouched` красный и НАЗВАН, не ослаблен.

**✅ Рулинг 03.09 применён; ждёт ЧТЕНИЯ тимлида за $0.** `CODEBOOK` несёт шесть дельт, `codebook_version()` =
`a97d3c71b8cf9b14…`; рендер `@VARUS_channel` root `6009` — `scripts/promo_dev_pass.py --render 6009`. Эталон через все
четыре хука: **140 about + 84 signal, 0 отказов**, покрытие 140/140. **Грейдер ПРОВЕРЕН на боевом эталоне, четыре
направления, $0:** сам с собой 1.0/1.0 · неверный субъект → subject 0.0 RED, сигналы 1.0 (бары НЕЗАВИСИМЫ) ·
сигналы сняты → 0.15 RED = ровно 6/40 (число рулинга, выведенное ДРУГИМ инструментом) · молчание → оба RED.
**S9 $0-половина ГОТОВА:** `--dry-run` →
`results/promo_dev40_prep.json` — 40 рендеров, 209 897 знаков; итерация 1 ОГРАНИЧЕНА, не оценена (ставки для ЭТОГО
инструмента НЕТ, взята взаймы `pass2_r2_seconds_per_thread` 23.76 с, n=75): **$0.2915 по среднему · $1.659 по
максимуму**, без бута, против $2.50 — одна итерация влезает в обоих углах, пять только по среднему.
**Платный K8 НЕ запускать до чтения рендера.**

**Проверки (s5):** (a)(b)(c)(d)(e-$0)(f)(g)(h)(i)(l) показаны. Дро-50 по C2: **50 из 1 113, 12 сетей, sha
`61b4fda7fdc83197…`** — positions-50 против ЭТОЙ sha. `make check` @ `6b6fe44` = **13 failed · 4 268 passed ·
7 errors** (35 → 20 красных, passed +21): каждый красный — вилка; счётная половина (j) ВЫПОЛНЕНА (4 268 ≥ 4 266),
держит только зелёность. Dv903 закрыт рулингом; 7 редов от `--window w2` были МОИ и починены.
**НЕ выводить:** $0.00030669/с, резерв $0.2843, хвост 60 с; 16 из 405 постов C2 без улики (14 `@epicentrk_sale`).

## ⏭️ Next
START RITUAL → два рулинга (корень `data/derived` · ключ `positions`) → чтение рендера → S9 платная петля dev-40 →
positions-50 → закрыть (d)(e)(j). Шаг НЕ закрыт: `--close --tolerance` ждёт дробь от тимлида.

## 🚧 Blockers
**⛔ ДВЕ ВИЛКИ ВЫШЕ**, денег не касаются; `PROMO-PULSE-1 $3.1909 of $3.95` · `CYCLE 3 $3.4826 of $7.00`; комната
$0.2333/день. **⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ** (`:366/:171/:153`). **⛔ `1925810730` и инвайт-хэш неадресуемы.**
**⚠️ Фоновые задачи харнеса убивают друг друга** — платный ран отцеплённым (`os.setsid()`), Dv904.

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт
обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list` показывает только running, смотри `pod list -a`.
