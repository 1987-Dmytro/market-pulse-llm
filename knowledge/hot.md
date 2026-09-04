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
**Last update:** 2026-09-04 (закрытие дня; сессии 10–14, все за $0). Этап 1 `SPEC-v2`, карта
`STATUS.md`, цикл `PROCESS.md` v3. Руками, ≤40 строк.

## 🔥 What's Hot
**✅ ОТКРЫТОГО СТОПА НЕТ — рулинг (l) ответил на оба вопроса и ПЕРЕСТАВИЛ порядок. СЛЕДУЮЩЕЕ — B,
платная итерация 2** (`*_iter2.*`, **≤ $1.9215**): готова и критический путь. ПЕРЕД запуском увести
`--score --suffix` и `--out` раннбука K8 с ПЛАТНЫХ `…_iter1.*`. Потом «c3» ОДНОЙ сессией.

**📐 c3 — закон, а не вилка ((l)2–3).** Параметры C2-продюсерам, НЕ сиблинги: `--out`, `--channels`,
`--anchor` (пиннится в регистрации), `--prereg`, `--step`, `--cap`; файлы C2 остаются побайтово теми
же (десять пинов держат), c3 пишет `results/*_c3.json` под `results/prereg_promo_c3.json` со своим
якорем и **своим леджером `promo-c3`** (`STEP promo-pulse-1` закрыт). Экран — **все окна**
(`tick --window all`, дефолт, если тест не пинит `w2`), оба канала под ОДНИМ существующим id
`marketopt_promo`: `chain_aliases.yaml` получает `chain_of_channel: {marketopt_private:
marketopt_promo}`, читается тем же читателем ДО написаний.

**✅ Сегодня.** «A-rest» принят (k): subject **0.8214**, закон **v1.2** `a587e0d6…`. **Маркетопт
собран** (`449cab1`, принято (l)1): был в членах с 30.08, не собирался из-за одного дефекта —
Telethon читает `+`-инвайт только после `t.me/`. **+33 поста, все с медиа, $0**; `make check`
**4 319 / 2 skipped**. Юнит-тест на `resolvable()` с `+`-хэндлом РАЗРЕШЁН (l)1.

**⚠️ Сдвинутый якорь не опасен, но и не забыт:** максимум корпуса 2026-08-30 → **2026-09-04**; (l)1 — пока C2-продюсеры не перезапускаются, правда C2 в его запечатанных файлах. У c3 якорь ЯВНЫЙ.

**💰** Цикл 3 **$4.2531 из $7.00**, REMAINING **$2.7469** (том ~$0.24/день); шаг $0.5254 из $2.4469 → **B ≤ $1.9215**. Кап c3 = **min($0.50, REMAINING − $0.30), как гард напечатает ПОСЛЕ B**; меньше $0.15 — стоп за словом оператора.

## ⏭️ Next / 🚧 Blockers
B → c3. Долги: `committed_registration()` не проверяет `pinned_inputs` · `check_law` сверяет только
`codebook_version` · ветка `--comments` шлёт голый хэндл (мертва из-за `comments_enabled: false`).
Закон и кодбук НЕ ТРОГАТЬ до заморозки ((k)2). **⚠️ ДЛИННЫЙ ПРОГОН — ТОЛЬКО ОТЦЕПЛЁННЫМ**
(`os.setsid`): фоновые задачи харнеса убивались на 26 %. · **⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ** · **⛔
`1925810730` неадресуем** · **⛔ `aggregates.py` НЕ СМЕЕТ открывать путь** ([[a_module_can_have_a_test_about_what_it_may_not_do]]).

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list` показывает только running, смотри `pod list -a`.
