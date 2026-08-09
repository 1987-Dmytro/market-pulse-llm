# Runbook — vis-b: the GM4 caption instrument on the serverless endpoint

> **Written at vis-a ($0, nothing created). Not executed.** Every number below is either read
> out of a committed record — the citation is beside it — or a `<placeholder>` vis-b fills from
> the console. **Cap: $1.00**, SPEC amendment 3.13 (4), anchored in `results/spend_5c1_vis.json`
> before the first job and never regenerated.

**Contract:** SPEC amendments 3.13 (the caption instrument) and 3.14 (the runtime) · this
session's contract `docs/PROMPT-5c1-vis-a.md` · the runtime procedure it inherits,
`scripts/runbook_srv2b.md` §§B–D, which is not restated here.

**What vis-b is for.** The yield screen refused to report because @atb_market_official's own 28
days carry 25 posts, **19 of them image-only**, no dairy, no ice cream, no watchlist brand
(`results/yield_screen_5c1.json`). The API pilot answered the modality question — those 19 posts
go **0 → 13** relevant once their pictures can be read (`results/caption_rematch_5c1.json`) — and
then 3.13 retired the instrument that answered it. vis-b re-buys that answer on the project's own
GM4 and reports whether the two instruments agree.

**One mode only.** The same endpoint will eventually serve three — captions (base, adapter OFF),
classification (adapter ON, thinking OFF), narrative (thinking ON). This builds the first.
`serve_handler.settings()` **refuses** `SERVING_CONFIG=CAPTION` beside `ADAPTER_DIR` or
`MERGED_DIR`, so the classification template cannot be reused by editing one field.

---

## A. The endpoint, from the template

### A.1 The environment the template passes

| Variable | Value | Where the value comes from |
|---|---|---|
| `SERVING_CONFIG` | `CAPTION` | SPEC amendment 3.13 (3): the NF4 base, adapter OFF |
| `BASE_WEIGHTS` | `google/gemma-4-31b-it` | `local_llm.MODEL_ID`; resolved out of the volume's HF cache, never fetched |
| `MODEL_REVISION` | `842da3794eaa0b77d5f08bae87a17459d91ff475` | `results/parity_5b_a.json :: config.runtime.model_revision` — the pinned revision, and `settings()` **refuses CAPTION without it** |

**Three variables, and no fourth.** `ADAPTER_DIR` and `MERGED_DIR` are not omitted for tidiness:
`settings()` raises on either of them, by name, because an endpoint updated from the srv-2d
template keeps srv-2d's environment and a caption worker that quietly loaded the classification
adapter would answer every job while every row it wrote still said `gm4-nf4-base`.

```bash
runpodctl template create --name market-pulse-vis-caption --serverless \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --container-disk-in-gb 30 \
  --docker-start-cmd "bash,-c,exec bash /runpod-volume/start.sh > /runpod-volume/worker-boot.log 2>&1" \
  --env '{"SERVING_CONFIG":"CAPTION","BASE_WEIGHTS":"google/gemma-4-31b-it","MODEL_REVISION":"842da3794eaa0b77d5f08bae87a17459d91ff475"}'

runpodctl serverless create --name market-pulse-vis-caption --template-id <TEMPLATE_ID> \
  --gpu-id ADA_24 --gpu-count 1 --workers-max 1 \
  --network-volume-id qw4nwleanc --data-center-ids EU-RO-1 \
  --idle-timeout 60 --execution-timeout 1800 --flash-boot
```

**1800, not 900** (vis-b's own correction to this line): the driver's per-request policy is
`execution_policy(1800, 3600)`, and hot.md's footgun says the endpoint value is what remains if
a per-request override silently fails. An endpoint budget *below* the request budget is a way to
lose a paid slice to a timeout with no retry. Read `executionTimeoutMs` back — the flag takes
seconds and stores milliseconds, so 1800 stores `1800000`.

**The stdout redirect is a standing line, not a diagnostic** (`runbook_srv2b.md` §D.1). RunPod's
troubleshooting page says logs "only appear for successfully initialized workers", so on the
failure that matters most the console channel is empty by design. It truncates
`/runpod-volume/worker-boot.log` at every worker boot — read it off the volume before creating
the next endpoint.

`ADA_24` in `EU-RO-1` because that is what the region catalogues at stock `none` with a volume
attached, measured at srv-2b's D7 re-read and used for the whole 758-row parity pass. The 48 GB
half was never offered there.

### A.2 The request policy is `serving.execution_policy` and nothing else

`--execution-timeout` on the create call **takes seconds and stores milliseconds**; the
per-request policy is in **milliseconds** and every briefing writes seconds. The one conversion
point is `market_pulse.serving.execution_policy(seconds, ttl)`, which refuses below RunPod's
documented minimums (5 s / 10 s) and refuses a ttl that does not outlast the execution budget —
the ttl clock starts at **submission**, so it has to cover the queue delay too. The driver
passes `execution_policy(1800, 3600)` and there is no other place in `src/` or `scripts/` where
a timeout is multiplied by a thousand; a test asserts that.

### A.3 The volume, and the one thing that must move on it

`qw4nwleanc`, 100 GB, EU-RO-1, **$0.009722/h settled** (`results/srv2c_bootlog.json`) — the only
standing resource. It already holds `hf/` at the pinned revision, the pinned `venv/`, the adapter
and `start.sh` byte-identical to `scripts/start_5b_worker.sh`. **`repo/` is at `ed9c0c9` and must
be re-staged to this session's commit**, because `caption_post_gm4`, `CaptionClient` and the
CAPTION branch of `settings()` did not exist then.

Stage it with `runbook_srv2b.md` §C.3, and then read the footgun that is waiting there:

> **A `git fetch` naming a missing ref leaves the OLD `FETCH_HEAD`,** so the `merge --ff-only`
> after it prints `Already up to date.` and moves nothing. `git bundle create f.bundle
> <base>..HEAD` names its ref **`HEAD`**, not `main`. End the deploy with a **content** check —
> `git bundle list-heads` names the real ref in one command.

This runbook has a second, cheaper net for exactly that failure: the worker reports
`caption_prompt_sha256` in `info`, and `caption_gm4_5c1.py` refuses before the first paid caption
unless it equals the sha this Mac renders. A volume a session behind fails the handshake instead
of captioning happily under the old prompt.

**Stage the volume BEFORE the endpoint exists, and never merge into a volume an endpoint is
already serving.** vis-b learned this at $0.16: a running worker has already imported
`serve_handler` and every module under it, so a `git merge` on the volume changes the files on
disk and reaches nothing. There is no reload lever — `serverless update` does not restart a
worker, and vis-b's `--idle-timeout 60` did **not** stop one that had failed a job (health read
`workers.running: 1` fifteen minutes and two full weight reloads later). The only restart is
**delete the endpoint**, which is why the order is not a preference:

1. staging pod → `repo/` at the session's commit, content-verified, pod deleted;
2. template + endpoint;
3. handshake, and from here the code on the volume is frozen for the session.

A code fix discovered after step 2 costs a new endpoint, and this contract forbids one.

### A.4 The decoding facts, which are code and not configuration

| Fact | Value | Authority |
|---|---|---|
| merge state | `base-no-adapter` | `serving.MERGE_STATE` |
| adapter | **none**, asserted on the loaded object | `serve_handler.assert_no_adapter` |
| quantization | NF4 · double quant · bf16 compute | `local_llm.QUANTIZATION` |
| chat template | `add_generation_prompt: true`, **`enable_thinking: false`** | `local_llm.CHAT_TEMPLATE` |
| decoding | greedy, `do_sample: false`, **forward batch 1 always** | `local_llm.CaptionClient` |
| max new tokens | **400**, not 256 | `local_llm.CAPTION_MAX_NEW_TOKENS` — 4.5g2 measured a six-image leaflet running past 600 tokens under the same task, and a caption cut off before its closing sentence has no parse failure to count |
| prompt | `caption_post_gm4`, `41d33d0299fe…` | `prompts.prompt_sha256`, derived from `caption_post` by one clause |
| images per post | **6**, the number the API instrument sent | `caption_posts.MAX_IMAGES` — the bridge compares models, not inputs |

---

## B. The smoke: one post, and the dump read back byte for byte

```bash
cd ~/Desktop/Projects/market-pulse-llm
git status --short && make check && ruff format --check .
python3 scripts/runpod_guard.py                       # the phase cap, before anything
runpodctl pod list -a; runpodctl serverless list; runpodctl network-volume list

PYTHONPATH=src python3 scripts/caption_gm4_5c1.py --scope smoke1 \
    --endpoint-id <ID> --only @atb_market_official:4340 \
    --dump-prefix /runpod-volume/captions_visb_smoke \
    --record results/serving_visb_smoke.json --out results/smoke/gm4_smoke1.jsonl
```

**`--record` to a NEW path, always.** `smoke_5b.py --record` defaults to
`results/serving_5b.json`, the pod's cost anchor — the `adopted` block every serverless
comparison is measured against ($0.5993/1000, $0.4611/pass, 4.071 s/row). A smoke without an
explicit path overwrites the baseline with the number under test. `caption_gm4_5c1.py` has no
default that can do that (its record is `results/captions_gm4_<scope>.json` and it refuses to
overwrite an existing one), and this line is here so the habit survives the next script.

PASS is four things:

1. the handshake refuses nothing — `info` answers `CAPTION` / `base-no-adapter` /
   `caption_prompt_sha256 41d33d0299fe…`, which is `assert_serving` reading the worker's own
   account before a single caption is generated;
2. **one** post comes back with a caption that is Ukrainian prose about a shelf, not a JSON
   object and not a paragraph of reasoning (`enable_thinking: false` plus the prompt's own
   closing clause);
3. `finish_reason` is `stop`. `length` means 400 tokens was not enough and the caption stops
   mid-leaflet — a finding, not a retry;
4. **the dump on the volume matches the reply byte for byte.** Fetch it before deleting
   anything (§ the abort ladder):

**The host in the next line is a POD, not the worker** — a serverless worker exposes no SSH, so
the only way off the volume is a cheap pod with it mounted (at `/workspace` there,
`/runpod-volume` on the worker). srv-2d paid $0.0363 for two RTX 2000 Ada pods, staging and the
dump fetch, at $0.24/h — the cheapest class EU-RO-1 catalogues in stock.

```bash
scp -i ~/.runpod/ssh/runpodctl-ssh-key -P <PORT> \
    root@<HOST>:/workspace/captions_visb_smoke_00.jsonl /tmp/visb_dump.jsonl
python3 - <<'PY'
import json
dump = [json.loads(line) for line in open("/tmp/visb_dump.jsonl")]
record = json.load(open("results/serving_visb_smoke.json"))
rows = [json.loads(line) for line in open("results/smoke/gm4_smoke1.jsonl")]
assert [row["sha8"] for row in dump] == record["jobs"][0]["sha8"], "the dump is not these posts"
assert dump[0]["reply"]["content"].split() == rows[0]["caption"].split(), "reply != written row"
print("dump matches:", dump[0]["sha8"], len(dump))
PY
```

The `sha8` is `serving.album_key` over the post's data URLs, hashed by the worker and written
into the driver's record by the Mac — one join rule read from both sides, so a dump recovered on
its own can be **checked** against the manifest rather than trusted to be in the order somebody
remembers sending.

```bash
python3 scripts/runpod_guard.py --note "vis-b smoke, 1 post"
```

---

## C. The measured session

### C.1 The rate, and the projection that authorises the rest

The caption rate is **not known** and nothing in this repo can predict it: the API pilot's
$0.000948/post priced a different vendor's model, and a caption's prompt is images, not the
~772 text tokens the parity pass measured. So it is measured on the smoke and the projection is
arithmetic over two observations, exactly as `serving.project_pair_usd` does for the pair:

```
$/post   = wall seconds per post x $0.00030669/s     # results/srv2d_cost.json :: rate
19 posts = 19 x $/post + $0.0733                     # cold start 239.022 s on this endpoint,
                                                     # results/srv2d_cost.json :: inputs
```

**If 19 posts project above $0.50, STOP and report** — half the $1.00 cap, because vis-b still
owes the re-pilot, the bridge and the screen after it, and a cap is not raised to finish a run.
Record the measured `$/post` and `s/post` beside the pod and API figures; the 5c2 briefing prices
the remaining 232 posts off this number and off nothing else.

### C.2 The re-pilot: the same 19 ATB posts

```bash
PYTHONPATH=src python3 scripts/caption_gm4_5c1.py --scope atb19 --endpoint-id <ID> \
    --dump-prefix /runpod-volume/captions_visb_atb19
python3 scripts/runpod_guard.py --note "vis-b re-pilot, 19 ATB posts"
```

The same manifest, the same 19 posts, the same six-images-per-post the API instrument sent
(`results/post_media_5c1.json`, 159 images, **108 sent**). Eight jobs at ≤8 MB — the pictures
travel **inside the job** because `data/annotation/**` is gitignored and cannot ride to the
worker on the volume, and RunPod documents **10 MB on `/run`**. The largest ATB post encodes to
3.68 MB and the largest slice to 7.83 MB; a post that would not fit on its own is a refusal, not
a truncated album.

Writes `data/annotation/captions_5c1/gm4_atb19.jsonl` and `results/captions_gm4_atb19.json`.
Every row carries `caption_source: "gm4-nf4-base"`; the qwen file beside it carries
`qwen-4.5g2`, and both readers refuse a file that mixes the two unless its record names both.

### C.3 The bridge: GM4 against qwen on identical posts

Two instruments, one task, the same 19 posts — the comparability seam 3.13 (1) created, made
visible instead of averaged. It costs nothing: both caption sets are already on disk.

```bash
# the same matcher, the same lexicon, the same untouched bars — on the GM4 captions
PYTHONPATH=src python3 scripts/rematch_with_captions_5c1.py \
    --captions data/annotation/captions_5c1/gm4_atb19.jsonl \
    --out results/caption_rematch_gm4_5c1.json

python3 - <<'PY'
import json
rows = lambda p: {r["msg_id"]: r for r in map(json.loads, open(p))}
qwen = rows("data/annotation/captions_5c1/atb_captions.jsonl")
gm4 = rows("data/annotation/captions_5c1/gm4_atb19.jsonl")
terms = {
    arm: {post["msg_id"]: sorted(post["terms"]) for post in json.load(open(path))["posts"]}
    for arm, path in (
        ("qwen", "results/caption_rematch_5c1.json"),
        ("gm4", "results/caption_rematch_gm4_5c1.json"),
    )
}
print(f"{'msg_id':>7}  {'qwen terms':<26} {'gm4 terms':<26} agree")
for msg_id in sorted(set(qwen) & set(gm4)):
    q, g = terms["qwen"][msg_id], terms["gm4"][msg_id]
    print(f"{msg_id:>7}  {str(q):<26} {str(g):<26} {q == g}")
    if q != g:  # quote both captions wherever the instruments disagree
        print(f"         qwen: {qwen[msg_id]['caption'][:160]}")
        print(f"         gm4 : {gm4[msg_id]['caption'][:160]}")
print("posts:", len(set(qwen) & set(gm4)), "· both empty is agreement too")
PY
```

The table goes into the session record whole, per post, with both captions quoted for any post
where the two instruments disagree. **An agreement rate is a description and gates nothing** —
what it is for is telling a reader of a future screen number which instrument produced it.

### C.4 Bar A, against the untouched pre-registration

`results/yield_bars_5c1.preregistration.json`, sha
**`1aa898180b01762d909e29997db659d2dc70931816855f4c0325b1ea1c892f2b`** — the file
`results/yield_screen_5c1.json` records that sha against, and `yield_screen_5c1
.check_preregistration()` re-hashes at every run. **It does not move here.** `rematch` re-derives
the *before* reading and refuses if it cannot reproduce the zero the signed screen reported: if
the before cannot be reproduced, the after is a number about a different instrument.

**The pre-registered instrument-failure rule (3.13 (4)), and it is not this session's to
soften:** if ATB with GM4 captions **fails bar A where qwen's PASS stands**, the instrument
failed. STOP — the fork returns to the operator with the bridge table of §C.3. Do not re-word the
prompt, do not raise the image count, do not re-run.

### C.5 Close the session

```bash
runpodctl serverless delete <ID>
runpodctl template delete <TEMPLATE_ID>
runpodctl pod list -a; runpodctl serverless list; runpodctl network-volume list
python3 scripts/runpod_guard.py --note "vis-b closed"
```

**Verify deletions by listing, never by an exit code** — two `probe-cls` endpoints once survived
a delete call that silently targeted a mangled id. Read all three listings out loud. The volume
persists and is the only thing that outlives the session.

Two readings of the spend, both reported: `results/captions_gm4_atb19.json :: cost.usd` (this
session's own balance anchor) and `runpod_guard.py` (the phase). Both are **floors** — the
balance settles minutes to hours behind the resource (Dv33) — and `runpod_guard`'s itemised
walk reads `billing serverless` since srv-2c, so the corroboration exists but still lags.

---

## The abort ladder

Each rung: STOP, report, delete what the failed run created, prove the deletion by listing.
**No retries anywhere** — the driver makes one attempt per slice and names a failed one in the
record rather than re-asking it, because a serverless worker bills while it fails.

| Rung | What it looks like | What it means |
|---|---|---|
| **`settings()` refuses at boot** | the worker never answers `info`; `worker-boot.log` names `ADAPTER_DIR` or `MODEL_REVISION` | the template carries the classification environment or an unpinned base. Fix the template, not the code. |
| **`assert_serving` refuses** | the driver stops before the first caption, naming the field | most likely `caption_prompt_sha256`: the volume's `repo/` is a session behind (§A.3). Re-stage and check the content, never pass by editing the expectation. |
| **OOM** | `torch.OutOfMemoryError` at load or in a forward | the vision tower's activations do not fit beside a 24 GB NF4 base. **Unmeasured:** srv-2b measured 19 874 of 24 564 MiB with the *adapter* and text-only inputs, and six images of a leaflet is a different allocation. STOP, report the card and the allocation — this is a measurement, not a check. |
| **`finish_reason: length`** | a caption used all 400 tokens | the description stopped mid-leaflet. Report the posts; do not silently raise the budget, which would make the bridge compare two ceilings. |
| **Over the §C.1 projection** | 19 posts project above $0.50 | STOP before the re-pilot. Report the measured rate — that number is what the 5c2 briefing needs anyway. |
| **Over cap** | the guard exits 1, or the driver's own anchor reaches $1.00 | a cap is not raised to finish a run. Whatever was bought is reported as bought. |
| **Bar A fails where qwen passed** | §C.4 | the pre-registered instrument failure. The fork returns to the operator with the bridge table. Not a prompt revision. |
| **A worker restarts** | any restart with a job still queued | srv-2b: 31 minutes at $0.00031/s for nothing. Watch **the first job's status**, not the worker's health, and delete the endpoint on the first restart. |
| **A worker does NOT restart** | the same failure twice, and `/health` still reads `workers.running: 1` | vis-b: the boot log was **appended to**, not truncated — one `Starting Serverless Worker`, one worker id, two full weight loads. The container is alive with the old modules imported, and a volume `git merge` cannot reach it. ~$0.031 per failed handshake. Delete the endpoint; there is no other restart lever. |

**Fetch before you delete.** The row dumps, `worker-boot.log`, anything written on the volume —
one command per artifact, verified against the record, **before** the only other copy is
destroyed. An async `/run` result is deleted 30 minutes after the job completes; the volume is
the only durable copy while a job is in flight.
