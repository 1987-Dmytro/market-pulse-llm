"""K12 — the screen renders from result files only, and refuses loudly when a source is missing.

Two halves, and the second is the one that gives the first a meaning. A screen that renders is not
evidence it reads what it claims to read; a screen that REFUSES a missing source, by name and with a
non-zero exit, is. The phase spec asks for the negative control in as many words: «a removed source
yields a non-zero exit with a named error».

The third assertion here is a rule about what may be printed, not about plumbing: SPEC 3.21 (4) and
3.22 (1) keep the extracted old price and the arithmetic depth off any surface that shows a row's
own promo price, and a surface can return the forbidden number without anybody noticing
([[a_surface_can_return_the_forbidden_number]]). So the rendered page is grepped for it.
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_promo_screen as screen  # noqa: E402

EXPORT = {
    "contract": "test",
    "window_id": "w1",
    "screen": {
        "positions": [
            {
                "row_id": "@atb:4342:0",
                "brand": {"display": "Рудь"},
                "item": {"line": "Чорниця-ожина", "size_value": 500.0, "size_unit": "г"},
                "chain": {"id": "atb", "named_by_amendment_3_20": True},
                "carrier": "leaflet_page",
                "tier": "position",
                "promo_price": 75.9,
                "printed_pct": 50.0,
                "depth": 0.5,
                "evidence": {"channel": "@atb", "msg_id": 4342},
            }
        ],
        "depth_by_chain_and_brand": [
            {"week": "2026-W35", "chain": "@atb", "brand": "Рудь", "depth_mean": 0.47}
        ],
        "weeks": ["2026-W35"],
        "rollup": [
            {"week": "2026-W35", "chain": "@atb", "brand": "Рудь", "metric": "sku_count",
             "value": 1.0}
        ],
        "feed": [
            {"channel": "@atb", "thread_root": 4342, "type": "цена", "msg_id": 101,
             "quote": "дорого стало"}
        ],
        "threads": {"population": 678, "not_collected": 12, "product_population": 666,
                    "read": 118, "queue": 548, "read_threads": ["@atb/4342"],
                    "from": "results/promo_threads_draw*.json :: population.by_channel"},
        "table_rows": {"attribution": 1, "signal": 1, "evidence": 1, "digest": 1, "unsure": 0,
                       "rollup": 1},
    },
}


@pytest.fixture
def export(tmp_path):
    path = tmp_path / "promo_screen_data.json"
    path.write_text(json.dumps(EXPORT, ensure_ascii=False), encoding="utf-8")
    return path


def test_the_screen_renders_from_the_export_alone(export, tmp_path):
    out = tmp_path / "promo.html"
    assert screen.main(["--export", str(export), "--out", str(out)]) == 0
    page = out.read_text(encoding="utf-8")
    for shown in ("Рудь", "Чорниця-ожина", "500 г", "75.9", "−50%", "дорого стало", "2026-W35"):
        assert shown in page, shown


def test_a_missing_file_is_a_named_non_zero_refusal(tmp_path):
    """The negative control the phase spec names, on the source as a whole."""
    with pytest.raises(SystemExit) as raised:
        screen.main(["--export", str(tmp_path / "gone.json"), "--out", str(tmp_path / "x.html")])
    assert raised.value.code != 0
    assert "gone.json" in str(raised.value.code), "the refusal must name the file"
    assert "make tick" in str(raised.value.code)


@pytest.mark.parametrize("removed", screen.REQUIRED)
def test_every_removed_block_is_a_named_non_zero_refusal(export, tmp_path, removed):
    """The same control per block. A screen missing one source must not render the rest and leave a
    blank panel — the blank reads as «no promo this week», which is a claim about the market."""
    document = json.loads(export.read_text(encoding="utf-8"))
    del document["screen"][removed]
    broken = tmp_path / "broken.json"
    broken.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(SystemExit) as raised:
        screen.main(["--export", str(broken), "--out", str(tmp_path / "x.html")])
    assert raised.value.code != 0
    assert removed in str(raised.value.code), "the refusal must name what is missing"


def test_the_page_never_prints_the_old_price_or_a_per_row_depth(export, tmp_path):
    """SPEC 3.21 (4) / 3.22 (1). `promo ÷ (1 − depth)` reconstructs the old price, so the arithmetic
    depth may not travel in a row beside that row's own promo price. Depth is on the page once, in
    its own aggregated panel — 47.0% — and 50% is the PRINTED badge, which is what the row may show.
    """
    out = tmp_path / "promo.html"
    screen.main(["--export", str(export), "--out", str(out)])
    page = out.read_text(encoding="utf-8")
    assert "price_old" not in page and "старая" not in page
    assert "0.5</td>" not in page, "the arithmetic depth must not be a column of the position row"
    row = page[page.index("<td>Рудь</td>") : page.index("</tr>", page.index("<td>Рудь</td>"))]
    assert "75.9" in row and "−50%" in row
    assert "0.47" not in row and "47.0%" not in row, "the window depth may not sit in the row"
    assert "47.0%" in page, "…but it IS on the page, in the aggregate panel 3.22 (1) allows"


def test_nothing_on_the_page_leaves_it(export, tmp_path):
    """`build_dashboard.py`'s rule, kept: no remote script, stylesheet, font or image."""
    out = tmp_path / "promo.html"
    screen.main(["--export", str(export), "--out", str(out)])
    page = out.read_text(encoding="utf-8")
    for forbidden in ("<script", "http://", "https://", "<link", "@import", "url("):
        assert forbidden not in page, forbidden
