# REPORT — `promo-pulse-1-scaffold`

Slice: S0 · S1a · S1b · S6 · S7 · S8 done · **S2 STOPPED at SP-4** · S3 blocked behind S2.
Plan: `docs/plans/promo-pulse-1.md` (corrections applied in `9d1aee7`). HEAD `b11109a`.

## 1. Answer

**The $0 scaffold stands, and the phase still does not fit its money — but S2 cannot run as
written, and that is the operator's decision, not a defect I may fix.**

- **The scaffold**: registry r2 is on disk and loads (`74 sources — collected 35, not collected 39`,
  K2), the six promo tables exist, the draw, the instrument, its hooks and the two graders are
  built and tested. `make check` **4 195 passed · 2 skipped**, from a 4 129-passed baseline with
  one red I inherited and closed.
- **The money** (dry run over the *pre*-top-up store, `results/run_5c2_positions.json` for rates,
  guard read live at `REMAINING $2.4200`): 609 leaflet posts → **1 050…5 901 pages**. At the
  realised rate 10.408 s/page the leg is **$3.35…$18.84 — it fits at neither end**. It fits only at
  the *page floor* of the two cheaper rates ($0.56 warm-up marginal, $1.37 fitted middle), and the
  fitted middle is an interpolation (`measured: false`), not a reading.
- **The stop**: four of the 20 A1 channels write into **pinned raw v1 files**, and they hold
  **92.4 % of posts and 98.1 % of comments**. S2 as planned would have appended to them
  irreversibly. Nothing was collected; no Telegram session was opened.

## 2. Evidence

| check | verdict |
|---|---|
| K0 `make check` | **4 195 passed, 2 skipped, exit 0** (`scratchpad/k0_guard.txt`); baseline `1 failed · 4 129 passed` → 4 130 → 4 138 → 4 190 → 4 195 |
| K1 `make preflight ARGS='config/registry.yaml'` | 32 of 38 pinned paths match. Six differ; **two are r2's** (`config/registry.yaml` live `9718aa52…`, `scripts/window_summary_5c2.py` live `2de23c07…`), reached through the revision chain, not re-pinned. The other four (`brands.py`, `docs/SPEC.md`, `census_c3a_posts.json`, `sku_prefilter_census.json`) predate this phase — `git log 58ff037..HEAD` touches none of them (0 commits). |
| K2 registry loads | `sources: 74 — collected 35, not collected 39`; A 18 · B 17 · PAUSED 39 |
| K11 `tests/test_promo_hooks.py` | green, inside K0 |
| raw v1 baseline | `shasum -c results/raw_v1_baseline.sha256` → **6 of 6 OK**, taken before the run and again after |
| K3 / K4 | **dry run only**, over the pre-top-up store, written to the scratchpad and *not* to `results/`: the plan's §5.1 fixes the window anchor after S2's top-up, so a census taken now would price a population S2 is meant to change. `results/promo_census_c2.json` and `results/promo_projection_c2.json` **do not exist**. |
| K7 draw | script + tests green; **not run** — see Dv7 |
| K5 / K6 / K8 | blocked on the team lead's label files, as the plan says |
| K10 `make tick` | **not runnable: the Makefile has no `tick` target** (`check`, `check-stamped`, `fmt`, `preflight`, `baselines`). It is built in a later step. |

Commits: `c74c9ce` (S0 ledger debt) · `58ff037` (S1a loader) · `952faeb` (S1b+S6) · `765552b` (S7) ·
`f914579` (S8) · `e89a4a5` (S2/S3 instruments) · `b11109a` (the collector fix and its guard).

Population figures, all re-derived from files: 678 price threads = **229 currency + 449
decimal-only** (disjoint, exhaustive); the queue rule removes **2 808 wordless comments of 4 718**,
leaving **488** eligible threads (182 / 306).

## 3. Deviations

- **Dv1 [contract-gap]** S1b and S6 landed in **one** commit. Their moved-pin claims share three
  files, so either alone is red at checkout, and splitting hunks needs `git add -p`, which is
  unavailable here.
- **Dv2 [spec-gap]** r2 was refused by **four** guards, not the one the plan named (`segment_for`).
  `registry_through_the_seal` tested the registry by byte equality and **ten producers** reach the
  registry through it. Answered with a revision chain (`registry_before_r2` / `registry_revisions` /
  `load_registry_as_pinned`); **24 committed records** quote the sealed producer sha and all pass.
  Nothing re-pinned. This mechanism is not in the approved plan.
- **Dv3 [contract-gap]** The derived A bucket after r2 is **18 rows against §3's 17**. The extra is
  `marketopt_promo`: §3 named Маркетопт *private* and did not say to drop the public channel. Both
  are in collection. **Team lead's call.**
- **Dv4 [verify-gap]** S1b/S6/S7/S8 got **one** verifier reading, not four: S8's tests import S6's
  module, so an S1b-only reading is unobtainable without holding S8 out of the tree, at ~12 min a
  reading. The commits are still separate and by path.
- **Dv5 [process]** **S2 stopped at SP-4** — see §4.
- **Dv6 [verify-gap]** `scripts/collect_r2.py` shipped in `e89a4a5` **with no test at all**, and
  carried two defects found by *running* it: provenance built once from `None` above both write
  loops (it is per source), and no pinned-file guard. Both fixed in `b11109a` with five tests and a
  measured negative control.
- **Dv7 [contract-gap]** The K7 draw was **not run**. Its population is the 678 price threads, which
  live almost entirely in the two pinned comment stores; whether that population grows is exactly
  what SP-4 decides. Drawing now would freeze a sample from a corpus about to change.

## 4. The stop — SP-4

`results/raw_v1_baseline.sha256` pins six store files, all six verify today, and four A1 channels
map onto them: `@atb_market_official`, `@silposilpo`, `@VARUS_channel`, `@msuaaaa`. They are the
incumbents S2 was told to top up — which is why `collect_5c1` refuses them at channel level, and
why `collect_r2.py` was written as a sibling in the first place. The refusal did not come with it.
`data/` is gitignored: the append is invisible to `git status` in both directions and there is no
history to restore from.

| | channels | posts | comments | threads |
|---|---|---|---|---|
| pinned (frozen) | 4 | 6 057 | 11 338 | 1 538 |
| free to collect | 16 | 497 | 223 | 37 |

At most **37 of the 678** price threads can lie outside the frozen files. The options:
**(a)** collect the top-up into a second store root and teach K3 to read v1 ∪ r2 — the repo's own
precedent (`fetch_comments_v2.py`: «`data/raw/comments/` is never opened for writing»); **(b)**
collect only the 16, leaving C2 with 1.9 % of the comment corpus; **(c)** re-baseline — not
recommended, the append cannot be undone and the baseline is the only durable proof those stores
were never written.

## 5. Debts

- S2 and S3, behind SP-4. S3's two paths go to the operator the moment they exist.
- K7's draw, behind the same answer (Dv7).
- K10 has no `make tick` target yet; K5/K6/K8 wait on the team lead's label files.
- Dv3 (18 vs 17) and Dv2 (the revision chain) want a team-lead ruling.

## 6. Verifier

```
All checks passed!
4195 passed, 2 skipped in 680.05s (0:11:20)
exit=0
```

HEAD `b11109a`. `shasum -c results/raw_v1_baseline.sha256` → 6 of 6 OK.
