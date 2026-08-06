<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-08-06 19:38:12 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
2f350f4 docs(vault): 5b.2 at the checkpoint — batch closed by rule, run-rate back to the operator
cb41ae3 docs(5b2): the ADR with its numbers, and twelve deviations
9295e3c feat(5b2): the ladder says every N is identical; the paid run at 16 dies on memory
0a0e09c docs(5b2): check the stack string before the 59 GB, not after it
00b82ac feat(5b2): regress batch 1 against the 5b.1 smoke, and the runbook's pre-registered rulings
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `5b2-batch-measurement.md` — 5b.2 — the batch measurement failed on memory, and serving is fixed at batch 1
- `5b-parity-abort-and-pod-runtime.md` — The pair aborted on a runtime that never took a job, and production moves to a stop-after pod

## 📅 Recent daily logs

- `2026-08-06.md`
- `2026-08-05.md`
- `2026-08-04.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->

# Hot Cache — curated

**Last update:** 2026-08-06 19:45 (**PHASE 5b.2 IS DONE AND THE MEASUREMENT FAILED — the paid run at batch 16 scored 666 of 758 rows and the GPU ran out of memory, so serving is fixed at batch 1 PERMANENTLY and the run-rate question goes back to the operator.** SPEC §3.11 (2)'s own outcome, applied rather than re-argued: the adoption rule needs G1b, G1b needs the sarcasm holdout, and 16 of its 108 rows were scored. 7 commits, `cf381e2` → `cb41ae3`. `make check` **1028 passed** (989 at the 5b.1 close), `ruff format --check` clean, **$1.7069 of the $4.00 stop — $2.29 unspent**, pod deleted and proven gone by listing. The ladder found **every** N byte-identical on the 24-row carve, including 16 — which is what selected 16, and which the 758-row test set contradicted: **six rows moved**. The phase's real finding is that a 24-row pre-filter cannot see a 1% effect, and that a selection rule with no memory term picks a batch size nobody checked would fit. Previously, 18:04 `/save`: **5b.1 DONE, SERVING DELTA ZERO** — config A on a booted-per-pass A6000 pod reproduced every reported 4.5h2 number exactly, 758/758 rows, $1.2324 of the stop; and a 45-minute $0 A6000 stock-out closed by the operator's capacity clause, which made the GPU CLASS the contract and the datacenter a convenience. Before that: **5b DONE, THE PAIR NEVER SCORED** — no worker on this account consumes a job, RunPod's own hub vLLM worker included, so A ships and merging stays forbidden. Edited by hand; the section above is auto-generated, do NOT touch the marker.)

## 🔥 What's Hot

**BATCH IS CLOSED AND IT IS CLOSED BY THE RULE, NOT BY THE NUMBERS.**
`results/batch_5b2_verdict.json` → `outcome: failed-measurement-oom`. The adoption rule adopts N
only if every 4.5h2-passed gate stays passing — G1b, G1d, G1e — and G1b is the sarcasm-holdout
slice, of which the run scored 16 of 108. An unmeasured gate is not a passing one, so the rule has
no input and does not run. **Batch 1, permanently.** Only a NEW pre-registered measurement can move
it. One attempt, no retry, no second N, and test v4 is spent. [[5b2-batch-measurement]]

**THE PRE-FILTER SAID IDENTICAL AND THE TEST SET SAID 1%.** All four ladder arms — 16, 8, 4 and a
repeat of 1 — came back byte-identical to batch 1 over the 24 carve rows. On 758 test rows,
**660 of 666 agree**: `posts_test` 250/250, `comments_test` 396/400, `sarcasm_holdout` 14/16. Six
rows moved that the carve swore could not. A 24-row sample cannot see a 1-in-100 effect, and
"byte-identical on the carve" was never evidence about the population.

**A DISCRIMINATOR EVERYTHING PASSES IS NOT A SELECTION RULE.** With 16, 8 and 4 all identical,
"the largest byte-identical N" quietly became "take the maximum" — and nothing in the rule asked
whether the maximum fits in memory. It did not: 1.85 GiB requested, 432 MiB free, **42.14 GiB
genuinely allocated** against a ~20 GiB model. The carve's longest batch fitted; the test set's
did not. Any re-opening carries N=8, a memory term, and `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`.

**THE MONEY FORK, WITH ITS THIRD LINE.** Batch 1 = **$27.67/mo** GPU at 2 passes/day (4.071 s/row,
3 132 s/pass). Batch 8 = **$10.39/mo** — *projected from the ladder, NOT measured*. SPEC §3.11 (6)
ceiling = $9–12. And the CA-MTL-3 volume bills **~$7.20/mo attached to nothing**, which is more
than the entire batch-8 GPU bill; 5b.1 proved fresh staging beats it on money and cold start both.
Two decisions, not one, and neither is the executor's.

**WHAT 5c READS NOW SAYS BATCH 1 OUT LOUD.** `results/serving_5b.json` → `adopted`:
`batch_size: 1`, `adopted: false`, `measured_at_batch_size: 16`, **$0.5993/1000 rows**,
**$0.4611/pass**, cold start 46.2 s (local NVMe; 278.9 s off the network volume). Written by
`salvage_5b2.py`, beside the 5b.1 smoke and its cost block, never over them.

**THE GUARD THAT WOULD HAVE COST A COLD START.** The runbook's first draft installed
`torch==2.8.0` from PyPI and checked the stack at the first `info` — after 59 GB and a load. A
PyPI wheel can report `2.8.0` with no `+cu128`, and `assert_runtime_matches` compares exactly. The
image already carries the right build: `venv --system-site-packages`, no torch in the pip line,
assert BEFORE the download. It passed first try.


**THE SERVING DELTA IS ZERO, AND THAT IS MEASURED RATHER THAN ASSUMED.** `results/parity_5b_a.json`
→ block `parity`: config A on a booted-per-pass A6000 pod, **758/758 rows**, zero parse, api,
generation and truncation failures, one attempt, batch 1, no retry. G1a 0.9214, G1b 0.6053 (23/38),
G1c 0.8478, G1d 0.9586, G1e 0.9610 — **every one identical to the 4.5h2 anchor**, both G1a language
floors too, `under_bar` empty, the same 3 of 5 gates passing. **Serving through `serve_handler` over
HTTP costs the gate numbers nothing**, and SPEC §3.11 (2)'s "the delta is reported, never averaged
away" has a number to report: `+0.0000`.

**THE PREMISE IS QUOTED, AND SO IS THE LIMIT.** Batch 1 on both sides comes from
`config.generation.batch_size` in **both** records (greedy is not batch-invariant on this stack —
ADR [[phase4-own-pod-anchor]] §(c)), and `scored_ids_sha256` matches on all three inputs, so it is
the same rows proven by hash. What cannot be claimed: a **per-row** identity. Arm A's prediction
dump was lost on 04.08 (`results/predictions/LOST.md`, and it may not be regenerated), so
"identical" means seven aggregates over a hash-pinned row set, not 758 verified rows. D12.
5b.1's own 758-row dump is committed — the next runtime comparison will not have this hole.

**THE GPU CLASS IS THE CONTRACT AND THE DATACENTER IS NOT** (SPEC §3.11 (1) capacity clause,
operator 2026-08-06 evening). A6000 in any datacenter is the primary path with
`assert_runtime_matches` as the gate on a fresh stage; **A40** is the authorised in-class fallback
with the card recorded in provenance; **A100 is refused** — the GPU class is the variable §(2)
measures. It was written after a $0, 45-minute stock-out: 31 refused `pod create` calls in
CA-MTL-3 while **`runpodctl gpu list` had said `none` for A6000 there all along**. `datacenter
list` prints `""` for everything and is the field 5b's runbook says not to trust; `gpu list` has a
per-datacenter sibling that does answer. The ladder took **A6000 in US-TX-1** on its second rung.

**A FRESH STAGE IS CHEAPER THAN THE VOLUME, AND FASTER TO LOAD FROM.** No network volume outside
CA-MTL-3, so 59 GB of weights came down in **4 m 15 s** and the venv was rebuilt with the 4.5h2
versions **pinned by hand** — and the cold start off local NVMe was **53.0 s against 278.9 s** off
the volume. `assert_runtime_matches` is what says the rebuild is the same instrument, and it passed
before the first scored row: same card, same driver 550.127.08, same CUDA 12.8, torch 2.8.0+cu128,
transformers 5.14.1, bitsandbytes 0.50.0. The 100 GB volume now buys convenience in one datacenter
that had no A6000 capacity that day, and it bills ~$0.24/day regardless.

**A POD HAS NO TEMPLATE, SO IT HAS NO CONFIGURATION.** `SERVING_CONFIG`, `ADAPTER_DIR`,
`BASE_WEIGHTS` and `MODEL_REVISION` were the serverless endpoint template's `--env`. The first pod
start refused with `SERVING_CONFIG must be one of ('A','B'), got ''` — for free, because `Worker`
loads the model lazily and `settings()` runs first. **5c inherits it:** whatever boots the pod per
pass is now the thing that carries the worker's environment.

**WHAT 5c SIZES OFF.** Cold start **53.0 s**, **4.065 s/row** at batch 1 (`wall_per_call`, 759
calls), **3085.4 s** of rows against **3110.1 s** projected (−0.8%, so the task-mix weighting
holds), a full cold pass **≈3138 s**, **$0.60 per 1000 rows**. Two passes a day is **~$28/month of
GPU** against SPEC §3.11 (6)'s ~$9–12/month ceiling — see ⏭️ Next 1.

**THE 5b PAIR WAS NEVER SCORED, AND THAT IS A VERDICT RATHER THAN A GAP.**
`results/parity_verdict_5b.json` → `outcome: aborted-runtime-unreachable`, **shipped A**, seven
observations as evidence. SPEC §3.11 (2) fixes it: *a failed or aborted pair closes the merge
question in favour of A; no retry*. **Merging stays forbidden** — it is adopted only if this
measurement selects it, and the measurement did not happen. Not one number in
`results/verdict_45h2.json` is touched and `run_loop.ENDPOINT` is still `None`.

**THE BLOCKER IS RUNPOD'S, NOT OURS, AND THE HUB WORKER IS WHAT PROVES IT.** Five endpoints
across four configurations left their jobs `IN_QUEUE` while `/health` reported a worker. Then
**RunPod's own hub vLLM worker** — their template, their image, a 0.5 B model reference, no
network volume, no datacenter pin, none of this project's code — cycled `initializing` ⇄
`throttled` for five minutes and never consumed its job either. That single control cost about
five cents and turned "our handler is broken" into "serverless is unreachable on this account".
The counter-proof sits beside it: the same code, venv, weights and adapter answered correctly on
an A6000 **pod** through the identical `start.sh` entrypoint — **278.9 s cold start**, `info`
naming `b3ca630846c7…`, and «Рудь … знижка 20%» → `launch`, «Акція на молоко Яготинське» →
`promo`, «Графік роботи» → `relevant: false, other`.

**SERVERLESS CAPACITY IS PER (DATACENTER × GPU CLASS), AND A NETWORK VOLUME PINS THE DATACENTER.**
In CA-MTL-3, where the volume lives, only **`ADA_24`** allocates a worker at all — `AMPERE_48`,
`ADA_48_PRO` and `AMPERE_80` allocate nothing. The same `AMPERE_48` class with **no volume and no
DC pin** allocated in 25 s, so it is regional capacity and not the endpoint config. `network-volume
create` refuses **US-KS-2** outright: only 18 datacenters take volumes at all. No second volume was
created — that would be ~$7/month more against SPEC 3.11 (6)'s ~$9–12/month ceiling, and it is the
operator's call.

**THE VOLUME ALREADY HELD WHAT MAKES CONFIG A A REPLICA.** `gfwa2an8fn` carries Phase 4a's HF cache
— `google/gemma-4-31b-it` at the pinned `842da379…`, 59 GB — and a venv with **exactly** the stack
`results/verdict_45h2.json` names: torch 2.8.0+cu128, transformers 5.14.1, bitsandbytes 0.50.0.
Only `peft` and `runpod` had to be added. A fresh install would have pulled today's releases and
quietly made config A a different instrument, which is why `serving.assert_runtime_matches` exists
— and why it deliberately does **not** pin the GPU: which card the worker gets IS the delta 5b
reports.

**THE COMBINED LEDGER IS IN, AND WIDENING DID NOT CLOSE THE GAP.** `results/discovery_5a1.json`:
seven themes and seven seed handles, **180 candidates** (114 checked in 5a.1, 66 carried from
`results/discovery_5a.json` unmeasured), no FloodWait, `scan_complete: true`. They add
**1,427,767** subscribers to the registry's **178,274** — **1,606,041 against a target of
10,000,000, still 8,393,959 short**. That is **14.5%** of the gap closed, against 5a's 6.8%:
four more themes and the seed list roughly doubled the reach and left 8.4 M outstanding. Taking
only the **90** candidates that posted in four weeks leaves **8,749,263**. **53** both post and
carry a discussion group — 571,904 subscribers, and the only rows that can ever become comments.
**The team lead's own survey says the whole segment is ~4–5 M**, so the target is about six times
what a scan can reach. **Ruled the same evening: the target stands, and 51 channels launch** — see ⏭️ Next 1.

**What the per-theme table says** (`ledger.per_theme`, priced per `found_by` tag): **7 handed
seed handles (411,399) beat six of the seven searched themes** — `@recepti` 115,783 at 50
posts/week could never surface through a ranked, capped search. **health_fitness, authorised
against the team lead's recommendation, is not the worst theme**: 81,490 subscribers, **17 with
a discussion group, 10 of which also post — second only to cooking_recipes' 12**. **food_quality is the
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

1. **THE RUN-RATE DECISION IS BACK WITH THE OPERATOR, AND THE ONE LEVER WAS TRIED AND LOST.**
   Batch > 1 was authorised, measured and **failed**: the paid run at 16 died on GPU memory with
   G1b unmeasured, so SPEC §3.11 (2) fixes serving at batch 1 **permanently** — only a new
   pre-registered measurement may move it. What that leaves on the table, all of it the operator's
   call and none of it started here: **(a)** authorise a fresh batch measurement at **N=8** with a
   memory term in the rule and `expandable_segments:True` — projected **$10.39/mo**, inside the
   ceiling, and 660/666 row agreement says the answers survive batching — but whether 8 FITS is
   an INFERENCE from the batch-16 OOM, not a measurement, and this phase's finding is that a
   24-row ladder underestimates the population; **(b)** fewer passes a day
   (the cadence is a recorded knob, not a constant); **(c)** a smaller v4 slice per pass;
   **(d)** delete or resize the CA-MTL-3 volume, which bills **~$7.20/mo attached to nothing** and
   is the single biggest line against a $9–12 ceiling. Today: batch 1 = **$27.67/mo**.
2. **`docs/PROMPT-5b1.md` IS EXECUTED — the measurement exists and the line is not stopped.**
   10 commits `c878e7b` → `4c43d5e`, `$1.2324` of the $4.00 stop. SPEC §3.11 (2)'s
   *"aggregates cannot take serving numbers without this measurement"* is satisfied:
   `results/parity_5b_a.json` carries the per-head numbers beside the anchors with the deltas, and
   `results/serving_5b.json` carries the pod config, the cold start, per-row latency and cost —
   the file the brief says 5c reads. `run_loop.ENDPOINT` is **still `None`**; 5c flips it.
3. **The serverless ticket is still worth filing, at zero cost and blocking nothing.** The pod
   runtime is measured and reproduces the anchor exactly, so nothing waits on it. If serverless
   ever comes back it needs a fresh §(2) measurement, and `results/parity_5b_a.json` is what that
   would be compared against. The hub-worker observation is the ready-made ticket.
4. **The three readings 5b handed over are ANSWERED — kept here for the record.**
   Three readings, cheapest first, all in `implementation-notes.md` "Phase 5b": **(a)** ask RunPod
   why serverless workers never consume jobs on this account — costs nothing, and the hub-worker
   observation is a ready-made ticket; endpoints were created through `runpodctl serverless
   create`, and the web console may take a different path, which is the first thing worth trying
   by hand. **(b)** ship config A **on a pod** and re-word what "production runtime" means — the
   artifact is proven to serve, the loop runs twice a day rather than continuously, and a pod with
   `--stop-after` is dearer per hour and cheaper per phase; this changes SPEC 3.11 (1)'s serving
   assumption and is not this phase's call. **(c)** leave the merge question closed and go to 5c —
   SPEC already fixes the outcome, nothing downstream waits on config B, and the **$3.47 left
   under the 5b stop stays unspent**.
5. **Before staging anything on a re-attempt, run the hub control first.**
   `runpodctl hub search vllm` → create → one job → delete, either way. If RunPod's own worker
   completes, `scripts/runbook_5b.md` §3–6 can run as written; if it does not, nothing in this
   repository can make it. §1–2 of that runbook are marked DONE and the volume still holds their
   output — the staging half does not need repeating.
6. **THE COVERAGE RULING IS TAKEN — and neither of the notes' cheap readings was taken whole.**
   Landed during this `/save` in an amended SPEC §3.11 (4) plus `docs/CHANNELS-launch.md`: the
   **≥10 M target STANDS as aspirational** (the ledger keeps reporting the honest gap), and the
   launch is fixed at **51 channels** — registry 4 + 29 comment-capable + 18 posts-only,
   **1,199,519 subscribers** — plus **14 watch** (group present, currently silent: track-R
   passed, posts collected, **no group joins until the channel posts again**, reviewed after
   cycle 1). 12 of the operator's 77 picks excluded (7 off-topic/non-UA, 6 dead, one overlap),
   one late addition `@marketopt_official` (41,518, Poltava/Kremenchuk grocery chain).
   `docs/CHANNELS-launch.md` is the authoritative per-channel list; every entry still goes
   through the track-R gate.
7. **`docs/PROMPT-5b.md` IS EXECUTED — this was the phase's one paid event, and it aborted.** SPEC §3.11 (2) as
   amended pre-registers the pair — config A = NF4 base + unmerged arm-A adapter at batch 1
   (the 4.5h2 replica), config B = merged in bf16 then **requantized** to NF4 (bf16 does not fit
   the GPU class: ~62 GB of weights against 48) — both scored once on test v4 through the
   PRODUCTION serverless runtime, **hard stop $4 of the $8 cap**, spend anchors before the first
   spend, **no retry**. Selection rule committed before the run: B is adopted only if every
   4.5h2-passed gate stays passing and no head drops more than 0.005; any tie or doubt ships A,
   and an aborted pair closes the merge question in favour of A.
   **⚠️ Its step 0 pre-authorises the vault tail as its OWN separate commit** — exactly the
   judgement D1 took here, now the house rule; STOP only for a path neither list explains.
8. **The ten-key finding is now load-bearing.** `docs/CHANNELS-launch.md` counts **views and
   reactions** among the launch signals and stars both: collector v1 writes neither (the post
   record has exactly ten keys, measured in 5a). The stated plan is a retrospective refetch **by
   the poll-census pattern** — $0, sidecar v2 beside raw v1, never into the v1 stores.
9. **A brief count to watch, now FOUR times — and SPEC now names one of them:** `docs/PROMPT-5a1.md` said "the five themes" in its read-back
   check while its own Deliverable 3 and SPEC §3.11 (4) name **seven** (three from 04.08 plus
   four from the 06.08 ruling). Seven were built; the discrepancy is D2 in the notes. The same
   class of staleness as the "five registry channels" 5a flagged — twice in two days.
10. **5c IS NEXT — the loop core.**
   + aggregates + the category post-layer (taxonomy is the operator's word BEFORE any labeling)
   → **5d** first reporting cycle + alerts v0 on spikes of both polarities.
11. **G1a and G1c are DEFERRED until after the loop's first reporting cycle**, on its fresh data —
   which is also the only new source of ru rows for G1a and of sarcasm for G1b, the old corpus
   having been exhausted at 4.5d. Whatever is decided then starts a **new pre-registration**.
12. **Budgets for Phase 5 are pre-registered: $8 GPU + $1 OpenRouter**, run-rate ceiling ~$9–12/mo.
   Spend anchors are written before the first spend. The 100 GB CA-MTL-3 volume is kept — review
   **~2026-09-05** if no GPU work has started by then.

## 🚧 Blockers
**NOTHING BLOCKS 5c's CODE. What is open is a money decision, not a fault.** Serving is fixed at
batch 1 by SPEC §3.11 (2), `results/serving_5b.json` → `adopted` carries the numbers 5c sizes off,
and every gate number the loop needs exists. The open item is whether **$27.67/mo** of GPU is
acceptable against a **$9–12** ceiling, and that is ⏭️ Next 1 — an operator ruling, not a blocker
this executor can clear. Starting 5c against a batch-1 run rate is a decision; so is authorising
another measurement first.


**NOTHING BLOCKS THE LINE. The one external fault is routed around and no longer stops anything.**
No RunPod serverless endpoint on this account reaches a job-consuming worker — jobs stay
`IN_QUEUE` while `/health` reports a worker in `idle`, `ready`, `running` or `throttled`; proven
not to be ours by RunPod's own hub vLLM worker failing the same way, and proven not to be the
artifact by the same code answering correctly on a pod. **SPEC §3.11 (2)'s measurement is no
longer blocked by it:** the runtime ruling moved production to a stop-after pod, and 5b.1 scored
config A there — every reported number identical to the anchor. Serverless returns only through a
fresh §(2) measurement, and the ticket costs nothing and waits on nothing (⏭️ Next 3).

**A capacity stock-out is a thing that happens and it is now in the contract.** A6000 was `none`
in the volume's datacenter for 45 minutes and 31 `pod create` calls, at $0. SPEC §3.11 (1)'s
capacity clause makes the CLASS the contract: A6000 anywhere, then A40 in-class with the card in
provenance, never A100. **`runpodctl gpu list` is the field that answers** — per-datacenter, and
it said `none` the whole time; `datacenter list` prints `""` for everything and is the one 5b's
runbook says not to trust. Read the granular sibling before spending a create call.

**Everything else stays clear.** The two owed amendments are **PAID** — `docs/SPEC.md` amendment **3.10** records the
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

**The 5a.1 open question is ANSWERED, not just tolerated:** `docs/PROMPT-5b.md`'s own step 0
pre-authorises the vault tail as its own separate commit, so `8a4582d`'s shape is now the house
rule and 5b's `382b755` follows it by instruction. For the record, the question was whether
`8a4582d` should have existed at all. `docs/PROMPT-5a1.md`'s step 0 says STOP if `git status` shows anything beyond its six paths;
it showed eight, the extra two being this session's own operator-invoked `/save`. The phase ran
to completion and the two files went into their own commit, separable from the team lead's
`f650ce1`, so reversing that judgement costs one `git revert`. D1 in the notes.

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
