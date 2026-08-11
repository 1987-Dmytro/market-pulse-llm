"""The serving pin: the values the code serves ARE the values the file pins.

SPEC 3.17 (9) makes `results/sku_pilot_serving.json` the identity stop — the driver refuses to make
its first paid call unless the worker's `describe()` matches it. That is only a stop while the two
sides cannot drift, and they can drift in both directions: an edit to `serve_handler` that the pin
never learned about, and a pin edited to agree with a worker that had already changed.

So every assertion here is between the ARTIFACT and the CODE, never between two constants in this
file. The one place a literal is allowed is the transcription check, and that reads its number back
out of `docs/SPEC.md`.
"""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest
from market_pulse import local_llm, prompts, serving

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))


def _script(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


handler = _script("serve_handler")
writer = _script("write_sku_serving_pin")


@pytest.fixture(scope="module")
def pin() -> dict:
    return json.loads(writer.RECORD.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def prereg() -> dict:
    return json.loads(writer.PREREG.read_text(encoding="utf-8"))


def test_the_pin_is_what_this_checkout_would_write(pin, prereg):
    """Everything but the two fields that MUST move on a rewrite. If this reddens, either the code
    moved under a committed pin or the pin was hand-edited — and the answer is never to re-run the
    writer over it, because the artifact's value is that it predates the run."""
    fresh = writer.build(prereg, writer.RECORD)
    assert {k: v for k, v in fresh.items() if k not in ("generated_at", "git")} == {
        k: v for k, v in pin.items() if k not in ("generated_at", "git")
    }


def test_the_worker_this_repo_builds_satisfies_the_pin(pin):
    """The other direction, and the one that matters on the day: `assert_serving` is handed the
    pin's own `expected_worker` block against what `describe` answers for a POSITIONS worker. A
    field the worker does not report is read as `<absent>` and refuses."""
    info = handler.describe(
        handler.settings(
            {"SERVING_CONFIG": "POSITIONS", "MODEL_REVISION": pin["serving"]["model_revision"]}
        ),
        {},
        None,
        {},
    )
    assert serving.assert_serving(info, pin["expected_worker"]) is info


def test_every_expected_field_can_actually_fire(pin):
    """The negative control on the test above. An `expected` block whose fields the worker happens
    to satisfy for unrelated reasons is not a guard — each one has to be able to refuse."""
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
        missing = {k: v for k, v in base.items() if k != field}
        with pytest.raises(SystemExit, match="not serving the registered configuration"):
            serving.assert_serving(missing, pin["expected_worker"])


def test_the_pin_names_the_generation_knobs_the_client_uses(pin):
    served = pin["serving"]
    assert served["serving_config"] == serving.POSITIONS_CONFIG
    assert served["merge_state"] == serving.MERGE_STATE[serving.POSITIONS_CONFIG]
    assert served["adapter"] is None and pin["expected_worker"]["adapter_sha256"] is None
    assert served["model"] == local_llm.MODEL_ID
    assert served["quantization"] == local_llm.QUANTIZATION
    assert served["chat_template"] == local_llm.CHAT_TEMPLATE
    assert served["do_sample"] is False and served["decoding"] == "greedy"
    assert served["forward_batch_size"] == 1
    assert served["max_new_tokens"] == local_llm.POSITIONS_MAX_NEW_TOKENS
    assert served["max_new_tokens"] == handler.MAX_NEW_TOKENS[serving.POSITIONS_CONFIG]


def test_the_two_prompt_shas_are_the_pre_registrations(pin, prereg):
    """Copied, not recomputed. The bars were registered against these two texts; a checkout that
    renders anything else is a revised instrument, which is a NEW registration, never an edit."""
    for task in prompts.POSITIONS:
        assert pin["instruments"][task] == prereg["instruments"][task]
        assert pin["instruments"][task] == prompts.prompt_sha256(task)
    assert pin["expected_worker"]["positions_prompt_sha256"] == {
        task: prereg["instruments"][task] for task in sorted(prompts.POSITIONS)
    }
    assert (
        pin["pinned_inputs"]["results/sku_pilot_prereg_v2.json"]
        == hashlib.sha256(writer.PREREG.read_bytes()).hexdigest()
    )


def test_a_moved_instrument_stops_the_writer(monkeypatch, prereg, tmp_path):
    """The refusal that would have caught an edited prompt text. Driven on a copy of the prereg
    with one sha changed, so the check fires on the artifact rather than on the code."""
    moved = json.loads(json.dumps(prereg))
    moved["instruments"]["positions_text_gm4"] = "0" * 64
    with pytest.raises(SystemExit, match="renders a text that is not the one"):
        writer.instruments(moved)


def test_the_revision_is_corroborated_by_a_record_that_served_it(pin):
    """A typed sha is a guess until something that ran on it agrees. SPEC abbreviates the revision
    and a worker cannot be held to an abbreviation, so the full value is checked against the
    freshest PAID record on this base — and the law's prefix against the full value."""
    assert writer.pinned_revision() == pin["serving"]["model_revision"]
    served = json.loads(writer.REVISION_SOURCE.read_text(encoding="utf-8"))
    assert served["endpoint"]["worker"]["revision_requested"] == pin["serving"]["model_revision"]
    assert f"`{pin['serving']['model_revision'][:12]}…`" in (
        (REPO_ROOT / "docs" / "SPEC.md").read_text(encoding="utf-8")
    )


def test_a_wrong_revision_is_refused_rather_than_written(monkeypatch):
    monkeypatch.setattr(writer, "MODEL_REVISION", "f" * 40)
    with pytest.raises(SystemExit, match="is not the base SPEC 3.17 \\(9\\) fixes"):
        writer.pinned_revision()


def test_the_pin_refuses_to_be_rewritten_over(tmp_path):
    """Once the paid attempt has read it, a regenerated copy would carry a timestamp and a git
    block from AFTER the run — which is exactly what the artifact exists to rule out."""
    out = tmp_path / "pin.json"
    assert writer.main(["--out", str(out)]) == 0
    with pytest.raises(SystemExit, match="already exists"):
        writer.main(["--out", str(out)])
    assert writer.main(["--out", str(out), "--force"]) == 0


def test_the_pin_predates_every_sku_b_run_artifact():
    """The claim the record makes about itself, checked: nothing this pin exists to judge is in
    the repo yet. A pin committed after the run it constrains is a rationalisation."""
    for name in ("positions_gm4_*.json", "sku_b_*.json", "spend_sku_b*.json"):
        assert not list((REPO_ROOT / "results").glob(name)), name
