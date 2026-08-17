# PROMPT — reader-v5b: the same instrument re-registered, with the transport that survives a dead endpoint

**One contract: the $0 fixes and the v5b registration first, then ONE paid run on a pod.
Cap $0.50 all-in (operator ruling 17.08), enforced by `runpod_guard --step reader-v5b
--step-cap 0.50`. ONE attempt for this registration: a STOP, or a completed run with a
failed bar, closes it. The PROGRAMME STOP-RULE is re-registered verbatim and still
armed: if the run COMPLETES and bars 1 and 4 are not BOTH taken, prompt-engineering
closes and the next step is an architecture sitting.**

**The instrument does NOT move.** Prompt v5 (`c529d279…`), parser v5, gold r2, the
ceiling 4000, the echo duty, the collapse, N1's exclusion — all copied OBJECT-EQUAL
out of the frozen `results/prereg_reader_probe_v5.json` (`8294673c…`). v5b registers
three TRANSPORT differences (operator rulings 17.08): the cap, the ssh gate-0, the
pack order. Nothing the reader is scored on changes.

**Baseline:** `make check` 2 782 / 2 skipped (team lead's own run, 17.08). Tail on
the tree: two `knowledge/**` files.

## Step 0 — tail and the v5 close

1. Tail by live `git status`, by path; team-lead files verbatim if dirty.
2. **Close the `reader-v5` step** — the walk has posted (team lead's read: billing
   $0.1501, pods only): `python3.11 scripts/runpod_guard.py --step reader-v5
   --step-cap 0.45 --close --note "reader-v5 settled"`. Commit both ledgers.

## Step 0.5 — the two fresh-context findings, red before green

1. **`already_answered()` gets the tolerant reader.** It parses the out-file with a
   bare `json.loads`, so a replacement pod resuming over a TORN last line — exactly
   the mid-write death the recovery clause covers — dies with a traceback. It must use
   the same torn-final-line rule as `raw_rows()` (Dv473), AND a torn last unit is
   NOT answered: it is re-asked. A torn middle line still refuses loudly. Tests both
   directions, red against the current runner.
2. **The Mac gate counts UNIQUE unit ids and refuses duplicates and foreign ids BY
   NAME.** Today `read = len(rows)`: duplicate rows (a pre-fix file, a double launch)
   would push `unread` negative and turn the full-pass factor into a trivial GO — the
   runner-side skip is the only guard and a cap gate deserves two. A duplicate id or
   an id not in the pack is a named SystemExit on the gate/ingest path, never a
   KeyError. Tests red-first.

## D1 ($0) — the v5b registration and the re-ordered pack

`results/prereg_reader_probe_v5b.json` via `scripts/write_reader_prereg_v5b.py`
CALLING the v5 producer (Dv451 idiom); byte-identical rebuild; a test file holding its
claims, object-equality to v5 asserted for everything the reader is scored on
(bars 1–4, gold sha, collapse, N1, echo, ceiling 4000, one-attempt class, programme
stop-rule). The three registered differences:

1. **Cap $0.50.** At the $0.74/h worked example: 2 432.4 s total, minus one 60 s
   delete margin per pod segment, minus the reading projection 1 454.0 s → the
   pre-generation budget is finally POSITIVE (~918 s with one segment) and the
   registration publishes it. The card's price is READ ON THE DAY; `costPerHr` from
   the create response re-prices everything (Dv448 law).
2. **Transport gate-0, ssh dead-man (operator ruling):** if `runpodctl ssh info` has
   not answered with a connectable endpoint by **180 s of create-elapsed**, KILL —
   delete the pod, prove it by listing, and CREATE A REPLACEMENT (same card class,
   same datacenter). **At most 2 recreates per attempt; a third dead pod is a STOP**
   — that is a datacenter state, not bad luck. All segments bill the same step;
   `elapsed` for boot/kill gates is measured from EACH segment's own create; the
   affordability comparison is always `cap − spent_across_all_segments` vs the
   reading projection. Gate snapshots APPEND, labeled with the segment's pod id.
   Never two pods at once — the ban's goal is that two meters never run concurrently.
3. **The pack order (operator ruling): leg A by DESCENDING payable count, then leg B
   chunks 1→3.** Same 26 units, same 26 rendering shas — only the order moves, and it
   is registered. Re-solve the full-pass gate backwards over the new order and
   publish the table (Dv471's method): with 15/12/12-payable threads first, the
   knife-edge at unit 2 is gone — show the margins.

Pack at `results/reader_v5b_pack.json` — the path is registered and `--gate` names it
in its refusal. Anchor fresh, never regenerate.

## D2 — the run

The v5-run contract's transport preflight (report §3.1) is inherited verbatim: bundle
staging into a NEW directory (never `rm -rf repo` — the 467 MB adapter lives there),
`reader_v4_pod_runner.py` ships too (the import), **`--repo` passed explicitly**
(the argparse default points at the old checkout), detached launch by Dv454's form,
liveness by `pgrep -af`.

1. Anchor (`--step reader-v5b --step-cap 0.50`) → three listings (volume = positive
   control) → create with `--terminate-after` 90 min.
2. **Gate-0 watch:** poll `ssh info` at 3–4 s; connectable by 180 s or KILL →
   delete → prove by listing → recreate (≤2). Every segment's create/kill lands in
   the run record.
3. On a live pod: stage from the bundle, verify checkout + handshake (the handshake
   proves staging, not the exit code), launch detached, watch with gates APPENDED;
   scp the partial jsonl inside the poll loop BEFORE every gate; boot-kill and
   full-pass exactly as registered — the KILL/STOP thresholds re-derived from the
   real `costPerHr` and pasted verbatim.
4. All 26 units in the registered order, transport stop at the first balanced object,
   per-unit rows flushed as they land. On a recreated pod the runner RESUMES: answered
   units skipped, a torn last unit re-asked (step 0.5's fix is what makes this legal).
5. Delete, never stop; three listings against the before-set; guard read (expect a
   LOWER BOUND); close only when the walk answers, else the close is the named debt.

## D3 — scoring and the verdict

`PYTHONPATH=src python3.11 scripts/score_reader_v5.py` on the Mac, unchanged: bars 1–4
over leg A (collapsed + uncollapsed beside), m1–m4 over leg B, bar 5 against the v5b
step ledger, the three-state echo census per thread (`@matusi_ukr:22242` and
`@VARUS_channel:10366` by name), refusal/repair censuses vs v4's paired columns,
finish_reason per unit at 4 000, tokens per answered row, stop telemetry (cut units,
seconds saved — still the one unmeasured thing). Bar-4 arithmetic named: which of the
7 non-agreed gold rows moved (needs ≥5: `21601`, `580124`, `580129`, `47899`,
`47902`, `48283`, `578951`).

## Verify (paste outputs, `python3.11` throughout)

```
make check                                   # counts before and after
runpodctl pod list -a                        # [] after; plus the other two listings
python3.11 scripts/runpod_guard.py --step reader-v5b --step-cap 0.50
shasum -a 256 results/prereg_reader_probe_v5b.json results/reader_v5b_pack.json
<v5b registration digest + byte-identical rebuild + object-equality test line>
<the re-solved gate table over the new order>
<verdict record printed by the scorer — or its named refusal if the run died>
```

## Report

`docs/reports/reader-v5b.md`, path-only in chat. Deviations from **Dv475** with
`[cause:]` tags; five-line Process signals. Read back first, one line each: what may
NOT move in this registration (the instrument) and the three things that do; the
gate-0 policy and the third-pod STOP; segment accounting in one sentence; the
re-solved unit-2 margin; when the registration freezes (FIRST `pod create` of the
attempt — recreates read the same frozen record).

## DO NOT

- No serverless anything. Never two pods concurrently. Delete, never stop.
- No cap raise, no anchor regeneration, no edit to any frozen file once the FIRST pod
  of the attempt exists; no re-ask of an answered unit (a torn unit is unanswered).
- Leg B rows never reach a leg-A bar, a production aggregate, or a window price.
- Team-lead files: commit verbatim, never edit. Never `git add -A`.
- Numbers in the report point at artifact paths; prose never carries a figure the
  artifact does not.
