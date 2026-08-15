#!/usr/bin/env python3
"""`data/derived/pulse.db` → `results/dashboard_data_w1.json` — the dashboard's only fuel.

**Where the numbers come from.** The database, and nothing else. This script computes no aggregate
of its own: every figure below is a call into `market_pulse.aggregates`, which answers it in SQL.
No number is typed here, and the two that a reader might expect to be — the window's anchor and its
bought population — are read from `results/census_5c2.json` and `results/prereg_5c2_run.json`
through the seal by `scripts/build_aggregates.py` before the database exists.

**Every rate names its sample.** `.claude/rules/registrations-and-draws.md`: a rate is a property of
the sample it was measured on, not of the leg. So every metric carries a `sample` block, and the
comment metrics carry TWO — `bought` (what the 5c2 session paid for, and the only sample the
convergence anchor can be met on) and `payable` (the rows that carry words, which SPEC 3.19 (2)
makes the denominator of any distribution about words). The headline the dashboard shows is named
in the record rather than assumed by the reader.

**Convergence is a refusal, not a note.** Two checks run before a byte is written: the whole sealed
window summary re-derived from SQL leaf by leaf (`build_aggregates.check_convergence`), and the
figures THIS record shares with it, declared in :data:`SHARED` and compared pair by pair. Either one
disagreeing stops the export.

**Deterministic.** Sorted keys, no clock, no git block: two runs over the same evidence are
byte-identical. `provenance` carries the inputs and their sha256s, the producers and theirs.

    PYTHONPATH=src python3 scripts/export_dashboard_data.py
    PYTHONPATH=src python3 scripts/export_dashboard_data.py --out /tmp/again.json   # the pair
"""

import argparse
import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_aggregates as builder  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import aggregates, brands  # noqa: E402

METRICS = REPO_ROOT / "config" / "metrics.yaml"
OUT = REPO_ROOT / "results" / "dashboard_data_w1.json"

PROMO_CHAINS = ("atb", "silpo", "varus", "marketopt_promo")
"""The chains SPEC 3.20 (6) puts on the promo surface, by registry source id.

Маркетопт is the one that amendment added (operator ruling 2026-08-15, extending 3.18 (7)(d)); the
other three were already there. Every one of them is a KEY in `metrics.promo_pressure.by_chain`
whether it carried a row this window or not — a surface built from whatever the GROUP BY returned
would drop a chain the day it goes quiet, and this list is what a fifth chain has to be added to."""

SAMPLE_READING = {
    "bought": (
        "every comment row the 5c2 session paid for — the population"
        " results/window_summary_5c2.json was computed over, and the only sample the convergence"
        " anchor can be met on"
    ),
    "payable": (
        "the comment rows that carry words. SPEC 3.19 (1) skips the rest before payment and"
        " 3.19 (2) makes this the denominator of any distribution about words; the text-less rows"
        " are counted beside it as their own class, never blended in"
    ),
}

HEADLINE = "payable"
"""Which sample the dashboard shows for a comment metric — SPEC 3.19 (2). Named in the record."""

SHARED = (
    ("window.populations.bought", "comment.total.rows"),
    ("window.populations.text_less", "comment.total.empty_text.rows"),
    ("window.populations.leaflet_pages", "leaflet_page.total.rows"),
    ("window.populations.post_texts", "post_text.total.rows"),
    ("window.populations.position_rows", "position_row.total.rows"),
    ("metrics.volume.comments.bought", "comment.total.rows"),
    ("metrics.volume.comments.text_less", "comment.total.empty_text.rows"),
    ("metrics.nsr.by_sample.bought.scored", "comment.total.scored"),
    ("metrics.nsr.by_sample.bought.positive", "comment.total.sentiment.positive"),
    ("metrics.nsr.by_sample.bought.neutral", "comment.total.sentiment.neutral"),
    ("metrics.nsr.by_sample.bought.negative", "comment.total.sentiment.negative"),
    (
        "metrics.negative_share_sarcasm_adjusted.by_sample.bought.negative",
        "comment.total.sentiment.negative",
    ),
    ("metrics.aspect_share.by_sample.bought.labels.price", "comment.total.intents.frequency.price"),
    ("metrics.aspect_share.by_sample.bought.labels.taste", "comment.total.intents.frequency.taste"),
    (
        "metrics.aspect_share.by_sample.bought.labels.availability",
        "comment.total.intents.frequency.availability",
    ),
    (
        "metrics.aspect_share.by_sample.bought.labels.service",
        "comment.total.intents.frequency.service",
    ),
    (
        "metrics.aspect_share.by_sample.bought.labels.quality",
        "comment.total.intents.frequency.quality",
    ),
    (
        "metrics.aspect_share.by_sample.bought.labels.packaging",
        "comment.total.intents.frequency.packaging",
    ),
    (
        "metrics.aspect_share.by_sample.bought.rows_with_no_aspect",
        "comment.total.intents.rows_with_no_intent",
    ),
    (
        "metrics.sov.by_sample.bought.mentions.rud",
        "comment.total.brand_attribution.mentions.rud",
    ),
    (
        "metrics.sov.by_sample.bought.mentions.limo",
        "comment.total.brand_attribution.mentions.limo",
    ),
    (
        "metrics.promo_depth.readings.from_price_pair.n",
        "position_row.total.depth.from_price_pair.n",
    ),
    (
        "metrics.promo_depth.readings.from_price_pair.median",
        "position_row.total.depth.from_price_pair.median",
    ),
    (
        "metrics.promo_depth.readings.from_printed_badge.median",
        "position_row.total.depth.from_printed_badge.median",
    ),
    (
        "metrics.promo_depth.printed_disagrees_with_computed",
        "position_row.total.depth.printed_disagrees_with_computed",
    ),
    ("metrics.promo_pressure.position_rows", "position_row.total.rows"),
    ("cuts.legs.leaflet_page.total.positions", "leaflet_page.total.positions"),
    ("cuts.legs.leaflet_page.total.unreadable.rows", "leaflet_page.total.unreadable.rows"),
    ("cuts.legs.post_text.total.positions", "post_text.total.positions"),
    ("cuts.legs.post_text.total.with_positions", "post_text.total.with_positions"),
)
"""(this record's path, the anchor's path) for every figure the two share, declared by hand.

The exhaustive half of the gate is `aggregates.converge`, which re-derives all 902 of the anchor's
numeric leaves from the database. This list is the other half and answers a different question: not
"does the layer agree" but "does the thing the DASHBOARD will render agree". A figure can only get
onto a screen through this record, so each shared one is named and compared pair by pair."""

NOT_SHARED = {
    "metrics.*.by_sample.payable": (
        "SPEC 3.19 (2)'s sample. The anchor predates the rule and was computed on the bought"
        " population, so there is nothing on its side to equal."
    ),
    "metrics.negative_share_sarcasm_adjusted.*.negative_share_sarcasm_adjusted": (
        "a cross of two heads — sentiment and sarcasm — that the anchor never computed. New, not"
        " shared."
    ),
    "metrics.sov.*.share": "a share among the watchlist; the anchor carries mention counts only",
    "metrics.promo_depth.readings.*.q1|q3": "quartiles; the anchor's spread is n/min/median/max",
    "metrics.promo_pressure.by_brand|by_chain": (
        "positions grouped by brand and by chain. The anchor groups positions by channel and by"
        " carrier and never joins them to the registry."
    ),
    "metrics.coverage.*": (
        "channels and segments against the registry's own size. The anchor has no registry-side"
        " denominator — it counts evidence."
    ),
    "cuts.comment_by_segment.*": (
        "the audience-segment cut. The anchor has no segment column; the join is this layer's."
    ),
    "cuts.brand_by_sentiment.*": (
        "brand × sentiment. The anchor counts brand mentions and sentiment separately and never"
        " crosses them."
    ),
    "promo.positions_table.rows[]": (
        "the position ROWS themselves — SPEC 3.21 (4). The anchor counts positions and spreads"
        " their depth; it carries no row, so there is nothing on its side to equal. What holds this"
        " table instead is its own refusal: its length must equal"
        " `window.populations.position_rows`, and THAT figure is shared and checked above."
    ),
    "metrics.sov.*.mentions.varto|selianske|garmonija": (
        "the three brands SPEC 3.21 (1)'s revision r1 rules on. The anchor was matched before the"
        " rules existed and is never rescored, so these counts CANNOT be equal — what holds them"
        " instead is `convergence.watchlist_revision`, which checks that r1 only ever removes."
    ),
}
"""What this record carries that the anchor cannot check, and why — by path pattern.

Named rather than left out, because "every shared figure agrees" is only a claim about the figures
somebody enumerated. The new ones are new for a reason and the reason is written down."""


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def dig(record: dict, path: str):
    """`a.b.c` into a nested record, or a refusal naming the step that failed."""
    node = record
    for step in path.split("."):
        if not isinstance(node, dict) or step not in node:
            raise SystemExit(f"{path}: no such field — stopped at {step!r}")
        node = node[step]
    return node


def sample_block(conn, window_id: str, name: str) -> dict:
    """A sample, named, sized and explained — what every rate in this record stands beside."""
    return {
        "name": name,
        "rows": aggregates.sample_rows(conn, window_id, name),
        "reading": SAMPLE_READING[name],
    }


def only(block: dict, *names: str) -> dict:
    """The fields one metric owns, out of a block that computes several.

    `aggregates.sentiment_metrics` answers NSR and both negative shares in one pass over the same
    rows — one query, one set of counts. Each metric then publishes only its own fields, so the
    dictionary entry for `nsr` does not silently ship the sarcasm correction under its own name.
    """
    return {name: block[name] for name in names}


def by_sample(conn, window_id: str, compute) -> dict:
    return {
        name: {"sample": sample_block(conn, window_id, name)} | compute(name)
        for name in sorted(aggregates.SAMPLES)
    }


def metrics_block(conn, window_id: str) -> dict:
    """The eight metrics `config/metrics.yaml` defines, each one answered by SQL."""
    window = conn.execute(
        "SELECT bought, payable, text_less, leaflet_pages, post_texts FROM windows"
        " WHERE window_id = ?",
        (window_id,),
    ).fetchone()
    (position_rows,) = conn.execute(
        "SELECT COUNT(*) FROM positions WHERE window_id = ?", (window_id,)
    ).fetchone()
    leaflet_chains = [
        source_id
        for (source_id,) in conn.execute(
            "SELECT DISTINCT ch.source_id FROM markers m JOIN channels ch USING (window_id, channel)"
            " WHERE m.window_id = ? AND m.leg = 'leaflet_page' ORDER BY 1",
            (window_id,),
        )
    ]
    brand_rows = conn.execute(
        f"SELECT COUNT(*) FROM (SELECT DISTINCT channel, msg_id FROM {aggregates.REVISED_BRANDS}"
        " WHERE window_id = ?)",
        (window_id,),
    ).fetchone()[0]
    revision = watchlist_revision(conn, window_id)

    depth = aggregates.depth_readings(conn, window_id)
    pressure = aggregates.promo_pressure(conn, window_id)
    position_sample = {
        "name": "position_rows",
        "rows": position_rows,
        "reading": (
            "the position rows the window's leaflet pages and promo post texts yielded. Leaflet"
            f" pages were collected for {', '.join(leaflet_chains)} only in window-1, so every"
            " other chain's depth here comes from post text — a different instrument on a smaller"
            " sample"
        ),
    }
    return {
        "volume": {
            "sample": {
                "name": "window",
                "rows": window[0] + window[3] + window[4],
                "reading": "every unit of observation the window carried, across the three legs",
            },
            "comments": {"bought": window[0], "payable": window[1], "text_less": window[2]},
            "leaflet_pages": window[3],
            "post_texts": window[4],
            "position_rows": position_rows,
        },
        "nsr": {
            "headline_sample": HEADLINE,
            "sample": sample_block(conn, window_id, HEADLINE),
            "by_sample": by_sample(
                conn,
                window_id,
                lambda name: only(
                    aggregates.sentiment_metrics(conn, window_id, sample=name),
                    "scored",
                    "positive",
                    "neutral",
                    "negative",
                    "nsr",
                ),
            ),
        },
        "negative_share_sarcasm_adjusted": {
            "headline_sample": HEADLINE,
            "sample": sample_block(conn, window_id, HEADLINE),
            "by_sample": by_sample(
                conn,
                window_id,
                lambda name: only(
                    aggregates.sentiment_metrics(conn, window_id, sample=name),
                    "scored",
                    "negative",
                    "reclassified_from_sarcasm",
                    "negative_share",
                    "negative_share_sarcasm_adjusted",
                ),
            ),
        },
        "sov": {
            "headline_sample": HEADLINE,
            "watchlist_rules": revision["revision"],
            "sample": {
                "name": "comment_rows_with_a_watchlist_brand",
                "rows": brand_rows,
                "of": window[0],
                "share": round(brand_rows / window[0], 6) if window[0] else None,
                "watchlist_rules": revision["revision"],
                "reading": (
                    "SoV is measured over the comment rows where the DETERMINISTIC matcher found a"
                    " watchlist name in the text that was sent, under the named rules revision"
                    f" {revision['revision']} (SPEC 3.21 (1)). That is a small part of the window"
                    " and it is not a model head — the comment instrument has no brand head at all."
                    " A row here is a comment that MENTIONS the brand, never a stance towards it"
                ),
            },
            "by_sample": by_sample(
                conn,
                window_id,
                lambda name: (
                    aggregates.share_of_voice(
                        conn, window_id, sample=name, table=aggregates.REVISED_BRANDS
                    )
                    | {"watchlist_rules": revision["revision"]}
                ),
            ),
        },
        "aspect_share": {
            "headline_sample": HEADLINE,
            "sample": sample_block(conn, window_id, HEADLINE),
            "by_sample": by_sample(
                conn, window_id, lambda name: aggregates.aspect_share(conn, window_id, sample=name)
            ),
        },
        "promo_depth": {
            "sample": position_sample,
            "readings": {
                "from_price_pair": depth["from_price_pair"],
                "from_printed_badge": depth["from_printed_badge"],
            },
            "printed_disagrees_with_computed": depth["printed_disagrees_with_computed"],
            "by_carrier": {
                carrier: aggregates.depth_readings(conn, window_id, carrier=carrier)
                for carrier in ("leaflet_page", "post_text")
            },
            "law": summary.DEPTH_LAW,
        },
        "promo_pressure": {
            "sample": position_sample,
            "position_rows": pressure["position_rows"],
            "by_brand": pressure["by_brand"],
            "share": pressure["share"],
            "rows_with_no_resolved_brand": pressure["rows_with_no_resolved_brand"],
            "by_chain": aggregates.promo_by_chain(conn, window_id, PROMO_CHAINS),
        },
        "coverage": {
            "sample": {
                "name": "registry",
                "rows": conn.execute(
                    "SELECT registry_channels FROM windows WHERE window_id = ?", (window_id,)
                ).fetchone()[0],
                "reading": (
                    "the denominator is the registry, not the evidence. Subscribers are not reach:"
                    " nothing here says how many people saw a post"
                ),
            }
        }
        | aggregates.coverage(conn, window_id),
    }


def promo_block(conn, window_id: str) -> dict:
    """The promo answer of SPEC 3.21 (4): every position of the window, as a table.

    ALL of them — the operator's question is «which positions, at which prices, of which brands are
    in promo» and a sample answers a different one. The count is held against the window's own
    population before the record is written, here and not only in a test: a table that lost a row on
    a join would still look like an answer.

    Two readings of the law meet on the `depth` column and the export says which one it carries.
    SPEC 3.18 (1) names the promo price and the printed −N% as the depth instrument, and this table
    follows it, because the arithmetic depth of 3.17 (3) is `(old − promo) / old` and printing it
    beside the promo price hands the reader back the extracted old price that 3.17 (3) and 3.18 (1)
    keep off every surface. The arithmetic reading is not lost: it is the window aggregate in
    `metrics.promo_depth.readings.from_price_pair`, where no row's own price sits beside it.
    """
    (position_rows,) = conn.execute(
        "SELECT COUNT(*) FROM positions WHERE window_id = ?", (window_id,)
    ).fetchone()
    rows = aggregates.promo_positions(conn, window_id, PROMO_CHAINS)
    if len(rows) != position_rows:
        raise SystemExit(
            f"the positions table holds {len(rows)} rows and the window has {position_rows}"
            " positions — the promo surface must answer for the whole population it names."
            " Stop and report."
        )
    return {
        "positions_table": {
            "window": window_id,
            "sample": {
                "name": "position_rows",
                "rows": position_rows,
                "reading": (
                    "every position row of the window, not a draw from them — the leaflet pages and"
                    " the promo post texts the window carried. Two instruments on one table: the"
                    " carrier column says which, and only ATB yielded leaflet PAGES in window-1"
                ),
            },
            "law": (
                "SPEC 3.21 (4). `promo_price` is the green leg of 3.18 (1) (80/80 in the team"
                " lead's read of the B′ population). `depth` is the PRINTED badge's reading —"
                " printed_pct / 100 — and never the arithmetic depth of 3.17 (3), which is computed"
                " from the extracted old price: printing it beside the promo price would hand back"
                " `price_old = promo_price / (1 - depth)`, so no column of this table carries the"
                " arithmetic reading. The extracted old price is in no field of this table. This"
                " says nothing about other surfaces — see docs/reports/fix-b.md finding (1)."
            ),
            "rows": rows,
        }
    }


def watchlist_revision(conn, window_id: str) -> dict:
    """Which rules revision the presentation cut was matched under — read from the database.

    Read and not passed in: the r1 table and this row are written together by
    `build_aggregates.add_revised_brands`, so a record that names a revision its rows were not
    matched under is impossible rather than merely unlikely.
    """
    row = conn.execute(
        "SELECT revision, dated, rules_sha256 FROM watchlist_revision WHERE window_id = ?",
        (window_id,),
    ).fetchone()
    if row is None:
        raise SystemExit(
            "the database holds no watchlist revision — the brand surfaces have no matcher to name"
        )
    return {"revision": row[0], "dated": row[1], "rules_sha256": row[2]}


def cuts_block(conn, window_id: str) -> dict:
    """The per-dimension aggregates the plan's tabs read — every one of them a GROUP BY."""
    channels = aggregates.channels_with(conn, window_id, "comments")
    segments = aggregates.registry_segments(conn, window_id)
    revision = watchlist_revision(conn, window_id)
    brand_sentiment: dict[str, dict] = {}
    for brand, sentiment, number in conn.execute(
        f"SELECT b.brand_id, c.sentiment, COUNT(*) FROM {aggregates.REVISED_BRANDS} b JOIN comments"
        " c USING (window_id, channel, msg_id) WHERE b.window_id = ? AND c.scored = 1"
        " AND c.has_text = 1 GROUP BY 1, 2 ORDER BY 1, 2",
        (window_id,),
    ):
        brand_sentiment.setdefault(brand, {})[sentiment] = number
    return {
        "comment_by_channel": {
            handle: {
                "source_id": source_id,
                "source_type": source_type,
                "segment": segment,
                "bought": aggregates.comment_block(
                    conn, window_id, channel=handle, sample="bought"
                ),
                "payable": aggregates.comment_block(
                    conn, window_id, channel=handle, sample="payable"
                ),
            }
            for handle in channels
            for source_id, source_type, segment in [
                conn.execute(
                    "SELECT source_id, source_type, segment FROM channels WHERE window_id = ?"
                    " AND channel = ?",
                    (window_id, handle),
                ).fetchone()
            ]
        },
        # every segment the REGISTRY holds, not every segment that produced a row: the plan's T3
        # screen is one card per audience, and an audience that said nothing this window is a
        # finding. `channels_with_a_row` is empty for those and `registry_channels` says how many
        # channels were listening.
        "comment_by_segment": {
            segment: {
                "registry_channels": registry_channels,
                "channels_with_a_row": aggregates.channels_with(
                    conn, window_id, "channels", segment=segment
                ),
                "bought": aggregates.comment_block(
                    conn, window_id, segment=segment, sample="bought"
                ),
                "payable": aggregates.comment_block(
                    conn, window_id, segment=segment, sample="payable"
                ),
            }
            for segment, registry_channels in segments
        },
        "brand_by_sentiment": {
            "watchlist_rules": revision["revision"],
            "sample": {
                "name": "payable",
                "watchlist_rules": revision["revision"],
                "reading": (
                    "scored, text-bearing comment rows in which the matcher found the brand under"
                    f" rules revision {revision['revision']}. A brand missing from this table was"
                    " matched in no such row. The cross is MENTION × the comment's own tonality:"
                    " SPEC 3.21 (3) — until the stance layer is law, a row here says the comment"
                    " named the brand and how that comment reads, never how it feels about it"
                ),
            },
            "rows": brand_sentiment,
        },
        "legs": {
            leg: {
                "total": aggregates.marker_block(conn, window_id, leg),
                "per_channel": {
                    handle: aggregates.marker_block(conn, window_id, leg, channel=handle)
                    for handle in aggregates.channels_with(conn, window_id, "markers", leg=leg)
                },
            }
            for leg in ("leaflet_page", "post_text")
        },
        "positions_by_category": aggregates.counts(
            conn,
            "SELECT category, COUNT(*) FROM positions WHERE window_id = ? GROUP BY 1 ORDER BY 1",
            (window_id,),
        ),
        "positions_by_carrier": aggregates.counts(
            conn,
            "SELECT carrier, COUNT(*) FROM positions WHERE window_id = ? GROUP BY 1 ORDER BY 1",
            (window_id,),
        ),
        # the two comment cuts above are the MIRROR's shape — the same `comment_block` the
        # convergence gate re-derives the anchor's 902 leaves from — so their `brand_attribution`
        # counts the matching the sealed record was measured under, not r1's. Said here rather than
        # left to be inferred: one record must never carry two brand definitions unlabelled.
        "brand_attribution_in_the_comment_cuts": {
            "watchlist_rules": "anchor",
            "reading": (
                "`comment_by_channel` and `comment_by_segment` carry the matching"
                " results/window_summary_5c2.json was sealed under, because the convergence gate"
                " re-derives that record out of the same blocks and SPEC 3.21 (1) never rescores"
                " G1e history. Every brand surface the DASHBOARD renders — metrics.sov and"
                f" cuts.brand_by_sentiment — is {revision['revision']} and says so in its own block"
            ),
        },
    }


NOT_COMPUTABLE = {
    "trend_vs_previous_window": {
        "surface": "T0, every KPI card's comparison",
        "reason": "one window is a point; a trend needs two",
        "unlock": "the cycle-2 paid run writes window-2 into the same tables",
    },
    "alert_baselines": {
        "surface": "T7",
        "reason": "an alert fires on a deviation from a baseline and a baseline of one window is"
        " the window itself",
        "unlock": "window-2, then a threshold ruled by the operator on the alert design",
    },
    "category_layer": {
        "surface": "T6",
        "reason": "the tracked taxonomy is approved but the category property is not computed for"
        " posts, so comments cannot inherit it",
        "unlock": "phase 5c3 builds the category layer",
    },
    "reactions_views_votes": {
        "surface": "T0 volume, T1 weighting",
        "reason": "the store carries no reaction, view or poll-vote sidecar for this window",
        "unlock": "sidecar v2 (phase 5c3)",
    },
    "leaflet_depth_for_silpo_varus_marketopt": {
        "surface": "T5",
        "reason": "leaflet PAGES were collected for one chain in window-1; the other three chains'"
        " promo depth here comes from post text, which is a different instrument",
        "unlock": "cycle-2 leaflet collection — SPEC 3.20 (6), contract cycle2-prep-b",
    },
    "reach": {
        "surface": "T0 coverage, T8",
        "reason": "subscriber counts are not reach and nothing in the store says how many people"
        " saw a post",
        "unlock": "none from public Telegram data; the metric stays unclaimed",
    },
    "sales_linkage": {
        "surface": "not on any tab",
        "reason": "internal sales and shipment data are not in this system",
        "unlock": "an owner decision on the ТПК data track, with its own legality and format gate",
    },
}
"""What the dashboard must render as an honest stub instead of a zero.

Each one names the surface it belongs to and the condition that unlocks it. A screen that showed 0
for a trend and 0 for a category share would be making two different claims with the same digit."""


def provenance(sources: dict, inputs: dict) -> dict:
    return {
        "reads": (
            "data/derived/ through the reading path of scripts/window_summary_5c2.py, plus the"
            " records below through the sealed registration's own pins. No clock and no git block:"
            " two runs over the same evidence are byte-identical."
        ),
        "evidence": sources,
        "inputs": inputs,
        "producers": {
            name: summary.sha256_of(REPO_ROOT / name)
            for name in (
                "scripts/export_dashboard_data.py",
                "scripts/build_aggregates.py",
                "scripts/window_summary_5c2.py",
                "src/market_pulse/aggregates.py",
                "src/market_pulse/prompts.py",
                "src/market_pulse/brands.py",
                "src/market_pulse/langid.py",
                "src/market_pulse/loop.py",
            )
        },
    }


def check_shared(record: dict, anchor: dict) -> dict:
    """Every pair in :data:`SHARED`, resolved on both sides. A mismatch stops the export."""
    checked = {}
    wrong = {}
    for here, there in SHARED:
        mine, theirs = dig(record, here), dig(anchor, there)
        checked[here] = {"anchor_field": there, "value": theirs}
        if mine != theirs:
            wrong[here] = {"export": mine, "anchor": theirs, "anchor_field": there}
    if wrong:
        raise SystemExit(
            f"the export disagrees with the convergence anchor on {len(wrong)} shared figures:"
            f" {json.dumps(wrong, ensure_ascii=False)}"
        )
    return checked


def check_revision(record: dict, anchor: dict, ruled: tuple[str, ...]) -> dict:
    """What replaces the two shared pairs SPEC 3.21 (1) took away — and it checks more than they did.

    The anchor's brand attribution is the matching of the day it was sealed; this record's is r1's.
    Equality is therefore the wrong question. The right one is the shape of the difference: a rule
    can only REMOVE a hit, so every brand r1 does not rule on must have exactly the anchor's count,
    and every brand it does rule on must have no more than it. A revision that added a mention
    anywhere would be a registry edit wearing a rules file's clothes, and this refuses it.
    """
    mine = dig(record, "metrics.sov.by_sample.bought.mentions")
    theirs = dig(anchor, "comment.total.brand_attribution.mentions")
    wrong = {}
    for brand, count in sorted(mine.items()):
        was = theirs.get(brand, 0)
        if (count > was) if brand in ruled else (count != was):
            wrong[brand] = {"export": count, "anchor": was, "ruled_by_r1": brand in ruled}
    if wrong:
        raise SystemExit(
            "the revised brand cut is not a narrowing of the anchor's:"
            f" {json.dumps(wrong, ensure_ascii=False)}"
        )
    return {
        "ruled": list(ruled),
        "removed": {
            brand: {"anchor": theirs.get(brand, 0), "r1": mine[brand]}
            for brand in ruled
            if theirs.get(brand, 0) != mine.get(brand, 0)
        },
        "unchanged": sorted(brand for brand in mine if brand not in ruled),
        "reading": (
            "every brand r1 does not rule on carries the anchor's own count on the bought sample,"
            " and every brand it does rule on carries no more. The rules can only remove, so this"
            " is the pair check the two dropped SHARED figures used to be — widened to all 23"
        ),
    }


def whole_record(verdict: dict) -> dict:
    """The exhaustive check, without its 902-path agreement list.

    The three lists that must be EMPTY are carried in full — a disagreement, a leaf with no answer,
    a leaf the mirror invented — and the one that is 902 entries long is carried as a count. It is
    the anchor's own leaf set, reproducible from the anchor in one walk, and 47 KB of dotted paths
    in the dashboard's fuel file would be the largest thing in it.
    """
    return {
        "leaves": verdict["leaves"],
        "agreed": len(verdict["agreed"]),
        "disagreed": verdict["disagreed"],
        "missing": verdict["missing"],
        "extra": verdict["extra"],
        "blocks": [
            "populations_registered",
            "comment",
            "leaflet_page",
            "post_text",
            "position_row",
        ],
    }


def export(conn, sources: dict, anchor_path: Path, metrics_path: Path) -> dict:
    anchor = json.loads(summary.read_text_or_refuse(anchor_path))
    dictionary = yaml.safe_load(summary.read_text_or_refuse(metrics_path))
    # the LAW, not the database's copy of its name: `check_revision` needs to know which brands the
    # rules file rules on, and reading that from the file the build matched with is what keeps the
    # check from being satisfied by whatever the table happens to contain.
    rules = brands.load_watchlist_rules(builder.RULES)
    window = conn.execute(
        "SELECT anchor, days, since, until, bought, payable, text_less, leaflet_pages, post_texts"
        " FROM windows WHERE window_id = ?",
        (builder.WINDOW_ID,),
    ).fetchone()
    (position_rows,) = conn.execute(
        "SELECT COUNT(*) FROM positions WHERE window_id = ?", (builder.WINDOW_ID,)
    ).fetchone()

    record = {
        "phase": "6a",
        "contract": (
            "docs/PROMPT-phase6a.md deliverable 2; docs/SPEC.md amendment 3.20. The dashboard reads"
            " THIS file and nothing else — no presentation surface reads the database, and no"
            " number on any surface was typed by a human."
        ),
        "window": {
            "id": builder.WINDOW_ID,
            "anchor": window[0],
            "days": window[1],
            "since": window[2],
            "until": window[3],
            "rule": "since <= date < until, half-open",
            "populations": {
                "bought": window[4],
                "payable": window[5],
                "text_less": window[6],
                "leaflet_pages": window[7],
                "post_texts": window[8],
                "position_rows": position_rows,
            },
            "reading": (
                "bought is what the 5c2 session paid for; payable is what SPEC 3.19 (1)'s queue"
                " rule leaves for the next cycle. They are stored apart and never conflated — the"
                " registration that names the next paid population must name the payable one."
            ),
        },
        "metrics": metrics_block(conn, builder.WINDOW_ID),
        "cuts": cuts_block(conn, builder.WINDOW_ID),
        "promo": promo_block(conn, builder.WINDOW_ID),
        "not_computable": NOT_COMPUTABLE,
        "dictionary": {
            "path": rel(metrics_path),
            "sha256": summary.sha256_of(metrics_path),
            "metrics": sorted(one["id"] for one in dictionary["metrics"]),
        },
    }
    record["convergence"] = {
        "anchor": rel(anchor_path),
        "sha256": summary.sha256_of(anchor_path),
        "shared_figures": check_shared(record, anchor),
        "not_shared": NOT_SHARED,
        "watchlist_revision": watchlist_revision(conn, builder.WINDOW_ID)
        | check_revision(record, anchor, tuple(sorted(rules.required))),
        "whole_record": whole_record(builder.check_convergence(conn, anchor_path)),
        "reading": (
            "two checks, both of which refuse rather than warn. `shared_figures` compares every"
            " figure THIS record shares with the anchor, pair by pair, and names the anchor field"
            " each one was held against. `whole_record` re-derives every numeric leaf of the"
            " anchor's five aggregate blocks from SQL, which is the exhaustive half — the agreed"
            " paths are a count and not a list, because they are exactly the leaves of the anchor"
            " and `tests/test_export_dashboard_data.py` walks them again."
        ),
    }
    record["provenance"] = provenance(
        sources,
        {
            rel(path): summary.sha256_of(path)
            for path in (
                anchor_path,
                metrics_path,
                builder.PREREG,
                builder.CENSUS,
                builder.REGISTRY,
                builder.RULES,
            )
        },
    )
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--derived-root", type=Path, default=builder.DERIVED)
    parser.add_argument("--db", type=Path, default=builder.OUT)
    parser.add_argument("--anchor", type=Path, default=builder.ANCHOR)
    parser.add_argument("--metrics", type=Path, default=METRICS)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)

    conn, sources = builder.build(args.derived_root, builder.PREREG, builder.REGISTRY, args.db)
    record = export(conn, sources, args.anchor, args.metrics)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    verdict = record["convergence"]
    print(f"wrote {rel(args.out)}  sha256 {summary.sha256_of(args.out)[:16]}…")
    print(
        f"  window        {record['window']['id']} anchor {record['window']['anchor']}"
        f" · {record['window']['populations']['bought']} bought"
        f" · {record['window']['populations']['payable']} payable"
    )
    print(f"  metrics       {', '.join(sorted(record['metrics']))}")
    table = record["promo"]["positions_table"]
    print(
        f"  promo table   {len(table['rows'])} position rows"
        f" · {sum(1 for row in table['rows'] if 'id' in row['brand'])} with a resolved brand"
        f" · {sum(1 for row in table['rows'] if 'depth' in row)} with a printed badge"
    )
    print(
        f"  convergence   {len(verdict['shared_figures'])} shared figures equal;"
        f" {verdict['whole_record']['agreed']}/{verdict['whole_record']['leaves']} anchor"
        f" leaves re-derived from SQL"
    )
    print(f"  not computable {len(record['not_computable'])} entries with unlock conditions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
