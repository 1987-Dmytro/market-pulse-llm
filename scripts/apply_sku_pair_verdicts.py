#!/usr/bin/env python3
"""Bar 2: the team lead's read of the 61 price pairs, transcribed onto the dump's own rows. ($0)

SPEC §10 says the executor never scores its own sample, so bar 2 was written with a denominator and
no value and waited. The read is done — `docs/PROMPT-sku-b-close.md`, 2026-08-12, all 61 pairs
against all 22 page images — and this file applies it. It does not derive a single verdict: the
table below is the team lead's dictation, and the only thing this script decides is whether the
dictation is legal to write.

What it guards, in the order a defect would arrive:

- **the dump is the sealed one.** Its sha256 has to be the one the run record pins, or the pairs
  being adjudicated are not the pairs that were bought.
- **every dump row matched exactly once.** A key is `(file, price_promo, price_old)` and `n` is how
  many dump rows carry it — duplicates share one physical price box and therefore one verdict. A
  dictated key no row carries, a row no key covers, an `n` that disagrees with the dump, or a file
  suffix that matches two different pages: each stops the run by name.
- **the counts the team lead stated, not the counts this file computes.** `EXPECTED` is transcribed
  from the contract's own checksum line, so a typo in `DICTATED` breaks it rather than becoming
  truth. Deriving the expectation from the table would make the check circular and worthless.
- **transcription, not interpretation.** A `wrong` verdict must carry the `printed_old` the page
  actually prints AND it must differ from the dump's old price; a `correct` verdict must carry none
  (the dump's old price IS the printed one, and the record fills it in). Flipping one correct row
  and one wrong row keeps 20/41 intact — the printed_old rule is the only structural guard that
  sees it.

    PYTHONPATH=src python3 scripts/apply_sku_pair_verdicts.py

Writes `results/sku_b_pair_verdicts.json`, which `scripts/sku_bar_verdicts.py` consumes to score
bar 2. Nothing else on disk is touched: the dump, the run record and the registration are immutable.

A second read exists — B′'s 80 pairs, `scripts/apply_sku_pair_verdicts_skub2.py`. It carries its own
dictation and reaches the guards above through :class:`Read` rather than copying them: two matchers
would be two rules, and the one that is not exercised daily is the one that rots.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import NamedTuple

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from market_pulse import provenance  # noqa: E402

RECORD = REPO_ROOT / "results" / "sku_b_positions_v4.json"
OUT = REPO_ROOT / "results" / "sku_b_pair_verdicts.json"

CONTRACT = "docs/PROMPT-sku-b-close.md — the team lead's verdicts table"
READ_BY = "the team lead"
READ_ON = "2026-08-12"
READ_SCOPE = "all 61 pairs against all 22 page images"

DICTATED = (
    ("4341.jpg", 37.9, 75.9, 1, "correct", None),
    ("4341.jpg", 131.5, 264.5, 1, "wrong", 264.90),
    ("4343.jpg", 17.9, 29.9, 1, "correct", None),
    ("4344.jpg", 27.9, 39.99, 1, "wrong", 39.90),
    ("4350.jpg", 49.9, 71.9, 1, "wrong", 71.50),
    ("4352.jpg", 12.9, 19.99, 1, "wrong", 19.90),
    ("4352.jpg", 30.9, 44.9, 1, "wrong", 44.40),
    ("4360.jpg", 21.9, 40.9, 1, "correct", None),
    ("4360.jpg", 23.5, 42.5, 2, "wrong", 42.90),
    ("4360.jpg", 42.9, 80.9, 1, "correct", None),
    ("4360.jpg", 24.9, 46.9, 1, "correct", None),
    ("4360.jpg", 29.9, 55.9, 1, "correct", None),
    ("4381.jpg", 74.5, 149.0, 1, "wrong", 149.50),
    ("4381.jpg", 99.5, 199.0, 1, "wrong", 199.90),
    ("4382.jpg", 24.5, 49.0, 2, "correct", None),
    ("4382.jpg", 39.5, 79.0, 2, "wrong", 79.90),
    ("4383.jpg", 13.9, 19.9, 1, "correct", None),
    ("4383.jpg", 119.9, 159.9, 2, "correct", None),
    ("4384.jpg", 15.5, 26.75, 2, "wrong", 26.80),
    ("4385.jpg", 59.9, 89.9, 2, "wrong", 89.40),
    ("4385.jpg", 59.9, 90.0, 1, "wrong", 90.70),
    ("4385.jpg", 68.9, 103.0, 1, "wrong", 103.70),
    ("4402.jpg", 46.9, 79.9, 1, "correct", None),
    ("4403.jpg", 79.9, 111.9, 1, "correct", None),
    ("4404.jpg", 11.7, 17.7, 1, "wrong", 17.80),
    ("4404.jpg", 20.5, 29.5, 1, "correct", None),
    ("4404.jpg", 26.9, 39.9, 1, "wrong", 39.70),
    ("4404.jpg", 26.5, 39.9, 1, "wrong", 39.80),
    ("4404.jpg", 15.9, 22.9, 1, "correct", None),
    ("4404.jpg", 119.9, 171.9, 1, "wrong", 171.30),
    ("4426.jpg", 103.9, 230.0, 3, "wrong", 230.90),
    ("4427.jpg", 17.9, 35.0, 1, "wrong", 35.80),
    ("4427.jpg", 22.3, 44.0, 1, "wrong", 44.90),
    ("4428.jpg", 25.5, 37.0, 2, "wrong", 37.90),
    ("4428.jpg", 117.9, 157.0, 2, "wrong", 157.90),
    ("4440.jpg", 64.5, 93.0, 3, "wrong", 93.90),
    ("4468.jpg", 18.3, 40.0, 1, "wrong", 40.90),
    ("4468.jpg", 26.5, 58.0, 1, "wrong", 58.90),
    ("4468.jpg", 36.3, 80.0, 1, "wrong", 80.90),
    ("4470.jpg", 16.9, 29.99, 1, "wrong", 29.80),
    ("4471.jpg", 28.9, 41.99, 2, "wrong", 41.90),
    ("4508.jpg", 29.9, 55.9, 2, "correct", None),
    ("4508.jpg", 21.9, 36.9, 2, "wrong", 36.50),
    ("4508.jpg", 24.9, 46.9, 1, "correct", None),
    ("4508.jpg", 22.9, 41.9, 2, "correct", None),
)
"""`docs/PROMPT-sku-b-close.md` §"The team lead's verdicts", transcribed row for row.

`(file suffix, price_promo, price_old, n, verdict, printed_old)`. The suffix is what the table
writes — every page in this population is `atb_market_official_<id>.jpg` — and it is resolved
against the dump rather than expanded here, so a suffix that reached two pages is a refusal instead
of a silent pick."""

EXPECTED = {"keys": 45, "rows": 61, "correct_rows": 20, "wrong_rows": 41, "accuracy_4dp": 0.3279}
"""The contract's own checksum line, transcribed. NOT derived from `DICTATED` — a checksum computed
from the thing it checks is not a checksum. A mistyped `n` or a swapped verdict lands here."""

DIAGNOSIS = (
    "promo price 61/61 correct · printed % 61/61 correct · crossed-out old price 20/61 — every"
    " error is confined to the small struck-through number (superscript kopiyky garbled, truncated"
    " to .0, or digit-shifted), and depth() is wrong wherever the old price is."
)
"""The team lead's diagnosis line, carried verbatim into this record and into the ADR."""

PHASE = "sku-b — bar 2, the team lead's read applied to the dump"


class Read(NamedTuple):
    """One team-lead read: what was dictated, what it states about itself, and where it lands.

    Everything that changes between two reads of the same kind and nothing that does not — the
    guards, the join and the record's shape are :func:`main`'s, so a second read cannot acquire a
    second set of rules by being written in a second file.
    """

    phase: str
    contract: str
    scope: str
    dictated: tuple
    expected: dict
    diagnosis: str
    record: Path
    out: Path
    stated: dict | None = None
    """The contract's own checksum line, verbatim, when it differs from `expected`."""
    stated_why: str | None = None
    """Why the asserted expectation departs from it — see :func:`deviation`."""
    prior: Path | None = None
    """A sealed earlier read this one extends, checked and split by :func:`carried_forward`."""


THIS = Read(
    phase=PHASE,
    contract=CONTRACT,
    scope=READ_SCOPE,
    dictated=DICTATED,
    expected=EXPECTED,
    diagnosis=DIAGNOSIS,
    record=RECORD,
    out=OUT,
)


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(REPO_ROOT)) if resolved.is_relative_to(REPO_ROOT) else str(path)


def refuse(reason: str) -> None:
    raise SystemExit(f"refused: {reason}")


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pair_rows(dump: list[dict]) -> list[dict]:
    """Bar 2's registered denominator: a leaflet-page position carrying a crossed-out price."""
    return [row for row in dump if row["page"] is not None and row["price_old"] is not None]


def match(dictated, pairs: list[dict]) -> list[dict]:
    """Each dictated key joined to the dump rows it rules on, or a refusal naming the mismatch."""
    claimed: dict[int, str] = {}
    keys = []
    for suffix, promo, old, n, verdict, printed_old in dictated:
        if verdict not in ("correct", "wrong"):
            refuse(f"{suffix} {promo}/{old}: verdict {verdict!r} is neither correct nor wrong")
        files = {row["file"] for row in pairs if row["file"].endswith(suffix)}
        if len(files) > 1:
            refuse(f"the suffix {suffix} reaches {len(files)} different pages: {sorted(files)}")
        rows = [
            i
            for i, row in enumerate(pairs)
            if row["file"].endswith(suffix)
            and row["price_promo"] == promo
            and row["price_old"] == old
        ]
        if not rows:
            refuse(f"{suffix} {promo}/{old} was ruled on and no dump row carries it")
        if len(rows) != n:
            refuse(
                f"{suffix} {promo}/{old}: the read says n={n} and the dump carries {len(rows)}"
                " row(s) — a verdict would land on a different number of positions than it read"
            )
        for i in rows:
            if i in claimed:
                refuse(
                    f"dump pair row {i} is claimed twice: {claimed[i]} and {suffix} {promo}/{old}"
                )
            claimed[i] = f"{suffix} {promo}/{old}"
        # a correct pair's old price IS what the page prints; only a wrong one needs the page read
        if verdict == "correct" and printed_old is not None:
            refuse(f"{suffix} {promo}/{old} is correct and carries printed_old {printed_old}")
        if verdict == "wrong":
            if printed_old is None:
                refuse(f"{suffix} {promo}/{old} is wrong and the read names no printed_old")
            if printed_old == old:
                refuse(
                    f"{suffix} {promo}/{old} is wrong and its printed_old is the dump's own old"
                    " price — a wrong pair whose old price is right is a transcription error"
                )
        printed = old if verdict == "correct" else printed_old
        keys.append(
            {
                "file": sorted(files)[0],
                "price_promo": promo,
                "price_old": old,
                "n": n,
                "verdict": verdict,
                "printed_old": printed,
                "printed_old_dictated": printed_old,
                "items": sorted({pairs[i]["item"] for i in rows}),
                "pages": sorted({pairs[i]["page"] for i in rows}),
                "discount_pct_printed": sorted({pairs[i]["discount_pct_printed"] for i in rows}),
            }
        )
    unclaimed = [i for i in range(len(pairs)) if i not in claimed]
    if unclaimed:
        named = [
            f"{pairs[i]['file'].rsplit('/', 1)[-1]} {pairs[i]['price_promo']}" for i in unclaimed
        ]
        refuse(f"{len(unclaimed)} dump pair row(s) no dictated key covers: {named}")
    return keys


def tally(keys: list[dict]) -> dict:
    """The four counts and the share, straight off a joined table. Asserts nothing."""
    found = {
        "keys": len(keys),
        "rows": sum(key["n"] for key in keys),
        "correct_rows": sum(key["n"] for key in keys if key["verdict"] == "correct"),
        "wrong_rows": sum(key["n"] for key in keys if key["verdict"] == "wrong"),
    }
    accuracy = found["correct_rows"] / found["rows"] if found["rows"] else 0.0
    return {**found, "accuracy": accuracy, "accuracy_4dp": round(accuracy, 4)}


def checksums(keys: list[dict], expected: dict) -> dict:
    """The team lead's stated counts against the joined table. Every miss is a refusal."""
    found = tally(keys)
    for what in ("keys", "rows", "correct_rows", "wrong_rows"):
        if found[what] != expected[what]:
            refuse(
                f"the read states {what} = {expected[what]} and the table joins to {found[what]}"
            )
    if found["accuracy_4dp"] != expected["accuracy_4dp"]:
        refuse(
            f"{found['correct_rows']}/{found['rows']} rounds to {found['accuracy_4dp']} and the"
            f" read states {expected['accuracy_4dp']}"
        )
    return found


def deviation(read: Read) -> dict | None:
    """Where the asserted expectation departs from the contract's own checksum line, field by field.

    A read whose `stated` is None deviates nowhere and this is None. Where it is set, the record
    carries BOTH numbers and names each field that moved: an executor who quietly retypes a
    team-lead checksum to make the applier run has deleted the only thing standing between a
    mistyped dictation and a verdict record, and the difference between that and this is that this
    one is on the page.
    """
    if read.stated is None:
        return None
    moved = {
        field: {"contract": read.stated[field], "asserted": read.expected[field]}
        for field in read.stated
        if read.stated[field] != read.expected[field]
    }
    if not moved:
        refuse(
            "the read carries a separate `stated` checksum line that is identical to `expected` —"
            " a deviation nobody can see is not a deviation, and two names for one number drift"
        )
    return {"contract_checksums": read.stated, "fields": moved, "why": read.stated_why}


def carried_forward(keys: list[dict], prior_path: Path) -> dict:
    """This read against the sealed read it extends: the shared keys checked, the split reported.

    A contract that says "same reader, same pages, the printed values already documented" is making
    a claim about a file on disk, so it is checked rather than repeated. A shared key whose verdict
    or `printed_old` moved is refused — a re-read that quietly flips an adjudicated pair re-scores a
    sample that already has a result, which `attempts.on_failure` forbids in as many words.

    `n` is allowed to differ and is reported: it counts the rows of a DUMP, and two instruments can
    extract one physical price box a different number of times. What may not differ is the verdict.
    """
    prior = json.loads(prior_path.read_text(encoding="utf-8"))
    before = {(key["file"], key["price_promo"], key["price_old"]): key for key in prior["keys"]}
    shared, fresh, moved_n = [], [], []
    for key in keys:
        was = before.get((key["file"], key["price_promo"], key["price_old"]))
        if was is None:
            fresh.append(key)
            continue
        for field in ("verdict", "printed_old"):
            if was[field] != key[field]:
                refuse(
                    f"{key['file'].rsplit('/', 1)[-1]} {key['price_promo']}/{key['price_old']}:"
                    f" {rel(prior_path)} reads {field} {was[field]!r} and this read says"
                    f" {key[field]!r} — a pair that already has a verdict is not re-adjudicated"
                )
        if was["n"] != key["n"]:
            moved_n.append({"key": key["file"], "prior_n": was["n"], "n": key["n"]})
        shared.append(key)
    by_page: dict[str, int] = {}
    for key in fresh:
        page = key["file"].rsplit("/", 1)[-1]
        by_page[page] = by_page.get(page, 0) + key["n"]
    return {
        "prior": {
            "path": rel(prior_path),
            "sha256": sha256_of(prior_path),
            "read_on": prior["read_on"],
            "checksums": prior["checksums"],
        },
        "shared": tally(shared),
        "new": {**tally(fresh), "rows_by_page": dict(sorted(by_page.items()))},
        "rows_whose_n_moved": moved_n,
        "why": (
            "the shared keys are the prior read's verdicts, unchanged and re-asserted against this"
            " dump; the new ones are what this instrument put in front of the reader that the last"
            " one did not. The two shares are what moved the bar, and neither is a re-adjudication"
        ),
    }


def main(argv: list[str] | None = None, read: Read = THIS) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, default=read.record)
    parser.add_argument("--dump", type=Path, help="default: the record's own dump path")
    parser.add_argument("--out", type=Path, default=read.out)
    args = parser.parse_args(argv)

    record = json.loads(args.record.read_text(encoding="utf-8"))
    dump_path = args.dump or REPO_ROOT / record["dump"]["path"]
    dump_sha = sha256_of(dump_path)
    if dump_sha != record["dump"]["sha256"]:
        refuse(
            f"{rel(dump_path)} hashes {dump_sha[:16]}… and {rel(args.record)} pins"
            f" {record['dump']['sha256'][:16]}… — these are not the pairs that were bought"
        )

    dump = [json.loads(line) for line in dump_path.read_text(encoding="utf-8").splitlines() if line]
    pairs = pair_rows(dump)
    keys = match(read.dictated, pairs)
    sums = checksums(keys, read.expected)

    out = {
        "phase": read.phase,
        "contract": read.contract,
        "class": (
            "TRANSCRIPTION. Every verdict here was read by the team lead against the page image;"
            " this file joins the dictation to the dump's rows and refuses anything that does not"
            " land exactly once. No verdict is derived, corrected or inferred"
        ),
        "authority": (
            f"SPEC §10 — the executor never scores its own sample. Read by {READ_BY} on {READ_ON},"
            f" {read.scope}"
        ),
        "read_by": READ_BY,
        "read_on": READ_ON,
        "read_scope": read.scope,
        "record": {"path": rel(args.record), "sha256": sha256_of(args.record)},
        "dump": {"path": rel(dump_path), "sha256": dump_sha, "pair_rows": len(pairs)},
        "key": "(file, price_promo, price_old); n = the dump rows sharing one physical price box",
        "checksums": sums,
        "expected": read.expected,
        "checksum_deviation": deviation(read),
        "diagnosis": read.diagnosis,
        "keys": keys,
    }
    if read.prior is not None:
        out["extends"] = carried_forward(keys, read.prior)
    out["git"] = provenance.git_state(args.out)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"{rel(dump_path)} — {len(pairs)} pair rows over {len(keys)} keys, each matched once")
    print(
        f"  correct {sums['correct_rows']} · wrong {sums['wrong_rows']} ·"
        f" accuracy {sums['accuracy_4dp']:.4f} ({sums['correct_rows']}/{sums['rows']})"
    )
    if out.get("extends"):
        for what in ("shared", "new"):
            part = out["extends"][what]
            print(
                f"  {what:7s} {part['keys']:2d} keys · {part['rows']:2d} rows ·"
                f" {part['correct_rows']}/{part['rows']} = {part['accuracy_4dp']:.4f}"
            )
    if out["checksum_deviation"]:
        print(f"  checksum deviation: {out['checksum_deviation']['fields']}")
    print(f"  {read.diagnosis}")
    print(f"wrote {rel(args.out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
