# PROMPT-srv-2b — volume, endpoint, D7 re-read, parity (one paid session)

**Contract:** execute `scripts/runbook_srv2b.md` §C.0–C.9 in order.
Authorization: operator go, 2026-08-08 late evening, on the srv-2a
acceptance. **Cap $4.00** — fill it into the runbook's placeholder and the
`--step srv2b` guard (`results/spend_srv2b.json`, written BEFORE the first
billable action, never regenerated). ONE attempt. The abort ladder is in
force: a rung = STOP, delete what the failed run created, prove the
deletion by LISTING, report; no rung authorises a retry, a cap raise, or a
bar edit. The volume is a run-rate line, not session spend: its price is
READ from the console at creation and recorded.

## Steps

0. Commit the pending tail unmodified (team-lead docs incl. this file; vault
   tail separately). Write the ADR for ruling 23 / SPEC amendment 3.14
   (runtime target = serverless; the probe; what stays unproven until this
   session) to `knowledge/decisions/` + INDEX, citing
   `docs/probe-serverless-20260808.md`.
1. §C.0 preflight (Mac, $0) — every check's command and output in the notes.
2. §C.1 D7 re-read → the datacenter decision, recorded with its evidence.
3. §C.2–C.3 volume + staging (recorded price; staging pod deleted after
   §C.3, deletion proven by listing).
4. §C.4–C.6 endpoint, smoke, D7 record.
5. §C.7–C.8 parity 758 rows batch 1 vs `results/parity_5b_a.json` under
   3.11 (2); the cost reading vs the pod's $0.60/1000.
6. §C.9 close; report: per-head verdicts read FROM the result artifacts
   (name their paths — numbers never travel as prose), D7 record, volume
   price, spend from the anchor, Deviations, STOP.

**Do NOT:** edit team-lead files (docs/STATUS.md, docs/SPEC.md,
docs/PROMPT-*); touch Telegram; merge the adapter; run batch >1 anywhere;
`git add -A`.
