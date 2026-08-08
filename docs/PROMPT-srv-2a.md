# PROMPT-srv-2a — GM4 serverless worker: config verified, volume plan, srv-2b runbook ($0)

**Contract:** SPEC amendment 3.14 (4); parity clause 3.11 (2); probe record
`docs/probe-serverless-20260808.md`. Operator rationale on record (08.08):
retail promos are image-first leaflets and one endpoint will eventually serve
three modes — captions (base, adapter OFF) · classification (adapter ON,
thinking OFF) · director-report narrative (thinking ON). THIS session builds
serving for the CLASSIFICATION mode only: the parity instrument must equal
4.5h2's exactly. The other two modes come after parity, by later contracts.

**$0 session. Do NOT:** create any cloud resource (no volume, no endpoint,
no pod), download models, touch Telegram, edit team-lead files
(docs/STATUS.md, docs/SPEC.md, docs/PROMPT-*), or `git add -A`.

## Steps

0. **Commit the pending tail, unmodified:** team-lead docs (SPEC, STATUS,
   probe record, both VOID/HOLD PROMPT files, this file) in one commit;
   vault tail (knowledge/*) in its own. You commit these, never edit them.

1. **Verify the 5b worker as a serverless config** (it was built for this:
   stock `runpod/pytorch` image, everything else on `/runpod-volume` —
   checkout, venv, weights; `scripts/start_5b_worker.sh` +
   `scripts/serve_handler.py`). Deliverable: a written env/config contract
   (MODEL_REVISION = config A pin `842da379…`; adapter =
   `results/train/45h2-arm-a` staged to the volume; batch 1, thinking OFF,
   greedy) and the MINIMAL fixes the verification demands — each named in
   Deviations. No new tasks, no caption or thinking modes.

2. **Volume plan** (a section of the runbook, not an action): 100 GB network
   volume; contents manifest = base weights at the pinned revision + adapter
   + venv + repo checkout, per the 5b staging pattern. The price is READ
   from the console at creation and recorded; never assumed. The datacenter
   is chosen AT srv-2b by the volume-attached GPU offering (the D7
   re-read), never hardcoded.

3. **Runbook `scripts/runbook_srv2b.md`:** create volume → stage weights →
   create endpoint (queue mode, max workers 1, scale-to-zero; GPU prefs:
   48 GB class first if offered with a volume, else 24 GB) → smoke: the
   3-row T2 batch that proved this stack on the pod → record the D7
   re-read (which GPUs serverless offers WITH the volume, today) → parity:
   758 rows, batch 1, against `results/parity_5b_a.json`, rule of
   3.11 (2) (every 4.5h2-passed gate stays passing, no head drops >0.005)
   → measured cost/row vs the pod's $0.60/1000 → spend anchor of its own;
   abort ladder: no GPU with volume / OOM / gate drop → STOP and report,
   no retry without a new briefing. Anything created for a FAILED run is
   deleted and deletion proven by LISTING; the volume persists as a
   run-rate line. Cap is set at the srv-2b briefing.

4. **Tests** (mocked, no downloads): env contract of the worker, request/
   response schema unchanged vs 5b, batch-1 guard intact. `make check`
   green.

**Report:** files changed, test output as evidence (commands + what they
returned), a Deviations section — silence is not compliance — then STOP.
