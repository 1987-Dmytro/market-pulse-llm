---
type: decision
date: 2026-09-03
status: open
tags: [decision, promo-pulse-1, s9, instrument]
---

# The ```json fence is read off, and nothing inside it is repaired — iteration 1's one deviation

**Executor's decision, taken during the paid run and awaiting the team lead's ruling.** Ruling
03.09 (c) item 3 makes iteration 1 the BASELINE: «this CODEBOOK and today's TEMPLATE, untouched»,
and reserves the template, the rendering, the decoding and **the answer repair** for iterations 2–5,
each a new `extractor_version`. This decision claims that reading a markdown fence off is on the
parser's side of that line, not the instrument's. Related: [[the_wrapper_is_not_the_answer]].

## What the model did

All 40 leg-A replies of iteration 1 came back as ` ```json ` + newline + a complete, well-formed
object. The balanced-prefix stop ended generation at the object's own last brace, so the closing
fence is the four characters recorded as `cut_chars: 4` on the rows that have it.

`promo_prompts.parse` called `json.loads` on the raw reply and failed every one at «Expecting value:
line 1 column 1 (char 0)». Scored as they stood, iteration 1 reports **subject 0.0 / signal 0.15**:
40 parse failures, 140 gold comments unmatched, and the phase's question answered by a code fence.

## Why this is parsing and not repair

1. **The law never forbade a fence.** `promo_prompts.CODEBOOK` and its TEMPLATE ask «Поверни JSON:
   {…}» and say nothing about fences. `prompts.positions_messages_text_gm4` — leg B's REGISTERED
   prompt — is the one that says «no code fence … the first thing you write is "["». That is exactly
   why leg A's 40 replies are fenced and leg B's 16 are not: the model obeyed both prompts.
2. **Nothing inside the object is touched.** `unfence` drops the opening fence line and a trailing
   fence if present. A malformed object, an object cut by the output ceiling, or junk inside a fence
   still returns a parse failure counted by cause — driven, all three, as negative controls.
3. **No registered version moves.** `codebook_version()` hashes the CODEBOOK and `extractor_version`
   hashes the RENDERED PROMPT. Neither reads `parse`, so the pack's pins and the registration's law
   are untouched. Nothing sealed moves.

## What it changed

`src/market_pulse/promo_prompts.py::unfence` (`36ef74f`), and the error table now carries
`fenced_answers` as a reading — 40 of 40 for iteration 1. With it: 151 gold-shaped rows, 0 parse
failures, **subject 0.7929 · signal 0.8792**.

## The open question for the team lead

The raw replies are committed (`results/promo_dev40_iter1.jsonl`), so iteration 1 is re-scorable
either way at $0. If the fence is ruled to be the model's failure rather than the parser's gap, the
grade is subject 0.0 / signal 0.15 and iteration 2's first knob is «forbid the fence in the
template» — which is a TEMPLATE change and therefore a new `extractor_version`, which is allowed.
