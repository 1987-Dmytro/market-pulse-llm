# Quiz 45g — operator verdicts on the emptied-97 remedy sample (2026-08-03)

Team-lead-run chat quiz (AskUserQuestion), 20 seeded rows (seed 42; 14
restore-arm = v1 label proposed, 6 model-arm = with-post label proposed).
Pre-registered bar, declared in chat BEFORE the first block: policy
matches >= 18/20 -> apply wholesale; below -> read per arm and decide.
Escalation declared: a second twenty. Verdicts below are OPERATOR LAW for
their rows regardless of the bar.

RESULT: 11/20 matches. BAR FAILED. Per arm: restore 8/14, model 3/6.

| # | id | arm | policy | operator | match |
|---|----|-----|--------|----------|-------|
| 1 | @msuaaaa:7091 | restore | ["price"] | [] | no |
| 2 | @msuaaaa:7552 | model | ["price"] | [] | no |
| 3 | @msuaaaa:12206 | restore | ["packaging"] | ["taste"] | no |
| 4 | @msuaaaa:9385 | restore | ["price"] | ["availability"] | no |
| 5 | @VARUS_channel:10737 | model | ["availability"] | ["service"] | no |
| 6 | @VARUS_channel:12049 | restore | ["taste"] | ["taste"] | yes |
| 7 | @msuaaaa:10363 | restore | ["packaging"] | ["packaging"] | yes |
| 8 | @VARUS_channel:12430 | restore | ["taste"] | ["taste"] | yes |
| 9 | @VARUS_channel:12323 | model | ["taste"] | ["taste"] | yes |
| 10 | @VARUS_channel:11963 | restore | ["taste"] | ["taste"] | yes |
| 11 | @VARUS_channel:12271 | model | ["taste"] | ["taste"] | yes |
| 12 | @VARUS_channel:1308 | restore | ["price"] | ["service"] | no |
| 13 | @msuaaaa:13560 | restore | ["price"] | ["service"] | no |
| 14 | @VARUS_channel:12024 | restore | ["taste"] | ["taste"] | yes |
| 15 | @VARUS_channel:12062 | restore | ["taste"] | ["taste"] | yes |
| 16 | @VARUS_channel:12023 | restore | ["taste"] | ["taste"] | yes |
| 17 | @VARUS_channel:12322 | restore | ["taste"] | ["taste"] | yes |
| 18 | @VARUS_channel:10867 | model | ["availability"] | [] | no |
| 19 | @msuaaaa:11941 | restore | ["taste"] | [] | no |
| 20 | @VARUS_channel:10542 | model | ["taste"] | ["taste"] | yes |

Sentiment/sarcasm/unclear untouched — intents rulings only.

## Patterns (team-lead reading)

- The dish/filling-answer family holds: 10/11 taste proposals confirmed
  (only @msuaaaa:11941 "Вацак 🤮" — a BRAND name, not a dish — went []).
- Non-taste v1 labels on this class collapse: price proposals 0/5, of
  which 2 -> ["service"] (the v2 wide boundary reaching rows the
  re-labeller never touched) and 2 -> [] (operator stricter than v1);
  availability proposals 0/2.
- Consistency check passed: the two identical «З вишнею» rows (#6, #14)
  got identical verdicts.
- Scope note: 55% is a property of THIS pathological class (rows the
  model emptied, all under media-only posts) — NOT of the corpus; the
  corpus-level calibration gate stands at 100/100.
