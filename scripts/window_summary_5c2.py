#!/usr/bin/env python3
"""The aggregates the sitting's rows WEAR — SPEC 3.18 (6), computed once and read by the pack.

3.18 (6) shows the operator ten rows and requires each one to be captioned with "the aggregate the
row belongs to … so a single row is never read as the population". That makes the aggregates an
artifact rather than a paragraph: they have to exist, be re-derivable, and be the same numbers on
the sitting's table as in Phase 6's dashboard. This is that record.

**What it reads, and nothing else.** `data/derived/` — the 5 423 evidence rows the paid run wrote —
plus the sealed `results/prereg_5c2_run.json` for the populations it must agree with. One file
outside those two: `config/registry.yaml`, and only THROUGH the registration, whose
`pinned_inputs` carries its sha256 and which this script re-checks before reading it. The window's
comments are not in `data/raw` for this script's purposes at all: a comment's text is recovered
from the `rendering` the model was actually given (:func:`comment_text`), which is the stronger
source — the language and the brand match are computed on the exact string that was sent.

**The fourth head does not exist.** 3.18 (6) asks for "sentiment, sarcasm, intents, and the brand
attribution" per comment, and `T1v2_with_post` returns THREE labels: there is no brand head on the
comment instrument and no model verdict to show. What this record carries under
`brand_attribution` is the deterministic watchlist matcher (`market_pulse.brands`) run over the
sent text — named as such in the record, because a string match presented as a model's answer would
be the worst kind of number at an operator sitting.

**No clock and no git block.** Two runs of this script over the same `data/derived/` are
byte-identical, which is what lets the report show a determinism pair and what lets
`tests/test_window_summary_5c2.py` re-derive every number instead of trusting it. A timestamp or a
`git_state()` — which `scripts/build_sitting_pack.py` does carry — would make that impossible.

    PYTHONPATH=src python3 scripts/window_summary_5c2.py
    PYTHONPATH=src python3 scripts/window_summary_5c2.py --derived-root <sandbox>  # the control
"""

import argparse
import json
import statistics
import sys
from collections import Counter
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from market_pulse import brands, langid, loop, prompts  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

DERIVED = REPO_ROOT / "data" / "derived"
PREREG = REPO_ROOT / "results" / "prereg_5c2_run.json"
REGISTRY = REPO_ROOT / "config" / "registry.yaml"
PINNED_REGISTRY = "config/registry.yaml"
"""The KEY the seal pins the watchlist under, and not `rel(--registry)`.

A caller may point `--registry` anywhere — the negative control does. What it may never do is
escape the pin by being somewhere the registration has no entry for: the sha of whatever file is
handed in is held against the one the run was registered against, or nothing is read at all."""

OUT = REPO_ROOT / "results" / "window_summary_5c2.json"

BORROWED = (
    "src/market_pulse/prompts.py",
    "src/market_pulse/langid.py",
    "src/market_pulse/brands.py",
    "src/market_pulse/positions.py",
    "src/market_pulse/loop.py",
)
"""The modules whose behaviour is IN these numbers. Hashed beside the producer's own sha because
a summary is only reproducible together with the parser that read the replies — `prompts.parse_reply`
decides what counts as an answer, `langid.detect` decides the language column, and `brands` decides
the attribution. An edit to any of them moves this record, and the test that regenerates it says so.
"""

DEPTH_LAW = (
    "SPEC 3.18 (1): the promo-depth aggregate is computed from the promo price and the PRINTED"
    " -N% badge. Where BOTH prices exist the code-computed arithmetic of 3.17 (3) stands and the"
    " printed % never substitutes it. The extracted old price is KEPT as the more accurate depth"
    " input and is FLAGGED — it never reaches a surface that prints it as a price and no was/now"
    " claim is built on it, so this record counts the rows that carry one and prints no value of"
    " it. Reconstructing the old price from the promo and the badge stays forbidden."
)

BRAND_INSTRUMENT = (
    "market_pulse.brands.find_watchlist_brands over config/registry.yaml's watchlist — a"
    " DETERMINISTIC string match on the text that was sent, not a model head. The comment"
    " instrument is T1v2_with_post and it returns three labels: sentiment, sarcasm, intents."
    " 3.18 (6) names a fourth verdict («the brand attribution») that this instrument does not"
    " produce; the matcher is what the sitting can be shown, and it is named rather than passed"
    " off as the model's answer."
)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def sha256_of(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def read_rows(path: Path) -> list[dict]:
    """One derived file, or a refusal naming it. §5's honesty rule: no silent empty aggregate."""
    if not path.exists():
        raise SystemExit(
            f"{rel(path)}: not found — SPEC 3.18 (6)(b) builds the sitting from result files and"
            " fails loudly on a missing source. An aggregate computed over the files that happen"
            " to be there is a number about the disk, not about the window."
        )
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def leg_files(root: Path, record_type: str) -> list[Path]:
    """Every channel file of one kind, sorted. The store's own layout: `<record_type>s/<handle>`.

    A GLOB, so this cannot see one channel's file go missing — it would simply return the others
    and every aggregate would be about a smaller window. That hole is closed one layer up by
    :func:`assert_populations`, which holds the counted rows against the sealed 5 075 / 159 / 44:
    the negative control removes `post_texts/silposilpo.jsonl` and the refusal names `42 on disk,
    44 registered`. What this function itself refuses is the whole leg — a missing or empty
    directory, which the glob would otherwise answer with a legal-looking `[]`.
    """
    folder = root / f"{record_type}s"
    if not folder.is_dir():
        raise SystemExit(
            f"{rel(folder)}: not a directory — the {record_type} leg of the run wrote its evidence"
            " there and this summary cannot be computed without it"
        )
    found = sorted(folder.glob("*.jsonl"))
    if not found:
        raise SystemExit(f"{rel(folder)}: no channel file — the {record_type} leg has no evidence")
    return found


# --- recovering what was SENT --------------------------------------------------------------------


def sent_parts(row: dict) -> tuple[str, str]:
    """(the post, the comment) as they were SENT, split out of the row's own `rendering`.

    Recovered from `rendering` rather than joined back to `data/raw`: this record's whole input is
    the derived store, and the strings inside the delimiters are the exact ones the model read. A
    join could quietly answer with a row the run never sent.

    The split is GUESSED and then PROVEN: `prompts.build_messages` is re-run on the two halves and
    the result must equal the recorded rendering byte for byte. That is why no delimiter-in-the-text
    edge case has to be argued about here — a wrong cut cannot re-render into the row it came from.
    """
    where = f"{row['channel']}:{row['msg_id']}"
    content = row["rendering"][0]["content"]
    prefix, closing = f"{prompts.PROMPTS[row['task']]}\n\n<post>\n", "\n</comment>"
    if not content.startswith(prefix) or not content.endswith(closing):
        raise SystemExit(
            f"{where}: the rendering is not a {row['task']} request — the evidence row cannot be"
            " read back to what the model was given, which is what 3.18 (6) shows the operator"
        )
    post, sep, text = content[len(prefix) : -len(closing)].partition("\n</post>\n\n<comment>\n")
    if not sep or prompts.build_messages(row["task"], text, parent=post) != row["rendering"]:
        raise SystemExit(
            f"{where}: the post and the comment do not re-render into the rendering on disk."
            " Stop rather than caption an operator's row with a string the model was not sent."
        )
    return post, text


def comment_text(row: dict) -> str:
    return sent_parts(row)[1]


# --- the comment leg ------------------------------------------------------------------------------


def comment_verdicts(rows: list[dict], aliases: dict[str, str]) -> list[dict]:
    """One row per comment: the three labels, the language, and the watchlist match.

    A reply the parser refuses is kept with `labels: None` and its reason. It is NOT folded into
    `intents: []`: an unreadable answer and "this comment is about none of the six" are different
    states, and the empty class is exactly where parse failures hide.
    """
    out = []
    for row in rows:
        text = comment_text(row)
        try:
            labels = prompts.parse_reply(row["task"], row["reply"]["content"])
            reason = None
        except prompts.ParseError as err:
            labels, reason = None, err.reason
        out.append(
            {
                "channel": row["channel"],
                "msg_id": row["msg_id"],
                "labels": labels,
                "unreadable": reason,
                "language": langid.detect(text),
                "brands": [
                    found["brand_id"] for found in brands.find_watchlist_brands(text, aliases)
                ],
            }
        )
    return out


def comment_block(verdicts: list[dict]) -> dict:
    """The per-head distributions of one population — the caption a shown comment wears.

    Every rate names its own denominator. `sarcasm_rate` divides by the rows the parser SCORED,
    never by the rows asked: a run with unreadable replies has two denominators and only one of
    them is the instrument's.
    """
    scored = [row for row in verdicts if row["labels"]]
    sarcastic = sum(1 for row in scored if row["labels"]["sarcasm"])
    intents = Counter(label for row in scored for label in row["labels"]["intents"])
    mentions = Counter(brand for row in verdicts for brand in row["brands"])
    by_language: dict[str, Counter] = {}
    for row in scored:
        by_language.setdefault(row["language"], Counter())[row["labels"]["sentiment"]] += 1
    return {
        "rows": len(verdicts),
        "scored": len(scored),
        "unreadable": {
            "rows": len(verdicts) - len(scored),
            "reasons": dict(Counter(row["unreadable"] for row in verdicts if row["unreadable"])),
        },
        "sentiment": dict(Counter(row["labels"]["sentiment"] for row in scored)),
        "sarcasm": {
            "true": sarcastic,
            "false": len(scored) - sarcastic,
            "rate": round(sarcastic / len(scored), 4) if scored else None,
            "denominator": "scored",
        },
        "intents": {
            "frequency": dict(intents),
            "rows_with_no_intent": sum(1 for row in scored if not row["labels"]["intents"]),
            "labels_per_scored_row": round(sum(intents.values()) / len(scored), 4)
            if scored
            else None,
        },
        "language": {
            "rows": dict(Counter(row["language"] for row in verdicts)),
            "note": "over ALL rows — the language is a property of the text, not of the reply",
            "sentiment": {name: dict(counts) for name, counts in sorted(by_language.items())},
        },
        "brand_attribution": {
            "instrument": BRAND_INSTRUMENT,
            "rows_with_a_brand": sum(1 for row in verdicts if row["brands"]),
            "mentions": dict(mentions),
        },
    }


# --- the position legs ----------------------------------------------------------------------------

PROMO_FIELDS = ("price_promo", "price_old", "discount_pct_printed", "discount_footnote")


def position_block(rows: list[dict]) -> dict:
    """The tier ladder's own distribution, and the promo/depth fields counted before valued.

    `depth` and `depth_disagrees_with_printed` are read off the row — `loop.page_rows` computes
    them at write time because they are methods on a frozen dataclass and no reader of a JSON row
    could call them. Two depth readings are reported side by side and neither is corrected into the
    other, which is what :data:`DEPTH_LAW` requires.
    """
    positions = [row["position"] for row in rows]
    pair_depth = [one["depth"] for one in positions if one["depth"] is not None]
    badge = [
        one["discount_pct_printed"] for one in positions if one["discount_pct_printed"] is not None
    ]
    return {
        "rows": len(rows),
        "tier": dict(Counter(row["tier"] for row in rows)),
        "presence": {
            field: sum(1 for row in rows if row["presence"][field])
            for field in ("brand", "line", "category", "size", "attribute")
        },
        "warnings": dict(Counter(name for row in rows for name in row["warnings"])),
        "category": dict(Counter(one["category"] for one in positions if one["category"])),
        "brand_resolved": sum(1 for one in positions if one["brand_id"]),
        "price_fields_present": {
            field: sum(1 for one in positions if one[field] not in (None, False))
            for field in PROMO_FIELDS
        },
        "price_fields_absent": {
            field: sum(1 for one in positions if one[field] in (None, False))
            for field in PROMO_FIELDS
        },
        "price_qualifier": dict(Counter(one["price_qualifier"] or "absent" for one in positions)),
        "depth": {
            "law": DEPTH_LAW,
            "from_printed_badge": _spread([value / 100 for value in badge]),
            "from_price_pair": _spread(pair_depth)
            | {"reading": "the arithmetic of 3.17 (3), kept and FLAGGED — never a printed price"},
            "printed_disagrees_with_computed": sum(
                1 for one in positions if one["depth_disagrees_with_printed"]
            ),
        },
    }


def _spread(values: list[float]) -> dict:
    """n / min / median / max of a depth reading, at four decimals. Empty says so with nulls."""
    if not values:
        return {"n": 0, "min": None, "median": None, "max": None}
    return {
        "n": len(values),
        "min": round(min(values), 4),
        "median": round(statistics.median(values), 4),
        "max": round(max(values), 4),
    }


def marker_block(rows: list[dict]) -> dict:
    """A page or a post as an ANSWER: it found positions, it found none, or it was unreadable.

    Three states and they are counted apart. `n_positions: 0` is a real answer — the page or the
    post was read and carried nothing of the tracked category — and `unreadable` is the instrument
    failing; folding the second into the first is how a parser's bad day reads as an empty market.
    """
    unreadable = [row for row in rows if row["unreadable"]]
    found = [row for row in rows if not row["unreadable"] and row["n_positions"]]
    return {
        "rows": len(rows),
        "with_positions": len(found),
        "empty": len(rows) - len(unreadable) - len(found),
        "unreadable": {
            "rows": len(unreadable),
            "reasons": dict(Counter(row["unreadable"] for row in unreadable)),
        },
        "positions": sum(row["n_positions"] for row in rows if row["n_positions"]),
    }


def by_channel(rows: list[dict], block) -> dict:
    """The same block per channel, sorted — what a shown row's caption actually reads from."""
    channels: dict[str, list[dict]] = {}
    for row in rows:
        channels.setdefault(row["channel"], []).append(row)
    return {handle: block(channels[handle]) for handle in sorted(channels)}


# --- the record -----------------------------------------------------------------------------------


def registry_through_the_seal(prereg: dict, path: Path):
    """The watchlist, read only after the registration's own pin agrees with the bytes on disk.

    `config/registry.yaml` is not `data/derived/` and is read anyway, for one head this record has
    to carry. It is legal because the sealed registration pins its sha256 — so the file is reached
    THROUGH the seal, and a registry that moved since the run is a refusal here rather than a
    brand column measured against a different watchlist than the one the run was priced on.
    """
    pinned = prereg["pinned_inputs"][PINNED_REGISTRY]
    found = sha256_of(path)
    if found != pinned:
        raise SystemExit(
            f"{rel(path)} hashes to {found[:16]}… and the sealed registration pins {pinned[:16]}…"
            " — the watchlist this summary would attribute brands with is not the one the run was"
            " registered against. Stop and report."
        )
    return load_registry(path)


def summarise(derived: Path, prereg_path: Path, registry_path: Path) -> dict:
    prereg = json.loads(read_text_or_refuse(prereg_path))
    registry = registry_through_the_seal(prereg, registry_path)
    aliases = brands.watchlist_aliases(registry.watchlist)

    sources: dict[str, str] = {}

    def load(record_type: str) -> list[dict]:
        rows = []
        for path in leg_files(derived, record_type):
            sources[rel(path)] = sha256_of(path)
            rows += read_rows(path)
        return rows

    comments = load(loop.RECORD_TYPE)
    pages = load(loop.PAGE_RECORD_TYPE)
    page_positions = load(loop.POSITION_RECORD_TYPE)
    posts = load(loop.POST_RECORD_TYPE)
    post_positions = load(loop.POST_POSITION_RECORD_TYPE)

    verdicts = comment_verdicts(comments, aliases)
    per_channel: dict[str, list[dict]] = {}
    for row in verdicts:
        per_channel.setdefault(row["channel"], []).append(row)
    all_positions = page_positions + post_positions

    record = {
        "phase": "5c2-validate-prep",
        "contract": (
            "SPEC 3.18 (6) — every row shown at the operator sitting is captioned with the"
            " aggregate it belongs to, so a single row is never read as the population. These are"
            " those aggregates; results/validate_5c2_pack.json reads them and computes none."
        ),
        "authority": rel(prereg_path),
        "reads": (
            f"{rel(derived)} only, plus {rel(registry_path)} through the seal's own pin."
            " No clock, no git block: two runs over the same evidence are byte-identical."
        ),
        "populations_registered": {
            kind: prereg["populations"][kind]["rows"]
            for kind in ("comment", "leaflet_page", "post_text")
        },
        "comment": {
            "task": loop.COMMENT_TASK,
            "prompt_sha256": prompts.prompt_sha256(loop.COMMENT_TASK),
            "heads": ["sentiment", "sarcasm", "intents"],
            "total": comment_block(verdicts),
            "per_channel": {
                handle: comment_block(per_channel[handle]) for handle in sorted(per_channel)
            },
        },
        "leaflet_page": {
            "task": loop.PAGE_TASK,
            "prompt_sha256": prompts.prompt_sha256(loop.PAGE_TASK),
            "posts": len({row["parent_msg_id"] for row in pages}),
            "total": marker_block(pages),
            "per_channel": by_channel(pages, marker_block),
        },
        "post_text": {
            "task": loop.POST_TASK,
            "prompt_sha256": prompts.prompt_sha256(loop.POST_TASK),
            "total": marker_block(posts),
            "per_channel": by_channel(posts, marker_block),
        },
        "position_row": {
            "total": position_block(all_positions),
            "by_carrier": {
                loop.CARRIER: position_block(page_positions),
                loop.POST_CARRIER: position_block(post_positions),
            },
            "per_channel": by_channel(all_positions, position_block),
        },
        "sources": sources,
        "producer": {
            "script": rel(Path(__file__)),
            "sha256": sha256_of(Path(__file__).resolve()),
            "borrowed": {name: sha256_of(REPO_ROOT / name) for name in BORROWED},
        },
    }
    assert_populations(record, prereg)
    return record


def read_text_or_refuse(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"{rel(path)}: not found — this record cannot be written without it")
    return path.read_text(encoding="utf-8")


def assert_populations(record: dict, prereg: dict) -> None:
    """The three legs, against the seal. A summary over fewer rows than were bought is a defect."""
    counted = {
        "comment": record["comment"]["total"]["rows"],
        "leaflet_page": record["leaflet_page"]["total"]["rows"],
        "post_text": record["post_text"]["total"]["rows"],
    }
    wrong = {
        kind: (rows, prereg["populations"][kind]["rows"])
        for kind, rows in counted.items()
        if rows != prereg["populations"][kind]["rows"]
    }
    if wrong:
        lines = "; ".join(
            f"{k}: {got} on disk, {want} registered" for k, (got, want) in wrong.items()
        )
        raise SystemExit(
            f"the evidence does not carry the registered population — {lines}. The sitting is shown"
            " rows drawn from the window's own output and the window is what the seal names."
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--derived-root", type=Path, default=DERIVED)
    parser.add_argument("--prereg", type=Path, default=PREREG)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)

    record = summarise(args.derived_root, args.prereg, args.registry)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    comment, position = record["comment"]["total"], record["position_row"]["total"]
    print(f"wrote {rel(args.out)}  sha256 {sha256_of(args.out)[:16]}…")
    print(
        f"  comments      {comment['rows']} rows, {comment['scored']} scored,"
        f" {comment['unreadable']['rows']} unreadable · sarcasm {comment['sarcasm']['rate']}"
        f" · languages {comment['language']['rows']}"
    )
    print(f"  positions     {position['rows']} rows · tiers {position['tier']}")
    print(
        f"  leaflet pages {record['leaflet_page']['total']} \n"
        f"  post texts    {record['post_text']['total']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
