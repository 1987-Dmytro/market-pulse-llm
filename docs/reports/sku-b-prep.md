# sku-b-prep — the positions serving path, everything before the paid pilot ($0)

## Read-back

1. **Serving path.** `serving.POSITIONS_CONFIG` beside CAPTION; `settings()` mirrors CAPTION's two
   refusals through a shared `BASE_ONLY` table; a `positions` op routed by the closed
   `serving.CONFIG_OPS` table, refusing every cell it does not name in both directions;
   `describe()` reports the REAL `max_new_tokens` per config; `local_llm.PositionsClient` renders
   exactly the two registered tasks — page = one image, text = no image — and refuses any other.
2. **Driver** `scripts/positions_gm4_skub.py`: 108 SENT pages and the 30 adjudicated rows, packed
   under a numeric `MAX_PAYLOAD_MB = 8.0` that refuses rather than shortens, parsed strictly through
   the dairy family's wire keys, one attempt, the identity stop before the first paid call, its own
   three-key spend anchor, `--dry-run`/`--smoke` proving the whole path with zero network.
3. **`git_state` collapse.** One `market_pulse.provenance.git_state`; the five copies migrated and
   `build_audit_pack.git_state` kept as the name 51 scripts import; an equality test pinned
   to the five copies' behaviour measured on a deliberately dirty tree before they were removed.
4. **Serving pin** `results/sku_pilot_serving.json`, written before any run artifact exists, with a
   test that asserts artifact ↔ code equality in both directions.
5. **Preflight extension.** `scripts/preflight_serving_guards.py` drives the POSITIONS guards both
   ways against real transformers + peft; 13 of 13 PASS; still exits 1 when the libraries are absent.
6. **Cost projection** `results/sku_projection.json`: arithmetic over named artifacts, four corners,
   the decode uplift stated as an assumption, total against the $0.35 cap with headroom.

**The serving pin, in one line:** `SERVING_CONFIG=POSITIONS`, the NF4 base with the adapter OFF
(`merge_state: base-no-adapter`, `adapter_sha256: null`), greedy (`do_sample: false`), forward batch
1, `MODEL_REVISION 842da3794eaa0b77d5f08bae87a17459d91ff475`, `max_new_tokens 800`.

**The invariant: no paid calls in this contract.** No pod, no endpoint, no template, no `/run`
request of any kind was made. The only client that ran is the in-process fake, and `--smoke` is
proved below to create no spend anchor at all.

---

## Commits

| # | commit | what |
|---|---|---|
| 0.1 | `1131d78` | team-lead docs, unedited: SPEC 3.17 (9), the brief, STATUS.md |
| 0.2 | `e657db7` | the strip's marker enumeration learns `sku-b-ratification-3` |
| D1 | `68c84bb` | the POSITIONS serving path — a fourth config and a closed op table |
| D3 | `7bc0bad` | one `git_state`, and the drift it was hiding named |
| D4 | `0577bef` | `results/sku_pilot_serving.json` — the identity stop, before the run |
| D4′ | `c0b0ecc` | the pin's ordering check must survive the run it constrains |
| D2 | `b6cf872` | the sku-b driver — proved end to end on `--smoke`, zero network |
| D5 | `a2b66bc` | the preflight learns the POSITIONS guards, both ways |
| D6 | `de9a637` | `results/sku_projection.json` — and the upper corner does not fit |
| — | `8530f97` | the importer count re-derived — 51, not "some forty" |
| — | `9157118` | **the cap's in-run stop CRASHED on its first call, and was never exercised** |
| — | `2beff78`, `25f921b`, `c5670c4` | the report, and its two corrections |
| — | `31fb3ff` | `run_leg`'s two accumulators are the run's, and their order matters |
| tail | `8b9301f` | the vault tail — the day's log, hot.md, the Dv pointers |

Order is not the brief's numbering and that is deliberate: D3 before D2 because the brief calls the
driver "caller six", so landing the driver first would have written a seventh `git_state` copy and
then migrated it; D4 before D2 because the driver's identity stop reads the pin.

### Each commit ran its own suite, on its own checkout

`git checkout <sha>` in the repository itself (a detached worktree cannot run this suite —
`data/raw/` is gitignored and `tests/test_train_qlora.py` raises at collection without it), then
`python3 -m pytest -q`. Every row prints `git rev-parse --short HEAD` and one content fact that
differs across the phase (`grep -c '^def test_' tests/test_positions_driver.py`), so a checkout
that silently did nothing cannot pass for a run — see the note below.

```
sha        head       driver_tests   suite
1131d78    1131d78    (file absent)  1 failed, 1636 passed, 2 skipped   <- RED BY CONSTRUCTION, Dv133
e657db7    e657db7    (file absent)  1637 passed, 2 skipped
68c84bb    68c84bb    (file absent)  1675 passed, 2 skipped
7bc0bad    7bc0bad    (file absent)  1684 passed, 2 skipped
0577bef    0577bef    (file absent)  1694 passed, 2 skipped
c0b0ecc    c0b0ecc    (file absent)  1694 passed, 2 skipped
b6cf872    b6cf872    24             1718 passed, 2 skipped
a2b66bc    a2b66bc    24             1718 passed, 2 skipped
de9a637    de9a637    24             1728 passed, 2 skipped
8530f97    8530f97    24             1728 passed, 2 skipped
2beff78    2beff78    24             1728 passed, 2 skipped
9157118    9157118    30             1734 passed, 2 skipped
25f921b    25f921b    30             1734 passed, 2 skipped
c5670c4    c5670c4    30             1734 passed, 2 skipped
8b9301f    8b9301f    30             1734 passed, 2 skipped
31fb3ff    31fb3ff    30             1734 passed, 2 skipped
```

**An earlier attempt at part of this table was invalid, and the table above is its rerun.**
`git checkout` ABORTS on a dirty tracked file — the report itself was being edited at the time —
and with stderr redirected the loop printed a number for every commit while the tree never moved:
two commits whose test files differ by six functions both reported `1734`. The identical number was
the only tell. So the whole table was re-run from a clean tree with HEAD and a content fact printed
per row. A verification loop that cannot fail loudly is not a verification.

`make check` on HEAD:

```
1734 passed, 2 skipped in 52.64s
```

`ruff check .` → `All checks passed!` · `ruff format --check .` clean (the formatter is not in
`make check`, so it is run separately).

### Byte identity — nothing on the DO-NOT list moved

Baselined before the first write-capable action and re-checked at the end. 16 of 16 unchanged:

```
b1bfa40d1f5073ec  results/sku_pilot_prereg.json
d4ced2a8ba00b48b  results/sku_pilot_prereg_v2.json
46f0d4d396476555  results/baselines.json
8b4faa0787dea842  results/spend_phase4.json
de767900a1ea578e  src/market_pulse/prompts.py
920c7f203b9f0e38  config/registry.yaml
21b50bac55c77683  config/lexicon.yaml
e301bb4f48f527e4  results/sku_reference_leaflet.json
80e4e12c0278f8cc  results/sku_text_pack_manifest.json
9e7dadf5fe392301  results/sku_prefilter_census.json
ba77b381a6d3c4d0  data/annotation/sku_a_text/text30.csv
ccae5cc8cd3909a6  results/uni_probe.json
9a157f91cdaf4e26  results/uni_probe_v2.json
71f1ec4884286961  results/srv2d_cost.json
92be7717868008fc  results/captions_gm4_atb19.json
3653a98618058c44  docs/SPEC.md        <- the file WITH the team lead's (9) block; not edited here
moved: 0
```

The two registered prompt texts are unedited and still hash to what the pre-registration pinned:

```
positions_post_gm4 ca6303c157d46e707aaf3fc52c7a05ed1450e24c26db0e7c93eefba4f6968754
positions_text_gm4 7250b87aa1c2de407e06ab9eed565dd4d88025add7be0d2d2a87607c0d872860
```

---

## D1 — the serving path

The brief asked for the both-ways config↔op refusal. The existing router could not express it. It
read

```python
if (op == "caption") != (served == serving.CAPTION_CONFIG):
```

which is correct for three configs and two ops and **silently permissive for four and three**: a
`batch` job on POSITIONS reads `False != False`, passes the guard, and is answered by whatever
client POSITIONS loaded — scored on the bare base at an 800-token ceiling, inside a record naming
POSITIONS. Measured rather than argued: reverting the router to that expression under the new
matrix test reddens exactly three of twelve cells.

```
FAILED tests/test_positions_serving.py::test_every_cell_of_the_config_by_op_matrix[batch-POSITIONS]
FAILED tests/test_positions_serving.py::test_every_cell_of_the_config_by_op_matrix[positions-A]
FAILED tests/test_positions_serving.py::test_every_cell_of_the_config_by_op_matrix[positions-B]
3 failed, 9 passed, 26 deselected in 0.29s
```

`serving.CONFIG_OPS` is a closed table read whole; the preflight prints the full matrix (below).

```
383:POSITIONS_CONFIG = "POSITIONS"
392:CONFIGS = ("A", "B", CAPTION_CONFIG, POSITIONS_CONFIG)
408:CONFIG_OPS = {
```

**The 256-vs-400 lie is dead in code, and its two records are declared, not re-pinned.** `describe`
answered `local_llm.MAX_NEW_TOKENS` (256) for every configuration while `CaptionClient` has
generated 400 since vis-a. Nothing broke because no caller compares the field —
`caption_gm4_5c1.expected_worker()` asserts four fields and this is not one of them — which is why
it survived two paid sessions. It now reads `serve_handler.MAX_NEW_TOKENS[config]`, held in a test
against the `max_new_tokens` default of the client class each config builds, with a source control
that the loader builds that class.

**`results/captions_gm4_atb19.json` and `results/serving_visc_smoke.json` still hold
`max_new_tokens: 256` and are NOT touched.** They say what the worker said; a record edited after
the fact is worse than a record that names a bug. The team lead should read those two fields as
"what `info` reported", not as what was generated.

Three existing tests moved with the code, each named because a moved test is a claim:

* `tests/test_serve_handler.py` — eight `handle(..., info={})` call sites now pass
  `INFO_A = {"serving_config": "A"}`. Under the closed table an info dict naming no config answers
  nothing, which is the same rule `assert_serving` states one layer up. The empty dict was a test
  convenience, never a production shape.
* `tests/test_vis_a_caption.py::test_the_merge_state_table_covers_every_config_and_nothing_else` —
  the "all merge states distinct" assertion became a statement about what the field describes.
  CAPTION and POSITIONS load the identical weights; a fourth state invented to keep the count would
  be describing the prompt inside a field about the checkpoint. What separates them in a record is
  `serving_config`, which `assert_serving` compares.
* two refusal-message matches follow the new message, which now names the whole routing table.

---

## D2 — the driver

`scripts/positions_gm4_skub.py --smoke`, real inputs, fake endpoint, zero network:

```
page leg   108 pages sent (of 159 available, 19 posts) in 7 job(s), largest 7.99 MB
text leg   30 rows in 1 job(s)
dump       17 columns: item, page, file, sha256, brand_raw, brand_id, line, category, size, fat,
           price_promo, price_old, discount_pct_printed, price_qualifier, tier, depth,
           depth_disagrees_with_printed
endpoint       <smoke> · POSITIONS/base-no-adapter
  revision      842da3794eaa0b77d5f08bae87a17459d91ff475
  ceiling       800 new tokens, greedy, batch 1
  prompts       positions_post_gm4 ca6303c157d4… · positions_text_gm4 7250b87aa1c2…
  warm-up positions_post_gm4   stop  []
  warm-up positions_text_gm4   stop  []
  page job 00  17 item(s)  ok  7.85 MB
  page job 01  17 item(s)  ok  7.70 MB
  page job 02  16 item(s)  ok  7.78 MB
  page job 03  17 item(s)  ok  7.79 MB
  page job 04  14 item(s)  ok  7.74 MB
  page job 05  17 item(s)  ok  7.99 MB
  page job 06  10 item(s)  ok  5.61 MB
  text job 00  30 item(s)  ok  0.03 MB
  page data/annotation/captions_5c1/posts_media/atb_market_official_4340.jpg 0 position(s)
  page data/annotation/captions_5c1/posts_media/atb_market_official_4341.jpg 1 position(s)
  …one line per source, 138 of them…
  text @telegraf_kremenchuk:71024                                     1 position(s)

92 positions from 138 sources · 19 unreadable · 27 empty · 92 carry a crossed-out price
· no spend of $0.35
```

* **Exactly the 108 sent pages**, never the 159 available (R2), and each page's sha re-checked
  against the bytes on disk rather than trusted from the reference's `images_verified` block — that
  field records what was true when the reference was built.
* **The 30 rows through the seven GIVEN columns only.** The five tick columns are bar 3's gold and a
  test asserts they never appear in what travels. Ids, order and `given_sha256` are re-derived before
  a single row is sent.
* **The dump's 17 columns are DERIVED** from `results/sku_pilot_prereg_v2.json ::
  bars.price_pair_accuracy.procedure`, not retyped beside it. The derivation caught its own bug:
  "the page's file and sha256" is one phrase with an `and` inside it, and splitting first produced a
  column literally called `the page's file` — legal-looking JSON nobody can address. A shape check
  now refuses any produced name that is not an identifier, and a test drives it.
* **The attribute column is the WIRE name.** The registered sentence says `fat`, because v2 keeps
  every bar byte-equal to v1 and predates the `fat` → `attribute` rename of 3.17 (8). Read through
  `positions.wire_key("attribute", "dairy")`; a test measures both directions — a reply carrying
  `"fat"` parses to `attribute_pct == 2.5`, and one carrying `"attribute"` is refused as an unasked
  key.
* **A refusal is a reason, never an empty answer.** The record's `unreadable` and `empty_answers`
  source sets are asserted disjoint, and `unreadable_by_reason` counts the kinds.
* **The payload guard refuses, never shortens.** A page over budget on its own raises rather than
  re-encoding or splitting the page across calls.
* **The identity stop restates nothing.** `serving.assert_serving(client.info(),
  pin["expected_worker"])`, the pin's block handed over whole. Driven with a client answering
  `serving_config: CAPTION` — the shape an endpoint updated from the wrong template has — it refuses
  before any call reaches the client.
* **`--smoke` writes no spend anchor.** Asserted, because a $0 contract that created the paid
  session's anchor would silently re-base its counter at today's balance.

### The finding: the in-run cap stop had never run, and crashed the first time it did

The gate is only wired when a budget exists, and under `--smoke` there is no ledger and
`--project-stop-usd` defaults to `None` — so `budget is None`, `gate` was never passed to
`run_leg`, and all 24 driver tests ran the loop with `stop=None`. Driven for the first time
(`--smoke --project-stop-usd 0.35`) it raised on its first call:

```
    seen = leader.projection(
        boot_seconds, float(client.timing()["worker_seconds"]), done, rows_total, rate)
KeyError: 'worker_seconds'
```

A client that has made no call has no such key. The cap-enforcement path would have died on the
paid attempt, at the first re-projection, after the money was spent. Three defects behind it:

1. **The clock was indexed, not read.** `billed_seconds()` now uses `.get` and reads an absent
   clock as `0.0`.
2. **The counter was per LEG.** `run_leg` owned its own outcome list, so `done` restarted at 0 when
   the text leg opened while the billed clock carried the whole page leg — and `and index` skipped
   each leg's first job, so the text leg had **no gate at all**. Both lists are the run's now, the
   gate closes over them, and it returns `None` at `done == 0` instead of being skipped by position.
3. **The formula re-added a cold start that was already billed.**
   `caption_gm4_5c1.projection` prices `rows_total × marginal + COLD_START_USD` — vis-b's caption
   constant. By the time any gate runs the boot is inside the measured seconds, so adding $0.0733
   on top double-counts it. The driver has its own now: everything paid is in `billed`, only what
   is LEFT is projected, and the marginal is measured from *after* the 3.17 (9) warm-up so neither
   the cold start nor the two non-gold calls is multiplied by 138.

The fake endpoint gained a **synthetic clock** — vis-c's 183.58 s boot plus 2.5 s/call, between
vis-b's 2.34 s/image and srv-2d's 4.26 s/row. Without one the marginal is zero and the gate can
never fire, which is a gate nothing proves. The record labels it (`timing.smoke: true`).

Measured on the real population, `--project-stop-usd 0.35`:

```
gates at calls_done 17 34 50 67 81 98 108 (7 of them), calls_total 138
the LAST is the text leg's first job and carries the page leg's 108
boot 183.58 s = $0.0563 · warm-up 5.0 s · projected $0.1636 · nothing unbought
```

and at `--project-stop-usd 0.10`:

```
STOP before positions_post_gm4 job 01: the run projects $0.1636 against $0.1000 left of the
$0.35 cap. A cap is not raised to finish a run
STOP before positions_text_gm4 job 00: …
17 asked · 121 unbought · stopped_early true
```

---

## D3 — one `git_state`

The five copies had drifted in **two** ways, and a clean tree can see neither (all five return
`dirty: []` there):

| copy | sorts? | ignores |
|---|---|---|
| `run_baseline` | yes | `results/baselines.json` |
| `eval_zero_shot` | yes | its results file + its ledger |
| `train_xlmr_baseline` | yes | `results/baselines.json`, `results/spend_3b.json` |
| `freeze_testsets_v3` | **no** | the record being written |
| `build_audit_pack` | **no** | the record being written |

`git status --porcelain` emits tracked changes first and untracked after, each block path-sorted, so
`sorted()` is a real behavioural difference the moment a tree carries both. Measured on a throwaway
dirty repo **before** the copies were removed; the five outputs are pinned in
`tests/test_provenance.py`. `sort` is therefore a named parameter and not a standardisation: every
record already on disk was written under one of the two readings.

```
test_the_fixture_really_separates_the_two_readings PASSED
test_run_baseline_s_reading PASSED
test_eval_zero_shot_s_reading PASSED
test_train_xlmr_s_reading PASSED
test_the_two_unsorted_readings[freeze_testsets_v3] PASSED
test_the_two_unsorted_readings[build_audit_pack] PASSED
test_the_record_being_written_is_left_out_of_its_own_dirty_list PASSED
test_no_script_defines_its_own_copy_any_more PASSED
test_the_five_migrated_producers_still_answer PASSED
9 passed in 0.68s
```

Negative control: flipping `run_baseline` to unsorted and `build_audit_pack` to sorted reddens
`test_the_five_migrated_producers_still_answer`.

**`build_audit_pack.git_state` keeps its name.** The brief's five is the list of *definitions*;
**51** scripts do `from build_audit_pack import git_state`, and that import is what every record's
`git` block is written through. Migrating the name instead of the body would have been a 51-file
diff for no behaviour change. (The `7bc0bad` commit message says "forty-five" — a number written
before it was counted. `grep -rl "from build_audit_pack import git_state" scripts/ | wc -l` says
**51**, and the two code docstrings were corrected to it; this report is the authority.) The five definitions now delegate, and a source guard
refuses a sixth copy:

```
scripts/run_baseline.py:88:def git_state() -> dict:
scripts/eval_zero_shot.py:151:def git_state() -> dict:
scripts/freeze_testsets_v3.py:81:def git_state(mine: Path) -> dict:
scripts/build_audit_pack.py:161:def git_state(mine: Path) -> dict:
scripts/train_xlmr_baseline.py:91:def git_state() -> dict:
src/market_pulse/provenance.py:42:def git_state(*ignore, sort: bool = False, root: Path | None = None) -> dict:
```

Not in `market_pulse.records`: that module's own first paragraph says "the package is not the place
that knows where the repo is", and this one shells out to git.

---

## D4 — the serving pin

`results/sku_pilot_serving.json`, written by `scripts/write_sku_serving_pin.py` and committed before
any run artifact exists. `expected_worker` is six fields and the driver restates none of them.

The revision is **corroborated, not typed**: `docs/SPEC.md:424` abbreviates it (`842da3794eaa…`) and
a worker cannot be held to an abbreviation, so the full sha is checked against
`results/captions_gm4_atb19.json :: endpoint.worker.revision_requested` — the freshest paid record on
this base — and the law's prefix against the full value. A mistyped sha is a refusal, driven by a
test.

Negative controls that fire: each of the six expected fields, broken **and** removed (a missing field
reads as `<absent>` and refuses); a moved instrument sha stops the writer; a wrong revision is
refused; the overwrite guard fires and `--force` clears it.

The ordering claim is checked against **git**, not the filesystem (`c0b0ecc`). The first version
asserted "no sku-b-run artifact exists in `results/`" — true today and false the moment sku-b-run
lands, i.e. a green suite whose first red is the operator's own run. The invariant is the ordering:
`git log --diff-filter=A` for the pin and for each named run artifact, `merge-base --is-ancestor`,
skipping files git has never seen. Control: pointing the artifact list at
`results/sku_pilot_prereg_v2.json` — committed before the pin — reddens it.

---

## D5 — the preflight, full output

Run on `transformers 5.14.1 · peft 0.20.0 · torch 2.13.0`, which is the volume's stack. Exit 0.

```
[transformers] Last layer must use `full_attention`, but got `sliding_attention`. Forcing last layer to `full_attention`.
local   transformers 5.14.1 · peft 0.20.0 · torch 2.13.0
volume  transformers 5.14.1 · peft 0.20.0

subject Gemma4ForConditionalGeneration from config, 135,207,040 params
  isinstance(model, PeftAdapterMixin)  True
  getattr(model, 'active_adapters')    method PeftAdapterMixin.active_adapters, bool() = True   <- an API, not an answer
  getattr(model, 'peft_config', None)  None

1. bare real model            assert_no_adapter  ACCEPT
   control (the vis-a guard)                      REFUSE — the caption model carries an adapter (Gemma4ForConditionalGeneration, active_adapters).

2. after add_adapter          peft_config ['default'] · active_adapters() ['default']
   assert_no_adapter                              REFUSE — the base-only model carries an adapter (Gemma4ForConditionalGeneration, default). SPEC amendments 3.13 (3) and 3.17 (9) serve the NF4 BASE with the adapter OFF — answers written through a classification adapter are another instrument and nothing in the output file could say so.

--- SPEC 3.17 (9): the POSITIONS configuration ---

4. settings(POSITIONS)        POSITIONS · adapter None
   ADAPTER_DIR  set            REFUSE — config POSITIONS serves the base with the ADAPTER OFF (SPEC amendment 3.17 (9)) and ADAPTER_DIR is set. Answers written 
   MERGED_DIR   set            REFUSE — config POSITIONS serves the base with the ADAPTER OFF (SPEC amendment 3.17 (9)) and MERGED_DIR is set. Answers written t
   MODEL_REVISION unset          REFUSE — config POSITIONS needs MODEL_REVISION and it is unset: SPEC amendment 3.17 (9) fixes this instrument at the PINNED base 

5. the adapted real model     assert_no_adapter  REFUSE — the base-only model carries an adapter (Gemma4ForConditionalGeneration, default). SPEC amendments 3.13 (3) and 3.17 (9) 

6. the config x op matrix (only the CONFIG_OPS cells may be answered)
   A          batch=answer(ok)  caption=refuse(ok)  positions=refuse(ok)
   B          batch=answer(ok)  caption=refuse(ok)  positions=refuse(ok)
   CAPTION    batch=refuse(ok)  caption=answer(ok)  positions=refuse(ok)
   POSITIONS  batch=refuse(ok)  caption=refuse(ok)  positions=answer(ok)

7. payload guard at 8.0 MB
      8000000 bytes            ACCEPT
      8000001 bytes            REFUSE — over.jpg encode above the 8.0 MB job budget on their own. RunPod's /run ceiling is 10 MB; raise --max-payload-mb deliber

8. a reply truncated mid-JSON REFUSE — malformed JSON
   an empty array               ACCEPT   <- the control

PASS  the fixed guard ACCEPTS a bare real model
PASS  the fixed guard REFUSES an adapter-carrying one
PASS  the control fires: the vis-a guard refuses the bare model
PASS  POSITIONS serves the base with no adapter directory
PASS  POSITIONS refuses ADAPTER_DIR
PASS  POSITIONS refuses MERGED_DIR
PASS  POSITIONS refuses an unpinned base
PASS  the adapter refusal reaches the POSITIONS config too
PASS  every config x op cell behaves as CONFIG_OPS says
PASS  a job exactly at the payload budget passes
PASS  a job one byte over it refuses rather than shortening the album
PASS  a truncated tail is a parse REFUSAL, never an empty answer
PASS  the control: an empty array is an ANSWER and is accepted
```

With `peft` absent it still exits **1** with its "do NOT treat this as a pass" message — verified on
the system interpreter (`real exit 1`).

---

## D6 — the cost projection

`results/sku_projection.json`. Every input names its artifact; nothing was measured to produce it.

**Rate.** `results/srv2d_cost.json :: rate.usd_per_second` = **$0.00030669/s**. Its own record
corroborates it across five endpoints billed the same day, within 1%.

**Page leg — per IMAGE, never per post.** `results/captions_gm4_atb19.json` (vis-b) is the freshest
record that paid for ATB leaflet captions, and it captioned **exactly the 108 images** sku-b's page
leg sends — the same files at the same encoding on the same base at the same revision.

```
worker_seconds 492.07 − boot 239.004 = 253.066 s over 108 images = 2.3432 s/image
```

The boot subtracted is the pre-registered cold start ($0.0733 ÷ the rate); vis-b's record carries no
`projection` block of its own, so its own boot is not on file — which is exactly the failure the ADR
retraction describes ("a whole cold start inside `worker_seconds`, per-post rate 2× too high").

**Corroboration.** `results/captions_gm4_visc.json`: `(1307.956 − 183.58) / 478 images` =
**2.3523 s/image**, an independent session with a different album size (3.32 images/call against
vis-b's 5.68). The two agree to **0.4%**, which is what makes this a rate rather than one run's
weather.

**Never used.** vis-b's `cost.usd = $0.3869` is a *balance delta for the whole session*. $0.3869 / 19
posts = $0.0204 is a number about the account; multiplying it by a page count would price 108 albums
plus 108 cold starts. The record names it in a `never_used` block so a reader can see it was
rejected rather than overlooked.

**Text leg.** `results/srv2d_cost.json :: measured.like_for_like_seconds_per_row` = **4.262 s/row** —
srv-2d's 758-row parity pass, the same base on the same serverless runtime, text in and JSON out,
no image on the wire. The only artifact that prices an image-free call on this stack.

**The decode-length uplift is an ASSUMPTION and is labelled one.** No artifact prices a positions
reply, because none has ever been generated. The uplift used is the ratio of the registered
ceilings — **800/400 = 2.0** for the page leg against vis-b's captions, **800/256 = 3.125** for the
text leg against srv-2d's rows. A ceiling bounds the longest honest answer, so this is an **upper**
bound; the projection at uplift 1.0 is reported beside it as the lower one. Two biases, opposite and
both stated: applying the uplift to the whole marginal over-counts (image prefill does not grow with
the reply), and taking a per-image rate from a 5.7-image-per-call run under-counts the per-call
overhead of a 1-image-per-call one.

**Cold start as a range**, never substituted: **$0.0563** measured (183.58 s, off
`results/captions_gm4_visc.json :: projection.per_slice[0].cold_start_usd_measured_here`) and
**$0.0733** pre-registered (SPEC 3.15 (3) / runbook §C.1).

### The four corners

| corner | page | text | warm-up | cold | **total** | headroom vs $0.35 |
|---|---:|---:|---:|---:|---:|---:|
| no uplift · measured cold | $0.0776 | $0.0392 | $0.0020 | $0.0563 | **$0.1752** | +$0.1748 (50%) |
| no uplift · pre-registered cold | $0.0776 | $0.0392 | $0.0020 | $0.0733 | **$0.1922** | +$0.1578 (45%) |
| stated uplift · measured cold | $0.1552 | $0.1225 | $0.0055 | $0.0563 | **$0.3396** | +$0.0104 (3%) |
| stated uplift · pre-registered cold | $0.1552 | $0.1225 | $0.0055 | $0.0733 | **$0.3566** | **−$0.0066 — over** |

Arithmetic, spelled out for the first and last rows:

```
page  108 × 2.3432 s × 1.0   × $0.00030669 = $0.0776   |  × 2.0   → $0.1552
text   30 × 4.2620 s × 1.0   × $0.00030669 = $0.0392   |  × 3.125 → $0.1225
warm  (2.3432 + 4.2620) s    × $0.00030669 = $0.0020   |  uplifted → $0.0055
cold                                          $0.0563  |            $0.0733
                                              -------              -------
                                              $0.1752              $0.3566
```

**The reading, unsoftened: the pilot fits the cap comfortably at the lower corner and sits ON the cap
at the stated upper one.** The decode uplift is the whole spread, and it is an assumption about a
reply nothing has generated. SPEC 3.17 (9)'s non-gold warm-up is the first thing that will price it
for real.

**And what an early stop costs is not money.** The driver re-projects before every job and halts when
the run would pass what is left of the cap, so an overrun is impossible — but a page leg that stops
early is *not* a cheaper pilot. Bar 1's registered page set is EXACTLY the 108 sent pages (R2), and a
post whose pages were only partly bought still has a gold set written against all of them. Fewer
pages moves the numerator and not the denominator, which reads as a model that missed brands. **If
the stop fires, the finding is about the cap and not about the instrument** — and that is a
team-lead ruling, not something the driver should paper over.

---

## Verify

| claim | command | result |
|---|---|---|
| the suite is green on HEAD | `make check` | 1734 passed, 2 skipped |
| every commit is green on its own checkout | `git checkout <sha> && pytest -q` ×9 | table above; `1131d78` red by construction (Dv133) |
| lint and format | `ruff check .` · `ruff format --check .` | passed · clean |
| nothing on the DO-NOT list moved | sha of 16 paths, before and after | 0 moved |
| the registered prompts are unedited | `prompts.prompt_sha256` ×2 | `ca6303c1…` / `7250b87a…`, equal to prereg v2 |
| the op table is closed | `pytest tests/test_positions_serving.py -k matrix` | 12 passed; the old XOR reddens 3 |
| `git_state` reproduces the five | `pytest tests/test_provenance.py -v` | 9 passed, output above |
| the pin matches the code both ways | `pytest tests/test_sku_serving_pin.py` | 10 passed |
| the guards fire on real libraries | `preflight_serving_guards.py` | 13/13 PASS, exit 0 |
| the driver runs end to end at $0 | `positions_gm4_skub.py --smoke` | 138 sources, 92 positions, no spend |
| the cap's in-run stop fires | `--smoke --project-stop-usd 0.10` | stops both legs, 17 asked, 121 unbought |
| its counter is cross-leg | `--smoke --project-stop-usd 0.35` | 7 gates, last at 108/138 |
| the projection is re-derivable | `pytest tests/test_sku_projection.py` | 10 passed |

New tests this phase: 97 (38 D1 · 9 D3 · 10 D4 · 30 D2 · 10 D6). Suite 1637 → 1734.

---

## Deviations

**Dv133 — one commit is RED on its own checkout, by construction.** `1131d78` carries the team-lead
docs including SPEC 3.17 (9); that block is what the marker enumeration of
`tests/test_sku_prereg.py` does not know about yet, and step 0.2 (`e657db7`) is what greens it.
Reversing the two does not help: a commit carrying only the test edit fails on a clean checkout,
where SPEC has no `-3` block. The brief names the failure ("On checkout, ONE test is red BY DESIGN")
and forbids fixing it any other way. Filed rather than hidden, because it collides with the standing
"`make check` green after every commit" rule.

**Dv134 — `docs/STATUS.md` was committed in step 0.1 although the brief's list names only
`docs/SPEC.md` and the brief.** STATUS.md arrived modified in the working tree and its own handoff
paragraph authorises it: *«рабочее дерево при передаче несёт стандартный хвост (daily log 11.08,
index, STATUS) — step 0 брифа sku-b коммитит»*. Committed unedited, not opened for editing.

**Dv135 — two producer scripts were written for artifacts the brief names as files.**
`scripts/write_sku_serving_pin.py` (D4) and `scripts/write_sku_projection.py` (D6). Assumption
stated: every result file in this repo has a producer, a hand-built record drops what the shared
stamper adds (the `git` block), and both artifacts have to be *re-derivable* for their tests to
compare artifact against code. Neither script does anything the brief did not ask for; both are
read-only over artifacts plus arithmetic, and a test greps `write_sku_projection.py` for
`EndpointClient` / `urlopen` / `requests` / `guard.balance` to prove it reaches no network.

**Dv136 — the paid non-gold warm-up is implemented although D2's bullet list does not name it.**
The brief's authority header ratifies "smoke-before-legs" and SPEC 3.17 (9) states it as law: the
paid session "opens with a smoke call on NON-gold inputs (a synthetic image and a text row outside
the 30-row pack) before either leg touches gold". A driver without it could not comply. It is priced
in D6 and the pack is checked not to contain the warm-up row.

**Dv137 — three existing tests moved with D1's code.** Listed in full under D1 with the reason for
each. None weakens a check; the merge-state one replaces a proxy assertion (all states distinct)
with a statement about what the field describes.

**Dv138 — `peft` was not installed on this Mac.** It was installed into a scratch venv built with
`--system-site-packages`, exactly as the preflight's own refusal message instructs. `transformers`
5.14.1 and `torch` 2.13.0 were already present and are the volume's versions. **No repo dependency
moved** — `pyproject.toml` is untouched and `make check` still imports no torch. Consequence for the
next session: the preflight needs that venv (or an equivalent) and will exit 1 under the plain
interpreter, which is the correct behaviour and not a failure.

**Dv139 — the projection's summary block is named `against_the_cap`, not `verdict`.**
`tests/test_sku_prereg.py::test_nothing_here_carries_a_bar_result` refuses a `verdict` key anywhere
in `results/sku_*.json`, and it fired on this record. The guard is right to be narrow — a
pre-registration that scores itself is not one — and the block is a reading against the cap, not
against a bar. The **field** was renamed; the gate was not loosened.

**Dv140 — the deliverables were landed out of the brief's numbering** (0 → D1 → D3 → D4 → D2 → D5 →
D6). Reason under *Commits* above: the driver is `git_state`'s caller six and reads the pin, so
landing it first would have created work to undo. No deliverable's content changed.

---

## What the team lead is being asked to look at

1. **The projection's upper corner does not fit** ($0.3566 against $0.35). Nothing is tuned to make
   it fit. The decision is the team lead's: authorise on the lower corner and accept that a stop may
   fire, raise nothing, or split the legs across the cap deliberately.
2. **A page leg that stops early breaks bar 1's registered denominator** (R2: exactly the 108 sent
   pages). If the §C.1 gate fires mid-leg, the resulting recall is not the registered measurement.
3. **`max_new_tokens: 256` in two paid records is wrong and stays wrong.**
   `results/captions_gm4_atb19.json` and `results/serving_visc_smoke.json` report what `info` said,
   not what was generated (400). Declared here rather than re-pinned.
4. **The preflight now needs a venv carrying `peft`** (Dv138). Without one it exits 1, which is a
   finding, not a pass.
5. **The in-run cap stop was broken and is now fixed and measured** (`9157118`, section under D2).
   It is worth a second pair of eyes because it is the only thing standing between a projection
   that lands on the cap and an overrun — and it had a `KeyError` on its first call.

---

# Fix pass (Dv141+) — the cap discipline, hardened before the paid run ($0)

## Read-back

**F1 (blocker).** `JOB_TIMEOUT_S` 1800 → 900, and a job the CLOCK killed (`TIMED_OUT`, or the
client's deadline) ends the RUN rather than the batch — its items forfeit and named, the remainder
`unbought`, the record still written.
**F2.** After both non-gold warm-up calls the whole run is projected from what they measured, each
leg from its own call, and a projection over what is left of the cap REFUSES before any gold call —
record written with `stopped_before_gold: true`, no dump on disk, no attempt consumed (3.17 (10)(a)).
**F3.** A `spend_now` crash after the paid legs no longer loses the record: `cost.usd: null` plus a
note naming the failure, and the anchor survives.
**F4.** `--smoke` redirects `--out` and `--record` on their own defaults, so a half-explicit smoke
cannot plant a fake record at the paid run's path.
**F5.** `--project-stop-usd` TIGHTENS the cap and never replaces it — `min(explicit, what is left)`.
**F6.** The idle-timeout tail (60 s, $0.0184) is a named term inside the driver's `projection()`, the
F2 go/no-go and `scripts/write_sku_projection.py`; `results/sku_projection.json` is regenerated.

**The invariant: no paid calls in this contract.** No pod, no endpoint, no template, no `/run`
request of any kind. Every number below comes from a file already in the repo or from the in-process
fake.

## Commits

| # | commit | what |
|---|---|---|
| 0.1 | `77c0820` | team-lead docs, unedited: SPEC 3.17 (10), the fix brief, STATUS.md |
| 0.2 | `c6ab33f` | the marker enumeration learns `sku-b-ratification-4` |
| 0.3 | `f2d1506` | ADR `sku-b-serving-and-cap-discipline` + INDEX row |
| F1a | `305e48d` | `serving.JobExpired` — a job the CLOCK killed is its own error |
| F1–F5 | `0c11642` | the cap discipline in the driver |
| F6 | `aafbb43` | the idle tail enters the projection, and it costs |

### Each commit ran its own suite, on its own checkout

Same method as the phase above and for the same reason: the four dirty tracked files (this report and
the vault tail) were **stashed first**, because `git checkout` aborts on a dirty tracked file and a
loop that swallows stderr then prints a number for a tree that never moved. Every row prints
`git rev-parse --short HEAD` and two content facts that differ across the pass.

```
sha        head       driver_tests  jt900   suite
77c0820    77c0820    30            0       1 failed, 1733 passed, 2 skipped  <- RED BY CONSTRUCTION
c6ab33f    c6ab33f    30            0       1734 passed, 2 skipped
f2d1506    f2d1506    30            0       1734 passed, 2 skipped
305e48d    305e48d    30            0       1738 passed, 2 skipped
0c11642    0c11642    41            1       1749 passed, 2 skipped
aafbb43    aafbb43    41            1       1750 passed, 2 skipped
```

`77c0820` is red exactly as `1131d78` was, and for the same mechanism: the strip is name-agnostic so
the pin holds, the enumeration is not so the amendment cannot land unseen. Before that commit the pin
was re-derived on this checkout — `registered_law(SPEC)` →
`973c87890ad049d5fa09879de148794f171994fac64437128bcecbaeade36604`, equal to what
`results/sku_pilot_prereg_v2.json` pins, while the live file hashes to `01b3569f4901c8ca`. No
ratification name survives the strip.

`make check` on HEAD:

```
1750 passed, 2 skipped in 53.68s
```

`ruff check .` → `All checks passed!` · `ruff format --check .` → `224 files already formatted`.

### The DO-NOT list — one file moved, and it is the team lead's own

15 of the 16 baselined paths are byte-identical to the prep phase's table. The sixteenth:

```
3653a98618058c44 -> 01b3569f4901c8ca   docs/SPEC.md
```

That is the `sku-b-ratification-4` block, arriving from the team lead and committed **unedited** in
step 0.1 — the brief's own instruction. The registered law did not move: the strip removes every
marked block, so the pin re-derives to `973c8789…` as above. `results/sku_pilot_prereg.json`,
`_v2.json`, `results/sku_pilot_serving.json`, `baselines.json`, `spend_phase4.json`, both registered
prompt texts, the frozen sets, the lexicon and the registry are untouched.

---

## F1 — no single job can out-bill the cap

The blocker, as arithmetic. The projection gate re-prices **between** jobs and cannot see inside one,
so the per-job execution timeout is the only thing bounding a wedged worker:

| | seconds | at $0.00030669/s | against the $0.35 cap |
|---|---|---|---|
| the value this replaced | 1800 | **$0.5520** | **1.58× the whole cap** |
| the value now | 900 | $0.2760 | fits on its own |
| the longest honest job predicted | ~400 | $0.1227 | the text leg is ONE job of 30 rows |
| the page leg's largest of 7 | ~80 | $0.0245 | 17 pages at the stated uplift |

900 s is also what `scripts/runbook_5b.md` and `scripts/runbook_srv2b.md` already pass as
`--execution-timeout`, so the driver and the endpoint that serves it now agree.

**The type, and what it deliberately is not.** Detection is not a string match on an error message.
`serving.JobExpired` is raised at the two sites where the clock ends a job — RunPod's `TIMED_OUT`
status and this client's own deadline — and it is a **subclass** of `ApiError`, so every
`except ApiError` written before it keeps catching it. It fires on the STATUS and not on
`!= COMPLETED`: `FAILED` and `CANCELLED` stay ordinary errors. Widening it would have silently
converted *a failed job is named per item and the run continues* into *any job failure kills the
run* — a much more expensive behaviour than the one being fixed, and the negative control is a test.

```
tests/test_serving.py::test_a_job_the_clock_killed_is_its_own_error PASSED
tests/test_serving.py::test_only_the_clock_raises_the_clock_error[FAILED] PASSED
tests/test_serving.py::test_only_the_clock_raises_the_clock_error[CANCELLED] PASSED
tests/test_serving.py::test_a_deadline_that_passes_while_the_job_runs_is_the_clock_too PASSED
```

In the driver, `run_leg` now returns the reason the run ended and `main` breaks out of the leg loop
on it. Driven end to end on the fake with one gold job replaced by a `JobExpired`:

```
test_a_job_the_clock_kills_ends_the_run_and_not_just_the_batch     PASSED
test_an_ordinary_job_failure_names_its_items_and_the_leg_continues PASSED
test_no_single_job_can_out_bill_the_cap                            PASSED
```

The first asserts the record's `ended_by` names TIMED_OUT, that `{row["leg"]}` is `{"page"}` only —
the text leg never opens — that the killed job's own items are named rather than dropped, and that
the remainder is `unbought`. The second is its control: a `FAILED` job leaves `ended_by` None, both
legs run, and nothing is unbought.

## F2 — the go/no-go, and the assumption under it

The in-run gate cannot answer this question: it needs a gold call to have a marginal at all, so by
the time it first fires the pilot has bought something. Under one attempt that is the most expensive
outcome available — the money is gone and no bar is scoreable. F2 is the only stop that can refuse
while the session is still worth nothing, and (10)(a) says it consumes NO attempt.

Each leg is priced from **its own** warm-up call. The warm-up makes exactly two, one per shape, and
the clock is read between them; a single blended figure would charge the image call's seconds to the
text leg's 30 calls.

```
test_the_go_no_go_refuses_before_the_first_gold_call        PASSED
test_a_warm_up_the_budget_can_afford_proceeds_to_gold       PASSED
test_the_go_no_go_prices_each_leg_from_its_own_warm_up_call PASSED
test_the_warm_up_reads_the_clock_between_its_two_calls      PASSED
```

The refusal test asserts what "zero gold artifacts" actually means on disk: **`assert not
out.exists()`** — the dump is never written — plus `asked == 0`, all 138 sources `unbought`,
`stopped_before_gold: true`, and a `why` that names the v3 route rather than a raised cap. The
proceed test is its control at a budget above the projection.

**The assumption this rests on, and it is checkable rather than assumed.** The per-leg marginals are
only honest if the weight load has already been billed by the time the warm-up runs. It has:
`serve_handler.Worker.__call__` loads on the **first job of any op**, and the driver's first job is
the `info` handshake — so `boot_seconds`, read immediately after `info`, contains the cold start and
neither warm-up call carries it. Had the load been lazy until the first `generate`, the page warm-up
would have swallowed ~183 s, the page marginal would have read ~183 s/call, and F2 would refuse a
perfectly healthy run. That is why it is named here.

## F3, F4, F5 — the three quiet ones, each driven through `main`

`--smoke` deliberately creates no ledger, so the whole ledgered branch of `main` is invisible to the
$0 path — the same shape as the defect the prep phase found in the cap stop. Two of these three tests
therefore drive the **ledgered** branch, with only `serving.EndpointClient` and `guard.balance`
replaced; `read_ledger`, the budget arithmetic, the record write and the ledger append all run for
real.

```
test_a_balance_read_that_crashes_after_the_paid_legs_keeps_the_record PASSED
test_an_explicit_project_stop_tightens_the_cap_and_never_replaces_it  PASSED
test_a_half_explicit_smoke_never_writes_at_the_real_record_default    PASSED
```

* **F3** lets the balance read succeed twice (the anchor, the pre-run cap check) and raise on the
  third — the one after the paid legs. The run still returns 0, the record is on disk with
  `cost.usd: null` and `"connection reset"` in `cost.read_failed`, the dump the run paid for is
  there, and the ledger's own run entry carries a null spend and the reason.
* **F5** pre-writes an anchor $0.30 above the balance, so $0.05 of the cap is left, and passes
  `--project-stop-usd 9.99`. The run refuses at **$0.05**, not at 9.99: the record's
  `go_no_go.budget_usd` and `projection.stop_at_usd` both read 0.05. Under the old code the flag
  replaced the budget and the one in-run guard was off.
* **F4** moves the module's `REPO_ROOT`/`RECORD`/`DUMP` to a tmp tree (with `--root` still at the
  checkout, so only where the DEFAULTS resolve is moved) and runs `--smoke --out <explicit>`. The
  real record path stays absent, the smoke copy lands under `results/smoke/`, and the explicit `--out`
  is still honoured.

## F6 — the idle tail, and what it does to the finding

Serverless bills **wall uptime**, not jobs: the worker stays up for the endpoint's idle timeout after
the last reply and that tail is charged to whoever woke it. Every endpoint this repo's runbooks
create is made with `--idle-timeout 60` — 60 s × $0.00030669/s = **$0.0184**. It is charged once per
session, so it sits beside the cold start rather than inside either leg's rate.

| corner | before | after | headroom | |
|---|---|---|---|---|
| lower — no uplift, cold start measured | $0.1752 | **$0.1936** | +$0.1564 | fits |
| lower — no uplift, cold start pre-registered | $0.1922 | **$0.2106** | +$0.1394 | fits |
| stated — ceiling-ratio uplift, cold start measured | $0.3396 | **$0.3580** | −$0.0080 | **OVER** |
| stated — ceiling-ratio uplift, cold start pre-registered | $0.3566 | **$0.3750** | −$0.0250 | **OVER** |

**The count of corners over the cap goes 1 → 2, and that is the finding, not the arithmetic.** At the
stated decode uplift the pilot exceeds $0.35 on *both* readings of the cold start. Nothing was tuned:
the rate, both per-image sources, the uplift and the corner structure are re-derived from the same
artifacts at the same shas, and only the one term was added.

The consequence is in the record's own `against_the_cap.reading` and pinned by a test: **the go/no-go
of 3.17 (10)(a) is now the likely first real event of sku-b-run.** Unless the two warm-up calls
measure a decode materially shorter than the ratio of the registered ceilings, the run will refuse
itself before the first gold call — which consumes no attempt and returns the pilot to the team lead
for a v3 registration at the measured price. That is the designed behaviour of (10)(a), not a
failure; it is stated here because it changes what "authorise sku-b-run" means.

```
test_the_idle_tail_is_priced_once_per_session_and_names_its_source PASSED
test_the_verdict_says_plainly_that_the_stated_corners_do_not_fit   PASSED
test_every_corner_is_priced_against_the_cap                        PASSED
test_the_idle_tail_is_a_named_term_in_the_go_no_go_too             PASSED
```

## Verify

| claim | command | result |
|---|---|---|
| the suite is green on HEAD | `make check` | 1750 passed, 2 skipped |
| every commit is green on its own checkout | stash → `git checkout <sha> && pytest -q` ×6 | table above; `77c0820` red by construction |
| lint and format | `ruff check .` · `ruff format --check .` | passed · 224 files formatted |
| the prereg pin still re-derives | `write_sku_prereg.registered_law(SPEC)` | `973c8789…` = the pinned sha; live file `01b3569f…` |
| the DO-NOT list held | sha of 16 paths | 15 identical; `docs/SPEC.md` = the team lead's own (10) block |
| one job cannot out-bill the cap | `pytest -k out_bill` | 900 s × rate = $0.2760 < $0.35; 1800 s = $0.5520 |
| a clock-killed job ends the run | `pytest -k "clock_kills or ordinary_job"` | 2 passed, both directions |
| the go/no-go fires both ways | `pytest -k go_no_go` | 3 passed; no dump on the refusal |
| the record survives a dead balance read | `pytest -k balance_read` | 1 passed, ledgered branch driven |
| `--project-stop-usd` only tightens | `pytest -k project_stop` | refuses at $0.05, not at 9.99 |
| the smoke cannot touch the real record | `pytest -k half_explicit` | 1 passed |
| the projection is re-derivable | `PYTHONPATH=src python3 scripts/write_sku_projection.py` | 4 corners, 2 OVER; `pytest tests/test_sku_projection.py` 11 passed |
| the driver still runs end to end at $0 | `--smoke` | go/no-go proceeds, 138 sources, 92 positions, no spend |
| the in-run gate is still cross-leg | `--smoke --project-stop-usd 0.35` | go/no-go proceeds; 7 gates, last at 108/138 |

## Deviations

**Dv141 — F1's detection is a new exception type in `src/market_pulse/serving.py`, not a string
match in the driver.** The brief named the behaviour ("a job that ends `TIMED_OUT` … ends the RUN")
and not the mechanism. Matching `"TIMED_OUT" in str(err)` would pin the driver to the exact wording
of a message in another module. `serving.JobExpired` is ~10 lines, is a subclass so no existing
caller changes, and is raised only on the two clock sites. It does touch a shared module — declared
for that reason.

**Dv142 — `FakeEndpoint` gained one constructor knob, `gold_seconds_per_call`.** Not asked for. On a
flat clock the go/no-go and the in-run gate compute the **identical** number by construction, so any
budget low enough to trip the mid-leg stop is refused before the first gold call — and
`test_the_gate_stops_the_run_and_leaves_the_rest_unbought` could not be driven through `main` at all.
The knob models the one scenario the in-run gate exists for: a warm-up that priced cheap and legs
that turned out expensive. It defaults to the old value, so every other test is unchanged.

**Dv143 — `run_leg` now returns a value.** It returned None and mutated its two accumulators; it now
also returns the reason the RUN ended (or None). The docstring's "neither is returned" line moved
with it.

**Dv144 — both records carry `stopped_before_gold`.** The brief asked for it on the refusal record.
The completed record carries `false` as well, so a reader keys on one field in either — and the two
records are built from one shared `head` dict so the stop path cannot drift from the run path.

**Dv145 — `spend_or_note` catches `Exception` blind**, with a `noqa` and a docstring saying why.
Narrowing it to the failures `runpodctl` is known to produce would re-open the hole for the next one,
and there is nothing above that frame that could use the exception. The record outranks the reason.

**Dv146 — one row of the prep phase's Verify table is now superseded, and was left standing.** It
reads `--smoke --project-stop-usd 0.10 → stops both legs, 17 asked, 121 unbought`. Under F2 that
command refuses **before** the first gold call instead. The brief authorised exactly one prose fix in
that table (1728 → 1734) and the table is the record of what was true at the phase's HEAD, so the row
was not rewritten — the supersession is named here. The equivalent command today is
`--smoke --project-stop-usd 0.35` (the row below it), which still proceeds and still gates cross-leg.

**Dv147 — no other deviation.** The six fixes are the six in the brief, none ran deeper than briefed,
and nothing on the DO-NOT list was touched.

---

## What the team lead is being asked to look at (fix pass)

1. **Two corners are now over the cap, not one** ($0.3580 and $0.3750 against $0.35), and both are at
   the stated decode uplift. The practical reading: **sku-b-run will probably refuse itself at the
   go/no-go** unless the warm-up measures a shorter decode. Under (10)(a) that costs the warm-up and
   the boot (~$0.08–0.10) and consumes no attempt — but it is a likely outcome, not a corner case,
   and it is worth deciding in advance whether that refusal is acceptable or whether the legs should
   be split across two registrations.
2. **F2's arithmetic depends on the boot being billed to the `info` handshake.** Verified in
   `serve_handler.Worker.__call__` (the load is on the first job of any op) rather than assumed — but
   it is the single assumption that, if wrong, makes the go/no-go refuse a healthy run.
3. **`JobExpired` lives in `src/market_pulse/serving.py`** and is therefore visible to every phase
   that uses the endpoint client, not only sku-b (Dv141).
4. **The prep report's `--project-stop-usd 0.10` row is superseded** (Dv146) — left standing on
   purpose, since the table records what was true then.
