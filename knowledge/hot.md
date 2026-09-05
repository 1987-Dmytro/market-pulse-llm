<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-05 17:17:29 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
89f775a docs(progress): the handoff command carries a real --note, not the placeholder <why>
b1256fe docs(progress): the tree line stops counting commits it cannot count
2dd8044 knowledge: the Stop hook's own stamps from s27 — the tree PROGRESS calls clean
0fd03fb docs(progress): the operator's word closes s27 — the close is carried to the next session, named
d1ec125 docs(progress): PROGRESS is 60 lines, and the tree line stops claiming a stale hash
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
**Last update:** 2026-09-05 (закрытие дня; итерация 4 НЕПОЛНА — OOM, рулинг (w) уже ответил). Этап 1 `SPEC-v2`, карта `STATUS.md`, цикл v3, фаза **v12**. Руками, ≤40 строк.

## 🔥 What's Hot
**Итерация 4 КУПЛЕНА и НЕПОЛНА (§6.5).** Под `kzcnhe01mgdwvk`, 3364 с, **$0.691489**, рунг 1 GO.
**Смок не вернулся целиком:** третий юнит `@VARUS_channel:8647` (**14281 симв., самый длинный
рендер**) умер на `torch.OutOfMemoryError` — 338 MiB при 23.19 из 23.52 GiB. **GO НЕ записан**, ни
один из 80 не куплен; смок-правило «кратчайший/медиана/длиннейший» окупило себя. **(v)+v11:** один
платный ран = одна линия шага, гард читается С `--step`. **(w)+v12:** сбой ОБСЛУЖИВАНИЯ двигает
обслуживание, не инструмент. `promo-iter4` $0.6690/$1.20, закрыть завтра; цикл-3 REMAINING **$2.8057**.

## ⏭️ Next
**Стоп по OOM ЗАКРЫТ рулингом (w) — завтра ПОКУПКА, итерация 5, и ничего кроме неё.**
1. Сначала за $0: **`--close` линии `promo-iter4`** (`--expect-ms 3364000 --tolerance 0.05`). Затем
   **транспортный дефект по §4**: раннер ловит исключение юнита, пишет ERROR-ответ (`error`, имя
   исключения, юнит) и выходит ненулём; Мак считает ERROR среди трёх смок-ответов за «смок не
   вернулся» и удаляет СРАЗУ. ОДИН тест в обе стороны, тем же коммитом; пин раннера едет с фиксом.
2. **Инструмент НЕ движется** (закон v1.2, шаблон, рендер, потолок 4000, NF4/bf16, greedy, парсер).
   Движется ОБСЛУЖИВАНИЕ: карта **≥32 GB** в EU-RO-1 (RTX PRO 4500 32 GB ~$0.72/ч, иначе A6000 / L40S)
   по дорогому предложению дня **≤$0.90/ч** — 4090 под этот промпт НЕ покупается; плюс
   `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`. Оба — в `re_emission`, `extractor_version` тот же.
3. **Итерация 5 — линия `promo-iter5`, кап $1.40** (оператор 16:35), FITS на mean по цене дня,
   жёсткий стоп из капа, бэкстоп поднимается до минут капа, если кусает первым. Последовательность
   (v)4. Это ПЯТАЯ и последняя из зарегистрированных: RED → вопрос закрывается красным и решает
   оператор; GREEN → эталон holdout-2 и выстрел на `promo-holdout2` ≤$0.90, потом c3.

## 🚧 Blockers / долги (названы, не построены)
**КРАСНЫХ ТЕСТОВ НЕТ** (прогон 4320/1 — красный был порядок «коммит → пак», позеленел по имени). ·
**`--open`/`--close-segment` пишут `results/promo_dev_loop_run.json` в масштабе ПАРТИИ, не ЛИНИИ:**
$1.9345 против $0.6690, «OVER» на здоровом закрытии; `--expect-ms` ОБЯЗАН фильтровать по
`created_at >=` якоря линии (проверено: ровно ОДИН сегмент, 3364000 мс). · **Ставки целого рана у
этого пода НЕТ**, у холдаута тоже. · **Срез `make check` — ЗАКРЫТЫЙ список:** `ls tests/test_*.py` =
**229**; сюита ~12 мин. · Леджеры `promo-iter4` (закрыть завтра), `promo-holdout`, `promo-dev-loop` открыты.
**⚠️ `make check` НЕ в платной сессии · ⚠️ ТОЛЬКО ОТЦЕПЛЁННЫМ (`os.setsid`) · ⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ · ⛔ `1925810730` · ⛔ `aggregates.py` и `open`**.
## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list -a` показывает только running, смотри `pod list -a`.
