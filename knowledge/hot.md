<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-06 10:49:41 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
f99f8d4 report(promo-pulse-1): three claims made evidenced instead of asserted
b624bca knowledge: the hooks' stamps for s28
f1df71a report(promo-pulse-1): sessions 9-28 — S2 is one paid run from an answer, and every line but one is closed
c145936 docs(progress): the dev-loop line is read at its OWN cap, not at one I typed
847e8e2 docs(progress): the verifier's reading, and the HEAD it was taken over
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `a-lines-close-settles-against-its-post-run-reading.md` — A step line's close settles against its POST-RUN reading
- `the-holdout-gate-is-rung-0-fits-plus-the-hard-stop.md` — The holdout's money gate is rung 0 FITS plus the cap as the hard stop — the band gate never runs (ruling 05.09 (r), option ii)

## 📅 Recent daily logs

- `2026-09-05.md`
- `2026-09-04.md`
- `2026-09-03.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->

# Hot Cache — curated
**Last update:** 2026-09-05 (закрытие дня; обе линии ЗАКРЫТЫ, транспорт починен, покупка — завтра). Этап 1 `SPEC-v2`, карта `STATUS.md`, цикл v3, фаза **v13**. Руками, ≤40 строк.

## 🔥 What's Hot
**Деньги сведены: цикл-3 SPENT $6.2494 / REMAINING $2.7506 из $9.00**, баланс $8.2306, якорь $14.4800.
`promo-iter4` ЗАКРЫТ **$0.694815/$1.20** (walk 3 363 287 из 3 364 000, settle 2.73% от ссылки
$0.7143). `promo-holdout` ЗАКРЫТ **$0.298209/$1.10** ПО ОДНОМУ WALK — его единственная запись 0.0 и
до пода, допуск пропущен. **PHASE v13 §6.1:** ссылка гейта = пост-рановое `--note` после удаления
пода и ДО любого следующего; линия без него закрывается по walk и позднего чтения НЕ БЕРЁТ.
**(w)3 починен за $0:** раннер пишет ERROR-ответ юнита в out-файл и выходит ненулём, Мак читает его
как «смок не вернулся» и удаляет СРАЗУ. `make check` **4322/2 skipped**, exit 0. Красных тестов нет.

## ⏭️ Next
**Завтра ПОКУПКА — итерация 5, и ничего кроме неё. Ни одна линия больше не мешает.**
1. **$0-половина:** ре-эмиссия регистрации (`--register` сам пересчитает `pinned_inputs` с диска —
   новая sha раннера `43646d52e12f…` ляжет туда) + **фит-пруф §6.5, единственный настоящий долг**:
   самый длинный зарегистрированный рендер доказан помещающимся ДО пода. (w)3 починил СООБЩЕНИЕ о
   крахе, не его предотвращение.
2. **Инструмент НЕ движется** (закон v1.2, шаблон, рендер, потолок 4000, NF4/bf16, greedy, парсер).
   Движется ОБСЛУЖИВАНИЕ: карта **≥32 GB** в EU-RO-1 (RTX PRO 4500 32 GB ~$0.72/ч, иначе A6000 /
   L40S) по дорогому предложению дня **≤$0.90/ч** — 4090 под этот промпт НЕ покупается; плюс
   `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`. И раннер — он тоже обслуживание.
3. **Итерация 5 — линия `promo-iter5`, кап $1.40** (оператор 16:35), FITS на mean по цене дня,
   жёсткий стоп из капа. ПЯТАЯ и последняя: RED → вопрос закрывается красным и решает оператор;
   GREEN → эталон holdout-2 (тимлид, вслепую) и выстрел `promo-holdout2` ≤$0.90, потом c3.
4. **Её закрытие уже расписано:** под удалён → СРАЗУ одно `--note` на линию → `--close` с
   `--until` (окно iter4 теперь ловушка для безграничного walk) → биллинг может отказать ЧАСАМИ,
   а не решением: повтор в ритуале старта, read-only walk ПЕРВЫМ.

## 🚧 Blockers / долги (названы, не построены)
**⛔ `promo-dev-loop` — единственная открытая линия, и она ОТКАЗЫВАЕТ: $2.5799 из своих $2.50,
exit 1.** Кап не поднять, закрыть нельзя (walk безграничен по построению, (r)4) — её просто **больше
никогда не называют**. Кап брать ИЗ ЛЕДЖЕРА, не с руки: я прочёл её при $2.16, который напечатал. ·
**Фит-пруф §6.5 не построен.** · **`--open`/`--close-segment` пишут `promo_dev_loop_run.json` в
масштабе ПАРТИИ, не ЛИНИИ** — `latest` = «OVER»; `--expect-ms` брать из сегмента с `created_at >=`
якоря линии. · **Ставки целого рана нет ни у iter4, ни у холдаута.** · **`prereg_promo_holdout.json`
ЗАПЕЧАТАН под старой sha раннера и НЕ перепинивается** — это факт записи, а не красное. ·
**Срез `make check` — ЗАКРЫТЫЙ список:** `ls tests/test_*.py` = **229**; сюита ~12 мин.
**⚠️ `make check` НЕ в платной сессии · ⚠️ ТОЛЬКО ОТЦЕПЛЁННЫМ (`os.setsid`) · ⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ · ⛔ `1925810730` · ⛔ `aggregates.py` и `open`**.
## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list -a` показывает только running, смотри `pod list -a`.
