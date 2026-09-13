<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-13 18:24:00 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
1a3e0e5 front(front-2): the command centre stops being a placeholder — nine tabs over one block
0a6eba7 docs(progress): s57 «data-shape» — the store is rebuilt, the week leaves with the tick, 4344/2
5c9f766 docs(datasets): drop a durability claim I did not measure, and say what the gitignore costs
24e6e07 docs(datasets): the layer map for the operator's future models — 66 lines
a954cac test(data-shape): the three checks the item names, each shown red by its own mutation
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `the-price-block-is-cut-per-unit-and-the-region-is-a-chain-list.md` — The price block is cut per UNIT, and the region block is a list of CHAINS
- `a-published-number-has-one-reader.md` — A published number has ONE reader, and a missing source is a refusal by name

## 📅 Recent daily logs

- `2026-09-13.md`
- `2026-09-12.md`
- `2026-09-10.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->

# Hot Cache — curated
**Last update:** 2026-09-13 s59 «front-2-close»: 3 коммита, vitest 30/30, $0; у меня стопов НЕТ.
Этап 1 `SPEC-v2`, карта `STATUS.md`, цикл v3, фаза **ship-1**, процесс **Money v2.6**. Руками, ≤40 строк.

## 🔥 What's Hot — приложение отвечает на вопрос директора по маркетингу
**13.09 (рулинг (ccc)):** батч s56–s58 разобран тимлидом — `insight-1` и `data-shape` ПРИНЯТЫ, а
`front-2` остался открытым: код девяти вкладок стоял в `1a3e0e5`, но сессия умерла на ритуале.
s59 закрыл его ПО ЕГО ЖЕ ЧЕКАМ и нашёл **два числа, которых нет ни в одном файле**: T5 печатал
«73.1 %» = 106 ÷ 145, поделённое в браузере, под провенансом блока, где доли нет вообще
(`promo_pressure.share` считается по БРЕНДУ) — теперь это **количество** `position_rows` (atb 106);
и T8 печатал «рішення [object Object]» — `decision` это блок из 10 ключей, теперь печатается
выбранная ветка **without-plast**. Каждый фикс показан КРАСНЫМ своей мутацией. Экспорт не двигался:
`dcef7ec5…`, запечатанный `e45860c6…`, `results/` чистый. **Правило дня: батч отложил не работу, а
приёмку — «нужен рулинг» в отчёте заканчивает ход.**

## ⏭️ Next — «weekly-home» ($0, рулинг (ccc) 4): недельные файлы в КОММИТИМЫЙ `results/weekly/`
Сегодняшние 10 недель (W27–W36) восстановимы на чистом клоне, будущая — НЕТ; истории для ML
оператора нужно пережить клон. Та же идемпотентность показывается заново; `DATASETS.md` — строка
тимлида. Потом **e2e-ship** (чистый клон) → ГЕЙТ среда 16.09 вечером.

## 🚧 Blockers / долги (названы, не построены)
**Файлы тимлида — только Read-tool; харнес-файл — только Write-tool, `diff` = пруф.**
**Деньги: $0 13.09, подов и ТОМОВ нет, дрипа нет.** Гард печатал `REMAINING $1.1602` (09.09) — с тех пор
не тратилось и не перемерялось. Незакоммичено и не моё:
`knowledge/runbooks/network-wifi-flap.md` (Wi-Fi разбор 12.09; читать секцию CORRECTION до чисел).
**Названо и НЕ починено (вне плана):** у приложения НЕТ error boundary — `must()` внутри рендера
вкладки размонтирует корень вместо красной панели §5 (нашлось в s59, чинить не просили); вторая
популяция на экране только у NSR; T4 «Δ до свого» — вычитание в браузере, которое ЗАКАЗАЛ бриф §7.
· **⛔ `tick.py --window all` — не окно, а МОЛЧАЛИВОЕ обнуление** (`positions 1113 → 0`); гони `make tick`.
· **⛔ `promo-dev-loop` ОТКАЗЫВАЕТ.** · **⛔ БЛОК РАНБУКА — ПО СВОЕЙ ПЕРВОЙ/ПОСЛЕДНЕЙ СТРОКЕ, НЕ по фенсу.**
· **⚠️ `pgrep -f "pytest -q"` матчит СВОЙ ЖЕ шелл-ожидатель** — петля не выходит; матчи по `bin/pytest`.
· **⚠️ zsh НЕ разбивает `$SSHO` · НЕТ `timeout`/`setsid` на macOS · живость по PID · K4 НЕ ПЕРЕЗАПУСКАТЬ
· ⛔ `1925810730` · ⛔ `aggregates.py` и `open` · ⛔ `make fmt` двигает запечатанные sha.**
## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list -a` показывает только running, смотри `pod list -a`.
