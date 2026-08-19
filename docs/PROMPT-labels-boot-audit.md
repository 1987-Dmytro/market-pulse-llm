# PROMPT — labels-boot-audit: the suite goes green in the commit that seals the labels, and the census learns the loader's axis

**Two operator rulings, 19.08 (docs/STATUS.md, «День 19.08»): (1) the two
pass1-data-prep tests that assert `docs/labels-pass1-r1.jsonl` does not exist
flip IN THE SAME COMMIT that commits the labels verbatim — a fresh clone must
never see the file without the tests that seal it; (2) the ≤9K boot-tax target
is SUSPENDED pending re-registration at a joint operator sitting — this
contract fixes the census AXIS (Dv526) and prepares the audit; it does NOT cut
hot.md and does NOT touch `TARGET_KTOK`. $0, no cloud call.**

**Baseline (team lead's runs, timestamps attached; quoted figures may drift
under you — the regime is MEASURE AND NAME, never silently fix):**

- `make check` is RED and registered so: 2 957 passed / 2 failed / 2 skipped
  (passed+failed = the registered 2 959; vault-dream Dv531). The two failures
  are exactly the tests this contract flips. Re-confirmed 19.08 morning by a
  targeted run of both files (2 failed / 30 passed).
- `docs/labels-pass1-r1.jsonl`: 500 lines; validator exit 0 (team lead's run,
  18.08 night); distribution не_наш_рынок 251 · null 167 · сеть_ритейлер 44 ·
  категория_личное 36 · молочный_бренд 2 (251+167+44+36+2 = 500 — re-derive
  as your step-1 refusal gate, H6).
- `git status --porcelain` at issue time (19.08, after the 10:57 SessionStart
  refresh): M docs/STATUS.md · M knowledge/daily_logs/2026-08-18.md ·
  M knowledge/hot.md · M knowledge/index.md · ?? docs/labels-pass1-r1.jsonl ·
  ?? knowledge/daily_logs/2026-08-19.md — plus, once written, ?? this PROMPT
  file. The vault paths drift by design
  (SessionStart/Stop hooks) — re-read at your step 0; their drift is not a
  deviation.

## Step 0 — the tail (checked against the live porcelain at YOUR start)

1. Vault tail, its own commit: `knowledge/daily_logs/2026-08-18.md`,
   `knowledge/daily_logs/2026-08-19.md`, `knowledge/index.md`.
   `knowledge/hot.md` is NOT in this commit — its two edits are this
   contract's own deliverable (D3) and ride with that commit.
2. Team-lead files, verbatim, their own commit: `docs/STATUS.md` (vault-dream
   accepted, both rulings registered) and `docs/PROMPT-labels-boot-audit.md`
   (this contract). A path in the porcelain that neither list explains: STOP
   and report.

## D1 — the sealing commit (ruling 1: ONE commit, atomic)

Everything below lands in a SINGLE commit, staged by explicit path; `make
check` is green from this commit on:

- **The labels, verbatim.** `shasum -a 256 docs/labels-pass1-r1.jsonl` BEFORE
  staging and after committing — printed, equal. You never edit this file.
- **The freeze**: copy to `results/labels_pass1_r1.jsonl`, byte-identical
  (sha equality asserted by a test, not by prose), plus a provenance sidecar
  `results/labels_pass1_r1_provenance.json`: labelled_by team lead · date
  2026-08-18 · codebook = attribution law v5 + F2a carve-out + gold-r2
  rulings (`docs/label-pack-pass1-r1.md`) · pack
  `results/pass1_label_pack_r1.json` · seed 20260818 · the distribution ·
  sha256 of the jsonl · the ablation duty (training data, ablate
  with/without — honesty frame §2, STATUS). **The sidecar doubles as the
  PIN**: shape its sha fields the way `scripts/preflight.py` parses pins
  (open it and match the existing `results/*.json` pin shape), so
  `make preflight ARGS='labels-pass1-r1'` shows the labels file pinned and
  its digest matching.
- **The flip, minimal diff.** `test_the_pack_names_who_writes_the_labels`
  (tests/test_pass1_label_pack.py): the two record asserts stand; the
  `not (...).exists()` line becomes `exists()`.
  `test_the_domain_is_the_prompt_s_and_the_real_labels_file_does_not_exist`
  (tests/test_validate_pass1_labels.py): the domain asserts stand; the test is
  RENAMED to say what it now guards (a test name that asserts the opposite of
  its body is the defect we are removing), and the seal lands here or beside
  it: `gate.LABELS` exists · 500 rows · the distribution above · the sha256
  pin — the guard that fails if the file ever drifts — · and the validator's
  green path driven on the REAL file (`gate.main([str(gate.LABELS), "--pack",
  str(gate.PACK)])`), not only on synthetics. The red-first refusal tests
  already cover the other direction; do not weaken them.

## D2 — the census axis (Dv526; `scripts/context-census.py`)

- Today `MEMORY.md` is counted as `min(st_size, 25*1024)` UTF-8 bytes. The
  loader counts differently: trim → cap 200 LINES → cap 25 000 UTF-16 code
  units, cut at the last `\n` under the cap — constants and semantics
  re-derived in `docs/reports/vault-dream.md` («Step 1 — the constants»);
  re-derive them from that section as your refusal gate. Replace the flat
  byte cap with a loaded-size function that models the loader, and count ITS
  result toward the census.
- **A moved constant ships with the guard that fails if it moves back**: a
  test driving the new function on synthetic content over BOTH caps (lines
  and units) asserting the truncation semantics, and pinning 200 / 25 000.
- `TARGET_KTOK = 9.0` and the warning line DO NOT change (ruling 2: the
  target is suspended, not moved; STATUS says how to read the warning).
- Census output pasted before and after the fix. Expected delta ≈ 0 (the file
  is under both caps today) — a larger move is a finding: name it.

## D3 — the record and the audit prep (rulings become ADRs; hot.md: two edits)

- **Two ADRs** in `knowledge/decisions/` + INDEX: (1) ruling 1 — a test that
  asserts a planned artifact's ABSENCE is a clock, not a verifier: it expires
  the moment the plan executes, and its flip belongs in the commit that lands
  the artifact [[a_green_suite_can_have_a_shelf_life]]; (2) ruling 2 — the
  ≤9K target suspended: hot.md is not cut to hit a number; the census axis
  becomes the loader's; the target is re-registered from the measured
  high-signal floor at a joint sitting — quote the reachability inequality
  from `docs/reports/vault-dream.md` with its numbers.
- **The audit prep is a TABLE in your report, not an edit**: every block of
  `knowledge/hot.md` — bytes · hot (live state: blockers, Next, sealed) or
  cold-candidate (its durable home named) — so the sitting starts from a
  table. Same one-line treatment for the three CLAUDE.md (19.08 figures to
  re-measure: ./ 6 999 B · ~/.claude/ 1 974 B · ~/ 350 B): which sections
  could move to `paths:`-scoped rules or on-demand homes. Classify; do not
  recommend evictions — what leaves is the sitting's decision.
- **`knowledge/hot.md`, exactly two edits, committed with this step:** the
  red-suite blocker CLOSES (green as of the sealing commit — name its sha);
  the boot-tax blocker's open half becomes the ruling (target suspended,
  audit prepared, joint sitting pending). Sealed AUTO-GEN markers byte-intact;
  the `~$0.24/day` literal untouched.

## Verify (paste outputs, `python3.11` throughout)

```
make check                            # RED before (the registered two), GREEN after D1 and at the end; name the final count (2 959 + your new guards)
PYTHONPATH=src python3.11 scripts/validate_pass1_labels.py docs/labels-pass1-r1.jsonl   # exit 0, distribution printed
shasum -a 256 docs/labels-pass1-r1.jsonl results/labels_pass1_r1.jsonl                  # equal
python3.11 scripts/context-census.py  # before and after D2
make preflight ARGS='labels-pass1-r1' # the labels file pinned, digests match
python3.11 scripts/check-wikilinks.py # 0 broken, including the ADRs' [[...]]
git status --porcelain                # only the Stop-hook tail may remain; name it
```

## Report

`docs/reports/labels-boot-audit.md`, path-only in chat. Deviations from
**Dv532**, cause tags from the CLOSED enum v2 only
(`contract-gap | spec-gap | verify-gap | env | tooling | model | process`),
lesson names as trailing `[[wiki-name]]`. Five-line Process signals. Read back
FIRST, one line each: the atomicity of the sealing commit; what may not change
in the census (`TARGET_KTOK`, the warning); the audit prep is a table, not an
edit; the pin duty for the frozen labels; the two-edits-only rule for hot.md.

## DO NOT

- Never EDIT `docs/labels-pass1-r1.jsonl` — commit byte-for-byte, sha proven
  before and after. It is a team-lead file (pass1-data-prep, File ownership).
- Never touch `docs/label-pack-pass1-r1.md`, `docs/label-pack-pass1-r1-blind40.md`,
  `scripts/build_pass1_label_pack.py`, `results/pass1_label_pack_r1.json` —
  pinned by sealed records (preflight 19.08: 3/3 digests match; keep it so).
- `TARGET_KTOK` and the census warning text stay; `knowledge/hot.md` content
  is not cut (the two named blocker edits are the only edits); `MEMORY.md`
  is not touched.
- Team-lead files (docs/STATUS.md, docs/SPEC.md, docs/PROMPT-*): commit
  verbatim, never edit. Never `git add -A`. No cloud calls, no money, no
  frozen records, no gold, no prompt files.
