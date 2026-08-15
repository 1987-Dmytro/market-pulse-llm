#!/usr/bin/env python3
"""`results/dashboard_data_w1.json` → `dashboard/index.html` — the command centre of SPEC 3.20.

**One figure source.** Every digit this page prints comes from the export, or from an arithmetic
derivation of the export's own values made HERE, at build time, where a test can see it. Nothing is
recomputed from the derived store, nothing is typed by hand, and where the export carries no figure
the surface renders a stub that names what is missing — never a zero. Two stub classes, kept apart
on purpose: :data:`NOT_COMPUTABLE_ORDER` are the export's own honest gaps (each with its unlock),
and :data:`GAPS` are surfaces this contract names that the aggregate layer exports no field for —
that second list IS phase 6a's backlog and the report carries it.

**The rows behind the figures are the same rows.** The drill-down samples are read through the ONE
reader (`scripts/window_summary_5c2.py`'s path, the same one `scripts/build_aggregates.py` imports)
and every file it opens is checked against the export's own `provenance` shas before a line of it is
parsed. A page that showed rows from evidence the figures were not built from would be worse than a
page with no rows at all. Each expander declares the export field that holds its population size and
the build REFUSES when the rows it found do not number what the export says.

**Nothing leaves the page.** No `<script src>`, no stylesheet link, no webfont, no remote image, no
fetch: the only external hrefs are t.me links on drill-down rows and on the promo table. JS does
tabs, the two toggles, tooltip show/hide, table sort and the promo table's filters — it hides rows
and swaps option labels, it computes no figure; both languages of every label and tooltip are
rendered into the document at build time.

    PYTHONPATH=src python3 scripts/build_dashboard.py
    PYTHONPATH=src python3 scripts/build_dashboard.py --out /tmp/index.html --export /tmp/poisoned.json
"""

import argparse
import html
import json
import random
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import window_summary_5c2 as summary  # noqa: E402

from market_pulse import brands, loop  # noqa: E402

EXPORT = REPO_ROOT / "results" / "dashboard_data_w1.json"
STRINGS = REPO_ROOT / "config" / "ui_strings.yaml"
METRICS = REPO_ROOT / "config" / "metrics.yaml"
REGISTRY = REPO_ROOT / "config" / "registry.yaml"
RULES = REPO_ROOT / "config" / "watchlist_rules.yaml"
PREREG = REPO_ROOT / "results" / "prereg_5c2_run.json"
DERIVED = REPO_ROOT / "data" / "derived"
OUT = REPO_ROOT / "dashboard" / "index.html"

REVISION_CARRIER = "comment"
"""Which text the revised matcher is told the drill-down rows are. Same constant, same reason as
`build_aggregates.CARRIER`: SPEC 3.21 (1) scopes one of its three rules to comment text."""

SEED = 42
"""The draw's seed, recorded in every expander's caption. Each expander seeds `f"{SEED}:{key}"` and
not `SEED`: one generator walked across several strata put three of five draws on the same rank of
their pools (Dv323, `.claude/rules/registrations-and-draws.md`)."""

DRAW = 10
"""Rows per expander. A cap, not a target — a population of three draws three."""

# --- the pre-validated palette (docs/PROMPT-phase6b.md; a changed hex is an unvalidated hex) -------

PALETTE = {
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

RAMP = ("#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#2a78d6", "#1c5cab", "#104281")
"""The sequential ramp, light→dark.

The contract bounds DISCRETE ordinal marks at «no lighter than #86b6ef on light, no darker than
#184f95 on dark», and on this ramp that is indices 2…5: index 1 (#9ec5f4) is lighter than the floor
and index 6 (#104281) darker than the ceiling. What the page actually spends is index 4 as its one
hue and index 2 for the second depth reading — a second instrument, not a second rank — with
de-emphasis carried by `--muted` rather than by a paler blue, because the contract asks for gray."""

POSITIVE_POLE = "s1"
"""The diverging pair's + pole. The contract names the − pole (red) and the gray midpoint and
leaves the + pole to the series slots; series-1 blue is taken because the aqua and green slots are
one step from the reserved status green, and status colour may not be spent on data."""

# --- honest gaps: surfaces this contract names that the export carries no field for ---------------

GAPS = (
    ("t2", "t2.gap.brand_aspect", "cuts.brand_by_aspect"),
    ("t2", "t2.gap.negative_profile", "cuts.aspect_by_sentiment"),
    ("t4", "t4.gap.private_label", "dictionary.watchlist[].private_label"),
    ("t8", "t8.gates.model", "gates.model"),
)
"""(tab, ui-string key, the export field that would fill it). The private-label badge is here and
not in the code because nothing in the repository knows which watchlist brands are chain private
labels: `config/registry.yaml` carries `own` and a section COMMENT, `market_pulse.registry`'s
`WatchlistBrand` has three fields, and `config/lexicon.yaml` — which the plan's data table names as
the home of the flags — is the category vocabulary and holds no brand at all."""

NOT_COMPUTABLE_ORDER = (
    "trend_vs_previous_window",
    "alert_baselines",
    "category_layer",
    "leaflet_depth_for_silpo_varus_marketopt",
    "reactions_views_votes",
    "reach",
    "sales_linkage",
)

TABS = ("t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7", "t8")

TAB_SOURCES = {
    "t0": (
        "metrics.volume",
        "metrics.nsr",
        "metrics.negative_share_sarcasm_adjusted",
        "metrics.sov",
        "metrics.promo_depth",
        "metrics.coverage",
        "not_computable.trend_vs_previous_window",
    ),
    "t1": (
        "metrics.nsr",
        "metrics.negative_share_sarcasm_adjusted",
        "metrics.sov",
        "cuts.brand_by_sentiment",
    ),
    "t2": ("metrics.aspect_share",),
    "t3": ("cuts.comment_by_segment", "metrics.coverage"),
    "t4": ("metrics.sov", "cuts.brand_by_sentiment", "metrics.promo_pressure.by_brand"),
    "t5": (
        "metrics.promo_depth",
        "metrics.promo_pressure",
        "cuts.positions_by_category",
        "cuts.positions_by_carrier",
        "promo.positions_table",
        "not_computable.leaflet_depth_for_silpo_varus_marketopt",
    ),
    "t6": ("not_computable.category_layer",),
    "t7": ("not_computable.alert_baselines", "not_computable.trend_vs_previous_window"),
    "t8": ("dictionary", "provenance", "convergence", "not_computable"),
}

ASPECTS = ("price", "taste", "availability", "service", "quality", "packaging")
"""Fixed slot order, so a hue follows the aspect and never its rank in a particular window."""

SENTIMENT = ("negative", "neutral", "positive")
"""The ordered scale, in its order — a diverging form only reads if the middle is the middle."""

# --- small helpers --------------------------------------------------------------------------------


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def num(value) -> str:
    """An integer with a narrow no-break space between thousands — one format for both languages."""
    return f"{int(value):,}".replace(",", " ")


def pct(share, digits: int = 1, sign: bool = False) -> str:
    """A share as a percent. `None` is not 0.0 — a rate over no rows has no value at all."""
    if share is None:
        return "—"
    text = f"{share * 100:.{digits}f}"
    return f"+{text}%" if sign and share > 0 else f"{text}%"


def bi(ua: str, en: str, tag: str = "span", cls: str = "") -> str:
    """One string in two languages, both in the document; CSS shows the active one."""
    room = f" {cls}" if cls else ""
    return f'<{tag} class="ua{room}">{ua}</{tag}><{tag} class="en{room}">{en}</{tag}>'


def tip(ua: str, en: str) -> str:
    """A tooltip's two languages as attributes — JS shows one, it never composes one."""
    return f' data-tip-ua="{esc(ua)}" data-tip-en="{esc(en)}"'


def dig(record: dict, path: str):
    """`a.b.c` → the value, or a refusal naming the path. The export is a contract, not a guess."""
    node = record
    for step in path.split("."):
        if not isinstance(node, dict) or step not in node:
            raise SystemExit(
                f"the export carries no `{path}` (it stops at `{step}`) — the dashboard renders"
                " figures the export holds and stubs for the rest, and a surface that silently"
                " lost its field would render neither"
            )
        node = node[step]
    return node


class Strings:
    """`config/ui_strings.yaml`, with a refusal for a missing key or a missing language.

    Every lookup is recorded, so `tests/test_ui_strings.py` can hold the file and the page against
    each other in both directions: no key rendered that the file lacks, no key in the file that no
    surface renders.
    """

    def __init__(self, path: Path):
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.table = loaded["strings"]
        self.used: set[str] = set()

    def __call__(self, key: str, **fmt) -> tuple[str, str]:
        """The two languages of one key. A `(ua, en)` pair passed in as a value is split per side,
        so a template that carries a word rather than a number stays translated on both."""
        entry = self.table.get(key)
        if entry is None:
            raise SystemExit(
                f"config/ui_strings.yaml has no `{key}` — the page will not render a"
                " surface whose words are missing"
            )
        out = []
        for index, language in enumerate(("ua", "en")):
            if not entry.get(language):
                raise SystemExit(
                    f"config/ui_strings.yaml: `{key}` has no `{language}` — a bilingual page with"
                    " one language empty is a page that lies about being bilingual"
                )
            side = {
                name: value[index] if isinstance(value, tuple) else value
                for name, value in fmt.items()
            }
            out.append(entry[language].format(**side) if fmt else entry[language])
        self.used.add(key)
        return out[0], out[1]

    def html(self, key: str, tag: str = "span", cls: str = "", **fmt) -> str:
        ua, en = self(key, **fmt)
        return bi(esc(ua), esc(en), tag=tag, cls=cls)


# --- the evidence behind the drill-down -----------------------------------------------------------


def through_the_provenance(record: dict, kind: str, name: str, path: Path) -> None:
    """A file the build is about to read, held against the export's own sha for it."""
    pinned = dig(record, f"provenance.{kind}").get(name)
    found = summary.sha256_of(path)
    if pinned is None:
        raise SystemExit(
            f"{name} is not in the export's provenance.{kind} — the dashboard may only draw rows"
            " from the evidence the figures were built from"
        )
    if pinned != found:
        raise SystemExit(
            f"{name} hashes to {found[:16]}… and the export pins {pinned[:16]}… — the rows this"
            " page would show are not the rows its numbers were computed over. Stop and report."
        )


def read_evidence(record: dict, derived: Path) -> dict:
    """Comments and position rows, through the one reader, from the export's own evidence files."""
    prereg = json.loads(summary.read_text_or_refuse(PREREG))
    for name, path in (("config/registry.yaml", REGISTRY), ("results/prereg_5c2_run.json", PREREG)):
        through_the_provenance(record, "inputs", name, path)
    registry = summary.registry_through_the_seal(prereg, REGISTRY)
    aliases = brands.watchlist_aliases(registry.watchlist)

    def load(record_type: str) -> list[dict]:
        rows: list[dict] = []
        for path in summary.leg_files(derived, record_type):
            through_the_provenance(record, "evidence", str(path.relative_to(REPO_ROOT)), path)
            rows += summary.read_rows(path)
        return rows

    through_the_provenance(record, "inputs", "config/watchlist_rules.yaml", RULES)
    rules = brands.load_watchlist_rules(RULES)
    comments = load(loop.RECORD_TYPE)
    verdicts = summary.comment_verdicts(comments, aliases)
    for verdict, row in zip(verdicts, comments, strict=True):
        verdict["parent_msg_id"] = row["parent_msg_id"]
        verdict["row"] = row
        # the page's brand figures are the export's, and the export counts under SPEC 3.21 (1)'s
        # revision — so the rows a reader opens under one of those figures have to be selected the
        # same way. `brands` (the anchor matching) stays on the verdict because the sealed record
        # was measured with it; nothing on this page reads it.
        verdict["brands_r1"] = [
            found["brand_id"]
            for found in brands.find_watchlist_brands(
                summary.comment_text(row), aliases, rules, carrier=REVISION_CARRIER
            )
        ]
    positions = load(loop.POSITION_RECORD_TYPE) + load(loop.POST_POSITION_RECORD_TYPE)
    return {
        "comments": verdicts,
        "positions": positions,
        # the operator reads «Гармонія», not `garmonija`. A display name is registry metadata and
        # not a figure — the id stays in `data-brand`, in the tooltips and in every export path, so
        # nothing here joins on the pretty name.
        "brand_names": {brand.brand_id: brand.display_names[0] for brand in registry.watchlist},
    }


def scored_payable(verdict: dict) -> bool:
    """SPEC 3.19: the payable sample is the rows that carried words, scored is what parsed."""
    return bool(verdict["labels"]) and not verdict["empty_text"]


def drill_populations(record: dict, evidence: dict, strings: Strings) -> list[dict]:
    """Every expander: its rows, and the export field that says how many there should be.

    The count is not computed here and then displayed — it is READ from the export and the rows are
    held against it. An expander whose population disagrees with the figure it hangs under would be
    a drill-down into a different number.
    """
    comments, positions = evidence["comments"], evidence["positions"]
    segments = dig(record, "cuts.comment_by_segment")
    of_segment = {
        channel: name for name, card in segments.items() for channel in card["channels_with_a_row"]
    }
    plans: list[dict] = []

    def plan(key, tab, count_path, rows, label_ua, label_en):
        plans.append(
            {
                "key": key,
                "tab": tab,
                "count_path": count_path,
                "rows": rows,
                "label": (label_ua, label_en),
            }
        )

    for name in ("negative", "positive"):
        plan(
            f"t1_{name}",
            "t1",
            f"metrics.nsr.by_sample.payable.{name}",
            [row for row in comments if scored_payable(row) and row["labels"]["sentiment"] == name],
            *strings(f"common.{name}"),
        )
    plan(
        "t1_sarcasm",
        "t1",
        "metrics.negative_share_sarcasm_adjusted.by_sample.payable.reclassified_from_sarcasm",
        [
            row
            for row in comments
            if scored_payable(row)
            and row["labels"]["sarcasm"]
            and row["labels"]["sentiment"] != "negative"
        ],
        *strings("t1.sarcasm"),
    )
    plan(
        "t1_brands",
        "t1",
        "metrics.sov.sample.rows",
        [row for row in comments if row["brands_r1"]],
        *strings("t1.brands"),
    )
    plan(
        "t1_text_less",
        "t1",
        "metrics.volume.comments.text_less",
        [row for row in comments if row["empty_text"]],
        *strings("t1.text_less"),
    )

    for aspect in ASPECTS:
        plan(
            f"t2_{aspect}",
            "t2",
            f"metrics.aspect_share.by_sample.payable.labels.{aspect}",
            [row for row in comments if scored_payable(row) and aspect in row["labels"]["intents"]],
            *strings(f"aspect.{aspect}"),
        )

    for name in sorted(segments):
        plan(
            f"t3_{name}",
            "t3",
            f"cuts.comment_by_segment.{name}.payable.rows",
            [
                row
                for row in comments
                if not row["empty_text"] and of_segment.get(row["channel"]) == name
            ],
            *strings(f"segment.{name}"),
        )

    for brand, by_sentiment in sorted(dig(record, "cuts.brand_by_sentiment.rows").items()):
        plans.append(
            {
                "key": f"t4_{brand}",
                "tab": "t4",
                "count_path": None,
                "count": sum(by_sentiment.values()),
                "count_reading": f"cuts.brand_by_sentiment.rows.{brand} (summed over its sentiments)",
                "rows": [
                    row for row in comments if scored_payable(row) and brand in row["brands_r1"]
                ],
                "label": (brand, brand),
            }
        )

    plan(
        "t5_positions",
        "t5",
        "metrics.promo_pressure.position_rows",
        positions,
        *strings("common.positions"),
    )
    plan(
        "t5_depth",
        "t5",
        "metrics.promo_depth.readings.from_price_pair.n",
        [row for row in positions if row["position"]["depth"] is not None],
        *strings("t5.reading.from_price_pair"),
    )

    for entry in plans:
        if "count" not in entry:
            entry["count"] = dig(record, entry["count_path"])
            entry["count_reading"] = entry["count_path"]
        if len(entry["rows"]) != entry["count"]:
            raise SystemExit(
                f"drill-down `{entry['key']}`: the store holds {len(entry['rows'])} rows and"
                f" `{entry['count_reading']}` says {entry['count']} — the sample under a figure"
                " must be drawn from the population that figure was computed over. Stop and report."
            )
    return plans


def draw(plan: dict) -> list[dict]:
    """`DRAW` rows of one population, by lot, seeded per expander and sorted for the page."""
    pool = sorted(
        plan["rows"], key=lambda row: (row["channel"], row.get("msg_id", 0), row.get("row_id", ""))
    )
    picked = random.Random(f"{SEED}:{plan['key']}").sample(pool, min(DRAW, len(pool)))
    return sorted(picked, key=lambda row: pool.index(row))


def ranks(plan: dict, drawn: list[dict]) -> list[int]:
    """Where the drawn rows sat in their sorted pool — what a draw's test must look at."""
    pool = sorted(
        plan["rows"], key=lambda row: (row["channel"], row.get("msg_id", 0), row.get("row_id", ""))
    )
    return [pool.index(row) for row in drawn]


def link_of(row: dict, *, comment: bool) -> str | None:
    """A t.me link the row's own fields prove, or none.

    A comment's `msg_id` lives in the linked discussion group's id space — the row carries no proof
    that a deep link to it resolves — so a comment links to the POST it replies to, which its
    `parent_msg_id` names in the channel's own space. Position and post rows link to themselves.
    """
    handle = row["channel"].lstrip("@")
    message = row["parent_msg_id"] if comment else row["msg_id"]
    return f"https://t.me/{handle}/{message}" if message else None


# --- charts ---------------------------------------------------------------------------------------


def bar_path(x: float, y: float, width: float, height: float, radius: float = 4) -> str:
    """A bar anchored flat on the baseline with its far end rounded."""
    radius = min(radius, max(width, 0.01))
    return (
        f"M{x:.1f},{y:.1f} h{width - radius:.1f} a{radius},{radius} 0 0 1 {radius},{radius}"
        f" v{height - 2 * radius:.1f} a{radius},{radius} 0 0 1 {-radius},{radius}"
        f" H{x:.1f} Z"
    )


def hbars(
    items: list[dict],
    *,
    width: int = 560,
    row_height: int = 26,
    hue: str | None = None,
    label_width: int = 150,
    value_room: int = 90,
) -> str:
    """Horizontal bars in one hue — the comparison form. Every bar carries its value at its end.

    One axis, no second scale, and the bars are anchored to it. Colour follows the entity through
    each item's own `color`, never the sort order; where a single hue is asked for, `hue` sets it
    for all of them.
    """
    plot = width - label_width - value_room
    top = max(value["value"] for value in items) if items else 0
    height = row_height * len(items) + 10
    parts = [
        f'<svg class="chart" viewBox="0 0 {width} {height}" role="img"'
        f' preserveAspectRatio="xMinYMin meet">',
        f'<line x1="{label_width}" y1="4" x2="{label_width}" y2="{height - 8}"'
        ' stroke="var(--axis)" stroke-width="1"/>',
    ]
    for index, item in enumerate(items):
        y = 6 + index * row_height
        span = (item["value"] / top * plot) if top else 0
        colour = item.get("color") or hue or "var(--s1)"
        parts.append(
            f'<text class="tick" x="{label_width - 8}" y="{y + 13}" text-anchor="end">'
            f"{item['label']}</text>"
        )
        parts.append(
            f'<g class="mark"{item["tip"]}>'
            f'<rect x="{label_width}" y="{y}" width="{plot}" height="{row_height - 6}"'
            ' fill="transparent"/>'
            f'<path d="{bar_path(label_width, y, max(span, 1), row_height - 6)}"'
            f' fill="{colour}"/></g>'
        )
        parts.append(
            f'<text class="value" x="{label_width + span + 8}" y="{y + 13}">{item["text"]}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)


def diverging(
    items: list[dict], *, width: int = 560, row_height: int = 28, label_width: int = 150
) -> str:
    """Sentiment as an ordered scale: negative left of the neutral block, positive right of it.

    The neutral block is centred, so the bars line up on the midpoint rather than on zero — which is
    what makes two rows comparable when their neutral mass differs. A segment is labelled only when
    it is wide enough to hold its own label; the rest is in the tooltip.

    ONE scale for every row, and it is set by the row that reaches furthest from the midpoint rather
    than by the full width: a row that is all negative reaches half a plot to the left, and a scale
    that ignored it drew that bar straight through the label column.
    """
    gutter = 48
    plot = width - label_width - 20 - 2 * gutter
    height = row_height * len(items) + 12
    middle = label_width + gutter + plot / 2
    reach = (
        max(
            (
                max(one["negative"], one["positive"]) + one["neutral"] / 2
                for one in items
                if one["scored"]
            ),
            default=1,
        )
        or 1
    )
    scale = (plot / 2) / reach
    parts = [
        f'<svg class="chart" viewBox="0 0 {width} {height}" role="img"'
        f' preserveAspectRatio="xMinYMin meet">',
        f'<line x1="{middle}" y1="4" x2="{middle}" y2="{height - 8}" stroke="var(--grid)"'
        ' stroke-width="1"/>',
    ]
    for index, item in enumerate(items):
        y = 8 + index * row_height
        bar = row_height - 8
        negative, neutral, positive = item["negative"], item["neutral"], item["positive"]
        if item["scored"]:
            widths = [share * scale for share in (negative, neutral, positive)]
        else:
            widths = [0, 0, 0]
        x = middle - widths[1] / 2 - widths[0]
        emphasis = ' font-weight="650" fill="var(--ink)"' if item.get("emphasis") else ""
        parts.append(
            f'<text class="tick" x="{label_width - 8}" y="{y + 13}" text-anchor="end"'
            f"{emphasis}>{item['label']}</text>"
        )
        parts.append(
            f'<g class="mark"{item["tip"]}>'
            f'<rect x="{label_width}" y="{y - 2}" width="{plot + 2 * gutter}"'
            f' height="{bar + 4}" fill="transparent"/>'
        )
        for share, colour in zip(
            widths, ("var(--neg)", "var(--mid)", f"var(--{POSITIVE_POLE})"), strict=True
        ):
            if share > 0:
                parts.append(
                    f'<rect x="{x:.1f}" y="{y}" width="{max(share - 2, 0.8):.1f}"'
                    f' height="{bar}" rx="2" fill="{colour}"/>'
                )
            x += share
        parts.append("</g>")
        if not item["scored"]:
            parts.append(
                f'<text class="value" x="{middle + 6}" y="{y + 13}">{item["empty"]}</text>'
            )
        else:
            for share, offset, text in (
                (negative, -widths[1] / 2 - widths[0] - 6, item["neg_text"]),
                (positive, widths[1] / 2 + widths[2] + 6, item["pos_text"]),
            ):
                if share * scale >= 26:
                    anchor = "end" if offset < 0 else "start"
                    parts.append(
                        f'<text class="value" x="{middle + offset:.1f}" y="{y + 13}"'
                        f' text-anchor="{anchor}">{text}</text>'
                    )
    parts.append("</svg>")
    return "".join(parts)


def quartile_band(
    readings: list[dict], *, width: int = 660, row_height: int = 46, label_width: int = 210
) -> str:
    """min–max as a hairline, q1–q3 as a band, the median as the one labelled tick."""
    plot = width - label_width - 40
    height = row_height * len(readings) + 24
    top = max((one["max"] or 0) for one in readings) or 1
    parts = [
        f'<svg class="chart" viewBox="0 0 {width} {height}" role="img"'
        f' preserveAspectRatio="xMinYMin meet">'
    ]
    for step in range(5):
        x = label_width + plot * step / 4
        parts.append(
            f'<line x1="{x:.1f}" y1="6" x2="{x:.1f}" y2="{height - 22}"'
            ' stroke="var(--grid)" stroke-width="1"/>'
        )
        parts.append(
            f'<text class="tick" x="{x:.1f}" y="{height - 6}" text-anchor="middle">'
            f"{pct(top * step / 4, 0)}</text>"
        )
    for index, one in enumerate(readings):
        y = 10 + index * row_height
        parts.append(
            f'<text class="tick" x="{label_width - 8}" y="{y + 18}" text-anchor="end">'
            f"{one['label']}</text>"
        )
        if not one["n"]:
            parts.append(
                f'<text class="value" x="{label_width + 4}" y="{y + 18}">{one["empty"]}</text>'
            )
            continue
        scale = plot / top
        low, high = one["min"] * scale, one["max"] * scale
        first, third = one["q1"] * scale, one["q3"] * scale
        median = one["median"] * scale
        parts.append(
            f'<g class="mark"{one["tip"]}>'
            f'<rect x="{label_width}" y="{y - 2}" width="{plot}" height="{row_height - 8}"'
            ' fill="transparent"/>'
            f'<line x1="{label_width + low:.1f}" y1="{y + 12}"'
            f' x2="{label_width + high:.1f}" y2="{y + 12}" stroke="var(--axis)"'
            ' stroke-width="1"/>'
            f'<path d="{bar_path(label_width + first, y + 4, max(third - first, 2), 17)}"'
            f' fill="{one["color"]}" opacity="0.85"/>'
            f'<line x1="{label_width + median:.1f}" y1="{y}"'
            f' x2="{label_width + median:.1f}" y2="{y + 25}" stroke="var(--ink)"'
            ' stroke-width="2"/></g>'
        )
        parts.append(
            f'<text class="value" x="{label_width + median + 6:.1f}" y="{y - 1}">'
            f"{one['median_text']}</text>"
        )
    parts.append("</svg>")
    return "".join(parts)


def legend(entries: list[tuple[str, str]]) -> str:
    swatches = "".join(
        f'<span class="key"><i style="background:{colour}"></i>{label}</span>'
        for colour, label in entries
    )
    return f'<div class="legend">{swatches}</div>'


# --- the page's blocks ----------------------------------------------------------------------------


class Page:
    """The build. One instance renders one document from one export."""

    def __init__(
        self,
        record: dict,
        strings: Strings,
        dictionary: dict,
        evidence: dict,
        export_bytes: bytes,
        export_sha: str,
    ):
        self.record = record
        self.s = strings
        self.dictionary = {entry["id"]: entry for entry in dictionary["metrics"]}
        self.evidence = evidence
        self.brand_names = evidence["brand_names"]
        self.export_bytes = export_bytes
        self.export_sha = export_sha
        self.plans = {plan["key"]: plan for plan in drill_populations(record, evidence, strings)}
        self.draws = {key: draw(plan) for key, plan in self.plans.items()}

    # -- shared pieces ----------------------------------------------------------------------------

    def metric_help(self, metric_id: str) -> str:
        """The ⓘ beside a figure — the same words the T8 glossary renders, from one file."""
        entry = self.dictionary[metric_id]
        texts = []
        for language in ("ua", "en"):
            pitfalls = " · ".join(entry["pitfalls"][language])
            texts.append(
                f"{entry['definition'][language]} — {entry['how_to_read'][language]}"
                f" [{entry['formula']}] · {pitfalls}"
            )
        return f'<button class="info" type="button"{tip(*texts)} aria-label="info">ⓘ</button>'

    def metric_name(self, metric_id: str) -> str:
        entry = self.dictionary[metric_id]
        return bi(esc(entry["name"]["ua"]), esc(entry["name"]["en"]))

    def sample_line(self, block: dict) -> str:
        """What a rate was measured ON, beside the rate — never inferred by the reader."""
        rows = block.get("rows")
        counted = f" — {num(rows)} {{}}" if rows is not None else ""
        ua, en = self.s("common.sample")
        rows_ua, rows_en = self.s("common.rows")
        of = f" {num(block['of'])}" if "of" in block else ""
        head_ua = f"{ua}: {block['name']}{counted.format(rows_ua)}"
        head_en = f"{en}: {block['name']}{counted.format(rows_en)}"
        if of:
            among_ua, among_en = self.s("common.of")
            head_ua, head_en = f"{head_ua} {among_ua}{of}", f"{head_en} {among_en}{of}"
        note = f'<span class="quote">{esc(block["reading"])}</span>'
        return (
            f'<p class="sample">{bi(esc(head_ua), esc(head_en))}'
            f"{self.s.html('common.export_prose_note', cls='hint')}{note}</p>"
        )

    def drill(self, key: str) -> str:
        """The trust feature: seed-drawn rows under the figure they stand on.

        The summary names the POPULATION as well as its size: several expanders sit under one
        heading on T1, and «10 of 553» twice over says nothing about which 553.
        """
        plan, rows = self.plans[key], self.draws[key]
        caption = self.s.html(
            "drill.caption", drawn=num(len(rows)), population=num(plan["count"]), seed=SEED
        )
        named = bi(esc(plan["label"][0]), esc(plan["label"][1]))
        comment = plan["tab"] != "t5"
        body = "".join(self.drill_row(row, comment=comment) for row in rows)
        # an empty population is a state, not a missing block: it opens and says so
        if not rows:
            body = f'<p class="empty">{self.s.html("common.no_rows")}</p>'
        note = f'<p class="hint">{self.s.html("drill.link.comment_note")}</p>' if comment else ""
        return (
            f'<details class="drill"><summary>{self.s.html("drill.open")}'
            f'<span class="pop">{named} · {caption}</span></summary>'
            f'<p class="hint">{self.s.html("drill.method")}'
            f'<span class="path">{esc(plan["count_reading"])}</span></p>{note}'
            f"{body}</details>"
        )

    def drill_row(self, row: dict, *, comment: bool) -> str:
        return self.comment_row(row) if comment else self.position_row(row)

    def comment_row(self, verdict: dict) -> str:
        text = summary.comment_text(verdict["row"])
        labels = verdict["labels"] or {}
        segments = dig(self.record, "cuts.comment_by_segment")
        segment = next(
            (
                name
                for name, card in segments.items()
                if verdict["channel"] in card["channels_with_a_row"]
            ),
            None,
        )
        aspects = ", ".join(labels.get("intents") or []) or None
        none_ua, none_en = self.s("drill.none")
        fields = [
            (
                self.s.html("common.positive")
                if labels.get("sentiment") == "positive"
                else self.s.html("common.negative")
                if labels.get("sentiment") == "negative"
                else self.s.html("common.neutral")
            ),
            f"{self.s.html('drill.sarcasm')}: {'✓' if labels.get('sarcasm') else '—'}",
            f"{self.s.html('drill.aspects')}: {esc(aspects) if aspects else bi(none_ua, none_en)}",
            f"{self.s.html('drill.brands')}: "
            f"{esc(', '.join(verdict['brands'])) if verdict['brands'] else bi(none_ua, none_en)}",
        ]
        link = link_of(verdict, comment=True)
        body = (
            f'<p class="text">{esc(text)}</p>'
            if text.strip()
            else f'<p class="text empty">{self.s.html("drill.empty_text")}</p>'
        )
        return (
            f'<article class="row">{body}'
            f'<p class="verdict">{" · ".join(fields)}</p>'
            f'<p class="meta">{esc(verdict["channel"])}'
            f"{' · ' + esc(segment) if segment else ''} · {esc(verdict['language'])}"
            f"{self.row_link(link)}</p></article>"
        )

    def position_row(self, row: dict) -> str:
        one = row["position"]
        # SPEC 3.22 (1): the depth a ROW prints is the PRINTED badge's reading, never the
        # arithmetic one of 3.17 (3) — `promo / (1 − arithmetic depth)` beside this row's own
        # promo price returns the extracted old price to the kopiyka, and that is the number
        # 3.17 (3) and 3.18 (7) keep off every surface. The arithmetic reading survives where no
        # row's price sits beside it: `metrics.promo_depth.readings.from_price_pair`.
        # `is not None` and not truthiness — a printed 0% badge is a fact, and absent is not zero.
        printed = one["discount_pct_printed"]
        parts = [
            f"{key}: {value}"
            for key, value in (
                ("brand", one["brand_raw"] or one["brand_id"]),
                ("line", one["line"]),
                ("category", one["category"]),
                ("size", f"{one['size_value']}{one['size_unit']}" if one["size_value"] else None),
                ("promo", one["price_promo"]),
                ("printed", printed),
                ("depth", pct(printed / 100, 2) if printed is not None else None),
                ("tier", row["tier"]),
            )
            if value not in (None, "")
        ]
        note = (
            f'<p class="hint">{self.s.html("drill.leaflet_note")}</p>'
            if one["carrier"] == "leaflet_page"
            else ""
        )
        return (
            f'<article class="row">{note}'
            f'<p class="verdict">{esc(" · ".join(parts))}</p>'
            f'<p class="meta">{esc(row["channel"])} · {esc(one["carrier"])}'
            f"{self.row_link(link_of(row, comment=False))}</p></article>"
        )

    def row_link(self, href: str | None, *, lead: bool = True) -> str:
        """The row's evidence link. `lead` is the separator it needs INSIDE a line of meta text and
        must not have when it is a table cell of its own."""
        if not href:
            return ""
        return (
            f'{" · " if lead else ""}<a href="{esc(href)}" rel="noreferrer noopener"'
            f' target="_blank">{self.s.html("drill.link")}</a>'
        )

    def stub(self, name: str) -> str:
        """One of the export's own honest gaps, with the condition that would unlock it."""
        entry = dig(self.record, f"not_computable.{name}")
        return (
            f'<div class="stub"><p class="stub-head">{self.s.html("stub.not_computable")}'
            f'<span class="path">{esc(name)}</span></p>'
            f'<p><b>{self.s.html("stub.reason")}:</b> <span class="quote">'
            f"{esc(entry['reason'])}</span></p>"
            f'<p><b>{self.s.html("stub.unlock")}:</b> <span class="quote">'
            f"{esc(entry['unlock'])}</span></p></div>"
        )

    def gap(self, key: str) -> str:
        """A surface the contract names that the export has no field for — 6a's backlog, on screen."""
        field = next(path for _, name, path in GAPS if name == key)
        return (
            f'<div class="stub gap"><p class="stub-head">{self.s.html(key)}'
            f'<span class="tag">{self.s.html("stub.gap")}</span></p>'
            f"<p>{self.s.html('stub.gap.note')}</p>"
            f'<p><b>{self.s.html("stub.gap.needs")}:</b> <span class="path">{esc(field)}</span>'
            f"</p></div>"
        )

    # -- T0 ---------------------------------------------------------------------------------------

    def insights(self) -> str:
        """Three readings, generated by fixed rules from the export — SPEC 3.20 (4)."""
        cards = [self.insight_text_less(), self.insight_aspect(), self.insight_segment()]
        stands = self.s.html("t0.insights.stands_on")
        body = "".join(
            f'<li>{text}<p class="path">{stands}: {esc(" · ".join(paths))}</p></li>'
            for text, paths in cards
        )
        return (
            f'<section class="insights"><h3>{self.s.html("t0.insights")}</h3>'
            f'<p class="hint">{self.s.html("t0.insights.note")}</p><ol>{body}</ol></section>'
        )

    def insight_text_less(self):
        volume, nsr = dig(self.record, "metrics.volume"), dig(self.record, "metrics.nsr.by_sample")
        return self.s.html(
            "t0.insight.text_less",
            text_less=num(volume["comments"]["text_less"]),
            bought=num(volume["comments"]["bought"]),
            nsr_bought=pct(nsr["bought"]["nsr"], 2, sign=True),
            nsr_payable=pct(nsr["payable"]["nsr"], 2, sign=True),
        ), (
            "metrics.volume.comments.text_less",
            "metrics.volume.comments.bought",
            "metrics.nsr.by_sample.bought.nsr",
            "metrics.nsr.by_sample.payable.nsr",
        )

    def insight_aspect(self):
        block = dig(self.record, "metrics.aspect_share.by_sample.payable")
        order = sorted(block["labels"], key=lambda name: (-block["labels"][name], name))
        top, second = order[0], order[1]
        return self.s.html(
            "t0.insight.dominant_aspect",
            top_aspect=self.s(f"aspect.{top}"),
            top_share=pct(block["share"][top]),
            top_labels=num(block["labels"][top]),
            second_aspect=self.s(f"aspect.{second}"),
            second_labels=num(block["labels"][second]),
        ), (
            "metrics.aspect_share.by_sample.payable.labels",
            "metrics.aspect_share.by_sample.payable.share",
        )

    def insight_segment(self):
        rated = [
            (
                name,
                self.nsr_of(card["payable"]["scored"], card["payable"]["sentiment"]),
                card["payable"]["rows"],
            )
            for name, card in dig(self.record, "cuts.comment_by_segment").items()
            if card["payable"]["scored"]
        ]
        coldest = min(rated, key=lambda one: (one[1], one[0]))
        warmest = max(rated, key=lambda one: (one[1], one[0]))
        # the sentence states how many segments are negative rather than asserting that this one is
        # the only one: a rule may only claim what it counted, and «the only segment» was true of
        # window-1 and guaranteed by nothing
        return self.s.html(
            "t0.insight.coldest_segment",
            rated=num(len(rated)),
            negatives=num(sum(1 for one in rated if one[1] < 0)),
            segment=self.s(f"segment.{coldest[0]}"),
            nsr=pct(coldest[1], 2, sign=True),
            rows=num(coldest[2]),
            warmest=self.s(f"segment.{warmest[0]}"),
            warmest_nsr=pct(warmest[1], 2, sign=True),
        ), (
            "cuts.comment_by_segment.*.payable.sentiment",
            "cuts.comment_by_segment.*.payable.scored",
        )

    @staticmethod
    def nsr_of(scored: int, counts: dict):
        """The dictionary's own formula, over the export's counts. `None` over no rows: a rate that
        nothing was measured on is not zero."""
        if not scored:
            return None
        return (counts.get("positive", 0) - counts.get("negative", 0)) / scored

    def kpi(self, metric_id: str, value: str, context: str, beside: str = "") -> str:
        window2 = self.s.html("common.delta.next_window")
        return (
            f'<article class="tile"><h3>{self.metric_name(metric_id)}'
            f"{self.metric_help(metric_id)}</h3>"
            f'<p class="figure">{value}</p>'
            f"{f'<p class=beside>{beside}</p>' if beside else ''}"
            f'<p class="context">{context}</p>'
            f'<p class="status"><span class="delta">Δ {window2}</span>'
            f'<span class="threshold">{self.s.html("common.status.no_threshold")}</span></p>'
            f"</article>"
        )

    def tab_t0(self) -> str:
        volume = dig(self.record, "metrics.volume")
        nsr = dig(self.record, "metrics.nsr.by_sample")
        negative = dig(self.record, "metrics.negative_share_sarcasm_adjusted.by_sample.payable")
        sov = dig(self.record, "metrics.sov")
        depth = dig(self.record, "metrics.promo_depth.readings.from_price_pair")
        coverage = dig(self.record, "metrics.coverage")
        own = sov["by_sample"]["payable"]["own_brands"][0]
        bought_name = nsr["bought"]["sample"]["name"]
        tiles = [
            self.kpi(
                "volume",
                num(volume["comments"]["payable"]),
                self.s.html("t0.kpi.context.volume"),
                beside=esc(
                    f"{num(volume['comments']['text_less'])} · "
                    f"{num(volume['leaflet_pages'])} · {num(volume['post_texts'])}"
                ),
            ),
            self.kpi(
                "nsr",
                pct(nsr["payable"]["nsr"], 2, sign=True),
                self.s.html("t0.kpi.context.two_samples"),
                beside=esc(f"{bought_name} {pct(nsr['bought']['nsr'], 2, sign=True)}"),
            ),
            self.kpi(
                "negative_share_sarcasm_adjusted",
                pct(negative["negative_share_sarcasm_adjusted"], 2),
                self.s.html("t0.kpi.context.two_samples"),
                beside=f"{esc(pct(negative['negative_share'], 2))} "
                f"{self.s.html('t0.kpi.beside.raw_negative')}",
            ),
            self.kpi(
                "sov",
                pct(sov["by_sample"]["payable"]["share"][own], 2),
                self.s.html("t0.kpi.context.sov"),
                beside=esc(self.brand_names.get(own, own)),
            ),
            self.kpi(
                "promo_depth",
                pct(depth["median"], 2),
                self.s.html("t0.kpi.context.depth"),
                beside=esc(f"{pct(depth['q1'], 1)} – {pct(depth['q3'], 1)}"),
            ),
            self.kpi(
                "coverage",
                f"{num(coverage['channels']['with_a_row'])}"
                f"/{num(coverage['channels']['in_registry'])}",
                self.s.html("t0.kpi.context.coverage"),
                beside=esc(
                    f"{num(coverage['segments']['with_a_row'])}"
                    f"/{num(coverage['segments']['in_registry'])}"
                ),
            ),
        ]
        return (
            f'<p class="lead">{self.s.html("t0.lead")}</p>'
            f'<div class="tiles">{"".join(tiles)}</div>'
            f"{self.insights()}"
            f"{self.stub('trend_vs_previous_window')}"
        )

    # -- T1 ---------------------------------------------------------------------------------------

    def sentiment_row(self, label: str, scored: int, counts: dict, extra: str = "") -> dict:
        """One diverging bar. `scored` and `counts` are passed apart on purpose: the export holds
        the three classes at the top of a metric block and under `sentiment` in a cut, and a reader
        that guessed which shape it had would silently draw an empty bar for the other one."""
        shares = {
            name: (counts.get(name, 0) / scored if scored else 0)
            for name in ("negative", "neutral", "positive")
        }
        empty_ua, empty_en = self.s("common.no_rows")
        reading = (
            f"{label}: {num(counts.get('negative', 0))} − / "
            f"{num(counts.get('neutral', 0))} = / {num(counts.get('positive', 0))} + "
            f"{extra}".strip()
        )
        return {
            "label": label,
            "scored": scored,
            "empty": bi(empty_ua, empty_en),
            "neg_text": pct(shares["negative"]),
            "pos_text": pct(shares["positive"]),
            "tip": tip(reading, reading),
            **shares,
        }

    def tab_t1(self) -> str:
        by_sample = dig(self.record, "metrics.nsr.by_sample")
        rows = [
            self.sentiment_row(
                name,
                block["scored"],
                {kind: block[kind] for kind in SENTIMENT},
                f"NSR {pct(block['nsr'], 2, sign=True)}",
            )
            for name, block in sorted(by_sample.items())
        ]
        brand_rows = dig(self.record, "cuts.brand_by_sentiment.rows")
        own = dig(self.record, "metrics.sov.by_sample.payable.own_brands")
        ranked_brands = sorted(brand_rows.items(), key=lambda one: (-sum(one[1].values()), one[0]))
        # emphasis, not hue: the three colours of this chart are the ordered scale itself and may
        # not be spent on which brand matters. The own brand is emphasised in the label, and the
        # accent hue does its work one chart down, where SoV has a hue to give away.
        brands_chart = [
            self.sentiment_row(self.brand_names.get(brand, brand), sum(counts.values()), counts)
            | {"emphasis": brand in own}
            for brand, counts in ranked_brands
        ]
        sov = dig(self.record, "metrics.sov.by_sample.payable")
        ranked = sorted(sov["share"].items(), key=lambda one: (-one[1], one[0]))
        sov_items = [
            {
                "label": esc(self.brand_names.get(brand, brand)),
                "value": share,
                "text": esc(f"{pct(share, 2)} · {num(sov['mentions'][brand])}"),
                "color": RAMP[4] if brand in own else "var(--muted)",
                "tip": tip(
                    f"{brand}: {sov['mentions'][brand]} mentions, {pct(share, 2)}",
                    f"{brand}: {sov['mentions'][brand]} mentions, {pct(share, 2)}",
                ),
            }
            for brand, share in ranked
            if share > 0
        ]
        reclassified = dig(
            self.record,
            "metrics.negative_share_sarcasm_adjusted.by_sample.payable.reclassified_from_sarcasm",
        )
        colours = [
            ("var(--neg)", self.s.html("common.negative")),
            ("var(--mid)", self.s.html("common.neutral")),
            (f"var(--{POSITIVE_POLE})", self.s.html("common.positive")),
        ]
        return "".join(
            [
                f"<h3>{self.s.html('t1.sentiment')}{self.metric_help('nsr')}</h3>",
                f'<p class="hint">{self.s.html("t1.sentiment.note")}</p>',
                legend(colours),
                diverging(rows),
                self.sample_line(dig(self.record, "metrics.nsr.sample")),
                self.drill("t1_negative"),
                self.drill("t1_positive"),
                f"<h4>{self.s.html('t1.text_less')}</h4>",
                f'<p class="badge">{num(dig(self.record, "metrics.volume.comments.text_less"))} '
                f"{self.s.html('t1.text_less.badge')}</p>",
                self.drill("t1_text_less"),
                f"<h3>{self.s.html('t1.sarcasm')}"
                f"{self.metric_help('negative_share_sarcasm_adjusted')}</h3>",
                f'<p class="badge">{self.s.html("t1.sarcasm.badge", reclassified=num(reclassified))}</p>',
                self.drill("t1_sarcasm"),
                f"<h3>{self.s.html('t1.brands')}</h3>",
                f'<p class="hint">{self.s.html("t1.brands.note")}</p>',
                legend(colours),
                diverging(brands_chart),
                f"<h3>{self.s.html('t1.sov')}{self.metric_help('sov')}</h3>",
                hbars(sov_items),
                self.sample_line(dig(self.record, "metrics.sov.sample")),
                f'<p class="hint">{self.s.html("t4.sample_warning")}</p>',
                self.drill("t1_brands"),
            ]
        )

    # -- T2 ---------------------------------------------------------------------------------------

    def tab_t2(self) -> str:
        block = dig(self.record, "metrics.aspect_share.by_sample.payable")
        items = []
        for aspect in sorted(ASPECTS, key=lambda name: (-block["labels"][name], name)):
            label_ua, label_en = self.s(f"aspect.{aspect}")
            reading = (
                f"{label_ua} / {label_en}: {block['labels'][aspect]}, "
                f"{pct(block['share'][aspect], 2)}"
            )
            items.append(
                {
                    "label": bi(esc(label_ua), esc(label_en), tag="tspan"),
                    "value": block["labels"][aspect],
                    "text": esc(
                        f"{num(block['labels'][aspect])} · {pct(block['share'][aspect], 2)}"
                    ),
                    "color": RAMP[4],
                    "tip": tip(reading, reading),
                }
            )
        no_aspect = (
            f'<p class="badge">{num(block["rows_with_no_aspect"])} '
            f"{self.s.html('t2.no_aspect')}</p>"
        )
        drills = "".join(
            f"<h4>{self.s.html(f'aspect.{aspect}')}</h4>{self.drill(f't2_{aspect}')}"
            for aspect in ASPECTS
        )
        return "".join(
            [
                f"<h3>{self.s.html('t2.aspects')}{self.metric_help('aspect_share')}</h3>",
                f'<p class="hint">{self.s.html("t2.aspects.note")}</p>',
                hbars(items),
                no_aspect,
                self.sample_line(dig(self.record, "metrics.aspect_share.sample")),
                f'<p class="hint">{self.s.html("t2.price_origin")}</p>',
                drills,
                self.gap("t2.gap.brand_aspect"),
                self.gap("t2.gap.negative_profile"),
            ]
        )

    # -- T3 ---------------------------------------------------------------------------------------

    def segment_card(self, name: str, card: dict) -> str:
        payable, bought = card["payable"], card["bought"]
        if payable["rows"]:
            state = "talked"
        elif card["channels_with_a_row"]:
            state = "evidence_only"
        else:
            state = "silent"
        aspects = sorted(
            payable["intents"]["frequency"].items(), key=lambda one: (-one[1], one[0])
        )[:3]
        top = " · ".join(
            f"{self.s(f'aspect.{aspect}')[0]} {num(count)}" for aspect, count in aspects
        )
        top_en = " · ".join(
            f"{self.s(f'aspect.{aspect}')[1]} {num(count)}" for aspect, count in aspects
        )
        rate = payable["sarcasm"]["rate"]
        nsr = self.nsr_of(payable["scored"], payable["sentiment"])
        chart = diverging(
            [
                self.sentiment_row(
                    "",
                    payable["scored"],
                    payable["sentiment"],
                    f"NSR {pct(nsr, 2, sign=True)}" if nsr else "",
                )
            ],
            width=380,
            label_width=8,
        )
        reading = (
            f'<p class="reading">{self.s.html("t3.reading.retail_official")}</p>'
            if name == "retail_official"
            else ""
        )
        return (
            f'<article class="card state-{state}">'
            f'<h4>{self.s.html(f"segment.{name}")}<span class="tag">'
            f"{self.s.html(f't3.state.{state}')}</span></h4>"
            f'<p class="figure">{num(payable["rows"])} <small>'
            f"{self.s.html('common.rows')}</small></p>"
            f'<p class="context">{num(bought["rows"])} {self.s.html("common.bought")} · '
            f"{self.s.html('t3.channels')}: {num(len(card['channels_with_a_row']))}"
            f"/{num(card['registry_channels'])}</p>"
            f'<p class="context">NSR {esc(pct(nsr, 2, sign=True))}</p>'
            f"{chart}"
            f'<p class="context">{self.s.html("t3.top_aspects")}: '
            f"{bi(esc(top), esc(top_en)) if aspects else self.s.html('common.no_rows')}</p>"
            f'<p class="context">{self.s.html("drill.sarcasm")}: '
            f"{pct(rate, 2) if rate is not None else self.s.html('common.not_measured')}</p>"
            f'<p class="meta">{esc(" · ".join(card["channels_with_a_row"])) or "—"}</p>'
            f"{reading}{self.drill(f't3_{name}')}</article>"
        )

    def tab_t3(self) -> str:
        cards = dig(self.record, "cuts.comment_by_segment")
        coverage = dig(self.record, "metrics.coverage.segments")
        rendered = "".join(self.segment_card(name, cards[name]) for name in sorted(cards))
        return "".join(
            [
                f"<h3>{self.s.html('t3.cards')}{self.metric_help('coverage')}</h3>",
                f'<p class="hint">{self.s.html("t3.cards.note")}</p>',
                f'<p class="badge">{num(coverage["with_a_row"])} / {num(coverage["in_registry"])} · '
                f"{pct(coverage['share'], 1)}</p>",
                f'<div class="cards">{rendered}</div>',
            ]
        )

    # -- T4 ---------------------------------------------------------------------------------------

    def tab_t4(self) -> str:
        sov = dig(self.record, "metrics.sov.by_sample.payable")
        sentiment = dig(self.record, "cuts.brand_by_sentiment.rows")
        pressure = dig(self.record, "metrics.promo_pressure")
        own = sov["own_brands"]
        head = "".join(
            [
                f'<th data-column="brand">{self.s.html("common.brand")}</th>',
                f'<th data-column="own">{self.s.html("t4.column.own")}</th>',
                f'<th data-column="mentions">{self.s.html("common.mentions")}</th>',
                f'<th data-column="sov">{self.s.html("t4.column.sov")}</th>',
                f'<th data-column="nsr">{self.s.html("t4.column.nsr")}</th>',
                # the promo column's head is the metric's own name; «SoV» and «NSR» beside it are
                # abbreviations the dictionary itself prints inside its names, not second definitions
                f'<th data-column="promo">{self.metric_name("promo_pressure")}</th>',
            ]
        )
        body = []
        top_sov = max(sov["share"].values()) or 1
        top_promo = max(pressure["share"].values()) or 1
        for brand in sorted(sov["mentions"], key=lambda name: (-sov["share"][name], name)):
            counts = sentiment.get(brand, {})
            scored = sum(counts.values())
            rate = self.nsr_of(scored, counts)
            promo = pressure["by_brand"].get(brand, 0)
            share = pressure["share"].get(brand, 0.0)
            drill = self.drill(f"t4_{brand}") if brand in sentiment else ""
            body.append(
                f'<tr data-brand="{esc(brand)}" data-own="{int(brand in own)}"'
                f' data-mentions="{sov["mentions"][brand]}" data-sov="{sov["share"][brand]}"'
                # a brand nobody said anything about has no NSR; -9 sorts it below every real
                # rate (which lives in [-1, 1]) instead of pretending it is a zero
                f' data-nsr="{rate if rate is not None else -9}" data-promo="{promo}">'
                f'<td class="name" title="{esc(brand)}">'
                f"{esc(self.brand_names.get(brand, brand))}{drill}</td>"
                f"<td>{self.s.html('t1.emphasis.own') if brand in own else ''}</td>"
                f'<td class="figure">{num(sov["mentions"][brand])}</td>'
                f"<td>{self.micro_bar(sov['share'][brand], pct(sov['share'][brand], 2), top_sov)}"
                f"</td>"
                f"<td>{self.micro_diverging(rate)}</td>"
                f"<td>{self.micro_bar(share, f'{num(promo)} · {pct(share, 1)}', top_promo)}</td>"
                f"</tr>"
            )
        return "".join(
            [
                f"<h3>{self.s.html('t4.table')}{self.metric_help('sov')}</h3>",
                f'<p class="hint">{self.s.html("t4.table.note")}</p>',
                self.sample_line(dig(self.record, "metrics.sov.sample")),
                f'<p class="hint">{self.s.html("t4.sample_warning")}</p>',
                f'<table class="sortable"><thead><tr>{head}</tr></thead>'
                f"<tbody>{''.join(body)}</tbody></table>",
                self.gap("t4.gap.private_label"),
            ]
        )

    @staticmethod
    def micro_bar(share: float, text: str, top: float) -> str:
        """A micro-bar scaled to its COLUMN's largest value — the column is the comparison."""
        width = max(share / top * 100, 0) if share else 0
        return (
            f'<span class="micro"><span class="track">'
            f'<i style="left:0;width:{width:.1f}%;background:{RAMP[4]}"></i></span>'
            f"<b>{esc(text)}</b></span>"
        )

    @staticmethod
    def micro_diverging(rate) -> str:
        if rate is None:
            return '<span class="micro diverging"><span class="track"></span><b>—</b></span>'
        width = min(abs(rate) * 50, 50)
        colour = f"var(--{POSITIVE_POLE})" if rate >= 0 else "var(--neg)"
        offset = 50 if rate >= 0 else 50 - width
        return (
            f'<span class="micro diverging"><span class="track">'
            f'<i style="left:{offset:.1f}%;width:{width:.1f}%;background:{colour}"></i>'
            f"</span><b>{esc(pct(rate, 1, sign=True))}</b></span>"
        )

    # -- T5 ---------------------------------------------------------------------------------------

    def tab_t5(self) -> str:
        depth = dig(self.record, "metrics.promo_depth")
        pressure = dig(self.record, "metrics.promo_pressure")
        empty_ua, empty_en = self.s("common.no_rows")
        readings = []
        for name in ("from_price_pair", "from_printed_badge"):
            one = depth["readings"][name]
            label_ua, label_en = self.s(f"t5.reading.{name}")
            reading = (
                f"{label_ua} / {label_en}: n={one['n']}, median {pct(one['median'] or 0, 2)},"
                f" q1 {pct(one['q1'] or 0, 2)}, q3 {pct(one['q3'] or 0, 2)}"
            )
            readings.append(
                {
                    "label": bi(
                        esc(f"{label_ua} · n={one['n']}"),
                        esc(f"{label_en} · n={one['n']}"),
                        tag="tspan",
                    ),
                    "color": RAMP[4] if name == "from_price_pair" else RAMP[2],
                    "median_text": esc(pct(one["median"], 2)) if one["n"] else "",
                    "empty": bi(empty_ua, empty_en),
                    "tip": tip(reading, reading),
                    **{key: one[key] for key in ("n", "min", "q1", "median", "q3", "max")},
                }
            )
        chains = []
        for chain in sorted(
            pressure["by_chain"],
            key=lambda name: (-pressure["by_chain"][name]["position_rows"], name),
        ):
            block = pressure["by_chain"][chain]
            label_ua, label_en = self.s(f"chain.{chain}")
            carriers = " · ".join(self.s(f"t5.carrier.{name}")[0] for name in block["by_carrier"])
            counted = " · ".join(
                f"{self.s(f't5.carrier.{name}')[0]} {count}"
                for name, count in sorted(block["by_carrier"].items())
            )
            counted_en = " · ".join(
                f"{self.s(f't5.carrier.{name}')[1]} {count}"
                for name, count in sorted(block["by_carrier"].items())
            )
            named = self.s("t5.named_by_law")
            marked = named[0] if block["named_by_amendment_3_20"] else ""
            marked_en = named[1] if block["named_by_amendment_3_20"] else ""
            chains.append(
                {
                    "label": bi(esc(label_ua), esc(label_en), tag="tspan"),
                    "value": block["position_rows"],
                    "text": esc(f"{num(block['position_rows'])} · {carriers}"),
                    "color": RAMP[4] if block["named_by_amendment_3_20"] else "var(--muted)",
                    "tip": tip(
                        f"{label_ua}: {counted} {marked}".strip(),
                        f"{label_en}: {counted_en} {marked_en}".strip(),
                    ),
                }
            )
        by_brand = pressure["by_brand"]
        brand_items = [
            {
                "label": esc(self.brand_names.get(brand, brand)),
                "value": count,
                "text": esc(f"{num(count)} · {pct(pressure['share'][brand], 1)}"),
                "color": RAMP[4],
                "tip": tip(f"{brand}: {count} positions", f"{brand}: {count} positions"),
            }
            for brand, count in sorted(by_brand.items(), key=lambda one: (-one[1], one[0]))
        ]
        return "".join(
            [
                # the heading IS the metric's name, read from the dictionary: a section title that
                # restated it would be the second home of a fact that has one (D4)
                f"<h3>{self.metric_name('promo_depth')}{self.metric_help('promo_depth')}</h3>",
                f'<p class="hint">{self.s.html("t5.depth.note")}</p>',
                quartile_band(readings),
                f'<p class="badge">{num(depth["printed_disagrees_with_computed"])} '
                f"{self.s.html('t5.disagree')}</p>",
                self.sample_line(dig(self.record, "metrics.promo_depth.sample")),
                self.drill("t5_depth"),
                self.stub("leaflet_depth_for_silpo_varus_marketopt"),
                f"<h3>{self.s.html('t5.pressure')}{self.metric_help('promo_pressure')}</h3>",
                f'<p class="hint">{self.s.html("t5.pressure.note")}</p>',
                hbars(chains, width=620, value_room=170),
                f'<p class="badge">{num(pressure["rows_with_no_resolved_brand"])} '
                f"{self.s.html('t5.no_brand')}</p>",
                f"<h3>{self.s.html('t5.pressure.brands')}</h3>",
                hbars(brand_items),
                self.drill("t5_positions"),
                self.positions_table(),
                f'<p class="hint">{self.s.html("t2.price_origin")}</p>',
            ]
        )

    # -- T5's positions table ---------------------------------------------------------------------

    POSITION_COLUMNS = (
        ("brand", "common.brand"),
        ("item", "t5.column.item"),
        ("chain", "t5.column.chain"),
        ("carrier", "t5.column.carrier"),
        ("promo", "t5.column.promo_price"),
        ("printed", "t5.column.printed"),
        ("depth", "t5.column.depth"),
        ("tier", "t5.column.tier"),
    )
    """(the `data-` key the sort reads, the heading's string key), in render order.

    The key is also what the filter selects match against, so a column and its filter cannot drift
    into two different attributes."""

    MISSING = -1.0
    """What a numeric `data-` attribute holds when the row carries no such figure.

    Not the empty string: `Number("")` is 0 in JS, so an absent promo price would sort as free.
    Every figure in these three columns is a price or a share and none can be negative, so -1 sorts
    them all below the cheapest real one — the same device as T4's -9 for a brand with no NSR."""

    @staticmethod
    def price(value) -> str:
        """A promo price as the leaflet prints it — two decimals, the currency in the heading."""
        return f"{value:.2f}" if value is not None else "—"

    @staticmethod
    def printed(value) -> str:
        """The badge as printed: a minus and a percent. `-N%` is the source's own mark."""
        return f"−{value:g}%" if value is not None else "—"

    def own_class(self, row: dict) -> str:
        """Ours, a competitor, or a trade mark the registry does not resolve — three states.

        The registry's watchlist is our brands and the competitors we track, so `own` answers the
        first two. It answers nothing about the 65 rows whose printed mark resolves to no watchlist
        id, and calling those competitors would be a claim the evidence does not carry.
        """
        if "id" not in row["brand"]:
            return "unresolved"
        return "own" if row["brand"]["own"] else "competitor"

    def item_cell(self, item: dict) -> str:
        """The product as recorded: its line, its pack size, its fat percentage — absent if absent."""
        size = ""
        if "size_value" in item:
            size = f"{item['size_value']:g} {item.get('size_unit', '')}".strip()
            if "pack_count" in item:
                size = f"{item['pack_count']:g} × {size}"
        parts = " · ".join(
            part
            for part in (
                item.get("line"),
                size,
                pct(item["attribute_pct"] / 100, 1) if "attribute_pct" in item else None,
            )
            if part
        )
        category = item.get("category")
        return (
            f"{esc(parts) if parts else '—'}{f'<small>{esc(category)}</small>' if category else ''}"
        )

    def position_filters(self, rows: list[dict]) -> str:
        """Four selects over the table's own values — brand, chain, carrier, ours vs competitors.

        The options are built from the rows THIS export carries, so a filter can never offer a
        value no row has; both languages of every option label are in the document as attributes and
        the language button swaps the text, the way it already swaps its own.
        """
        # `(casefold, itself)` and not `casefold` alone: «ПростоНаше» and «Простонаше» fold to the
        # same key, and a tie broken by a SET's iteration order is a page that differs between runs
        brands = sorted(
            {row["brand"]["display"] for row in rows}, key=lambda one: (one.casefold(), one)
        )
        chains = sorted({row["chain"]["id"] for row in rows})
        carriers = sorted({row["carrier"] for row in rows})
        classes = ("own", "competitor", "unresolved")
        controls = [
            ("brand", "common.brand", [(one, (one, one)) for one in brands]),
            ("chain", "t5.column.chain", [(one, self.s(f"chain.{one}")) for one in chains]),
            (
                "carrier",
                "t5.column.carrier",
                [(one, self.s(f"t5.carrier.{one}")) for one in carriers],
            ),
            ("own", "t5.filter.own", [(one, self.s(f"t5.own.{one}")) for one in classes]),
        ]
        blocks = []
        for key, label, options in controls:
            all_ua, all_en = self.s("t5.filter.all")
            rendered = [
                f'<option value="" data-ua="{esc(all_ua)}" data-en="{esc(all_en)}">{esc(all_ua)}</option>'
            ]
            rendered += [
                f'<option value="{esc(value)}" data-ua="{esc(ua)}" data-en="{esc(en)}">{esc(ua)}</option>'
                for value, (ua, en) in options
            ]
            blocks.append(
                f'<label class="filter">{self.s.html(label)}'
                f'<select data-filter-for="t5-positions" data-key="{key}">{"".join(rendered)}</select>'
                f"</label>"
            )
        return f'<div class="filters">{"".join(blocks)}</div>'

    def positions_table(self) -> str:
        """SPEC 3.21 (4): what is in promo, at what price, from which brand — all of it, as a table.

        Every cell is a field of `promo.positions_table.rows`; nothing here is recomputed from the
        store and nothing is derived from a price the export does not carry. The row's own evidence
        link is the last cell, so a reader can go from a line of this table to the post it came from.
        """
        table = dig(self.record, "promo.positions_table")
        rows = table["rows"]
        head = "".join(
            f'<th data-column="{key}">{self.s.html(label)}</th>'
            for key, label in self.POSITION_COLUMNS
        )
        head += f'<th class="plain">{self.s.html("t5.column.evidence")}</th>'
        body = []
        for row in rows:
            brand, item, chain = row["brand"], row["item"], row["chain"]
            own = self.own_class(row)
            tag = (
                f' <span class="tag">{self.s.html("t1.emphasis.own")}</span>'
                if own == "own"
                else ""
            )
            link = link_of(row["evidence"], comment=False)
            chain_name = self.s.html("chain." + chain["id"])
            carrier_name = self.s.html("t5.carrier." + row["carrier"])
            body.append(
                f'<tr data-brand="{esc(brand["display"])}" data-chain="{esc(chain["id"])}"'
                f' data-carrier="{esc(row["carrier"])}" data-own="{own}"'
                f' data-item="{esc(item.get("line") or "")}" data-tier="{esc(row["tier"])}"'
                f' data-promo="{row.get("promo_price", self.MISSING)}"'
                f' data-printed="{row.get("printed_pct", self.MISSING)}"'
                f' data-depth="{row.get("depth", self.MISSING)}">'
                f'<td class="name" title="{esc(brand.get("id", ""))}">'
                f"{esc(brand['display'])}{tag}</td>"
                f"<td>{self.item_cell(item)}</td>"
                f"<td>{chain_name}</td>"
                f"<td>{carrier_name}</td>"
                f'<td class="figure">{esc(self.price(row.get("promo_price")))}</td>'
                f"<td>{esc(self.printed(row.get('printed_pct')))}</td>"
                f"<td>{esc(pct(row.get('depth'), 2))}</td>"
                f"<td>{esc(row['tier'])}</td>"
                f'<td class="plain">{self.row_link(link, lead=False) or "—"}</td></tr>'
            )
        # the filtered-to-nothing state is a row of the table itself: «наші» selects zero rows in
        # window-1 and a tbody that just went blank is indistinguishable from a broken filter
        body.append(
            f'<tr class="none" hidden><td colspan="{len(self.POSITION_COLUMNS) + 1}">'
            f"{self.s.html('common.no_rows')}</td></tr>"
        )
        # which chains yielded PAGES and which only post texts — the census the export already
        # carries per chain, read from it rather than counted again over the rows
        by_chain = dig(self.record, "metrics.promo_pressure.by_chain")

        def chains_with(carrier: str, side: int) -> str:
            return ", ".join(
                self.s(f"chain.{chain}")[side]
                for chain, block in sorted(by_chain.items())
                if carrier in block["by_carrier"]
            )

        census = self.s.html(
            "t5.positions.carriers",
            leaflet=(chains_with("leaflet_page", 0), chains_with("leaflet_page", 1)),
            post=(chains_with("post_text", 0), chains_with("post_text", 1)),
        )
        return "".join(
            [
                f"<h3>{self.s.html('t5.positions')}</h3>",
                f'<p class="hint">{self.s.html("t5.positions.note")}</p>',
                self.sample_line(table["sample"]),
                f'<p class="hint">{census}</p>',
                self.position_filters(rows),
                f'<table id="t5-positions" class="sortable filtered wide">'
                f"<thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>",
            ]
        )

    # -- T6, T7 -----------------------------------------------------------------------------------

    def tab_t6(self) -> str:
        return self.stub("category_layer") + self.stub("reactions_views_votes")

    def tab_t7(self) -> str:
        mock = (
            f'<div class="mock"><p class="watermark">{self.s.html("t7.mock")}</p>'
            f"<h4>{self.s.html('t7.mock.title')}</h4>"
            f'<p class="hint">{self.s.html("t7.mock.note")}</p>'
            f'<div class="mock-alert"><b>{self.s.html("t7.mock.rule")}</b>'
            f"<code>share(sentiment, brand, window) − baseline(brand) &gt; threshold</code>"
            f"<p>{self.s.html('t7.mock.delivery')}</p></div></div>"
        )
        return mock + self.stub("alert_baselines") + self.stub("trend_vs_previous_window")

    # -- T8 ---------------------------------------------------------------------------------------

    def glossary(self) -> str:
        entries = []
        for metric_id, entry in sorted(self.dictionary.items()):
            pitfalls = "".join(
                f"<li>{bi(esc(ua), esc(en))}</li>"
                for ua, en in zip(entry["pitfalls"]["ua"], entry["pitfalls"]["en"], strict=True)
            )
            entries.append(
                f'<article class="glossary"><h4>{self.metric_name(metric_id)}</h4>'
                f"<p><b>{self.s.html('common.definition')}:</b> "
                f"{bi(esc(entry['definition']['ua']), esc(entry['definition']['en']))}</p>"
                f"<p><b>{self.s.html('common.how_to_read')}:</b> "
                f"{bi(esc(entry['how_to_read']['ua']), esc(entry['how_to_read']['en']))}</p>"
                f"<p><b>{self.s.html('common.formula')}:</b> <code>{esc(entry['formula'])}</code>"
                f" · <b>{self.s.html('common.from_export')}:</b> "
                f'<span class="path">{esc(entry["export_field"])}</span></p>'
                f"<p><b>{self.s.html('common.pitfalls')}:</b></p><ul>{pitfalls}</ul></article>"
            )
        return "".join(entries)

    def provenance_table(self) -> str:
        provenance = dig(self.record, "provenance")
        blocks = []
        for kind, key in (
            ("inputs", "t8.provenance.inputs"),
            ("producers", "t8.provenance.producers"),
            ("evidence", "t8.provenance.evidence"),
        ):
            rows = "".join(
                f'<tr><td class="path">{esc(name)}</td><td class="sha">{esc(sha[:16])}…</td></tr>'
                for name, sha in sorted(provenance[kind].items())
            )
            blocks.append(
                f'<h4>{self.s.html(key)}</h4><table class="prov"><tbody>{rows}</tbody></table>'
            )
        screens = "".join(
            f"<tr><td>{self.s.html(f'tab.{tab}')}</td>"
            f'<td class="path">{esc(" · ".join(paths))}</td></tr>'
            for tab, paths in TAB_SOURCES.items()
        )
        blocks.insert(
            0,
            f"<h4>{self.s.html('t8.provenance.screens')}</h4>"
            f'<table class="prov"><tbody>{screens}</tbody></table>',
        )
        return "".join(blocks)

    def gates_table(self) -> str:
        convergence = dig(self.record, "convergence")
        whole = convergence["whole_record"]
        rows = "".join(
            [
                f"<tr><td>{self.s.html('t8.gates.convergence')}</td>"
                f'<td class="figure">{num(whole["agreed"])} / {num(whole["leaves"])}</td></tr>',
                f"<tr><td>{self.s.html('t8.gates.shared')}</td>"
                f'<td class="figure">{num(len(convergence["shared_figures"]))}</td></tr>',
                f"<tr><td>{self.s.html('t8.gates.disagreed')}</td>"
                f'<td class="figure">{num(len(whole["disagreed"]))}</td></tr>',
            ]
        )
        return (
            f'<p class="hint">{self.s.html("t8.gates.note")}</p>'
            f'<table class="prov"><tbody>{rows}</tbody></table>'
            f'<p class="quote">{esc(convergence["reading"])}</p>'
            f"{self.gap('t8.gates.model')}"
        )

    def tab_t8(self) -> str:
        limits = "".join(
            f"<li>{self.s.html(key)}</li>"
            for key in (
                "t8.limits.reach",
                "t8.limits.one_window",
                "t8.limits.matcher",
                "t8.limits.collection",
                "t8.limits.numbers",
            )
        )
        stubs = "".join(self.stub(name) for name in NOT_COMPUTABLE_ORDER)
        return "".join(
            [
                f"<h3>{self.s.html('t8.glossary')}</h3>",
                f'<p class="hint">{self.s.html("t8.glossary.note")}</p>',
                self.glossary(),
                f"<h3>{self.s.html('t8.gates')}</h3>",
                self.gates_table(),
                f"<h3>{self.s.html('t8.provenance')}</h3>",
                f'<p class="hint">{self.s.html("t8.provenance.note")}</p>',
                self.provenance_table(),
                f'<h3>{self.s.html("t8.limits")}</h3><ul class="limits">{limits}</ul>',
                stubs,
                f"<h3>{self.s.html('t8.embedded')}</h3>",
                f'<p class="hint">{self.s.html("t8.embedded.note")}</p>',
            ]
        )

    # -- the document -----------------------------------------------------------------------------

    def banner(self) -> str:
        window = dig(self.record, "window")
        return (
            f'<p class="window">'
            f"{self.s.html('banner.window', days=num(window['days']), anchor=window['anchor'][:10], since=window['since'][:10], until=window['until'][:10])}"
            f' · <span class="sha">{self.s.html("banner.export", sha=self.export_sha[:16] + "…")}</span>'
            f" · {self.s.html('banner.built_from')}</p>"
        )

    def render(self) -> str:
        # the first tab is open and selected in the MARKUP, not by the script. `show()` toggles
        # both from here on, but a page whose only visible state arrives with the JS is a blank
        # command centre the moment anything in that script throws — and the acceptance sitting
        # opens this file cold.
        nav = "".join(
            f'<button class="tab-button" type="button" data-tab="{tab}"'
            f' aria-selected="{str(tab == TABS[0]).lower()}">'
            f"{self.s.html(f'tab.{tab}')}</button>"
            for tab in TABS
        )
        bodies = {
            "t0": self.tab_t0,
            "t1": self.tab_t1,
            "t2": self.tab_t2,
            "t3": self.tab_t3,
            "t4": self.tab_t4,
            "t5": self.tab_t5,
            "t6": self.tab_t6,
            "t7": self.tab_t7,
            "t8": self.tab_t8,
        }
        sections = "".join(
            f'<section class="tab{" active" if tab == TABS[0] else ""}" id="{tab}">'
            f"<h2>{self.s.html(f'tab.{tab}')}<small>{self.s.html(f'tab.question.{tab}')}</small></h2>"
            f"{self.banner()}{bodies[tab]()}</section>"
            for tab in TABS
        )
        title = self.s("app.title")[0]
        return "\n".join(
            [
                "<!doctype html>",
                '<html lang="uk" data-lang="ua" data-tab="t0">',
                "<head>",
                '<meta charset="utf-8">',
                '<meta name="viewport" content="width=device-width, initial-scale=1">',
                f"<title>{esc(title)}</title>",
                f"<style>{CSS.replace('__VARS__', css_vars())}</style>",
                "</head>",
                "<body>",
                f'<header><div class="brand"><h1>{self.s.html("app.title")}</h1>'
                f"<p>{self.s.html('app.subtitle')} — {self.s.html('app.owner')}</p></div>"
                f'<div class="toggles">'
                f'<button id="lang" type="button" data-ua="EN" data-en="UA">EN</button>'
                f'<button id="theme" type="button">{self.s.html("nav.theme")}</button>'
                f"</div></header>",
                f'<nav class="tabs">{nav}</nav>',
                f"<main>{sections}</main>",
                f"<footer><p>{self.s.html('footer.note')}</p>{self.banner()}</footer>",
                '<script type="application/json" id="export-data">',
                self.export_bytes.decode("utf-8"),
                "</script>",
                f"<script>{JS}</script>",
                "</body>",
                "</html>",
                "",
            ]
        )


def css_vars() -> str:
    light = ";".join(f"--{name}:{value[0]}" for name, value in PALETTE.items())
    dark = ";".join(f"--{name}:{value[1]}" for name, value in PALETTE.items())
    return (
        f":root{{{light}}}"
        f'@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{{dark}}}}}'
        f':root[data-theme="dark"]{{{dark}}}'
        f':root[data-theme="light"]{{{light}}}'
    )


CSS = """
__VARS__
*{box-sizing:border-box}
body{margin:0;background:var(--plane);color:var(--ink);
font-family:system-ui,-apple-system,"Segoe UI",sans-serif;font-size:15px;line-height:1.5}
h1{font-size:19px;margin:0}
h2{font-size:22px;margin:0 0 4px}
h2 small{display:block;font-size:14px;font-weight:400;color:var(--ink2);margin-top:2px}
h3{font-size:16px;margin:26px 0 6px}
h4{font-size:14px;margin:16px 0 4px}
header{display:flex;justify-content:space-between;align-items:center;gap:16px;padding:12px 20px;
background:var(--surface);border-bottom:1px solid var(--grid)}
header p{margin:2px 0 0;color:var(--ink2);font-size:13px}
.toggles{display:flex;gap:8px}
button{font:inherit;color:var(--ink);background:var(--surface);border:1px solid var(--axis);
border-radius:6px;padding:8px 12px;min-height:36px;cursor:pointer}
button:hover{border-color:var(--ink2)}
nav.tabs{display:flex;flex-wrap:wrap;gap:4px;padding:8px 20px;background:var(--surface);
border-bottom:1px solid var(--grid);position:sticky;top:0;z-index:5}
.tab-button{border:1px solid transparent;background:transparent;padding:8px 10px;min-height:44px}
.tab-button[aria-selected="true"]{background:var(--plane);border-color:var(--axis);font-weight:600}
main{padding:18px 20px 60px;max-width:1180px}
section.tab{display:none}
section.tab.active{display:block}
p.window{color:var(--muted);font-size:12px;margin:0 0 14px;font-variant-numeric:tabular-nums}
p.lead{color:var(--ink2);margin:0 0 12px}
p.hint{color:var(--ink2);font-size:13px;margin:4px 0 10px;max-width:78ch}
p.meta,span.path,.sha{color:var(--muted);font-size:12px}
span.path,code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;
overflow-wrap:anywhere}
span.quote{display:block;color:var(--muted);font-size:12px;margin-top:2px;max-width:90ch}
p.badge{display:inline-block;background:var(--surface);border:1px solid var(--grid);
border-radius:6px;padding:6px 10px;margin:8px 0;font-size:13px}
/* 175px and not 210: `main` is capped at 1180, so the row has 1140 to spend and six tiles at 210
   need 1310 — the KPI row wrapped 5 + 1 on every desktop. auto-fit still collapses it on narrow
   screens, and the mobile rule below still takes over at 720. */
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(175px,1fr));gap:10px}
.tile{background:var(--surface);border:1px solid var(--grid);border-radius:10px;padding:12px}
.tile h3{margin:0 0 6px;font-size:13px;color:var(--ink2);font-weight:600}
.figure{font-size:26px;font-weight:650;margin:0;font-variant-numeric:tabular-nums}
.figure small{font-size:13px;font-weight:400;color:var(--ink2)}
.beside{margin:0;color:var(--ink2);font-size:13px;font-variant-numeric:tabular-nums}
.context{margin:6px 0 0;color:var(--ink2);font-size:12px}
.status{margin:8px 0 0;font-size:11px;color:var(--muted);display:flex;
justify-content:space-between;gap:6px}
.insights{margin:24px 0}
.insights ol{padding-left:20px}
.insights li{margin-bottom:10px;max-width:86ch}
.stub{border:1px dashed var(--axis);border-radius:10px;padding:12px;margin:14px 0;
background:var(--surface)}
.stub p{margin:4px 0}
.stub-head{font-weight:600;display:flex;gap:8px;align-items:baseline;flex-wrap:wrap}
.stub.gap{border-style:solid;border-color:var(--warn)}
.tag{font-size:11px;color:var(--ink2);border:1px solid var(--grid);border-radius:20px;
padding:1px 8px}
.chart{width:100%;max-width:620px;height:auto;display:block;margin:6px 0}
.chart text{font-size:11px;fill:var(--muted);font-family:inherit}
.chart text.value{fill:var(--ink2);font-variant-numeric:tabular-nums}
.chart .mark{cursor:default}
.legend{display:flex;gap:14px;flex-wrap:wrap;font-size:12px;color:var(--ink2);margin:6px 0}
.legend i{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:5px}
.sample{font-size:12px;color:var(--ink2);margin:6px 0 2px;max-width:90ch}
span.hint{display:block;color:var(--ink2)}
.info{border:none;background:transparent;color:var(--muted);padding:0 6px;min-height:0;
cursor:help;font-size:13px}
#tip{position:fixed;z-index:20;max-width:44ch;background:var(--surface);color:var(--ink);
border:1px solid var(--axis);border-radius:8px;padding:8px 10px;font-size:12px;
box-shadow:0 6px 18px rgba(0,0,0,.16);display:none;pointer-events:none;line-height:1.4}
details.drill{margin:8px 0 16px;border-left:2px solid var(--grid);padding-left:10px}
details.drill summary{cursor:pointer;font-size:13px;color:var(--ink2);min-height:32px;
display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.pop{color:var(--muted);font-variant-numeric:tabular-nums}
.row{border-top:1px solid var(--grid);padding:8px 0}
.row .text{margin:0 0 4px;white-space:pre-wrap}
.row .text.empty{color:var(--muted);font-style:italic}
.row .verdict{margin:0;font-size:12px;color:var(--ink2)}
.row .meta{margin:2px 0 0}
a{color:var(--s1)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:10px}
.card{background:var(--surface);border:1px solid var(--grid);border-radius:10px;padding:12px}
.card h4{margin:0 0 4px;display:flex;gap:8px;align-items:baseline;flex-wrap:wrap}
.card.state-silent{border-style:dashed}
.reading{font-size:13px;color:var(--ink2);border-left:2px solid var(--axis);padding-left:8px;
margin:8px 0}
table{border-collapse:collapse;width:100%;max-width:900px;font-size:13px}
table.wide{max-width:none}
table.wide td small{display:block;color:var(--muted);font-size:11px}
.filters{display:flex;flex-wrap:wrap;gap:10px;margin:8px 0}
.filters label{display:flex;flex-direction:column;gap:2px;font-size:12px;color:var(--ink2)}
.filters select{font:inherit;font-size:13px;padding:4px 6px;border:1px solid var(--grid);
border-radius:6px;background:var(--surface);color:var(--ink);max-width:260px}
th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--grid);vertical-align:top}
th{cursor:pointer;color:var(--ink2);font-size:12px;white-space:nowrap}
th.plain{cursor:default}
td.plain{white-space:nowrap}
td.figure{font-size:13px;font-weight:500}
td,th{font-variant-numeric:tabular-nums}
table.prov td{font-size:12px}
.micro{display:block;min-width:120px}
.micro .track{position:relative;display:block;height:6px;margin-bottom:2px}
.micro .track i{position:absolute;top:0;height:6px;border-radius:3px}
.micro.diverging .track::before{content:"";position:absolute;left:50%;top:-2px;width:1px;
height:10px;background:var(--axis)}
.micro b{font-weight:500;font-size:12px}
.mock{position:relative;border:1px solid var(--axis);border-radius:10px;padding:14px;
margin:10px 0;background:var(--surface);overflow:hidden}
.watermark{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
font-size:34px;font-weight:700;color:var(--muted);opacity:.22;transform:rotate(-12deg);
letter-spacing:2px;margin:0;pointer-events:none;text-transform:uppercase}
.mock-alert{border:1px solid var(--grid);border-radius:8px;padding:10px;margin-top:8px}
.mock-alert code{display:block;margin:6px 0;color:var(--ink2)}
.limits li{margin-bottom:6px;max-width:88ch}
.glossary{border-top:1px solid var(--grid);padding:10px 0;max-width:92ch}
.glossary ul{margin:4px 0 0;padding-left:20px}
.empty{color:var(--muted)}
tr[hidden]{display:none}
html[data-lang="ua"] .en,html[data-lang="en"] .ua{display:none}
@media (max-width:720px){main{padding:14px 12px 50px}.tiles{grid-template-columns:1fr}
header{flex-direction:column;align-items:flex-start}}
"""

JS = """
(function(){
var root=document.documentElement;
function lang(){return root.getAttribute('data-lang');}
function show(name){
  root.setAttribute('data-tab',name);
  document.querySelectorAll('section.tab').forEach(function(s){
    s.classList.toggle('active',s.id===name);});
  document.querySelectorAll('.tab-button').forEach(function(b){
    b.setAttribute('aria-selected',String(b.dataset.tab===name));});
}
document.querySelectorAll('.tab-button').forEach(function(b){
  b.addEventListener('click',function(){show(b.dataset.tab);});});
show(root.getAttribute('data-tab'));
var langButton=document.getElementById('lang');
langButton.addEventListener('click',function(){
  var next=lang()==='ua'?'en':'ua';
  root.setAttribute('data-lang',next);
  root.setAttribute('lang',next==='ua'?'uk':'en');
  langButton.textContent=next==='ua'?langButton.dataset.ua:langButton.dataset.en;
  document.querySelectorAll('option[data-ua]').forEach(function(o){
    o.textContent=next==='ua'?o.dataset.ua:o.dataset.en;});
  hide();});
var themeButton=document.getElementById('theme');
themeButton.addEventListener('click',function(){
  var dark=window.matchMedia('(prefers-color-scheme: dark)').matches;
  var current=root.getAttribute('data-theme')||(dark?'dark':'light');
  root.setAttribute('data-theme',current==='dark'?'light':'dark');});
var box=document.createElement('div');
box.id='tip';document.body.appendChild(box);
function hide(){box.style.display='none';}
function place(target){
  var text=target.getAttribute(lang()==='ua'?'data-tip-ua':'data-tip-en');
  if(!text){return;}
  box.textContent=text;box.style.display='block';
  var r=target.getBoundingClientRect();
  var w=box.getBoundingClientRect();
  var left=r.left;
  if(left+w.width>window.innerWidth-8){left=window.innerWidth-w.width-8;}
  box.style.left=Math.max(8,left)+'px';
  box.style.top=(r.bottom+8+w.height>window.innerHeight?r.top-w.height-8:r.bottom+8)+'px';
}
document.addEventListener('mouseover',function(e){
  var t=e.target.closest('[data-tip-ua]');
  if(t){place(t);}else{hide();}});
document.addEventListener('focusin',function(e){
  var t=e.target.closest('[data-tip-ua]');
  if(t){place(t);}else{hide();}});
document.addEventListener('scroll',hide,true);
document.querySelectorAll('table.sortable').forEach(function(table){
  table.querySelectorAll('th[data-column]').forEach(function(th){
    var descending=true;
    th.addEventListener('click',function(){
      var key=th.dataset.column;
      var body=table.tBodies[0];
      var rows=Array.prototype.slice.call(body.querySelectorAll('tr:not(.none)'));
      rows.sort(function(a,b){
        var x=a.dataset[key],y=b.dataset[key];
        var nx=Number(x),ny=Number(y);
        var same=(x===y);
        if(same){return a.dataset.brand<b.dataset.brand?-1:1;}
        if(!isNaN(nx)&&!isNaN(ny)){return descending?(ny<nx?-1:1):(nx<ny?-1:1);}
        return descending?(y<x?-1:1):(x<y?-1:1);});
      rows.forEach(function(r){body.appendChild(r);});
      var none=body.querySelector('tr.none');
      if(none){body.appendChild(none);}
      descending=!descending;});});});
document.querySelectorAll('table.filtered').forEach(function(table){
  var controls=Array.prototype.slice.call(
    document.querySelectorAll('select[data-filter-for="'+table.id+'"]'));
  var body=table.tBodies[0];
  var none=body.querySelector('tr.none');
  function apply(){
    var any=false;
    Array.prototype.slice.call(body.querySelectorAll('tr:not(.none)')).forEach(function(r){
      var keep=controls.every(function(c){
        return !c.value||r.dataset[c.dataset.key]===c.value;});
      r.hidden=!keep;
      if(keep){any=true;}});
    if(none){none.hidden=any;}}
  controls.forEach(function(c){c.addEventListener('change',apply);});
  apply();});
})();
"""


def embeddable(export_bytes: bytes, export_path: Path) -> bytes:
    """The export as it will sit inside a `<script type="application/json">` block, or a refusal.

    The blob is embedded VERBATIM so the page can be checked against the file byte for byte, which
    means an export carrying a closing tag would end the script element early and take the rest of
    the document with it. Today's export has no `</` in it at all; a future one that does must be
    escaped by its producer rather than quietly mangled here.
    """
    if b"</" in export_bytes:
        raise SystemExit(
            f"{export_path.name} contains `</` and would be embedded verbatim in a <script> block —"
            " the page would break at that byte. Stop and report: the fix belongs to the export's"
            " producer, not to an escape in the dashboard."
        )
    return export_bytes


def build_page(export_path: Path, strings_path: Path, metrics_path: Path, derived: Path) -> Page:
    """The assembled page, unrendered — the test that holds `config/ui_strings.yaml` against what
    the document actually asks for needs the `Strings` instance the build used, not a second one."""
    export_bytes = embeddable(export_path.read_bytes(), export_path)
    record = json.loads(export_bytes.decode("utf-8"))
    strings = Strings(strings_path)
    dictionary = yaml.safe_load(metrics_path.read_text(encoding="utf-8"))
    evidence = read_evidence(record, derived)
    return Page(record, strings, dictionary, evidence, export_bytes, summary.sha256_of(export_path))


def build(export_path: Path, strings_path: Path, metrics_path: Path, derived: Path) -> str:
    return build_page(export_path, strings_path, metrics_path, derived).render()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", type=Path, default=EXPORT)
    parser.add_argument("--strings", type=Path, default=STRINGS)
    parser.add_argument("--metrics", type=Path, default=METRICS)
    parser.add_argument("--derived-root", type=Path, default=DERIVED)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    page = build(args.export, args.strings, args.metrics, args.derived_root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(page, encoding="utf-8")
    if not args.quiet:
        written = (
            args.out.relative_to(REPO_ROOT) if args.out.is_relative_to(REPO_ROOT) else args.out
        )
        print(f"wrote {written}  {len(page.encode('utf-8')) / 1024:.0f} KB")
        print(f"  export        {summary.sha256_of(args.export)[:16]}…")
        print(f"  tabs          {len(TABS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
