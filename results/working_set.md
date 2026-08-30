# retail-census r2 — the working set

Rendered by `scripts/retail_working_set.py` from `results/retail_chains.json` (category A,
measured 2026-08-30) and `results/retail_census.json` (category B, r1's readings of
2026-08-27, NOT re-measured). Candidates and their basis — the pick is the operator's.

## A1 — prices and promo: channels that post them

Comments are not required here. `n` is the posts the share was computed over.

| chain | channel | subs | n | price share | dairy | posts/day | what the channel is |
|---|---|--:|--:|--:|--:|--:|---|
| Хочу дешевше | @xochydeshevshe | 621 | 10 | **1.000** | 0.000 | 0.357 | — |
| ЕКО маркет | @ekomarket_shop | 1341 | 17 | **0.882** | 0.412 | 0.607 | — |
| Знижком | @znishkom | 7166 | 168 | **0.762** | 0.000 | 6.000 | — |
| Епіцентр [not in SPEC §3 A] | @epicentrk_sale | 52081 | 137 | **0.657** | 0.051 | 4.893 | «ЕПІЦЕНТР», 52 081 subs, price .657 — but NOT linked from Епіцентр's own properties: epicentrk.ua carries no t.me and the official Instagram @epicentr_ua (191K) carries none either. It is a SEED handle from the research note, so its identity is the census's assumption, not the chain's word. |
| Фора | @foraINFO | 7506 | 10 | **0.600** | 0.200 | 0.357 | — |
| Rozetka продукти | @rrozetka | 369535 | 167 | **0.521** | 0.000 | 5.964 | the marketplace as a whole; the SPEC §3 name is its grocery vertical, which has no channel of its own — dairy share 0.000 is the marketplace's mix, not a grocer's. |
| Близенько | @blyzenkoua | 4985 | 57 | **0.351** | 0.018 | 2.036 | the chain's own channel, «БЛИЗЕНЬКО🌿», preview description «Мережа магазинів Близенько». blyzenko.ua links no t.me at all, so step 1 could not see it; r1's name search did. Measured on r1's 2026-08-27 clock, not re-measured. |
| Маркетопт | +Ejz6ubzm21IyMTQy | 42378 | 29 | **0.276** | 0.241 | 1.036 | «Маркетопт 🔆 Офіційна сторінка», 42 378 members — the chain's main channel, found via its official Instagram because it has no website. JOINED on the operator's word 2026-08-30 (logged in results/joins_5c1.jsonl, reversible), which is what made its history readable: this is the census's only row measured from inside. media_share 1.000 over 29 posts and no `грн`/`₴` hit at all — the prices are IN the flyer images, so the 0.276 text share understates it and the 5c2 vision instrument is what reads this row properly. |
| Varus | @VARUS_channel | 121086 | 134 | **0.246** | 0.194 | 4.786 | — |
| Сільпо | @silposilpo | 19714 | 33 | **0.212** | 0.152 | 1.179 | — |
| Fozzy | @fozzyshopua | 518 | 11 | **0.182** | 0.091 | 0.393 | «FOZZY Cash&Сarry» — the wholesale cash-and-carry format, not a retail store. |
| Сім23 | @sim23_simi | 5266 | 17 | **0.176** | 0.000 | 0.607 | — |
| Копійочка | @kop1chat | 4872 | 618 | **0.104** | 0.011 | 22.071 | — |
| Акції та знижки | @brovarysale | 3914 | 85 | **0.035** | 0.000 | 3.036 | — |

## A2 — comments: channels where the customer can answer

`*` marks a megagroup, where the column is messages/day: a group has no comments under
posts, its whole traffic is the conversation.

| chain | channel | subs | comments/day | price share | dairy | what the channel is |
|---|---|--:|--:|--:|--:|---|
| Rozetka продукти | @rrozetka | 369535 | 304.429 | 0.521 | 0.000 | the marketplace as a whole; the SPEC §3 name is its grocery vertical, which has no channel of its own — dairy share 0.000 is the marketplace's mix, not a grocer's. |
| Знижком | @znishkom | 7166 | 59.714 | 0.762 | 0.000 | — |
| Копійочка | @kop1chat | 4872 | 22.071* | 0.104 | 0.011 | — |
| Varus | @VARUS_channel | 121086 | 16.643 | 0.246 | 0.194 | — |
| Сім23 | @sim23_simi | 5266 | 0.607 | 0.176 | 0.000 | — |
| METRO | @HRCNc | 3359 | 0.071 | 0.000 | 0.231 | resolves to «HoReCaНець» — METRO's HoReCa (hotel/restaurant/café) B2B channel, not its retail one. Its dairy share is a wholesale audience's, not a shopper's. |
| Хочу дешевше | @xochydeshevshe | 621 | 0.000 | 1.000 | 0.000 | — |

**Chains with dairy AND open comments AND a shopper's audience: 1** — Varus (@VARUS_channel, dairy 0.194, 16.643 comments/day). Everything else is one or the other: METRO has dairy and comments but a HoReCa audience, ЕКО and Фора have the deepest promo and comments CLOSED.  Among aggregators, Копійочка (@kop1chat) carries dairy 0.011 — an order of magnitude below the chain above, and on r1's older clock.

## A3 — the chains' promo that their own sites never link

r1's name search measured these and the site instrument cannot see them: a chain does not
link a fan channel, and Близенько does not link its own. Identity confirmed by hand from
each channel's public preview; `own` means the chain's, `unofficial` a third party's, and
`unconfirmed` must NOT be collected before someone confirms it.

| chain | channel | kind | subs | price | comments | com/day | dairy | ua | identity |
|---|---|---|--:|--:|---|--:|--:|--:|---|
| АТБ | @ATB_FANatik | unofficial | 3446 | **1.000** | open | 0.250 | 0.059 | 1.00 | «ФАНАТИК АТБ \| АКЦІЇ» — a fan/deals channel, not ATB's. ATB's own @atb_market_official carries no promo and no comments |
| АТБ | @discountAtb | unofficial | 610 | **1.000** | open | 0.000 | 0.000 | 1.00 | «Знижки АТБ» — a deals channel |
| Zakaz.ua | @zakazzua | unofficial | 805 | **0.500** | closed | 0.000 | 0.000 | 0.50 | «Доставка з супермаркетів/Знижки» — not linked from zakaz.ua |
| Копійка | @kopiyka_tm | unconfirmed | 2362 | **0.500** | closed | 0.000 | 0.500 | 1.00 | titled «Копійка» with no description; dairy 0.500 is the highest in the census and rests on an unconfirmed identity — do not collect before confirming |
| Близенько | @blyzenkoua | own | 4985 | **0.351** | closed | 0.000 | 0.018 | 1.00 | preview says «Мережа магазинів Близенько» — the CHAIN's own channel; blyzenko.ua simply does not link it, which is why the site instrument missed it |
| АТБ | @ATBATBATBAT | unofficial | 276 | **0.238** | open | 0.036 | 0.000 | 1.00 | «НАШЕ АТБ / АКЦІЇ / НОВИНКИ» |
| Маркетопт | @rozlyvne | own | 7228 | **0.234** | open | 3.393 | 0.000 | 1.00 | preview says «Офіційний канал Маркетопт Розливне Пиво» — official, but the draft-beer line |
| Рукавичка | @RUKAVICHKAkr | unconfirmed | 623 | **0.200** | closed | 0.000 | 0.000 | 0.86 | «РУКАВИЧКА-КР» — reads like a local branch; no description, identity NOT confirmed |
| АТБ | @atbmarketznuzhku | unofficial | 7877 | **0.182** | closed | 0.000 | 0.091 | 0.91 | «АТБ знижки Україна \| Економія», description «Актуальні акції та знижки» |

**4 of these 9 have comments OPEN** — @ATB_FANatik (АТБ), @discountAtb (АТБ), @ATBATBATBAT (АТБ), @rozlyvne (Маркетопт). This is where a comment under a promo post actually exists for АТБ, whose own channel has neither promo nor comments.

Measured under a chain's name and NOT that chain — excluded on the record, not silently:

- `@chortkiv2` — «Наш край - Чортківщина», description «канал Чортківщини» — regional news, not the Наш Край chain
- `@ON_LINE_MO` — «Маркетопт ON_LINE» — its own description says «Ця група тільки для робітників мережі МаркетОпт»: a STAFF group, not a promo feed, despite a 0.460 price share
- `@ispkopiyka` — «Копійка» the internet provider (Dv871's original example)
- `@K_G_B_fin` — «Копійка гривню береже» — a personal-finance channel
- `@depositorfrank` — «Канал про гроші» — finance, matched on the word «Грош»

## B — Poltava oblast: the chats, by district centre

61 chats with verdict `enter`, across 21 of 24 district centres SPEC v2 §3 authorises. The Ukrainian-language bar is LIFTED (operator, 2026-08-30) — language is the `ua` column below, not a filter; at the former `ua >= 0.5` this table held 47 chats and 18 centres. A chat surfaced by two centres' queries is listed under both and counted once.

| district centre | chats | handles (subs · msgs/day · dairy · ua) |
|---|--:|---|
| Полтава | 13 | @fontan1000000chat (1017 · 42.2 · 0.002 · ua 0.83) · @chat_poltava (5582 · 42.2 · 0.001 · ua 0.41) · @Poltava_intelligence_chat (5198 · 41.1 · 0.003 · ua 0.35) · @poltava053 (625 · 41.0 · 0.000 · ua 0.23) · @poltava24na7 (1383 · 30.5 · 0.001 · ua 0.63) · @huevapoltava (980 · 17.1 · 0.002 · ua 0.66) · @poltava_obyava (162 · 13.6 · 0.003 · ua 0.85) · @baraholka_poltavaaa (236 · 10.8 · 0.003 · ua 0.36) · @Poltava_tviy_market (1182 · 8.9 · 0.008 · ua 0.85) · @tovarka_go (559 · 8.6 · 0.004 · ua 0.40) · @Poltava_OLX (14129 · 7.5 · 0.014 · ua 0.72) · @poltava_cooperation (499 · 1.4 · 0.000 · ua 0.82) · @Avto_Bara_Poltava (365 · 1.0 · 0.000 · ua 0.78) |
| Кременчук | 9 | @kremenchyk1 (11211 · 20.7 · 0.003 · ua 0.85) · @ogo_kremenchuk (281 · 13.3 · 0.003 · ua 0.82) · @Kremenchug_OLX (15600 · 8.1 · 0.009 · ua 0.56) · @Globino_Kremenchyg (204 · 5.2 · 0.007 · ua 0.94) · @svetlovodsk_baracholka (711 · 4.2 · 0.009 · ua 0.79) · @Kremenchuki (338 · 4.1 · 0.000 · ua 0.11) · @globinos (1798 · 1.1 · 0.000 · ua 0.94) · @kremik_chat (2697 · 0.2 · 0.000 · ua 0.67) · @Chat_Kremenchuk (279 · 0.0 · 0.000 · ua 0.00) |
| Лубни | 6 | @lubnyChat (2387 · 41.4 · 0.001 · ua 0.68) · @Vp9OhFMO9C5jZGIy (435 · 33.9 · 0.003 · ua 0.92) · @lubnyreklama988 (925 · 33.8 · 0.006 · ua 0.95) · @lubnya888 (259 · 17.9 · 0.000 · ua 0.00) · @barlybnu (747 · 1.9 · 0.000 · ua 0.94) · @zdgsdjgjj (670 · 0.9 · 0.000 · ua 0.95) |
| Миргород | 6 | @chatmirgo (5953 · 41.2 · 0.003 · ua 0.78) · @mirgorod_chat (1584 · 41.0 · 0.002 · ua 0.91) · @baraholka_mirgorod (2663 · 12.4 · 0.006 · ua 0.81) · @chatmirgorod (1219 · 10.7 · 0.007 · ua 0.81) · @fhdtdjdjgdsdjdj (2332 · 5.2 · 0.007 · ua 0.98) · @mirgorodreclama (1590 · 0.2 · 0.143 · ua 1.00) |
| Гадяч | 2 | @ogoloshennya_Gadyach (306 · 31.7 · 0.011 · ua 0.82) · @bkbsehjshg (404 · 0.5 · 0.000 · ua 0.89) |
| Горішні Плавні | 2 | @ogo_gorishniplavni (219 · 1.4 · 0.000 · ua 0.92) · @xxcbjhsfhsfghjjkkhg (974 · 0.3 · 0.000 · ua 0.86) |
| Пирятин | 3 | @Piryatin4AT (837 · 26.9 · 0.000 · ua 0.77) · @buypiryat (1612 · 17.8 · 0.002 · ua 0.82) · @xcvggjdhshkff (382 · 0.1 · 0.000 · ua 1.00) |
| Хорол | 4 | @Yaroslavski_haltura_shabashka (1536 · 41.6 · 0.003 · ua 0.00) · @Yaroslavskiy_BARAHOLKA_AVITO (952 · 40.4 · 0.001 · ua 0.00) · @khorol2026 (2410 · 22.2 · 0.002 · ua 0.88) · @barahHorol (348 · 0.7 · 0.000 · ua 0.00) |
| Зіньків | 2 | @zinkivchat (2257 · 33.9 · 0.003 · ua 0.67) · @shebshsjje (258 · 0.3 · 0.000 · ua 1.00) |
| Карлівка | 1 | @sdhdsjjhsjsjsj (341 · 0.2 · 0.000 · ua 0.83) |
| Кобеляки | 1 | @dhdhdhshsdhjsjbsj (1209 · 6.1 · 0.000 · ua 0.75) |
| Решетилівка | 1 | @reshetrobota (204 · 2.3 · 0.000 · ua 0.85) |
| Глобине | 4 | @h_globino_official1 (2154 · 41.9 · 0.000 · ua 0.70) · @Globino_Kremenchyg (204 · 5.2 · 0.007 · ua 0.94) · @dghjjhffhjchufusjsjjsjdjdh (2739 · 1.2 · 0.061 · ua 1.00) · @globinos (1798 · 1.1 · 0.000 · ua 0.94) |
| Лохвиця | 1 | @xjsjejhjfgdhhdznghjjjt (681 · 1.1 · 0.000 · ua 0.92) |
| Гребінка | 1 | @gshsgswerdfgghjtyjjy (368 · 1.1 · 0.000 · ua 0.83) |
| Шишаки | 2 | @shyshaky_chat (1449 · 3.8 · 0.010 · ua 0.86) · @xddfhnhfsdf (2154 · 1.1 · 0.000 · ua 0.96) |
| Диканька | 0 | — |
| Котельва | 1 | @dfhjjhffgssjshh (440 · 0.5 · 0.000 · ua 0.38) |
| Нові Санжари | 1 | @cdfrsjsjsjsjsjwjwjej (377 · 1.4 · 0.000 · ua 0.83) |
| Оржиця | 1 | @orzhicaoriginal (94 · 0.4 · 0.000 · ua 0.56) |
| Чутове | 0 | — |
| Семенівка | 1 | @semenivka_ogoloshennya (2721 · 14.5 · 0.002 · ua 0.51) |
| Козельщина | 0 | — |
| Машівка | 1 | @mashivkashop_ua (82 · 2.9 · 0.049 · ua 0.52) |

**3 district centres carry no chat in the working set**, for three different reasons — and the difference decides which of them money can fix:

- **Диканька** — 1 of 1 measured chat(s) resolve and are OPEN, and carry ZERO messages in the 28-day window — the chat exists and is silent, which no budget changes: @dykanka_chat
- **Чутове** — nothing found at any bar — a finding about Ukraine, not about the budget
- **Козельщина** — 1 of 1 measured chat(s) resolve and are OPEN, and carry ZERO messages in the 28-day window — the chat exists and is silent, which no budget changes: @kozelshchynabazar

## What the two categories are for

The chains' own channels are a PRICE instrument: of the ones with a channel, almost all
have comments closed, and the open ones are B2B, a marketplace, or carry no dairy. The
customer's voice on dairy is therefore not under the chains' promo posts — it is in the
Poltava chats, which is what category B exists for and what SPEC v2 §3 already ruled.
