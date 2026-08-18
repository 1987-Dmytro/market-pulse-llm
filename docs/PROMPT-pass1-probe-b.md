# PROMPT — pass1-probe-b: the same instrument, one boot constant, and the transport proofs the last attempt taught

**The pass1-probe attempt was spent by its own runner (KeyError on the READER probe —
fixed red-first in `90f1cc6`, fresh-context confirmed) and by a boot ceiling charged
from ONE measurement where two now exist (192.1 s and 267–293 s). The operator
authorises a second attempt: the instrument does NOT move; ONE constant does. Cap
$0.20, one attempt, the return-to-sitting clause re-registered verbatim: a failed bar
P1 goes to the sitting (B — labelled data + LoRA, C — another base), never to a
prompt iteration.**

**Baseline:** `make check` 2 879 / 2 skipped (team lead's own run, 18.08).

## Step 0 — tail, and the pass1-probe close ONLY on a COMPLETE walk

1. Tail by live `git status`, by path; team-lead files verbatim in their own commit.
2. **Close the `pass1-probe` step only when the pod-scoped walk is COMPLETE** (the
   Dv488 discriminator): `runpodctl billing pods --pod-id rx89zok35e5ca6 …` must
   cover ~**427 000 ms** — the run record's own billed seconds — before
   `--close --note "pass1-probe settled"` may run. The team lead's read at
   acceptance showed a PARTIAL walk (pods $0.0617 of the meter's $0.0878): a close
   on it would freeze 70% of the truth forever. If still partial, carry the debt
   NAMED with the ms figure observed.

## D1 ($0) — the b-registration, and the transport proofs

`results/prereg_pass1_probe_b.json` + `results/pass1_probe_b_pack.json` via a
producer CALLING the pass1 producer (the v5b idiom): object-equality asserted for
everything P1 is scored on — the prompt sha (`5a4a3cb6…` — UNCHANGED, this is what
makes it legal), the parser, the 64-unit population and its per-item shas, bar P1
≥12/14 with the loss budget, the census rules, the one-attempt class, the
return-to-sitting clause — and the enumerated diff test asserting the ONLY moved
keys are the transport ones:

1. **Boot charged at 300 s** (the max of the stack's two measurements, not the min)
   and **`BOOT_KILL_S` 300 → 420**. Republish the solved-backwards table at the new
   constants (team lead's own recompute to be reproduced, not trusted: usable
   913.0 s · reading 409.7 s · affordability 503.3 s · budget +83.3 s · worst case
   ≈ $0.175 of the $0.20 cap). Gate-0 (180 s / ≤2 recreates / third = STOP) and
   segment accounting unchanged.
2. **The registration is DRIVEN through every transport command that reads it, at
   $0, before it is committed** (the Dv486 rule, now a deliverable): `--pre-create-
   check`, `--open`, `--deadlines`, `--gate` — each against the b-record on
   synthetic state, outputs pasted in the report. A registered field no command can
   read is a red gate here, not on a live pod.
3. **The freeze commit runs its own suite** (the Dv487 rule): the commit that
   carries the b-record gets `make check` (or the registered fast set) executed ON
   that commit, output pasted, before any pod. `producer.sha256` must pin bytes
   that are IN that commit.

## D2 — the run

Transport exactly as pass1-probe with two additions from the paid lessons:

- **The pod LOG is scp'd inside the poll loop alongside the jsonl** — before every
  gate, both files. Tonight's only traceback survived as a screen read; that may
  not happen twice.
- The real-constructor path stays covered: `tests/test_pass1_transport.py`'s
  shipped-probe test (already landed in `90f1cc6`) is in the suite the freeze
  commit runs.

Everything else per the pass1-probe contract: anchor before create, three listings
with the volume as positive control, gate-0 watch, bundle staging to a NEW
directory, `--repo` explicit, detached launch with pid liveness, per-row flush,
balanced-object stop, resume-skip with the tolerant reader, delete never stop,
guard read after (expect a LOWER BOUND; close only on a COMPLETE walk, else the
named debt).

## D3 — scoring

`scripts/score_pass1_probe.py` as built and driven (bar P1 through the reader's own
comparison; both denominators published; absent rows counted apart; the census
distribution, refusals, seconds/tokens per call, and the window pass-1 re-price at
the census cell's 1 032 payable comments).

## Verify (paste outputs, `python3.11` throughout)

```
make check                                       # counts before and after; PLUS on the freeze commit
runpodctl pod list -a                            # [] after; plus the other two listings
python3.11 scripts/runpod_guard.py --step pass1-probe-b --step-cap 0.20
shasum -a 256 results/prereg_pass1_probe_b.json results/pass1_probe_b_pack.json
<b-registration digest + byte-identical rebuild + enumerated-diff test line>
<the four transport commands driven against the b-record, at $0>
<the re-solved gate table at boot 300/420>
<verdict printed by the scorer — the 14-row table, census, re-price — or its named refusal>
```

## Report

`docs/reports/pass1-probe-b.md`, path-only in chat. Deviations from **Dv490** with
`[cause:]` tags; five-line Process signals. Read back first, one line each: what may
NOT move (the instrument, the bar, the clause) and the one constant that does; the
complete-walk rule for the old step's close; the four commands the record was driven
through; when the b-registration freezes (FIRST `pod create` of this attempt).

## DO NOT

- No change to the pass-1 prompt, parser, population, bar, census rules, or the
  return-to-sitting clause — any of those needs a sitting, not a contract.
- The 22 old ledgers stay UNTOUCHED — their contract (guard `--until`) is next in
  the queue, ruled by the operator.
- No serverless; one pod at a time; ≤2 recreates; delete, never stop; no cap raise;
  no edit to any frozen file once the first pod of this attempt exists.
- Team-lead files: commit verbatim, never edit. Never `git add -A`.
- Probe rows never enter production aggregates or window prices.
