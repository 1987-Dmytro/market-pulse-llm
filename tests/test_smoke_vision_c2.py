"""The C2 vision smoke's $0 half — the selection and rung 0, before anything bills."""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import smoke_vision_c2 as smoke  # noqa: E402


def test_the_smoke_never_draws_from_the_population_5c2_already_bought():
    """`post_media_5c1.json`'s 159 pages are the exam. A rate measured on them is not a sample.

    Both directions: the excluded manifest is named and absent from the list the draw walks, and
    the manifests it does walk are on disk — a selection that silently found no manifest at all
    would return an empty draw and this test would be the only thing that could say so.
    """
    assert smoke.EXCLUDED_MANIFEST not in smoke.MANIFESTS
    assert smoke.MANIFESTS, "a draw over no manifest is not a draw"
    chosen = smoke.pages()
    assert len(chosen) == smoke.MAX_PAGES
    assert {p["manifest"] for p in chosen} <= set(smoke.MANIFESTS)
    assert smoke.EXCLUDED_MANIFEST not in {p["manifest"] for p in chosen}


def test_the_draw_is_the_same_draw_twice():
    """Seeded and sorted, so the registration's `ids_sha256` still names it at the paid step."""
    assert smoke.ids_sha256(smoke.pages()) == smoke.ids_sha256(smoke.pages())


def test_rung_0_is_priced_from_measured_seconds_and_fits_the_cap():
    """Two boots, the slower measured one, plus the idle tail — and it must fit BEFORE the create.

    The negative control matters more than the pass: a projection that could not go over the cap
    would be a rung that never fires. 300 pages at the same rates must not fit.
    """
    fits = smoke.projection(smoke.MAX_PAGES)
    assert fits["boots_priced"] == 2, "something boots at creation (srv2c_bootlog)"
    assert fits["projected_usd"] <= smoke.CAP_USD and fits["fits"]
    assert not smoke.projection(300)["fits"], "the rung can refuse, so its pass means something"


def test_the_registration_pins_the_worker_run_5c2_asserts():
    """One pin, not a second copy of it — a hand-written expectation is free to drift."""
    prereg = json.loads(smoke.PREREG.read_text(encoding="utf-8"))
    pinned = json.loads(smoke.POSITIONS_PIN.read_text(encoding="utf-8"))["expected_worker"]
    assert prereg["expected_worker"] == pinned
    assert pinned["serving_config"] == "POSITIONS"
    assert pinned["adapter_sha256"] is None, "POSITIONS is the base with the adapter OFF"
