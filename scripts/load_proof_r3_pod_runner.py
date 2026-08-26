#!/usr/bin/env python3
"""The r3 load proof — the migration's runner, CALLED, with the invariant moved onto the BLOBS.

`scripts/load_proof_pod_runner.py` does the whole job already: it calls the shipped loader, times
it, reads the card and records `du -sb $HF_HOME` either side. It is not edited here — its sha is
pinned by the SEALED `docs/reports/lora-c-migrate-r2.md` through a checker the suite drives as a
command, so an edit would make a closed report stop re-deriving
([[the_gates_evidence_outlived_its_artifact]]).

**What this adds is one reading.** The migration KILLed on a 40-byte move of the whole cache, and the
40 bytes were `refs/main` plus four zero-byte `.no_exist` absence markers — 0 of 12 blobs touched,
62 578 686 256 bytes of weights read and none fetched. A HuggingFace cache is not immutable under a
read. The blobs ARE the weights, and they are what a re-download would write, so the inventory taken
here is `{blob path: size}` either side of the load. The whole-cache count is still recorded, and it
grades nothing ([[an_invariant_on_the_container_not_the_payload]]).

    HF_HOME=/workspace/hf PYTHONPATH=/workspace/repo/src \\
    /workspace/venv/bin/python -u /workspace/repo/scripts/load_proof_r3_pod_runner.py \\
        --revision 842da3794eaa0b77d5f08bae87a17459d91ff475 \\
        --out /workspace/run/load_proof.json
"""

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import load_proof_pod_runner as sibling  # noqa: E402


def blob_inventory(hf_home: str) -> dict[str, int]:
    """Every blob under the cache, by path relative to `hf_home`, with its size in bytes.

    `stat` and not `du`: a `du` total cannot say WHICH file moved, and «which» is the whole reason
    this reading exists. Symlinks are followed to nothing — the snapshot directory is links INTO
    blobs, so counting the links as well would count each weight twice and make a re-download
    invisible inside the noise of its own symlink ([[an_invariant_on_the_container_not_the_payload]]).
    """
    root = Path(hf_home)
    found: dict[str, int] = {}
    for path in sorted(root.glob("hub/*/blobs/*")):
        if path.is_symlink() or not path.is_file():
            continue
        found[str(path.relative_to(root))] = path.stat().st_size
    return found


def main(argv: list[str] | None = None, loader=None, du=sibling.du_bytes) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    peek = argparse.ArgumentParser(add_help=False)
    peek.add_argument("--hf-home", default=None)
    peek.add_argument("--out", type=Path, required=True)
    known, _ = peek.parse_known_args(argv)
    hf_home = known.hf_home or os.environ.get("HF_HOME", "")
    if not hf_home:
        raise SystemExit("HF_HOME is unset and --hf-home was not given — the cache has no home")

    before = blob_inventory(hf_home)
    if not before:
        raise SystemExit(
            f"{hf_home} holds no blob files. The weights are not on this volume and this contract"
            " does not price a download here — STOP."
        )

    code = sibling.main(argv, loader=loader, du=du)
    after = blob_inventory(hf_home)

    record = json.loads(known.out.read_text(encoding="utf-8"))
    grew = {name: size for name, size in after.items() if size > before.get(name, 0)}
    record.update(
        {
            "blob_bytes_before": before,
            "blob_bytes_after": after,
            "blobs_counted": len(after),
            "blob_bytes_total": sum(after.values()),
            "blobs_that_grew": grew,
            "no_blob_grew": not grew,
            "the_invariant": (
                "no blob grows. The whole-cache `du -sb` delta above is bookkeeping — a `refs/main`"
                " write and zero-byte `.no_exist` markers — and it grades nothing"
            ),
        }
    )
    known.out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"blobs_counted       {len(after)}")
    print(f"blob_bytes_total    {sum(after.values())}")
    print(f"blobs_that_grew     {len(grew)}  {sorted(grew) if grew else ''}")
    print(f"no_blob_grew        {not grew}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
