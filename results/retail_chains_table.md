# retail-census r2 — one row per chain (36 rows)

Built by `scripts/retail_chains_report.py` from `results/retail_chains.json`. Sorted by
comments open, then price share; rows with no channel are at the bottom and say why.
`instr.` is which instrument read the site (`curl` · `curl+bundle` · `browser`), and
`measured` is which census measured the channel — r1's window ends 2026-08-27, r2's
2026-08-30, so the two must not be read as one clock. `n` is the posts the shares were
computed over — `price 1.000` over n=10 is not the claim `price 0.762` over n=168 is.
A `*` on `com/d` marks a megagroup, where the column is messages/day: a group has no
comments under posts, its whole traffic is the conversation.

| # | chain | site | site read | instr. | handle | subs | posts/d | n | price | comments | com/d | dairy | language | verdict | Ukraine screen | measured |
|--:|---|---|---|---|---|--:|--:|--:|--:|---|--:|--:|---|---|---|---|
| 1 | Хочу дешевше | — | aggregator — answered from r1's Telegram measurement | — | @xochydeshevshe | 621 | 0.357 | 10 | 1.000 | yes | 0.000 | 0.000 | ua 1.00 | enter | keep | api (r1, 2026-08-27) |
| 2 | Знижком | — | aggregator — answered from r1's Telegram measurement | — | @znishkom | 7166 | 6.000 | 168 | 0.762 | yes | 59.714 | 0.000 | ua 1.00 | enter | keep | api (r1, 2026-08-27) |
| 3 | Rozetka продукти | rozetka.com.ua | ok | browser | @rrozetka | 369535 | 5.964 | 167 | 0.521 | yes | 304.429 | 0.000 | ua 0.99 other 0.01 | enter | keep | api (r2) |
| 4 | Varus | varus.ua | ok | curl | @VARUS_channel | 121086 | 4.786 | 134 | 0.246 | yes | 16.643 | 0.194 | ua 0.83 other 0.17 | enter | keep | api (r2) |
| 5 | Сім23 | sim23.ua | ok | curl | @sim23_simi | 5266 | 0.607 | 17 | 0.176 | yes | 0.607 | 0.000 | ua 1.00 | enter | keep | api (r2) |
| 6 | Копійочка | — | aggregator — answered from r1's Telegram measurement | — | @kop1chat | 4872 | 22.071 | 618 | 0.104 | yes | 22.071* | 0.011 | ua 0.86 other 0.13 | enter | keep | api (r1, 2026-08-27) |
| 7 | METRO | metro.ua | ok | browser | @HRCNc | 3359 | 0.929 | 26 | 0.000 | yes | 0.071 | 0.231 | ua 1.00 | enter | keep | api (r2) |
| 8 | ЕКО маркет | eko.com.ua | ok | curl | @ekomarket_shop | 1341 | 0.607 | 17 | 0.882 | no | 0.000 | 0.412 | ua 1.00 | posts-only | keep | api (r2) |
| 9 | Епіцентр [not in SPEC §3 A] | epicentrk.ua | ok (site links no t.me; handle is a seed, not the chain's own link) | seed handle + browser check of the chain's properties | @epicentrk_sale | 52081 | 4.893 | 137 | 0.657 | no | 0.000 | 0.051 | ua 1.00 | posts-only | keep | api (r3) |
| 10 | Фора | fora.ua | ok | curl+bundle | @foraINFO | 7506 | 0.357 | 10 | 0.600 | no | 0.000 | 0.200 | ua 1.00 | posts-only | keep | api (r2) |
| 11 | Близенько | blyzenko.ua | no-link | curl | @blyzenkoua | 4985 | 2.036 | 57 | 0.351 | no | 0.000 | 0.018 | ua 1.00 | posts-only | keep | api (r1, 2026-08-27) |
| 12 | Маркетопт | — | no site — official Instagram carries the Telegram | browser (official social property) | +Ejz6ubzm21IyMTQy | 42378 | 1.036 | 29 | 0.276 | no | 0.000 | 0.241 | ua 1.00 | — | keep | api (r4, after joining) |
| 13 | Сільпо | silpo.ua | ok | browser | @silposilpo | 19714 | 1.179 | 33 | 0.212 | no | 0.000 | 0.152 | ua 1.00 | posts-only | keep | api (r2) |
| 14 | Fozzy | fozzyshop.ua | ok | curl | @fozzyshopua | 518 | 0.393 | 11 | 0.182 | no | 0.000 | 0.091 | ua 1.00 | posts-only | keep | api (r2) |
| 15 | Акції та знижки | — | aggregator — answered from r1's Telegram measurement | — | @brovarysale | 3914 | 3.036 | 85 | 0.035 | no | 3.036* | 0.000 | ua 0.86 other 0.10 | enter | keep | api (r1, 2026-08-27) |
| 16 | АТБ | atbmarket.com | ok | browser (official social property) | @atb_market_official | 41858 | 1.107 | 31 | 0.000 | no | 0.000 | 0.000 | ua 1.00 | posts-only | keep | api (r3) |
| 17 | Таврія В | tavriav.ua | ok | curl | +Gpo70IWKXOE1NzZi | — | — | — | — | — | — | — | — | ChatInvitePeek | keep | api (r2) |
| 18 | Novus | novus.ua | ok | browser | — | — | — | — | — | — | — | — | — | — | — | — |
| 19 | Auchan | auchan.ua | ok | curl | — | — | — | — | — | — | — | — | — | — | — | — |
| 20 | Thrash! | thrash.ua | no-link | browser | — | — | — | — | — | — | — | — | — | — | — | — |
| 21 | Велмарт | velmart.ua | ok | curl | — | — | — | — | — | — | — | — | — | — | — | — |
| 22 | Наш Край | nashkraj.ua | no-link | curl | — | — | — | — | — | — | — | — | — | — | — | — |
| 23 | Рукавичка | rukavychka.ua | ok | curl | — | — | — | — | — | — | — | — | — | — | — | — |
| 24 | Коло | kolo.ua | no-link | curl | — | — | — | — | — | — | — | — | — | — | — | — |
| 25 | Delikat | delikat.site | ok | curl | — | — | — | — | — | — | — | — | — | — | — | — |
| 26 | Копійка | kopiyka.ua | ok | curl | — | — | — | — | — | — | — | — | — | — | — | — |
| 27 | Ультрамаркет | ultramarket.ua | no-link | curl | — | — | — | — | — | — | — | — | — | — | — | — |
| 28 | MegaMarket | megamarket.ua | no-link | curl | — | — | — | — | — | — | — | — | — | — | — | — |
| 29 | Zakaz.ua | zakaz.ua | ok | browser | — | — | — | — | — | — | — | — | — | — | — | — |
| 30 | Толока | — | no-site-verified | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 31 | Гурман | — | no-site-verified | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 32 | Файно маркет | fayno.market | no-link | curl | — | — | — | — | — | — | — | — | — | — | — | — |
| 33 | Грош | grosh.ua | no-link | curl | — | — | — | — | — | — | — | — | — | — | — | — |
| 34 | Барвінок | — | no-site-verified | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 35 | MSUa | — | aggregator — answered from r1's Telegram measurement | — | — | — | — | — | — | — | — | — | — | no Ukrainian channel found | reject · not the Ukrainian market | api (r1, 2026-08-27) |
| 36 | Skidka | — | aggregator — answered from r1's Telegram measurement | — | — | — | — | — | — | — | — | — | — | no Ukrainian channel found | reject · not the Ukrainian market | api (r1, 2026-08-27) |

## Why a row has no channel

- **Novus** — site read, and it links only a Telegram bot (@novus_ai_assistant_bot) — no channel to collect
- **Auchan** — site read, and it links only a Telegram bot (@Auchan_Info_bot) — no channel to collect
- **Thrash!** — site READ in a browser and carrying no t.me link
- **Велмарт** — site read, and it links only a Telegram bot (@VelmartUaBot, @Velmart_FeedBack_bot) — no channel to collect
- **Наш Край** — site READ, twice (HTML and its JS bundle), and carries no t.me link
- **Рукавичка** — site read, and it links only a Telegram bot (@rukavychka_chat_bot) — no channel to collect
- **Коло** — site READ, twice (HTML and its JS bundle), and carries no t.me link
- **Delikat** — site read; its only Telegram is the Делікат group's FLORIST brand Bloom, not the grocery chain: delikat.site is «сім'я магазинів» and the grocery brand's own links there are Facebook and Instagram, neither of them Telegram. Not counted as Delikat's channel.
- **Копійка** — site read, and it links only a Telegram bot (@kopiyka_ua_bot) — no channel to collect
- **Ультрамаркет** — site READ, twice (HTML and its JS bundle), and carries no t.me link
- **MegaMarket** — site READ, twice (HTML and its JS bundle), and carries no t.me link
- **Zakaz.ua** — site read, and it links only a Telegram bot (@help_zakaz_ua_bot) — no channel to collect
- **Толока** — web discovery finds no retail chain of this name; «толока» is the Ukrainian word for a community work-day, which is what the searches return. SPEC v2 §3 pairs it with «Маркетопт»; the pairing is not visible in any source found.
- **Гурман** — no Poltava-region chain with a site: the name belongs to a shop in Південне (Instagram only) and to gurman-dnepr.com.ua in Dnipro. `gurman.ua` is a domain-for-sale page.
- **Файно маркет** — site READ, twice (HTML and its JS bundle), and carries no t.me link
- **Грош** — site READ, twice (HTML and its JS bundle), and carries no t.me link
- **Барвінок** — the retail brand no longer exists: the chain was sold in December 2015 and bought by ATB-Market in 2016, and every «Барвінок» store was rebranded to «АТБ». This is why r1's name search returned an ОСББ «Барвінок» — there is no retail channel to find.
- **MSUa** — every r1 row for «MSUa» is below ua 0.5 or already rejected
- **Skidka** — every r1 row for «Skidka» is below ua 0.5 or already rejected

Chains whose site links a Telegram BOT and no channel: Novus (@novus_ai_assistant_bot), Auchan (@Auchan_Info_bot), Велмарт (@VelmartUaBot, @Velmart_FeedBack_bot), Рукавичка (@rukavychka_chat_bot), Копійка (@kopiyka_ua_bot), Zakaz.ua (@help_zakaz_ua_bot)
