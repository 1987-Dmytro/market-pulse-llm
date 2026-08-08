# PROMPT-srv-2c — the boot-log diagnostic: where does our worker die? (cap $0.75)

**Contract:** operator go, 2026-08-08 night, on the srv-2b abort acceptance.
ONE question: does `bash /runpod-volume/start.sh` execute as the worker's
main process — and if yes, where does it stop before its first print? The
3.11 (2) parity attempt is NOT touched (test v4 stays closed). The abort
ladder of `scripts/runbook_srv2b.md` is in force: a rung = STOP, delete,
prove by listing, report; no retries. Own spend anchor
`results/spend_srv2c.json`, cap **$0.75**, written before the first
billable action. Step 0 also re-lists serverless endpoints ($0) — the
console would not render for either side at srv-2b close.

## Steps

0. Commit the pending tail. $0 code first: fix the spend guard's serverless
   blindness (billing_since walks only pods and volumes; srv-2b undercounted
   $0.86) + a test that pins the fix. Free re-listing: pods, endpoints.
1. Recreate the minimal endpoint per runbook §C.4 with ONE change — the
   template's start command wraps all output onto the volume:
   `bash -c 'exec bash /runpod-volume/start.sh > /runpod-volume/worker-boot.log 2>&1'`
   ADA_24 + volume `qw4nwleanc`, queue mode, max workers 1.
2. ONE job. Observe ≤10 minutes (job status · worker state · console logs).
   The signal is the log FILE, not the job — a completing job would be a
   welcome surprise and is recorded as one. Delete the endpoint; listing.
3. Cheapest §C.3-style pod in EU-RO-1 with the volume: read
   `/runpod-volume/worker-boot.log` VERBATIM into
   `results/srv2c_bootlog.json` (plus `ls -la` of the volume root, start.sh
   perms, venv presence); refresh the volume's stale repo checkout to
   current main and update the manifest; delete the pod; listing.
4. Report: the verbatim log (absence = the start command never ran), the
   file listing, ranked hypotheses, spend from the anchor, Deviations,
   STOP. No fixes beyond the guard code — the fix decision is the
   operator's briefing.

**Do NOT:** edit team-lead files; open test v4; touch the adapter or bars;
retry any rung; `git add -A`.
