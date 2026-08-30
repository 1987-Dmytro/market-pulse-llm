"""The r2 pass's pacing floor, derived from the record it shipped — not from what it printed.

The contract's floor is ≥3 s between requests, and `entry_check.PAUSE_SECONDS` is 2.0: inheriting
the module constant would have run the floor at two thirds with every line still reading like
compliance. `step_2.pause_seconds_measured_min` cannot carry the proof — a later single-handle pass
has no gap and overwrites it — so the proof is the rows' own `checked_at` stamps, which no pass
rewrites ([[a_flag_that_asserts_turns_a_poll_into_a_verdict]]).
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from retail_resolve_r2 import PAUSE_SECONDS  # noqa: E402

RECORD = Path(__file__).resolve().parents[1] / "results" / "retail_chains.json"


def stamps() -> list[datetime]:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    out = [
        datetime.fromisoformat(m["checked_at"])
        for row in record["rows"]
        for m in row.get("measured", [])
        if m.get("checked_at")
    ]
    return sorted(out)


def test_the_floor_the_script_carries_is_the_contract_s():
    assert PAUSE_SECONDS >= 3.0


def test_every_gap_the_record_stamped_clears_the_floor():
    times = stamps()
    assert len(times) >= 8, "the record should carry every resolved candidate's stamp"
    gaps = [(b - a).total_seconds() for a, b in zip(times, times[1:])]
    assert min(gaps) >= PAUSE_SECONDS, f"pacing broke the floor: {min(gaps)}s < {PAUSE_SECONDS}s"


def test_the_budget_ceiling_bound_and_was_not_exceeded():
    step2 = json.loads(RECORD.read_text(encoding="utf-8"))["step_2"]
    assert step2["requests_all_passes"] == sum(p["requests"] for p in step2["passes"])
    assert step2["requests_all_passes"] <= step2["budget"]
