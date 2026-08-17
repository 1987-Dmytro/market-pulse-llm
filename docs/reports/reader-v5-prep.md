# reader-v5-prep — the sitting's rulings become an instrument, and the measurement that changed one of them

**Contract:** `docs/PROMPT-reader-v5-prep.md` · **baseline:** `make check` **2 685 passed / 2 skipped**
at `f19a9b4` (the team lead's figure, reproduced here) · **HEAD:** `647b47f` · **`make check` now:
2 777 passed / 2 skipped** · **spent: $0.00.**

**Outcome in one line.** The accepted phase's four debts are paid, prompt v5 is seven visible
`_swap` calls over v3 with every example proven synthetic against a 43.9-million-character corpus,
the transport stop / echo census / chunk merge are a module with 20 tests of its own (50 with the
driver's and the scorer's), and
`results/prereg_reader_probe_v5.json` (`48b6cbde119ec3b1…`) is committed before any pod exists with
**25 tests** holding its claims. **Nothing billable was created:** `pod list -a` `[]`,
`serverless list` `[]`, the volume unchanged as the positive control.

**And one thing the contract asked for turned out to rest on a misreading, which is the finding of
this contract.** reader-v4's report reads its 93 `per_comment` rows against 111 requested as «one
row in six is missing». It is not missing. 18 of those ids are answered in `noise` and 3 more are in
BOTH lists; over the parsed threads `per_comment ∪ noise` covers **111 of 111 with nothing absent
and nothing extra**. The echo duty is therefore written over the PAIR of lists — the only form of it
the instrument can obey — and the census counts three states instead of a ratio. **Dv460.**

---

## 0. Read back, one line each

**The seven pairs.** (1) ATTRIBUTION — the subject is read off THE COMMENT, and the swap test («would
this still stand if the chain or the trade mark were another one?») decides it, with three synthetic
examples, one per confusion pair bar 4 actually produced; (2) the aspect names what the text is
ABOUT, so a request for a kind of product is `availability` and never `taste`; (3) a question and the
channel's answer are ONE signal and its `evidence` carries BOTH msg_ids; (4) the F2a carve-out, NARROW
— an event changing the availability or status of the post's subject, opinions without a name still
never carried; (5) «категория» leaves the TEXT and `категория_личное` is the one word (the parser's
domain does not move); (6) the echo duty over `per_comment` ∪ `noise`, every id answered exactly
once; (7) «частина i з n» means this part's comments and this part's list.

**The stop-rule.** Pre-registered inside the record, not written after the numbers: if v5 COMPLETES
and bars 1 and 4 are not BOTH taken, the prompt-engineering line CLOSES and the next step is an
architecture sitting — never a v6 of the same kind.

**What leg B can and cannot touch.** It produces four MECHANICAL bars (every payable id exactly once
· every chunk `stop` · every chunk parses · no duplicate signal survives the merge) and bar 5. It
carries no gold, is not in the reference, has its OWN digest, and no row of it enters a bar of leg A,
leg A's completeness census, or a production aggregate. Driven, not asserted: scoring leg B perfectly
and scoring it not at all give byte-identical leg-A bars.

**The byte-preservation proof.** `prompts.py` moved (`dfa7a79f…` → `be5a8164…`) and reader-v4's **23
of 23** registered request shas re-render byte-identically under task `reader_thread_gm4_v3`; the
default render path is unchanged by construction — `part` is a prefix that is the empty string.

**Why this contract spends $0.** It creates no pod, no serverless endpoint, no template and no
network volume. Its one guard write CLOSES a step that was already spent, which moves a settled
figure from a billing walk into a ledger and costs nothing to read.

---

## 1. Step 0 — the tail, and it is four vault files rather than three

`git status` before anything: `docs/STATUS.md` modified, four `knowledge/**` files, and this
contract untracked. **The contract's baseline names three vault files and the live tree carries
four** — `knowledge/hot.md` is modified too, because this session's SessionStart hook rewrote its
AUTO-GEN block. The list is built from `git status` and never from prose. **Dv456.**

- `974fe89` — `knowledge/**`, four files, staged by path.
- `8dc3309` — `docs/STATUS.md` and `docs/PROMPT-reader-v5-prep.md`, **verbatim**, in their own
  commit. Both are the team lead's. The Dv446 manoeuvre, third time in this family.

Never `git add -A`, never an edit to either.

## 2. Step 0.5 — the accepted phase's four debts

### 2.1 The step is CLOSED at $0.236118, and the verdict moves in exactly one place

```
$ python3.11 scripts/runpod_guard.py --step reader-v4 --step-cap 0.35 --close --note "reader-v4 settled"
CLOSED spend_reader_v4.json at $0.2361 — entry APPENDED
READER-V4 CLOSED     $0.2361 of $0.35  (settled at 2026-08-17T10:17:10+00:00, window from 2026-08-16T17:49:04+00:00)
  pods            $0.2361
  network-volume  $0.1556   <- always on, beside the run and never inside it
  serverless      $0.0000
[exit 0]
```

The walk had posted, so what was a LOWER BOUND of $0.2446 is a settled figure of **$0.236118** —
pods only, serverless $0.0000. The `$0.391674` the same walk reports is the always-on volume dripping
into an open window and belongs to no step.

**The close writes TWO ledgers and that is Dv447's fix working — Dv459.** The closing entry lands in
`results/spend_reader_v4.json` and the LIVE line's own witness of the same balance lands in
`results/spend_cycle2.json`, beside it, so a refusal afterwards cannot take the witness with it. The
contract's «the ONLY guard write» is one COMMAND; it is two files, and this is where that is said.

**A re-close is a NO-OP, not a refusal — Dv458.** The contract says «idempotent — a re-close is
refused, proven». What the guard actually does is find the closing entry, print it and append
nothing. Proven the only way that is worth anything, by running it twice:

```
$ python3.11 scripts/runpod_guard.py --step reader-v4 --step-cap 0.35 --close --note "reader-v4 settled"
READER-V4 CLOSED     $0.2361 of $0.35  (settled at 2026-08-17T10:17:10+00:00, …)      # no "entry APPENDED"
[exit 0]
$ cmp spend_reader_v4.AFTER_CLOSE.json results/spend_reader_v4.json  →  BYTE-IDENTICAL
$ cmp spend_cycle2.AFTER_CLOSE.json    results/spend_cycle2.json     →  BYTE-IDENTICAL
```

**The re-score, and the proof that bars 1–4 did not move.** `7f5c96c8352ad052…` → `79c6c796512434bd…`:

```
$ PYTHONPATH=src python3.11 scripts/score_reader_v4.py
  bar 1_flagships                SCORED — False (collapsed)
  bar 2_entity_cases             SCORED — True
  bar 3_noise                    SCORED — True
  bar 4_per_comment_agreement    SCORED — False (collapsed)
  bar 5_time_and_cost            CLOSED — passed True

$ # every top-level key of the two verdicts, compared
keys that differ: ['5_time_and_cost']
bars 1-4 byte-equal: True
```

| | before | after |
|---|---|---|
| `state` | OPEN | **CLOSED** |
| `lower_bound_usd` | 0.2446 | — |
| `settled_usd` | — | **0.236118** |
| `passed` | null | **true** |

**reader-v4 therefore closes at three bars of five.** Bars 2, 3 and 5 pass; 1 and 4 fail, and they
are what v5 exists for. → `b268862`

### 2.2 Two ADRs, every number read out of a ledger

- `knowledge/decisions/reader-v3-serverless-close-and-the-pod-ruling.md` — v3 settled **$0.393577**
  over its own $0.35 cap with **zero threads read**: serverless `$0.371765` (endpoint
  `77o1ing6cy0972`, `1 211 005 ms` that answered nothing), staging pod `$0.021812`, volume
  `$0.009722`. Every one of those figures is the closing entry of `results/spend_reader_v3.json`, not
  a sentence from a report. The defect is structural — the only gate sat downstream of a boot no
  branch could stop — and the operator's ruling is the pod, the stopwatch from `pod create` and a
  kill rule that is a command. Beside it, what the ruling was worth: the same instrument on the same
  23 threads settled at `$0.236118` for 23 of 23 read.
- `knowledge/decisions/reader-v4-closed-and-sitting-17-08.md` — v4 accepted as an honest negative
  (3 bars of 5), and the sitting's six rulings (a)–(f) recorded as given, including the PROGRAMME
  STOP-RULE and the synthetic-examples constraint.

**Cross-checked against `docs/STATUS.md`'s own Russian list before writing.** The contract's (a)–(f)
and STATUS's four rulings + stop-rule are the same content re-cut: STATUS's ruling 1 splits into the
contract's (a) and the echo half of (d); STATUS's ruling 4 splits into (d)'s chunking and (e)'s cap.
No divergence. Both INDEX rows added; `scripts/check-wikilinks.py` → `OK, none broken`. → `bbc9b35`

### 2.3 Runbook hygiene — the procedure edited, the record left alone

`scripts/runbook_reader_v4.md`: the **eight** verify commands now name `python3.11` explicitly, and a
dated block at the end carries both paid lessons — the detached launch that must not hold the ssh
channel (`nohup … </dev/null >log 2>&1 &`, verified separately by `pgrep -af`, never by the launch's
own exit) and the `python3.11` rule with the reason (the team lead's own scorer run failed on a
system `python3` that is 3.9).

**Scope, stated: no file under `docs/reports/` is touched — Dv464.** The contract says «every verify
command in runbooks/reports». A runbook is a PROCEDURE and is meant to be followed again; a report is
the record of what was run, and rewriting its transcript would be falsifying evidence. The runbook's
dated block says what changed and when, so the citation in `docs/reports/reader-v4.md` resolves to a
file that names its own correction. Runbooks of closed phases are left alone — churn with no reader.

---

## 3. D1 — prompt v5: seven pairs, and the one the evidence rewrote

`READER_THREAD_PROMPT_V5 = _swap(…)` × 7 over v3, registered as `reader_thread_gm4_v5`
(`c529d279321269e1…`, 9 779 chars against v3's 6 630). `_swap` refuses an `old` it cannot find
exactly once, which IS the audit; an eighth edit would have to appear as an eighth call.

**There is deliberately no v4 prompt** and the constant says so in one line: reader-v4 registered the
v3 TEXT on a pod, so the number follows the contract that registers a text and the gap 3 → 5 is the
honest name for that. `tests/test_prompts.py` asserts `"reader_thread_gm4_v4" not in prompts.PROMPTS`.

| pair | what it changes | the paid miss it answers |
|---|---|---|
| 1 | ATTRIBUTION block in duty (3), the swap test, three synthetic examples | bar 4's **four** disagreements — every one a `subject_type` on already-collapsed gold |
| 2 | the aspect names what the text is ABOUT | F1b's aspect half — `availability`, not `taste` |
| 3 | a question and its answer are one signal, BOTH msg_ids | F1b's evidence half — two of its three ids are the channel's |
| 4 | the narrow F2a carve-out, EVENTS only | F2a, missed; scoped so bar 3 (a PASS) is not put at risk |
| 5 | «категория» leaves the signals line | the seam gold r2 opened |
| 6 | the echo duty, over BOTH lists | the completeness census — **and see Dv460** |
| 7 | «частина i з n» semantics | leg B |

**Bar 4's four disagreements are three confusion pairs**, so the block carries three examples and not
four: 21601 and 48283 are a category read as the chain, 580124 a brand read as the chain, 580129 a
category read as a brand.

### 3.1 Dv460 — the echo duty's premise was wrong, measured before it was written

`[cause: measured-before-writing]`

The contract's pair 6 asks for «one row for EVERY id ON THAT LIST» in `per_comment`. Measured on
reader-v4's own 19 parsed threads, id by id:

| | rows |
|---|---:|
| requested | **111** |
| answered in `per_comment` | 93 |
| answered ONLY in `noise` | 18 |
| in BOTH lists | 3 |
| **absent** | **0** |
| extra (an id nobody sent) | 0 |

A duty demanding a `per_comment` row per id would REFUSE the answers v3's own outranking rule — «a
comment belongs to at most one of "per_comment" and "noise"» — obliges the model to give. So pair 6
is stated over the pair of lists, and `reader_v5.echo` counts the three states apart. Only `absent`
is a shortfall.

**What this changes about the diagnosis.** Four threads answered every id as noise: `@retsepty:7312`,
`:7325` and `:7327` are the registered NOISE threads N4–N6, where that is the CORRECT answer; only
`@matusi_ukr:22242` is a miss, and it is a classification miss of one whole thread, not eighteen
dropped rows. And the 3 ids in both lists are all in `@VARUS_channel:10366` — the outranking rule
broken on three comments, which the parser deliberately does not refuse.

**And it re-prices bar 4's reachability, which nobody had written down.** The bar is 14 gold rows: 7
agreed, 4 disagreed on `subject_type`, 3 absent. 0.80 of 14 needs **12**, so **v5 must win at least 5
of the 7 rows that are not already agreed**. The three absent ones have named paths: 47899 and 47902
are in `@mandziak:3676`, which REFUSED (`two disagreeing objects: quote`) — the TRANSPORT stop is
what recovers them, not the echo duty; 578951 is in `@matusi_ukr:22242`, recovered only if that
thread stops being called noise wholesale, which is the ATTRIBUTION block's job.

### 3.2 The contamination gate, with its negative control

Every example in pairs 1–4 is synthetic, and the check runs over everything the reader could ever
have been shown:

```
corpus: 129 files · 43,871,545 chars raw · 43,845,739 normalised
        (data/raw/comments, data/raw/comments_v2, data/raw/posts,
         data/derived/inferences, data/derived/post_texts,
         results/reader_gold_w1.json, results/reader_gold_w1_r2.json, docs/REFERENCE-signals-w1.md)

  raw=False norm=False  жирність у таких йогуртах давно вже не та
  raw=False norm=False  на касі простояла сорок хвилин із повним візком
  raw=False norm=False  сирки з родзинками ніхто вже не робить такі, як колись
  raw=False norm=False  а є у вас кефір без лактози?
  raw=False norm=False  партію відкликали, у продажу її більше немає
```

Both readings: the sentence as written, and whitespace-collapsed + case-folded through
`write_reader_gold.normalise`. **The negative control is the half that makes it a proof** — a phrase
taken out of the evidence store is FOUND by the same two comparisons, so «not found» cannot be the
matcher. And the list is held against the text both ways: a sixth example added to the prompt without
joining `SYNTHETIC` would fail `test_every_synthetic_example_is_declared_and_every_declared_one_is_used`.

### 3.3 The fan-out — 16 red tests in 8 files, every one named

`prompts.py` moved, so the MOVED-tuple manoeuvre runs for the third time in this family. It lives in
`tests/test_prompts.py` this time — the file whose subject is the file that moved — and the four
records that pin it import from there: gold r2, the v3 and v4 registrations, the dashboard export.
`SEALED_AT = "ace1a0d"`, the commit reader-v4's pod read under; witness token `reader_thread_gm4_v5`,
asserted absent from the sealed blob and present on disk.

**The swap COUNT is the caller's**, because how many times a record names one file is a fact about
that record: the v3 registration twice (`instruments.parser.sha256` and `producer.borrowed`), the
others once — v4 copies its whole `instruments` block out of the frozen v3 file instead of
re-deriving it. A hard-coded 1 would have quietly stopped repairing the second occurrence.

**One record needed a second repair.** `write_reader_prereg_v3.py` derives `instruments.prompt_sha256`
LIVE over `prompts.READER`, so a rebuild today gains a fourth entry. Its own `prompt_rule` says that
is expected — «a text registered LATER is not in this map and is not expected to be» — so the later
entry is dropped before the byte comparison and the drop must FIRE.

### 3.4 Dv457 — a guard that refused a pack nothing had touched

`[cause: code-and-record-parted]`

`reader_v4_pod_runner.check_instrument` compared the pod's WHOLE reader map against the
registration's. Registering a fourth text therefore refused the frozen v4 pack — untouched — before
the model loads, **and with the wrong sentence**: it blamed the prompt map, when what really parted
is the module. The v4 registration says the opposite in as many words:

> «a sha per reader text registered at the moment this record was written — three of them. A text
> registered LATER is not in this map and is not expected to be; the driver compares each of THESE
> against the worker…»

Narrowed to the tasks the PACK pins, with the module sha left as the whole-checkout witness. Nothing
is lost — a pod carrying a different set of texts carries different `prompts.py` bytes — and both
directions are tested: a later text does not refuse, a task the pack pins that the pod cannot serve
still does, and the SHIPPED `results/reader_v4_pack.json` still refuses on this checkout with «the
parser and the renderer have parted», which is the true reason.

→ `9fe6dd4`, prompt + fan-out in ONE commit, so no intermediate commit is red.

---

## 4. D2 — the transport, and one number the contract could not have known

### 4.1 The stop, the census and the merge — `src/market_pulse/reader_v5.py`

Nothing here parses. `prompts.parse_reply` is untouched; every function runs either before it (the
stop) or over what it returned (the census, the merge). Dv451's idiom, a generation later.

`balanced_prefix` counts brace depth OUTSIDE string literals with escapes handled, and its cases are
the ones the contract names: a brace inside a string, `\"` versus `\\`, a second object after the
first (CUT), a reply that never balances (`None`, left to the ceiling). **Its strongest control is
free:** all 23 replies reader-v4 paid for — every one that parses has a balanced prefix, and parsing
the prefix gives a verdict IDENTICAL to parsing the whole reply, with at least one really shortened.
The stop may only shorten an answer, never change it.

**What is proven and what is not.** `balanced_prefix` is proven on 23 paid replies, and the
PERSISTED bytes are correct whatever the stopping criterion does — the runner cuts the decoded text
with the same function. What is NOT proven on this machine is the SAVING: that generation really
ends early. `stop_at_balanced` needs `transformers` and a loaded model, so it carries
`# pragma: no cover` and its first firing is on the pod. Both failure modes are caught rather than
silent — a criterion that raises is loud, and one that never fires costs seconds the full-pass gate
re-checks after every unit — but the report says which is which rather than letting the test list
read as if the criterion were exercised.

`merge` verifies the partition rather than assuming it: an id in two chunks' `per_comment` is a
`MergeError`. `signals` dedupe on `(signal_type, subject_type, subject_id, aspect, stance)` with
`evidence` UNIONED — `evidence` is deliberately out of the key, because the same finding read in two
parts names different msg_ids in each and keying on it would be the merge failing to merge.

### 4.2 The render, and the proof the default did not move

`reader_messages_gm4` gains `part=(i, n)`, default `None`. The header is a PREFIX that is the empty
string unless a part is asked for, so there is no second construction and no branch a frozen record's
re-render can take by accident:

```
re-render of reader-v4's registered requests under task reader_thread_gm4_v3: 23 of 23 byte-identical
part=None is byte-identical to the default: True
header present under part=(2,3): True · absent by default: True
```

A part that is not a part (`(0,3)`, `(4,3)`, `(2,1)`) is REFUSED: a header saying «part 4 of 3» would
tell the model something untrue about the request it is in, and the model cannot see that it is
untrue.

### 4.3 Dv466 — `local_llm.py` is not edited, and that is a decision about pins

`[cause: keep-the-pins]`

The v5 runner needs two things `ReaderClient` does not do: the chunk header in `render`, and a
stopping criterion in `generate`. Both arrive through a subclass and a wrapped `model.generate`
inside `scripts/reader_v5_pod_runner.py`, so `ReaderClient.read` — the encode, the ONE `generate`
call, the usage counters and `finish_reason` — is inherited untouched and stays the single inference
path in this repo. Editing `local_llm.py` for a keyword argument would move a sha that
`results/prereg_reader_probe.json`, `…_v2.json` and `…_v3.json` all pin, and pull three more sealed
records into the MOVED manoeuvre.

**The ceiling comes from the PACK and is refused if absent**, driven by a test: a pack with no
`serving.output_tokens` raises «a ceiling registered and never passed is a ceiling nobody lifted»
naming `local_llm`'s 2 000 default it would otherwise have taken silently.

### 4.4 Gate records APPEND

`results/reader_v5_run.json` keeps `gates` as a LIST; every WAIT/GO/KILL snapshot is appended and
`latest` names the newest. Driven: four snapshots go in, four come out in order, none displaced.
reader-v4's record overwrote its own first GO snapshot and its arithmetic had to be re-checked by
hand afterwards — it agreed, which is luck and not a property.

### 4.5 The scorer

`scripts/score_reader_v5.py` CALLS `score_reader_probe_b` (bars 1/2/4, collapsed), `score_reader_v3`
(bar 3's predicate, the refusal/repair/ceiling censuses, bar 5's three ledger states) and
`score_reader_v4` (the collapse's registered scope) — every one of them called, none edited. What is
new is the three-state completeness census with the absent ids NAMED, and leg B's four mechanical
bars. Bars 1–4 are computed over LEG A rows only, and the uncollapsed reading is reported beside.

---

## 5. D3 — the registration, and the number it had to compute

`results/prereg_reader_probe_v5.json` — **`48b6cbde119ec3b1…`**, byte-identical rebuild,
`tests/test_reader_prereg_v5.py` holds its claims in **25** tests.

### 5.1 Leg A: the digest copied, the renderings re-derived

The population digest is `ccef35fa…` — **copied**, because it is over `channel:post_id\tflag\tpayable
msg_ids` and carries no rendering, which is exactly why it is the pin three runs rest on. The 23
per-thread `rendering_sha256` are **RE-DERIVED under v5 and all 23 differ from v4's**, because the
same thread shown a different instrument is a different request. Bars 1–4, gold r2, the symmetric
collapse and N1's exclusion with v2's cause are asserted **object-equal** to v4's, not restated.

The `instruments` block is **RE-DERIVED, the inverse of v4's rule.** v4 copied v3's whole block
because nothing about what is measured had moved; here the task, the prompt map, the parser's
behaviour and the ceiling all move, so a copy would be a claim that is false in four places. What is
copied is copied object-equal and listed in the record.

### 5.2 Dv461 — the output ceiling moves, 2 000 → 4 000, and it is computed rather than chosen

`[cause: bar-unreachable-as-registered]`

The contract registers leg B's chunks at ≤16 and its bar **m2 as «`finish_reason` stop on every
chunk»**. Under v4's registered 2 000-token ceiling that bar fails by arithmetic before the model is
asked. The evidence, from v4's own rows:

- v4's ceiling never fired (`finish_reason: length` on 0 of 23) — **and that is not the same as
  having room.** Its largest reply is **1 946 tokens on `@VARUS_channel:10613`, 97.3% of 2 000, at
  ten answered rows.**
- A least-squares fit over the **14** v4 threads that answered every id in `per_comment` and none in
  `noise` (a noise row is two fields, a `per_comment` row is six — mixing them prices the wrong
  shape): **completion = 383.9 + 90.83 × rows**, largest residual **+653.8**.

| unit | rows | central | pessimistic (fit + max residual) |
|---|---:|---:|---:|
| leg B chunk 1 and 2 | 16 | 1 837 | **2 491** |
| leg A `@matusi_ukr:22272` | 15 | 1 746 | 2 400 |
| leg B chunk 3 | 11 | 1 383 | 2 037 |

**7 of the run's 26 units are over 2 000 pessimistically**, both legs. The ceiling is set at **4 000**
— 1.61× the worst corner, a doubling rather than a number tuned to a fit — and it is **ONE ceiling
for both legs**, because two ceilings in one run would make leg A and leg B two instruments, which is
worse than either value. Raising it costs seconds only where the model would have run past the old
ceiling, and the transport stops a well-formed answer at its closing brace whatever the ceiling is.

### 5.3 The money, at the cap the operator ruled

```
cap $0.45 = 2 189.2 s · usable 2 129.2 s (after the 60 s delete margin)
reading projection 1 454.0 s = leg A 1 134.0 + leg B 320.0
affordability deadline 675.2 s of create-elapsed · pre-generation budget −44.8 s

  boot  180 s -> 1 910.2 s for reading (1.314x the projection) · fits · all-in $0.3439
  boot  300 s -> 1 790.2 s                (1.231x)             · fits · all-in $0.3686
  boot  480 s -> 1 610.2 s                (1.107x)             · fits · all-in $0.4056
  boot  600 s -> 1 490.2 s                (1.025x)             · fits · all-in $0.4302
  boot  720 s -> 1 370.2 s                (0.942x)             · DOES NOT FIT · $0.4549
```

Leg A's projection is the pessimistic of two: v4's own measured floor (23 × 39.461 = **907.6 s**,
the contract's registered floor) scaled by the output growth the token model predicts (1.127×), and
the projected tokens at the **slowest per-thread rate v4 measured** (18.52 tok/s). probe-b's
31.6376 s a thread is explicitly no longer the floor and the record says why. Leg B is the
pessimistic of the contract's own rule (137.83 tokens a requested row × 43) and the row model, at
the same slow rate; per-chunk prefill is priced at **zero and that is measured, not assumed** — a fit
of v4's seconds on its completion tokens has an intercept of −0.39 s, inside the noise.

**Dv462 — the boot table cannot be worked at the pre-generation BUDGET, because it is negative.**
`usable − 720 − projection = −44.8 s`, which is a legal state and says something specific: the
affordability deadline (675.2 s) binds before the twelve-minute ceiling, always, on this
registration. The table is worked at reader-v4's **measured** pre-generation leg instead (39.0 s,
`pod create` 18:00:12Z → the generation process's first line 18:00:51Z) — the only measurement of
that leg this stack has. A budget is not an elapsed and the record says so where it is published.

**Dv463 — two denominators, and the first draft mixed them.** `tokens_per_requested_row` must be
completion tokens over the **PARSED** threads (15 299 / 111 = **137.83**, v4's own published figure),
not over every billed thread (18 637 / 111 = 167.9). The seconds-per-token rate uses every billed
thread, because a refused reply still cost its seconds. Mixed, they over-price leg B by 22% and
nothing downstream can see it.

**The card's price is READ ON THE DAY.** `$0.74/h` appears throughout as a WORKED EXAMPLE and is
labelled as one in the record; Dv448 is quoted as the reason. `costPerHr` from the create response is
the meter of record and re-prices every figure before the generation process starts.

### 5.4 Leg B, and what it is really buying

`@klopotenkofood:6040`, enumerated out of the reader census cell (`caa17216…`) and never typed: 43
payable ids, chunked 16/16/11, own digest `0ea101d7d26cb18c…`. Each part's request re-renders to its
pinned sha with exactly one `<part>` line, and every id of a part is in that request and no id of
another part is.

**Registered where a reader will look: this thread does NOT need chunking.** Whole, it renders to
14 128 characters against a 40 000 ceiling. The MECHANISM is what is being bought, before the
window's 125 / 108 / 105-comment threads are sent through it. A registration that let the three parts
read as a necessity would teach the next contract the wrong lesson.

---

## 6. Verify

```
$ make check
2777 passed, 2 skipped in 367.20s                 # baseline 2685 passed, 2 skipped at f19a9b4
$ ruff check .        → All checks passed!
$ ruff format --check .  → 332 files already formatted

$ python3.11 scripts/runpod_guard.py --step reader-v4 --step-cap 0.35
READER-V4 CLOSED     $0.2361 of $0.35  (settled at 2026-08-17T10:17:10+00:00, window from 2026-08-16T17:49:04+00:00)
  pods            $0.2361
  network-volume  $0.1556   <- always on, beside the run and never inside it
  serverless      $0.0000
CYCLE 2 SPENT     $0.8533 of $20.00
REMAINING         $19.1467

$ shasum -a 256 results/reader_v4_verdict.json
79c6c796512434bda613d93979764aaf80ec116315a0aacb72fcb331514ce4d8      # was 7f5c96c8352ad052…
  keys that differ against the accepted verdict: ['5_time_and_cost']
  bars 1-4 byte-equal: True

$ shasum -a 256 results/prereg_reader_probe_v5.json
48b6cbde119ec3b1f3f8ea6101b73b1d675a739031de8de748bbda204140c78a
$ PYTHONPATH=src python3.11 scripts/write_reader_prereg_v5.py --out $SCRATCH/v5_rebuild.json >/dev/null \
    && cmp results/prereg_reader_probe_v5.json $SCRATCH/v5_rebuild.json && echo "byte-identical rebuild: OK"
byte-identical rebuild: OK

$ PYTHONPATH=src python3.11 scripts/read_threads_reader_v5.py --pack $SCRATCH/v5_pack.json
pack … · 26 units, every sha matches the record
  leg A 23 threads · leg B 3 chunks
  task reader_thread_gm4_v5 · parser be5a81641afc2aa5… · ceiling 4000 output tokens

$ # the seam's law: reader-v4's registered requests after the prompts.py edit
23 of 23 registered requests re-render byte-identically under task reader_thread_gm4_v3
prompts.py sha: be5a81641afc2aa5 (was dfa7a79f39ed7d62…)

$ python3.11 -m pytest tests/test_reader_prompt_v5.py -k "corpus or synthetic or declared"
3 passed
corpus: 129 files · 43,871,545 chars raw · 43,845,739 normalised — 0 of 5 examples found, control FOUND

$ runpodctl pod list -a && runpodctl serverless list && runpodctl network-volume list
[]  ·  []  ·  [ { "dataCenterId": "EU-RO-1", "id": "qw4nwleanc", "name": "mp-srv2", "size": 100 } ]
```

### 6.1 The runner's stop tests and the parser's merge/echo tests, by name

```
test_reader_v5.py::test_the_prefix_ends_at_the_first_balanced_object                          PASSED
test_reader_v5.py::test_a_brace_inside_a_string_does_not_count                                PASSED
test_reader_v5.py::test_an_escaped_quote_does_not_end_the_string_and_an_escaped_backslash_does PASSED
test_reader_v5.py::test_a_second_object_after_the_first_is_CUT_and_that_is_the_whole_ruling   PASSED
test_reader_v5.py::test_a_reply_that_never_balances_returns_None_and_is_left_to_the_ceiling   PASSED
test_reader_v5.py::test_noise_BEFORE_the_first_brace_is_kept_because_the_prefix_is_what_was_emitted PASSED
test_reader_v5.py::test_the_scanner_agrees_with_the_parser_on_every_reply_reader_v4_actually_got PASSED
test_reader_v5.py::test_the_census_counts_three_states_and_only_absent_is_a_shortfall         PASSED
test_reader_v5.py::test_reader_v4s_own_replies_come_back_111_of_111_which_is_why_the_duty_names_both_lists PASSED
test_reader_v5.py::test_an_id_answered_twice_and_an_id_nobody_asked_for_are_different_defects PASSED
test_reader_v5.py::test_the_chunks_partition_the_comment_list                                 PASSED
test_reader_v5.py::test_a_msg_id_in_two_chunks_is_a_MergeError_and_never_a_row_kept_twice     PASSED
test_reader_v5.py::test_one_signal_read_in_two_chunks_becomes_one_with_its_evidence_UNIONED   PASSED
test_read_threads_reader_v5.py::test_the_runner_answers_every_unit_and_persists_the_BALANCED_PREFIX PASSED
test_read_threads_reader_v5.py::test_a_reply_that_never_balances_is_persisted_WHOLE_and_flagged PASSED
test_read_threads_reader_v5.py::test_a_chunked_item_renders_its_header_on_the_pod_too         PASSED
test_read_threads_reader_v5.py::test_the_pod_runner_refuses_a_pack_that_carries_no_output_ceiling PASSED
test_read_threads_reader_v5.py::test_every_gate_snapshot_is_APPENDED_and_none_is_overwritten  PASSED
test_read_threads_reader_v5.py::test_the_ingest_merges_leg_bs_chunks_into_one_row_and_keeps_the_parts PASSED
test_read_threads_reader_v5.py::test_leg_bs_rows_cannot_reach_a_leg_a_bar                     PASSED
(50 in the two files, all passing)
```

### 6.2 The per-commit rule — every commit of this contract is green

Checked out one at a time in a throwaway worktree with the gitignored store linked in, over the 13
test files this contract touches or that pin what it moved
(`test_export_dashboard_data.py` is excluded: it builds a SQLite database a worktree has no inputs
for):

```
f19a9b4  the baseline, before this contract      9 files  287 passed
974fe89  vault(tail)                             9 files  287 passed
8dc3309  docs(team-lead)                         9 files  287 passed
b268862  close(reader-v4)                        9 files  287 passed
bbc9b35  adr(reader)                             9 files  287 passed
9fe6dd4  prompt(reader v5)                      10 files  304 passed
3a9d6c7  transport(reader v5)                   11 files  324 passed
7727a24  prereg(reader v5)                      13 files  376 passed
64b36a2  docs(report)                           13 files  376 passed
647b47f  fix(reader v5)                         13 files  379 passed
```

**No red commit.** reader-v4 carried three; this contract carries none, because the prompt edit and
its whole fan-out went in as one commit and the registration went in with the code that pins it.

---

## 7. Deviations from Dv456

| id | what | cause |
|---|---|---|
| **Dv456** | Step 0's tail is FOUR `knowledge/**` files and not the three the contract names — `hot.md` is modified by this session's own SessionStart hook. The list is built from live `git status`. | `[cause: live-status-over-prose]` |
| **Dv457** | `reader_v4_pod_runner.check_instrument` compared the pod's WHOLE reader map against the registration, so registering a fourth text refused a frozen pack nothing had touched — and blamed the prompt map when what parted is the module. Narrowed to the tasks the pack pins, exactly as the v4 record's own `prompt_rule` states; both directions tested and the shipped pack still refuses, with the true reason. | `[cause: code-and-record-parted]` |
| **Dv458** | A re-close is a NO-OP, not a refusal. The contract says «a re-close is refused, proven»; the guard finds the closing entry and appends nothing, exit 0, both ledgers byte-identical. Reported as measured. | `[cause: reading-of-the-clause]` |
| **Dv459** | ONE close COMMAND writes TWO ledgers — the step's closing entry and the live line's witness of the same balance. That is Dv447's fix working, and «the ONLY guard write» is named here rather than left to be discovered in a diff. | `[cause: name-the-write]` |
| **Dv460** | The echo duty's premise. v4's 93 of 111 is not a completeness shortfall: 18 ids are answered in `noise`, 3 are in BOTH lists, and the union covers 111 of 111 with 0 absent and 0 extra. Pair 6 is written over both lists — the only form the instrument can obey without breaking v3's own outranking rule — and the census counts three states. | `[cause: measured-before-writing]` |
| **Dv461** | The output ceiling moves 2 000 → 4 000, both legs. m2 («`finish_reason` stop on every chunk») is unreachable by arithmetic at 2 000: a 16-row chunk's pessimistic answer is 2 491 tokens and 7 of 26 units are over. Computed from v4's own rows and published as a table. | `[cause: bar-unreachable-as-registered]` |
| **Dv462** | The pre-generation BUDGET is negative (−44.8 s), so the boot table cannot use it as an elapsed. Worked at v4's measured 39.0 s, and the affordability deadline (675.2 s) is registered as binding before the twelve-minute ceiling, always. | `[cause: a-budget-is-not-an-elapsed]` |
| **Dv463** | Two denominators. `tokens_per_requested_row` is completion over the PARSED threads (137.83), not over every billed thread (167.9); the seconds rate is the other way round. The first draft mixed them and over-priced leg B by 22%. | `[cause: two-denominators]` |
| **Dv464** | Runbook hygiene applied as an EDIT to `scripts/runbook_reader_v4.md`'s eight verify commands plus a dated corrections block. NO file under `docs/reports/` is touched: a runbook is a procedure, a report is the record of what was run. Runbooks of closed phases are left alone. | `[cause: procedure-not-transcript]` |
| **Dv465** | Leg A's 23 per-thread request shas are RE-DERIVED under v5 and all 23 differ from v4's, while the population DIGEST is copied unchanged. «Copied object-equal where possible» reaches the bars and the digest; a rendering under a different instrument is a different request and may not be copied. | `[cause: the-digest-carries-no-rendering]` |
| **Dv466** | `local_llm.py` is NOT edited. The chunk header and the stopping criterion reach the client through a subclass and a wrapped `generate` inside the v5 runner, so `ReaderClient.read` stays the one inference path and no sha three sealed registrations pin has to move for a keyword argument. | `[cause: keep-the-pins]` |
| **Dv467** | m1 carried Dv461's defect one bar over. `echo` counted an id in `per_comment` AND in `noise` as `duplicated` and m1 gated on it, so the prompt's «at most one of the two» broken would fail the bar that exists to prove the CHUNKING mechanism — a slip reader-v4 made on 3 of 111 ids with no chunking near it and the parser tolerates by design. `duplicated` now means one id twice in the SAME list, which is what the registration's rule says («no duplicate across parts»); `in_both_lists` is REPORTED with v4's baseline and the reachability is registered. Both directions driven, and m1 also fails when the merge could not be made. | `[cause: bar-unreachable-as-registered]` |
| **Dv468** | v5's `--gate` reads the PACK, which v4's never had to — the projection's second leg needs the per-unit payable counts. A new file dependency on the KILL-RULE path: named as a `SystemExit` that says where to write the pack, and `main(["--gate"])` driven end to end instead of only `projection()` with a fixture. The run contract inherits the constraint: the pack must land at `results/reader_v5_pack.json`. | `[cause: new-dependency-on-the-kill-path]` |

---

## 8. Process signals

1. **The measurement rewrote the duty it was asked to write.** Pair 6 was specified as «a row for
   every id»; the evidence says every id already comes back and the question is WHICH list it comes
   back in. Fifteen minutes of counting on a file already on disk turned a bar that would have failed
   an obedient reader into a census that can tell three states apart — and re-priced bar 4's
   reachability, which nobody had written down: **v5 must win 5 of the 7 non-agreeing gold rows.**
2. **A registered bar can be unreachable by arithmetic before the model is asked.** m2 at ≤16 rows
   under a 2 000-token ceiling fails on 7 of the run's 26 units by the pessimistic reading, and v4's
   own largest reply already sits at 97.3% of that ceiling. «It never fired» is not «it had room»,
   and the only way to tell them apart is to fit the number rather than quote it.
3. **Two guards fired on their author this time, at $0.** The registration-tracked check refused the
   driver until the record was committed; the pod handshake refused a frozen pack the moment a fourth
   text existed — and the second was a real defect in code that has been on a pod. Both were free to
   find here and would have been a boot each to find there.
4. **The cheapest correctness move in this contract was choosing what NOT to edit.** `scorer.py`,
   `local_llm.py`, the v3 parser's behaviour, gold r2 and every accepted report stayed still; the
   ceiling, the chunk header and the stop all arrived beside them. The one shipped file that WAS
   edited — v4's pod runner — was edited because its code and its own registration disagreed.
5. **The finished contract was reviewed and it moved twice — both times for the same reason.** m1
   could have failed for a defect that is not chunking, exactly as m2 could have failed for a
   ceiling that is not the model; and the gate quietly grew a file dependency on the kill-rule path
   that only a direct call to `projection()` was covering. Ten commits, none red. The prompt edit and its 16-test fan-out went in together, and the
   registration went in with the code whose sha it pins — reader-v4 left three red commits behind
   and named them honestly, and the way to not make them is to ask which artefact pins which before
   choosing where the commit boundary goes.

---

## 9. What is open

- **The paid run is NOT in this contract.** `results/prereg_reader_probe_v5.json` is committed and
  FREEZES when the run contract's pod exists.
- **The volume must be re-staged.** Gate 1 differs from v4's for the first time: `src/` HAS moved, so
  the run re-stages and the handshake is what proves the staging worked — not the staging command's
  exit code.
- **The pack must land at `results/reader_v5_pack.json`.** `--gate` reads it for the per-unit
  payable counts and a missing one is now a named refusal; the run contract's runbook has to write
  it to that path and not to a scratch directory.
- **Leg B's projection is an ESTIMATE.** No chunked request has ever been sent on this stack. Its own
  gate is the full-pass inequality, re-checked after every chunk exactly as after every thread.
- **`@matusi_ukr:22242` is one thread answered wholly as noise**, and `@VARUS_channel:10366` put three
  comments in both lists. Neither is a completeness defect and both are attribution questions — the
  census now names them per thread, so v5's result can say whether the block moved them.
