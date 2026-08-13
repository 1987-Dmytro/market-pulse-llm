# 5c2-prep-c3a — the build track: cap 33, the post-text pass, the pre-filter census

**The Phase 4 cap is $33.00 in both homes, and the two records written under $30.00 still say
`fits: false` — which is now a sentence about a moment, held there by a test in both directions.**
**`market_pulse.loop` has a third `*_pass`: the post leg SPEC 3.18 (7)(e) ordered exists, runs on the
same instrument as the leaflet leg, and carries three of the four properties its siblings carry —
the fourth needs a fourth `evidence.KINDS` member, which is the team lead's fork and is measured
here rather than argued.** **The post leg's population is no longer a 9 158-post bound: 349 posts
pass the relevance pre-filter ($0.3291 with drift), and 318 of those 349 are community channels
while 29 rows in total carry a currency marker.**

Contract: `docs/PROMPT-5c2-prep-c3a.md`. Authority: `docs/SPEC.md` amendment **3.18 (7)** — the
operator's ruling on the prep-c2 STOP. **$0 session: nothing was spent, no pod, no endpoint, no
serverless job, no OpenRouter call, no Telegram client.** Phase 4 stands at **$23.8310 of $33.00**,
$9.1690 remaining.

---

## Step 0 — the tail, committed by path

`git status --short` at the start matched the contract's list exactly — five modified paths and two
untracked ones, no eighth:

```
 M docs/SPEC.md            M docs/STATUS.md          M knowledge/daily_logs/2026-08-13.md
 M knowledge/hot.md        M knowledge/index.md
?? docs/PROMPT-5c2-prep-c3a.md   ?? docs/reviews/
```

Three commits, staged by path, `git add -A` nowhere: `454cfa4` (SPEC + STATUS + this prompt),
`5d9a261` (the three vault paths), `affa8ca` (`docs/reviews/` — the operator's process audit).
Baseline before the first write-capable action: the whole gitignored `data/` tree hashes
`b0151164db18b9af93d35fd64365944f139e18b09cb1d74f25f27b369d4f09d3` over 1 496 files, and
`data/derived/` does not exist. Both re-measured at the end and unchanged.

`make check` before anything moved: **2 140 passed, 2 skipped**.

---

## Deliverable 1 — the cap moves 30 → 33 (3.18 (7)(b))

Both homes in one commit (`c4f0aba`), the 3.18 (3) mechanics exactly. The ledger diff is **2 changed
lines**, and the untouched half is measured rather than promised:

```
cap         30.0 -> 33.0
anchor      35.0 -> 35.0 | anchored_at same: True
sessions    35 -> 35 | byte-identical: True
```

**Reading the contract's ledger row.** It says "append the raise entry mirroring the 25→30
precedent". The precedent (`3cfd792`) appended **no session entry** — it moved `phase4_cap_usd` and
added a sentence to the top-level `note`; the `sessions` row at 07:59:22 came from a real
`runpod_guard --note` run with a live balance reading. SPEC 3.18 (7)(b) settles it in the same
breath — *"the anchor and every logged session UNTOUCHED"* — and a session entry would have needed a
`runpodctl` balance call this $0 contract forbids. So: the field, and a sentence appended to `note`
beside the two it supersedes (Dv280).

### The consumers, verified against disk before editing

| consumer | what happened |
|---|---|
| `scripts/runpod_guard.py:42` `PHASE_CAP_USD` | 30.00 → **33.00**; docstring now names both raises and the cap-in-force rule |
| `results/spend_phase4.json` | `phase4_cap_usd` 33.0 + the raise sentence; 35 sessions byte-identical |
| `tests/test_runpod_guard.py` 26, 192 | both fixture ledgers 30.0 → 33.0 (silent — the guard reads the constant, not the file) |
| same file, 82, 98, 116, 121 | four live tests, below |
| `tests/test_repair_phase4_ledger.py:100` | `guard.PHASE_CAP_USD == 33.00`; line 101's `CAP_IN_FORCE_USD != PHASE_CAP_USD` **verified still true** (25 ≠ 33), the gap now wider without the test changing shape |
| `tests/test_projection_5c2.py` :202, :259 | the meaning-flip class, below |
| `scripts/repair_phase4_ledger.py` 15–17, 42 | **not in the contract's table** — two dead-cap sentences corrected (Dv281). The note string written INTO the three repaired ledger entries is untouched: those entries are on disk and are history |
| prose | `knowledge/hot.md` regenerated at session end; `docs/STATUS.md` not touched (team-lead file) |

### Both directions, measured

Moving the constant alone reddened **six** tests — one more than the contract's table enumerates
(Dv282):

```
FAILED tests/test_runpod_guard.py::test_the_cap_refuses_the_next_start
FAILED tests/test_runpod_guard.py::test_the_volume_keeps_billing_while_the_pod_is_stopped
FAILED tests/test_runpod_guard.py::test_the_first_run_anchors_and_says_so
FAILED tests/test_runpod_guard.py::test_a_session_note_is_only_logged_when_the_start_is_allowed
FAILED tests/test_repair_phase4_ledger.py::test_the_history_is_scored_under_the_cap_that_was_in_force_not_todays
FAILED tests/test_projection_5c2.py::test_the_budget_is_the_ledger_entry_it_names_and_the_guards_own_cap
6 failed, 38 passed
```

Two of those FLIPPED rather than drifted — they went on measuring the opposite thing:

* `test_the_cap_refuses_the_next_start`: balance 4.99 is $30.01 spent, which is **under** $33.00 and
  allowed. Moved to 1.99 ($33.01), the same one cent over;
* `test_a_session_note_is_only_logged_when_the_start_is_allowed`: balance 4.00 = $31.00 stopped
  refusing at all. Moved to 1.00 ($34.00) — 2.00 would sit exactly ON $33.00 and still refuse
  (`spent >= cap`), so the boundary is left to the test above and this one keeps its margin.

**And the reverse direction — the cap put BACK to 30.00:**

```
FAILED tests/test_runpod_guard.py::test_the_volume_keeps_billing_while_the_pod_is_stopped
FAILED tests/test_runpod_guard.py::test_the_first_run_anchors_and_says_so
FAILED tests/test_repair_phase4_ledger.py::test_the_history_is_scored_under_the_cap_that_was_in_force_not_todays
FAILED tests/test_projection_5c2.py::test_the_budget_is_the_ledger_entry_it_names_and_the_cap_that_was_in_force
FAILED tests/test_projection_5c2.py::test_the_whole_window_did_not_fit_under_the_cap_in_force_and_fits_under_todays
5 failed, 39 passed
```

The acceptance requirement — an equality on 33.00 in a live, non-record test — is
`test_the_first_run_anchors_and_says_so`'s `written["phase4_cap_usd"] == guard.PHASE_CAP_USD ==
33.00`. `== guard.PHASE_CAP_USD` alone cannot do that job: it agrees with the constant whatever the
constant says. (`test_the_cap_refuses_the_next_start` is correctly indifferent — $33.01 is over both
caps.)

### The meaning-flip class, and the one that stayed green

`results/projection_5c2.json` was written under the 30 cap and 3.18 (7)(b) forbids regenerating it.
**Its bytes did not change.** Two tests decouple by the cap-in-force pattern:

1. the budget test pinned `record == guard == ledger` as one number — true of one moment, when the
   three were one number. It now pins `budget["phase_cap_usd"] == CAP_IN_FORCE_AT_WRITE_USD ==
   30.00` and asserts it **different** from the 33.00 the guard and the ledger now carry.
2. `test_the_whole_window_does_not_fit_and_the_record_says_so` **did not go red** — it reads the
   record's own fields, so it stayed green while its sentence inverted: the same $7.6870 with drift
   now fits inside the $9.1690 that remains. This is the trap the clause exists for (Dv283). It is
   renamed and carries both halves — the record's sentence about $6.1690, and the live reading:

```python
remaining_today = round(guard.PHASE_CAP_USD - RECORD["budget"]["spent_usd"], 4)
assert remaining_today == 9.1690
assert whole["usd_with_drift"] < remaining_today
```

---

## Deliverable 2 — the post-text pass (3.18 (7)(e))

`market_pulse.loop.post_pass`, beside `inference_pass` (:197) and `page_pass` (:455), carrying
`page_pass`'s own sentence: *the ordering, the seam and the failure mode are `inference_pass`',
deliberately.* Commit `72ac6a5`.

**One instrument, the other input shape.** `prompts.positions_messages_text_gm4` is the TEXT TIER of
3.18 (2) — bar 3, 0.8667, the leg that passed. The code path was opened before it was used, not
grepped: `positions_gm4_skub.run_leg` packs `[item["url"]] if "url" in item else item["text"]`, so
the page leg's payload is a one-image album and this leg's is a bare string.
`StubPostTransport` refuses an album for exactly that reason, and it subclasses `StubPageTransport`
so the four-outcome schedule is the sibling's rather than a copy of it.

**`price_origin` is inherited, not decided** (Dv286). `positions.origin_of("post_text")` *refuses* —
SPEC fixes no origin for that carrier because "a retail chain's post and an aggregator's repost are
the retailer speaking, and a community channel's post about prices may not be". The paid skub2 text
leg already answered `retail_leaflet` in the `else` of its `carrier in CARRIER_ORIGIN` test. A
second answer here would mean the rows the pilot scored and the rows the loop writes are not the
same observation. Named as `loop.POST_PRICE_ORIGIN` with a test asserting both it and the refusal.

**A fourth watermark key** (Dv284). `post_text`, not `posts`: they share an id space, which is why
the reflex is to reuse the key and why that is wrong — `posts` is how far COLLECTION walked, and one
completed extraction pass would tell the collector it had already fetched everything up to that id
and the channel would stop collecting. Its own record type for the same class of reason: `above`
subtracts the ids it finds in ONE file, and a page id and a post id are both channel message ids.

### The four properties, both directions

| property | how it is measured |
|---|---|
| durable write BEFORE the watermark | `test_an_interrupted_post_pass_leaves_the_watermark_and_the_queue_where_they_were` — a `RawStore` that raises between the answer and the write; the on-disk watermark never moved and both posts are still queued |
| the queue subtracts the answered set | `test_the_post_queue_subtracts_posts_a_killed_pass_already_answered` — two answered, cursor never saved, one left. **And the gap below** |
| the send seam is replaceable by a stub and nothing else | the pre-filter, the fenced rendering, `parse_positions`, the ladder and the ordering are the production path in the smoke; `test_the_post_stub_refuses_the_page_legs_payload_shape` holds the seam's contract |
| the refusal carries THIS leg's queue depth (Dv265) | measured on the REAL corpus: `--posts` without `--smoke` prints `27 rows are queued` for `@atb_market_official` while the comment leg's line above it says `0 rows are queued` |

### The fork — and it is the team lead's (Dv285)

There is no `evidence.KINDS` member for *"a post was read and yielded nothing"*, and this contract's
DO NOT freezes `KIND_FIELDS`. Both sibling legs always write a row per input — a `comment` row, a
`leaflet_page` row saying `n_positions: 0` — so their answered-set is exact. The post leg writes
only position rows, so a post that returns `[]` or an unparseable reply leaves **nothing** behind.

A COMPLETED pass is still idempotent: the watermark covers it. An INTERRUPTED one re-buys its empty
posts. It is a **cost, never a hole** — no row is lost and nothing downstream is wrong.

Measured twice, with the leaflet leg as the control on the SAME three stub answers:

```
test_an_interrupted_post_pass_re_asks_the_posts_that_yielded_nothing
  post leg   3 answered (2 positions, 1 empty, 1 refused) → queue after the kill: [4341, 4342]
  page leg   the same three answers                       → queue after the kill: []
```

and through the script, where it actually bites — a smoke never saves the cursor, so a second
`--posts --smoke` over an **exhausted** queue (`--limit 400`, Dv266's lesson) is not free:

```
test_a_second_post_smoke_over_an_exhausted_queue_re_asks_exactly_the_empty_posts
  transport_calls 2   asked 2   (the sibling test asserts 0 and 0 on five pages)
```

**The shape of the fix, so the ruling is one line:** a fourth `KINDS` member (`post_text`) with
`KIND_FIELDS[...] = ()` like `comment`, written LAST per post exactly as `leaflet_page` is, carrying
`n_positions` / `unreadable` as extras. Not taken here.

### The smoke, on the real corpus

```
PYTHONPATH=src python3 scripts/run_loop.py --once --smoke --posts \
  --channel @atb_market_official --limit 8

  stub-served @atb_market_official     8 posts, 6 positions, 2 unreadable, 2 empty,
                                       watermark now 1091
```

`data/loop_cursor.json` byte-identical before and after (`10989c43…`), `data/derived/` still absent.

**One consumer flipped.** `tests/test_projection_5c2.py` pinned `dir(loop)`'s `*_pass` list to
`["inference_pass", "page_pass"]` — it documented the REPO at the record's write moment, so it went
red on the fix 3.18 (7)(e) ordered. Rewritten to pin the RECORD's own sentence
(`posts_in_scope_and_unpriced.no_writer`), which stays true of its write moment forever, plus
`hasattr(loop, "post_pass")` — the writer that sentence predates.

---

## Deliverable 3 — the pre-filter census over this window ($0)

`results/census_c3a_posts.json`, commit `a39a8ad`, anchor `2026-08-09T00:00:00+00:00` (ratified).
`results/census_5c2.json` was not touched.

Nothing in it is a second implementation: the window is `census_5c2.window_of`, the screening is
`sku_prefilter_census.screen_rows`, the controls are its `run_controls`, the price is
`write_sku_projection_b2.text_marginal`, and the citations are `projection_5c2.cite` /
`quote_line`. What the file adds is the intersection — that frame, over this window, per channel.

```
window 2026-07-12 .. 2026-08-09 (28d, anchor 2026-08-09T00:00:00+00:00)
  9158 posts in window · 8926 with text · 349 pass the pre-filter (3.81%) · row-level reading 441
  of the passed: {'currency': 29, 'percent': 92, 'size': 328}
  priced at 2.8132 s/row → $0.3291 with drift
  selection pin vs census_5c2: AGREES on 59 channels
```

**The selection is pinned, not re-decided.** Every channel's in-window post ids are re-hashed with
`census_5c2.leg`'s own formula and compared to that record's `posts.ids_sha256` — 59 channels, all
agreeing. A row COUNT would not see a store that moved under a later re-run; the run exits 1 if any
channel disagrees, and the negative control drives exactly that.

**Seven channels say CANNOT ANSWER** (`@Evgenija_dutjache_menu`, `@dimakaminskyifit`,
`@dutyache_menu`, `@hydnem_prosto`, `@itsmamix`, `@lab_of_childhood`, `@skhudnennya`) — no posts
file, never walked. Not zero.

### The finding the pre-registration needs before it names a number (Dv290)

The pre-filter's rule is *a watchlist brand or a tracked category term **AND** a size/price pattern,
both on the same line*. On this window it is satisfied overwhelmingly by **recipes**:

| by what | number |
|---|---:|
| passing rows carrying a size (`г/кг/л/мл`) | **328** of 349 |
| passing rows carrying a currency marker (`грн`) | **29** of 349 |
| passing rows from `community` channels | **318** of 349 |
| passing rows from `official_retail` + `aggregator` | **30 + 1** |
| `@recepti` + `@mameni_recepti` + `@korolevakuchni` + `@retsepty` | **250 = 71.6%** |

Not one of the 29 priced lines comes from those four cooking channels; they are local news and
retail feeds (`@telegraf_kremenchuk` 8, `@ekomarket_shop` 5, `@VARUS_channel` 4, `@forainfo` 4,
`@gorishnie_plavni1` 4, `@silposilpo` 2, `@kremen_news` 1, `@msuaaaa` 1).

`positions.prefilter`'s own docstring says the filter cannot tell «Кефір — 400 мл» in an ingredient
list from an offer. This is the first time that sentence has a number under it. **The census reports
it and decides nothing** — narrowing the leg is prep-c3b's or the operator's.

### The leaflet corpus, for 3.18 (7)(d)

Re-counted from the manifest and quoted from the clause in the same block: **159 pages under 19
posts**, all `@atb_market_official`, 2026-07-01T17:53:57Z … 2026-07-23T06:35:09Z. The window holds
78 of them and the leg buys all 159.

---

## Deliverable 4 — the RECORD debt

`knowledge/decisions/5c2-stop-ruling-and-cap-33.md` + its INDEX line (commit `5c485bc`): the six
clauses of 3.18 (7), each with what it binds, and the clause that binds the TEAM LEAD — records
written under the 30 cap are never regenerated to fit the new one. The ADR names why that rule needs
writing down: `fits: false` stayed green across the raise while its meaning inverted, so nothing
would have gone red and the STOP would have read as unresolved forever.

`python3 scripts/check-wikilinks.py` → `OK, none broken`.

---

## Verify gate

### 1. `make check` after every commit

<!-- CHECKOUT-TABLE -->

### 2. The census's determinism pair

```
ab927a23fae51288bc464b3b3bcc4131520dde9792a4f69c3e86b93179511791  results/census_c3a_posts.json
--- run 2 ---
ab927a23fae51288bc464b3b3bcc4131520dde9792a4f69c3e86b93179511791  results/census_c3a_posts.json
producer sha matches script: True
```

Measured **after** `ruff format` last touched the producer (Dv288) — the record carries
`producer.sha256` over that file, so a formatting-only edit invalidates it exactly as a logic change
would.

### 3. The cap guards in both directions

Above, under Deliverable 1: six red under the naive form, five red with the cap moved back, the live
`== 33.00` equality among them.

### 4. `git log --oneline` and a clean tree

<!-- COMMITS -->

---

## Do NOT — what was not done

* **Nothing was spent.** No endpoint, template or serving config registered; `run_loop.ENDPOINT` is
  still `None` and `test_5c2_prep_c3a_leaves_the_endpoint_constant_closed` asserts it. No Telegram
  client.
* **No pre-registration was written**, in any file, under any name. That is prep-c3b.
* **`results/census_5c2.json` and `results/projection_5c2.json` are byte-identical**, and no record
  written under cap 30 was regenerated.
* `evidence.REQUIRED` / `KIND_FIELDS` / `KINDS` untouched — which is what made Dv285 a report and
  not a change. `src/market_pulse/positions.py`, the sealed sku artifacts and the team-lead files
  untouched. `RAW_STORE_SALT` not rotated.
* `data/` unchanged: `b0151164…` over 1 496 files at the start and at the end; `data/derived/` never
  created.

## Deviations

`implementation-notes.md` § *5c2-prep-c3a* — **Dv280–Dv290**, every one with a `[cause: …]` tag.
Two are the ones a reader should not skip: **Dv285** (the fourth evidence kind, the team lead's
fork) and **Dv290** (the population is recipes).

## Process signals

* The contract's consumer table is built by grep and misses what grep cannot see: `repair_phase4_ledger.py`'s docstrings were three true-sounding sentences about a dead cap, in a file the table does not name (Dv281).
* "Verify each against disk" caught one flipped test the table did not predict and one that stayed green while inverting — enumeration of consumers is not enumeration of MEANINGS (Dv282, Dv283).
* The contract said "append the raise entry"; the precedent it named did something else. Resolving it needed the actual diff of `3cfd792`, not the sentence about it (Dv280).
* What had to be discovered rather than read: that `evidence.KINDS` has no marker kind for this leg. The contract expected the existing kinds to suffice and said to STOP if not — the fork was findable only by building the leg and killing it.
* `ruff format` silently invalidated a shipped record's `producer.sha256`; `make check` cannot see it, because the formatter is not in the verifier (Dv288).
