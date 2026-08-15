# probe-b — the interface fixed, the card replaced, the bars scored for the first time

**Contract:** `docs/PROMPT-probe-b.md` · **closes:** `docs/reports/probe-a.md` §5–§6 · **baseline:**
`make check` 2 521 passed / 2 skipped at `8c68107` (probe-a close) · **HEAD at the start:** `8c68107`.

**Outcome in one line.** Step 0, D1 and D2 landed before any endpoint existed; then the endpoint drew
the card option B was bought for — an **RTX 4090**, `gpuIds: ADA_24`, read back for free before the
first job — and the warm-up measured **20.759 s a thread against probe-a's 54.806 on an L4: 2.64×**,
over the **2.007×** break-even this registration had computed before anything was created. The gate
said **GO**, all **23 threads** were read for **$0.2907 of $0.35** at the deletion reading, and the
four bars were computed for the first time in this program: **flagships 2 of 5 · entity cases 2 of 4
· noise 0 signals (passes) · per-comment 0.357 against 0.80**. The two defects v2 was written to
close never reappeared. Six OTHER reply shapes refused 10 of the 23 replies, and the two most
consequential numbers in this report are what that costs: coerced with container-only repairs the
replies go **13 → 19 of 23** and entity cases **2 → 3 of 4**, and **bar 3's pass is a count of zero
over four threads that have no verdict at all**.

---

## 0. Step 0 — the tail, one money-path fix, and a seal nobody planned

### 0.1 The standing tail, and the baseline that was already red

`git status` carried the three vault files of the 20:56 `/save`, this contract untracked — and a
fourth file nobody had mentioned: **`docs/PLAN-comment-signals.md`, modified by the team lead**. §3's
schema example spelled two of its own class words the short way, and the edit puts the ratified ones
there:

```
-    {"signal_type": "жалоба", "subject_type": "сеть",
+    {"signal_type": "жалоба", "subject_type": "сеть_ритейлер",
-    {"signal_type": "спрос", "subject_type": "категория",
+    {"signal_type": "спрос", "subject_type": "категория_личное",
```

**The contract's baseline was therefore not reproducible: `make check` was 2 517 / 4 failed before a
line of this contract was written.** The plan is pinned in `authority` by
`results/reader_gold_w1.json` and `results/prereg_reader_probe.json`, and its sha moved under both.

Neither record is re-pinned. Both are probe-a artefacts, frozen by that registration's own
`frozen_when_the_endpoint_exists` clause the moment its endpoint existed — and it existed and was
deleted. Re-deriving them today would rewrite a pre-registration after the money was spent. They take
the house manoeuvre instead: a `MOVED` tuple with its own witness, the sealed bytes recoverable at
`git show 8c68107:docs/PLAN-comment-signals.md`, the substitution required to FIRE so a silent revert
cannot pass, and the witness token read both ways. **The gold rebuilds byte for byte beside it** —
not one row moves, because the transcription is from `docs/REFERENCE-signals-w1.md` and that file is
untouched.

The negative control is in the report because it is the point: restoring the sealed plan into the
working tree makes both re-derivation tests fail again.

→ `d19d454` · `2bdb428` (the tail by path, `docs/PROMPT-probe-b.md` verbatim, never `git add -A`).

### 0.2 Dv392 closed before money moved again

`step_ledger_path` (renamed from `step_file` to the name the records and this contract already used)
normalised `probe-a` on the READ, while `--note` rebuilt the path from the raw step name and appended
to `results/spend_probe-a.json`. One command, one step, two anchor files.

The old test compared two calls of the path function and could not see it — the second spelling was
never built by that function ([[a_guard_on_one_path_is_not_a_guard]]). The new one drives `main` with
`--note`, without `--step-ledger`, and asserts the results directory holds exactly one `spend_probe*`
file. Against the old guard it fails with `['spend_probe-b.json', 'spend_probe_b.json']`.

The two probe-a ledgers are merged into the canonical path, content-preserving: every shared key was
asserted identical before the hyphen file's one session was carried across, and the guard reads the
same anchor `$23.0729` afterwards. **And the fix is proven in production below: probe-b's whole
session, `--note` included, left exactly one `results/spend_probe_b.json`.**

`results/prereg_5c2.json` borrows this module LIVE and its test says the day one of them moves is the
day to look at the line rather than relax it. Looked at: what moved is where a session note is
appended, and no balance, anchor or threshold in that registration is computed by those lines. It
takes a `MOVED_BORROWS` entry with its witness. → `692f161`.

### 0.3 The staging-class footgun re-dated

`knowledge/hot.md`'s Dv177 held that the $0.24/h class had left EU-RO-1. Today's `runpodctl gpu list`
offers **RTX 2000 Ada at $0.240/h, stock Low**, and this session staged on it. The line now carries
the measured fact and says what is durable: read the class list before `pod create`, not the footgun.
→ `4a00952`.

---

## 1. D1 ($0) — `reader_thread_gm4_v2`, two measured defects and nothing else

`5f93116` · sha **`9d281bc80f18c91b…`**, beside v1's `b272115637f784ad…`.

**v2 is DERIVED from v1 by three `_swap` calls, not retyped**, so «exactly two wording changes» is a
property of the code rather than a claim in this report: every other character is v1's, and a fourth
edit would have to appear in `prompts.py` as a fourth call. The whole diff is three lines:

| defect | v1 said | v2 says |
|---|---|---|
| **Dv393** | `"entities" — one object per name of duty (2): {…}` | `"entities" — a LIST of objects, one per name of duty (2), and the name is INSIDE each object: [{…}]. Never an object keyed by the names.` |
| **Dv394** (schema) | `"evidence": the msg_ids you read it from` | `"evidence": the msg_ids of the COMMENTS you read it from, and the empty list [] when you read it in the post — never null and never the post; "from_post": true when the post is where you read it` |
| **Dv394** (rule) | `The post has none: for the post the id is null.` | `The post was given none, so null is the answer in exactly one field — "entities"."msg_id" … Every other id field takes comment ids and never null.` |

`parse_reply` follows in place, one branch: `from_post` absent reads **False**, so a v1 verdict is
still validated by exactly the rule it was registered under, and `evidence: [null]` still refuses.

**v1 stays registered, untouched and servable.** probe-a bought three verdicts under it and its
evidence has to stay re-renderable. That makes the serving stack learn one fact: `reader_messages_gm4`
takes the task and defaults to the live one, `ReaderClient` renders anything in `prompts.READER`, and
`info` answers with a **sha per registered task** — POSITIONS' shape, for POSITIONS' reason. A scalar
could name only one of two texts, and a worker a session behind would match the registration while
the other one had moved.

**The pin fan-out, again and larger** (Dv380's shape). probe-a's gold and registration take a second
`MOVED` tuple; the registration takes a THIRD, because probe-b made v2 the renderer's default and
`write_reader_prereg.py` had to name `task=prompts.READER_TASK` or a frozen record would re-derive
under a prompt no thread was ever sent with ([[a_sealed_caller_forces_the_default]]).
`results/dashboard_data_w1.json` pins its producers LIVE and was **regenerated**: one line moved, and
the page's only moved figures are the export banners and the one node naming this module.

---

## 2. D2 ($0) — the registration, committed before any endpoint

`8bf5a14`, re-derived at `72a9f40` (Dv402), both before any endpoint existed.
`results/prereg_reader_probe_v2.json`, sha `a1f9369bb771562a…`. It supersedes v1 **by sha**, keeps the
scorer, the gold, the ceilings, the serving block and every threshold byte for byte, and changes
three things: the instrument, the card, the population.

### 2.1 The population is 23 threads, enumerated

The contract expected «~16–19» and said «enumerate, don't estimate». Enumerating produced **23
threads and 134 payable comments** (Dv399): the six S-list rows resolve to four posts nobody had
counted, and the three probe-a warm-up threads are a fourth group.

| group | threads |
|---|---|
| flagships F1–F5 | 5 |
| entity cases E2, E3 | 2 (E2's thread also carries S3) |
| noise N2, N4–N6 | 4 |
| the S list | 6 posts, of which 4 are new (S1 is N1's thread) |
| probe-a's warm-up | 3 |
| **gated subtotal** | **19** |
| **injected** — E1 `@matusi_ukr:22242`, E4a `@mandziak:3684`, E4b `@mandziak:3689`, N3 `@sashafitnesslife:3939` | **4** |

The injected four are marked `injected: true`, and the record states what that means: they exist to
make bars 2 and 3 reachable, they never enter a production aggregate or a window price — the gate
does not deliver them, so a rate measured over them would price a population nobody has — and **they
are inside this cap, because this run buys them.** `assert_the_injected_are_the_four_the_gate_removes`
refuses in both directions and is checked against the gold's own reachability block, so the list
cannot quietly grow.

**What that buys:** bar 2 becomes 4 of 4 where v1 could only register 2 of 2, and bar 4 becomes 14 of
14 where v1 had 13 — msg 578951 arrives with E1.

### 2.2 The cap divided by a measured rate, before anything was created

probe-a's own lesson, applied one contract earlier in the sequence ([[the_setup_is_inside_the_cap]]):

```
setup (measured, probe-a's SETTLED ledger) ...................... $0.0440
seconds $0.35 can buy after it ................................... 997.8 s
23 threads at the L4's 54.806 s ........... 1 260.5 s ........... $0.4306 all-in
134 payable at the L4's 14.947 s .......... 2 002.9 s ........... $0.6583 all-in   ← binding
```

**Neither fits.** So the registration states the number the go/no-go exists to measure: a card
**1.946×** faster than probe-a's L4 makes this population affordable — **2.007×** after Dv402 moved
the setup constant. That is not a guess about the card: the $/s every projection in this repo uses
was measured on an `ADA_24` (RTX 4090, `docs/reports/5c2-run.md`), probe-a's endpoint drew an L4 at
the same price, and EU-RO-1 lists `ADA_24` at **High** stock. The class is requested fastest-first and
never asserted — which card a worker gets is the runtime delta SPEC 3.11 (2) exists to report, and a
slow card is caught by the gate's arithmetic rather than by a guard that would spend a boot to refuse.

### 2.3 Two findings registered rather than repaired

- **N3 reaches the reader as an empty thread** (Dv400). `@sashafitnesslife:3939` has 29 comments and
  the gate's own plus-spam silencer removes **all 29** before payment, so the reader is given a post
  and nothing else. Its «0 signals» cell is produced by the silencer, not by the reader
  ([[a_structurally_unreachable_zero]]). Registered inside the bar because the contract names it,
  and reported beside it because a cell that cannot be non-zero is not evidence.
- **8 of the 14 per-comment gold rows score on `subject_type: категория`** (Dv398) — a word the
  ratified entity taxonomy does not carry, which is in the prompt only because plan §3's schema
  example used it (Dv388), and which that example **stopped using today**. The bar is not moved for
  it. The same bars recomputed with `категория_личное` folded into `категория` are registered as a
  reported number, through the same scorer functions, so a failure on that split can be told apart
  from a reading failure.

---

## 3. The driver, the preflight and the scorer — all $0, all before the endpoint

`8fd1b44` · `a5089e0` · `6c975b4`.

**The go/no-go arithmetic v1 got wrong** (Dv401). probe-a's driver projected the WHOLE population and
compared it against what the cap had left AFTER the warm-up, counting the warm-up's threads twice —
2.7% of the cap at 111 threads, **13% at 23**, which is the difference between a STOP and a GO on a
run the cap can afford. probe-b projects the UNREAD remainder, adds the measured setup, computes both
projections and lets the pessimistic bind. probe-a's own STOP is unaffected: its binding projection
was $4.18 against $0.45.

Three guards the fake endpoint proves, none of which v1 had:

- the handshake compares a sha for **every** registered reader text. A worker that matched the text
  this run reads with could still be a session behind on the other — exactly what a half-applied
  volume fetch leaves — and a scalar answer is named as v1's shape rather than diffed key by key;
- a re-invoked `--warm-up` reads its billed seconds from the **persisted rows**. A fresh client
  reports zero, and a projection over zero seconds says GO on a run nobody priced;
- every thread's rendered request is held to a **per-thread sha** the registration pinned. The digest
  says which threads; this says what each of them is.

**The preflight ran on the real libraries before anything could bill: 63 of 63 PASS**, up from 57.
Six are new and two could only be bought here — the real chat template over BOTH registered texts
(each keeps `<bos>`, each closes the thought channel, and the two must render differently) — plus
section 17, Dv394 driven three ways on the parser that would read the paid replies:

```
17. Dv394 a post signal       from_post + [] parses: True
    evidence [null]            REFUSE — signals.evidence is not a msg_id
    an empty evidence unflagged REFUSE — signals.evidence is empty and the signal is not marked from_post
    Dv393 the entities line    LIST + brackets: True
```

**And the bars were computed at $0 before the endpoint existed.** probe-a's scorer never computed
one: its gate stopped the run before any bar's threads were read, so four functions with
hand-computed unit tests had never once run against a verdict. A synthetic PERFECT reader built out
of the gold passes all four; broken one field at a time it fails each for its own reason and leaves
the other three passing. **Then probe-a's three REAL paid replies, coerced to v2's container shape,
all three parse — `from_post` signal included.** That is the cheapest evidence there is that the two
wording changes address the defects that were measured rather than defects that were guessed.

---

## 4. The paid pass

### 4.1 What was created, in the runbook's order

| step | resource | clock (UTC) | cost |
|---|---|---|---|
| the step anchor | `results/spend_probe_b.json`, balance **$22.9784784161** | 20:31 | $0 |
| stage the volume | pod `tv196vx3p5khsu`, RTX 2000 Ada, EU-RO-1, `--terminate-after` | 20:31:30 → 20:33:09 (**1 min 39 s**) | ~$0.0066 |
| serve | template `ueasek6tk6` + endpoint `lfqvip37lpgcii`, **`gpuIds: ADA_24`**, workersMax 1, idle 60 s, execution 900 s, flash-boot, volume `qw4nwleanc` | 20:33 → 20:51 | the rest |

The volume's `repo/` moved `a4fb51e → f0fd745` by **fetch + hard reset**, never `rm -rf`: the
gitignored 467 MB adapter lives inside `repo/` and is still there (489 840 816 bytes). Then the
strongest check available before an endpoint exists, and this time over BOTH instruments — the
volume's own venv renders

```
reader_thread_gm4      b272115637f784ad63c6fb2483e0b0ac3d6381901a096dc1cb5406b81a46c8cd
reader_thread_gm4_v2   9d281bc80f18c91b6b0c32cbcdb37540504be887887d0dd1f1ab1c25841250c5
parse_reply module 4b466bec6278c80f
```

byte for byte what this Mac renders.

**`gpuIds` was read back before the first job, and that is the contract's option B in one line.**
Endpoint creation is free and only requests bill, so the class came back from the create call itself:
`ADA_24`, the class requested — where probe-a asked for `NVIDIA L4` and got `AMPERE_24`.

### 4.2 The handshake

```
handshake OK · worker READER · commit f0fd745cbf711072c7dd79deb4477459bfae931a
```

`serving_config: READER`, `merge_state: base-no-adapter`, adapter `None`, `max_new_tokens: 2000`,
`enable_thinking: false`, revision `842da379…`, **`reader_prompt_sha256` a map of BOTH registered
texts**, and a runtime of **NVIDIA GeForce RTX 4090, 24 564 MiB**, torch 2.8.0+cu128, transformers
5.14.1, bitsandbytes 0.50.0, peft 0.20.0. Boot to first answer: **2 min 59 s** — against probe-a's
6 min 13 s, on a warm cache and flash-boot.

### 4.3 The warm-up, and the number the whole contract was built around

```
  @mandziak:3701                       3 payable ·    9.1 s worker · parsed
  @VARUS_channel:10451                 4 payable ·   19.0 s worker · parsed
  @tarilka_malyuka:715                 4 payable ·   26.3 s worker · REFUSED (missing field: evidence)
```

**62.276 s billed for 3 threads = 20.759 s a thread, 5.661 s a payable comment.**

| | probe-a (L4) | probe-b (4090) | ratio |
|---|---|---|---|
| seconds per thread | 54.806 | **20.759** | **2.64×** |
| seconds per payable comment | 14.947 | **5.661** | **2.64×** |
| registered break-even | | **2.007×** | cleared |

| | seconds | usd |
|---|---|---|
| remainder by thread (20 unread) | 415.2 | 0.1273 |
| remainder by payable comment (123 unread) | 696.4 | **0.2136** ← binding |
| setup + warm-up already billed | | 0.0631 |
| **projected total** | | **$0.2767** of $0.35, headroom $0.0733 |

**VERDICT GO.**

### 4.4 The run

20 threads in 12 min 23 s. **727.664 billed worker seconds over the whole 23, 31.638 s a thread** —
higher than the warm-up's 20.759 because the warm-up's threads are the small ones (3/4/4 payable
against the population's mean of 5.8), which is exactly why the per-payable projection was registered
as the one that binds. The largest thread, `@VARUS_channel:10613` at 10 payable, took 78.5 s.

**Thirteen of the 23 replies parse; ten are refused, across six shapes, and NOT ONE of them is a
defect v2 closed** (Dv404):

| shape | n | what came back |
|---|---|---|
| `signals is not a list` | **4** | `"signals": {}` — an empty OBJECT where the schema asks for `[]`. **All four are noise threads**, i.e. exactly where «nothing here» is the correct answer |
| `missing field: entities` | 2 | the answer split into **two top-level JSON objects**: `{thread, post_summary, discussion_summary}` then `{entities, signals, per_comment, noise}`. `parse_reply` reads from the first brace |
| `missing field: evidence` | 2 | a `from_post: true` signal with **no `evidence` key at all** — v2's own rule, half-obeyed |
| `noise is not a list` | 1 | `{"47896": {...}, "47897": {...}}` — a map keyed by msg_id. Dv393's shape, one field over |
| `signals.aspect is not a string` | 1 | `"aspect": null` |

`finish_reason: length` on zero replies; the 2 000-token ceiling never fired.

### 4.5 Deleted, and proven

```
$ runpodctl serverless delete lfqvip37lpgcii → {"deleted": true}
$ runpodctl template delete ueasek6tk6       → {"deleted": true}
$ runpodctl serverless list                  → []
$ runpodctl pod list -a                      → []
$ runpodctl network-volume list              → [ qw4nwleanc · mp-srv2 · 100 GB · EU-RO-1 ]
```

The same three listings were taken BEFORE anything was created and read the same, which is what makes
this a deletion proof rather than a hope. **`results/spend_probe_b.json` is the only `spend_probe_b*`
file in `results/` — Dv392's fix, in production, on the write path that created it.**

---

## 5. The bars

### 5.1 As registered

| bar | threshold | result | |
|---|---|---|---|
| 1 flagships | 5 of 5 cases | **2 of 5** | F4, F5 answered; F1 missed (1 of its 3 signals found), F2 and F3 missed |
| 2 entity cases | 4 of 4 | **2 of 4** | **E1 ✅** and **E4 ✅** (both threads) — the two the injection bought; E2, E3 missed |
| 3 noise | 0 signals | **0 — PASSES** | over 5 threads, and see §5.2 |
| 4 per-comment | ≥ 0.80 over 14 | **0.357** (5 agreed · 2 disagreed · 7 absent) | |
| 5 time and cost | ≤ $0.35 all-in | **$0.2907** at the deletion reading | see Dv407 |

**Three of the four gating bars fail. The headline is not that — it is which failures are the reader's
and which are the interface's.**

### 5.2 The pass that is a count over nothing

`results/reader_probe_b_refusals.json`, post-run and gating nothing:

```
3_noise          passed=True over 1 threads with a verdict and 4 without
```

Bar 3 counts SIGNALS, and a refused reply has none. Four of its five threads — `@retsepty:7312`,
`7325`, `7327` and the injected `@sashafitnesslife:3939` — returned `"signals": {}` and were refused,
so they contribute a zero that is indistinguishable from a clean pass. **The bar's 0 is computed over
one actual answer** (`@VARUS_channel:10366`, N2, which really did raise no signal and resolved one
entity). This is [[the_empty_class_eats_the_parse_failures]] arriving one level up, at the bar rather
than at the row, and it means the only bar that passed proves the least.

Going the other way, the same join says which failures are not the reader's:

```
1_flagships      missed on a refused reply: ['F3'] · missed while the reply parsed: ['F1', 'F2']
2_entity_cases   missed on a refused reply: ['E2', 'E3'] · missed while the reply parsed: []
4_per_comment    absent on a refused reply [47899, 47902, 20664] · absent while it parsed [21601, 21629, 580124, 578951]
```

**Both entity cases that failed failed on unreadable replies**, and one of them —
`@VARUS_channel:10348`, E3 — carries the correct answer in the object beside the one the parser read:

```json
{ "name": "Varus", "msg_id": "20664", "subject_type": "сеть_ритейлер",
  "reading": "мережа супермаркетів", "quote": "Зайшла в Varus на Деміївській" }
```

### 5.3 What the interface costs, measured

`results/reader_probe_b_coerced.json` — each refused reply through an ENUMERATED list of
container-only repairs (two top-level objects merged; an empty object read as an empty list; a map
keyed by the id read as the list it describes; a null aspect dropped). No field invented, no value
changed, no taxonomy word mapped. An absent `evidence` on a `from_post` signal is deliberately **not**
repaired: an evidence list is what a finding is made of, and supplying one would be writing the answer.

| | as run | coerced | + collapsed vocabulary |
|---|---|---|---|
| replies parsed | 13 of 23 | **19 of 23** | — |
| bar 1 flagships | 2 of 5 | 2 of 5 | **3 of 5** |
| bar 2 entity cases | 2 of 4 | **3 of 4** | — |
| bar 3 noise | 0 over **1** real verdict | 0 over **5** real verdicts | — |
| bar 4 per-comment | 0.357 | **0.429** | **0.643** |

**Not one bar clears its threshold under any reading.** The reading gap is real and it is not only
the interface: even with every container repaired and the two `категория` words collapsed, bar 4 is
0.643 against 0.80 and bar 1 is 3 of 5.

### 5.4 The vocabulary split, confirmed in production

Registered before the run (§2.3) and observed in it: msg **21599**, gold `категория`, reader
`категория_личное`. The collapsed reading moves bar 4 from 0.357 to 0.429 as run and from 0.429 to
0.643 coerced — one row and one flagship case that turn on a word two authorities disagree about.

The other disagreement is a genuine one: msg **580129**, gold `категория_личное`, reader
`молочный_бренд`.

### 5.5 The injected four, reported apart

| thread | case | read | entities | signals |
|---|---|---|---|---|
| `@matusi_ukr:22242` | E1 | parsed | **5** | 0 |
| `@mandziak:3684` | E4a | parsed | 0 | 0 |
| `@mandziak:3689` | E4b | refused (`aspect: null`) | — | — |
| `@sashafitnesslife:3939` | N3 | refused (`signals: {}`) | — | — |

**E1 is answered** — «Гармонія» resolved as `не_наш_рынок`, the case probe-a could not show the
reader at all because SPEC 3.21 (1)'s marker rule removes the thread before payment. E4 is answered
on both threads: neither reports a Varto entity, which is the ruling. That is 2 of the 4 entity cases,
bought for the price of four threads, and it is the strongest argument in this report that the
question the marker rule raises belongs at the sitting.

---

## 6. Findings

1. **The container is still the whole story, and it moved.** v2 closed both defects probe-a measured
   and neither returned. What refused ten of 23 replies is the SAME class of defect in five other
   places: an empty object for an empty list, a map for a list, an answer split across two top-level
   objects, a null where a domain word belongs. A schema stated in prose fixes the field it names and
   nothing beside it. The cheap decision the sitting can take is a tolerant reader for CONTAINERS
   only — it is worth **6 replies and one entity case**, measured, and it changes no taxonomy.
2. **A bar that counts things is a bar an unreadable reply passes.** Bar 3's «0 signals» is the only
   gate this run cleared and it is the one that proves least: four of its five threads had no verdict.
   Any bar whose predicate is «zero of X» has to be scored over answers that exist, and the
   registration should say so in the bar rather than in a post-run analysis.
3. **The four injected threads did their job.** E1 answered, E4 answered on both threads, and N3 read
   as an empty thread exactly as §2.3 predicted. 2 of the 4 entity cases in this report exist only
   because the run bought threads the production gate removes — which is a measured argument for the
   sitting's marker-rule question, not a claim that the gate is wrong.
4. **The card was the cheap lever and it worked exactly as priced.** 2.64× against a 2.007×
   break-even, same $/s, one flag. probe-a's whole $1.87–$4.18 projection for the window was a
   property of a card nobody chose: on this one the 111-thread window projects to **$0.71** by thread
   and **$1.58** by payable comment — still above the phase remainder, but no longer by 4×.
5. **The reading gap is real and smaller than the interface gap.** Coerced and collapsed, bar 4 is
   0.643 and bar 1 is 3 of 5. The reader finds flagship signals it is shown (F4, F5, F1a) and misses
   others in threads it parsed (F1b, F1c, F2a; 4 absent per-comment rows in parsed threads). That is a
   prompt question for the sitting, and it is now measurable in one $0.06 rung rather than a $4 one.
6. **A pre-registration's own constants can be stale by the time it is written.** probe-a's report
   closed at «$0.0750 spent» and the guard read **$0.0944** for the same step the next day, with
   nothing running. The setup constant was re-derived from the settled figure before the endpoint
   existed (Dv402) — and probe-b is doing the same thing right now, $0.2907 at deletion and $0.3132
   twenty minutes later (Dv407).
7. **The contract's baseline was not reproducible and the cause was upstream.** `make check` was
   2 517 / 4 failed before this contract began, because a team-lead edit to the plan moved a sha two
   frozen probe-a records pin. Nothing was wrong with either record; what was missing was a seal.

---

## 7. Deviations

- **Dv397** — `docs/PLAN-comment-signals.md` §3's schema example moved (`сеть` → `сеть_ритейлер`,
  `категория` → `категория_личное`) between probe-a's close and this contract, reddening four tests
  across two frozen probe-a records. Sealed with a `MOVED` tuple and a witness, never re-pinned; the
  gold rebuilds byte for byte. [cause: authority-edit]
- **Dv398** — the gold scores 12 cells on `категория` and, after Dv397, only `docs/REFERENCE-signals-w1.md`
  still uses that word: 8 of 14 per-comment rows and 4 of 7 flagship signals. Registered as a reported
  collapsed reading, never as a moved bar; confirmed in production on msg 21599. [cause: authority-conflict]
- **Dv399** — the population enumerates to **23 threads / 134 payable comments** against the
  contract's «~16–19». The contract's own instruction is «enumerate, don't estimate»; the six S-list
  rows resolve to four uncounted posts and the warm-up adds three. [cause: brief-vs-enumeration]
- **Dv400** — N3 `@sashafitnesslife:3939` reaches the reader with **0 payable comments**: 29 of 29
  removed by the gate's plus-spam silencer. Registered inside bar 3 as the contract names it, and
  reported beside it as a cell that cannot be non-zero. [cause: population-reachability]
- **Dv401** — probe-a's driver double-counted the warm-up: it projected the whole population and
  compared it against the cap MINUS the warm-up. 2.7% of the cap at 111 threads, 13% at 23. Corrected
  here; probe-a's own STOP is unaffected. [cause: arithmetic]
- **Dv402** — probe-a's SETTLED cost is **$0.0944**, not the $0.0750 its report closed with. The
  registration's setup constant was re-derived ($0.0343 → $0.0440) and the break-even moved 1.946× →
  2.007×, before any endpoint existed. [cause: unsettled-billing]
- **Dv403** — the driver prints `info["runtime"]["gpu_name"]` and the worker answers `runtime.gpu`, so
  the handshake line reads `runtime None` and `non_gating.gpu` is `null` in the verdict. The card is
  in `results/reader_probe_b_run.json :: worker.runtime.gpu` and in this report. NOT fixed mid-flight:
  it is a print on the money path of a run that was open. [cause: field-name]
- **Dv404** — six reply shapes refused 10 of 23 replies, none of them a defect v2 closed: `signals: {}`
  (4), two top-level objects (2), a missing `evidence` on a `from_post` signal (2), `noise` as a map
  (1), `aspect: null` (1). Frozen and reported. A seventh shape appears once —
  `@VARUS_channel:10360` emits the second half as bare key-value fragments with no enclosing braces —
  and is deliberately not reconstructed, because at that point a repair authors structure.
  [cause: schema-wording]
- **Dv405** — bar 3 PASSES with four of its five threads carrying no verdict. The bar counts signals
  and a refused reply has none. [cause: empty-class]
- **Dv406** — the contract's «phase remainder $1.08» is not what the guard reads: **$0.9882** of
  $33.00 at the start of this session. The contract says to read the guard and that is what was done;
  $0.35 fits either way. [cause: brief-vs-instrument]
- **Dv407** — probe-b's spend is still settling: **$0.2907** at the deletion reading, **$0.3132**
  twenty minutes later, against a $0.35 cap. Nothing is running and nothing can be done about it now;
  the final reading is in §Verify and the operator should re-read the guard once more tomorrow.
  [cause: unsettled-billing]
- **Dv408** — `make check` is RED for exactly as long as a registration is uncommitted, because the
  driver's own guard refuses a registration that differs from HEAD. The verifier has to be read after
  the commit that carries a registration change, not before it. [cause: guard-vs-verifier]
- **Dv409** — the staging pod cost **$0.0066** in 1 min 39 s (RTX 2000 Ada at $0.240/h), against
  probe-a's $0.0097 in 2 min 26 s. A warm volume needs a fetch and a reset and nothing else.
  [cause: estimate-vs-measurement]
- **Dv410** — `ruff format` moved `prompts.py` AFTER the dashboard export had been regenerated from
  it, so two pinned artefacts had to be re-derived a second time. Dv363's rule, one order deeper: run
  the formatter before regenerating anything that hashes the file it formats. [cause: tooling-order]

---

## 8. Process signals

1. **A go/no-go's arithmetic is an instrument and deserves the same scrutiny as a prompt.** v1's
   double-count was invisible at 111 threads and decisive at 23. The fix was four lines; finding it
   took reading the docstring against the code, because the docstring already said the right thing.
2. **The bars had never run.** Four scorer functions, four hand-computed unit tests, one registration
   — and not one of them had ever seen a verdict, because the previous run stopped before its bars.
   Driving the whole scoring path on synthetic verdicts AND on the previous run's real replies cost
   $0 and would have caught a raise after the money was spent.
3. **`gpuIds` is free and was the difference between this run and probe-a's.** Endpoint creation
   bills nothing; only requests do. Reading the class back from the create call turned «a faster card
   would help» into «the class requested is the class allocated» before a single second was billed.
4. **A container defect does not stay in the field you fixed.** v2 closed `entities` and the model
   moved the same shape into `signals`, `noise`, and the framing of the whole reply. The lesson is not
   «write more schema prose» — it is that the parser's tolerance for CONTAINERS is a decision to take
   once, deliberately, and separately from its strictness about DOMAINS.
5. **A settled bill is a different number from a reported one.** probe-a closed at $0.0750 and cost
   $0.0944; probe-b closed at $0.2907 and is at $0.3132 an hour later. Any cap read at deletion time
   is optimistic, and a contract that plans to spend ≥85% of its cap should either leave that margin
   or say it is spending against a number that will still move.

---

## 9. What this leaves the operator

**Spent: $0.3132 of $0.35** (still settling — Dv407). **Phase 4: $0.9882 remaining of $33.00** at the
start, to be re-read.

**Decided by the run:** the card question is closed — `ADA_24` is 2.64× the L4 at the same price, and
every future projection should name it. The window of 111 threads projects to **$0.71 by thread** /
**$1.58 by payable comment** on this card.

**Open, and each one is now cheap:**

| | what it costs | what it buys |
|---|---|---|
| **A. A container-tolerant reader** — accept an empty object for an empty list, a map for a list, and a split answer; DOMAIN strictness unchanged | $0, plus a re-score of the evidence already bought | +6 replies and +1 entity case, measured. It is a parser decision, not a prompt one, so it needs no new instrument sha — but it does need a registration, because it changes what «refused» means |
| **B. Re-read the same 23 under a v3 prompt** that says «one JSON object» and «`[]` for nothing» | ~$0.08 at the measured rate | whether the framing defects are promptable at all. A new instrument, a new registration |
| **C. The reading gap** — F1b, F1c, F2a and four absent per-comment rows in threads that parsed | a design sitting, $0 | what the reader is actually missing, once the interface stops accounting for most of it |
| **D. The sitting's two standing questions** | $0 | the marker rule (E1/E4/N3 exist only because this run bought them) and `категория` vs `категория_личное` |

**What no longer needs deciding:** whether the bars can be computed — they were, all four, on a
population that carries every case the operator made obligatory.

## Verify

```
$ make check                       # at ac276fb
2562 passed, 2 skipped in 180.52s (0:03:00)
$ ruff format --check .
306 files already formatted

$ HF_HUB_OFFLINE=1 PYTHONPATH=src python3 scripts/preflight_serving_guards.py | grep -c '^PASS'
63                                  # and no FAIL line

$ PYTHONPATH=src python3 scripts/probe_b_population.py
probe-b population: 23 threads · 134 payable comments · 4 injected
  digest ccef35fa4b9c771f…

$ runpodctl serverless list && runpodctl pod list -a
[]
[]

$ PYTHONPATH=src python3 scripts/score_reader_probe_b.py
  outcome GO · 23 of 23 threads read
  bar 1_flagships                SCORED — False
  bar 2_entity_cases             SCORED — False
  bar 3_noise                    SCORED — True
  bar 4_per_comment_agreement    SCORED — False
  replies: {'parsed': 13, 'refused': 10, 'refusals_by_cause': {'missing field: evidence': 2,
   'missing field: entities': 2, 'noise is not a list': 1, 'signals.aspect is not a string': 1,
   'signals is not a list': 4}, 'finish_reason_length': 0, 'signal_bearing': 7, 'no_signal': 6, …}

$ PYTHONPATH=src python3 scripts/probe_b_coercion.py
  replies as run 13/23 · coerced 19/23
  1_flagships                as run 2 · coerced 2
  2_entity_cases             as run 2 · coerced 3
  4_per_comment_agreement    as run 0.357… · coerced 0.428…

$ python3 scripts/runpod_guard.py --step probe-b --step-cap 0.35
PHASE 4 SPENT     $32.0118 of $33.00
REMAINING         $0.9882
PROBE-B SPENT      $0.3132 of $0.35  (anchor $22.98 from runpod_balance_at_probe-b_start)

$ ls results/spend_probe*
results/spend_probe_a.json  results/spend_probe_b.json     # Dv392: one step, one ledger
```

**The per-commit rule, stated rather than listed** (a list cannot name the commit that carries it):
the verifier ran on the tree of every commit that moves code, a test or a result artefact. Two
commits move only documentation or vault files (`2bdb428`, `4a00952`) and nothing in `tests/` opens
`docs/reports` or `knowledge/`. `f0fd745` moves only the step anchor, and the two tests that read the
real `results/spend_phase4.json` select their row by timestamp rather than by position. One commit —
`72a9f40` — was made while `make check` was red for the reason Dv408 names, and the tree is green at
that commit: the driver refuses a registration that differs from HEAD, so the verifier can only be
read once the registration is committed.

**Commits:** `d19d454` · `2bdb428` · `692f161` · `4a00952` · `5f93116` · `8bf5a14` · `8fd1b44` ·
`a5089e0` · `72a9f40` · `6c975b4` · `f0fd745` · `275fefb` · `ac276fb`, plus this report's own.
