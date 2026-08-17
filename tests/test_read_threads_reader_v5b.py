"""reader-v5b's transport — the segments, gate 0, and the pack in the registered order.

Everything about the instrument is v5's and is tested in `test_read_threads_reader_v5.py`; what is
exercised here is only what a second pod in one attempt makes possible, and every path that can spend
money. The two clocks are driven at a moment and asked for a verdict rather than read off a record:
`elapsed` is always a segment's own, the money is always the attempt's, and the tests are written so
that confusing the two fails.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import read_threads_reader_v5 as v5  # noqa: E402
import read_threads_reader_v5b as driver  # noqa: E402

RECORD = json.loads(
    (REPO_ROOT / "results" / "prereg_reader_probe_v5b.json").read_text(encoding="utf-8")
)
V5_RECORD = json.loads(
    (REPO_ROOT / "results" / "prereg_reader_probe_v5.json").read_text(encoding="utf-8")
)
PACK_PATH = REPO_ROOT / "results" / "reader_v5b_pack.json"
PACK = json.loads(PACK_PATH.read_text(encoding="utf-8"))
CREATED = "2026-08-17T18:00:00+00:00"
RATE = 0.74 / 3600.0


def a_segment(pod_id="pod-1", created_at=CREATED, usd_per_hour=0.74, **rest) -> dict:
    return {
        "segment": 1,
        "pod_id": pod_id,
        "created_at": created_at,
        "card": "NVIDIA GeForce RTX 4090",
        "usd_per_hour": usd_per_hour,
        "usd_per_second": round(usd_per_hour / 3600.0, 9),
        "deleted_at": None,
        "billed_seconds": None,
        "billed_usd": None,
        "outcome": None,
        **rest,
    }


def closed(segment: dict, billed: float) -> dict:
    return segment | {
        "deleted_at": "2026-08-17T18:04:00+00:00",
        "billed_seconds": billed,
        "billed_usd": round(billed * segment["usd_per_second"], 6),
        "outcome": "gate 0 KILL",
    }


@pytest.fixture
def opened(tmp_path, monkeypatch):
    """A run record with one live segment, on a path the tests own."""
    monkeypatch.setattr(driver, "RECORD", tmp_path / "run.json")
    monkeypatch.setattr(driver, "PACK", PACK_PATH)
    monkeypatch.setattr(driver, "registration", lambda: RECORD)

    def write(segments: list[dict]) -> dict:
        state = {"phase": "reader-v5b", "segments": segments, "gates": []}
        (tmp_path / "run.json").write_text(json.dumps(state), encoding="utf-8")
        return state

    return write


# --- the pack -------------------------------------------------------------------------------------


def test_the_pack_is_the_registered_order_and_carries_the_v5b_registration():
    """The registered order is v5's own — the descending-payable ruling was withdrawn before any pod,
    on the gate table the registration publishes."""
    assert len(PACK["items"]) == 26
    assert "".join(one["leg"] for one in PACK["items"]) == "A" * 23 + "B" * 3
    assert [one["payable_comments"] for one in PACK["items"]] == [
        7, 2, 12, 4, 5, 5, 2, 2, 5, 10, 9, 12, 8, 3, 9, 12, 15, 2, 3, 2, 1, 0, 4, 16, 16, 11
    ]  # fmt: skip
    assert PACK["phase"] == "reader-v5b"
    assert PACK["registration"]["record"] == "results/prereg_reader_probe_v5b.json"
    assert PACK["items"][0]["id"] == "@VARUS_channel:10348"
    assert [one["id"] for one in PACK["items"]] == [
        one["thread"] for one in RECORD["population"]["leg_a"]["enumeration"]["threads"]
    ] + [one["id"] for one in RECORD["population"]["leg_b"]["items"]]


def test_the_pack_is_v5s_pack_and_not_a_second_population():
    """The units and their rendering shas against the frozen v5 record. A pack that re-rendered
    anything would be a new population wearing an old digest."""
    pinned = {
        one["thread"]: one["rendering_sha256"]
        for one in V5_RECORD["population"]["leg_a"]["enumeration"]["threads"]
    } | {one["id"]: one["rendering_sha256"] for one in V5_RECORD["population"]["leg_b"]["items"]}
    assert {one["id"]: one["rendering_sha256"] for one in PACK["items"]} == pinned
    assert PACK["serving"] == V5_RECORD["instruments"]["serving"] | {"output_tokens": 4000}
    assert PACK["task"] == "reader_thread_gm4_v5"


def test_the_swap_puts_the_siblings_constants_back_even_when_the_call_raises():
    """A module left pointing at another phase's files is a bug that only shows up in the second
    command — and one of those commands deletes a pod."""
    before = {name: getattr(v5, name) for name in driver.SWAPPED}
    with driver.as_this_phase():
        assert v5.PACK == driver.PACK and v5.PHASE == "reader-v5b"
    assert {name: getattr(v5, name) for name in driver.SWAPPED} == before
    with pytest.raises(RuntimeError), driver.as_this_phase():
        raise RuntimeError("boom")
    assert {name: getattr(v5, name) for name in driver.SWAPPED} == before


def test_the_swap_reads_the_constants_at_CALL_time(monkeypatch, tmp_path):
    """Frozen into a dict at import, the swap would hand the sibling the original path while this
    module used the new one — and the gate's refusal would name a file nobody wrote."""
    monkeypatch.setattr(driver, "PACK", tmp_path / "elsewhere.json")
    with driver.as_this_phase():
        assert v5.PACK == tmp_path / "elsewhere.json"


# --- never two pods, and the third pod -----------------------------------------------------------


def test_never_two_pods_is_a_check_BEFORE_create_and_not_a_refusal_after_it(opened, capsys):
    opened([a_segment()])
    with pytest.raises(SystemExit, match="two meters never run at once"):
        driver.main(["--pre-create-check"])
    # closed, and the replacement may be created
    opened([closed(a_segment(), 240.0)])
    assert driver.main(["--pre-create-check"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["may_create"] is True
    assert printed["segment"] == 1 and printed["segments_allowed"] == 3
    assert printed["billed_seconds_closed_segments"] == 240.0


def test_the_third_dead_pod_is_a_STOP_before_anything_is_created(opened):
    opened(
        [
            closed(a_segment("pod-1"), 240.0),
            closed(a_segment("pod-2") | {"segment": 2}, 240.0),
            closed(a_segment("pod-3") | {"segment": 3}, 240.0),
        ]
    )
    with pytest.raises(SystemExit, match="DATACENTER STATE"):
        driver.main(["--pre-create-check"])


def test_open_refuses_a_second_live_segment_and_the_ledger_must_exist_first(opened, monkeypatch):
    opened([a_segment()])
    monkeypatch.setattr(driver, "LEDGER", REPO_ROOT / "results" / "spend_reader_v5.json")
    with pytest.raises(SystemExit, match="Never two pods at once"):
        driver.main(
            [
                "--open",
                "--pod-id",
                "pod-2",
                "--created-at",
                CREATED,
                "--usd-per-hour",
                "0.74",
                "--card",
                "NVIDIA GeForce RTX 4090",
            ]
        )
    monkeypatch.setattr(driver, "LEDGER", REPO_ROOT / "results" / "does-not-exist.json")
    opened([closed(a_segment(), 240.0)])
    with pytest.raises(SystemExit, match="the step's spend anchor is written by"):
        driver.main(
            [
                "--open",
                "--pod-id",
                "pod-2",
                "--created-at",
                CREATED,
                "--usd-per-hour",
                "0.74",
                "--card",
                "NVIDIA GeForce RTX 4090",
            ]
        )


# --- gate 0 ---------------------------------------------------------------------------------------


def test_gate_zero_waits_before_180_seconds_and_KILLS_at_it(opened):
    state = opened([a_segment()])
    early = driver.gate_zero(RECORD, state, elapsed=179.0, ssh_ok=False)
    assert early["verdict"] == "WAIT" and early["seconds_left"] == 1.0
    assert "keep polling" in early["next_step"]
    at = driver.gate_zero(RECORD, state, elapsed=180.0, ssh_ok=False)
    assert at["verdict"] == "KILL" and at["seconds_left"] == 0.0
    assert "delete, prove it by listing" in at["next_step"]
    assert at["recreates_left"] == 2


def test_gate_zero_GOES_the_moment_the_endpoint_answers_however_late(opened):
    """The threshold is a dead-man and not a schedule: a pod that answers at 179 s is alive, and the
    reason to record the GO is that the boot clock starts from it."""
    state = opened([a_segment()])
    gate = driver.gate_zero(RECORD, state, elapsed=179.0, ssh_ok=True)
    assert gate["verdict"] == "GO" and gate["next_step"] == "stage and launch"


def test_gate_zero_on_the_LAST_allowed_segment_says_STOP_and_not_recreate(opened):
    state = opened(
        [
            closed(a_segment("pod-1"), 240.0),
            closed(a_segment("pod-2") | {"segment": 2}, 240.0),
            a_segment("pod-3") | {"segment": 3},
        ]
    )
    gate = driver.gate_zero(RECORD, state, elapsed=200.0, ssh_ok=False)
    assert gate["verdict"] == "KILL" and gate["recreates_left"] == 0
    assert "the attempt closes" in gate["next_step"]


def test_every_gate_snapshot_carries_its_SEGMENT_and_that_segments_pod_id(opened, tmp_path):
    state = opened([closed(a_segment("pod-1"), 240.0), a_segment("pod-2") | {"segment": 2}])
    driver.append_gate(state, {"verdict": "WAIT"}, "gate0")
    driver.append_gate(state, {"verdict": "GO"}, "gate0")
    written = json.loads((tmp_path / "run.json").read_text(encoding="utf-8"))
    assert [one["segment"] for one in written["gates"]] == [2, 2]
    assert {one["pod_id"] for one in written["gates"]} == {"pod-2"}
    assert written["latest"] == {"kind": "gate0", "verdict": "GO", "segment": 2}


# --- the money: one cap, several segments ---------------------------------------------------------


def test_a_closed_segment_is_priced_at_ITS_OWN_rate_and_never_a_balance_delta(opened):
    state = opened(
        [
            closed(a_segment("pod-1", usd_per_hour=0.74), 240.0),
            closed(a_segment("pod-2", usd_per_hour=0.99) | {"segment": 2}, 120.0),
        ]
    )
    seconds, usd = driver.spent_before(state)
    assert seconds == 360.0
    # each leg is stored rounded to the microdollar, so the sum agrees to that and no further
    assert usd == pytest.approx(240.0 * 0.74 / 3600 + 120.0 * 0.99 / 3600, abs=1e-6)
    # the same seconds at ONE rate would be wrong by 0.8 of a cent, which is the whole point
    assert usd - 360.0 * 0.74 / 3600 == pytest.approx(0.0083, abs=1e-4)


def test_the_affordability_leg_shrinks_by_what_EARLIER_segments_billed(opened):
    """The contract's rule, driven: (cap − spent across all segments) against the reading projection.
    Two dead pods cost 480 s and the third segment's usable seconds are 480 s shorter."""
    alone = driver.deadlines(RECORD, opened([a_segment()]), elapsed=10.0, generation_at=None)
    third = driver.deadlines(
        RECORD,
        opened(
            [
                closed(a_segment("pod-1"), 240.0),
                closed(a_segment("pod-2") | {"segment": 2}, 240.0),
                a_segment("pod-3") | {"segment": 3},
            ]
        ),
        elapsed=10.0,
        generation_at=None,
    )
    assert alone["usable_seconds_this_segment"] == pytest.approx(2372.4, abs=0.1)
    assert third["usable_seconds_this_segment"] == pytest.approx(2372.4 - 480.0, abs=0.1)
    assert third["billed_seconds_closed_segments"] == 480.0
    assert third["first_reply_must_land_by_create_elapsed"] == pytest.approx(
        alone["first_reply_must_land_by_create_elapsed"] - 480.0, abs=0.1
    )
    # and the registration's own table says the same thing about three segments
    rows = RECORD["money"]["segments"]["at_each_segment_count"]
    assert rows[2]["usable_seconds"] == pytest.approx(third["usable_seconds_this_segment"], abs=0.1)


def test_the_cap_in_a_gate_snapshot_is_the_ATTEMPTS_and_the_remainder_is_named_apart(opened):
    """The reduced cap is an implementation detail of reusing one inequality; a field called
    `cap_usd_all_in` that shrank would be a lie in the record every bar 5 is read against."""
    state = opened([closed(a_segment("pod-1"), 240.0), a_segment("pod-2") | {"segment": 2}])
    rows = [{"id": PACK["items"][0]["id"], "seconds": 40.0}]
    gate = driver.projection(RECORD, state, rows, elapsed=300.0, pack=PACK)
    assert gate["usd"]["cap_usd_all_in"] == 0.50
    assert gate["usd"]["cap_left_for_this_segment_usd"] == pytest.approx(
        0.50 - 240.0 * RATE, abs=1e-6
    )
    assert gate["usd"]["spent_this_segment_usd"] == pytest.approx(300.0 * RATE, abs=1e-4)
    assert gate["usd"]["spent_all_segments_usd"] == pytest.approx(540.0 * RATE, abs=1e-4)
    assert gate["elapsed_since_create_seconds"] == 300.0
    assert gate["units_read"] == 1 and gate["units_unread"] == 25


def test_a_segment_is_closed_once_and_a_second_close_is_refused(opened, tmp_path):
    opened([a_segment()])
    assert driver.main(["--close-segment", "--deleted-at", "2026-08-17T18:04:00+00:00"]) == 0
    written = json.loads((tmp_path / "run.json").read_text(encoding="utf-8"))
    segment = written["segments"][-1]
    assert segment["billed_seconds"] == 240.0
    assert segment["billed_usd"] == pytest.approx(240.0 * RATE, abs=1e-6)
    with pytest.raises(SystemExit, match="already closed"):
        driver.main(["--close-segment", "--deleted-at", "2026-08-17T18:09:00+00:00"])


# --- the resume protocol -------------------------------------------------------------------------


def test_normalize_drops_a_torn_last_line_as_a_BYTE_PREFIX_and_refuses_a_middle_one(tmp_path):
    """What goes back up to a replacement pod has whole lines only, and every reply that landed is
    left exactly as the pod wrote it — the drop is a slice and never a re-serialisation."""
    path = tmp_path / "pod.jsonl"
    whole = json.dumps({"id": "a", "reply": "{}", "seconds": 1.0}, ensure_ascii=False)
    path.write_text(f'{whole}\n{{"id": "b", "sec', encoding="utf-8")
    report = driver.normalize(path)
    assert report["dropped_a_torn_last_line"] is True
    assert report["dropped_chars"] == len('{"id": "b", "sec')
    assert report["rows"] == 1
    assert path.read_text(encoding="utf-8") == f"{whole}\n"

    # idempotent: a clean file is left alone, byte for byte
    again = driver.normalize(path)
    assert again["dropped_a_torn_last_line"] is False and again["rows"] == 1
    assert path.read_text(encoding="utf-8") == f"{whole}\n"

    path.write_text(f'{{"id": "b", "sec\n{whole}\n', encoding="utf-8")
    with pytest.raises(SystemExit, match="do not send it back"):
        driver.normalize(path)


def test_normalize_says_so_when_there_is_nothing_to_normalize(tmp_path):
    with pytest.raises(SystemExit, match="nothing to normalize"):
        driver.normalize(tmp_path / "never-written.jsonl")


def test_the_normalized_file_is_what_both_readers_then_agree_on(tmp_path):
    """The end of the chain: normalize on the Mac, resume on the pod, gate on the Mac — and no reader
    meets a torn middle line ([[the_hardening_did_not_reach_the_sibling_reader]])."""
    import reader_v5_pod_runner as pod

    path = tmp_path / "pod.jsonl"
    whole = json.dumps({"id": PACK["items"][0]["id"], "reply": "{}", "seconds": 1.0})
    path.write_text(f'{whole}\n{{"id": "torn", "rep', encoding="utf-8")
    driver.normalize(path)
    rows, torn = pod.whole_lines(path.read_text(encoding="utf-8"), str(path))
    assert torn is None and [row["id"] for row in rows] == [PACK["items"][0]["id"]]
    assert [row["id"] for row in driver.raw_rows(path)] == [PACK["items"][0]["id"]]
