# pass2-signals r2 — the 75 threads still owed

`docs/PROMPT-pass2-signals-r2.md`, executed. Step 0.5 (the r1 acceptance addendum, $0) → D0′ at $0
on a committed tree → D1 paid, cap $2.50 → D2 at $0 over all 79 units.

## Read back — one line each

- **What step 0.5 corrects.** Three things, all landed before r2's first line of code and all in
  `docs/reports/pass2-signals.md`'s ADDENDUM: Dv681–Dv703 re-tagged on the closed enum so the tally
  can be run (**contract health 16 · paid 7 · 23 of 23**); the pack's headroom is **144 characters
  of 12 000, not 603**, because the D0 section quoted the pre-review pack and `4d60d33` grew the
  prompt +459; and «a smoke mean of 43.09 would have been a GO» is **false by 0.29 s** — the
  break-even mean is **43.087**, whose 1.5× is the live knife edge 64.63.
- **The 75, the four carried rows, and why the prompt must not move a byte.** Owed: the 74 never
  bought plus `@matusi_ukr:22303` (F2), whose reply was REFUSED on a report-only field and never
  read — a transport outcome, not a verdict. The four replies that parsed are COPIED into r2's
  out-file as its first four rows and never re-bought; that copy is only legitimate if the request
  they answered is the request r2 would send, so `pass2_thread_gm4_v1` is byte-identical and every
  carried row is re-verified against the r2 pack's own `rendering_sha256`.
- **Which fields can no longer refuse, and which still can.** Report-only fields are read through a
  tolerant reader that records `unreadable` beside the value and never raises: `per_comment.note`,
  `subject_doubt`, `subject_id`, `stance`, `aspects`, `signals.signal_type` (the scorer says in as
  many words that it is not compared), `signals.reading`, `signals.quote`, `noise.class`,
  `post_summary` and `discussion_summary`. What still refuses, and only this: a relabel; an id that
  was not in the request; a signal citing no comment; a reply about another thread; an
  unbalanced or unreadable object; a domain violation on a SCORED field — `thread`,
  `signals.evidence`, `signals.subject_type`, `signals.aspect`, `per_comment.subject_type` and the
  three answer lists being lists at all.
- **The ceiling and where it is derived from.** **15 569 characters**, and it is measured rather
  than typed: no record on this stack carries the model's context, so the anchor is the largest
  prompt this exact serving config has been PROVEN to serve — `@matusi_ukr:22272` in the reader's
  v5b run, **4 510 prompt tokens, `finish_reason: stop`, 1 896 completion tokens against the
  `serving.output_tokens` reservation of 4 000** — converted into the unit the renderer refuses in
  at pass 2's own worst measured density, **3.4523 chars per prompt token**. 15 569 ≥ **11 856**,
  the widest r2 unit, so there is no STOP; headroom 3 713 characters, 23.8 %.
- **The rate, its two factors, and why the MAX.** `charged = 58.07 × 1.67 = 96.98 → 97 s/thread`:
  the smoke's slowest call, times v2's measured pod-class spread on pass 1 (2.694 → 4.498 s/call
  over three pods). The MAX and not a row-weighted mean because the population's widest unit is 26
  filtered rows (`@klopotenkofood:6040`) against the smoke's widest **eight** — the contract prints
  10 and the pack does not carry it, so the extrapolation a fit would make is **3.25×** and not
  2.6× — and the max is the only reading that covers the heavy tail without a model of it.
- **The worst case, the cap, the hard stop, the recovery, the step sum.** Generation 75 × 97 =
  **7 275 s**; + ssh 500 + stage/launch 150 + load 450 + overhead 1 300 = **9 675 s = 2.6875 h →
  $2.15** at the $0.80/h price ceiling ($1.4244 at the measured $0.53). Cap **$2.50**; cumulative
  hard stop **11 000 s = $2.4444**; session ceiling 11 250 s ≥ the stop, so the seconds bind first.
  Recovery: one dead pod at rung 2 (500 s, $0.1111) + the worst case = 10 175 s ≤ 11 000 and
  **$2.2611 ≤ $2.50**; the widest dead pod that still fits is **1 325 s**. Step sum: r1's
  $0.108122 on the clock + r2's $2.50 cap = **$2.608122**, on a fresh guard step
  `pass2-signals-r2` with `--step-cap 2.50`.
- **What a KILL after the first new reply means.** The session closes. The rows already bought
  stand in the out-file as evidence, nothing is deleted and nothing is re-asked, and the remainder
  is a new registration — never a second pod after a reply, never a third pod at all.
- **Why the review reads a committed tree.** r1's five-lens review reported «3 confirmed, 12
  refuted» and the split measured nothing but the timing of my own commits: I was fixing the tree
  while the skeptics read it, so twelve of them refuted with «already fixed at HEAD» and named the
  commit that fixed it. Every finding was real. This time the finders are given a COMMIT SHA and
  quote it, the fixes land on top, and a second skeptic pass reads the fixed sha with the tree
  frozen — so the tally is a tally.

## Step 0.5 — the acceptance addendum of r1 ($0, its own commit, before D0′)

`docs/reports/pass2-signals.md` gained an **ADDENDUM** section; nothing above it was rewritten.
Commit `19724e4`, before a line of r2's code existed.

| what | before | after |
|---|---|---|
| the Deviation tally | free lesson names, **0 `[cause:]` tags**, no tally possible | **23 of 23** tagged on the closed enum, names kept beside each as links |
| the pack's headroom | 603 chars of 12 000, widest 11 397 | **144 of 12 000, widest 11 856** — the D0 section quoted the pre-review pack |
| «a mean of 43.09 would have been a GO» | true | **false by 0.29 s** — the break-even mean is 43.087 |

**The tally, by the grep the template names, run over the file:**

```
23 {'contract-gap': 13, 'tooling': 5, 'verify-gap': 2, 'spec-gap': 1, 'process': 1, 'model': 1}
contract health 16 · paid 7 · enum canonicity 23 of 23
```

`env` is empty: that session had no platform surprise. Sixteen of twenty-three are the registration
meeting its own contract at $0 before the create, which is a contract doing its job — and it is the
first pass-2 registration on this stack, with no sibling to copy.

**The rebuild that moved the headroom is `4d60d33`**, the bars-lens fix that spliced
`prompts.READER_ASPECT_V5` and `prompts.READER_NOT_A_SIGNAL_V3` into the prompt: +464 characters
and −5, net **+459** on the text and on all 79 requests, widest 11 397 → 11 856, median 6 253 →
6 712. Traced commit by commit in the addendum. The reading gets sharper rather than softer: a fix
that buys two clauses with 459 characters of prompt spends **76 % of the remaining headroom**, and
nobody costed it in that unit at the time.

**The 43.087 is the fourth instance of one input with two values on this line** — and it appeared in
the sentence that was explaining the third. The ADR and `knowledge/hot.md` quote none of the three
numbers; that was grepped and reported rather than assumed.

## D0′ — at $0, before any pod, on a committed tree

### The sibling rule, applied four times — and why it is not an evasion

`src/market_pulse/pass2.py` is pinned by `results/pass2_pack.json::instruments.module.sha256`, that
pack is pinned by `results/prereg_pass2_signals.json`, and r1's own
`test_the_pack_rebuilds_byte_for_byte_from_its_own_inputs` re-runs the builder and compares. **One
character in that file turns `make check` red on a closed paid session's artifacts.** The contract
states the rule for the gate — «`--revision r2` if r1's pinned bytes stay untouched, otherwise a
sibling (say which)» — and the same rule decides the module, the runner and the scorer. Said, and
here is which:

| r2 | r1 | why a sibling |
|---|---|---|
| `src/market_pulse/pass2_r2.py` | `pass2.py` | pinned by r1's pack, which is pinned by r1's record |
| `scripts/gate_pass2_signals_r2.py` | `gate_pass2_signals.py` | pinned by `prereg_pass2_signals.json::instruments.gate` |
| `scripts/pass2_r2_pod_runner.py` | `pass2_pod_runner.py` | same record, `instruments.runner` |
| `scripts/score_pass2_signals_r2.py` | `score_pass2_signals.py` | same record, `instruments.verdict_producer` |

Each one LOADS its r1 counterpart rather than copying it. The module imports the prompt, the
renderer and the blocks; the gate executes r1's gate as a module object with its sha checked first;
the runner reuses the shipped reader loop; the scorer imports r1's own bar, scorecard, DROP and
doubt tables as the pure functions they are. **Two tripwires say so and fail if that stops being
true:** `test_r1s_parser_still_REFUSES_F2` and `test_r1s_pack_still_rebuilds_byte_for_byte`.

### The prompt did not move, and the four carried rows are why that is a requirement

```
prompt sha256  a674f284085d43c54df590ce943fb8c02d6ac28b7832c05f2e4b7a54879f61f8
               == results/prereg_pass2_signals.json::instruments.prompt_sha256
               == results/pass2_r2_pack.json::instruments.prompt_sha256
79 of 79 units re-render byte for byte through BOTH modules, to r1's own rendering_sha256
```

r2's ceiling is different from r1's, so the renderer is called inside a contextmanager that swaps
`pass2.PASS2_MAX_INPUT_CHARS` for the length of one call and puts it back. The ceiling is read once,
after the string is built, and only to refuse it — so the RENDERING cannot move, and a test asserts
the constant is restored.

### The derived input ceiling — 15 569 characters, and what it is derived FROM

The contract asks for a ceiling «derived from what the serving config actually bounds (the model's
context and `reader_v5b_pack.json::serving` — name the field)». Two of those three exist:

| | |
|---|---|
| the field | `results/reader_v5b_pack.json::serving.output_tokens = 4000` — the config bounds the ANSWER and names no input bound at all |
| the model's context | **not on this stack.** Grepped for `context_window` / `context_length` / `max_position` / `n_ctx` and for the round numbers across `src/`, `scripts/`, `results/`, `docs/` and `knowledge/` — nothing. A number taken from outside would be a typed value wearing a derivation |
| what IS provable | the widest prompt this exact serving config has been observed to SERVE: `@matusi_ukr:22272` in the reader's v5b run — **15 673 characters, 4 510 prompt tokens, `finish_reason: stop`, 1 896 completion tokens** under the same 4 000-token reservation. Four reader requests were over 12 000 characters and all 23 answered |
| the conversion | pass 2's own density, over its five PAID requests: 41 922 chars / 11 907 prompt tokens = 3.5208 mean, range **3.4523 → 3.6894**. The MINIMUM is used — fewest chars per token is most tokens per char |

```
4 510 prompt tokens × 3.4523 chars/token = 15 569.9 → 15 569 chars
15 569 ≥ 11 856 (the widest r2 unit)  →  the contract's STOP-before-any-pod does NOT fire
headroom 3 713 chars = 23.8 %, against 144 = 1.2 % under pass 1's aliased constant
```

Both inputs are re-derived from the files they name by `test_the_ceiling_re_derives_from_the_artifacts_it_names`, and the pack re-checks all 79 units against the ceiling at build time.

### The parser — a closed refusal set, and the domains never re-implemented

**Report-only fields are read through the PINNED validator that owns them and repaired only where
that validator raises.** `prompts._text`, `_choice`, `_flag` and `_msg_id` are CALLED; the only
thing r2 decides is what happens when one of them says no. A second spelling of a domain is the
two-copies state one of the two files moves out of silently.

| the refusal set, closed at six | |
|---|---|
| a relabel | the ADR's line |
| an id that was not in the request | `scorer.reader_signal_found` matches on EVIDENCE, so an invented id can make a bar answer by accident |
| a signal citing no comment | strict authority keys on the label of a CITED row |
| a reply about another thread | it would be scored against another thread's gold |
| an unbalanced or unreadable object | the pinned container reader's own refusals |
| a domain violation on a SCORED field | `thread` · `signals.evidence` · `signals.subject_type` · `signals.aspect` · `per_comment.subject_type` · the three answer lists being lists |

**What «scored» means is read off the scorer, not asserted.** `scorer.reader_signal_found` compares
evidence, `subject_type` and `aspect` — and says in its own docstring that `signal_type` and
`subject_id` are *deliberately NOT compared*. So `signals.signal_type` is report-only, and a reply
that invents a sixth signal word keeps its thread, its evidence and its aspect. It is recorded as
unreadable in that field — and, because carrying the word past the pinned domain check means
forcing `proposed` to True, the OVERWRITE is recorded too, in its own census with the model's own
flag beside it. (Both of those sentences are corrections the second skeptic pass made; see the
review section below.)

Eleven fields can no longer refuse: `post_summary` · `discussion_summary` · `signals.signal_type` ·
`signals.subject_id` · `signals.stance` · `signals.reading` · `signals.quote` ·
`signals.proposed`/`from_post` · `per_comment.subject_id`/`.stance`/`.aspects` ·
`per_comment.note` · `per_comment.subject_doubt` · `noise.class`. One test poisons **every one of
them at once** and the thread survives with its signal, its evidence and its aspect intact and all
thirteen named in `unreadable_fields`.

**And F2's exact reply:**

```
pass2_r2.parse_pass2(r1's @matusi_ukr:22303 reply)
  → 0 signals · 2 per_comment rows · subject_doubt False on both · note None on both
  → unreadable_field_names ['per_comment.note'], 2 rows, each «per_comment.note is not a
    non-empty string»
  → COUNTED, not refused
pass2.parse_pass2(the same bytes)   → ParseError, exactly as r1's sealed record says
```

Three more repairs r1's parser did not have, each a state and not a refusal: a **missing**
`subject_type` is the same omission a `null` one is (Dv699 extended); a `per_comment` or `noise` row
with **no readable msg_id** is DROPPED and counted rather than refusing the thread; and a **missing
answer list** still refuses, because `scorer.reader_noise_count({})` returns `signals: 0` and
defaulting the list to `[]` would read GREEN over a non-answer.

### The pack and the seed

```
79 units · carried 4 · owed 75 · every rendering matches r1
length: widest 11856 chars (@mandziak:3679) · median 6712
        headroom 3713 of 15569 (derived) · 144 of 12000 (pass 1's constant)
seed:   results/pass2_signals_r2_v1.jsonl — 4 rows, each with `carried_from`
        @VARUS_channel:10613 · @mandziak:3676 · @mandziak:3703 · @matusi_ukr:22272
owed after the seed: 75, first @matusi_ukr:22303
```

The source is r1's pack itself, checked against the sha its sealed record pins — r2 does not
re-derive the population, because re-running the census filter would put a second producer between
the four carried replies and the requests they answer. Every unit is re-rendered and held to r1's
`rendering_sha256`; a moved rendering is a **build-time STOP**, and the test that says so patches
the renderer and watches the builder refuse.

`--seed` is its own named step. It refuses to overwrite a file carrying a BOUGHT reply, and it
refuses a carried row whose rendering the pack does not produce.

### The record — 73 H6 rows, and one of them refused the contract's own number

```
H6: 73 rows, every registered number re-derives
owed 75 × 97 s = 7275 s · all-in 9675 s = $2.1500 at $0.8/h
hard stop 11000 s = $2.4444 of $2.50 · widest dead pod 1325 s
recoverable up to 1246.5 s of create-elapsed (2211.5 at the measured pre-generation)
ceiling 15569 chars (derived) · widest unit 11856 · headroom 3713
```

**The refusal gate fired once, on the contract's own figure.** `docs/PROMPT-pass2-signals-r2.md`
argues the MAX by «the population's widest unit is 26 rows against the smoke's widest 10». The pack
says the smoke's widest is **8** — `@mandziak:3703` and `@matusi_ukr:22272` TIE at 8 — and no
reading of the five gives 10. Registered at 8, with the contract's number named in the formula
string, and the argument gets **stronger**: the extrapolation the MAX avoids is 26/8 = **3.25×**,
not 2.6×.

**The recovery number the contract prints is $2.2607 and the arithmetic is $2.261111.** 10 175 s ×
$0.80/h. Nothing binds — both are under the $2.50 cap — but it is the fifth instance of one input
with two values on this line, and step 0.5's third correction was about the fourth. Registered at
the derived value with the printed one named beside it.

**The Dv613 sweep.** 6 600 · 1.50 · 120 · 48.6486 · 32.4324 · 12 000-as-a-ceiling appear ONLY inside
`supersedes`, with one exception that is named rather than silent: the `step_0_5_*` H6 rows
re-derive r1's arithmetic in order to correct it, so they carry r1's numbers by subject. A test
holds the sweep with that exclusion spelled out.

### The gate — six re-bindings, and every one of them closes a defect found by DRIVING

The four carried rows sit in the out-file before the pod exists, so **every inherited rung that
counts rows answers a different question than it thinks.**

| # | re-bound | what the inherited code would have done |
|---|---|---|
| 1 | `population.sha256` in the record | **`KeyError` inside `--watch`, `--projection`, `--completeness` and `--close`.** `gate_pass1_window.main` subscripts `record["population"]["sha256"]` before every rung that reads a pack. It would have landed on a pod that was already billing — the same shape as r1's `payable_comments`, in a different key |
| 2 | `fingerprint` | **rung 3 could never fire.** `watch`'s boot branch is `if not cleared and not answered`, and four rows make `answered` non-zero from the first poll. A pod that produced nothing would have run to the liveness deadline |
| 3 | `first_reply_after_launch` | rung 3's READING would be **197.6 s measured on r1's pod**, so `--boot` reports GO before this pod has answered anything |
| 4 | `leg_state` | the leg would owe **79 and not 75**, and the rate rung 4 multiplies would blend r1's four calls into this pod's mean |
| 5 | `pre_create` | the recovery clause would read four carried rows as «a reply has been bought» and **refuse this session's FIRST create** |
| 6 | `authorised` / `legs_of` | r1's slices the leg to a smoke prefix until a go token is recorded, and r2 has no go/no-go |

**Number 1 and number 5 were both found the same way and neither is visible from a function.** The
`KeyError` lives in `main`, past every function a unit test calls; the recovery clause looks correct
until `_SHIPPED["pre_create"]` is traced and turns out to be **r1's wrapper and not the raw
arithmetic** — r1's gate had already re-bound it onto the window module before this file imported
it, so delegating «to the shipped one» delegated to r1's clause reading r1's out-file. That is
[[a_proof_can_cover_the_sibling_branch]] one level deeper than the r1 session found it.

**The rule that came out of it, and it is in the gate's docstring:** rungs 3, 4 and 5 count the rows
THIS POD bought; rung 7 counts the whole file. Neither count is wrong — using one where the other
belongs is.

`--go-no-go` is REFUSED by name with the reason, so a hand that types r1's command gets a sentence
instead of a stack trace.

### The runner, the scorer, the runbook

The runner is the shipped reader loop with pass 2's render and handshake swapped in, called ONCE
over 79 units; `already_answered` skips the four. The handshake pins **both** modules — the one that
renders and the one that will read the answers. Before the model is loaded it verifies that the
seeded file carries exactly the ids the pack names as carried, each against its unit's rendering.

The scorer imports r1's `bar_states`, `scorecard`, `drop_table`, `doubt_table` and `accounting`
unchanged, binds r2's parser HERE rather than re-binding r1's module global — **that re-binding
would break r1's scorer for the rest of the process, and its own tests re-parse r1's out-file and
expect the refusal that is r1's record** — and adds the unreadable-field table and a rate table
computed over the 75 rows this pod buys.

The runbook is r1's minus the go/no-go and **plus one scp**: the seeded out-file to
`/workspace/run/`, digest compared on both sides, before the launch. Without it `already_answered`
finds an empty directory and the pod re-buys four threads the registration forbids re-buying —
and `check_requests` cannot catch it, because the renderings match by construction. A test greps
the runbook for that scp.

### The five-lens review on a FROZEN tree — and this time the tally is a tally

D0′ was committed first (`d71a93d`), and every lens was given that sha, told the tree would not
move, and told to quote it. **All five quoted it back.**

```
filed 12 · confirmed 10 · refuted 1 · 1 over the per-lens cap and listed unverified (fixed anyway)
```

r1's review reported **3 confirmed and 12 refuted**, and that split measured nothing but the timing
of my own commits — twelve skeptics refuted with «already fixed at HEAD» and named the commit that
fixed it. One structural change, a commit before the finders start, and the same apparatus returns
10 of 11. That is the whole of Process signal 4 of r1, closed.

**Ten confirmed findings, eight distinct defects.** Two were found twice by different lenses, which
is itself a reading: `money` and `bars` both landed on the smoke mean, `population` and `transport`
both landed on the seed.

| # | lens(es) | what it was | what it would have cost |
|---|---|---|---|
| **1** | authority, bars | **`parse_pass2` wrote `None` into fields the pinned reader guarantees are non-empty STRINGS, and two of them are GROUPED ON.** `score_pass2_signals.drop_table` — a SEALED file — does `sorted(Counter(noise.class))`, and r2's own verdict producer does the same over `signals.signal_type` | **the whole run.** 75 threads, $2.15, rung 7 GO — and `TypeError: '<' not supported between 'NoneType' and 'str'`, so D2 produces no verdict, no bars, no scorecard. Triggered by ONE unreadable report-only field in any of 79 threads: the exact repair r2 exists to make |
| **2** | population, transport | **an ABSENT seed file returned «no carried rows» and skipped the whole guard.** Staging does `rm -rf /workspace/run`, so absence is the DEFAULT state | four threads re-bought — the one thing the contract's DO NOT names in as many words — ≈388 s, ≈$0.08, and r1's $0.108122 of paid evidence discarded |
| **3** | population | **rung 7 and D2 split carried-vs-bought on the PACK'S ID LIST**, so the four re-bought threads would be reported as carried and rung 7 would say GO | it is what makes #2 invisible after the money is spent |
| **4** | money, bars | **D2 published r1's smoke mean as 53.027** — the four CARRIED rows. r1's smoke was FIVE calls and the fifth (`@matusi_ukr:22303`, 15.801 s, the fastest) is refused and re-bought | the one reading D2 exists to publish, inflated 16.3 %, on a line the record, the contract and r1's report all state at 45.582 |
| **5** | transport | **the `pod create` line was a hybrid of two CLIs** — `--gpuType` / `--networkVolumeId` / `--imageName` do not exist; `runpodctl pod create --help` is the authority | it cannot parse. And the natural repair of a create that will not parse is a retyped line without `--terminate-after`, which is the whole of rung 6 |
| **6** | authority | **a present-but-not-a-list `per_comment`/`noise` was rewritten to `[]` and the thread COUNTED as parsed** | the false GREEN this module's own `SCORED_FIELDS` table forbids two screens above — seven answered rows thrown away and the thread reported as read |
| **7** | authority | **`proposed` was forced True to carry an unreadable `signal_type` past the pinned domain check, and the invention was never recorded** | a value the model explicitly denied, published in the verdict as its answer |
| **8** | bars (over the cap, verified by me) | **r2's record republished r1's `under_a_STOP` clause** on bars 2 and 3 — prose about a rung `main()` now raises on | the operator reads a verdict block describing a STOP arm `arm_rule` says nothing can select |

**The one refutation is worth reading.** `bars` filed «an unreadable `subject_doubt` is counted as
*not doubted*, so the published rate is a lower bound printed as a rate». The mechanism reproduces —
`doubt_table` is falsy-tested — and the skeptic drove two 79-row out-files differing only in that
field and showed the published tables DO carry the denominator caveat. Mechanism real, defect not.

**And one that was nobody's finding, isolated by driving.** `tests/test_pass2_signals.py`'s go-token
test was a **CLOCK**: `run_go_no_go` projects from `datetime.now()`, so with a fixed `created_at` its
GO half stopped passing at `created_at + 1 970 s` — **10:32:50Z today** — and went red with no commit
behind it. Found because `make check` failed on r1's file while I was fixing r2's, and isolated by
stashing everything and re-running at the committed tree. The pod's create stamp moves with the
clock it is measured against now.

### The second skeptic pass — on the FIXED commit, and it read the fixes as new code

The fixes landed as `7843d50`; the tree was frozen again and eight skeptics were given that sha,
one per fix, each with two jobs: **does the fix close its defect, and did the fix OPEN something.**
All eight quoted `7843d50`.

```
fixes checked 8 · closed 8 · NOT closed 0 · new defects filed 24 (19 distinct)
```

**Every fix closed. And the second half is where the value was: 19 distinct defects the FIXES
introduced or left behind**, 18 of them corrected in the commit that follows this section. The five
that matter:

| what the fix opened | why it matters |
|---|---|
| **the `proposed` overwrite was filed in the census of UNREADABLE fields** — and its recorded `value` was the parser's own repaired flag, not the model's | it inflates the Dv702 measurement this whole contract was bought to take, with a field the reader read perfectly well. It now has its OWN list, its own name, the model's RAW value (captured before the repair), and it fires only when something actually changed |
| **`unreadable_table.on_carried_rows` was the one census the carried-field fix did not re-key** | one verdict would say `units_carried_from_r1: 0` and four keys later attribute rows to `on_carried_rows` — the same defect class, inside the deliverable that reports it |
| **the fourth and fifth RED causes of rung 7 were registered nowhere** — the record still said «All three, or RED» and the runbook enumerated three | a bar may not go RED for a reason the pre-registration does not carry. Registered now, in both |
| **D2 still published a sixth signal type the model DENIED** — `proposed_signal_types` listed the sentinel | recording the overwrite was not enough; the consumer had to stop reading the parser's flag as the model's |
| **an untracked `results/pass2_signals_r2_run.json` was sitting in the working tree**, holding a TEST fixture pod `p1` with no `deleted_at` | **rung 0 would have returned KILL before the first legitimate create**, with an instruction to delete a pod that never existed. Written as a SIDE EFFECT of a read-only-looking gate command: `launched_at_of` stamps the record and `save()`s it. Deleted, and step 0 of the runbook now looks for it |

Three more the pass found that are r1 inheritances rather than r2's: `$SSHK` is used six times in
the runbook and defined nowhere (fixed — step 0 defines it and every use is quoted); nothing in the
runbook or the suite ever asks the CLI whether its flags still exist (fixed — step 0 greps
`pod create --help`); and the create-line test compared flag NAMES only, so a drifted `--image` or
`--network-volume-id` would parse, create a pod and fail on a cold volume at ≈$0.10 of billed time
(fixed — it compares values too, and asserts the only one that moved is `--name`).

**One is named as a bound rather than fixed.** The sentinel `"(unreadable)"` is FORGEABLE where
`None` was not: a model that writes that exact string is indistinguishable from a repair *in the
value*. It is distinguishable everywhere it matters — `unreadable_fields` names every field the
parser repaired and is the authority, no bar reads `signal_type` or `noise.class`, and both rule
strings now point at that census. The alternative is a sentinel no model can produce, which is more
machinery for a case no reply has ever shown.
