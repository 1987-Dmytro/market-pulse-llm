# Dumps a record names and this repository cannot back

A per-row dump is what makes a run re-scorable at $0 when gold is later corrected —
`knowledge/decisions/test-v3.md` §(c) names the eight runs that have none and says plainly that
they "cannot be re-scored at any price". This file is the ledger of dumps that *were* written and
then lost, so the gap is a recorded fact rather than a missing file nobody notices.

Nothing here may be regenerated. A re-run would be a different run under the same name, and every
arm in this project is scored exactly once.

| record | path it names | sha256 | how it was lost |
|---|---|---|---|
| `google/gemma-4-31b-it` @ `2026-08-04T18:54:42+00:00` — 4.5h2 arm `without-plast` | `results/predictions/google-gemma-4-31b-it--20260804T185442Z.jsonl` | `bfaafc7dc7663315310e02a417f5051643ed08f78cce468de94c50950228af46` | The fetch was issued in a compound command whose first `scp` failed on an unquoted option string; the `&&` chain stopped before the dump, the failure scrolled past under a `2>/dev/null`, and the volume-less pod was deleted about twenty minutes later. Nothing else from that session was lost: the adapter, the loss curve, the training provenance, the eval log and the gate record are all committed, and the adapter's sha256 was verified against the record on the Mac. |

## What the loss does and does not cost

- **It does not touch a single gate number.** Every value the 4.5h2 verdict reads is in
  `results/baselines.json`, and the `scored_ids_sha256` of all three inputs is recorded, so *which
  rows* were scored is still provable.
- **It does cost the re-score.** If gold is ever corrected again the way 4.5a corrected it, arm
  `without-plast` cannot be re-measured against the new gold and arm `with-plast` can — so any
  future v5 comparison of the two arms would be **unpaired**, and must say so rather than quietly
  compare one re-scored column against one stale one.
- **The verified thing is the adapter, not the dump.** The runbook's step-7 hash check is what
  caught a stale `/tmp/arm-a-record.json` from Phase 4 in the same minutes; it says nothing about
  the dump, and now the runbook fetches and *verifies* the dump before the pod is deleted.
