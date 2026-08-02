#!/usr/bin/env python3
"""The 97 rows the re-label emptied, asked again with the post they reply to (4.5g).

4.5f measured the class: 97 rows carried an intent under v1 and none under v2, median
length 18 characters, every one of them a reply, and 30.9% of all the drift the taxonomy
does not explain on the rows a gate scores (`results/drop_45f.json`). The cause was in the
instrument — `docs/annotation/comments.md` §Unit lets the annotator read the parent post
and every prompt said "never the thread around it". 4.5g registered the with-post
revisions; this spends ~$0.02 asking these 97 rows again under the corrected one.

What it refuses:

- **a population that names itself.** The 97 are re-derived by `measure_empty_drop`'s own
  functions and then checked against `results/drop_45f.json` — the count *and* the
  distribution of the labels that were lost, because a count can agree by accident.
- **overwriting an operator ruling.** Two of the three 4.5f rulings are in this class by
  construction. They are asked — what the with-post model says about a row the operator
  has already decided is free evidence — and never written. Which rows are held is derived
  from the data (a row the `fixes` history has moved since the run), so a ruling applied
  tomorrow is protected without editing a constant.
- **a row asked without the post it was promised.** Every parent is resolved before the
  first request; a missing one stops the run rather than quietly rendering a prompt with
  no post in it. A parent that exists and has no text is a different state and is rendered
  as such.
- **more than one column moving.** Each rewritten line has to reproduce its staged line
  byte for byte once the previous intents are put back — `relabel.relabelled`, the same
  inverse the paid run was held to.

    python3.11 scripts/relabel_emptied.py --smoke      # fake client, no network, no spend
    python3.11 scripts/relabel_emptied.py --dry-run    # the population and the estimate
    python3.11 scripts/relabel_emptied.py

Writes `results/emptied_with_post_45g.json` and the rows it produced, rewrites the staged
`_tax2` files' intents column, and appends a `fixes` block to `results/relabel_45e.json`.
The drift block there is the re-labeller's own output and is never recomputed.
"""

import argparse
import json
import random
import sys
import threading
from collections import Counter
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))  # the staging convention lives there

import eval_zero_shot as evaluator  # noqa: E402
import measure_empty_drop as drop  # noqa: E402
import relabel_intents as relabel  # noqa: E402
from apply_calibration_rulings import body, index  # noqa: E402
from build_audit_pack import git_state  # noqa: E402
from market_pulse import parents, prompts, zero_shot  # noqa: E402

RESULTS = REPO_ROOT / "results"
POSTS = REPO_ROOT / "data" / "raw" / "posts"
DROP = RESULTS / "drop_45f.json"
RELABEL_RECORD = RESULTS / "relabel_45e.json"
RECORD = RESULTS / "emptied_with_post_45g.json"
ROWS_OUT = RESULTS / "emptied_45g_rows.jsonl"
LEDGER = RESULTS / "spend_45g.json"

PHASE = "45g"
CAP_USD = 1.25
"""The whole 4.5g budget, shared with the up-label precheck. One anchor, one cap: the
precheck's own run reads the same ledger, so the two cannot each spend the full amount."""

TASK = "relabel_intents_v2_with_post"
MODEL = "qwen/qwen3.6-27b"
SEED = 42
MAX_TOKENS = 128
CONCURRENCY = 4

SAMPLE_ROWS = 40
SAMPLE_BAR = 0.90
SAMPLE_RULE = (
    "A seeded {rows}-of-{population} contrastive sample: the v1 label beside the with-post"
    " set, verdict `old` / `new` / `neither`. The batch of {population} is accepted when"
    " rows marked `new` / {rows} >= {bar:.2f}; below the bar all {population} go to the"
    " operator by hand. A row whose with-post set EQUALS its v1 set counts as `new` — the"
    " model recovered the annotator's label, which is the thing being tested — and those"
    " rows are counted separately in the record so the rate is recomputable from this rule"
    " alone. A blank cell counts as not `new`. Registered in"
    " knowledge/decisions/45g-parent-context-and-uplabel.md before the first request."
)


def population(drop_record: Path, run: Path) -> tuple[list[dict], dict]:
    """The 97, re-derived and then checked against the record that measured them."""
    reversed_rows = drop.reversals(run)
    rows = drop.pairs(relabel.SOURCES, reversed_rows)
    emptied = [row for row in rows if row["before"] and not row["after"]]
    recorded = json.loads(drop_record.read_text(encoding="utf-8"))["populations"]["all"]
    lost = Counter(", ".join(row["before"]) for row in emptied)
    if len(emptied) != recorded["emptied"] or dict(lost) != recorded["emptied_from"]:
        raise SystemExit(
            f"{len(emptied)} rows derive as emptied and {relabel.rel(drop_record)} recorded"
            f" {recorded['emptied']}; lost labels {dict(lost)} against"
            f" {recorded['emptied_from']}. The population and the record of it disagree, so"
            " neither says which rows this run is about."
        )
    return emptied, reversed_rows


def with_context(rows: list[dict], posts: dict) -> list[dict]:
    """Each row with its parent post's text, or a stop naming the row that has none."""
    raw = {row["id"]: row for source in relabel.SOURCES.values() for row in relabel.load(source)[0]}
    out = []
    for row in rows:
        try:
            parent = parents.text_for(posts, raw[row["id"]])
        except ValueError as err:
            raise SystemExit(str(err)) from None
        out.append({**row, "parent": parent, "parent_empty": not parent.strip()})
    return out


class Asker:
    """One pinned endpoint, one budget, retries — the with-post prompt and nothing else."""

    def __init__(self, key: str, model: str, tag: str, quantization: str | None, budget):
        self.key, self.model, self.tag, self.quantization = key, model, tag, quantization
        self.budget = budget
        self.lock = threading.Lock()

    def __call__(self, text: str, parent: str) -> str:
        payload = zero_shot.call_with_retry(
            lambda: zero_shot.post(
                "/chat/completions",
                zero_shot.request_body(
                    model=self.model,
                    messages=prompts.build_messages(TASK, text, parent=parent),
                    tag=self.tag,
                    quantization=self.quantization,
                    max_tokens=MAX_TOKENS,
                    seed=SEED,
                ),
                self.key,
            )[0],
            attempts=6,
        )
        with self.lock:
            self.budget.add(float((payload.get("usage") or {}).get("cost") or 0.0))
        return payload["choices"][0]["message"]["content"] or ""


class FakeAsker:
    """`--smoke`: every branch of the write path, no network, no spend.

    The canned answers include a row the model still cannot label, because a smoke run
    whose unusable counter prints zero has not exercised the counter.
    """

    def __init__(self, budget):
        self.budget = budget
        self.calls = 0
        self.lock = threading.Lock()

    def __call__(self, text: str, parent: str) -> str:
        with self.lock:
            self.calls += 1
            unreadable = self.calls % 13 == 0
            empty_again = self.calls % 5 == 0
            self.budget.add(0.0002)
        if unreadable:
            return "I cannot label this."
        if empty_again or prompts.NO_POST_TEXT in parent:
            return '{"intents": []}'
        return '{"intents": ["taste"]}'


def ask_all(rows: list[dict], ask, concurrency: int, on_row) -> list[dict]:
    """One outcome per row, persisted as each lands — a lost row is money spent twice."""
    from concurrent.futures import ThreadPoolExecutor

    def one(row: dict) -> dict:
        try:
            reply = ask(row["text"], row["parent"])
            return {"id": row["id"], "intents": prompts.parse_reply(TASK, reply)["intents"]}
        except prompts.ParseError as err:
            return {"id": row["id"], "intents": None, "unusable": f"parse: {err.reason}"}
        except (zero_shot.ApiError, OSError) as err:
            return {"id": row["id"], "intents": None, "unusable": f"api: {err}"}

    outcomes = []
    with ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool:
        for outcome in pool.map(one, rows):
            outcomes.append(outcome)
            on_row(outcome)
    return outcomes


def answered(path: Path, allowed: set[str]) -> dict[str, list[str]]:
    """Rows a previous invocation wrote — re-checked against this population, not adopted."""
    if not path.exists():
        return {}
    done = {}
    for row in relabel.load(path)[0]:
        if row["id"] not in allowed:
            raise SystemExit(
                f"{relabel.rel(path)} holds {row['id']}, which is not one of the emptied rows —"
                " resuming on top of another run's file would mix two populations"
            )
        done[row["id"]] = row["intents"]
    return done


def apply_all(produced: dict[str, list[str]], held: set[str], staged: dict[str, Path]) -> dict:
    """The answers written into the staged files' intents column, one column and no more."""
    where = index(staged)
    loaded = {key: relabel.load(path) for key, path in staged.items()}
    for key, path in staged.items():
        if body(loaded[key][1]) != path.read_text(encoding="utf-8"):
            raise SystemExit(
                f"{relabel.rel(path)}: its lines do not join back into the file it was read"
                " from, so rewriting it would change lines no answer names."
            )
    touched: dict[str, list[str]] = {}
    applied, unchanged = [], []
    for row_id, intents in produced.items():
        if row_id in held:
            continue
        key, position = where[row_id]
        rows, lines = loaded[key]
        row, line = rows[position], lines[position]
        before, wanted = sorted(row["intents"]), sorted(intents)
        if before == wanted:
            unchanged.append(row_id)
            continue
        lines[position] = relabel.relabelled(row, line, wanted)
        rows[position] = {**row, "intents": wanted}
        touched.setdefault(key, []).append(row_id)
        applied.append(
            {"id": row_id, "file": relabel.rel(staged[key]), "old": before, "new": wanted}
        )
    before_sha = {relabel.rel(staged[key]): digest(staged[key]) for key in touched}
    for key in touched:
        staged[key].write_text(body(loaded[key][1]), encoding="utf-8")
    after_sha = {relabel.rel(staged[key]): digest(staged[key]) for key in touched}
    return {"applied": applied, "unchanged": unchanged, "before": before_sha, "after": after_sha}


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def recovered(rows: list[dict], produced: dict[str, list[str]]) -> dict:
    """What the post bought, split by whether the parent had any text of its own.

    The confound this answers: 23 of the 97 reply to a media-only post, and "the post fixes
    it" is a different claim from "the post fixes it when there is one".
    """
    by_id = {row["id"]: row for row in rows}
    seen = [by_id[row_id] for row_id in produced]
    blocks = {}
    for name, part in (
        ("all", seen),
        ("parent_has_text", [row for row in seen if not row["parent_empty"]]),
        ("parent_is_media_only", [row for row in seen if row["parent_empty"]]),
    ):
        filled = [row for row in part if produced[row["id"]]]
        blocks[name] = {
            "asked": len(part),
            "regained_a_label": len(filled),
            "rate": len(filled) / len(part) if part else 0.0,
            "still_empty": len(part) - len(filled),
            "matches_v1": sum(1 for row in filled if produced[row["id"]] == row["before"]),
        }
    return blocks


def sample(rows: list[dict], produced: dict[str, list[str]], size: int) -> list[dict]:
    """The seeded contrastive draw, in id order so the file does not depend on a dict."""
    pool = sorted((row for row in rows if row["id"] in produced), key=lambda row: row["id"])
    drawn = random.Random(SEED).sample(pool, min(size, len(pool)))
    return sorted(
        (
            {
                "id": row["id"],
                "text": row["text"],
                "intents_v1": row["before"],
                "intents_with_post": sorted(produced[row["id"]]),
            }
            for row in drawn
        ),
        key=lambda row: row["id"],
    )


def main(argv: list[str] | None = None, asker=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, default=RECORD)
    parser.add_argument("--rows-out", type=Path, default=ROWS_OUT)
    parser.add_argument("--ledger", type=Path, default=LEDGER)
    parser.add_argument("--relabel-record", type=Path, default=RELABEL_RECORD)
    parser.add_argument("--drop", type=Path, default=DROP)
    parser.add_argument("--posts", type=Path, default=POSTS)
    parser.add_argument("--concurrency", type=int, default=CONCURRENCY)
    parser.add_argument("--smoke", action="store_true", help="fake client, no network, no spend")
    parser.add_argument("--dry-run", action="store_true", help="the population, then stop")
    args = parser.parse_args(argv)
    if args.smoke:
        # A smoke run produces a record shaped exactly like a real one. The two things it
        # must not do are land where the real one is read from, and write invented labels
        # into files an accepted gate judged — so it stops before the staged files.
        smoke = RESULTS / "smoke"
        args.record = smoke / args.record.name
        args.rows_out = smoke / args.rows_out.name

    emptied, reversed_rows = population(args.drop, args.relabel_record)
    held = {row["id"] for row in emptied if row["id"] in reversed_rows}
    rows = with_context(emptied, parents.load(args.posts))
    media_only = sum(1 for row in rows if row["parent_empty"])
    print(
        f"{len(rows)} emptied rows, population verified against {relabel.rel(args.drop)}"
        f"\n  {media_only} reply to a post with no text of its own"
        f"\n  {len(held)} held by an operator ruling and asked but never written:"
        f" {', '.join(sorted(held)) or '—'}"
    )
    if args.dry_run:
        for row in rows[:5]:
            print(f"  {row['id']:<24} {row['before']} · parent {len(row['parent'])} chars")
        return 0

    produced = answered(args.rows_out, {row["id"] for row in rows})
    pending = [row for row in rows if row["id"] not in produced]
    if produced:
        print(f"resume: {len(produced)} rows already written, {len(pending)} to go")

    pinned = evaluator.ROWS[MODEL]
    endpoint = {"tag": pinned["tag"], "quantization": pinned["quantization"]}
    ledger, key = None, None
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
        print(
            f"ledger: {PHASE} spend so far ${spent_before:.4f}, headroom ${budget.headroom():.4f}"
        )
        ask = Asker(key, MODEL, pinned["tag"], pinned["quantization"], budget)

    args.rows_out.parent.mkdir(parents=True, exist_ok=True)
    handle = args.rows_out.open("a" if produced else "w", encoding="utf-8")

    def persist(outcome: dict) -> None:
        if outcome["intents"] is not None:
            produced[outcome["id"]] = sorted(outcome["intents"])
            handle.write(
                json.dumps({"id": outcome["id"], "intents": produced[outcome["id"]]}) + "\n"
            )
            handle.flush()
        print(f"  {outcome['id']:<24} {outcome.get('unusable') or outcome['intents']}")

    started = datetime.now(UTC).isoformat(timespec="seconds")
    try:
        outcomes = ask_all(pending, ask, args.concurrency, persist)
    finally:
        handle.close()
    if ledger is not None:
        budget.reconcile(zero_shot.total_usage(key) - ledger[relabel.anchor_key(PHASE)])

    unusable = [out for out in outcomes if out["intents"] is None]
    if len(rows) != len(produced) + len(unusable):
        raise SystemExit(
            f"{len(rows)} rows in the population but {len(produced)} written and"
            f" {len(unusable)} unusable — a row that is neither is a row silently left empty"
        )
    staged = {key_: relabel.staged(path) for key_, path in relabel.SOURCES.items()}
    outcome = (
        {"applied": [], "unchanged": [], "before": {}, "after": {}}
        if args.smoke
        else apply_all(produced, held, staged)
    )
    if args.smoke:
        print("--smoke: the staged files are not touched and no `fixes` block is written")
    drawn = sample(rows, produced, SAMPLE_ROWS)

    record = {
        "timestamp": started,
        "task": TASK,
        "model": MODEL,
        "endpoint": endpoint,
        "smoke": bool(args.smoke),
        "prompt_sha256": {
            task: prompts.prompt_sha256(task)
            for task in (TASK, "relabel_intents_v2", "T1v2_with_post")
        },
        "population": {
            "rows": len(rows),
            "source": relabel.rel(args.drop),
            "parent_is_media_only": media_only,
            "held_by_operator_ruling": sorted(held),
        },
        "answers": recovered(rows, produced),
        "unusable": unusable,
        "applied": outcome["applied"],
        "unchanged": outcome["unchanged"],
        "staged_sha256_before": outcome["before"],
        "staged_sha256_after": outcome["after"],
        "check": {
            "rows": len(drawn),
            "bar": SAMPLE_BAR,
            "rule": SAMPLE_RULE.format(rows=SAMPLE_ROWS, population=len(rows), bar=SAMPLE_BAR),
            "seed": SEED,
            "identical_to_v1": sum(
                1 for row in drawn if row["intents_with_post"] == row["intents_v1"]
            ),
            "rows_drawn": drawn,
        },
        "cost": {
            "requests": len(pending),
            "usd": budget.run_spend,
            "phase_spend_usd": budget.phase_spend,
            "cap_usd": CAP_USD,
        },
        "rows_out": relabel.rel(args.rows_out),
        "git": git_state(args.record),
        "note": (
            "The 97 rows 4.5e emptied, asked again under the with-post revision of the"
            " re-label prompt. Rows held by an operator ruling were asked and their answer"
            " recorded, never written. Nothing here recomputes the drift block of"
            " results/relabel_45e.json: that is what the 4.5f calibration judged."
        ),
    }
    if ledger is not None:
        ledger["runs"].append(
            {
                "model": MODEL,
                "timestamp": started,
                "usd": budget.run_spend,
                "requests": len(pending),
                "note": f"{PHASE}: {len(pending)} emptied rows re-asked with the parent post",
            }
        )
        relabel.write_json(args.ledger, ledger)
    relabel.append_record(args.record, record)

    if outcome["applied"]:
        history = json.loads(args.relabel_record.read_text(encoding="utf-8"))
        history.setdefault("fixes", []).append(
            {
                "applied_by": "scripts/relabel_emptied.py",
                "timestamp": started,
                "authority": relabel.rel(args.record),
                "rows": outcome["applied"],
                "staged_sha256_before": outcome["before"],
                "staged_sha256_after": outcome["after"],
                "note": (
                    "The with-post re-label of the rows 4.5e emptied. The drift and churn in"
                    " `runs` are the re-labeller's own output under the old prompt and are"
                    " deliberately NOT recomputed — they are what the 4.5f gate judged. These"
                    " rows are not accepted yet: the 40-row contrastive check in"
                    " results/emptied_with_post_45g.json decides the batch."
                ),
                "git": git_state(args.relabel_record),
            }
        )
        relabel.write_json(args.relabel_record, history)

    print(f"\n{'':<22}{'asked':>7}{'regained':>10}{'rate':>8}{'= v1':>7}")
    for name, block in record["answers"].items():
        print(
            f"  {name:<20}{block['asked']:>7}{block['regained_a_label']:>10}"
            f"{block['rate']:>8.0%}{block['matches_v1']:>7}"
        )
    print(
        f"\n{len(outcome['applied'])} rows rewritten, intents only ·"
        f" {len(outcome['unchanged'])} already matching · {len(held)} held ·"
        f" {len(unusable)} unusable"
    )
    print(f"cost ${budget.run_spend:.4f} of the ${CAP_USD:.2f} 4.5g cap")
    print(f"wrote {relabel.rel(args.record)} — {len(drawn)} rows drawn for the operator check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
