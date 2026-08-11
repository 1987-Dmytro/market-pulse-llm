"""Local GPU inference: the same zero-shot evaluation, on weights we rent.

`zero_shot.py` talks to OpenRouter; this module talks to a model in this
process. Everything that decides a number is deliberately NOT here — the
prompts, the parser, the failure taxonomy, the record builder and the scorer
are 3b's, reused unchanged. The run exists to cross-check a third-party
serving stack (`knowledge/decisions/3b-infra-and-precision.md` §(d), SPEC
amendment 3.4), and a cross-check that changed the measurement measures
nothing.

What lives here is the part that genuinely differs: the NF4 quantization Phase
4 also trains and serves in, greedy batched generation, and the environment
provenance a number produced on rented hardware needs to be reproducible at
all.

torch, transformers and bitsandbytes live in the `gpu` extra and are imported
inside functions, never at module scope — no test may import them, so
`make check` stays green on a bare checkout (the rule the `baseline` and `xlmr`
extras already follow).
"""

import os
import subprocess
from collections import Counter

from market_pulse import prompts

MODEL_ID = "google/gemma-4-31b-it"
"""The base model, locked by SPEC amendment 3.4 (1) / [[phase4-base-model-gate]].

Hugging Face spells the repo `google/gemma-4-31B-it`; the lowercase form is the
OpenRouter slug the 3b rows carry and resolves to the same repo. The record key
stays the lowercase one so the own-pod row lands beside its OpenRouter row.
"""

MAX_NEW_TOKENS = 256
"""3b's ``max_tokens``. Same budget, so a truncation means the same thing."""

SEED = 42
DEFAULT_BATCH_SIZE = 8
"""Fits an A6000 at NF4 with room for the KV cache; the runbook proves batch
invariance on the pod before the full run rather than assuming it."""

QUANTIZATION = {
    "load_in_4bit": True,
    "bnb_4bit_quant_type": "nf4",
    "bnb_4bit_use_double_quant": True,
    "bnb_4bit_compute_dtype": "bfloat16",
}
"""The 4-bit base, as a dict rather than a bitsandbytes object.

This is the single source of truth: it is what the result record stores, what
step 4b trains its LoRA adapters against, and what production serves. The
loader builds its config *from* this dict so the three cannot drift apart —
"train in the precision you serve" is only true if one value spells all three.
"""

CHAT_TEMPLATE = {"add_generation_prompt": True, "enable_thinking": False}
"""Gemma 4 has a thinking channel, and `enable_thinking` defaults to false in
the shipped template — which then emits `<|channel>thought\\n<channel|>`, an
already-closed thought, so the model answers directly. That is the local
equivalent of the `reasoning: {"enabled": False}` every 3b request carried.
Passed explicitly rather than left to the default: a template revision that
flipped it would silently turn every reply into reasoning followed by JSON, and
`parse_reply` reads the first brace it finds.
"""


def quantization_config():
    """:data:`QUANTIZATION` in the form bitsandbytes wants it."""
    import torch
    from transformers import BitsAndBytesConfig

    kwargs = dict(QUANTIZATION)
    kwargs["bnb_4bit_compute_dtype"] = getattr(torch, kwargs["bnb_4bit_compute_dtype"])
    return BitsAndBytesConfig(**kwargs)


def load(
    model_id: str = MODEL_ID,
    revision: str | None = None,
    seed: int = SEED,
    prequantized: bool = False,
):
    """Tokenizer + NF4-quantized model, ready to generate.

    Gemma 4 is a `Gemma4ForConditionalGeneration`, so the auto-class is the
    image-text-to-text one; the causal-LM fallback exists because a load that
    fails after a 62 GB download costs a pod session, not a stack trace.

    ``prequantized`` is Phase 5b's config B: a checkpoint that was merged in
    bf16 and then written back out **already** in NF4 carries its own
    ``quantization_config`` in ``config.json``, and passing a second one is how
    a run silently double-quantizes or refuses after the weights have loaded.
    The dict in :data:`QUANTIZATION` is still the single source of truth — the
    merge script writes the checkpoint *from* it, and 5b's endpoint asserts the
    served config against it before the first scored row.
    """
    import torch
    import transformers

    torch.manual_seed(seed)  # greedy decoding, so this is recorded, not load-bearing
    tokenizer = transformers.AutoTokenizer.from_pretrained(model_id, revision=revision)
    tokenizer.padding_side = "left"  # decoder-only: right padding decodes garbage
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    errors = []
    for name in ("AutoModelForImageTextToText", "AutoModelForCausalLM"):
        factory = getattr(transformers, name, None)
        if factory is None:
            continue
        try:
            model = factory.from_pretrained(
                model_id,
                revision=revision,
                device_map="auto",
                **({} if prequantized else {"quantization_config": quantization_config()}),
            )
        except (ValueError, KeyError) as err:  # architecture not in this auto-class
            errors.append(f"{name}: {type(err).__name__}: {err}")
            continue
        model.eval()
        return tokenizer, model
    raise RuntimeError(f"{model_id}: no transformers auto-class loaded it — {' | '.join(errors)}")


CAPTION_MAX_NEW_TOKENS = 400
"""The caption budget, and deliberately not :data:`MAX_NEW_TOKENS`.

4.5g2 measured it on the API instrument (`caption_posts.MAX_TOKENS`): "a six-image leaflet
transcribed item by item runs past 600 tokens and never reaches its summary sentence". 256 is
3b's budget for a JSON object of four fields, and a caption cut off before its closing sentence
is not a shorter caption — it is a description of half a leaflet, silently, since free text has
no parse failure to count. The two instruments get the same budget so that the 3.13 (4) bridge
compares models rather than ceilings.
"""


def image_from_data_url(url: str):
    """One ``data:`` URL from a caption job, as a PIL image.

    The driver runs on the Mac and the pictures are gitignored, so they cannot ride on the
    network volume with the weights: they travel inside the job, base64, exactly as
    `caption_posts.data_url` already encodes them for the API instrument. Pillow arrives with
    the vision half of transformers and is imported here rather than at module scope, like
    every other GPU-extra dependency in this file.
    """
    import base64
    import io

    from PIL import Image

    if not url.startswith("data:"):
        raise ValueError(f"a caption image must be a data: URL, got {url[:32]!r}")
    payload = url.split(",", 1)[1] if "," in url else ""
    if not payload:
        raise ValueError("a data: URL with no payload carries no picture")
    return Image.open(io.BytesIO(base64.b64decode(payload))).convert("RGB")


def load_captioner(model_id: str = MODEL_ID, revision: str | None = None, seed: int = SEED):
    """Processor + NF4 image-text model — the caption instrument of SPEC amendment 3.13 (3).

    Two differences from :func:`load`, both deliberate:

    - an ``AutoProcessor``, not an ``AutoTokenizer``. The processor is what turns pixels into
      the model's image tokens; a tokenizer would render the chat template and silently drop
      every picture, and a caption written without looking at the image is the one failure
      nothing downstream can see.
    - **no causal-LM fallback.** :func:`load` falls back because a load that fails after a
      62 GB download costs a pod session. Here the fallback would be the failure: a text-only
      auto-class that accepts these weights would generate captions from the prompt alone.

    The adapter is not loaded and is not loadable here — see `serve_handler.assert_no_adapter`,
    which is what refuses if one ever arrives.
    """
    import torch
    import transformers

    torch.manual_seed(seed)  # greedy decoding, so this is recorded, not load-bearing
    processor = transformers.AutoProcessor.from_pretrained(model_id, revision=revision)
    model = transformers.AutoModelForImageTextToText.from_pretrained(
        model_id,
        revision=revision,
        device_map="auto",
        quantization_config=quantization_config(),
    )
    model.eval()
    return processor, model


class CaptionClient:
    """One post's album per call, greedy, forward batch 1 — never more.

    The reply dict is `LocalClient`'s, key for key, so the worker's job envelope and every
    record downstream cannot tell a caption reply from a labelling one. ``cost`` is 0.0 for the
    same reason: serverless bills the worker's uptime, and the driver's own spend anchor is
    what counts the dollars.

    Batch 1 is not a default here, it is the instrument (SPEC amendment 3.13 (3)). It is also
    what makes the padding question moot: nothing is padded, so the left-padding trap
    `LocalClient._assert_left_padding` exists for cannot arise.
    """

    def __init__(self, processor, model, *, max_new_tokens: int = CAPTION_MAX_NEW_TOKENS):
        self.processor, self.model = processor, model
        self.max_new_tokens = max_new_tokens
        self.usage = Counter()
        self._assert_template_emits_bos()

    def _assert_template_emits_bos(self) -> None:
        """`add_special_tokens=False` is only safe while the template emits <bos>.

        `LocalClient` checks this against the tokenizer; the processor wraps one, and the
        chat template it renders is the same file. A processor that does not expose a
        tokenizer is not a reason to refuse — it is a reason to say nothing, since the flag
        then has nothing to drop.
        """
        tokenizer = getattr(self.processor, "tokenizer", None)
        bos = getattr(tokenizer, "bos_token", None)
        if not bos:
            return
        if not self.render(prompts.CAPTION_TASK_GM4, 1).startswith(bos):
            raise RuntimeError(
                f"the chat template no longer starts the caption prompt with {bos!r}, so"
                " add_special_tokens=False would drop it silently — stop and report"
            )

    def render(self, task: str, images: int) -> str:
        """The caption request through the processor's own chat template.

        ``task`` is checked rather than used: the job names the registered prompt it wants and
        this worker serves exactly one. A job asking for `caption_post` would be asking for the
        4.5g2 API text, which is a different sha and therefore a different measurement.
        """
        if task != prompts.CAPTION_TASK_GM4:
            raise ValueError(
                f"{task}: the CAPTION config serves {prompts.CAPTION_TASK_GM4} and nothing else"
                " — a caption under another registered prompt is another instrument"
            )
        return self.processor.apply_chat_template(
            prompts.caption_messages_gm4(images), tokenize=False, **CHAT_TEMPLATE
        )

    def caption(self, task: str, albums: list[list[str]]) -> list[dict]:
        """One reply dict per album, in order. Each album is one post's images as data URLs.

        Positional and never zipped short, the way `LocalClient.batch` is: a reply list that
        did not match its albums would attach every caption after the gap to the wrong post,
        and a caption file is read by `(channel, msg_id)` — nothing downstream could see it.
        """
        replies = []
        for album in albums:
            images = [image_from_data_url(url) for url in album]
            text = self.render(task, len(images))
            encoded = self.processor(
                text=text,
                images=images,
                return_tensors="pt",
                add_special_tokens=False,  # the chat template already emits <bos>
            ).to(self.model.device)
            generated = self.model.generate(
                **encoded,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,  # temperature 0 / greedy, as everywhere in this repo
            )
            width = encoded["input_ids"].shape[1]
            new = generated[0].tolist()[width:]
            prompt_tokens = int(encoded["input_ids"].shape[1])
            self.usage["prompt_tokens"] += prompt_tokens
            self.usage["completion_tokens"] += len(new)
            replies.append(
                {
                    "content": self.processor.decode(new, skip_special_tokens=True),
                    # At batch 1 nothing is padded, so a reply that used its whole budget is
                    # the truncation `LocalClient._trim` reads off the stop token. Free text
                    # has no parse failure to count, so this field is the only signal that a
                    # caption stopped mid-leaflet.
                    "finish_reason": "length" if len(new) >= self.max_new_tokens else "stop",
                    "cost": 0.0,
                    # completion_tokens counts the end-of-turn token, which `skip_special_tokens`
                    # keeps out of `content`. A token of slack in a counter nothing is billed on.
                    "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": len(new)},
                    "generation_id": None,
                }
            )
        return replies


class LocalClient:
    """One padded batch per call, greedy, in the reply shape ``classify`` expects.

    The dict it returns is the OpenRouter client's dict, key for key, so the
    parser and the failure taxonomy cannot tell the two backends apart. ``cost``
    is 0.0 because GPU time is billed by the hour and not by the row — the pod
    ledger is where 4a's money is counted.

    ``finish_reason`` is synthesised, and that matters: ``failure_block``
    separates a truncated reply from a badly formatted one off that field, and
    a local backend that never says "length" would silently retire the one
    counter that says ``max_new_tokens`` is too small.
    """

    def __init__(self, tokenizer, model, *, max_new_tokens: int = MAX_NEW_TOKENS, seed: int = SEED):
        self.tokenizer, self.model = tokenizer, model
        self.max_new_tokens, self.seed = max_new_tokens, seed
        self.usage = Counter()
        stop = getattr(getattr(model, "generation_config", None), "eos_token_id", None)
        stop = stop if stop is not None else tokenizer.eos_token_id
        self.stop_ids = set(stop) if isinstance(stop, list | tuple | set) else {stop}
        if tokenizer.pad_token_id is not None:
            # generate() pads rows that stopped early; a pad is an end for us too.
            self.stop_ids.add(tokenizer.pad_token_id)
        self._assert_left_padding()
        self._assert_template_emits_bos()

    def _assert_left_padding(self) -> None:
        """The one thing batching can get wrong that no number downstream can see.

        :func:`load` sets it, but the client is what depends on it: with right padding a
        batch's shorter rows end in pads, ``generate`` continues from a pad instead of from
        the prompt, and ``row[width:]`` slices at the longest row's width — so every row but
        the longest decodes garbage. At batch 1 nothing is padded and the bug does not exist,
        which is precisely why it would first appear in a paid batched run (SPEC amendment
        3.11 (2), the batch measurement).
        """
        side = getattr(self.tokenizer, "padding_side", None)
        if side != "left":
            raise RuntimeError(
                f"the tokenizer pads on the {side!r} side; decoder-only generation needs 'left'."
                " Right padding is invisible at batch 1 and wrong for every shorter row above it."
            )

    def _assert_template_emits_bos(self) -> None:
        """`add_special_tokens=False` is only safe while the template emits <bos>.

        Checked once, at construction, because nothing downstream can see it: a
        missing BOS produces slightly worse answers, not an error, and the run
        would read as a model disagreeing with its OpenRouter row. Verified
        against the shipped Gemma 4 template before the first pod existed; this
        keeps it true if the template is ever revised under us.
        """
        bos = getattr(self.tokenizer, "bos_token", None)
        if not bos:
            return  # a tokenizer with no BOS has nothing for the flag to drop
        rendered = self.render(prompts.TASKS[0], "probe")
        if not rendered.startswith(bos):
            raise RuntimeError(
                f"the chat template no longer starts the prompt with {bos!r}, so"
                " add_special_tokens=False would drop it silently — stop and report"
            )

    def render(self, task: str, text: str, post: dict | None = None) -> str:
        """The one request, through the model's own chat template.

        ``post`` is :func:`parents.post_kwargs`' answer for this row, and it is required
        by exactly the tasks in :data:`prompts.WITH_POST` — ``build_messages`` refuses
        the mismatch either way, so a caller cannot half-apply the with-post rendering.
        """
        return self.tokenizer.apply_chat_template(
            prompts.build_messages(task, text, **(post or {})), tokenize=False, **CHAT_TEMPLATE
        )

    def _trim(self, tokens: list[int]) -> tuple[list[int], bool]:
        """Tokens before the first end-of-turn, and whether one was emitted.

        A row that emitted none ran out of ``max_new_tokens`` — the local
        reading of OpenRouter's ``finish_reason == "length"``.
        """
        for position, token in enumerate(tokens):
            if token in self.stop_ids:
                return tokens[:position], True
        return tokens, False

    def batch(self, task: str, texts: list[str], posts: list[dict] | None = None) -> list[dict]:
        """Generate for a batch of rows; one reply dict per text, in order.

        ``posts`` is one :func:`parents.post_kwargs` per text, or ``None`` for a task that
        takes no parent post. Positional and length-checked rather than zipped short: a
        silently truncated list would ask the tail of the batch without the context the
        head was asked with, and nothing downstream could see it.
        """
        if posts is not None and len(posts) != len(texts):
            raise ValueError(f"{len(posts)} parent posts for {len(texts)} rows")
        encoded = self.tokenizer(
            [
                self.render(task, text, post)
                for text, post in zip(texts, posts or [None] * len(texts))
            ],
            return_tensors="pt",
            padding=True,
            add_special_tokens=False,  # the chat template already emits <bos>
        ).to(self.model.device)
        generated = self.model.generate(
            **encoded,
            max_new_tokens=self.max_new_tokens,
            do_sample=False,  # temperature 0 / greedy (SPEC amendment 3.4 (2))
            pad_token_id=self.tokenizer.pad_token_id,
        )
        width = len(encoded["input_ids"][0])
        replies = []
        for index, row in enumerate(generated.tolist()):
            new, stopped = self._trim(row[width:])
            prompt_tokens = int(sum(encoded["attention_mask"][index]))
            self.usage["prompt_tokens"] += prompt_tokens
            self.usage["completion_tokens"] += len(new)
            replies.append(
                {
                    "content": self.tokenizer.decode(new, skip_special_tokens=True),
                    "finish_reason": "stop" if stopped else "length",
                    "cost": 0.0,
                    "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": len(new)},
                    "generation_id": None,
                }
            )
        return replies


POSITIONS_MAX_NEW_TOKENS = 800
"""SPEC 3.17 (9), transcribed and not chosen here: a CEILING against mid-JSON truncation.

Not a target length, and that is the whole reason it is not :data:`CAPTION_MAX_NEW_TOKENS`. A
caption cut off at 400 tokens is a description of half a leaflet and only ``finish_reason`` can see
it; a position array cut off mid-object is a **parse failure**, which the strict parser counts by
reason and excludes from bar 3's denominator (`results/sku_pilot_prereg_v2.json ::
bars.text_tier_accuracy.unreadable_rows`). One dense leaflet page can name a dozen SKUs at ~40
tokens of JSON each, so the ceiling has to sit above the longest honest answer or the instrument
fails on exactly the pages that carry the most.
"""


class PositionsClient:
    """One page or one row per call, greedy, forward batch 1 — the instruments of SPEC 3.17 (5).

    Built on the processor and not the tokenizer, because one of the two legs carries an image:
    `positions_post_gm4` is a page (SPEC 3.17 (4): one image, one call) and `positions_text_gm4`
    is a row of text with no image at all. A tokenizer would render the page request's template
    and silently drop the picture, which is the one failure nothing downstream can see — the reply
    would still be a legal JSON array, of whatever the instructions alone suggest.

    The reply dict is `LocalClient`'s, key for key, so the worker's job envelope and every record
    downstream cannot tell a positions reply from a caption or a labelling one.
    """

    def __init__(self, processor, model, *, max_new_tokens: int = POSITIONS_MAX_NEW_TOKENS):
        self.processor, self.model = processor, model
        self.max_new_tokens = max_new_tokens
        self.usage = Counter()
        self._assert_template_emits_bos()

    def _assert_template_emits_bos(self) -> None:
        """`add_special_tokens=False` is only safe while the template emits <bos>. `CaptionClient`'s
        check, on the text leg — it needs no picture and renders through the same template file."""
        tokenizer = getattr(self.processor, "tokenizer", None)
        bos = getattr(tokenizer, "bos_token", None)
        if not bos:
            return
        if not self.render(prompts.POSITIONS_TASK_TEXT, "проба").startswith(bos):
            raise RuntimeError(
                f"the chat template no longer starts the positions prompt with {bos!r}, so"
                " add_special_tokens=False would drop it silently — stop and report"
            )

    def render(self, task: str, item) -> str:
        """The request for one page or one row, through the processor's own chat template.

        ``task`` is checked and not used as a switch label: this worker serves exactly the two
        prompts SPEC 3.17 (5) registered, and their shas are pinned in
        `results/sku_pilot_prereg_v2.json :: instruments`. A job asking for anything else — a
        revised text, a caption prompt — is another instrument and is refused rather than served.
        """
        if task == prompts.POSITIONS_TASK_PAGE:
            # `positions_messages_page_gm4` is what refuses a second image: the one-page ruling
            # answers caption sampling, the token ceiling and the 10 MB transport at once.
            images = len(item) if isinstance(item, list) else 1
            messages = prompts.positions_messages_page_gm4(images)
        elif task == prompts.POSITIONS_TASK_TEXT:
            messages = prompts.positions_messages_text_gm4(item)
        else:
            raise ValueError(
                f"{task}: the POSITIONS config serves {sorted(prompts.POSITIONS)} and nothing"
                " else — an extraction under another registered prompt is another instrument"
            )
        return self.processor.apply_chat_template(messages, tokenize=False, **CHAT_TEMPLATE)

    def positions(self, task: str, items: list) -> list[dict]:
        """One reply dict per item, in order. A page item is a one-image album, a text item a row.

        Positional and never zipped short, the way `CaptionClient.caption` is: the per-position
        dump the price-pair bar is read from cites a page by its file and sha, so a reply list off
        by one would attribute every extraction after the gap to the wrong image.
        """
        replies = []
        for item in items:
            images = (
                [image_from_data_url(url) for url in item]
                if task == prompts.POSITIONS_TASK_PAGE
                else []
            )
            text = self.render(task, item)
            encoded = self.processor(
                text=text,
                # the text leg passes no `images` at all rather than an empty list: a processor
                # asked to align zero pictures against a template with no image token is a
                # different call, and this way the two legs differ only where they must.
                **({"images": images} if images else {}),
                return_tensors="pt",
                add_special_tokens=False,  # the chat template already emits <bos>
            ).to(self.model.device)
            generated = self.model.generate(
                **encoded,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,  # temperature 0 / greedy, as everywhere in this repo
            )
            width = encoded["input_ids"].shape[1]
            new = generated[0].tolist()[width:]
            prompt_tokens = int(width)
            self.usage["prompt_tokens"] += prompt_tokens
            self.usage["completion_tokens"] += len(new)
            replies.append(
                {
                    "content": self.processor.decode(new, skip_special_tokens=True),
                    # At batch 1 nothing is padded, so a reply that used its whole budget ran out
                    # of ceiling. Here that is not a shorter answer but an unparseable one, and
                    # the driver counts it by reason rather than reading it as an empty page.
                    "finish_reason": "length" if len(new) >= self.max_new_tokens else "stop",
                    "cost": 0.0,
                    "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": len(new)},
                    "generation_id": None,
                }
            )
        return replies


def nvidia_smi() -> dict:
    """Driver and card as the driver itself reports them, or ``{}`` off-GPU."""
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=driver_version,name,memory.total", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return {}
    fields = [field.strip() for field in out.splitlines()[0].split(",")]
    return dict(zip(("driver_version", "name", "memory_total"), fields))


def environment(model=None, weights: str = MODEL_ID, revision: str | None = None) -> dict:
    """Which machine, which driver, which wheels, which weights — provenance.

    A GPU number that does not name its stack cannot be re-run: bitsandbytes
    kernels and the transformers generation path both move between releases,
    and step 4b trains against exactly this environment.

    ``weights`` and ``revision`` are what the operator asked for and are
    recorded as asked, beside ``model_revision``, which is what transformers
    resolved. The resolved one is a best-effort read of a private attribute and
    is ``None`` for a local-directory load — so it can corroborate the request,
    never replace it.
    """
    import bitsandbytes
    import torch
    import transformers

    smi = nvidia_smi()
    return {
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else smi.get("name"),
        "gpu_count": torch.cuda.device_count(),
        "gpu_memory_total": smi.get("memory_total"),
        "driver": smi.get("driver_version"),
        "cuda_runtime": torch.version.cuda,
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "bitsandbytes": bitsandbytes.__version__,
        "pod_id": os.environ.get("RUNPOD_POD_ID"),
        "weights_requested": weights,
        "revision_requested": revision,
        "model_revision": getattr(getattr(model, "config", None), "_commit_hash", None),
    }
