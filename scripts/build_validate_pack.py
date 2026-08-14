#!/usr/bin/env python3
"""The 5c2-validate sitting pack — SPEC 3.18 (6), drawn under a recorded seed and never picked.

The phase does not close without an operator sitting: at least five leaflet posts and five
comments, ORIGINAL beside VERDICT, in a form the operator can check against reality. This builds
that pack — `results/validate_5c2_pack.json` and the Russian rendering
`results/validate_5c2_pack.html` the sitting is read from.

**Drawn, not picked.** :data:`SEED` is a constant in this file and it is written into the record;
the draw is `random.Random(f"{SEED}:{stratum}").sample` over SORTED ids — see :func:`draw` for why
the stratum is in the seed. Two strata, both stated in the record. Neither keys on whether the
output looks CORRECT; one of them does key on whether the instrument produced output at all, and
says so:

* leaflet posts — the pages of a post either yielded positions or they did not, and a post that
  yielded none cannot answer "field by field, what made each a POSITION". Eleven of the nineteen
  posts yielded, so a blind draw of five could show the operator one. Four are drawn from the
  posts that yielded and two from those that did not, because «this leaflet was read and had
  nothing of ours» is itself a claim worth checking against the pictures.
* comments — one per channel for the FIVE channels with the most rows in the window, seeded within
  each. Two channels are 73.8% of the window, so an unstratified draw of five is a draw about
  @matusi_ukr.

**Nothing here computes an aggregate.** The captions come from `results/window_summary_5c2.json`,
and the pack refuses unless that record was written over the same bytes this one reads — a
sitting whose "3.4% of the channel" was measured on a different disk than the row beside it is
worse than a sitting with no caption at all.

**One file outside `data/derived/` and `results/`.** `config/registry.yaml`, reached only through
the sealed registration's own pin (`window_summary_5c2.registry_through_the_seal`), because the
brand column 3.18 (6) asks for is a watchlist match and the pack has to run the SAME matcher on the
shown row that the aggregate beside it was built with. A registry that moved since the run is a
refusal here, not a differently-measured brand column.

**What it refuses.** A missing source, by name. A page image whose bytes no longer hash to the
`image_sha256` the run recorded — "the page as it was SENT" has to be provable and not merely
displayed. An aggregate record out of step with the evidence. And it pre-fills no `findings` slot.

    PYTHONPATH=src python3 scripts/build_validate_pack.py
    PYTHONPATH=src python3 scripts/build_validate_pack.py --derived-root <sandbox>   # the control
"""

import argparse
import html
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import window_summary_5c2 as summary  # noqa: E402

from market_pulse import loop, positions, prompts  # noqa: E402

SUMMARY = REPO_ROOT / "results" / "window_summary_5c2.json"
OUT = REPO_ROOT / "results" / "validate_5c2_pack.json"
PAGE = REPO_ROOT / "results" / "validate_5c2_pack.html"

SEED = 42
"""The recorded seed. `scripts/build_sitting_pack.py`'s constant, kept: the draws are over
different populations, so sharing the number costs nothing and the house has one seed to look for.
Changing it redraws the sitting, which is a decision and not a tweak."""

LEAFLET_YIELDED, LEAFLET_EMPTY = 4, 2
COMMENT_CHANNELS = 5

FINDINGS_LAW = (
    "Findings are the operator's reactions, recorded here as `ratified` or `disputed` with a note."
    " SPEC 3.18 (6)(c): they belong to the REVIEW class of 3.16 (1) and become watchlist, lexicon"
    " or prompt-revision ORDERS — never re-scored numbers and never a moved bar. The team lead"
    " fills them DURING the sitting; this file ships every slot empty."
)

FINDINGS_LAW_RU = (
    "Вердикты сидения — это ORDERS класса REVIEW 3.16 (1): watchlist, лексикон или ревизия"
    " промпта. НИКОГДА не пересчитанные числа и НИКОГДА не сдвинутая планка."
)

PRICE_OLD_FLAG = (
    "SPEC 3.18 (1): извлечённая старая цена — ПОМЕЧЕННЫЙ вход глубины, а не цена. На популяции B′"
    " она верна как ЧИСЛО лишь на 33 из 80 пар; она не выходит ни на одну поверхность, которая"
    " печатает её как цену, и никакое «было/стало» на ней не строится. Здесь она показана"
    " ИМЕННО как вход — чтобы оператор мог сверить её с перечёркнутым числом на картинке."
)

IMAGE_PREFIX = "../"
"""How the rendering points at a page. The HTML lives in `results/` and the record stores the page
path REPO-relative (the team-lead ruling on Dv264), so `../<path>` resolves for a browser opened
inside the checkout — and the bytes of this file do not depend on where `--out` was pointed, which
is what keeps the determinism pair honest. An absolute path would name one machine."""


def rel(path: Path) -> str:
    return summary.rel(path)


def read_json(path: Path) -> dict:
    return json.loads(summary.read_text_or_refuse(path))


# --- the draw --------------------------------------------------------------------------------


def draw(pool: list, count: int, stratum: str, seed: int = SEED) -> list:
    """`count` from a SORTED pool, under a seed DERIVED from the stratum's name.

    Sorted first and always: `sample` over a list whose order came off a filesystem glob would be
    reproducible only on the machine that built it.

    The stratum is in the seed, and that is a defect fix rather than a flourish.
    `build_sitting_pack.draw` re-seeds each stratum with the SAME constant, and one `Random(42)`
    asked for one element out of pools of 242, 223 and 222 answers the same INDEX for all three:
    the first version of this pack drew rank **163 of 242, 163 of 223 and 163 of 222** — three of
    five comments at one position. The ids differ and nobody picked them, but five draws that share
    an index are not five independent draws, and "drawn under a recorded seed" has to mean more
    than "nobody typed the ids". `f"{seed}:{stratum}"` gives each stratum its own stream and stays
    exactly as reproducible: the record carries both halves.
    """
    if len(pool) < count:
        raise SystemExit(
            f"{len(pool)} rows in a stratum the draw needs {count} from — the pack cannot show the"
            " operator rows that do not exist, and shrinking the draw silently would hide it"
        )
    return random.Random(f"{seed}:{stratum}").sample(sorted(pool), count)


def leaflet_strata(pages: list[dict], position_rows: list[dict]) -> dict[str, list[str]]:
    """The nineteen posts, split by whether the instrument got anything off them."""
    yielded = {f"{row['channel']}:{row['parent_msg_id']}" for row in position_rows}
    posts = {f"{page['channel']}:{page['parent_msg_id']}" for page in pages}
    return {
        "yielded positions": sorted(posts & yielded),
        "yielded none": sorted(posts - yielded),
    }


def top_channels(aggregates: dict, count: int = COMMENT_CHANNELS) -> list[str]:
    """The `count` channels with the most comments in the window — by the aggregates, not by a list.

    Ties broken by handle so the stratum is a function of the record and not of dict order.
    """
    rows = aggregates["comment"]["per_channel"]
    ranked = sorted(rows, key=lambda handle: (-rows[handle]["rows"], handle))
    return ranked[:count]


# --- one shown row ---------------------------------------------------------------------------


def page_block(page: dict, root: Path) -> dict:
    """One page as it was SENT: the picture, its sha PROVEN against the file, and what came back."""
    path = root / page["image_path"]
    if not path.exists():
        raise SystemExit(
            f"{page['image_path']}: not found — 3.18 (6) shows the operator «the page image as it"
            " was sent», and a pack that cannot open it has nothing to show"
        )
    found = summary.sha256_of(path)
    if found != page["image_sha256"]:
        raise SystemExit(
            f"{page['image_path']} hashes to {found[:16]}… and the evidence row records"
            f" {page['image_sha256'][:16]}… — the picture on disk is not the one the model was"
            " sent. Stop rather than show the operator a different image beside the same verdict."
        )
    return {
        "msg_id": page["msg_id"],
        "image_path": page["image_path"],
        "image_sha256": page["image_sha256"],
        "n_positions": page["n_positions"],
        "unreadable": page["unreadable"],
        "reply": page["reply"]["content"],
    }


def why_a_position(row: dict) -> dict:
    """Field by field, what made this a POSITION and not a product_mention — 3.18 (6) verbatim.

    The five presence booleans, the VALUES behind them, and the rung re-derived from those booleans
    by the ladder's own function. `ladder_table` travels with the pack so the rung can be re-derived
    AT THE TABLE rather than trusted: 32 rows, and the operator can find this row's combination in
    it.
    """
    one = row["position"]
    return {
        "presence": row["presence"],
        "values": {
            "brand": one["brand_raw"],
            "brand_id": one["brand_id"],
            "line": one["line"],
            "category": one["category"],
            "size": _size(one),
            "attribute_pct": one["attribute_pct"],
        },
        "tier": row["tier"],
        "tier_re_derived": positions.tier_from_presence(**row["presence"]),
        "ladder_key": "+".join(name for name, on in row["presence"].items() if on) or "none",
    }


def _size(one: dict) -> str | None:
    if one["size_value"] is None:
        return None
    pack = f"{one['pack_count']}×" if one["pack_count"] else ""
    return f"{pack}{one['size_value']:g} {one['size_unit']}"


def position_block(row: dict) -> dict:
    """One extracted SKU: why it is a position, what it costs, and the two depth readings."""
    one = row["position"]
    return {
        "row_id": row["row_id"],
        "page_msg_id": row["msg_id"],
        "ordinal": row["ordinal"],
        "why_a_position": why_a_position(row),
        # the two laws that govern these fields are stated ONCE, at `laws` in the record: a
        # sentence repeated under all 48 positions is 90 KB of boilerplate an operator scrolls past.
        "price": {
            "price_promo": one["price_promo"],
            "price_old": one["price_old"],
            "discount_pct_printed": one["discount_pct_printed"],
            "discount_footnote": one["discount_footnote"],
            "price_qualifier": one["price_qualifier"],
            "price_origin": one["price_origin"],
        },
        "depth": {
            "from_printed_badge": (
                None
                if one["discount_pct_printed"] is None
                else round(one["discount_pct_printed"] / 100, 4)
            ),
            "from_price_pair": None if one["depth"] is None else round(one["depth"], 4),
            "printed_disagrees_with_computed": one["depth_disagrees_with_printed"],
        },
        "warnings": row["warnings"],
    }


def leaflet_block(post: str, stratum: str, pages: list[dict], rows: list[dict], root: Path) -> dict:
    """One leaflet POST: its pages and every position extracted from them, in msg_id order."""
    channel, _, parent = post.rpartition(":")
    return {
        "post": post,
        "channel": channel,
        "parent_msg_id": int(parent),
        "stratum": stratum,
        "task": loop.PAGE_TASK,
        "prompt_sha256": prompts.prompt_sha256(loop.PAGE_TASK),
        "pages": [page_block(page, root) for page in sorted(pages, key=lambda p: p["msg_id"])],
        "positions": [
            position_block(row) for row in sorted(rows, key=lambda r: (r["msg_id"], r["ordinal"]))
        ],
    }


def comment_block(row: dict, aggregates: dict, aliases: dict[str, str]) -> dict:
    """One comment: what was written, what was SENT, every head's verdict, and its aggregate."""
    post, text = summary.sent_parts(row)
    verdicts = summary.comment_verdicts([row], aliases)[0]
    labels = verdicts["labels"]
    return {
        "comment": f"{row['channel']}:{row['msg_id']}",
        "channel": row["channel"],
        "msg_id": row["msg_id"],
        "parent_msg_id": row["parent_msg_id"],
        "task": row["task"],
        "prompt_sha256": row["prompt_sha256"],
        "post_state": row["post_state"],
        "text": text,
        "parent_post": post,
        "rendering": row["rendering"],
        "reply": row["reply"]["content"],
        "verdicts": {
            "sentiment": labels and labels["sentiment"],
            "sarcasm": labels and labels["sarcasm"],
            "intents": labels and labels["intents"],
            "unreadable": verdicts["unreadable"],
            "brand_attribution": {"matched": verdicts["brands"], "law": "laws.brand_attribution"},
        },
        "language": verdicts["language"],
        # 1 361 of the 5 075 reached the model this way; the caption below carries the count so a
        # shown empty row is read as its class rather than as an accident of the draw.
        "empty_text": verdicts["empty_text"],
        "aggregate": comment_caption(row["channel"], labels, aggregates),
    }


def comment_caption(channel: str, labels, aggregates: dict) -> dict:
    """The aggregate this row belongs to, READ from `window_summary_5c2.json` and never recomputed.

    3.18 (6): "with the aggregate the row belongs to printed beside it, so a single row is never
    read as the population". Both denominators travel — the channel's and the window's — because a
    row of a 2 717-row channel and a row of a 4-row one are not the same evidence.
    """
    here, whole = aggregates["comment"]["per_channel"][channel], aggregates["comment"]["total"]
    return {
        "source": rel(SUMMARY),
        "channel": channel,
        "rows": {"in_channel": here["rows"], "in_window": whole["rows"]},
        "sentiment": {"in_channel": here["sentiment"], "in_window": whole["sentiment"]},
        "sarcasm": {
            "rate_in_channel": here["sarcasm"]["rate"],
            "rate_in_window": whole["sarcasm"]["rate"],
        },
        "intents": {
            "frequency_in_channel": here["intents"]["frequency"],
            "no_intent_in_channel": here["intents"]["rows_with_no_intent"],
            "frequency_in_window": whole["intents"]["frequency"],
            "no_intent_in_window": whole["intents"]["rows_with_no_intent"],
        },
        "brand_attribution": {
            "rows_with_a_brand_in_channel": here["brand_attribution"]["rows_with_a_brand"],
            "rows_with_a_brand_in_window": whole["brand_attribution"]["rows_with_a_brand"],
        },
        "language": {
            "in_channel": here["language"]["rows"],
            "in_window": whole["language"]["rows"],
        },
        "empty_text": {
            "in_channel": here["empty_text"]["rows"],
            "in_window": whole["empty_text"]["rows"],
        },
        "this_row": {
            "sentiment": labels and labels["sentiment"],
            "sarcasm": labels and labels["sarcasm"],
            "intents": labels and labels["intents"],
        },
    }


def leaflet_caption(aggregates: dict) -> dict:
    """The aggregate a shown leaflet row belongs to — the page markers and the leaflet carrier."""
    return {
        "source": rel(SUMMARY),
        "pages": aggregates["leaflet_page"]["total"],
        "positions": aggregates["position_row"]["by_carrier"][loop.CARRIER],
    }


# --- the record ------------------------------------------------------------------------------


def build(
    derived: Path, summary_path: Path, prereg_path: Path, registry_path: Path, root: Path
) -> dict:
    aggregates = read_json(summary_path)
    # the watchlist, reached only THROUGH the seal's own pin — `window_summary_5c2` owns the check,
    # and the pack has to run the same matcher on the shown row that the aggregate was built with.
    registry = summary.registry_through_the_seal(read_json(prereg_path), registry_path)
    aliases = summary.brands.watchlist_aliases(registry.watchlist)
    sources = {rel(summary_path): summary.sha256_of(summary_path)}

    def named(record_type: str, handle: str) -> list[dict]:
        path = derived / f"{record_type}s" / f"{handle.lstrip('@')}.jsonl"
        sources[rel(path)] = summary.sha256_of(path) if path.exists() else None
        rows = summary.read_rows(path)
        sources[rel(path)] = summary.sha256_of(path)
        return rows

    leaflet_channel = next(iter(aggregates["leaflet_page"]["per_channel"]))
    pages = named(loop.PAGE_RECORD_TYPE, leaflet_channel)
    position_rows = named(loop.POSITION_RECORD_TYPE, leaflet_channel)
    strata = leaflet_strata(pages, position_rows)
    drawn_posts = [
        (post, "yielded positions")
        for post in draw(strata["yielded positions"], LEAFLET_YIELDED, "yielded positions")
    ] + [
        (post, "yielded none")
        for post in draw(strata["yielded none"], LEAFLET_EMPTY, "yielded none")
    ]

    pages_of, rows_of = defaultdict(list), defaultdict(list)
    for page in pages:
        pages_of[f"{page['channel']}:{page['parent_msg_id']}"].append(page)
    for row in position_rows:
        rows_of[f"{row['channel']}:{row['parent_msg_id']}"].append(row)

    channels = top_channels(aggregates)
    drawn_comments, comments = [], []
    for handle in channels:
        rows = named(loop.RECORD_TYPE, handle)
        by_id = {row["msg_id"]: row for row in rows}
        (msg_id,) = draw(list(by_id), 1, handle)
        drawn_comments.append(f"{handle}:{msg_id}")
        comments.append(comment_block(by_id[msg_id], aggregates, aliases))

    assert_same_evidence(aggregates, sources, summary_path)
    leaflets = [
        leaflet_block(post, stratum, pages_of[post], rows_of[post], root)
        for post, stratum in sorted(drawn_posts)
    ]
    return {
        "phase": "5c2-validate",
        "contract": (
            "SPEC 3.18 (6) — the operator sitting the phase does not close without. At least five"
            " leaflet posts and five comments, original beside verdict, drawn under a recorded seed"
            " from the window's own output."
        ),
        "aggregates": {"record": rel(summary_path), "sha256": sources[rel(summary_path)]},
        "laws": {
            "findings": FINDINGS_LAW,
            "depth": summary.DEPTH_LAW,
            "price_old": PRICE_OLD_FLAG,
            "brand_attribution": summary.BRAND_INSTRUMENT,
        },
        "seed": SEED,
        "seed_derivation": (
            "random.Random(f'{seed}:{stratum}').sample(sorted(pool), n), the stratum being"
            " «yielded positions» / «yielded none» for the leaflet legs and the channel handle for"
            " each comment. The stratum is in the seed because ONE Random(42) asked for one element"
            " out of pools of 242, 223 and 222 answers the same index for all three — the first"
            " build of this pack drew rank 163 of each. Reproducible from these two fields alone."
        ),
        "strata": {
            "leaflet_post": {
                "rule": (
                    "the nineteen posts split by whether any page of them yielded a position;"
                    f" {LEAFLET_YIELDED} drawn from the first and {LEAFLET_EMPTY} from the second."
                    " A post that yielded nothing cannot answer «field by field, what made each a"
                    " POSITION», and eleven of nineteen yielded — a blind draw of five could show"
                    " one. The stratum keys on whether the instrument PRODUCED output, which is"
                    " something the model did; it never keys on whether that output looks correct,"
                    " and no row in either stratum was chosen for what its verdict says."
                ),
                "populations": {name: len(pool) for name, pool in strata.items()},
                "drawn": {
                    name: count
                    for name, count in (
                        ("yielded positions", LEAFLET_YIELDED),
                        ("yielded none", LEAFLET_EMPTY),
                    )
                },
            },
            "comment": {
                "rule": (
                    f"one row from each of the {COMMENT_CHANNELS} channels with the most comments"
                    " in the window, seeded within each. Two channels are 73.8% of the window, so"
                    " an unstratified draw of five is a draw about @matusi_ukr."
                ),
                "channels": channels,
                "populations": {
                    handle: aggregates["comment"]["per_channel"][handle]["rows"]
                    for handle in channels
                },
            },
        },
        "drawn": {
            "leaflet_posts": sorted(post for post, _ in drawn_posts),
            "comments": drawn_comments,
        },
        "ladder": {
            "table": positions.ladder_table(),
            "sha256": positions.ladder_sha256(),
            "reading": (
                "the rung is a function of PRESENCE only. Every row below carries its five booleans"
                " and its `ladder_key`, so the tier can be re-derived at the table from this table."
            ),
        },
        "leaflet_posts": leaflets,
        "leaflet_aggregate": leaflet_caption(aggregates),
        "comments": comments,
        "findings": findings_skeleton(leaflets, comments),
        "sources": dict(sorted(sources.items())),
        "producer": {
            "script": rel(Path(__file__)),
            "sha256": summary.sha256_of(Path(__file__).resolve()),
            "borrowed": {
                name: summary.sha256_of(REPO_ROOT / name)
                for name in (*summary.BORROWED, "scripts/window_summary_5c2.py")
            },
        },
    }


def findings_skeleton(leaflets: list[dict], comments: list[dict]) -> dict:
    """One EMPTY slot per shown row, keyed by the id the evidence already uses.

    Three levels because the operator's reactions have three shapes: a post ("page 6 has a syrok
    nobody extracted"), a position ("that line is the flavour, not the line") and a comment ("this
    is sarcasm"). A skeleton that only had the eleven top-level slots would push every position
    dispute into free text, and free text does not become an ORDER without someone re-reading it.
    """
    return {
        "verdicts": ["ratified", "disputed"],
        "leaflet_posts": {block["post"]: _slot() for block in leaflets},
        "positions": {row["row_id"]: _slot() for block in leaflets for row in block["positions"]},
        "comments": {block["comment"]: _slot() for block in comments},
    }


def _slot() -> dict:
    return {"verdict": "", "note": ""}


def assert_same_evidence(aggregates: dict, sources: dict, summary_path: Path) -> None:
    """The captions and the rows must be about the same bytes, or neither is evidence.

    `window_summary_5c2.json` records the sha256 of every derived file it read. Every file THIS
    pack reads is in that set and must hash the same; a mismatch means the aggregates describe a
    different disk than the row they would be printed beside.
    """
    pinned = aggregates["sources"]
    wrong = {
        name: (digest, pinned.get(name, "<absent>"))
        for name, digest in sources.items()
        if name != rel(summary_path) and pinned.get(name, "<absent>") != digest
    }
    if wrong:
        lines = "; ".join(
            f"{n}: {a[:12]}… against {b[:12]}…" for n, (a, b) in sorted(wrong.items())
        )
        raise SystemExit(
            f"{rel(summary_path)} was computed over different bytes than this pack reads — {lines}."
            " Re-run scripts/window_summary_5c2.py; a caption measured on another disk is worse"
            " than no caption."
        )


# --- the rendering ---------------------------------------------------------------------------


# Every label this module writes is RUSSIAN. The contract's header makes the rendering the one
# artifact exempt from the English rule and names the language — «which is in Russian» — and the
# exemption STATUS.md carries is scoped to Russian by name, not to "whatever the reader speaks".
# The rows themselves are Ukrainian and Russian and travel through `esc` untouched; a label in a
# third language is this module's own voice, not the corpus's. Checked by
# `tests/test_build_validate_pack.py::test_the_rendering_speaks_russian_in_its_own_voice`.
def esc(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def yes_no(value) -> str:
    return {True: "да", False: "нет", None: "—"}.get(value, esc(value))


def render(record: dict) -> str:
    """The operator-facing rendering. Russian, because the operator reads it — the STATUS.md rule."""
    parts = [_head(record)]
    parts.append("<h2>Комментарии — 5 строк, по одной из пяти самых крупных каналов</h2>")
    parts += [_comment(block) for block in record["comments"]]
    parts.append("<h2>Листовки — 6 постов: страницы как отправлены, и что с них снято</h2>")
    parts.append(_leaflet_aggregate(record["leaflet_aggregate"]))
    parts += [_leaflet(block) for block in record["leaflet_posts"]]
    parts.append(_ladder(record["ladder"]))
    return "\n".join(parts) + "\n"


def _head(record: dict) -> str:
    drawn = record["drawn"]
    return f"""<meta charset="utf-8">
<title>5c2-validate — пакет сидения</title>
<style>
 body {{ font: 15px/1.5 -apple-system, system-ui, sans-serif; max-width: 1100px; margin: 2rem auto;
        padding: 0 1rem; color: #16191d; }}
 h1 {{ font-size: 1.6rem }} h2 {{ margin-top: 2.5rem; border-top: 2px solid #16191d; padding-top: .6rem }}
 h3 {{ margin-bottom: .3rem }}
 .law {{ background: #fff6d6; border-left: 4px solid #d8a800; padding: .8rem 1rem; margin: 1rem 0 }}
 .row {{ border: 1px solid #d5d9de; border-radius: 6px; padding: 1rem; margin: 1.2rem 0 }}
 .sent {{ background: #f4f6f8; padding: .6rem .8rem; border-radius: 4px; white-space: pre-wrap;
          font-family: ui-monospace, Menlo, monospace; font-size: 13px }}
 table {{ border-collapse: collapse; margin: .6rem 0; font-size: 14px }}
 td, th {{ border: 1px solid #d5d9de; padding: .25rem .5rem; text-align: left; vertical-align: top }}
 th {{ background: #f4f6f8 }}
 .page {{ display: flex; gap: 1rem; align-items: flex-start; margin: .8rem 0;
          border-top: 1px dashed #d5d9de; padding-top: .8rem }}
 .page img {{ width: 300px; border: 1px solid #d5d9de }}
 .empty {{ color: #6b7480 }}
 .flag {{ color: #8a4b00; font-size: 13px }}
 code {{ background: #f4f6f8; padding: 0 .2rem }}
 details {{ margin: .4rem 0 }}
</style>
<h1>5c2-validate — пакет сидения</h1>
<div class="law"><b>{esc(FINDINGS_LAW_RU)}</b><br>
Слоты вердиктов пусты и заполняются ВО ВРЕМЯ сидения — в
<code>{esc(rel(OUT))}</code>, блок <code>findings</code>.</div>
<p>Строки <b>вытянуты по записанному seed {record["seed"]}</b>, не выбраны руками. Страты и
вытянутые id — в записи. Каждая строка подписана агрегатом, к которому принадлежит
(<code>{esc(record["aggregates"]["record"])}</code>): одна строка никогда не читается как
популяция.</p>
<p class="empty">Вытянуто: {esc(", ".join(drawn["comments"]))} · {esc(", ".join(drawn["leaflet_posts"]))}</p>
<p class="empty">Картинки лежат вне git (<code>data/</code>), пути относительные — открывай этот
файл из <code>results/</code> внутри чекаута.</p>"""


def _comment(block: dict) -> str:
    caption, verdicts = block["aggregate"], block["verdicts"]
    intents = ", ".join(verdicts["intents"] or []) or "— (ни одной из шести)"
    shown = (
        f'<div class="sent">{esc(block["text"])}</div>'
        if not block["empty_text"]
        else f"""<div class="sent flag">(ПУСТО — у комментария нет текста: стикер, фото или
голосовое. Модели ушёл пустой блок &lt;comment&gt;&lt;/comment&gt;, и все три головы ответили
про ничто. Таких строк в окне {caption["empty_text"]["in_window"]} из
{caption["rows"]["in_window"]}, в этом канале — {caption["empty_text"]["in_channel"]} из
{caption["rows"]["in_channel"]}.)</div>"""
    )
    return f"""<div class="row">
<h3>{esc(block["comment"])} <span class="empty">· язык {esc(block["language"])} · пост
{esc(block["parent_msg_id"])} ({esc(block["post_state"])})</span></h3>
<b>Комментарий, как написан:</b>
{shown}
<b>Родительский пост, как его получила модель:</b>
<div class="sent">{esc(block["parent_post"])}</div>
<details><summary>Точный рендеринг запроса ({esc(block["task"])},
sha {esc(block["prompt_sha256"][:16])}…) и сырой ответ</summary>
<div class="sent">{esc(block["rendering"][0]["content"])}</div>
<div class="sent">{esc(block["reply"])}</div></details>
<table>
<tr><th>голова</th><th>вердикт строки</th><th>агрегат канала {esc(caption["channel"])}
({caption["rows"]["in_channel"]} строк)</th><th>агрегат окна ({caption["rows"]["in_window"]})</th></tr>
<tr><td>sentiment</td><td><b>{esc(verdicts["sentiment"])}</b></td>
<td>{esc(json.dumps(caption["sentiment"]["in_channel"], ensure_ascii=False))}</td>
<td>{esc(json.dumps(caption["sentiment"]["in_window"], ensure_ascii=False))}</td></tr>
<tr><td>sarcasm</td><td><b>{yes_no(verdicts["sarcasm"])}</b></td>
<td>доля {esc(caption["sarcasm"]["rate_in_channel"])}</td>
<td>доля {esc(caption["sarcasm"]["rate_in_window"])}</td></tr>
<tr><td>intents</td><td><b>{esc(intents)}</b></td>
<td>{esc(json.dumps(caption["intents"]["frequency_in_channel"], ensure_ascii=False))}
· без интенции {caption["intents"]["no_intent_in_channel"]}</td>
<td>{esc(json.dumps(caption["intents"]["frequency_in_window"], ensure_ascii=False))}
· без интенции {caption["intents"]["no_intent_in_window"]}</td></tr>
<tr><td>brand attribution</td>
<td><b>{esc(", ".join(verdicts["brand_attribution"]["matched"]) or "—")}</b></td>
<td>срабатывает на {caption["brand_attribution"]["rows_with_a_brand_in_channel"]} строках
из {caption["rows"]["in_channel"]}</td>
<td>{caption["brand_attribution"]["rows_with_a_brand_in_window"]} из
{caption["rows"]["in_window"]}<br><span class="flag">Модельной головы НЕТ: T1v2_with_post отдаёт
три метки. Это детерминированный матчер watchlist по отправленному тексту.</span></td></tr>
</table>
<p class="empty">Слот вердикта: <code>findings.comments["{esc(block["comment"])}"]</code></p>
</div>"""


def _leaflet_aggregate(caption: dict) -> str:
    return f"""<div class="law">Агрегат, к которому принадлежит каждая строка ниже
(<code>{esc(caption["source"])}</code>): страниц {caption["pages"]["rows"]}, из них с позициями
{caption["pages"]["with_positions"]}, пустых {caption["pages"]["empty"]}, нечитаемых
{caption["pages"]["unreadable"]["rows"]}; позиций с листовок {caption["positions"]["rows"]}, тиры
{esc(json.dumps(caption["positions"]["tier"], ensure_ascii=False))}. Глубина по печатному бейджу:
{esc(json.dumps(caption["positions"]["depth"]["from_printed_badge"], ensure_ascii=False))}.
<br><br><span class="flag">{esc(PRICE_OLD_FLAG)}</span></div>"""


def _leaflet(block: dict) -> str:
    by_page: dict[int, list[dict]] = defaultdict(list)
    for row in block["positions"]:
        by_page[row["page_msg_id"]].append(row)
    pages = "\n".join(_page(page, by_page[page["msg_id"]]) for page in block["pages"])
    return f"""<div class="row">
<h3>{esc(block["post"])} <span class="empty">· страта «{esc(block["stratum"])}» ·
{len(block["pages"])} страниц · {len(block["positions"])} позиций ·
{esc(block["task"])} sha {esc(block["prompt_sha256"][:16])}…</span></h3>
{pages}
<p class="empty">Слот вердикта поста: <code>findings.leaflet_posts["{esc(block["post"])}"]</code></p>
</div>"""


def _page(page: dict, rows: list[dict]) -> str:
    if page["unreadable"]:
        verdict = f'<p class="flag">НЕЧИТАЕМО: {esc(page["unreadable"])}</p>'
    elif not rows:
        verdict = (
            '<p class="empty">0 позиций — страница прочитана и ничего из категории не несёт.</p>'
        )
    else:
        verdict = "\n".join(_position(row) for row in rows)
    return f"""<div class="page">
<a href="{esc(IMAGE_PREFIX + page["image_path"])}"><img loading="lazy"
 src="{esc(IMAGE_PREFIX + page["image_path"])}" alt="{esc(page["msg_id"])}"></a>
<div><b>msg_id {page["msg_id"]}</b>
<span class="empty">· sha {esc(page["image_sha256"][:16])}… (сверена с байтами на диске)</span>
{verdict}
<details><summary>Сырой ответ модели</summary><div class="sent">{esc(page["reply"])}</div></details>
</div></div>"""


def _position(row: dict) -> str:
    why, price, depth = row["why_a_position"], row["price"], row["depth"]
    present = ", ".join(name for name, on in why["presence"].items() if on)
    values = why["values"]
    return f"""<table>
<tr><th colspan="2">{esc(row["row_id"])} — тир <b>{esc(why["tier"])}</b>
(перевыведен из присутствия: {esc(why["tier_re_derived"])}, ключ лестницы
<code>{esc(why["ladder_key"])}</code>)</th></tr>
<tr><td>что сделало это ПОЗИЦИЕЙ</td><td>присутствуют: <b>{esc(present)}</b><br>
бренд <b>{esc(values["brand"])}</b> (id {esc(values["brand_id"] or "—")}) · линия
{esc(values["line"] or "—")} · категория <b>{esc(values["category"] or "—")}</b> · размер
{esc(values["size"] or "—")} · жирность {esc(values["attribute_pct"] or "—")}</td></tr>
<tr><td>цена</td><td>промо <b>{esc(price["price_promo"])}</b> · печатный бейдж
{esc(price["discount_pct_printed"])}% · сноска {yes_no(price["discount_footnote"])} ·
квалификатор {esc(price["price_qualifier"] or "—")} · происхождение
{esc(price["price_origin"])}<br><span class="flag">старая цена (вход глубины, ПОМЕЧЕН):
{esc(price["price_old"])}</span></td></tr>
<tr><td>глубина</td><td>по бейджу <b>{esc(depth["from_printed_badge"])}</b> · по паре цен
{esc(depth["from_price_pair"])} · расходятся: {yes_no(depth["printed_disagrees_with_computed"])}</td></tr>
<tr><td>предупреждения</td><td>{esc(", ".join(row["warnings"]) or "—")}
<br><span class="empty">слот вердикта: <code>findings.positions["{esc(row["row_id"])}"]</code></span>
</td></tr>
</table>"""


def _ladder(ladder: dict) -> str:
    rows = "\n".join(
        f"<tr><td><code>{esc(key)}</code></td><td>{esc(rung)}</td></tr>"
        for key, rung in ladder["table"].items()
    )
    return f"""<h2>Лестница тиров — 32 комбинации, sha {esc(ladder["sha256"][:16])}…</h2>
<p>{esc(ladder["reading"])}</p>
<details><summary>Открыть таблицу</summary><table>
<tr><th>присутствуют</th><th>тир</th></tr>
{rows}
</table></details>"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--derived-root", type=Path, default=summary.DERIVED)
    parser.add_argument("--summary", type=Path, default=SUMMARY)
    parser.add_argument("--prereg", type=Path, default=summary.PREREG)
    parser.add_argument("--registry", type=Path, default=summary.REGISTRY)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--page", type=Path, default=PAGE)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    record = build(args.derived_root, args.summary, args.prereg, args.registry, args.root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.page.write_text(render(record), encoding="utf-8")

    print(f"wrote {rel(args.out)}  sha256 {summary.sha256_of(args.out)[:16]}…")
    print(f"wrote {rel(args.page)} sha256 {summary.sha256_of(args.page)[:16]}…")
    print(f"  seed {record['seed']} · {len(record['leaflet_posts'])} leaflet posts, ", end="")
    print(f"{sum(len(b['pages']) for b in record['leaflet_posts'])} pages, ", end="")
    print(f"{sum(len(b['positions']) for b in record['leaflet_posts'])} positions")
    print(f"  {len(record['comments'])} comments from {record['strata']['comment']['channels']}")
    print(
        f"  findings: {len(record['findings']['leaflet_posts'])} post slots,"
        f" {len(record['findings']['positions'])} position slots,"
        f" {len(record['findings']['comments'])} comment slots — all empty"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
