<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-05 14:19:30 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
11f0029 docs(progress): s25 done — the reading arm is pinned, --score takes the arm, no stop is open
0bb62fb s25(pack): the pack re-pins the re-emitted registration — the 80 units are byte-identical
705e2d1 s25(register): the reading arm's key is PINNED and --score takes the arm — ruling 05.09 (u) item 2
ee15c55 docs(team-lead): ruling 05.09 (u) — s24 accepted; dev-2's gold pin and --score by arm come before the pod
0a18c92 docs(progress): the s23 stop is answered and CLOSED — iteration 4 registered and packed at $0
```

## 📋 Recent decisions

- `the-holdout-gate-is-rung-0-fits-plus-the-hard-stop.md` — The holdout's money gate is rung 0 FITS plus the cap as the hard stop — the band gate never runs (ruling 05.09 (r), option ii)
- `INDEX.md` — Decision records
- `the-fence-defeats-the-dispatch-that-fixes-the-array.md` — The fence defeats the dispatch that fixes the array

## 📅 Recent daily logs

- `2026-09-05.md`
- `2026-09-04.md`
- `2026-09-03.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->

# Hot Cache — curated
**Last update:** 2026-09-05 14:14 (s25 checkpoint, рука стала параметром, платная итерация 4 разблокирована). Этап 1 `SPEC-v2`, карта `STATUS.md`, цикл v3, фаза **v10**. Руками, ≤40 строк.

## 🔥 What's Hot
**(u) item 2 сделан за $0 и ПРИНЯТ (аддендум (u)5, 14:20) — предусловие пода закрыто.**
`--score` читал ОДИН эталон по ВСЕЙ ноге: ключ dev-40 (140 строк) против 80 отвеченных юнитов, ключ
dev-2 (188 строк) не открывался. Теперь `DEV_ARMS` — обе руки по МЕТКЕ (`dev40` → часть дро `dev`;
`dev2` → часть `holdout`), `DEV_FILES["arms"]` ВЫВОДИТСЯ из неё; `use_arm` отказывает любой руке вне
`--part dev` и связывает ТОЛЬКО скорер; `score()` судит ОДНУ руку — свои юниты пака, свой эталон,
свой `strata_of`; `--score` без `--arm` ОТКАЗЫВАЕТ на ноге из двух рук; `leg_golds()` — единственный список пинов, и `pinned_inputs` получил `docs/labels-promo-dev2.jsonl 4b60ab99…`.
**Прогон $0** (`--suffix _armdrive`, выходы удалены): dev40 на
`promo_dev40_iter3.jsonl` → 40/40, subject 0.8714 / signal 0.9104; dev2 на `promo_holdout40.jsonl` →
40/40, subject 0.7394 / signal 0.7833. Это ПРОВОДКА, не производительность — оба файла старше v1.2.
**Рунг 0 переоценён на день и НЕ сдвинулся:** cheap $0.8705 · priced $0.9279 · dear $4.9984 → FITS на
MEAN-угле, кап $1.20, жёсткий стоп 5838 с; в паке сдвинулся только `registration.sha256`.
`make check`: 656+1092+2152+421 = **4321 passed, 0 failed, 2 skipped**. Цикл-3: SPENT $5.5157,
REMAINING $3.4843 из $9.00.

## ⏭️ Next
1. **ПЛАТНАЯ итерация 4 — по (u)5 это СЛЕДУЮЩАЯ сессия и ничего кроме неё.** Кап $1.20
   даёт `--terminate-after` 5838 с, но бэкстоп 90 мин = 5400 с кусает ПЕРВЫМ. Смок 3 → **GO по трём ответам,
   полосного гейта НЕТ** → 80 → delete → `--close-segment --replies results/promo_dev40_iter4.jsonl`
   → `--score --arm dev40` (БАР 0.80/0.75) и `--arm dev2` (ЧТЕНИЕ), каждый со своим `--gold`, плюс K8 на каждую → КОНЕЦ на чтениях.
2. Потом эталон holdout-2 (тимлид) → выстрел holdout-2 ≤$0.90 → c3.

## 🚧 Blockers / долги (названы, не построены)
**КРАСНЫХ ТЕСТОВ НЕТ. Долг `--score` ЗАКРЫТ.** · **Тест на селектор руки НЕ добавлен** (§4, прецедент
s24): оба отказа прогнаны в транскрипте; заказать «одна рука → один эталон, один набор юнитов, одна
карта стратумов», негативный контроль — пустая карта на ЧУЖОЙ части дро. · **Срез `make check` обязан
быть ЗАКРЫТЫМ списком:** `ls tests/test_*.py` = **229** файлов; раскрой до 200 дал ЗЕЛЁНЫЕ 3900
вместо 4321, и ничего не упало. · **Порядок пака не строго dev-40→dev-2:** dev-40 закрывается на
юните **42 из 80**. · Леджеры `promo-holdout` и `promo-dev-loop` открыты. · Остальное — в PROGRESS.
**⚠️ `make check` НЕ в платной сессии · ⚠️ ТОЛЬКО ОТЦЕПЛЁННЫМ (`os.setsid`) · ⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ · ⛔ `1925810730` · ⛔ `aggregates.py` и `open`**.
## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list -a` показывает только running, смотри `pod list -a`.
