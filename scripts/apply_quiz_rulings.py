#!/usr/bin/env python3
"""The quiz rulings the operator gave on the emptied 97, and the pattern they validated (4.5g2).

The 4.5g contrastive check was pre-registered at `new / 40 >= 0.90`. The team lead ran it as a
20-row chat quiz instead and it came back **11/20** (`docs/quiz-45g-verdicts.md`), so the bar
failed and the pre-registered fallback stands: the batch is not accepted wholesale. What the quiz
did produce is operator law for the twenty rows it asked about, and one pattern with enough
support to extend — the dish/filling answer under a media-only post, confirmed 10 of 11 times.

This applies exactly those two things and nothing else:

- **(a) the 11 matched rows**, authority `operator-quiz-45g`. A matched row is one where the
  operator's set equals the policy's, so the label written here is the one they wrote down.
- **(b) the taste family**, authority `quiz-validated-pattern`: v1 was exactly `["taste"]`, the
  comment is at most {short} characters, it names no watchlist brand, and its parent post has no
  text of its own. Four conjuncts, all mechanical, all checkable from the corpus.

The 9 divergent rows are deliberately **not** applied. The operator ruled them blind — the class
exists because the parent post is an image nobody could see — and 4.5g2 exists to hand them back
with that image. They go to `emptied_redo.csv` instead.

What it refuses:

- **a ruling the table does not carry.** The quiz file is parsed and totalled first: twenty rows,
  eleven matches, nine divergences, the arms as declared, and `policy == operator` on every
  matched row. A markdown table is a fragile authority, so it is checked before it is believed.
- **a row outside the population.** Every id written here has to derive as one of the 97 by
  `measure_empty_drop`'s own functions, checked against `results/drop_45f.json`.
- **overwriting an operator ruling.** Rows a fix from neither this script nor `relabel_emptied`
  has moved are 4.5f rulings; they are held, whatever the pattern would write.
- **more than one column moving.** Each rewritten line has to reproduce its staged line byte for
  byte once the previous intents are put back — `relabel.relabelled`, the same inverse the paid
  runs were held to.

    PYTHONPATH=src python3 scripts/apply_quiz_rulings.py --dry-run
    PYTHONPATH=src python3 scripts/apply_quiz_rulings.py

Rewrites the staged `_tax2` files' intents column, writes `results/quiz_rulings_45g2.json` and
appends one `fixes` block to `results/relabel_45e.json`. The drift block there is the
re-labeller's own output and is never recomputed.
"""

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))  # the staging convention lives there

import relabel_intents as relabel  # noqa: E402
from apply_calibration_rulings import body, digest, index  # noqa: E402
from build_audit_pack import git_state  # noqa: E402
from build_sitting_pack import SHORT_CHARS  # noqa: E402  (one home for the short-text bound)
from relabel_emptied import population  # noqa: E402
from market_pulse import parents  # noqa: E402
from market_pulse.brands import find_watchlist_brands, watchlist_aliases  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402

QUIZ = REPO_ROOT / "docs" / "quiz-45g-verdicts.md"
DROP = REPO_ROOT / "results" / "drop_45f.json"
RELABEL_RECORD = REPO_ROOT / "results" / "relabel_45e.json"
RECORD = REPO_ROOT / "results" / "quiz_rulings_45g2.json"
REGISTRY = REPO_ROOT / "config" / "registry.yaml"
POSTS = REPO_ROOT / "data" / "raw" / "posts"

APPLIED_BY = "scripts/apply_quiz_rulings.py"
MINE = (APPLIED_BY, "scripts/relabel_emptied.py")
"""Fixes whose authorship is not an operator ruling. Everything else in the history is one, and
is held — the same rule `relabel_emptied` uses, widened by this script's own name so that a
second invocation does not read its own writes back as somebody else's law."""

QUIZ_AUTHORITY = "operator-quiz-45g"
PATTERN_AUTHORITY = "quiz-validated-pattern"
EXPECTED = {"rows": 20, "matched": 11, "divergent": 9, "restore": 14, "model": 6}
"""What `docs/quiz-45g-verdicts.md` says about itself, in its own header. Totals, because a
table that lost a row to a formatting slip still parses — it just parses into a smaller quiz."""

PATTERN_RULE = (
    'v1 intents were exactly ["taste"], the comment is at most {short} characters, it names no'
    " watchlist brand, and its parent post has no text of its own. Support: of the 11 `taste`"
    " proposals in the quiz the operator confirmed 10, and the one refusal (@msuaaaa:11941"
    ' "Вацак 🤮") is a watchlist-shaped brand name rather than a dish, which is the conjunct'
    " that excludes it. The bound is scripts/build_sitting_pack.py's SHORT_CHARS, the same"
    " threshold the sitting strata already use, and not a number chosen for this rule."
)


def quiz_rows(path: Path) -> list[dict]:
    """The verdict table, parsed and then totalled against what its own header claims."""
    text = path.read_text(encoding="utf-8")
    rows = []
    for line in text.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 6 or not cells[1].startswith("@"):
            continue
        try:
            policy, operator = json.loads(cells[3]), json.loads(cells[4])
        except ValueError:
            raise SystemExit(f"{relabel.rel(path)}: row {cells[0]} has unreadable label cells")
        rows.append(
            {
                "id": cells[1],
                "arm": cells[2],
                "policy": sorted(policy),
                "operator": sorted(operator),
                "match": cells[5] == "yes",
            }
        )
    matched = [row for row in rows if row["match"]]
    found = {
        "rows": len(rows),
        "matched": len(matched),
        "divergent": len(rows) - len(matched),
        "restore": sum(1 for row in rows if row["arm"] == "restore"),
        "model": sum(1 for row in rows if row["arm"] == "model"),
    }
    if found != EXPECTED:
        raise SystemExit(
            f"{relabel.rel(path)} parses as {found} and declares {EXPECTED}. The table is the"
            " authority for every label written here, so a shape it does not confirm is not one"
            " to write from."
        )
    if not re.search(rf"RESULT: {EXPECTED['matched']}/{EXPECTED['rows']} matches", text):
        raise SystemExit(f"{relabel.rel(path)}: the RESULT line does not state the parsed total")
    for row in rows:
        if row["match"] != (row["policy"] == row["operator"]):
            raise SystemExit(
                f"{row['id']}: marked {'a match' if row['match'] else 'divergent'} while policy"
                f" {row['policy']} and operator {row['operator']} say otherwise"
            )
    if len({row["id"] for row in rows}) != len(rows):
        raise SystemExit(f"{relabel.rel(path)}: an id appears twice, so a ruling is ambiguous")
    return rows


def operator_ruled(record: Path) -> set[str]:
    """Ids a fix *neither this script nor the re-labeller* wrote has moved — an operator ruling.

    `relabel_emptied.ruled` answers the same question one name short: run twice, this script
    would read its own `fixes` block back and report its own writes as somebody's law. So the
    authorship filter carries both names, and a ruling applied tomorrow by a third script is
    still protected without an id being named here.
    """
    if not record.exists():
        return set()
    history = json.loads(record.read_text(encoding="utf-8"))
    return {
        row["id"]
        for fix in history.get("fixes", [])
        if fix.get("applied_by") not in MINE
        for row in fix["rows"]
    }


def taste_family(emptied: list[dict], labelled: dict, posts: dict, aliases: dict) -> list[dict]:
    """The rows the validated pattern closes, each carrying which conjuncts it met."""
    found = []
    for row in emptied:
        raw = labelled[row["id"]]
        tests = {
            "v1_is_taste_only": row["before"] == ["taste"],
            "short": len(raw["text"]) <= SHORT_CHARS,
            "no_watchlist_brand": not find_watchlist_brands(raw["text"], aliases),
            "parent_is_media_only": not parents.text_for(posts, raw).strip(),
        }
        if all(tests.values()):
            found.append({"id": row["id"], "intents": ["taste"], "conjuncts": tests})
    return found


def rulings(quiz: list[dict], family: list[dict]) -> list[dict]:
    """The two authorities in one list, the operator's first — a quiz row is never a pattern row.

    Order matters only because the first ruling for an id wins; the operator wrote a label down
    for these eleven, and a mechanical rule agreeing with it does not get to claim the row.
    """
    seen = set()
    out = []
    for row in quiz:
        if not row["match"]:
            continue
        seen.add(row["id"])
        out.append(
            {
                "id": row["id"],
                "intents": row["operator"],
                "authority": QUIZ_AUTHORITY,
                "detail": f"quiz row {row['arm']} arm: policy {row['policy']}, operator agreed",
            }
        )
    for row in family:
        if row["id"] in seen:
            continue
        out.append(
            {
                "id": row["id"],
                "intents": row["intents"],
                "authority": PATTERN_AUTHORITY,
                "detail": PATTERN_RULE.format(short=SHORT_CHARS),
                "conjuncts": row["conjuncts"],
            }
        )
    return out


def apply_all(rulings_: list[dict], held: set[str], staged: dict[str, Path]) -> dict:
    """Every ruling written into the staged intents column, one column and no more."""
    where = index(staged)
    loaded = {key: relabel.load(path) for key, path in staged.items()}
    for key, path in staged.items():
        # `load` drops blank lines, so joining them back is only lossless if there were none.
        if body(loaded[key][1]) != path.read_text(encoding="utf-8"):
            raise SystemExit(
                f"{relabel.rel(path)}: its lines do not join back into the file it was read"
                " from, so rewriting it would change lines no ruling names."
            )
    touched: dict[str, list[str]] = {}
    applied, unchanged, skipped = [], [], []
    for ruling in rulings_:
        row_id, wanted = ruling["id"], sorted(ruling["intents"])
        if row_id in held:
            skipped.append({**ruling, "reason": "held by an operator ruling from 4.5f"})
            continue
        key, position = where[row_id]
        rows, lines = loaded[key]
        row, line = rows[position], lines[position]
        before = sorted(row["intents"])
        entry = {
            "id": row_id,
            "file": relabel.rel(staged[key]),
            "old": before,
            "new": wanted,
            "authority": ruling["authority"],
            "detail": ruling["detail"],
        }
        if before == wanted:
            unchanged.append(entry)
            continue
        lines[position] = relabel.relabelled(row, line, wanted)
        rows[position] = {**row, "intents": wanted}
        touched.setdefault(key, []).append(row_id)
        applied.append(entry)
    before_sha = {relabel.rel(staged[key]): digest(staged[key]) for key in touched}
    for key in touched:
        staged[key].write_text(body(loaded[key][1]), encoding="utf-8")
    after_sha = {relabel.rel(staged[key]): digest(staged[key]) for key in touched}
    return {
        "applied": applied,
        "unchanged": unchanged,
        "skipped": skipped,
        "before": before_sha,
        "after": after_sha,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quiz", type=Path, default=QUIZ)
    parser.add_argument("--record", type=Path, default=RECORD)
    parser.add_argument("--relabel-record", type=Path, default=RELABEL_RECORD)
    parser.add_argument("--drop", type=Path, default=DROP)
    parser.add_argument("--posts", type=Path, default=POSTS)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--dry-run", action="store_true", help="what would be written, then stop")
    args = parser.parse_args(argv)

    quiz = quiz_rows(args.quiz)
    emptied = population(args.drop, args.relabel_record)
    held = operator_ruled(args.relabel_record)
    labelled = {
        row["id"]: row for source in relabel.SOURCES.values() for row in relabel.load(source)[0]
    }
    posts = parents.load(args.posts)
    aliases = watchlist_aliases(load_registry(args.registry).watchlist)

    in_population = {row["id"] for row in emptied}
    outside = sorted(row["id"] for row in quiz if row["id"] not in in_population)
    if outside:
        raise SystemExit(
            f"{outside} are in the quiz and not in the 97 the re-label emptied. The quiz asked"
            " about that class, so a row outside it is a row this script cannot place."
        )
    family = taste_family(emptied, labelled, posts, aliases)
    todo = rulings(quiz, family)
    by_authority = {
        name: [row for row in todo if row["authority"] == name]
        for name in (QUIZ_AUTHORITY, PATTERN_AUTHORITY)
    }
    print(
        f"{len(emptied)} emptied rows, population verified against {relabel.rel(args.drop)}"
        f"\n  {len(by_authority[QUIZ_AUTHORITY])} matched quiz rows ({QUIZ_AUTHORITY})"
        f"\n  {len(family)} rows match the validated pattern, {len(by_authority[PATTERN_AUTHORITY])}"
        f" of them not already ruled on ({PATTERN_AUTHORITY})"
        f"\n  {len(held)} held by a 4.5f operator ruling: {', '.join(sorted(held)) or '—'}"
    )
    if args.dry_run:
        for ruling in todo:
            print(f"  {ruling['id']:<24} -> {ruling['intents']}  {ruling['authority']}")
        return 0

    staged = {key: relabel.staged(path) for key, path in relabel.SOURCES.items()}
    outcome = apply_all(todo, held, staged)
    for entry in outcome["applied"]:
        print(f"  {entry['id']:<24} {entry['old']} -> {entry['new']}   {entry['authority']}")

    record = {
        "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
        "authority": {
            QUIZ_AUTHORITY: relabel.rel(args.quiz),
            PATTERN_AUTHORITY: PATTERN_RULE.format(short=SHORT_CHARS),
        },
        "quiz": {
            "rows": len(quiz),
            "matched": len(by_authority[QUIZ_AUTHORITY]),
            "divergent": sorted(row["id"] for row in quiz if not row["match"]),
            "divergent_note": (
                "Ruled blind: the class exists because the parent post is an image, and these"
                " nine are the rows where the operator's blind verdict and the policy disagree."
                " They are NOT applied — they go back with the image in emptied_redo.csv."
            ),
        },
        "population": {"rows": len(emptied), "source": relabel.rel(args.drop)},
        "pattern": {
            "rule": PATTERN_RULE.format(short=SHORT_CHARS),
            "short_chars": SHORT_CHARS,
            "matched": sorted(row["id"] for row in family),
            "new_to_the_operator": sorted(
                row["id"] for row in by_authority[PATTERN_AUTHORITY] if row["id"] not in held
            ),
        },
        "applied": outcome["applied"],
        "unchanged": outcome["unchanged"],
        "held": outcome["skipped"],
        "staged_sha256_before": outcome["before"],
        "staged_sha256_after": outcome["after"],
        "git": git_state(args.record),
        "note": (
            "The two things the 11/20 quiz settled, and nothing else. The bar it was run against"
            " (18/20) failed, so the batch of 97 is not accepted: what is written here is the"
            " eleven rows the operator matched and the family their taste proposals validated."
            " Everything else in the 97 goes back to the operator with the parent image."
        ),
    }
    relabel.append_record(args.record, record)

    if outcome["applied"]:
        history = json.loads(args.relabel_record.read_text(encoding="utf-8"))
        history.setdefault("fixes", []).append(
            {
                "applied_by": APPLIED_BY,
                "timestamp": record["timestamp"],
                "authority": relabel.rel(args.record),
                "rows": outcome["applied"],
                "staged_sha256_before": outcome["before"],
                "staged_sha256_after": outcome["after"],
                "note": (
                    "Operator quiz rulings and the pattern they validated (4.5g2). The drift and"
                    " churn in `runs` are the re-labeller's own output under the old prompt and"
                    " are deliberately NOT recomputed: they are what the 4.5f gate judged."
                ),
                "git": git_state(args.relabel_record),
            }
        )
        relabel.write_json(args.relabel_record, history)
    # Re-derived from the staged files with every fix reversed, so it has to still be the same 97
    # now that this run's own block is in the history. Checked rather than argued: a population
    # that stops deriving is how the next phase comes to measure a different class.
    still = population(args.drop, args.relabel_record)
    print(
        f"\n{len(outcome['applied'])} rows rewritten, intents only ·"
        f" {len(outcome['unchanged'])} already matching · {len(outcome['skipped'])} held"
        f"\nthe population still derives as {len(still)} rows after the fix block"
        f"\nwrote {relabel.rel(args.record)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
