<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-04 07:46:22 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
3ab9038 docs(progress): the open stop inside its own 15-line format
30dc21c docs(progress): the stop file back inside its 60-line cap
a552a98 docs(progress): the stop before the first edit — `admin_anon_ids` cannot enter a file 21 sealed records pin
5fcecad knowledge: session 9 artifacts — the fence decision, the terminate-after derivation, hot cache
7675946 docs(lead): ruling 03.09 (f) — iteration 1 READ; codebook v1.1; iteration 2 = admin marker + chain canonical id + codebook examples
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `terminate-after-is-the-cap-less-what-the-step-spent.md` — `--terminate-after` is derived from the cap LESS what the step already spent
- `the-fence-is-not-the-answer.md` — The ```json fence is read off, and nothing inside it is repaired — iteration 1's one deviation

## 📅 Recent daily logs

- `2026-09-04.md`
- `2026-09-03.md`
- `2026-09-02.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->
# Hot Cache — curated
**Last update:** 2026-09-04 (с10 — рулинг (f) принят, A(1) ОСТАНОВЛЕН до правки). Этап 1 `SPEC-v2-promo-pulse.md`, карта `STATUS.md`, цикл `PROCESS.md` v3. Руками, ≤40 строк.

## 🔥 What's Hot
**⏸️ `promo-pulse-1` — стоп «где могут жить `admin_anon_ids`».** Состояние — в
`docs/plans/promo-pulse-1.PROGRESS.md`. Рулинг (f) принят и закоммичен (`7675946`): кодбук **v1.1**,
3 строки эталона → `post`, итерация 2 = сессия A ($0: метка `[admin]`, id сети, примеры в шаблоне,
тесты) → сессия B (платная ≤$1.9746). Итерация 1: signal **0.8792** ✅ · subject **0.7929** / 0.80.

**⛔ A(1) НЕ ПОСТРОЕН — и это правильно.** `config/registry.yaml` пинят **21 запечатанный рекорд**:
r1 `d4e3b237…` 7 · pre-(13)(b) `920c7f20…` 8 · signed-screen `c82d0cff…` 5 · ЖИВЫЕ байты `eff8ba5b…`
1 (`prereg_promo_c2.json`). Строки VARUS/msuaaaa — r1-эпохи, ВНЕ скобки r2, поэтому любая строка
попадает в каждую реконструкцию. Проверено запуском: `run_promo_c2.preflight` проходит на HEAD и
отказывает после ОДНОЙ строки; `build_aggregates.py:294` красит `make check` через
`tests/test_export_dashboard_data.py`. Ревизия r3 чинит все четыре семейства и НЕ чинит байтовый
preflight — [[5c2-closed-the-sitting-and-the-shelf-life-redesign]]. Три ветки — в PROGRESS.

**🔴 Пины регистрации УЖЕ сдвинулись** (деньги сессии B): `prereg_promo_dev_loop.json` держит эталон
`302113b8…` / кодбук `6a74bc81…`, на HEAD `2303ea43…` / `23610346…` — коммит v1.1 тимлида; а
`committed_registration()` сверяет только СВОЙ файл, `pinned_inputs` не переверяет никто.

**⚠️ Ловушки метки.** 59 из 82 админских комментов dev-40 БЕЗ текста — метить только непустые. Флаг
обязан ехать В ПАКЕТЕ: под ре-рендерит и сверяет `rendering_sha256`, а там лишь пары `[msg_id, text]`.

## ⏭️ Next / 🚧 Blockers
Ждём рулинг по трём веткам A(1) → A(2) `promo_key`, A(3) примеры в шаблоне, A(4) чтение v1.1 за $0
(НЕ через `--score`: перезаписывает `errors_iter1.json`), A(5) тесты. Параллельно за $0: разметка
позиций тимлидом ПО СТРАНИЦАМ (46 страниц) — критический путь S1. Деньги: шаг `promo-dev-loop`
**$0.5254 из $2.50** ($1.9746) · `CYCLE 3 SPENT $4.0631 of $7.00 · REMAINING $2.9369`; сессия 10 = **$0**.
**⚠️ K4 НЕ ПЕРЕЗАПУСКАТЬ** (`:366/:171/:153`) · **⛔ `1925810730` и инвайт-хэш неадресуемы** ·
**⚠️ платный ран отцеплённым (`setsid`), Dv904** · **⚠️ фикстура в стор патчит ВСЕ derived-корни** ·
**⚠️ `volume_calc_5c1.py` НЕ ЗАПУСКАТЬ просто так.**

## 🔫 Footguns этого файла
**⛔ ЭТОТ ФАЙЛ ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА.** `scripts/volume_calc_5c1.py :: quoted()` берёт обе строки ниже посимвольно; пропажа любой роняет девять `tests/test_volume_calc_5c1.py`.
- 100 GB сетевого тома стоят **~$0.24/day** — цена ЗА ТОМ, а не состояние счёта; с 27.08 том один,
  `mp-srv2`. Литерал обязан стоять ровно так, по-английски со слэшем.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. Под на одну сессию — **delete** (`runpodctl pod delete`),
  не stop; `runpodctl pod list` показывает только running, смотри `pod list -a`.
