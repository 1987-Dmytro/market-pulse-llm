# PROMPT — lora-b-run ADDENDUM: the Deviations table, the vault tail, and one pin ($0)

**The report `docs/reports/lora-b-run.md` is ACCEPTED by the team lead on
evidence (own suite 3 169 / 2, own scorer re-run, own guard reading LORA-B
$2.3624 of $6.00, own cloud listing `[]` with the volume as positive control,
fresh-context refutation pass). The operator's ruling at acceptance, verbatim:
«Красный = ответ, линия B закрыта» — RED stands, line B is CLOSED, sitting C
is next. Nothing below reopens the bar. This addendum is the ADDENDUM cycle
of the skill: append-only writes, separate commits, gates re-run after the
writes, an ADDENDUM section in the same report.**

Deviations continue from **Dv575**, closed enum v2 (`contract-gap | spec-gap |
verify-gap | env | tooling | model | process`), optional `[[lesson-name]]`.
No pod, no training, no eval, no touch of `results/prereg_lora_b.json`, the
datasets, the gold, the base verdict or the replies. Team-lead files
(docs/STATUS.md, docs/SPEC.md, docs/PROMPT-*.md) are committed verbatim,
never edited. Never `git add -A`. Report path-only in chat.

## Step 0 — the vault tail, its own commit FIRST

`git status --porcelain` shows `knowledge/hot.md`, `knowledge/daily_logs/
2026-08-20.md`, `knowledge/index.md` modified and uncommitted (the /close
tail). Commit them as ONE vault commit before anything else. Paste the
`git status` before and after.

## 1. The Deviations section the report is missing

The report has Process signals but NO `## Deviations from Dv575` table —
the skill's «silence is not compliance» rule. Add it (append-only, above the
Process section is fine) as the lora-b.md table shape: `| Dv | finding |
tag |`. The team lead's acceptance found the candidates below — VERIFY each
against the artifacts (results/lora_b_run.json, the loss log, the verdict,
the guard), merge or split as the evidence says, keep the numbering dense,
and tag every row from the closed enum. An off-enum or empty tag is returned.

Candidates (team-lead readings; the numbers in brackets are what the team
lead re-derived — reproduce them, do not trust them):

- **Dv575** — 9 720 s of idle billing ($1.43): arm A finished 14:38:23Z, next
  poll ~17:20Z; rungs 4 and 8 were never read while the meter ran; no rung
  watches a pod that is not training. It cost arm B. `[cause: process]`
- **Dv576** — the registered step formula `ceil(n/16) × 2` is not the
  trainer's: the trainer completes only whole accumulation groups, so arm A
  ran 62 (registered 64) and arm B would run 80 (registered 82); the
  arm-b-fit snapshot priced «79 steps», which matches neither. `[cause:
  verify-gap]`
- **Dv577** — the arm-b-fit snapshot says «cumulative hard stop leaves
  5 437 s»; 19 800 − (17:21:55Z − 13:21:44Z = 14 411 s) = 5 389 s. The
  platform figure 4 787 s re-derives (4 788). No gate flips. `[cause:
  verify-gap]`
- **Dv578** — the boot GO snapshot is stamped 13:29:44Z = 480 s after create
  for a 450 s rung; the event itself (loop start 13:27:37Z, 353 s) was in
  time — the gate was READ late, not missed. `[cause: process]`
- **Dv579** — `results/lora_b_verdict.json` `provenance.run_record.sha256`
  (3d0277c7…) pins a state of `results/lora_b_run.json` git never saw: the
  `train-a-retrospective` entry was appended at 17:40:15Z AFTER the scorer
  ran. Fixed by §2 below. `[cause: process]`
- **Dv580** — the rung-5 milestone reading was taken post-idle (17:21:21Z,
  $2.1938), not «after arm A» (14:38Z, ≈$0.7 by the clock). GO either way.
  `[cause: process]`
- **Dv581** — the projection gate carries two tightenings beyond the
  contract's letter (arm B priced at the RUNNING rate; the hard stop as a
  second bound) — registered with the worked examples that make them
  necessary. `[cause: contract-gap]`
- **Dv582** — the «arm-A-only branch» was applied to a CLOCK refusal whose
  cause was Dv575, and the registration is silent on the alternative that
  existed (close after the smoke, before any gold-row reply, attempt NOT
  spent, return to the team lead). Ruled at acceptance: RED stands.
  `[cause: spec-gap]`
- **Dv583** — the brief's mask-boundary mechanism named the merge that was
  already supervised (`к"`), not the one that straddled (`",`); the number
  (+1) was right, the sentence one character off. `[cause: verify-gap]`
- **Dv584** — the registration named `score_lora_b` as the judge of the bar
  and the file did not exist before this session. `[cause: contract-gap]`
- **Dv585** — rung 1 registered the card's PRICE, not its availability; the
  A6000 was out of stock in the pinned datacenter; the operator ruled
  «wait» and the window reopened. `[cause: contract-gap]`
- **Dv586** — at acceptance the guard's billing-history arm read pods
  $1.9823 against the clock's $2.2671 (~1 934 s unposted); the pessimistic
  balance-delta arm ($2.3624) is the one that gates — the Dv504 class.
  `[cause: env]`

Close the table with the split tally line: contract-health = contract-gap
+ spec-gap + verify-gap; paid = the rest. Then add `## ADDENDUM` to the
report: the operator's ruling quoted verbatim, what this addendum wrote,
the commit shas.

## 2. The one pin — re-run the scorer over the FINAL run record

The team lead's own `PYTHONPATH=src python3.11 scripts/score_lora_b.py
--outdir /tmp/x` reproduced the committed verdict byte-for-byte EXCEPT the
single leaf `provenance.run_record.sha256` (Dv579). Re-run the scorer in
place and show the before/after diff of `results/lora_b_verdict.json` — it
must contain exactly that one leaf and nothing else; if anything else
moves, STOP and report instead of committing. This is a derived record
re-read from unchanged inputs (gold, base verdict, pack, replies — their
shas are asserted inside the file), not a re-pin of a sealed one. Commit it
alone, with the message naming Dv579. The ADR
`knowledge/decisions/lora-b-red-and-line-b-closes.md` gains ONE line:
the scorer runs after the LAST append to the run record, or its pin is of
a state nobody can check out.

## 3. Gates after the writes

`make check` green (paste the final line; 3 169 / 2 is the team lead's own
count — a different number is a finding, not a rounding). `git status`
clean. Commits: vault tail · report addendum · verdict re-run (+ ADR line).
Report closes with its Process signals updated if anything above changed
them. Path-only in chat.
