<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-08-06 12:19:38 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
03915ad feat(5a.1): discovery widened to seven themes plus seed handles, with per-theme subtotals
260463d docs(adr): 5a — the census had to fetch, and three themes buy 6.8% of the gap
303ef9f fix(5a.1): the six acceptance items — a rate limit is a wait, a smoke keeps its deliverable
8a4582d docs: the /save checkpoint of 2026-08-06 — hot.md and the day's log
f650ce1 docs: 5a accepted — SPEC 3.11 (4) amended to four channels and seven themes, PROMPT-5a1
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `5a-census-api-and-theme-expansion.md` — The census had to fetch, and three themes buy 6.8% of the gap
- `45h2-ablation-verdict.md` — The пласт is dropped: it made every gated head worse but one

## 📅 Recent daily logs

- `2026-08-06.md`
- `2026-08-05.md`
- `2026-08-04.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->

# Hot Cache — curated

**Last update:** 2026-08-06 (**5a.1 IS BUILT AND COMMITTED — the combined ledger is on disk and the coverage-target ruling is now the operator's to take (see Next).** Six commits: `f650ce1` the team-lead tail · `8a4582d` this checkpoint's two files, kept out of that commit · `303ef9f` the six acceptance fixes · `260463d` the owed ADR · `03915ad` the widened discovery · plus the record. `make check` **884 passed** (863 at the 5a close), `ruff format --check` clean, `shasum -c results/raw_v1_baseline.sha256` **6/6 OK after the scan**. **$0** — no GPU, no serverless, not one model call; the whole scan is Telegram's free API. Earlier the same day, `/save`: **5a WAS BUILT, COMMITTED AND ACCEPTED.** Four commits: `242fcdc` the team-lead tail (six paths, `hot.md` the expected sixth) · `15723c1` the three deliverables · `81c25ea` this file · `5f1b571` the `--rebuild-ledger` test and the provenance check. All three deliverables done at **$0** — no GPU, no serverless, not one model call. `make check` **863 passed** (814 before), `ruff format --check` clean, raw v1 byte-identical against a sha256 baseline taken BEFORE the first fetch. **The ledger's verdict: the three authorised themes close 6.8% of the gap** — that is the operator's decision now. The session opened 05.08 at 21:55 and crossed midnight, so its checkpoint is in [[2026-08-06]] while the 4.5 close and the Phase 5 briefing stay in [[2026-08-05]]. Phase 4+4.5 spend unchanged: **$16.30 of $25**, $8.70 left; no pods. Edited by hand; the section above is auto-generated, do NOT touch the marker.)

## 🔥 What's Hot

**THE COMBINED LEDGER IS IN, AND WIDENING DID NOT CLOSE THE GAP.** `results/discovery_5a1.json`:
seven themes and seven seed handles, **180 candidates** (114 checked in 5a.1, 66 carried from
`results/discovery_5a.json` unmeasured), no FloodWait, `scan_complete: true`. They add
**1,427,767** subscribers to the registry's **178,274** — **1,606,041 against a target of
10,000,000, still 8,393,959 short**. That is **14.5%** of the gap closed, against 5a's 6.8%:
four more themes and the seed list roughly doubled the reach and left 8.4 M outstanding. Taking
only the **90** candidates that posted in four weeks leaves **8,749,263**. **53** both post and
carry a discussion group — 571,904 subscribers, and the only rows that can ever become comments.
**The team lead's own survey says the whole segment is ~4–5 M**, so the target is about six times
what a scan can reach. **The coverage-target ruling is the operator's, on this ledger.**

**What the per-theme table says** (`ledger.per_theme`, priced per `found_by` tag): **7 handed
seed handles (411,399) beat six of the seven searched themes** — `@recepti` 115,783 at 50
posts/week could never surface through a ranked, capped search. **health_fitness, authorised
against the team lead's recommendation, is not the worst theme**: 81,490 subscribers and **17
comment-capable channels, more than any theme but cooking_recipes**. **food_quality is the
smallest and none of it can carry comments**: 6 candidates, 3,387 subscribers, **0** discussion
groups — the regional Держпродспоживслужба offices are broadcast-only. The ledger priced a theme
the recommendation would have dropped and a theme the operator added, in opposite directions.
And the two biggest candidates are dormant: `@itsmamix` (280,895, silent) and `@tretyakovaele`
(244,639, one post in 28 days) are **37% of all candidate subscribers**.

**The registry has FOUR channels, not five** — `@znizhki_ua` was dropped 2026-07-27 (dead since
2024-03). 5a flagged it without editing a team-lead file, and the **06.08 amendment to SPEC
§3.11 (4) now says four**. The ledger summed four from the start.

**THE POLL PAYLOAD WAS NEVER ON DISK.** The brief's Deliverable-2 premise is false: a v1 post
record has ten keys and none is a poll, and 4.5g2 read its sixteen transcripts from a **live**
fetch. So the census re-read the 815 text-less ids from Telegram ($0 — the API is free) and wrote
`data/raw/post_polls.jsonl` beside v1. **37 polls of 815 (4.54%)** — *not* a continuation of
4.5g2's 16/41, which counted one sitting pack of one channel. All 16 old rows reproduce
**byte-identically**; the rest are 758 photo · 16 video · 2 giveaway · 1 voice · 1 document, and
zero are gone from Telegram.

**The loop refuses to run live in 5a, by design.** `scripts/run_loop.py --once` without a dry flag
exits 1: a live pass would append to the raw v1 store, which the brief forbids. The dry pass over
all four channels reports **0 threads to fetch and 11,338 rows queued for inference** — the corpus
total, arrived at independently. The spend guard (`loop.inference_refusal`) **defaults closed** and
opens the moment `run_loop.ENDPOINT` stops being `None`: that is 5b's one-constant change.

**Two honesty clauses ride with the coverage ledger and are printed verbatim in the record:**
*summed subscribers != unique reach* (overlap is unmeasurable from the API) and *subscribers !=
comment flow* (rows are born in discussion groups) — the brief's ASCII spelling, not SPEC's `≠`.
Discovery yielded **candidates only**: `config/registry.yaml` is untouched, and a new channel
enters through the track-R gate by the operator's choice.

**The deliverable Phase 5 inherits is one artifact: the NF4 base plus the UNMERGED arm-A adapter**
(`b3ca6308…`, `results/train/45h2-arm-a/`, dataset `ba368273cc4d…`, 2 171 rows, rendering
`T1v2_with_post`, every eval at batch 1). **Merging stays forbidden until 5b's serving-parity
measurement selects it** — SPEC 3.11 (2) pre-registers that the exact production configuration is
scored once against test v4 before any serving number reaches an aggregate, and the delta is
reported, never averaged away.

**The gates are 3 of 5 and CLOSED, not pending** — G1a FAIL (0.9214 / bar 0.9470, ru floor also
fails), G1b PASS 23/38 exactly on the bar, **G1c FAIL by 0.0005**, G1d and G1e PASS. The full table
with the ceilings is in STATUS «Модель сейчас»; the reasoning is ADR [[45h2-ablation-verdict]].
No bar moves and nothing is re-run: a failed gate closes its question.

**ARM A'S PER-ROW DUMP IS LOST** — `results/predictions/LOST.md`. No gate number moves and
`scored_ids_sha256` still proves which rows were scored; what is gone is the **re-score**, so a
future corrected-gold comparison of the two arms is **unpaired and must say so**.

## ⏭️ Next

1. **THE COVERAGE-TARGET RULING IS OWED, AND THE LEDGER IT WAS DEFERRED TO EXISTS.** Three
   readings are laid out in `implementation-notes.md` §«Phase 5a.1», cheapest first: **(a)
   launch on the registry four and let the 14-day cycle price the question** — costs nothing,
   6,057 posts and 11,338 comment rows are already in the store and have never been through the
   loop, and it is the only option that can falsify the premise; **(b) enter the 53 candidates
   that both post and carry a discussion group** (571,904 subscribers, 53 track-R gates);
   **(c) move the target** — 10 M is ~6× what discovery can reach and ~2× the whole segment.
   Not this executor's call.
2. **A brief count to watch:** `docs/PROMPT-5a1.md` says "the five themes" in its read-back
   check while its own Deliverable 3 and SPEC §3.11 (4) name **seven** (three from 04.08 plus
   four from the 06.08 ruling). Seven were built; the discrepancy is D2 in the notes. The same
   class of staleness as the "five registry channels" 5a flagged.
3. **After 5a.1:** **5b serving parity** (the merge/batch measurement above) → **5c** loop core
   + aggregates + the category post-layer (taxonomy is the operator's word BEFORE any labeling)
   → **5d** first reporting cycle + alerts v0 on spikes of both polarities.
4. **G1a and G1c are DEFERRED until after the loop's first reporting cycle**, on its fresh data —
   which is also the only new source of ru rows for G1a and of sarcasm for G1b, the old corpus
   having been exhausted at 4.5d. Whatever is decided then starts a **new pre-registration**.
5. **Budgets for Phase 5 are pre-registered: $8 GPU + $1 OpenRouter**, run-rate ceiling ~$9–12/mo.
   Spend anchors are written before the first spend. The 100 GB CA-MTL-3 volume is kept — review
   **~2026-09-05** if no GPU work has started by then.

## 🚧 Blockers

**None open.** The two owed amendments are **PAID** — `docs/SPEC.md` amendment **3.10** records the
per-arm ceiling 6.5 h → 8.5 h and `max_seq_len` 1024 → 1408, with the recording delay admitted in
its own text. `docs/STATUS.md` **has caught up with the briefing**: it was still the acceptance
document when this session began (Phase 5 `⏸`, the briefing listed as upcoming) and the team lead
refreshed it the same day, so the gap flagged at step 0 is closed. Both pods are deleted and
`runpodctl pod list -a` is empty.

**The three stalenesses 5a flagged are ANSWERED by the 06.08 tail, not by this executor.** The
amended SPEC §3.11 (4) now says the registry is **four** channels, and STATUS was refreshed with
it. What 5a reported and the tail did not have to fix: PROMPT-5a's Deliverable 2 heading said
"$0, no API" on a premise that turned out false — the deliverable needed the (free) Telegram API
and `$0` still held. Team-lead files were never edited here.

**Nothing else is open.** The prompt-revision blocker of 04.08 was ruled the same day (with the
post, both sides), the anchor was scored through it once, and every record now names its rendering.
Both pods are deleted and `runpodctl pod list -a` is empty; what still accrues is the 100 GB
CA-MTL-3 volume, which bills whether or not a pod exists.

## ⚠️ Footguns for the next run

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

**Never `git add -A` here.** `docs/PROMPT-5a.md` is sitting untracked in the tree right now, and
`docs/SPEC.md` / `docs/STATUS.md` are modified by the team lead. Stage by path. The same trap has
fired with every queued prompt since `docs/PROMPT-4.5g4.md`.

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
- **Greedy decoding is NOT batch-invariant on bitsandbytes NF4 + A6000** — measured 2026-08-01, one
  row of 24 flipped its intents between batch 8 and batch 1. Every gate run goes at `--batch-size 1`
  until someone re-measures and records the result. Batch 1 is run-to-run identical, also measured.
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
