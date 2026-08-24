#!/usr/bin/env python3
"""`scripts/pass2_r2_pod_runner.py` at r2's OWN ceiling — a sibling of eleven lines, not a fork.

**The mismatch this closes, measured at $0.** `pass2_r2.PASS2_MAX_INPUT_CHARS` is 15 569 and it is
what `results/lora_c_pass2_pack.json` declares as `instruments.ceiling_chars`. But
`pass2_r2_pod_runner.render` calls `pass2.pass2_messages_gm4`, which reads
`pass2.PASS2_MAX_INPUT_CHARS` — **12 000** — as a module global at call time. So a unit between the
two ceilings builds on the Mac and RAISES on the pod, inside `check_requests`, before a single reply.

pass2-signals-r2 never met it: its widest unit was 11 856. This line can. The pass-2 pack is rebuilt
from an ARM's pass-1 answers, and a thread's rendered size grows with the number of rows pass 1
marked `OURS` — so an adapter that marks more of them renders wider than the window's v2 leg did.
Bounded rather than hoped for, in `build_lora_c_pass2_pack.the_widest_a_leg_can_render`: with EVERY
row of every reference thread filtered in, exactly one thread crosses 12 000 — `@matusi_ukr:22272`
at 12 399 — and none crosses 15 569 (3 170 of headroom). That thread is a FLAGSHIP thread of bar 1,
so it cannot be dropped: a bar with a missing case is not a bar
([[an_absolute_bar_needs_a_reachability_state]]).

`scripts/pass2_r2_pod_runner.py` is pinned by `results/prereg_pass2_signals_r2.json` and is not
edited. `pass2_r2._ceiling` is the contextmanager that module already owns for exactly this, and
`main` is CALLED inside it — nothing here is copied.

    HF_HOME=/workspace/hf PYTHONPATH=/workspace/repo/src \\
    /workspace/venv/bin/python -u /workspace/repo/scripts/pass2_lora_c_pod_runner.py \\
        --pack /workspace/lora_c_pass2_arm_a.json --outdir /workspace/run/pass2_a \\
        --repo /workspace/repo
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pass2_r2_pod_runner as sibling  # noqa: E402

from market_pulse import pass2, pass2_r2  # noqa: E402


def main(argv: list[str] | None = None, loader=None) -> int:
    """r2's runner, with r1's renderer refusing at r2's ceiling for the length of the call.

    The assertion first: if the two ceilings were ever made equal, this file would be a pointless
    layer between the pod and its runner, and silence is the wrong way to find that out.
    """
    if pass2_r2.PASS2_MAX_INPUT_CHARS <= pass2.PASS2_MAX_INPUT_CHARS:
        raise SystemExit(
            f"pass2_r2's ceiling is {pass2_r2.PASS2_MAX_INPUT_CHARS} and pass2's is"
            f" {pass2.PASS2_MAX_INPUT_CHARS} — this file exists to raise the first above the"
            " second. Run scripts/pass2_r2_pod_runner.py directly and delete this one."
        )
    with pass2_r2._ceiling(pass2_r2.PASS2_MAX_INPUT_CHARS):
        return sibling.main(argv, loader=loader)


if __name__ == "__main__":
    raise SystemExit(main())
