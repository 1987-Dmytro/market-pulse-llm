# PROMPT-sku-miss-pack — the 29 missed gold pairs, packed for the team-lead read ($0)

> Light contract (the 12.08 regime): one deliverable, no report file —
> the pack IS the deliverable; a five-line summary in chat is fine.
> $0, local, no paid calls. Purpose: decompose bar 1's 29 misses into
> (a) brand printed WITH a price box → a real under-read, (b) brand
> visible WITHOUT a price box → bar-vs-instrument mismatch, (c) brand
> not visible on the sent pages at all → gold noise. The verdicts are
> the team lead's, from the images; this contract only lays the table.

## Deliverable

`scripts/build_sku_miss_pack.py` → `results/sku_miss_pack.json` +
a read-sheet `results/sku_miss_pack.md` (grouped by post, for reading
images beside it):

- Recompute bar 1's per-post found/missed via the SAME scorer route
  the verdict record used (`gold_key` on both halves — never a new
  matching rule). Assert: missed pairs = **29**, found = 26, over the
  15 scoreable posts.
- Per missed pair: the post id; the gold key and the DISPLAY name(s)
  behind it (from `results/sku_reference_leaflet.json`
  watchlist_hits / other_dairy_brands as the reviewer wrote them);
  the post's SENT pages in order (file, sha256); per page what the
  instrument answered — positions extracted (brand_raw list) or `[]`
  or unreadable-by-reason (from the merged v4 artifacts).
- Per FOUND pair (compactly): post, key, the page(s) whose positions
  carried it — the control half, so the read-sheet shows both.
- The read-sheet ends with an empty verdict template: one line per
  missed pair, `a | b | c` to be dictated by the team lead.

Tests: the 29/26 checksums, one hand-checked post, refusal on a gold
or record sha that moved. `make check` green. Deviations **Dv188+**
(in chat, one line each — no report file this time). Do NOT: no paid
calls; no edits to team-lead files, sealed artifacts, registrations;
never `git add -A`; vault tail → its own commit.
