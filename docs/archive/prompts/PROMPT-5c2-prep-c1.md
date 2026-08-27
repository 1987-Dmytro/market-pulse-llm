# PROMPT-5c2-prep-c1 — the record track: the guard aims at the real root, and the positions leg learns to keep evidence

**Contract:** `docs/SPEC.md` amendment **3.18 (2)** and **3.18 (6)**, the B1 finding of the
prep-b acceptance (below), and this file. Read those two clauses only — not the whole spec.
**$0 session:** no pod, no endpoint, no template, no serverless job, no OpenRouter call, no
Telegram client. All artifacts in English. Team-lead files (`docs/STATUS.md`, `docs/SPEC.md`,
`docs/PRODUCT.md`, `docs/PROMPT-*.md`) are read-and-commit, **never edit**.

**Context in four lines:** prep-b gave the loop its comment leg and the evidence table
(`src/market_pulse/evidence.py`), accepted 13.08. The acceptance's one finding (B1): the smoke
guard asserts a phantom path. And of the three row kinds the table defines, only `comment` has a
producer — the paid session must NOT be the first to write a `leaflet_page` or `position_row`
(`results/predictions/LOST.md` is the precedent). Money work (census, projection,
pre-registration) is prep-c2, a separate contract by operator ruling 13.08.

## Step 0 — commit the tail

`git status --short` shows exactly four paths, verified by the team lead at issue time:
`docs/STATUS.md` (modified — the team lead's hand, prep-b acceptance + this split),
`knowledge/daily_logs/2026-08-13.md`, `knowledge/index.md` (modified, your own prep-b session
end) and `docs/PROMPT-5c2-prep-c1.md` (untracked, this file). Before committing the vault paths,
refresh `knowledge/hot.md`'s `## ⏭️ Next`: prep-b is DONE, next is c1 (this contract) then c2
(census → projection → STOP with numbers → pre-registration after the operator's ruling). Mind
the standing footgun: hot.md is grepped as a priced input (`scripts/volume_calc_5c1.py` needs
`~$0.24/day` and `80 GB is about what the` verbatim, both outside your section) — run
`make check` after editing it. Stage by path, never `git add -A`. Two commits:
`docs: 5c2-prep-c1 queued — STATUS after the prep-b acceptance` and
`docs(vault): the prep-b session tail and hot.md's Next`. Your own session output at the end is
pre-authorised into its own final commit — do not stop for it. STOP only for a path neither
list explains.

## Deliverable 1 — B1: the smoke guard aims at the real root

`tests/test_loop.py::test_a_smoke_leaves_the_real_cursor_and_the_derived_store_untouched`
currently ends with:

```python
assert not (tmp_path / "derived").exists(), "data/derived/ is the real pass's, not a smoke's"
```

`tmp_path / "derived"` is a path no code references — `wire_infer` deliberately does not patch
`DERIVED_ROOT`, so the constant still points at the repo's `data/derived/`, and a regression
that wired the smoke to it would write into the real repo while this line stayed green. Replace
the assertion's target with the real root:

```python
assert not runner.DERIVED_ROOT.exists(), "data/derived/ is the real pass's, not a smoke's"
```

Three consequences, each part of this deliverable:

1. **Sensitivity is proven, not assumed.** Add the other direction: a test that monkeypatches
   `runner.DERIVED_ROOT` to a `tmp_path` location, plants a row there via the smoke's own code
   path (or asserts the guard trips when the directory exists), and shows the guard REFUSES.
   Patching is legitimate in THAT test only — it verifies the guard's sensitivity, while the
   unpatched test verifies the real root. A guard is accepted only with evidence in both
   directions.
2. **The docstring stops lying by omission.** `run_loop.DERIVED_ROOT`'s docstring says the
   constant is "read by nothing"; after this change the guard test IS its first reader. Name it
   there. The "written by nothing yet" half stays true and stays.
3. **The loud day is designed, and said.** The day a legitimate writer creates `data/derived/`,
   the unpatched assertion goes red ON PURPOSE — the guard must then be redesigned WITH the
   writer (existence check → before/after snapshot), never deleted to make the suite green. Put
   that sentence in the test's docstring; it is written for whoever trips it.

Consumers of what this moves, enumerated at issue time: the assertion string has **1** home
(`tests/test_loop.py`); `DERIVED_ROOT` has **2** code homes (`scripts/run_loop.py`,
`tests/test_loop.py`) plus a prose home (`knowledge/hot.md` quotes the prep-b commit title —
no edit needed there, it is history).

## Deliverable 2 — the positions leg keeps evidence, at zero cost

The loop learns its second leg: a leaflet page in, one `leaflet_page` row plus one
`position_row` per parsed position out — through the SAME seam (`send(task, rendering) ->
reply dict`), with the same ordering, and only a stub transport, because `ENDPOINT` stays
`None`. Design constraints, each of which is a test:

- **The shapes are the law and are FROZEN.** `evidence.REQUIRED`, `evidence.KIND_FIELDS`
  (`leaflet_page` → `image_path`, `image_sha256`; `position_row` → `presence`, `tier`,
  `warnings`) and `src/market_pulse/positions.py` (sha-pinned inside
  `results/sku_pilot_prereg_b2.json`) are not edited in this contract. If the leg cannot be
  built without a shape change, STOP and report — a shape change is a 3.18 (6) question for the
  team lead, not a deviation.
- **Reuse the sealed instrument by import, never by copy.** Parsing goes through
  `positions.parse_positions`; the ladder through `positions.tier_from_presence`; the five
  booleans through `evidence.presence`. Read how `scripts/positions_gm4_skub.py` drives them
  before writing your own driver code — that file is the closed sku programme's instrument and
  its own record/dump shapes stay untouched (Dv256 stands).
- **`image_sha256` is the sha of the BYTES SENT.** Compute it from the exact file handed to the
  transport, at send time — not from a path re-read later. `image_path` is the path as the run
  saw it.
- **Per-row invariants, asserted through the PASS (not the builder):** every written row
  satisfies `evidence.assert_complete`; every `position_row` re-derives —
  `positions.tier_from_presence(**row["presence"]) == row["tier"]`; `warnings` is index-aligned
  per position (`len(warnings) == n_positions` on every answered page, `None` on a refusal);
  the stub smoke includes one page whose fake reply carries all three warning families at once
  (`multipack`, `discount_footnote`, `price_from` — the FakeEndpoint precedent in
  `tests/test_positions_driver.py`) and one refused page, so the shape is proven where it is
  full, where it is empty, and where it is absent.
- **Ordering and idempotence, same as the comment leg:** record durable on disk BEFORE the
  watermark moves; the queue subtracts the watermark AND the ids already in the store; a re-run
  over the same window writes zero new rows byte-identically; an interrupted pass leaves the
  watermark and the queue where they were. Reuse the comment leg's mechanisms — a second
  implementation of the cursor or the store is a defect, not initiative.
- **The smoke stays in its sandbox.** Stub rows land under `results/smoke/` only; the real
  cursor and `data/` are untouched (the D1 guard now watches the real root); a smoke never
  saves the cursor. Page fixtures: use the test suite's existing image-fixture pattern; if none
  fits, add a tiny fixture under `tests/` — never fetch anything.
- **The endpoint guard covers the new leg.** The leaflet path without `--smoke` is refused the
  same way the comment path is, message asserted, with the existing comment-leg guard tests
  untouched as the control.

## Verify gate — evidence, not assertions

1. `make check` green after **every** commit, and the per-commit checkout table with the
   control beside it (Dv193: in a worktree `data/` is a symlink, so
   `tests/test_collect_5c1.py::test_the_guard_reads_the_pinned_paths_off_the_pin_file` is red
   on every row including the control — re-measure the nodeid on the control, do not inherit
   this sentence).
2. D1 both directions: the retargeted assertion green in the real tree, and the sensitivity
   test's output showing the guard REFUSE a planted row.
3. The leaflet-leg stub smoke: paste the KEYS of one `leaflet_page` row and one `position_row`
   (the triple-warning one), plus the re-derivation line for that row.
4. The interrupted-pass and idempotence outputs for the leaflet leg — the watermark that did
   not move, the byte-identical second run.
5. `git log --oneline` for the session and a clean `git status --short` at the end apart from
   the pre-authorised vault tail.

## Do NOT

- Do NOT spend anything, register an endpoint/template/serving config, or open the spend
  guard's endpoint constant. The only RunPod contact allowed is the read-only guard, and this
  contract does not need it.
- Do NOT do the census, the price projection or the pre-registration — that is prep-c2, split
  by operator ruling 13.08. If a number for them falls into your lap, write it in the report
  and move on.
- Do NOT edit `src/market_pulse/positions.py`, `evidence.REQUIRED`/`KIND_FIELDS`, any sealed
  sku artifact, or any team-lead file. Do NOT write into `data/raw/` or `data/derived/`, and
  do not rotate `RAW_STORE_SALT`.
- Do NOT build a Telegram client or fetch media — fixtures only.

## Report

`docs/reports/5c2-prep-c1.md`, opening with three plain sentences: what is true now that was
not true this morning. Keep `implementation-notes.md` current with a **Deviations** section —
every departure logged there and cited in the report. Silence is not compliance.

**Read-back before you start:** name the two deliverables' gates in one line each, list what is
FROZEN in this contract, and state what a smoke must never touch.
