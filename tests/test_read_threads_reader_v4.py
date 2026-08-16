"""reader-v4's transport — the pack, the two clocks, the kill rule and the ingest, driven.

Nothing here touches RunPod and nothing here loads a model: the pod runner takes its loader as a
parameter and every test hands it a fake, so the checks that refuse BEFORE the expensive rung are
exercised with a control that proves the loader was never reached. The money arithmetic is
hand-computed at the registered price, on both sides of every threshold — a gate tested only where
it passes is a gate nobody has seen fire.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import read_threads_reader_v4 as driver  # noqa: E402
import reader_v4_pod_runner as pod  # noqa: E402

RECORD = json.loads(
    (REPO_ROOT / "results" / "prereg_reader_probe_v4.json").read_text(encoding="utf-8")
)
RATE = 0.74 / 3600.0
USABLE = 1642.703
CREATED = "2026-08-16T18:00:00+00:00"


# --- the pack -------------------------------------------------------------------------------


def test_the_pack_is_the_registered_population_and_every_request_matches_its_sha():
    pack = driver.build_pack(RECORD)
    assert len(pack["items"]) == RECORD["population"]["threads"] == 23
    assert sum(one["payable_comments"] for one in pack["items"]) == 134
    pinned = {
        one["thread"]: one["rendering_sha256"]
        for one in RECORD["population"]["enumeration"]["threads"]
    }
    assert {one["thread"]: one["rendering_sha256"] for one in pack["items"]} == pinned
    assert pack["task"] == RECORD["instruments"]["task"]
    assert pack["serving"] == RECORD["instruments"]["serving"]
    # the item is the shape ReaderClient.render reads, so the object the sha was checked on is the
    # object the model is shown
    assert set(pack["items"][0]) >= {"channel", "post_id", "post", "comments"}


def test_a_thread_whose_text_moved_is_refused_before_anything_is_created(monkeypatch):
    """The check that costs $0 today and a pod's boot tomorrow. Driven by moving the renderer, not
    by editing a frozen record."""
    original = driver.writer.rendering_sha256
    calls = {"n": 0}

    def moved(thread, task):
        calls["n"] += 1
        return "0" * 64 if calls["n"] == 3 else original(thread, task)

    monkeypatch.setattr(driver.probe_b.writer, "rendering_sha256", moved)
    monkeypatch.setattr(driver.writer, "rendering_sha256", moved)
    with pytest.raises(SystemExit) as err:
        driver.build_pack(RECORD)
    assert "moved" in str(err.value) or "renders to" in str(err.value)


# --- the two clocks -------------------------------------------------------------------------


def test_the_cap_in_seconds_is_recomputed_from_the_price_actually_charged():
    """The registration prices the 4090 at $0.74/h; a create response with another figure re-prices
    everything. Both directions, because a cheaper card must WIDEN the run and not narrow it."""
    assert driver.usable_seconds(RECORD, RATE) == pytest.approx(USABLE, abs=0.001)
    cheaper = driver.usable_seconds(RECORD, 0.49 / 3600)
    dearer = driver.usable_seconds(RECORD, 1.39 / 3600)
    assert cheaper > USABLE > dearer
    assert cheaper == pytest.approx(0.35 * 3600 / 0.49 - 60, abs=0.001)


def test_before_the_generation_starts_only_affordability_is_on_the_axis():
    gate = driver.deadlines(RECORD, RATE, elapsed=120.0, generation_at=None)
    assert gate["contract_ceiling_as_create_elapsed"] is None
    assert gate["affordability_deadline_as_create_elapsed"] == pytest.approx(
        round(USABLE - 727.664, 1)
    )
    assert gate["first_reply_must_land_by_create_elapsed"] == 915.0
    assert gate["verdict"] == "WAIT"
    assert "has not started" in gate["which_binds"]


def test_the_twelve_minutes_binds_inside_the_pre_generation_budget_and_stops_binding_outside_it():
    """195.039 s is the registered budget: launch the runner inside it and the contract's ceiling is
    the tighter deadline; launch it later and affordability takes over. Both sides, one number."""
    budget = RECORD["money"]["arithmetic"]["pre_generation_budget_seconds"]
    assert budget == 195.039
    inside = driver.deadlines(RECORD, RATE, elapsed=200.0, generation_at=budget - 1)
    assert inside["which_binds"] == "the contract's twelve minutes"
    assert inside["first_reply_must_land_by_create_elapsed"] == round(budget - 1 + 720.0, 1)
    outside = driver.deadlines(RECORD, RATE, elapsed=300.0, generation_at=budget + 1)
    assert outside["which_binds"].startswith("affordability")
    assert outside["first_reply_must_land_by_create_elapsed"] == 915.0


def test_the_kill_rule_fires_on_one_side_of_the_deadline_and_not_on_the_other():
    """The negative control is the point: a rule that only ever says KILL is not a rule."""
    gen = 100.0
    deadline = gen + 720.0
    assert driver.deadlines(RECORD, RATE, deadline - 1, gen)["verdict"] == "WAIT"
    assert driver.deadlines(RECORD, RATE, deadline + 1, gen)["verdict"] == "KILL"
    # and it is the same at the affordability edge, with the generation started far too late
    late = driver.deadlines(RECORD, RATE, 916.0, 800.0)
    assert late["which_binds"].startswith("affordability") and late["verdict"] == "KILL"


# --- the full-pass gate ---------------------------------------------------------------------


PACK_ITEMS = RECORD["population"]["enumeration"]["threads"]


def rows(n: int, seconds: float) -> list[dict]:
    """n replies, drawn from the registered enumeration IN ORDER.

    Real thread names and therefore real payable counts: the gate's second leg divides by them, and
    a fixture with invented names would exercise only the leg that does not need them.
    """
    return [{"thread": one["thread"], "seconds": seconds} for one in PACK_ITEMS[:n]]


def test_the_full_pass_gate_is_hand_computable_and_solved_for_seconds():
    """One reply at 30 s, 500 s elapsed: 500 + 22×30 = 1160 ≤ 1642.7, so GO, and the threshold is
    (1642.7 − 500) ÷ 22 = 51.94 s a thread."""
    gate = driver.projection(RECORD, RATE, rows(1, 30.0), elapsed=500.0, of=23)
    assert gate["threads_unread"] == 22
    assert gate["measured_seconds_per_thread"] == 30.0
    # both legs are computed and the pessimistic one binds: 22 unread threads over 1 read beats
    # 127 unread payable comments over the 7 that thread carried
    assert gate["payable_comments_read"] == 7 and gate["payable_comments_unread"] == 127
    assert gate["projections"]["by_thread"]["factor"] == 22.0
    assert gate["projections"]["by_payable_comment"]["factor"] == pytest.approx(127 / 7, abs=0.001)
    assert gate["projections"]["binding"]["which"] == "by_thread"
    assert gate["projected_total_seconds"] == pytest.approx(1160.0, abs=0.05)
    assert gate["seconds_per_thread_that_still_fits"] == pytest.approx(
        (USABLE - 500.0) / 22, abs=0.001
    )
    assert gate["verdict"] == "GO"
    assert gate["slowdown_vs_probe_b"] == pytest.approx(30.0 / 31.6376, abs=0.001)


def test_the_full_pass_gate_stops_on_the_other_side_of_the_same_threshold():
    threshold = (USABLE - 500.0) / 22
    assert driver.projection(RECORD, RATE, rows(1, threshold - 0.01), 500.0, 23)["verdict"] == "GO"
    assert (
        driver.projection(RECORD, RATE, rows(1, threshold + 0.01), 500.0, 23)["verdict"] == "STOP"
    )
    # and the dollars are why the verdict may not be re-derived from them: at the STOP side the
    # projected total is $0.3377 — UNDER the $0.35 cap, because the delete margin is held back —
    # so a reader adding the published figures up would get a GO out of a STOP
    go = driver.projection(RECORD, RATE, rows(1, threshold - 0.01), 500.0, 23)["usd"]
    stop = driver.projection(RECORD, RATE, rows(1, threshold + 0.01), 500.0, 23)["usd"]
    assert stop["projected_total_usd"] < stop["cap_usd_all_in"] == 0.35
    assert abs(stop["projected_total_usd"] - go["projected_total_usd"]) <= 0.0001
    assert stop["delete_margin_usd"] == round(60 * RATE, 4)


def test_the_gate_re_projects_from_every_thread_read_so_far():
    """Three replies at 40 s with 700 s gone: 700 + 20×40 = 1500 ≤ 1642.7 and it still fits."""
    gate = driver.projection(RECORD, RATE, rows(3, 40.0), elapsed=700.0, of=23)
    assert gate["threads_read"] == 3 and gate["threads_unread"] == 20
    assert gate["payable_comments_read"] == 21 and gate["payable_comments_unread"] == 113
    assert gate["projections"]["binding"]["factor"] == pytest.approx(20 / 3, abs=0.001)
    assert gate["projected_total_seconds"] == pytest.approx(1500.0, abs=0.05)
    assert gate["verdict"] == "GO"


# --- the pod runner -------------------------------------------------------------------------


class FakeClient:
    def __init__(self, replies):
        self.replies, self.seen = replies, []

    def read(self, task, items):
        self.seen.append((task, items[0]["channel"], items[0]["post_id"]))
        content = self.replies[len(self.seen) - 1]
        return [
            {
                "content": content,
                "finish_reason": "stop",
                "usage": {"prompt_tokens": 10, "completion_tokens": len(content)},
            }
        ]


def a_pack(tmp_path, items=2):
    pack = driver.build_pack(RECORD)
    pack["items"] = pack["items"][:items]
    return pack


def test_the_runner_answers_every_item_and_flushes_one_line_as_each_lands(tmp_path):
    pack = a_pack(tmp_path)
    out = tmp_path / "pod.jsonl"
    seen = {}

    def loader(pack_, repo):
        seen["client"] = FakeClient(['{"thread":"x"}', "not json at all"])
        return seen["client"]

    assert pod.run(pack, out, REPO_ROOT, loader=loader) == 0
    lines = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines() if line]
    assert len(lines) == len(pack["items"]) == 2
    assert [one["thread"] for one in lines] == [one["thread"] for one in pack["items"]]
    assert [one["rendering_sha256"] for one in lines] == [
        one["rendering_sha256"] for one in pack["items"]
    ]
    assert lines[1]["reply"] == "not json at all"  # the pod does not parse, and must not
    assert all(one["boot_seconds"] >= 0 and one["seconds"] >= 0 for one in lines)
    assert seen["client"].seen[0][0] == pack["task"]


def test_the_runner_refuses_a_moved_prompt_sha_BEFORE_the_model_is_loaded(tmp_path):
    """The control is `loaded`: a refusal that happened after the load would have cost the boot."""
    pack = a_pack(tmp_path)
    pack["instruments"]["prompt_sha256"]["reader_thread_gm4_v3"] = "0" * 64
    loaded = []
    with pytest.raises(SystemExit) as err:
        pod.run(pack, tmp_path / "pod.jsonl", REPO_ROOT, loader=lambda p, r: loaded.append(1))
    assert "not the registered instrument" in str(err.value)
    assert loaded == []
    assert not (tmp_path / "pod.jsonl").exists()


def test_the_runner_refuses_a_moved_request_sha_BEFORE_the_model_is_loaded(tmp_path):
    pack = a_pack(tmp_path)
    pack["items"][1]["rendering_sha256"] = "0" * 64
    loaded = []
    with pytest.raises(SystemExit) as err:
        pod.run(pack, tmp_path / "pod.jsonl", REPO_ROOT, loader=lambda p, r: loaded.append(1))
    assert "the registration pinned" in str(err.value)
    assert loaded == []


def test_the_runner_loads_when_nothing_moved_which_is_what_makes_the_two_refusals_mean_something(
    tmp_path,
):
    """The premise the two negative controls rest on: this pack, unmodified, reaches the loader."""
    loaded = []
    pod.run(
        a_pack(tmp_path, items=1),
        tmp_path / "pod.jsonl",
        REPO_ROOT,
        loader=lambda p, r: loaded.append(FakeClient(["{}"])) or loaded[0],
    )
    assert len(loaded) == 1


# --- the ingest -----------------------------------------------------------------------------


def test_the_ingest_parses_here_and_carries_the_request_beside_its_sha(tmp_path):
    pack = a_pack(tmp_path)
    good = json.dumps(
        {
            "thread": {
                "channel": pack["items"][0]["channel"],
                "post_id": pack["items"][0]["post_id"],
            },
            "post_summary": "s",
            "discussion_summary": "d",
            "entities": [],
            "signals": [],
            "per_comment": [],
            "noise": [],
        },
        ensure_ascii=False,
    )
    raw = [
        {
            "thread": pack["items"][0]["thread"],
            "rendering_sha256": pack["items"][0]["rendering_sha256"],
            "reply": good,
            "finish_reason": "stop",
            "usage": {"prompt_tokens": 1, "completion_tokens": 2},
            "seconds": 12.5,
        },
        {
            "thread": pack["items"][1]["thread"],
            "rendering_sha256": pack["items"][1]["rendering_sha256"],
            "reply": "no braces here",
            "finish_reason": "stop",
            "usage": {},
            "seconds": 3.0,
        },
    ]
    rows_out = driver.ingest(RECORD, raw, pack)
    assert rows_out[0]["parsed"] is not None and rows_out[0]["parse_error"] is None
    assert rows_out[0]["repairs"] == []
    assert rows_out[1]["parsed"] is None and rows_out[1]["parse_error"]
    for row, item in zip(rows_out, pack["items"]):
        assert row["rendering_sha256"] == item["rendering_sha256"]
        # the request travels beside its sha, and the sha is OF the request — the row is readable
        # on its own, which is the whole point of persisting the text as well as the digest
        assert pod.sha256_of_text(row["request"]) == row["rendering_sha256"]
        assert row["payable_comments"] == item["payable_comments"]
        assert row["seconds"]["worker"] > 0


def test_the_ingest_refuses_a_reply_whose_request_is_not_the_one_that_was_packed(tmp_path):
    pack = a_pack(tmp_path)
    raw = [
        {
            "thread": pack["items"][0]["thread"],
            "rendering_sha256": "0" * 64,
            "reply": "{}",
            "seconds": 1.0,
        }
    ]
    with pytest.raises(SystemExit) as err:
        driver.ingest(RECORD, raw, pack)
    assert "the pack pinned" in str(err.value)


# --- the CLI, end to end on tmp paths -------------------------------------------------------


def redirect(monkeypatch, tmp_path):
    """Every file the driver writes, moved into tmp_path — the write path is exercised, not mocked.

    A run record that only ever existed as a return value is a run record nobody has seen written
    ([[exercise_the_write_path_not_just_the_compute]]).
    """
    for name in ("LEDGER", "RECORD", "EVIDENCE", "PACK", "RAW"):
        monkeypatch.setattr(driver, name, tmp_path / getattr(driver, name).name)
    return tmp_path


def test_the_cli_refuses_to_open_a_pod_against_a_counter_that_does_not_exist(monkeypatch, tmp_path):
    """The anchor is written by the guard BEFORE anything billable; without it there is nothing
    measuring the pod. The negative control for the test below."""
    redirect(monkeypatch, tmp_path)
    with pytest.raises(SystemExit) as err:
        driver.main(
            [
                "--open",
                "--pod-id",
                "p1",
                "--created-at",
                CREATED,
                "--usd-per-hour",
                "0.74",
                "--card",
                "NVIDIA GeForce RTX 4090",
            ]
        )
    assert "does not exist" in str(err.value)
    assert not driver.RECORD.exists()


def test_the_cli_walks_open_then_boot_then_the_gate_then_the_evidence(monkeypatch, tmp_path):
    redirect(monkeypatch, tmp_path)
    driver.LEDGER.write_text('{"gpu_sessions": []}\n', encoding="utf-8")
    pack = driver.build_pack(RECORD)
    driver.PACK.write_text(json.dumps(pack, ensure_ascii=False), encoding="utf-8")

    from datetime import timedelta

    zero = driver.stamp(CREATED)
    assert (
        driver.main(
            [
                "--open",
                "--pod-id",
                "p1",
                "--created-at",
                CREATED,
                "--usd-per-hour",
                "0.74",
                "--card",
                "NVIDIA GeForce RTX 4090",
            ],
            now=zero + timedelta(seconds=5),
        )
        == 0
    )
    state = json.loads(driver.RECORD.read_text(encoding="utf-8"))
    assert state["pod"]["priced_as_registered"] is True
    assert state["deadlines_at_open"]["verdict"] == "WAIT"

    # the generation starts at +150 s and no reply has landed at +400 s: inside the twelve minutes
    launched = (zero + timedelta(seconds=150)).isoformat()
    assert (
        driver.main(
            ["--gate", "--generation-started-at", launched], now=zero + timedelta(seconds=400)
        )
        == 3
    )
    assert json.loads(driver.RECORD.read_text(encoding="utf-8"))["boot_kill"]["verdict"] == "WAIT"
    # ...and at +900 s it has not: past 150 + 720, so KILL
    assert driver.main(["--gate"], now=zero + timedelta(seconds=900)) == 2
    assert json.loads(driver.RECORD.read_text(encoding="utf-8"))["boot_kill"]["verdict"] == "KILL"

    # the first reply lands; the full-pass gate takes over from the boot rule
    good = json.dumps(
        {
            "thread": {
                "channel": pack["items"][0]["channel"],
                "post_id": pack["items"][0]["post_id"],
            },
            "post_summary": "s",
            "discussion_summary": "d",
            "entities": [],
            "signals": [],
            "per_comment": [],
            "noise": [],
        },
        ensure_ascii=False,
    )
    driver.RAW.write_text(
        json.dumps(
            {
                "thread": pack["items"][0]["thread"],
                "rendering_sha256": pack["items"][0]["rendering_sha256"],
                "reply": good,
                "finish_reason": "stop",
                "usage": {"prompt_tokens": 1, "completion_tokens": 2},
                "seconds": 30.0,
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    assert driver.main(["--gate"], now=zero + timedelta(seconds=500)) == 0
    gate = json.loads(driver.RECORD.read_text(encoding="utf-8"))["go_no_go"]
    assert gate["verdict"] == "GO" and gate["threads_unread"] == 22

    assert driver.main(["--ingest"]) == 0
    lines = [
        json.loads(line)
        for line in driver.EVIDENCE.read_text(encoding="utf-8").splitlines()
        if line
    ]
    assert len(lines) == 1 and lines[0]["parsed"] is not None
    assert lines[0]["thread"] == pack["items"][0]["thread"]
