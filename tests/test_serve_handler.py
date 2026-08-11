"""The serverless worker, driven by a stub client — an import proves nothing about a handler.

The worker is the half of the parity measurement that runs where no test can follow it, so
what is checked here is everything that decides a number *before* the weights: which config
the environment names, what `info` promises the Mac-side guard, and that a batch is handed
to `LocalClient` untouched. The load itself is the one thing stubbed out.
"""

import hashlib
import importlib.util
import json
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

INFO_A = {"serving_config": "A"}
"""What `describe` puts in front of `handle`, reduced to the field the op router reads.

`{}` used to do here: until SPEC 3.17 (9) there were two ops and the routing was one XOR, which
read False on both sides for an info dict naming no config at all. `serving.CONFIG_OPS` is a
closed table now and an unnamed config answers nothing — an endpoint that cannot say what it
loaded is not a configuration (`serving.assert_serving`, same rule one layer up)."""


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
        {"input": {"op": "batch", "task": "T1", "texts": ["a", "b"], "posts": None}}, client, INFO_A
    )
    assert client.seen == [("T1", ["a", "b"], None)]
    assert out["n"] == 2 and len(out["replies"]) == 2


def test_the_parent_post_travels_with_the_row():
    client = StubClient()
    handler.handle(
        {"input": {"op": "batch", "task": "T2", "texts": ["a"], "posts": [{"post_text": "p"}]}},
        client,
        INFO_A,
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
        handler.handle({"input": payload}, StubClient(), INFO_A)


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


def test_info_names_the_commit_the_worker_is_serving():
    """`git_state()` in the record names the Mac's HEAD; the worker runs the volume's
    checkout. A record that describes code which did not serve is not provenance."""
    info = handler.describe(handler.settings(ENV_A), {}, "b3ca6308", {})
    assert "repo_commit" in info
    assert info["repo_commit"] == handler.repo_commit()


def test_the_commit_is_absent_rather_than_fatal_off_a_checkout(monkeypatch):
    monkeypatch.setattr(handler, "REPO_ROOT", Path("/nonexistent-checkout"))
    assert handler.repo_commit() is None


# --- srv-2d: one job carries a whole input, and the worker walks it -----------


def test_a_job_without_a_batch_size_is_one_forward_as_it_always_was():
    """The default is what the 8-row smoke measured; srv-2d must not move it silently."""
    client = StubClient()
    handler.handle(
        {"input": {"op": "batch", "task": "T1", "texts": ["a", "b", "c"]}}, client, INFO_A
    )
    assert client.seen == [("T1", ["a", "b", "c"], None)]


def test_batch_size_1_makes_every_forward_a_one_row_call():
    """The parity claim in one line: the transport changed, the generate call did not."""
    client = StubClient()
    out = handler.handle(
        {"input": {"op": "batch", "task": "T1", "texts": ["a", "b", "c"], "batch_size": 1}},
        client,
        INFO_A,
    )
    assert client.seen == [("T1", ["a"], None), ("T1", ["b"], None), ("T1", ["c"], None)]
    assert [r["content"] for r in out["replies"]] == ["reply to a", "reply to b", "reply to c"]
    assert out["n"] == 3


def test_the_parent_posts_are_sliced_with_their_rows():
    """A window that took the whole posts list would render every row against post 0."""
    client = StubClient()
    posts = [{"post_text": "p0"}, {"post_text": "p1"}]
    handler.handle(
        {
            "input": {
                "op": "batch",
                "task": "T1",
                "texts": ["a", "b"],
                "posts": posts,
                "batch_size": 1,
            }
        },
        client,
        INFO_A,
    )
    assert client.seen == [("T1", ["a"], [posts[0]]), ("T1", ["b"], [posts[1]])]


def test_a_zero_batch_size_is_refused_rather_than_looping_forever():
    with pytest.raises(ValueError, match="batch_size must be at least 1"):
        handler.handle(
            {"input": {"op": "batch", "task": "T1", "texts": ["a"], "batch_size": 0}},
            StubClient(),
            INFO_A,
        )


def test_the_rows_land_on_the_volume_as_they_are_generated(tmp_path):
    """The async result is deleted after 30 minutes and the job runs for the better part of
    an hour — until it returns, this file is the only copy of the rows already answered."""
    dump = tmp_path / "parity_comments.jsonl"
    out = handler.handle(
        {
            "input": {
                "op": "batch",
                "task": "T1",
                "texts": ["a", "b"],
                "batch_size": 1,
                "dump_path": str(dump),
            }
        },
        StubClient(),
        INFO_A,
    )
    lines = [json.loads(line) for line in dump.read_text(encoding="utf-8").splitlines()]
    assert [line["i"] for line in lines] == [0, 1]
    assert [line["reply"]["content"] for line in lines] == ["reply to a", "reply to b"]
    # the row's own text, so a recovered dump can be CHECKED against the test set
    assert lines[0]["sha8"] == hashlib.sha256(b"a").hexdigest()[:8]
    assert out["dump_path"] == str(dump) and out["forward_batch_size"] == 1


def test_a_job_that_asked_for_no_dump_writes_none(tmp_path):
    out = handler.handle(
        {"input": {"op": "batch", "task": "T1", "texts": ["a"]}}, StubClient(), INFO_A
    )
    assert "dump_path" not in out
    assert list(tmp_path.iterdir()) == []


# --- srv-2d: the SDK release RunPod documents as breaking job delivery --------


@pytest.mark.parametrize("version", ["1.7.11", "1.8.0", "1.10.0", "1.9.9"])
def test_the_broken_sdk_range_refuses_to_serve(version):
    with pytest.raises(SystemExit, match="job tracking"):
        handler.assert_sdk_version(version)


@pytest.mark.parametrize("version", ["1.10.1", "1.11.0", "2.0.0", "1.11.0.post1"])
def test_a_fixed_sdk_serves(version):
    assert handler.assert_sdk_version(version) == version


def test_an_sdk_that_cannot_name_itself_is_refused_too():
    """`library_versions` answers None for a distribution that is not installed."""
    with pytest.raises(SystemExit, match="cannot name its dispatcher"):
        handler.assert_sdk_version(None)


def test_the_bar_is_a_floor_and_not_a_range_test():
    """RunPod documents 1.7.11-1.10.0 as broken and 1.10.1 as the fix. Nothing says an
    OLDER release is safe, so the guard is a floor — and its message says so, because a
    refusal that misdescribes the version it refused sends the next reader to the wrong page."""
    assert handler.MIN_RUNPOD_SDK == (1, 10, 1)
    with pytest.raises(SystemExit, match="below 1.10.1"):
        handler.assert_sdk_version("1.7.10")
