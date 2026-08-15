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
    window_id     TEXT PRIMARY KEY,
    anchor        TEXT NOT NULL,
    days          INTEGER NOT NULL,
    since         TEXT NOT NULL,
    until         TEXT NOT NULL,
    bought        INTEGER NOT NULL,
    payable       INTEGER NOT NULL,
    text_less     INTEGER NOT NULL,
    leaflet_pages INTEGER NOT NULL,
    post_texts    INTEGER NOT NULL
);

CREATE TABLE channels (
    window_id   TEXT NOT NULL,
    channel     TEXT NOT NULL,
    source_id   TEXT NOT NULL,
    source_type TEXT NOT NULL,
    segment     TEXT,
    PRIMARY KEY (window_id, channel)
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


def add_window(conn, window_id: str, anchor: dict, populations: dict, split: dict) -> None:
    """One window's identity and its two populations, stored side by side and labelled.

    `populations` is the SEALED registration's (what was bought); `split` is what the rows on disk
    say about text. Storing `bought` and `payable` in the same row is the prep-a §1.5 memo made
    structural: collected is not payable, and a table that held one number could not say so.
    """
    conn.execute(
        "INSERT INTO windows VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
            " ?, ?, ?, ?, ?)",
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


def _where(window_id: str, channel: str | None, extra: str = "") -> tuple[str, tuple]:
    sql = "window_id = ?"
    params: tuple = (window_id,)
    if channel is not None:
        sql += " AND channel = ?"
        params += (channel,)
    if extra:
        sql += f" AND {extra}"
    return sql, params


def comment_block(conn, window_id: str, *, channel: str | None = None, sample: str) -> dict:
    """The per-head distributions of one comment population — the shape the anchor carries.

    `sample` is `bought` or `payable` and is NOT optional: every rate below divides by rows this
    argument chose, and a default would let a caller print a number without saying what it is about.
    Inside, a second denominator lives beside it — `sarcasm.rate` divides by the rows the parser
    SCORED, never by the rows asked, which is the anchor's own rule.
    """
    if sample not in SAMPLES:
        raise Refusal(f"unknown sample {sample!r} — the two are {sorted(SAMPLES)}")
    where, params = _where(window_id, channel, SAMPLES[sample])
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


def marker_block(conn, window_id: str, leg: str, *, channel: str | None = None) -> dict:
    """A page or a post as an ANSWER: it found positions, it found none, or it was unreadable.

    Three states counted apart, the anchor's rule: `n_positions = 0` is a real answer and
    `unreadable` is the instrument failing, and folding the second into the first is how a parser's
    bad day reads as an empty market.
    """
    where, params = _where(window_id, channel, "leg = ?")
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


def position_block(conn, window_id: str, *, carrier: str | None = None, channel=None) -> dict:
    """The tier ladder's distribution and the promo fields counted before they are valued.

    `price_fields_present` is `field IS NOT NULL AND field != 0` and that second clause is not
    decoration: the anchor's test is `one[field] not in (None, False)`, and in Python `0.0 == False`,
    so a zero-valued promo price counts as ABSENT there. Replicated rather than corrected — this
    block has to equal the sealed record, and the divergence would be silent.
    """
    where, params = _where(window_id, channel)
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


def channels_with(conn, window_id: str, table: str, extra: str = "") -> list[str]:
    sql = f"SELECT DISTINCT channel FROM {table} WHERE window_id = ?"
    if extra:
        sql += f" AND {extra}"
    return [handle for (handle,) in conn.execute(sql + " ORDER BY channel", (window_id,))]


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
                for handle in channels_with(conn, window_id, "markers", "leg = 'leaflet_page'")
            },
        },
        "post_text": {
            "total": marker_block(conn, window_id, "post_text"),
            "per_channel": {
                handle: marker_block(conn, window_id, "post_text", channel=handle)
                for handle in channels_with(conn, window_id, "markers", "leg = 'post_text'")
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
