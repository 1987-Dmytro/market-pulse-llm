# retail-census (C1) — ценз сетей и полтавских чатов, $0

**236 запросов по двум темам, 410 нерегистрированных хэндлов найдено, 200 проверено entry-check'ом, 114 с вердиктом `enter`.** Реестровые 66 каналов измерены по стору, не по API (так велит бриф) — это 66 несделанных `ResolveUsername`. Всё read-only: ни одного вступления в группу. Запись — `results/retail_census.json`, таблица ниже — её же строки.

**Шаг 0 — том `mp-lora-c` удалён.** Оба листинга дословно ниже; `mp-srv2` в обоих — положительный контроль того, что листинг вообще работает. Строка гарда: остаток **$3.1686** из $20.00 цикла-2 (баланс $5.6783611613).

```
$ runpodctl network-volume list        # BEFORE
[
  {
    "dataCenterId": "EU-RO-1",
    "id": "qw4nwleanc",
    "name": "mp-srv2",
    "size": 100
  },
  {
    "dataCenterId": "CA-MTL-3",
    "id": "soymlju8q0",
    "name": "mp-lora-c",
    "size": 100
  }
]

$ runpodctl network-volume delete soymlju8q0
{
  "deleted": true,
  "id": "soymlju8q0"
}

$ runpodctl network-volume list        # AFTER
[
  {
    "dataCenterId": "EU-RO-1",
    "id": "qw4nwleanc",
    "name": "mp-srv2",
    "size": 100
  }
]
```

## Что нашлось

- `retail_chains` — 257 кандидатов из 140 запросов, измерено 135; `poltava_chats` — 153 из 96, измерено 65.
- **Планки — бюджет, не приговор**, и выставлены ПО найденному населению: `retail_chains` >= 50 · `poltava_chats` >= 0. Ниже них осталось 85 строк (210 без замера всего: 85 по планке, 125 не дошли до стены) — они В ЗАПИСИ со своими бесплатными полями и причиной, а не выброшены молча; `--min-subscribers 0 --min-subscribers-chats 0` проверяет всё. Медиана подписчиков: у сетей 182, у чатов 81 — планка 100 на чаты вычеркнула бы Оржицю, Козельщину и Машівку целиком, поэтому она 0.
- В таблице только измеренные строки: прочерк вместо замера читался бы как замер.
- Вердикты: `enter` 114 · `reject` 51 · `posts-only` 35; молочка > 0 у 55 из 200 измеренных, `enter` у 114. В таблице только измеренные строки: прочерк вместо замера читался бы как замер.
- **Покрытие — измерено 33/35 названий сетей и 19/24 райцентров.** НИЧЕГО НЕ НАЙДЕНО ни при какой планке — сети: Rozetka продукти; райцентры: Чутове. Это вывод про Украину. Остальное — найдено, но не дошли до стены (сети: Файно маркет; райцентры: Диканька, Оржиця, Козельщина, Машівка) — это вывод про бюджет, и он досчитывается.
- **54 измеренных строк без единого украинского текста** (`ua 0.00`, помечены ⚠): поиск по «METRO», «Auchan», «Толока» приводит каналы РФ-рынка. Рыночный экран SPEC 3.11 (4) — операторский, поэтому это колонка, а не вердикт; но верх таблицы читать с ней.

## Два замера, которые нельзя читать как один

- **Колонка «инстр.»**: `api` — окно 28 дней до сегодня; `store` — те же 28 дней, но кончаются они датой сбора канала (07–08.08 или 27.07). Длина окна одна, дата разная; сортировка идёт по обоим сразу, и без этой колонки порядок читался бы как вывод.
- **Цена**: бриф пишет паттерн `grn|₴|\d+[,.]\d\d` латиницей, а корпус пишет «грн». Считаются оба: у 65 строк доля по расширенному паттерну ВЫШЕ, чем по буквальному. Ветки `грн · ₴ · grn · decimal` посчитаны отдельно в записи — `decimal` срабатывает и на «27.08», и только по веткам видно, кто несёт колонку.
- **«Листовка» насыщена и потому бесполезна как различитель.** Это `has_media` (определение `scripts/image_census_5c1.py`) — прокси, без vision картинка листовкой не доказана. По стору медиана `media_share` = 0.84, у 63 из 207 строк она равна 1.00: рецепты и новости — тоже сплошь фото. Колонка «листовка/цена» (объединение, как просит бриф) стоит в таблице, но различает ритейл именно **«цена»**: её медиана 0.05.

## FloodWait — проход остановлен, собранное сохранено

- стадия `check`: Telegram попросил **85352 с (23.7 ч)** в 2026-08-27T10:38:35+00:00, снимется 2026-08-28T10:21:07+00:00. Лимит на `ResolveUsernameRequest` — он не поканальный: с резолва хэндла начинается каждый вход, каждая выборка комментов и каждый entry-check, поэтому одна строка закрывает их все.

Стена записана в `results/joins_5c1.jsonl` строкой `(census)`, а не только сюда: этот лог — то место, откуда все фазы читают «заперт ли аккаунт» (`collect_5c1.refuse_inside_flood_wait` — читатель). Стена, найденная здесь и не записанная туда, — это стена, в которую сборщик войдёт завтра. Проверено негативным контролем: повторный запуск теперь отказывается стартовать и называет час.

**Что это стоило покрытию:** 125 строк выше планки остались неизмеренными — это не «нет данных», а «ещё не смотрели»; 85 строк ниже планки не смотрели по бюджету. Обе причины стоят в записи построчно. Досчитать их — одна команда после того, как стена снимется, запись накопительная и уже измеренное не перемеряется.

## Таблица — 266 измеренных строк, сортировка `dairy posts/day × (1 + comments/day)`

`к/д или с/д` = комментов/день для каналов, сообщений/день для чатов (у чата нет счётчика ответов — там прочерк, а не ноль). Реестровые строки идут без вердикта: их измерял стор, а не этот ценз: **строки 201–266 — это реестровые 66 каналов**, они идут вторым блоком (сначала `api`, потом `store`), чтобы сортировка не сравнивала два разных окна. Кто из сетей уже в сборе и сколько даёт — смотреть туда, а не в верх таблицы. **`≥` — окно упёрлось в потолок 1200 сообщений: у 23 строк история обрезана, и ставка — нижняя граница, а не замер (потолок = 42.86 сообщ./день).**

| # | канал | handle | подп. | ✓ | п/д | листовка/цена | цена | комменты | к/д или с/д | молочка | мова | инстр. | вердикт · причина |
|---:|---|---|---:|:-:|---:|---:|---:|---|---:|---:|---|---|---|
| 1 | METRO | `@metroccrus` | 176579 | ✓ | 2.18 | 85% | 8% | да | 17.36 | 28% | ru 0.98 ua 0.02 | api | **enter** · — |
| 2 | МАША И ЕДА | `@delikatessenit` | 46008 |  | 0.86 | 88% | 8% | да | 27.75 | 12% | ru 1.00 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 3 | Гурман | `@Its_gurman` | 7196 |  | 0.68 | 100% | 0% | нет | 0.00 | 84% | ru 0.95 other 0.05 ⚠ | api | posts-only · no blue check — confirm this is the official channel |
| 4 | 🇺🇦 Шухляда\|Гадяч\|Оголошення | `@ogoloshennya_Gadyach` | 306 |  | 31.68 | 80% | 35% | чат | 31.68 | 1% | ua 0.82 ru 0.13 | api | **enter** · no blue check — confirm this is the official channel |
| 5 | 💄КОСМЕТИЧКА💋👝🇺🇦 | `@kosmetychka_ua_zakaz` | 2142 |  | ≥20.29 | 95% | 94% | нет | 0.00 | 2% | other 0.61 ua 0.28 | api | posts-only · no blue check — confirm this is the official channel |
| 6 | Metro Москва | `@gazetametro` | 21697 | ✓ | 10.11 | 100% | 2% | нет | 0.00 | 3% | ru 0.97 other 0.03 ⚠ | api | posts-only · comments disabled (no linked discussion group) |
| 7 | Копійочка Chat! 🧡 | `@kop1chat` | 4872 |  | 22.07 | 33% | 10% | чат | 22.07 | 1% | ua 0.86 other 0.13 | api | **enter** · no blue check — confirm this is the official channel |
| 8 | Скидки на Вайлдберриз \| Скидка 7 \| Дикие скидки \| Смайлик \| skidka7.com | `@skidka7` | 105857 |  | ≥42.86 | 100% | 0% | нет | 0.00 | 0% | ru 1.00 ⚠ | api | posts-only · no blue check — confirm this is the official channel |
| 9 | Оголошення Лубни Чат | `@lubnyreklama988` | 925 |  | ≥33.82 | 68% | 39% | чат | ≥33.82 | 1% | ua 0.95 other 0.04 | api | **enter** · no blue check — confirm this is the official channel |
| 10 | АШАН Россия | `@auchanrus` | 82364 | ✓ | 1.79 | 80% | 20% | нет | 0.00 | 12% | ru 1.00 ⚠ | api | posts-only · comments disabled (no linked discussion group) |
| 11 | Копійка | `@kopiyka_tm` | 2362 |  | 0.43 | 100% | 50% | нет | 0.00 | 50% | ua 1.00 | api | posts-only · no blue check — confirm this is the official channel |
| 12 | Наш Красноярский край | `@gazetankk` | 4992 |  | 16.68 | 75% | 1% | нет | 0.00 | 1% | ru 1.00 ⚠ | api | posts-only · no blue check — confirm this is the official channel |
| 13 | 🦊 BoxFox \| КАНАЛ с акциями и скидками | `@boxfoxx_katalog` | 9782 |  | ≥41.96 | 96% | 0% | группа закрыта | 0.00 | 0% | ru 0.98 other 0.02 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 14 | 💬 Чат Полтавщини | `@Poltava_intelligence_chat` | 5198 |  | ≥41.07 | 13% | 1% | чат | ≥41.07 | 0% | other 0.36 ua 0.35 | api | **enter** · no blue check — confirm this is the official channel |
| 15 | Fozzy Експериментаріум | `@fozzy_experimentanium` | 1226 |  | 1.61 | 29% | 20% | чат | 1.61 | 9% | ua 0.95 en 0.02 | api | **enter** · no blue check — confirm this is the official channel |
| 16 | Наш край - Чортківщина | `@chortkiv2` | 3789 |  | 9.18 | 100% | 10% | да | 0.79 | 1% | ua 1.00 | api | **enter** · no blue check — confirm this is the official channel |
| 17 | ЯР ® JOB — ПГТ Ярославский \| ХАЛТУРА ШАБАШКА ВАКАНСИИ ИЩУ РАБОТУ Ярославка ПОДРАБОТКУ РЕЗЮМЕ Объявления Чат Группа Хорольский ра | `@Yaroslavski_haltura_shabashka` | 1536 |  | ≥41.64 | 16% | 0% | чат | ≥41.64 | 0% | en 0.78 ru 0.18 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 18 | Чат ЩДК? Миргород 🇺🇦 | `@chatmirgo` | 5953 |  | ≥41.18 | 12% | 2% | чат | ≥41.18 | 0% | ua 0.78 other 0.16 | api | **enter** · no blue check — confirm this is the official channel |
| 19 | Зіньків Чат | `@zinkivchat` | 2257 |  | 33.89 | 25% | 5% | чат | 33.89 | 0% | ua 0.67 other 0.23 | api | **enter** · no blue check — confirm this is the official channel |
| 20 | Лубни приватні оголошення🇺🇦 | `@Vp9OhFMO9C5jZGIy` | 435 |  | 33.86 | 78% | 41% | чат | 33.86 | 0% | ua 0.92 other 0.06 | api | **enter** · no blue check — confirm this is the official channel |
| 21 | КОЛОБОК ИЗ ОДЕССЫ | `@kolobok_odesa` | 99848 |  | 30.11 | 97% | 2% | нет | 0.00 | 0% | ru 0.85 other 0.13 ⚠ | api | posts-only · no blue check — confirm this is the official channel |
| 22 | Барановичи - Наш край | `@nashkraj` | 14716 |  | ≥17.68 | 85% | 8% | нет | 0.00 | 1% | ru 0.96 other 0.04 ⚠ | api | posts-only · no blue check — confirm this is the official channel |
| 23 | 🔰 ПОЛТАВА ♨️ OLX ♨️ 🔰 ІНФО ЧАТ | `@Poltava_OLX` | 14129 |  | 7.46 | 85% | 41% | чат | 7.46 | 1% | ua 0.72 ru 0.18 | api | **enter** · no blue check — confirm this is the official channel |
| 24 | Чат Фонтан Полтава | `@fontan1000000chat` | 1017 |  | ≥42.21 | 14% | 4% | чат | ≥42.21 | 0% | ua 0.83 other 0.10 | api | **enter** · no blue check — confirm this is the official channel |
| 25 | Миргород 🔆 ЧАТ | `@mirgorod_chat` | 1584 |  | ≥41.04 | 91% | 8% | чат | ≥41.04 | 0% | ua 0.91 en 0.04 | api | **enter** · no blue check — confirm this is the official channel |
| 26 | Кременчук Оголошення \| Товари \| Послуги \| Барахолка | `@kremenchyk1` | 11211 |  | ≥20.68 | 82% | 46% | чат | ≥20.68 | 0% | ua 0.85 ru 0.14 | api | **enter** · no blue check — confirm this is the official channel |
| 27 | Барахолка Миргород | `@baraholka_mirgorod` | 2663 |  | ≥12.39 | 86% | 48% | чат | ≥12.39 | 1% | ua 0.81 other 0.14 | api | **enter** · no blue check — confirm this is the official channel |
| 28 | Чат Миргород | `@chatmirgorod` | 1219 |  | 10.71 | 14% | 2% | чат | 10.71 | 1% | ua 0.81 other 0.14 | api | **enter** · no blue check — confirm this is the official channel |
| 29 | Оголошення 🛍️ Полтава TM | `@Poltava_tviy_market` | 1182 |  | 8.89 | 76% | 9% | чат | 8.89 | 1% | ua 0.85 other 0.08 | api | **enter** · no blue check — confirm this is the official channel |
| 30 | 🔰 КРЕМЕНЧУК ♨️ OLX 🔰 ІНФО ЧАТ | `@Kremenchug_OLX` | 15600 |  | 8.11 | 81% | 37% | чат | 8.11 | 1% | ua 0.56 ru 0.29 | api | **enter** · no blue check — confirm this is the official channel |
| 31 | Море вкуса | `@morevkusa_delikat` | 295 |  | 1.29 | 100% | 42% | нет | 0.00 | 6% | ru 0.89 other 0.11 ⚠ | api | posts-only · no blue check — confirm this is the official channel |
| 32 | Барахолка Глобине Полтавська область 🇺🇦 | `@dghjjhffhjchufusjsjjsjdjdh` | 2739 |  | 1.18 | 46% | 33% | чат | 1.18 | 6% | ua 1.00 | api | **enter** · no blue check — confirm this is the official channel |
| 33 | АТБ знижки Україна \| Економія | `@atbmarketznuzhku` | 7877 |  | 0.79 | 100% | 18% | нет | 0.00 | 9% | ua 0.91 other 0.09 | api | posts-only · no blue check — confirm this is the official channel |
| 34 | ФАНАТИК АТБ \| АКЦІЇ | `@ATB_FANatik` | 3446 |  | 0.61 | 100% | 100% | да | 0.25 | 6% | ua 1.00 | api | **enter** · no blue check — confirm this is the official channel |
| 35 | Чат Полтава | `@chat_poltava` | 5582 |  | ≥42.18 | 43% | 26% | чат | ≥42.18 | 0% | ru 0.44 ua 0.41 | api | **enter** · no blue check — confirm this is the official channel |
| 36 | ЛУБНИ Chat | `@lubnyChat` | 2387 |  | ≥41.39 | 19% | 0% | чат | ≥41.39 | 0% | ua 0.68 other 0.32 | api | **enter** · no blue check — confirm this is the official channel |
| 37 | ПГТ Ярославский AVITO 💰🛍 БАРАХОЛКА в Telegram чат Хорольский район группа в Телеграм Рынок Базар Объявления Реклама Ярославка | `@Yaroslavskiy_BARAHOLKA_AVITO` | 952 |  | ≥40.36 | 6% | 1% | чат | ≥40.36 | 0% | en 0.50 ru 0.44 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 38 | Куплю продам Полтава ОГОЛОШЕННЯ | `@poltava24na7` | 1383 |  | ≥30.54 | 78% | 34% | чат | ≥30.54 | 0% | ua 0.63 ru 0.24 | api | **enter** · no blue check — confirm this is the official channel |
| 39 | Куплю/Продам/Чат Хорол | `@khorol2026` | 2410 |  | 22.25 | 56% | 20% | чат | 22.25 | 0% | ua 0.88 other 0.10 | api | **enter** · no blue check — confirm this is the official channel |
| 40 | 📦 БАРАХОЛКА ПИРЯТИН | `@buypiryat` | 1612 |  | 17.82 | 55% | 21% | чат | 17.82 | 0% | ua 0.82 other 0.14 | api | **enter** · no blue check — confirm this is the official channel |
| 41 | Чат Хуевая Полтава🖤 | `@huevapoltava` | 980 |  | 17.11 | 22% | 4% | чат | 17.11 | 0% | ua 0.66 ru 0.20 | api | **enter** · no blue check — confirm this is the official channel |
| 42 | Семенівка Дошка оголошень | `@semenivka_ogoloshennya` | 2721 |  | ≥14.54 | 72% | 16% | чат | ≥14.54 | 0% | ua 0.51 other 0.39 | api | **enter** · no blue check — confirm this is the official channel |
| 43 | Полтава Оголошення | `@poltava_obyava` | 162 |  | 13.64 | 69% | 10% | чат | 13.64 | 0% | ua 0.85 ru 0.09 | api | **enter** · no blue check — confirm this is the official channel |
| 44 | Оголошення Кременчук \| Объявления Кременчуг \| OGO | `@ogo_kremenchuk` | 281 |  | 13.32 | 79% | 37% | чат | 13.32 | 0% | ua 0.82 other 0.13 | api | **enter** · no blue check — confirm this is the official channel |
| 45 | Маркетопт ON_LINE 🔆 | `@ON_LINE_MO` | 1091 |  | 12.96 | 50% | 46% | чат | 12.96 | 0% | ua 0.74 other 0.23 | api | **enter** · no blue check — confirm this is the official channel |
| 46 | Барахолка Полтава | `@baraholka_poltavaaa` | 236 |  | 10.75 | 54% | 31% | чат | 10.75 | 0% | ua 0.36 other 0.35 | api | **enter** · no blue check — confirm this is the official channel |
| 47 | БАРАХОЛКА 🎒Доброполье \| Покровск \| Славянск \| Краматорск \| Белозерка \| Константиновка \| Белицкое \| Павлоград \| Днепр \| Полтава | `@tovarka_go` | 559 |  | 8.57 | 86% | 28% | чат | 8.57 | 0% | ru 0.54 ua 0.40 | api | **enter** · no blue check — confirm this is the official channel |
| 48 | Барахолка Миргород Полтавська область 🇺🇦 | `@fhdtdjdjgdsdjdj` | 2332 |  | 5.25 | 83% | 11% | чат | 5.25 | 1% | ua 0.98 other 0.02 | api | **enter** · no blue check — confirm this is the official channel |
| 49 | Кременчук - Глобине Барахолка 💰 | `@Globino_Kremenchyg` | 204 |  | 5.21 | 86% | 76% | чат | 5.21 | 1% | ua 0.94 ru 0.04 | api | **enter** · no blue check — confirm this is the official channel |
| 50 | Барахолка Світловодськ/Кременчук | `@svetlovodsk_baracholka` | 711 |  | 4.18 | 85% | 27% | чат | 4.18 | 1% | ua 0.79 ru 0.14 | api | **enter** · no blue check — confirm this is the official channel |
| 51 | ШИШАКИ 🇺🇦 Шишаччина | `@shyshaky_chat` | 1449 |  | 3.75 | 39% | 8% | чат | 3.75 | 1% | ua 0.86 other 0.12 | api | **enter** · no blue check — confirm this is the official channel |
| 52 | БЛИЗЕНЬКО🌿 | `@blyzenkoua` | 4985 |  | 2.04 | 100% | 35% | нет | 0.00 | 2% | ua 1.00 | api | posts-only · no blue check — confirm this is the official channel |
| 53 | Копійка гривню береже | `@K_G_B_fin` | 18953 |  | 0.36 | 70% | 40% | нет | 0.00 | 10% | ua 1.00 | api | posts-only · no blue check — confirm this is the official channel |
| 54 | Оголошення Миргород | `@mirgorodreclama` | 1590 |  | 0.25 | 43% | 29% | чат | 0.25 | 14% | ua 1.00 | api | **enter** · no blue check — confirm this is the official channel |
| 55 | АШАН Ритейл Россия | `@auchan_retail_russia` | 1425 |  | 0.18 | 100% | 40% | нет | 0.00 | 20% | ru 1.00 ⚠ | api | posts-only · no blue check — confirm this is the official channel |
| 56 | Milli Savunma Üniversitesi | `@msualayi` | 8319 |  | ≥42.86 | 1% | 0% | чат | ≥42.86 | 0% | en 0.98 other 0.02 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 57 | Наш Край! Слобожанщина! | `@nash_kray_loz` | 28453 |  | ≥42.75 | 10% | 0% | группа закрыта | 0.00 | 0% | ua 0.86 other 0.14 | api | **enter** · no blue check — confirm this is the official channel |
| 58 | Тактична Рукавичка/НІЖИН | `@taktychna_rukavuchkaa` | 45882 |  | ≥42.14 | 38% | 0% | группа закрыта | 2.54 | 0% | ua 0.88 other 0.12 | api | **enter** · no blue check — confirm this is the official channel |
| 59 | Чат-Глобино/Глобине👹 | `@h_globino_official1` | 2154 |  | ≥41.93 | 12% | 0% | чат | ≥41.93 | 0% | ua 0.70 other 0.27 | api | **enter** · no blue check — confirm this is the official channel |
| 60 | ОГОЛОШЕННЯ \| ОБЪЯВЛЕНИЯ \| ПОЛТАВА \| ADS \| POLTAVA \| НОВОСТИ \| НОВИНИ | `@poltava053` | 625 |  | ≥41.00 | 16% | 6% | чат | ≥41.00 | 0% | ru 0.75 ua 0.23 | api | **enter** · no blue check — confirm this is the official channel |
| 61 | ЗнижКом \| Чат | `@znishhhkom` | 188 |  | ≥40.00 | 40% | 2% | чат | ≥40.00 | 0% | ua 0.54 other 0.23 | api | **enter** · no blue check — confirm this is the official channel |
| 62 | 💬 ЧАТ \| ПИРЯТИН | `@Piryatin4AT` | 837 |  | 26.89 | 12% | 2% | чат | 26.89 | 0% | ua 0.77 other 0.19 | api | **enter** · no blue check — confirm this is the official channel |
| 63 | Промокоды Мегамаркет | `@promokody_megamarket` | 6038 |  | 18.04 | 100% | 96% | да | 0.71 | 0% | ru 1.00 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 64 | Мегамаркет | `@megamarket0` | 1069 |  | 18.04 | 100% | 96% | да | 0.14 | 0% | ru 1.00 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 65 | РОМАНЭ ЛУБНЯ ЧАТ 001 | `@lubnya888` | 259 |  | 17.89 | 2% | 0% | чат | 17.89 | 0% | ru 0.85 other 0.14 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 66 | Metro City Samachar | `@Metrosamachar` | 258 | ✓ | 9.43 | 100% | 3% | группа закрыта | 0.00 | 0% | en 1.00 ⚠ | api | **enter** · linked group present but no comments on the sampled posts |
| 67 | Каталог оптом.Скидки🇹🇷 | `@turktrendkatalog_skidka` | 879 |  | 9.07 | 84% | 0% | нет | 0.00 | 0% | en 0.42 other 0.35 ⚠ | api | posts-only · no blue check — confirm this is the official channel |
| 68 | Знижкоман | `@znizkomn` | 2322 |  | 8.04 | 54% | 2% | да | 8.93 | 0% | ua 0.77 other 0.10 | api | **enter** · no blue check — confirm this is the official channel |
| 69 | Копійочка Лосинівка | `@kopiyochka_losinovka` | 420 |  | 7.89 | 99% | 0% | нет | 0.00 | 0% | ua 0.54 other 0.46 | api | posts-only · no blue check — confirm this is the official channel |
| 70 | Барахолка Кобеляки Полтавська область🇺🇦 | `@dhdhdhshsdhjsjbsj` | 1209 |  | 6.11 | 70% | 14% | чат | 6.11 | 0% | ua 0.75 other 0.23 | api | **enter** · no blue check — confirm this is the official channel |
| 71 | ЗнижКом \| Ігрові Знижки 🇺🇦 | `@znishkom` | 7166 |  | 6.00 | 98% | 76% | да | 59.71 | 0% | ua 1.00 | api | **enter** · no blue check — confirm this is the official channel |
| 72 | FC Kolos Kovalivka | `@fckoloskovalivka` | 2083 | ✓ | 4.46 | 100% | 1% | да | 3.29 | 0% | ua 0.86 en 0.09 | api | **enter** · — |
| 73 | ЧАТ ОБЩЕНИЯ ЗНАКОМСТВА | `@Kremenchuki` | 338 |  | 4.14 | 10% | 3% | чат | 4.14 | 0% | other 0.46 ru 0.43 | api | **enter** · no blue check — confirm this is the official channel |
| 74 | Vel_Martinys | `@velmartinus` | 610 |  | 3.25 | 79% | 0% | да | 17.75 | 0% | ru 0.88 other 0.11 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 75 | Бровари Київ \| акції та знижки ☺️ | `@brovarysale` | 3914 |  | 3.04 | 66% | 4% | чат | 3.04 | 0% | ua 0.86 other 0.10 | api | **enter** · no blue check — confirm this is the official channel |
| 76 | Ukrainian 🇺🇦.Украінці в Німеччині.Берлін,Регенсбург,Амберг,Нюрнберг,Баварія.Допомога.Спілкування.Подіі.Толока.Акціі.Новини.... | `@ukrgermspilka` | 279 |  | 2.96 | 53% | 5% | чат | 2.96 | 0% | ua 0.91 ru 0.09 | api | **enter** · no blue check — confirm this is the official channel |
| 77 | MEGAMARKET | `@finestmegaleaks` | 20095 |  | 2.61 | 81% | 0% | нет | 0.00 | 0% | en 1.00 ⚠ | api | posts-only · no blue check — confirm this is the official channel |
| 78 | Наш родны край Лагойск | `@rodnykraj` | 4703 |  | 2.54 | 89% | 18% | да | 0.50 | 0% | ru 0.99 ua 0.01 | api | **enter** · no blue check — confirm this is the official channel |
| 79 | Решетилівка робота та оголошення | `@reshetrobota` | 204 |  | 2.32 | 45% | 22% | чат | 2.32 | 0% | ua 0.85 other 0.08 | api | **enter** · no blue check — confirm this is the official channel |
| 80 | Барахолка Лубни | `@barlybnu` | 747 |  | 1.86 | 90% | 52% | чат | 1.86 | 0% | ua 0.94 other 0.06 | api | **enter** · no blue check — confirm this is the official channel |
| 81 | Алексей Коломийцев | `@bibliyagovorit` | 11082 |  | 1.75 | 61% | 2% | группа закрыта | 2.64 | 0% | ru 1.00 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 82 | Маркетопт 🔆 Розливне Пиво | `@rozlyvne` | 7228 |  | 1.68 | 68% | 23% | группа закрыта | 3.39 | 0% | ua 1.00 | api | **enter** · no blue check — confirm this is the official channel |
| 83 | Инна Замова Таролог Психолог | `@taro_delikatesy` | 564 |  | 1.54 | 100% | 0% | группа закрыта | 0.68 | 0% | ru 0.58 other 0.42 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 84 | Копійка до копійки | `@penni108` | 827 |  | 1.50 | 21% | 7% | чат | 1.50 | 0% | ua 0.85 en 0.05 | api | **enter** · no blue check — confirm this is the official channel |
| 85 | Обмін Валют \| Сільпо | `@obmin_silpo` | 1440 |  | 1.46 | 100% | 100% | нет | 0.00 | 0% | ua 1.00 | api | posts-only · no blue check — confirm this is the official channel |
| 86 | Барахолка Нові Санжари Полтавська область 🇺🇦 | `@cdfrsjsjsjsjsjwjwjej` | 377 |  | 1.43 | 70% | 12% | чат | 1.43 | 0% | ua 0.83 other 0.17 | api | **enter** · no blue check — confirm this is the official channel |
| 87 | Валерій Копійка - в.о. ректора КНУ | `@knu_rector` | 858 |  | 1.36 | 97% | 0% | да | 0.25 | 0% | ua 1.00 | api | **enter** · no blue check — confirm this is the official channel |
| 88 | Полтавська область \| Спільнота волонтерів України | `@poltava_cooperation` | 499 |  | 1.36 | 18% | 13% | чат | 1.36 | 0% | ua 0.82 other 0.18 | api | **enter** · no blue check — confirm this is the official channel |
| 89 | Оголошення Горішні Плавні \| Объявления Горишние Плавни \| OGO | `@ogo_gorishniplavni` | 219 |  | 1.36 | 84% | 26% | чат | 1.36 | 0% | ua 0.92 other 0.04 | api | **enter** · no blue check — confirm this is the official channel |
| 90 | каталог № 10 акции и выгодные предложения | `@skidka_vigodno` | 520 |  | 1.29 | 97% | 3% | да | 0.00 | 0% | ru 0.64 other 0.36 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 91 | Музей-заповедник «Коломенское» | `@kolomenskoe_moscow` | 18022 | ✓ | 1.25 | 100% | 3% | нет | 0.00 | 0% | ru 0.91 other 0.09 ⚠ | api | posts-only · comments disabled (no linked discussion group) |
| 92 | Барахолка,дошка оголошень Глобине-Кременчук | `@globinos` | 1798 |  | 1.11 | 42% | 3% | чат | 1.11 | 0% | ua 0.94 other 0.06 | api | **enter** · no blue check — confirm this is the official channel |
| 93 | Барахолка Лохвиця Полтавська область🇺🇦 | `@xjsjejhjfgdhhdznghjjjt` | 681 |  | 1.11 | 45% | 16% | чат | 1.11 | 0% | ua 0.92 ru 0.08 | api | **enter** · no blue check — confirm this is the official channel |
| 94 | Барахолка Гребінка Полтавська область🇺🇦 | `@gshsgswerdfgghjtyjjy` | 368 |  | 1.11 | 84% | 23% | чат | 1.11 | 0% | ua 0.83 ru 0.17 | api | **enter** · no blue check — confirm this is the official channel |
| 95 | Никита Кологривый | `@nik_kologrivyy` | 36522 | ✓ | 1.07 | 97% | 3% | да | 49.71 | 0% | ru 0.86 en 0.07 ⚠ | api | **enter** · — |
| 96 | Барахолка Шишаки 🇺🇦 Полтавська область 🇺🇦 | `@xddfhnhfsdf` | 2154 |  | 1.07 | 63% | 33% | чат | 1.07 | 0% | ua 0.96 ru 0.04 | api | **enter** · no blue check — confirm this is the official channel |
| 97 | Ансамбль Толока_почти официально | `@toloka_ensemble` | 12542 |  | 0.96 | 89% | 0% | да | 5.00 | 0% | ru 1.00 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 98 | Канал про гроші 💸 | `@depositorfrank` | 730 |  | 0.96 | 96% | 74% | да | 0.11 | 0% | ua 0.96 other 0.04 | api | **enter** · no blue check — confirm this is the official channel |
| 99 | Суботній авторинок Барахолка Полтава». | `@Avto_Bara_Poltava` | 365 |  | 0.96 | 82% | 4% | чат | 0.96 | 0% | ua 0.78 other 0.11 | api | **enter** · no blue check — confirm this is the official channel |
| 100 | Барахолка Лубни Полтавська область 🇺🇦 | `@zdgsdjgjj` | 670 |  | 0.93 | 88% | 42% | чат | 0.93 | 0% | ua 0.95 other 0.05 | api | **enter** · no blue check — confirm this is the official channel |
| 101 | RobiX Shop \| Акції та знижки | `@robixshop` | 539 |  | 0.89 | 88% | 84% | нет | 0.00 | 0% | ua 1.00 | api | posts-only · no blue check — confirm this is the official channel |
| 102 | PRO МЕТРО | `@pro_metro` | 53800 | ✓ | 0.79 | 100% | 0% | группа закрыта | 108.57 | 0% | ru 1.00 ⚠ | api | **enter** · — |
| 103 | Metropol Chronicles | `@metropolchronicles` | 25303 |  | 0.79 | 100% | 96% | нет | 0.00 | 0% | en 1.00 ⚠ | api | posts-only · no blue check — confirm this is the official channel |
| 104 | Работа в АШАН | `@auchanjob` | 1742 |  | 0.75 | 95% | 0% | да | 0.32 | 0% | ru 0.89 other 0.11 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 105 | 🛒НАШЕ АТБ / АКЦІЇ / НОВИНКИ 🛍🛒 | `@ATBATBATBAT` | 276 |  | 0.75 | 100% | 24% | да | 0.04 | 0% | ua 1.00 | api | **enter** · no blue check — confirm this is the official channel |
| 106 | Барахолка с. Хороль | `@barahHorol` | 348 |  | 0.68 | 95% | 10% | чат | 0.68 | 0% | ru 0.67 other 0.33 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 107 | مترور | `@metror` | 2586 |  | 0.64 | 83% | 0% | да | 1.04 | 0% | en 0.88 other 0.12 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 108 | Сім23 та Сімі💜 | `@sim23_simi` | 5083 |  | 0.61 | 88% | 12% | да | 0.71 | 0% | ua 1.00 | api | **enter** · no blue check — confirm this is the official channel |
| 109 | Фора-Банк | `@forabank_official` | 3140 | ✓ | 0.57 | 100% | 0% | нет | 0.00 | 0% | ru 1.00 ⚠ | api | posts-only · comments disabled (no linked discussion group) |
| 110 | Барахолка Котельва Полтавська область 🇺🇦 | `@dfhjjhffgssjshh` | 440 |  | 0.54 | 87% | 20% | чат | 0.54 | 0% | other 0.62 ua 0.38 | api | **enter** · no blue check — confirm this is the official channel |
| 111 | Маркетопт 🔆 Робота \| Вакансії | `@marketoptwork` | 3225 |  | 0.50 | 100% | 0% | да | 0.61 | 0% | ua 0.91 other 0.09 | api | **enter** · no blue check — confirm this is the official channel |
| 112 | Барахолка Гадяч Полтавська область 🇺🇦 | `@bkbsehjshg` | 404 |  | 0.46 | 62% | 15% | чат | 0.46 | 0% | ua 0.89 other 0.11 | api | **enter** · no blue check — confirm this is the official channel |
| 113 | Из метро | `@iz_metro` | 23163 | ✓ | 0.43 | 100% | 0% | да | 3.71 | 0% | ru 0.82 other 0.18 ⚠ | api | **enter** · — |
| 114 | New World Order | `@novusorbis` | 508 |  | 0.39 | 100% | 100% | да | 0.00 | 0% | en 1.00 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 115 | РУКАВИЧКА-КР | `@RUKAVICHKAkr` | 623 |  | 0.36 | 50% | 20% | нет | 0.00 | 0% | ua 0.86 other 0.14 | api | posts-only · no blue check — confirm this is the official channel |
| 116 | Хочу дешевше | `@xochydeshevshe` | 621 |  | 0.36 | 100% | 100% | да | 0.00 | 0% | ua 1.00 | api | **enter** · no blue check — confirm this is the official channel |
| 117 | Барахолка Горішні плавні Полтавська область 🇺🇦 | `@xxcbjhsfhsfghjjkkhg` | 974 |  | 0.32 | 78% | 22% | чат | 0.32 | 0% | ua 0.86 other 0.14 | api | **enter** · no blue check — confirm this is the official channel |
| 118 | Барахолка Зіньків Полтавська область 🇺🇦 | `@shebshsjje` | 258 |  | 0.32 | 89% | 11% | чат | 0.32 | 0% | ua 1.00 | api | **enter** · no blue check — confirm this is the official channel |
| 119 | FORA.SSTATTOO | `@multiplyforass` | 178 |  | 0.32 | 89% | 0% | да | 0.82 | 0% | ru 0.78 other 0.22 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 120 | Еком-маркетолог | `@ecomedu_roregroup` | 171 |  | 0.29 | 100% | 0% | да | 0.11 | 0% | ru 1.00 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 121 | << ЭКОНОМ МАРКЕТ >> ТЦ ЗВЕЗДА | `@EKONOMMARKET1` | 1172 |  | 0.25 | 100% | 0% | нет | 0.00 | 0% | ru 0.80 other 0.20 ⚠ | api | posts-only · no blue check — confirm this is the official channel |
| 122 | Барахолка Карлівка Полтавська область🇺🇦 | `@sdhdsjjhsjsjsj` | 341 |  | 0.25 | 57% | 0% | чат | 0.25 | 0% | ua 0.83 ru 0.17 | api | **enter** · no blue check — confirm this is the official channel |
| 123 | ОГОЛОШЕННЯ МИРГОРОД© | `@ogolochennya_mirgorod` | 334 |  | 0.25 | 86% | 14% | нет | 0.00 | 0% | ua 0.80 en 0.20 | api | posts-only · no blue check — confirm this is the official channel |
| 124 | Новини НАТ "Барвінок" (Вінниця) | `@natbarvinok_news` | 283 |  | 0.25 | 86% | 0% | нет | 0.00 | 0% | ua 1.00 | api | posts-only · no blue check — confirm this is the official channel |
| 125 | Юрий Колокольников | `@yurikolokolnikovofficial` | 5132 | ✓ | 0.21 | 100% | 0% | да | 3.89 | 0% | ru 0.83 other 0.17 ⚠ | api | **enter** · — |
| 126 | Lisik \| Продуктове-ІТ, маркетинг, економіка 🤖 | `@lisik_notes` | 3004 |  | 0.21 | 0% | 0% | да | 0.36 | 0% | ua 1.00 | api | **enter** · no blue check — confirm this is the official channel |
| 127 | Чат⚡Кременчук. | `@kremik_chat` | 2697 |  | 0.21 | 17% | 17% | чат | 0.21 | 0% | ua 0.67 other 0.33 | api | **enter** · no blue check — confirm this is the official channel |
| 128 | Экологичный маркетинг у Лены | `@ekomarketing` | 2462 |  | 0.21 | 33% | 0% | да | 0.75 | 0% | ru 1.00 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 129 | RUKAVICHKA🤍 | `@rukavichka789` | 195 |  | 0.21 | 83% | 0% | да | 0.11 | 0% | ru 1.00 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 130 | Промокоды АШАН 2026 | `@auchan_promokod` | 585 |  | 0.18 | 100% | 0% | нет | 0.00 | 0% | ru 1.00 ⚠ | api | posts-only · no blue check — confirm this is the official channel |
| 131 | Доставка з супермаркетів/Знижки/Zakaz.ua | `@zakazzua` | 805 |  | 0.14 | 100% | 50% | нет | 0.00 | 0% | other 0.50 ua 0.50 | api | posts-only · no blue check — confirm this is the official channel |
| 132 | Знижки АТБ💛💙 | `@discountAtb` | 610 |  | 0.14 | 100% | 100% | да | 0.00 | 0% | ua 1.00 | api | **enter** · no blue check — confirm this is the official channel |
| 133 | varush.kins | `@varysshkins` | 500 |  | 0.14 | 100% | 0% | да | 0.54 | 0% | ru 0.50 en 0.25 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 134 | ОСББ Барвінок (інфо) | `@shumskogo5` | 463 |  | 0.14 | 25% | 0% | нет | 0.00 | 0% | ua 1.00 | api | posts-only · no blue check — confirm this is the official channel |
| 135 | Madness | `@madness_oldschool_thrash_metal` | 182 |  | 0.14 | 100% | 0% | да | 0.79 | 0% | ru 0.75 en 0.25 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 136 | Маркет Оптика | `@marketoptika` | 166 |  | 0.14 | 100% | 0% | да | 0.00 | 0% | ru 1.00 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 137 | ТОЛОКА #ищу \| удалённая работа | `@tolokaSeek` | 15853 |  | 0.11 | 100% | 33% | нет | 0.00 | 0% | ru 1.00 ⚠ | api | posts-only · no blue check — confirm this is the official channel |
| 138 | "Копійка" - Інтернет-провайдер | `@ispkopiyka` | 1921 |  | 0.11 | 100% | 67% | нет | 0.00 | 0% | ua 1.00 | api | posts-only · no blue check — confirm this is the official channel |
| 139 | Velmartyr: DISBAND. | `@velmartyr` | 662 |  | 0.07 | 0% | 0% | да | 0.21 | 0% | en 1.00 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 140 | Барвінок Світло | `@BarvinokSvitloCh` | 564 |  | 0.07 | 0% | 0% | нет | 0.00 | 0% | other 0.50 ua 0.50 | api | posts-only · no blue check — confirm this is the official channel |
| 141 | Барахолка Пирятин Полтавська область🇺🇦 | `@xcvggjdhshkff` | 382 |  | 0.07 | 0% | 0% | чат | 0.07 | 0% | ua 1.00 | api | **enter** · no blue check — confirm this is the official channel |
| 142 | ТОЛОКА фриланс биржа \| удалённая работа | `@teletoloka` | 39263 |  | 0.04 | 0% | 0% | чат | 0.04 | 0% | ru 1.00 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 143 | Промокодыч • Скидки и Акции | `@skidka3` | 15243 |  | 0.04 | 100% | 0% | да | 0.04 | 0% | ru 1.00 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 144 | ТОЛОКА вакансии \| удалённая работа | `@tolokaWork` | 12827 |  | 0.04 | 100% | 100% | нет | 0.00 | 0% | ru 1.00 ⚠ | api | posts-only · no blue check — confirm this is the official channel |
| 145 | Рецепты \| Готовим с Павлом | `@Gotovim_s_Pavlom_Gurmanovim` | 4581 |  | 0.04 | 100% | 0% | да | 0.00 | 0% | ru 1.00 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 146 | Радіо «Сільпо» | `@radio_silpo` | 3145 |  | 0.04 | 100% | 0% | да | 0.00 | 0% | ua 1.00 | api | **enter** · no blue check — confirm this is the official channel |
| 147 | Market Store (Опт) | `@MarketOptSale` | 421 |  | 0.04 | 0% | 0% | нет | 0.00 | 0% | ru 1.00 ⚠ | api | posts-only · no blue check — confirm this is the official channel |
| 148 | Кременчуг Чат - Форум | `@Chat_Kremenchuk` | 279 |  | 0.04 | 0% | 0% | чат | 0.04 | 0% | ru 1.00 ⚠ | api | **enter** · no blue check — confirm this is the official channel |
| 149 | Оголошення Кременчук | `@ogol_kremenchuk657` | 187 |  | 0.04 | 100% | 0% | нет | 0.00 | 0% | en 1.00 ⚠ | api | posts-only · no blue check — confirm this is the official channel |
| 150 | Алеся Теперикова ДНЕВНИК КОЛОРИСТА | `@alesya_teperikova` | 30035 | ✓ | 0.00 | — | — | да | 0.00 | — | — | api | reject · no posts in the sampled window |
| 151 | Thrash upload | `@thrash5` | 20555 |  | 0.00 | — | — | чат | 0.00 | — | — | api | reject · no messages in the sampled window |
| 152 | UKR SALES l Акції та знижки🇺🇦 | `@ukrsales` | 14641 |  | 0.00 | — | — | нет | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 153 | ГурманЪ \| Рецепты \| Советы | `@food_gurman` | 7967 |  | 0.00 | — | — | да | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 154 | Знижки та акції УКРАЇНЦІ РАЗОМ | `@ukrazom_org` | 5993 |  | 0.00 | — | — | нет | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 155 | Thrash movie | `@Thrash4` | 4141 |  | 0.00 | — | — | чат | 0.00 | — | — | api | reject · no messages in the sampled window |
| 156 | Скидки и промокоды Яндекс \| Lovely | `@megamarketlovely` | 3736 |  | 0.00 | — | — | да | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 157 | Копійка \| Аукціони, Лоти | `@kopiykalot` | 3672 |  | 0.00 | — | — | группа закрыта | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 158 | Полтава Барахолка ➡️ Опублікувати Оголошення | `@Barakholka_Poltava` | 2961 |  | 0.00 | — | — | чат | 0.00 | — | — | api | reject · no messages in the sampled window |
| 159 | ai-треш в тг | `@ai_thrash` | 2712 |  | 0.00 | — | — | нет | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 160 | Наш Край🇺🇦 | `@nashkray` | 2213 |  | 0.00 | — | — | нет | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 161 | НАТАЛИ ГУРМАНОВА | `@natalie_gurmanova` | 2174 | ✓ | 0.00 | — | — | нет | 0.00 | — | — | api | reject · no posts in the sampled window |
| 162 | Мега Знижки🇺🇦\| АТБ, АВРОРА, Фора, ЕКОмаркет, Копійочка | `@megaznuchki` | 1606 |  | 0.00 | — | — | чат | 0.00 | — | — | api | reject · no messages in the sampled window |
| 163 | NOVUS ORDO SECLORUM | `@newworldra` | 1563 |  | 0.00 | — | — | нет | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 164 | КАЗАНЬ СКИДКИ | `@skidkakazan116` | 1279 |  | 0.00 | — | — | нет | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 165 | 🧀 Сырный Гурман \| Владивосток | `@CheeseGourmetVl` | 1156 |  | 0.00 | — | — | группа закрыта | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 166 | Полтава Чат | `@poltava_chat1` | 1114 |  | 0.00 | — | — | чат | 0.00 | — | — | api | reject · no messages in the sampled window |
| 167 | Економщик 360° \| Знижки | `@znizhki_atb_avrora_ukraine` | 1109 |  | 0.00 | — | — | нет | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 168 | «Сільпо» Семафорний пров.,4 | `@silpo_301` | 911 |  | 0.00 | — | — | да | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 169 | 1 копійка до Мілліона | `@shum_inmarketing` | 895 |  | 0.00 | — | — | чат | 0.00 | — | — | api | reject · no messages in the sampled window |
| 170 | Гроші на ЗСУ | `@groshi_na_zsu` | 772 |  | 0.00 | — | — | нет | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 171 | Годнота с Aliexpress | `@skidka_sbermegamarket` | 680 |  | 0.00 | — | — | нет | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 172 | Знижки та Акції 🇺🇦 \| АТБ VARUS СІЛЬПО METRO АШАН | `@znizhki_ua` | 655 |  | 0.00 | — | — | да | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 173 | АромаГурман | `@aroma_gurman` | 615 |  | 0.00 | — | — | да | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 174 | ДО ГРОШЕЙ | `@dohroshei` | 571 |  | 0.00 | — | — | да | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 175 | Сільпо Respublika Park | `@respublikasilpo` | 550 |  | 0.00 | — | — | да | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 176 | Кременчук Барахолка ➡️ Опублікувати Оголошення | `@Barakholka_Kremenchuk` | 528 |  | 0.00 | — | — | чат | 0.00 | — | — | api | reject · no messages in the sampled window |
| 177 | METRO Moldova | `@metro_moldova` | 488 | ✓ | 0.00 | — | — | нет | 0.00 | — | — | api | reject · no posts in the sampled window |
| 178 | НАШ КРАЙ_Кочубеевское | `@Nash_Kray` | 450 |  | 0.00 | — | — | да | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 179 | Полтава Чат - Форум | `@Poltava_chats` | 444 |  | 0.00 | — | — | чат | 0.00 | — | — | api | reject · no messages in the sampled window |
| 180 | فرا بازاریابی | `@UltraMarketingCG` | 431 |  | 0.00 | — | — | нет | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 181 | Thrash Playlist | `@Thrash_Playlist` | 416 |  | 0.00 | — | — | нет | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 182 | Наш Край Мариуполь🏡🏭🏢 | `@smaylikMRPL` | 398 |  | 0.00 | — | — | да | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 183 | ШКОЛА ПЛЮС | `@msuauditorium` | 385 |  | 0.00 | — | — | да | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 184 | ЗнижКом \| PS Store | `@znishkomps` | 385 |  | 0.00 | — | — | да | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 185 | РУКАВИЧКА❤️ | `@demohinaa` | 349 |  | 0.00 | — | — | да | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 186 | Кар’єра в Близенько | `@robotablyzenko` | 345 |  | 0.00 | — | — | нет | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 187 | varus-valgus.net | `@varusnet` | 343 |  | 0.00 | — | — | да | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 188 | Мужское воспитание | `@forallman1` | 309 |  | 0.00 | — | — | да | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 189 | ТАВРІЯ В | `@tavria_v` | 267 |  | 0.00 | — | — | нет | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 190 | Novusy.cc | `@novusycc` | 262 |  | 0.00 | — | — | нет | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 191 | Польский Грошик 🪙 | `@polski_grosz` | 253 |  | 0.00 | — | — | да | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 192 | СОПРОТИВЛЕНИЕ ⭕ | `@novus_ordo` | 246 |  | 0.00 | — | — | да | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 193 | ГУРМАН 🍓 | `@gurmanz` | 234 |  | 0.00 | — | — | нет | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 194 | ИИчки Рувимовны/Homo Novus | `@iichkirushi` | 198 |  | 0.00 | — | — | да | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 195 | Столичная Гурманка | `@stolichnayagurmanka` | 195 |  | 0.00 | — | — | да | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 196 | ВДТ «Волинська толока 2025» | `@voltoloka` | 186 |  | 0.00 | — | — | да | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 197 | Арабский клуб ФМП МГУ | `@msuarabia` | 185 |  | 0.00 | — | — | да | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 198 | Клуб выпускников МГУ | `@MSUAlumni` | 178 |  | 0.00 | — | — | группа закрыта | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 199 | Смачні Акції АТБ | `@zniijkiATB` | 175 |  | 0.00 | — | — | нет | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 200 | АТБ Акції / Знижки | `@ATBUAH` | 157 |  | 0.00 | — | — | да | 0.00 | — | — | api | reject · no blue check — confirm this is the official channel |
| 201 | Матусі України | `@matusi_ukr` | 19278 |  | 7.79 | 100% | 2% | да | 97.04 | 6% | ua 0.93 ru 0.07 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 202 | Мандзяк Віктор | `@mandziak` | 123985 |  | 4.25 | 82% | 2% | да | 36.64 | 8% | ua 0.97 other 0.03 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 203 | Varus | `@VARUS_channel` | — |  | 4.71 | 100% | 22% | да | 15.43 | 15% | ua 0.89 other 0.11 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 204 | Кулінарні рецепти | `@retsepty` | 23954 |  | 3.25 | 100% | 0% | да | 3.75 | 64% | ua 0.99 en 0.01 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 205 | Тарілка Малюка • Прикорм | `@tarilka_malyuka` | 10420 |  | 2.93 | 95% | 1% | да | 1.61 | 65% | ua 0.99 other 0.01 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 206 | Кулінарні рецепти | `@recepti` | 115746 |  | 7.04 | 100% | 0% | нет | — | 60% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 207 | Мамині Рецепти | `@mameni_recepti` | 90429 |  | 8.86 | 100% | 31% | нет | — | 46% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 208 | Королева Кухні 👑 (Кулінарія та рецепти) | `@korolevakuchni` | 1196 |  | 4.50 | 100% | 2% | нет | — | 57% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 209 | MSUa Акції та знижки | `@msuaaaa` | — |  | 2.36 | 100% | 61% | да | 11.36 | 8% | ua 0.94 other 0.06 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 210 | Гастровсесвіт Клопотенка | `@klopotenkofood` | 36098 | ✓ | 1.36 | 47% | 0% | да | 8.04 | 10% | ua 0.97 other 0.03 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 211 | Консервація та кулінарія | `@konservacia_kulinaria` | 33970 |  | 3.18 | 99% | 0% | нет | — | 27% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 212 | the VYLKA (рецепти) | `@vylkachannel` | 8890 |  | 0.96 | 100% | 0% | нет | — | 59% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 213 | Держпродспоживслужба | `@dpssgovua` | 2619 |  | 2.71 | 100% | 8% | нет | — | 20% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 214 | Кременчуцький Телеграф | `@telegraf_kremenchuk` | 32827 |  | 21.89 | 93% | 26% | нет | — | 2% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 215 | Х Кременчук | `@h_kremenchug` | 137222 |  | 15.89 | 39% | 5% | нет | — | 2% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 216 | Катерина Ненька — грудне вигодовування та дитяче харчування \| сон | `@ya_Nenka` | 2369 |  | 0.36 | 100% | 30% | да | 0.57 | 60% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 217 | Копійочка 🫶🏻 | `@kopiyochka1` | 77638 |  | 1.86 | 100% | 4% | да | 7.96 | 2% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 218 | Сільпо | `@silposilpo` | — |  | 1.29 | 100% | 53% | нет | — | 25% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 219 | ЕПІЦЕНТР | `@epicentrk_sale` | 52501 | ✓ | 4.86 | 99% | 59% | нет | — | 6% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 220 | Горішні Плавні 🇺🇦 | `@gorishnie_plavni1` | 21077 |  | 19.57 | 58% | 16% | нет | — | 1% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 221 | Фора | `@forainfo` | 7533 |  | 0.57 | 100% | 62% | нет | — | 31% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 222 | ЕКО Маркет | `@ekomarket_shop` | 1346 |  | 0.43 | 100% | 100% | нет | — | 42% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 223 | Полтава ІНФО \| Новини Світло | `@poltava20` | 43486 |  | 53.07 | 24% | 3% | нет | — | 0% | ua 0.88 other 0.12 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 224 | Суспільне Полтава | `@suspilnepoltava` | 56254 | ✓ | 18.18 | 74% | 3% | нет | — | 1% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 225 | ВИХОВАННЯ З ЛЮБОВ'Ю💕 | `@educationwithloven` | 31490 |  | 15.04 | 100% | 2% | нет | — | 1% | ua 0.98 other 0.02 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 226 | Mirgorodtown | `@myrhorodtown` | 19587 |  | 9.25 | 29% | 4% | нет | — | 1% | ua 0.99 other 0.01 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 227 | Маркетопт (Толока) м.Кременчук | `@marketopt_promo` | 2914 |  | 0.43 | 100% | 50% | нет | — | 25% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 228 | Здорове харчування\| Софія Ігорівна | `@useful_healthy_fitness_menu` | 1426 |  | 0.61 | 94% | 0% | да | 0.14 | 12% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 229 | Полтава Інформує | `@poltava_informue` | 66474 |  | 45.39 | 20% | 2% | нет | — | 0% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 230 | МОЗАМБІК.МЕДІА: Лубни, Пирятин, Хорол, Гребінка, Оржиця | `@mo3ambik` | 34664 |  | 6.93 | 89% | 15% | нет | — | 1% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 231 | Творча Матуся \| Розвиток дитини | `@tvorcha_matusyua` | 45396 |  | 3.93 | 99% | 0% | нет | — | 2% | ua 0.95 other 0.05 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 232 | Х Глобине | `@globine1` | 12187 |  | 3.61 | 68% | 18% | нет | — | 2% | ua 0.96 other 0.03 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 233 | Мамо, не псіхуй!👌 | `@mamo_nepsichuy` | 13781 |  | 1.57 | 100% | 2% | да | 0.32 | 2% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 234 | Тренування з Олею Поляковою та Сергієм Шеремета | `@polyakova_fitness` | 9078 |  | 1.86 | 92% | 0% | да | 0.29 | 2% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 235 | PVP.POLTAVA | `@poltava_pvp` | 106758 |  | 14.43 | 83% | 29% | нет | — | 0% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 236 | КРЕМІНЬ \| НОВИНИ \| КРЕМЕНЧУК | `@kremen_news` | 28286 |  | 12.29 | 95% | 17% | нет | — | 0% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 237 | Гадяч | `@Hadiach_telegram` | 12390 |  | 5.04 | 86% | 10% | нет | — | 1% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 238 | MAUDAU: канал цікавих штук | `@maudau` | 29542 |  | 2.25 | 94% | 36% | нет | — | 2% | ua 0.98 other 0.02 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 239 | АТБ Акції | `@atb_aktsiyi` | 1507 |  | 1.89 | 100% | 4% | нет | — | 2% | ua 0.86 en 0.14 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 240 | BLW.BABIES 🥦🍓 СМАЧНИЙ ПРИКОРМ 🥑 BLW 🥑 САМОПРИКОРМ 🥑 ДИТЯЧЕ МЕНЮ 🥑 РЕЦЕПТИ | `@blwbabies` | 10054 |  | 0.14 | 100% | 0% | нет | — | 25% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 241 | ✨Павлуша і Ява 🇺🇦 | `@pavlushaiyava` | 45810 |  | 3.75 | 100% | 0% | нет | — | 0% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 242 | 🔻Пирятин Оперативний | `@PirOperative` | 5250 |  | 3.68 | 18% | 2% | нет | — | 0% | ua 0.98 other 0.01 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 243 | Пирятинська громада | `@piryatingromada` | 10997 |  | 2.43 | 93% | 6% | нет | — | 0% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 244 | Smirnovy.com – здоров'я та розвиток | `@smirnov108` | 14820 |  | 0.96 | 78% | 0% | да | 3.57 | 0% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 245 | АТБ | `@atb_market_official` | — |  | 0.89 | 100% | 12% | нет | — | 0% | ua 0.83 other 0.17 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 246 | Нутриціологія \| Молодість \| ЖИТТЯ | `@denisovapro` | 1087 |  | 0.79 | 68% | 0% | да | 0.21 | 0% | ua 0.94 en 0.06 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 247 | Розумний ФІТНЕС з Sashafitnesslife ❤️ | `@sashafitnesslife` | 3180 |  | 0.71 | 100% | 15% | да | 2.96 | 0% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 248 | Відгуки гайд схуднення | `@gaid_skobioale` | 2772 |  | 0.64 | 94% | 0% | нет | — | 0% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 249 | Психологія здоров’я Health Psychology | `@HealthPsycholog` | 6617 |  | 0.61 | 100% | 24% | да | 3.46 | 0% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 250 | Оголошення. Karlivka Live🇺🇦 | `@KarlivkaLive` | 539 |  | 0.43 | 100% | 0% | нет | — | 0% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 251 | Зіньків Новини | `@zinkivnews` | 3422 |  | 0.32 | 56% | 0% | нет | — | 0% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 252 | ПХ та схуднення 🍀 | `@Wellosophy_Lesya` | 1609 |  | 0.29 | 100% | 0% | нет | — | 0% | other 0.50 ua 0.50 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 253 | Оля \| розумний фітнес 💪 | `@olgaa_trainer` | 1421 |  | 0.29 | 62% | 0% | да | 0.14 | 0% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 254 | Мама, я Голодний😋 | `@mamaiagolodniy` | 35757 |  | 0.18 | 80% | 20% | нет | — | 0% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 255 | Оля CHIFIT\| тренування і харчування🔥 | `@chifit_family` | 2634 |  | 0.14 | 75% | 0% | да | 0.14 | 0% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 256 | Kkondratyuchka тренування | `@kkondr_fit` | 9276 |  | 0.07 | 100% | 50% | да | 0.14 | 0% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 257 | Лохвиця.info | `@LHVC_info` | 2603 |  | 0.04 | 100% | 0% | нет | — | 0% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 258 | Онлайн-тренування з Анастасією Давидюк | `@anastasiiadavydiukfitness` | 1320 |  | 0.04 | 100% | 100% | нет | — | 0% | ua 1.00 | store | in_registry · in_registry — measured on the store, not graded by this census |
| 259 | Mamix🥼 | `@itsmamix` | 280731 | ✓ | 0.00 | — | — | да | — | — | — | store | in_registry · in_registry — measured on the store, not graded by this census |
| 260 | ЗДОРОВЕ СХУДНЕННЯ | `@skhudnennya` | 3895 |  | 0.00 | — | — | да | — | — | — | store | in_registry · in_registry — measured on the store, not graded by this census |
| 261 | Марафон схуднення онлайн | `@hydnem_prosto` | 3108 |  | 0.00 | — | — | да | — | — | — | store | in_registry · in_registry — measured on the store, not graded by this census |
| 262 | ЛАБОРАТОРІЯ ДИТИНСТВА | `@lab_of_childhood` | 2484 |  | 0.00 | — | — | нет | — | — | — | store | in_registry · in_registry — measured on the store, not graded by this census |
| 263 | Дмитро Камінський \| Фітнес та Саморозвиток | `@dimakaminskyifit` | 2173 |  | 0.00 | — | — | да | — | — | — | store | in_registry · in_registry — measured on the store, not graded by this census |
| 264 | Дитяче меню | `@dutyache_menu` | 1635 |  | 0.00 | — | — | да | — | — | — | store | in_registry · in_registry — measured on the store, not graded by this census |
| 265 | Євгенія_Дитяче меню | `@Evgenija_dutjache_menu` | 1534 |  | 0.00 | — | — | да | — | — | — | store | in_registry · in_registry — measured on the store, not graded by this census |
| 266 | Я ЗДОРОВА | `@eftforhealth` | 1067 |  | 0.00 | — | — | да | — | — | — | store | in_registry · in_registry — measured on the store, not graded by this census |

---
Проза — 20 непустых строк (потолок PROCESS.md v2 — 30); оба листинга шага 0 и таблица идут экспонатами под ней, как парные таблицы. Числа — из `results/retail_census.json`; таблицу рендерит `scripts/retail_census_report.py`. `config/registry.yaml` не тронут: в этом контракте в реестр ничего не входит и ничего из него не выходит. Проект ревизии — `docs/reports/registry-revision-proposal.md`.
