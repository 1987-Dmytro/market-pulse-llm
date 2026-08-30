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
| Фора | @foraINFO | 7506 | 10 | **0.600** | 0.200 | 0.357 | — |
| Rozetka продукти | @rrozetka | 369535 | 167 | **0.521** | 0.000 | 5.964 | the marketplace as a whole; the SPEC §3 name is its grocery vertical, which has no channel of its own — dairy share 0.000 is the marketplace's mix, not a grocer's. |
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

## B — Poltava oblast: the chats, by district centre

47 chats, `enter`, `ua >= 0.5`, across 18 of 24 district centres SPEC v2 §3 authorises. These are r1's readings, not re-measured in r2. A chat surfaced by two centres' queries is listed under both and counted once.

| district centre | chats | handles (subs · msgs/day · dairy) |
|---|--:|---|
| Полтава | 8 | @fontan1000000chat (1017 · 42.2 · 0.002) · @poltava24na7 (1383 · 30.5 · 0.001) · @huevapoltava (980 · 17.1 · 0.002) · @poltava_obyava (162 · 13.6 · 0.003) · @Poltava_tviy_market (1182 · 8.9 · 0.008) · @Poltava_OLX (14129 · 7.5 · 0.014) · @poltava_cooperation (499 · 1.4 · 0.000) · @Avto_Bara_Poltava (365 · 1.0 · 0.000) |
| Кременчук | 7 | @kremenchyk1 (11211 · 20.7 · 0.003) · @ogo_kremenchuk (281 · 13.3 · 0.003) · @Kremenchug_OLX (15600 · 8.1 · 0.009) · @Globino_Kremenchyg (204 · 5.2 · 0.007) · @svetlovodsk_baracholka (711 · 4.2 · 0.009) · @globinos (1798 · 1.1 · 0.000) · @kremik_chat (2697 · 0.2 · 0.000) |
| Лубни | 5 | @lubnyChat (2387 · 41.4 · 0.001) · @Vp9OhFMO9C5jZGIy (435 · 33.9 · 0.003) · @lubnyreklama988 (925 · 33.8 · 0.006) · @barlybnu (747 · 1.9 · 0.000) · @zdgsdjgjj (670 · 0.9 · 0.000) |
| Миргород | 6 | @chatmirgo (5953 · 41.2 · 0.003) · @mirgorod_chat (1584 · 41.0 · 0.002) · @baraholka_mirgorod (2663 · 12.4 · 0.006) · @chatmirgorod (1219 · 10.7 · 0.007) · @fhdtdjdjgdsdjdj (2332 · 5.2 · 0.007) · @mirgorodreclama (1590 · 0.2 · 0.143) |
| Гадяч | 2 | @ogoloshennya_Gadyach (306 · 31.7 · 0.011) · @bkbsehjshg (404 · 0.5 · 0.000) |
| Горішні Плавні | 2 | @ogo_gorishniplavni (219 · 1.4 · 0.000) · @xxcbjhsfhsfghjjkkhg (974 · 0.3 · 0.000) |
| Пирятин | 3 | @Piryatin4AT (837 · 26.9 · 0.000) · @buypiryat (1612 · 17.8 · 0.002) · @xcvggjdhshkff (382 · 0.1 · 0.000) |
| Хорол | 1 | @khorol2026 (2410 · 22.2 · 0.002) |
| Зіньків | 2 | @zinkivchat (2257 · 33.9 · 0.003) · @shebshsjje (258 · 0.3 · 0.000) |
| Карлівка | 1 | @sdhdsjjhsjsjsj (341 · 0.2 · 0.000) |
| Кобеляки | 1 | @dhdhdhshsdhjsjbsj (1209 · 6.1 · 0.000) |
| Решетилівка | 1 | @reshetrobota (204 · 2.3 · 0.000) |
| Глобине | 4 | @h_globino_official1 (2154 · 41.9 · 0.000) · @Globino_Kremenchyg (204 · 5.2 · 0.007) · @dghjjhffhjchufusjsjjsjdjdh (2739 · 1.2 · 0.061) · @globinos (1798 · 1.1 · 0.000) |
| Лохвиця | 1 | @xjsjejhjfgdhhdznghjjjt (681 · 1.1 · 0.000) |
| Гребінка | 1 | @gshsgswerdfgghjtyjjy (368 · 1.1 · 0.000) |
| Шишаки | 2 | @shyshaky_chat (1449 · 3.8 · 0.010) · @xddfhnhfsdf (2154 · 1.1 · 0.000) |
| Диканька | 0 | — |
| Котельва | 0 | — |
| Нові Санжари | 1 | @cdfrsjsjsjsjsjwjwjej (377 · 1.4 · 0.000) |
| Оржиця | 0 | — |
| Чутове | 0 | — |
| Семенівка | 1 | @semenivka_ogoloshennya (2721 · 14.5 · 0.002) |
| Козельщина | 0 | — |
| Машівка | 0 | — |

**6 district centres carry no chat in the working set**, for three different reasons — and the difference decides which of them money can fix:

- **Диканька** — 1 candidate(s) found and NEVER measured — the FloodWait stopped the pass; still buyable
- **Котельва** — measured, and @dfhjjhffgssjshh IS collectable (`enter`) — it is held out by the Ukrainian bar alone, ua 0.38 < 0.5. Lowering that bar is the operator's
- **Оржиця** — 2 candidate(s) found and NEVER measured — the FloodWait stopped the pass; still buyable
- **Чутове** — nothing found at any bar — a finding about Ukraine, not about the budget
- **Козельщина** — 1 candidate(s) found and NEVER measured — the FloodWait stopped the pass; still buyable
- **Машівка** — 3 candidate(s) found and NEVER measured — the FloodWait stopped the pass; still buyable

## What the two categories are for

The chains' own channels are a PRICE instrument: of the ones with a channel, almost all
have comments closed, and the open ones are B2B, a marketplace, or carry no dairy. The
customer's voice on dairy is therefore not under the chains' promo posts — it is in the
Poltava chats, which is what category B exists for and what SPEC v2 §3 already ruled.
