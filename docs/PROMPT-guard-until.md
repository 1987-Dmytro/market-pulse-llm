# PROMPT — guard-until: the walk gets an end, the backlog gets closed, and the preflight becomes an instrument

**Bar P1 failed and the SITTING owns the reader's next move — this contract does
not touch the reader. It fixes the money instrument: the guard never gives
`runpodctl billing` an end bound, so (a) an OPEN step ledger drifts upward on the
network volume's drip forever, and (b) a close over an old window settles on
everything billed SINCE it — measured at 2.6×–156× over seven ledgers, $86.49
against ~$13.4 recorded (docs/reports/pass1-probe.md §«(3) The 22-ledger batch»,
Dv483). The operator authorised this contract 17.08. It is $0 — no pod, no
serverless, nothing created; every cloud call is a read.**

**Pilots riding this contract (weekly retro 2026-08-18, docs/reviews/):**
- **H1:** the preflight instrument is BUILT here (D1); its output becomes a
  standing contract artifact from now on.
- **H6:** every numeric constant below carries its derivation, and step 1 is a
  REFUSAL gate: re-derive them all from the named artifacts; a mismatch is a
  finding reported BEFORE any close is written.
- **H4:** the report's Dv cause tags use the CLOSED enum v2 — see Report.

**Baseline:** `make check` **2 911 / 2 skipped** (team lead's own run, 18.08).

## Step 0 — the tail (checked against live `git status`: exactly these paths)

1. Vault tail, its own commit: `knowledge/daily_logs/2026-08-18.md`,
   `knowledge/hot.md`, `knowledge/index.md`.
2. Team-lead files, verbatim, their own commit: `docs/STATUS.md` (accepted
   pass1-probe-b; compacted 409→~220 by the team lead, incl. the B-sitting
   ruling of 18.08 evening),
   `docs/reviews/2026-08-18-weekly-retro.md` (new),
   `docs/PROMPT-guard-until.md` (this contract). Never edited, never
   `git add -A`.

## Step 0.5 — the ADR debt of the accepted step

ADR in `knowledge/decisions/` + INDEX: pass1-probe-b — pass 1 MEASURED, bar P1
9/14 against 12, STOP by the pre-registered clause; the sitting (B: labelled
subject_type + LoRA / C: another base) owns the next move; transport settled
(gate-0 GO ×3, boot spread 1.53× registered, $0.135050 of $0.20). Cite the
report; do not re-argue it.

## Step 1 — the H6 refusal gate: re-derive every constant

- **~427 000 ms** — pass1-probe's expected COMPLETE walk: re-derive from
  `results/pass1_probe_run.json` `segments` (create→delete spans, summed). The
  report's «~427 000» is a claim to reproduce, not to trust.
- **~657 000 ms** — pass1-probe-b's: same derivation from
  `results/pass1_probe_b_run.json` (one segment, 657.0 s).
- **The close tolerance** — a bounded walk must agree with the ledger's own
  recorded reading; the demonstrated spread is 6–7% (the control table in
  docs/reports/pass1-probe.md §(3)). Re-derive the max divergence from that
  table and REGISTER the tolerance you will close under, with this derivation,
  in the close path and its test — a close outside it is a refusal, not a
  rounding.

A mismatch on any of the three: STOP, report the figure, nothing is closed.

## D1 ($0) — the preflight instrument (pilot H1)

`scripts/preflight.py` + Makefile target `preflight` (the namespace is free:
current targets are only `check` and `fmt`). Input: one or more names /
constants / paths (CLI args or a file). Output, per query, designed to be
PASTED into a contract:

- grep hits with COUNTS, split by root (`src/ tests/ scripts/ docs/ knowledge/
  config/`) — the consumer-count rule;
- prose quotes: doc/knowledge lines citing the queried constant's VALUE (a note
  quoting the old number is a consumer);
- the pin registry: which sealed records pin which files (seed from the pins
  named in docs/STATUS.md «Пины — потребители» and the sha fields of
  `results/prereg_*.json`), and whether a queried path is pinned;
- digests: sha256 of every pinned file it names.

Prove it on THIS contract's own names (`--until`, `closing_record`,
`billing_by_kind`, `spend_pass1_probe*.json`, `runpod_guard.py`) and paste that
output in the report — the guard is edited only AFTER its preflight output is
in hand (the dogfood is the point). Design latitude is yours; the four output
blocks above are the acceptance bar.

## D2 ($0) — the guard learns an end bound (red-first)

- `--until <ISO-8601>`: the walk's end. Plumb it through `billing_by_kind` to
  `runpodctl billing` as an end bound (with the bucket sizing the report's
  bounded probe used); it bounds BOTH the step reading and the
  `--close --since` walk.
- The step reading keeps today's per-kind attribution and gains the end bound —
  that is what stops the volume's drip from accruing into an open step forever
  (the Dv491/Dv499 family).
- The Dv488 three-state walk stays law: `closing_record()` refuses anything but
  a COMPLETE read; completeness = the bounded walk's ms converge with the run
  record's own billed span (step-1 constants). Partial → refusal printing both
  figures.
- Red-first tests: the unbounded-close inflation shape (the $86.49 class), the
  partial-walk refusal, the bounded-walk convergence, the tolerance gate.

## D3 ($0; irreversible writes LAST, only after the suite is green) — the closes

Order: the two fresh ledgers, then the backlog of 22.

1. `pass1-probe`: close only if its bounded walk now covers the full span
   (~427 000 ms, step-1 re-derived); else the debt stays NAMED with the
   observed ms.
2. `pass1-probe-b`: same at ~657 000 ms (at acceptance the pods line already
   read $0.1355 ≈ the record's $0.135050 — likely ripe).
3. The 22 ledgers of docs/reports/pass1-probe.md §(3): each closed with
   `--close --since <its window start> --until <its window end>` (window ends
   from each ledger's own last session), settled figure within the registered
   tolerance of its own recorded reading — else NOT closed, named with both
   figures. Closing entries are APPEND-ONLY; no existing entry is rewritten.
   Hash-control the ledger files you do NOT close (the pass1-probe report's
   29-file control is the idiom).

After all closes: paste the guard's cycle-2 line reading.

## Verify (paste outputs, `python3.11` throughout)

```
make check                    # before and after; baseline 2911/2 + this contract's tests
make preflight ...            # the instrument on this contract's own names
PYTHONPATH=src python3.11 -m pytest tests/test_runpod_guard.py -q
<the two probe closes: bounded walks + settled figures, or named refusals>
<the 22-ledger batch: closed count, refused count with figures>
python3.11 scripts/runpod_guard.py     # the cycle-2 line reading after the closes
runpodctl pod list -a                  # [] unchanged; + serverless list + network-volume list (positive control)
<shasum control of untouched spend_*.json, before/after>
```

## Report

`docs/reports/guard-until.md`, path-only in chat. Deviations from **Dv500**.
**Cause tags: the CLOSED enum v2 only** — `[cause: contract-gap | spec-gap |
verify-gap | env | tooling | model | process]`; the lesson's name goes in an
optional trailing `[[wiki-name]]`, never in the tag; an off-enum or empty tag
comes back for re-tagging at acceptance. Five-line Process signals. Read back
first, one line each: the three step-1 constants with their derivations; what
`--until` bounds; the completeness rule for a close; the append-only law; what
this contract may NOT touch.

## DO NOT

- Nothing is created in the cloud — no pod, no serverless, no volume change;
  billing/list reads only.
- Closing entries are append-only; a ledger that fails its tolerance stays OPEN
  and NAMED — never forced, never approximated.
- Frozen records (`results/prereg_*`, packs, verdicts, gold) untouched; the
  pass-1 instrument/prompt/bars belong to the SITTING, not to this contract.
- Team-lead files (docs/STATUS.md, docs/SPEC.md, docs/PROMPT-*): commit
  verbatim, never edit. Never `git add -A`.
- If the bounded walk exposes a NEW defect class in the guard, STOP and
  report — do not widen scope to fix it here.
