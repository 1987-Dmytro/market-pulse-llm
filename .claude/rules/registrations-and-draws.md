---
paths:
  - "scripts/write_prereg*.py"
  - "scripts/write_sku_prereg*.py"
  - "scripts/write_sku_projection*.py"
  - "scripts/projection_*.py"
  - "scripts/build_*_pack*.py"
---
# Registrations and draws — the 5c2 retro's one rule

> **Beside every price, name what it was measured ON. Beside every draw, measure a rank.**

Routed here at the 5c2 phase close (2026-08-14) off the `[model]` cluster — 10 of the program's 45
tagged deviations, the largest single tag. `paths:` is what the harness matches to decide when this
is loaded, so it costs nothing at startup and arrives when it binds. Each glob was checked to match
at least one real producer (1 / 2 / 4 / 1 / 10 files); the injection itself was NOT observed in the
session that wrote this file — a rule appears to load once per session and the sibling rule had
already loaded before this one existed.

## The price half

A rate is not a property of a leg. It is a property of the SAMPLE it was measured on, and the two
are only the same number when the sample is the population.

* **Dv308** — the leaflet page rate came from skub2, which measured a sparse PREFIX of the corpus
  (the first pages of each post). On the 159-page population the real rate is **2.43× higher**. The
  comment rate, measured on a population, landed within **−0.4%**. Same session, same discipline,
  same record — one of them named its sample and one did not.
* **Dv310** — the go/no-go warm-up ran on a page that happened to be EMPTY, and under-priced the
  leg **2.4×** across two independent boots. A warm-up is a sample of one.
* **Dv180** (sku-b, the precedent this inherits) — a 64×64 probe priced a real leaflet page at 1/3.5
  of the truth and the gate passed the run it exists to refuse.

So a `prices` block carries, per corner: the value, its unit, the record and field it came from, the
SESSION that measured it, and **what population it was measured over**. `write_prereg_5c2.prices()`
is the shape; the team lead's ruling after 5c2-run made the last of those mandatory
(«beside every price the sample of the measurement is NAMED»), with the leaflet reference price now
**10.408 s/page over n = 159** and older records never re-scored.

The bound is safe in one direction only: a rate measured on a cheap sample is a FLOOR on the real
one, never a ratio. Say which you are using.

## The draw half

A seed makes a draw reproducible. It does not make it representative, and the two get confused
because the record prints only the seed.

* **Dv323** — five comments drawn from five strata under one `random.Random(42)` put **three of them
  on rank 163** of their sorted pools. Reproducible, and correlated: the draw was about the seed's
  position, not about the population. Fixed by putting the stratum INTO the seed
  (`random.Random(f"{seed}:{stratum}")`) and by a test that measures the RANKS rather than the ids.

So a draw over more than one stratum seeds per stratum, and its test asserts something about the
distribution of the drawn ranks — an id-equality test passes on a perfectly correlated draw. And a
draw that changes after somebody has seen it is printed BOTH ways in the report, because an
audience is what makes a redraw auditable.

## Why here

CLAUDE.md was declined: it is capped at 200 lines and the boot census already reads 13.4K against a
9.0K target, so a rule that binds when two kinds of file are edited would be paid for in every
session that edits neither. A producer docstring was declined: it reaches whoever opens that one
file, and the next cycle's registration is a new file.
