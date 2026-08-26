# PROMPT — `think-zero-shot` (fresh session; D1 $0, D2 ONE paid pod, cap $8.00; Dv from 844)

You are the executor on `market-pulse-llm`. Ruling (ф), operator 26.08 (`docs/STATUS.md` §«Живые
рулинги»): **the same registered prompts, the same instances, Gemma-4-31B thinking ON** — a paired
A/B against the readings this repo already bought with `enable_thinking: false`. Nothing is tuned:
no prompt edit, no pack edit, no adapter. Read only STATUS (ф) and this file before step 0.

**The BEFORE columns (files, not prose):** dev-200 — `results/pass1_dev_base.jsonl` (v1: 87/200,
«our» 31/49) and `results/pass1_dev_v2.jsonl` (v2: 136/200, 38/49), pack `results/pass1_dev_pack.json`,
scorer `scorer.reader_comment_agreement`; pass-2 — `results/pass2_r2_pack.json` (79 threads),
replies `results/pass2_signals_r2_v1.jsonl`, bars in `results/pass2_signals_r2_verdict.json`
(4/5 · 3/4 · bar 3 red), gate `scripts/gate_pass2_signals_r2.py`; holdout-100 —
`results/pass1_holdout_100.json`, v2 column as cited by `docs/reports/pass1-window-r2.md` (64/100); if
that artifact has no per-row replies, report the thinking column alone and say so.

## Step 0 — commit team-lead files by path (`docs/STATUS.md`, this prompt); `make check-stamped`.

## D1 ($0) — the thinking instrument, driven on the Mac
1. A NEW template constant `THINK_CHAT_TEMPLATE = {..., "enable_thinking": True}` in `local_llm.py`,
   selected explicitly by `LocalClient` / `ReaderClient` (a `chat_template=` argument, default = the
   shipped `CHAT_TEMPLATE`, which is NOT edited); greedy, batch 1; `max_new_tokens` 4 000 for
   pass-1 and 8 000 for pass-2 (registered; a `length` finish is a counted parse failure, never a
   retry). srv-2d / CAPTION / POSITIONS paths are untouched — assert they still render a CLOSED thought.
2. `prompts.parse_reply` for thinking replies reads the JSON AFTER the thought channel closes
   (`<|channel>thought … <channel|>`), never the first brace; the reply record keeps `thought` and
   `thought_tokens`. Tests: braces inside the thought still parse the answer; an unclosed thought →
   a recorded parse failure, not an exception; a closed-empty thought (today's shape) parses as before.
3. Runners: `pass1_fewshot_pod_runner.py` and `pass2_r2_pod_runner.py` gain a `--serving
   READER_THINK` switch; output files carry the config name. Drive both end to end at $0 with a
   fake client (`main()`, the r2/r3 discipline), plus `preflight_serving_guards.py` on the new
   config (bos, thought channel OPEN on every request).
4. Registration `results/prereg_think_zero_shot.json`: ruling (ф) through `quoted()`, instances by
   sha, the BEFORE columns by file+sha, stage order and cap. **Readings, not bars:** the deliverable
   is the paired table; the operator decides on it. ONE attempt per stage; no re-runs.
5. `results/measurements.jsonl` (create if absent, one row per measurement with `source`): the
   smoke's s/call, thought length, peak VRAM go here.

## D2 — ONE pod (RTX PRO 4500 32 GB, EU-RO-1, `mp-srv2`; fallback 4090 $0.74), cap $8.00
Four rungs only: (0) price ≤$0.80/h at create; (1) liveness — 900 s from the LAST reply or
`nvidia-smi` activity (thinking is silent longer than JSON); (2) projection after the smoke and
after every stage at MEASURED s/call — over the cap by ≤20% → **ASK**: hold the pod ≤10 min for the
operator's typed word (quoted verbatim in the report), silence = KILL; over by more → KILL;
(3) platform hard stop from the cap at the observed price. Stages, in VALUE order — each completed
stage is a paired number: **smoke** = the pack's longest thread (pass-2) + 3 dev rows → s/call,
thought tokens, peak VRAM → **v2+think on dev-200** → **pass-2+think on the 16 reference
threads** (bars re-read by the shipped gate) → **v1+think on dev-200** → **v2+think on holdout-100**
→ the remaining 63 threads. Pull every reply file (hash both sides); teardown proven by listing
(`mp-srv2` present). Never two pods; never leave the pod unpolled past rung 1.

## D3 ($0) — report `docs/reports/think-zero-shot.md`, ≤80 lines
The paired table per stage: BEFORE column · thinking column · delta · n, on IDENTICAL rows; «our»
49 and the per-class table; the mention cell (`не_наш_рынок → категория`); pass-2 bars 4/5 · 3/4
· red vs thinking; flips both ways (fixed / broken, row ids); thought-length distribution; parse
failures and `length` cut-offs; s/call and $/stage; 14 gold as a census line (never a bar). Money by
the pod clock, guard delta beside. Deviations only for departures from this contract (enum v2,
from Dv844); one line of Process signals. STOP — the operator decides on the table.

**DO NOT:** edit any prompt text, pack, gold, sealed record or team-lead file; tune anything after
seeing a reply; exceed $8.00 or create a second billing resource; touch `mp-lora-c`; `git add -A`;
`make fmt` repo-wide; add gates or tests beyond D1's; invent a number a file does not carry.
