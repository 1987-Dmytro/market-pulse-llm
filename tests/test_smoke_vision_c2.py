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


def test_the_projection_uses_the_measured_rate_and_bounds_the_marginal():
    """K4 stops being a band the moment the ledger has the row — and says what the row contains.

    Two directions that matter more than the pass. (1) The measured corner must be IN the table:
    a projection that wrote the row and then projected off the interpolation would answer SP-1
    with a number nothing measured. (2) The marginal bound must be strictly inside the ledger's
    boot-inclusive rate — if it were not, the bound would be claiming the cold start cost nothing,
    and the two blocks would be the same number wearing two names.
    """
    import promo_projection_c2 as k4

    row = k4.measured_rate()
    assert row and row["name"] == k4.VISION_RATE_NAME and row["n"] == smoke.MAX_PAGES

    record = json.loads((k4.REPO_ROOT / "results" / "promo_projection_c2.json").read_text("utf-8"))
    names = [corner["name"] for corner in record["table"]]
    assert "measured_smoke" in names, "the measured rate has to reach the table"
    verdict = record["verdict"]
    assert verdict["the_one_number_usd"] is not None

    bound = verdict["marginal_bound"]
    assert bound["seconds_per_page_lower"] < bound["seconds_per_page_upper"] < row["value"], (
        "the boot-amortised marginal must be cheaper than the boot-inclusive measurement"
    )
    assert bound["one_boot_seconds"] > 0
    # And the floor's two ends bracket: a bound whose ends crossed would be arithmetic, not a bound.
    lo, hi = bound["usd_at_pages_floor"]
    assert 0 < lo < hi < verdict["the_one_number_usd"]
