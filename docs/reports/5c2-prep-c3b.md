# 5c2-prep-c3b — the pre-registration: the D cut, the fourth kind, the sealed numbers

**The post leg's registered population is 44 posts, not 349: `results/postcut_c3b.json` applies
3.18 (7)(g)'s D cut to the shipped census and keeps a row iff its channel is `official_retail` or
`aggregator` OR its evidence carries a `currency` pattern — zero recipe channels survive, and both
readings of the ruling's wording select exactly the same rows.** **`evidence.KINDS` has a fourth
member: `post_text`, the marker the post leg had no way to write, so an interrupted pass now re-asks
nothing it already answered and the exhausted-queue smoke went from 2 transport calls to 0.**
**5c2-run is pre-registered at `results/prereg_5c2_run.json`: 5 075 comments + 159 leaflet pages +
44 posts = $7.8546 with drift, a session cap of $8.00 against $9.1690 remaining, every number pinned
by VALUE.**

Contract: `docs/PROMPT-5c2-prep-c3b.md`. Authority: `docs/SPEC.md` amendment **3.18 (5)–(7)**,
including the operator's Dv290 ruling **(7)(g)**. **$0 session: nothing was spent, no pod, no
endpoint, no serverless job, no OpenRouter call, no Telegram client.** Phase 4 stands at **$23.8310
of $33.00**, $9.1690 remaining.

---

## Step 0 — the tail, and one report amendment

`git status --short` at the start matched the contract's list exactly — five modified paths and one
untracked one, no seventh:

```
 M docs/SPEC.md            M docs/STATUS.md          M knowledge/daily_logs/2026-08-13.md
 M knowledge/hot.md        M knowledge/index.md      ?? docs/PROMPT-5c2-prep-c3b.md
```

Two commits, staged by path, `git add -A` nowhere: `e8b31fa` (SPEC + STATUS + this prompt),
`569c918` (the three vault paths). Baseline before the first write-capable action: the whole
gitignored `data/` tree hashes
`b0151164db18b9af93d35fd64365944f139e18b09cb1d74f25f27b369d4f09d3` over 1 496 files, and
`data/derived/` does not exist. Both re-measured at the end and unchanged.

`make check` before anything moved: **2 184 passed, 2 skipped**.

### The report amendment (Dv293)

The acceptance's finding is exactly right, and the check is one command:

```
$ git show a39a8ad:results/census_c3a_posts.json | shasum -a 256
ab927a23fae51288bc464b3b3bcc4131520dde9792a4f69c3e86b93179511791
```

That is the revision §2 printed. `9c723a7` then added `producer.borrows` to the record in answer to
a review finding, moving its bytes by design, and §2 was never re-measured. Re-measured now — two
fresh runs to a scratch `--out`, so the shipped record's bytes were not rewritten to measure them:

```
4a7e755b73d6381153b422495b8cce16dc8e5a040de866539c58d46f7d87b569  det1.json
4a7e755b73d6381153b422495b8cce16dc8e5a040de866539c58d46f7d87b569  det2.json
4a7e755b73d6381153b422495b8cce16dc8e5a040de866539c58d46f7d87b569  results/census_c3a_posts.json
```

§2 amended in `1e0c89b` with the stale-revision cause named. **The class is worth naming: a verify
gate's number was written once and outlived the artifact it describes** — the same shape as Dv281
and as the session-header correction this session's predecessor caught at `/save`.

One thing the re-measurement turned up on the way (Dv294): `--anchor 2026-08-09`, a bare date, is
parsed as LOCAL time and silently produces a different window (9 160 posts, anchor
`2026-08-08T22:00:00+00:00`). `refuse_to_move_the_anchor` reads the OUT file's own anchor, so a
fresh `--out` skips the guard entirely. The run failed anyway — the selection pin disagreed on all
59 channels and `main` returns 1 — so the instrument caught what the guard could not. Not fixed:
c3a's code is shipped, its record sealed, and the pin is the stronger check.

---

## Step 0.5 — the fourth evidence kind (`24d24b5`)

The team lead's ruling on Dv285. `evidence.KINDS` grows `post_text`; `KIND_FIELDS["post_text"] = ()`
— the `comment` shape, because a post's text IS its `rendering` and there is no second artifact to
name. `REQUIRED` does not change. `n_positions` and `unreadable` ride in `extra`, as the page
marker's do.

`post_rows` appends the marker LAST per post and `queued_posts` keys on `POST_RECORD_TYPE` instead
of the position rows. The marker carries no `row_id`, so `raw_store.dedup_key` returns its msg_id —
the house pattern, read out of `leaflet_page` before writing.

### Both directions, measured

| what | measurement |
|---|---|
| the c3a scenario, planted unchanged | three posts, the middle two finding nothing, cursor never saved → `queued_posts` returns **`[]`** |
| the negative control, in the same test | the OLD key (`POST_POSITION_RECORD_TYPE`) on the SAME store still yields **`[4341, 4342]`** |
| the sibling leg, unchanged | the same kill with the same three answers on the page leg: `[]`, as it always was |
| the order | a store that dies after the first file leaves both positions and **no marker**, and the post is still queued |
| the collision | appending the same post's rows twice: `dedup_key` reads `['…:4340:0', '…:4340:1', 4340]` and the second append adds **one of nothing** |
| the exhausted-queue smoke | `transport_calls` **2 → 0**, `asked` **2 → 0**, derived store byte-identical |

The negative control is the part that matters. Without it "the queue is empty" and "the store is
empty" look the same, and the test would pass on a store that never wrote anything at all.

### The smoke, on the real corpus

```
PYTHONPATH=src python3 scripts/run_loop.py --once --smoke --posts \
  --channel @atb_market_official --limit 400

run 1:  stub-served @atb_market_official  27 posts, 21 positions, 7 unreadable, 6 empty, wm 2465
run 2:  stub-served @atb_market_official   0 posts,  0 positions, 0 unreadable, 0 empty, wm None
```

Dv266's lesson applied: the queue is EXHAUSTED (`--limit 400`) before the re-run, so the second run
is measuring idempotence and not the next five rows. `results/smoke/derived` hashes
`052938b4…` before and after run 2; `data/loop_cursor.json` byte-identical (`10989c43…`);
`data/derived/` never created.

### Three sentences that would have stayed green (Dv298)

Only the two tests the contract named went red. What did not:

* `post_pass`'s summary comment said the two no-row outcomes are counted apart in the summary
  "because the disk cannot tell them apart afterwards" — false the moment the marker exists;
* `queued_posts`' whole docstring documented a gap that is now closed;
* `if rows:` in `post_pass` became a dead branch.

And one gap in the suite itself: **`tests/test_evidence.py` never asserted the MEMBERSHIP of
`KINDS`.** A fourth kind was added and everything stayed green. A literal enumeration is now there —
the "law that grows loudly" pattern — so a fifth costs one line and a reader.

---

## Deliverable 1 — the D cut, computed and pinned (`2bdb53f`)

`scripts/postcut_c3b.py` → `results/postcut_c3b.json`. The shipped census is an INPUT, pinned by
sha256, and its bytes were never touched.

```
349 passed the pre-filter → 44 kept (12.6%) across 10 channels
  by reason: {'carrier_only': 15, 'currency_only': 13, 'both': 16}
  declined:  {'all_that_pass': 349, 'carriers_only': 31, 'currency_only': 29}
  priced at 2.8132 s/row → $0.0581 with drift
  magnitude check 44 against [50, 55]: OUTSIDE — reported, not a stop
  the two readings of «matched evidence» agree: True
  recipe rows removed: 270 (the ruling's four: 250) · kept from them: 0
```

| channel | source_type | passed | kept | by |
|---|---|---|---|---|
| @VARUS_channel | official_retail | 9 | 9 | carrier 9, currency 4 |
| @telegraf_kremenchuk | community | 9 | 8 | currency 8 |
| @epicentrk_sale | official_retail | 6 | 6 | carrier 6 |
| @ekomarket_shop | official_retail | 5 | 5 | carrier 5, currency 5 |
| @forainfo | official_retail | 4 | 4 | carrier 4, currency 4 |
| @gorishnie_plavni1 | community | 4 | 4 | currency 4 |
| @marketopt_promo | official_retail | 4 | 4 | carrier 4 |
| @silposilpo | official_retail | 2 | 2 | carrier 2, currency 2 |
| @kremen_news | community | 1 | 1 | currency 1 |
| @msuaaaa | aggregator | 1 | 1 | carrier 1, currency 1 |

### The magnitude check: 44, not 50–55 (Dv295)

**Reported, not a STOP, and the arithmetic is why.** The contract's range is 31 + 29 minus a small
overlap. The overlap is **16**, not the ~5–10 that implies, because currency-bearing rows cluster in
exactly the retail and aggregator carriers the first half already keeps — which is the coherence
3.18 (7)(g) rests on, so the miss is evidence FOR the ruling.

What the range protects is the registered cap. 44 rows and 55 rows differ by 31 seconds at
2.8132 s/row — under two cents — and the cap is rounded UP to the next half dollar. **Both ends were
computed before deciding not to stop: $8.00 at 44 and $8.00 at 55.** Nothing downstream moves.

### Two readings of the ruling's wording, closed by measurement (Dv296)

3.18 (7)(g) says "its matched evidence carries the `currency` pattern"; the contract operationalises
it as `"currency" ∈ pattern_kinds`. Those are not the same question — `pattern_kinds` is the kinds
found ANYWHERE in the post's text, and the wording points at the matched LINE. Both computed:

| reading | rows carrying currency | the cut |
|---|---|---|
| anywhere in the text (`pattern_kinds`) | 29 | 44 |
| the matched line alone | 29 | 44 |

They select exactly the same rows, so the ambiguity is closed. The contract's reading is also the
field behind the 29 the ruling cites, which is the tie-break. The producer **exits non-zero** on a
population where they part, and the test plants one to prove the refusal fires.

### One number in the ruling is a floor (Dv297)

"250 of 349 rows from four cooking channels" names the top four of the concentration table
(85 + 72 + 52 + 41, cumulative share 0.7163). The `cooking_recipes` audience has **six** channels
with a pass and **270** rows between them. The cut removes all 270 — the clause understates what it
removes and is not contradicted by it. Found because a test asserted 250 and went red.

Of the 44 kept: 30 `retail_official`, 13 `regional`, 1 `supermarket_deals`. The 13 regional rows are
kept by the currency half — they carry a price on the line that fired. **That is what makes
`POST_PRICE_ORIGIN`'s inheritance of skub2's `retail_leaflet` defensible: recipe carriers no longer
reach it.**

---

## Deliverable 2 — the pre-registration of 5c2-run (`0e390ff`)

`scripts/write_prereg_5c2.py` → `results/prereg_5c2_run.json`.

```
`make check` green: True · 9 inputs pinned

leg              rows  $ with drift    seconds
----------------------------------------------
comment          5075        7.4840    21928.7
leaflet_page      159        0.3125      989.4
post_text          44        0.0581      183.8
TOTAL                        7.8546    23101.9

session cap $8.00 (projected $7.8546, rounded up to the next $0.50)
  remaining $9.1690 under the $33.00 cap — fits: True, headroom $1.1690
  the ledger's own remaining_usd reads $6.1690 under the $30.00 cap it was written beside
  wall clock 6.42 h · 26 jobs at 900 s
```

**Pinned by VALUE, per 3.18 (7)(f).** `tests/test_prereg_5c2.py` carries one equality per registered
number — 5075, 159, 44, 1.4281, 4.262, 4.2794, 2.8132, 8.00, 7.8546, 9.1690, 1.1690, 23101.9, 6.42,
26 — and `session_cap.fits` is asserted BESIDE them, never in place of them. A suite carrying only
`cap <= remaining` would pass on any cap under $9.1690, which is the defect the clause was written
about.

**Selections, not only sizes.** The comment leg is pinned by the **nineteen** per-channel
`ids_sha256` the census records, re-checked against the census itself; a hash-of-hashes would be a
number nothing else in this repo — least of all the run — could rebuild. The post leg is pinned by
the kept ids' own hash, so a run that asked 44 OTHER posts would not match.

### The field that could not be used (Dv299)

`spend_phase4.json :: sessions[-1].remaining_usd` reads **6.1690**. It is not wrong — it is a true
statement under the 30 cap it was written beside, and 3.18 (7)(b) forbids re-scoring it.
`projection_5c2.budget()` reads that field, so reusing it would have **refused an $8.00 cap that
fits with $1.1690 of headroom**. The producer derives `PHASE_CAP_USD - spent_usd` = **9.1690** and
prints both, each with the cap it answers under. Same class as Dv283: a field whose truth is fixed
to a moment, read as if it were current.

### Two supersessions, one paragraph

A reader meets `$7.6870 fits: false` in the c2 projection and `$7.8546 fits: true` here — a LARGER
number that fits, which reads as an error unless one block says both things. The leaflet leg's
population moved **78 → 159** (3.18 (7)(d): the corpus on disk, not the window intersection) and the
phase cap moved **30 → 33** (3.18 (7)(b)). Neither record corrects the other; `projection_5c2.json`
is a true statement of its write moment and was not regenerated.

### The registered law keeps all ten blocks (Dv300)

B′ keeps two — the blocks that authorise it. This registration keeps **all ten** the file carries,
because 3.18 (7)(c) sends the run's stop rules to **3.17 (10)**, which lives inside
`sku-b-ratification-4`: a pin that stripped it would register a document that does not carry the
discipline the record names. Keeping all ten means the pin equals the raw file TODAY, and the
strip's job starts the day they diverge — a block added later is taken off and the pin survives.

The producer refuses on a block SET that is not exactly those ten, which is stronger than trusting
the name expression: `amendment-3\.\d+` matches a future `amendment-3.19` and would strip it
silently. **The constraint that puts on the team lead:** new text arrives inside its own marked
block, and a sealed registration is never re-pinned to make it green.

### The refusals, measured

| refusal | how it was measured | the message |
|---|---|---|
| a red suite | injected verdict, `returncode 1` | `` `make check` exited 1 … `` and **no file written** |
| the command is real | `CHECK` greps back to the Makefile's `check:` body (`ruff check .`, `pytest -q`) | an injected runner proves the branch, not the command |
| the cut over another census | `postcut.input.sha256` moved | "does not belong to the census this registration pins" |
| a producer moved under its record | `producer.borrows` entry moved | "was written by code that has changed since" |
| an eleventh marked block | a copy of SPEC with `amendment-3.19` appended | "add its name here and look at it" |
| a sealed record re-pinned | an existing record whose `pinned_inputs` moved | "is not re-pinned to make it green" |

### Two things the record had to be built around

**Dv301 — the verifier block cannot carry pytest's last line.** It holds the run's DURATION, and
byte-identity is this record's gate; the tail is returned beside the block and printed only in the
refusal message. Found by the determinism pair failing on its first attempt.

**Dv302 — the test module reads the record at import**, so it cannot be present the first time the
record is written: the producer runs `make check`, the suite collects the test, the test cannot find
the file. Bootstrapped by holding the module aside for one run, then re-running with it in place.
The record is byte-identical across both, so the shipped `verifier.green` describes a suite that
includes its own equalities.

---

## Deliverable 3 — the RECORD (`e64398d`)

`knowledge/decisions/the-d-cut-and-the-fourth-kind.md` + its INDEX line: the rule and both things in
it that needed reading (the carrier field, the two readings), the three declined alternatives
re-counted rather than quoted, why `POST_PRICE_ORIGIN`'s inheritance is now defensible, and the
fourth kind with its both-directions measurements. Every number in it was re-derived from the
records by a script before the commit — two dollar figures were wrong on the first pass (0.0470 /
0.0453 against the record's 0.0465 / 0.0447) and are fixed.

The c3a ADR needed no change: it cross-references (7)(g) as "the pre-registration's" and that is
still what happened.

---

## Verify gate

### 1. `make check` after every commit

Each commit checked out into its own detached worktree with the gitignored `data/` entries linked
per ENTRY (c3a's repaired instrument, Dv191/Dv193 — a symlink at `data/` lands INSIDE as
`data/data` because `data/` is only PARTLY tracked, and every row then reads `1 error`, which is a
broken instrument and not a measurement).

| commit | subject | result | failing |
|---|---|---|---|
| `e8b31fa` | docs: 5c2-prep-c3b queued | 1 failed, **2183** passed, 2 skipped | `test_collect_5c1.py::test_the_guard_reads_the_pinned_paths_off_the_pin_file` |
| `569c918` | docs(vault): the c3a session tail | 1 failed, **2183** passed, 2 skipped | the same one |
| `1e0c89b` | docs(report): c3a §2 re-measured | 1 failed, **2183** passed, 2 skipped | the same one |
| `24d24b5` | feat: the fourth evidence kind | 1 failed, **2188** passed, 2 skipped | the same one |
| `2bdb53f` | data: the D cut computed | 1 failed, **2210** passed, 2 skipped | the same one |
| `0e390ff` | data: the pre-registration of 5c2-run | 1 failed, **2234** passed, 2 skipped | the same one |
| `e64398d` | docs(decision): the D cut and the fourth kind | 1 failed, **2234** passed, 2 skipped | the same one |
| **`ba1cf7d`** | **control** — the last commit BEFORE this session | 1 failed, **2183** passed, 2 skipped | the same one |

**The control is the row that makes the table a measurement.** It reads 2183 — the same as this
session's three documentation commits and 51 below its end — so the instrument is reading each
commit rather than reporting a constant, and the one failure is a property of the WORKTREE and not
of any commit here: `test_collect_5c1.py::test_the_guard_reads_the_pinned_paths_off_the_pin_file`
resolves pinned paths against the checkout it runs in. Re-measured this session rather than
inherited from c3a's sentence about it (Dv193).

Each worktree row is `1 failed + N passed`, so the totals are 2184 / 2189 / 2211 / 2235 — which is
what `make check` reads in the repo itself at each of those points, green.

The last two commits (`docs(report)` and the vault tail) are documentation only and postdate the
table; each has its own `make check` at commit time, quoted in the commit list below.

### 2. The two new records' determinism pairs

```
13bb475864fdd4f476237293aa279fffa5b07dd87b80820c71c65444d8321ad0  cut1.json
13bb475864fdd4f476237293aa279fffa5b07dd87b80820c71c65444d8321ad0  cut2.json
13bb475864fdd4f476237293aa279fffa5b07dd87b80820c71c65444d8321ad0  results/postcut_c3b.json

d5d3afd5e6d7e966233a7e449546b2001f9c2a08646cab207e87531f5df4cbc8  pr1.json
d5d3afd5e6d7e966233a7e449546b2001f9c2a08646cab207e87531f5df4cbc8  pr2.json
d5d3afd5e6d7e966233a7e449546b2001f9c2a08646cab207e87531f5df4cbc8  results/prereg_5c2_run.json
```

Both measured **after** `ruff format` last touched their producers (Dv288's lesson, applied without
having to re-learn it), and both runs went to a scratch `--out`, so neither shipped record was
rewritten to measure it. The third line of each pair is the file on disk.

### 3. The fourth kind in both directions

Above, under Step 0.5 — six measurements, including the old key planted as the negative control and
the exhausted-queue smoke at 0/0.

### 4. The registration's refusal

Above, under Deliverable 2 — six refusals, each with the message it prints.

### 5. `git log --oneline` and a clean tree

```
e8b31fa docs: 5c2-prep-c3b queued -- the D cut in law (SPEC 3.18 (7)(g))
569c918 docs(vault): the c3a session tail
1e0c89b docs(report): c3a §2 -- the determinism pair re-measured after 9c723a7
24d24b5 feat(5c2-prep-c3b): the fourth evidence kind -- post_text, the marker the post leg had no way to write
2bdb53f data(5c2-prep-c3b): the D cut computed -- 44 of 349, and the ruling's four channels are 270 rows
0e390ff data(5c2-prep-c3b): the pre-registration of 5c2-run -- three populations, three prices, an $8.00 cap
e64398d docs(decision): the D cut and the fourth evidence kind
<this report>  docs(report): 5c2-prep-c3b
<the tail>     chore(vault): the 5c2-prep-c3b session tail
```

`make check` green immediately before this report's commit: **2 235 passed, 2 skipped**.
`ruff format --check .`: **262 files already formatted** — run separately, because `make check`
does not include the formatter.

After the tail commit the tree is clean apart from what the Stop hook regenerates
(`knowledge/index.md`).

---

## Do NOT — what was not done

* **Nothing was spent.** No endpoint, template or serving config registered; `run_loop.ENDPOINT` is
  still `None`. No Telegram client. **5c2-run was not started** — the run is its own session under
  the sealed registration.
* **`results/census_5c2.json`, `results/projection_5c2.json` and `results/census_c3a_posts.json` are
  byte-identical**, and no record written under cap 30 was regenerated. The census's identity is
  asserted three ways: the determinism pair above, `postcut_c3b.json :: input.sha256`, and the
  registration's `pinned_inputs`.
* **`evidence` changed by exactly what Step 0.5 names** — one `KINDS` member and one `KIND_FIELDS`
  row. `REQUIRED` is untouched, checked on the TUPLE and not on the line that assigns it (a field
  added or removed inside the parens would move neither the assignment nor a grep for its name):

  ```
  $ git show ba1cf7d:src/market_pulse/evidence.py  →  ('row_kind', 'at', 'channel', 'msg_id',
      'parent_msg_id', 'task', 'prompt_sha256', 'model_revision', 'served_by', 'rendering', 'reply')
  $ HEAD                                           →  the same 11, in the same order
  ```

  `src/market_pulse/positions.py` untouched, the sealed sku artifacts and the team-lead files
  untouched, `RAW_STORE_SALT` not rotated.
* `data/` unchanged: `b0151164…` over 1 496 files at the start and at the end; `data/derived/` never
  created.

## Deviations

`implementation-notes.md` § *5c2-prep-c3b* — **Dv293–Dv302**, every one with a `[cause: …]` tag.
Three a reader should not skip: **Dv295** (44 rather than 50–55, and why it is not a stop),
**Dv299** (the ledger field that would have refused a cap that fits) and **Dv300** (the strip family
this registration keeps, and what it asks of the team lead).

## Process signals

* The acceptance's own finding (Dv293) is a class, not an incident: a verify-gate number written once and outlived by its artifact. Third instance TODAY (Dv281, the c3a session header, this one) — the fix belongs in the gate, not in the report.
* The contract's expected magnitude was off by the overlap it could not know (Dv295). Naming what the range PROTECTS turned "STOP or not" into arithmetic instead of judgement.
* SPEC and the contract operationalised (7)(g) differently (Dv296). Computing both and finding they agree costs less than choosing — and the producer now refuses where they would part.
* A ruling's count can be a floor (Dv297): "250 from four channels" is the top four; the audience is 270 across six. Found only because a test asserted the quoted number.
* `tests/test_evidence.py` never pinned the MEMBERSHIP of `KINDS` (Dv298) — the fourth one landed green. Enumerations that grow loudly need to exist BEFORE the thing that grows.
