"""The serverless worker, driven by a stub client — an import proves nothing about a handler.

The worker is the half of the parity measurement that runs where no test can follow it, so
what is checked here is everything that decides a number *before* the weights: which config
the environment names, what `info` promises the Mac-side guard, and that a batch is handed
to `LocalClient` untouched. The load itself is the one thing stubbed out.
"""

import importlib.util
import sys
from pathlib import Path

import pytest
from market_pulse import local_llm

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
spec = importlib.util.spec_from_file_location(
    "serve_handler", REPO_ROOT / "scripts" / "serve_handler.py"
)
handler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(handler)

ENV_A = {"SERVING_CONFIG": "A", "ADAPTER_DIR": "/vol/adapter", "MODEL_REVISION": "842da379"}
ENV_B = {"SERVING_CONFIG": "B", "MERGED_DIR": "/vol/merged-nf4"}


class StubClient:
    """`LocalClient`'s interface, remembering exactly what it was asked."""

    def __init__(self):
        self.seen = []

    def batch(self, task, texts, posts=None):
        self.seen.append((task, texts, posts))
        return [{"content": f"reply to {text}", "finish_reason": "stop"} for text in texts]


# --- the environment --------------------------------------------------------


def test_config_a_serves_the_base_and_loads_the_adapter_onto_it():
    config = handler.settings(ENV_A)
    assert config["serving_config"] == "A"
    assert config["weights_dir"] == local_llm.MODEL_ID
    assert config["adapter_dir"] == "/vol/adapter"
    assert config["revision"] == "842da379"


def test_config_b_serves_the_merged_checkpoint_and_has_no_adapter():
    config = handler.settings(ENV_B)
    assert config["weights_dir"] == "/vol/merged-nf4"
    assert config["adapter_dir"] is None


def test_a_base_weights_override_is_honoured():
    config = handler.settings(ENV_A | {"BASE_WEIGHTS": "/vol/base-snapshot"})
    assert config["weights_dir"] == "/vol/base-snapshot"


@pytest.mark.parametrize(
    "env, message",
    [
        ({}, "SERVING_CONFIG must be one of"),
        ({"SERVING_CONFIG": "C", "ADAPTER_DIR": "/x"}, "SERVING_CONFIG must be one of"),
        ({"SERVING_CONFIG": "A"}, "config A needs ADAPTER_DIR"),
        ({"SERVING_CONFIG": "B"}, "config B needs MERGED_DIR"),
        ({"SERVING_CONFIG": "B", "MERGED_DIR": "  "}, "config B needs MERGED_DIR"),
    ],
)
def test_a_worker_that_cannot_name_its_config_refuses(env, message):
    with pytest.raises(ValueError, match=message):
        handler.settings(env)


# --- what `info` promises ---------------------------------------------------


def test_info_names_the_unmerged_adapter_for_config_a():
    info = handler.describe(handler.settings(ENV_A), {"gpu": "A6000"}, "b3ca6308", {})
    assert info["merge_state"] == "unmerged-adapter"
    assert info["adapter_sha256"] == "b3ca6308"
    assert info["merged_sha256"] is None
    assert info["quantization"] == local_llm.QUANTIZATION
    assert info["chat_template"] == local_llm.CHAT_TEMPLATE


def test_info_carries_the_source_adapter_through_a_merge():
    """The field means the same thing in both configs, or the two cannot be compared."""
    info = handler.describe(
        handler.settings(ENV_B), {}, "merged-digest", {"adapter_sha256": "b3ca6308"}
    )
    assert info["merge_state"] == "merged-requantized"
    assert info["adapter_sha256"] == "b3ca6308"
    assert info["merged_sha256"] == "merged-digest"


# --- dispatch ---------------------------------------------------------------


def test_batch_reaches_the_client_untouched():
    client = StubClient()
    out = handler.handle(
        {"input": {"op": "batch", "task": "T1", "texts": ["a", "b"], "posts": None}}, client, {}
    )
    assert client.seen == [("T1", ["a", "b"], None)]
    assert out["n"] == 2 and len(out["replies"]) == 2


def test_the_parent_post_travels_with_the_row():
    client = StubClient()
    handler.handle(
        {"input": {"op": "batch", "task": "T2", "texts": ["a"], "posts": [{"post_text": "p"}]}},
        client,
        {},
    )
    assert client.seen[0][2] == [{"post_text": "p"}]


def test_info_answers_without_touching_the_client():
    client = StubClient()
    assert handler.handle({"input": {"op": "info"}}, client, {"serving_config": "A"}) == {
        "serving_config": "A"
    }
    assert client.seen == []


@pytest.mark.parametrize(
    "payload, message",
    [
        ({"op": "generate"}, "unknown op"),
        ({}, "unknown op"),
        ({"op": "batch", "task": "T1", "texts": []}, "non-empty list of texts"),
        ({"op": "batch", "task": "T1"}, "non-empty list of texts"),
    ],
)
def test_a_job_the_worker_cannot_answer_is_an_error(payload, message):
    with pytest.raises(ValueError, match=message):
        handler.handle({"input": payload}, StubClient(), {})


# --- the worker -------------------------------------------------------------


def test_the_worker_loads_once_and_answers_many():
    loads = []

    def loader(config):
        loads.append(config["serving_config"])
        return StubClient(), {"serving_config": config["serving_config"]}

    worker = handler.Worker(env=ENV_A, loader=loader)
    assert worker({"input": {"op": "info"}})["serving_config"] == "A"
    worker({"input": {"op": "batch", "task": "T1", "texts": ["a"]}})
    assert loads == ["A"]


def test_a_misconfigured_worker_reports_instead_of_dying_at_import():
    """The load is lazy on purpose: a container that died at import answers nothing at all."""
    worker = handler.Worker(env={"SERVING_CONFIG": "A"}, loader=lambda _c: (None, None))
    with pytest.raises(ValueError, match="config A needs ADAPTER_DIR"):
        worker({"input": {"op": "info"}})
