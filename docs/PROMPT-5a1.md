# PROMPT 5a.1 — acceptance tail of 5a + widened discovery (5 themes + seeds)

This file is the whole brief. Read ALSO: docs/SPEC.md §3.11 (4) **as amended
2026-08-06** (theme expansion; registry is FOUR channels) and
docs/RESEARCH-5a1-themes.md (operator verdict + seed handles). Do NOT re-read
PROMPT-5a wholesale; where this brief says "5a conventions", it means the
discovery record schema and the two ledger caveats whose exact ASCII bytes a
test already holds to PROMPT-5a.

Everything here is $0: Telegram free API only, no GPU, no serverless, no model
call of any kind. Read-back check: before coding, list in ONE line each — the
six fix items, the five themes, and the two things a live loop pass is still
forbidden to touch.

## Step 0 — commit the team-lead tail (by path, never `git add -A`)

docs/SPEC.md, docs/STATUS.md, docs/RESEARCH-5a1-themes.md, docs/PROMPT-5a1.md,
plus the Stop-hook tail: knowledge/daily_logs/2026-08-05.md, knowledge/index.md.
One commit. If `git status --short` shows anything beyond these, STOP and
report before committing.

## Deliverable 1 — fixes from the 5a acceptance (each lands with its guard)

Order matters: F1 must land BEFORE the Deliverable 3 scan runs.

- **F1 (MED).** `scripts/discover_channels.py`: the candidate loop's bare
  `except Exception` swallows `FloodWaitError` — a rate-limited candidate is
  mislabeled `verdict: "error"` and the scan keeps hammering. Branch on
  `FloodWaitError` BEFORE the generic handler, matching the
  `scripts/entry_check.py:187` pattern (abort the scan, keep what was
  collected, print the wait). Unit test with a mocked raise.
- **F2 (MED).** `scripts/poll_census.py`: a `--limit` run currently rewrites
  `data/raw/post_polls.jsonl` wholesale — the documented smoke would silently
  truncate 37 real rows. A limited run must NOT touch the real sidecar (skip
  the write or write a `--limit`-suffixed path). Test: run with a tmp store
  and `--limit`, assert the real sidecar path is not opened for write.
- **F3 (LOW).** `src/market_pulse/telegram_client.py:37`: drop `got
  {api_id!r}` from the numeric-check error — the swapped-.env case would
  print the API hash to stderr. Message keeps the variable NAME only.
- **F4 (LOW).** `src/market_pulse/loop.py`: spend guard `if endpoint is
  None:` → `if not endpoint:` — an empty-string endpoint from env/config in
  5b must NOT open the guard. Extend the existing negative-control test with
  `""`.
- **F5.** `results/poll_census_5a.json` promises the sidecar's sha256 (D12)
  but carries none. Add `sidecar.sha256` computed over the existing
  `data/raw/post_polls.jsonl` bytes, plus a `sidecar_sha256_added_at`
  timestamp — NO refetch, no other field changes; a test recomputes the hash
  from the file and matches the record.
- **F6.** Durable integrity baseline: write and COMMIT
  `results/raw_v1_baseline.sha256` — sha256 lines for all six
  `data/raw/posts|comments` store files in `shasum -c` format, with a header
  comment naming the date and that it baselines the post-5a state (the 5a
  session's temporary baseline did not survive; acceptance must be able to
  re-run the check). Test: file parses, names six existing files.

## Deliverable 2 — the owed ADR (RECORD tail of 5a)

`knowledge/decisions/5a-census-api-and-theme-expansion.md` + INDEX line.
Contents, with numbers: (1) ratification of the 5a census deviation — the
brief's "poll payload already on disk" premise was false (ten keys, measured),
census re-read ids via the free API, $0 held, 16/16 byte-identical control;
(2) the coverage finding — three themes close 6.8% / 3.6% of the 10 M gap;
(3) the operator ruling 2026-08-06 — five themes authorised (health/fitness
against the team-lead recommendation, priced by the ledger), coverage-target
decision deferred to the combined ledger. English, vault style.

## Deliverable 3 — discovery 5a.1 (runs only after F1)

Extend `THEMES` in `scripts/discover_channels.py` (line ~50, the printed
constant echoed into the record) with:

- `cooking_recipes`: ["рецепти", "кулінарія", "готуємо вдома", "страви",
  "випічка", "десерти", "вечеря"]
- `supermarket_deals`: ["знижки", "акції АТБ", "акції Сільпо",
  "акції Аврора", "супермаркет знижки", "економія продукти"]
- `health_fitness`: ["здоров'я", "схуднення", "фітнес", "тренування"]
- `food_quality`: ["якість продуктів", "фальсифікат",
  "експертиза продуктів", "перевірка якості",
  "безпечність харчових продуктів", "Держпродспоживслужба"]

Plus `SEED_HANDLES` (checked directly through the entry_check machinery, no
search): @recepti, @mameni_recepti, @klopotenkofood, @blwbabies,
@kopiyochka1, @epicentrk_sale, @maudau. A seed that resolves to an
already-known candidate dedups by handle.

Output `results/discovery_5a1.json`, 5a conventions: same record schema,
`found_by` theme tags per candidate, fixed 28-day window, langid mix,
liveness split, `window_truncated` marks, both caveats in the exact
PROMPT-5a ASCII bytes. Its ledger is the COMBINED reading: registry four +
the union of 5a and 5a.1 candidates deduped by handle — plus a per-theme
subtotal table (subscribers, live count, with-discussion-group count) so the
operator can price each theme, health_fitness explicitly included. The old
themes are NOT re-scanned; their rows come from `results/discovery_5a.json`.

FloodWait policy stays per script and named: discovery aborts-and-keeps
(entry_check pattern, now via F1); nothing blends policies.

## DO NOT

- Edit docs/STATUS.md, docs/SPEC.md, docs/PROMPT-*.md,
  docs/RESEARCH-*.md — team-lead files (File ownership). Committing them in
  step 0 is required; editing them is forbidden.
- Touch raw v1 stores (`data/raw/posts|comments`) — read-only; the census
  sidecar F5 edit touches `results/`, not the sidecar itself.
- Change `config/registry.yaml`. Candidates only; entry is the operator's.
- Any paid API, any model call, any serving work, any loop change beyond F4.
- No live collection pass — still 5c, own store root.

## Verify-gate (evidence, not assertions — paste commands and output)

1. `make check` green (new tests included; state the new total).
2. `ruff format --check .` clean.
3. `shasum -c results/raw_v1_baseline.sha256` → 6/6 OK, run AFTER the scan.
4. `git status` clean at the end; commits atomic, by path.
5. Report numbers point at artifact paths (`results/discovery_5a1.json`,
   the updated census record) — no numbers that live only in prose.

`implementation-notes.md` gets a "Phase 5a.1" section with a **Deviations**
heading — every departure from this brief is logged there and cited in the
report; silence is not compliance. Report ends with: per-theme subtotal
table, the combined gap number, and the three cheapest operator readings of
it (including "launch registry-only" — the menu must contain the no-add
option).
