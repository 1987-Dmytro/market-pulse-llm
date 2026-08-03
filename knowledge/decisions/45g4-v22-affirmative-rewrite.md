---
type: decision
id: dec-2026-08-03-45g4-v22-affirmative-rewrite
date: 2026-08-03
status: accepted
tags: [decision]
---

# The rulings were right and the sentences were backwards: v2.2, bought a hundred rows at a time

**Context:** [[45g3-sitting-gates]] ends on a negative result. All three strata failed the
sitting (81 · 88 · 89 against a bar of 0.90), the whole batch of 1,912 rows went back under
`precheck_v2.1_with_post`, and the re-label came back **worse than the one it replaced**: 1,153
rows (60%) moved a field, 172 of the 258 rows the sitting had accepted moved with them against
25 of the 42 it had refused, and of the 29 rows whose right answer the verdicts stated outright
the revision got 10. A corrected re-run did not fit the cap and the decision went to the
operator. This ADR records what the operator chose and what it is allowed to conclude.

## (a) The decision: the form of the block changes, and nothing else does

The eight rulings are the operator's and are not in question — they were adjudicated row by
row and the guideline carries them. What is in question is how they reached the model.
`prompts.SETTLED_CASES` states them as **negations**: *"is not a consumer reaction at all"*,
*"never `price`, and never no intent at all"*, *"is not a reaction to judge"*, ending on *"the
comment carries no intent"*. A rule in that voice names a value the model must **not** write
and leaves it to guess the one it must — and the label space moved the way a model reading
those negations positively would move it: `price` 110 → 313, rows with no intent 809 → 1,366.

**v2.2 is those same eight rulings in the form "condition → field = value".** The text was
written by the team lead and transcribed verbatim; `docs/annotation/comments.md` gains a
**`v2.2 changelog`** marked **FORM-ONLY**, with a line-by-line old→new table. No annotator
behaviour changes, no label space moves, and the eighth line still restates a v2 clause rather
than adding law.

**One variable, deliberately.** `prompts.UNCLEAR_RULE` is untouched — it was already in v2,
which scored 86% — and the block is inserted at exactly the position v2.1's occupied. Both are
asserted by test, because either would be a second variable and neither run could then be
charged to the rewrite. Registered **beside**, never over: `T1v2.2` `8542a1d5…` and
`precheck_v2.2_with_post` `02e804b2…`, with the ten older hashes unmoved.

Two guards ship with it. A **transcription guard** holds the canonical block as a second
literal, wrapped at a different width, and compares whitespace-insensitively — the realistic
defect in a transcription is a space lost at a line join, and nobody reviews a copy. A
**negation guard** greps the constant for `not|never|no|none|neither|nor|n't` and fails on a
hit; its negative control asserts the same regex still fires on `SETTLED_CASES`, so the guard
cannot pass by matching nothing.

## (b) Alternatives rejected

- **Move the block as well** (higher in the prompt, or before the label definitions). Plausible
  — position effects are real — but it is a second variable in a run that costs $0.04 to make
  attributable. If the affirmative rewrite fails, position is the next single thing to try.
- **Re-run all 1,912 rows immediately under v2.2.** $0.8492 against $0.7571 of headroom under
  the $1.50 cap. A projected overrun is a pre-registered stop, and this is the same mistake
  4.5g3 made in the other direction: it bought the whole population before knowing whether the
  instrument worked.
- **Judge the wave-2 hundred as it stands.** Its own README opens with the warning against it:
  the hundred gates the v2.1 labels, and those labels measure as a regression. An evening of
  operator time to confirm a number already visible in `batch_health`.
- **Keep v2.1 and fix the rows by hand.** The 42 refusals are spread across three failed strata
  and a stratum below the bar sends back its whole population by pre-registered rule; hand-fixes
  apply inside a passed stratum, of which there are none.

## (c) The probe, pre-registered before a request was made

`results/v22_probe_plan.json` is written and **committed** before the first API call, and the
runner refuses to start unless git reports that file tracked and unmodified. The plan names its
own sample, its reference labels and its thresholds:

- **100 rows**: all 42 the sitting called `incorrect`, plus 58 of the 258 it called `correct`,
  drawn with `random.Random(42)` over the id-sorted list. Every id and its stratum is in the file.
- **Reference labels** are the sealed sitting pack's four judged fields, read only after a
  rebuild of that pack reproduces `sealed_sha256` `c0d7656f…` — the same machinery STOP-RULE 1
  used, so the labels being scored against are provably the ones the operator ruled on.
- **`preserved`** (the 58): v2.2 equals the pack on all four fields.
- **`fixed`** (the 29 whose verdict note states an answer the 4.5g3 parser can read): every
  field the ruling names matches it, **and** every field it does not name still equals the pack.
  The other 13 refusals are reported moved/unmoved and gate nothing — their notes state the
  error without stating the value. **All three P5 rows and three of the four P6 rows are among
  those 13**, so the two families below are diagnostics and not gate arithmetic.
- **The gate, one attempt, no retry:** PASS = `preserved ≥ 55/58` **and** `fixed ≥ 24/29`.
  KILL = `preserved < 52/58` **or** `fixed < 20/29`. Between the two, the operator decides on
  the numbers. A failed gate closes the form-only hypothesis rather than inviting a third
  wording.

**What this probe cannot do.** It is `in_sample: true` and says so in its own file: the v2.1 and
v2.2 rulings were both distilled from these very verdicts, so the absolute numbers are
optimistic by construction. It authorises the **next purchase** and never batch acceptance —
only a fresh blind hundred can do that. Its value is the paired comparison: v2.1's own
`preserved` and `fixed` counts on the identical rows are computed from
`uplabel_precheck_45g3.jsonl` and written into the plan as the reference row, so the probe reads
as v2.2 against v2.1 on the same 100 rows rather than against a corpus average.

One asymmetry is named in the plan rather than discovered afterwards: 19 of the 29 rulings are
`unclear: true`, and the guideline excludes an unclear row's other labels from scoring — so a
row where v2.2 correctly sets `unclear` but also moves `intents` counts as **not fixed** under
the pre-registered rule. That rule stands as written. The plan also pre-registers a secondary
breakdown — how many of the 29 match every *named* field regardless of unnamed drift — because
"the rulings did not land" and "the rulings landed and the row moved elsewhere" are different
findings and the difference has to be decidable without a second run.

## (d) The probe came back KILL — and the rewrite still worked

One attempt, $0.0365, 100 of 100 rows answered, nothing unusable
(`results/v22_probe_results.json`).

| | v2 (the pack) | v2.1 | **v2.2** | PASS at | KILL below |
|---|---|---|---|---|---|
| `preserved` | 58/58 | 20/58 | **37/58** | 55 | 52 |
| `fixed` | 0/29 | 4/29 | **9/29** | 24 | 20 |

**Verdict: KILL**, on both counters, by the rule registered before the run. Task 4 is skipped
and nothing is pinned for the wave-2 hundred.

And the rewrite is not what failed. On the identical rows, under the identical scorer, v2.2
preserves **37 where v2.1 preserved 20** and fixes **9 where v2.1 fixed 4**. The unconfounded
view of the improvement is the accepted rows alone, where any movement is a loss:

| lost an accepted row by moving | `intents` | `unclear` | `sarcasm` | `sentiment` | rows lost |
|---|---|---|---|---|---|
| v2.1 | 28 | 7 | 6 | 6 | 38 |
| **v2.2** | **14** | **6** | **2** | **1** | **21** |

(The per-field counts over all 100 rows — `intents` 31 against 48, `sentiment` 4 against 9,
`unclear` 13 against 16, `sarcasm` 2 against 9 — are in the record as the prompt asked, but they
sum movement on the 58 accepted rows, where it is a loss, with movement on the 42 refused ones,
where it is the goal. The table above is the comparable one.)

The clearest single case is the **P5 family** — the three promo-mechanics questions: v2.1
answered `[]` on all three, v2.2 answers `["service"]` on all three. Their notes name the value
without naming the field, so the 4.5g3 parser reads nothing and **all three are ungated**: this
is a diagnostic, not part of the 9/29. Saying what a case *is* moved the label space back
towards the operator's verdicts, exactly as the hypothesis predicted. It moved it about a third
of the way.

**Where the remaining misses are is the finding.** Of the 20 stated rulings v2.2 still gets
wrong, **15 name `unclear`** (3 name `sarcasm`, 2 `intents`), and only 3 of the 20 are the
benign class the plan pre-registered — the ruling landed and an unnamed field moved. The other
17 miss the field the ruling names. `unclear` is also the second-largest source of preserved
losses (6 of 21, behind `intents` at 14).

Two readings of that, and they point in different directions:

1. **`UNCLEAR_RULE` speaks last.** In the assembled prompt the settled cases sit at offset
   2,410, the untouched v2 `unclear` rule at 3,642, and the answer format at 4,240 — so the
   final thing the model reads about `unclear` is v2's own list, which knows nothing of the
   sitting's rulings and closes on *"do not use it to avoid a decision you can make"*. This
   phase held that block fixed on purpose (it was in v2, which scored 86%), and the ADR
   pre-committed to naming position as the next variable if form failed. It is now named.
2. **For the P6 family, no wording can work.** The four unsigned corporate-voice rows are the
   sharpest case — and, like P5, mostly ungated: only `@VARUS_channel:1271` carries a parseable
   ruling and counts in the 29. v2.2 still answers `unclear: false` on three of them — even
   though the
   rule reaches the model **twice**: v2.2's second line says it, and `UNCLEAR_RULE` already
   listed *"a reply written by the retailer in its own corporate voice"* in v2. Their texts are
   `Акційні товари дійсно мають високий попит…`, `Тамагочі Варусятко живе у мобільному
   додатку VARUS.`, `Акція з ОТР банком була завершена 15.08.25р.` — statements no reader can
   attribute to a retailer from the text alone. And the discriminator already exists on disk:
   **all four carry the same `sender_anon_id`** (`2fa2b73f617b…`), the busiest sender in the
   channel at 876 comments against 81 for the next — the support account, stable under the
   raw-store HMAC and never deanonymised. `data/raw/comments/` has it; the labelling row does
   not. P6 is a **missing feature, not a missing sentence**, and a third prompt revision would
   spend money proving that again.

## Consequences

- **The cap does not move.** $1.50 total, `results/spend_45g4.json` anchored against the
  provider before the first request of this phase, and the 4.5g3 spend read from that phase's
  own ledger rather than typed — so the headroom this phase enforces is what 4.5g3 actually
  left.
- **Nothing under `data/annotation/wave2_45g3/` is touched**, whatever the probe says. On a PASS
  the phase pins v2.2's answers for those hundred ids in a separate result file, so a later
  sitting can be compared against labels that existed before any verdict did.
- **`prompts.SETTLED_CASES` stays in the file.** `results/rerun_45g3.json` pins the v2.1 hash
  and 1,912 rows on disk carry an `llm-precheck-v2.1` annotator; deleting the constant would
  leave a record naming a prompt nobody can rebuild.
- **A staged purchase is now the house rule for a prompt revision.** 4.5g3 bought a whole
  population to discover the instrument had changed; this phase buys a hundred rows to find out
  the same thing for four cents. `[[45g3-sitting-gates]]` recorded that lesson; this is the
  first phase to spend under it — $0.0365 against the $0.7429 that bought the same class of
  finding last time, a twentieth of the price.
- **The form-only hypothesis is closed, and it is closed as a partial success.** Affirmative
  phrasing is worth keeping — it doubled preservation and more than doubled the landed rulings
  — but it does not reach a bar the sitting's own verdicts set. `precheck_v2.2_with_post` is
  registered and is the best prompt on file; nothing on disk is labelled with it.
- **The next variable is position, and it is a smaller experiment than it looks.** Fold the
  settled `unclear` cases into `UNCLEAR_RULE` itself — or move that rule above the block — and
  re-run the same committed plan. The sample, the reference labels, the scorer and the
  thresholds already exist; the marginal cost is another $0.04. The 100 answers of this run are
  in `results/v22_probe_rows.jsonl`, so it is a paired comparison on arrival.
- **P6 is out of the prompt's reach and should stop being asked of it.** The retailer's own
  support account is already a stable pseudonym in `data/raw/comments/`; carrying
  `sender_anon_id` into the labelling row would settle the corporate-voice class by lookup
  rather than by inference. No code is written for that here — it changes what a labelled row
  is, which is a registry and pipeline decision, not a prompt one.
- **The shared cap has $0.7206 left.** 4.5g3 spent $0.7429 and this phase $0.0365 of $1.50
  (`results/spend_45g4.json`, anchored against the provider before the first request). A full
  1,912-row re-run under any revision still does not fit, and that has not changed.
