<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-08-16 18:57:45 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
48a32d7 docs(report): reader-v3-run -- bound the twenty minutes, and close the billing wait explicitly
a8bfd18 docs(report): reader-v3-run -- the delta had not stopped, it was between the volume's chunks
0aced41 docs(report): reader-v3-run -- Dv445, and the two commits that are red on their own trees
6fde752 fix(test): the witness ledger is whichever one is LIVE, not the phase's
1b7b0bc docs(report): reader-v3-run
```

## 📋 Recent decisions

- `reader-sitting-16-08.md` — The reader sitting of 16.08: four rulings — the $20 line, instrument v3, the reader's own gate, and one word
- `INDEX.md` — Decision records
- `serving-latency-deferred.md` — Serving latency is decomposed and the cure is deferred until production

## 📅 Recent daily logs

- `2026-08-16.md`
- `2026-08-15.md`
- `2026-08-14.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->
# Hot Cache — curated

**Last update:** 2026-08-16 `/save` 18:50, после ТРЁХ контрактов дня — `cycle2-money`,
`reader-v3-prep` (оба $0 GPU) и **`reader-v3-run` — ПЛАТНЫЙ И ПРОВАЛЕННЫЙ**. `make check`
**2 645 / 2 skipped**. Подробности — [[2026-08-16]]; рулинги дня — [[reader-sitting-16-08]].

**🔴 `reader-v3-run` ИСПОЛНЕН, ИСХОД ПЛОХОЙ: кап съеден setup-ом, прочитано НОЛЬ тредов.**
Отчёт `docs/reports/reader-v3-run.md`, девиации **Dv436–Dv445**. Эндпоинт `77o1ing6cy0972` поднялся
с `gpuIds: ADA_24`, и джоб `info` (это и есть загрузка весов) не ответил **≥20 минут** при
`running: 1 · completed: 0 · retried: 0`. Дельта шага $0.0000 → **$0.3918 при капе $0.35**. Счётчик
убит на $0.3062, эндпоинт и шаблон удалены, три листинга совпали с «до». **Ни один бар не посчитан —
все UNSCORED, не «провалены».** Единственная попытка контракта потрачена; переоткрытие — решение
оператора.

**💰 ЛИНИЯ ЦИКЛА-2: потрачено $0.4325 из $20.00 (чтение 16:09:47Z), свободно $19.5675.**
Якорь `$22.5097614388` (`2026-08-16T12:14:48Z`). Фаза 4 ЗАКРЫТА на $32.4708 из $33.00.
⚠️ **Шаг `reader-v3` НЕ ЗАКРЫТ:** прогон биллинга пуст (`pods` и `serverless` = `[]` на 16:11:55Z),
settled-цифры нет, `$0.3918` — НИЖНЯЯ ГРАНИЦА на момент удаления. **Первый гард следующей сессии
закрывает шаг и заодно решает, чем был провал (Dv444).**

**🔬 ИНСТРУМЕНТ v3 ЖИВ И ЗАСТЕЙДЖЕН — следующая попытка за стейджинг НЕ платит.** Том на `aa0ca18`,
адаптер 489 840 816 Б цел, все ТРИ ридерских текста и модуль парсера побайтово равны Mac'у и
регистрации. Драйвер `scripts/read_threads_reader_v3.py` и скорер `scripts/score_reader_v3.py`
в дереве, 21 тест, всё за $0.

**⏭️ С ЧЕГО НАЧАТЬ ЗАВТРА.** (1) `runpod_guard --step reader-v3 --step-cap 0.35 --close --since
2026-08-16T15:16:06Z` — закрыть шаг, как только биллинг постнёт строки; (2) прочитать `timeBilledMs`
эндпоинта `77o1ing6cy0972` — он различает «медленный бут» и «джоб не исполнялся» (Dv443);
(3) три решения оператора: две находки по замороженной регистрации (**Dv440**, **Dv441**) и
`setup_usd`, ошибающийся в 4.3 раза.

## 🔥 What's Hot

**🔥 БУТ МОЖЕТ СТОИТЬ ДОРОЖЕ ВСЕЙ ПРОБЫ. Три бута на этом стеке: probe-a 373 с · probe-b 179 с ·
16.08 >1 200 с.** `setup_usd: 0.0900` в замороженной регистрации ошибается в **4.3 раза**. Одно
измерение бута даёт число, а не границу. И главное: **гейт стоял ПОСЛЕ шага, который тратил** —
go/no-go меряет прогрев, а прогрев не наступил, так что ни одна ветка инструмента выстрелить не
могла. Ставить дедлайн на бут (или доказывать его на поде $0.24/ч до открытия serverless-счётчика,
`scripts/runbook_srv2b.md` §C.3), а не проверять арифметику после.
[[a-gate-downstream-of-the-spend]]

**⚠️ ДВА ДЕФЕКТА В ЗАМОРОЖЕННОЙ РЕГИСТРАЦИИ v3 — куплены за $0, ждут оператора** (аргумент целиком
в `docs/reports/reader-v3-run.md` §5–§6): **Dv440** — бар 3 вырос с ПЯТИ тредов (N2–N6) до ШЕСТИ,
исключение N1 у v2 не поехало в продюсер v3, а референс сам читает сигнал S1 (msg 21420) в этом
треде → **читатель, согласный с референсом, теперь ПРОВАЛИВАЕТ бар 3**; **Dv441** — голд r2 стал
баром, но `READER_SUBJECT_TYPES` всё ещё несёт ОБА слова, и ответ «категория» теперь ошибка
(**6 из 14** против **14 из 14** при схлопывании) — направление противоположно probe-b.

**📏 Порог гейта — 69.592 биллинговых секунды (1.117×), а НЕ опубликованные 1.165× (Dv437).**
1.165× ограничивает ВЕСЬ проход; гейт стоит на ПРОГРЕВЕ, чьи секунды тоже внутри итога, поэтому
запас = `(cap − setup) / (rate × (1 + 11.1818))`. На границе оба вердикта печатают
`projected_total_usd: 0.35` — вердикт переизводится ТОЛЬКО из пары секунд.
[[a-published-ratio-is-not-the-gates]]

**📐 Три зарегистрированных текста читателя, и v3 — OPT-IN.**
v1 `b272115637f784ad…` · v2 `9d281bc80f18c91b…` · **v3 `22533644cf35420e…`** (6 630 символов, полный
текст в приложении `docs/reports/reader-v3-prep.md`, round-trip'ится по sha). `reader_messages_gm4`
держит дефолтом **v2**: каждый вызывающий без `task` — это вызывающий, чьи улики уже на диске, и
сдвиг дефолта пере-рендерил бы запрос замороженной записи под текстом, которым её не слали.
v3 называет ТОЛЬКО контракт прогона.

**🔧 Парсер терпим к КОНТЕЙНЕРАМ и строг к ДОМЕНАМ — ровно три ремонта.** (1) два top-level объекта
сливаются, **и ключ в обоих с разными значениями = ОТКАЗ**, никогда не last-wins; (2) `{}` вместо
списка → `[]`; (3) map по **msg_id** → список (ключи ВЫБРАСЫВАЮТСЯ — каждая строка несёт свой
`msg_id`). Не чиним: `aspect: null`, `from_post`-сигнал без `evidence`, голый фрагмент без скобок.
`repairs: [...]` едет на КАЖДОМ вердикте, включая пустой список. На 23 реальных платных ответах
probe-b: **13/23 → 19/23**. `@VARUS_channel:10348` вернул entity-кейс E3.

**📊 Ячейка ценза читателя ИЗМЕРЕНА: 129 тредов · 1 032 платных коммента**
(`results/gate_census_w1_reader.json`, narrow · varto off · plus-spam/scam on). Окно на 4090 читается
за **$1.2517 / $1.7187** (связывает по платным комментам). ⚠️ **129 — это ТАКЖЕ thread-count
`narrow|silencers_off`**: два глушителя снимают КОММЕНТАРИИ и в этом окне ни разу не уносят последний
лексиконный хит треда. Различает только платный счёт (1 032 против 1 116) — цифру треда одну цитировать
НЕЛЬЗЯ.

**🎯 Популяция probe-b теперь production-reachable ЦЕЛИКОМ.** Все ЧЕТЫРЕ инъецированных треда (E1,
E4a, E4b, **N3**) входят в читательскую ячейку — убирал их `varto_rule`, и рулинг 3 его снял.
Ожидание контракта «N3 останется injectable» опровергнуто ЗАМЕРОМ. Дайджест популяции
`ccef35fa4b9c771f…` НЕ двигается: он считает флаги probe-b, а статус под новой ячейкой лежит РЯДОМ.

**🧪 Голд r2 — 12 ячеек и ни байтом больше.** `results/reader_gold_w1_r2.json`: `subject_type`
«категория» → «категория_личное», обход ТИПИЗИРОВАННЫЙ (по имени поля), проза о слове не тронута.
`CELLS = 12` — зарегистрированный литерал, тринадцатая ячейка ОТКАЖЕТ. Референс не правится,
`reader_gold_w1.json` (v1) не тронут — на него смотрят два запечатанных пина.

**⚙️ Карта: `ADA_24` (RTX 4090), 2.64× от L4 при той же цене за секунду.** `gpuIds` читается
БЕСПЛАТНО из ответа `serverless create`; фактическая карта — из `runtime.gpu` воркера, и поля могут
расходиться. **Ни одна ставка $/с не переезжает между контрактами без названной карты.** Полный
проход probe-b: 727.664 биллинговых секунд воркера на 23 тредах = **31.6376 с/тред · 5.4303
с/платный коммент**. Setup = закрытая цифра шага минус его чтение = **$0.0900**.

**🚩 Бары слоя комментных сигналов — ни один не взят.** Две пробы, $0.4173, бары на 23 тредах:
2/5 · 2/4 · 0 сигналов (проходит) · 0.357. Бар 3 «проходил» на счёте по ЧЕТЫРЁМ тредам без вердикта
вообще — предикат починен В САМОМ БАРЕ v3-регистрации: считается по тредам С распарсенным вердиктом,
отказ никогда не ноль, а без единого вердикта бар **UNREACHABLE**, что не проход.
[[a-bar-that-counts-passes-on-an-unreadable-reply]]

**🔄 ТЫ ЗДЕСЬ: джойнт-планирование цикла-2 и Фазы 6.** Фаза 5 закрыта, Фаза 4 закрыта, линия
цикла-2 открыта и заякорена. Все $0-задачи ниже можно делать не дожидаясь.

## ⏭️ Next

**Первым делом завтра — три бесплатные вещи, и только потом деньги:**

1. **Закрыть шаг `reader-v3`.** `python3 scripts/runpod_guard.py --step reader-v3 --step-cap 0.35
   --close --since 2026-08-16T15:16:06Z --note "..."`. Сегодня гард ОТКАЗАЛСЯ дважды: биллинг-прогон
   «no billing rows yet» (нечего settle) и кап достигнут ($0.3918 из $0.35). Долг **Dv444**.
2. **Прочитать `timeBilledMs` эндпоинта `77o1ing6cy0972`** (`runpodctl billing serverless
   --start-time 2026-08-16T15:16:00Z`). Он РАЗЛИЧАЕТ две разные находки (**Dv443**): ≈1 100 с =
   воркер честно грузил веса (причина — холодный старт, решение про кап/карту/прогрев); ≪1 100 с =
   форма srv-2b (`inQueue` при назначенном воркере, ничего не исполняется). Сегодняшняя улика
   склоняется к первому: `workers.running: 1` и `jobs.retried: 0` — это НЕ форма srv-2b.
3. **Решения оператора по `reader-v3`** — три, и без них платить снова нельзя:
   **Dv440** (бар 3 над пятёркой или шестёркой), **Dv441** (где живёт схлопывание словаря — в голде,
   в списке субъектов промпта или в скорере), и **кап против бута** (`setup_usd: 0.0900` ошибается
   в 4.3 раза; $0.35 бут такой длины не покрывает).
4. **`prep-b`** — сбор Сільпо / Varus / Маркетопт + докачка корпуса, $0. Слово оператора 16.08:
   ПОСЛЕ читателя, «мы не закончили с комментариями». Читатель теперь ждёт решений выше.

**Кандидаты цикла-2 в порядке ценности:**

1. **Деньги — линия $20.00 открыта и заякорена, $19.99 свободно.** В линию влезает всё решённое
   (окно-2 ≈$4.8 · читатель ≈$1.7 · v3-проба $0.35 кап · батч-пробник $2.13 · том ≈$2/нед);
   история 11 143 — не влезает.
2. **Батч-паритет — СПРОЕКТИРОВАН, решение за оператором.**
   `results/batch_cycle2_projection.json`. Из записей выводится НЕРАВЕНСТВО: шаг с batch 16 требовал
   **23.99 ГиБ** сверх весов, у 4090 их **3.99** — короче в **6.02×**, поэтому 16/8/4/3 исключены и
   единственный кандидат — **batch 2**; влезет ли он, **НЕ ИЗМЕРИМО** без живого пробника. Главный
   риск не память, а ОТВЕТЫ: при batch 16 разошлись **6 строк из 666**. Пробник: фикс **$0.1520** +
   **$0.0013025**/строка; арм 758 с контролем — **$2.1266**. Окупаемость −30%: **$4.3536** на
   истории и **$1.4511** на окне. **Само правило 3.19 уже сэкономило $1.7727 на окне и бесплатно.**
3. **Сбор листовок Сільпо / Varus / Маркетопт** — 3.18 (7)(d) + **3.20 (6)** (Маркетопт обязателен).
   Бесплатно, не начат, идёт в `prep-b`. В окне-1 листовочные СТРАНИЦЫ есть только у АТБ.
4. **Докачка корпуса** — сборка стоит с 08.08.
5. **История 11 143** — вход бесплатен, ~13 ч, ЖДЁТ батча И денег.
6. **Serving-латенси** — разобрана 16.08, лечение ОТЛОЖЕНО до «готовим прод»
   ([[serving-latency-deferred]]). ~4 мин на одиночный запрос — принятая цена отладки, не дефект.

**Долги-входы следующих регистраций:** цена страницы листовки **10.408 с/стр (n=159)** — старые
записи НЕ перескориваются. Ценз `results/gate_census_w1.json`: narrow|silencers_on = **111 тредов,
912 платных комментариев** (это популяция ПРОБ; читательская ячейка — отдельный файл, см. выше).
Два вопроса из §5 отчёта fix-a (два чтения правила `selianske`, коллизия `varus-pl`) и **метка типа
поста для окна-1** — без неё четвёртый глушитель нечем включить. Мелочи step-0.5: заголовок
`t5_depth`, валюта ₴ в шапке промо-таблицы, fix-b(2) «две колонки — одно число»; пачка закрытий
22 старых шаговых леджеров — при первом контракте, трогающем гард.

## 🚧 Blockers

**✅ Dv426 РЕШЁН тимлидом: ремонт 3 остаётся УЗКИМ** («map keyed by msg_id», как зарегистрировано)
— преамбула `docs/PROMPT-reader-v3-run.md`. Не переоткрывать. Для памяти, почему решение вообще
понадобилось: клауза контракта говорила «msg_id», а его же verify-блок ждал 3/3 парса на трёх
платных ответах probe-a; измерены оба чтения — узкое **1/3**, широкое **2/3**, и **3/3 недостижим ни
при каком**, потому что третий ответ несёт `evidence: [null]` — ДОМЕННЫЙ дефект из списка «не чиним».

**🟡 Dv433 ОТКРЫТ — потолок вывода для ОКОННОГО прохода.** v3 просит `per_comment`-строку на КАЖДЫЙ
показанный коммент, так что длина вывода масштабируется платным счётом треда. probe-b вернула
`finish_reason: length` на НУЛЕ из 23 ответов, её самый большой тред — 15 платных. **Самый большой
тред 129-тредовой ячейки — 125** против `READER_MAX_NEW_TOKENS = 2000`. Пробу это не связывает (те же
23 треда), ОКНО — связывает. Разблокировка встроена в `reader-v3-run`: `finish_reason` per thread и
чтение токенов-на-`per_comment`-строку в вердикте; окно не открывать, пока их нет.

**⛔ Ни один бар слоя комментных сигналов не взят, и `reader-v3-run` этого НЕ снял.** Прогон
исполнен 16.08 и не прочитал ни одного треда — все бары UNSCORED, не «провалены». Инструмент собран,
заморожен и застейджен; что мешает — деньги и три решения оператора выше, не код.

**🟡 Dv443 ОТКРЫТ — чем был провал бута, ещё не решено.** ≥20 минут `running: 1 · completed: 0`.
Разделяет `timeBilledMs` эндпоинта, чтение бесплатное, см. «Первым делом завтра» (2).

**🟡 Dv444 ОТКРЫТ — шаг `reader-v3` не закрыт.** Биллинг ничего не постнул за 55 минут после
удаления; `$0.3918` (15:49:41Z) — НИЖНЯЯ ГРАНИЦА, а не settled-цифра. И дельта продолжает расти
порциями тома ($0.4033 к 16:09:47Z) — Dv412 в силе, метр на балансовой дельте меряет СЧЁТ, а не шаг.

**🟢 Снято сегодня: два гарда, которые отказывали платному прогону не по делу.** `Dv439` —
префлайт держал `len(set(rendered)) == 2` над семейством из трёх текстов (форма Dv428 одним скриптом
дальше); `Dv445` — тест-свидетель искал платные шаги только в леджере ЗАКРЫТОЙ Фазы 4, и первый же
`--note` под линией цикла-2 покраснил сюиту, зелёную неделю.

**Деньги — три числа, которые легко перепутать, и правило для каждого.** Шаг цени ПО БИЛЛИНГУ с
исключением всегда-включённых видов ПО ВИДУ: probe-b — **$0.313162** из $0.35, внутри капа. Фазу и
линию — пессимистичным максимумом двух чтений. Дельта баланса меряет СЧЁТ, а не шаг, и после
закрытия шага растёт вечно — поэтому шаг и леджер теперь можно ЗАКРЫТЬ. Остаток ВЫВОДИТЬ
(`CAP - spent_usd`), а не читать из `sessions[-1].remaining_usd`
([[the-field-true-under-the-old-constant]]). Записи леджера **anchor-relative** — `spent_usd` по
сессиям НЕ суммируется.

**⚠️ Якорь цикла-2 ОДНОРАЗОВЫЙ, и сюита однажды его уже написала (Dv424).** Снятие порога $40
открыло место записи, которое порог до того закрывал СЛУЧАЙНО: все балансы `tests/test_runpod_guard
.py` ниже $40, поэтому `read_cycle2` возвращал `None`. Самый следующий `make check` заякорил линию на
балансе фикстуры $22.00. Плохой якорь удалён до коммита, редирект теперь autouse и НА МОДУЛЬ.
Правило шире: **снимая порог, спрашивай не что перестаёт отказывать, а что становится ДОСТИЖИМЫМ.**

**⚠️ 22 шаговых леджера в третьем состоянии.** Ни один из 23 `results/spend_*.json` шага не несёт
времени якоря; закрыты только probe-b и линия цикла-2. Остальные при опросе честно печатают «нижняя
граница». Закрыть каждый дёшево (`--close --since` с окном из его же отчёта).

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
идентичная по строкам, но не по байтам) уронит возврат сидения с «the sitting read …».

**Якоря, которые не трогают:** `results/spend_phase4.json` — ЗАКРЫТ, append-only, никогда не
регенерируется. `results/spend_cycle2.json` — ЖИВОЙ якорь линии, одноразовый, никогда не
регенерируется. `results/spend_5c2run.json` — закрытый якорь сессии. `results/spend_sku_b*.json`,
`results/spend_skub2.json`, `results/spend_probe_b.json` — тоже закрыты. Том биллится всегда:
**≈ $0.012/ч**.

**Запечатанные записи, которые НЕ перепинываются, а получают MOVED-манёвр:**
`prereg_reader_probe.json`, `prereg_reader_probe_v2.json`, `reader_gold_w1.json`,
`validate_5c2_pack.json`, `window_summary_5c2.json` — все пять держат старую sha `prompts.py` через
`MOVED` в своих тестах. `dashboard_data_w1.json` — ЖИВОЙ экспорт: он пере-генерируется В ТОМ ЖЕ
коммите вместе с `dashboard/index.html`, который его встраивает.

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
  Указатель поэтому отстал на ШЕСТЬ амендментов (3.19, 3.20, 3.21, 3.22, 3.23, 3.24 — каждый сам себе
  индексная запись внутри своего блока), и это сделано намеренно. Посадка амендмента — **ШЕСТЬ**
  частей: маркированный блок в SPEC (индексная заметка ВНУТРИ него) · `write_prereg_5c2.BLOCKS_TODAY`
  + абзац её докстринга · перечисление в `tests/test_sku_prereg.py` · литеральный хвост
  `BLOCKS_TODAY[10:]` в `tests/test_prereg_5c2.py` · имя злоумышленника в негативном контроле там же
  (сдвинуть на следующее незанятое!) · зелёный `make check` одним коммитом. Шестую часть с 3.23
  ВЫНУЖДАЕТ красный тест, до этого она рвалась молча.
- **`dashboard/index.html` — генерат, и тест сравнивает его байты со свежей сборкой.** Тронул
  `scripts/build_dashboard.py`, `config/ui_strings.yaml`, `config/metrics.yaml` или сам экспорт —
  прогони `PYTHONPATH=src python3 scripts/build_dashboard.py` и закоммить страницу в ТОМ ЖЕ коммите.
  Порядок тот же: `ruff format` СНАЧАЛА, сборка ПОТОМ. И проверяй страницу глазами в браузере, а не
  только грепом: пустая диаграмма и полоса поверх подписей — не красный тест, а картинка
  ([[the-helper-that-guesses-its-inputs-shape]]).
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
- **Price the staging class from a reading taken TODAY, never from this line** (Dv177 → Dv387).
  Dv177 said the $0.24/h class had left EU-RO-1 and the cheapest with stock was L4 at $0.49/h;
  `runpodctl gpu list` on **15.08** offers **RTX 2000 Ada at $0.240/h in EU-RO-1, stock Low** — half
  what the stale line assumed, and probe-a staged on it for **$0.0097** in 2 min 26 s. The durable
  part is the habit, not the number: read the class list before `pod create`, build the bundle and
  the staging script first, and price the pod from its own clock (the balance still reads $0.0000 —
  Dv166).
- **`runpodctl ssh info` answers with `ip`/`port`, not `host`** (Dv178). A readiness loop grepping
  for the wrong key runs its full timeout against an answer that was already complete — 55 s of
  billed pod, and it looks exactly like a slow resource.
- **Эта оболочка — zsh, и `$SSHOPT` в ней НЕ расщепляется** (Dv442, ≈$0.02 сегодня). Незакавыченная
  переменная с ssh-опциями уезжает одним аргументом: `ssh` печатает
  `keyword stricthostkeychecking extra arguments at end of line`, цикл готовности крутит полный
  таймаут, а под всё это время биллится — и выглядит как «под не поднялся». Пиши флаги явно.
  `scripts/runbook_4b.md` предупреждает об этом с Фазы 4, но для bash.
- **`op: info` на этом воркере — это ЗАГРУЗКА ВЕСОВ, а не дешёвый вызов** (Dv443). `Worker` грузит
  лениво, на ПЕРВОМ джобе, поэтому хендшейк платит весь холодный старт. И `EndpointClient.timing()`
  стартует стенные часы с первого запроса ПРОЦЕССА — то есть с `info`: `--handshake` и `--warm-up`
  разными вызовами и подряд, иначе бут окажется внутри окна гейта, порог которого 69.592 с.
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
- ~~**`runpod_guard.py --step <name>` reads one ledger and writes another**~~ — **CLOSED 15.08**
  (`692f161`, Dv392): both writes now use the one path `step_ledger_path` resolved, the two probe-a
  ledgers are merged content-preserving, and the test drives `main --note` and looks at the
  DIRECTORY. Проверено в проде: сессия probe-b оставила ровно один `results/spend_probe_b.json`.
- ~~**`runpod_guard.py --step` даёт ОДНО чтение (Dv411)**~~ и ~~**шаговый счётчик на дельте не
  останавливается (Dv412)**~~ — **ЗАКРЫТЫ 16.08** (`27eba42`, SPEC 3.23). Что осталось знать:
  у шагового чтения **ТРИ состояния**, и их нельзя схлопывать — «оба чтения → пессимистичный
  максимум» · «окно есть, строк нет → UNAVAILABLE, цифра НИЖНЯЯ ГРАНИЦА» · «времени якоря нет →
  другое предложение, ходока не спрашивали». Новые якоря пишут `anchored_at` сами; у старых 22
  леджеров его нет, им нужен `--close --since <окно из их отчёта>`.
  [[a-step-meter-on-a-balance-delta-never-stops]], [[a-window-never-asked-is-not-an-empty-one]]
- **A RUNNING WORKER HOLDS THE CODE IT BOOTED WITH — a `git merge` on the volume reaches nothing.**
  vis-b paid $0.1581 to learn it. `serverless update` does not restart a worker, `--idle-timeout 60`
  does not stop one that failed a job, and **only `serverless delete` stops it**. **Stage the volume
  BEFORE the endpoint exists** and treat the code as frozen from the first request onward.
- **A failing serverless worker bills exactly like a working one** — srv-2b's ran 31 min at
  $0.00031/s with its job stuck in the queue. Watch **the first job's status**, not worker health.
  (`runpod_guard` has walked serverless since srv-2c and now reports the three kinds APART.) And a
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
- **`results/spend_phase4.json` is the $33.00 cap's anchor, is now CLOSED, and must not be
  regenerated.** Delete it and the counter silently restarts at today's balance. The guard still
  refuses when the balance is *above* an open ledger's anchor — a mid-phase top-up is an operator
  decision. `results/spend_cycle2.json` is its successor, ANCHORED 2026-08-16 at
  $22.5097614388 and just as one-shot: SPEC 3.24 (1) repealed 3.23 (2)'s $40.00 floor, so nothing
  gates a re-anchor except the file's own existence.
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
