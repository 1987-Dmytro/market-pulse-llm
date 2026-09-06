<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-06 13:01:22 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
4b996af s30(runbook §0a): the slice list ASSERTS its coverage and COMPUTES the floor
1abfd82 docs(progress): the stop is answered by (y)(ii) — next is the paid iteration 5
65d1285 s30(runbook §0a): the pack is committed SECOND, and §0a is the paid session's first minutes
c5a22f3 docs(team-lead): ruling (y) — the registration OPENS its line, so §0a lives in the paid session
31a6bc5 s29(runbook,progress): the gpu-id is read from the record, and the damaged-file case is named
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `a-lines-close-settles-against-its-post-run-reading.md` — A step line's close settles against its POST-RUN reading
- `the-holdout-gate-is-rung-0-fits-plus-the-hard-stop.md` — The holdout's money gate is rung 0 FITS plus the cap as the hard stop — the band gate never runs (ruling 05.09 (r), option ii)

## 📅 Recent daily logs

- `2026-09-06.md`
- `2026-09-05.md`
- `2026-09-04.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->

# Hot Cache — curated
**Last update:** 2026-09-06 12:56 (s30; стоп ЗАКРЫТ (y), §0a исправлен). Этап 1 `SPEC-v2`,
карта `STATUS.md`, цикл v3, фаза **v14**, процесс **Money v2.1**. Руками, ≤40 строк.

## 🔥 What's Hot
**Ничего не потрачено в s29/s30: цикл-3 SPENT $6.2494 / REMAINING $2.7506 из $9.00** (чтение s28
15:28Z, НЕ перечитано — гард не вызывался). `promo-iter4` $0.694815/$1.20 и `promo-holdout`
$0.298209/$1.10 ЗАКРЫТЫ. **`promo-iter5` НЕ ЗАЯКОРЕН и НЕ ДОЛЖЕН БЫТЬ:**
`results/spend_promo_iter5.json` создаёт `--register` СЛЕДУЮЩЕЙ, платной сессии за минуты до create.
**Рулинг (y): регистрация ОТКРЫВАЕТ линию** → §0a живёт в платной сессии; (x)2 отозван; PHASE v14
§6.1, PROCESS «Деньги» v2.1 (+ «стоящий закон бьёт рулинг по механике — назвать в PROGRESS, без
остановки»). **s30 (`c5a22f3`, `65d1285`) починил §0a ранбука, 5 мест:** укус верификатора —
`--pack` стоял МЕЖДУ `--register` и коммитом, где `committed_registration()` ОТКАЗЫВАЕТ (запись
переписана и не закоммичена) → теперь ДВА коммита. **`make check` того HEAD (`4b996af`): срезы САМИ
проверяют покрытие и САМИ считают пол (сумма хвостов против 4266)** — прежняя просьба «сложи три
числа» стояла там, где якорь уже живой; негативный контроль `'146,200p'` отказывает.
**Рунг 0 за $0 (s29): FITS на mean $0.8470 против капа $1.40**, dear $4.8633, hard stop 7000 с.
`make check` **4323/2** (1000+2030+1293 по срезам 60+85+84 из 229), ruff чист, exit 0.

## ⏭️ Next — ПЛАТНАЯ итерация 5, вся сессия, открытых стопов НЕТ
**Ранбук `scripts/runbook_promo_dev_1.md` пастится целиком.** §0a (первые минуты платной сессии,
перед ним — только стартовый ритуал, НИКАКОЙ разработки): `--dry-run` → `--register --part dev
--step promo-iter5 --cap 1.40` (FITS; ЭТО и есть якорь линии) → коммит prep+запись+леджер → `--pack`
→ коммит пака → `make check` срезами (COVER/FLOOR — команды) → §0 предподовый `--note` (ОДНА строка) →
§1 create, gpu-id ИЗ ЗАПИСИ → §2 dead-man → §3 бандл → §4 отцеплённый запуск → §5 смок, GO → §6
delete, ПОСТ-РАНОВЫЙ `--note`, `--close --expect-ms --until --tolerance 0.05` → §7 `--score --arm
dev40` (БАР 0.80/0.75) и `--arm dev2` (ЧТЕНИЕ). Отказ на `--register` (цена ушла, карты нет в стоке,
FITS потерян) ЗАКАНЧИВАЕТ ход выводом гарда и листинга — до всякого create. Топ-апа не будет.
**ПЯТАЯ и последняя (§2):** GREEN → эталон holdout-2 (тимлид, вслепую) → `promo-holdout2` ≤$0.90 →
c3. RED → вопрос закрыт красным, решает оператор.

## 🚧 Blockers / долги (названы, не построены)
**⛔ `promo-dev-loop` ОТКАЗЫВАЕТ: $2.5799 из своих $2.50, exit 1**, закрыть нельзя ((r)4) — **больше
никогда не называется**; кап брать ИЗ ЛЕДЖЕРА, не с руки. · **(y)4 риск 2: исключение с ПУСТЫМ
текстом читается как ОТВЕЧЕНО** (читатели смотрят на truthy `error`) — фикс `"exception" in row` +
тест (w)3, ПЕРВЫЙ $0-пункт ПОСЛЕ итерации 5. · **(y)4 риск 3: `close_segment` суммирует ВСЕ сегменты
партии против капа** — его `OVER` ложное поле, деньги в линии гарда; фильтр по `anchored_at`, тот же
пункт. · **`prereg_promo_holdout.json` ЗАПЕЧАТАН под старой sha раннера.** · сюита ~12 мин, 229 файлов.
**⚠️ `make check` ТЕПЕРЬ ВНУТРИ §0a платной сессии** (срезами, до create — (y)3/PROCESS v2.1
отменили прежнее «НЕ в платной сессии»). **⚠️ ТОЛЬКО ОТЦЕПЛЁННЫМ (`os.setsid`) · ⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ · ⛔ `1925810730` · ⛔ `aggregates.py` и `open`**.
## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list -a` показывает только running, смотри `pod list -a`.
