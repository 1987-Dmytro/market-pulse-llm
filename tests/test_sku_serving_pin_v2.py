"""Serving pin v2: instrument v2's configuration, registered beside v1 and not in place of it.

The expensive failure is a worker that answers under a configuration nobody registered, and the
cheap version of it is a second pin that quietly moved more than the amendment did. So the two
things held here are: exactly one knob differs from the sealed v1 pin, and the worker this checkout
builds satisfies THIS pin while v1's refuses it by name.
"""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

import serve_handler as handler  # noqa: E402

from market_pulse import local_llm, prompts, serving  # noqa: E402


def _script(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


writer = _script("write_sku_serving_pin_v2")
v1 = writer.v1


@pytest.fixture(scope="module")
def pin():
    return json.loads(writer.RECORD.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def previous():
    return json.loads(v1.RECORD.read_text(encoding="utf-8"))


def test_exactly_one_knob_differs_from_the_sealed_v1_pin(pin, previous):
    """(13)(a) raises the ceiling. Anything else moving is a configuration nobody ratified, and the
    producer refuses rather than writes — this is that comparison, on the shipped pair."""
    moved = sorted(
        field
        for field in set(pin["expected_worker"]) | set(previous["expected_worker"])
        if pin["expected_worker"].get(field) != previous["expected_worker"].get(field)
    )
    assert moved == ["max_new_tokens"] == [writer.CHANGED]
    assert previous["expected_worker"]["max_new_tokens"] == 800
    assert pin["expected_worker"]["max_new_tokens"] == 1200


def test_the_ceiling_is_the_live_one_and_v1s_is_the_transcribed_one(pin, previous):
    assert pin["serving"]["max_new_tokens"] == local_llm.POSITIONS_MAX_NEW_TOKENS == 1200
    assert pin["serving"]["max_new_tokens"] == handler.MAX_NEW_TOKENS[serving.POSITIONS_CONFIG]
    assert pin["serving"]["max_new_tokens_was"] == v1.MAX_NEW_TOKENS == 800
    assert previous["serving"]["max_new_tokens"] == 800


def test_the_prompts_did_not_move_with_the_ceiling(pin, previous):
    """«No new ML mechanism is authorised» — (13). The parser, the ceiling and the alias table move;
    the two registered texts do not, and they are copied from the same pre-registration v1 read."""
    for task in prompts.POSITIONS:
        assert pin["instruments"][task] == previous["instruments"][task]
        assert pin["instruments"][task] == prompts.prompt_sha256(task)
    assert pin["instruments"]["source"] == previous["instruments"]["source"]


def test_the_worker_this_repo_builds_satisfies_this_pin(pin):
    info = handler.describe(
        handler.settings(
            {"SERVING_CONFIG": "POSITIONS", "MODEL_REVISION": pin["serving"]["model_revision"]}
        ),
        {},
        None,
        {},
    )
    assert serving.assert_serving(info, pin["expected_worker"]) is info


def test_a_worker_still_generating_the_old_ceiling_is_refused_by_name(pin):
    """The reason the ceiling is a PINNED field rather than a client-side default: a stale worker
    answers every other check and truncates exactly the dense pages (13)(a) exists to keep."""
    info = handler.describe(
        handler.settings(
            {"SERVING_CONFIG": "POSITIONS", "MODEL_REVISION": pin["serving"]["model_revision"]}
        ),
        {},
        None,
        {},
    )
    stale = dict(info) | {"max_new_tokens": 800}
    with pytest.raises(SystemExit, match=r"max_new_tokens: worker says 800, expected 1200"):
        serving.assert_serving(stale, pin["expected_worker"])


def test_every_expected_field_can_actually_fire(pin):
    """The negative control: an `expected` block whose fields the worker happens to satisfy for
    unrelated reasons is not a guard."""
    base = handler.describe(
        handler.settings(
            {"SERVING_CONFIG": "POSITIONS", "MODEL_REVISION": pin["serving"]["model_revision"]}
        ),
        {},
        None,
        {},
    )
    for field in pin["expected_worker"]:
        broken = dict(base)
        broken[field] = "<moved>"
        with pytest.raises(SystemExit, match="not serving the registered configuration"):
            serving.assert_serving(broken, pin["expected_worker"])


def test_it_pins_the_v1_record_it_stands_beside(pin):
    assert pin["supersedes"]["path"] == "results/sku_pilot_serving.json"
    assert (
        pin["supersedes"]["sha256"]
        == hashlib.sha256(v1.RECORD.read_bytes()).hexdigest()
        == pin["pinned_inputs"]["results/sku_pilot_serving.json"]
    )
    assert "stays SEALED" in pin["supersedes"]["reading"]
    assert pin["authority"].startswith("docs/SPEC.md amendment 3.17 (13)(a)")


def test_it_says_where_the_parsers_sha_is_pinned_instead(pin):
    """Half of instrument v2 is client-side and no worker can report it, so this file names where
    that half is registered rather than leaving the reader to assume it is here."""
    assert "sku_pilot_prereg_b2.json" in pin["not_in_scope"]["the parser"]
    assert "market_pulse.positions runs on the CLIENT" in pin["not_in_scope"]["the parser"]


# --- the refusals ---------------------------------------------------------------------------------


def test_it_refuses_to_overwrite_a_pin_that_may_have_been_read():
    assert writer.RECORD.exists()
    with pytest.raises(SystemExit, match="already exists"):
        writer.main([])


def test_a_second_moved_knob_stops_the_write(monkeypatch, tmp_path):
    """The producer's own guard, driven: a v2 that differs from v1 on anything but the ceiling is a
    configuration the amendment did not ratify."""
    monkeypatch.setattr(
        writer,
        "expected_worker",
        lambda prereg: (
            writer.v1.expected_worker(prereg)
            | {
                "max_new_tokens": 1200,
                "merge_state": "merged-requantized",
            }
        ),
    )
    with pytest.raises(SystemExit, match=r"differs from results/sku_pilot_serving.json on"):
        writer.main(["--out", str(tmp_path / "v2.json")])


def test_a_ceiling_that_went_DOWN_stops_the_write(monkeypatch, tmp_path):
    """The direction matters: (13)(a) raises the ceiling, and a lower one would truncate the pages
    the amendment exists to keep. Driven with the negative control the equality check cannot be."""
    monkeypatch.setattr(
        writer,
        "expected_worker",
        lambda prereg: writer.v1.expected_worker(prereg) | {"max_new_tokens": 400},
    )
    with pytest.raises(SystemExit, match="RAISES it"):
        writer.main(["--out", str(tmp_path / "v2.json")])


def test_a_moved_instrument_stops_the_writer(tmp_path):
    """Inherited from v1's producer and re-driven here, because this file calls it: a checkout that
    renders a text the pre-registration does not name is a revised instrument."""
    prereg = json.loads(v1.PREREG.read_text(encoding="utf-8"))
    prereg["instruments"]["positions_text_gm4"] = "0" * 64
    moved = tmp_path / "prereg.json"
    moved.write_text(json.dumps(prereg, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(SystemExit, match="renders a text that is not the one"):
        writer.main(["--prereg", str(moved), "--out", str(tmp_path / "v2.json")])


def test_the_shipped_pin_is_the_one_this_script_writes(tmp_path):
    fresh = writer.build(json.loads(v1.PREREG.read_text(encoding="utf-8")), tmp_path / "v2.json")
    shipped = json.loads(writer.RECORD.read_text(encoding="utf-8"))
    for record in (fresh, shipped):
        record.pop("generated_at"), record.pop("git")
    assert fresh == shipped
