#!/usr/bin/env python3
"""Score sku-b's bars 1 and 3 over the completed population, through the registered readings. ($0)

SPEC amendment 3.17 (6) states three bars; (11) says the resumed session's merged population is what
they are read over. Two of the three are arithmetic and are computed here:

* **bar 1 — leaflet brand recall**, per POST over the union of its page answers, macro-averaged over
  the posts with a non-empty gold set (R1/R2/R3);
* **bar 3 — text tier accuracy**, per adjudicated row, unreadable replies excluded and counted (R5).

**Bar 2 is never scored here.** Price-pair accuracy is a team-lead read of the dump against the page
images at acceptance (SPEC §10 — the executor never scores its own sample). Until that read exists
this writes its denominator, its reachability class under R4 and the dump that makes the read
possible, and stops there. Once it exists as `results/sku_b_pair_verdicts.json` — a transcription of
the dictated verdicts, pinned to the same dump — the share is re-derived from that file's own keys
by the applier's `checksums` and carried here. The value still comes from the read, not from this
file; what this file adds is the arithmetic and the threshold.

Every number comes from :mod:`market_pulse.scorer`, every gold key from the reference's own
``gold_key``, and every tier from ``positions.tier_from_presence`` — one function per quantity, or a
bar measures the drift between two implementations of it. Nothing is adjudicated, nothing is
repaired: a defect is named and the run stops.

    PYTHONPATH=src python3 scripts/sku_bar_verdicts.py
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import apply_sku_pair_verdicts as pair_read  # noqa: E402
import build_sku_reference_leaflet as leaflet  # noqa: E402
import validate_sku_text_pack as pack  # noqa: E402

from market_pulse import positions, provenance, scorer  # noqa: E402
from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.registry import load_registry_as_pinned  # noqa: E402

PREREG = REPO_ROOT / "results" / "sku_pilot_prereg_v4.json"
RECORD = REPO_ROOT / "results" / "sku_b_positions_v4.json"
PAIRS = REPO_ROOT / "results" / "sku_b_pair_verdicts.json"
REFERENCE = REPO_ROOT / "results" / "sku_reference_leaflet.json"
REGISTRY = REPO_ROOT / "config" / "registry.yaml"
OUT = REPO_ROOT / "results" / "sku_bar_verdicts.json"
SMOKE_OUT = REPO_ROOT / "results" / "smoke" / "sku_bar_verdicts.json"

UNREADABLE_SHARE_MAX = 0.10
"""R5: above this the instrument did not answer and bar 3 is NOT_SCORED."""

CONTRACT = (
    "docs/PROMPT-sku-b-close.md deliverable 2 (bar 2 applied and the closure);"
    " docs/PROMPT-sku-b-v4-run.md step 6 (bars 1 and 3);"
    " docs/SPEC.md amendment 3.17 (6), (11), (12)"
)
"""The provenance string written INTO the verdict record — the artifact the team lead opens at
acceptance. Nothing downstream checks it, which is why Dv170 named it: scored after the v4 session
it used to claim the verdicts were produced under the v3-run contract and cite (6) and (11) without
(12), the amendment the population's second half was bought under. A constant with a test on it,
because a string nobody re-derives is a string that stops being true silently. It now names both
contracts, because the record is written twice and the second writing is the one on disk."""


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    """Repo-relative when it can be — a path outside the tree keeps its own name rather than
    crashing, because a fixture pointed at a temporary directory is a legitimate caller."""
    resolved = path.resolve()
    return str(resolved.relative_to(REPO_ROOT)) if resolved.is_relative_to(REPO_ROOT) else str(path)


def refuse(reason: str) -> None:
    raise SystemExit(f"refused: {reason}")


def highest_tier(tiers: list[str]) -> str:
    """The best rung a row reached — `positions.TIERS` is ordered best-first."""
    return min(tiers, key=positions.TIERS.index) if tiers else "none"


def check_the_inputs_are_the_registered_ones(record: dict, prereg: dict, args) -> dict:
    """Every pin the bars stand on, re-derived. A moved gold is a different bar."""
    pins = {}
    for what, path, pinned in (
        ("prereg", args.prereg, record["prereg"]["sha256"]),
        ("leaflet gold", args.reference, prereg["bars"]["leaflet_brand_recall"]["gold"]["sha256"]),
        (
            "text pack manifest",
            REPO_ROOT / prereg["bars"]["text_tier_accuracy"]["gold"]["manifest"],
            prereg["bars"]["text_tier_accuracy"]["gold"]["manifest_sha256"],
        ),
        ("dump", args.dump, record["dump"]["sha256"]),
    ):
        found = sha256_of(path)
        if found != pinned:
            refuse(f"{what} {rel(path)} hashes {found[:16]}… and the record pins {pinned[:16]}…")
        pins[what] = {"path": rel(path), "sha256": found}

    ladder = prereg["bars"]["text_tier_accuracy"]["gold"]["ladder_sha256"]
    if positions.ladder_sha256() != ladder:
        refuse(
            f"the ladder hashes {positions.ladder_sha256()[:16]}… and the registration pins"
            f" {ladder[:16]}… — the gold and the model's tiers would come from two rungs"
        )
    if record["prereg"]["path"] != rel(args.prereg):
        refuse(f"the record was bought under {record['prereg']['path']}, not {rel(args.prereg)}")
    return pins


def check_the_population_is_complete(record: dict, prereg: dict) -> None:
    """A bar over a half-bought population is not the bar that was registered."""
    if record["population"]["unbought"]:
        refuse(
            f"{record['population']['unbought']} element(s) are still unbought — the bars read the"
            " COMPLETED population of (11), and a partial one is a different denominator"
        )
    registered = prereg["resume"]["population"]["registered"]
    sources = [outcome["source"] for outcome in record["outcomes"]]
    if len(sources) != registered or len(set(sources)) != registered:
        refuse(
            f"{len(sources)} outcomes over {len(set(sources))} distinct sources against the"
            f" registered {registered}: the merged population must carry each element exactly once"
        )


def registered_aliases(prereg: dict) -> dict[str, str]:
    """The watchlist alias table the PRE-REGISTRATION pins — never simply today's.

    SPEC 3.17 (13)(b) added three Latin display names on 2026-08-12, and one of them («Three
    Bears») resolves a dump row that was `not_in_gold` when the v4 population was bought.
    Recomputing v4's bar 1 through the amended table would report a recall nobody measured; B′
    registers the amended table and reaches it through this same call. A registration that pins no
    registry is refused rather than defaulted: which alias table a bar was scored under is not
    something a reader should have to infer from the date on the file.
    """
    pin = (prereg.get("pinned_inputs") or {}).get("config/registry.yaml")
    if pin is None:
        refuse(
            "the pre-registration pins no config/registry.yaml, so the alias table these bars were"
            " scored under is not named anywhere — SPEC 3.17 (13)(b) made that table a moving part"
        )
    return watchlist_aliases(load_registry_as_pinned(pin, REGISTRY).watchlist)


def bar_one(record: dict, dump: list[dict], prereg: dict, reference: dict, aliases: dict) -> dict:
    """Brand recall per post, macro over the posts with gold. R1 (per post), R2 (108 sent pages)."""
    bar = prereg["bars"]["leaflet_brand_recall"]
    empty = set(reference["gold"]["posts_with_an_empty_gold_set"])
    if empty != set(bar["excluded"]["posts"]):
        refuse("the reference's empty-gold posts are not the ones R3 excludes")

    extracted: dict[str, set[str]] = {}
    pages_of: dict[str, list[dict]] = {}
    for row in dump:
        if row["page"] is None:  # a text row: bar 1 reads the leaflet leg only
            continue
        key = leaflet.gold_key(row["brand_id"] or row["brand_raw"], aliases)
        extracted.setdefault(row["item"], set()).add(key)
        pages_of.setdefault(row["item"], []).append({"page": row["page"], "brand": key})

    unreadable_pages: dict[str, list[str]] = {}
    for outcome in record["outcomes"]:
        if outcome["leg"] == "page" and outcome["unreadable"]:
            unreadable_pages.setdefault(outcome["item"], []).append(outcome["source"])

    scored = [post for post in reference["posts"] if post["item"] not in empty]
    gold_sets = [set(post["brands_visible"]["gold_keys"]) for post in scored]
    pred_sets = [extracted.get(post["item"], set()) for post in scored]
    reading = scorer.leaflet_brand_recall(gold_sets, pred_sets)

    per_post = [
        {
            "item": post["item"],
            "gold": sorted(gold),
            "extracted": sorted(pred),
            "found": sorted(gold & pred),
            "missed": sorted(gold - pred),
            "not_in_gold": sorted(pred - gold),
            "recall": recall,
            "pages_sent": len(post["pages_sent"]),
            "unreadable_pages": len(unreadable_pages.get(post["item"], [])),
        }
        for post, gold, pred, recall in zip(scored, gold_sets, pred_sets, reading["per_post"])
    ]
    value = round(reading["macro"], scorer.BAR_PRECISION)
    return {
        "verbatim": bar["verbatim"],
        "reading": bar["denominator"],
        "ratification": ["R1", "R2", "R3"],
        "threshold": bar["threshold"],
        "value": value,
        "verdict": "PASS" if value >= bar["threshold"] else "FAIL",
        "n_posts": reading["n_posts"],
        "n_gold_keys": reading["n_gold"],
        "n_extracted_keys": reading["n_extracted"],
        "micro_reported_never_gated": round(reading["micro"], scorer.BAR_PRECISION),
        "precision_micro_reported_never_gated": (
            None
            if reading["precision_micro"] is None
            else round(reading["precision_micro"], scorer.BAR_PRECISION)
        ),
        "per_post": per_post,
        "precision_probe": {
            "why": bar["excluded"]["instead"],
            "posts": [
                {
                    "item": item,
                    "false_positives": sorted(extracted.get(item, set())),
                    "on_pages": pages_of.get(item, []),
                    "unreadable_pages": len(unreadable_pages.get(item, [])),
                }
                for item in sorted(empty)
            ],
        },
        "unreadable_pages": {
            "why": (
                "an unreadable page answer contributes no brand to its post's union, so it costs"
                " recall exactly as an empty answer does. The registered reading of bar 1 carries no"
                " unreadable clause (only bar 3 does), so nothing is excluded here — the exposure is"
                " reported instead"
            ),
            "n": sum(len(pages) for pages in unreadable_pages.values()),
            "by_post": {item: sorted(pages) for item, pages in sorted(unreadable_pages.items())},
        },
        "key_space": {
            "gold": reference["gold"]["definition"],
            "prediction": (
                "the SAME build_sku_reference_leaflet.gold_key, applied to the position's brand_id"
                " when the resolver found one and to brand_raw when it did not — one function on"
                " both sides, so the comparison cannot be an artefact of two spaces"
            ),
        },
    }


def bar_two(record, dump: list[dict], prereg: dict, read: dict | None = None, pin=None) -> dict:
    """The denominator and the dump; the value only when the team lead's read is on the table.

    ``read`` is `results/sku_b_pair_verdicts.json` — the dictated verdicts, transcribed and joined
    to the dump by `scripts/apply_sku_pair_verdicts.py`. The share is re-derived here from that
    file's own keys through the applier's `checksums`, never read out of it as a number: one
    implementation, two callers, and a hand-edited accuracy field would be refused by its own
    stated counts. Without the read this stays where it was — a denominator, a reachability class
    and the dump that makes the read possible.
    """
    bar = prereg["bars"]["price_pair_accuracy"]
    pairs = [row for row in dump if row["page"] is not None and row["price_old"] is not None]
    rule = bar["reachability"]["rule"]
    if not pairs:
        reach = "NOT_REACHABLE"
    elif len(pairs) < 10:
        reach = "REPORTED_NOT_SCORED"
    else:
        reach = "SCOREABLE"
    out = {
        "verbatim": bar["verbatim"],
        "reading": bar["denominator"],
        "ratification": ["R4"],
        "threshold": bar["threshold"],
        "value": None,
        "verdict": "PENDING_TEAM_LEAD",
        "why_no_value": (
            "SPEC §10: the executor never scores its own sample. Bar 2 is the team lead's read of"
            " each cited page image against the pair in the dump, at acceptance"
        ),
        "n_pairs": len(pairs),
        "reachability": {"rule": rule, "class": reach},
        "dump": {
            "path": record["dump"]["path"],
            "sha256": record["dump"]["sha256"],
            "rows": record["dump"]["rows"],
            "columns": record["dump"]["columns"],
        },
        "procedure": bar["procedure"],
    }
    if read is None:
        return out

    if read["dump"]["sha256"] != record["dump"]["sha256"]:
        refuse(
            f"the read was taken over a dump hashing {read['dump']['sha256'][:16]}… and the record"
            f" pins {record['dump']['sha256'][:16]}… — those are two different sets of pairs"
        )
    sums = pair_read.checksums(read["keys"], read["expected"])
    if sums["rows"] != len(pairs):
        refuse(
            f"the read covers {sums['rows']} rows and the bar's denominator is {len(pairs)}:"
            " every pair in the dump is in the read, or the accuracy has a different bottom"
        )
    value = round(sums["accuracy"], scorer.BAR_PRECISION)
    verdict = "PASS" if value >= bar["threshold"] else "FAIL"
    out.update(
        value=value,
        verdict=verdict,
        why_no_value=None,
        stated=(
            f"{sums['accuracy_4dp']:.4f} vs {bar['threshold']:.2f} — {verdict}"
            f" (n={sums['rows']}, read by {read['read_by']} {read['read_on']})"
        ),
        read={
            **(pin or {}),
            "by": read["read_by"],
            "on": read["read_on"],
            "scope": read["read_scope"],
            "contract": read["contract"],
            "keys": sums["keys"],
            "correct_rows": sums["correct_rows"],
            "wrong_rows": sums["wrong_rows"],
            "accuracy_4dp": sums["accuracy_4dp"],
            "diagnosis": read["diagnosis"],
        },
    )
    return out


def bar_three(record: dict, dump: list[dict], prereg: dict, readings: list[dict]) -> dict:
    """Tier accuracy per adjudicated row; unreadable replies excluded and counted (R5)."""
    bar = prereg["bars"]["text_tier_accuracy"]
    gold_tier = {row["id"]: row["tier"] for row in readings}
    # "the adjudicated rows that came back with a legal tick set. A row the operator left untouched
    # is not gold and is not counted" — the bar's own denominator. `tier_from_presence` reads five
    # blank cells as `none`, which is also a legitimate ANSWER, so an unfinished pack would score
    # its blanks as agreements with every empty model reply. The predicate is the validator's.
    untouched = {row["id"] for row in readings if not pack.is_adjudicated(row)}
    tiers_of: dict[str, list[str]] = {}
    for row in dump:
        if row["page"] is None:
            tiers_of.setdefault(row["item"], []).append(row["tier"])

    rows, excluded, not_gold = [], [], []
    for outcome in record["outcomes"]:
        if outcome["leg"] != "text":
            continue
        item = outcome["item"]
        if item not in gold_tier:
            refuse(f"{item} was asked in the text leg and is not in the adjudicated pack")
        if item in untouched:
            not_gold.append(item)
            continue
        if outcome["unreadable"]:
            excluded.append({"id": item, "reason": outcome["unreadable"]})
            continue
        rows.append(
            {
                "id": item,
                "carrier": outcome["carrier"],
                "gold": gold_tier[item],
                "model": highest_tier(tiers_of.get(item, [])),
                "n_positions": outcome["n_positions"],
            }
        )
    for row in rows:
        row["agrees"] = row["gold"] == row["model"]

    asked = len(rows) + len(excluded)
    share = len(excluded) / asked if asked else 0.0
    reasons: dict[str, int] = {}
    for row in excluded:
        reasons[row["reason"]] = reasons.get(row["reason"], 0) + 1

    verdict, why = None, None
    if share > UNREADABLE_SHARE_MAX:
        verdict, why = (
            "NOT_SCORED",
            (
                f"{len(excluded)} of {asked} replies were unreadable ({share:.1%} >"
                f" {UNREADABLE_SHARE_MAX:.0%}) — the instrument did not answer"
            ),
        )
    elif len(rows) < 20:
        verdict, why = (
            "NOT_SCORED",
            (
                f"{len(rows)} scoreable rows against the registered floor of 20: a bar at"
                f" {bar['threshold']} moves 5 pp per row below it"
            ),
        )
    value = round(scorer.text_tier_accuracy(*zip(*[(r["gold"], r["model"]) for r in rows])), 10)
    if verdict is None:
        verdict = "PASS" if value >= bar["threshold"] else "FAIL"
    confusion: dict[str, int] = {}
    for row in rows:
        confusion[f"{row['gold']} -> {row['model']}"] = (
            confusion.get(f"{row['gold']} -> {row['model']}", 0) + 1
        )
    return {
        "verbatim": bar["verbatim"],
        "reading": bar["comparison"],
        "ratification": ["R5"],
        "threshold": bar["threshold"],
        "value": value,
        "verdict": verdict,
        "why_not_scored": why,
        "n_scored": len(rows),
        "n_asked": asked,
        "not_gold": {
            "rule": bar["denominator"],
            "n": len(not_gold),
            "ids": not_gold,
            "why": (
                "rows the operator never touched. Not unreadable and not wrong — outside the"
                " denominator, because five blank cells are not an adjudication"
            ),
        },
        "by_carrier": bar["gold"]["by_carrier"],
        "unreadable": {
            "rule": bar["unreadable_rows"],
            "n": len(excluded),
            "share": round(share, 4),
            "max_share": UNREADABLE_SHARE_MAX,
            "by_reason": reasons,
            "ids": [row["id"] for row in excluded],
        },
        "reachability": {"rule": bar["reachability"]["rule"], "n_scored": len(rows)},
        "confusion": dict(sorted(confusion.items())),
        "rows": rows,
    }


def closure(bars: dict, prereg: dict) -> dict:
    """What the registration says happens now, with the bars that trigger it named from the data.

    `attempts.on_failure` is quoted out of the registration rather than restated here — the
    consequence of a failed bar was fixed before the run and a producer that paraphrases it is a
    producer that can soften it. The rule says "a failed bar" in the singular; which bars actually
    failed is a fact about the verdicts, so it is derived, and a bar still without a verdict makes
    the state UNDETERMINED rather than a closure taken on two thirds of the evidence.
    """
    decided = {name: bar["verdict"] for name, bar in bars.items()}
    failed = sorted(name for name, verdict in decided.items() if verdict == "FAIL")
    passed = sorted(name for name, verdict in decided.items() if verdict == "PASS")
    open_bars = sorted(name for name, v in decided.items() if v not in ("PASS", "FAIL"))
    if open_bars:
        state, why = "UNDETERMINED", f"{open_bars} carry no verdict yet"
    elif failed:
        state = "CLOSED — instrument not ready, BY MEASUREMENT"
        why = f"{len(failed)} of {len(decided)} bars failed: {', '.join(failed)}"
    else:
        state, why = "NOT CLOSED BY THIS RULE", "every bar passed"
    return {
        "rule": prereg["attempts"]["on_failure"],
        "rule_source": "results/sku_pilot_prereg_v4.json attempts.on_failure, quoted verbatim",
        "verdicts": decided,
        "failed_bars": failed,
        "passed_bars": passed,
        "undecided_bars": open_bars,
        "state": state,
        "why": why,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, default=RECORD)
    parser.add_argument("--dump", type=Path, help="default: the record's own dump path")
    parser.add_argument("--prereg", type=Path, default=PREREG)
    parser.add_argument("--reference", type=Path, default=REFERENCE)
    parser.add_argument("--pack", type=Path, default=None, help="default: the manifest's own pack")
    parser.add_argument("--pairs", type=Path, default=PAIRS, help="the team lead's bar-2 read")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    if not args.record.exists():
        refuse(f"{rel(args.record)} does not exist — the bars are read from the run's own record")
    record = json.loads(args.record.read_text(encoding="utf-8"))
    prereg = json.loads(args.prereg.read_text(encoding="utf-8"))
    # a (10)(a) refusal writes a record with no dump at all. Measured on the sku-b-v3 session,
    # where this crashed on `REPO_ROOT / None` instead of saying what was wrong: the record of a
    # session that bought nothing is a legitimate thing to point this at, and by far the likeliest.
    if record.get("stopped_before_gold") or record["dump"].get("path") is None:
        refuse(
            f"{rel(args.record)} stopped before the first gold call — it has no dump and no"
            " answers. There is nothing to score: the bars need the COMPLETED population of (11)"
        )
    args.dump = args.dump or REPO_ROOT / record["dump"]["path"]
    # a smoke record must never be able to write the paid verdict, the F4 rule of the driver
    if args.out is None:
        args.out = SMOKE_OUT if record.get("smoke") else OUT
    elif record.get("smoke") and args.out == OUT:
        refuse("a smoke record cannot be written to the paid verdict path")

    pins = check_the_inputs_are_the_registered_ones(record, prereg, args)
    check_the_population_is_complete(record, prereg)

    reference = json.loads(args.reference.read_text(encoding="utf-8"))
    manifest_path = REPO_ROOT / prereg["bars"]["text_tier_accuracy"]["gold"]["manifest"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    readings, defects = pack.check(pack.read_pack(args.pack or Path(manifest["pack"])), manifest)
    if defects:
        refuse("the adjudicated pack is not scoreable: " + "; ".join(defects))
    aliases = registered_aliases(prereg)

    # bar 2 has a value only once the team lead's read is on disk. A missing file is the state the
    # bar was in for the whole pilot and is not an error; a file that does not parse or does not
    # match the dump is, and lands in `bar_two`.
    read, pin = None, None
    if args.pairs is not None and args.pairs.exists():
        read = json.loads(args.pairs.read_text(encoding="utf-8"))
        pin = {"path": rel(args.pairs), "sha256": sha256_of(args.pairs)}

    dump = [json.loads(line) for line in args.dump.read_text(encoding="utf-8").splitlines() if line]
    bars = {
        "leaflet_brand_recall": bar_one(record, dump, prereg, reference, aliases),
        "price_pair_accuracy": bar_two(record, dump, prereg, read, pin),
        "text_tier_accuracy": bar_three(record, dump, prereg, readings),
    }

    out = {
        "phase": "sku-b — the three bars over the completed population",
        "contract": CONTRACT,
        "class": (
            "MEASUREMENT. Bars 1 and 3 are computed by market_pulse.scorer over the merged"
            " population; bar 2's verdicts are the team lead's read, transcribed by"
            " scripts/apply_sku_pair_verdicts.py and re-derived here from its keys. No adjudication"
            " happens in this file"
        ),
        "smoke": bool(record.get("smoke")),
        "prereg": {"path": rel(args.prereg), "sha256": pins["prereg"]["sha256"]},
        "record": {"path": rel(args.record), "sha256": sha256_of(args.record)},
        "pins": pins,
        "population": record["population"],
        "sessions": record["resume"]["sessions"],
        "ratification_required": prereg["ratification_required"],
        "bars": bars,
        "closure": closure(bars, prereg),
        "scored_by": {
            "bar_1": "market_pulse.scorer.leaflet_brand_recall",
            "bar_2": (
                "the team lead's read; the share re-derived from its keys by"
                " apply_sku_pair_verdicts.checksums"
            ),
            "bar_3": "market_pulse.scorer.text_tier_accuracy",
            "tiers": "market_pulse.positions.tier / tier_from_presence",
            "gold_keys": "build_sku_reference_leaflet.gold_key",
        },
    }
    out["git"] = provenance.git_state(args.out)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"{rel(args.record)} — {record['population']['asked']} elements, unbought 0")
    for name, bar in bars.items():
        value = "—" if bar["value"] is None else f"{bar['value']:.4f}"
        print(f"  {name:24s} {value:>8} vs {bar['threshold']:.2f}   {bar['verdict']}")
    one, three = bars["leaflet_brand_recall"], bars["text_tier_accuracy"]
    print(
        f"  bar 1 over {one['n_posts']} posts · micro {one['micro_reported_never_gated']:.4f} ·"
        f" precision {one['precision_micro_reported_never_gated']}"
    )
    print(
        f"  bar 3 over {three['n_scored']} of {three['n_asked']} rows ·"
        f" {three['unreadable']['n']} unreadable ({three['unreadable']['share']:.1%})"
    )
    two = bars["price_pair_accuracy"]
    print(
        f"  bar 2 over {two['n_pairs']} pairs, the team lead's read — "
        + (two["stated"] if two.get("stated") else "no read on disk, PENDING")
    )
    print(f"  closure: {out['closure']['state']} ({out['closure']['why']})")
    print(f"wrote {rel(args.out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
