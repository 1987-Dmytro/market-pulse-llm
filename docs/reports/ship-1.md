# ship-1 — «Проект закончен и работает?»

**Yes on a clean clone — every clause of the check line but one.** `git clone <repo> /tmp/mp-e2e` at `671ab29`:
`make front` exit 0, `make tick` exit 0 («no store at data/derived/pulse.db — nothing to promote, nothing
written»), `make promo-screen` exit 0 off the committed exports, `make serve` → `/api/status` 200 and `/` 200
then stopped, `draw_truth_20.py` 20 rows, `make session` the standing prompt out of `docs/PROMPT-standing.md`,
`firebase.json` + `.firebaserc.example` present and nothing deployed. Porcelain then EMPTY and the two seals
plus the front export unmoved (`e45860c6…` · `eff8ba5b…` · `25566dff…`). Log: `/tmp/e2e_final.log`.

**The open clause is `make check` ON THE CLONE** (the open stop in `docs/plans/ship-1.PROGRESS.md`): exit 2 at
collection, `tests/test_train_qlora.py` reading `data/raw/posts` at import; allowed to continue it reads **3939
passed · 245 failed · 127 errors · 5 skipped** — 372 tests in 65 files whose input is the collection store under
`data/`, which `.gitignore` keeps out of git by SPEC law. The same red stands at `643c012`, before this item.

**The removed-source probe renames a DIRECTLY-required export** (ruling (iii) 3): `mv
results/region_collect_report.json …renamed && make front` → exit 2, «export-front REFUSED: missing required
source(s) results/region_collect_report.json …», make stopping at the first recipe line, so `npm ci` never ran.
`make front` stages 0 of 402 leaflet photos there — they live under gitignored `data/annotation/`.

**Built here.** `firebase.json` (`public: dashboard/app`, SPA rewrite) + `.firebaserc.example`, the operator's
real `.firebaserc` gitignored. `make session` prints the standing prompt's fenced block out of the file, never a
copy, refusing by name when the file carries no block or more than one. `README.md` is the front page — seven frames of the
app — and carries not one typed number: `scripts/build_readme_results.py` writes its figures between one marker pair,
every row naming its `file :: field`, byte-identically on a second run and on the clone.

**Deviations.** None to the built clauses. The SPA rewrite never fires on the app's own hash routes; on a
hand-typed deep path it would serve `index.html`, whose relative assets then 404 — it is in the file because the
check line names it (cause: spec text). **Debts:** PROGRESS «named, not built».
**`make check` (working tree, HEAD `671ab29` both ends).** `ruff check .` **All checks passed!** · **4348 passed, 2 skipped in 703.65 s**, exit 0 — the same 4348 ruling (iii) accepted, since this item adds no Python test; the two docs written during the run are read by no test (grep shown in the session).
