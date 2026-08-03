# PROMPT-4.5g4 — prompt v2.2 (affirmative settled-cases block) + pre-registered in-sample probe

You are the executor on market-pulse-llm. Full context is in this file; do not
re-read docs/SPEC.md. Read only: `results/sitting_45g_gates.json` (the `rows`
array: id/verdict/notes), `src/market_pulse/prompts.py` (SETTLED_CASES and the
v2.1 assembly), and the 4.5g3 code that produced `rulings_landed` in
`results/wave2_45g3_manifest.json` (the stated-ruling parser) and the
sealed-pack rebuild (STOP-RULE 1 machinery).

## Context (3 lines)

The 4.5g3 re-run under v2.1 regressed: 172 of the 258 sitting-approved rows
moved, only 10/29 stated rulings landed (see `batch_health` in the wave2
manifest). Diagnosis: the SETTLED_CASES block states rules as negations and
never names the output field ("is not a consumer reaction", "never price" —
price 110→313, no_intent 809→1366). This phase registers v2.2 (same eight
rulings, affirmative, field+value named), buys one pre-registered 100-row
in-sample probe, and stops. The full 1,912-row re-run is NOT in this phase.

## Budget

Cap $1.50 unchanged; 4.5g3 spent $0.7429, headroom $0.7571. This phase:
~100 probe requests ≈ $0.04, plus ~100 more (Task 4, only on PASS) ≈ $0.04.
Ledger: `results/spend_45g4.json`, NEW anchor read from the provider BEFORE
the first request of this phase (same footgun note as spend_45g3.json).

## Task 0 — sweep the dirty tree

`knowledge/daily_logs/2026-08-03.md`, `knowledge/index.md`,
`results/sitting_45g_gates.json` were rewritten AFTER the last commit by the
Stop hook and the returns reader (git-block refresh; diff is benign). Commit
them as a chore. If anything ELSE is dirty, stop and report.

## Task 1 — register v2.2

In `src/market_pulse/prompts.py` add `SETTLED_CASES_V2_2` whose rendered text
is EXACTLY the following — transcribe verbatim, do not improve, reword, or
reorder (wrap lines with the file's trailing-backslash convention as needed):

```
Cases the annotation guideline has since settled, and they outrank the general wording above:
- A joke, a piece of trivia or banter on a topic other than the product or the retailer: set unclear true.
- Unsigned support wording about demand, stock or how a promo runs is the retailer speaking in its own voice: set unclear true, the same as for any reply the retailer signs.
- Praise of how the retailer behaves takes intents ["service"], exactly as a complaint about the same conduct does.
- A question about how a promo works, what its terms are or who it applies to takes intents ["service"].
- A comment aimed at another commenter: set unclear true. When it accuses the retailer directly, the accusation outranks the addressee: set unclear false and judge it normally.
- An answer naming a dish, a filling or a food someone likes — as a joke or a childhood memory included — takes intents ["taste"].
- A quotation used to mock what it quotes — the retailer's own words, an app message or a promo line — sets sarcasm true, and so does a joke that elevates something ordinary into something grander.
- Bare thanks and a single unambiguous emoji are readable reactions: set unclear false, read the sentiment, and give intents [].
```

Assembly mirrors v2.1 exactly: `T1_PROMPT_V2_2` = `_swap(T1_PROMPT_V2, ...)`
inserting `SETTLED_CASES_V2_2` before the answer-format line (same position
as v2.1 — position is deliberately NOT a variable this phase);
`T1_PROMPT_V2_2_WITH_POST` as a build step (unregistered, per the v2.1
rationale); `PRECHECK_PROMPT_V2_2_WITH_POST` via the same three swaps as
v2.1. Register `"T1v2.2"` and `"precheck_v2.2_with_post"` in `PROMPTS`,
`PROMPT_KIND`, `PROMPT_INTENTS` (INTENTS_V2), `PROMPT_FIELDS` (three fields
for T1, four for precheck). Old names and SHAs untouched.

Docstrings: v2.2 is v2.1's eight rulings restated affirmatively, each naming
its output field and value; semantics 1:1; the bare-thanks line still
restates a v2 clause (keep that flag). UNCLEAR_RULE is untouched — it was in
v2, which scored 86%; the regression delta is SETTLED_CASES only.

Changelog: section `v2.2 changelog` in `docs/annotation/comments.md` with a
per-line old→new mapping, marked FORM-ONLY — the guideline law is unchanged.

Guards (tests):
1. Transcription guard: a unit test holding the canonical block text from
   this prompt and asserting `" ".join(SETTLED_CASES_V2_2.split()) ==
   " ".join(canonical.split())` (whitespace-insensitive, content-exact).
2. Negation guard: assert no instructional negation tokens in the block —
   regex `r"\b(not|never|no|none|neither|nor)\b|n't"` finds nothing in
   `SETTLED_CASES_V2_2` (scoped to this constant only; `false` as a field
   value is fine and expected).
3. From 4.5g3 deviation 9: if the two guard fixes (cost estimate computed on
   pending rows, not the whole volume; `check_labels` running on rewritten
   rows) lack regression tests, add them; if they exist, name them in the
   report.

## Task 2 — pre-register the probe gate (BEFORE any API request)

Write and COMMIT `results/v22_probe_plan.json`, then and only then run:

- `sample`: all 42 ids with `verdict: "incorrect"` from
  `results/sitting_45g_gates.json`, plus 58 ids drawn from the 258 `correct`
  with `random.Random(42)` over the lexicographically sorted id list. List
  all 100 ids in the file, with each id's stratum.
- Reference labels: the sealed sitting pack's four judged fields (rebuild the
  pack exactly as STOP-RULE 1 did if the gitignored CSV is absent; the
  rebuild must reproduce `sealed_sha256` c0d7656f… before labels are read).
- `preserved` (58 correct rows): v2.2 output equals the pack labels on ALL
  four fields.
- `fixed` (the 29 rows with a parseable stated ruling — reuse the 4.5g3
  parser): every field the ruling names matches the ruling AND every field
  it does not name equals the pack label. The other 13 incorrect rows are
  reported moved/unmoved only, ungated.
- Gate, one attempt, no retry: **PASS = preserved ≥ 55/58 AND fixed ≥
  24/29. KILL = preserved < 52/58 OR fixed < 20/29.** Between: the operator
  decides on the numbers. A failed gate closes the form-only hypothesis.
- `in_sample: true` with the caveat: the v2.1/v2.2 rules were distilled from
  these same verdicts, so absolute numbers are optimistic; this probe
  authorizes only the next purchase, never batch acceptance. Reference
  v2.1: preservation ~33% in-sample, fixed 10/29.

## Task 3 — run the probe

`precheck_v2.2_with_post` on the 100 sample ids only — same model
(`qwen/qwen3.6-27b`), same pinned endpoint and parameters, same posts and
surrogates as the 4.5g3 re-run (its provenance is the reference). Score per
the committed plan into `results/v22_probe_results.json`; print the gate
table (preserved n/58, fixed n/29, verdict, plus per-field move counts on
the 100 and the P5/P6 family rows by id with before→after). Every reported
number comes from the scoring script, none typed by hand. Ledger updated.

## Task 4 — ONLY on PASS: pin v2.2 answers for the wave2 hundred

Run `precheck_v2.2_with_post` on the 100 ids of
`data/annotation/wave2_45g3/wave2_100.csv` (~$0.04). Write labels + their
sha256 to `results/wave2_45g3_v22_labels.json` and COMMIT — the point is
v2.2's answers pinned before any wave2 verdict exists. DO NOT modify
anything under `data/annotation/wave2_45g3/`; re-verify both manifest
hashes afterwards and show the check.

## Hard stops

- No API request before the plan commit of Task 2.
- One probe attempt; no re-prompting, no second sample, no threshold edits.
- FAIL or KILL → skip Task 4, report.
- No requests beyond the ≤200 named here. No full re-run.
- Do not edit docs/STATUS.md, docs/SPEC.md or docs/PROMPT-*.md — team-lead
  files (File ownership).
- State your assumptions; if the rulings parser or the pack rebuild is not
  in the shape this prompt assumes, stop and report instead of inventing a
  workaround.

## RECORD

ADR `knowledge/decisions/45g4-v22-affirmative-rewrite.md` (+ INDEX):
decision = form-only affirmative rewrite; alternatives rejected (position
change — second variable; immediate full re-run — $0.85 over $0.757
headroom; judging the wave2 v2.1 hundred as-is — its own README warns
against it); thresholds as pre-registered; staged design chosen by the
operator 03.08.

## Commits (atomic, repo green after each)

1. chore: tree sweep (Task 0)
2. feat: v2.2 registered + transcription/negation/guard tests + changelog + ADR
3. feat: probe gate pre-registered
4. feat: probe run + scoring + ledger
5. (PASS only) feat: v2.2 labels for the wave2 hundred, pinned pre-sitting

## Before executing

Read back in one line each: the gate (thresholds and one-attempt rule), the
hard stops, and the file-ownership line. Then execute.

## Report

Gate table with verdict; preserved and fixed counts vs thresholds; the 13
unparsed rows moved/unmoved; per-field move counts; P5/P6 rows by id;
spend and anchor; test count; Deviations section in
`implementation-notes.md` cited in full — silence is not compliance.
