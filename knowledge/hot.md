<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-08-13 18:33:08 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
f8ba5bf docs(report): the commit list closed
b6a9c86 docs(report): 5c2-prep-c3b -- REQUIRED checked on the tuple, not the assignment line
16a4da9 chore(vault): the 5c2-prep-c3b session tail -- the day's log and hot.md
82d5483 docs(report): 5c2-prep-c3b -- the D cut, the fourth kind, and the sealed numbers
e64398d docs(decision): the D cut and the fourth evidence kind
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `the-d-cut-and-the-fourth-kind.md` — The post leg's population is the D cut — 44 of 349 — and the marker row that makes its resume exact
- `5c2-stop-ruling-and-cap-33.md` — The prep-c2 STOP is answered by raising the line, not by cutting the window — and the records written under the old cap are never re-scored

## 📅 Recent daily logs

- `2026-08-13.md`
- `2026-08-12.md`
- `2026-08-11.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->
# Hot Cache — curated

**Last update:** 2026-08-13 18:15 — **ДЕНЬ ЗАКРЫТ.** Шесть контрактов `5c2-prep-{a,b,c1,c2,c3a,c3b}`,
65 коммитов (09:47 → 18:06), **потрачено $0.00**. `make check` **2235 / 2 skipped** (было 2025 утром),
`ruff format --check` — 262 файла чисты, дерево чистое. Приняты: `-a`, `-b`, `-c1`. Сданы, ждут
приёмки: `-c2` (STOP отвечен рулингом), `-c3a`, `-c3b`.
Phase 4: **$23.8310 из $33.00**, остаток **$9.1690**. Полный день — [[2026-08-13]].

## 🔥 What's Hot

**Прекурсор 5c2 закончен. Следующее — платная сессия.** Утром петля умела только планировать сбор;
вечером у неё три прохода (комментарии, страницы листовок, текст поста), у всех трёх одна форма
улики и один шов, окно посчитано, цена снята с платных замеров, а платная сессия пре-регистрирована
и запечатана.

**🎯 `results/prereg_5c2_run.json` — прережка `5c2-run`, читать первой.**
5 075 комментов + **159** страниц листовок + **44** поста = **$7.8546** с дрейфом → кап сессии
**$8.00** против остатка $9.1690 (запас $1.1690). Стенные часы 6.42 ч, 26 джобов по 900 с при одном
воркере; один джоб на таймауте стоит $0.2843 — 3.17 (10)(c) удовлетворена. Каждое число пинится
РАВЕНСТВОМ (3.18 (7)(f)); `fits` — проверка РЯДОМ, не сам пин. Выборки пинятся не только размером:
комменты — **девятнадцатью** поканальными `ids_sha256` (так их пишет ценз; хэш-от-хэшей никто в репе
не воспроизведёт), посты — хэшем оставленных id. Резюм = вотермарк + четвёртый вид улики.

**⚖️ Четыре рулинга дня** (SPEC 3.18, ADR [[5c2-stop-ruling-and-cap-33]] и
[[the-d-cut-and-the-fourth-kind]]):
- кап фазы **25 → 30 → 33**, денег не добавляли (баланс 11.1690), поднята искусственная линия;
- **STOP prep-c2 закрыт**: якорь 2026-08-09 ратифицирован, сессия покупает ВСЁ окно двух ног
  (клаузы обреза не существует), листовки = **159 страниц на диске**, а не 78 из окна;
- **D-срез** — население ноги постов: `official_retail`/`aggregator` ИЛИ `currency` на evidence,
  **44 из 349**, ноль рецептных каналов. Это и делает наследование `POST_PRICE_ORIGIN =
  retail_leaflet` защитимым;
- **четвёртый `evidence.KINDS`** — `post_text`, пустой `KIND_FIELDS`, маркер ПОСЛЕДНИМ на пост.

**⚠️ Клауза, которая вяжет ТИМЛИДА.** Записи под старым капом НЕ перегенерируются.
`projection_5c2.json :: whole_window.fits: false` **остался зелёным**, пока смысл переворачивался:
те же $7.6870 теперь влезают в $9.1690. Ничего бы не покраснело. Развязка — образец
`CAP_IN_FORCE`: тест пинит кап, ДЕЙСТВОВАВШИЙ на момент записи, утверждает его ОТЛИЧИЕ от живого и
несёт живую половину рядом.

**🔁 Три находки про «отвечено» — одна и та же форма отказа, три слоя.** Знать любому, кто добавит
писателя: (1) ключ хранилища был грубее строки — N позиций одной страницы терялись **внутри одного
`append()`**; теперь `dedup_key` = `row_id` при наличии, иначе `msg_id`, `StoreIndex.ids` —
пространство СООБЩЕНИЙ, `.keys` — СТРОК, очередь вычитает `ids`. (2) Маркер пишется **последним**:
`RawStore.append` пишет по файлу за раз, и строка-маркер, легшая первой, пережила бы падение, а её
позиции нет. (3) У ноги постов маркера не было вовсе — пост с ответом `[]` был неотличим от
неспрошенного; закрыто четвёртым видом.
[[the-store-key-is-coarser-than-the-row]] · [[the-marker-is-written-last]]

**📊 Числа окна** (якорь 2026-08-09, 2026-07-12…08-09). `results/census_5c2.json`: 5 075
неотвеченных комментариев, 9 158 постов, 5 773 с медиа, 78 страниц листовок в окне (корпус на
диске — 159 под 19 постами, один канал `@atb_market_official`).
`results/census_c3a_posts.json`: **349 постов проходят префильтр (3.81%)**, из них 328 несут размер
и только **29 — гривну**; четыре кулинарных канала = **71.6%** населения. Конъюнкция префильтра не
отличает «Кефір — 400 мл» в списке ингредиентов от оффера — это и вызвало рулинг (7)(g).
`results/postcut_c3b.json`: D-срез 44, $0.0581.
Цены ног — `results/projection_5c2.json`, обе с ПЛАТНЫХ serverless-сессий (srv-2d $1.4281/1000
строк и 4.262 с/строка; skub2 4.2794 с/страница и 2.8132 с/строка текста).

**🧭 Три правила артефактов, выученные за день.** (1) Записи ценза/проекции/прережки НЕ несут
`git`-блок: `git_state` кладёт внутрь `git status --porcelain`, и байты двигаются от ЧУЖОГО коммита
— измерено (`ec35644b` → `cbc05c84` при том же якоре). Провенанс = `producer.sha256` **плюс
`borrows`** — хэши модулей, из которых запись собрана. (2) Цитата берётся по УНИКАЛЬНОМУ якорю:
`quote_line` отказывает на любом количестве совпадений кроме одного. (3) Блок верификации
записывается ПОСЛЕДНИМ, после коммитов-правок по ревью — иначе он несёт хэш ревизии, которой ни у
кого нет ([[the-gates-evidence-outlived-its-artifact]]).

**📄 Два домашних правила процесса** (операторский аудит
`docs/reviews/2026-08-13-process-audit-and-self-improvement.md`, `affa8ca`): каждая Dv кончается
тегом `[cause: contract-gap | spec-gap | env | tooling | model | process]`, и отчёт кончается
секцией **Process signals** (≤5 строк).

## ⏭️ Next

**`5c2-run` — ОДНА платная сессия** под запечатанной прережкой, после приёмки `-c2`/`-c3a`/`-c3b`.
Ворота go/no-go 3.17 (10)(a) применяются без изменений, разогрев — на ПРЕДСТАВИТЕЛЬНЫХ входах
(3.17 (11)(c): 64×64-проба оценила страницу листовки в 1/3.5 правды и пропустила ран, который
обязана была отказать). Ноги 3.18 (2) проверяются на выходе самого окна при приёмке; нога, которую
там проверить нельзя, докладывается как НЕпроверенная, а не считается пройденной.

**`5c2-validate` — СИДЕНИЕ С ОПЕРАТОРОМ, и фаза без него не закрывается** (3.18 (6)). Пять листовых
постов и пять комментариев, оригинал рядом с вердиктом, отобранные ПО ЗАПИСАННОМУ СИДУ из выхода
самого окна, ~45 минут. Прережка перечисляет поля, которые ран ОБЯЗАН сохранить, ПОИМЁННО —
«ран сохраняет улику» удовлетворяется прогоном, сохранившим три поля. Прецедент
`results/predictions/LOST.md`: подушный дамп, потерянный навсегда.

**Авторизовано, но не начато:** сбор листовок сетей помимо АТБ — отдельная **$0** задача сбора,
никогда внутри платной сессии (3.18 (7)(d)).

**DEFERRED, всё ещё не решено:** нужна ли `carrier=comment` своя планка; полные 11 338 строк истории
(3.18 (4) — эта сессия покупает окно). Прережка v4 и B′ закрыты и не меняются.

## 🚧 Blockers

**НИЧЕГО НЕ БЛОКИРУЕТ.** Оба вопроса, стоявшие после c3a, закрыты рулингами. Деньги упирались —
линия поднята до $33.00, кап рана $8.00 против остатка $9.1690.

**Знать перед платной сессией:**
- **Остаток НЕЛЬЗЯ читать из леджера.** `spend_phase4.json :: sessions[-1].remaining_usd` = **6.1690**
  — верно про кап 30, и 3.18 (7)(b) запрещает перескоривать. Чтение поля отказало бы капу $8.00,
  который влезает. Выводить `PHASE_CAP_USD - spent_usd` = **9.1690** и печатать оба с их капами.
  `projection_5c2.budget()` читает это поле — не переиспользовать
  ([[the-field-true-under-the-old-constant]]).
- **Прережка держит ВСЕ ДЕСЯТЬ размеченных блоков SPEC**, а не два по прецеденту B′: 3.18 (7)(c)
  отправляет стоп-правила в 3.17 (10) внутри `sku-b-ratification-4`. Новый текст закона — только
  внутри своего размеченного блока (`amendment-3\.\d+` молча срезал бы будущий 3.19, поэтому
  продюсер отказывается на НАБОРЕ блоков). Запечатанную прережку не перепинивают
  ([[the-law-grows-inside-marked-blocks]]).
- **`--anchor` берёт ПОЛНЫЙ ISO.** Голая дата парсится как локальное время и даёт другое окно
  (9 160 постов); `refuse_to_move_the_anchor` смотрит только в файл `--out` и на свежем пути не
  срабатывает. Ловит пин выборки, не гвард.
- **`docs/ARCHITECTURE.md:324`** всё ещё описывает кап как «$25 Phase-4 GPU cap» — устарело с утра,
  оставлено намеренно (расширять скоуп запрещено).

**Бюджет — живое ограничение.** Phase 4 **$23.8310 из $33.00**, остаток **$9.1690** (читать гард
перед сессией, а не эту строку — Dv33: баланс отстаёт от ресурса на минуты-часы). Баланс
$11.1690436569 на 13.08. Позиционный инструмент от начала до конца стоил **$0.8796**;
`results/spend_sku_b*.json` и `results/spend_skub2.json` — закрытые якоря, не трогать. Том биллится
всегда: **≈ $0.012/ч**.

**Recorded rather than open:** том CA-MTL-3 удалён, его **~$0.24/day** больше не капают — литерал
нагруженный, не украшение, и он ОБЯЗАН стоять ровно так, по-английски со слэшем:
`scripts/volume_calc_5c1.py :: quoted(HOT, "~$0.24/day", 0.24)` грепает его ИЗ ЭТОГО ФАЙЛА как вход.
Перевод слова `day` уже уронил девять тестов один раз (12.08). Второй такой литерал —
`80 GB is about what the` в Footguns. Подушный дамп арма A из 4.5h2 потерян
навсегда (`results/predictions/LOST.md`). Две оплаченные строки, которых никто не claim'ит: под 4090
$0.5098 / 2470 с 08-08 (Dv38) и 30-секундная A4500 у srv-2b — ни одна не двигает число.

**SUPERSEDED, оставлено чтобы старую строку не прочли как текущую:** `results/parity_verdict_5b.json`
говорит, что ни один serverless-эндпойнт здесь не доходит до воркера — верно на **2026-08-06** и
опровергнуто с тех пор (паритет 758/758, худшее движение головы 0.0000, [[srv2-program-close]]).

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
