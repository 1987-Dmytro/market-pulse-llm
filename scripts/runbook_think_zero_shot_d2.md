# Runbook — `think-zero-shot` D2: one pod, seven stages in value order, $8.00

`results/prereg_think_zero_shot.json` is the law. It registers **readings, not bars**, so there is
no gate script and no `--watch`: the four rungs are executed here, by hand, against numbers the
platform and `results/measurements.jsonl` return. **Nothing in this file may add a number the
record does not carry.**

**The meter starts at `pod create` and stops at `pod delete`.** Not at ssh, not at the model load.
A pod bills for existing and `pod stop` does NOT stop it. **Delete, never stop.**

**One attempt per stage.** A stage that dies is not re-run; its column is missing from the table
and the report says so.

## The four rungs, and where each one lives

| rung | the law | executed as |
|---|---|---|
| 0 | price ≤ $0.80/h at create | read `costPerHr` out of the create response, before ssh |
| 1 | liveness — 900 s from the LAST reply **or `nvidia-smi` activity** | the poll loop below reads BOTH; thinking is silent longer than JSON |
| 2 | projection after the smoke and after every stage at the MEASURED s/call | `scripts/project_think_zero_shot.py` |
| 3 | platform hard stop from the cap at the observed price | `--terminate-after`, an ABSOLUTE UTC datetime (`pod create --help`) = create + cap ÷ price |

Rung 2's verdict: at or under the cap **GO**; over by ≤20% **ASK** — hold the pod ≤10 min for the
operator's typed word, quoted verbatim in the report, silence = KILL; over by more **KILL**.
`stop_after_stage` names the last stage that fits, and the value order IS the drop order.

## What the stages write, and why two of them are already partly answered

| # | stage | units | out-file on the pod | new calls |
|---|---|---:|---|---:|
| 1 | smoke — the longest pass-2 thread | 1 | `pass2_signals_r2_remainder.READER_THINK.jsonl` | 1 |
| 2 | smoke — three dev rows | 3 | `pass1_dev_v2.READER_THINK.jsonl` | 3 |
| 3 | v2 + think on dev-200 (`--only v2`) | 200 | `pass1_dev_v2.READER_THINK.jsonl` | 197 |
| 4 | pass 2 + think, reference | 11 | `pass2_signals_r2_reference.READER_THINK.jsonl` | 11 |
| 5 | v1 + think on dev-200 (`--only base`) | 200 | `pass1_dev_base.READER_THINK.jsonl` | 200 |
| 6 | v2 + think on holdout-100 | 100 | `pass1_holdout_100_v2.READER_THINK.jsonl` | 100 |
| 7 | pass 2 + think, remainder | 68 | `pass2_signals_r2_remainder.READER_THINK.jsonl` | 67 |

**579 renderings, 575 new calls after the two smokes.** The smoke's thread `@mandziak:3679` is one
of the remainder's 68 and the dev smoke's three rows are three of stage 3's 200 —
`already_answered` skips both, and the projector counts them the same way. Every out-file carries
`.READER_THINK`, so **no BEFORE column is ever written to**: `pass1_dev_base.jsonl`,
`pass1_dev_v2.jsonl` and `pass2_signals_r2_v1.jsonl` are pinned by sha in the record and are the
left half of the table.

## 0 — before anything exists ($0)

```bash
make check-stamped                         # HOLDS at HEAD, or nothing below is provable
runpodctl pod list -a                      # [] — nothing of ours is billing
runpodctl network-volume list              # mp-srv2 present: the POSITIVE CONTROL for teardown
PYTHONPATH=src python3.11 scripts/runpod_guard.py --step think-zero-shot --step-cap 8.00 \
  --note "think-zero-shot D2, before the create"
PYTHONPATH=src python3 scripts/preflight_serving_guards.py | grep -c '^PASS'
```

## 1 — create (the meter starts here)

Ruling (о) names the card: **RTX PRO 4500, 32 GB, $0.72/h secure, EU-RO-1** — the volume's own
datacenter. **A refused create costs $0 and creates nothing.** One fallback create on a 4090 at
$0.74 is pre-authorized by the contract; anything else is a STOP.

```bash
runpodctl pod create --name mp-think-zero-shot --gpu-id 'NVIDIA RTX PRO 4500 Blackwell' \
  --gpu-count 1 --network-volume-id qw4nwleanc --data-center-ids EU-RO-1 --cloud-type SECURE \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --container-disk-in-gb 30 \
  --ports '22/tcp' --ssh --terminate-after '<create + 8.00/costPerHr hours, UTC ISO8601 with Z>'
```

Read `costPerHr` back OUT of the response. **Rung 0 refuses anything above $0.80/h** — delete at
once and report; the create is not the attempt.

## 2 — ssh, stage, and the VRAM sampler

```bash
: "${SSHK:=$HOME/.runpod/ssh/runpodctl-ssh-key}"
runpodctl ssh info <POD_ID>                # poll on '"port"', BOUND BY THE CLOCK, never a count
git bundle create /tmp/market-pulse-think.bundle HEAD
scp -i "$SSHK" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P <PORT> /tmp/market-pulse-think.bundle root@<HOST>:/workspace/
ssh -i "$SSHK" ... -p <PORT> root@<HOST>
# on the pod:
cd /workspace && rm -rf repo && git clone -q market-pulse-think.bundle repo
cd repo && git rev-parse HEAD && git status --short     # equals the Mac's HEAD, empty
ls -d /workspace/venv /workspace/hf && du -sh /workspace/hf   # the volume is warm, or STOP
rm -rf /workspace/run && mkdir -p /workspace/run && ls /workspace/run   # empty — the proof
```

**Peak VRAM has no producer in the runner**, and stage 1 owes it a row. A sampler beside the run is
the whole fix — no code, no moved pin:

```bash
nohup sh -c 'nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -l 5' \
  > /workspace/run/vram.log 2>&1 &
```

It reads `memory.used` — the whole process including the CUDA context — which is **not**
`torch.cuda.max_memory_allocated()`, the instrument behind the `gpu_gb_peak` numbers in
`results/train/*/provenance.json`. The ledger row says which one it is, or the two get compared
([[two_instruments_two_inputs]]).

## 3 — one command per stage, in the record's order

Pass-1 stages (`--serving READER_THINK`, ceiling 4 000):

```bash
cd /workspace && HF_HOME=/workspace/hf PYTHONPATH=/workspace/repo/src nohup \
  /workspace/venv/bin/python -u /workspace/repo/scripts/pass1_fewshot_pod_runner.py \
    --pack /workspace/repo/results/<PACK> --outdir /workspace/run --repo /workspace/repo \
    --serving READER_THINK <--only v2 | --only base> \
    > /workspace/run/stage<N>.log 2>&1 & echo $!
```

Pass-2 stages (ceiling 8 000) are the same line with `pass2_r2_pod_runner.py` and no `--only`.

**Poll after every launch and never leave the pod unpolled.** Rung 1 needs BOTH signals, because a
thinking model writes nothing for minutes:

```bash
ssh ... -p <PORT> root@<HOST> \
  'tail -2 /workspace/run/stage<N>.log; tail -1 /workspace/run/vram.log; \
   wc -l /workspace/run/<OUT>'
```

After every stage completes: pull the out-file, hash both sides, then rung 2.

```bash
scp -i "$SSHK" ... -P <PORT> root@<HOST>:/workspace/run/<OUT> results/<OUT>
python3 scripts/project_think_zero_shot.py --usd-per-hour <costPerHr> \
  --elapsed-seconds <now − create> --load-seconds <measured at stage 1>
```

The smoke writes three rows into `results/measurements.jsonl` — `think_pass2_seconds_per_thread`,
`think_pass1_seconds_per_call`, `think_peak_vram_gb` — each with the out-file as its `source`.
**Until they are there the projector refuses to project**, which is the point: a remembered rate
priced pass-2 4.1× wrong on 26.08.

## 4 — pull everything, delete, prove it

One command per artifact, hashed on both sides, BEFORE the deletion.

```bash
ssh ... -p <PORT> root@<HOST> 'cd /workspace/run && find . -type f | sort | xargs sha256sum'
# ... one scp per file ...
runpodctl pod delete <POD_ID>
runpodctl pod list -a           # []
runpodctl serverless list       # [] — nothing was ever created here
runpodctl network-volume list   # mp-srv2 AND mp-lora-c both present, unchanged
PYTHONPATH=src python3.11 scripts/runpod_guard.py --step think-zero-shot --step-cap 8.00 \
  --note "think-zero-shot D2, pod deleted"
```

Then re-hash the three BEFORE files against the record — nothing may have been written to them.

## What must NOT change

* No edit to any prompt text, pack, gold or sealed record. The registration pins
  `scripts/reader_v5_pod_runner.py` at its PRE-step-0 sha and is **not** re-pinned; no pack pins the
  runner, so the handshake on the pod is unaffected, and `tests/test_think_zero_shot.py` derives
  that allowance from the live shas in both directions.
* Nothing is tuned after a reply is seen — no prompt, no pack, no ceiling.
* Never a second billing resource. **Never touch `mp-lora-c`.**
* No number invented that a file does not carry.
## AMENDMENT — five things settled at $0 after the runbook was written

**1. `--terminate-after` is 9 h 45 min, not cap ÷ price, and it CANNOT be changed after create.**
`runpodctl pod update` has no such flag (`--help` is the authority), so the number typed into the
create is final. Rung 3 says «hard stop from the cap at the observed price», and the guard's step
counter is a BALANCE DELTA — it counts the network volumes too. So the window is computed at the
rung-0 CEILING price plus the measured volume drip, and a create that comes back dearer than
expected still cannot cross the cap:

    $8.00 / ($0.80 + 2 x $0.0103/h) = 9.749 h  ->  9 h 45 m
    at the expected $0.72/h that window costs $7.2208; at the $0.80 ceiling, $8.0008

The volume rate is the guard's own reading: network-volume $2.4986 since the 2026-08-16 anchor.

**2. EU-RO-1 stock, read before the create ($0).** `RTX PRO 4500 Blackwell` — **Low** (the
contract's card, available). `NVIDIA GeForce RTX 4090` — **none**. `NVIDIA RTX A6000` — **none**
(and $0.53/h, so ruling (о)'s «A6000 в датацентре тома none» still describes EU-RO-1 today). The
pre-authorized fallback has no stock: if the create is refused, the contract's next step is a STOP,
not a second card. A refused create costs $0.

**3. Before the first launch, run the preflight ON THE POD.** The venv lives on the volume and its
`transformers` was installed by an earlier contract. A version that ignores `enable_thinking`
renders a CLOSED channel and every stage silently re-buys the BEFORE column at thinking prices —
the whole $8.00 measuring nothing, and no reply would look wrong. The tokenizer is already in
`/workspace/hf`, so this costs under a minute of pod time:

```bash
/workspace/venv/bin/python -c "import transformers, torch; \
  print(transformers.__version__, torch.__version__, torch.cuda.is_available())"   # Mac: 5.14.1 / 2.13.0
cd /workspace/repo && HF_HOME=/workspace/hf PYTHONPATH=src \
  /workspace/venv/bin/python scripts/preflight_serving_guards.py | grep -E "THINK|thought channel"
df -h /workspace && du -sh /workspace/hf     # 100 GB volume, ~62.58 GB of weights
ls -l /workspace/repo/results/*think*.json   # six packs arrived with the bundle
```

The line that must PASS is `enable_thinking:true leaves the thought channel OPEN on every reader
request`, with its control `READER and READER_THINK render differently for every text`.

**4. Proven at $0 on the Mac, so it is not discovered on the pod.** The two shared out-files were
driven through the pod's own stage order with a fake client: stage 1 → stage 7 buys **1 then 67**
and the file ends at 68 unique threads (the `carried` guard does NOT refuse the smoke's row — it
filters on `carried_from`, and the pod's own row has none); stages 2 → 3 → 5 buy **3, 197, 200**
and stage 5 never touches the v2 file.

**5. D3 will need a merge, and it is not free to discover after teardown.** The pass-2 thinking
column lands in TWO files (11 reference + 68 remainder) and both
`scripts/gate_pass2_signals_r2.py` and `scripts/score_pass2_signals_r2.py` hold their reply path as
a MODULE CONSTANT (`OUT_FILE`, `EVIDENCE`), pointing at `results/pass2_signals_r2_v1.jsonl` — which
is the BEFORE column and may not be written to. D3 merges the two into
`results/pass2_signals_r2_v1.READER_THINK.jsonl` and redirects the constant; the gate's LOGIC is
what the contract means by «via the shipped gate», and it does not move.
