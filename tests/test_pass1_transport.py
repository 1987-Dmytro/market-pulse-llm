"""The two thin callers of pass-1-probe — driven, not described.

`scripts/pass1_pod_runner.py` and `scripts/read_pass1_probe.py` both work by SWAPPING names on
shipped modules, which is a shape that fails silently in exactly two ways: the name it replaces
stops existing, or the swap is never put back. Both are exercised here, and the runner is driven end
to end on a FAKE client so the render, the resume-skip and the per-row persistence are proved without
a GPU ([[stub_driven_script_verification]]).
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import moved_pins  # noqa: E402
import pass1_pod_runner as podrunner  # noqa: E402
import read_pass1_probe as driver  # noqa: E402
import read_threads_reader_v5 as v5  # noqa: E402
import read_threads_reader_v5b as v5b  # noqa: E402
import reader_v5_pod_runner as shipped  # noqa: E402

from market_pulse import prompts  # noqa: E402

SEALED = json.loads((REPO_ROOT / "results" / "pass1_probe_pack.json").read_text(encoding="utf-8"))
"""probe-a's own pack, as it was sealed. It pins the `prompts.py` of the day it was written, and
`docs/PROMPT-pass1-fewshot.md` D0.2 moved that module — so the handshake refuses it now, BY NAME,
and the test below asserts that refusal instead of pretending it away."""


PACK = moved_pins.servable(SEALED)


# --- the swaps ------------------------------------------------------------------------------------


def test_the_runner_swap_puts_every_shipped_name_back():
    before = {name: getattr(shipped, name) for name in podrunner.SWAPPED}
    with podrunner.as_pass1():
        assert shipped.render is podrunner.render
        assert shipped.check_instrument is podrunner.check_instrument
    assert {name: getattr(shipped, name) for name in podrunner.SWAPPED} == before


def test_the_runner_swap_refuses_a_name_the_shipped_runner_no_longer_has(monkeypatch):
    """The failure a swap cannot otherwise see: the shipped runner renames `render`, this file goes
    on setting an attribute nobody reads, and the run silently uses the READER's request."""
    monkeypatch.delattr(shipped, "render")
    with pytest.raises(SystemExit, match="has no `render` any more"):
        with podrunner.as_pass1():
            pass


def test_the_driver_swap_reaches_v5b_and_through_it_v5_and_puts_both_back():
    before_b = {name: getattr(v5b, name) for name in driver.SWAPPED}
    before_5 = {name: getattr(v5, name) for name in driver.SWAPPED}
    with driver.as_this_phase():
        assert v5b.PHASE == "pass1-probe"
        assert v5b.PACK == REPO_ROOT / "results" / "pass1_probe_pack.json"
        with v5b.as_this_phase():
            assert v5.PHASE == "pass1-probe"
            assert v5.PREREG == REPO_ROOT / "results" / "prereg_pass1_probe.json"
    assert {name: getattr(v5b, name) for name in driver.SWAPPED} == before_b
    assert {name: getattr(v5, name) for name in driver.SWAPPED} == before_5


def test_the_driver_ledger_is_this_steps_and_not_the_readers():
    assert driver.LEDGER.name == "spend_pass1_probe.json"
    assert driver.PHASE == "pass1-probe" != v5b.PHASE


# --- the handshake --------------------------------------------------------------------------------


def test_the_handshake_asks_the_pass1_family_and_refuses_a_moved_text():
    got = podrunner.check_instrument(PACK, REPO_ROOT, prompts)
    # the handshake answers with the family this checkout SERVES, which since D0.2 is two texts,
    # while the pack pins one — and a text registered LATER is not expected to be in an older map
    assert got["prompt_sha256"] == {
        task: prompts.prompt_sha256(task) for task in sorted(prompts.PASS1)
    }
    assert set(PACK["instruments"]["prompt_sha256"]) == {prompts.PASS1_TASK}
    bent = json.loads(json.dumps(PACK))
    bent["instruments"]["prompt_sha256"][prompts.PASS1_TASK] = "0" * 64
    with pytest.raises(SystemExit, match="not the registered instrument"):
        podrunner.check_instrument(bent, REPO_ROOT, prompts)
    moved = json.loads(json.dumps(PACK))
    moved["instruments"]["parser"]["sha256"] = "0" * 64
    with pytest.raises(SystemExit, match="the parser and the renderer have parted"):
        podrunner.check_instrument(moved, REPO_ROOT, prompts)
    # a task the pack pins that this checkout does not serve is «unserved here» and refused too
    unknown = json.loads(json.dumps(PACK))
    unknown["instruments"]["prompt_sha256"]["pass1_comment_gm4_v9"] = "0" * 64
    with pytest.raises(SystemExit, match="unserved here"):
        podrunner.check_instrument(unknown, REPO_ROOT, prompts)


def test_the_SEALED_pack_is_no_longer_servable_and_the_refusal_names_why():
    """The consequence of registering a second pass-1 text, asserted rather than discovered.

    `src/market_pulse/prompts.py` moved when `pass1_comment_gm4_v2` joined it, so probe-a's own
    pack — whose parser pin is that module — can no longer be served on this checkout. That is the
    correct outcome and it is the one the contract wants: the base's evidence is the file
    `results/pass1_probe_b_verdict.json` already holds, and it is never re-run
    ([[the_identity_field_stops_covering_the_change]]). v1's TEXT is untouched, which is what keeps
    the old evidence comparable.
    """
    with pytest.raises(SystemExit, match="the parser and the renderer have parted"):
        podrunner.check_instrument(SEALED, REPO_ROOT, prompts)
    assert SEALED["instruments"]["prompt_sha256"][prompts.PASS1_TASK] == prompts.prompt_sha256(
        prompts.PASS1_TASK
    )


def test_the_shipped_reader_handshake_would_have_refused_this_pack():
    """Why the handshake had to be pass 1's own rather than the shipped one: the pack pins a family
    `prompts.READER` does not contain, so the shipped check reads a correct pod as a wrong one."""
    from reader_v4_pod_runner import check_instrument as reader_handshake

    with pytest.raises(SystemExit, match="unserved here"):
        reader_handshake(PACK, REPO_ROOT, prompts)


# --- the runner, end to end on a fake client ------------------------------------------------------


class FakeClient:
    """A client that answers every request with the object the schema asks for.

    It reads the request the runner actually built, so a render that lost the msg_id attribute would
    answer about nothing — the echo below is the check that catches it.
    """

    def __init__(self, requests: list[str]) -> None:
        self.requests = requests

    def read(self, task, items):
        (item,) = items
        content = shipped.render(prompts, item, task)
        self.requests.append(content)
        msg_id = content.split('<comment msg_id="')[1].split('"')[0]
        answer = json.dumps(
            {
                "msg_id": int(msg_id),
                "subject_type": "категория_личное",
                "subject_id": None,
                "stance": None,
            },
            ensure_ascii=False,
        )
        return [
            {
                "content": answer + "\ntrailing prose the stop would have cut",
                "finish_reason": "stop",
                "usage": {"prompt_tokens": 900, "completion_tokens": 40},
            }
        ]


def test_the_runner_renders_pass1_requests_and_persists_one_row_per_unit(tmp_path):
    pack = json.loads(json.dumps(PACK))
    pack["items"] = pack["items"][:3]
    out = tmp_path / "pod.jsonl"
    requests: list[str] = []
    assert (
        podrunner.main(
            [
                "--pack",
                str(_write(tmp_path / "pack.json", pack)),
                "--out",
                str(out),
                "--repo",
                str(REPO_ROOT),
            ],
            loader=lambda pack, repo: FakeClient(requests),
        )
        == 0
    )
    rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines() if line]
    assert [row["id"] for row in rows] == [one["id"] for one in pack["items"]]
    # the requests really are pass 1's, not the reader's
    assert all(request.startswith(prompts.PASS1_COMMENT_PROMPT) for request in requests)
    assert all(request.count("<comment ") == 1 for request in requests)
    # and the balanced stop cut the trailing prose off what was persisted
    for row in rows:
        assert row["balanced"] is True and row["cut_chars"] > 0
        assert prompts.parse_pass1(row["reply"], msg_id=int(row["id"].split("#")[1]))


def test_a_second_run_re_asks_nothing_that_is_already_answered(tmp_path):
    pack = json.loads(json.dumps(PACK))
    pack["items"] = pack["items"][:3]
    path = _write(tmp_path / "pack.json", pack)
    out = tmp_path / "pod.jsonl"
    first: list[str] = []
    podrunner.main(
        ["--pack", str(path), "--out", str(out), "--repo", str(REPO_ROOT)],
        loader=lambda pack, repo: FakeClient(first),
    )
    again: list[str] = []
    assert (
        podrunner.main(
            ["--pack", str(path), "--out", str(out), "--repo", str(REPO_ROOT)],
            loader=lambda pack, repo: FakeClient(again),
        )
        == 0
    )
    assert len(first) == 3 and again == [], "an answered unit was re-asked — the resume is not one"


def _write(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


# --- the ingest -----------------------------------------------------------------------------------


def test_the_ingest_parses_with_the_REQUESTS_msg_id_and_names_its_refusals(tmp_path, monkeypatch):
    """The echo check is only a check while the id it compares against comes from the PACK. A reply
    that answers about a neighbouring comment has to be REFUSED, not silently accepted."""
    pack = json.loads(json.dumps(PACK))
    pack["items"] = pack["items"][:3]
    good, other, broken = pack["items"]
    raw = [
        {
            "id": good["id"],
            "reply": json.dumps(
                {"msg_id": good["msg_id"], "subject_type": None, "subject_id": None, "stance": None}
            ),
        },
        {
            "id": other["id"],
            "reply": json.dumps(
                {"msg_id": good["msg_id"], "subject_type": None, "subject_id": None, "stance": None}
            ),
        },
        {"id": broken["id"], "reply": "no object here"},
    ]
    monkeypatch.setattr(driver, "EVIDENCE", tmp_path / "rows.jsonl")
    rows = driver.ingest({}, raw, pack)
    assert [row["parse_error"] for row in rows] == [
        None,
        f"msg_id echoes {good['msg_id']}, not the {other['msg_id']} it was asked about",
        "no JSON object in reply",
    ]
    assert rows[0]["parsed"]["msg_id"] == good["msg_id"]
    written = [
        json.loads(line)
        for line in (tmp_path / "rows.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    assert [row["id"] for row in written] == [one["id"] for one in pack["items"]]
    assert all(row["rendering_sha256"] for row in written)


# --- the defect that ate the attempt ---------------------------------------------------------------

PROBE = {"channel": "@probe", "post_id": 1, "post": "проба", "comments": []}
"""The exact item `local_llm.ReaderClient._assert_template_emits_bos` probes the chat template with.

Copied here rather than imported because it is a LITERAL inside a module this contract may not edit,
and the test below asserts that the literal is still that one — a probe that changed shape would make
this check pass while the pod crashed again ([[the_control_whose_premise_stopped_being_true]])."""


def test_the_swapped_render_survives_the_BOS_probe_local_llm_makes_on_every_client():
    """pass1-probe's whole attempt died here, at 427 billed seconds with nothing read.

    `ReaderClient.__init__` calls `_assert_template_emits_bos`, which renders a READER-shaped probe
    with `READER_TASK_V2` through `self.render` — and `self.render` is the runner's swapped one. The
    swap assumed every call it would ever see was a pass-1 item, so the constructor of the client
    raised `KeyError: 'topic'` AFTER the model had loaded.

    The stub-driven test above could not see it: a fake client replaces the very constructor whose
    self-check makes the call.
    """
    with podrunner.as_pass1():
        rendered = shipped.render(prompts, PROBE, prompts.READER_TASK_V2)
    assert rendered.startswith(prompts.PROMPTS[prompts.READER_TASK_V2])
    assert "@probe" in rendered
    # and a pass-1 item still renders as pass 1 through the same swapped function
    item = PACK["items"][0]
    with podrunner.as_pass1():
        mine = shipped.render(prompts, item, prompts.PASS1_TASK)
    assert mine.startswith(prompts.PASS1_COMMENT_PROMPT)


def test_the_probe_local_llm_uses_is_still_the_one_this_file_guards_against():
    """The premise. If `local_llm`'s probe grows a field or changes task, the guard above stops
    guarding the call that actually happens."""
    source = (REPO_ROOT / "src" / "market_pulse" / "local_llm.py").read_text(encoding="utf-8")
    assert 'probe = {"channel": "@probe", "post_id": 1, "post": "проба", "comments": []}' in source
    assert "self.render(prompts.READER_TASK_V2, probe)" in source
