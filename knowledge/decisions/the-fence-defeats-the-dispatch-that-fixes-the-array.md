---
type: decision
date: 2026-09-04
status: open — the team lead's ruling is the open stop of session 15
tags: [decision, promo-pulse-1, s9, transport, money]
---

# The fence defeats the dispatch that fixes the array

**Finding of session 15 (paid iteration 2, $0.223850).** Subject agreement read **0.7500** against
the 0.80 bar, down from the **0.8214** iteration 1 reads under the same v1.1 gold — and the whole
gap is one thread, `@VARUS_channel:6216`, which went 18 gold comments answered to **0**.

## The mechanism, in the order it fires

1. gemma-4 fences every leg-A answer: `promo_dev40_errors_iter2.json :: answers.fenced_answers` is
   **40 of 40**. The codebook asks for JSON and never forbids a fence.
2. On this one thread the model answered with an ARRAY of per-comment objects instead of the
   registered single object — `[{"about": {…}, "signals": [], "unsure": []}` …
3. `scripts/promo_dev_pod_runner.py :: balanced_prefix` dispatches the array rule on
   `text.lstrip().startswith("[")`. With the fence the lead is `` ```json ``, so it is False.
4. The SHIPPED rule — «close the first top-level OBJECT» — therefore ran, and it is wired into the
   GENERATION stop as well as the persisted prefix (`close_arrays_too`). Generation ended at the
   first element: **213 chars, 5.9 s, `finish_reason: stop`, `balanced: true`.**
5. The remaining 17 answers were never generated, so no parse-time repair could recover them. The
   answer that survived failed `json.loads` at «Expecting ',' delimiter».

The rule's own docstring asserts leg A «can never begin with `[`». That premise is about the raw
text, and the raw text always begins with a fence — so the guard was written against a shape the
instrument never emits.

## What it did NOT do — checked, because a cut that parses reads as a model saying less

Exactly **1 of 40** leg-A answers is array-shaped. The only other row-count moves between the
iterations are `@msuaaaa:9014` (11 → 1) and `@VARUS_channel:9999` (6 → 5), and both are complete,
well-closed objects whose threads carry 1 and 5 gold comments — they cost **0** gold rows. On the
122 comments outside 6216 iteration 2 misses **17** where iteration 1 missed **25**.

## The fork that is not the executor's to settle

Repairing the dispatch is either a DEFECT FIX — same `extractor_version`, iteration 2 re-bought —
or a NEW INSTRUMENT under ruling 03.09 (c) item 3, which makes it iteration 3 of at most five. It
decides whether the $0.2239 bought a reading of the LAW or a reading of the TRANSPORT.

Related: [[the_wrapper_is_not_the_answer]] · [[empty_class_eats_the_parse_failures]] ·
[[a_number_typed_into_its_own_checker]] · [[count_the_kind_not_the_rows]]
