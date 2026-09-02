<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-01 19:09:39 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
c754cf7 docs(report,stop): make check green at 4 230 — the ledger hole is closed, not named
d305953 fix(tests): no test can write a real spend ledger — the hole cycle 3 reopened
e7d0c24 docs(stop): name the ledger-write hole cycle 3 inherited from cycle 2
20d263f docs(report,plan): promo-pulse-1 pauses on the even cut's two unset parameters
0a8d02a fix(guard): cycle 3's ledger follows cycle 2's, so an isolated test stays isolated
```

## 📋 Recent decisions

- `the-goal-loop-never-engaged.md` — The `/goal` loop never engaged — §8's resume protocol rests on an unverified mechanism
- `INDEX.md` — Decision records
- `one-live-raw-root-and-an-opt-in-union.md` — One live raw root, and a union that is opt-in

## 📅 Recent daily logs

- `2026-09-01.md`
- `2026-08-30.md`
- `2026-08-27.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->
# Hot Cache — curated
**Last update:** 2026-09-01. Этап 1 `SPEC-v2-promo-pulse.md`, карта `STATUS.md`, цикл `PROCESS.md`
v2.1. Руками, ≤40 строк; археология — в логах дня.

## 🔥 What's Hot
**⏸️ `promo-pulse-1` НА ПАУЗЕ — гард отказывает авторизованному прогону.** Потолок поднят до **$7.00**
(`CYCLE3_CAP_USD`, `981202b`), но якорь цикла-3 остался $4.48 при балансе $14.26 → `enforce()` даёт
**exit 1**, рунг 0 не пишет степ-леджер, S4 не стартует. Вопрос в `docs/plans/promo-pulse-1.STOP.md`:
двинуть ТОЛЬКО `runpod_balance_at_cycle3_start` до $14.26, `anchored_at` не трогая? **make check
4 266 · 2 skipped** @ `97e84e6`. Куплено НИЧЕГО, ни один рунг не сработал.

**НЕ выводить заново.** Vision **7.872 с/стр.** (n=30, бут внутри), маргинал **2.623…3.369**; страницы
C2 **3 008** (968/968); **C2 = $3.1563**, при $7.00 влезает: 3.1563+2.50+0.30 = **$5.9563**. Дро
позиций `a3f659f9a8d73f5e`, дро-20 `3d80c81a9c353130`, экран `28fffc93c723ab8d` — seed 42, дважды.

**Сделано 02.09, всё $0:** `make tick`+`make promo-screen`+`draw_truth_20`+`draw_positions_50`, шесть
промо-таблиц, дайджест остывших тредов, дельта поздних комментов. **`/code-review` перед платной
ногой: BLOCKING ×2, обе починены** (`97e84e6`) — отказанный `--close` больше не закрывает линию,
список леджеров тривайра ВЫВОДИТСЯ из констант гарда.

## ⏭️ Next
Свежая сессия → START RITUAL. Затем: 1) рулинг по якорю; 2) **S4 (платный C2)** → дро-50 ПЕРЕСНЯТЬ
(нынешнее — до-C2 популяция, метить нельзя) → tick → screen; разметки тимлида ждём.

## 🚧 Blockers
**⛔ ЯКОРЬ ЦИКЛА-3 НИЖЕ БАЛАНСА** — единственный блокер платной ноги; ждём слова оператора.
**⚠️ ДОЛГ K4:** `promo_projection_c2.py` пишет «$4.80» (`:366`), грепает `CYCLE 2 SPENT` (`:171`),
игнорирует код возврата гарда (`:153`) — **не перезапускать K4**, пока не закрыто.
**⛔ ЭНДПОИНТ 5c2 И ШАБЛОН УДАЛЕНЫ 08.08** (том `mp-srv2` жив, $0.2333/день): платный vision
начинается со СБОРКИ, рунг 0 — С бутом (`scripts/smoke_vision_c2.py`). **⛔ `1925810730` и
инвайт-хэш неадресуемы** — только через `@ATB_FANatik`. **⚠️ `/goal` НЕ ВКЛЮЧАЕТСЯ** →
[[the-goal-loop-never-engaged]]. **⚠️ MEMORY.md на потолке** — только подселением к близнецу.

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт
обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list` показывает только running, смотри `pod list -a`.
