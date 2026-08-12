# market-pulse-llm — Project Specification (rev. 3.14)

**Status:** APPROVED rev. 3 (2026-07-26); amendment 3.1 approved 2026-07-27;
amendments 3.2 and 3.3 approved 2026-07-28; amendments 3.4–3.6 approved
2026-08-01; amendments 3.7 and 3.8 approved 2026-08-02; amendment 3.9 approved
2026-08-03; amendment 3.10 authorised 2026-08-04, recorded 2026-08-05;
amendment 3.11 (Phase 5 contract) approved at the briefing 2026-08-05;
amendment 3.12 (relevance floor of the entry gate + content-first discovery)
approved 2026-08-08; amendment 3.13 (captions move to the project's own
Gemma-4 vision path; API caption instrument retired) ruled by the operator
2026-08-08, recorded the same session; amendment 3.14 (target runtime =
serverless; same-evening probe overturns the 5b wall) ruled and recorded
2026-08-08 late evening.
**Amendment 3.1:** EN removed from per-language gates — the collected corpus
contains 8 EN comments out of 2,000 sampled (retail channels post in UA); a
per-language metric over n=8 is meaningless. Gates run on UA and RU. The model
stays multilingual; EN support is untested, not claimed. Decided BEFORE
baselines were scored.
**Amendment 3.2:** G1b's slice is drawn from the frozen sarcasm holdout
(`data/frozen/sarcasm_holdout.jsonl`): fresh-corpus sarcastic rows (wave-2
mining of threads disjoint from test and train) topped up with rows moved OUT of
the mined training pool — removed from training, not copied (option 1a). At
Phase 3 the zero-shot base model is scored on the holdout; the G1b slice = the
holdout rows the base model misclassifies. The gate itself is unchanged: the
fine-tuned model fixes ≥60% of the slice with ≤2 pp overall macro-F1 loss.
Fallback recorded: if the base model errs on fewer than 100 holdout rows, the
slice is whatever it errs on, and the smaller n is reported next to the gate
verdict. The corpus bounded the freeze at 108 rows (54 fresh + 54 moved) —
counts and provenance in `docs/frozen-testsets.md`. Decided BEFORE baselines
were scored.
**Amendment 3.3:** G1d gates the **3-class post-type** macro-F1 alone. The
rev. 3 wording "relevance + 3-class" named two distinct metrics and read as one
number; scoring them separately at Phase 3a showed why the difference matters —
relevance is already near its ceiling (TF-IDF+logreg 0.8119 against post-type
0.6653), so demanding +10 pp on a blended number would be arithmetically
dishonest: the blend would move on the head with the least room to give.
Relevance macro-F1 is REPORTED next to the gate with its own n and never enters
it. The threshold and the test set are unchanged. Unlike 3.1 and 3.2 this
amendment was decided AFTER a baseline was scored (2026-07-28, the TF-IDF+logreg
run) — it disambiguates a gate that was never one metric, and no fine-tuned
number exists yet, but the ordering is recorded rather than smoothed over.
**Amendment 3.4 (Phase 4 briefing, 2026-08-01):** four operator decisions, all
pre-registered before any Phase 4 code or GPU spend.
(1) **Base + precision — branch (2).** The base model is `google/gemma-4-31b-it`
(gate decision 2026-07-31, ADR `phase4-base-model-gate`; supersedes §7's
candidate list, which predates the 2026-07-31 live search). Training is QLoRA:
frozen base quantized NF4 4-bit (bf16 compute dtype) + LoRA adapters, on a
RunPod A6000 48 GB. Rationale: train in the precision you serve — production is
the quantized serverless path (2026-07-28); bf16 needs ~70 GB and does not fit
a 48 GB card. The deliverable artefact is the 4-bit base plus the UNMERGED
adapter, and every gate is scored in exactly that configuration. Merging the
adapter into bf16 weights is forbidden until measured (Phase 5).
(2) **Own-pod zero-shot re-run** — the first smoke step: the base model, the
same NF4 config, the same frozen inputs and byte-identical prompts as 3b, with
per-row prediction dumps. It anchors G1d/G1e, defines the G1b slice (the union
of sentiment ∪ sarcasm errors on the 108-row holdout, gate-review decision of
2026-07-31), and cross-checks the OpenRouter fp8 row; on material disagreement
the own-pod number anchors and the disagreement is recorded, never averaged.
The Phase 4 gate eval reuses this same local inference path, the adapter being
the only difference.
(3) **Ablation protocol for the synthetic source.** Two arms — with and without
`data/annotation/synthetic_sarcasm.jsonl` — identical config and seed, exactly
one data path differs. BOTH arms are scored on the frozen sets. Selection rule,
fixed now: the synthetic source stays iff its arm's G1b fix-rate is strictly
higher AND no other gated head is lower by more than 0.5 pp. The Tier-1 gate
verdict is the selected arm's; both columns are published side by side; there
is no third run. No retraining after gate numbers are seen — a failed gate
closes the question.
(4) **Budget time-box (§7/§9).** Hard cap **$25** GPU spend across all of
Phase 4, checked against RunPod billing before every start; the smoke must
project the full run, and a projection over **4 h per arm** stops the line for
an operator decision. Top-up $35 with a ~100 GB network volume (pods without a
volume are deleted unrecoverably at $0 balance).
**Amendment 3.5 (4a acceptance, 2026-08-01 — before any fine-tuned number exists):**
(1) **The own-pod NF4 row is baseline (c) for every gate** (operator decision):
G1a's best baseline and per-language floors, G1c's baseline, and the G1d/G1e
anchor already pre-registered in 3.4 (2). Anchors are read programmatically
from the own-pod record in `results/baselines.json` (config.backend "local"),
never hand-typed. Resulting targets: G1a ≥ 0.9418 overall (floors: ua 0.8718,
ru 0.8649), G1c ≥ 0.8436.
(2) **G1d and G1e replace "+ 10 pp" with a no-regression gate:** fine-tuned ≥
anchor − 1 pp (G1d ≥ 0.8984, G1e ≥ 0.8874); improvement is reported beside
the verdict, never gated. Ordering recorded honestly: "+10 pp" was written
2026-07-26 assuming a weak zero-shot base; the selected base saturated both
heads (anchor + 10 pp exceeds 1.0 for G1d and demands 0.9974 for G1e), the
impossibility was arithmetically visible in the 3b numbers on 2026-07-31 and
was named only at the 4a acceptance — a team-lead miss, recorded not smoothed.
No fine-tuned number existed at decision time (amendment 3.3's epistemic
position). The rescaled-ambition alternative (relative error reduction ≥25%)
was considered and rejected: near the ceiling it collides with label noise
and a failure would be uninterpretable. The T2 heads now gate the real
multi-task risk — forgetting; the phase's ambition burden lies on G1a, G1b,
G1c.
(3) **G1b mechanics, fixed before training:** the slice IS
`results/g1b_slice.json` (44 ids); the scorer's fix-rate function is changed —
by this team-lead instruction — to consume that persisted list. A slice row
counts as FIXED iff it leaves the fine-tuned model's union of sentiment ∪
sarcasm errors (correct on BOTH labels). Gate: ≥60% of 44 → **≥27 rows**,
with the existing ≤2 pp overall macro-F1 guard; n=44 is reported beside the
verdict (amendment 3.2 fallback). Gate evals run the local inference path at
batch size 1 unless batch-invariance is re-measured and recorded (4a ADR
§(c)).
**Amendment 3.6 (4b acceptance, 2026-08-01 — before any full run):** the
per-arm projection ceiling of 3.4 (4) rises 4 h → **5 h**, uniformly for both
arms. The smoke measured 45.23 s/step (NF4 dequantizes on every forward and
backward — the quantization that fits the card prices the step), projecting
3.42 h / 4.37 h per arm; the pre-registered stop fired on the second arm, and
the operator resolved it by raising the time proxy rather than touching the
frozen config: 2 epochs and every other hyperparameter stand, the ablation
stays paired, and the $25 cap remains the binding protection (projected
training total ≈ $4.13). Rejected: 1 epoch for both arms (halves the training
of the small G1b signal to satisfy a proxy) and dropping the synthetic arm
(decides the ablation without measuring it). Ordering recorded: decided after
smoke timing and loss curves only — no gate or frozen-set number existed.
**Amendment 3.7 (quality program, 2026-08-02):** Phase **4.5 — a
ceiling-driven quality program** — is inserted before Phase 5, and Phase 5
stays paused until 4.5 concludes (operator sequencing decision: quality
first, then the loop). Motivation, recorded honestly: the operator's stated
target of 0.98 exceeds the measuring instrument — comment gold was
calibrated at 96.3% agreement, so this test's ceiling is ≈0.96–0.97 for a
perfect model; the program therefore chases the MEASURED ceiling, never an
absolute number picked in advance. Structure: **4.5a = error audit +
ceiling measurement**; all further steps (targeted re-labelling at scale,
synthetic v2, a dev-set hyperparameter search) are DEFERRED until 4.5a's
results exist, and each gets its own pre-registered gate. 4.5a protocol:
the executor assembles an ANONYMIZED adjudication pack from the persisted
per-row dumps and the frozen files — every disagreement row shows the two
candidate labels in per-row random order with no attribution (the key is
sealed, its sha256 recorded), plus a 30–40-row control sample of agreement
rows; the operator is the sole arbiter (SPEC §10) and rules each row
label-A-correct / label-B-correct / ambiguous. NOTHING in the frozen files
changes in 4.5a: gold re-adjudication, if the audit justifies it, is a
separate test-set-v3 decision at the 4.5a gate with honest versioning (all
old runs re-scored from their dumps at $0). Output: per-head ceiling
estimate, gold-error rate, error taxonomy.
**Amendment 3.8 (intents law gate, 2026-08-02):** the operator, in a
structured interview over the audited rows, resolved the intents question in
two parts. (1) **The old law largely stands where it was challenged:** 17 of
the 19 disputed `[]` control rows are confirmed correct under the Phase-2
guideline (emoji-only, thanks, jokes, giveaway distrust); those control
verdicts are recorded as a context artifact — the audit pack showed the
intents field WITHOUT sentiment and sarcasm, inviting conflation (a pack
design flaw, recorded). The 4.5b "22/40 incorrect" figure therefore does NOT
mean mass mislabeling under the old law. (2) **The taxonomy changes — v2
adds a sixth intent `service`** (operator product decision): "interaction
with the retailer as a service — in-store and online service, the delivery
PROCESS, app/checkout, support hotline, staff, and the organization of
promos and giveaways (mechanics, fairness, communication)". The WIDE
boundary was chosen explicitly: giveaway-distrust rows move from `[]` to
`service`; `availability` keeps product presence/stock/delivery-of-the-
product; co-occurrence (`service` + product intents) is allowed. The three
audited non-empty rows fall into the service family under v2.
Pre-registered consequences, executed as 4.5d (prep, $0-ish) then 4.5e
(label + retrain), each gated: guideline v2; intents re-label of ALL
labeled data via the Phase-2 pipeline with operator calibration (the same
≥90% pre-registered threshold); test **v4** = v3 + the re-labeled intents
column; the T1 prompt grows the sixth class, so G1c re-anchors on a fresh
own-pod zero-shot of the base model with the v2 prompt (old prompt SHAs
remain valid for old records); one retrain; new program bars pre-registered
BEFORE the retrain is scored. Timing: combined with the corpus up-labeling
(its appetite is decided at the 4.5d gate on concrete candidate counts).

**Amendment 3.9 (4.5h precheck acceptance, 2026-08-03):** the per-arm training
ceiling rises 5 h → **6.5 h** for the 4.5h2 ablation only (arm B projects to
5.44 h at the slowest observed rate; the margin leaves room for a crash-resume
without breaching). Three bound decisions from the same acceptance, recorded
here because they alter what a gate reads: (1) both arms train on the `_tax2`
(taxonomy-v2) siblings of the T1 comment sources — the v1 `SOURCES` would give
arm A zero `service` exposure and turn the selection rule into a
taxonomy-exposure measurement (precheck finding, `results/precheck_45h.json`);
(2) the 24-row carve is drawn BEFORE the пласт is appended, so both arms hold
the identical carve (pairing discipline of 3.4 (3)); (3) test v4 is derived
v3 → intents migration pass (508 rows, the `intents` field only) → the 31
audit rulings + 1 law verdict re-applied ON TOP (operator rulings supersede
the model); the 54 dual-home ids are resolved by option (i): the holdout pool
is materialized at 917 rows as a new version beside the pristine file, and v4
inherits v3 values on the 4 diverging rows.
**Amendment 3.10 (4.5h2 mid-phase ruling, authorised 2026-08-04, recorded
2026-08-05):** amendment 3.9 (1)'s `_tax2` sources are unparseable under the
frozen v1 training prompt (`service` is not a T1v1 label; the trainer's
train/eval format-identity invariant then moves the eval's rendering with it —
implementation-notes.md D2), so the training/eval rendering moves to
**`T1v2_with_post`**, the instrument the gold was annotated with. Two bound
consequences, both operator-authorised in the same ruling: (1) the per-arm
training ceiling rises **6.5 h → 8.5 h** for the 4.5h2 ablation only —
3.9's 6.5 h was projected against a rendering without the parent post;
with-post projected arm B at 8.16 h (observed: arm A 4.58 h, arm B 7.51 h);
(2) `config/qlora.yaml` **`max_seq_len` 1024 → 1408** — a guard threshold, not
a pad width (`collate` pads per micro-batch), so step time does not move, and
all 5 676 rows of both arms encode under it (0 over). The authorisation was
recorded same-day in implementation-notes.md D2, `scripts/runbook_45h2.md` and
both runs' provenance; it reached this file only at the 4.5h2 acceptance
(2026-08-05) — a team-lead process fault, recorded rather than smoothed over.
Rule going forward (written into the team-lead skill, 2026-08-05): a mid-phase
authorisation that changes a contract limit is written into SPEC the same
session it is made, before the run that depends on it.
**Amendment 3.11 (Phase 5 contract, briefing 2026-08-05):** Phase 4.5 is
formally closed — 3/5 gates on arm A accepted as the measured result; the
G1a/G1c question is deferred until after the loop's first reporting cycle.
Phase 5 (production loop) opens under this contract:
(1) **Scope & cadence:** collection via Mac cron at **2 passes/day** (operator
choice; frequency is a recorded knob, not a constant), batch inference on
RunPod serverless (NF4 base + arm-A adapter of 4.5h2), SQLite aggregates
**[runtime ruling, operator 2026-08-06: serverless is unreachable on this
account — no endpoint, including RunPod's own hub worker, consumes a job
(evidence: results/parity_verdict_5b.json). Production runtime = a
stop-after POD on AMPERE_48 (A6000 — the same card the 4.5h2 anchors were
measured on), booted per pass; serverless may return later ONLY through a
fresh §(2) measurement. A support ticket runs in parallel at zero cost.
Capacity clause (team-lead ruling 2026-08-06 evening, on the A6000
stock-out in CA-MTL-3): the CLASS is the contract, the datacenter is not
— the volume is a convenience. A6000 in any datacenter is the primary
path (fresh staging must pass assert_runtime_matches before any scored
row); A40 is an authorised in-class fallback when A6000 is out
everywhere, with the exact card recorded in the run's provenance.
AMPERE_80/A100 is NOT authorised — the GPU class is the variable §(2)
measures. The 5c loop keeps a per-pass allocation-latency ledger; the
second-volume question is decided on that data, not on fear.]**
(brand × intent × sentiment × time × category), a **14-day first reporting
cycle** + alerts v0 on spikes of both polarities, own and competitors
(PRODUCT.md §6; alert latency = collection interval).
(2) **Serving parity, pre-registered:** before any serving number reaches an
aggregate, the EXACT production configuration (merge state, batch size,
runtime) is scored once against test v4 and recorded beside the 4.5h2 gate
numbers; the delta is reported, never averaged away. Merging the adapter
stays forbidden unless this measurement selects it.
**Pair pre-registered (operator, 2026-08-06):** config A = NF4 base +
unmerged arm-A adapter, batch 1 (the 4.5h2 replica); config B = adapter
merged in bf16 then REQUANTIZED to NF4, batch 1 (bf16 serving does not
fit the GPU class — ~62 GB weights vs 48). Both scored once on test v4
through the PRODUCTION serverless runtime, one attempt each, smoke
before any paid call, hard budget stop $4 of the $8 cap, spend anchors
written before the first spend. Selection rule, committed BEFORE the
run: B is adopted only if every 4.5h2-passed gate stays passing on B
(G1b fix-count, G1d, G1e against the bars in
`results/verdict_45h2.json`) and no gate head drops more than 0.005
vs A; any tie or doubt ships A — the safe default. A failed or aborted
pair closes the merge question in favour of A; no retry.
**Single-config measurement pre-registered (operator, 2026-08-06, after
the pair aborted):** config A alone is scored once against test v4 on the
POD runtime of the (1) ruling — the pair stays closed, B stays dead. One
attempt, batch 1, hard stop = the $3.47 remaining under the 5b cap; smoke
on the 24-row arm-A carve (`results/train/45h2-arm-a/provenance.json`,
`n_carve: 24` — PROMPT-5b's "carve-758" was a team-lead misname; 758 is
test v4's row count). Deltas vs `results/verdict_45h2.json` are REPORTED,
never averaged away; this is not a gate and no bar moves, but any
4.5h2-passed gate head landing under its bar is reported loudly as its
own finding for an operator briefing. A failed attempt stops the line —
aggregates cannot take serving numbers without this measurement.
**Batch measurement pre-registered (operator, 2026-08-06, after the
Δ=0 batch-1 parity; motive: at batch 1 the one-off backlog ≈ $6.80
against $6.77 of phase headroom, run-rate ≈ $28/mo against the $9–12
ceiling):** serving batch>1 may be adopted ONLY through this
measurement. Candidate ladder {16, 8, 4}: the 24-row carve is smoked
at each N; the largest N whose carve outputs are byte-identical to the
batch-1 smoke picks the candidate (a pre-filter on training rows — no
test exposure); if none is identical, the candidate is 8. Test v4 is
then scored ONCE at the candidate N. Adopted only if every
4.5h2-passed gate stays passing and no gate head drops more than
0.005 vs `results/parity_5b_a.json` (the batch-1 record with its
committed per-row dump; row-level agreement vs that dump is REPORTED
as description, never gated). One attempt, no retry, hard stop =
the $2.77 remaining under the parity $4 stop. A failed measurement
fixes serving at batch 1 permanently and returns the money question
to the operator. GATE EVALS stay batch 1 regardless — the anchor
methodology is untouched, and the batch-1 serving path must remain
byte-stable under any new batching code (guarded by test).
(3) **Category post-layer is in-phase** (operator choice): the taxonomy is
the operator's word BEFORE any labeling; one LLM pass over ~6k posts
(~$0.2–0.5) with its own pre-registered gate (sealed hundred of posts,
operator session); comments inherit the category via parent_msg_id; the
fine-tuned comment model is untouched.
(4) **Channels & coverage:** the loop launches on the current **four** registry
channels (correction 2026-08-06: this clause said "five" — stale at the time
of writing; @znizhki_ua was removed 2026-07-27, ADR `znizhki-ua-removed`, and
`config/registry.yaml` held four for a week before 3.11 was drafted. A
team-lead preflight fault, recorded, not smoothed over);
discovery (mothers/kids, healthy-lifestyle, baby-food themes —
authorised 2026-08-04; **expanded 2026-08-06 at the 5a acceptance,
operator ruling on docs/RESEARCH-5a1-themes.md:** + cooking/recipes,
+ supermarket discounts/promos, + health/fitness — authorised AGAINST
the team-lead recommendation, the ledger prices it — + food-quality /
falsification watch, + direct seed-handle checks from the research
note) produces candidates only, and every new channel
enters through the track-R entry gate before its rows reach train or
production aggregates. **Market-origin screen (operator ruling,
2026-08-08, wartime-principled and data-quality-motivated): the gate
REQUIRES UA-market evidence and excludes RF-market channels regardless
of language — RU-language is not RF (Ukrainian consumers write in
Russian), so the discriminators are market facts: currency in price
posts (грн vs ₽), retailer names (АТБ/Сільпо/Varus vs Пятёрочка/
Магнит/Перекрёсток), locations, domains, «запрещён на территории РФ»
disclaimers. Ambiguity → FLAG to the operator, never a silent pass.
Applied retroactively to every current source and standing for every
future candidate.**
**Language policy (operator ruling, 2026-08-08, against the team lead's
softer recommendation — recorded, not smoothed): the composition takes
UKRAINIAN-language channels only — channel-level UA dominance of posts
is an entry requirement, applied retroactively. The operator's market
read: by 2026 posts and comments run Ukrainian across Ukraine, with
occasional RU comments (Дніпропетровщина most of all); the model KEEPS
its RU capability for stray comments inside UA channels — the bilingual
training is insurance, not an invitation. Mechanics: per-source UA/RU
post shares computed OFFLINE from the collected window; RU-dominant →
out (members leave, verified by membership flag); mixed → FLAG to the
operator. Every exclusion triggers the replacement rule (same segment,
UA, max audience).** **Coverage target (operator, 2026-08-05): the
monitored portfolio aims at ≥10,000,000 summed subscribers.** Discovery
keeps a coverage ledger: per-candidate subscriber counts, the current
four's sum, and the gap to target — with two caveats printed beside the
ledger: summed subscribers ≠ unique reach (overlap is unmeasurable from
the API), and subscribers ≠ comment flow (rows are born in discussion
groups). Widening discovery beyond the authorised themes — and the
coverage-target ruling itself — are operator decisions taken on the
combined ledger (next reading: after the 5a.1 scan).
**Coverage rulings (operator, 2026-08-06, on the combined ledger):**
the ≥10,000,000 target STANDS as aspirational (the ledger keeps
reporting the honest gap); launch composition is fixed at **51
channels** (registry 4 + 29 comment-capable + 18 posts-only,
1,199,519 subscribers) plus **14 watch** (group present, currently
silent: track-R gate passed, posts collected, NO group joins until
the channel posts again; reviewed after reporting cycle 1); 12
operator picks excluded (7 off-topic/non-UA, 6 dead, one overlap);
+1 operator addition (2026-08-06 evening): @marketopt_official —
Poltava/Kremenchuk regional grocery chain, 41,518 subscribers,
verified, dairy/ice-cream promos throughout — enters via the same
track-R gate. The authoritative per-channel list:
`docs/CHANNELS-launch.md`.
**Signal layer (operator, 2026-08-06):** beside post text and comment
text, the loop extracts reactions (emoji valence), views and forwards
— absent from raw v1's ten keys, fetched retroactively at zero cost
by the poll-census pattern into a v2 sidecar (5c deliverable); poll
vote counts join the same sidecar. Reaction valence is reported
BESIDE model sentiment with its own scale, never merged into it.
(5) **Brand normalization v2** (declensions + homoglyphs) is registered
BESIDE v1; historical dumps are re-scored under v2 at $0; every number
names its normalization version; gate history under v1 is not rewritten.
(6) **Budgets, pre-registered:** phase cap **$8 GPU** (of the $8.70
remainder — the 2026-08-05 figure; the live headroom is read from the
spend anchors `results/spend_*.json`, and the CA-MTL-3 volume bills
~$0.24/day whether attached or not — correction 2026-08-06, D9)
+ **$1 OpenRouter**; post-launch run-rate ceiling ~$9–12/month
(serverless + the CA-MTL-3 volume, kept — review ~2026-09-05 if no GPU
work has started). Spend anchors are written before the first spend.
**Cycle-1 economics ruling (operator, 2026-08-06, on the measured
batch-1 prices — $0.4611/pass, $0.5993/1000 rows):** the inference
backlog is scored as a WINDOW — the most recent ~4 weeks of stored
comments (~$2–2.5) at the 5c start; the full 11,338-row history is a
separate, visibly deferred decision taken only if a use-case demands
it. Reporting cycle 1 runs at 2 passes/day; the PERMANENT run-rate
ceiling is set AFTER cycle 1 on its measured daily row flow — the
$9–12 figure was written for per-second serverless and is not the
ruling. The volume-vs-redownload-vs-stopped-pod economics is a
zero-cost step-0 task of 5c (using the measured staging costs and
RunPod's price list); the CA-MTL-3 volume's fate — it idles at
~$0.24/day and local-NVMe staging is faster (46 s vs 279 s) — is
decided on those numbers, advancing the ~2026-09-05 review.
**Volume ruling (operator, 2026-08-07, on `results/volume_calc_5c1.json`):**
option (b) — the CA-MTL-3 network volume is DELETED; every 5c2+ pass
re-stages the 59 GB pinned-revision weights onto pod NVMe (measured:
$2.53/mo against $9.66 for keeping the volume, at 60 passes/mo; boot
286.2 s against 278.9 s). The decisive argument is the datacenter
unpin, not the $7: §(1)'s capacity clause becomes fully symmetric —
A6000 in ANY datacenter, nothing pinning CA-MTL-3 (its stock-out
already bit on 2026-08-06). Deletion is executed by the executor and
proven BY LISTING (deletion is never proven by an exit code); the
~2026-09-05 volume review is closed by this ruling.
(7) **Out of scope:** any retrain; dashboard UI (Phase 6); a VPS; merging
without the (2) measurement; new-domain rows in aggregates before their
entry gate. Raw v1 stores stay byte-untouched — derived columns land
beside them, as reply_to did.
Sub-phases, each with its own verify-gate: **5a** loop skeleton + poll
census + discovery → **5b** serving parity → **5c** loop core + aggregates
+ category layer → **5d** first reporting cycle + alerts v0 → the G1a/G1c
decision briefing.
**Amendment 3.12 (operator rulings 2026-08-08: relevance floor + content-first
discovery):**
(1) **The track-R entry gate gains a mandatory relevance floor — the yield
screen.** The existing screens grade capability, language, market origin and
"about food" theme; none measured whether a channel contains OUR taxonomy. The
yield screen runs the brand watchlist display_names (`docs/WATCHLIST.md`, folded
into the registry) plus the category lexicon over a channel's collected 28-day
window and reports per channel: brand hits/week, category hits/week, share of
taxonomy-relevant posts, and comment flow on relevant posts. Posts and comments
are separate currencies — retail_official earns on posts, audience segments earn
on comments — so the screen never blends them into one number. Thresholds are
PRE-REGISTERED by the operator before any number is seen (the language-census
discipline). The screen also runs retroactively over the whole current registry;
zero-yield members are surfaced to the operator with their numbers — removal is
an operator ruling, never automatic. Launch verdicts for the day-2 candidates
are signed only AFTER their yield numbers exist; day-2 collection and joins
proceed as queued, since they produce the very windows the screen reads.
(2) **Content-first discovery is authorised.** Telegram's global full-text post
search over all public channels (`channels.searchPosts`, live since 2025-07-31)
becomes the primary discovery instrument: queries drawn from the watchlist and
the category lexicon return the channels where the taxonomy actually lives,
replacing name-based guessing. Costs: Telegram Premium on the collection account
(€5.99/month, operator's purchase screen 2026-08-08; the subscription must sit
on the ACCOUNT BEHIND `marketpulse.session`, since the search is called from
it) + Stars above the free daily quota; the exact
per-query price and remaining quota are returned by the API itself
(`searchPostsFlood`) and are read before the first paid query. Free instruments
beside it: `channels.getChannelRecommendations` seeded from channels that PASSED
the yield screen, and the forward graph of already-collected windows (whether
forward metadata exists in raw v1 records is verified by opening one record,
never assumed). **TGStat is ruled OUT** (RF service, RUB payment); Telemetr.io's
free tier is the permitted catalog fallback.
(3) **Money:** a separate discovery budget line beside the $8 GPU + $1
OpenRouter caps — the Premium subscription + **≤$5 in Stars per discovery
session**, each session individually authorised by the operator and
spend-anchored like every other paid instrument.
**Amendment 3.13 (operator ruling 2026-08-08, second evening session: captions
move to the project's own Gemma-4; the paid-API caption instrument is
retired):**
(1) **The ruling.** The operator does not accept a paid external API as the
caption instrument for the loop; captions run on the project's own Gemma-4.
This supersedes the late-08.08 closing ruling "captions stay on the cheap API
path" and VOIDS `docs/PROMPT-5c1-captions-full.md` before execution — its
$0.35 OpenRouter cap was never touched. Recorded price of the ruling, stated
at decision time: the spend moves to the GPU meter and grows (build + smoke +
re-pilot + full run ≈ $1–2.5 GPU against $0.22 API); the caption instrument
changes, so a comparability seam is created and documented (below).
(2) **Feasibility, verified on disk before this amendment ($0, team-lead
reads):** the pinned base revision `842da3794eaa…` is a
`Gemma4ForConditionalGeneration` image-text model; `local_llm.py` already
loads via `AutoModelForImageTextToText`; the QLoRA adapter explicitly
excludes `vision_tower` / `multi_modal_projector` (config/qlora.yaml).
Missing and to be built: the AutoProcessor image path, a caption task and
runner, tests, and a pod runbook.
(3) **The instrument.** Captions come from the NF4 BASE at the pinned
revision with the ADAPTER OFF (the adapter is classification-tuned; captions
through it would be a third instrument), greedy, batch 1, its own registered
caption prompt (new sha, registered before any result exists). Provenance
gains `caption_source` (`qwen-4.5g2` | `gm4-nf4-base`): every
caption-carrying record and every screen or gate number names its caption
instrument, and numbers with different caption sources are never compared
without saying so. The 4.5g2 API instrument is retired for new data from this
date; its bought captions stand as history.
(4) **Program and gates.** **vis-a** (executor, $0, local): processor path +
caption task + tests + runbook; no model download, no pod. **vis-b** (one pod
session, cap $1.00 GPU): load smoke → measured rate ($/post, s/post) →
re-pilot of the SAME 19 ATB media-only posts → bridge table GM4-vs-qwen on
identical posts (qwen captions already bought and committed) → screen-pilot
check against the UNTOUCHED prereg sha `1aa89818…`. Pre-registered
instrument-failure rule: if ATB with GM4 captions fails bar A where qwen's
PASS stands, the instrument failed — STOP, the fork returns to the operator
with the bridge table. **vis-c** (one pod session, cap $1.50 GPU): the
remaining 232 posts + yield screen v2, prereg unchanged. Launch signing stays
frozen until v2 (the operator's freeze stands). Caps come from the $8 GPU
line (headroom $6.29 after the parity program's $1.71); one attempt each,
STOP over cap, a partial run reports what it bought.
**Amendment 3.14 (operator ruling 2026-08-08 late evening: the target
runtime is serverless; a same-evening probe overturns the 5b wall):**
(1) **The ruling.** The production runtime target moves back to SERVERLESS
(model resident on a network volume, workers scale to zero) — supersedes
decision 20's pod-stop-after as the TARGET; pods remain the measured,
proven fallback. All paid 5c1 steps and the launch signing are HELD by the
operator's word until the serverless track proves out.
(2) **The probe** (team lead, live in the operator's console, same evening;
record: `docs/probe-serverless-20260808.md`): endpoint `8mkl2lbxho3bfa`,
`runpod/mock-worker:dev`, 16 GB flex, queue mode, no volume, no DC pin.
Two jobs consumed and COMPLETED (delay 10 964 / 6 800 ms, execution
142/144 ms, worker `pri0muyf75j143`). The 5b blocker did NOT reproduce.
The vendor ticket is unnecessary — closed unfiled; the operator's "we wait
for no one" was the correct call, over the team lead's records-first
recommendation. Endpoint deleted after answering; deletion proven by the
zero-endpoint listing. `results/parity_verdict_5b.json` stands untouched as
the honest record of 2026-08-06.
(3) **Not proven by the probe, pre-registered before srv-2:** the
volume-attached GPU offering today (D7 re-read required); GM4 NF4 fit and
batch-1 byte-stability on the offered GPU; cost per row vs the pod's
$0.60/1000. SPEC 3.11 (2) parity (758 rows vs the 4.5h2 anchors, batch 1)
remains mandatory before any production number.
(4) **Program:** srv-2a (executor, $0, local): serverless worker config
reusing the 5b entrypoint proven on the pod (`scripts/serve_handler.py` +
`scripts/start_5b_worker.sh`), volume re-creation plan, runbook. srv-2b
(one paid session, cap set at its briefing): volume + weights + endpoint +
smoke + D7 re-read + parity. The caption instrument of amendment 3.13 is
unchanged; vis-a code is runtime-agnostic and rides along.
**Amendment 3.15 (operator go 2026-08-09, after srv-2d parity held: the vis
program moves to the proven serverless runtime):**
(1) Supersedes the SESSION SHAPE of 3.13 (4) only: vis-b and vis-c run as
serverless-endpoint sessions (CAPTION template/config, weights resident on
volume `qw4nwleanc`), not pod sessions. Everything else in 3.13 stands
unchanged: caps ($1.00 / $1.50 from the $8 GPU line), the gate order, the
untouched prereg sha `1aa89818…` (= sha256 of
`results/yield_bars_5c1.preregistration.json`, which the screen record
carries), the instrument-failure STOP rule, and the launch-signing freeze.
vis-b procedure: `scripts/runbook_vis_b.md` (accepted at vis-a-r), anchor
`results/spend_5c1_vis.json` written before the first billable action.
(2) Transport constraint measured at vis-a-r binds the job shape: media
travel as data: URLs inside the job under RunPod's documented 10 MB `/run`
ceiling (19 ATB posts → 8 jobs, largest 7.83 MB); the volume carries weights
and dumps, never the gitignored media.
(3) §C.1 stop rule, pre-registered: the caption rate is measured on a
one-post smoke first; a >$0.50 projection for the 19 posts stops the session
BEFORE the re-pilot, and the measured rate is reported — it is a 5c2 input
either way. Cold start $0.0733 (srv-2d reading) is priced into the cap.
**Amendment 3.16 (operator order 2026-08-09: a second-instrument REVIEW of
brand recall and caption faithfulness on Opus 5 inside Claude Code, before
the launch signature):**
(1) **Class: REVIEW, never measurement.** The 2026-08-08 ruling ("an
executor chat session may not produce data — no model pin, no price") is
NARROWED by the operator's order, not repealed: a chat session may produce
REVIEWABLE FINDINGS under a committed audit protocol; it may not produce
numbers that enter gates, screens or `results/baselines.json`. The
deterministic matcher remains the sole judge of screen/G1e numbers; screen
v2 verdicts are not re-scored; prereg bars do not move.
(2) **The pin that is possible is mandatory:** the running model name
echoed in the report header (claude-opus-5), the audit protocol file
committed with its sha BEFORE any pack is opened, the pack manifest
sha-pinned (build_audit_pack pattern, 4.5a). Price is unpinnable
(subscription) — which is WHY the output class is review.
(3) **Adjudication:** Opus findings (missed-brand candidates, caption
faithfulness flags, patterns) go to an operator sitting; only ratified
items become watchlist/lexicon revisions (named revision, provenance;
G1e history never re-scored on it) or caption re-do orders. The launch
signature waits for this audit by the operator's word — deferral
criterion: audit findings on the table.
(4) **Population is bounded by strata,** committed in the pack manifest:
S1 all caption-decided screen hits; S2 per-channel sample of matcher
brand-hit posts (precision); S3 per-channel sample of matcher-zero
relevant posts (recall probe); S4 all committed GM4 captions against
their images (faithfulness; images are the sha-matched sent sets).
**Amendment 3.17 (operator, 2026-08-10: the position layer — question 7
of PRODUCT.md; design ratified in the team-lead sitting the same day):**
(1) **The question.** PRODUCT.md gains question 7 (operator's wording):
what and at what price the chains promote — and at what DISCOUNT DEPTH —
for our brands and competitors. The layer answers it from leaflets.
(2) **Data model.** A position's IDENTITY is (brand_id | brand_raw,
line, category, size, fat_pct); PRICE is an OBSERVATION at (channel,
date, carrier), never part of identity. The tier ladder is assigned by
CODE from field completeness, never by the model: `position` (brand +
category + ≥1 differentiating attribute) / `product_mention` (brand +
product, no attributes) / `brand_mention`. No field is ever imputed;
aggregates roll up at the level a record actually names. `line` subsumes
variant C: the watchlist becomes two-level (brand → lines[], with
requires_anchor flags) — the 5c3 named revision implements the operator's
2026-08-10 ВАРТО and «Селянське» rulings through it.
(3) **Prices.** Three extracted fields: price_promo, price_old,
discount_pct_printed. depth = (old − promo) / old is computed by code
ONLY when both prices exist; the printed % never substitutes arithmetic
and old price is never reconstructed from it; printed-vs-computed
disagreement is recorded as a flag, not resolved. One price without
promo markers = regular price; promo price without an old one = depth
null. Aggregate for question 7: promo depth, brand × category × week
(median + n).
(4) **Carriers and origins.** carrier = leaflet_page | post_text |
comment; price_origin = retail_leaflet | consumer_quote. Consumer
quotes NEVER enter promo aggregates — they feed the price ASPECT
(question 2). Leaflet extraction is per PAGE (one image = one call:
answers caption sampling, the 400-token ceiling and the 10 MB transport
at once). Text extraction runs only on rows passed by a DETERMINISTIC
pre-filter (watchlist/category hit + a size/price pattern nearby).
(5) **Instruments.** New registered prompts positions_post_gm4 (page)
and positions_text_gm4 (text) BESIDE the existing ones, own shas, own
strict JSON parser; extraction_source on every record, never silently
mixed with caption_source; the frozen classification family (T1v2) is
untouched.
(6) **Program and gates.** sku-a (executor, $0): PRODUCT.md row, schema
+ tier ladder + normalization + depth/cross-check, both prompts, the
pre-filter and its corpus census, ground-truth packs (leaflet reference
from the Opus-audit S4 rows; text sample for team-lead triage +
operator adjudication, 4.5f pattern, ~30 min of operator time), and the
PRE-REGISTERED sku-b bars committed before the pilot: leaflet
brand-recall ≥ 0.75 per page vs audit-visible brands; price-pair
accuracy ≥ 0.80 on positions carrying a crossed-out price (verified by
team-lead read of the per-position dump against the images at
acceptance); text tier-assignment accuracy ≥ 0.85 vs adjudicated rows.
sku-b (one paid session, cap $0.35 GPU): the two-leg pilot (19 ATB
posts page-wise; ~30 adjudicated text rows), one attempt; a failed bar
closes B as "instrument not ready" by measurement. Integration into
the 5c2 loop only on a green gate.
<!-- sku-b-ratification begin — stripped by tests/test_sku_prereg.py before hashing
docs/SPEC.md against the prereg pin; the registered law is the stripped text -->
(7) **Pilot bar operationalization — ratified (operator, 2026-08-10).** The five
readings registered in results/sku_pilot_prereg.json (ratification_required, R1–R5)
are ratified as written there: R1 — bar 1's "per page" is read per POST (recall over
the union of the post's page answers), macro-averaged over the 15 posts with a
non-empty gold set; the micro reading over the 55 pairs is reported beside it and
gates nothing. R2 — the page set is exactly the 108 sent pages. R3 — the four
empty-gold posts are outside the recall mean and serve as a precision probe. R4 —
bar 2 is SCORED at n >= 10 pairs, REPORTED and not scored at 1–9, NOT_REACHABLE at 0.
R5 — unreadable replies are excluded and counted (>10% blocks bar 3); n >= 20
adjudicated rows to score; both carriers pooled as drawn. Thresholds, the $0.35 cap
and the one-attempt clause are unchanged. Text gold: data/annotation/sku_a_text/
text30.csv adjudicated 2026-08-10, 30/30 rows, validator clean (11 position ·
3 product_mention · 16 none).
<!-- sku-b-ratification end -->
<!-- sku-b-ratification-2 begin — stripped by tests/test_sku_prereg.py before
hashing docs/SPEC.md against the prereg pin; the registered law is the stripped text -->
(8) **Vocabulary law and the attribute field — ratified (operator, 2026-08-11).**
The pre-filter's category vocabulary is law in config/lexicon.yaml (source:
data/category_lexicon_draft.json sha 1225ad75…, migrated byte-faithfully; the
draft stays frozen as history). The position schema's fifth presence field is
generalized fat → attribute; dairy instruments keep the wire key "fat" — the
registered prompt texts are unchanged. The pilot's pre-registration is
re-registered beside as results/sku_pilot_prereg_v2.json BEFORE any attempt:
thresholds, the $0.35 cap, the one-attempt clause and the R1–R5 readings are
verbatim-unchanged; only schema naming and vocabulary provenance moved. Bar 3's
ladder sha follows the renamed table.
<!-- sku-b-ratification-2 end -->
<!-- sku-b-ratification-3 begin — stripped by tests/test_sku_prereg.py before
hashing docs/SPEC.md against the prereg pin; the registered law is the stripped text -->
(9) **Pilot serving configuration and split — ratified (operator, 2026-08-11 joint
review).** The positions instruments serve from the NF4 BASE at the pinned revision
with NO adapter, greedy, batch 1, max_new_tokens 800 (a ceiling against mid-JSON
truncation, not a target length), under a new worker configuration
SERVING_CONFIG=POSITIONS that mirrors CAPTION's refusals: any variable of
serve_handler's adapter set present refuses before the model loads, and
MODEL_REVISION is required. The configuration is committed as its own artifact
BEFORE the paid attempt and the driver stops before the first paid call unless the
worker's describe() matches it. The build of the positions serving path — the
worker op, the driver with its per-position dump and a numeric payload guard, the
$0 preflight guards — is a $0 precursor contract (sku-b-prep); the paid attempt
remains the single session of (6), and inside its cap it opens with a smoke call
on NON-gold inputs (a synthetic image and a text row outside the 30-row pack)
before either leg touches gold.
<!-- sku-b-ratification-3 end -->
<!-- sku-b-ratification-4 begin — stripped by tests/test_sku_prereg.py before
hashing docs/SPEC.md against the prereg pin; the registered law is the stripped text -->
(10) **Cap discipline for the paid attempt — ratified (operator, 2026-08-11,
sku-b-prep acceptance).** Three readings, registered before the run: (a) after the
two non-gold warm-up calls of (9) the driver re-projects the WHOLE run from the
warm-up-measured marginal plus everything already billed, and REFUSES to make any
gold call if that projection exceeds what is left of the $0.35 cap — a session
stopped at this gate has touched no gold and has consumed NO attempt; the pilot
then returns to the team lead for a v3 registration under the measured price.
(b) A cap stop that fires mid-leg, after gold calls began, is a finding about the
CAP and not about the instrument: it does not close B, it is not a failed bar, and
what happens next is a team-lead ruling — never a silent re-run. (c) No single job
may be CAPABLE of billing past the remaining cap on its own: the per-job execution
timeout is sized so one wedged job cannot overrun, and a job that ends TIMED_OUT
ends the run, its unbought remainder recorded. Thresholds, the cap and the
one-attempt clause of (6) are unchanged.
<!-- sku-b-ratification-4 end -->
<!-- sku-b-ratification-5 begin — stripped by tests/test_sku_prereg.py before
hashing docs/SPEC.md against the prereg pin; the registered law is the stripped text -->
(11) **Completion of the interrupted attempt — ratified (operator, 2026-08-11,
sku-b-run acceptance).** The (10)(b) stop at 17 of 138 gold calls resolves as
RESUME: the registered population is bought to completion in ONE additional paid
session under a re-registration (results/sku_pilot_prereg_v3.json, registered
BESIDE v2 before the resumed session). Readings: (a) each element of the
registered population (108 pages + 30 rows) is bought EXACTLY ONCE across the
program — the resumed session buys only the 121 recorded as unbought, and the 17
existing answers (including the one parse refusal) enter the bars as they stand,
never re-asked; (b) the instrument is FROZEN as registered — prompts, parser and
serving pin unchanged; the superscript and asterisk findings are a post-pilot
NAMED revision, never an in-flight edit; (c) for the resumed session the warm-up
of (9) becomes REPRESENTATIVE: one real UNSENT page (of the 51 outside the R2
gold) and one real pre-filtered text row outside the 30-row pack; warm-up
answers are never scored; (d) the resumed session's cap is $0.45, priced from
the measured marginals; the go/no-go and every reading of (10) apply unchanged
against that cap; (e) the team lead's calibration read of the 13 prefix pairs
(6 correct) is NON-GATING: bar 2 is scored only by the team-lead read over the
pairs of the COMPLETED population at acceptance. The three bars' verbatim texts,
thresholds and R1–R5 are unchanged.
<!-- sku-b-ratification-5 end -->
<!-- sku-b-ratification-6 begin — stripped by tests/test_sku_prereg.py before
hashing docs/SPEC.md against the prereg pin; the registered law is the stripped text -->
(12) **The v4 session and the cost of a refusal — ratified (operator, 2026-08-11,
sku-b-v3-run acceptance).** The v3 session was refused by the (10)(a) gate on a
representative probe (14.808 s/page from the registered unsent page) and consumed
no attempt. Readings: (a) ONE more resumed session is authorised under a v4
re-registration (results/sku_pilot_prereg_v4.json, BESIDE v3, before the session),
cap **$0.65** — sized to admit the gate's own pessimistic projection (~$0.60),
whose probe is structurally a DEEP leaflet page and prices above the first-six-page
gold population's drawn marginal (5.0772 s, n=17); the in-run gate still protects
the middle. (b) **A session refused at the (10)(a) gate charges the PHASE ledger,
never the next attempt's cap:** each registered attempt runs under its own fresh
anchor and its own cap/ledger/phase constants, set together (the Dv167 finding).
(c) The warm-up inputs remain the REGISTERED ones of v3 — the same unsent page and
the same non-pack row, re-verified by hash, never re-picked. (d) Every reading of
(10) and (11) otherwise applies unchanged; the population is still the 121
unbought elements, each element of the 138 bought exactly once across the program.
<!-- sku-b-ratification-6 end -->
<!-- sku-b-ratification-7 begin — stripped by tests/test_sku_prereg.py before
hashing docs/SPEC.md against the prereg pin; the registered law is the stripped text -->
(13) **The B′ revision — ratified (operator, 2026-08-12, after the miss
decomposition).** The team lead's read of bar 1's 29 misses found ZERO confirmed
vision under-reads: 11 are parser refusals and one alias gap (four refused pages
carried 8 gold pairs; the 800-token ceiling killed the densest page), 12 are
bar-vs-instrument mismatches (non-dairy watchlist items, maker logos without a
price box, SKU-name-vs-TM granularity), 2 are gold noise, 4 pairs remain to be
read at the B′-prep acceptance. Ratified, all four parts: (a) **instrument v2** —
the parser family (asterisk-footnoted discounts, multipack pack-counts,
«від X грн» ranges become recorded WARNINGS that keep the position, never
page-refusals) and the positions ceiling 800 → **1200** (serving pin v2,
registered BESIDE v1); (b) **evidenced Latin aliases** enter the watchlist alias
table (Three Bears → try-vedmedi; Rud → rud; LIMO → limo) — an operator-owned
registry edit, ratified here; (c) **bar 1 re-scoped**: the B′ gold is the dairy
positions carrying a price box on the sent pages — class-b and class-c pairs
leave the denominator, derived from the decomposition verdicts, never re-judged
by the executor; (d) **one re-measurement** of instrument v2 over the same 138
elements under a B′ pre-registration BESIDE v4 (bars' verbatim thresholds
unchanged; gold and instrument shas move; cap **$0.40**), with every reading of
(9)–(12) in force. No new ML mechanism is authorised: the two-stage OCR and the
brands_visible channel stay named candidates, unbuilt.
<!-- sku-b-ratification-7 end -->
**Date:** 2026-07-26 · **Team lead:** Fable session · **Executor:** Claude Code
**Repo folder:** `/Users/hdv_1987/Desktop/Projects/market-pulse-llm`
**rev. 3 change (operator decision):** producers in Ukraine barely use Telegram for
consumer communication → observation points switch to **retail-chain channels**
(АТБ, Сільпо, Varus) + discount aggregators; tracked category fixed: **dairy (all
subcategories) + ice cream**, category-wide with a brand watchlist.

## 1. Mission

**Category Intelligence System** — the company's key marketing-research instrument
for the Ukrainian food retail market (UA / RU / EN). The system monitors Telegram
channels of leading retail chains (АТБ, Сільпо, Varus) and discount aggregators,
filters the stream to the tracked category (**dairy — all subcategories — and ice
cream**), detects new-product announcements and promos, extracts brand/product
mentions, and classifies audience reactions in comments (sentiment, sarcasm/irony,
hidden intents: taste / price / packaging / quality / availability). Output:
comparative analytics per brand (watchlist highlighted) and per launch. Core = one
fine-tuned open LLM (QLoRA on rented NVIDIA GPU), multi-task instruction format.

**MVP constraint (operator decision): Telegram-only, $0 data budget.**
X API, FB/IG scrapers, and website monitoring are future extensions behind a
source-agnostic connector interface — out of MVP scope, no code for them.

## 2. Data reality

| Item | Tag | Notes |
|---|---|---|
| Retail-chain Telegram channels via MTProto API (Telethon), free. Candidate handles — operator-provided: @silpoua, @atb_market_official, @varus_ua; search-found: @silposilpo, @VARUS_channel | [REAL: channels exist; exact handles UNVERIFIED] | PRIMARY sources. Phase 2 entry check resolves each chain via Telegram global search to the verified (blue-check) channel, then checks comments enabled + traffic. Loyalty chat-bots (@silpo_bot etc.) are OUT of scope. Constraints: dedicated account, conservative rate limits, graceful FloodWait, no member-list harvesting, join discussion groups to read comments |
| Discount aggregator channels: @znizhki_ua, «Хочу дешевше» and similar | [REAL: channels exist] | SECONDARY sources, tagged separately in provenance (deal-hunter audience bias). Same entry check |
| Broader UA food/dairy community channels | [ASSUMED] | Extra training corpus for slang/sarcasm; candidates collected in Phase 2 |
| Public datasets (RuSentiment, RuReviews, SemEval-2018 irony, UA sentiment corpora) | [ASSUMED] | Augmentation only; licenses verified in Phase 2 before use |
| Domain annotation: 1–2k labeled comments + 0.5–1k labeled retailer posts | [PLANNED] | Operator-in-the-loop; annotation guidelines are Phase 2 deliverables |
| Future: X API pay-per-use, FB/IG via managed scrapers, retailer/producer websites | [DEFERRED] | Researched & costed 2026-07; excluded from MVP by operator decision |

## 3. Registry (three entities, extensible without code changes)

- **Sources:** chain/aggregator → Telegram channels; `source_type:
  official_retail | aggregator | community`.
- **Category taxonomy:** tracked group = dairy with ALL subcategories (milk,
  kefir/ryazhanka, yogurt, curd/сирки, sour cream, butter, cheese, dairy
  desserts, plant-milk analogs) + ice cream. New groups are added by registry
  edit only.
- **Brand watchlist:** operator's own + priority competitor brands; highlighted
  in analytics. Category-wide coverage remains (watchlist prioritizes, never
  filters out the rest). Initial watchlist = Phase 2 deliverable (operator
  confirms).

## 4. Model tasks

One base LLM, QLoRA fine-tuned, multi-task via instruction prefixes:

- **T1 — Comment classification:** sentiment (pos/neg/neutral) + sarcasm flag +
  multi-label intents (taste/price/packaging/quality/availability). Ambiguous
  cases get explicit `unclear`, excluded from gates.
- **T2 — Retailer-post analysis:** (a) relevance to tracked category (binary);
  (b) for relevant posts: {new-product announcement, promo/discount, other};
  (c) extraction of brand + product mentions (normalized to watchlist entries
  where applicable). Trained from the start; zero-shot base LLM is its baseline.

## 5. Success metrics (pre-registered; the scorer is the judge)

**Tier 1 — Model (primary project gate), one attempt after full training:**
- G1a: frozen held-out comment test set (per-language UA/RU; EN excluded by
  amendment 3.1): fine-tuned sentiment macro-F1 ≥ best baseline + 5 pp overall;
  no gated language below its baseline by more than 2 pp.
- G1b: sarcasm slice — the rows of the frozen sarcasm holdout that the base
  model gets wrong (amendment 3.2 replaces the 150–200 curated examples of
  rev. 3): fine-tuned fixes ≥60% while overall macro-F1 degrades ≤2 pp.
- G1c: intents multi-label micro-F1 ≥ baseline + 5 pp.
- G1d: T2 post-type classification (3-class: launch / promo / other) macro-F1 ≥
  zero-shot base LLM + 10 pp on the frozen post test set. Binary relevance
  macro-F1 is reported beside it with its own n and is not gated (amendment
  3.3, which reads rev. 3's "relevance + 3-class" as the two metrics it is).
- G1e: T2 brand-mention extraction F1 (exact match after normalization) ≥
  zero-shot base LLM + 10 pp on the same frozen post test set.
- A failed gate closes the question; negative result is a result.

**Tier 2 — Pipeline:** smoke run: 1,000 real comments + 200 retailer posts
end-to-end (collect → filter → classify → aggregate → dashboard), ≥99% processed
without error; latency budget fixed before the run.

**Tier 3 — Business signal:** on ≥2 real new-product announcements in the dairy /
ice-cream category the system (a) detects the announcement post, (b) attributes
the correct brand, (c) produces a reaction verdict agreeing with a human check of
50 random comments (≥85% agreement).

Honesty rules: every published number has fixed seed + saved config + provenance;
comparisons paired on identical instances; comparison tables always include the
cheapest realistic baseline (TF-IDF+logreg and zero-shot); dashboard/README read
numbers only from result files and fail loudly if a source is missing.

## 6. Architecture (MVP)

source registry (sources + taxonomy + watchlist, YAML) → Telegram collector
(Telethon; incremental backfill + polling; append-only raw store JSONL/Parquet
with provenance incl. source_type) → normalize/dedup/lang-id → **category
relevance filter (T2a)** → model service (fine-tuned LLM, batch: T2b/c on posts,
T1 on comments of relevant posts) → aggregation store (per-brand, per-launch,
per-intent rollups; watchlist flag) → dashboard: launch feed + reaction
scorecards + negative-share by intent, brand vs brand. Connector interface is
source-agnostic so X/FB/IG/web can be added later without touching the core.

## 7. Model plan

- Base candidates (choice = Phase 4 gate, decided on baseline numbers, not
  vibes): Qwen3-8B/14B, Llama-3.1-8B, Gemma-3-12B — must be strong UA/RU.
- QLoRA on rented NVIDIA GPU (Vast.ai / RunPod, 24–48 GB); training budget
  time-boxed before Phase 4. Smoke run mandatory before any long run.
- Baselines BEFORE fine-tuning (pre-registered "before" numbers), per task:
  (a) TF-IDF + logistic regression (+ keyword rules for T2a relevance),
  (b) fine-tuned XLM-R encoder, (c) zero-shot base LLM with fixed prompt.

## 8. Phases & verify-gates

| Phase | Deliverable | Gate |
|---|---|---|
| 0 | Spec approved; folder, git init, second-brain layer, /init | DONE (rev. 2); rev. 3 approval pending |
| 1 | Repo skeleton: pytest + ruff green; scorer stubs; registry | DONE 2026-07-26 |
| 2 | Registry migration (sources+taxonomy+watchlist); Telegram collector; channel entry checks (АТБ handle found, comments enabled, traffic); corpus backfill; licenses verified; annotation guidelines (comments + posts); 1–2k comment labels, 0.5–1k post labels; FROZEN test sets | Entry-check report per channel; dataset cards; label QA (self-agreement ≥90%); test-set hashes committed |
| 3 | Baselines a/b/c for T1 and T2 scored by the shared scorer; numbers pre-registered | Scorer is single source of truth; results file committed |
| 4 | QLoRA multi-task fine-tune: smoke → full; gates G1a–e evaluated once | Tier-1 gates |
| 5 | Production loop: polling collector + batch inference + aggregation | Tier-2 smoke (1k comments + 200 posts) |
| 6 | Dashboard (launch feed, brand scorecards, negative-share by intent) reading result files only | No hand-typed numbers; loud failure on missing source |
| 7 | Real-launch validation on ≥2 category announcements + packaging | Tier-3 gate |
| R (deferred) | X / FB-IG / website connectors: legal, cost, go/no-go | Decision record per source |

## 9. Failure modes & risks

- Retail channels are high-volume and promo-dominated → T2a relevance filter is
  on the critical path; measure its precision/recall on the frozen post set.
- Some chain channels may have comments disabled → entry check per channel;
  fall back to aggregator/community channels for reactions.
- Aggregator audience bias (deal hunters skew negative on price) → source_type
  in provenance; report per-source splits, never blend silently.
- Brand extraction ambiguity (private labels, sub-brands, UA/RU spellings) →
  normalization table in registry; `unknown-brand` bucket reported explicitly.
- Telegram account restrictions → dedicated account, conservative limits,
  history reads only, graceful FloodWait, cursor resume.
- Launch labels are rare → months of historical backfill across all channels.
- Public-dataset domain mismatch → domain test set is the arbiter.
- Label noise / sarcasm subjectivity → guideline with examples; `unclear` label.
- GPU rental cost creep → time-boxed budget fixed before Phase 4.

## 10. Conventions

- Chat: Russian. All artifacts (code, comments, commits, docs, vault): English.
- Small diffs, atomic commits, executor never self-accepts; every phase ends
  with a report reviewed against the gate checklist.
