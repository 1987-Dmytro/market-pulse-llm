<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-08-15 12:21:00 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
3a16b55 docs(report): phase6a -- the index block that could not move, and 902 numbers
a7fd072 fix(phase6a): the census printout skipped a table it had just filled
981c5ad refactor(phase6a): bind the filters, and stop reaching for a private name
6043d95 feat(phase6a): the deterministic export and the metric dictionary
63676db feat(phase6a): the SQLite aggregate layer, converged with the sealed window summary
```

## 📋 Recent decisions

- `5c2-closed-the-sitting-and-the-shelf-life-redesign.md` — 5c2 closes: the sitting ratified both halves, 3.19 rules on the text-less comments, and the shelf-life redesign is named as a house pattern
- `INDEX.md` — Decision records
- `the-d-cut-and-the-fourth-kind.md` — The post leg's population is the D cut — 44 of 349 — and the marker row that makes its resume exact

## 📅 Recent daily logs

- `2026-08-15.md`
- `2026-08-14.md`
- `2026-08-13.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->
# Hot Cache — curated

**Last update:** 2026-08-15 (checkpoint 12:18) — исполнен `phase6a` ($0): **амендмент 3.20 в SPEC**,
слой агрегатов SQLite (`data/derived/pulse.db`, gitignored), детерминированный экспорт
`results/dashboard_data_w1.json` и словарь метрик `config/metrics.yaml`. `make check`
**2 369 / 2 skipped**, потрачено $0.00. Отчёт — `docs/reports/phase6a.md` (Dv335–Dv340).
Следом — `6b` (UI) и `cycle2-prep-b` (сбор). День — [[2026-08-15]].

**Предыдущий срез:** 2026-08-15 (11:18) — `cycle2-prep-a` ($0): правило 3.19 вшито в очередь
инференса, проекция батч-паритета написана. Отчёт — `docs/reports/cycle2-prep-a.md` (Dv330–Dv334).

**Предыдущий срез:** 2026-08-14 (закрытие дня) — **ФАЗА 5c2 ЗАКРЫТА.** За день три контракта:
`5c2-run` (платный, куплено ВСЁ окно за $7.5309), `5c2-validate-prep` ($0) и `5c2-close` ($0).
Сидение 3.18 (6) состоялось, **обе половины РАТИФИЦИРОВАНЫ** (6 постов / 36 позиций и 5 из 5
комментов, спорных 0, ORDERS 0), рулинг сидения = **SPEC амендмент 3.19**. `witness_phase_ledger`
вшит в `finalise` драйвера. Phase 4: **$31.4493 из $33.00**, остаток **$1.5507**. `make check`
**2 332 / 2 skipped**, дерево чистое. Отчёт — `docs/reports/5c2-close.md` (Dv325–Dv329), ADR —
[[5c2-closed-the-sitting-and-the-shelf-life-redesign]]. Полный день — [[2026-08-14]].

## 🔥 What's Hot

**🔄 ТЫ ЗДЕСЬ (рукой тимлида в STATUS, приземлилось на закрытии дня): джойнт-планирование цикла-2 и
Фазы 6.** Фаза 5 закрыта, хроника до 12.08 в STATUS сжата — полная история в git этого файла.
Остатка $1.5507 не хватит ни на один платный цикл; линию поднимает ТОЛЬКО оператор. Все $0-задачи
ниже можно делать не дожидаясь.

**ФАЗА 6a СДЕЛАНА (15.08, `phase6a`) — слой данных командного центра стоит.** SPEC вырос
**амендментом 3.20** (числа только из артефактов через слой агрегатов · SQLite — дом агрегатов ·
UA/EN и словарь метрик · выводы кодом · цены из комментов не в промо · **Маркетопт на промо-поверхности**).
`data/derived/pulse.db` пересобирается из `data/derived/` за секунду и НИКОГДА не коммитится;
дашборд читает ТОЛЬКО `results/dashboard_data_w1.json` (108 КБ, закоммичен, две пары байт-в-байт).
Гейт сходимости исчерпывающий: `aggregates.mirror()` пересобирает пять блоков
`window_summary_5c2.json` из SQL — **902 из 902 листьев**, 0 лишних, 0 пропущенных, плюс 30
объявленных общих пар. Сборка ОТКАЗЫВАЕТ, а не предупреждает. Восемь метрик в
`config/metrics.yaml` (UA/EN, биекция с экспортом в обе стороны), семь `NOT_COMPUTABLE`-заглушек с
условиями разблокировки. **6b (UI) строится ТОЛЬКО на этом файле.**

**Числа окна-1, которых раньше не было (из слоя, не из прозы).** Все **1 361** бестекстовых строк
размечены `neutral` — все до одной; поэтому NSR прыгает **0.0770 (купленная) → 0.1053 (платимая),
+37%**, и headline дашборда — платимая выборка (3.19 (2)). **`retail_official` — единственный
сегмент с отрицательным NSR** (−0.1111 на 234 строках), community-сегменты тёплые. Поправка на
сарказм двигает **3 строки** (64 из 67 саркастичных и так негатив). `regional` — 3 канала,
13 маркеров, 9 позиций, **0 комментариев**. SoV меряется на **11 строках из 5 075** — 0.22%.

**Правило 3.19 ВШИТО (15.08, `cycle2-prep-a`).** Бестекстовые комментарии исключаются из очереди
инференса ДО оплаты — правило ОЧЕРЕДИ, не удаление: строки остаются собранными, под вотермарком и
посчитанными, `loop.queue_depth` (инструмент переписи) не тронут, окно 09.08 остаётся как куплено.
Единственный предикат — **`market_pulse.loop.has_text`**, поднят из инлайна
`scripts/window_summary_5c2.py:198`; второго определения нет и не должно появиться. `strip()` и
`== ""` проверены на окне с ОБЕИХ сторон (sent и source) — ровно 1 361 строка в каждом случае,
расхождений 0. Считает и печатает рядом `text_less_skipped`. `scripts/run_5c2.py` наследует правило
через `loop.queued` без правки.

**⚠️ НОВЫЙ ШОВ: перепись и печать теперь считают РАЗНЫЕ популяции, и платный драйвер этого не
видит.** `loop.queue_depth` (чем считает `census_5c2.py`) слеп к тексту, `loop.queued` — нет.
`run_5c2.restrict` (`:250`) — просто фильтр, а отказ на `:295` про пару «пак/строка», не про
короткую очередь. Регистрация, собранная из переписи на 5 075, будет встречена очередью в 3 714,
купит 3 714 и упрётся только в `window_summary_5c2.assert_populations` — ПОСЛЕ трат. **Следующая
pre-registration обязана регистрировать ОПЛАЧИВАЕМУЮ популяцию, а не собранную.** Красная линия
стоит: `tests/test_run_5c2.py::test_a_registered_selection_is_met_by_a_smaller_queue_and_nothing_raises`.

**⚠️ Правка `src/market_pulse/loop.py` роняет ДВА запечатанных рекорда.**
`results/window_summary_5c2.json` и `results/validate_5c2_pack.json` держат его sha в
`producer.borrowed` (и sha `scripts/window_summary_5c2.py` тоже). Рекорды НЕ перепинены: гварды
восстанавливают байты через `git show d69c812b206faff15f5a12adff113a5ef1335154:` и проверяются в обе
стороны (`SEALING_COMMIT` в `tests/test_window_summary_5c2.py`, импортируется в
`tests/test_build_validate_pack.py`). Следующая правка loop.py — грепни пины ПЕРЕД первым Edit.

**Правило регистраций и жребиев** — «рядом с каждой ценой ИМЕНУЙ выборку замера; рядом с каждым
жребием МЕРЬ ранг» — живёт в `.claude/rules/registrations-and-draws.md`, path-scoped, 0 токенов на
старте. Должно подхватиться при работе с `write_prereg*`, `projection_*`, `build_*_pack*` — globs
проверены по реальным файлам, сама инжекция в сессии написания НЕ наблюдалась (правило грузится
один раз за сессию). Не увидел его в system-reminder, редактируя регистрацию, — открой руками.

## ⏭️ Next

**Кандидаты цикла-2 в порядке ценности — список тимлида из STATUS:**

1. **Деньги** — на счету ~$3.55, Phase 4 = $31.4493/$33.00. Пополнение или новый кап; без этого
   платного контракта нет.
2. **Батч-паритет — СПРОЕКТИРОВАН, решение за оператором.**
   `results/batch_cycle2_projection.json`. Из записей выводится НЕРАВЕНСТВО: шаг с batch 16 требовал
   **23.99 ГиБ** сверх весов, у 4090 24 ГБ их **3.99** — короче в **6.02×**, поэтому 16/8/4/3
   исключены и единственный кандидат — **batch 2**; влезет ли он, **НЕ ИЗМЕРИМО** без живого пробника.
   Главный риск не память, а ОТВЕТЫ: при batch 16 разошлись **6 строк из 666**, тогда как на
   24-строчном карве все размеры были байт-в-байт. Пробник: фикс **$0.1520** + **$0.0013025**/строка
   (потолок по batch 1); арм 758 с контролем — **$2.1266**. Окупаемость: −30% даёт **$4.3536** на
   истории 11 143 и **$1.4511** на одном окне после 3.19; −50% — **$7.2574** / **$2.4189**.
   **Само правило 3.19 уже сэкономило $1.7727 на окне и бесплатно — больше, чем дал бы −30%.**
3. ~~**Скип-правило 3.19 в петлю**~~ — **СДЕЛАНО 15.08** (`8d47fb3`), см. выше.
4. **Сбор листовок Сільпо / Varus / Маркетопт** — 3.18 (7)(d) расширен **амендментом 3.20 (6)**
   (рулинг оператора 15.08: Маркетопт обязателен). Бесплатно, не начат. Идёт в `prep-b` вместе с
   докачкой корпуса. В окне-1 листовочные СТРАНИЦЫ есть только у АТБ; у Сільпо/Varus/Маркетопта
   позиции только из текстов постов — это записано в
   `dashboard_data_w1.json :: not_computable.leaflet_depth_for_silpo_varus_marketopt`.
5. **Докачка корпуса** — сборка стоит с 08.08.
6. **История 11 143** — вход бесплатен, ~13 ч на текущей скорости, ЖДЁТ батча.
7. ~~**Приёмка `5c2-close`**~~ — **RESOLVED 2026-08-15:** тимлид ратифицировал маршрутизацию
   правила `[model]` в `.claude/rules/` (третий дом вместо двух названных контрактом, Dv327).
   `docs/reports/5c2-close.md` принят.

**Четвёртый долг, который не в списке:** цена страницы листовки **10.408 с/стр (n=159)** — вход
следующей регистрации, старые записи НЕ перескориваются.

## 🚧 Blockers

**Ничего не блокирует работу.** `phase6a` исполнен, суита зелёная (**2 369 / 2 skipped**), потрачено
$0.00. Ждём приёмки `cycle2-prep-a` и `phase6a`; дальше — `6b` (UI на экспорте) и `cycle2-prep-b`
(сбор). `docs/PLAN-phase6-command-center.md` — файл тимлида, его законная часть уже уехала
амендментом 3.20.

**⚠️ Деньги.** Phase 4: **$31.4493 из $33.00**, остаток **$1.5507** — на полный цикл НЕ хватит,
линию поднимает только оператор. Остаток ВЫВОДИТЬ (`PHASE_CAP_USD - spent_usd`), а не читать из
`sessions[-1].remaining_usd` ([[the-field-true-under-the-old-constant]]). Записи леджера фазы
**anchor-relative** — `spent_usd` по сессиям НЕ суммируется.

**⚠️ Зарегистрированная цена страницы листовки известна НЕВЕРНОЙ.** 4.2794 с в
`results/sku_b_positions_skub2.json` снята с постеров; полная популяция из 159 страниц стоит
**10.408 с**. Не переиспользовать без рулинга.

**⚠️ Очередь комментов читает 0, а не 11 143.** Вотермарк накрыл всё старое. Строки на диске целы,
но контракт, который захочет историю, обязан САМ сбросить поле `inference` в
`data/loop_cursor.json` ([[a-watermark-past-a-window-buries-the-backlog]]). Побочный эффект: смоук
по реальному стору печатает нулевой сплит 3.19 — это не дефект правила (Dv332). **Сколько из
11 143 бестекстовые — НЕ посчитано ни в одном якоре**; доля окна 26.8% на историю НЕ переносится
(другая выборка), а сам подсчёт бесплатен — кандидат в `prep-b`.

**⚠️ `build_validate_pack.py` перезаписывает пакет без `--force`-гарда, а его sha ЗАПИНЕН.**
`results/validate_5c2_returns.json` отвечает ровно на `2fad5339…`; перестройка пакета (даже
идентичная по строкам, но не по байтам) уронит возврат сидения с «the sitting read …». Вердикты
теперь живут в возврате, а не в пакете, так что скелет терять нечего — но пин уронить легко.

**Якоря, которые не трогают:** `results/spend_5c2run.json` — закрытый якорь сессии, драйвер
отказывается его переписать. `results/spend_sku_b*.json`, `results/spend_skub2.json` — тоже
закрыты. Том биллится всегда: **≈ $0.012/ч**.

**Recorded rather than open:** том CA-MTL-3 удалён, его **~$0.24/day** больше не капают — литерал
нагруженный, не украшение, и он ОБЯЗАН стоять ровно так, по-английски со слэшем:
`scripts/volume_calc_5c1.py :: quoted(HOT, "~$0.24/day", 0.24)` грепает его ИЗ ЭТОГО ФАЙЛА как вход.
Перевод слова `day` уже уронил девять тестов один раз (12.08). Второй такой литерал —
`80 GB is about what the` в Footguns. Подушный дамп арма A из 4.5h2 потерян навсегда
(`results/predictions/LOST.md`).

**SUPERSEDED, оставлено чтобы старую строку не прочли как текущую:** `results/parity_verdict_5b.json`
говорит, что ни один serverless-эндпойнт здесь не доходит до воркера — верно на **2026-08-06** и
опровергнуто с тех пор (паритет 758/758, [[srv2-program-close]]; и 5c2-run купил на serverless
5 278 строк).

## ⚠️ Footguns for the next run

- **Блок `amendment-index` в `docs/SPEC.md` ПРАВИТЬ НЕЛЬЗЯ** (Dv335). Он один из десяти имён
  `write_prereg_5c2.KEEP_BLOCKS`, то есть его байты ВНУТРИ запечатанного пина
  `results/prereg_5c2_run.json`: правка выводит закон в `a39c05d5…` против запиненного `3dd43923…`.
  Указатель поэтому отстал на два амендмента (3.19 и 3.20 — каждый сам себе индексная запись
  внутри своего блока), и это сделано намеренно. Новый амендмент = новый маркированный блок
  + строка в `BLOCKS_TODAY` + имя в перечислении `tests/test_sku_prereg.py`. Четыре детали, не три.
- **Любая правка producer'а роняет `results/dashboard_data_w1.json`.** Экспорт держит sha восьми
  файлов в `provenance.producers` (включая `loop.py`, `prompts.py`, `window_summary_5c2.py`), а тест
  сравнивает закоммиченные байты с тем, что продюсер пишет СЕГОДНЯ. Тронул любой из них — прогони
  `PYTHONPATH=src python3 scripts/export_dashboard_data.py` и закоммить файл в том же коммите.
  Порядок: `ruff format` СНАЧАЛА, генерация ПОТОМ.
- **The DRIVER writes a `contract:` provenance string nobody checks** (Dv176 — the bar producer's
  twin, closed as Dv170, is now a constant with a test). `positions_gm4_skub.head["contract"]` puts
  `docs/PROMPT-sku-b-v3-prep.md deliverable 2; … 3.17 (9), (10), (11)` INTO every run record,
  including v4's, and omits (12). Nothing reads the field; fix it in the next contract that already
  touches the driver, never mid-flight on the money path.
- **The staging class v3 priced at $0.24/h is not offered in EU-RO-1 any more** (Dv177). Cheapest
  with stock is L4 at **$0.49/h** = $0.008/min, so a pod eats a tight cap headroom twice as fast:
  build the bundle and write the staging script BEFORE `pod create`, and price the pod from its own
  clock (the balance will still read $0.0000 — Dv166).
- **`runpodctl ssh info` answers with `ip`/`port`, not `host`** (Dv178). A readiness loop grepping
  for the wrong key runs its full timeout against an answer that was already complete — 55 s of
  billed pod, and it looks exactly like a slow resource.
- **A registered probe can be a correct measurement of the wrong page** (Dv180). (11)(c)'s unsent
  page reproduces to 1.2% across two sessions and still over-prices the population **3.64×**,
  because the sent set is the first six pages of each leaflet and the unsent ones are the dense
  grids. Price the next go/no-go from `4.0161 s/page (n=91)`, not from a probe.
- **A missing `results/sku_b_pair_verdicts.json` puts bar 2 silently back to PENDING** and the bar
  producer still writes a record — the closure just goes `UNDETERMINED`. That is deliberate (it is
  the state the bar was in for the whole pilot) and the guard is a test asserting the read exists
  and that the record on disk is the scored one. Delete or move that file and the guard, not the
  producer, is what tells you.
- **`knowledge/hot.md` is grepped as a priced INPUT.** `volume_calc_5c1.py` needs the literals
  `~$0.24/day` and `80 GB is about what the` verbatim — translating or reformatting either reddens
  nine tests. Run `make check` after editing this file, not only after editing code.
- **The caption endpoint cannot be made by editing the srv-2d template — `settings()` refuses it, by
  design.** `SERVING_CONFIG=CAPTION` beside `ADAPTER_DIR` or `MERGED_DIR` raises before the model
  loads. Create a NEW template with the three variables of `runbook_vis_b.md` §A.1 and nothing else.
  The refusal is against `serve_handler.ADAPTER_ENV` as a whole, so a third such variable still fires.
- **A RUNNING WORKER HOLDS THE CODE IT BOOTED WITH — a `git merge` on the volume reaches nothing.**
  vis-b paid $0.1581 to learn it. `serverless update` does not restart a worker, `--idle-timeout 60`
  does not stop one that failed a job, and **only `serverless delete` stops it**. **Stage the volume
  BEFORE the endpoint exists** and treat the code as frozen from the first request onward.
- **A failing serverless worker bills exactly like a working one** — srv-2b's ran 31 min at
  $0.00031/s with its job stuck in the queue. Watch **the first job's status**, not worker health.
  Also: `runpod_guard` walks pods and volumes only, so **serverless spend is invisible to it**; and a
  remote `pgrep -f` inside an ssh command **matches its own shell**.
- **A `git fetch` naming a missing ref leaves the OLD `FETCH_HEAD`,** so the merge "succeeds" and
  moves nothing (`Already up to date.` is also a no-op's signature). End every deploy with a
  **content** check of what the runtime executes; `git bundle list-heads` names the real ref.
- **`smoke_5b.py --record` defaults to `results/serving_5b.json` — the pod's cost anchor** ($0.5993/1000,
  $0.4611/pass, 4.071 s/row). Always pass an explicit path.
- **RunPod's request policy is in MILLISECONDS and every briefing writes seconds.**
  `serving.execution_policy(3600, 7200)` is the one conversion point; the endpoint's own
  `--execution-timeout` takes **seconds** and stores ms. Set the endpoint-level timeout too.
- **`assert_runtime_matches` pins three libraries and cannot be taught a fourth** — it skips any the
  frozen anchor (`results/verdict_45h2.json`) lacks, so a `peft` entry would pass every test and never
  fire. peft's pin is in `scripts/runbook_srv2b.md` (**0.20.0**), only REPORTED at runtime.
- **`relabel.read_ledger` writes a provenance string that is wrong for anything past phase 4** — for a
  5c1 phase name it renders `docs/PROMPT-5.c1captions.md` INSIDE a money record. Copy
  `scripts/caption_atb_5c1.py`'s own three-key anchor, not the helper.
- **A caption's price is not stable across phases: 4.5g2 measured $0.000483/post, the pilot paid
  $0.000948.** Same model, endpoint, prompt and images-per-request. Any projection from an old record
  carries a factor-of-two error bar; reprice from the most recent run that actually paid.
- **Two Telethon clients must never share `marketpulse.session`.** `seconds_until_next_join` reads the
  last timestamp in `results/joins_5c1.jsonl`, so the fifteen-minute gap is wall-clock and survives a
  restart — `--join --max 1` can be fired between phases, but a `--join` left in the background while a
  collection runs puts two clients on one SQLite file. Interleave, never overlap.
- **A bare `--posts` or `--comments` resolves the WHOLE registry** — `run()` calls `get_entity(handle)`
  before it checks `comments_enabled and not watch`. That request is what the 2026-08-07 FloodWait wall
  was on. Every collection run carries `--only`.
- **`language_census_5c1.py` and `market_screen_5c1.py` refuse their own default path.** Their shipped
  records are dated measurements a ruling cites and two of those channels have LEFT the registry. Pass
  `--out` with a new path; the day-2 passes are the `_day2.json` pair.
- **`apply_gate_rulings_5c1.remove_sources` stamps `removed 2026-08-07` from a hardcoded literal.** A
  test pins the string; the next channel that leaves the registry gets yesterday's date on its tombstone.
- **The harvest's «already ours» marker does not know the canon's «Исключены — 12» table.**
  `late_batch_5c1.known_handles()` reads the registry and the 5c1 gate record only, so
  `results/harvest_mothers_ua.json` offers back @prikorm_kids_menu — dead by the 06.08 ruling.
- **A pod has no template, so it has no configuration** — whatever boots it carries the worker's
  environment (`SERVING_CONFIG`, `ADAPTER_DIR`, `BASE_WEIGHTS`, `MODEL_REVISION`). 5c2's pod runner
  inherits this: the loop is what must pass them now.
- **Read `runpodctl gpu list` before spending a create call.** Availability is reported per datacenter;
  `datacenter list` answers nothing. A **network volume pins the datacenter**, and SPEC §3.11 (1) makes
  the CLASS the contract: A6000 anywhere, A40 in-class with the card in provenance, **never A100**.
- **`parent_msg_id` and `reply_to_msg_id` are different id spaces, and comparing them looks fine.** One
  is the channel post, the other a message in the discussion group, so `reply_to != parent` is true for
  essentially every row. The thread head is the **smallest** reply target in the thread. Sanity gate: a
  reply family near the corpus size means the discriminator is wrong, not the corpus.
- **Never `git add -A` here.** Team-lead files land in the tree mid-session and the next queued
  `docs/PROMPT-*.md` arrives untracked without warning. Stage by path. The trap has fired with every
  queued prompt since `docs/PROMPT-4.5g4.md`.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. If the pod exists only for one session, **delete** it
  (`runpodctl pod delete` — there is no `pod terminate`), do not stop it. A stopped pod is not a stopped
  bill, and `runpodctl pod list` shows running pods only — use `pod list -a`.
- **Network volumes live in a different datacenter set than the A6000 does** (`EU-SE-1` had the best
  A6000 stock and takes no volumes); pick on the intersection or pay for a second volume. And
  `RUNPOD_POD_ID` is not inherited over ssh — export it or the record cannot name its machine.
- **The RunPod PyTorch image's python is PEP 668 managed.** Use `python3 -m venv --system-site-packages`
  so the image's CUDA-matched torch is reused rather than re-downloaded.
- **Python buffers stdout when it is redirected to a file.** `loss.jsonl` is the live view; `python3 -u`
  fixes the log itself.
- **`results/spend_phase4.json` is the $25 cap's anchor and must not be regenerated.** Delete it and the
  counter silently restarts at today's balance. The guard also refuses when the balance is *above* the
  anchor — a mid-phase top-up is an operator decision.
- **`results/baselines.json` is append-only and never hand-edited.** Numbers reach it only through the
  scorer; `scripts/show_results.py` only reads. A hand-typed number there is invisible.
- **A results record cannot name the commit that contains it**, so provenance is `commit` + the `dirty`
  paths at run time; the runner shouts if any is under `src/`, `scripts/` or `config/`.
- **A run that trips the cap writes no record** — a partial run must never become a gate anchor. Do not
  re-run with a bigger `--max-run-usd` to get the record.
- **A ceiling lifted by the operator is not a ceiling lifted in code.** `train_xlmr_baseline.py` refuses
  to train above `--time-budget-min` and exits **3**, which reads exactly like a crash. Grep your own
  guards before any unattended launch.
- **Batch 1 is PERMANENT, and "re-measure it" is no longer the answer.** The authorised re-measurement
  ran 2026-08-06 and failed; SPEC §3.11 (2) fixes serving at batch 1. Only a NEW pre-registration may
  re-open it. [[5b2-batch-measurement]]
- **`add_special_tokens=False` is load-bearing and now asserted** (Gemma 4's chat template emits `<bos>`
  itself), and **Gemma 4 has a thinking channel** — `enable_thinking=False` + `add_generation_prompt=True`,
  passed explicitly, or `parse_reply` reads the first brace inside the reasoning text.
- **A `--probe` is not a smoke test unless it prints rows.** Aggregate counts are identical whenever two
  configurations merely parse. Diff the per-row prediction lines and guard with `test -s` — `diff` on two
  empty files is silent success.
- **A print statement can crash a run after the record is written.** Drive `main` through `--record-out`
  with a stub: `--smoke` returns before the record is built and `--probe` before it is written.
- **`docs/STATUS.md`, `docs/SPEC.md`, `docs/PRODUCT.md`, `docs/PROMPT-*.md` are team-lead files.** Read
  and commit, never edit. Phase-end facts go to the daily log or `implementation-notes.md`. The refusal
  reads "File is in a directory that is denied", but the rules are file-scoped: the rest of `docs/` is
  writable.
- sklearn lives in the `baseline` extra and torch/transformers in `xlmr` — no test may import either, or
  `make check` stops being runnable on a bare checkout. And `RAW_STORE_SALT` in `.env` must never be
  rotated: a new salt orphans every `sender_anon_id`.

## 🐞 Known harness bug

Fixed 2026-07-28: `knowledge/templates/daily-log.md` now carries `{{DATE}}`, the placeholder
`scripts/brain-session-end.py` actually substitutes; `tests/test_templates.py` keeps the pair honest.
