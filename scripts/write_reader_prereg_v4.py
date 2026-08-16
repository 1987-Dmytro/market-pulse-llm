#!/usr/bin/env python3
"""`results/prereg_reader_probe_v4.json` — the v3 instrument re-cut for a POD, frozen before it.

**The instrument does not move.** Prompt v3, the v3 parser, gold r2 and the same 23 threads:
everything `results/prereg_reader_probe_v3.json` registered about WHAT is measured is copied through
its own producer rather than retyped, and this record imports that producer instead of forking it.
v3 stays frozen as the record of the attempt that was spent.

**Three differences and no others**, each with its own block below:

1. **bar 3 is back over FIVE threads** — v2's `["N2","N3","N4","N5","N6"]` with v2's own
   `excluded_with_cause` for N1, read out of the frozen v2 record rather than retyped. v3's producer
   took every noise id from the gold and the exclusion did not come with it, so v3's bar failed the
   reader for agreeing with the reference (Dv440). The predicate — `bar_three_over_answers`, with its
   denominator and its reachability state — is v3's and stays v3's, imported.
2. **the vocabulary collapse is the BAR, symmetric.** «категория» ≡ «категория_личное» on BOTH sides
   wherever bars 1 and 4 compare `subject_type` — the gold cell and the reader's answer alike. Gold
   r2 stays the gold and the prompt is not touched: the equivalence is a SCORING rule and it is
   registered as one (Dv441).
3. **the money is a pod's** — one rented machine billed for every second it EXISTS, not a worker
   billed per job. That is the whole reason this run is on a pod: v3's serverless boot had no branch
   that could stop it and ate a $0.35 cap before one thread was read
   ([[a_gate_downstream_of_the_spend]]). Here the boot is watched, and what watches it is an
   inequality solved for SECONDS with both of its numbers published.

**The rate is read, not assumed.** `runpodctl gpu list` on the day of the run, EU-RO-1 SECURE, the
datacenter the volume pins. The contract's own worked example prices a killed boot at $0.59/h; the
4090 in EU-RO-1 is **$0.74/h today**, so every figure here is recomputed from the read price and the
contract's $0.12 becomes $0.148 ([[projected_rate_versus_measured_rate]]).

    PYTHONPATH=src python3 scripts/write_reader_prereg_v4.py
    PYTHONPATH=src python3 scripts/write_reader_prereg_v4.py --out /tmp/again.json   # the pair
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import score_reader_probe_b as scoring  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402
import write_reader_prereg_v3 as v3  # noqa: E402

from market_pulse import prompts  # noqa: E402

OUT = REPO_ROOT / "results" / "prereg_reader_probe_v4.json"
SUPERSEDES = REPO_ROOT / "results" / "prereg_reader_probe_v3.json"
V2 = REPO_ROOT / "results" / "prereg_reader_probe_v2.json"
PROBE_B_RUN = REPO_ROOT / "results" / "reader_probe_b_run.json"
CONTRACT = REPO_ROOT / "docs" / "PROMPT-reader-v4.md"

CAP_USD = v3.CAP_USD
"""$0.35 all-in, imported from the registration that carries it — the same cap, a third time."""

NOISE_THREADS_V2 = ["N2", "N3", "N4", "N5", "N6"]
"""Difference 1, pinned as a literal and then CHECKED against the frozen v2 record.

A list read out of v2 would agree with whatever v2 happens to say; a literal that must match it is
the only version of «restored verbatim» that can fail ([[verbatim_quotes_must_be_grepped]])."""

CARD = "NVIDIA GeForce RTX 4090"
CARD_USD_PER_HOUR = 0.74
CARD_READ_AT = "2026-08-16, runpodctl gpu list, EU-RO-1 SECURE, stockStatus Low"
"""The meter. `securePricePerHr` for the card the volume's datacenter can attach — read on the day
and recorded with the reading, because the contract's worked example is priced at $0.59/h and this
is not that number."""

ALTERNATES_TODAY = {
    "NVIDIA RTX PRO 4500 Blackwell": 0.72,
    "NVIDIA RTX PRO 4000 Blackwell": 0.57,
    "NVIDIA L4": 0.49,
}
"""What else EU-RO-1 SECURE offered at ≥24 GB on the day, with its price — recorded so a card
substitution during the run is priced against a reading taken before the money, not during it."""

BOOT_KILL_S = 720.0
"""The contract's twelve minutes: if the FIRST parsed-or-refused reply has not landed within this
many seconds of the generation process starting, the pod is killed and the run STOPS."""

DELETE_MARGIN_S = 60.0
"""Seconds held back from the cap for the deletion itself. A pod killed at exactly the second the cap
buys has already spent the cap: the meter runs until the machine is gone, and `pod delete` is a call
with a latency ([[the_setup_is_inside_the_cap]])."""

TERMINATE_AFTER_MIN = 90
"""The runaway backstop passed at create. It is NOT a cap guard — 90 minutes at this rate is $1.11,
three times the cap — it is what deletes the pod if this Mac dies mid-run."""

BOOT_TABLE_S = (180.0, 300.0, 480.0, 600.0, 720.0)
"""Boots to publish the arithmetic at. Three are on record for this stack and they disagree by 6.7x
(probe-a 373 s, probe-b 179 s, reader-v3 >1 200 s), so a single expected boot would be a forecast
dressed as a bound ([[a_price_is_as_representative_as_its_sample]])."""


def probe_b_reading() -> dict:
    """What reading these same 23 threads cost probe-b, re-summed from ITS rows.

    Both legs, because they are different quantities and the pod meter only measures one of them:
    `worker` is generation, `wall` is generation plus the queue and the HTTP round trip a serverless
    job carries. A pod has no queue — the generation loop is contiguous — so the analogue of a pod
    second is the WORKER second, and taking the larger figure here would not be pessimism but a unit
    error ([[a_published_ratio_is_not_the_gates]]).
    """
    rows = [
        json.loads(line)
        for line in (REPO_ROOT / "results" / "reader_probe_b_w1.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line
    ]
    worker = round(sum(row["seconds"]["worker"] for row in rows), 3)
    return {
        "threads": len(rows),
        "payable_comments": sum(row["payable_comments"] for row in rows),
        "worker_seconds": worker,
        "wall_seconds": round(sum(row["seconds"]["wall"] for row in rows), 3),
        "seconds_per_thread": round(worker / len(rows), 4),
        "gpu": "RTX 4090 (ADA_24), endpoint "
        + json.loads(PROBE_B_RUN.read_text(encoding="utf-8"))["endpoint"],
    }


def money() -> dict:
    """The pod's arithmetic — the cap in SECONDS, and every leg that spends them.

    A pod bills for existing. That makes the cap a stopwatch rather than a bill to be added up
    afterwards, and it is the one thing the serverless version of this run could not say: v3's gates
    all sat downstream of a boot that was already spending.
    """
    rate = CARD_USD_PER_HOUR / 3600.0
    cap_seconds = CAP_USD / rate
    usable = cap_seconds - DELETE_MARGIN_S
    reading = probe_b_reading()
    floor = float(reading["worker_seconds"])
    pre_generation = usable - BOOT_KILL_S - floor
    return {
        "cap_usd_all_in": CAP_USD,
        "line": (
            "the CYCLE-2 line of SPEC amendment 3.23 (1), $20.00, anchored 2026-08-16T12:14:48Z in"
            " results/spend_cycle2.json. $0.4422 of it is spent (reader-v3's closed step $0.3936 and"
            " the volume's rent), so $19.5578 remains and this cap is 1.8% of it"
        ),
        "guard": (
            "scripts/runpod_guard.py --step reader-v4 --step-cap 0.35, anchored BEFORE the pod is"
            " created and read from the guard, never from a ledger line or a sentence in a contract"
        ),
        "meter": {
            "resource": (
                "ONE rented pod, billed for every second it EXISTS — from `pod create` to `pod"
                " delete`, whether it is provisioning, booting, generating or idle. Not per job:"
                " there is no job. `pod stop` does not stop the bill, the disk keeps billing, so the"
                " run deletes and never stops"
            ),
            "card_requested": CARD,
            "usd_per_hour": CARD_USD_PER_HOUR,
            "usd_per_second": round(rate, 9),
            "read_at": CARD_READ_AT,
            "datacenter": "EU-RO-1, pinned by network volume qw4nwleanc — the volume decides",
            "alternates_offered_the_same_day": ALTERNATES_TODAY,
            "price_rule": (
                "`costPerHr` in the create response is the meter of record. If it differs from the"
                " price above, every number in this block is recomputed from IT before the"
                " generation process starts, and a projection that no longer fits deletes the pod"
                " and STOPS. A card other than the 4090 also ends the paired seconds comparison with"
                " probe-b, which ran on a 4090 — the pairing is on the card as well as on the data,"
                " and a cross-card column is labelled rather than aligned"
            ),
            "the_contracts_own_example": (
                "the contract prices a killed boot at «≈ $0.12 at $0.59/h». The 4090 in EU-RO-1 reads"
                f" ${CARD_USD_PER_HOUR:.2f}/h today, so the same 12 minutes is"
                f" ${BOOT_KILL_S * rate:.4f} — recomputed rather than carried over"
            ),
        },
        "arithmetic": {
            "seconds_the_cap_buys": round(cap_seconds, 3),
            "delete_margin_seconds": DELETE_MARGIN_S,
            "usable_seconds": round(usable, 3),
            "usable_rule": (
                "the cap in seconds minus the deletion's own margin. Every deadline below is against"
                " THIS number, so the `pod delete` that ends the run is inside the cap and not"
                " charged to the next contract"
            ),
            "reading_projection_seconds": floor,
            "reading_projection_rule": (
                f"probe-b's own {reading['threads']} threads on a 4090:"
                f" {reading['worker_seconds']} billed WORKER seconds, {reading['seconds_per_thread']}"
                f" a thread. Its {reading['wall_seconds']} s wall leg is recorded beside it and is"
                " NOT the projection: wall carries the serverless queue and the HTTP round trip,"
                " which a pod's contiguous generation loop does not have. This is a FLOOR either"
                " way — v3's prompt asks for a per_comment row for EVERY comment shown, so these"
                " threads owe more output than probe-b paid for"
            ),
            "probe_b": reading,
            "boot_kill_seconds": BOOT_KILL_S,
            "boot_kill_usd": round(BOOT_KILL_S * rate, 4),
            "boot_deadline_rule": (
                "min(boot_kill_seconds, usable_seconds − seconds already elapsed since `pod create` −"
                " reading_projection_seconds). The contract's twelve minutes is a CEILING; what"
                " binds is whichever of the two comes first, because a boot that runs past the point"
                " where the remaining 23 threads no longer fit is spending on a pass that must stop"
                " anyway. Both numbers are printed at the gate and both land in the run record"
            ),
            "pre_generation_budget_seconds": round(pre_generation, 3),
            "pre_generation_rule": (
                "the seconds between `pod create` and the generation process's first line —"
                " provisioning, ssh readiness, the pack's scp, the sha checks — that leave the full"
                " twelve-minute boot allowance intact. Over it the boot deadline shrinks second for"
                " second by the rule above; it is not a separate kill"
            ),
            "at_each_boot": [
                {
                    "boot_seconds": boot,
                    "seconds_left_for_reading": round(usable - pre_generation - boot, 1),
                    "slowdown_vs_probe_b_that_fits": round(
                        (usable - pre_generation - boot) / floor, 3
                    ),
                    "all_in_usd_at_probe_bs_rate": round((pre_generation + boot + floor) * rate, 4),
                }
                for boot in BOOT_TABLE_S
            ],
            "at_each_boot_rule": (
                "computed at the pre-generation budget above, so the row for 720 s is the corner"
                " where the twelve-minute ceiling and the affordability deadline meet and the"
                " slowdown that fits is 1.000. Three boots are on record for this stack and they"
                " disagree by 6.7x — probe-a 373 s, probe-b 179 s, reader-v3 over 1 200 s — so what"
                " is registered is the table and not a forecast"
            ),
            "what_a_stop_costs": (
                "whatever the pod has existed for when it is killed. A boot killed at the ceiling is"
                f" ${(BOOT_KILL_S + pre_generation) * rate:.4f} with the pre-generation budget"
                " inside it; a STOP at the first reply's gate is that plus the one thread that"
                " measured it"
            ),
        },
    }


def go_no_go() -> dict:
    """Three gates, each on the step that is spending WHILE it spends.

    v3's registration put its only gate after a warm-up that a boot never reached. The lesson it
    bought is not «measure earlier», it is that a gate has to sit on the resource that is running:
    the pod's clock starts at `create` and every deadline here is read against seconds since that
    stamp ([[a_gate_downstream_of_the_spend]]).
    """
    return {
        "clock": (
            "seconds since the `pod create` response, which is when the meter starts. Not since ssh"
            " came up, not since the model began loading — the machine is billed for provisioning"
            " too, and a clock that starts later prices a leg at zero"
        ),
        "gates": {
            "1_staging": {
                "expected_usd": 0.0,
                "rule": (
                    "the volume is already staged at reader-v3's HEAD and `src/` has not moved"
                    " since: the run VERIFIES the three reader prompt shas and the parser module's"
                    " sha on the pod, and re-stages only if one has moved. A verification that fails"
                    " deletes the pod and STOPS — a volume a session behind reads happily under the"
                    " wrong text"
                ),
            },
            "2_boot_kill": {
                "rule": (
                    "if the FIRST parsed-or-refused reply has not landed by the boot deadline, KILL"
                    " the pod and STOP. The deadline is min(720 s, usable − elapsed − reading"
                    " projection) and BOTH numbers are printed when it is set"
                ),
                "watched": (
                    "the generation process is tailed live and unbuffered. A deadline nobody can see"
                    " pass is a deadline that is discovered afterwards, in a bill"
                ),
            },
            "3_the_full_pass": {
                "rule": (
                    "at the first reply, project the UNREAD remainder two ways and let the"
                    " PESSIMISTIC one bind: elapsed_since_create + max(unread threads ÷ read"
                    " threads, unread payable comments ÷ read payable comments) × the seconds"
                    " measured so far ≤ usable_seconds. Over it, KILL and STOP — a partial pass"
                    " scores no bar at all (every bar's state is UNSCORED unless every registered"
                    " thread was read), so continuing spends the rest of the cap for nothing"
                ),
                "binding": (
                    "probe-a's and probe-b's rule and v3's, kept: BOTH projections are computed and"
                    " the larger decides. v3's own registration carries it word for word — «the"
                    " pessimistic of the per-thread and per-payable-comment projections» — and a"
                    " single-leg projection is looser in the direction that opens runs, which is the"
                    " one direction a cap guard may not be loose in. This population's threads carry"
                    " between 1 and 15 payable comments and v3 asks for an output row per comment,"
                    " so which leg binds depends on which threads have been read"
                ),
                "solved_for_seconds": (
                    "seconds_per_thread_that_still_fits = (usable_seconds − elapsed) ÷ (binding"
                    " factor × threads read), printed beside the measured figure. The verdict"
                    " re-derives from that pair and never from the dollars, which round to four"
                    " decimals and agree on both sides of a margin"
                    " ([[a_record_must_rederive_from_what_it_publishes]])"
                ),
                "re_checked_after_every_thread": (
                    "the same inequality over the threads still unread. It cannot open anything —"
                    " the run is already open — and what it does is delete the pod before the cap is"
                    " reached rather than after"
                ),
            },
        },
        "backstop": {
            "terminate_after_minutes": TERMINATE_AFTER_MIN,
            "rule": (
                "passed at create. It is NOT a cap guard: 90 minutes at this rate is"
                f" ${TERMINATE_AFTER_MIN * 60 * CARD_USD_PER_HOUR / 3600:.2f}, three caps. It is what"
                " deletes the pod if this Mac dies with the run open"
            ),
        },
        "stop_rule": (
            "a kill or a STOP closes the question. The attempt stays intact, the measured seconds"
            " and the card they were measured on go back to the operator, whatever rows were read"
            " are brought back and scored as far as they reach, and no bar is scored on a partial"
            " pass"
        ),
    }


def bar_three() -> dict:
    """Difference 1 — five threads, v2's exclusion restored, v3's predicate untouched."""
    v2 = json.loads(summary.read_text_or_refuse(V2))["bars"]["3_noise"]
    if list(v2["scored_over"]) != NOISE_THREADS_V2:
        raise SystemExit(
            f"v2 registered {v2['scored_over']} and this record restores {NOISE_THREADS_V2}."
            " «Restored verbatim» is a claim about the frozen file — stop and report."
        )
    return {
        "threshold": "0 signals",
        "scorer": "reader_noise_count",
        "scored_over": list(NOISE_THREADS_V2),
        "excluded_with_cause": dict(v2["excluded_with_cause"]),
        "excluded_rule": (
            "read out of results/prereg_reader_probe_v2.json, the frozen record that states it, and"
            " checked against a literal in this producer. v3 took every noise id from the gold and"
            " the exclusion did not come with it, so its bar scored the reader on a thread whose"
            " signal the reference itself asserts (S1, msg 21420) — a bar that fails the reader for"
            " agreeing with the reference measures nothing. Dv440, closed by the team lead"
        ),
        "n3_is_not_a_discriminating_case": v2["n3_is_not_a_discriminating_case"],
        "n3_rule": (
            "carried from v2 as well, because it belongs to this population: N3's «0 signals» is"
            " produced by the gate's plus-spam silencer and not by the reader, so of the five"
            " threads FOUR can move this bar. v3's registration lost this note with the exclusion"
        ),
        "rule": (
            "zero signals in the verdicts of the reference's noise threads — counted over the"
            " threads that HAVE a parsed verdict. A refused reply contributes nothing and is NEVER a"
            " zero; with no parsed verdict among them the bar is UNREACHABLE, which is not a pass"
        ),
        "producer": (
            "scripts/write_reader_prereg_v3.py::bar_three_over_answers — v3's own reference"
            " implementation, IMPORTED and not re-stated. The population changed and the predicate"
            " did not, and two copies of a registered predicate are two predicates"
        ),
        "result_must_carry": [
            "threads_registered",
            "threads_with_a_verdict",
            "threads_refused",
            "signals",
            "reachable",
            "passed",
        ],
    }


def vocabulary_collapse() -> dict:
    """Difference 2 — the collapse promoted from a column beside the bar to the bar itself."""
    return {
        "map": dict(scoring.COLLAPSE),
        "symmetric": True,
        "applies_to": ["1_flagships", "4_per_comment_agreement"],
        "rule": (
            "wherever a bar compares `subject_type`, BOTH sides pass through the map before the"
            " comparison — the gold cell and the reader's answer alike. «категория» and"
            " «категория_личное» are ONE class, so neither direction of that disagreement is an"
            " error and neither direction is scored as one"
        ),
        "authority": (
            "the reader sitting of 2026-08-16, ruling 4, as adjudicated by the team lead in"
            " docs/PROMPT-reader-v4.md: the two words are one class. Dv441, closed"
        ),
        "why_a_scoring_rule_and_not_a_gold_edit": (
            "gold r2 already IS ruling 4 applied to twelve cells — it moved them to"
            " «категория_личное». What r2 could not do is make the other direction safe: the v3"
            " prompt still offers BOTH words in prompts.READER_SUBJECT_TYPES, so a reader answering"
            " the reference's word is scored wrong against the ratified one. Moving the gold again"
            " would break every record sealed against it and moving the prompt would swap the"
            " instrument mid-registration ([[a_prompt_revision_is_an_instrument_swap]]). The"
            " equivalence belongs where the comparison happens"
        ),
        "producer": (
            "scripts/score_reader_probe_b.py::collapse, applied by flagships(collapsed=True) and"
            " per_comment(collapsed=True) — the same two functions probe-b reported the collapsed"
            " reading with. What changes is which column is the bar"
        ),
        "reported_beside_it": (
            "the UNCOLLAPSED reading of both bars, for continuity with v3's registration and"
            " probe-b's verdict, labelled and gating nothing"
        ),
        "subject_types_the_prompt_offers": list(prompts.READER_SUBJECT_TYPES),
    }


def bars(gold: dict) -> dict:
    """v3's bars, with bar 3 re-cut and the collapse named on the two bars it touches."""
    table = v3.bars(gold)
    table["3_noise"] = bar_three()
    for name in ("1_flagships", "4_per_comment_agreement"):
        table[name] = table[name] | {
            "scoring_rule": (
                "the vocabulary collapse applies, symmetrically — see"
                " `scoring_rules.vocabulary_collapse`. The threshold itself is unchanged"
            )
        }
    return table


def build() -> dict:
    gold = json.loads(summary.read_text_or_refuse(v3.GOLD_R2))
    older = json.loads(summary.read_text_or_refuse(SUPERSEDES))
    record = {
        "phase": "reader-v4",
        "contract": "docs/PROMPT-reader-v4.md D1",
        "class": (
            "PRE-REGISTRATION. Committed before the pod exists; git history is the only witness that"
            " it preceded the money. It FREEZES when the pod exists and nothing after that may edit"
            " it — a registration a run may amend is a registration the run wrote"
        ),
        "attempt": (
            "ONE attempt, no retry. A kill or a STOP closes the question, and so does a completed"
            " run with a failed bar: what follows is a new registration after a sitting, never a"
            " second pass at this one"
        ),
        "supersedes": {
            "record": summary.rel(SUPERSEDES),
            "sha256": summary.sha256_of(SUPERSEDES),
            "state": (
                "v3 stays FROZEN and is not withdrawn: it is the record of the attempt that was"
                " spent, and results/spend_reader_v3.json closed against it at $0.3936"
            ),
            "ruling": (
                "the operator, 2026-08-16, after reader-v3-run: no serverless. On a pod the boot is"
                " watched and killable"
            ),
            "what_it_changes": [
                "bar 3 is back over v2's five noise threads with v2's exclusion of N1 (Dv440)",
                "the vocabulary collapse is the BAR and it is symmetric (Dv441)",
                "the money is a pod's — a stopwatch from `pod create`, with a kill rule on the boot",
            ],
            "what_it_keeps": (
                "the v3 prompt, the v3 parser, gold r2, the population digest, the five thresholds,"
                " the serving configuration, the $0.35 cap and the scorer's bytes. Everything that"
                " could make the two runs incomparable is held still on purpose"
            ),
            "no_ablation": older["supersedes"]["no_ablation"],
        },
        "authority": {
            summary.rel(path): summary.sha256_of(path)
            for path in (
                v3.PLAN,
                CONTRACT,
                v3.REFERENCE,
                SUPERSEDES,
                V2,
                v3.GOLD_R2,
                v3.CENSUS_CELL,
            )
        },
        "instruments": older["instruments"],
        "instruments_rule": (
            "copied WHOLE from the v3 registration — the task, the three prompt shas, the parser's"
            " stated behaviour, the scorer's bytes, the gold, the ceilings and the serving block."
            " Not a single field is re-derived here: v4 measures the same instrument on the same"
            " population and a re-derivation is where the two would silently part"
        ),
        "population": v3.population_block(),
        "money": money(),
        "go_no_go": go_no_go(),
        "bars": bars(gold),
        "scoring_rules": {"vocabulary_collapse": vocabulary_collapse()},
        "transport": {
            "shape": (
                "the generation runs ON the pod and nothing else does. The 23 rendered requests"
                " travel as a pack whose every entry is checked against this record's per-thread"
                " `rendering_sha256` on the Mac before it is sent and again on the pod before the"
                " model is loaded; the on-pod runner loads the READER config once and answers them"
                " in order, flushing a raw reply per line as each lands; parsing and scoring happen"
                " on the Mac, under the v3 parser"
            ),
            "why_the_split": (
                "the parser and the scorer are the instrument and they are pinned by sha in this"
                " record. Running them on a machine whose checkout is a commit behind would score"
                " the run with an instrument nobody registered — and the pod's checkout IS a commit"
                " behind, deliberately: staging it again costs money this cap does not have"
            ),
            "persisted_per_row": [
                "the rendered request and its sha256",
                "the raw reply, byte for byte",
                "the parse outcome — the verdict with its `repairs`, or the refusal's reason",
                "seconds, `finish_reason` and the token usage",
            ],
            "flush_rule": (
                "one line per reply, flushed as it lands, on the pod AND on the Mac. A killed run"
                " must still show what it read: the partial file is copied back before the pod is"
                " deleted, and a row that exists only in an aggregate cannot be shown to the"
                " operator afterwards"
            ),
        },
        "frozen_when_the_pod_exists": [
            "results/prereg_reader_probe_v4.json",
            summary.rel(v3.GOLD_R2),
            summary.rel(v3.CENSUS_CELL),
            summary.rel(SUPERSEDES),
            f"the {prompts.READER_TASK_V3} prompt text",
            "src/market_pulse/prompts.py — the parser",
            "src/market_pulse/scorer.py",
            "scripts/probe_b_population.py's enumeration",
        ],
        "non_gating": older["non_gating"],
        "producer": {
            "script": summary.rel(Path(__file__)),
            "sha256": summary.sha256_of(Path(__file__)),
            "borrowed": {
                name: summary.sha256_of(REPO_ROOT / name)
                for name in (
                    "scripts/probe_b_population.py",
                    "scripts/score_reader_probe_b.py",
                    "scripts/window_summary_5c2.py",
                    "scripts/write_reader_prereg_v2.py",
                    "scripts/write_reader_prereg_v3.py",
                    "src/market_pulse/prompts.py",
                    "src/market_pulse/scorer.py",
                )
            },
        },
    }
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    record = build()
    args.out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {summary.rel(args.out)}  sha256 {summary.sha256_of(args.out)[:16]}…")
    pop = record["population"]
    print(
        f"  population {pop['threads']} threads · {pop['payable_comments']} payable ·"
        f" digest {pop['enumeration']['digest'][:16]}…"
    )
    sums = record["money"]["arithmetic"]
    meter = record["money"]["meter"]
    print(
        f"  meter {meter['card_requested']} ${meter['usd_per_hour']:.2f}/h ="
        f" ${meter['usd_per_second']:.8f}/s  ({meter['read_at']})"
    )
    print(
        f"  cap ${CAP_USD:.2f} buys {sums['seconds_the_cap_buys']:.1f} s ·"
        f" usable {sums['usable_seconds']:.1f} s after the delete margin"
    )
    print(
        f"  reading floor {sums['reading_projection_seconds']:.1f} s ·"
        f" boot kill {sums['boot_kill_seconds']:.0f} s (${sums['boot_kill_usd']:.4f}) ·"
        f" pre-generation budget {sums['pre_generation_budget_seconds']:.1f} s"
    )
    for row in sums["at_each_boot"]:
        print(
            f"    boot {row['boot_seconds']:6.0f} s -> {row['seconds_left_for_reading']:7.1f} s for"
            f" reading ({row['slowdown_vs_probe_b_that_fits']:.3f}x probe-b),"
            f" all-in ${row['all_in_usd_at_probe_bs_rate']:.4f}"
        )
    print(f"  bar 3 over {record['bars']['3_noise']['scored_over']}")
    print(f"  excluded with cause: {sorted(record['bars']['3_noise']['excluded_with_cause'])}")
    collapse = record["scoring_rules"]["vocabulary_collapse"]
    print(f"  collapse {collapse['map']} — the BAR on {collapse['applies_to']}, symmetric")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
