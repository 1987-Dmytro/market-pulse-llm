# vault-dream — the loader's ceiling is re-derived from its own constants, 51 pointers leave with a proven home, and the boot-tax target is shown unreachable

`$0`. No cloud call, no project code, no frozen record, no gold, no prompt. Every command below ran
on this machine, and the only file this contract changed outside `knowledge/` is `MEMORY.md`, which
lives outside the repo and has no git history — so it was snapshotted first.

## Read back

- **The ceiling and the 75% target** — the loader is the Claude Code binary itself
  (`~/.local/share/claude/versions/2.1.234`); its `LOr()` compares the trimmed index against
  `vee = 200` lines and `dde = 25 000`, so the target is **≤150 lines and ≤18 750** on the loader's
  own byte axis, and the file ends at **147 / 18 166 = 73.5% / 72.7%**.
- **No home, no eviction** — a pointer may leave the index only if an ADR, report, review or daily
  log states that lesson's *mechanism*; naming the lesson is not stating it. Five candidates failed
  that test after their evidence was read, and all five stayed.
- **The mapping-table duty** — every line that left is a row below with the file:line of the record
  that holds it, and every evicted lesson's own file is still on disk (186 files, none deleted).
- **What runs in parallel and what that forbids** — the team lead is writing
  `docs/labels-pass1-r1.jsonl`. It appeared mid-session and was never staged, never read, never
  depended on; `docs/label-pack-pass1-r1*.md` was not touched either. That is also why the final
  `git status --porcelain` is not empty (Dv528).

## Step 0 — the tail, by path, in two commits

```
$ git status --porcelain
 M docs/STATUS.md
 M knowledge/daily_logs/2026-08-18.md
 M knowledge/hot.md            <- the fifth path; the contract's list has four
 M knowledge/index.md
?? docs/PROMPT-vault-dream.md
```

`e629569` the vault tail · `1be0ba2` the team-lead files, verbatim. Staged by path, never `-A`.

The fifth path is **not** a deviation this time: `knowledge/hot.md` is D1's own target, so the
contract routes it to the dream pass rather than to the tail. It is committed with D1.

## Step 1 — the constants, re-derived

### 1. The loader's ceiling — from the loader, not from the file's own header

`MEMORY.md`'s real path is
`~/.claude/projects/-Users-hdv-1987-Desktop-Projects-market-pulse-llm/memory/MEMORY.md` — outside
the repo, as the team lead's `find` showed. The loader that reads it is the compiled Claude Code
binary. Its constants, and the function that applies them:

```js
var hb = "MEMORY.md", vee = 200, dde = 25000;          // offset 274909329

function G7t(e){ let t = e.trim();
  return { trimmed: t, lineCount: dp(t,"\n") + 1, byteCount: t.length } }

function LOr(e, t="index"){                            // offset 274996801
  let { trimmed:r, lineCount:n, byteCount:o } = G7t(e), i = n > vee, s = o > dde;
  if (!i && !s) return { content: r, ... }              // <- nothing is dropped
  let a = i ? r.split("\n").slice(0, vee).join("\n") : r;
  if (a.length > dde) { let u = a.lastIndexOf("\n", dde); a = a.slice(0, u > 0 ? u : dde) } ... }

function kOb(e){ return { path: XBe(), type: "AutoMem", content: LOr(e).content } }
```

`XBe()` is `path.join(lh(), "MEMORY.md")` and `lh()` resolves to the per-project memory directory —
so `LOr` is the function that loads *this* file. The blocker's «200 lines» reproduces exactly
(`vee = 200`, counted as `dp(trimmed,"\n") + 1`).

**The byte limit is not bytes.** `byteCount` is `t.length` — JavaScript string length, i.e. UTF-16
code units — compared against **25 000**, while `scripts/context-census.py` caps the same file at
`25 * 1024 = 25 600` UTF-8 bytes. Two units and two numbers (Dv526). For this content the two run
1.5% apart, and UTF-8 bytes are the larger, so `wc -c` is the conservative axis: clearing 18 750 on
`wc -c` clears the loader's real ceiling too.

The loader also ships its own compaction advice, which the contract's 75% sits just above:
`gpv = 0.8` is where it starts warning, and `yLf = 0.7` is the size it tells you to compact to —
`Math.floor(cap * 0.7)` = **140 lines / 17 500 units**.

### 2. The consolidation target — headroom, formula printed

```
lines : 147 / 200 = 73.5%   bar 0.75 x 200   = 150      loader's own target 0.70 x 200   = 140
length: 18 166 / 25 000 = 72.7%   bar 0.75 x 25 000 = 18 750   loader's own target        = 17 500
wc -c : 18 447 / 25 000 = 73.8%   (the conservative axis, above)
```

Both axes are under the bar with **53 lines and 6 834 units** of headroom. The file was **not** cut
to the loader's 70%: the contract asks for headroom, not a squeeze, and the last five candidates
were held back because their evidence did not survive reading (Dv529).

### 3. Boot tax — measured before the first edit and after the last, same invocation

```
$ python3.11 scripts/context-census.py                 # BEFORE, before any edit
brain-census: 14.5Ktok boot tax  ⚠️ > 9.0K target — de-bloat: rules with paths: / shrink the MEMORY index / curate hot.md

$ python3.11 scripts/context-census.py                 # AFTER, after the last edit
brain-census: 13.1Ktok boot tax  ⚠️ > 9.0K target — de-bloat: rules with paths: / shrink the MEMORY index / curate hot.md
```

**The target was not reached, and it is not reachable from inside this contract's scope.** The
census budget for ≤9.0K is 36 000 B. Out of scope: three `CLAUDE.md` = 9 323 B. In scope but
rate-limited by the contract's own rule for it («touch only what fails that check»):
`knowledge/hot.md`, which ended at 24 532 B. That is **33 855 B = 8.46K before MEMORY.md contributes
one byte**, so ≤9.0K needs MEMORY.md ≤ **2 145 B** — about 16 index lines out of 185 entries, a 91%
eviction that the no-home-no-eviction law forbids. The table below was computed **before** the cut
and at the `hot.md` of that moment (23 885 B), which is what made it a decision and not a
post-mortem (Dv527):

| MEMORY.md | bytes | census | ≤9.0K? |
|---|---:|---:|---|
| 197 lines (before) | 24 980 | 14.55K | no |
| 150 lines (75% bar) | 19 020 | 13.06K | no |
| **147 lines (shipped)** | **18 447** | **12.92K** | **no** |
| 100 lines | 12 680 | 11.47K | no |
| 21 lines | 2 663 | 8.97K | yes |

`hot.md` ended 647 B larger than it started — the two blockers this contract was obliged to
write (Dv530) — so the shipped census reads **13.1K** where the table's 147-line row says 12.92K.

**The gap decomposed by file** (AFTER = 52 302 B = 13.08K):

| file | bytes | Ktok | in this contract's scope? |
|---|---:|---:|---|
| `knowledge/hot.md` | 24 532 | 6.13 | yes, but only what fails its check |
| `MEMORY.md` (capped at 25 600) | 18 447 | 4.61 | yes — moved 24 980 → 18 447 |
| `./CLAUDE.md` | 6 999 | 1.75 | no |
| `~/.claude/CLAUDE.md` | 1 974 | 0.49 | no |
| `~/CLAUDE.md` | 350 | 0.09 | no |
| `.claude/rules/*.md` | 0 | 0.00 | all three carry `paths:` — none loads at boot |

To reach 9.0K with MEMORY.md where it now stands, `hot.md` would have to fall to **8 230 B, −66.5%**.
That is an operator call about what leaves the live state, not an executor call, and it is now the
open half of the boot-tax blocker.

**And 19.1K → 14.5K was not this contract's doing.** Reconstructed from git: `hot.md` was 364 lines
/ 38 988 B before `/close` and 203 / 19 234 after it, which puts the pre-`/close` census at
**18.33K** — 0.77K short of the registered 19.1K, and the residual sits in inputs that are outside
git (`~/CLAUDE.md`, `~/.claude/CLAUDE.md`, MEMORY.md) and cannot be dated. What is provable:
`/close` banked −4.94K, the `pass1-data-prep` session gave +1.16K back by adding 36 curated lines
that were never committed, and **this contract moved 14.55K → 13.08K = −1.47K**: −1.63K out of
MEMORY.md, +0.16K back into `hot.md` for the two blockers it had to write.

## D1 — the dream pass

### MEMORY.md — section-scoped, snapshot-first, pass-through with an assertion

The file is not in git, so there is no diff to appeal to afterwards. It was copied to the scratchpad
before the first edit (`sha256 2eaa256c…`, 24 980 B), together with a tar of the whole memory
directory, and the transform reads the snapshot rather than the live file. It removes exactly the
listed stems, changes exactly one header line, adds exactly one, and then **asserts that every other
line is byte-identical to the snapshot** — that assertion is what makes it provably not a rewrite:

```python
body = [l for l in lines if l.strip()]                    # index lines are unique, so a
assert len(set(body)) == len(body)                        # content filter IS a positional one
removed_set = set(removed)
expect = []                                               # rebuild the expected file from the
for l in lines:                                           # snapshot by applying ONLY the change list
    if l in removed_set:
        continue
    expect.append(NEW_CEIL if l == OLD_CEIL else l)
    if l == INSERT_AFTER:
        expect.append(NEW_LINE)
assert out == expect, "a line moved or changed that was not on the change list"
```

```
$ cp MEMORY.md.snapshot MEMORY.md && python3.11 consolidate.py     # idempotent, off the snapshot
pass-through: 145 lines carried byte-identical from the snapshot
evicted 51 · header lines changed 1 · added 1
lines  147/200 = 73.5%   (75% bar = 150, loader's own target 140)
length 18166/25000 = 72.7%   (75% bar = 18750, loader's own target 17500)
$ shasum -a 256 MEMORY.md
03aa8f7d529469b00e1897ca548eaab742774679d17a66402d55eb8e39a15da0
```

The first version of that check filtered by line *content* on both sides, which would have passed
even if a retained line had been dropped for colliding with a removed one. It is positional now, and
the uniqueness assertion is what licenses the filter — the file rebuilt to the same sha under it.

**How the 51 were chosen.** Every one of the 185 index entries was mapped to its citations in the
four durable homes the contract names (`docs/reports/`, `knowledge/decisions/`, `docs/reviews/`,
`knowledge/daily_logs/`), resolving both the file stem and the frontmatter `name:` slug. 99 entries
have no citation at all — under the law those stay, whatever their value. Of the 86 that had one,
each candidate's passage was **read**, against one test: *does this passage state the lesson's
mechanism, or does it only name the lesson?* Five failed and stayed (Dv529). The 51 that left are
the table below.

**Two edits to the header block**, both section-scoped:

```
-Only the first 200 lines / 25KB of this file are loaded — keep one-liners here, put the content in
+Only the first 200 lines / 25 000 chars of this file are loaded (the loader's own `vee`/`dde`) — one-liners here,
 topic files. Volatile state (deploy/state/next) → `knowledge/hot.md` ONLY; one home per fact.
+Consolidated 2026-08-18 by `vault-dream`: 51 pointers evicted to proven durable homes — mapping table in `docs/reports/vault-dream.md`; every evicted lesson's own file is still on disk.
```

The first is the re-derived truth about the loader replacing the file's own inherited claim about
it. The second costs one line and is what makes the eviction reversible from inside the index: a
future session reading only `MEMORY.md` can still find what left and where it went.

### The Dv519 lesson — already landed, verified rather than re-landed

```
$ grep -n "codebook" MEMORY.md
145:- [The codebook quoted the answer key](the_codebook_quoted_the_answer_key.md) — a record may hold what an artifact built from it may not
$ grep -m1 "^name:" the_codebook_quoted_the_answer_key.md
name: the-codebook-that-quoted-the-answer-key
```

The pointer and the file both exist, with the `name:` slug that makes
`[[the-codebook-that-quoted-the-answer-key]]` resolve from STATUS, the `pass1-data-prep` report and
`hot.md`. It was written at 22:36 by the previous session — the one slot the operator's ruling
bought — after the contract and STATUS §130 were written (Dv524). Kept as it stands: its hook is
one compact line and says the same thing as the contract's phrasing from the other end.

### knowledge/index.md — verified, not touched

51 lines against the 200-line auto-dream cap (25.5%), and its content matches the vault exactly:
23 daily logs, 60 decisions, 1 runbook, 2 goals, 2 templates. It carries
`*Auto-generated by the Stop hook; do not edit by hand.*` and is regenerated by
`scripts/brain-session-end.py`, so there is nothing here a hand edit could improve and one thing it
could break [[corrections_break_derivations]]. No stale entries — nothing to curate.

### knowledge/hot.md — four edits, and only what failed the check

Sealed markers byte-intact (`AUTO-GEN START` / `AUTO-GEN END`, one each), the generated block above
`AUTO-GEN END` byte-identical, and the grepped price literal `quoted(HOT, "~$0.24/day", 0.24)`
untouched — all four asserted by the transform before it wrote.

1. **The BOOT TAX blocker** stated «`MEMORY.md` ВСЁ ЕЩЁ У ПОТОЛКА — 197 строк из 200, 24 980 байт».
   That stopped being true, so it is now the measurement plus the half that is still open: the
   ≤9K target needs a ruling about `hot.md`, not another consolidation.
2. **Next §4** announced `vault-dream` as written and queued. Replaced by what is left of it — the
   8.30K floor and the −61% that ≤9K would cost `hot.md`.
3. **The day summary** said «день трёх контрактов» and named three reports. One line added for the
   fourth; the chronicle itself stays in the daily log and this report, because `hot.md`'s own rule
   is that the archaeology of closed contracts does not come back here.
4. **A blocker that did not exist when the check was written** — `make check` came back RED for a
   reason outside this contract's footprint (Dv531). A suite that is red for everyone, unannounced,
   is exactly the live state this file exists to carry, so it is registered here with its owner (the
   next contract) even though it costs 639 B of the boot tax this contract is measuring.

Every blocker was checked for an owner and a decide-by. All seven name an owner; none carries a
calendar date, and each names a **deciding event** instead — the operator's ruling on the stuck
walk and on the right-hand side of a close, the `money-anchors` contract for the 19 refused ledgers,
the LoRA registration for bar P1, and now the operator's ruling on what leaves `hot.md`. Read that
way they pass; read as «a date» none of them ever has. Named rather than invented, because a
decide-by the executor makes up is not a decide-by.

## The mapping table — what left, and where its record lives

| # | what left the index | where its record lives (verified file:line) |
|---:|---|---|
| 1 | **Fixtures built on live data collide** — filter out the class you inject | `docs/reports/pass1-data-prep.md:306 (Dv522)` |
| 2 | **A brief can outrun the document** — grep the file before naming it the authority | `docs/reports/pass1-data-prep.md:302 (Dv518)` |
| 3 | **A guard on one path is not a guard** — grep every caller of the limited request | `docs/reports/probe-b.md:61` |
| 4 | **A commit must run its own suite** — check each one out | `docs/reports/guard-until.md:562 (Dv516)` |
| 5 | **An evidence artifact cannot be re-derived** — a screen's record is why rows were removed | `knowledge/decisions/guard-until-the-tolerance-that-was-a-window-bug.md:67` |
| 6 | **The fix that was not a fix** — changing one thing and seeing it work isn't a cause | `knowledge/daily_logs/2026-08-18.md:64-68` |
| 7 | **A failed fetch leaves the old ref** — "already up to date" is also the signature of a no-op | `knowledge/daily_logs/2026-08-08.md:463` |
| 8 | **The document's command is its own artifact** — the tests drove the same code through different flags | `docs/reports/guard-until.md:559 (Dv514)` |
| 9 | **A structurally unreachable zero** — ask what would have had to happen for the cell to be non-zero | `docs/reports/probe-b.md:174 (Dv400)` |
| 10 | **A green suite can have a shelf life** — the operator's first tick reddens it | `docs/reports/reader-v3-run.md:402` |
| 11 | **A comment-only edit moves the file's hash** — no row changed and five sealed records broke | `docs/reports/pass1-data-prep.md:212 + knowledge/daily_logs/2026-08-15.md:34` |
| 12 | **A rename the data cannot follow** — a header, a wire key, a filled-in file | `knowledge/daily_logs/2026-08-11.md:273` |
| 13 | **A guard wired only when it can fire** — the smoke path skips the optional gate | `knowledge/daily_logs/2026-08-11.md:416` |
| 14 | **A checkout that never happened** — checkout aborts on a dirty tracked file | `knowledge/daily_logs/2026-08-11.md:318` |
| 15 | **A law that grows loudly** — generalise the strip so the pin survives | `docs/reports/guard-until.md:555 (Dv511)` |
| 16 | **A new gate can subsume the old one** — on a uniform fixture both compute the same number | `knowledge/daily_logs/2026-08-11.md:447` |
| 17 | **The probe must cost what the run costs** — a 64×64 warm-up priced a leaflet page at 1/3.5 of the truth | `knowledge/daily_logs/2026-08-11.md:466` |
| 18 | **An invariant the new member cannot satisfy** — give v3 its own narrower rule | `knowledge/daily_logs/2026-08-11.md:579` |
| 19 | **A new guard can be shadowed by an old one** — read the message, not the exit | `knowledge/daily_logs/2026-08-12.md:185` |
| 20 | **A hash is not the claim it carries** — the pin guards the bytes, never the field the inheritance rests on | `knowledge/daily_logs/2026-08-12.md:167` |
| 21 | **A monkeypatch is not a reader** — the constant nothing reads | `knowledge/daily_logs/2026-08-15.md:80` |
| 22 | **The store key is coarser than the row** — a fan-out loses rows inside ONE append | `knowledge/daily_logs/2026-08-13.md:46` |
| 23 | **The marker is written last** — the row a queue reads as "answered" must land after what it marks | `knowledge/daily_logs/2026-08-13.md:49` |
| 24 | **Two readings of one clause** — compute both, refuse where they part | `docs/reports/guard-until.md:549 (Dv505)` |
| 25 | **A price is as representative as its sample** — one endpoint, two legs: 0.4% vs 2.43x | `knowledge/daily_logs/2026-08-14.md:34` |
| 26 | **A watermark past a window buries the backlog** — the queue reads 0, not the remainder | `knowledge/daily_logs/2026-08-14.md:38` |
| 27 | **A reproducible draw can be correlated** — three of five landed on rank 163 | `knowledge/daily_logs/2026-08-14.md:57` |
| 28 | **A deviation is dated, not just true** — `git log -S` on the mechanism | `knowledge/daily_logs/2026-08-14.md:46` |
| 29 | **Rebuild the input and compare bytes** — re-render the guessed split | `knowledge/daily_logs/2026-08-14.md:51` |
| 30 | **The hand-typed number fails the total** — it passed the gate it fed and broke the report's own sum | `knowledge/daily_logs/2026-08-14.md:47` |
| 31 | **A narrowing rule shrinks the sealed population** — the guard that compares registered vs bought | `knowledge/daily_logs/2026-08-15.md:38` |
| 32 | **A lift adds a key, a move only changes one** — read the pin's SHAPE before refactoring the file it | `knowledge/daily_logs/2026-08-15.md:48` |
| 33 | **Mirror the whole anchor, not the overlap** — 902 leaves was fewer lines than a hand-listed pair map | `knowledge/daily_logs/2026-08-15.md:50` |
| 34 | **A dimension belongs to the registry** — a cut off the evidence renders only what talked | `knowledge/daily_logs/2026-08-15.md:62` |
| 35 | **The helper that guesses its input's shape** — two shapes, one `.get`, a chart of zeros | `knowledge/daily_logs/2026-08-15.md:77` |
| 36 | **The template claims more than the rule counted** — «the only segment» came from the string file | `knowledge/daily_logs/2026-08-15.md:81` |
| 37 | **A sealed caller forces the default** — the frozen caller picks which behaviour is the default | `docs/reports/probe-b.md:111` |
| 38 | **An order key that is not total** — two spellings, one sort key, a build that differed between runs | `docs/reports/pass1-data-prep.md:124` |
| 39 | **«One object per name» reads as a map** — decide the parser's container tolerance before the freeze | `knowledge/daily_logs/2026-08-15.md:135` |
| 40 | **The setup is inside the cap** — divide the cap by the measured rate before opening a gated run | `docs/reports/probe-b.md:152` |
| 41 | **The control whose premise stopped being true** — the planted «unknown» name became law and the test kept passing | `docs/reports/reader-v3-run.md:401` |
| 42 | **A bar that counts passes on an unreadable reply** — the only gate that cleared was a zero over | `knowledge/daily_logs/2026-08-15.md:159` |
| 43 | **A container defect moves to the next field** — fix `entities` and the same shape lands in signals | `knowledge/daily_logs/2026-08-15.md:157` |
| 44 | **The class you asked for is free to verify** — `gpuIds` comes back from the create call | `knowledge/daily_logs/2026-08-15.md:153` |
| 45 | **A record must re-derive from what it publishes** — headline from full precision | `docs/reports/guard-until.md:556 (Dv512)` |
| 46 | **A window never asked is not an empty one** — three states, not two | `docs/reports/guard-until.md:546 (Dv502)` |
| 47 | **A gate downstream of the spend** — the boot before the warm-up had no ceiling and ate the whole cap | `knowledge/decisions/reader-v3-serverless-close-and-the-pod-ruling.md:36` |
| 48 | **One flag, two branches** — a command routing on STATE is two commands; drive both | `knowledge/daily_logs/2026-08-18.md:55` |
| 49 | **The producer is not the verifier** — running the script to check its input erased an operator ruling | `knowledge/daily_logs/2026-08-17.md:127 (Dv474)` |
| 50 | **A spread that is really a window** — decompose each outlier's mechanism before registering a tolerance from it | `knowledge/decisions/guard-until-the-tolerance-that-was-a-window-bug.md:34` |
| 51 | **A lagged reading is not a second opinion** — reproduce one reading from the other before calling the gap noise | `knowledge/decisions/guard-until-the-tolerance-that-was-a-window-bug.md:83` |

**Five candidates that did NOT leave**, because reading their evidence broke the claim (Dv529):

| candidate | what its only «home» actually says |
|---|---|
| `trace_the_producer_not_the_result` | `pass1-data-prep.md:66` cites it while proving a *different* claim (129/1 032 reproduces); the lesson's own mechanism is not stated |
| `unreadable_now_versus_never` | `2026-08-08.md:433` is «В память легли два урока: …» — a roster of what was written, not a record of what it says |
| `a_reproducible_probe_can_be_unrepresentative` | `2026-08-12.md:271` ends «Урок в память: [[…]] — рядом»; the paragraph above it is about a different fix |
| `the_guard_you_built_and_then_bypassed` | `guard-until.md:557` is Dv513, a **stale pin** — nothing there about a required parameter making the caller say something |
| `cooccurrence_is_not_explanation` | its hits record **Dv521**'s `max()` tie; the memory holds the 4.5g5 family-size measurement (23 co-occurring vs 10 explained), which no repo file states |

## Verify

```
$ python3.11 scripts/context-census.py            # BEFORE, before any edit
brain-census: 14.5Ktok boot tax  ⚠️ > 9.0K target — de-bloat: rules with paths: / shrink the MEMORY index / curate hot.md

$ python3.11 scripts/context-census.py            # AFTER, after the last edit
brain-census: 13.1Ktok boot tax  ⚠️ > 9.0K target — de-bloat: rules with paths: / shrink the MEMORY index / curate hot.md

$ make check                                      # against the final tree, after the last edit
tests/test_validate_pass1_labels.py:124: AssertionError
=========================== short test summary info ============================
FAILED tests/test_pass1_label_pack.py::test_the_pack_names_who_writes_the_labels
FAILED tests/test_validate_pass1_labels.py::test_the_domain_is_the_prompt_s_and_the_real_labels_file_does_not_exist
2 failed, 2957 passed, 2 skipped in 471.16s (0:07:51)
make: *** [check] Error 1
#  RED, and not by this contract — see Dv531. 2 957 + 2 = the registered 2 959; both failures
#  assert `not docs/labels-pass1-r1.jsonl.exists()` and the team lead wrote that file this session.
#  Run twice: once mid-session and once against the final tree — same two, same counts.

$ python3.11 scripts/check-wikilinks.py
check-wikilinks: OK, none broken

$ B=~/.local/share/claude/versions/2.1.234       # every literal this report quotes, grepped back
$ for lit in 'var hb="MEMORY.md"' 'vee=200,dde=25000' 'lineCount:dp(t,' 'byteCount:t.length}' \
             'function kOb(e){let{content:t}=LOr(e);return{path:XBe(),type:"AutoMem"' \
             'gpv=0.8,yLf=0.7' 'Math.floor(e.byteCap*yLf)'; do
    echo "$(LC_ALL=C grep -a -c -F "$lit" $B)  <<$lit>>"; done
1  <<var hb="MEMORY.md">>
1  <<vee=200,dde=25000>>
1  <<lineCount:dp(t,>>
1  <<byteCount:t.length}>>
1  <<function kOb(e){let{content:t}=LOr(e);return{path:XBe(),type:"AutoMem">>
1  <<gpv=0.8,yLf=0.7>>
1  <<Math.floor(e.byteCap*yLf)>>

$ wc -l -c ~/.claude/projects/-Users-hdv-1987-Desktop-Projects-market-pulse-llm/memory/MEMORY.md
     147   18447 /Users/hdv_1987/.claude/projects/-Users-hdv-1987-Desktop-Projects-market-pulse-llm/memory/MEMORY.md
#  147 / 200      = 73.5%  ≤ 150  (0.75 x vee)
#  18 447 / 25 000 = 73.8%  ≤ 18 750 (0.75 x dde, on the conservative UTF-8 axis)
#  18 166 / 25 000 = 72.7%  ≤ 18 750 (0.75 x dde, on the loader's own String.length axis)

$ ls ~/.claude/projects/.../memory/*.md | wc -l
     186                                   # unchanged: 51 pointers left, 0 files were deleted

$ git status --porcelain                          # at this contract's last commit
 M docs/STATUS.md                          # the team lead re-edited it at 23:51:57 — Dv528
?? docs/labels-pass1-r1.jsonl              # the TEAM LEAD's file, 500/500 — Dv528
```

That is the state **at the last commit**, and it is the last state this contract controls. The Stop
hook (`scripts/brain-session-end.py`) runs afterwards: it appends one `session ended (auto)` line to
`knowledge/daily_logs/2026-08-18.md` and re-stamps `knowledge/index.md` with a fresh timestamp, so
two vault paths go dirty again about a minute from now. That is by design — it is exactly how this
session's tail reaches the **next** contract's step 0, and it is where the four paths this contract
committed at its own step 0 came from. Its third output, `knowledge/.vault-state.json`, is
gitignored (`.gitignore:24`). The hook was read rather than run: running the producer to see what it
would produce is how an operator ruling got erased once [[the_producer_is_not_the_verifier]].

`ruff format --check` is not run separately here [[verifier_format_gap]]: this contract changed no
Python in the repo at all — the only tracked paths it touches are `knowledge/` and `docs/`, and the
transform script lives in the scratchpad and is never committed.

No `runpodctl`, no `git add -A`, no edit to any team-lead file.

## Deviations from Dv524

| # | what | tag |
|---|---|---|
| **Dv524** | **The Dv519 lesson had already landed before the contract asked for it.** The blocker and STATUS §130 say the lesson «has no home»; the previous session spent its one bought slot at 22:36 writing `the_codebook_quoted_the_answer_key.md` AND its index line, which is why the index stood at 197 of 200. Verified present with the matching `name:` slug and kept as it stands rather than re-landed or reworded. The document was right when it was written [[brief_can_outrun_the_document]]. | `[cause: contract-gap]` |
| **Dv525** | **The blocker's byte figure does not reproduce: 24 992 claimed, 24 980 measured.** The 12-byte gap is not noise — `hot.md` records it: the same bought slot «индекс уменьшился на 12 байт». The contract quotes the reading taken *before* that eviction landed. Named rather than silently corrected, because a figure that misses by exactly the amount the tree moved is a dated reading, not a wrong one [[brief_can_outrun_the_document]]. | `[cause: contract-gap]` |
| **Dv526** | **The ceiling's second axis is not bytes, and the repo's own instrument uses a different unit AND a different number.** The loader compares `t.length` — UTF-16 code units — against `dde = 25 000`; `scripts/context-census.py` caps the same file at `25 * 1024 = 25 600` UTF-8 bytes. For this content they run 1.5% apart (18 166 vs 18 447), so the census's cap is 2.4% loose in a unit the loader never uses. Reported and not fixed: this contract forbids project code. Both numbers ship, and the conservative one is the one the target is checked against [[id_spaces_that_look_comparable]]. | `[cause: tooling]` |
| **Dv527** | **The ≤9K boot-tax target is unreachable inside this contract's scope, and the inequality says so before any cut.** 9 323 B of `CLAUDE.md` that this contract may not touch, plus a `hot.md` it may only touch where the check fails, is 8.30K before MEMORY.md contributes a byte; ≤9.0K needs MEMORY.md ≤ 2 784 B ≈ 21 of 185 entries. Computed BEFORE the consolidation, shipped as a reachability table with the gap decomposed by file, and handed to the operator as the ruling it actually needs [[an_absolute_bar_needs_a_reachability_state]]. | `[cause: contract-gap]` |
| **Dv528** | **`git status --porcelain` cannot be clean, and DO NOT is why.** `docs/labels-pass1-r1.jsonl` appeared mid-session while the team lead labelled in parallel, and `docs/STATUS.md` was edited again at 23:51:57 — after this contract's step-0 commit — to record the labelling done. The Verify block wants an empty porcelain; DO NOT forbids staging, committing or read-depending on the labels file, and STATUS's own new paragraph routes BOTH to «шагом 0 следующего контракта». The prohibition wins and two paths ship in the output. Every commit staged by explicit path, so neither was ever at risk [[queued_prompt_claims_files]]. | `[cause: contract-gap]` |
| **Dv529** | **A citation is not a record, and five candidates only had a citation.** The first pass scored a durable home by grepping `[[slug]]` into reports, ADRs, reviews and daily logs — which proves a lesson was *named*, not that its mechanism was *written down*. Reading every candidate's passage killed five: three whose only hit is a «Урок в память: [[…]]» roster line, and two tagged onto a **different** incident (`Dv513` is a stale pin, not a bypassed guard; `Dv521` is a `max()` tie, not a family-size misread). All five stayed in the index, and the eviction fell 56 → 51 [[verbatim_quotes_must_be_grepped]]. | `[cause: verify-gap]` |
| **Dv530** | **The first `hot.md` rewrite grew the file 564 B — a boot-tax contract moving its own metric the wrong way.** The three required edits had been written as a four-line chronicle of this contract plus an eight-line blocker, which is exactly what `hot.md`'s own curation rule forbids («не восстанавливать сюда то, у чего есть дом»). Caught by re-running the census, not by a test: 12.9K read back as 13.1K. Rewritten to one summary line and a tighter blocker, net **+8 B**, and the boot-tax literals inside it fixed with same-length substitutions so the file could not move under its own report. The red suite then forced a fourth edit worth **+639 B** (Dv531), which is why `hot.md` ends **+647 B** and the shipped census is 13.1K and not 12.9K — named here rather than absorbed [[a_probe_must_not_create_what_it_measures]]. | `[cause: process]` |
| **Dv531** | **`make check` is RED, and this contract changed no Python.** 2 957 passed / **2 failed** / 2 skipped — the total is the registered **2 959**, with two flipped and none added or removed. `test_the_pack_names_who_writes_the_labels` and `test_the_domain_is_the_prompt_s_and_the_real_labels_file_does_not_exist` both assert `not docs/labels-pass1-r1.jsonl.exists()`; the team lead wrote that file during this session (it is already `??` in the porcelain of this contract's own step-0 commit at 22:49:26, before its first edit) and STATUS now records the labelling done, 500/500. `pass1-data-prep` sealed «the file does not exist YET» into the suite — a green with a shelf life that expired from exactly the work the pack was built to commission. NOT fixed here: `tests/` is project code, which this contract forbids, and the file itself is under DO NOT. It belongs to the next contract, in the same step that commits the labels verbatim [[a_green_suite_can_have_a_shelf_life]]. | `[cause: verify-gap]` |

## Process signals

1. **The instrument was in the binary, and reading it changed the answer.** «200 lines / 25KB» was
   inherited prose in the file's own header; the loader says 200 lines and 25 000 *UTF-16 units*.
   Every downstream number in this report — the 75% bar, the census's 2.4% loose cap, which axis is
   conservative — comes from having opened `LOr` instead of quoting the header that quoted it.
2. **The expensive half was proving homes, not choosing evictions.** The grep produced 86 candidates
   in seconds; reading their passages cost the session's real time and deleted five of them
   (Dv529). A mapping table built from the grep alone would have been 56 rows, five of them false,
   and nothing in the artifact would have shown which five.
3. **The law's side effect is worth naming: the index is now biased toward lessons nobody wrote up.**
   99 of 185 entries have no repo citation at all, so they stay regardless of value, while
   well-recorded general laws are exactly the ones eligible to leave. That is the correct trade
   under «no home, no eviction» — and it means the cheapest way to keep the index healthy is for
   future reports to keep tagging their deviations, which is what makes a lesson evictable later.
4. **Two numbers came out wrong, and both taught more than the ones that came out right.** ≤75%
   took a mechanical cut; ≤9K took an inequality, and the inequality is what turns «missed» into a
   priced operator decision — 66.5% of `hot.md`. And `make check` is red against a baseline that was
   already stale when the contract quoted it: two tests assert `docs/labels-pass1-r1.jsonl` does not
   exist, and the team lead spent this session creating it. A green that depends on work **not**
   having happened yet is a clock, not a verifier.
5. **A file with no git history has to be snapshotted or it cannot be reported on.** `MEMORY.md` has
   no diff, no `checkout`, no blame. The mapping table is generated from snapshot-minus-final, not
   hand-typed from memory of what was cut, and the pass-through assertion is the only evidence that
   the 145 lines nobody meant to touch were not touched.
