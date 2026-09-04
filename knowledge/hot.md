<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-04 16:26:48 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
97880de docs(progress): the $0 write moved the corpus anchor, and the census artifact is inside the stop
e6299fe docs(progress): the $0 leg of «sources-r3» is done; the paid leg has no instrument
449cab1 fix(collect): the invite form Telethon reads is `t.me/+hash`, not `+hash`
32d05ba knowledge: session 13's checkpoint artifacts, left uncommitted by the auto-end
b2a4a1b docs(lead): ruling 04.09 (k) — A-rest accepted in full, B at ≤ $1.9215
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `the-invite-hash-is-resolved-at-the-call-site.md` — The invite hash is resolved at the call site, not in the registry
- `the-sealed-file-does-not-grow-it-gets-a-sibling.md` — A file 21 seals pin does not grow — the new key gets a sibling file (ruling 04.09 (g), option b)

## 📅 Recent daily logs

- `2026-09-04.md`
- `2026-09-03.md`
- `2026-09-02.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->
# Hot Cache — curated
**Last update:** 2026-09-04 (s15, B куплена: $0.2239). Этап 1 `SPEC-v2`, карта `STATUS.md`, цикл `PROCESS.md` v3. Руками, ≤40 строк.

## 🔥 What's Hot
**⛔ ОТКРЫТЫЙ СТОП — «iteration 2 read».** Субъект **0.7500** против бара 0.80 (итерация 1 по тому
же v1.1-голду — 0.8214), сигналы **0.8854** ✅. **ВЕСЬ провал — один тред** `@VARUS_channel:6216`:
18 → 0 строк; без него было бы **0.8786**, а на 122 комментах вне него итерация 2 ЛУЧШЕ (17 против 25).

**🔬 Транспорт, а не закон.** Ответ пришёл ARRAY внутри ```json-забора; `balanced_prefix`
(`promo_dev_pod_runner.py`) диспатчит массив по `text.lstrip().startswith("[")` — забор делает это
False (`fenced_answers: 40 из 40`), сработало правило объекта, а оно же стоит на СТОПЕ ГЕНЕРАЦИИ
(213 симв., 5.9 с, `finish stop`): 17 ответов НЕ СГЕНЕРИРОВАНЫ, парсером не вернуть. Проверено:
массивный ответ **1 из 40**; `9014` (11→1) и `9999` (6→5) — целые объекты, 0 голд-строк.

**❓ Тимлиду (в PROGRESS).** Починка диспатча — ДЕФЕКТ (тот же `extractor_version`, итерация 2
перекупается) или НОВЫЙ ИНСТРУМЕНТ (03.09 (c) 3 → итерация 3)? От этого зависит, что куплено за
$0.2239: чтение ЗАКОНА или ТРАНСПОРТА. И второй: рост или плато?

**💰** Шаг `promo-dev-loop` ОТКРЫТ: **$0.7493 из $2.4469**, осталось $1.6977 — гарду `--close` НЕ
звать, итерации 3–5 обязаны влезть. Цикл 3: **$4.5265 из $7.00, REMAINING $2.4735** (баланс-дельта,
биллинг отстаёт). Кап c3 = min($0.50, REMAINING−$0.30) = **$0.50**; холдаут $0.30 цел.


## ⏭️ Next / 🚧 Blockers
**Ждём рулинг по стопу**, потом «c3» одной сессией (рулинг (l) 2–4). Раннбук `promo_dev_1.md` уже
на `_iter2` — ни одной ссылки на ПЛАТНЫЕ `…_iter1.*`, юниты смока `7187/9006/6009`. Долги: лег B в ОБЕИХ итерациях
вернул `[]` на всех 16 постах · голд покрывает 140 из 208 комментов (меньше строк — выше процент) ·
`committed_registration()` не смотрит `pinned_inputs` (сверено руками, держат) · `check_law` — только
`codebook_version` · `project()` меряет KILL против ВСЕГО капа шага. **⚠️ Не гонять `make check` во
время платной сессии** (параллельный прогон — красный ERROR в `test_zero_spend_45g5.py`, на тихом
дереве 4 319 / 2 skipped) · **⚠️ ДЛИННЫЙ ПРОГОН ТОЛЬКО ОТЦЕПЛЁННЫМ** (`os.setsid`) · **⚠️ K4 НЕ
ПЕРЕЗАПУСКАТЬ** · **⛔ `1925810730` неадресуем** · **⛔ `aggregates.py` НЕ СМЕЕТ открывать путь**.

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list -a` показывает только running, смотри `pod list -a`.
