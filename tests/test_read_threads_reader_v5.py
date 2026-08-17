"""reader-v5's transport — the two-leg pack, the appended gates, the merge-on-ingest, and the score.

Everything here runs at $0 and nothing loads a model: the pod runner takes its loader as a parameter
and every test hands it a fake, so the checks that refuse BEFORE the expensive rung are exercised
with a control that proves the loader was never reached. The gate arithmetic is hand-computed at the
registration's own worked-example price, on both sides of the threshold.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import read_threads_reader_v5 as driver  # noqa: E402
import reader_v5_pod_runner as pod  # noqa: E402
import score_reader_v5 as scoring  # noqa: E402

from market_pulse import prompts  # noqa: E402

from test_reader_v3_verdict import GOLD, perfect  # noqa: E402

RECORD = json.loads(
    (REPO_ROOT / "results" / "prereg_reader_probe_v5.json").read_text(encoding="utf-8")
)
RATE = 0.74 / 3600.0
USABLE = RECORD["money"]["arithmetic"]["usable_seconds"]
CREATED = "2026-08-17T18:00:00+00:00"


@pytest.fixture(scope="module")
def pack() -> dict:
    return driver.build_pack(RECORD)


# --- the pack ------------------------------------------------------------------------------------


def test_the_pack_is_both_legs_and_every_request_matches_its_sha(pack):
    assert len(pack["items"]) == 23 + 3 == 26
    legs = {leg: [one for one in pack["items"] if one["leg"] == leg] for leg in ("A", "B")}
    assert len(legs["A"]) == 23 and len(legs["B"]) == 3
    assert sum(one["payable_comments"] for one in legs["A"]) == 134
    assert sum(one["payable_comments"] for one in legs["B"]) == 43

    pinned = {
        one["thread"]: one["rendering_sha256"]
        for one in RECORD["population"]["leg_a"]["enumeration"]["threads"]
    } | {one["id"]: one["rendering_sha256"] for one in RECORD["population"]["leg_b"]["items"]}
    assert {one["id"]: one["rendering_sha256"] for one in pack["items"]} == pinned
    assert pack["task"] == RECORD["instruments"]["task"] == prompts.READER_TASK_V5
    # the ceiling travels WITH the pack, or the runner takes local_llm's 2000 in silence
    assert pack["serving"]["output_tokens"] == 4000


def test_leg_b_items_carry_their_part_and_leg_a_items_do_not(pack):
    for one in pack["items"]:
        assert (one["part"] is not None) is (one["leg"] == "B"), one["id"]
    parts = [one["part"] for one in pack["items"] if one["leg"] == "B"]
    assert parts == [[1, 3], [2, 3], [3, 3]]


def test_a_request_whose_text_moved_is_refused_before_anything_is_created(monkeypatch):
    """The check that costs $0 today and a pod's boot tomorrow. Driven by moving the renderer."""
    original = prompts.reader_messages_gm4
    calls = {"n": 0}

    def moved(*args, **kwargs):
        calls["n"] += 1
        out = original(*args, **kwargs)
        if calls["n"] == 3:
            out[0]["content"] += " (edited in the store)"
        return out

    monkeypatch.setattr(driver.prompts, "reader_messages_gm4", moved)
    with pytest.raises(SystemExit, match="the request moved since the registration"):
        driver.build_pack(RECORD)


def test_the_pack_copies_the_registrations_dicts_instead_of_aliasing_them(pack):
    """A pack that shares the record's objects can be edited into agreeing with it, and the pod's
    whole handshake is that the two can differ."""
    pack["instruments"]["prompt_sha256"]["reader_thread_gm4"] = "poisoned"
    assert RECORD["instruments"]["prompt_sha256"]["reader_thread_gm4"] != "poisoned"
    pack["instruments"]["prompt_sha256"]["reader_thread_gm4"] = RECORD["instruments"][
        "prompt_sha256"
    ]["reader_thread_gm4"]


# --- the on-pod runner ---------------------------------------------------------------------------


class FakeClient:
    def __init__(self, replies):
        self.replies, self.seen = replies, []

    def read(self, task, items):
        self.seen.append((task, items[0]["id"]))
        content = self.replies[(len(self.seen) - 1) % len(self.replies)]
        return [
            {
                "content": content,
                "finish_reason": "stop",
                "usage": {"prompt_tokens": 10, "completion_tokens": len(content)},
            }
        ]


def a_pack(pack, items=2):
    """The registered pack, cut short and re-pinned to THIS checkout's parser.

    The parser sha the registration carries IS this checkout's today, so the swap is a no-op — but
    it is written down, because the day `prompts.py` moves again a positive control built on the
    frozen sha would refuse for a reason that has nothing to do with what the test is about
    ([[the_control_whose_premise_stopped_being_true]]).
    """
    live = json.loads(json.dumps(pack))
    live["items"] = live["items"][:items]
    live["instruments"]["parser"]["sha256"] = pod.sha256_of_text(
        (REPO_ROOT / "src" / "market_pulse" / "prompts.py").read_text(encoding="utf-8")
    )
    return live


VERDICT = json.dumps(
    {
        "thread": {"channel": "@c", "post_id": 1},
        "post_summary": "п",
        "discussion_summary": "д",
        "entities": [],
        "signals": [],
        "per_comment": [],
        "noise": [],
    },
    ensure_ascii=False,
)


def test_the_runner_answers_every_unit_and_persists_the_BALANCED_PREFIX(tmp_path, pack):
    """The stop, on disk: what is written is the reply up to the closing brace and `cut_chars` says
    how much came after it."""
    live = a_pack(pack)
    out = tmp_path / "pod.jsonl"
    trailing = VERDICT + '{"entities": ["a second object nobody asked for"]}'
    assert pod.run(live, out, REPO_ROOT, loader=lambda p, r: FakeClient([trailing])) == 0
    lines = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines() if line]
    assert len(lines) == len(live["items"]) == 2
    for row in lines:
        assert row["reply"] == VERDICT
        assert row["balanced"] is True
        assert row["cut_chars"] == len(trailing) - len(VERDICT) > 0
        assert row["emitted_chars"] == len(trailing)
        # and the persisted prefix parses, where the whole emitted text would have refused
        assert prompts.parse_reply(live["task"], row["reply"])["thread"]["post_id"] == 1
    with pytest.raises(prompts.ParseError):
        prompts.parse_reply(live["task"], trailing)


def test_a_reply_that_never_balances_is_persisted_WHOLE_and_flagged(tmp_path, pack):
    live = a_pack(pack, items=1)
    out = tmp_path / "pod.jsonl"
    assert pod.run(live, out, REPO_ROOT, loader=lambda p, r: FakeClient(['{"a": 1'])) == 0
    row = json.loads(out.read_text(encoding="utf-8").splitlines()[0])
    assert row["reply"] == '{"a": 1' and row["balanced"] is False and row["cut_chars"] == 0


def test_the_runner_refuses_a_moved_request_sha_BEFORE_the_model_is_loaded(tmp_path, pack):
    live = a_pack(pack)
    live["items"][1]["rendering_sha256"] = "0" * 64
    loaded = []
    with pytest.raises(SystemExit, match="The request moved"):
        pod.run(live, tmp_path / "pod.jsonl", REPO_ROOT, loader=lambda p, r: loaded.append(1))
    assert loaded == [] and not (tmp_path / "pod.jsonl").exists()


def test_the_runner_refuses_a_moved_prompt_sha_BEFORE_the_model_is_loaded(tmp_path, pack):
    live = a_pack(pack)
    live["instruments"]["prompt_sha256"][prompts.READER_TASK_V5] = "0" * 64
    loaded = []
    with pytest.raises(SystemExit, match="not the registered instrument"):
        pod.run(live, tmp_path / "pod.jsonl", REPO_ROOT, loader=lambda p, r: loaded.append(1))
    assert loaded == []


def test_the_runner_loads_when_nothing_moved_which_is_what_makes_the_refusals_mean_something(
    tmp_path, pack
):
    loaded = []
    pod.run(
        a_pack(pack, items=1),
        tmp_path / "pod.jsonl",
        REPO_ROOT,
        loader=lambda p, r: loaded.append(FakeClient([VERDICT])) or loaded[0],
    )
    assert len(loaded) == 1


def test_a_replacement_pod_answers_ONLY_the_units_with_no_persisted_reply(tmp_path, pack):
    """The run contract's recovery clause, driven. One attempt means one answer per unit, so a
    second `run()` over a half-written out-file must ask for the remainder and nothing else."""
    out = tmp_path / "pod.jsonl"
    first = FakeClient([VERDICT])
    assert pod.run(a_pack(pack, items=1), out, REPO_ROOT, loader=lambda p, r: first) == 0
    assert [one[1] for one in first.seen] == [pack["items"][0]["id"]]

    second = FakeClient([VERDICT])
    assert pod.run(a_pack(pack, items=3), out, REPO_ROOT, loader=lambda p, r: second) == 0
    # the unit answered by the dead pod was never re-asked, and the other two were
    assert [one[1] for one in second.seen] == [one["id"] for one in pack["items"][1:3]]
    rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines() if line]
    assert [row["id"] for row in rows] == [one["id"] for one in pack["items"][:3]]
    # `index` stays the position in the PACK, not the position in the resumed loop
    assert [row["index"] for row in rows] == [0, 1, 2]


def test_a_complete_out_file_does_not_pay_for_a_boot(tmp_path, pack):
    """The other end of the same clause: nothing to answer means nothing to load, and 59 GB of
    weights is the most expensive thing this run can do for no rows."""
    out = tmp_path / "pod.jsonl"
    live = a_pack(pack, items=2)
    assert pod.run(live, out, REPO_ROOT, loader=lambda p, r: FakeClient([VERDICT])) == 0
    loaded = []
    assert pod.run(live, out, REPO_ROOT, loader=lambda p, r: loaded.append(1)) == 0
    assert loaded == []
    assert len(out.read_text(encoding="utf-8").splitlines()) == 2


def test_an_out_file_from_another_run_is_REFUSED_and_never_appended_to(tmp_path, pack):
    """`--out` is append-only, and a stale file is the one way that design can hurt: a foreign row
    would be counted by the Mac's projection and loosen the cap gate on a live pod."""
    out = tmp_path / "pod.jsonl"
    out.write_text(json.dumps({"id": "@somebody_else:1", "reply": "{}"}) + "\n", encoding="utf-8")
    loaded = []
    with pytest.raises(SystemExit, match="another run's file"):
        pod.run(a_pack(pack), out, REPO_ROOT, loader=lambda p, r: loaded.append(1))
    assert loaded == []
    assert len(out.read_text(encoding="utf-8").splitlines()) == 1


def test_a_chunked_item_renders_its_header_on_the_pod_too(pack):
    """The pod renders the request ITSELF, so the header has to be in the pod's renderer as well —
    a chunk whose header was dropped there would hash to something nobody pinned."""
    chunk = next(one for one in pack["items"] if one["leg"] == "B")
    content = pod.render(prompts, chunk, pack["task"])
    assert "<part>частина 1 з 3</part>" in content
    assert pod.sha256_of_text(content) == chunk["rendering_sha256"]
    whole = next(one for one in pack["items"] if one["leg"] == "A")
    assert "<part>" not in pod.render(prompts, whole, pack["task"])


def test_the_pod_runner_refuses_a_pack_that_carries_no_output_ceiling(pack):
    """A ceiling registered in a record and never passed to the client is a ceiling nobody lifted.
    The refusal is driven, and the message names the default it would otherwise have taken."""
    live = a_pack(pack, items=1)
    del live["serving"]["output_tokens"]
    with pytest.raises(SystemExit, match="ceiling nobody lifted"):
        pod.load_reader(live, REPO_ROOT)


# --- the clocks and the appended gates -------------------------------------------------------------


def test_the_cap_in_seconds_is_recomputed_from_the_price_actually_charged():
    assert driver.usable_seconds(RECORD, RATE) == pytest.approx(USABLE, abs=0.001)
    cheaper = driver.usable_seconds(RECORD, 0.49 / 3600)
    assert cheaper > USABLE
    assert cheaper == pytest.approx(0.45 * 3600 / 0.49 - 60, abs=0.001)


def test_the_affordability_deadline_binds_before_the_twelve_minute_ceiling():
    """A registration whose pre-generation budget is negative says the twelve minutes never gets to
    bind. Driven here rather than read: the gate is asked at a moment and it answers."""
    gate = driver.deadlines(RECORD, RATE, elapsed=10.0, generation_at=5.0)
    assert gate["which_binds"].startswith("affordability")
    assert gate["first_reply_must_land_by_create_elapsed"] == pytest.approx(
        RECORD["money"]["arithmetic"]["affordability_deadline_as_create_elapsed"], abs=0.1
    )
    assert gate["verdict"] == "WAIT"
    # and one second past it, KILL
    past = driver.deadlines(
        RECORD, RATE, elapsed=gate["first_reply_must_land_by_create_elapsed"] + 1, generation_at=5.0
    )
    assert past["verdict"] == "KILL"


def test_the_projection_computes_BOTH_legs_and_the_pessimistic_one_binds(pack):
    rows = [{"id": pack["items"][0]["id"], "seconds": 40.0, "leg": "A"}]
    gate = driver.projection(RECORD, RATE, rows, elapsed=250.0, pack=pack)
    assert gate["units_read"] == 1 and gate["units_unread"] == 25
    assert gate["payable_comments_read"] == pack["items"][0]["payable_comments"]
    assert gate["payable_comments_unread"] == 134 + 43 - gate["payable_comments_read"]
    by = gate["projections"]
    assert by["binding"]["factor"] == max(
        by["by_unit"]["factor"], by["by_payable_comment"]["factor"]
    )
    assert by["binding"]["which"] in ("by_unit", "by_payable_comment")
    # the verdict re-derives from the pair of SECONDS and never from the dollars
    assert (gate["measured_seconds_per_unit"] <= gate["seconds_per_unit_that_still_fits"]) is (
        gate["verdict"] == "GO"
    )


def test_a_unit_slow_enough_to_break_the_cap_is_a_STOP(pack):
    rows = [{"id": pack["items"][0]["id"], "seconds": 400.0, "leg": "A"}]
    assert driver.projection(RECORD, RATE, rows, elapsed=250.0, pack=pack)["verdict"] == "STOP"


def test_a_torn_LAST_line_is_dropped_and_a_torn_middle_one_still_raises(tmp_path, capsys):
    """The jsonl is copied back while the pod appends to it, so its final line can be half written
    at the moment scp reads it. That is a race, on the kill-rule path, where a traceback costs
    billed seconds — but only the last line gets the benefit of the doubt."""
    path = tmp_path / "pod.jsonl"
    good = json.dumps({"id": "a", "seconds": 1.0})
    path.write_text(f'{good}\n{{"id": "b", "sec', encoding="utf-8")
    assert [row["id"] for row in driver.raw_rows(path)] == ["a"]
    assert "dropped a torn last line" in capsys.readouterr().out

    path.write_text(f'{{"id": "b", "sec\n{good}\n', encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        driver.raw_rows(path)


def test_every_gate_snapshot_is_APPENDED_and_none_is_overwritten(tmp_path, monkeypatch):
    """reader-v4's record overwrote its own first GO snapshot. A list cannot lose a reading."""
    monkeypatch.setattr(driver, "RECORD", tmp_path / "run.json")
    state = {"phase": "reader-v5", "pod": {"pod_id": "x"}, "gates": []}
    for index, kind in enumerate(("open", "boot_kill", "full_pass", "full_pass")):
        state = driver.append_gate(state, {"verdict": f"V{index}"}, kind)
    written = json.loads((tmp_path / "run.json").read_text(encoding="utf-8"))
    assert [one["kind"] for one in written["gates"]] == [
        "open",
        "boot_kill",
        "full_pass",
        "full_pass",
    ]
    assert [one["verdict"] for one in written["gates"]] == ["V0", "V1", "V2", "V3"]
    assert written["latest"] == {"kind": "full_pass", "verdict": "V3"}


# --- the ingest ------------------------------------------------------------------------------------


def raw_for(pack, replies: dict) -> list[dict]:
    return [
        {
            "id": one["id"],
            "rendering_sha256": one["rendering_sha256"],
            "reply": replies[one["id"]],
            "balanced": True,
            "emitted_chars": len(replies[one["id"]]),
            "cut_chars": 0,
            "finish_reason": "stop",
            "usage": {"prompt_tokens": 10, "completion_tokens": 20},
            "seconds": 1.0,
        }
        for one in pack["items"]
        if one["id"] in replies
    ]


def chunk_reply(item, *, in_noise=()) -> str:
    return json.dumps(
        {
            "thread": {"channel": item["channel"], "post_id": item["post_id"]},
            "post_summary": "п",
            "discussion_summary": f"частина {item['part'][0]}.",
            "entities": [],
            "signals": [],
            "per_comment": [
                {"msg_id": one, "subject_type": None}
                for one in item["msg_ids"]
                if one not in in_noise
            ],
            "noise": [{"msg_id": one, "class": "оффтоп"} for one in in_noise],
        },
        ensure_ascii=False,
    )


def test_the_ingest_merges_leg_bs_chunks_into_one_row_and_keeps_the_parts(pack):
    items = {one["id"]: one for one in pack["items"] if one["leg"] == "B"}
    replies = {name: chunk_reply(one) for name, one in items.items()}
    rows = driver.ingest(RECORD, raw_for(pack, replies), pack)
    merged = [row for row in rows if row["id"].endswith("#merged")]
    assert len(rows) == 4 and len(merged) == 1
    assert merged[0]["merged_from"] == sorted(items)
    assert merged[0]["merge_error"] is None
    assert len(merged[0]["parsed"]["per_comment"]) == 43
    assert merged[0]["echo"]["covered"] == 43 and merged[0]["echo"]["absent"] == []
    assert merged[0]["parsed"]["discussion_summary"] == "частина 1. частина 2. частина 3."


def test_a_chunk_that_refuses_leaves_the_merge_UNMADE_and_says_why(pack):
    items = {one["id"]: one for one in pack["items"] if one["leg"] == "B"}
    replies = {name: chunk_reply(one) for name, one in items.items()}
    replies[sorted(items)[1]] = "not json at all"
    rows = driver.ingest(RECORD, raw_for(pack, replies), pack)
    merged = next(row for row in rows if row["id"].endswith("#merged"))
    assert merged["parsed"] is None
    assert "1 of 3 chunks did not parse" in merged["merge_error"]


def test_the_echo_census_rides_on_every_leg_a_row(pack):
    item = next(one for one in pack["items"] if one["leg"] == "A" and one["payable_comments"] > 3)
    body = json.loads(chunk_reply(item | {"part": [1, 1]}))
    body["per_comment"] = body["per_comment"][:-1]  # one id left out
    rows = driver.ingest(
        RECORD, raw_for(pack, {item["id"]: json.dumps(body, ensure_ascii=False)}), pack
    )
    assert rows[0]["echo"]["absent"] == [item["msg_ids"][-1]]
    assert rows[0]["echo"]["covered"] == item["payable_comments"] - 1


# --- the scorer --------------------------------------------------------------------------------------


def evidence_file(path: Path, pack: dict, verdicts: dict, leg_b_rows: list[dict]) -> Path:
    rows = []
    for one in pack["items"]:
        if one["leg"] != "A":
            continue
        body = verdicts.get(one["thread"])
        rows.append(
            {
                "id": one["id"],
                "leg": "A",
                "thread": one["thread"],
                "part": None,
                "msg_ids": one["msg_ids"],
                "payable_comments": one["payable_comments"],
                "task": pack["task"],
                "reply": json.dumps(body, ensure_ascii=False) if body else "",
                "parsed": body,
                "repairs": [] if body else None,
                "parse_error": None if body else "empty reply",
                "echo": {
                    "requested": one["payable_comments"],
                    "in_per_comment": [
                        row["msg_id"] for row in (body or {}).get("per_comment", [])
                    ],
                    "in_noise": [],
                    "absent": [],
                    "extra": [],
                    "duplicated": [],
                    "in_both_lists": [],
                    "covered": one["payable_comments"],
                    "in_list_order": True,
                },
                "seconds": {"worker": 40.0},
                "finish_reason": "stop",
                "balanced": True,
                "cut_chars": 0,
                "usage": {"completion_tokens": 800, "prompt_tokens": 2000},
            }
        )
    rows += leg_b_rows
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )
    return path


def leg_b_perfect(pack: dict) -> list[dict]:
    items = [one for one in pack["items"] if one["leg"] == "B"]
    rows = []
    for one in items:
        rows.append(
            {
                "id": one["id"],
                "leg": "B",
                "thread": one["thread"],
                "part": one["part"],
                "msg_ids": one["msg_ids"],
                "payable_comments": one["payable_comments"],
                "task": pack["task"],
                "parsed": json.loads(chunk_reply(one)),
                "parse_error": None,
                "finish_reason": "stop",
                "balanced": True,
                "cut_chars": 0,
                "seconds": {"worker": 30.0},
                "usage": {"completion_tokens": 900, "prompt_tokens": 2000},
            }
        )
    ids = [msg_id for one in items for msg_id in one["msg_ids"]]
    merged = {
        "thread": {"channel": items[0]["channel"], "post_id": items[0]["post_id"]},
        "post_summary": "п",
        "discussion_summary": "д",
        "entities": [],
        "signals": [],
        "per_comment": [{"msg_id": one, "subject_type": None} for one in ids],
        "noise": [],
        "repairs": [],
    }
    rows.append(
        {
            "id": f"{items[0]['thread']}#merged",
            "leg": "B",
            "thread": items[0]["thread"],
            "part": None,
            "merged_from": [one["id"] for one in items],
            "msg_ids": ids,
            "payable_comments": len(ids),
            "task": pack["task"],
            "parsed": merged,
            "merge_error": None,
            "echo": {
                "requested": len(ids),
                "in_per_comment": ids,
                "in_noise": [],
                "absent": [],
                "extra": [],
                "duplicated": [],
                "in_both_lists": [],
                "covered": len(ids),
                "in_list_order": True,
            },
            "seconds": {"worker": 90.0},
        }
    )
    return rows


@pytest.fixture
def score(tmp_path, monkeypatch, pack):
    def run(verdicts, leg_b_rows=None):
        monkeypatch.setattr(
            scoring,
            "EVIDENCE",
            evidence_file(
                tmp_path / "evidence.jsonl",
                pack,
                verdicts,
                leg_b_rows if leg_b_rows is not None else leg_b_perfect(pack),
            ),
        )
        monkeypatch.setattr(scoring, "RUN", tmp_path / "no-such-run.json")
        monkeypatch.setattr(scoring, "LEDGER", tmp_path / "no-such-ledger.json")
        return scoring.build()

    return run


def test_a_perfect_reader_passes_every_leg_a_bar_and_leg_b_is_scored_apart(score):
    record = score(perfect())
    assert record["evidence"]["leg_a_read"] == 23
    assert record["evidence"]["leg_b_units"] == 3
    for name, state in record["bars"].items():
        assert state["verdict"] == "SCORED", name
        assert state["result"]["passed"] is True, name
    mechanical = record["leg_b_mechanical"]
    for name in (
        "m1_every_payable_id_exactly_once",
        "m2_every_chunk_finished",
        "m3_every_chunk_parses",
        "m4_the_merge_has_no_duplicate_signal",
    ):
        assert mechanical[name]["passed"] is True, name
    assert record["5_time_and_cost"]["state"] == "NO LEDGER"


def test_leg_bs_rows_cannot_reach_a_leg_a_bar(score):
    """The registration's own sentence, driven: leg B answered perfectly and leg B answered not at
    all give the SAME four bars, because none of its rows is in their population."""
    both = score(perfect())
    without = score(perfect(), leg_b_rows=[])
    assert both["bars"] == without["bars"]
    assert both["completeness"] == without["completeness"]
    assert without["leg_b_mechanical"]["m1_every_payable_id_exactly_once"]["passed"] is False


def test_m1_fails_on_a_duplicate_across_chunks_and_names_it(score, pack):
    rows = leg_b_perfect(pack)
    merged = rows[-1]
    merged["echo"]["duplicated"] = [merged["msg_ids"][0]]
    record = score(perfect(), leg_b_rows=rows)
    assert record["leg_b_mechanical"]["m1_every_payable_id_exactly_once"]["passed"] is False
    assert record["leg_b_mechanical"]["m1_every_payable_id_exactly_once"]["duplicated"] == [
        merged["msg_ids"][0]
    ]


def test_m1_does_NOT_fail_on_an_id_the_reader_put_in_BOTH_lists(score, pack):
    """The reachability the registration states. reader-v4 broke «at most one of per_comment and
    noise» on 3 of 111 ids with no chunking anywhere near it, and the parser tolerates it by design.
    A bar that exists to prove the chunking MECHANISM may not fail for that
    ([[an_absolute_bar_needs_a_reachability_state]])."""
    rows = leg_b_perfect(pack)
    merged = rows[-1]
    both = merged["msg_ids"][0]
    merged["echo"]["in_both_lists"] = [both]
    merged["parsed"]["noise"] = [{"msg_id": both, "class": "оффтоп"}]
    m1 = score(perfect(), leg_b_rows=rows)["leg_b_mechanical"]["m1_every_payable_id_exactly_once"]
    assert m1["in_both_lists"] == [both]
    assert m1["passed"] is True, "an at-most-one slip is REPORTED, never gating"
    # the control, one line up: the same row with a real cross-part duplicate DOES fail
    merged["echo"]["duplicated"] = [both]
    assert (
        score(perfect(), leg_b_rows=rows)["leg_b_mechanical"]["m1_every_payable_id_exactly_once"][
            "passed"
        ]
        is False
    )


def test_m1_fails_when_the_merge_could_not_be_made(score, pack):
    """A merge that raised leaves no union to count, and «43 of 43» over nothing is not a pass."""
    rows = leg_b_perfect(pack)
    rows[-1]["merge_error"] = "msg_id 21231 is in the per_comment of chunk 1 and chunk 2"
    m1 = score(perfect(), leg_b_rows=rows)["leg_b_mechanical"]["m1_every_payable_id_exactly_once"]
    assert m1["passed"] is False


def test_m2_fails_when_a_chunk_ran_to_the_ceiling(score, pack):
    rows = leg_b_perfect(pack)
    rows[1]["finish_reason"] = "length"
    record = score(perfect(), leg_b_rows=rows)
    assert record["leg_b_mechanical"]["m2_every_chunk_finished"]["passed"] is False


def test_m4_fails_when_two_identical_signals_survive_the_merge(score, pack):
    rows = leg_b_perfect(pack)
    twice = {
        "signal_type": "спрос",
        "proposed": False,
        "from_post": False,
        "subject_type": "категория_личное",
        "subject_id": "морозиво",
        "aspect": "availability",
        "stance": None,
        "reading": "р",
        "evidence": [1],
        "quote": "ц",
    }
    rows[-1]["parsed"]["signals"] = [twice, dict(twice)]
    record = score(perfect(), leg_b_rows=rows)
    assert record["leg_b_mechanical"]["m4_the_merge_has_no_duplicate_signal"]["passed"] is False
    assert record["leg_b_mechanical"]["m4_the_merge_has_no_duplicate_signal"]["distinct_keys"] == 1


def test_the_gate_path_is_driven_through_main_and_names_a_missing_pack(tmp_path, monkeypatch, pack):
    """v5's `--gate` reads the PACK, which v4's never had to — the projection's second leg needs the
    per-unit payable counts. That is a new file dependency on the KILL-RULE path, so it is driven
    end to end and its absence is a named refusal rather than a traceback on a live pod."""
    monkeypatch.setattr(driver, "RECORD", tmp_path / "run.json")
    monkeypatch.setattr(driver, "PACK", tmp_path / "pack.json")
    monkeypatch.setattr(driver, "registration", lambda: RECORD)
    raw = tmp_path / "pod.jsonl"
    item = pack["items"][0]
    raw.write_text(
        json.dumps({"id": item["id"], "seconds": 40.0}, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (tmp_path / "run.json").write_text(
        json.dumps(
            {
                "phase": "reader-v5",
                "pod": {"created_at": CREATED, "usd_per_hour": 0.74},
                "gates": [],
            }
        ),
        encoding="utf-8",
    )

    # the pack is not there yet: a named refusal, and it says where to write it
    with pytest.raises(SystemExit, match="does not exist, and the gate reads it"):
        driver.main(["--gate", "--raw", str(raw)])

    (tmp_path / "pack.json").write_text(json.dumps(pack, ensure_ascii=False), encoding="utf-8")
    now = driver.stamp(CREATED).replace(minute=4)
    assert driver.main(["--gate", "--raw", str(raw)], now=now) == 0
    written = json.loads((tmp_path / "run.json").read_text(encoding="utf-8"))
    assert [one["kind"] for one in written["gates"]] == ["full_pass"]
    assert written["gates"][0]["verdict"] == "GO"
    assert written["gates"][0]["units_read"] == 1 and written["gates"][0]["units_unread"] == 25
    assert written["gates"][0]["read_from"]["exists"] is True


def test_the_completeness_census_names_the_absent_ids_and_gates_nothing(score, pack):
    verdicts = perfect()
    census = score(verdicts)["completeness"]
    assert census["totals"]["requested"] == 134
    assert census["totals"]["absent"] == 0
    assert "REPORTED and never gating" in census["rule"]
    assert census["v4_baseline"]["answered_only_in_noise"] == 18
    assert "not a 93-of-111 ratio" in census["v4_baseline"]["reading"]


def test_the_stop_rule_travels_into_the_verdict(score):
    record = score(perfect())
    assert "prompt-engineering" in record["registration"]["programme_stop_rule"]
    assert "never a v6" in record["registration"]["programme_stop_rule"]


def test_the_gold_the_scorer_reads_is_the_registered_one(score):
    assert scoring.GOLD.name == "reader_gold_w1_r2.json"
    assert GOLD["revision"]["name"] == "r2"
    record = score(perfect())
    assert record["gold"]["revision"] == "r2"
    assert record["scorer"]["unchanged"] is True
