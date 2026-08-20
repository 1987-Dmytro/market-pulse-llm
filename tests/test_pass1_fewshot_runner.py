"""The fewshot pod runner — both legs, ONE model load, one out-file each. Driven at $0.

Three things can only be proved here. That the swap really installs the examples-aware render and
puts every shipped name back afterwards, so a later import on the same pod is not answering under
this contract's renderer. That the two dev legs share ONE client — the boot is 350 s measured on
this stack against 5 s a call, and paying it twice is the difference between the budget and the
cap. And that each leg's replies land in its OWN file: the shipped resume skips every id it already
sees, so two legs sharing a file would answer half the units and look complete (Dv560).
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_pass1_fewshot_packs as packs  # noqa: E402
import pass1_fewshot_pod_runner as fewshot  # noqa: E402
import pass1_pod_runner as pass1  # noqa: E402
import reader_v5_pod_runner as runner  # noqa: E402

from market_pulse import prompts  # noqa: E402

DEV = json.loads((REPO_ROOT / packs.DEV_NAME).read_text("utf-8"))
SHOT = json.loads((REPO_ROOT / packs.SHOT_NAME).read_text("utf-8"))


class FakeClient:
    """Answers the schema, and REMEMBERS which task each request came under."""

    def __init__(self):
        self.model = "the base model local_llm built"
        self.tasks = []

    def read(self, task, items):
        (item,) = items
        self.tasks.append(task)
        answer = json.dumps(
            {
                "msg_id": int(item["msg_id"]),
                "subject_type": "категория_личное",
                "subject_id": None,
                "stance": None,
            },
            ensure_ascii=False,
        )
        return [
            {
                "content": answer,
                "finish_reason": "stop",
                "usage": {"prompt_tokens": 900, "completion_tokens": 40},
            }
        ]


def small(pack: dict, per_leg: int = 3) -> dict:
    """The real pack cut to a few units per leg — same shape, same fields, same shas."""
    return {**pack, "legs": [{**leg, "items": leg["items"][:per_leg]} for leg in pack["legs"]]}


def test_the_swap_installs_the_examples_render_and_puts_every_shipped_name_back():
    was = {"render": runner.render, "check_instrument": runner.check_instrument}
    with fewshot.as_fewshot():
        assert runner.render is fewshot.render
        assert runner.check_instrument is pass1.check_instrument
    assert runner.render is was["render"]
    assert runner.check_instrument is was["check_instrument"]


def test_the_render_reproduces_each_legs_registered_sha_and_refuses_a_mixed_item():
    for pack in (DEV, SHOT):
        for leg in pack["legs"]:
            for item in leg["items"][:5]:
                content = fewshot.render(prompts, item, leg["task"])
                assert packs.sha_text(content) == item["rendering_sha256"], item["id"]
    # the v2 item under v1's task, and the base item under v2's — both refused by the renderer
    v2_item = next(one for one in DEV["legs"] if one["name"] == "v2")["items"][0]
    base_item = next(one for one in DEV["legs"] if one["name"] == "base")["items"][0]
    with pytest.raises(ValueError, match="half-applies the revision"):
        fewshot.render(prompts, v2_item, prompts.PASS1_TASK)
    with pytest.raises(ValueError, match="half-applies the revision"):
        fewshot.render(prompts, base_item, prompts.PASS1_TASK_V2)


def test_a_task_that_is_not_pass_1_goes_to_the_shipped_chain():
    """`ReaderClient.__init__` probes the chat template with a READER task before it will build a
    client at all. pass1-probe's attempt died at 427 billed seconds on exactly that call."""
    probe = {"channel": "@probe", "post_id": 1, "post": "проба", "comments": []}
    content = fewshot.render(prompts, probe, prompts.READER_TASK_V2)
    assert content.startswith(prompts.PROMPTS[prompts.READER_TASK_V2])


def test_both_dev_legs_run_off_ONE_client_and_into_their_own_files(tmp_path):
    built = []

    def loader(pack, repo):
        built.append(pack["task"])
        return FakeClient()

    assert (
        fewshot.main(
            [
                "--pack",
                str(write(tmp_path, small(DEV))),
                "--outdir",
                str(tmp_path / "run"),
                "--repo",
                str(REPO_ROOT),
            ],
            loader=loader,
        )
        == 0
    )
    assert len(built) == 1, built  # the second leg does NOT reload 59 GB of weights
    for leg in small(DEV)["legs"]:
        rows = [
            json.loads(line)
            for line in (tmp_path / "run" / leg["out"]).read_text("utf-8").splitlines()
            if line
        ]
        assert [row["id"] for row in rows] == [one["id"] for one in leg["items"]]
        assert all(row["balanced"] for row in rows)
        assert {row["rendering_sha256"] for row in rows} == {
            one["rendering_sha256"] for one in leg["items"]
        }
    # the two files really are two populations: the shas differ row for row
    base_rows, v2_rows = (
        [
            json.loads(line)
            for line in (tmp_path / "run" / name).read_text("utf-8").splitlines()
            if line
        ]
        for name in (packs.DEV_LEGS["base"], packs.DEV_LEGS["v2"])
    )
    assert [row["rendering_sha256"] for row in base_rows] != [
        row["rendering_sha256"] for row in v2_rows
    ]


def test_each_leg_is_answered_under_its_OWN_task(tmp_path):
    client = FakeClient()
    assert (
        fewshot.main(
            [
                "--pack",
                str(write(tmp_path, small(DEV))),
                "--outdir",
                str(tmp_path / "run"),
                "--repo",
                str(REPO_ROOT),
            ],
            loader=lambda pack, repo: client,
        )
        == 0
    )
    assert client.tasks == [prompts.PASS1_TASK] * 3 + [prompts.PASS1_TASK_V2] * 3


def test_only_narrows_to_one_leg_and_refuses_a_name_that_is_not_one(tmp_path):
    pack = write(tmp_path, small(DEV))
    assert (
        fewshot.main(
            [
                "--pack",
                str(pack),
                "--outdir",
                str(tmp_path / "one"),
                "--repo",
                str(REPO_ROOT),
                "--only",
                "v2",
            ],
            loader=lambda p, r: FakeClient(),
        )
        == 0
    )
    assert (tmp_path / "one" / packs.DEV_LEGS["v2"]).exists()
    assert not (tmp_path / "one" / packs.DEV_LEGS["base"]).exists()
    with pytest.raises(SystemExit, match="not a leg of this pack"):
        fewshot.main(
            [
                "--pack",
                str(pack),
                "--outdir",
                str(tmp_path / "two"),
                "--repo",
                str(REPO_ROOT),
                "--only",
                "nope",
            ],
            loader=lambda p, r: FakeClient(),
        )


def test_a_pack_with_no_legs_is_refused_by_name(tmp_path):
    flat = {**DEV}
    flat.pop("legs")
    with pytest.raises(SystemExit, match="carries no `legs`"):
        fewshot.main(
            [
                "--pack",
                str(write(tmp_path, flat)),
                "--outdir",
                str(tmp_path / "run"),
                "--repo",
                str(REPO_ROOT),
            ],
            loader=lambda p, r: FakeClient(),
        )


def test_the_shot_leg_writes_a_file_no_dev_leg_would_resume_over(tmp_path):
    """Dv560: the shipped resume skips every id already in the out-file, so the shot's own file is
    what makes «64 answered» mean sixty-four questions asked."""
    assert (
        fewshot.main(
            [
                "--pack",
                str(write(tmp_path, small(SHOT))),
                "--outdir",
                str(tmp_path / "run"),
                "--repo",
                str(REPO_ROOT),
            ],
            loader=lambda p, r: FakeClient(),
        )
        == 0
    )
    shot = tmp_path / "run" / packs.SHOT_LEG["shot"]
    assert shot.exists()
    assert not (tmp_path / "run" / packs.DEV_LEGS["base"]).exists()
    # and the id spaces are disjoint, so a shot row could never be mistaken for a dev row
    dev_ids = {one["id"] for leg in DEV["legs"] for one in leg["items"]}
    shot_ids = {one["id"] for one in SHOT["legs"][0]["items"]}
    assert dev_ids & shot_ids == set()


def write(where: Path, pack: dict) -> Path:
    path = where / "pack.json"
    path.write_text(json.dumps(pack, ensure_ascii=False), encoding="utf-8")
    return path
