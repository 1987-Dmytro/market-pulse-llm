# PROMPT — reader-v3-prep: the A+B instrument, gold r2, the reader census cell, and a frozen registration

**$0 GPU. No endpoint, no pod, no template may be created — the paid re-read is the NEXT
contract (`reader-v3-run`). Cloud reads (balance, billing) are unlimited.**

**Goal.** Everything the operator ruled at the 2026-08-16 sitting lands as a frozen v3
registration, so the run contract has nothing left to decide. The rulings below are LAW —
zero invention on them; code structure and test names are yours. Authority for all four
rulings: `knowledge/decisions/reader-sitting-16-08.md`.

**Baseline:** `make check` 2 584 / 2 skipped at `c3b6b70` (or current HEAD) plus the
standing tail.

## Step 0 — the tail, two commits by path (never `git add -A`)

Live `git status` first. Expected: (1) `knowledge/**` (daily log 2026-08-16, index.md,
plus anything today's sessions left); (2) team-lead files `docs/STATUS.md` and this
contract `docs/PROMPT-reader-v3-prep.md`, committed verbatim. Anything outside those two
classes → STOP and report.

## Step 0.5 — amendment 3.24 and the anchor, taken deliberately

**3.24 (one clause):** the $40.00 floor of 3.23 (2) is REPEALED — it was derived from a
false assumption (the operator's $20 landed 2026-08-15 and is the current balance). The
cycle-2 anchor is the first guard balance reading taken AFTER this amendment lands,
recorded verbatim with its timestamp by THIS contract, supervised — which closes
`docs/reports/cycle2-money.md` finding (2). 3.23's other clauses stand: the line is
$20.00, home `results/spend_cycle2.json` + `CYCLE2_CAP_USD`, the volume named separately.

Landing = the house manoeuvre, SIX parts (this morning's `b3db748` is the fresh
precedent): marked block in `docs/SPEC.md` + `write_prereg_5c2.BLOCKS_TODAY` (+docstring)
+ the enumeration in `tests/test_sku_prereg.py` + the literal tail + **the intruder moves
`amendment-3.24` → `amendment-3.25`** (`tests/test_prereg_5c2.py:318`) + negative
controls shown, six sealed pins re-derived unmoved. `CYCLE2_ANCHOR_MIN_USD` in the guard
follows the law (repealed → remove or set to 0.0 with its test moved, whichever the
cleaner diff — but the constant must not survive asserting $40).

Then run the guard once: the anchor writes (~$22.5 verbatim), `results/spend_cycle2.json`
exists, the inter-ledger gap is over. Paste the guard's output in the report.

## D1 ($0) — the v3 parser: container tolerance by ruling, domains strict

Scope: the READER task family only (`prompts.READER`, `src/market_pulse/prompts.py:862`);
POSITIONS and caption parsing untouched. `parse_reply` (`prompts.py:1429`) learns, for
reader tasks, EXACTLY the three container repairs measured in
`scripts/probe_b_coercion.py::repairs()` (line 67):
1. an answer split into two top-level JSON objects → merged, **and a key present in both
   with different values = REFUSE** («two disagreeing objects», operator's word — never
   last-wins; this is the one place the coercion script's `dict.update` is NOT the law);
2. `{}` where the schema asks for a list → the empty list;
3. a map keyed by msg_id where a list belongs → the list it describes.

NOT repaired (domain, not container): `aspect: null`; a `from_post` signal with no
`evidence` key; bare un-braced fragments (probe-b's seventh shape). Each stays a refusal
with its test. Every repair is logged on the parsed object (`repairs: [...]`) so a
verdict can always say whether it was read straight or coerced.

## D2 ($0) — the v3 prompt, derived, not retyped

`reader_thread_gm4_v3` derived from v2 by `_swap` calls (`prompts.py:359` — the probe-b
discipline: every change is a visible call), registered beside v1/v2 in the task map
(:782) and in `READER`. Changes, each traceable to a measured miss:
- the frame: «answer with ONE JSON object», «`[]` when there is nothing» (kills shapes
  1–3 at the source; the parser tolerance stays as belt-and-braces);
- the reading gap (probe-b §5.5 / finding 5): every payable comment gets its
  `per_comment` row; a thread may carry SEVERAL signals — do not stop at the first
  (F1 carries three); the channel's own reply is readable evidence (F1b — the network
  answering «морозиво без цукру» with SKUs is a спрос signal); praise of taste is a
  signal, not filler (F1c).
Draft wording is yours; the FULL final text goes in the report and freezes in the
registration. v1 and v2 stay registered and servable.

**Pin fan-out, eyes open:** ~10 result records name `prompts.py` (both reader preregs,
`reader_gold_w1.json`, `dashboard_data_w1.json` LIVE, `validate_5c2_pack.json`, uni/
caption records…). Enumerate them at your step, grep + a graph query; sealed ones take
the MOVED manoeuvre (third time — probe-b did it twice), the live export regenerates in
the same commit, `ruff format` BEFORE any sha is computed (Dv410).

## D3 ($0) — gold r2, beside v1, reference untouched

`results/reader_gold_w1_r2.json`, a NEW file derived from `docs/REFERENCE-signals-w1.md`
(not one byte of it moves) + the vocabulary adjudication (ruling (4) of the sitting ADR):
every gold cell reading «категория» is re-labelled «категория_личное». Nothing else
changes — same rows, same msg-ids, same reachability block. `reader_gold_w1.json` (v1)
stays untouched, so probe-a/b records keep their pins. The r2 file records its
derivation (source sha + ruling reference) and a test rebuilds it byte-for-byte.

## D4 ($0) — the reader census cell, measured

A NEW file `results/gate_census_w1_reader.json` (the shipped `gate_census_w1.json` is
never rewritten): the cell **narrow · varto_rule OFF · plus_spam+scam ON**, measured by
the census producer over window-1 — threads, payable comments, and the window price at
probe-b's measured 4090 rates. Expectation from the existing decomposition is 129
threads; the point is to MEASURE it (sitting ruling (3): never derived). This cell is
the reader's production population for window pricing; the probe population below stays
probe-b's for pairing.

## D5 ($0) — the registration, frozen before any money

`results/prereg_reader_probe_v3.json` via `scripts/write_reader_prereg.py` (extend as
needed): instrument = prompt v3 sha + parser v3 behaviour (the three repairs and the
refuse list, stated); population = **probe-b's same 23 threads — the digest must equal
`ccef35fa4b9c771f…`** (paired comparability), with each thread's in/out status under the
NEW reader cell recorded (E1/E4's threads are expected to enter the gated population
with varto off; N3 likely stays injectable — ENUMERATE, don't estimate, Dv399);
serving unchanged (READER config, base-no-adapter, batch 1, `ADA_24` requested, card
named in every projection); cap **$0.35 all-in** against the cycle-2 line; go/no-go =
probe-b's corrected arithmetic (remainder + measured setup, pessimistic binds). Bars:
same five thresholds — flagships 5/5 · entities 4/4 · noise 0 · per-comment ≥0.80 vs
gold r2 · cost ≤ cap — with one fix written INTO bar 3: **«zero signals» is counted
over threads WITH a parsed verdict; a refused reply is never a zero** (probe-b finding
2). The registration freezes when written; the run contract may not edit it.

## Verify (evidence, not assertions)

```
make check                                   # green, count stated
ruff format --check .
python3 scripts/runpod_guard.py              # cycle-2 ANCHORED at ~$22.5, no gap refusal
PYTHONPATH=src python3 -c "<render v1,v2,v3 shas; parse_reply drives the three repairs + refuse-on-conflict + the three standing refusals>"
<gold r2 rebuild byte-for-byte; census cell printed; registration digest printed>
<negative controls of the 3.24 landing>
```

Probe-b's three REAL paid replies re-driven through the v3 parser: expected 3/3 parse
(they did under coercion) — paste the outcome.

## Report

`docs/reports/reader-v3-prep.md`, path-only in chat. Deviations with `[cause:]` tags
(numbering continues from Dv423), five-line Process signals. Read back before code, one
line each: the six landing parts of 3.24; the three repairs + the refuse-on-conflict
rule; bar 3's fixed predicate; the population digest that must not move.

## DO NOT

- No billable resource of any kind — the paid re-read is `reader-v3-run`, a separate
  contract after team-lead acceptance of this one.
- `docs/REFERENCE-signals-w1.md`, `docs/PLAN-comment-signals.md`, `config/registry.yaml`,
  `config/lexicon.yaml`, gold v1, both v1/v2 preregs, shipped census — untouched.
- POSITIONS/caption parse paths, r1 brand attribution, classification gate — untouched.
- Team-lead files (`docs/STATUS.md`, `docs/SPEC.md` outside the 3.24 block,
  `docs/PROMPT-*.md`, `docs/PRODUCT.md`) — commit, never edit.
- No re-pinning of sealed records — MOVED manoeuvres only; never `git add -A`.
