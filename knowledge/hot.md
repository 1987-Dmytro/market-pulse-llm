<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-14 15:05:57 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
7c207f1 brain(s63): the cache points at «e2e-ship», not at a phase two items back
9d53ab5 docs(progress): the six joined files are TRACKED, and four more things named not built
86ffebb docs(progress): s63 «reactions-region» — the two tabs, and what the month really is
1f3e100 fix(reactions-region): ten defects my own adversarial review of this diff caught
7ff8c26 fix(reactions-region): §13 (5) says CHIPS with counts, and a select is not one
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `the-price-block-is-cut-per-unit-and-the-region-is-a-chain-list.md` — The price block is cut per UNIT, and the region block is a list of CHAINS
- `a-published-number-has-one-reader.md` — A published number has ONE reader, and a missing source is a refusal by name

## 📅 Recent daily logs

- `2026-09-14.md`
- `2026-09-13.md`
- `2026-09-12.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->

# Hot Cache — curated
**Last update:** 2026-09-14 s63 «reactions-region»: 8 коммитов, vitest 37/37, 4348/2, $0; у меня стопов НЕТ.
Этап 1 `SPEC-v2`, карта `STATUS.md`, цикл v3, фаза **ship-1**, процесс **Money v2.6**. Руками, ≤40 строк.

## 🔥 What's Hot — приложение отвечает на вопрос директора по маркетингу
**14.09 ((hhh)):** s63 закрыл **«reactions-region»**, все четыре клаузулы. Реакції перерисована по §13,
**Промо · Регіон** — новая вкладка (`#/promo/region`), у которой ЧЕСТНЫЙ НОЛЬ — это предложение продюсера,
а не пустой экран. `collect_region.py` пишет `results/region_collect_report.json` на ЛЮБОМ режиме, `--plan`
включительно (**3 700 / 1 008 / 2 692**, `8cf7563b…` одинаково из трёх запусков, $0). **Даты и тексты — из
закоммиченных `promo_threads_draw*.json` и `promo_*_pack.json`, НЕ из `data/raw/`** (gitignored → клон
собрал бы другое); все шесть файлов git несёт, но в `required()` они ГЛОБЫ, а глоб не умеет отказать по
имени. Свой ревью диффа (6 линз → 42 находки → по 3 скептика) дал **10 починок**, одна сняла нарушение
§12: месячный график был **ДВОЙНОЙ ОСЬЮ**. **Правило дня: перевёрнутый заголовок проходит три `toContain`
— держи ПОРЯДОК слов, а не их наличие.**

## ⏭️ Next — «e2e-ship» ($0): фаза закрывается на ЧИСТОМ КЛОНЕ
`git clone <repo> /tmp/mp-e2e`, затем `make check && make front && make tick && make promo-screen` — зелено
(клон без стора говорит это и выходит 0); переименованный источник → `make front` падает ≠ 0 ПО ИМЕНИ;
`make serve` smoke, `draw_truth_20.py`, `make session`, `firebase.json` + `.firebaserc.example` есть и НЕ
деплоятся, README как первая страница со скриншотами, `docs/reports/ship-1.md` ≤30 строк, порцелан пуст.
Далее **linkedin-pack** (тимлид) → ГЕЙТ ср 16.09 вечером.

## 🚧 Blockers / долги (названы, не построены)
**Файлы тимлида — только Read-tool; харнес-файл — только Write-tool, `diff` = пруф.**
**Деньги: $0 14.09, подов и ТОМОВ нет, дрипа нет.** Гард печатал `REMAINING $1.1602` (09.09) — с тех пор
не тратилось. **Названо и НЕ починено (вне плана):** у приложения НЕТ error boundary — `must()` внутри
рендера вкладки размонтирует корень вместо красной панели §5 (нашлось в s59, чинить не просили; (ddd) 3 —
POST-GATE); вторая популяция только у NSR; `SovReading.share` типизирована `number`, хотя продюсер
может писать null; `report()` над пустым стором пишет восемнадцать НУЛЕЙ, и экран печатает их как замер.
· **⛔ `tick.py --window all` — не окно, а МОЛЧАЛИВОЕ обнуление** (`positions 1113 → 0`); гони `make tick`.
· **⛔ `promo-dev-loop` ОТКАЗЫВАЕТ.** · **⛔ БЛОК РАНБУКА — ПО СВОЕЙ ПЕРВОЙ/ПОСЛЕДНЕЙ СТРОКЕ, НЕ по фенсу.**
· **⚠️ `pgrep -f "pytest -q"` матчит СВОЙ ЖЕ шелл-ожидатель** — петля не выходит; матчи по `bin/pytest`.
· **⚠️ zsh НЕ разбивает `$SSHO` · НЕТ `timeout`/`setsid` на macOS · живость по PID · K4 НЕ ПЕРЕЗАПУСКАТЬ · ⛔ `1925810730` · ⛔ `aggregates.py` и `open` · ⛔ `make fmt` двигает запечатанные sha.**
## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list -a` показывает только running, смотри `pod list -a`.
