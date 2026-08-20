# pass1-fewshot — D0 delivered in full; D1 closed at rung 2, the attempt NOT spent

**Verdict.** Everything `docs/PROMPT-pass1-fewshot.md` asks for at $0 is built, tested, driven and
committed: the holdout, the v2 prompt, the neighbours, both packs, the gate with its blocking
liveness loop, the pre-registration with H6 as a step-1 refusal, and D2's scorer. The paid session
did **not** happen. Two RTX 4090s were created in EU-RO-1 at the registered `costPerHr` **0.74**;
both were KILLed on **rung 2, the 180 s ssh dead-man**, and the recovery clause's ONE re-creation is
used. **No generation of any kind ran. The ONE attempt is NOT spent** — no gold row was answered, no
dev row was answered, and the question returns to the operator exactly as `attempt` registers it.

**Billed: 573.0 s = $0.117783** of the $1.50 cap, on the clock's arithmetic; the guard's balance
delta reads **$0.0906** and is a lower bound that is still settling (Dv504 class). Cycle 2 stands at
**$5.8992 of $20.00, remaining $14.1008**.

## Read back first, one line each (the contract's own list)

- **The dev gate's two inequalities.** `our_v2 − our_base ≥ 10` over the 49 категория_личное /
  молочный_бренд rows AND `agree_v2 − agree_base ≥ −5` over all 200, paired on the same rows. Both
  or no shot.
- **When the attempt is SPENT.** At the first GOLD-row reply generated. Not at create, not at a dev
  reply, not at the dev gate. It was never reached.
- **The liveness rung and who holds it.** Rung 5, 600 s with no new answered row and no new pod-log
  line, measured from the LAST EVENT; held by `scripts/gate_pass1_fewshot.py --watch`, a blocking
  loop the executor does not leave — a script now, not a habit.
- **The hard stop vs the cap.** 6 300 s = $1.40 at the $0.80/h ceiling, PLATFORM-held through each
  pod's `--terminate-after`; it sits UNDER the $1.50 cap it defends.
- **Why one example per class.** Nearest-k over the 650 labels is 52 % `не_наш_рынок` — the marginal
  the LoRA of line B learned instead of the decision. Balance by construction is the defence.
- **The four contamination lists.** Empty in both packs, because
  `build_pass1_label_pack.py::excluded_threads` removed the seven probe threads from the labelling
  population WHOLE, so the neighbour pool is disjoint from both exams.
- **The base is never re-run on the fourteen.** Its column comes from the sealed
  `results/pass1_probe_b_verdict.json`; arm A's from `results/lora_b_verdict.json`.

## 0 — baselines, at step 0, from the instrument

```
## Baselines — instrument output, 2026-08-20T19:25:01+00:00

- head: 317762ecea6d on main
- porcelain:  M knowledge/daily_logs/2026-08-20.md · M knowledge/hot.md · M knowledge/index.md
- census: brain-census: 9.9Ktok boot tax
- suite: 3169 passed / 2 skipped — whole suite, stamped 2026-08-20T19:20:14+00:00 at 46d58c620298
- boot files: … = 158 lines / 19 887 UTF-16 units
- preflight: 1499 pinned paths · 2533 pins · 107 records — 1468 match every pin, 31 carry an older pin
```

The three dirty vault files are the SessionStart hook's own tail and are the last commit of this
session, not this contract's work.

## D0.1 — the holdout, registered before anyone trains again

`results/pass1_holdout_100.json`, sha `5a62c957…`, producer `scripts/write_pass1_holdout.py`.

```
wrote results/pass1_holdout_100.json  100 units  seed 20260820
  population 650 labels: {'молочный_бренд': 2, 'сеть_ритейлер': 48, 'категория_личное': 47,
                          'не_наш_рынок': 340, 'null': 213}
  allocation {'молочный_бренд': 1, 'сеть_ритейлер': 7, 'категория_личное': 7,
              'не_наш_рынок': 52, 'null': 33}   — registered {…} identical
  sealed arm a: 78 of the 100 holdout rows are in results/pass1_sft_arm_a.jsonl (500 rows)
  sealed arm b: 100 of the 100 holdout rows are in results/pass1_sft_arm_b.jsonl (650 rows)
  contamination: gold ids 0 · gold threads 0 · eval ids 0 · eval threads 0
```

**The draw is largest remainder with a FLOOR OF ONE per non-empty class, and the floor is
load-bearing.** Plain largest remainder does not produce the contract's registered 52:33:7:7:1 — the
floors are 52, 32, 7, 7, 0 and the two largest remainders are `null` (.769) and `сеть_ритейлер`
(.385), which gives **52:33:8:7:0**: a holdout with **no `молочный_бренд` row at all**, the class
with two rows in 650 deleted by rounding. `tests/test_pass1_holdout.py` computes that alternative,
so the rule is a rule and not a coincidence (**Dv587**).

**The refusal is scoped, and the scope is declared.** The holdout is drawn from the same 650 arm B
is made of, so «a holdout id in the input → refuse» and «the current arms' inputs minus nothing →
build» cannot both hold unscoped. `scripts/build_pass1_sft.py::assert_no_holdout` exempts exactly
the two SEALED line-B arms and keys the exemption on the **shas `results/pass1_sft.json` pins**, not
on their names: the day arm A is composed differently the sha moves and the exemption is gone
(**Dv588**). Both directions are tested, with the positive control that arm B really does contain
all 100 — an empty intersection would make the refusal unreachable and the test vacuous.

## D0.2 — `pass1_comment_gm4_v2`

v1's bytes + one codebook clause + the examples slot, a strict PREFIX extension asserted in both
directions. **v1's own sha `5a4a3cb6…` is UNCHANGED**, which is what keeps probe-b's evidence and
this line's paired dev legs comparable; v2 hashes `f5f6a5af…`. 2 521 → 3 455 characters.

The renderer grew `examples=`. A v1 request carrying a block and a v2 request without one are both
refused by name — a request that half-applies the revision is a third instrument nobody registered.
The block renders between `<entities>` and `<comment>`:

```
<examples>
Labelled examples (subject_type only):
"<text>" → категория_личное
… one row per reading, and `null` written as itself
</examples>
```

The contract writes that block as one compressed span, `Labelled examples (subject_type only):
"<text>" → <label>`, which is a row template with its block name attached. It is rendered as that
name once and one row per example: the name is plural and names a BLOCK, and five repetitions of a
plural label is not a thing a codebook says (**Dv596**).

**The sweep this caused, and it is the largest single consequence of D0.** Adding a second text
moved `src/market_pulse/prompts.py`, and six sealed records pin that module. The contract says those
pins «are already «moved since» and are NOT re-pinned» — true of the READER records and **not** of
the pass-1 ones, whose pins were live until tonight (**Dv589**). Per the ruling they stay unmoved
and the tests that asserted byte-identical rebuilds are narrowed to an enumerated diff DERIVED from
which paths carry the live sha (`tests/moved_pins.py`), with the registered `prompt_sha256` map
asserted unmoved beside it. Two real defects surfaced and are fixed rather than papered over:

- `pass1_pod_runner.check_instrument` compared the served pass-1 family **whole**, so a second
  registered text refused every older pack on a perfectly correct pod. The reader's own handshake
  had been narrowed to a subset check one family earlier, for this exact reason, and the same
  narrowing is applied here (**Dv598**).
- `write_pass1_prereg_b`'s self-check refused any move of pass1-probe's frozen record. It now
  forgives exactly the paths carrying `prompts.py`'s live sha — derived, never listed — and refuses
  outright if the registered TEXT moves.

**Consequence, asserted rather than discovered:** the sealed `results/pass1_probe_pack.json` is no
longer servable on this checkout, because its parser pin is the module that moved. That is the
correct outcome — the base is never re-run on the fourteen, and v1's TEXT is untouched, which is
what keeps the old evidence comparable — and `tests/test_pass1_transport.py` now says so (**Dv597**).

## D0.3 / D0.4 — the neighbours and the two packs

```
wrote results/pass1_dev_pack.json  sha256 cbdb18c4c0e9dad0…
wrote results/pass1_probe_b_pack_v2.json  sha256 2c4b8d7796c1c88a…
  dev: 200 rows (49 «our») × 2 legs = 400 items · seed 20260820
       distribution {'молочный_бренд': 2, 'сеть_ритейлер': 12, 'категория_личное': 47,
                     'не_наш_рынок': 85, 'null': 54}
       top-up {'null': 54, 'не_наш_рынок': 85, 'сеть_ритейлер': 12} of {213, 340, 48}
       paired: same rows True · same context True
       holdout overlap 74 of 200 — declared
  shot: 64 units, order unchanged from results/pass1_probe_b_pack.json
  dev length: widest 7939 chars (@matusi_ukr:22327#580336) · median 4030 · headroom 4061 of 12000
  dev contamination: gold ids 0 · gold threads 0 · eval ids 0 · eval threads 0 · own-thread 0
  dev balance: {'молочный_бренд': 200, 'сеть_ритейлер': 200, 'категория_личное': 200,
                'не_наш_рынок': 200, 'null': 200}
  shot length: widest 7276 chars (@matusi_ukr:22272#579429) · median 4684 · headroom 4724 of 12000
  shot contamination: 0 · 0 · 0 · 0 · own-thread 0
  shot balance: {each reading: 64}
```

The ceiling was **measured before either pack was written**, not rescued at build time: the widest
v2 request is 7 939 characters of a 12 000 ceiling that REFUSES rather than truncates, leaving
4 061. Balance is exact by construction — 200 of each reading across the dev leg, 64 across the shot
— which is the whole defence against the prior line B's adapter learned.

`msg_id` is unique across the 200 dev rows and the 64 shot units, and that is now asserted:
`scorer.reader_comment_agreement` keys its answers on `msg_id` alone, so a collision would be
last-wins and BOTH rows would read `absent`.

The two dev legs run in **one invocation with one model load** — the contract's «base-dev → v2-dev»
reads as two launches, and two launches pay the ~350 s boot twice out of a 5 326 s budget. Order is
preserved (base first, v2 second) and each leg answers into its OWN out-file (**Dv599**).

## D0.5 — the gate, and the loop the executor does not leave

`scripts/gate_pass1_fewshot.py`, 19 tests, every flag driven at $0 on a fake transport.
`scripts/runbook_pass1_fewshot.md` is the order.

The contract asks for `--watch` to KILL on idleness. As specified it would only ever exit on KILL,
so it could never hand control back for the dev gate; it exits GO when every registered unit is
answered (**Dv593**). Three further tightenings, each strictly stronger and each with its own test:

- **An event is a RISE.** `pull` is scp and scp fails; a failed copy leaves a local file SHORTER.
  Refreshing the deadline on any CHANGE would make a dead pod behind a flapping link immortal —
  N → 0 → N → 0 is four «events» and the deadline never expires — which is precisely the state this
  rung exists for. The fingerprint is a high-water mark
  (`test_a_FLAPPING_copy_does_not_keep_a_dead_pod_alive`) (**Dv594**).
- **Rung 4 runs on EVERY poll**, not every 20 answered calls. The registered interval is the floor:
  the projection is a pure computation over local files and costs nothing, while a slowdown starting
  just after a checkpoint would run unexamined for twenty more calls — and at a degraded rate twenty
  calls can outlast the hard stop. Rung 6 is checked directly beside it (**Dv595**).
- **Rung 3 is armed by the loop itself**, once per pod, so the boot ceiling needs no hand-polling;
  the shot's watch does not re-arm a create-anchored ceiling that would kill a healthy pod.

Whatever ends the loop — an exception, a broken pipe, Ctrl-C — records a gate and prints the pod id
with its delete command, and then RE-RAISES.

`BACKSTOP_TOLERANCE_SECONDS = 60.0` is a threshold the gate acts on that lives in the script and not
in the registration. It is lora-b's precedent and it only ever bounds overshoot — a window rounded
DOWN is always safe — but it is named here rather than left implicit (**Dv603**).

## D0.6 — the registration, and H6 as a refusal

`results/prereg_pass1_fewshot.json`, sha `bd731e53…`.

```
  H6: 16 rows, every registered number re-derives
  seconds: boot 450.0 + base 1032.4 + v2 1548.6 + shot 495.552 + overhead 1800.0
           = 5326.552 = 1.4796 h
  worst case $1.1837 at $0.8/h ($0.7842 at $0.53/h) against a cap of $1.50
  hard stop 6300 s = 1.75 h = $1.40 < cap · session ceiling 1.875 h
  dev gate: our delta ≥ 10 of 49 AND agreement delta ≥ -5 over 200
  kill clock: 8 rungs, liveness is rung 5 and the script holds it
```

Two of the contract's figures re-derive DIFFERENTLY from the way its parentheses spell them, and
both are recorded as such:

- **the boot ceiling.** «450 (worst 293 × 1.5)» quotes the worst boot as it stood before lora-b
  measured **353 s** on the same card and the same volume. 450 is KEPT — it is rung 3's own
  threshold and it still sits above the true worst — and its derivation is now «≥ max(every boot
  this stack has measured), ×1.2748». H6 checks the DIRECTION of that margin, which is what a
  ceiling has instead of a value (**Dv590**).
- **the printed seconds.** 64 × 7.743 = 495.552 against a printed 495.6, and 5 326.552 against
  5 326.6. The exact values are registered and the printed ones are asserted to be their roundings
  (**Dv591**).

**The dev gate's reachability is registered BEFORE the pod** (**Dv592**): `our_v2 − our_base ≥ 10`
over 49 rows is unreachable whenever the base already answers more than **39** of them, and the
base's dev number is measured on the pod with a meter running. That branch is a **STOP** with the
attempt not spent, not a RED, and `gate_pass1_fewshot.py` reports the two apart.

The memory constraint is re-derived too: this line trains nothing, so lora-b's 48 GB does not apply
— probe-b served this same base on a 24 GB 4090 — which made rung 1 a price gate against a much
wider market than lora-b faced. That is why a 4090 was obtainable tonight at all.

## D1 — the paid session, and why it closed at rung 2

```
pod 7spsy61lpjumrz  created 2026-08-20T20:56:55Z  deleted 21:02:36Z  341.0 s  $0.070094  4090 $0.74/h
pod juupgp6y77jvuz  created 2026-08-20T21:03:41Z  deleted 21:07:33Z  232.0 s  $0.047689  4090 $0.74/h

20:57:01Z pod1 price  rung 1  GO    elapsed   6.5
20:57:09Z pod1 gate0  rung 2  WAIT  elapsed  15.0
21:01:17Z pod1 gate0  rung 2  KILL  elapsed 262.5
21:02:44Z pod1 close          GO
21:03:46Z pod2 price  rung 1  GO    elapsed   5.5
21:07:32Z pod2 gate0  rung 2  KILL  elapsed 231.9
21:07:42Z pod2 close          GO
```

**Pod 1 was killed by my own instrument, not by the pod (Dv601).** The poll loop grepped `"host"` —
a key `runpodctl ssh info` never emits; it answers `{"error": "pod not ready"}` and then an object
carrying `"ip"` and `"port"` — so it spun blind for 240 s, and the `--gate0` I ran after it asserted
`ssh_ok=False` at 262.5 s of create-elapsed. The endpoint WAS answering by then; what the gate
recorded is the reading it was handed. **The KILL stands.** A rung whose deadline cannot be
demonstrated has not been passed, and re-running a gate with a different flag after seeing its
verdict is the one thing this whole architecture exists to prevent. Deleted, proven by three
listings with the volume as the positive control, closed at 341 s.

**Pod 2 was killed by the pod, on a correct reading (Dv602).** The recovery clause's arithmetic was
computed and pasted first — reading $0.0701 + worst case ahead $1.0949 = **$1.1650 ≤ $1.50**, and
341 + 5 326.6 = **5 667.6 s ≤ 6 300** — and the ONE re-creation was made. This time the poll was
bounded at 34 × 5 s = 170 s and looked for `"port"`. It never appeared: `runpodctl ssh info` still
answered `pod not ready` at **231.9 s** of create-elapsed, against the registered **180 s**.

So rung 2's ceiling, inherited from pass1-probe and passed by probe-b on 2026-08-18, **did not hold
on either 4090 in EU-RO-1 tonight**. Two pods, two readings, one of them clean. The recovery clause
is used, no third pod may be created, and the session closes exactly where the registration says a
pre-generation KILL closes it: **the attempt is NOT spent, and the question returns to the operator.**

## D2 — the scorer, driven at $0 against the real (empty) run state

`scripts/score_pass1_fewshot.py --outdir <scratch>`, so nothing is published over a session that
measured nothing:

```
VERDICT  NOT EVALUATED
DEV GATE  not scored — ['pass1_dev_base.jsonl', 'pass1_dev_v2.jsonl'] are not on this machine …
GOLD 14   results/pass1_fewshot_shot.jsonl does not exist — no gold row was answered. The ONE
          attempt is NOT spent and the question returns to the team lead. This is a STATE and is
          never scored 0 of 14
PAIRED    {'base': 9, 'arm_a': 9}
CENSUS-50 base {'None': 25, 'категория_личное': 11, 'молочный_бренд': 2, 'не_наш_рынок': 8,
                'сеть_ритейлер': 4}
```

No `results/pass1_fewshot_verdict.json` is committed: the gate record
`results/pass1_fewshot_run.json` is the artefact of what happened, and a verdict file asserting that
nothing was measured would be a second, emptier copy of it.

## Verify — outputs, not summaries

```
$ make check
3239 passed, 2 skipped in 501.74s          # 3169/2 at step 0; +70 tests
$ ruff format --check . && ruff check .
390 files already formatted · All checks passed!

$ make preflight ARGS='PROMPTS pass1_comment_gm4_v1 build_pass1_sft.py'
  src/market_pulse/prompts.py       live b70e2114b03a76dc…  DIFFERS   # the ruled «moved since»
  scripts/build_pass1_sft.py        live c1e9bf5ecee005a0…  DIFFERS   # the holdout refusal
  scripts/write_pass1_prereg_b.py   live 18efe14570d11d07…  DIFFERS   # the narrowed self-check
  16 of 19 pinned paths match every digest on them

$ shasum -a 256 …
5a62c957…  results/pass1_holdout_100.json
cbdb18c4…  results/pass1_dev_pack.json
2c4b8d77…  results/pass1_probe_b_pack_v2.json
bd731e53…  results/prereg_pass1_fewshot.json
7308ed0c…  results/pass1_fewshot_run.json

$ runpodctl pod list -a && runpodctl serverless list && runpodctl network-volume list
[]
[]
[{"dataCenterId": "EU-RO-1", "id": "qw4nwleanc", "name": "mp-srv2", "size": 100}]   # the control

$ PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass1-fewshot --step-cap 1.50
CYCLE 2 SPENT     $5.8992 of $20.00
REMAINING         $14.1008
PASS1-FEWSHOT SPENT      $0.0906 of $1.50   (balance delta; the billing walk still reads $0.0097)
```

Each intermediate commit was checked out into a scratch worktree and the whole suite run on it.
`5a47ca6` returns 3 183 passed / 2 failed, and both failures reproduce at the pre-contract HEAD
`317762e` in the same worktree — `test_baselines` and `test_collect_5c1` read repo-root paths and
git state that a detached worktree does not have. They are worktree artefacts, not commits.

## Deviations (enum v2)

| # | What | Tag |
|---|---|---|
| **Dv587** | The contract registers the holdout as 340:213:48:47:2 → **52:33:7:7:1**, and plain largest remainder does not produce it — floors 52/32/7/7/0, top remainders `null` .769 and `сеть_ритейлер` .385, giving **52:33:8:7:0** with **no `молочный_бренд` row**. Implemented as largest remainder with a FLOOR OF ONE per non-empty class, which reproduces the registered tuple exactly; the test computes the alternative so the floor is provably load-bearing. | `[cause: contract-gap]` `[[an-absolute-bar-needs-a-reachability-state]]` |
| **Dv588** | «A holdout id in the input → refusal» and «the current arms' inputs minus nothing → build» cannot both hold: the holdout is drawn from the same 650 arm B IS. Scoped — the two SEALED arms are exempt, keyed on the shas `results/pass1_sft.json` pins rather than on their names, so a re-composed arm loses the exemption with its bytes. | `[cause: contract-gap]` `[[the-guard-hashes-the-half-that-cannot-move]]` |
| **Dv589** | «Old records' pins of prompts.py are already «moved since»» is true of the READER records and false of the pass-1 ones — those pins were live until tonight. Six sealed records moved for the first time and two producer-level self-checks had to be narrowed; the narrowing is derived from the live sha, never listed. | `[cause: contract-gap]` `[[the-identity-field-stops-covering-the-change]]` |
| **Dv590** | «boot 450 (worst 293 × 1.5)» quotes a worst lora-b has since beaten: **353 s**, same card, same volume. The CEILING is kept (it is rung 3's threshold and still above the true worst) and its derivation is re-registered as «≥ max(measured), ×1.2748»; H6 checks the direction of that margin. | `[cause: verify-gap]` `[[a-named-revision-is-not-a-passing-one]]` |
| **Dv591** | 64 × 7.743 = **495.552** and the contract prints 495.6; the total is **5 326.552** against 5 326.6. The exact values are registered, the printed ones asserted as their roundings — so the money block carries the arithmetic and the contract carries the reading. | `[cause: verify-gap]` `[[rederive-doc-numbers]]` |
| **Dv592** | The dev gate had no reachability state. `our_v2 ≤ 49`, so the +10 delta is unreachable whenever `our_base > 39` — and the base's dev number is measured on a billed pod. Registered before the pod as a **STOP** distinct from a RED, with the attempt not spent. | `[cause: spec-gap]` `[[an-absolute-bar-needs-a-reachability-state]]` |
| **Dv593** | `--watch` as specified exits only on KILL, so it could never hand control back for the dev gate. Given a completion condition: GO when every registered unit of the watched packs is answered. | `[cause: contract-gap]` `[[a-checker-whose-failure-is-silence]]` |
| **Dv594** | The idle fingerprint had to be a HIGH-WATER mark. `pull` is scp; a failed copy leaves a local file shorter, and refreshing on any CHANGE makes a dead pod behind a flapping link immortal — the exact state rung 5 exists for. Found in review before the pod, and it now has its own test. | `[cause: verify-gap]` `[[guard-selftest-negative-control]]` |
| **Dv595** | Rung 4 runs on EVERY poll, not every 20 answered calls; the registered interval is the floor. The projection is local and free, while a slowdown starting just after a checkpoint would run unexamined for twenty calls — and at a degraded rate twenty calls can outlast the hard stop. Rung 6 is checked beside it. | `[cause: contract-gap]` `[[a-negative-pre-generation-budget-is-a-forecast]]` |
| **Dv596** | The examples block is given as one compressed span, `Labelled examples (subject_type only): "<text>" → <label>`. Rendered as the block name once plus one row per example: the name is plural and names a block. Registered here rather than read silently; the whole rendering is pinned per item by `rendering_sha256` either way. | `[cause: contract-gap]` `[[spell-the-rows-out-with-their-source]]` |
| **Dv597** | «`instruments`/`serving` copied from the sealed pack» cannot be verbatim: `parser.sha256` is the module that moved, and the pod's handshake compares the WHOLE served family, so the map must cover v1 and v2. Both recomputations are recorded with the reason. Consequence, asserted: the sealed `pass1_probe_pack.json` is no longer servable on this checkout — correct, since the base is never re-run. | `[cause: contract-gap]` `[[the-record-says-subset-the-code-says-equality]]` |
| **Dv598** | `pass1_pod_runner.check_instrument` compared the served pass-1 family whole and so refused every older pack the moment a second text existed — verbatim the defect the READER handshake had been narrowed for one family earlier, with the fix and its reasons already written in that docstring. | `[cause: verify-gap]` `[[the-record-says-subset-the-code-says-equality]]` |
| **Dv599** | «base-dev → v2-dev» reads as two launches; run as ONE invocation over a two-leg pack, one model load, order preserved, one out-file per leg. Two launches would pay the ~350 s boot twice out of a 5 326 s budget. | `[cause: process]` `[[the-transport-fixes-the-job-shape]]` |
| **Dv600** | D0.1 and D0.2 are committed together. The refusal READS the holdout record and the holdout record PINS `prompts.py`, so every split ordering leaves one red commit — and a red commit is worse than a merged one. | `[cause: process]` `[[a-test-that-reads-a-shipped-artifact]]` |
| **Dv601** | **The poller cost a pod.** It grepped `"host"`, a key `runpodctl ssh info` never emits, spun blind for 240 s, and the `--gate0` after it recorded a rung-2 KILL nobody could prove either way. The endpoint was answering; what the gate recorded is the reading it was GIVEN. The KILL stands — a deadline that cannot be demonstrated has not been passed — and the runbook now polls on `"port"` with the loop bounded at 170 s, inside the rung. 341 s, $0.0701. | `[cause: process]` `[[a-checker-whose-failure-is-silence]]` |
| **Dv602** | **Rung 2's 180 s ceiling does not hold on these pods.** Pod 2, polled correctly and bounded, was still `pod not ready` at **231.9 s** of create-elapsed. probe-b passed the same rung on the same card in the same datacenter on 18.08, so the constant is a reading of that night and not a property of the stack. The session closes here by the registration's letter, attempt NOT spent. | `[cause: env]` `[[projected-rate-versus-measured-rate]]` |
| **Dv603** | `BACKSTOP_TOLERANCE_SECONDS = 60.0` is a threshold the gate acts on that lives outside the registration (lora-b precedent). It bounds overshoot only — a window rounded down shortens itself — but a number the gate acts on belongs in the record. | `[cause: contract-gap]` `[[preregistration-is-a-file-not-a-constant]]` |
| **Dv604** | The guard anchor was taken **~4 h** before the first `pod create`, so the volume drip in that window lands on this step: of the step's $0.0906 balance delta, **$0.0097** is network volume the billing walk attributes to nothing this contract ran. The gate's own clock — 573.0 s × $0.74/h = **$0.117783** — is the per-leg figure; the delta is the account's. | `[cause: env]` `[[a-balance-delta-is-not-a-per-leg-cost]]` |

**Tally.** contract-health (contract-gap + spec-gap + verify-gap) **13** · paid (process + env) **5**.
Thirteen contract-health entries on a contract that never generated a token is the shape of a D0
that was reviewed adversarially before the money: eleven of them were found and closed at $0, and
the two that were not (Dv601, Dv602) are the two that cost the session.

## Process signals (five lines)

1. **The review before the pod paid for itself and the review of my own tooling did not.** Six
   findings landed at $0 — the holdout tuple, the SFT scope, the boot derivation, the reachability
   branch, the flapping fingerprint, the msg_id key — and the one thing nobody reviewed was the
   four-line shell loop that polls for ssh. That loop cost a pod.
2. **A gate records the reading it is given, and that is the whole danger of polling with it.**
   `--gate0` with no `--ssh-ok` is an assertion, not a question. The runbook now says so in the
   place a person reads at 21:00.
3. **The recovery clause worked exactly as registered** — arithmetic first, pasted, then one
   re-creation — and it is the reason the second reading exists at all. It is now used.
4. **A constant measured once is a reading of that night.** 180 s passed on 18.08 and failed twice
   on 20.08, on the same card in the same datacenter. The same is already true of the boot on this
   stack (146.8 … 353 s), and rung 2 has now joined it.
5. **Nothing about the question moved.** No prompt was iterated, no bar was re-read, no pod was
   left unwatched, and the attempt is intact. What this session bought is a D0 that is committed and
   an environment reading that the next registration needs.

## What returns to the operator

1. **The attempt is NOT spent.** `docs/PROMPT-pass1-fewshot.md` D1 is unexecuted and every D0
   artefact it depends on is committed and green.
2. **Rung 2 needs a ruling.** Either wait for the datacenter (lora-b's precedent: the operator ruled
   «ждать» and the window opened in ~1 h) or re-register the dead-man from tonight's two readings —
   which is a new registration, not an edit, because the current one is committed and spent one
   recovery.
3. **The recovery clause is used.** A third pod under this registration is not allowed.
4. **$0.1178 of the $1.50 cap is gone** and 5 727 s of the 6 300 s hard stop remain — but the stop
   is cumulative across the attempt, so a re-registration inherits neither.
