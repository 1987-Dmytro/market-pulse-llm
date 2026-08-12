<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-08-12 10:39:32 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
2fc88ae docs(report): sku-b-v4-prep -- the table's own tail, a listing control, Dv175
7b9caa4 chore(vault): the sku-b-v4-prep tail -- the day's log, hot.md, the index
8f4a7ed docs(report): sku-b-v4-prep
bb6b96e docs(decision): the v3 refusal and the v4 ruling
87c2240 feat(sku-b-v4-prep): the preflight re-driven against the v4 registration
```

## 📋 Recent decisions

- `sku-b-v3-refusal-and-v4.md` — The v3 session was refused by its own gate: three marginals, a fresh ledger, and a $0.65 cap
- `INDEX.md` — Decision records
- `sku-b-run-acceptance-and-resume.md` — sku-b-run accepted at 17 of 138: the probe priced the run, not the cap, and the (10)(b) stop resolves as a resume

## 📅 Recent daily logs

- `2026-08-12.md`
- `2026-08-11.md`
- `2026-08-10.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->
# Hot Cache — curated

**Last update:** 2026-08-12 (arch-a ✅, uni-a ✅, uni-b ✅, sku-b-prep ✅, sku-b-run ✅ ПРИНЯТ,
sku-b-v3-prep ✅, sku-b-v3-run ⛔ ОТКАЗ на воротах — попытка ЦЕЛА, sku-b-v4-prep ✅ $0,
**sku-b-v4-run ✅ ЗАВЕРШЁН, 121 куплен, $0.2541 из $0.65**).
**sku-a ✅, R1–R5 ратифицированы, голд text30 размечен, SPEC 3.17 (7)–(12) — закон.**
Артефакты v4: **`results/sku_b_positions_v4.json` + `.jsonl` (СЛИТЫЕ, 138 источников)**,
**`results/sku_bar_verdicts.json`**, `results/sku_pilot_prereg_v4.json`,
`results/sku_projection_v4.json`, `results/sku_pilot_serving.json`, `results/spend_sku_b_v4.json`,
`results/sku_b_positions.json` + `.jsonl` (запечатаны), `results/sku_b_positions_v3.json` (отказ,
улика). Отчёты: **`sku-b-v4-run.md` ← читать первым**, `sku-b-v4-prep.md`, `sku-b-v3-run.md`,
`sku-b-v3-prep.md`, `sku-b-run.md`, `sku-b-prep.md`, `uni-a.md`, `uni-b.md`.
Ещё: `docs/ARCHITECTURE.md`, граф кода, `docs/PORTING.md`.
**Next: приёмка — чтение тимлидом 61 ценовой пары (планка 2), вердикт B, брифинг 5c2.**
Блок правится руками; секция выше — авто-ген, маркер НЕ трогать.
Длинная форма отклонений: `implementation-notes.md` (Dv100–120), `uni-a.md` (Dv121–124),
`uni-b.md` (Dv125–132), `sku-b-prep.md` (Dv133–147), `sku-b-run.md` (Dv148–153),
`sku-b-v3-prep.md` (Dv154–160), `sku-b-v3-run.md` (Dv161–168), `sku-b-v4-prep.md` (Dv169–175),
**`sku-b-v4-run.md` (Dv176–180)**. Дневники [[2026-08-12]] / [[2026-08-11]], ADR ниже.

## 🔥 What's Hot

**ПИЛОТ ЗАКРЫТ ИЗМЕРЕНИЕМ. 121 КУПЛЕН, ПОПУЛЯЦИЯ 138/138, $0.2541 ИЗ $0.65** (`sku-b-v4-run` ✅
12.08, семь коммитов `910c4b6..`). Ни (10)(a), ни (10)(b) не сработали: ворота дали **$0.5300
против $0.6500 — proceed**, ин-ран гейт шёл вниз ($0.2685 → $0.2361). 79 позиций, 5 нечитаемых
ответов (3.62%, четыре разные причины), 102 пустых, **61 позиция с зачёркнутой ценой**.
Слитые артефакты `results/sku_b_positions_v4.{json,jsonl}` — каждая строка дампа называет свою
сессию в `bought_by`: 65 `sku-b-v4` + 14 `sku-b`.

**ПЛАНКИ (`results/sku_bar_verdicts.json`, числа из кода, приговоров нет).**
Планка 1 — brand-recall **0.3603 против 0.75 → FAIL** (макро по 15 постам; micro 0.4727,
**precision 0.9286**, на четырёх постах с пустым голдом — НОЛЬ ложных). Планка 3 — tier-accuracy
**0.8621 против 0.85 → PASS** (29 из 30, 1 нечитаемая = 3.3% < 10%). Планка 2 — **PENDING_TEAM_LEAD,
n = 61 пара, класс SCOREABLE (R4); значения НЕТ и быть не может — SPEC §10.**
`attempts.on_failure` зарегистрирован: провалившаяся планка закрывает B «инструмент не готов»
ИЗМЕРЕНИЕМ — ни ретрая, ни переформулировки, ни второй выборки.

**ГЛАВНАЯ НАХОДКА: ПРОБА ВЕРНА И ВСЁ РАВНО ВТРОЕ ДОРОЖЕ ПОПУЛЯЦИИ.** Зарегистрированная страница
(11)(c) дала **14.625 с** против 14.808 с в v3 — воспроизводимость 1.2%, проба не шумная. А сама
популяция стоила **4.0161 с/стр. (n=91)**: проба переоценивает то, ради чего выбрана, в **3.64
раза** — она структурно ГЛУБОКАЯ, потому что отправленный набор это первые шесть страниц каждой
листовки. Текст: 3.773 с варм-ап против 2.819 с/строка на деле (×1.34). Оценщик ворот несмещён для
пробы и смещён против рана. Именно это отказало v3 — и именно кап $0.65 из (12)(a) позволил тому же
инструменту дойти до конца за $0.2541.

**БУТ УПАЛ ВДВОЕ И ПОЧЕМУ — НЕИЗВЕСТНО.** 205.518 с против 402.586 с на той же конфигурации
($0.0630 вместо $0.1235). Структурный кандидат один — 112 с холодного чтения 1188 шардов с тома,
которые том, прочитанный дважды за двенадцать часов, не повторяет. Два замера, отличающиеся вдвое,
это разброс, а не тренд: проекции по-прежнему платят полные 402.586 с (Dv179).

**ЧТО КУПЛЕНО И ЧТО НЕТ.** Каждый элемент из 138 куплен РОВНО ОДИН раз за всю программу: 17 —
первой сессией ($0.1965), 121 — этой; ни один ответ не переспрошен, parse refusal первой сессии
вошёл в планки как есть. Отказавшая v3 не купила НИЧЕГО (`stopped_before_gold: true`) и её $0.1526
списаны на ФАЗУ по (12)(b), а не на этот кап.

**КАЛИБРОВКА ТИМЛИДА (n=13, один лейаут — инференс, не приговор):** промо **13/13** ✓, печатный %
**13/13** ✓, бренды читаются отлично; **вся ошибка в зачёркнутой старой цене и вся — в суперскрипте
копеек** (264⁹⁰→264.5, 39⁹⁰→39.99, 71⁵⁰→71.9, 19⁹⁰→19.99, 44⁴⁰→44.9, 42⁹⁰→42.5). Плюс дубль
«Каштан 75 г» и промо-без-старой (два товара под одним ценником). Если 91 оставшаяся страница ведёт
себя так же, планка 2 (0.80) провалится и B закроется ИЗМЕРЕНИЕМ. Суперскрипт и звёздочка — ПОСТ-
пилотная ИМЕНОВАННАЯ ревизия рядом с замороженными промптами, НИКОГДА не правка на лету ((11)(b)).

## ⏭️ Next

**ПРИЁМКА — ЗА ТИМЛИДОМ, И ЭТО ЕДИНСТВЕННОЕ, ЧТО ОСТАЛОСЬ ОТ ПИЛОТА.** Планка 2 читается по
`results/sku_b_positions_v4.jsonl`: **61 строка с `price_old`**, каждая несёт номер страницы, файл
и его sha256, обе цены, печатный %, тир и `depth()` — картинку можно открыть, ничего не
перезапуская. Исполнитель НЕ скорит свою выборку (SPEC §10) и в отчёте нет ни одного числа планки 2.
Дальше: вердикт B (планка 1 провалена ИЗМЕРЕНИЕМ — решает тимлид, закрывает ли это B) → **брифинг
5c2**.

**ЧТО ОТЧЁТ КЛАДЁТ НА СТОЛ ВМЕСТЕ С ЧИСЛАМИ.** Инструмент НЕДОЧИТЫВАЕТ, а не ошибается: 28
извлечённых ключей против 55 голдовых, precision 0.9286, ноль ложных на постах с пустым голдом, и
все промахи планки 3 — в ту же сторону (модель возвращает меньше ступеней, чем тики оператора).
Шесть постов из 15 дали recall 0.0000, и у пяти из них голд = один бренд. Суперскрипт копеек и
звёздочка снова в списке нечитаемых (`'-50%*' is not a percentage` ×2) — это ПОСТ-пилотная
ИМЕНОВАННАЯ ревизия, никогда не правка на лету ((11)(b)).

**ДОЛГ Dv170 ЗАКРЫТ.** `scripts/sku_bar_verdicts.py` смотрит на v4 обоими дефолтами, а строка
`contract` — теперь константа с тестом, который пинит её к регистрации (`attempts.phase`), к
наличию файла контракта в дереве и к трём поправкам (6), (11), (12). Негативный контроль прогнан.
**Открыт близнец — Dv176:** ту же болезнь несёт `head["contract"]` самого драйвера
(`results/sku_b_positions_v4.json :: contract` называет `PROMPT-sku-b-v3-prep.md` и (9), (10), (11)
без (12)). Не тронуто намеренно: драйвер — денежный путь, а step 0.5 был назван поимённо. Никто это
поле не читает (проверено грепом) — чинить в следующем контракте, который и так трогает драйвер.

**DEFERRED, решается ПОСЛЕ пилота:** двухступенчатое чтение листовки (OCR-транскрипт → SKU из
текста) — предложение оператора 10.08, записано в `docs/STATUS.md`; и нужна ли `carrier=comment`
своя планка. Прережка не меняется ни в ту, ни в другую сторону.

## 🚧 Blockers

**НИЧЕГО НЕ БЛОКИРУЕТ ПРИЁМКУ.** Сюита **1824 passed, 2 skipped**; `ruff format --check` 230 файлов;
прелёт 30/30 exit 0. Почекаутная таблица зелёная на КАЖДОМ коммите сессии, красных по замыслу нет;
контроль — родитель `2fc88ae`, 1823. Запечатанные артефакты (`sku_b_positions.{json,jsonl}`,
`sku_b_positions_v3.json`, `sku_pilot_prereg_v4.json`, `spend_phase4.json`, `baselines.json`)
захэшированы ДО первого пишущего действия сессии и после рана — те же байты.

**Ничего не биллится, и это с ПОЗИТИВНЫМ КОНТРОЛЕМ** (два пустых массива — ещё и подпись
сломанного CLI): `pod list -a` → `[]`, `serverless list` → `[]`, `template list --type user` → два
5b-шных остатка `unfcr3ja0t` / `0g6zg73ptq`, `network-volume list` → `qw4nwleanc mp-srv2 EU-RO-1
100`. Биллится только том.

**ОТКРЫТ ОДИН: холодный старт, и он стал МЕНЕЕ предсказуем.** 12.08 тот же конфиг дал **205.518 с**
против 402.586 с накануне — вдвое, без единой правки. Два замера ×2 друг от друга это разброс:
проекции платят полный 402.586 с, и любая новая должна делать так же, пока не появится третий
замер. Ниже — диагноз того, медленного. 402.586 с против 183.58 с у vis-c (**×2.19**). Снят с
`worker-boot.log`: 11.76 с SDK-fitness + **112 с** загрузки 1188 шардов (первые 822 идут 7.61/с,
последние 366 — 91.5/с, ступенька ×12 = холодное чтение сетевого тома, потом кэш) + **267.6 с (68%)
НЕ АТРИБУТИРОВАНЫ** — лог без таймстемпов. Веса на `qw4nwleanc` (`HF_HOME=/runpod-volume/hf`).
Рычаг — консолидация шардов, отложено на 5c. Проекция v4 платит полные 402.586 с. Внимание:
175.8 с из старых записей — это **ПОД**, другой транспорт.

**ТОНКИЙ ЗАПАС ОКАЗАЛСЯ НЕ НУЖЕН.** $0.0357 пессимистичного угла не понадобились: ран пришёл по
оптимистичному сценарию и лёг ниже даже его ($0.2541 против $0.3315 с дрейфом). Ставить кап по
пессимистичному углу всё равно было верно — иначе это кап, который откажет в день запуска, что
ровно и случилось 11.08.

**Бюджет — живое ограничение.** Phase 4 **$23.3209 из $25**, остаток **$1.6791** (читать гард перед
сессией, а не эту строку — Dv33: баланс отстаёт от ресурса на минуты-часы). Пилот суммарно:
$0.1965 + $0.1526 + $0.2541 ≈ **$0.60** против исходной оценки $0.35 — цена честных ворот, а не
перерасход. `results/spend_sku_b.json`, `results/spend_sku_b_v3.json` и теперь
`results/spend_sku_b_v4.json` — закрытые якоря, не трогать. Том биллится всегда: **≈ $0.012/ч**
(выведено из двух балансов за 9.7 ч простоя) — этим объясняется, почему осевшая дельта выше
секундной.

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
