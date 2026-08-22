# lora-c-prep — the data and the registration for the rationale-supervised LoRA line

**Everything below cost $0. No pod, no endpoint, no paid call of any kind.** Both team-lead review
gates are OPEN and D0 stops at them; the registration is a DRAFT.

## Read back — one line each

- **The four error classes and where each was measured.** brand ↔ retailer — F2, msg `580124`, pass 1
  called the row `сеть_ритейлер` where the gold says `молочный_бренд`, which is why bar 1's F2a was
  unreachable in r2. A retailer in a non-dairy context — N2, `@VARUS_channel:10366`, four rows pass 1
  called `сеть_ритейлер` in a giveaway thread and the team lead's labels on all 12 are `null`; this
  is bar 3's two signals. Non-dairy «brands» — a café, a stationery brand and a throat spray, all
  read as `молочный_бренд`, which is `subject_doubt`'s highest rate at **21.4 %**. Mention-vs-about —
  18 of the 52 `не_наш_рынок` rows on holdout-100 pulled into `категория_личное`.
- **What v3 adds and where it lives.** One clause after v2's two: write ONE Ukrainian sentence,
  ≤ 160 characters, saying what the comment is ABOUT as against what it MENTIONS and naming the
  deciding cue, in the field `rationale`, BEFORE the label. It lives in a NEW module
  `src/market_pulse/pass1_v3.py`; `prompts.py` is pinned by 38 records and is not touched.
- **The shared pool and what it excludes.** ONE pool for every leg: the 650 team-lead labels MINUS
  holdout-100 MINUS every row of the 16 reference threads. `650 − 100 − 41 + 6 = 515` — the two
  exclusions overlap on six rows. Base v2, base v3, arm A and arm B are all rendered against it, so
  the paired table compares prompts and adapters and never neighbours.
- **The four legs and why base v3 exists.** base v2 (the re-measured BEFORE column) · base v3 (the
  rationale clause alone, no adapter) · arm A (QLoRA on the real rows) · arm B (arm A's rows plus the
  synthetic). Without base v3 nothing separates «the adapter learned» from «a sentence of reasoning
  helped», and the two have different consequences for the next line.
- **Who writes rationales, who reviews, and what STOPS.** Claude Code writes them from
  `build_pass1_label_pack.codebook()` and the team lead's label; the team lead reviews every «our»
  row and 40 boundary rows and writes `docs/reviews/lora-c-rationales-verdict.md`. Until that file
  exists no rationale is rewritten, `rationale_reviewed` stays `false` on all 515, and D0 stops.
- **What synthetic may never touch.** The neighbour pool, any eval set, arm A, the holdout and the
  gold. No synthetic text may share a word 6-gram with a labelled row, a holdout row, a
  reference-thread comment or the gold, and the four lists are printed EMPTY.
- **The bar per arm and the report-only rows.** holdout-100 ≥ 64 AND end-to-end bar 1 = 5 of 5 AND
  bar 3 = 0 — all three or RED, one attempt. Base v3 takes no bar. Report-only: the
  `не_наш_рынок → категория_личное` cell (18 before), «our» on holdout (6/8), dev-200 as training
  FIT, the gold-14 census row (the sixth look), the per-class tables, pass 2's DROP and doubt tables,
  and the arm-A-vs-arm-B ablation.
- **Why the money block stays open.** A number without a run behind it reads as a measurement forever
  after — r1 of `pass1-window` registered a rate it had not measured and the figure outlived its own
  correction. `lora-c-run` derives the price and seals it.

## Step 0 — baselines, at the opening tree

```
## Baselines — instrument output, 2026-08-22T14:04:29+00:00

- head: 664c3ae50d9d on main
- porcelain:
     M docs/STATUS.md
     M knowledge/daily_logs/2026-08-22.md
     M knowledge/hot.md
     M knowledge/index.md
    ?? docs/PROMPT-lora-c-prep.md
- census: brain-census: 10.1Ktok boot tax
- suite: 3608 passed / 2 skipped — whole suite, stamped 2026-08-22T13:43:17+00:00 at 664c3ae50d9d
- boot files: ~/.claude/CLAUDE.md 1974 B · ~/CLAUDE.md 23 B · CLAUDE.md 4581 B · knowledge/hot.md 10570 B · MEMORY.md 23163 B = 177 lines / 22823 UTF-16 units
- preflight: 1547 pinned paths · 2752 pins · 125 records — 1511 match every pin on them, 36 carry an older pin
```

`make check` re-run live at that tree: **3 608 passed, 2 skipped**, exit 0. The first commit was the
team lead's files verbatim — `docs/STATUS.md`, `docs/PROMPT-lora-c-prep.md` and the previous
session's vault tail — staged by path, never `-A`.

## D0 — the training set and the rationales

### The pool is 515, and the arithmetic is the finding

| | |
|---|---|
| team-lead labels | 650 |
| − holdout-100 | 100 |
| − rows of the 16 reference threads | 41 |
| + the overlap, added back once | 6 |
| **= the shared pool** | **515** |

The contract expects ~430. It is 515 because **the two exclusions overlap**: six holdout rows sit
inside reference threads, and subtracting both sets independently removes those rows twice. The 16
reference threads are derived from `results/reader_gold_w1_r2.json` — `flagships` + `entity_cases` +
`noise_threads`, keyed `channel:post_id`; E4a and E4b are two threads and one case, so 5 + 5 + 6
rows resolve to 16 distinct threads. **8 of them carry labelled rows**, exactly as the contract
says.

Distribution of the pool: `не_наш_рынок` 272 · `null` 165 · `категория_личное` 40 ·
`сеть_ритейлер` 37 · `молочный_бренд` **1**. «Our» rows 41 = **7.96 %**, against the contract's ~7 %.

### 506 rows render; 9 do not, and that is the first STOP

`build_pass1_fewshot_packs.neighbours` refuses a query when a class has no candidate outside the
query's own thread — a four-example block is a different instrument from a five-example one, and the
function says so itself. The pool holds **one** `молочный_бренд` row, `@VARUS_channel:10367:20766`;
the 650 hold two and **the holdout took the other** (`@mandziak:3721:48445`). So every one of the
nine pool rows of `@VARUS_channel:10367` is unrenderable, and two holdout rows of the same thread
fall out of eval set E.

**The rendered training set therefore has ZERO real `молочный_бренд` positives.** Distribution:
`не_наш_рынок` 267 · `null` 165 · `категория_личное` 40 · `сеть_ритейлер` 34.

Four remedies are named in `results/lora_c_data.json::unreachable` and **none is taken** — each
breaks something the contract states, and the choice is the operator's:

1. render those rows with FOUR examples — `neighbours()` itself calls that a different instrument;
2. allow the query's own thread as a candidate for that class alone — a per-class rule, and for the
   `молочный_бренд` row itself it hands the model its own answer;
3. draw the example from the EXCLUDED set — it leaks a holdout or reference-thread comment into a
   training and an inference request;
4. drop the eleven rows — arm A then has zero real positives of that class and the holdout
   denominator moves off the registered 100.

Remedy 1 is also a remedy for the SECOND stop below — but it does not close it, and the report says
so with the measurement rather than with the intention.

### The class-balance rule, and why the second one applies to nothing

lora-b's rule is inherited by CALL, not by copy: `train_qlora.class_weights` is the function the
trainer samples with, `w_c = N/(5·n_c)` capped at 8.0.

| class | rows | weight | expected draws / epoch |
|---|---|---|---|
| `не_наш_рынок` | 267 | 0.379026 | 101.20 |
| `null` | 165 | 0.613333 | 101.20 |
| `категория_личное` | 40 | 2.530000 | 101.20 |
| `сеть_ритейлер` | 34 | 2.976471 | 101.20 |

The contract asks for a SECOND rule — «cap the majority class by sampling so no class is under 8
rows per epoch-equivalent». The arithmetic says the first rule already delivers it: expected draws
are `n_c · w_c = min(N/5, 8·n_c)`, so the majority class is capped at a fifth of the epoch **by
construction** and the floor can only bind on a class with fewer than 8 rows. **Applied: none.**
The one class that would have hit the floor is the one with zero rendered rows.

### 515 rationales — and the measurement that says they are not the label in a costume

Every rationale is one Ukrainian sentence, ≤ 160 characters, naming a cue that occurs in ITS OWN
comment, in one of three shapes: «коментар ПРО X (cue: …)» 339 · «коментар ні про кого (cue: …)»
160 · «лише ЗГАДУЄ X; насправді про Y (cue: …)» 16.

**The check that matters is the distinct-cue rate.** If a rationale were derivable from the label,
the target would still be a deterministic function of the class and the model would learn
label → template → label — line B's failure wearing a sentence.

| class | rows | distinct rationales | distinct cues |
|---|---|---|---|
| `не_наш_рынок` | 272 | 268 | **267** |
| `null` | 165 | 159 | 159 |
| `категория_личное` | 40 | 40 | 40 |
| `сеть_ритейлер` | 37 | 36 | 36 |
| `молочный_бренд` | 1 | 1 | 1 |
| **all** | **515** | **504** | **501** |

Every cue is checked back into its comment on whitespace-collapsed, case-folded text, by
`build_lora_c_data.joined()`, which STOPS on a miss with the message *«a rationale whose cue is not
in the text was written from the LABEL»*.

### The SFT row is the v3 inference request, byte for byte

`build_pass1_sft.target_for` is CALLED, not copied — it owns the `+1` END-offset boundary that
carries the supervised span one character past the `subject_type` value's closing quote. Prefixing
the rationale shifts every offset of the head by `len(prefix) − 1`, so the supervised span is **the
rationale AND the label**: the loss lands on the reasoning before it lands on the class, which is
the whole of the line. `subject_id` and `stance` stay written and unsupervised, exactly as in lora-b.

```
{"rationale": "коментар ПРО сам сир із допису — як його доводити після покупки (cue: «цей сир»)", "msg_id": 20766, "subject_type": "молочный_бренд", "subject_id": null, "stance": null}
                                                                                                                                                                      ^ learn_chars
```

`tests/test_lora_c_prep.py::test_the_sft_prompt_is_the_v3_inference_request_byte_for_byte` drives
the builder and re-renders every row through `pass1_v3.pass1_messages_gm4_v3`, comparing the STRING
and not only its sha.

Widest rendered request **9 228 characters** against `prompts.PASS1_MAX_INPUT_CHARS` = 12 000 —
headroom 2 772, median 5 565. No new ceiling constant was needed.

### REVIEW GATE 1 — STOP

`docs/reviews/lora-c-rationales-sample.md`: **40 «our» rows** (every one, no sampling) and **40
boundary rows**, seed `20260822`, in two tiers.

**The boundary draw found the instrument before it found the rows.** The shipped
registry-and-watchlist matchers find **zero** retailer or brand mentions across all 466 non-«our»
rows. `config/registry.yaml` spells the chain `Varus` in Latin; the comments write «Варус»,
«варусі», «Варусу». Running the registry names through the lexicon's own stem+endings screen
(`yield_screen.compile_categories`) reaches «Сільпо» and «АТБ» and **still not «варусі»** — no file
in this repository carries that source's Cyrillic spelling.

So tier A is named by TWO instruments and the record says which contributed what:
`brands.find_watchlist_brands` over the sealed watchlist (ruled revision, `carrier="comment"`) —
**0 hits** — and pass 1's own window answer where it read `сеть_ритейлер` / `молочный_бренд` **and**
the `subject_id` it wrote occurs in the comment — **9 hits**. Tier B is the same rule with pass 1's
reading unrestricted: 104 found, 31 drawn under the seed to make up the 40.

**Tier A is the four error classes, exactly:**

| pair | team lead | pass 1 read | comment |
|---|---|---|---|
| `@VARUS_channel:10356:20696` | `сеть_ритейлер` | `молочный_бренд` «варус кафе» | А варус кафе? |
| `@VARUS_channel:10455:21201` | `сеть_ритейлер` | `сеть_ритейлер` «Омега» | …почему Окко у них эту сеть не захотели покупать… |
| `@VARUS_channel:10465:21199` | `сеть_ритейлер` | `сеть_ритейлер` «варусі» | В нашому варусі поки ту піцу дочекаєшся… |
| `@VARUS_channel:10466:21387` | `null` | `сеть_ритейлер` «Новус» | …два найвідданіші фанати Новус… |
| `@VARUS_channel:10466:21390` | `null` | `сеть_ритейлер` «Варусу» | Більше хвилююсь… за розіграш Варусу… |
| `@mandziak:3702:48171` | `не_наш_рынок` | `молочный_бренд` «Кола Зеро» | …щодо Кола Зеро: … |
| `@matusi_ukr:22131:578253` | `не_наш_рынок` | `молочный_бренд` «1 вересня» | …ручки (ми купували «1 вересня»)… |
| `@matusi_ukr:22158:578055` | `не_наш_рынок` | `сеть_ритейлер` «Гамета» | Гамета. Возле первого роддома |
| `@matusi_ukr:22158:578081` | `не_наш_рынок` | `молочный_бренд` «Uakino» | Uakino |

**D0 stops here for the rationales.** `docs/reviews/lora-c-rationales-verdict.md` does not exist; all
515 rows carry `rationale_reviewed: false`; nothing is rewritten.

## D0 — the 160 synthetic rows for arm B

40 per error class, and the four classes are the ones pass 2 measured. **Balance is 8/8/8/8/8 inside
every class — spread 0 against the contract's ±2.** Synthetic that carries a prior teaches the
prior, which is the one thing line B already proved.

**Contamination, printed as four EMPTY lists** on word 6-grams through `market_pulse.synthetic` (the
shipped inverted index over casefolded `\w+` tokens, so the comparison is already normalised):

| corpus | rows | collisions |
|---|---|---|
| labelled rows | 650 | `[]` |
| holdout rows | 100 | `[]` |
| reference-thread comments | 106 | `[]` |
| gold quotes | 67 | `[]` |

Frames: the commonest two-word opening covers **5 %** of rows and the commonest closing **1 %** —
two hundred rows on one frame are pairwise distinct and still one machine, and a shingle check
cannot see it.

**The register is a distribution, not an adjective, so it is measured on both sides with the same
code — and four of six axes do NOT match.**

| axis | the window's 515 rows | these 160 | delta | matched at ±3 |
|---|---|---|---|---|
| carries an emoji % | 19 | 19 | 0 | ✅ |
| opens lowercase % | 6 | 6 | 0 | ✅ |
| no terminal punctuation % | 59 | 54 | −5 | ❌ |
| carries a question mark % | 13 | 8 | −5 | ❌ |
| words, median | 11 | 7 | −4 | ❌ |
| characters, median | 68 | 40 | −28 | ❌ |
| alphabet ua / ru / neutral % | 66 / 14 / 19 | 71 / 11 / 18 | ≤ 5 each | — |

The length gap is **deliberate and named rather than smoothed**: the contract asks for «short,
colloquial» rows, and the window's tail is 40–190-word recipe and advice posts (max 192 words
against synthetic's 20). Writing those synthetically would be a different instrument, not a longer
version of this one. Questions are under-represented because three of the four error classes are
statements about a subject and only one is naturally a question.

### REVIEW GATE 2 — STOP

`docs/reviews/lora-c-synthetic.md`: all 160 rows with a blank verdict column, grouped by error class
with each class's label counts above it. `docs/reviews/lora-c-synthetic-verdict.md` does not exist;
every row carries `reviewed: false`; nothing is dropped or rewritten.

## D0 — the eval packs

### Eval set E: 200 rows, 198 rendered

`100 + 106 − 6 = 200`. The same overlap as the pool, in the other direction: six holdout rows are
payable comments of reference threads. The two that do not render are the holdout rows of
`@VARUS_channel:10367` — the same thread the training set lost nine rows to.

Two legs in ONE pack, paired on identical instances the way `results/pass1_dev_pack.json` carries
`base`/`v2`. The builder refuses if the two legs carry different instances, if any item renders
identically under both prompts, if an item is shown a neighbour from its own thread, or if a
synthetic thread reaches either the pool or E.

| leg | task | items | widest | median | headroom under 12 000 |
|---|---|---|---|---|---|
| v2 | `pass1_comment_gm4_v2` | 198 | 7 781 | 4 582 | 4 219 |
| v3 | `pass1_comment_gm4_v3` | 198 | 8 894 | 5 704 | 3 106 |

**All 14 gold rows are inside E** — they are payable comments of the reference threads — and they
take **no bar**: a report-only census row, the SIXTH look, per `docs/STATUS.md` п. 1 (д).
**dev-200 is not in E**: it is training data now, and its agreement is reported as training FIT only.

### The pass-2 pack, and the test the contract names for it

`scripts/build_lora_c_pass2_pack.py` takes the pass-1 out-file as an ARGUMENT, which is why it is a
sibling: `build_pass2_pack.filtered` names the window's two out-files through
`census_pass1_window_r2.union_view` and is pinned by a sealed record. Everything else is CALLED —
`census_pass1_window.pass_2_filter`, `entity_block`, `unit`, `membership`.

**Its test passes.** Driven at $0 over the window's own out-files and cut from 79 threads to the 11
reference threads that carry a filtered row (46 rows):

```
threads selected: 11 of the 16 reference threads
  replies parsed 11 · refused []
  bar 1: 4 of 5  (r2 measured 4 of 5)
  bar 3: 2 signals  (r2 measured 2)
  AGREES: True
```

Both bars read only reference threads, so the cut may not move them — and now that is a measurement
and not an argument. Bar 2 is **inherited and reported «held»**: its cases are resolved from the
reader's bought verdicts, which no pass-1 adapter moves.

## D0 — the registration draft

`results/prereg_lora_c.json`, state **DRAFT**, frozen by `lora-c-run`'s first `pod create` and by
nothing before it. Rulings (в) and (к) are quoted verbatim and **grepped back into `docs/STATUS.md`
on every build**; a paraphrase raises. `rank` 16, `alpha` 32, `learning_rate` 1e-4, `epochs` 2 are
all READ from `config/qlora.yaml` and never typed.

### The bar, per arm

`holdout-100 ≥ 64 AND bar 1 = 5 of 5 AND bar 3 = 0` — all three or RED, ONE attempt, no retry and no
tuning after any eval output is seen. Base v3 takes no bar. **The reachable maximum on holdout is 98
and not 100**, because of the two unrenderable rows; the bar of 64 is still reachable with 34 to
spare. Bar 1 is registered at 5 and not at 4 for a reason: F2a was unreachable in r2 *because pass 1
labelled its only cited row `сеть_ритейлер`*, and a pass-1 adapter that relabels that row is exactly
what would make 5 of 5 reachable. It is the right bar for THIS line and would have been the wrong
one for the last.

### The money block is OPEN — formulas, and what would invalidate each rate

```
eval_seconds_per_leg      = 198 calls × <pass-1 s/call>
pass_2_seconds_per_leg    = <threads with ≥1 filtered row> × 97 s/thread
training_seconds_per_arm  = <steps> × <s/step>
steps = floor(ceil(n / micro_batch_size) / grad_accum) × epochs   →  arm A 62 · arm B 82
```

**All three rates are borrowed, and two of them across a change of instrument.** They are registered
as inherited readings with the condition that invalidates them, and they are NOT the formulas'
inputs:

| rate | value | measured on | what would invalidate it |
|---|---|---|---|
| pass-1 s/call | 6.14 | **v2** requests (`prereg_pass1_window_r2`; the window pod ran at 2.694) | three of four legs send **v3**, whose widest E request is 8 894 chars against v2's 7 781. Safe as a FLOOR, wrong as a ratio |
| pass-2 s/thread | 97 | `ceil(58.07 × 1.67)`, the smoke MAX × pass 1's pod-class spread | r2 realised **23.760** (0.245 of the charge) and measured the spread on this decode directly at **1.008**. `lora-c-run` has a direct reading available |
| training s/step | 61.047 registered · 68.442 measured · 121.0 compliant-slow | all at **≤ 1 222 tokens** | v3's rows are **1 435–2 759** tokens. `config/qlora.yaml` says raising `max_seq_len` «changes no step time except on the batches that need it» — here EVERY batch needs it |

Cap **$4.00**, the ruling's own number. The hard stop is TO BE DERIVED in `lora-c-run`. The record
carries no `worst_case_usd`, no `total_seconds` and no projection, and a test asserts those three
field names are absent from the money block's keys.

### The three reachability blocks

1. **`the_smallest_class_has_no_fifth_neighbour`** — above.
2. **`no_row_fits_max_seq_len`** — below.
3. **`the_pinned_trainer_refuses_a_v3_dataset`** — below.

## The second STOP: no v3 row fits `max_seq_len`

`config/qlora.yaml` freezes `training.max_seq_len` at **1 408** and it is pinned by
`results/prereg_lora_b.json::instruments.config_sha256`. v3's SFT rows are **5 262–9 402 characters**
(median 5 750) where lora-b's v1 rows were **2 950 median and 4 132 max** — the five-neighbour block
now carries a rationale per example on top of v2's two paragraphs.

`train_qlora.encode_pass1` tokenizes `apply_chat_template(...)` and refuses on
`len(context) + len(target)`; `build_pass1_sft.ratio()` measured tokens-per-character against served
`prompt_tokens`, which counts the same template. So the pod's own number is the bound minus
`TEMPLATE_SLACK` = 16, and the producer's drop rule and the pod's refusal are two readings of one
number.

| tokens-per-character | where it comes from | min | median | max | over 1 408 | the pod's count for the SHORTEST row |
|---|---|---|---|---|---|---|
| 0.291741 | the registered maximum over probe-b's 64 paid rows | 1 552 | 1 694 | 2 759 | **506 of 506** | 1 536 |
| 0.282802 | the median of the same 64 | 1 505 | 1 643 | 2 675 | **506 of 506** | 1 489 |
| 0.269618 | the MINIMUM of the same 64 — the ratio most favourable to the run | 1 435 | 1 567 | 2 551 | **506 of 506** | **1 419** |

**Not a bound artefact.** At the most favourable ratio this repository has ever measured, the
shortest row still needs 1 419 tokens of the pod's own count against 1 408. Four remedies are named
and none is taken; `config/qlora.yaml` is frozen law and raising it is the operator's word — there
is precedent (1 024 → 1 408 by operator decision of 2026-08-04) and it is not the executor's.

**Four neighbours does NOT dissolve the second STOP, and that is measured.** Re-rendering the same rows with FOUR examples leaves **484 of 506 over at the most favourable measured ratio and 506 of 506 at the registered one**; with ONE example 62 are still over. The cause is the TEXT, not the block: v3's prompt is **4 112 characters = 1 200 tokens at the worst measured ratio and 1 109 at the minimum**, against a ceiling of 1 408 — the prompt alone occupies 79–85 % of it before a single neighbour, the topic, the entity block or the comment. Only raising `max_seq_len` or shortening the text closes STOP 2. Four neighbours DOES dissolve STOP 1, and that is a **scoped** change to nine rows of one thread against a **global** one — so they are two decisions, not one.

| neighbours per request | chars, median / max | tokens at the MIN ratio, median / max | over 1 408 |
|---|---|---|---|
| five (as built) | 5 750 / 9 402 | 1 567 / 2 551 | **506 of 506** |
| four | 5 541 / 9 193 | 1 510 / 2 495 | **484 of 506** |
| one | 4 925 / 6 125 | 1 344 / 1 668 | **62 of 506** |

## The third STOP: the pinned trainer refuses a v3 dataset

`scripts/train_qlora.py` is pinned live by `results/prereg_lora_b.json` **and**
`results/lora_b_verdict.json`. Both refusals were driven at $0:

```
train_qlora.load_sft:
  @VARUS_channel:10367#20766: task 'pass1_comment_gm4_v3' is not 'pass1_comment_gm4_v1'

train_qlora.build_pass1:
  …hashes 58718596d2dc909c… and pass1_sft.json registers ['79988046f96c981f', 'dc7c8390c3fff439']
  — this is not a registered dataset. Stop rather than train on bytes nobody pre-registered.
```

**What PASSES is named beside them**, because a refusal without its control is half a reading: the
`learn_chars` guard and the `prompt_sha256` equality **both pass**. Give the same v3 row v1's task
name and `load_sft` accepts it — so the refusal is a statement about the task field and not about
the row's shape, and the `+1` END-offset boundary survived being prefixed with a rationale.

The remedy is a SIBLING trainer that imports `train_qlora` and re-binds the two guards, exactly as
`scripts/gate_pass2_signals_r2.py` is a sibling of r1's gate. It is `lora-c-run`'s first $0
deliverable. Registering `train_qlora.py` as THE trainer without saying this would be a bar with no
producer.

## The ready-to-price table for `lora-c-run`

Every number from a file this contract built, at $0.

| | |
|---|---|
| training rows, arm A | **506** |
| training rows, arm B | **666** (506 + 160 synthetic) |
| optimizer steps, arm A / arm B | **62 / 82** |
| eval calls per leg | **198** |
| legs | **4** (base v2 reads the v2 leg; base v3, arm A and arm B read the v3 leg) |
| pass-2 threads per leg | **11** of the 16 reference threads, 46 filtered rows — measured on the window's out-file; each leg rebuilds its own pack |
| tokens per SFT row, median / max / min | **1 694 / 2 759 / 1 552** at the worst measured ratio |
| characters per SFT row, median / max | **5 750 / 9 402** |
| widest E request, v2 / v3 | 7 781 / 8 894 characters |
| cap | **$4.00** |

## The review — launched on a frozen tree, and it did not return

The contract asks for a five-lens review on a COMMITTED tree with a second skeptic pass on the
fixes. **Five lenses were launched against sha `8982dd3b48b84bba46f5589ca9785bed5e7c229d`** — the
two STOPs' arithmetic · the hand-written content of the 675 rows · the exclusion algebra · the
registration's honesty · the negative controls — each given the sha and told to quote it back.

**None of the five returned a report, and none answered a wrap-up request after 95 minutes.** So
the second skeptic pass did not happen either: there is no first pass to read fixes against. This
section says so instead of implying a review that was not delivered.

What DID verify this work, and it is not nothing:

| instrument | outcome |
|---|---|
| the advisor, before the approach crystallised | predicted both STOPs before they were measured — the `молочный_бренд` neighbour collision and the trainer's two refusals — and each fired exactly as described |
| the advisor, on the draft | caught the ONE claim in this contract with no producer behind it: «four neighbours dissolves both STOPs». Re-rendering says 484 of 506 are still over. **That is the correction this report exists to carry** |
| 46 tests, every guard driven in both directions | two defects the positive cases could not have found: an UNREACHABLE guard and `relative_to` raising on a tmpdir in four `main()`s |
| the rebuild-identity test | every one of the five producers is run into a tmpdir and its bytes diffed against what is committed |
| `--reproduce` on the pass-2 builder | bar 1 = 4 of 5, bar 3 = 2 signals, against r2's own verdict |
| my own re-derivation after the lenses stalled | see below |

### What I re-derived myself when the lenses did not come back

- **Disjointness, by the PAIR.** training ∩ E = **0**; training ∩ holdout = 0; training ∩ gold-14 =
  0; training rows shown a neighbour from their own thread = 0; example ids outside the shared pool
  = 0, in both the training set and E. **And training ∩ E by `msg_id` ALONE is 1** — `21239` lives
  in `@VARUS_channel:10470` and in `@klopotenkofood:6040`. A msg_id-keyed disjointness check would
  have reported a leak that does not exist, and a msg_id-keyed EXCLUSION would have dropped a
  legitimate training row ([[select_one_row_refuse_ambiguity]], [[id_spaces_that_look_comparable]]).
- **Every pinned sha in the registration matches its file today** — the v3 module, `prompts.py`,
  `scorer.py`, `train_qlora.py`, all three packs, both written inputs, `pass2_r2.py`, the gold and
  the holdout. Zero mismatches.
- **Every rate's provenance opens to the field it names**: 6.14 at
  `prereg_pass1_window_r2::money.arithmetic.seconds_per_call.charged`, `ceil(58.07 × 1.67)` at
  `prereg_pass2_signals_r2`, 61.047 and `longest_kept: 1222` at `prereg_lora_b`.
- **A seventh state of the `rationale` field does not exist.** Driven with a list, a dict, a bool, a
  float, whitespace, embedded newlines, guillemets, a duplicate key and a `\u0000`: every one
  resolves to one of the six named states and **not one refuses the reply**.
- **The step formula, read off the loop.** `train_qlora.train` steps only when `seen % accum == 0`
  over micro-batches, so `floor(ceil(506/2)/8) × 2 = 62` and `floor(ceil(666/2)/8) × 2 = 82` are the
  optimizer steps — and `planned`, which drives the cosine schedule and its warmup, is
  `ceil(n/(micro·accum)) × epochs` = **64 and 84**. Two real numbers of one run, and the money
  formula wants the first. Both are now in the record.

### Two defects that self-review found, fixed in the closing commit

1. **Two checks in the eval builder are INVARIANT ASSERTIONS and not guards, and calling them guards
   is what the unreachable-guard defect was made of.** `synthetic rows reached E` cannot fire: E is
   `holdout_units() ∪ payable_of_reference()` and neither enumeration can yield a `synthetic:`
   thread. Nor can `an item renders identically under v2 and v3`: the texts differ by a whole
   paragraph. Both are kept — they are the properties the paired table rests on — and both now say
   in the code that they have never fired and cannot, and what would make them reachable. Their twin
   above the rationale join IS a real guard, and it fires.
2. **`steps` had two right answers and the record carried one.** Above.
3. **And the first attempt at fix 1 did not land** — the patch aborted on an assert before its write
   and the commit message claimed it anyway. Grepping the file for the comment I had just said I
   added is what caught it (Dv751).

## Verification, at the closing tree

```
$ make check
3654 passed, 2 skipped in 550.81s (0:09:10)          exit 0

$ make preflight ARGS='pass1_v3.py prereg_lora_c.json'
pin registry: 1559 paths pinned by results/*.json

QUERY  pass1_v3.py
[3] pins — 5 of the 12 touched paths are pinned by a record
[4] digests — sha256 of all 5 pinned paths, against what is pinned
    5 of 5 pinned paths match every digest on them

QUERY  prereg_lora_c.json
[3] pins — 4 of the 9 touched paths are pinned by a record
[4] digests — sha256 of all 4 pinned paths, against what is pinned
    4 of 4 pinned paths match every digest on them
```

The suite opened this contract at **3 608 passed / 2 skipped** and closes at **3 654 / 2** — the 46
tests of `tests/test_lora_c_prep.py`, at a cost of **1.2 s** against the opening run's 549.57 s. The
pin registry grew 1 547 → 1 559 paths.


## Deviations from Dv728

Each with its cause tag from the closed enum v2 and the lesson beside it. **Every one was found at
$0; there is no money on this contract.**

| # | cause | what |
|---|---|---|
| **Dv728** | `[cause: contract-gap]` [[a_count_in_prose_is_not_the_enumeration]] | **The pool is 515 and the contract expects ~430** — the two exclusions OVERLAP. Six holdout rows sit inside reference threads, so `650 − 100 − 41` removes them twice and the honest count is `650 − 100 − 41 + 6`. The record carries the arithmetic and not the number. Same class for «our»: 41 rows = 7.96 % against the contract's ~43 and ~7 %. |
| **Dv729** | `[cause: contract-gap]` [[a-pinned-file-is-not-edited-to-grow-a-parameter]] | **`rendered_item` CANNOT take v3, and the contract asks.** It dispatches into `prompts.pass1_messages_gm4`, which raises for every task outside `prompts.PASS1`; `prompts.py` is pinned by 38 records. So the renderer is a SIBLING that restates the assembly and CALLS everything shareable. Answered by DRIVING the shipped renderer at v3 in a test, not by reading it. |
| **Dv730** | `[cause: spec-gap]` [[compute_the_ceiling_first]] | **NO v3 ROW FITS `max_seq_len`.** 506 of 506 are over the frozen 1 408 at all three measured tokens-per-character, and at the MINIMUM ratio the SHORTEST row needs 1 419 of the pod's own count. v3's request is 5 262–9 402 chars against lora-b's 2 950/4 132. `config/qlora.yaml` is frozen law and pinned by lora-b's record — a ruling, not an edit. Four remedies named, none taken. |
| **Dv731** | `[cause: contract-gap]` [[a-registered-bar-may-have-no-producer]] | **The pinned trainer refuses a v3 dataset by name**, on two guards driven at $0 — `load_sft`'s task check and `build_pass1`'s registered-sha check. The contract names `train_qlora.py` among the instruments to pin. It is pinned live by lora-b's prereg AND verdict, so the remedy is a sibling and it is `lora-c-run`'s first deliverable. What PASSES is registered beside what fails. |
| **Dv732** | `[cause: tooling]` [[run_the_instrument_on_the_named_example]] | **The boundary draw came back EMPTY under the shipped matcher, and the cause is one spelling.** `brands.find_watchlist_brands` finds zero retailer or brand mentions in all 466 non-«our» rows: `config/registry.yaml` spells the chain `Varus` in Latin and the comments write «варусі». The registry names run through the lexicon's own stem+endings screen reach «Сільпо» and «АТБ» and still not «варусі». No file in this repo carries that source's Cyrillic spelling. Tier A is named by two instruments and the record says which contributed what — 0 and 9. |
| **Dv733** | `[cause: verify-gap]` [[verbatim_quotes_must_be_grepped]] | **The cue check compared raw store bytes against a whitespace-collapsed working copy** and reported nine false misses. The comments carry doubled internal spaces and newlines; nine of the 515 cues are phrases a human can point at and differ from the raw text by one space. The rule is normalised on both sides — and a check that compares raw bytes against a rendered dump is checking the dump. |
| **Dv734** | `[cause: verify-gap]` [[an-empty-class-is-the-definitions-answer]] | **The synthetic-isolation guard in the eval builder was UNREACHABLE.** `data.joined()` refuses a synthetic row first, for want of a rationale, so the isolation guard below it could never fire. Found by the negative-control test that plants one — the guard passed its positive case forever. Moved to the top of `build()`, where it fires. |
| **Dv735** | `[cause: tooling]` [[the-entry-points-preamble-is-untested-code]] | **`Path.relative_to(REPO_ROOT)` raises on a temporary directory**, in FOUR scripts' `main()`. Found by the test that drives every command end to end with its output redirected — which is the only reason a green suite does not depend on having overwritten a committed artifact. Replaced with `window_summary_5c2.rel`, which already carries the try/except. |
| **Dv736** | `[cause: contract-gap]` [[a-registered-threshold-that-is-really-a-function]] | **The contract's second balance rule applies to nothing, and the arithmetic says so.** «no class under 8 rows per epoch-equivalent» — expected draws are `n_c·w_c = min(N/5, 8·n_c)`, so lora-b's weighting rule caps the majority at a fifth of the epoch by construction and the floor binds only under 8 rows. Applied: none, and the reason is registered rather than the knob. |
| **Dv737** | `[cause: process]` [[blinding_leaks_are_distributional]] | **«In the register of the window's comments» is a distribution, so it was measured on both sides — and the first draft failed four of six axes.** 2 % Russian against 14 %, 54 % lowercase openings against 6 %, 8 % emoji against 19 %. Corrected where correction was honest (a seeded pass, and 19 rewritten in Russian); the residual gap is named per axis with its delta, and the length gap is stated as deliberate. A synthetic corpus a model can separate from the real one by its openings is a weaker arm than the row count suggests. |
| **Dv738** | `[cause: process]` [[rederive_doc_numbers]] | **A number in a commit message was wrong and the record was right.** `4f4b9cc` claims «question mark 13% vs 13%» and lists alphabet and terminal punctuation as matched; the measurement is **8 % vs 13 %** and the record's own `matched` list — computed at a stated ±3 — names two axes, not five. The record was never wrong; the prose was. The commit stands, this row is the correction, and the report's table is the authority. It is also why this project's rule is that a number in a commit message is not a number in the report. |
| **Dv739** | `[cause: contract-gap]` [[a_consumer_list_is_not_a_meaning_list]] | **What `subject_id` means for `категория_личное` is READ OFF the gold, not assumed.** `results/reader_gold_w1_r2.json::per_comment` writes the CATEGORY there — «морозиво без цукру», «творог», «функциональная молочка», «baby-food» — and never the retailer's name. The 160 synthetic rows follow the gold's convention, which is exactly the discrimination the class is about: a comment naming Сільпо inside a habit has a subject, and it is not Сільпо. |
| **Dv740** | `[cause: tooling]` [[a-fixture-on-disk-pins-yesterdays-schema]] | **Four shipped APIs answer a different shape than the name suggests**, all found by driving them: `pass1_dev_pack.json::legs` is a LIST and not a dict; `build_pass1_sft.envelope()` returns `limit`, not `topic_limit`; `ratio()` returns `tokens_per_char_max`; and `build_pass1_fewshot_packs.pool()` STRIPS `store`, which `sft.request` needs — so the shared pool is built from `labelled_units()` plus `fewshot.grams` and is the same computation by construction. |
| **Dv741** | `[cause: contract-gap]` [[a-prefilter-cannot-certify-the-population]] | **Pass 1's own answer is in the boundary SELECTION, and that is declared.** With the shipped matcher at zero, tier A uses the window's paid replies: `сеть_ритейлер` / `молочный_бренд` with a `subject_id` that OCCURS in the comment. The occurrence check is what keeps it a mention test — without it a hallucinated name would select a row that never carried one. It is a selection instrument and never a gold, and the sample says so on its face. |
| **Dv742** | `[cause: contract-gap]` [[the_smokes_rate_carries_the_smokes_transport]] | **All three money rates are borrowed and two cross a change of instrument**, so each is registered with the condition that invalidates it rather than with a correction: 6.14 s/call was measured on v2 and three legs send v3; 61.047 / 68.442 / 121.0 s/step are readings at ≤ 1 222 tokens against v3's 1 435–2 759. A corrected rate would be a price, and this record may not carry one. |
| **Dv743** | `[cause: verify-gap]` [[a-moved-constant-fails-green]] | **The step count uses the arithmetic the trainer RUNS, not the one lora-b registered.** `optimizer.step()` fires on a whole `grad_accum` of micro-batches, so it is `floor(ceil(n/micro)/accum) × epochs` and not `ceil(n/(micro×accum)) × epochs` — lora-b registered 64 and ran 62. `micro`, `accum`, `epochs`, `rank`, `alpha` and `learning_rate` are all READ from `config/qlora.yaml` at build time and none of them is typed into this registration. |
| **Dv744** | `[cause: verify-gap]` [[a_claim_no_number_can_check]] | **The remedy I named for BOTH stops closes only one, and I wrote it before measuring it.** «Four neighbours dissolves both» reached `results/lora_c_data.json`, the registration, the ADR, the INDEX row, this report twice and a commit message before anything re-rendered a row at four examples. Measured: **484 of 506 still over at the most favourable ratio, 506 of 506 at the registered one**, and even at ONE example 62 remain — because v3's prompt TEXT is 1 200 tokens of a 1 408 ceiling before a neighbour exists. The record now carries the measurement AND the counts at four and one examples; the two remedies are also different in SCOPE — nine rows of one thread against all 506 — so they were never one decision. |
| **Dv745** | `[cause: tooling]` [[a_fixture_on_disk_pins_yesterdays_schema]] | **`legs` was a dict and every pod runner in this repo indexes `pack["legs"][0]`.** The contract names `results/pass1_dev_pack.json` as the precedent and that file carries a LIST of named legs; `build_pass1_fewshot_packs.legs_of` and both pass-2 runners unpack it positionally. A dict would have been a shape only this file knew, and `lora-c-run`'s runner would have been the thing that discovered it. Changed to a list with a `leg_of(pack, name)` helper, and the same defect had already shown itself once — reading `pass1_dev_pack.json::legs` as a dict is what raised while E was being built. |
| **Dv746** | `[cause: process]` [[a_review_that_verifies_a_moving_tree]] | **A `make check` was killed because I edited the tree it was verifying.** Two producers and two artifacts were rewritten while the suite was mid-flight, so its result would have been about a moment and not about a tree. Killed at 68 % and re-run on a stable tree: **3 653 passed, 2 skipped in 572.63 s**. The same rule that makes the five-lens review read a committed sha applies to the verifier, and it is cheaper to notice at 68 % than in a report. |
| **Dv747** | `[cause: verify-gap]` [[a_checker_whose_failure_is_silence]] | **Three of my own waits on that suite returned instantly and I read them as progress.** `until grep -qE "passed\|failed\|error"` matched ruff's «All checks passed!» from the START of `make check`; `while kill -0 <pid>` exits on EPERM from another shell session; and the harness returned background `sleep`s immediately. Each looked like «the suite is stuck» when the suite was fine. What settled it was `ps -o etime` on the PID — watch the PROCESS, not a grep of its log. |
| **Dv748** | `[cause: process]` [[a_review_that_verifies_a_moving_tree]] | **The five-lens review was launched on a frozen sha and did not return.** All five were given `8982dd3b48b84bba46f5589ca9785bed5e7c229d` and told to quote it back; none delivered a report and none answered a wrap-up request after 95 minutes, so the second skeptic pass has no first pass to read against. The construction was right — commit, freeze, hand out the sha — and the apparatus did not answer. What replaced it is enumerated above rather than implied: the advisor caught the one claim with no producer behind it, the 46 tests' negative controls caught two defects, and I re-derived the disjointness, every pinned sha, every rate's provenance, the seventh-state question and the step formula by hand. **This row exists so that «reviewed» is not read off a section that says nothing.** |
| **Dv749** | `[cause: verify-gap]` [[an-empty-class-is-the-definitions-answer]] | **Two checks in the eval builder can never fire, and they were written as guards.** `synthetic rows reached E` is unreachable — E is `holdout_units() ∪ payable_of_reference()` and neither can yield a `synthetic:` thread; so is the identical-sha check between the two legs, whose texts differ by a whole paragraph. Both are kept as the invariants the paired table rests on, and both now SAY in the code that they have never fired and cannot, and what would make them reachable. The same defect one layer down had already been found by a negative control (Dv734) — the difference is that its twin above the rationale join is a real guard. |
| **Dv750** | `[cause: contract-gap]` [[two_values_for_one_input_get_quoted_kindly]] | **`steps` has two right answers and the record carried one.** `train_qlora.train` steps only on a whole `grad_accum` of micro-batches, so the optimizer takes 62 and 82; its own `planned` — which drives the cosine schedule's total and its warmup — is `ceil(n/(micro·accum)) × epochs` = 64 and 84. Both are real numbers of the same run and the money formula wants the first. This is the SIXTH instance of one input with two values on this line, and the record now names both. |
| **Dv751** | `[cause: process]` [[a_claim_no_number_can_check]] | **A commit message claimed a change that had not been applied.** `1be8676` says two checks in the eval builder «now say in the code that they have never fired» — the patch that would have written them aborted on an assert BEFORE its write, and I read the surviving prereg half as the whole. Caught by grepping the file for the comment I had just claimed to add. Landed for real in the commit after it. Second instance on this contract of a commit message being wrong where the record was right (Dv738), and the same remedy applies: **the report is the authority and the commit message is prose**. |

**The tally, by the grep the template names:**

```python
import re, pathlib, collections
flat = " ".join(pathlib.Path("docs/reports/lora-c-prep.md").read_text(encoding="utf-8").split())
tag = {}
for chunk in re.split(r"(?=\*\*Dv\d+)", flat):
    if (m := re.match(r"\*\*Dv(\d+)", chunk)) and (t := re.findall(r"\[cause:\s*([a-z-]+)\]", chunk)):
        tag.setdefault(int(m.group(1)), t[0])
inr = {d: t for d, t in tag.items() if 728 <= d <= 751}
health = sum(1 for t in inr.values() if t in ("contract-gap", "spec-gap", "verify-gap"))
print(len(inr), dict(collections.Counter(inr.values()).most_common()))
print("contract health", health, "· paid", len(inr) - health, "· enum canonicity", len(inr), "of 24")
```

## Process signals

1. **A remedy named in five artifacts before anything measured it — and it closes one STOP of the
   two.** «Four neighbours dissolves both» reached `results/lora_c_data.json`, the registration, the
   ADR, the INDEX row, this report twice and a commit message before a single row was re-rendered at
   four examples. Measured: **484 of 506 still over at the most favourable ratio, 506 of 506 at the
   registered one**, and at ONE example 62 remain — because v3's prompt TEXT is 1 200 tokens of a
   1 408 ceiling before a neighbour, a topic, an entity block or the comment exists. The two remedies
   also differ in SCOPE: nine rows of one thread against all 506. **The sentence the operator would
   act on is the one that most needs a number under it**, and it was the only claim in this contract
   with no producer behind it ([[a_claim_no_number_can_check]], [[compute_the_ceiling_first]]).
2. **Two negative controls found defects the positive cases could not have.** Planting a synthetic
   row in the pool showed that guard was UNREACHABLE — `data.joined()` refuses it first for want of a
   rationale, so the isolation check below it had never fired and never could. Driving every command
   end to end found `Path.relative_to(REPO_ROOT)` raising on a temporary directory in FOUR scripts'
   `main()`. Both were green in the only state they had ever been run in, and both were found by
   asking the guard to refuse rather than to pass ([[guard_selftest_negative_control]],
   [[the_entry_points_preamble_is_untested_code]]).
3. **A cell that comes back EMPTY is a reading about the instrument.** The boundary draw found zero
   retailer or brand mentions in all 466 non-«our» rows, and the cause was one spelling:
   `config/registry.yaml` writes `Varus` in Latin and the comments write «варусі». Running the
   registry names through the lexicon's own stem+endings screen reached «Сільпо» and «АТБ» and still
   not «варусі». The answer was to name a SECOND instrument beside the first with the count each
   contributed — 0 and 9 — and not to substitute one for the other, because the zero is itself the
   finding the team lead needs ([[run_the_instrument_on_the_named_example]],
   [[a_prefilter_cannot_certify_the_population]]).
4. **A verifier run over a tree I was still editing, and then three waits that were not waits.**
   `make check` was killed at 68 % because two producers and two artifacts moved under it — the same
   rule that makes the five-lens review read a committed sha applies to the verifier. Then three of
   my own waits on the clean re-run returned instantly and each read as «the suite is stuck»: an
   `until grep` that matched ruff's «All checks passed!» banner from the START of `make check`, a
   `while kill -0 <pid>` that exits on EPERM from another shell session, and background `sleep`s the
   harness returns immediately. What settled it was `ps -o etime` on the PID —
   **watch the process, not a grep of its log** ([[a_review_that_verifies_a_moving_tree]],
   [[a_checker_whose_failure_is_silence]], [[long_run_watch_the_process]]).
5. **«In the register of the window's comments» is a distribution, and the first draft failed four of
   six axes.** Measured on both sides with one function: 2 % Russian against the window's 14 %, 54 %
   lowercase openings against 6 %, 8 % emoji against 19 %. Corrected where correction was honest — a
   seeded pass and 19 rows rewritten in Russian — and the residual is named per axis with its delta
   and its tolerance, including the length gap that is deliberate. **A synthetic corpus a model can
   separate from the real one by its openings is a weaker arm than its row count suggests**, and no
   shingle check can see it ([[blinding_leaks_are_distributional]]).
