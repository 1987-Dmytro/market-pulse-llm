# PROMPT-5c2-prep-b — the inference leg becomes real, and the run starts keeping its evidence

**Contract:** `docs/SPEC.md` amendment **3.18 (5)** and **3.18 (6)**, and this file.
Read those two clauses only — not the whole spec. This file is the whole brief.
**$0 session:** no pod, no endpoint, no template, no serverless job, no OpenRouter
call. All artifacts in English. Team-lead files (`docs/STATUS.md`, `docs/SPEC.md`,
`docs/PRODUCT.md`, `docs/PROMPT-*.md`) are read-and-commit, **never edit**.

**Context in four lines:** 5a built the loop skeleton and stopped on purpose — the
pass is computed from the cursor and the store, the live path refuses, and the
`inference` watermark is advanced by nobody because no serving endpoint existed
(`src/market_pulse/loop.py`, `scripts/run_loop.py`, `data/loop_cursor.json`, whose
entries carry `posts` and nothing else). prep-a raised the cap and repaired the
ledger. This contract gives the loop its inference leg and the record shape SPEC
3.18 (6) makes mandatory — **still without spending a cent.**

## Step 0 — commit the tail

`git status --short` should show exactly five paths, verified by the team lead at
10:5x: `docs/STATUS.md` (modified — today's map, the team lead's hand),
`knowledge/daily_logs/2026-08-13.md`, `knowledge/hot.md`, `knowledge/index.md`
(modified, your own prep-a session end) and `docs/PROMPT-5c2-prep-b.md`
(untracked, this file). Stage **by path** — never `git add -A`. Two commits:
`docs: 5c2-prep-b queued — STATUS after the prep-a acceptance` and
`docs(vault): the prep-a session tail`. Your own session output at the end (hot.md
refresh, the daily log, `/save`) is pre-authorised into its own commit — do not
stop for it. STOP only for a path neither list explains.

## Step 0.5 — close prep-a's RECORD (three mechanical items, one commit)

These are debts from the accepted contract, not new scope. They ship first
because a rule that lives only in a report decays.

- **The ADR that prep-a earned:** `knowledge/decisions/` + `INDEX.md`. The rule to
  record, with prep-a's own evidence: `docs/SPEC.md` is pinned WHOLE (stripped of
  marked blocks) inside sealed pre-registrations, so **the law may only grow
  inside a marked block whose name the strip knows**; re-pinning a sealed record
  is forbidden; the file's `rev. 3.14` heading is frozen because those bytes are
  pinned, and the live revision lives in the `amendment-index` block instead.
  Name what a future amendment must do — wear `<!-- amendment-3.N begin/end -->`
  and be added to the enumeration in `tests/test_sku_prereg.py` — and that a name
  the expression does not know reddens the pin rather than passing quietly.
  This ADR is written for the TEAM LEAD, who is the one who will next add an
  amendment.
- **`knowledge/hot.md`'s `## ⏭️ Next` section is stale:** it still opens with the
  5c2 briefing that has happened. The curated block at the top is already correct;
  bring the section under it in line — prep-b and prep-c are what is next. Mind
  the footgun: hot.md is grepped as a priced INPUT (`volume_calc_5c1.py` needs
  `~$0.24/day` and `80 GB is about what the` verbatim), so run `make check` after
  editing it, not only after editing code.
- **`docs/ARCHITECTURE.md:324` still sells the old cap:** the `runpod_guard.py`
  row reads «The $25 Phase-4 GPU cap». Fix it to $30 with the authority (SPEC 3.18
  (3), operator ruling 2026-08-13), and grep the file for every other stale cap
  figure while you are in it — fix-on-touch, and name in the report what you
  found and changed.

## Deliverable 1 — the inference leg, end to end, at zero cost

The pass gets its second half. Design constraints, each of which is a test:

- **The queue is the `inference` watermark's, per channel.** It is stored the way
  `posts` is (`data/loop_cursor.json`, `market_pulse.backfill`'s atomic
  whole-file writer). Nothing about the `posts` watermark or the raw v1 stores
  changes — derived data lands BESIDE them, as `reply_to` did.
- **The watermark advances only after the record is durably on disk.** Write the
  record, flush it, then move the watermark — never the other way round. Prove it
  with a test that interrupts the pass between «the model answered» and «the
  record was written» and asserts the watermark did not move and the row is still
  queued.
- **A re-run buys nothing twice.** Running the same pass again over the same
  window produces zero new records and does not move the watermark. Idempotence
  is asserted on the artifact, not argued in prose.
- **No endpoint exists yet, and the smoke must not pretend otherwise.** The pass
  runs `--dry-run` (plan only, the 5a meaning kept) and a stub-served smoke
  through the SAME seam production will use — the stub replaces the transport,
  never the record-building code. Smoke records stay under `results/smoke/`
  (gitignored); quote their numbers in the report.
- **The spend guard's endpoint constant stays CLOSED.** 5a left it closed until an
  endpoint is registered; opening it belongs to the paid session's contract, not
  to this one. A test that asserts it is still closed is cheap and belongs here.
- **What is free to check against reality, is checked against reality.** Anything
  verifiable with a real local import at $0 — `scripts/serve_handler.py`'s refusal
  when an adapter variable sits beside `SERVING_CONFIG`, the millisecond/second
  conversion in `market_pulse.serving.execution_policy`, `prompts.prompt_sha256`
  for the registered names — is exercised against the REAL module, not a stub. A
  stub shares the premises of the code it tests; that is what cost a paid boot in
  August (`active_adapters` was truthy on every model).

## Deliverable 2 — the record shape that makes 5c2-validate buildable

SPEC 3.18 (6) makes an operator sitting a condition of closing the phase: five
leaflet posts and five comments, original beside verdict, drawn under a recorded
seed. **The pack cannot be built afterwards from records that never kept the
evidence** — `results/predictions/LOST.md` is the precedent, a per-row dump lost
forever. So the shape lands now, and a guard keeps it.

Every row the loop writes carries, at minimum: the registered prompt name and its
sha (`prompts.prompt_sha256`), the model revision, the EXACT rendering handed to
the model, the raw reply as returned, the parent post id, and — for a leaflet page
— the image path and its sha256. For a position row, the presence fields that
`positions.tier_from_presence` read, so the tier can be RE-DERIVED at the sitting
rather than trusted.

Two standing debts belong to this same deliverable, because both are the record
lying or staying silent:

- **Dv232 — the parser warnings never reached the run record.**
  `positions.warnings()` (the footnote / multipack / «від X грн» families) is
  computed and dropped. The standing rule in hot.md is that no future positions
  run happens before it lands. It lands here.
- **Dv176 — the driver writes a `contract:` provenance string that is false.**
  `scripts/positions_gm4_skub.py` puts `docs/PROMPT-sku-b-v3-prep.md … 3.17 (9),
  (10), (11)` into every run record, omitting (12), and nothing reads the field.
  Close it the way its twin Dv170 was closed in `scripts/sku_bar_verdicts.py`: a
  constant with a test pinning it to the contract actually in force. This
  contract touches the driver, which is the condition the debt was parked under.

Finally, the guard that keeps the two halves from drifting: **one place** names
the fields the validation pack requires, and a test asserts the record shape
carries every one of them. Delete a field and the test — not the sitting with the
operator — is what tells you.

## Verify gate — evidence, not assertions

1. `make check` green after **every** commit, and the per-commit checkout table as
   usual (Dv193: in a worktree `data/` is a symlink, so
   `test_collect_5c1.py::test_the_guard_reads_the_pinned_paths_off_the_pin_file`
   is red on every row including the control-parent — read the table only with the
   control beside it).
2. The dry pass, printed: what a pass would do, from the cursor and the store.
3. The stub smoke: paste the KEYS of one written record, so the evidence fields
   can be read rather than believed.
4. The interrupted-pass test's output — the watermark that did not move.
5. `git log --oneline` for the session and a clean `git status --short` at the end
   apart from the pre-authorised vault tail.

## Do NOT

- Do NOT spend anything. No `pod create`, no `serverless`, no template, no
  OpenRouter call. The only RunPod contact allowed is the read-only guard.
- Do NOT do the census, the price projection or the paid session's
  pre-registration — those are prep-c, deliberately a separate contract. If a
  number for them falls into your lap, write it in the report and move on.
- Do NOT open the spend guard's endpoint constant, and do NOT register an
  endpoint, a template or a serving configuration.
- Do NOT write into `data/raw/` v1 stores, and do not rotate `RAW_STORE_SALT`.
- Do NOT edit team-lead files or re-pin any sealed artifact of the sku programme.
- Do NOT collect: no Telegram client, no joins — two Telethon clients must never
  share `marketpulse.session`.

## Report

`docs/reports/5c2-prep-b.md`, opening with three plain sentences: what is true now
that was not true this morning. Keep `implementation-notes.md` current with a
**Deviations** section — every departure logged there and cited in the report.
Silence is not compliance.

**Read-back before you start:** name this contract's three verify-gate items in one
line each, say which deliverable the Dv232 debt sits in, and state what this
contract must NOT touch that a reasonable person might assume it should.
