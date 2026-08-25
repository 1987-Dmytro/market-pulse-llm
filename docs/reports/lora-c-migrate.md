# `lora-c-migrate` — the datacenter the ruling names cannot hold the volume

**STOP, at $0.0000 of $1.00.** Ruling (р) moves the training line to **EU-SE-1, RTX A6000 48 GB,
$0.53/h**, and D2's first action is «create the volume in EU-SE-1». **EU-SE-1 does not support
network volumes.** RunPod's own volume-create endpoint enumerates the 21 datacenters that do and
EU-SE-1 is not among them — a reading taken for free, before anything was created. And the card is
`Low` in EU-SE-1 alone: in every datacenter that *can* hold the volume it reads `none`.

No volume was created. No pod was created. Nothing was trained, nothing was evaluated, the frozen
registration is byte-identical and the attempt is UNSPENT. What this session bought instead is the
intersection the ruling was taken without — plus the two guard debts Step 0.5 owed, one of which
settled and one of which refused.

**The card and the datacenter remain the operator's to name.** §5 is a table, not a choice.

## The commits

| commit | what |
|---|---|
| `9bd250a` | the team-lead files — `docs/PROMPT-lora-c-migrate.md` and the STATUS write-up of ruling (р) — verbatim |
| `e3fc756` | the `/save` vault tail, committed before any stamped reading because `hot.md` is a suite input and sits outside `check-stamped`'s whitelist by name |
| `42a0ccb` | `scripts/probe_lora_c_migrate_stock.py` and its reading — the refusal, the two catalogues, the intersection |
| `a609b0e` | `results/prereg_lora_c_migrate.json` — D1, registered as EVIDENCE and marked as not law |
| `9003c0b` | step 0.5's two closes — r2 settled and appended, the vramprobe refused and left open |
| `aa9d946` | `tests/test_lora_c_migrate.py` — 37 tests |
| `e925ab7` | `scripts/check_lora_c_migrate_report.py` and this report — 63 of 63 numbers re-derived |
| `03cb8fd` | the vault tail: `hot.md`'s curated block and today's log |
| *(this)* | the closing stamped reading, and the commit table completed |

---

## §1 — the answer, from the platform's own refusal

A network volume can only be attached to a pod in **its own** datacenter. `scripts/runbook_4a.md`
§1 chose CA-MTL-3 on exactly that intersection back on 2026-08-01, and named EU-SE-1 as a
datacenter that held the card but not a volume. Ruling (р) rests on `docs/reports/lora-c-vramprobe.md`
§5, which read where the card is and never asked where a volume may live. Those are two different
lists.

The free test is a create that is refused, which is $0 and creates nothing:

```
$ runpodctl network-volume create --name probe --size 1 --data-center-id NOPE
{"error":"failed to create volume: create network volume: Data center \"NOPE\" not found or does
not support network volumes. Available data centers: AP-IN-2, AP-JP-1, CA-MTL-3, CA-MTL-4, EU-FR-1,
EU-NL-1, EU-RO-1, EUR-IS-1, EUR-IS-3, EUR-IS-4, EUR-NO-1, EUR-NO-2, US-CA-2, US-CO-1, US-IL-1,
US-KS-2, US-MO-2, US-NC-2, US-NE-1, US-TX-3, US-WA-1.","code":"server_error","status":500}
```

**21 datacenters.** EU-SE-1 is absent — and so is US-TX-1, the other datacenter §5 named for this
card, and so are EUR-IS-2 and US-PA-1, which §5 named for the MIG slice. That message comes from the
create path itself, not from a catalogue standing beside it ([[a_stock_window_needs_the_create_not_a_poll]]).
`runpodctl network-volume list` was read before and after and is byte-identical in the record: the
refusal created nothing.

And the card, datacenter by datacenter, from `results/lora_c_migrate_stock.json` at
`2026-08-25T18:01:18Z`:

| RTX A6000 48 GB, $0.53/h | stock | takes a network volume |
|---|---|---|
| EU-SE-1 — **the ruling's** | `Low` | **no** |
| US-TX-1 | `none` | no |
| CA-MTL-3 | `none` | yes |
| EU-RO-1 — **the existing volume's** | `none` | yes |
| US-KS-2 | `none` | yes |

Both halves fail, and either half alone is enough: the datacenter cannot hold the volume, and the
card is not obtainable in any datacenter that can. No create was attempted in EU-SE-1 — the endpoint
that would have to accept it has already said which datacenters it accepts, and a second attempt
would add a create-shaped risk to a question already answered. That limit is named rather than
left implicit: what is proven is that the endpoint does not list EU-SE-1.

**Two independent listings, cross-checked.** `datacenter list` spells out-of-stock as `''` and
`gpu list --include-unavailable` spells it `none`. Both were read, normalised and compared pair by
pair: **137 pairs, 0 disagreements.** A card in stock in one surface and absent in the other would
be a row in the record, not a silent average.

---

## §2 — the gates, none of which was reached

The contract registers six rungs. Every one of them is downstream of a create that never happened,
so this table is what an honest gates table looks like when the answer arrives before the money — a
rung reported as NOT REACHED, never as a passing reading.

| rung | what | threshold | reading |
|---|---|---|---|
| 0 | the create refusal | free | **NOT REACHED** — the volume the pod would mount cannot exist |
| 1 | the boot gate | 500 s | NOT REACHED — no pod |
| 2 | the download deadline | 2 400 s, liveness 600 s | NOT REACHED — no pod |
| 3 | the model-load proof | 600 s | **NOT REACHED — and this is the deliverable that did not land.** D2 calls the load proof the deliverable, «a volume nobody loaded from is a hope». There is no volume |
| 6 | the platform backstop | 3 600 s | NOT REACHED — nothing was created to carry a `--terminate-after` |
| 7 | never two billing resources | 1 pod | **HELD trivially** — `runpodctl pod list -a` is `[]` at `2026-08-25T17:48Z` and again at `2026-08-25T18:12:22Z`, `serverless list` empty in both |

---

## §3 — what the plan's own numbers said, before the money

Four findings from reading the registered rungs against the instruments that would have graded
them. All four are independent of which card is chosen, so the next contract inherits them checked.

**(a) The hard stop must be an inequality, and the guard on hand asserts an equality.** The
vramprobe's `the_hard_stop_is_solved_at_the_observed_price` requires `cap / price × 3600` to *equal*
the registered hard stop within 1.0 s. That held there by accident of its numbers — $0.30 ÷ $0.72 ×
3600 is 1 500.0 exactly, and its own docstring says the cap and the hard stop were one constraint
with no headroom. Here $1.00 ÷ $0.53 × 3600 = **6 792.45 s** against a registered **3 600 s**, so the
same helper raises `SystemExit` — on `--open`, which runs when the pod already exists and the meter
is already running. The rule that generalises is `cap / price × 3600 ≥ hard_stop`: the backstop must
be **affordable**, not equal to the cap. Registered, and driven both ways in the suite.

At the ruling's own price the cap divides as **$0.53 of pod at the hard stop + ~$0.24 for the new
volume's first day = $0.77 of $1.00** — which is what «$1.00 all-in» and «the volume's rent named
separately» mean together. 3 600 s is 53.0% of what the cap buys.

**(b) The deadlines do not fit inside the hard stop at their bounds.** boot 500 + download 2 400 +
load proof 600 = **3 500 s** against a **3 600 s** hard stop measured from create, leaving **100 s**
for the mount, the git bundle, the venv, the two SFT files, the eval and pass-2 packs and the
teardown — and the vramprobe measured its own teardown at 19 s and carries 90, which alone leaves
10. In practice the measured path fits easily (ssh 23.2 s and 29.4 s on the last two pods; 62 GB
downloaded in 240 s per `scripts/runbook_4b.md`; 177.3 s to the first token on a warm volume per
`docs/reports/lora-c-run-r2.md`) — but a kill clock is made of bounds, and these bounds cross. The
order is not rearranged to fix it: the contract fixes the order and reordering would be a scope
change.

**The venv is the stage nobody priced.** A *new* volume has no `/workspace/venv` and no
`/workspace/hf`. `scripts/runbook_4a.md` §4 builds the venv with `--system-site-packages` and
`pip install -e '.[dev,gpu]'` before anything loads. D2 does not name that stage, no rung bounds it,
and this repo holds no measurement of how long it takes — searched, absent.

**(c) A download's liveness cannot be read off a log line.** Rung 2 words its liveness as «600 s
from the last progress line». `hf download` renders CR-based progress bars: a healthy 59 GB download
can leave `tail -1` unchanged for minutes while bytes keep landing, and the rung would KILL a
working pod. The reading that is actually alive is growth in `du -sb /workspace/hf` between two
stamped polls — bytes, not lines ([[no_rung_watches_an_idle_pod]]). Rung 2 also carries **two**
thresholds in one sentence, and `first_number` — how every rung in this line reads its own
threshold — returns only the first. The liveness deadline is registered as a field of its own so it
is a value and not a phrase ([[a_threshold_that_lives_in_prose]]).

**(d) `first_number` would have read the card's name as a price.** `gate_lora_c.price_gate` takes
its ceiling from `first_number(rung(record, 0)["rule"])`. A rung-0 rule worded the way the contract
words it — «card `RTX A6000` at ≤$0.60/h» — yields **6 000.0**, and `over = usd_per_hour > 6000.0`
is vacuously false for every pod RunPod rents. Silently, with the suite green. The safe wording is
price-first, as the vramprobe's rung 0 has it. Both strings are in the suite, and the hazardous one
is asserted to return 6 000.0 so the negative control cannot rot.

---

## §4 — the money

**$0.0000 of the $1.00 cap.** No pod, no volume, no serverless endpoint. Cycle 2 stands unchanged at
**$9.4659 of $20.00, $10.5341 remaining** — the only movement against it this session is the
network volume's own drip, which is always-on and beside every step by rule.

**Step 0.5's two debts, at the tolerance this line's own runbook names (`0.07`, `scripts/runbook_lora_c.md`
line 288 — not a number chosen here to make a close go green):**

| step | verdict | settled | the ledger's recorded reading | off | pod clock |
|---|---|---|---|---|---|
| `lora-c` (r2) | **CLOSED** | $0.764952 | $0.7338 | 4.2% | $0.7606 |
| `lora-c-vramprobe` | **REFUSED — stays open and named** | $0.075729 | $0.0495 | **53.0%** | $0.0752 |

The billing walk has caught up: a day ago it read $0.0602 for a session the pod clock priced at
$0.7606, and it now settles at $0.764952 over a window of 3 803 927 ms against the run record's
3 803 000. **What refuses the probe's close is not the settled figure — it is the ledger's own
recorded reading.** $0.075729 settled is within 0.7% of the pod clock's $0.0752; $0.0495 is a
balance delta taken **21 s after the pod was deleted**, before the platform had settled it.

And the two rows together say something the band cannot see. Both readings lag the settled figure by
about the same *absolute* amount — **$0.031152** on r2 and **$0.026229** on the probe — and produce
relative errors of 4.2% and 53.0%. The difference is the size of the step, not the quality of either
reading. A 7% band needs `recorded ≥ lag / 0.07`, which at these lags is roughly **$0.37 to $0.45**:
**a step that spends less than that cannot close at 7% however correct it is.** Two points, n = 2,
and not fixed here — the guard's band is not this contract's scope. The debt is carried named.

---

## §5 — what the operator is being asked

Ruling (р)'s economics rest on **$0.53/h**, and that price is exactly the one that is not
obtainable. The reading below is `results/lora_c_migrate_stock.json` at `2026-08-25T18:01:18Z`:
**19** cards of 48 GB or more are in stock in a datacenter that can hold a network volume.

| the cheapest that exist | $/h | GB | datacenter | stock |
|---|---|---|---|---|
| PRO 6000 MIG 48GB | **$1.09** | 48 | US-NE-1 | `Low` |
| A100 PCIe | $1.39 | 80 | CA-MTL-3 | `Low` |
| RTX PRO 6000 | $2.09 | 96 | EU-NL-1, **EU-RO-1**, EUR-IS-1, US-KS-2, US-MO-2, US-NC-2, US-NE-1 | `Low` |

**No migration is needed to reach a card that fits.** The existing volume's own datacenter, EU-RO-1,
holds the **RTX PRO 6000 96 GB at $2.09/h** in stock today — the card ruling (п) has already
declared non-fitting at ~$11 a session. Everything cheaper than it that fits requires a *new* volume:
59 GB re-downloaded and a second ~$0.24/day rent, neither priced by any registration this line
holds.

**And the remaining r2 cap does not reach the only step-rate this repo has measured, at any
obtainable price.** $4.00 − $0.7606 = **$3.2394**, against 150 optimizer steps (144 registered plus
a re-run smoke) and the fixed part charged at ruling (п)'s **9.20 s/call**:

| $/h | seconds the cap buys | ≤ s/step, fixed 6 577.2 | ≤ s/step, fixed 7 721.2 | obtainable |
|---|---|---|---|---|
| **0.53** — the ruling's | 22 003.5 | **102.84** | 95.22 | **no** |
| 1.09 | 10 698.9 | 27.48 | 19.85 | yes |
| 1.39 | 8 389.8 | 12.08 | 4.46 | yes |
| 2.09 | 5 579.8 | **−6.65** | −14.28 | yes |

lora-b measured **61.047 s/step** on a 48 GB A6000 with rows of at most 1 222 tokens; this line's
rows run to 2 975. At $2.09 the cap is exhausted **before a single optimizer step**. And the
conclusion survives a faster card: halve every model-dependent charge — a factor larger than this
stack's own measured card-to-card spread of 1.65× — and $2.09/h still leaves **12.61 s/step**, a
fifth of the only rate ever measured here. The prices above 2.09 in the reading (3.19, 3.29, 4.59,
6.79, 7.89) are strictly worse and already negative.

So the choice in front of the operator is not «which datacenter» — it is whether to raise the cap,
shrink the plan, or wait for a $0.53 A6000 to reappear in a volume-capable datacenter. **None of the
three is taken here**, and the r3 contract remains the next team-lead session's to write.

One volatility reading, stated as what it is: a probe run 13 minutes earlier in this same session
listed **22** candidates rather than 19, with three A100 SXM rows present and A100 PCIe absent. That
run's output was not kept as an artifact and is quoted only for the direction — stock moves inside a
quarter of an hour, in both directions, and a listing dates the question rather than answering it.

---

## §6 — the numeric session audit

| | |
|---|---|
| volumes created | **0** · pods created **0** · serverless **0** |
| creates attempted | 1, deliberately refused, `--data-center-id NOPE`, $0 |
| billed this contract | **$0.0000** of $1.00 |
| optimizer steps | **0** · eval replies **0** · adapters **0** |
| the attempt | **UNSPENT** — no adapter leg has answered against eval set E |
| `results/prereg_lora_c.json` | FROZEN and byte-identical, sha `4d5a8f1d34765b4a` |
| `mp-srv2` | untouched — no writes, no deletion; `qw4nwleanc`, 100 GB, EU-RO-1 |
| closing listing, `2026-08-25T18:12:22Z` | pods `[]` · serverless `[]` · **one volume**, `mp-srv2`. The contract's «both volumes» closing state has one member because the second was never created |
| formatter | 2 files drifted, both left alone, **both pinned by a record** — checked by sha, not assumed |
| numbers in this report re-derived from their own file | **`python3.11 scripts/check_lora_c_migrate_report.py`** — and the suite drives it |
| suite, baseline | **3 806 passed / 2 skipped**, `make check-stamped` «reading HOLDS» at `e3fc756` |
| suite, closing | **3 843 passed / 2 skipped**, «reading HOLDS» at `295815f`, tree unmoved outside the two whitelisted Stop-hook outputs. The first attempt of this reading was **killed** at 3 842/1 and is reported as killed, never as a pass — the one failure it surfaced is Dv828 |

| file | sha256 (first 16) |
|---|---|
| `results/lora_c_migrate_stock.json` | `90b70c914e9a5623` |
| `results/prereg_lora_c_migrate.json` | `089f3a740511c7ba` |
| `scripts/probe_lora_c_migrate_stock.py` | `6d4e1a5fa60f311b` |
| `scripts/check_lora_c_migrate_report.py` | `52ea8139f2deb92f` |
| `tests/test_lora_c_migrate.py` | `9fa09ccf8028ddd3` |

---

## Deviations — from Dv820, enum v2

| Dv | cause | what |
|---|---|---|
| **820** | contract-gap | **the contract's first action is refused by the platform.** Ruling (р) and D2 name EU-SE-1, which does not support network volumes; the create endpoint's own refusal lists 21 that do and EU-SE-1 is not one. D2 was not executed and D1 was written as EVIDENCE rather than as law. $0 spent |
| **821** | verify-gap | **the ruling rests on a table this executor produced, and that table answered a different question.** `docs/reports/lora-c-vramprobe.md` §5 read where the A6000 is and never asked where a volume may live — a capability the whole plan depends on: **all four** datacenters §5 named (EU-SE-1, US-TX-1, EUR-IS-2, US-PA-1) cannot hold one — the capable list has US-TX-**3** and EUR-IS-1/3/4, which are different datacenters ([[a_capability_gate_is_not_a_theme_gate]]) |
| **822** | contract-gap | boot 500 + download 2 400 + load 600 = 3 500 s against a 3 600 s hard stop, with the mount, the bundle, the venv, the packs and the teardown still owed — and the **venv stage is named by no rung at all** and measured nowhere in this repo. §3 (b) |
| **823** | verify-gap | the vramprobe's hard-stop helper asserts an EQUALITY that held only at that probe's numbers; at $1.00 and $0.53 it raises `SystemExit` on `--open`, after the meter starts. §3 (a) |
| **824** | contract-gap | rung 2 words its liveness as «the last progress line», and `hf download`'s CR-based progress bars make that a false-KILL instrument on a healthy pod; and it carries two thresholds in one rule where `first_number` reaches only the first. §3 (c) |
| **825** | verify-gap | `first_number` on a rung-0 rule worded card-first returns **6 000.0** out of «RTX A6000», making the price ceiling vacuous with the suite green. §3 (d) |
| **826** | process | **no gate script was written.** `scripts/gate_lora_c_migrate.py` would have been the producer of six rungs for a plan that cannot execute, and every number in it — cap, hard stop, price column, card — changes with the operator's answer. Named as a deliberate non-deliverable rather than shipped as speculative code |
| **827** | tooling | the `--close` of the cheaper of the two debts is **unreachable at the registered tolerance**: a fixed absolute settlement lag (~$0.026–0.031 at 16–21 s after the delete) is 4.2% of an $0.73 step and 53.0% of a $0.075 one. The refusal is recorded as the contract asks; the band is not touched. §4 |
| **828** | verify-gap | **step 0.5's close broke the PREVIOUS contract's report checker, and the suite is what said so.** `check_lora_c_vramprobe_report.py` derived cycle 2's spend from `results/spend_cycle2.json`'s **last** row — true only while nothing else wrote — and the close appended a later reading. Fixed by selecting that report's own row by stamp, raising on absent-or-duplicated rather than picking a neighbour; the sealed report's numbers are untouched and a provenance note records that the checker's sha moved to `42a6efd7…` ([[select_one_row_refuse_ambiguity]], [[rewriting_a_record_resets_state_you_do_not_own]]) |

`contract-gap 3 · verify-gap 4 · tooling 1 · process 1` — nine, against nine rows.

---

## Process signals

- **The cheapest reading in this contract refuted its most expensive assumption.** One refused
  create, $0, answered in a second what a $1.00 paid step would have discovered at the first
  command — and it was reachable the whole time, documented in this repo's own
  `scripts/runbook_4a.md` since 2026-08-01.
- **Two lists that share most of their names are not the same list.** «Where is the card» and
  «where can the volume live» overlap in CA-MTL-3, EU-RO-1 and US-KS-2, which is exactly why reading
  one and acting on the other survived a report, a ruling and a contract.
- **A relative band cannot grade a cheap step.** The guard refused the smaller close on a 53% miss
  whose absolute size was smaller than the one it accepted at 4.2%. Reported, not tuned.
