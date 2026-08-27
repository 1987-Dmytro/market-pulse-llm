<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-08-27 16:09:40 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
e11c9a9 docs(retail-census): make check 2/4099, the registry block located, the vault caught up
9fa2ff4 feat(retail-census): the census — 410 found, 200 measured, FloodWait at 191 with everything kept
3c7904f feat(retail-census): the report renderer, the dead-channel rule, and an offline re-grade
acb70dd feat(retail-census): per-theme bars, one sort per instrument, and the deviations
0318243 feat(retail-census): the two themes, and a census that spends one history request a candidate
```

## 📋 Recent decisions

- `lora-c-the-line-trains-at-90-seconds-a-step.md` — The line trains at 89.961 s/step — and the gate that would have hidden it
- `INDEX.md` — Decision records
- `lora-c-the-volume-moves-to-ca-mtl-3.md` — The training line's volume moves to CA-MTL-3 — and the cheaper cards arrived 107 minutes late

## 📅 Recent daily logs

- `2026-08-27.md`
- `2026-08-26.md`
- `2026-08-25.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->
# Hot Cache — curated

**Last update:** 2026-08-27 — этап 1 = `docs/SPEC-v2-promo-pulse.md`. Карта и деньги —
`docs/STATUS.md`; цикл фазы — `docs/PROCESS.md` v2.1: `/plan-phase` → «go» → `/report`. Блок
курируется руками, **≤40 строк**: у археологии есть дом — отчёты, ADR, логи дня.

## 🔥 What's Hot
**⛔ АККАУНТ TELEGRAM ЗАПЕРТ ДО 2026-08-28 10:21 UTC.** FloodWait 85 352 с записан в
`results/joins_5c1.jsonl` строкой `(census)`; лимит на `ResolveUsernameRequest` — начале КАЖДОГО
входа и выборки комментов, — и повтор внутри окна его удлиняет. `retail_census.py` и
`collect_5c1.py` отказываются стартовать сами ([[rate_limit_on_the_shared_first_step]]).

**🧾 C1 ИСПОЛНЕН, ТАБЛИЦА НЕПОЛНАЯ — 200 из 315.** `docs/reports/retail-census.md` (410 найдено · 200 измерено · `enter` 114) и `docs/reports/registry-revision-proposal.md` (A 10 · B 17 · PAUSED 39)
**ждут слова оператора**; `config/registry.yaml` не тронут, находки — в самих отчётах.

## ⏭️ Next
1. **СЛОВО ОПЕРАТОРА ПО ДВУМ ОТЧЁТАМ C1** — ревизия registry делается отдельным шагом.
2. **Досчёт ценза ($0, ПОСЛЕ стены)** — `retail_census.py --min-subscribers 50 --min-subscribers-chats 0`, накопительно; раньше времени НЕ запускать.
3. **C2 `positions-scale` (≤$1)** — ждёт (1); полнота таблицы для решения не гейт.
4. **`phase7-a1` ($0)** — `docs/PROMPT-phase7-a1.md`, неисполнен (том удалён шагом 0 C1).
5. **`money-anchors` ($0)**; и дыра гарда (`harness-v2.1` Dv6): голый `ruff format`, `git add -u`, `git stage -A` хук НЕ ловит.

## 🚧 Blockers
**⛔ `make check` — ДВА красных, оба не исполнительские:** `2 failed, 4101 passed, 2 skipped`
(27.08, `abe56bb`). (1) `test_repair_phase4_ledger` — старый долг r3. (2) `test_think_zero_shot::…rebuilds…` — цитаты (ф) тимлид ВЕРНУЛ и они проходят, но тот же `370f016` вымыл из STATUS свидетеля `MOVED_BY_D2_STEP_0` `D1 (инструмент, $0)`. Ярус тимлида, разбор — `docs/reports/harness-v2.1.md` Dv1.

**⛔ `MEMORY.md` УПЁРСЯ В ОБА ПОТОЛКА ЗАГРУЗЧИКА** (200 строк → отрез по 25 000 UTF-16 units):
индекс длиннее окна, часть указателей не доезжает, файлы уроков целы. Рычаг один — убрать строки,
это **отдельное решение оператора**. Мерить `context-census.py::loaded_memory`, не `head -c`.

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт
обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list` показывает только running, смотри `pod list -a`.
