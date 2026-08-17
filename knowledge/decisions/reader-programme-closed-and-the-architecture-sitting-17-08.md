---
type: decision
date: 2026-08-17
status: accepted
tags: [decision, phase6, comment-signals, reader, stop-rule, architecture, decomposition, pass1]
---

# The reader's prompt-engineering programme is CLOSED by its own stop-rule, and the sitting of 17.08 rules architecture D

**The stop-rule fired on a COMPLETED run.** `reader-v5b` was not killed, not capped and not aborted:
it read every registered unit and every bar was computed. That is the precondition the rule was
written to need, and it is why the closure is a measurement and not a mood.

## The run that closed it

Verdict `results/reader_v5b_verdict.json` (`8c975558b8da31cf…`), evidence
`results/reader_v5b_w1.jsonl` (`9540a84bc87109ce…`), registration
`results/prereg_reader_probe_v5b.json` (`8122fce0eb25c223…`). Every number below is read out of the
verdict, not out of the session's memory.

| bar | v5b | v4 | threshold |
|---|---|---|---|
| `1_flagships` | **FAIL — 2 of 5** (F4, F5) | FAIL — 2 of 5 | 5 of 5 |
| `2_entity_cases` | PASS — 4 of 4 | PASS — 4 of 4 | 4 of 4 |
| `3_noise` | PASS — 0 signals over 5 threads | PASS — 0 | 0 signals |
| `4_per_comment_agreement` | **FAIL — 0.4286** (6 agreed / 4 disagreed / 4 absent of 14) | FAIL — 0.500 | ≥ 0.80 |
| `5_time_and_cost` | OPEN — the walk had not posted | PASS — $0.236118 | $0.50 cap |

Bar 4 over the rows the model actually ANSWERED is **6 of 10 = 0.600**, against v4's paired reading
of 0.636. The instrument moved the bar in neither denominator.

**The transport and the mechanics were all green** — which is what makes the negative honest. Gate 0
went **GO with 143.5 s of its 180 s dead-man unused** (`results/reader_v5b_run.json`, the `gate0`
snapshot), where v5's pod never answered `ssh info` inside 727.9 billed seconds; **26 of 26** units
read; 21 `full_pass` gates, every one GO; the pod deleted, one segment, no recreate;
**$0.311211 of the $0.50 cap** over 1 514.0 billed seconds. The msg_id echo duty came back
**117 requested / 117 covered / 0 absent**. Leg B's chunking mechanism passed all four mechanical
bars (m1–m4) on `@klopotenkofood:6040`, 43 payable ids covered exactly once. The 4 000-token ceiling
never fired (`finish_reason_length` 0). The «two disagreeing objects» class is extinct: 26 of 26
replies balanced, `never_balanced` empty.

**And the reading did not move.** Row by row against v4's own fourteen: exactly ONE row moved from
disagreement to agreement on attribution alone (48283, `категория` vs `null` → agreed). 580124 lost
its `stance` disagreement and kept its `subject_type` one. Three rows arrived out of ABSENCE through
the echo duty and only one of them agreed (47899 agreed; 47902 and 578951 disagreed on
`subject_type`). Four rows went the other way, from scored to ABSENT, when `@VARUS_channel:10613`
was refused — and two of those four had AGREED under v4. The F2a carve-out of ruling (c) did not
fire at all; msg_id 580129 is still read as a brand where the gold says the category. The bar moved
0.500 → 0.4286 and not one of these movements is the reader learning to attribute.

Four replies of 23 were refused — the SAME count v4 had —
and three of those four are the new transport stop taking a balanced object that was not the answer
(`missing field: entities` ×2, `missing field: evidence` ×1); the fourth cut at a brace and left
`malformed JSON`, which is where four of bar 4's fourteen gold rows went ABSENT.

**Completed run + bars 1 and 4 both unmet = the pre-registered programme stop-rule.** Quoted from
the v5b registration's own `registration.programme_stop_rule` field, written before any number
existed: the prompt-engineering line CLOSES and the next step is an architecture sitting, never a v6
of the same kind.

## The episode that did not cost money: a ruling withdrawn before the pod

The v5b contract carried three transport differences, one of them a RULING that leg A be ordered by
**descending payable** — aimed at the 9% knife-edge Dv471 had found on the cap gate's PAYABLE leg.

- **Ruled** 2026-08-17, inside `docs/PROMPT-reader-v5b.md`, together with the cap raise $0.45 → $0.50.
- **Priced** the same evening at $0, by running the live gate's own function over four candidate
  orders on the built pack (commit `c88da32`, 17:49 CEST): the ruled order makes the gate **STOP at
  unit 1**, by 23.2 s/unit, because the by-UNIT leg extrapolates 25 unread units off whatever the
  first reply costs and descending payable puts the second-slowest thread there. The cap raise ALONE
  had already turned the knife-edge into 23% of margin on the unchanged order. The STOP survives the
  boot-free corner: `usable ÷ units` bounds unit 1 at 91.2 s with no provisioning forecast in it.
- **Withdrawn** by the operator 2026-08-17 18:11 CEST (commit `f7e2263`), pack rebuilt in v5's
  enumeration order at 18:12 (`1942a74`), the step anchored at 18:21 (`a25ab76`) — every one of them
  BEFORE the first `pod create` of the attempt. No money was spent under the withdrawn order and the
  one attempt was never at risk.
- **Then measured.** The run read that same thread (`@matusi_ukr:22272`) as unit 17 in **103.8 s**
  against the table's forecast of 105.3 s — 1.4% high. Under the ruled order the pod really would
  have been deleted after one thread.

The withdrawn ruling's gate table stays inside the registration record rather than being deleted:
what was refused is part of what was registered.

## The sitting of 17.08 — three rulings

**(1) The frame is architecture D — hybrid decomposition.** The v5 reader keeps what it demonstrably
delivers (entity cases 4 of 4 twice over, zero noise signals, quotes) and stops being asked for
per-comment attribution. That attribution moves into a separate **pass 1**: short classification
calls, one comment at a time, fed the thread's already-resolved entity context. Signal assembly
becomes pass 2.

**(2) The first step is a micro-measurement of pass 1, at ~$0.10–0.15.** Its own pre-registration,
its own population — bar 4's 14 gold rows plus the neighbouring payable comments of the same threads
as a report-only census — a gating bar of **≥12 of 14**, and ONE attempt. The entity context is
taken from verdicts ALREADY BOUGHT (v5b's, and v4's for `@VARUS_channel:10613`, which v5b refused);
no reading is re-purchased to feed context. **A failed bar returns to this sitting** — options B
(labelled data + LoRA) and C (a different base) — and never to a prompt iteration.

**(3) Labelling `subject_type` is PLANNED but not yet bought.** 2–4 hours of operator time, on the
precedent of the 508-row intents pass. It is authorised only AFTER the micro-measurement confirms
the frame — labelling for an architecture that has not been shown to work is the expensive version
of the mistake this programme just closed.

## The legal reading, and what binds the team lead

The stop-rule closes **the one-shot prompt reader**: one call, one thread, every question answered at
once, cured by editing the prompt. A per-comment classification pass is the rule's own named
successor — the sentence says the next step is an architecture sitting and names «two passes» among
its options, so pass 1 IS that step and is not «a v6 of the same kind».

**This record binds the TEAM LEAD as well as the executor: no new one-shot reader registration may
be written.** Not under a new letter, not with a new prompt, not at a smaller cap. The reader's
per-comment attribution question is now answerable only through the decomposition, through labelled
data, or through a different base — and which of the three is a sitting's decision, not a contract's.

## Debts this record carries forward, named

- **The `reader-v5b` step is not closed.** The billing walk over its window had not posted at
  acceptance; bar 5 stays OPEN and the step's floor is the $0.3223 balance delta against a meter of
  $0.311211. Closing it is bookkeeping and it moves ONLY `5_time_and_cost`.
- **22 old step ledgers stand open**, named on 15.08 and still open. See
  `docs/reports/pass1-probe.md` for why the guard's `--close` cannot settle them as written.

Related: [[reader-v4-closed-and-sitting-17-08]] (the stop-rule's own registration and the sitting
that wrote it), [[reader-v3-serverless-close-and-the-pod-ruling]] (the pod ruling that made all of
this affordable), [[reader-sitting-16-08]], [[reader-probe-card-and-interface]].
