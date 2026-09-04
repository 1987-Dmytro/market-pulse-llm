<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-04 12:02:04 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
d002967 docs(progress): the stop before A-rest's first edit — the registry carries no chain aliases
1590ab8 knowledge: session 11's artifacts and the PROGRESS next-line under ruling (h)
ec1b55a docs(lead): rulings 04.09 (h) and (i) — A(1) accepted, A(2)–A(5) are one item, Маркетопт collected before B
be6a35e docs(progress): the rebuild proved against iteration 1's own pack, inside the 60-line cap
b4f1700 knowledge(hot): the curated block says A(1) is BUILT — it is injected before PROGRESS is read
```

## 📋 Recent decisions

- `the-sealed-file-does-not-grow-it-gets-a-sibling.md` — A file 21 seals pin does not grow — the new key gets a sibling file (ruling 04.09 (g), option b)
- `INDEX.md` — Decision records
- `terminate-after-is-the-cap-less-what-the-step-spent.md` — `--terminate-after` is derived from the cap LESS what the step already spent

## 📅 Recent daily logs

- `2026-09-04.md`
- `2026-09-03.md`
- `2026-09-02.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->
# Hot Cache — curated
**Last update:** 2026-09-04 (с13 — «A-rest» СДЕЛАН целиком за $0; следующее — «sources-r3: Маркетопт», потом платная B). Этап 1 `SPEC-v2-promo-pulse.md`, карта `STATUS.md`, цикл `PROCESS.md` v3. Руками, ≤40 строк.

## 🔥 What's Hot
**✅ `promo-pulse-1` — «A-rest» ЗАКРЫТ** (`1ae3c40` рулинги по путям · `c2234a4` код+регистрация ·
`d64faf7` пак). Итерация 1 под v1.1 + свёрткой = **115/140 = 0.8214**, signal **0.8792** ✅.
Открытого стопа НЕТ. Всё, что ниже, — состояние ПОСЛЕ A-rest.

**💰 ДВЕ ЦИФРЫ ИЗМЕНИЛИСЬ, обе вниз.** Кап шага `promo-dev-loop` **$2.50 → $2.4469** (переиздание
пересчитало `min($2.50, REMAINING − $0.30)`), REMAINING цикла **$3.3305 → $2.7469** — это сутки
всегда-включённого тома, не ран. **У B остаётся $1.9215, а НЕ $1.9746 из рулинга (h)4** —
`--terminate-after` выводится из этого. Цикл 3: **$4.2531 из $7.00**; сессии 10–13 = **$0**.

**🧪 Закон теперь v1.2.** `codebook_version a587e0d6…`, `template_sha256 57dd9d25…` (новое поле
регистрации, (g)3). 11 дословных dev-комментов ушли из `promo_prompts.CODEBOOK` — пары старое→новое
лежат в PROGRESS. Чек живой: `promo_dev_pass.py --leak-check` → `results/promo_law_leak_check.json`,
берёт строки ИЗ модуля, 27+8 литералов × 328 комментов (dev+холдаут) → **CLEAN**.
**Два примера тимлида из (j)3 заменены**, потому что не проходят его же чек: «Ну да» — это холдаут
`@VARUS_channel:8647:15419`, «+1» — внутри dev'ского «по акції 1+1». Откат — одна строка.

**🔧 Свёртка сети:** `config/chain_aliases.yaml` → `aggregates.chain_key` (единственный читатель);
`subject_id` и грейдер сводят ТОЛЬКО `chain`. Одно написание на два id — отказ. +1 строка, названа:
`@VARUS_channel:6216:8865`. KFC / Roshen / Велмарт / Mono НЕ внесены — их написания пришлось бы
брать из экзамена. [[measure_what_the_normalisation_would_fix]]

**⚠️ `promo_dev40_prep.json` был протухшим с A(1)** — мерил рендер с бессловесными комментами.
После перегенерации короткий дымовой юнит: `@msuaaaa:6523` → **`@msuaaaa:7187`**. Пины регистрации
теперь v1.1 (`2303ea43…` / `23610346…`) — старый разрыв закрыт; `pinned_inputs` по-прежнему никто
не переверяет. [[a_fixture_on_disk_pins_yesterdays_schema]]

## ⏭️ Next / 🚧 Blockers
**Следующий пункт — «sources-r3: Маркетопт» (рулинг (i)), ДО платной B:** вступить в
`marketopt_private` (`+Ejz6ubzm21IyMTQy`, строка реестра есть), сбор ($0), ценз, страницы под
`results/prereg_promo_c3.json` **кап $0.50**, ТРЕТЬЕ окно, `make tick` дважды, `make promo-screen`
рядом с w2. `@ON_LINE_MO` — через боковой файл, если ценз покажет цены. Потом B: `*_iter2.*`,
**≤ $1.9215**. Параллельно за $0: позиции тимлидом ПО СТРАНИЦАМ (46).
**⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ** (`:366/:171/:153`) · **⛔ `1925810730` и инвайт-хэш неадресуемы** ·
**⚠️ платный ран отцеплённым (`setsid`), Dv904** · **⚠️ фикстура в стор патчит ВСЕ derived-корни** ·
**⚠️ `volume_calc_5c1.py` НЕ ЗАПУСКАТЬ просто так.**

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list` показывает только running, смотри `pod list -a`.
