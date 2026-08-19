"""`--adapter` on the pass-1 transport — both argv branches, driven at $0.

The flag is the one thing lora-b adds to the pod's own command, and the failure it can have is
silent: `PeftModel.from_pretrained` injects LoRA into the base modules IN PLACE, so after the wrap
the base and the adapted model are not distinguishable by identity, and an evidence file carries
nothing that says which arm produced it. So the branches are separated by what the run RECORDS —
the mounted adapter, hashed, written beside the evidence before the first reply.

The `attach` half is driven directly with a fake `peft` rather than only through `main(loader=...)`:
a stub loader replaces the very code path the flag exists to exercise.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import pass1_pod_runner as podrunner  # noqa: E402
import reader_v5_pod_runner as runner  # noqa: E402

PACK = json.loads((REPO_ROOT / "results" / "pass1_probe_b_pack.json").read_text("utf-8"))


class FakeClient:
    """Answers every request with the object the schema asks for — the transport sim's own."""

    def __init__(self):
        self.model = "the base model local_llm built"

    def read(self, task, items):
        (item,) = items
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


def adapter_dir(tmp_path: Path) -> Path:
    path = tmp_path / "adapter"
    path.mkdir()
    (path / "adapter_config.json").write_text('{"peft_type": "LORA"}', encoding="utf-8")
    (path / "adapter_model.safetensors").write_bytes(b"not really weights")
    return path


def three_item_pack(tmp_path: Path) -> Path:
    pack = json.loads(json.dumps(PACK))
    pack["items"] = pack["items"][:3]
    path = tmp_path / "pack.json"
    path.write_text(json.dumps(pack, ensure_ascii=False), encoding="utf-8")
    return path


def fake_peft(monkeypatch, *, takes: bool):
    import types

    class Wrapped:
        def __init__(self, base):
            self.base = base
            if takes:
                self.peft_config = {"default": object()}

    module = types.ModuleType("peft")
    module.PeftModel = type(
        "PeftModel", (), {"from_pretrained": staticmethod(lambda model, path: Wrapped(model))}
    )
    monkeypatch.setitem(sys.modules, "peft", module)
    return Wrapped


# --- the argv split ---------------------------------------------------------


def test_the_flag_never_reaches_the_shipped_parser_and_out_still_does():
    adapter, out, rest = podrunner.split(
        ["--pack", "p.json", "--out", "o.jsonl", "--repo", "/r", "--adapter", "/a"]
    )
    assert adapter == Path("/a") and out == Path("o.jsonl")
    assert "--adapter" not in rest and "/a" not in rest
    assert rest.count("--out") == 1 and "o.jsonl" in rest
    # and what is left is exactly what the shipped runner has always parsed
    parsed = runner.argparse.ArgumentParser()
    parsed.add_argument("--pack", type=Path, required=True)
    parsed.add_argument("--out", type=Path, required=True)
    parsed.add_argument("--repo", type=Path)
    assert parsed.parse_args(rest).out == Path("o.jsonl")


def test_without_the_flag_the_argv_is_untouched_and_the_loader_is_the_shipped_one():
    adapter, out, rest = podrunner.split(["--pack", "p.json", "--out", "o.jsonl"])
    assert adapter is None
    assert sorted(rest) == sorted(["--pack", "p.json", "--out", "o.jsonl"])
    assert podrunner.with_adapter(None) is runner.load_reader


# --- the wrap ---------------------------------------------------------------


def test_attach_wraps_the_model_local_llm_built(monkeypatch):
    Wrapped = fake_peft(monkeypatch, takes=True)
    client = FakeClient()
    base = client.model
    assert podrunner.attach(client, Path("/adapter")) is client
    assert isinstance(client.model, Wrapped)
    assert client.model.base == base


def test_attach_refuses_a_wrap_that_did_not_take(monkeypatch):
    """The failure that would publish an ablation with no ablation in it."""
    fake_peft(monkeypatch, takes=False)
    with pytest.raises(SystemExit, match="carrying no peft_config"):
        podrunner.attach(FakeClient(), Path("/adapter"))


def test_the_shipped_loader_asserts_no_adapter_BEFORE_this_one_attaches_one():
    """Order, not presence: the base-only handshake is passed and then deliberately reversed."""
    shipped = Path(runner.__file__).read_text(encoding="utf-8")
    assert "serve_handler.assert_no_adapter(model)" in shipped
    ours = Path(podrunner.__file__).read_text(encoding="utf-8")
    assert "def assert_no_adapter" not in ours  # inherited, never re-implemented
    # the order is the nesting: the shipped loader RUNS, and the wrap goes on what it returns
    assert "attach(runner.load_reader(pack, repo), adapter)" in ours


# --- what the run records ---------------------------------------------------


def test_the_adapter_record_is_written_before_the_run_and_hashes_every_file(tmp_path):
    out = tmp_path / "pod.jsonl"
    adapter = adapter_dir(tmp_path)
    assert (
        podrunner.main(
            [
                "--pack",
                str(three_item_pack(tmp_path)),
                "--out",
                str(out),
                "--repo",
                str(REPO_ROOT),
                "--adapter",
                str(adapter),
            ],
            loader=lambda pack, repo: FakeClient(),
        )
        == 0
    )
    record = json.loads((tmp_path / "pod.jsonl.adapter.json").read_text(encoding="utf-8"))
    assert record["adapter"] == str(adapter)
    assert sorted(record["files"]) == ["adapter_config.json", "adapter_model.safetensors"]
    assert all(len(sha) == 64 for sha in record["files"].values())
    assert len(out.read_text(encoding="utf-8").splitlines()) == 3


def test_a_run_with_no_adapter_leaves_no_record_beside_its_evidence(tmp_path):
    """The other branch: an evidence file with no record beside it was answered by the BASE."""
    out = tmp_path / "pod.jsonl"
    assert (
        podrunner.main(
            [
                "--pack",
                str(three_item_pack(tmp_path)),
                "--out",
                str(out),
                "--repo",
                str(REPO_ROOT),
            ],
            loader=lambda pack, repo: FakeClient(),
        )
        == 0
    )
    assert not (tmp_path / "pod.jsonl.adapter.json").exists()
    assert len(out.read_text(encoding="utf-8").splitlines()) == 3


def test_the_swap_still_puts_every_shipped_name_back_with_the_flag_on(tmp_path):
    before = {name: getattr(runner, name) for name in podrunner.SWAPPED}
    podrunner.main(
        [
            "--pack",
            str(three_item_pack(tmp_path)),
            "--out",
            str(tmp_path / "pod.jsonl"),
            "--repo",
            str(REPO_ROOT),
            "--adapter",
            str(adapter_dir(tmp_path)),
        ],
        loader=lambda pack, repo: FakeClient(),
    )
    assert {name: getattr(runner, name) for name in podrunner.SWAPPED} == before
