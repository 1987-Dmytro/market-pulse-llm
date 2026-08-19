---
type: decision
date: 2026-08-19
status: accepted
tags: [decision, phase6, pass1, labels, testing, ruling, shelf-life]
---

# A test that asserts a planned artifact's ABSENCE is a clock, not a verifier

**Operator ruling 1 of 2026-08-19**, registered in `docs/STATUS.md` («День 19.08 — два рулинга») and
executed by `docs/PROMPT-labels-boot-audit.md` D1. This record is the English long form.

## What forced it

`pass1-data-prep` shipped the labelling pack together with the gate that will read the labels, and
two of its tests stated the file's absence as if it were an invariant:

| test | the line |
|---|---|
| `tests/test_pass1_label_pack.py::test_the_pack_names_who_writes_the_labels` | `assert not (REPO_ROOT / "docs" / "labels-pass1-r1.jsonl").exists()` |
| `tests/test_validate_pass1_labels.py::test_the_domain_is_the_prompt_s_and_the_real_labels_file_does_not_exist` | `assert not gate.LABELS.exists()` |

Both were green when they were written and both were true statements about that moment. The team
lead then did the work the pack exists for — 500 rows, validator exit 0, the night of 18.08 — and
the suite went red at **2 957 passed / 2 failed / 2 skipped**: the same registered 2 959, two of
them flipped, and not one line of code involved. `vault-dream` measured it and registered it rather
than fixing it (Dv531), because the file it would have had to touch was a team-lead file being
written in a parallel session.

The defect is not the assertion, it is what the assertion is ABOUT. A test that pins a state the
project's own plan is scheduled to destroy is a **clock**: it does not verify anything after the
hour it was set for, and it goes off exactly when the planned work succeeds. Its second cost is
that it manufactures pressure to loosen a neighbouring real guard, which is the older lesson this
is now the fifth instance of — cap-in-force, the derived-root snapshot, the ten-block keep,
recover-instead-of-re-pin, and now planned-absence ([[a_green_suite_can_have_a_shelf_life]],
[[5c2-closed-the-sitting-and-the-shelf-life-redesign]]).

## The ruling

**The flip lands in the SAME commit that lands the artifact.** Not before (the tests would assert a
file nobody has), not after (a fresh clone would see the file without the tests that seal it, and
`git bisect` would walk through a red window that never existed as a real state of the work).

Executed as commit **`8d2e1ba`**, staged by explicit path, carrying in one atomic change:

* `docs/labels-pass1-r1.jsonl` verbatim, sha
  `776b204f3d3aa1a193f0faad7f68198595c81963199124efca8f6b74a9e1c920` printed before staging and
  re-read out of git after committing;
* `results/labels_pass1_r1.jsonl` — the frozen copy training reads — and
  `results/labels_pass1_r1_provenance.json`, which is both the provenance the pack record left as a
  debt and the pin `scripts/preflight.py` parses;
* the two test flips, the second one RENAMED, because a test whose name asserts the opposite of its
  body is the defect being removed and not a cosmetic detail.

## What replaced the clock

An absence assertion deletes cheaply and leaves nothing behind, so the ruling required the flip to
be a net gain in coverage rather than a subtraction. What now stands where `assert not …exists()`
stood: the file EXISTS · 500 rows · the registered distribution (не_наш_рынок 251 · null 167 ·
сеть_ритейлер 44 · категория_личное 36 · молочный_бренд 2) · the sha pinned in the provenance
record and re-derived at test time · the validator's green path driven on the REAL file rather than
only on synthetics · and the freeze proven byte-identical.

The seal was checked against a single flipped label — a drift that keeps the row count at 500 and
would still pass the validator — and the digest, the distribution and the byte-identity each catch
it.

Reading a team-lead file from a test is licensed, not assumed: the green-path test asserts at the
source level that the gate holds no `write_text` and no `write_bytes`, so running it on the real
file cannot write to what it reads.

## The rule this leaves behind

When a contract writes a test about an artifact a LATER step will create:

1. State the invariant that survives the plan — who writes the file, what shape it has, what the
   gate refuses — and let that be the test.
2. If the absence itself must be asserted, the plan that ends it OWNS the flip: it is named in the
   contract that lands the artifact, and it ships in that commit.
3. A red suite caused by a planned success is registered with an owner and a decide-by, never
   merged over and never quietly relaxed.
