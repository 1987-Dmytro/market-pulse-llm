# `lora-c-close` — the landing manoeuvre for SPEC amendment 3.26

**Contract:** `docs/PROMPT-lora-c-close.md` · **Deviations from Dv781** · **everything $0 — no pod,
no endpoint, no paid call.** Opening HEAD `c15b502`.

| commit | what | staged by path |
|---|---|---|
| `1e9eebf` | `docs(spec)` — 3.26, day-23 STATUS, this contract, **verbatim** | `docs/SPEC.md` `docs/STATUS.md` `docs/PROMPT-lora-c-close.md` |
| `d76091a` | `fix(5c2)` — the strip registry: four touches | `scripts/write_prereg_5c2.py` `tests/test_prereg_5c2.py` `tests/test_sku_prereg.py` |
| `2f8fe17` | `fix(lora-c)` — the raw-spec pin + the field that denied its own file (Dv781, Dv782, Dv783) | `scripts/write_lora_c_prereg.py` `results/prereg_lora_c.json` `tests/test_lora_c_prep.py` |
| this report | `docs(report)` | `docs/reports/lora-c-close.md` |
| the vault tail | `chore(vault)` | `knowledge/hot.md` · daily log · index |

No `git add -A` anywhere; this report cannot name its own sha
([[provenance_cannot_name_itself]]), and the vault tail's follows it.

One mechanical deliverable, and it turned up one thing the contract's own premise did not cover.
That finding is the lead, not a footnote:

> **`results/prereg_lora_c.json` pins the RAW `docs/SPEC.md`, not the stripped law.** Every other
> pin in the repo goes through `write_sku_prereg.registered_law()`, so a new marked block is taken
> off before hashing and the pin survives. `write_lora_c_prereg.py:647` calls `sha(SPEC)`. A new
> block therefore MOVES it, and the contract's «Nothing else changes» is true of the registered law
> and false of that record. Two tests were red on arrival, not one.

---

## 1 — the grep that found the touches

The command the contract names, run first:

```
$ git log -p --all -S "amendment-3.25" -- scripts tests | head -80
commit 681b11ea959874387ebb8078e3930f997ce94872
    fix(lora-c): registration DRAFT v2 carries the count, and amendment 3.25 lands in the strip
    …
    The landing manoeuvre 3.25 owed: `amendment-3.25` added to write_prereg_5c2.BLOCKS_TODAY and to
    test_sku_prereg's enumerated strip list, and the planted intruder moved on to 3.26.
```

The 3.25 landing is **one commit, three files, four touches**. Enumerated rather than counted, by
grepping the live tree for the whole family so a sibling list could not hide behind a different
amendment number:

```
$ grep -rn "amendment-3\.2[0-9]" scripts tests src
scripts/write_prereg_5c2.py:100      "amendment-3.25",          <- [1] the block registry
tests/test_prereg_5c2.py:249         "amendment-3.25",          <- [3] the literal tail BLOCKS_TODAY[10:]
tests/test_prereg_5c2.py:321   intruder = "amendment-3.26"      <- [4] the planted intruder
tests/test_sku_prereg.py:295         "amendment-3.25",          <- [2] the enumerated strip list
tests/test_build_dashboard.py:359    …amendment-3.20…           (a named block, not an enumeration)
tests/test_export_dashboard_data.py:182  …amendment-3.20…       (same)

$ grep -rn "BLOCKS_TODAY\|KEEP_BLOCKS" scripts tests src
scripts/write_sku_prereg_b2.py:63  KEEP_BLOCKS = ("sku-b-ratification-7", "sku-b-ratification-8")
```

The two dashboard hits split by name, not by position — they reach into one block by name and do
not enumerate the family, so they cannot go stale on a new one. `write_sku_prereg_b2.KEEP_BLOCKS` is
a two-name keep and is likewise not an enumeration of what the file carries. **Four touches, and the
fourth (the intruder) is the one the suite does not force — it has to be moved by hand.**

## 2 — the two red tests on arrival

```
$ python3.11 -m pytest tests/test_sku_prereg.py -q
>       assert prereg.RATIFICATION_NAME.findall(spec_text) == blocks
E       AssertionError: Left contains one more item: 'amendment-3.26'
tests/test_sku_prereg.py:297: AssertionError
1 failed, 31 passed in 0.78s
```

That is the one the contract names. The second was found by running the producer the contract does
NOT name, before touching anything:

```
$ PYTHONPATH=src python3.11 scripts/write_lora_c_prereg.py --out $SCRATCH/prereg_rebuild.json
$ diff <(sorted json of results/prereg_lora_c.json) <(sorted json of $SCRATCH/prereg_rebuild.json)
10c10
<    "sha256_of_the_spec": "ff300bc7013eef64e35ea12ab35ebb7448ec04ebc27d463164c74673bb2c48e9"
---
>    "sha256_of_the_spec": "b5aa39af8fc002ec89d5b0cf8eb184bd772f2ccfdfa48e35d7cfd3dd9943077a"
```

One field. `test_every_producer_is_driven_end_to_end_and_rebuilds_its_shipped_bytes
[scripts/write_lora_c_prereg.py]` compares those bytes, so it was red too.

**The blast radius was then enumerated rather than discovered one red test at a time** — search for
the sha itself, which finds every artifact carrying it regardless of which producer wrote it, and
for every producer that hashes a team-lead file raw:

```
$ grep -rl ff300bc7013eef64…  results/ docs/ config/ scripts/ tests/
results/prereg_lora_c.json                       <- the only one
$ grep -rl 987a70b576baa449…  results/ docs/ config/ scripts/ tests/   # STATUS.md's old sha
                                                 <- none
$ grep -rnE "SPEC\.read_bytes|sha\(SPEC\)|STATUS\.read_bytes|sha\(STATUS\)" scripts/*.py src/**/*.py
scripts/write_lora_c_prereg.py:647    "sha256_of_the_spec": sha(SPEC),   <- the only one
```

## 3 — the diff

`git diff --stat` for the code commit:

```
 results/prereg_lora_c.json     | 14 +++++++++++---
 scripts/write_lora_c_prereg.py | 31 ++++++++++++++++++++++++++++---
 scripts/write_prereg_5c2.py    | 12 +++++++++++-
 tests/test_lora_c_prep.py      | 33 +++++++++++++++++++++++++++++++++
 tests/test_prereg_5c2.py       | 19 ++++++++++---------
 tests/test_sku_prereg.py       |  8 ++++++++
 6 files changed, 101 insertions(+), 16 deletions(-)
```

### The manoeuvre — four touches, mirrored exactly

| # | file | what | forced by |
|---|---|---|---|
| 1 | `scripts/write_prereg_5c2.py:101` | `BLOCKS_TODAY += "amendment-3.26"` + its docstring paragraph | the producer's own `check_the_strip_family_is_what_it_says` |
| 2 | `tests/test_sku_prereg.py:303` | the enumerated strip list + its comment | the red test the contract names |
| 3 | `tests/test_prereg_5c2.py:250` | the literal tail `BLOCKS_TODAY[10:]` | a red assertion |
| 4 | `tests/test_prereg_5c2.py:324` | the planted intruder `-3.26` → `-3.27`, docstring updated | **nothing** — by hand |

```diff
@@ scripts/write_prereg_5c2.py
     "amendment-3.25",
+    "amendment-3.26",
 )
@@ tests/test_prereg_5c2.py
         "amendment-3.25",
+        "amendment-3.26",
     ), "after the seal"
-    intruder = "amendment-3.26"
+    intruder = "amendment-3.27"
@@ tests/test_sku_prereg.py
         "amendment-3.25",
+        # 3.26 — the operator's ruling of 2026-08-23 … `max_seq_len` 2 816 → 3 072 (3.25 (1)
+        # superseded), the 2 800 STOP threshold reads the REAL tokenizer's count with no
+        # `TEMPLATE_SLACK`, and the tokens-per-character model retires for ceilings. …
+        "amendment-3.26",
     ]
```

### The registration — the assertion replaced by a read

`results/prereg_lora_c.json` had to be rebuilt for the sha (§2). Rebuilding it alone would have left
the record pinning a `docs/SPEC.md` that carries 3.26 while the adjacent field said, in bold, that
no such block exists — a record contradicting itself about the very file it pins. So the assertion
was replaced by three quotations through the machinery already in the file:

```diff
-      "1_max_seq_len_SUPERSEDED": "… **No marked block in docs/SPEC.md records that ruling yet** —
-       SPEC is a team-lead file — so a later contract grepping SPEC for the ceiling in force will
-       find 2 816 and must read this field beside it",
+      "1_max_seq_len_SUPERSEDED": "… That ruling is now REGISTERED — `amendment_3_26` below quotes
+       the block that carries it, so a contract grepping docs/SPEC.md for the ceiling in force
+       reads 3 072 from the law itself and not from a field beside it",
+      "amendment_3_26": {
+        "1_max_seq_len": quoted_spec(AMENDMENT_326_1),                          # 3 072
+        "2_the_stop_threshold_reads_the_true_count": quoted_spec(AMENDMENT_326_2),
+        "3_the_ratio_model_retires_for_ceilings": quoted_spec(AMENDMENT_326_3),
+      }
```

`quoted_spec` whitespace-normalises and raises `SystemExit` if the text is not in `docs/SPEC.md`, so
this field cannot outlive its state the way its predecessor did — the build refuses instead
([[verbatim_quotes_must_be_grepped]], [[a_reading_that_outlived_its_state]]). **That refusal had
never been watched fire**, and a claim about a guard nobody has seen refuse is not evidence
([[guard_selftest_negative_control]]) — `test_the_spec_quotation_refuses_a_paraphrase` now drives
both directions on a copy in `tmp_path`, and `docs/SPEC.md` itself is never written to.

## 4 — no registered law moved

The contract asks this to be asserted, not asserted about. Two legs.

**Leg 1 — the bytes.** The raw file moved; all three readings of the registered law are byte-identical
across the block's arrival, and each matches the digest its pins carry:

```
raw            head ff300bc7013eef64   live b5aa39af8fc002ec   MOVED
keep=()        head 973c87890ad049d5   live 973c87890ad049d5   IDENTICAL   <- v1–v4 pins
keep=5c2 ten   head 3dd43923edc18e72   live 3dd43923edc18e72   IDENTICAL   <- prereg_5c2_run.json
keep=b2 two    head 6818926d22b2a46b   live 6818926d22b2a46b   IDENTICAL   <- sku_pilot_prereg_b2.json
```

**Leg 2 — the three modules that own those pins**, the failing one plus the law subset. The b2 leg
is included because it derives a THIRD pin over `docs/SPEC.md` through `keep=b2.KEEP_BLOCKS` and the
contract's «the law subset» does not name it:

```
$ python3.11 -m pytest tests/test_sku_prereg.py tests/test_prereg_5c2.py tests/test_sku_prereg_b2.py -q
88 passed in 1.24s
```

**Preflight**, on the names this contract touched:

```
$ make preflight ARGS='amendment-3.26 BLOCKS_TODAY registered_law'
pin registry: 1563 paths pinned by results/*.json
[3] pins — 4 of the 8 touched paths are pinned by a record
    scripts/write_lora_c_prereg.py  <- results/prereg_lora_c.json.producer.sha256 77ef863e0958…
    scripts/write_prereg_5c2.py     <- results/prereg_5c2_run.json.producer.sha256 1477512a7ea5…
    docs/SPEC.md                    <- 6 pin(s)
    results/prereg_lora_c.json      <- results/prereg_lora_c.json.frozen_when_the_pod_exists
                                       FROZEN (no digest)
[4] digests — 2 of 4 pinned paths match every digest on them
```

The two that DIFFER both differed at `c15b502` and are by design, checked rather than assumed:
`docs/SPEC.md` differs from every pin on it because the pins are over the STRIPPED law (leg 1 above
is the actual check, and preflight cannot see a strip); `scripts/write_prereg_5c2.py` differs from
the sealed 5c2 record's `producer.sha256` because that pin is `1477512a…` and HEAD's file already
hashed `3ac6c848…` before this contract touched it — a sealed record's producer sha is never
re-taken, which is what makes each landing move it. `results/prereg_lora_c.json` carries
`frozen_when_the_pod_exists` and no digest: it is a DRAFT, and **that is the sentence that makes its
rebuild legal rather than merely necessary** — the contract's DO NOT forbids re-pinning a SEALED
record, and no pod exists.

## 5 — `make check`, full green on a stable tree

Formatter first, because the verifier does not run it:

```
$ python3.11 -m ruff format --check .
433 files already formatted
```

Then the verifier, over a tree that did not move under it (Dv785 is the run that did):

```
$ ruff check . ; pytest -q
All checks passed!
........................................................................ [ 98%]
.......................................................................  [100%]
3669 passed, 2 skipped in 590.47s (0:09:50)
exit=0
```

**3 669 against `lora-c-apply`'s closing 3 668** — one test, and it is
`test_the_spec_quotation_refuses_a_paraphrase` (Dv783). The landing manoeuvre itself adds none: it
greens four assertions that were already standing, which is what an enumeration is for.

## Deviations from Dv781

Each with its cause tag from the closed enum v2. **Every one was found at $0; there is no money on
this contract.**

| # | cause | what |
|---|---|---|
| **Dv781** | `[cause: contract-gap]` [[the_contracts_scope_is_narrower_than_the_rulings]] | **«Nothing else changes» is true of the registered law and false of one record.** The landing manoeuvre's whole premise is that a pin goes through `registered_law()`, so a new marked block is stripped and the pin survives. `write_lora_c_prereg.py` hashes the RAW `docs/SPEC.md` — `sha(SPEC)` at line 647, one call in the whole repo — so the block moved `results/prereg_lora_c.json` and the byte-comparison rebuild test was red beside the one the contract names. Step 2 demands full green and step 3's commit list does not reach that record, which is the gap. Rebuilt (a DRAFT, `frozen_when_the_pod_exists`, no pod), given its own commit so it can be reverted alone, and the blast radius ENUMERATED by grepping the old sha and every raw-hash call site rather than discovered one red test at a time ([[count_in_prose_is_not_the_enumeration]]). Both searches return exactly one file. |
| **Dv782** | `[cause: contract-gap]` [[a_reading_that_outlived_its_state]] | **The record asserted the gap that 3.26 closed, in bold.** `1_max_seq_len_SUPERSEDED` read «**No marked block in docs/SPEC.md records that ruling yet**» — written by me eight hours earlier, true then, false the hour the team lead wrote the block. Rebuilding the sha alone would have shipped a record that pins a file and, in the field beside the pin, denies what that file contains. The DO NOT list forbids touching anything beyond the manoeuvre; the alternative was to ship a self-contradicting registration and report it, which is strictly worse than either doing nothing or fixing it. Fixed the way the previous contract's Dv770 fixed three others — the assertion replaced by a READ, three `quoted_spec` quotations of 3.26 (1)(2)(3). This is the second half of [[a_ruling_can_outrun_the_law_it_amends]]: the grep that guards a quotation checks fidelity to the file, never that the file still holds the operative law, and the two diverge for exactly as long as a ruling is ahead of its block. |
| **Dv783** | `[cause: verify-gap]` [[guard_selftest_negative_control]] | **The refusal the record now offers instead of an assertion had never been seen to refuse.** `quoted_spec` is what makes Dv782's fix a read rather than a nicer sentence, and the only evidence it greps at all was that it had never raised. `test_the_spec_quotation_refuses_a_paraphrase` drives both directions — a copy of `docs/SPEC.md` with `3 072` respaced to `3072` must raise `SystemExit`, the live file must return its argument unchanged. The producer's other grep (`quoted`, against `docs/STATUS.md`) is in the same state and is NOT covered here; it is named in the open items below rather than fixed, because it is outside even the reading of scope this report already stretched twice. |
| **Dv784** | `[cause: process]` [[a_moved_constant_fails_green]] | **The ordinal I wrote for 3.25 was wrong by two, and nothing could have gone red on it.** `BLOCKS_TODAY`'s docstring called 3.25 «the nineteenth»; the list is ten kept blocks plus 3.19–3.25, so 3.25 is the seventeenth and 3.24's «sixteenth» directly above it is right. Prose in a docstring is checked by no test, which is why it drifted in the previous session and why writing «eighteenth» for 3.26 beside an uncorrected «nineteenth» would have made the correct line look like the error. One word fixed, in the same hunk, disclosed here rather than left silent. |
| **Dv785** | `[cause: process]` [[a_review_that_verifies_a_moving_tree]] | **A baseline suite was started and then edited underneath — void, and killed rather than quoted.** The full run was launched at `c15b502` to establish the opening state and was still going when the first edit landed; pytest reads source at import and run time, so from that moment its result described neither tree. Killed at ~68 %, and the opening state was established instead by two targeted runs against the UNTOUCHED tree — the 1-failed/31-passed above, and the byte diff of the rebuilt registration — both taken before anything was written. The green tail in §5 is a separate run over a tree that did not move under it. |

**The tally, by the grep the template names:**

```python
import re, pathlib, collections
flat = " ".join(pathlib.Path("docs/reports/lora-c-close.md").read_text(encoding="utf-8").split())
tag = {}
for chunk in re.split(r"(?=\*\*Dv\d+)", flat):
    if (m := re.match(r"\*\*Dv(\d+)", chunk)) and (t := re.findall(r"\[cause:\s*([a-z-]+)\]", chunk)):
        tag.setdefault(int(m.group(1)), t[0])
inr = {d: t for d, t in tag.items() if 781 <= d <= 785}
health = sum(1 for t in inr.values() if t in ("contract-gap", "spec-gap", "verify-gap"))
print(len(inr), dict(collections.Counter(inr.values()).most_common()))
print("contract health", health, "· paid", len(inr) - health, "· enum canonicity", len(inr), "of 5")
```

```
5 {'contract-gap': 2, 'process': 2, 'verify-gap': 1}
contract health 3 · paid 2 · enum canonicity 5 of 5
```

«paid» here is the enum's residual class (`process`, `tooling`, `model`) and not money: this
contract spent nothing. The health share is 3 of 5 against `lora-c-apply`'s 8 of 16 — the same
proportion on a tenth of the surface, and both of this contract's contract-gaps are the SAME gap
seen twice, from the sha and from the sentence beside it.

## Open, and named rather than closed

1. **`quoted(…)` against `docs/STATUS.md` has no negative control.** Dv783 gave one to the SPEC grep
   because the record now leans on it; its STATUS twin, which checks `RULING_V` and `RULING_K`, is in
   the state the SPEC grep was in this morning. Both quotations were verified to still grep back
   after the team lead rewrote the day-23 section (they do), so nothing is broken — but that was
   checked by me, once, by hand, which is the shape a test replaces.
2. **3.26 (2) and (3) are now law and no producer reads them as a threshold.** The 2 800 STOP and the
   retired ratio model are quoted into the registration as text. `results/lora_c_tokens.json` still
   publishes BOTH readings of the threshold with `STOP_AT = 2800` as a module constant that predates
   the ruling. Nothing is wrong today — the two readings agree on the verdict — but a bar whose law
   lives in one file and whose constant lives in another is the shape that drifts.
3. **The P-NULL question from `lora-c-apply` is still open**, untouched by this contract: whether the
   rule I wrote is the rule the gate-1 verdict meant. Only the team lead can close it.

## Process signals

1. **The contract's premise was checkable and checking it took one command.** «Nothing else changes»
   is a claim about which producers hash which file how; `grep -rnE "sha\(SPEC\)"` answers it in a
   second and answered it against the contract.
2. **Enumerate the blast radius from the VALUE, not from the failures.** Grepping the old sha across
   `results/` found the affected artifact set in one shot; waiting for red tests would have found the
   same file later and proved nothing about the ones that stayed green.
3. **A record that pins a file may not deny what the file says.** The rebuild and the prose were one
   decision, not two — shipping the sha without the sentence would have manufactured a contradiction
   that neither the old state nor the new one had.
4. **The one touch the suite cannot force is the one that keeps the suite honest.** Moving the planted
   intruder is unforced by construction: a duplicate name still refuses, so a landing that forgets it
   stays green and the NEXT amendment arrives quietly. Four landings in a row have now walked into it.
5. **A concurrent baseline is not a baseline.** The full run started before the edits and finished
   describing nothing; two targeted runs taken before the first write cost seconds and are the
   evidence §2 rests on.
