"""S3 — price and depth per SKU, per week, per chain. SQL only, no model.

`positions` carries no date: a position is a row on a leaflet page, and the page's date is the
POST's. So the week is derived from the store the way the promo tables' schema comment says it is
— «week is derived from the thread root's post date at query time» — and it is derived ONCE, into
a SQLite scalar function the aggregation calls. Everything above that is one statement of SQL, so
a recompute cannot drift from a second implementation of the same grouping.

An empty week is ABSENT, never `0`. A chain that ran no promo in week 32 did not run a promo worth
zero hryvnia, and a screen that renders the zero invites the customer to read a flat line as a
price collapse. This is asserted in both directions in `tests/test_trends_sql.py`.

Weeks are ISO weeks (`%G-W%V`), so the label sorts lexicographically and a year boundary does not
put week 1 before week 52.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from market_pulse import aggregates

REPO_ROOT = Path(__file__).resolve().parents[2]
STORES = (REPO_ROOT / "data" / "raw" / "posts", REPO_ROOT / "data" / "raw_r2" / "posts")

SKU = "brand_raw, line, size_value, size_unit"
"""What makes two positions the same SKU. The four fields SPEC 3.21 (4) asks for, and no price:
a SKU whose identity contained its own promo price would have one row per promo and no trend."""

PREFERRED_CARRIER = "leaflet_page"
"""Which leg wins when both read the same SKU off the same message — ruling 03.09 (b), fork 2.

A post can be both a leaflet page and a text price post, and the C2 window holds 7 row_ids stored
under both carriers. Those are two genuine paid readings and `positions` keeps them both, but a
trend must not COUNT one promo twice: `n` would be 2 for one price and the mean would be that price
weighted double. So the aggregation takes one row per (window, channel, msg_id, SKU) and prefers the
leaflet page — the carrier that carries the printed badge and the old price the depth is checked
against. Measured, not assumed: over w2 exactly ONE (brand, product, volume) triple is read by both
legs off one message (`@forainfo:6056`), which is why this rule exists and how small it is.

The same string as `loop.CARRIER`, kept here so this module reads the store's vocabulary without
importing the collection loop; `tests/test_trends_sql.py` holds the two against each other."""


def deduped(source: str) -> str:
    """The CTE both statements below read, over the rows `aggregates.positions_source` hands them.

    The screen's population is decided in ONE place ((mm) 2(c)): a window or the deduped union of
    all of them, minus the channels the live registry stopped collecting. This layer is only the
    leg-preference rule on top of whatever that returned — a second `WHERE window_id = ?` here
    would be a second answer to «which rows are on the screen».

    The partition lost `window_id` with that move and the rule did not change: the source already
    returns one row per `(carrier, row_id)`, so for one window the key is the same set it always
    was, and over the union a SKU read off one message stays ONE group instead of splitting per
    window and being counted twice ([[a_fold_is_not_a_membership_test]]).

    When BOTH legs read the same SKU off one message, the leaflet page's rows are the ones that
    count and the text leg's are dropped.

    **It drops a LEG, not a row, and that is the correction the measurement forced.** Ruling 03.09
    (b) names the key (window, channel, msg_id, brand, product, volume) with no carrier in it, and
    taking ONE row per that key drops 39 rows over 35 groups in this store — of which only ONE group
    spans carriers, the case the ruling was ruling on. The other 34 are two readings of one SKU by
    ONE leg, 24 of them holding more than one distinct promo price (`@atb_market_official:4359`
    prints Активіа Біфідойогурт 260 г at 23.9 AND 24.7), and 2 of them sit inside the SEALED w1
    window. Those are two promos, not one promo counted twice — and «prefer `leaflet_page`» cannot
    even be applied to a group with a single carrier, so it would fall through to an arbitrary
    `row_id` ([[a_gate_wider_than_the_order_it_guards]]).

    So the partition selects the preferred LEG and keeps every row of it. `MIN(carrier <>
    'leaflet_page')` over the group is 0 when any row is a leaflet page and 1 when none is, and a
    row is kept when its own leg matches that. Nothing is ORDERED, so there is no tiebreak to be
    arbitrary about, and two runs over one store return the same rows — which is what makes
    `make tick` idempotent on this table.
    """
    return f"""
one_leg_per_sku AS (
    SELECT * FROM (
        SELECT *,
               MIN(carrier <> '{PREFERRED_CARRIER}') OVER (
                   PARTITION BY channel, msg_id, {SKU}) AS best_leg
          FROM ({source}))
     WHERE (carrier <> '{PREFERRED_CARRIER}') = best_leg)
"""


def iso_week(when: str) -> str:
    return datetime.fromisoformat(when).strftime("%G-W%V")


def post_weeks(roots=STORES) -> dict[tuple[str, int], str]:
    """(channel, msg_id) -> ISO week, read off the raw store.

    Both roots: `data/raw/` is the archive and `data/raw_r2/` the live root, and a position bought
    from a topped-up channel has its post in the second one only.
    """
    weeks: dict[tuple[str, int], str] = {}
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.glob("*.jsonl")):
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                record = json.loads(line)
                weeks[(record["channel"], int(record["msg_id"]))] = iso_week(record["date"])
    return weeks


def bind_weeks(conn: sqlite3.Connection, weeks: dict[tuple[str, int], str]) -> None:
    """Bind `week_of(channel, msg_id)` on this connection.

    A function and not a temp table on purpose: a temp table would be a second copy of the store's
    dates living inside the db, and the next reader would have to know which of the two was stale.
    """
    conn.create_function("week_of", 2, lambda channel, msg_id: weeks.get((channel, int(msg_id))))


def trend_sql(source: str) -> str:
    """One statement. `week_of` returning NULL for a position whose post is not in the store drops
    the row rather than bucketing it under an invented week — an unknown week is not a week."""
    return f"""
WITH {deduped(source)}
SELECT week_of(channel, msg_id) AS week,
       channel                  AS chain,
       {SKU},
       COUNT(*)                 AS n,
       MIN(price_promo)         AS price_min,
       MAX(price_promo)         AS price_max,
       AVG(price_promo)         AS price_mean,
       AVG(depth)               AS depth_mean
  FROM one_leg_per_sku
 WHERE price_promo IS NOT NULL
   AND week_of(channel, msg_id) IS NOT NULL
 GROUP BY week, chain, {SKU}
 ORDER BY week, chain, {SKU}
"""


def sku_trends(
    conn: sqlite3.Connection, window_id: str, excluded: tuple[str, ...] = ()
) -> list[dict]:
    """Price per SKU per week per chain, as rows. `bind_weeks` first."""
    source, params = aggregates.positions_source(window_id, excluded)
    conn.row_factory = sqlite3.Row
    return [dict(row) for row in conn.execute(trend_sql(source), params)]


def depth_sql(source: str) -> str:
    """Depth per chain and per brand — a WINDOW aggregate, SPEC 3.22 (1). It never sits beside a
    row's own promo price, because `promo ÷ (1 − depth)` reconstructs the old price the screen may
    not print (3.21 (4)); that is why depth leaves `positions` through this query and not through
    `sku_trends`."""
    return f"""
WITH {deduped(source)}
SELECT week_of(channel, msg_id) AS week,
       channel                  AS chain,
       brand_raw                AS brand,
       COUNT(*)                 AS n,
       AVG(depth)               AS depth_mean
  FROM one_leg_per_sku
 WHERE depth IS NOT NULL
   AND week_of(channel, msg_id) IS NOT NULL
 GROUP BY week, chain, brand
 ORDER BY week, chain, brand
"""


def depth_trends(
    conn: sqlite3.Connection, window_id: str, excluded: tuple[str, ...] = ()
) -> list[dict]:
    source, params = aggregates.positions_source(window_id, excluded)
    conn.row_factory = sqlite3.Row
    return [dict(row) for row in conn.execute(depth_sql(source), params)]


def by_week(rows: list[dict]) -> dict[str, list[dict]]:
    """Rows grouped under their week. A week with no rows is ABSENT — it has no key here.

    The whole point of the function. `{week: []}` and `{week: {"price": 0}}` both render as a
    number on a screen, and neither is what "this chain ran no promo that week" means.
    """
    out: dict[str, list[dict]] = {}
    for row in rows:
        out.setdefault(row["week"], []).append(row)
    return out


def build(
    conn: sqlite3.Connection,
    window_id: str,
    weeks: dict | None = None,
    excluded: tuple[str, ...] = (),
) -> dict:
    """The whole S3 reading: bind the weeks, run the two statements, group by week."""
    bind_weeks(conn, post_weeks() if weeks is None else weeks)
    skus = sku_trends(conn, window_id, excluded)
    depths = depth_trends(conn, window_id, excluded)
    return {
        "window_id": window_id,
        "weeks": sorted(by_week(skus)),
        "sku_price_by_week": by_week(skus),
        "depth_by_week": by_week(depths),
        "sku_rows": len(skus),
        "depth_rows": len(depths),
    }
