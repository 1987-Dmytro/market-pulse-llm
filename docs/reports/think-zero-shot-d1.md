# think-zero-shot — D1: the thinking instrument, built and driven at $0

**No pod, $0 spent.** D2 is held for the operator's word — rung 2 projects at a MEASURED s/call this
session does not have, rung 0 reads a price only a create returns — with its four rungs registered
(`prereg_think_zero_shot.json :: money`), cap $8.00 against a cycle-2 remainder of $9.5079, and the
stages, packs and out-files fixed: one command per stage. `think-zero-shot.md` is left for D3.

**Step 0.** `8d40782` commits `docs/STATUS.md` and this contract **by path**; three other team-lead
files sit untracked and were left alone. The first `make check-stamped` came back **VOID**, naming
its cause — `docs/PLAN-harness-gemma4-think.md` landed mid-run — over `6 failed, 3993 passed`. Those
six are **pre-existing**: five grep rulings verbatim out of `docs/STATUS.md`, which the 410 → 118-line
diet deleted, one reads `results/spend_cycle2.json`. Reproduced at HEAD in 14 s before D1 began.

**Closing reading — `make check-stamped`, HEAD `9c29ae0`** — the same six by name and nothing else;
4001 tests before this contract, 4048 now (44 in `tests/test_think_zero_shot.py`, three asserting a
copy guard fires):

    6 failed, 4040 passed, 2 skipped in 717.93s (0:11:57)
    reading HOLDS — HEAD 9c29ae0, tree unmoved outside ['knowledge/daily_logs/', 'knowledge/index.md']

## What landed — `9c29ae0`

- `local_llm.py` — `THINK_CHAT_TEMPLATE`; `chat_template=` on `LocalClient`/`ReaderClient`, default unmoved.
- `prompts.py` — `split_thought` / `after_thought`: the answer is read after the channel closes, every family.
- `reader_v5_pod_runner.py` — `stops_here`: the balanced-object stop never fires inside an open thought.
- both pod runners — `--serving READER_THINK`, a closed template table, out-files carrying the name.
- `build_think_packs.py` — six packs, 579 renderings re-hashed live, nothing carried.
- `write_think_zero_shot_prereg.py` (readings, not bars; every BEFORE number derived) and `measurements.py` (the ledger, `source` required).

`preflight_serving_guards.py` on the REAL template at the pinned revision: all PASS — the channel
renders OPEN, its control says READER and READER_THINK differ, CAPTION and POSITIONS still CLOSED.

## Findings

**1. The transport stop would have stopped inside the thought, and the runner would have persisted
it as the verdict.** `stop_at_balanced` ends generation at the first balanced top-level object and
`run()` writes `balanced_prefix(emitted)` to disk; a model reasoning about the object it is about to
write puts `{` in its working-out. Both families route through this file, so it was live for every
stage of D2. Fixed by `stops_here` — no channel → the shipped rule; open and unclosed → never stop;
closed → scan only the answer — with both controls. A fake client replaces `generate`, so nothing
D1.3 asks for could see it ([[a_stub_replaces_the_guard_it_should_trigger]]).

**2. `<|channel>` and `<channel|>` are `special: True` (ids 100, 101).** Every client decoded with
`skip_special_tokens=True`, which erases the boundary and leaves prose with a JSON object somewhere
in it. The thinking path keeps the specials; `thought_tokens` is the INDEX of id 101 in the emitted
ids, never a second tokenization of the decoded string.

**3. Ruling (ф) moves four PINNED files, and the repo already had the manoeuvre.** `prompts.py` is
pinned by 18 result files (7 sealed registrations), `local_llm.py` by 2, `reader_v5_pod_runner.py`
by 2, `pass1_fewshot_pod_runner.py` by 5 — and every `check_instrument` refuses a pack whose parser
sha is not live, *before the model is loaded*. **No sealed record was re-pinned and no shipped pack
rebuilt.** `tests/moved_pins.py`, written when D0.2 moved the same module a generation ago, narrows
each claim: the allowance is computed from which paths carry a live sha, both ways, sealed bytes at
`git show 74f4a81:<path>`. Three copy-guard producers refuse outright by design, so their rebuilds
run under the SEALED pins with the refusal asserted beside them. 42 red, 42 green again.

**4. Three cited numbers, traced.** «16 reference threads → the remaining 63» is **11 + 68**: five
of the 16 (`cases_outside_the_population`) were never in the r2 population and were never bought by
the run this is paired against, so 79 − 16 double-counts them (`reference_split`). The holdout's
**64/100** is not in `docs/reports/pass1-window-r2.md` — it is two reply files, r2's window
answering 88 rows (56 agreed) and r1's the other 12 (8 agreed), disjoint and complete, each row's
thinking request taken from the pack that answered it. And STATUS's «проход-2 97 с/тред» is not the
r2 rate: `pass2_signals_r2_v1.jsonl` over 75 threads reads **23.760 s mean, 135.232 s max** — 97
over-prices the pass-2 stages 4.1×. Four BEFORE rates are now in `results/measurements.jsonl` with
source, n and max ([[a_rate_is_a_property_of_the_pod]]).

## Deviations — enum v2, from Dv844

- **844** `[contract-gap]` **D2 not executed** — rung 2 has no measured s/call, rung 0 no price; everything it needs is staged by sha.
- **845** `[contract-gap]` **The rule went into `_object`, so `parse_pass1` got it too** — dev-200's 87/200 and 136/200 are read by that parser, not `parse_reply`.
- **846** `[verify-gap]` **Two things D1 does not list had to move** or the pod writes half-thoughts: the transport stop and the runner's persistence. Finding 1.
- **847** `[contract-gap]` **`READER_THINK` is a runner-level name, not a `serving.CONFIGS` member** — no HTTP worker serves it, and `settings()` refusing the unknown name is the right guard until one does.
- **848** `[contract-gap]` **The reference leg is 11, the remainder 68**; the holdout column is two files. Finding 4.
- **849** `[contract-gap]` **The ledger was seeded with four BEFORE rates**, derived at $0 with source, n and max — rung 2 needs a prior and the remembered one is 4.1× off (Finding 4).
- **850** `[contract-gap]` **A pack builder was needed** — the moved parser sha makes every shipped pack refuse at the handshake.
- **851** `[verify-gap]` **~20 test files narrowed through `moved_pins`** — nothing added; each allowance derived rather than typed, plus three tests asserting the copy guards FIRE. Finding 3. One of them, `test_pass1_fewshot_packs`, now reads `pass1_dev_pack_think.json` to make its pin claim positive both ways: a contract that moves that pack lands there.
- **852** `[tooling]` **The first stamped reading was VOID** — a team-lead file arrived mid-run; named and re-taken. And the report is `think-zero-shot-d1.md`: D3 registers `think-zero-shot.md` for the paired table.

**Process signal.** The three checks that mattered most cost $0 and needed no GPU — the real
template rendered from the pinned tokenizer here, 579 renderings re-hashed, and `stops_here` driven
on strings; the last of them is the one whose absence would have been found on a billed pod.
