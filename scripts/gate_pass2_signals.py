#!/usr/bin/env python3
"""pass2-signals — the Mac half of the ONE paid session: r1's rungs, by KEY, plus S and S′.

**The construction is Dv663's**, the one `scripts/gate_pass1_window_r2.py` introduced:
`scripts/gate_pass1_window.py` is pinned by a sealed record and may not be edited, so its source is
loaded ONE MORE TIME as its own module object and the module globals this attempt needs are re-bound.
Nothing of the rung logic is copied. What is re-bound is more than r2 re-bound, and every name is
here for a reason this contract created:

* the six PATHS — `PHASE` `PREREG` `RECORD` `PACK` `POD_LOG` `LAUNCH_STAMP` — as r2 re-bound them.
* **`rung`**, so that every inherited call site reads a deadline BY KEY. `docs/PROMPT-pass2-signals.md`
  D0 asks for it and Dv669 is why: `first_number("rung 5 of 7 — 600 s …")` is 5, the suite stays
  green and a 600 s deadline becomes 5 s. The three call sites that read a deadline live in
  `gate_pass1_fewshot.gate_zero`, `::gate_boot` and `gate_pass1_window.watch`, all of them pinned,
  so the fix is applied where BOTH of them look: the rung dict itself. `deadline_seconds` is
  rendered at the head of the rule the pure functions parse, so what they read is the field and the
  prose can no longer reach it. A clock rung with no `deadline_seconds` is a REFUSAL, not a fallback.
* **`legs_of` and `leg_state`**, so that what the projection prices is what the registration has
  AUTHORISED. Before rung S′ records a GO the pod owes the five smoke units; after it, all 79. Rung
  4 pricing 79 units at the registered 120 s/call would kill the pod at the first poll — the full
  run at that rate is 11 880 s against a 6 600 s stop, and it is supposed to be: this registration
  buys a measurement and registers the guard that decides on the rest.
* **`completeness`**, because rung 7 parses replies and pass 2's parser is not pass 1's — and
  because its bar has two arms, one for each way rung S′ can go.

**Two commands are this file's own.** `--pre-create-check` records its verdict every time it runs
(the step-0.5 finding of `pass1-window`, carried), and `--go-no-go` IS rung S′: it reads the smoke's
seconds off the out-file, computes the charge, RECORDS the verdict, and only then — only on GO —
writes the token the pod is waiting for. That order is the point: the guard's verdict is what
authorises the spend, and a token written before the record would be spend authorised by nothing.

Exit codes are r1's: 0 GO, 2 KILL/STOP, 3 WAIT.

    PYTHONPATH=src python3.11 scripts/gate_pass2_signals.py --pre-create-check
    PYTHONPATH=src python3.11 scripts/gate_pass2_signals.py --price --pod-id <ID> \\
        --created-at <UTC ISO8601> --usd-per-hour <costPerHr> --card '<the card>' \\
        --terminate-after '<the stamp `pod create` was actually given>'
    PYTHONPATH=src python3.11 scripts/gate_pass2_signals.py --gate0 [--ssh-ok]
    PYTHONPATH=src python3.11 scripts/gate_pass2_signals.py --boot
    PYTHONPATH=src python3.11 scripts/gate_pass2_signals.py --watch --ssh root@<HOST> \\
        --ssh-port <PORT>
    PYTHONPATH=src python3.11 scripts/gate_pass2_signals.py --go-no-go
    PYTHONPATH=src python3.11 scripts/gate_pass2_signals.py --projection
    PYTHONPATH=src python3.11 scripts/gate_pass2_signals.py --completeness
    PYTHONPATH=src python3.11 scripts/gate_pass2_signals.py --close --deleted-at <UTC ISO8601> \\
        --outcome '<why this pod ended>'
"""

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import window_summary_5c2 as summary  # noqa: E402

from market_pulse import pass2  # noqa: E402

R1_GATE = REPO_ROOT / "scripts" / "gate_pass1_window.py"
R1_PREREG = REPO_ROOT / "results" / "prereg_pass1_window.json"

PHASE = "pass2-signals"
PREREG = REPO_ROOT / "results" / "prereg_pass2_signals.json"
RECORD = REPO_ROOT / "results" / "pass2_signals_run.json"
PACK = REPO_ROOT / "results" / "pass2_pack.json"
POD_LOG = REPO_ROOT / "results" / "pass2_signals_pod.log"
GO_TOKEN = REPO_ROOT / "results" / "pass2_signals_go.json"
LAUNCH_STAMP = "pass2_signals_launched_at"
"""This attempt's OWN names for every file a rung reads or writes. `results/` already holds three
closed sessions' stamps and logs, and a rung that read one of them would be reading a dead pod's
clock (Dv621/632)."""

REBOUND_PATHS = ("PHASE", "PREREG", "RECORD", "PACK", "POD_LOG", "LAUNCH_STAMP")
DEADLINE_RUNGS = (2, 3, 5, 8)
"""The rungs whose deadline an inherited pure function reads out of the rule. Rung 8 (S) is read by
the RUNNER through the runbook rather than by a pure function here, and it is in the list because
the refusal below is what makes «by key» a property of the record and not of a call site."""

GO_KIND = "go-no-go"


def _load() -> object:
    """r1's gate, executed as its own module object and re-bound to this attempt's world."""
    pinned = json.loads(summary.read_text_or_refuse(R1_PREREG))["instruments"]["gate"]["sha256"]
    live = summary.sha256_of(R1_GATE)
    if live != pinned:
        raise SystemExit(
            f"{summary.rel(R1_GATE)} hashes {live} and {summary.rel(R1_PREREG)} pins {pinned}. This"
            " gate RUNS that file's rung logic, so a file that has moved is a different instrument"
            " answering the same question. Stop and report — r1's gate is pinned by a sealed record"
            " of a closed paid session and may not be edited."
        )
    spec = importlib.util.spec_from_file_location("gate_pass1_window_pass2_source", R1_GATE)
    module = importlib.util.module_from_spec(spec)
    # NOT registered in sys.modules: `import gate_pass1_window` elsewhere must keep r1's own paths
    spec.loader.exec_module(module)
    for name in REBOUND_PATHS:
        if not hasattr(module, name):
            raise SystemExit(
                f"{summary.rel(R1_GATE)} has no module global {name}. This sibling works by"
                " re-binding that gate's globals, and a name it does not carry is a path this file"
                " would silently fail to move. Stop and report."
            )
        setattr(module, name, globals()[name])
    return module


r1 = _load()

GO, KILL, WAIT = r1.GO, r1.KILL, r1.WAIT
_SHIPPED = {name: getattr(r1, name) for name in ("rung", "legs_of", "leg_state", "completeness")}


def rung(record: dict, number: int) -> dict:
    """A rung with its deadline READ BY KEY — and rendered where the inherited parsers look.

    `gate_zero`, `gate_boot` and `watch` are all pinned by sealed records and all three read their
    threshold with `first_number(rule)`. This function is the one place both of them reach, so the
    by-key value is put at the HEAD of the rule they parse: whatever the prose then says, and in
    whatever order, the number those three act on is `deadline_seconds` and nothing else.

    A clock rung that carries no `deadline_seconds` is refused rather than defaulted. A threshold
    with a fallback in the source is exactly the two-copies state one of the two files can move out
    of silently ([[preregistration_is_a_file_not_a_constant]], [[a_threshold_that_lives_in_prose]]).
    """
    one = _SHIPPED["rung"](record, number)
    if int(one["rung"]) not in DEADLINE_RUNGS:
        return one
    if one.get("deadline_seconds") is None:
        raise SystemExit(
            f"{summary.rel(PREREG)} rung {number} carries no `deadline_seconds`. This gate reads"
            " every clock rung's deadline by KEY and will not parse one out of prose — that is the"
            " defect Dv669 registered and it goes green in a suite. Stop and report."
        )
    return {**one, "rule": f"{float(one['deadline_seconds'])} s — {one['rule']}"}


def go_recorded() -> dict | None:
    """Rung S′'s own verdict, off the run record — the authority on what has been authorised.

    The RECORD and not the token file: the token is a transport artefact the runbook scp's to the
    pod, and a guard that read its own authorisation off the thing it ships could be told GO by a
    stray file. `append_gate` writes every snapshot with its pod, so this also cannot pick up a
    previous pod's go.
    """
    if not r1.RECORD.exists():
        return None
    state = json.loads(r1.RECORD.read_text(encoding="utf-8"))
    for gate in reversed(state.get("gates", [])):
        if gate.get("kind") == GO_KIND:
            return gate if gate.get("verdict") == "GO" else None
    return None


def authorised(pack: dict) -> dict:
    """The pack as the registration has authorised it: the smoke until the go, the whole leg after.

    The smoke is a PREFIX of the one leg, so this is a slice and never a second population — the
    out-file, the shas and the ids are the same either way. What changes is how many units the pod
    is judged to OWE, which is what rung 4 multiplies by a rate and what rung 5 waits for.
    """
    if go_recorded() is not None:
        return pack
    leg = pack["legs"][0]
    return {**pack, "legs": [{**leg, "items": leg["items"][: int(pack["smoke"]["units"])]}]}


def legs_of(pack: dict) -> list[dict]:
    return _SHIPPED["legs_of"](authorised(pack))


def leg_state(record: dict, packs: list[dict], where: Path) -> list[dict]:
    return _SHIPPED["leg_state"](record, [authorised(one) for one in packs], where)


def completeness(record: dict, state: dict, pack: dict, where: Path, now=None) -> dict:
    """Rung 7 — r1's three numbers over pass 2's parser, on the arm the go/no-go landed on.

    Two things could not be inherited. The parser is `pass2.parse_pass2`, which needs the UNIT the
    reply was asked about — the pass-1 labels it is held to are in the pack item and nowhere else —
    and the bar has two arms, because a STOP at rung S′ is a registered outcome that owes five units
    and not 79. The arm is READ off the recorded verdict; it is never chosen by hand
    ([[a_flag_that_asserts_turns_a_poll_into_a_verdict]]).

    A RELABELLING is counted as its own cause and never folded into «other»: it is the ADR's line,
    and a run whose refusals are all relabellings is a different result from one whose refusals are
    torn objects ([[count_the_kind_not_the_rows]]).
    """
    go = go_recorded()
    arm = "GO" if go is not None else "STOP"
    bar = {**record["bars"]["completeness"], **record["bars"]["completeness"]["arms"][arm]}
    leg = authorised(pack)["legs"][0]
    items = leg["items"]
    by_id = {one["id"]: one for one in items}
    rows = r1.rows_of(where / leg["out"])

    seen: dict[str, dict] = {}
    duplicates, unknown, mismatched = [], [], []
    refusals, not_balanced = [], []
    parsed = 0
    for row in rows:
        row_id = row.get("id")
        item = by_id.get(row_id)
        if item is None:
            unknown.append(row_id)
            continue
        if row_id in seen:
            duplicates.append(row_id)
            continue
        seen[row_id] = row
        if row.get("rendering_sha256") != item["rendering_sha256"]:
            mismatched.append(row_id)
        if row.get("balanced") is False:
            not_balanced.append(row_id)
        try:
            pass2.parse_pass2(row["reply"], unit=item)
        except Exception as err:  # the parser's own refusal, whatever it names itself
            refusals.append({"id": row_id, "cause": r1.cause_of(err), "why": f"{err}"})
            continue
        parsed += 1

    owed = int(bar["owed"])
    unanswered = [one["id"] for one in items if one["id"] not in seen]
    by_cause = Counter(one["cause"] for one in refusals)
    # a RELABELLING is readable and does not spend a budget that prices a TRANSPORT. It is the
    # ADR's line arriving as a measurement, counted by its own cause and reported beside the bar
    relabels = sum(count for cause, count in by_cause.items() if "RelabelError" in cause)
    unreadable = len(refusals) - relabels
    answered_ok = len(seen) >= int(bar["answered_minimum"])
    sha_ok = len(mismatched) <= int(bar["sha_mismatches_maximum"])
    refusals_ok = unreadable <= int(bar["parse_refusals_maximum"])
    clean = not unknown and not duplicates
    verdict = "GO" if answered_ok and sha_ok and refusals_ok and clean else "RED"
    return {
        "rung": 7,
        "arm": arm,
        "arm_rule": record["bars"]["completeness"]["arm_rule"],
        "go_no_go": None if go is None else {"verdict": go["verdict"], "at": go.get("at")},
        "file": r1.rel(where / leg["out"]),
        "rows_in_the_file": len(rows),
        "owed": owed,
        "answered": len(seen),
        "answered_minimum": int(bar["answered_minimum"]),
        "answered_passed": answered_ok,
        "parsed": parsed,
        "sha_mismatches": len(mismatched),
        "sha_mismatch_ids": mismatched[:20],
        "sha_mismatches_maximum": int(bar["sha_mismatches_maximum"]),
        "sha_passed": sha_ok,
        "parse_refusals": len(refusals),
        "unreadable_replies": unreadable,
        "unreadable_replies_maximum": int(bar["parse_refusals_maximum"]),
        "parse_refusals_maximum": int(bar["parse_refusals_maximum"]),
        "parse_refusals_passed": refusals_ok,
        "parse_refusals_by_cause": dict(sorted(by_cause.items())),
        "budget_rule": bar["parse_refusals_fraction_rule"],
        "relabellings_refused": relabels,
        "relabellings_are_outside_the_budget": bar["relabellings_are_outside_the_budget"],
        "relabelling_rule": (
            "a reply that rewrote a pass-1 subject is refused by cause and counted here. It is not"
            " a transport failure — it is pass 2 doing the one thing the ADR says it may not"
        ),
        "parse_refusal_rows": refusals[:20],
        "replies_that_never_closed_their_object": len(not_balanced),
        "unanswered": len(unanswered),
        "unanswered_ids": unanswered[:20],
        "ids_the_leg_never_asked": unknown[:20],
        "duplicate_ids": duplicates[:20],
        "answered_means": bar["answered_means"],
        "verdict": verdict,
        "rule": bar["rule"],
        "next_step": (
            (
                "GO: the out-file is complete — score it with scripts/score_pass2_signals.py and"
                " write the report"
                + (
                    ""
                    if not relabels
                    else f". READ THIS FIRST: {relabels} of {len(seen)} replies were refused as"
                    " RELABELLINGS. The transport is clean and the ANSWERS are not — bars 1/2/3"
                    " are where that lands, and it is the finding of the run"
                )
            )
            if verdict == "GO"
            else "RED: the out-file goes back to the team lead WITH its refusals by cause and its"
            " mismatches. Nothing already bought is deleted and nothing is re-asked"
        ),
        **r1.clock(record, state, now),
    }


def go_no_go(where: Path, now=None) -> dict:
    """Rung S′ — the charge computed from the smoke's own seconds, RECORDED, then the token.

    `charged_full = max(1.5 × smoke_mean, smoke_max)`: the same pod answered all five, so what is
    charged is the CALL-LENGTH spread and not the pod-class spread this line has been bitten by.

    The projection is published on BOTH arms. The contract writes `create_elapsed_now`; this
    computes it on `cumulative_billed_seconds` as well, which is create-elapsed plus every closed
    pod. They are equal when no pod died and the cumulative one is stricter when one did, so a
    recovery cannot hide a dead pod's seconds from the guard that authorises the spend (Dv630/655).

    The cap arm is computed and cannot bind: the hard stop is $1.4667 at the price ceiling against a
    $1.50 cap, so the seconds bound is the tighter one at any price. It is printed so a reader does
    not have to take that on trust.
    """
    record = r1.registration()
    state = r1.run_state()
    pack = json.loads(summary.read_text_or_refuse(PACK))
    leg = pack["legs"][0]
    wanted = list(pack["smoke"]["ids"])
    sums = record["money"]["arithmetic"]
    gate = sums["cumulative"]["projection_gate"]
    rule = _SHIPPED["rung"](record, 9)

    rows = {one["id"]: one for one in r1.rows_of(where / leg["out"])}
    missing = [one for one in wanted if one not in rows]
    seconds = [float(rows[one]["seconds"]) for one in wanted if one in rows]
    clock = r1.clock(record, state, now)
    if missing or not seconds:
        return {
            "rung": 9,
            "verdict": "WAIT",
            "smoke_ids": wanted,
            "smoke_answered": len(seconds),
            "smoke_missing": missing,
            "cause": "the smoke leg is not answered yet — this rung reads its seconds off the file",
            "rule": rule["rule"],
            "next_step": "stay inside --watch; it returns GO when the authorised leg is answered",
            **clock,
        }

    multiplier = float(rule["multiplier"])
    mean = sum(seconds) / len(seconds)
    beside = row_weighted(leg, wanted, rows, overhead=float(gate["overhead_seconds"]))
    charged = max(multiplier * mean, max(seconds))
    remaining = len(leg["items"]) - len(wanted)
    overhead = float(gate["overhead_seconds"])
    ahead = remaining * charged + overhead
    stop = float(sums["cumulative"]["hard_stop_seconds"])
    cap = float(record["money"]["cap_usd_all_in"])
    pod = r1.live_pod(state)
    if pod is None:
        raise SystemExit("no pod is live — rung S′ prices the run the live pod would do")
    rate = r1.r2gate.rate_of(pod)

    cumulative = clock["cumulative_billed_seconds"] + ahead
    create_arm = clock["elapsed_on_this_pod_seconds"] + ahead
    usd = clock["spent_closed_pods_usd"] + (clock["elapsed_on_this_pod_seconds"] + ahead) * rate
    verdict = "GO" if cumulative <= stop else "STOP"
    return {
        "rung": 9,
        "verdict": verdict,
        "smoke_ids": wanted,
        "smoke_answered": len(seconds),
        "smoke_seconds": [round(one, 3) for one in seconds],
        "smoke_mean_seconds": round(mean, 4),
        "smoke_max_seconds": round(max(seconds), 4),
        "smoke_total_seconds": round(sum(seconds), 3),
        "multiplier": multiplier,
        "charged_full_seconds_per_call": round(charged, 4),
        "charged_arm": "1.5 × mean" if multiplier * mean >= max(seconds) else "the maximum call",
        "remaining_units": remaining,
        "seconds_ahead": round(ahead, 1),
        "overhead_seconds": overhead,
        "projected_cumulative_seconds": round(cumulative, 1),
        "projected_create_elapsed_seconds": round(create_arm, 1),
        "hard_stop_seconds": stop,
        "seconds_left_after_the_full_run": round(stop - cumulative, 1),
        "projected_usd": round(usd, 6),
        "cap_usd_all_in": cap,
        "the_cap_cannot_bind_before_the_stop": round(stop / 3600 * 0.80, 4) <= cap,
        "knife_edge_seconds_per_call": rule["knife_edge_seconds_per_call"],
        "measured_against_the_knife_edge": round(
            charged - float(rule["knife_edge_seconds_per_call"]), 4
        ),
        "both_arms": rule["cumulative_not_create_elapsed"],
        "the_row_weighted_reading": {
            **beside,
            "projected_cumulative_seconds": round(
                clock["cumulative_billed_seconds"] + beside["seconds_ahead"], 1
            ),
            "would_have_said": (
                "GO"
                if clock["cumulative_billed_seconds"] + beside["seconds_ahead"] <= stop
                else "STOP"
            ),
            "and_it_does_not_gate": (
                "REPORT-ONLY. The registered charge is a flat rate on the smoke's own seconds and"
                " it is what decides, because that is what the record registered before the money."
                " This reading is here because the smoke is NOT a sample — the five F threads carry"
                " 6.0 filtered rows a thread against the population's 3.56 — and a STOP that comes"
                " out of the sampling rather than out of the rate is a thing the operator has to be"
                " able to see ([[a_reproducible_probe_can_be_unrepresentative]])"
            ),
        },
        "rule": rule["rule"],
        "worked_arm": rule["worked_arm"],
        "next_step": (
            f"GO: write the token — scp {summary.rel(GO_TOKEN)} to the pod's --go path, then"
            " --watch again for the remaining units"
            if verdict == "GO"
            else "STOP: the full run does not fit at the measured rate. Do NOT write the token —"
            " let the pod's go-wait expire or kill it, score the five, and the remainder returns to"
            " the operator with this number"
        ),
        **clock,
    }


def row_weighted(leg: dict, smoke: list[str], rows: dict, *, overhead: float) -> dict:
    """The remaining units priced from their OWN row counts — beside the flat charge, never gating.

    The registered charge is a flat `max(1.5 × mean, max)` on five threads that carry 6.0 filtered
    rows each against a population that carries 3.56, so it prices the remaining 74 at the weight of
    the heaviest five. This fits `seconds = a + b × rows` on the smoke's five points and predicts
    each of the 74 from its own row count. Two points make a line and five make a fit worth
    printing; neither makes a threshold, which is why this number decides nothing.

    Degenerate input — every smoke thread carrying the same number of rows — has no slope, and the
    honest answer then is the flat mean rather than a division by zero.
    """
    by_id = {one["id"]: one for one in leg["items"]}
    xs = [len(by_id[one]["comments"]) for one in smoke]
    ys = [float(rows[one]["seconds"]) for one in smoke]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    spread = sum((x - mx) ** 2 for x in xs)
    slope = (
        0.0
        if not spread
        else sum((x - mx) * (y - my) for x, y in zip(xs, ys, strict=True)) / spread
    )
    intercept = my - slope * mx
    predicted = [
        max(0.0, intercept + slope * len(one["comments"]))
        for one in leg["items"]
        if one["id"] not in set(smoke)
    ]
    return {
        "fit": f"seconds = {intercept:.2f} + {slope:.2f} × filtered_rows, over the {len(xs)} smoke threads",
        "intercept_seconds": round(intercept, 3),
        "seconds_per_filtered_row": round(slope, 3),
        "smoke_rows_per_thread": round(sum(xs) / len(xs), 3),
        "remaining_rows_per_thread": round(
            sum(len(one["comments"]) for one in leg["items"] if one["id"] not in set(smoke))
            / max(1, len(predicted)),
            3,
        ),
        "predicted_mean_seconds_per_call": round(sum(predicted) / max(1, len(predicted)), 3),
        "predicted_generation_seconds": round(sum(predicted), 1),
        "seconds_ahead": round(sum(predicted) + overhead, 1),
        "degenerate": not spread,
    }


def pre_create_check() -> int:
    """Rung 0 — r1's own computation, and the verdict RECORDED whichever way it goes.

    `pass1-window`'s step 0.5: r1 printed this verdict and returned. A guard whose verdict lives
    only in a terminal is not a record ([[gate_verdicts_need_an_artifact]]).
    """
    record = r1.registration()
    state = json.loads(r1.RECORD.read_text(encoding="utf-8")) if r1.RECORD.exists() else {}
    pod = r1.live_pod(state)
    if pod is not None:
        gate = {
            "rung": 0,
            "verdict": "KILL",
            "cause": f"pod {pod['pod_id']} is OPEN in {r1.rel(r1.RECORD)} and has no deleted_at",
            "verdict_is_an_instruction": True,
            "next_step": (
                "never two billing endpoints at once — delete it, prove it by listing, and --close"
                " first"
            ),
        }
    else:
        gate = r1.pre_create(record, state)
        gate["what_this_authorises"] = record["money"]["arithmetic"]["total_seconds_rule"]
    print(json.dumps(gate, ensure_ascii=False, indent=2, sort_keys=True))
    print(f"\n{gate['verdict']}  ·  {gate['next_step']}")
    state.setdefault("pods", [])
    r1.append_gate(state, gate, "pre-create-check")
    return GO if gate["verdict"] == "GO" else KILL


def run_go_no_go(argv: list[str]) -> int:
    """`--go-no-go`: RECORD first, token second. That order is the guard.

    The token is what unblocks the pod, so writing it before the verdict is recorded would be spend
    authorised by a file nobody wrote a reason into — which is the exact shape of the step-0.5
    finding this whole lineage carries.
    """
    where = REPO_ROOT / "results"
    if "--outdir" in argv:
        where = Path(argv[argv.index("--outdir") + 1])
    gate = go_no_go(where)
    state = r1.run_state()
    r1.append_gate(state, gate, GO_KIND)
    print(json.dumps(gate, ensure_ascii=False, indent=2, sort_keys=True))
    if gate["verdict"] == "GO":
        GO_TOKEN.write_text(
            json.dumps(gate, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(f"\nwrote {summary.rel(GO_TOKEN)} — the pod is waiting for it")
    elif GO_TOKEN.exists():
        raise SystemExit(
            f"{summary.rel(GO_TOKEN)} exists and this verdict is {gate['verdict']}. A token on disk"
            " from an earlier decision would authorise a run this one refuses — move it aside and"
            " re-run."
        )
    print(f"\n{gate['verdict']}  ·  {gate['next_step']}")
    return GO if gate["verdict"] == "GO" else (WAIT if gate["verdict"] == "WAIT" else KILL)


for _name in ("rung", "legs_of", "leg_state", "completeness"):
    setattr(r1, _name, globals()[_name])


def main(argv: list[str] | None = None, now=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--pre-create-check" in argv:
        if len(argv) != 1:
            raise SystemExit("--pre-create-check takes no other flags — it reads the record alone.")
        return pre_create_check()
    if "--go-no-go" in argv:
        return run_go_no_go(argv)
    return r1.main(argv, now)


if __name__ == "__main__":
    raise SystemExit(main())
