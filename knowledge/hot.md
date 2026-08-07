<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-08-07 10:38:48 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
9be36e4 fix(5b2): the verdict names the commit that produced its rows
2f350f4 docs(vault): 5b.2 at the checkpoint — batch closed by rule, run-rate back to the operator
cb41ae3 docs(5b2): the ADR with its numbers, and twelve deviations
9295e3c feat(5b2): the ladder says every N is identical; the paid run at 16 dies on memory
0a0e09c docs(5b2): check the stack string before the 59 GB, not after it
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

**Last update:** 2026-08-07 10:38 (`/close` of a day in which **nothing was executed** — zero
commits, zero files touched, zero spend; the tree carries **six** uncommitted paths — the 06.08
close's five plus this day's own log — and the next step is still the **5c contract briefing**. Everything below is unchanged
from that close and still current. Previously, 2026-08-06 19:57: **the serving-parity programme is
CLOSED — 5a → 5a.1
→ 5b → 5b.1 → 5b.2 in one day, $1.7069 of the $4.00 stop, 40 commits `f650ce1` → `9be36e4`,
`make check` 814 → 1028 passed.** The runtime is a stop-after A6000 pod and it costs the gate
numbers **nothing** (Δ 0.0000, 758/758); batch > 1 was authorised, measured and **failed by its own
rule**, so serving is batch 1 **permanently**; and the operator ruled the cycle-1 economics the
same evening, so the money question is **answered, not open**. Next session is the **5c contract
briefing** — see ⏭️ Next 1. This block is hand-edited; the section above it is auto-generated, do
NOT touch the marker.)

## 🔥 What's Hot

**WHAT 5c READS, AND IT SAYS BATCH 1.** `results/serving_5b.json` → `adopted`: `batch_size: 1`,
`adopted: false`, `measured_at_batch_size: 16`, **$0.5993/1000 rows**, **$0.4611/pass**,
**4.065 s/row**, cold start **46.2 s** off local NVMe (278.9 s off the network volume). Beside it,
`results/parity_5b_a.json` → `parity`: config A on a booted-per-pass A6000 pod, **758/758 rows**,
zero failures of any kind, and **every reported number identical to the 4.5h2 anchor** — G1a
0.9214, G1b 0.6053, G1c 0.8478, G1d 0.9586, G1e 0.9610, `under_bar` empty, the same 3 of 5 gates.
SPEC §3.11 (2)'s "the delta is reported, never averaged away" has a number: **+0.0000**.
What cannot be claimed is a **per-row** identity — arm A's dump was lost 04.08 (D12).

**BATCH IS CLOSED BY THE RULE, NOT BY THE NUMBERS.** `results/batch_5b2_verdict.json` →
`outcome: failed-measurement-oom`. The paid run at 16 scored 666 of 758 rows and the card ran out
of memory; the adoption rule needs every 4.5h2-passed gate to stay passing, G1b is the sarcasm
holdout, and 16 of its 108 rows were scored. An unmeasured gate is not a passing one, so the rule
has no input. **Batch 1, permanently** — only a NEW pre-registration can move it, carrying N=8, a
**memory term** in the rule and `expandable_segments:True`, **and the team lead does not recommend
it**. [[5b2-batch-measurement]]

**THE PRE-FILTER SAID IDENTICAL AND THE TEST SET SAID 1%.** All four ladder arms came back
byte-identical to batch 1 over 24 carve rows; on the test set **660 of 666 agree**. Six rows moved
that the carve swore could not, and a discriminator everything passes had quietly become "take the
maximum" — with no memory term in it. That is the phase's real finding, and it is a lesson about
pre-filters, not about batching.

**THE MONEY QUESTION IS ANSWERED** (operator 06.08, SPEC §3.11 (6), STATUS decision 22): the
inference backlog is scored as a **WINDOW** — the most recent ~4 weeks (**~$2–2.5**) at the 5c
start, the full 11,338-row history a **visibly deferred** decision taken only if a use-case demands
it; cycle 1 runs **2×/day**; the **permanent** ceiling is set AFTER cycle 1 on its measured daily
row flow (**the $9–12 figure was written for per-second serverless and is not the ruling**); and
volume-vs-redownload-vs-stopped-pod is a **$0 step-0 calculation of 5c** that also decides the
CA-MTL-3 volume's fate, advancing the ~2026-09-05 review.

**THE LAUNCH SET IS FIXED AT 51 CHANNELS + 14 WATCH.** `docs/CHANNELS-launch.md` is authoritative:
registry 4 + 29 comment-capable + 18 posts-only, **1,199,519 subscribers**; the 14 watch channels
have a group but are silent — track-R passed, posts collected, **no group joins until the channel
posts again**. The **≥10 M target STANDS as aspirational** and the ledger keeps reporting the
honest gap: 180 candidates closed **14.5%** of it, and the team lead's own survey puts the whole
segment at **~4–5 M**, so the target is about six times what any scan can reach. Every entry still
goes through the track-R gate.

**THE ARTIFACT PHASE 5 SERVES IS THE NF4 BASE PLUS THE UNMERGED ARM-A ADAPTER** (`b3ca6308…`,
dataset `ba368273cc4d…`, 2 171 rows, rendering `T1v2_with_post`, every eval at batch 1).
**Merging stays forbidden** — SPEC §3.11 (2) adopts it only if a measurement selects it, and 5b's
pair aborted, which closes the question in favour of A. [[5b-parity-abort-and-pod-runtime]]

**THE GATES ARE 3 of 5 and CLOSED, not pending** — G1a FAIL (0.9214 / bar 0.9470, ru floor too),
G1b PASS 23/38 exactly on the bar, **G1c FAIL by 0.0005**, G1d and G1e PASS. No bar moves and
nothing is re-run: a failed gate closes its question. [[45h2-ablation-verdict]]

**ARM A'S PER-ROW DUMP IS LOST** — `results/predictions/LOST.md`. No gate number moves and
`scored_ids_sha256` still proves which rows were scored; what is gone is the **re-score**, so a
future corrected-gold comparison of the two arms is **unpaired and must say so**. 5b.1's own
758-row dump is committed — the next runtime comparison will not have this hole.

**THE COLLECTOR WRITES TEN KEYS, AND TWO LAUNCH SIGNALS ARE NOT AMONG THEM.**
`docs/CHANNELS-launch.md` counts **views and reactions** and stars both; a v1 post record carries
neither, and neither does a poll payload. The proven pattern is a retrospective refetch like the
5a poll census — **$0**, sidecar v2 **beside** raw v1, never into the v1 stores. 5c3 inherits it.

## ⏭️ Next

1. **THE 5c CONTRACT BRIEFING IS THE NEXT SESSION.** The team lead's proposed split, to be
   confirmed there: **5c1** — entry gates for the launch set (batched, the operator's own hours,
   ~1–2 evenings) + collector on the new set + the volume calculation, all $0. **A count to
   reconcile at the briefing:** `docs/CHANNELS-launch.md` says «запуск **51** · watch 14» and the
   STATUS sketch of 5c1 says **52 каналов**. The document is authoritative; do not edit STATUS,
   name the gap. Fifth instance of brief-count-vs-document in this project;
   **5c2** — the loop core (a pod runner in place of `run_loop.ENDPOINT`, still `None`) + the
   ~4-week backlog window (~$2–2.5, one paid event) + SQLite aggregates; **5c3** — the category
   layer (**the operator's taxonomy BEFORE any labeling**) + sidecar v2 + alerts v0 on spikes of
   both polarities. Then **5d**: the first 14-day reporting cycle.
2. **Two operator actions, both $0 and blocking nothing:** the RunPod serverless ticket (still not
   filed — the hub-worker observation is a ready-made ticket) and pre-thinking the dairy /
   ice-cream category taxonomy needed in 5c3.
3. **The tree starts with SIX uncommitted paths** — `docs/SPEC.md` and `docs/STATUS.md` (the team
   lead's tail), plus `knowledge/hot.md`, `knowledge/daily_logs/2026-08-06.md`,
   `knowledge/daily_logs/2026-08-07.md` (untracked) and `knowledge/index.md`, which are the two
   `/close` runs' own output. A step 0 that names fewer paths should **commit them, not stop** —
   this has fired at every phase boundary since 5a. Stage by path, never `git add -A`.
4. **G1a and G1c stay DEFERRED** until the loop's first reporting cycle, on its fresh data — also
   the only new source of ru rows for G1a and of sarcasm for G1b, the old corpus having been
   exhausted at 4.5d. Whatever is decided then starts a **new** pre-registration.
5. **Phase 5 budgets: $8 GPU + $1 OpenRouter**, of which **$1.7069 GPU is spent** ($6.29 left,
   $0 OpenRouter). Spend anchors are written before the first spend and never regenerated.

## 🚧 Blockers

**NOTHING IS OPEN.** The one external fault is routed around rather than fixed: no RunPod
serverless endpoint on this account reaches a job-consuming worker — proven not to be ours by
**RunPod's own hub vLLM worker** failing the same way, and proven not to be the artifact by the
same code answering correctly on a pod. Production moved to a stop-after pod, 5b.1 scored config A
there, and serverless can only return through a fresh §3.11 (2) measurement. The money question
that was open at the 19:43 checkpoint was ruled the same evening (decision 22). What is left before
5c is a **briefing**, not a decision.

**Two things recorded rather than open:** the 100 GB CA-MTL-3 volume bills **~$0.24/day attached to
nothing** (its fate is 5c's $0 step-0 calculation), and arm A's per-row dump is permanently lost.
No pod, endpoint or template exists — `runpodctl pod list -a` and `serverless list` both `[]`.

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
