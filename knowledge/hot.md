<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-06 19:50:01 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
69b7db1 docs(progress): s33 — holdout-2 bought once and READ COMPLETE: signal 0.8021 HOLDS, subject 0.7054 RED; $0.4232 of $0.90; the close waits for billing; no open stop — the next word is the operator's
0c5f488 s33(holdout-2): the ONE shot READ — 40/40 units, 0 unparsed; signal 0.8021 HOLDS, subject 0.7054 RED (79/112) under the instrument frozen at d598573; pod p3krn2lwhhcyyi 2116 s = $0.4232, rate 40.8653 s/thread (n=40); the post-run reading $0.4107; the close REFUSED on «no billing rows yet» — retried next session
c4e4827 money(ledger): promo-holdout2 — the session's ledger line, the pre-pod --note at 16:33:53Z ($0.0000 of $0.90; cycle 3 REMAINING $2.5626)
18eca34 docs(progress): s33 — the holdout-2 line is OPENED (registration, pack, make check green at d519ad4, the pre-pod note); OPEN STOP: the harness denied the pod create — the operator runs runbook §1 or allows it
d519ad4 s33(holdout-2): the pack of the committed registration — 40 units of draw-2's holdout arm, the smoke first; the pack SECOND, its own commit
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `the-registration-opens-the-line.md` — The registration OPENS its line, so §0a lives in the PAID session
- `a-lines-close-settles-against-its-post-run-reading.md` — A step line's close settles against its POST-RUN reading

## 📅 Recent daily logs

- `2026-09-06.md`
- `2026-09-05.md`
- `2026-09-04.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->

# Hot Cache — curated
**Last update:** 2026-09-06 19:47 (s33 checkpoint: выстрел holdout-2 КУПЛЕН ОДИН раз и ПРОЧИТАН — signal HOLDS, subject RED).
Этап 1 `SPEC-v2`, карта `STATUS.md`, цикл v3, фаза **v17**, процесс **Money v2.2**. Руками, ≤40 строк.

## 🔥 What's Hot
**Holdout-2 ПРОЧИТАН ПОЛНОСТЬЮ (s33, 40/40, 0 unparsed) под инструментом `d598573`: signal 0.8021 HOLDS · subject 0.7054
RED (79/112)** — `results/grade_promo_holdout2.json`; страты currency 0.766 / 0.7125, decimal_only 0.6615 / 0.8917; 33 промаха
subject (`promo_holdout2_errors.json`), семь из первых десяти — `chain` эталона (VARUS, KFC, Аврора, McDonald's). По (z):
S2 закрывается КРАСНЫМ на популяции продукта; холдаут потрачен ОДИН раз, не перекупается; **слово — оператора.**
**Линия `promo-holdout2` ОТКРЫТА и названа:** под `p3krn2lwhhcyyi` 16:45:21 → 17:20:37Z, 2116 с = **$0.4232** (сегмент
закрыт, GO; прогноз mean $0.5170); пост-рановое чтение 17:21:10Z **$0.4107**; `--close` ОТКАЗАЛ («no billing rows yet») →
в следующем start-ритуале: read-only walk, затем `--close --tolerance 0.05 --expect-ms 2116000 --until <после 17:20:37Z, до
любого следующего пода>`. **Цикл-3: SPENT $7.8480 / REMAINING $2.1520** (17:21Z, потолок $10.00). Темп ЭТОГО инструмента на
32 GB карте: **40.8653 с/тред (n=40, max 219.4)** — строка `promo_holdout2_seconds_per_thread` в `measurements.jsonl`.
**Ранбук по (aa)3 (`215f80f`):** гейт четырёх пинов по ДИСКУ, exit 1 ДО `--register`, одна цепочка `&&` до коммита; повтор
регистрации = новая линия `-r2` (СТОП) или `--cap` = остаток линии; край hard stop закрывается по walk. Рунги сработали как
записаны: rung 1 GO, дым 12.6 / 26.8 / 219.4 с, GO прочитан на 492.9 с, «DONE» через 1376 с. `make check` **4323/2** на
`d519ad4`; HEAD `69b7db1`, porcelain пуст, подов НЕТ (`pod list -a` []).

## ⏭️ Next — чтение тимлида (§6.2, плановое) → слово оператора по RED → следующая сессия: `--close` линии в start-ритуале
Потом c3 (≤ $0.50, рулинг (l) 2–4), потом удалить том `mp-srv2` ((z)5) — только по слову. **Открытых стопов у исполнителя НЕТ.**

## 🚧 Blockers / долги (названы, не построены)
**⛔ Классификатор auto-режима БЛОКИРУЕТ `runpodctl pod create`** (и скрипт с ним) — только слово оператора В СЕССИИ снимает.
**⚠️ zsh НЕ разбивает `$SSHO` на слова** — опции ssh/scp выписывать явно (4-й раз, ≈ $0.03 пода). · **Край hard stop в
закрытии гарда:** ненулевое пред-подовое чтение при отказавшей пост-рановой `--note` — отказ закрытия навсегда; закрытие на
≥ cap печатает CLOSED и затем exit 1 — это settled. · **⛔ `promo-dev-loop` ОТКАЗЫВАЕТ** — никогда не называется. ·
`--step promo-holdout2` БЕЗ `--part holdout2` = dev-нога под линией (отказ не построен). · `-r2` сам ничего не перенацеливает.
· сюита ~12 мин, 229 файлов — только срезами; тесты ГРЕПАЮТ `hot.md`/PROGRESS — не править, пока идут.
**⚠️ ТОЛЬКО ОТЦЕПЛЁННЫМ (`setsid`) · ⚠️ живость по PID, `pgrep -f` ловит и свой зонд · ⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ ·
⛔ `1925810730` · ⛔ `aggregates.py` и `open`**.
## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list -a` показывает только running, смотри `pod list -a`.
