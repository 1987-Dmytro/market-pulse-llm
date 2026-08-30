---
type: decision
date: 2026-08-28
status: accepted
tags: [decision, harness]
---

# The PreToolUse guard judges behaviour, not spelling

**Decision (team lead, 2026-08-28, on the `harness-v2.1` report).** The `PreToolUse(Bash)` guard is
rewritten from a bash script matching four literal strings into
`scripts/hooks/refuse_sweeping_commands.py`, which splits the command on `&& || ; |`, strips leading
env assignments and git globals (`-C`, `-c`, `--git-dir`, `--work-tree`), and judges the first tokens
of each segment. It lands as step 0 of `retail-census-r2`; `permissions.deny` gains
`Edit(/docs/archive/**)` in the same step.

**Why — the v1 guard was measured in both directions and failed both.** v1's regexes were
`git[[:space:]]+add[[:space:]]+(-A|--all|-a|\.)([[:space:]]|$)` and
`ruff[[:space:]]+format[[:space:]]+\.([[:space:]]|$)`.

- **Under-match (Dv875), seven spellings at exit 0 against the real script:** bare `ruff format`
  (ruff's own `[FILES]... [default: .]` — the file list is byte-identical to `ruff format .`, 475
  files in this repo), `ruff format src tests scripts config`, `ruff format --check .`,
  `ruff format --no-cache .`, `git add -u`, `git add :/`, `git stage -A`, `git -C . add -A`. The
  alternation also refuses `git add -a`, which git does not accept (`error: unknown switch 'a'`) —
  the list was written from the contract's four example strings, not from git's flag set.
- **Over-match (Dv874):** the patterns matched anywhere in the command text, so a `git commit` whose
  MESSAGE quoted the refused forms was itself refused. The `harness-v2.1` commits all went through
  `git commit -F <file>` for that reason.
- **The test could not see either.** `tests/test_hooks.py::test_refuses_the_sweeps` asserted exactly
  the four strings the regex was written from; all four exit 2 and the suite is green
  ([[guard_list_closed_by_its_anchor]]).

**What the guard protects.** Repo-wide `ruff format` moves the sha of files pinned inside sealed
registrations — `scripts/write_lora_c_prereg.py` → `results/prereg_lora_c.json::producer` and
`scripts/build_lora_c_marker_census.py` → `results/lora_c_marker_census_pack.json`. `make check` runs
`ruff check`, not `ruff format --check`, so the verifier does not see the damage
([[the_formatter_voids_a_frozen_producer_pin]], [[verifier_format_gap]]). Bare `ruff format` was the
shortest unguarded spelling of exactly that.

**Acceptance test.** `pytest tests/test_hooks.py -q` — 16 refused forms, 10 accepted, bare
`ruff format` among the refused.

**Provenance.** `docs/reports/harness-v2.1.md` (Dv874, Dv875) · `implementation-notes.md`
§ «Deviations from `docs/PROMPT-harness-v2.1.md`» · draft in
`docs/reviews/2026-08-27-harness-v2.1/`. The defect was found by an adversarial re-derivation of the
executor's own work, not by the suite.
