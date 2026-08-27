---
paths:
  - "docs/plans/**"
  - "docs/reports/**"
---
# Plans and reports — the two documents the team lead reads

A plan (`docs/plans/<phase>.md`, `/plan-phase`) is written BEFORE implementation and reviewed by the
team lead: question → checks → steps → stop-points → assumptions and scope choices → out of scope.
Every threshold, floor, sample, window or filter you introduce is listed there; one found only in
the report is a scope change and turns the acceptance red.

A report (`docs/reports/<phase>.md`, `/report`) opens with the question and its answer in ten lines,
then evidence, deviations with cause tags, debts, the `make check` tail. ≤30 lines of prose; a table
over 40 rows is a linked file. Numbers name the file they come from; nothing is typed by hand.
Why: D2's report was 64 lines, C1's 361 — both measured everything and answered nothing the operator
could read first. Reference: `docs/PROCESS.md` («Reports», «Plans»).
