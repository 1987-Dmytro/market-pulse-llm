"""srv-2a: the 5b worker read as a SERVERLESS config, and the runbook that will deploy it.

Nothing here downloads a weight or reaches a network. What it checks is the half of srv-2b
that can be wrong for free on a Mac and expensive on a billed worker:

* the environment `scripts/runbook_srv2b.md` literally prints is the environment
  `serve_handler.settings()` reads — the JSON is parsed out of the document and fed to the
  code, so a doc that drifts from the worker reddens here rather than at a cold start;
* the request/response schema is unchanged against `results/serving_5b.json`, the committed
  record of the run this one must replicate;
* the pins the runbook quotes are re-derived from the records they claim to come from;
* the batch-1 refusal still fires on the exact parity command the runbook prints.
"""

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))


def _script(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


handler = _script("serve_handler")
runner = _script("eval_zero_shot")

RUNBOOK = (REPO_ROOT / "scripts" / "runbook_srv2b.md").read_text(encoding="utf-8")
SERVING_5B = json.loads((REPO_ROOT / "results" / "serving_5b.json").read_text(encoding="utf-8"))
PARITY_5B = json.loads((REPO_ROOT / "results" / "parity_5b_a.json").read_text(encoding="utf-8"))
ADAPTER = REPO_ROOT / "results" / "train" / "45h2-arm-a" / "adapter"


def template_env() -> dict:
    """The `--env '{...}'` block of the runbook's `template create`, as the code will see it.

    Parsed rather than retyped: the point of the test is that the document and the worker
    cannot drift, and a copy of the JSON in this file would drift with neither of them.
    """
    match = re.search(r"--env '(\{.*?\})'", RUNBOOK, re.DOTALL)
    assert match, "the runbook no longer prints a template --env block"
    return json.loads(match.group(1))


# --- the environment contract -----------------------------------------------


def test_the_runbooks_template_env_is_exactly_what_the_worker_reads():
    env = template_env()
    assert set(env) == {"SERVING_CONFIG", "ADAPTER_DIR", "BASE_WEIGHTS", "MODEL_REVISION"}
    config = handler.settings(env)
    assert config["serving_config"] == "A"
    assert config["adapter_dir"] == "/runpod-volume/repo/results/train/45h2-arm-a/adapter"
    assert config["weights_dir"] == "google/gemma-4-31b-it"
    assert config["revision"] == PARITY_5B["config"]["runtime"]["model_revision"]


def test_the_template_does_not_carry_a_knob_the_entrypoint_overrides():
    """`start_5b_worker.sh` exports HF_HOME unconditionally, so a template value would be a
    field someone could edit with no effect at all."""
    assert "HF_HOME" not in template_env()
    entrypoint = (REPO_ROOT / "scripts" / "start_5b_worker.sh").read_text(encoding="utf-8")
    for line in ("export HF_HOME=/runpod-volume/hf", "export HF_HUB_OFFLINE=1"):
        assert line in entrypoint


def test_the_worker_answers_under_the_runbooks_environment():
    """Driven through `Worker`, not `settings`: the lazy load is part of the contract — a
    misconfigured endpoint has to report rather than die before it can (5b.1 D8)."""
    loaded = []

    def loader(config):
        loaded.append(config)
        return object(), handler.describe(config, {"gpu": "<card>"}, "b3ca6308", {})

    worker = handler.Worker(env=template_env(), loader=loader)
    info = worker({"input": {"op": "info"}})
    assert loaded and info["merge_state"] == "unmerged-adapter"
    assert info["chat_template"]["enable_thinking"] is False
    assert info["revision_requested"] == PARITY_5B["config"]["runtime"]["model_revision"]


def test_no_pod_path_is_baked_into_the_worker():
    """The pod runtime symlinks /workspace to /runpod-volume; the code knows neither."""
    for name in ("serve_handler.py", "start_5b_worker.sh"):
        assert "/workspace" not in (REPO_ROOT / "scripts" / name).read_text(encoding="utf-8")


# --- the schema, against the committed 5b record ----------------------------


def test_the_response_schema_is_unchanged_against_the_5b_record():
    info = handler.describe(handler.settings(template_env()), {}, "b3ca6308", {})
    assert set(info) == set(SERVING_5B["worker"]), "srv-2 must not move 5b's info schema"


def test_the_runtime_block_gains_the_reported_libraries_and_nothing_else():
    """`runtime` is free-form provenance and is where the new fields go, because the guard
    that reads it walks a fixed list of three keys while `assert_serving` compares the top
    level. Widening it must still be visible: the added keys are named here."""
    info = handler.describe(
        handler.settings(template_env()), SERVING_5B["worker"]["runtime"], "x", {}
    )
    added = set(info["runtime"]) - set(SERVING_5B["worker"]["runtime"])
    assert added == set(handler.REPORTED_LIBRARIES)


def test_a_library_that_is_not_installed_is_reported_as_absent():
    """peft is the real negative control: it is not installed on the Mac, and `None` is the
    answer rather than a missing key or an ImportError."""
    assert handler.library_versions(("peft",)) == {"peft": None}
    assert handler.library_versions(("no-such-distribution-srv2a",)) == {
        "no-such-distribution-srv2a": None
    }
    assert handler.library_versions(("pytest",))["pytest"] == pytest.__version__


# --- the pins, re-derived from the records the runbook cites ----------------


def test_the_runbook_quotes_the_stack_the_parity_record_pins():
    runtime = PARITY_5B["config"]["runtime"]
    for library in ("torch", "transformers", "bitsandbytes"):
        assert runtime[library] in RUNBOOK, f"{library} {runtime[library]} is not in the runbook"
    assert runtime["model_revision"] in RUNBOOK


def test_the_runbook_pins_the_peft_the_adapter_itself_names():
    """The one library that moves a token and no guard can see. The number is the adapter's
    own, and `adapter_config.json` sits inside the directory whose sha256 IS checked."""
    config = json.loads((ADAPTER / "adapter_config.json").read_text(encoding="utf-8"))
    assert f"peft=={config['peft_version']}" in RUNBOOK
    assert "peft==0.18.0" in RUNBOOK, "the 5b2 line is corrected in the open, not silently"


def test_the_runbook_names_the_adapter_and_carve_digests_and_the_image():
    assert SERVING_5B["worker"]["adapter_sha256"][:12] in RUNBOOK
    assert SERVING_5B["carve"]["sha256"][:12] in RUNBOOK
    assert SERVING_5B["deployment"]["pod"]["imageName"] in RUNBOOK


def test_the_runbook_takes_its_cap_from_the_contract_and_still_defers_the_datacenter():
    """Two things srv-2a must not decide: the money and the region.

    srv-2a left both as placeholders and this test asserted they were empty. The srv-2b briefing
    filled the money one — `docs/PROMPT-srv-2b.md` sets $4.00 and instructs the runbook be filled
    — so "empty" is no longer the property worth pinning. What is: the runbook cannot carry a cap
    the contract did not set. Every guard call gets it, and the region is still read, not chosen.
    """
    contract = (REPO_ROOT / "docs" / "PROMPT-srv-2b.md").read_text(encoding="utf-8")
    cap = re.search(r"\*\*Cap \$(\d+\.\d\d)\*\*", contract)
    assert cap, "the contract no longer states a cap in the form it was briefed in"
    caps = set(re.findall(r"--step-cap (\S+)", RUNBOOK))
    assert caps == {cap.group(1)}, f"the runbook's cap drifted from the contract's: {caps}"
    assert "<DC>" in RUNBOOK, "the datacenter is the C.1 reading's to make, never the runbook's"


# --- the batch-1 guard, on the command the runbook prints -------------------


def parity_argv(batch_size: str) -> list[str]:
    return [
        *("--model", "google/gemma-4-31b-it", "--backend", "endpoint"),
        *("--endpoint-id", "srv2-a", "--serving-config", "A"),
        *("--batch-size", batch_size, "--testset-version", "v4"),
        *("--adapter", str(ADAPTER), "--arm", "without-plast"),
    ]


def test_the_parity_command_is_refused_above_batch_one():
    with pytest.raises(SystemExit, match="scored at batch 1"):
        runner.main(parity_argv("2"))


def test_the_runbook_prints_the_command_at_batch_one():
    """The prose may name `--batch-measurement` — it has to, to forbid it. No command may."""
    commands = "\n".join(re.findall(r"```bash\n(.*?)```", RUNBOOK, re.DOTALL))
    assert "--batch-size 1" in commands
    assert "--batch-measurement" not in commands, "the door 5b.2 opened stays shut for parity"
