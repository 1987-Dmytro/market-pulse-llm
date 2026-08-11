# PROMPT-uni-b — the vocabulary law, the attribute field, one re-registration ($0)

Issued 2026-08-11 (team-lead file — read and commit, never edit). Operator ruling
11.08, made AFTER the cost briefing: land all three universality moves NOW, one
phase, before sku-b. The moves share pinned surfaces, so they land as ONE ceremony,
in the order below. No paid calls. sku-b shifts by one phase.

**Read-back check (first lines of your report):** step 0, deliverables A–D in
order, the DO-NOT list, and the four byte-identity guarantees (prompts.py ·
registry.yaml · the draft lexicon · text30.csv) — one line each.

**Method (operator's ask, verified against Claude Code docs):** there is NO native
/refactor. Enable `pyright-lsp@claude-plugins-official` for this session; after
every rename use `lsp_find_references` to prove zero stale references (cite the
counts in the report); run `make check` after EACH deliverable, not once at the
end. Plan the edits before touching disk. Smallest working diff (ponytail).

**Report:** `docs/reports/uni-b.md`, own commit `docs(report): uni-b`, chat gets
the path. Deviations continue at **Dv125**.

## Step 0

Commit the standing vault tail if dirty (own commit); this brief + the STATUS
block arrive from the team lead — commit unedited, staged by path.

## Deliverable A — config/lexicon.yaml, the vocabulary law

Byte-faithful migration of `data/category_lexicon_draft.json`: the 14+2 tracked
stems, the endings table, PLUS a new `units` section absorbing
`positions.SIZE_PRICE_UNITS` (L6). Loader beside `Taxonomy` (smallest diff —
`registry.py` or a small `lexicon.py`). `yield_screen.compile_categories` and the
pre-filter path read the LAW file. The draft file is NOT edited and NOT deleted —
five sealed records pin its sha `1225ad75…`; the law file's header names it as
source with that sha. Guards, both loud: law stems must be prefixes of registry
display names (build_lexicon's rule, now on the law); a one-time migration test:
law content == draft content at this commit.

## Deliverable B — fat → attribute, wire-compatible

Schema level only: `Position` field, `PRESENCE_FIELDS`, `tier_from_presence`
kwargs, ladder labels — fat → attribute. `ladder_sha256()` changes BY DESIGN.

WIRE COMPATIBILITY IS LAW: registered prompt texts are not touched — the dairy
instruments emit the JSON key `"fat"`, and the parser maps wire key → schema field
per instrument family (a small alias table beside the parser; smallest diff).
`data/annotation/sku_a_text/text30.csv` is NOT touched: header keeps `fat`,
`given_sha256` stays byte-identical (`448d8d20…` over given columns, file sha
`d0945b91…` may NOT move); the validator maps the column. The pack manifest
`results/sku_text_pack_manifest.json` is REBUILT (its ladder sha moves); ids,
`given_sha256` and the README sha must come out unchanged. Every rename site
verified by `lsp_find_references`.

## Deliverable C — L2–L5 de-literal, loud not silent

- L2 `theme_screen_5c1.py::TRACKED` and L3 `measure_categories.coverage()`'s local
  `tracked`: read the tracked groups from `load_registry()`; an empty intersection
  is a LOUD refusal (SystemExit / `ok: false`), never a silent zero.
- L4 `entry_check.PRE_REGISTERED_FLAGS`: the keys stay (a transcribed 5c1 ruling —
  provenance); add a loud guard: flag keys not in the current composition → the
  verdict record carries `flags_unmatched` with the list.
- L5 `prompts.SENDER_CONTEXT`: prompts.py is UNDER DO-NOT and stays byte-identical.
  The cleanup is a GUARD, not an edit: a test asserting the closed task
  (`precheck_v2ctx_with_post`) is in no live task list, plus one PORTING.md line.
- L6 is closed by deliverable A (units in the law file).

## Deliverable D — the re-registration ceremony, in this order

(1) **SPEC 3.17 (8)** — the verbatim team-lead block below, same strip-marker
mechanism as (7); evolve the strip to remove ALL marked ratification blocks before
hashing; the stripped sha must still equal `973c87890ad049d5…`. One green commit
with the test evolution, as d3bf781 did.

```
<!-- sku-b-ratification-2 begin — stripped by tests/test_sku_prereg.py before
hashing docs/SPEC.md against the prereg pin; the registered law is the stripped text -->
(8) **Vocabulary law and the attribute field — ratified (operator, 2026-08-11).**
The pre-filter's category vocabulary is law in config/lexicon.yaml (source:
data/category_lexicon_draft.json sha 1225ad75…, migrated byte-faithfully; the
draft stays frozen as history). The position schema's fifth presence field is
generalized fat → attribute; dairy instruments keep the wire key "fat" — the
registered prompt texts are unchanged. The pilot's pre-registration is
re-registered beside as results/sku_pilot_prereg_v2.json BEFORE any attempt:
thresholds, the $0.35 cap, the one-attempt clause and the R1–R5 readings are
verbatim-unchanged; only schema naming and vocabulary provenance moved. Bar 3's
ladder sha follows the renamed table.
<!-- sku-b-ratification-2 end -->
```

(2) **results/sku_pilot_prereg_v2.json** BESIDE v1: bars, thresholds, cap,
attempts, R1–R5 readings — VERBATIM from v1 (byte-equal strings, tested). New
pins: ladder sha (new), `config/lexicon.yaml` sha (new), rebuilt manifest sha,
prompts shas (UNCHANGED — asserted), registry sha `920c7f20…` (unchanged), the
stripped SPEC pin. A `supersedes` block names v1's sha `b1bfa40d…` and the
reason: "schema rename + vocabulary law; before any attempt; no bar moved." v1
is NOT edited; it freezes under a sealed-content test (the c82d0cff pattern),
and the LIVE pin-test migrates to v2.

(3) `scripts/write_sku_prereg.py` now writes v2 (`registered_law` strips both
blocks); the negative control (a reworded bar refuses) must still fire.

(4) **Regression proof:** re-run the probe → `results/uni_probe_v2.json` BESIDE
uni-a's artifact (which is a dated measurement and is not overwritten). Step 2
must now read follows-registry(law); steps 1/3/4 stay green under the renamed
field; step 5 unchanged (prompts are instances by design).

## Verify (evidence, not assertions)

`make check` green after EACH deliverable — four numbers in the report. Byte
identity proven by sha: `src/market_pulse/prompts.py` (all 16 PROMPTS shas,
`positions_post_gm4` `ca6303c157d4…` and `positions_text_gm4` `7250b87aa1c2…`
named), `config/registry.yaml` `920c7f20…`, `data/category_lexicon_draft.json`
`1225ad75…`, `data/annotation/sku_a_text/text30.csv` `d0945b91…`, v1 prereg
`b1bfa40d…`. `lsp_find_references` zero-stale evidence per renamed symbol.
Probe v2 verdicts. Manifest rebuild: ids + given_sha + README sha unchanged,
ladder sha new. Wikilinks green. Dv125+. Report at `docs/reports/uni-b.md`.

## DO NOT

- `src/market_pulse/prompts.py`, `config/registry.yaml`,
  `data/category_lexicon_draft.json`, `data/annotation/sku_a_text/text30.csv`,
  `results/sku_pilot_prereg.json` (v1), `results/uni_probe.json`, the sealed
  records, `results/sku_reference_leaflet.json`, `results/sku_prefilter_census.json`
  — byte-identical, proven by sha in the report. (Goal: the ceremony re-registers
  BESIDE; it never rewrites what was registered.)
- No edits to team-lead files beyond committing them; SPEC — nothing beyond the
  exact (8) block at the marked place.
- No paid calls; no new MCP servers; no scripts beyond the edits named here.

**Recovery:** a deliverable that cannot go green is reverted whole (its commits),
and the phase STOPS with the failing diff in the report — a red pin or a moved
byte-identity sha is never committed. The goal of every prohibition here: what
was registered stays readable and re-derivable at every commit.

**Operator budget at acceptance:** ~15 min — sign-off on prereg v2 (the (8)
ruling is already his) + the report.
