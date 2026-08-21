#!/usr/bin/env python3
"""pass1-window r2 — the Mac half of the ONE paid session, and it is r1's gate under r2's paths.

**Why this file is a SIBLING and not a `--revision r2` flag.**
`docs/PROMPT-pass1-window-r2.md` D0′ allows the flag «ONLY if that leaves r1's pinned bytes
untouched — otherwise a sibling, and say which». `scripts/gate_pass1_window.py` is pinned by
`results/prereg_pass1_window.json::instruments.gate.sha256` (8b812597c4ea…), a SEALED record of a
closed paid session. Any flag added to that file moves those bytes. So: a sibling. Dv624's split
stands.

**And here is exactly what kind of sibling.** r1's gate is a sibling of `gate_pass1_fewshot.py` in
the ordinary way — it imports the pure rung computations and RE-DECLARES the ones bound to module
paths, ~570 lines of them. Doing that again would copy `watch` (138 lines) and `main` (297) a third
time, and a copy is where two instruments start to disagree about the same question.

What is bound to a path in r1's gate is bound through a MODULE GLOBAL and nothing else — the AST says
so: `registration` reads `PREREG`, `run_state`/`save` read `RECORD`, `launched_at_of` reads
`LAUNCH_STAMP`, `main` reads `PACK` and `POD_LOG`, and every other path-bound function reaches them
through those. So this file loads that same source ONE MORE TIME, as its own module object, and
re-binds those six names. The rung logic is not copied, not re-implemented and not imported
piecemeal: it is r1's, executing, byte for byte, against r2's registration.

* the load is `importlib.util.spec_from_file_location` + `module_from_spec` — the stdlib's own way to
  hold one source as two modules. The new module is NOT registered in `sys.modules`, so
  `import gate_pass1_window` anywhere else (the r1 census does exactly that) still gets the r1-bound
  module with r1's paths untouched. There is a test that asserts precisely that.
* the source is held to the sha the r1 record pins BEFORE it is executed. If r1's gate ever moves,
  this file refuses to run rather than quietly becoming a different instrument
  ([[the_guard_hashes_the_half_that_cannot_move]]).
* `--pre-create-check` is the ONE behaviour that changes, and it is the step 0.5 finding: r1's
  version printed its verdict and returned without recording it, so the refusal that ended the r1
  session existed only in a terminal. Here it is intercepted before r1's `main` sees it, and its
  verdict is APPENDED to the run record every time it runs — GO and KILL alike.

Everything else — every threshold, every rung, the watch loop, rung 7's completeness bar — is read
out of `results/prereg_pass1_window_r2.json` by r1's own code. Exit codes are r1's: 0 GO, 2
KILL/STOP, 3 WAIT.

    PYTHONPATH=src python3.11 scripts/gate_pass1_window_r2.py --pre-create-check
    PYTHONPATH=src python3.11 scripts/gate_pass1_window_r2.py --price --pod-id <ID> \\
        --created-at <UTC ISO8601> --usd-per-hour <costPerHr> --card '<the card>' \\
        --terminate-after '<the stamp `pod create` was actually given>'
    PYTHONPATH=src python3.11 scripts/gate_pass1_window_r2.py --gate0 [--ssh-ok]
    PYTHONPATH=src python3.11 scripts/gate_pass1_window_r2.py --boot
    PYTHONPATH=src python3.11 scripts/gate_pass1_window_r2.py --watch --ssh root@<HOST> \\
        --ssh-port <PORT>
    PYTHONPATH=src python3.11 scripts/gate_pass1_window_r2.py --projection
    PYTHONPATH=src python3.11 scripts/gate_pass1_window_r2.py --completeness
    PYTHONPATH=src python3.11 scripts/gate_pass1_window_r2.py --close --deleted-at <UTC ISO8601> \\
        --outcome '<why this pod ended>'
"""

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import window_summary_5c2 as summary  # noqa: E402

R1_GATE = REPO_ROOT / "scripts" / "gate_pass1_window.py"
R1_PREREG = REPO_ROOT / "results" / "prereg_pass1_window.json"

PHASE = "pass1-window-r2"
PREREG = REPO_ROOT / "results" / "prereg_pass1_window_r2.json"
RECORD = REPO_ROOT / "results" / "pass1_window_r2_run.json"
PACK = REPO_ROOT / "results" / "pass1_window_r2_pack.json"
POD_LOG = REPO_ROOT / "results" / "pass1_window_r2_pod.log"
LAUNCH_STAMP = "pass1_window_r2_launched_at"
"""This attempt's OWN names for every file a rung reads or writes. `results/` already holds
`pass1_window_launched_at`, `pass1_window_pod.log` and `pass1_window_run.json` from the closed r1
session, and a rung that read one of them would be reading a dead pod's clock (Dv621/632)."""

REBOUND = ("PHASE", "PREREG", "RECORD", "PACK", "POD_LOG", "LAUNCH_STAMP")


def _load() -> object:
    """r1's gate, executed as its own module object and re-bound to this attempt's paths."""
    pinned = json.loads(summary.read_text_or_refuse(R1_PREREG))["instruments"]["gate"]["sha256"]
    live = summary.sha256_of(R1_GATE)
    if live != pinned:
        raise SystemExit(
            f"{summary.rel(R1_GATE)} hashes {live} and {summary.rel(R1_PREREG)} pins {pinned}. This"
            " gate RUNS that file's rung logic, so a file that has moved is a different instrument"
            " answering the same question. Stop and report — r1's gate is pinned by a sealed record"
            " of a closed paid session and may not be edited."
        )
    spec = importlib.util.spec_from_file_location("gate_pass1_window_r1_source", R1_GATE)
    module = importlib.util.module_from_spec(spec)
    # NOT registered in sys.modules: `import gate_pass1_window` elsewhere must keep r1's own paths
    spec.loader.exec_module(module)
    for name in REBOUND:
        if not hasattr(module, name):
            raise SystemExit(
                f"{summary.rel(R1_GATE)} has no module global {name}. This sibling works by"
                " re-binding that gate's path globals, and a name it does not carry is a path this"
                " file would silently fail to move. Stop and report."
            )
        setattr(module, name, globals()[name])
    return module


r1 = _load()

GO, KILL, WAIT = r1.GO, r1.KILL, r1.WAIT


def pre_create_check() -> int:
    """Rung 0 — r1's own computation, and the verdict RECORDED whichever way it goes.

    Step 0.5's second finding, closed here: r1 printed this verdict and returned. A guard whose
    verdict lives only in a terminal is not a record ([[gate_verdicts_need_an_artifact]]), and the
    refusal that ENDED the r1 session is the one that proved it.
    """
    # `r1.RECORD` and not this module's RECORD: the bound module is where the path LIVES once
    # `_load` has run, and every other rung reads it there. Two homes for one path is how a test
    # redirects the state file and a guard goes on writing to the real one
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
    print(json.dumps(gate, ensure_ascii=False, indent=2, sort_keys=True))
    print(f"\n{gate['verdict']}  ·  {gate['next_step']}")
    state.setdefault("pods", [])
    r1.append_gate(state, gate, "pre-create-check")
    return GO if gate["verdict"] == "GO" else KILL


def main(argv: list[str] | None = None, now=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--pre-create-check" in argv:
        if len(argv) != 1:
            raise SystemExit("--pre-create-check takes no other flags — it reads the record alone.")
        return pre_create_check()
    return r1.main(argv, now)


if __name__ == "__main__":
    raise SystemExit(main())
