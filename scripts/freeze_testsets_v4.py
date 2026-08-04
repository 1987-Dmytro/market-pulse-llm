#!/usr/bin/env python3
"""v4 of the frozen test sets: the intents law, materialized (4.5h2).

SPEC amendment 3.9 (3) fixes the derivation and this executes it, in that order and
nothing else:

    v3  ->  the migration pass (`intents` only, 508 rows attempted)
        ->  the 31 audit intents rulings, re-applied ON TOP
        ->  the 1 law verdict of guideline v2, on top of those

"On top" is the whole point: an operator ruling supersedes the model, so a row the
operator adjudicated keeps the operator's answer even where the pass moved it.

The same discipline as v3, and for the same reasons:

- **v2 and v3 are never touched.** v4 is new files beside them, so every record, bar and
  manifest that references an older sha keeps meaning what it meant.
- **only `intents` moves.** `sentiment`, `sarcasm`, `unclear`, `text` and every T2 field
  are re-serialised from v3 and required to come back byte for byte; `annotator` moves
  only on a row whose `intents` actually changed, the way v3 stamped its own fixes.
- **the counts are pre-registered.** A derivation that yields other numbers stops instead
  of writing.
- **a row the pass could not read keeps its v3 `intents` and is named.** 39 of them, and
  the record lists every id: `{}` is what the model answered on those rows, and coercing
  it to `[]` — the majority answer — would rewrite gold exactly where the instrument
  failed (`results/migration_45h2.json`).
- **posts carry no `intents` column at all**, so `posts_test_v4` is `posts_test_v3`
  re-serialised under the v4 name and its changelog is required to be empty.

The 54 dual-home ids are resolved here too, by option (i) of the precheck: the holdout
pool is written out at 917 rows as a NEW file beside the pristine 971, so each id lives
in exactly one place and every existing sha pin stays valid.

    PYTHONPATH=src python3 scripts/freeze_testsets_v4.py

Writes ``data/frozen/*_v4.jsonl``, ``data/annotation/sarcasm_holdout_pool_v4.jsonl`` and
``results/frozen_v4.json``, and prints the summary docs/frozen-testsets.md quotes.
"""

import argparse
import json
import sys
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))

import freeze_testsets_v3 as v3  # noqa: E402
import precheck_45h as precheck  # noqa: E402

from market_pulse import audit  # noqa: E402

FROZEN = REPO_ROOT / "data" / "frozen"
ANNOTATION = REPO_ROOT / "data" / "annotation"
RESULTS = REPO_ROOT / "results"

V3_RECORD = RESULTS / "frozen_v3.json"
MIGRATION = RESULTS / "migration_45h2_rows.jsonl"
MIGRATION_RECORD = RESULTS / "migration_45h2.json"
RECORD = RESULTS / "frozen_v4.json"

INPUTS = ("comments_test", "sarcasm_holdout", "posts_test")
POOL = ANNOTATION / "sarcasm_holdout_pool.jsonl"
POOL_V4 = ANNOTATION / "sarcasm_holdout_pool_v4.jsonl"

EXPECTED = {
    "migration_attempted": 508,
    "migration_written": 469,
    "migration_kept_v3": 39,
    "audit_rulings": 31,
    "law_verdicts": 1,
    "pool_rows": 917,
    "pool_dropped": 54,
    "posts_changed": 0,
}
"""What amendment 3.9 (3) and the migration record between them say this must produce.

`migration_written` is not a target the pass was steered to — it is what
`results/migration_45h2.json` recorded after its resume, checked here so that a re-run
against a different pass file stops instead of freezing a second version of v4."""

ANNOTATOR = {
    "migration": "intents-v2-migration-45h2",
    "audit": v3.ANNOTATOR,
    "law": "operator-law-v2",
}
"""Where a moved `intents` value came from, stamped on the row itself. Three sources,
three names — a frozen row should say which one wrote it without a changelog lookup."""

MOVES = ("intents",)
"""Every field this freeze is allowed to move, `annotator` aside. Named rather than
implied: it is what turns "only intents moved" into a check."""


def summary_table(record: dict) -> str:
    """The doc's table, generated: a hand-typed one is a second source of truth.

    A per-id changelog the way v3 printed one would be 274 rows here, so the document
    gets the counts and the hashes and `results/frozen_v4.json` keeps the per-id list.
    """
    lines = [
        "| file | rows | changed | migration | audit | law | sha256 (v4) |",
        "|---|---|---|---|---|---|---|",
    ]
    for name, sizes in record["rows"].items():
        by = sizes["by_source"]
        lines.append(
            f"| `data/frozen/{name}` | {sizes['rows']} | {sizes['rows_changed']} |"
            f" {by['migration']} | {by['audit']} | {by['law']} |"
            f" `{record['v4_sha256'][name]}` |"
        )
    pool = record["holdout_pool"]
    lines.append(f"| `{pool['v4']}` | {pool['rows']} | — | — | — | — | `{pool['v4_sha256']}` |")
    return "\n".join(lines)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def lines_of(path: Path) -> list[str]:
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def migrated() -> dict[str, list[str]]:
    """``id -> intents`` from the paid pass, re-checked against what its record claims."""
    rows = [json.loads(line) for line in lines_of(MIGRATION)]
    record = json.loads(MIGRATION_RECORD.read_text(encoding="utf-8"))["runs"][-1]
    if len(rows) != record["accounting"]["written"]:
        raise SystemExit(
            f"{rel(MIGRATION)} holds {len(rows)} rows and its record claims"
            f" {record['accounting']['written']} — the two are not the same run"
        )
    return {row["id"]: row["intents"] for row in rows}


def audit_manifest() -> dict:
    """The manifest the blind audit was built from, reached through v3's own record."""
    record = json.loads(V3_RECORD.read_text(encoding="utf-8"))
    return json.loads((REPO_ROOT / record["source"]["manifest"]).read_text(encoding="utf-8"))


def ruled_intents(manifest: dict | None = None) -> tuple[dict[str, list[str]], dict]:
    """The 31 audit rulings, as values — derived from the pack the gate read, not listed.

    `freeze_testsets_v3` derived exactly these and deliberately did not apply them
    (`LAW_PENDING`); the law is settled now, so the same derivation runs and the values
    come from the same place: the arm's own dump, which is what the operator ruled for.
    """
    manifest = manifest or audit_manifest()
    key = json.loads((REPO_ROOT / manifest["key_path"]).read_text(encoding="utf-8"))
    ruled = v3.read_pack(REPO_ROOT / manifest["pack_path"], key)
    dump = REPO_ROOT / manifest["predictions_path"]
    predicted: dict[str, dict[str, dict]] = {}
    for line in dump.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        predicted.setdefault(row["input"], {})[row["id"]] = row["pred"]
    source = predicted[audit.INPUT_OF["intents"]]
    return {row_id: sorted(set(source[row_id]["intents"])) for row_id in ruled["intents"]}, ruled


def law_values() -> dict[str, list[str]]:
    """The corpus rows guideline v2 rules on directly — one definition, imported.

    `precheck_45h.LAW_VERDICTS` transcribes `taxonomy-v2-relabel-and-appetite` §(b) and is
    already under test; two of its three entries are guideline examples rather than rows.
    """
    return {
        row_id: verdict["v2"]
        for row_id, verdict in precheck.LAW_VERDICTS.items()
        if verdict["where"].startswith("data/frozen/")
    }


def apply_to(lines: list[str], fixes: dict[str, tuple[list[str], str]]) -> tuple[list[str], list]:
    """v4's lines and its changelog — and a stop if an untouched row would move.

    Re-serialising a row that takes no fix must reproduce its v3 line byte for byte, and a
    row that does take one must differ from it in ``intents`` and ``annotator`` alone.
    That pair is what makes "v4 differs from v3 only in the intents column" a check.

    ``fixes`` is one input's own, never the whole set: a post and a comment can carry the
    same ``@channel:msg_id`` and 11 of these do, so a lookup by id alone would write a
    comment's intents onto a post row — which is how this function first ran.

    A fix is compared as a SET, and a fix that agrees with the row is a confirmation
    rather than a change — v3's own rule, applied to the one field this freeze moves. The
    pass returns its labels sorted and 34 v3 rows do not carry them sorted, so on 4 rows
    the only difference is the order; ``intents`` is scored as a label set
    (`scorer.intents_micro_f1`), so rewriting those rows would move bytes, stamp a
    different annotator and change no answer.
    """
    out, changes = [], []
    for line in lines:
        row = json.loads(line)
        found = fixes.get(row["id"])
        if found is None or set(row["intents"]) == set(found[0]):
            if json.dumps(row, ensure_ascii=False) != line:
                raise SystemExit(
                    f"{row['id']}: re-serialising an unchanged row does not reproduce its v3 line."
                    " v4 would differ from v3 in rows nothing ruled, so nothing is written."
                )
            out.append(line)
            continue
        intents, source = found
        changes.append({"id": row["id"], "from": row["intents"], "to": intents, "source": source})
        produced = {**row, "intents": intents, "annotator": ANNOTATOR[source]}
        if {k: v for k, v in produced.items() if k not in (*MOVES, "annotator")} != {
            k: v for k, v in row.items() if k not in (*MOVES, "annotator")
        }:
            raise SystemExit(f"{row['id']}: this fix moves a field outside {MOVES}")
        out.append(json.dumps(produced, ensure_ascii=False))
    return out, changes


def pool_without(holdout_ids: set[str]) -> tuple[list[str], list[str]]:
    """The holdout pool at 917 rows: single-home materialization, option (i).

    A new file beside the pristine 971 rather than an edit of it — four records pin the
    original's sha256, and amendment 3.9 (3) keeps them valid by construction.
    """
    kept, dropped = [], []
    for line in lines_of(POOL):
        (dropped if json.loads(line)["id"] in holdout_ids else kept).append(line)
    return kept, dropped


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, default=RECORD)
    parser.add_argument("--out", type=Path, default=FROZEN)
    parser.add_argument("--pool-out", type=Path, default=POOL_V4)
    args = parser.parse_args(argv)

    v3_record = json.loads(V3_RECORD.read_text(encoding="utf-8"))
    manifest = json.loads((REPO_ROOT / v3_record["source"]["manifest"]).read_text(encoding="utf-8"))
    for name, expected in v3_record["v2_sha256"].items():
        if digest(FROZEN / name) != expected:
            raise SystemExit(f"{name}: v2 has moved. v4 cannot be derived from a shifted base.")
    for name, expected in v3_record["v3_sha256"].items():
        if digest(FROZEN / name) != expected:
            raise SystemExit(f"{name}: sha256 is not results/frozen_v3.json's — v3 has moved.")

    moved = migrated()
    rulings, ruled = ruled_intents(manifest)
    law = law_values()
    if len(rulings) != EXPECTED["audit_rulings"] or len(law) != EXPECTED["law_verdicts"]:
        raise SystemExit(
            f"the pack yields {len(rulings)} intents rulings and {len(law)} law verdicts;"
            f" amendment 3.9 (3) says {EXPECTED['audit_rulings']} and {EXPECTED['law_verdicts']}."
        )
    if overlap := set(rulings) & set(law):
        raise SystemExit(f"{sorted(overlap)}: ruled twice, and the order would decide gold")

    # Which input owns an id, so no fix can cross the comment/post namespace boundary.
    owner = {
        name: {json.loads(line)["id"] for line in lines_of(FROZEN / f"{name}_v3.jsonl")}
        for name in INPUTS
    }
    # the order of amendment 3.9 (3): the pass first, the operator's rulings over it
    flat: dict[str, tuple[list[str], str]] = {i: (v, "migration") for i, v in moved.items()}
    flat |= {i: (v, "audit") for i, v in rulings.items()}
    flat |= {i: (v, "law") for i, v in law.items()}
    fixes = {
        name: {i: fix for i, fix in flat.items() if i in owner[name]}
        for name in INPUTS
        if name != "posts_test"
    }
    fixes["posts_test"] = {}
    homeless = set(flat) - set().union(*(set(part) for part in fixes.values()))
    if homeless:
        raise SystemExit(f"{sorted(homeless)}: ruled, but in no comment input — nothing is written")

    written, changes, shas, superseded = {}, {}, {}, {}
    for name in INPUTS:
        source = FROZEN / f"{name}_v3.jsonl"
        lines, changed = apply_to(lines_of(source), fixes[name])
        target = args.out / f"{name}_v4.jsonl"
        body = "\n".join(lines) + "\n"
        target.write_text(body, encoding="utf-8")
        written[target.name] = {
            "rows": len(lines),
            "rows_changed": len(changed),
            "by_source": {
                source_name: sum(1 for c in changed if c["source"] == source_name)
                for source_name in ANNOTATOR
            },
        }
        changes[target.name] = changed
        shas[target.name] = sha256(body.encode("utf-8")).hexdigest()
    if written["posts_test_v4.jsonl"]["rows_changed"] != EXPECTED["posts_changed"]:
        raise SystemExit("a post row moved, and posts carry no intents column at all")
    superseded = {
        row_id: moved[row_id]
        for row_id in (*rulings, *law)
        if row_id in moved and moved[row_id] != flat[row_id][0]
    }

    holdout_ids = {json.loads(line)["id"] for line in lines_of(FROZEN / "sarcasm_holdout_v3.jsonl")}
    kept, dropped = pool_without(holdout_ids)
    if (len(kept), len(dropped)) != (EXPECTED["pool_rows"], EXPECTED["pool_dropped"]):
        raise SystemExit(
            f"the pool materializes at {len(kept)} rows dropping {len(dropped)};"
            f" amendment 3.9 (3) says {EXPECTED['pool_rows']} and {EXPECTED['pool_dropped']}."
        )
    pool_body = "\n".join(kept) + "\n"
    args.pool_out.write_text(pool_body, encoding="utf-8")

    kept_v3 = sorted(
        row_id
        for row_id in {
            json.loads(line)["id"] for line in lines_of(FROZEN / "comments_test_v3.jsonl")
        }
        | holdout_ids
        if row_id not in moved
    )
    if len(kept_v3) != EXPECTED["migration_kept_v3"]:
        raise SystemExit(f"{len(kept_v3)} rows the pass could not read, expected {EXPECTED}")
    # Four of the unread rows are covered by an operator ruling, which supersedes the pass
    # whether or not the pass answered. Only the rest actually keep their v3 value, and a
    # record that called all 39 "kept" would be wrong about gold on four rows.
    ruled_ids = {*rulings, *law}
    untouched = [row_id for row_id in kept_v3 if row_id not in ruled_ids]

    record = {
        "derived_by": "scripts/freeze_testsets_v4.py",
        "gate": "SPEC amendment 3.9 (3): v3 -> intents migration -> 31 audit rulings -> 1 law"
        " verdict, operator rulings on top",
        "testset_version": "v4",
        "order": ["migration", "audit", "law"],
        "source": {
            "v3_record": rel(V3_RECORD),
            "migration_rows": rel(MIGRATION),
            "migration_rows_sha256": digest(MIGRATION),
            "migration_record": rel(MIGRATION_RECORD),
            "audit_manifest": v3_record["source"]["manifest"],
            "predictions_path": manifest["predictions_path"],
            "predictions_sha256": manifest["predictions_sha256"],
            "key_sha256": manifest["key_sha256"],
            "law": "knowledge/decisions/taxonomy-v2-relabel-and-appetite.md §(b), via"
            " scripts/precheck_45h.py LAW_VERDICTS",
        },
        "v2_sha256": v3_record["v2_sha256"],
        "v3_sha256": v3_record["v3_sha256"],
        "v4_sha256": shas,
        "rows": written,
        "counts": {
            "migration_attempted": EXPECTED["migration_attempted"],
            "migration_written": len(moved),
            "migration_unread": len(kept_v3),
            "migration_kept_v3": len(untouched),
            "audit_rulings": len(rulings),
            "law_verdicts": len(law),
            "rulings_over_the_pass": len(superseded),
        },
        "unread_by_the_pass": kept_v3,
        "kept_v3_intents": untouched,
        "unread_but_ruled": sorted(set(kept_v3) & ruled_ids),
        "superseded_by_a_ruling": superseded,
        "audit_ruling_ids": sorted(rulings),
        "law_verdict_ids": sorted(law),
        "intents_rulings_derived_by_v3": len(ruled["intents"]),
        "posts": {
            "file": "posts_test_v4.jsonl",
            "carries_intents": False,
            "note": "posts_test_v3.jsonl re-serialised under the v4 name. The T2 heads are"
            " relevance, post_type and brands; nothing in the intents law can move a post row,"
            " and the changelog is required to be empty.",
        },
        "holdout_pool": {
            "pristine": rel(POOL),
            "pristine_sha256": digest(POOL),
            "v4": rel(args.pool_out),
            "v4_sha256": sha256(pool_body.encode("utf-8")).hexdigest(),
            "rows": len(kept),
            "dropped": len(dropped),
            "why": "option (i) of results/precheck_45h.json: each id lives in exactly one file."
            " A new file, so the four records pinning the pristine sha stay valid.",
        },
        "changes": changes,
        "git": v3.git_state(args.record),
    }
    args.record.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"v4 written to {rel(args.out)} — v2 and v3 untouched")
    for name, sizes in written.items():
        print(
            f"  {name:<26} {sizes['rows']:>4} rows · {sizes['rows_changed']:>3} changed"
            f"  {sizes['by_source']}  {shas[name][:16]}…"
        )
    print(f"  {args.pool_out.name:<26} {len(kept):>4} rows · {len(dropped)} dropped to the holdout")
    print(
        f"\n  migration {len(moved)} written of {EXPECTED['migration_attempted']} attempted,"
        f" {len(kept_v3)} unread of which {len(untouched)} keep their v3 intents"
    )
    print(f"  rulings applied over the pass: {len(superseded)} of {len(rulings) + len(law)}")
    print(f"\n{summary_table(record)}\n\nrecord: {rel(args.record)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
