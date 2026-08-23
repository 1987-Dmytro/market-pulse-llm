# `lora-c-run` — a STOP report: the derivation reported short, and arm B has no dataset

**Contract:** `docs/PROMPT-lora-c-run.md` (fresh session, ONE paid pod session, cap $4.00, Dv from
786) · **Spent: $0.0000.** No pod was created, no endpoint exists, the registration is still a
DRAFT and its attempt is unspent.

Two findings stop this contract before `pod create`, and the second is not a judgement call:

1. **The four-leg plan does not fit the $4.00 cap at the rates the contract itself charges.** The
   fixed part alone is 11 019.88 s — **$2.4489** at the worst price a create may meet — and what is
   left pays for at most **48.47 s/step** over the 144 optimizer steps (58.61 at the price the last
   five pods billed). The only two s/step readings this repo holds are **61.047** and **68.442**,
   both above both break-evens and both taken on sequences of at most 1 222 tokens against this
   line's 1 445–2 975. SPEC amendment 3.25 (1) made the cap conditional on exactly this derivation:
   «the cap stays $4.00 until that derivation reports». It reports.
2. **Arm B's 666-row dataset does not exist, no producer renders one, and `pod create` is the
   freeze.** The registration's `legs.arm_b.train_rows` is 666; `population.train` names one file
   of 506; the 160 synthetic rows are raw comments with no `prompt`, `target` or `learn_chars`. The
   record's state is «DRAFT — frozen only by lora-c-run's first `pod create`», so a create would
   SEAL a registration that cannot name half its own experiment, and registering arm B afterwards
   is re-pinning a sealed record — which this contract's DO NOT list forbids. **A cap raise does
   not unblock this one.**

Everything the contract asks for at $0 is DONE and green: step 0.5's two close debts, D1's sibling
trainer with its $0 drive in both directions, and D2's pre-pod arithmetic written into the record.

| commit | what |
|---|---|
| `ed1c341` | team-lead files verbatim — `docs/PROMPT-lora-c-run.md`, `docs/STATUS.md` (day 23) |
| `251afcd` | step 0.5 — the two close debts |
| `7c7035e` | D1 — `scripts/train_qlora_v3.py`, its tests and the encode census |
| `1c84944` | D2 first half — the pre-pod derivation, in the record |
| this | the report |

---

## 0 — the read-back gate (refusal gate), one line each

Every number re-derived from the file that owns it, before step 1. **All match; the gate does not
refuse on any of them.** The two findings above are not read-back mismatches — they are what the
read-back could not cover.

| # | number | re-derived from | reading |
|---|---|---|---|
| 1 | optimizer steps **62 / 82** | `config/qlora.yaml` micro 2 · accum 8 · epochs 2 → `floor(ceil(n/2)/8)×2` | `floor(253/8)×2 = 62` · `floor(333/8)×2 = 82` ✅ |
| 2 | `planned` **64 / 84** | same file → `ceil(n/(2·8))×2` | `ceil(31.625)×2 = 64` · `ceil(41.625)×2 = 84` ✅ |
| 3 | rows **506 / 666** | `results/pass1_sft_v3_train.jsonl` (`wc -l`) · + `results/synthetic_pass1_v1.jsonl` 160 | 506 on disk ✅ · **666 is arithmetic only — no file holds it** ⛔ (Dv786) |
| 4 | E legs **198 + 198** | `results/lora_c_eval_pack.json::calls` | `per_leg: 198`, `legs_bought_by_lora_c_run: 4` ✅ |
| 5 | pass-2 **11 threads, 46 rows** | `results/lora_c_pass2_pack.json::population` | `threads_with_at_least_one_filtered_row: 11`, `filtered_rows: 46`, `legs[0].items` is 11 long ✅ |
| 6 | ceiling **3 072** (3.26) | `config/qlora.yaml` `training.max_seq_len` = 3072, quoted as law in `authority.amendment_3_26` | ✅, and `quoted_spec` greps all three clauses back into `docs/SPEC.md` |
| 7 | STOP_AT **2 800**, TRUE count | `scripts/tokenize_lora_c_rows.py::STOP_AT` vs the number PARSED out of the 3.26 (2) quotation | equal — and now a test, not a coincidence (step 0.5 (2)) ✅ |
| 8 | **6.14** s/call (pass-1) | `results/prereg_lora_c.json::money.rates…pass_1_seconds_per_call.value` | ✅ charged; the window pod's own direct reading is 2.694083 |
| 9 | **97** s/thread (pass-2) | same block, `pass_2_seconds_per_thread.value` | ✅ charged; r2 realised 23.760 |
| 10 | cap **4.00** | `money.cap_usd_all_in`, and ruling (к) quoted through `quoted()` | ✅ |

Two supporting readings taken at the same time:

- **Every pinned instrument still hashes to what the registration says** — 12 of 12 (`lora_c_data`,
  `lora_c_eval_pack`, `lora_c_pass2_pack`, `lora_c_synthetic`, `pass1_sft_v3_train`,
  `pass1_holdout_100`, `reader_gold_w1_r2`, `pass1_v3.py`, `prompts.py`, `scorer.py`,
  `train_qlora.py`, `pass2_r2.py`).
- **Both `quoted()` rulings and all six `quoted_spec()` amendment clauses still grep back** after
  the team lead's day-23 rewrite of `docs/STATUS.md` — which is what `docs/reports/lora-c-close.md`
  §«Open» 1 said had been checked once, by hand. It is a test now.

## 1 — the money, read from the guard and never from prose

```
$ PYTHONPATH=src python3 scripts/runpod_guard.py
PHASE 4 CLOSED    $32.4708 of $33.00  (final reading 2026-08-16T11:09:48+00:00)
anchor            $22.51 at 2026-08-16T12:14:48+00:00
balance now       $14.37
CYCLE 2 SPENT     $8.1391 of $20.00
REMAINING         $11.8609
```

`$11.8609` is the outer bound the contract names; `$4.00` is what binds. **No reading was logged**
— the guard was run without `--note`, so it wrote nothing to `results/spend_cycle2.json`: there is
no session to anchor.

```
$ runpodctl pod list -a          → []
$ runpodctl network-volume list  → mp-srv2, 100 GB
```

The volume is the always-on rent SPEC 3.23 (4) says is named separately and never inside a step's
figure. It is not this contract's resource and this contract created nothing beside it.

## 2 — step 0.5, the two close debts (`251afcd`)

Both were named as open by `docs/reports/lora-c-close.md`, and both are the same shape: a number or
a guard living in one file with nothing holding it to the file that owns it.

**(1) `quoted()` against `docs/STATUS.md` gets the control `quoted_spec` got in Dv783.** `RULING_V`
and `RULING_K` are the registration's entire authority. The planted paraphrase swaps the guillemets
both rulings quote inside — drift that whitespace normalisation cannot forgive — and the copy lives
in `tmp_path`, never on the real file. Both directions: the copy must raise, the live file must
return its argument unchanged.

**(2) `STOP_AT` is bound to amendment 3.26 (2) through the registration's own quotation of it.** The
number is **parsed out of the quote and never typed a second time** — a second literal in the test
would be a third home for the threshold. The parse carries its own negative control (a mutated
quotation must read a different number), and the tokens record's `stop_threshold`, its
`which_the_amendment_names` and its `by_the_true_count` are all checked against that one reading.
The `by_the_true_count` count is *re-derived*, not copied: every row over the threshold is inside
the published `widest_rows`, so `sum(row.pod_count > law)` is a real recount.

## 3 — D1, the sibling trainer (`7c7035e`)

`scripts/train_qlora.py` is pinned by `results/prereg_lora_b.json` and `results/lora_b_verdict.json`
and may not be edited. `scripts/train_qlora_v3.py` moves **exactly two guards** and holds no second
copy of anything else — `load_sft`, `class_weights`, `content_hash`, `load_for_training`,
`encode_pass1`, `collate`, `train`, `save` and `main` are all reached through the module object.

| guard | where it lives | how it moved |
|---|---|---|
| 1 — the task | `load_sft`: `row["task"] != prompts.PASS1_TASK` | a contextmanager swaps the constant and **puts it back**. A module-level guard cannot be told anything by a parameter, and `prompts.py` is itself pinned |
| 2 — the sha list | `build_pass1`: `SFT_RECORD` = `results/pass1_sft.json` | `build_pass1_v3` reads `results/prereg_lora_c.json::population.train`, and `arm_of` reads the leg from the **registered row count** rather than taking it from a flag |

**Why the provenance dict is written rather than reached for.** `build_pass1`'s names
`results/pass1_sft.json`, `pass1_comment_gm4_v1` and that record's `supervision` block. A v3 run
publishing it would describe another line's dataset in its own record. Everything else in that
function is called; the third read the re-bind touches — `record["instruments"]["prompt_sha256"]`
compared for EQUALITY against `{PASS1_TASK: …}` — is satisfied by not going through `build_pass1`
at all rather than by widening the registration's three-entry prompt map down to one.

### The $0 drive, both directions

**ACCEPT** — `PYTHONPATH=src python3 scripts/train_qlora_v3.py --census`, the real tokenizer at the
pinned revision `842da379…`, through `train_qlora.encode_pass1` itself:

```json
{ "rows": 506, "encoded": 506, "refused": [],
  "max_seq_len": 3072,
  "tokens": {"min": 1445, "max": 2975, "widest_row": "@tarilka_malyuka:746#83"},
  "headroom": 97,
  "sha256": "cf55d3f20216139845d320b4283d543c5283e3475f3c6afa42ea98cf20997c18" }
```

**0 of 506 refused, max 2 975, headroom 97** — agreeing row for row with the count amendment 3.26
was ruled from (`results/lora_c_tokens.json`), which a test asserts. `class_weights` on arm A
returns **four** classes — `null` 0.617073 · `категория_личное` 2.53 · `не_наш_рынок` 0.377612 ·
`сеть_ритейлер` 2.976471 — and `молочный_бренд` is absent, which is the registered reachability
fact read forward, not a surprise.

**REFUSE** — three, each by name:

| planted | raises |
|---|---|
| a `pass1_comment_gm4_v1` row | `task 'pass1_comment_gm4_v1' is not 'pass1_comment_gm4_v3'` |
| the registered file one row short | `not a registered dataset of this line` |
| a row over the ceiling (one-token-per-character tokenizer) | `against a max_seq_len of 3072` |

And the control that says the re-bind is a re-bind and not an edit:
`test_the_pinned_trainer_still_refuses_a_v3_row` — `train_qlora.load_sft` on the real v3 file still
raises, and `test_the_pinned_task_constant_is_put_back` asserts `prompts.PASS1_TASK` reads
`pass1_comment_gm4_v1` again the moment the contextmanager exits.

### What could NOT be driven — arm B

D1 asks that «the full arm A and arm B datasets load and every row of 506 and **666** ENCODES».
**No file on disk is arm B's dataset**, and `class_weights` returning five classes on it cannot be
asserted. This is Dv786 below. `test_the_registration_names_no_arm_b_dataset` pins the gap rather
than papering over it.

## 4 — D2 first half, the pre-pod arithmetic (`1c84944`)

Written into `results/prereg_lora_c.json::money.pre_pod_arithmetic` **before** any create, which is
where D2 says it belongs. The clause that makes the cap conditional is quoted through `quoted_spec`,
not paraphrased.

**No s/step is registered.** None exists at 3 072 and the contract forbids projecting one from
lora-b's ≤1 222-token readings. What is registered instead is the inequality **solved backwards** —
the largest s/step the cap can pay for once every other term is charged, in the unit the smoke
measures.

```
fixed  = boot 500 + load 300
       + base legs        2 × 198 × 6.14 = 2 431.44
       + adapter evals    2 × 198 × 6.14 = 2 431.44
       + pass-2           4 ×  11 ×  97  = 4 268.00
       + training smoke   6 × (121.0 × 1.5) = 1 089.00
       = 11 019.88 s
```

| price | source | budget | fixed | left for 144 steps | **break-even s/step** |
|---|---|---|---|---|---|
| **$0.80/h** | lora-b rung 1, registered — a create refuses above it | 18 000.0 s | $2.4489 | 6 980.1 s | **48.47** |
| **$0.74/h** | what the last five pods actually billed | 19 459.5 s | $2.2652 | 8 439.6 s | **58.61** |

Hard stop = cap / worst rate = **18 000 s**, the stamp `--terminate-after` would carry.

**The readings that exist, against that bar:**

| s/step | what it is | taken at | vs 48.47 | vs 58.61 |
|---|---|---|---|---|
| 61.047 | registered by lora-b | ≤1 222 tokens | over | over |
| 68.442 | measured on lora-b arm A | ≤1 222 tokens | over | over |
| 121.0 | not a reading — a worked example built from the 122 s watchdog | — | over | over |

So the cap is short **even at lora-b's own speed, on rows less than half as long**. This is a
statement about the reachability of the acceptance criterion, not a projected rate: no number above
is used as this line's s/step, and none is written into the record as one.

### What the projection rung would see — a scenario, registered as one

The rung fires at MEASURED rates, and both charged rates have a direct sibling measurement:
**2.694083** s/call (pass1-window r2's own pod) and **23.760** s/thread (pass2-signals r2's) —
0.439 and 0.245 of the charge. At those rates the fixed part is 3 979.2 s and the break-even rises
to **93.47 s/step at $0.80/h · 103.20 at $0.74/h**, i.e. above both lora-b readings.

**Reading:** the session is short, not arithmetically hopeless. It is **undecided** until the smoke
reads s/step at 3 072 — and that decision is not the executor's to take under a cap the derivation
has just reported short. Note also what a KILL would cost here beyond money: **`pod create` is the
freeze**, so an exploratory session that ends at the projection rung leaves a SEALED registration
that still cannot name arm B.

### Proof that only the money block moved

The record was rebuilt by an edited producer, so «only `money` changed» was a belief until it was a
list. Flattened both sides of `1c84944` to key paths:

```
ADDED   37   (all 37 under .money.pre_pod_arithmetic)
REMOVED  0
CHANGED  2   .money.state          OPEN… → DERIVED…
             .producer.sha256      77ef863e… → e512486b…
```

## 5 — the verifier

Baseline **before any edit**, at `6fc6773` with the team lead's `docs/STATUS.md` in the tree:

```
$ make check
ruff check .
All checks passed!
3669 passed, 2 skipped in 601.91s (0:10:01)
exit=0
```

After every code commit of this contract, at `1c84944`:

```
$ make check
ruff check .
All checks passed!
3682 passed, 2 skipped in 624.60s (0:10:24)
exit=0

$ ruff format --check .
435 files already formatted
```

**3 682 = 3 669 + 13**, and the thirteen are this contract's: two parametrised STATUS-quotation
controls, the STOP_AT binding, nine sibling-trainer tests and the derivation's re-computation. The
formatter is checked separately because `make check` does not run it.

A re-read on the CLOSING tree — after the report and vault commits, which touch `knowledge/hot.md`,
a price input `scripts/volume_calc_5c1.py` greps — is in §«The verifier, re-read on the closing
tree» below.

## 6 — the numeric session audit

The contract makes this table the replacement for the subagent second-skeptic (twice silent,
Dv748/Dv779). **There was no session, so every count is zero and the table's job is to say so with
readings rather than with a sentence.**

| axis | reading |
|---|---|
| pods created | **0** — `runpodctl pod list -a` → `[]`, before and after |
| serverless endpoints | **0** |
| per-leg call counts | base v2 **0** · base v3 **0** · arm A **0** · arm B **0** (of 198 each) |
| pass-2 threads run | **0** of 11 × 4 |
| optimizer steps run | **0** of 144, and **0** of the 6 smoke steps |
| refusals seen on a pod | **0** — the three refusals in §3 were bought at $0 on this Mac |
| spend, balance delta | **$0.0000** — cycle-2 spent $8.1391 both before and after |
| spend, billing walk | **$0.0000** attributable; the only live resource is the `mp-srv2` volume's always-on rent, named separately per 3.23 (4) |
| guard reading vs cap | $11.8609 remaining of $20.00 · $4.00 cap untouched |
| attempt | **UNSPENT** — `bars.attempt` is «ONE. No retry, no second draw, no tuning after any eval output is seen», and no eval output of any leg was seen |

Artifact shas (first 16), the tree this report is written against:

| artifact | sha256 |
|---|---|
| `results/prereg_lora_c.json` | `b68d129b73be4575` |
| `results/lora_c_encode_census.json` | `e9544b069efe6e7f` |
| `scripts/train_qlora_v3.py` | `f1d108dc92429aba` |
| `scripts/train_qlora.py` (PINNED, unmoved) | `1a1a0b5983db60d8` |
| `config/qlora.yaml` (revision 3) | `96b4b31865576c24` |

## Deviations from Dv786

Each with its cause tag from the closed enum v2. **Every one was found at $0.**

| # | cause | what |
|---|---|---|
| **Dv786** | `[cause: contract-gap]` [[a_registered_bar_may_have_no_producer]] | **Arm B has a registered row count and no registered file — and the create is the freeze.** `legs.arm_b.train_rows` is 666; `population.train` names one file of 506; `instruments.packs` names five artifacts and none is an arm-B SFT dataset; `results/synthetic_pass1_v1.jsonl`'s 160 rows carry `text`/`rationale`/`subject_type` and no `prompt`, `target` or `learn_chars`, so arm B is not a concatenation but a RENDERING nobody has run. `scripts/build_lora_c_data.py`'s own docstring says «the shared pool and **arm A's rows**» and its argparse carries one `--train-out` and no arm-B output. What is missing is not only a producer: **nothing registered says how a synthetic row is rendered as a v3 query.** `scripts/build_lora_c_synthetic.py` states the isolation as «a synthetic row may never reach the neighbour pool, an eval set or arm A» — that bars synthetic as a NEIGHBOUR and says nothing about synthetic as a QUERY, and ruling (к) («синтетика ~160 … — арм B, тег в provenance, абляция армом A, никогда в холдаут/голд») says nothing either. Drawing a synthetic query's five neighbours from the 515 real rows is therefore permitted and unregistered — a design decision only the team lead can take. And the ordering is forced rather than chosen: the record's own state is «DRAFT — frozen only by lora-c-run's first `pod create`» and `frozen_when_the_pod_exists` lists ten artifacts, `results/prereg_lora_c.json` first. So a create before arm B's file exists seals a registration that cannot name half its experiment, and adding it afterwards is re-pinning a sealed record — which this contract's DO NOT list forbids by name. **A cap raise does not unblock this.** |
| **Dv787** | `[cause: contract-gap]` [[the_expectation_no_reading_reaches]] | **The cap does not cover the four legs at the rates the contract charges.** §4's table. The contract's own fixed part is 11 019.88 s — 61 % of the $0.80/h budget and 57 % of the $0.74/h one — leaving a break-even of 48.47–58.61 s/step against readings of 61.047 and 68.442 taken at less than half these rows' width. Reported rather than projected: the derivation registers no s/step, and the inequality is published in the unit the smoke measures ([[a_published_ratio_is_not_the_gates]]). SPEC 3.25 (1) pre-authorised exactly this report and reserved the raise to the operator, BEFORE a create. |
| **Dv788** | `[cause: contract-gap]` [[two_values_for_one_input_get_quoted_kindly]] | **The contract states the pass-2 leg count twice.** Its fixed part charges `4 × 11 × 97` — four legs — and its order of operations names pass 2 only under «eval A» and «eval B likewise», which is two. The registration's `bars.report_only.pass_2_tables` says «per leg», so four is coherent, and four is the conservative charge under a cap; four is what §4 sums. The difference is 2 134 s = **$0.4742** at the worst price. Named in the record itself rather than chosen quietly — this line has made the one-input-two-values mistake five times already. |
| **Dv789** | `[cause: spec-gap]` [[a_stock_window_needs_the_create_not_a_poll]] | **The card ruling (к) names was last read as out of stock, and the only free test of that is the create that freezes the record.** «один A6000»; `knowledge/hot.md` records A6000 48 GB in EU-RO-1 as `none` and a 4090 24 GB at $0.74/h taken first try, five pods running. A refused create costs $0 and IS the stock test — but a create that SUCCEEDS is this registration's freeze, so stock and freeze cannot be separated and the card is part of what the operator is being asked. The derivation therefore prices BOTH the $0.80/h rung-1 ceiling and the $0.74/h reading rather than assuming a card. |
| **Dv790** | `[cause: process]` [[a_citation_is_not_a_record]] | **A test changed its content under a name a shipped report cites.** `test_the_registration_carries_no_price` asserted `money["state"].startswith("OPEN")`, which stopped being true the moment this contract did what 3.25 (1) ordered. `docs/reports/lora-c-apply.md:481` — «The money block is still **OPEN**, the cap is still $4.00, and `test_the_registration_carries_no_price` still passes» — cites the test by name, and two of that sentence's three clauses are superseded by this contract (the block is DERIVED; the test's content moved). The cap is still $4.00. All three were true when written and a shipped report is not edited to follow a later state. Renaming would strand that citation, so the NAME is kept and the assertions moved: `DERIVED`, the forbidden field names still absent, the fixed part re-summed from its own terms, and the one rate the contract forbids projecting asserted to be a `str` and not a number. Disclosed here rather than left for a reader to notice the docstring no longer matches the title. |
| **Dv791** | `[cause: process]` [[gate_verdicts_need_an_artifact]] | **The census is written to a file the contract only asked to have printed.** D1 says «print the census»; `results/lora_c_encode_census.json` is 12 lines of JSON and is committed beside the print. A verdict a report quotes from stdout is a verdict nobody can re-hash. Named because it is a results file this contract added and no registration pins — and it is deliberately NOT added to `frozen_when_the_pod_exists`, which is a sealed list. |
| **Dv792** | `[cause: process]` [[a_review_that_verifies_a_moving_tree]] | **The closing verifier was started and then edited underneath — void, killed, re-run.** The operator ruled on this report while the closing `make check` was in flight, and recording the ruling means writing `knowledge/hot.md` and the day log. `hot.md` is a price input `scripts/volume_calc_5c1.py` greps, and pytest reads files at run time, so from that edit onward the run described neither tree — the same shape as Dv785 one contract ago, made again. Killed at ~70 % rather than quoted; the reading in §«The verifier, re-read on the closing tree» is a separate run over a tree that did not move under it. The rule this keeps breaking against is simple and was already written down: **do not touch the repo while a verifier is running, including the vault.** |

**The tally, by the grep the template names:**

```python
import re, pathlib, collections
flat = " ".join(pathlib.Path("docs/reports/lora-c-run.md").read_text(encoding="utf-8").split())
tag = {}
for chunk in re.split(r"(?=\*\*Dv\d+)", flat):
    if (m := re.match(r"\*\*Dv(\d+)", chunk)) and (t := re.findall(r"\[cause:\s*([a-z-]+)\]", chunk)):
        tag.setdefault(int(m.group(1)), t[0])
inr = {d: t for d, t in tag.items() if 786 <= d <= 792}
health = sum(1 for t in inr.values() if t in ("contract-gap", "spec-gap", "verify-gap"))
print(len(inr), dict(collections.Counter(inr.values()).most_common()))
print("contract health", health, "· paid", len(inr) - health, "· enum canonicity", len(inr), "of 7")
```

```
7 {'contract-gap': 3, 'process': 3, 'spec-gap': 1}
contract health 4 · paid 3 · enum canonicity 7 of 7
```

«paid» is the enum's residual class (`process`, `tooling`, `model`) and not money: this contract
spent nothing. Four of seven are contract- or spec-gaps; the three that are not are disclosures of my own
edits, and one of them (Dv792) is a repeat of Dv785 from the contract before.

## What the operator is being asked

Three options. **None of them is «open the session and let the projection rung decide»** — the
freeze makes that the one option with an irreversible cost, because a KILL after the smoke leaves a
sealed registration that still cannot name arm B.

1. **Raise the cap.** The derivation says how much is missing at the charged rates; the sibling
   rates say the true requirement is probably lower but genuinely unknown until the smoke.
   This unblocks Dv787 and leaves Dv786 standing.
2. **Cut scope to the legs that can run** — base v2 · base v3 · arm A. Cheaper, and it buys the two
   unknowns (real s/call at v2 and v3 widths, real s/step at 3 072) for the next contract. But
   **a RED on arm A alone says almost nothing**: arm A carries zero real `молочный_бренд` targets,
   so bar 1 is near-unreachable for it by construction — the registration says so under
   `reachability.arm_a_has_no_молочный_бренд_target`. The ablation is the point of the design, and
   this option does not deliver it.
3. **Send arm B's dataset back to a prep contract first** ($0), with the team lead ruling on how a
   synthetic row is rendered as a v3 query. Then `lora-c-run` opens once, with a cap the derivation
   has priced and a registration that names both arms.

## Open, and named rather than closed

1. **The P-NULL question from `lora-c-apply` is still open**, untouched by this contract.
2. **`results/lora_c_encode_census.json` is pinned by nothing.** It is checked against
   `results/lora_c_tokens.json` by a test, which is the strongest tie available without touching a
   sealed list.
3. **`money.pre_pod_arithmetic` is a DERIVATION and not a SEAL.** If the operator raises the cap or
   cuts the legs, the block is re-derived and the numbers above are superseded — they describe the
   four-leg plan at $4.00 and nothing else.
4. **This report is long for a contract that bought nothing.** The length is the two findings'
   arithmetic and the read-back gate the contract demands «in one line each»; the sections that are
   short are the ones with nothing in them (§6).

## Process signals

1. **The derivation was the deliverable, not the preamble.** The contract's own law made the cap
   conditional on it, and running it first — before any create — is what turned an $0.89 KILL into
   a $0.00 report.
2. **The gap arm B has is a shape, not an omission.** `legs.arm_b` was fully registered — rows,
   weights, the ablation's reason — and the only thing missing was the file, which no test asked
   for because no test asks for a file the registration never names.
3. **The break-even is the honest form of a rate nobody has.** Publishing 48.47 s/step as a
   requirement says what 137 s/step as a guess could not: it names what the smoke has to beat.
4. **Two guards, three reads.** The re-bind is exactly two guards, but `build_pass1` also compares
   the prompt map for equality — satisfied by not calling it rather than by widening a registration
   down to one entry, which is the shape that would have moved the record to fit the code.
5. **A test's name is a citation surface.** `test_the_registration_carries_no_price` had to change
   content and could not change name; the report that cites it stays greppable and the change is in
   the ledger instead.


## Addendum — the operator ruled on this report, in this session

Both questions were put to the operator with the arithmetic above in front of them, and both were
answered. **The ruling is recorded here because `docs/STATUS.md` is a team-lead file and the
executor never writes it — п. 1 needs the team lead to register this the way it registered (к),
(л) and (м).**

1. **Arm B first, at $0.** «Сначала $0-контракт на датасет арма B» — a separate prep contract in
   which the team lead rules how a synthetic row is rendered as a v3 query, a producer renders the
   666 rows, and the registration pins the file. Then ONE `lora-c-run` with a derived cap and both
   arms. This is option 3 of §«What the operator is being asked», and it is the only one under
   which the A-vs-B ablation — the reason the line exists — happens at all.
2. **The cap stays $4.00.** «Оставить $4.00 — решать после выбора объёма.» Nothing is raised
   blind: the cap is re-derived in the contract that knows its scope. The derivation in
   `money.pre_pod_arithmetic` describes the FOUR-leg plan at $4.00 and is superseded the moment
   the scope moves — §«Open» 3 already said so, and this is that clause firing.

**What this contract does NOT do with the ruling.** It does not build arm B's dataset. That is a
new contract's scope, it turns on a design decision only the team lead can take (the pool rule bars
synthetic as a NEIGHBOUR and is silent about synthetic as a QUERY), and a paid contract's executor
quietly widening into a $0 prep deliverable is how a scope stops being the operator's to set.
`scripts/train_qlora_v3.py` is ready for it: `arm_of(666)` already reads `arm_b` out of the
registration, and guard 2 will accept that file the moment `population` names it.

## The verifier, re-read on the closing tree

§5's 3 682 was taken at `1c84944` — before this report, the vault tail and the addendum above. Two
of those touch files the suite reads (`knowledge/hot.md` is a price input `scripts/volume_calc_5c1.py`
greps through `quoted(HOT, "~$0.24/day", 0.24)`), so a gate measured before the last commits is a
gate measured on a tree that no longer exists ([[the_gates_evidence_outlived_its_artifact]]).

**A first attempt at that re-read was VOID and was killed rather than quoted** — see Dv792. The
reading below is a run over a tree that did not move under it.

Taken at **`7c0719b`** with the working tree clean at the start — the run stamps `HEAD` and
`git status --porcelain` on both sides of itself, which is what says so:

```
$ HEAD=7c0719b  dirty=[]
$ make check
ruff check .
All checks passed!
3682 passed, 2 skipped in 601.17s (0:10:01)
make_exit=0

$ ruff format --check .
435 files already formatted
fmt_exit=0

$ HEAD_after=7c0719b  dirty_after=[ M knowledge/daily_logs/2026-08-23.md
                                    M knowledge/index.md]
```

**The tree DID move once during the run, and it was the Stop hook, not an edit of mine** — one
appended line, `- 18:17: session ended (auto)`, plus the index the hook regenerates. Disclosed
rather than waved away, because Dv792 is exactly this failure made deliberately. It does not touch
the reading: no pytest input reads `knowledge/daily_logs/` at all, and the grep says so —

```
$ grep -rn "daily_logs" tests/ src/ scripts/ | grep "\.py:" \
    | grep -vE "check-wikilinks|refresh-hot-cache|brain-session-end|context-census"
NONE
```

`knowledge/hot.md`, which IS a suite input, is byte-identical across the run.
