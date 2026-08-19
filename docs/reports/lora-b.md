# Report — `lora-b`: D0–D2 closed at $0, and the pod is NOT created

Contract `docs/PROMPT-lora-b.md`. **Steps 0, 0.5, D1 and D2 are executed and committed. D3 — the
one paid session — was NOT started, and D4 has nothing to score.** The reason is the contract's own
H6 clause: *«re-derive every registered number below from its formula; a mismatch is a finding
BEFORE the money»*. Seven of the fourteen registered numbers moved, and beside them sits a
train/eval difference on the gate's own rows that has a measured price and a removal that does not
fit inside one paid session. With ONE attempt at a sealed bar, that is the operator's call and not
the executor's, so it is on the table with numbers instead of spent.

**The operator then ruled branch C** (below): the substituted topic is cut to the envelope a
bought one occupies. It put every one of the 650 rows back under the frozen ceiling, returned the
second `молочный_бренд` row to both arms, and **H6 now re-derives all fourteen registered numbers**.
The pod is still not created — the entity-block finding is the half branch C does not touch, and
that is the ruling still open.

Ten commits, `9317c80` → `HEAD`, `make check` green at every boundary — 3 004 / 3 009 / 3 053 /
3 068 / **3 071 passed, 2 skipped** — and `ruff format --check` clean. Cause tags from the closed enum v2 only; lesson names ride as trailing
`[[wiki-name]]`.

## Read back, before the first edit

1. **The gate is ONE attempt and its multiplicity is named.** `max(gold14(A), gold14(B)) ≥ 12/14`
   on the sealed gold r2, scored by probe-b's scorer; no retry, no tuning after any eval output is
   seen; two shots ≈ double the false-pass odds of one, accepted by the sitting-2 ruling and
   written into the record; red closes line B and returns to sitting C; a tie ships arm B.
2. **Frozen:** `config/qlora.yaml` · the `pass1_comment_gm4_v1` prompt sha `5a4a3cb6…` ·
   `src/market_pulse/local_llm.py` · `src/market_pulse/prompts.py` · gold r2 and probe-b's per-row
   base record · both packs and both label files (verbatim commits only).
3. **Kill-clock, each rung BEFORE its milestone:** price > $0.80/h at create → no endpoint · ssh
   dead-man ≤ 180 s → KILL · boot-to-training-start ≤ 450 s → KILL · s/step > 122 s over five
   consecutive logs → KILL · **guard reading ≤ $2.50 after arm A or arm B never starts** · absolute
   session ceiling 7.5 h, window bounded by `guard --until`.
4. **The arm-A milestone is a STOP, not a warning:** over $2.50 the session closes with arm A.
5. **Recovery:** ONE pod re-creation, only after a deletion proven by listing, same cap, never two
   billing endpoints at once; pods, not serverless.
6. **The base is never re-run:** 9/14 and its per-row verdicts come from probe-b's sealed record,
   paired on identical instances and the same prompt sha.

## Step 0 — the tail and the r2 seal

`git status --porcelain` at step 0 returned exactly the Baselines block's six paths:

```
 M docs/STATUS.md
 M knowledge/daily_logs/2026-08-19.md
 M knowledge/hot.md
 M knowledge/index.md
?? docs/PROMPT-lora-b.md
?? docs/labels-pass1-r2.jsonl
```

Three commits: the vault tail (`9317c80`), the team-lead files verbatim (`29f0639`), and the
atomic r2 seal (`e027d0b`). The seal's three readings of the same sha, before staging, after
committing, and out of git:

```
=== sha BEFORE staging ===
8f611437fdd3ed724acda516186bfa2837d94d7e8d74ac6c25e23a8e57d60e50  docs/labels-pass1-r2.jsonl
8f611437fdd3ed724acda516186bfa2837d94d7e8d74ac6c25e23a8e57d60e50  results/labels_pass1_r2.jsonl
=== sha AFTER committing ===
8f611437fdd3ed724acda516186bfa2837d94d7e8d74ac6c25e23a8e57d60e50  docs/labels-pass1-r2.jsonl
=== sha OUT OF GIT ===
8f611437fdd3ed724acda516186bfa2837d94d7e8d74ac6c25e23a8e57d60e50  -
```

`results/labels_pass1_r2_provenance.json` is provenance and pin in preflight's shape, and it
carries the distribution **with its zero in it** — `молочный_бренд: 0`. The class the whole re-draw
was aimed at is the input arm B is registered on, and a key dropped for being empty reads as a
class nobody counted. The pin resolves:

```
[3] pins — 1 of the 4 touched paths are pinned by a record
    results/labels_pass1_r2.jsonl  <- 1 pin(s): results/labels_pass1_r2_provenance.json.frozen.sha256 8f611437fdd3…
[4] digests — sha256 of all 1 pinned paths, against what is pinned
    1 of 1 pinned paths match every digest on them
```

The seal tests mirror r1's **with** the hardened `FILES` path-asserts from day one — every block's
digest is checked against the file that block NAMES — plus the flipped-label negative control on a
scratch copy, which shows the validator still saying `OK` while the digest, the distribution and
the byte-identity each catch the moved label. The last test used to SKIP until the file existed;
it flips in the same commit as the file, because a skip is the softer form of the clock an absence
assert is. That accounts for the baseline: **3 001 passed / 3 skipped** was measured before the
labels landed, and the seal commit reads **3 004 passed / 2 skipped** — two new tests, and the
third skip was this one.

## Step 0.5 — `make baselines`, and the lesson that had no file

**The instrument (Dv553's escalation).** `scripts/baselines.py` + `make baselines` print the block
a contract pastes, measured at the moment it is asked for: head, porcelain, the census line (by
RUNNING `context-census.py`, never by re-implementing it), the suite count, the boot files with
MEMORY.md's two axes, and the pin registry's counts. The suite count is the one thing it refuses to
invent — `tests/conftest.py` stamps what pytest ran, and the stamp records **which selection** ran:

```
- suite: 15 passed — PARTIAL RUN: tests/test_lora_b_prereg.py, stamped 2026-08-19T14:32:48+00:00 at b7a259981518
```

A one-file run reporting as the suite would be the same defect one step down, so the test that
proves it does not is the point of the file. With no stamp at all the line says «run `make check`».

The pin line is a **population count** and says so: a record pins a file as it was at ITS moment,
so 31 of 1 487 paths carrying an older pin is the shape of a repo with history, not an alarm.
`make preflight ARGS='<path>'` is where a stale pin is a finding.

**The orphan lesson.** `the-argmax-and-the-max-are-two-rows` is planted (2 273 B): `max(items,
key=allocation)` names one row and `max(sizes)` measures another, thirteen threads tied at
allocation 12, and the record published `@klopotenkofood:6032 · 125 payable` — a true name, a true
count, a false sentence. **No index line**, and no eviction to make room:

```
150 lines / 18 895 B  =  150/200 lines (75.0%) · 18 609/25 000 UTF-16 units (74.4%)
```

The index stands exactly AT the 150-line bar, so the line-debts stay named, now two:
`a-checker-whose-failure-is-silence` and `the-argmax-and-the-max-are-two-rows`. Both files are on
disk and cost 0 at boot.

## D1 — the three seams, driven at zero cost

### The SFT builder, and the census it prints

`scripts/build_pass1_sft.py --census` writes nothing. **As first built** — before the branch-C
ruling, and the state the two findings below were measured in:

```
PASS-1 SFT — the two arms, bound at max_seq_len 1408

 arm   rows   steps   бренд   кат  сеть    нн  null    entities  topic
   a    464      58       1    35    44   246   138          32     70
   b    607      76       1    45    48   335   178          39     91
  arm a sampler weights: {'null': 0.672464, 'категория_личное': 2.651429, 'молочный_бренд': 8.0, 'не_наш_рынок': 0.377236, 'сеть_ритейлер': 2.109091}
  arm b sampler weights: {'null': 0.682022, 'категория_личное': 2.697778, 'молочный_бренд': 8.0, 'не_наш_рынок': 0.362388, 'сеть_ритейлер': 2.529167}

DROPPED FOR LENGTH  43 rows {'r1': 36, 'r2': 7} — longest kept 1344 tokens, shortest dropped 1412
CONTEXT             the gate's 14 rows carry 12 entity blocks; the eval pack's 64 items carry 55
                    arm b's 607 rows carry 39
```

Determinism, the `--outdir` pair against the shipped copy (**as first built**; the shipped shas
after branch C are in the section at the end):

```
pass1_sft_arm_a.jsonl            identical  37493f6319b9be35…
pass1_sft_arm_b.jsonl            identical  e1e14ee7f5e17bc7…
pass1_sft.json                   identical  edbea54af33fa857…
```

**The supervised span.** The team lead labelled `subject_type`; `prompts.parse_pass1` demands four
keys. Filling the other two with `null` and training on it teaches «stance is always null» — and
three of the fourteen gold rows score `stance` against a non-null value (21626, 21629, 580124), so
not one of them could agree again whatever the model said about the subject. **14 − 3 = 11 against
a threshold of 12: the gate would have been unreachable before the pod existed.** So each row
carries `learn_chars` and only the head — through the `subject_type` value — is supervised. The
arithmetic is a test, not a paragraph.

### The trainer

`--data` takes a pre-rendered dataset and **refuses one `results/pass1_sft.json` does not
register**; `--class-weights` turns on `w_c = N/(5·n_c)` capped at 8.0, computed on the arm's own
dataset, OFF by default and both branches driven. The epoch draws the dataset's **own size** with
replacement, so `steps/epoch = ceil(n/16)` is unchanged and the registered step count stays true —
a sampler that oversampled to balance would have lengthened the run it was registered under. The
formula has one home: `build_pass1_sft` calls `train_qlora.class_weights`, and a test asserts the
two agree row for row.

The pass-1 branch loads through `local_llm.load_captioner` — the **processor** the eval path builds
its client on — so train/eval format identity is held by construction rather than by an assertion
made afterwards. The mask is cut on character offsets, and a token that straddles the boundary is
masked (supervising less, never more), because re-tokenizing the head and hoping the merges agree
is the kind of thing that moves by one token and says nothing.

### The transport

`--adapter` mounts the PEFT adapter **around** the model `local_llm` builds, after the shipped
loader's own `serve_handler.assert_no_adapter` has passed on the base — the base-only handshake is
not skipped, it is passed and then deliberately reversed by a run that registers an adapter.
`local_llm.py` is untouched and so is the shipped runner's parser: the flag is consumed before argv
reaches it, and `--out` is re-appended.

peft injects LoRA into the base modules **in place**, so after the wrap nothing distinguishes the
two branches by identity and no evidence row says which arm produced it. The observable is written:
`<out>.adapter.json`, every file of the adapter hashed, **before** the first reply. Both argv
branches are driven — with the flag the record exists, without it there is none — and `attach` is
driven directly with a fake `peft` rather than only through `main(loader=…)`, because a stub loader
replaces the very path the flag exists to exercise.

### H6 — every registered number, re-derived (**as first run**)

```
H6 — 14 registered numbers re-derived from their formulas

  RED arm_a_rows                   registered 500       -> 464
  RED arm_a_seconds                registered 3907      -> 3540.7
  RED arm_a_steps                  registered 64        -> 58
  RED arm_b_rows                   registered 650       -> 607
  RED arm_b_seconds                registered 5006      -> 4639.6
  RED arm_b_steps                  registered 82        -> 76
  ok  base_bar                     registered 9         -> 9
  ok  boot_gate_seconds            registered 450       -> 439.5
  ok  census_50_baseline_none      registered 25        -> 25
  ok  combined_distribution        registered {…340, 213, 48, 47, 2}  -> identical
  ok  eval_seconds                 registered 660       -> 660.7
  ok  session_ceiling_hours        registered 7.5       -> 7.5
  ok  step_watchdog_seconds        registered 122       -> 122.094
  RED worst_case_usd               registered 2.63      -> 2.4647

  mismatches: ['arm_a_rows', 'arm_a_seconds', 'arm_a_steps', 'arm_b_rows', 'arm_b_seconds', 'arm_b_steps', 'worst_case_usd']
```

Every mismatch is one cause: **the contract sized the arms in LABELS and the trainable set is what
fits `config/qlora.yaml`'s frozen `max_seq_len`.** 43 rows render past it and are dropped by name
into `results/pass1_sft.json`. All seven move in the cheaper direction; none was silently fixed —
and after the branch-C ruling all seven re-derive exactly, which is the strongest thing that can be
said about the contract's own arithmetic: it was right, and the executor's substitute was what
broke it.

The two kill thresholds are checked for the direction of their margin instead of for equality, and
that is spelled out in the record: 450 s over a derived 439.5 s is margin, 122 s under a derived
122.094 fires slightly early, and either on the wrong side of its own formula would come out red.

## D2 — the pre-registration, committed before any pod

`results/prereg_lora_b.json`. Nothing in it is typed twice: the bar block, the per-call readings
and `return_to_sitting` are READ out of `results/prereg_pass1_probe_b.json`, the fourteen gold rows
are derived from the gold record and **refused unless they equal probe-b's registered list**, and
the arms come from the self-pinned `results/pass1_sft.json`.

The shape is derived from its consumer, not from the contract's prose: a test hands this record to
`score_pass1_probe.bar_p1` — the function D4 will grade with — and drives it to 14/14, to 12/14
(passing, exactly at the bar) and to 11/14 (failing).

```
WORST CASE 3.081 h × $0.80/h = $2.4647 against a cap of $6.00  (headroom $3.5353)
REACH      9 of 14 today; the arm must turn 3 of the 5 missed — {'категория': 4, 'молочный_бренд': 1}
CONTEXT    the gate's rows carry 12/14 entity blocks; arm B's training rows carry 39/607
```

### Reachability, priced before the attempt is spent

| what the arms must do | number |
|---|---|
| agreed today (sealed base record) | 9 of 14 |
| rows the arm must turn | **3** |
| the five missed, by gold class | `категория` 4 · `молочный_бренд` 1 |
| arm B training rows behind `категория_личное` | 47 (45 before branch C) |
| arm B training rows behind `молочный_бренд` | **2** (1 before branch C) |

Four of the five rows an arm has to turn are gold «категория» and the fifth is «молочный_бренд».
Arm B carries **two** rows of that class — the labelled set holds two, and until the branch-C
ruling one of them rendered past `max_seq_len` and was dropped. A sampler weight of 8.0 on two rows
is still a weight on two rows.

### The context the gate carries and the training set does not

A pass-1 request holds the thread's `<topic>` and `<entities>`, and **both come from a reader
verdict that was paid for**. 15 of the 120 labelled threads have one.

| | rows | with a real entity block |
|---|---:|---:|
| the gate's own 14 | 14 | **12** |
| the eval pack | 64 | 55 |
| arm B training set | 650 | **39** |

For the other 105 threads the topic is rendered from the store's own post text. Bought reader
summaries run **26–147 characters** (median 87); the substituted post texts ran to a median of
3 226 and a maximum of 6 810 characters in the rendered request, which is also what pushed the 43
dropped rows over the ceiling. **Branch C closed that half and only that half**: the substitute is
now cut to 147 characters, so nothing is dropped — and the entity block is exactly as empty as it
was, because a cut buys no verdict. The arms are trained on requests whose entity block is almost
always empty and graded on requests where it is almost always full.

**It has a price, and there are three branches — all measured, none of them assumed.**

| branch | what the arms train on | cost | what it fixes |
|---|---|---|---:|
| **A — run as registered** | topic = the raw post, entity block empty on 568 of 607 rows | **$0 extra**; D3 is $2.46 of the $6.00 cap | nothing; the risk is accepted knowingly |
| **B — buy the reader pass first** | topic = a bought summary, entity block real, on every thread | **≈$1.20** · 105 × 51.3 s ≈ 5 390 s ≈ 1.5 h, in a SEPARATE session | both findings: the context gap AND the 43 dropped rows |
| **C — bound the substituted topic** ✅ **RULED AND EXECUTED** | topic = the post's opening cut to the bought-summary envelope, entity block still empty | **$0** | the length finding only: **0 of 650 rows over the ceiling, max bound 1 225 tokens, both `молочный_бренд` rows kept** |

Branch B cannot happen inside D3: a dataset built during the paid session could not have been
pre-registered before `pod create`, which is the clause the whole registration rests on. Branch C
is a rebuild of the datasets and a re-run of the prereg producer, both at $0, and it recovers the
second brand row — but a truncated advertisement is not a summary, so it closes the length finding
and leaves the context one open. Registered as a risk; the ruling is the operator's.

### Digests, after as before

The DO-NOT list demands that every pinned or sealed file hash the same after this contract as
before it. The exact proof is the diff, not a summary — `git diff --stat 872449d..HEAD` over
`config/qlora.yaml`, `src/market_pulse/local_llm.py`, `src/market_pulse/prompts.py`,
`results/reader_gold_w1_r2.json`, both label packs, both r1 label files and both rendered pack
pages returns **empty**: not one of them moved.

The pins the paid run will depend on resolve to the same bytes from two independent records:

```
prompts.py live           a4a5a5d08546f53af18117c37e49f7e396919555563e16737a633c1df1a86eec
probe-b pack pins parser  a4a5a5d08546f53af18117c37e49f7e396919555563e16737a633c1df1a86eec True
lora-b prereg pins parser a4a5a5d08546f53af18117c37e49f7e396919555563e16737a633c1df1a86eec True
prompt sha pass1_comment_gm4_v1  5a4a3cb6ce4db89adb304c04de41210fdabfde0c53addfdb75adba0f1d866650  (pack == prereg)
config/qlora.yaml         6771ed373f9e7c52b3180a45506fe0dfef4446bc89b2c3ff6c1b39992f2d00ff True
```

`scripts/preflight.py` on those paths also lists older pins on `prompts.py` and `local_llm.py`
from reader-era records. Those are the population effect `make baselines` prints — 31 of 1 487
paths carry a pin from an earlier state, by design — and not a finding of this contract: the two
records the pass-1 instrument is registered under agree with the live bytes, and the git diff above
is what says nothing moved.

## D3 / D4 — not run

No `pod create`, no endpoint, no `runpodctl` call, `$0.00` spent. `git log` for this contract shows
no `run(` and no `close(` commit, because there was nothing to spend. The three reasons, in order:

1. **H6 came out red on seven numbers** and the contract's own words make that «a finding BEFORE
   the money», not a footnote after it. ✅ **Closed** by the operator's branch-C ruling: all
   fourteen re-derive.
2. **The train/eval context difference lands on the gate's own rows** — 12 of the 14 are answered
   under an entity block the training set almost never carries (39 of 650) — and it has a measured
   removal cost that does not fit inside the one paid session. **Still open**; branch C does not
   touch it.
3. **One attempt.** Every reason above would be a footnote if the bar could be re-run. It cannot.

Everything D3 needs is committed and green: the datasets, the prereg, the trainer's two flags, the
transport's `--adapter`, and the exact commands are in the record's `arms[*].command` /
`arms[*].eval_command`. A fresh session reads the committed prereg and starts at `pod create`.

## Branch C — ruled by the operator, executed at $0

The ruling: **cut a substituted topic to the envelope a bought one occupies.** The envelope is
measured at every run and never typed — the longest `post_summary` over the 24 bought verdicts,
which is 147 characters (shortest 26, median 87) — and the cut is made at a word boundary with an
ellipsis where anything was removed, because a cut advertisement presented whole is a claim that
the topic ends there.

```
PASS-1 SFT — the two arms, bound at max_seq_len 1408; substituted topics cut to 147 chars (the longest of 24 bought ones)

 arm   rows   steps   бренд   кат  сеть    нн  null    entities  topic
   a    500      64       2    36    44   251   167          32     70
   b    650      82       2    47    48   340   213          39     91
  arm a sampler weights: {'null': 0.598802, 'категория_личное': 2.777778, 'молочный_бренд': 8.0, 'не_наш_рынок': 0.398406, 'сеть_ритейлер': 2.272727}
  arm b sampler weights: {'null': 0.610329, 'категория_личное': 2.765957, 'молочный_бренд': 8.0, 'не_наш_рынок': 0.382353, 'сеть_ритейлер': 2.708333}

DROPPED FOR LENGTH  0 rows — every row fits; the longest is 1225 tokens
CONTEXT             the gate's 14 rows carry 12 entity blocks; the eval pack's 64 items carry 55
                    arm b's 650 rows carry 39
TOPIC               91 bought · 372 cut to the envelope · 187 substituted and already inside it
```

The last line is how far the ruling actually reaches, and it is a field of the record rather than a
sentence here: **372 of 650** topics were shortened by the cut, 187 substituted ones were already
inside the envelope, and 91 were bought and are never cut. Rendered topics now run 16–147
characters with a median of 139, and not one row falls back to «this post has no text».

The arm distributions are now the contract's own, to the row: 251 · 167 · 44 · 36 · 2 for r1 and
340 · 213 · 48 · 47 · 2 combined. **H6 re-derives all fourteen:**

```
  ok  arm_a_rows      500 -> 500       ok  arm_b_rows      650 -> 650
  ok  arm_a_steps      64 -> 64        ok  arm_b_steps      82 -> 82
  ok  arm_a_seconds  3907 -> 3907.0    ok  arm_b_seconds  5006 -> 5005.9
  ok  eval_seconds    660 -> 660.7     ok  worst_case_usd 2.63 -> 2.6275
  ok  boot_gate_seconds 450 -> 439.5   ok  step_watchdog_seconds 122 -> 122.094
  ok  session_ceiling_hours 7.5 -> 7.5 ok  census_50_baseline_none 25 -> 25
  ok  base_bar          9 -> 9         ok  combined_distribution — identical

  mismatches: none

WORST CASE 3.284 h × $0.80/h = $2.6275 against a cap of $6.00  (headroom $3.3725)
REACH      9 of 14 today; the arm must turn 3 of the 5 missed — {'категория': 4, 'молочный_бренд': 1}
CONTEXT    the gate's rows carry 12/14 entity blocks; arm B's training rows carry 39/650
```

Determinism, the `--outdir` pair against the shipped copies, after the rebuild:

```
pass1_sft_arm_a.jsonl          identical  383fa254983163c2…
pass1_sft_arm_b.jsonl          identical  378203ef77d98698…
pass1_sft.json                 identical  249295f0d984dd79…
prereg_lora_b.json             identical  6f412efca513a2df…
```

One bounded topic, as the model now sees it, with the supervised head beside it:

```
@matusi_ukr:22327#580336 | topic chars 144
'1)Привіт Дівчата, ви все знаєте.  Порекомендуйте з власного досвіду генератор для дому, щоб тягнув і холодильник і морозилку і пралку і праску.…'

target:      {"msg_id": 580336, "subject_type": "не_наш_рынок", "subject_id": null, "stance": null}
learn_chars: 49 -> '{"msg_id": 580336, "subject_type": "не_наш_рынок"'
```

**What branch C did not do.** It bought no reader verdict, so the entity block is unchanged: 39 of
650 training rows carry one against 12 of the gate's 14. The finding stands, it is registered in
`results/prereg_lora_b.json` under `reachability.the_context_the_gate_carries`, and the branch that
closes it is still B — a reader pass over the 105 uncovered threads, ≈$1.20, in its own session.
**The pod is not created.**

## Deviations from Dv554

| # | finding | tag |
|---|---|---|
| **Dv554** | **The registered arm sizes are label counts, and the trainable set is what fits the frozen ceiling.** `config/qlora.yaml` is frozen law and its `max_seq_len` is 1408; 43 of the 650 rendered rows are bounded past it at the worst tokens-per-character probe-b measured (0.291741, its own max over 64 paid rows, not the mean). Arm A is 464 and arm B 607, so steps, seconds and the worst case all move — every one of them cheaper. The rows are dropped BY NAME into the record rather than discovered by a `SystemExit` inside a training loop at $0.80/h. One of the two `молочный_бренд` rows is among them, which is why the class the re-draw was aimed at had one training row. **CLOSED by the operator's branch-C ruling**: cutting the substituted topic to a bought one's envelope put all 650 back under the ceiling and every one of the seven numbers re-derives. | `[cause: contract-gap]` `[[compute-the-ceiling-first]]` |
| **Dv555** | **The answer has four fields, the labels have one, and the obvious fill puts the bar out of reach.** `parse_pass1` demands `msg_id`, `subject_type`, `subject_id`, `stance`; the team lead labelled `subject_type`. Writing `null` into the other two AND training on it teaches «stance is always null», and three of the fourteen gold rows score `stance` against a non-null value — 21629 scores it ALONE. The reachable maximum would be 11 against a threshold of 12. The contract does not mention the field gap at all; it is closed by masking the unlabelled tail out of the loss, which is why `learn_chars` exists and why the arithmetic is a test. | `[cause: contract-gap]` `[[compute-the-ceiling-first]]` |
| **Dv556** | **The context a pass-1 request carries is BOUGHT, and 105 of the 120 labelled threads never bought it.** `<topic>` and `<entities>` come from a reader verdict; only 15 labelled threads have one. Arm B carries 39 entity blocks over 607 rows while the gate's own 14 rows carry 12 and the eval pack 55 of 64. The substitute — the store's raw post text as topic — is also what pushes 43 rows past `max_seq_len`, since bought summaries are 26–147 characters and the posts are thousands. Registered as a reachability term with its removal priced (~$1.20, a separate session); NOT silently accepted, and not silently fixed either. | `[cause: contract-gap]` `[[build-the-training-prompt-with-the-inference-call]]` |
| **Dv557** | **«A class-weighted sampling flag» needs a data path the trainer never had.** `train_qlora` is hardwired to phase 4's T1/T2 sources and `prompts.build_messages` refuses a pass-1 task BY NAME (`prompts.py:1419-1420`), so no arrangement of the existing code could have trained on `subject_type` at all. The contract's own sentence — «arm deltas (data path, weights on) live in the prereg record and CLI args only» — is what licenses `--data`; it is read here as naming two flags, not one. | `[cause: contract-gap]` `[[a-consumer-list-is-not-a-meaning-list]]` |
| **Dv558** | **The two `--adapter` branches are not distinguishable by identity.** `PeftModel.from_pretrained` injects LoRA into the base modules in place, so the wrapped model and the base are the same object graph afterwards and the shipped runner records nothing about weights. A sim that asserted «the loader returned something different» would pass on a wrap that silently did nothing. The branches are separated by an artefact instead: `<out>.adapter.json`, hashed per file, written before the first reply — and `attach` refuses outright if `peft_config` comes back empty, because a run that evaluated the base under an arm's name would publish an ablation with no ablation in it. | `[cause: verify-gap]` `[[gate-verdicts-need-an-artifact]]` |
| **Dv559** | **H6's first tolerance passed a number that had moved.** `max(1.0, 1%)` is a sane rule for seconds and a blind one for dollars: it marked the worst case $2.4647 as agreeing with the registered $2.63, a 6.3% move, because the absolute floor swallowed it. Tightened to 1% relative, which turns that row red — and the two kill thresholds, which are ceilings and not measurements, are checked for the DIRECTION of their margin instead. Caught by reading the printed table, not by a test; the test came after. | `[cause: verify-gap]` `[[check-granularity-matches-the-claim]]` |
| **Dv560** | **Two arms evaluating into one file would answer nothing and look complete.** The shipped runner's resume skips every unit already answered, so the second arm's eval against the first arm's out-file would find 64 of 64 answered, print «nothing to generate», exit 0 — and D4 would score arm A's replies twice under two names. Each arm's eval command names its own out file, registered in the record, and the reason is written beside it. | `[cause: verify-gap]` `[[the-hardening-did-not-reach-the-sibling-reader]]` |
| **Dv561** | **D3 is not run, and the contract's own H6 clause is why.** «A mismatch is a finding BEFORE the money» — seven of fourteen registered numbers moved, and the context finding lands on 12 of the gate's 14 rows with a removal that costs ~$1.20 in a session this registration cannot contain. Against ONE attempt at a sealed bar, spending it is a ruling and not an execution detail. Everything D3 consumes is committed and green; the split the contract itself offers («you MAY close D0–D2 in one session and run D3–D4 in a fresh one») is where this stops. **After branch C, H6 is green and the remaining reason is the entity block alone** — the ruling on branch B is what the pod waits for. | `[cause: contract-gap]` `[[an-absolute-bar-needs-a-reachability-state]]` |
| **Dv562** | **A record's prose quoted numbers the record derives, and the ruling made it false.** `reachability.to_pass.reading` in the pre-registration producer spelled out «Arm B carries 45 rows of the first class and ONE of the second — the second brand row … was dropped». Both halves stopped being true the moment branch C rebuilt the datasets, and the block around them is regenerated from `results/pass1_sft.json`, so the record would have shipped a paragraph contradicting the numbers three lines above it. Rewritten as an f-string over the same source, and it says so: «the numbers are read off the dataset record rather than written here — this sentence has already been wrong once». | `[cause: verify-gap]` `[[corrections-break-derivations]]` |
| **Dv563** | **The contract's arithmetic was right and the executor's substitute was what broke it.** Seven of the fourteen H6 rows were red on the first build, and after a $0 change to how ONE context field is rendered every one of them re-derives — 500 / 650 rows, 64 / 82 steps, 3 907 / 5 006 s, $2.6275 against a registered $2.63. The finding was real and the number it accused was not: H6 says «these two disagree», and reading it as «the contract is wrong» would have been the expensive half of being right. | `[cause: process]` `[[trace-the-producer-not-the-result]]` |

## Process signals

1. **The cheapest measurement of the session killed the most expensive mistake.** Counting which
   gold rows score `stance` takes one list comprehension over a sealed record and it is what
   decided the target format. Had the datasets shipped with `stance: null` supervised, the arms
   would have been trained, evaluated and scored against a bar arithmetically out of reach — and
   nothing in the loss curve would have said so.
2. **Two independent findings had one cause, and only one of them was visible.** The dropped rows
   and the empty entity blocks are both «no reader verdict was bought for this thread». The length
   overflow announces itself with a `SystemExit`; the context gap announces itself with nothing at
   all, and would have been discovered as a disappointing number after the money.
3. **The seam the contract described in one clause was three files deep.** «A class-weighted
   sampling flag» is a two-line formula sitting behind a data path, an encode, a sampler and a
   loader branch — because pass 1 had never been trainable at all. Reading the seam before pricing
   it is what turned that into a $0 finding instead of a pod-side stack trace.
4. **A tolerance is a threshold and deserves the same suspicion as a bar.** H6's `max(1.0, 1%)` was
   written to keep roundings quiet and it silenced a 6.3% move in the one number the cap depends
   on. The fix was not more tolerance rules but naming, per row, WHICH way each number is allowed
   to be wrong.
5. **The instrument built in step 0.5 reported on the session that built it.** `make baselines`
   printed `PARTIAL RUN: tests/test_lora_b_prereg.py` while this report was being written — the
   exact class of claim Dv553 escalated it for, refused by the tool the escalation asked for, on
   its first day.
6. **A red gate is a disagreement and not a verdict about which side is wrong.** H6 accused the
   contract's arithmetic on seven rows; the contract was right on all seven and the executor's
   substitute for a bought topic was the defect. The table's value was that it made the two
   readings sit beside each other — had it been written as «the registered numbers are stale», the
   $0 fix would have looked like a re-registration instead of a bug.

[[compute-the-ceiling-first]]
