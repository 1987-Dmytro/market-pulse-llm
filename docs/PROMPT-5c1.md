# PROMPT-5c1 — entry gates for the launch set, collector on the new composition, the volume calculation

**Contract:** `docs/SPEC.md` §3.11 — read §3.11 only, not the whole spec.
This file is the whole brief. **$0 phase**: no pods, no endpoints, no
OpenRouter — Telegram API only. All artifacts in English. Team-lead files
(`docs/STATUS.md`, `docs/SPEC.md`, `docs/PROMPT-*.md`) are read-and-commit,
never edit.

**Context in three lines:** The parity programme closed 06.08 — runtime is
a stop-after A6000 pod, batch 1 permanent, Δ=0.0000 (`results/parity_5b_a.json`).
The operator fixed the launch composition 06.08 (`docs/CHANNELS-launch.md`,
canon) and ratified the 5c split 07.08: **5c1** gates + collector + volume
calc ($0) → **5c2** loop core + backlog window (the one paid event) →
**5c3** category layer + sidecar v2 + alerts v0.

## Step 0 — commit the tail

`git status --short` should show exactly: `docs/SPEC.md`, `docs/STATUS.md`,
`knowledge/hot.md`, `knowledge/index.md`, `knowledge/daily_logs/2026-08-06.md`
(modified), `knowledge/daily_logs/2026-08-07.md` (untracked) and
`docs/PROMPT-5c1.md` (this file, untracked). Stage BY PATH (never
`git add -A`), two commits: (1) `docs: 5c opened — STATUS decisions of 07.08,
PROMPT-5c1` for the three team-lead files; (2) `docs(vault): the 06-07.08
tail` for the knowledge/ paths. Your own session output (hot.md refresh,
today's daily log, /save checkpoints) is pre-authorised into its own commit
at session end — do not stop for it. STOP only for a path neither list
explains.

## Deliverable 1 — the track-R entry gate over 62 candidates; the registry grows additively

The operator's composition choice is already made (verdict 06.08 + one late
addition); the gate VERIFIES each entry before it reaches
`config/registry.yaml`. The 4 registry channels passed the 27.07 entry check
and are OUT of gate scope.

- Extend `scripts/entry_check.py` with a batch mode over the explicit handle
  list below, reusing the pure core (`src/market_pulse/entry_check.py`:
  `collapse_albums`, `traffic_stats`, `build_verdict`). Read-only Telegram:
  NO group joins in this deliverable, no store writes.
- Per channel: resolves; language mix over recent posts (UA/RU vs other);
  liveness (last-post date, posts/week over the last 4 weeks); linked
  discussion group (present, open); comment counters on recent posts.
- Mechanical verdict: PASS / FAIL (does not resolve · dead against its
  bucket's expectation · non-UA/RU dominant) / FLAG for the operator.
  Pre-registered flags: `@kolyastravinsky`, `@whowears` (theme check),
  `@marketopt_official` (class + comments confirm). Also FLAG wherever
  evidence contradicts the bucket (e.g. a comments-bucket channel whose
  group is missing or closed).
- **STOP after the gate report**: present every FAIL and FLAG with one-line
  evidence; the operator rules in chat (dictated-verdict pattern); apply
  rulings, then write the registry. Deliverable 2 starts only after this.
- `config/registry.yaml`: ADDITIVE edits under `sources:` only.
  `source_type` from the existing `SOURCE_TYPES` (most candidates are
  `community`; `@marketopt_official` is `official_retail`);
  `comments_enabled` from the gate's group finding. Watch-bucket entries
  need a `watch: true` marker — extend the `Source` dataclass additively
  (default `False`), keep the loader strict, guard with tests. `taxonomy:`
  and `watchlist:` stay untouched (the operator's 15-class category ruling
  is 5c3's input, recorded in STATUS).
- Record: `results/entry_gate_5c1.json` — one row per candidate (handle,
  bucket, checks, verdict, ruling if any), summary counts, provenance.
  `data/entry_check_report.json` (the 27.07 run) is not touched.

The 62 candidates by bucket (canon: `docs/CHANNELS-launch.md`; on any
mismatch STOP and name it, do not resolve it yourself):

- **launch, posts+comments (29):** @tretyakovaele @kopiyochka1
  @klopotenkofood @maudau @uasaler @retsepty @katyal55 @smirnov108
  @tarilka_malyuka @kkondr_fit @polyakova_fitness @znishkom @kuksa2022
  @HealthPsycholog @ATB_FANatik @offspringrus @sashafitnesslife
  @Pro_Detyintumama @chifit_family @ya_Nenka @baby_broccoli_club
  @useful_healthy_fitness_menu @olgaa_trainer @kolyastravinsky @whowears
  @denisovapro @eftforhealth @rezeptmoi @discountua1
- **launch, posts only (18):** @recepti @mameni_recepti @retsepty4
  @epicentrk_sale @konservacia_kulinaria @intensiv_Mamiev @Mambabyua
  @retsepty5 @blwbabies @vylkachannel @whitecode_zny @gaid_skobioale
  @dpssgovua @kulinariya_chat_a @Wellosophy_Lesya @atb_aktsiyi
  @anastasiiadavydiukfitness @korolevakuchni
- **watch (14, posts only, NO joins ever in this phase):** @itsmamix
  @regina_tatlybaeva @netainaya_vecherya @retsepty10 @skhudnennya
  @prostetsofa @viktoria_sshh @hydnem_prosto @dimakaminskyifit
  @dutyache_menu @polinalykovagv @Evgenija_dutjache_menu
  @chekh_yevheniia1982 @cozymotherhood
- **late addition (1, gate confirms class):** @marketopt_official

## Deliverable 2 — collector on the new composition + the 4-week window ($0)

Ruling 22 (SPEC §3.11 (6)): the backlog is a WINDOW of the most recent ~4
weeks; SCORING it is 5c2's paid event — 5c1 only COLLECTS.

- Group joins ONLY for gate-passed comment-capable channels (the 29 bucket
  + `@marketopt_official` if its flag resolves that way). Registry channels
  are already joined. NEVER a watch-bucket join. Pace conservatively (a few
  joins per hour at most), obey FloodWait with wait-and-resume, log every
  join (timestamp, channel, outcome) to `results/joins_5c1.jsonl`;
  spreading joins over 2-3 days is expected — a channel's comment
  collection starts once its join has landed.
- Collect the posts window — `since = first run date minus 28 days`, the
  exact date fixed in the record — for every gate-passed channel INCLUDING
  watch; comments for the window's threads in joined groups only.
- Idempotency is the store's: `RawStore.append` dedup on (channel, msg_id);
  cursors via the loop watermarks (`market_pulse.loop`). New channels write
  NEW per-channel files under `data/raw/`; the original v1 stores stay
  byte-identical — `shasum -c results/raw_v1_baseline.sha256` → 6/6 AFTER
  collection, output shown.
- After collection: `PYTHONPATH=src python3 scripts/run_loop.py --once
  --dry-run` over the grown registry; quote the rendered totals (channels
  in pass, threads, rows_to_inference) — that queue is what 5c2 prices.
- Record: `results/collect_5c1.json` — per channel: posts stored, comments
  stored, window dates, damaged lines; totals; provenance.

## Deliverable 3 — the volume decision input ($0, artifact-sourced)

`scripts/volume_calc_5c1.py` → `results/volume_calc_5c1.json` + a printed
table. Every input names its source artifact in the record — no hand-typed
numbers: cold starts and per-pass cost from `results/serving_5b.json`
(46.2 s local NVMe / 278.9 s network volume), the 59 GB pinned-revision
weight payload (`scripts/runbook_5b.md`), the volume's observed ~$0.24/day
billing (knowledge/hot.md, corroborate from the account-balance deltas in
`results/spend_phase4.json` sessions), the A6000 $/h from
`scripts/runbook_5b.md`, the stopped-pod container-disk billing footgun
(knowledge/hot.md). Three rows at cycle-1 cadence (2 passes/day × 30 days):

- (a) keep the network volume (storage $ + the SLOWER 278.9 s boot);
- (b) delete it, re-stage 59 GB onto pod NVMe per pass (download minutes
  priced at pod $/h; the faster 46.2 s cold start shown beside);
- (c) stopped pod with container disk (disk bills while stopped; capacity
  caveat stated: resume is NOT guaranteed — the capacity clause pins the
  GPU class, never one pod).

Decompose every row into storage $ + boot/stage minutes $ + risk caveat —
never one blended number without its parts. End with a recommendation
line; the DECISION (volume fate, advancing the ~05.09 review) is the
operator's at acceptance.

## DO NOT

- No pods, no endpoints, no templates, no OpenRouter — $0; the spend
  anchors are not touched, not even read-modified.
- Do not edit `docs/STATUS.md`, `docs/SPEC.md`, `docs/PROMPT-*.md` —
  team-lead files (read and commit only).
- Do not write into the six original raw v1 store files; do not touch
  `data/raw/comments_v2/`, frozen sets, or annotation artifacts.
- No join before that channel's gate verdict; no watch-bucket joins at all.
- `taxonomy:` / `watchlist:` in `config/registry.yaml` stay untouched.
- None of the `--force` / freeze / one-shot scripts (standing list in
  `knowledge/hot.md`).

## Verification — evidence, not assertions

`make check` green (show the tail). `shasum -c` 6/6 after collection.
Dry-run totals quoted. `git diff --stat` for the registry change + the
list of added ids. Numbers quoted from all three result files by path.
The Deviations section in `implementation-notes.md` updated — silence is
not compliance. `git log --oneline` for your commits; clean `git status`
at the end.

**Report back:** gate counts (pass/fail/flag) + flag evidence for the
operator's rulings; join-log summary; collection totals + queue depth; the
volume table. Numbers by artifact path, never prose recall. State your
assumptions explicitly.
