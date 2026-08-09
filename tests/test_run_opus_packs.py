"""The session driver (`scripts/run_opus_packs.sh`), against a stub instead of Opus.

The driver's whole job is spending the operator's sessions carefully: two packs, then a
stop; one returns file per pack; a halt the moment a session comes back wrong. None of
that can be checked by reading it, and none of it may be checked by running it for real —
the contract says the sessions are the operator's. So `CLAUDE_BIN`, `OPUS_PACK_DIR` and
`OPUS_MANIFEST` are the seams, and every test below drives the real script end to end
with a fake `claude` that records what it was asked to do.
"""

import json
import os
import subprocess
import sys
from hashlib import sha256
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_opus_audit import REGISTRY, item  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
DRIVER = REPO_ROOT / "scripts" / "run_opus_packs.sh"

STUB = '''#!/usr/bin/env python3
"""A fake `claude`: prints a first line, writes the returns file it was allowed to write."""
import json, os, re, sys

argv = " ".join(sys.argv[1:])
number = re.search(r"returns_(\\d+)\\.jsonl", argv).group(1)
with open(os.environ["STUB_LOG"], "a", encoding="utf-8") as log:
    log.write(f"pack_{number}\\t{'--model opus' in argv}\\t{argv.count('allowedTools')}\\n")

print(os.environ.get("STUB_FIRST_LINE", "claude-opus-5"))
if os.environ.get("STUB_WRITE") == "0":
    sys.exit(0)

manifest = json.load(open(os.environ["OPUS_MANIFEST"], encoding="utf-8"))
rows = []
for entry in manifest["items"]:
    if entry["pack"] != f"pack_{number}":
        continue
    rows.append({
        "pack": entry["pack"],
        "item": entry["item"],
        "watchlist_hits": ["Dziugas"] if os.environ.get("STUB_BAD") == "1" else [],
        "other_dairy_brands": [],
        "caption_verdict": "faithful" if entry["judgeable_caption"] else "n/a",
        "brands_visible_missed": [],
        "note": "",
    })
path = os.path.join(os.environ["OPUS_PACK_DIR"], f"returns_{number}.jsonl")
with open(path, "w", encoding="utf-8") as handle:
    for row in rows:
        handle.write(json.dumps(row, ensure_ascii=False) + "\\n")
print(f"{len(rows)}/{len(rows)} items judged")
'''


@pytest.fixture
def world(tmp_path):
    """Three packs, their manifest, a stub `claude`, and the environment tying them."""
    packs = tmp_path / "packs"
    packs.mkdir()
    entries, items = [], []
    for number in ("01", "02", "03"):
        path = packs / f"pack_{number}.md"
        path.write_text(f"# pack {number}\n", encoding="utf-8")
        entries.append(
            {
                "pack": f"pack_{number}",
                "path": str(path),
                "sha256": sha256(path.read_bytes()).hexdigest(),
                "items": 2,
            }
        )
        items += [
            item(f"@chan:{number}1", pack=f"pack_{number}", brands=["rud"]),
            item(f"@chan:{number}2", pack=f"pack_{number}", judgeable=False, images=0),
        ]
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "seed": 42,
                "pinned_inputs": {
                    REGISTRY: sha256((REPO_ROOT / REGISTRY).read_bytes()).hexdigest()
                },
                "packs": entries,
                "items": items,
                "items_total": len(items),
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    stub = tmp_path / "claude"
    stub.write_text(STUB, encoding="utf-8")
    stub.chmod(0o755)
    log = tmp_path / "invocations.tsv"
    return {
        "packs": packs,
        "manifest": manifest,
        "log": log,
        "env": {
            **os.environ,
            "CLAUDE_BIN": str(stub),
            "OPUS_PACK_DIR": str(packs),
            "OPUS_MANIFEST": str(manifest),
            "STUB_LOG": str(log),
        },
    }


def run(world, *args, **overrides):
    env = {**world["env"], **overrides}
    return subprocess.run(
        [str(DRIVER), *args], cwd=REPO_ROOT, env=env, capture_output=True, text=True
    )


def invoked(world):
    if not world["log"].exists():
        return []
    return [line.split("\t")[0] for line in world["log"].read_text().splitlines()]


def test_the_pilot_runs_two_packs_and_stops(world):
    done = run(world)
    assert done.returncode == 0, done.stderr
    assert invoked(world) == ["pack_01", "pack_02"]
    assert not (world["packs"] / "returns_03.jsonl").exists()
    assert "STOP -- the pilot is done" in done.stdout
    assert "--after-pilot" in done.stdout


def test_the_pilot_returns_are_validated_as_they_land(world):
    done = run(world)
    assert "1 file(s) validate" in done.stdout
    rows = (world["packs"] / "returns_01.jsonl").read_text().splitlines()
    assert len(rows) == 2


def test_the_session_is_told_the_model_and_the_allowlist(world):
    run(world)
    model_named, allowlists = world["log"].read_text().splitlines()[0].split("\t")[1:]
    assert model_named == "True"
    assert allowlists == "1"


def test_the_rest_will_not_run_before_the_pilot(world):
    done = run(world, "--after-pilot")
    assert done.returncode == 1
    assert "run it first" in done.stderr
    assert invoked(world) == []


def test_after_the_pilot_the_rest_run(world):
    run(world)
    done = run(world, "--after-pilot")
    assert done.returncode == 0, done.stderr
    assert invoked(world) == ["pack_01", "pack_02", "pack_03"]
    assert (world["packs"] / "returns_03.jsonl").exists()


def test_a_pack_already_answered_is_not_run_again(world):
    """A returns file is an evening. The driver reads it, it does not re-buy it."""
    (world["packs"] / "returns_01.jsonl").write_text(
        json.dumps(
            {
                "pack": "pack_01",
                "item": "@chan:011",
                "watchlist_hits": [],
                "other_dairy_brands": [],
                "caption_verdict": "faithful",
                "brands_visible_missed": [],
                "note": "written by hand",
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    done = run(world)
    assert invoked(world) == ["pack_02"]
    assert "already exists -- skipping" in done.stdout


def test_a_session_that_is_not_opus_stops_the_run(world):
    done = run(world, STUB_FIRST_LINE="claude-sonnet-5")
    assert done.returncode != 0
    assert "does not name Opus" in done.stderr
    assert invoked(world) == ["pack_01"]  # and pack_02 was never bought


def test_a_session_that_writes_nothing_stops_the_run(world):
    done = run(world, STUB_WRITE="0")
    assert done.returncode != 0
    assert "No " in done.stderr and "was written" in done.stderr
    assert invoked(world) == ["pack_01"]


def test_returns_that_do_not_validate_stop_the_run(world):
    done = run(world, STUB_BAD="1")
    assert done.returncode != 0
    assert "neither a brand_id nor a display name" in done.stdout
    assert invoked(world) == ["pack_01"]


def test_a_dry_run_spends_nothing(world):
    done = run(world, "--dry-run")
    assert done.returncode == 0, done.stderr
    assert invoked(world) == []
    assert not list(world["packs"].glob("returns_*.jsonl"))
    assert done.stdout.count("--allowedTools") == 2
    assert "Write(" in done.stdout and "pack_01.md" in done.stdout


def test_only_runs_one_pack(world):
    done = run(world, "--only", "03")
    assert done.returncode == 0, done.stderr
    assert invoked(world) == ["pack_03"]


def test_no_packs_is_a_refusal_not_an_empty_loop(world, tmp_path):
    empty = tmp_path / "nothing"
    empty.mkdir()
    done = run(world, OPUS_PACK_DIR=str(empty))
    assert done.returncode == 1
    assert "Build them first" in done.stderr
