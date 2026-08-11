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

Order is not the brief's numbering and that is deliberate: D3 before D2 because the brief calls the
driver "caller six", so landing the driver first would have written a seventh `git_state` copy and
then migrated it; D4 before D2 because the driver's identity stop reads the pin.

### Each commit ran its own suite, on its own checkout

`git checkout <sha>` in the repository itself (a detached worktree cannot run this suite — 
`data/raw/` is gitignored and `tests/test_train_qlora.py` raises at collection without it), then
`python3 -m pytest -q`:

```
1131d78  1 failed, 1636 passed, 2 skipped in 49.38s   <- RED BY CONSTRUCTION, see Dv133
e657db7  1637 passed, 2 skipped in 49.03s
68c84bb  1675 passed, 2 skipped in 49.71s
7bc0bad  1684 passed, 2 skipped in 50.46s
0577bef  1694 passed, 2 skipped in 50.69s
c0b0ecc  1694 passed, 2 skipped in 51.06s
b6cf872  1718 passed, 2 skipped in 51.84s
a2b66bc  1718 passed, 2 skipped in 52.02s
de9a637  1728 passed, 2 skipped in 51.44s
```

`make check` on HEAD:

```
1728 passed, 2 skipped in 52.04s
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
| the suite is green on HEAD | `make check` | 1728 passed, 2 skipped |
| every commit is green on its own checkout | `git checkout <sha> && pytest -q` ×9 | table above; `1131d78` red by construction (Dv133) |
| lint and format | `ruff check .` · `ruff format --check .` | passed · clean |
| nothing on the DO-NOT list moved | sha of 16 paths, before and after | 0 moved |
| the registered prompts are unedited | `prompts.prompt_sha256` ×2 | `ca6303c1…` / `7250b87a…`, equal to prereg v2 |
| the op table is closed | `pytest tests/test_positions_serving.py -k matrix` | 12 passed; the old XOR reddens 3 |
| `git_state` reproduces the five | `pytest tests/test_provenance.py -v` | 9 passed, output above |
| the pin matches the code both ways | `pytest tests/test_sku_serving_pin.py` | 10 passed |
| the guards fire on real libraries | `preflight_serving_guards.py` | 13/13 PASS, exit 0 |
| the driver runs end to end at $0 | `positions_gm4_skub.py --smoke` | 138 sources, 92 positions, no spend |
| the projection is re-derivable | `pytest tests/test_sku_projection.py` | 10 passed |

New tests this phase: 91 (38 D1 · 9 D3 · 10 D4 · 24 D2 · 10 D6). Suite 1637 → 1728.

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
