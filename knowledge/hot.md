<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-04 13:03:06 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
cc7b855 docs(progress): the verifier's own number — `make check` 4319 passed / 2 skipped
a64062a docs(progress): both reds named — the predicted one and the layering invariant I broke
3f75106 fix(aggregates): the layer is handed the chain spellings, it does not open the file
ad739f5 docs(progress): the runbook's K8 `--out` is the same hazard as `--score` without `--suffix`
b0a11ec docs(progress): A-rest done and no open stop — the cap fell to $2.4469 and B has $1.9215
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
**Last update:** 2026-09-04 13:00 (чекпоинт с13 — «A-rest» ПРИНЯТ рулингом (k); следующее — «sources-r3: Маркетопт», потом платная B). Этап 1 `SPEC-v2-promo-pulse.md`, карта `STATUS.md`, цикл `PROCESS.md` v3. Руками, ≤40 строк.

## 🔥 What's Hot
**✅ `promo-pulse-1` — «A-rest» ПРИНЯТ ЦЕЛИКОМ, рулинг 04.09 (k)** (`c2234a4` · `d64faf7` ·
`3f75106`; PROGRESS — `cc7b855`). `make check` **4 319 passed / 2 skipped**. Открытого стопа НЕТ.
Итерация 1 под v1.1 + свёрткой = **115/140 = 0.8214** ($0-чтение), signal **0.8792** ✅. Закон v1.2
(`a587e0d6…`), `template_sha256 57dd9d25…`, регистрация переиздана под пины v1.1.
**(k) и (j) лежат в дереве НЕ закоммиченными** — коммитит по путям ритуал следующей сессии.

**💰 ДВЕ ЦИФРЫ УПАЛИ, обе подтверждены (k)3.** Кап шага **$2.50 → $2.4469** (переиздание пересчитало
`min($2.50, REMAINING − $0.30)`), REMAINING цикла **$3.3305 → $2.7469** — сутки всегда-включённого
тома, не ран. **У B остаётся $1.9215, а НЕ $1.9746 из (h)4.** Цикл 3: **$4.2531 из $7.00**;
сессии 10–13 = **$0**.

**⏸️ ЗАКОН И КОДБУК-ДОКУМЕНТ НЕ ТРОГАТЬ до заморозки ((k)2).** Near-quote «Шикарно. Цілий день тиша,
а потім скидка» остаётся, `docs/CODEBOOK-promo-signals.md` остаётся с 11 дословными цитатами:
двигать закон сейчас = переиздавать пак ради косметики. Обе правки — ОДНИМ движением на заморозке
перед прережкой холдаута.

**⚠️ Долги, которые кусают именно B:** `--score` БЕЗ `--suffix` и `runbook_promo_dev_1.md:162`
(`--out`) целятся в ПЛАТНЫЕ `…_iter1.*` — раннбук B обязан перенаправить их на `*_iter2.*`.
`committed_registration()` по-прежнему не переверяет `pinned_inputs`.
**⛔ `aggregates.py` НЕ ИМЕЕТ ПРАВА открывать путь** — `test_the_layer_reads_nothing_and_parses_nothing`
парсит его AST; конфиг читает `registry.chain_spellings()`.
[[a_module_can_have_a_test_about_what_it_may_not_do]]

## ⏭️ Next / 🚧 Blockers
**Следующий пункт — «sources-r3: Маркетопт» (рулинг (i)), ДО платной B:** вступить в
`marketopt_private` (`+Ejz6ubzm21IyMTQy`, строка реестра есть), сбор ($0), ценз, страницы под
`results/prereg_promo_c3.json` **кап $0.50**, ТРЕТЬЕ окно, `make tick` дважды, `make promo-screen`
рядом с w2. `@ON_LINE_MO` — боковым файлом, если ценз покажет цены. Потом B: `*_iter2.*`, **≤ $1.9215**.
**⚠️ ДЛИННЫЙ ПРОГОН — ТОЛЬКО ОТЦЕПЛЁННЫМ** (`os.setsid` в форке): фоновые задачи харнеса убивались
на 26 %, и `make check` умирал вместе с ними. · **⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ** (`:366/:171/:153`) ·
**⛔ `1925810730` и инвайт-хэш неадресуемы** · **⚠️ фикстура в стор патчит ВСЕ derived-корни** ·
**⚠️ `volume_calc_5c1.py` НЕ ЗАПУСКАТЬ просто так.**

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list` показывает только running, смотри `pod list -a`.
