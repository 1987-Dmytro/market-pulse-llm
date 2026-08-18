# guard-until — the walk gets an end, the preflight becomes an instrument, and three ledgers close

**Read back, one line each.**

- **~427 000 ms** — `pass1-probe`'s expected COMPLETE walk. Re-derived from
  `results/pass1_probe_run.json` `segments`: one segment, created `2026-08-17T18:41:24+00:00`,
  deleted `18:48:31+00:00` = 427.0 s, and `billed_seconds: 427.0` says the same independently.
  **MATCHES.**
- **~657 000 ms** — `pass1-probe-b`'s. Same derivation on `results/pass1_probe_b_run.json`:
  `09:47:42+00:00` → `09:58:39+00:00` = 657.0 s, `billed_seconds: 657.0`. **MATCHES.**
- **The close tolerance** — **MISMATCH, and the finding is bigger than the number.** The named
  artifact cannot yield a tolerance at all: its «6–7%» holds for 3 of 7 rows, the max divergence is
  **100.00%**, and every divergence decomposes into a defect in how the table's WINDOW was built
  rather than into billing spread. **Nothing was closed by this contract** — its own refusal gate —
  and the operator then ruled the band at 7% and closed the three convergent ledgers by hand
  (addendum under D3).
- **What `--until` bounds:** the walk. Both callers of it — the step's open reading and the
  `--close` walk — and nothing else. It does NOT bound the balance delta, which has no window, so
  an open step goes on drifting; `--until` is what makes the CLOSE that stops the drift possible.
- **The completeness rule for a close:** a bounded walk's `timeBilledMs` must sit inside
  `max(1 000 ms, 1% × the run record's own billed span)`. Outside it the walk is PARTIAL, not a
  read, and `closing_record()` returns nothing.
- **The append-only law:** a closing entry lands beside the sessions already there and moves none of
  them; a ledger that fails a gate stays OPEN and NAMED, never forced and never approximated.
- **What this contract may NOT touch:** the reader — instrument, prompt, bars, population — which
  belongs to the SITTING; the frozen records (`results/prereg_*`, packs, verdicts, gold); the team
  lead's files, which are committed verbatim and never edited.

**Not one byte of any ledger moved under the contract itself.** 31 `results/spend_*.json`, hashed
before the first edit and after the last command of D1–D3, `diff` empty — at git level too. Four of
them moved afterwards, under the operator's own ruling, and only by APPENDED entries (addendum under
D3). Every cloud call throughout was a read: no pod, no serverless, no volume change. **$0.**

---

## Step 0 — the tail, by path, in two commits

```
$ git status --porcelain      # at the start of this session
 M docs/STATUS.md
 M knowledge/daily_logs/2026-08-18.md
 M knowledge/hot.md
 M knowledge/index.md
?? docs/PROMPT-guard-until.md
?? docs/reviews/2026-08-18-weekly-retro.md
```

Exactly the paths the contract named, and nothing else was in the tree.

- `ee0de07 vault(tail): …` — the three `knowledge/` files, staged by path.
- `bca17a9 docs(team-lead): …` — `docs/STATUS.md`, `docs/reviews/2026-08-18-weekly-retro.md` and
  `docs/PROMPT-guard-until.md`, **committed verbatim, never edited**, in their own commit.

No `git add -A` at any point in this session.

## Step 0.5 — the ADR debt of the accepted step

`knowledge/decisions/pass1-probe-b-measured-and-the-sitting-owns-it.md`, and the INDEX row beside
it (`f75cc3a`). It records the decision and cites `docs/reports/pass1-probe-b.md` for the argument:
bar P1 **9 of 14** against 12, the failure is ONE field (all five losses `subject_type`, two of them
the model declining to type at all with **0 refusals of 64** behind it), the transport settled
(gate-0 GO ×3, boot 237.2 s inside the raised 420 s ceiling, 1.53× spread registered rather than
averaged, **$0.135050 of $0.20**), and the STOP returns the question to the SITTING. `check-wikilinks`
OK, none broken.

---

## Step 1 — the H6 refusal gate: two constants reproduce, one does not

### The two that reproduce

```
$ python3.11 -c "…"      # results/pass1_probe_run.json, segments, create->delete summed
pass1-probe    created 2026-08-17T18:41:24+00:00  deleted 18:48:31+00:00  = 427.0 s  billed_seconds 427.0
pass1-probe-b  created 2026-08-18T09:47:42+00:00  deleted 09:58:39+00:00  = 657.0 s  billed_seconds 657.0
```

Both records carry ONE segment, so «summed» and «the segment» are the same number, and each carries
its own independent `billed_seconds` that agrees with the span. Nothing to report.

The artifact the third constant comes from is itself pinned and MATCHES:
`docs/reports/pass1-probe.md` is pinned by `results/prereg_pass1_probe_b.json.authority` at
`8c8cf16a32c9…` and the live file digests to the same, so the table below is byte-for-byte the one
the `pass1-probe-b` registration sealed.

### The third: the tolerance does not re-derive, and the table cannot yield one

The claim under test is `docs/reports/pass1-probe.md` §(3): *«with an end bound the walk agrees with
each ledger's own reading to within 6–7%»*. Re-derived from that table, every row:

| ledger | recorded | bounded walk | divergence | within 7%? |
|---|---:|---:|---:|:--:|
| `45h2` | $8.8287 | $8.217558 | **−6.92%** | yes |
| `srv2b` | $0.9999 | $0.939957 | **−5.99%** | yes |
| `srv2d` | $1.2332 | $1.163192 | **−5.68%** | yes |
| `5b` | $1.7069 | $1.484759 | **−13.01%** | no |
| `srv2c` | $0.1006 | $0.077418 | **−23.04%** | no |
| `5c1_vis` | $0.4484 | $0.875542 | **+95.26%** | no |
| `probe_a` | $0.0750 | $0.000000 | **−100.00%** | no |

**Max |divergence| = 100.00% (`probe_a`); 95.26% excluding the zero-walk. Three rows of seven are
inside 7%.** The claim is not reproducible. Under the contract's own clause — *«a mismatch on any of
the three: STOP, report the figure, nothing is closed»* — **D3 does not run.**

### And the reason it cannot be repaired by picking a bigger number

A tolerance is supposed to measure how far a billing walk can honestly sit from a ledger's reading.
Every one of the four outliers is a defect in how the table's WINDOW was constructed, not spread:

**(a) The window start is each ledger's first SESSION, not its anchor.** None of the seven carries
`anchored_at`, so the table substituted the first `gpu_sessions[0].at` — which is when the first
reading was taken, after money had already been spent. Measured, per ledger, as the money the walk
structurally cannot see:

| ledger | anchor | first session's balance | spent BEFORE the window | as % of the recorded reading |
|---|---:|---:|---:|---:|
| `45h2` | $27.5332912062 | $27.1128684841 | $0.4204 | 4.76% |
| `5b` | $18.3980224421 | $18.2271420227 | $0.1709 | **10.01%** |
| `srv2c` | $15.4915993671 | $15.4793697004 | $0.0122 | **12.16%** |
| `srv2d` | $15.3538770133 | $15.3434597244 | $0.0104 | 0.84% |
| `srv2b` | $16.5012168447 | $16.5012168447 | $0.0000 | 0.00% |
| `probe_a` | $23.0729004744 | $22.9979228605 | $0.0750 | **99.97%** |

The three rows that land inside 7% are the three whose pre-window spend is 0.00%, 0.84% and 4.76%.
The two that miss by 13% and 23% are the two whose pre-window spend is 10.01% and 12.16%. The
«spread» is the window.

**(b) `probe_a`'s window is zero-width.** Its ledger holds ONE session, written at 18:39:15 *after*
the endpoint and template were deleted, so start = end = the moment the step finished and 99.97% of
its recorded reading was spent before the window opens. The walk answers «no billing rows yet» —
which is not a $0.00 reading, it is no reading — and −100% is arithmetic on an empty set.

**(c) `5c1_vis` holds TWO anchors in one file.** `runpod_balance_at_5c1vis_vis-b_start` and
`runpod_balance_at_5c1vis_vis-c_start`. The table's window spans both sessions while the recorded
reading, $0.4484, is `vis-c`'s delta alone — so +95.26% compares a two-step walk against one step's
figure. Driven through the guard, this row is not closable at all (below).

**(d) The right-hand side is a LAGGED reading of the same walk.** Measured on `pass1-probe-b`, and
the identity is exact to ten decimal places:

```
$ python3.11 -c "print(20.9182116007 - 20.8328926451)"
0.0853189556000018                                  <- the ledger's recorded step_spent_usd

$ runpodctl billing pods --bucket-size hour \
    --start-time 2026-08-18T09:47:08Z --end-time 2026-08-18T09:52:00Z
[{"amount": 0.08531895559281111, "timeBilledMs": 413376, …}]
```

The ledger's «recorded reading» taken at 09:59:15 is exactly what the same walk returns truncated at
**09:52:00** — seven minutes earlier. The account balance settles behind the billing history, so a
ledger closed promptly after a pod is deleted records a systematically LOW figure: for
`pass1-probe-b`, 64.9% of the truth. Two opposing defects, which is why five rows read low and one
reads high.

**Conclusion.** The re-derivation does not disagree with «6–7%» by a margin; it says the artifact
conflates a window bug with billing spread, so no number taken from it would be measuring what a
tolerance has to measure. `--tolerance` therefore ships as a **required parameter with no default**
— the caller says a number or there is no close.

---

## D1 ($0) — the preflight instrument (pilot H1)

`scripts/preflight.py` + `make preflight ARGS='…'` (`c871a4c`). Four blocks per query: hits with
counts split by root · prose quoting the query's VALUE · the pin registry joined against the query's
own hits · sha256 of every pinned path against what is pinned.

**The instrument's own control caught its first version.** `docs/STATUS.md` «Пины — потребители»
names four files as pinned; the first walk knew only the `{"sha256": …, "module": "path"}` shape and
found ONE of them. It refuses (exit 1) rather than warning, and adding the two shapes the records
actually use — `producer.borrowed` with the path as the KEY, and `frozen_when_the_pod_exists` as a
freeze with no digest — took the registry from 1 379 to 1 466 pinned paths. `git.dirty` lists are
proved NOT to be pins, both ways, in `tests/test_preflight.py`.

**The value channel, on a real constant.** `CYCLE2_CAP_USD` greps to 13 hits in 7 files. The same
query's VALUE, `20.00`, is quoted on **38 lines in 17 files** that never name the constant. That is
pattern P1 in one command.

### The dogfood — run BEFORE the guard was edited

This is the pre-edit run and it is checkable as one: the `live` digest it prints for the guard,
`23aae8a49ae8f546…`, is `git show c871a4c:scripts/runpod_guard.py | shasum -a 256`, i.e. the file as
the D1 commit left it. Re-running the same command today prints `1d27f7a24a194b10…` instead, which
is the point — the instrument's output is dated, and the dated one is what authorised the edit.

```
$ make preflight ARGS='--limit 3 -- --until closing_record billing_by_kind spend_pass1_probe scripts/runpod_guard.py'
pin registry: 1466 paths pinned by results/*.json

QUERY  --until
[1] hits — 27 in 10 files          other 1  docs/ 18  knowledge/ 6  scripts/ 2
[2] prose — 24 lines in 8 files
[3] pins — 2 of the 11 touched paths are pinned by a record
    docs/PROMPT-pass1-probe-b.md  <- results/prereg_pass1_probe_b.json.contract 8180beb399bf…
    docs/reports/pass1-probe.md   <- results/prereg_pass1_probe_b.json.authority 8c8cf16a32c9…
[4] digests — 2 of 2 pinned paths match every digest on them

QUERY  closing_record
[1] hits — 16 in 10 files          other 1  docs/ 6  knowledge/ 3  scripts/ 4  tests/ 2
[2] prose — no module-level literal resolves for this query
[3] pins — 2 of the 11 touched paths are pinned by a record
    scripts/runpod_guard.py  <- results/prereg_5c2_run.json.producer.borrows e19ea02481b3…
[4] scripts/runpod_guard.py  live 23aae8a49ae8f546…  DIFFERS
        results/prereg_5c2_run.json.producer.borrows pins e19ea02481b32415… — the file has moved since

QUERY  billing_by_kind
[1] hits — 48 in 18 files          other 1  docs/ 10  results/ 10  scripts/ 10  tests/ 17
[3] pins — 3 of the 19 touched paths are pinned by a record
    scripts/runpod_guard.py · results/reader_v4_verdict.json · results/reader_v5b_verdict.json

QUERY  spend_pass1_probe
[1] hits — 5 in 5 files            docs/ 3  knowledge/ 1  tests/ 1
[3] pins — 1 of the 6 touched paths is pinned; [4] 1 of 1 match

QUERY  scripts/runpod_guard.py
[1] hits — 156 in 74 files         docs/ 67  scripts/ 60  results/ 15  knowledge/ 8  tests/ 4  src/ 1
[3] pins — 30 of the 74 touched paths are pinned by a record
[4] digests — 22 of 30 pinned paths match every digest on them
```

**The answer the contract needed before D2**, and the reason the dogfood is the point:
`scripts/runpod_guard.py` **is pinned**, by `results/prereg_5c2_run.json.producer.borrows`, and the
live file **already DIFFERS** from what that record pins. So editing it does not break a matching
pin — it widens one that has been stale since 2026-08-16. What that pin's own test demands instead
is a MOVED manoeuvre, which is where the third name below came from.

`spend_pass1_probe*.json` was queried as the prefix `spend_pass1_probe`: the walk is a FIXED-string
grep and a `*` in it would match nothing. The prefix covers both files.

---

## D2 ($0) — the guard learns an end bound (red-first)

Eight tests written first, then the code. Seven went red; the eighth is the negative control that
asserts `--end-time` is ABSENT on an unbounded call, and a control for an absence is green before the
change by construction — which is exactly why it is not the test that proves anything, and why it is
written beside one that is:

```
$ PYTHONPATH=src python3.11 -m pytest tests/test_runpod_guard.py -q     # before the implementation
7 failed, 43 passed in 0.48s
$ PYTHONPATH=src python3.11 -m pytest tests/test_runpod_guard.py -q     # after
52 passed in 0.21s
```

**The seam the tests are written at is new, and it is the one the flag lives on.** Every test in
that file patched `billing_by_kind` itself, so a `--until` that never reached the command line would
ship green through all 968 lines. The new block patches `guard.runpodctl` one layer lower and
asserts the **argv list**: `--end-time` present with the value given, `--bucket-size hour` present,
and — the negative control — `--end-time` **absent** rather than empty on an unbounded call.

### What was built

- `billing_by_kind(anchored_at, until=None)` → `(lines, how, ms)`. The end bound rides through to
  `runpodctl billing`, and the third return is the walk's `timeBilledMs` — the only thing that can
  tell a bounded walk from a PARTIAL one.
- `--until <ISO-8601>` bounds **both** callers: the step's open reading and the `--close` walk.
- `--expect-ms` is the run record's own billed span. `complete()` is the Dv488 three-state walk as a
  function: outside `max(MS_FLOOR 1 000, MS_BAND 1% × expect)` the walk is partial and
  `closing_record()` returns nothing, with **both figures** printed in the refusal.
- `--tolerance` — required for a step close, no default, for the reason step 1 gives. The settled
  figure is checked against the ledger's own recorded reading and the check runs **before the
  write**.
- The LIVE ledger's close now re-walks when it is given a window. It used to take `enforce()`'s
  unbounded lines while recording `window_start: --since`, so the entry's window and its figures
  came from two different walks. Fixed as a consequence of plumbing the flag, and named as Dv508.

### The constants, with their derivations

```python
MS_BAND  = 0.01     # pass1-probe-b's COMPLETE walk: 657 684 ms vs a record of 657 000 = +0.104%
                    # pass1-probe's PARTIAL walk:    300 000 ms vs a record of 427 000 = -29.7%
                    # 1% is 10x above the one measured convergence and 30x below the one measured
                    # shortfall. TWO-SIDED: over-reading is the $86.49 class through a wide window.
MS_FLOOR = 1_000    # the run record publishes billed_seconds to whole seconds
BILLING_BUCKET = "hour"     # what the report's bounded probe used -- and cosmetic, measured below
```

### `--bucket-size` changes no total — measured before it was wired

```
$ runpodctl billing pods --bucket-size day  --start-time 2026-07-20T00:00:00Z --end-time 2026-08-18T23:00:00Z
  rows 26   total $18.60995761   ms 122329741
$ runpodctl billing pods --bucket-size hour --start-time 2026-07-20T00:00:00Z --end-time 2026-08-18T23:00:00Z
  rows 78   total $18.60995761   ms 122329741
```

Identical over 30 days, and identical over a 12-minute window. The bucket changes the row GROUPING
and never the sum, so passing `hour` on every call — including the live cap readings — is provably
not a basis change. Dv483's «the guard passes neither `--end-time` nor `--bucket-size`» reads as two
defects; measured, only the end bound is one.

### The pin the preflight found: `MOVED_BORROWS` grows a third name

`tests/test_prereg_5c2.py::MOVED_BORROWS` records which borrowed modules have moved under the sealed
`results/prereg_5c2_run.json`, one token per move. Its own docstring predicts the failure it then
had: **the whole suite stayed green across this third move**, because a list of what moved cannot
check its own completeness. `"--until"` was added by hand, with the flag as the token rather than the
word `until` — which the sealed blob already carries in a docstring, and a token the recovered bytes
contain would assert nothing.

```
$ git show 0e390ff:scripts/runpod_guard.py | grep -c -- "--until"       # sealed
0
$ grep -c -- '"--until"' scripts/runpod_guard.py                         # live
1
$ PYTHONPATH=src python3.11 -m pytest tests/test_prereg_5c2.py -q
25 passed in 0.22s
```

---

## D3 — the closes: ZERO by this contract, then three by the operator's ruling

Step 1's refusal gate blocks every close. So that the debt is carried with figures rather than with
prose, every command the contract specifies was driven against the real ledgers' data in a
**sandbox** — a copy of `scripts/runpod_guard.py` under a scratch `REPO_ROOT`, so `LEDGER`,
`CYCLE2_LEDGER` and every step ledger resolve to copies while the billing reads stay live and free.
The production ledgers were hashed before and after: **no byte moved.**

### 1. `pass1-probe` — REFUSED on its own merits, independent of the tolerance

```
$ python3.11 scripts/runpod_guard.py --step pass1-probe --step-cap 0.20 --close \
    --since 2026-08-17T18:39:40+00:00 --until 2026-08-17T18:49:29+00:00 \
    --expect-ms 427000 --tolerance 0.07 --note "…"
REFUSED: the billing walk over pass1-probe's window answered «read» and covered 300000 ms against
the run record's 427000, so there is no settled figure to close on. A PARTIAL walk is a third state
and settling on it freezes a number that is never re-derived.                          (exit 1)
```

**300 000 of ~427 000 ms — 70.3%, unchanged since 2026-08-18T09:0xZ.** The debt stays NAMED with its
observed ms. Its open reading has meanwhile drifted **$0.2075 → $0.4305** against a $0.20 cap, all of
it the volume.

### 2. `pass1-probe-b` — the walk IS complete, and the close still refuses

```
$ python3.11 scripts/runpod_guard.py --step pass1-probe-b --step-cap 0.20 --close \
    --since 2026-08-18T09:47:08+00:00 --until 2026-08-18T09:59:15+00:00 \
    --expect-ms 657000 --tolerance 0.07 --note "…"
REFUSED: pass1-probe-b settles at $0.135538 against its own recorded reading of $0.085300 — 58.9%
off, outside the registered tolerance of 7.0%. NOT closed: a close outside the band is a refusal,
never a rounding, and the ledger stays OPEN and named.                                 (exit 1)
```

The completeness gate PASSES — 657 684 ms against 657 000, +0.104%. The dollar gate refuses at
**58.9%**. The contract calls this one «likely ripe» because *«the pods line already read $0.1355 ≈
the record's $0.135050»* — but that compares the walk to the **run record**, while D3.3's own rule
names *«its own recorded reading»*, which is the ledger's $0.0853. Two right-hand sides in one
document, and they part by 1.59×. Under the run record the divergence is +0.36% and this closes;
under the ledger it is +58.9% and it does not. **The instrument implements the rule the contract
wrote for the batch, so it refuses.** Step 1 had already stopped it; this is the second lock.

### 3. The 22-ledger batch — 3 inside 7%, 19 refuse

```
$ python3.11 …/sandbox/scripts/runpod_guard.py --step <each> --step-cap <its own> --close \
    --since <its window start> --until <its window end> --tolerance 0.07 --note "…"
TOTAL  closed 3 · refused 19 of 22
```

**A. the seven with an anchor and a window**

| ledger | verdict | figures |
|---|---|---|
| `45h2` | inside 7% | settled **$8.217558** vs recorded $8.8287 — **6.92%** off |
| `srv2b` | inside 7% | settled **$0.939957** vs $0.9999 — **5.99%** |
| `srv2d` | inside 7% | settled **$1.163191** vs $1.2332 — **5.68%** |
| `5b` | REFUSED | settled $1.484759 vs $1.706900 — **13.0%** off |
| `srv2c` | REFUSED | settled $0.077418 vs $0.100600 — **23.0%** off |
| `probe_a` | REFUSED | «no billing rows yet», **0 ms** — the window is zero-width |
| `5c1_vis` | REFUSED | *«has no anchor on disk — a step that never ran cannot be closed»* |

`5c1_vis` is the row the control table could not have closed under any tolerance: its anchor key is
`runpod_balance_at_5c1vis_vis-b_start`, which `anchor_key_in` does not recognise for the step name
`5c1_vis`, so the guard reads the ledger as never having run. A row of the tolerance's own
derivation table is not reachable by the instrument the tolerance is for.

The three settled figures reproduce the report's bounded column exactly, which is the strongest
thing that can be said for that column: `45h2` $8.217558 = $8.217558, `srv2b` $0.939957 = $0.939957,
`srv2d` $1.163191 against a published $1.163192 — one micro-dollar, because the guard rounds each
kind to 6 dp and then sums while the report summed and then rounded (Dv512).

**B. the ten with no RunPod anchor** — `3b`, `45d`, `45e`, `45g`, `45g2`–`45g6`, `5c1_captions`:
all ten REFUSED, *«… has no anchor on disk — a step that never ran cannot be closed»*. OpenRouter-only
steps. The refusal returns before any write.

**C. the five with an anchor and no window** — `5c2run`, `sku_b`, `sku_b_v3`, `sku_b_v4`, `skub2`:
all five REFUSED, *«carries no `anchored_at` and no `--since` was given, so the closing walk has no
window to ask for»*. `--until` does not change this: an end bound is not a window start.

### ADDENDUM — the operator ruled, and the three are CLOSED (2026-08-18 evening)

**«закрой три сходящихся леджера под 7%».** The band is the operator's, the closes are theirs, and
the caveat below was on the table before they ruled. Three commands, run verbatim against the
production ledgers:

```
$ python3.11 scripts/runpod_guard.py --step 45h2 --step-cap 9.00 --close --tolerance 0.07 \
    --since 2026-08-04T12:32:37+00:00 --until 2026-08-05T06:42:18+00:00 --note "…"
CLOSED spend_45h2.json at $8.2176 — entry APPENDED
45H2 CLOSED     $8.2176 of $9.00  (settled at 2026-08-18T19:01:05+00:00, window from 2026-08-04T12:32:37+00:00)
  pods            $8.2176
  network-volume  $0.1750   <- always on, beside the run and never inside it
  serverless      $0.0000                                                              (exit 0)

$ … --step srv2b --step-cap 4.00 … --since 2026-08-08T17:35:05+00:00 --until 2026-08-08T18:59:30+00:00
CLOSED spend_srv2b.json at $0.9400 — entry APPENDED
  pods $0.3898 · network-volume $0.0097 · serverless $0.5501                           (exit 0)

$ … --step srv2d --step-cap 2.00 … --since 2026-08-08T21:00:57+00:00 --until 2026-08-08T22:13:58+00:00
CLOSED spend_srv2d.json at $1.1632 — entry APPENDED
  pods $0.0052 · network-volume $0.0097 · serverless $1.1580                           (exit 0)
```

| ledger | settled | its recorded reading | off | band | verdict |
|---|---:|---:|---:|---:|---|
| `45h2` | **$8.217558** | $8.828700 | 6.92% | 7.00% | CLOSED |
| `srv2b` | **$0.939957** | $0.999900 | 5.99% | 7.00% | CLOSED |
| `srv2d` | **$1.163191** | $1.233200 | 5.68% | 7.00% | CLOSED |

Each entry carries `window_start`, `window_end`, `walk_ms`, `recorded_reading_usd` and the
`tolerance` it was judged under, so the gate's verdict is re-derivable from the record rather than
from this page. Each re-derives from what it publishes: `settled_usd` is exactly the sum of its own
`billing_by_kind` with the always-on kinds left out, and `billing_since_usd` is the sum of all three.

**Append-only, proved on all four files the closes touched** — the three steps and the live cycle-2
line, which witnesses each close (Dv447):

```
$ find results -name 'spend_*.json' | sort | xargs shasum -a 256 | diff ledgers.pre_close -
results/spend_45h2.json  results/spend_cycle2.json  results/spend_srv2b.json  results/spend_srv2d.json
                                   # exactly 4 of 31; the other 27 byte-identical

45h2     3 -> 4 entries   prefix-identical=True   every other field unchanged=True
srv2b    3 -> 4 entries   prefix-identical=True   every other field unchanged=True
srv2d    4 -> 5 entries   prefix-identical=True   every other field unchanged=True
cycle2  12 -> 15 entries  prefix-identical=True   every other field unchanged=True
```

**The batch line changes: 3 closed · 19 refused of 22.** Section A's table above stands as the
prediction; these are the same figures written to disk. Nothing in B or C moved — an anchor that
does not exist and a window that was never recorded are not things a band can fix.

**The caveat, now inside a settled record.** Each of the three windows starts at its ledger's first
SESSION, so the settled figure is right about the window it names and low about the step by the
pre-window spend: **$0.4204 for `45h2`, $0.0000 for `srv2b`, $0.0104 for `srv2d`**. It is recorded
here because a closing entry is never re-derived, and the next reader of `spend_45h2.json` should
know that $8.217558 is a window's figure and the step cost about $0.42 more.

**The cycle-2 line after the closes** — unchanged, as a close of a step must leave it:

```
$ python3.11 scripts/runpod_guard.py
CYCLE 2 SPENT     $1.8146 of $20.00
REMAINING         $18.1854
```

`make check` after the three writes: **2 927 passed, 2 skipped**. Nothing in the suite reads the
three step ledgers; `tests/test_repair_phase4_ledger.py` does read the live line and its invariant
(«a paid step is witnessed by the ledger the guard reads before a start») is satisfied by the three
witness entries rather than broken by them.

### What this contract itself closed: nothing

The three closes above are the operator's, taken after this contract's gate had already refused
them and after the pre-window figures were on the table. What the contract delivered is the
instrument and the refusal — and the refusal was the useful half: a run that had simply closed the
three at 7% would have written the same numbers without ever learning that 7% was a window bug's
shadow, and would have closed `pass1-probe-b` beside them on a right-hand side its own rule does
not name.

---

## Verify

```
$ make check                                          # baseline, before anything
2911 passed, 2 skipped in 481.60s (0:08:01)

$ make check                                          # after D1 + D2, on the tree that was committed
2927 passed, 2 skipped in 488.76s (0:08:08)

$ PYTHONPATH=src python3.11 -m pytest tests/test_runpod_guard.py -q
52 passed in 0.21s

$ PYTHONPATH=src python3.11 -m pytest tests/test_preflight.py -q
6 passed in 0.51s

                       # every code commit checked out and run on its own, not just the tip.
                       # `;` and not `&&`: the return to main must happen whether or not the
                       # suite is green, or a red run leaves the reader on a detached HEAD
$ git checkout -q --detach c871a4c; make check; RC=$?; git checkout -q main; echo $RC    # D1
2917 passed, 2 skipped in 482.22s (0:08:02)   EXIT=0                     # = 2911 + 6
$ make check                                                             # D2, at 46a477b's tree
2927 passed, 2 skipped in 488.76s (0:08:08)                              # = 2917 + 10
                       # c392c2e adds only this file, and no test reads docs/reports/ —
                       # the four that name it quote it in prose (`git grep -n docs/reports tests/`)

$ make preflight ARGS='--limit 3 -- --until closing_record billing_by_kind spend_pass1_probe scripts/runpod_guard.py'
    (pasted in D1 above)

$ python3.11 scripts/runpod_guard.py                  # the cycle-2 line, read-only
PHASE 4 CLOSED    $32.4708 of $33.00  (final reading 2026-08-16T11:09:48+00:00)
  pods            $17.6921
  network-volume  $3.2278   <- always on, beside the run and never inside it
  serverless      $11.5509
anchor            $22.51 at 2026-08-16T12:14:48+00:00
balance now       $20.70
  balance delta   $1.8146
  billing since   $1.8049 (read)
    pods            $0.9178
    network-volume  $0.5153   <- always on, beside the run and never inside it
    serverless      $0.3718
CYCLE 2 SPENT     $1.8146 of $20.00
REMAINING         $18.1854                                                             (exit 0)

$ runpodctl pod list -a
[]
$ runpodctl serverless list
[]
$ runpodctl network-volume list                       # the positive control: the listing works
[{"dataCenterId": "EU-RO-1", "id": "qw4nwleanc", "name": "mp-srv2", "size": 100}]

$ find results -name 'spend_*.json' | sort | xargs shasum -a 256 | diff ledgers.before -
NONE — no ledger byte moved        (31 files, hashed before the first edit and after the last command)

$ git status --porcelain results/ ; git diff --stat HEAD -- results/
                                   # both empty: nothing under results/ moved across the WHOLE
                                   # session, which is a stronger claim than a mid-session snapshot

$ python3.11 scripts/check-wikilinks.py
check-wikilinks: OK, none broken
```

---

## Deviations from Dv500

| # | what | tag |
|---|---|---|
| **Dv500** | **The close tolerance does not re-derive, and the artifact it was to come from cannot yield one.** «6–7%» holds for 3 of 7 rows; max divergence **100.00%** (`probe_a`), 95.26% excluding the zero-walk. The gate fired as designed: nothing is closed. `--tolerance` ships required with no default. | `[cause: contract-gap]` `[[a-tolerance-derived-from-two-bugs]]` |
| **Dv501** | **The control table's window start is each ledger's first SESSION, not its anchor.** None of the seven carries `anchored_at`. Pre-window spend measured at 0.00% / 0.84% / 4.76% / 10.01% / 12.16% / 99.97% of the recorded reading — and the three rows inside 7% are exactly the three with the smallest. The «control» column could not control what it was cited for. | `[cause: verify-gap]` `[[the-control-whose-window-was-the-defect]]` |
| **Dv502** | **`probe_a`'s window is zero-width.** Its one session is written after the step finished, so start = end and 99.97% of its spend precedes the window. −100% is arithmetic on an empty walk, and the guard correctly answers «no billing rows yet», which is not $0.00. | `[cause: verify-gap]` `[[a-window-never-asked-is-not-an-empty-one]]` |
| **Dv503** | **`5c1_vis` holds two anchors in one file and is not closable at all.** The table's row compares a `vis-b`+`vis-c` walk against `vis-c`'s delta (+95.26%); driven through the guard it refuses with «has no anchor on disk», because the key is `runpod_balance_at_5c1vis_vis-b_start` and `anchor_key_in` does not reach it for step `5c1_vis`. A row of the derivation table is unreachable by the instrument. | `[cause: contract-gap]` `[[a-row-the-instrument-cannot-reach]]` |
| **Dv504** | **The ledger's recorded reading is a LAGGED reading of the same walk, measured exactly.** `pass1-probe-b`'s $0.0853189556 is `0.08531895559281111` — what the same bounded walk returns truncated at 09:52:00, seven minutes before the balance was read. The balance settles behind the billing history, so a promptly-closed ledger records 64.9% of the truth. | `[cause: tooling]` `[[the-balance-lags-the-bill]]` |
| **Dv505** | **The contract's «likely ripe» uses a different right-hand side from its own rule.** D3.2 compares the walk to the RUN RECORD ($0.135050, +0.36%); D3.3 says «its own recorded reading», which is the ledger ($0.0853, +58.9%). They part by 1.59× and decide the close in opposite directions. | `[cause: contract-gap]` `[[two-readings-of-one-clause]]` |
| **Dv506** | **`--bucket-size` changes no total.** Measured day vs hour over 12 minutes and over 30 days: `$18.60995761` / `122329741 ms` both times, volume `$3.76250014` both times; only the row count moves (26 vs 78). Dv483 names two missing flags; one of them is cosmetic, and passing it is therefore safe on the live cap path. | `[cause: verify-gap]` `[[the-flag-that-changes-no-number]]` |
| **Dv507** | **Dv483's «2.6×–156×» mixes two bases.** 2.6× is unbounded/recorded (`45h2` 2.604); 156× and «`srv2d` alone 10.26×» are unbounded/BOUNDED (`srv2c` 155.86, `srv2d` 10.258). On one basis the range is 2.60×–119.94× against recorded, or 2.80×–∞ against bounded. The direction of the defect is unaffected; the range as quoted exists on neither axis. | `[cause: process]` `[[a-range-with-two-denominators]]` |
| **Dv508** | **`--until` bounds the walk and not the balance delta, and the LIVE close was taking two different walks.** `spend()` is `max(delta, walk)` and a delta has no window, so an open step keeps drifting whatever bound the walk carries (`pass1-probe` $0.2075 → $0.4305). Separately, `--close` on the live ledger recorded `window_start: --since` while its figures came from `enforce()`'s unbounded walk; re-walking when a window is supplied is part of plumbing the flag, and is the one place this contract changed behaviour beyond adding a parameter. | `[cause: spec-gap]` `[[a-bound-on-one-of-two-readings]]` |
| **Dv509** | **The preflight's own STATUS control caught its first version blind to two of three pin shapes.** It found 1 of the 4 files STATUS names as pinned; teaching it `producer.borrowed` (path as KEY) and `frozen_when_the_pod_exists` (a freeze with no digest) took the registry 1 379 → 1 466 paths. The control is a REFUSAL (exit 1), not a warning. | `[cause: verify-gap]` `[[a-registry-that-knows-one-shape]]` |
| **Dv510** | **`make preflight` swallowed its own options.** The recipe forced a `--` before `ARGS`, so `--limit 8` arrived as a QUERY and grepped 53 887 hits for the string `8`. Caught by the dogfood on the first real run; the recipe now passes `ARGS` verbatim and a dashed query brings its own `--`. | `[cause: tooling]` `[[the-separator-that-ate-the-flags]]` |
| **Dv511** | **`MOVED_BORROWS` stayed green across the guard's third move**, exactly as its own docstring predicts: a list of what moved cannot check its own completeness. `"--until"` added by hand, as the FLAG rather than the word `until`, which the sealed blob already carries in prose. | `[cause: verify-gap]` `[[a-law-that-grows-loudly]]` |
| **Dv512** | **`srv2d` settles at $1.163191 against a published $1.163192.** The guard rounds each kind to 6 dp and then sums (so the entry re-derives from what it publishes); the report summed the full-precision walk and then rounded. One micro-dollar, reported because the two are different rules and only one of them is checkable from the record. | `[cause: process]` `[[a-record-must-rederive-from-what-it-publishes]]` |
| **Dv513** | **`scripts/runpod_guard.py` was already stale against its pin before this contract touched it.** `results/prereg_5c2_run.json.producer.borrows` pins `e19ea02481b3…`; the live file was `23aae8a49ae8…` at the start of the session. The edit widens a stale pin rather than breaking a matching one — which is what made the MOVED manoeuvre the right answer instead of a re-pin. Found by the preflight, before the guard was opened. | `[cause: process]` `[[the-guard-you-built-and-then-bypassed]]` |

| **Dv514** | **The required flag broke this module's own documented command, and nothing was red.** `--close --step … --note` with no `--tolerance` now exits 2, and that is the example in `scripts/runpod_guard.py`'s docstring — the P1 class, in the file the contract changes. Fixed there and in `scripts/runbook_reader_v4.md`; closed permanently by `test_every_command_the_module_docstring_shows_is_still_a_command`, which drives the docstring's block through a new `parse()` seam and is proved to bite (the pre-fix example raises `SystemExit(2)`). **Six `docs/PROMPT-*.md` carry the same now-broken shape and are NOT fixed here** — they are team-lead files, and every one of them is a contract that has already run. | `[cause: tooling]` `[[the-documents-command-is-its-own-artifact]]` |
| **Dv515** | **`MS_BAND`'s two-sidedness was registered in prose and asserted nowhere.** The three ms tests covered under-reading and convergence, and the inflation test passed no `--expect-ms`, so the gate ran unarmed there — `complete()` could have been a one-sided floor and the suite would have stayed green. Closed with a window three times too wide (4 381 000 ms against a 657 000 record) that must refuse and write nothing, plus the honest walk through the same band. | `[cause: verify-gap]` `[[a-band-tested-on-one-side]]` |

| **Dv516** | **A worktree verification failed on a partially-tracked directory, and the first diagnosis was too broad.** A `git worktree` starts without `data/*` (gitignored), so collection errors immediately; the repair — `for item in $(ls data); do [ -e "$W/data/$item" ] \|\| cp -R …; done` — then left **48 failed, 6 errors**, and the first write-up charged that to the worktree method. Measured instead of assumed: `data/annotation` is **252 MB of the 313 MB**, it is PARTIALLY tracked (two `.jsonl` files are un-ignored), so the guard `[ -e ]` saw it present and skipped 250 MB of media. The method is fine; the copy was not. The control still stands and is what proved the failures were not the commit — the SAME 12 fail at HEAD in that worktree while HEAD in the real tree is 2 927 green — and the commit was verified by checking it out in the real repo on a clean tree. **A `[ -e ] \|\| copy` guard is wrong for any directory git tracks part of.** | `[cause: env]` `[[a-commit-must-run-its-own-suite]]` |

| **Dv517** | **A step's close has ONE reading, and on an old ledger the second one is negative.** The live ledger's close takes `max(balance_delta, billing_since)`; a STEP's takes `own_resources(billing_by_kind)` alone — deliberately, because the delta includes the always-on volume and the headline must not. The consequence only shows on an old close: `srv2b` and `srv2d` recorded `balance_delta_usd` of **−$4.193957** and **−$5.341297**, because the account has been topped up twice since 2026-08-08. So Dv411's «a step takes both readings and the pessimistic one binds» is structurally unavailable at close time, the settled figure rests on the billing walk alone, and the delta sits in the entry as provenance a reader must not add up. Pre-existing, not introduced here, and named because three records now carry it. | `[cause: spec-gap]` `[[a-balance-delta-is-not-a-per-leg-cost]]` |

**Split tally (H7).** Contract health — `contract-gap` 3 · `spec-gap` 2 · `verify-gap` 6 = **11**.
Paid-lesson findings — `tooling` 3 · `process` 3 · `env` 1 = **7**. Total 18, and every one of them
cost $0 to find. Enum v2 canonicity: **18 of 18**, zero empty, zero off-enum.

---

## Process signals

1. **The refusal gate is the deliverable.** H6 asked for one re-derivation and it falsified the
   constant that would have driven every irreversible write in the contract. The cheap version of
   this contract closes 3 ledgers and never learns that its tolerance was measuring a window bug.
2. **The dogfood found the thing the dogfood is for.** The preflight's first output said the guard
   was pinned and already stale — which is why the change went out as a MOVED manoeuvre and not as a
   re-pin, and why `MOVED_BORROWS` grew a name that no test could have demanded.
3. **The seam moved one layer down, twice.** 968 lines of guard tests patch `billing_by_kind`; a
   flag whose whole content is an argv is invisible to every one of them, so the new block patches
   `runpodctl` and asserts the argument list. And a flag that becomes REQUIRED is invisible to tests
   that build their argv by hand — which is how the module's own docstring example broke green
   (Dv514). Both seams now have a test; neither had one this morning.
4. **A sandbox made D3 measurable at zero risk.** Copying the guard under a scratch `REPO_ROOT`
   redirected `LEDGER`, `CYCLE2_LEDGER` and every step ledger at once, so all 24 close commands ran
   against real data and real billing with nothing writable in reach. The hash control is the proof,
   not the intention.
5. **Two of the four blockers are shaped like the next contract.** Every one of the 22 ledgers is
   missing an `anchored_at` or has one that does not match its step name; until a window start is a
   recorded fact rather than a session timestamp, no tolerance can be honest. That, and not a bigger
   number, is what would let this batch close.
