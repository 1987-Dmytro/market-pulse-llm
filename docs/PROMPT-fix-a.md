# PROMPT — fix-a (watchlist rules r1, honest labels, gate census, rebuild; $0)

**Contract class:** zero-cost. No GPU, no network, no collection, no spend, no re-inference.
**Issued:** 2026-08-15 (team lead). **Baseline:** `make check` 2 392 passed / 2 skipped (6b accepted);
record your starting HEAD in the report.
**Design authority:** `docs/PLAN-comment-signals.md` §2 (the gate and its silencers) + the operator
rulings of 15.08 (sitting red gate). Context: the dashboard's brand surfaces are currently fed by a
matcher with known collisions (варто ×7, Гармонія-centre ×1 of 11 brand rows) — ruled, now applied.

## Step 0 — tail + amendment 3.21

1. Commit the standing tail by path — verify against live `git status`; expected:
   `knowledge/hot.md`, `knowledge/daily_logs/2026-08-15.md`, `knowledge/index.md`, the MODIFIED
   `docs/PLAN-phase6-command-center.md` (team-lead edits after its last commit), untracked
   `docs/PLAN-comment-signals.md`, this prompt and `docs/PROMPT-fix-b.md` (both arrive untracked).
   List the actuals in the report. Never `git add -A`.
2. Land **amendment 3.21** by the house manoeuvre — FOUR moving parts (6a's Dv336 lesson): the
   marked block in `docs/SPEC.md` (3.19/3.20 marker convention, index entry INSIDE the block — the
   `amendment-index` block is sealed-kept, never touched) + `tests/test_sku_prereg.py` enumeration +
   `scripts/write_prereg_5c2.BLOCKS_TODAY` + `make check` green, ONE commit.

## Amendment 3.21 — verbatim block content

1. Watchlist text-matching rules are law in `config/watchlist_rules.yaml` (a NEW file).
   `config/registry.yaml` and `config/lexicon.yaml` are sealed by pre-registration pins and are
   never edited for rule changes. Named revision **r1 (2026-08-15)**: `varto` — text hits only with
   a brand marker; `selianske` — text hits only with a Гармонія marker nearby (both: operator
   rulings of 2026-08-10, applied early by the operator's 15.08 ruling); `garmonija` — comment-text
   hits only with a dairy-category marker nearby (operator ruling 15.08 — the children's-centre
   homonym). G1e history is never rescored; provenance names the rules revision it matched under.
2. The comment-analysis target architecture is ratified: thread gate with silencers → one LLM
   reading per thread → signal verdicts carrying evidence msg_ids (design authority:
   `docs/PLAN-comment-signals.md`). Its bars arrive by pre-registration before any paid reading.
3. Until the stance layer is law, every brand × tonality surface is labelled «повідомлення, де
   згадано бренд» — never «ставлення до бренду».
4. The promo surface answers with a positions TABLE: brand × item × chain × promo price ×
   printed −N% × depth. The promo price is a green leg (80/80); the extracted old price is never
   printed (3.17 (3) and 3.18 (7) stand). Implementation: fix-b.

## Deliverable 1 — `config/watchlist_rules.yaml` + matcher revision r1

- The rules file: per-brand marker requirements exactly as the amendment states them; the marker
  vocabularies NAMED in the file (dairy-category words sourced read-only from `config/lexicon.yaml`
  and `data/category_lexicon_draft.json` — list the chosen terms explicitly; brand markers: «ТМ»,
  «торгова марка», latin `Varto` etc.). Revision id `r1`, dated, with the three rulings cited.
- `src/market_pulse/brands.py` (`find_watchlist_brands` / `watchlist_aliases`) learns the rules —
  ONE matcher, no second definition anywhere. Every consumer found by grep + graph query is
  enumerated in the report with the count.
- **Seal discipline (team-lead preflight, verified today):** `registry.yaml` is pinned by
  `results/prereg_5c2_run.json` AND `results/sku_pilot_prereg_v2.json`; `lexicon.yaml` by the sku
  prereg. NO byte of either moves. The rules live ONLY in the new file.
- **Anchor-parity check BEFORE wiring:** open `results/window_summary_5c2.json` and determine
  whether any of its 902 convergence leaves derives from the matcher. If yes — the 6a mirror keeps
  the anchor's own (old) matching for those leaves (the `price_fields_present` precedent: the
  mirror reproduces the sealed record's definitions), and the PRESENTATION brand cut moves to r1 as
  a separately labelled field. If this split cannot be kept clean — STOP and report.
- Tests both directions: «дитячий центр "Гармонія"…» → no hit · «Гармонія, молоко смачне» → hit ·
  «чи варто йти» → no hit · «новинка від власної ТМ Varto» → hit · «Селянське» alone → no hit —
  each against the REAL rules file, not stubs of it.

## Deliverable 2 — rebuild with r1 + honest labels

Regenerate `data/derived/pulse.db` → `results/dashboard_data_w1.json` → `dashboard/index.html`
(this contract EXPECTS those two committed artifacts to move — determinism, embedded==committed,
convergence and the poisoned-export guard all stay green on the NEW pair; every spend/prereg/
window_summary anchor stays byte-untouched).

- The brand cut now carries `watchlist_rules: "r1"` in its sample block; expect the honest
  shrinkage (~3–4 real brand rows of the former 11) — that shrinkage IS the deliverable.
- Labels per amendment 3.21 (3): T1/T4 headings and ⓘ say «повідомлення, де згадано бренд»; the
  T4 «Наша» column renders «наш бренд» (not «власна марка» — it collides with private-label
  vocabulary); both languages, via `config/ui_strings.yaml`.
- Cosmetic, one line each: the T0 KPI row fits six tiles in one row at 1920px.

## Deliverable 3 — the gate census, priced

`scripts/gate_census_w1.py` → `results/gate_census_w1.json`: over the window's comment threads,
the 2×2 grid {lexicon: narrow (`config/lexicon.yaml`) | wide (+`data/category_lexicon_draft.json`)}
× {silencers: off | on (варто-rule · giveaway-post threads via the model's post-type label ·
plus/«Тест» repeat rule · scam pattern)} — for each cell: threads, comments covered, and the
projected cost of one LLM reading per thread at the measured serverless prices
(`results/run_5c2_comments.json` anchors; beside every price, its sample — the
registrations-and-draws rule; open it by hand if it does not inject). This record prices the
cycle-2 gate AND the stance probe. No prereg is written here.

## DO NOT

- `config/registry.yaml`, `config/lexicon.yaml` — read-only, sealed (see D1).
- No byte moves under `results/` EXCEPT the regenerated `dashboard_data_w1.json` and the NEW
  `gate_census_w1.json`; sealed anchors untouched; `data/loop_cursor.json`, `data/raw` untouched.
- No re-inference, no Telegram, no GPU, no spend. Team-lead files: commit verbatim, never edit;
  `docs/SPEC.md` only via the step-0 manoeuvre. Never `git add -A`.

## Autonomy

Free within the seam (matcher + rules file + builders + census script). A convergence leaf that
cannot survive the anchor-parity split, a pin guard reddening, or a rule the amendment text does
not cover → STOP and report, never improvise law.

## Verify (evidence, not assertions)

`make check` green (baseline 2 392/2 — expect growth); paste the tail. Paste: the brand-cut before
/after counts read from the two exports; the census 2×2 grid from the JSON; the anchor-parity
finding (which leaves, if any, derive from the matcher and what the mirror does about it); the
rebuilt page's T4 first rows parsed FROM `dashboard/index.html`.

## Report

`docs/reports/fix-a.md`, commit `docs(report): fix-a`; chat gets ONLY the path. Deviations in
`implementation-notes.md`, numbering continues after Dv353, cause tags; "Process signals" ≤5
lines. End with the house `/save`.

## Read-back first (one line each, before any edit)

1. Which two config files are sealed, and where do the new rules live?
2. What happens to the 902-leaf convergence when the matcher changes?
3. What does the census price, and what does it NOT write?
4. Step-0 commit list, and the four moving parts of the 3.21 manoeuvre?
