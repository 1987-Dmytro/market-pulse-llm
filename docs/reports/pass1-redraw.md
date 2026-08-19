# Report — `pass1-redraw`: the r2 pack, and the census that says the gate is already the dairy gate

Contract `docs/PROMPT-pass1-redraw.md`, $0, no cloud call. Five commits,
`115422e` → `45021f7`, working tree clean at every boundary and `make check`
green at every one of them. Cause tags from the closed enum v2 only; lesson
names ride as trailing `[[wiki-name]]`.

## Read back, before the first edit

1. **Pinned → read-only:** `scripts/build_pass1_label_pack.py` (its sha256 *is*
   `producer.sha256` inside the r1 record), `src/market_pulse/brands.py`,
   `src/market_pulse/prompts.py`, `config/registry.yaml`, `config/lexicon.yaml`,
   `results/pass1_label_pack_r1.json`, `docs/labels-pass1-r1.jsonl` +
   `results/labels_pass1_r1*`, `docs/label-pack-pass1-r1*.md` — read, never edited, digests
   equal after as before.
2. **No absence assert:** no test may say `docs/labels-pass1-r2.jsonl` does not exist; a test may
   assert the pack record NAMES it and, WHEN it exists, that it validates.
3. **Reachability before the target:** the cap and `sum(min(available, cap))` are computed and
   PRINTED before `target = min(150, …)` freezes; a smaller honest number ships with its inequality.
4. **One-edit budget:** `knowledge/hot.md` gets exactly one curation edit — the step-0.5 sweep;
   sealed literal blocks and AUTO-GEN byte-intact.
5. **The blind subset lives on r1**, not here; r2 spends no pack row on it.

## Step 0 — the tail

`git status --porcelain` at step 0 returned exactly the five paths the contract's Baselines block
predicts, and nothing else:

```
 M docs/STATUS.md
 M knowledge/daily_logs/2026-08-19.md
 M knowledge/hot.md
 M knowledge/index.md
?? docs/PROMPT-pass1-redraw.md
```

- `115422e` — the vault tail: the previous session's `/save` (checkpoint 13:27, the curated
  `hot.md`, the Stop hook's `index.md`).
- `9ef3213` — team-lead files verbatim: `docs/STATUS.md` (sitting-2 rulings) and this contract.

## Step 0.5 — the accepted `boot-debloat`'s debts

### The Dv541 sweep: one edit, and the half that was already done

**The blocker the contract sends the sweep after was already closed.** `/save` ran between the two
contracts and its own spec mandates curating Next/Blockers, so the ⛔ BOOT TAX blocker and Next §2
went then — they arrived here inside the step-0 tail, not as work outstanding. What the contract
could not have seen is what was left: a bar sentence that was **wrong in the other direction**.
Three sentences changed, and they are the whole edit (`a74d3e8`, `hot.md` 12 187 → 12 623 B):

| # | before | after |
|---|---|---|
| 1 | «MEMORY.md **149/200 строк (74.5%) · 18 472/25 000 юнитов (73.9%)**» | «**150/200 строк (75.0%) · 18 609/25 000 юнитов (74.4%)**» — re-measured after the plantings; the old unit figure was also one low |
| 2 | «150-я строка это ровно 75.0%, то есть **уже не «под баром»**: следующий урок либо дописывается в существующий файл, либо требует консолидации» | «бар контракта `pass1-redraw` это **≤150 / ≤18 750**, то есть строки ровно НА баре: следующий урок садится файлом (файл в индекс не входит и на буте стоит **0**), а строку индекса он получит только после консолидации» |
| 3 | «⚠️ Без дома: **Dv521** (…), плюс два слуга из `boot-debloat` — `a-checker-whose-failure-is-silence` (Dv540) и `a-guard-that-runs-after-the-write` (Dv542)» | «⚠️ Без дома остался **Dv521** — и причина названа точно: … Долг индекса: `a-checker-whose-failure-is-silence` — файл посажен, строки не хватило» |

Sentence 2 is the one worth having: the previous session read «под баром» as strictly less than
75%, and on that reading the index was already full. The contract writes the bar as
**«≤75% (≤150 lines / ≤18 750)»**, which makes 150 admissible — and that is the reading that let
the plantings happen at all.

Every invariant ran **on the in-memory string, before `write_text`** — Dv542's own lesson, applied
in the contract that plants it. The sealed literals (`~$0.24/day`, «80 GB is about what the …»)
kept their counts, the AUTO-GEN region compared byte-equal, and the curated half was grepped for
`≤9K`, `ПРИОСТАНОВЛЕНА` and every pre-debloat size literal (`8 090`, `24 662`, `24 718`, `24 807`,
`7 921`) — none survives. Immediately after:

```
$ python3.11 -m pytest tests/test_volume_calc_5c1.py -q
10 passed in 0.08s
```

### The three orphan lessons

Two files planted, and the mechanism of the first was **moved rather than copied** — `/save` had
written it into `long_run_watch_the_process.md` the night before, and one fact keeps one home:

| file | bytes | index line |
|---|---:|---|
| `a_checker_whose_failure_is_silence.md` (new, `name: a-checker-whose-failure-is-silence`) | 2 107 | **no** — the debt below |
| `a_guard_that_runs_after_the_write.md` (new, `name: a-guard-that-runs-after-the-write`) | 1 961 | yes |
| `long_run_watch_the_process.md` (section moved out, one-line pointer left) | 3 991 → 2 971 | unchanged |

**The bar allows exactly one index line, and the arithmetic is what says so.** Before: 149 lines /
18 473 UTF-16 units. One line → **150 / 18 609**, both at or under `≤150 / ≤18 750`. Two lines →
151, which crosses on the line axis whatever the units do. The line went to
`a-guard-that-runs-after-the-write` because it is the one no indexed file reaches;
`a-checker-whose-failure-is-silence` is reachable through the pointer left in
`long_run_watch_the_process`, which is indexed. **Debt: it has a file and no index line of its own.**

**Dv521 — the check the contract asks for passes, and the homelessness is in the other direction.**
`<memory>/cooccurrence_is_not_explanation.md` states the 4.5g5 family-size mechanism in full
(«The reply feature covered 23 of them … **10 said the refusal was about the reply**») and never
mentions `max()` — so there was nothing to add, and I added nothing. What has no home is **Dv521's
own** mechanism (a record block whose two fields came from different rows: `max(weights,
key=allocation)` picked the first of thirteen ties and printed another thread's payable count beside
it), which `docs/reports/pass1-data-prep.md:305` tags with **that same wikilink**. `vault-dream`
Dv529 caught exactly this pair and refused the eviction for it; the pairing is still live, one
direction now proven clean. Left as Dv521's debt rather than fixed, because a third planting is not
in this contract's budget and the index has no room for its line.

## D1 — the dairy-signal census (read-only, `--census` writes nothing)

```
$ PYTHONPATH=src python3.11 scripts/build_pass1_label_pack_r2.py --census
D1 — the dairy-signal census (matcher: src/market_pulse brands ∪ tracked categories, DEFAULT matching)
  definition                                        thr  -exam  payable  drawn  avail  r1 rows  ours   share
  brand or category (D1's rule, = the shipped gate)  129    122      968    500    468      500    38    7.6%
  watchlist brand only                               42     38      187    157     30      157     0    0.0%
  tracked category only                              96     91      804    364    440      364    38   10.4%
  category and no brand                              87     84      781    343    438      343    38   11.1%
  (not a thread rule) the COMMENT's own text hits    48     41       59     38     21       38    14   36.8%

  arithmetic (D1's rule): 968 payable in the 122 candidate threads left after the 7 exam threads − 500 drawn by r1 − 0 gold = 468 AVAILABLE
  candidate threads: payable min 0 · median 3 · p90 14 · max 125   |   available min 0 · median 0 · p90 2 · max 113
  REACHABILITY BEFORE THE TARGET: cap 14 (p90 of the candidates' payable counts) → sum(min(available, cap)) = 176; available 468; ceiling 150  →  target = min(150, 468, 176) = 150
```

**The census's first finding is that the rule does not narrow.** D1 defines a candidate as a thread
where the shipped matcher finds a dairy brand or a tracked category — and that is the same predicate
the reader cell itself was selected with, so it keeps **129 of 129 threads**, 122 after the exam,
968 payable, 468 available. The contract's own Baselines block states «468 payable remain», which is
the arithmetic of this row and of no other; the number closes on the first reading and on nothing
else, which is what fixed the interpretation ([[a-prefilter-cannot-certify-the-population]]).

**The second finding is that the targeting the sitting bought is aimed at the wrong half.** «Ours»
below is `молочный_бренд` + `категория_личное`, the deficit sitting-2 is closing, and the share is
measured on r1's own 500 labels restricted to the rows each rule would have kept — the incumbent
priced in the same units as its challengers ([[price-the-incumbent-in-the-same-units]]):

- **watchlist brand only → 0 of 157 «ours». Zero.** Under the DEFAULT matching the contract
  mandates, the brand hits over these threads are `varto` ×22, `varus-pl` ×17 and `selianske` ×1 —
  an ordinary Ukrainian adverb («чи варто») and a retail chain whose own channel is in the window.
  SPEC 3.21 (1) exists for the first of those and is OFF by construction here. A re-draw restricted
  to brand-hit threads would have drawn **30 units from the one cut of this tract that has never
  produced a single row of the class it is meant to fix**.
- **tracked category → 10.4%, category-and-no-brand → 11.1%**, against the whole tract's **7.6%**.
  Real lift, and small: 150 units at 11.1% is ≈17 «ours» where a blind top-up gives ≈11. For
  `молочный_бренд` alone the pool is 2 of 343 — a 150-unit re-draw expects **0.9 more rows** of the
  class the arm is named after.
- **the comment's own text → 36.8% of 38 rows**, a 4.8× lift, and its ceiling is the number that
  matters: **59 such payable comments exist in the whole tract and 21 are undrawn**. This is NOT
  the pack's rule — D1 says a candidate is a THREAD, and I did not redefine it — but it is measured,
  committed and asserted, because it is the only cut with a large lift and the next ruling needs its
  ceiling, not its rate.

## D2 — the r2 pack (`c3fa4b3`, census amended in `45021f7`)

**A new producer, and the old one proven untouched.** `scripts/build_pass1_label_pack_r2.py`
copies-and-adapts r1 (which the contract licenses); the record carries
`producer.r1_producer_untouched: true`, computed by hashing `build_pass1_label_pack.py` against the
r1 record's own `producer.sha256`.

**The weight is not r1's.** r1 weights a thread `min(payable, CAP)`; for r2 that would allocate
units the draw cannot supply, because what r2 may take from a thread is what r1 **left** there. The
weight is `min(available, cap)`, and the difference is the whole ceiling: `sum(w)` is **176**, not
r1's 572. The cap is the p90 of the candidate threads' payable counts, re-derived every run and
refused if it moves — the candidate subset is r1's remaining population thread for thread, so it
comes out at r1's **14**, derived rather than copied.

**The target froze after the reachability, not before.** `min(150, 468, 176) = 150`; the binding
term is the ceiling, named in the record. At `cap = 4` the same population tops out at 176 → the
`allocate` refusal fires, and a test drives it.

**Contamination — five lists, all empty, printed:**

```
  contamination: in-exam 0 · already-drawn 0 · gold drawn 0 · gold in population 0 · gold rendered 0
```

The last is checked against the RENDERED page and not against the unit list, because a thread is
rendered whole. `gold in population 0` is an empty class with a cause, not a coincidence: every one
of the 14 gold rows lives inside one of the 7 exam threads, so the exam removal already took them
and the gold subtraction the contract asks for removes **nothing** — the record says so in the
arithmetic line rather than leaving a zero to be read as luck.

**Determinism.** Two `--outdir` runs and the shipped copy, three identical digests each:

```
92b2d066…  (before the census amendment)  →  5acae80b28463f58…  results/pass1_label_pack_r2.json
86919f8410b96924…  docs/label-pack-pass1-r2.md   (unchanged by the amendment — the draw did not move)
```

No `generated_at`, no clock, and no `--outdir` string anywhere in the record.

**The page carries r1's law by the same bytes.** `READER_ATTRIBUTION_LAW_V5` and `READER_CARRY_V5`
are read from `prompts.py` and their sha256 is compared to the r1 record's — `same_law_as_r1: true`.
A re-draw that re-worded the codebook would be a second instrument, not more of the first. The
Dv519 excision holds: `r2_ruling()` cuts the adjudication at the literal marker
`", and probe-b measured"` and refuses if that marker ever moves. Both r1 page-guard classes have
their r2 equivalents **with their negative controls** — the 14 gold msg-ids appear nowhere on the
page (control: a planted id is caught), and the three bar figures `0.357 / 0.429 / 0.643` appear
nowhere (control: the record the quote is cut from does carry all three).

**The gate needed no new code.** `scripts/validate_pass1_labels.py` already takes `--pack`, so the
r2 file validates against the r2 pack with the r1 validator unchanged — one home for the taxonomy,
the four refusals and the «writes nothing» source-level proof. `tests/test_validate_pass1_labels_r2.py`
drives it red-first on synthetic files in `tmp_path`: missing unit · unit answered twice · the
STRING `"null"` · an absent `subject_type` key · a row from an exam thread · **and the defect only
r2 can have — a row answering a unit r1 already drew, refused as not a unit of this pack.** Green
path on a complete synthetic file, and a last test that runs the real
`docs/labels-pass1-r2.jsonl` through the gate **when it exists** and skips when it does not. Nothing
anywhere asserts its absence.

**Blind subset: not drawn.** `blind.drawn: 0`, with the rule naming where the option lives.

## Verify

```
$ make check
ruff check .
All checks passed!
3001 passed, 3 skipped in ...s
```

2 967 registered + **35 new tests** — 26 on the pack, 9 on the r2 gate; 34 pass and the 35th is
the skip, the conditional on the team lead's not-yet-written labels file. Green at every earlier
boundary too: **2 967/2** at baseline, **2 967/2** after step 0.5, **3 000/3** at the D2 commit,
**3 001/3** after the census amendment.

```
$ python3.11 -m pytest tests/test_volume_calc_5c1.py -q       # right after the hot.md sweep
10 passed in 0.08s

$ PYTHONPATH=src python3.11 scripts/build_pass1_label_pack_r2.py     # and again: same sha
wrote docs/label-pack-pass1-r2.md  sha256 86919f8410b96924…  213585 chars
wrote results/pass1_label_pack_r2.json  sha256 5acae80b28463f58…  38426 chars
  968 payable in the 122 candidate threads that survive the 7 exam threads − 500 already drawn by r1
  − 0 gold rows (every gold row lives inside an exam thread) = 468 available → min(150, 468, 176) = 150 drawn
  contamination: in-exam 0 · already-drawn 0 · gold drawn 0 · gold in population 0 · gold rendered 0
  seed 20260819 · cap 14 (p90) · capped weights 176 >= target 150 — reachable True, binding ceiling
  per-thread distribution (allocated → threads):
      0 drawn ×  70 threads   (available 0–0)
      1 drawn ×  39 threads   (available 1–2)
      2 drawn ×   1 threads   (available 2–2)
      3 drawn ×   1 threads   (available 4–4)
      4 drawn ×   2 threads   (available 5–5)
      7 drawn ×   2 threads   (available 8–8)
     12 drawn ×   7 threads   (available 15–113)

$ python3.11 scripts/check-wikilinks.py
check-wikilinks: OK, none broken

$ wc -l -c <memory>/MEMORY.md
     150   18895 …/memory/MEMORY.md

$ python3.11 scripts/context-census.py
brain-census: 9.5Ktok boot tax

$ git status --porcelain
(empty)
```

**`wc -c` is the wrong axis for the second bar, and the two readings disagree.** `wc -c` returns
**bytes** — 18 895, which is 75.6% of 25 000 and would read as a crossed bar. The loader's cap is
`MEMORY_UNITS = 25_000` **UTF-16 code units** («not the UTF-8 bytes a `stat()` returns»,
`scripts/context-census.py:26`, Dv526), and on that axis the file is **18 609 = 74.4%**. Cyrillic
is why they differ. The bar is the loader's, so the planting is inside it — but the command the
contract names cannot show that ([[check-granularity-matches-the-claim]]).

**Census, named — and it does not start where the contract's baseline says.** The contract's
Baselines block quotes **9.7K**; the reading at step 0 was **9.4K**, and the difference is not
drift. 9.7K was `boot-debloat`'s floor at `hot.md` **13 457 B**; `/save` then curated the file to
**12 187 B**, and that curation was on disk **uncommitted** when this contract was written — the
contract's own porcelain list names it (` M knowledge/hot.md (hook/save tails)`) beside a census
figure taken before it. The whole chain, three files and three readings:

| moment | `hot.md` | census |
|---|---:|---:|
| `boot-debloat` D4, the registered floor | 13 457 B | **9.7K** |
| `/save`'s curation (inherited, committed here as `115422e`) | 12 187 B | **9.4K** |
| after this contract's step 0.5 (sweep +436 B, one index line +136 units) | 12 623 B | **9.5K** |

D2 adds nothing loadable — the pack, the page, the producer and the tests are not read at boot —
but «adds 0» would be one word too strong: `hot.md`'s AUTO-GEN block regenerates from `git log -5`
at the next SessionStart, and this contract replaced all five subjects. Measured with the READER,
never `main()`, `git status --porcelain` empty afterwards (Dv543's own precedent): the region is
1 210 B on disk and **1 220 B** at the next boot, **+10 B = +0.0025K** against the 1.2K of headroom
`TARGET_KTOK = 10.7` leaves at 9.5. The census prints no warning.

**The pins, which the Verify block does not name but the DO NOT does:**

```
$ make preflight ARGS='labels-pass1-r1'
[3] pins — 5 of the 27 touched paths are pinned by a record
    scripts/build_pass1_label_pack.py     <- results/pass1_label_pack_r1.json.producer.sha256 408bce3725ab…
    scripts/build_pass1_label_pack_r2.py  <- results/pass1_label_pack_r2.json.producer.sha256 7ae4f6e440ff…
    docs/label-pack-pass1-r1-blind40.md   <- results/pass1_label_pack_r1.json.blind.sha256 d2364ff3e30b…
    docs/label-pack-pass1-r1.md           <- 2 pins, both 5aec5c9835f8…
    results/pass1_label_pack_r1.json      <- 2 pins, both e5ca328e5d99…
[4] digests — sha256 of all 5 pinned paths, against what is pinned
    5 of 5 pinned paths match every digest on them
```

The r2 record's `inputs` now pins the r1 record too, so `e5ca328e5d99…` is confirmed by two
independent records — the provenance sidecar's and this pack's.

## Deviations from Dv545

| # | finding | tag |
|---|---|---|
| **Dv545** | **D1's candidate rule selects the whole tract — the gate already IS the dairy gate.** A thread passes the shipped matcher exactly when the reader cell kept it, so «candidates» is 129 of 129 and 122 of 122 after the exam. The re-draw D2 builds is therefore a **blind top-up of r1's own population**, not a targeted one, and no arrangement of the contract's own words makes it otherwise. Executed as written, because the contract's Baselines block states «468 payable remain» — the arithmetic of this reading and of no other — and named here because «targeted» is the word the ruling was bought with. | `[cause: contract-gap]` `[[a-prefilter-cannot-certify-the-population]]` |
| **Dv546** | **«`market_pulse.brands` is the ONE matcher» is a mis-scope, and the quote proves it.** `config/watchlist_rules.yaml:13–14` says it is «the one matcher **that reads this file**» — a claim about the rules file, not about the gate. The category half of «a watchlist hit (dairy brand or category)» lives in `yield_screen.category_hits` over `gate_census_w1.compiled(wide=False)`, a module the contract never names; taking the citation literally would have cut the population from 122 threads to 38 and the available units from 468 to 30. Quoted back into the record's `population.matcher` so the next reader sees both halves. | `[cause: contract-gap]` `[[verbatim_quotes_must_be_grepped]]` |
| **Dv547** | **The narrowing the sitting had in mind returns zero of the class it is aimed at.** Measured on r1's own labels: brand-hit threads yield **0 «ours» in 157 rows**, because under the mandated DEFAULT matching the brand strings that fire in this window are `varto` (the adverb, 22 threads) and `varus-pl` (the retailer, 17). Category-hit threads yield 10.4% and category-without-brand 11.1% against the tract's 7.6% — real, small, and worth ≈0.9 extra `молочный_бренд` rows at 150 units. The only large lift is comment-level (36.8%) and its ceiling is **21 undrawn units**. All five rows are in the record; none of them changes what this contract draws. | `[cause: verify-gap]` `[[price-the-incumbent-in-the-same-units]]` |
| **Dv548** | **r1's weight formula is wrong for a re-draw, and copying it would have crashed or re-drawn r1's units.** `min(payable, CAP)` counts units r1 already took; the r2 weight is `min(available, cap)`, and the ceiling it produces is **176**, not 572. Had the reachability been asserted against the copied number, `target = 150` would have looked comfortable against 572 while the draw sampled from pools it had already emptied. The reachability is a term of the target's own `min`, printed before the freeze. | `[cause: verify-gap]` `[[an-absolute-bar-needs-a-reachability-state]]` |
| **Dv549** | **The Verify block's `wc -c` measures bytes and the bar is in UTF-16 units.** 18 895 B = 75.6% of 25 000 reads as a crossed bar; the loader's own `MEMORY_UNITS` axis reads **18 609 = 74.4%**, and Dv526 already ruled which one the loader uses. The two readings disagree about whether the step-0.5 planting was allowed at all. Pasted both, planted on the loader's axis. | `[cause: verify-gap]` `[[check-granularity-matches-the-claim]]` |
| **Dv550** | **The Dv521 clause checks the direction that was already true.** `cooccurrence_is_not_explanation.md` states the 4.5g5 mechanism in full and never mentions `max()`, so «add it there if it only names the max() tie» has nothing to add. What has no home is Dv521's own mechanism, which the repo tags with that very wikilink — the pairing `vault-dream` Dv529 refused an eviction over. One direction is now proven clean and the other is named; a third planting is outside this contract's budget and the index has no line for it. | `[cause: contract-gap]` `[[a-citation-is-not-a-record]]` |
| **Dv551** | **Half of the sweep was already done by a command that is not a contract.** `/save` ran between `boot-debloat` and this contract, and its own spec mandates curating Next/Blockers — so the ⛔ BOOT TAX blocker and the Next §2 line went then, arriving here inside the step-0 tail. The contract describes them as outstanding. What was genuinely left is a sentence neither the ruling nor the contract could have predicted: `hot.md` asserting that 150 index lines is **over** the bar the contract sets at exactly 150. Named because «the sweep found nothing to do» and «the sweep was already done» are different reports. | `[cause: contract-gap]` `[[the-gates-evidence-outlived-its-artifact]]` |
| **Dv553** | **The contract's baseline census and its own porcelain list describe different moments.** Baselines quotes «census 9.7K», which is `boot-debloat`'s floor at `hot.md` 13 457 B — while the same block lists ` M knowledge/hot.md (hook/save tails)` as expected, i.e. the `/save` curation that had already taken the file to 12 187 B and the census to **9.4K**. Both sentences were written from the same tree and only one of them is current, so «≈9.7K ± the sweep's delta» cannot be checked as written. Reconciled by the chain above rather than by picking a number: 13 457 → 12 187 → 12 623 B against 9.7 → 9.4 → 9.5K, each reading printed by the census itself. | `[cause: contract-gap]` `[[the-gates-evidence-outlived-its-artifact]]` |
| **Dv552** | **«Extend or parallel the validator» — neither was needed.** `validate_pass1_labels.py` already takes `--pack` and its refusals are all pack-relative, so the r2 gate is the r1 gate pointed at the r2 record: zero production lines, zero risk to the constants its tests consume, and one home for the taxonomy. The enumeration the contract asked for was still owed and is done — the only importers are `tests/test_validate_pass1_labels.py` and the new r2 file, and the r1 test touches **six** symbols (`gate.VALUES`, `gate.PACK`, `gate.LABELS`, `gate.validate`, `gate.main`, `gate.__file__`); beyond the module, the two rendered pack pages quote its command line. Nothing shared was edited, so the list is a proof and not a plan. | `[cause: process]` `[[a-consumer-list-is-not-a-meaning-list]]` |

## Process signals

1. **The census earned its «read-only, pasted first» ordering.** Had the target frozen before the
   table, the pack would have shipped with «targeted re-draw» on its cover and 0.0% behind the word;
   the ordering is what let the number be a finding instead of a footnote.
2. **A definition that selects everything and a definition that selects nothing useful sat one
   parenthesis apart.** «Watchlist hit (dairy brand or category)» reads as one rule and is two, and
   the tie was broken by an arithmetic the contract itself states — 468 — not by which sentence
   sounded more like the ruling.
3. **Pricing a rule on labels that already exist costs nothing and changes the answer.** The deficit
   is not a sampling artefact of r1's draw: it is the population. That is only sayable because 500
   labels were already on disk and the four candidate rules could be run backwards over them.
4. **The lesson planted in step 0.5 was applied in step 0.5.** Every hot.md invariant ran against
   the in-memory string before the write — Dv542's own rule, in the contract that gives it a file.
5. **Two guards this session were armed on the wrong signal, and one of them was mine.** The wait
   loop watching `make check` matched ruff's «All checks passed!» and returned at 63%; re-armed on
   the pytest summary line. Same shape as Dv540 — a checker whose silence and whose speech are
   easy to confuse — one day later and in the other direction.

[[a-prefilter-cannot-certify-the-population]]
