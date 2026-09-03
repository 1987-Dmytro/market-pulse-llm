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

DEDUPED = f"""
one_row_per_sku AS (
    SELECT * FROM (
        SELECT *,
               ROW_NUMBER() OVER (
                   PARTITION BY window_id, channel, msg_id, {SKU}
                   ORDER BY carrier <> '{PREFERRED_CARRIER}', row_id) AS leg_rank
          FROM positions
         WHERE window_id = ?)
     WHERE leg_rank = 1)
"""
"""The one source both statements below read. `carrier <> 'leaflet_page'` sorts the preferred leg
first (0 before 1) and `row_id` breaks the remaining tie, so the choice is TOTAL: two runs over one
store pick the same row, which is what makes `make tick` idempotent on this table."""


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


TREND_SQL = f"""
WITH {DEDUPED}
SELECT week_of(channel, msg_id) AS week,
       channel                  AS chain,
       {SKU},
       COUNT(*)                 AS n,
       MIN(price_promo)         AS price_min,
       MAX(price_promo)         AS price_max,
       AVG(price_promo)         AS price_mean,
       AVG(depth)               AS depth_mean
  FROM one_row_per_sku
 WHERE price_promo IS NOT NULL
   AND week_of(channel, msg_id) IS NOT NULL
 GROUP BY week, chain, {SKU}
 ORDER BY week, chain, {SKU}
"""
"""One statement. `week_of` returning NULL for a position whose post is not in the store drops the
row rather than bucketing it under an invented week — an unknown week is not a week."""


def sku_trends(conn: sqlite3.Connection, window_id: str) -> list[dict]:
    """Price per SKU per week per chain, as rows. `bind_weeks` first."""
    conn.row_factory = sqlite3.Row
    return [dict(row) for row in conn.execute(TREND_SQL, (window_id,))]


DEPTH_SQL = f"""
WITH {DEDUPED}
SELECT week_of(channel, msg_id) AS week,
       channel                  AS chain,
       brand_raw                AS brand,
       COUNT(*)                 AS n,
       AVG(depth)               AS depth_mean
  FROM one_row_per_sku
 WHERE depth IS NOT NULL
   AND week_of(channel, msg_id) IS NOT NULL
 GROUP BY week, chain, brand
 ORDER BY week, chain, brand
"""
"""Depth per chain and per brand — a WINDOW aggregate, SPEC 3.22 (1). It never sits beside a row's
own promo price, because `promo ÷ (1 − depth)` reconstructs the old price the screen may not print
(3.21 (4)); that is why depth leaves `positions` through this query and not through `sku_trends`."""


def depth_trends(conn: sqlite3.Connection, window_id: str) -> list[dict]:
    conn.row_factory = sqlite3.Row
    return [dict(row) for row in conn.execute(DEPTH_SQL, (window_id,))]


def by_week(rows: list[dict]) -> dict[str, list[dict]]:
    """Rows grouped under their week. A week with no rows is ABSENT — it has no key here.

    The whole point of the function. `{week: []}` and `{week: {"price": 0}}` both render as a
    number on a screen, and neither is what "this chain ran no promo that week" means.
    """
    out: dict[str, list[dict]] = {}
    for row in rows:
        out.setdefault(row["week"], []).append(row)
    return out


def build(conn: sqlite3.Connection, window_id: str, weeks: dict | None = None) -> dict:
    """The whole S3 reading: bind the weeks, run the two statements, group by week."""
    bind_weeks(conn, post_weeks() if weeks is None else weeks)
    skus, depths = sku_trends(conn, window_id), depth_trends(conn, window_id)
    return {
        "window_id": window_id,
        "weeks": sorted(by_week(skus)),
        "sku_price_by_week": by_week(skus),
        "depth_by_week": by_week(depths),
        "sku_rows": len(skus),
        "depth_rows": len(depths),
    }
