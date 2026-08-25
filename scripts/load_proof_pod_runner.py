#!/usr/bin/env python3
"""The migration's deliverable, on the pod: load the weights from the volume, once, and time it.

`docs/PROMPT-lora-c-migrate-r2.md` §4 — «model loaded to GPU once through the shipped loader at the
pinned revision, seconds and VRAM printed and recorded». A volume nobody loaded from is a hope.

**The shipped loader is CALLED.** `market_pulse.local_llm.load` is the function
`scripts/eval_zero_shot.py --backend local` calls, quantization config and auto-class fallback
included. A proof that used its own `from_pretrained` would show that a volume can feed
transformers, not that it can feed THIS stack
([[a_frozen_record_is_an_input_to_shipped_code]]).

**The volume is measured either side of the load.** A load that quietly re-fetched a missing shard
is a load from the internet with a volume attached, and it reads exactly like a successful one.
`du -sb $HF_HOME` before and after is what makes «it loaded FROM the volume» a reading, and the
snapshot directory that exists for the pinned revision is what ties those bytes to the pin
([[the_identity_field_stops_covering_the_change]]).

Nothing is generated: no prompt, no reply, no adapter, no scored row.

    HF_HOME=/workspace/hf PYTHONPATH=/workspace/repo/src \\
    /workspace/venv/bin/python -u /workspace/repo/scripts/load_proof_pod_runner.py \\
        --revision 842da3794eaa0b77d5f08bae87a17459d91ff475 \\
        --out /workspace/run/load_proof.json
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))


def du_bytes(path: str, run=subprocess.run) -> int | None:
    """`du -sb <path>`, or None when the path is not there. Bytes, never a human-readable string."""
    done = run(["du", "-sb", path], capture_output=True, text=True)
    if done.returncode != 0:
        return None
    return int(done.stdout.split()[0])


def snapshot_dir(hf_home: str, model_id: str, revision: str) -> str | None:
    """The cache directory the pinned revision actually occupies, if it is on disk."""
    slug = "models--" + model_id.replace("/", "--")
    path = Path(hf_home) / "hub" / slug / "snapshots" / revision
    return str(path) if path.exists() else None


def main(argv: list[str] | None = None, loader=None, du=du_bytes) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="google/gemma-4-31b-it")
    parser.add_argument("--revision", required=True, help="the pinned sha, never a branch name")
    parser.add_argument("--hf-home", default=os.environ.get("HF_HOME", ""))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)

    if not args.hf_home:
        raise SystemExit("HF_HOME is unset and --hf-home was not given — the cache has no home")

    before = du(args.hf_home)
    if before is None:
        raise SystemExit(
            f"{args.hf_home} does not exist. The weights are not on this volume and this contract"
            " does not price a download here — STOP."
        )

    if loader is None:
        from market_pulse import local_llm

        loader = local_llm.load

    began = time.monotonic()
    tokenizer, model = loader(args.model, args.revision)
    took = time.monotonic() - began
    after = du(args.hf_home)

    record = {
        "model_id": args.model,
        "revision": args.revision,
        "hf_home": args.hf_home,
        "snapshot_dir": snapshot_dir(args.hf_home, args.model, args.revision),
        "hf_bytes_before": before,
        "hf_bytes_after": after,
        "load_seconds": round(took, 3),
        "loaded": model is not None and tokenizer is not None,
        "generated_nothing": "no prompt was rendered, no token was produced, no adapter was loaded",
    }

    # built whole and merged whole: a card reading that fails half way through leaves fields from
    # the half that worked, and `vram_allocated 0.000` beside `gpu None` reads like a measurement
    # ([[an_empty_field_hides_several_states]])
    try:
        import torch

        card = {
            "gpu": torch.cuda.get_device_name(0),
            "vram_bytes_allocated": int(torch.cuda.memory_allocated()),
            "vram_bytes_reserved": int(torch.cuda.memory_reserved()),
            "vram_bytes_peak": int(torch.cuda.max_memory_allocated()),
            "vram_bytes_total": int(torch.cuda.get_device_properties(0).total_memory),
        }
    except Exception as err:  # a proof that cannot read the card still records the seconds
        card = {"gpu": None, "vram_read_failed": f"{type(err).__name__}: {err}"}
    record.update(card)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    gb = 1024**3
    print(f"load_seconds        {record['load_seconds']}")
    print(f"gpu                 {record.get('gpu')}")
    if record.get("vram_bytes_allocated") is not None:
        print(f"vram_allocated_gb   {record['vram_bytes_allocated'] / gb:.3f}")
        print(f"vram_reserved_gb    {record['vram_bytes_reserved'] / gb:.3f}")
        print(f"vram_total_gb       {record['vram_bytes_total'] / gb:.3f}")
    print(f"hf_bytes_before     {record['hf_bytes_before']}")
    print(f"hf_bytes_after      {record['hf_bytes_after']}")
    print(f"volume_unmoved      {record['hf_bytes_before'] == record['hf_bytes_after']}")
    print(f"snapshot_dir        {record['snapshot_dir']}")
    print(f"wrote               {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
