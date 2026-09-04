---
type: decision
date: 2026-09-04
tags: [decision, collection, registry]
---

# The invite hash is resolved at the call site, not in the registry

**Decision.** `scripts/collect_r2.py` gains `resolvable(handle)`, which hands
`get_entity` the spelling `t.me/+<hash>` when the registry handle starts with `+`.
The registry row does not move, and the store is not re-keyed.

## The problem

`marketopt_private` is a private channel with no username, so its registry handle IS
its invite hash, `+Ejz6ubzm21IyMTQy`. Telethon's `utils.parse_username` recognises the
`+` form only AFTER a `t.me/`:

- `parse_username('+Ejz6ubzm21IyMTQy')` → `(None, False)`
- `parse_username('t.me/+Ejz6ubzm21IyMTQy')` → `('Ejz6ubzm21IyMTQy', True)`

The bare spelling then falls through to a session lookup that misses, and
`collect_r2.py:377`'s `except Exception` swallowed the `ValueError` into a silent zero
row. The account has been a member since 30.08 (`results/joins_5c1.jsonl:33`,
`already_member`), so five days of «joined but uncollected» were this one defect and
nothing else. `knowledge/hot.md`'s «инвайт-хэш неадресуем» was true of every call site
in the repo, not of the entity.

## The two rejected branches

1. **Change the registry row** to `t.me/+…` or to the numeric id `1255265634`.
   Refused: `config/registry.yaml` is PINNED (PHASE §4) and its live bytes `eff8ba5b…`
   are one of ten `prereg_promo_c2.json :: pinned_inputs`; `registry._HANDLE` and
   `tests/test_registry.py` also pin the accepted handle shapes.
2. **Collect under the numeric id.** Refused: `handle` is the store key
   (`data/raw_r2/posts/<handle>.jsonl`) and the segment key `build_aggregates.segment_for`
   joins on. A channel collected under a second spelling is a second channel to every
   reader downstream.

## Consequence

Only the RESOLVE ARGUMENT is rewritten; `handle` stays the registry spelling everywhere
else. The `--comments` branch still passes the bare handle — dead today only because
`marketopt_private` has `comments_enabled: false`, and named as a debt in PROGRESS.

See [[2026-09-04]], [[a_collection_moves_every_anchor_computed_from_the_store]].
