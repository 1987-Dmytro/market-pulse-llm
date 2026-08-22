# pass2-signals — the assembly pass over the bought window

`docs/PROMPT-pass2-signals.md`, executed. D0 at $0 → D1 paid (the smoke first, then rung S′'s
go/no-go, then the remaining 74; cap $1.50) → D2 at $0.

## Read back — one line each

- **The population and who derives it.** The 79 threads of window 1 carrying at least one comment
  pass 1 labelled `категория_личное` / `молочный_бренд` / `сеть_ритейлер` — 281 rows, 32 756 chars —
  derived by CALLING `census_pass1_window.pass_2_filter` over the union of
  `results/pass1_window_v2.jsonl` (131) and `results/pass1_window_r2_v2.jsonl` (901) against
  `results/pass1_window_pack.json`, keyed on the PAIR `(thread, msg_id)`; the 48 callable threads
  with no filtered row are «no signal by construction» and are not called.
- **What pass 2 may and may not do to a pass-1 label.** It may DROP the comment into `noise` and it
  may record `subject_doubt` with a reason; it may not change the label, in `per_comment` or in a
  signal's `subject_type`, and a reply that does is a parse REFUSAL counted by its own cause.
- **The four output lists and the one new field.** `signals` · `entities` (the bought block, passed
  through, never re-resolved) · `per_comment` (pass 1's labels, repeated) · `noise` (the DROPs); plus
  report-only `subject_doubt: true/false` with a one-line reason, which changes nothing downstream.
- **Which bars are registered and which is NOT.** Registered: bar 1 flagships 5/5, bar 2 entity
  cases 4/4 (inherited), bar 3 zero signals from the N threads pass 2 calls, and rung 7's
  completeness. NOT registered: the per-comment agreement on the fourteen — it would be their SIXTH
  look through a threshold, and `per_comment` is pass 1's own pass-through.
- **The expectation on F2 and why the bar still stands.** Pass 1 labelled msg 580124 `сеть_ритейлер`
  and the gold's F2a is a `молочный_бренд` signal read from it, so the only reply that could take F2
  is one strict authority refuses; the bar stays at 5 of 5 because a bar lowered to what the layer
  can reach measures nothing, and the RED is registered in advance as the measurement it is.
- **The smoke, rung S′'s formula, the hard stop.** The five F threads at an assumed 120 s/call =
  600 s, all-in worst case 3 000 s = $0.6667; then `charged_full = max(1.5 × smoke_mean, smoke_max)`
  and `projected = cumulative_billed_now + 74 × charged_full + 1 300` against a cumulative hard stop
  of 6 600 s = $1.4667 under a $1.50 cap — GO or STOP.
- **What a death after the first reply means.** The session closes. One re-creation is allowed only
  for a death at rungs 1–3 (price, ssh, boot); after the first reply the replies on the Mac are the
  evidence and the remainder is a new registration, never a third pod.
- **Which file is never edited and where the prompt lives.** `src/market_pulse/prompts.py` — pinned
  by 38 sealed records — and `src/market_pulse/scorer.py`, the single judge of all numbers. The
  pass-2 text and renderer live in the new `src/market_pulse/pass2.py`, task `pass2_thread_gm4_v1`.

## Step 0 — baselines and the team lead's files

```
## Baselines — instrument output, 2026-08-22T06:45:21+00:00
- head: 70db5e302c2c on main
- census: brain-census: 10.3Ktok boot tax
- suite: 3424 passed / 2 skipped — whole suite, stamped 2026-08-22T06:31:58+00:00 at 70db5e302c2c
- preflight: 1526 pinned paths · 2659 pins · 119 records — 1490 match every pin on them, 36 carry an older pin
```

Committed first, by path, verbatim and unedited: `docs/STATUS.md`, `docs/PROMPT-pass2-signals.md`
and the vault tail (`knowledge/index.md`, the Stop hook's auto line in the 21.08 log) as
`dfded5e`. Last session's `/save` checkpoint — `knowledge/hot.md` and
`knowledge/daily_logs/2026-08-22.md`, mine, left uncommitted by the skill's own rule — followed as
`e1d8081` on the operator's word.

## D0 — at $0, before any pod

*(filled in below as each piece landed; every commit precedes the first `pod create`)*

### The module — `src/market_pulse/pass2.py`

A NEW module because `prompts.py` is pinned by 38 sealed records. What it imports from there rather
than restating: the subject taxonomy, the signal words, the noise classes, the six aspects, the
input ceiling, and **both halves of the reader parser** — `prompts._reader_object` for the container
repairs the 2026-08-16 sitting ruled, then `prompts._reader` for the domains. That pair is exactly
what `prompts.parse_reply` binds for `task in prompts.READER`; `parse_reply` itself cannot be used,
because it dispatches on a task name and `pass2_thread_gm4_v1` is not in `prompts.READER` — adding
it would edit the pinned file.

**Strict authority is code, not prose.** `parse_pass2` refuses four things by cause:

| refusal | why it exists |
|---|---|
| a `subject_type` that is not the pass-1 label of the row it names — `RelabelError` | the ADR's line |
| an id that was not in the request, in `per_comment`, `noise` or a signal's `evidence` | `scorer.reader_signal_found` matches a gold signal on its EVIDENCE, so an invented id is the one field that can make a bar answer by accident |
| a signal citing NO comment (`from_post`, which the prompt does not offer) | strict authority keys on the label of a CITED row; a signal citing none carries a subject nothing authorises |
| a reply about another thread | a verdict scored against another thread's gold |

A signal citing two rows may take the label of **either** — one and not all, because pass 1 labelled
each comment on its own and demanding both would refuse F1(б)'s two-row shape for a reason no ruling
gave.

**What is COUNTED and not refused:** a comment in both lists (the reader's own parser calls that a
bookkeeping slip whose two rows are each readable, and this file does not overrule it) and a comment
in neither. Refusing a whole thread's signals over an incomplete list would trade the measurement
for the bookkeeping.

### The pack — `results/pass2_pack.json`

```
79 units · 281 filtered rows · 32756 chars · 48 callable threads with no signal by construction
smoke leg: @VARUS_channel:10613 · @matusi_ukr:22303 · @mandziak:3676 · @mandziak:3703 · @matusi_ukr:22272
length: widest 11397 chars (@mandziak:3679) · median 6253 · headroom 603 of 12000
membership: F 5 in, 0 out · E 4 in, 1 out · N 2 in, 4 out
contamination: labels_outside_the_filter [] · comments_edited_against_the_store []
                renderings_that_move_without_the_membership_flags [] · requests_naming_a_case_id []
```

The filter is the AUTHORITY and the builder's selection is the thing being checked: the units are
held to `pass_2_filter`'s table thread by thread and count by count, and a disagreement refuses. The
census's own function is CALLED over a scratch union view — never a merge on disk — rather than its
published output being read, so the pack and the census cannot drift.

**The input ceiling has 603 characters of headroom, 5.0 %.** The 12 000 the contract names is pass
1's constant, derived for a request whose prompt is ~2 300 characters; pass 2's prompt is 5 021, so
the same ceiling is doing far less work here than it did there. It holds, and the margin is thin
enough to be worth a line in a report.

### The pre-registration — `results/prereg_pass2_signals.json`

```
H6: 41 rows, every registered number re-derives
smoke 5 × 120 s = 600 s · worst 3000 s = $0.6667
rung S′ knife edge 48.6486 s/call · a GO needs mean ≤ 32.4324 AND max ≤ 48.6486
hard stop 6600 s = $1.4667 of $1.50 · widest dead pod 3600 s
bar 2 at $0: 3 of 4 · unreachable ['E1'] · unreachable flagship signals ['F2a']
```

**Three numbers this registration knows before the pod, and each is registered rather than
discovered.**

1. **Bar 2 is 3 of 4 — RED — and it was computable at $0.** `entities` is the bought v5b/v4/topup
   block, passed through and never re-resolved, so the bar the reader's scorer computes over it is
   decided by the pack and the watchlist matcher and not by the model. E2, E3 and E4 are held; E1's
   thread (`@matusi_ukr:22242`) carries no filtered row, so pass 2 never calls it.
2. **F2a is unreachable.** Pass 1 labelled msg 580124 `сеть_ритейлер`; the gold's F2a is a
   `молочный_бренд` signal read from it. The only reply that could take F2 is one strict authority
   refuses. Registered as an expectation; the bar stays at 5 of 5.
3. **Reachability is a property of the POPULATION, and pass 2's is not the reader probe's — in both
   directions.** E1 falls out; E4a/E4b (`@mandziak:3684/3689`), which the reader's own gate silenced
   before payment, come in.

**And one the registration had to derive rather than carry.** The completeness bar's refusal
fraction was pass 1's 1 %, and `int(0.01 × 79)` is **zero** — a transport bar allowing no refusal at
all, on both arms, against a four-list schema whose only measured rate is v5b's **4 of 23 = 0.174**.
It is measured now: `ceil(0.174 × 79) = 14` on the GO arm, `ceil(0.174 × 5) = 1` on the STOP arm.
Relabellings sit OUTSIDE that budget — a reply that rewrote a subject is readable, and it is the
ADR's line arriving as a measurement, not a transport failure.

**The rate this run has to find out.** The nearest measured shape is the reader's, and on v5b's pod
the five smoke threads took **376.9 s — mean 75.4, max 108.4** against a population mean of 45.0.
The smoke is not a sample: it carries **6.0 filtered rows a thread against the population's 3.56**,
and rung S′ charges the remaining 74 at the weight of the heaviest five. On v5b's own numbers a
least-squares fit of seconds on rows over those five predicts the 74 at **3 998 s** while the
registered flat arms would charge **8 019–8 366 s** — a factor of two. A pass-2 reply is smaller
than a reader's (no `entities`, only the filtered rows in `per_comment`) and how much smaller is
exactly what the smoke is bought to find out. **A STOP is a likely and registered outcome**, the
row-weighted arm is computed at the go/no-go and published beside the verdict, and it gates nothing.

### The five-lens review — 13 distinct defects, two of them fatal

Five lenses (money · strict authority · population · bars · transport), each finding handed to an
independent skeptic. **15 filings, 13 distinct defects, and every one of them real.** Three more came
out of my own re-reading — two before the review, one after.

| # | found by | what it was |
|---|---|---|
| 1 | transport, money | **`--watch`, `--projection`, `--completeness` and `--close` all died on `KeyError: 'payable_comments'`** — `gate_pass1_window.main` hard-subscripts that key in both the pack and the record, and that file is pinned by a sealed record and cannot be renamed. It would have landed on `--watch`, on a pod already billing, with nothing watching it |
| 2 | money | **Rungs 2 and 3 had no enforcement at all** — rebinding `rung` reaches `watch` (defined in `gate_pass1_window`) and not `gate_zero`/`gate_boot` (defined in `gate_pass1_fewshot`); `--gate0` raised `ValueError: could not convert string to float: '.'` |
| 3 | money | **The recovery clause was in the record and in no instrument** — the shipped `pre_create` counts pods, seconds and dollars, and after a rung-4 KILL the seconds still fit |
| 4 | transport | **A half-copied go token read as a STOP** — scp truncates the destination at the start of the transfer, and one unlucky poll would have thrown away 74 units the guard had just authorised |
| 5 | transport, money | **A second `--go-no-go` recorded before anything stopped it**, and `go_recorded` reads the LAST verdict — a second STOP would de-authorise a run that was still generating |
| 6 | authority | **A REFUSED reply was scored as an unread thread** — a relabelling on N2 deleted bar 3 instead of failing it, and gave «the go/no-go stopped the run before the population was bought» as the reason for a unit the pod had answered |
| 7 | authority | **`subject_doubt` — report-only by contract — could refuse a whole thread**: `prompts._flag` raises on `0`, on `null` and on a Ukrainian yes |
| 8 | authority | **The request itself invited a RelabelError on F2** — the entity block rendered pass 1's four-word taxonomy above comments carrying one of three, so a SMOKE thread showed `Ласунка → молочный_бренд` over the only comment naming Ласунка, which pass 1 labelled `категория_личное` |
| 9 | bars | **The prompt shipped the pre-v3 signal text** — `READER_ASPECT_V5` and `READER_NOT_A_SIGNAL_V3` are F1(б) and F1(в) in as many words, F1 is all-or-nothing, and its three signals are the only gold signals that state an aspect |
| 10 | bars | **«parse refusals ≤ 1 % of N» printed in two places beside an enforced 14 of 79** |
| 11 | bars | **«категория» was refused as the ADR's cardinal violation** — a synonym `READER_SUBJECT_TYPES` carries and `score_reader_probe_b.COLLAPSE` folds, on three of the five flagship cases |
| 12 | population | **A null `subject_type` was called a relabelling** — an omission reported as an architecture breach, and exempt from the transport budget, so unbounded |
| 13 | population | **The record carried two values for one input** — F5a published `{"579457": null}` two blocks from prose naming that row `не_наш_рынок` |
| 14 | mine, before | **The completeness bar allowed ZERO refusals** — `int(0.01 × 79)` is 0, against a schema measured at 17.4 % |
| 15 | mine, before | **Under a STOP, bar 3 read GREEN over zero threads and bar 2 RED at 0 of 4** — `reader_noise_count({})` returns `signals: 0` |
| 16 | mine, after | **The knife edge omitted the go wait it is billed for** — the third instance of #13's class inside this one registration |

**Defects 1 and 2 were fatal and both live in the COMMANDS.** Every test written before the review
drove the FUNCTIONS behind them — `watch(...)`, `completeness(...)` — and walked straight past the
line that crashes. `test_EVERY_gate_command_runs_end_to_end` now drives all six, and the Dv669
by-key property is proven by driving rungs 2, 3 and 5 on a poisoned record rather than by calling
`rung` directly.

**Defect 8 is the one worth reading twice:** it was not in an instrument, it was in the REQUEST, on
the thread whose expected-RED the registration had already written down.

**One honest note about the review's own numbers.** Its skeptic stage reports 3 confirmed and 12
refuted, and that split is not a judgement of the findings: I was fixing the tree while the skeptics
read it, so twelve of them refute with «already fixed at HEAD» and name the commit that fixed it.
Every finding was verified by me first — driven, not reasoned — before anything was changed. If this
shape is run again, the finders and the verifiers should read a frozen tree.

## Deviations from Dv680

Each with its cause tag. Everything below was decided at $0, before the create.

| # | cause | what |
|---|---|---|
| **Dv681** | `contract-description-vs-source` | **A sibling runner, said before it was written.** The contract calls `reader_v5_pod_runner.py` duck-typed on `prompts`; its module-level `render`/`check_requests` are, and `run()` is not — it does `from market_pulse import prompts` itself, and the `Client` its `load_reader` builds imports the same module inside `render`. A prompt living in `market_pulse.pass2` is unreachable without replacing the module-level `render`, which is exactly the swap `pass1_pod_runner.py` already makes. |
| **Dv682** | `pinned-file` | **`prompts._reader_object` then `prompts._reader`, named.** The contract asked which of `_reader_object` / `parse_reply`; `parse_reply` dispatches on a task name and `pass2_thread_gm4_v1` is not in `prompts.READER`, so using it would mean editing the file 38 sealed records pin. The two private halves ARE the pair `parse_reply` binds. |
| **Dv683** | `smoke-cost-and-refusal-risk` | **`entities` is injected, not echoed.** The block is 1 288 chars on F1 and 653 on F2 — two of the five threads whose seconds rung S′ multiplies by 74 — and a verbatim-copy slip would refuse the thread and take bar 1's hardest case with it. Consequence registered: bar 2's value is knowable at $0. |
| **Dv684** | `pinned-parser-domain` | **«не_сигнал» is not offered as a noise class.** `prompts._reader` domain-checks `noise.class` against the three ratified words; a fourth would refuse the whole thread. «оффтоп» is the ratified word for a comment that is not a signal. |
| **Dv685** | `strict-authority-hole` | **`from_post` is refused and not offered.** Strict authority keys on the pass-1 label of a CITED row, so a signal citing none carries a subject nothing authorises. |
| **Dv686** | `unit-error-in-the-contract` | **The reader's output ceiling is 4 000 TOKENS, not characters.** `reader_v5b_pack.json::serving.output_tokens` and the v5b verdict's `max_new_tokens: 4000` with `finish_reason_length: 0` over 23 threads. |
| **Dv687** | `stricter-arm-published` | **Rung S′ projects on `cumulative_billed_seconds`, not `create_elapsed_now`.** Equal when no pod died, stricter when one did; both arms printed. |
| **Dv688** | `pinned-call-sites` | **Deadlines by key, without copying three pinned functions.** `by_key()` prefixes every clock rung's rule with its own `deadline_seconds`, and `gate_zero` / `gate_boot` / `watch` are each handed the transformed record — because rebinding `rung` reaches only the one of the three defined in `gate_pass1_window`. |
| **Dv689** | `registration-authorises-the-smoke` | **`legs_of` and `leg_state` rebound to the AUTHORISED leg.** Rung 4 pricing 79 units at 120 s/call would kill the pod at the first poll. |
| **Dv690** | `unpriceable-run` | **`money.arithmetic.total_seconds` is the SMOKE's worst case, not the run's** — which is what rung 0 authorises a create against. |
| **Dv691** | `a-bar-no-reading-reaches` | **The completeness bar's refusal fraction is MEASURED.** `int(0.01 × 79)` is zero; the schema's only measured rate is v5b's 4 of 23 = 0.174, so `ceil(0.174 × N)` — 14 and 1. |
| **Dv692** | `finding-not-defect` | **Relabellings sit outside the transport budget** and are counted by cause. Rung 7 is transport; whether the answers are right is bars 1/2/3. |
| **Dv693** | `false-green-under-a-STOP` | **Every bar goes through `bar_state` before it reports a number.** `reader_noise_count({})` returns `signals: 0`, so bar 3 would have read GREEN over zero threads and bar 2 RED at 0 of 4. |
| **Dv694** | `smoke-leg-membership` | **Bar 3 is UNSCORED under a STOP, registered in advance.** N2 is not one of the five F threads, so the contract's «bars 1/3 on the five» reaches bar 1 and not bar 3. |
| **Dv695** | `the-smoke-is-not-a-sample` | **The row-weighted reading is computed at the go/no-go** and gates nothing. The smoke carries 6.0 filtered rows a thread against the population's 3.56. |
| **Dv696** | `one-out-file` | **The smoke is a PREFIX of one leg with one out-file**, not a second leg or a second pack — which is what lets the shipped resume-skip take the remaining 74 into the same file. |
| **Dv697** | `pre-generation-charged-once` | **The go is a WAIT inside the runner**, with the loader shared between the two `run()` calls. The registered 48.6 s/call arm only closes if the model is loaded once. |
| **Dv698** | `pinned-guard-subscripts` | **The pack and the record carry `payable_comments` under pass 1's word.** A pass-2 unit is a THREAD; the key is what `gate_pass1_window.main` compares, and that file cannot be renamed. |
| **Dv699** | `an-omission-is-not-a-rewrite` | **A null `subject_type` in `per_comment` is counted, not refused** as the ADR's cardinal violation. |
| **Dv700** | `two-authorities-one-word` | **«категория» is a synonym, not a relabelling** — compared through `SUBJECT_SYNONYMS`, asserted equal to `score_reader_probe_b.COLLAPSE`. |
| **Dv701** | `paid-for-clauses` | **`READER_ASPECT_V5` and `READER_NOT_A_SIGNAL_V3` are spliced into the pass-2 text** from `prompts`, not retyped. They are F1(б) and F1(в) in as many words, and F1 is all-or-nothing. |

## Process signals

1. **Every test I wrote before the review drove the FUNCTIONS, and the two fatal defects lived in
   the COMMANDS.** `watch(...)` and `completeness(...)` were driven directly, so both walked past
   `gate_pass1_window.main`'s pack check — which crashes — and past the `gate_zero`/`gate_boot` call
   sites, whose `rung` resolves in a module my rebinding never touched. A guard is only proven by
   the entry point an operator types ([[a_proof_can_cover_the_sibling_branch]],
   [[drive_the_consumer_not_only_the_producer]]).
2. **A rule written into a record and enforced nowhere goes green.** «One re-creation, ONLY for a
   death before the smoke's first reply» was in `money.recovery`, in the runbook, in the ADR and in
   no instrument — and after a rung-4 KILL the seconds still fit, so the shipped arithmetic would
   have reported GO on a create the record forbids. Every clause a record states about WHEN
   something may happen needs a reading of the world, not a sentence.
3. **Two values for one input, twice more in one registration.** «parse refusals ≤ 1 % of N» in two
   prose places beside an enforced 14 of 79; `null` for a gold evidence row's pass-1 label two
   blocks from prose naming that same label; and the knife edge printed without the wait term that
   is billed against it. This is the class I documented on 21.08 and it has now appeared four times
   on this line ([[two_values_for_one_input_get_quoted_kindly]]). What catches it is an H6 row that
   parses the number back out of the prose that prints it.
4. **The defect that mattered most was not in an instrument — it was in the REQUEST.** The entity
   block rendered pass 1's four-word taxonomy above comments carrying one of three, so F2's own
   request offered `Ласунка → молочный_бренд` over the only comment naming Ласунка, which pass 1
   labelled `категория_личное`: the most natural signal in that thread was a refusal the request had
   set up, on the thread whose expected-RED the registration had already written down. And the
   prompt shipped the pre-v3 wording, un-learning the two clauses this line PAID for on F1(б) and
   F1(в) — the all-or-nothing case the smoke opens with.
5. **The registration could not price its own run, so it bought the measurement instead.** No pass-2
   decode has ever been measured on this stack; `total_seconds` is the SMOKE's worst case, rung 0
   authorises that and nothing more, and the remaining 74 are authorised by a rung with a recorded
   verdict. The honest half is the part that had to be published beside it: the smoke is not a
   sample — 6.0 filtered rows a thread against the population's 3.56, and v5b's two slowest threads
   are two of the five — so a STOP is a likely outcome of the SAMPLING and not only of the rate, and
   the row-weighted arm is computed at the go/no-go so the operator can tell the two apart.
