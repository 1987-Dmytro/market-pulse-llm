<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-08-08 19:22:30 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
6388229 fix(srv-2a): the pass formula was borrowing an A6000's seconds per row
f798053 feat(srv-2a): the worker is a serverless config already, minus the peft it could not name
2d2a8e8 docs(5c1): the /save checkpoint -- the pilot's numbers and the private-label correction
74a5adb docs(srv-2): the serverless wall came down and the runtime target moved back
6b15ebf docs(5c1): the pilot billed twice the projected rate — both numbers, both reasons
```

## 📋 Recent decisions

- `5c1-relevance-floor-and-discovery.md` — 5c1 — the relevance floor: 66 channels were admitted without anyone measuring the category
- `INDEX.md` — Decision records
- `5c1-day2-composition-and-search.md` — 5c1 day 2 — three "city feeds" were chats, and the search for replacements outperformed the scan

## 📅 Recent daily logs

- `2026-08-08.md`
- `2026-08-07.md`
- `2026-08-06.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->

# Hot Cache — curated

**Last update:** 2026-08-08 19:16 (`/save`). `docs/PROMPT-srv-2a.md` executed — **$0, no
`runpodctl` call, nothing created**: the pending team-lead tail committed unedited, the 5b worker
verified as a serverless config, the volume plan and `scripts/runbook_srv2b.md` written, 13 tests
added. `make check` **1,270 passed** (1,257 → 1,270). Four commits (`74a5adb` → `6388229`).
Earlier the same evening: the caption pilot, all five steps, **$0.0180 of its $0.10 cap**. The
yield half is [[5c1-relevance-floor-and-discovery]]; the day-2 half is
[[5c1-day2-composition-and-search]]. This block is hand-edited; the section above it is
auto-generated — do NOT touch the marker.

## 🔥 What's Hot

**THE SERVERLESS WALL IS DOWN AND THE RUNTIME TARGET MOVED BACK (SPEC 3.14).** A team-lead probe
in the operator's own console, the same evening: `runpod/mock-worker:dev` on endpoint
`8mkl2lbxho3bfa`, queue mode, 16 GB flex, no volume, no DC pin — **two jobs consumed and
COMPLETED** (delay 10 964 / 6 800 ms, execution 142/144 ms), deleted the moment it had answered,
deletion proven by a zero-endpoint listing. The 5b blocker did not reproduce and the vendor ticket
was closed unfiled. `results/parity_verdict_5b.json` stands **untouched** as the honest record of
2026-08-06. Pods remain the measured fallback; serverless is the target again, and **all paid 5c1
steps are HELD by the operator's word until srv-2 proves out.** The probe pre-registers what it
did NOT prove: the volume-attached GPU offering (D7 re-read), NF4 fit and batch-1 byte-stability
on whatever card is offered, and cost per row against the pod's $0.5993/1000.

**srv-2a IS DONE AND THE WORKER WAS ALREADY A SERVERLESS CONFIG — MINUS THE peft IT COULD NOT
NAME.** No `/workspace` is baked into `serve_handler.py` or `start_5b_worker.sh`; the template env
and `settings()` agree field for field; `runpod.serverless.start` with a callable handler is
proven on the pod (06.08, the three-row T2 batch), not assumed. The one thing verification
demanded: **config A is `peft` applying a LoRA to an NF4 base and no record named the peft that
served.** `RUNTIME_LIBRARIES` cannot grow — the 4.5h2 anchor carries three libraries and a fourth
entry would be a guard that never fires — so `library_versions()` now **reports** peft, accelerate
and runpod inside the `runtime` block, where widening breaks no schema. The pin is **0.20.0**,
read from the adapter's own `adapter_config.json`, i.e. from **inside the directory whose sha256
`b3ca6308…` the guard already checks**; `runbook_5b2.md`'s `peft==0.18.0` is corrected in the open
and that runbook is left unedited.

**THE srv-2b COST ARITHMETIC IS PRE-REGISTERED AND ITS PRIOR IS WEAK ON PURPOSE.** The pod side is
committed: **$0.4611 per 758-row pass**, $0.5993/1000 rows, 4.071 s/row, cold start 46.2 s off
local NVMe vs **278.9 s off a network volume**. The serverless side is
`(measured_cold_start + 758 × measured_s_per_row) × measured_usd_per_second` — **the run's own
numbers, not the pod's.** Filling it with what exists today (A6000 seconds, the probe's
$0.00016/s on a 16 GB class) gives $0.538 a pass, 17% dearer, $0.045 of it the boot alone — but
all three inputs come off hardware this endpoint will probably not run on, and at 3.0 s/row on a
4090 serverless wins instead. Quoted as a prior, never as a finding.

**THE FAILED CONTROL WAS ABOUT MODALITY, AND READING THE IMAGES ANSWERS IT: ATB GOES 0 → 13.**
Same window, same matcher, same lexicon, same pre-registered bar (`1aa89818…`, unmoved) — the only
thing added is a caption for each silent post. `results/caption_rematch_5c1.json`: **before 0 of 25
relevant, bar A FAIL** (re-derived here as a control, and it reproduces the signed screen exactly)
→ **after 13 of 25, bar A PASS**. It survives brand ablation: strike every brand alias, including
ATB's own «Своя Лінія» (12 of the 13 hits), and **10 posts still carry dairy or ice-cream**;
`bar_A_sole_carriers` is **empty** — the pass hangs on no single term. Five captioned posts are
honest misses: the «7 ДНІВ» leaflets sell bags, toys and a metal glider, and the matcher fires on
nothing. **RULED on acceptance: a private label IS a full brand hit**, not the executor's «miss of
the second kind» — a chain's own label inside its own channel is the most valuable class of hit
there is, so v2 carries a `private_label` flag from the registry and counts those hits in full;
the ablation is a side metric that demotes nothing. This does NOT lift `verdicts_reportable:
false` on the yield screen — that is screen v2's job.

**THE BLINDNESS IS 2.8% OF THE CORPUS AND IT IS NOT EVENLY SPREAD.** `results/image_census_5c1.json`
over 66 channels and 9,343 windowed posts, counted by `parents.context` state: **261 unreadable
today**, 250 of them carrying media, 11 carrying nothing at all. By segment — supermarket_deals
**22.6%** · health_fitness **16.2%** · retail_official **14.9%** against regional **0.5%**. The two
segments the screen just failed on content are the two that publish in pictures. Worst rows:
@atb_aktsiyi 46 of 53 · @VARUS_channel 32 of 135 · @matusi_ukr 23 · @educationwithloven 22 ·
@atb_market_official 19 of 25. Every channel's split is reconciled against the signed screen and a
mismatch stops the run.

**THE PILOT BILLED TWICE THE PROJECTED RATE, AND BOTH NUMBERS ARE THE OPERATOR'S TO READ.** The
census had to project at 4.5g2's $0.000483/post — the brief said so and the file was committed
before a cent was spent, which is what makes it a projection. The pilot then billed **$0.000948
per post asked** ($0.001001 per usable caption), 1.96×, and album size does not explain it (5.37
images/post against 4.5g2's 5.33). One full pass over the 250 captionable posts: **$0.12 upper /
$0.06 discounted at the projected rate, $0.24 / $0.12 at the measured one**; the **232 still
uncaptioned** (the 18 are bought, 4350 is billed-and-unusable) are $0.22 / $0.11. The 0.512
discount is 4.5g2's photo/poll/unreadable split — this pilot's own population came out **19 photos
of 19**, so a retail-leaflet run sits nearer the upper bound.

**66 SOURCES: BAR A 29 · BAR B 8 · BELOW BOTH 36 — BUT ONLY 24 OF THOSE ARE A CONTENT FINDING.**
Twelve rows could not be graded at all: nine have **0 posts in the window** and three have fewer
readable posts than the bar is high, so they fail bar A by arithmetic. Seven of the twelve are the
ENTIRE `watch` bucket, already ruled onto a waiting list for that same silence — re-failing them
would re-decide a decision on evidence that measures nothing. `summary.below_both_gradeable` (24)
is the list to act from; `below_both_not_gradeable` (12) says why each one is not on it.
Gradeable-empty by segment: health_fitness **7 of 17** · regional 8 of 17 · baby_food 4 of 8 ·
supermarket_deals 3 of 4 · mothers_kids 1 of 5 · retail_official 1 of 7 · cooking_recipes **0 of
7**. Nothing entered or left on this: removal is an operator ruling, never automatic.

**«ВАРТО» OUTFIRES EVERY REAL BRAND.** It is АТБ's private label AND the ordinary Ukrainian word
for "it is worth": **89 posts across 24 channels**, more than any other brand on the list.
«Президент» is 33 posts, mostly Zelensky; «масл» + the lexicon's `ов` ending is the justice
minister Маслов. Nothing was patched — the lexicon says `draft-not-law` and the watchlist is the
operator's — but every count now breaks down to the term that made it with one quoted line, and
each row carries `bar_A_sole_carriers`: **@polyakova_fitness clears bar A on «варто» alone,
@myrhorodtown on «Президент» alone.** The pass list of 29 must not be read as 29 channels that
carry the category.

**THE REGISTRY IS 66 = launch 59 + watch 7**, @dikankaa excluded on the acceptance (ru 1.00 over
20 decidable posts). Still **PROVISIONAL pending the operator's signature** — amendment 3.12's
rider: the failed control has been ruled on, and the signature now waits on screen v2. Excluded
across the phase: **34**. Audience: regional 17 · health_fitness 17 · baby_food 8 · retail_official 7 ·
cooking_recipes 7 · mothers_kids 5 · supermarket_deals 4 · food_quality 1. **mothers_kids stopped
being an empty launch segment** — 3 live (@educationwithloven, @matusi_ukr, @mamo_nepsichuy)
against 0 yesterday, which is what the whole harvest track existed for. Subscribers **+924,347**
over the 63 sources `results/entry_gate_5c1.json` measured (849,230 → 1,773,577); the four
originals add ~178,274 more but that number is the canon's table, not an artifact.

**THREE "CITY FEEDS" WERE CHATS, AND THE FIX WAS BIGGER THAN THE HOLE.** @poltava_misto,
@kremenchug_live and @Karlivka_live came back `broadcast=false, megagroup=true` — their 111/77/197
posts a week is member traffic, the class @Mambabyua was excluded for on 06.08. @Karlivka_live's
LINKED object turned out to be a broadcast channel of the same town (@KarlivkaLive), so the canon
had taken the chat's handle; and the operator's own addition to step 7 — search for broadcast
analogues of the two remaining towns — returned feeds LARGER than what left: @h_kremenchug 137,221
against a 16,056 chat. **Three of the four picks were not in the 119-candidate town-name scan at
all.** Name-scanning under-covers; `contacts.SearchRequest` over the same words did not.

**FIVE FLAGS WERE CLEARED, NOT OVERRIDDEN, AND THE ROWS STILL SAY FLAG.** Each was raised about a
discussion group on a channel that enters posts-only and never joins one. `CLEARED` covers a FLAG
and refuses a FAIL — a FAIL is a bucket change (`MOVED`), which is how @lab_of_childhood went to
watch: 0 posts in the window failed it, 49 posts to 2026-06-04 is why it is not dead.

**THE SCREENS NOW REFUSE THEIR OWN DEFAULT PATH.** `language_census_5c1.json` IS wave 3's evidence
— @retsepty5's 139 posts, @katyal55's 36 — and those channels have LEFT, so a re-run writes a
table that cannot contain the rows the rulings cite. Same for the market screen's «RF 0 on the
live 39». Today's passes are `results/language_census_5c1_day2.json` (UA_DOMINANT 43 ·
TOO_FEW 16 · NO_POSTS 7 · **RU_DOMINANT 1**) and `results/market_screen_5c1_day2.json`
(UA_EVIDENCE 40 · NO_EVIDENCE 24 · **RF_FLAG 3**). Both report-only, all seven controls fire.

**THE MARKET SCREEN'S FIRST FALSE POSITIVES ARE WAR REPORTING.** All three RF_FLAGs are Ukrainian
city feeds on the same sentence: «склади Wildberries розбомбили під Санкт-Петербургом»
(@myrhorodtown 2 of 273), «пожежі на складах Wildberries» (@poltava_informue 1 of 1,316),
«Українські БПЛА рознесли … хабів … Wildberries в Електросталі» (@poltava20 1 of 1,535). The
ratio reads the row — 947 UA-evidence posts against one mention. There is no stop-word fix:
*Wildberries* IS an RF retailer and naming it IS what the screen is for.

**THE WINDOW IS 9,393 POSTS AND 4,880 COMMENTS NOW, AND THE QUEUE 5c2 PRICES IS 16,218 ROWS.**
0 damaged lines, `shasum -c` 6/6, 0 threads left to fetch. The two channels step 7's handle top-up
found are the biggest comment sources in the composition: **@matusi_ukr 2,890 comments over 156
threads** and @mandziak 1,048 over 104 — between them 81% of everything the window collected.
The queue is 11,338 of 5a's v1 backlog plus these 4,880; `results/collect_5c1.json` carries the
per-channel table and `run_loop.py --once --dry-run` renders the total.

**AND THE TWO SCREENS DISAGREED ABOUT @dikankaa, BOTH RIGHT.** Census: RU_DOMINANT, ru 1.00 over 20
decidable posts, its own text covering «Волгоградской области ( Энгельс, Саратов )». Market screen:
NO_EVIDENCE — those oblasts are not in a table of places a MARKET is in. Neither instrument
subsumes the other. RULED on the acceptance: EXCLUDED on the census, and the removal comment says
which half of the operator's reason this repo holds an artifact for — the description is not in
one, because the gate stores a title and never a bio.

## ⏭️ Next

**srv-2a IS ACCEPTED — the team lead re-ran the suite (1,270 in 32.8 s) and verified the tail was
committed unedited.** Two notes came back with it. The **step reordering is credited as an
improvement**: the D7 re-read now happens **BEFORE the volume is created**, so the volume lands in
a datacenter that actually has the GPU — 5b did it the other way round, which is exactly how the
volume ended up pinning CA-MTL-3 where no 48 GB class allocated. And **Dv3 caught a team-lead
error**: the contract cited its smoke from prose rather than from an artifact, and those three T2
rows exist in no file. Ten deviations against a norm of 0–4, charged to an overloaded contract.

**NEXT IS srv-2b, AND ITS CAP IS SET AT ITS OWN BRIEFING — NOT HERE.**
`scripts/runbook_srv2b.md` is written and unexecuted: create the volume → stage → endpoint
(queue mode, max workers 1, scale-to-zero **confirmed in the console**, 48 GB class first if
offered with a volume, else 24 GB) → smoke on the hash-pinned 8-row carve → record the **D7
re-read** → **parity, 758 rows, batch 1**, against `results/parity_5b_a.json` under the rule of
3.11 (2): every 4.5h2-passed gate stays passing, no head drops > 0.005. Its own spend anchor,
`results/spend_srv2b.json`. The abort ladder is written down: no GPU with the volume · OOM ·
gate drop · over cap → STOP and report, no retry without a new briefing. **The 24 GB fit is
unproven** — the model sits at ~20 GiB at rest and no record carries a peak-VRAM figure for
batch-1 inference, so OOM is a named rung, not an assumption.

**THE CAPTION PROGRAM WAS RE-ROUTED BEFORE IT SPENT ANYTHING (SPEC 3.13).**
`docs/PROMPT-5c1-captions-full.md` is **VOID, never executed** — its $0.35 OpenRouter cap was
never touched, and it is kept only as provenance of the authorisation it recorded. Captions move
to the project's own **Gemma-4 vision path**: NF4 base at the pinned revision, **adapter OFF**,
greedy, batch 1, its own registered prompt with a new sha before any result, and a
`caption_source` field (`qwen-4.5g2` | `gm4-nf4-base`) so numbers from two caption instruments
are never compared silently. `docs/PROMPT-5c1-vis-a.md` is **ON HOLD** and will be re-issued
against the proven runtime after srv-2b parity — the runner must target the endpoint, not a pod
session. The 19 qwen captions already bought stay bought and become the bridge table's control.

**THE LAUNCH SIGNATURE IS STILL FROZEN — it is the operator's, next session, on the v2 numbers.**
`results/yield_screen_5c1.json` still reads `verdicts_reportable: false` and **the pilot does not
lift it** — lifting it is screen v2's job, and every registry action waits behind it.
The operator's v1 readings stand: a text-only screen is systematically blind to image-first
segments, so nothing is cut from those on v1 numbers; the two rows that held bar A on noise
(@polyakova_fitness on «варто», @myrhorodtown on «Президент») **count as BELOW bar A** and now
carry that ruling in the record itself (`--close`, `summary.pass_A_ruled_below_bar_A`); matcher
guards for «Варто»/«Президент» are deferred to the 5c3 lexicon session.

**The discovery session is still a separate future contract** (amendment 3.12 (2)), priced and
unspent: Premium €5.99/mo ALREADY active on the collector account, **10 free full-text queries a
day**, 10 Stars ≈ €0.20 beyond it — a brand-lexicon pass (~20–25 queries, +3 for the new brands) is
$0 over two to three days or ~€2–3 in one. TGStat is out (RF service); Telemetr.io free is the
fallback.

## 🚧 Blockers

**None.** The 2026-08-07 wall cleared at 10:02:05 UTC and today's ~100 resolves drew no new one —
because every collection run was scoped with `--only`. That is the discipline, not luck:
`collectable()` returns the whole registry and a bare `--posts` over 66 sources is sixty-six
`ResolveUsernameRequest`s for the work of six.

**$0.0180 spent today, all of it on the caption pilot, and the account is idle again.** The yield
session touched Telegram zero times (step 5's one authorised resolve was never needed —
@KarlivkaLive had been gated on day 2 at 10:48, so the brief's «66 → 67» was one step behind the
registry). The pilot's fetch brought the account back for 19 posts and 159 images and drew **no
FloodWait**; raw v1 is byte-identical before and after, `shasum -c results/raw_v1_baseline.sha256`
6/6. The money sits on the pilot's OWN anchor, `results/spend_5c1_captions.json` — $0.0180 against
its $0.10 cap, and 4.5g2's $0.75 balance was never touched.

**Recorded rather than open:** the CA-MTL-3 volume is deleted, so its **~$0.24/day** idle billing
has stopped — that literal is load-bearing, not decoration: `scripts/volume_calc_5c1.py` greps it
out of THIS file as a priced input, and a rewrite that drops it reddens nine tests. The account is
**empty**: no pod, no endpoint, no template, no volume, and srv-2a created none — which is what
makes the same three listings at the end of srv-2b a deletion proof rather than a hope. Arm A's
per-row dump is permanently lost.

**SUPERSEDED, kept so the old line is not re-read as current:** "no serverless endpoint on this
account reaches a job-consuming worker" was true on **2026-08-06** and is the honest content of
`results/parity_verdict_5b.json`. The probe of **2026-08-08** overturned it (SPEC 3.14) — but on
`n=2`, one evening, **no volume attached**. "The wall is down today" is not "it can never return",
and the volume is exactly the variable the probe left out. Production stays a stop-after pod until
srv-2b's parity says otherwise.

## ⚠️ Footguns for the next run

**`assert_runtime_matches` pins three libraries and cannot be taught a fourth.** It walks
`serving.RUNTIME_LIBRARIES` and **skips any library the anchor does not carry** — and the anchor
is `results/verdict_45h2.json`, frozen. So adding `peft` to that tuple would compile, pass every
test, and never fire once. peft is what applies the LoRA in config A, i.e. it moves tokens: the
pin lives in `scripts/runbook_srv2b.md` (**0.20.0**, from the adapter's own `adapter_config.json`)
and the version is merely REPORTED by `serve_handler.library_versions()`. Read the staged version
out of the run's record; do not expect a refusal.

**`relabel.read_ledger` writes a provenance string that is wrong for anything past phase 4.** Its
note renders `f"docs/PROMPT-{phase[0]}.{phase[1:]}.md"` — fine for `45g2`, and for any 5c1 phase
name it produces `docs/PROMPT-5.c1captions.md`, a path that does not exist, INSIDE a money record.
`scripts/caption_atb_5c1.py` writes its own three-key anchor instead. Copy that, not the helper.

**A caption's price is not stable across phases: 4.5g2 measured $0.000483/post, this pilot paid
$0.000948.** Same model, same pinned endpoint, same prompt, same ~5.35 images per request — the
rate still doubled. Any projection quoted from an old record is an estimate with a factor-of-two
error bar; say so, and reprice from the most recent run that actually paid.

**Two Telethon clients must never share `marketpulse.session`, and the join pace makes that easy
to forget.** `seconds_until_next_join` reads the LAST timestamp in `results/joins_5c1.jsonl`, so
the fifteen-minute gap is wall-clock and survives a restart — which means `--join --max 1` can be
fired between other phases at no cost, and a `--join` left running in the background while a gate
or a collection runs puts two clients on one SQLite file. Interleave, never overlap.

**A bare `--posts` or `--comments` resolves the WHOLE registry.** `collectable()` returns all 67
sources and `run()` calls `get_entity(handle)` before it checks `comments_enabled and not watch`
— so `--comments` without `--only` is sixty-seven `ResolveUsernameRequest`s to fetch five
channels' threads. That request is what the 2026-08-07 wall was on. Every collection run of the
day-2 order carried `--only` and the day drew no wall on ~100 resolves.

**`language_census_5c1.py` and `market_screen_5c1.py` now refuse their own default path.** Their
shipped records are dated measurements a ruling cites — the census holds @retsepty5's 139 posts
and @katyal55's 36, and those channels have LEFT the registry, so a re-run cannot contain them.
Pass `--out` with a new path; the day-2 passes are the `_day2.json` pair. `theme_screen_5c1.py`
carried this refusal already, for a harder reason.

**`apply_gate_rulings_5c1.remove_sources` stamps `removed 2026-08-07` from a hardcoded literal.**
No removal happened on 08.08 so nothing is mislabelled yet, and a test pins the string — but the
next channel that leaves the registry gets yesterday's date on its tombstone. Left as found: it is
a two-line change plus a test, and it was not this order's scope.

**The harvest's «already ours» marker does not know the canon's «Исключены — 12» table.**
`late_batch_5c1.known_handles()` reads the registry and the 5c1 gate record only, so
`results/harvest_mothers_ua.json` offers back @prikorm_kids_menu — dead by the 06.08 ruling and
never gated. The cost is an operator's attention at a sitting.


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
