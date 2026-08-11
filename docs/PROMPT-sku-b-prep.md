# PROMPT-sku-b-prep — the positions serving path, everything before the paid pilot ($0)

> Authority: SPEC §3.17 (6)–(9); joint review 2026-08-11 (operator ratified: the
> prep/run split, the serving pin base-off · greedy · batch 1 · pinned revision ·
> max_new_tokens 800, smoke-before-legs). This contract is $0 and local: no pods,
> no endpoints, no templates, no /run calls of any kind. The paid attempt is
> sku-b-run and it is NOT this contract.

## Read first (sections, not documents)

- `docs/SPEC.md` §3.17 (6)–(9) — (9) is new today and is the law this
  contract implements. Transcribe it, do not redesign it.
- `results/sku_pilot_prereg_v2.json` — `bars.price_pair_accuracy.procedure`
  (the dump's field list, verbatim) and `instruments` (both prompt shas).
- `scripts/serve_handler.py` module docstring, `settings()` and the op
  router — the pattern POSITIONS must mirror, refusals included.
- `scripts/caption_gm4_5c1.py` module docstring — the driver pattern:
  `MAX_PAYLOAD_MB`, the identity stop, the three-key spend anchor.
- The registration discipline in `.claude/rules/phase345-artifacts.md`.

**On checkout, ONE test is red BY DESIGN:** `tests/test_sku_prereg.py`'s
marker enumeration knows two names and `docs/SPEC.md` now carries three.
Step 0.2 extends the list with `sku-b-ratification-3` and the suite is
green from there. Do not "fix" this any other way; the prereg pin itself
does not move (the strip removes every marked block).

**Read-back check — FIRST lines of the report:** the six deliverables one
line each, then the serving pin in one line (config name, base-off,
greedy, batch 1, revision, max_new_tokens), then the invariant
"no paid calls in this contract".

## Step 0 (commits pre-authorised)

1. Team-lead docs commit, unedited: `docs/SPEC.md` (the -3 block),
   `docs/PROMPT-sku-b-prep.md`.
2. `tests/test_sku_prereg.py`: the marker enumeration gains
   `sku-b-ratification-3`; `make check` green from this commit on.
3. Vault tail (fixed paths as usual) → its own final commit.

## Deliverables (six; STOP and report if one runs deeper than briefed)

1. **Serving path.** `POSITIONS` config beside `CAPTION` (constant in
   `src/market_pulse/serving.py`, wiring in `scripts/serve_handler.py`):
   `settings()` accepts it with CAPTION's refusals mirrored — any variable
   of the adapter set present refuses BEFORE the model loads,
   `MODEL_REVISION` required; a `positions` op routed like `caption`, with
   the both-ways config↔op refusal (a positions job on any other config
   refuses, and any other job on POSITIONS refuses); `describe()` reports
   the REAL max_new_tokens per config — the known 256-vs-400 lie dies in
   code here (the volume re-stage that deploys it is sku-b-run's, not
   yours); a client render for exactly the two registered tasks — page leg
   one image (`prompts.positions_messages_page_gm4`), text leg no image
   (`prompts.positions_messages_text_gm4`) — refusing any other task, the
   same shape as `CaptionClient`'s refusal. Generation per (9): greedy,
   batch 1, max_new_tokens 800. Values are transcription of (9), not
   design space.

2. **Driver** `scripts/positions_gm4_skub.py` (PAID when live; this
   contract builds it and proves it on `--smoke`/`--dry-run` only): page
   leg reads EXACTLY the 108 sent pages named by
   `results/sku_reference_leaflet.json` (never the 159 available), text
   leg the 30 rows via `results/sku_text_pack_manifest.json`; jobs packed
   under a NUMERIC `MAX_PAYLOAD_MB = 8.0` that REFUSES an oversized job —
   a shortened album is a different instrument, images are never dropped;
   strict parse via `market_pulse.positions.parse` with the dairy family's
   wire keys (the wire says `fat`; read it through `wire_key`, never
   `row["attribute"]` off the wire); a parse failure is counted by reason
   and is NEVER an empty answer; the per-position dump carries the
   verbatim field list of prereg v2 `bars.price_pair_accuracy.procedure`;
   identity stop before the first paid call unless the worker's
   `describe()` matches `results/sku_pilot_serving.json` (D4); spend
   record via the three-key anchor pattern of `scripts/caption_atb_5c1.py`
   (never `relabel.read_ledger`); provenance via the collapsed
   `git_state` (D3). `--smoke` and `--dry-run` prove the whole path with
   zero network and print per-row lines (`test -s` guardable), not only
   aggregates.

3. **`git_state` collapse (fix-on-touch, operator 11.08).** One function
   in `src/market_pulse/`, an equality test pinning its output shape to
   the five current copies' behaviour on a clean tree, the five callers
   migrated (`run_baseline`, `eval_zero_shot`, `freeze_testsets_v3`,
   `build_audit_pack`, `train_xlmr_baseline`), the driver is caller six.
   No behaviour change — records keep their exact shape.

4. **Serving pin artifact** `results/sku_pilot_serving.json`: config name,
   adapter none, greedy, batch 1, MODEL_REVISION `842da379…` (full sha),
   max_new_tokens 800, both prompt shas copied from prereg v2
   `instruments`. A test asserts artifact ↔ code equality (the values the
   code serves are the values the file pins), so the pin cannot drift.
   Committed BEFORE any sku-b-run artifact exists.

5. **Preflight extension.** `scripts/preflight_serving_guards.py` drives
   the POSITIONS guards BOTH WAYS against real transformers+peft on the
   tiny-config model: config↔op refusal in both directions, the adapter-
   set refusal, revision-required refusal, the driver's payload guard at
   the numeric boundary (just under passes, just over refuses), parser
   refusal on a truncated-JSON tail; keeps its existing positive control;
   still exits 1 when the libraries are missing. Evidence = its full
   output in the report.

6. **Cost projection** `results/sku_projection.json`: from the freshest
   record that actually PAID for ATB-leaflet captions (name it; quote its
   per-image marginal; never multiply an all-in per-post figure by a
   count), an explicit stated decode-length uplift assumption for
   positions JSON vs captions, cold start carried as the range $0.0563
   measured / $0.0733 preregistered, the text leg priced, total vs the
   $0.35 cap with headroom stated. A projection is arithmetic over named
   artifacts — no new measurement, no paid call.

Tests + `make check` green; Deviations continue Dv133+.

## Do NOT

- No paid calls, no RunPod resources of any kind — no pod, endpoint,
  template or /run request (GOAL: prep is the zero-cost rung of the
  ladder; the single paid session of SPEC 3.17 (6) is sku-b-run's).
- Do not edit `docs/STATUS.md`, `docs/SPEC.md`, `docs/PRODUCT.md`,
  `docs/PROMPT-*.md` — team-lead files; commit-only (File ownership).
- Do not edit registered prompt texts; do not re-pin
  `results/sku_pilot_prereg.json` or `_v2.json` (GOAL: the prereg chain is
  the pilot's witness; a v3 happens only on team-lead instruction).
- Do not touch the frozen family (T1v2), frozen sets,
  `results/baselines.json`, verdict/parity records, the adapter,
  `results/spend_phase4.json`.
- Do not invent serving values — (9) is transcription, not design space.
- Never `git add -A`; vault tail → its own final commit.

## Report — evidence, not assertions

The report is a FILE — `docs/reports/sku-b-prep.md`, own commit
`docs(report): sku-b-prep` — and chat gets ONLY the path. Read-back lines
first. Per deliverable: the commands run and their output tails
(registration greps, the git_state equality test, the preflight's full
output, `make check` tail). The projection's arithmetic with every input
named by artifact path. A Deviations section (Dv133+), explicitly "none"
if none. English. State your assumptions.
