<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-08-27 11:24:38 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
5f1716a docs(report): think-zero-shot -- 136/200 both ways, 27 rows moved, three bars unchanged
4d09eff chore(measurements): the pass-1 rate's population, said correctly
7f7fc1d feat(think-zero-shot-d2): dev-200 v2 with thinking is 136/200 — the same number, 27 different rows
1cd84da feat(think-zero-shot-d2): the paired table's producer, and both halves proven at $0
4bffd16 feat(think-zero-shot-d2): the two smokes, and the rate that decides the programme
```

## 📋 Recent decisions

- `lora-c-the-line-trains-at-90-seconds-a-step.md` — The line trains at 89.961 s/step — and the gate that would have hidden it
- `INDEX.md` — Decision records
- `lora-c-the-volume-moves-to-ca-mtl-3.md` — The training line's volume moves to CA-MTL-3 — and the cheaper cards arrived 107 minutes late

## 📅 Recent daily logs

- `2026-08-27.md`
- `2026-08-26.md`
- `2026-08-25.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->
# Hot Cache — curated

**Last update:** 2026-08-27 — **РАМКА СМЕНИЛАСЬ: рулинг (х), переспека.** Этап 1 —
`docs/SPEC-v2-promo-pulse.md`, «промо-пульс сетей»: цены и комменты под промо-постами сетей,
перечень сетей расширен максимально; тренды/алерты по брендам — трек роста источников.
**Контракт C1 `retail-census` ИСПОЛНЕН** ($0): шаг 0 — том `mp-lora-c` удалён (листинги в отчёте,
`mp-srv2` — контроль); две новые темы в `discover_channels.py`; `results/retail_census.json`;
отчёты `docs/reports/retail-census.md` и `docs/reports/registry-revision-proposal.md`.
**Оба отчёта ЖДУТ СЛОВА ОПЕРАТОРА** — выбор источников и ревизия registry (A · B · PAUSED)
делаются отдельным шагом, в этом контракте registry не тронут. Дальше по карте — C2
`positions-scale` (≤$1). Карта, деньги и живые рулинги — в `docs/STATUS.md`; читать ЕГО.

**Долг, который исполнитель не может закрыть сам:** переспека STATUS.md вымыла цитату рулинга (ф),
которую `scripts/write_think_zero_shot_prereg.py :: quoted()` грепает дословно, — с шага 0
`tests/test_think_zero_shot.py::test_the_registration_rebuilds_except_where_step_0_moved_a_pin`
красный. Продюсер запечатан, STATUS — файл тимлида; цитируемым рулингам место в MACHINE-READ
BLOCK, а не в прозе над ним. `make check`: 2 failed, 4088 passed (второй красный — старый долг
`test_repair_phase4_ledger`).

> Блок курируется руками. Археология закрытых контрактов живёт в отчётах, ADR и логах дня — не
> восстанавливать сюда то, у чего есть дом. Ценз буста мерить ДО и ПОСЛЕ каждой правки.

## 🔥 What's Hot

**🧭 ЕДИНИЦА РАБОТЫ — ПУНКТ DoD, НЕ РЕГИСТРАЦИЯ С РУНГАМИ** (рулинг (у), полный текст в
`docs/reviews/2026-08-26-replan-and-process-diet.md`): одна фича на сессию, контракт **≤50 строк**,
отчёт **≤80**, без чекера «своих чисел», платный контракт — **четыре** рунга с ASK при перерасходе
≤20%, кап **2× оценки из реестра**. Не выдаётся, пока контракт не назвал пункт DoD, гейт — потерю,
число — файл.

**📐 РЕЗУЛЬТАТ ИЗМЕРЕН 05.08, А README ЭТОГО НЕ ЗНАЕТ.** `results/verdict_45h2.json`: тональность
**0.921 против 0.683**, сарказм **23 из 38**. README пишет «No measured numbers are published yet»
— это и есть фича A1.

**📊 РЕЕСТР ФИЗИЧЕСКИХ КОНСТАНТ** живёт в `docs/STATUS.md` §«Реестр измерений»; файл
`results/measurements.jsonl` **уже создан** (`think-zero-shot` D1) и несёт четыре BEFORE-ставки с
источником, n и максимумом — полная миграция реестра остаётся шагом 1d контракта `a1`. Капы:
**89.961 с/шаг** и пик **49.54 GiB** при 3 072 на A100 PCIe · 61.047/68.442 и 33–35 GB при 1 408 на
A6000 · v3 9.20 с/звонок · walk биллинга отстаёт на 30–40 мин.

**⚠️ ДВЕ СТАВКИ РЕЕСТРА STATUS РАСХОДЯТСЯ С ЗАМЕРОМ ПО ФАЙЛАМ ОТВЕТОВ.** STATUS: «проход-2 **97
с/тред**», «v1/v2 **6.14**». Файлы: **23.760 / 135.232 макс** (n = 75) и **2.293 / 2.726** (n = 200
каждая). 97 переоценивает проход-2 в **4.1×**. Правка STATUS — за тимлидом; считать по
`results/measurements.jsonl` ([[a_rate_is_a_property_of_the_pod]]).

**🧠 THINKING МЕНЯЕТ ФОРМУ ОТВЕТА, А НЕ ТОЛЬКО ПРОМПТ.** `<|channel>`/`<channel|>` — **special**-токены
(100, 101), поэтому `skip_special_tokens=True` СТИРАЕТ границу «работа/ответ», и её теряют трое:
парсер, слияние двух объектов у читателя и балансный стоп транспорта — последний остановил бы
генерацию ВНУТРИ мысли. Стаб этого не видит: он подменяет `generate`. Починено в `9c29ae0`
(`prompts.after_thought`, `reader_v5_pod_runner.stops_here`) — [[the_marker_the_decoder_deletes]].

**🧭 У СДВИНУТОЙ КОНСТАНТЫ ЕСТЬ ПОТРЕБИТЕЛИ, КОТОРЫХ ГРЕП НЕ НАХОДИТ.** VRAM, с/шаг и доллары
символ не читают — они им ДВИГАЮТСЯ. Цена молчания на `max_seq_len` 1 408 → 3 072: OOM за $0.76 и
KILL за $0.44. Перед платным шагом писать пять чисел из ближайшего ЗАМЕРА: пик памяти · с/шаг ·
секунды · $ ×1.0 и ×1.5 ([[a_shifted_constant_has_physical_consumers]]).

**✅ ЗАКРЫТО, живёт в отчётах/ADR:** вся линия `lora-c` (итого **$1.123**) —
[[lora-c-the-line-trains-at-90-seconds-a-step]], `docs/reports/lora-c-run-r3.md`,
[[lora-c-the-volume-moves-to-ca-mtl-3]]; там же Dv813/Dv814 (гейт `gate_lora_b.measured_step`,
53.690 против 89.961) и бар 3 с атрибуцией прохода-1, которые обучением не лечатся.

## ⏭️ Next

1. **`think-zero-shot` D2 — ОДИН платный под, кап $8.00, СЛОВО ОПЕРАТОРА.** Застейджено: шесть
   паков по sha (`results/*_think*.json`), порядок стадий, имена out-файлов (`X.READER_THINK.jsonl`)
   и четыре рунга в `results/prereg_think_zero_shot.json`. Держу: рунг 2 проецирует по ИЗМЕРЕННОЙ
   s/call, которой нет, рунг 0 читает цену, которую даёт только create. Одна команда на стадию.
2. **Шесть красных тестов — ярус тимлида.** Пять грепают рулинги дословно из `docs/STATUS.md`,
   которые диета 410 → 118 удалила; исполнителю STATUS править нельзя. Варианта два: вернуть абзацы
   в STATUS или перевести `quoted()` на `git show <sealing>:docs/STATUS.md`. См. Blockers.
3. **`phase7-a1` ($0)** — лежит в дереве неисполненным (`docs/PROMPT-phase7-a1.md`), отложен до
   таблицы 6t. Внутри: закрытие lora-c сайдкаром, **удаление тома `mp-lora-c`**, README-таблица A1.
4. **Остаток цикла-2 — слово оператора, одно из двух:** (а) инференс для демо сарказма A2 (≈$1–2,
   рекомендация тимлида) или (б) окно-2 ($4.8). Вместе не влезают; D2 ($8.00) конкурирует с обоими.
5. **Приёмка отчёта r3** — вердикт уже вынесен (у); чтение «suite, closing» теперь ЕСТЬ, см. Blockers.
6. **`money-anchors` ($0)** — settled-закрытия, зависший walk pass1-probe, 19 без `anchored_at`.

## 🚧 Blockers

**⛔ БАЗА КРАСНАЯ, И ЭТО НЕ ИСПОЛНИТЕЛЬСКОЕ. ШЕСТЬ ТЕСТОВ.** `make check-stamped` на `9c29ae0`:
`reading HOLDS`, **`6 failed, 4040 passed, 2 skipped`**. Те же шесть воспроизводятся на HEAD за
**14 с** — до первой строки `think-zero-shot`. Пять из них грепают рулинги ДОСЛОВНО из
`docs/STATUS.md` (`test_lora_c_run::…RULING_V/RULING_K`, `test_lora_c_prep::…rulings_are_quoted…` и
её же `[write_lora_c_prereg.py]`, `test_lora_c_armb::…leg_count_is_two…`), а диета 410 → 118 эти
абзацы удалила — грепать больше нечего. Шестой, `test_repair_phase4_ledger::…LINE_ledger…`, читает
`results/spend_cycle2.json`. Исполнителю STATUS править нельзя, поэтому это ждёт слова: вернуть
абзацы или перевести `quoted()` на `git show`. **Закон «зелено после каждого коммита» сейчас
недостижим ничем, что мне разрешено** ([[the_gates_evidence_outlived_its_artifact]]).

**⛔ `mp-lora-c` ЕЩЁ КАПАЕТ.** Два тома ~$0.47/сутки; цикл-2 по чтению тимлида после r3 —
**$10.4921 из $20.00, остаток $9.5079**. Удаление — step 1c контракта `a1`, доказательство
листингом. `mp-srv2` (EU-RO-1, сервинг) ОСТАЁТСЯ.

**⛔ ОТЧЁТ r3: ЧТЕНИЕ ТЕПЕРЬ ЕСТЬ, И ОНО ОПРОВЕРГАЕТ ПРЕДСКАЗАНИЕ.** «suite, closing» стояло
`NOT TAKEN` с предсказанием **3 999 / 2**. Step 0 контракта `think-zero-shot` снял то же чтение на
`8d40782`: **3 993 passed, 6 failed, 2 skipped**. Предсказание не подтвердилось — шесть красных были
уже там. Плейсхолдеры в отчёте r3 на месте, файл модифицирован в дереве не мной и я его не трогал;
вписывать — решение тимлида ([[gate_verdicts_need_an_artifact]]).

**⛔ `make fmt` ОБНУЛЯЕТ ПИНЫ ПРОДЮСЕРОВ — ОБА РАСФОРМАТИРОВАННЫХ ФАЙЛА ЗАПИНЕНЫ.**
`scripts/write_lora_c_prereg.py` → `results/prereg_lora_c.json::producer`;
`scripts/build_lora_c_marker_census.py` → `results/lora_c_marker_census_pack.json`, запиненный внутри
замороженной регистрации. `make check` гоняет `ruff check`, а не `ruff format --check`, и не видит
ни того, ни другого. Форматировать ТОЛЬКО по путям.

**⛔ ДВА ДОЛГА ИНСТРУМЕНТА, ОБА С ДОМОМ.** Допуск гарда 7% недостижим на дешёвом шаге (n = 2, долг
в `money-anchors`; третья точка от r3 — 0.29%, там полоса грейдит нормально). И `preflight` слеп к
`config_sha256`: у поля нет соседа-пути, поэтому `config/qlora.yaml` не попадает в реестр пинов —
проверять перечисленным диффом записи, не preflight'ом.

**🧹 `MEMORY.md` УПЁРСЯ В ОБА ПОТОЛКА, ВТОРОЙ НЕ ЗАКРЫТ.** Загрузчик
(`context-census.py::loaded_memory`): trim → первые **200 строк** → отрез по **25 000 UTF-16 units**.
После чекпоинта 14:40: **204 строки**, окно **186 / 24 933 units**, **18 указателей не доезжают**
(файлы уроков целы). Четвёртая запись дня — [[the_marker_the_decoder_deletes]] — вставлена В НАЧАЛО
`## Feedback`; торг: первым за окном теперь [[a_gate_command_is_a_write]]. Рычаг один —
убрать ~15 СТРОК, это консолидация и отдельное решение оператора. Выживание проверять
`loaded_memory`, **НЕ `head -c`** ([[the_wrong_unit_points_at_the_wrong_lever]]). Ценз буста
**11.7 Ktok** при цели 10.7 — из них `MEMORY.md` 25 274 байта, больше половины.

**⚠️ `_to_delete/` В КОРНЕ РЕПО** — внутри один `git-index.lock` на 0 байт, появился вместе с
тимлидовой правкой. Не исполнительский файл; не трогал, называю.

## 🔫 Footguns этого файла

**⛔ ИНВАРИАНТ РУНГА 5 — НА БЛОБАХ, НЕ НА КАТАЛОГЕ КЭША.** `du -sb /workspace/hf` сдвигается за
обычную загрузку (`refs/main` + нулевые маркеры `.no_exist`), блобов при этом пишется 0. Ремеди
ИСПОЛНЕН в step 0.5 r3, в НОВЫХ файлах (sha файлов миграции запинены запечатанным отчётом); на поде
прочитано **12 блобов, 0 выросших**. Разбор — `results/lora_c_migrate_r2_load_bytes.json`
([[an_invariant_on_the_container_not_the_payload]]).

**⛔ `knowledge/hot.md` ГРЕПАЕТСЯ КАК ВХОД — ДВА ЛИТЕРАЛА, НЕ ОДИН.** `scripts/volume_calc_5c1.py`
берёт отсюда **`~$0.24/day`** (строка 107) И **`80 GB is about what the`** (строка 136); пропажа
любого роняет девять тестов `tests/test_volume_calc_5c1.py`. Сегодня это и случилось: при
переписывании блока я сократил вторую фразу, грепнул только первый литерал — и получил 9 из 10
красными. **Грепать оба, и гонять `pytest tests/test_volume_calc_5c1.py` после КАЖДОЙ правки этого
файла**, не только после правки кода ([[fact_is_the_rule_when_the_law_keys_on_it]]).

- **Литерал живой и нагруженный:** 100 GB сетевого тома стоят **~$0.24/day** — это ЦЕНА ЗА ТОМ, а не
  состояние счёта; сейчас таких тома два. Литерал ОБЯЗАН стоять ровно так, по-английски со слэшем:
  `scripts/volume_calc_5c1.py :: quoted(HOT, "~$0.24/day", 0.24)` грепает его ИЗ ЭТОГО ФАЙЛА как
  вход. Перевод слова `day` уже уронил девять тестов один раз (12.08).
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month — фраза нагруженная, `volume_calc_5c1.py` грепает её
  посимвольно. Если под нужен на одну сессию — **delete** (`runpodctl pod delete`, `pod terminate` не
  существует), не stop. Остановленный под — не остановленный счёт, и `runpodctl pod list` показывает
  только running: смотри `pod list -a`.
