"""lora-c's generation legs, DRIVEN on the Mac against the frozen packs — before any pod exists.

Both transports: the four pass-1 legs through `scripts/pass1_v3_pod_runner.py`, and the two pass-2
legs through the shipped `scripts/pass2_r2_pod_runner.py`.

`results/lora_c_eval_pack.json` is an input to shipped code, so it is run through that code at $0
rather than described ([[a_frozen_record_is_an_input_to_shipped_code]]). Three refusals of the
SHIPPED chain are driven first, because a sibling written against a gap nobody measured is a sibling
written against a guess — and because the same class of gap once killed an attempt at 427 billed
seconds with the model loaded and nothing read.

The strong check here is `--pack` through `main()` with a fake client: `reader_v5_pod_runner.run`
calls the handshake and then `check_requests`, which RE-RENDERS all 198 items and compares each
against the pack's own `rendering_sha256`. Every request this pod would send is therefore proven
against the registration on this machine, for free.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import pass1_fewshot_pod_runner as fewshot  # noqa: E402
import pass1_pod_runner as pass1  # noqa: E402
import pass1_v3_pod_runner as v3runner  # noqa: E402
import pass2_r2_pod_runner as pass2runner  # noqa: E402
import reader_v5_pod_runner as runner  # noqa: E402

from market_pulse import pass1_v3, prompts  # noqa: E402

PACK_PATH = REPO_ROOT / "results" / "lora_c_eval_pack.json"
PACK = json.loads(PACK_PATH.read_text("utf-8"))
LEGS = {leg["name"]: leg for leg in PACK["legs"]}


def registered_render(item: dict, task: str) -> str:
    """What the registration says this request IS — rendered from the module that owns the task."""
    if task == pass1_v3.PASS1_TASK_V3:
        return pass1_v3.pass1_messages_gm4_v3(
            item["channel"],
            item["post_id"],
            item["topic"],
            item["entities"],
            item["msg_id"],
            item["text"],
            examples=item["examples"],
        )[0]["content"]
    return prompts.pass1_messages_gm4(
        item["channel"],
        item["post_id"],
        item["topic"],
        item["entities"],
        item["msg_id"],
        item["text"],
        task=task,
        examples=item["examples"],
    )[0]["content"]


# --- what the SHIPPED chain does with this pack --------------------------------------------------


def test_the_shipped_handshake_refuses_this_pack_including_its_v2_leg():
    """v3 is not in `prompts.PASS1` and may not be added, so the shipped family map is short.

    Both legs die on it, not just the v3 one: one pack carries both and the map is compared whole.
    This is the loud half of the gap — it fires before the model is loaded.
    """
    assert pass1_v3.PASS1_TASK_V3 not in prompts.PASS1
    assert pass1_v3.PASS1_TASK_V3 in PACK["instruments"]["prompt_sha256"]
    with pytest.raises(SystemExit, match="not the registered instrument"):
        pass1.check_instrument(PACK, REPO_ROOT, prompts)


def test_the_shipped_render_sends_a_v3_item_to_the_readers_renderer():
    """The quiet half — a KeyError raised on a pod, at the price of a loaded model.

    `pass1_fewshot_pod_runner.render` hands anything outside `prompts.PASS1` down the shipped chain,
    which hands it to the reader's own renderer, which wants a `post` field a pass-1 item has never
    carried ([[a_stub_replaces_the_guard_it_should_trigger]]).
    """
    item = LEGS["v3"]["items"][0]
    with pytest.raises(KeyError, match="post"):
        fewshot.render(prompts, item, LEGS["v3"]["task"])


def test_the_shipped_leg_runner_has_no_adapter_flag():
    """The third gap: lora-c's two arm legs are the same pack with an adapter mounted."""
    with pytest.raises(SystemExit):
        fewshot.main(["--pack", str(PACK_PATH), "--outdir", "/tmp/x", "--adapter", "/tmp/a"])


# --- what the sibling does with it ---------------------------------------------------------------


@pytest.mark.parametrize("leg", ("v2", "v3"))
def test_the_sibling_renders_each_leg_as_its_own_registered_renderer_does(leg):
    """Under the real nesting, and compared with the module that OWNS the task, not with itself."""
    item = LEGS[leg]["items"][0]
    with v3runner.as_v3(), fewshot.as_fewshot():
        got = runner.render(prompts, item, LEGS[leg]["task"])
    assert got == registered_render(item, LEGS[leg]["task"])


def test_the_siblings_handshake_serves_all_three_texts_and_pins_the_v3_module():
    """The family the pack names, plus a sha the shipped handshake knows nothing about."""
    with v3runner.as_v3(), fewshot.as_fewshot():
        got = runner.check_instrument(PACK, REPO_ROOT, prompts)
    assert sorted(got["prompt_sha256"]) == [
        "pass1_comment_gm4_v1",
        "pass1_comment_gm4_v2",
        "pass1_comment_gm4_v3",
    ]
    assert got["module_v3_sha256"] == PACK["instruments"]["module_v3_sha256"]
    assert got["parser_sha256"] == PACK["instruments"]["parser"]["sha256"]


def test_the_handshake_refuses_a_moved_v3_module(tmp_path):
    """The negative control: the pin is worth nothing until it has been seen to fire."""
    moved = {**PACK, "instruments": {**PACK["instruments"], "module_v3_sha256": "0" * 64}}
    with v3runner.as_v3(), fewshot.as_fewshot():  # noqa: SIM117 — the nesting IS the thing driven
        with pytest.raises(SystemExit, match="pass1_v3.py hashes"):
            runner.check_instrument(moved, REPO_ROOT, prompts)


def test_the_swaps_are_put_back():
    """Line B's own runs share this process — a swap that leaked would re-render their packs."""
    before = (fewshot.render, pass1.SWAPPED)
    with v3runner.as_v3():
        assert fewshot.render is v3runner.render
        assert pass1.SWAPPED["check_instrument"] is v3runner.check_instrument
    assert (fewshot.render, pass1.SWAPPED) == before


def test_the_swap_refuses_a_chain_that_moved_under_it(monkeypatch):
    """A rename one layer down must be loud, never a silent fall-back to the shipped behaviour."""
    monkeypatch.setattr(pass1, "SWAPPED", {"render": pass1.render})
    with pytest.raises(SystemExit, match="no longer carries"):
        with v3runner.as_v3():
            pass


@pytest.mark.parametrize("leg", ("v2", "v3"))
def test_every_request_of_the_leg_matches_the_packs_own_per_item_sha(leg, tmp_path, monkeypatch):
    """`main()` DRIVEN with a fake client — the handshake and all 198 renders, at $0.

    `reader_v5_pod_runner.run` re-renders every item and compares it against the pack's
    `rendering_sha256` before a single reply is generated, so this is the whole transport proven
    against the frozen record on a Mac ([[stub_driven_script_verification]]). What it cannot cover
    is the constructor's own template probe — that lives behind the loader this test replaces, and
    it is the shipped chain's, unchanged and already paid for three times.
    """
    answered = []

    class Fake:
        def read(self, task, items):
            answered.append((task, items[0]["id"]))
            return [
                {
                    "content": '{"msg_id": 1, "subject_type": null, "subject_id": null, "stance": null}'
                }
            ]

    code = v3runner.main(
        [
            "--pack",
            str(PACK_PATH),
            "--outdir",
            str(tmp_path),
            "--repo",
            str(REPO_ROOT),
            "--only",
            leg,
        ],
        loader=lambda pack, repo: Fake(),
    )
    assert code == 0
    assert len(answered) == LEGS[leg]["n"] == 198
    assert {task for task, _ in answered} == {LEGS[leg]["task"]}
    written = (tmp_path / LEGS[leg]["out"]).read_text("utf-8").splitlines()
    assert len(written) == 198


def test_an_adapter_is_recorded_before_the_first_reply(tmp_path, monkeypatch):
    """The observable that says WHICH arm answered — written before anything is generated.

    `PeftModel.from_pretrained` injects into the base modules in place, so afterwards no evidence
    row distinguishes the arms. The record is the adapter's own files, hashed
    ([[baseline_before_the_run_not_after]]).
    """
    adapter = tmp_path / "adapter"
    adapter.mkdir()
    (adapter / "adapter_model.safetensors").write_bytes(b"weights")
    (adapter / "adapter_config.json").write_text("{}", encoding="utf-8")
    outdir = tmp_path / "eval_a"

    seen = {}

    def loader(pack, repo):
        seen["loaded"] = True

        class Fake:
            def read(self, task, items):
                return [
                    {
                        "content": '{"msg_id": 1, "subject_type": null, "subject_id": null, "stance": null}'
                    }
                ]

        return Fake()

    v3runner.main(
        [
            "--pack",
            str(PACK_PATH),
            "--outdir",
            str(outdir),
            "--repo",
            str(REPO_ROOT),
            "--only",
            "v3",
            "--adapter",
            str(adapter),
        ],
        loader=loader,
    )
    record = json.loads((outdir / "adapter.json").read_text("utf-8"))
    assert record["adapter"] == str(adapter)
    assert sorted(record["files"]) == ["adapter_config.json", "adapter_model.safetensors"]


def test_the_entry_point_runs_as_a_command():
    """A preamble is untested code until something executes it — and a missing --leg is the refusal."""
    import subprocess

    done = subprocess.run(
        [sys.executable, "scripts/pass1_v3_pod_runner.py", "--pack", str(PACK_PATH)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={"PYTHONPATH": "src", "PATH": "/usr/bin:/bin:/usr/local/bin"},
    )
    assert done.returncode != 0
    assert "--outdir" in done.stdout + done.stderr


# --- the pass-2 legs -----------------------------------------------------------------------------

PASS2_PATH = REPO_ROOT / "results" / "lora_c_pass2_pack.json"
PASS2 = json.loads(PASS2_PATH.read_text("utf-8"))


def test_the_pass_2_pack_carries_the_instrument_block_its_runner_reads():
    """The shape belongs to the pinned handshake, not to the builder's taste.

    `pass2_r2_pod_runner.check_instrument` reads `parser.sha256`, `module.sha256` and
    `module_r2.sha256`. This pack shipped a flat `module_sha256` string until r2 drove it, so every
    pass-2 leg of this line would have died on a `KeyError` with the model already loaded.
    """
    block = PASS2["instruments"]
    for name in ("parser", "module", "module_r2"):
        assert isinstance(block[name], dict) and len(block[name]["sha256"]) == 64, name
    for name, path in (
        ("parser", "src/market_pulse/prompts.py"),
        ("module", "src/market_pulse/pass2.py"),
        ("module_r2", "src/market_pulse/pass2_r2.py"),
    ):
        assert block[name]["path"] == path


def test_the_pass_2_transport_is_driven_end_to_end_with_a_fake_client(tmp_path):
    """Eleven threads, the handshake and every per-item sha — at $0, on the shipped runner."""
    answered = []

    class Fake:
        def read(self, task, items):
            answered.append(items[0]["id"])
            return [{"content": '{"signals": [], "drops": [], "subject_doubt": []}'}]

    code = pass2runner.main(
        ["--pack", str(PASS2_PATH), "--outdir", str(tmp_path), "--repo", str(REPO_ROOT)],
        loader=lambda pack, repo: Fake(),
    )
    assert code == 0
    assert len(answered) == PASS2["population"]["threads_with_at_least_one_filtered_row"] == 11
