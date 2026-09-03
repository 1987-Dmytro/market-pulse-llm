"""The pod side, driven on the Mac: the render dispatch, the law handshake, and one model load.

The generation needs a rented card, so what is tested here is everything AROUND it — and that is
the half that has killed runs before ([[the_entry_points_preamble_is_untested_code]]). Each check
has its negative control, because a dispatch that only ever answers one way is not a dispatch.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

import promo_dev_pod_runner as pod  # noqa: E402

from market_pulse import prompts, promo_prompts  # noqa: E402

THREAD = {
    "id": "@c:1",
    "task": pod.PROMO_TASK,
    "channel": "@c",
    "post_id": "1",
    "post": "акція",
    "comments": [[2, "смачно"], [3, "дорого"]],
}
POST = {"id": "@c:9", "task": pod.POST_TASK, "text": "Молоко 900 мл 39.90 грн"}


def test_the_render_dispatches_on_the_item_and_falls_back_to_the_shipped_one():
    """Leg A is the promo law, leg B the REGISTERED positions text, and an item with neither goes
    to the reader's own render — the branch `ReaderClient.__init__` takes inside its constructor."""
    leg_a = pod.render(prompts, THREAD, pod.PROMO_TASK)
    assert leg_a == promo_prompts.render("@c", "1", "акція", [
        {"msg_id": 2, "text": "смачно"}, {"msg_id": 3, "text": "дорого"}
    ])
    assert promo_prompts.CODEBOOK.splitlines()[0] in leg_a

    leg_b = pod.render(prompts, POST, pod.PROMO_TASK)
    assert leg_b == prompts.positions_messages_text_gm4(POST["text"])[0]["content"]
    assert leg_b != leg_a

    probe = {"channel": "@probe", "post_id": 1, "post": "проба", "comments": []}
    fallback = pod.render(prompts, probe, prompts.READER_TASK_V2)
    assert fallback == pod.SHIPPED_RENDER(prompts, probe, prompts.READER_TASK_V2)


def test_a_moved_codebook_stops_the_pod_before_the_model_loads():
    """The law is leg A's whole instrument and lives in neither the reader's prompt shas nor its
    parser sha, so it gets its own handshake — and the handshake has to be able to REFUSE."""
    pack = {"instruments": {"leg_a": {"codebook_version": promo_prompts.codebook_version()}}}
    assert pod.check_law(pack, REPO_ROOT)["codebook_version"] == promo_prompts.codebook_version()

    moved = {"instruments": {"leg_a": {"codebook_version": "0" * 64}}}
    with pytest.raises(SystemExit, match="the LAW moved"):
        pod.check_law(moved, REPO_ROOT)


def test_the_go_sits_between_two_runs_and_only_one_boot_pays_for_both(tmp_path, monkeypatch):
    """The smoke, the GO, then the rest — on ONE loaded model. A second `runner.run` that loaded
    again would pay a second boot for a decision the Mac makes in seconds, and the pod is billed
    for every one of them ([[no_rung_watches_an_idle_pod]])."""
    pack = {
        "instruments": {"leg_a": {"codebook_version": promo_prompts.codebook_version()}},
        "items": [dict(THREAD, smoke=True), dict(POST, smoke=False)],
    }
    pack_path, out = tmp_path / "pack.json", tmp_path / "out.jsonl"
    pack_path.write_text(json.dumps(pack), encoding="utf-8")
    go = tmp_path / "go"
    go.write_text(json.dumps({"verdict": "GO"}), encoding="utf-8")

    loads, asked = [], []
    monkeypatch.setattr(pod.runner, "run", lambda p, o, r, loader: (
        loads.append(loader(p, r)), asked.append([one["id"] for one in p["items"]]), 0
    )[-1])
    argv = ["--pack", str(pack_path), "--out", str(out), "--repo", str(REPO_ROOT),
            "--go", str(go), "--go-deadline", "1"]
    assert pod.main(argv, loader=lambda p, r: object()) == 0
    assert asked == [["@c:1"], ["@c:1", "@c:9"]]
    assert loads[0] is loads[1], "two boots for one attempt"


def test_no_go_leaves_the_rest_unasked(tmp_path, monkeypatch):
    """A token that is not a GO ends the process with the remaining units unbought. Guessing GO
    would spend money nobody authorised ([[a_flag_that_asserts_turns_a_poll_into_a_verdict]])."""
    pack = {
        "instruments": {"leg_a": {"codebook_version": promo_prompts.codebook_version()}},
        "items": [dict(THREAD, smoke=True), dict(POST, smoke=False)],
    }
    pack_path, out = tmp_path / "pack.json", tmp_path / "out.jsonl"
    pack_path.write_text(json.dumps(pack), encoding="utf-8")
    asked = []
    monkeypatch.setattr(pod.runner, "run", lambda p, o, r, loader: (
        asked.append([one["id"] for one in p["items"]]), 0
    )[-1])
    argv = ["--pack", str(pack_path), "--out", str(out), "--repo", str(REPO_ROOT),
            "--go", str(tmp_path / "never"), "--go-deadline", "0"]
    assert pod.main(argv, loader=lambda p, r: object(), sleep=lambda _: None) == 0
    assert asked == [["@c:1"]]
