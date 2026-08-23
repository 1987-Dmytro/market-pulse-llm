# PROMPT — `lora-c-run` (fresh session, ONE paid pod session, cap $4.00, Dv from 786)

You are the executor on `market-pulse-llm`. This contract buys the lora-c measurement: four legs
(base v2 · base v3 · adapter A · adapter B) on the frozen packs, under registration
`results/prereg_lora_c.json` (DRAFT → FROZEN at your first `pod create`). Read: `docs/SPEC.md`
amendments 3.25–3.26 (marked blocks at the end), `docs/STATUS.md` пп. 1 (к)(л)(м),
`docs/reports/lora-c-apply.md` §«The ruling», `docs/reports/lora-c-close.md` §«Open». Money is
read from `scripts/runpod_guard.py`, never from prose. **Cap $4.00 all-in for this contract's
resources; the guard's cycle-2 remaining is the outer bound. ONE pod at a time, pods only, never
serverless, never two billing resources concurrently (the goal: no parallel spend).**

**Read-back before step 1 (refusal gate):** re-derive and list in one line each — optimizer steps
62 (arm A) / 82 (arm B) and `planned` 64/84 from `config/qlora.yaml`'s micro/accum/epochs; rows
506/666; E legs 198+198; pass-2 threads 11, filtered rows 46; ceiling 3 072 (3.26) and STOP_AT
2 800 true-count; charged rates 6.14 s/call (pass-1, v1/v2-measured — v3 is WIDER) and 97 s/thread
(pass-2); cap 4.00. A mismatch with any registered number is a FINDING — stop and report it.

## Step 0 — baselines; commit list

Baseline instrument as in prior contracts. Commits staged by path, never `-A`: (a) team-lead files
verbatim (`docs/PROMPT-lora-c-run.md`, `docs/STATUS.md` if moved); (b) step-0.5; (c) sibling
trainer + tests; (d) registration seal; (e) paid-session artifacts under `results/`; (f) report
`docs/reports/lora-c-run.md` + ADR; (g) vault tail. Team-lead files: commit, never edit.

## Step 0.5 — the close debts ($0)

1. `quoted()`-vs-STATUS negative control: mirror `test_the_spec_quotation_refuses_a_paraphrase`
   for the STATUS twin (`RULING_V`/`RULING_K`), on a COPY in `tmp_path`, both directions.
2. Bind the constant to the law: a test asserting `STOP_AT` in `scripts/tokenize_lora_c_rows.py`
   equals the number inside the registration's `amendment_3_26` quotation (parse the quote, no
   second literal), and that the tokens record's verdict fields agree with it.

## D1 — the sibling trainer ($0, the middle rung)

`scripts/train_qlora_v3.py`: IMPORT `train_qlora`, re-bind exactly two guards — `load_sft`
accepts task `pass1_comment_gm4_v3`; the registered-dataset sha list reads
`results/prereg_lora_c.json`. Everything else is CALLED, nothing copied. Drive at $0, evidence
both directions: (accept) the full arm A and arm B datasets load and **every row of 506 and 666
ENCODES under `encode_pass1` with the real tokenizer against 3 072 — print the census: refused
must be 0/0, max token count, headroom**; `class_weights` returns 4 classes on arm A and 5 on
arm B (assert both); (refuse) a v1-task row, an unregistered-sha dataset, and a row inflated
over 3 072 each raise by name. The original `train_qlora` guards stay untouched for line B.

## D2 — seal the registration, then the ONE paid session

Pre-pod arithmetic, written into the record before `pod create` (formulas + charged rates, no
invented s/step): fixed part = boot ≤500 s + load (worst measured 300 s) + base legs 2×198×6.14
+ pass-2 4×11×97 + training smoke 6 steps at the BOUND below + pass-1 evals 2×198×6.14.
**Training s/step at 3 072 has NO measured value — it is bought by the smoke, never projected
from lora-b's ≤1 222-token readings** (3.26 (3): the ratio model is retired for ceilings; the
same honesty applies to rates). Smoke bound for its kill-clock only: 121 s/step × 1.5. The
session's GO/KILL rungs are pre-registered CONDITIONS, not numbers:

- **Boot gate:** ssh ≤500 s from create, else kill+recreate (once; third pod = STOP).
- **Liveness:** deadline 600 s from the LAST log line or event, at every stage.
- **Projection rung, fired after the smoke and after EVERY leg:** cumulative spend (pod clock)
  + remainder projected at MEASURED rates ≤ cap remaining → GO; else KILL, pull artifacts,
  teardown, STOP to the team lead with the ledger. A KILL here is compliance, not failure.
- **Hard stop:** pod lifetime ≤ cap / worst rate, set at create.

Order on the pod: boot gate → load → **base v2 leg → base v3 leg** (these also measure real
s/call on v2 and v3 widths) → **training smoke: 6 optimizer steps of arm A's config at 3 072,
measure s/step** → projection rung → **arm A (62 steps) → eval A: pass-1 on E-198 + pass-2 pack
rebuilt from arm A's out-file, 11 threads** → projection rung → **arm B (82) → eval B likewise**
→ pull adapters + every out-file + ledgers → teardown. Deletion proven by LISTING with a
positive control; volume rent named separately. Recovery clause: after a proven deletion, one
re-create within the cap is authorized; artifacts already pulled are never re-bought.

## D3 — scoring and the report ($0)

Bars per arm, ONE attempt, scored by the shipped scorer from result files (never prose):
holdout agreement ≥ 64 (denominator note: reachable 98 of 100) AND bar 1 = 5/5 AND bar 3 = 0 —
all three or RED. Base v3 takes NO bar. Report-only rows (к): the `не_наш_рынок →
категория_личное` cell (18/52 before, denominator 50 after — print both), «our» on holdout
(6/8 before), dev-200 as FIT with its 115/80/5 split (the 8 «our» rows in E are a legitimate
eval reading — quote them as such and nothing else from dev), gold-14 census (SIXTH look, never
a bar), per-class tables, DROP/doubt tables per leg, the A-vs-B ablation with the reachability
note (arm A has zero real positives of `молочный_бренд`; synthetic is the only positive
supervision — a RED on A and a RED on B say different things).

Report closes with: **the numeric session-audit table** (per-leg call counts, refusals, spend
decomposition vs guard reading, artifact shas) — this REPLACES the subagent second-skeptic
(twice silent, Dv748/Dv779); the team lead reviews independently at acceptance. Deviations from
**Dv786** on enum v2 + the tally grep; five-line Process signals. STOP after the report.

**DO NOT:** exceed the cap or raise it (a raise is the operator's word BEFORE any endpoint);
create a second billing resource while one exists; leave the pod unpolled past the liveness
deadline; retry a bar or tune anything after seeing any eval output; touch the 14 golds as a
gate; merge adapters; edit team-lead files, sealed records, `prompts.py`, the sealed configs, or
any pack byte after the freeze; relabel anything; invent an s/step; write a price outside the
sealed money block.
