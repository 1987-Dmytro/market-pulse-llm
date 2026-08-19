# PROMPT — lora-b: two arms, one pre-registered attempt, and the bar decides line B

**Sitting-2 rulings (19.08) + the r2 ruling (docs/STATUS.md «День 19.08»):
arms A = 500·weighted / B = 650 top-up·weighted; gate = the SEALED gold r2
bar ≥12/14, ONE pre-registered attempt; cap $6.00, frozen at the first
`pod create`; red gate CLOSES line B → sitting C. This contract has exactly
ONE paid session (D3); everything else is $0. You MAY close D0–D2 in one
session and run D3–D4 in a fresh session that reads the committed prereg —
prefer that split if context runs long.**

## Baselines — hand-run 19.08 evening (the instrument this contract builds
## in step 0.5 did not exist yet); regime: measure and name, never silently fix

- porcelain: M docs/STATUS.md · M knowledge/daily_logs/2026-08-19.md ·
  M knowledge/hot.md · M knowledge/index.md · ?? docs/labels-pass1-r2.jsonl
  (+ ?? this PROMPT once written). Census 9.8K (target 10.7). Suite
  **3 001 / 3 skipped**, r2 gate 9/9 with the real file.
- `docs/labels-pass1-r2.jsonl`: **150 rows, sha256 8f611437fdd3…**,
  distribution не_наш_рынок 89 · null 46 · категория_личное 11 ·
  сеть_ритейлер 4 · молочный_бренд 0 (validator exit 0, team lead's run).
  Combined arm-B set = 650: нн 340 · null 213 · сеть 48 · кат 47 · бренд 2
  (re-derive as your step-1 refusal gate, H6).
- Measured constants (4.5h2 / probe-b, worst cases): **61.047 s/step**
  (A6000, seq 1408, micro 2 × accum 8); boot-to-ready spread **192–293 s**
  (1.53×, registered as a spread); transport call **5.162 s/unit**; base
  model bar **9/14** — per-row verdicts live in probe-b's SEALED record and
  are NOT re-run (paired on identical instances, same prompt sha).

## Step 0 — the tail and the r2 seal

1. Vault tail, own commit: `knowledge/daily_logs/2026-08-19.md`,
   `knowledge/index.md`, `knowledge/hot.md` (inherited).
2. Team-lead files verbatim, own commit: `docs/STATUS.md` +
   `docs/PROMPT-lora-b.md`.
3. **The r2 SEALING commit, atomic (precedent `8d2e1ba`):**
   `docs/labels-pass1-r2.jsonl` verbatim — sha printed BEFORE staging, after
   committing, and out of git, all equal to 8f611437… ·
   `results/labels_pass1_r2.jsonl` byte-identical freeze ·
   `results/labels_pass1_r2_provenance.json` = provenance AND pin (labelled_by
   team lead · date 2026-08-19 · codebook `docs/label-pack-pass1-r2.md` ·
   pack r2 · the distribution · sha fields in preflight's shape) · seal tests
   mirroring r1's WITH the hardened FILES path-asserts from day one, plus the
   flipped-label negative control on a scratch copy. `make check` green from
   this commit; final count named.

## Step 0.5 — debts ($0)

- **`make baselines`** (script + Makefile target): deterministically prints
  the block every future contract pastes — `git status --porcelain`, census
  line, latest suite count (from a stamp file the check writes, or "run make
  check"), `wc -c` of the boot files, preflight registry count. Escalation of
  Dv553: a Baselines block is INSTRUMENT OUTPUT, never team-lead memory.
- Orphan lessons: plant the memory FILE for Dv521's own mechanism (the
  `max(weights, key=allocation)` tie that printed another thread's payable
  beside its pick — `docs/reports/pass1-data-prep.md:305`); lesson files cost
  0 at boot. Index lines: the index stands AT the 150-line bar — if a line
  does not fit, the line-debts stay NAMED (no ad-hoc eviction).

## D1 — the two seams, driven at zero cost BEFORE any pod

- **`scripts/train_qlora.py`: class-weighted sampling as an OPT-IN flag.**
  Formula (pre-registered): sampler weight w_c = N/(K·n_c), K=5, capped at
  8.0, computed on the arm's own dataset. Default OFF preserves today's
  behavior — drive BOTH branches in tests ([[one-flag-two-branches]]).
  `config/qlora.yaml` is FROZEN LAW — never edited; arm deltas (data path,
  weights on) live in the prereg record and CLI args only.
- **A pass-1 SFT builder** (`scripts/build_pass1_sft.py`, new): renders
  prompt→target pairs for arm A (labels r1, 500) and arm B (r1+r2, 650)
  under the SAME frozen prompt the transport sends (`PASS1_TASK`,
  `prompts.py:1274`, sha 5a4a3cb6… on the may-not-move list); deterministic,
  record self-pinned, provenance tags labelled-by-team-lead; exam threads
  are excluded by pack construction — assert it again anyway.
- **`scripts/pass1_pod_runner.py`: an `--adapter` flag** that attaches the
  PEFT adapter AROUND the model `local_llm.py` constructs —
  `src/market_pulse/local_llm.py` is PINNED and is not edited. Sim both
  argv branches on the seam, like probe-b's transport sims.
- H6 refusal gate: re-derive every registered number below from its formula;
  a mismatch is a finding BEFORE the money.

## D2 — the pre-registration (committed BEFORE `pod create`; git clock proves order)

`results/prereg_lora_b.json`, sealed at the first pod create:

- **Gate:** max(gold14(armA), gold14(armB)) ≥ **12/14** on sealed gold r2,
  scored by probe-b's scorer, ONE attempt, no retry, no tuning after any
  eval output is seen. **Multiplicity named:** two shots ≈ double the
  false-pass odds of one — accepted by the sitting-2 ruling and written in
  the record. Red → line B CLOSED, sitting C. Green → the higher arm ships;
  tie ships arm B (pre-named).
- **Census-50: observation only, no bar** (baseline 25/50 None).
- **Arithmetic (formulas in the record):** steps/epoch = ceil(n/16); 2
  epochs; arm A 64 steps ≈ 3 907 s; arm B 82 steps ≈ 5 006 s; eval 2
  adapters × 64 units × 5.162 s ≈ 660 s; worst case ≈ (2.48 + 0.18 + 0.13
  boot + 0.5 overhead) h × $0.80/h ≈ **$2.63**; cap **$6.00** covers the
  recovery clause with margin.
- **Kill-clock, every rung BEFORE its milestone:** live A6000-class price >
  **$0.80/h** at create → STOP, no endpoint · ssh dead-man ≤180 s or KILL
  (proven gate-0) · boot-to-training-start ≤ **450 s** (worst 293 × 1.5) or
  KILL · s/step watchdog: >122 s (2× measured) over 5 consecutive logs →
  KILL · **milestone after arm A: guard reading ≤ $2.50 else STOP before
  arm B** · absolute session ceiling **7.5 h** (= cap / price ceiling) ·
  `guard --until` bounds the window.
- **Recovery clause:** ONE pod re-creation after a PROVEN deletion
  (listing), same cap; NEVER two billing endpoints concurrently — the goal
  is no parallel spend, whatever the letter. Pods, not serverless (16.08).

## D3 — the ONE paid session

Create (price read and recorded, Dv448) → boot gate → train arm A →
checkpoint + provenance + **milestone guard reading** → train arm B → eval
A and B on gold-14 + census-50 via the transport with `--adapter` → **scp
EVERYTHING before any verdict** (per-row raw replies, adapters, loss logs,
pod log) → delete pod, deletion proven by LISTING. Gate records append-only.

## D4 — the verdict ($0)

Verdict record (gate applied by the scorer, never the eyeball) · ablation
table: base 9/14 (sealed) / arm A / arm B, paired per-row on the same 14,
census-50 profiles beside it · adapters' provenance (shas, seed, config,
weights) · ADR: registration + outcome, multiplicity note, what ships ·
report `docs/reports/lora-b.md`, path-only in chat. Deviations from
**Dv554**, closed enum v2, `[[wiki-name]]` lessons, five-line Process
signals. Read back first, one line each: the one-attempt gate and its named
multiplicity; what is FROZEN (qlora.yaml · prompt sha · `local_llm.py` ·
gold r2 · base per-row record); the kill-clock rungs in order; the arm-A
milestone STOP; the recovery clause terms; base is never re-run.

## DO NOT

- Never edit: `config/qlora.yaml`, `src/market_pulse/local_llm.py`,
  `src/market_pulse/prompts.py`, gold files/records, pack pages/records
  r1+r2, `docs/labels-pass1-r1.jsonl` + `docs/labels-pass1-r2.jsonl`
  (commit verbatim only) — pinned/sealed; preflight digests equal after.
- Cap $6.00 freezes at the first `pod create`; raising it is the operator's
  word BEFORE any endpoint. One attempt at the gate — a red bar is an
  ANSWER, not a bug to fix in-session.
- Never `git add -A`; never two billing endpoints at once; no serverless.
- Team-lead files (docs/STATUS.md, docs/SPEC.md, docs/PROMPT-*): commit
  verbatim, never edit.
