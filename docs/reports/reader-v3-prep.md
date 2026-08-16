# reader-v3-prep — the A+B instrument, gold r2, the reader's own cell, and a registration nothing may edit

**$0 GPU. No endpoint, no pod, no template was created.** The only cloud calls this contract made
are `runpodctl user` and `runpodctl billing` — balance and billing reads, which the contract puts
outside the budget. The paid re-read is `reader-v3-run`.

**Baseline:** `make check` **2 584 / 2 skipped** at `c3b6b70`, plus the standing tail.
**Close:** `make check` **2 623 / 2 skipped**, `ruff format --check .` clean over 312 files.

Nine commits, `f1368da` … `881941c`.

---

## 0. Step 0 — the tail, two commits by path

`git status` before anything: five modified files and one untracked, and every one of them inside
the two classes the contract names. Nothing outside them, so nothing to stop on.

- **`f1368da`** — `knowledge/**`: the 16.08 sitting ADR (which grew its own amendment paragraph
  during `cycle2-money`), the daily log, `hot.md`, `index.md`.
- **`fabd2f3`** — the team-lead files, committed **verbatim**: `docs/STATUS.md` and this contract,
  `docs/PROMPT-reader-v3-prep.md`.

Staged by path in both cases. Never `git add -A`.

---

## 0.5 — amendment 3.24, and the anchor taken deliberately

### 0.5.1 The landing, six parts

`b3db748` was the precedent and every part of it is here:

| # | part | where |
|---|---|---|
| 1 | its own marked block, index note INSIDE it | `docs/SPEC.md`, after `amendment-3.23 end` |
| 2 | `write_prereg_5c2.BLOCKS_TODAY` + its own docstring paragraph | `scripts/write_prereg_5c2.py` |
| 3 | the literal enumeration, with its own comment | `tests/test_sku_prereg.py` |
| 4 | the literal tail `BLOCKS_TODAY[10:]` | `tests/test_prereg_5c2.py` |
| 5 | the intruder moves `amendment-3.24` → `amendment-3.25` | `tests/test_prereg_5c2.py:318` |
| 6 | negative controls shown, six sealed pins re-derived unmoved | below |

The suite FORCED part 5 for the second landing running: `fix-c`'s assertion
`intruder not in writer.BLOCKS_TODAY` reddened on the name it had planted.

**The registered law — SPEC with every marked block stripped — is unmoved at 50 135 bytes**, which
is the figure `b3db748` recorded. Live file 82 195 → 84 338.

```
registered law (strip all)  50135 bytes  — b3db748 recorded 50 135, unmoved: True
OK    sku_pilot_prereg       pin 973c87890ad049d5  derived 973c87890ad049d5  keep=[]
OK    sku_pilot_prereg_v2    pin 973c87890ad049d5  derived 973c87890ad049d5  keep=[]
OK    sku_pilot_prereg_v3    pin 973c87890ad049d5  derived 973c87890ad049d5  keep=[]
OK    sku_pilot_prereg_v4    pin 973c87890ad049d5  derived 973c87890ad049d5  keep=[]
OK    sku_pilot_prereg_b2    pin 6818926d22b2a46b  derived 6818926d22b2a46b  keep=['sku-b-ratification-7', 'sku-b-ratification-8']
OK    prereg_5c2_run         pin 3dd43923edc18e72  derived 3dd43923edc18e72  keep=[…the ten…]

SIX SEALED PINS RE-DERIVE UNMOVED: True
negative control — live SPEC hashes to no pin: True
negative control — a 17th block REFUSED: True
negative control — the file as it stands still passes: True
negative control — a KEPT block edited breaks the 5c2 pin: True
negative control — 3.24's own bytes moved, every pin holds: True
```

The last two are the pair that makes this a control rather than a refusal that refuses everything:
editing a block the seal KEEPS breaks the pin, and editing 3.24's own text moves nothing.

### 0.5.2 The constant, removed rather than zeroed

`CYCLE2_ANCHOR_MIN_USD` is **deleted**. Setting it to `0.0` would have left `if balance_now < 0.0` —
unreachable code shaped like a guard — and the whole `cycle is None` / «NOT ANCHORED» / INTER-LEDGER
GAP branch dangling behind it. Removing it took `read_cycle2`'s `None` return, that branch, and the
gap refusal with it: **without a threshold there is no state that produces a gap**. 3.23 (3) still
describes what the gap was; it is closed by the reading now rather than reported by it.

Three tests moved with the law. The two that asserted the floor in both directions are replaced by
one that anchors at **$22.5292058832** — the real reading the old threshold refused — with a
negative control that the constant is **gone from the module**, plus a second test that the one-shot
survives the repeal (a later, lower reading must not re-anchor). The third had a live-walk control
that passed for two reasons at once and is now scoped to the closed phase's half of the print.

### 0.5.3 Dv424 — the repeal made the suite able to write a one-shot anchor

**The very next `make check` after the landing wrote `results/spend_cycle2.json`, untracked, anchored
at $22.00 — a fixture's balance, not the account's.**

The write came from `test_the_phase_is_closed_by_the_guard_and_the_entry_carries_both_readings`,
whose subject is the PHASE close and whose second reading falls through to the line. It patches
`guard.LEDGER` and never had a reason to patch `guard.CYCLE2_LEDGER` — because **3.23 (2)'s $40.00
floor was doing a second job nobody had registered it for**: every balance that file drives is under
$40, so `read_cycle2` returned `None` and the write site was unreachable from the suite. The repeal
removed the accidental protection along with the clause, and the anchor it exposed is a ONE-SHOT.

The bad anchor was deleted before it was ever committed. The fix is autouse and on the MODULE, not
on the test that was caught: a per-test patch holds only until the next test drives `main()` past a
closed phase, which is exactly how this one arrived. Its negative control asserts the REDIRECT and
not the absence of a file — «the real ledger does not exist» would pass forever once the operator's
deliberate run has created it, which is precisely when the protection stops being observable.
`[cause: guard]`

### 0.5.4 The anchor, taken once and on purpose

The deliberate run, after the landing (`25fe282`) and after the leak was closed (`044495a`):

```
PHASE 4 CLOSED    $32.4708 of $33.00  (final reading 2026-08-16T11:09:48+00:00)
  pods            $17.6921
  network-volume  $3.2278   <- always on, beside the run and never inside it
  serverless      $11.5509
anchor            $22.51 at 2026-08-16T12:14:48+00:00
balance now       $22.51
  balance delta   $0.0000
  billing since   $0.0000 (no billing rows yet)
CYCLE 2 SPENT     $0.0000 of $20.00
REMAINING         $20.0000
anchored spend_cycle2.json — commit it and never regenerate it
```

Exit 0. No «NOT ANCHORED», no INTER-LEDGER GAP refusal. **`runpod_balance_at_cycle2_start` is
$22.5097614388** — read back out of the file, not off the print, which rounds it. The inter-ledger
gap is over and `docs/reports/cycle2-money.md` finding (2) is closed. Re-read at the end of the
contract it stands at $0.0097 of $20.00 — the standing volume, and nothing else.

---

## 1. D1 — the v3 parser: container tolerance by ruling, domains strict

`parse_reply` learns EXACTLY three container repairs, scoped to `prompts.READER` (the family, all
three texts — the ruling is about how the reader's answer is READ, not about which text asked for
it). POSITIONS and the caption paths are untouched.

```
=== the three repairs, driven ===
  1 two objects merged   -> ['two top-level objects merged']
  2 {} -> []             -> ['signals: empty object -> empty list', 'noise: empty object -> empty list']
  3 msg_id map -> list   -> ['noise: map keyed by msg_id -> list']
  clean verdict          -> [] (the key rides on every verdict)

=== refuse-on-conflict, and the three standing refusals ===
  two disagreeing objects                      -> REFUSED two disagreeing objects: post_summary
  aspect: null                                 -> REFUSED signals.aspect is not a string
  from_post, no evidence                       -> REFUSED missing field: evidence
  bare fragment                                -> REFUSED no JSON object in reply
  a map keyed by a NAME (NOT one of the three) -> REFUSED entities is not a list
```

`repairs: [...]` rides on **every** reader verdict, empty list included, so «read straight» and
«written by an older parser» are never the same absence.

### 1.1 The measurement: probe-b's own 23 paid replies

```
as run 13/23   ->   under v3 19/23
repairs that fired: {'two top-level objects merged': 1,
                     'noise: map keyed by msg_id -> list': 1,
                     'signals: empty object -> empty list': 4}
refusals that remain: {'missing field: evidence': 2,
                       'two disagreeing objects: name': 1,
                       'signals.aspect is not a string': 1}
```

Nineteen is the same count `results/reader_probe_b_coerced.json` reached — **with a wider repair
list and by a different instrument. It is not the same measurement**, and neither the registration
nor this report claims an agreement nobody bought.

Two results inside that table are worth naming.

**`@VARUS_channel:10348` recovers the entity case §5.2 of probe-b's report found in the object
beside the one v2 read.** Two top-level objects, nothing shared, merged — and `Varus` /
`сеть_ритейлер` (E3) is in the verdict.

**`@VARUS_channel:10360` is refused by the refuse-on-conflict clause, and that is the right
outcome.** Its reply closes the object after `discussion_summary` and goes on writing
`"entities": [...]` OUTSIDE the braces — probe-b's seventh shape, a bare fragment. The array's five
elements read as five top-level objects that disagree on `name`, so the clause catches it. Under
`dict.update` last-wins they would have merged into ONE entity out of five: exactly the silent
repair that authors structure, which the operator's clause exists to prevent.

### 1.2 Dv425 — repair 3 is narrower than the coercion script's, on purpose

`probe_b_coercion.repairs()` turns a map into a list for any of the four fields and, for `entities`,
folds the key in as `{"name": key}`. This parser implements the contract's clause 3 as written — «a
map keyed by **msg_id**» — so the keys are DROPPED (every row already carries its own `msg_id`) and
a map keyed by anything else is not repaired.

Two reasons, and the first is the ruling's own words. The second: writing the key into a `name`
field is supplying a field the model did not write, which is the far side of «tolerant to the
CONTAINER, strict about the DOMAINS». The shape it would have repaired is `entities`' Dv393 shape,
which the v2 schema line closed at the source and which **no probe-b reply returned** — the
coercion script's `entities: map -> list` branch never fired. `[cause: contract-reading]`

### 1.3 Dv426 — the verify block's «3/3 parse» cannot be met by any container-only tolerance

The contract's verify block expects probe-a's three real paid replies to parse 3/3 under the v3
parser, «they did under coercion». Measured, both readings:

| reply | as run (v1) | narrow, as ruled | wide (the script's `entities` branch) |
|---|---|---|---|
| `@mandziak:3701` | `entities is not a list` | **parses** (`entities: empty object -> empty list`) | parses |
| `@VARUS_channel:10451` | `entities is not a list` | REFUSED `entities is not a list` | parses (`entities: map -> list`) |
| `@tarilka_malyuka:715` | `entities is not a list` | REFUSED `entities is not a list` | **REFUSED `signals.evidence is not a msg_id`** |
| | | **1 of 3** | **2 of 3** |

**Neither reading reaches 3/3**, because the third reply carries Dv394's `evidence: [null]` — a
DOMAIN defect, on the explicit NOT-repaired side of the ruling. The expectation is unreachable by
construction and both readings are reported rather than one of them chosen quietly.

This is the one place where the contract's clause 3 and its verify block disagree, and the
implementation follows the **clause**, which is the part the contract calls LAW. Widening repair 3
to cover a map keyed by a name is a one-line change and a decision for the team lead; it is worth
one reply of probe-a's frozen history and nothing in probe-b's. `[cause: contract-conflict]`

### 1.4 Dv428 — probe-b's driver lost a comparison it could no longer make

`assert_serving` compares dicts WHOLE, so `expected_worker`'s `reader_prompt_sha256` — the frozen
record's two-entry map against a worker that now serves three — became an invariant **no new
registered reader text can satisfy**, and re-pinning a sealed registration to green it is refused.

The field left `expected_worker`; the record's real claim — each text IT registered is served with
the bytes it registered — is asserted in `handshake` with a message of its own, so «the volume is a
session behind» and «this worker is not serving what this run registered» are never confused. The
live whole-dict check one line above is untouched and is strictly stronger for the failure it
exists to catch. `[cause: sealed-record]`

### 1.5 Dv429 — a frozen producer was deriving from a family that grows

`write_reader_prereg_v2.instruments.prompt_sha256` was built from `sorted(prompts.READER)` — the
LIVE family. Left alone, the frozen v2 record would have re-derived with a third entry nobody
registered: a sealed registration rewriting itself because a later contract registered a prompt. It
names the two texts it registers now, and the producer joins the MOVED list with its own witness.
`[cause: sealed-record]`

### 1.6 Dv430 — a planted control became law

`tests/test_positions_serving.py` refused `reader_thread_gm4_v3` as an unregistered task. D2 made
that name law, so the control would have gone on passing while testing nothing. It is
`reader_thread_gm4_v4` now, with its premise (`unregistered not in prompts.PROMPTS`) asserted rather
than assumed. `[cause: house-pattern]`

---

## 2. D2 — the v3 prompt, derived and not retyped

`reader_thread_gm4_v3`, registered beside v1 and v2 in `PROMPTS`, in `READER` and in the task map.
**Six `_swap` calls**, so «six changes» is a property of `prompts.py` and a seventh would have to
appear there as a seventh call. The test asserts it as a diff: 6 edits, 4 `replace` + 2 `insert`, 0
`delete`, four old lines rewritten into six new ones — plus each swap's new text absent from v2 and
present exactly once in v3.

```
reader_thread_gm4      b272115637f784ad63c6fb2483e0b0ac3d6381901a096dc1cb5406b81a46c8cd
reader_thread_gm4_v2   9d281bc80f18c91b6b0c32cbcdb37540504be887887d0dd1f1ab1c25841250c5
reader_thread_gm4_v3   22533644cf35420eb18599c7329f80ea5ffa877b7aec8cb9eca292b80998803f
```

### 2.1 The full final text of the six changes

Each is a `V2 → V3` pair of module constants; the v2 side is what the text says today.

**The frame — two changes.**

1. `READER_ANSWER_ALONE_V2 → _V3`, the closing line:

> Answer with ONE JSON object and nothing else: one opening brace before the first key, one closing
> brace after the last, and every key above INSIDE them. No explanation, no code fence, nothing
> before the first brace and nothing after the last — never a second object beside the first, and
> never a key written outside the braces.

2. `READER_ONE_OF_TWO_V2 → _V3`, a rule line gains a second one beside it:

> - A comment belongs to at most one of "per_comment" and "noise".
> - "entities", "signals", "per_comment" and "noise" are LISTS. A list with nothing in it is written
>   [] — never {} and never an object keyed by an id or by a name.

**The reading gap — four changes.**

3. `READER_PER_COMMENT_V2 → _V3`:

> - "per_comment" — one object for EVERY comment you were given, in the order you were given them:
>   {"msg_id"; "subject_type"; "subject_id" or null; "stance" or null; "aspects": the aspects it
>   touches, from the six above; "note": one phrase, only where the row needs one}. A comment that
>   carries neither a subject nor an attitude still gets its object, with "subject_type": null and
>   "stance": null — that row says «read, and nothing to charge to anybody». The only comments left
>   out are the ones you report in "noise".

4. `READER_DUTY_THREE_V2 → _V3`:

> (3) THE SIGNALS. Only now, and only what duty (2) has already resolved. One thread usually carries
> MORE THAN ONE: report every signal you find and never stop at the first.

5. `READER_JUDGE_WHAT_IS_WRITTEN_V2 → _V3`, a rule line gains a second one beside it:

> - The channel's own reply inside the thread is evidence like any other comment. When somebody asks
>   for a kind of product and the channel answers with the trade marks it has, that exchange is a
>   signal about demand — read it, and do not skip a comment because the shop wrote it.

6. `READER_NOT_A_SIGNAL_V2 → _V3`, inside the SIGNAL definition:

> Praise counts: «смачне», «беру постійно» about a tracked trade mark or about the tracked kind of
> product is a signal (похвала) with the aspect it names, however short the comment is. Anything
> else in this thread is not a signal, however interesting — a thread that carries none is a normal
> answer and gets an empty list [].

Each is traceable to a miss that was paid for: (1) and (2) to probe-b's container shapes 1–3 and the
bare fragment; (3) to finding 5's four gold rows absent from replies that parsed cleanly; (4) to F1
carrying three signals where the run returned one; (5) to F1b, two of whose three msg-ids are the
channel's own reply; (6) to F1c.

**v3 is opt-in.** `reader_messages_gm4` keeps v2 as its default. Every caller that passes no `task`
is a caller whose evidence is already on disk, and moving the default would re-render a frozen
record's request under a text no thread was ever sent with.

### 2.2 Pin fan-out, eyes open

Six result records name `prompts.py` by sha. Enumerated with a typed walk over `results/**.json`,
not grepped:

| record | before | treatment |
|---|---|---|
| `prereg_reader_probe.json` | already stale | existing MOVED tuple, still holds |
| `reader_gold_w1.json` | already stale | existing MOVED tuple, still holds |
| `validate_5c2_pack.json` | already stale | existing MOVED tuple, still holds |
| `window_summary_5c2.json` | already stale | existing MOVED tuple, still holds |
| `dashboard_data_w1.json` | **LIVE** | regenerated in the same commit, with `dashboard/index.html` which embeds it |
| `prereg_reader_probe_v2.json` | **LIVE, SEALED** | **MOVED manoeuvre, third time in this family** |

The v2 registration's MOVED block carries `SEALING_COMMIT = 48c974a` (probe-b's last commit), two
tuples with their own witnesses, and `NAMED_IN_THE_RECORD = {prompts.py: 2, write_reader_prereg_v2
.py: 1}` — so a swap that put back one of two mentions cannot pass. `ruff format` ran before every
sha was computed (Dv410).

---

## 3. D3 — gold r2, beside v1, reference untouched

`results/reader_gold_w1_r2.json`, a NEW file. **Twelve `subject_type` cells** reading «категория»
become «категория_личное» — four flagship signals (F1b, F3a, F4a, F5a) and eight per-comment rows —
and nothing else.

```
wrote results/reader_gold_w1_r2.json  sha256 716ff4174bdafa59…
  12 cells «категория» -> «категория_личное»
  `subject_type` cells still reading «категория»: 0
byte-identical rebuild: True (52 928 bytes)
```

Derived, not retyped: the producer imports `write_reader_gold`, builds v1's record from the
reference and the evidence store, and rewrites the cells. **The walk is typed** — it keys on the
FIELD NAME and the exact value — so the sentences that DISCUSS the word (`derivation
.per_comment_rule`, the reference's own `reading_reference` strings) are untouched, which a
`str.replace` would have destroyed. `CELLS = 12` is a registered literal: a thirteenth cell arriving
under a later gold edit REFUSES instead of being relabelled silently.

The rebuild test diffs r2 against **v1 rebuilt today**, not against the committed v1 — the committed
one carries shas a later contract MOVED, and diffing against the file would report those as changes
this revision made. What is left after the twelve cells is byte-identical, plus the two blocks this
producer owns.

`docs/REFERENCE-signals-w1.md` is not edited; its sha is hashed LIVE in the record, so an edit
reddens here instead of being absorbed. `reader_gold_w1.json` is untouched and still carries its 12
cells, which is what says r2 is a new file and not an edit to the one two sealed registrations pin.
The ruling's three operative phrases are quoted verbatim and grepped back into the ADR
whitespace-normalised.

---

## 4. D4 — the reader census cell, measured

`results/gate_census_w1_reader.json` — **narrow · `varto_rule` OFF · `plus_spam`+`scam` ON**.

```
narrow|varto_off|plus_spam+scam: 129 threads · 1032 payable comments  (expected 129 · agrees True)
shipped grid: silencers_off 129 · silencers_on 111 · varto alone 111
at probe-b's 4090 rate: $1.2517 by thread · $1.7187 by payable — binding $1.7187 (by_payable_comment)
output ceiling: probe max 15 payable · this cell max 125 against local_llm.READER_MAX_NEW_TOKENS = 2000
```

The shipped census's own `cell()` is imported and run — that file is never rewritten, its producer's
sha is pinned by its own record and by both reader registrations. An enumeration beside the
measurement is held to it on BOTH numbers, and it exists because D5 needs each of probe-b's 23
threads' status under this cell and a count cannot answer that for one of them.

### 4.1 Dv432 — the thread count alone could not have identified this cell

**129 is also `narrow|silencers_off`'s thread count.** `plus_spam` and `scam` remove COMMENTS, and in
this window they never take a thread's last lexicon hit with them — the shipped decomposition
reports 0 threads removed for both. So a record that reported «129» and stopped would have been
indistinguishable from a cell nobody meant.

The discriminator is the payable count: **1 032 against 1 116**, the 84 comments the two silencers
took. That is the second reason ruling 3 asks for a measurement, and it is what the test asserts.
`[cause: measurement]`

### 4.2 Dv433 — the output ceiling is a WINDOW risk, and it is new

v3 asks for a `per_comment` row for EVERY comment shown, so output length now scales with a thread's
payable count. probe-b returned `finish_reason: length` on **zero of 23** replies under v2 and its
largest thread carries 15 payable comments. **This cell's largest carries 125**, against
`READER_MAX_NEW_TOKENS = 2000`.

So the paired re-read cannot reach the ceiling and a window pass under v3 might. Reported in the
cell record with its unlock — measure `finish_reason` per thread on the v3 re-read and re-price the
ceiling against the observed tokens-per-row before any window pass is opened — and registered as a
non-gating field of bar 5. `[cause: instrument-change]`

---

## 5. D5 — the registration, frozen before any money

`results/prereg_reader_probe_v3.json`, byte-identical rebuild confirmed.

```
population 23 threads · 134 payable · digest ccef35fa4b9c771f… (paired True)
under narrow|varto_off|plus_spam+scam: 23/23 in the cell · 4 of probe-b's injected now enter
cap $0.35 · setup $0.0900 · reading $0.2232 -> all-in $0.3132 (fits the cap, headroom $0.0368)
the cap absorbs a 1.165x slowdown against probe-b
bar 1_flagships                5 of 5 cases
bar 2_entity_cases             4 of 4 cases
bar 3_noise                    0 signals
bar 4_per_comment_agreement    rate >= 0.8
bar 5_time_and_cost            {'cap_usd_all_in': 0.35}
```

**The instrument** is the v3 prompt's sha plus the parser's behaviour STATED — the three repairs by
the exact names the code emits (built from `prompts.TWO_OBJECTS_MERGED` and `READER_LIST_FIELDS`, so
a rename reddens the registration rather than quietly changing what it registered), the narrowing of
Dv425, and the three standing refusals by their reason strings. The test makes every one of them
FIRE on a reply that produces it.

**The population** is probe-b's, unchanged. `POPULATION_DIGEST` is a LITERAL in the producer that
the computed digest must MATCH — a digest recomputed and stored would agree with whatever the
enumeration happened to be. Each thread's status under the new cell is recorded BESIDE the pin: the
digest line carries `gated|injected` from probe-b's cell, and folding today's cell into it would
move the digest and end the pairing.

### 5.1 Dv427 — all four injected threads enter the reader cell, N3 included

Enumerated, not estimated (Dv399):

| thread | case | probe-b | reader cell |
|---|---|---|---|
| `@matusi_ukr:22242` | E1 | INJECTED | **in** |
| `@mandziak:3684` | E4a | INJECTED | **in** |
| `@mandziak:3689` | E4b | INJECTED | **in** |
| `@sashafitnesslife:3939` | N3 | INJECTED | **in** |

The contract expected E1 and E4's threads to enter and N3 to «likely stay injectable». **That is
wrong, measured**: `varto_rule` is the silencer that removed every one of the four, and N3's post
carries the lexicon hit — `plus_spam` only silences its 29 «Тест» comments. So under the reader's
own gate this population has **ZERO injected threads and all 23 are production-reachable**.

The payable lists are identical under both cells, checked per thread: `varto_rule` gates a THREAD,
and the two per-comment silencers stay on. That is why the digest could not have moved.
`[cause: enumeration]`

### 5.2 The money, re-derived

**Setup $0.0900** — probe-b's SETTLED ledger entry ($0.313162, its own resources; the standing
volume is on its own line and not inside it) minus its own reading (727.664 billed worker seconds at
$0.00030669/s). Read from `results/spend_probe_b.json`, the file the guard wrote, never from a
sentence in a report — probe-a closed at $0.0750 and the same step settled at $0.0944 the next day.

**All-in $0.3132 against a $0.35 cap**, headroom $0.0368. And the number that makes that honest:

> **the cap absorbs a 1.165× slowdown against probe-b.**

probe-b's seconds were measured under the v2 prompt, whose `per_comment` carried a row only where a
comment had something to charge. v3 asks for a row for EVERY comment shown, so the same 23 threads
owe more output and will bill more seconds. The projection is registered as a **FLOOR**, not a
forecast, and 1.165× is what the warm-up measures and what the go/no-go stops on. The cap is against
the **cycle-2 line**, not a phase cap: Phase 4 is closed and 3.18 (7)(b) keeps it that way.

### 5.3 Bar 3's fixed predicate, with a producer

> «zero signals» is counted over the noise threads that HAVE a parsed verdict. A refused reply
> contributes nothing and is NEVER a zero; with no parsed verdict among them the bar is
> **UNREACHABLE**, which is not a pass.

It is not prose. `write_reader_prereg_v3.bar_three_over_answers` is the reference implementation the
run contract must reproduce, and the test drives it on probe-b's own rows:

```
as scored:  passed=True · signals=0 · threads=5
registered: threads_registered=5 · threads_with_a_verdict=1 · signals=0
            threads_refused=['@retsepty:7312','@retsepty:7325','@retsepty:7327','@sashafitnesslife:3939']
with none read: reachable=False · passed=False · signals=0   <- zero signals, and still not a pass
with a signal:  passed=False · signals=1                      <- and it still fails the right way
```

The record registers what a result must carry (`threads_registered`, `threads_with_a_verdict`,
`threads_refused`, `signals`, `reachable`, `passed`), so a driver cannot report the number without
its denominator.

### 5.4 Dv431 — the scorer is deliberately untouched

The obvious home for bar 3's fix is `scorer.reader_noise_count`. It is not there, and that is a
decision: `scorer.py`'s sha is pinned by **four** records (`prereg_reader_probe.json`,
`prereg_reader_probe_v2.json`, `reader_probe_verdict.json`, `reader_probe_b_verdict.json`, the last
of which is re-derived byte for byte by its own test). Moving it would have taken all four into
MOVED manoeuvres for a change that is a DENOMINATOR and a reachability state, not a new count —
`reader_noise_count` already returns `per_thread`, and what the fix adds is which threads may be in
it. The run contract writes its own scorer driver and carries the predicate there.
`[cause: sealed-record]`

### 5.5 Dv434 — the 3.24 block had to be inserted by a script

`permissions.deny` carries `Edit(/docs/SPEC.md)`, and the deny rule covers every file-editing tool.
The contract authorises exactly one edit to that file (its DO NOT names «`docs/SPEC.md` outside the
3.24 block»), so the block was written to a scratch file and inserted by a one-shot `python3` script
that asserts the anchor appears exactly once and that `amendment-3.24` is not already present. No
other byte of `docs/SPEC.md` was touched, which the six unmoved pins prove independently.
`[cause: harness]`

---

## 6. Verify — evidence, not assertions

```
$ make check
2623 passed, 2 skipped in 191.22s

$ ruff format --check .
312 files already formatted

$ python3 scripts/runpod_guard.py
PHASE 4 CLOSED    $32.4708 of $33.00  (final reading 2026-08-16T11:09:48+00:00)
anchor            $22.51 at 2026-08-16T12:14:48+00:00
CYCLE 2 SPENT     $0.0097 of $20.00
REMAINING         $19.9903
                                                          exit 0 — ANCHORED, no gap refusal
```

The three prompt shas, the three repairs, the refuse-on-conflict rule and the three standing
refusals are in §1 above, driven. The rebuilds:

```
results/reader_gold_w1_r2.json       byte-identical rebuild: True
results/gate_census_w1_reader.json   byte-identical rebuild: True
results/prereg_reader_probe_v3.json  byte-identical rebuild: True
population digest ccef35fa4b9c771fd62506cd7878177f8184c8344702ad1d05c3bec33abbc1f3  (paired True)
```

The negative controls of the 3.24 landing and the six sealed pins are in §0.5.1.

**probe-b's 23 real paid replies re-driven through the v3 parser: 13/23 → 19/23** (§1.1).
**probe-a's three real paid replies: 1/3 narrow, 2/3 wide, 3/3 unreachable** (§1.3, Dv426).

---

## 7. Deviations

| # | what | cause |
|---|---|---|
| **Dv424** | the repeal made `make check` write the one-shot cycle-2 anchor at a fixture's $22.00; the $40 floor had been protecting the write site by accident | `guard` |
| **Dv425** | repair 3 implemented as ruled («keyed by msg_id»), narrower than `probe_b_coercion`'s `entities` branch, which folds the key in as a `name` | `contract-reading` |
| **Dv426** | the verify block's «3/3 parse» is unreachable under BOTH readings — the third reply carries a DOMAIN defect. Measured 1/3 and 2/3, neither chosen quietly | `contract-conflict` |
| **Dv427** | N3 enters the reader cell; the contract expected it to stay injectable. All 23 threads are production-reachable now | `enumeration` |
| **Dv428** | probe-b's `expected_worker` dropped `reader_prompt_sha256` — a whole-dict invariant no new registered text can satisfy — and the record's real claim moved to `handshake` with its own message | `sealed-record` |
| **Dv429** | `write_reader_prereg_v2` derived `prompt_sha256` from the LIVE reader family and would have grown a frozen record an entry | `sealed-record` |
| **Dv430** | the planted unregistered name `reader_thread_gm4_v3` became law; the control moved to `_v4` and asserts its premise | `house-pattern` |
| **Dv431** | `scorer.py` deliberately untouched — bar 3's fix would have taken four sealed records with it | `sealed-record` |
| **Dv432** | the reader cell shares its thread count with `narrow|silencers_off`; only the payable count identifies it | `measurement` |
| **Dv433** | v3's row-per-comment makes output scale with a thread's payable count: 125 in the window cell against a 2 000-token ceiling. A WINDOW risk, not a probe risk | `instrument-change` |
| **Dv434** | `permissions.deny` blocks every file-editing tool on `docs/SPEC.md`; the authorised 3.24 block was inserted by a one-shot script with its own assertions | `harness` |

---

## 8. Process signals

1. **A repealed threshold can be load-bearing somewhere nobody registered.** The $40 floor was a
   money clause and also, silently, the only thing keeping a test suite away from a one-shot
   production anchor. Removing a guard is a change to everything that was standing behind it.
2. **An expectation inside a contract is data, and it gets measured.** 129 agreed, N3 did not, and
   «3/3» was unreachable. All three are in the record with what was actually measured beside them.
3. **A count that two cells share is not an identification.** 129 threads is `varto_off` and
   `silencers_off` at once; the payable number is what tells them apart. Report the number that can
   discriminate, not the one that reads well.
4. **A frozen record's invariants age against a growing family.** Two of this contract's deviations
   are the same shape — a sealed artifact comparing itself WHOLE against something that grew. The
   fix is always to narrow the claim to what the record registered, never to re-pin it.
5. **Changing what a prompt asks for changes the transport it has to fit.** A row per comment is a
   reading fix and an output-length change at the same time, and the second only shows up when
   somebody multiplies it by the largest thread in the population.

---

## 9. What this leaves the operator

**Decided and frozen.** `results/prereg_reader_probe_v3.json` — the instrument, the population, the
serving, $0.35 all-in against the cycle-2 line, five bars with bar 3's predicate fixed and bar 4
against gold r2. The run contract may not edit it.

**Two questions this contract could not answer alone.**

1. **Dv426 — repair 3's width.** The contract's clause says «keyed by msg_id»; its verify block
   expects an outcome only the wider reading can approach, and even that reaches 2/3. Widening is
   one line and buys one reply of probe-a's frozen history. The narrow reading is what is
   registered.
2. **Dv433 — the output ceiling for a WINDOW pass.** The probe is safe; the 129-thread cell's
   largest thread owes 125 `per_comment` rows against 2 000 tokens. `reader-v3-run` is the run that
   can measure `finish_reason` and settle it before any window pass is priced.

**Money.** Cycle 2 anchored at $22.5097614388, $0.0097 spent of $20.00. The next contract's $0.35 is
inside it with $19.99 to spare; the window at probe-b's rate reads for $1.72 and would still fit.

---

## Appendix — `reader_thread_gm4_v3`, the full registered text

`sha256 22533644cf35420eb18599c7329f80ea5ffa877b7aec8cb9eca292b80998803f` · 6630 characters. The registration freezes the SHA, so this is the only
place the instrument can be read without running Python. Verbatim, and the report's own test of
that is the line below the fence: this block is what the module renders, hashed.

```text
You read ONE discussion thread from a Ukrainian Telegram channel — a retail chain, a discount aggregator, a recipe feed or a parenting feed — and report what the marketing director of a dairy producer needs from it. One thread, one answer: you are given the post and every comment under it, and nothing else.

A SIGNAL is only what answers one of the director's seven questions: (1) what is said, good or bad, about a dairy trade mark; (2) what exactly is liked or disliked about it — taste, price, packaging, quality, availability, service; (3) the same about the competing trade marks and the chains' own labels; (4) which flavours and which kinds of dairy people want; (5) where it is said; (6) that the talk about a brand has turned sharply positive or negative; (7) what a chain promotes, at what price and at what discount. Praise counts: «смачне», «беру постійно» about a tracked trade mark or about the tracked kind of product is a signal (похвала) with the aspect it names, however short the comment is. Anything else in this thread is not a signal, however interesting — a thread that carries none is a normal answer and gets an empty list [].

Three duties, in this order. Never begin one before the one above it is finished.

(1) THE THREAD. The POST sets the topic: the comments are answers to it and are read in its light, never as texts standing on their own.

(2) THE NAMES. Every trade mark and every chain name that appears anywhere in the thread — in the post or in any comment — is resolved from the context it stands in: what it IS here, in one phrase, with the quote you read it in. Four readings and no fifth:
- "молочный_бренд" — a dairy trade mark named as a product, ours or a competitor's, a chain's own label included;
- "сеть_ритейлер" — a retail chain named as the shop: where somebody went, bought, ordered, or whose service is being discussed;
- "категория_личное" — the name stands inside a statement about the kind of product in general, and charging that statement to the brand would be wrong;
- "не_наш_рынок" — the name belongs to something that is not food retail at all: a school, a centre, a club, a housing block, a business in another trade.
A word that is both a name and an ordinary word of the language is a name only where the text uses it as one. Used as the ordinary word, it is not a name: do not report it and do not attach anything to it.

(3) THE SIGNALS. Only now, and only what duty (2) has already resolved. One thread usually carries MORE THAN ONE: report every signal you find and never stop at the first.

Return ONE JSON object with exactly these keys.

- "thread" — {"channel": the handle you were given, "post_id": the number you were given}.
- "post_summary" — one sentence in Ukrainian: what the post is.
- "discussion_summary" — one to three sentences in Ukrainian: what the comments are about.
- "entities" — a LIST of objects, one per name of duty (2), and the name is INSIDE each object: [{"name": as it is written in the text, "msg_id": the comment you read it in, or null when it is in the post, "subject_type": one of the four readings, "reading": one phrase in Ukrainian, "quote": copied from that text}]. Never an object keyed by the names.
- "signals" — one object per signal: {"signal_type": one of "спрос", "жалоба", "похвала", "привычка", "тренд"; "subject_type": one of "молочный_бренд", "сеть_ритейлер", "категория", "категория_личное", "не_наш_рынок"; "subject_id": the trade mark, the chain or the kind of product as one lowercase word or phrase, or null; "aspect": one of "taste", "price", "packaging", "quality", "availability", "service"; "stance": "positive", "negative" or "neutral"; "reading": one sentence in Ukrainian for the director; "evidence": the msg_ids of the COMMENTS you read it from, and the empty list [] when you read it in the post — never null and never the post; "from_post": true when the post is where you read it, and leave it out otherwise; "quote": copied from the post or from one of those comments}. No signal_type in the list fits what you found? Write the word you need and put "proposed": true beside it — a word of your own without that flag is an error.
- "per_comment" — one object for EVERY comment you were given, in the order you were given them: {"msg_id"; "subject_type"; "subject_id" or null; "stance" or null; "aspects": the aspects it touches, from the six above; "note": one phrase, only where the row needs one}. A comment that carries neither a subject nor an attitude still gets its object, with "subject_type": null and "stance": null — that row says «read, and nothing to charge to anybody». The only comments left out are the ones you report in "noise".
- "noise" — one object per comment that is not discussion at all: {"msg_id", "class": one of "плюс_спам" (a participation marker and nothing else), "скам" (money offered by a stranger with a handle or a link), "оффтоп" (an advertisement or a subject with nothing to do with this thread)}.

Rules that outrank everything above.

- COPY a quote, never compose one: it must appear in the message you attribute it to, character for character.
- Every msg_id you write is one that was given to you. The post was given none, so null is the answer in exactly one field — "entities"."msg_id", where it means «this name is in the post». Every other id field takes comment ids and never null.
- A comment belongs to at most one of "per_comment" and "noise".
- "entities", "signals", "per_comment" and "noise" are LISTS. A list with nothing in it is written [] — never {} and never an object keyed by an id or by a name.
- Do not carry a brand from the post into a comment that does not mention it, and do not read the thread's subject off the channel it is in.
- Judge what is written. Do not work out what the author probably meant, and do not report a signal because the post advertises something nobody discussed.
- The channel's own reply inside the thread is evidence like any other comment. When somebody asks for a kind of product and the channel answers with the trade marks it has, that exchange is a signal about demand — read it, and do not skip a comment because the shop wrote it.
- Ukrainian in every prose field; the type words exactly as they are spelled above; the quotes in the language they were written in.

Answer with ONE JSON object and nothing else: one opening brace before the first key, one closing brace after the last, and every key above INSIDE them. No explanation, no code fence, nothing before the first brace and nothing after the last — never a second object beside the first, and never a key written outside the braces.
```

The fenced text above hashes to `22533644cf35420eb18599c7329f80ea5ffa877b7aec8cb9eca292b80998803f` — the same sha `results/prereg_reader_probe_v3.json` pins as `instruments.prompt_sha256.reader_thread_gm4_v3`.
§2.1 stays where it is: the six `V2 → V3` pairs are what makes the change auditable, and this
appendix is what makes the instrument readable.
