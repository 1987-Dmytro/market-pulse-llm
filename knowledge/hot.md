<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-14 12:17:04 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
117e10b docs(progress): run the write paths the fixes changed, and reconcile the test count
6a9cac7 docs(progress): s62 «region-collect» — the registry never moved and the zero is honest
e608f56 data(region-collect iii): the stage-2 regional baseline is an honest, printed ZERO
9d102a3 fix(region-collect): five defects my own adversarial review of this diff caught
40c1087 feat(region-collect ii+iii): a regional collector and a $0 sentinel, both one-reader
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
**Last update:** 2026-09-13 s60 «weekly-home»: 7 коммитов, vitest 31/31, 4344/2, $0; у меня стопов НЕТ.
Этап 1 `SPEC-v2`, карта `STATUS.md`, цикл v3, фаза **ship-1**, процесс **Money v2.6**. Руками, ≤40 строк.

## 🔥 What's Hot — приложение отвечает на вопрос директора по маркетингу
**13.09 ((ddd)+(eee)):** `front-2` ПРИНЯТ; s60 закрыл **«weekly-home»**, обе клаузулы. (1) 10 недель
W27–W36 (**1 301 строка**) — в **`results/weekly/`**, который git несёт: один коммит by path, `cmp` 10/10
против принятого набора. **Принятый дайджест `72d9d46e…` = `shasum <пути> | shasum`: он хеширует ПУТИ,
законный переезд его двигает (`b636e842…`); держится контентный `cat …` = `d4fb6a44…`.** (2) T4 «Δ до
свого» — ПОЛЕ `command_center_derived`, приложение не вычитает; доля эталона 0.0000, поэтому Δ численно
равна доле — тест краснеет только от мутации ССЫЛКИ (`max(share)`). Свой ревью диффа (5 линз → 10 находок
→ по 3 скептика, выжило 0) принёс 3 починки МОЕГО текста: обещание восстановимости на клоне в
`DATASETS.md` (реально 15 из 28 колонок), несуществующий `aggregates.sov_block` в докстринге, тест
сравнивал блок сам с собой. **Правило дня: единогласный отказ 30 из 30 — тоже показание, не приговор.**

## ⏭️ Next — «region-collect» ($0, (eee)): ЕДИНСТВЕННЫЙ разрешённый ход реестра
НАПЕЧАТАТЬ каналы, чья пауза ссылается на «phase B (рулинг (ц) 30.08)» (ждём 17 районных), снять паузу
ТОЛЬКО с них, дифф построчно — §4.1: слово оператора дано, это НЕ стоп. Потом `collect_r2.py` (посты И
комментарии в `data/raw_r2/`), потом НОВЫЙ `region_sentinel.py` ($0, БЕЗ модели) → `region_mentions.jsonl`
+ `region_baseline.json` (ноль — число). Далее **reactions-region** → **e2e-ship** → ГЕЙТ 16.09 вечером.

## 🚧 Blockers / долги (названы, не построены)
**Файлы тимлида — только Read-tool; харнес-файл — только Write-tool, `diff` = пруф.**
**Деньги: $0 13.09, подов и ТОМОВ нет, дрипа нет.** Гард печатал `REMAINING $1.1602` (09.09) — с тех пор
не тратилось. Незакоммичено и не моё: `knowledge/runbooks/network-wifi-flap.md` (12.09, читать CORRECTION).
**Названо и НЕ починено (вне плана):** у приложения НЕТ error boundary — `must()` внутри рендера
вкладки размонтирует корень вместо красной панели §5 (нашлось в s59, чинить не просили; (ddd) 3 —
POST-GATE); вторая популяция только у NSR; `SovReading.share` типизирована `number`, хотя продюсер
может писать null — окно с нулём упоминаний умрёт на колонке доли раньше Δ.
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
