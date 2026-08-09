<!-- AUTO-GEN START (refreshed by scripts/refresh-hot-cache.py) -->

# Hot Cache

**Auto-refreshed:** 2026-08-09 10:45:00 (every SessionStart)
**Branch:** `main`

## 🔀 Recent commits (top 5)

```
23ea209 docs(srv-2d): one balance, one moment -- the phase figure was a stale reading
824f716 docs(srv-2d): the live state stops saying the attempt is unspent
f276aaa docs(srv-2d): the report, and six deviations
6fcfa5e feat(srv-2d): the parity attempt is spent, and it holds
76a1b31 feat(srv-2d): the 0.005 clause stops being prose
```

## 📋 Recent decisions

- `INDEX.md` — Decision records
- `srv2-serverless-runtime-target.md` — The 5b wall did not reproduce, and the production runtime target moves back to serverless
- `5c1-relevance-floor-and-discovery.md` — 5c1 — the relevance floor: 66 channels were admitted without anyone measuring the category

## 📅 Recent daily logs

- `2026-08-09.md`
- `2026-08-08.md`
- `2026-08-07.md`

<!-- AUTO-GEN END (everything below preserved across refreshes) -->

# Hot Cache — curated

**Last update:** 2026-08-08 (`/close`). **Day closed: six contracts, $2.3939 spent, and the
serverless question is answered by measurement rather than argument.** The headline —
`docs/PROMPT-srv-2d.md` executed, **the single SPEC 3.11 (2) parity attempt is SPENT and it
HOLDS** — and the team lead accepted it the same night: serverless is the ruled runtime and 5c1 is
off HOLD. This block is hand-edited; the section above it is auto-generated — do NOT touch the
marker. Long form: `implementation-notes.md`, and the day's log [[2026-08-08]]. ADRs:
[[srv2-serverless-runtime-target]] · [[5c1-relevance-floor-and-discovery]] ·
[[5c1-day2-composition-and-search]] · [[5b2-batch-measurement]].

## 🔥 What's Hot

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
the 1.7.11–1.10.0 job-tracking bug), `repo/` at **`ed9c0c9`**, the adapter at `b3ca6308…`, and
`start.sh` byte-identical to `scripts/start_5b_worker.sh`. Everything else is deleted and proven
deleted by listing.

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

**THE RUNTIME IS RULED, AND IT IS SERVERLESS.** The team lead accepted srv-2d the same night
(`docs/STATUS.md`, "ТЫ ЗДЕСЬ — serverless ДОКАЗАН (паритет Δ=0); 5c1 снят с HOLD"): parity verified
against the artefacts, **serverless validated as the runtime**, ruling 23 executed, **5c1 comes off
HOLD**, and the vis contracts are re-issued against the endpoint. The cost finding was accepted as
a finding **against** the chosen path and goes into the 5c2 briefing rather than being argued away
— their reading of the same artefacts, $1.0825/pass against $0.4611 (×2.35), matches
`results/srv2d_cost.json` (the per-1000 ratio is 2.38 on a different denominator, both correct).

**NEXT SESSION: vis-a / vis-b on the endpoint** (flyer captions) → screen v2 → the composition
signature. Team-lead debt for the morning, deliberately deferred to daylight: the ADR closing the
srv-2 programme, and the operator quiz.

**Three things srv-2d built that the next session inherits.** The worker takes `batch_size` and
`dump_path` in a job, so one job carries a whole input slice at forward batch 1 and writes every
reply to the volume as it goes (an async `/run` result is deleted 30 min after completion, and
"logs only appear for successfully initialized workers" — the volume is the log channel, not a
diagnostic to remove). `serving.execution_policy(seconds, ttl)` is the single seconds→milliseconds
conversion for RunPod's request policy. `serve_handler.assert_sdk_version` refuses to boot below
`runpod 1.10.1`.

**Still open on the 5c1 track, none of it started:** the launch signature is the operator's, on the
v2 numbers; the discovery session is a separate future contract (3.12 (2)); the candidate reserve is
untouched — `results/harvest_mothers_ua.json` (79 recommendations, 3 genuinely in-segment), five
unaccepted city analogues in `results/entry_gate_5c1.json :: notes.*_broadcast_analogue`, reserve
#4 (12 handles) and the private track, RECORDED and not actioned.

## 🚧 Blockers

**None, technical.** The 2026-08-07 FloodWait wall cleared at 10:02:05 UTC and ~100 resolves drew
no new one — because every collection run carried `--only`. That is discipline, not luck.

**Budget is the live constraint.** Phase 4 stands at **$20.8844 of $25.00, $4.1156 left** (read
2026-08-08 22:34:28Z; still settling — Dv33). Today spent $2.3939 across four paid sessions.
`pod list -a` → `[]`, `serverless list` → `[]`; only the volume stands.

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
  never edit — the deny rules refuse `Edit` *and* `Write` on them, without a restart. Phase-end
  facts go to the daily log or `implementation-notes.md`. The refusal reads "File is in a directory
  that is denied", but the rules are file-scoped: the rest of `docs/` is still writable.
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
