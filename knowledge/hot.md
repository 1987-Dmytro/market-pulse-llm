<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-04 19:13:08 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
e18ce58 docs(progress): the stop names the WHOLE repair — the docstring's «56» and the leg-B test beside it
5e133af docs(progress): iteration 3's $0 half is done and proven; the open stop is a test that must change
1962ee5 s17: the pack is 40 leg-A units, and the runbook is off every paid `…_iter2.*`
48537b9 s17(prereg): the registration re-emitted for iteration 3 — cap $2.1638, dear $1.3100, FITS
8efb0c8 s17: the emitter is iteration 3 — both halves of the repair pinned, leg B closed
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `the-fence-defeats-the-dispatch-that-fixes-the-array.md` — The fence defeats the dispatch that fixes the array
- `the-invite-hash-is-resolved-at-the-call-site.md` — The invite hash is resolved at the call site, not in the registry

## 📅 Recent daily logs

- `2026-09-04.md`
- `2026-09-03.md`
- `2026-09-02.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->
# Hot Cache — curated
**Last update:** 2026-09-04 19:35 (checkpoint s18). Этап 1 `SPEC-v2`, карта `STATUS.md`, цикл
`PROCESS.md` v3, файл фазы **PHASE v6**. Руками, ≤40 строк.

## 🔥 What's Hot
**СТОПОВ НЕТ — (o) закрыл единственный; `make check` ЗЕЛЁНЫЙ: 4320 passed, 2 skipped, exit 0 на
`cb84bfa`** (пол §8 (j) — 4266). `test_the_pack_pins…` больше не пиннит популяцию ОДНОЙ регистрации:
счёт = `leg_a.threads + leg_b.posts`, множество = `leg_a.order` + `leg_b.by_channel` (карту итерирует
`build_pack`), «ровно» — в ОБЕ стороны; лег B = цикл по юнитам записи, пустой пока держит (m)4.
PHASE §6.6 (v6): этот класс больше не стоп; синтетический юнит отказан ((o)2).

**✅ Весь $0-слой итерации 3 готов ($0; `8efb0c8` · `48537b9` · `1962ee5` · тест `2f2b62c`).** Cap
**$2.1638**, rung 0 на 43 треда + 0 постов, dear **$1.3100 FITS**; `pinned_inputs` += раннер
`102fa524…` и `promo_prompts.py` `dd260cb5…`; лег B закрыта, 16 id в `not_bought`; пак 40 юнитов.
**Все 40 leg-A рендеров побайтово равны итерации 2** при сдвинутой sha модуля — поэтому пины.

## ⏭️ Next — ПЛАТНЫЙ шаг: покупка итерации 3 одной сессией, ничего перед ней
Раннбук `scripts/runbook_promo_dev_1.md` §0–§6 (create → dead-man 500 s → бандл → отцепленный запуск
→ смок → таблица решений → teardown) → `--score --iteration 3` → K8 → таблица ошибок с диффом против
итерации 2. Субъект ≥ 0.80 → НОТИС холдаута = стоп, END; красный → таблица, END. Потом «c3» (l) 2–4.

**💰 Три числа объявлены ДО смока ((m)5):** итерация 3 имеет **$1.4146** (cap $2.1638 − потраченные
шагом $0.749250); KILL читать РУКАМИ против $1.4146; `--terminate-after` = **90 мин = $1.1100**,
ниже dear-угла. REMAINING **$2.4638**, цикл 3 **$4.5362/$7.00**, кап c3 $0.50. `--close` НЕ звать.

## 🚧 Blockers / долги (названы, не построены)
**135.232 s (заимствованный максимум) в рунге 0 — теперь рулинг (o)4, не мой долг:** уходит ПЕРЕД
переизданием итерации 4 (собственный измеренный максимум 178.298 s; не попал — средний угол, кап как
жёсткий стоп). · `items[:3] == pack["smoke_ids"]` — пак против пака · `pod.main` не снимает патч с
`reader_v5` · `committed_registration()` не смотрит `pinned_inputs` · `resolvable()`-тест с `+`
разрешён (l)1 · `project()` меряет KILL против ВСЕГО капа · голд 140 из 208 · «Шикарно…» ((k)2).
**⚠️ `make check` НЕ в платной сессии · ⚠️ ТОЛЬКО ОТЦЕПЛЁННЫМ (`os.setsid`) · ⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ · ⛔ `1925810730` · ⛔ `aggregates.py` и `open`**.

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list -a` показывает только running, смотри `pod list -a`.
