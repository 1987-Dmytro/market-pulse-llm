---
type: decision
date: 2026-08-17
status: accepted
tags: [decision, phase6, comment-signals, reader, prompt, chunking, stop-rule, cost]
---

# reader-v4 accepted as an honest negative, and the sitting of 17.08 rules instrument v5

**The layer is measured.** `reader-v4` read all 23 registered threads on one rented pod and every
bar was computed. The team lead ACCEPTED it on 2026-08-17 as an honest NEGATIVE result: the money
worked, the transport worked, the parser was fixed — and the reader still does not read.

## What v4 bought

Verdict `results/reader_v4_verdict.json` (`79c6c796512434bd…` after the step's close; the record the
report `docs/reports/reader-v4.md` quotes is `7f5c96c8352ad052…`, whose ONLY difference is bar 5).

| bar | verdict | number | uncollapsed | probe-b |
|---|---|---|---|---|
| `1_flagships` | **FAIL** | 2 of 5 | 1 of 5 | 2 of 5 |
| `2_entity_cases` | PASS | 4 of 4 | — | 2 of 4 |
| `3_noise` | PASS | 0 signals over five answered threads | — | 0 |
| `4_per_comment_agreement` | **FAIL** | 0.500 against a bar of 0.80 | 0.357 | 0.429 collapsed |
| `5_time_and_cost` | PASS | **$0.236118** settled of $0.35 | — | $0.313162 |

**Three of five pass.** Bar 5 closed on 2026-08-17 once the billing walk posted: step resources
`$0.236118`, pods only, `serverless $0.0000`; the `$0.391674` headline of the same walk is the
always-on network volume dripping into an open window and belongs to no step.

**The containers are cured and the reading is not.** 19 of 23 replies parsed against probe-b's 13,
and **zero of the nine registered container repairs fired** — the recovery did not come from a
repair, because none ran. What is left is attribution: all four bar-4 disagreements are
`subject_type`, and not one of them is a vocabulary disagreement (every gold value compared is
already the collapsed one). The reader reads a comment about a category as a comment about the
chain. Beside that, one requested row in six is simply not written — **93 `per_comment` rows
returned against 111 requested (0.838)** — and three of bar 4's fourteen gold rows are absent for
that reason alone.

**The attempt is spent.** The registration's own clause — one attempt, and a completed run with a
failed bar closes the question — means what follows is a sitting and a new registration, never a
second pass at v4.

## The sitting of 17.08 — the operator's rulings, recorded as they were given

**(a) The attribution block goes into the prompt.** The subject of a signal and of a `per_comment`
row is read off THE COMMENT ITSELF, never off the thread's protagonist. The test is a swap: would
the complaint or the praise survive the chain or the brand being exchanged for another? Then it is
«категория_личное» — not the chain and not the brand. «сеть_ритейлер» is the subject only where the
shop AS a shop is what is discussed: its service, its checkout, its delivery, its shelves. The
aspect half of the same disease is ruled with it: the aspect names what the text is ABOUT, not what
the product is enjoyed for.

**(b) The «two objects» class is killed by the TRANSPORT.** The runner stops generation at the first
balanced top-level JSON object. The prompt line and the parser's refuse-on-conflict clause stay as
defence; they are no longer the cure. Two of v4's four refusals were `two disagreeing objects`.

**(c) The F2a carve-out, and it is narrow.** An event that changes the availability or the status of
the POST's subject — a destroyed warehouse, a recalled batch, a delisting — is a signal about the
post's subject even where the comment does not name it. **Opinions without a name are still never
carried over**: the old law stands for them, and the carve-out is scoped to events about
availability or status.

**(d) Completeness is echoed, and the chunking mechanism is tested on a real thread.** The request
lists the payable msg_ids; `per_comment` carries one row for EVERY id on that list, in list order,
and the shortfall is printed BESIDE the bars rather than folded into them. The mechanism itself is
bought once, on `@klopotenkofood:6040` — 43 payable comments, chunks of ≤16 — with its own
MECHANICAL bars, held apart from the semantic ones and unable to touch them. The window's giants
(125 / 108 / 105 payable comments) go to the window afterwards, under a mechanism that has been
proven.

**(e) The cap for v5 is $0.45**, one pod, kill rule as code.

**(f) The PROGRAMME STOP-RULE, pre-registered inside the v5 record.** If v5 completes and bars 1
and 4 are not BOTH taken, **the prompt-engineering line CLOSES**. The next step is an architecture
sitting — two passes, labelled data, a different base — and never a v6 of the same kind.

**And one constraint on the executor:** every example inside the prompt is SYNTHETIC, with a
grep proof that it occurs in no stored comment and in no gold file. Teaching the exam is a red gate.

## Two instrument notes the phase leaves behind

- **Gate records were OVERWRITTEN in `results/reader_v4_run.json`** — the first GO snapshot was
  displaced by the re-gate at twelve threads. The arithmetic was re-checked by hand against the
  jsonl and agrees; the next transport contract keeps a `gates` LIST and appends.
- **A detached launch must not hold the ssh channel** (Dv454) and **every verify command names
  `python3.11`**: the team lead's own scorer run failed on the system `python3` (3.9) before
  reproducing byte-identically on 3.11.

Related: [[reader-v3-serverless-close-and-the-pod-ruling]] (the ruling that made this measurement
affordable), [[reader-sitting-16-08]] (rulings 2 and 4, whose worth this run measures),
[[the-d-cut-and-the-fourth-kind]].
