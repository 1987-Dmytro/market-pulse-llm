#!/usr/bin/env python3
"""Config B's artifact: the arm-A adapter merged in bf16, then requantized to NF4 (5b).

SPEC amendment 3.11 (2) fixes the pair. Config A is the 4.5h2 replica — the NF4 base with
the adapter loaded **unmerged**. Config B is this script's output: the same adapter folded
into bf16 weights and the result written back out in NF4, because bf16 serving does not fit
the GPU class (~62 GB of weights against 48 GB of card). Merging is otherwise forbidden
until this measurement selects it, so this script produces a *candidate* and decides nothing.

Two properties it has to have, and both are refusals rather than hopes:

- **the merge is peft's own.** ``merge_and_unload`` on a bf16 CPU load, not a hand-rolled
  ``B @ A * alpha/r`` — the scaling, ``use_rslora``, ``fan_in_fan_out`` and the target-module
  set all live in ``adapter_config.json``, and a re-implementation that read one of them
  wrong would produce a plausible artifact that is quietly not the adapter. The cost is RAM,
  so the RAM is checked before the weights, not after an hour of them;
- **the requantization is `local_llm.QUANTIZATION`.** The same dict that trained the adapter
  and that config A serves. Two NF4 configurations that differ in double-quant or compute
  dtype are two different models, and the delta would be charged to the merge.

The artifact names what it came from — adapter sha, base revision, every tool version — in
``merge_provenance.json`` **inside** the checkpoint, and the checkpoint's own content hash
goes to a sidecar **outside** it. A hash written into the thing it hashes cannot be checked.

    $PY scripts/merge_requantize.py --adapter /workspace/repo/results/train/45h2-arm-a/adapter \\
        --out /workspace/merged-nf4 --bf16-scratch /scratch/merged-bf16 \\
        --sidecar /workspace/out/merged_5b.json
"""

import argparse
import json
import os
import shutil
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed

from market_pulse import local_llm, records  # noqa: E402

BF16_WEIGHTS_GB = 62
"""What the base occupies unquantized — the number SPEC amendment 3.11 (2) names."""

RAM_HEADROOM = 1.15
"""peft holds the merged tensor and its two factors at once for one module at a time."""


def enough_ram(available_gb: float, weights_gb: float = BF16_WEIGHTS_GB) -> bool:
    """Whether a bf16 CPU merge fits. Pure, so the refusal is testable off-GPU."""
    return available_gb >= weights_gb * RAM_HEADROOM


def available_ram_gb() -> float:
    """Total RAM as the kernel reports it (Linux pods; 0.0 where it cannot be read)."""
    try:
        return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 1024**3
    except (ValueError, OSError, AttributeError):
        return 0.0


def tool_versions() -> dict:
    """Every library whose release can move a merged weight, as it is installed here."""
    import bitsandbytes
    import peft
    import torch
    import transformers

    return {
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "peft": peft.__version__,
        "bitsandbytes": bitsandbytes.__version__,
        "cuda_runtime": torch.version.cuda,
    }


def provenance(adapter: Path, revision: str | None, seconds: float) -> dict:
    """What the merged artifact says about itself, written inside the checkpoint."""
    return {
        "step": "5b config B",
        "built_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "adapter_path": str(adapter),
        "adapter_sha256": records.artifact_sha256(adapter),
        "adapter_config": json.loads((adapter / "adapter_config.json").read_text("utf-8")),
        "base_model": local_llm.MODEL_ID,
        "base_revision": revision,
        "merge": "peft merge_and_unload on a bf16 CPU load",
        "quantization": local_llm.QUANTIZATION,
        "tools": tool_versions(),
        "seconds": round(seconds, 1),
        "note": (
            "SPEC amendment 3.11 (2): merged in bf16 then REQUANTIZED to NF4, because bf16"
            " serving does not fit the GPU class. This artifact is config B of the"
            " pre-registered pair and is adopted only if the selection rule selects it."
        ),
    }


def merge(adapter: Path, scratch: Path, revision: str | None):  # pragma: no cover — GPU extra
    """bf16 base + adapter → a merged bf16 checkpoint on scratch disk."""
    import torch
    import transformers
    from peft import PeftModel

    tokenizer = transformers.AutoTokenizer.from_pretrained(local_llm.MODEL_ID, revision=revision)
    factory = getattr(
        transformers, "AutoModelForImageTextToText", transformers.AutoModelForCausalLM
    )
    model = factory.from_pretrained(
        local_llm.MODEL_ID, revision=revision, dtype=torch.bfloat16, device_map="cpu"
    )
    model = PeftModel.from_pretrained(model, str(adapter))
    model = model.merge_and_unload()
    scratch.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(scratch)
    tokenizer.save_pretrained(scratch)
    del model


def requantize(scratch: Path, out: Path):  # pragma: no cover — GPU extra
    """The merged bf16 checkpoint, written back out in `local_llm.QUANTIZATION`."""
    import transformers

    factory = getattr(
        transformers, "AutoModelForImageTextToText", transformers.AutoModelForCausalLM
    )
    model = factory.from_pretrained(
        scratch, quantization_config=local_llm.quantization_config(), device_map="auto"
    )
    out.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(out)
    transformers.AutoTokenizer.from_pretrained(scratch).save_pretrained(out)
    del model


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True, help="the NF4 checkpoint to serve")
    parser.add_argument("--bf16-scratch", type=Path, required=True, help="deleted after requantize")
    parser.add_argument(
        "--sidecar", type=Path, required=True, help="the hash, outside the artifact"
    )
    parser.add_argument("--revision", default=None, help="pin the base weights, as 4.5h2 did")
    parser.add_argument("--keep-scratch", action="store_true")
    parser.add_argument("--check-only", action="store_true", help="preflight, load nothing")
    args = parser.parse_args(argv)

    if not (args.adapter / "adapter_config.json").exists():
        raise SystemExit(f"{args.adapter} is not a peft adapter directory — stop and report")
    ram = available_ram_gb()
    print(f"adapter        {args.adapter} ({records.artifact_sha256(args.adapter)})")
    print(f"RAM            {ram:.1f} GB, need >= {BF16_WEIGHTS_GB * RAM_HEADROOM:.1f} GB")
    if not enough_ram(ram):
        raise SystemExit(
            f"a bf16 merge of {BF16_WEIGHTS_GB} GB does not fit in {ram:.1f} GB of RAM."
            " Pick a pod with more memory rather than a hand-rolled shard-wise merge: the"
            " scaling, rslora and fan_in_fan_out all live in adapter_config.json and getting"
            " one of them wrong produces a plausible artifact that is not this adapter."
        )
    if args.check_only:
        print("--check-only: the merge fits, nothing was loaded")
        return 0

    started = time.monotonic()
    merge(args.adapter, args.bf16_scratch, args.revision)
    print(f"merged bf16 -> {args.bf16_scratch}  ({time.monotonic() - started:.0f}s)")
    requantize(args.bf16_scratch, args.out)
    print(f"requantized -> {args.out}  ({time.monotonic() - started:.0f}s)")

    record = provenance(args.adapter, args.revision, time.monotonic() - started)
    (args.out / "merge_provenance.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    # After the provenance file lands, so the worker's own walk of the directory reproduces
    # it. The hash lives in the sidecar and never inside the checkpoint it covers.
    digest = records.artifact_sha256(args.out)
    args.sidecar.parent.mkdir(parents=True, exist_ok=True)
    args.sidecar.write_text(
        json.dumps(record | {"merged_sha256": digest, "merged_dir": str(args.out)}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print(f"merged_sha256  {digest}")
    print(f"sidecar        {args.sidecar}")
    if not args.keep_scratch:
        shutil.rmtree(args.bf16_scratch, ignore_errors=True)
        print(f"removed        {args.bf16_scratch}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
