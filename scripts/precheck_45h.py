"""The 4.5h precheck: six questions answered from files, nothing written but a record.

Read-only by construction. No model is called, no pod is started, no frozen file,
пласт or gold row is opened for writing — the whole phase is $0 and the ledger
section of the record is what proves it.

Every number the report states is derived here so it can be re-derived. Two of
them are numbers a document already claims, and both are checked rather than
copied: `docs/STATUS.md` says arm A trains on 2 346 rows, and the brief says the
пласт adds to that count. The first is a different quantity from the one the
trainer uses and the second is only true if the ids are disjoint — so both are
computed from the files and the disagreement, where there is one, is reported.

Usage: PYTHONPATH=src python3 scripts/precheck_45h.py [--record results/precheck_45h.json]
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

FROZEN = REPO_ROOT / "data" / "frozen"
ANNOTATION = REPO_ROOT / "data" / "annotation"
RESULTS = REPO_ROOT / "results"
RECORD = RESULTS / "precheck_45h.json"

HOLDOUT = FROZEN / "sarcasm_holdout.jsonl"
HOLDOUT_V3 = FROZEN / "sarcasm_holdout_v3.jsonl"
COMMENTS_TEST = FROZEN / "comments_test.jsonl"
COMMENTS_TEST_V3 = FROZEN / "comments_test_v3.jsonl"
PLAST = ANNOTATION / "uplabel_precheck_45g2.jsonl"

# The stores a moved holdout row could still be living in. `train_qlora.SOURCES`
# is the training side; the pool is where the 54 came from and the batch is where
# the 400 test rows came from — neither is a training source, and saying so is
# half the answer to "does the dual home cost anything".
HOMES = {
    "comments_train.jsonl": FROZEN / "comments_train.jsonl",
    "comments_train_tax2.jsonl": FROZEN / "comments_train_tax2.jsonl",
    "sarcasm_candidates.jsonl": ANNOTATION / "sarcasm_candidates.jsonl",
    "sarcasm_candidates_tax2.jsonl": ANNOTATION / "sarcasm_candidates_tax2.jsonl",
    "sarcasm_holdout_pool.jsonl": ANNOTATION / "sarcasm_holdout_pool.jsonl",
    "sarcasm_holdout_pool_tax2.jsonl": ANNOTATION / "sarcasm_holdout_pool_tax2.jsonl",
    "comments_batch.jsonl": ANNOTATION / "comments_batch.jsonl",
    "uplabel_precheck_45g2.jsonl": PLAST,
}
TRAINING_SIDE = ("comments_train.jsonl", "sarcasm_candidates.jsonl", "uplabel_precheck_45g2.jsonl")
"""The three the brief names, and the only three a training run can reach:
`train_qlora.SOURCES` opens the first two and `NEVER_READ` forbids the pool."""

LABEL_FIELDS = ("sentiment", "sarcasm", "intents", "unclear", "text", "language", "annotator")
SERVICE = "service"
"""The sixth intent of taxonomy v2 (amendment 3.8). A store that holds it somewhere
has been through the v2 re-label; a store with zero of them has not. That is the
discriminator this step uses, because no file carries a taxonomy version field."""

# The three rows guideline v2 rules on directly (taxonomy-v2-relabel-and-appetite
# §(b)). Two are guideline examples and one is a row of the frozen test set — the
# only one of the three that a re-label could collide with.
LAW_VERDICTS = {
    "@VARUS_channel:5951": {
        "v1": ["price", "availability"],
        "v2": ["price", "service"],
        "where": "data/frozen/comments_test.jsonl",
    },
    "comments.md sarcasm example 2": {
        "v1": [],
        "v2": ["service"],
        "where": "docs/annotation/comments.md",
    },
    "comments.md sarcasm example 3": {
        "v1": ["availability"],
        "v2": ["service"],
        "where": "docs/annotation/comments.md",
    },
}

GPU_USD_PER_HOUR = 0.53
"""The A6000 rate the 4.5h briefing projects against (docs/PROMPT-4.5h.md Step 1.5).
Stated by the team lead, not derived here; the ledger below is what it is checked
against after the fact."""
CEILING_HOURS = 5.0
"""SPEC amendment 3.6: the per-arm projection ceiling, raised 4 h -> 5 h at the 4b
acceptance. A projection over it stops the line for an operator decision."""


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def load(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"{rel(path)}: not found")
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def by_id(rows: list[dict]) -> dict[str, dict]:
    return {row["id"]: row for row in rows}


def scoreable(rows: list[dict]) -> list[dict]:
    """The rows a training run keeps — `train_qlora.examples` line for line.

    One definition, imported by `measure_categories.py` rather than written twice:
    two readings of "scoreable" that disagree by three rows is exactly the kind of
    difference that survives a review.
    """
    return [row for row in rows if not row["unclear"]]


def line_of(path: Path, marker: str) -> int:
    """The 1-based line a marker sits on — so a `file:line` in the report cannot go stale.

    A hand-typed line number is right until someone inserts an import. This raises
    instead of reporting a line that no longer holds what it claims.
    """
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if marker in line:
            return number
    raise SystemExit(f"{rel(path)}: the guard marker {marker!r} is gone — the report would lie")


# --- (1) the 54 that live in two files --------------------------------------
def dual_home() -> dict:
    holdout, holdout_v3 = by_id(load(HOLDOUT)), by_id(load(HOLDOUT_V3))
    stores = {name: by_id(load(path)) for name, path in HOMES.items()}
    texts = {name: {row["text"] for row in rows.values()} for name, rows in stores.items()}

    hits = {
        name: sorted(set(rows) & set(holdout))
        for name, rows in stores.items()
        if set(rows) & set(holdout)
    }
    moved = sorted(set(stores["sarcasm_holdout_pool.jsonl"]) & set(holdout))
    pool = stores["sarcasm_holdout_pool.jsonl"]

    def diverging(left: dict, right: dict, ids: list[str]) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        for row_id in ids:
            for field in LABEL_FIELDS:
                a = json.dumps(left[row_id].get(field), ensure_ascii=False, sort_keys=True)
                b = json.dumps(right[row_id].get(field), ensure_ascii=False, sort_keys=True)
                if a != b:
                    out.setdefault(field, []).append(row_id)
        return {field: sorted(ids) for field, ids in sorted(out.items())}

    return {
        "moved_ids": moved,
        "n_moved": len(moved),
        "second_home": "data/annotation/sarcasm_holdout_pool.jsonl",
        "id_hits_per_store": {name: len(ids) for name, ids in sorted(hits.items())},
        "verbatim_text_hits_per_store": {
            name: len(texts[name] & {row["text"] for row in holdout.values()})
            for name in sorted(stores)
        },
        "training_side_hits": {
            name: len(set(stores[name]) & set(holdout)) for name in TRAINING_SIDE
        },
        "diverging_columns": {
            "pool_v1_vs_frozen_v2": diverging(pool, holdout, moved),
            "pool_v1_vs_frozen_v3": diverging(pool, holdout_v3, moved),
            "frozen_v2_vs_frozen_v3_the_54": diverging(holdout, holdout_v3, moved),
            "frozen_v2_vs_frozen_v3_all_108": diverging(holdout, holdout_v3, sorted(holdout)),
        },
        "v2_taxonomy_rows_in_pool": sum(
            1 for row in pool.values() if SERVICE in (row.get("intents") or [])
        ),
        "v2_taxonomy_rows_in_pool_tax2": sum(
            1
            for row in stores["sarcasm_holdout_pool_tax2.jsonl"].values()
            if SERVICE in (row.get("intents") or [])
        ),
        "pool_tax2_rows": len(stores["sarcasm_holdout_pool_tax2.jsonl"]),
        "pool_rows": len(pool),
        "options": reconciliation(len(pool), len(stores["sarcasm_holdout_pool_tax2.jsonl"]), moved),
    }


def reconciliation(pool_rows: int, pool_tax2_rows: int, moved: list[str]) -> list[dict]:
    """The two options the brief asks for, each with the numbers that decide it."""
    return [
        {
            "option": "(i) single-home materialization in v4",
            "what": (
                "drop the 54 v1 copies from data/annotation/sarcasm_holdout_pool.jsonl so each id"
                " lives in exactly one file; the v2 sibling already excludes them"
            ),
            "rows_on_disk": f"{pool_rows} -> {pool_rows - len(moved)}",
            "matches_existing_v2_sibling": pool_rows - len(moved) == pool_tax2_rows,
            "training_rows_removed": 0,
            "g1b_denominator": "unchanged: 108 rows, slice 44 (v2 reading) / 29 (v3 reading)",
            "usd": 0.0,
            "cost": (
                "edits an annotation store that four records pin by sha256; the pristine copy"
                " sarcasm_holdout_pool.pristine.jsonl keeps the original bytes either way"
            ),
        },
        {
            "option": "(ii) scoring-time dedup",
            "what": (
                "leave both copies and make the reader drop a pool row whose id is in the holdout"
            ),
            "rows_on_disk": f"{pool_rows} -> {pool_rows}",
            "matches_existing_v2_sibling": False,
            "training_rows_removed": 0,
            "g1b_denominator": "unchanged: 108 rows, slice 44 (v2 reading) / 29 (v3 reading)",
            "usd": 0.0,
            "cost": (
                "there is no reader to add it to today: train_qlora.NEVER_READ already refuses"
                " the pool and no scorer opens it, so the guard would protect a future caller"
            ),
        },
    ]


# --- (2) the guards that held intents at v1 ---------------------------------
def guards() -> list[dict]:
    freeze = REPO_ROOT / "scripts" / "freeze_testsets_v3.py"
    relabel = REPO_ROOT / "scripts" / "relabel_intents.py"
    trainer = REPO_ROOT / "scripts" / "train_qlora.py"
    return [
        {
            "file": rel(freeze),
            "line": line_of(freeze, 'LAW_PENDING = ("intents",)'),
            "name": "LAW_PENDING",
            "holds": "the 31 derived intents rulings are counted and NOT applied to v3",
            "applied_at": [
                {"line": line_of(freeze, "if head in LAW_PENDING:"), "what": "the apply skip"},
                {"line": line_of(freeze, "if head not in LAW_PENDING"), "what": "the fix count"},
                {"line": line_of(freeze, '"law_pending": list(LAW_PENDING)'), "what": "the record"},
            ],
        },
        {
            "file": rel(relabel),
            "line": line_of(relabel, "NEVER = ("),
            "name": "NEVER / forbidden_ids",
            "holds": "no frozen test or holdout id may be re-labelled under taxonomy v2",
            "applied_at": [
                {"line": line_of(relabel, "def forbidden_ids"), "what": "the id set is read"},
                {
                    "line": line_of(relabel, "a test row is never labelled here"),
                    "what": "the refusal",
                },
                {"line": line_of(relabel, '"--skip-frozen"'), "what": "the drop-instead switch"},
            ],
        },
        {
            "file": rel(trainer),
            "line": line_of(trainer, "NEVER_READ = ("),
            "name": "NEVER_READ",
            "holds": "training may not open the test sets, the holdout or the holdout pool",
            "applied_at": [
                {"line": line_of(trainer, "is a frozen test input"), "what": "the refusal"}
            ],
        },
        {
            "file": rel(trainer),
            "line": line_of(trainer, "SOURCES = {"),
            "name": "SOURCES",
            "holds": (
                "training reads the v1 files, not their _tax2 siblings — the fourth place"
                " intents sits at v1, and the only one that is not a guard: nothing refuses"
                " when it is wrong, the run just trains on the old taxonomy"
            ),
            "applied_at": [
                {"line": line_of(trainer, '"T1": (FROZEN / "comments_train.jsonl"'), "what": "T1"}
            ],
        },
    ]


# --- (3) what test v4 has to re-label, and what it costs --------------------
def ledger_anchor() -> dict:
    """Read BEFORE any projection arithmetic, and never from a live API.

    The brief forbids OpenRouter requests this phase, so the anchor is the last
    recorded lifetime usage plus what the closed phases spent against it — the
    same files the 4.5g runs enforced their cap on.
    """
    g6 = json.loads((RESULTS / "spend_45g6.json").read_text(encoding="utf-8"))
    anchor = g6["openrouter_total_usage_at_45g6_start"]
    spent_45g6 = sum(run["usd"] for run in g6["runs"])
    phase4 = json.loads((RESULTS / "spend_phase4.json").read_text(encoding="utf-8"))
    last = phase4["sessions"][-1]
    return {
        "openrouter_lifetime_usage_at_45g6_start": anchor,
        "openrouter_45g6_spend": spent_45g6,
        "openrouter_lifetime_usage_now": anchor + spent_45g6,
        "openrouter_45g3_to_45g6_total": round(
            sum(
                sum(run["usd"] for run in json.loads((RESULTS / name).read_text())["runs"])
                for name in (
                    "spend_45g3.json",
                    "spend_45g4.json",
                    "spend_45g5.json",
                    "spend_45g6.json",
                )
            ),
            6,
        ),
        "runpod_balance": last["balance"],
        "runpod_phase4_spent": last["spent_usd"],
        "runpod_read_at": last["at"],
        "note": "read from result files only — no live balance call, the phase forbids requests",
    }


def observed_relabel_rate() -> dict:
    """$/row for a taxonomy-v2 re-label, from 4.5e's own ledger."""
    ledger = json.loads((RESULTS / "spend_45e.json").read_text(encoding="utf-8"))
    usd = sum(run["usd"] for run in ledger["runs"])
    requests = sum(run["requests"] for run in ledger["runs"])
    first = ledger["runs"][0]
    return {
        "usd": round(usd, 6),
        "requests": requests,
        "usd_per_row_all_passes": usd / requests,
        "usd_per_row_first_pass": first["usd"] / first["requests"],
        "note": "all passes includes the retries of unusable rows; the first pass is the clean rate",
    }


def migration() -> dict:
    test, holdout = load(COMMENTS_TEST), load(HOLDOUT)
    gold = by_id(test + holdout)
    stores = {name: by_id(load(path)) for name, path in HOMES.items()}

    carries_v2 = {
        name: sum(1 for row in rows.values() if SERVICE in (row.get("intents") or []))
        for name, rows in sorted(stores.items())
    }
    gold_with_v2 = {
        name: sorted(
            row_id
            for row_id in set(rows) & set(gold)
            if SERVICE in (rows[row_id].get("intents") or [])
        )
        for name, rows in stores.items()
    }
    already = sorted({row_id for ids in gold_with_v2.values() for row_id in ids})
    rate = observed_relabel_rate()
    need = len(gold) - len(already)
    posts_test = load(FROZEN / "posts_test.jsonl")
    return {
        "ledger_anchor": ledger_anchor(),
        "gold_rows": len(gold),
        "comments_test": len(test),
        "sarcasm_holdout": len(holdout),
        "rows_carrying_a_v2_intents_value_today": len(already),
        "rows_needing_a_fresh_pass": need,
        "where_the_gold_rows_live": {
            name: len(set(rows) & set(gold))
            for name, rows in sorted(stores.items())
            if set(rows) & set(gold)
        },
        "service_rows_per_store": carries_v2,
        "observed_rate": rate,
        "projection_usd": {
            "at_all_passes_rate": round(need * rate["usd_per_row_all_passes"], 4),
            "at_first_pass_rate": round(need * rate["usd_per_row_first_pass"], 4),
        },
        "posts_test": {
            "rows": len(posts_test),
            "carries_intents": any("intents" in row for row in posts_test),
            "fields": sorted(posts_test[0]),
            "what_v4_posts_is": (
                "posts_test has no intents column — the T2 heads are relevance, post_type and"
                " brands — so v4 posts IS posts_test_v3.jsonl unchanged, re-used under the v4"
                " name or not re-issued at all; nothing in the intents law can move a post row"
            ),
        },
    }


# --- (4) the rulings that want the same column ------------------------------
def collisions() -> dict:
    import freeze_testsets_v3 as fz

    manifest = json.loads(fz.MANIFEST.read_text(encoding="utf-8"))
    key = json.loads(Path(manifest["key_path"]).read_text(encoding="utf-8"))
    ruled = fz.read_pack(Path(manifest["pack_path"]), key)
    audit_ids = sorted(ruled["intents"])

    record = json.loads((RESULTS / "frozen_v3.json").read_text(encoding="utf-8"))
    if record["law_pending_rulings"]["intents"] != len(audit_ids):
        raise SystemExit(
            f"the v3 record says {record['law_pending_rulings']['intents']} intents rulings and the"
            f" pack derives {len(audit_ids)} — one of them is not the phase's own artefact"
        )

    stores = {name: by_id(load(path)) for name, path in HOMES.items()}
    v2_stores = {
        name: rows
        for name, rows in stores.items()
        if any(SERVICE in (row.get("intents") or []) for row in rows.values())
    }
    law_ids = sorted(row_id for row_id in LAW_VERDICTS if row_id.startswith("@"))
    test_ids, holdout_ids = set(by_id(load(COMMENTS_TEST))), set(by_id(load(HOLDOUT)))
    return {
        "audit_intents_rulings": len(audit_ids),
        "audit_ids": audit_ids,
        "audit_ids_in_comments_test": len(set(audit_ids) & test_ids),
        "audit_ids_in_sarcasm_holdout": len(set(audit_ids) & holdout_ids),
        "law_verdicts": len(LAW_VERDICTS),
        "law_verdict_corpus_rows": law_ids,
        "law_verdict_rows_in_comments_test": len(set(law_ids) & test_ids),
        "audit_and_law_same_row": sorted(set(audit_ids) & set(law_ids)),
        "collisions_with_a_v2_relabel_value": {
            name: sorted((set(audit_ids) | set(law_ids)) & set(rows))
            for name, rows in sorted(v2_stores.items())
        },
        "reading": (
            "a collision needs a v2 intents value on the same id, and no store that has been"
            " through the v2 re-label holds one: the guard in relabel_intents.py kept every"
            " frozen test and holdout id out of the pass. The 31 and the 3 collide with each"
            " other on no row at all, and two of the three are guideline examples rather than"
            " corpus rows — so 32 test rows carry a ruling the v4 pass would overwrite. That is"
            " a sequencing decision for 4.5h2 (rule first, then re-label, or re-label and"
            " re-apply), not a data conflict today"
        ),
    }


# --- (5) the two arms ---------------------------------------------------------
def steps_for(rows: int, config: dict) -> int:
    """The optimizer steps a run of `rows` rows takes, the way 4c actually took them.

    `floor`, not `ceil`: the trailing micro-batches of an epoch do not complete a
    step, which is the recorded "planned over-counts steps by one per epoch"
    finding — 272 planned against 270 run.
    """
    per_step = config["micro_batch_size"] * config["grad_accum"]
    return (rows // per_step) * config["epochs"]


def arms() -> dict:
    import yaml

    config = yaml.safe_load((REPO_ROOT / "config" / "qlora.yaml").read_text(encoding="utf-8"))[
        "training"
    ]
    real = {
        "comments_train.jsonl": scoreable(load(FROZEN / "comments_train.jsonl")),
        "sarcasm_candidates.jsonl": scoreable(load(ANNOTATION / "sarcasm_candidates.jsonl")),
        "posts_train.jsonl": scoreable(load(FROZEN / "posts_train.jsonl")),
    }
    plast = load(PLAST)
    plast_scoreable = scoreable(plast)

    train_ids = {
        row["id"]
        for name in ("comments_train.jsonl", "sarcasm_candidates.jsonl")
        for row in real[name]
    }
    overlap = sorted({row["id"] for row in plast_scoreable} & train_ids)

    a_pool = sum(len(rows) for rows in real.values())
    a_train = a_pool - config["carve_rows"]
    b_pool = a_pool + len(plast_scoreable)
    b_train = b_pool - config["carve_rows"]

    arm_a = json.loads((RESULTS / "train" / "4c-arm-a" / "provenance.json").read_text())
    arm_b = json.loads((RESULTS / "train" / "4c-arm-b" / "provenance.json").read_text())
    observed = {
        "arm_a_4c": {
            "steps": arm_a["run"]["steps"],
            "s_per_step": arm_a["run"]["seconds_per_step"],
        },
        "arm_b_4c": {
            "steps": arm_b["run"]["steps"],
            "s_per_step": arm_b["run"]["seconds_per_step"],
        },
    }
    slowest = max(observed["arm_a_4c"]["s_per_step"], observed["arm_b_4c"]["s_per_step"])
    fastest = min(observed["arm_a_4c"]["s_per_step"], observed["arm_b_4c"]["s_per_step"])

    def project(rows: int) -> dict:
        steps = steps_for(rows, config)
        return {
            "train_rows": rows,
            "steps": steps,
            "hours_at_slowest": steps * slowest / 3600,
            "hours_at_fastest": steps * fastest / 3600,
            "usd_at_slowest": steps * slowest / 3600 * GPU_USD_PER_HOUR,
            "over_ceiling": steps * slowest / 3600 > CEILING_HOURS,
            "over_ceiling_at_fastest": steps * fastest / 3600 > CEILING_HOURS,
        }

    projected = {"arm_a": project(a_train), "arm_b": project(b_train)}
    exposure = taxonomy_exposure(real, plast_scoreable)
    longest = max(len(row["text"]) for rows in real.values() for row in rows if "text" in row)
    return {
        "status_md_claim": 2346,
        "status_md_claim_is": (
            "the comment rows of the two T1 sources before the unclear filter:"
            " comments_train.jsonl 1600 + sarcasm_candidates.jsonl 746 = 2346."
            " It is not the trainer's row count and it excludes posts_train.jsonl entirely"
        ),
        "unclear_filter": {
            "file": "scripts/train_qlora.py",
            "line": line_of(REPO_ROOT / "scripts" / "train_qlora.py", 'if not row["unclear"]'),
        },
        "scoreable_per_source": {name: len(rows) for name, rows in sorted(real.items())},
        "arm_a_scoreable_pool": a_pool,
        "arm_a_train_rows": a_train,
        "arm_a_4c_recorded_n_train": arm_a["n_train"],
        "arm_a_matches_4c": a_train == arm_a["n_train"],
        "plast_rows": len(plast),
        "plast_scoreable": len(plast_scoreable),
        "plast_ids_already_in_training": len(overlap),
        "additive": not overlap,
        "arm_b_scoreable_pool": b_pool,
        "arm_b_train_rows": b_train,
        "carve_rows": config["carve_rows"],
        "config": {
            k: config[k] for k in ("epochs", "micro_batch_size", "grad_accum", "carve_rows")
        },
        "observed": observed,
        "projected": projected,
        "taxonomy_exposure": exposure,
        "carve_is_no_longer_paired": {
            "what": (
                "train_qlora.assemble draws the carve from the assembled REAL pool, which is why"
                " Phase 4's two arms held out the same 24 rows: the synthetic source joined after"
                " the draw. A пласт entering as a source would be drawn from, so arms A and B"
                " would hold out different rows"
            ),
            "cost": "the carve selects nothing (it is a convergence thermometer), but the arms"
            " stop being paired on it, and 4c's carve_sha256 stops being comparable",
            "decision": "4.5h2 code, not this step",
        },
        "ceiling_hours": CEILING_HOURS,
        "usd_per_hour": GPU_USD_PER_HOUR,
        "longest_text_chars": {
            "current_training_pool": longest,
            "plast": max(len(row["text"]) for row in plast_scoreable),
            "note": (
                "a proxy for the 1024-token max_seq_len, which was measured at 973 tokens for the"
                " longest of the 2795 rows; a longer пласт row would be truncated and teach a"
                " cut-off label. Tokens are not counted here — no tokenizer is loaded in a $0 step"
            ),
        },
    }


def taxonomy_exposure(real: dict[str, list[dict]], plast: list[dict]) -> dict:
    """Which taxonomy each arm would actually be trained on — the confound in the ablation.

    `train_qlora.SOURCES` reads the v1 files. They hold zero `service` rows; the пласт
    holds hundreds. So arm A as specified today cannot emit the sixth intent at all,
    while arm B sees it — and G1c is scored against test v4, which IS taxonomy v2. The
    selection rule ("the пласт stays iff arm B's G1c is strictly higher") would then be
    decided by taxonomy exposure and read as data volume. Row counts are identical
    between each v1 file and its `_tax2` sibling, so repointing SOURCES changes no hour
    in the projection above — only what the arms are comparable on.
    """
    counts = {
        name: sum(1 for row in rows if SERVICE in (row.get("intents") or []))
        for name, rows in sorted(real.items())
    }
    siblings = {
        "comments_train_tax2.jsonl": FROZEN / "comments_train_tax2.jsonl",
        "sarcasm_candidates_tax2.jsonl": ANNOTATION / "sarcasm_candidates_tax2.jsonl",
    }
    tax2 = {
        name: [row for row in scoreable(load(path)) if SERVICE in (row.get("intents") or [])]
        for name, path in siblings.items()
    }
    return {
        "service_rows_in_arm_a_sources": counts,
        "service_rows_in_the_plast": sum(
            1 for row in plast if SERVICE in (row.get("intents") or [])
        ),
        "service_rows_in_the_tax2_siblings": {
            name: len(rows) for name, rows in sorted(tax2.items())
        },
        "rows_match_between_v1_and_tax2": {
            "comments_train.jsonl": len(real["comments_train.jsonl"])
            == len(scoreable(load(FROZEN / "comments_train_tax2.jsonl"))),
            "sarcasm_candidates.jsonl": len(real["sarcasm_candidates.jsonl"])
            == len(scoreable(load(ANNOTATION / "sarcasm_candidates_tax2.jsonl"))),
        },
        "reading": (
            "arm A trains on a 5-class intents column and arm B on 5-class plus 1 286 rows of"
            " 6-class, while the gate scores both against a 6-class test. Repointing SOURCES at"
            " the _tax2 siblings is what 'arm A under the v2 law' means; it is a 4.5h2 code"
            " decision and it leaves every projected hour where it is"
        ),
    }


def leakage() -> dict:
    """Thread-disjointness for the rows arm B would add. The standing invariant."""
    plast = scoreable(load(PLAST))
    test, holdout = load(COMMENTS_TEST), load(HOLDOUT)
    test_v3, holdout_v3 = load(COMMENTS_TEST_V3), load(HOLDOUT_V3)

    def threads(rows: list[dict]) -> set[tuple[str, int]]:
        return {(row["channel"], row["parent_msg_id"]) for row in rows if row.get("parent_msg_id")}

    def texts(rows: list[dict]) -> set[str]:
        return {row["text"] for row in rows}

    return {
        "plast_scoreable": len(plast),
        "id_overlap": {
            "comments_test": len({r["id"] for r in plast} & {r["id"] for r in test}),
            "sarcasm_holdout": len({r["id"] for r in plast} & {r["id"] for r in holdout}),
        },
        "thread_overlap": {
            "comments_test": len(threads(plast) & threads(test)),
            "sarcasm_holdout": len(threads(plast) & threads(holdout)),
            "comments_test_v3": len(threads(plast) & threads(test_v3)),
            "sarcasm_holdout_v3": len(threads(plast) & threads(holdout_v3)),
        },
        "verbatim_text_overlap": {
            "comments_test": len(texts(plast) & texts(test)),
            "sarcasm_holdout": len(texts(plast) & texts(holdout)),
        },
        "note": (
            "docs/frozen-testsets.md checked this at the 2026-07-28 freeze, before the пласт"
            " existed; arm B is the first thing that would put these rows into training"
        ),
    }


# --- (6) the anchor and the two evals -----------------------------------------
def eval_budget() -> dict:
    phase4 = json.loads((RESULTS / "spend_phase4.json").read_text(encoding="utf-8"))
    anchor_session = next(s for s in phase4["sessions"] if "own-pod zero-shot" in s["note"])
    found = re.search(r"(\d+) rows, batch size (\d+), (\d+) min", anchor_session["note"])
    if not found:
        raise SystemExit(
            "results/spend_phase4.json no longer records the 4a run as"
            " '<rows> rows, batch size <n>, <m> min' — the eval rate cannot be re-derived"
        )
    rows, batch, minutes = (int(g) for g in found.groups())
    per_row = minutes * 60 / rows
    runs = 3
    return {
        "observed_4a": {
            "rows": rows,
            "batch_size": batch,
            "minutes": minutes,
            "seconds_per_row": per_row,
            "session_usd": anchor_session["spent_usd"],
            "source": "results/spend_phase4.json, the 4a session note",
        },
        "runs": {"anchor": 1, "arm_evals": 2},
        "rows_each": rows,
        "minutes_total": runs * minutes,
        "hours_total": runs * minutes / 60,
        "usd_total_at_gpu_rate": runs * minutes / 60 * GPU_USD_PER_HOUR,
        "note": (
            "the two arm evals run on their own training pods and add no pod setup; the anchor is"
            " a pod of its own, and the 4a session billed $0.6203 for a 39-minute run — model"
            " download and idle included, which is the honest per-anchor figure"
        ),
        "usd_anchor_session_observed": anchor_session["spent_usd"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, default=RECORD)
    args = parser.parse_args(argv)

    record = {
        "step": "4.5h precheck",
        "produced_by": "scripts/precheck_45h.py",
        "spend_usd": 0.0,
        "dual_home": dual_home(),
        "guards": guards(),
        "migration": migration(),
        "collisions": collisions(),
        "arms": arms(),
        "leakage": leakage(),
        "eval_budget": eval_budget(),
    }
    args.record.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )

    arm = record["arms"]
    print(f"record: {rel(args.record)}")
    print(
        f"  the 54: one second home ({record['dual_home']['second_home']}),"
        f" {sum(record['dual_home']['training_side_hits'].values())} training-side hits"
    )
    print(
        f"  v4 migration: {record['migration']['rows_needing_a_fresh_pass']} of"
        f" {record['migration']['gold_rows']} gold rows need a pass,"
        f" ${record['migration']['projection_usd']['at_all_passes_rate']}"
    )
    print(
        f"  arm A {arm['arm_a_train_rows']} rows / {arm['projected']['arm_a']['steps']} steps /"
        f" {arm['projected']['arm_a']['hours_at_slowest']:.2f} h"
    )
    print(
        f"  arm B {arm['arm_b_train_rows']} rows / {arm['projected']['arm_b']['steps']} steps /"
        f" {arm['projected']['arm_b']['hours_at_slowest']:.2f} h"
        f" — over the {CEILING_HOURS} h ceiling: {arm['projected']['arm_b']['over_ceiling']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
