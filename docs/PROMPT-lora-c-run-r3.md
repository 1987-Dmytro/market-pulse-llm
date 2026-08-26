# PROMPT — `lora-c-run r3` (fresh session, ONE paid pod session, cap $7.00, Dv from 837)

You are the executor on `market-pulse-llm`. This contract BUYS the lora-c measurement — the
smoke that prices the step, both adapters, both eval legs, the bars. The registration
`results/prereg_lora_c.json` is **FROZEN** (sha `4d5a8f1d34765b4a…` — assert unchanged at every
gate) and its **ONE attempt is spent by this session's eval legs**. The volume is WARM:
`mp-lora-c` (100 GB, CA-MTL-3) holds the weights at revision `842da379…`, the venv (1.8 GiB)
and the repo checkout at `997a2a2`. Read first: `docs/reports/lora-c-migrate-r2.md` §5 (the venv
path) and §3 (rung 5), `docs/STATUS.md` п. 1 (к)(н)(о)(п)(с)(т), `docs/PROMPT-lora-c-run-r2.md`
amendments 3–4 (the marker census), `docs/reports/lora-c-run-r2.md` §5 (the pod runners).

**Money law (ruling (т), operator 26.08): cap $7.00 all-in for this session's pod.** Charged
rates: pass-1 v3 **9.20 s/call** (never 6.14; v2 leg is already bought), pass-2 **97 s/thread**
at the **bound of 15 threads/leg**, smoke ceiling 6 × 181.5 s. The projection rung is the
governor: a KILL is compliance. Hard stop from the cap at the OBSERVED price via the INEQUALITY
helper (`cap/price×3600 ≥ hard_stop`); at $1.39/h the cap buys 18 129 s — register hard stop
**18 000 s**. Money by the pod clock; the two volumes' rent (~$0.47/day) is named beside, never
inside.

**Read-back before step 1 (refusal gate), one line each:** steps 62/82 (planned 64/84); rows
506/666; E 198 per leg, bases BOUGHT and not re-bought; pass-2 ≤15 threads; ceiling 3 072, max
row 2 975; v3 = 9.20; cap 7.00; bars per (к) — holdout ≥64 (reachable 98/100) AND bar 1 = 5/5
AND bar 3 = 0, ONE attempt per arm, no retry, no tuning after any eval output; base v3 takes no
bar. A mismatch with any registered number is a FINDING — stop and report.

## Step 0 — baselines (`make check-stamped`); commit list

Commits by path, never `-A`: (a) team-lead files verbatim (`docs/PROMPT-lora-c-run-r3.md`,
`docs/STATUS.md`); (b) step 0.5; (c) the sidecar money record + gate script + $0 drives;
(d) the paid session's artifacts under `results/`; (e) scoring + report
`docs/reports/lora-c-run-r3.md` + ADR; (f) vault tail. Team-lead files: commit only.

## Step 0.5 ($0)

1. **Rung 5's invariant becomes «no BLOB grows»** (the migrate-r2 KILL was 40 bytes of HF cache
   bookkeeping — refs/main + zero-byte absence markers; blobs are the weights). Fix the rung
   BEFORE any reading; negative control: a planted blob-growth must still KILL.
2. Route the vramprobe's structurally-refused `--close` into the `money-anchors` backlog note
   (the n=2 lag evidence is in `docs/reports/lora-c-migrate-r2.md` §7); do NOT touch the band.
3. Grep `results/`-reading checkers for remaining `[-1]` selectors over live ledgers (the
   Dv828/829 class) — fix by stamp-selection with a negative control, before this session
   appends new ledger rows.

## D1 ($0) — the sidecar money record and the drives

`results/prereg_lora_c_run_r3.json` — the POST-FREEZE arithmetic lives here, beside the frozen
prereg, never inside it: cap 7.00 (ruling (т) quoted through `quoted()`), rates as above, the
projection-rung formula, hard stop, the rung table. Rungs: 0 price-first equality («≤$1.50/h,
card `A100 PCIe`»); 1 ssh ≤500 s; 2 liveness **600 s from the LAST log line or byte-growth
poll, at every stage**; 3 realised-rate reading after every eval leg (report GO/KILL with the
projection); 4 smoke; 5 projection after smoke and after EVERY leg: spent + remainder at
MEASURED rates ≤ cap → GO, else KILL + pull + teardown + STOP; 6 platform backstop at create;
7 never two billing resources; recovery clause: ONE re-create after a proven deletion (stock
flickers — a refused create is $0; one retry, then STOP). **Drive every gate command and both
refusal branches at $0 on this Mac before the create** (the r2/vramprobe/migrate discipline —
`main()` end to end with a fake client).

## D2 — the ONE paid session (order is law)

1. Create A100 PCIe CA-MTL-3 (rung 0) → boot gate → mount `mp-lora-c`.
2. **Clone the fresh bundle OVER `/workspace/repo` — the SAME path; the venv is an editable
   install bound to it** (a clone to a new directory is the Dv19 shape). Rebuild the venv ONLY
   if `pyproject.toml`'s dependency set moved (price known: 132 s); otherwise prove it with the
   one-line stack print.
3. Load through the shipped loader (~40 s measured) → rung 5 (blob invariant).
4. **The smoke: 6 optimizer steps of arm A's config at 3 072** via `train_qlora_v3.py`.
   `log_every: 5` → expect TWO loss lines (steps 5, 6); the quotable rate is
   `provenance.json::run.seconds_per_step` — the whole loop's wall over its steps; print both,
   never average them. This is the line's FIRST measured s/step at 3 072 — it goes in the
   record verbatim with the smoke's sha.
5. **Projection rung** → GO: continue; KILL: pull everything bought, teardown, STOP report.
6. Arm A (62 steps; save adapter; pull immediately) → **eval A**: pass-1 on E-198 (v3 leg,
   `pass1_v3_pod_runner.py`) + pass-2 pack rebuilt from arm A's out-file
   (`build_lora_c_pass2_pack.py` at the 15 569 ceiling, `pass2_lora_c_pod_runner.py`,
   ≤15 threads) → projection rung.
7. Arm B (82 steps; save; pull) → **eval B** likewise → **the marker census**: the shipped
   `results/lora_c_marker_census_pack.json` — 40 requests, 20 pairs differing in the header
   alone, against ARM B's adapter; report-only, never a bar.
8. Pull every artifact not yet pulled (out-files, loss curves, provenance, ledgers; hash both
   sides) → teardown; deletion proven by listing with BOTH volumes as positive controls.
   Every reply file: hash on pod and Mac. **Never two pods; never leave the pod unpolled past
   rung 2; adapters are never merged.**

## D3 ($0) — scoring and the report

Score from out-files by the SHIPPED scorer (`scorer.reader_comment_agreement` and the pass-2
verdict machinery) — bars per (к), one attempt, per arm; base v3 no bar. Report-only rows: the
`не_наш_рынок → категория_личное` cell (18/52 registered before; E denominators 66 per leg —
print both populations' numbers, never conflate), «our» on holdout, dev-200 as FIT (115/80/5
split; only the 8 «our»-in-E rows are eval readings), gold-14 census (SIXTH look, never a bar),
per-class tables per leg, DROP/doubt tables per pass-2 leg, **A-vs-B with the reachability
caveat** (arm A has ZERO real `молочный_бренд` positives — bar 1 near-unreachable for it by
construction; a RED on A and a RED on B say different things), **the marker-census flip table
as a caveat on arm B's reading**. The four-column paired table (base v2 · base v3 · arm A ·
arm B) on identical instances — the bases from `results/lora_c_base_v2.jsonl` / `_v3.jsonl`.
Report `docs/reports/lora-c-run-r3.md`: gates table, money (pod clock / guard delta / walk —
each named), numeric session audit, the report's own number-checker script driven by the suite,
Deviations from **Dv837** on enum v2 + the tally grep, five-line Process signals.
**STOP — the report goes to a NEW team-lead session for acceptance.**

**DO NOT:** retry a bar or tune anything after seeing any eval output; edit the frozen prereg,
any pack byte, `config/qlora.yaml`, sealed records, `prompts.py`, or team-lead files (commit
only); re-buy the base legs; exceed $7.00 or create a second billing resource; merge adapters;
clone to a new directory; run `make fmt` repo-wide; quote the step-6 loss line as a rate; touch
`mp-srv2`; invent any number a file does not carry.
