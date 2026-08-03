---
type: decision
id: dec-2026-08-03-45g3-sitting-gates
date: 2026-08-03
status: accepted
tags: [decision]
---

# All three strata failed, the guideline grew a v2.1, and the whole batch goes back

**Context:** [[45g2-captions-and-quiz-rulings]] resealed the sitting — 300 gated precheck rows in
three strata of 100, 75 emptied rows to decide by hand, 14 unreadable ones — with the bar
registered before the pack went out: a row is `correct` only if **all four** fields are, agreement
is per stratum on its own denominator, and a stratum below **0.90** sends back its **whole**
population rather than the hundred judged. The sitting came back filled. This ADR records what its
numbers say and what follows.

## (a) The capture changed hands, and said so before it did

The operator judged 36 gated rows itself. **Amendment 2 of `docs/quiz-sitting-45g-log.md`**,
registered before any tally was shown, delegated the rest to a team-lead LLM against two
safeguards: the operator adjudicates every row the team lead flags as contested, and a **blind
seeded twenty** of the team lead's own `correct` rows goes back to the operator at a bar of 18/20,
with the void-fallback written down in advance. It came back **20/20**
(`docs/quiz-sitting-45g-check20.md`), so the triage verdicts stand.

**The provenance is renamed because of it.** This is not the SPEC §8 operator calibration, and
every record downstream says **"team-lead-LLM triage with operator adjudication and operator
spot-check"** — one constant, `read_sitting_returns.PROVENANCE`, because four hand-typed copies
drift. Per-row authorship is in the `notes` column and survives into the merged rows.

## (b) The gate: 88 / 89 / 81, and all three are FAIL

`scripts/read_sitting_returns.py` rebuilds the sealed pack from the batch the manifest pins,
reproduces its sha256, compares the returned rows cell by cell on the seven frozen columns, and
only then counts. `results/sitting_45g_gates.json`:

| stratum | correct / 100 | agreement | bar | verdict | population sent back |
|---|---|---|---|---|---|
| `service-rich` | 88 | 88.0% | 0.90 | **FAIL** | 382 |
| `short-text <= 30 chars` | 89 | 89.0% | 0.90 | **FAIL** | 671 |
| `general` | 81 | 81.0% | 0.90 | **FAIL** | 859 |
| total (reported, never gated) | 258 | 86.0% | — | — | **1,912** |

The recount matches what the capture log records after its own one-row correction — 258/42 — and a
disagreement there was a pre-registered stop, not something to reconcile.

**What failed, by field.** Of the 42 refusals the notes name `unclear` on **22**, `intents` on
**17**, `sarcasm` on **3** and `sentiment` on **1** — 43 mentions over 42 rows, because
`@msuaaaa:12621` names two. That distribution is why v2.1 is not an intents patch: a revision
touching only the label block would have addressed a third of what the sitting refused, and
`unclear` is the single largest class of error.

**No row is fixed one at a time.** The prompt's remedy for an adjudicated error applies inside a
**passed** stratum, and there are none — every one of the 42 sits in a stratum whose whole
population goes back. `incorrect_in_passed_strata` is in the gate record and is empty; that is the
artifact, not a sentence in a report.

## (c) What merged, and what did not

`scripts/merge_sitting_returns.py`, record `results/merge_45g3.json`:

- **Nothing from the 1,912.** They stay model output with an `llm-precheck` annotator. The merge
  path for an accepted stratum is deliberately **unbuilt** and stops the run if one ever passes:
  none of the 1,912 ids exists in any source file today, so accepting a stratum is a decision
  about which file its rows join and under what annotator, and code written for that with nothing
  to exercise it is guesswork shipped into the one place a mistake is unrecoverable.
- **The 75 emptied rows merged** into the `intents` column of the staged `_tax2` copies — 45 moved
  a label, 11 answer `[]`. `[]` is a filled cell and blank is not, so every cell had to parse as a
  JSON list rather than pass a truthiness test.
- **The 14 unreadable rows joined** the staged files at their **source file's own position** (6 +
  6 + 2). They had never been staged: the re-labeller refused them four passes running, so they
  sat on their v1 labels. A `_tax2` copy exists to diff against its source, and rows appended at
  the end would show up in that diff as everything after them moving.

**The bug worth writing down.** The first draft recorded, in its `fixes` block, the `intents`
value it found on disk as `old`. For 27 of the 75 that value is a **later fix's** answer, not the
re-labeller's — and `measure_empty_drop.reversals` takes the last fix per id, so the reversal
restored the 4.5g model answer instead of the `[]` the re-labeller produced. The 97 stopped
deriving and came back as 70. The history's `old` means *what the re-labeller said*; what this run
overwrote is a separate field, `replaced`. The check that caught it ran after the files were
already rewritten, which is the same shape of defect 4.5g2 recorded — so the guard that can run
early now does: a row that would **join** the emptied class by being added stops the merge before
a byte is written.

## (d) Guideline v2.1, and the prompt that carries it

`docs/annotation/comments.md` grew a **`v2.1 changelog`** section: eight numbered rulings with the
row ids they were decided on, plus the four the operator ruled on the redo file. Nothing above
that line is edited — v2.1 is additive law, not a moved label space. In substance: off-topic
banter is `unclear`; unsigned support boilerplate is the corporate voice and the marker list is
indicative, not exhaustive; bare praise of retailer conduct is `["service"]`, symmetric with the
complaint; a promo-mechanics question is `["service"]` and not `[]`; a direct accusation against
the retailer outranks a commenter addressee; a food-preference joke is `["taste"]`; a mock
quotation is `sarcasm: true`, and so is a mock-elevation joke (the operator's own same-day
amendment to `@msuaaaa:12621`).

`prompts.SETTLED_CASES` renders those eight as instruction lines, and two revisions are registered
**beside** the existing ones, never over: **`T1v2.1`** `e131dc06…` and
**`precheck_v2.1_with_post`** `95d506c4…`. Derived through the same `_swap` chain as their v2
siblings, so `precheck_v2.1_with_post` minus the settled-cases block is byte-identical to
`precheck_v2_with_post` — a difference in the returned labels is the rulings and not a rewording.
`TASKS` is still `("T1","T2")` and the eight older hashes are unmoved.

**They are registered in `src/market_pulse/prompts.py`, not in `config/registry.yaml`.** That file
registers sources, taxonomy and the brand watchlist and has no prompt section; `PROMPTS` is where
a prompt's SHA256 comes from, and therefore the only place "old SHAs immutable" means anything.

## (e) The second round, and the pack that gates it

All three strata failed, so all 1,912 rows went back — same model, same pinned endpoint, same
parent posts and the same tagged surrogates for the media-only ones. The only thing that moved is
the prompt. `scripts/rerun_failed_strata.py`, ledger `results/spend_45g3.json` anchored before the
first request against a **$1.50** cap.

The gate on it is `data/annotation/wave2_45g3/wave2_100.csv` — **one hundred rows in one draw**,
seed 42, blind, `verdicts_present: 0`, bar unchanged at 0.90. Two departures from the pack it
replaces, both recorded in `results/wave2_45g3_manifest.json`:

- **One frame, not three.** The strata did their work in the first sitting: they located the
  weakness. The question now is whether the batch as a whole clears the bar. The cost is named
  rather than hidden — a pass here can still hold one class below 0.90, and the per-stratum table
  above is where a reader goes for that.
- **The 300 already-judged rows are out of the frame.** The v2.1 rulings were distilled from those
  verdicts, so a second round scored on them would be measured against its own source. The frame
  is the remaining rows of the batch, and the exclusion is by id and listed in the manifest.

The re-run record also reports how the 300 judged rows moved, split by the verdict they carried.
That is **in-sample by construction** and is a diagnostic, never the gate — and it is what turned
this step into a negative result.

## (f) The v2.1 re-run regressed, and the cap forbids fixing it in this phase

All 1,912 rows came back — 17 needed a second pass, which is the shape 4.5g2 already recorded —
for **$0.7429** of the $1.50 cap. And the diagnostics say the revision made the batch worse, not
better:

| | 4.5g2 (v2 prompt) | 4.5g3 (v2.1 prompt) |
|---|---|---|
| `service` | 689 | **138** |
| rows with no intent | 809 | **1,366** |
| `price` | 110 | **313** |
| `sarcasm` | 87 | **197** |
| `unclear` | 612 | 477 |

**1,153 of 1,912 rows (60%) moved a field**, and — the sign that should not appear — **172 of the
258 previously-`correct` rows moved with them**, against 25 of 42 of the `incorrect` ones. A
revision that fixes what a gate refused should move the refused rows and leave the accepted ones
alone; this did close to the opposite. And on the rows whose right answer the sitting wrote down
outright — 29 of the 42, parsed from the verdict notes rather than listed by hand — the v2.1 run
now gets **10**. All three P5 promo-question rows still answer `[]` where the ruling says
`["service"]`, and three of the four P6 rows are still `unclear: false`.

**The likely mechanism is form, not substance.** `SETTLED_CASES` is eight lines dense with
negations — *"is not a consumer reaction at all"*, *"never `price`"*, *"is not a reaction to
judge"* — and it sits last before the answer format, ending on *"the comment carries no intent"*.
The label space moved the way a model reading those negations positively would move it: questions
collect `price`, everything about the retailer collapses to `[]`. The rulings themselves are the
operator's and are not in doubt; how they were rendered is.

**This phase cannot correct it.** A corrected re-run of the same пласт estimates at **$0.8492**
(measured against this pricing at the start of the phase) and the headroom is **$0.7571**, so it
does not fit; a projected overrun is a pre-registered stop, not a thing to trim the scope around.
So the wave-2 pack is sealed as instructed and carries the measurement: `batch_health` in its
manifest — the distribution shift, the in-sample split, the 10-of-29 and the headroom, all
derived — and the warning is the first thing in the README the operator would open.

**Two guards changed on the way.** The cost estimate was priced over the whole scope rather than
over what a resume would actually buy, so a 17-row remainder was refused by an estimate for
1,912; it now prices `pending`. And the frame of the wave-2 pack excludes any row the re-run did
not answer — such a row keeps the previous prompt's labels, and one inside the hundred would gate
the old prompt under the new one's name. Today that set is empty, and the manifest says so.

## Consequences

- **Nothing merges from the up-label precheck**, and 4.5h inherits that. The three strata gates
  are still the only thing that can accept those rows.
- **The staged `_tax2` files now hold 89 rows the sitting decided** and carry a `sitting-45g`
  annotator, which is what a distribution over `annotator` will show them as.
- **v2.1 is law for anything labelled from now on**, the model included. Test v4 — a re-label of
  the frozen test set — is where it reaches gold, and that is still gated behind lifting the guard
  `relabel_intents.py` puts on frozen ids.
- **The next sitting is one file and about 40 minutes — and it is probably not worth holding
  yet.** Judging the wave-2 hundred, and re-judging `precheck300`, are both outside this phase.
  The decision in front of the operator is whether to raise the cap for one corrected re-run
  (rewrite `SETTLED_CASES` in the positive voice, probe it on ~100 rows first) or to judge the
  hundred as it stands.
- **A prompt revision is an instrument change and should be probed before it is bought at
  scale.** A hundred paid rows would have cost about four cents and would have shown the
  distribution inverting. The smoke run proves the write path; it cannot see this.
- **The 54 dual-home ids stay untouched** (4.5h), and so does everything Phase-4 or frozen.
