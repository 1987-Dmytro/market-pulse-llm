<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-06 16:04:01 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
4b3c649 knowledge(hot): s31 — the cache said promo-iter5 must NOT be anchored, and it is closed green
d2bbba3 docs(progress): REMAINING is the BALANCE delta and already carries this run — the headroom is $0.21, not "enough"
1f60bf0 knowledge: s31's day — the paid iteration 5 came back green
811a7c3 docs(progress): s31 trimmed to the 60-line cap — lines deleted, not reflowed
0bba811 docs(progress): s31 — iteration 5 is GREEN, and the open stop is the holdout-2 blind draw
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
**Last update:** 2026-09-06 (s32, $0: «holdout-2 prep» ЗАКРЫТ на committed dry run; эталон holdout-2 ЕСТЬ). Этап 1
`SPEC-v2`, карта `STATUS.md`, цикл v3, фаза **v16**, процесс **Money v2.1**. Руками, ≤40 строк.

## 🔥 What's Hot
**S2 зелёный на dev-40 (итерация 5, (z)): subject 0.8857 · signal 0.8667, 80/80.** Инструмент ЗАМОРОЖЕН как куплен —
четыре пина `d598573`; пин, сдвинувшийся до выстрела, — СТОП (ранбук §0a сравнивает их КОМАНДОЙ, прогнана: HOLD).
**Эталон holdout-2 ЕСТЬ и закоммичен по пути:** `docs/labels-promo-holdout2.jsonl`, 112 строк / 40 тредов, sha
`5525ddf1…` ((z) addendum 2, PHASE v16 §2). **`promo-iter5` ЗАКРЫТА $0.9450** (0.47 % от $0.9495). **Потолок цикла-3
$10.00** ((z) addendum): **SPENT $7.4179 / REMAINING $2.5821** (14:21Z). Над двумя заборами ($0.90 + $0.50) = **$1.18**.
**`--part holdout2` в эмиттере:** draw-2, свой эталон, линия `promo-holdout2`, файлы `promo_holdout2_*`; `by_part`
пишет каждое решающее поле записи ПО ИМЕНИ ноги и отказывает ноге без текста (§4 v8); без `--cap` — отказ ДО гарда.
**Две починки (y)4:** `died(row)` = `"exception" in row` во всех пяти читателях; `close_segment` суммирует сегменты
ОТ ЯКОРЯ линии (`line_anchor` из леджера, который называет запись) — ложное `OVER` итерации 5 не повторится.
**Dry-run holdout-2:** 40 тредов, самый длинный рендер 10 529 симв. (< 14 281), темп **53.6254 с/тред (n=80)**; rung 0
read-only на $0.72/ч, кап $0.90: **mean $0.5170 · dear $2.8109 → FITS на mean, hard stop 4500 с = 75 мин** — цифра
СТОП-уведомления §6.2. `make check` **4323/2** на `d4bc013`, ruff чист; §8 (l) пуст.

## ⏭️ Next — свежий верификатор → чтение тимлида (prep + HEAD) → ПЛАТНЫЙ выстрел «holdout-2»
Ранбук §0a ВНУТРИ платной сессии: `--register --part holdout2 --step promo-holdout2 --cap 0.90` (FITS, пины) → коммит →
`--pack --part holdout2` → коммит → срезы → §0–§7 → `--score --part holdout2`. Уведомление оператору §6.2 — ДО
открытия сессии. Потом c3 ($0.50), потом удалить том `mp-srv2` ((z)5). **Открытых стопов у исполнителя НЕТ.**

## 🚧 Blockers / долги (названы, не построены)
**⛔ `promo-dev-loop` ОТКАЗЫВАЕТ** (над своими $2.50 с 05.09), закрыть нельзя ((r)4) — **никогда не называется**.
· **`--step promo-holdout2` БЕЗ `--part holdout2` = dev-нога под линией holdout-2** — отказ на чужой `--step` НЕ
построен (~3 строки, не просили); `--part holdout2` — несущий флаг, пишется всегда. · наивный `--created-at` без `Z` →
TypeError на `--close-segment` (недостижимо: все штампы с `Z`). · `prereg_promo_holdout.json` ЗАПЕЧАТАН под старой
sha раннера. · сюита ~12 мин, 229 файлов — только срезами; тесты ГРЕПАЮТ `hot.md`/PROGRESS — не править, пока идут.
**⚠️ ТОЛЬКО ОТЦЕПЛЁННЫМ (`os.setsid`) · ⚠️ живость по PID, `pgrep -f` ловит и свой зонд · ⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ ·
⛔ `1925810730` · ⛔ `aggregates.py` и `open`**.
## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list -a` показывает только running, смотри `pod list -a`.
