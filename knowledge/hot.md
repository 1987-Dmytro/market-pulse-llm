<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-10 15:54:46 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
b26da6d docs(report): chain-fold — 83 on the screen, `marketopt_private` at 0, and no graded number moved
3cc99ad docs(progress): back under the ≤60-line cap with the two added lines kept
accd83a docs(progress): two reaches the item's own check does not cover — `chain_key`'s callers, and the sibling readers' second defect
6fb5009 docs(progress): the deviation line fits the ≤60-line cap the ruling sets for this file
cc7cc6e docs(progress): s45 — «chain-fold» DONE at $0, no open stop; ONE Маркетопт, 83 rows, no graded number moved
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `a-published-number-has-one-reader.md` — A published number has ONE reader, and a missing source is a refusal by name
- `the-registration-opens-the-line.md` — The registration OPENS its line, so §0a lives in the PAID session

## 📅 Recent daily logs

- `2026-09-10.md`
- `2026-09-09.md`
- `2026-09-08.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->

# Hot Cache — curated
**Last update:** 2026-09-09 s43 «kk-close»: DOLLAR_FLOOR + закрытие c3 $0.2577 + том УДАЛЁН, $0; стопов НЕТ.
Этап 1 `SPEC-v2`, карта `STATUS.md`, цикл v3, фаза **v27**, процесс **Money v2.6**. Руками, ≤40 строк.

## 🔥 What's Hot — c3 КУПЛЕНА и ЗАКРЫТА: $0.2577 из капа $0.80, линия ЗАКРЫТА, том УДАЛЁН
**Отгружаемое (петля хуки + P1, `grade_promo_loop_readings.json`):** dev-3 **0.7411 (83/112) ❌ 0.80**
· сигналы **0.7937 ✅ 0.75**; dev-40 0.8857 / 0.8667, dev-2 0.9043 / 0.8296 — одинаковы обоими путями.
Чтения рядом как «reading» (0.7500 / 0.8021, сырьё 0.7054, holdout-40 0.7181), НЕ переписываются;
ничьи dev-3 — **16 из 28**; holdout-3 — РЕЗЕРВ. **c3 (s42, платно):** 30 страниц + 8 постов ОТВЕЧЕНЫ,
57 позиций, `stopped false`; мерено **19.828 s/page** против прогноза 3.369 — прогноз был 5.9× оптимистичен,
влезло из-за КАПА, не из-за прогноза. **Закрытие (s43):** `DOLLAR_FLOOR = $0.05` рядом с относительной
полосой (`max(floor, tolerance × recorded)`, паттерн `MS_FLOOR`) — щель $0.0305 = целый поздний вид
`pods` при 5% = $0.0114 на $0.2272; ГРАДУИРОВАЛ ПОЛ, не полоса. `--tolerance` осталась 5%.

## ⏭️ Next — «chain-fold» ($0, форма (b), (gg)2 — P1 перемеряется функциями продукта)
Дальше: «launch-field» ($0) → e2e на чистом клоне + `draw_truth_20` → гейт **12.09** (резерв 13.09).
Подов, эндпоинтов и ТОМОВ нет — `network-volume list` = `[]`, дрип ≈$0.24/day ОСТАНОВЛЕН.

## 🚧 Blockers / долги (названы, не построены)
**Файлы тимлида — только Read-tool; харнес-файл — только Write-tool, `diff` = пруф.**
**⚠️ `promo_projection_c2.json` НЕ ВОСПРОИЗВОДИМ производителем** (живое чтение гарда + растущий
ledger внутри sha-закреплённой записи): пруф такой записи — её пин, не перепрогон.
**Деньги: гард печатает `REMAINING $1.1602`**, цикл-3 $8.8398 из $10.00; тома БОЛЬШЕ НЕТ, дрипа нет.
`make check` **4330/2** на `c5cad96` (весь прогон, 11:51); два коммита после него двигают только
`spend_promo_c3.json` / `spend_cycle3.json` — 151 тест, которые их читают, зелёные. $0 за сессию s43. · K12 читает настоящий `results/`, `tick.REGISTRY` — константа.
· **⛔ `tick.py --window all` — НЕ окно, а МОЛЧАЛИВОЕ обнуление**: таблица `windows` = только `w1`/`w2`,
`all` не матчит ничего и экран уезжает `positions 1113 → 0` без ошибки. Гони `make tick` (дефолт `w2`,
окно ruling 02.09 (d)). · **⛔ `promo-dev-loop` ОТКАЗЫВАЕТ.**
**⛔ БЛОК РАНБУКА БЕРЁТСЯ ПО СВОЕЙ ПЕРВОЙ/ПОСЛЕДНЕЙ СТРОКЕ, НЕ по номеру фенса** — в s41 он указал на **§2** и выполнил `template create` (создан, удалён, $0). **⚠️ zsh НЕ разбивает `$SSHO` · ⚠️ НЕТ `timeout` на macOS · ⚠️ НЕТ `setsid` на macOS (локально —
`nohup`; «ТОЛЬКО setsid» = правило УДАЛЁННОГО раннера) · ⚠️ живость по PID · ⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ ·
⛔ `1925810730` · ⛔ `aggregates.py` и `open`**.
## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list -a` показывает только running, смотри `pod list -a`.
