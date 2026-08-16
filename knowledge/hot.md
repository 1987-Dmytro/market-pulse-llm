<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-08-16 13:49:52 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
c3b6b70 docs(report): cycle2-money -- the figures re-read from the artifacts, and hot.md  stops booting a retired blocker
e941b34 fix(guard): one balance reading, one printed line
536a643 docs(report): cycle2-money
c86d3fd ledger: Phase 4 is CLOSED, probe-b's step is settled at its own resources
27eba42 fix(guard): Dv411/Dv412 -- a step is read twice, decomposed by kind, and can be closed
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

**Last update:** 2026-08-16, после контракта `cycle2-money` ($0 GPU, облако READ-ONLY). Закрыты два
леджера, приземлён амендмент **3.23**, оплачены два ADR-долга ([[serving-latency-deferred]],
[[reader-sitting-16-08]]). `make check` **2 584 / 2 skipped**.

День 15.08 дал восемь контрактов (`cycle2-prep-a`, `phase6a`, `phase6b`, `fix-a`, `fix-b`, `fix-c`,
`probe-a`, `probe-b`), три амендмента SPEC (3.20, 3.21, 3.22), командный центр и две платные пробы
слоя комментных сигналов; по БИЛЛИНГУ **≈$0.388** GPU (probe-a $0.075 + probe-b $0.313162).
Подробности — [[2026-08-15]]; решение дня — [[reader-probe-card-and-interface]].

**✅ БЛОКЕР ГВАРДА СНЯТ (`cycle2-money`, 16.08, $0).** Dv411 и Dv412 починены: шаг читается ДВУМЯ
чтениями (дельта баланса + ходок по биллингу от `anchored_at`), разложение идёт ПО ВИДАМ, том
`network-volume` печатается своей строкой и никогда не входит в цифру пробы, а шаг можно ЗАКРЫТЬ.
probe-b закрыт на **$0.313162** из $0.35 — внутри капа; том ($0.136111) назван рядом. Отчёт —
`docs/reports/cycle2-money.md`.

**💰 ФАЗА 4 ЗАКРЫТА: $32.4708 из $33.00** (финальное чтение 2026-08-16T11:09:48Z, запись дописана
гардом в `results/spend_phase4.json`). Оба чтения расходятся на $19.99 — это пополнение оператора
15.08, пришедшее ПОСЛЕ якоря леджера, поэтому связывает ходок по биллингу, а не дельта.

**⛔ МЕЖЛЕДЖЕРНЫЙ РАЗРЫВ ОТКРЫТ — В НЁМ НИЧЕГО НЕ ЗАПУСКАТЬ (SPEC 3.23 (3)).** Гард отказывает на
любом старте и это правильно, а не пробой капа. **НО РАЗБЛОКИРУЕТ ЕГО НЕ ПОПОЛНЕНИЕ.** Приёмка
16.08: порог «баланс ≥ $40» в 3.23 (2) — **ошибка тимлида**, построенная на непроверенном допущении
«пополнение придёт новым, поверх». Деньги линии цикла-2 УЖЕ на счету: пополнение $20 легло **15.08**,
и доказывает это закрывающая запись Фазы 4 — разрыв двух её чтений ровно **$19.99**. Порог снимается
амендментом **3.24** (шаг 0.5 `reader-v3-prep`), после чего якорь берётся ОСОЗНАННЫМ прогоном от
текущего баланса **$22.52**. Новых платежей не требуется. Пока разрыв открыт, счёт тянет только том
(~$0.0092/ч ≈ $0.22/сутки).

**⏭️ С ЧЕГО НАЧАТЬ ЗАВТРА.** Контракт **`reader-v3-prep`** ($0, уже в дереве:
`docs/PROMPT-reader-v3-prep.md`) — шаг 0.5: амендмент **3.24** снимает порог $40 и якорит линию;
затем контейнерный рулинг парсера, v3-промпт, голд-r2, ячейка ценза varto-off, замороженная
регистрация. Платная перечитка 23 тредов — СЛЕДУЮЩИЙ контракт `reader-v3-run`, кап $0.35.
Рулинги — [[reader-sitting-16-08]]. `prep-b` — после читателя.

## 🔥 What's Hot

**🔬 СЛОЙ КОММЕНТНЫХ СИГНАЛОВ: инструмент есть, ни один бар не взят.** Две пробы, $0.4173.
Читатель `reader_thread_gm4_v2` (`9d281bc80f18c91b…`) зарегистрирован; v1 (`b272115637f784ad…`)
остаётся зарегистрированным и обслуживаемым — probe-a купил под ним три вердикта, и его улики обязаны
пере-рендериваться. Бары на популяции из 23 тредов: **2/5 · 2/4 · 0 сигналов (проходит) · 0.357**.
Отчёты `docs/reports/probe-a.md` и `docs/reports/probe-b.md`, решение —
[[reader-probe-card-and-interface]].

**✅ Вопрос карты ЗАКРЫТ: `ADA_24` (RTX 4090), 2.64× от L4 при той же цене за секунду.**
`gpuIds` читается БЕСПЛАТНО из ответа на `serverless create` — создание не биллится, биллятся только
запросы; фактическая карта берётся из `runtime.gpu` воркера, и эти два поля могут расходиться
(probe-a просил «NVIDIA L4», получил `AMPERE_24`). **Ни одна ставка $/с не переезжает между
контрактами без названной карты.** Замерено: 20.759 с/тред, 5.661 с/платный коммент; окно из
111 тредов — **$0.71 / $1.58**. [[the-class-you-asked-for-is-free-to-verify]]

**⚠️ Связывает не чтение, а ИНТЕРФЕЙС.** v2 закрыл оба измеренных дефекта, ни один не вернулся — и
10 из 23 ответов всё равно отказаны шестью формами того же класса: `signals: {}` вместо `[]` (4, все
шумовые треды), ответ разбит на ДВА top-level объекта (2), `noise` словарём по msg_id (1),
`aspect: null` (1), у `from_post`-сигнала нет ключа `evidence` (2). Коэрс только контейнеров:
**13 → 19 из 23**, entity 2 → 3 из 4. Терпимость к КОНТЕЙНЕРАМ — решение, которое принимается один
раз и отдельно от строгости к ДОМЕНАМ. [[a-container-defect-moves-to-the-next-field]]

**⚠️ Бар, который считает «ноль чего-то», проходит на нечитаемом ответе.** Единственный взятый бар
(шум) — ноль по четырём тредам без вердикта вообще. Любой будущий бар с таким предикатом обязан
считаться по СУЩЕСТВУЮЩИМ ответам, и это должно стоять в самом баре, а не в пост-ран разборе.
[[a-bar-that-counts-passes-on-an-unreadable-reply]]

**🚩 Два вопроса сидению, оба с измерением.** (1) Маркер-правило SPEC 3.21 (1) — платёжные ворота
читателя: E1, E4a, E4b, N3 снимаются ДО оплаты, probe-b купил их мимо гейта (`injected: true`,
никогда не в продакшн-агрегат) и получил **2 из 4 entity-кейсов**. (2) `категория` vs
`категория_личное`: 8 из 14 голд-строк держатся на слове, которое `docs/PLAN-comment-signals.md`
перестал демонстрировать 15.08 — бары считаются и как зарегистрировано, и с коллапсом двух слов.

**🔄 ТЫ ЗДЕСЬ (рукой тимлида в STATUS, приземлилось на закрытии дня): джойнт-планирование цикла-2 и
Фазы 6.** Фаза 5 закрыта, хроника до 12.08 в STATUS сжата — полная история в git этого файла.
Фаза 4 закрыта на $32.4708 из $33.00; линию цикла-2 ($20.00) открыл оператор 16.08, якорь ждёт
пополнения. Все $0-задачи ниже можно делать не дожидаясь.

**`fix-a` СДЕЛАН (15.08) — правила матчера стали ЗАКОНОМ, и бренд-поверхности честные.**
**Амендмент 3.21** в SPEC: (1) правила текстового матчинга живут в `config/watchlist_rules.yaml`,
ревизия **r1**, а `config/registry.yaml` и `config/lexicon.yaml` запечатаны пинами и под правила НЕ
редактируются; (2) ратифицирована архитектура сигналов из комментариев (`docs/PLAN-comment-signals.md`);
(3) любая поверхность «бренд × тональность» подписана «повідомлення, де згадано бренд», НИКОГДА
«ставлення до бренду»; (4) промо-поверхность отвечает ТАБЛИЦЕЙ позиций (это `fix-b`).
Результат: 11 рядов с брендом → **3**. Ключ — ревизия **opt-in ПО ПРИНУЖДЕНИЮ**: запечатанный
`scripts/window_summary_5c2.py` не редактируется, значит старое поведение обязано остаться дефолтом,
а `find_watchlist_brands` берёт правила и `carrier` только вместе (одно из трёх правил ограничено
текстом КОММЕНТАРИЯ, и область, которую вызывающий не назвал, ничем не проверяется).

**⚠️ Раскол якоря делают ДВЕ таблицы, а не колонка `rules`.** `comment_brands` — то, чем меряли
запечатанную запись, и SQL зеркала (`aggregates.mirror`) не изменился ни на символ;
`comment_brands_r1` — презентация, и каждый блок экспорта из неё несёт `watchlist_rules`. С колонкой
каждый существующий запрос стал бы неверным по умолчанию до тех пор, пока кто-то не вспомнит фильтр.
Проверено в ОБЕ стороны: позитив — 902/902 листа сходятся; негатив (тест) — подменяем таблицу
зеркала и гейт краснеет ровно на 12 листах `brand_attribution` из 35 выведенных матчером.

**⚠️ `src/market_pulse/brands.py` сам запинен** в `producer.borrowed` ДВУХ запечатанных записей.
Любая правка матчера двигает его хэш; вошёл в семью sha-подстановки СВОИМ кортежем (`MOVED_BY_R1`)
и своим свидетелем — общая ветка проверяет свидетеля 3.19 (`has_text`), которого brands.py никогда
не выучит.

**ФАЗА 6b СДЕЛАНА (15.08, `phase6b`) — командный центр открывается.** `dashboard/index.html`
собирается `scripts/build_dashboard.py` из экспорта + `config/metrics.yaml` + нового
`config/ui_strings.yaml`: девять вкладок T0–T8 по вопросам PRODUCT.md, UA/EN и светлая/тёмная
переключателями, всё инлайном, **ни одного внешнего запроса** (t.me у строк drill-down — единственные
внешние ссылки), экспорт вложен в страницу байт в байт. Два сборки байт-в-байт, и закоммиченный файл
ЕСТЬ эта сборка. 27 раскрытий drill-down, 196 строк жребием (сид на стратум), каждое объявляет поле
экспорта со своей популяцией — **билд отказывает**, если строки не сходятся с числом. Заглушки двух
классов: семь `NOT_COMPUTABLE` экспорта и четыре `GAPS` (бэклог 6a, выше). Приёмка — сидение по
квизу «10 секунд на вопрос». Первая вкладка открыта РАЗМЕТКОЙ, не скриптом (Dv353): страница,
у которой видимое состояние приходит с JS, — пустой центр в момент любой ошибки в нём.

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

**⚠️ Измерение принадлежит РЕЕСТРУ, а не уликам (Dv341).** Срез по сегментам, построенный от
таблицы `channels` (её наполняют собранные строки), отрисовывал **семь** карточек там, где реестр
держит восемь: `food_quality` молчал всё окно. Починено таблицей-измерением `segments`, а НЕ
расширением `channels` — `coverage.channels.with_a_row` считает строки в `channels`, и вставка всех
66 хендлов дала бы 66/66. Тот же аргумент уже был выигран дважды в этом контракте (`watchlist`,
`PROMO_CHAINS`) и не был перенесён — [[a-dimension-belongs-to-the-registry]]. Три состояния
различимы: говорил · нёс улики без разговора (`regional`) · молчал (`food_quality`, rate = **null**,
не 0.0).

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

**Первым делом завтра:**

1. **`reader-v3-prep`** ($0, контракт уже в дереве). Шаг 0.5 — **амендмент 3.24**: снять ошибочный
   порог $40 из 3.23 (2) и заякорить линию осознанным прогоном от текущего баланса. Затем:
   контейнерная терпимость явным рулингом при строгих доменах, расхождение двух top-level объектов =
   **отказ, не last-wins**; v3-промпт «один JSON-объект, `[]` для пустого» с F1b/F1c/F2a; новая
   ячейка ценза (narrow · varto off · plus-spam/scam on) — **МЕРЯЕТСЯ, не выводится**; голд-r2
   именованной ревизией без правки `docs/REFERENCE-signals-w1.md`; замороженная регистрация.
2. **`reader-v3-run`** — платная перечитка тех же 23 тредов ~**$0.08**, бары против голда-r2,
   кап $0.35. Первый платный шаг против линии цикла-2.
3. **`prep-b`** — сбор Сільпо / Varus / Маркетопт + докачка корпуса, $0. Слово оператора 16.08:
   в очередь ПОСЛЕ читателя, «мы не закончили с комментариями».

**Сидение 16.08 закрыло то, что здесь стояло вопросом.** Четыре варианта §9 отчёта probe-b решены
как **A+B одной регистрацией**; маркер-правило и «категория» vs «категория_личное» отвечены
рулингами (3) и (4). Всё — [[reader-sitting-16-08]].

**Кандидаты цикла-2 в порядке ценности:**

1. **Деньги — ЛИНИЯ ОТКРЫТА, ЯКОРЬ НЕТ, НО ДЕНЬГИ ЕСТЬ.** Фаза 4 закрыта на $32.4708 из $33.00;
   дальше работает линия цикла-2 **$20.00** (SPEC 3.23), и это деньги, уже лежащие на счету.
   В линию влезает всё решённое (окно-2 ≈$4.8 · читатель ≈$1.6 · v3-проба $0.08 · батч-пробник
   $2.13 · том ≈$2/нед); история 11 143 — не влезает. Якорь — шагом 0.5 `reader-v3-prep`.
2. **Батч-паритет — СПРОЕКТИРОВАН, решение за оператором.**
   `results/batch_cycle2_projection.json`. Из записей выводится НЕРАВЕНСТВО: шаг с batch 16 требовал
   **23.99 ГиБ** сверх весов, у 4090 24 ГБ их **3.99** — короче в **6.02×**, поэтому 16/8/4/3
   исключены и единственный кандидат — **batch 2**; влезет ли он, **НЕ ИЗМЕРИМО** без живого пробника.
   Главный риск не память, а ОТВЕТЫ: при batch 16 разошлись **6 строк из 666**, тогда как на
   24-строчном карве все размеры были байт-в-байт. Пробник: фикс **$0.1520** + **$0.0013025**/строка
   (потолок по batch 1); арм 758 с контролем — **$2.1266**. Окупаемость: −30% даёт **$4.3536** на
   истории 11 143 и **$1.4511** на одном окне после 3.19; −50% — **$7.2574** / **$2.4189**.
   **Само правило 3.19 уже сэкономило $1.7727 на окне и бесплатно — больше, чем дал бы −30%.**
3. **Сбор листовок Сільпо / Varus / Маркетопт** — 3.18 (7)(d) расширен **амендментом 3.20 (6)**
   (рулинг оператора 15.08: Маркетопт обязателен). Бесплатно, не начат, идёт в `prep-b` вместе с
   докачкой корпуса. В окне-1 листовочные СТРАНИЦЫ есть только у АТБ; у Сільпо/Varus/Маркетопта
   позиции только из текстов постов — записано в
   `dashboard_data_w1.json :: not_computable.leaflet_depth_for_silpo_varus_marketopt`.
4. **Докачка корпуса** — сборка стоит с 08.08.
5. **История 11 143** — вход бесплатен, ~13 ч на текущей скорости, ЖДЁТ батча И денег.
6. **Serving-латенси** — разобрана 16.08, лечение ОТЛОЖЕНО до «готовим прод»
   ([[serving-latency-deferred]]). До того окна и история идут на текущем стеке; ~4 мин на одиночный
   запрос — принятая цена отладки, не дефект.

**Долги-входы следующих регистраций:** цена страницы листовки **10.408 с/стр (n=159)** — старые
записи НЕ перескориваются. Ценз `results/gate_census_w1.json`: narrow|silencers_on = **111 тредов,
912 платных комментариев**, окно стоит **$0.71 / $1.58**. Два вопроса из §5 отчёта fix-a (два чтения
правила `selianske`, коллизия `varus-pl`) и **метка типа поста для окна-1** — без неё четвёртый
глушитель нечем включить. Мелочи step-0.5: заголовок `t5_depth`, валюта ₴ в шапке промо-таблицы,
fix-b(2) «две колонки — одно число».

## 🚧 Blockers

**⛔ МЕЖЛЕДЖЕРНЫЙ РАЗРЫВ (SPEC 3.23 (3)) — единственный блокер, и он снимается КОДОМ, не деньгами.**
Фаза 4 закрыта, линия цикла-2 не заякорена, между ними запускать нельзя ничего; гард отказывает на
любом старте и это ПРАВИЛЬНО — не пробой капа. Разблокировка: **амендмент 3.24** снимает порог
`CYCLE2_ANCHOR_MIN_USD = 40.00` (ошибка тимлида — допущение «пополнение придёт поверх»), затем якорь
берётся осознанным прогоном от текущего баланса **$22.52**. Деньги линии уже на счету с 15.08.
Пока разрыв открыт, счёт тянет только том: измерено за 16.08 — **0 строк pods, 0 строк serverless**,
одна строка network-volume **$0.106944**. **У разрыва есть цена и нет владельца**, поэтому 3.24
стоит первым шагом следующего контракта, а не позже.

**Деньги — три числа, которые легко перепутать, и правило для каждого.** Шаг цени ПО БИЛЛИНГУ с
исключением всегда-включённых видов ПО ВИДУ: probe-b — **$0.313162** из $0.35, внутри капа. Фазу и
линию — пессимистичным максимумом двух чтений. Дельта баланса меряет СЧЁТ, а не шаг, и после
закрытия шага растёт вечно — поэтому шаг и леджер теперь можно ЗАКРЫТЬ, и закрытый читает свою
осевшую цифру, а не дельту. Остаток ВЫВОДИТЬ (`CAP - spent_usd`), а не читать из
`sessions[-1].remaining_usd` ([[the-field-true-under-the-old-constant]]). Записи леджера
**anchor-relative** — `spent_usd` по сессиям НЕ суммируется.

**⚠️ 22 шаговых леджера в третьем состоянии.** Ни один из 23 `results/spend_*.json` шага не несёт
времени якоря, закрыт только probe-b. Остальные при опросе честно печатают «нижняя граница». Закрыть
каждый дёшево (`--close --since` с окном из его же отчёта), но никто этого не заказывал.

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

**Якоря, которые не трогают:** `results/spend_phase4.json` — ЗАКРЫТ, append-only, никогда не
регенерируется. `results/spend_5c2run.json` — закрытый якорь сессии, драйвер отказывается его
переписать. `results/spend_sku_b*.json`, `results/spend_skub2.json`, `results/spend_probe_b.json` —
тоже закрыты. Том биллится всегда: **≈ $0.012/ч**.

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
  Указатель поэтому отстал на ПЯТЬ амендментов (3.19, 3.20, 3.21, 3.22, 3.23 — каждый сам себе
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
  decision. `results/spend_cycle2.json` will be its successor and does not exist yet: the guard
  anchors it on the first reading of $40.00 or more (SPEC 3.23 (2)).
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
