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
**Last update:** 2026-09-05 (close, s22). Этап 1 `SPEC-v2`, карта `STATUS.md`, цикл v3, фаза **v8**. Руками, ≤40 строк.

## 🔥 What's Hot
**✅ ХОЛДАУТ ВЫСТРЕЛЕН И ПРОЧТЁН — ВОПРОС S2 ЗАКРЫТ ЧИСЛОМ. Сигнал 0.7958 ✅ (бар 0.75) · субъект
0.7181 ❌ (бар 0.80)** — `results/grade_promo_holdout40.json`. Чтение ПОЛНОЕ по §6.5: 188 строк из
**40 из 40** юнитов, **0 unparsed**, все `finish=stop`, id-множество равно порядку записи. По (r)5 это
ЗАКАНЧИВАЕТ выстрел: красный бар не двигает гейт, он отвечает. Против dev-бара (0.8714 / 0.9104),
взятого ПОБАЙТНО тем же инструментом, субъект упал на **0.1533**; кластер из 53 промахов —
**chain↔brand на банковском треде `@VARUS_channel:4422`** (`izibank`, `OTP банк`).
**Деньги: $0.296617 из капа $1.10.** Под `pcu2fqc7ebwfcw` 1443 s, шёл в **3.4× быстрее**
зарегистрированной ставки (25.826 s/тред против 88.772) — разброс хостов 1.5–2.3× в нашу сторону.
**Рулинг (r) снял оба стопа s21:** гейт денег = FITS рунга 0 + жёсткий стоп, полосный гейт §5 НЕ
запускается, `project()` не тронут; поля записи с решениями ветвятся по ноге — рулинг называл ЧЕТЫРЕ,
аудит нашёл **СЕМЬ**. Разбор: [[the-holdout-gate-is-rung-0-fits-plus-the-hard-stop]].

## ⏭️ Next
1. **Слово тимлида по КРАСНОМУ бару субъекта** — закон заморожен, перевыстрела по §8 (e) нет.
2. «c3» ((l)2–4, ≤ min($0.50, остаток)); после него том `mp-srv2` удаляется.
3. near-quote и синхронизация кодбука-документа РАЗБЛОКИРОВАНЫ ((q)2 ставила их за выстрелом).
**💰 цикл 3: SPENT $5.4962, REMAINING $1.5038 из $7.00** (гард 09:05).

## 🚧 Blockers / долги (названы, не построены)
**Леджер `promo-holdout` ОТКРЫТ:** `--close` отказал ДВАЖДЫ, не форсирован (0 мс, затем $0.2130
против $0.296617); оба отказа не записали НИЧЕГО — в `gpu_sessions` ровно одна запись. Цитируемое
число — `results/promo_holdout_run.json :: gates[1].spent_all_segments_usd`. `promo-dev-loop` тоже
открыт ((r)4). · **`write_measurement()` зовётся ТОЛЬКО из ветки `--project`** (`promo_dev_pass.py:1538`),
(r)2 её не запускает → ставка холдаута не попадёт в `measurements.jsonl`; следующая нога по
`own_rate()` прочтёт DEV-строку 88.772 s там, где под намерил 25.826. · **`make check` идёт ~12 мин —
больше потолка ОДНОГО вызова:** гонять `ruff` + три среза `tests/`, итог 4320 / 2 skipped. · Остальное
— в `docs/plans/promo-pulse-1.PROGRESS.md` («named, not built»).
**⚠️ `make check` НЕ в платной сессии · ⚠️ ТОЛЬКО ОТЦЕПЛЁННЫМ (`os.setsid`) · ⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ · ⛔ `1925810730` · ⛔ `aggregates.py` и `open`**.

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list -a` показывает только running, смотри `pod list -a`.
