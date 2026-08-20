# PROMPT — pass1-fewshot: the codebook clause + labelled neighbours, measured on a dev set before ONE shot at the sealed fourteen (D0 $0 → D1 paid, cap $1.50 → D2 $0)

**Runs in a FRESH executor session, AFTER `docs/PROMPT-lora-b-run-addendum.md`
is accepted.** Authority: the operator's rulings of 2026-08-20 in the
team-lead session, registered in `docs/STATUS.md` «Открытые решения» п. 0
(the base stays Gemma-4-31B; the operator's word replaces sitting C; the goal
is the analysis of `docs/REFERENCE-signals-w1.md`; the team lead labels) and
the three answers of the joint step review (dev-200 · the shot in the same
session on a pre-registered gate · the dev gate as written below). Read:
this file → `docs/PROMPT-pass1-probe-b.md` (transport, rungs, DO NOT — still
binding) → `results/prereg_lora_b.json` `attempt` / `return_to_sitting` /
`kill_clock` (the shape to borrow) → `knowledge/decisions/lora-b-red-and-line-b-closes.md`.
Deviations from **Dv587**, closed enum v2, `[[lesson]]` optional, five-line
Process signals. Team-lead files (docs/STATUS.md, docs/SPEC.md,
docs/PROMPT-*.md) are committed verbatim, never edited. Never `git add -A`.

## Why this line, in three lines (state your assumptions against them)

Line B (labels + LoRA) is CLOSED red: the adapter learned the label marginal,
not the decision. All four «категория» misses of the base are ONE error
class — the comment MENTIONS a retailer or brand inside a category habit
(47902 «творог … з АТБ»), or a retailer answers a category demand with SKUs
(21601) — and the base classifies by the mention, not by what the comment is
ABOUT. This line fixes the definition in the prompt and shows the contrast
with labelled neighbours; nothing is trained.

## Baselines — paste `make baselines` output at step 0, never recall

Team-lead readings at issue time: suite **3 169 / 2**; `git status` — only
the addendum's files if it has not landed; LORA-B step closed at $2.3624;
cycle-2 **$5.7892 of $20.00**, remaining **$14.2108**; cloud `[]` / `[]`,
volume `qw4nwleanc` present. Labels: `results/labels_pass1_r1.jsonl` (500) +
`results/labels_pass1_r2.jsonl` (150) = 650 rows — не_наш_рынок 340 · null
213 · сеть_ритейлер 48 · категория_личное 47 · молочный_бренд 2 («our» rows
= 49). `scripts/build_pass1_label_pack.py::excluded_threads` is why no label
shares a thread with the 14 gold rows or the 64 eval-pack items — re-assert
it, do not assume it.

## D0 — everything at $0, committed before any pod

**D0.1 The holdout, registered before anyone trains again.** A new producer
writes `results/pass1_holdout_100.json`: 100 of the 650 labelled rows, drawn
with seed 20260820, stratified by `subject_type` in the labels' own
proportion (340:213:48:47:2 → 52:33:7:7:1), listed as (thread, msg_id, label)
with the labels files' sha256 beside them. Rule, written into the record:
**never in any training set of any future line; evaluation only; a dataset
builder that finds one of these ids refuses to build.** Add that refusal to
`scripts/build_pass1_sft.py` with a test in both directions (a holdout id in
the input → refusal; the current arms' inputs minus nothing → build). This
line does not train, so dev rows below MAY overlap the holdout — say so in
the record.

**D0.2 The prompt `pass1_comment_gm4_v2`.** A new entry in `PROMPTS`
(`src/market_pulse/prompts.py` — the reader v2→v5 manoeuvre; old records'
pins of prompts.py are already «moved since» and are NOT re-pinned). Text =
`PASS1_COMMENT_PROMPT` (v1, by reference, same bytes) + ONE codebook clause
+ the examples slot. The clause, in the prompt's own English register:
«`subject_type` is what the comment is ABOUT, never what it mentions. A
retailer or brand named inside a personal category habit (where one buys
the curd, which shop's kefir) is `категория_личное`. A retailer's own reply
that answers a category demand with products is `категория_личное`, not
`сеть_ритейлер`. A comment about the retailer's service, stock, prices or
stores is `сеть_ритейлер`. A comment about a named dairy producer or its
product as such is `молочный_бренд`.» No gold msg_id, thread or answer in
the text — extend `tests/test_pass1_prompt.py`'s synthetic-examples proof
over v2 (positive control included). `PASS1_TASK` stays v1; v2 is selected
by the pack's `task`.

**D0.3 Neighbours — one labelled example per class, by similarity.** For a
query comment, from the pool = the 650 labels MINUS every row of the query's
own thread, pick for EACH of the five classes (null included) the single
nearest comment by Jaccard similarity over lower-cased character 3-grams of
the comment text; ties by the smaller msg_id. Five examples, one per class,
rendered in the request after the entities block as
`Labelled examples (subject_type only): "<text>" → <label>`; never the
query's own row. Balance by construction is the point — nearest-k would hand
the model the same 52% prior the LoRA learned. Comment texts come from the
same store reader `scripts/build_pass1_label_pack.py` used. Deterministic:
the pack records, per item, the five (thread, msg_id, label) chosen and the
`rendering_sha256` of the full request, so the shot is reproducible from the
file. Contamination, printed as FOUR empty lists by the producer: neighbour
ids ∩ gold-14 · neighbour threads ∩ gold threads · neighbour ids ∩ eval-pack
64 · neighbour threads ∩ eval-pack threads.

**D0.4 Two packs.** (a) `results/pass1_dev_pack.json` — 200 labelled rows:
ALL 49 «our» rows (категория_личное 47 + молочный_бренд 2) + 151 drawn with
seed 20260820 from the other 601, stratified 340:213:48 → 85:54:12; each item
rendered TWICE in the pack — task v1 (base arm, no examples) and task v2
(examples) — same topic/entities context as probe-b's pack builder renders
(the entity block comes from bought reader verdicts where they exist, else
the branch-C topic cut, exactly as `results/pass1_sft.json` records it).
(b) `results/pass1_probe_b_pack_v2.json` — probe-b's 64 units UNCHANGED in
identity and order, task v2, examples added; `instruments`/`serving` copied
from the sealed pack; its sha registered. The sealed `pass1_probe_b_pack.json`
and the base's per-row verdicts are never touched or re-run on the 14.

**D0.5 The gate script and the liveness rung.** `scripts/gate_pass1_fewshot.py`
(borrow `scripts/gate_lora_b.py`'s record/append shape): `--pre-create-check`,
`--price`, `--gate0`, `--boot`, `--projection` (every 20 calls: elapsed +
remaining calls × MEASURED s/call + the shot's 64 × s/call + overhead ≤ cap at
the live price AND ≤ the hard stop), `--dev-gate` (below), `--close`. **New,
and the reason this contract exists in this shape: `--watch` is a BLOCKING
loop the executor runs for the whole paid session** — it tails the pod's
out-files and log over ssh, and KILLs (deletes the pod, records the gate)
when **no new row or log line has appeared for 600 s, deadline measured from
the LAST event, never from create**. The executor does not poll by hand and
does not leave the loop; the lora-b-run lesson (9 720 s idle) is a script
now, not a habit. Drive every flag at $0 on a fake client; a KILL on a
frozen out-file is a test, and so is a GO on one that advances.

**D0.6 The registration** `results/prereg_pass1_fewshot.json` by a producer
`scripts/write_pass1_fewshot_prereg.py`: bars · population · instruments
(prompt v2 sha, both packs' shas, parser, scorer, runner) · kill clock ·
money with every number's FORMULA and an H6 block that re-derives them all
(step-1 refusal gate: a mismatch STOPS before any pod) · `attempt` ·
`return_to_the_operator`. `make check` green, `make preflight ARGS='PROMPTS
pass1_comment_gm4_v1 build_pass1_sft.py'` output pasted, commits: holdout ·
prompt+tests · neighbours+packs · gate · prereg · vault tail separately.

## The bars (pre-registered; the scorer is the judge, never the eyeball)

- **Judge:** `scorer.reader_comment_agreement` through `score_pass1_probe.bar_p1`,
  the symmetric collapse категория_личное ≡ категория, ABSENT/refusal = a
  disagreement. Same bytes as probe-b and lora-b; a new equality loop is a
  second definition of the bar and is refused.
- **Dev gate (rung 7, before the shot), paired on the same 200 rows:**
  `our_v2 − our_base ≥ 10` (correct rows among the 49 категория/бренд) AND
  `agree_v2 − agree_base ≥ −5` (over all 200). Both or no shot. The base's
  dev numbers are MEASURED in this session, never assumed.
- **The shot:** `gold14(v2) ≥ 12 of 14` on the sealed r2 gold, probe-b's 64
  pack identity, ONE attempt, SPENT at the first gold-row reply. Multiplicity,
  named: this is the THIRD shot at the same fourteen (base, arm A, v2) —
  false-pass odds ≈ 3p — accepted by the operator's «приступаем» and written
  into the record so the verdict is never read as a single shot.
- **Red:** the line closes; nothing iterates in-session; the dev table and
  the per-row 14 go back to the team lead for the next option of the menu
  (synthetic + LoRA, or rationale-supervised LoRA). A green shot ships v2 as
  the pass-1 prompt of the window run (the next contract, ~$1.1 generation
  FLOOR + boot, re-priced at v2's MEASURED s/call).
- **Census-50 profile of v2** beside the base's and arm A's: observation only.

## Money — every number with its formula (H6 re-derives ALL of them, step 1)

- Price ceiling **$0.80/h**; card: probe-b's class (RTX 4090, $0.74/h, the
  card the 5.162 s/call sample was measured on) preferred; an A6000 under the
  ceiling allowed. Volume `qw4nwleanc` pins EU-RO-1.
- Base s/call **5.162** (sample: probe-b, 64 calls, 4090). v2 s/call is
  UNMEASURED (longer prefill): registered as a bound **1.5 × 5.162 = 7.743 s**
  until the projection gate measures it at call 20.
- Seconds: boot 450 (worst 293 × 1.5) + dev base 200 × 5.162 = 1 032.4 + dev
  v2 200 × 7.743 = 1 548.6 + shot 64 × 7.743 = 495.6 + overhead 0.5 h = 1 800
  → **5 326.6 s = 1.4796 h → worst case $1.1837 at the ceiling** (≈$0.78 at
  $0.53/h). **Cap $1.50 all-in**, frozen at the first `pod create`.
- **Cumulative hard stop 1.75 h = 6 300 s ≈ $1.40 at the ceiling < $1.50** —
  `--terminate-after` = create + 6 300 s − seconds billed by closed pods;
  `--open` takes the stamp actually given and refuses overshoot (lora-b's
  rung-7 shape). Session ceiling = cap / ceiling = 1.875 h.
- Recovery: ONE re-creation after a deletion proven by listing, only if guard
  reading + worst-case remaining at MEASURED rates ≤ $1.50 and inside the
  cumulative stop; never two billing endpoints. Guard:
  `PYTHONPATH=src python3.11 scripts/runpod_guard.py --step pass1-fewshot
  --step-cap 1.50` — anchor committed before the pod exists.

## Kill clock (positioned BEFORE the first milestone, clock = the billing one)

1. price ≤ $0.80/h at create else STOP, no endpoint (costPerHr of record);
   backstop stamp checked against the cumulative stop.
2. ssh dead-man ≤ 180 s or KILL. 3. boot → first reply ≤ 450 s or KILL.
4. projection every 20 calls (D0.5) — cap at live price AND hard stop.
5. **liveness: 600 s without a new event → KILL** (script-held, `--watch`).
6. cumulative hard stop 6 300 s (platform-held, read back).
7. dev gate (bars above) — RED → delete, listing, attempt NOT spent, return.
8. the shot — 64 units into its OWN out-file (never a dev file: Dv560 resume
   skip); the attempt is SPENT at the first gold-row reply.
Order on the pod: base-dev → v2-dev → scp both → dev gate on the Mac →
(GO) v2 shot → scp → delete → listing with the volume as positive control.
Guard reading pasted at every rung. Gate records append-only.

## D2 — the verdict ($0)

A scorer `scripts/score_pass1_fewshot.py` (probe-b's scorer through the file
swap, as `score_lora_b.py` did; an arm with no replies is `not_evaluated`;
REFUSES while the run record says a shot happened and its replies are not
on this machine): the dev table (base vs v2, per class, per row), the 14
paired base / arm A (sealed) / v2, census-50 profiles, provenance (prompt
sha, pack shas, neighbours per item, seeds). Report
`docs/reports/pass1-fewshot.md`, path-only; ADR registration + outcome +
what ships. The scorer runs AFTER the last append to the run record (Dv579).

## Read back FIRST, one line each

the dev gate's two inequalities · when the attempt is SPENT · the liveness
rung and who holds it · the hard stop vs the cap · why one example per class
· the four empty contamination lists · base never re-run on the 14.

## DO NOT

No training, no adapter, no second prompt variant, no tuning after any eval
output; never edit `results/prereg_pass1_probe_b.json`, `results/
pass1_probe_b_pack.json`, the gold, the labels or the base verdict; never
the sealed 14 before the dev gate says GO; never leave `--watch`; never two
billing endpoints. Team-lead files verbatim (docs/STATUS.md, docs/SPEC.md,
docs/PROMPT-*.md). Report path-only in chat.
