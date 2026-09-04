---
type: decision
date: 2026-09-04
status: accepted
tags: [decision, promo-pulse-1, s10, s11, seals, registry]
---

# A file 21 seals pin does not grow — the new key gets a sibling file (ruling 04.09 (g), option b)

**Team lead's ruling, taken on the executor's stop and implemented the same day.** Ruling 03.09 (f)
A(1) said `config/registry.yaml` gains `admin_anon_ids` per collected channel. Session 10 stopped
BEFORE the first edit and priced three branches; ruling (g) chose (b) — the ids live outside the
registry. Built in session 11 as `c7a63a7` and accepted by diff the same day (ruling 04.09 (h) item 1).
Related:
[[5c2-closed-the-sitting-and-the-shelf-life-redesign]], [[the-law-grows-inside-marked-blocks]].

## Why the registry cannot take the key

`config/registry.yaml` is pinned by **21 sealed records** in four sha families, counted in
`results/`: r1 `d4e3b237…` (7) · pre-SPEC-3.17-(13)(b) `920c7f20…` (8) · signed-screen `c82d0cff…`
(5, rebuilt only inside `tests/test_registry.py`) · LIVE bytes `eff8ba5b…` (1,
`results/prereg_promo_c2.json`, via the 02.09 (d) addendum).

The two rows the ruling names — `@VARUS_channel` (`:36`) and `@msuaaaa` (`:45`) — are **r1-era rows,
outside the r2 bracket**, so any line added to them lands in EVERY reconstruction, not just the
newest. Driven, not reasoned: `run_promo_c2.preflight` passes at HEAD and refuses after ONE added
line, and `build_aggregates.py:294` reaches the C2 seal from `tests/test_export_dashboard_data.py`,
so `make check` — session A's own exit condition — goes red.

**A fourth revision is not enough.** `R3_MARK` + `registry_before_r3` under `registry_before_r2`
restores all four families exactly, and that preflight (`:523-535`, live at `:979`) compares RAW
BYTES and walks no revisions. Its own writer left the rule in the file: «If the registry moved, that
is a refusal for the team lead, not a rewrite here.» A revision chain saves the readers that walk
revisions and never the guard that hashes the file.

## What was decided and built

1. **(b)** — `config/channel_admins.yaml`, a new file with one reader (`promo_prompts.admin_ids`).
   No pin moves, no revision r3, no preflight change. The two ids were resolved from the store, not
   typed from the codebook: each prefix the codebook names (`2fa2b7…`, `58805a…`) matches exactly
   ONE `sender_anon_id` across all of `data/raw/comments/`, in exactly one channel.
2. The render DROPS wordless comments (`text.strip()==""`) — outside the queue (SPEC 3.19), outside
   the gold, and a blank `[admin]` line would be content nobody labelled. 68 of the 208 dev-40
   comments; the count equals the draw's own summed `n_wordless`.
3. `[admin] ` is prefixed by the SENDER'S ID, never by the text, so the 28 VARUS comments with
   `sender_anon_id: null` get nothing. 23 markers over the 40 threads = the 23 admin comments that
   carry text (82 admin comments − 59 wordless).
4. The flag rides IN the pack: `comments` entries became `[msg_id, text, sender_anon_id]`, because
   the pod re-renders from those rows and nothing else. The pod names the columns rather than
   unpacking them, so a pack written before this ruling still renders.
5. C2 collection stays OPEN — option (c) was not taken.

## What it does not close

`config/channel_admins.yaml` is an UNPINNED input to `rendering_sha256`. That is covered, not by a
record, but by the consumer: the pod re-renders every unit on its own checkout and compares, so a
divergent config refuses the unit instead of rendering something else — demonstrated by pointing the
module at a divergent file (56/56 accepted before, refused at `@VARUS_channel:2537` after).
`check_law` still compares `codebook_version` alone, and A(1) did not move `CODEBOOK`; only ruling
(g)3's `template_sha256`, at session B's re-emitted registration, will separate the v1 instrument
from the v1.1 one in a record. @kopiyochka1 has such an account too and is deliberately NOT in the
file: outside dev-40, outside the ruling, and its source carries two handles for one id.
