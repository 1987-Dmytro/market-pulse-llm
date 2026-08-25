# PROMPT — `lora-c-migrate` (fresh session, ONE paid migration step, cap $1.00, Dv from 820)

Ruling (р), `docs/STATUS.md` п. 1: the training line moves to **EU-SE-1, RTX A6000 48 GB,
$0.53/h** — no 48 GB card exists in EU-RO-1 (`docs/reports/lora-c-vramprobe.md` §5). This
contract builds the new datacenter's volume and proves a pod there can load the model. It trains
NOTHING and evaluates NOTHING.

**Read first:** `docs/reports/lora-c-vramprobe.md` §5–§6; `docs/STATUS.md` п. 1 (п)/(р).
**Read-back before step 1:** one line each — the (р) clauses; cap $1.00; the card+price rung
(equality on `RTX A6000` and ≤$0.60/h); what may NEVER be touched (below).

## Step 0 — baselines; commit list

Baselines via `make check-stamped`. Commits by path: team-lead files verbatim
(`docs/PROMPT-lora-c-migrate.md`, `docs/STATUS.md`), step 0.5, the migration registration, the
paid-step artifacts, report `docs/reports/lora-c-migrate.md`, vault tail.

## Step 0.5 ($0) — the two guard `--close` debts + the formatter note

1. Run the guard's `--close` for the r2 session and the vramprobe (the billing walk has had a
   day; if it still refuses, record the refusal — a refusal is a reading).
2. Register the formatter drift as a KNOWN state in the migration record: two files are
   `ruff format`-drifted and `scripts/write_lora_c_prereg.py` is pinned by the FROZEN
   registration's producer sha — **never run `make fmt` repo-wide while that pin lives**; name
   both files. No reformatting in this contract.

## D1 ($0) — the migration registration

`results/prereg_lora_c_migrate.json`, its own record (the FROZEN `results/prereg_lora_c.json`
is untouched — assert its sha `4d5a8f1d34765b4a…` unchanged at every build): datacenter EU-SE-1;
volume 100 GB (parity with `mp-srv2`); card `RTX A6000` at ≤$0.60/h by EQUALITY; rungs — create
refusal (free), boot ssh ≤500 s, **download deadline 2 400 s with liveness 600 s from the last
progress line**, model-load proof deadline 600 s, hard stop 3 600 s at create; cap $1.00 all-in;
teardown rules. A fresh read-only stock check of A6000/EU-SE-1 at issue time goes into the
record with its timestamp.

## D2 — the ONE paid step

Create the volume in EU-SE-1 → create ONE `RTX A6000` pod there (rung 0 grades card AND price by
equality; a refused create is $0 and a STOP report) → mount → download the model weights (59 GB,
`HF_HOME` on the new volume, the pinned revision `842da379…`) → **prove the serve: load the model
to GPU once through the shipped loader, print the load seconds and VRAM** — this is the
deliverable, a volume nobody loaded from is a hope — → stage the repo bundle + the two SFT files
+ the eval/pass-2 packs onto the volume (small) → teardown the POD, deletion proven by listing;
**both volumes listed as the closing state** (`mp-srv2` AND the new one — the old volume is the
project's serving stack and is NOT this contract's to touch). Money by the pod clock at the
observed price; the new volume's rent named separately from the step.

## D3 ($0) — report

Short: the gates table, the load-proof reading (seconds, VRAM), the money, the closing volume
listing, the numeric audit (steps 0, evals 0, adapters 0, attempt UNSPENT, frozen sha unchanged),
Deviations from **Dv820** on enum v2 + tally grep, three-line Process signals. STOP for
acceptance. The r3 contract (arms on A6000 at $0.53 under the r2 cap's remaining $3.24, v3
charged at 9.20) is the NEXT team-lead session's to write — not this one's.

**DO NOT:** touch `results/prereg_lora_c.json`, any pack, any bar, `mp-srv2` (no deletion, no
writes), or team-lead files (commit only); train; evaluate; keep two pods alive at once; exceed
$1.00; leave the pod unpolled past liveness; buy anything after the load proof lands.
