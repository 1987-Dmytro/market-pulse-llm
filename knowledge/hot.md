<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-09-04 10:15:01 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
be6a35e docs(progress): the rebuild proved against iteration 1's own pack, inside the 60-line cap
b4f1700 knowledge(hot): the curated block says A(1) is BUILT — it is injected before PROGRESS is read
9f77ac8 docs(progress): A(1) built and checked — the open stop is closed, next is A(2)
d01586a knowledge: session 9's Stop-hook artifacts, left uncommitted by the auto-end
c7a63a7 s10 A(1): the channel's own account is marked `[admin]`, and a wordless comment leaves the render
```

## 📋 Recent decisions

- `the-sealed-file-does-not-grow-it-gets-a-sibling.md` — A file 21 seals pin does not grow — the new key gets a sibling file (ruling 04.09 (g), option b)
- `INDEX.md` — Decision records
- `terminate-after-is-the-cap-less-what-the-step-spent.md` — `--terminate-after` is derived from the cap LESS what the step already spent

## 📅 Recent daily logs

- `2026-09-04.md`
- `2026-09-03.md`
- `2026-09-02.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->
# Hot Cache — curated
**Last update:** 2026-09-04 (с11 — **A(1) ПРИНЯТ** рулингом (h), `c7a63a7`; следующее — «A-rest»). Этап 1 `SPEC-v2-promo-pulse.md`, карта `STATUS.md`, цикл `PROCESS.md` v3. Руками, ≤40 строк.

## 🔥 What's Hot
**▶️ `promo-pulse-1` — стопа нет, следующий шаг A(2).** Состояние — в
`docs/plans/promo-pulse-1.PROGRESS.md`. Рулинг (f) + (g) закоммичены (`7675946`, `5d6aecf`): кодбук
**v1.1**, 3 строки эталона → `post`, итерация 2 = сессия A ($0: метка `[admin]`, id сети, примеры в
шаблоне, тесты) → сессия B (платная ≤$1.9746). Итерация 1: signal **0.8792** ✅ · subject **0.7929** / 0.80.

**✅ A(1) готов (`c7a63a7`, $0).** id админов — в НОВОМ `config/channel_admins.yaml`, реестр НЕ тронут
(21 печать; r3 закрыта опцией (b) — [[the-sealed-file-does-not-grow-it-gets-a-sibling]]). Читатель один — `promo_prompts.admin_ids`; метка по ID,
`null`-отправитель ни с чем не совпадает; бестекстовые комменты выброшены из рендера. Флаг едет В
ПАКЕТЕ: `comments` = `[msg_id, text, sender_anon_id]`, под называет колонки (пакет пар ещё рендерится).
Проверено: сброшено **68** = `n_wordless` жеребьёвки; меток **23** = админских коммента с текстом;
пакет пересобран, `56/56`, при расхождении yaml — ОТКАЗ на `@VARUS_channel:2537`; `prep` = `7971ed66…`.

**🔴 Пины регистрации УЖЕ сдвинулись** (деньги сессии B): `prereg_promo_dev_loop.json` держит эталон
`302113b8…` / кодбук `6a74bc81…`, на HEAD `2303ea43…` / `23610346…` — коммит v1.1 тимлида, а
`pinned_inputs` не переверяет никто. `check_law` сверяет ТОЛЬКО `codebook_version`, и A(1) его не
двинул: пока нет `template_sha256`, защита — по-юнитный `rendering_sha256`. Обе дыры закрывает A-rest.

## ⏭️ Next / 🚧 Blockers
**Рулинг (h): A(2)–A(5) + переиздание регистрации = ОДИН пункт «A-rest» в одной сессии.** `promo_key`
→ примеры в TEMPLATE (ДОСЛОВНО из кодбука v1.1 §3–§6, со ссылкой на §, блок в PROGRESS) → чтение v1.1
за $0 в `errors_iter1_v1.1.json` (НЕ через `--score --iteration 1`: перезапишет платный) → stub-тесты
→ регистрация под sha v1.1 + `template_sha256`, в пакете `"iteration": 2`. Дальше сразу B, БЕЗ чтения
рендера тимлидом ((h) п.3): `--out …_iter2.jsonl`, ≤ $1.9746.
Параллельно за $0: разметка позиций тимлидом ПО СТРАНИЦАМ (46 страниц) — критический путь S1.
Деньги: шаг `promo-dev-loop` **$0.5254 из $2.50** ($1.9746) · `CYCLE 3 SPENT $4.0631 of $7.00 · REMAINING $2.9369`; сессии 10 и 11 = **$0**.
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
