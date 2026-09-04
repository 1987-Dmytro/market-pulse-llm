<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-04 18:16:11 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
c46f9e3 docs(lead): ruling 04.09 (n) — s16 accepted by diff, and the map moved with it
6aabc3c docs(progress): the stop's cost is measured, and the re-emission must pin BOTH halves of the repair
65ae76c docs(progress): the stop is closed by (m), the dispatch is repaired, next is iteration 3's re-emission
f872a53 fix(promo-dev): unfence BEFORE the dispatch, and a bare array is the rows it is
b220acc docs(lead): ruling 04.09 (m) + PHASE v5 + the day's stop-pattern review, committed by path
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
**Last update:** 2026-09-04 (close дня). Этап 1 `SPEC-v2`, карта `STATUS.md`, цикл `PROCESS.md` v3,
файл фазы **PHASE v5**. Руками, ≤40 строк.

## 🔥 What's Hot
**Открытого стопа НЕТ.** Рулинг **(m)** закрыл «iteration 2 read»: итерация 2 стоит как измерена
(сигналы **0.8854** ✅, субъект **0.7500** ❌ — весь провал один тред `@VARUS_channel:6216`, 18 → 0),
починка = **НОВЫЙ инструмент = итерация 3** в той же сессии; **плато нет** (0 из 2); B закрыта.

**✅ Починка сделана и ПРИНЯТА рулингом (n) по диффу (s16, $0, `f872a53`).** `balanced_prefix` читает забор через
`promo_prompts.unfence` ПЕРВЫМ, диспатчит по форме ВТОРЫМ; `fold` читает голый массив как строки.
ОДИН тест = $0-дрилл §6.5. `make check` **4 320 / 2 skipped**. Платная запись НЕ двигается: перепарс
`_iter2` даёт те же 122 строки и тот же один parse failure.

## ⏭️ Next — итерация 3, ОДНОЙ сессией ((m)5)
Переиздание регистрации (`iteration: 3`; **пиннуть sha И раннера, И `promo_prompts.py`** — половина
починки в каждом, `check_law` не покрывает ни одного; `extractor_version` = `sha256(rendered)` и
идентичность нести НЕ может) → три числа ДО смока → покупка → K8 → таблица ошибок с диффом.
Субъект ≥ 0.80 → НОТИС холдаута = стоп, END; красный → таблица, END. Потом «c3» по (l) 2–4.
Раннбук: репоинтить `_iter2`-пути и юниты смока `7187/9006/6009`.

**💰** Шаг `promo-dev-loop` ОТКРЫТ: **$0.7493 из $2.4469, осталось $1.6977** — гарду `--close` НЕ
звать, итерации 3–5 обязаны влезть. Цикл 3: **$4.5265 из $7.00, REMAINING $2.4735** (дельта баланса,
биллинг отстаёт 30–40 мин). Кап c3 = **$0.50**; холдаут $0.30 цел. Одна леджер-строка за сессию.

## 🚧 Blockers / долги (названы, не построены)
`pod.main` не снимает свой патч с `reader_v5` · `committed_registration()` не смотрит
`pinned_inputs` · тест `resolvable()` с `+` разрешён (l)1, не написан · `project()` меряет KILL
против ВСЕГО капа шага · голд — 140 из 208 комментов · near-quote «Шикарно…» ждёт заморозки ((k)2).
**⚠️ Не гонять `make check` во время платной сессии** · **⚠️ ДЛИННЫЙ ПРОГОН ТОЛЬКО ОТЦЕПЛЁННЫМ**
(`os.setsid`) · **⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ** · **⛔ `1925810730` неадресуем** · **⛔ `aggregates.py`
НЕ СМЕЕТ открывать путь**.

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list -a` показывает только running, смотри `pod list -a`.
