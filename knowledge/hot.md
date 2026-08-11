<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-08-11 12:00:39 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
1c3ecc9 docs(status): the team lead's 10.08 handover block, verbatim
115a4db fix(sku-a): five tests had a shelf life -- the operator's first tick reddened them
e40c58e chore(vault): the sku-a tail
0fcc002 feat(sku-a): the three bars pre-registered, before sku-b exists
330e995 feat(sku-a): the two ground-truth packs, and what the leaflet gold cannot do
```

## 📋 Recent decisions

- `sitting-2026-08-10-composition-signed.md` — The 2026-08-10 sitting: «Варто» loses text matching, «Селянське» needs an anchor, the 141 names wait for the position layer, and the composition is signed
- `opus-review-programme-close.md` — The Opus review programme closes: the matcher is acquitted on 498 rows, and every miss prices the captions
- `INDEX.md` — Decision records

## 📅 Recent daily logs

- `2026-08-11.md`
- `2026-08-10.md`
- `2026-08-09.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->

# Hot Cache — curated

**Last update:** 2026-08-10 18:17 (`/save`, sku-a delivered). **THE COMPOSITION IS SIGNED
(66 = launch 59 + watch 7) AND THE POSITION LAYER'S WHOLE $0 HALF IS BUILT.** SPEC 3.17: schema +
tier ladder, two registered prompts, the deterministic pre-filter and its 769-row census, both
ground-truth packs, and sku-b's three bars pre-registered. The Opus audit closed before it — 25/25
packs, 498/498 rows — and its findings now live in two ADRs instead of here. **sku-a IS ACCEPTED and R1–R5 are
RATIFIED (operator, 10.08, quiz passed). Next: the operator ticks the 30-row pack (~45–60 min), THEN
sku-b — one paid attempt, cap $0.35.** This block is hand-edited; the section above it is auto-generated —
do NOT touch the marker. Long form: `implementation-notes.md` (Dv100–Dv111), and the days' logs
[[2026-08-10]] /
[[2026-08-09]]. ADRs: [[opus-review-programme-close]] · [[sitting-2026-08-10-composition-signed]] ·
[[5c1-vis-b-caption-instrument]] · [[srv2-program-close]] · [[5c1-relevance-floor-and-discovery]] ·
[[5c1-day2-composition-and-search]].


## 🔥 What's Hot

**THE FIVE RATIFIED READINGS ARE HOW EVERY sku-b NUMBER IS COMPUTED, AND THEIR HOME IS
`results/sku_pilot_prereg.json` — NOT SPEC.** All five were the executor's readings of denominators
SPEC does not state, and all five were ratified 10.08: **R1** recall per POST over the union of a
post's page answers, macro-averaged over the 15 posts with a non-empty gold set (the bar says "per
page"; the audit gold cannot be split that way). **R2** the page set is the **108 SENT** pages, not
the 159 available. **R3** four empty-gold posts are a precision probe, not recall. **R4** bar 2
scores at n ≥ 10 pairs. **R5** bar 3 excludes and counts unreadable replies, n ≥ 20, carriers pooled.
Thresholds, the $0.35 cap and "one attempt" never moved. Read them from
`ratification_required` in that file — SPEC 3.17 (7) lands in sku-b's step 0, because
`test_every_pinned_input_still_hashes_to_what_it_says` pins the live SPEC byte-for-byte and the
amendment needs the pin test to evolve in the same green commit (the Dv100 manoeuvre).

**THE PRE-FILTER'S FRAME IS MOSTLY RECIPES, AND THAT IS THE RULE WORKING AS WRITTEN.** 769 rows:
posts 717 of 14,388 texted (4.98%), comments 52 of 10,875 (0.48%). The top channels after @silposilpo
are recipe feeds firing on «сир» beside an ingredient quantity — «Твердий сир - 120 г» is a category
term next to a real size and is not an offer. The only deterministic separator is in the record:
`passed_carrying` = currency 226 · percent 384 · size 478 of the 717 posts. **The 30-row pack prices
it properly** — a drawn row adjudicated as naming no position is a pre-filter false positive, and
that reading is pre-registered rather than invented afterwards. Comments are 6.8% of the frame, so
bar 3 prices the POST leg; a comment bar of its own would be a team-lead ruling.

**THE SIGNATURE STAMP MOVED `config/registry.yaml`'s SHA, AND FIVE SEALED RECORDS PIN THE OLD BYTES.**
`validate_opus_returns.py` and `read_opus_audit.py` now REFUSE to run — correctly, the same way
`read_calibration_returns.py` does. **Do not re-pin any manifest.** To re-derive
`results/opus_audit_5c1.json`, check the registry out at `d832477` first;
`tests/test_registry.py::registry_without_the_signature_stamp` strips the block and reproduces the
signed bytes `c82d0cff…`, and that reconstruction is the only chain between the two.

**THE AUDIT'S NUMBERS NOW LIVE IN AN ADR, NOT HERE.** [[opus-review-programme-close]]: 25/25 packs,
498/498 rows, `fn_matcher` **0** with all 102 misses image-only — so `recall_candidate` 0.4769 is a
number about the CAPTIONS and must never be quoted as the matcher's; captions 117/43/3 (0.7178);
93 of 104 FP are «варто» + «Президент»; 141 names outside the watchlist. Two things that ADR adds
and the old blocks here did not have: the strata's FN columns **do not sum** to the total (230 vs
102 — an item carries every stratum it belongs to), and GM4 wrote «Three Bears» for Три Ведмеді on
two rows, so the caption was right and the **Cyrillic-only alias table** missed — a 5c3 gap, not a
captioner one. The sitting's rulings are in [[sitting-2026-08-10-composition-signed]]: «Варто»
text-matching OFF, «Селянське» anchored-only, the 141 names deferred into the position layer. Both
are 5c3's NAMED revision and **neither is applied in sku-a** — brand resolution here is the plain
alias table.

**OPERATIONAL, AND IT WILL RECUR: THE HARNESS KILLS LONG BACKGROUND WORK.** A 2.7 h driver launched
with Bash `run_in_background` was stopped from outside at 36 minutes; the process watcher armed the
same way at ~30. Nothing was lost only because the driver skips any pack whose returns file exists.
Launch anything past half an hour with `nohup … & disown`, and watch the **process**
(`while pgrep -f "[r]un_x.sh" …` — the bracket stops `pgrep` matching the watcher itself), not a
`tail -f`, which is silent through a dead process exactly as it is through a quiet one. Second stop
of the run: pack_08 named Opus on line 3 instead of line 1. **Operator's ruling: rows accepted,
gate left strict** — a gate loosened to keep a run moving is the gate the next surprise walks
through. Further occurrences stop the driver and get ruled one at a time.

**A `Write(path)` PERMISSION RULE IS NOT A RULE, AND AN ALLOWLIST CANNOT NARROW.** Measured, twice,
$0: the harness refuses to match `Write(path)` against a file operation and says so on startup —
only `Edit(path)` does, and it covers every file-editing tool. Worse and silent: **allow rules
union**, and `~/.claude/settings.json` carries bare `Read`/`Edit`/`Write`/`Bash(*)`, so
`--allowedTools` cannot narrow a headless session below that. **Only deny subtracts.** Three dead
`Write(/docs/…)` rules are gone from `.claude/settings.json`; the `Edit(...)` rules beside them
already did the job, proved with both tools plus a positive control, 42 team-lead files
byte-identical. `run_opus_packs.sh` confines with `--disallowedTools`, one rule per foreign pack.

**THE BLIND NEEDED THREE CUTS AND THE SWEEP THAT GUARDS IT WAS ITSELF BROKEN.** Removing the
printed verdict was one; the stratum tag says the same thing (S2's label *is* "the matcher found a
brand here"); and stratum-major ORDER would have made a whole pack one contiguous stratum. All
three handled — items shuffled by the same seed, `packs_carrying_one_stratum_only: []`, 3–4 strata
per pack. The blinding sweep's fence tracker never closed ` ```json `, so it read one header and
swept a pasted-back verdict clean; **its negative control is what found that**, not review.

**THE SCREEN REPORTS. `results/yield_screen_5c1_v2.json`, same script as the signed one (it gained
`--captions`, it was not forked), prereg `1aa89818…` re-hashed and unmoved, five controls green —
and `verdicts_reportable` goes FALSE → TRUE.** The signed screen refused because
@atb_market_official measured 0 relevant posts, and that channel is the one whose posts are
pictures. **bar A passed 29 → 32**, below-both 36 → 33, bar B unmoved. Three flips:
@atb_market_official 0 → 14, @atb_aktsiyi 1 → 26, @useful_healthy_fitness_menu 3 → 6. One change
of KIND: @gaid_skobioale was `TOO_FEW_TEXTED_POSTS` (1 texted post in 18, bar unreachable by
arithmetic) and its 17 captions make it `gradeable` — still FAIL, but now a finding about content.
194 graded on a caption, **67 blind**, 5 truncated. **NOTHING IS SIGNED HERE.**

**THE PAID POPULATION WAS 144, NOT 232 — AND EVERY MISSING POST IS COUNTED.** The census names
231 askable ids outside ATB and counts 11 more it never names (no media at all): 242. The sweep
fetched 175 and left **56 blind, 0 owed** — **42 of them video/mp4**, plus 8 pdf, 2 ogg, 2 docx,
1 pptx, 1 giveaway. @polyakova_fitness (18 of 18 video) and @Wellosophy_Lesya are wholly blind, so
no budget grades them. Of the 175 fetchable, **31 carry a poll and no image** — Telegram has been
carrying the question all along, so they are transcribed for **$0** and never reach the model.

**THE MEASURED PRODUCTION RATE FOR 5c2 IS $0.002328/POST** (7.592 s/row marginal, boot 183.58 s
priced once). That is HALF vis-b's ATB rate, and the reason is the manifest, not the model: 3.32
images per post against ATB's 5.68. The §C.1 gate re-priced before all 15 slices and never fired —
projection $0.35–$0.46 against $1.4676 left of the cap.

**GREEDY IS NOT BYTE-REPRODUCIBLE ACROSS WORKERS — AND THE VERDICT SURVIVED ANYWAY.** The smoke was
spent on `@atb_market_official:4340`, a post vis-b already bought, which made it a free
cross-endpoint control. Same weights, same NF4 config, same prompt sha, greedy, batch 1, image
lists proven byte-identical: vis-b wrote 164 chars, vis-c 172 (`Рудь, Своя Лінія та ковбасу` vs
`Рудь та Своя Лінія, а також ковбасу`). Different worker, different driver (580.173.02 →
570.211.01). `core.carriers` extracted **exactly the same three terms** from both. n = 1 — an
existence proof, not a rate; 5c2 prices a real re-run if any number is to be defended as
reproducible.

**A STABLE `worker_id` IS NOT A WARM WORKER, AND IT COST A PUBLISHED NUMBER.** The rescued boot
log (Dv67's debt, paid in step 0) is truncated at every boot and held ONE weight load and exactly
NINE request ids — vis-b's re-pilot's own `timing.calls`, with the handshake and smoke calls
absent. So the re-pilot paid its OWN cold start inside `worker_seconds: 492.07`, and vis-b's "one
worker, one cold start" is **retracted** in the ADR with the error named. A worker slot keeps its
id across scale-to-zero.

**KNOWN AND DELIBERATELY NOT FIXED:** `serve_handler.describe()` reports `max_new_tokens: 256`
under `SERVING_CONFIG=CAPTION` while the caption path runs at **400**. Provenance only —
`finish_reason` and `truncated_replies` use the real 400. Fixing it needs a volume re-stage, which
risks a session's one endpoint for a field; the next session that opens the volume does it.

**THE PROJECT'S OWN GEMMA 4 NOW WRITES CAPTIONS, AND THE SCREEN MOVES ON THEM.** 19 of 19 ATB
media-only posts, 8 jobs, 0 unusable, every row `caption_source: gm4-nf4-base`. `rematch`
re-derives the signed screen's zero and then reads **0 → 14 relevant, bar A PASS (bar = 4)** —
qwen's own bought reading was 0 → 13, so **the pre-registered instrument failure of 3.13 (4) does
NOT fire** and there is no fork to hand back. Prereg `1aa89818…` re-hashed before use and
untouched. §C.1 projected **$0.1716 against the $0.50 stop** and the leg cost **$0.1693** — 552 s
of wall at the settled rate, accurate to 1.4%. Balance deltas are NOT per-leg costs: a $0.24/h
pod was running inside those windows. **RETRACTED at vis-c:** this block used to say the whole
session ran on one worker and paid one cold start. `worker_ids` was the same across the legs, but
a slot keeps its id across scale-to-zero, and the rescued boot log shows the re-pilot booted for
itself — so its per-post rate is a **bound**, $0.0045–$0.0061, not the $0.00891 that divides the
whole leg by 19. **One
truncated reply** (`@atb_market_official:4391`, the 400-token ceiling, 847 chars against a
231-char median) is reported and NOT repaired — raising the budget would make the bridge compare
two ceilings.

**THE BRIDGE SAYS THE TWO INSTRUMENTS SAMPLE, THEY DO NOT DESCRIBE.** `results/bridge_gm4_qwen_5c1.json`:
**8 of 18 posts agree on terms**, four of those both-empty. It looks alarming per post — qwen
describes salmon where GM4 describes mayonnaise — and the free check settles it: **all 18 posts
sent byte-identical image lists by sha256** (same manifest `a93fc8a1…`, same `[:6]` slice, and
qwen's 102 vs GM4's 108 images differ by exactly the post qwen failed). So an ATB album is six
pages of a promo leaflet with dozens of products, and a ~230-character caption is a **sample** of
it. Term matching downstream inherits that sampling. **A 5c2 input, and not fixable by picking
the better captioner.** An agreement rate gates nothing — it tells a reader of a future screen
number which instrument produced it.

**THE MIDDLE RUNG NOW EXISTS: `scripts/preflight_serving_guards.py`, $0, RUN BEFORE PAYING.** It
builds a REAL `Gemma4ForConditionalGeneration` from a tiny config (no download, CPU, seconds) and
drives every serving guard both ways against real transformers + peft. It carries the vis-a guard
body as its own positive control, so it cannot degrade into a check that never looked, and it
exits 1 saying so when the libraries are missing — an unrunnable preflight is a finding, never a
pass. It caught a defect in itself on the first run (the control's verdict scored with inverted
polarity). `make check` stays torch-free: no test imports it.

**ATTEMPT 1 STOPPED AT THE BOOT RUNG FOR $0.1702, AND THE CAUSE WAS OUR OWN
GUARD.** `assert_no_adapter` refused the NF4 base it exists to admit: it read
`getattr(model, "active_adapters")` for truthiness, and transformers hands **every** model that
name as a bound method (`PeftAdapterMixin`), which is always truthy. The worker's own message
named the base class and did **not** name `peft_config`, so nothing was ever attached. Fixed at
`d408034` — the attribute is now *called*, and only its two "nothing is loaded" answers become an
empty list. The vis-a suite was green because its stubs had no such attribute at all: **a stub
built from the same assumption as the guard cannot contradict it.** The new negative control
fails against the old guard with the worker's own sentence.

**THE ONE MEASUREMENT THE SESSION DID BUY: GM4 NF4 + THE VISION TOWER LOADS ON A 24 GB CARD.**
`results/visb_worker_boot.log` — seven fitness checks in 3 983.97 ms, CUDA 12.8, then
**`1188/1188 [01:39]`**, no OOM. srv-2d's comparable load was 127 s *with* the adapter and no
processor. The forward pass at six images is a different allocation and is still **unmeasured**.

**AND THE FACT THAT ENDED IT: A RUNNING WORKER CANNOT BE REDEPLOYED.** The fix was staged onto the
volume and hash-verified byte for byte; the next handshake failed **identically**. The boot log
had been *appended to*, not truncated — the earlier copy is a byte-exact prefix — with **one**
`Starting Serverless Worker`, one worker id, and **two** full weight loads (~$0.031 each). The
container imported `serve_handler` at boot and held it. `--idle-timeout 60` did not stop a worker
that had failed a job: `/health` read `workers.running: 1` fifteen minutes later. Only
`serverless delete` stops one — and a fresh endpoint is what the contract forbids by name, so the
session reported what it bought. **Stage the volume BEFORE the endpoint exists.** The runbook now
says so, in §A.3 and in a new ladder rung.

**THE CAPTION INSTRUMENT IS BUILT AND UNPAID.** A third served configuration `CAPTION` (NF4 base
at the pinned revision, adapter OFF — refused on `ADAPTER_DIR`, on `MERGED_DIR`, on a missing
`MODEL_REVISION`, and on the loaded object itself via `assert_no_adapter`); the registered prompt
**`caption_post_gm4` = `41d33d0299fe…`** beside `caption_post` (`5dd76ab2…`), derived by one
clause; the processor path `local_llm.load_captioner` + `CaptionClient` at **400 new tokens** and
forward batch 1; required `caption_source` (`qwen-4.5g2` | `gm4-nf4-base`) with both readers
refusing an undeclared mix; `scripts/caption_gm4_5c1.py`; `scripts/runbook_vis_b.md`.
**1 343 tests, 33 s**, and the four deliverable commits were each checked out and run alone
(1302 / 1323 / 1333 / 1342). Deviations: 13, and Dv40 explains twelve of them — the judgment
call it names sits at the head of the report, not inside it.

**THE RUNBOOK'S OWN FIRST COMMAND IS NOW DRIVEN, AND IT FOUND A BUG.** §B's invocation shape had
never been run: the write path was proved through `--smoke`'s redirected defaults and a fake
client on tmp paths, neither of which is what the document prints. Run verbatim, `--only`
turned out to narrow `images` and `polls` but **not** `blind` — a one-post smoke would have
written the whole manifest's `no_surrogate_at_all` into its record. Empty on the ATB manifest,
so nothing showed; vis-c is a different scope. Fixed, and a test now runs §B word for word.

**TWO NUMBERS vis-b INHERITS, MEASURED FOR FREE.** One post at six images is **3.68 MB** encoded
against RunPod's documented **10 MB `/run` ceiling** — the pictures ride inside the job because
`data/annotation/**` is gitignored — so the 19 ATB posts are **8 jobs, largest 7.83 MB**. And the
cold start on this endpoint class is **$0.0733** (239.022 s × $0.00030669/s), 7% of vis-b's cap
before a single caption exists.

**PARITY IS RUN, THE ATTEMPT IS SPENT, AND IT HOLDS.** `results/parity_srv2.json`:
**758/758 rows scored, zero parse / api / generation failures**, config A on `ADA_24` in EU-RO-1
off the volume. Both clauses of 3.11 (2) hold — G1b, G1d and G1e (everything 4.5h2 passed) still
pass, `under_bar: []`, and the **worst head movement against `results/parity_5b_a.json` is
+0.0000**: nothing dropped, G1c rose 0.0018 (and now clears a bar the pod missed by 0.0005), G1e
rose 0.0133. G1a fails its bar exactly as it did on the pod and at 4.5h2, to the same sixteen
digits — the deferred 3.11 question, not a new finding. Row agreement with the pod **751/758 =
99.08%**, description and gated on nothing. **A serving number may now reach an aggregate.** Not
appended to `results/baselines.json`: a parity measurement is not a gate anchor, and the pod
reading of 08-06 is not in there either.

**AND THE COST IS THE FINDING.** `results/srv2d_cost.json`: **$1.4281 / 1000 rows against the
pod's committed $0.5993 — 2.38×**; $1.0825 a pass against $0.4611. The cause is priced, not
mysterious: the RTX 4090 worker runs **4.262 s/row against the A6000 pod's 4.071** (4.7% slower)
at **$1.1041/h equivalent against $0.53/h**. Two independent readings agree to 1% — this
endpoint's own settled ledger rate on measured seconds, and the balance delta — and Dv33 makes
both **floors**. See Next: this is the operator's ruling, not the executor's.

**THE SERVERLESS RUNTIME IS PROVEN END TO END, AND THREE OLD BELIEFS ARE DEAD.** The 5b "wall"
(no endpoint reaches a job-consuming worker) was true on 08-06 and is gone. srv-2b's diagnosis
("our own container does not start") was **falsified twice** — by srv-2c's boot log, and then by
an operator-bought control running srv-2b's *exact unwrapped argv* twenty minutes later on the
same volume, region and class: also COMPLETED. So srv-2b's hang was **the platform**, not us. And
the 24 GB fit is answered better than the preference: **19 874 of 24 564 MiB**, batch 1, with the
adapter loaded. `ADA_24` with a volume attached allocates and consumes; the 48 GB half was never
asked, because EU-RO-1 catalogues only the A6000 at stock `none`.

**THE VOLUME IS THE ONLY STANDING RESOURCE AND ITS CONTENTS ARE KNOWN.** `qw4nwleanc`, 100 GB,
EU-RO-1, **$0.009722/h settled** (= $7.00/720 h, read from `billing network-volume`, not a prior).
It holds `hf/` at revision `842da379…`, `venv/` with the pinned stack (`runpod 1.11.0`, outside
the 1.7.11–1.10.0 job-tracking bug), `repo/` at **`d408034`** (moved by vis-b from `ed9c0c9`, the
six runtime files hash-checked on both sides — and vis-b-r left it there deliberately, because
`git diff d408034 HEAD` over every file the worker imports is EMPTY), the adapter at
`b3ca6308…`, the caption dumps, and `start.sh` byte-identical to `scripts/start_5b_worker.sh`.
Everything else is deleted and proven deleted by listing. **Two 5b-era serverless TEMPLATES also
survive** (`unfcr3ja0t market-pulse-5b-a`, `0g6zg73ptq mp-5b-diag`): they carry no charge, but
they were invisible until vis-b — `runpodctl template list` shows official + community only, and
**`--type user` is the only listing that can prove a template deletion**, which is why deletion
proofs are now positive-controlled: show the listing displaying a live object first, then gone.

**5c1: THE REGISTRY IS 66 = launch 59 + watch 7**, the window is **9 393 posts and 4 880
comments** over 63 channels (0 malformed rows, `shasum -c` 6/6), and the queue 5c2 prices is
**16 218 rows**. Two channels that did not exist in the repository twelve hours earlier carry
**81%** of what was collected. `mothers_kids` is 3 live channels against 0.

**THE YIELD SCREEN REFUSED TO REPORT, AND THE REFUSAL IS HONEST.** Its pre-registered positive
control failed on @atb_market_official — 25 posts in its own 28 days, **19 image-only**, no dairy,
no ice cream, no watchlist brand — so `verdicts_reportable: false`, exit 1, record complete. Of 66
sources, 29 clear bar A and 8 bar B; of the 36 below both, **only 24 can be graded** — nine have 0
posts in the window and three have fewer readable posts than the bar itself, and seven of those
twelve are the whole `watch` bucket. **"варто" outscores every real brand** (89 posts in 24
channels): ATB's private label and an ordinary Ukrainian word. Nothing was patched — the lexicon is
`draft-not-law` and the watchlist is the operator's.

**CAPTIONS ANSWER THE MODALITY QUESTION: ATB GOES 0 → 13.** Corpus blindness is 2.8% and unevenly
spread. The pilot billed **twice its projected rate** — $0.000948/post against 4.5g2's $0.000483,
same model, same endpoint, same prompt — $0.0180 of its $0.10 cap.

## ⏭️ Next

**R1–R5 ARE RATIFIED (operator, 10.08) — the readings are above and in the pre-registration.**

**WHAT IS LEFT, IN ORDER.** (1) **The adjudication sitting** — ~45–60 minutes of operator time on
`data/annotation/sku_a_text/text30.csv`, `README-text30.md` beside it, then
`PYTHONPATH=src python3 scripts/validate_sku_text_pack.py`, which refuses a non-tick cell, a moved
GIVEN column and a moved ladder and computes no gate number. (2) **sku-b**: two legs, cap $0.35, ONE
attempt, a failed bar closes B by measurement. Its step 0 also carries the four acceptance tails
listed under Blockers. (3) Then the **5c2 briefing**.

**WHAT sku-b MUST NOT DO.** Re-run a bar after seeing its result; read the 159 available pages
instead of the 108 the gold covers; write a renderer (both are built and tested —
`prompts.positions_messages_page_gm4`, which refuses two images, and
`positions_messages_text_gm4`); score its own sample (SPEC §10 — bar 2 is the team lead's read of
the per-position dump against the page images); or read a parse failure as an empty answer.

**THE OPUS-AUDIT QUEUE IS CLOSED.** The FN split, the 23 remaining packs and the findings sitting all
happened on 10.08 — see [[opus-review-programme-close]] and
[[sitting-2026-08-10-composition-signed]]. Nothing in that programme is owed.

**THE RUNTIME IS RULED, AND IT IS SERVERLESS.** The team lead accepted srv-2d the same night
(`docs/STATUS.md`, "ТЫ ЗДЕСЬ — serverless ДОКАЗАН (паритет Δ=0); 5c1 снят с HOLD"): parity verified
against the artefacts, **serverless validated as the runtime**, ruling 23 executed, **5c1 comes off
HOLD**, and the vis contracts are re-issued against the endpoint. The cost finding was accepted as
a finding **against** the chosen path and goes into the 5c2 briefing rather than being argued away
— their reading of the same artefacts, $1.0825/pass against $0.4611 (×2.35), matches
`results/srv2d_cost.json` (the per-1000 ratio is 2.38 on a different denominator, both correct).

**QUEUED WHILE vis-c RAN — READ BEFORE STAGING ANYTHING.** The team lead landed a new SPEC §3.16
and two contracts: `docs/PROMPT-opus-audit-a.md` ($0, local — build the packs, the validator and
the reader) and `docs/PROMPT-opus-audit-protocol.md` (one Opus 5 session per pack). Class is
**REVIEW**: a second instrument reviewing the deterministic matcher and the GM4 captioner, and
**nothing it produces may enter a gate, the screen, or `results/baselines.json`** — the matcher
stays the judge. `docs/SPEC.md` and `docs/STATUS.md` also moved and are uncommitted; they are
team-lead files, commit them **unedited** and stage by path (`git add -A` would sweep the vault
tail and the new prompts into one commit).

**NEXT: THE SITTING OF 3.16 (3), THEN THE SIGNATURE, THEN 5c2.** The audit is off the critical
path: 25 of 25 packs, 498 of 498 rows, `results/opus_audit_5c1.json` rebuilt over the whole
population and committed with its returns preserved in `results/opus_audit_returns/`. What the
sitting rules on, in one list: **141 open-extraction names** the watchlist lacks · **`varto` in both
columns** (13 misses, 69 FPs — the adverb against the brand) · `president` ×24 and `varus-pl` ×5 as
already-settled collisions arriving a second time · «Селянське» as a watchlist TM *and* a butter
grade · **3 captions judged outright wrong** and 43 partial of 163 (faithful rate 0.7178) · and the
finding under all of it, that the FN column prices the caption's coverage and not the matcher.
Nothing here may enter a gate — 3.16 (1), review class, the deterministic matcher stays the judge.
No contract is outstanding and nothing is queued.

**AFTER THE SIGNATURE: 5c2.** vis-c is done and the package is on the desk —
`results/yield_screen_5c1_v2.json`, the same instrument as the signed screen, prereg `1aa89818…`
unmoved, `verdicts_reportable: true`, **pass_A 32 of 66**, below-both 33, 67 blind named and
counted. The launch composition is frozen by the operator's own word and **this executor signed
nothing**. Nothing is queued and no contract is outstanding.

**What 5c2 inherits, priced:** the caption instrument (NF4 base at `842da379…`, adapter OFF,
prompt `caption_post_gm4 41d33d0299fe…`), the CAPTION template recipe and the volume at
`d408034`, the 10 MB `/run` transport ceiling, and **two rates that must not be confused** —
marginal **$0.002328/post** on the wide manifest (3.32 images/post), marginal **$0.0045–$0.0061**
on ATB leaflets (5.68 images/post), plus the cold start **once** at the pre-registered $0.0733
(measured $0.0563 here). Never multiply an all-in per-post figure by a post count.

**Three questions vis-c answered rather than left open:** (1) the 400-token ceiling truncated 4 of
144, concentrated in the two leaflet channels — a case about leaflet channels specifically, and
only ever a NAMED revision; (2) blind is 56 of 231 and **42 of those are video**, not a fetch
failure, so no budget grades @polyakova_fitness or @Wellosophy_Lesya; (3) a caption is a SAMPLE of
a dense leaflet, which is the bridge's finding and a 5c2 design input.

**One defect left on purpose:** `describe()` reports `max_new_tokens: 256` under CAPTION while the
caption path runs at 400. Fix it on the next trip that opens the volume — a re-stage risks a
session's one endpoint, and there is no restart lever short of deleting the endpoint.

## 🚧 Blockers

**THE 30-ROW PACK IS BLANK, AND IT IS THE ONLY BLOCKER.** Without it bar 3 has no gold.
`data/annotation/sku_a_text/text30.csv`, README beside it, ~45–60 minutes of operator time, then
`PYTHONPATH=src python3 scripts/validate_sku_text_pack.py`. Everything else sku-b needs is built,
pinned and ratified.

**FOUR ACCEPTANCE TAILS, RULED INTO sku-b's STEP 0 (team lead, 10.08):** (1) commit the two vault
files the tree carries — the 10.08 daily log and `knowledge/index.md` (both landed in `e40c58e`; what
is dirty now is a 17:53 Stop-hook regeneration of the index plus this checkpoint's own edits);
(2) curate this file — 604 lines, `cat` in full at every boot against a 9.0K-token target; (3) an ADR
of the R1–R5 ratification; (4) SPEC 3.17 (7) plus the pin-test evolution, one green commit.

**The signature is DONE** (66 = launch 59 + watch 7, stamped in `config/registry.yaml`), and its
price is a live footgun rather than a blocker: five sealed records pin the pre-stamp bytes, so
`validate_opus_returns.py` and `read_opus_audit.py` refuse to run. Correct. Do not re-pin.

**The `permissions.deny` hole is CLOSED** — the team lead added `Edit(/docs/PRODUCT.md)` on 10.08, so
all four team-lead file classes are now enforced and not merely observed.

**None, technical.** The 2026-08-07 FloodWait wall cleared at 10:02:05 UTC and ~100 resolves drew
no new one — because every collection run carried `--only`. That is discipline, not luck.

**Budget is the live constraint.** Phase 4 stands at **$22.0663 of $25.00, $2.9337 left** (read
2026-08-09 after the vis-c close, still settling — Dv33). 09.08 spent **$0.4993** on vis-b (both
attempts, inside $1.00) and **$0.5505** on vis-c (inside $1.50, $0.9495 unspent). `pod list -a` →
`[]`, `serverless list` → `[]`, `template list --type user` → the two 5b leftovers; only the
volume stands and only it bills. Re-read the guard before each session rather than trusting this
line, and note the volume's own $0.009722/h keeps running underneath it.

**Bill the compute on `worker_seconds`, not `wall_seconds`.** vis-c reconciles: endpoint
$0.4598 (rate x worker) + ~$0.08 of pod and volume = $0.5398 against a $0.5505 balance floor, 2%
apart in the right direction. On wall the endpoint alone reads $0.5341 and leaves no room for the
pods that demonstrably ran. vis-b's $0.1693 leg was priced on wall; on this basis it is $0.1509,
and both sit inside a settling balance's noise, so that figure stands and this is the better basis
going forward.

**Recorded rather than open:** the CA-MTL-3 volume is deleted, so its **~$0.24/day** idle billing
has stopped — that literal is load-bearing, not decoration: `scripts/volume_calc_5c1.py` greps it
out of THIS file as a priced input, and a rewrite that drops it reddens ten tests. Arm A's 4.5h2
per-row dump is permanently lost (`results/predictions/LOST.md`). Two billed rows nobody claims:
a **4090 pod row, $0.5098 / 2 470 s on 08-08** (Dv38) and srv-2b's 30-second A4500 row — neither
moves a number, since `runpod_guard.spend()` takes the max of the balance delta and the ledger and
the delta binds.

**SUPERSEDED, kept so the old line is not re-read as current:** "no serverless endpoint on this
account reaches a job-consuming worker" was true on **2026-08-06** and is the honest content of
`results/parity_verdict_5b.json`. Everything after it — the probe, srv-2b's volume-attached
allocation, srv-2c's boot log and control, srv-2d's 758 rows — overturned it. Do not cite that file
as current state.

## ⚠️ Footguns for the next run

**The caption endpoint cannot be made by editing the srv-2d template — `settings()` refuses it,
by design.** `SERVING_CONFIG=CAPTION` beside `ADAPTER_DIR` or `MERGED_DIR` raises before the
model loads, because an endpoint updated from an A template keeps A's environment and a caption
worker that quietly loaded the classification adapter would answer every job while every row it
wrote still said `gm4-nf4-base`. Create a NEW template with the three variables of
`runbook_vis_b.md` §A.1 and nothing else. The refusal is against `serve_handler.ADAPTER_ENV` as a
whole, not against two names inline, so a third such variable added later still fires — and a
test derives that tuple back out of the code that reads it.

**A caption travels as base64 inside the job, and RunPod's `/run` ceiling is 10 MB.** One ATB
post at six images is 3.68 MB; a slice of three is up to 7.83 MB. There is no volume path for the
pictures — `data/annotation/**` is gitignored, so they exist only on this Mac. If a post ever
grows past the budget the driver refuses rather than dropping images, because a shortened album
is a different instrument for that one post.

**A `git fetch` that names a missing ref leaves the OLD `FETCH_HEAD`, so the merge after it
"succeeds" and moves nothing.** `git bundle create f.bundle <base>..HEAD` names its ref **`HEAD`**,
not `main`; the srv-2d staging script (copied from srv-2c, whose bundle carried `main`) fetched
`main`, printed `fatal: couldn't find remote ref main`, and the next line's `merge --ff-only
FETCH_HEAD` then merged the **previous session's** pointer and printed `Already up to date.` The
volume stayed on the old commit with a paid run minutes away. Only the script's own sha256
comparison against the Mac's values caught it. End every deploy with a **content** check of the
files the runtime executes; `git bundle list-heads` names the real ref in one command.

**`smoke_5b.py --record` defaults to `results/serving_5b.json` — the pod's cost anchor.** That file
holds the `adopted` block every serverless comparison is measured against ($0.5993/1000,
$0.4611/pass, 4.071 s/row). A smoke run without an explicit `--record` overwrites the baseline with
the number under test. Always pass a path.

**RunPod's request policy is in MILLISECONDS and every briefing writes seconds.**
`serving.execution_policy(3600, 7200)` is the one conversion point and it refuses values under the
documented minimums (5 s / 10 s). The endpoint's own `--execution-timeout` takes **seconds** and
stores ms — the two are opposite, which is exactly how a 3 600 ms budget kills an hour-long job.
Set the endpoint-level timeout to cover the run as well: if a per-request override silently fails,
the endpoint value is what remains.

**A RUNNING WORKER HOLDS THE CODE IT BOOTED WITH — a `git merge` on the volume reaches nothing.**
vis-b paid $0.1581 to learn it: the fix landed on the volume, hash-verified byte for byte, and
the next handshake failed identically. The boot log had been **appended to**, not truncated (the
earlier copy is a byte-exact prefix), with one `Starting Serverless Worker`, one worker id and
two full weight loads at ~$0.031 each. There is no reload lever: `serverless update` does not
restart a worker, `--idle-timeout 60` did not stop one that had failed a job (`/health` read
`workers.running: 1` fifteen minutes later), and **only `serverless delete` stops it**. So:
**stage the volume BEFORE the endpoint exists**, run every guard the worker will run on the
volume's own interpreter while a $0.24/h staging pod is still up, and treat the code as frozen
from the first request onward.

**A failing serverless worker bills exactly like a working one, and only DELETE stops it.** srv-2b's
worker was `running` for 31 minutes at **$0.00031/s** with its job stuck in the queue — $0.55 for
nothing. `--idle-timeout 60` does not apply to a worker that never reports itself idle, and
`runpodctl serverless update <id> --workers-max 0` returned a success payload while the REST API
still read `workersMax 1`. Watch **the first job's status**, not the worker's health, and delete
the endpoint on the first worker restart. Two more from the same session: `runpod_guard`'s billing
corroboration walks `billing pods` and `billing network-volume` only, so **serverless spend is
invisible to it** (an $0.86 under-count here — only the balance delta binds); and a remote
`pgrep -f "hf download"` inside an ssh command **matches its own shell**, so a download-finished
poll reported `alive=yes` for eight minutes after the file was complete.

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

**Never `git add -A` here.** `docs/SPEC.md` and `docs/STATUS.md` are modified by the team lead
right now, and the next queued `docs/PROMPT-5c*.md` will land untracked without warning. Stage by
path. The same trap has fired with every queued prompt since `docs/PROMPT-4.5g4.md`.

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
  never edit — **one `Edit(path)` deny rule covers every file-editing tool, Write included**, and it
  bites without a restart. A `Write(path)` rule is not the other half of that pair: the harness
  refuses to match one against a file operation and says so on startup. Three of them sat in
  `.claude/settings.json` doing nothing until 2026-08-09; dropping them changed no behaviour, and
  the probe that proved it is in `implementation-notes.md` (Dv94). Phase-end facts go to the daily
  log or `implementation-notes.md`. The refusal reads "File is in a directory that is denied", but
  the rules are file-scoped: the rest of `docs/` is still writable.
- **A ceiling lifted by the operator is not a ceiling lifted in code.** `train_xlmr_baseline.py`
  refuses to train above `--time-budget-min` and exits **3** — it prints a projection and leaves no
  process, which reads exactly like a crash. Grep your own guards before any unattended launch.
- **A run that trips the cap writes no record** — a partial run must never become a gate anchor.
  Do not re-run with a bigger `--max-run-usd` to get the record.
- **`results/baselines.json` is append-only and never hand-edited.** Numbers reach it only through
  the scorer; `scripts/show_results.py` only reads. A hand-typed number there is invisible.
- **A results record cannot name the commit that contains it**, so provenance is `commit` + the
  `dirty` paths at run time; the runner shouts if any is under `src/`, `scripts/` or `config/`.
- sklearn lives in the `baseline` extra and torch/transformers in `xlmr` — no test may import
  either, or `make check` stops being runnable on a bare checkout.
- `RAW_STORE_SALT` in `.env` must never be rotated: a new salt orphans every `sender_anon_id`.

- **A print statement can crash a run after the record is written.** The G1b-slice line at the end
  of `eval_zero_shot.main` was guarded by `anchor_valid` alone; on a fine-tuned arm `slice_ids` is
  `None`. It would have raised at the end of a 45-minute eval following a 3.4 h training run. Drive
  `main` through `--record-out` with a stub: `--smoke` returns before the record is built and
  `--probe` before it is written, so neither exercises that path.

## 🐞 Known harness bug

Fixed 2026-07-28: `knowledge/templates/daily-log.md` now carries `{{DATE}}`, the placeholder
`scripts/brain-session-end.py` actually substitutes; `tests/test_templates.py` keeps the pair
honest.
