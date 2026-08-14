#!/usr/bin/env python3
"""The 5c2-validate sitting's returns — SPEC 3.18 (6), the half of the sitting that is a record.

The pack went out with every `findings` slot empty and the sitting filled them. This writes what
came back into `results/validate_5c2_returns.json`, which is the committed copy of an evening
nobody will sit through twice — the team lead's ruling at the validate-prep acceptance was that the
returns are a NEW record and the pack's skeleton is never written over.

**What came back.** The leaflet half — 6 posts and the 36 position rows printed under them —
RATIFIED, with the operator's own words kept as data and untranslated. The comment half — 5 of 5 —
RATIFIED. Nothing disputed, so no ORDER of the REVIEW class (3.16 (1)) was issued. The sitting
produced exactly one ruling, and it is law rather than a finding: amendment 3.19, referenced here
and never restated, because a record that paraphrased the SPEC would become a second place to read
the law from.

**Nothing here is measured and nothing is re-scored.** 3.18 (6)(c) puts these verdicts in the
REVIEW class: they are the operator's reactions, they become watchlist / lexicon / prompt-revision
orders, and they never move a bar or a number. What this producer does is check that the verdicts
answer the pack that was actually shown, and refuse otherwise:

* the pack's sha256 is not the one the sitting read — the verdicts are about another draw;
* the pack's `findings` groups or their sizes are not what the sitting ruled on;
* a slot the pack PRINTED has no verdict, or a slot exists for a row the pack never printed;
* the shipped skeleton is not empty — somebody has already written into the pack;
* the amendment the sitting produced is not in `docs/SPEC.md`.

    PYTHONPATH=src python3 scripts/write_validate_returns.py
"""

import argparse
import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

PACK = REPO_ROOT / "results" / "validate_5c2_pack.json"
RECORD = REPO_ROOT / "results" / "validate_5c2_returns.json"
CONTRACT = REPO_ROOT / "docs" / "PROMPT-5c2-close.md"
SPEC = REPO_ROOT / "docs" / "SPEC.md"

PACK_SHA256 = "2fad5339ecb721d963a1cf2ca6cb091aabea473b706301e656b6e0bd15afc12a"
"""The pack the operator read, by its bytes. A returns record whose pack moved under it is a set of
verdicts about a draw nobody saw — and this pack is drawn under a seed, so a redraw is silent."""

HELD = "2026-08-14"

SITTING = {
    "leaflet_posts": {
        "n": 6,
        "verdict": "ratified",
        "half": "leaflet",
        "what": "the six leaflet posts drawn 4 + 2 across the yielded / yielded-none strata",
    },
    "positions": {
        "n": 36,
        "verdict": "ratified",
        "half": "leaflet",
        "what": "every position row the pack printed under those six posts, field by field",
    },
    "comments": {
        "n": 5,
        "verdict": "ratified",
        "half": "comment",
        "what": "one comment from each of the five channels with the most rows in the window",
    },
}
"""The verdicts as relayed, per group, with the SIZE each was ruled on.

The size is the part that does work. The operator ratified a half, not a list of ids, so a pack
carrying a 37th position row would be answered wholesale by a record that only knew the words
«ratified» — and that row would never have been on the table. The counts are the sitting's own, so
a pack that does not match them is refused rather than covered."""

DISPUTED: dict[str, str] = {}
"""Slot id → the operator's note, for anything he did NOT ratify. Empty: the sitting disputed
nothing. It is a map rather than a flag because the sitting could have disputed one row of one
post, and a returns record that could only say «the half was fine» would have nowhere to put it."""

ORDERS: tuple[str, ...] = ()
"""The REVIEW-class orders the sitting issued (3.18 (6)(c) → 3.16 (1)). None: nothing was disputed,
and an order with no dispute behind it would be this record inventing work."""

VERBATIM = "распознавание SKU идеальное"
"""The operator's words on the leaflet half, in Russian and untranslated — this is DATA, not prose.

Checked back against :data:`CONTRACT` before it is written, with whitespace normalised, because the
line wraps there. A quote nobody grepped is a quote somebody remembered."""

VERBATIM_SOURCE = "docs/PROMPT-5c2-close.md — the team lead relaying the sitting"

RULING = {
    "amendment": "3.19",
    "where": "docs/SPEC.md, inside the marked block `amendment-3.19`",
    "answers": "Dv324 — 1 361 of the 5 075 bought comment rows reached the model with empty text",
    "reference_not_restatement": (
        "the clauses are not copied here. A record that paraphrased them would become a second"
        " place to read the law from, and the two would drift on the first correction"
    ),
    "not_a_finding": (
        "3.18 (6)(c) makes the sitting's VERDICTS review-class findings. This is the other thing a"
        " sitting can produce — a ruling that becomes law — and it is filed as law"
    ),
}

MARKER = "<!-- amendment-3.19 begin"


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def refuse(reason: str) -> None:
    raise SystemExit(f"refused: {reason}")


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check_the_pack_is_the_one_that_was_read(path: Path) -> str:
    found = sha256_of(path)
    if found != PACK_SHA256:
        refuse(
            f"{rel(path)} hashes {found} and the sitting read {PACK_SHA256}. The pack is DRAWN"
            " under a seed, so a redraw looks like the same file — these verdicts would be about"
            " rows nobody saw. Take it to the team lead; do not re-pin this record"
        )
    return found


def printed_slots(pack: dict) -> dict[str, list[str]]:
    """What the pack actually PRINTED, rebuilt from the shown rows rather than from its skeleton.

    The skeleton and the printed rows are written by the same producer one line apart, which is
    exactly why they are compared: a slot with no row is a verdict on something the operator never
    saw, and a row with no slot is a row he had no way to rule on. Neither is visible from inside
    the skeleton alone.
    """
    return {
        "leaflet_posts": [block["post"] for block in pack["leaflet_posts"]],
        "positions": [
            row["row_id"] for block in pack["leaflet_posts"] for row in block["positions"]
        ],
        "comments": [block["comment"] for block in pack["comments"]],
    }


def resolve(pack: dict) -> dict:
    """Every slot the pack carries, with the verdict the sitting gave its group — or a refusal."""
    findings = pack["findings"]
    groups = {name: slots for name, slots in findings.items() if name != "verdicts"}
    if set(groups) != set(SITTING):
        refuse(
            f"the pack's findings groups are {sorted(groups)} and the sitting ruled on"
            f" {sorted(SITTING)}. A group nobody ruled on cannot be resolved by this record"
        )

    shown = printed_slots(pack)
    resolved = {}
    for name, slots in groups.items():
        ruled = SITTING[name]
        if len(slots) != ruled["n"]:
            refuse(
                f"the pack carries {len(slots)} `{name}` slots and the sitting ruled on"
                f" {ruled['n']}. The operator ratified a HALF, not a list of ids, and a slot that"
                " was not in front of him is not covered by that"
            )
        if sorted(slots) != sorted(shown[name]):
            refuse(
                f"the pack's `{name}` slots are not the `{name}` rows it printed —"
                f" {sorted(set(slots) ^ set(shown[name]))} is in one and not the other"
            )
        if ruled["verdict"] not in findings["verdicts"]:
            refuse(
                f"the sitting's verdict {ruled['verdict']!r} for `{name}` is not one of the pack's"
                f" own {findings['verdicts']} — a verdict form invented here means something"
                " different from the one the pack put on the table"
            )
        filled = sorted(key for key, slot in slots.items() if slot["verdict"] or slot["note"])
        if filled:
            refuse(
                f"the pack's `{name}` slots {filled} are already filled in. The pack ships every"
                " slot EMPTY and is never written over — the returns live in this record"
            )
        resolved[name] = {
            key: {
                "verdict": "disputed" if key in DISPUTED else ruled["verdict"],
                "note": DISPUTED.get(key, ""),
            }
            for key in sorted(slots)
        }

    unaccounted = sorted(
        key for slots in resolved.values() for key, slot in slots.items() if not slot["verdict"]
    )
    if unaccounted:
        refuse(f"{len(unaccounted)} slots came out with no verdict: {unaccounted}")
    stray = sorted(key for key in DISPUTED if not any(key in slots for slots in resolved.values()))
    if stray:
        refuse(f"the sitting disputed {stray}, which the pack does not carry")
    return resolved


def check_the_quote_is_the_contracts(text: str) -> None:
    """The verbatim, grepped back. Whitespace is normalised because the line wraps in the source."""
    flat = " ".join(text.split())
    if " ".join(VERBATIM.split()) not in flat:
        refuse(
            f"{rel(CONTRACT)} does not carry {VERBATIM!r}. The operator's words are DATA in this"
            " record and a quote nobody can grep is a quote somebody remembered"
        )


def check_the_ruling_is_law(text: str) -> None:
    if MARKER not in text:
        refuse(
            f"{rel(SPEC)} carries no `{MARKER}` block. This record REFERENCES amendment 3.19"
            " rather than restating it, so a reference to nothing would leave the sitting's one"
            " ruling written down nowhere"
        )


def tally(resolved: dict) -> dict:
    counts: dict[str, int] = {}
    for slots in resolved.values():
        for slot in slots.values():
            counts[slot["verdict"]] = counts.get(slot["verdict"], 0) + 1
    return dict(sorted(counts.items()))


def producer() -> dict:
    return {
        "script": rel(Path(__file__)),
        "sha256": sha256_of(Path(__file__)),
        "why": "no git block: `git status --porcelain` is a fact about the tree, not the sitting",
        "borrows": {},
        "borrows_note": (
            "this producer imports no module of this repo. It reads three files and writes what the"
            " sitting said about one of them; there is no house function whose bytes could change a"
            " field here, and an empty map says that rather than hiding it"
        ),
    }


def build(pack_path: Path) -> dict:
    pack_sha = check_the_pack_is_the_one_that_was_read(pack_path)
    pack = load(pack_path)
    check_the_quote_is_the_contracts(CONTRACT.read_text(encoding="utf-8"))
    check_the_ruling_is_law(SPEC.read_text(encoding="utf-8"))
    resolved = resolve(pack)
    counts = tally(resolved)

    return {
        "phase": "5c2-validate — the operator sitting's returns",
        "class": (
            "RETURNS. The operator's reactions to a sealed pack. SPEC 3.18 (6)(c) files them in the"
            " REVIEW class of 3.16 (1): they become watchlist, lexicon or prompt-revision ORDERS,"
            " never re-scored numbers and never a moved bar"
        ),
        "contract": "docs/PROMPT-5c2-close.md deliverable 1; docs/SPEC.md amendment 3.18 (6)",
        "answers": {
            "pack": rel(pack_path),
            "sha256": pack_sha,
            "seed": pack["seed"],
            "why_the_sha_is_pinned": (
                "the pack is DRAWN under a seed, so a redraw produces the same filename and a"
                " different set of rows. Without the sha these verdicts could be read as answering"
                " a draw the operator never saw"
            ),
        },
        "sitting": {
            "held": HELD,
            "mode": (
                "asynchronous — the operator read results/validate_5c2_pack.html and his verdicts"
                " were relayed to this executor through the team lead"
            ),
            "operator_minutes": None,
            "operator_minutes_note": (
                "no actual was relayed and nothing on disk carries one, so the field is null rather"
                " than filled. docs/STATUS.md named ~45 minutes BEFORE the sitting; that is a plan"
                " and a plan is not a measurement"
            ),
            "verdicts_are_the_operators": (
                "the executor scores nothing here (SPEC §10). Every verdict below is the operator's"
                " own, applied to the group he ruled on"
            ),
        },
        "halves": {
            "leaflet": {
                "verdict": "ratified",
                "posts": SITTING["leaflet_posts"]["n"],
                "positions": SITTING["positions"]["n"],
                "verbatim": VERBATIM,
                "verbatim_language": "ru",
                "verbatim_source": VERBATIM_SOURCE,
                "verbatim_note": (
                    "kept in the operator's own words and untranslated: it is the DATUM this half"
                    " produced, and a translation of it would be this executor's sentence"
                ),
            },
            "comment": {
                "verdict": "ratified",
                "comments": SITTING["comments"]["n"],
                "of": SITTING["comments"]["n"],
            },
        },
        "totals": {
            "slots": sum(len(slots) for slots in resolved.values()),
            "tally": counts,
            "disputed": len(DISPUTED),
            "orders_issued": len(ORDERS),
            "orders": list(ORDERS),
            "orders_note": (
                "an ORDER follows a dispute. Nothing was disputed, so the sitting issued none —"
                " reported as zero rather than left out, because an absent field reads as unasked"
            ),
        },
        "ruling": RULING,
        "resolved": resolved,
        "resolved_note": (
            "every slot the pack printed, with the verdict of the group it belongs to. Kept row by"
            " row rather than summarised: a half that was ratified wholesale still has to name"
            " WHICH rows were on the table, or a later reader cannot tell what was examined"
        ),
        "refuses_when": [
            "the pack's sha256 is not the one the sitting read",
            "its findings groups or their sizes are not what the sitting ruled on",
            "a printed row has no slot, or a slot has no printed row",
            "the pack's skeleton is already filled in",
            "the verbatim is not in the contract, or amendment 3.19 is not in the SPEC",
        ],
        "producer": producer(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, default=PACK)
    parser.add_argument("--out", type=Path, default=RECORD)
    args = parser.parse_args(argv)

    record = build(args.pack)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"{rel(args.pack)} -> {rel(args.out)}")
    print(f"  pack sha256 {record['answers']['sha256'][:16]}… (seed {record['answers']['seed']})")
    for name, ruled in SITTING.items():
        print(f"  {name:<14} {ruled['n']:>3} slots  ==> {ruled['verdict']}")
    totals = record["totals"]
    print(
        f"  {'TOTAL':<14} {totals['slots']:>3} slots  {totals['tally']}"
        f"  · disputed {totals['disputed']} · orders {totals['orders_issued']}"
    )
    print(f"\nverbatim (leaflet half): «{VERBATIM}» — {VERBATIM_SOURCE}")
    print(f"ruling: amendment {RULING['amendment']} — {RULING['answers']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
