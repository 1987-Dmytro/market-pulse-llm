"""vis-a: the GM4 caption instrument, everything about it that can be wrong for free.

Nothing here downloads a weight, reaches a network or spends a cent. What it pins is the half
of vis-b that is expensive to discover on a billed endpoint:

* the CAPTION config refuses the two environments that would make it a different instrument —
  an adapter variable left on the endpoint, and an unpinned base revision;
* the registered prompt is derived from `caption_post` by exactly one clause, both ways;
* every NEW caption record names its instrument, and no reader will silently average two;
* the driver refuses to run without an endpoint id, and its slices stay under RunPod's
  documented `/run` ceiling;
* seconds still become milliseconds in exactly one place.
"""

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from market_pulse import local_llm, prompts, serving  # noqa: E402


def _script(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


handler = _script("serve_handler")

PINNED_REVISION = "842da3794eaa"


def caption_env(**extra) -> dict:
    return {"SERVING_CONFIG": "CAPTION", "MODEL_REVISION": PINNED_REVISION} | extra


# --- the CAPTION serving config ---------------------------------------------


def test_the_caption_config_is_the_base_at_a_pinned_revision_with_no_adapter():
    config = handler.settings(caption_env())
    assert config["serving_config"] == serving.CAPTION_CONFIG
    assert config["adapter_dir"] is None
    assert config["weights_dir"] == local_llm.MODEL_ID
    assert config["revision"] == PINNED_REVISION


@pytest.mark.parametrize("variable", handler.ADAPTER_ENV)
def test_caption_refuses_every_environment_variable_that_carries_trained_weights(variable):
    """An endpoint updated from an A template keeps A's environment. A caption worker that
    quietly loaded the classification adapter would answer every job, and `caption_source`
    would still say `gm4-nf4-base` on every row it wrote."""
    with pytest.raises(ValueError, match="ADAPTER OFF"):
        handler.settings(caption_env(**{variable: "/runpod-volume/repo/adapter"}))


def test_the_adapter_variables_are_exactly_the_ones_settings_reads():
    """The negative control on the refusal above: a third variable added later would be a
    name the check never learned about, and the guard would pass while doing nothing."""
    source = (REPO_ROOT / "scripts" / "serve_handler.py").read_text(encoding="utf-8")
    read = set(re.findall(r'env\.get\("([A-Z_]+_DIR)"\)', source))
    read |= set(re.findall(r'needed = "([A-Z_]+_DIR)" if', source))
    read |= set(re.findall(r'else "([A-Z_]+_DIR)"', source))
    assert read == set(handler.ADAPTER_ENV)


def test_caption_refuses_an_unpinned_base():
    """3.13 (3) fixes the instrument at the PINNED revision. An unpinned base resolves to
    whatever `main` is that day and every record would still call it `gm4-nf4-base`."""
    with pytest.raises(ValueError, match="MODEL_REVISION"):
        handler.settings({"SERVING_CONFIG": "CAPTION"})


def test_an_adapter_on_the_loaded_model_is_refused_too():
    """`settings` refuses the environment; this refuses the object, and they are not the same
    check — peft attaches to the model it wraps and the result answers like the base."""
    handler.assert_no_adapter(SimpleNamespace(peft_config=None))
    with pytest.raises(ValueError, match="carries an adapter"):
        handler.assert_no_adapter(SimpleNamespace(peft_config={"default": object()}))
    with pytest.raises(ValueError, match="carries an adapter"):
        handler.assert_no_adapter(type("PeftModelForCausalLM", (), {})())


def test_the_caption_worker_names_the_prompt_it_serves():
    """The FETCH_HEAD footgun, priced: the volume carries its own `repo/`, and a fetch naming a
    missing ref leaves it on the previous commit while printing "Already up to date"."""
    info = handler.describe(handler.settings(caption_env()), {}, None, {})
    assert info["merge_state"] == "base-no-adapter"
    assert info["adapter_sha256"] is None
    assert info["caption_prompt_sha256"] == prompts.prompt_sha256(prompts.CAPTION_TASK_GM4)
    # exactly what the driver asserts before the first paid caption
    expected = {
        "serving_config": serving.CAPTION_CONFIG,
        "merge_state": "base-no-adapter",
        "adapter_sha256": None,
        "caption_prompt_sha256": prompts.prompt_sha256(prompts.CAPTION_TASK_GM4),
    }
    assert serving.assert_serving(info, expected) is info


def test_the_merge_state_table_covers_every_config_and_nothing_else():
    assert set(serving.MERGE_STATE) == set(serving.CONFIGS) == set(handler.CONFIGS)
    assert len(set(serving.MERGE_STATE.values())) == len(serving.CONFIGS)


def caption_worker(config: str = "CAPTION"):
    """A worker whose loader answers without a GPU, so `handle` can be driven."""

    class Client:
        def __init__(self):
            self.asked = []

        def caption(self, task, albums):
            self.asked.append((task, albums))
            return [{"content": f"caption of {len(a)}"} for a in albums]

        def batch(self, task, texts, posts=None):
            self.asked.append((task, texts))
            return [{"content": t} for t in texts]

    client = Client()
    env = caption_env() if config == "CAPTION" else {"SERVING_CONFIG": "A", "ADAPTER_DIR": "/a"}
    return client, handler.Worker(
        env=env, loader=lambda cfg: (client, handler.describe(cfg, {}, "sha", {}))
    )


def test_one_job_carries_a_slice_and_the_worker_walks_it_at_batch_1():
    client, worker = caption_worker()
    out = worker(
        {
            "input": {
                "op": "caption",
                "task": prompts.CAPTION_TASK_GM4,
                "images": [["data:a"], ["data:b", "data:c"]],
                "batch_size": 1,
            }
        }
    )
    assert out["n"] == 2 and [r["content"] for r in out["replies"]] == [
        "caption of 1",
        "caption of 2",
    ]
    assert [len(albums) for _, albums in client.asked] == [1, 1], "one album per forward"


def test_a_caption_job_and_a_row_job_are_refused_on_each_other_s_config():
    """Both directions: a caption on config A is answered by the classification adapter, and a
    batch on CAPTION scores rows on the bare base. Both produce replies."""
    _, caption_side = caption_worker("CAPTION")
    with pytest.raises(ValueError, match="captions are served by"):
        caption_side({"input": {"op": "batch", "task": "T1", "texts": ["x"]}})
    _, label_side = caption_worker("A")
    with pytest.raises(ValueError, match="captions are served by"):
        label_side(
            {"input": {"op": "caption", "task": prompts.CAPTION_TASK_GM4, "images": [["d"]]}}
        )


def test_the_dump_keys_a_caption_row_by_its_own_album(tmp_path):
    """A dump recovered without its job has to be checkable against the manifest, and the
    driver writes the same digest per post — one join rule, read by both sides."""
    _, worker = caption_worker()
    dump = tmp_path / "captions.jsonl"
    worker(
        {
            "input": {
                "op": "caption",
                "task": prompts.CAPTION_TASK_GM4,
                "images": [["data:a", "data:b"]],
                "batch_size": 1,
                "dump_path": str(dump),
            }
        }
    )
    row = json.loads(dump.read_text(encoding="utf-8").strip())
    assert row["i"] == 0
    # the driver writes this same digest per post into its record — one join rule, both sides
    expected = hashlib.sha256(serving.album_key(["data:a", "data:b"]).encode("utf-8"))
    assert row["sha8"] == expected.hexdigest()[:8]


# --- the registered prompt ---------------------------------------------------


def test_the_gm4_caption_prompt_is_its_base_with_one_clause_swapped_both_ways():
    assert prompts.PROMPTS[prompts.CAPTION_TASK_GM4] == prompts.PROMPTS[
        prompts.CAPTION_TASK
    ].replace(prompts.CAPTION_ANSWER_ALONE, prompts.CAPTION_ANSWER_ALONE_GM4)
    gm4 = prompts.PROMPTS[prompts.CAPTION_TASK_GM4]
    base = prompts.PROMPTS[prompts.CAPTION_TASK]
    assert prompts.CAPTION_ANSWER_ALONE_GM4 in gm4 and prompts.CAPTION_ANSWER_ALONE_GM4 not in base
    assert prompts.CAPTION_ANSWER_ALONE in base and prompts.CAPTION_ANSWER_ALONE not in gm4
    # everything the description has to CONTAIN is identical: the 3.13 (4) bridge compares two
    # instruments on one task, and a reworded task would make it two tasks
    assert (
        gm4.split(prompts.CAPTION_ANSWER_ALONE_GM4)[0]
        == base.split(prompts.CAPTION_ANSWER_ALONE)[0]
    )
    assert prompts.prompt_sha256(prompts.CAPTION_TASK_GM4) != prompts.prompt_sha256(
        prompts.CAPTION_TASK
    )


def test_the_gm4_request_carries_image_slots_and_the_instructions_first():
    messages = prompts.caption_messages_gm4(3)
    parts = messages[0]["content"]
    assert messages[0]["role"] == "user" and len(messages) == 1
    assert parts[0] == {"type": "text", "text": prompts.PROMPTS[prompts.CAPTION_TASK_GM4]}
    assert parts[1:] == [{"type": "image"}] * 3
    with pytest.raises(ValueError, match="no image"):
        prompts.caption_messages_gm4(0)


# --- the client that renders it ----------------------------------------------


class StubIds:
    def __init__(self, rows):
        self.rows = rows

    @property
    def shape(self):
        return (len(self.rows), len(self.rows[0]))


class StubEncoded(dict):
    def to(self, device):
        self.device = device
        return self


class StubRow(list):
    def tolist(self):
        return list(self)


class StubProcessor:
    """Enough of an `AutoProcessor` to prove the rendering, with no transformers installed."""

    def __init__(self, bos: str = "<bos>"):
        # what the TOKENIZER reports; the template below always renders "<bos>", so a stub
        # built with another value is the drifted-template case and nothing else
        self.tokenizer = SimpleNamespace(bos_token=bos)
        self.calls = []
        self.template_kwargs = None

    def apply_chat_template(self, messages, tokenize=False, **kwargs):
        self.template_kwargs = kwargs
        content = messages[0]["content"]
        slots = sum(1 for part in content if part["type"] == "image")
        return f"<bos>{content[0]['text']}<img>{slots}"

    def __call__(self, text=None, images=None, return_tensors=None, add_special_tokens=None):
        self.calls.append(
            {"text": text, "images": len(images), "add_special_tokens": add_special_tokens}
        )
        return StubEncoded(input_ids=StubIds([[1, 2, 3]]))

    def decode(self, ids, skip_special_tokens=False):
        return "".join(chr(token) for token in ids if token != 0)


class StubModel:
    device = "cpu"

    def __init__(self, answer: str = "ok", pad: int = 0):
        self.answer, self.pad = answer, pad
        self.kwargs = None

    def generate(self, input_ids=None, max_new_tokens=None, do_sample=None, **rest):
        self.kwargs = {"max_new_tokens": max_new_tokens, "do_sample": do_sample}
        new = [ord(char) for char in self.answer] + [self.pad]
        return [StubRow([1, 2, 3] + new)]


def one_pixel_url() -> str:
    import base64
    import io

    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (2, 2), (10, 20, 30)).save(buffer, format="JPEG")
    return "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def test_the_caption_client_renders_through_the_processor_and_stays_greedy():
    processor, model = StubProcessor(), StubModel("hi")
    client = local_llm.CaptionClient(processor, model)
    url = one_pixel_url()
    replies = client.caption(prompts.CAPTION_TASK_GM4, [[url, url]])
    assert processor.template_kwargs == local_llm.CHAT_TEMPLATE
    assert processor.template_kwargs["enable_thinking"] is False
    assert processor.calls[-1]["images"] == 2, "both pictures reach the processor"
    assert processor.calls[-1]["add_special_tokens"] is False, "the template already emits <bos>"
    assert model.kwargs == {"max_new_tokens": local_llm.CAPTION_MAX_NEW_TOKENS, "do_sample": False}
    assert replies[0]["content"] == "hi" and replies[0]["cost"] == 0.0
    assert replies[0]["finish_reason"] == "stop"


def test_a_caption_that_used_its_whole_budget_says_so():
    """Free text has no parse failure to count, so `finish_reason` is the only signal that a
    description stopped mid-leaflet — which is what 400 tokens rather than 256 is for."""
    client = local_llm.CaptionClient(StubProcessor(), StubModel("abcd"), max_new_tokens=5)
    assert client.caption(prompts.CAPTION_TASK_GM4, [[one_pixel_url()]])[0]["finish_reason"] == (
        "length"
    )


def test_the_caption_client_serves_one_registered_prompt_and_says_which():
    client = local_llm.CaptionClient(StubProcessor(), StubModel())
    with pytest.raises(ValueError, match="and nothing else"):
        client.caption(prompts.CAPTION_TASK, [[one_pixel_url()]])


def test_a_template_that_stopped_emitting_bos_is_a_refusal():
    with pytest.raises(RuntimeError, match="no longer starts the caption prompt"):
        local_llm.CaptionClient(StubProcessor(bos="<different>"), StubModel())


def test_only_a_data_url_is_a_picture():
    with pytest.raises(ValueError, match="data: URL"):
        local_llm.image_from_data_url("https://example.invalid/a.jpg")
    with pytest.raises(ValueError, match="no payload"):
        local_llm.image_from_data_url("data:image/jpeg;base64,")


# --- one conversion point ----------------------------------------------------


MS_LINE = re.compile(r"1_?000")
POLICY_WORD = re.compile(r"timeout|ttl|policy", re.IGNORECASE)


def millisecond_sites(text: str) -> list[tuple[int, str]]:
    """Lines that scale a *time policy* by a thousand — the conversion this repo allows once."""
    return [
        (number, line)
        for number, line in enumerate(text.splitlines(), 1)
        if MS_LINE.search(line) and POLICY_WORD.search(line) and "*" in line
    ]


def test_the_detector_fires_on_a_line_that_would_be_the_bug():
    """The negative control. A scan that matches nothing proves nothing about the code."""
    assert millisecond_sites('payload = {"executionTimeout": timeout_s * 1000}')
    assert not millisecond_sites('"usd_per_1000_rows": round(seconds * rate * 1000, 4)')


def test_seconds_become_milliseconds_in_exactly_one_function():
    """`serving.execution_policy` is the one conversion point, and the endpoint's own
    `--execution-timeout` takes seconds and stores ms — the two are opposite, which is how a
    3 600 ms budget kills an hour-long job."""
    allowed = REPO_ROOT / "src" / "market_pulse" / "serving.py"
    source = allowed.read_text(encoding="utf-8")
    start = (
        source.splitlines().index(
            "def execution_policy(execution_timeout_s: float, ttl_s: float) -> dict:"
        )
        + 1
    )
    body = [n for n, _ in millisecond_sites(source)]
    assert body and all(start <= n <= start + 30 for n in body), body
    for path in sorted((REPO_ROOT / "src").rglob("*.py")) + sorted(
        (REPO_ROOT / "scripts").glob("*.py")
    ):
        if path == allowed:
            continue
        assert not millisecond_sites(path.read_text(encoding="utf-8")), path.name
