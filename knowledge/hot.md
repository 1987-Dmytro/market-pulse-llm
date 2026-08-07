<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-08-07 20:36:01 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
789c352 docs(5c1): D63 — every commit now runs its own suite, and the checker has a bias
fdf4115 docs(5c1): the SPEC's two new rulings, and D45-D62
bad3ee7 feat(5c1): the retail addition, the chain searches, and a screen that stops overwriting its own evidence
8c64103 feat(5c1): wave 3 — seventeen exits, registry 56 to 39
b90c2e0 feat(5c1): the language census — 21 UA, 3 RU, and 36 sources it cannot rule on
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `5b2-batch-measurement.md` — 5b.2 — the batch measurement failed on memory, and serving is fixed at batch 1
- `5b-parity-abort-and-pod-runtime.md` — The pair aborted on a runtime that never took a job, and production moves to a stop-after pod

## 📅 Recent daily logs

- `2026-08-07.md`
- `2026-08-06.md`
- `2026-08-05.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->

# Hot Cache — curated

**Last update:** 2026-08-07 22:15 (day-2 pre-flight: **the market screen exists** and flags nothing
on the live 39, «Дозаявка №8»'s six are wired, and the gate now refuses inside the wall — it did
not, and I walked into it. Before: 21:00 wave 3 → registry 39; 20:05 addendum 9; 19:40 the census — 21 UA · 3 RU · 36 without a
verdict — and three joins held pending the operator's word. Before it, 18:52: "Дозаявка №5" wired
and queued; 16:52: wave 2 · "Дозаявка №3" · `audience`).
**5c1 is executed except the tail of the joins.** The morning's "nothing was executed" is gone: 18
commits `82ddfe1` → `2fc784a`, `make check` 1028 → **1137 passed**, **$0** spent, and the CA-MTL-3
volume is **deleted** so its
~$0.24/day has stopped. The launch composition was rebuilt four times in one day — 51 → 48
(rulings) → 43 (theme screen) → **42** (wave 2: @uasaler out entirely) — and the day ended against
an **account-wide FloodWait of 20 hours** on username resolution, clearing **2026-08-08 10:02
UTC**. This block is hand-edited; the section above it is auto-generated, do NOT touch the marker.

## 🔥 What's Hot

**THE GATE GRADES CAPABILITY, NOT THEME — AND THAT GAP COST FIVE CHANNELS.** The 5c1 track-R gate
checks resolve, liveness, language, discussion group and comment flow. It never checked what a
channel is ABOUT, except the two the operator pre-registered by name. The composition's themes came
from 5a1 discovery TAGS, and a tag says what a search query matched. The operator saw «Чат
Аліекспрес» in their own client and the hole opened. `results/theme_screen_5c1.json` put a number on
it from the window already collected — $0, offline, on `measure_categories.py`'s own lexicon:
**of 44 measurable launch channels, 23 have zero dairy posts and 15 have zero food posts of any
kind.** Two distinct failures: OFF-TOPIC (@znishkom = 191 posts of Steam game discounts,
@whitecode_zny = footwear, @offspringrus = a Russian baby-goods shop) and TEXT-FREE (@discountua1,
@ATB_FANatik — flyer reposts with the products inside the images). **Any future entry gate must
screen theme, or it admits the same class again.**

**AN ACCOUNT-WIDE FLOODWAIT OF 20 HOURS, CLEARING 2026-08-08 10:02 UTC.** 72,312 s on
`ResolveUsernameRequest` — the request every join, every comment fetch and every gate check starts
with, so it closes ALL of them, not one channel. The bill is cumulative: 63 gate rows + 119
discovery candidates + three searches + 13 joins in one day. It is written into
`results/joins_5c1.jsonl` with its expiry and `scripts/collect_5c1.py` **refuses to start** until it
passes. **Do not retry inside the window** — that is how 20 hours becomes longer.

**THE LAUNCH SET IS 42, NOT 51.** `config/registry.yaml` holds **56 sources** = 4 registry + 21
comment-capable + 17 posts-only + 14 watch. `docs/CHANNELS-launch.md` still says «запуск 51» in its
tables; its two rulings sections amend them, and the registry is what the loop reads. Excluded:
**12** (4 flagged 07.08 + the withdrawn late addition + @akcii_skidki_plt + the theme screen's 5 +
@uasaler). The wave-2 ruling closed the last open composition question: the 07.08 word named the
CHAT, the 08.08 ruling names the CHANNEL, so it left the registry entirely. **Removing a source
does not retract its rows** — its 30 posts are still in the raw store, which is why collection
totals carry a basis.

**THE REGISTRY HAS A THIRD DIMENSION: `audience`, FILLED FOR ALL 56.** Beside `source_type` (who
runs it) and the taxonomy (what is discussed) — whose audience a source speaks to. Closed list of
eight in `market_pulse.registry.AUDIENCES`: retail_official 5 · supermarket_deals 4 ·
cooking_recipes 13 · mothers_kids 9 · baby_food 7 · health_fitness 17 · food_quality_gov 1 ·
**regional 0** until the 16 city feeds pass the gate. **Keyed by HANDLE, never by source id** —
`@VARUS_channel` is `varus`, `@silposilpo` is `silpo`, so an id-keyed table looks complete and
ships nulls. The assignment is the canon's table, held to it by a test that parses the section;
5c2 keys aggregates on it and folding (retail = official + deals) is the report's job, so the
registry stays granular.

**THE WINDOW IS COLLECTED AND THE COMMENTS ARE NOT.** `results/collect_5c1.json`: **2,132 posts**
over 58 channels, window fixed at `since 2026-07-10T10:33:14Z`, 0 damaged lines, `shasum -c` **6/6**
after the run. Comments: **106 rows, one channel** (@tretyakovaele) — the write path is proven on a
real thread, the rest waits on joins. **11 of 21 authorised joins have landed**; two joined groups
were later thrown out (@uasaler, @znishkom) and the operator had already deleted those chats in
their own client.

**THE DRY-RUN'S `rows_to_inference` IS NOT THE WINDOW QUEUE.** `queue_depth` counts every stored
comment above the inference watermark, and that watermark has never moved — so the number is the
full v1 history of the four original channels, exactly the backlog ruling 22 DEFERRED. It now reads
**11,444**, which is 5a's 11,338 plus the **106** comments this phase collected: the delta is the
whole of 5c1's contribution, and the 2,132 posts contribute nothing because the queue counts comment
rows. The window's comment queue is what 5c2 prices and it barely exists yet. The watermark is an
id, the window is a date; the dry run as written cannot show it.

**THE VOLUME IS GONE.** Operator ruling on `results/volume_calc_5c1.json`: option (b). `runpodctl
network-volume list` returned one volume before and **`[]` after** — proven by listing, never by an
exit code. Storage+boot per month: keep $9.66 · delete-and-restage **$2.53** · stopped pod $7.61.
The decisive argument was the **datacenter unpin**, not the $7.14. The arm-A adapter was verified to
have a second local copy (`b3ca6308…`, directory hash) BEFORE the delete. The ~2026-09-05 review is
closed.

**WHAT 5c READS, AND IT SAYS BATCH 1.** `results/serving_5b.json` → `adopted`: `batch_size: 1`,
`adopted: false`, `measured_at_batch_size: 16`, **$0.5993/1000 rows**, **$0.4611/pass**,
**4.065 s/row**, cold start **46.2 s** off local NVMe (278.9 s off the network volume — that figure
lives in `scripts/runbook_5b.md`, NOT in serving_5b.json). Beside it, `results/parity_5b_a.json`:
config A on a booted-per-pass A6000 pod, **758/758 rows**, every reported number identical to the
4.5h2 anchor, delta **+0.0000**. A per-row identity cannot be claimed — arm A's dump was lost 04.08.

**BATCH IS CLOSED BY THE RULE, NOT BY THE NUMBERS.** `results/batch_5b2_verdict.json` →
`outcome: failed-measurement-oom`. **Batch 1, permanently** — only a NEW pre-registration can move
it, and the team lead does not recommend it. [[5b2-batch-measurement]]

**THE ARTIFACT PHASE 5 SERVES IS THE NF4 BASE PLUS THE UNMERGED ARM-A ADAPTER** (`b3ca6308…`,
2 171 rows, rendering `T1v2_with_post`, every eval at batch 1). **Merging stays forbidden** — 5b's
pair aborted, which closes the question in favour of A. [[5b-parity-abort-and-pod-runtime]]

**THE GATES ARE 3 of 5 and CLOSED, not pending** — G1a FAIL (0.9214 / bar 0.9470), G1b PASS 23/38
exactly on the bar, **G1c FAIL by 0.0005**, G1d and G1e PASS. No bar moves and nothing is re-run.
[[45h2-ablation-verdict]]

**ARM A'S PER-ROW DUMP IS LOST** — `results/predictions/LOST.md`. No gate number moves; what is gone
is the **re-score**, so a future corrected-gold comparison of the two arms is **unpaired and must
say so**.

**THE COLLECTOR WRITES TEN KEYS, AND TWO LAUNCH SIGNALS ARE NOT AMONG THEM.** Views and reactions
are absent from a v1 post record and from a poll payload. The proven pattern is a retrospective
refetch like the 5a poll census — **$0**, sidecar v2 **beside** raw v1, never into the v1 stores.
5c3 inherits it.

## ⏭️ Next

**AFTER 2026-08-08 10:02 UTC, IN THIS ORDER — the whole sequence is wired and tested, ~63
resolves.** Everything below is offline-ready; the wall is the only thing missing.

0. **`--leave @katyal55 @tretyakovaele @kuksa2022`** — wave 3's three member exits, FIRST because
   they are the only actions that undo something already done. **3 resolves**, the flag re-read
   after each (D28: leaving is not proven by a request that did not raise).
1. `scripts/collect_5c1.py --join` — **7 left (List A), all authorised**; the six wave-3 exits
   dropped out of the authorised set by derivation, not by rewriting `joins_authorised`. The log
   is both cursor and pace. **7 resolves.** Only 3 of the 7 are measured UA (@sashafitnesslife,
   @denisovapro, @ya_Nenka); the other 4 are a title read, same as the exits were.
2. `scripts/entry_check.py --gate-5c1` — the 16 "Дозаявка №3" city rows; the existing rows keep
   their `ruling` and `replaced`. Then `scripts/apply_gate_rulings_5c1.py`: PASS → posts only,
   `comments_enabled: false`, no join. **16 resolves.** Expect registry 41 + up to 16.
3. `--posts --only <the passes>` then `--comments --only <the joined>`. `--only` narrows the LOOP,
   not the record. **16 + 15 resolves.** Both lists are DERIVED, never retyped: passes from the
   gate record (`bucket == "city" and verdict == "PASS"`), joined from `joins_5c1.jsonl`
   (`outcome in ("joined", "already_member")`, minus anything since left).
4. `shasum -c` 6/6, `run_loop.py --once --dry-run`, final Deliverable-2 report.
5. **"Дозаявка №5" — three national chains, wired 07.08 and queued BEHIND the four steps above**
   (operator: "after the phase-close queue"). `--gate-5c1 --only @forainfo @ekomarket_shop
   @tadaua` — the gate now takes `--only` for the same reason the collector does, and here it also
   keeps two batches' RULINGS apart: `final_bucket` refuses the whole apply run over one unruled
   FLAG, so a joint pass would hold these three hostage to a verdict about @LHVC_info. Bucket
   `late` → comments or posts by the group finding, `audience: retail_official`,
   `source_type: official_retail`. **3 resolves**, then `late_batch_5c1.py --search-retail` for
   the five chains the web pass missed (**10 searches, not resolves**; one note per chain, Novus
   and Auchan will come back "MATCHES FOUND, not closed" and need a written judgement), and
   `--search-food-quality` for the Consumer Union of Ukraine's counterfeit-dairy channel
   (addendum 9: **5 searches**, ONE note — one channel asked about under five names). If it is
   found, the gate runs and the registry write will STOP: the brief's segment «food_quality» is
   not in the closed list of eight and `food_quality_gov` means the STATE service. That is the
   operator's word, and both guards already refuse to guess it (D55).
6. **mothers-UA harvest (addendum 8 item 4, REQUIRED not optional)** — similar-channels from
   @ya_Nenka, @tarilka_malyuka, @blwbabies + @TGStat_Bot lookups → `results/harvest_mothers_ua.json`
   as a ledger for the operator's picks. Nothing enters from it without the gate. Resolve-budget
   aware, and on any FloodWait: stop and record. Note what the census actually says about the
   premise — the segment's emptying is predicted, not yet measured (see Blockers).

**`make check` WILL GO RED between steps 2 and 3, and that is the gate reporting.** A city row that
FAILs or FLAGs makes `final_bucket` raise — the STOP working — and it lands in
`AWAITING_A_RULING` (empty today) with its evidence. `checked == 52` and the bucket counts move
with the passes too. Read the red, do not loosen the assertion. Expected after clean passes:
registry **up to 57** (41 + 16), launch **up to 49** (33 + 16), watch 8.

**@LHVC_info will probably FLAG on its own merits** (0.2 posts/week, last post 2026-07-20 — a
window opened on 08.08 can hold zero of its posts, and it has a group → "watch shape").
@zinkivnews is next closest. Those go to the operator; they are findings, not bucket artifacts.

5. **5c2** — the loop core (a pod runner in place of `run_loop.ENDPOINT`, still `None`) + the
   ~4-week backlog window (one paid event) + SQLite aggregates, **keyed by `audience`**. The queue
   it prices is the WINDOW's comments, which do not exist yet.
6. **The chat-mining track is DEFERRED, not dropped** — @Mambabyua and @kulinariya_chat_a were
   excluded as supergroups whose "posts" are member chat. Build nothing for it.

## 🚧 Blockers

**ONE, AND IT IS A CLOCK: the account-wide FloodWait clears 2026-08-08 10:02 UTC.** Nothing
Telegram-side runs before then — joins, comment collection and any gate check all begin with
`ResolveUsernameRequest`, which is what was rate-limited. Not a fault to fix and not something to
work around: `scripts/collect_5c1.py` refuses until the time passes, and retrying inside the window
extends it. Everything offline is unaffected.

**WAVE 3 IS APPLIED: THE REGISTRY IS 41, AND THE LAUNCH MOTHERS SEGMENT IS EMPTY.**
56 → **41** = launch 33 (4 originals + 15 comment-capable + 14 posts-only) + watch 8, matching the
canon's table row for row. Fifteen exits with four reasons: 3 on the census (@retsepty5 ru 1.00 over
139 posts · @retsepty4 1.00/115 · @katyal55 1.00/36), **1 on market-origin evidence**
(@tretyakovaele — its one windowed post is «прилетели в Сочи, на Красную Поляну», a flight into the
RF; 244k subscribers and the only channel with collected comments, the costliest row in the
ruling), 5 RU-title TOO_FEW and 6 RU-title watch. Every removal left its line with its numbers;
`taxonomy:`/`watchlist:` byte-identical. Ledger: **−423,072 subscribers**, 852,254 remain — both
floors, the four originals carry no measured count anywhere. `audience.food_quality_gov` →
**`food_quality`** (wave-3 ruling; who runs it is `source_type`'s question). **mothers_kids: 0
launch, 1 watch (@itsmamix)** — the harvest is the only way back into the segment.

**THREE GROUP EXITS ARE QUEUED, NOT DONE.** @katyal55, @tretyakovaele and @kuksa2022 are out of the
registry, but leaving their groups is Telegram-side: `leave_group` starts with `get_entity`, which
IS the resolve the wall is on, so a leave fired today would lengthen the window instead of leaving
anything. `--leave` is now behind the same guard as `--join` (it was not), and the three go first
after 10:02 UTC — **3 resolves**, membership flag re-read after each.

**THE MARKET-ORIGIN SCREEN EXISTS AND CLOSES D45.** `scripts/market_screen_5c1.py` (SPEC §3.11
(4)): what you pay with, where you shop, where you are, what domain you link, and the RF
legal-regime disclaimers — never the alphabet. **Report-only**, it never removes a source. Over the
live 39: **UA_EVIDENCE 19 · NO_EVIDENCE 20 · RF_FLAG 0**, and the zero is readable only because the
controls fire: @offspringrus → RF_FLAG, @dpssgovua → UA_EVIDENCE, the «Сочи» and «₽/Яндекс Еды»
rows flag on their own text, and «щоб добре просочився» produces nothing. Two calls to know about:
the bare «РФ»/«Росія» is NOT a signal (a UA channel writes it about the war), and **NO_EVIDENCE is
half the registry** — twenty sources never quote a price or a shop, so a hard "REQUIRES UA
evidence" gate would exclude them for not being about shopping. Operator's call; the record names
it. Every hit carries its quoted line.

**ONE COMPOSITION DECISION IS WAITING ON THE OPERATOR AND NOTHING MOVES WITHOUT IT:** the census
list. Note both halves of what it cannot see — of tomorrow's 7 joins only 3 are measured UA
(@sashafitnesslife, @denisovapro, @ya_Nenka), the other 4 are a title read exactly like the 3 held.
 Three sources are RU_DOMINANT with their numbers and their own posts quoted in the record;
36 more carry no verdict and the two reasons are named separately. Two things the census CANNOT
do, so they are decisions and not tasks: it cannot support the exit of the three held joins
(4, 2 and 1 posts each — the hold itself is right and reversible), and it cannot see the watch
bucket at all, whose 14 zeros are the channels' own silence measured twice (the gate recorded
`posts_per_week: 0.0` and `last_post_at: null` for every one on 07.08). A posts pass over watch
would spend ~14 resolves to buy 14 zeros.

**NO OTHER COMPOSITION DECISION IS OUTSTANDING.** @uasaler is closed by the wave-2 ruling (out
entirely), wave 2 ratified the five theme removals and the @discountua1 reversal, and the Poltava
ledger's picks are made — "Дозаявка №3", 16 handles, waiting on the gate rather than on a person.
The next decision comes back only if a city feed FAILs or FLAGs, which is what the STOP is for.

**The external fault is still routed around rather than fixed:** no RunPod serverless endpoint on
this account reaches a job-consuming worker — proven not to be ours by **RunPod's own hub vLLM
worker** failing the same way, and proven not to be the artifact by the same code answering
correctly on a pod. Production is a stop-after pod; serverless can only return through a fresh
§3.11 (2) measurement.

**Recorded rather than open:** the CA-MTL-3 volume is **deleted** (07.08, proven by listing), so
its ~$0.24/day has stopped and the ~2026-09-05 review is closed. Arm A's per-row dump is
permanently lost. No pod, endpoint or template exists.

## ⚠️ Footguns for the next run

**A pod has no template, so it has no configuration — whatever boots it carries the worker's
environment.** `SERVING_CONFIG`, `ADAPTER_DIR`, `BASE_WEIGHTS` and `MODEL_REVISION` were the
serverless endpoint template's `--env`; the first pod start refused with `SERVING_CONFIG must be
one of ('A','B'), got ''`, for free, because `Worker` loads the model lazily and `settings()` runs
first. **5c2's pod runner inherits this** — the loop is what must pass them now.

**Read `runpodctl gpu list` before spending a create call, and remember what pins the datacenter.**
Availability is reported **per datacenter** by `gpu list`; `datacenter list` prints `""` for
everything and answers nothing — the difference cost 45 minutes and 31 refused `pod create` calls
at $0. Capacity is discrete per (datacenter × GPU class), and a **network volume pins the
datacenter** (in CA-MTL-3 only `ADA_24` ever allocated). SPEC §3.11 (1)'s capacity clause makes the
CLASS the contract: A6000 anywhere, A40 in-class with the card in provenance, **never A100**.

**`parent_msg_id` and `reply_to_msg_id` are different id spaces, and comparing them looks fine.**
`parent_msg_id` is the **channel** post; `reply_to_msg_id` is a message in the **discussion
group**. A top-level comment replies to the group's mirror of the post, a reply-to-a-commenter
replies to another comment — so `reply_to != parent` is true for essentially every row and would
report ~100% of comments as replies. The thread head is recoverable without a second field: it is
the **smallest** reply target in the thread, because the mirror exists before any comment on it.
Sanity gate: if the reply family comes out near the corpus size, the discriminator is wrong, not
the corpus. Measured 2026-08-03 on one real thread **before** the 1,538-thread walk.

**`results/sitting_45g2_manifest.json` no longer matches the batch it pins, and that is correct.**
4.5g5 wrote 35 adjudicated rows into `uplabel_precheck_45g2.jsonl` (`df688e59…` → `f436c419…`).
`build_sitting_pack.py` will refuse. **Do not re-pin the manifest** — it describes the corpus the
300 verdicts were passed on; `results/verdicts_45g5.json` is the only place the chain lives. Same
shape as `calib_45e_manifest.json` and `relabel_45e.json`.

**The batch is no longer pure model output.** 35 of the 1,912 rows carry
`annotator: sitting-45g-verdicts`. Any counter that says "the precheck said X" has to name which
rows it means, and any new gate over the batch has to decide whether adjudicated rows are in it.

**A size and a cost are different numbers, and only the cost decides.** The reply family is the
bigger one — 23 of 42 refusals against the sender family's 7 — and the more expensive by far: a
blanket rule over it flips 62 of 258 judged-correct rows against the sender family's 10 of 45.
Measure what a rule would break on the rows already accepted before deciding a feature is worth
buying.

**"N of the refusals are in family F" is co-occurrence and reads as explanation.** 23 refusals are
structurally replies; only **10** have a note that says the refusal was *about* the reply. The
other 13 are food-poll `taste` rulings and P5/P6 rows that happen to sit on replying rows. Before
a family size becomes an argument, check the notes: does the verdict name the feature?

**A family averaged over two members can hide that they behave oppositely.** The two hyperactive
pseudonyms cost 6-of-40 and 4-of-5 under the same rule, one is `official_retail` and the other an
`aggregator`, and one has 874 texted comments against the other's 73 in 3,761 rows. The pair's
"10 of 45" is arithmetic, not a description of either. Split before pricing.

**A prompt revision can only re-weigh evidence the model HAS.** v2.2 states the corporate-voice
ruling, and `UNCLEAR_RULE` had already listed it since v2 — the model reads it twice and still
answers `unclear: false` on 3 of the 4 P6 rows, because nothing in their text identifies a
retailer. The discriminator was one directory away the whole time (`sender_anon_id`, same
pseudonym on all four). Before rewording a rule the model keeps breaking, check whether the input
it would need to obey the rule is in the row at all.

**A pre-registration that is not committed is not a pre-registration.** `run_v22_probe.py` shells
out to `git ls-files` and `git diff HEAD` and refuses to spend against a plan that is untracked
**or modified** — tracked-but-edited is the case a shallow check misses. Both branches are tested
against a throwaway repo.

**A comparison row read off the wrong file looks like a perfect score.** The v2.1 baseline was
first computed from the plan's own source batch, which holds the labels the sitting judged: v2
against itself, reported as 58/58 for a prompt that scores 20. The smoke run caught it. Whenever
a record carries a "before" column, check which file it came from.

**A cost estimate must price what the run will BUY, not what it chooses from.** `rerun_failed_strata`
priced the whole 1,912-row scope against the remaining headroom and refused a 17-row resume that
would have cost $0.008. It now reads the resume file before the ledger block and prices `pending`.
`precheck_uplabel.py` still has the older shape — if a resume of it is ever refused, that is why.

**A history's `old` is whatever the reader of that history reverses to — not the value on disk.**
`measure_empty_drop.reversals` keeps the LAST fix per id, so a block recording the disk value
restores a later fix's answer and the population stops deriving. `merge_sitting_returns` writes
`old` (the re-labeller's answer) and `replaced` (what this run overwrote) as two fields. Anything
appending to `results/relabel_45e.json` has to do the same.

**Never `git add -A` here.** `docs/SPEC.md` and `docs/STATUS.md` are modified by the team lead
right now, and the next queued `docs/PROMPT-5c*.md` will land untracked without warning. Stage by
path. The same trap has fired with every queued prompt since `docs/PROMPT-4.5g4.md`.

- **Two taxonomies exist now, and the five-class one is still the one every number was measured
  over.** `scorer.INTENTS` (5) is what `run_baseline.py`, `train_xlmr_baseline.py` and
  `parse_reply("T1", ...)` use; `INTENTS_V2` (6) is what guideline v2, `T1v2` and the re-labeller
  use. **Never widen the five-member tuple** — it would change old label spaces in files nobody
  edited. And never add a prompt to `prompts.TASKS`: that tuple is the identity map
  `records.assert_prompt_sha` compares whole against every stored record.
- **Eight registered prompts now, and none of them may be edited in place.** 4.5g added
  `T1v2_with_post`, `relabel_intents_v2_with_post` and `precheck_v2_with_post` **beside** the four,
  which are pinned in `results/relabel_45e.json` / `relabel_probe_45d.json`; 4.5g2 added
  `caption_post`. A with-post variant is *derived* from its base at import through `_swap`, so
  editing the base silently moves the revision too — that is the point, and it is also why the
  derivation is asserted both ways in `tests/test_prompts.py`. Adding another **labelling** prompt
  means adding it to `PROMPTS`, `DELIMITERS`, `INTENTS_OF` **and** `COMMENT_FIELDS`; the
  registration test fails on any one of them missing. `caption_post` is in **none** of those three
  tables and is in `FREE_TEXT` instead — its answer is prose, so `build_messages` and `parse_reply`
  refuse it **by name** rather than crashing on a missing table entry.
- **A post reaches the model in one of four states, and one function decides which.**
  `parents.context(posts, captions, row)` returns `post_text` / `image_caption` / `poll_text` /
  `no_text_and_no_caption` **and** the text to render, so a run cannot ask half its rows with a
  description and half with `(this post has no text)` because two call sites disagreed — the counts
  land in the record and are checkable. `build_messages` refuses a caption beside a post that has
  text and beside a task that takes no post, the same both-directions guard `parent` already had.
  **A caption file that is not the one its record describes stops a run before the first request**:
  the failure it prevents is invisible downstream, since the prompt hash does not move.
- **A script that appends to a history and reads it back must tell its own writes apart.**
  `relabel_emptied.py` held rows by "a `fixes` block has moved this row" — right on the first run,
  and on the second it read back its own block and called 32 model answers operator rulings. It is
  narrowed by `applied_by` now. Anything else that grows a `fixes` list inherits the same trap.
- **`results/spend_45d.json` and `results/spend_45e.json` are anchors, not logs.** Same footgun as
  `results/spend_3b.json` and `results/spend_phase4.json`: delete or regenerate one and its counter
  silently restarts at today's lifetime usage. Each is written *before* the first request on
  purpose, and `relabel_intents.py --phase` refuses a ledger carrying another phase's anchor key.
  **The run entries do not sum to the phase spend** — `Budget.reconcile` can only push a number up,
  so a run whose predecessor had not yet posted absorbs its tail ($0.5778 of entries against
  $0.5448 measured from the anchor). The anchored difference is the spend; the sum is a bound.
- **The `_tax2` files are accepted now, but they are still not drop-in replacements.** The ≥90% gate
  passed, so the labels are validated — the row *counts* are not: `sarcasm_holdout_pool_tax2.jsonl`
  has 915 of 971 rows (54 frozen ids + 2 with no answer) and `comments_train_tax2.jsonl` 1,594 of
  1,600. A trainer pointed at them silently drops the 14 unreadable rows and the frozen ids. 4.5g
  moved 32 of their `intents` cells and did **not** change any count.
- **`read_calibration_returns.py` refuses to run, and that is correct.** It sha-pins the staged
  files against `results/calib_45e_manifest.json`, and the three 4.5f rulings moved them
  (`comments_train_tax2.jsonl` `d2132c1e…` → `e5a52a08…`). The gate was computed **before** the
  rulings and lives in `results/calib_45e_verdict.json`; the sealed manifest describes the corpus as
  it was sealed, and `fixes` in `results/relabel_45e.json` is the only place the chain to today's
  bytes is written down. Do not "fix" the refusal by re-pinning the manifest.
- **`uplabel_precheck_45g2.jsonl` is the live batch; `…_45g.jsonl` is its predecessor and both are
  committed MODEL output.** The gitignore exceptions are deliberate (paid output a gate decision
  reads), but neither file is annotation: every row carries `annotator: "llm-precheck"` and nothing
  may merge until all three strata of **`results/sitting_45g2_manifest.json`** come back ≥0.90. A
  stratum that misses sends back its **whole population** — 382 / 671 / 859 rows, not the 100
  judged. The 4.5g batch is kept byte-identical because the superseded manifest pins its sha; read
  the **g2** file for anything current.
- **`build_sitting_pack.py` now writes the 4.5g2 pack, and `--force` destroys an evening's
  verdicts** — the same footgun `build_audit_pack.py` and `build_micro_pack.py` carry, and the pack
  directory is gitignored, so there is no HEAD to restore from. `verdicts_present` in the manifest
  is what a rebuild measured, so a forced one says what it destroyed. The build also stops if the
  draw no longer matches the superseded manifest's `stratum_of`, or if `unreadable14.csv` no longer
  hashes to what `results/calib_45e_micro_manifest.json` pinned; the latter means the operator has
  started on it, and the answer is to say so in the manifest, never to re-pin.
- **A 4.5g2 script must never import `PHASE` / `CAP_USD` / `LEDGER` from `relabel_emptied`.**
  `precheck_uplabel.py` does exactly that on purpose — it *is* 4.5g and shares the $1.25 cap and the
  4.5g anchor. Copying that import into a later phase charges new work against a closed phase's
  budget and its anchor. Each phase declares its own three constants; `Asker` is fine to reuse.
- **Two gold versions exist now, so every number has to name one.** `data/frozen/*_v3.jsonl` sit
  beside the v2 files and **nothing reads them by default** — the gates, the bars,
  `eval_zero_shot.py` and `run_baseline.py` all still score against v2, which is what keeps Phase 4's
  verdict meaningful. v3 numbers live only in `results/rescores_v3.json` (`gold_version: "v3"`) and
  are **program measurements, never gate results**; they must never be appended to
  `results/baselines.json`. Scoring a *new* run against v3 is a gate decision nobody has taken.
- **`data/annotation/audit_45a/` now holds 244 verdicts and gitignored data has no HEAD to restore
  from.** `build_audit_pack.py --force` is the only path that overwrites a filled pack and it takes
  no snapshot — do not run it to "regenerate" anything. What can be re-run safely:
  `normalize_audit_returns.py` (no-ops once the pack matches `results/audit_45b_returns.json`) and
  `audit_ceiling.py` (reads only). The verdicts survive in the raw returns under
  `data/annotation/audit_45a_returned/`, sha-pinned in the normalizer and in that record; treat that
  directory as read-only.
- **Registry brand normalization does not fold Unicode homoglyphs.** A mention spelled with a
  Cyrillic `о` inside a Latin-script brand casefolds to a token the watchlist alias table misses,
  so two strings that render identically score as two different entities — one FP and one FN on
  G1e. Found on the 4.5a brands stratum (n=4, so at least a quarter of it). **The fix is deferred
  to the 4.5 follow-ups on purpose: a normalization change mid-audit would silently redefine future
  G1e numbers against past ones** — Phase 3, the own-pod anchor and both arms were all scored
  through today's `normalise_brand`. Do not "just fix" it; it is a re-scoring decision with a plan,
  and every old run can be re-scored from its dump at $0 (`implementation-notes.md`, Phase 4.5a).
- **The results record holds TWO rows under the gate id `G1d`** — post_type, which gates, and
  relevance, which amendment 3.3 reports beside it and never inside it. A dict keyed by gate id
  returns the relevance number and a bar that looks entirely plausible (0.9315 instead of 0.8984).
  `records.anchor_values` selects on the metric name and refuses anything but one match.
- **Gemma 4's chat template drops the thinking channel when you render a full assistant turn.**
  The generation prompt ends `<|turn>model\n<|channel>thought\n<channel|>`; the turn form ends
  `<|turn>model\n` and then the content. Build a training example from the turn form and the model
  is conditioned on a context no gate row carries — silent, and it only shows up as gates lower
  than the smoke suggested. Take the prompt from the eval call, the end-of-turn marker from the
  turn form.
- **A stopped pod with no network volume still bills its container disk.** 80 GB is about what the
  100 GB network volume costs per month. If the pod exists only for one session, **delete** it
  (`runpodctl pod delete` — there is no `pod terminate`), do not stop it.
- **Python buffers stdout when it is redirected to a file.** 15 minutes into the 4b smoke the log
  still held nothing after the model load. `loss.jsonl` is written open/write/close per line and is
  the live view; `python3 -u` fixes the log itself.
- **`results/spend_phase4.json` is the $25 cap's anchor and must not be regenerated.** It stores
  the RunPod balance as Phase 4 opened; delete it and the counter silently restarts at today's
  balance. The guard also refuses when the balance is *above* the anchor — a mid-phase top-up means
  the delta stopped measuring this phase, and re-anchoring is an operator decision.
- **A stopped pod is not a stopped bill.** The 100 GB network volume bills by the month with no pod
  attached. `runpodctl billing pods` cannot see it; only the account-balance delta can, which is why
  the guard reads both and takes the larger.
- **`runpodctl pod list` shows running pods only.** An empty list is "nothing running", not
  "nothing exists". Use `pod list -a` or `pod get <id>` to show a stopped pod's `EXITED` state.
- **Network volumes live in a different datacenter set than the A6000 does.** `EU-SE-1` had the
  best A6000 stock and takes no volumes at all; the intersection was `CA-MTL-3`. Pick on the
  intersection or pay for a second volume.
- **`RUNPOD_POD_ID` is not inherited over ssh** — export it in the run command or the record's
  `runtime.pod_id` is `None` and the number cannot name its machine.
- **The RunPod PyTorch image's python is PEP 668 managed.** `pip install` refuses; use
  `python3 -m venv --system-site-packages` so the image's CUDA-matched torch is reused rather than
  a 3 GB re-download of a possibly different build.
- **Batch 1 is PERMANENT, and "re-measure it" is no longer the answer.** Greedy decoding was
  measured non-invariant on bitsandbytes NF4 + A6000 on 2026-08-01 (one row of 24 flipped between
  batch 8 and batch 1); the authorised re-measurement ran 2026-08-06 and **failed** — the carve
  ladder called every N byte-identical, the paid run at 16 died on GPU memory with G1b at 16 of 108
  rows, and SPEC §3.11 (2) fixes serving at **batch 1 permanently**. Gate evals were always batch 1
  and stay so regardless. Only a NEW pre-registration may re-open it; the door in the code
  (`--batch-measurement`) refuses `--backend local` on purpose. [[5b2-batch-measurement]]
- **`add_special_tokens=False` is load-bearing and now asserted.** Gemma 4's chat template emits
  `<bos>` itself; a template revision that stopped would silently make every prompt worse, so
  `LocalClient` refuses to construct if the rendered prompt does not start with the BOS token.
- **Gemma 4 has a thinking channel.** `enable_thinking=False` + `add_generation_prompt=True` emits
  an already-closed `<|channel>thought\n<channel|>` — the local equivalent of 3b's
  `reasoning: {"enabled": false}`. It is the current default and is passed explicitly anyway: with
  thinking on, `parse_reply` would read the first brace inside the reasoning text.
- **A `--probe` is not a smoke test unless it prints rows.** Aggregate counts are identical whenever
  two configurations merely parse, so a check built on them cannot fail. The batch-invariance check
  diffs the per-row prediction lines and guards with `test -s` — two crashed probes produce two
  empty files, and `diff` on those is silent success.

- **`docs/STATUS.md`, `docs/SPEC.md`, `docs/PROMPT-*.md` are team-lead files.** Read and commit,
  never edit — the deny rules refuse `Edit` *and* `Write` on them, without a restart. Phase-end
  facts go to the daily log or `implementation-notes.md`. The refusal reads "File is in a directory
  that is denied", but the rules are file-scoped: the rest of `docs/` is still writable.
- **A ceiling lifted by the operator is not a ceiling lifted in code.** `train_xlmr_baseline.py`
  refuses to train above `--time-budget-min` and exits **3** — it prints a projection and leaves no
  process, which reads exactly like a crash. Grep your own guards before any unattended launch.
- **The six 3b zero-shot records carry no per-row predictions — never claim paired re-scoring from
  them.** They hold `scored_ids_sha256` (a hash of the id list) and error counts, nothing that can
  be re-scored. Dumps exist only from step 3c onward, and the six are **not** backfilled: they
  cannot be reconstructed and a synthesized dump would be worse than the gap.
- **A prediction dump must be sorted before it is hashed.** Rows come back from four workers; a
  digest in completion order is a hash of the scheduler, not of the data. And it carries ids and
  predicted labels **only** — no gold, no source text, or it becomes a second copy of a frozen file.
- **`results/spend_3b.json` is the $8 cap's anchor and must not be regenerated.** It stores the
  lifetime OpenRouter usage as of the first 3b request; delete it and the next run re-anchors at
  today's usage, silently resetting the phase counter to zero.
- **Never use `anthropic/claude-haiku-4.5:batch`** — served only through `/api/beta/batches`, 404s
  on `/chat/completions`. The runner refuses the slug on purpose.
- **The reference row is marked in the record, not just the filename.** `build_record` rewrites
  every `gate` field of a `--reference-only` run to `ref`, so a lookup for `G1d` cannot find it.
  Do not "fix" those entries back to gate ids.
- **A run that trips the cap writes no record** — a partial run must never become a gate anchor.
  Do not re-run with a bigger `--max-run-usd` to get the record.
- **`GET /api/v1/generation?id=` 404s for our generations** at every delay tried (2 s to 60 s).
  Spend reads `usage.cost` and reconciles against `/credits`; do not "restore" that path.
- **Endpoint health readings are point-in-time.** The pins were chosen on status/uptime as read at
  pin time; `deepinfra/fp8` was deranked then and healthy hours later. The precision *rule* is
  pre-registered; re-pinning a provider is legal — but say so if you do it.
- **`scripts/freeze_testsets.py --force` would rebuild the split and destroy v2.** A fresh draw
  differs from v2 by 8 rows. Do not run it. Likewise `mine_sarcasm_candidates.py --force`
  (746 hand labels) and `mine_sarcasm_holdout.py --force` (971); `refreeze_v2.py`,
  `sync_batch_v2.py` and `freeze_sarcasm_holdout.py` are one-shot.
- **`data/annotation/sarcasm_holdout_pool.jsonl` is not training data** — its non-sarcastic rows
  share threads with the holdout.
- **Never merge `synthetic_sarcasm.jsonl` into a real-source file.** The Phase-4 ablation has to
  drop it by dropping one path. `data/annotation/*` is gitignored, so the file survives only
  through an explicit `!` exception — do not "tidy" that line away.
- **The generated rows passed QA but carry no QA number, and that is not an oversight.** ≥80% `ok`
  was pre-registered before the 50-row draw; the operator ruled it passed without returning the
  marked-up CSV. The executor never scores its own sample (SPEC §10), so the empty
  `operator_verdict` column stays empty. The ADR is the authority on the verdict.
- **The freeze shrank `sarcasm_candidates.pristine.jsonl` 800 → 746** so the validator would not
  read the moved rows as lost. Legitimate once, audited — but the validator can be silenced the
  same way again. Any further row loss must be diffed against the baseline before it is believed.
- **`results/baselines.json` is append-only and never hand-edited.** Numbers reach it only through
  the scorer; `scripts/show_results.py` only reads. A hand-typed number there is invisible.
- **A results record cannot name the commit that contains it**, so provenance is `commit` + the
  `dirty` paths at run time; the runner shouts if any is under `src/`, `scripts/` or `config/`.
- sklearn lives in the `baseline` extra and torch/transformers in `xlmr` — no test may import
  either, or `make check` stops being runnable on a bare checkout.
- `RAW_STORE_SALT` in `.env` must never be rotated: a new salt orphans every `sender_anon_id`.
- `packaging` has 19 rows in the test set — G1c is thin by construction, not by accident.
- **Do not merge a QLoRA adapter into bf16 base weights without measuring it (Phase 5).** An
  adapter trained against a 4-bit NF4 base learned to compensate THAT base's quantization error;
  merged into unquantized weights it corrects errors that are no longer there. Second-order but
  measurable — so measure it: score the final artefact in the EXACT configuration that will serve
  production. Safe default: serve the same 4-bit base plus the adapter, unmerged.
- **XLM-R cannot do G1e** without a token-classification head. An empty G1e cell means "not
  attempted", never "scored zero" — the two must never be conflated in a comparison table.

- **A print statement can crash a run after the record is written.** The G1b-slice line at the end
  of `eval_zero_shot.main` was guarded by `anchor_valid` alone; on a fine-tuned arm `slice_ids` is
  `None`. It would have raised at the end of a 45-minute eval following a 3.4 h training run. Drive
  `main` through `--record-out` with a stub: `--smoke` returns before the record is built and
  `--probe` before it is written, so neither exercises that path.
- **`planned` is not `steps`.** `ceil(rows / (micro × accum)) × epochs` over-counts by one step per
  epoch whenever the epoch's micro-batches do not divide by the accumulation, and those leftovers'
  gradients are never zeroed — they fold into the next epoch's first step. 272 planned, 270 run.
- **Two runs of the same arm at the same seed give different losses** (0.18010 vs 0.18051 at step 5,
  same pod, same data, same config). Never write "identical" about two runs on this stack.
- **A test fixture that copies the real results file will collide with reality.** `test_gate_verdict`
  adds two fixture arms to the committed history; once the real arms existed that was two rows per
  arm and the suite failed on its own setup. It now strips records carrying `config.fine_tune`.

## 🐞 Known harness bug

Fixed 2026-07-28: `knowledge/templates/daily-log.md` now carries `{{DATE}}`, the placeholder
`scripts/brain-session-end.py` actually substitutes; `tests/test_templates.py` keeps the pair
honest.
