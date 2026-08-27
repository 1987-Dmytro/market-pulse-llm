# PROMPT — `lora-c-close` (micro, fresh session, $0, Dv from 781)

One mechanical deliverable: the team lead wrote SPEC **amendment 3.26** (the marked block after
3.25 — the operator's max_seq_len 3072 ruling) and the block is not yet in the strip registry, so
`tests/test_sku_prereg.py::test_every_pinned_input_still_hashes_to_what_it_says` is RED on the
working tree. Give `amendment-3.26` the SAME landing manoeuvre `amendment-3.25` received in the
`lora-c-apply` session (Dv776 called it four tests' worth):

1. `git log -p --all -S "amendment-3.25" -- scripts tests | head -80` — find every place the
   3.25 landing touched (the block registry at `scripts/write_prereg_5c2.py` ~line 100 and any
   test/sibling list that enumerates the blocks). Mirror each touch for `amendment-3.26`.
   Nothing else changes: old pins predate 3.26, stripping removes it, so no registered law moves
   — assert that by re-running the failing test AND the law subset.
2. `make check` to full green on a stable tree; paste the tail.
3. Commits: (a) the team-lead files verbatim, staged by path — `docs/SPEC.md` (3.26),
   `docs/STATUS.md` (day 23), `docs/PROMPT-lora-c-close.md`; (b) the registry fix + tests;
   (c) the vault tail. Never `-A`.
4. Report `docs/reports/lora-c-close.md` — short: the grep that found the touches, the diff, the
   green tail, Deviations from Dv781 with cause tags (enum v2), one-line Process signals.

**DO NOT:** touch anything beyond the block-registry manoeuvre and the commits above; no pods;
no edits to team-lead files (commit only); no re-pinning of any sealed record.
