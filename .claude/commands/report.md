# /report <name> — write `docs/reports/<name>.md`

Order is fixed; the first ten lines must let the operator answer the phase's question without
reading further.

1. **Answer** — the question from the plan, then the answer with its numbers and the files they
   come from (≤10 lines). A negative or partial answer is written as plainly as a positive one.
2. **Evidence** — commands run and their tails, artifacts by path, the checks with pass/fail.
3. **Deviations** — every departure from the approved plan, `Dv<n> [cause: contract-gap | spec-gap |
   verify-gap | env | tooling | model | process]`, one line each; full text in `implementation-notes.md`.
4. **Debts** — what is left, who owns it, what it costs.
5. `make check` tail, HEAD sha.

≤30 lines of prose. A table over 40 rows is a file under `results/` or `docs/reports/`, linked, and the
report carries only the rows that answer the question. Chat gets the path, nothing else.
