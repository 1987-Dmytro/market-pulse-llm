# PROMPT — reader-v5-prep: the sitting's four rulings become instrument v5, at $0

**A $0 contract. NO pod, NO serverless, NOTHING billable is created here — the only
guard write is closing the settled `reader-v4` step. This contract lands the
17.08 sitting's rulings as prompt v5 + parser/runner/scorer v5 + the v5 registration
file, plus the accepted phase's named debts. The paid run is a SEPARATE contract
(`reader-v5-run`), issued after this one is accepted.**

**Baseline:** `make check` 2 685 / 2 skipped at HEAD (team lead's own run, 17.08).
Working tree carries an uncommitted tail: `knowledge/daily_logs/2026-08-16.md`,
`knowledge/index.md`, `knowledge/daily_logs/2026-08-17.md`, and the team lead's
acceptance edit in `docs/STATUS.md`.

## Step 0 — the tail

Commit by path, never `git add -A`: the three `knowledge/**` files in a vault commit;
`docs/STATUS.md` verbatim in its own commit — it is the team lead's file.

## Step 0.5 — debts of the ACCEPTED reader-v4 (named debts, not new scope)

1. **Close the `reader-v4` step.** The walk has posted (team lead's guard read 17.08:
   step resources $0.2361 — pods only, serverless $0.0000; the $0.3917 headline is the
   always-on volume dripping into the open window). Run
   `python3.11 scripts/runpod_guard.py --step reader-v4 --step-cap 0.35 --close --note
   "reader-v4 settled"`. Then re-run `scripts/score_reader_v4.py` so bar
   `5_time_and_cost` scores against the closed ledger, and commit the updated verdict.
   **Bars 1–4 may not move:** state in the report that the verdict changed ONLY in
   `5_time_and_cost` (compare the two files and say so with evidence).
2. **ADR `reader-v3-serverless-close-and-the-pod-ruling`** (knowledge/decisions/ +
   INDEX row): v3 closed at $0.3936 with nothing read; a boot no branch could stop;
   the operator's ruling — a pod with the boot in plain sight and a kill rule that is
   code. Numbers from the two reports, not from memory.
3. **ADR `reader-v4-closed-and-sitting-17-08`** (+ INDEX row): v4's honest negative
   (23/23 for $0.2361-class money, bars 1/4 failed, containers cured — 0 repairs
   fired), and the sitting's rulings recorded verbatim: (a) attribution block in the
   prompt; (b) transport stop at the first balanced object; (c) the narrow F2a
   carve-out; (d) per_comment echo + the mechanical chunking leg on
   `@klopotenkofood:6040`; (e) cap $0.45; (f) the PROGRAMME STOP-RULE — if v5
   completes and bars 1 and 4 are not both taken, the prompt-engineering line CLOSES
   and the next step is an architecture sitting, never a v6 of the same kind.
4. **Runbook hygiene, both from paid lessons:** the detached launch must not hold the
   ssh channel (Dv454 — launch via `nohup … </dev/null >log 2>&1 &` or `ssh -f`), and
   every verify command in runbooks/reports names `python3.11` explicitly (the team
   lead's own scorer run failed on system `python3` = 3.9 before reproducing
   byte-identically on 3.11).

## D1 ($0) — prompt v5: seven pairs over v3, every one traceable to a paid miss

`READER_THREAD_PROMPT_V5 = _swap(...)` over `READER_THREAD_PROMPT_V3`
(`src/market_pulse/prompts.py:852` is the v3 anchor; `_swap` refuses an unmatched old
text, which is the audit). Registered as task `"reader_thread_gm4_v5"` in the `READER`
set. **There is deliberately no v4 prompt — the number follows the contract that
registers it; write that in a one-line comment beside the constant.**

The seven pairs. Semantic content is FIXED here (sitting rulings); the English/Ukrainian
phrasing inside each pair is yours:

1. **Attribution block** (→ all four bar-4 misses, F1c, the F2 fork): the subject of a
   signal and of a per_comment row is read off THE COMMENT ITSELF, never off the
   thread's protagonist. The test: would the complaint/praise survive the chain or
   brand being swapped? Then it is «категория_личное», not the chain and not the
   brand. «сеть_ритейлер» only where the shop AS a shop (service, checkout, delivery,
   its shelves) is the subject. Three SYNTHETIC micro-examples, one per confusion pair.
2. **Aspect contrast** (→ F1b): a question «а є …?» / a request for a kind of product
   is `availability`, not `taste` — the aspect names what the text is ABOUT, not what
   the product is enjoyed for.
3. **Evidence of an exchange** (→ F1b): when a question and the channel's answer make
   one demand signal, `evidence` carries BOTH msg_ids.
4. **The F2a carve-out, narrow** (→ F2a): an event that changes the availability or
   status of the POST's subject (a destroyed warehouse, a recalled batch, a delisting)
   is a signal about the post's subject even when the comment does not name it.
   Opinions without a name are still never carried over — the old law stands for them.
5. **One vocabulary** (→ the seam): «категория» leaves the `signals.subject_type`
   list; «категория_личное» is the one word for that class, matching duty (2).
6. **The echo duty** (→ 93/111, the dropped 578951): the request lists the payable
   msg_ids; `per_comment` carries one row for EVERY id ON THAT LIST, in list order.
7. **Chunk header semantics** (→ leg B): when the request says «частина i з n», the
   duties apply to THIS part's comments; the echo duty applies to THIS part's list.

**Contamination guard:** no example sentence in pair 1–4 may occur as a substring of
any stored comment or any gold file — prove it with a test or a grep over the evidence
store and paste the proof. Teaching the exam is a red gate.

`prompts.py`'s sha moves → the **MOVED-tuple manoeuvre** (precedent
`tests/test_reader_gold.py`; third-plus time in this family). Enumerate the fan-out
with the typed walk over `results/**.json` (preflight counted 10 records naming
`prompts.py`), treat each as v3-prep §2.2 did. **Re-render proof:** the v4
registration's 23 request shas (task v3) rebuild byte-identically after the edit —
that test is the seam's law.

## D2 ($0) — render, parser, runner, scorer

- **`reader_messages_gm4` gains an optional `part` kwarg, default `None`.** Default
  path renders BYTE-IDENTICALLY to today (proof = the re-render test above). With
  `part=(i, n)` it adds the one chunk-header line inside the fence and passes only
  that chunk's comments. No other signature change; no default moves
  ([[a_sealed_caller_forces_the_default]] stands).
- **Parser v5** (new module or v5 entry point CALLING v3's `parse_reply` — the Dv451
  idiom, never editing the shipped one): (a) echo verification — the reply's
  `per_comment` ids compared against the request's list; missing/extra ids REPORTED
  per thread (beside the bars for leg A; gating for leg B); (b) chunk merge —
  `per_comment` concat (disjoint by construction — verify), `signals` deduped on
  (signal_type, subject_type, subject_id, aspect, stance) with evidence unioned,
  `entities` deduped by (name, msg_id), `noise` concat; (c) strict domains and
  refuse-on-conflict UNCHANGED.
- **Runner v5** (imports v4 runner's handshake/checks): generation STOPS at the first
  balanced top-level JSON object — incremental decode, brace depth counted OUTSIDE
  string literals (escapes handled); the persisted raw reply is exactly the emitted
  prefix; a reply that never balances runs to the ceiling as today. Tests on crafted
  texts: braces inside strings, escaped quotes, a second object after the first (cut),
  never-balancing (ceiling).
- **Gate records APPEND** (v4's overwrite lesson): the run record keeps a `gates`
  LIST; every WAIT/GO/KILL snapshot is appended, none overwritten.
- **`scripts/score_reader_v5.py`** CALLS v3/v4 scoring functions; adds the
  completeness census (rows returned/requested per thread, absent ids NAMED) and the
  leg-B mechanical bars; keeps uncollapsed-beside-collapsed reporting.

## D3 ($0) — the v5 registration, written now, FROZEN when the run's pod exists

`results/prereg_reader_probe_v5.json` via `scripts/write_reader_prereg_v5.py`
(byte-identical rebuild + a test file holding its claims):

- **Leg A:** the same 23 threads, digest `ccef35fa…` copied from v4; bars 1–4
  UNCHANGED and copied object-equal where possible (gold r2 `716ff417…`, symmetric
  collapse, N1 `excluded_with_cause`, thresholds 5/5 · 4/4 · 0 · ≥0.80). Completeness
  is REPORTED beside the bars, never gating bars 1–4.
- **Leg B:** `@klopotenkofood:6040` (43 payable comments — census `caa17216…`),
  chunked at ≤16 per chunk (43 → 16/16/11), NO semantic gold, CANNOT touch bars 1–4.
  Its gating bars are mechanical: m1 — the union of `per_comment` ids equals exactly
  the 43 payable ids, no duplicates; m2 — `finish_reason` stop on every chunk; m3 —
  every chunk parses; m4 — the merged signal list carries no two entries identical on
  the dedupe key.
- **Bar 5: cap $0.45 all-in** (operator ruling 17.08), one pod, kill rule as code,
  gates appended. The projection FLOOR for leg A is v4's own measured
  **39.461 s/thread** (probe-b's 31.6 is the wrong floor now — v3-output is longer);
  leg B is projected from v4's 137.83 tokens per requested row × 43 rows plus
  per-chunk prefill, stated as an estimate with its own gate. Both projection legs
  (per-thread AND per-payable-comment), pessimistic binds. The card's price is READ ON
  THE DAY (`runpodctl gpu list`, Dv448 law); the worked example may use $0.74/h and
  must say that is an example.
- **One attempt** (a kill, a STOP, or a completed run with a failed bar closes the
  question) and the **programme stop-rule** from the ADR, pre-registered in the file.

## Verify (paste outputs, `python3.11` throughout)

```
make check                                        # counts before and after
python3.11 scripts/runpod_guard.py --step reader-v4 --step-cap 0.35   # CLOSED, decomposition shown
<v4 verdict re-scored: bar 5 line + proof bars 1–4 unchanged>
<prereg v5 digest + byte-identical rebuild line>
<re-render test: v4's 23 request shas hold after the prompts.py edit>
<contamination grep/test output>
<runner stop tests + parser merge/echo tests named in the pytest output>
```

## Report

`docs/reports/reader-v5-prep.md`, path-only in chat. Deviations from **Dv456** with
`[cause:]` tags; five-line Process signals. Read back first, one line each: the seven
pairs; the stop-rule; what leg B can and cannot touch; the byte-preservation proof;
why this contract spends $0.

## DO NOT

- Nothing billable: no pod, no serverless, no endpoint, no template. The ONLY guard
  write is the `reader-v4` close (idempotent — a re-close is refused, proven).
- No edits to prompt v1/v2/v3 texts, v3 parser behaviour for v3-task replies, gold r2,
  any sealed registration, `scorer.py`, shipped census files. Registered request
  bytes of frozen records must re-render identically — that is a test, not a promise.
- Team-lead files (docs/STATUS.md, docs/SPEC.md, docs/PROMPT-*): commit verbatim,
  never edit. Never `git add -A`.
- The paid run is NOT in this contract. `results/prereg_reader_probe_v5.json` is
  committed here and freezes only when the run contract's pod exists.
