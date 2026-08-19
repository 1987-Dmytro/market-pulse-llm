---
paths:
  - "src/**/*.py"
  - "tests/**/*.py"
---
# Code map — what each module is for

Moved out of `CLAUDE.md` on 2026-08-19 by `boot-debloat` (the joint sitting's group D),
verbatim: still true, and needed only by a session that opens the files below.

Which phase is live is in `knowledge/hot.md` and `docs/STATUS.md`, never here or in code comments.

- `src/market_pulse/scorer.py` — one public function per Tier-1 gate, all implemented (the module
  holds zero `NotImplementedError`). `tests/test_scorer.py::test_every_public_scorer_function_has_a_hand_computed_test`
  discovers the public functions reflectively and demands a hand-computed `test_<name>_*` for each,
  so adding a public function to the module immediately puts it under the same rule.
- `src/market_pulse/registry.py` — `config/registry.yaml` → frozen `Source` / `Taxonomy` /
  `WatchlistBrand` inside a `Registry`, raising `ValueError` that names the defect (malformed
  `@handle`, duplicate id, empty channel list, unknown `source_type`, no tracked groups). Strict on
  purpose: a silently accepted typo collects nothing and only surfaces as wrong analytics much
  later. Channel handles are candidates with `verified: false` until the Phase 2 entry check.
- The target pipeline — collector → normalize/dedup/lang-id → model service → aggregation →
  dashboard, behind a source-agnostic connector interface — is specified in SPEC §5; `src/` is the
  authority on which parts are built.
