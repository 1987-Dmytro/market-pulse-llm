# 5c2-prep-c1 — the record track: the guard aims at the real root, and the positions leg keeps evidence

**Contract:** `docs/PROMPT-5c2-prep-c1.md`; `docs/SPEC.md` amendment 3.18 (2) and 3.18 (6); the B1
finding of the prep-b acceptance. **Cost: $0.** No pod, no endpoint, no template, no serverless job,
no OpenRouter call, no Telegram client. Phase 4 spend is where prep-b left it: **$23.8310 of
$30.00**, remaining $6.1690.

Three sentences, what is true now that was not true this morning.

**The smoke guard watches the directory a regression would actually write into.** It named
`tmp_path / "derived"` — a path no code in the repository references, so it could not fire; it now
names `runner.DERIVED_ROOT`, and a second test plants three evidence rows in a patched copy of that
root and shows the same assertion refuse.

**The loop has its second leg, and `leaflet_page` and `position_row` have a producer.** One page in
through the same seam, one page row and one row per position out, with the record durable before the
watermark moves — so 5c2-run is no longer the contract that would first write those two shapes.

**The derived store can hold a fan-out.** `RawStore` keyed rows on `(channel, msg_id)`, and the
three positions of one page all carry that page's msg_id: two of them were dropped inside a single
`append()`, silently. Measured red, then fixed by a key that falls back to the msg_id everything in
`data/raw/` already uses.

---

## Deliverable 1 — B1: the guard aims at the real root

`tests/test_loop.py::test_a_smoke_leaves_the_real_cursor_and_the_derived_store_untouched` ended with

```python
assert not (tmp_path / "derived").exists(), "data/derived/ is the real pass's, not a smoke's"
```

`wire_infer` deliberately does not patch `DERIVED_ROOT` and the smoke writes to `SMOKE_DERIVED`, so
the directory in that assertion had no producer anywhere and the guard was green by construction.

The assertion now lives in one place and names the real constant:

```python
def the_derived_root_is_untouched() -> None:
    assert not runner.DERIVED_ROOT.exists(), "data/derived/ is the real pass's, not a smoke's"
```

**Spelled once on purpose.** A sensitivity test that re-typed the assertion would prove a look-alike
refuses and say nothing about the one that runs in the smoke test.

### Both directions

```
tests/test_loop.py::test_a_smoke_leaves_the_real_cursor_and_the_derived_store_untouched PASSED
tests/test_loop.py::test_the_derived_root_guard_refuses_a_row_planted_in_the_real_root  PASSED
tests/test_loop.py::test_a_page_smoke_leaves_the_real_cursor_and_the_derived_store_untouched PASSED
3 passed, 48 deselected in 0.40s
```

The sensitivity test patches `runner.DERIVED_ROOT` into a tmp root, plants rows through **the pass's
own writer** (`RawStore` pointed at that root — exactly the regression being guarded against), and
asserts the guard raises. Patching the constant is legitimate in that test and nowhere else: there
it is read, by the guard, one line later.

### The old form, measured

Before trusting the new one, the guard was temporarily reverted to the B1 spelling and the
sensitivity test re-run against the same three planted rows:

```
        planted = RawStore(runner.DERIVED_ROOT)
        assert run(store, planted, posts, state)["written"] == 3

>       with pytest.raises(AssertionError, match="the real pass's"):
E       Failed: DID NOT RAISE <class 'AssertionError'>
```

Three real evidence rows in the real destination, and the old assertion stayed green. The patch was
reverted immediately (`tests/test_loop.py` restored from a byte copy, suite re-run).

### The two consequences the contract asks for, and where they are written

- `run_loop.DERIVED_ROOT`'s docstring now names its first reader — the guard, not a writer. The
  "written by nothing yet" half is still true and stays.
- The test's docstring says what to do the day a legitimate writer creates `data/derived/`: it goes
  red **on purpose**, and the guard is redesigned WITH that writer (existence check → before/after
  snapshot), never deleted to make the suite green.

`wire()`'s comment was corrected too: it claimed the smoke test "asserts the real thing instead —
that no directory appears there at all", which was false about *that* directory.

---

## Deliverable 2 — the positions leg keeps evidence, at zero cost

### The store had to be able to hold the rows first

`RawStore._by_file` skips a record whose `(channel, msg_id)` it already holds **and marks each one
seen as it iterates**, so N positions sharing a page's msg_id collapse inside one call. Proven
before anything was changed:

```
>       assert store.append(rows) == 3
E       AssertionError: assert 1 == 3
E        +  where 1 = append([{'brand': 'Рудь', …}, {'brand': 'Яготин…', …}, {'brand': 'Своя Лінія', …}])
```

The key is now `dedup_key(record)` — `row_id` when a record carries one, `msg_id` otherwise. No
record ever written carries `row_id`, so every post and comment keeps the key it always had;
`tests/test_raw_store.py::test_the_raw_v1_stores_still_hash_to_their_baseline` is green and the six
store files hash to their pins. `StoreIndex` grows `keys` **beside** `ids` rather than widening
`ids`: a queue subtracts the MESSAGES it has answered, and one answered page is one message and
three rows.

`raw_store.py` is in no frozen list in this contract and is sha-pinned in no pre-registration
(checked: only `src/market_pulse/positions.py` is, in `sku_pilot_prereg_b2.json` and
`sku_pilot_prereg_v2.json`). So this is an executor-file change, not the 3.18 (6) shape question the
brief says to STOP for. `evidence.REQUIRED`, `evidence.KIND_FIELDS` and `positions.py` were not
touched.

### The leg

`loop.page_pass` is `inference_pass`' ordering, seam and failure mode: render, send, **write**, and
only then move the watermark. The queue filter is now one function both legs call (`loop.above`), so
the page queue subtracts the watermark AND the pages already in the store — which is what makes a
re-run free after a pass that was killed.

The sealed instrument is reached by import, never copied: `positions.parse_positions`,
`positions.tier_from_presence`, `positions.origin_of`, `evidence.presence`.

**Where the ladder is called from, and why it is two paths.** The `tier` a row STORES comes from
`Position.tier()`; `positions.tier_from_presence` is what the invariant re-derives it WITH. The
contract's letter says "the ladder through `tier_from_presence`", and writing the stored value with
that function too would make the re-derivation compare it to itself — the invariant would hold on a
`presence` that was wrong. The two are held together by
`tests/test_evidence.py::test_the_presence_fields_re_derive_the_ladders_own_tier` over every
combination of the four optional fields, and per row by the pass test above.

**The page row is written LAST.** `RawStore.append` writes file by file — one `open("a")` per record
type, closed before the next — and `queued_pages` keys the queue on the page record type, so the
page row on disk **is** the answered-marker. Written first, a kill between the two file writes would
leave a page row claiming `n_positions: 2` with nothing behind it and the re-run would subtract that
page as answered: rows gone for good, hole invisible. Written last, the same kill leaves the
positions with no marker, the page is re-asked, and `dedup_key` skips what is already there. Both
directions are tested (`test_a_kill_between_the_two_files_leaves_the_page_queued`,
`test_the_resumed_page_writes_only_what_the_kill_left_missing`), and the test is sensitive to the
ORDER, not merely to the failure — under page-first it goes red with `assert [] == [0, 1]`, measured
by temporarily restoring that order.

**`image_sha256` is the sha of the bytes sent.** `render_page` reads the file ONCE and builds both
the hash and the payload from that one `bytes` object — hashing a path separately from encoding it
is two reads of a file that can move between them.

### The stub smoke, on the real pages

```
PYTHONPATH=src python3 scripts/run_loop.py --once --smoke --pages --channel @atb_market_official

  stub-served @atb_market_official        5 pages,    4 positions, 1 unreadable, watermark now 4344
wrote results/smoke/loop_5a.json (gitignored — quote it, do not point at it)
```

Against an EMPTY smoke store: the sandbox is throwaway and was cleared between the demonstrations
below. `StubPageTransport`'s schedule is per INVOCATION, so a window split across several runs of
the script gets a different fake answer per page than the same window answered in one (Dv268) —
which is why the counts below come from a single run and not from a continuation.

One `leaflet_page` row's KEYS:

```
["at", "channel", "image_path", "image_sha256", "model_revision", "msg_id", "n_positions",
 "parent_msg_id", "prompt_sha256", "record_type", "rendering", "reply", "row_kind", "served_by",
 "task", "unreadable", "warnings"]

  image_path   : …/data/annotation/captions_5c1/posts_media/atb_market_official_4340.jpg
  image_sha256 : 7ae55c29dc8d0adce4cec35cc3d4300ec696fe9f32141d7e34f6368054ec5002
  n_positions  : 1   warnings: [['multipack', 'discount_footnote', 'price_from']]
  task         : positions_post_gm4   prompt_sha256: ca6303c157d46e70…   model_revision: None
```

That sha is the one `results/post_media_5c1.json` pinned for the page when 5c1 downloaded it — an
independent check that the hash is of the real bytes and not of something the run built.

The triple-warning `position_row`'s KEYS, and its re-derivation:

```
["at", "channel", "image_path", "image_sha256", "model_revision", "msg_id", "ordinal",
 "parent_msg_id", "position", "presence", "prompt_sha256", "record_type", "rendering", "reply",
 "row_id", "row_kind", "served_by", "task", "tier", "warnings"]

  row_id   : @atb_market_official:4340:0   msg_id: 4340   parent_msg_id: 4340
  warnings : ['multipack', 'discount_footnote', 'price_from']
  presence : {'brand': True, 'line': False, 'category': True, 'size': True, 'attribute': True}
  tier     : position

  RE-DERIVATION: positions.tier_from_presence(**row["presence"]) == "position" == row["tier"] -> True

  position : {"brand_raw": "Рудь", "brand_id": "rud", "category": "ice-cream",
              "size_value": 100.0, "size_unit": "г", "pack_count": 6, "attribute_pct": 12.0,
              "price_promo": 89.9, "price_qualifier": "from", "discount_pct_printed": 31.0,
              "discount_footnote": true, "depth": null,
              "carrier": "leaflet_page", "price_origin": "retail_leaflet"}
```

All three SPEC 3.17 (13)(a) families on one position, `depth` correctly `null` (a «від» promo price
with no old price has no depth), and `price_origin` fixed by the carrier rather than by the caller.

### Ordering and idempotence

The interrupted-pass and the re-run, both legs, asserted on the cursor ON DISK and on the artifact:

```
tests/test_loop.py::test_an_interrupted_pass_leaves_the_watermark_and_the_queue_where_they_were PASSED
tests/test_loop.py::test_a_rerun_of_the_same_pass_writes_no_new_record_and_leaves_the_watermark  PASSED
tests/test_loop.py::test_the_queue_subtracts_rows_a_killed_pass_already_answered                PASSED
tests/test_loop.py::test_an_interrupted_page_pass_leaves_the_watermark_and_the_queue_where_they_were PASSED
tests/test_loop.py::test_a_rerun_of_the_same_page_pass_writes_no_new_rows_and_leaves_the_watermark   PASSED
tests/test_loop.py::test_the_page_queue_subtracts_pages_a_killed_pass_already_answered           PASSED
tests/test_loop.py::test_the_positions_of_one_page_all_survive_the_write                         PASSED
8 passed, 43 deselected
```

And through the script, on the real 159-page queue. **The first attempt at this was the wrong
demonstration** — `--limit 5` against 159 queued pages, so the second run correctly answered the
NEXT five (Dv266, and prep-b's Dv257 was the same mis-step). Redone by exhausting the queue:

```
--limit 400 (first)    159 pages,  120 positions,  40 unreadable
  leaflet_pages/atb_market_official.jsonl  8490e0489f5aad4b…   159 lines
  position_rows/atb_market_official.jsonl  831d48a9cc364335…   120 lines

--limit 400 (second)     0 pages,    0 positions,   0 unreadable    transport_calls: 0
  leaflet_pages/atb_market_official.jsonl  8490e0489f5aad4b…   159 lines
  position_rows/atb_market_official.jsonl  831d48a9cc364335…   120 lines
```

Zero asked, zero transport calls, both files byte-identical. Note the second run started from a
watermark of `None` — a smoke never saves the cursor — so what made it free was the derived store's
own ids alone, which is exactly the killed-pass path.

### The guard covers the new leg

```
$ PYTHONPATH=src python3 scripts/run_loop.py --once --pages --channel @atb_market_official
159 rows are queued and no serving endpoint is registered. SPEC 3.11 (2) pre-registers a
serving-parity measurement before any serving number reaches an aggregate, so 5a queues rows and
sends none.
EXIT=1
```

**159, not 0.** The first version passed the COMMENT leg's queue depth to the refusal — a true
refusal reporting a number about something else (Dv265). Each leg now hands `inference_refusal` its
own depth. The comment leg's guard tests are untouched beside it, as the control:
`test_a_served_pass_without_the_smoke_is_refused_by_the_guard` and
`test_a_pass_with_no_mode_at_all_is_still_the_5a_live_refusal`.

`run_loop.ENDPOINT` is still `None` (`test_5c2_prep_b_leaves_the_endpoint_constant_closed`).

---

## Verify gate

### 1. `make check` after every commit, and the per-commit checkout table

Six commits, each checked out into a git worktree with `data/` symlinked to the repo's (Dv193), the
row above the session as the control:

| commit | result | failed |
|---|---|---|
| `51ed64a` **(control, pre-session)** | 1 failed, 2080 passed, 2 skipped | `test_collect_5c1.py::test_the_guard_reads_the_pinned_paths_off_the_pin_file` |
| `4cde4f4` | 1 failed, 2080 passed, 2 skipped | same nodeid |
| `a7fd937` | 1 failed, 2080 passed, 2 skipped | same nodeid |
| `464a33c` | 1 failed, 2081 passed, 2 skipped | same nodeid |
| `31236c3` | 1 failed, 2083 passed, 2 skipped | same nodeid |
| `0af552c` | 1 failed, 2100 passed, 2 skipped | same nodeid |

One failure, the same nodeid on every row **including the control** — the Dv193 worktree symlink,
re-measured this session rather than inherited. In the working tree itself:

```
$ make check
2101 passed, 2 skipped in 60.02s
$ ruff format --check .
252 files already formatted
```

(`make check` does not run the formatter; it was run separately.)

### 2–4

Above: D1 both directions, the smoke's record keys with the re-derivation line, the interrupted-pass
and idempotence outputs.

### 5. The session

```
0af552c feat(5c2-prep-c1): the loop's leaflet leg -- one page in, a page row and its positions out
31236c3 feat(5c2-prep-c1): the store's key is the row, not only the message
464a33c fix(5c2-prep-c1): B1 -- the smoke guard aims at the real derived root, in both directions
a7fd937 docs(vault): the prep-b session tail and hot.md's Next
4cde4f4 docs: 5c2-prep-c1 queued -- STATUS after the prep-b acceptance
```

Three commits follow and cannot be named here, because a file cannot carry its own hash: the one
that adds this report, the pre-authorised vault tail (the day's log and hot.md's curated block), and
the one that adds this paragraph. `git log --oneline 51ed64a..HEAD` is the enumeration.

Nothing outside the sandbox moved, hashed before the first write-capable action and again after the
last smoke:

```
data/loop_cursor.json   10989c439b4f80ba…   unchanged
data/raw (6 files)      9932fe8a787a6345…   unchanged
data/derived            ABSENT
results/                git diff --stat 51ed64a..HEAD -- results/   (empty)
```

## Do NOT — what was not done

Nothing was spent; no endpoint, template or serving configuration was registered and
`run_loop.ENDPOINT` was not opened. The census, the price projection and the paid session's
pre-registration were not touched — they are prep-c2. Nothing was written into `data/raw/` or
`data/derived/`; `RAW_STORE_SALT` was not rotated. No Telegram client was built and no media was
fetched — the page fixtures in the suite are two-pixel JPEGs generated by PIL, and the live smoke
read pages 5c1 had already downloaded. `src/market_pulse/positions.py`, `evidence.REQUIRED`,
`evidence.KIND_FIELDS`, every sealed sku artifact and every team-lead file are unchanged.

## A number that fell into my lap (prep-c2's, not mine to use)

The leaflet page population reachable today is **159 pages across 19 posts of one channel**
(`@atb_market_official`), from `results/post_media_5c1.json`. Under the stub that produced 120
position rows, 40 unreadable pages and 39 empty ones — those three are the fake's schedule and mean
nothing about the model. Only the 159 is a real count, and prep-c2's census is where it belongs.

## Open, for the team lead

- **`image_path` is absolute** ("the path as the run saw it"). Every other artifact here names files
  repo-relative; if the 3.18 (6) pack wants that, it is one line in `run_loop.pages_of` (Dv264).
- **The page source is 5c1's collection manifest** and covers one channel. A general page source is
  the collector's, not this leg's (Dv267).

Deviations **Dv259–Dv267**: `implementation-notes.md`, section *5c2-prep-c1*.
