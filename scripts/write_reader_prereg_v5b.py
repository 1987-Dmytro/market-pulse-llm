#!/usr/bin/env python3
"""`results/prereg_reader_probe_v5b.json` — the same instrument, a transport that survives a dead pod.

**The instrument does not move, and that is CHECKED rather than claimed.** This producer CALLS
`write_reader_prereg_v5.build()` (Dv451's idiom, a generation later) and refuses unless it rebuilds
v5's own frozen record byte for byte. Everything the reader is scored on — the v5 task, the four
prompt texts, the parser, gold r2, the population digest, the 4 000-token ceiling, the collapse, N1's
exclusion, the echo duty, bars 1-4 and leg B's four mechanical bars — is therefore object-equal to
the frozen record BY CONSTRUCTION, and the keys this file overrides are the whole diff.

**Three TRANSPORT differences, all of them operator rulings of 2026-08-17** after a pod was billed
727.9 s and never answered `ssh info` once:

1. **The cap is $0.50.** v5's $0.45 bought 2 189.2 usable seconds against a 1 454.0 s reading
   projection, so its `pre_generation_budget_seconds` was NEGATIVE (−44.785) and there was no slack
   to pay for provisioning. Every derived second here is recomputed by v5's OWN `money()` under the
   new cap, not re-spelled: the producer self-pins its sha inside the frozen record, so it cannot
   grow a parameter and the cap is swapped around the call instead.
2. **Transport gate-0, an ssh dead-man at 180 s of segment-elapsed,** with at most two recreates.
   A third dead pod is a datacenter state and a STOP.
3. **The pack order: leg A by DESCENDING payable count, then leg B's chunks 1→3.** Same 26 units,
   same 26 rendering shas, and the order is registered with its TIEBREAK — six of the leg-A payable
   counts are shared by two or three threads, so `-payable` alone is not a total order and the pack
   would differ between two builds of one registration.

**The full-pass gate is re-solved backwards over the registered order and PUBLISHED here**, at v4's
own measured seconds times this registration's own growth factor. It is reported and gates nothing —
but it is in the record because a knife-edge nobody named before the money is a knife-edge that gets
discovered in a log.

    PYTHONPATH=src python3.11 scripts/write_reader_prereg_v5b.py
    PYTHONPATH=src python3.11 scripts/write_reader_prereg_v5b.py --out /tmp/again.json   # the pair
"""

import argparse
import json
import sys
from contextlib import contextmanager
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import read_threads_reader_v5 as driver  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402
import write_reader_prereg_v3 as v3  # noqa: E402
import write_reader_prereg_v5 as v5writer  # noqa: E402

OUT = REPO_ROOT / "results" / "prereg_reader_probe_v5b.json"
SUPERSEDES = REPO_ROOT / "results" / "prereg_reader_probe_v5.json"
CONTRACT = REPO_ROOT / "docs" / "PROMPT-reader-v5b.md"
V5_RUN = REPO_ROOT / "results" / "reader_v5_run.json"
PACK = REPO_ROOT / "results" / "reader_v5b_pack.json"

PHASE = "reader-v5b"
CAP_USD = 0.50
"""The operator's ruling of 2026-08-17, at the sitting after the pod that never answered. v5's $0.45
had no slack for provisioning: its pre-generation budget was −44.785 s, which said the affordability
deadline bound from the first second. The raise buys about fifteen minutes of it."""

SSH_DEADMAN_S = 180.0
MAX_RECREATES = 2
"""Transport gate-0 and its ceiling, both the operator's ruling. reader-v5's pod was RUNNING and
unreachable for 727.9 s across ~150 polls; v4's answered in 17. 180 s is over ten times v4's and it
is a transport bar, not a boot bar — what it measures is whether the endpoint exists at all."""


@contextmanager
def capped_at(cap: float):
    """v5's `CAP_USD`, swapped for the length of one call and put back.

    `scripts/write_reader_prereg_v5.py` hashes ITSELF into the record it writes (`producer.sha256`)
    and that record is frozen, so the function cannot grow a `cap` parameter without invalidating the
    registration it produced. Swapping the module constant around the call is the one way to reuse
    the arithmetic rather than write a second spelling of it — and a second spelling of a cap
    computation is exactly the drift a paired run cannot afford.
    """
    was = v5writer.CAP_USD
    v5writer.CAP_USD = cap
    try:
        yield
    finally:
        v5writer.CAP_USD = was


def order_key(thread: dict) -> tuple[int, str]:
    """`(-payable, thread id)`. The tiebreak is half the rule, not a detail.

    Six payable counts are shared: 12 by three threads, 9/5/4/3/2 by two or more. A sort on the count
    alone leaves those ties to whatever order the enumeration happened to be in, which makes «the
    pack is in descending payable order» unverifiable and the pack itself unreproducible
    ([[an_order_key_that_is_not_total]]).
    """
    return (-int(thread["payable_comments"]), str(thread["thread"]))


def withdrawn_order(leg_a: dict) -> dict:
    """Leg A re-ordered the way the ruling of 2026-08-17 said, so its gate table can be published.

    Nothing is built from this: it exists to be MEASURED. The population digest is computed from the
    STORE and not from this list, so a re-ordering cannot move it — which is what made the order a
    thing the registration could change without touching the pairing.
    """
    return leg_a | {
        "enumeration": leg_a["enumeration"]
        | {"threads": sorted(leg_a["enumeration"]["threads"], key=order_key)}
    }


def registered_order(leg_a: dict) -> dict:
    """v5's enumeration order, UNCHANGED — and the ruling that was withdrawn, with its number.

    The order ruling of 2026-08-17 was «leg A by descending payable comments». This producer solved
    the registered full-pass gate backwards over it before anything was created and it STOPs after the
    FIRST unit; the operator withdrew the order ruling the same day, on that measurement, with the cap
    and gate 0 standing. Both tables are published in `money.arithmetic` — the withdrawal's evidence
    belongs in the record that the withdrawal changed, not only in a report.
    """
    threads = leg_a["enumeration"]["threads"]
    counts = [one["payable_comments"] for one in threads]
    ties = sorted(
        {one["payable_comments"] for one in threads if counts.count(one["payable_comments"]) > 1},
        reverse=True,
    )
    return leg_a | {
        "order": [one["thread"] for one in threads],
        "order_rule": (
            "v5's enumeration order, UNCHANGED — the order this population has been read in since"
            " probe-b. The 23 threads, their 23 rendering shas, the population digest and their"
            " SEQUENCE are all v5's own"
        ),
        "order_withdrawn": {
            "ruled": "leg A by DESCENDING payable comments, ties by thread id ascending",
            "ruled_on": "2026-08-17",
            "withdrawn_on": "2026-08-17, on the measurement below, before any pod of this attempt",
            "why_it_was_ruled": (
                "v5's second unit carried 2 payable comments against a first with 7, so the"
                " projection's payable leg extrapolated 168 comments off 9 and left 9% of margin at"
                " unit 2 (Dv471). Reading the payable-dense threads first was the answer to that leg"
            ),
            "why_it_was_withdrawn": (
                "the gate has TWO legs and they pull opposite ways. The by-UNIT leg extrapolates the"
                " 25 unread units off whatever the FIRST reply cost, and descending payable puts the"
                " second-slowest thread v4 measured in that position: 105.3 s expected against 82.1 s"
                " allowed, a STOP after one unit. See"
                " `money.arithmetic.full_pass_over_the_withdrawn_order`"
            ),
            "what_removed_the_knife_edge_instead": (
                "the cap raise on its own. At $0.50 and this order, unit 2's margin is +12.9 s a unit"
                " — 23% where $0.45 left 9% — and no unit of the 26 fails"
            ),
            "the_tiebreak_it_would_have_needed": (
                f"`(-payable_comments, thread_id)`. Payable counts {ties} are each shared by two or"
                " three threads, so «descending payable» is not a total order on this population and"
                " two builds of one registration could have produced two packs"
                " ([[an_order_key_that_is_not_total]])"
            ),
        },
    }


def gate_table(record: dict, leg_a: dict, leg_b: dict) -> dict:
    """The registered full-pass gate, solved BACKWARDS over the registered order, before any money.

    Run through `read_threads_reader_v5.projection` itself — the function the live gate calls — over
    synthetic rows whose seconds are v4's OWN measurement on the same 23 threads times this
    registration's growth factor, and leg B's chunks at the registration's own per-chunk projection.
    Dv471's method, at the order and the cap that are being registered here.

    REPORTED and gating nothing. What it is for: the first gate fires after the FIRST reply, and
    there the by-unit leg extrapolates 25 unread units off whatever the first unit cost — so the
    order decides which unit that is, and the answer is arithmetic and free to have today.
    """
    sums = record["money"]["arithmetic"]
    rate = v5writer.CARD_USD_PER_HOUR_EXAMPLE / 3600.0
    growth = float(sums["leg_a"]["growth_vs_v4"])
    per_chunk = float(sums["leg_b"]["projection_seconds"]) / len(leg_b["chunks"])
    measured = {row["thread"]: row["seconds"]["worker"] for row in v5writer.v4_rows()}
    boots = {row["boot_seconds"] for row in v5writer.v4_rows()}
    start = v5writer.V4_PRE_GENERATION_S + max(boots)

    units = [
        (one["thread"], one["payable_comments"], measured[one["thread"]] * growth, "A")
        for one in leg_a["enumeration"]["threads"]
    ] + [(one["id"], len(one["msg_ids"]), per_chunk, "B") for one in leg_b["items"]]
    pack = {
        "phase": PHASE,
        "items": [
            {"id": unit, "payable_comments": payable, "leg": leg} for unit, payable, _, leg in units
        ],
    }

    rows, elapsed, table = [], start, []
    for index, (unit, payable, seconds, _) in enumerate(units, start=1):
        elapsed += seconds
        rows.append({"id": unit, "seconds": seconds})
        gate = driver.projection(record, rate, rows, elapsed, pack)
        table.append(
            {
                "after_units": index,
                "unit": unit,
                "payable_comments": payable,
                "expected_seconds": round(seconds, 1),
                "mean_seconds_per_unit": gate["measured_seconds_per_unit"],
                "binding": gate["projections"]["binding"]["which"],
                "factor": gate["projections"]["binding"]["factor"],
                "seconds_per_unit_that_still_fits": gate["seconds_per_unit_that_still_fits"],
                "headroom_seconds": gate["headroom_seconds"],
                "verdict": gate["verdict"],
            }
        )
    stops = [one["after_units"] for one in table if one["verdict"] == "STOP"]
    tight = min(
        table,
        key=lambda one: one["seconds_per_unit_that_still_fits"] - one["mean_seconds_per_unit"],
    )
    usable = driver.usable_seconds(record, rate)
    first = units[0]
    return {
        "method": (
            "`read_threads_reader_v5.projection` — the live gate's own function — over synthetic rows"
            " at v4's measured seconds x this registration's growth factor"
            f" ({growth}), leg B's chunks at {round(per_chunk, 1)} s each, starting from"
            f" {round(start, 1)} s of create-elapsed (v4's own measured pre-generation"
            f" {v5writer.V4_PRE_GENERATION_S} s + its measured boot {max(boots)} s)"
        ),
        "reported_not_gating": (
            "a FORECAST at v4's rate and not a threshold. The gate itself compares MEASURED seconds"
            " and is the law in `go_no_go.gates.3_the_full_pass`"
        ),
        "rows": table,
        "first_stop_after_units": stops[0] if stops else None,
        "tightest_margin": {
            "after_units": tight["after_units"],
            "unit": tight["unit"],
            "seconds": round(
                tight["seconds_per_unit_that_still_fits"] - tight["mean_seconds_per_unit"], 2
            ),
        },
        "the_first_gate_is_boot_free": {
            "rule": (
                "the first gate GOes only if `pre_generation + boot + 26 x m1 <= usable_seconds`, so"
                " the loosest possible reading of it charges NO boot at all and still bounds the"
                " first unit"
            ),
            "first_unit": first[0],
            "first_unit_payable_comments": first[1],
            "expected_seconds": round(first[2], 1),
            "ceiling_at_zero_boot_seconds": round(usable / len(units), 1),
            "clears_at_zero_boot": first[2] <= usable / len(units),
        },
    }


def money() -> dict:
    """v5's money block recomputed at the new cap, plus what a multi-SEGMENT attempt costs.

    Every second here comes out of `write_reader_prereg_v5.money` under `capped_at`, so leg A's
    projection, leg B's projection, the boot table and the affordability rule are the same arithmetic
    that priced v5 — with one number different. What is ADDED is the segment accounting the ssh
    dead-man makes possible: a pod that is killed at gate 0 and replaced bills the same step.
    """
    with capped_at(CAP_USD):
        reading = v5writer.v4_reading()
        model = v5writer.output_model()
        leg_a = v5writer.leg_a_population()
        leg_b = v5writer.leg_b_population(v5writer.leg_b_thread())
        block = v5writer.money(reading, model, leg_a, leg_b)

    rate = v5writer.CARD_USD_PER_HOUR_EXAMPLE / 3600.0
    sums = block["arithmetic"]
    cap_seconds = float(sums["seconds_the_cap_buys"])
    margin = float(sums["delete_margin_seconds"])
    usable = float(sums["usable_seconds"])
    affordability = float(sums["affordability_deadline_as_create_elapsed"])
    budget = float(sums["pre_generation_budget_seconds"])
    dead = SSH_DEADMAN_S + margin

    return block | {
        "cap_usd_all_in": CAP_USD,
        "cap_rule": (
            "the operator's ruling of 2026-08-17, at the sitting after reader-v5's pod was billed"
            " 727.9 s and never answered ssh. v5's $0.45 left a NEGATIVE pre-generation budget"
            " (−44.785 s): there was no slack to pay for provisioning, and provisioning is what went"
            f" wrong. ${CAP_USD:.2f} buys {cap_seconds:.1f} s and the budget is positive"
        ),
        "guard": (
            f"scripts/runpod_guard.py --step {PHASE} --step-cap {CAP_USD:.2f}, anchored BEFORE the"
            " first pod of the attempt is created and read from the guard, never from a ledger line"
            " or a sentence in a contract. Every segment of the attempt bills THIS step"
        ),
        "segments": {
            "rule": (
                "one attempt may span up to"
                f" {MAX_RECREATES + 1} pod SEGMENTS, never two at once. The cap is the attempt's, not"
                " the segment's: the live affordability comparison is (cap − spent across all"
                " segments) against the reading projection, and `spent` is each closed segment's"
                " BILLED seconds times that segment's own `costPerHr` — never a balance delta"
                " ([[a_balance_delta_is_not_a_per_leg_cost]])"
            ),
            "usable_seconds_rule": (
                "(cap − spent_before_this_segment) ÷ usd_per_second − one delete margin. With no"
                " earlier segment it is v5's `usable_seconds` unchanged, which is what makes the"
                " single-segment case object-equal arithmetic and not a new formula"
            ),
            "a_dead_segment_costs_seconds": round(dead, 1),
            "a_dead_segment_rule": (
                f"{SSH_DEADMAN_S:.0f} s to gate 0's verdict plus the {margin:.0f} s delete margin."
                " reader-v5 measured 4.7 s from create to the first gate and 6 s from KILL to"
                " deleted, so the margin is the pessimistic corner and not the expected one"
            ),
            # every row DERIVES from the three figures this same block publishes, by subtracting what
            # the dead segments billed — so the one-segment row IS the published number and not a
            # second computation of it that rounds a hundredth of a second differently
            # ([[a_record_must_rederive_from_what_it_publishes]])
            "at_each_segment_count": [
                {
                    "segments": n,
                    "dead_segments": n - 1,
                    "billed_before_this_segment_seconds": round((n - 1) * dead, 1),
                    "usable_seconds": round(usable - (n - 1) * dead, 1),
                    "affordability_deadline_as_segment_elapsed": round(
                        affordability - (n - 1) * dead, 1
                    ),
                    "pre_generation_budget_seconds": round(budget - (n - 1) * dead, 1),
                    "the_reading_still_fits": affordability - (n - 1) * dead >= 0,
                }
                for n in range(1, MAX_RECREATES + 2)
            ],
            "at_each_segment_count_rule": (
                "one delete margin per LIVE segment and one dead segment's whole billed length per"
                " kill: `usable_seconds` of segment n is the published one-segment figure minus"
                f" {round(dead, 1)} s per dead pod before it. The live rule reads each closed"
                " segment's ACTUAL billed seconds instead, which is this table's own pessimistic"
                " corner"
            ),
            "reachability": {
                "billed_seconds_before_the_reading_no_longer_fits": round(affordability, 1),
                "usd_before_the_reading_no_longer_fits": round(affordability * rate, 4),
                "per_dead_segment_at_the_ceiling_seconds": round(affordability / MAX_RECREATES, 1),
                "identity": (
                    "the bound IS the affordability deadline, and that is not a coincidence: the"
                    " reading fits while usable − billed_before ≥ projection, which rearranges to"
                    " billed_before ≤ usable − projection. One number, two questions"
                ),
                "rule": (
                    "solve the affordability leg backwards for the SPEND, not for the seconds: the"
                    " last segment can still buy the whole reading only while everything billed"
                    " before it is under this bound. It is the third-pod STOP's arithmetic twin —"
                    f" the ruling caps the recreates at {MAX_RECREATES}, and this caps what they may"
                    " cost. A pod that dies SLOWLY is the state a count of recreates cannot see"
                ),
            },
            "rounding": (
                "the two deadlines are computed at FULL precision and the reading projection is"
                f" published rounded to a tenth ({sums['reading_projection_seconds']} s), so a reader"
                " re-deriving `affordability_deadline_as_create_elapsed` from the published fields"
                " lands within 0.1 s of it and never on a different decision. Every figure in this"
                " segment block derives from the published deadlines themselves, so the one-segment"
                " row and the block above cannot disagree at all"
            ),
            "budget_reading": (
                "the contract's «~918 s with one segment» is the AFFORDABILITY deadline"
                f" ({round(affordability, 1)} s of segment-elapsed: usable −"
                " the reading projection). `pre_generation_budget_seconds` is a different quantity —"
                " usable − the twelve-minute ceiling − the reading projection — and at this cap it is"
                f" {sums['pre_generation_budget_seconds']} s, POSITIVE for the first time. Both"
                " readings of «the budget is positive» hold; they are published apart because they"
                " answer different questions ([[two_readings_of_one_clause]])"
            ),
        },
    }


def go_no_go(older: dict) -> dict:
    """v5's gates, kept, with a gate 0 in front of them and the segment rule written into gate 2."""
    gates = older["go_no_go"]["gates"]
    return older["go_no_go"] | {
        "gates": {
            "0_transport_ssh_deadman": {
                "expected_usd": 0.0,
                "rule": (
                    f"if `runpodctl ssh info` has not answered with a connectable endpoint by"
                    f" {SSH_DEADMAN_S:.0f} s of THIS segment's create-elapsed, KILL: delete the pod,"
                    " prove it by listing, and create a replacement of the same card class in the"
                    " same datacenter"
                ),
                "threshold_seconds": SSH_DEADMAN_S,
                "max_recreates": MAX_RECREATES,
                "third_pod_is_a_stop": (
                    f"at most {MAX_RECREATES} recreates per attempt. A third dead pod is a"
                    " DATACENTER STATE and not bad luck: the attempt STOPs, the step closes, and the"
                    " finding is infrastructural rather than about the reader"
                ),
                "why_it_exists": (
                    "reader-v5's pod was billed 727.9 s, was listed RUNNING throughout, and never"
                    " answered `ssh info` once across ~150 polls; reader-v4's answered in 17 s. The"
                    " boot gate killed it at 721.5 s on the affordability arithmetic — correctly, and"
                    " twelve minutes too late to buy anything with what was left"
                ),
                "measured_on": (
                    "each segment's OWN create response stamp. The affordability leg is the"
                    " attempt's and the reachability leg is the segment's, and they are two axes"
                ),
                "never_two_pods": (
                    "the replacement is created only after the dead one is deleted AND the deletion"
                    " is proven by a listing. The ban's goal is that two meters never run at once, so"
                    " it is a check to be made BEFORE `pod create` and not a refusal afterwards"
                ),
            },
            "1_staging": gates["1_staging"],
            "2_boot_kill": gates["2_boot_kill"]
            | {
                "segments": (
                    "measured from EACH segment's own create response. The twelve-minute ceiling is a"
                    " property of a generation process and every segment starts a new one; the"
                    " affordability leg it is compared against shrinks by what earlier segments"
                    " billed"
                ),
            },
            "3_the_full_pass": gates["3_the_full_pass"]
            | {
                "order": (
                    "leg A first, whole, in DESCENDING payable order (ties by thread id), then leg"
                    " B's three chunks. A stop inside leg A leaves leg B unbought and scores no bar;"
                    " a stop inside leg B leaves leg A COMPLETE and its four bars scored"
                ),
                "identities_not_rows": (
                    "the gate counts UNIQUE unit ids, and a duplicate or a foreign id is a named"
                    " refusal on both the gate and the ingest path. Two rows for one unit would count"
                    " as two units read, shrink `units_unread` and turn the inequality into a trivial"
                    " GO — and the recovery clause is what made an out-file readable twice"
                ),
                "solved_over_the_order_before_the_money": (
                    "`money.arithmetic.full_pass_over_the_registered_order` — the gate run over this"
                    " registration's own order at v4's measured rate, published before anything is"
                    " created"
                ),
            },
        },
    }


def bars(older: dict) -> dict:
    """Bars 1-4 and leg B's four object-equal; bar 5 re-priced to the new cap and nothing else."""
    table = dict(older["bars"])
    cost = table["5_time_and_cost"]
    table["5_time_and_cost"] = cost | {
        "thresholds": {"cap_usd_all_in": CAP_USD},
        "segments": (
            "the bar is scored against the step ledger, and the step is the ATTEMPT's — every"
            " segment of it, dead pods included. A recreate does not get its own budget"
        ),
    }
    return table


def build() -> dict:
    rebuilt = v5writer.build()
    frozen = json.loads(summary.read_text_or_refuse(SUPERSEDES))
    if rebuilt != frozen:
        moved = sorted(
            key for key in set(rebuilt) | set(frozen) if rebuilt.get(key) != frozen.get(key)
        )
        raise SystemExit(
            f"{summary.rel(SUPERSEDES)} no longer rebuilds from its own producer — {moved} differ."
            " v5b registers the SAME instrument, so a moved key here means the instrument moved and"
            " the two runs would not be comparable. Stop and report."
        )

    leg_a = registered_order(frozen["population"]["leg_a"])
    leg_b = frozen["population"]["leg_b"]
    block = money()
    # the tables are solved against the money block that is being registered, so they are built second
    # and folded back in — the gate reads `usable_seconds` off the cap it will actually run under
    priced = frozen | {"money": block}
    block["arithmetic"] = block["arithmetic"] | {
        "full_pass_over_the_registered_order": gate_table(priced, leg_a, leg_b),
        "full_pass_over_the_withdrawn_order": gate_table(
            priced, withdrawn_order(frozen["population"]["leg_a"]), leg_b
        )
        | {
            "why_it_is_here": (
                "the order ruled on 2026-08-17 and WITHDRAWN the same day on this table, before any"
                " pod of this attempt existed. It is published because a withdrawal whose evidence"
                " lives only in a report is a withdrawal the next contract can re-decide"
                " ([[a_deviation_is_dated_not_just_true]])"
            )
        },
    }

    return frozen | {
        "phase": PHASE,
        "contract": "docs/PROMPT-reader-v5b.md",
        "class": (
            "PRE-REGISTRATION. Committed before any pod of this attempt exists; git history is the"
            " only witness that it preceded the money. It FREEZES at the FIRST `pod create` of the"
            " attempt and nothing after that may edit it — a recreated pod reads the SAME frozen"
            " record, which is what makes a replacement a segment of one attempt rather than a second"
            " attempt"
        ),
        "supersedes": {
            "record": summary.rel(SUPERSEDES),
            "sha256": summary.sha256_of(SUPERSEDES),
            "state": (
                "v5 stays FROZEN and is not withdrawn. Its step closed at $0.150095, pods only, and"
                " every bar of it is UNSCORED: the pod it registered was billed 727.9 s, never became"
                " reachable and read nothing. The instrument it registered was never exercised, which"
                " is why this registration re-registers it instead of revising it"
            ),
            "ruling": "the sitting of 2026-08-17, after the pod that never answered ssh",
            "run_record": {
                "record": summary.rel(V5_RUN),
                "sha256": summary.sha256_of(V5_RUN),
                "reading": (
                    "four appended gate snapshots, three WAIT and one KILL at 721.5 s of"
                    " create-elapsed with `seconds_left` −46.3, and no reply"
                ),
            },
            "what_it_changes": [
                f"the cap: $0.45 -> ${CAP_USD:.2f}, one attempt, up to"
                f" {MAX_RECREATES + 1} pod segments",
                f"transport gate 0: `ssh info` connectable by {SSH_DEADMAN_S:.0f} s or KILL and"
                " recreate",
                "nothing else. The third ruling of 2026-08-17 — leg A by descending payable — was"
                " WITHDRAWN the same day, before any pod, on the gate table this record publishes:"
                " see `population.leg_a.order_withdrawn`",
            ],
            "what_it_keeps": (
                "EVERYTHING the reader is scored on, object-equal and checked by rebuilding v5's own"
                " record from v5's own producer: the v5 task and its four prompt shas, the parser,"
                " `market_pulse.reader_v5`, gold r2, the population digest and its 23 threads, leg"
                " B's thread and its three chunks, the 4 000-token output ceiling, the symmetric"
                " vocabulary collapse, N1's exclusion, the echo duty, bars 1-4 with their thresholds"
                " and leg B's four mechanical bars, the serving configuration, the scorer's bytes,"
                " the one-attempt class and the programme stop-rule"
            ),
        },
        "authority": frozen["authority"]
        | {
            summary.rel(path): summary.sha256_of(path)
            for path in (CONTRACT, SUPERSEDES, V5_RUN, v3.GOLD_R2)
        },
        "population": frozen["population"] | {"leg_a": leg_a},
        "money": block,
        "go_no_go": go_no_go(frozen),
        "bars": bars(frozen),
        "transport": frozen["transport"]
        | {
            "resume_protocol": (
                "the partial jsonl is scp'd back inside the poll loop, so a segment that dies leaves"
                " its answered units on the Mac. Before that file goes back UP to a replacement pod"
                " the Mac NORMALIZES it — a torn last line is dropped, as a byte prefix, so every"
                " reply that landed is left exactly as the pod wrote it. Otherwise the fragment"
                " travels, the replacement appends onto it, and the next gate reads a torn MIDDLE"
                " line and raises on the kill-rule path. A torn unit is UNANSWERED and is re-asked;"
                " an answered unit is never re-asked, because one attempt means one answer per unit"
            ),
            "segments": (
                f"at most {MAX_RECREATES + 1}, never two at once, delete and never stop. Each"
                " segment's create response is its own clock and its own `costPerHr`; the gate"
                " snapshots APPEND and carry the segment's pod id"
            ),
        },
        "frozen_when_the_pod_exists": [
            summary.rel(OUT),
            summary.rel(SUPERSEDES),
            summary.rel(PACK),
            *frozen["frozen_when_the_pod_exists"][1:],
        ],
        "non_gating": frozen["non_gating"]
        + [
            "the full-pass gate solved over the registered order at v4's measured rate, and over the"
            " withdrawn one beside it",
            "the segment table: what one and two dead pods leave for the reading",
        ],
        "producer": {
            "script": summary.rel(Path(__file__)),
            "sha256": summary.sha256_of(Path(__file__)),
            "calls": {
                summary.rel(REPO_ROOT / "scripts" / "write_reader_prereg_v5.py"): summary.sha256_of(
                    REPO_ROOT / "scripts" / "write_reader_prereg_v5.py"
                ),
                "rule": (
                    "v5's producer is CALLED and its output is compared to v5's frozen record before"
                    " one key of it is overridden. That check is what «the instrument does not move»"
                    " means here — a claim in prose would be a claim; this is a refusal"
                ),
            },
            "borrowed": frozen["producer"]["borrowed"]
            | {
                name: summary.sha256_of(REPO_ROOT / name)
                for name in ("scripts/read_threads_reader_v5.py",)
            },
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    record = build()
    args.out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {summary.rel(args.out)}  sha256 {summary.sha256_of(args.out)[:16]}…")
    sums = record["money"]["arithmetic"]
    print(
        f"  cap ${CAP_USD:.2f} buys {sums['seconds_the_cap_buys']:.1f} s ·"
        f" usable {sums['usable_seconds']:.1f} s · reading projection"
        f" {sums['reading_projection_seconds']:.1f} s"
    )
    print(
        f"  pre-generation budget {sums['pre_generation_budget_seconds']:.1f} s ·"
        f" affordability deadline {sums['affordability_deadline_as_create_elapsed']:.1f} s"
    )
    for row in record["money"]["segments"]["at_each_segment_count"]:
        print(
            f"    {row['segments']} segment(s): usable {row['usable_seconds']:7.1f} s ·"
            f" affordability {row['affordability_deadline_as_segment_elapsed']:7.1f} s ·"
            f" budget {row['pre_generation_budget_seconds']:7.1f} s ·"
            f" reading fits {row['the_reading_still_fits']}"
        )
    order = record["population"]["leg_a"]
    print(f"  leg A order: {' '.join(one.split(':')[0] for one in order['order'][:5])} …")
    print(
        "  payable, in order:"
        f" {[one['payable_comments'] for one in order['enumeration']['threads']]}"
    )
    gate = sums["full_pass_over_the_registered_order"]
    print(
        f"  full pass over that order: first STOP after"
        f" {gate['first_stop_after_units']} unit(s) · tightest margin"
        f" {gate['tightest_margin']['seconds']} s/unit at unit"
        f" {gate['tightest_margin']['after_units']} ({gate['tightest_margin']['unit']})"
    )
    first = gate["the_first_gate_is_boot_free"]
    print(
        f"  unit 1 {first['first_unit']} · {first['first_unit_payable_comments']} payable ·"
        f" expected {first['expected_seconds']} s vs a zero-boot ceiling of"
        f" {first['ceiling_at_zero_boot_seconds']} s -> clears {first['clears_at_zero_boot']}"
    )
    for row in gate["rows"][:4]:
        print(
            f"    after {row['after_units']:2d} {row['unit']:30s} {row['payable_comments']:3d} pay ·"
            f" mean {row['mean_seconds_per_unit']:6.1f} s ·"
            f" {row['binding']:18s} x{row['factor']:6.2f} · fits"
            f" {row['seconds_per_unit_that_still_fits']:7.1f} s · {row['verdict']}"
        )
    gone = sums["full_pass_over_the_withdrawn_order"]
    print(
        f"  the WITHDRAWN order (descending payable): first STOP after"
        f" {gone['first_stop_after_units']} unit(s) · tightest margin"
        f" {gone['tightest_margin']['seconds']} s/unit at unit"
        f" {gone['tightest_margin']['after_units']} ({gone['tightest_margin']['unit']})"
    )
    print(f"  gates: {sorted(record['go_no_go']['gates'])}")
    print(f"  bar 5 cap: ${record['bars']['5_time_and_cost']['thresholds']['cap_usd_all_in']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
