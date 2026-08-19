# labels-boot-audit — the labels are sealed in the commit that flips their clocks, and the census learns the loader's axis

**Contract:** `docs/PROMPT-labels-boot-audit.md` ($0, no cloud call). **Deviations from Dv532.**
Cause tags from the closed enum v2 only; lesson names ride as trailing `[[wiki-name]]`.

## Read back, before the first edit

1. **The sealing commit is ATOMIC** — labels verbatim + the freeze with its provenance pin + both
   test flips in ONE commit, staged by explicit path, so a fresh clone never sees the file without
   the tests that seal it and `make check` is green from that commit on.
2. **The census may not move `TARGET_KTOK = 9.0` or the warning text** — ruling 2 suspends the
   target, it does not re-site it; what changes is the AXIS the MEMORY.md share is measured on.
3. **The audit prep is a TABLE in this report, not an edit** — every block of `knowledge/hot.md`
   and the three `CLAUDE.md` classified hot / cold-candidate with a durable home named; what leaves
   is the joint sitting's decision, and no row of the table recommends an eviction.
4. **The pin duty for the frozen labels** — `shasum` before staging and after committing, printed
   and equal; the sidecar's sha fields carry the shape `scripts/preflight.py` parses, so the labels
   file reads as PINNED with its digest matching.
5. **`knowledge/hot.md` gets exactly two edits** — the red-suite blocker closes naming the sealing
   commit's sha, and the boot-tax blocker's open half becomes the ruling. Sealed AUTO-GEN markers
   byte-intact, the `~$0.24/day` literal untouched, nothing else in the file cut.

## Step 0 — the tail, checked against the live porcelain at my start

```
$ git status --porcelain
 M docs/STATUS.md
 M knowledge/daily_logs/2026-08-18.md
 M knowledge/hot.md
 M knowledge/index.md
?? docs/PROMPT-labels-boot-audit.md
?? docs/labels-pass1-r1.jsonl
?? knowledge/daily_logs/2026-08-19.md
```

Seven paths, and the contract explains all seven: three vault files to commit 1, two team-lead
files to commit 2, `docs/labels-pass1-r1.jsonl` to D1, `knowledge/hot.md` held back for D3 because
its two edits are this contract's own deliverable. Nothing unexplained, so nothing to stop for.

| commit | what |
|---|---|
| `0bb52b5` | `knowledge/daily_logs/2026-08-18.md`, `knowledge/daily_logs/2026-08-19.md`, `knowledge/index.md` |
| `85256b4` | `docs/STATUS.md` + `docs/PROMPT-labels-boot-audit.md`, verbatim, never edited |

## Step 1 — the refusal gate (H6): the baseline distribution re-derived

The contract quotes the labels' distribution and asks for it back as a refusal gate. Counted off
the file itself, not read out of the validator's own summary:

```
$ PYTHONPATH=src python3.11 scripts/validate_pass1_labels.py docs/labels-pass1-r1.jsonl
OK — 500 rows, every one of 500 drawn units answered once
  не_наш_рынок       251    50.2%
  null               167    33.4%
  сеть_ритейлер       44     8.8%
  категория_личное    36     7.2%
  молочный_бренд       2     0.4%
exit=0

$ (independent count, json.loads per line)
  не_наш_рынок 251 · null 167 · сеть_ритейлер 44 · категория_личное 36 · молочный_бренд 2
  sum = 500   rows = 500
```

251 + 167 + 44 + 36 + 2 = 500 reproduces exactly, and `wc -l` reads 500. The gate passes.

The red baseline reproduces too, on the two files the contract names:

```
$ python3.11 -m pytest tests/test_pass1_label_pack.py tests/test_validate_pass1_labels.py -q
FAILED tests/test_pass1_label_pack.py::test_the_pack_names_who_writes_the_labels
FAILED tests/test_validate_pass1_labels.py::test_the_domain_is_the_prompt_s_and_the_real_labels_file_does_not_exist
2 failed, 30 passed in 17.17s
```

## D1 — the sealing commit `8d2e1ba`

### The labels, verbatim

```
$ shasum -a 256 docs/labels-pass1-r1.jsonl          # BEFORE staging
776b204f3d3aa1a193f0faad7f68198595c81963199124efca8f6b74a9e1c920

$ shasum -a 256 docs/labels-pass1-r1.jsonl results/labels_pass1_r1.jsonl   # after committing
776b204f3d3aa1a193f0faad7f68198595c81963199124efca8f6b74a9e1c920  docs/labels-pass1-r1.jsonl
776b204f3d3aa1a193f0faad7f68198595c81963199124efca8f6b74a9e1c920  results/labels_pass1_r1.jsonl

$ git show HEAD:docs/labels-pass1-r1.jsonl | shasum -a 256
776b204f3d3aa1a193f0faad7f68198595c81963199124efca8f6b74a9e1c920  -
```

Equal before staging, after committing, and out of git — the third reading is the one that says the
COMMITTED bytes are the team lead's bytes, which the working tree alone cannot say.

### The freeze and its provenance

`results/labels_pass1_r1.jsonl` is a byte-identical copy (`cmp` silent), and
`results/labels_pass1_r1_provenance.json` (2 255 B) carries what the pack record left as an
explicit debt — its own `labels.provenance_debt` says «frozen into results/ by the NEXT contract,
after the labels exist and validate»:

| field | value |
|---|---|
| `labels.labelled_by` / `.date` | the TEAM LEAD, by hand, off `docs/label-pack-pass1-r1.md` · 2026-08-18 |
| `codebook.file` / `.law` | `docs/label-pack-pass1-r1.md` — attribution law v5 in the same bytes + the F2a carve-out + the gold r2 rulings |
| `pack.file` / `.seed` / `.units` | `results/pass1_label_pack_r1.json` · 20260818 · 500 |
| `distribution` | the five counts above |
| `ablation` | training data, ablated with/without at training time; the bar stays the sealed gold r2 ≥12/14 |
| sha fields | `labels`, `frozen`, `codebook`, `pack` — every digest computed at write time, none copied from prose |

The record is the PIN as well as the provenance: each block pairs a `file` key (in preflight's
`PATH_KEYS`) with a `sha256` sibling, which is the first of the three shapes
`scripts/preflight.py` parses.

### The flip, and what replaced the clock

`test_the_pack_names_who_writes_the_labels` keeps its name and its two record asserts; one line
inverts. `test_the_domain_is_the_prompt_s_and_the_real_labels_file_does_not_exist` is RENAMED to
`…_and_the_real_labels_file_is_sealed`, because a name that asserts the opposite of its body is the
defect being removed rather than a detail. Its body now guards: the file exists · 500 rows, equal to
the distribution's own sum · the distribution · the validator's exit-0 path driven on the REAL file
(`gate.main([str(gate.LABELS), "--pack", str(gate.PACK)])`). Beside it a second test proves the
freeze byte-for-byte and re-derives all four digests out of the provenance record — the sha lives
in the record and nowhere else, because a digest with two homes goes green while one of them drifts
[[a_moved_constant_fails_green]].

Driving the validator on a team-lead file is licensed and not assumed: the green-path test asserts
at the SOURCE level that the gate contains no `write_text` and no `write_bytes`, so running it
cannot write to what it reads. Nothing in this contract opened the labels file for writing.

**The seal has teeth** — the negative control, run on a scratch copy so nothing real was touched:
one label flipped (`null` → `молочный_бренд`), row count still 500, and the validator would still
exit 0. Caught three ways:

```
rows still 500          : True
sha pin catches it      : True
distribution catches it : True {'null': 166, 'молочный_бренд': 3, …}
byte-identity catches it: True
```

### `make check`, green from the sealing commit

```
$ make check                                   # at 8d2e1ba, nothing else in flight
2960 passed, 2 skipped in 499.54s (0:08:19)
```

2 959 registered + 1: the freeze/provenance test is the only test added, and the two that were red
are back among the passed.

## D2 — the census axis (Dv526), commit `d444be5`

```
$ python3.11 scripts/context-census.py          # BEFORE the fix
brain-census: 13.2Ktok boot tax  ⚠️ > 9.0K target — de-bloat: rules with paths: / shrink the MEMORY index / curate hot.md

$ python3.11 scripts/context-census.py          # AFTER the fix
brain-census: 13.2Ktok boot tax  ⚠️ > 9.0K target — de-bloat: rules with paths: / shrink the MEMORY index / curate hot.md
```

Unchanged to the printed digit, and the underlying move is **−1 B**:

| | MEMORY.md's share | census total |
|---|---:|---:|
| old axis — `min(st_size, 25 * 1024)` UTF-8 bytes | 18 587 | 52 628 B = 13.1570K |
| loader axis — trim → 200 lines → 25 000 UTF-16 units | 18 586 | 52 627 B = 13.1568K |

The delta was **predicted before the run** and is the trailing newline the loader's `trim()` takes:
today's file is under both caps, so no truncation branch fires and only the trim can move anything.
An ≈0 that was forecast is evidence the model is right; an ≈0 discovered afterwards would only have
been evidence that nothing happened.

`loaded_memory()` returns the loaded text's BYTE length. That direction matters: the census sums
UTF-8 bytes, so handing it back a UTF-16 unit count would be Dv526 again, pointing the other way.
`TARGET_KTOK = 9.0` and the warning text are untouched, and the test pins them — a suspended number
with nothing watching it is the one that drifts.

`tests/test_context_census.py`, 6 tests, drives the function rather than the constants:

```
$ python3.11 -m pytest tests/test_context_census.py -q
6 passed in 0.05s
```

* both constants pinned at 200 / 25 000, `TARGET_KTOK` at 9.0, and `MEMORY_CAP` asserted GONE;
* under both caps → only the trim moves;
* over the line cap → cut at 200 lines exactly;
* over the unit cap on **Cyrillic** (1 unit, 2 bytes per character) → cut back to a newline, the
  kept-line count derived from the cap arithmetic rather than hardcoded, and the result asserted
  **larger than 25 000** — which is what fails if the function ever returns units;
* a first line longer than the cap → the loader's mid-line branch;
* a missing file → 0, because a fresh clone has no MEMORY.md and a census that raises there
  measures nothing at all.

## D3 — the record and the audit prep

### The two ADRs

| record | ruling |
|---|---|
| `knowledge/decisions/the-absence-test-is-a-clock-and-flips-with-its-artifact.md` | ruling 1 — an absence assertion is a clock; the flip belongs in the commit that lands the artifact |
| `knowledge/decisions/boot-tax-target-suspended-and-the-census-axis.md` | ruling 2 — ≤9K suspended, the reachability inequality quoted with its numbers, the axis moved |

Both are in `knowledge/decisions/INDEX.md`; `check-wikilinks` is clean including their `[[…]]`.

### The audit prep — `knowledge/hot.md` block by block

**Classification only. No row of this table recommends an eviction** — what leaves live state is the
joint sitting's decision. `hot` = live state (a blocker, a Next item, a sealed input, a rule about
this file). `cold-candidate` = the block has a durable home elsewhere, named in the row; whether
that makes it evictable is exactly what the sitting decides.

Bytes are of the block including its blank separator line, and they sum to the file: **24 807 B**.

| bytes | block | class | durable home if the sitting moves it |
|---:|---|---|---|
| 1 353 | AUTO-GEN region (commits · decisions · daily logs) | generated | `scripts/refresh-hot-cache.py` rebuilds it every SessionStart from git — the only block nobody edits |
| 25 | `# Hot Cache — curated` | structure | — |
| 1 070 | `**Last update:**` + the three-contract day summary | mixed | attribution is hot; the day summary's home is `knowledge/daily_logs/2026-08-18.md` + the three reports it names |
| 237 | «Этот блок курируется руками» | hot | the file's own curation law |
| 20 | `## 🔥 What's Hot` | structure | — |
| 596 | 🔄 ТЫ ЗДЕСЬ | hot | where the project is and what moves next |
| 1 174 | 🏷️ ПАК РАЗМЕТКИ ГОТОВ — ЧИТАТЬ И РАЗМЕЧАТЬ | cold-candidate | the work it commissions is DONE as of `8d2e1ba`; `docs/reports/pass1-data-prep.md` + `results/labels_pass1_r1_provenance.json` |
| 1 164 | 🎲 ПАК ДЕТЕРМИНИРОВАН | cold-candidate | `results/pass1_label_pack_r1.json` `draw` block (seed · cap · formula · reachability) + the report |
| 1 150 | 🚫 ЭКЗАМЕН ВЫНЕСЕН | cold-candidate | the pack record's `exclusion` block with its four empty lists + [[the_codebook_quoted_the_answer_key]] |
| 777 | 🎯 ЧТО ПРОВАЛИЛОСЬ У ПРОХОДА-1 | cold-candidate | `knowledge/decisions/sitting-b-line-b-and-the-team-lead-labels.md` + `docs/reports/pass1-probe-b.md` |
| 274 | 💵 ЦЕНА ПРОХОДА-1 (the $1.0950 floor) | hot | an input the next money registration reads before it is spent |
| 542 | 💰 ДЕНЬГИ СЕЙЧАС | cold-candidate | `scripts/runpod_guard.py`'s ledger — and this file's own law says money is read FROM the guard; the prose copy already disagrees with STATUS ($1.8146 vs $1.8243) |
| 918 | 🧰 ГАРД УМЕЕТ КОНЕЦ ОКНА | cold-candidate | `knowledge/decisions/guard-until-the-tolerance-that-was-a-window-bug.md` + `docs/reports/guard-until.md` |
| 718 | 🔎 ПРЕФЛАЙТ — ИНСТРУМЕНТ | cold-candidate | `scripts/preflight.py`'s own docstring is the long form; the card's «1 466 путей» reads 1 472 live |
| 740 | 🧬 ИДИОМЫ, КОТОРЫЕ ДЕРЖАТ | cold-candidate | one memory lesson per idiom, all of them written |
| 873 | ⚙️ ТРАНСПОРТ ПРОХОДА-1 | cold-candidate | `results/prereg_pass1_probe_b.json` + `docs/reports/pass1-probe-b.md` |
| 347 | 💥 ОДИН ФЛАГ — ДВЕ КОМАНДЫ | cold-candidate | [[one-flag-two-branches]] + both branches in the suite |
| 465 | 🧾 РЕГИСТРАЦИЯ — ВХОД ДЛЯ ЧУЖОГО КОДА | cold-candidate | [[a-frozen-record-is-an-input-to-shipped-code]] |
| 317 | ⚙️ Карта RTX 4090 и цены 16.08 | cold-candidate | its own rule says read the price on the DAY from `create`; the law is Dv448 |
| 516 | 📊 Ячейка ценза читателя | hot | 129 / 1 032 / 122 / 968 are inputs the next contracts quote; the record is `results/gate_census_w1_reader.json` |
| 16 | `## ⏭️ Next` | structure | — |
| 1 611 | Next 1–4 | hot | item 1 (разметка) and item 2's provenance freeze completed in this contract; items 2–4 are live |
| 670 | Кандидаты цикла-2 | hot | the live purchase queue |
| 706 | Долги-входы следующих регистраций | hot | registered debts, each naming its own record |
| 18 | `## 🚧 Blockers` | structure | — |
| 575 | ⛔ `pass1-probe` обход завис | hot | open, owner named, needs a ruling |
| 628 | ⛔ `pass1-probe-b` правая часть закрытия | hot | open, needs a ruling |
| 714 | ⛔ 19 отказанных леджеров | hot | open, shape of the next money contract |
| 413 | ⛔ ПРОХОД-1 НЕ БЕРЁТ БАР | hot | open until the LoRA registration measures it |
| 613 | ⛔ БУТ НЕ КОНСТАНТА | hot | open, binds every future deadline |
| 373 | ⛔ ЗАПАС НА ПРОВИЖЕН | hot | open, binds every future deadline |
| 586 | ✅ СУИТА СНОВА ЗЕЛЁНАЯ | **closed by this contract** (edit 1) | the ADR above; kept as one short closed line naming `8d2e1ba` |
| 1 265 | ⛔ BOOT TAX — цель приостановлена | **rewritten by this contract** (edit 2) | the ruling + the pending sitting; Dv521 still has no home |
| 40 | `## 🔫 Footguns этого файла` | structure | — |
| 386 | ⛔ `hot.md` грепается как ЦЕНОВОЙ ВХОД | **hot and SEALED** | `tests/test_volume_calc_5c1.py` — nine tests die if it moves |
| 988 | «Recorded rather than open» + `~$0.24/day` | **hot and SEALED** | carries the literal `scripts/volume_calc_5c1.py` greps out of this file |
| 698 | ⛔ Суита не идёт в голом worktree | cold-candidate | [[a-commit-must-run-its-own-suite]] + Dv492 |
| 584 | 🔫 ПРОДЮСЕР — НЕ ВЕРИФИКАТОР | cold-candidate | [[the-producer-is-not-the-verifier]] |
| 647 | Деньги — три числа | cold-candidate | the guard's docstring + the money lessons in memory |

**Totals**, summing to the file: hot **7 926 B** (32.0%) · the two blocker blocks this contract
rewrote **1 851 B** (7.5%) · sealed **1 374 B** (5.5%) · **cold-candidate 11 114 B (44.8%)** ·
generated **1 353 B** (5.5%) · the mixed `Last update` header **1 070 B** (4.3%) · structure
**119 B** (0.5%). Computed from the file by the same split that produced the rows, not added up by
hand.

Two things the table found and did not touch, because this contract may make exactly two edits
here: **Next §4 quotes this file's own size** («24 583 Б `hot.md`», «~8.1K Б (−67%)») and both
figures were stale before I arrived (live 24 718, now 24 807); and two prose numbers have drifted
from their producers (the cycle-2 spend against STATUS, the pin count against preflight). Named,
not fixed.

### The three `CLAUDE.md` — the same one-line treatment

Re-measured today: **./ 6 999 B · ~/.claude/ 1 974 B · ~/ 350 B = 9 323 B**, the contract's figures
reproduce exactly.

| bytes | section | class | candidate home if the sitting moves it |
|---:|---|---|---|
| 117 + 225 | `# CLAUDE.md` + `# market-pulse-llm` | hot | what the project is — the first thing a session needs |
| 531 | `## Where the truth lives` | hot | routes every task to SPEC/STATUS/decisions |
| 726 | `## File ownership` | hot | enforced by `permissions.deny`; a session that learns it late has already written |
| 650 | `## Rules` | hot | the standing law (Russian chat, Telegram only, frozen sets, small diffs) |
| 387 | `## Pitfalls` | mixed | FloodWait/comments/sarcasm are collector-and-annotation scoped — `paths:`-scoped rule candidates |
| 705 | `## Second brain` | hot | tells the session where volatile vs durable state lives |
| 742 | `## Stack & commands` | hot | `make check` is quoted by every contract's Verify block |
| 1 239 | `## Code map` | cold-candidate | the largest section, and it describes `src/` + `tests/` — a `paths:`-scoped rule reaches it exactly when a session opens those |
| 445 | `## Harness plumbing` | cold-candidate | hooks and `/save` — `.claude/`-scoped |
| 460 | `## Tooling` | mixed | its own last line already points at `knowledge/runbooks/tooling.md` for the full inventory |
| 772 | `## graphify` | cold-candidate | duplicated in spirit at `~/.claude/CLAUDE.md`'s own graphify section (273 B); a tool section, on-demand by nature |
| 1 402 | `~/.claude/CLAUDE.md` `## Karpathy coding principles` | hot (user-level) | the operator's standing working law, not this repo's to move |
| 299 + 273 | `~/.claude/CLAUDE.md` preamble + graphify | mixed | the `/graphify` trigger is hot; the rest overlaps this repo's own section |
| 326 | `~/CLAUDE.md` `## Dev Stack` | cold-candidate | Bun/Foundry/GSD/Antigravity — no line of it applies to this Python repo, and it loads in every session of it |

**The mechanism the sitting can spend is already proven here:** `.claude/rules/*.md` holds
**22 629 B** on disk (`phase345-artifacts.md` 18 753 · `registrations-and-draws.md` 3 587 ·
`_TEMPLATE.md` 289) and contributes **0** to the census, because all three carry `paths:`
frontmatter and load only when a session touches the paths they scope.

### `knowledge/hot.md` — the two edits, and nothing else

```
hot.md: 24 718 -> 24 807 B  (+89)
AUTO-GEN markers: 2        ~$0.24/day literal: unmoved (count identical before and after)
the whole region above AUTO-GEN END: byte-identical
```

1. the red-suite blocker becomes **✅ СУИТА СНОВА ЗЕЛЁНАЯ: 2 960 / 2 skipped**, naming `8d2e1ba` and
   the ADR — 639 B → 586 B;
2. the boot-tax blocker's open half becomes the ruling: target suspended, `hot.md` not cut for a
   number, census axis moved (−1 B), the joint sitting starting from this report's table — 1 123 B
   → 1 265 B. `Dv521` still has no home and says so.

The `**Last update:**` line was NOT touched: it is a third edit, and the contract authorises two.

## Verify

```
$ make check                          # at 8d2e1ba, the sealing commit
2960 passed, 2 skipped in 499.54s (0:08:19)

$ make check                          # at the end, after D2 and D3
2966 passed, 2 skipped in 499.29s (0:08:19)

$ PYTHONPATH=src python3.11 scripts/validate_pass1_labels.py docs/labels-pass1-r1.jsonl
OK — 500 rows, every one of 500 drawn units answered once
  не_наш_рынок       251    50.2%
  null               167    33.4%
  сеть_ритейлер       44     8.8%
  категория_личное    36     7.2%
  молочный_бренд       2     0.4%
exit=0

$ shasum -a 256 docs/labels-pass1-r1.jsonl results/labels_pass1_r1.jsonl
776b204f3d3aa1a193f0faad7f68198595c81963199124efca8f6b74a9e1c920  docs/labels-pass1-r1.jsonl
776b204f3d3aa1a193f0faad7f68198595c81963199124efca8f6b74a9e1c920  results/labels_pass1_r1.jsonl

$ python3.11 scripts/context-census.py     # before D2 / after D2 / after the hot.md edits
brain-census: 13.2Ktok boot tax  ⚠️ > 9.0K target — …   (52 628 B)
brain-census: 13.2Ktok boot tax  ⚠️ > 9.0K target — …   (52 627 B)
brain-census: 13.2Ktok boot tax  ⚠️ > 9.0K target — …   (52 716 B, +89 from hot.md's two edits)

$ python3.11 scripts/check-wikilinks.py
check-wikilinks: OK, none broken

$ git status --porcelain              # after the D3 commit, before this report's own
?? docs/reports/labels-boot-audit.md
```

**The final count is 2 959 + 7**: one freeze/provenance test in the sealing commit and six census
guards in D2. Nothing was removed, and the two that were failing are among the passed. The porcelain
above is the state at the D3 commit `05dbae3`; the only path in it is this file, which its own commit
takes. The SessionStart and Stop hooks move `knowledge/index.md` and the daily log by design, so
whatever they write after this line is the next contract's step 0 and not a leftover of this one.

### `make preflight ARGS='labels-pass1-r1'` — the pin is there, and this command cannot show it

```
pin registry: 1472 paths pinned by results/*.json          # was 1 469 before the sidecar

[3] pins — 4 of the 23 touched paths are pinned by a record
    scripts/build_pass1_label_pack.py  <- results/pass1_label_pack_r1.json.producer.sha256 408bce3725ab…
    docs/label-pack-pass1-r1-blind40.md  <- results/pass1_label_pack_r1.json.blind.sha256 d2364ff3e30b…
    docs/label-pack-pass1-r1.md  <- 2 pin(s): results/labels_pass1_r1_provenance.json.codebook.sha256 5aec9…, results/pass1_label_pack_r1.json.rendering.sha256 5aec9…
    results/pass1_label_pack_r1.json  <- results/labels_pass1_r1_provenance.json.pack.sha256 e5ca328e5d99…

[4] digests — 4 of 4 pinned paths match every digest on them
```

The sidecar IS parsed — two of the four rows are its pins — and the DO NOT's «keep preflight 3/3
matching» holds at 4 of 4. What the command cannot print is the labels file itself, because
preflight joins pins onto the query's grep HITS and `docs/labels-pass1-r1.jsonl` is the one file
that never contains the string `labels-pass1-r1`:

```
$ git grep -c -I -F --untracked -e "labels-pass1-r1" -- docs/labels-pass1-r1.jsonl
(no output, exit 1)
```

Asked by path, the same instrument answers the question the contract wanted answered (Dv532):

```
$ make preflight ARGS='docs/labels-pass1-r1.jsonl'
[3] pins — 5 of the 23 touched paths are pinned by a record
    docs/labels-pass1-r1.jsonl  <- 1 pin(s): results/labels_pass1_r1_provenance.json.labels.sha256 776b204f3d3a…
    …
[4] digests — 5 of 5 pinned paths match every digest on them
```

## Deviations from Dv532

| # | what | tag |
|---|---|---|
| **Dv532** | **The Verify block's own preflight command cannot display what it promises, and the pin is fine.** `make preflight ARGS='labels-pass1-r1'` shows 4 of 4 digests matching and NOT the labels file, because block 3 joins the pin registry onto the query's grep hits and the subject of a query is the one file that never names itself — `git grep -F labels-pass1-r1` on the jsonl exits 1. Shaping the sidecar differently cannot fix it: it is the join, not the record. Both runs ship, the by-path one showing `docs/labels-pass1-r1.jsonl <- …labels.sha256 776b204f3d3a…`, 5 of 5 matching. `scripts/preflight.py` NOT touched — a pinned instrument is not adjusted to make a report read better [[the_subject_of_a_query_never_names_itself]]. | `[cause: verify-gap]` |
| **Dv533** | **The renamed test's MODULE DOCSTRING asserted the same expired fact, one level up.** The contract names the test to rename; `tests/test_validate_pass1_labels.py`'s docstring said «every fixture lives in `tmp_path` and the last test asserts the real path is still absent». Flipping the assertion and leaving the prose would have reproduced exactly the defect the rename exists to remove — a file describing itself as the opposite of what it does. Rewritten in the same commit, and it now names what licenses reading a team-lead file: the source-level proof that the gate holds no `write_text`/`write_bytes` [[the_docstring_is_a_consumer_of_the_test]]. | `[cause: contract-gap]` |
| **Dv534** | **A boot-tax contract grew `knowledge/hot.md` by 89 B, and both writes were mandatory.** Edit 1 shrank the file 53 B by closing the red-suite blocker; edit 2 grew it 142 B, because a suspension has to carry more than an open question did — the ruling, the axis, the owner, the pointer to the sitting's table. Measured after the last edit and re-run through the census rather than asserted: 24 718 → 24 807 B, census 52 627 → 52 716 B, still 13.2K printed. Same shape as Dv530, and it is the arithmetic of a contract whose D3 is a WRITE into the file its D2 measures [[a_probe_must_not_create_what_it_measures]]. | `[cause: process]` |
| **Dv535** | **`hot.md` quotes its own size, and the quote was already stale before this contract opened it.** Next §4 says «24 583 Б `hot.md`» and «~8.1K Б (−67%)»; the file read 24 718 B on arrival and 24 807 B on exit, so the derived −67% is wrong in the third digit and cannot be right for long — any edit to the file invalidates it. Not fixed: the contract authorises exactly two edits and this is neither. Named in the audit table so the sitting starts from a live measurement instead of the file's own memory of itself [[a_file_that_quotes_its_own_size]]. | `[cause: contract-gap]` |
| **Dv536** | **Two live numbers in `hot.md` have drifted from their producers, and the audit is how they surfaced.** The money card reads «цикл-2 $1.8146» where `docs/STATUS.md` reads $1.8243 (both are prose copies of a reading whose home is the guard's ledger — and this file's own law says money is read FROM the guard); the preflight card reads «1 466 путей» where the live registry printed 1 469 before this contract and 1 472 after it. Neither is fixable inside the two-edit budget, and one of them lives in a team-lead file. Classified, not corrected [[trace_the_producer_not_the_result]]. | `[cause: process]` |

## Process signals

1. **The atomic commit was the cheap part; proving the seal replaced the clock was not.** Deleting
   `assert not …exists()` takes one line and leaves the suite green and weaker. What cost the work
   was building the thing that stands in its place — 500 rows, the distribution, a digest that
   lives in exactly one file, the validator driven on the real input — and then attacking it with a
   single flipped label to see whether all three legs actually fire. They did; a row-count check
   alone would not have.
2. **A pin can be correct and invisible at the same time.** The sidecar parses, the registry grew by
   three paths, 4 of 4 and then 5 of 5 digests match — and the command the contract wrote down
   shows none of it, because a grep-hit join cannot see the file that is the SUBJECT of the query.
   The instrument was not adjusted to make the report look right; the gap was measured, named, and
   answered with a second command.
3. **An ≈0 that is predicted is a measurement; an ≈0 that is discovered is nothing.** D2's whole
   risk was that a rewrite of the MEMORY.md axis would move the census by a byte and read as «no
   change, no effect». Deriving −1 B from the loader's semantics BEFORE running it turned the
   non-event into the evidence that the model is right — the file is under both caps, so only
   `trim()` can move anything, and only the trailing newline is there to take.
4. **The audit's own instrument found two numbers nobody was watching.** Splitting `hot.md` into
   blocks to price them surfaced a money figure that disagrees with STATUS and a pin count three
   short of live, neither of which any test or gate reads. That is the argument for the sitting
   working off a table: the classification is cheap and the drift it exposes is the expensive kind
   — prose copies of numbers that have producers.
5. **Two edits was the right budget, and it cost something visible.** `**Last update:**` still says
   `/save`, Next §4 still quotes a size the file no longer has. Both were left alone because the
   contract said two, and both are in the report instead. A file that may only be touched twice
   ships its staleness into the record — which is better than a contract that quietly renegotiates
   its own limit.
