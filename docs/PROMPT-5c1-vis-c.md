# PROMPT-5c1-vis-c — 232 posts captioned + yield screen v2 (cap $1.50)

> Authority: operator go 2026-08-09; SPEC §3.13 (4) gates + §3.15 runtime.
> Endpoint procedure: `scripts/runbook_vis_b.md` §A–§B apply verbatim
> (template → endpoint → one-post smoke with a NEW `--record` path); the
> §C of vis-b is replaced by the slice plan below. One replacement
> endpoint after a proven deletion is authorised (3.15 recovery pattern);
> never two BILLING endpoints concurrently.

## Read first

- `docs/SPEC.md` §3.13 (4) + §3.15; `docs/PROMPT-5c1-vis-b.md` RESUME
  addendum points 4–6 (boot proof, positive-controlled listings, the
  §C.1 constant discipline).
- `knowledge/hot.md` footguns: `--only` on every collection run; two
  Telethon clients never share `marketpulse.session`; `smoke_5b.py
  --record` defaults to the pod cost anchor.

**Read-back check — FIRST lines of the report:** the step-0 items, the
slice-plan gates, and ALL stop rules, one line each.

## Step 0 (before anything billable)

1. Fetch attempt-2's SUCCESSFUL boot log from the volume into `results/`
   (debt Dv67 — the next boot overwrites it); commit.
2. ADR closing vis-b → `knowledge/decisions/` + INDEX entry, numbers from
   artifacts only: instrument VALID (19/19; bar A 14 against bar 4; qwen
   13; the pre-registered instrument-failure rule did not fire), bridge
   8/18 on proven-identical inputs = caption sampling — a 5c2 design
   input, not a captioner defect; costs from
   `results/spend_5c1_vis.json` including the $0.1693 correction. Commit.
3. Team-lead docs commit, content unedited: `docs/STATUS.md`,
   `docs/PROMPT-5c1-vis-c.md`.
4. Run `scripts/preflight_serving_guards.py`, paste its output — the
   standing zero-cost rule; it caught the last bug class.

## The work

1. **Manifest ($0, Telegram).** `results/image_census_5c1.json` minus the
   19 captioned ATB posts: fetch media via the `fetch_post_media.py`
   pattern, `--only` discipline, ONE client on the session file. Every
   post lands in exactly one bucket: `fetchable` / `blind` (media gone,
   expired, unsupported) — blind is COUNTED and reported, never dropped
   silently. Record the manifest with counts and sha256s.
2. **Captions (paid).** `scripts/caption_gm4_5c1.py` against the
   endpoint, slices under the 8 MB job budget,
   `caption_source: "gm4-nf4-base"`, ceiling stays
   `CAPTION_MAX_NEW_TOKENS = 400` — truncations counted and reported per
   channel; the ceiling is revisited only as a NAMED revision after
   screen v2, never mid-run. **Re-projection stop:** after the first
   slice, project the full run from measured spend; STOP if the
   projection exceeds the cap remainder, and report the measured rate —
   5c2 needs it either way.
3. **Screen v2 ($0 compute).** The yield screen re-run with captions
   joined, same UNTOUCHED prereg
   (`results/yield_bars_5c1.preregistration.json` — re-hash before use),
   same controls. Verdicts name: graded N / blind M / truncated T. The
   output is the operator's signature package — **this contract SIGNS
   NOTHING**: the launch composition is the operator's word alone.

## Money

Cap **$1.50** (SPEC 3.13 (4)); the ledger continues in
`results/spend_5c1_vis.json` with a vis-c block and its own start
balance; both floors at every rung (Dv33 — the balance delta lags and
the itemised ledger settles late; report the max, name both).
Conservative projection $1.20–1.27 at the vis-b measured rate; ATB was
the heaviest image segment, so expect less.

## Cleanup — regardless of outcome

Template and endpoint deleted; deletion proven by POSITIVE-CONTROLLED
listings (first show the listing displaying a known-live object of that
kind, or use the API that names it — the vis-b template-list finding).
All dumps fetched and content-verified BEFORE deletion. The volume
`qw4nwleanc` stays.

## Do NOT

- Do not edit `docs/STATUS.md`, `docs/SPEC.md`, `docs/PROMPT-*.md` —
  team-lead files (File ownership); commit-only.
- Never two billing endpoints concurrently; one replacement after a
  proven deletion is authorised; no retry of a failed rung.
- `data/frozen/**`, `results/baselines.json`, `results/verdict_*.json`,
  `results/parity_*.json`, `results/serving_5b.json`, the adapter, the
  19 committed ATB captions and their records — untouched.
- No `--record` defaults; never `git add -A`; the vault tail of this
  session goes to its own final commit.

## Report — evidence, not assertions

The boot log names the running commit BEFORE the first job; per-gate
command + output; manifest counts (fetchable / blind); truncation count
per channel; the screen v2 verdict with the prereg sha echoed; both
spend floors and the closing balance; `implementation-notes.md`
Deviations continue from Dv68 — silence is not compliance. Report in
English.
