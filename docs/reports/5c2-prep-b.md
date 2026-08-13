# 5c2-prep-b — the inference leg is real, and the run keeps its evidence

**Three sentences, and each is a thing that was not true this morning.** The loop can now answer a
queued comment end to end — render, send, write the record, and only then move the watermark — with
the transport as the one replaceable part and no endpoint registered anywhere. Every row it writes
carries what SPEC 3.18 (6) asks the operator sitting to see, named in ONE place
(`src/market_pulse/evidence.py`) so that deleting a field reddens a test instead of surfacing as a
missing column at the sitting. And the two record debts the sku programme parked — Dv232's dropped
parser warnings and Dv176's false `contract:` provenance — are paid, in the driver, with tests on
both arms.

**Cost: $0.** No pod, no endpoint, no template, no serverless job, no OpenRouter call. The RunPod
guard was not run either — this contract needed no balance reading and made no spend to bound.

---

## 1. What shipped, by commit

| # | commit | what |
|---|---|---|
| 1 | `9d558a7` | step 0 — `docs/STATUS.md` + `docs/PROMPT-5c2-prep-b.md` |
| 2 | `24c42cc` | step 0 — the prep-a session tail (three `knowledge/` paths) |
| 3 | `2910037` | step 0.5 — the ADR, `hot.md`'s `⏭️ Next`, the `$30` cap in `ARCHITECTURE.md` |
| 4 | `09b5dac` | **Deliverable 1** — the inference leg |
| 5 | `3232a52` | **Deliverable 2** — Dv232 and Dv176 |

`git status --short` at the end shows one path: `docs/STATUS.md`, arrived modified in the team
lead's hand mid-session (Dv257). It is committed verbatim with this report and was never edited.

## 2. Verify gate

### 2.1 `make check` after every commit, and the checkout table

Every row below is a real `git checkout --detach` into a worktree, running **that commit's own**
suite. `c53e069` is the control — the parent of this session's first commit.

**Read the table with Dv193 beside it.** In a worktree `data/` must be replaced by a symlink to the
repo's (it is partly gitignored and cannot be checked out), and that makes
`tests/test_collect_5c1.py::test_the_guard_reads_the_pinned_paths_off_the_pin_file` red on **every**
row — the control included. The nodeid below was measured on the control in this session, not
inherited from the prep-a report.

```
FAILED tests/test_collect_5c1.py::test_the_guard_reads_the_pinned_paths_off_the_pin_file
```

| # | commit | suite in a fresh checkout |
|---|---|---|
| 0 | `c53e069` **(control)** | 1 failed, 2024 passed, 2 skipped |
| 1 | `9d558a7` | 1 failed, 2024 passed, 2 skipped |
| 2 | `24c42cc` | 1 failed, 2024 passed, 2 skipped |
| 3 | `2910037` | 1 failed, 2024 passed, 2 skipped |
| 4 | `09b5dac` | 1 failed, **2072** passed, 2 skipped |
| 5 | `3232a52` | 1 failed, **2080** passed, 2 skipped |

The one failure is byte-identical on all six rows (`uniq -c` over the six `FAILED` lines returns a
single group of 6). In the real tree, where `data/` is not a symlink, `make check` is green after
every commit: **2025 → 2073 → 2081 passed, 2 skipped**. `ruff format --check .` reports
`252 files already formatted` — it is not part of `make check` and was run separately.

### 2.2 The dry pass, printed

`PYTHONPATH=src python3 scripts/run_loop.py --once --dry-run`, tail:

```
@mandziak                    123      1048      3789        0      1048  yes
@matusi_ukr                  237      2890     22335        0      2890  yes
@mamo_nepsichuy               48        10      8088        0        10  yes

TOTAL 0 comment threads would be fetched, 16218 rows would go to inference

inference: 16218 rows are queued and no serving endpoint is registered. SPEC 3.11 (2)
pre-registers a serving-parity measurement before any serving number reaches an aggregate,
so 5a queues rows and sends none.

--dry-run: nothing fetched, nothing written, no client built
```

**16,218 rows queued** across the registry is a number that fell into my lap and belongs to prep-c.
It is not the pre-registered window: SPEC 3.18 (4) fixes the window BY ROW COUNT from a zero-cost
census, and this is the whole standing backlog above the `inference` watermark, which is currently
unset for every channel. Written down here and taken no further, per the DO NOT list.

### 2.3 The stub smoke — the KEYS of one written record

`PYTHONPATH=src python3 scripts/run_loop.py --once --smoke --infer --channel @mamo_nepsichuy`

```
  stub-served @mamo_nepsichuy             5 rows written, watermark now 17441
wrote results/smoke/loop_5a.json (gitignored — quote it, do not point at it)
```

One evidence row from `results/smoke/derived/inferences/mamo_nepsichuy.jsonl`, keys and types:

```
  row_kind         str        'comment'
  at               str
  channel          str        '@mamo_nepsichuy'
  msg_id           int        17413
  parent_msg_id    int        8025
  task             str        'T1v2_with_post'
  prompt_sha256    str        '495b43d1361d0e4f5f7a186eebb971f4dc3ed9f8afd128f539ba0f6a8ffc2a19'
  model_revision   NoneType   None
  served_by        str        '<stub: scripts/run_loop.py::StubTransport>'
  rendering        list
  reply            dict
  record_type      str
  post_state       str
```

`rendering[0]["content"]`, first 200 characters — the EXACT request, not a description of it:

```
You label one comment from a Ukrainian food-retail Telegram channel (retail chains and
discount aggregators). Comments are in Ukrainian or Russian. You are given the comment
and the post it replies to
```

`reply`, as returned:

```json
{"content": "{\"sentiment\": \"negative\", \"sarcasm\": false, \"intents\": [\"price\"]}",
 "finish_reason": "stop", "cost": 0.0,
 "usage": {"prompt_tokens": 0, "completion_tokens": 0}, "generation_id": null}
```

`finish_reason` across the five rows: `['stop', 'stop', 'stop', 'stop', 'length']` — the stub breaks
one reply on purpose, so the record shape is proven on a row nobody could parse as well as on four
that answer.

**`model_revision` is `None` and that is the point.** Nothing at $0 can say which weights answered.
The key is CARRIED holding the only true value there is, because `evidence.assert_complete` requires
**presence, not truthiness** — an absent field and a null one are different states and only the
second can be read later.

### 2.4 Idempotence, on the artifact

Two runs over the same window, `--limit 20` against 10 queued rows:

```
  stub-served @mamo_nepsichuy            10 rows written, watermark now 17508
  stub-served @mamo_nepsichuy             0 rows written, watermark now None

rows: 10 -> 10   sha256[:16]: a78acaf946b94223 -> a78acaf946b94223   byte-identical: YES
```

**A caveat I hit myself and am reporting rather than hiding:** my first attempt used the default
`--limit 5` and the second run wrote five MORE rows. That is correct behaviour — the queue had ten
and the limit took the next five — but it is not the idempotence claim, because the window was not
the same. The demonstration above uses a limit that covers the whole queue.

`data/loop_cursor.json :: @mamo_nepsichuy` after both smokes is `{'posts': 8088}` — no `inference`
key at all. **A smoke never saves the cursor.** If it did, rows a fake answered would be marked
bought and the next real pass would skip them permanently.

### 2.5 The interrupted pass — the watermark that did not move

`tests/test_loop.py::test_an_interrupted_pass_leaves_the_watermark_and_the_queue_where_they_were`
PASSED. The same scenario, printed rather than asserted:

```
watermark on disk BEFORE : 100
queued BEFORE            : [101, 102]

the model ANSWERED, then the write failed: the disk went away between the answer and the write

watermark on disk AFTER  : 100   <-- did not move
queued AFTER             : [101, 102]  <-- still owed
evidence rows on disk    : 0
```

The assertion is against `load_cursor(path)` — the file — and not against the in-memory `state`. A
`finally: save_cursor(...)` anywhere in the pass would make an in-memory assertion pass while the
file told the opposite story.

### 2.6 `git log --oneline` and the final tree

```
3232a52 fix(5c2-prep-b): Dv232 and Dv176 -- the warnings reach the record per position, …
09b5dac feat(5c2-prep-b): the loop's inference leg -- the record is durable before the watermark …
2910037 docs(5c2-prep-b): prep-a's record closed -- the ADR for the team lead, hot.md's Next, …
24c42cc docs(vault): the prep-a session tail
9d558a7 docs: 5c2-prep-b queued -- STATUS after the prep-a acceptance
```

Run at `3232a52`. This report and the vault tail postdate it and are outside the checkout table
above; their evidence is `make check` green in a tree identical to each of them.

## 3. Step 0.5 — prep-a's record, closed

**The ADR.** `knowledge/decisions/the-law-grows-inside-marked-blocks.md`, written **for the team
lead**, plus its row in `INDEX.md`. It states the mechanism (`registered_law`, one implementation,
four callers, `keep=` for B′), the three things a future amendment must do (wear
`<!-- amendment-3.N begin/end -->`, join the literal enumeration in `tests/test_sku_prereg.py`,
change nothing else), and why the `rev. 3.14` heading is frozen — those bytes are inside the pinned
region, so correcting the number would break five sealed pins for a cosmetic gain. It carries
prep-a's own evidence and a $0 command to re-derive it:

| what | sha256 | state |
|---|---|---|
| `docs/SPEC.md` on disk | `273e9dae9e37ba1a…` | the live file, matching no pin and not meant to |
| registered law, `keep=()` | `973c87890ad049d5…` | re-derives `sku_pilot_prereg_v4.json` |
| registered law, `keep=(7, 8)` | `6818926d22b2a46b…` | re-derives `sku_pilot_prereg_b2.json` |

**`hot.md`'s `⏭️ Next`.** It still opened with the 5c2 briefing that has happened. Rewritten to
prep-b (in flight), prep-c, 5c2-run and 5c2-validate, with the pod-versus-serverless price warning
of 3.18 (4) and the still-open `carrier=comment` deferral. The finished-pilot narrative was not
deleted from the record — it lives in `[[skub2-b-prime-closed]]` and
`[[sku-b-pilot-closed-by-measurement]]`, which the section now points at. **The footgun the brief
named was checked:** `scripts/volume_calc_5c1.py` greps `~$0.24/day` and `80 GB is about what the`
out of this file; both sit in `## 🚧 Blockers` and `## ⚠️ Footguns`, not in the section I touched,
and `make check` was run after the edit and again after the commit.

**`docs/ARCHITECTURE.md`.** Line 324 read «The $25 Phase-4 GPU cap» and now reads $30 with its
authority (SPEC 3.18 (3), operator ruling 2026-08-13). **I grepped the whole file for every other
cap figure and changed nothing else**, because every one of them is a different budget's own cap and
correct as history: `$0.10` (vis-a), `$8` (Phase-3b OpenRouter), `$4.00` (5b stop), `$1.00` (vis-b),
`$0.00` (the 4.5g5 tripwire). A second sweep for a bare `25` found only an unrelated table cell.

## 4. Deliverable 1 — the inference leg

**The queue is the `inference` watermark's, per channel**, stored exactly as `posts` is —
`data/loop_cursor.json` through `market_pulse.backfill`'s atomic whole-file writer. Nothing about
the `posts` watermark or the raw v1 stores changed.

**Where evidence rows go, stated exactly.** The destination decided by this contract is a NEW root,
`data/derived/` — beside the raw v1 stores, never inside them, already gitignored by `data/*` — and
`run_loop.DERIVED_ROOT` is that registration. **Nothing writes there yet, and the constant says so
in its own docstring.** The writer belongs to the paid session's contract, because a served pass
needs an endpoint this contract may not register. The only code that writes evidence rows today is
the stub-served smoke, into `results/smoke/derived/`, which a real pass must never read as already
answered. Both go through `RawStore`, which is generic over `record_type`, so the derived store
inherits the raw store's own `(channel, msg_id)` dedup with no second implementation.

`DERIVED_ROOT` is deliberately not monkeypatched in the tests either: patching a constant nothing
reads makes it look wired. What is asserted instead is the real property —
`test_a_smoke_leaves_the_real_cursor_and_the_derived_store_untouched` checks that no directory
appears there at all.

**The ordering, which is the deliverable.** Per row: render → `send` → append the evidence row →
the write closes (flushing it) → advance the watermark. The reverse order loses rows silently,
because the queue is *defined* as "above the watermark": a row whose record was never written stops
being in it and nothing downstream can see the hole. The watermark advances **in memory**;
persisting the cursor is the caller's, once, after the pass — and a pass that raises must not have
its cursor persisted, which §2.5 drives.

**The queue subtracts two things, not one.** `loop.queued` filters on the watermark AND on the
derived store's own ids. Without the second filter, "a re-run buys nothing twice" would hold only
for a *completed* pass: a pass killed after writing records and before saving the cursor leaves
durable rows and an unmoved watermark, and the watermark alone would re-buy every one of them.
`test_the_queue_subtracts_rows_a_killed_pass_already_answered` is that case.

**The seam.** `send(task, rendering) -> reply dict`. `StubTransport` replaces it and **nothing
else** — the rendering, the prompt sha, the evidence table and the ordering are the production path
in a smoke exactly as in a run. The split is not stylistic: vis-b's paid boot was refused by a guard
whose stub had agreed with it, because a stub built from the same assumption as the code cannot
contradict it.

**The endpoint constant stays CLOSED.** `run_loop.ENDPOINT is None`, asserted by
`test_5a_registers_no_endpoint` and again by `test_5c2_prep_b_leaves_the_endpoint_constant_closed`,
with `test_the_guard_opens_once_an_endpoint_exists` as the negative control beside them. `--infer`
without `--smoke` asks for a SERVED pass and is refused by `loop.inference_refusal` — see Dv249 for
why the message, and not just the exit, is asserted.

**What is free to check against reality, is checked against reality.** All three the brief names
were already driven against the REAL modules by the existing suite, and I verified each rather than
assuming it:

| check | where it already lives |
|---|---|
| `serve_handler.settings` refusing an adapter variable beside `SERVING_CONFIG` | `tests/test_positions_serving.py:59`, `tests/test_vis_a_caption.py:64` (both `match="ADAPTER OFF"`) |
| the ms/s conversion in `serving.execution_policy` | `tests/test_serving.py:373` and its refusal at `:389` |
| `prompts.prompt_sha256` for the registered names | `tests/test_prompts.py:37, 93, 100, 128` |

What this contract adds on the same terms: the loop's own leg is exercised against the real
`prompts`, the real `parents` and the real `evidence` — only the network hop is a stub. `render_comment`
reaches `parents.context` and `parents.post_kwargs` rather than assembling the keywords itself, which
is what stops a run asking half its rows with a caption and half without; the smoke's own record
carries the resulting `post_states` count (`{"post_text": 5}` on the channel above).

## 5. Deliverable 2 — the record shape

**One place names the fields.** `market_pulse.evidence` — `REQUIRED` for every row and
`KIND_FIELDS` for the three kinds 3.18 (6) shows (`comment`, `leaflet_page`, `position_row`).
`record()` calls `assert_complete` on its own result before returning, so a row that could not be
shown at the sitting never reaches the disk, and `assert_complete` names **every** absent field at
once — a writer fixing them one exception at a time learns the table one field per run, and the run
that teaches it is the paid one.

**The guard is driven through the PASS, not through the builder.** Checking `record()`'s output
against the table `record()` also writes is circular.
`test_every_row_the_pass_writes_satisfies_the_evidence_table` runs the production pass and asserts
each written row satisfies `assert_complete`, that its `prompt_sha256` is
`prompts.prompt_sha256(task)`, and that the rendering contains both the comment and `<post>`. A
per-field negative control (`test_deleting_any_required_field_is_refused_by_name`, parametrised over
all eleven) proves the table discriminates rather than merely accepting.

**`presence()` and the ladder.** `src/market_pulse/positions.py` is pinned by sha256 inside
`results/sku_pilot_prereg_b2.json`, so the `Position → five booleans` mapping could not be added
there — it lives in `evidence.py`, which makes it a SECOND implementation of the ladder's own
inputs (Dv252). The drift is closed by measurement, not by a comment: 16 parametrised cases assert
`positions.tier_from_presence(**evidence.presence(p)) == p.tier()` over every combination of the
four optional fields, and one more asserts the keys ARE `positions.PRESENCE_FIELDS`. Without it the
sitting would re-derive a rung from inputs that do not produce it, and nothing in the record could
say so.

### 5.1 Dv232 — the parser warnings reach the record

They ride the **outcome row, per POSITION**, index-aligned to the parsed order:

```json
"warnings": [["multipack", "discount_footnote", "price_from"], []]
```

**Per position and not per source**, because the question hot.md says was lost is *which warning
saved which position*, and a page yields several. A per-source aggregate would have closed the
ticket without closing the defect. The dump's columns are DERIVED from B′'s sealed bar-2 sentence
and cannot grow (Dv255), so the outcome row is where this fits; `len(warnings) == n_positions` is
the invariant that holds the two lists together and it is asserted on every answered row.
`warnings is None` for a refusal — `[]` and "unreadable" are different outcomes here as everywhere
else in this record.

The run-level summary (`extraction.warnings_by_kind`, `positions_with_a_warning`) is **derived from
those per-position lists**, never counted a second time while parsing: two counters over one event
is how a summary and its rows stop agreeing without either looking wrong.

**The smoke's fake gained a warned reply (Dv253).** Before that, every position the smoke produced
warned about nothing, so the whole path from `positions.warnings()` to `extraction.warnings_by_kind`
was exercised **only on empty lists**. The new seat carries all three families at once — a multipack
size, a footnote asterisk and a «від X грн» price — and the test now demands
`set(warnings_by_kind) == {"multipack", "discount_footnote", "price_from"}`. A field proven only
where it is empty is a field nobody has seen work.

`results/sku_b_positions_skub2.json` is **not** rewritten. The skub2 run's warnings are gone and
stay gone; what changed is what the next run writes.

### 5.2 Dv176 — the `contract:` provenance

The resume arm read `docs/PROMPT-sku-b-v3-prep.md deliverable 2; docs/SPEC.md amendment 3.17 (9),
(10), (11)`. Two defects in one string: it named the **prep** contract of the session that was
REFUSED before its first gold call rather than the v4 run that bought the 121, and it omitted
**(12)** — the amendment that authorised that attempt and fixed its cap, its ledger and its fresh
anchor.

Both arms are constants now (`CONTRACT`, `RESUME_CONTRACT`) with a test on **each**, parametrised so
neither can be the one that is checked. **This is the whole reason both are tested:** the non-resume
arm was already moved at skub2-fix and its twin was left standing, so a test driving only the live
path would have covered the sibling branch and reported the fix verified. A third test asserts the
two strings are not equal — two arms that drifted into one would name a single session's contract on
both paths, which is the same defect spelled differently.

`results/sku_b_positions_v4.json :: contract` is **not** corrected. A record edited after the fact
is worse than a record that names a bug.

## 6. Assumptions stated, and what I did not touch

1. **The evidence shape binds the LOOP, not the sku driver.** D2 opens "Every row **the loop**
   writes", so `evidence.REQUIRED` governs `data/derived/`. `scripts/positions_gm4_skub.py` keeps
   its own record and dump shapes — it is the closed sku programme's instrument, its dump columns
   are derived from a sealed sentence, and re-architecting a paid driver to emit evidence rows is
   neither asked for nor safe here (Dv256). The `leaflet_page` and `position_row` kinds exist and
   are tested because 3.18 (2) puts both legs into the 5c2 loop; the leg that will fill them ships
   with the paid session's driver.
2. **`loop.inference_refusal`'s message still says "5a queues rows and sends none"** and I left it
   (Dv254). `implementation-notes.md:2189` quotes that string verbatim as the 5a smoke's output, and
   editing it would make a recorded quote stop reproducing for a cosmetic gain.
3. **No RunPod call at all.** The guard's read-only balance read was permitted and not needed:
   nothing here spends, so there is no number to bound. Phase 4 stands where prep-a left it —
   **$23.8310 of $30.00**, $6.1690 remaining.
4. **Not done, deliberately, and named:** the census, the price projection and the paid session's
   pre-registration are prep-c. No endpoint, template or serving configuration was registered. No
   write into `data/raw/`, no `RAW_STORE_SALT` rotation. No Telegram client was built. No team-lead
   file was edited and no sealed sku artifact was re-pinned — `git status --short results/` is empty
   for the whole session.

## 7. Deviations

Long form here; the index is in `implementation-notes.md`.

**Dv249 — a new guard shadowed by an older one.** `--infer` alone fell through to `LIVE_REFUSAL`
before reaching `inference_refusal`. Still a refusal, still a `SystemExit`, and for a reason that
does not apply: `LIVE_REFUSAL` is about appending to the raw v1 stores, which the inference leg
never does. `--infer` is a MODE now, and the test asserts the MESSAGE (`match="3.11 \\(2\\)"`) with
`test_a_pass_with_no_mode_at_all_is_still_the_5a_live_refusal` as the control that the older guard
did not move.

**Dv250 — `**extra` silently overrode a derived field.** `evidence.record` builds
`prompt_sha256` from `task` and spread `**extra` after it, so a caller could hand in a sha that did
not belong to the prompt it named. Found by the test written to assert the refusal *before* the
refusal existed; `record()` now refuses any extra that collides with `REQUIRED`.

**Dv251 — a deliberate STOP that raised the wrong exception.** `parents.text_for` named a missing
parent by `row["id"]`; a raw `raw_store.comment_record` is keyed `(channel, msg_id)` and has no
`id`, so the loop — the first caller reading the store directly — turned a STOP whose whole value is
its message into a `KeyError`. Fixed on touch: `row.get("id") or f"{channel}:{msg_id}"`.

**Dv252 — a second implementation of the ladder's inputs, on purpose.** See §5. Pinned by 16
parametrised cases against `tier_from_presence`, because the alternative was re-pinning a sealed
pre-registration.

**Dv253 — a fixture that never exercised what it was proving.** See §5.1.

**Dv254 — a stale phase name left in a guard message.** See §6.2.

**Dv255 — the dump's columns cannot grow.** They are derived from
`bars.price_pair_accuracy.procedure` in the sealed B′ registration, so Dv232's warnings could not
become a dump column and ride the outcome row instead. Named because a reader looking for them in
the dump will not find them.

**Dv256 — the sku driver does not emit evidence rows.** Scoping, stated in §6.1 rather than left to
be discovered.

**Dv257 — `docs/STATUS.md` arrived modified mid-session.** The team lead wrote a handover section
while D1 and D2 were being built, so it describes both as "не начаты" — true when written, before
`09b5dac` and `3232a52`. Committed verbatim with this report; a team-lead file is read-and-commit
and I edited nothing in it. The acceptance reads this report for the state, not that paragraph.

## 8. For prep-c, found and not pursued

**A prerequisite, not a finding — it needs scheduling, not noting.** Of the three row kinds the
table defines, only `comment` has a producer. `leaflet_page` and `position_row` have a schema, a
completeness guard and tests, and **no writer**: the loop's pass builds comment rows, and the sku
driver keeps its own shapes for the reasons in §6.1. So the leaflet half of the 3.18 (6) pack is
specified and unbuilt. **5c2-run must not be the contract that first produces a `position_row`** —
a paid session is the wrong place to discover that a record shape has never been written, which is
the precedent `results/predictions/LOST.md` is. The positions leg's evidence writer belongs in
prep-c or in a contract before the paid one.


- **16,218 rows** sit above the `inference` watermark across the whole registry today (§2.2). This
  is the standing backlog, **not** the 3.18 (4) window, which is pre-registered BY ROW COUNT from a
  zero-cost census.
- The `inference` watermark is **unset on every channel** — no pass has ever advanced it, so today's
  queue is the whole collected comment corpus.
- **19 channels** carry a non-empty queue and it is very unevenly spread. The enumeration, built by
  script rather than read off the printed table:

  | channel | queued | | channel | queued |
  |---|---:|---|---|---:|
  | `@VARUS_channel` | 6,410 | | `@smirnov108` | 101 |
  | `@msuaaaa` | 4,928 | | `@HealthPsycholog` | 97 |
  | `@matusi_ukr` | 2,890 | | `@sashafitnesslife` | 83 |
  | `@mandziak` | 1,048 | | `@tarilka_malyuka` | 45 |
  | `@klopotenkofood` | 232 | | `@ya_Nenka` | 16 |
  | `@kopiyochka1` | 223 | | `@mamo_nepsichuy` | 10 |
  | `@retsepty` | 105 | | 6 more | 4–8 each |

  **The top two are 70% of the backlog** (11,338 of 16,218) and the bottom six are four rows each,
  so a window drawn by row count without stratification is a window about `@VARUS_channel` and
  `@msuaaaa`. That is a prep-c decision and is not taken here.

  **How I got this wrong first, since it is the kind of error the gate exists for.** I named
  `@matusi_ukr` and `@mandziak` as the two biggest — they are the last two rows of the dry pass's
  printed table, which is registry order, not rank. A count read off the tail of a listing is not
  the enumeration; the table above is built by iterating every verified channel.
