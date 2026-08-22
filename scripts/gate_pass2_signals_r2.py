#!/usr/bin/env python3.11
"""The kill clock of `pass2-signals-r2` — r1's gate, re-bound to r2's world and r2's arithmetic.

**A SIBLING and not a `--revision r2` flag.** `scripts/gate_pass2_signals.py` is pinned by
`results/prereg_pass2_signals.json::instruments.gate.sha256`, a sealed record of a closed paid
session, and the contract's own rule is «`--revision r2` if r1's pinned bytes stay untouched,
otherwise a sibling (say which)». This is the sibling. It loads r1's gate as its own module object
by the Dv663 construction — sha-checked first — and re-binds the names r2 changes.

**What r2 changes, and every one of these was found by driving the inherited code, not by reading
it.** The four carried rows are in the out-file BEFORE the pod exists, so every inherited rung that
counts rows is answering a different question than it thinks:

* `fingerprint` — `watch`'s idea of «an event». With four rows already present the boot branch
  `if not cleared and not answered` is dead from the first poll, so **rung 3 could never fire in the
  watch loop**. Re-bound to count BOUGHT rows.
* `first_reply_after_launch` — `min(elapsed_since_start)` over the out-file returns 197.6 s from
  r1's pod before this one has answered anything, and rung 3 reports GO on a reading taken on
  another machine last session ([[a_rate_is_a_property_of_the_pod]]).
* `leg_state` — the leg owes 75 and not 79, and the rate it measures must be THIS pod's. Averaging
  r1's four calls into it would publish a rate no pod ever ran at.
* `pre_create` — r1's recovery clause reads «any row in the out-file» as «a reply has been bought»,
  which with a seeded file refuses the FIRST create of the session.
* `authorised` — r1's slices the leg to the smoke until a go is recorded. r2 has no go/no-go and
  the whole leg is authorised from rung 0.
* `completeness` — r2's parser, and ONE arm.

**The two counts, and the rule between them.** Rungs 3, 4 and 5 are about THIS POD: they count the
75 units it owes and the rows it bought. Rung 7 is about the OUT-FILE: 79 rows, carried and bought
alike, each re-parsed. Neither count is wrong; using one where the other belongs is
([[the_argmax_and_the_max_are_two_rows]]).

Exit codes ARE the rule — 0 GO, 2 KILL/STOP, 3 WAIT.

    PYTHONPATH=src python3.11 scripts/gate_pass2_signals_r2.py --pre-create-check
    PYTHONPATH=src python3.11 scripts/gate_pass2_signals_r2.py --price --pod-id <ID> ...
    PYTHONPATH=src python3.11 scripts/gate_pass2_signals_r2.py --watch --ssh ... --pack results/pass2_r2_pack.json
    PYTHONPATH=src python3.11 scripts/gate_pass2_signals_r2.py --completeness --pack results/pass2_r2_pack.json
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

from market_pulse import pass2_r2  # noqa: E402

R1_GATE = REPO_ROOT / "scripts" / "gate_pass2_signals.py"
R1_PREREG = REPO_ROOT / "results" / "prereg_pass2_signals.json"

PHASE = "pass2-signals-r2"
PREREG = REPO_ROOT / "results" / "prereg_pass2_signals_r2.json"
RECORD = REPO_ROOT / "results" / "pass2_signals_r2_run.json"
PACK = REPO_ROOT / "results" / "pass2_r2_pack.json"
POD_LOG = REPO_ROOT / "results" / "pass2_signals_r2_pod.log"
OUT_FILE = REPO_ROOT / "results" / "pass2_signals_r2_v1.jsonl"
LAUNCH_STAMP = "pass2_signals_r2_launched_at"
"""This attempt's OWN names. `results/` holds four closed sessions' stamps and logs, and a rung that
read one of them would be reading a dead pod's clock (Dv621/632)."""

DEADLINE_RUNGS = (2, 3, 5, 6)
"""The rungs whose deadline must be a KEY and never prose. Rung 8 is gone with the smoke leg and
rung 6 joins the list — its deadline is the hard stop, and a clock rung whose number lives only in a
sentence is the defect Dv669 registered ([[a_threshold_that_lives_in_prose]])."""

CARRIED = "carried_from"
"""The field the seeder writes on a row r1 bought. Its presence is the whole of «this row is not
this pod's», and every count in this file that is about THIS POD filters on it."""


def _load() -> object:
    """r1's pass-2 gate, executed as its own module object, sha-checked against its sealed record."""
    pinned = json.loads(summary.read_text_or_refuse(R1_PREREG))["instruments"]["gate"]["sha256"]
    live = summary.sha256_of(R1_GATE)
    if live != pinned:
        raise SystemExit(
            f"{summary.rel(R1_GATE)} hashes {live} and {summary.rel(R1_PREREG)} pins {pinned}. This"
            " gate RUNS that file's rung logic, so a file that has moved is a different instrument"
            " answering the same question. Stop and report — r1's gate is pinned by a sealed record"
            " of a closed paid session and may not be edited."
        )
    spec = importlib.util.spec_from_file_location("gate_pass2_signals_r2_source", R1_GATE)
    module = importlib.util.module_from_spec(spec)
    # NOT registered in sys.modules: `import gate_pass2_signals` elsewhere must keep r1's own paths
    spec.loader.exec_module(module)
    return module


r2 = _load()
window = r2.r1
"""The two module objects this file re-binds. `r2` is r1's pass-2 gate; `window` is the
`gate_pass1_window` object it built for itself and already re-bound to r1's paths. Python resolves a
global in the module where the FUNCTION is defined, so BOTH have to move or half the rungs keep
reading r1's files ([[a_proof_can_cover_the_sibling_branch]])."""

GO, KILL, WAIT = r2.GO, r2.KILL, r2.WAIT

for _name in (
    "PHASE",
    "PREREG",
    "RECORD",
    "PACK",
    "POD_LOG",
    "LAUNCH_STAMP",
    "OUT_FILE",
    "DEADLINE_RUNGS",
):
    _moved = False
    for _module in (r2, window):
        if hasattr(_module, _name):
            setattr(_module, _name, globals()[_name])
            _moved = True
    if not _moved:
        raise SystemExit(
            f"neither {summary.rel(R1_GATE)} nor its window gate carries a module global {_name}."
            " This sibling works by re-binding those globals, and a name neither of them has is a"
            " path this file would silently fail to move. Stop and report."
        )

_SHIPPED = {name: getattr(window.r2gate, name) for name in ("legs_of", "pre_create")}
"""The RAW inherited functions, taken from `gate_pass1_fewshot` and NOT from the window gate.

r1's pass-2 gate has already re-bound `legs_of`, `leg_state` and `pre_create` onto the window module
by the time this file imports it, so `getattr(window, ...)` returns r1's wrappers — the ones that
slice the leg to a smoke prefix and read r1's own out-file. Delegating to those would apply r1's
recovery clause on top of r2's and count the four carried rows as replies of this session, which is
a KILL on the first create. Driven, not reasoned: the test that says so is
`test_the_recovery_clause_refuses_a_pod_after_the_first_BOUGHT_reply`
([[a_proof_can_cover_the_sibling_branch]])."""


def registration() -> dict:
    return window.registration()


def carried_ids(pack: dict | None = None) -> set[str]:
    pack = pack if pack is not None else json.loads(summary.read_text_or_refuse(PACK))
    return set(pack["carried"]["ids"])


def bought(rows: list[dict]) -> list[dict]:
    """The rows THIS pod paid for. A carried row is evidence and it is not this session's work."""
    return [one for one in rows if not one.get(CARRIED)]


def authorised(pack: dict) -> dict:
    """The whole leg, from rung 0. r2 has no go/no-go and nothing to slice."""
    return pack


def legs_of(pack: dict) -> list[dict]:
    """Each leg with `units` = what THIS POD owes — 75 and not 79.

    `watch` compares its answered count against this, and `leg_state` prices the remainder from it.
    Both are questions about the pod, and the four rows it starts with are not its work
    ([[the_fix_widened_the_denominator]] read the other way: a denominator that quietly grew by four
    would report the run complete four units early)."""
    carried = carried_ids(pack)
    return [
        {
            **one,
            "units": one["units"]
            - sum(1 for item in pack["legs"][index]["items"] if item["id"] in carried),
        }
        for index, one in enumerate(_SHIPPED["legs_of"](pack))
    ]


def leg_state(record: dict, packs: list[dict], where: Path) -> list[dict]:
    """Per leg: what this pod owes, what it has bought, and the rate IT is running at.

    The inherited version counts every row in the out-file and averages every `seconds` it finds.
    With a seeded file that is r1's pod's rate blended into this one's, on a number rung 4
    multiplies by 75 ([[a_rate_is_a_property_of_the_pod]]).
    """
    registered = record["money"]["arithmetic"]["seconds_per_call"]
    out = []
    worst = 0.0
    for pack in packs:
        for one in legs_of(pack):
            rows = bought(window.rows_of(where / one["out"]))
            seen = [float(row["seconds"]) for row in rows if row.get("seconds")]
            measured = max(sum(seen) / len(seen), seen[-1]) if seen else None
            if measured:
                worst = max(worst, measured)
            out.append(
                {
                    **one,
                    "answered": len(rows),
                    "answered_means": "rows THIS pod bought; the carried rows are excluded",
                    "carried_rows_in_the_file": len(window.rows_of(where / one["out"])) - len(rows),
                    "measured_seconds_per_call": measured,
                }
            )
    for one in out:
        floor = float(registered[one["name"]])
        one["seconds_per_call_used"] = round(
            one["measured_seconds_per_call"] or max(floor, worst), 4
        )
        one["rate_source"] = "measured" if one["measured_seconds_per_call"] else "registered"
        one["remaining"] = max(0, one["units"] - one["answered"])
    return out


def fingerprint(where: Path, legs: list[dict], log: Path) -> tuple[int, int]:
    """`watch`'s event counter, over the rows THIS POD bought.

    The inherited one counts every line of the out-file, so a seeded file makes `answered` four from
    the first poll — and `watch`'s boot branch is `if not cleared and not answered`. **Rung 3 would
    never fire.** That is the fatal one of this file's re-bindings and it was found by driving the
    loop on a fake transport, not by reading it.
    """
    rows = sum(len(bought(window.rows_of(where / one["out"]))) for one in legs)
    lines = len(log.read_text(encoding="utf-8").splitlines()) if log.exists() else 0
    return rows, lines


def first_reply_after_launch(record: dict, where: Path) -> float | None:
    """Rung 3's reading — the first reply THIS POD wrote, in seconds since its own launch.

    A carried row's `elapsed_since_start` is 197.6 s measured on pod `9rquj8p0lelct3` in r1's
    session. Taking the minimum over the seeded file hands rung 3 a passing number before this pod
    has done anything at all.
    """
    seen = [
        float(row["elapsed_since_start"])
        for row in bought(window.rows_of(where / record["population"]["out_file"]))
        if row.get("elapsed_since_start") is not None
    ]
    return min(seen) if seen else None


def pre_create(record: dict, state: dict) -> dict:
    """Rung 0 — r1's arithmetic, plus the recovery clause read on the rows THIS SESSION bought.

    `money.recovery` allows ONE re-creation and only for a death BEFORE the first NEW reply. r1's
    version counts every row in the out-file; r2's out-file is seeded with four before the pod
    exists, so that version would refuse the session's very first create — and, worse, would call a
    death at rung 2 unrecoverable because r1 answered four threads yesterday.
    """
    gate = _SHIPPED["pre_create"](record, state)
    rows = window.rows_of(OUT_FILE)
    answered = len(bought(rows))
    fits = not (answered and state.get("pods"))
    gate["replies_bought_by_this_session"] = answered
    gate["carried_rows_in_the_file"] = len(rows) - answered
    gate["fits_the_recovery_clause"] = fits
    gate["recovery_clause"] = record["money"]["recovery"]["after_the_first_reply"]
    gate["the_carried_rows_are_not_a_reply"] = record["money"]["recovery"][
        "the_carried_rows_are_not_a_reply"
    ]
    if not fits:
        gate["verdict"] = "KILL"
        gate["next_step"] = (
            f"STOP: {answered} repl(ies) of THIS session are already on the Mac, so the death that"
            " ended the last pod happened AFTER the first new reply. The recovery clause allows one"
            " re-creation only for a death at rungs 1–3; what follows this is a new registration"
            " with this pod's measured rate in it, never a second pod."
        )
    return gate


def completeness(record: dict, state: dict, pack: dict, where: Path, now=None) -> dict:
    """Rung 7 — the transport bar over the WHOLE out-file: 79 rows, carried and bought alike.

    One arm. r1's bar had two because rung S′ could stop the run at five units; r2 has no rung whose
    verdict could select one, and an arm nothing writes is a bar reading a field that does not exist
    ([[a_flag_that_asserts_turns_a_poll_into_a_verdict]]).

    The parser is `pass2_r2.parse_pass2`, whose refusal set is closed at six causes and contains no
    report-only field. What that removes from this count is exactly the refusal that fired in r1 —
    and what it ADDS is a census of the fields it could not read, which is the measurement Dv702
    bought.
    """
    bar = {**record["bars"]["completeness"], **record["bars"]["completeness"]["arms"]["GO"]}
    leg = pack["legs"][0]
    items = leg["items"]
    by_id = {one["id"]: one for one in items}
    rows = window.rows_of(where / leg["out"])
    carried = carried_ids(pack)

    seen: dict[str, dict] = {}
    duplicates, unknown, mismatched = [], [], []
    refusals, not_balanced, unreadable_fields = [], [], []
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
            verdict = pass2_r2.parse_pass2(row["reply"], unit=item)
        except Exception as err:  # the parser's own refusal, whatever it names itself
            refusals.append({"id": row_id, "cause": window.cause_of(err), "why": f"{err}"})
            continue
        parsed += 1
        for one in verdict["unreadable_fields"]:
            unreadable_fields.append({"id": row_id, **one})

    owed = int(bar["owed"])
    # the split is keyed on the FIELD the seeder writes and never on the pack's id list. A pod that
    # never got the seed re-buys those four and writes rows with no `carried_from`; keyed on the
    # list, the census would report them as carried and rung 7 would say GO over a run that bought
    # 79 ([[a_reading_is_not_an_identity]]). The pack's list is kept — as an ASSERTION
    carried_rows = sorted(one for one, row in seen.items() if row.get(CARRIED))
    named = sorted(carried)
    disagreement = sorted(set(named) ^ set(carried_rows))
    unanswered = [one["id"] for one in items if one["id"] not in seen]
    by_cause = Counter(one["cause"] for one in refusals)
    relabels = sum(count for cause, count in by_cause.items() if "RelabelError" in cause)
    unreadable = len(refusals) - relabels
    answered_ok = len(seen) >= int(bar["answered_minimum"])
    sha_ok = len(mismatched) <= int(bar["sha_mismatches_maximum"])
    refusals_ok = unreadable <= int(bar["parse_refusals_maximum"])
    clean = not unknown and not duplicates and not disagreement
    verdict = "GO" if answered_ok and sha_ok and refusals_ok and clean else "RED"
    return {
        "rung": 7,
        "arm": "GO",
        "arm_rule": record["bars"]["completeness"]["arm_rule"],
        "file": window.rel(where / leg["out"]),
        "rows_in_the_file": len(rows),
        "carried": carried_rows,
        "carried_count": len(carried_rows),
        "bought_by_this_pod": len(seen) - len(carried_rows),
        "carried_the_pack_names": named,
        "carried_disagreement": disagreement,
        "carried_rule": (
            "counted on the row's own `carried_from` field. A disagreement with the pack's list is"
            " RED: it means either the seed never reached the pod (and those threads were RE-BOUGHT"
            " against the contract) or a row was hand-edited"
        ),
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
        "parse_refusal_rows": refusals[:20],
        "unreadable_report_only_fields": len(unreadable_fields),
        "unreadable_report_only_fields_by_name": dict(
            sorted(Counter(one["field"] for one in unreadable_fields).items())
        ),
        "unreadable_report_only_field_rows": unreadable_fields[:40],
        "unreadable_fields_are_not_refusals": (
            "a report-only field the parser could not read is COUNTED here and the reply is kept."
            " In r1 the first such field refused the whole thread and took bar 1's hardest case"
            " with it (Dv702). This number is what that fix measures"
        ),
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
                "GO: the out-file is complete — score it with scripts/score_pass2_signals_r2.py and"
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
        **window.clock(record, state, now),
    }


def pre_create_check() -> int:
    """Rung 0 — the computation, and the verdict RECORDED whichever way it goes."""
    record = registration()
    state = json.loads(RECORD.read_text(encoding="utf-8")) if RECORD.exists() else {}
    pod = window.live_pod(state)
    if pod is not None:
        gate = {
            "rung": 0,
            "verdict": "KILL",
            "cause": f"pod {pod['pod_id']} is OPEN in {window.rel(RECORD)} and has no deleted_at",
            "verdict_is_an_instruction": True,
            "next_step": (
                "never two billing endpoints at once — delete it, prove it by listing, and --close"
                " first"
            ),
        }
    else:
        gate = pre_create(record, state)
        gate["what_this_authorises"] = record["money"]["arithmetic"]["total_seconds_rule"]
    print(json.dumps(gate, ensure_ascii=False, indent=2, sort_keys=True))
    print(f"\n{gate['verdict']}  ·  {gate['next_step']}")
    state.setdefault("pods", [])
    window.append_gate(state, gate, "pre-create-check")
    return GO if gate["verdict"] == "GO" else KILL


for _name, _value in (
    ("authorised", authorised),
    ("legs_of", legs_of),
    ("leg_state", leg_state),
    ("fingerprint", fingerprint),
    ("first_reply_after_launch", first_reply_after_launch),
    ("pre_create", pre_create),
    ("completeness", completeness),
):
    for _module in (r2, window):
        if hasattr(_module, _name):
            setattr(_module, _name, _value)


def main(argv: list[str] | None = None, now=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--go-no-go" in argv:
        raise SystemExit(
            "r2 has no go/no-go. The rate is registered — 97 s/thread, the smoke's max × the"
            " measured pod-class spread — so the decision rung S′ took in the middle of r1's"
            " session was taken by the operator before this create. There is nothing here to"
            " authorise mid-run."
        )
    if "--pre-create-check" in argv:
        if len(argv) != 1:
            raise SystemExit("--pre-create-check takes no other flags — it reads the record alone.")
        return pre_create_check()
    return window.main(argv, now)


if __name__ == "__main__":
    raise SystemExit(main())
