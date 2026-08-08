# PROMPT-srv-2d — parity on the live endpoint (THE one attempt, cap $2.00)

**Contract:** operator go 2026-08-08 night, on the documented scheme. This
session SPENDS the single 3.11 (2) parity attempt — no retry under any
outcome; a failed gate is a finding, reported with both readings. Abort
ladder of `scripts/runbook_srv2b.md` in force. Own anchor
`results/spend_srv2d.json`, cap **$2.00**, written before the first
billable action.

**Normative docs — READ both before anything billable; they are the spec
for every setting this session touches:**
- https://docs.runpod.io/serverless/endpoints/endpoint-configurations.md
  (execution timeout default 600s and its per-request override; TTL timer
  starts at SUBMISSION; async /run results deleted after 30 min; GPU
  priority; FlashBoot default)
- https://docs.runpod.io/serverless/troubleshooting.md (SDK 1.7.11–1.10.0
  network-volume job-tracking bug; "logs only appear for successfully
  initialized workers"; logs-to-volume as the recommended durable channel)

## Steps

0. Commit the pending tail. $0 code first, each with a test:
   (a) worker boot assert `runpod>=1.10.1` (the documented network-volume
   bug); (b) the parity task writes its PER-ROW dump onto the volume — the
   API reply carries only the summary (30-min retention; LOST.md never
   again); (c) runbook edits: redirect standing, the
   `{"executionTimeout": 3600, "ttl": 7200}` policy lines, the idle
   scale-down note (3/7 days), the SDK assert line.

1. Endpoint per runbook §C.4: **ADA_24 PINNED, no fallback list** — a
   measurement does not mix cards; documented fallback priorities are for
   the production loop, later, by their own briefing. Max workers 1, queue
   mode, volume `qw4nwleanc`, redirect wrap standing.
2. Smoke: the 8-row carve job (as srv-2c) — green before the attempt.
3. **Parity — the ONE attempt.** A single `/run` job: the 758-row v4 pass,
   batch 1 per forward (the same per-row compute path the smoke ran),
   request policy `{"executionTimeout": 3600, "ttl": 7200}`. Per-row dump
   lands on the volume; fetch `/status` immediately on completion (30-min
   retention window). Score against `results/parity_5b_a.json` under
   3.11 (2): every 4.5h2-passed gate stays passing, no head drops > 0.005.
   Write `results/parity_srv2.json`; copy the row dump into
   `results/predictions/`.
4. Cost reading vs the pod's $0.60/1000: measured seconds × measured $/s,
   with the Dv33 caveat named (a closing balance figure is a lower bound).
5. Cleanup: endpoint deleted, proven by listing; the volume stays. Report:
   per-head verdicts read FROM the artifact paths (numbers never travel as
   prose), spend from the anchor, Deviations, STOP.

**Do NOT:** edit team-lead files (docs/STATUS.md, docs/SPEC.md,
docs/PROMPT-*); touch bars, the adapter, or the gold set; submit a second
parity job under ANY outcome; `git add -A`.
