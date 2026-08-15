"""The command centre: what it renders, what it refuses, and that no digit on it was typed.

The committed `dashboard/index.html` is read here and every check that can be made against a fresh
build is made against the COMMITTED bytes too — what ships is what an operator opens.
"""

import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_dashboard as builder  # noqa: E402
import export_dashboard_data as exporter  # noqa: E402

PAGE = builder.OUT.read_text(encoding="utf-8")
RECORD = json.loads(builder.EXPORT.read_text(encoding="utf-8"))
BLOB_OPEN = '<script type="application/json" id="export-data">'
BANNERS = 2 * (9 + 1)
"""The window banner renders on every tab and once in the footer, and each one carries BOTH
languages — a bilingual page holds two nodes where a monolingual one holds one."""

# the palette as `docs/PROMPT-phase6b.md` prints it. Copied by hand ONCE, on purpose: it is
# pre-validated on a machine this one is not, so a hex that drifts must fail here rather than ship
# as an unvalidated colour.
CONTRACT_PALETTE = {
    "surface": ("#fcfcfb", "#1a1a19"),
    "plane": ("#f9f9f7", "#0d0d0d"),
    "ink": ("#0b0b0b", "#ffffff"),
    "ink2": ("#52514e", "#c3c2b7"),
    "muted": ("#898781", "#898781"),
    "grid": ("#e1e0d9", "#2c2c2a"),
    "axis": ("#c3c2b7", "#383835"),
    "s1": ("#2a78d6", "#3987e5"),
    "s2": ("#eb6834", "#d95926"),
    "s3": ("#1baf7a", "#199e70"),
    "neg": ("#e34948", "#e66767"),
    "mid": ("#f0efec", "#383835"),
    "good": ("#0ca30c", "#0ca30c"),
    "warn": ("#fab219", "#fab219"),
    "serious": ("#ec835a", "#ec835a"),
    "critical": ("#d03b3b", "#d03b3b"),
    "deltagood": ("#006300", "#0ca30c"),
}
CONTRACT_RAMP = ("#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#2a78d6", "#1c5cab", "#104281")


def chrome(page: str) -> str:
    """The document without the embedded export — everything the build itself wrote."""
    return page.split(BLOB_OPEN)[0]


def digit_nodes(page: str) -> list[str]:
    """Every text node carrying a digit, in document order, blob excluded.

    Attributes are deliberately out: SVG geometry is derived from the figures and moves with them,
    and this list exists to answer «what does a reader SEE», which is the claim guard 4 makes.
    """
    return [text for text in re.findall(r">([^<>]*\d[^<>]*)<", chrome(page)) if text.strip()]


@pytest.fixture(scope="module")
def fresh(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("dashboard") / "index.html"
    assert builder.main(["--out", str(out), "--quiet"]) == 0
    return out


@pytest.fixture(scope="module")
def page() -> builder.Page:
    built = builder.build_page(builder.EXPORT, builder.STRINGS, builder.METRICS, builder.DERIVED)
    built.render()
    return built


def test_two_builds_are_byte_identical_and_the_committed_page_is_that_build(fresh, tmp_path):
    """Determinism, and the shipped file IS what the producer writes today.

    No clock, no git block, sorted everything — so the pair is byte-identical and anyone can
    regenerate what they are looking at. The second half is what makes the first load-bearing.
    """
    again = tmp_path / "again.html"
    assert builder.main(["--out", str(again), "--quiet"]) == 0

    assert fresh.read_bytes() == again.read_bytes()
    assert fresh.read_bytes() == builder.OUT.read_bytes()
    diff = subprocess.run(["diff", str(fresh), str(again)], capture_output=True, text=True)
    assert diff.returncode == 0 and diff.stdout == ""


def test_the_embedded_export_is_the_committed_export_byte_for_byte():
    """Guard 2: the page carries its own source, and the footer names its sha.

    A page that embedded a re-serialised copy would look identical and be unverifiable — the bytes
    are compared, not the parsed record.
    """
    raw = PAGE.split(BLOB_OPEN)[1].split("</script>")[0]

    assert raw[0] == "\n" and raw[-1] == "\n", "the join's own newlines, and only those"
    assert raw[1:-1].encode("utf-8") == builder.EXPORT.read_bytes()
    assert json.loads(raw) == RECORD
    sha = exporter.summary.sha256_of(builder.EXPORT)
    assert PAGE.count(sha[:16]) == BANNERS, "the banner on every tab, and the footer, in both"


def test_the_page_asks_the_network_for_nothing():
    """Guard 3: everything inline. The only external hrefs are t.me links on drill-down rows."""
    body = chrome(PAGE)

    for forbidden in (
        "<script src=",
        "<link ",
        "@import",
        'src="http',
        "fetch(",
        "XMLHttpRequest",
        "WebSocket",
        "<iframe",
        "url(http",
        "@font-face",
    ):
        assert forbidden not in body, forbidden
    assert "<img" not in body
    for href in re.findall(r'href="([^"]+)"', body):
        assert href.startswith("https://t.me/"), href
    assert len(re.findall(r'href="https://t\.me/', body)) > 50


def test_no_figure_was_typed_by_hand(tmp_path):
    """Guard 4: poison ONE figure in the export, rebuild, and see it move everywhere it surfaces.

    The target is `promo_depth.readings.from_price_pair.median`: it reaches a KPI tile and the
    quartile band's median label, and — unlike the aspect counts — it is nobody's drill-down
    population, so the build's own population check cannot fire first and mask the result.

    The export's sha is a figure ABOUT the export, so the banner nodes carrying it move too and are
    named as such; every other digit-bearing text node on the page must be untouched, which is the
    half of this test that would catch a hand-typed number.
    """
    poisoned = tmp_path / "poisoned.json"
    record = json.loads(builder.EXPORT.read_text(encoding="utf-8"))
    record["metrics"]["promo_depth"]["readings"]["from_price_pair"]["median"] = 0.1234
    poisoned.write_text(
        json.dumps(record, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8"
    )

    plain, spoilt = tmp_path / "plain.html", tmp_path / "spoilt.html"
    for out, export in ((plain, builder.EXPORT), (spoilt, poisoned)):
        assert builder.main(["--out", str(out), "--export", str(export), "--quiet"]) == 0

    before = digit_nodes(plain.read_text(encoding="utf-8"))
    after = digit_nodes(spoilt.read_text(encoding="utf-8"))
    assert len(before) == len(after) > 300
    moved = [(one, two) for one, two in zip(before, after, strict=True) if one != two]
    figures = [pair for pair in moved if "42.06%" in pair[0]]
    shas = [pair for pair in moved if "експорт" in pair[0] or "export " in pair[0]]

    assert len(figures) >= 2, "the median surfaces on more than one screen"
    assert all("12.34%" in new for _, new in figures)
    assert len(moved) == len(figures) + len(shas), moved
    assert len(shas) == BANNERS


def test_every_honest_stub_and_every_card_the_law_names_is_on_the_page():
    """Guard 5: the export's seven gaps, the registry's eight audiences, the law's four chains."""
    body = chrome(PAGE)

    assert set(builder.NOT_COMPUTABLE_ORDER) == set(RECORD["not_computable"])
    for name in builder.NOT_COMPUTABLE_ORDER:
        assert f'<span class="path">{name}</span>' in body
        assert RECORD["not_computable"][name]["unlock"] in body
    for _, key, field in builder.GAPS:
        assert field in body, field
    assert body.count('class="stub gap"') == len(builder.GAPS)

    segments = RECORD["cuts"]["comment_by_segment"]
    assert len(segments) == 8
    strings = yaml.safe_load(builder.STRINGS.read_text(encoding="utf-8"))["strings"]
    for name in segments:
        for language in ("ua", "en"):
            assert html.escape(strings[f"segment.{name}"][language]) in body, name
    assert body.count('<article class="card state-') == 8
    assert "state-silent" in body and "state-evidence_only" in body and "state-talked" in body

    for chain in builder.PROMO_CHAINS:
        assert RECORD["metrics"]["promo_pressure"]["by_chain"][chain]["named_by_amendment_3_20"]
    assert 'class="watermark"' in body and "макет — не дані" in body and "mock — not data" in body


def test_every_string_the_page_renders_is_in_the_file_and_nothing_in_the_file_is_orphaned(page):
    """Guard 6, both directions. A one-way check passes on a file full of dead keys."""
    declared = set(page.s.table)

    assert page.s.used == declared, declared ^ page.s.used
    for key, entry in page.s.table.items():
        assert entry["ua"] and entry["en"], key
    for language in ("ua", "en"):
        for key in ("app.title", "tab.t0", "t3.reading.retail_official"):
            assert html.escape(page.s.table[key][language]) in PAGE


def test_a_missing_key_and_a_missing_language_both_stop_the_build(tmp_path):
    """The negative control for the refusal — a bilingual page will not render half a label."""
    table = yaml.safe_load(builder.STRINGS.read_text(encoding="utf-8"))
    thinned = tmp_path / "thin.yaml"

    table["strings"].pop("t0.lead")
    thinned.write_text(yaml.safe_dump(table, allow_unicode=True), encoding="utf-8")
    with pytest.raises(SystemExit, match="has no `t0.lead`"):
        builder.build(builder.EXPORT, thinned, builder.METRICS, builder.DERIVED)

    table["strings"]["t0.lead"] = {"ua": "щось", "en": ""}
    thinned.write_text(yaml.safe_dump(table, allow_unicode=True), encoding="utf-8")
    with pytest.raises(SystemExit, match="has no `en`"):
        builder.build(builder.EXPORT, thinned, builder.METRICS, builder.DERIVED)


def test_a_drill_down_population_that_disagrees_with_the_export_stops_the_build(tmp_path):
    """The seam of the whole page: the rows under a figure are the rows that figure was computed on.

    The build reads the store and holds every expander's population against the export field the
    figure comes from. Here the export says one more price row than the store holds, and the build
    refuses rather than drawing ten rows out of a population it cannot name.
    """
    poisoned = tmp_path / "poisoned.json"
    record = json.loads(builder.EXPORT.read_text(encoding="utf-8"))
    record["metrics"]["aspect_share"]["by_sample"]["payable"]["labels"]["price"] += 1
    poisoned.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(SystemExit, match=r"drill-down `t2_price`: the store holds 553 rows"):
        builder.build(poisoned, builder.STRINGS, builder.METRICS, builder.DERIVED)


def test_the_rows_are_drawn_from_the_evidence_the_export_was_built_from(tmp_path):
    """A file whose bytes moved since the export is a refusal, not a footnote."""
    copy = tmp_path / "registry.yaml"
    shutil.copy(builder.REGISTRY, copy)
    copy.write_text(copy.read_text(encoding="utf-8") + "\n# one comment\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="are not the rows its numbers were computed over"):
        builder.through_the_provenance(RECORD, "inputs", "config/registry.yaml", copy)
    with pytest.raises(SystemExit, match="is not in the export's provenance"):
        builder.through_the_provenance(RECORD, "inputs", "config/nowhere.yaml", copy)


def test_the_draw_is_seeded_per_expander_and_its_ranks_say_so(page):
    """`.claude/rules/registrations-and-draws.md`: measure the RANKS, never the ids.

    One generator walked across several strata put three of five draws on rank 163 of their pools
    (Dv323). Each expander here seeds `f"{SEED}:{key}"`, so the rank vectors must differ between
    expanders — an id-equality test would pass on a perfectly correlated draw.
    """
    wide = {key: plan for key, plan in page.plans.items() if plan["count"] >= 100}
    assert len(wide) >= 8

    vectors = {}
    for key, plan in wide.items():
        drawn = page.draws[key]
        positions = builder.ranks(plan, drawn)
        assert len(positions) == builder.DRAW == 10
        assert len(set(positions)) == 10, key
        assert all(0 <= rank < plan["count"] for rank in positions)
        vectors[key] = tuple(positions)

    assert len(set(vectors.values())) == len(vectors), "two expanders drew the same ranks"
    shared = set.intersection(*(set(one) for one in vectors.values()))
    assert not shared, f"every wide expander drew rank(s) {shared} — the seed, not the population"


def test_a_comment_links_to_its_post_and_a_position_links_to_itself(page):
    """The one link the rows prove. A comment's own id belongs to the discussion group's space."""
    comment = page.draws["t2_price"][0]
    position = page.draws["t5_positions"][0]

    assert builder.link_of(comment, comment=True).endswith(str(comment["parent_msg_id"]))
    assert str(comment["msg_id"]) not in builder.link_of(comment, comment=True)
    assert builder.link_of(position, comment=False).endswith(str(position["msg_id"]))
    assert page.s("drill.link.comment_note")[0] in PAGE


def test_the_palette_is_the_one_the_contract_pre_validated():
    """A changed hex is an unvalidated hex: there is no validator on this machine."""
    assert builder.PALETTE == CONTRACT_PALETTE
    assert builder.RAMP == CONTRACT_RAMP
    for light, dark in CONTRACT_PALETTE.values():
        assert light in PAGE and dark in PAGE
    assert "prefers-color-scheme:dark" in PAGE and ':root[data-theme="dark"]' in PAGE
    assert ':root[data-theme="light"]' in PAGE, "the toggle must win in both directions"


def test_the_javascript_does_no_arithmetic_on_the_data():
    """The honesty seam, mechanised: JS may switch, sort and place — never compute a figure.

    `Number()` inside the sort comparator is the one numeric call, and it orders rows the build
    already wrote; the check is that the script never touches the embedded record at all.
    """
    script = PAGE.split(BLOB_OPEN)[1].split("</script>", 1)[1]

    for forbidden in ("export-data", "JSON.parse", "toFixed", "parseFloat", "reduce("):
        assert forbidden not in script, forbidden
    assert script.count("Number(") == 2, "the sort comparator, and nothing else"
    assert script.count("Math.max") == 1 and script.count("Math.") == 1, (
        "one clamp, and it clamps a tooltip to the viewport rather than a figure"
    )
    assert "textContent=text" in script.replace(" ", ""), "the tooltip prints, it does not build"


def test_every_metric_of_the_dictionary_reaches_a_surface_with_its_help(page):
    """The ⓘ and the glossary render from one file — plan §4, SPEC 3.20 (3)."""
    dictionary = yaml.safe_load(builder.METRICS.read_text(encoding="utf-8"))
    ids = [entry["id"] for entry in dictionary["metrics"]]

    assert set(ids) == set(RECORD["metrics"])
    for entry in dictionary["metrics"]:
        for language in ("ua", "en"):
            assert html.escape(entry["name"][language]) in PAGE, entry["id"]
            assert html.escape(entry["definition"][language]) in PAGE
        assert entry["export_field"] in PAGE
    assert PAGE.count('class="info"') >= len(ids)


def test_the_owner_can_read_the_window_and_its_source_from_every_tab():
    """«Снимок называет своё окно» — plan §7, on every tab and not only on the first."""
    window = RECORD["window"]

    assert chrome(PAGE).count('<p class="window">') == len(builder.TABS) + 1
    assert PAGE.count(window["anchor"][:10]) >= len(builder.TABS)
    for tab in builder.TABS:
        section = PAGE.split(f'<section class="tab" id="{tab}">')[1].split("<section")[0]
        assert '<p class="window">' in section, tab
        assert "28" in section and "2026-08-09" in section
