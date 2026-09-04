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
**Last update:** 2026-09-04 19:03 (checkpoint s17). Этап 1 `SPEC-v2`, карта `STATUS.md`, цикл
`PROCESS.md` v3, файл фазы **PHASE v5**. Руками, ≤40 строк.

## 🔥 What's Hot
**ОТКРЫТ СТОП — тест, который пришлось бы менять (PHASE §8 (j)).** `make check` на `1962ee5`:
**1 failed, 4319 passed**. `test_the_pack_pins_exactly_what_the_pod_re_derives` держит популяцию
итерации 2 — `== 56` (стр. 302), 16 leg-B (стр. 303), «56» в docstring (стр. 287); (m)4 закрыл лег B,
пак законно 40/0, а содержательное утверждение ПРОШЛО (40 sha перевыведены, отказов ноль). Варианты:
(a) счётчики из регистрации · (b) 40 и 0 руками · (c) синтетический leg-B юнит — любой правит тест.

**✅ Весь $0-слой итерации 3 готов ($0; `8efb0c8` · `48537b9` · `1962ee5`).** Cap **$2.1638**, rung 0
на 43 треда + 0 постов, dear **$1.3100 FITS**; `pinned_inputs` += раннер `102fa524…` и
`promo_prompts.py` `dd260cb5…`; лег B закрыта, 16 id в `not_bought`; пак 40 юнитов; раннбук переточен.
**Все 40 leg-A рендеров побайтово равны итерации 2** при сдвинутой sha модуля — поэтому пины.

## ⏭️ Next — рулинг по стопу, потом покупка итерации 3 одной сессией
`make check` зелёный → раннбук §0–§6 (create → dead-man 500 s → бандл → отцепленный запуск → смок →
таблица решений → teardown) → `--score --iteration 3` → K8 → таблица ошибок с диффом против
итерации 2. Субъект ≥ 0.80 → НОТИС холдаута = стоп, END; красный → таблица, END. Потом «c3» (l) 2–4.

**💰 Три числа объявлены ДО смока ((m)5):** итерация 3 имеет **$1.4146** (cap $2.1638 − потраченные
шагом $0.749250); KILL читать РУКАМИ против $1.4146; `--terminate-after` = **90 мин = $1.1100**,
ниже dear-угла. REMAINING **$2.4638**, цикл 3 **$4.5362/$7.00**, кап c3 $0.50. `--close` НЕ звать.

## 🚧 Blockers / долги (названы, не построены)
**Rung 0 считает по ЗАИМСТВОВАННОМУ максимуму 135.232 s**, хотя измеренных смок-максимума два —
178.298 s (итер. 1) и 88.237 s (итер. 2); по первому dear дал бы **$1.6906** > $1.4146 — решить ДО
итерации 4. · `pod.main` не снимает патч с `reader_v5` · `committed_registration()` не смотрит
`pinned_inputs` · `resolvable()`-тест с `+` разрешён (l)1 · `project()` меряет KILL против ВСЕГО
капа · голд 140 из 208 · «Шикарно…» ждёт ((k)2). **⚠️ `make check` НЕ в платной сессии · ⚠️ ТОЛЬКО
ОТЦЕПЛЁННЫМ (`os.setsid`) · ⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ · ⛔ `1925810730` · ⛔ `aggregates.py` и `open`**.

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list -a` показывает только running, смотри `pod list -a`.
