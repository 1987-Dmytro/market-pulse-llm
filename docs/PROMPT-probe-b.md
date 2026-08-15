# PROMPT — probe-b (the re-probe: fixed interface, faster card, scored bars; cap $0.35)

**Operator rulings 2026-08-15 (evening):** re-probe = probe-a's options A+B+C in ONE registration ·
cap **$0.35 all-in** (of the phase remainder $1.08 per the guard — read the guard, never a ledger
line or this sentence). **Baseline:** probe-a close (`make check` 2 521 passed / 2 skipped);
record HEAD. Probe-a's machinery is INHERITED (driver, READER config, scorer, gold, preflight) —
this contract changes the interface, the card and the population, nothing else.

## Step 0 — tail + one money-path fix

1. Commit the standing tail by path (verify live `git status`; this prompt arrives untracked).
2. **Dv392 closed before money moves again:** `runpod_guard.py` reads the underscore step-ledger and
   writes the hyphen one — normalise BOTH paths through `step_ledger_path`, one file per step, with
   a test that fails on a second spelling. Merge the two existing probe-a ledger files into the
   canonical path, content-preserving, and say so in the report.
3. Executor-owned hygiene: update `knowledge/hot.md`'s stale Dv177 footgun with Dv387's measured
   fact (RTX 2000 Ada · $0.240/h · EU-RO-1 · stock Low, dated 15.08). `make check` after hot.md.

## D1 ($0) — `reader_thread_gm4_v2`, a new instrument

New prompt registration, own sha; v1 stays registered and untouched (frozen history). Exactly two
wording changes, each closing a measured defect:

- **Dv393:** `entities` is a JSON **ARRAY**; each element carries `"name"` inside itself. One
  minimal shape line is now justified by measurement (v1's «one object per name» is exactly what
  the model rendered as an object). State the array shape explicitly.
- **Dv394:** a signal read in the POST carries `"from_post": true` and `evidence: []` (comment ids
  only, possibly empty); the «post id is null» rule moves OUT of any field the schema requires
  non-null. `parse_reply`'s reader branch follows — same single parser, updated in place.

## D2 ($0) — registration v2, superseding, committed BEFORE any endpoint

`results/prereg_reader_probe_v2.json`, supersedes v1 with the ruling cited. Changes, and ONLY these:

- **Population = a registered SUBSET, enumerated as a list with shas:** all reference threads —
  F1–F5, N2, N4–N6, the S-list threads, E2, E3 — PLUS the three probe-a warm-up threads (re-read
  under v2), PLUS four INJECTED threads from outside the billing gate: E1 (@matusi_ukr #22242),
  E4a (#3684), E4b (#3689), N3 (@sashafitnesslife #3939). Injected rows are marked
  `injected: true`: they exist to score bars 2/3, they NEVER enter production aggregates, and the
  production gate's design stays a sitting question. Expected size ~16–19 threads — enumerate, don't
  estimate.
- **Bars:** flagship cases 5/5 · entity cases **4/4** (all four now reachable) · noise 0 over
  {N2–N6, N3} with N1's exclusion carried unchanged · per-comment agreement ≥0.80 over **all 14
  gold rows** (578951 reachable via E1) · cap $0.35 all-in; the ≤30-min window budget stays a
  REPORTED projection (it prices production, not this probe).
- **Card (option B):** the endpoint requests the fastest available 24 GB class first (4090-class
  before L4), preference order registered; the ACTUAL card lands in provenance and the measured
  s/thread is reported per card. Warm-up = the same three registered threads under v2 → go/no-go
  against the cap before the rest.

## The paid pass — same discipline as probe-a, nothing relaxed

Preflight on real imports (57/57 + the v2 template check) BEFORE the endpoint; prereg → endpoint
order proven by git; everything frozen at endpoint creation; one attempt, STOP paths intact and an
un-anticipated situation stops with the attempt intact; every reply persisted raw
(`results/reader_probe_b_w1.jsonl`); scorer computes the five bars → `results/reader_probe_b_verdict.json`;
endpoint and template deleted with positive-controlled listings; spend from the guard.

## DO NOT

No SPEC edits; sealed anchors untouched (the prompts.py pin manoeuvre repeats — third tuple exists,
extend its witness list, never re-pin); no adapter, no batch >1, no thinking, no OpenRouter; never
`git add -A`; nothing beyond $0.35.

## Report · Read-back

`docs/reports/probe-b.md`, `docs(report): probe-b`, path only; Deviations Dv397+, cause tags;
Process signals ≤5; `/save`. Read-back (one line each): (1) the two wording changes and what each
closes; (2) which threads are injected and what they may never touch; (3) the order
prereg → preflight → endpoint, proven how; (4) where the spend number comes from.
