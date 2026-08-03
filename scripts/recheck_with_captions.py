#!/usr/bin/env python3
"""The rows whose post was silent, asked again now that it is not (4.5g2).

Two populations, one instrument change, one ledger:

- **the 424 media-only up-label rows.** 4.5g prechecked all 1,912 with the parent post, but 424
  of them replied to a post whose text was empty, so what they actually got was
  `(this post has no text of its own)`. They are re-asked under the same
  `precheck_v2_with_post` prompt with the image description or the poll question in that slot,
  and the diff per field is the measurement of what the surrogate bought.
- **the emptied rows the quiz did not close.** They go back to the operator by hand, and the
  redo file shows an `intents_model` column beside the v1 label. Nothing here is applied to
  anything: this run produces a column for a human to argue with.

What it refuses:

- **a pool that names itself.** The batch and its media-only class are re-derived and checked
  against `results/precheck_45g.json`.
- **asking half a population with the surrogate and half without.** Every row goes through
  `parents.context`, which is the only place that decides between the post's text, a caption and
  nothing at all; the three counts land in the record, and the caption file is checked against
  what `results/captions_45g2.json` says it wrote before a single request goes out.
- **rewriting a row nobody asked about.** The 1,488 rows outside the media-only class are copied
  from the 4.5g batch line for line, bytes included.
- **a reply that could not be read.** Counted, named, excluded; never coerced to a label.

    python3.11 scripts/recheck_with_captions.py --smoke     # fake client, no network, no spend
    python3.11 scripts/recheck_with_captions.py --dry-run   # the populations and the estimate
    python3.11 scripts/recheck_with_captions.py

Writes `data/annotation/uplabel_precheck_45g2.jsonl`, `results/redo_45g2_rows.jsonl` and
`results/recheck_45g2.json`. The 4.5g batch and its record are read-only here.
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
sys.path.insert(0, str(Path(__file__).resolve().parent))

import eval_zero_shot as evaluator  # noqa: E402
import relabel_intents as relabel  # noqa: E402
from build_audit_pack import git_state  # noqa: E402
from caption_posts import CAP_USD, LEDGER, PHASE  # noqa: E402
from fetch_post_media import media_only, posts_index  # noqa: E402
from relabel_emptied import DROP, RELABEL_RECORD, population  # noqa: E402
from market_pulse import annotation, parents, prompts, zero_shot  # noqa: E402

POSTS = REPO_ROOT / "data" / "raw" / "posts"
CAPTIONS = REPO_ROOT / "data" / "annotation" / "post_captions.jsonl"
CAPTION_RECORD = REPO_ROOT / "results" / "captions_45g2.json"
BATCH_IN = REPO_ROOT / "data" / "annotation" / "uplabel_precheck_45g.jsonl"
BATCH_OUT = REPO_ROOT / "data" / "annotation" / "uplabel_precheck_45g2.jsonl"
PRECHECK = REPO_ROOT / "results" / "precheck_45g.json"
QUIZ_RECORD = REPO_ROOT / "results" / "quiz_rulings_45g2.json"
REDO_ROWS = REPO_ROOT / "results" / "redo_45g2_rows.jsonl"
OUTCOMES = REPO_ROOT / "results" / "recheck_45g2_rows.jsonl"
RECORD = REPO_ROOT / "results" / "recheck_45g2.json"

PRECHECK_TASK = "precheck_v2_with_post"
REDO_TASK = "relabel_intents_v2_with_post"
MODEL = "qwen/qwen3.6-27b"
ANNOTATOR = "llm-precheck"
MAX_TOKENS = 128
CONCURRENCY = 4
SEED = 42
FIELDS = ("sentiment", "sarcasm", "intents", "unclear")


class Asker:
    """One pinned endpoint, one budget, retries — and the surrogate travelling with the row."""

    def __init__(self, key, model, tag, quantization, budget):
        self.key, self.model, self.tag, self.quantization = key, model, tag, quantization
        self.budget = budget
        self.lock = threading.Lock()

    def __call__(self, task: str, row: dict) -> str:
        payload = zero_shot.call_with_retry(
            lambda: zero_shot.post(
                "/chat/completions",
                zero_shot.request_body(
                    model=self.model,
                    messages=prompts.build_messages(
                        task,
                        row["text"],
                        parent=row["parent"],
                        caption=row["caption"],
                        caption_kind=row["caption_kind"] or "image",
                    ),
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
    """`--smoke`: every branch of both write paths, no network, no spend."""

    def __init__(self, budget):
        self.budget = budget
        self.calls = 0
        self.lock = threading.Lock()

    def __call__(self, task: str, row: dict) -> str:
        with self.lock:
            self.calls += 1
            step = self.calls % 7
            self.budget.add(0.0004)
        if step == 0:
            return "I cannot label this."  # the unusable counter has to be exercised
        if task == REDO_TASK:
            return '{"intents": ["taste"]}' if step != 1 else '{"intents": []}'
        if step == 1:
            return '{"sentiment": "neutral", "sarcasm": false, "intents": [], "unclear": true}'
        return '{"sentiment": "positive", "sarcasm": false, "intents": ["taste"], "unclear": false}'


def with_context(rows: list[dict], posts: dict, captions: dict) -> list[dict]:
    """Every row with what its post says, and the name of which of the three that is."""
    out = []
    for row in rows:
        try:
            found = parents.context(posts, captions, row)
        except ValueError as err:
            raise SystemExit(str(err)) from None
        out.append({**row, **found})
    return out


def states(rows: list[dict]) -> dict:
    return dict(Counter(row["state"] for row in rows).most_common())


def ask_all(task: str, rows: list[dict], ask, concurrency: int, parse, on_row) -> list[dict]:
    """One outcome per row, handed to ``on_row`` as it lands — a lost row is money spent twice."""

    def one(row: dict) -> dict:
        try:
            return {"id": row["id"], "labels": parse(prompts.parse_reply(task, ask(task, row)))}
        except prompts.ParseError as err:
            return {"id": row["id"], "labels": None, "unusable": f"parse: {err.reason}"}
        except (zero_shot.ApiError, OSError) as err:
            return {"id": row["id"], "labels": None, "unusable": f"api: {err}"}

    outcomes = []
    with ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool:
        for outcome in pool.map(one, rows):
            outcomes.append(outcome)
            on_row(outcome)
    return outcomes


def answered(path: Path, allowed: dict[str, set[str]]) -> dict[str, dict]:
    """What a previous invocation already paid for — re-checked against these populations.

    Per task, because the two passes ask about overlapping ids under different prompts: the same
    row can be a media-only up-label candidate and one of the 97, and adopting one pass's answer
    for the other would put a one-field reply where four are expected.
    """
    if not path.exists():
        return {task: {} for task in allowed}
    done: dict[str, dict] = {task: {} for task in allowed}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row["task"] not in allowed or row["id"] not in allowed[row["task"]]:
            raise SystemExit(
                f"{relabel.rel(path)} holds {row['id']} for {row['task']}, which is not in that"
                " population — resuming on top of another run's file would mix two of them"
            )
        done[row["task"]][row["id"]] = row["labels"]
    return done


def field_diff(before: dict[str, dict], after: dict[str, dict]) -> dict:
    """Per field: how many of the re-asked rows moved, and where the intents went.

    The number the phase is judged on. `changed_any_field` is rows, the rest are per-field row
    counts, and they do not sum to it — one row can move two fields.
    """
    moved = {field: 0 for field in FIELDS}
    changed = 0
    intents_gained: Counter = Counter()
    intents_lost: Counter = Counter()
    for row_id, new in after.items():
        old = before[row_id]
        any_field = False
        for field in FIELDS:
            same = (
                sorted(old[field]) == sorted(new[field])
                if field == "intents"
                else old[field] == new[field]
            )
            if not same:
                moved[field] += 1
                any_field = True
        intents_gained.update(set(new["intents"]) - set(old["intents"]))
        intents_lost.update(set(old["intents"]) - set(new["intents"]))
        changed += any_field
    return {
        "rows": len(after),
        "changed_any_field": changed,
        "changed_rate": changed / len(after) if after else 0.0,
        "per_field": moved,
        "intents_gained": dict(intents_gained.most_common()),
        "intents_lost": dict(intents_lost.most_common()),
    }


def rewritten(row: dict, line: str, labels: dict) -> str:
    """The row with its four label fields replaced — proved by putting the old ones back.

    `relabel.relabelled`'s discipline, widened from one column to the four this prompt asks for:
    a field-by-field comparison would miss key order, spacing and escaping, and the only
    statement worth making is that this line differs from its source in those four values.
    """
    produced = json.dumps({**row, **labels}, ensure_ascii=False)
    back = {**json.loads(produced), **{field: row[field] for field in FIELDS}}
    if json.dumps(back, ensure_ascii=False) != line:
        raise SystemExit(
            f"{row['id']}: restoring the 4.5g labels does not reproduce the batch line byte for"
            " byte, so this run changed more than the four fields it asked about. Stop and report."
        )
    return produced


def closed_ids(record: Path) -> set[str]:
    """Rows the quiz rulings closed — applied, already matching, or held by an earlier ruling."""
    run = json.loads(record.read_text(encoding="utf-8"))["runs"][-1]
    return {row["id"] for key in ("applied", "unchanged", "held") for row in run[key]}


def main(argv: list[str] | None = None, asker=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-in", type=Path, default=BATCH_IN)
    parser.add_argument("--batch-out", type=Path, default=BATCH_OUT)
    parser.add_argument("--redo-rows", type=Path, default=REDO_ROWS)
    parser.add_argument("--outcomes", type=Path, default=OUTCOMES)
    parser.add_argument("--record", type=Path, default=RECORD)
    parser.add_argument("--precheck", type=Path, default=PRECHECK)
    parser.add_argument("--quiz-record", type=Path, default=QUIZ_RECORD)
    parser.add_argument("--captions", type=Path, default=CAPTIONS)
    parser.add_argument("--caption-record", type=Path, default=CAPTION_RECORD)
    parser.add_argument("--posts", type=Path, default=POSTS)
    parser.add_argument("--ledger", type=Path, default=LEDGER)
    parser.add_argument("--drop", type=Path, default=DROP)
    parser.add_argument("--relabel-record", type=Path, default=RELABEL_RECORD)
    parser.add_argument("--concurrency", type=int, default=CONCURRENCY)
    parser.add_argument("--smoke", action="store_true", help="fake client, no network, no spend")
    parser.add_argument("--dry-run", action="store_true", help="the populations, then stop")
    args = parser.parse_args(argv)
    if args.smoke:
        smoke = REPO_ROOT / "results" / "smoke"
        args.record = smoke / args.record.name
        args.batch_out = smoke / args.batch_out.name
        args.redo_rows = smoke / args.redo_rows.name
        args.outcomes = smoke / args.outcomes.name

    posts_full = posts_index(args.posts)
    posts = {key: record["text"] for key, record in posts_full.items()}
    captions = parents.load_captions(args.captions)
    written = json.loads(args.caption_record.read_text(encoding="utf-8"))["runs"][-1]["kinds"]
    if len(captions) != sum(written.values()):
        raise SystemExit(
            f"{relabel.rel(args.captions)} holds {len(captions)} surrogates and"
            f" {relabel.rel(args.caption_record)} recorded {written}. Asking with a caption file"
            " that is not the one the record describes would render some rows with a description"
            " and some with `no text`, and nothing downstream could tell them apart."
        )

    batch_rows, batch_lines = relabel.load(args.batch_in)
    media = media_only(batch_rows, posts_full)
    recorded = json.loads(args.precheck.read_text(encoding="utf-8"))["runs"][-1]["pool"]
    if len(media) != recorded["parent_is_media_only"] or len(batch_rows) != recorded["rows"]:
        raise SystemExit(
            f"{len(media)} of {len(batch_rows)} rows derive as media-only and"
            f" {relabel.rel(args.precheck)} recorded {recorded['parent_is_media_only']} of"
            f" {recorded['rows']} — this is not the batch that was prechecked."
        )
    reask = with_context(media, posts, captions)

    emptied = population(args.drop, args.relabel_record)
    closed = closed_ids(args.quiz_record)
    labelled = {
        row["id"]: row for source in relabel.SOURCES.values() for row in relabel.load(source)[0]
    }
    redo = with_context(
        [
            {**labelled[row["id"]], "before": row["before"]}
            for row in emptied
            if row["id"] not in closed
        ],
        posts,
        captions,
    )

    print(
        f"{len(reask)} media-only up-label rows to re-ask, of {len(batch_rows)} in the batch"
        f"\n  what their post says now: {states(reask)}"
        f"\n{len(redo)} emptied rows the quiz did not close, of {len(emptied)}"
        f"\n  what their post says now: {states(redo)}"
    )
    if args.dry_run:
        return 0

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
        print(f"ledger: {PHASE} spent ${spent_before:.4f}, headroom ${budget.headroom():.4f}")
        ask = Asker(key, MODEL, pinned["tag"], pinned["quantization"], budget)

    started = datetime.now(UTC).isoformat(timespec="seconds")
    already = answered(
        args.outcomes,
        {PRECHECK_TASK: {row["id"] for row in reask}, REDO_TASK: {row["id"] for row in redo}},
    )
    if any(already.values()):
        print(f"resume: {sum(len(rows) for rows in already.values())} rows already paid for")
    args.outcomes.parent.mkdir(parents=True, exist_ok=True)
    handle = args.outcomes.open("a" if any(already.values()) else "w", encoding="utf-8")
    done = 0

    def persist(task: str):
        def tick(outcome: dict) -> None:
            nonlocal done
            done += 1
            if outcome["labels"] is not None:
                handle.write(json.dumps({"task": task, **outcome}, ensure_ascii=False) + "\n")
                handle.flush()  # on disk before the next row is asked for
            if outcome["labels"] is None or done % 50 == 0:
                print(f"  {done:>5} {outcome['id']:<24} {outcome.get('unusable') or ''}")

        return tick

    pending = {
        PRECHECK_TASK: [row for row in reask if row["id"] not in already[PRECHECK_TASK]],
        REDO_TASK: [row for row in redo if row["id"] not in already[REDO_TASK]],
    }
    try:
        precheck_out = ask_all(
            PRECHECK_TASK,
            pending[PRECHECK_TASK],
            ask,
            args.concurrency,
            dict,
            persist(PRECHECK_TASK),
        )
        done = 0
        redo_out = ask_all(
            REDO_TASK,
            pending[REDO_TASK],
            ask,
            args.concurrency,
            lambda labels: labels["intents"],
            persist(REDO_TASK),
        )
    finally:
        handle.close()
    precheck_out += [
        {"id": row_id, "labels": labels} for row_id, labels in already[PRECHECK_TASK].items()
    ]
    redo_out += [{"id": row_id, "labels": labels} for row_id, labels in already[REDO_TASK].items()]
    if ledger is not None:
        budget.reconcile(zero_shot.total_usage(key) - ledger[relabel.anchor_key(PHASE)])

    # --- the batch: the re-asked rows replaced, every other line copied byte for byte
    at = {row["id"]: position for position, row in enumerate(batch_rows)}
    produced = {out["id"]: out["labels"] for out in precheck_out if out["labels"] is not None}
    replacement = {}
    for row_id, labels in produced.items():
        row, line = batch_rows[at[row_id]], batch_lines[at[row_id]]
        if bad := annotation.check_labels({**row, **labels}, "comments"):
            raise SystemExit(
                f"{row_id}: the re-precheck produced a row the checker refuses ({bad})"
            )
        replacement[row_id] = rewritten(row, line, labels)
    lines = [
        replacement.get(row["id"], line) for row, line in zip(batch_rows, batch_lines, strict=True)
    ]
    args.batch_out.parent.mkdir(parents=True, exist_ok=True)
    args.batch_out.write_text("".join(line + "\n" for line in lines), encoding="utf-8")

    before = {row["id"]: {field: row[field] for field in FIELDS} for row in batch_rows}
    diff = field_diff(before, produced)

    args.redo_rows.parent.mkdir(parents=True, exist_ok=True)
    redo_written = [
        {"id": out["id"], "intents": sorted(out["labels"])}
        for out in redo_out
        if out["labels"] is not None
    ]
    args.redo_rows.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in redo_written),
        encoding="utf-8",
    )

    unusable = {
        "precheck": [out for out in precheck_out if out["labels"] is None],
        "redo": [out for out in redo_out if out["labels"] is None],
    }
    record = {
        "timestamp": started,
        "model": MODEL,
        "endpoint": endpoint,
        "smoke": bool(args.smoke),
        "prompt_sha256": {
            task: prompts.prompt_sha256(task)
            for task in (PRECHECK_TASK, REDO_TASK, prompts.CAPTION_TASK)
        },
        "captions": {
            "file": relabel.rel(args.captions),
            "sha256": sha256(args.captions.read_bytes()).hexdigest(),
            "surrogates": len(captions),
            "kinds": written,
        },
        "precheck": {
            "source": relabel.rel(args.batch_in),
            "source_sha256": sha256(args.batch_in.read_bytes()).hexdigest(),
            "batch": relabel.rel(args.batch_out),
            "batch_sha256": sha256(args.batch_out.read_bytes()).hexdigest(),
            "rows_in_batch": len(batch_rows),
            "re_asked": len(reask),
            "relabelled": len(produced),
            "copied_unchanged": len(batch_rows) - len(replacement),
            "context_states": states(reask),
            "diff": diff,
            "unusable": unusable["precheck"],
        },
        "redo": {
            "population": len(emptied),
            "closed_by_the_quiz": len(closed),
            "rows": len(redo),
            "answered": len(redo_written),
            "context_states": states(redo),
            "rows_out": relabel.rel(args.redo_rows),
            "outcomes": relabel.rel(args.outcomes),
            "unusable": unusable["redo"],
            "note": (
                "An informed model column for the operator to argue with. Nothing here is"
                " applied to any file: the 11/20 quiz failed its bar, so these rows are decided"
                " by hand with the post in front of the operator."
            ),
        },
        "cost": {
            # what this invocation asked for, which after a resume is not the population
            "requests": sum(len(rows) for rows in pending.values()),
            "rows_from_an_earlier_run": sum(len(rows) for rows in already.values()),
            "usd": budget.run_spend,
            "phase_spend_usd": budget.phase_spend,
            "cap_usd": CAP_USD,
        },
        "git": git_state(args.record),
        "note": (
            "The same rows, the same prompts and the same endpoint as 4.5g — the only thing that"
            " moved is what stands in the <post> block for a post with no text of its own. The"
            " 4.5g batch and record are read-only here; this writes a new batch beside them so"
            " that results/sitting_45g_manifest.json still pins the bytes it sealed."
        ),
    }
    if ledger is not None:
        ledger["runs"].append(
            {
                "model": MODEL,
                "timestamp": started,
                "usd": budget.run_spend,
                "requests": sum(len(rows) for rows in pending.values()),
                "note": (
                    f"{PHASE}: {len(pending[PRECHECK_TASK])} media-only rows re-prechecked,"
                    f" {len(pending[REDO_TASK])} redo"
                ),
            }
        )
        relabel.write_json(args.ledger, ledger)
    relabel.append_record(args.record, record)

    print(
        f"\n{len(produced)} of {len(reask)} media-only rows re-asked with the post's surrogate"
        f"\n  {diff['changed_any_field']} changed a field ({diff['changed_rate']:.0%})"
        f" · per field {diff['per_field']}"
        f"\n  intents gained {diff['intents_gained']} · lost {diff['intents_lost']}"
        f"\n{len(redo_written)} of {len(redo)} redo rows carry an informed model column"
        f"\ncost ${budget.run_spend:.4f} of the ${CAP_USD:.2f} 4.5g2 cap"
        f"\nwrote {relabel.rel(args.batch_out)} and {relabel.rel(args.record)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
