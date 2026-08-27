# PROMPT — `retail-census` (fresh session; $0 GPU; Telegram API only; contract C1 of `docs/SPEC-v2-promo-pulse.md`)

You are the executor on `market-pulse-llm`. The operator re-specced the project on 27.08: stage 1 is
«промо-пульс сетей» — prices and comments under retailers' promo posts, with the list of retail chains
widened as far as it goes. Read `docs/SPEC-v2-promo-pulse.md` §2–§3 and `docs/STATUS.md` (rulings (х)),
then this file. `docs/SPEC.md` rev. 3.x stays frozen law for sealed records — do not edit it.

**Step 0 ($0).** Commit by path: `docs/STATUS.md`, `docs/SPEC-v2-promo-pulse.md`, this prompt. Delete the
network volume `mp-lora-c` (`runpodctl`): listing BEFORE and AFTER, `mp-srv2` present in both as the positive
control, both listings verbatim in the report; the guard line notes the deletion. Nothing else is created.

**The census.** Extend `scripts/discover_channels.py` with TWO new themes, keeping every existing theme carried
(`--carry`), run both, then `scripts/entry_check.py` over every new candidate. (1) `retail_chains`: queries in
UA/RU = chain names below + «акції», «знижки», «каталог», plus seed handles. (2) `poltava_chats`: Telegram
GROUPS/chats with open messaging per district centre of Poltava oblast (SPEC v2 §3, category B: Полтава,
Кременчук, Лубни, Миргород, Гадяч, Горішні Плавні, Пирятин, Хорол, Зіньків, Карлівка, Кобеляки, Решетилівка,
Глобине, Лохвиця, Гребінка, Шишаки, Диканька, Котельва, Нові Санжари, Оржиця, Чутове, Семенівка, Козельщина,
Машівка) × «чат», «спільнота», «оголошення», «барахолка»; a group is a candidate only if its history is readable
after joining — record `messages_open` and messages/day instead of comments/day. Chains to look for (official
channel + promo/deals channel + any channel with a linked discussion group): АТБ, Сільпо, Novus, METRO, Auchan,
Фора, Varus, Thrash!, Fozzy, ЕКО маркет, Велмарт, Близенько, Наш Край, Рукавичка, Коло, Delikat, Сім23,
Копійка, Таврія В, Ультрамаркет, MegaMarket, Zakaz.ua, Rozetka (продукти); Poltava region: Маркетопт/Толока,
Гурман, Файно маркет, Грош, Барвінок; promo aggregators: MSUa, Копійочка, Знижком, Хочу дешевше, «Акції та
знижки», Skidka. A chain with several channels lists each. Do not edit `config/registry.yaml` — candidates only.

**Per candidate, measured from one history request (last 4 weeks) — never typed:** handle resolves (blue
check?), subscribers, posts/day, share of posts that are leaflet pages or carry a price (`grn|₴|\d+[,.]\d\d`),
comments enabled + linked group, comments/day, **dairy share** = posts matching `config/lexicon.yaml`
`tracked.dairy|ice-cream` stems (the lexicon's own matcher rule), language mix. Already-registered channels
get the same row from the store (`data/raw/`), tagged `in_registry`.

**Output.** `results/retail_census.json` (rows + the queries + timestamps + FloodWait events) and
`docs/reports/retail-census.md` ≤30 lines + ONE table sorted by `dairy posts/day × (1 + comments/day)`,
columns as above, `verdict ∈ {enter | posts-only | reject}` with the reason from the entry-check vocabulary.
Add `docs/reports/registry-revision-proposal.md`: the 66 current sources in three lists — A retail, B Poltava,
PAUSED (moms/health/recipes/fitness — everything else) — with each channel's posts/day and comments/day from the
store; the operator rules on it, and only then a separate step writes the registry revision. Nothing enters or
leaves `config/registry.yaml` in this contract.

**Rules.** Read-only against Telegram (one channel at a time, the pause `entry_check.py` already keeps;
FloodWait aborts and keeps what was collected — report it). No GPU, no pod, no serverless. Deviations with
cause tags from the PROCESS enum. `make check` tail in the report. Do not edit team-lead files.
