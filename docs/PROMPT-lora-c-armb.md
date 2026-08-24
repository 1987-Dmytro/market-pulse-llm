# PROMPT — `lora-c-armb` (fresh session, ALL $0, Dv from 793)

You are the executor on `market-pulse-llm`. This contract renders ARM B's dataset (the file
`lora-c-run` found missing — Dv786), re-derives the money block for the REAL scope, and probes
A6000 stock read-only. **Everything is $0: no pod, no endpoint, no paid call; the stock probe is
a listing/query and creates NOTHING** (a probe that creates billable resources is not a probe).
Read: `docs/STATUS.md` п. 1 (н) — the operator's ruling and the team lead's two design rulings —
and `docs/reports/lora-c-run.md` §Dv786, §4. **Read-back before step 1:** one line each — the
(н) clauses; the rendering rule below; pass-2 = 2 legs; 666 = 506 + 160; the arm-B class weight
4.1625 = 666/(5·32); the break-even shape of §4.

## Step 0 — baselines; commit list

As always; commits by path, never `-A`: (a) team-lead files verbatim (`docs/PROMPT-lora-c-armb.md`,
`docs/STATUS.md`); (b) step 0.5; (c) producer + tests + `results/pass1_sft_v3_arm_b.jsonl` +
censuses; (d) registration DRAFT v3 + re-derived money block; (e) report
`docs/reports/lora-c-armb.md` + ADR (the rendering ruling — write it as a decision record, the
team lead's ruling quoted); (f) vault tail.

## Step 0.5 — the moving-tree verifier becomes an INSTRUMENT (Dv785 → Dv792, twice)

Add a `make check-stamped` target (or fold into `make check`): stamp `HEAD` +
`git status --porcelain` before and after the suite; if either moved, the target EXITS NON-ZERO
with «reading VOID — the tree moved» and the reading may not be quoted. The Stop-hook exception
(`knowledge/daily_logs/` only) is allowed by an explicit path whitelist, since no test reads it —
carry the grep that proves that beside the whitelist. Every later gate in this contract uses it.

## D1 — arm B's dataset ($0)

**The rendering rule (team-lead ruling, 24.08, registered by this contract and its ADR):** a
synthetic row is rendered as a v3 QUERY by the SAME renderer (`pass1_v3.pass1_messages_gm4_v3`)
against the SAME shared pool of 515, under ALL existing rules — five per-class neighbours from
the pool, the own-thread block (trivially satisfied: `synthetic:*` threads are not in the pool),
and the equality refusal. The pool law already bars synthetic as a NEIGHBOUR; this ruling makes
it a QUERY and nothing else. Target shape identical to real rows: `rationale` BEFORE the label,
same `learn_chars` rule; provenance tag (`synthetic: true`, error class) carried into every row.

Producer: extend `scripts/build_lora_c_data.py` with `--arm-b-out` (its records are DRAFT-pinned,
rebuild them; sealed records untouched). Output `results/pass1_sft_v3_arm_b.jsonl` = **the 506
real rows BYTE-IDENTICAL as a prefix** (assert against `results/pass1_sft_v3_train.jsonl`; a
diff is a STOP) **+ 160 rendered synthetic rows**. Censuses, each printed AND written to a
results file: (1) encode census via `train_qlora_v3.py --census` over all 666 with the real
tokenizer — refused must be 0, print min/median/max/headroom (a synthetic row over 3 072 is a
STOP report, not a drop); (2) `class_weights` on arm B → FIVE classes, `молочный_бренд` =
4.1625; (3) isolation battery: every example id of the 160 ∈ pool-515, zero synthetic ids as
examples anywhere, zero example texts equal to their query, synthetic ∩ E/holdout/gold = 0;
(4) the widest arm-B request vs `PASS1_MAX_INPUT_CHARS`.

## D2 — registration DRAFT v3 + the re-derived money block ($0)

`population.train` names BOTH files with shas; `legs.arm_b` gains its instrument. Money block
re-derived for the REAL scope: **pass-2 = 2 legs (arms only)** — base v2's end-to-end BEFORE is
r2's registered 4/5 · 2 signals, base v3 takes no bar; the derivation quotes this design ruling.
Publish the same two-price table as §4 (charged rates and the sibling measured rates), the fixed
part, and the break-even s/step for 144 steps — **still NO chosen s/step**; the smoke buys it.
Keep `bars` untouched, the attempt unspent, no price keys, DRAFT state (`pod create` still the
freeze). **Stock probe, read-only:** query A6000 availability in the volume's region
(`runpodctl` query/listing only); record the reading with its timestamp and the note that stock
at create-time may differ; if A6000 shows none, list the read-only alternatives' prices WITHOUT
choosing — the card is the operator's word at the cap decision.

## D3 — report ($0)

`docs/reports/lora-c-armb.md`: the censuses as readings, the derivation table the operator will
rule on (cap word comes on THESE numbers), the numeric audit table (zero-session shape as in
lora-c-run §6), Deviations from **Dv793** on enum v2 + the tally grep, five-line Process
signals. STOP for team-lead acceptance.

**DO NOT:** create any billable resource (the probe is read-only); edit team-lead files, sealed
records, `prompts.py`, `pass1_v3.py`, the sealed configs, or `results/pass1_sft_v3_train.jsonl`;
move any label; drop or rewrite a synthetic row (gate-2 verdicts are applied and closed); spend
the registration's attempt; write a chosen s/step anywhere; touch `bars`.
