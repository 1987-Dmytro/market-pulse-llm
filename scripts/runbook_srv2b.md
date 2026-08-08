# Runbook — srv-2b: the serverless endpoint, from an empty account to a parity number

> **Written at srv-2a ($0, nothing created). Not executed.** Every number below is either
> read out of a committed record — the citation is beside it — or a `<placeholder>` that
> srv-2b fills from the console. **The cap is set at the srv-2b briefing and is a placeholder
> here on purpose:** a runbook that carries its own budget is a runbook that authorises itself.

**Contract:** SPEC amendment 3.14 (4) · parity clause 3.11 (2) · probe record
`docs/probe-serverless-20260808.md` · this session's contract `docs/PROMPT-srv-2a.md`.

**What srv-2b is for.** 3.14 moved the production runtime target back to serverless on the
evidence of a two-job probe. The probe proved delivery and nothing else — it says so itself,
in three pre-registered lines. srv-2b answers those three: which GPU the account is offered
*with a volume attached*, whether the NF4 base fits and stays byte-stable at batch 1 on that
card, and what a row costs against the pod's measured $0.5993/1000
(`results/serving_5b.json :: adopted.usd_per_1000_rows`).

**Classification mode only.** One endpoint will eventually serve three modes — captions
(base, adapter OFF), classification (adapter ON, thinking OFF), director-report narrative
(thinking ON). This runbook builds the second and nothing else, because the parity instrument
of 3.11 (2) must equal 4.5h2's exactly and the other two modes are a different instrument.

---

## A. The env/config contract

This is what the endpoint must be, stated before it exists. `serving.assert_serving` refuses
the run before the first paid row if the worker's own `info` disagrees with any of it.

### A.1 The environment the template passes

| Variable | Value | Where the value comes from |
|---|---|---|
| `SERVING_CONFIG` | `A` | 3.11 (2): the pair closed in favour of A (`results/parity_verdict_5b.json`), and merging stays forbidden. B is not built. |
| `ADAPTER_DIR` | `/runpod-volume/repo/results/train/45h2-arm-a/adapter` | the arm-A adapter, staged with the checkout |
| `BASE_WEIGHTS` | `google/gemma-4-31b-it` | `local_llm.MODEL_ID`; resolved out of the volume's HF cache, never fetched |
| `MODEL_REVISION` | `842da3794eaa0b77d5f08bae87a17459d91ff475` | `results/parity_5b_a.json :: config.runtime.model_revision` |

Four variables, and `scripts/serve_handler.py :: settings()` reads exactly those four
(`SERVING_CONFIG`, `ADAPTER_DIR` / `MERGED_DIR`, `BASE_WEIGHTS`, `MODEL_REVISION`). It raises
a `ValueError` naming the missing one rather than defaulting, and `Worker` loads lazily, so a
misconfigured endpoint answers the refusal instead of dying before it can say anything (5b.1
D8 — the first pod start refused for free, exactly this way).

**`HF_HOME` is deliberately NOT in the template.** `scripts/start_5b_worker.sh` exports it
unconditionally, so a template value would be overridden and would read like a knob that does
nothing. The entrypoint is the authority on the four process variables it owns:

    HF_HOME=/runpod-volume/hf     HF_HUB_OFFLINE=1
    PYTHONPATH=/runpod-volume/repo/src     TOKENIZERS_PARALLELISM=false

`HF_HUB_OFFLINE=1` is the load-bearing one: without it a cold start may decide to re-fetch
59 GB at worker rates, and nothing in the log would say that is what it is doing.

### A.2 The decoding facts, which are code and not configuration

| Fact | Value | Authority |
|---|---|---|
| merge state | `unmerged-adapter` | `serve_handler.describe` |
| adapter sha256 | `b3ca630846c7e75c5e7058ce45804c45a6bff5c49dcf2389cb8cdda0b7a68a6c` | `results/serving_5b.json :: worker.adapter_sha256`, over the **directory**, by `market_pulse.records.artifact_sha256` |
| quantization | NF4 · double quant · bf16 compute | `local_llm.QUANTIZATION` |
| chat template | `add_generation_prompt: true`, **`enable_thinking: false`** | `local_llm.CHAT_TEMPLATE` |
| decoding | greedy, `do_sample: false`, **batch 1** | `results/parity_5b_a.json :: config.generation` |
| max new tokens | 256 | `local_llm.MAX_NEW_TOKENS` |

Batch 1 is not a preference. Greedy is not batch-invariant on this stack — one row of 24
flipped its intents between batch 8 and batch 1 (ADR `phase4-own-pod-anchor` §(c)) — and the
pre-registered batch measurement of 5b.2 **failed** (`results/batch_5b2_verdict.json`), which
under 3.11 (2) fixes serving at batch 1 permanently. `scripts/eval_zero_shot.py` refuses any
served run above batch 1 outside `--batch-measurement`; do not pass that flag here.

### A.3 The stack, which is what makes config A a replica rather than a rebuild

| Library | Pin | Guarded? |
|---|---|---|
| torch | `2.8.0+cu128` | **yes** — `serving.assert_runtime_matches` |
| transformers | `5.14.1` | **yes** |
| bitsandbytes | `0.50.0` | **yes** |
| peft | `0.20.0` | **no** — reported only |
| accelerate | `1.14.0` | **no** — reported only |
| runpod | whatever installs | **no** — reported only |

The three pinned ones are read from `results/parity_5b_a.json :: config.runtime`, which is the
same record `assert_runtime_matches` compares against; they are not retyped from prose.

**torch comes from the image, not from pip.** `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`
carries the `2.8.0+cu128` build, and the venv is created `--system-site-packages` to inherit
it. A PyPI `torch==2.8.0` wheel reports `2.8.0` with no local version and would be refused at
the first `info` — one cold start too late. **The image tag is therefore part of this contract,
not a convenience of the create call.**

**`peft==0.20.0`, and where that number comes from.** peft is what applies the LoRA to the NF4
base, so it moves generated tokens — but the 4.5h2 anchor records no peft field, so
`assert_runtime_matches` cannot pin it and must not be made to pretend it does (a fourth entry
in `RUNTIME_LIBRARIES` would be a guard that never fires, because the anchor it reads has
nothing to compare). The number is the adapter's own: `results/train/45h2-arm-a/adapter/`
`adapter_config.json :: peft_version`, which is **inside the directory whose sha256 the guard
already checks**. It corroborates implementation-notes D7, where the 5b.1 fresh stage came out
at 0.20.0.

> **Do not copy the pin line from `scripts/runbook_5b2.md` §fresh staging.** It says
> `peft==0.18.0`, and the run it describes reported 0.20.0. That runbook is the honest record
> of a session that happened and is not edited here; this line is the correction.

### A.4 What the srv-2a verification looked at, and what it found

Read-only, on the Mac, with the outputs in the session report:

- **No pod paths are baked into the worker.** `grep -n '/workspace' scripts/serve_handler.py
  scripts/start_5b_worker.sh` returns nothing: every path is either an environment variable or
  `/runpod-volume`. The pod proof of 5b.1 ran the same files with `/workspace` values and a
  `ln -sfn /workspace /runpod-volume` — the split is the mount point, not the code.
- **The template's env and `settings()` agree**, field for field (§A.1).
- **The SDK entrypoint is proven, not assumed.** `runpod.serverless.start({"handler":
  Worker()})` with a callable object answered a three-row T2 batch on the pod on 2026-08-06 —
  the real `start.sh` → `serve_handler.py` path, not a mock and not an import check
  (implementation-notes, "The cold start and the entrypoint"; decision
  `5b-parity-abort-and-pod-runtime`).
- **The lazy load lands inside the first job's `executionTime`.** The model is loaded at the
  first job rather than at import, on purpose. On serverless that means the cold start —
  **278.9 s off a network volume** (`results/volume_calc_5c1.json :: inputs.cold_start_volume_s`)
  — is billed and timed as handler execution. So `--execution-timeout` must clear it with room,
  and the client's `HANDSHAKE_TIMEOUT` of 1800 s already does.
- **One fix was demanded and made:** the worker could not say which peft loaded the adapter.
  `serve_handler.library_versions()` now reports peft, accelerate and runpod inside the
  `runtime` block. Reported, never asserted — see §A.3 and the Deviations of
  `implementation-notes.md`.

---

## B. The volume plan

**Not an action.** No volume is created at srv-2a. This is the manifest srv-2b stages and the
two facts it must read rather than assume.

`gfwa2an8fn` (100 GB, CA-MTL-3) — the volume that carried all of this through 5b — **was
deleted** on the operator's option-(b) ruling, deletion proven by listing (implementation-notes
D22). Its contents are re-creatable, which is what option (b) meant. So srv-2b starts empty.

### B.1 Size and contents

100 GB, as before. The manifest and where each size is measured:

| Item | Size | Source | Re-creatable from |
|---|---|---|---|
| `hf/` — base weights at the pinned revision | 59 GB | `results/volume_calc_5c1.json :: inputs.weights_gb` | Hugging Face, at `842da379…`; ~4 min measured onto local NVMe (`inputs.stage_minutes`) |
| `venv/` — the pinned stack over the image's torch | ~20 GB | `results/volume_calc_5c1.json :: inputs.container_disk_note` | pip, §A.3 pins |
| `repo/` — the checkout | < 0.1 GB | a `git bundle` of the Mac's HEAD | git |
| `repo/results/train/45h2-arm-a/adapter/` | 467 MB | `scripts/runbook_5b.md` §1 | **the Mac only** — see below |
| `start.sh` | — | a copy of `scripts/start_5b_worker.sh` | git |

≈ 80 GB of 100. The 20 GB of slack is what config B would have needed and is not free to
reclaim mid-run; leave it.

**The adapter is the one item with a single copy.** `adapter_model.safetensors` is 467 MB and
gitignored, so it exists on this Mac and nowhere else. Before it is staged and after it lands,
hash the **directory** with `market_pulse.records.artifact_sha256` and match
`b3ca630846c7…`. Use that hasher and not `shasum` on one file: D22 burned a check on exactly
that mismatch — a single file's digest against a directory hash — and the directory hasher is
what re-derived the number.

### B.2 The two facts that are read, never assumed

**The price.** RunPod's console prints the monthly cost at creation; **read it there and paste
it into the spend record.** What this repo has is priors, and they are labelled as priors:
~$0.24/day observed while attached to nothing (`knowledge/hot.md`), $7.20/month as a run-rate
line (`knowledge/decisions/5b2-batch-measurement.md`), corroborated but not re-derived by
`results/volume_calc_5c1.json :: idle_rate_corroboration` (the quietest 10.67 h interval of
phase 4 implies $0.2528/day and is an upper bound). A prior is not a reading.

**The datacenter.** CA-MTL-3 appears above only as *where the deleted volume happened to live*.
It is not the choice. The choice is made in §C.3 by which GPU class serverless actually offers
**with a volume attached, today** — the D7 re-read the probe record pre-registers as unproven.
Only 18 datacenters support network volumes at all, and a volume pins the region, so the volume
is created *after* that reading and in the datacenter that reading selects.

---

## C. The procedure

Copy-paste, in order. **Budget: `<CAP>` of the $8 Phase-5 GPU line, set at the srv-2b
briefing**, with its own spend anchor written before the first spend and never regenerated.
`--step srv2b` gives the guard its own ledger, `results/spend_srv2b.json`, anchored on the
first call — no other phase's anchor is imported, and this one is never regenerated.

### C.0 Before anything (Mac, $0)

```bash
cd ~/Desktop/Projects/market-pulse-llm
git status --short                       # empty
make check                               # green
ruff format --check .                    # make check does not run the formatter
python3 scripts/runpod_guard.py --step srv2b --step-cap <CAP>
PYTHONPATH=src python3 scripts/smoke_5b.py --endpoint-id x --serving-config A --carve-only
runpodctl pod list -a; runpodctl serverless list; runpodctl network-volume list
```

The last two lines are the ones that matter. The carve rebuild costs nothing and refuses
unless it hashes to `8347abd74ae9…`, the sha arm A's own provenance recorded — it is the check
that killed 5b's first attempt before a GPU second was billed. The three listings establish
that the account is empty **before** srv-2b creates anything, which is what makes the same
three listings at the end a deletion proof rather than a hope.

### C.1 The D7 re-read, before the volume — the reading that picks the datacenter

D7 (2026-08-06) measured, one class at a time, in CA-MTL-3 with a volume attached:

| class | GPU | then |
|---|---|---|
| `AMPERE_48` | A6000 / A40 48 GB | no worker |
| `ADA_48_PRO` | L40S 48 GB | no worker |
| `AMPERE_80` | A100 80 GB | no worker |
| `ADA_24` | RTX 4090 24 GB | **allocated** |

That table is 2026-08-06 and the probe of 2026-08-08 already overturned its neighbouring
finding. Re-read it. **Preference order for this contract: a 48 GB class first if it is
offered with a volume, else 24 GB.** Probe by creating ONE endpoint at a time and deleting it
the moment it is not the one you want — a loop that creates before it reads bills every hit.

The authorisation chain, because a 24 GB card looks like it violates SPEC: 3.11 (1) fixed
**pods** on AMPERE_48 and left AMPERE_80 unauthorised, because on that path the GPU class was
the variable under measurement. 3.14 moves the target to serverless, and this contract
authorises 48 GB first / 24 GB otherwise. `assert_runtime_matches` deliberately does **not**
pin the GPU: which card the worker gets *is* the runtime delta 3.11 (2) exists to report.

**A class is "offered" only when a worker actually runs a job.** 5b's whole wall was endpoints
that reported a healthy worker and consumed nothing. Record the reading after §C.5, not before.

### C.2 Create the volume (the first billable thing)

100 GB, in the datacenter §C.1 selected. **Read the printed price and write it down.**

```bash
runpodctl network-volume create --name mp-srv2 --size 100 --data-center-id <DC>
runpodctl network-volume list            # exactly one, and its id
python3 scripts/runpod_guard.py --step srv2b --step-cap <CAP> --note "srv-2b volume created, console price <READ>/mo"
```

### C.3 Stage it (a pod at a third of the serverless rate)

A staging pod, not a worker: the serverless class bills ~3× and a staging mistake there costs
the boot *and* the handshake. `--terminate-after` is not optional — a staging pod is small
enough to forget and bills like a working one.

```bash
runpodctl pod create --name mp-srv2-stage --gpu-id <a card available in <DC>> --gpu-count 1 \
  --network-volume-id <VOL> --data-center-ids <DC> --cloud-type SECURE \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --container-disk-in-gb 30 \
  --ports '22/tcp' --ssh --terminate-after <UTC ISO8601, a couple of hours out>
runpodctl pod list -a                    # exactly one pod, and its costPerHr
runpodctl ssh info <POD_ID>
```

From the Mac — the bundle and the one file git does not carry:

```bash
SSHK=~/.runpod/ssh/runpodctl-ssh-key
SSHOPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
git bundle create /tmp/market-pulse-srv2.bundle HEAD
scp -i $SSHK $SSHOPT -P <PORT> /tmp/market-pulse-srv2.bundle root@<HOST>:/workspace/
scp -i $SSHK $SSHOPT -P <PORT> results/train/45h2-arm-a/adapter/adapter_model.safetensors \
    root@<HOST>:/workspace/adapter_model.safetensors      # 467 MB, gitignored — ~3 min
```

On the pod — **the volume is `/workspace` here and `/runpod-volume` on a worker**:

```bash
cd /workspace && rm -rf repo && git clone -q market-pulse-srv2.bundle repo
cd repo && git rev-parse HEAD && git status --short          # equals the Mac's HEAD, empty
cp /workspace/adapter_model.safetensors results/train/45h2-arm-a/adapter/
python3 -m venv --system-site-packages /workspace/venv       # inherit the IMAGE's torch
/workspace/venv/bin/pip install -q transformers==5.14.1 bitsandbytes==0.50.0 \
  peft==0.20.0 accelerate==1.14.0 runpod pyyaml               # PINNED, and deliberately NO torch
```

**Check the stack string before the 59 GB, not after it** — the three pinned libraries against
`arm_runtime()`, exactly as `scripts/runbook_5b2.md` §fresh staging does it, and then the
adapter's directory hash:

```bash
cd /workspace/repo && PYTHONPATH=src /workspace/venv/bin/python -c "
from pathlib import Path; import sys; sys.path.insert(0,'src')
from market_pulse import records
print(records.artifact_sha256(Path('results/train/45h2-arm-a/adapter')))"   # b3ca630846c7…
HF_HOME=/workspace/hf /workspace/venv/bin/python -c "
from huggingface_hub import snapshot_download
snapshot_download('google/gemma-4-31b-it', revision='842da3794eaa0b77d5f08bae87a17459d91ff475')"
cp scripts/start_5b_worker.sh /workspace/start.sh && chmod +x /workspace/start.sh
```

Then **prove the cold start here, on the ~$0.53/h pod, before a serverless second is billed** —
the 5b.1 pattern: launch the worker under the §A.1 environment with `/workspace` paths, watch
the *process* and not the log (`pgrep -af`), and require three things of it: `info` names
`adapter_sha256 b3ca630846c7…`, the three pinned libraries match, and a T2 row parses.

```bash
runpodctl pod delete <POD_ID>
runpodctl pod list -a                    # []
python3 scripts/runpod_guard.py --step srv2b --step-cap <CAP> --note "srv-2b staging + cold-start proof"
```

### C.4 The endpoint (creation is free; workers bill only on a request)

```bash
runpodctl template create --name market-pulse-srv2-a --serverless \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --container-disk-in-gb 30 \
  --docker-start-cmd "bash,/runpod-volume/start.sh" \
  --env '{"SERVING_CONFIG":"A","ADAPTER_DIR":"/runpod-volume/repo/results/train/45h2-arm-a/adapter","BASE_WEIGHTS":"google/gemma-4-31b-it","MODEL_REVISION":"842da3794eaa0b77d5f08bae87a17459d91ff475"}'

runpodctl serverless create --name market-pulse-srv2-a --template-id <TEMPLATE_ID> \
  --gpu-id <the class §C.1 selected> --gpu-count 1 --workers-max 1 \
  --network-volume-id <VOL> --data-center-ids <DC> \
  --idle-timeout 60 --execution-timeout 900 --flash-boot
```

Queue mode (the probe's, and the default) and **max workers 1**. Three flags are money and all
three default wrong:

- **`--workers-max 1`.** The default is 3, and 758 sequential `runsync` calls will happily spin
  up three workers — three 31 B cold starts, all billed, for a run that is batch 1 by contract.
- **`--execution-timeout 900`.** The default is `-1`. The flag takes **seconds** and stores
  milliseconds, so `600000` becomes a week of a hung worker. `serverless update` cannot change
  it — delete and recreate. 900 s is chosen to clear the 278.9 s cold start that lands inside
  the first job's execution time (§A.4) with room for the longest row.
- **`--idle-timeout 60`.** Long enough that 758 sequential rows keep one warm worker, short
  enough that a finished run stops billing. A shorter value re-pays the cold start mid-run.

**Scale-to-zero is a requirement of 3.14 and is NOT asserted by a flag here.** Minimum workers
0 is RunPod's default and the 5b create call never passed a flag for it, so this runbook does
not invent one: **confirm min-workers 0 in the console after creation**, before the smoke. A
resident worker bills through the ~12 h between the two collection passes a day that SPEC
3.11 (1) sets, which is the whole economic case 3.14 rests on.

### C.5 The smoke

```bash
PYTHONPATH=src python3 scripts/smoke_5b.py --endpoint-id <ID> --serving-config A \
    --adapter results/train/45h2-arm-a/adapter
python3 scripts/runpod_guard.py --step srv2b --step-cap <CAP> --note "srv-2b config A smoke"
```

Eight rows of the arm's own **train carve**, rebuilt and refused unless it hashes to
`8347abd7…`. No frozen test file is opened — the parity run is test v4's only exposure. The
smoke calls `assert_serving` and `assert_runtime_matches` before the first row, so a wrong
endpoint costs the handshake and stops.

> The contract names "the 3-row T2 batch that proved this stack on the pod". Those three rows
> were an ad-hoc check and **their input strings were never written down** — only their labels
> survive («Рудь … знижка 20%» → `launch`, «Акція на молоко Яготинське» → `promo`, «Графік
> роботи магазинів» → `relevant: false, other`). The carve smoke is the reproducible superset:
> hash-pinned, T2 rows included, and it is the instrument the record already reads. Run it, and
> **write the three T2 rows' text and replies into the session record this time**, so the next
> runbook does not have to make this note again.

PASS is three things, and any of them failing is a staging problem: `info` names the registered
adapter sha, all eight rows parse, and the per-row seconds are in the region already measured
(2.73 s/row at 4.5h2, 4.071 s/row over the whole 5b.1 paid run —
`results/serving_5b.json :: adopted.seconds_per_row`).

### C.6 Record the D7 re-read

Now — after a worker has actually consumed a job — write down which classes the account was
offered **with the volume attached**, which one allocated, and how long it took. "Offered" and
"allocates" are different facts and 5b is the proof.

### C.7 Parity — the one paid event

```bash
PYTHONPATH=src python3 scripts/eval_zero_shot.py --model google/gemma-4-31b-it \
  --backend endpoint --endpoint-id <ID> --serving-config A --batch-size 1 \
  --testset-version v4 --adapter results/train/45h2-arm-a/adapter --arm without-plast \
  --eval-checkpoint /tmp/parity-srv2.jsonl --record-out results/parity_srv2.json
```

758 rows, batch 1, one attempt, `retries=0` by design. `--eval-checkpoint` is passed for the
same reason 5b.2 passed it: a run that dies at row 700 has still been paid for.

**The rule, from 3.11 (2), pre-registered and not negotiable after the fact:** every gate that
passed at 4.5h2 stays passing — G1b (fix count), G1d, G1e against the bars in
`results/verdict_45h2.json` — and no gate head drops more than **0.005** against
`results/parity_5b_a.json :: parity.values`, which is the pod reading of the identical config.
The deltas are reported, never averaged away. A 4.5h2-passed head under its bar is a finding
for an operator briefing, not a verdict this session may issue.

### C.8 The cost reading

Take `usd_per_second` from the guard's own balance delta over the run divided by the run's
**wall** seconds — not by summed `executionTime`. A worker bills while it is up, including the
gaps between sequential rows.

What it is compared against, all from committed records:

| | pod (measured, 5b.1) |
|---|---|
| $/1000 rows | **0.5993** (`serving_5b.json :: adopted.usd_per_1000_rows`) |
| s/row, batch 1 | 4.071 |
| 758-row wall | 3085.4 s |
| cold start | 46.2 s off local NVMe · **278.9 s off a network volume** |
| $/pass (758 rows + one cold start) | **0.4611** |

Pre-registered arithmetic, so the answer is not argued for after the number lands:

- serverless per pass = `(cold_start_s + 3085.4) × usd_per_second`
- it beats the pod's $0.4611/pass only if the offered class bills under **$0.000137/s
  (≈ $0.49/h)** — derived as `0.4611 / (278.9 + 3085.4)`
- at the probe's observed **$0.00016/s** (`docs/probe-serverless-20260808.md`, a 16 GB flex
  class — a **prior**, and not the class this endpoint will run on), a pass is **$0.538**, i.e.
  **17% more than the pod**, of which **$0.045 is the boot alone** — 10% of a whole pod pass
  spent before a single row.

So the honest prior is that serverless may well be *dearer per row* than the stop-after pod,
and its case rests on what the pod path costs in allocation latency and staging minutes rather
than on $/row. Report the measured number against $0.5993/1000 and let the operator decide;
do not present a saving that the arithmetic above does not show.

### C.9 Close the session

```bash
runpodctl serverless delete <ID>
runpodctl template delete <TEMPLATE_ID>
runpodctl pod list -a; runpodctl serverless list; runpodctl network-volume list
python3 scripts/runpod_guard.py --step srv2b --step-cap <CAP> --note "srv-2b closed"
```

**Verify deletions by listing, never by an exit code.** Two `probe-cls` endpoints once
survived a delete call that silently targeted a mangled id and were found ~25 minutes later by
`runpodctl serverless list`. Read all three listings out loud.

**The volume persists** and becomes a run-rate line at the price §C.2 read. It is the only
thing srv-2b creates that outlives the session, and it is deleted only by an operator ruling —
D22 is the precedent, and it required the adapter's local copy to be hash-proven first.

---

## The abort ladder

Each rung: STOP, report, delete what the failed run created, prove the deletion by listing. No
retry without a new briefing — 3.11 (2) gives this measurement one attempt and a retry spends
an attempt the contract does not have.

| Rung | What it looks like | What it means |
|---|---|---|
| **No GPU with the volume** | every class §C.1 probes leaves the job `IN_QUEUE`, or no worker allocates | the 5b wall is back for volume-attached endpoints. The probe of 2026-08-08 was `n=2` on one evening and said so. STOP: delete the endpoints, keep the volume, report. |
| **OOM** | `torch.OutOfMemoryError` at load or in a row | the NF4 base does not fit the offered card. **Unproven and expected to be tight on 24 GB:** the model sits at **~20 GiB at rest** (implementation-notes, the 5b.2 OOM analysis; 4a's inference figure was 18.9 GB), which leaves ~4 GB on an `ADA_24` for KV cache and activations at ~772 prompt + 256 new tokens. No peak-VRAM figure for batch-1 inference exists in any record — this is a measurement, not a check. STOP, report the card and the allocation. |
| **Gate drop** | any 4.5h2-passed gate fails, or a head drops > 0.005 | the runtime changed the answers. That is a finding, reported with both readings side by side. It does not authorise a re-run, a re-tune or a bar edit. |
| **Over cap** | the guard exits 1 | a cap is not raised to finish a run. Whatever was bought is reported as bought. |
| **The handshake times out** | `info` does not answer inside 1800 s | the weights are not where `HF_HOME` says. Check that on a pod, not by re-running the endpoint. |
| **`assert_serving` / `assert_runtime_matches` refuses** | the worker is not the registered config | do not pass the check by editing the expectation. Find out what the worker loaded. |

**Fetch before you delete.** Anything written on the volume or the pod — sidecars, checkpoints,
logs — comes back to the Mac and is verified against the record *before* the only other copy is
destroyed, one command per artifact.
