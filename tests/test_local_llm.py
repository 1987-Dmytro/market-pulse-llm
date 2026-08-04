"""The local GPU backend, with the model call faked.

No test may import torch, transformers or bitsandbytes — they are the `gpu`
extra and `make check` has to stay runnable on a bare checkout. So the fakes
below stand in for a tokenizer and a `generate()`, and one test walks the
module's AST to prove the real imports never escaped into module scope.

The fake tokenizer decodes a token id as `chr(id)`, so a canned reply is just
its own characters and a test reads as the thing it is checking.
"""

import ast
from pathlib import Path

import pytest

from market_pulse import local_llm, prompts

PAD, EOS = 0, 1


class Encoding(dict):
    def to(self, device):
        return self


class FakeTokenizer:
    pad_token_id = PAD
    eos_token_id = EOS
    bos_token = "<bos>"

    def __init__(self, width: int = 4, bos: str = "<bos>") -> None:
        self.width = width
        self.bos = bos
        self.template_kwargs = None
        self.rendered: list[str] = []

    def apply_chat_template(self, messages, tokenize=False, **kwargs) -> str:
        self.template_kwargs = kwargs
        assert tokenize is False
        return f"{self.bos}<|turn>user\n{messages[0]['content']}<turn|><|turn>model\n"

    def __call__(self, texts, return_tensors=None, padding=None, add_special_tokens=None):
        self.rendered = list(texts)
        self.add_special_tokens = add_special_tokens
        return Encoding(
            input_ids=[[ord("p")] * self.width for _ in texts],
            attention_mask=[[1] * self.width for _ in texts],
        )

    def decode(self, tokens, skip_special_tokens=True) -> str:
        return "".join(chr(token) for token in tokens)


class Rows(list):
    def tolist(self):
        return list(self)


class FakeModel:
    """`generate()` over canned (reply, stopped) pairs, padded the way a real one is."""

    device = "cpu"

    class generation_config:  # noqa: N801 — mirrors the transformers attribute
        eos_token_id = [EOS]

    def __init__(self, replies: list[tuple[str, bool]]) -> None:
        self.replies = replies
        self.seen = None

    def generate(self, input_ids=None, attention_mask=None, max_new_tokens=None, **kwargs):
        self.seen = kwargs
        rows = []
        for reply, stopped in self.replies:
            tokens = [ord(char) for char in reply][:max_new_tokens]
            if stopped and len(tokens) < max_new_tokens:
                tokens.append(EOS)
            rows.append(tokens)
        width = max(len(row) for row in rows)
        return Rows(
            list(input_ids[0]) + row + [PAD] * (width - len(row))
            for row in rows  # a row that stopped early is padded; the longest never is
        )


def client(replies, **kwargs) -> local_llm.LocalClient:
    return local_llm.LocalClient(FakeTokenizer(), FakeModel(replies), **kwargs)


GOOD = '{"sentiment": "neutral", "sarcasm": false, "intents": []}'


def test_the_quantization_is_the_one_phase_4_trains_and_serves_in():
    """Amendment 3.4 (1): NF4, double quant, bf16 compute — one dict, three uses."""
    assert local_llm.QUANTIZATION == {
        "load_in_4bit": True,
        "bnb_4bit_quant_type": "nf4",
        "bnb_4bit_use_double_quant": True,
        "bnb_4bit_compute_dtype": "bfloat16",
    }


def test_the_chat_template_closes_the_thinking_channel():
    """Gemma 4 can answer with reasoning first, and `parse_reply` reads the first
    brace it finds. 3b sent `reasoning: {"enabled": False}`; this is that."""
    assert local_llm.CHAT_TEMPLATE["enable_thinking"] is False
    assert local_llm.CHAT_TEMPLATE["add_generation_prompt"] is True


def test_the_request_carries_the_fixed_prompt_and_the_row_it_labels():
    backend = client([(GOOD, True)])
    rendered = backend.render("T1", "молоко скисло")
    assert prompts.T1_PROMPT in rendered, "the prompt is the measurement — it goes through whole"
    assert "<comment>\nмолоко скисло\n</comment>" in rendered
    assert backend.tokenizer.template_kwargs == local_llm.CHAT_TEMPLATE


def test_a_batch_answers_every_row_in_order():
    replies = [
        (f'{{"sentiment": "neutral", "sarcasm": false, "intents": ["{tag}"]}}', True)
        for tag in "ab"
    ]
    backend = client(replies)
    out = backend.batch("T1", ["one", "two"])
    assert [reply["content"] for reply in out] == [text for text, _ in replies]
    assert len(backend.tokenizer.rendered) == 2


def test_the_prompt_is_not_tokenized_twice():
    """The chat template already emits <bos>; a second one shifts every position."""
    backend = client([(GOOD, True)])
    backend.batch("T1", ["one"])
    assert backend.tokenizer.add_special_tokens is False


def test_generation_is_greedy():
    backend = client([(GOOD, True)])
    backend.batch("T1", ["one"])
    assert backend.model.seen["do_sample"] is False


def test_a_reply_that_never_stopped_is_reported_as_truncated():
    """`failure_block` counts "length" apart from a bad format. Without a
    synthesised finish_reason that counter reads zero forever, and the signal
    that max_new_tokens is too small is gone."""
    backend = client([("ok", True), ('{"sentiment": "neu', False)], max_new_tokens=18)
    stopped, running = backend.batch("T1", ["one", "two"])
    assert stopped["finish_reason"] == "stop"
    assert running["finish_reason"] == "length"


def test_padding_after_an_early_stop_is_not_decoded_as_content():
    """Rows that finish early are padded up to the longest row of the batch."""
    backend = client([("ok", True), ("a much longer reply", False)], max_new_tokens=64)
    short, long = backend.batch("T1", ["one", "two"])
    assert short["content"] == "ok"
    assert long["content"] == "a much longer reply"


def test_token_usage_accumulates_across_batches():
    backend = client([(GOOD, True), (GOOD, True)])
    backend.batch("T1", ["one", "two"])
    assert backend.usage["prompt_tokens"] == 8  # two rows, four prompt tokens each
    assert backend.usage["completion_tokens"] == 2 * len(GOOD)


def test_a_template_that_stopped_emitting_bos_refuses_to_run():
    """`add_special_tokens=False` is a silent bug if the template ever changes:
    a missing BOS makes the answers a little worse, never an error, and the run
    would read as the model disagreeing with its OpenRouter row."""
    tokenizer = FakeTokenizer(bos="")
    with pytest.raises(RuntimeError) as caught:
        local_llm.LocalClient(tokenizer, FakeModel([(GOOD, True)]))
    assert "add_special_tokens=False" in str(caught.value)


def test_the_gpu_extra_never_reaches_module_scope():
    """The rule the `baseline` and `xlmr` extras already follow: one top-level
    import of torch here and `make check` stops running on a bare checkout."""
    source = Path(local_llm.__file__).read_text(encoding="utf-8")
    banned = {"torch", "transformers", "bitsandbytes", "accelerate"}
    for node in ast.parse(source).body:
        if isinstance(node, ast.Import):
            assert not banned & {alias.name.split(".")[0] for alias in node.names}
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in banned


# --- the parent post on the eval path (4.5h2) ---------------------------------


def test_a_with_post_request_carries_the_post_the_row_replies_to():
    backend = client([(GOOD, True)])
    rendered = backend.render(
        "T1v2_with_post",
        "смачно",
        {"parent": "Нове морозиво", "caption": None, "caption_kind": "image"},
    )
    assert "<post>\nНове морозиво\n</post>" in rendered
    assert "<comment>\nсмачно\n</comment>" in rendered


def test_a_with_post_batch_gives_each_row_its_own_post():
    """The failure this stops is silent: one post reused for a whole batch reads as a
    labelled run and is a different instrument for every row but the first."""
    backend = client([(GOOD, True), (GOOD, True)])
    backend.batch(
        "T1v2_with_post",
        ["перший", "другий"],
        [
            {"parent": "пост А", "caption": None, "caption_kind": "image"},
            {"parent": "пост Б", "caption": None, "caption_kind": "image"},
        ],
    )
    assert "<post>\nпост А\n</post>" in backend.tokenizer.rendered[0]
    assert "<post>\nпост Б\n</post>" in backend.tokenizer.rendered[1]


def test_a_short_list_of_posts_is_refused_rather_than_zipped():
    backend = client([(GOOD, True), (GOOD, True)])
    with pytest.raises(ValueError, match="1 parent posts for 2 rows"):
        backend.batch("T1v2_with_post", ["перший", "другий"], [{"parent": "пост А"}])
