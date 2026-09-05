<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-05 11:42:33 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
f2a596a docs(progress): the close refused TWICE and wrote nothing; the quotable figure's real path
4ff787a knowledge: s22 — the holdout is shot and read, signal HOLDS and subject is RED
84c7b2e docs(progress): the shot is bought and READ — signal HOLDS 0.7958, subject RED 0.7181
6c6b37f s22(holdout): the reading — signal 0.7958 HOLDS, subject 0.7181 RED, and it is COMPLETE
5174f2b s22(holdout): the ONE shot is bought and the pod is gone — 40 of 40, $0.296617
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
**Last update:** 2026-09-05 (s23, «v1.2-prep»). Этап 1 `SPEC-v2`, карта `STATUS.md`, цикл v3, фаза **v9**. Руками, ≤40 строк.

## 🔥 What's Hot
**s23 сделана целиком за $0, и стоит ОДИН вопрос — деньги итерации 4.** Кодбук v1.2 приехал в ЗАКОН
(`promo_prompts.CODEBOOK`): партнёр акции → `chain`, новое правило 11 для внедоменного треда, три формы
товара в правиле 4, пара «а X де?» → спрос+цена, (д) цена-как-качество → только `цена`; near-quote
«Шикарно…» убран, три синтетических примера. **`--leak-check` ЧИСТ по ВСЕМ ТРЁМ наборам: 440 комментов
(140 dev-40 + 188 dev-2 + 112 holdout-2).** Пины закона сдвинулись: codebook `a587e0d6…` → **`0bbb665a…`**,
template `57dd9d25…` → **`32fa6c42…`**. **holdout-2 вытянут** (`promo_threads_draw_2.json`): популяция
продукта, 40/40/40, пересечения 0, `@matusi_ukr` (21 из 53 промахов) вне. Дро 1 переигрывается ПОБАЙТНО.
**K8 v2** — одна парная `subjects_agree()`, её зовут и грейд, и таблица ошибок; `k8_version` в записи.
**Измерено, а не обещано: алиас «Сильпо» даёт 0 строк, K8 v2 — ровно 1 из 188 (0.7181 → 0.7234).**
Потолок цикла-3 поднят до **$9.00** (рулинг (s) доб. 8): SPENT $5.5059, **REMAINING $3.4941**.

## ⏭️ Next
1. **СТОП: итерация 4 не регистрируется под кап $0.60.** `--register --part dev --cap 0.60` ОТКАЗАЛ:
   dear $1.3100 против $0.6000 (+118.3%), у dev-ноги нет отката на средний угол. На 83 юнитах: боррow
   0.4627/0.5201/**2.4219** · own 88.772 → **1.5719/1.6292/3.5605 (не влезает НИГДЕ)** · темп холдаута
   25.826 → 0.4980/0.5553/**2.6577**. Вопрос тимлиду — в `docs/plans/promo-pulse-1.PROGRESS.md`.
2. После ответа: ноги leg A (dev-40 первым, dev-2 после), `ITERATION = 4`, регистрация → `--pack` →
   итерация 4 (платно) → эталон holdout-2 (тимлид) → выстрел holdout-2 ≤$0.90. c3 — после.

## 🚧 Blockers / долги (названы, не построены)
**ОДИН КРАСНЫЙ ТЕСТ, и он часть стопа:** `test_the_pack_pins_exactly_what_the_pod_re_derives` — пак на
диске итерации 3, а чекаут рендерит новый закон; зеленеет при пересборке пака на регистрации итерации 4.
`make check`: ruff чист · pytest тремя срезами (1000+2027+1293) → **4320 passed, 1 failed, 2 skipped**. · **Ставка холдаута
ВСЁ ЕЩЁ не попала в `measurements.jsonl`** (`write_measurement()` зовётся только из `--project`) — теперь
это половина вопроса (2). · Леджеры `promo-holdout` и `promo-dev-loop` открыты. · Остальное — в PROGRESS.
**⚠️ `make check` НЕ в платной сессии · ⚠️ ТОЛЬКО ОТЦЕПЛЁННЫМ (`os.setsid`) · ⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ · ⛔ `1925810730` · ⛔ `aggregates.py` и `open`**.

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list -a` показывает только running, смотри `pod list -a`.
