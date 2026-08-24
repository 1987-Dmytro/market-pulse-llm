# `lora-c-run r2` — STOP at rung 4: the card cannot train this line at 3 072

**Verdict: the session ran, KILLED itself on the registered rung, and the attempt is NOT SPENT.**
One pod, 3 803 s, **$0.7606 of the $4.00 cap on the pod clock**. Both base legs were bought and
kept; the smoke OOMed at 3 072 on 32 GB — after the shipped trainer's own registered fallback had
already halved `micro_batch` — and no arm was trained, so no bar exists to score.

The lead finding is the smoke, and it is an ANSWER, not a failure to work around: **RTX PRO 4500
32 GB cannot train arm A's config at `max_seq_len` 3 072, even at `micro_batch_size` 1.** The
decision the operator now owns is the card, and it is one number wide: 32 GB against the 48 GB every
prior reading of this stack was taken on.

The second finding is what the base legs measured on the way. **base v3 — v2 plus one clause asking
for a sentence of reasoning before the label — agrees with the team lead on 66 of the 98 holdout
rows inside E, against base v2's 61.** That is the control column doing exactly what it was
registered for, and it moved with no adapter anywhere.

---

## The commits

| # | commit | what |
|---|---|---|
| 1 | `e2d28b4` | team-lead files verbatim: `docs/PROMPT-lora-c-run-r2.md`, `docs/STATUS.md` with rulings (н)/(о) |
| 2 | `3083296` | step 0.5 — `knowledge/index.md` joins `check-stamped`'s whitelist on the criterion that licenses it |
| 3 | `20c8581` | step 0.75 — the false string leaves the synthetic header; the $0.72 column; nine rungs; CLOSED-BY-SIBLING |
| 4 | `928f353` | `scripts/gate_lora_c.py` — the nine rungs get an instrument |
| 5 | `455a958` | the transport, driven against the frozen packs at $0 — six gaps |
| 6 | `f39434e` | the pass-2 ceiling, bounded; rung 0 grades the card |
| 7 | `29e1804` | the spend anchor, committed before the create |
| 8 | `1aed4fa` | the cycle-2 ledger records the pre-pod reading — **the HEAD the pod cloned** |
| 9 | `422fb60` | the paid session: both base legs, the OOM, the teardown |
| 10 | `25816f7` | the two BEFORE columns, scored |

---

## §1 — the money, from the guard and the pod clock

| reading | value | what it is |
|---|---|---|
| pod clock | **3 803 s × $0.72/h = $0.7606** | create 20:29:20Z → delete 21:32:43Z. The per-leg number |
| guard, balance delta | $0.7338 | a LOWER BOUND — it prices the account, not the leg |
| guard, billing rows | $0.0602 | the walk posts hours late. Named as a debt, not quoted as the spend |
| cap | $4.00 | **$3.24 unspent** |
| cycle 2 | $9.0943 → $10.91 left of $20.00 | the outer bound |

The three readings disagree by construction and each is named for what it measures
([[a_balance_delta_is_not_a_per_leg_cost]]). `--close` is NOT run: the guard refuses it over an
unanswered walk and must, so the settled figure is a debt the next session closes.

**The gap is 8 % of the leg, not a rounding.** $0.0602 read against $0.7606 on the clock is not a
few late rows — the settled number can land anywhere between them, and the next session's anchor
must not inherit $0.7338 as though it were settled. What is safe to quote today is the pod clock:
3 803 s at the `costPerHr` the create response gave, which is the only reading that prices THIS leg
rather than the account ([[a_reading_is_not_an_identity]]).

Resources: **one pod, no serverless, no second billing resource at any moment.** Deletion proven by
three listings — `pod list -a` `[]`, `serverless list` `[]`, and `network-volume list` still holding
`qw4nwleanc / mp-srv2 / EU-RO-1 / 100 GB` as the positive control that the listing works at all.

---

## §2 — the session, rung by rung

Every line below is a row of `results/lora_c_run.json::gates`, written by
`scripts/gate_lora_c.py` at the time it fired.

| at (UTC) | rung | verdict | reading |
|---|---|---|---|
| 20:29:27 | 0 — price and card | **GO** | `costPerHr 0.72`, card `RTX PRO 4500` — both registered |
| 20:29:32 | 1 — boot gate | WAIT | 12 s of the 500 s deadline |
| 20:29:43 | 1 — boot gate | **GO** | ssh answered at **23.2 s** |
| 20:38:19 | 3 — realised rate | **GO** | base v2 at **5.323 s/call** = 0.867 × charged; projected $3.19 |
| 20:48:42 | 2 — liveness | GO | 6.8 s quiet of the 600 s deadline |
| 20:57:47 | 3 — realised rate | **GO** | base v3 at **8.922 s/call** = 1.453 × charged; projected $3.65 |
| 21:32:24 | 4 — the smoke | **KILL** | `torch.OutOfMemoryError`, 0 of 6 steps logged |
| 21:32:54 | close-pod | GO | 3 803 s, $0.7606 |

Rung 6's backstop held: `--terminate-after` was given `2026-08-25T01:29:19Z` against the computed
`01:29:20Z` — one second short, and rounding the window down is always accepted.

Rung 5, the projection, never fired: it is the rung AFTER the smoke and the smoke killed the
session first. That ordering is the contract's and it is the right one — the projection needs an
s/step and the smoke is what buys it.

---

## §3 — the smoke: what actually happened, and why it is not a config away

```
    "rows": 506,
OOM: micro_batch -> 1, grad_accum -> 16 (effective batch held)
Traceback (most recent call last):
    record["run"] = train(config, built, args.out, args.max_steps, args.resume_from)
torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 1.72 GiB. GPU 0 has a total
capacity of 31.37 GiB of which 1.66 GiB is free. Including non-PyTorch memory, this process has
29.70 GiB memory in use. Of the allocated memory 28.07 GiB is allocated by PyTorch, and 1.33 GiB
is reserved by PyTorch but unallocated.
```

Read the second line before the fifth. **The shipped trainer's OWN registered fallback fired
first** — `config/qlora.yaml` says «on OOM the trainer halves one and doubles the other», and it
did: `micro_batch 2 → 1`, `grad_accum 8 → 16`, effective batch held at 16. Then it OOMed **again**,
at micro_batch 1, in `backward()`.

So the frozen law was not edited on the pod and did not need to be: the trainer walked itself down
to the smallest batch the config permits and the card still could not hold the graph. `loss.jsonl`
was never written, `/workspace/run/smoke/` is empty, and **zero optimizer steps** ran.

**What this does and does not say.** It says this card cannot train THIS dataset at THIS ceiling. It
does not say 3 072 is wrong, or that the line is dead: 48 GB is what lora-b's readings were taken
on, and the ceiling is a property of the rows, which have not moved. The reachable remedies are the
operator's to rule on and none was taken here:

- **a 48 GB card** — A6000 reads `none` in EU-RO-1, the volume's own datacenter, in both the 08:24Z
  probe and the 20:2xZ reading taken before the create. A different datacenter means a different
  volume, which this registration did not price;
- **`gradient_checkpointing`** is already `true` — there is no headroom to buy there;
- **a lower ceiling frees NOTHING, and this is the sentence that decides what kind of finding this
  is.** `max_seq_len` is a guard threshold at encode time and not a pad width: `train_qlora.collate`
  pads each micro-batch to `max(len(row["input_ids"]) for row in rows)` — the longest row IN THAT
  BATCH — so 3 072 → 3 008 or 2 992 would still admit all 506 rows and change not one byte of
  activation memory. `config/qlora.yaml` says exactly this in its own words («raising this is a
  guard threshold and not a pad width … so the ceiling itself costs no step time and no memory»).
  Below 2 975 it stops being free and starts being a different instrument: two rows are over 2 816
  already, and an arm trained on 504 rows is not the registered one. **So the card is too small for
  these ROWS, not for this ceiling** — which is why the remedy list is about cards and not about
  numbers in the config;
- **`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`**, which the error message itself suggests,
  is 1.33 GiB of reserved-but-unallocated fragmentation against a 1.72 GiB allocation. It is the
  only cheap thing on this list and it is a **guess** until a pod measures it. Naming it is not
  recommending it.

**The VRAM test is exactly what ruling (о) bought.** It cost $0.76 including two keepable eval
legs, and it fired before a single training dollar.

---

## §4 — what the $0.76 bought and kept

Both base legs, 198 replies each, hashed on the pod and again on the Mac **before** the delete.

| leg | s/call realised | charged | ratio | parsed | refused |
|---|---|---|---|---|---|
| base v2 | 1 053.5 s / 198 = **5.32** | 6.14 | 0.87 | 198/198 | **0** |
| base v3 | 1 820.8 s / 198 = **9.20** | 6.14 | **1.50** | 198/198 | **0** |

Boot 177.3 s to the first token, against 300 s charged for the load. Both legs on one model load.

### The agreement, by `scorer.reader_comment_agreement` — CALLED, per thread

| leg | every labelled row of E | the 98 holdout rows inside E |
|---|---|---|
| base v2 | 85 / 133 = **0.639** | 61 / 98 = **0.622** |
| base v3 | 91 / 133 = **0.684** | **66 / 98 = 0.673** |

Per class, agreed / n:

| gold | base v2 | base v3 |
|---|---|---|
| `null` | 34 / 48 | 34 / 48 |
| `категория_личное` | 5 / 7 | **6 / 7** |
| `молочный_бренд` | 1 / 1 | 1 / 1 |
| `не_наш_рынок` | 35 / 66 | **41 / 66** |
| `сеть_ритейлер` | 10 / 11 | 9 / 11 |

**The control column moved, and it moved where the line targets.** base v3 is base v2 plus one
clause; the whole gain is in `не_наш_рынок` (+6) with `сеть_ритейлер` giving one back. Had an arm
run and come out ahead, this is the share of the gain that would have been credited to the adapter
and belongs to the prompt.

The 64 the bar names is **quoted here as context and is not a verdict**: base v3 takes no bar, the
denominator here is 98 and not 100, and the bar is registered per ARM. That said, the number is
worth the operator's eye — the v3 prompt alone already sits above it.

The mention cell, on E's own denominator: `не_наш_рынок` gold answered `категория_личное` in
**20 of 66** under v2 and **19 of 66** under v3. It barely moves. This is NOT the registered 18/52 —
that cell is holdout-100's and these two populations are different ([[the_fix_widened_the_denominator]]).

---

## §5 — seven transport gaps, all found at $0, none on a meter

The contract's four legs had no working producer. Every one below was found by DRIVING the shipped
chain against this line's frozen packs with a fake client, on the Mac, before the create.

| # | where | what would have happened |
|---|---|---|
| 1 | `pass1_pod_runner.check_instrument` | `prompts.PASS1` is `{v1, v2}` and v3 may not be added, so the family map is short and the pack is REFUSED — **both** legs, since one pack carries them |
| 2 | `pass1_fewshot_pod_runner.render` | a v3 item falls through to the READER's renderer → `KeyError: 'post'`, with the model loaded. The shape that killed pass1-probe at 427 billed seconds |
| 3 | `pass1_fewshot_pod_runner.main` | no `--adapter`, which both arm legs need |
| 4 | `lora_c_pass2_pack.json::instruments` | a flat `module_sha256` string where the runner reads `parser.sha256` / `module.sha256` / `module_r2.sha256` → `KeyError` |
| 5 | the same pack | no `carried` block → the resume guard raises |
| 6 | the same pack | no `serving` block → the loader raises |
| 7 | **the pass-2 ceiling** | the pack DECLARES `pass2_r2`'s 15 569 and RENDERED at `pass2`'s 12 000 |

Numbers 1–3 are closed by `scripts/pass1_v3_pod_runner.py`, a sibling that moves
`fewshot.render` and `pass1.SWAPPED["check_instrument"]` — the swap TABLE, not the module attribute,
which looks correct and changes nothing. 4–6 are closed in the pack producer, which now inherits
r2's serving block by READING it.

**Number 7 is the one with a reachability answer.** The pass-2 pack is rebuilt from an ARM's
pass-1 answers while a pod bills, and a thread's rendered size grows with the rows pass 1 marks
`OURS`. Bounded rather than hoped for — every reference thread rendered with EVERY row filtered in,
which no labelling can exceed:

| | r1's 12 000 | r2's 15 569 |
|---|---|---|
| threads over it in the worst case | **1 of 15** — `@matusi_ukr:22272` at **12 399** | **0 of 15** (3 170 headroom) |

`@matusi_ukr:22272` is a FLAGSHIP thread of bar 1
(`results/prereg_pass2_signals_r2.json::reachability.flagship_signals`), so dropping it would make
the bar unscoreable. Both sides now render at 15 569: the builder through `pass2_r2._ceiling`, and
the pod through `scripts/pass2_lora_c_pod_runner.py` — eleven lines that CALL r2's pinned runner
inside that contextmanager.

**Driven, not argued**: the arm-A rebuild runs end to end in `tests/test_pass1_v3_pod_runner.py` on
a synthesised v3 out-file, through the builder and the runner, 15 threads at the bound.

---

## §6 — step 0.75, the marker fix

Ruling (о): the FALSE production string leaves the synthetic header.

| line | in the 160 | in the 506 | |
|---|---|---|---|
| `(this post has no text of its own — it is an image or a video)` | **0** (was 160) | 0 | `prompts.NO_POST_TEXT` — gone |
| `(synthetic training row — this thread has no post)` | **160** | **0** | the registered constant |
| `<thread channel="synthetic" post_id="…">` ×4 | 40 each | 0 | unchanged |

The 506 prefix re-renders BYTE-IDENTICAL. The encode census re-taken through the real tokenizer at
the pinned revision: **666 encoded, 0 refused**, min 1 445 / median 1 601 / max 2 975 against 3 072,
headroom **97**, and the widest row is still the REAL `@tarilka_malyuka:746#83`.

**The confound REMAINS and is registered, not repaired.** All 160 synthetic rows are still marked by
at least one tell, and those 160 carry all 32 `молочный_бренд` targets. The fix moves the marker off
a sentence production emits and onto one it never does; the census that would have separated
«synthetic did not help» from «the adapter learned the marker» was built, priced and driven at $0 —
**40 requests, 20 pairs differing in the header alone** — and never ran, because rung 4 fired first.

---

## §7 — the money, re-derived and what the session moved

Registered before the create, at the charged rates:

| price | fixed | left for 144 steps | break-even s/step | with the census | at the pass-2 bound |
|---|---|---|---|---|---|
| $0.72 — **the ruled card** | 8 885.88 s = $1.7772 | 11 114.1 s | **77.18** | 75.48 | **70.09** |
| $0.74 | $1.8265 | 10 573.6 s | 73.43 | 71.72 | 66.33 |
| $0.80 — the create ceiling | $1.9746 | 9 114.1 s | 63.29 | **61.59** | 56.20 |

Readings this repo holds: 61.047 (registered by lora-b) and 68.442 (measured on lora-b arm A). At
the ruled card both fit under every column, including the worst case.

**What the session measured moves this.** v3 runs at **1.50×** the charged rate, and three of the
four eval legs plus the census are v3. At the measured rates the break-even after the base legs was
**≈75.7 s/step** (≈70.3 at the pass-2 bound) — still above both readings, so the plan was
arithmetically alive when the smoke killed it for a different reason. **The next contract's money
block must carry 9.20 s/call for v3, not 6.14.**

Two bounds registered before the create, both of which can only close a session early:

- **the marker census is not inside the fixed part.** 8 885.88 s decomposes exactly with no room for
  40 calls, so 245.6 s is charged BESIDE it. At $0.80 that leaves **0.54 s/step** of margin over
  lora-b's registered 61.047 — a real margin and a thin one ([[a_new_leg_joins_the_gates_denominator]]);
- **the pass-2 thread count is a READING**, not the charged 11. The reachable maximum is 15, worth
  776 s across two legs.

---

## §8 — the numeric session audit

| | |
|---|---|
| pods created | 1 (`ob1svfs3y23teh`) · deleted 1 · serverless 0 |
| pod lifetime | 3 803 s · $0.7606 at $0.72/h |
| calls bought | **396** — base v2 198, base v3 198 |
| calls refused by the parser | **0** |
| optimizer steps | **0** |
| adapters produced | **0** |
| eval replies by an adapter | **0** — the attempt is NOT SPENT |
| bars scored | **0** — the registered three are per arm |
| artifacts pulled before the delete | 4 files, hashes equal on both machines |
| suite | **3 771 passed / 2 skipped**, `make check-stamped` «reading HOLDS» at `f39434e` |

Artifact shas (first 16):

| file | sha256 |
|---|---|
| `results/prereg_lora_c.json` | `4d5a8f1d34765b4a` |
| `results/pass1_sft_v3_arm_b.jsonl` | `311571555169300c` |
| `results/lora_c_arm_b.json` | `a95475af501e0305` |
| `results/lora_c_encode_census_arm_b.json` | `e428632c20c6716b` |
| `results/lora_c_pass2_pack.json` | `16cf023608d4ce04` |
| `results/lora_c_marker_census_pack.json` | `c632d8506c3e90c7` |
| `results/lora_c_base_v2.jsonl` | `f01506d94a456623` |
| `results/lora_c_base_v3.jsonl` | `fdfa36d2ee39a0f9` |
| `results/lora_c_bases_verdict.json` | `fe63bc09ee214b52` |
| `results/lora_c_run.json` | `cd7e639cdd338838` |
| `scripts/gate_lora_c.py` | `e59a3e68af67159a` |
| `scripts/pass1_v3_pod_runner.py` | `060643dab086fb11` |
| `scripts/pass2_lora_c_pod_runner.py` | `7b0d3eb3c4113394` |
| `scripts/build_lora_c_marker_census.py` | `a947947e6a295284` |
| `scripts/score_lora_c_bases.py` | `717a7bf7651e5c84` |

---

## Deviations — from Dv803, enum v2

| Dv | cause | what |
|---|---|---|
| **Dv803** | `[cause: contract-gap]` | **Ruling (о) names a card with no price column.** The derivation held $0.80 and $0.74 only, and every projection rung divides by a price. Registered $0.72 before the create: budget 20 000 s, fixed $1.7772, break-even 77.18 s/step, both s/step readings under it. |
| **Dv804** | `[cause: contract-gap]` | **The marker census cannot be «inside the fixed part».** Amendment 4 prices it there and amendment 1 pins that part at 8 885.88 s, which decomposes exactly. Charged beside it with what it costs per price; the finding is the $0.80 knife-edge, 0.54 s/step over lora-b's registered rate. |
| **Dv805** | `[cause: verify-gap]` | **`header_tell` emitted a different file on every run.** Its table is filled from a `set` and every prompt paragraph shares the sort cell (506, −160). Found by adding arm B's outputs to the byte-for-byte producer test — which is also the finding that the file the pod trains arm B on was written by a producer no test drove. |
| **Dv806** | `[cause: verify-gap]` | **Six transport gaps, 1–6 of §5.** Four registered legs with no working producer. Found by driving the shipped chain against the frozen packs with a fake client; every one would have fired on a billed pod, three of them with the model already loaded. |
| **Dv807** | `[cause: spec-gap]` | **The pass-2 pack declared one ceiling and rendered at another** (§5 #7). Reachable: one reference thread crosses 12 000 in the worst case, and it is a flagship thread of bar 1. Both sides moved to 15 569; the bound is registered in the pack. |
| **Dv808** | `[cause: process]` | **Rung 3's first version would have KILLED every session at the first base leg.** It charged the remaining 150 steps at the smoke's 181.5 s/step kill-clock ceiling — 27 225 s, more than the cap buys on its own. Rewritten as a BOUND at the cheapest s/step this stack has registered. Found by the test, not on the pod. |
| **Dv809** | `[cause: contract-gap]` | **Rung 0 graded the price and only recorded the card.** Ruling (о) authorises two cards and makes anything else a STOP, and a third card at $0.72 would have passed — `RTX PRO 4000` is 24 GB at exactly that price. Both `gpuId` strings are the platform's own, from the stock probe. |
| **Dv810** | `[cause: model]` | **The charged 6.14 s/call is a v1/v2 rate and v3 runs at 1.50× it.** 9.20 s/call measured against 5.32 for v2 on the same pod, same load, same card. The contract says «v3 is WIDER» in prose and charges 6.14 anyway. Three of four eval legs are v3. |
| **Dv811** | `[cause: tooling]` | **The card cannot train this line at 3 072 even at `micro_batch` 1.** The registered rung fired and the session STOPped. This is the deviation the contract was written to discover, and it discovered it for $0.76. |

Tally, by the pattern `grep -c "\[cause: <t>\]"` over this block:
**contract-gap 3 · verify-gap 2 · spec-gap 1 · process 1 · model 1 · tooling 1 — nine.**

---

## What the operator is being asked

1. **The card.** 32 GB is not enough for this line at 3 072, at any batch the frozen config permits.
   A6000 48 GB reads `none` in the volume's datacenter and has for two readings a day apart. The
   choices are a different datacenter (a different volume, unpriced), a wait, a bigger card
   (`RTX PRO 6000` 96 GB at $2.09/h is in stock — it re-prices the whole plan), or the
   `expandable_segments` guess.
2. **The v3 rate.** 9.20 s/call, not 6.14. The next money block should carry it, and the fixed part
   grows by roughly 3 × 198 × 3.06 ≈ 1 800 s.
3. **base v3's 66/98.** Report-only and above the number the bar names. Whether the line still needs
   an adapter to clear its own bar is now a live question and it is the team lead's.

## Open

1. `--close` on the guard is a DEBT: the billing walk posts hours late and the settled figure is
   $0.0602 read against $0.7606 on the clock.
2. The marker census is built, priced and driven — and unspent. It is the first thing arm B's eval
   owes.
3. `bars.report_only.pass_2_tables` still says «per leg»; ruling (н) says the legs that RUN are the
   two arms. Reconciled inside the money block and nowhere else.
4. The two holdout rows of `@VARUS_channel:10367` still cannot be rendered — the reachable maximum
   is 98 of 100 and every rate above is on that denominator.
5. `results/prereg_lora_c.json` is FROZEN by this session's create and its attempt is intact.

## Process signals

1. **The rung that pays for itself is the one that fires while money is moving.** Rung 3 graded both
   base legs on the rate they were realising and said GO twice — and the v3 reading it produced,
   1.50× the charge, is the number the next contract needs. lora-b's first spend decision fired at
   its arm-A milestone; this one fired 8 minutes in.
2. **Driving the shipped chain against a frozen pack costs nothing and found seven gaps.** Four of
   them would have raised on a billed pod with a 31 GB model in memory. A pack built at $0 by a
   previous contract is an INPUT to shipped code, and nobody had ever run it through that code.
3. **My own new rung was wrong in the direction that looks safe.** Charging the remaining steps at
   the smoke's kill ceiling is conservative, and conservative enough to refuse every possible
   session. The test caught it; the pod would have caught it eight minutes in, for real money.
4. **A worst-case stub is a measuring instrument.** Labelling every reference row `сеть_ритейлер` is
   not a realistic arm — it is the BOUND, and it is what turned «the ceiling might be a problem»
   into «one named thread, 12 399 characters, and it carries a bar case».
5. **The KILL is the deliverable.** $0.76 bought a VRAM answer, two keepable base columns, a
   card-specific rate table and nine deviations, and left the attempt unspent. A session that had
   skipped the smoke would have discovered the same OOM after paying for arm A's first steps.

**STOP for team-lead acceptance.**

Related: `docs/reports/lora-c-run.md` (the $0 STOP that preceded this) ·
`docs/reports/lora-c-armb.md` (arm B's dataset, Dv793–802) ·
`knowledge/decisions/lora-c-the-card-cannot-train-at-3072.md`
