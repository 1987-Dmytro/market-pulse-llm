<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-04 19:40:10 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
4133f17 knowledge: s18's boot state — no stop is open, make check is 4320/0, next is the paid session
cb84bfa docs(progress): the stop is closed by (o) — the test reads the record, and next is the purchase
2f2b62c test(promo-dev): the pack test reads the population from the registration, both directions
ec16e82 docs(lead): ruling 04.09 (o) + PHASE v6 §6.6 + the day's fifth stop, committed by path
e18ce58 docs(progress): the stop names the WHOLE repair — the docstring's «56» and the leg-B test beside it
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
**Last update:** 2026-09-04 (s19). Этап 1 `SPEC-v2`, карта `STATUS.md`, цикл `PROCESS.md` v3, фаза **PHASE v6**. Руками, ≤40 строк.

## 🔥 What's Hot
**⛔ ИТЕРАЦИЯ 3 УЖЕ КУПЛЕНА (s19, `b93c997`, $0.493744) — НЕ ПОКУПАТЬ ЕЁ СНОВА.** Под
`cd918wet7sea5b` удалён, сегмент 5 закрыт, `pod list -a` и `serverless list` = `[]`. **ОБА БАРА
ДЕРЖАТ: субъект 0.8714 ≥ 0.80** (было 0.7500 RED) **· сигнал 0.9104 ≥ 0.75.** 40 из 40 юнитов, все
ответы balanced/finish stop, **0 parse failures**, 140 gold-строк. `make check` ЗЕЛЁНЫЙ **4320
passed, 2 skipped, exit 0** на `ca0dfdb` (пол §8 (j) — 4266).
**Дифф против итерации 2 — ровно транспортная починка:** 122 строки итерации 2 стоят НЕИЗМЕННЫМИ,
добавилось 18; 0 сдвинулось, 0 пропало. Страта currency идентична построчно (48/61, субъект 0.7869),
весь прирост в decimal_only **57/79 → 74/79**. Все 40 ответов в ФЕНСЕ, `unfence` прочёл объект.

## ⏭️ Next — СТОП: НОТИС ХОЛДАУТА, решение оператора, ничего не писать вперёд
§8 (e): холдаут — ОДИН выстрел, предрегистрация в закоммиченной записи + STOP-нотис, потом трата.
(m)5 и (o)5 обе кончают сессию на «субъект ≥ 0.80 → НОТИС, END». Заморозка закона (near-quote,
кодбук v1.2) и holdout-40 — зависимость ТИМЛИДА (§7), не моя. Потом «c3» (l) 2–4. Плато 0 из 2.
**💰 После s19:** шаг **$1.242994 из $2.1638**, осталось **$0.920806**; цикл 3 **$5.0299/$7.00**;
холдаут $0.30 нетронут, кап c3 $0.50. `--close` НЕ звать (`closing_entry` односторонний).
REMAINING дрейфует вниз на ~$0.24/день — читать РУКАМИ в §0, не носить из записи.

## 🚧 Blockers / долги (названы, не построены)
**Замена заимствованных 135.232 s ИЗМЕРЕНА И БОЛЬШЕ: смок итерации 3 дал max 201.967 s** (mean
88.772, n=3) — выше и 178.298 s из (o)4, и заимствования в `rung_0`. По (o)4 борроу уходит ПЕРЕД
переизданием итерации 4 на СОБСТВЕННОМ максимуме; на нём dear-угол НЕ влезает в остаток → ветка
(o)4 «средний угол, кап как жёсткий стоп». `rung_0` в s19 не тронут. · **Страта currency 0.7869 не
сдвинулась НИ НА СТРОКУ** — бара на ней нет, но currency-тяжёлый холдаут ляжет у черты. ·
`project()` меряет KILL против ВСЕГО капа: s19 читал руками, max-угол $1.8425 > остатка $1.4048, и
это НЕ KILL — `terminate-after` держит под на $1.1098 (разбор в PROGRESS). · `items[:3] ==
pack["smoke_ids"]` — пак против пака · `pod.main` не снимает патч с `reader_v5` ·
`committed_registration()` не смотрит `pinned_inputs` (s19 сверил все 7 РУКАМИ до create) · `resolvable()` с `+` (l)1 · голд 140 из 208 · «Шикарно…» ((k)2).
**⚠️ `make check` НЕ в платной сессии · ⚠️ ТОЛЬКО ОТЦЕПЛЁННЫМ (`os.setsid`) · ⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ · ⛔ `1925810730` · ⛔ `aggregates.py` и `open`**.

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list -a` показывает только running, смотри `pod list -a`.
