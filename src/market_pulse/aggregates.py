"""The window aggregates and the SQL that answers them — SPEC 3.20 (2).

**What this module is.** A schema, the inserts that fill it, and the queries that read it back.
It never opens a `.jsonl`, never parses a reply and never touches the disk except through the
`sqlite3.Connection` it is handed: `scripts/build_aggregates.py` does the reading, through the
reading path of `scripts/window_summary_5c2.py`, and hands rows in. That split is the whole reason
`src/` does not import `scripts/` here — and it is what keeps ONE reader for the derived store.

**Why SQLite.** Operator ruling 2026-08-15 (`docs/PLAN-phase6-command-center.md` §11 (1)): the
aggregate layer is the spine trends and alerts will stand on, and windows accumulate in it. Every
table therefore carries `window_id` in its key rather than assuming one window; window-2 is an
INSERT, not a migration.

**The two populations.** A window has a BOUGHT population and a PAYABLE one, and since SPEC 3.19 (1)
they are different numbers. `windows` stores both, labelled, and every comment row carries
`has_text` so a distribution can be asked for on either sample. Nothing in here defaults to one of
them silently: :func:`comment_block` takes the sample by name and the caller says which it wanted.

**What SQL does and what Python does.** Counting, grouping, filtering and ordering are SQL. The
median is not — SQLite has no percentile function — so :func:`spread` reads the ordered column back
and uses `statistics.median`, which is also what `window_summary_5c2._spread` uses, so the two agree
by construction rather than by luck.

:func:`mirror` re-derives `results/window_summary_5c2.json`'s five aggregate blocks from the
database alone. It exists so the convergence gate can compare 902 numbers instead of four.
"""

import json
import sqlite3
import statistics

SCHEMA = """
CREATE TABLE windows (
    window_id         TEXT PRIMARY KEY,
    anchor            TEXT NOT NULL,
    days              INTEGER NOT NULL,
    since             TEXT NOT NULL,
    until             TEXT NOT NULL,
    bought            INTEGER NOT NULL,
    payable           INTEGER NOT NULL,
    text_less         INTEGER NOT NULL,
    leaflet_pages     INTEGER NOT NULL,
    post_texts        INTEGER NOT NULL,
    registry_channels INTEGER NOT NULL
);

CREATE TABLE channels (
    window_id   TEXT NOT NULL,
    channel     TEXT NOT NULL,
    source_id   TEXT NOT NULL,
    source_type TEXT NOT NULL,
    segment     TEXT,
    PRIMARY KEY (window_id, channel)
);

CREATE TABLE segments (
    window_id         TEXT NOT NULL,
    segment           TEXT NOT NULL,
    registry_channels INTEGER NOT NULL,
    PRIMARY KEY (window_id, segment)
);

CREATE TABLE watchlist (
    window_id TEXT NOT NULL,
    brand_id  TEXT NOT NULL,
    own       INTEGER NOT NULL,
    display   TEXT NOT NULL,
    PRIMARY KEY (window_id, brand_id)
);

CREATE TABLE comments (
    window_id  TEXT NOT NULL,
    channel    TEXT NOT NULL,
    msg_id     INTEGER NOT NULL,
    task       TEXT NOT NULL,
    has_text   INTEGER NOT NULL,
    language   TEXT NOT NULL,
    scored     INTEGER NOT NULL,
    unreadable TEXT,
    sentiment  TEXT,
    sarcasm    INTEGER,
    n_intents  INTEGER NOT NULL,
    PRIMARY KEY (window_id, channel, msg_id)
);

CREATE TABLE comment_intents (
    window_id TEXT NOT NULL,
    channel   TEXT NOT NULL,
    msg_id    INTEGER NOT NULL,
    intent    TEXT NOT NULL
);

CREATE TABLE comment_brands (
    window_id TEXT NOT NULL,
    channel   TEXT NOT NULL,
    msg_id    INTEGER NOT NULL,
    brand_id  TEXT NOT NULL
);

CREATE TABLE comment_brands_r1 (
    window_id TEXT NOT NULL,
    channel   TEXT NOT NULL,
    msg_id    INTEGER NOT NULL,
    brand_id  TEXT NOT NULL
);

CREATE TABLE watchlist_revision (
    window_id    TEXT NOT NULL,
    revision     TEXT NOT NULL,
    dated        TEXT NOT NULL,
    rules_sha256 TEXT NOT NULL,
    PRIMARY KEY (window_id)
);

CREATE TABLE markers (
    window_id     TEXT NOT NULL,
    leg           TEXT NOT NULL,
    channel       TEXT NOT NULL,
    msg_id        INTEGER NOT NULL,
    parent_msg_id INTEGER,
    n_positions   INTEGER,
    unreadable    TEXT,
    PRIMARY KEY (window_id, leg, channel, msg_id)
);

CREATE TABLE positions (
    window_id                    TEXT NOT NULL,
    row_id                       TEXT NOT NULL,
    channel                      TEXT NOT NULL,
    carrier                      TEXT NOT NULL,
    msg_id                       INTEGER NOT NULL,
    ordinal                      INTEGER NOT NULL,
    tier                         TEXT NOT NULL,
    brand_id                     TEXT,
    category                     TEXT,
    price_promo                  REAL,
    price_old                    REAL,
    discount_pct_printed         REAL,
    discount_footnote            INTEGER,
    price_qualifier              TEXT,
    depth                        REAL,
    depth_disagrees_with_printed INTEGER,
    presence_brand               INTEGER NOT NULL,
    presence_line                INTEGER NOT NULL,
    presence_category            INTEGER NOT NULL,
    presence_size                INTEGER NOT NULL,
    presence_attribute           INTEGER NOT NULL,
    brand_raw                    TEXT,
    line                         TEXT,
    size_value                   REAL,
    size_unit                    TEXT,
    pack_count                   INTEGER,
    attribute_pct                REAL,
    PRIMARY KEY (window_id, row_id)
);

CREATE TABLE position_warnings (
    window_id TEXT NOT NULL,
    row_id    TEXT NOT NULL,
    warning   TEXT NOT NULL
);
"""

PRESENCE = ("brand", "line", "category", "size", "attribute")
PROMO_FIELDS = ("price_promo", "price_old", "discount_pct_printed", "discount_footnote")

ANCHOR_BRANDS = "comment_brands"
REVISED_BRANDS = "comment_brands_r1"
"""Two tables and not one table with a `rules` column, deliberately.

The anchor table is what `results/window_summary_5c2.json` was measured under, and :func:`mirror`
re-derives 35 of that record's 902 numeric leaves out of it. A column would have made every existing
query on it wrong until somebody remembered a filter; two tables mean the convergence path's SQL is
the SAME SQL, and that is checkable with `git diff` rather than with an argument about filters.
The revised table is the presentation side (SPEC 3.21 (1)) and every block built from it says so."""

SAMPLES = {
    "bought": "1",
    "payable": "has_text = 1",
}
"""The two comment samples, as SQL, by name.

`bought` is the 5 075 rows the 5c2 session paid for and is what
`results/window_summary_5c2.json` was computed over — the convergence anchor cannot be met on any
other sample. `payable` is what SPEC 3.19 (1)'s queue rule leaves for the NEXT paid cycle, and
3.19 (2) makes it the denominator a distribution about words is reported on. A caller names one;
there is no default, because the whole point is that the reader is told which."""


class Refusal(Exception):
    """A source the aggregate layer needed and did not get — SPEC 3.20 (1)'s loud failure."""


def connect(path) -> sqlite3.Connection:
    """A connection with the schema already in it. `path` may be `":memory:"`."""
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    return conn


# --- filling it ----------------------------------------------------------------------------------


def add_window(
    conn, window_id: str, anchor: dict, populations: dict, split: dict, registry_channels: int
) -> None:
    """One window's identity, its two populations, and the registry it was collected against.

    `populations` is the SEALED registration's (what was bought); `split` is what the rows on disk
    say about text. Storing `bought` and `payable` in the same row is the prep-a §1.5 memo made
    structural: collected is not payable, and a table that held one number could not say so.
    `registry_channels` is coverage's denominator: how many channels COULD have produced a row,
    which is a fact about the registry and not about the evidence. The segment denominator is the
    `segments` table, because that one has to be ENUMERABLE and not just counted.
    """
    conn.execute(
        "INSERT INTO windows VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            window_id,
            anchor["anchor"],
            anchor["days"],
            anchor["since"],
            anchor["until"],
            populations["comment"],
            split["payable"],
            split["text_less"],
            populations["leaflet_page"],
            populations["post_text"],
            registry_channels,
        ),
    )


def add_channels(conn, window_id: str, segments: dict) -> None:
    conn.executemany(
        "INSERT INTO channels VALUES (?, ?, ?, ?, ?)",
        [
            (window_id, handle, one["source_id"], one["source_type"], one["segment"])
            for handle, one in sorted(segments.items())
        ],
    )


def add_segments(conn, window_id: str, segments: dict) -> None:
    """Every audience segment the REGISTRY holds — including the ones no row reached.

    `channels` is fed from the evidence and can only hold segments that produced a row, so a cut
    driven off it renders however many segments happened to be talkative. The plan's T3 screen is
    eight cards from the registry's audiences and it has to render eight: an audience that said
    nothing this window is a finding, and a card missing from a screen is not.

    Note what this table deliberately does NOT do: it is a segment dimension, not a channel one.
    Widening `channels` to hold all 66 registry handles would make `coverage.channels.with_a_row`
    read 66/66 and destroy the metric.
    """
    counted: dict[str, int] = {}
    for one in segments.values():
        if one["segment"] is not None:
            counted[one["segment"]] = counted.get(one["segment"], 0) + 1
    conn.executemany(
        "INSERT INTO segments VALUES (?, ?, ?)",
        [(window_id, name, number) for name, number in sorted(counted.items())],
    )


def add_watchlist(conn, window_id: str, brands: list) -> None:
    """The watchlist as a dimension, so a brand nobody mentioned is a ZERO and not an absence.

    SoV is a share among the watchlist; a query that only saw the brands with a mention would rank
    six brands and silently drop the rest of the field it is meant to be a share of.

    `display` is the registry's FIRST display name — the same choice `build_dashboard.read_evidence`
    makes — and it is stored here so the promo table's brand column is a join and not a second map
    built beside the page.
    """
    conn.executemany(
        "INSERT INTO watchlist VALUES (?, ?, ?, ?)",
        [
            (window_id, brand.brand_id, 1 if brand.own else 0, brand.display_names[0])
            for brand in brands
        ],
    )


def add_comments(conn, window_id: str, verdicts: list[dict]) -> None:
    """The comment leg, as `window_summary_5c2.comment_verdicts` returns it.

    A verdict whose reply the parser refused keeps `labels: None` and its reason — it is stored as
    `scored = 0` with a null sentiment, never folded into a class. That is the same discipline the
    producer of those verdicts states: an unreadable answer and "about none of the six" are
    different states, and the empty class is where parse failures hide.
    """
    for row in verdicts:
        labels = row["labels"]
        conn.execute(
            "INSERT INTO comments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                window_id,
                row["channel"],
                row["msg_id"],
                row["task"],
                0 if row["empty_text"] else 1,
                row["language"],
                1 if labels else 0,
                row["unreadable"],
                labels["sentiment"] if labels else None,
                (1 if labels["sarcasm"] else 0) if labels else None,
                len(labels["intents"]) if labels else 0,
            ),
        )
        if labels:
            conn.executemany(
                "INSERT INTO comment_intents VALUES (?, ?, ?, ?)",
                [(window_id, row["channel"], row["msg_id"], name) for name in labels["intents"]],
            )
        conn.executemany(
            "INSERT INTO comment_brands VALUES (?, ?, ?, ?)",
            [(window_id, row["channel"], row["msg_id"], name) for name in row["brands"]],
        )


def add_revised_brands(conn, window_id: str, revision: dict, hits: list[dict]) -> None:
    """The named revision's brand hits, in a table of their own — SPEC 3.21 (1).

    `hits` are `{channel, msg_id, brands}` rows, the shape `add_comments` already reads. The
    revision is stored beside them so the export can NAME which rules the presentation cut matched
    under: a brand table whose matcher is not written down is a table nobody can re-derive.
    """
    conn.execute(
        "INSERT INTO watchlist_revision VALUES (?, ?, ?, ?)",
        (window_id, revision["revision"], revision["dated"], revision["sha256"]),
    )
    conn.executemany(
        f"INSERT INTO {REVISED_BRANDS} VALUES (?, ?, ?, ?)",
        [
            (window_id, row["channel"], row["msg_id"], name)
            for row in hits
            for name in row["brands"]
        ],
    )


def add_markers(conn, window_id: str, leg: str, rows: list[dict]) -> None:
    conn.executemany(
        "INSERT INTO markers VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            (
                window_id,
                leg,
                row["channel"],
                row["msg_id"],
                row["parent_msg_id"],
                row["n_positions"],
                row["unreadable"],
            )
            for row in rows
        ],
    )


def add_positions(conn, window_id: str, rows: list[dict]) -> None:
    for row in rows:
        one = row["position"]
        conn.execute(
            "INSERT INTO positions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,"
            " ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                window_id,
                row["row_id"],
                row["channel"],
                one["carrier"],
                row["msg_id"],
                row["ordinal"],
                row["tier"],
                one["brand_id"],
                one["category"],
                one["price_promo"],
                one["price_old"],
                one["discount_pct_printed"],
                1 if one["discount_footnote"] else 0,
                one["price_qualifier"],
                one["depth"],
                1 if one["depth_disagrees_with_printed"] else 0,
                *(1 if row["presence"][name] else 0 for name in PRESENCE),
                # the item ITSELF, which the layer never held before: the presence flags say a size
                # was printed, and SPEC 3.21 (4) asks which size. Appended after them so the
                # positional INSERT above stays readable against the CREATE TABLE.
                one["brand_raw"],
                one["line"],
                one["size_value"],
                one["size_unit"],
                one["pack_count"],
                one["attribute_pct"],
            ),
        )
        conn.executemany(
            "INSERT INTO position_warnings VALUES (?, ?, ?)",
            [(window_id, row["row_id"], name) for name in row["warnings"]],
        )


# --- reading it back -----------------------------------------------------------------------------


def counts(conn, sql: str, params: tuple = ()) -> dict:
    """`SELECT <key>, COUNT(*) … GROUP BY <key>` as a dict, zero-rows as `{}`."""
    return {key: number for key, number in conn.execute(sql, params) if key is not None}


def spread(values: list[float]) -> dict:
    """n / min / median / max at four decimals — `window_summary_5c2._spread`, to the digit.

    Same rounding and the same `statistics.median`, because this number has to EQUAL the anchor's
    and a second implementation of a median is a second answer waiting to happen.
    """
    if not values:
        return {"n": 0, "min": None, "median": None, "max": None}
    return {
        "n": len(values),
        "min": round(min(values), 4),
        "median": round(statistics.median(values), 4),
        "max": round(max(values), 4),
    }


def _where(
    window_id: str, channel: str | None = None, segment: str | None = None, extra: str = ""
) -> tuple[str, tuple]:
    """The scope of one block, as a WHERE clause and its parameters.

    A segment scope is a subquery against `channels` rather than a list of handles built in Python:
    the join belongs in SQL, and a caller that assembled the handles itself would be a second place
    that decides which channels a segment holds.
    """
    sql = "window_id = ?"
    params: tuple = (window_id,)
    if channel is not None:
        sql += " AND channel = ?"
        params += (channel,)
    if segment is not None:
        sql += " AND channel IN (SELECT channel FROM channels WHERE window_id = ? AND segment = ?)"
        params += (window_id, segment)
    if extra:
        sql += f" AND {extra}"
    return sql, params


def comment_block(
    conn, window_id: str, *, channel: str | None = None, segment: str | None = None, sample: str
) -> dict:
    """The per-head distributions of one comment population — the shape the anchor carries.

    `sample` is `bought` or `payable` and is NOT optional: every rate below divides by rows this
    argument chose, and a default would let a caller print a number without saying what it is about.
    Inside, a second denominator lives beside it — `sarcasm.rate` divides by the rows the parser
    SCORED, never by the rows asked, which is the anchor's own rule.
    """
    if sample not in SAMPLES:
        raise Refusal(f"unknown sample {sample!r} — the two are {sorted(SAMPLES)}")
    where, params = _where(window_id, channel, segment, SAMPLES[sample])
    scored_where = f"{where} AND scored = 1"

    (rows,) = conn.execute(f"SELECT COUNT(*) FROM comments WHERE {where}", params).fetchone()
    (scored,) = conn.execute(
        f"SELECT COUNT(*) FROM comments WHERE {scored_where}", params
    ).fetchone()
    (sarcastic,) = conn.execute(
        f"SELECT COUNT(*) FROM comments WHERE {scored_where} AND sarcasm = 1", params
    ).fetchone()
    intents = counts(
        conn,
        f"SELECT intent, COUNT(*) FROM comment_intents JOIN comments USING (window_id, channel,"
        f" msg_id) WHERE {scored_where} GROUP BY intent",
        params,
    )
    by_language: dict[str, dict] = {}
    for language, sentiment, number in conn.execute(
        f"SELECT language, sentiment, COUNT(*) FROM comments WHERE {scored_where}"
        f" GROUP BY language, sentiment",
        params,
    ):
        by_language.setdefault(language, {})[sentiment] = number
    return {
        "rows": rows,
        "scored": scored,
        "unreadable": {
            "rows": rows - scored,
            "reasons": counts(
                conn,
                f"SELECT unreadable, COUNT(*) FROM comments WHERE {where} AND unreadable IS NOT"
                " NULL GROUP BY unreadable",
                params,
            ),
        },
        "empty_text": {
            "rows": conn.execute(
                f"SELECT COUNT(*) FROM comments WHERE {where} AND has_text = 0", params
            ).fetchone()[0],
            "with_no_intent": conn.execute(
                f"SELECT COUNT(*) FROM comments WHERE {scored_where} AND has_text = 0"
                " AND n_intents = 0",
                params,
            ).fetchone()[0],
        },
        "sentiment": counts(
            conn,
            f"SELECT sentiment, COUNT(*) FROM comments WHERE {scored_where} GROUP BY sentiment",
            params,
        ),
        "sarcasm": {
            "true": sarcastic,
            "false": scored - sarcastic,
            "rate": round(sarcastic / scored, 4) if scored else None,
            "denominator": "scored",
        },
        "intents": {
            "frequency": intents,
            "rows_with_no_intent": conn.execute(
                f"SELECT COUNT(*) FROM comments WHERE {scored_where} AND n_intents = 0", params
            ).fetchone()[0],
            "labels_per_scored_row": round(sum(intents.values()) / scored, 4) if scored else None,
        },
        "language": {
            "rows": counts(
                conn,
                f"SELECT language, COUNT(*) FROM comments WHERE {where} GROUP BY language",
                params,
            ),
            "sentiment": {name: by_language[name] for name in sorted(by_language)},
        },
        "brand_attribution": {
            "rows_with_a_brand": conn.execute(
                f"SELECT COUNT(*) FROM (SELECT DISTINCT channel, msg_id FROM comment_brands JOIN"
                f" comments USING (window_id, channel, msg_id) WHERE {where})",
                params,
            ).fetchone()[0],
            "mentions": counts(
                conn,
                f"SELECT brand_id, COUNT(*) FROM comment_brands JOIN comments USING (window_id,"
                f" channel, msg_id) WHERE {where} GROUP BY brand_id",
                params,
            ),
        },
    }


def marker_block(
    conn, window_id: str, leg: str, *, channel: str | None = None, segment: str | None = None
) -> dict:
    """A page or a post as an ANSWER: it found positions, it found none, or it was unreadable.

    Three states counted apart, the anchor's rule: `n_positions = 0` is a real answer and
    `unreadable` is the instrument failing, and folding the second into the first is how a parser's
    bad day reads as an empty market.
    """
    where, params = _where(window_id, channel, segment, "leg = ?")
    params += (leg,)
    (rows,) = conn.execute(f"SELECT COUNT(*) FROM markers WHERE {where}", params).fetchone()
    (unreadable,) = conn.execute(
        f"SELECT COUNT(*) FROM markers WHERE {where} AND unreadable IS NOT NULL", params
    ).fetchone()
    (found,) = conn.execute(
        f"SELECT COUNT(*) FROM markers WHERE {where} AND unreadable IS NULL AND n_positions > 0",
        params,
    ).fetchone()
    (positions,) = conn.execute(
        f"SELECT COALESCE(SUM(n_positions), 0) FROM markers WHERE {where}", params
    ).fetchone()
    return {
        "rows": rows,
        "with_positions": found,
        "empty": rows - unreadable - found,
        "unreadable": {
            "rows": unreadable,
            "reasons": counts(
                conn,
                f"SELECT unreadable, COUNT(*) FROM markers WHERE {where} AND unreadable IS NOT NULL"
                " GROUP BY unreadable",
                params,
            ),
        },
        "positions": positions,
    }


def position_block(
    conn,
    window_id: str,
    *,
    carrier: str | None = None,
    channel: str | None = None,
    segment: str | None = None,
) -> dict:
    """The tier ladder's distribution and the promo fields counted before they are valued.

    `price_fields_present` is `field IS NOT NULL AND field != 0` and that second clause is not
    decoration: the anchor's test is `one[field] not in (None, False)`, and in Python `0.0 == False`,
    so a zero-valued promo price counts as ABSENT there. Replicated rather than corrected — this
    block has to equal the sealed record, and the divergence would be silent.
    """
    where, params = _where(window_id, channel, segment)
    if carrier is not None:
        where += " AND carrier = ?"
        params += (carrier,)
    (rows,) = conn.execute(f"SELECT COUNT(*) FROM positions WHERE {where}", params).fetchone()
    badge = [
        value / 100
        for (value,) in conn.execute(
            f"SELECT discount_pct_printed FROM positions WHERE {where} AND discount_pct_printed"
            " IS NOT NULL ORDER BY discount_pct_printed",
            params,
        )
    ]
    pair = [
        value
        for (value,) in conn.execute(
            f"SELECT depth FROM positions WHERE {where} AND depth IS NOT NULL ORDER BY depth",
            params,
        )
    ]
    return {
        "rows": rows,
        "tier": counts(
            conn, f"SELECT tier, COUNT(*) FROM positions WHERE {where} GROUP BY tier", params
        ),
        "presence": {
            name: conn.execute(
                f"SELECT COUNT(*) FROM positions WHERE {where} AND presence_{name} = 1", params
            ).fetchone()[0]
            for name in PRESENCE
        },
        "warnings": counts(
            conn,
            f"SELECT warning, COUNT(*) FROM position_warnings JOIN positions USING (window_id,"
            f" row_id) WHERE {where} GROUP BY warning",
            params,
        ),
        "category": counts(
            conn,
            f"SELECT category, COUNT(*) FROM positions WHERE {where} GROUP BY category",
            params,
        ),
        "brand_resolved": conn.execute(
            f"SELECT COUNT(*) FROM positions WHERE {where} AND brand_id IS NOT NULL", params
        ).fetchone()[0],
        "price_fields_present": {
            name: conn.execute(
                f"SELECT COUNT(*) FROM positions WHERE {where} AND {name} IS NOT NULL AND {name}"
                " != 0",
                params,
            ).fetchone()[0]
            for name in PROMO_FIELDS
        },
        "price_fields_absent": {
            name: conn.execute(
                f"SELECT COUNT(*) FROM positions WHERE {where} AND ({name} IS NULL OR {name} = 0)",
                params,
            ).fetchone()[0]
            for name in PROMO_FIELDS
        },
        "price_qualifier": counts(
            conn,
            f"SELECT COALESCE(price_qualifier, 'absent'), COUNT(*) FROM positions WHERE {where}"
            " GROUP BY 1",
            params,
        ),
        "depth": {
            "from_printed_badge": spread(badge),
            "from_price_pair": spread(pair),
            "printed_disagrees_with_computed": conn.execute(
                f"SELECT COUNT(*) FROM positions WHERE {where} AND depth_disagrees_with_printed = 1",
                params,
            ).fetchone()[0],
        },
    }


# --- the metric dictionary's own numbers ---------------------------------------------------------


def quartiles(values: list[float]) -> dict:
    """q1 / q3 beside :func:`spread`'s median. `None` when there are too few values to cut.

    `statistics.quantiles` needs at least two points; a single-row leg gets nulls rather than a
    quartile equal to itself, which would read as a spread that had been measured.
    """
    if len(values) < 2:
        return {"q1": None, "q3": None}
    q1, _, q3 = statistics.quantiles(values, n=4)
    return {"q1": round(q1, 4), "q3": round(q3, 4)}


def sentiment_metrics(conn, window_id: str, *, sample: str, segment: str | None = None) -> dict:
    """NSR and the two negative shares — raw, and after the sarcasm correction.

    The adjustment is the one the T1 badge names: a row whose sarcasm head fired and whose sentiment
    was NOT already negative is re-read as negative. `reclassified` is that count, carried beside the
    share, because the correction has to be visible as a correction — a share that moved with no
    number to explain it is the same number twice.
    """
    block = comment_block(conn, window_id, sample=sample, segment=segment)
    scored = block["scored"]
    counted = block["sentiment"]
    positive, neutral, negative = (
        counted.get(name, 0) for name in ("positive", "neutral", "negative")
    )
    where, params = _where(window_id, None, segment, SAMPLES[sample])
    (reclassified,) = conn.execute(
        f"SELECT COUNT(*) FROM comments WHERE {where} AND scored = 1 AND sarcasm = 1"
        " AND sentiment != 'negative'",
        params,
    ).fetchone()
    return {
        "scored": scored,
        "positive": positive,
        "neutral": neutral,
        "negative": negative,
        "nsr": round((positive - negative) / scored, 4) if scored else None,
        "negative_share": round(negative / scored, 4) if scored else None,
        "reclassified_from_sarcasm": reclassified,
        "negative_share_sarcasm_adjusted": round((negative + reclassified) / scored, 4)
        if scored
        else None,
    }


def share_of_voice(conn, window_id: str, *, sample: str, table: str = ANCHOR_BRANDS) -> dict:
    """Every watchlist brand's share of watchlist mentions — zeros included.

    Left-joined off `watchlist` so the field is the whole watchlist: a brand with no mention in the
    window has a share of 0.0, which is an answer, and dropping it would make the denominator look
    like the set of brands that happened to be talked about.

    ``table`` names which matcher's hits to count (:data:`ANCHOR_BRANDS` / :data:`REVISED_BRANDS`)
    and defaults to the anchor's, so a caller that does not think about revisions gets the matching
    every sealed record was measured under. The dashboard asks for the revised one and labels it.
    """
    if table not in (ANCHOR_BRANDS, REVISED_BRANDS):
        raise Refusal(f"{table!r} is not a brand-hit table")
    where, params = _where(window_id, None, None, SAMPLES[sample])
    mentions = {
        brand: number
        for brand, number in conn.execute(
            f"SELECT brand_id, COUNT(*) FROM {table} JOIN comments USING (window_id,"
            f" channel, msg_id) WHERE {where} GROUP BY brand_id",
            params,
        )
    }
    field = conn.execute(
        "SELECT brand_id, own FROM watchlist WHERE window_id = ? ORDER BY brand_id", (window_id,)
    ).fetchall()
    total = sum(mentions.values())
    return {
        "mentions": {brand: mentions.get(brand, 0) for brand, _ in field},
        "share": {
            brand: round(mentions.get(brand, 0) / total, 4) if total else None for brand, _ in field
        },
        "total_mentions": total,
        "own_brands": [brand for brand, own in field if own],
    }


def aspect_share(conn, window_id: str, *, sample: str, segment: str | None = None) -> dict:
    """The aspect profile — a share over LABELS, with the rows that carry none named beside it."""
    block = comment_block(conn, window_id, sample=sample, segment=segment)
    labels = block["intents"]["frequency"]
    total = sum(labels.values())
    return {
        "labels": labels,
        "total_labels": total,
        "share": {name: round(number / total, 4) for name, number in labels.items()}
        if total
        else {},
        "rows_with_no_aspect": block["intents"]["rows_with_no_intent"],
        "scored": block["scored"],
    }


def depth_readings(conn, window_id: str, *, carrier: str | None = None) -> dict:
    """Both depth readings with quartiles — the arithmetic pair and the printed badge.

    Neither corrects the other and neither is dropped: SPEC 3.18 (1) keeps them side by side, and
    the count of rows where they DISAGREE is reported rather than resolved.
    """
    block = position_block(conn, window_id, carrier=carrier)
    where, params = _where(window_id)
    if carrier is not None:
        where += " AND carrier = ?"
        params += (carrier,)
    pair = [
        value
        for (value,) in conn.execute(
            f"SELECT depth FROM positions WHERE {where} AND depth IS NOT NULL ORDER BY depth",
            params,
        )
    ]
    badge = [
        value / 100
        for (value,) in conn.execute(
            f"SELECT discount_pct_printed FROM positions WHERE {where} AND discount_pct_printed"
            " IS NOT NULL ORDER BY discount_pct_printed",
            params,
        )
    ]
    return {
        "from_price_pair": block["depth"]["from_price_pair"] | quartiles(pair),
        "from_printed_badge": block["depth"]["from_printed_badge"] | quartiles(badge),
        "printed_disagrees_with_computed": block["depth"]["printed_disagrees_with_computed"],
        "position_rows": block["rows"],
    }


def promo_pressure(conn, window_id: str) -> dict:
    """How often each brand appears in the window's promo material at all."""
    (rows,) = conn.execute(
        "SELECT COUNT(*) FROM positions WHERE window_id = ?", (window_id,)
    ).fetchone()
    per_brand = counts(
        conn,
        "SELECT brand_id, COUNT(*) FROM positions WHERE window_id = ? GROUP BY brand_id",
        (window_id,),
    )
    return {
        "position_rows": rows,
        "by_brand": per_brand,
        "share": {brand: round(number / rows, 4) for brand, number in per_brand.items()}
        if rows
        else {},
        "rows_with_no_resolved_brand": conn.execute(
            "SELECT COUNT(*) FROM positions WHERE window_id = ? AND brand_id IS NULL", (window_id,)
        ).fetchone()[0],
    }


def promo_positions(conn, window_id: str, chains: tuple) -> list[dict]:
    """Every position of the window as a ROW — the promo answer of SPEC 3.21 (4).

    **The old price is not here, and neither is anything derived from it.** `depth` is the PRINTED
    badge's own reading (SPEC 3.18 (1): the depth instrument is the promo price and the printed
    −N%), never the `depth` COLUMN, which is the arithmetic of the extracted `price_old`. The
    difference is not stylistic: a reader holding the promo price and the arithmetic depth has
    `price_old = promo / (1 − depth)` back to the kopiyka, and 3.17 (3) keeps that number off every
    surface. The arithmetic reading stays where it already lawfully lives — the window's aggregate
    in :func:`depth_readings` — and is not carried per row.

    **A field the row does not carry is ABSENT**, not null-filled: an empty `attribute_pct` key says
    no fat percentage was printed, where `0.0` would say it was printed as zero. The tier ladder's
    presence flags stay in :func:`position_block`; this table is what the flags were flags ABOUT.

    The brand column is a LEFT JOIN on the watchlist: 65 of window-1's rows carry a trade mark the
    registry does not resolve, and those rows keep their printed name with no id and no `own` flag —
    an unresolved mark is not evidence that the brand is a competitor.
    """
    rows: list[dict] = []
    order: list[tuple] = []
    for (
        row_id,
        brand_id,
        display,
        own,
        brand_raw,
        line,
        category,
        size_value,
        size_unit,
        pack_count,
        attribute_pct,
        source_id,
        carrier,
        price_promo,
        printed_pct,
        tier,
        channel,
        msg_id,
        ordinal,
    ) in conn.execute(
        "SELECT p.row_id, p.brand_id, w.display, w.own, p.brand_raw, p.line, p.category,"
        " p.size_value, p.size_unit, p.pack_count, p.attribute_pct, ch.source_id, p.carrier,"
        " p.price_promo, p.discount_pct_printed, p.tier, p.channel, p.msg_id, p.ordinal"
        " FROM positions p JOIN channels ch USING (window_id, channel)"
        " LEFT JOIN watchlist w ON w.window_id = p.window_id AND w.brand_id = p.brand_id"
        " WHERE p.window_id = ?",
        (window_id,),
    ):
        brand = {"display": display or brand_raw}
        if brand_id is not None:
            brand |= {"id": brand_id, "own": bool(own)}
        rows.append(
            {
                "row_id": row_id,
                "brand": brand,
                "item": _present(
                    {
                        "line": line,
                        "category": category,
                        "size_value": size_value,
                        "size_unit": size_unit,
                        "pack_count": pack_count,
                        "attribute_pct": attribute_pct,
                    }
                ),
                "chain": {"id": source_id, "named_by_amendment_3_20": source_id in chains},
                "carrier": carrier,
                "tier": tier,
                "evidence": {"channel": channel, "msg_id": msg_id},
            }
            | _present(
                {
                    "promo_price": price_promo,
                    "printed_pct": printed_pct,
                    "depth": round(printed_pct / 100, 4) if printed_pct is not None else None,
                }
            )
        )
        order.append(((display or brand_raw or "").casefold(), source_id, channel, msg_id, ordinal))
    # sorted HERE and not by the query: SQLite's NOCASE folds ASCII only, so «ПростоНаше» and
    # «Простонаше» would rank by code point and the rule would be one no reader could state.
    # `casefold` is Unicode-aware, and the key is the order the operator reads — brand first, then
    # the chain, then the message the row came out of. Sorted by INDEX so no comparison ever
    # reaches the row dictionaries themselves.
    return [rows[index] for index in sorted(range(len(rows)), key=order.__getitem__)]


def _present(fields: dict) -> dict:
    """The keys that have a value. Absence is the record's way of saying nothing was printed."""
    return {name: value for name, value in fields.items() if value is not None}


def promo_by_chain(conn, window_id: str, chains: tuple) -> dict:
    """Positions per chain, split by carrier — every chain the law names, present or empty.

    `chains` arrives from the caller and every one of them is a KEY here whether it carried a row or
    not: SPEC 3.20 (6) puts Маркетопт on the promo surface, and a surface that renders whatever the
    GROUP BY returned would drop a chain the day it goes quiet.
    """
    found: dict[str, dict] = {}
    for source_id, carrier, number in conn.execute(
        "SELECT ch.source_id, p.carrier, COUNT(*) FROM positions p JOIN channels ch"
        " USING (window_id, channel) WHERE p.window_id = ? GROUP BY 1, 2 ORDER BY 1, 2",
        (window_id,),
    ):
        found.setdefault(source_id, {})[carrier] = number
    return {
        source_id: {
            "position_rows": sum(found.get(source_id, {}).values()),
            "by_carrier": found.get(source_id, {}),
            "named_by_amendment_3_20": source_id in chains,
        }
        for source_id in sorted(set(found) | set(chains))
    }


def coverage(conn, window_id: str) -> dict:
    """Channels and segments that produced a row, against what the registry holds.

    Both denominators come from the `windows` row — the registry's own size — and not from the
    evidence, because a coverage figure whose denominator is the evidence is always 100%.
    """
    (channels,) = conn.execute(
        "SELECT registry_channels FROM windows WHERE window_id = ?", (window_id,)
    ).fetchone()
    (segments,) = conn.execute(
        "SELECT COUNT(*) FROM segments WHERE window_id = ?", (window_id,)
    ).fetchone()
    (with_rows,) = conn.execute(
        "SELECT COUNT(*) FROM channels WHERE window_id = ?", (window_id,)
    ).fetchone()
    (segments_with_rows,) = conn.execute(
        "SELECT COUNT(DISTINCT segment) FROM channels WHERE window_id = ?", (window_id,)
    ).fetchone()
    return {
        "channels": {
            "with_a_row": with_rows,
            "in_registry": channels,
            "share": round(with_rows / channels, 4) if channels else None,
        },
        "segments": {
            "with_a_row": segments_with_rows,
            "in_registry": segments,
            "share": round(segments_with_rows / segments, 4) if segments else None,
        },
    }


def channels_with(
    conn, window_id: str, table: str, *, leg: str | None = None, segment: str | None = None
) -> list[str]:
    """The channels one table holds rows for, sorted.

    `leg` and `segment` are BOUND parameters and not an `extra` clause spliced into the SQL: the
    values come out of the database and go straight back into it, and a filter that arrives as text
    is one refactor away from carrying something that was never meant to be SQL. The table name is
    the only thing interpolated, and it is always a literal at the call site.
    """
    sql = f"SELECT DISTINCT channel FROM {table} WHERE window_id = ?"
    params: tuple = (window_id,)
    if leg is not None:
        sql += " AND leg = ?"
        params += (leg,)
    if segment is not None:
        sql += " AND segment = ?"
        params += (segment,)
    return [handle for (handle,) in conn.execute(sql + " ORDER BY channel", params)]


def registry_segments(conn, window_id: str) -> list[tuple[str, int]]:
    """(segment, how many registry channels it holds), sorted — the T3 screen's card list."""
    return list(
        conn.execute(
            "SELECT segment, registry_channels FROM segments WHERE window_id = ? ORDER BY segment",
            (window_id,),
        )
    )


def sample_rows(conn, window_id: str, sample: str) -> int:
    """How many comment rows one named sample holds — the denominator, by name."""
    if sample not in SAMPLES:
        raise Refusal(f"unknown sample {sample!r} — the two are {sorted(SAMPLES)}")
    where, params = _where(window_id, extra=SAMPLES[sample])
    return conn.execute(f"SELECT COUNT(*) FROM comments WHERE {where}", params).fetchone()[0]


# --- the convergence mirror ----------------------------------------------------------------------


def mirror(conn, window_id: str) -> dict:
    """`results/window_summary_5c2.json`'s five aggregate blocks, re-derived from the database.

    Not part of what the dashboard reads — this is the gate's other side. The anchor was computed
    by a different program over the same evidence, so building its shape out of SQL and comparing
    every numeric leaf turns "the export agrees with the sealed record" from four spot checks into
    902 of them. The comment leg is mirrored on the BOUGHT sample, because that is the population
    the anchor was measured on; the payable sample is a dashboard figure, not a convergence one.
    """
    window = conn.execute(
        "SELECT bought, leaflet_pages, post_texts FROM windows WHERE window_id = ?", (window_id,)
    ).fetchone()
    (leaflet_posts,) = conn.execute(
        "SELECT COUNT(DISTINCT parent_msg_id) FROM markers WHERE window_id = ? AND leg = ?",
        (window_id, "leaflet_page"),
    ).fetchone()
    return {
        "populations_registered": dict(zip(("comment", "leaflet_page", "post_text"), window)),
        "comment": {
            "total": comment_block(conn, window_id, sample="bought"),
            "per_channel": {
                handle: comment_block(conn, window_id, channel=handle, sample="bought")
                for handle in channels_with(conn, window_id, "comments")
            },
        },
        "leaflet_page": {
            "posts": leaflet_posts,
            "total": marker_block(conn, window_id, "leaflet_page"),
            "per_channel": {
                handle: marker_block(conn, window_id, "leaflet_page", channel=handle)
                for handle in channels_with(conn, window_id, "markers", leg="leaflet_page")
            },
        },
        "post_text": {
            "total": marker_block(conn, window_id, "post_text"),
            "per_channel": {
                handle: marker_block(conn, window_id, "post_text", channel=handle)
                for handle in channels_with(conn, window_id, "markers", leg="post_text")
            },
        },
        "position_row": {
            "total": position_block(conn, window_id),
            "by_carrier": {
                carrier: position_block(conn, window_id, carrier=carrier)
                for carrier in ("leaflet_page", "post_text")
            },
            "per_channel": {
                handle: position_block(conn, window_id, channel=handle)
                for handle in channels_with(conn, window_id, "positions")
            },
        },
    }


def numeric_leaves(node, path: str = "") -> dict:
    """Every number in a nested record, by dotted path. Booleans are not numbers here."""
    out: dict[str, float] = {}
    if isinstance(node, dict):
        for key, value in node.items():
            out |= numeric_leaves(value, f"{path}.{key}" if path else str(key))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            out |= numeric_leaves(value, f"{path}[{index}]")
    elif isinstance(node, (int, float)) and not isinstance(node, bool):
        out[path] = node
    return out


def converge(anchor: dict, built: dict) -> dict:
    """Every numeric leaf of the anchor's five blocks against the same leaf of the mirror.

    Three sets come back and all three are reported: `agreed`, `disagreed` and `missing` — a leaf
    the anchor carries and the mirror has no answer for. Silence on the third would let a mirror
    that computed nothing at all pass with an empty disagreement list.
    """
    blocks = ("populations_registered", "comment", "leaflet_page", "post_text", "position_row")
    want = numeric_leaves({name: anchor[name] for name in blocks})
    got = numeric_leaves({name: built[name] for name in blocks})
    return {
        "leaves": len(want),
        "agreed": sorted(path for path, value in want.items() if got.get(path) == value),
        "disagreed": {
            path: {"anchor": value, "database": got[path]}
            for path, value in want.items()
            if path in got and got[path] != value
        },
        "missing": sorted(set(want) - set(got)),
        "extra": sorted(set(got) - set(want)),
    }


def rows_as_json(conn, sql: str, params: tuple = ()) -> str:
    """A query's rows as a JSON array of objects — for showing a cut in a report."""
    cursor = conn.execute(sql, params)
    names = [column[0] for column in cursor.description]
    return json.dumps([dict(zip(names, row)) for row in cursor], ensure_ascii=False, indent=2)
