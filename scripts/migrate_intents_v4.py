#!/usr/bin/env python3
"""The 508 gold rows' `intents`, re-asked under taxonomy v2 — the paid half of test v4.

SPEC amendment 3.9 (3): v4 is v3 plus an intents migration pass over the frozen comment
gold, with the operator's own rulings re-applied on top afterwards. This is the pass. It
is a script of its own rather than a fourth `--phase` of `scripts/relabel_intents.py`,
and that is the whole design:

- **the guard that forbids this stays where it is.** `relabel_intents.NEVER` refuses every
  frozen test and holdout id, which is exactly these 508 rows, and it has held since 4.5d.
  Widening it for one authorised pass would retire it for every later one. So the
  permission is written here instead, and inverted: :func:`allowed` is the *only* set this
  script will label, read out of the two v3 files, and a drawn row outside it stops the run.
- **one column moves.** The request asks for `intents` alone
  (`prompts.relabel_intents_v2_with_post`), and every produced line is proved by putting
  the v3 intents back: unless it then reproduces the v3 line byte for byte, the run stops.
  `sentiment`, `sarcasm`, `unclear` and `text` cannot move through a path that never
  carries them.
- **the parent post travels with the row.** Gold was annotated under
  `docs/annotation/comments.md` §Unit, which allows the parent post; 4.5f measured what
  asking without it costs (97 rows emptied, `results/drop_45f.json`). Scoring gold written
  one way against a pass run the other way would charge the difference to the model.
- **a row that comes back unreadable keeps its v3 intents and is named.** Never coerced to
  `[]`, which is the majority answer and would flatter the drift.

    python3.11 scripts/migrate_intents_v4.py --smoke
    python3.11 scripts/migrate_intents_v4.py --dry-run
    python3.11 scripts/migrate_intents_v4.py

Writes `results/migration_45h2_rows.jsonl` (the produced lines) and appends to
`results/migration_45h2.json`. It writes no frozen file — `scripts/freeze_testsets_v4.py`
is what turns these rows into v4.
"""

import argparse
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed
sys.path.insert(0, str(Path(__file__).resolve().parent))  # the pinned endpoints live with the eval

import eval_zero_shot as evaluator  # noqa: E402
import relabel_intents as relabel  # noqa: E402

from market_pulse import parents, prompts, zero_shot  # noqa: E402

FROZEN = REPO_ROOT / "data" / "frozen"
ANNOTATION = REPO_ROOT / "data" / "annotation"
RESULTS = REPO_ROOT / "results"

GOLD = (FROZEN / "comments_test_v3.jsonl", FROZEN / "sarcasm_holdout_v3.jsonl")
"""The two v3 comment files v4 derives from. `posts_test` carries no `intents` column at
all — the T2 heads are relevance, post_type and brands — so no post row can move here."""

RAW_POSTS = REPO_ROOT / "data" / "raw" / "posts"
CAPTIONS = ANNOTATION / "post_captions.jsonl"
LEDGER = RESULTS / "spend_45h2.json"
RECORD = RESULTS / "migration_45h2.json"
ROWS_OUT = RESULTS / "migration_45h2_rows.jsonl"

PHASE = "45h2"
CAP_USD = 0.30
"""`docs/PROMPT-4.5h2.md`: migration pass <= $0.30, against a projection of $0.0869."""

TASK = "relabel_intents_v2_with_post"
"""Operator decision, 2026-08-04. The contract said "T1v2.1-with-parent-post"; the only
registered prompt of that family is `precheck_v2.1_with_post`, and revision v2.1 failed
its own pre-registered gate (preserved 20/58 against v2's 58/58,
`results/v2ctx_probe_results.json` and the 4.5g3 record). This one asks for `intents`
alone, carries the same v2 law that no gate killed, and takes the parent post."""

MODEL = relabel.MODEL
SEED = relabel.SEED
MAX_TOKENS = relabel.MAX_TOKENS
CONCURRENCY = relabel.DEFAULT_CONCURRENCY


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def allowed() -> dict[str, tuple[dict, str]]:
    """``id -> (row, its v3 line)`` for the 508 rows this pass may label, and nothing else.

    Read from the files rather than listed: a hand-kept id list is a second source of
    truth, and the one thing this script must not get wrong is *which* rows it is
    permitted to touch.
    """
    found: dict[str, tuple[dict, str]] = {}
    for path in GOLD:
        rows, lines = relabel.load(path)
        for row, line in zip(rows, lines):
            if row["id"] in found:
                raise SystemExit(f"{row['id']} is in two gold files — v4 could not say which")
            found[row["id"]] = (row, line)
    return found


class Asker:
    """One pinned endpoint, one budget, the parent post — and nothing else to spend on."""

    def __init__(self, key, model, tag, quantization, budget, posts, captions):
        self.key, self.model, self.tag, self.quantization = key, model, tag, quantization
        self.budget, self.posts, self.captions = budget, posts, captions
        self.lock = threading.Lock()

    def __call__(self, row: dict) -> dict:
        context = parents.context(self.posts, self.captions, row)
        body = zero_shot.request_body(
            model=self.model,
            messages=prompts.build_messages(TASK, row["text"], **parents.post_kwargs(context)),
            tag=self.tag,
            quantization=self.quantization,
            max_tokens=MAX_TOKENS,
            seed=SEED,
        )
        payload = zero_shot.call_with_retry(
            lambda: zero_shot.post("/chat/completions", body, self.key)[0],
            attempts=relabel.RETRY_ATTEMPTS,
        )
        with self.lock:
            self.budget.add(float((payload.get("usage") or {}).get("cost") or 0.0))
        return payload | {"post_state": context["state"]}


class FakeAsker:
    """The smoke client: every branch of the write path, no network, no spend."""

    def __init__(self, budget, posts, captions):
        self.budget, self.posts, self.captions = budget, posts, captions
        self.calls = 0
        self.lock = threading.Lock()

    def __call__(self, row: dict) -> dict:
        context = parents.context(self.posts, self.captions, row)
        prompts.build_messages(TASK, row["text"], **parents.post_kwargs(context))  # same refusals
        with self.lock:
            self.calls += 1
            bad = self.calls % 17 == 0  # a reply that is not an answer, so the counter is exercised
            self.budget.add(0.0001)
        reply = '{"intents": ["service"]}' if "розіграш" in row["text"] else '{"intents": []}'
        return {
            "choices": [{"message": {"content": "I cannot label this." if bad else reply}}],
            "usage": {"cost": 0.0001, "prompt_tokens": 700, "completion_tokens": 12},
            "post_state": context["state"],
        }


def ask_one(row: dict, ask) -> dict:
    """One outcome for one row: the new intents, or the reason there are none."""
    try:
        payload = ask(row)
        content = payload["choices"][0]["message"]["content"] or ""
        return {
            "id": row["id"],
            "intents": prompts.parse_reply(TASK, content)["intents"],
            "post_state": payload.get("post_state"),
        }
    except prompts.ParseError as err:
        return {"id": row["id"], "intents": None, "unusable": f"parse: {err.reason}"}
    except (zero_shot.ApiError, OSError) as err:
        return {"id": row["id"], "intents": None, "unusable": f"api: {err}"}


def ask_all(rows: list[dict], ask, concurrency: int, on_row) -> list[dict]:
    """One outcome per row, in row order, each persisted the moment it lands.

    Not `relabel_intents.ask_all`: that one hands its worker ``row["text"]``, and this
    pass needs the whole row to find the post it replies to. ``BudgetExceeded`` is not
    caught anywhere below — the cap ends the run, it is not one more failed row.
    """
    outcomes = []
    with ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool:
        for index, outcome in enumerate(pool.map(lambda row: ask_one(row, ask), rows), start=1):
            outcomes.append(outcome)
            on_row(index, outcome)
    return outcomes


def drift(pairs, outcomes: list[dict], posts: dict, captions: dict) -> dict:
    """What the pass moved, against the v3 values it is replacing.

    The post state is recomputed from the corpus rather than carried through the outcome:
    it is a deterministic property of the row, it costs nothing, and a resumed run has no
    outcome to carry it on — a counter that goes blank on resume would read as "no post".
    """
    scored = [out for out in outcomes if out["intents"] is not None]
    added: dict[str, int] = {}
    removed: dict[str, int] = {}
    changed = service = 0
    for out in scored:
        old, new = set(pairs[out["id"]][0]["intents"]), set(out["intents"])
        for label in new - old:
            added[label] = added.get(label, 0) + 1
        for label in old - new:
            removed[label] = removed.get(label, 0) + 1
        changed += old != new
        service += "service" in new
    states: dict[str, int] = {}
    for out in scored:
        state = parents.context(posts, captions, pairs[out["id"]][0])["state"]
        states[state] = states.get(state, 0) + 1
    return {
        "rows": len(outcomes),
        "scored": len(scored),
        "unusable": [out for out in outcomes if out["intents"] is None],
        "changed": changed,
        "changed_rate": changed / len(scored) if scored else 0.0,
        "service_rows": service,
        "service_prevalence": service / len(scored) if scored else 0.0,
        "labels_added": dict(sorted(added.items(), key=lambda kv: -kv[1])),
        "labels_removed": dict(sorted(removed.items(), key=lambda kv: -kv[1])),
        "post_states": dict(sorted(states.items())),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows-out", type=Path, default=None)
    parser.add_argument("--record", type=Path, default=None)
    parser.add_argument("--ledger", type=Path, default=LEDGER)
    parser.add_argument("--model", default=MODEL, choices=sorted(evaluator.ROWS))
    parser.add_argument("--concurrency", type=int, default=CONCURRENCY)
    parser.add_argument("--max-run-usd", type=float, default=CAP_USD)
    parser.add_argument("--smoke", action="store_true", help="fake client, no network, no spend")
    parser.add_argument("--dry-run", action="store_true", help="draw and render, then stop")
    parser.add_argument("--resume", action="store_true", help="keep what is on disk, ask the rest")
    args = parser.parse_args(argv)

    smoke_dir = RESULTS / "smoke"
    args.record = args.record or (smoke_dir / RECORD.name if args.smoke else RECORD)
    args.rows_out = args.rows_out or (smoke_dir / ROWS_OUT.name if args.smoke else ROWS_OUT)

    pairs = allowed()
    posts = parents.load(RAW_POSTS)
    captions = parents.load_captions(CAPTIONS)
    rows = [row for row, _ in pairs.values()]
    print(f"{len(rows)} gold rows drawn from {', '.join(rel(p) for p in GOLD)}")
    if args.dry_run:
        for row in rows[:3]:
            context = parents.context(posts, captions, row)
            message = prompts.build_messages(TASK, row["text"], **parents.post_kwargs(context))
            print(f"\n--- {row['id']} · {context['state']} · v3 intents {row['intents']}")
            print(message[0]["content"][-400:])
        states: dict[str, int] = {}
        for row in rows:
            state = parents.context(posts, captions, row)["state"]
            states[state] = states.get(state, 0) + 1
        print(f"\nevery row renders · post states {dict(sorted(states.items()))}")
        return 0

    if args.smoke:
        budget = zero_shot.Budget(CAP_USD, args.max_run_usd)
        ask, ledger, key = FakeAsker(budget, posts, captions), None, None
        endpoint = {"tag": "—", "quantization": None}
    else:
        key = evaluator.api_key()
        pinned = evaluator.ROWS[args.model]
        live = evaluator.verify_pin(key, args.model, pinned["tag"], pinned["quantization"])
        endpoint = {
            "tag": pinned["tag"],
            "quantization": pinned["quantization"],
            "served_quantization": live.get("quantization"),
            "status": live.get("status"),
        }
        usage_now = zero_shot.total_usage(key)
        ledger = relabel.read_ledger(args.ledger, PHASE, CAP_USD, usage_now)
        relabel.write_json(args.ledger, ledger)  # anchored before the first request, never after
        spent_before = usage_now - ledger[relabel.anchor_key(PHASE)]
        budget = zero_shot.Budget(CAP_USD, args.max_run_usd, spent_before=spent_before)
        print(
            f"ledger: {PHASE} spend so far ${spent_before:.4f}, headroom ${budget.headroom():.4f}"
        )
        ask = Asker(key, args.model, pinned["tag"], pinned["quantization"], budget, posts, captions)

    produced = relabel.already_done(args.rows_out, pairs) if args.resume else {}
    pending = [row for row in rows if row["id"] not in produced]
    if produced:
        print(f"resume: {len(produced)} rows already written and re-checked, {len(pending)} to go")

    args.rows_out.parent.mkdir(parents=True, exist_ok=True)
    handle = args.rows_out.open("a" if produced else "w", encoding="utf-8")

    def persist(index: int, outcome: dict) -> None:
        """On disk before the next row is asked for — a lost row is money spent twice."""
        row, line = pairs[outcome["id"]]
        if outcome["intents"] is not None:
            produced[outcome["id"]] = relabel.relabelled(row, line, outcome["intents"])
            handle.write(produced[outcome["id"]] + "\n")
            handle.flush()
        print(
            f"  {index:>4}/{len(pending)} {outcome['id']:<24}"
            f" {outcome.get('unusable') or outcome['intents']}"
        )

    started = datetime.now(UTC).isoformat(timespec="seconds")
    try:
        outcomes = ask_all(pending, ask, args.concurrency, persist)
    finally:
        handle.close()
    # written in arrival order for crash safety, re-emitted in the gold files' own order
    args.rows_out.write_text(
        "\n".join(produced[row["id"]] for row in rows if row["id"] in produced) + "\n",
        encoding="utf-8",
    )

    if ledger is not None:
        budget.reconcile(zero_shot.total_usage(key) - ledger[relabel.anchor_key(PHASE)])
    unusable = [out for out in outcomes if out["intents"] is None]
    if len(rows) != len(produced) + len(unusable):
        raise SystemExit(
            f"{len(rows)} rows drawn but {len(produced)} written and {len(unusable)} unusable —"
            " a row that is neither is a row silently left on the old taxonomy"
        )
    settled = [
        {"id": row["id"], "intents": json.loads(produced[row["id"]])["intents"]}
        for row in rows
        if row["id"] in produced
    ] + unusable
    scored = len(pending) - len(unusable)
    record = {
        "timestamp": started,
        "step": "4.5h2 intents migration",
        "task": TASK,
        "testset_version": "v4",
        "model": args.model,
        "endpoint": endpoint,
        "smoke": args.smoke,
        "sources": {rel(p): sha256(p.read_bytes()).hexdigest() for p in GOLD},
        "seed": SEED,
        "prompt_sha256": {TASK: prompts.prompt_sha256(TASK)},
        "git": evaluator.git_state(),
        "drift": drift(pairs, settled, posts, captions),
        "accounting": {
            "gold_rows": len(rows),
            "written": len(produced),
            "unusable": len(unusable),
            "unusable_keep_v3": [out["id"] for out in unusable],
        },
        "cost": {
            "requests": len(pending),
            "usd": budget.run_spend,
            "usd_per_row": budget.run_spend / scored if scored else 0.0,
            "phase_spend_usd": budget.phase_spend,
            "cap_usd": CAP_USD,
        },
        "rows_out": rel(args.rows_out),
        "note": (
            "Intents only; every other column is byte-identical to its v3 line. These rows are"
            " an input to scripts/freeze_testsets_v4.py, not gold: the 31 audit rulings and the"
            " operator's law verdict are applied ON TOP of them there (amendment 3.9 (3))."
        ),
    }
    if ledger is not None:
        ledger["runs"].append(
            {
                "model": args.model,
                "timestamp": started,
                "usd": budget.run_spend,
                "requests": len(pending),
                "note": f"{PHASE}: {len(pending)} gold rows re-asked for `intents` under {TASK}",
            }
        )
        relabel.write_json(args.ledger, ledger)
    relabel.append_record(args.record, record)

    found = record["drift"]
    print(f"\nscored {found['scored']} · unusable {len(found['unusable'])}")
    print(f"  changed        {found['changed']:>4}  {found['changed_rate']:.1%}")
    print(f"  carry `service`{found['service_rows']:>4}  {found['service_prevalence']:.1%}")
    print(f"  added   {json.dumps(found['labels_added'], ensure_ascii=False)}")
    print(f"  removed {json.dumps(found['labels_removed'], ensure_ascii=False)}")
    print(f"  posts   {json.dumps(found['post_states'], ensure_ascii=False)}")
    cost = record["cost"]
    print(f"cost: ${cost['usd']:.4f} over {cost['requests']} requests of ${CAP_USD:.2f}")
    print(f"\nwrote {rel(args.rows_out)} ({len(produced)} rows) and {rel(args.record)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
