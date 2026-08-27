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

**Last update:** 2026-08-27 — этап 1 = `docs/SPEC-v2-promo-pulse.md` («промо-пульс сетей»). Карта,
деньги и рулинги — `docs/STATUS.md`; цикл фазы — `docs/PROCESS.md` v2.1 (`/plan-phase` → «go» →
`/report`). Блок курируется руками, **≤40 строк**: у археологии есть дом — отчёты, ADR, логи дня.

## 🔥 What's Hot
**⛔ АККАУНТ TELEGRAM ЗАПЕРТ ДО 2026-08-28 10:21 UTC.** FloodWait 85 352 с записан в
`results/joins_5c1.jsonl` строкой `(census)`; лимит сидит на `ResolveUsernameRequest`, с которого
начинается КАЖДЫЙ вход и выборка комментов, и повтор внутри окна окно удлиняет. `retail_census.py`
и `collect_5c1.py` отказываются стартовать сами ([[rate_limit_on_the_shared_first_step]]).

**🧾 C1 ИСПОЛНЕН, ТАБЛИЦА НЕПОЛНАЯ — 200 из 315.** `results/retail_census.json`,
`docs/reports/retail-census.md` (410 найдено · 200 измерено · `enter` 114) и
`docs/reports/registry-revision-proposal.md` (A 10 · B 17 · PAUSED 39) **ждут слова оператора**;
`config/registry.yaml` не тронут. Поправки чтения и находки — в отчётах и в логе дня 27.08.

## ⏭️ Next
1. **СЛОВО ОПЕРАТОРА ПО ДВУМ ОТЧЁТАМ C1** — ревизия registry делается отдельным шагом.
2. **Досчёт ценза ($0, ПОСЛЕ 2026-08-28 10:21 UTC)** — `retail_census.py --min-subscribers 50
   --min-subscribers-chats 0`, запись накопительная. Раньше времени НЕ запускать.
3. **C2 `positions-scale` (≤$1)** — ждёт (1); полнота таблицы для решения не гейт.
4. **`phase7-a1` ($0)** — `docs/PROMPT-phase7-a1.md`, неисполнен (том удалён шагом 0 C1).
5. **`money-anchors` ($0)** — settled-закрытия, 19 без `anchored_at`.

## 🚧 Blockers
**⛔ `make check` — один красный, не исполнительский:** `test_repair_phase4_ledger`, старый долг r3
(второй, `test_think_zero_shot`, снят шагом 0 `harness-v2.1`). **`MEMORY.md` упёрся в оба потолка
загрузчика** (200 строк → 25 000 UTF-16 units): мерить `context-census.py::loaded_memory`, не `head -c`.

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт
обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py` — гонять
их после КАЖДОЙ правки этого файла ([[fact_is_the_rule_when_the_law_keys_on_it]]).

- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list` показывает только running, смотри `pod list -a`.
