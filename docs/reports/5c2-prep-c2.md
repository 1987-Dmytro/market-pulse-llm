# 5c2-prep-c2 — the money track: the census, the projection, and a STOP with numbers

**Contract:** `docs/PROMPT-5c2-prep-c2.md` · **Spend:** $0.00 · **Date:** 2026-08-13

Three plain sentences, first:

1. The 4-week window is no longer a phrase — it is 5 075 unanswered comments, 9 158 posts,
   5 773 of them with media, and 78 downloaded leaflet pages, counted per channel from one
   recorded anchor and reproducible byte for byte from it.
2. Both legs of the paid session now have a price that came off a session that actually paid on
   the serverless runtime, with the file and the field printed beside every figure.
3. And the answer is that **the whole window does not fit**: $7.6870 with drift against $6.1690
   left in the phase, which is why this contract ends at a STOP and writes no pre-registration.

---

## Step 0 — the tail

`git status --short` showed the five paths the contract named, and nothing else. Two commits,
staged by path:

| commit | subject | paths |
|---|---|---|
| `86757dd` | `docs: 5c2-prep-c2 queued — STATUS after the prep-c1 acceptance` | `docs/STATUS.md`, `docs/PROMPT-5c2-prep-c2.md` |
| `60067a2` | `docs(vault): the prep-c1 session tail` | `knowledge/daily_logs/2026-08-13.md`, `knowledge/hot.md`, `knowledge/index.md` |

`make check` was green before the first of them: **2103 passed, 2 skipped**.

**One path appeared later that neither list explains** — `docs/reviews/` (untracked), holding
`2026-08-13-process-audit-and-self-improvement.md`, written at 14:00 while this session was
running. It is an operator document about the team-lead/executor process, in Russian, by an
external audit. It is not this contract's, it is not the executor's, and it is **left untracked and
unedited**: it is named here so it is not mistaken for something this session forgot.

---

## Step 0.5 — `image_path` goes repo-relative (Dv264, team-lead ruling)

`run_loop.pages_of` emitted `str(REPO_ROOT / image["file"])`, so every evidence row carried this
laptop's directory layout — in a row the 3.18 (6) sitting has to open months later, on a tree that
may have been cloned or moved by then.

The record now stores the manifest's own repo-relative string, and `loop.page_file` resolves it
against `loop.REPO_ROOT` at read time. `REPO_ROOT` in the package is the house pattern —
`raw_store`, `provenance` and `telegram_client` each carry the same line — rather than a `root=`
parameter that exists only so a test can pass something else. `image_sha256` is untouched: it is
still the row's identity.

**The four consumers the contract enumerated, and what each needed:**

| file | needed | done |
|---|---|---|
| `src/market_pulse/loop.py` | resolve at read time | `REPO_ROOT` + `page_file`, called by `page_pass` |
| `src/market_pulse/evidence.py` | field name only | **no change** — verified: the table checks presence, never the path's shape |
| `scripts/run_loop.py` | emit repo-relative | `pages_of` returns `image["file"]`; existence is still checked against `REPO_ROOT` |
| `tests/test_evidence.py` | adjust the assertion inspecting the path | **no change needed** — `test_a_leaflet_page_row_needs_its_image_and_sha` asserts the field is REQUIRED, with `image_path="p.jpg"`; it never looks at the shape |

`tests/test_loop.py` got a **new** test rather than an edited one, and that is the point of it:

```python
def test_pages_of_emits_the_manifests_repo_relative_path(monkeypatch, tmp_path):
    ...
    assert [page["path"] for page in found] == [f"media/atb_{i}.jpg" for i in range(4340, 4345)]
    for page in found:
        assert not Path(page["path"]).is_absolute()
        assert loop.page_file(page).read_bytes()
```

`loop.page_file` is `REPO_ROOT / path`, and pathlib makes that a **no-op on an absolute path** — so
a producer that went back to absolute paths would keep every other test in the file green. The old
assertion `row["image_path"].endswith("atb_4340.jpg")` is true under both shapes, which is how the
defect shipped in the first place; the script-level assertion is now EQUALITY against the exact
repo-relative string.

**Measured in both directions.** With `pages_of` put back to the absolute form:

```
>       assert [page["path"] for page in found] == [f"media/atb_{msg_id}.jpg" ...]
E       AssertionError: assert ['/private/va...atb_4344.jpg'] == ['media/atb_4...atb_4344.jpg']
>       assert [page["image_path"] for page in pages] == [
E       AssertionError: assert ['/private/va...atb_4344.jpg'] == ['media/atb_4...atb_4344.jpg']
FAILED tests/test_loop.py::test_pages_of_emits_the_manifests_repo_relative_path
FAILED tests/test_loop.py::test_the_stub_served_page_smoke_writes_a_page_row_and_its_position_rows
2 failed, 52 passed
```

and after the revert, `54 passed`.

**No rows were migrated because none exist:** `data/derived/` is absent (checked before and after
every run in this session), and the smoke sandbox is throwaway. It was cleared and re-run once, at
`--limit 400`, so every number below comes from ONE invocation:

```
stub-served @atb_market_official      159 pages,  120 positions, 40 unreadable, watermark now 4526
```

159 pages = 40 unreadable + 39 empty + 80 with positions; the two files hold 159 and 120 lines.
The first page row now reads:

```
image_path:   data/annotation/captions_5c1/posts_media/atb_market_official_4340.jpg
image_sha256: 7ae55c29dc8d0adce4cec35cc3d4300ec696fe9f32141d7e34f6368054ec5002
```

resolved from the repo-relative string, the sha of those bytes matches, and it is the same sha
`results/post_media_5c1.json` pinned when 5c1 downloaded the file.

---

## Deliverable 1 — the census

`results/census_5c2.json`, written by `scripts/census_5c2.py`, 18 tests in
`tests/test_census_5c2.py`. No number downstream of it is hand-typed.

### The anchor

```
PYTHONPATH=src python3 scripts/census_5c2.py --anchor 2026-08-09T00:00:00+00:00
window 2026-07-12 .. 2026-08-09 (28d, anchor 2026-08-09T00:00:00+00:00)
```

`--anchor` is **required and has no default**. A default read from the clock would make two runs of
the same census two different artifacts, and the re-run is the census's own gate. `since <= date <
until`, half-open, so the window counts exactly 28 days.

**Why this anchor.** The newest record anywhere in `data/raw/` is dated 2026-08-08, so this is the
corpus's own last day + 1. The reasoning is `yield_screen_5c1.window_for`'s, quoted from its
docstring: screening over a window the store does not reach "would measure the collection
schedule". A window ending today buys five days no channel has collected into and drops five that
hold rows. **It is the operator's to overturn at the STOP**, and the record prices the
alternatives rather than arguing for the choice:

| anchor | window | posts | with media | comments | leaflet posts | leaflet pages |
|---|---|---:|---:|---:|---:|---:|
| **2026-08-09** (scored) | 07-12 … 08-09 | **9 158** | **5 773** | **5 075** | **9** | **78** |
| 2026-08-14 (today) | 07-17 … 08-14 | 7 621 | 4 692 | 3 927 | 5 | 45 |
| 2026-07-28 (the leaflet corpus) | 06-30 … 07-28 | 5 848 | 3 788 | 3 677 | 19 | **159** |

The leaflet column is the one that moves most: 45 / 78 / 159. That is not a reason to pick an
anchor — it is the trade the operator is entitled to see before ruling.

### Determinism, the census's own gate

```
$ PYTHONPATH=src python3 scripts/census_5c2.py --anchor 2026-08-09T00:00:00+00:00
a1384a12bcbe975954f8feaa1c5207d59cc66ab524b3d877099bad92ede5305f  results/census_5c2.json
$ PYTHONPATH=src python3 scripts/census_5c2.py --anchor 2026-08-09T00:00:00+00:00
a1384a12bcbe975954f8feaa1c5207d59cc66ab524b3d877099bad92ede5305f  results/census_5c2.json
```

It did not hold on the first attempt, and the failure is worth stating because it is a class:
**the record carried a `git` block**, every other record in this repo does, and `git_state` embeds
`git status --porcelain`. The census hashed `ec35644b` when it was written and `cbc05c84` after an
unrelated commit landed — same anchor, same data, different bytes. Provenance is now the producing
script's own sha256 (`producer.sha256`), which answers "which code wrote this" more precisely than
a commit id does: a commit id does not say the file was not dirty when it ran. The second pair of
hashes above brackets a working-tree change.

Both halves are pinned by tests, and both read the **AST** rather than grepping, because the
module's own docstrings argue about `datetime.now()` and `git_state` in prose:

```python
assert not called & {"now", "utcnow", "today", "time"}, "the census reads no clock"
assert "git" not in record
```

Negative control, measured: with a `generated_at` added, `test_the_same_anchor_reproduces_the_
artifact_byte_for_byte` and `test_the_record_carries_no_clock_of_its_own` both go red.

### What it counts, and where it refuses to

Scope is the **66 registry channels** — the loop walks `registry.sources` (`run_loop.channels_of`),
so a store file with no registry entry is invisible to every number the paid session will produce.
Those files are counted apart: 16 post stores and 1 comment store, the latter `@tretyakovaele` with
106 rows.

`posts_with_media` is `scripts/image_census_5c1.py`'s own definition — the stored `has_media` flag,
which is `message.media is not None` merged across an album by `raw_store.collapse_albums` — reused
rather than re-derived, because a second definition would be a second opinion about the corpus.

`CANNOT ANSWER` is written where the store cannot answer, and the record splits it by cause,
because "never read" and "read, produced nothing" are different facts:

| cell | n | what it is |
|---|---:|---|
| posts | 7 | channels with no file in `data/raw/posts/` — never walked |
| comments · no discussion group | 40 | `comments_enabled: false` — cannot produce a comment at all |
| comments · watch, never joined | 6 | the group exists and is deliberately not joined |
| comments · **collection gap** | **1** | `@eftforhealth` — comments enabled, not a watch, never read |

Only the last is a gap. It goes in this report and nothing was fetched, per the DO NOT.

Every in-window comment is unanswered, and that is read off the cursor rather than assumed:
`watermarks.inference_set_on` and `leaflet_set_on` are both **empty lists** — no channel has ever
had either watermark set.

### Composition — the concentration question, enumerated

Comments in the window — **all 19 channels that have any**, not the top of the table, because the
clause asks for the composition "answered by enumeration, not by reading the tail of a printed
table":

| channel | comments | share | cumulative |
|---|---:|---:|---:|
| `@matusi_ukr` | 2 717 | 53.5% | 53.5% |
| `@mandziak` | 1 026 | 20.2% | 73.8% |
| `@VARUS_channel` | 242 | 4.8% | 78.5% |
| `@kopiyochka1` | 223 | 4.4% | 82.9% |
| `@klopotenkofood` | 222 | 4.4% | 87.3% |
| `@msuaaaa` | 163 | 3.2% | 90.5% |
| `@retsepty` | 104 | 2.1% | 92.5% |
| `@smirnov108` | 100 | 2.0% | 94.5% |
| `@HealthPsycholog` | 97 | 1.9% | 96.4% |
| `@sashafitnesslife` | 83 | 1.6% | 98.1% |
| `@tarilka_malyuka` | 45 | 0.9% | 99.0% |
| `@ya_Nenka` | 16 | 0.3% | 99.3% |
| `@mamo_nepsichuy` | 9 | 0.2% | 99.5% |
| `@polyakova_fitness` | 8 | 0.2% | 99.6% |
| `@chifit_family` | 4 | 0.1% | 99.7% |
| `@denisovapro` | 4 | 0.1% | 99.8% |
| `@kkondr_fit` | 4 | 0.1% | 99.8% |
| `@olgaa_trainer` | 4 | 0.1% | 99.9% |
| `@useful_healthy_fitness_menu` | 4 | 0.1% | 100.0% |

**Two channels are 73.8% of the comment window, and neither is a retailer.** Posts are the
opposite — flat and regional: `@poltava20` 16.2%, `@poltava_informue` 13.9%, and the top six are
53.2% between them.

### Leaflet coverage — the number the ATB-only default is measured against

| | in the window |
|---|---:|
| posts with media, all channels | **5 773** |
| of them, with a page on disk | **9** |
| posts with media and **no page anywhere** | **5 764** |
| posts with media **in channels with no page at all** | 5 760 |
| channels with any downloaded page | **1** (`@atb_market_official`) |
| ATB: posts with media | 13 |
| ATB: posts with pages downloaded | 9 |
| ATB: pages downloaded | 78 |

Those two middle rows are four apart and they are different questions — the second one does not
count ATB's own four uncovered posts. Both are in `leaflet_coverage.gap` rather than subtracted in
this report, because the first draft of this table put the second number under the first one's
label and only the re-derivation script caught it. The gap is not only across channels: it is
**4 posts wide inside ATB as well**. The manifest was checked against the store before any of this
was counted: 19 entries, 0 missing, 0 date drift.

### Cross-check — corpus-level, and labelled as such

The census re-derives **16 218** comments stored for registry channels. That is the number
`docs/reports/5c2-prep-b.md`'s dry pass reported over the same channels, and the 106-row difference
against everything on disk is `@tretyakovaele`, which the registry does not carry. It is **not** a
window number — the dry pass has no window — and the record says so in the same block:
the window's own figure is 5 075, and the two are different questions.

**And 16 218 is not SPEC 3.18 (4)'s "full 11 338-row history" either.** 11 338 is the v1 corpus:
`@VARUS_channel`'s 6 410 comments plus `@msuaaaa`'s 4 928, the five original channels STATUS records
as «11 338 комментов + 6 057 постов из 5 каналов». The other 4 880 arrived with 5c1's collection of
new channels, and the amendment's sentence predates them. The deferred decision it names is still
the same one; the number attached to it has moved, and this report does not restate it.

---

## Deliverable 2 — the projection

`results/projection_5c2.json`, written by `scripts/projection_5c2.py`, 18 tests in
`tests/test_projection_5c2.py`. Every figure enters through `cite()`, which READS it out of the
file by the dotted path the record prints; the test re-resolves all of them with a **second
implementation** of the resolver, and the walk is over the whole record, so a citation added later
is checked by the same loop.

### Every projected number, beside the line it came from

| value | source |
|---:|---|
| `0.00030669` | `results/srv2d_cost.json :: rate.usd_per_second` |
| `1.4281` | `results/srv2d_cost.json :: measured.usd_per_1000_rows` |
| `4.262` | `results/srv2d_cost.json :: measured.like_for_like_seconds_per_row` |
| `239.022` | `results/srv2d_cost.json :: inputs.cold_start_seconds_measured_on_this_endpoint` |
| `400` | `results/parity_srv2.json :: diagnostics.failures[0].rows` |
| `4.2794` | `results/sku_b_positions_skub2.json :: projection.per_gate[-1].marginal_seconds_per_call` |
| `230.118` | `results/sku_b_positions_skub2.json :: projection.boot_seconds` |
| `18.811` | `results/sku_b_positions_skub2.json :: projection.warmup_seconds` |

and the quoted line, from `docs/reports/skub2-run.md`:

```
page leg   462.173 s over 108 calls = 4.2794 s/page   $0.1417
```

`(711.102 − 248.929) / 108 = 4.2794`, which is the cited field exactly.

**That quote was wrong before it was right, and the way it was caught matters.** `quote_line` was
given the needle `"page leg"`, which matches the PACKING line of the same report — «108 pages sent
(of 159 available, 19 posts) in 7 job(s), largest 7.99 MB» — and it took the first match. A true
quote, sitting beside a number it says nothing about, with a green test under it (the test only
asked whether the line was in the file). It was found by printing every citation and reading them.
`quote_line` now **refuses on anything but exactly one match**.

### The comment leg — two corners, because the file gives two

| corner | rate | 5 075 rows |
|---|---|---:|
| unit cost (conservative) | $1.4281 / 1 000 rows, srv-2d's own boot inside it | **$7.4840** with drift |
| marginal + boot | 4.262 s/row + a 239.022 s cold start + the 60 s tail | $6.9271 with drift |

Both come from `results/srv2d_cost.json`, the cost record of the srv-2d session — 758 rows on the
serverless endpoint `hbq25reui1tpj6`, paid, `results/spend_srv2d.json` naming $1.2332 cumulative at
its close. Two caveats the file itself supplies and the record carries:

* **it is a FLOOR** — `caveat_dv33`: "the RunPod balance delta lags the resource by minutes and the
  itemised ledger by hours … Every figure here is a FLOOR";
* **it is blended** — 400 comment rows, 250 post rows and 108 holdout rows, while this window is
  pure T1. The smoke's own per-row seconds give the direction for free: T1 5.176 / 4.319 / 4.368 /
  4.408 against T2 3.978 / 3.903 / 3.991 / 3.958, n=4 each. The comment task is the **slower** of
  the two, so a blended rate under-prices this window rather than over-pricing it.

### The third row type — in scope, unpriced, and bounded

The operator's ruling of 13.08, as STATUS records it, scopes «комменты + **посты** + листовки того
же окна», and SPEC 3.18 (2) admits the TEXT TIER leg (bar 3, 0.8667) into the 5c2 loop. This
contract's Deliverable 2 named two legs and two candidate sources, and it is priced as two — but a
two-leg total printed with no mention of the third reads as the whole bill, so the third is in the
record as `posts_in_scope_and_unpriced`: a **bound**, entering no row and no cap.

* **9 158 posts × 2.8132 s/row + one idle tail = 25 823.3 s = $8.1573 with drift, 7.17 h.**
* The rate is skub2's own **text leg** — 30 rows, serverless, paid — derived by
  `write_sku_projection_b2.text_marginal` (the house function, reused rather than rewritten)
  and quoted from that session's report: `text leg    84.398 s over  30 rows  = 2.8133 s/row
  $0.0259`. The fourth decimal differs by rounding, not by measurement.
* It is a **bound in both directions of wrongness**: an upper bound on the population (skub2 sent
  30 PRE-FILTERED rows, not every post it had) and a lower one on the fixed cost (no boot).
* **There is no writer.** `market_pulse.loop` has `inference_pass` and `page_pass` and nothing that
  asks a post's text — asserted by a test, not claimed in prose. A post leg is unbuildable in
  5c2-run without code that does not exist, which is a team-lead question and not a deviation.

**With the bound beside the two legs, the window is ~$15.84 against $6.1690 — 2.6×, not 1.25×.**

### The leaflet leg

78 pages × 4.2794 s + 230.118 s boot + 18.811 s warm-up + 60 s idle tail = **642.7 s = $0.2030**
with drift. The briefing says the skub2 session "bought 138 pages"; `population` in its own record
says **138 SOURCES — 108 pages and 30 text rows** (Dv273). The marginal used is the in-run gate
whose `calls_done` is that 108, which is the reading the cap stop itself acted on.

### Seconds beside dollars — and the job shape

One worker (`workersMax: 1`), a 900 s execution timeout (`positions_gm4_skub.JOB_TIMEOUT_S`, sized
by SPEC 3.17 (10)(c) so no single job can bill past a remaining cap). The seconds are serial, so a
cap that fits in dollars can still name a session that does not fit in a sitting:

| cap | leaflet pages | comments (conservative) | $ at that rate | hours | jobs |
|---:|---:|---:|---:|---:|---:|
| $0.25 | 78 | 0 | 0.2030 | 0.18 | 1 |
| $2.00 | 78 | 1 208 | 1.9989 | 1.69 | 7 |
| $6.00 | 78 | 3 928 | 5.9998 | 4.91 | 20 |

The row count is solved at the **conservative** rate, so the dollars that bind come from that
model; the wall clock and the job count come from the **marginal** one, which is the only model
whose seconds were counted rather than divided out of a price. Each field says which — a dollar
figure from one model beside a wall clock from the other in a single unlabelled row is two
denominators in one line.

### The pod numbers, once, as context

SPEC 3.18 (4) names them: "5b's 0.5993 per 1,000 rows and 0.4611 per pass were measured on a POD
and are not this runtime's numbers". They live in `results/srv2d_cost.json :: pod_comparison` and
appear in the record **only** inside `context_not_a_headline`, with the amendment's sentence beside
them. A test asserts they occur nowhere else.

`results/parity_srv2.json :: diagnostics` was read, as the contract asked, and did **not** become a
source: it carries 400 + 250 + 108 rows and 0 failures of every kind, and no seconds and no
dollars at all. Its row counts are used (they are what the unit cost is *per*); its cost is not,
because it has none. Neither leg is marked `NO PAID MEASUREMENT`.

---

## THE STOP — the operator's table

**No pre-registration is written. That is prep-c3, after the ruling on the numbers below.**

### 1 · What the window holds — anchor 2026-08-09, window 2026-07-12 … 2026-08-09

| | in the window | concentration |
|---|---:|---|
| comments, all unanswered | **5 075** | 19 channels; `@matusi_ukr` + `@mandziak` = **73.8%** |
| posts | 9 158 | 66 registry channels; top six = 53.2%, all regional news |
| posts with media | 5 773 | — |
| leaflet pages downloaded | **78** | one channel, 9 posts |

Cells the store cannot answer: 7 channels have no posts file; 47 have no comments file, of which
exactly **one** (`@eftforhealth`) is a collection gap and the rest cannot produce a comment at all.

### 2 · Leaflet coverage vs downloaded — the ATB-only default

| | |
|---|---:|
| posts with media in the window | 5 773 |
| of them, with **no page anywhere** | **5 764** (99.8%) |
| channels with any page on disk | 1 |
| inside ATB: media posts / with pages / pages | 13 / 9 / **78** |

The ATB-only default is not a preference this cycle — **it is the only channel with a single page
downloaded**, and even ATB is 9 of its 13 in-window media posts. Widening the leaflet leg to any
other chain is a COLLECTION task before it is an extraction task, and this contract fetched
nothing.

### 3 · Cost — per leg, from paid serverless measurements

Dollars from the **conservative** corner, wall clock from the **marginal** one — the only corner
whose seconds were counted rather than divided out of a price. Each column says which, because a
dollar figure from one model beside a wall clock from the other, unlabelled, is two denominators
in one row.

| leg | rows | $ (conservative) | wall clock (marginal) |
|---|---:|---:|---:|
| comment | 5 075 | **$7.4840** | 6.09 h, 25 jobs |
| leaflet_page | 78 | **$0.2030** | 0.18 h, 1 job |
| **the two priced legs** | | **$7.6870** | **6.27 h** |
| post text — **BOUND, no writer** | 9 158 | *$8.1573* | *7.17 h, 29 jobs* |
| **all three row types** | | **~$15.84** | **~13.4 h** |

Both legs are priced on their UNANSWERED count, not on what the window holds — identical today
because neither watermark is set anywhere, and one leg subtracting while the other does not would
mis-price the first re-run after a pass.

**Remaining: $6.1690** — `results/spend_phase4.json :: sessions[-1]` (spent $23.8310 of the
$30.00 cap, read 2026-08-13T07:59:22+00:00), enforced by `scripts/runpod_guard.py :: PHASE_CAP_USD`.
That is the **last logged reading**; nothing has been billed since (prep-a, -b, -c1 and this
session are all $0), and the live figure needs a balance call this contract does not make.

**The two priced legs alone do not fit — 1.25× what the phase has left**, and a test asserts it so
that a later re-run cannot make the STOP quietly change shape. **With the post-text bound the window
is 2.6×**, and that leg has no code behind it yet.

### 4 · Candidate caps that fit

| cap | buys | share of the comment window | hours | jobs |
|---:|---|---:|---:|---:|
| $0.25 | 78 pages, 0 comments | 0.0% | 0.18 | 1 |
| $2.00 | 78 pages + 1 208 comments | 23.8% | 1.69 | 7 |
| $6.00 | 78 pages + 3 928 comments | 77.4% | 4.91 | 20 |

### 5 · What the operator is being asked to rule

1. **The anchor.** 2026-08-09 is the executor's choice with its reasoning; 2026-08-14 and
   2026-07-28 are priced beside it. The last of the three is the only window that holds all 159
   leaflet pages — and it holds 1 398 fewer comments.
2. **The composition.** Two channels are three quarters of the comment window, and neither is a
   retailer. A cap that buys 3 928 of 5 075 comments buys mostly `@matusi_ukr`.
3. **The cap**, from the table above, and whether the leaflet leg goes first.
4. **Leaflets beyond ATB** — a collection decision, not an extraction one.
5. **The post-text leg**: is it in 5c2-run at all? It is in the ruling's scope, its instrument
   passed bar 3, it has a paid rate — and `loop.py` has no pass that asks a post's text. Building
   one is code this contract was not given, and its bound alone is larger than the whole remaining
   budget.

A number that fell into this session's lap and belongs here rather than anywhere else: the whole
leaflet corpus on disk is **159 pages under 19 posts**, all of them ATB, dated 2026-07-01 … 07-23.

---

## Verify gate

### 1 · `make check` after every commit

Every commit of this session checked out into a worktree and run on its own. **Dv193 re-measured
rather than inherited:** a worktree cannot hold `data/` (gitignored), so it is replaced by a symlink
to the repo's, and `tests/test_collect_5c1.py::test_the_guard_reads_the_pinned_paths_off_the_pin_file`
is red on **every** row — including the control, which is the commit before this session began. In
the main tree that nodeid passes:

```
$ python3 -m pytest tests/test_collect_5c1.py::test_the_guard_reads_the_pinned_paths_off_the_pin_file -q
1 passed in 0.27s
```

| # | commit | result | failures |
|---|---|---|---|
| — | `139dd34` **(control)** | 1 failed, 2102 passed, 2 skipped | `test_the_guard_reads_the_pinned_paths_off_the_pin_file` |
| 1 | `86757dd` | 1 failed, 2102 passed, 2 skipped | the same one |
| 2 | `60067a2` | 1 failed, 2102 passed, 2 skipped | the same one |
| 3 | `f06edcd` | 1 failed, **2103** passed, 2 skipped | the same one |
| 4 | `8d4bd0b` | 1 failed, **2118** passed, 2 skipped | the same one |
| 5 | `716bca5` | 1 failed, **2133** passed, 2 skipped | the same one |
| 6 | `333cf2c` | 1 failed, **2135** passed, 2 skipped | the same one |
| 7 | `d469942` | 1 failed, **2136** passed, 2 skipped | the same one |
| 8 | `ae88b44` | 1 failed, 2136 passed, 2 skipped | the same one |
| 9 | `22ac2a6` | 1 failed, 2136 passed, 2 skipped | the same one |
| 10 | `daaa355` | 1 failed, **2139** passed, 2 skipped | the same one |

Same nodeid on every row, control included, and the count only ever rises. In the main tree, HEAD is
**2140 passed, 2 skipped**, and `ruff format --check .` is clean.

The last commits of this session are the ones that append this table and the vault tail, so they
cannot carry their own result: they add markdown to an already-green tree, and the `make check` run
beside each is the evidence for it.

### 2 · The census run twice with the same anchor

Both `sha256 = a1384a12bcbe975954f8feaa1c5207d59cc66ab524b3d877099bad92ede5305f`, shown above,
with a working-tree change between them. The cross-check against an independent count is the
16 218 re-derivation in Deliverable 1 — corpus-level, and labelled so it is never read as a window
figure.

### 3 · Per projection row, the quoted source beside the derived number

The citation table in Deliverable 2, plus `tests/test_projection_5c2.py`, which re-resolves every
`source` string in the record and greps every `quote` back to its file. Measured: halve one cited
value by hand and three tests go red; regenerate and all pass.

### 4 · `git log` and a clean `git status`

```
$ git log --oneline 139dd34..HEAD
d469942 docs(report): 5c2-prep-c2 -- the census, the projection, and the STOP the numbers force
333cf2c fix(5c2-prep-c2): the two records stop moving with the working tree, and the quote names the line it prices
716bca5 data(5c2-prep-c2): the projection -- both legs priced from paid serverless sessions, and the window does not fit
8d4bd0b data(5c2-prep-c2): the census of the window -- 66 channels, one anchor, CANNOT ANSWER where the store cannot answer
f06edcd fix(5c2-prep-c2): image_path goes into the record repo-relative, the reader resolves it
60067a2 docs(vault): the prep-c1 session tail
86757dd docs: 5c2-prep-c2 queued -- STATUS after the prep-c1 acceptance

$ git status --short
?? docs/reviews/          # the operator document of step 0, left alone
```

plus this report's own amendment commit and the session's vault tail, which are the two commits a
report cannot carry its own hash for. Nothing else is uncommitted.

### 5 · The report's own numbers, re-derived

A throwaway script re-derives every figure in this report straight from `results/census_5c2.json`,
`results/projection_5c2.json`, the smoke's own rows and `git log`, and greps each one back into the
rendered file: **66 OK, 0 FAIL**. It is what caught the coverage-gap mislabel above.

---

## Do NOT — what this session did not do

* **Nothing was spent.** No pod, no endpoint, no template, no serverless job, no OpenRouter call,
  no RunPod contact at all — the budget was read off `results/spend_phase4.json` and
  `scripts/runpod_guard.py`, both on disk. `ENDPOINT` in `scripts/run_loop.py` is still `None`.
* **No pre-registration**, in any file, under any name.
* **No Telegram client and nothing fetched.** The collection gap found by the census is reported
  above and was not closed.
* `src/market_pulse/positions.py`, `evidence.REQUIRED` / `KIND_FIELDS`, the sealed sku artifacts
  and the team-lead files are untouched: `git diff --stat 139dd34..HEAD` names none of them.
* `data/raw/` was hashed before the first write-capable action and after every run — the six v1
  stores still match `results/raw_v1_baseline.sha256`, and `data/derived/` does not exist.

---

## Deviations

`implementation-notes.md`, section `5c2-prep-c2`: **Dv269–Dv279**. Every one of them is cited in
the sections above.

---

## Commits

| # | commit | subject |
|---|---|---|
| 1 | `86757dd` | `docs: 5c2-prep-c2 queued — STATUS after the prep-c1 acceptance` |
| 2 | `60067a2` | `docs(vault): the prep-c1 session tail` |
| 3 | `f06edcd` | `fix(5c2-prep-c2): image_path goes into the record repo-relative, the reader resolves it` |
| 4 | `8d4bd0b` | `data(5c2-prep-c2): the census of the window — 66 channels, one anchor, CANNOT ANSWER where the store cannot answer` |
| 5 | `716bca5` | `data(5c2-prep-c2): the projection — both legs priced from paid serverless sessions, and the window does not fit` |
| 6 | `333cf2c` | `fix(5c2-prep-c2): the two records stop moving with the working tree, and the quote names the line it prices` |
| 7 | `d469942` | `docs(report): 5c2-prep-c2 — the census, the projection, and the STOP the numbers force` |
| 8 | `ae88b44` | `docs(report): 5c2-prep-c2 — the per-commit checkout table and the session's git log` |
| 9 | `22ac2a6` | `chore(vault): the 5c2-prep-c2 session tail — the STOP, and the two records that stopped moving` |
| 10 | `daaa355` | `fix(5c2-prep-c2): the post row type is in scope, bounded and out of the two-leg total` |
| 11 | — | this report's own amendment and the session's vault tail — the two a report cannot carry its own hash for |
