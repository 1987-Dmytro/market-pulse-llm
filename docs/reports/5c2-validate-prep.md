# 5c2-validate-prep — the sitting pack, and three report debts

The sitting of SPEC 3.18 (6) can now be held: `results/validate_5c2_pack.html` shows six leaflet
posts (56 pages, 36 positions) and five comments, original beside verdict, drawn under seed 42 from
the window's own output and captioned with the aggregates in `results/window_summary_5c2.json`. All three debts of the
accepted run report are paid by measurement — Dv307's hole is CLOSED at HEAD and the amendment says
so with the commit that closed it, the $0.8451 is named as a hand-typed conservative reading with
its consequence priced both ways, and the 55th call is the `assert_serving` handshake, verified on
both legs. `make check` is 2 309 passed / 2 skipped, nothing cloud-touching ran, and nothing under
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
**$0.8160 – $0.8344** — a RANGE, because the session has one 60 s idle tail and nothing on disk says
which leg it belongs to. No balance of $10.2364436571 — the reading that would produce the typed
number — appears in any file, log or record in the repo, and the session transcript is not on disk.

It is legal because Dv33 makes the balance delta a **FLOOR** (`positions_gm4_skub.spend_now`'s
docstring: "RunPod settles it minutes to hours late"), so the true spend was ≥ $0.8230 and a bigger
number is the conservative direction. The
consequence is one-way and checkable: a larger `already_usd` SHRINKS the (10)(a) budget, so the
typed number could only make the gate stricter. Priced both ways the verdict does not move —
projected $7.0196 against $7.1549 (typed) or $7.1770 (ledger), GO under both, while the registered
conservative corner $7.4840 exceeds both budgets.

**And the run report's own arithmetic settles which number is the true one.** Its Step 4 says
"Session: $7.5309 of the $8.00 cap" and three lines later "$6.7079 for the comment leg on top of
$0.8451" — but `6.7079 + 0.8451 = 7.5530`, $0.0221 over the total, while `6.7079 + 0.8230 = 7.5309`
closes to the cent against the balance delta. The typed number does not survive its own report's
decomposition; the ledger's does. Both the addendum and a bracketed marker on the sentence itself
now say so, without editing the accepted line. Found by the adversarial review pass below, not by
the debt's own arithmetic — which had checked the gate and never the decomposition.

The addendum in `docs/reports/5c2-run.md` carries the table and the rule it leaves behind.

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

`scripts/window_summary_5c2.py`, 73 KB of record, one second to build, reading `data/derived/`
alone plus the sealed registration. What it says about the window:

| leg | rows | what the aggregate carries |
|---|---:|---|
| comments | 5 075 | 5 075 scored, **0 unreadable**; **1 361 sent with an EMPTY `<comment>` block**; sentiment 4 144 neutral / 661 positive / 270 negative; sarcasm **0.0132** on the scored rows; intents 553 price · 245 taste · 184 availability · 161 service · 138 quality · 17 packaging, **3 944 rows with no intent**; languages ua 2 606 · other 1 925 · ru 493 · en 51 |
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

**A quarter of the comment leg was sent with no text at all.** Recovering the sent string made a
class visible that no counter in the run report has: **1 361 of the 5 075** comments reached the
model as an EMPTY `<comment></comment>` block — a sticker, a photo, a voice note. Every head
answered them anyway, and all 1 361 came back with `intents: []`, so **a third of
`rows_with_no_intent: 3944` is not a statement about what the audience talks about**. @matusi_ukr
carries 1 172 of them — 43% of that channel's own 2 717 rows. Counted as its own class per channel
and total rather than dropped: the rows were bought and they are inside the registered 5 075, and a
distribution that does not say how many of its rows had no text is a distribution about the wrong
thing. A shown empty row says which class it is instead of being a blank box beside three confident
labels.

**No clock and no git block**, so the record is byte-identical across runs and
`tests/test_window_summary_5c2.py::test_the_committed_record_is_what_the_producer_writes_today`
regenerates it and compares bytes. Every number in it re-derives or the suite is red.

## Deliverable 2 — `results/validate_5c2_pack.json` + `.html` (`8b6cbf4`)

```
$ PYTHONPATH=src python3 scripts/build_validate_pack.py
wrote results/validate_5c2_pack.json  sha256 2fad5339ecb721d9…
wrote results/validate_5c2_pack.html sha256 cd928f38fbc4d244…
  seed 42 · 6 leaflet posts, 56 pages, 36 positions
  5 comments from ['@matusi_ukr', '@mandziak', '@VARUS_channel', '@kopiyochka1', '@klopotenkofood']
  findings: 6 post slots, 36 position slots, 5 comment slots — all empty
```

**The draw, and its two strata.** Comments: one row from each of the five channels with the most
rows in the window, seeded within each — the contract's own prescription, and it exists because two
channels are 73.8% of the window. Leaflets: the nineteen posts split by whether any page of them
yielded a position (11 / 8), four drawn from the first and two from the second. That second stratum
is a deviation from the letter of the contract and is argued in Dv317: a post that yielded nothing
cannot answer "field by field, what made each a POSITION", and a blind draw of five from nineteen
could have shown the operator one such post. Both strata are stated in the record with their
populations. **Precisely:** the leaflet stratum keys on whether the instrument PRODUCED output —
which is something the model did — and never on whether that output looks correct; no row in either
stratum was chosen for what its verdict SAYS. The draw is reproducible from the seed and the record
alone, and a test redoes it.

**The draw was rebuilt once, and both versions are here.** The first build re-seeded each stratum
with the same `Random(42)`, which is `build_sitting_pack.draw`'s shape — and one `Random(42)` asked
for one element out of pools of 242, 223 and 222 answers the same INDEX for all three. Measured
after the fact: rank **163 of 242, 163 of 223, 163 of 222** — three of five comments at one
position. Nobody picked those rows and their ids differ, but five draws sharing an index are not
five independent draws. The seed is now derived per stratum (`f"{SEED}:{stratum}"`, recorded in the
record as `seed_derivation`) and the ranks spread: 218/2717, 158/1026, 224/242, 128/223, 126/222.
The last two are within two of each other on pools of nearly equal size and come from different
streams — a coincidence, not the old shared one.

| | first build | after the fix |
|---|---|---|
| comments | `@matusi_ukr:580182` `@mandziak:48186` `@VARUS_channel:21270` `@kopiyochka1:392342` `@klopotenkofood:21280` | `@matusi_ukr:576430` `@mandziak:48066` `@VARUS_channel:21629` `@kopiyochka1:392092` `@klopotenkofood:21239` |
| leaflet posts | 4340 · 4350 · 4370 · 4377 · 4401 · 4508 | 4340 · 4370 · 4391 · 4401 · 4436 · 4446 |
| pages / positions | 51 / 48 | 56 / 36 |

Both are printed because a draw that changes after someone has seen it is either auditable or it is
a redraw. `8b6cbf4` holds the first, `d69c812` the second; the fix is a defect fix and not a taste.

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
against the `image_sha256` the run recorded — 56 of 56 agree, so "as it was SENT" is proven and not
merely displayed. The pack refuses unless `window_summary_5c2.json` was computed over the same bytes
it reads, because a caption measured on another disk is worse than no caption. The seed, the strata,
the populations and the drawn ids are IN the record. Not one `findings` slot carries a value.

**Verified by opening it.** The rendering was served over `127.0.0.1` and read in a browser: the
header law, the comment tables and the leaflet pages all render, the `../data/…` image paths
resolve, and the markup is balanced (checked by `html.parser` as well as by eye). The local server
was stopped and the tab closed.

**One defect shipped in it and was fixed before this report was final.** The contract makes this
rendering the ONE artifact exempt from the English rule and names its language — "which is in
Russian". Three of its label constructs were UKRAINIAN: `yes_no` answered «так»/«ні», the comment
header printed «мова», and the empty-intent fallback read «— (жодної з шести)». They are the
module's own voice, not the corpus's — every string that comes off a row goes through `esc()`
untouched — and the STATUS.md exemption is scoped to Russian by name. Now «да»/«нет», «язык» and
«— (ни одной из шести)», with
`tests/test_build_validate_pack.py::test_the_rendering_speaks_russian_in_its_own_voice` holding the
script to it: the four Ukrainian-only letters plus «мова», which those letters cannot catch.

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
7760d32d0ffec80c…  results/window_summary_5c2.json
7760d32d0ffec80c…  pair A
7760d32d0ffec80c…  pair B

$ scripts/build_validate_pack.py --out {A,B} --page {A,B}
2fad5339ecb721d9…  results/validate_5c2_pack.json    cd928f38fbc4d244…  results/validate_5c2_pack.html
2fad5339ecb721d9…  pair A                            cd928f38fbc4d244…  pair A
2fad5339ecb721d9…  pair B                            cd928f38fbc4d244…  pair B
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
2309 passed, 2 skipped in 64.19s
$ ruff format --check scripts/window_summary_5c2.py scripts/build_validate_pack.py \
      tests/test_window_summary_5c2.py tests/test_build_validate_pack.py
4 files already formatted            # `make check` does not run the formatter
$ git status --short
(clean)
```

Green after every commit of this session; the verifier was invoked under `set -o pipefail` each
time (Dv313). New tests: 1 for the Dv307 debt, 20 for Deliverable 1, 26 for Deliverable 2 — 47
against the 2 262 the run left.

**$0 held.** No pod, no endpoint, no serverless job, no OpenRouter call, no Telegram client; the one
test that drives the paid driver stubs `runpod_guard.balance` and never reaches a transport. The
only network use in the session was `127.0.0.1:8731`, a local `http.server` opened to look at the
rendering and stopped afterwards.

**`data/derived/` untouched.** Every producer opens it read-only, and the proof is a hash rather
than an assertion: `results/window_summary_5c2.json` records the sha256 of all 38 derived files, and
`test_the_record_carries_the_producer_and_every_source_it_read` re-hashes every one of them against
the record on each suite run. Independently, every count Deliverable 1 computes off those bytes —
5 075 / 159 / 44 / 106 / 39 and the 2 + 1 unreadable — equals what `docs/reports/5c2-run.md` recorded
before this session existed. (`data/derived/` is gitignored, so there is no HEAD to diff and no
baseline was taken before the first write-capable action; that is the gap those two checks close.)

---

## The adversarial review pass, and what it caught

The deliverables were re-read by a fan-out of five independent lenses — contract compliance, law and
money path, code correctness, whether the tests actually test, and the report as evidence — each of
whose findings was then handed to a separate agent instructed to REFUTE it. 34 agents, 24 findings
raised, **10 survived refutation**. Two were already fixed (Dv323's correlated draw, Dv324's
text-less rows) and one was a duplicate; the other six were real and are fixed above and below:

| what it caught | where it was |
|---|---|
| Ukrainian labels in a rendering the contract fixes as Russian | `build_validate_pack.py` — three constructs |
| `6.7079 + 0.8451 ≠ 7.5309` in the accepted run report's own Step 4 | the debt-2 arithmetic I had not run |
| the "FLOOR / minutes to hours late" docstring is `spend_now`'s, not `spend_or_note`'s | the addendum's attribution |
| the comment half of the draw had NO reproducibility test — the half Dv323 was in | `test_the_draw_is_reproducible_from_the_seed_alone` |
| `test_no_old_price_value_ever_reaches_this_record` walked three blocks while its docstring promised the whole record | the test that guards a money-path law |
| "captioned with BOTH denominators" was false of the brand row — window only | the caption builder and the report sentence |

Every one is a claim the artifacts contradicted, not a preference. The last three are the sharpest:
a guard whose docstring promises more than its body does, a reproducibility test that covers the leg
that was fine, and a report sentence that says "each" about four rows when it is true of three.

## Deviations

**Dv316 — 3.18 (6) names a fourth comment head and the instrument does not produce one.** The
clause asks the sitting to see "every head's verdict (sentiment, sarcasm, intents, and the brand
attribution)". `T1v2_with_post` returns THREE labels; there is no brand head on the comment
instrument and no model verdict to show. Resolved by showing the deterministic watchlist matcher
(`market_pulse.brands.find_watchlist_brands` over the sent text) and NAMING it as such in the record
field, in the caption and in the rendering — a string match presented as a model's answer is the
worst kind of number at a sitting. Its yield is the finding: **11 rows of 5 075** carry a watchlist
brand. Whether the comment leg should have a brand head at all is a ruling, not an executor's call.

This head is also the ONLY reason either producer reads a file outside `data/derived/` and
`results/`: the watchlist lives in `config/registry.yaml`, and both scripts reach it through the
sealed registration's own pin (`registry_through_the_seal`), so a registry that moved since the run
is a refusal rather than a differently-measured brand column. The pack has to run the SAME matcher
on the shown row that the aggregate beside it was built with, which is why the read is in both.
[cause: contract-gap]

**Dv317 — the leaflet draw needed a stratum the contract prescribed only for comments, and six
posts rather than five.** The contract stratifies the COMMENT draw and leaves the leaflet draw
plain. Eleven of nineteen posts yielded a position, so a blind draw of five could have shown the
operator a sitting where "field by field, what made each a POSITION" has no subject. Four are drawn
from the posts that yielded and two from those that did not — six against the clause's "at least
five", both strata and both populations stated in the record. The claim the record makes about it
is the precise one: the stratum keys on whether the instrument PRODUCED output — something the model
did — and never on whether that output looks correct, so no row is chosen for what its verdict says.
The alternative considered and rejected: draw five blind and accept the risk, which would have made
the pack's usefulness a function of the seed.

One shape of `build_sitting_pack.py` is deliberately NOT reused: its **seeded shuffle**. There the
shuffle exists so that a row's POSITION in the file cannot be read off as its stratum — the pack is
a blind gate. This one is the opposite by clause: 3.18 (6) has the strata stated in the record and
printed beside every row, so a shuffle could hide nothing and would only cost the operator the
ability to walk the leaflets in msg_id order. The posts are sorted by id, which interleaves the two
strata anyway (4340 · 4370 · 4391 · 4401 · 4436 · 4446), so the ordering carries no signal either.
[cause: contract-gap]

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

**Dv323 — the seeded draw was CORRELATED across strata, and only a rank measurement showed it.**
`build_sitting_pack.draw`'s shape re-seeds every stratum with the same constant, and one
`Random(42)` asked for one element out of pools of 242, 223 and 222 answers the same INDEX for all
three: the first build of this pack drew rank 163 of each. The rows were not picked and their ids
differ, so nothing in the record, the tests or the rendering could have shown it — it took computing
each drawn row's rank inside its own sorted channel. Fixed by deriving the seed per stratum
(`f"{SEED}:{stratum}"`, with `seed_derivation` in the record so reproducibility is unchanged); both
draws are printed in this report because a draw changed after it was seen has to be auditable. The
house's own `build_sitting_pack.py` still has the shape and is NOT touched here: its three strata
are 382/671/859 rows and 100 draws each, a different exposure, and re-drawing a pack whose 300
verdicts are already in `results/verdicts_45g5.json` is not a fix. [cause: model]

**Dv324 — 1 361 of the 5 075 comments were sent to the model with an EMPTY `<comment>` block.**
26.8% of the paid comment leg — stickers, photos, voice notes — and the run report has no counter
for it. Found by recovering the SENT string per row for the language column, not by looking for it.
All 1 361 came back with no intent, so `rows_with_no_intent: 3944` is a third made of rows that had
no text; @matusi_ukr carries 1 172 of them, 43% of that channel. Counted as its own class in the
aggregate rather than dropped from the population, because the rows were bought and are inside the
registered 5 075 — the class is a caveat on every distribution, not a correction to one. Whether the
loop should skip a text-less comment before paying for it is a ruling for the next contract; nothing
was re-scored here. [cause: model]

## Process signals

1. **A deviation can be true of the revision it was written against and false of the session that
   wrote it.** `git log -S` on the mechanism, not a re-read of HEAD, is what dated Dv307's claim.
2. **A draw can be reproducible, unpicked and still not random** (Dv323). Nothing in a record shows
   it; measure each drawn row's RANK inside its own stratum, which is one line and the only check
   that would have.
3. **Two of this session's own controls first passed for the wrong reason** (a "control" field the
   pin actually compares; an in-delimiter edit that re-renders by construction). A guard that fires
   still has to be asked WHY.
4. **Reconstructing the input beat every rule I could have written about it.** Re-rendering the
   split proved the cut, and it is what surfaced Dv324 as a side effect.
5. **A test's docstring can promise more than its body delivers, and only a mutation shows it.**
   Two of this session's guards said "the whole record" and "the draw" while walking three blocks
   and one leg. Both were written by me and both read as thorough.

## Open questions for the team lead

1. **Dv316 — the comment brand head.** The sitting will be shown a string matcher. Whether the loop
   should acquire a real brand head for comments, or whether the watchlist match IS the answer for
   this category, is a ruling.
2. **Dv318 — the old price at the sitting.** The pack prints it, flagged. If the reading is wrong,
   the fix is one field in `position_block` and a rebuild.
3. **Dv324 — the 1 361 text-less comments.** They were bought and labelled. Whether the loop should
   skip a comment with no text before paying for it, and whether the phase's numbers should ever be
   reported on the 3 714 rows that HAD text, is a ruling — nothing was re-scored here.
4. **The sitting's own record.** `findings` is a skeleton in a committed file; whether the filled
   version supersedes it in place or lands as a new record (`results/validate_5c2_returns.json`, the
   `read_sitting_returns.py` pattern) is a decision the sitting should not discover at the table.
