# PROMPT — fix-b (T5: the promo positions table; $0)

**Contract class:** zero-cost. Runs ONLY after fix-a is accepted (it edits the same three build
artifacts — sequential, never parallel). **Baseline:** fix-a's closing `make check`; record HEAD.
**Law:** amendment 3.21 (4) — the promo surface answers with a positions table; the promo price is
a green leg (80/80); the extracted old price is NEVER printed (3.17 (3), 3.18 (7) stand).
**The operator's question this answers:** «какие позиции, по каким ценам, у каких брендов в промо».

## Step 0 — tail

Commit the standing tail by path (verify live `git status`, list actuals). This prompt too.

## Deliverable 1 — the export gains `promo.positions_table`

From the window's position evidence (145 rows): per row — `brand` (id + display), `item` (name,
volume/fat attribute as recorded), `chain` (АТБ · Сільпо · Varus · Маркетопт · other, from the
row's channel through the registry, read-only), `carrier` (leaflet_page | post_text — different
instruments, labelled), `promo_price`, `printed_pct`, `depth` (from promo + printed %, the lawful
path), `tier`, `evidence` (channel + post/page ids for the drill-down link). Fields the row does
not carry render as absent — never guessed. The extracted old price appears in NO export field of
this table. Rows: ALL 145, no sampling; the table names its window and population.

## Deliverable 2 — T5 renders it

Sortable, filterable table (brand / chain / carrier; «наші — конкуренти» toggle from the
watchlist's own-flag), value labels per the visual law, drill-down row → t.me/leaflet evidence.
Beside the table: its sample line (145 rows · which chains yielded leaflet PAGES vs post texts —
the census point already in the export). The chains' honest stubs (Сільпо/Varus/Маркетопт leaflet
depth waits on prep-b collection) stay in place.

## Guards

Determinism; embedded == committed; convergence untouched (depth aggregates still equal the
anchor); the poisoned-export guard extended to one `promo_price` cell (changed where it surfaces,
nowhere else); no external resources; strings closure (new headings in both languages via
`config/ui_strings.yaml`, no digits in strings).

## DO NOT

No byte under `results/` except the regenerated export; sealed anchors untouched; no extracted
old price on any surface or export field of this table; no re-inference, no network, no spend;
team-lead files verbatim only. Never `git add -A`.

## Verify · Report · Read-back

`make check` green, tail pasted; the first five table rows parsed FROM the built page (both a
leaflet-carrier and a post-text-carrier row among them); the poisoned-cell diff summary. Report:
`docs/reports/fix-b.md`, `docs(report): fix-b`, chat gets the path; Deviations continue numbering,
cause tags, Process signals ≤5. Read-back (one line each): (1) which price is printable and which
never; (2) where `chain` comes from; (3) what the poisoned cell proves; (4) step-0 list.
