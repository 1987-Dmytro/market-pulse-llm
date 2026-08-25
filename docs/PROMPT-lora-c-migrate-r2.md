# PROMPT — `lora-c-migrate r2` (fresh session, ONE paid migration step, cap $1.50, Dv from 829)

Ruling (с), `docs/STATUS.md` п. 1: the training line moves to **CA-MTL-3, A100 PCIe 80 GB,
≤$1.50/h** — a datacenter the volume-create endpoint LISTS as capable (the refusal artifact,
`docs/reports/lora-c-migrate.md` §1) and the one `scripts/runbook_4a.md` §1 itself chose on this
intersection. This contract builds the volume there and proves a pod loads the model from it.
It trains NOTHING and evaluates NOTHING. Execute `docs/PROMPT-lora-c-migrate.md` as the base,
with these amendments (this file wins on conflict):

1. **Target:** datacenter `CA-MTL-3`; volume 100 GB there; card **`A100 PCIe`** by displayName
   EQUALITY, rung-0 rule worded **PRICE-FIRST**: «≤$1.50/h, card A100 PCIe» (Dv825 — a card-first
   wording feeds `first_number` a model number as a price). A refused create is $0 and a STOP.
2. **The money arithmetic, derived not asserted (Dv822/823):** cap **$1.50** all-in → at $1.39/h
   the affordable hard stop is `1.50/1.39×3600 = 3 884 s`; registered hard stop **3 600 s**
   (`cap/price×3600 ≥ hard_stop` — the INEQUALITY helper, driven both ways). Stage bounds must
   SUM inside it: boot 500 + download **1 200** (the runbook measured 240 s for 62 GB — a 2 400 s
   bound was 10× measured and crossed the stop) + **venv build 900 — a NEW rung; no measurement
   of this stage exists in the repo, so this is its first: record the measured seconds in the
   registration for every future plan** + load proof 600 + teardown margin 90 = **3 290 ≤ 3 600**.
   The new volume's first-day rent (~$0.24) is named beside the step, never inside it.
3. **Download liveness by BYTES (Dv824):** growth of `du -sb /workspace/hf` between stamped polls
   (≤120 s apart); a poll with zero growth starts the 600 s liveness clock; `hf download`'s
   CR-progress lines are NOT a liveness signal. The liveness deadline is its own registered
   FIELD, never the second number of a prose rule.
4. **Deliverable unchanged:** model loaded to GPU once through the shipped loader at the pinned
   revision `842da379…` — seconds and VRAM printed and recorded; then stage the repo bundle, both
   SFT files, the eval/pass-2/marker-census packs; teardown proven by listing; **closing state =
   pods `[]`, serverless `[]`, BOTH volumes** (`mp-srv2` untouched — the project's serving stack).
5. Registration `results/prereg_lora_c_migrate_r2.json` (own record; the FROZEN
   `results/prereg_lora_c.json` asserted byte-identical at every build); fresh read-only stock
   check of A100/CA-MTL-3 at issue time, dated. Report `docs/reports/lora-c-migrate-r2.md` —
   short: gates, the load-proof and venv readings, money by the pod clock, closing listing,
   audit, Deviations from **Dv829** + tally, three-line signals. STOP for acceptance. The r3
   contract (smoke on the A100 buys s/step at 3 072 → the operator's cap word on those numbers)
   is the next team-lead session's to write.

**DO NOT:** touch the frozen prereg, packs, bars, `mp-srv2`, or team-lead files (commit only);
train; evaluate; keep two pods alive; exceed $1.50; poll by log lines; run `make fmt` repo-wide
(two drifted files, one pinned by the frozen record's producer sha).
