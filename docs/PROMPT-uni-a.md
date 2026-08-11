# PROMPT-uni-a — the universality audit, the dry-run probe, and PORTING.md ($0)

Issued 2026-08-11 (team-lead file — read and commit, never edit). Context: arch-a is
accepted (graph + ARCHITECTURE.md + 149-row inventory); the operator's question is
how universal the system is when `config/registry.yaml` (watchlist / sources /
taxonomy) changes. Ratified scope: level (a) new brands/channels, same category;
level (b) a new retail category. Beyond-Telegram is OUT: name it in one paragraph
as the SPEC §1 future contour (source-agnostic connector interface), design nothing.
No paid calls anywhere in this phase.

**Read-back check (first lines of your report):** step-0 items, deliverables A–C,
the DO-NOT list — one line each.

**Report protocol (NEW, first use):** the phase report is a FILE —
`docs/reports/uni-a.md`, its own commit `docs(report): uni-a`, chat gets only the
path + commit hash. Same structure as before: read-back, evidence, Deviations
(continue at Dv119).

## Step 0

(1) Commit the standing vault tail if dirty (daily log, index) — own commit.
(2) CLAUDE.md, two mechanical lines (zero behavior change): add to the ownership
map "docs/reports/ — executor's; phase reports are files, not chat" · fix the
stale scorer sentence (Dv118): the NotImplementedError claim is replaced by the
actual mechanism (`tests/test_scorer.py` reflectively demands a hand-computed
test per public scorer function). File stays ≤200 lines.

## Deliverable A — the domain-leak sweep (graph-assisted, read-only)

Sweep `src/`, `scripts/` and `tests/` for domain literals that BYPASS the registry:
dairy category words (сир, молок, сметан, масл, кефір, йогурт, морозив, dairy,
ice-cream, …), watchlist brand names, channel handles. Use graphify queries + grep;
cite the query per finding. Classify every hit:

- REGISTRY-DRIVEN — the value flows from `config/registry.yaml` (e.g.
  `positions.category_keys` reads the taxonomy; `scorer.normalise_brand` takes
  aliases as an argument). This is the good class; count it.
- INSTANCE-PINNED BY DESIGN — registered prompt texts (sha-pinned, replaced by a
  new registration, never edited), frozen test fixtures, gold packs. Named, not a
  defect.
- LEAK — a hard-coded domain value in battle/pilot code that would silently
  survive a registry change. Every LEAK gets file:line + what a new domain would
  observe. FIX NOTHING — the list goes to the operator at acceptance.

## Deliverable B — the dry-run probe (measured, $0, no model)

One new script is authorized: `scripts/uni_probe.py` (one-shot class, header says
so). It materializes a TOY registry at runtime in a tempdir — category «кава», 3–4
taxonomy subcategories, 3 real coffee brands in the watchlist, sources unchanged —
and, against COPIES only, measures what follows the registry with no code change:

1. `positions.category_keys` over the toy taxonomy — does the schema accept the
   new vocabulary? (expected yes per its own docstring; prove it).
2. The pre-filter over a ≥2 000-row corpus sample with toy category words — fires
   / does not fire, counts by pattern kind.
3. Parser + tier ladder on ~10 synthetic coffee replies (fixtures inside the
   probe) — tiers assigned, no dairy assumption trips.
4. `scorer.normalise_brand` + alias table with the toy watchlist on sample
   strings, Cyrillic/Latin variants included.
5. Prompt instantiation: state the MEASURED fact — the positions prompt text is
   authored per domain and registered beside (there is no generator); what exactly
   would have to be written anew, listed by line class (intro, category enum,
   examples).

The ONLY persistent artifact is `results/uni_probe.json`: per-step verdict
{follows-registry | needs-new-registration | hard-coded}, counts, the toy
registry's sha, live registry sha `920c7f20…` untouched beside it. Live configs,
prompts and tests stay byte-identical.

## Deliverable C — docs/PORTING.md (English; every claim cites a measurement)

Level (a) — new brands / new channels, same category: the procedure that ALREADY
exists, written down: watchlist named revision (provenance, G1e history never
re-scored — the 2026-08-08 +3-brands precedent), sources via the discovery track
and entry gate (track R). Steps, owners, cost ≈ $0.

Level (b) — a new retail category: the full checklist derived from A+B, honest
about cost class per step: registry taxonomy block (cheap) · NEW registered
prompts, authored and sha'd beside the dairy ones (cheap, manual) · the `fat`
field ruling — flag as a SPEC question (generalize to `attribute` or keep
per-domain), decide nothing · pre-filter category words (registry) · NEW gold
packs + frozen sets + gates re-earned (the irreducible cost; numbers NEVER
transfer) · adapter: reuse-and-measure first, retrain only on measured failure
(ablation discipline). End with the one-paragraph beyond-Telegram contour (SPEC
§1, out of MVP).

## Verify

`make check` green (1611/2 skipped — no new fast-suite tests required; ruff
clean); live `config/registry.yaml` sha unchanged; `prompts.PROMPTS` still 16
entries, shas unchanged; the only new results/ file is `results/uni_probe.json`;
wikilinks green; Deviations Dv119+; report at `docs/reports/uni-a.md`.

## DO NOT

- No changes to `src/`, `src/market_pulse/prompts.py` above all, `tests/`,
  `config/`, `data/`, or any existing `results/` file. (Goal: this phase measures
  the terrain; a probe that edits what it probes proves nothing.)
- No fixes to LEAKs found — list them for the operator's ruling.
- No new scripts beyond `scripts/uni_probe.py`; no MCP servers; no paid calls.
- Team-lead files (docs/STATUS.md, SPEC.md, PRODUCT.md, PROMPT-*.md) — read and
  commit only.

**Recovery:** nothing here is irreversible; if the probe cannot complete a step,
the step's verdict is UNMEASURED with the reason — never a guess.

**Operator budget at acceptance:** ~20–30 min (PORTING.md + LEAK ruling).
