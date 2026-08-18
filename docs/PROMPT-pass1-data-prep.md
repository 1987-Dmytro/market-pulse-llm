# PROMPT — pass1-data-prep: the labelling pack for line B, and nothing that spends

**The sitting of 18.08 ruled line B: labelled `subject_type` data + LoRA, and the
TEAM LEAD does the labelling.** This contract builds the pack the team lead will
label from and the harness that will refuse a bad labels file. It trains nothing,
registers no money, and makes no cloud call of any kind — the store is local. $0.

**The honesty frame this contract implements (the sitting's word, to be recorded
in the ADR of step 0.5):**
1. The judge does NOT move: the bar stays sealed gold r2 ≥12/14, and the labeller
   never touches exam material — every thread carrying any of the 64 registered
   probe units is EXCLUDED from the pack, with proof.
2. Team-lead labels are TRAINING data: provenance-tagged (labelled_by, date,
   codebook, seed, pack sha) and to be ablated at training time — that ablation is
   the LoRA registration's law, named here so it is not lost.
3. The codebook is not an opinion: the v5 attribution law by the same bytes, the
   F2a carve-out, and the gold-r2 adjudication rulings.

**Baseline:** `make check` **2 927 / 2 skipped** (team lead's own run, 18.08).

## Step 0 — the tail (checked against live `git status`: exactly these paths)

1. Vault tail, its own commit: `knowledge/daily_logs/2026-08-18.md`,
   `knowledge/index.md`.
2. Team-lead files, verbatim, their own commit: `docs/STATUS.md` (guard-until
   accepted; the B-sitting and the three-close ruling registered) and
   `docs/PROMPT-pass1-data-prep.md` (this contract). Never edited, never
   `git add -A`.

## Step 0.5 — TWO ADR debts of the accepted steps

1. **The B-sitting** (18.08 evening): line B chosen, the team lead labels, the
   honesty frame above — cite `docs/STATUS.md`'s registration and
   `docs/reports/pass1-probe-b.md` for the numbers that forced the sitting.
2. **guard-until**: the tolerance finding (a control table that measured its own
   window defect, not billing spread — nothing closable from it) and the ADDENDUM
   closes (operator's 7% band, three ledgers, pre-window caveats INSIDE the
   entries). Cite `docs/reports/guard-until.md`; do not re-argue it.

## Step 1 — the H6 refusal gate: re-derive every constant

- **129 threads / 1 032 payable comments** — the reader cell
  (`narrow|varto_off|plus_spam+scam`): re-derive from
  `results/gate_census_w1_reader.json` and its producer
  `scripts/gate_census_w1_reader.py`. Claims to reproduce, not to trust.
- **7 excluded threads** — every thread carrying any of the 64 registered probe
  units, derived from `results/pass1_probe_b_pack.json` items: expect
  `@VARUS_channel:10348`, `@VARUS_channel:10613`, `@mandziak:3676`,
  `@mandziak:3703`, `@matusi_ukr:22242`, `@matusi_ukr:22272`,
  `@matusi_ukr:22303` — re-derive the list, do not copy it.
- **The target volume** — `min(500, payable comments remaining after the
  exclusion)`; 500 is precedent-sized (the intents pass, 508 rows). Print the
  arithmetic: payable in cell − payable in excluded threads = remainder → drawn.

A mismatch on any of the three: STOP, report the figure, no pack is built.

## D1 ($0) — the labelling pack, drawn under a recorded seed

`scripts/build_pass1_label_pack.py`, deterministic from a registered seed:

- **Population:** every payable comment of the reader cell MINUS the excluded
  threads. Contamination proof in the pack record AND as a test: zero drawn
  units share a thread with any of the 64 probe units; the 14 gold msg_ids
  appear nowhere.
- **Draw:** stratified by thread — proportional with a per-thread cap so no
  giant thread dominates (register the exact formula and cap; print the
  per-thread distribution table). Seed recorded in the pack record.
- **The labeller's rendering** — the team lead reads it over the file MCP:
  `docs/label-pack-pass1-r1.md` — ordered by thread; per thread the FULL text
  (post, then every comment with its msg_id, payable or not, in order), target
  comments clearly marked; a codebook header up top: the v5 attribution law
  section quoted by the same bytes with its source named, the F2a carve-out,
  the r2 adjudication rulings, the four `subject_type` values + the null
  semantics («no subject» is an answer). Labels are `subject_type` ONLY —
  stance reads 3/3 and is not this pack's business.
- **The machine pack** beside it: `results/pass1_label_pack_r1.json` — units
  (thread, msg_id), seed, formula, exclusion proof, sha of the rendering.
- **The blind subset, emitted but unlabelled:** 40 of the drawn targets under
  the same seed → `docs/label-pack-pass1-r1-blind40.md` (same rendering, its
  own file). It exists so the operator CAN blind-label it later; nothing in
  this contract or the next depends on whether they do.

## D2 ($0) — the validation harness (red-first)

`scripts/validate_pass1_labels.py` — takes a labels file (JSONL: thread, msg_id,
subject_type) and REFUSES unless: every drawn unit is answered exactly once;
every value ∈ {сеть_ритейлер, молочный_бренд, категория_личное, не_наш_рынок,
null}; every (thread, msg_id) matches the pack; no unit from an excluded thread.
On pass it prints the per-class distribution and writes nothing. Red-first
tests: a missing unit, a duplicate, an off-taxonomy value, a contaminated row —
each refused; plus the green path on a synthetic complete file.

**File ownership, extended by this contract (one line for the record):** the
labels file `docs/labels-pass1-r1.jsonl` will be WRITTEN BY THE TEAM LEAD — it
is a team-lead file like docs/STATUS.md: the executor validates and commits it
verbatim, never edits it. Freezing a provenance-tagged copy into `results/` is
the NEXT contract's step, after the labels exist and validate.

## Verify (paste outputs, `python3.11` throughout)

```
make check                    # before and after; baseline 2927/2 + this contract's tests
PYTHONPATH=src python3.11 scripts/build_pass1_label_pack.py           # and re-run:
<the pack and both renderings rebuild BYTE-IDENTICAL from the recorded seed>
<the step-1 re-derivations: cell counts, the 7 threads, the volume arithmetic>
<the exclusion proof and the per-thread distribution table>
PYTHONPATH=src python3.11 -m pytest tests/test_pass1_label_pack.py tests/test_validate_pass1_labels.py -q
git status --porcelain        # clean at the end
```

No `runpodctl` anything — this contract has no cloud surface at all.

## Report

`docs/reports/pass1-data-prep.md`, path-only in chat. Deviations from **Dv518**,
cause tags from the CLOSED enum v2 only (`contract-gap | spec-gap | verify-gap |
env | tooling | model | process`), lesson names as trailing `[[wiki-name]]`.
Five-line Process signals. Read back first, one line each: the three step-1
constants with derivations; the exclusion rule and its proof; who writes the
labels file and who may not; what the blind subset is and what does NOT depend
on it.

## DO NOT

- No cloud calls, no money, no registration — nothing here spends or freezes.
- The 64 probe units' threads and the 14 gold rows never enter the pack.
- No edits to the reader or pass-1 instruments, prompts, parsers, bars, gold, or
  any frozen record — line B's TRAINING design (renders, ablation, cost) belongs
  to the LoRA registration, not here.
- `docs/labels-pass1-r1.jsonl` is a team-lead file from the moment it exists:
  commit verbatim, never edit, never generate labels into it.
- Team-lead files: commit verbatim, never edit. Never `git add -A`.
