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
**Last update:** 2026-09-06 12:55 (s31; ПЛАТНАЯ итерация 5 — **GREEN**). Этап 1 `SPEC-v2`,
карта `STATUS.md`, цикл v3, фаза **v14**, процесс **Money v2.1**. Руками, ≤40 строк.

## 🔥 What's Hot
**S2 ОТВЕЧЕН зелёным на ПЯТОЙ и последней прогонке (§2).** `--arm dev40` (БАР): **subject 0.8857 ≥
0.80 · signal 0.8667 ≥ 0.75**, 40/40 юнитов, **0 unparsed**; `--arm dev2` (ЧТЕНИЕ) 0.8883/0.8296.
**Рулинг (w) отвечен и это был СЕРВИНГ:** инструмент не двигался, а рендер 14 281 симв.
(`@VARUS_channel:8647`), убивший итерацию 4 по OOM, вернулся за **313.9 с** на 32 ГБ карте с
`expandable_segments:True`. Под `xt4c5osyr36ew0` 11:20:39Z→12:38:57Z = 4698 с = **$0.9396 из $1.40**.
**Цикл-3 SPENT $7.3933 / REMAINING $1.6067 из $9.00** (чтение 12:39Z; это БАЛАНСОВАЯ дельта, она уже
несёт этот прогон — биллинг проставил лишь $0.2156). Новая целопрогонная скорость для следующей
ноги: **53.6254 с/тред (max 313.867, n=80)**. `make check` **4323/2** на ОБОИХ HEAD, ruff чист.
**Дрейф (y) сработал в нашу пользу:** якорь 11:06Z → пост-рановый `--note` 12:39Z = H 1.55 ч →
капель тома **1.29 %**, глубоко внутри полосы 5 % (у итерации 4 все её 2.73 % были этим членом).

## ⏭️ Next — стартовый ритуал, потом ход ТИМЛИДА. Открытых стопов ДВА (см. PROGRESS)
**1. Линия `promo-iter5` НЕ ЗАКРЫТА и это ЗАДЕРЖКА, а не решение.** `--close` ОТКАЗАЛ: обход
покрыл **1 072 748 мс из 4 698 000**, частичный обход — третье состояние. Биллинг проставляется
на 30–40 мин позже. Повторять в стартовом ритуале КАЖДОЙ сессии, дословно:
`--close --tolerance 0.05 --expect-ms 4698000 --until '2026-09-06T12:45:00Z'` (`--until` бьёт по
ОКНУ ПОТРЕБЛЕНИЯ, не по времени проводки, поэтому те же границы однажды сойдутся).
**2. GREEN ⇒ пора за holdout-2, и исполнитель НЕ начинает его сам:** тимлид тянет эталон ВСЛЕПУЮ из
популяции ПРОДУКТА (каналы r2), а PHASE §6.2 делает саму попытку СТОП-уведомлением оператору.
$0.90 из §6.1 — ЗАБОР, а не кап: перецена на своём `--register` по 53.6254 с/тред и цене дня.
Запас после двух заборов ($0.90 + $0.50) = **$0.21** до капели тома — тонко.

## 🚧 Blockers / долги (названы, не построены)
**⛔ `promo-dev-loop` ОТКАЗЫВАЕТ: $2.5799 из своих $2.50, exit 1**, закрыть нельзя ((r)4) — **больше
никогда не называется**; кап брать ИЗ ЛЕДЖЕРА, не с руки. · **(y)4 риск 3 СРАБОТАЛ как предсказано:**
`--close-segment` напечатал `verdict OVER`, `spent_all_segments_usd 2.874083` — просуммировал ВСЕ
СЕМЬ сегментов с итерации 1 против капа этой линии; ложное поле, деньги в линии гарда ($0.9495).
Фильтр по `anchored_at`. · **(y)4 риск 2: исключение с ПУСТЫМ текстом читается как ОТВЕЧЕНО** —
фикс `"exception" in row` + тест (w)3. **Оба — ПЕРВЫЕ $0-пункты этой сессии.**
· **`prereg_promo_holdout.json` ЗАПЕЧАТАН под старой sha раннера.** · сюита ~12 мин, 229 файлов.
**⚠️ ТОЛЬКО ОТЦЕПЛЁННЫМ (`os.setsid`) · ⚠️ `pgrep -f <script>.py` ЛОВИТ И СВОЙ ЖЕ ЗОНД — живость
брать по PID · ⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ · ⛔ `1925810730` · ⛔ `aggregates.py` и `open`**.
## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list -a` показывает только running, смотри `pod list -a`.
