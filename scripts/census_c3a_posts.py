#!/usr/bin/env python3
"""How many of the window's posts the relevance pre-filter passes, and what that leg costs. ($0.)

SPEC amendment 3.18 (7)(e): the post leg enters 5c2-run FILTERED, never raw — through "the
lexicon-over-post-text instrument of `scripts/sku_prefilter_census.py` (the frame skub2's text pack
drew from, the matched line kept as evidence), never the channel entry gate of 3.12, which gates
CHANNELS; its population is counted by a zero-cost census of the pre-filter over THIS window BEFORE
the pre-registration, and the leg is priced on that count at the paid text marginal". This is that
census. The projection's 9 158-post raw bound "enters no cap and no session", and what replaces it
is the number below.

**Nothing here is a second implementation.** The window is `census_5c2.window_of`, the screening is
`sku_prefilter_census.screen_rows`, the controls are its `run_controls`, and the price is
`write_sku_projection_b2.text_marginal` — the same four instruments their own records were built
with. What this file adds is the intersection: that frame, over this window, per channel.

**The selection is PINNED, not re-decided.** `results/census_5c2.json` carries a per-channel
`posts.ids_sha256` over the in-window post ids, and the ruling of 3.18 (7)(a) ratified that anchor.
Every channel's ids are re-hashed here and compared to that pin, so "the same window" is a check and
not a shared constant.

Record hygiene is the prep-c2 pair's: no clock, no `git` block, a `producer.sha256` instead — the
re-run under the same anchor must be byte-identical, and a provenance field that moves with the
working tree voids that on the first unrelated commit.

    PYTHONPATH=src python3 scripts/census_c3a_posts.py --anchor 2026-08-09T00:00:00+00:00
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import census_5c2 as c2  # noqa: E402
import projection_5c2 as projection  # noqa: E402
import sku_prefilter_census as frame  # noqa: E402
import write_sku_projection_b2 as b2  # noqa: E402
import yield_screen_5c1 as screen  # noqa: E402

from market_pulse import yield_screen  # noqa: E402
from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.lexicon import load_lexicon  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

POSTS = REPO_ROOT / "data" / "raw" / "posts"
LEXICON = REPO_ROOT / "config" / "lexicon.yaml"
CENSUS_5C2 = REPO_ROOT / "results" / "census_5c2.json"
POST_MEDIA = REPO_ROOT / "results" / "post_media_5c1.json"
SKUB2 = REPO_ROOT / "results" / "sku_b_positions_skub2.json"
SKUB2_REPORT = REPO_ROOT / "docs" / "reports" / "skub2-run.md"
SPEC = REPO_ROOT / "docs" / "SPEC.md"
RECORD = REPO_ROOT / "results" / "census_c3a_posts.json"

rel = c2.rel
sha256_of = c2.sha256_of
cite = projection.cite
quote_line = projection.quote_line
cost = projection.cost
"""Five borrowed outright. `cite` is what makes a number in this record executable — the dotted path
it prints is walked by `tests/test_census_c3a_posts.py` with a second resolver — and `cost` carries
the same 3% contract drift every projection in this repo has carried since sku-b."""


def producer() -> dict:
    """Which code wrote this, by its own sha — `census_5c2.producer`'s reason, verbatim.

    A `git` block holds `git status --porcelain`, so the artifact's bytes move when an unrelated
    file is committed. Byte-identity under one anchor is this record's gate; that block voids it.

    ``borrows`` is this record's own addition and it closes a hole the other two do not have. This
    census is deliberately built out of four other modules — the window, the screening, the controls
    and the price — and it copies one of their docstrings INTO the record (``rule``). So a change in
    any of them moves these bytes while `sha256` above sits still, and a pre-registration pinning
    this file by sha would be pinning half of what produced it.
    """
    return {
        "script": rel(Path(__file__)),
        "sha256": sha256_of(Path(__file__)),
        "why": "no git block: `git status --porcelain` is a fact about the tree, not the measurement",
        "borrows": {
            rel(Path(module.__file__)): sha256_of(Path(module.__file__))
            for module in (c2, frame, projection, b2)
        },
    }


def instruments(registry) -> tuple[dict, list]:
    """The pre-filter's two compiled halves, from the vocabulary LAW of SPEC 3.17 (8).

    `run_loop.prefilter_instruments` builds the same pair for the pass, off the same two files.
    They are not imported from each other on purpose: this one is a $0 census and that one is on
    the path of a paid session, and a shared helper would put this file in that call stack.
    """
    lexicon = load_lexicon(LEXICON, taxonomy=registry.taxonomy)
    return (
        yield_screen.compile_categories(lexicon),
        yield_screen.compile_aliases(watchlist_aliases(registry.watchlist)),
    )


def ids_sha256(msg_ids: list[int]) -> str:
    """`census_5c2.leg`'s hash, so the two records' pins are comparable at all."""
    return hashlib.sha256(",".join(str(msg_id) for msg_id in msg_ids).encode("utf-8")).hexdigest()


def pinned_by_the_ratified_census() -> dict:
    """``{handle: the ids_sha256 census_5c2 recorded for that channel's in-window posts}``."""
    record = json.loads(CENSUS_5C2.read_text(encoding="utf-8"))
    return {
        row["handle"]: row["posts"]["ids_sha256"]
        for row in record["channels"]
        if row["posts"] != c2.CANNOT_ANSWER
    }


def channel_row(
    handle: str, source, window: dict, compiled: dict, aliases: list, pins: dict
) -> dict:
    """One channel's window, screened. The cell is `sku_prefilter_census.screen_rows`' own shape."""
    path = POSTS / f"{handle.lstrip('@')}.jsonl"
    if not path.exists():
        return {
            "handle": handle,
            "posts_in_window": c2.CANNOT_ANSWER,
            "why": "no file in data/raw/posts/ — the channel has never been walked",
        }
    inside = list(screen.in_window(screen.load_jsonl(path), window))
    cell = frame.screen_rows(handle, inside, compiled, aliases)
    ids = sorted({row["msg_id"] for row in inside})
    return {
        "handle": handle,
        "source_id": source.id,
        "audience": source.audience,
        "source_type": source.source_type,
        "posts_in_window": len(inside),
        "ids_sha256": ids_sha256(ids),
        # the check, per channel: this window is the ratified one or this row says so
        "matches_census_5c2": pins.get(handle) == ids_sha256(ids),
        **{key: value for key, value in cell.items() if key != "_passed"},
        "_passed": cell["_passed"],
    }


def leaflet_corpus() -> dict:
    """The leaflet leg's population under 3.18 (7)(d): the corpus ON DISK, not window-intersected.

    Computed from the manifest and QUOTED from the clause in the same block, because the contract
    calls that file "the citable source for 3.18 (7)(d) in the prereg" — so the file is the
    authority and the ruling's sentence is the thing that has to still agree with it.
    """
    manifest = json.loads(POST_MEDIA.read_text(encoding="utf-8"))
    entries = list(manifest["entries"].values())
    dates = sorted(entry["date"] for entry in entries)
    return {
        "asks": "the whole leaflet corpus on disk — 3.18 (7)(d), NOT intersected with the window",
        "manifest": {"path": rel(POST_MEDIA), "sha256": sha256_of(POST_MEDIA)},
        "pages": sum(len(entry["images"]) for entry in entries),
        "posts": len(entries),
        "channels": sorted({entry["channel"] for entry in entries}),
        "span": {"first": dates[0], "last": dates[-1]} if dates else c2.CANNOT_ANSWER,
        "ruling": quote_line(
            SPEC,
            "159 pages under 19 posts",
            "SPEC 3.18 (7)(d) states the population; the numbers beside it are re-counted from the"
            " manifest here, so the clause and the file agree or this record shows they do not",
        ),
        "why_not_window_intersected": (
            "«leaflets follow their own weekly cadence, and the window clause of (4) binds the"
            " comment and post legs only» — 3.18 (7)(d). The window holds 78 of these 159 pages"
            " (results/census_5c2.json :: totals.leaflet_pages_in_window) and the leg buys all 159"
        ),
    }


def priced(passed: int, rate: float) -> dict:
    """The post leg at skub2's paid text marginal — the rate 3.18 (7)(e) names, on this count."""
    marginal = b2.text_marginal(json.loads(SKUB2.read_text(encoding="utf-8")))
    seconds = passed * marginal + projection.driver.IDLE_TAIL_SECONDS
    return {
        "rows": passed,
        "seconds_per_row": marginal,
        # DERIVED and not a field, so deliberately not in the `value` + `source` citation shape:
        # that shape promises the number can be dug out of the file it names, and this one cannot.
        "derivation": {
            "source": f"{rel(SKUB2)} :: derived, no single field holds it",
            "how": (
                "write_sku_projection_b2.text_marginal, the house derivation reused rather than"
                " rewritten: (timing.worker_seconds - projection.opened_seconds"
                " - pages x page_marginal) / population.text_rows"
            ),
            "why": "skub2's own text leg — 30 rows, on the serverless runtime, PAID",
        },
        "report_line": quote_line(
            SKUB2_REPORT,
            "84.398",
            "the same leg in that session's report. It reads 2.8133 against the 2.8132 derived"
            " here — a fourth-decimal rounding difference, not two measurements",
        ),
        **cost(seconds, rate),
        "fixed_seconds": {
            "idle_tail": projection.driver.IDLE_TAIL_SECONDS,
            "boot": (
                "NOT added: 3.18 (7)(c) buys the two-leg window in ONE session, and this leg rides"
                " the endpoint the leaflet leg already booted. A boot here would be double-counted"
                " against results/projection_5c2.json, which already pays one"
            ),
        },
    }


def concentration(rows: list[dict]) -> list[dict]:
    """Whose population this is, by enumeration — `census_5c2.concentration`'s shape and reason."""
    return c2.concentration(
        [row for row in rows if row["posts_in_window"] != c2.CANNOT_ANSWER],
        lambda row: row["passed"],
    )


def refuse_to_move_the_anchor(out: Path, window: dict) -> None:
    """`census_5c2.refuse_to_move_the_anchor`, on this record's own anchor field.

    A re-run under the SAME anchor is the determinism gate and is allowed; a different window under
    the name the ruling cites is what gets stopped.
    """
    if not out.exists():
        return
    was = json.loads(out.read_text(encoding="utf-8"))["anchor"]["anchor"]
    if was != window["anchor"]:
        raise SystemExit(
            f"{rel(out)} was written with anchor {was} and this run's is {window['anchor']}."
            " A different window is a different population: give it --out with another path."
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--anchor",
        required=True,
        help="the ONE timestamp the window ends at, ISO 8601 — ratified by SPEC 3.18 (7)(a) as"
        " 2026-08-09T00:00:00+00:00. Required on purpose: a default read from the clock would make"
        " two runs of the same census two different artifacts",
    )
    parser.add_argument("--out", type=Path, default=RECORD)
    args = parser.parse_args(argv)

    window = c2.window_of(args.anchor)
    refuse_to_move_the_anchor(args.out, window)
    registry = load_registry(screen.REGISTRY)
    compiled, aliases = instruments(registry)
    pins = pinned_by_the_ratified_census()
    sources = {handle: source for source in registry.sources for handle in source.telegram_channels}

    rows = [
        channel_row(handle, source, window, compiled, aliases, pins)
        for handle, source in sorted(sources.items())
    ]
    frame_rows = sorted(
        (
            {**entry, "channel": row["handle"], "carrier": "post_text"}
            for row in rows
            if row["posts_in_window"] != c2.CANNOT_ANSWER
            for entry in row["_passed"]
        ),
        key=lambda entry: (entry["channel"], entry["id"]),
    )
    for row in rows:
        row.pop("_passed", None)

    scored = [row for row in rows if row["posts_in_window"] != c2.CANNOT_ANSWER]
    passed = sum(row["passed"] for row in scored)
    rate = cite(
        projection.RATE,
        "rate.usd_per_second",
        "the settled serverless rate — the one field every projection in this repo has used since"
        " sku-b, and the one results/projection_5c2.json prices both other legs with",
    )
    controls = frame.run_controls(compiled, aliases)
    carrying = {
        kind: sum(row["passed_carrying"][kind] for row in scored)
        for kind in ("currency", "percent", "size")
    }

    record = {
        "phase": "5c2-prep-c3a — the pre-filter census of the post leg",
        "contract": "docs/PROMPT-5c2-prep-c3a.md deliverable 3; docs/SPEC.md amendment 3.18 (7)(e)",
        "asks": "how many of the window's posts the relevance pre-filter passes, and what they cost",
        "decides_nothing": (
            "the pre-registration (prep-c3b) pins the number; this file only counts it. Nothing is"
            " fetched, nothing is spent, and no row is asked of any model"
        ),
        "anchor": {
            **window,
            "why": "ratified by SPEC 3.18 (7)(a) — the corpus's own last day + 1. The two"
            " alternatives priced beside it in results/census_5c2.json were seen and declined",
            "ratified_by": "the operator, 2026-08-13 (3.18 (7)(a))",
        },
        "rule": frame.__doc__.split("\n\n")[0].strip(),
        "instrument": {
            "prefilter": "market_pulse.positions.prefilter — a watchlist brand or a tracked"
            " category term AND a size/price pattern, both on the SAME line",
            "not_the_entry_gate": (
                "3.18 (7)(e) is explicit: «never the channel entry gate of 3.12, which gates"
                " CHANNELS». This filter gates ROWS and every registry channel is screened"
            ),
            "lexicon": {"path": rel(LEXICON), "sha256": sha256_of(LEXICON)},
            "registry": {"path": rel(screen.REGISTRY), "sha256": sha256_of(screen.REGISTRY)},
            "same_code_as_the_pass": (
                "scripts/run_loop.py :: posts_of calls the same positions.prefilter over the same"
                " two files, so the population counted here is the queue that pass would answer"
            ),
        },
        "selection_pin": {
            "asks": "is this the window the operator ratified, or another one with the same dates",
            "source": f"{rel(CENSUS_5C2)} :: channels[].posts.ids_sha256",
            "census_5c2_sha256": sha256_of(CENSUS_5C2),
            "channels_pinned": len(pins),
            "channels_checked": len(scored),
            "disagreements": sorted(
                row["handle"] for row in scored if not row["matches_census_5c2"]
            ),
            "agrees": all(row["matches_census_5c2"] for row in scored),
            "why": (
                "the row COUNT can match while the rows differ — a store that moved under a later"
                " re-run produces the same total from different posts. The hash is what catches it"
            ),
        },
        "controls": controls,
        "population_reportable": all(control["ok"] for control in controls.values()),
        "totals": {
            "posts_in_window": sum(row["posts_in_window"] for row in scored),
            "with_text": sum(row["with_text"] for row in scored),
            "passed": passed,
            "passed_row_level": sum(row["passed_row_level"] for row in scored),
            "share_of_posts_in_window": (
                round(passed / sum(row["posts_in_window"] for row in scored), 4) if scored else 0.0
            ),
            "channels_with_a_pass": sum(1 for row in scored if row["passed"]),
            "passed_carrying": carrying,
            "carrying_note": (
                "rows, not matches, and the three are not exclusive. `currency` is the cheapest"
                " deterministic reading of «is this line priced at all» — the filter cannot tell an"
                " OFFER from a recipe, and «Кефір — 400 мл» is a category term beside a size in an"
                " ingredient list. `percent` is its own bucket because «82,5%» is a fat content and"
                " «-38%» is a discount, and nothing here can tell them apart"
            ),
        },
        "frame": {
            "rows": len(frame_rows),
            "ids_sha256": hashlib.sha256(
                "\n".join(entry["id"] for entry in frame_rows).encode("utf-8")
            ).hexdigest(),
            "ids_sha256_note": (
                "sha256 of the passing ids, newline-joined in this record's order —"
                " sku_prefilter_census's own convention, so prep-c3b can pin the draw"
            ),
            "evidence": "every row below carries the LINE that fired, the term that matched and"
            " the size/price pattern beside it, which is the frame convention 3.18 (7)(e) names",
        },
        "rate": rate,
        "priced": priced(passed, rate["value"]),
        "leaflet_corpus": leaflet_corpus(),
        "concentration": concentration(rows),
        "cannot_answer": {
            "channels": sorted(
                row["handle"] for row in rows if row["posts_in_window"] == c2.CANNOT_ANSWER
            ),
            "why": "no file in data/raw/posts/ — the channel has never been walked. NOT zero",
        },
        "channels": sorted(scored, key=lambda row: (-row["passed"], row["handle"])),
        "rows": frame_rows,
        "producer": producer(),
    }
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        f"window {window['since'][:10]} .. {window['until'][:10]} (28d, anchor {window['anchor']})"
    )
    totals = record["totals"]
    print(
        f"  {totals['posts_in_window']} posts in window · {totals['with_text']} with text ·"
        f" {totals['passed']} pass the pre-filter ({totals['share_of_posts_in_window']:.2%})"
        f" · row-level reading {totals['passed_row_level']}"
    )
    print(f"  of the passed: {totals['passed_carrying']}")
    print(
        f"  priced at {record['priced']['seconds_per_row']} s/row →"
        f" ${record['priced']['usd_with_drift']:.4f} with drift"
    )
    print(
        f"  selection pin vs census_5c2: {'AGREES' if record['selection_pin']['agrees'] else 'DISAGREES'}"
        f" on {record['selection_pin']['channels_checked']} channels"
    )
    header = f"\n{'channel':<30}{'posts':>7}{'texted':>8}{'pass':>6}{'share':>8}   top hit"
    print(header)
    print("-" * (len(header) - 1))
    for row in record["channels"][:15]:
        if not row["passed"]:
            break
        top = next(iter(row["by_hit"].items()), ("—", 0))
        print(
            f"{row['handle'][:29]:<30}{row['posts_in_window']:>7}{row['with_text']:>8}"
            f"{row['passed']:>6}{row['share_of_texted']:>8.1%}   {top[0]} ×{top[1]}"
        )
    for name, control in controls.items():
        print(f"control {name[:60]:<62}{'OK' if control['ok'] else 'FAILED'}")
    print(f"\nwrote {rel(args.out)}")
    return 0 if record["population_reportable"] and record["selection_pin"]["agrees"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
