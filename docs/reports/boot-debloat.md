# boot-debloat — everything evicted has a home somebody opened, and the target is the measurement times 1.1

**Contract:** `docs/PROMPT-boot-debloat.md` ($0, no cloud call). **Deviations from Dv537.**
Cause tags from the closed enum v2 only; lesson names ride as trailing `[[wiki-name]]`.

## Read back, before the first edit

1. **No home, no eviction — and a home is READ, not grepped** (`vault-dream` Dv529): for every block
   I open the passage in the home the audit table names and confirm it states the block's CONTENT,
   not its name; a block whose home fails that reading STAYS, and this report says which and why.
   The mapping table carries `file:line`, because a row without a line number is a row I grepped.
2. **ONE pointer line total** replaces all of it — «вытеснено 19.08 → mapping-таблица в
   `docs/reports/boot-debloat.md`» — never one per block; the mapping lives here.
3. **Untouchable in `hot.md`, byte-intact:** the seven blockers · ТЫ ЗДЕСЬ · ЦЕНА ПРОХОДА-1 ·
   Ячейка ценза · both sealed literal blocks (`~$0.24/day` and «80 GB is about what the», which
   `scripts/volume_calc_5c1.py` greps out of this file) · the AUTO-GEN region · Next/долги · the
   Footguns headers.
4. **D4 is LAST and its number comes from the measurement:** three census runs on the same
   invocation are the floor, `TARGET_KTOK := floor × 1.1` to one decimal, and it lands in **two**
   files in the SAME commit — the constant plus docstring in `scripts/context-census.py` and the pin
   `== 9.0` in `tests/test_context_census.py`.
5. **Parking rule for `~/CLAUDE.md`:** `## Dev Stack` is cut and parked VERBATIM at
   `~/dev-stack-parked.md`, a file nothing loads (proved by grep, no `@import` anywhere points at
   it); everything else in `~/CLAUDE.md` stays byte-for-byte; the file is outside the repo, so it is
   snapshotted (path + sha) before the first edit and the after-state stands beside it.

## Step 0 — the tail

```
$ git status --porcelain
 M docs/STATUS.md
 M knowledge/daily_logs/2026-08-19.md
 M knowledge/hot.md
 M knowledge/index.md
?? docs/PROMPT-boot-debloat.md
```

Five paths and both lists explain all five, so there is nothing to stop for.

| commit | what |
|---|---|
| `ec14ff1` | `knowledge/daily_logs/2026-08-19.md`, `knowledge/index.md`, `knowledge/hot.md` — the previous session's `/save` curation, inherited |
| `6dcfa53` | `docs/STATUS.md` + `docs/PROMPT-boot-debloat.md`, verbatim, never edited |

Baseline before any edit: `make check` **2 966 passed / 2 skipped**; census **13.2K**;
`./CLAUDE.md` 6 999 B · `~/.claude/CLAUDE.md` 1 974 B · `~/CLAUDE.md` 350 B; `knowledge/hot.md`
24 662 B; `.claude/rules/` three files, all with `paths:`, 0 in the census. Every contract figure
reproduces.

## Step 0.5 — the two debts of the accepted `labels-boot-audit`, and both are red first

**(a) The sidecar's blocks must NAME their four files.** The freeze test re-derived four digests but
only asserted two of the four `file` paths, so a record pointing its `codebook` block somewhere else
passed with every digest matching. Proved on a scratch record whose `codebook` block was replaced by
the `frozen` one:

```
swapped codebook block: digest still matches = True | the new path assert catches it = True
```

`FILES` now names all four and the loop asserts the path before it hashes it.

**(b) `str.strip()` is not `String.trim()`.** The loader trims with JS `String.trim()` — WhiteSpace
plus LineTerminator. Python's set is a different one: it also takes **U+001C–U+001F** and **U+0085**,
which JS keeps, and it leaves **U+FEFF**, which JS takes. `JS_TRIM` is that set, and the guard uses
two fixtures because one cannot see a difference that points both ways — the BOM proves something is
stripped, the NEL-and-US edges prove it is not a strip of everything Python calls whitespace
([[guard_selftest_negative_control]]). Both are RED against the old code:

```
BOM   : old = 24 expected 21 -> RED
NEL/US: old = 21 expected 24 -> RED
```

**Predicted before the run: census delta 0 B.** Today's `MEMORY.md` starts with `#` and ends with
`\n`, so both trims take exactly the same one byte — checked on the file's edge code points
(`0x23 0x20 0x4d 0x65` … `0x6e 0x63 0x65 0x0a`) before the fix was applied. Measured: **13.2K →
13.2K**. A predicted ≈0 is a measurement; a discovered ≈0 is nothing.

Commit `a26db9f`. `make check` **2 967 / 2 skipped** (2 966 + the new census guard; (a) landed
inside an existing test).

## D1 — `hot.md`: groups A + B + C leave, every home opened first

**Fourteen of fifteen blocks evicted. One STAYED**, and it is the point of the discipline.

### The mapping table — block → the home that was READ

| B | block | home, `file:line` | what the passage actually states |
|---:|---|---|---|
| 1 033 | 🏷️ МЕТКИ ЗАПЛОМБИРОВАНЫ | `docs/reports/labels-boot-audit.md:76–151` · `results/labels_pass1_r1_provenance.json` | the sha by three readings, the distribution, the freeze byte-identical, the sidecar as PIN, the flipped-label negative control |
| 1 163 | 🎲 ПАК ДЕТЕРМИНИРОВАН | `results/pass1_label_pack_r1.json` `draw` · `docs/reports/pass1-data-prep.md:109, 124, 210, 304` | `cap_rule` = p90 re-derived every run · `formula` = `min(payable,CAP)` + largest remainder on a total key · largest thread 125 → 12 against 65 uncapped · «`SEED = 20260818` is a module constant and not a flag» · the CAP=9 ceiling **483 < 500** · the self-pinning producer |
| 1 149 | 🚫 ЭКЗАМЕН ВЫНЕСЕН | `results/pass1_label_pack_r1.json` `exclusion` + `population.arithmetic` + `rendering.codebook` · `<memory>/the_codebook_quoted_the_answer_key.md:9–16` | the 7 threads · `the_units_are_the_payable_set: true` · «1032 − 64 = 968 → min(500, 968) = 500» · the four empty lists and why the gold check is against the RENDERED text · the law quoted by the same bytes, and the r2 redaction with what it cut |
| 776 | 🎯 ЧТО ПРОВАЛИЛОСЬ | `knowledge/decisions/sitting-b-line-b-and-the-team-lead-labels.md:25–28, 36` · `docs/reports/pass1-probe-b.md:399, 539` | «all five are `subject_type`» · «`stance` is right on all three rows that score it» · «an **abstention**, not a parse failure» · «25 of 50 census rows … zero refusals» · «the symmetric collapse a no-op» |
| 917 | 🧰 ГАРД УМЕЕТ КОНЕЦ ОКНА | `knowledge/decisions/guard-until-the-tolerance-that-was-a-window-bug.md:35, 37–38, 42–46` · `docs/reports/guard-until.md:18, 258, 550, 552, 564` | `--tolerance` REQUIRED with no default · the three-state walk at `MS_BAND` 1% · «`--until` bounds **both** callers» and «does NOT bound the balance delta, which has no window» · Dv506 bucket-size changes no total · Dv517 the delta is negative on an old ledger |
| **739** | **🧬 ИДИОМЫ** | — | **STAYS. See below.** |
| 872 | ⚙️ ТРАНСПОРТ ПРОХОДА-1 | `docs/reports/pass1-probe-b.md:5, 147, 286, 502` · `src/market_pulse/prompts.py:694, 925, 1104` | the prompt sha `5a4a3cb6…` on the may-not-move list · the record sha `a29e85ad…` · «64 units = 14 gold + 50 census» · Dv494 the empty `scored_fields` and the real rule in the gold rows, not repaired because it is object-equal to the frozen record · the FOUR readings, and the law carried by reference |
| 346 | 💥 ОДИН ФЛАГ — ДВЕ КОМАНДЫ | `<memory>/one_flag_two_branches.md:13–20, 27` | the dispatch spelled out (`if args.gate and not rows: deadlines(…) else: projection(…)`), what each branch reads, and «put every drive in the suite» |
| 464 | 🧾 РЕГИСТРАЦИЯ — ВХОД | `<memory>/a_frozen_record_is_an_input_to_shipped_code.md:11–19, 26–28` | `boot_kill_rule` against `boot_deadline_rule`, the `KeyError` on `--deadlines` with a pod billing, the record frozen by its own clause, and the $0 duty that prevents it |
| 697 | ⛔ Суита не идёт в голом worktree | `<memory>/a_commit_must_run_its_own_suite.md:39–47, 68–75` · `docs/reports/pass1-probe-b.md:500` · `knowledge/daily_logs/2026-08-18.md:156–158` | `data/` is PARTLY tracked so the naive fix misses · collection aborts before a single test runs · the working method is the primary tree at that HEAD on an empty porcelain, pins proved via `git show` · «`[ -e ] || cp -R` промахивается мимо частично отслеживаемых каталогов» |
| 583 | 🔫 ПРОДЮСЕР — НЕ ВЕРИФИКАТОР | `<memory>/the_producer_is_not_the_verifier.md:11–19, 26–30` | the `quoted(HOT, "~$0.24/day", 0.24)` grep, `main()` rewriting `results/volume_calc_5c1.json` and deleting the operator's `executed` block, and «call the READER … never `main()`» |
| 541 | 💰 ДЕНЬГИ СЕЙЧАС | `results/spend_cycle2.json` · `results/spend_phase4.json` | cap 20.0 · anchor **22.5097614388** at `2026-08-16T12:14:48+00:00` · `sessions[-1]` spent **1.8146** / remaining **18.1854** with every close's note · phase 4 cap 33.0, `billing_since_usd` **32.470794**, «PHASE 4 IS CLOSED at this final reading» |
| 647 | Деньги — три числа | `scripts/runpod_guard.py:6–7, 11–16, 27–29, 565` · `docs/reports/guard-until.md:564` · `docs/reports/5c2-prep-c3b.md:209` | «two readings … the pessimistic one wins» · the kinds kept APART, never summed on the way in · a closed step priced by its settled figure, never by a delta that goes on growing · `remaining_usd = cap − spent` derived · the stored remainder читается «under the $30.00 cap it was written beside» |
| 717 | 🔎 ПРЕФЛАЙТ | `scripts/preflight.py:1–34, 130, 133` · `docs/reports/guard-until.md:172, 553, 557` | the four blocks in order · the registry joined against the query's OWN hits · the **three** pin shapes named one by one (`{"sha256","module"}` · `borrowed` with the path as KEY · `frozen_when_the_pod_exists`) · Dv513, the guard already stale against its own pin |
| 316 | ⚙️ Карта RTX 4090 / цены | `docs/reports/reader-v4.md:101–108, 385` · `docs/reports/probe-a.md:451` | the card as a table with availability (4500 Blackwell 0.72 High, 4000 Blackwell 0.57 Medium) · Dv448, «the 4090 in EU-RO-1 reads $0.74/h today, so every figure is recomputed» · L4 at $0.49 |
| 1 216 | C — the day summary inside `**Last update:**` | `knowledge/daily_logs/2026-08-18.md:12, 15, 19–20, 340, 348` · `docs/STATUS.md` «День 19.08» | «ПРОВАЛИЛ бар P1 (9 из 14 при пороге 12)» · «постановил полосу 7% и три сходящихся леджера ЗАКРЫТЫ» · «`make check` 2 879 → 2 911 → 2 927 → 2 959 / 2 skipped» · «MEMORY.md 197 → 147 строк» · «Boot tax 14.5K → 13.1K» |

**11 437 B left, 232 B came back** (the rewritten attribution line and the one pointer sentence):
`hot.md` **24 662 → 13 457 B (−11 205)**.

### The one block that stayed, and why

**🧬 ИДИОМЫ (739 B) is still in the file.** Its home in the audit table reads «one memory lesson per
idiom, all of them written» — a **roster claim**, which is exactly the shape Dv529 refuses. Read
idiom by idiom, five of the six hold: the APPEND rule is a whole section at
`docs/reports/reader-v5-prep.md:347` with its test named at `:526`; the paired `--outdir` run is
`docs/reports/pass1-data-prep.md:272–273`; the self-pinning producer, the two-way enumerated diff and
the one-attempt/stop-rule idiom all resolve. The sixth — **«право исполнителя на отказ»** — is stated
in **no file**: `grep` over `knowledge/decisions/`, `docs/reports/`, `knowledge/runbooks/`, `CLAUDE.md`
and the whole memory directory returns one hit, and it is `MEMORY.md`'s own index line for
`a_refusal_is_an_outcome_with_a_price`, whose subject is a **billed boot on a retry's budget** — a
different claim. `guard-until`'s ADR:17 says «the contract's step-1 refusal gate», which is a
contract's own gate, not the executor's standing right.

No home, no eviction. The block stays whole; splitting it to evict five sixths would be a rewrite,
and the contract forbids one. `[[a-citation-is-not-a-record]]`

### The untouchables, proved rather than asserted

The edit script compares **21 anchors** block-for-block between the before and after text and refuses
on any difference:

```
hot.md: 24,662 -> 13,457 B (-11,205)
blocks evicted: 14 · untouchables proved byte-identical: 21
```

They are: both AUTO-GEN markers and the whole region above `AUTO-GEN END` · ТЫ ЗДЕСЬ · ЦЕНА
ПРОХОДА-1 · Ячейка ценза · ИДИОМЫ · `## ⏭️ Next` with all four sub-blocks · `## 🚧 Blockers` and each
of the **seven** blockers · `## 🔫 Footguns этого файла` with both sealed literal blocks. Plus:
`~$0.24/day` and «80 GB is about what the» appear the same number of times before and after, exactly
two AUTO-GEN markers survive, and no double blank line was left behind by a deletion.

```
$ python3.11 -m pytest tests/test_volume_calc_5c1.py -q      # immediately after the edit
10 passed in 0.08s
$ scripts/stale-check.sh
                                                              # silent: the ISO date still parses
```

Two prose numbers the previous contract handed over as drifted (Dv536) — the cycle-2 spend against
STATUS, and «1 466 путей» against a live 1 472 — are resolved **by** the eviction: both lived in
group-B blocks that are now gone, and the producers they disagreed with are the homes.

Commit `cf00a44`. Census **13.2K → 10.4K**. `make check` **2 967 / 2 skipped**.

## D2 — `./CLAUDE.md` sections into `paths:`-scoped rules

Every body is lifted out and asserted present in its destination **by substring**, so the diff is a
move and not a rewrite:

```
## Code map            -> .claude/rules/code-map.md              verbatim: True
## Harness plumbing    -> .claude/rules/harness-plumbing.md      verbatim: True
## graphify            -> knowledge/runbooks/tooling.md          verbatim: True
pitfall verbatim in telegram-collection.md: True   (FloodWait / member harvesting)
pitfall verbatim in telegram-collection.md: True   (comments enabled)
```

| destination | `paths:` | bytes |
|---|---|---:|
| `.claude/rules/code-map.md` | `src/**/*.py`, `tests/**/*.py` | 1 486 |
| `.claude/rules/harness-plumbing.md` | `.claude/**`, `scripts/brain-*`, the four hook scripts by name | 842 |
| `.claude/rules/telegram-collection.md` | the twelve collector paths (`scripts/collect_*`, `fetch_*`, `harvest_*`, `late_batch_*`, `backfill.py`, `discover_channels.py`, `entry_check.py`, `poll_census.py`, `tg_login.py`, `src/market_pulse/{telegram_client,backfill,entry_check}.py`) | 773 |
| `knowledge/runbooks/tooling.md` | not a rule — the runbook `CLAUDE.md ## Tooling` already points at | 4 800 |

**Reachability, and the limit on proving it.** Every pattern is matched against the working tree in
the same glob flavour `_TEMPLATE.md` uses (`"src/**/*.py"`), and **no pattern is dead**:

```
code-map.md                   2 patterns ->  191 files matched; dead: none
   e.g. ['src/market_pulse/__init__.py', 'src/market_pulse/aggregates.py', …]
harness-plumbing.md           6 patterns ->   17 files matched; dead: none
telegram-collection.md       12 patterns ->   15 files matched; dead: none
   e.g. ['scripts/collect_5c1.py']
phase345-artifacts.md        25 patterns -> 1434 files matched; dead: none
registrations-and-draws.md    5 patterns ->   20 files matched; dead: none
```

What this does **not** prove is the injection itself: a path-scoped rule loads once per session, so
I cannot watch a rule I wrote this session fire in this session
([[you_cannot_watch_your_own_new_rule_fire]]). The claim here is the glob match plus the census
check below, and it is stated as that.

Every rule carries `paths:` inside the 300 bytes the census reads, which is why the directory still
costs nothing:

```
.claude/rules/_TEMPLATE.md                    paths: in head = True
.claude/rules/code-map.md                     paths: in head = True
.claude/rules/harness-plumbing.md             paths: in head = True
.claude/rules/phase345-artifacts.md           paths: in head = True
.claude/rules/registrations-and-draws.md      paths: in head = True
.claude/rules/telegram-collection.md          paths: in head = True
```

**25 730 B on disk, 0 B at boot.**

What stays in `./CLAUDE.md`: identity, Where the truth lives, File ownership, Rules, the two Pitfalls
that are **not** collector-scoped (sarcasm labelling, the scorer as the single judge), Second brain,
Stack & commands, Tooling with a one-line `graphify` trigger. **6 999 → 4 581 B, 115 → 80 lines**,
against its own ≤200-line bar. Commit `e2ca966`; census **10.4K → 9.8K**; `make check`
**2 967 / 2 skipped**.

## D3 — `~/CLAUDE.md`: the Dev Stack is PARKED, not deleted

This file is outside the repo, so it is snapshotted first and shown on both sides.

```
BEFORE ~/CLAUDE.md           c5fee9d2c94ed5dbb6d0445a0d10ebc6a94453d6ecd12305b25858216d3cb1d6 350 B
AFTER  ~/CLAUDE.md           e8b25bc5d5e9f8900362e50759bd2279d2068b25475ef4c77c503ab85adb23db  23 B
NEW    ~/dev-stack-parked.md ce5e18510f51e699349428c33f9f86eff12852c3b469926e36fda14bb54a0e51 840 B
```

Three proofs before the cut:

```
$ grep -nE '(^|[[:space:]])@[[:alnum:]._/~-]+\.md' ~/CLAUDE.md ~/.claude/CLAUDE.md CLAUDE.md
none                                  # no @import exists at all, so none can point at the parked file

$ find ~/Desktop/Projects ~/Documents -maxdepth 3 -name CLAUDE.md
/Users/hdv_1987/Desktop/Projects/market-pulse-llm/CLAUDE.md
/Users/hdv_1987/Desktop/Projects/FlashArb-Bot/CLAUDE.md
/Users/hdv_1987/Desktop/Projects/logistics-rl-gnn/CLAUDE.md
$ … | xargs -0 grep -lE 'Bun 1\.2|Foundry|gsd-pi|Antigravity|Aider'
                                      # empty: no project on this machine consumes the parked stack

$ grep -rn "dev-stack-parked" ~/CLAUDE.md ~/.claude/CLAUDE.md ~/.claude/settings.json CLAUDE.md .claude/
                                      # empty: nothing points at it after the move either
```

The section is inside `~/dev-stack-parked.md` byte for byte, under a header saying what it is, why it
is out of the load path, and that the operator re-homes it into a specific project if one ever needs
it. `~/CLAUDE.md` keeps its heading and nothing else — the blank separator line went with the section
it separated, the same trade D1 made for every evicted block. **327 of 350 bytes now cost 0 at every
session start of every project on this machine.** Census **9.8K → 9.7K**.

Nothing here is a repo file, so this step has no commit; the record of it is this section, the shas
above, and the ADR.

## D4 — the target, from the measurement, last

Three runs, same invocation, and they agree:

```
$ python3.11 scripts/context-census.py
brain-census: 9.7Ktok boot tax
brain-census: 9.7Ktok boot tax
brain-census: 9.7Ktok boot tax
```

The reading decomposed, so the floor is checkable and not a screen:

```
    1,974 B  /Users/hdv_1987/.claude/CLAUDE.md
       23 B  /Users/hdv_1987/CLAUDE.md
    4,581 B  /Users/hdv_1987/Desktop/Projects/market-pulse-llm/CLAUDE.md
   18,756 B  MEMORY.md (loaded)
   13,457 B  knowledge/hot.md
        0 B  .claude/rules/*.md without paths:
   38,791 B  TOTAL -> 9.6977K -> printed 9.7K
```

**The rounding is stated rather than delegated.** The floor is the census's own printed one-decimal
reading — the figure that is reproducible from the output above — so floor = **9.7K**;
9.7 × 1.1 = **10.67**; half-up to one decimal = **10.7**. Registered:
**`TARGET_KTOK = 10.7`**. The sitting's own projection (floor ≈9.6 → target ≈10.5) is a forecast and
was not used; the measured floor is 0.1K above it.

**The constant had four homes, not two** — enumerated with one grep before the edit, and all four
move in commit `ab372c4`:

| file | what it was | what it is |
|---|---|---|
| `scripts/context-census.py:15` | `TARGET_KTOK = 9.0` | `10.7` |
| `scripts/context-census.py:16–18` | «Suspended, not moved …» | the formula, the measured floor, the ADR that ends the suspension |
| `scripts/context-census.py:6` | «warns above 9K» | «warns above `TARGET_KTOK`» — the literal is gone |
| `tests/test_context_census.py:10, 34` | «It is SUSPENDED … not moved», `== 9.0` | the re-registration, `== 10.7` |

The warning stops firing, which is the visible half of the ruling:

```
brain-census: 9.7Ktok boot tax
```

**The floor contains a region my own commits rewrite.** `scripts/refresh-hot-cache.py` regenerates
the AUTO-GEN block from `git log -5` at every SessionStart, and this contract's commit subjects are
long. Bounded by calling the **reader** `build_auto()` and never `main()`
([[the-producer-is-not-the-verifier]]) — `git status --porcelain` stayed empty across the check:

```
AUTO-GEN region now :  1,300 B
AUTO-GEN region next:  1,257 B   (what the next SessionStart writes)
drift               :    -43 B = -0.0107K against a 1.0K margin (10.7 - 9.7)
```

The registered number survives the next boot with 1.0K of headroom against a 0.01K wobble.

The ADR is `knowledge/decisions/boot-tax-re-registered-from-the-measured-floor.md` (commit
`1f48431`), in `INDEX.md`, and it links to — and un-suspends —
`boot-tax-target-suspended-and-the-census-axis`.

## Verify

```
$ python3.11 scripts/context-census.py
brain-census: 13.2Ktok boot tax  ⚠️ > 9.0K target — …        # BEFORE step 0.5
brain-census: 13.2Ktok boot tax  ⚠️ > 9.0K target — …        # after step 0.5 (predicted 0 B)
brain-census: 10.4Ktok boot tax  ⚠️ > 9.0K target — …        # after D1
brain-census:  9.8Ktok boot tax  ⚠️ > 9.0K target — …        # after D2
brain-census:  9.7Ktok boot tax  ⚠️ > 9.0K target — …        # after D3 — the floor, three times
brain-census:  9.7Ktok boot tax                              # after D4: under the registered 10.7

$ make check
ruff check .
All checks passed!
2967 passed, 2 skipped in 499.36s (0:08:19)

$ python3.11 -m pytest tests/test_volume_calc_5c1.py -q      # right after the hot.md edit
10 passed in 0.08s

$ python3.11 scripts/check-wikilinks.py
check-wikilinks: OK, none broken

$ wc -l CLAUDE.md
      80 CLAUDE.md

$ wc -c CLAUDE.md ~/.claude/CLAUDE.md ~/CLAUDE.md knowledge/hot.md
    4581 CLAUDE.md            (was 6 999)
    1974 ~/.claude/CLAUDE.md  (untouched — the operator's own working law)
      23 ~/CLAUDE.md          (was 350)
   13457 knowledge/hot.md     (was 24 662)
   20035 total                (was 33 985)

$ git status --porcelain
                                                             # empty, before this report
```

`make check` was run at **every** commit boundary and was green at each: `a26db9f` 2 967 · `cf00a44`
2 967 · `e2ca966` 2 967 · `ab372c4` 2 967 (the run above). Step 0's two commits changed nothing in
the working tree, so the 2 966 baseline run is their boundary. The final run stands at `1f48431`;
this report's own commit adds one file under `docs/reports/`, which no test in the suite reads
(`tests/test_templates.py` reads `knowledge/templates/`, `tests/test_reader_gold_r2.py` one path
under `knowledge/decisions/`).

**The DO NOT's check that the Verify block does not name.** Pinned records must match after as
before, so preflight was run — by path, because its grep-join cannot reach a data file that never
contains its own name (Dv532):

```
$ PYTHONPATH=src python3.11 scripts/preflight.py docs/labels-pass1-r1.jsonl
[3] pins — 5 of the 23 touched paths are pinned by a record
    docs/labels-pass1-r1.jsonl              <- results/labels_pass1_r1_provenance.json.labels.sha256 776b204f3d3a…
    scripts/build_pass1_label_pack.py       <- results/pass1_label_pack_r1.json.producer.sha256 408bce3725ab…
    docs/label-pack-pass1-r1-blind40.md     <- results/pass1_label_pack_r1.json.blind.sha256 d2364ff3e30b…
    docs/label-pack-pass1-r1.md             <- 2 pins, both 5aec5c9835f8…
    results/pass1_label_pack_r1.json        <- results/labels_pass1_r1_provenance.json.pack.sha256 e5ca328e5d99…
[4] digests — sha256 of all 5 pinned paths, against what is pinned
    5 of 5 pinned paths match every digest on them
```

`check-wikilinks.py` scans `knowledge/**` and the memory directory — **not `docs/`** — so its OK
covers the new ADR and the INDEX row, and says nothing about the `[[…]]` in this report.

## Deviations from Dv537

| # | finding | tag |
|---|---|---|
| **Dv537** | **The audit table's home for one block is a roster claim, and the block stays.** «one memory lesson per idiom, all of them written» names a set instead of stating a mechanism. Five of the six idioms resolve to a passage; **«право исполнителя на отказ» is stated in no file** — the only hit in `knowledge/`, `docs/reports/`, `CLAUDE.md` and the whole memory directory is `MEMORY.md`'s index line for `a_refusal_is_an_outcome_with_a_price`, which is about a **billed boot**, and `guard-until`'s ADR:17 is about a contract's own refusal gate. The ruling said all eleven A-blocks go; the no-home law kept one, and this report is where that is visible. | `[cause: contract-gap]` `[[a-citation-is-not-a-record]]` |
| **Dv538** | **The moved constant had FOUR homes, not the two the contract names.** Beside `TARGET_KTOK` and its test pin, `scripts/context-census.py:6` carried a hardcoded «warns above 9K» in the module docstring, and `tests/test_context_census.py:10` asserted the SUSPENSION in prose — a claim the D4 commit makes false. Both are consumers a `grep -rn '9K\|9\.0'` finds and a diff on the constant does not. All four move together; the literal in the module docstring is replaced by the name, so the class cannot recur there. | `[cause: verify-gap]` `[[a-moved-constant-fails-green]]` |
| **Dv539** | **The contract routes two sentences to «the rule whose paths cover the collector scripts», and no such rule exists.** The registry holds three: `phase345-artifacts.md` (annotation/frozen artefacts), `registrations-and-draws.md` (prereg and pack producers) and `_TEMPLATE.md`. None of their 31 patterns reaches `scripts/collect_*`, `scripts/fetch_*` or `src/market_pulse/telegram_client.py`. A destination named with no file behind it is the same shape as a bar with no producer; created `.claude/rules/telegram-collection.md` with twelve patterns, all matching. | `[cause: contract-gap]` `[[a-registered-bar-may-have-no-producer]]` |
| **Dv540** | **The checker group C could break fails SILENT, not red.** `scripts/stale-check.sh` greps `**Last update:** <ISO>` and is `[ -n "$LU" ]`-guarded: a rewritten header that loses the date shape produces **no output at all**, which reads exactly like «in sync». Group C rewrites that very line. The header keeps the ISO date immediately after the marker and the script was RUN after the edit as the proof — reading the regex would have proved nothing about the file. | `[cause: verify-gap]` `[[a-checker-whose-failure-is-silence]]` |
| **Dv541** | **The file now contradicts the ruling that emptied it.** `hot.md`'s Next §2 and the ⛔ BOOT TAX blocker both still read «цель ≤9K ПРИОСТАНОВЛЕНА … пере-регистрация — от измеренного пола», and both sit on the contract's byte-intact list — twice, in D1's UNTOUCHED and in the DO NOT. They were true when written; D4 ended the suspension four commits later. Named, not fixed: the two-list conflict is the team lead's to resolve, and a silent edit of a protected block would be the worse error. | `[cause: contract-gap]` `[[the-gates-evidence-outlived-its-artifact]]` |
| **Dv542** | **A guard that runs after the write is not a guard.** The D1 script asserted the sealed literal `~$0.24/day` appears exactly once — it appears **twice** — and the assertion sat AFTER `write_text`, so a wrong invariant left a wrongly-edited `hot.md` on disk and the fix needed `git checkout`. The invariant was wrong, not the edit, and the file was recoverable because it was committed; on an uncommitted or out-of-repo file (this contract had one: `~/CLAUDE.md`) it would not have been. The out-of-repo edit was written the other way round — `assert not parked.exists()` and the kept text compared to the source BEFORE either file was written. | `[cause: process]` `[[a-guard-that-runs-after-the-write]]` |
| **Dv543** | **The registered floor includes a region this contract's own commits rewrite.** The census sums `knowledge/hot.md` whole, and its AUTO-GEN block is regenerated from `git log -5` at every SessionStart — with subjects this contract just made longer. Measured rather than assumed, and measured with the READER (`build_auto()`, never `main()`, `git status --porcelain` empty after): **−43 B = −0.011K** against the 1.0K the ×1.1 margin buys. Bounded, so the number registered today is defensible tomorrow. | `[cause: verify-gap]` `[[the-producer-is-not-the-verifier]]` |

## Process signals

1. **The eviction discipline earns its keep only when it refuses something.** Fourteen homes read
   clean and one did not; had all fifteen passed, the honest reading would have been that I read too
   fast, not that the table was good.
2. **A roster and a record look identical to grep and opposite to a reader.** Dv529 was written for
   memory pointers; it caught an idiom card here. The tell is the same both times — a home that names
   what the block is called instead of stating what the block says.
3. **Writing the number last is what made the formula worth pre-registering.** The floor came in at
   9.7K against the sitting's own ≈9.6K forecast; had the constant been written from the forecast,
   the target would now be 10.5 and the census would still be warning.
4. **Two files went out of the repo's protection this session** — `~/CLAUDE.md` and
   `~/dev-stack-parked.md`. Both were snapshotted by sha before the first byte moved, which is the
   only reason «byte-for-byte» is a checkable claim and not a promise.
5. **The contract left one thing it could not have foreseen: its own execution invalidates two
   protected blocks.** Dv541 is not a defect in the work; it is the cost of a byte-intact list
   written before the ruling that changes what those bytes say.
