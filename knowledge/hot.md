<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-09 20:40:28 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
eaee5d2 docs(team-lead): ruling 09.09 (kk) — s42 «c3» ACCEPTED as a COMPLETE paid leg ($0.2577 of $0.80, 30 pages + 8 posts) on my own runs; the OPEN STOP is a FALSE band refusal (5% relative tolerance cannot grade a $0.23 leg — a late-posting $0.0305 kind is 13.4%); ruling: an ABSOLUTE floor beside the band (DOLLAR_FLOOR $0.05, the MS-floor pattern) → «kk-close» ($0) adds it + a two-way test, closes $0.2577, deletes the volume; PHASE v27, stop-patterns §6
6ae9fcb docs(progress): s42's OPEN STOP — §5 refuses on the BAND, settled $0.257668 vs a recorded $0.227200, 13.4% off a 5.0% tolerance; the reference missed a whole billed kind
1ec4e27 docs(progress): s42's PROGRESS lands inside its 60-line cap
fef6e0b docs(progress): the band refusal is labelled a FORECAST off a LOWER BOUND, not a measurement, and the constraint is named — a 5% relative band cannot grade a $0.23 leg
9095d39 docs(progress): s42 — «c3» BOUGHT at $0.2272 of the $0.80 cap, record complete; §5 refused on the WALK three times (no billing rows), the line stays OPEN
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `a-published-number-has-one-reader.md` — A published number has ONE reader, and a missing source is a refusal by name
- `the-registration-opens-the-line.md` — The registration OPENS its line, so §0a lives in the PAID session

## 📅 Recent daily logs

- `2026-09-09.md`
- `2026-09-08.md`
- `2026-09-06.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->

# Hot Cache — curated
**Last update:** 2026-09-09 s41 «c3-prep-4»: ранбук ОТРЕПЕТИРОВАН вызов за вызовом, $0; стопов НЕТ.
Этап 1 `SPEC-v2`, карта `STATUS.md`, цикл v3, фаза **v25**, процесс **Money v2.6**. Руками, ≤40 строк.

## 🔥 What's Hot — нога c3 готова к ПОКУПКЕ по кап $0.80 (слово оператора, (hh)3)
**Отгружаемое (петля хуки + P1, `grade_promo_loop_readings.json`):** dev-3 **0.7411 (83/112) ❌ 0.80**
· сигналы **0.7937 ✅ 0.75**; dev-40 0.8857 / 0.8667, dev-2 0.9043 / 0.8296 — одинаковы обоими путями.
Чтения рядом как «reading» (0.7500 / 0.8021, сырьё 0.7054, holdout-40 0.7181), НЕ переписываются; ничьи dev-3 — **16 из 28**; holdout-3 — РЕЗЕРВ. **c3 за $0:** якорь 2026-09-05, 29 медиапостов,
**30 страниц ТОЧНО**, 30/30 на диске; dry run 30 стр. + 8 постов, `pagecount: match`, дорогой угол
**$0.1864** против капа **$0.80** — **ВЛЕЗАЕТ (−76.7%)**; кап $0.80 И ЕСТЬ починка in-run pack gate
(s39 читал NOT SAFE при $0.50), код денег НЕ трогали. Ранбук: §0 = ключ API → штамп → поля v2.6 → **КАП КОМАНДОЙ**
(min($0.80, REMAINING − $0.30), вниз до цента, пол $0.15 → exit 1), §1 — ХВОСТ того же вызова,
**§3 — ОДИН вызов: свой `export RUNPOD_API_KEY` (из §0 он НЕ доезжает) + кап из регистрации +
`{ nohup … & echo $! > pid; }` в ФИГУРНЫХ скобках** (без них `$!` — pid сабшелла), полл по
`-o args=` (НЕ `comm=`), НЕ `| tee`; **§5 — БЕЗ `--expect-ms`** (walk считает uptime воркера, а не
wall записи; у C2 в записи `expected_ms: null`), `--until` = часы, `--tolerance 0.05`; пост-ран
`--note` уехал В §4 сразу после листингов, **том удаляется ПОСЛЕ закрытия**.

## ⏭️ Next — ТРЕТИЙ проход верификатора (§3/§5 + `cap_from`) → чтение тимлида → «c3» (платно)
Кап c3 = min($0.80, REMAINING − $0.30) — **берётся гардом В ТОЙ сессии**, не отсюда. §0 → §5.
Дальше: «chain-fold» ($0, форма (b), (gg)2 — P1 перемеряется функциями продукта) → e2e на чистом клоне + `draw_truth_20` → гейт **12.09**.

## 🚧 Blockers / долги (названы, не построены)
**Файлы тимлида — только Read-tool; харнес-файл — только Write-tool, `diff` = пруф.**
**⚠️ `promo_projection_c2.json` НЕ ВОСПРОИЗВОДИМ производителем** (живое чтение гарда + растущий
ledger внутри sha-закреплённой записи): пруф такой записи — её пин, не перепрогон.
**Деньги: гард печатает `REMAINING $1.4470`** (том пьёт ≈$0.24/day); запас над капом $0.6470.
`make check` **4326/2** на `c9cc937` (весь прогон целиком, 12:37); HEAD `ba1d94b`, подов НЕТ,
$0 за сессию. · K12 читает настоящий `results/`, `tick.REGISTRY` — константа.
· `tick.py --window` дефолт `w2` — ранбук несёт `--window all`. · **⛔ `promo-dev-loop` ОТКАЗЫВАЕТ.**
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
