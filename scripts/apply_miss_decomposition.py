#!/usr/bin/env python3
"""Bar 1: the team lead's decomposition of the 29 missed gold pairs, applied to the pack. ($0)

Deliverable 1 of `docs/PROMPT-skub2-prep.md`, and the evidence SPEC 3.17 (13) was ratified on.
`results/sku_miss_pack.md` laid 29 rows on the table with an empty verdict column; the team lead
read the page images and dictated 25 of them, leaving four for the B′-prep acceptance. The four
came back at that acceptance as SPEC 3.17 (14)(a) — all class b, each with the pages that were
read — and `docs/PROMPT-skub2-fix.md` is where they are dictated. This file applies both
dictations and derives no verdict of its own — SPEC §10 runs both ways.

What it guards, in the order a defect would arrive:

- **the pack is the one that was read.** Both halves are pinned by sha: the JSON this file joins
  against and the MARKDOWN the team lead actually had open. A pack rebuilt between the read and the
  transcription would move rows under their numbers.
- **every row ruled on exactly once.** 25 dictated plus 4 pending must cover 1..29 with no gap and
  no row twice, and the counts are the contract's own (`a=11 · b=12 · c=2 · pending=4`),
  transcribed — never computed from the table they check.
- **the mechanism agrees with the instrument's own record.** A row the read tags `refusal:*` has to
  sit on a post whose refused page recorded THAT refusal: `-50%*` for `asterisk`, the truncated
  reply's `malformed JSON` for `token-ceiling`, `6х100 г` for `multipack`. This is the one check
  that is not a transcription — the team lead read the images and the extractor wrote the reason,
  and a numbering that slipped between them fails here rather than downstream in the B′ gold.
- **the alias gap is evidenced.** The row tagged `alias:latin-form` has to sit on a post where the
  instrument DID extract something no gold key matched; a row with nothing unmatched on it cannot
  be an alias gap.
- **a page the read names was a page that could be read.** (14)(a)'s four verdicts each cite page
  numbers («fish p2, tea p3 …»), and those pages have to exist on that post and not be among the
  ones the extractor refused. A verdict citing a refused page is row 14's `by-pattern` caveat
  wearing the words of a full read.

    PYTHONPATH=src python3 scripts/apply_miss_decomposition.py

Writes `results/sku_miss_decomposition.json`. `scripts/write_sku_prereg_b2.py` reads it for the B′
gold and refuses while any pair is still `PENDING_TEAM_LEAD`. Nothing is pending since (14)(a).
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from market_pulse import provenance  # noqa: E402

PACK = REPO_ROOT / "results" / "sku_miss_pack.json"
SHEET = REPO_ROOT / "results" / "sku_miss_pack.md"
OUT = REPO_ROOT / "results" / "sku_miss_decomposition.json"

CONTRACT = (
    "docs/PROMPT-skub2-prep.md — deliverable 1, the decomposition verdicts applied;"
    " docs/PROMPT-skub2-fix.md — step 2, the last four verdicts of SPEC 3.17 (14)(a)"
)
READ_BY = "the team lead"
READ_ON = "2026-08-12"
READ_SCOPE = "the 29 missed pairs of results/sku_miss_pack.md against the sent page images"

PACK_SHA = "e02053ecdde1eccbc92ababd372f65c3ca6963b5d080e2ee06739a704f32e567"
SHEET_SHA = "3eabfeae00e47d246398d722bec173d0f498035f58cae111bd61763bdec73ef4"
"""The two halves of the pack as the read had them (commit `0001cd9`). The sheet is pinned as well
as the record: the numbers 1..29 the dictation speaks in are printed in the MARKDOWN, so it is the
markdown that has to be unmoved for a row number to mean what the team lead meant by it."""

DICTATED = (
    (1, "a", "refusal:asterisk"),
    (2, "a", "alias:latin-form"),
    (3, "b", "maker-logo"),
    (4, "b", "non-dairy watchlist item"),
    (5, "b", "non-dairy watchlist item"),
    (6, "b", "SKU-name-vs-TM"),
    (7, "b", "SKU-name-vs-TM"),
    (8, "c", "gold-key artifact — brand was found"),
    (9, "b", "non-dairy watchlist item"),
    (10, "a", "refusal:token-ceiling"),
    (11, "a", "refusal:token-ceiling"),
    (12, "a", "refusal:token-ceiling"),
    (13, "b", "two-brands-one-box"),
    (14, "b", "non-dairy, by-pattern"),
    (15, "a", "refusal:token-ceiling"),
    (16, "a", "refusal:token-ceiling"),
    (17, "b", "non-dairy watchlist item"),
    (18, "b", "non-dairy watchlist item"),
    (19, "b", "non-dairy watchlist item"),
    (20, "a", "refusal:multipack"),
    (21, "c", "dairy-adjacent, reviewer's own caveat"),
    (22, "a", "refusal:multipack"),
    (23, "b", "non-dairy"),
    (24, "a", "refusal:multipack"),
    (25, "a", "refusal:asterisk"),
    (26, "b", "maker-logo"),
    (27, "b", "non-dairy watchlist item"),
    (28, "b", "non-dairy watchlist item"),
    (29, "b", "non-dairy watchlist item"),
)
"""Two chat messages, transcribed row for row and re-sorted by `n` only: `docs/PROMPT-skub2-prep.md`
dictated 25 and `docs/PROMPT-skub2-fix.md` — SPEC 3.17 (14)(a) — the last four.

`(row number on the sheet, class, mechanism)`. The mechanisms are the team lead's words: `14` is
ruled "by-pattern" because its page came back refused and could not be read, and that caveat is
carried rather than tidied away — it is the difference between a verdict from an image and a
verdict from the four rows beside it.

The four that came last wear the SAME mechanism string as the five `non-dairy watchlist item` rows
of the first read, deliberately: what each of them saw is in :data:`PAGE_READS`, and a per-row
mechanism would have turned one count of nine into nine counts of one."""

PAGE_READS = {
    4: (
        (2, 3, 4, 5, 6),
        "fish p2, tea p3, zefir p4, oil p5, pate p6 — every page read",
    ),
    9: ((1, 5), "mayonnaise p1, cereals p5"),
    28: ((2, 3, 5), "crab sticks/dough p2, drink p3, sweets p5"),
    29: ((2,), "dumplings p2, with price boxes"),
}
"""What the team lead saw on each of (14)(a)'s four, page by page, verbatim from the contract.

Kept beside the mechanism rather than inside it. The four rows the first read deferred are the four
the second read had to justify hardest — the guess they were left open against was «three of these
are `svoia-liniia`, rule them like the other two» — so the pages are the evidence that the verdict
came from the images. :func:`check_the_page_reads_land_on_readable_pages` holds them against the
pack: a page number that is not on that post, or that came back refused, is a claim the images
cannot carry."""

PENDING: tuple[int, ...] = ()
"""Empty since SPEC 3.17 (14)(a). It was `(4, 9, 28, 29)` — three `svoia-liniia` rows and a
`try-vedmedi`, deferred because they were NOT inferable from the five `svoia-liniia` rows that were
ruled. The machinery stays: a row named here is deferred rather than guessed, `pending` is one of
the contract's checksums, and `write_sku_prereg_b2.py` refuses while the tuple is non-empty."""

PENDING_STATUS = "PENDING_TEAM_LEAD"

EXPECTED = {"a": 11, "b": 16, "c": 2, "pending": 0, "rows": 29}
"""The contract's own checksum line — `docs/PROMPT-skub2-fix.md`'s «a=11 · b=16 · c=2 · pending=0,
total 29» — and the pack's row count, transcribed. A checksum computed from `DICTATED` would agree
with every typo in it. The first read's line was «a=11 · b=12 · c=2 · pending=4» and the four that
moved are exactly the four that were pending."""

REFUSAL_REASON = {
    "refusal:asterisk": "printed discount '-50%*' is not a percentage",
    "refusal:token-ceiling": "malformed JSON",
    "refusal:multipack": "size '6х100 г' is a multipack — a pack count is not a size",
}
"""What the extractor wrote on the page each `refusal:*` row blames, verbatim from the record. The
team lead named the mechanism from the image; this is the instrument's own account of the same
page, and the two have to be the same page."""

ALIAS_MECHANISM = "alias:latin-form"

B_PRIME_RULE = (
    "SPEC 3.17 (13)(c) — the B′ gold is the dairy positions carrying a price box on the sent"
    " pages: class-b and class-c pairs leave the denominator, class-a pairs and the 26 found stay."
    " 3.17 (14)(b) fixes the grain: a class is a fact about ONE (post, brand) pair and never about"
    " the brand everywhere, so a brand ruled non-dairy on one post stays gold where it sits on a"
    " dairy position"
)


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(REPO_ROOT)) if resolved.is_relative_to(REPO_ROOT) else str(path)


def refuse(reason: str) -> None:
    raise SystemExit(f"refused: {reason}")


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_the_pack_is_the_one_that_was_read(pack: dict, pack_sha: str, sheet_sha: str) -> None:
    """Both halves by sha, and the pack's own checksums — the read speaks in ITS row numbers."""
    if pack_sha != PACK_SHA:
        refuse(
            f"{rel(PACK)} hashes {pack_sha[:16]}… and the read was taken against {PACK_SHA[:16]}…"
            " — the rows the dictation numbers are not these rows"
        )
    if sheet_sha != SHEET_SHA:
        refuse(
            f"{rel(SHEET)} hashes {sheet_sha[:16]}… and the read was taken against"
            f" {SHEET_SHA[:16]}… — the sheet the team lead had open has moved"
        )
    if pack["checksums"] != {"posts": 15, "missed": EXPECTED["rows"], "found": 26}:
        refuse(f"the pack decomposes a different bar: {pack['checksums']}")


def join(pack: dict) -> dict[int, dict]:
    """Row number → the pack's own row. Refuses a numbering that is not 1..29 exactly once."""
    rows = {row["n"]: row for row in pack["missed"]}
    if sorted(rows) != list(range(1, EXPECTED["rows"] + 1)):
        refuse(f"the pack's missed rows are numbered {sorted(rows)}")
    return rows


def rule(dictated, pending, rows: dict[int, dict], classes: set[str]) -> list[dict]:
    """The dictation joined to the pack's rows, or a refusal naming the mismatch."""
    claimed: dict[int, str] = {}
    out = []
    for n, verdict, mechanism in list(dictated) + [(n, PENDING_STATUS, None) for n in pending]:
        if n not in rows:
            refuse(f"row {n} was ruled on and the pack has no such row")
        if n in claimed:
            refuse(f"row {n} is ruled on twice: {claimed[n]} and {verdict}")
        claimed[n] = verdict
        if verdict != PENDING_STATUS and verdict not in classes:
            refuse(f"row {n}: class {verdict!r} is not one of {sorted(classes)}")
        row = rows[n]
        out.append(
            {
                "n": n,
                "item": row["item"],
                "msg_id": row["msg_id"],
                "gold_key": row["gold_key"],
                "reading_as": row["registry_display_names"]
                or [name["written"] for name in row["written_by_the_reviewer"]],
                "verdict": verdict,
                "mechanism": mechanism,
                "unreadable_pages": row["unreadable_pages"],
                "unmatched_extractions_on_this_post": row["unmatched_extractions_on_this_post"],
                **({"pages": row["pages"]} if verdict == PENDING_STATUS else {}),
                **(
                    {"pages_read": {"pages": list(PAGE_READS[n][0]), "saw": PAGE_READS[n][1]}}
                    if n in PAGE_READS and verdict != PENDING_STATUS
                    else {}
                ),
            }
        )
    missing = sorted(set(rows) - set(claimed))
    if missing:
        refuse(f"{len(missing)} pack row(s) nobody ruled on and nobody deferred: {missing}")
    return sorted(out, key=lambda row: row["n"])


def check_the_mechanism_is_the_one_the_instrument_recorded(ruled: list[dict]) -> int:
    """The one non-transcription check: a named refusal against the page that refused."""
    checked = 0
    for row in ruled:
        mechanism = row["mechanism"]
        if mechanism in REFUSAL_REASON:
            reasons = {page["reason"] for page in row["unreadable_pages"]}
            if reasons != {REFUSAL_REASON[mechanism]}:
                refuse(
                    f"row {row['n']} ({row['msg_id']}) is ruled {mechanism} and its post's refused"
                    f" page(s) recorded {sorted(reasons)}"
                )
            checked += 1
        elif mechanism == ALIAS_MECHANISM:
            if not row["unmatched_extractions_on_this_post"]:
                refuse(
                    f"row {row['n']} ({row['msg_id']}) is ruled an alias gap and the instrument"
                    " extracted nothing unmatched on that post"
                )
            checked += 1
        elif mechanism is not None and mechanism.startswith("refusal:"):
            refuse(f"row {row['n']}: {mechanism!r} is a refusal this file has no reason string for")
    return checked


def check_the_page_reads_land_on_readable_pages(ruled: list[dict], rows: dict[int, dict]) -> int:
    """SPEC 3.17 (14)(a) cites page numbers, and a cited page has to be one that could be read.

    The second non-transcription check, and it exists for the same reason the first one does. These
    four verdicts were deferred precisely because the rows beside them were not evidence, so «fish
    p2» is the claim that carries them — and a page number that is not on that post, or that the
    extractor returned as unreadable, means the verdict came from somewhere other than the image it
    names. That is row 14's `by-pattern` caveat, and row 14 says so out loud.
    """
    unruled = sorted(set(PAGE_READS) - {row["n"] for row in ruled})
    if unruled:
        refuse(f"PAGE_READS names row(s) the table does not rule on: {unruled}")
    deferred = sorted(
        set(PAGE_READS) & {row["n"] for row in ruled if row["verdict"] == PENDING_STATUS}
    )
    if deferred:
        refuse(
            f"row(s) {deferred} are {PENDING_STATUS} and cite the pages they were read on — a row"
            " nobody has ruled on cannot carry a read"
        )
    checked = 0
    for row in ruled:
        if "pages_read" not in row:
            continue
        packed = rows[row["n"]]
        sent = {page["page"] for page in packed["pages"]}
        refused = {page["page"] for page in packed["unreadable_pages"]}
        named = set(row["pages_read"]["pages"])
        if not named <= sent:
            refuse(
                f"row {row['n']} ({row['msg_id']}) cites page(s) {sorted(named - sent)} and that"
                f" post has {sorted(sent)}"
            )
        if named & refused:
            refuse(
                f"row {row['n']} ({row['msg_id']}) cites page(s) {sorted(named & refused)} the"
                " extractor returned as unreadable — that is a by-pattern verdict, not a page read"
            )
        checked += 1
    return checked


def checksums(ruled: list[dict], expected: dict) -> dict:
    """The team lead's stated counts against the joined table. Every miss is a refusal."""
    found = {name: sum(1 for row in ruled if row["verdict"] == name) for name in ("a", "b", "c")}
    found["pending"] = sum(1 for row in ruled if row["verdict"] == PENDING_STATUS)
    found["rows"] = len(ruled)
    for what, value in expected.items():
        if found[what] != value:
            refuse(f"the read states {what} = {value} and the table joins to {found[what]}")
    return found


def by_mechanism(ruled: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in ruled:
        name = row["mechanism"] or PENDING_STATUS
        counts[name] = counts.get(name, 0) + 1
    return dict(sorted(counts.items(), key=lambda pair: (-pair[1], pair[0])))


def b_prime(pack: dict, sums: dict) -> dict:
    """What (13)(c) removes from bar 1's denominator, and what it cannot decide yet."""
    gold = pack["checksums"]["found"] + pack["checksums"]["missed"]
    removed = sums["b"] + sums["c"]
    return {
        "rule": B_PRIME_RULE,
        "bar_1_gold_pairs": gold,
        "removed_so_far": removed,
        "removed_by_class": {"b": sums["b"], "c": sums["c"]},
        "remaining_if_no_pending_pair_leaves": gold - removed,
        "pending": sums["pending"],
        "final": None if sums["pending"] else gold - removed,
        "note": (
            "`final` is null while ANY pair is PENDING_TEAM_LEAD — each one can still leave the"
            " denominator, so the B′ gold is not a number yet — and the producer of"
            " results/sku_pilot_prereg_b2.json refuses on this field rather than guessing it. It"
            " did refuse, for one contract: the first read left four pending and SPEC 3.17 (14)(a)"
            " ruled all four class b. `remaining_if_no_pending_pair_leaves` therefore equals"
            " `final` now, and it is kept because it is what the field meant while they stood"
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, default=PACK)
    parser.add_argument("--sheet", type=Path, default=SHEET)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)

    pack = json.loads(args.pack.read_text(encoding="utf-8"))
    pack_sha, sheet_sha = sha256_of(args.pack), sha256_of(args.sheet)

    check_the_pack_is_the_one_that_was_read(pack, pack_sha, sheet_sha)
    rows = join(pack)
    ruled = rule(DICTATED, PENDING, rows, set(pack["classes"]))
    evidenced = check_the_mechanism_is_the_one_the_instrument_recorded(ruled)
    pages_checked = check_the_page_reads_land_on_readable_pages(ruled, rows)
    sums = checksums(ruled, EXPECTED)

    out = {
        "phase": "sku-b — bar 1's 29 misses, decomposed by the team lead's read",
        "contract": CONTRACT,
        "class": (
            "TRANSCRIPTION. Every verdict here was read by the team lead against the page images;"
            " this file joins the dictation to the pack's rows and refuses anything that does not"
            " land exactly once. No verdict is derived, corrected or inferred. The four rows the"
            f" first read left {PENDING_STATUS} were never guessed from the rows beside them: they"
            " were deferred, the producer of the B′ registration refused while they stood, and"
            " they came back as SPEC 3.17 (14)(a) with the pages each verdict was read on"
        ),
        "authority": (
            "SPEC §10 — the executor never scores its own sample; SPEC 3.17 (13), ratified on this"
            " read, and 3.17 (14)(a), which closes it. Read by"
            f" {READ_BY} on {READ_ON}, {READ_SCOPE}"
        ),
        "read_by": READ_BY,
        "read_on": READ_ON,
        "read_scope": READ_SCOPE,
        "pack": {"path": rel(args.pack), "sha256": pack_sha},
        "sheet": {"path": rel(args.sheet), "sha256": sheet_sha},
        "classes": pack["classes"],
        "pending_status": PENDING_STATUS,
        "pending_rows": list(PENDING),
        "counts": sums,
        "expected": EXPECTED,
        "expected_source": (
            "docs/PROMPT-skub2-fix.md — «a=11 · b=16 · c=2 · pending=0», transcribed and not"
            " computed from the rows. It supersedes docs/PROMPT-skub2-prep.md's «a=11 · b=12 ·"
            " c=2 · pending=4» by moving exactly the four rows that were pending"
        ),
        "by_mechanism": by_mechanism(ruled),
        "mechanism_evidence": {
            "checked": evidenced,
            "refusal_reasons": REFUSAL_REASON,
            "page_reads_checked": pages_checked,
            "page_reads_note": (
                "SPEC 3.17 (14)(a)'s four verdicts each cite the pages they were read on, and each"
                " cited page was checked against the pack: it is a page of that post and the"
                " extractor did not return it as unreadable. What is ON the page is still only the"
                " image's to say"
            ),
            "note": (
                "each refusal:* row was checked against the reason the extractor recorded on its"
                " post's refused page, and the alias:latin-form row against that post's unmatched"
                " extractions. The classes themselves are the team lead's and are not checkable"
                " from here — only the images can say whether a brand carried a price box"
            ),
        },
        "b_prime_denominator": b_prime(pack, sums),
        "rows": ruled,
    }
    out["git"] = provenance.git_state(args.out)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"{rel(args.pack)} — {sums['rows']} missed pairs, each ruled on or deferred exactly once")
    print(
        f"  a {sums['a']} · b {sums['b']} · c {sums['c']} · {PENDING_STATUS.lower()}"
        f" {sums['pending']}"
        + (f" ({', '.join('#' + str(n) for n in PENDING)})" if PENDING else "")
    )
    print(f"  {evidenced} mechanism(s) checked against the instrument's own refusal reasons")
    print(f"  {pages_checked} page-read citation(s) checked against the pages that could be read")
    for name, count in out["by_mechanism"].items():
        print(f"    {count:2d}  {name}")
    print(f"wrote {rel(args.out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
