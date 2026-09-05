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
**Last update:** 2026-09-05 12:27 (s23 checkpoint, «v1.2-prep»). Этап 1 `SPEC-v2`, карта `STATUS.md`, цикл v3, фаза **v9**. Руками, ≤40 строк.

## 🔥 What's Hot
**s23 сделана целиком за $0, и стоит ОДИН вопрос — деньги итерации 4.** Кодбук v1.2 приехал в ЗАКОН
(`promo_prompts.CODEBOOK`): партнёр → `chain`, правило 11 для внедоменного треда, три формы товара в
правиле 4, пара «а X де?» → спрос+цена, (д) цена-как-качество → только `цена`; near-quote «Шикарно…»
убран, три синтетических примера. **`--leak-check` ЧИСТ по ВСЕМ ТРЁМ наборам: 440 комментов (140 dev-40
+ 188 dev-2 + 112 holdout-2).** Пины закона: codebook `a587e0d6…` → **`0bbb665a…`**, template `57dd9d25…`
→ **`32fa6c42…`**. **holdout-2 вытянут** (`promo_threads_draw_2.json`): популяция продукта, 40/40/40,
пересечения 0, `@matusi_ukr` (21 из 53 промахов) вне; дро 1 переигрывается ПОБАЙТНО. **K8 v2** — одна
парная `subjects_agree()`, её зовут и грейд, и таблица ошибок. **Измерено: алиас «Сильпо» даёт 0 строк,
K8 v2 — ровно 1 из 188 (0.7181 → 0.7234).** Потолок цикла-3 → **$9.00**: SPENT $5.5059, REMAINING $3.4941.

## ⏭️ Next
1. **СТОП: итерация 4 не регистрируется под кап $0.60.** Прогон САМОГО `rung_0` на настоящей ноге
   (3 смока + 80): `rate_for("dev")` = borrowed 23.760/135.232 → 0.4627/0.5201/**2.4219**, issued dear,
   FITS=False · `own_rate()` = 88.772/201.967 → **1.5719/1.6292/3.5605**, issued mean, FITS=**False**.
   Вопрос (2) — к КОДУ: `rate_for("dev")` не спрашивает `own_rate()` вообще, а темп 25.826 не попал в
   `measurements.jsonl`. Три части вопроса — в `docs/plans/promo-pulse-1.PROGRESS.md` (стоп, 15 строк).
2. После ответа: ноги leg A (dev-40 первым, dev-2 после), `ITERATION = 4`, регистрация → `--pack` → итерация 4 (платно) → эталон holdout-2 (тимлид) → выстрел holdout-2 ≤$0.90. c3 — после.

## 🚧 Blockers / долги (названы, не построены)
**ОДИН КРАСНЫЙ ТЕСТ, и он часть стопа:** `test_the_pack_pins_exactly_what_the_pod_re_derives` — пак на
диске итерации 3, а чекаут рендерит новый закон; зеленеет при пересборке пака на регистрации итерации 4.
`make check`: ruff чист · pytest тремя срезами (1000+2027+1293) → **4320 passed, 1 failed, 2 skipped**. · **Ставка холдаута
ВСЁ ЕЩЁ не попала в `measurements.jsonl`** (`write_measurement()` зовётся только из `--project`) — теперь
это половина вопроса (2). · **Второй красный назван заранее:** `test_promo_dev_pass.py:61` (`== 40`) и
`:202` (`SMOKE_N + 40`) покраснеют при `dev_threads()` == 80 — две переписки §6.6, не стоп. · Леджеры
`promo-holdout` и `promo-dev-loop` открыты. · Остальное — в PROGRESS.
**⚠️ `make check` НЕ в платной сессии · ⚠️ ТОЛЬКО ОТЦЕПЛЁННЫМ (`os.setsid`) · ⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ · ⛔ `1925810730` · ⛔ `aggregates.py` и `open`**.

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list -a` показывает только running, смотри `pod list -a`.
