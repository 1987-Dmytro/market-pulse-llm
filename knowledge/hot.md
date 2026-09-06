<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-06 21:48:14 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
ab29a60 docs(progress): s34 — «p1-prep» DONE at the $0 table: promo-holdout2 CLOSED $0.4253, holdout-3 drawn (358 → 20/20, blind), P1 + its ONE test, dev-3 0.7054 → 0.7500 (dev-40 0.8857 =, dev-2 0.8883 → 0.9043), make check 4326/2 at 9b8a2de; OPEN STOP: the pre-registered decision table RETURNS the fork to the operator at $0 — dev-3 < 0.80, the holdout-3 shot is NOT bought
9b8a2de s34(p1-prep): P1 measured at $0 on the three dev sets, K8 v2 before → after — dev-40 0.8857 → 0.8857 (0 rows) · dev-2 0.8883 → 0.9043 (5 rows: R1 4, R2 1) · dev-3 0.7054 → 0.7500 (5 rows: R1 2, R3 3; 84 of 112); signals unmoved on all three, zero hit→miss; leak check: holdout-3's 40 threads share none of the 120 this reading opened; the DECISION TABLE of PHASE v18 §6.2 reads RETURN to the operator at $0 (dev-3 0.7500 < 0.80; dev-40 and dev-2 hold) — results/grade_promo_p1_readings.json (two runs byte-identical, edacb611…), results/promo_p1_predicted_{dev40,dev2,dev3}.jsonl, scripts/promo_p1_apply.py
4a27940 s34(p1-prep): P1 — src/market_pulse/promo_post.py, the deterministic layer over the frozen reader's rows: R1 post ⇒ subject = root · R2 own channel: post with signals ⇒ chain = the owner · R3 sku/brand with жалоба on the store-stock lexicon ⇒ chain = the thread's retailer (own channel → owner; aggregator → the ONE registry chain the post names, else the row stays) — nothing else; pure, rows copied never edited; the lexicon is the addendum's verbatim, matched at a word start as a prefix; its ONE test, both directions per rule, against the real registry and alias table (3 passed)
7a2bf3d s34(p1-prep): the holdout-3 DRAW — results/promo_threads_draw_3.json, seed 42 over draw-2's 398 MINUS holdout-2's 40 = 358, 20/20 by stratum, disjoint from all 120 drawn; the producer takes N earlier draws as parameters and its record's decision fields branch on the leg (LEGS) or refuse; draw 2 still rebuilds byte for byte (567cb236…); K7 two runs identical (76435461…); no gold yet — the team lead labels it BLIND
1a0d503 money(ledger): promo-holdout2 CLOSED at $0.4253 — the walk covered the run record's 2116 s, 3.6 % off the post-run reading $0.4107
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `the-registration-opens-the-line.md` — The registration OPENS its line, so §0a lives in the PAID session
- `a-lines-close-settles-against-its-post-run-reading.md` — A step line's close settles against its POST-RUN reading

## 📅 Recent daily logs

- `2026-09-06.md`
- `2026-09-05.md`
- `2026-09-04.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->

# Hot Cache — curated
**Last update:** 2026-09-06 22:14 (s35 «p1-ship»: S2 отгружен КАК ИЗМЕРЕНО — P1 в петле, блок S2 на экране и в README из result-файлов).
Этап 1 `SPEC-v2`, карта `STATUS.md`, цикл v3, фаза **v19**, процесс **Money v2.3**. Руками, ≤40 строк.

## 🔥 What's Hot
**S2 ЗАКРЫТ КАК ИЗМЕРЕНО (рулинг (cc), слово (a)):** holdout-2 с P1 **0.7500 (84/112) ❌ бар 0.80** · сигналы **0.8021 ✅ бар 0.75**; сырьё
0.7054 / 0.8021; holdout-40 0.7181 / 0.7958 — три строки на экране (`dashboard/promo.html`) и в README ИЗ `grade_promo_p1_readings :: sets.dev3` ·
`grade_promo_holdout2` · `grade_promo_holdout40` (отказ ПО ИМЕНИ; `--results` — контроль, exit 1); README пишет `build_readme_results.py` тем же
ридером. Дро holdout-3 (`76435461…`) — резерв, НЕ размечается, выстрела НЕТ, $0 потрачено.
**P1 в петле (`ba81a37`):** `make tick` гонит `promo_post.apply` по КАЖДОЙ строке ридера (about + signal) ДО `subject_id`; тред из `RawStore`, оба
корня; тред без поста — считается, не отказ. K10 держит (8 тестов). Реальный стор: 0 строк ридера (C3 не куплен, 2290 тредов в очереди).
**Счётчик ничьих (`b60560d`):** `promo_p1_apply.py :: misses` → `misses_before/after` (предикат грейдера + `gold_unsure`); принятые числа не тронуты,
два прогона байт-в-байт. **Файл говорит 16 из 28**, рулинг (cc) руками — 15: шесть заметок из 16 — ничьи только по СИГНАЛУ. Определение — тимлида.
`make check` **4326/2** на `d6e4ce9`; `runpodctl` не звался ($0); цикл-3 REMAINING **$2.1178** (18:21Z, нового чтения нет).
**⛔ ОТКРЫТЫЙ СТОП (s35):** вход P1 в ПЕТЛЕ ≠ вход P1 в ЗАМЕРЕ — замер кормил сырой ответ, запись петли ПРОСЕЯНА хуками, тип упавшей
signal-строки до P1 не доходит. Реплей: 3 отказа `quote_is_a_substring` на holdout-2, 4 на dev-40, ОДНА строка меняет исход
(`@VARUS_channel:5119/5987`, цитата с маленькой буквы) → петля даёт **83/112 = 0.7411**, экран и README печатают замеренные **84/112 = 0.7500**
(dev-40 без изменений). Тимлиду: (a) запись C3 несёт сырые типы; (b) число раскрывается как ЗАМЕР; (c) иначе. Чисел не менял, запись не расширял.

## ⏭️ Next — «c3-prep» ($0): нога c3 по рулингу (l) 2–4 на своей линии `promo-c3`, кап ≤ $0.50 (переоценка на dry-run); разрешение на
`runpodctl pod create` ДОКАЗАНО за $0 (PROCESS v2.3: allow-правило в `.claude/settings.json` + `--help` в ранбуке §0); ранбук перенацелен → свежий
верификатор → «c3» (платно) → том `mp-srv2` → clean-clone e2e + `draw_truth_20` → гейт 12–13.09. **СНАЧАЛА — рулинг по стопу выше.**

## 🚧 Blockers / долги (названы, не построены)
**⛔ Классификатор auto-режима БЛОКИРУЕТ `runpodctl pod create`** (и скрипт с ним) — только слово оператора В СЕССИИ снимает.
**⚠️ zsh НЕ разбивает `$SSHO` на слова** — опции ssh/scp выписывать явно (4-й раз, ≈ $0.03 пода). · **Край hard stop в
закрытии гарда:** ненулевое пред-подовое чтение при отказавшей пост-рановой `--note` — отказ закрытия навсегда; закрытие на
≥ cap печатает CLOSED и затем exit 1 — это settled. · **⛔ `promo-dev-loop` ОТКАЗЫВАЕТ** — никогда не называется. ·
`--step promo-holdout2` БЕЗ `--part holdout2` = dev-нога под линией (отказ не построен). · `-r2` сам ничего не перенацеливает.
· сюита ~12 мин, 229 файлов — только срезами; тесты ГРЕПАЮТ `hot.md`/PROGRESS — не править, пока идут.
**⚠️ ТОЛЬКО ОТЦЕПЛЁННЫМ (`setsid`) · ⚠️ живость по PID, `pgrep -f` ловит и свой зонд · ⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ ·
⛔ `1925810730` · ⛔ `aggregates.py` и `open`**.
## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list -a` показывает только running, смотри `pod list -a`.
