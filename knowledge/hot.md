<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-08-12 19:03:46 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
958716d docs(report): the commit count and the clock from git log, and the price_from negative
51711db docs(report): skub2-run
489271e data(skub2-run): bars 1 and 3 over the B-prime gold, bar 2 pending the team lead
fb4e8dd data(skub2-run): the 138 bought, instrument v2, 101 positions and no unreadable reply
0793a3c fix(skub2-run): the registered warm-up reaches a full run, not only a resumed one
```

## 📋 Recent decisions

- `sku-b-pilot-closed-by-measurement.md` — The sku-b pilot closes as "instrument not ready" BY MEASUREMENT: two bars of three failed
- `INDEX.md` — Decision records
- `sku-b-v3-refusal-and-v4.md` — The v3 session was refused by its own gate: three marginals, a fresh ledger, and a $0.65 cap

## 📅 Recent daily logs

- `2026-08-12.md`
- `2026-08-11.md`
- `2026-08-10.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->
# Hot Cache — curated

**Last update:** 2026-08-12 19:01 (arch-a ✅, uni-a ✅, uni-b ✅, sku-b-prep ✅, sku-b-run ✅ ПРИНЯТ,
sku-b-v3-prep ✅, sku-b-v3-run ⛔ ОТКАЗ на воротах — попытка ЦЕЛА, sku-b-v4-prep ✅ $0,
sku-b-v4-run ✅ 121 куплен, **sku-b-close ✅ $0 — ПИЛОТ ЗАКРЫТ ИЗМЕРЕНИЕМ, 2 планки из 3 FAIL**,
sku-miss-pack ✅ $0, skub2-prep ✅ $0, skub2-fix ✅ $0, **skub2-run ✅ 138 куплены за $0.2764 —
ПЛАНКА 1 = 0.9800 PASS, планка 3 = 0.8667 PASS, планка 2 ЖДЁТ чтения тимлида**).
**sku-a ✅, R1–R5 ратифицированы, голд text30 размечен, SPEC 3.17 (7)–(14) — закон.**
Артефакты: **`results/sku_pilot_prereg_b2.json` (B′: голд 37 пар / 10 постов, 138 элементов, кап
$0.65 — ПРЕДРАНОВАЯ УЛИКА, не перезаписывается)**,
**`results/sku_b_positions_v4.json` + `.jsonl` (СЛИТЫЕ, 138 источников)**,
**`results/sku_b_positions_skub2.json` + `.jsonl` (138 источников, 101 позиция, 0 нечитаемых,
80 пар — ДАМП ДЛЯ ЧТЕНИЯ ПЛАНКИ 2)**,
**`results/sku_bar_verdicts_skub2.json` (планки 1 и 3 по голду B′; планка 2 = n и НИ ОДНОГО
значения; `closure` UNDETERMINED)**, `results/spend_skub2.json`,
`results/sku_bar_verdicts.json` (закрытие ПИЛОТА, запечатано — не перезаписывать),
**`results/sku_b_pair_verdicts.json` (чтение тимлида, 45 ключей / 61 строка)**,
**`results/sku_depth_from_pct.json` (глубина: бейдж vs старая цена)**,
`results/sku_miss_pack.json` + `.md` (стол для чтения, вердикты уже сняты),
**`results/sku_miss_decomposition.json` (все 29 вердиктов, a=11·b=16·c=2, `final` = 37)**,
**`results/sku_pilot_serving_v2.json` (потолок 1200, РЯДОМ с v1)**,
**`results/sku_projection_b2.json` (4 угла против $0.65, самый дорогой $0.4004, запас $0.2496)**,
`results/sku_pilot_prereg_v4.json`, `results/sku_projection_v4.json`,
`results/sku_pilot_serving.json`, `results/spend_sku_b_v4.json`,
`results/sku_b_positions.json` + `.jsonl` (запечатаны), `results/sku_b_positions_v3.json` (отказ,
улика). Отчёты: **`skub2-prep.md` ← читать первым, секция `## Fix` — текущее состояние**,
`sku-b-v4-run.md` (секция `# Close` — итог пилота), `sku-b-v4-prep.md`, `sku-b-v3-run.md`,
`sku-b-v3-prep.md`, `sku-b-run.md`, `sku-b-prep.md`, `uni-a.md`, `uni-b.md`. Ещё:
`docs/ARCHITECTURE.md`, граф кода, `docs/PORTING.md`.
**Next: чтение планки 2 тимлидом — 80 пар против картинок страниц, дамп
`results/sku_b_positions_skub2.jsonl` (sha `5592b324…`). Транскрипция ложится в
`results/sku_b_pair_verdicts_skub2.json`; продюсер пересчитает долю из ключей этого файла и
ОТКАЖЕТ чтению, снятому над другим дампом. До этого чтения `closure` = UNDETERMINED и вердикта по
B′ нет.** Планка 1 сдвинулась ПО ДВУМ причинам сразу (перескоуп голда (13)(c) + инструмент v2) —
разложение не делалось; цифра тимлида для v1 на том же голде 0.703, из SPEC 3.17 (14).
Блок правится руками; секция выше — авто-ген, маркер НЕ трогать.
Длинная форма отклонений: `implementation-notes.md` (Dv100–120), `uni-a.md` (Dv121–124),
`uni-b.md` (Dv125–132), `sku-b-prep.md` (Dv133–147), `sku-b-run.md` (Dv148–153),
`sku-b-v3-prep.md` (Dv154–160), `sku-b-v3-run.md` (Dv161–168), `sku-b-v4-prep.md` (Dv169–175),
**`sku-b-v4-run.md` (Dv176–180, и в её секции `# Close` — Dv181–186)**, **Dv188–194 — только в
дневнике [[2026-08-12]]: лёгкий контракт 12.08 отчёта-файла не просит**,
`skub2-prep.md` (Dv195–210, и в её секции `## Fix` — Dv211–227),
**`skub2-run.md` (Dv228–236)**.
Дневники [[2026-08-12]] / [[2026-08-11]], ADR ниже.

## 🔥 What's Hot

**ПРЕРЕЖКА B′ НАПИСАНА. ГОЛД 37 ПАР / 10 ПОСТОВ, ВСЕ 138 ЭЛЕМЕНТОВ, КАП $0.65** (`skub2-fix` ✅
12.08, $0, тринадцать коммитов `2621d6f..4b0ed29`, `make check` 1985 / 2 skipped, префлайт 47/0).
SPEC 3.17 (14): четыре висевшие пары (#4 #9 #28 #29) — ВСЕ класс b, каждая с процитированными
страницами; итог **a=11 · b=16 · c=2**, `final` = 37. B1/B4/B5 РАТИФИЦИРОВАНЫ ((14)(b) — класс это
факт о ПАРЕ, не о бренде везде), кап (13)(d) $0.40 → **(14)(e) $0.65**. Пин прережки держит и `-7`,
и `-8`: закон без (14) не содержит фразы, которой этот ран разрешён.

**ЧТО ЭТО ПОКУПАЕТ, СКАЗАНО ДО ТРАТЫ.** Планка 1 — порог **0.75**; цифра самого тимлида по v1 на
новом голде — **0.703** (`docs/STATUS.md`, исполнитель её НЕ пересчитывал, SPEC §10). Пересмотр сам
по себе планку не берёт: инструменту v2 остаётся добрать ~**4.7 pp**. И 0.703 — уже дважды
поднятое число: правило исключения выведено из разбора ОШИБОК и умеет убирать только ошибки — 18
гарантированных промахов ушли, а девять пар на вычеркнутых в другом месте ключах остались, шесть из
них v1 уже находил.

**ДРАЙВЕР ПЕРЕВЕДЁН НА skub2, И ГАРД ПЕРЕЕХАЛ ВМЕСТЕ С НИМ (Dv208 оплачен).** `PHASE`/`CAP_USD`/
`LEDGER`/`PREREG` = `skub2` / `$0.65` / `spend_skub2.json` / `sku_pilot_prereg_b2.json` — ПЕРВИЧНЫЙ
набор, потому что у B′ нет resume-блока и skub2 идёт не-resume путём; тройка `RESUME_*` остаётся
v4-й. Две вещи сверх буквы контракта, обе на денежном пути: (1)
`check_the_constants_are_the_registrations` вызывался ВНУТРИ `if args.resume:` — единственный путь
со свежим капом, свежим якорем и свежей регистрацией был единственным непроверяемым; (2) `PIN`
переведён на `sku_pilot_serving_v2.json` — `assert_serving` сверяет `max_new_tokens`, старый пин
(800) отказал бы ПОСЛЕ оплаченного бута. Плюс `DUMP`/`RECORD` → `sku_b_positions_skub2.*`: старые
дефолты — запечатанные артефакты первой сессии.

**ИНСТРУМЕНТ v2** (`skub2-prep` ✅ 12.08, $0, шестнадцать коммитов `d3fa574..c85d595`).
Парсер: `-50%*` → 50.0 + `discount_footnote`, `6х100 г` → 100 г + `pack_count: 6` (НЕ умножается),
`від 39,90` → 39.9 + `price_qualifier: from` (приоритет `from` > `approx` > `exact`). Потолок
800 → **1200** — это то, на чём планка 1 потеряла свою самую плотную страницу (4401 p5,
`malformed JSON`, ПЯТЬ пропущенных пар на одной странице). Обрезанный хвост по-прежнему отказ:
потолок и парсер — две РАЗНЫЕ половины (13)(a). **Ни `pack_count`, ни `discount_footnote` никуда
не доезжают** (Dv199): колонки дампа выведены из фразы планки 2, а её (13)/(14) держат байт-в-байт.

**АЛИАСЫ СДВИНУЛИ SHA, КОТОРЫЙ ПИНЯТ ВОСЕМЬЮ ЗАПЕЧАТАННЫМИ ЗАПИСЯМИ — НИ ОДНА НЕ ПЕРЕПИНЕНА.**
`registry_before_the_latin_aliases` снимает правку (13)(b) и воспроизводит `920c7f20…` в точности;
`load_registry_as_pinned` отдаёт живой файл или реконструкцию по пину, а на всё остальное —
ОТКАЗ. Планки v4 пересчитываются в **0.3603 / 0.3279 / 0.8621** байт-в-байт. И побочный эффект,
который поймал тест, чей docstring его предсказал: «Rud» и «LIMO» казефолдятся в СВОИ ЖЕ brand_id,
поэтому `gold_key` отвечает `rud` там, где запечатанный референс хранит `raw:rud` — голд B′
ПЕРЕСОБИРАЕТСЯ по именам ревьюера, а не фильтруется, и префикс `raw:` нигде не срезается.

**СТОЛ ДЛЯ ЧТЕНИЯ ПЛАНКИ 1 — КАК ОН БЫЛ НАКРЫТ** (вердикты сняты полностью, см. выше: a=11 ·
b=16 · c=2) (`sku-miss-pack` ✅ 12.08, $0, семь коммитов
`1845b49..724d65c`). `results/sku_miss_pack.md` — 29 пропущенных голд-пар по постам: строка КАК её
написал ревьюер, отправленные страницы с sha и ответ инструмента на каждой (`brand_raw` / `[]` /
`UNREADABLE` с причиной), найденная половина рядом как контроль, 29 пустых ячеек `a|b|c` в конце.
Планка 1 пересчитана `sku_bar_verdicts.bar_one` (тот же `gold_key` с обеих сторон) и построчно
сверена с отгруженной вердикт-записью: **29 / 26 / 15** сошлись.
**Два флага на КАЖДОЙ строке, а не в шапке поста** — вердикт диктуется построчно: **16 из 29**
сидят на посту с нечитаемой страницей, **5** — на посту с извлечённым брендом, не совпавшим ни с
одним голд-ключом. Без флага такая строка читается как (a) «недочитал», хотя причина не в картинке.
**Разрыв словаря (решать оператору):** две из 29 — `raw:try-vedmedi` на 4340 («Three Bears») и
`raw:комо / komo` на 4381 («Komo») — извлечены под именем, которого нет в alias-таблице; класса для
этого в a|b|c нет, и пары нигде не заявлены (это была бы вторая матчинг-правила).

**ПИЛОТ ЗАКРЫТ ИЗМЕРЕНИЕМ. 121 КУПЛЕН, ПОПУЛЯЦИЯ 138/138, $0.2541 ИЗ $0.65** (`sku-b-v4-run` ✅
12.08, одиннадцать коммитов `910c4b6..06617c8`). Ни (10)(a), ни (10)(b) не сработали: ворота дали **$0.5300
против $0.6500 — proceed**, ин-ран гейт шёл вниз ($0.2685 → $0.2361). 79 позиций, 5 нечитаемых
ответов (3.62%, четыре разные причины), 102 пустых, **61 позиция с зачёркнутой ценой**.
Слитые артефакты `results/sku_b_positions_v4.{json,jsonl}` — каждая строка дампа называет свою
сессию в `bought_by`: 65 `sku-b-v4` + 14 `sku-b`.

**ВСЕ ТРИ ПЛАНКИ ПРОЧИТАНЫ, B ЗАКРЫТ** (`results/sku_bar_verdicts.json :: closure` =
`CLOSED — instrument not ready, BY MEASUREMENT`, 2 из 3 провалены).
Планка 1 — brand-recall **0.3603 против 0.75 → FAIL** (макро по 15 постам; micro 0.4727,
**precision 0.9286**, на четырёх постах с пустым голдом — НОЛЬ ложных). Планка 2 — price-pair
**0.3279 против 0.80 → FAIL** (**20 из 61**, чтение тимлида 12.08 по всем 22 картинкам). Планка 3 —
tier-accuracy **0.8621 против 0.85 → PASS** (29 из 30, 1 нечитаемая = 3.3% < 10%).
`attempts.on_failure` цитируется из регистрации дословно: провалившаяся планка закрывает B
«инструмент не готов» ИЗМЕРЕНИЕМ — ни ретрая, ни переформулировки, ни второй выборки.

**ДИАГНОЗ В ОДНОЙ СТРОКЕ: КРУПНЫЙ ТЕКСТ ИДЕАЛЕН, МЕЛКИЙ ЗАЧЁРКНУТЫЙ — НА ТРЕТЬ.** Промо **61/61**,
печатный % **61/61**, зачёркнутая старая цена **20/61**; вся ошибка — суперскрипт копеек, обрезка
до `.0` или сдвиг цифры. По страницам: 22 страницы, **4 чистые, 13 без единой верной пары** — это
инструмент, а не одна плохая листовка. Оговорка: все 22 страницы — `atb_market_official_*`, одна
сеть и один лейаут; про чужой ценник это не говорит ничего.

**И ГЛАВНАЯ ПОПРАВКА К ЭТОМУ ДИАГНОЗУ (`results/sku_depth_from_pct.json`, $0):** ошибка копеечная,
а ГЛУБИНА к ней нечувствительна. Бейдж `-N%` даёт медиану **0.2886 pp** / макс **1.4171 pp**, а
старая цена, которую пайплайн УЖЕ извлекает, — **0.1761 pp** / **1.6366 pp**; обе внутри 2 pp на
всех 61 паре. Планка 2 проваливается на ПЕЧАТНОМ ЧИСЛЕ, но на этой популяции не проваливается на
ГЛУБИНЕ, ради которой это число нужно. Порог НЕ зарегистрирован — это вход в дизайн B′, не планка.

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
«Каштан 75 г» и промо-без-старой (два товара под одним ценником). Это чтение n=13 по префиксу
первой сессии, НЕ гейт: планка 2 регистрирована по ЗАВЕРШЁННОЙ популяции, и её выборка теперь
**61 пара** — прогноз по 13 остаётся тем, чем был, догадкой до данных. Суперскрипт и звёздочка —
ПОСТ-пилотная ИМЕНОВАННАЯ ревизия рядом с замороженными промптами, НИКОГДА не правка на лету
((11)(b)); в v4 обе снова в списке нечитаемых.

## ⏭️ Next

**ВСЁ ГОТОВО К skub2-run, КОНТРАКТА НЕТ.** Прережка подписана и не перезаписывается, драйвер
настроен, гарды прогнаны на $0. **Первый шаг того контракта — Dv210:** переключить
`sku_bar_verdicts.bar_one` на `results/sku_pilot_prereg_b2.json ::
bars.leaflet_brand_recall.gold.per_post`. Сейчас он читает `gold_keys` запечатанного референса —
СТАРОЕ ключевое пространство, где «Рудь» это `raw:rud`, — и отказывает на сверке пустых голдов
(у B′ их девять, у референса четыре). Отказ поставлен туда фиксом Dv209 намеренно.

**Пакет 29 строк `a|b|c` ПРОЧИТАН ПОЛНОСТЬЮ** (SPEC (14)(a)): a=11 · b=16 · c=2. Счёт, которого
пилоту не хватило: **ноль промахов зрения** — все 11 «недочитов» это отказы парсера, потолок и
алиас-разрыв, ровно то, что чинит инструмент v2.

**ПИЛОТ ЗАКОНЧЕН. ДАЛЬШЕ — ДИЗАЙН-СЕССИЯ B′** (решение оператора 12.08 в `docs/STATUS.md`:
ревизия инструмента СЕЙЧАС, брифинг 5c2 — ПОСЛЕ; для B′ облегчённый режим — короче контракты, те же
гарды на деньгах). Три КАНДИДАТА записаны в [[sku-b-pilot-closed-by-measurement]] §7 и ни один не
авторизован: (1) двухступенчатое чтение — OCR-транскрипт, потом SKU из текста (предложение оператора
10.08; отказ — глиф-резолюция, то есть проблема транскрипции раньше, чем извлечения; цена — теряется
пространственная связь цены с товаром); (2) сайд-канал `brands_visible` рядом с позициями — тогда
голд планки 1 и инструмент планки 1 меряют ОДИН объект (см. ниже); (3) семейство парсера
суперскрипт/звёздочка — ИМЕНОВАННАЯ пост-пилотная ревизия ((11)(b)), обе снова в списке нечитаемых
v4.

**ГОЛД ПЛАНКИ 1 И ИНСТРУМЕНТ ПЛАНКИ 1 — РАЗНЫЕ ОБЪЕКТЫ, и это КАНДИДАТ, а не измеренная причина.**
Голд — `brands_visible`: всё, что рецензент ВИДИТ на странице (55 пар на 15 постах). Инструмент
возвращает ПОЗИЦИИ: все **62 из 62** страничных строк дампа несут тир `position`. Бренд без цены
рядом виден и позицией не является, и его никто не просил. Сколько из 29 неназванных пар лежат на
непрайсовых товарах — пилот НЕ считал.

**ЧТО ОТЧЁТ КЛАДЁТ НА СТОЛ ВМЕСТЕ С ЧИСЛАМИ.** Инструмент НЕДОЧИТЫВАЕТ, а не ошибается: micro
**26/55**, precision **26/28** — из 28 названных пар (пост, бренд) мимо голда всего **две**
(`raw:three bears`, `raw:komo`), а НЕ названо 29; ноль ложных на постах с пустым голдом, и
все промахи планки 3 — в ту же сторону (модель возвращает меньше ступеней, чем тики оператора).
Шесть постов из 15 дали recall 0.0000, и у пяти из них голд = один бренд. Суперскрипт копеек и
звёздочка снова в списке нечитаемых (`'-50%*' is not a percentage` ×2) — это ПОСТ-пилотная
ИМЕНОВАННАЯ ревизия, никогда не правка на лету ((11)(b)).

**ЧЕМ ЗАКРЫТ ПИЛОТ, ПОИМЁННО.** `scripts/apply_sku_pair_verdicts.py` переносит 45 продиктованных
ключей на 61 строку дампа (каждая ровно один раз) и отказывается на любом промахе контрольных сумм,
на непокрытой строке, на суффиксе, достающем две страницы, и на двух переворотах вердикта, которые
суммы 20/41 не видят. `EXPECTED` — контрольная строка контракта, ПЕРЕПИСАННАЯ, а не выведенная из
`DICTATED`: сумма, посчитанная из проверяемого, соглашается с любой опечаткой в нём. Продюсер планок
пере-выводит долю через `checksums` того же апплаера — правка поля `accuracy` руками ловится.

**ДОЛГ Dv170 ЗАКРЫТ.** `scripts/sku_bar_verdicts.py` смотрит на v4 обоими дефолтами, а строка
`contract` — теперь константа с тестом, который пинит её к регистрации (`attempts.phase`), к
наличию файла контракта в дереве и к трём поправкам (6), (11), (12). Негативный контроль прогнан.
**Открыт близнец — Dv176:** ту же болезнь несёт `head["contract"]` самого драйвера
(`results/sku_b_positions_v4.json :: contract` называет `PROMPT-sku-b-v3-prep.md` и (9), (10), (11)
без (12)). Не тронуто намеренно: драйвер — денежный путь, а step 0.5 был назван поимённо. Никто это
поле не читает (проверено грепом) — чинить в следующем контракте, который и так трогает драйвер.

**DEFERRED, всё ещё не решено:** нужна ли `carrier=comment` своя планка. Прережка v4 закрыта и не
меняется ни в ту, ни в другую сторону.

## 🚧 Blockers

**НИЧЕГО НЕ БЛОКИРУЕТ — ЖДЁМ КОНТРАКТ skub2-run.** Сюита **1985 passed, 2 skipped**;
`ruff check` и `ruff format --check` чисты, 244 файла; **тринадцать коммитов `2621d6f..4b0ed29`** поверх
шестнадцати `d3fa574..c85d595`. Почекаутная таблица зелёная на каждом коммите, кроме `2621d6f` —
там второй красный **ПО ЗАМЫСЛУ** (восьмой маркер ратификации приходит на коммите тимлид-доков,
перечисление в `tests/test_sku_prereg.py` на имя короче, зелено снова на `56b2214`). Контроль —
родитель `c85d595`, 1968. Ни одного платного вызова; префлайт перегнан в пересобранном peft-venv,
**EXIT=0, PASS 47, FAIL 0** (было 40).

**Почекаутная таблица гоняется в git-worktree, и у него свой артефакт (Dv193).** `data/`
гитигнорится, поэтому в worktree она симлинк — и `test_collect_5c1.py::test_the_guard_reads_the_
pinned_paths_off_the_pin_file` красный на ВСЕХ деревьях, включая контроль-родителя. Читать таблицу
можно только с контролем рядом; «1 failed» без контроля ничего не значит.

**`config/registry.yaml` СДВИНУЛСЯ, и восемь запечатанных записей пинят его прежний sha.** Не
перепинены: реконструкция `registry_before_the_latin_aliases` + `load_registry_as_pinned`
(`src/market_pulse/registry.py`). Правка помечена префиксом `# (13)(b)` на каждой добавленной
строке комментария, а три тронутых списка `display_names` перечислены ЛИТЕРАЛЬНО в
`LATIN_ALIASES_13B` — четвёртый алиас в этих строках без записи там ломает реконструкцию, а не
проходит молча. Не «чинить» отказ перепиниванием.

**`sku_bar_verdicts.bar_one` читает голд из ЗАПЕЧАТАННОГО референса — это старое ключевое
пространство (Dv209/Dv210). ЕДИНСТВЕННОЕ, ЧТО ОСТАЛОСЬ.** Пока скорер не переключён на
`results/sku_pilot_prereg_b2.json :: bars.leaflet_brand_recall.gold.per_post`, он отказывается на
сверке пустых голдов (B′ исключает 9 постов, референс — 4). Отказ поставлен намеренно: до фикса та
же сверка СОВПАДАЛА и молча считала по 15 постам в чужом пространстве ключей.

**Драйвер переведён на skub2 — Dv208 ОПЛАЧЕН** (`skub2` / $0.65 / `spend_skub2.json` /
`sku_pilot_prereg_b2.json` / серв-пин v2 / `sku_b_positions_skub2.*`). Тройка `RESUME_*` остаётся
v4-й: у B′ нет resume-блока, skub2 идёт не-resume путём. `check_the_constants_are_the_registrations`
и новый `check_the_serving_pin_is_the_registered_one` теперь вызываются на ОБОИХ путях — раньше
первый жил внутри `if args.resume:`.

**Три новые записи называют свои продюсеры в `git.dirty` — и это ОСТАВЛЕНО так (Dv187).**
`provenance.git_state` пишется в момент записи, коммитов ещё нет: у всех трёх `commit: 06617c8`.
Переписать = сдвинуть три sha, на которые ссылаются отчёт, два теста и пин записи глубины. Доказано
иначе: на чистом дереве `d347777` все три пересобраны побайтно одинаково везде, кроме блока `git`.

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
$0.1965 + $0.1526 + $0.2541 = **$0.6032** против исходной оценки $0.35 — цена честных ворот, а не
перерасход (контракт закрытия называл ≈$0.62; сходятся к леджерам именно эти три). `results/spend_sku_b.json`, `results/spend_sku_b_v3.json` и теперь
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
