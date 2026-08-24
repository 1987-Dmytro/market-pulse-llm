#!/usr/bin/env python3
"""The lora-c session's rungs, executable — a SIBLING of `scripts/gate_lora_b.py`.

`docs/PROMPT-lora-c-run.md` D2 registers GO/KILL rungs as CONDITIONS, and a registered rung with no
producer is not a rung ([[a_registered_bar_may_have_no_producer]]). This is that producer:
`results/prereg_lora_c.json::kill_clock` holds nine of them and every one is graded here, against a
READING, never against a number typed into a runbook.

**What is CALLED and what is written.** `gate_lora_b` owns the accounting that must not exist twice:
the cumulative clock across pods, the `--terminate-after` backstop check, the ssh dead-man, the log
reader that survives a torn last line, the gate-append and the state file. All of those are reached
through the module object, with `PHASE`/`PREREG`/`RECORD` re-bound for the length of one call by
:func:`the_gate_reads_lora_c` — a module-level constant cannot be told anything by a parameter
([[a_self_pinning_producer_cannot_grow_a_parameter]]). Line B's own gates keep reading line B's
files: the swap is undone in a `finally`.

Three rungs are written here because line B has no equivalent, not for convenience:

- **rung 3, the realised rate of the base legs.** lora-b's first spend decision fired at its arm-A
  milestone. Here the first projection rung fires after the smoke — boot, load, two base legs and
  six optimizer steps of spend. Ruling (о) names RTX PRO 4500, a card this repo has never billed,
  and every charged second in the plan was measured on a 4090; this stack's own card-to-card spread
  on identical work is 1.65× ([[a_rate_is_a_property_of_the_pod]]). So the base legs are graded on
  the rate they are REALISING, while they are being paid for.
- **rung 4, the smoke.** It buys the only s/step this line may use and it is also the VRAM test:
  32 GB against the 48 GB every prior reading of this stack was taken on. An OOM at 3 072 is a KILL
  and a STOP — `micro_batch_size` is frozen law in `config/qlora.yaml` and is not edited on a pod.
- **rung 5, the projection.** Eight milestones, not two arms, and the remainder after each is
  DERIVED from the registration's own leg table rather than restated.

    PYTHONPATH=src python3.11 scripts/gate_lora_c.py --pre-create-check
    PYTHONPATH=src python3.11 scripts/gate_lora_c.py --open --pod-id <id> --created-at <ISO> \\
        --usd-per-hour <costPerHr> --card '<displayName>' --terminate-after '<the stamp given>'
    PYTHONPATH=src python3.11 scripts/gate_lora_c.py --gate0 [--ssh-ok]
    PYTHONPATH=src python3.11 scripts/gate_lora_c.py --liveness --last-event <ISO>
    PYTHONPATH=src python3.11 scripts/gate_lora_c.py --rate --leg base_v2 \\
        --replies results/lora_c_base_v2.jsonl --started-at <ISO>
    PYTHONPATH=src python3.11 scripts/gate_lora_c.py --smoke --loss results/lora_c_smoke_loss.jsonl
    PYTHONPATH=src python3.11 scripts/gate_lora_c.py --projection --after smoke --reading <USD>
    PYTHONPATH=src python3.11 scripts/gate_lora_c.py --close-pod --deleted-at <ISO> --outcome '<why>'
"""

import argparse
import contextlib
import json
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gate_lora_b as sibling  # noqa: E402

PHASE = "lora-c"
PREREG = REPO_ROOT / "results" / "prereg_lora_c.json"
RECORD = REPO_ROOT / "results" / "lora_c_run.json"

GO, KILL, WAIT = sibling.GO, sibling.KILL, sibling.WAIT

rel = sibling.rel
stamp = sibling.stamp
elapsed_since = sibling.elapsed_since
rate_of = sibling.rate_of
first_number = sibling.first_number
rung = sibling.rung
log_lines = sibling.log_lines
show = sibling.show


@contextlib.contextmanager
def the_gate_reads_lora_c():
    """`gate_lora_b`'s file constants point at this line, for the length of one call.

    Everything the sibling does with those constants — refusing an untracked registration, loading
    and saving the run state, appending a gate — is the behaviour this line wants, on this line's
    files. The `finally` is what keeps line B's own gates true in the same process.
    """
    was = (sibling.PHASE, sibling.PREREG, sibling.RECORD)
    sibling.PHASE, sibling.PREREG, sibling.RECORD = PHASE, PREREG, RECORD
    try:
        yield
    finally:
        sibling.PHASE, sibling.PREREG, sibling.RECORD = was


def as_the_sibling_reads_it(record: dict) -> dict:
    """A VIEW of this registration at the paths `gate_lora_b`'s clock and backstop read.

    lora-b keeps the cumulative stop at `money.arithmetic.cumulative.hard_stop_seconds`; this line
    derives it in `money.pre_pod_arithmetic`. The view moves the reference, never the number — a
    second literal here is how a threshold starts having two values
    ([[two_values_for_one_input_get_quoted_kindly]]).
    """
    return {
        **record,
        "money": {
            **record["money"],
            "arithmetic": {
                "cumulative": {
                    "hard_stop_seconds": record["money"]["pre_pod_arithmetic"]["hard_stop_seconds"]
                }
            },
        },
    }


def registration() -> dict:
    with the_gate_reads_lora_c():
        return as_the_sibling_reads_it(sibling.registration())


def state_now() -> dict:
    with the_gate_reads_lora_c():
        return sibling.run_state()


def save(state: dict) -> None:
    with the_gate_reads_lora_c():
        sibling.save(state)


def append_gate(state: dict, gate: dict, kind: str) -> dict:
    with the_gate_reads_lora_c():
        return sibling.append_gate(state, gate, kind)


def clock(record: dict, state: dict, now: datetime | None = None) -> dict:
    return sibling.clock(record, state, now)


# --- the plan, in the units each rate prices ----------------------------------------------------

ORDER = (
    "base_v2",
    "base_v3",
    "smoke",
    "arm_a",
    "eval_a",
    "arm_b",
    "eval_b",
    "marker_census",
)
"""The order on the pod, `docs/PROMPT-lora-c-run-r2.md` amendment 6. `--projection --after <one of
these>` prices everything to the right of it."""


def plan(record: dict) -> dict:
    """What each milestone costs, in calls / optimizer steps / pass-2 threads — DERIVED.

    Every quantity is read out of the registration: the eval-call count off each leg, the step
    counts off `money.formulas.steps`, the pass-2 thread count off the money block's own formula
    input, and the marker census off the block ruling (о) added. Nothing here is a literal, so a
    registration that moves moves this table with it ([[preregistration_is_a_file_not_a_constant]]).
    """
    legs = record["legs"]
    steps = record["money"]["formulas"]["steps"]
    arithmetic = record["money"]["pre_pod_arithmetic"]
    threads = int(
        round(
            arithmetic["fixed_seconds"]["pass_2"]
            / arithmetic["rates_used"]["pass_2_seconds_per_thread"]
            / 2
        )
    )
    census = arithmetic["the_marker_census_is_not_inside_the_fixed_part"]
    census_calls = int(
        round(census["seconds"] / arithmetic["rates_used"]["pass_1_seconds_per_call"])
    )
    smoke_steps = int(rung(record, 4)["steps"])
    return {
        "base_v2": {"pass_1_calls": legs["base_v2"]["eval_calls"]},
        "base_v3": {"pass_1_calls": legs["base_v3"]["eval_calls"]},
        "smoke": {"steps": smoke_steps},
        "arm_a": {"steps": steps["arm_a"]},
        "eval_a": {"pass_1_calls": legs["arm_a"]["eval_calls"], "pass_2_threads": threads},
        "arm_b": {"steps": steps["arm_b"]},
        "eval_b": {"pass_1_calls": legs["arm_b"]["eval_calls"], "pass_2_threads": threads},
        "marker_census": {"pass_1_calls": census_calls},
    }


def remaining_after(record: dict, milestone: str) -> dict:
    """The work still to be bought once `milestone` is done — the sum of everything after it."""
    if milestone not in ORDER:
        raise SystemExit(f"{milestone!r} is not one of the registered milestones {ORDER}")
    table = plan(record)
    left = {"pass_1_calls": 0, "steps": 0, "pass_2_threads": 0}
    for name in ORDER[ORDER.index(milestone) + 1 :]:
        for unit, value in table[name].items():
            left[unit] += value
    return left


def seconds_for(
    left: dict, seconds_per_call: float, seconds_per_step: float, seconds_per_thread: float
) -> float:
    return (
        left["pass_1_calls"] * seconds_per_call
        + left["steps"] * seconds_per_step
        + left["pass_2_threads"] * seconds_per_thread
    )


# --- rung 0, the price and the card at create ----------------------------------------------------


def price_gate(record: dict, usd_per_hour: float, card: str) -> dict:
    """The create response's own `costPerHr`, against the price columns this record holds.

    THREE conditions, not one. The ceiling is lora-b's registered rung 1 and it refuses an expensive
    pod. The COLUMN check refuses a pod whose price the plan was never derived at — every projection
    rung after this divides by the price, and a price with no column is a projection nobody can
    check ([[a_rate_is_a_property_of_the_pod]]). And the CARD is graded by name, because ruling (о)
    authorises exactly two and the price is not a proxy for the card: a third card at $0.72 would
    pass a price-only rung, and its seconds are what the whole plan is charged in.
    """
    entry = rung(record, 0)
    rule = entry["rule"]
    ceiling = first_number(rule)
    columns = {float(one) for one in record["money"]["pre_pod_arithmetic"]["at_each_price"]}
    cards = entry["authorised_cards"]
    names = {one for name, spec in cards.items() for one in (name, spec["gpu_id"])}
    registered = any(abs(usd_per_hour - one) < 1e-9 for one in columns)
    authorised = card in names
    over = usd_per_hour > ceiling
    good = registered and authorised and not over
    return {
        "rung": 0,
        "usd_per_hour": usd_per_hour,
        "card": card,
        "price_ceiling_usd_per_hour": ceiling,
        "registered_price_columns": sorted(columns),
        "price_has_a_registered_column": registered,
        "authorised_cards": sorted(names),
        "card_is_authorised": authorised,
        "over_the_ceiling": over,
        "verdict": "GO" if good else "KILL",
        "rule": rule,
        "why_the_card_is_graded": entry["the_card_is_graded_too"],
        "next_step": (
            "the card and the price are both ones this plan was derived at; poll --gate0"
            if good
            else "DELETE the pod now and STOP — no load, no generation, no training"
        ),
    }


# --- rung 1, the boot gate -----------------------------------------------------------------------


def boot_gate(record: dict, state: dict, ssh_ok: bool, now: datetime | None = None) -> dict:
    """The ssh dead-man on THIS pod's create-elapsed — three outcomes, not two.

    `gate_lora_b.gate_zero` is the same logic and it is NOT called: it reads its threshold out of
    lora-b's rung 2, and this line's rung 2 is liveness. Reusing it would grade a 500 s boot against
    a 600 s deadline that means something else entirely — a borrowed rule arriving with an unstated
    population ([[a_borrowed_rule_carries_an_unstated_population]]). The twelve lines are cheaper
    than the coupling.
    """
    rule = rung(record, 1)["rule"]
    threshold = first_number(rule)
    pod = sibling.live_pod(state)
    if pod is None:
        raise SystemExit("no pod is live — the boot gate has nothing to measure")
    elapsed = elapsed_since(pod["created_at"], now)
    verdict = "GO" if ssh_ok else ("KILL" if elapsed >= threshold else "WAIT")
    return {
        "rung": 1,
        "elapsed_on_this_pod_seconds": round(elapsed, 1),
        "threshold_seconds": threshold,
        "seconds_left": round(threshold - elapsed, 1),
        "ssh_endpoint_answered": ssh_ok,
        "verdict": verdict,
        "rule": rule,
        "next_step": (
            "stage the bundle, then load"
            if verdict == "GO"
            else "keep polling `runpodctl ssh info` at 3-4 s"
            if verdict == "WAIT"
            else "KILL: delete, prove it by listing, --close-pod — ONE re-creation is authorised"
        ),
        **clock(record, state, now),
    }


# --- rung 2, liveness ----------------------------------------------------------------------------


def liveness(record: dict, state: dict, last_event: str, now: datetime | None = None) -> dict:
    """Seconds since the last thing that HAPPENED — not since the last time anyone looked.

    A run that is quiet because it died and a run that is quiet because nothing prints are the same
    output to a poll, so the deadline is measured from the last log line or event the caller can
    name ([[no_rung_watches_an_idle_pod]]).
    """
    rule = rung(record, 2)["rule"]
    threshold = first_number(rule)
    quiet = elapsed_since(last_event, now)
    return {
        "rung": 2,
        "last_event": last_event,
        "quiet_seconds": round(quiet, 1),
        "threshold_seconds": threshold,
        "seconds_left": round(threshold - quiet, 1),
        "verdict": "KILL" if quiet >= threshold else "GO",
        "rule": rule,
        "next_step": (
            "KILL: delete, prove it by listing, --close-pod, and report the ledger"
            if quiet >= threshold
            else "the stage is alive; re-run at the next log line"
        ),
        **clock(record, state, now),
    }


# --- rung 3, the realised rate of a base leg -----------------------------------------------------


def answered_rows(replies: Path) -> int:
    """How many replies have landed. A torn last line is DROPPED, as on the loss log."""
    return len(log_lines(replies))


def rate_gate(
    record: dict,
    state: dict,
    leg: str,
    replies: Path,
    started_at: str,
    now: datetime | None = None,
) -> dict:
    """The leg's OWN s/call, extended over everything still to be bought, against the cap.

    The steps are charged at the registration's own `steps_charged_at_seconds_per_step` — the
    cheapest s/step any pod of this stack has been registered at. That is a BOUND and not a
    projection: the contract forbids projecting this line's rate and the smoke buys it, so the rung
    asks only whether the card's realised GENERATION leaves room for the cheapest training anyone
    has measured ([[bound_instead_of_recompute]]). Charging the smoke's kill-clock ceiling instead
    would refuse every session at the first base leg — 150 steps at 181.5 s is more than the cap
    buys on its own, which is how that first version was caught.
    """
    rule = rung(record, 3)["rule"]
    cap = first_number(rule)
    answered = answered_rows(replies)
    elapsed = elapsed_since(started_at, now)
    if answered == 0:
        return {
            "rung": 3,
            "leg": leg,
            "rows_answered": 0,
            "elapsed_seconds": round(elapsed, 1),
            "verdict": "WAIT",
            "rule": rule,
            "next_step": "no reply has landed yet — copy the out-file back again",
            **clock(record, state, now),
        }
    realised = elapsed / answered
    charged = float(record["money"]["pre_pod_arithmetic"]["rates_used"]["pass_1_seconds_per_call"])
    per_step = float(rung(record, 3)["steps_charged_at_seconds_per_step"])
    per_thread = float(
        record["money"]["pre_pod_arithmetic"]["rates_used"]["pass_2_seconds_per_thread"]
    )
    left = remaining_after(record, leg)
    left["pass_1_calls"] += plan(record)[leg]["pass_1_calls"] - answered
    ahead = seconds_for(left, realised, per_step, per_thread)
    now_clock = clock(record, state, now)
    pod = sibling.live_pod(state)
    if pod is None:
        raise SystemExit("no pod is live — there is nothing to rate")
    projected = now_clock["spent_closed_pods_usd"] + (
        now_clock["elapsed_on_this_pod_seconds"] + ahead
    ) * rate_of(pod)
    over = projected > cap
    return {
        "rung": 3,
        "leg": leg,
        "rows_answered": answered,
        "elapsed_seconds": round(elapsed, 1),
        "realised_seconds_per_call": round(realised, 3),
        "charged_seconds_per_call": charged,
        "realised_over_charged": round(realised / charged, 3),
        "remaining_work": left,
        "steps_charged_at_seconds_per_step": per_step,
        "seconds_ahead": round(ahead, 1),
        "projected_usd": round(projected, 4),
        "cap_usd_all_in": cap,
        "verdict": "KILL" if over else "GO",
        "rule": rule,
        "next_step": (
            "KILL before the next leg: pull what exists, prove the teardown by listing, STOP. The"
            " finding is the card"
            if over
            else "the card pays for the plan at the rate it is realising; continue"
        ),
        **now_clock,
    }


# --- rung 4, the smoke ---------------------------------------------------------------------------


def smoke_gate(
    record: dict,
    state: dict,
    loss: Path,
    oom: bool = False,
    now: datetime | None = None,
) -> dict:
    """The six optimizer steps that buy s/step, and the VRAM test ruling (о) makes them.

    An OOM is a KILL and a STOP with no branch: `micro_batch_size` is frozen law and halving it on
    a pod would make the arm a different instrument from the one the registration prices.
    """
    rule = rung(record, 4)["rule"]
    ceiling = first_number(rule)
    rows = log_lines(loss)
    steps = plan(record)["smoke"]["steps"]
    seen = [float(one["seconds_per_step"]) for one in rows if one.get("seconds_per_step")]
    measured = None if not seen else sibling.measured_step(rows)
    if oom:
        verdict, why = "KILL", "OOM at 3 072 — micro_batch is frozen law and is not edited on a pod"
    elif len(seen) < steps:
        verdict, why = "WAIT", f"{len(seen)} of {steps} smoke steps have logged"
    elif measured > ceiling:
        verdict, why = "KILL", f"{measured:.2f} s/step is over the registered {ceiling} ceiling"
    else:
        verdict, why = "GO", None
    gate = {
        "rung": 4,
        "loss": rel(loss),
        "smoke_steps_registered": steps,
        "smoke_steps_logged": len(seen),
        "seconds_per_step_each": [round(one, 2) for one in seen],
        "measured_seconds_per_step": None if measured is None else round(measured, 3),
        "ceiling_seconds_per_step": ceiling,
        "out_of_memory": oom,
        "why": why,
        "verdict": verdict,
        "rule": rule,
        "next_step": (
            "this is the ONLY s/step this line may use — run --projection --after smoke"
            if verdict == "GO"
            else "keep copying the loss log back"
            if verdict == "WAIT"
            else "KILL and STOP: delete, prove it by listing, --close-pod, report to the team lead"
        ),
        **clock(record, state, now),
    }
    if verdict == "GO":
        state["measured_seconds_per_step"] = gate["measured_seconds_per_step"]
    return gate


# --- rung 5, the projection ----------------------------------------------------------------------


def projection(
    record: dict,
    state: dict,
    after: str,
    reading: float,
    now: datetime | None = None,
) -> dict:
    """Cumulative spend + the remainder at MEASURED rates, against the cap and the hard stop.

    `reading` is `scripts/runpod_guard.py`'s USD — the meter, not this clock's projection. The rung
    acts on the reading plus the forecast, which is the shape lora-b's rung 9 uses and the one that
    survives a pod whose clock and whose billing disagree ([[a_balance_delta_is_not_a_per_leg_cost]]).

    Rates: s/call from whatever base leg this session has already measured, s/step from the smoke.
    Where a measurement is missing the CHARGED rate stands in, and the field says which was used —
    a projection quietly falling back to a rosier number is the failure this whole ladder exists to
    prevent ([[projected_rate_versus_measured_rate]]).
    """
    rule = rung(record, 5)["rule"]
    cap = first_number(rule)
    rates = record["money"]["pre_pod_arithmetic"]["rates_used"]
    per_call = state.get("measured_seconds_per_call") or float(rates["pass_1_seconds_per_call"])
    per_step = state.get("measured_seconds_per_step") or first_number(rung(record, 4)["rule"])
    per_thread = float(rates["pass_2_seconds_per_thread"])
    left = remaining_after(record, after)
    ahead = seconds_for(left, per_call, per_step, per_thread)
    now_clock = clock(record, state, now)
    pod = sibling.live_pod(state)
    if pod is None:
        raise SystemExit("no pod is live — there is nothing to project")
    projected_usd = reading + ahead * rate_of(pod)
    projected_seconds = now_clock["cumulative_billed_seconds"] + ahead
    over_cap = projected_usd > cap
    over_stop = projected_seconds > now_clock["hard_stop_seconds"]
    return {
        "rung": 5,
        "after": after,
        "guard_reading_usd": reading,
        "remaining_work": left,
        "seconds_per_call_used": round(per_call, 3),
        "seconds_per_call_is_measured": state.get("measured_seconds_per_call") is not None,
        "seconds_per_step_used": round(per_step, 3),
        "seconds_per_step_is_measured": state.get("measured_seconds_per_step") is not None,
        "seconds_per_thread_used": per_thread,
        "seconds_ahead": round(ahead, 1),
        "projected_seconds": round(projected_seconds, 1),
        "projected_usd": round(projected_usd, 4),
        "cap_usd_all_in": cap,
        "over_the_cap": over_cap,
        "over_the_hard_stop": over_stop,
        "verdict": "KILL" if over_cap or over_stop else "GO",
        "rule": rule,
        "next_step": (
            "KILL: pull every artifact, prove the teardown by listing, STOP to the team lead with"
            " the ledger. A KILL here is compliance"
            if over_cap or over_stop
            else f"GO — the next milestone after {after}"
        ),
        **now_clock,
    }


def main(argv: list[str] | None = None, now: datetime | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pre-create-check", action="store_true", help="rung 7")
    parser.add_argument("--open", action="store_true", help="rungs 0 and 6, at create")
    parser.add_argument("--pod-id")
    parser.add_argument("--created-at", help="the create response's stamp — the meter's zero")
    parser.add_argument("--usd-per-hour", type=float, help="costPerHr, read back from create")
    parser.add_argument("--card", help="the displayName the create response actually gave")
    parser.add_argument("--terminate-after", help="the backstop stamp ACTUALLY given to pod create")
    parser.add_argument("--gate0", action="store_true", help="rung 1, the ssh dead-man")
    parser.add_argument("--ssh-ok", action="store_true", help="the endpoint answered")
    parser.add_argument("--liveness", action="store_true", help="rung 2")
    parser.add_argument("--last-event", help="the stamp of the last log line or event")
    parser.add_argument("--rate", action="store_true", help="rung 3, on a base leg's out-file")
    parser.add_argument("--leg", choices=("base_v2", "base_v3"))
    parser.add_argument("--replies", type=Path, help="the leg's growing out-file")
    parser.add_argument("--started-at", help="when this leg's first call was issued")
    parser.add_argument("--smoke", action="store_true", help="rung 4, s/step and the VRAM")
    parser.add_argument("--loss", type=Path, help="the smoke's loss.jsonl, copied back")
    parser.add_argument("--oom", action="store_true", help="the smoke died out of memory")
    parser.add_argument("--projection", action="store_true", help="rung 5")
    parser.add_argument("--after", choices=ORDER)
    parser.add_argument("--reading", type=float, help="the guard's reading in USD")
    parser.add_argument("--clock", action="store_true", help="the cumulative reading, right now")
    parser.add_argument("--close-pod", action="store_true", help="this pod is deleted")
    parser.add_argument("--deleted-at", help="the deletion's stamp — the meter's end")
    parser.add_argument("--outcome", help="why this pod ended")
    args = parser.parse_args(argv)

    record = registration()

    if args.pre_create_check:
        state = json.loads(RECORD.read_text(encoding="utf-8")) if RECORD.exists() else {}
        pod = sibling.live_pod(state)
        if pod is not None:
            print(
                f"pod {pod['pod_id']} is OPEN in {rel(RECORD)} and has no deleted_at. Rung 7: never"
                " two billing resources — delete it, prove it by listing, --close-pod first."
            )
            return KILL
        stop = float(record["money"]["arithmetic"]["cumulative"]["hard_stop_seconds"])
        billed, spent = sibling.billed_before(state)
        print(
            f"no pod is open · {len(state.get('pods', []))} closed, {billed:.0f} s = ${spent:.4f}"
            f" billed · the hard stop leaves {stop - billed:.0f} s for the next pod's"
            " --terminate-after"
        )
        return GO if billed < stop else KILL

    if args.open:
        for name in ("pod_id", "created_at", "usd_per_hour", "card", "terminate_after"):
            if getattr(args, name) is None:
                parser.error(f"--open needs --{name.replace('_', '-')}")
        state = json.loads(RECORD.read_text(encoding="utf-8")) if RECORD.exists() else {"pods": []}
        if sibling.live_pod(state) is not None:
            raise SystemExit(
                f"pod {sibling.live_pod(state)['pod_id']} is still open in {rel(RECORD)}. Rung 7:"
                " never two billing resources — close it with --close-pod first."
            )
        backstop = sibling.terminate_after(record, state, args.created_at, args.terminate_after)
        state.setdefault("pods", []).append(
            {
                "pod_id": args.pod_id,
                "created_at": args.created_at,
                "usd_per_hour": args.usd_per_hour,
                "card": args.card,
                "terminate_after": backstop["given"],
                "terminate_after_computed": backstop["computed"],
            }
        )
        save(state)
        gate = {
            **price_gate(record, args.usd_per_hour, args.card),
            "backstop": backstop,
            "terminate_after_rule": rung(record, 6)["rule"],
            **clock(record, state, now),
        }
        append_gate(state, gate, "open")
        return show(gate)

    state = state_now()

    if args.clock:
        print(json.dumps(clock(record, state, now), ensure_ascii=False, indent=2, sort_keys=True))
        return GO

    if args.gate0:
        gate = boot_gate(record, state, args.ssh_ok, now)
        append_gate(state, gate, "gate0")
        return show(gate)

    if args.liveness:
        if not args.last_event:
            parser.error("--liveness needs --last-event: the stamp of the last thing that HAPPENED")
        gate = liveness(record, state, args.last_event, now)
        append_gate(state, gate, "liveness")
        return show(gate)

    if args.rate:
        if not args.leg or not args.replies or not args.started_at:
            parser.error("--rate needs --leg, --replies and --started-at")
        gate = rate_gate(record, state, args.leg, args.replies, args.started_at, now)
        if gate["verdict"] != "WAIT":
            state["measured_seconds_per_call"] = gate["realised_seconds_per_call"]
        append_gate(state, gate, f"rate-{args.leg}")
        save(state)
        return show(gate)

    if args.smoke:
        if not args.loss:
            parser.error("--smoke needs --loss")
        gate = smoke_gate(record, state, args.loss, args.oom, now)
        append_gate(state, gate, "smoke")
        save(state)
        return show(gate)

    if args.projection:
        if not args.after or args.reading is None:
            parser.error("--projection needs --after and --reading (the guard's USD)")
        gate = projection(record, state, args.after, args.reading, now)
        append_gate(state, gate, f"projection-{args.after}")
        return show(gate)

    if args.close_pod:
        if not args.deleted_at:
            parser.error("--close-pod needs --deleted-at: this pod's billed end")
        pod = sibling.live_pod(state)
        if pod is None:
            raise SystemExit("no pod is open — there is nothing to close")
        billed = (stamp(args.deleted_at) - stamp(pod["created_at"])).total_seconds()
        pod["deleted_at"] = args.deleted_at
        pod["billed_seconds"] = round(billed, 1)
        pod["billed_usd"] = round(billed * rate_of(pod), 6)
        pod["outcome"] = args.outcome
        save(state)
        gate = {
            "billed_seconds": pod["billed_seconds"],
            "billed_usd": pod["billed_usd"],
            "outcome": args.outcome,
            "verdict": "GO",
            "next_step": "prove the deletion by LISTING, with the volume as the positive control",
            **clock(record, state, now),
        }
        append_gate(state, gate, "close-pod")
        return show(gate)

    parser.error(
        "one of --pre-create-check / --open / --gate0 / --liveness / --rate / --smoke /"
        " --projection / --clock / --close-pod"
    )
    return KILL


if __name__ == "__main__":
    raise SystemExit(main())
