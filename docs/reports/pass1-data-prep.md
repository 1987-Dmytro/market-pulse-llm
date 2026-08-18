# pass1-data-prep — the exam leaves the population, 500 units are drawn under a seed, and the labels file gets a gate

`$0`. No cloud call of any kind, no registration, no money. The store is local and every command
below runs on this machine.

## Read back

- **129 threads / 1 032 payable comments** — the reader cell `narrow|varto_off|plus_spam+scam`,
  re-derived by calling `gate_census_w1_reader.population()`, which holds its own enumeration to
  `gate_census_w1.cell`'s measurement on BOTH numbers; the producer also rebuilds its shipped
  record byte for byte.
- **7 excluded threads** — every thread carrying any of the 64 registered units of
  `results/pass1_probe_b_pack.json`, derived from the pack's `items` and never copied from the
  contract's list, which it then reproduces exactly.
- **The target volume** — `min(500, 968)` = **500**: 1 032 payable in the cell − 64 payable in the
  seven excluded threads = 968 remaining. The 64 units ARE the payable set of those seven threads,
  so the subtraction is exact rather than approximate.
- **The exclusion rule and its proof** — a thread carrying any probe unit leaves the population
  WHOLE; the proof is four empty lists in `results/pass1_label_pack_r1.json` (drawn units inside an
  excluded thread · gold ids drawn · gold ids anywhere in the remaining population · gold ids
  anywhere in either RENDERED page) plus `tests/test_pass1_label_pack.py`, whose gold check has a
  negative control that catches a planted id.
- **Who writes the labels** — the **TEAM LEAD** writes `docs/labels-pass1-r1.jsonl`; the executor
  validates it and commits it verbatim and may never edit a row or generate a label into it. The
  file does not exist yet and two tests assert that it does not.
- **The blind subset** — 40 of the 500 drawn units, same seed, rendered UNLABELLED into
  `docs/label-pack-pass1-r1-blind40.md` so the operator CAN label them blind later. Nothing in this
  contract or the next depends on whether they do.

## Step 0 — the tail, by path, in two commits

```
$ git status --porcelain
 M docs/STATUS.md
 M knowledge/daily_logs/2026-08-18.md
 M knowledge/hot.md            <- the fifth path; the contract's list has four
 M knowledge/index.md
?? docs/PROMPT-pass1-data-prep.md
```

`932164e` the vault tail · `19e19b8` the team-lead files, verbatim. Staged by path, never `-A`.
The extra path is Dv518.

## Step 0.5 — the two ADR debts

`b830d22`. `knowledge/decisions/sitting-b-line-b-and-the-team-lead-labels.md` and
`knowledge/decisions/guard-until-the-tolerance-that-was-a-window-bug.md`, both in the INDEX, both
linked. Neither re-argues its report: the numbers stay in `docs/reports/pass1-probe-b.md` and
`docs/reports/guard-until.md`, and the records state what was decided. The B-sitting record carries
the honesty frame in its five points, including the one this contract had to widen — the sitting
scopes contamination to *the 14 gold rows and their threads*, and the pack is built under the
strictly larger *every thread carrying any of the 64 probe units*.

## Step 1 — the H6 refusal gate: all three constants re-derive

### 1. The reader cell — from the producer, not from the record

```
$ PYTHONPATH=src python3.11 scripts/gate_census_w1_reader.py --out /tmp/again_reader.json
  narrow|varto_off|plus_spam+scam: 129 threads · 1032 payable comments  (expected 129 · agrees True)
$ cmp /tmp/again_reader.json results/gate_census_w1_reader.json && echo "PAIR: byte-identical"
PAIR: byte-identical
```

The record reproduces from its producer, so the 129/1 032 this contract stands on is a measurement
and not a quotation [[trace_the_producer_not_the_result]].

### 2. The seven threads — derived from the probe pack's items

```
@VARUS_channel:10348   @VARUS_channel:10613   @mandziak:3676   @mandziak:3703
@matusi_ukr:22242      @matusi_ukr:22272      @matusi_ukr:22303
```

Identical to the contract's expectation, and `tests/test_pass1_label_pack.py` holds the derivation
to that literal so the two can never drift apart quietly.

**And a stronger fact than the contract asked for.** The 64 probe units are EXACTLY the payable set
of those seven threads — every one of the 64 is payable in the cell, and every payable comment of
those seven is one of the 64. So thread-level exclusion removes 64 payable comments and not 64 ± k;
the volume arithmetic below is a subtraction and never an estimate. Asserted in the record
(`exclusion.the_units_are_the_payable_set`) and in a test.

### 3. The target volume

```
1032 payable in cell − 64 payable in the 7 excluded threads = 968 remaining → min(500, 968) = 500 drawn
```

## D1 ($0) — the pack, drawn under a recorded seed

`scripts/build_pass1_label_pack.py` writes three files and nothing else.

### The cap is DERIVED, and its reachability was computed before it was registered

The contract asks for "proportional with a per-thread cap" and does not name one — so the cap had to
come from somewhere, and a cap picked by eye turns `min(500, 968)` into a claim the draw may not be
able to honour. This population needs a cap: against a median of 3 payable comments it carries
threads of **105, 108 and 125**, and uncapped proportional allocation would put **65 units — 13% of
the pack — in one thread** and 175 in the top three.

**`CAP = 14`, the 90th percentile of the remaining 122 threads' payable counts**, re-derived at
every run by `assert_cap_is_the_derivation`, which refuses if the population moves. Beside it, the
ceiling `Σ min(payable, CAP)` at several caps — the check is not decorative, because the reachable
region starts two steps below the chosen value:

| CAP | ceiling `Σ min(payable, CAP)` | target 500 |
|---:|---:|---|
| 9 | 483 | **unreachable** |
| 10 | 505 | reachable by 5 |
| 12 | 544 | reachable by 44 |
| **14** | **572** | **reachable by 72** |
| 17 | 607 | reachable by 107 |

### The formula, registered

> weight `w = min(payable, CAP)`; allocate the target over the threads by **largest remainder** on
> `w`, tie-broken on `(−remainder, thread)`; take that many msg_ids from the thread's
> msg-id-sorted payable list off one `random.Random(SEED)` stream.

Largest remainder rather than a redistribute loop because it cannot exceed a weight here:
`floor(target·w/W) + 1 ≤ w` for every `w ≥ 1` whenever `target < W`, and `W ≥ target` is asserted
before the allocation runs. The tie-break key is total, so two runs cannot order two equal
remainders differently [[an_order_key_that_is_not_total]]. **`SEED = 20260818`** is a module
constant and not a flag — a `--seed` option is an option to produce a different pack — and the draw
was run once under it and never re-rolled.

### What it printed

```
$ PYTHONPATH=src python3.11 scripts/build_pass1_label_pack.py
wrote docs/label-pack-pass1-r1.md  sha256 5aec5c9835f84e58…  278694 chars
wrote docs/label-pack-pass1-r1-blind40.md  sha256 d2364ff3e30b765c…  91238 chars
wrote results/pass1_label_pack_r1.json  sha256 e5ca328e5d993b81…  60453 chars
  1032 payable in cell − 64 payable in the 7 excluded threads = 968 remaining → min(500, 968) = 500 drawn
  cell narrow|varto_off|plus_spam+scam: 129 threads · 1032 payable  →  122 threads · 968 payable
  excluded 7 threads carrying 64 probe units (64 payable removed); the units ARE that payable set: True
  contamination: drawn-in-excluded 0 · gold drawn 0 · gold in population 0 · gold rendered 0
  seed 20260818 · cap 14 (p90) · capped weights 572 >= target 500 — reachable True
  largest thread @matusi_ukr:22058: 125 payable → 12 drawn (2.4% of the pack; uncapped it would have taken 65)
  per-thread distribution (allocated → threads):
      0 drawn ×   2 threads   (payable 0–0)
      1 drawn ×  35 threads   (payable 1–1)
      2 drawn ×  24 threads   (payable 2–3)
      3 drawn ×  17 threads   (payable 3–4)
      4 drawn ×   9 threads   (payable 5–5)
      5 drawn ×   4 threads   (payable 6–6)
      6 drawn ×   2 threads   (payable 7–7)
      7 drawn ×   3 threads   (payable 8–8)
      8 drawn ×   4 threads   (payable 9–9)
      9 drawn ×   3 threads   (payable 10–11)
     10 drawn ×   4 threads   (payable 12–12)
     11 drawn ×   2 threads   (payable 13–13)
     12 drawn ×  13 threads   (payable 14–125)
```

**120 of the 122 threads carry at least one target.** The two that do not carry **zero payable
comments** and cannot contribute one: `@sashafitnesslife:3939` is 29 comments of which 29 are
silenced participation markers, and `@tarilka_malyuka:829` is 3 comments all of which are
text-less. They are named in the record and not rendered, so a reader is never left guessing
whether they were dropped or missed — and they are also the whole difference between the 84
silenced comments of the remaining population and the 55 that reach the page.

### The contamination proof

Four lists in `results/pass1_label_pack_r1.json`, all four empty:

| check | result |
|---|---|
| drawn units sharing a thread with a probe unit | `[]` |
| the 14 gold msg_ids drawn | `[]` |
| the 14 gold msg_ids anywhere in the remaining population | `[]` |
| the 14 gold msg_ids anywhere in either RENDERED page | `[]` |

The last one is checked against the rendered TEXT and not against the unit list, because a thread
is rendered whole — 847 text-less and 55 silenced comments are on those pages beside the 500
targets, and an id can be on the page without being drawn. Its test carries a negative control that
plants a gold id in a string and proves the same expression finds it.

### The rendering

`docs/label-pack-pass1-r1.md`, 278 694 chars: a codebook header, then 120 threads in
`channel:post_id` order, each printed WHOLE — the post, then every comment in the store's own order
with its msg_id, whether payable or not, `*(silenced)*` and `*(text-less)*` marked — with the drawn
comments marked `⬛ **TARGET**`. The labeller reads a conversation, and a conversation with a third
of its turns deleted is not the one the comment was written into.

**The codebook is quoted by the same bytes, from the module the pass-1 prompt itself answers
under**, never retyped, so a label and an answer are decided by one law and not by two wordings of
it [[prompt-must-carry-the-annotators-law]]:

| section | source | sha256 |
|---|---|---|
| the attribution law | `src/market_pulse/prompts.py::READER_ATTRIBUTION_LAW_V5` | `4343df2179523fd3…` |
| the F2a carve-out | `src/market_pulse/prompts.py::READER_CARRY_V5` | `5a2f520883b6ec48…` |
| the r2 adjudication | `results/reader_gold_w1_r2.json::revision` | ruling 4 |

Plus the four `subject_type` readings taken from `prompts.PASS1_SUBJECT_TYPES`, JSON `null` stated
as an ANSWER rather than a skip («this comment is about nobody»), and one line saying «категория» is
not one of the four. A test asserts both quoted blocks are present verbatim in both pages and that
the law it quotes is the same string `PASS1_COMMENT_PROMPT` carries.

**One sentence of the r2 ruling is elided, and the elision is declared** — see Dv519. Two tests
guard it: the 14 gold msg_ids appear on neither page, and neither do the three bar figures that
sentence carries (`0.357`, `0.429`, `0.643`), each with the source record as the positive control.

**The producer pins itself.** `producer.sha256` in the pack record is the sha of
`scripts/build_pass1_label_pack.py`, so ANY edit to that script — a comment included — reddens
`test_the_shipped_pack_is_what_the_producer_builds_today` until the three files are rebuilt. That
is safe here only because the draw is deterministic from the seed: rebuilding after an edit
reproduces the same 500 units and moves nothing but the sha
[[a_comment_only_edit_moves_the_files_hash]]. Rebuild, do not re-pin.

### The blind 40

`docs/label-pack-pass1-r1-blind40.md`, the same renderer over 40 of the 500 drawn units sampled off
the same seeded stream immediately after the draw. Same codebook, same whole threads, no labels and
no answer key. It exists so a second reader CAN label the same units blind and the agreement can be
measured; **nothing in this contract or the next depends on whether anyone does.**

## D2 ($0) — the labels gate, red-first

`scripts/validate_pass1_labels.py <file>` refuses and **writes nothing** — it holds no `write_text`
at all, and a test asserts that as well as the untouched directory, because a directory snapshot
cannot see a write somewhere else [[check_granularity_matches_the_claim]].

Five named refusals, each with its own red test, plus the green path:

| defect | refusal |
|---|---|
| a row from one of the seven excluded threads | «rows come from EXCLUDED threads …» |
| a `(thread, msg_id)` that is not a drawn unit | «rows are not units of the pack …» |
| a unit answered twice | «units are answered more than once …» |
| a drawn unit not answered | «of 500 drawn units are not answered …» |
| a `subject_type` outside the four + `null` — including the STRING `"null"` | «outside the taxonomy … never the string 'null'» |
| an absent `subject_type` key | «An absent subject_type is not null — null is an answer» |

The excluded-thread check is deliberately separate from «not a unit», which subsumes it
arithmetically: it is the one defect the honesty frame exists to prevent and it deserves its own
sentence when it fires. An absent key is refused apart from `null` for the same reason — `null` is
an answer and a missing key is a row nobody looked at.

```
$ PYTHONPATH=src python3.11 scripts/validate_pass1_labels.py /tmp/fake_labels.jsonl
OK — 500 rows, every one of 500 drawn units answered once
  null               100    20.0%
  категория_личное   100    20.0%
  молочный_бренд     100    20.0%
  не_наш_рынок       100    20.0%
  сеть_ритейлер      100    20.0%

$ PYTHONPATH=src python3.11 scripts/validate_pass1_labels.py /tmp/bad.jsonl   # one gold row planted
1 rows come from EXCLUDED threads, first @matusi_ukr:22242:578951 at line 500. Those threads carry
the 64 registered probe units and the 14 gold rows — this file must never label one
exit=1
```

## File ownership, extended

**`docs/labels-pass1-r1.jsonl` is a team-lead file from the moment it exists**: the executor
validates it and commits it verbatim, and never edits a row or generates a label into it. Recorded
in `implementation-notes.md`, in the pack record's `labels.written_by`, and asserted by two tests
that the file does not exist. Freezing a provenance-tagged copy into `results/` — `labelled_by`,
date, codebook, seed, pack sha — is the NEXT contract's step, after the labels exist and validate.

## Verify

```
$ make check                                    # before
2927 passed, 2 skipped in 480.85s (0:08:00)     # the team lead's baseline, reproduced

$ PYTHONPATH=src python3.11 scripts/build_pass1_label_pack.py --outdir /tmp/pack1
$ PYTHONPATH=src python3.11 scripts/build_pass1_label_pack.py --outdir /tmp/pack2
$ for f in docs/label-pack-pass1-r1.md docs/label-pack-pass1-r1-blind40.md \
           results/pass1_label_pack_r1.json; do cmp /tmp/pack1/$f /tmp/pack2/$f && echo "IDENTICAL $f"; done
IDENTICAL docs/label-pack-pass1-r1.md
IDENTICAL docs/label-pack-pass1-r1-blind40.md
IDENTICAL results/pass1_label_pack_r1.json

$ PYTHONPATH=src python3.11 -m pytest tests/test_pass1_label_pack.py tests/test_validate_pass1_labels.py -q
32 passed in 17.77s

$ shasum -a 256 results/pass1_label_pack_r1.json docs/label-pack-pass1-r1*.md
e5ca328e5d993b81d7536b2846924ddb6e5bef3364250ba51fcf8fd35a362e4a  results/pass1_label_pack_r1.json
5aec5c9835f84e584d4d6f4770cb8c1080c4c5084acd0f3434caa6dd11fc0f93  docs/label-pack-pass1-r1.md
d2364ff3e30b765ce1fa76bd379bcde8a09d505fc6f646075d12152b87a4e4b7  docs/label-pack-pass1-r1-blind40.md

$ make check                                    # after
2959 passed, 2 skipped in 495.44s (0:08:15)     # 2927 + this contract's 32

$ git status --porcelain                        # after the last commit of this contract
                                                # (empty)
```

No `runpodctl` was run. `git log --oneline` for this contract shows no `run(` and no `close(`
commit, because there was nothing to spend.

## Deviations from Dv518

| # | what | tag |
|---|---|---|
| **Dv518** | **Step 0's path list is four and the live tree carried five.** `knowledge/hot.md` was rewritten by `/close` after the contract was written, so it is not in the list — and the contract's own Verify block demands a clean `git status` at the end. Committed with the vault tail rather than left dirty or committed alone. The list was right when it was written; the tree moved under it [[brief_can_outrun_the_document]]. | `[cause: contract-gap]` |
| **Dv519** | **The r2 ruling names a gold row, its gold value and the bar it moved — and the codebook may not.** `revision.ruling.reading` ends «…msg 21599 was scored gold «категория» against a reader that answered «категория_личное», and collapsing the two moved bar 4 from 0.357 to 0.429…». The contract asks the codebook to carry "the r2 adjudication rulings"; the honesty frame's first point forbids showing the labeller exam material. Quoted: the three `operator_words`, the `change`, and the reading up to that sentence. The cut is made at a literal marker the producer REFUSES to run without, and the elision is printed on the page and recorded in the pack. | `[cause: contract-gap]` `[[the-codebook-that-quoted-the-answer-key]]` |
| **Dv520** | **The contract names a per-thread cap and no value, and a cap has a floor the target sets.** `min(500, 968)` is only honest if `Σ min(payable, CAP) ≥ 500`: at CAP=9 the ceiling is **483** and the draw would have come up 17 short with nothing in the record saying so. The cap is registered as a derivation (p90 = 14, ceiling 572) with `assert_cap_is_the_derivation` refusing if the population moves and `allocate` refusing if the ceiling ever falls under the target. Reachability computed BEFORE the formula was registered, not after. | `[cause: contract-gap]` `[[an_absolute_bar_needs_a_reachability_state]]` |
| **Dv521** | **A record block named one thread beside another thread's size.** `largest_thread_share` first picked `max(weights, key=allocation)` and printed `max(sizes)` next to it — but **thirteen threads share the top allocation of 12** and only one of them is the 125-comment thread the cap exists for, so the first run published `@klopotenkofood:6032 · 125 payable`, which is false about that thread. Keyed on payable count now, with the thread's own weight and allocation beside it. Caught by reading the output, not by a test — the test came after. | `[cause: process]` `[[cooccurrence_is_not_explanation]]` |
| **Dv522** | **A red-first fixture built by mutating a live id went red for the wrong reason.** "a `(thread, msg_id)` that is not a unit" was built as `msg_id + 1` — which landed on ANOTHER drawn unit of the same thread, so the duplicate gate refused it and the test passed while never exercising the check it names. Replaced with an id no pack can hold. The refusal a red test observes has to be the one it is named after [[fixtures_built_on_live_data_collide]]. | `[cause: verify-gap]` |
| **Dv523** | **«writes nothing» cannot be proved by watching one directory.** The first version of the green-path test snapshotted `tmp_path` — before its own fixture had been written, so it failed loudly; but even correct it would only have seen writes into that one directory, and the risk is a write into `results/`. Now: the directory is snapshotted after the fixture exists AND the module's source is asserted to contain no `write_text`/`write_bytes` at all. | `[cause: verify-gap]` `[[check_granularity_matches_the_claim]]` |

## Process signals

1. **The gate passed on all three and the useful work was the fourth constant nobody registered.**
   The contract's three re-derived in about four seconds; the cap it did not name is where the
   thinking went, and the reachability table (Dv520) is the only artifact here that could have
   turned into a silent 483-row pack.
2. **The stronger fact was cheaper than the one asked for.** «the 64 units ARE the payable set of
   those seven threads» costs one set comparison and turns the whole volume arithmetic from an
   estimate into a subtraction. Asking what ELSE is true of a derivation, once it is in hand, keeps
   paying.
3. **Two of three self-inflicted defects were in the tests, not in the code** (Dv522, Dv523). A
   red-first suite is only as good as the reason each test goes red, and both of these went red —
   or would have — for a reason that was not the one on the label.
4. **Reading the output caught what no test was watching** (Dv521). The block was internally
   consistent, its numbers were all real, and it named the wrong thread; nothing but a human
   reading the line beside the distribution table would have seen it.
5. **The honesty frame did work here, not just in the ADR.** It is what forced Dv519's elision, what
   made the excluded-thread refusal its own message in D2 rather than a special case of «not a
   unit», and what makes the gold check run against the rendered page instead of the unit list. A
   frame that never changes an implementation decision is a paragraph.
