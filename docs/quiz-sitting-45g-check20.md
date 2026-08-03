# Control twenty ON the team lead — blind operator spot-check (2026-08-03)

Pre-registered in Amendment 2, docs/quiz-sitting-45g-log.md. New team-lead
session administered this check WITHOUT reading: precheck300.csv, the log
below line 22, or the sitting manifests (handoff blindness rule).

- Frame: precheck300.csv rows with verdict==correct AND notes=='tl-llm'.
- Sampling: random.Random(42).sample(sorted(pool, key=id), 20), then
  random.Random(42).shuffle — house convention of build_sitting_pack.py,
  pinned in chat BEFORE generation. Blind pack:
  data/annotation/sitting_45g/check20_blind.csv (no verdict/notes columns).
- Operator judges each row blind: correct only if ALL FOUR fields right
  (sentiment, sarcasm, intents, unclear). Bar: >= 18/20 confirms.
  Below bar: team-lead verdicts VOID, capture returns to operator
  (fallback registered in Amendment 2).
- Score = count of operator "correct" answers out of 20; no key needed
  (every frame row is a team-lead "correct" by construction).
- Capture: AskUserQuestion blocks of 4, pack file order, no running
  tallies shown before the file completes.

RESULT: 20/20 confirmed vs bar 18/20 — PASS (counted mechanically by
parser over this table + blind-pack id cross-check; team-lead triage
verdicts STAND per Amendment 2)

| # | id | operator | note |
|---|---|---|---|
| 1 | @VARUS_channel:1693 | correct | "все 4 верны"; operator asked why brands are absent — answered: brands are outside the four judged fields (v4/anchor step) |
| 2 | @VARUS_channel:1806 | correct | |
| 3 | @VARUS_channel:8062 | correct | |
| 4 | @VARUS_channel:18782 | correct | |
| 5 | @VARUS_channel:12279 | correct | |
| 6 | @VARUS_channel:12224 | correct | |
| 7 | @VARUS_channel:4516 | correct | |
| 8 | @VARUS_channel:12234 | correct | |
| 9 | @VARUS_channel:16953 | correct | |
| 10 | @VARUS_channel:7337 | correct | |
| 11 | @VARUS_channel:11602 | correct | |
| 12 | @VARUS_channel:8801 | correct | |
| 13 | @VARUS_channel:12286 | correct | |
| 14 | @msuaaaa:8966 | correct | |
| 15 | @VARUS_channel:11369 | correct | |
| 16 | @VARUS_channel:11664 | correct | judged in block 5 after the ordering slip |
| 17 | @VARUS_channel:13194 | correct | DEVIATION: shown in block 4 in place of pack row 16 (11664) — team-lead ordering slip; per-row capture unaffected (question carried id + full content); row 16 presented in block 5 |
| 18 | @VARUS_channel:9243 | correct | |
| 19 | @VARUS_channel:8649 | correct | |
| 20 | @VARUS_channel:9370 | correct | |
