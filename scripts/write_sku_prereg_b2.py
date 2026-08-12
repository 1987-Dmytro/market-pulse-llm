#!/usr/bin/env python3
"""Write `results/sku_pilot_prereg_b2.json` — the B′ pre-registration, BESIDE v4 ($0).

Deliverable 4 of `docs/PROMPT-skub2-prep.md`, transcribing SPEC 3.17 (13)(c) and (13)(d). v4 is
SEALED and stays true: it is what the 121 bought elements were measured under, and its bars are
what closed the pilot. This registers the ONE re-measurement (13)(d) authorises, under instrument
v2, over the same 138 elements.

**It refuses to write while any decomposition pair is still `PENDING_TEAM_LEAD`**, and today four
are (#4, #9, #28, #29). That is not a defect to work around: (13)(c) derives the B′ gold from the
team lead's verdicts, each of those four can still leave the denominator, and a registration whose
denominator moves after it is committed is not a registration. The record lands at the B′-prep
acceptance, in its own commit, before the session.

Three things this file does that v4's producer does not:

* **it pins a law that contains its own authority.** `registered_law` strips every marked
  ratification block; v1–v4 predate all of them, and B′ does not — it is registered UNDER (13). So
  the SPEC pin is taken over the law with block `-7` KEPT and the rest stripped.
* **it rebuilds the gold rather than filtering it.** (13)(b) made two brand_ids their own aliases,
  so `gold_key` answers `rud` where the sealed reference stores `raw:rud`. Every reviewer name is
  keyed TWICE — once under the v4 alias table, to join the decomposition's verdicts, and once under
  today's, to write the B′ key — and the two spaces are never bridged by stripping a prefix.
* **it buys all 138.** (11)(a)'s exactly-once rule was written for a resumed session; (13)(d) says
  «one re-measurement of instrument v2 over the same 138 elements», and a re-measurement of a
  changed instrument cannot reuse the old instrument's answers. Stated as a reading, out loud.

    PYTHONPATH=src python3 scripts/write_sku_prereg_b2.py

Writes nothing and exits non-zero while a pair is pending.
"""

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_sku_reference_leaflet as leaflet  # noqa: E402
import write_sku_prereg as v4  # noqa: E402

from market_pulse import provenance  # noqa: E402
from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.registry import load_registry, load_registry_as_pinned  # noqa: E402

SPEC = v4.SPEC
REFERENCE = v4.REFERENCE
PACK_MANIFEST = v4.PACK_MANIFEST
CENSUS = v4.CENSUS
REGISTRY = REPO_ROOT / "config" / "registry.yaml"
LEXICON = v4.LEXICON
PARSER = REPO_ROOT / "src" / "market_pulse" / "positions.py"
SERVING_V2 = REPO_ROOT / "results" / "sku_pilot_serving_v2.json"
DECOMPOSITION = REPO_ROOT / "results" / "sku_miss_decomposition.json"
SUPERSEDED = REPO_ROOT / "results" / "sku_pilot_prereg_v4.json"
RECORD = REPO_ROOT / "results" / "sku_pilot_prereg_b2.json"

KEEP_BLOCK = "sku-b-ratification-7"
"""The one ratification block this pin KEEPS. (13) is what authorises B′; a law stripped of it
would be a law that does not contain the run being registered."""

CAP_USD = 0.40
PHASE = "skub2"
LEDGER = REPO_ROOT / "results" / "spend_skub2.json"
"""SPEC 3.17 (13)(d) for the cap, and (12)(b)'s standing rule for the three names: a cap, a ledger
path and a phase key are ONE decision and are registered together. A fresh anchor of its own — the
Dv167 trap is reading a closed phase's ledger under a new cap."""

POPULATION = 138
"""(13)(d): «one re-measurement of instrument v2 over the same 138 elements». Not the 121 v4 had
left — instrument v2 is a different instrument, and 17 answers from the old parser at the old
ceiling are not measurements of it."""

LEAVING_CLASSES = ("b", "c")
"""(13)(c): class-b and class-c pairs leave the denominator. Class a stays — those are the misses
instrument v2 exists to fix, and removing them would be marking the exam."""


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def refuse(reason: str) -> None:
    raise SystemExit(f"refused: {reason}")


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pinned_sha256(path: Path) -> str:
    """What THIS registration pins: for SPEC the law including (13), else the file as it sits.

    The registry is deliberately hashed live — (13)(b) is part of instrument v2, so B′ registers
    the amended alias table rather than reconstructing the one v4 read.
    """
    if path == SPEC:
        return hashlib.sha256(v4.registered_law(path, keep=(KEEP_BLOCK,))).hexdigest()
    return sha256_of(path)


def check_no_pair_is_pending(decomposition: dict) -> None:
    """(13)(c) derives the gold from the verdicts, so a pending verdict is a moving denominator."""
    pending = [
        row["n"]
        for row in decomposition["rows"]
        if row["verdict"] == decomposition["pending_status"]
    ]
    if pending:
        refuse(
            f"{len(pending)} missed pair(s) are still {decomposition['pending_status']}:"
            f" {pending}. SPEC 3.17 (13)(c) builds the B′ gold out of these verdicts and each of"
            " these rows can still leave the denominator, so registering now would register a"
            " denominator that moves afterwards. The team lead reads them at the B′-prep"
            " acceptance and this producer runs then."
        )


def leaving(decomposition: dict) -> set[tuple[str, str]]:
    """(post, v4-era gold key) for every pair (13)(c) takes out of the denominator."""
    return {
        (row["item"], row["gold_key"])
        for row in decomposition["rows"]
        if row["verdict"] in LEAVING_CLASSES
    }


def b_prime_gold(reference: dict, decomposition: dict, was: dict, now: dict) -> dict:
    """The B′ denominator: every reviewer name re-keyed, minus the pairs (13)(c) removes.

    ``was`` is the alias table v4 was scored under and ``now`` is today's. Each reviewer name is
    keyed under BOTH: the v4 key is what the decomposition's rows are written in and is used only
    to join, and today's key is what goes into the gold. Nothing bridges the two spaces by editing
    a string — «Rud» and «LIMO» became aliases of their own brand_ids in (13)(b), so `raw:rud`
    and `rud` are the same brand under two tables and NOT the same key, and a `raw:` prefix
    stripped to make them match would silently also match `raw:try-vedmedi` to `try-vedmedi`.
    """
    removed, matched, posts = leaving(decomposition), set(), []
    ruled_out_keys = {key for _, key in removed}
    # what the same team lead said about each (post, key) that IS a miss — a pair not in here was
    # found by the v1 instrument and was therefore never ruled on at all
    verdict_of = {(row["item"], row["gold_key"]): row["verdict"] for row in decomposition["rows"]}
    elsewhere, seen_here = [], set()
    for post in reference["posts"]:
        block = post["brands_visible"]
        names = [
            {"field": field, "written": name}
            for field in ("watchlist", "other_dairy_brands")
            for name in block[field]
        ]
        kept, dropped = [], []
        for name in names:
            key_v4 = leaflet.gold_key(name["written"], was)
            key_b2 = leaflet.gold_key(name["written"], now)
            if (post["item"], key_v4) in removed:
                matched.add((post["item"], key_v4))
                dropped.append({**name, "gold_key_v4": key_v4, "gold_key_b2": key_b2})
                continue
            if key_v4 in ruled_out_keys and (post["item"], key_v4) not in seen_here:
                # the same BRAND, ruled out of the denominator on another post and kept here.
                # (13)(c) removes class-b and class-c PAIRS, and a class only exists for a pair the
                # instrument missed — so a pair it found was never ruled on and stays. Counted and
                # reported, never acted on: which of the two readings is the law is the team lead's.
                # Split by what this pair was, because the two halves are not the same thing: a
                # FOUND pair is one v2 will very likely find again, a class-a miss is not.
                seen_here.add((post["item"], key_v4))
                elsewhere.append(
                    {
                        "item": post["item"],
                        "gold_key_v4": key_v4,
                        "gold_key": key_b2,
                        "was": verdict_of.get((post["item"], key_v4), "found by v1"),
                        **name,
                    }
                )
            if key_b2 not in kept:
                kept.append(key_b2)
        if sorted(set(leaflet.gold_key(n["written"], was) for n in names)) != sorted(
            block["gold_keys"]
        ):
            refuse(
                f"{post['item']}: re-keying the reviewer's names under the v4 alias table does not"
                " reproduce the gold_keys the reference stores — the join to the decomposition"
                " cannot be trusted"
            )
        posts.append(
            {
                "item": post["item"],
                "msg_id": post["msg_id"],
                "gold_keys_v4": block["gold_keys"],
                "gold_keys": sorted(kept),
                "removed": dropped,
            }
        )
    if matched != removed:
        refuse(
            f"{len(removed - matched)} pair(s) (13)(c) removes match no reviewer name:"
            f" {sorted(removed - matched)} — the decomposition and the reference disagree on what"
            " the gold is"
        )
    return {
        "posts": posts,
        # lists, not tuples: the in-memory record has to be the record that lands on disk, or a
        # test comparing the two is comparing a serialisation quirk
        "removed": [list(pair) for pair in sorted(removed)],
        "kept_on_a_key_ruled_out_elsewhere": elsewhere,
    }


MOVED_BY_THE_RESCOPE = ("gold", "excluded", "denominator", "reachable")
"""Every leaf of bar 1 that (13)(c) moves, enumerated LITERALLY.

The contract holds the bars' «verbatim texts and thresholds» byte-equal, and those are the law's
own words. These four are the registration's READING of the law, and all four count posts or pairs:
a gold of 41 pairs over 11 posts beside a `denominator` still saying 15 and 55 is a record that
answers the same question two ways. `excluded` is the sharpest of them — `sku_bar_verdicts.bar_one`
compares it against the reference's own empty-gold list before it scores anything.

Literal so a fifth cannot slip in behind the check below."""


def check_the_bars_did_not_move(record: dict, previous: dict) -> list[str]:
    """The bars are (6)'s words and (13) moves none of them. Only bar 1's re-scope, leaf-wise."""
    moved = []
    for name, bar in record["bars"].items():
        was = previous["bars"][name]
        for leaf in sorted(set(bar) | set(was)):
            if bar.get(leaf) != was.get(leaf):
                moved.append(f"{name}.{leaf}")
        if bar["verbatim"] != was["verbatim"] or bar["threshold"] != was["threshold"]:
            refuse(f"bar {name}'s verbatim text or threshold moved, and (13) moves neither")
    expected = sorted(f"leaflet_brand_recall.{leaf}" for leaf in MOVED_BY_THE_RESCOPE)
    if sorted(moved) != expected:
        refuse(
            f"the bars differ from v4 on {sorted(moved)} and (13)(c) re-scopes exactly {expected}."
            " Anything else is a bar nobody ratified — stop and report."
        )
    gold = record["bars"]["leaflet_brand_recall"]["gold"]
    excluded = record["bars"]["leaflet_brand_recall"]["excluded"]["posts"]
    if sorted(excluded) != sorted(gold["posts_with_an_empty_gold_set"]):
        refuse(
            "bar 1 excludes {excluded} and its gold says {gold} posts have an empty set — that"
            " equality is what sku_bar_verdicts.bar_one checks before it scores anything".format(
                excluded=len(excluded), gold=len(gold["posts_with_an_empty_gold_set"])
            )
        )
    return moved


def build(decomposition: dict, out: Path) -> dict:
    v4.check_the_bars_are_the_laws(SPEC)
    check_no_pair_is_pending(decomposition)

    reference = json.loads(REFERENCE.read_text(encoding="utf-8"))
    census = json.loads(CENSUS.read_text(encoding="utf-8"))
    pack = json.loads(PACK_MANIFEST.read_text(encoding="utf-8"))
    previous = json.loads(SUPERSEDED.read_text(encoding="utf-8"))

    was = watchlist_aliases(
        load_registry_as_pinned(
            previous["pinned_inputs"]["config/registry.yaml"], REGISTRY
        ).watchlist
    )
    now = watchlist_aliases(load_registry(REGISTRY).watchlist)
    gold = b_prime_gold(reference, decomposition, was, now)
    scoreable = [post for post in gold["posts"] if post["gold_keys"]]
    empty = [post["item"] for post in gold["posts"] if not post["gold_keys"]]
    pairs = sum(len(post["gold_keys"]) for post in scoreable)

    record = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "phase": "skub2 — the position layer re-measured under instrument v2",
        "written_by": "skub2-prep (executor, $0), docs/PROMPT-skub2-prep.md deliverable 4",
        "authority": "docs/SPEC.md amendment 3.17 (6), (9)–(12) as they stand, and (13)",
        "class": (
            "PRE-REGISTRATION, registered BESIDE results/sku_pilot_prereg_v4.json and never in"
            " place of it. Committed in its own commit before any skub2-run artifact exists; git"
            " history is the only witness to that ordering. Nothing here is a result. The bars are"
            " (6)'s words unchanged; what (13) moves is bar 1's GOLD, the instrument and the cap"
        ),
        "supersedes": {
            "record": rel(SUPERSEDED),
            "sha256": sha256_of(SUPERSEDED),
            "reason": (
                "v4 stays SEALED and stays true: its three bars are what closed the sku-b pilot by"
                " measurement, and the 121 elements it bought were extracted under instrument v1."
                " This record does not revise that verdict — it registers the ONE re-measurement"
                " 3.17 (13)(d) authorises, under an instrument the same law changes"
            ),
            "authority": "docs/SPEC.md amendment 3.17 (13), ratified 2026-08-12",
            "bars_unchanged": v4.BARS_UNCHANGED,
        },
        "attempts": {
            "verbatim": (
                "one re-measurement of instrument v2 over the same 138 elements under a B′"
                " pre-registration BESIDE v4 (bars' verbatim thresholds unchanged; gold and"
                " instrument shas move; cap $0.40), with every reading of (9)–(12) in force"
            ),
            "count": 1,
            "cap_usd": CAP_USD,
            "phase": PHASE,
            "ledger": rel(LEDGER),
            "authority": (
                "SPEC 3.17 (13)(d) for the attempt and the cap; (12)(b)'s standing rule for the"
                " three constants being one decision. A session refused at the (10)(a) gate charges"
                " this phase's ledger and never the next attempt's cap"
            ),
            "on_failure": previous["attempts"]["on_failure"],
            "on_success": v4.GREEN_GATE,
        },
        "population": {
            "elements": POPULATION,
            "reading": (
                "ALL 138, and this is a reading rather than a transcription: (11)(a) says each"
                " element is bought exactly once ACROSS THE PROGRAM, and (13)(d) says «one"
                " re-measurement of instrument v2 over the same 138 elements». A re-measurement"
                " cannot reuse the old instrument's answers — the 17 first-session pages and the"
                " 121 v4 pages were extracted at an 800-token ceiling by a parser that refused"
                " four of them. So (13)(d) supersedes (11)(a) HERE, for this registration only, and"
                " the earlier answers stay on disk as v1's measurement. See ratification_required"
            ),
            "not_a_resume": (
                "v4's `resume` block and its bought_already/17-of-138 pins describe a session that"
                " completed a population. This is not that: nothing here is carried over, and no"
                " element of the 138 is excluded because someone already paid for it"
            ),
        },
        "instruments": {
            **{
                task: previous["instruments"][task]
                for task in ("positions_post_gm4", "positions_text_gm4")
            },
            "note": (
                "UNCHANGED, and copied from v4 rather than recomputed. (13) says «no new ML"
                " mechanism is authorised»: the two registered prompt texts are byte-identical to"
                " the ones the pilot was scored against, and what moves is around them"
            ),
            "instrument_v2": {
                "parser": {"path": rel(PARSER), "sha256": sha256_of(PARSER)},
                "serving_pin": {"path": rel(SERVING_V2), "sha256": sha256_of(SERVING_V2)},
                "registry": {"path": rel(REGISTRY), "sha256": sha256_of(REGISTRY)},
                "reading": (
                    "the three halves of instrument v2, each pinned where it can actually be read:"
                    " the parser family and the warnings of (13)(a) in the module sha, the 1200"
                    " ceiling in serving pin v2 (which is what the worker's describe() is held"
                    " against), and the three Latin aliases of (13)(b) in the registry sha. The"
                    " prompts are not among them"
                ),
            },
        },
        "bars": {
            "leaflet_brand_recall": {
                **{
                    key: value
                    for key, value in previous["bars"]["leaflet_brand_recall"].items()
                    if key not in MOVED_BY_THE_RESCOPE
                },
                # the three readings that COUNT posts and pairs. Inherited from v4 they would say
                # 15 and 55 beside a gold that says 11 and 41 — and `sku_bar_verdicts.bar_one`
                # opens by comparing `excluded.posts` against the reference's own empty-gold list,
                # so v4's four would MATCH the sealed reference and wave a 15-post scoring through
                # in the v4 key space. Recomputed, so that same guard refuses instead.
                "excluded": {
                    **previous["bars"]["leaflet_brand_recall"]["excluded"],
                    "posts": empty,
                    "why_this_list_grew": (
                        f"v4 excluded {len(previous['bars']['leaflet_brand_recall']['excluded']['posts'])}"
                        f" posts and B′ excludes {len(empty)}. The four new ones each carried exactly"
                        " one gold key, all four ruled class b, so (13)(c) empties their gold and"
                        " R3's own rule — an empty gold set is a precision probe — moves them. The"
                        " rule is not new; what changed is which posts it reaches"
                    ),
                },
                "denominator": (
                    f"the {len(scoreable)} posts whose gold brand set is non-empty AFTER the (13)(c)"
                    " re-scope. Recall is computed PER POST as |extracted ∩ gold| / |gold|, over the"
                    f" union of that post's page answers, and the bar reads the MACRO MEAN of those"
                    f" {len(scoreable)} values. The micro reading over all {pairs} pairs is reported"
                    " beside it and gates nothing"
                ),
                "reachable": (
                    f"yes, measured before the run: {len(scoreable)} of 19 posts carry a non-empty"
                    f" gold set after the re-scope and {pairs} pairs sit on them"
                ),
                "gold": {
                    "derived_from": {"path": rel(REFERENCE), "sha256": sha256_of(REFERENCE)},
                    "decomposition": {
                        "path": rel(DECOMPOSITION),
                        "sha256": sha256_of(DECOMPOSITION),
                        "read_by": decomposition["read_by"],
                        "read_on": decomposition["read_on"],
                    },
                    "rule": decomposition["b_prime_denominator"]["rule"],
                    "pairs": pairs,
                    "pairs_v4": reference["gold"]["pairs"],
                    "removed": len(gold["removed"]),
                    "removed_pairs": gold["removed"],
                    "key": (
                        "the same `gold_key` on both halves, computed under the (13)(b) alias table."
                        " NOT the v4 keys: «Rud» and «LIMO» became display names of their own"
                        " brand_ids, so a name that keyed `raw:rud` under v4 keys `rud` here. The"
                        " decomposition's rows are in the v4 space and are joined in it, once, by"
                        " re-keying every reviewer name under both tables"
                    ),
                    "per_post": gold["posts"],
                    "posts_with_a_non_empty_gold_set": len(scoreable),
                    "posts_with_an_empty_gold_set": empty,
                    "posts_emptied_by_the_rescope": [
                        post["item"]
                        for post in gold["posts"]
                        if post["gold_keys_v4"] and not post["gold_keys"]
                    ],
                    "asymmetry_reported_never_gated": {
                        "n": len(gold["kept_on_a_key_ruled_out_elsewhere"]),
                        "by_what_the_pair_was": {
                            was: sum(
                                1
                                for pair in gold["kept_on_a_key_ruled_out_elsewhere"]
                                if pair["was"] == was
                            )
                            for was in sorted(
                                {pair["was"] for pair in gold["kept_on_a_key_ruled_out_elsewhere"]}
                            )
                        },
                        "pairs": gold["kept_on_a_key_ruled_out_elsewhere"],
                        "reading": (
                            "a class exists only for a pair the instrument MISSED, so (13)(c) can"
                            " only ever remove misses. Every one of these is the SAME brand on"
                            " another post, kept because the v1 instrument happened to find it —"
                            " and it stays in the B′ denominator as a pair v2 is very likely to"
                            " find again. The rescope therefore moves recall up on both sides:"
                            " guaranteed misses leave and these stay. Reported here, gating"
                            " nothing; whether a brand ruled out of scope is out of scope"
                            " EVERYWHERE is a team-lead ruling — see ratification_required B4"
                        ),
                    },
                },
            },
            "price_pair_accuracy": previous["bars"]["price_pair_accuracy"],
            "text_tier_accuracy": previous["bars"]["text_tier_accuracy"],
        },
        "ratification_required": [
            {
                "id": "B1",
                "bar": "leaflet_brand_recall",
                "question": (
                    "(13)(d) authorises a re-measurement over «the same 138 elements» and (11)(a)"
                    " says each element is bought exactly once across the program. Registered"
                    " reading: (13)(d) supersedes (11)(a) for this registration, all 138 are"
                    " re-asked, and v1's answers stay on disk as v1's measurement"
                ),
                "if_refused": (
                    "the alternative is re-asking only what instrument v2 could change, which"
                    " nobody can enumerate before the run — and a bar computed half on v1 answers"
                    " and half on v2 answers measures neither instrument"
                ),
            },
            {
                "id": "B2",
                "bar": "leaflet_brand_recall",
                "question": (
                    f"the B′ gold is {pairs} pairs, the 55 of v4 minus the"
                    f" {len(gold['removed'])} the team lead ruled class-b or class-c. Class-a"
                    " pairs STAY: they are what instrument v2 exists to fix, and removing them"
                    " would be marking the exam"
                ),
                "if_refused": "the denominator is the team lead's to set; nothing here re-judges a pair",
            },
            {
                "id": "B3",
                "bar": "leaflet_brand_recall",
                "question": (
                    "the gold keys are computed under the (13)(b) alias table, so two of them"
                    " change shape (`raw:rud` → `rud`, `raw:limo` → `limo`). The bar's threshold"
                    " and text do not move; the key SPACE does"
                ),
                "if_refused": (
                    "the alternative is scoring v2's extractions against v1's key space, where"
                    " «Рудь» resolves to `rud` and the gold says `raw:rud` — a miss by arithmetic"
                ),
            },
            {
                "id": "B4",
                "bar": "leaflet_brand_recall",
                "question": (
                    "(13)(c) removes class-b and class-c PAIRS, and a class only exists for a pair"
                    " the instrument missed — so the rescope can only ever take out misses."
                    f" {len(gold['kept_on_a_key_ruled_out_elsewhere'])} pairs the v1 instrument"
                    " FOUND carry a gold key the same team lead ruled out of the denominator on"
                    " another post, and they stay. Registered reading: the verdicts are per pair"
                    " and the executor re-judges none of them, so they stay"
                ),
                "if_refused": (
                    "the alternative reading is that a brand ruled «non-dairy watchlist item» or"
                    " «maker logo» is out of scope EVERYWHERE, which would take those pairs out"
                    " too and lower the B′ denominator further. Both readings are defensible and"
                    " they move the bar in opposite directions, which is exactly why this is a"
                    " ratification line and not an executor's choice"
                ),
            },
            {
                "id": "B5",
                "bar": "leaflet_brand_recall",
                "question": (
                    f"the rescope EMPTIES the gold of"
                    f" {len([p for p in gold['posts'] if p['gold_keys_v4'] and not p['gold_keys']])}"
                    " posts whose only gold key was a class-b pair, so they leave the recall"
                    " average and join the precision probe under R3's own rule. The macro mean is"
                    f" over {len(scoreable)} posts, not v4's 15"
                ),
                "if_refused": (
                    "keeping them in would divide by an empty denominator; R3 already rules that"
                    " an empty gold set is a precision probe, and this applies that rule rather"
                    " than writing a new one"
                ),
            },
        ],
        "pinned_inputs": {
            rel(path): pinned_sha256(path)
            for path in (SPEC, REFERENCE, PACK_MANIFEST, CENSUS, REGISTRY, LEXICON)
        }
        | {
            rel(PARSER): sha256_of(PARSER),
            rel(SERVING_V2): sha256_of(SERVING_V2),
            rel(DECOMPOSITION): sha256_of(DECOMPOSITION),
        },
        "pinned_inputs_note": (
            f"`docs/SPEC.md` is pinned as the law WITH `{KEEP_BLOCK}` in it and the six earlier"
            " ratification blocks stripped — this registration is made under (13), and a pin over a"
            " law that does not contain (13) would not be a pin on the authority for this run."
            " `config/registry.yaml` is pinned LIVE for the same reason: the aliases are part of"
            " the instrument being registered"
        ),
        "ladder": previous["ladder"],
        "not_in_scope": {
            **previous["not_in_scope"],
            "the two candidates (13) names and does not authorise": (
                "two-stage OCR and the brands_visible channel stay NAMED CANDIDATES, unbuilt."
                " (13)'s last sentence: «no new ML mechanism is authorised»"
            ),
            "the four pending pairs": (
                "#4, #9, #28 and #29 are read at the B′-prep acceptance. This record cannot exist"
                " while any of them is pending — the producer refuses — so a copy of it carrying"
                " four guesses is not a thing that can be produced by mistake"
            ),
        },
        "text_pack": {"rows": pack["rows"], "frame_rows": census["frame"]["rows"]},
    }
    check_the_bars_did_not_move(record, previous)
    record["git"] = provenance.git_state(out)
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decomposition", type=Path, default=DECOMPOSITION)
    parser.add_argument("--out", type=Path, default=RECORD)
    args = parser.parse_args(argv)

    if args.out.exists():
        refuse(
            f"{rel(args.out)} already exists. A pre-registration is the pre-run witness and a"
            " regenerated copy carries a timestamp from after the run — there is no --force here"
        )
    decomposition = json.loads(args.decomposition.read_text(encoding="utf-8"))
    record = build(decomposition, args.out)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    gold = record["bars"]["leaflet_brand_recall"]["gold"]
    print(f"wrote {rel(args.out)}  (beside {rel(SUPERSEDED)}, which stays sealed)")
    print(
        f"  bar 1 gold    {gold['pairs']} pairs over"
        f" {gold['posts_with_a_non_empty_gold_set']} posts"
        f" ({gold['pairs_v4']} - {gold['removed']} removed by (13)(c))"
    )
    print(f"  population    {record['population']['elements']} elements, cap ${CAP_USD:.2f}")
    print(
        f"  instrument    parser {record['instruments']['instrument_v2']['parser']['sha256'][:12]}…"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
