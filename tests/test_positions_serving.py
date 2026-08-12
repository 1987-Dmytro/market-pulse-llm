"""The POSITIONS serving path: everything about the pilot's instrument that can be wrong for free.

SPEC 3.17 (9) fixes the configuration and sku-b gets ONE paid attempt, so a wrong knob here is not
a bug that gets fixed next run — it is the attempt. What is checked:

* the config is the NF4 base at the pinned revision with the adapter OFF, refusing the two
  environments that would make it a different instrument, exactly as CAPTION does;
* the op router refuses EVERY cell it does not name — the whole 3 x 4 matrix, because the pairwise
  reading it replaced had a silent one;
* the worker names both registered prompts and the max_new_tokens it will really generate;
* the client serves the two registered tasks and refuses any other, one page per call, greedy.

The values are transcription of SPEC 3.17 (9), and one test reads them back out of the amendment
rather than trusting this file to have copied them right.
"""

import importlib.util
import inspect
import re
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from market_pulse import local_llm, prompts, serving

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
spec = importlib.util.spec_from_file_location(
    "serve_handler", REPO_ROOT / "scripts" / "serve_handler.py"
)
handler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(handler)

PINNED_REVISION = "842da3794eaa0b77d5f08bae87a17459d91ff475"
SPEC_PATH = REPO_ROOT / "docs" / "SPEC.md"


def positions_env(**extra) -> dict:
    return {"SERVING_CONFIG": "POSITIONS", "MODEL_REVISION": PINNED_REVISION} | extra


# --- the configuration -------------------------------------------------------


def test_the_positions_config_is_the_base_at_a_pinned_revision_with_no_adapter():
    config = handler.settings(positions_env())
    assert config["serving_config"] == serving.POSITIONS_CONFIG
    assert config["adapter_dir"] is None
    assert config["weights_dir"] == local_llm.MODEL_ID
    assert config["revision"] == PINNED_REVISION


@pytest.mark.parametrize("variable", handler.ADAPTER_ENV)
def test_positions_refuses_every_environment_variable_that_carries_trained_weights(variable):
    """CAPTION's refusal, inherited rather than copied. An endpoint updated from an A template
    keeps A's environment, and a positions worker that quietly loaded the classification adapter
    would extract happily while every record still named the base."""
    with pytest.raises(ValueError, match="ADAPTER OFF"):
        handler.settings(positions_env(**{variable: "/runpod-volume/repo/adapter"}))


def test_positions_refuses_an_unpinned_base():
    with pytest.raises(ValueError, match="MODEL_REVISION"):
        handler.settings({"SERVING_CONFIG": "POSITIONS"})


def test_both_base_only_configs_read_one_refusal_table():
    """The negative control on the two above: if POSITIONS were spelled out in its own branch, a
    guard added to CAPTION later would not reach it. `BASE_ONLY` is what makes them one path, and
    each entry names the amendment that put its config there."""
    assert set(handler.BASE_ONLY) == {serving.CAPTION_CONFIG, serving.POSITIONS_CONFIG}
    assert handler.BASE_ONLY[serving.POSITIONS_CONFIG] == "SPEC amendment 3.17 (9)"
    for config in handler.BASE_ONLY:
        assert serving.MERGE_STATE[config] == "base-no-adapter"


# --- the op router: every cell, not two directions of one pair ----------------


def worker_for(config: str):
    """A worker on ``config`` whose client records what it was asked. The load is stubbed."""
    asked = []

    class Client:
        def batch(self, task, texts, posts=None):
            asked.append(("batch", task, texts))
            return [{"content": "row"} for _ in texts]

        def caption(self, task, albums):
            asked.append(("caption", task, albums))
            return [{"content": "prose"} for _ in albums]

        def positions(self, task, items):
            asked.append(("positions", task, items))
            return [{"content": "[]"} for _ in items]

    env = {
        "A": {"SERVING_CONFIG": "A", "ADAPTER_DIR": "/a", "MODEL_REVISION": PINNED_REVISION},
        "B": {"SERVING_CONFIG": "B", "MERGED_DIR": "/m"},
        serving.CAPTION_CONFIG: {
            "SERVING_CONFIG": "CAPTION",
            "MODEL_REVISION": PINNED_REVISION,
        },
        serving.POSITIONS_CONFIG: positions_env(),
    }[config]
    client = Client()
    worker = handler.Worker(
        env=env,
        loader=lambda cfg: (client, handler.describe(cfg, {}, "artifact-sha", {})),
    )
    return asked, worker


JOB = {
    "batch": {"op": "batch", "task": "T1", "texts": ["a"]},
    "caption": {"op": "caption", "task": prompts.CAPTION_TASK_GM4, "images": [["data:x"]]},
    "positions": {"op": "positions", "task": prompts.POSITIONS_TASK_TEXT, "items": ["a row"]},
}


@pytest.mark.parametrize("config", serving.CONFIGS)
@pytest.mark.parametrize("op", sorted(handler.OP_FIELD))
def test_every_cell_of_the_config_by_op_matrix(config, op):
    """Twelve cells, and only the four `serving.CONFIG_OPS` names may be answered.

    The reading this replaces was `(op == "caption") != (served == CAPTION)`, which is correct for
    two ops and silently permissive for three: a `batch` job on POSITIONS reads False on both
    sides, passes, and is scored on the base at an 800-token ceiling by a record that names
    POSITIONS. A parametrised matrix is the only shape that can see a cell like that.
    """
    asked, worker = worker_for(config)
    if op in serving.CONFIG_OPS[config]:
        worker({"input": JOB[op]})
        assert [entry[0] for entry in asked] == [op]
    else:
        with pytest.raises(ValueError, match="this configuration answers"):
            worker({"input": JOB[op]})
        assert asked == [], "a refused job must never reach the client"


def test_info_is_answered_on_every_config():
    """`info` is deliberately not in the table: it is the guard that reports the others, and a
    config that could not be asked what it loaded could not be refused for being the wrong one."""
    for config in serving.CONFIGS:
        _, worker = worker_for(config)
        assert worker({"input": {"op": "info"}})["serving_config"] == config


def test_an_unknown_op_names_the_ops_that_exist():
    _, worker = worker_for(serving.POSITIONS_CONFIG)
    with pytest.raises(ValueError, match="unknown op"):
        worker({"input": {"op": "extract", "items": ["a"]}})


def test_a_positions_job_with_no_items_is_refused():
    _, worker = worker_for(serving.POSITIONS_CONFIG)
    with pytest.raises(ValueError, match="non-empty list of items"):
        worker({"input": {"op": "positions", "task": prompts.POSITIONS_TASK_TEXT, "items": []}})


def test_the_dump_keys_a_positions_row_by_its_own_input(tmp_path):
    """One join rule for both legs: a page is keyed by its album and a row by its text, so a dump
    recovered without its job can be checked against the manifest rather than trusted to be in
    the order someone remembers sending."""
    import hashlib
    import json

    _, worker = worker_for(serving.POSITIONS_CONFIG)
    dump = tmp_path / "positions.jsonl"
    worker(
        {
            "input": {
                "op": "positions",
                "task": prompts.POSITIONS_TASK_TEXT,
                "items": ["перша строка", "друга строка"],
                "batch_size": 1,
                "dump_path": str(dump),
            }
        }
    )
    rows = [json.loads(line) for line in dump.read_text(encoding="utf-8").splitlines()]
    assert [row["i"] for row in rows] == [0, 1]
    assert rows[0]["sha8"] == hashlib.sha256("перша строка".encode()).hexdigest()[:8]
    # and the page leg hashes the album, through the same function the caption dump uses
    assert serving.positions_key(["data:a", "data:b"]) == serving.album_key(["data:a", "data:b"])


# --- what the worker says it is ----------------------------------------------


def test_the_positions_worker_names_both_registered_prompts():
    """The page leg and the text leg are one instrument in two halves. A worker a session behind
    on one of them would extract happily under the other's text — the volume carries its own
    `repo/`, and a fetch naming a missing ref leaves it on the previous commit."""
    info = handler.describe(handler.settings(positions_env()), {}, None, {})
    assert info["serving_config"] == serving.POSITIONS_CONFIG
    assert info["merge_state"] == "base-no-adapter"
    assert info["adapter_sha256"] is None
    assert info["positions_prompt_sha256"] == {
        "positions_post_gm4": prompts.prompt_sha256("positions_post_gm4"),
        "positions_text_gm4": prompts.prompt_sha256("positions_text_gm4"),
    }
    assert set(info["positions_prompt_sha256"]) == set(prompts.POSITIONS)
    assert "caption_prompt_sha256" not in info


def test_the_prompt_field_is_absent_on_the_other_configs_rather_than_null():
    """`assert_serving` reads a missing field as `<absent>` and refuses, so asking a CAPTION
    endpoint to name a positions prompt is a refusal for free instead of a null that compares
    equal to nothing. Same rule vis-a wrote for `caption_prompt_sha256`."""
    for env in (
        {"SERVING_CONFIG": "A", "ADAPTER_DIR": "/a", "MODEL_REVISION": PINNED_REVISION},
        {"SERVING_CONFIG": "CAPTION", "MODEL_REVISION": PINNED_REVISION},
    ):
        info = handler.describe(handler.settings(env), {}, "sha", {})
        assert "positions_prompt_sha256" not in info


BUILDS = {
    "A": "LocalClient",
    "B": "LocalClient",
    serving.CAPTION_CONFIG: "CaptionClient",
    serving.POSITIONS_CONFIG: "PositionsClient",
}


def test_info_reports_the_token_ceiling_each_config_really_generates():
    """The 256-vs-400 lie, killed. `describe` answered `local_llm.MAX_NEW_TOKENS` for every
    config while `CaptionClient` has generated 400 since vis-a, and nothing broke because no
    caller compares the field — which is why it sat wrong in two paid records.

    Checked against the CLIENT CLASS each config builds rather than against the numbers retyped
    here: a table of three integers agreeing with itself proves nothing about the generate call.
    """
    for config, class_name in BUILDS.items():
        default = (
            inspect.signature(getattr(local_llm, class_name).__init__)
            .parameters["max_new_tokens"]
            .default
        )
        assert handler.MAX_NEW_TOKENS[config] == default, config
    assert set(handler.MAX_NEW_TOKENS) == set(serving.CONFIGS)
    # and the three ceilings really are different instruments, not one constant read three times
    assert handler.MAX_NEW_TOKENS[serving.POSITIONS_CONFIG] > handler.MAX_NEW_TOKENS["A"]


def test_the_loader_builds_the_client_this_table_names():
    """The negative control on the test above: it holds a constant against a class, and the map
    from config to class lives in `Worker._load`. If the loader ever built a `CaptionClient` for
    POSITIONS, every assertion above would still pass and the worker would generate 400."""
    source = inspect.getsource(handler.Worker._load)
    for config, class_name in BUILDS.items():
        assert f"local_llm.{class_name}(" in source, config
    assert "PositionsClient" in source.split("CaptionClient")[1], (
        "the POSITIONS branch is the else of the CAPTION test — if that inverts, both configs"
        " still load and each serves the other's ceiling"
    )


# --- the values are transcription, not design space ---------------------------


def ratification_block(name: str = "sku-b-ratification-3") -> str:
    text = SPEC_PATH.read_text(encoding="utf-8")
    body = text.split(f"<!-- {name} begin", 1)[1]
    return body.split(f"<!-- {name} end", 1)[0]


@pytest.mark.parametrize(
    "phrase",
    ["max_new_tokens 800", "greedy", "batch 1", "NO adapter", "MODEL_REVISION is required"],
)
def test_the_serving_knobs_are_read_back_out_of_the_amendment(phrase):
    """The brief's own words: "(9) is transcription, not design space". This is the check that
    says so — every knob below is quoted from the block that ratified it, so a value edited here
    later has to edit the law with it."""
    assert phrase in ratification_block()


def test_the_ceiling_is_the_number_the_LATEST_amendment_names():
    """(9) fixed it at 800 and (13)(a) moved it to 1200 — both blocks are quoted, because the older
    one is still the authority the sealed v1 pin was written under and the newer one is the
    authority the live constant follows. A test that read only one of them would pass either
    before the amendment landed or after it was reverted."""
    assert local_llm.POSITIONS_MAX_NEW_TOKENS == 1200
    assert re.search(r"max_new_tokens 800", ratification_block())
    assert re.search(r"800 → \*\*1200\*\*", ratification_block("sku-b-ratification-7"))


# --- the client: two registered tasks, one page per call, greedy --------------


class StubIds(list):
    @property
    def shape(self):
        return (len(self), len(self[0]))


class StubEncoded(dict):
    def to(self, device):
        return self


class StubRow(list):
    def tolist(self):
        return list(self)


class StubProcessor:
    """Enough of an `AutoProcessor` to prove the rendering, with no transformers installed.

    Its `apply_chat_template` handles BOTH message shapes on purpose: the page request's content
    is a list of parts with an image slot and the text request's is a plain string. A stub that
    only knew the caption shape would crash on the leg that has no picture.
    """

    def __init__(self, bos: str = "<bos>"):
        self.tokenizer = SimpleNamespace(bos_token=bos)
        self.calls = []
        self.template_kwargs = None

    def apply_chat_template(self, messages, tokenize=False, **kwargs):
        self.template_kwargs = kwargs
        content = messages[0]["content"]
        if isinstance(content, str):
            return f"<bos>{content}"
        slots = sum(1 for part in content if part["type"] == "image")
        return f"<bos>{content[0]['text']}<img>{slots}"

    def __call__(self, text=None, images=None, return_tensors=None, add_special_tokens=None):
        self.calls.append(
            {
                "text": text,
                # None and [] are different findings: the text leg must pass no `images` kwarg
                "images": None if images is None else len(images),
                "add_special_tokens": add_special_tokens,
            }
        )
        return StubEncoded(input_ids=StubIds([[1, 2, 3]]))

    def decode(self, ids, skip_special_tokens=False):
        return "".join(chr(token) for token in ids if token != 0)


class StubModel:
    device = "cpu"

    def __init__(self, answer: str = "[]", pad: int = 0):
        self.answer, self.pad = answer, pad
        self.kwargs = None

    def generate(self, input_ids=None, max_new_tokens=None, do_sample=None, **rest):
        self.kwargs = {"max_new_tokens": max_new_tokens, "do_sample": do_sample}
        return [StubRow([1, 2, 3] + [ord(char) for char in self.answer] + [self.pad])]


def one_pixel_url() -> str:
    import base64
    import io

    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (2, 2), (10, 20, 30)).save(buffer, format="JPEG")
    return "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def test_the_page_leg_sends_exactly_one_image_and_stays_greedy():
    processor, model = StubProcessor(), StubModel("[]")
    client = local_llm.PositionsClient(processor, model)
    replies = client.positions(prompts.POSITIONS_TASK_PAGE, [[one_pixel_url()]])
    assert processor.template_kwargs == local_llm.CHAT_TEMPLATE
    assert processor.calls[-1]["images"] == 1
    assert processor.calls[-1]["add_special_tokens"] is False
    assert model.kwargs == {
        "max_new_tokens": local_llm.POSITIONS_MAX_NEW_TOKENS,
        "do_sample": False,
    }
    assert replies[0]["content"] == "[]" and replies[0]["cost"] == 0.0


def test_the_text_leg_sends_no_image_at_all():
    """Not an empty list: a processor asked to align zero pictures against a template with no
    image token is a different call, and the row would travel through the vision path."""
    processor = StubProcessor()
    client = local_llm.PositionsClient(processor, StubModel())
    client.positions(prompts.POSITIONS_TASK_TEXT, ["Рудь пломбір 450 г 89,90 грн"])
    assert processor.calls[-1]["images"] is None
    assert "Рудь пломбір 450 г 89,90 грн" in processor.calls[-1]["text"]


def test_a_second_page_in_one_call_is_refused():
    """SPEC 3.17 (4): one image, one call. The ruling answers caption sampling, the token
    ceiling and the 10 MB transport at once, and a batched page would undo all three."""
    client = local_llm.PositionsClient(StubProcessor(), StubModel())
    url = one_pixel_url()
    with pytest.raises(ValueError, match="one PAGE per call"):
        client.positions(prompts.POSITIONS_TASK_PAGE, [[url, url]])


def test_the_positions_client_serves_two_registered_prompts_and_nothing_else():
    client = local_llm.PositionsClient(StubProcessor(), StubModel())
    with pytest.raises(ValueError, match="and nothing"):
        client.positions(prompts.CAPTION_TASK_GM4, ["a row"])
    with pytest.raises(ValueError, match="and nothing"):
        client.positions("positions_post_gm4_v2", ["a row"])


def test_a_reply_that_used_its_whole_budget_says_so():
    """A caption cut off at its ceiling is a shorter caption; a position array cut off is a PARSE
    FAILURE, which bar 3 counts by reason and excludes from its denominator. `finish_reason` is
    what tells the driver which of the two it is holding."""
    client = local_llm.PositionsClient(StubProcessor(), StubModel("[{}]"), max_new_tokens=4)
    reply = client.positions(prompts.POSITIONS_TASK_TEXT, ["a row"])[0]
    assert reply["finish_reason"] == "length"


def test_a_template_that_stopped_emitting_bos_is_a_refusal():
    with pytest.raises(RuntimeError, match="no longer starts the positions prompt"):
        local_llm.PositionsClient(StubProcessor(bos="<different>"), StubModel())


def test_an_empty_row_never_reaches_the_model():
    """`positions_messages_text_gm4`'s own refusal, reached through the client: an extraction
    request over an empty row would come back `[]` and score as a row naming no position."""
    client = local_llm.PositionsClient(StubProcessor(), StubModel())
    with pytest.raises(ValueError, match="empty row"):
        client.positions(prompts.POSITIONS_TASK_TEXT, ["   "])
