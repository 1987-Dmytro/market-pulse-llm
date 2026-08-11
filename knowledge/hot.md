<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-08-11 12:29:30 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
5add452 docs(adr): the five sku-b readings ratified, and bar 3's denominator is 30
d3bf781 docs(spec): 3.17 (7) ratified, and the pin holds the law instead of the file
5c94f40 chore(vault): the standing tail -- 10.08 checkpoint, the 11.08 stub, hot.md, index
e1a46a5 chore(augment): the Tooling layer -- CLAUDE.md routing map + the runbook behind it
daa2832 docs(team-lead): the 11.08 arch-a brief, the 10.08 acceptance block, the PRODUCT.md deny line
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `sku-b-pilot-readings-ratified.md` — sku-b's five readings are ratified, the text gold is adjudicated, and bar 3's denominator is all 30 rows
- `sitting-2026-08-10-composition-signed.md` — The 2026-08-10 sitting: «Варто» loses text matching, «Селянське» needs an anchor, the 141 names wait for the position layer, and the composition is signed

## 📅 Recent daily logs

- `2026-08-11.md`
- `2026-08-10.md`
- `2026-08-09.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->
# Hot Cache — curated

**Last update:** 2026-08-11 (arch-a step 0). **sku-a IS ACCEPTED, R1–R5 ARE RATIFIED, THE 30-ROW TEXT
GOLD IS ADJUDICATED, AND SPEC 3.17 (7) IS LAW.** Everything sku-b needs is built, pinned and ratified.
Live phase: **arch-a** ($0 — code graph, `docs/ARCHITECTURE.md`, instrument inventory; nothing is
deleted). Then **sku-b**: one paid attempt, cap $0.35, a failed bar closes B by measurement. This
block is hand-edited; the section above it is auto-generated — do NOT touch the marker. Long form:
`implementation-notes.md` (Dv100–), the day logs [[2026-08-11]] / [[2026-08-10]], and the ADRs named
inline below.

## 🔥 What's Hot

**THE FIVE RATIFIED READINGS ARE HOW EVERY sku-b NUMBER IS COMPUTED, AND THEIR HOME IS
`results/sku_pilot_prereg.json` — NOT THIS FILE.** [[sku-b-pilot-readings-ratified]] is the long form.
**R1** recall per POST over the union of a post's page answers, macro-averaged over the 15 posts with
a non-empty gold set (the micro reading over 55 pairs is reported and gates nothing). **R2** the page
set is the **108 SENT** pages, not the 159 available. **R3** the four empty-gold posts are a precision
probe, not recall. **R4** bar 2 scores at n ≥ 10 pairs, reports at 1–9, NOT_REACHABLE at 0. **R5**
unreadable replies are excluded and counted (>10% blocks bar 3), n ≥ 20, carriers pooled. Thresholds
(0.75/0.80/0.85), the $0.35 cap and "one attempt" never moved.

**BAR 3's DENOMINATOR IS ALL 30 ADJUDICATED ROWS, AND 14 WAS REFUSED (team lead, 11.08).** Gold `none`
is a VALUE — the prereg's `comparison` clause makes the model answer `[]` to match it. The 16 `none`
rows price refusal discipline, the 14 rung rows price tiering, and the bar catches both failure modes
(always-`[]` = 16/30 = 0.53, always-a-position = 14/30 = 0.47). Composition from the registered
validator: 11 position · 3 product_mention · 0 brand_mention · 16 none, of the none-rows 12 carry
ticks without a brand and 4 are all-empty pre-filter false positives.

**SPEC 3.17 (7) IS IN THE FILE, AND THE PREREG PIN NOW HOLDS THE STRIPPED TEXT.** The amendment is
wrapped in `<!-- sku-b-ratification begin/end -->` markers; `write_sku_prereg.registered_law` cuts the
block out and the pin `973c8789…` is the sha of what is left. ONE strip function, called by the
producer and by `test_every_pinned_input_still_hashes_to_what_it_says` — a second copy would drift and
nothing downstream would see it. **Never re-pin the prereg**, and never add a second marked block:
the strip refuses more than one.

**THE PRE-FILTER'S FRAME IS MOSTLY RECIPES, AND THAT IS THE RULE WORKING AS WRITTEN.** 769 of 31 638
collected rows (= 769 of the 25 263 that carry text): posts 717 of 14 388 texted (4.98%), comments 52
of 10 875 (0.48%). `passed_carrying` = currency 226 · percent 384 · size 478 of the 717 posts. Top
channels after @silposilpo are recipe feeds firing on «сир» beside an ingredient quantity. The 30-row
pack prices it: 4 of 30 drawn rows are direct false positives. Comments are 6.8% of the frame, so bar
3 prices the POST leg; a comment bar of its own is a team-lead ruling after the pilot.

**THE SIGNATURE STAMP MOVED `config/registry.yaml`'s SHA, AND FIVE SEALED RECORDS PIN THE OLD BYTES.**
`validate_opus_returns.py` and `read_opus_audit.py` REFUSE to run — correctly. **Do not re-pin any
manifest.** To re-derive `results/opus_audit_5c1.json`, check the registry out at `d832477`;
`tests/test_registry.py::registry_without_the_signature_stamp` strips the block and reproduces the
signed bytes `c82d0cff…`, and that reconstruction is the only chain between the two.

**THE AUDIT'S AND THE SITTING'S NUMBERS LIVE IN ADRs, NOT HERE.** [[opus-review-programme-close]]:
25/25 packs, 498/498 rows, `fn_matcher` **0** with all 102 misses image-only — so `recall_candidate`
0.4769 is a number about the CAPTIONS and must never be quoted as the matcher's; captions 117/43/3
(0.7178); 93 of 104 FP are «варто» + «Президент»; 141 names outside the watchlist; the strata's FN
columns do not sum (an item carries every stratum it belongs to). [[sitting-2026-08-10-composition-signed]]:
«Варто» text-matching OFF, «Селянське» anchored-only, the 141 names deferred into the position layer.
Both are 5c3's **NAMED** revision and **neither is applied in sku-a or sku-b** — brand resolution
there is the plain alias table.

**A CAPTION IS A SAMPLE OF A LEAFLET PAGE, AND NO BETTER CAPTIONER FIXES IT.** GM4 vs qwen agree on
terms for 8 of 18 posts on inputs proven byte-identical by sha256 ([[5c1-vis-b-caption-instrument]]) —
an ATB album is six pages carrying dozens of products and a ~230-character caption samples it. That is
why the position layer exists: sku-b measures a NEW per-page instrument (1 page = 1 call, recall bar
0.75) and captions stay in the loop for **themes and coverage, never for brands**.

**OPERATIONAL, AND IT WILL RECUR: THE HARNESS KILLS LONG BACKGROUND WORK.** A 2.7 h driver launched
with Bash `run_in_background` was stopped from outside at 36 minutes. Launch anything past half an
hour with `nohup … & disown`, and watch the **process** (`while pgrep -f "[r]un_x.sh" …` — the bracket
stops `pgrep` matching the watcher itself), never a `tail -f`, which is silent through a dead process
exactly as it is through a quiet one.

**ONLY `deny` NARROWS A SESSION, AND `Write(path)` IS NOT A RULE.** The harness refuses to match
`Write(path)` against a file operation; only `Edit(path)` does, and it covers every file-editing tool.
Allow rules **union** with `~/.claude/settings.json`, so `--allowedTools` cannot narrow a headless
session below it. `permissions.deny` is 4 entries and now covers all four team-lead file classes
(STATUS, SPEC, PRODUCT, PROMPT-*). `run_opus_packs.sh` confines with `--disallowedTools`.

**TWO RATES THAT MUST NOT BE CONFUSED, AND A COLD START PRICED ONCE.** Marginal **$0.002328/post** on
the wide 5c2 manifest (3.32 images/post); marginal **$0.0045–$0.0061** on ATB leaflets (5.68
images/post); cold start **$0.0733** pre-registered, $0.0563 measured. Never multiply an all-in
per-post figure by a post count, and **bill compute on `worker_seconds`, not `wall_seconds`** — vis-c
reconciles to 2% that way and leaves room for the pods that demonstrably ran.

**A JOB CARRIES ITS IMAGES AS BASE64 AND RunPod's `/run` CEILING IS 10 MB.** One ATB post at six
images is 3.68 MB, a slice of three up to 7.83 MB, so the 19 ATB posts are 8 jobs. There is no volume
path for the pictures — `data/annotation/**` is gitignored, they exist only on this Mac. The driver
refuses rather than dropping images: a shortened album is a different instrument for that post.

**GREEDY IS NOT BYTE-REPRODUCIBLE ACROSS WORKERS** — same weights, NF4 config, prompt sha, batch 1 and
byte-identical image lists produced 164 vs 172 chars on two workers (different driver versions), while
`core.carriers` extracted exactly the same terms. n = 1: an existence proof, not a rate. **And a
stable `worker_id` is not a warm worker** — a slot keeps its id across scale-to-zero, which retracted
vis-b's "one cold start" in its own ADR. Find the boot, subtract it once, quote all-in and marginal
separately.

**KNOWN AND DELIBERATELY NOT FIXED:** `serve_handler.describe()` reports `max_new_tokens: 256` under
`SERVING_CONFIG=CAPTION` while the caption path runs at **400**. Provenance only — `finish_reason` and
`truncated_replies` use the real 400. Fixing it needs a volume re-stage, which risks a session's one
endpoint for a field; the next session that opens the volume does it.

**THE MIDDLE RUNG EXISTS: `scripts/preflight_serving_guards.py`, $0, RUN BEFORE PAYING.** It builds a
REAL `Gemma4ForConditionalGeneration` from a tiny config (no download, CPU, seconds) and drives every
serving guard both ways against real transformers + peft. It carries the vis-a guard body as its own
positive control, so it cannot degrade into a check that never looked, and it exits 1 when the
libraries are missing — an unrunnable preflight is a finding, never a pass. `make check` stays
torch-free: no test imports it.

**THE VOLUME IS THE ONLY STANDING RESOURCE AND ITS CONTENTS ARE KNOWN.** `qw4nwleanc`, 100 GB, EU-RO-1,
**$0.009722/h settled**. It holds `hf/` at revision `842da379…`, `venv/` with the pinned stack (`runpod
1.11.0`), `repo/` at **`d408034`**, the adapter at `b3ca6308…`, the caption dumps, and `start.sh`
byte-identical to `scripts/start_5b_worker.sh`. Everything else is deleted and proven deleted by
listing. **Two 5b-era serverless TEMPLATES also survive** (`unfcr3ja0t`, `0g6zg73ptq`): no charge, but
they were invisible until vis-b — `--type user` is the only listing that can prove a template
deletion, which is why deletion proofs are positive-controlled (show it live, then gone).

**5c1: THE REGISTRY IS 66 = launch 59 + watch 7**, signed by the operator 10.08 (the stamp moves the
file's sha and no row of it). The window is **9 393 posts and 4 880 comments** over 63 channels and the
queue 5c2 prices is **16 218 rows**. Screen v2 reports (`results/yield_screen_5c1_v2.json`, prereg
`1aa89818…` re-hashed and unmoved): **pass_A 32 of 66**, below-both 33, **67 blind** named and counted,
of which 42 are video. **This executor signed nothing** — the composition is the operator's word.

## ⏭️ Next

**arch-a IS LIVE ($0).** Code graph (graphify + post-commit hook), `docs/ARCHITECTURE.md` with the two
ratified flows, and an instrument inventory of every prompt, script and module. **Nothing is deleted
or renamed** — the candidate-dead list goes to the operator for a ruling at acceptance.

**THEN sku-b:** two legs, cap $0.35, **ONE attempt**, a failed bar closes B by measurement. **Then the
5c2 briefing.**

**WHAT sku-b MUST NOT DO.** Re-run a bar after seeing its result; read the 159 available pages instead
of the 108 the gold covers; write a renderer (both are built and tested —
`prompts.positions_messages_page_gm4`, which refuses two images, and `positions_messages_text_gm4`);
score its own sample (SPEC §10 — bar 2 is the team lead's read of the per-position dump against the
page images); or read a parse failure as an empty answer.

**DEFERRED, DECIDED AFTER THE PILOT AND NOT BEFORE:** a two-stage leaflet read (OCR transcript → SKU
from the text) — the operator's 10.08 proposal, recorded under "Отложено СОЗНАТЕЛЬНО" in
`docs/STATUS.md`; and whether `carrier=comment` earns a bar of its own. The pre-registration does not
change either way.

## 🚧 Blockers

**None on the critical path.** The 30-row pack is adjudicated and committed, R1–R5 are ratified, SPEC
3.17 (7) is law, and the deny gap is closed.

**Budget is the live constraint.** Phase 4 stands at **$22.0663 of $25.00, $2.9337 left** (read
2026-08-09 after the vis-c close, still settling — Dv33). `pod list -a` → `[]`, `serverless list` →
`[]`, `template list --type user` → the two 5b leftovers; only the volume stands and only it bills.
Re-read the guard before each session rather than trusting this line.

**Recorded rather than open:** the CA-MTL-3 volume is deleted, so its **~$0.24/day** idle billing has
stopped — that literal is load-bearing, not decoration: `scripts/volume_calc_5c1.py` greps it out of
THIS file as a priced input, and a rewrite that drops it reddens ten tests. Arm A's 4.5h2 per-row dump
is permanently lost (`results/predictions/LOST.md`). Two billed rows nobody claims: a 4090 pod row
$0.5098 / 2 470 s on 08-08 (Dv38) and srv-2b's 30-second A4500 row — neither moves a number.

**SUPERSEDED, kept so the old line is not re-read as current:** "no serverless endpoint on this account
reaches a job-consuming worker" was true on **2026-08-06** and is the honest content of
`results/parity_verdict_5b.json`. Everything after it overturned it — parity is 758/758 with worst head
movement 0.0000, see [[srv2-program-close]]. Do not cite that file as current state.

## ⚠️ Footguns for the next run

- **The caption endpoint cannot be made by editing the srv-2d template — `settings()` refuses it, by
  design.** `SERVING_CONFIG=CAPTION` beside `ADAPTER_DIR` or `MERGED_DIR` raises before the model
  loads. Create a NEW template with the three variables of `runbook_vis_b.md` §A.1 and nothing else.
  The refusal is against `serve_handler.ADAPTER_ENV` as a whole, so a third such variable still fires.
- **A RUNNING WORKER HOLDS THE CODE IT BOOTED WITH — a `git merge` on the volume reaches nothing.**
  vis-b paid $0.1581 to learn it. `serverless update` does not restart a worker, `--idle-timeout 60`
  does not stop one that failed a job, and **only `serverless delete` stops it**. **Stage the volume
  BEFORE the endpoint exists** and treat the code as frozen from the first request onward.
- **A failing serverless worker bills exactly like a working one.** srv-2b's was `running` 31 minutes
  at $0.00031/s with its job stuck in the queue. Watch **the first job's status**, not worker health.
  Two more from that session: `runpod_guard`'s billing corroboration walks pods and volumes only, so
  **serverless spend is invisible to it** (only the balance delta binds); and a remote `pgrep -f` inside
  an ssh command **matches its own shell**.
- **A `git fetch` that names a missing ref leaves the OLD `FETCH_HEAD`,** so the merge after it
  "succeeds" and moves nothing (`Already up to date.` is also the signature of a no-op). End every
  deploy with a **content** check of the files the runtime executes; `git bundle list-heads` names the
  real ref in one command.
- **`smoke_5b.py --record` defaults to `results/serving_5b.json` — the pod's cost anchor** ($0.5993/1000,
  $0.4611/pass, 4.071 s/row). Always pass an explicit path.
- **RunPod's request policy is in MILLISECONDS and every briefing writes seconds.**
  `serving.execution_policy(3600, 7200)` is the one conversion point; the endpoint's own
  `--execution-timeout` takes **seconds** and stores ms. Set the endpoint-level timeout too.
- **`assert_runtime_matches` pins three libraries and cannot be taught a fourth.** It skips any library
  the frozen anchor (`results/verdict_45h2.json`) does not carry, so adding `peft` would pass every test
  and never fire. peft's pin lives in `scripts/runbook_srv2b.md` (**0.20.0**) and the version is merely
  REPORTED by `serve_handler.library_versions()`.
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
