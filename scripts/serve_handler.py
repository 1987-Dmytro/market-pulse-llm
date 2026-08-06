#!/usr/bin/env python3
"""The RunPod serverless worker: this repo's own generation path, behind an HTTP job (5b).

The parity measurement of SPEC amendment 3.11 (2) is only a measurement if the production
runtime differs from the 4.5h2 pod in *one* way — where the process runs. So the worker
imports `market_pulse.local_llm` and answers through `LocalClient`: the same chat template,
the same `add_special_tokens=False`, the same greedy `generate`, the same trim-at-first-stop
and the same reply dict. Nothing is re-implemented here, and a serving stack with a
different generation library (vLLM, TGI) was rejected for exactly that reason — it would
confound the runtime delta with a library delta in the one paid run the phase gets.

Two ops, and the first one is a guard rather than a convenience:

``info``
    what this worker actually loaded — the served config, the adapter or merged-artifact
    sha, the quantization dict, the weights and the environment. `serving.assert_serving`
    refuses the run before the first paid row if any of it is not what 5b registered.
``batch``
    ``(task, texts, posts)`` → one reply dict per text, in order.

Configuration is environment, because a serverless worker has no argv:

    SERVING_CONFIG   A (NF4 base + unmerged adapter) or B (merged, requantized to NF4)
    ADAPTER_DIR      config A: the arm-A adapter directory
    BASE_WEIGHTS     config A: the base checkpoint, defaulting to the Hugging Face repo id
    MERGED_DIR       config B: the merged+requantized checkpoint directory
    MODEL_REVISION   config A: the base weights revision to pin

The model loads once per cold start, at the first job — not at import, so that `info` on a
misconfigured worker reports the refusal instead of the container dying before it can.
"""

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed

from market_pulse import local_llm, records  # noqa: E402

CONFIGS = ("A", "B")


def settings(env: dict) -> dict:
    """The worker's configuration, or a ValueError naming what is missing.

    Read once and reported in ``info``, so that "which config is this endpoint"
    is answered by the worker's own environment rather than by the endpoint name
    someone typed — an endpoint is updatable, and a name is not a checksum.
    """
    config = (env.get("SERVING_CONFIG") or "").strip().upper()
    if config not in CONFIGS:
        raise ValueError(f"SERVING_CONFIG must be one of {CONFIGS}, got {config!r}")
    needed = "ADAPTER_DIR" if config == "A" else "MERGED_DIR"
    path = (env.get(needed) or "").strip()
    if not path:
        raise ValueError(f"config {config} needs {needed} and it is unset")
    merged = config == "B"
    return {
        "serving_config": config,
        # A serves the base checkpoint and loads the adapter onto it; B serves the merged
        # checkpoint and has no adapter at all. Keeping both fields, one of them None, is
        # what lets `describe` answer the same questions about either config.
        "weights_dir": path if merged else (env.get("BASE_WEIGHTS") or local_llm.MODEL_ID),
        "adapter_dir": None if merged else path,
        "revision": (env.get("MODEL_REVISION") or "").strip() or None,
    }


def describe(config: dict, runtime: dict, artifact_sha: str, merged_provenance: dict) -> dict:
    """What ``info`` answers — every field `serving.assert_serving` can be asked to check.

    ``adapter_sha256`` means the same thing in both configs and that is the point:
    for A it is the unmerged adapter this worker loaded, for B it is the adapter
    the merge consumed, copied out of the merged artifact's own provenance. A
    field that changed meaning between the two configs could not compare them.
    """
    merged = config["serving_config"] == "B"
    return {
        "serving_config": config["serving_config"],
        "merge_state": "merged-requantized" if merged else "unmerged-adapter",
        "adapter_sha256": merged_provenance.get("adapter_sha256") if merged else artifact_sha,
        "merged_sha256": artifact_sha if merged else None,
        "quantization": local_llm.QUANTIZATION,
        "chat_template": local_llm.CHAT_TEMPLATE,
        "max_new_tokens": local_llm.MAX_NEW_TOKENS,
        "model": local_llm.MODEL_ID,
        "weights_dir": config["weights_dir"],
        "adapter_dir": config["adapter_dir"],
        "revision_requested": config["revision"],
        "merged_provenance": merged_provenance or None,
        "runtime": runtime,
    }


def handle(job: dict, client, info: dict) -> dict:
    """Dispatch one job against an already-loaded client. Pure — the tests drive it.

    An unknown ``op`` is an error rather than a default: a typo that silently
    returned ``info`` would score zero rows and look like an empty test set.
    """
    payload = job.get("input") or {}
    op = payload.get("op")
    if op == "info":
        return info
    if op == "batch":
        texts = payload.get("texts")
        if not isinstance(texts, list) or not texts:
            raise ValueError(f"batch needs a non-empty list of texts, got {type(texts).__name__}")
        replies = client.batch(payload["task"], texts, payload.get("posts"))
        return {"replies": replies, "n": len(replies)}
    raise ValueError(f"unknown op {op!r} — this worker answers 'info' and 'batch'")


class Worker:
    """Load-once, answer-many. The load is lazy so a bad config reports instead of crashing."""

    def __init__(self, env: dict | None = None, loader=None) -> None:
        self.env = os.environ if env is None else env
        self.loader = loader or self._load
        self.client = None
        self.info = None

    def _load(self, config: dict):  # pragma: no cover — needs the GPU extra and the weights
        weights = config["weights_dir"]
        merged = config["serving_config"] == "B"
        tokenizer, model = local_llm.load(
            weights, revision=None if merged else config["revision"], prequantized=merged
        )
        provenance, walked = {}, Path(weights)
        if merged:
            source = Path(weights) / "merge_provenance.json"
            if not source.exists():
                raise ValueError(
                    f"{source} is missing — a merged artifact that cannot name the adapter it"
                    " consumed is not the pre-registered config B"
                )
            provenance = json.loads(source.read_text(encoding="utf-8"))
        else:
            from peft import PeftModel

            walked = Path(config["adapter_dir"])
            model = PeftModel.from_pretrained(model, str(walked))
            model.eval()
        client = local_llm.LocalClient(tokenizer, model)
        runtime = local_llm.environment(model, weights=weights, revision=config["revision"])
        return client, describe(config, runtime, records.artifact_sha256(walked), provenance)

    def __call__(self, job: dict) -> dict:
        if self.client is None:
            config = settings(self.env)
            self.client, self.info = self.loader(config)
        return handle(job, self.client, self.info)


def main() -> int:  # pragma: no cover — the RunPod entrypoint, exercised on the worker
    import runpod

    runpod.serverless.start({"handler": Worker()})
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
