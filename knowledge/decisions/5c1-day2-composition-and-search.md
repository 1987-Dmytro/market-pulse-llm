---
type: decision
status: accepted
date: 2026-08-08
tags: [decision, phase5, composition, discovery]
---

# 5c1 day 2 — three "city feeds" were chats, and the search for replacements outperformed the scan

`docs/PROMPT-5c1-day2.md` was the day's whole order: exits, joins, three gate batches, the window,
the census, the searches, the audience fill and the harvest. The order executed end to end, and
the operator ruled twice more during it. Registry **39 → 67** = launch 60 + watch 7, excluded
across the phase **33**. Everything below is provisional pending the yield screen of amendment
3.12 — the rider says so in the brief's own words, and no loop run consumes this composition until
the operator signs after those numbers exist.

## (1) The ruling: a supergroup is not a city feed

Three of «Дозаявка №3»'s sixteen came back `broadcast=false, megagroup=true`:

| handle | subscribers | "posts"/week | what that number is |
|---|---|---|---|
| @poltava_misto | 60,028 | 111.25 | member chat traffic |
| @kremenchug_live | 16,056 | 77.25 | member chat traffic |
| @Karlivka_live | 8,045 | 197.25 | member chat traffic |

Exactly the class @Mambabyua (280/week) and @kulinariya_chat_a (300/week) were excluded for on
06.08, with the chat-mining track recorded as deferred. The operator ruled all three out on that
precedent. Regional entered 11 of 16 on the day, before the replacements below.

## (2) The replacement economics, written down because they are not favourable everywhere

@Karlivka_live's LINKED object turned out to be a broadcast channel of the same town — the canon
had taken the chat's handle. It went to the gate as «Дозаявка №9» and passed, and the cost of the
swap is in its ruling rather than after it:

| town | left | entered | ratio |
|---|---|---|---|
| Карлівка | @Karlivka_live 8,045 | @KarlivkaLive 539 | 0.07× |
| Полтава | @poltava_misto 60,028 | @poltava_pvp 106,761 + @poltava20 43,486 | 2.5× |
| Кременчук | @kremenchug_live 16,056 | @h_kremenchug 137,221 + @kremen_news 28,286 | 10.3× |

«Карловка покрыта» must not be read off the first row.

## (3) The measured finding: name-scanning under-covers

The Poltava/Kremenchuk replacements came from the operator's own one-line addition to step 7 —
search for broadcast analogues of the two towns whose handle had just left. **Three of the four
picks were not in the 119-candidate town-name discovery scan at all**, @h_kremenchug (137,221)
included. `discover_channels` walks a list of TOWN NAMES; `contacts.SearchRequest` ranks by
Telegram's own relevance over the same words, and only the second reached the town's largest feed.
A free, measured argument for SPEC 3.12 (2)'s content-first discovery before any Stars are spent.

Alert and war-digest feeds were deliberately NOT taken (@region_poltava_syrena 195,553,
@treeshkremik 49,521) — see (5).

## (4) Five flags cleared, one FAIL moved, and what separates the two

`CLEARED` downgrades a FLAG to PASS **before** routing, because `GATED_LATE` and the city path both
refuse a non-PASS row; it covers a FLAG and refuses a FAIL. Each of the five was raised about a
discussion group on a channel that enters posts-only and never joins one — the flag was about a
capability the standing rule declines to use. The gate rows still say FLAG; the clearance rides in
the ruling text.

A FAIL is a bucket change, not a clearance. @lab_of_childhood: 0 posts in the 28-day window failed
it, 49 posts running to 2026-06-04 are why it is not dead, and `watch` is that state exactly.
@tadaua left dead — 71 subscribers, three posts in its whole history, the last 2025-01-02.

## (5) The market screen's first false positives are war reporting

All three RF_FLAGs over the 67 are Ukrainian city feeds on the same sentence shape:

| handle | rf / ua / window | quoted line |
|---|---|---|
| @myrhorodtown | 2 / 50 / 273 | «склади Wildberries розбомбили під Санкт-Петербургом» |
| @poltava_informue | 1 / 947 / 1,316 | «пожежі на складах Wildberries» |
| @poltava20 | 1 / 688 / 1,535 | «Українські БПЛА рознесли … хабів … Wildberries в Електросталі» |

There is no stop-word fix: *Wildberries* IS an RF retailer and naming it IS what the screen is for.
The ratio reads the row. Report-only by design; the reading is the operator's, and this is the
shape that makes that design correct rather than cautious.

The census and the market screen also disagreed about @dikankaa and both were right: RU_DOMINANT
(ru 1.00 over 20 decidable posts, its own text covering «Волгоградской области ( Энгельс,
Саратов )») against NO_EVIDENCE, because those oblasts are not in a table of places a MARKET is in.
Neither instrument subsumes the other.

## (6) What the day collected

9,393 posts and **4,880 comments** over 63 channels, 0 damaged lines, `shasum -c` 6/6, 0 threads
outstanding, queue **16,218 rows** (5a's 11,338 v1 backlog plus these 4,880). Ten joins landed on
the fifteen-minute pace with no FloodWait on ~100 resolves — every collection run carried `--only`,
because `collectable()` returns the whole registry and a bare `--comments` is 67 resolves for five
channels of work.

**The two handles step 7 resolved carry 81% of everything collected**: @matusi_ukr 2,890 comments
over 156 threads and @mandziak 1,048 over 104. Neither existed as a handle in this repo that
morning. `mothers_kids` went from 0 live sources to 3.

## Searches, all closed by record

Five national chains NEGATIVE (Velmart's channel has 3 subscribers; Auchan has only its Russian
one, @auchanrus 82,813; METRO's name is held by resellers on 13 and 3). Max Control NEGATIVE —
@maxcontrol exists and has 2 subscribers. Handle top-up 2 of 5: @matusi_ukr (19,278 against
TGStat's ~19.3k) and @mamo_nepsichuy (13,781 against ~13.8k) confirmed by SIZE, while «Все про
дітей» matched a 277-subscriber namesake where 23.7k was expected and «Сучасні батьки» a
10-subscriber one against 36.4k. A title is copyable; a subscriber count is not.

## Open, and carried to the next contract

The theme of @pavlushaiyava and @mandziak is measured by nothing — `entry_check` grades capability,
liveness, language and group, the census grades language. Their segments are EXPECTATIONS and the
code says so. Together with @dikankaa and the three RF_FLAGs, that is what the yield screen of
[[5b2-batch-measurement]]'s successor contract — SPEC amendment 3.12 (1) — is asked to answer.

Artifacts: `results/entry_gate_5c1.json` (96 rows, rulings, 14 closed search notes) ·
`results/collect_5c1.json` · `results/language_census_5c1_day2.json` ·
`results/market_screen_5c1_day2.json` · `results/harvest_mothers_ua.json` ·
`results/joins_5c1.jsonl` · canon `docs/CHANNELS-launch.md`, sections «Рулинги гейта дня 2» and
«Дозаявка №10».
