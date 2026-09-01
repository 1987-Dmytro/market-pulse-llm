<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-01 07:32:29 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
8ae33e4 docs(report): keep the addendum inside PROCESS's 30-line rule
6c31492 feat(collect): S2's join and comment phases finished — +1 190 comments into the live root
ee23a13 docs(report): the smoke ran — the STOP is lifted and the rate is measured
3f137b9 feat(smoke,projection): the smoke landed — 7.872 s/page measured, and K4 states one number
1a8b1d4 feat(smoke): the C2 vision smoke, pre-registered before the first billable action
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `one-live-raw-root-and-an-opt-in-union.md` — One live raw root, and a union that is opt-in
- `poltava-chats-carry-category-voice-not-brand-voice.md` — The Poltava chats carry category voice, not brand voice

## 📅 Recent daily logs

- `2026-09-01.md`
- `2026-08-30.md`
- `2026-08-27.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->
# Hot Cache — curated
**Last update:** 2026-09-01 (закрытие смены 30.08). Этап 1 `SPEC-v2-promo-pulse.md`, карта `STATUS.md`, цикл `PROCESS.md` v2.1. Руками, ≤40 строк; археология — в логах дня.

## 🔥 What's Hot
**✅ СЛАЙС `promo-pulse-1-s2s3` ПРИНЯТ GREEN** — `docs/reports/promo-pulse-1-s2s3.md` @ `ee23a13`
+ аддендум `8ae33e4`. **make check 4 205 · 2 skipped.** SP-4 закрыт рулингом (a): v1 — архив
навсегда, `data/raw_r2/` — единственный живой корень, union **опционален**, дро читает ТОЛЬКО v1
→ [[one-live-raw-root-and-an-opt-in-union]]. Реестр: **74 источника, collected 17 / not 57**;
стор: **+1 340 постов, +1 190 комментов**, свежесть до 30.08; `shasum -c raw_v1_baseline` 6/6 OK.

**Числа, которые НЕ выводить заново.** Vision **7.872 с/стр. (n=30, БУТ ВНУТРИ)**; маргинал с
бутом, оплаченным один раз, — **2.623…3.369**, бут **157.449 с = $0.0483**. 5c2 = 10.408; «1.7» —
прогрев. Перепись (ПОСЛЕ докачки): окно **03–31.08**, `ids_sha256 a56dc6dace1bfb44`, **968 постов
→ 1 022…9 653 страниц**, 405 текстово-ценовых. Дро **`6f9fa245b9d70254`**, 678 → 488 (182/306),
20+20/20+20, seed 42 — не двигалось после докачки: это и есть контроль на утечку union.

## ⏭️ Next
1. **`docs/PROMPT-c2-pagecount.md` ($0)** — численность страниц: ЕДИНСТВЕННОЕ, на чём стоит SP-1.
   Его п.2 — `collect_5c1 :: collectable` не читает `source.collect` (находка `/code-review`;
   спасает только гард `RawStore.append`).
2. **Разметка dev-40 разблокирована** (по 10 тредов); 50 позиций — после S4. Слово оператора по
   SP-1 — **ОДИН раз**, на числе из п.1: цикл-3 / сузить / под-раннер.

## 🚧 Blockers
**⛔ SP-1 — ПРО СТРАНИЦЫ, НЕ ПРО СТАВКУ.** Остаток **$2.3202**, том ест $0.2333/день; у пола
страниц C2 = **$0.87…$1.10 (влезает)**, у потолка **$7.81…$10.02 (нет)**.
**⛔ ЭНДПОИНТ 5c2 И ШАБЛОН УДАЛЕНЫ 08.08**, выжил только том `mp-srv2`: следующий платный vision
начинается со СБОРКИ, рунг 0 считать С бутом. Драйвер — `scripts/smoke_vision_c2.py`.
**⛔ ЧИСЛОВОЙ ID И ИНВАЙТ-ХЭШ НЕАДРЕСУЕМЫ.** `1925810730` достижим ТОЛЬКО через `@ATB_FANatik`
(`linked_chat_id`), `+Ejz6ubzm21IyMTQy` то же — убрать или пометить, **слово тимлида**.
**⚠️ MEMORY.md на потолке:** 200 строк / 24 952 из 25 000 — мерить `context-census.py::loaded_memory`.

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт
обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list` показывает только running, смотри `pod list -a`.
