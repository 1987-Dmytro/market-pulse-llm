# /plan-phase <name> — write the plan for `docs/PHASE-<name>.md`, then STOP for review

Read `docs/PHASE-<name>.md` and only the spec sections it cites. Explore in plan mode; no edits.
Write `docs/plans/<name>.md` in this exact order and nothing else:

1. **Question** — the operator's question the phase answers, quoted from the phase spec, and the
   artifact that answers it (file, row, number, screen).
2. **Checks** — every check you will run, as commands, with the pass condition; the end-to-end
   check last. A check you cannot run is named as such.
3. **Steps** — small, each ending in a commit by path and a check. Name the files each step touches.
4. **Stop-points** — operator decisions, paid or irreversible steps: what you will ask, and before
   which step. Money: the smoke, the cap, the rungs from `docs/PROCESS.md`.
5. **Assumptions and scope choices** — every threshold, floor, sample, window, filter you intend to
   introduce, with its reason. What the phase spec leaves open that you decided.
6. **Out of scope** — what you will not touch, copied from the spec plus anything you add.

Then STOP. Print the plan's path. Do not implement until the operator relays the team lead's «go».
