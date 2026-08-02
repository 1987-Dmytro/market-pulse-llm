#!/usr/bin/env python3
"""The 1,912 labelable rows, pre-labelled by the model for the operator to calibrate (4.5g).

[[taxonomy-v2-relabel-and-appetite]] took the whole labelable pool as the up-label appetite
and made it conditional on the ≥90% re-label gate. That gate passed at 100/100, so the pool
is labelled here — as a **precheck**, not as labels. Nothing merges into any train or
candidates file until the three strata of `scripts/build_sitting_pack.py` come back at
≥90% each; until then this file is model output with `annotator: "llm-precheck"` on every
row, and the sitting pack is what decides whether it becomes annotation.

All four comment fields at once, with the parent post, under
`prompts.PRECHECK_PROMPT_V2_WITH_POST`. `unclear` is asked rather than defaulted: 37% of
the labelled corpus carries it and writing `false` into 1,912 rows would coerce the one
field that decides whether a row is scored at all.

What it refuses:

- **a pool that names itself.** The funnel is re-derived by `uplabel_candidates`' own
  functions and every step of it is compared against `results/uplabel_candidates.json` —
  the whole table, not the total, because two exclusions can cancel out.
- **a row asked without the post it was promised.** Every parent is resolved before the
  first request; a missing one stops the run.
- **spending past the estimate.** The 4.5g cap is enforced against the same anchored
  ledger the emptied-row run writes to, so the two cannot each spend the full amount, and
  an estimate over the remaining headroom stops the run instead of trimming the pool.
- **a row that is not a legal annotation row.** Every produced row goes through
  `annotation.check_labels` — the checker the hand-labelled batches pass — so a precheck
  that a later merge could not accept fails here rather than there.
- **a reply that could not be read.** Counted, named, excluded; never coerced to a label.

    python3.11 scripts/precheck_uplabel.py --smoke     # fake client, no network, no spend
    python3.11 scripts/precheck_uplabel.py --dry-run   # the funnel and the cost estimate
    python3.11 scripts/precheck_uplabel.py

Writes `data/annotation/uplabel_precheck_45g.jsonl` and `results/precheck_45g.json`.
"""

import argparse
import json
import sys
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))  # the pinned endpoints live with the eval

import eval_zero_shot as evaluator  # noqa: E402
import relabel_intents as relabel  # noqa: E402
import uplabel_candidates as candidates  # noqa: E402
from build_audit_pack import git_state  # noqa: E402
from relabel_emptied import CAP_USD, LEDGER, PHASE, Asker  # noqa: E402
from market_pulse import annotation, parents, prompts, zero_shot  # noqa: E402
from market_pulse.langid import detect  # noqa: E402

POSTS = REPO_ROOT / "data" / "raw" / "posts"
BATCH = REPO_ROOT / "data" / "annotation" / "uplabel_precheck_45g.jsonl"
RECORD = REPO_ROOT / "results" / "precheck_45g.json"
FUNNEL = REPO_ROOT / "results" / "uplabel_candidates.json"

TASK = "precheck_v2_with_post"
MODEL = "qwen/qwen3.6-27b"
ANNOTATOR = "llm-precheck"
MAX_TOKENS = 128
CONCURRENCY = 4
COMPLETION_TOKENS = 45
"""What one four-field answer costs to generate, for the estimate. The 4.5e re-label
measured ~12 for a one-field answer; four fields and a JSON wrapper is about this."""


def pool(funnel_record: Path) -> tuple[list[dict], dict]:
    """The labelable rows, and the funnel re-checked step by step against its record."""
    rows, steps = candidates.funnel()
    recorded = json.loads(funnel_record.read_text(encoding="utf-8"))["funnel"]
    if steps != recorded:
        differ = {
            name: (steps.get(name), recorded.get(name))
            for name in set(steps) | set(recorded)
            if steps.get(name) != recorded.get(name)
        }
        raise SystemExit(
            f"the funnel no longer reproduces {relabel.rel(funnel_record)}: {differ}. Two"
            " exclusions moving in opposite directions leave the total intact, so the whole"
            " table is compared — this pool is not the one the 4.5d gate sized."
        )
    return rows, steps


def as_batch_row(record: dict, labels: dict) -> dict:
    """One precheck row in the shape `docs/annotation/comments.md` §Schema defines."""
    row = annotation.comment_row(record, detect(record["text"]))
    return {
        **row,
        "sentiment": labels["sentiment"],
        "sarcasm": labels["sarcasm"],
        "intents": labels["intents"],
        "unclear": labels["unclear"],
        "annotator": ANNOTATOR,
        "notes": "",
    }


class FakeAsker:
    """`--smoke`: every branch of the write path, no network, no spend."""

    def __init__(self, budget):
        self.budget = budget
        self.calls = 0
        self.lock = threading.Lock()

    def __call__(self, text: str, parent: str) -> str:
        with self.lock:
            self.calls += 1
            step = self.calls % 7
            self.budget.add(0.0004)
        if step == 0:
            return "I cannot label this."  # the unusable counter has to be exercised
        if step == 1:
            return '{"sentiment": "neutral", "sarcasm": false, "intents": [], "unclear": true}'
        return (
            '{"sentiment": "negative", "sarcasm": true, "intents": ["service"], "unclear": false}'
        )


def ask_all(rows: list[dict], ask, concurrency: int, on_row) -> list[dict]:
    """One outcome per row, persisted as each lands — a lost row is money spent twice."""

    def one(row: dict) -> dict:
        try:
            reply = ask(row["text"], row["parent"])
            return {"id": row["id"], "labels": prompts.parse_reply(TASK, reply)}
        except prompts.ParseError as err:
            return {"id": row["id"], "labels": None, "unusable": f"parse: {err.reason}"}
        except (zero_shot.ApiError, OSError) as err:
            return {"id": row["id"], "labels": None, "unusable": f"api: {err}"}

    outcomes = []
    with ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool_:
        for outcome in pool_.map(one, rows):
            outcomes.append(outcome)
            on_row(outcome)
    return outcomes


def already(path: Path, allowed: set[str]) -> dict[str, dict]:
    """Rows a previous invocation wrote — re-checked against this pool, not adopted."""
    if not path.exists():
        return {}
    done = {}
    for row in relabel.load(path)[0]:
        if row["id"] not in allowed:
            raise SystemExit(
                f"{relabel.rel(path)} holds {row['id']}, which is not in this pool — resuming"
                " on top of another run's file would mix two batches into one"
            )
        done[row["id"]] = row
    return done


def distribution(rows: list[dict]) -> dict:
    """What the model produced, per field — the shape the operator's sample is drawn from."""
    labelled = [row for row in rows if not row["unclear"]]
    return {
        "rows": len(rows),
        "unclear": sum(1 for row in rows if row["unclear"]),
        "unclear_share": sum(1 for row in rows if row["unclear"]) / len(rows) if rows else 0.0,
        "sentiment": dict(Counter(row["sentiment"] for row in rows).most_common()),
        "sarcasm": sum(1 for row in rows if row["sarcasm"]),
        "intents": dict(Counter(intent for row in rows for intent in row["intents"]).most_common()),
        "no_intent": sum(1 for row in rows if not row["intents"]),
        "scoreable": len(labelled),
        "language": dict(Counter(row["language"] for row in rows).most_common()),
    }


def main(argv: list[str] | None = None, asker=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=Path, default=BATCH)
    parser.add_argument("--record", type=Path, default=RECORD)
    parser.add_argument("--funnel", type=Path, default=FUNNEL)
    parser.add_argument("--posts", type=Path, default=POSTS)
    parser.add_argument("--ledger", type=Path, default=LEDGER)
    parser.add_argument(
        "--limit", type=int, default=0, help="first N rows of the pool, for a probe"
    )
    parser.add_argument("--concurrency", type=int, default=CONCURRENCY)
    parser.add_argument("--smoke", action="store_true", help="fake client, no network, no spend")
    parser.add_argument("--dry-run", action="store_true", help="the funnel and the estimate")
    args = parser.parse_args(argv)
    if args.smoke:
        smoke = REPO_ROOT / "results" / "smoke"
        args.record, args.batch = smoke / args.record.name, smoke / args.batch.name

    raw, steps = pool(args.funnel)
    if args.limit:
        raw = raw[: args.limit]
    posts = parents.load(args.posts)
    try:
        rows = [{**record, "parent": parents.text_for(posts, record)} for record in raw]
    except ValueError as err:
        raise SystemExit(str(err)) from None
    media_only = sum(1 for row in rows if not row["parent"].strip())
    print(f"pool {len(rows)} rows, funnel verified against {relabel.rel(args.funnel)}")
    print(f"  {media_only} reply to a post with no text of its own")

    pinned = evaluator.ROWS[MODEL]
    endpoint = {"tag": pinned["tag"], "quantization": pinned["quantization"]}
    ledger, key, estimate = None, None, None
    if asker is not None:
        ask, budget = asker, asker.budget
    elif args.smoke:
        budget = zero_shot.Budget(CAP_USD, CAP_USD)
        ask = FakeAsker(budget)
    else:
        key = evaluator.api_key()
        live = evaluator.verify_pin(key, MODEL, pinned["tag"], pinned["quantization"])
        endpoint |= {"served_quantization": live.get("quantization"), "status": live.get("status")}
        usage_now = zero_shot.total_usage(key)
        ledger = relabel.read_ledger(args.ledger, PHASE, CAP_USD, usage_now)
        relabel.write_json(args.ledger, ledger)  # anchored before the first request, never after
        spent_before = usage_now - ledger[relabel.anchor_key(PHASE)]
        budget = zero_shot.Budget(CAP_USD, CAP_USD, spent_before=spent_before)
        estimate = zero_shot.estimate_cost(
            # the post travels with the row, so the estimate has to charge for both
            rows=[f"{row['parent']}\n{row['text']}" for row in rows],
            prompt_chars=len(prompts.PROMPTS[TASK]),
            pricing=live["pricing"],
            completion_tokens=COMPLETION_TOKENS,
        )
        print(
            f"ledger: {PHASE} spend so far ${spent_before:.4f}, headroom ${budget.headroom():.4f}"
            f"\nestimate: ${estimate['usd']:.4f} over {estimate['requests']} requests"
            f" ({estimate['prompt_tokens']} prompt tokens)"
        )
        if estimate["usd"] > budget.headroom():
            raise SystemExit(
                f"the estimate ${estimate['usd']:.4f} is over the ${budget.headroom():.4f} left"
                f" under the ${CAP_USD:.2f} 4.5g cap. Stop and report — do not trim the pool to"
                " fit, because a precheck of part of it calibrates a different batch."
            )
        ask = Asker(key, MODEL, pinned["tag"], pinned["quantization"], budget, TASK, MAX_TOKENS)
    if args.dry_run:
        print("--dry-run: nothing spent")
        return 0

    produced = already(args.batch, {row["id"] for row in rows})
    pending = [row for row in rows if row["id"] not in produced]
    if produced:
        print(f"resume: {len(produced)} rows already written, {len(pending)} to go")
    args.batch.parent.mkdir(parents=True, exist_ok=True)
    handle = args.batch.open("a" if produced else "w", encoding="utf-8")
    by_id = {row["id"]: row for row in rows}

    def persist(outcome: dict) -> None:
        if outcome["labels"] is not None:
            row = as_batch_row(by_id[outcome["id"]], outcome["labels"])
            if bad := annotation.check_labels(row, "comments"):
                raise SystemExit(
                    f"{row['id']}: the precheck produced a row the annotation checker refuses"
                    f" ({bad}). A batch a later merge could not accept must fail here."
                )
            produced[outcome["id"]] = row
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()
        if len(produced) % 100 == 0 or outcome["labels"] is None:
            print(
                f"  {len(produced):>5}/{len(pending)}  {outcome['id']:<24} {outcome.get('unusable') or ''}"
            )

    started = datetime.now(UTC).isoformat(timespec="seconds")
    try:
        outcomes = ask_all(pending, ask, args.concurrency, persist)
    finally:
        handle.close()
    if ledger is not None:
        budget.reconcile(zero_shot.total_usage(key) - ledger[relabel.anchor_key(PHASE)])

    unusable = [out for out in outcomes if out["labels"] is None]
    if len(rows) != len(produced) + len(unusable):
        raise SystemExit(
            f"{len(rows)} rows in the pool but {len(produced)} written and {len(unusable)}"
            " unusable — a row that is neither is a row silently left unlabelled"
        )
    # written in arrival order for crash safety, re-emitted in the pool's own order
    ordered = [produced[row["id"]] for row in rows if row["id"] in produced]
    args.batch.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in ordered), encoding="utf-8"
    )

    record = {
        "timestamp": started,
        "task": TASK,
        "model": MODEL,
        "endpoint": endpoint,
        "smoke": bool(args.smoke),
        "annotator": ANNOTATOR,
        "prompt_sha256": {task: prompts.prompt_sha256(task) for task in (TASK, "T1v2_with_post")},
        "funnel": steps,
        "pool": {
            "rows": len(rows),
            "parent_is_media_only": media_only,
            "labelled": len(produced),
            "unusable": len(unusable),
        },
        "unusable_rows": unusable,
        "distribution": distribution(ordered),
        "batch": relabel.rel(args.batch),
        "batch_sha256": sha256(args.batch.read_bytes()).hexdigest(),
        "estimate_usd": estimate and estimate["usd"],
        "cost": {
            "requests": len(pending),
            "usd": budget.run_spend,
            "phase_spend_usd": budget.phase_spend,
            "cap_usd": CAP_USD,
        },
        "git": git_state(args.record),
        "note": (
            "A PRECHECK, not annotation. Every row carries annotator `llm-precheck` and"
            " nothing merges into a train or candidates file until the three strata of the"
            " sitting pack come back at >=90% each (4.5g). Each row was asked with the post it"
            " replies to, under the with-post revision registered beside T1v2."
        ),
    }
    if ledger is not None:
        ledger["runs"].append(
            {
                "model": MODEL,
                "timestamp": started,
                "usd": budget.run_spend,
                "requests": len(pending),
                "note": f"{PHASE}: {len(pending)} up-label candidates prechecked, all four fields",
            }
        )
        relabel.write_json(args.ledger, ledger)
    relabel.append_record(args.record, record)

    print(f"\n{len(produced)} rows written · {len(unusable)} unusable")
    shape = record["distribution"]
    print(
        f"  unclear {shape['unclear']} ({shape['unclear_share']:.0%}) · sarcasm {shape['sarcasm']}"
    )
    print(f"  sentiment {shape['sentiment']}")
    print(f"  intents {shape['intents']} · no intent {shape['no_intent']}")
    print(f"cost ${budget.run_spend:.4f} of the ${CAP_USD:.2f} 4.5g cap")
    print(f"wrote {relabel.rel(args.batch)} and {relabel.rel(args.record)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
