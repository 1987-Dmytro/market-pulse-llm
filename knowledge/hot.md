<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-05 09:22:09 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
1b6aa9f docs(progress): the block starts at `--register`, not at `--project` — §0a writes the dev bands
96be763 knowledge: the Stop hook's own regeneration of the index and the day's log
9d82b48 docs(progress): back under the file's own 60-line cap
2bf1f86 docs(progress): holdout-prep is done at $0 and TWO stops are open — the shot is blocked
858ead0 s20(holdout-prep): `use_part` binds BOTH halves — `use_part("dev")` was a silent no-op
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `the-fence-defeats-the-dispatch-that-fixes-the-array.md` — The fence defeats the dispatch that fixes the array
- `the-invite-hash-is-resolved-at-the-call-site.md` — The invite hash is resolved at the call site, not in the registry

## 📅 Recent daily logs

- `2026-09-05.md`
- `2026-09-04.md`
- `2026-09-03.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->
# Hot Cache — curated
**Last update:** 2026-09-05 08:25 (s22, выстрел сделан). Этап 1 `SPEC-v2`, карта `STATUS.md`, цикл
`PROCESS.md` v3, фаза **v8**. Руками, ≤40 строк.

## 🔥 What's Hot
**✅ ХОЛДАУТ ВЫСТРЕЛЕН (s22, $0.296617 из капа $1.10) — ЧТЕНИЕ ПОЛНОЕ, ВОПРОС S2 ЗАКРЫТ ЧИСЛОМ.**
Сигнал **0.7958** ✅ (бар 0.75) · субъект **0.7181** ❌ (бар 0.80) — `results/grade_promo_holdout40.json`.
188 строк из **40 из 40** юнитов, **0 unparsed**, все `finish=stop`, id-множество равно порядку записи —
по §6.5 чтение СЧИТАЕТСЯ, и по (r)5 оно ЗАКАНЧИВАЕТ выстрел: красный бар не двигает гейт, он отвечает.
Против dev-бара (0.8714 / 0.9104) субъект упал на **0.1533** на непересекающейся половине того же
seed-42. 53 промаха субъекта, видимый кластер — **chain↔brand на банковском треде `@VARUS_channel:4422`**
(`izibank`, `OTP банк`). Под `pcu2fqc7ebwfcw` жил 1443 с и шёл в **3.4× БЫСТРЕЕ** зарегистрированной
ставки (25.826 с/тред против 88.772) — тот же разброс хостов 1.5–2.3×, но в нашу сторону.
Инструмент байт-в-байт тот, что взял dev-бар ((q)2 — доказано по пинам dev-регистрации).
**Рулинг (r) снял ОБА стопа s21:** гейт денег холдаута = FITS рунга 0 + жёсткий стоп, полосный гейт не
запускался, `project()` не тронут; таблица решений в записи ветвится по ноге (нашлось СЕМЬ полей, не 4).

## ⏭️ Next
**Слово тимлида по КРАСНОМУ бару субъекта.** Потом «c3» ((l)2–4, ≤ min($0.50, остаток)), потом том
`mp-srv2` удаляется. near-quote и синхронизация кодбука-документа РАЗБЛОКИРОВАНЫ ((q)2 ставила их за
выстрелом). Исполнителю в очередь ничего не поставлено сверх этого.
**💰 остаток цикла 3: $1.5469 из $7.00.** Леджер `promo-holdout` **ОТКРЫТ**: `--close` ОТКАЗАЛ (биллинг
не сел — 0 мс против 1443000), НЕ форсирован; цитируемое число — **$0.296617** из run record.

## 🚧 Blockers / долги (названы, не построены)
**`write_measurement()` зовётся ТОЛЬКО из ветки `--project`** (`promo_dev_pass.py:1538`), а (r)2 её не
запускает → ставка холдаута никогда не попадёт в `measurements.jsonl`; следующая нога по `own_rate()`
прочтёт DEV-строку 88.772 с там, где этот под намерил 25.826. · `gates.terminate_after_minutes` —
заимствованные 5400 с, на 49 с БОЛЬШЕ собственного стопа 5351.4 с ($1.11 против капа $1.10); `STOP_AT`
берёт min(). · Поле, добавленное в запись позже, не ветвится, пока кто-то не заметит. · Остальные — в
`docs/plans/promo-pulse-1.PROGRESS.md` («named, not built»).
**⚠️ `make check` НЕ в платной сессии · ⚠️ ТОЛЬКО ОТЦЕПЛЁННЫМ (`os.setsid`) · ⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ · ⛔ `1925810730` · ⛔ `aggregates.py` и `open`**.

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list -a` показывает только running, смотри `pod list -a`.
