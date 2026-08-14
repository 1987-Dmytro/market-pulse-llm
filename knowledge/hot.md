<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-08-14 17:27:11 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
c02f0ad fix(5c2-validate): six defects the adversarial review pass confirmed
1532102 docs(report): the redraw, the 1 361 text-less comments, and four corrections
d69c812 fix(5c2-validate): a correlated draw, and a quarter of the comment leg with no text
12aba50 docs(report): 5c2-validate-prep -- the pack is buildable, and Dv307 was closed by a side effect
8b6cbf4 feat(5c2-validate): the sitting pack -- drawn under seed 42, original beside verdict
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `the-d-cut-and-the-fourth-kind.md` — The post leg's population is the D cut — 44 of 349 — and the marker row that makes its resume exact
- `5c2-stop-ruling-and-cap-33.md` — The prep-c2 STOP is answered by raising the line, not by cutting the window — and the records written under the old cap are never re-scored

## 📅 Recent daily logs

- `2026-08-14.md`
- `2026-08-13.md`
- `2026-08-12.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->
# Hot Cache — curated

**Last update:** 2026-08-14 (закрытие дня) — **`5c2-run` + `5c2-validate-prep` ИСПОЛНЕНЫ.** Ран
купил ВСЁ окно (5 075 комментов + 159 страниц + 44 поста, 5 423 строки улик, ноль неполных) за
**$7.5309** из капа $8.00; prep построил агрегаты и пакет сидения за **$0**. Phase 4:
**$31.4493 из $33.00**, остаток **$1.5507**. `make check` **2 309 / 2 skipped**, дерево чистое.
Отчёты — `docs/reports/5c2-run.md` (Dv303–Dv315) и `docs/reports/5c2-validate-prep.md`
(Dv316–Dv324). Полный день — [[2026-08-14]].

## 🔥 What's Hot

**ФАЗА УПИРАЕТСЯ В ОДНО: сидение с оператором.** `results/validate_5c2_pack.html` — открыть **из
`results/` внутри чекаута** (картинки лежат по относительным путям в `data/`, вне git). 6
листовочных постов (56 страниц, 36 позиций) + 5 комментов, seed 42, оригинал рядом с вердиктом,
каждая строка подписана агрегатом из `results/window_summary_5c2.json`. Тимлид заполняет `findings`
в `results/validate_5c2_pack.json` ВО ВРЕМЯ сидения; вердикты → ORDERS класса REVIEW 3.16 (1),
никогда не пересчитанные числа и никогда не сдвинутая планка. ~45 минут.

**1 361 из 5 075 комментов (26.8%) ушли в модель с ПУСТЫМ блоком `<comment>`** — стикеры, фото,
голосовые. Все головы ответили, все 1 361 вернулись без интенции: **треть
`rows_with_no_intent: 3944` — не про то, о чём говорит аудитория.** @matusi_ukr несёт 1 172 из них,
43% собственных строк. Ни один счётчик рана этого не видел; нашлось при восстановлении
ОТПРАВЛЕННОЙ строки из `rendering` ([[rebuild-the-input-and-compare-bytes]]).

**Жребий может быть воспроизводимым, невыбранным — и всё равно коррелированным.** Один
`Random(42)`, пересеянный на каждую страту, отдаёт ОДИН индекс пулам одной битовой длины: три из
пяти комментов сели на ранг **163** (пулы 242/223/222). Видно только по РАНГУ — ни запись, ни
тесты, ни рендеринг показать этого не могли. Seed теперь пер-стратный
([[a-reproducible-draw-can-be-correlated]]).

**Цена настолько представительна, насколько представительна её выборка.** Один эндпоинт, две ноги:
страница листовки 4.2794 с → **10.408 с** (+143%), строка комментария 4.262 с → **4.247 с**
(−0.4%). `idle_share` 0.059/0.015 исключает транспорт. Комментарий мерили на 758 строках популяции,
страницу — на 108 ПЕРВЫХ страницах листовок, то есть на постерах. **Ран доехал только благодаря
консервативному углу** ноги комментов ([[a-price-is-as-representative-as-its-sample]]).

**Отклонение датируют, а не перечитывают.** Dv307 («отказ рукопожатия не пишет леджер, не
починено») был верен про ревизию, к которой написан, и ложен три коммита спустя: `git log -S` дал
`79ae380` — крашевый фикс Dv309, ВНУТРИ платной сессии; `SystemExit` наследует `BaseException`, и
дыра закрылась побочным эффектом ([[a-deviation-is-dated-not-just-true]]).

**Число, набранное руками, ломает не гейт, а сумму.** `--already-usd 0.8451` прошло свой гейт (GO
при обоих значениях), но `6.7079 + 0.8451 = 7.5530` против итога сессии 7.5309, тогда как
`6.7079 + 0.8230 = 7.5309` до цента ([[the-hand-typed-number-fails-the-total]]).

## ⏭️ Next

0. **ШАГ 0 — SPEC 3.19 приземлился ВО ВРЕМЯ закрытия дня и суита от этого КРАСНАЯ.**
   `docs/SPEC.md` + `docs/STATUS.md` не закоммичены. Закоммитить оба **по путям** (файлы тимлида:
   читать и коммитить, никогда не редактировать), затем добавить `amendment-3.19` в `KEEP_BLOCKS`
   и перевывести стрипнутый закон — запечатанные прережки НЕ перепинивать
   ([[a-law-that-grows-loudly]]). Шесть падающих тестов — это проектное поведение: перечисление
   блоков литеральное, чтобы новый амендмент не приземлился незамеченным.
1. **СИДЕНИЕ 3.18 (6)** — см. выше. Фаза 5c2 без него НЕ закрывается.
2. **Приёмка `5c2-validate-prep`** — `docs/reports/5c2-validate-prep.md`.
3. **После сидения** — закрытие фазы 5c2 с ретро; телли тегов Dv303–Dv324.
4. **Авторизовано, не начато:** сбор листовок сетей помимо АТБ — отдельная **$0**-задача
   (3.18 (7)(d)).

**Открытые вопросы тимлиду (все в двух отчётах):** (1) у комментного инструмента НЕТ бренд-головы —
сидению показывают детерминированный матчер watchlist, 11 строк из 5 075 (Dv316); (2) показывать ли
извлечённую старую цену на столе сидения (Dv318 — сейчас показывается с флагом); (3) что делать с
1 361 бестекстовой строкой (Dv324); (4) форма записи ЗАПОЛНЕННОГО сидения — правка на месте или
новый файл по образцу `read_sitting_returns.py`; (5) цена страницы листовки 10.408 с как
зарегистрированная цена цикла; (6) кто вызывает `witness_phase_ledger.py`.

## 🚧 Blockers

**⚠️ СУИТА КРАСНАЯ И ДЕРЕВО ГРЯЗНОЕ — не из-за моих коммитов.** Все 11 коммитов сессии зелёные;
краснота пришла с рукой тимлида (SPEC 3.19), приземлившейся во время закрытия. Измерено: с
откаченными `docs/SPEC.md` + `docs/STATUS.md` — **2 309 passed / 2 skipped**, с ними — **6 failed**,
все на пинах/стрипе. Файлы восстановлены байт-в-байт. Лечение — шаг 0 выше.

**SPEC 3.19 (рулинг по Dv324), знать перед следующим циклом:** бестекстовые комментарии
ИСКЛЮЧАЮТСЯ из очереди инференса ДО оплаты — правило очереди, не удаление; распределения
отчитываются на строках С ТЕКСТОМ, бестекстовый счёт печатается рядом отдельным классом; окно 09.08
остаётся как куплено, ничего не перескоривается.

Кроме этого — **ничего не блокирует**: оба контракта исполнены, деньги сведены, консоль пуста.

**⚠️ Деньги.** Phase 4: **$31.4493 из $33.00**, остаток **$1.5507** — на полный цикл НЕ хватит,
линию поднимает только оператор. Остаток ВЫВОДИТЬ (`PHASE_CAP_USD - spent_usd`), а не читать из
`sessions[-1].remaining_usd` ([[the-field-true-under-the-old-constant]]). Записи леджера фазы
**anchor-relative** — `spent_usd` по сессиям НЕ суммируется.

**⚠️ Зарегистрированная цена страницы листовки известна НЕВЕРНОЙ.** 4.2794 с в
`results/sku_b_positions_skub2.json` снята с постеров; полная популяция из 159 страниц стоит
**10.408 с**. Не переиспользовать без рулинга.

**⚠️ Очередь комментов читает 0, а не 11 143.** Вотермарк накрыл всё старое. Строки на диске целы,
но контракт, который захочет историю, обязан САМ сбросить поле `inference` в
`data/loop_cursor.json` ([[a-watermark-past-a-window-buries-the-backlog]]).

**⚠️ `scripts/witness_phase_ledger.py` никто не вызывает автоматически.** Следующая платная сессия
снова оставит леджер молчащим, пока `finalise` драйвера его не вызовет.

**⚠️ `build_validate_pack.py` НЕ проверяет заполненные `findings` перед перезаписью.** В отличие от
`build_sitting_pack.py` у него нет `--force`-гарда. Разница в риске: пакет **закоммичен**, так что
HEAD восстановит вечер работы, — но после сидения запускать его повторно нельзя без коммита
заполненного файла.

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
