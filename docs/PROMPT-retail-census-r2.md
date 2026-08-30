# PROMPT — `retail-census-r2` (fresh session; $0; web first, Telegram API only AFTER the FloodWait lifts)

You are the executor on `market-pulse-llm`. C1 r1 (`9fa2ff4`…`e11c9a9`, `docs/reports/retail-census.md`) is
accepted for category B (47 Poltava chats, `enter`, ua ≥ 0.5) and NOT for category A: Telegram name-search
returned no official chain channel beyond the registry's (METRO Russia, an ISP «Копійка», FC Kolos, an ОСББ
«Барвінок» — Dv871 named it). The instrument was wrong for the question, not the run. Read SPEC v2 §3,
`docs/PROCESS.md` («Reports», new rule), this file.

**The operator's question this contract answers:** «Which Ukrainian retail chains and promo aggregators have
an official Telegram channel we can collect, and where are comments open?» — ONE ROW PER CHAIN.

**Step 0 ($0).** Commit by path `docs/STATUS.md` (the Dv872 witness `D1 (инструмент, $0)` is restored —
`tests/test_think_zero_shot.py::test_the_registration_rebuilds…` must be GREEN at HEAD; paste the line),
`docs/reviews/2026-08-27-harness-v2.1/**`, this prompt. Apply guard v2 (closes Dv874/Dv875, the harness
report's top debt): copy `refuse_sweeping_commands.py` → `scripts/hooks/` (`chmod +x`), the updated
`settings.json` → `.claude/settings.json` (python hook + `Edit(/docs/archive/**)`), the updated
`tests_test_hooks.py` → `tests/test_hooks.py`; `git rm scripts/hooks/refuse-sweeping-commands.sh`;
`ruff format tests/test_hooks.py`; add two lines to `.claude/rules/harness-plumbing.md` naming the
PreToolUse guard and `/plan-phase` + `/report`; `pytest tests/test_hooks.py -q` green — 16 refused,
10 accepted, the bare `ruff format` among the refused. The account is inside a FloodWait until 2026-08-28T10:21:07Z
(`results/joins_5c1.jsonl :: (census)`): no `ResolveUsername` before that moment; the run refuses on its own.

**Step 1 — handles from the chains' own sites, not from Telegram search ($0, HTTP only).** For every chain
in SPEC v2 §3 category A (35 names) fetch the official site (`metro.ua`, `novus.ua`, `auchan.ua`, `thrash.ua`,
`velmart.ua`, `fora.ua`, `delikat.ua`, `sim23.ua`, `tavriav.ua`, `ultramarket.ua`, `megamarket.ua`, `zakaz.ua`,
`kolo.ua`, `rukavychka.ua`, `nashkraj.ua`, `blyzenko.ua`, `kopiyka.ua`, `marketopt.ua`, `grosh.ua`, `silpo.ua`,
`atbmarket.com`, `varus.ua`, `eko.com.ua`, `epicentrk.ua`, `fozzyshop.ua` — these are candidates: verify each
domain resolves and is the chain's, do not invent one) and extract every `t.me/` link from the page (footer, social block, app links). Record per chain:
site, links found, or «no Telegram link on site» — a fact, not a gap. Known from r1: Novus `@NovusNews`,
Thrash invite `t.me/+HR0vG1EaFXw4NzA6`, Близенько `@blyzenkoua`, Сім23 `@sim23_simi`, Zakaz `@zakazzua`,
ATB fan promo `@ATB_FANatik`. Aggregators: from their Telegram presence already measured in r1.

**Step 2 — after the FloodWait lifts: resolve ONLY the handles of step 1 (≤40 requests, ≥3 s apart).** Same
measured columns as r1 (posts/day, price share, comments enabled + linked group, comments/day, dairy share,
language) from one history request each. Ukraine screen is a COLUMN and a filter for the table: rows with
`ua + ru-from-.ua-site` — a chain whose site is `.ru` is `reject · not the Ukrainian market`.

**Output.** `results/retail_chains.json` (one object per chain: name, site, handles, measured rows, verdict)
and `docs/reports/retail-census-r2.md` ≤30 lines: the answer first — a table of ≤40 rows, one per chain,
sorted by `comments open` then `price share`; `no channel` rows at the bottom, named. Category B: the 47
`enter` chats of r1 as a linked list, no re-measurement. Deviations with cause tags; `make check` tail
(expect 1 red — the ledger debt). Do not edit `config/registry.yaml` or team-lead files.
