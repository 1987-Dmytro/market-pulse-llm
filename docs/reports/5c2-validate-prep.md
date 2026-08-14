# 5c2-validate-prep — the sitting pack, and three report debts

The sitting of SPEC 3.18 (6) can now be held: `results/validate_5c2_pack.html` shows six leaflet
posts and five comments, original beside verdict, drawn under seed 42 from the window's own output
and captioned with the aggregates in `results/window_summary_5c2.json`. All three debts of the
accepted run report are paid by measurement — Dv307's hole is CLOSED at HEAD and the amendment says
so with the commit that closed it, the $0.8451 is named as a hand-typed conservative reading with
its consequence priced both ways, and the 55th call is the `assert_serving` handshake, verified on
both legs. `make check` is 2 303 passed / 2 skipped, nothing cloud-touching ran, and nothing under
`data/derived/` was written, moved or re-scored.

## Read-back

**Where the aggregates the rows wear come from.** `results/window_summary_5c2.json` — Deliverable 1,
computed from `data/derived/` alone plus the sealed registration (and `config/registry.yaml`
reached only through the seal's own pin). The pack READS it and computes no aggregate of its own.

**What the pack does on a missing source.** It refuses, loudly, naming the file, and writes nothing.
Proven by a negative control below: a sandbox copy of `data/derived/` with one channel file removed.

**Who fills `findings` and when.** The TEAM LEAD, DURING the sitting. Every slot ships empty, and
the verdicts become watchlist / lexicon / prompt-revision ORDERS in the REVIEW class of 3.16 (1) —
never re-scored numbers and never a moved bar. That sentence is in the rendering's header.

**The one thing this session must never edit.** `data/derived/` — the run's own evidence. (With it:
the sealed registration, the run records, the cap-30 records and every team-lead file.)

---

## Step 0 — the tail, and the three debts

Two commits by path for the tail: `ef0d4c4` (`docs:` — `docs/STATUS.md` and this contract's own
`docs/PROMPT-5c2-validate-prep.md`, both team-lead files, committed verbatim) and `7fb98d7`
(`docs(vault):` — the day's log, `knowledge/index.md` and `knowledge/hot.md`). `hot.md` is not in
the contract's `git status` listing and was modified anyway — see Dv319. Nothing was staged with
`git add -A`; every commit names its paths.

### Debt 1 — Dv307, settled by measurement (`6fd604c`)

The acceptance was right: `except BaseException` now wraps `run_the_legs` and a refused handshake
DOES write a ledger row. The discriminating question was not what HEAD looks like but WHEN that arm
landed, and `git log -S` answers it:

```
$ git log -S 'except BaseException' --oneline -- scripts/run_5c2.py
79ae380 fix(5c2-run): the leaflet pack is bounded by BYTES, and a crash still writes the ledger
```

`79ae380` is Dv309's twin, committed 2026-08-13 19:21 — INSIDE the paid session, between the two
endpoints. So Dv307's "NOT fixed mid-session" was true about the instrument (nothing was edited for
this hole) and false about the exit (`SystemExit` derives from `BaseException`, so the refusal
landed in the crash handler). The hole closed as a side effect.

Driven rather than re-read —
`tests/test_run_5c2.py::test_a_refused_handshake_writes_the_ledger_row_and_the_record`, with
`runpod_guard.balance` stubbed so no `runpodctl` call is made and the real ledger is never opened:

```
$ PYTHONPATH=src python3 -m pytest \
    "tests/test_run_5c2.py::test_a_refused_handshake_writes_the_ledger_row_and_the_record" -v
tests/test_run_5c2.py::test_a_refused_handshake_writes_the_ledger_row_and_the_record PASSED [100%]
1 passed in 0.23s
```

**Both directions.** The refusal fires:

```
SystemExit: the endpoint is not serving the registered configuration — merge_state: worker says
'merged-requantized', expected 'unmerged-adapter'. SPEC amendment 3.11 (2) scores the EXACT
production configuration; stop and report.        # client.calls == 1: nothing past the handshake
```

and the two artifacts land, the ledger row carrying the refusal message itself:

```
the ledger  {"balance": 9.0, "step_spent_usd": 0.0,
             "note": "5c2-run comments — SystemExit: the endpoint is not serving the registered
                      configuration — merge_state: …"}
the record  died:   "SystemExit: the endpoint is not serving the registered configuration — …"
            notes:  ["the run ENDED on an exception: SystemExit"]      timing.calls: 1
```

**The control that says the guard discriminates:** the worker's own answer plus a field the pin does
not compare (`gpu_name`) passes `assert_serving` unchanged. **The negative control that says the
test measures the fix:** with the `except BaseException` arm deleted from a scratch copy of the
driver — the Dv307 shape — the same test fails on `len(runs) == 1` with `runs == []`, which is the
deviation's claim, reproduced. The scratch copy was restored and verified byte-identical.

What is still owed is narrower than the deviation states and is named in the amendment: the exit is
covered by the CRASH handler, so narrowing `except BaseException` to a crash-only type would
silently reopen it. This test is what would go red.

### Debt 2 — the $0.8451 citation (`9f7a7ab`)

`--already-usd 0.8451` is **hand-typed and no artifact on this disk re-derives it.** Every persisted
carrier says something else: the ledger row `$0.8230` (anchor $11.0815436571 − balance
$10.2585299348), the phase ledger carrying the same balance reading, and the client's wall clock
`$0.8344` ((2 267.544 + 393.079 + 60) s × $0.00030669). No balance of $10.2364436571 — the reading
that would produce the typed number — appears in any file, log or record in the repo, and the
session transcript is not on disk.

It is legal because Dv33 makes the balance delta a **FLOOR** ("RunPod settles it minutes to hours
late"), so the true spend was ≥ $0.8230 and a bigger number is the conservative direction. The
consequence is one-way and checkable: a larger `already_usd` SHRINKS the (10)(a) budget, so the
typed number could only make the gate stricter. Priced both ways the verdict does not move —
projected $7.0196 against $7.1549 (typed) or $7.1770 (ledger), GO under both, while the registered
conservative corner $7.4840 exceeds both budgets. The addendum in `docs/reports/5c2-run.md` carries
the table and the rule it leaves behind.

### Debt 3 — `calls` 55 against 53 packs and one warm-up (`4fb2648`)

The extra call is the `assert_serving` handshake, **verified against the records rather than
asserted**: `EndpointClient._run` increments `calls` on every terminal job whatever its `op`, and
both legs leave exactly one call unaccounted after packs and warm-ups.

| leg | packs | warm-up jobs | handshake | `timing.calls` | `timing.rows` |
|---|---:|---:|---:|---:|---:|
| comments | 53 | 1 (3 rows in one job) | 1 | **55** | 5 078 = 5 075 + 3 |
| positions | 11 + 10 | 2 | 1 | **24** | 205 = 159 + 44 + 2 |

`positions_gm4_skub.JOBS_READING` already said it in prose. The comment leg's 53 packs sum to
`written` 5 075 of `asked` 5 075, so no pack is missing from the count either.

---

## Deliverable 1 — `results/window_summary_5c2.json` (`e9770da`)

`scripts/window_summary_5c2.py`, 65 KB of record, one second to build, reading `data/derived/`
alone plus the sealed registration. What it says about the window:

| leg | rows | what the aggregate carries |
|---|---:|---|
| comments | 5 075 | 5 075 scored, **0 unreadable**; sentiment 4 144 neutral / 661 positive / 270 negative; sarcasm **0.0132** on the scored rows; intents 553 price · 245 taste · 184 availability · 161 service · 138 quality · 17 packaging, **3 944 rows with no intent**; languages ua 2 606 · other 1 925 · ru 493 · en 51 |
| leaflet pages | 159 | 30 with positions · 127 empty · 2 unreadable · 106 positions, 19 posts |
| post texts | 44 | 21 with positions · 22 empty · 1 unreadable · 39 positions |
| position rows | 145 | tier **`position` × 145** · promo price on 138 · printed badge on 128 · old price on 95 · depth by badge median 0.4150, by price pair median 0.4206 · printed disagrees with computed on 8 |

Four things in it are load-bearing and none of them is a paragraph:

**The comment text is recovered from the `rendering`, not from `data/raw`.** The record's whole
input is the derived store, and the string inside the `<comment>` delimiter is the exact one the
model read — so the language column and the brand match are computed on what was SENT. The split is
guessed and then PROVEN: `prompts.build_messages` is re-run on the two halves and must reproduce the
recorded rendering byte for byte. All 5 075 rows pass it; a row that did not would stop the build.

**The fourth head does not exist.** `T1v2_with_post` returns three labels. 3.18 (6) asks the sitting
to see "sentiment, sarcasm, intents, and the brand attribution", and there is no brand head on the
comment instrument. What the record carries is the deterministic watchlist matcher, named as such in
the field itself — it fires on **11 rows of 5 075**. See Dv316.

**Two depth readings, neither corrected into the other.** 3.18 (1) makes the printed `-N%` badge the
aggregate instrument; where both prices exist the arithmetic of 3.17 (3) stands and the printed %
never substitutes it. Both are reported side by side with the disagreement count. The extracted old
price is COUNTED and never VALUED in this record — a test asserts no depth block ever grows a field
that could leak one.

**No clock and no git block**, so the record is byte-identical across runs and
`tests/test_window_summary_5c2.py::test_the_committed_record_is_what_the_producer_writes_today`
regenerates it and compares bytes. Every number in it re-derives or the suite is red.

## Deliverable 2 — `results/validate_5c2_pack.json` + `.html` (`8b6cbf4`)

```
$ PYTHONPATH=src python3 scripts/build_validate_pack.py
wrote results/validate_5c2_pack.json  sha256 0c57d094102b025c…
wrote results/validate_5c2_pack.html sha256 e2754e8834937017…
  seed 42 · 6 leaflet posts, 51 pages, 48 positions
  5 comments from ['@matusi_ukr', '@mandziak', '@VARUS_channel', '@kopiyochka1', '@klopotenkofood']
  findings: 6 post slots, 48 position slots, 5 comment slots — all empty
```

**The draw, and its two strata.** Comments: one row from each of the five channels with the most
rows in the window, seeded within each — the contract's own prescription, and it exists because two
channels are 73.8% of the window. Leaflets: the nineteen posts split by whether any page of them
yielded a position (11 / 8), four drawn from the first and two from the second. That second stratum
is a deviation from the letter of the contract and is argued in Dv317: a post that yielded nothing
cannot answer "field by field, what made each a POSITION", and a blind draw of five from nineteen
could have shown the operator one such post. Both strata are stated in the record, both populations
with them, and neither is a filter on the VERDICT — no row is selected for what the model said about
it. The draw is reproducible from the record alone, and a test redoes it from the seed.

**Per leaflet post** — every page of the post as it was sent, each `<img>` beside what came back
from it, and per position the five presence booleans with their VALUES, the rung, the rung
re-derived from those booleans by the ladder's own function, and the ladder key. The 32-row ladder
table travels inside the pack, so the rung is re-derivable AT THE TABLE rather than trusted.

**Per comment** — the comment as written, the parent post as the model received it (surrogate
included, tagged), the exact rendering behind a `<details>`, the raw reply, and all four verdict
rows: sentiment, sarcasm, intents, and the brand column with its instrument spelled out. Each is
captioned with BOTH denominators, the channel's and the window's, read from Deliverable 1 and
recomputed nowhere.

**The honesty rails, each with a test.** A missing source refuses by name. A page image is re-hashed
against the `image_sha256` the run recorded — 51 of 51 agree, so "as it was SENT" is proven and not
merely displayed. The pack refuses unless `window_summary_5c2.json` was computed over the same bytes
it reads, because a caption measured on another disk is worse than no caption. The seed, the strata,
the populations and the drawn ids are IN the record. Not one `findings` slot carries a value.

**Verified by opening it.** The rendering was served over `127.0.0.1` and read in a browser: the
header law, the comment tables and the leaflet pages all render, the `../data/…` image paths
resolve, and the markup is balanced (checked by `html.parser` as well as by eye). The local server
was stopped and the tab closed.

### What the rendering makes visible — an executor observation, NOT a finding

On page `@atb_market_official:4342` the leaflet prints `135⁹⁰ → 66⁹⁰ −50%` and `152⁹⁰ → 75⁹⁰ −50%`.
The record has promo `66.9` and `75.9` (exact), badge `50.0%` (exact) and old price **`135.2`** and
**`152.2`** — both wrong, by 0.70 UAH each. This is 3.18 (1)'s own flag reproduced on this window's
data ("right as a NUMBER on only 33 of 80 pairs"), and it is also the ruling working: the pair-derived
depths are 0.5052 and 0.5013 against the badge's 0.5000, inside the 2 pp tolerance, so a wrong number
did not become a wrong depth. Recorded here because I saw it while checking that the pack renders.
**No `findings` slot was touched** — the verdict on that row is the operator's, at the table.

---

## The determinism pairs

Two runs of each producer over the same evidence, and the committed artifact beside them:

```
$ scripts/window_summary_5c2.py --out {A,B}
b6d043833f430a6d…  results/window_summary_5c2.json
b6d043833f430a6d…  pair A
b6d043833f430a6d…  pair B

$ scripts/build_validate_pack.py --out {A,B} --page {A,B}
0c57d094102b025c…  results/validate_5c2_pack.json    e2754e8834937017…  results/validate_5c2_pack.html
0c57d094102b025c…  pair A                            e2754e8834937017…  pair A
0c57d094102b025c…  pair B                            e2754e8834937017…  pair B
```

Both pairs are byte-identical, record AND rendering, and both are asserted in the suite against the
COMMITTED file rather than against each other — a pair that only agrees with itself proves the seed
and not the artifact.

## The negative controls, and what each one actually catches

```
$ scripts/build_validate_pack.py --derived-root <sandbox copy, inferences/kopiyochka1.jsonl removed>
<sandbox>/inferences/kopiyochka1.jsonl: not found — SPEC 3.18 (6)(b) builds the sitting from
result files and fails loudly on a missing source. An aggregate computed over the files that
happen to be there is a number about the disk, not about the window.          exit 1, nothing written

$ scripts/window_summary_5c2.py --derived-root <sandbox copy, post_texts/silposilpo.jsonl removed>
the evidence does not carry the registered population — post_text: 42 on disk, 44 registered. The
sitting is shown rows drawn from the window's own output and the window is what the seal names.

$ scripts/window_summary_5c2.py --derived-root <a root whose inferences/ is empty>
<sandbox>/inferences: no channel file — the inference leg has no evidence
```

The three are not the same guard and the difference is Dv320: the pack reads its channel files BY
NAME, so a removed file is a `not found`; the summary reaches them through a GLOB, which cannot see
one go missing, and what catches it there is the population assertion against the seal. The empty-leg
refusal closes the third case, where a glob would have answered with a legal-looking `[]`.

Both negative controls have a positive control. The pack's: the same mirrored root with NOTHING
removed builds and draws the same ten rows (its aggregates rebuilt over the mirror — see Dv321).
The handshake test's: the worker's own answer passes the same guard.

## Verify gate

```
$ set -o pipefail && make check
2303 passed, 2 skipped in 64.30s
$ ruff format --check scripts/window_summary_5c2.py scripts/build_validate_pack.py \
      tests/test_window_summary_5c2.py tests/test_build_validate_pack.py
4 files already formatted            # `make check` does not run the formatter
$ git status --short
(clean)
```

Green after every commit of this session; the verifier was invoked under `set -o pipefail` each
time (Dv313). New tests: 1 for the Dv307 debt, 18 for Deliverable 1, 22 for Deliverable 2 — 41
against the 2 262 the run left.

**$0 held.** No pod, no endpoint, no serverless job, no OpenRouter call, no Telegram client; the one
test that drives the paid driver stubs `runpod_guard.balance` and never reaches a transport. The
only network use in the session was `127.0.0.1:8731`, a local `http.server` opened to look at the
rendering and stopped afterwards.

**`data/derived/` untouched.** Every producer opens it read-only; `tests/test_run_5c2.py`'s
derived-root guard is green in the full suite above, which is the check that would have seen a write.

---

## Deviations

**Dv316 — 3.18 (6) names a fourth comment head and the instrument does not produce one.** The
clause asks the sitting to see "every head's verdict (sentiment, sarcasm, intents, and the brand
attribution)". `T1v2_with_post` returns THREE labels; there is no brand head on the comment
instrument and no model verdict to show. Resolved by showing the deterministic watchlist matcher
(`market_pulse.brands.find_watchlist_brands` over the sent text) and NAMING it as such in the record
field, in the caption and in the rendering — a string match presented as a model's answer is the
worst kind of number at a sitting. Its yield is the finding: **11 rows of 5 075** carry a watchlist
brand. Whether the comment leg should have a brand head at all is a ruling, not an executor's call.
[cause: contract-gap]

**Dv317 — the leaflet draw needed a stratum the contract prescribed only for comments, and six
posts rather than five.** The contract stratifies the COMMENT draw and leaves the leaflet draw
plain. Eleven of nineteen posts yielded a position, so a blind draw of five could have shown the
operator a sitting where "field by field, what made each a POSITION" has no subject. Four are drawn
from the posts that yielded and two from those that did not — six against the clause's "at least
five", both strata and both populations stated in the record, and no row selected for what the model
said about it. The alternative considered and rejected: draw five blind and accept the risk, which
would have made the pack's usefulness a function of the seed. [cause: contract-gap]

**Dv318 — two surfaces, two readings of 3.18 (1) on the extracted old price.** The clause says it
"never reaches a surface that prints it as a price". The AGGREGATE record counts rows that carry one
and prints no value (a test enforces it); the SITTING pack prints the value, flagged, beside the
picture it was read from. The reading: (1) keeps the field precisely so it can be examined, and the
one place examination is possible is in front of the leaflet page. The flag travels with it in both
the record and the rendering. Named rather than assumed silently, because it is a money-path field
and the two surfaces really do differ. [cause: contract-gap]

**Dv319 — `knowledge/hot.md` is modified and absent from the contract's Step-0 listing.** The
contract's live `git status --short` names four paths and `hot.md` is not one of them; the working
tree carried it modified, with the previous day's close in its curated block and this session's
SessionStart refresh in its AUTO-GEN region. Committed by path with the rest of the vault tail
(`7fb98d7`) rather than left dirty, and the commit message says why. Nothing outside the four listed
paths plus this one was staged. [cause: process]

**Dv320 — a glob cannot see one channel file go missing.** `window_summary_5c2.leg_files` reaches
the derived store through `folder.glob("*.jsonl")`, so removing one channel's file returns the
others and every aggregate would silently be about a smaller window. Found by running the negative
control, which refused for the RIGHT reason and the WRONG one — the population assertion against the
sealed 5 075 / 159 / 44, not the missing-source check. Both are kept and the difference is written
into the function's docstring; the empty-leg case was closed with a third refusal. The pack does not
have the hole: it reads its files by name. [cause: model]

**Dv321 — the mirrored-root positive control could not use the committed aggregates.**
`assert_same_evidence` joins the pack's sources to the summary's by NAME, and a sandbox root names
itself, so a complete mirror refuses for a reason that has nothing to do with what the control
tests. Resolved by rebuilding the aggregates over the mirror inside that test and asserting the DRAW
is unchanged, with the name-mismatch refusal exercised separately on its own. A control that fails
for an unrelated reason is not a control. [cause: tooling]

**Dv322 — the re-render proof has a blind spot, and a failed control is what found it.** The
`sent_parts` guard re-runs `build_messages` on its own split and compares. The first attempt at a
negative control edited the comment text INSIDE the delimiters — and it round-tripped, because a
rendering is defined by its content: any in-delimiter edit is a valid rendering of the edited text
and no re-render can see it. What the guard actually catches is a rendering `build_messages` could
NOT have produced (a stripped-away post, a foreign prompt, a mangled delimiter), and the test now
uses one. The evidence row's own integrity against tampering is the store's problem, not this
function's, and saying so is the honest scope. [cause: model]

## Process signals

1. **A deviation can be true of the revision it was written against and false of the session that
   wrote it.** `git log -S` on the mechanism, not a re-read of HEAD, is what dated Dv307's claim.
2. **Two of this session's own controls first passed for the wrong reason** (a "control" field that
   the pin actually compares; an in-delimiter edit that re-renders by construction). A guard that
   fires still has to be asked WHY it fired.
3. **A hand-typed money number has no carrier a month later.** `--already-usd` should read the
   previous leg's `step_spent_usd` and require an override to be LARGER, or record its provenance.
4. **The strongest guard here cost one line: rebuild the input and compare bytes.** Re-rendering the
   split beat every delimiter rule I could have written for it.
5. **`make check` does not run the formatter**, and `ruff format` moved the producer's own sha256 —
   which is inside its record. Format first, generate second, or the byte-identical test is red.

## Open questions for the team lead

1. **Dv316 — the comment brand head.** The sitting will be shown a string matcher. Whether the loop
   should acquire a real brand head for comments, or whether the watchlist match IS the answer for
   this category, is a ruling.
2. **Dv318 — the old price at the sitting.** The pack prints it, flagged. If the reading is wrong,
   the fix is one field in `position_block` and a rebuild.
3. **The sitting's own record.** `findings` is a skeleton in a committed file; whether the filled
   version supersedes it in place or lands as a new record (`results/validate_5c2_returns.json`, the
   `read_sitting_returns.py` pattern) is a decision the sitting should not discover at the table.
