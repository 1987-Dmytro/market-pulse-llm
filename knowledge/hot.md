<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-08-17 11:42:51 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
f19a9b4 docs(report): reader-v4 -- three red commits, not two, checked out one by one
276205d docs(report): reader-v4 -- the measurement, and two bars that fail
ace1a0d run(reader v4): 23 of 23 read on a pod for $0.2446, and the reader FAILS bars 1 and 4
f1bb539 prereg(reader v4): restore the projection's second leg, before the pod exists
05df60d anchor(reader-v4): the counter and the pack, both before the pod exists
```

## 📋 Recent decisions

- `reader-sitting-16-08.md` — The reader sitting of 16.08: four rulings — the $20 line, instrument v3, the reader's own gate, and one word
- `INDEX.md` — Decision records
- `serving-latency-deferred.md` — Serving latency is decomposed and the cure is deferred until production

## 📅 Recent daily logs

- `2026-08-17.md`
- `2026-08-16.md`
- `2026-08-15.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->
# Hot Cache — curated

**Last update:** 2026-08-17 `/close` дня 16.08 — ШЕСТЬ сессий, из них ДВЕ платные: `reader-v3-run`
(провален, $0.3936 за ноль тредов) и **`reader-v4` (исполнен, $0.2446 за все 23 треда)**.
`make check` **2 685 / 2 skipped**. Подробности — [[2026-08-16]]; рулинги — [[reader-sitting-16-08]].

**🎯 СЛОЙ КОММЕНТНЫХ СИГНАЛОВ ИЗМЕРЕН. Бары 1 и 4 ПРОВАЛЕНЫ, попытка потрачена.**
Отчёт `docs/reports/reader-v4.md`, девиации **Dv446–Dv455**, вердикт
`results/reader_v4_verdict.json` (`7f5c96c8352ad052…`).

| бар | итог | число | без склейки | probe-b |
|---|---|---|---|---|
| `1_flagships` | **FAIL** | 2 из 5 | 1 из 5 | 2 из 5 |
| `2_entity_cases` | PASS | **4 из 4** | — | 2 из 4 |
| `3_noise` | PASS | 0 сигналов на пяти отвеченных | — | 0 (те же пять) |
| `4_per_comment_agreement` | **FAIL** | **0.500** при баре 0.80 | 0.357 | 0.429 схлопн. |
| `5_time_and_cost` | OPEN | $0.2446 нижняя граница | — | — |

По clause об ОДНОЙ попытке вопрос закрыт: дальше **сидение и НОВАЯ регистрация**, а не второй заход.

**💰 ЛИНИЯ ЦИКЛА-2: потрачено $0.6868 из $20.00 (чтение 18:19:28Z), свободно $19.3132.**
Якорь `$22.5097614388` (`2026-08-16T12:14:48Z`). Фаза 4 ЗАКРЫТА на $32.4708 из $33.00.
Шаг `reader-v3` **ЗАКРЫТ** на **$0.393577** settled (serverless $0.371765 — бут 1 211 005 мс,
не ответивший ничего; pods $0.021812). ⚠️ Шаг `reader-v4` **НЕ ЗАКРЫТ**: биллинг ещё не постнул,
`$0.2446` — нижняя граница, и в неё входит том, который не принадлежит никакому шагу. Метр самого
пода: 1 143 с × $0.74/ч = **$0.2350**.

**⏭️ С ЧЕГО НАЧАТЬ.** (1) `runpod_guard --step reader-v4 --step-cap 0.35 --close --note "reader-v4
settled"` — как только прогон биллинга ответит (сегодня честно отказал: «no billing rows yet»);
(2) **сидение по результату v4** — вход оператора, материал §5–§6 отчёта; (3) `prep-b` ($0) после
сидения.

## 🔥 What's Hot

**🔥 ГЕЙТ ДОЛЖЕН СТОЯТЬ НА ТОМ, ЧТО ТРАТИТ — подтверждено двумя прогонами в один вечер.**
v3: go/no-go мерил прогрев, прогрев не наступил, serverless-бут съел $0.3918 при капе $0.35 —
**ни одна ветка инструмента выстрелить не могла**. v4: под, кап в СЕКУНДАХ (1 702.7 с при $0.74/ч,
1 642.7 после вычета 60 с на само удаление), два дедлайна на одной оси (контрактные 12 мин от старта
генерации, affordability от `create`), `--gate` возвращает **3=WAIT / 2=KILL / 0=GO** — цикл
наблюдения это КОМАНДА, а не человек, глядящий в лог. Бут вышел **175 с** и был виден всю дорогу.
**23 из 23 за $0.2446 против $0.3918 за ноль.** [[a-gate-downstream-of-the-spend]]

**💸 ЦЕНУ КАРТЫ ЧИТАТЬ В ДЕНЬ ПРОГОНА.** Контракт считал убитый бут по $0.59/ч; 4090 в EU-RO-1
стоит **$0.74/ч** (`runpodctl gpu list`, 16.08, SECURE, stock Low) — те же 12 минут это **$0.148**,
а не $0.12, и это двигает КАЖДЫЙ дедлайн. Что ещё было в EU-RO-1 в тот день: RTX PRO 4500 Blackwell
$0.72 (High) · RTX PRO 4000 Blackwell $0.57 (Medium) · L4 $0.49 (Low).

**📐 ПРОЕКЦИЯ ОСТАТКА — ДВЕ НОГИ, СВЯЗЫВАЕТ ПЕССИМИСТИЧНАЯ.** На первом ответе: 22 непрочитанных
треда на 1 прочитанный (фактор 22.0) против 127 непрочитанных платных комментов на 7 (18.14) —
связывает `by_thread`. Первый черновик v4 имел ОДНУ ногу; одна нога слабее в единственном
направлении, в котором гард капа слабеть не имеет права. Восстановлено ДО создания пода (Dv449).
Порог публикуется в секундах: `(usable − elapsed) / (фактор × прочитано)`; доллары на границе
печатают одно и то же. [[a-published-ratio-is-not-the-gates]]

**🖥️ ПОДОВЫЙ ТРАНСПОРТ В ДЕРЕВЕ И ПЕРЕИСПОЛЬЗУЕМ.** `scripts/read_threads_reader_v4.py` (Mac: пак,
часы, ворота, ingest) + `scripts/reader_v4_pod_runner.py` (под: ТОЛЬКО генерация, ни парса, ни
скоринга) + `scripts/runbook_reader_v4.md`. Пак — 23 айтема с зарегистрированной sha каждого
запроса; под РЕНДЕРИТ сам и отказывает при расхождении — одна проверка накрывает и правку коммента
в сторе, и том, отставший на сессию. Оба отказа — ДО загрузки модели, тесты утверждают
`loaded == []`. Раннер кладётся в `/workspace/`, **никогда** в `/workspace/repo/scripts/` — иначе
`git status --short` на поде перестаёт быть доказательством стейджинга.

**⚠️ `--gate` читает КОПИЮ файла, который пишет под.** «Ответ не пришёл» — утверждение о ФАЙЛЕ.
scp partial-jsonl обязан идти ПЕРЕД каждой проверкой; в записи ворот теперь есть `read_from` с путём
и временем копии, чтобы протухшее чтение было видно в артефакте, а не приезжало необъяснимым KILL.

**🧮 ЧТО ИЗМЕРЕНО СВЕРХ БАРОВ (v4).** 19 из 23 ответов распарсились против 13 у probe-b — и **ни
один из девяти зарегистрированных контейнерных ремонтов не сработал**; refuse-on-conflict, наоборот,
снял ДВА ответа, один из которых probe-b принимала. Ближайшее к абляции: собственные 23 ответа
probe-b под сегодняшним парсером дают **4** отказа против **10** «как прогонялось».
`finish_reason: length` — **0 из 23**. **137.83 токена** на ЗАПРОШЕННУЮ строку `per_comment`;
вернулось **93 из 111** (0.838) — даже под промптом «строка на КАЖДЫЙ комментарий» шестой строки
нет, и оттуда же три `absent` в баре 4. Секунды: **39.461 с/тред** против 31.6376 у probe-b на той
же карте = **1.247×**.

**🪟 ОКНО СПРОГНОЗИРОВАНО, НО НЕ ОТКРЫТО (Dv433 закрыт замером).** Самый большой тред 129-тредовой
ячейки — **125** платных комментов; при 137.83 токена на запрошенную строку это ≈**17 200 токенов
вывода на ОДИН тред** против `READER_MAX_NEW_TOKENS = 2000`. Число есть — решение оператора.

**🔤 СКЛЕЙКА СЛОВАРЯ — ЭТО БАР, И ОНА СИММЕТРИЧНА (Dv441 закрыт).** «категория» ≡
«категория_личное» с ОБЕИХ сторон везде, где бары 1 и 4 сравнивают `subject_type`: и голд-клетка, и
ответ читателя. Голд r2 остаётся голдом, промпт не тронут — эквивалентность зарегистрирована как
ПРАВИЛО СКОРИНГА (`scoring_rules.vocabulary_collapse`), а скорер держит её область против записи.
Стоила ровно разницы колонок: бар 1 с 1 до 2, бар 4 с 0.357 до 0.500. **Четыре оставшихся
расхождения бара 4 — НЕ словарь**: читатель называет комментарий о категории комментарием о сети
(21601, 580124, 580129, 48283).

**🎚️ БАР 3 — ПЯТЬ ТРЕДОВ, N1 ИСКЛЮЧЁН С ПРИЧИНОЙ (Dv440 закрыт).** v2's `excluded_with_cause`
восстановлен дословно из замороженной записи; предикат `bar_three_over_answers` — прежний,
ИМПОРТИРУЕТСЯ из продюсера v3, не копируется. Отказ никогда не ноль; без единого вердикта бар
**UNREACHABLE**, что не проход. N3 (`@sashafitnesslife:3939`) несёт **0 платных комментов** — его
ноль делает глушитель, а не читатель, так что бар двигают ЧЕТЫРЕ треда из пяти.
[[a-bar-that-counts-passes-on-an-unreadable-reply]]

**🔧 Парсер терпим к КОНТЕЙНЕРАМ и строг к ДОМЕНАМ — ровно три ремонта.** (1) два top-level объекта
сливаются, **и ключ в обоих с разными значениями = ОТКАЗ**, никогда не last-wins; (2) `{}` вместо
списка → `[]`; (3) map по **msg_id** → список (ключи ВЫБРАСЫВАЮТСЯ). Не чиним: `aspect: null`,
`from_post`-сигнал без `evidence`, голый фрагмент без скобок. `repairs: [...]` едет на КАЖДОМ
вердикте. Отказы v4: `two disagreeing objects: name` · `…: quote` · `signals.aspect is not a string`
· `missing field: evidence`. Три контейнерные формы, в которых тонула probe-b, исчезли.

**📐 Три зарегистрированных текста читателя, и v3 — OPT-IN.**
v1 `b272115637f784ad…` · v2 `9d281bc80f18c91b…` · **v3 `22533644cf35420e…`** (6 630 символов).
`reader_messages_gm4` держит дефолтом **v2**: каждый вызывающий без `task` — вызывающий, чьи улики
уже на диске. v3 называют только контракты прогона.

**📊 Ячейка ценза читателя ИЗМЕРЕНА: 129 тредов · 1 032 платных коммента**
(`results/gate_census_w1_reader.json`, narrow · varto off · plus-spam/scam on). ⚠️ **129 — это ТАКЖЕ
thread-count `narrow|silencers_off`**; различает только платный счёт (1 032 против 1 116) — цифру
треда одну цитировать НЕЛЬЗЯ.

**🎯 Популяция probe-b production-reachable ЦЕЛИКОМ.** Все ЧЕТЫРЕ инъецированных треда (E1, E4a,
E4b, **N3**) входят в читательскую ячейку — убирал их `varto_rule`, рулинг 3 его снял. Дайджест
`ccef35fa4b9c771f…` НЕ двигается: он считает флаги probe-b, статус под новой ячейкой лежит РЯДОМ.

**🧪 Голд r2 — 12 ячеек и ни байтом больше.** `CELLS = 12` — зарегистрированный литерал,
тринадцатая ОТКАЖЕТ. `reader_gold_w1.json` (v1) не тронут — на него смотрят два запечатанных пина.
`src/market_pulse/scorer.py` не тронут ни одним контрактом v3/v4 (Dv431): его байты пинят четыре
запечатанные записи.

**⚙️ Карта: RTX 4090. probe-b (serverless): 727.664 биллинговых секунды воркера на 23 тредах =
31.6376 с/тред · 5.4303 с/платный коммент. v4 (под): 907.6 с генерации = 39.461 с/тред, бут 175.1 с,
жизнь пода 1 143 с.** Единицы РАЗНЫЕ и складывать их нельзя: у serverless это биллинговые секунды
воркера, у пода — секунды генерации вокруг одного `ReaderClient.read`, а бут и простой пода не в
этой колонке вообще. Деньги — только бар 5, из леджера гарда.

**🔄 ТЫ ЗДЕСЬ: сидение по результату v4, потом джойнт-планирование цикла-2 и Фазы 6.**
Фаза 5 закрыта, Фаза 4 закрыта, линия цикла-2 открыта и заякорена.

## ⏭️ Next

1. **Закрыть шаг `reader-v4`**, когда запостится биллинг:
   `python3 scripts/runpod_guard.py --step reader-v4 --step-cap 0.35 --close --note "reader-v4 settled"`.
   Отказ по неотвеченному обходу — правильное поведение, а не сбой (**Dv455**).
2. **Сидение по результату v4** — вход оператора. Что на столе:
   - бар 4 = 0.500 при 0.80; четыре расхождения из четырнадцати — чтение ПРЕДМЕТА, не словарь;
   - три строки `absent`: читатель не написал `per_comment` вовсе (вернулось 93 из 111);
   - бар 1 = 2 из 5: F2 и F3 не найдены, причём F3 — вообще отказ парса (`…: quote`);
   - ремонтная половина парсера не сработала НИ РАЗУ, refuse-on-conflict снял два ответа — стоит ли
     контейнерная терпимость своей цены;
   - улика по строкам: `results/reader_v4_w1.jsonl` (340 627 Б) — запрос, сырой ответ, исход парса,
     секунды, `finish_reason`.
3. **`prep-b`** — сбор Сільпо / Varus / Маркетопт + докачка корпуса, $0. Слово оператора: ПОСЛЕ
   читателя.
4. **Окно** — 17 200 токенов на самый большой тред против потолка 2 000. Решение оператора; никакой
   оконный проход не открыт.

**Кандидаты цикла-2 в порядке ценности:**

1. **Деньги — $19.3132 свободно.** Влезает всё решённое (окно-2 ≈$4.8 · читатель на поде ≈$0.25 за
   проход · батч-пробник $2.13 · том ≈$2/нед); история 11 143 — не влезает.
2. **Батч-паритет — СПРОЕКТИРОВАН, решение за оператором.**
   `results/batch_cycle2_projection.json`. Из записей выводится НЕРАВЕНСТВО: шаг с batch 16 требовал
   **23.99 ГиБ** сверх весов, у 4090 их **3.99** — короче в **6.02×**, единственный кандидат
   **batch 2**, и влезет ли он — **НЕ ИЗМЕРИМО** без живого пробника. Риск не память, а ОТВЕТЫ: при
   batch 16 разошлись **6 строк из 666**. Пробник: фикс **$0.1520** + **$0.0013025**/строка; арм 758
   с контролем — **$2.1266**. Окупаемость −30%: **$4.3536** на истории, **$1.4511** на окне.
3. **Сбор листовок Сільпо / Varus / Маркетопт** — 3.18 (7)(d) + **3.20 (6)**. Бесплатно, в `prep-b`.
4. **Докачка корпуса** — сборка стоит с 08.08.
5. **История 11 143** — вход бесплатен, ~13 ч, ЖДЁТ батча И денег.
6. **Serving-латенси** — лечение ОТЛОЖЕНО до «готовим прод» ([[serving-latency-deferred]]).

**Долги-входы следующих регистраций:** цена страницы листовки **10.408 с/стр (n=159)** — старые
записи НЕ перескориваются. Ценз `results/gate_census_w1.json`: narrow|silencers_on = **111 тредов,
912 платных комментариев** (популяция ПРОБ; читательская ячейка — отдельный файл). Два вопроса из §5
отчёта fix-a и **метка типа поста для окна-1**. Мелочи step-0.5: заголовок `t5_depth`, валюта ₴ в
шапке промо-таблицы, fix-b(2) «две колонки — одно число»; пачка закрытий 22 старых шаговых леджеров.

## 🚧 Blockers

**⛔ Бары 1 и 4 ПРОВАЛЕНЫ, и попытка потрачена.** Это больше не «ни один бар не взят»: 2 и 3 взяты,
1 и 4 измерены и не дотянули, 5 ждёт биллинга. Снимает это только НОВАЯ регистрация после сидения —
код не мешает, инструмент и транспорт в дереве и оплачены.

**🟡 Dv455 ОТКРЫТ — шаг `reader-v4` не закрыт.** Биллинг не постнул. `$0.2446` — нижняя граница,
названный долг, не потеря.

**✅ Снято 16.08:** Dv426 (ремонт 3 остаётся УЗКИМ — не переоткрывать) · Dv433 (потолок вывода
замерен: 0 из 23 `length`, 137.83 токена на запрошенную строку) · Dv440 и Dv441 (закрыты рулингами и
измерены) · Dv443/Dv444 (шаг v3 закрыт на $0.393577; биллинг подтвердил 1 211 005 мс исполнения —
настоящий холодный старт, а не очередь srv-2b) · Dv439 и Dv445 (два гарда, отказывавшие платному
прогону не по делу) · межледжерный разрыв.

**🟢 Dv447 — гард починен на собственном отказе.** Закрытие шага v3 покраснило зелёную неделю
`make check`: `--close` не пишет свидетельство в живой леджер линии, а отказ по капу возвращается
раньше этой ветки, так что свежее чтение баланса жило в одном файле. Теперь свидетельство пишется
РЯДОМ с закрывающей записью, до любого раннего возврата; `line_reading()` — одна форма для обоих
писателей. [[a-settlement-is-a-reading-too]]

**⚠️ Worktree этого репозитория НЕ отвечает за весь suite.** Стор под `data/` в gitignore — 164
падения по причинам, не связанным с коммитами, плюс abort на коллекции `tests/test_train_qlora.py`.
Утверждение «зелено на каждом коммите» проверяется ПО ФАЙЛУ, который читает только закоммиченное
(так три красных коммита 16.08 и были найдены — я сначала назвал не те и не столько).
[[a-commit-must-run-its-own-suite]]

**Деньги — три числа, которые легко перепутать.** Шаг цени ПО БИЛЛИНГУ с исключением всегда-включённых
видов ПО ВИДУ: probe-b **$0.313162**, reader-v3 **$0.393577**. Фазу и линию — пессимистичным
максимумом двух чтений. Дельта баланса меряет СЧЁТ, а не шаг, и после закрытия шага растёт вечно.
Остаток ВЫВОДИТЬ (`CAP - spent_usd`), а не читать из `sessions[-1].remaining_usd`
([[the-field-true-under-the-old-constant]]). Записи леджера **anchor-relative** — `spent_usd` по
сессиям НЕ суммируется.

**⚠️ Якорь цикла-2 ОДНОРАЗОВЫЙ, и сюита однажды его уже написала (Dv424).** Снятие порога $40
открыло место записи, которое порог закрывал СЛУЧАЙНО. Редирект теперь autouse и НА МОДУЛЬ. Правило
шире: **снимая порог, спрашивай не что перестаёт отказывать, а что становится ДОСТИЖИМЫМ.**

**⚠️ 22 шаговых леджера в третьем состоянии.** Закрыты probe-b, reader-v3 и линия цикла-2; остальные
не несут времени якоря и честно печатают «нижняя граница». Закрыть каждый дёшево
(`--close --since` с окном из его же отчёта).

**⚠️ Зарегистрированная цена страницы листовки известна НЕВЕРНОЙ.** 4.2794 с в
`results/sku_b_positions_skub2.json` снята с постеров; полная популяция из 159 страниц стоит
**10.408 с**. Не переиспользовать без рулинга.

**⚠️ Очередь комментов читает 0, а не 11 143.** Вотермарк накрыл всё старое. Строки на диске целы,
но контракт, который захочет историю, обязан САМ сбросить поле `inference` в
`data/loop_cursor.json` ([[a-watermark-past-a-window-buries-the-backlog]]). Побочный эффект: смоук по
реальному стору печатает нулевой сплит 3.19 — это не дефект правила (Dv332). **Сколько из 11 143
бестекстовые — НЕ посчитано**; доля окна 26.8% на историю НЕ переносится, а сам подсчёт бесплатен.

**⚠️ `build_validate_pack.py` перезаписывает пакет без `--force`-гарда, а его sha ЗАПИНЕН.**
`results/validate_5c2_returns.json` отвечает ровно на `2fad5339…`; перестройка пакета уронит возврат
сидения с «the sitting read …».

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
