<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-05 12:41:05 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
da92e7c docs(progress): the stop's two rate lines are rung_0's OWN verdict, and (2) is a code question
81fe34d docs(progress): s23 is done at $0 and ONE stop is open — iteration 4 cannot be registered at $0.60
4be406e s23(law): the law re-rendered from codebook v1.2, and the leak check over all THREE sets
0224167 s23(K8 v2): sku/brand agree on the product's identity, not its spelling
4a03307 s23(draw-2): the holdout-2 draw — the product's population, 20/20, disjoint from both spent arms
```

## 📋 Recent decisions

- `the-holdout-gate-is-rung-0-fits-plus-the-hard-stop.md` — The holdout's money gate is rung 0 FITS plus the cap as the hard stop — the band gate never runs (ruling 05.09 (r), option ii)
- `INDEX.md` — Decision records
- `the-fence-defeats-the-dispatch-that-fixes-the-array.md` — The fence defeats the dispatch that fixes the array

## 📅 Recent daily logs

- `2026-09-05.md`
- `2026-09-04.md`
- `2026-09-03.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->
# Hot Cache — curated
**Last update:** 2026-09-05 (s24, итерация 4 зарегистрирована). Этап 1 `SPEC-v2`, карта `STATUS.md`, цикл v3, фаза **v10**. Руками, ≤40 строк.

## 🔥 What's Hot
**Стоп s23 ЗАКРЫТ рулингом (t), s24 сделана за $0: итерация 4 ЗАРЕГИСТРИРОВАНА и ЗАПАКОВАНА.** Обе
половины стопа были кодом: `rate_for("dev")` возвращала заимствованную ставку и `own_rate()` не
спрашивала вовсе, а сама `own_rate()` читала три СМОКА (88.772 с/тред — втрое больше всего, чем этот
инструмент когда-либо шёл). Теперь `own_rate()` выбирает по `contract` + `sample == "whole run"`:
mean-угол — среднее ЦЕЛОГО рана самого медленного пода, dear-угол — наибольший max. Условие
`part != "dev"` УШЛО из `rung_0`: на ЛЮБОЙ ноге dear-если-влезает, иначе mean + кап как жёсткий стоп.
**Ставки целых ранов (`--measure-run`, $0):** итерация 2 **17.7118**/88.237, итерация 3
**47.6615**/286.248, холдаут **25.8263**/149.054, n=40 каждая. **Нога dev = ДВЕ руки** (`ARMS`):
dev-40 [0:40] + dev-2 [40:80], 80 тредов. **Рунг 0: cheap $0.8705 · priced $0.9279 · dear $4.9984 НЕ
влезает → FITS на MEAN-угле, жёсткий стоп 5838 с ≈ 97 мин, кап $1.20.** Пак — 80 юнитов; красный тест
позеленел ПО ИМЕНИ. `make check`: **4321 passed, 0 failed, 2 skipped** (было 4320 + 1 failed — тот же
сбор, один тест перевернулся). Цикл-3: SPENT $5.5059, REMAINING $3.4941 из $9.00.

## ⏭️ Next
1. **ПЛАТНАЯ итерация 4 — ничего не блокирует.** `--terminate-after` из
   `results/prereg_promo_dev_loop.json :: step.cap_usd` $1.20 → 5838 с; зарегистрированный бэкстоп
   90 мин = 5400 с кусает ПЕРВЫМ (места на ≈107 тредов). Смок 3 → **GO по трём ответам, полосного
   гейта НЕТ** → 80 → delete → `--close-segment --replies results/promo_dev40_iter4.jsonl`.
2. Потом чтения (см. долг ниже) → эталон holdout-2 (тимлид) → выстрел holdout-2 ≤$0.90 → c3.

## 🚧 Blockers / долги (названы, не построены)
**КРАСНЫХ ТЕСТОВ НЕТ.** · **Главный долг: `--score` не умеет ногу из 80** — одна `GOLD` и
`k8.strata_of(DRAW, PART)`: эталон dev-40 (140 строк) против 80 отвеченных юнитов, `docs/labels-promo-dev2.jsonl`
(188 строк) не открывается. Нужен селектор РУКИ; регистрация пинит только эталон dev-40 (второй пин
запрещён §4 без слова). · **Порядок пака не строго dev-40→dev-2:** смок — ПРАВИЛО по корпусу ноги, две
его единицы из dev-2, поэтому dev-40 закрывается на юните **42 из 80**. · Единицы dev-2 — ЭТО единицы
holdout-40, так что dev-порядок примет `promo_holdout40.jsonl` и напишет правдоподобную строку. ·
Леджеры `promo-holdout` и `promo-dev-loop` открыты. · Остальное — в PROGRESS.
**⚠️ `make check` НЕ в платной сессии · ⚠️ ТОЛЬКО ОТЦЕПЛЁННЫМ (`os.setsid`) · ⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ · ⛔ `1925810730` · ⛔ `aggregates.py` и `open`**.

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list -a` показывает только running, смотри `pod list -a`.
