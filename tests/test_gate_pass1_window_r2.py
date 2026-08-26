"""The r2 gate — the sibling that RUNS r1's bytes, and the four scenarios the contract names.

Three properties belong to this file and to nothing else.

* **Loading r1's gate a second time must not move r1's gate.** The census imports
  `gate_pass1_window` and expects r1's paths on it. The sibling re-binds a SEPARATE module object,
  never registers it in `sys.modules`, and there is a negative control for every one of the six
  globals ([[rewriting_a_record_resets_state_you_do_not_own]]).
* **The bytes it runs are the bytes r1's sealed record pins.** If that file ever moves, the sibling
  refuses instead of quietly becoming a different instrument.
* **`--pre-create-check` records its verdict.** r1's printed the refusal that ended its session and
  wrote nothing down — step 0.5's second finding. Both verdicts are driven.

Then the scenarios `docs/PROMPT-pass1-window-r2.md` D0′ asks for, in both directions, on the fake
transport and with no pod anywhere.
"""

import json
import sys
from datetime import timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import gate_pass1_window as r1gate  # noqa: E402
import moved_pins  # noqa: E402
import gate_pass1_window_r2 as gate  # noqa: E402
import volume_tail_pass1_window as tail  # noqa: E402

RECORD = json.loads((REPO_ROOT / "results" / "prereg_pass1_window_r2.json").read_text("utf-8"))
PACK = moved_pins.servable(
    json.loads((REPO_ROOT / "results" / "pass1_window_r2_pack.json").read_text("utf-8"))
)
"""The sealed pack with its ONE moved pin brought up to date, in memory only — ruling (ф) moved
`src/market_pulse/prompts.py` and the handshake refuses the sealed value, correctly. The file on
disk is never written and the registered prompt shas are untouched ([[tests/moved_pins.py]])."""
SUMS = RECORD["money"]["arithmetic"]
HARD_STOP = SUMS["cumulative"]["hard_stop_seconds"]
OVERHEAD = SUMS["overhead_seconds"]
CHARGED_PRE_GENERATION = SUMS["pre_generation_seconds"]
MEASURED_PRE_GENERATION = SUMS["cumulative"]["projection_gate"]["single_call_sensitivity"][
    "at_the_MEASURED_pre_generation"
]["pre_generation_seconds"]
WIDEST_DEAD_POD = SUMS["recovery_arithmetic"]["widest_dead_pod_that_still_fits_seconds"]
CALLS = SUMS["calls"]["v2"]
CREATE = "2026-08-22T09:00:00+00:00"


def at(seconds: float, created: str = CREATE):
    return r1gate.stamp(created) + timedelta(seconds=seconds)


@pytest.fixture
def run(tmp_path, monkeypatch):
    """The r2 gate with its state in tmp_path — and r1's record redirected to a SENTINEL."""
    monkeypatch.setattr(gate.r1, "RECORD", tmp_path / "pass1_window_r2_run.json")
    monkeypatch.setattr(gate.r1, "POD_LOG", tmp_path / "pod.log")
    monkeypatch.setattr(gate.r1, "registration", lambda: RECORD)
    sentinel = tmp_path / "r1_must_not_move.json"
    sentinel.write_text('{"sealed": true}\n', encoding="utf-8")
    monkeypatch.setattr(r1gate, "RECORD", sentinel)
    monkeypatch.setattr(r1gate, "POD_LOG", tmp_path / "r1_pod.log")
    gate.SENTINEL = sentinel
    return gate


def sealed_is_untouched(run) -> bool:
    return run.SENTINEL.read_text("utf-8") == '{"sealed": true}\n'


def backstop_for(run, created: str) -> str:
    state = json.loads(run.r1.RECORD.read_text("utf-8")) if run.r1.RECORD.exists() else {}
    left = HARD_STOP - r1gate.billed_before(state)[0]
    return (r1gate.stamp(created) + timedelta(seconds=left)).isoformat(timespec="seconds")


def opened(run, *, usd_per_hour=0.74, created=CREATE, pod_id="pod-1"):
    return run.main(
        [
            "--price",
            "--pod-id",
            pod_id,
            "--created-at",
            created,
            "--usd-per-hour",
            str(usd_per_hour),
            "--card",
            "NVIDIA GeForce RTX 4090",
            "--terminate-after",
            backstop_for(run, created),
        ],
        now=at(5, created),
    )


def answered(where: Path, leg: dict, n: int, seconds: float, elapsed0: float) -> None:
    where.mkdir(parents=True, exist_ok=True)
    lines = []
    for index, item in enumerate(leg["items"][:n]):
        lines.append(
            json.dumps(
                {
                    "index": index,
                    "id": item["id"],
                    "rendering_sha256": item["rendering_sha256"],
                    "reply": json.dumps(
                        {
                            "msg_id": int(item["msg_id"]),
                            "subject_type": "не_наш_рынок",
                            "subject_id": None,
                            "stance": None,
                        },
                        ensure_ascii=False,
                    ),
                    "balanced": True,
                    "seconds": seconds,
                    "elapsed_since_start": elapsed0 + index * seconds,
                    "boot_seconds": elapsed0,
                },
                ensure_ascii=False,
            )
        )
    (where / leg["out"]).write_text("\n".join(lines) + "\n", encoding="utf-8")


def projected(run, where: Path, elapsed: float) -> dict:
    state = json.loads(run.r1.RECORD.read_text("utf-8"))
    legs = r1gate.leg_state(RECORD, [PACK], where)
    return r1gate.projection(RECORD, state, legs, at(elapsed))


# --- the sibling itself ------------------------------------------------------------------------


def test_loading_r1s_gate_again_leaves_r1s_gate_alone():
    for name in gate.REBOUND:
        assert getattr(gate.r1, name) != getattr(r1gate, name), name
    assert gate.r1 is not r1gate
    assert "gate_pass1_window_r1_source" not in sys.modules
    # the PURE rungs are the same objects — the logic is not copied, it is r1's, executing
    for name in ("pre_create", "clock", "leg_state", "projection", "gate_zero", "gate_boot"):
        assert getattr(gate.r1, name) is getattr(r1gate, name), name
    # and the path-bound ones are r1's SOURCE re-executed, so they are distinct functions
    for name in ("registration", "run_state", "save", "append_gate", "watch", "completeness"):
        assert getattr(gate.r1, name) is not getattr(r1gate, name), name


def test_the_sibling_refuses_to_run_r1s_gate_if_its_bytes_have_MOVED(tmp_path, monkeypatch):
    moved = tmp_path / "gate.py"
    moved.write_text(
        (REPO_ROOT / "scripts" / "gate_pass1_window.py").read_text("utf-8") + "\n# moved\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(gate, "R1_GATE", moved)
    with pytest.raises(SystemExit, match="a different instrument answering the same question"):
        gate._load()


def test_the_sibling_names_its_OWN_record_stamp_log_and_pack():
    assert gate.r1.RECORD.name == "pass1_window_r2_run.json"
    assert gate.r1.LAUNCH_STAMP == "pass1_window_r2_launched_at"
    assert gate.r1.POD_LOG.name == "pass1_window_r2_pod.log"
    assert gate.r1.PACK.name == "pass1_window_r2_pack.json"
    assert gate.r1.PHASE == "pass1-window-r2"
    # r1's three are really on disk in results/, so a shared name would read a dead pod's clock
    assert (REPO_ROOT / "results" / r1gate.LAUNCH_STAMP).exists()
    assert r1gate.POD_LOG.exists()
    assert r1gate.RECORD.exists()


# --- --pre-create-check, and the verdict it RECORDS ---------------------------------------------


def test_pre_create_check_RECORDS_its_GO(run, capsys):
    assert run.main(["--pre-create-check"]) == r1gate.GO
    state = json.loads(run.r1.RECORD.read_text("utf-8"))
    entry = state["gates"][-1]
    assert entry["kind"] == "pre-create-check"
    assert entry["verdict"] == "GO"
    assert entry["pods_opened"] == 0
    assert entry["worst_case_ahead_seconds"] == SUMS["total_seconds"]
    assert entry["widest_dead_pod_that_still_fits_seconds"] == WIDEST_DEAD_POD
    assert "GO" in capsys.readouterr().out
    assert sealed_is_untouched(run)


def test_pre_create_check_RECORDS_its_KILL_and_the_open_pod_case_too(run):
    """r1's printed both and recorded neither — the refusal that ended its session included."""
    assert opened(run) == r1gate.GO
    assert run.main(["--pre-create-check"]) == r1gate.KILL
    state = json.loads(run.r1.RECORD.read_text("utf-8"))
    entry = state["gates"][-1]
    assert entry["kind"] == "pre-create-check"
    assert entry["verdict"] == "KILL"
    assert "is OPEN" in entry["cause"]
    assert entry["verdict_is_an_instruction"] is True


def test_pre_create_check_takes_no_other_flags(run):
    with pytest.raises(SystemExit, match="takes no other flags"):
        run.main(["--pre-create-check", "--clock"])


# --- the recovery arithmetic, at the knife edge -------------------------------------------------


def close_pod(run, *, seconds: float, created: str, pod_id: str) -> None:
    assert opened(run, created=created, pod_id=pod_id) == r1gate.GO
    assert (
        run.main(
            [
                "--close",
                "--deleted-at",
                at(seconds, created).isoformat(timespec="seconds"),
                "--outcome",
                "rung 2 dead-man",
            ],
            now=at(seconds + 1, created),
        )
        == r1gate.GO
    )


@pytest.mark.parametrize(
    ("dead_seconds", "verdict"),
    [(667.0, "GO"), (669.0, "KILL")],
)
def test_the_recovery_clause_at_667_and_at_669(run, dead_seconds, verdict):
    """667.86 s is `hard_stop − worst_case_ahead`, and the clause turns over between 667 and 669."""
    close_pod(run, seconds=dead_seconds, created=CREATE, pod_id="dead-1")
    assert run.main(["--pre-create-check"]) == (r1gate.GO if verdict == "GO" else r1gate.KILL)
    entry = json.loads(run.r1.RECORD.read_text("utf-8"))["gates"][-1]
    assert entry["verdict"] == verdict
    assert entry["billed_by_closed_pods_seconds"] == dead_seconds
    assert entry["projected_attempt_seconds"] == round(dead_seconds + SUMS["total_seconds"], 2)
    # the money fits at BOTH — the clause refuses on SECONDS, which is the shape that closed r1
    assert entry["fits_the_cap"] is True
    assert entry["fits_the_hard_stop"] is (verdict == "GO")


def test_a_SECOND_dead_pod_is_refused_on_the_COUNT_even_when_the_seconds_would_fit(run):
    close_pod(run, seconds=60.0, created=CREATE, pod_id="dead-1")
    close_pod(run, seconds=60.0, created=at(600).isoformat(timespec="seconds"), pod_id="dead-2")
    assert run.main(["--pre-create-check"]) == r1gate.KILL
    entry = json.loads(run.r1.RECORD.read_text("utf-8"))["gates"][-1]
    assert entry["fits_the_hard_stop"] is True
    assert entry["fits_the_cap"] is True
    assert entry["fits_the_re_creation_count"] is False


# --- rung 4, at the rates the contract names ----------------------------------------------------


def test_a_pod_at_6_0_seconds_per_call_runs_to_the_END(run, tmp_path):
    """Under the knife edge at either span: the projection is a GO from the first poll onward."""
    where = tmp_path / "run"
    assert opened(run) == r1gate.GO
    for n in (20, 200, 900):
        answered(where, PACK["legs"][0], n, seconds=6.0, elapsed0=CHARGED_PRE_GENERATION)
        elapsed = CHARGED_PRE_GENERATION + n * 6.0
        gateway = projected(run, where, elapsed)
        assert gateway["verdict"] == "GO", n
        assert gateway["projected_seconds"] <= HARD_STOP
    # and the whole run at 6.0 fits with room: pre-generation + 901 × 6.0 + overhead
    assert CHARGED_PRE_GENERATION + CALLS * 6.0 + OVERHEAD < HARD_STOP


def test_a_pod_at_8_seconds_per_call_dies_about_20_calls_in_with_the_re_creation_REACHABLE(
    run, tmp_path
):
    """The registration's own worked example, driven: «≈ 20 calls in, ≈ $0.10, still recoverable»."""
    where = tmp_path / "run"
    assert opened(run) == r1gate.GO
    answered(where, PACK["legs"][0], 20, seconds=8.0, elapsed0=MEASURED_PRE_GENERATION)
    elapsed = MEASURED_PRE_GENERATION + 20 * 8.0
    gateway = projected(run, where, elapsed)
    assert gateway["verdict"] == "KILL"
    assert gateway["projected_seconds"] > HARD_STOP
    assert gateway["over_the_hard_stop"] is True
    assert gateway["over_the_cap"] is False, "the seconds bind and the money does not"
    # and the pod that just died is cheap enough for the recovery clause to still be reachable —
    # AT THIS SPAN. The charged arm is driven in the test below and it answers the other way
    assert elapsed <= WIDEST_DEAD_POD
    assert elapsed / 3600 * 0.74 < 0.11
    # driven, not asserted: delete this pod at that elapsed and the clause still says GO
    assert (
        run.main(
            [
                "--close",
                "--deleted-at",
                at(elapsed).isoformat(timespec="seconds"),
                "--outcome",
                "rung 4 KILL on the rate",
            ],
            now=at(elapsed + 1),
        )
        == r1gate.GO
    )
    assert run.main(["--pre-create-check"]) == r1gate.GO
    entry = json.loads(run.r1.RECORD.read_text("utf-8"))["gates"][-1]
    assert entry["verdict"] == "GO" and entry["this_would_be_pod"] == 2


def test_a_pod_at_6_9_seconds_per_call_is_a_KILL_at_the_CHARGED_span_and_a_GO_at_the_MEASURED(
    run, tmp_path
):
    """The contract's D0′ line, driven — and it needs BOTH arms, which is the finding.

    6.9 s/call sits just above the knife edge computed at the CHARGED pre-generation (6.8812) and
    well below the one computed at the span r1's pod actually MEASURED (7.8219). So the verdict is
    not a property of the rate alone: the same 6.9 s/call pod is killed in one world and finishes in
    the other. And in the world where it IS killed, the pod has already billed past the widest dead
    pod the recovery clause allows, so «KILL with the re-creation still allowed» is not reachable at
    this rate — it needs ≥ 7.53 s/call at 20 answered rows
    ([[a_ceiling_derived_from_one_span_measured_over_another]]).
    """
    where = tmp_path / "run"
    assert opened(run) == r1gate.GO

    answered(where, PACK["legs"][0], 20, seconds=6.9, elapsed0=CHARGED_PRE_GENERATION)
    charged_elapsed = CHARGED_PRE_GENERATION + 20 * 6.9
    killed = projected(run, where, charged_elapsed)
    assert killed["verdict"] == "KILL"
    assert killed["over_the_hard_stop"] is True
    assert charged_elapsed > WIDEST_DEAD_POD, "and the re-creation is NOT reachable here"

    answered(where, PACK["legs"][0], 20, seconds=6.9, elapsed0=MEASURED_PRE_GENERATION)
    measured_elapsed = MEASURED_PRE_GENERATION + 20 * 6.9
    survives = projected(run, where, measured_elapsed)
    assert survives["verdict"] == "GO"
    assert survives["projected_seconds"] < HARD_STOP

    # the rate at which a 20-call death still leaves the clause reachable, derived not typed —
    # and the meter runs to `pod delete`, so the charged deletion tail comes off the allowance first
    tail = SUMS["recovery_arithmetic"]["deletion_tail"]["charged_seconds"]
    breakeven_ignoring_the_tail = (HARD_STOP - OVERHEAD - WIDEST_DEAD_POD) / (CALLS - 20)
    breakeven = (HARD_STOP - OVERHEAD - (WIDEST_DEAD_POD - tail)) / (CALLS - 20)
    assert round(breakeven_ignoring_the_tail, 4) == 7.528
    assert round(breakeven, 4) == 7.6171
    assert breakeven > breakeven_ignoring_the_tail > 6.9, "the contract's 6.9 is under both"


def test_the_watch_loop_kills_on_the_projection_from_INSIDE_its_own_loop(run, tmp_path):
    where = tmp_path / "run"
    assert opened(run) == r1gate.GO
    state = json.loads(run.r1.RECORD.read_text("utf-8"))
    where.mkdir(parents=True, exist_ok=True)
    (where / gate.r1.LAUNCH_STAMP).write_text(
        at(200.0).isoformat(timespec="seconds") + "\n", encoding="utf-8"
    )

    class Clock:
        def __init__(self):
            self.now = 0.0

        def __call__(self):
            return self.now

        def sleep(self, seconds):
            self.now += seconds

    clock = Clock()
    killed = []
    grown = {"n": 20}

    def pull():
        grown["n"] += 1
        answered(where, PACK["legs"][0], grown["n"], seconds=90.0, elapsed0=300.0)

    gateway = gate.r1.watch(
        RECORD,
        state,
        [PACK],
        where=where,
        log=tmp_path / "pod.log",
        pull=pull,
        kill=lambda: killed.append("deleted") or {"deleted": True},
        sleep=clock.sleep,
        now=at(600),
        clock_now=clock,
        poll_seconds=20.0,
    )
    assert gateway["verdict"] == "KILL"
    assert "rung 4" in gateway["cause"] or "rung 6" in gateway["cause"]
    assert killed == ["deleted"]
    assert sealed_is_untouched(run)


# --- rung 7 over the 901 -------------------------------------------------------------------------


def test_rung_7_is_GO_only_when_every_one_of_the_901_is_answered(run, tmp_path):
    where = tmp_path / "run"
    assert opened(run) == r1gate.GO
    state = json.loads(run.r1.RECORD.read_text("utf-8"))
    answered(where, PACK["legs"][0], CALLS - 1, seconds=6.0, elapsed0=300.0)
    short = gate.r1.completeness(RECORD, state, PACK, where, at(8000))
    assert short["verdict"] == "RED"
    assert short["answered"] == CALLS - 1
    assert short["unanswered"] == 1
    answered(where, PACK["legs"][0], CALLS, seconds=6.0, elapsed0=300.0)
    whole = gate.r1.completeness(RECORD, state, PACK, where, at(8000))
    assert whole["verdict"] == "GO"
    assert whole["answered"] == whole["owed"] == CALLS
    assert whole["sha_mismatches"] == 0
    assert whole["parse_refusals"] == 0


# --- the volume tail: counted, priced, never merged -----------------------------------------------


def _tail_file(tmp_path: Path, held: list[str], extra: list[str]) -> Path:
    path = tmp_path / "volume_tail.jsonl"
    path.write_text(
        "".join(
            json.dumps({"id": one, "reply": "{}"}, ensure_ascii=False) + "\n"
            for one in held + extra
        ),
        encoding="utf-8",
    )
    return path


def test_the_volume_tail_with_five_extra_rows_is_COUNTED_and_never_merged(tmp_path):
    held = [
        json.loads(line)["id"]
        for line in (REPO_ROOT / "results" / "pass1_window_v2.jsonl")
        .read_text("utf-8")
        .splitlines()
        if line.strip()
    ]
    extra = [one["id"] for one in PACK["legs"][0]["items"][:5]]
    path = _tail_file(tmp_path, held, extra)
    reading = tail.account(
        path, REPO_ROOT / "results" / "pass1_window_v2.jsonl", PACK, seconds_per_call=4.5
    )
    assert reading["rows_on_the_volume"] == 136
    assert reading["rows_the_mac_already_held"] == 131
    assert reading["rows_beyond_the_mac"] == 5
    assert reading["rows_beyond_the_mac_ids"] == sorted(extra)
    assert reading["bought_twice_seconds"] == 22.5
    assert reading["merged"] is False
    # and they are still owed: the pack asks every one of them, so they are bought again
    assert set(extra) <= {one["id"] for one in PACK["legs"][0]["items"]}


def test_a_volume_tail_row_that_belongs_to_NO_population_is_refused(tmp_path):
    path = _tail_file(tmp_path, [], ["@nobody:1#2"])
    with pytest.raises(SystemExit, match="belongs to no population"):
        tail.account(path, REPO_ROOT / "results" / "pass1_window_v2.jsonl", PACK)


def test_a_volume_tail_that_repeats_an_id_is_refused(tmp_path):
    one = PACK["legs"][0]["items"][0]["id"]
    path = _tail_file(tmp_path, [], [one, one])
    with pytest.raises(SystemExit, match="more than once"):
        tail.account(path, REPO_ROOT / "results" / "pass1_window_v2.jsonl", PACK)


def test_a_tail_that_holds_ONLY_what_the_mac_holds_costs_nothing(tmp_path):
    held = [
        json.loads(line)["id"]
        for line in (REPO_ROOT / "results" / "pass1_window_v2.jsonl")
        .read_text("utf-8")
        .splitlines()
        if line.strip()
    ]
    reading = tail.account(
        _tail_file(tmp_path, held, []),
        REPO_ROOT / "results" / "pass1_window_v2.jsonl",
        PACK,
        seconds_per_call=4.5,
    )
    assert reading["rows_beyond_the_mac"] == 0
    assert reading["bought_twice_seconds"] == 0.0


# --- the shipped transport, over the real pack ---------------------------------------------------


class FakeClient:
    def __init__(self):
        self.model = "the base model local_llm built"
        self.tasks = []

    def read(self, task, items):
        (item,) = items
        self.tasks.append(task)
        return [
            {
                "content": json.dumps(
                    {
                        "msg_id": int(item["msg_id"]),
                        "subject_type": "не_наш_рынок",
                        "subject_id": None,
                        "stance": None,
                    },
                    ensure_ascii=False,
                ),
                "finish_reason": "stop",
                "usage": {"prompt_tokens": 1400, "completion_tokens": 40},
            }
        ]


def test_the_shipped_runner_answers_the_r2_pack_unchanged(tmp_path):
    """The runner is r2's, unedited, and `--only v2` narrows a one-leg pack. No finding."""
    import pass1_fewshot_pod_runner as transport

    from market_pulse import prompts

    leg = PACK["legs"][0]
    cut = {**PACK, "legs": [{**leg, "items": leg["items"][:5]}]}
    path = tmp_path / "pack.json"
    path.write_text(json.dumps(cut, ensure_ascii=False), encoding="utf-8")
    client = FakeClient()
    assert (
        transport.main(
            [
                "--pack",
                str(path),
                "--outdir",
                str(tmp_path / "run"),
                "--repo",
                str(REPO_ROOT),
                "--only",
                "v2",
            ],
            loader=lambda p, r: client,
        )
        == 0
    )
    rows = [
        json.loads(line)
        for line in (tmp_path / "run" / leg["out"]).read_text("utf-8").splitlines()
        if line.strip()
    ]
    assert [row["id"] for row in rows] == [one["id"] for one in cut["legs"][0]["items"]]
    assert [row["rendering_sha256"] for row in rows] == [
        one["rendering_sha256"] for one in cut["legs"][0]["items"]
    ]
    assert client.tasks == [prompts.PASS1_TASK_V2] * 5
    assert all(row["balanced"] for row in rows)
    assert rows[0]["id"] != "", "and the file the leg NAMES is the one that was written"


def test_ALL_901_items_re_render_to_the_shas_r1s_pack_PINNED():
    """The property the whole subtraction rests on: the r2 pack did not re-render anything.

    The items were copied out of r1's pack, so their `rendering_sha256` is r1's — the same digest
    r1's pod verified on all 1 032 before its first call. This drives the SHIPPED render over every
    one of the 901 on this checkout and hashes it the way the pod does.
    """
    import hashlib

    import pass1_fewshot_pod_runner as transport

    from market_pulse import prompts

    leg = PACK["legs"][0]
    r1_pack = json.loads((REPO_ROOT / "results" / "pass1_window_pack.json").read_text("utf-8"))
    r1_by_id = {one["id"]: one for one in r1_pack["legs"][0]["items"]}
    with transport.as_fewshot():
        for item in leg["items"]:
            content = transport.render(prompts, item, leg["task"])
            got = hashlib.sha256(content.encode("utf-8")).hexdigest()
            assert got == item["rendering_sha256"], item["id"]
            assert got == r1_by_id[item["id"]]["rendering_sha256"], item["id"]


# --- the runbook against the gate's own code ------------------------------------------------------


def test_the_runbook_writes_the_stamp_under_the_name_the_WATCH_copies():
    """The one name the executor does not get to choose, and prose is where it drifts.

    `--watch`'s `pull()` copies `<remote-dir>/launched_at` — a literal in r1's gate — into
    `results/<LAUNCH_STAMP>`. If the launch command in the runbook wrote the LOCAL name onto the pod,
    the watch would copy a file that does not exist: rung 3 would have no anchor, `--boot` would be a
    KILL rather than a WAIT, and the create-anchored backstop would be the only bound left. This
    greps the runbook and asserts both names against the gate's own source
    ([[a_report_proves_it_does_not_instruct]]).
    """
    import inspect

    runbook = (REPO_ROOT / "scripts" / "runbook_pass1_window_r2.md").read_text("utf-8")
    source = inspect.getsource(r1gate.main)
    assert 'f"{args.remote_dir}/launched_at"' in source, "the gate's own literal moved"
    assert "--remote-dir" in inspect.getsource(r1gate.main)

    # what the pod is told to write, and what the watch will look for
    assert "> /workspace/run/launched_at;" in runbook
    assert "/workspace/run/pass1_window_r2_launched_at" not in runbook
    # and the scp back names the remote file and the LOCAL name of this attempt
    assert "root@<HOST>:/workspace/run/launched_at results/pass1_window_r2_launched_at" in runbook
    assert gate.r1.LAUNCH_STAMP == "pass1_window_r2_launched_at"
    # the out-file and the pod log are the leg's own name and the gate's own default
    assert "/workspace/run/pass1_window_r2_v2.jsonl" in runbook
    assert PACK["legs"][0]["out"] == "pass1_window_r2_v2.jsonl"
    assert "> /workspace/run/pod.log 2>&1" in runbook


def test_the_runbook_stages_the_r2_pack_and_runs_the_shipped_runner_with_only_v2():
    runbook = (REPO_ROOT / "scripts" / "runbook_pass1_window_r2.md").read_text("utf-8")
    assert "scripts/pass1_fewshot_pod_runner.py" in runbook
    assert "--pack /workspace/repo/results/pass1_window_r2_pack.json --only v2" in runbook
    assert "results/pass1_window_pack.json" not in runbook.split("## DO NOT")[0].replace(
        "results/pass1_window_r2_pack.json", ""
    )
    # every gate invocation in the runbook is the SIBLING's, never r1's
    assert "scripts/gate_pass1_window.py --" not in runbook
    assert runbook.count("scripts/gate_pass1_window_r2.py") >= 8
    # and the guard is the fresh step at this contract's cap
    assert "--step pass1-window-r2 --step-cap 2.00" in runbook
    assert "--step pass1-window --step-cap 1.50" not in runbook


def test_the_runbook_copies_the_volume_BEFORE_it_clears_the_run_directory():
    """The one ordering that cannot be got wrong: `rm -rf /workspace/run` deletes the evidence."""
    runbook = (REPO_ROOT / "scripts" / "runbook_pass1_window_r2.md").read_text("utf-8")
    scp_at = runbook.index("root@<HOST>:/workspace/run/pass1_window_v2.jsonl")
    clear_at = runbook.index("rm -rf /workspace/run && mkdir -p /workspace/run")
    assert scp_at < clear_at, "the volume tail is copied before the directory is cleared"
    assert "Do not run this until step 3a's scp and sha have both passed." in runbook
    assert "scripts/volume_tail_pass1_window.py" in runbook


def test_the_SAME_8_seconds_per_call_kill_is_UNRECOVERABLE_at_the_charged_pre_generation():
    """The five-lens review's finding, driven: the worked example reverses on the span.

    The recovery clause is checked on BILLED seconds and the meter runs to `pod delete`, so what
    decides it is the create-elapsed at the kill plus the charged deletion tail against the widest
    dead pod. At the pre-generation r1's pod MEASURED that is inside; at the one the budget CHARGES
    it is already outside before the first call lands, so no rate KILL is recoverable in that world
    at any rate and any call count ([[a_ceiling_derived_from_one_span_measured_over_another]]).
    """
    recovery = SUMS["recovery_arithmetic"]
    tail = recovery["deletion_tail"]["charged_seconds"]
    boundary = recovery["which_KILLS_stay_recoverable"]["the_number_that_decides_it"]
    assert boundary == round(WIDEST_DEAD_POD - tail, 2) == 589.36

    measured = MEASURED_PRE_GENERATION + 20 * 8.0
    charged = CHARGED_PRE_GENERATION + 20 * 8.0
    assert measured + tail <= WIDEST_DEAD_POD, "recoverable in the world r1 measured"
    assert charged + tail > WIDEST_DEAD_POD, "and NOT in the world the budget charges"
    # the charged pre-generation is past the boundary before a single call lands
    assert CHARGED_PRE_GENERATION > boundary
    # rung 2 is always inside it; rung 3's create-anchored backstop never is
    assert recovery["one_dead_pod_at_rung_2_with_the_measured_tail_seconds"] <= WIDEST_DEAD_POD
    assert CHARGED_PRE_GENERATION + tail > WIDEST_DEAD_POD
    # and the record says all of it, in the block the runbook points at
    block = recovery["which_KILLS_stay_recoverable"]
    assert "ALWAYS inside" in block["rung_2"]
    assert "never is" in block["rung_3"] or "well outside" in block["rung_3"]
    assert "NO rung-4 kill is recoverable" in block["rung_4"]
    gate = SUMS["cumulative"]["projection_gate"]
    assert "what_an_early_rate_KILL_costs_AT_BOTH_SPANS" in gate
    assert "FALSE at the" in gate["what_an_early_rate_KILL_costs_AT_BOTH_SPANS"]
    # the runbook carries both rows of the same table
    runbook = (REPO_ROOT / "scripts" / "runbook_pass1_window_r2.md").read_text("utf-8")
    assert "AT BOTH SPANS, because the answer reverses" in runbook
    assert "589.36" in runbook
    assert "**no — STOP**" in runbook


def test_every_threshold_the_gate_PARSES_OUT_OF_PROSE_is_pinned_to_its_constant():
    """r1's rungs read their deadlines with `first_number(rule)` — the first digit-run of a sentence.

    So the live deadline of rung 2, rung 3 and rung 5 is a property of PROSE. Four words in front of
    a rule and the idle deadline becomes 5 s: a healthy pod dies on the first poll that shows no new
    row, which is what one failed scp looks like, and the ONE allowed re-creation is burnt. Nothing
    in the suite pinned the parse for this record until this test
    ([[preregistration_is_a_file_not_a_constant]] read the other way: the file IS the constant, so
    the parse of it has to be checked).
    """
    assert r1gate.first_number(r1gate.rung(RECORD, 2)["rule"]) == 500.0
    assert r1gate.first_number(r1gate.rung(RECORD, 3)["rule"]) == 450.0
    assert r1gate.first_number(r1gate.rung(RECORD, 5)["rule"]) == 600.0
    assert float(r1gate.rung(RECORD, 3)["backstop_seconds"]) == 1100.0
    assert r1gate.first_number(r1gate.rung(RECORD, 6)["rule"]) == HARD_STOP
    # rung 4's own interval, the same way
    assert r1gate.first_number(r1gate.rung(RECORD, 4)["rule"]) == 20.0


def test_rung_5_FIRES_at_the_deadline_this_record_carries(run, tmp_path):
    """The negative control the other watch test cannot give: an out-file that stops growing.

    The existing loop test grows the file on every poll, so `last_event` refreshes and rung 5 can
    never fire at ANY deadline. This one lets it go idle and asserts the KILL lands at the deadline
    the RECORD carries — so a prose edit that moved it would change this test's answer.
    """
    where = tmp_path / "run"
    assert opened(run) == r1gate.GO
    state = json.loads(run.r1.RECORD.read_text("utf-8"))
    where.mkdir(parents=True, exist_ok=True)
    (where / gate.r1.LAUNCH_STAMP).write_text(
        at(200.0).isoformat(timespec="seconds") + "\n", encoding="utf-8"
    )
    answered(where, PACK["legs"][0], 3, seconds=6.0, elapsed0=300.0)

    class Clock:
        def __init__(self):
            self.now = 0.0

        def __call__(self):
            return self.now

        def sleep(self, seconds):
            self.now += seconds

    clock = Clock()
    killed = []
    gateway = gate.r1.watch(
        RECORD,
        state,
        [PACK],
        where=where,
        log=tmp_path / "pod.log",
        pull=lambda: None,  # nothing new ever lands
        kill=lambda: killed.append("deleted") or {"deleted": True},
        sleep=clock.sleep,
        now=at(900),
        clock_now=clock,
        poll_seconds=60.0,
    )
    assert gateway["verdict"] == "KILL"
    assert "rung 5" in gateway["cause"]
    idle_deadline = r1gate.first_number(r1gate.rung(RECORD, 5)["rule"])
    assert gateway["idle_seconds"] >= idle_deadline == 600.0
    assert gateway["idle_seconds"] < idle_deadline + 60.0, (
        "it fires at the deadline, not long after"
    )
    assert killed == ["deleted"]
    assert sealed_is_untouched(run)
