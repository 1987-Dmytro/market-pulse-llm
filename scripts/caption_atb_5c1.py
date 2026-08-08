#!/usr/bin/env python3
"""What @atb_market_official's 19 silent posts say. (PAID, cap $0.10.)

The pilot the operator authorised after the yield screen refused to report: read the 19 images
that made the project's anchor retail channel look empty, and find out whether the taxonomy was
in them all along. One channel, one window, one attempt per post.

The instrument is 4.5g2's, deliberately and completely — the same vision model on the same pinned
endpoint, under the same registered `caption_post` prompt, with the whole album travelling in one
request. Step 4 compares a before and an after; a swapped model would make that comparison two
different measurements.

The BUDGET is not 4.5g2's and must never be. Three constants below are this pilot's own: its
phase name, its $0.10 cap and its own ledger file. 4.5g2's anchor holds a $0.75 budget and its
caption file `data/annotation/post_captions.jsonl` is a committed labelling input — spending
against the first or writing over the second would be invisible from inside this script.

One attempt, no retry loop: `zero_shot.call_with_retry` defaults to four and 4.5g2 asked for six,
which inside a $0.10 cap is a six-fold re-bill of exactly the requests that are already failing.
A post whose call fails is named in the record and not re-asked.

    python3.11 scripts/caption_atb_5c1.py --dry-run     # the population, no spend
    python3.11 scripts/caption_atb_5c1.py --smoke       # the write path, fake client, no spend
    python3.11 scripts/caption_atb_5c1.py
"""

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import caption_posts as pattern  # noqa: E402
import eval_zero_shot as evaluator  # noqa: E402
from build_audit_pack import git_state  # noqa: E402

from market_pulse import prompts, zero_shot  # noqa: E402

PHASE = "5c1captions"
CAP_USD = 0.10
LEDGER = REPO_ROOT / "results" / "spend_5c1_captions.json"
"""The pilot's three constants. Not imported, not shared, not derived from another phase's: the
cap the operator wrote in `docs/PROMPT-5c1-captions-pilot.md` is enforced against a balance
anchored in this file and nowhere else."""

MANIFEST = REPO_ROOT / "results" / "post_media_5c1.json"
CAPTIONS = REPO_ROOT / "data" / "annotation" / "captions_5c1" / "atb_captions.jsonl"
RECORD = REPO_ROOT / "results" / "captions_5c1.json"

MODEL = pattern.MODEL
PINNED = pattern.VISION[MODEL]
TASK = prompts.CAPTION_TASK
"""The instrument, shared with 4.5g2 on purpose — see the module docstring."""

ATTEMPTS = 1
"""One paid call per post. Not a default anybody can drift: the test asserts this number."""

CONCURRENCY = 4


def anchor_key() -> str:
    return f"openrouter_total_usage_at_{PHASE}_start"


def read_ledger(path: Path, usage_now: float) -> dict:
    """This pilot's anchor, created before the first request or refused if it is another's."""
    if path.exists():
        ledger = json.loads(path.read_text(encoding="utf-8"))
        if anchor_key() not in ledger:
            raise SystemExit(
                f"{path.name} carries no {anchor_key()} — it is another phase's anchor."
                " Spending against it would enforce this cap on the wrong balance."
            )
        return ledger
    return {
        anchor_key(): usage_now,
        "note": (
            "lifetime OpenRouter usage read at the start of the 5c1 caption pilot, before its"
            " first request. Pilot spend = total_usage now minus this, and the $0.10 cap of"
            " docs/PROMPT-5c1-captions-pilot.md is enforced against that difference. Delete or"
            " regenerate this file and the counter silently restarts at today's usage. Every"
            " other phase's anchor is a different file and is never written here."
        ),
        "cap_usd": CAP_USD,
        "runs": [],
    }


def ask_once(caller):
    """The paid call, made exactly once. The name is the whole point: `call_with_retry` is one
    import away and re-bills the failures it cannot fix."""
    return caller()


class Asker:
    """One pinned vision endpoint, one budget, one attempt — and one description per post."""

    def __init__(self, key: str, budget: zero_shot.Budget) -> None:
        self.key, self.budget = key, budget
        self.lock = pattern.threading.Lock()

    def __call__(self, urls: list[str]) -> str:
        payload = ask_once(
            lambda: zero_shot.post(
                "/chat/completions",
                zero_shot.request_body(
                    model=MODEL,
                    messages=prompts.caption_messages(urls),
                    tag=PINNED["tag"],
                    quantization=PINNED["quantization"],
                    max_tokens=pattern.MAX_TOKENS,
                    seed=pattern.SEED,
                ),
                self.key,
                timeout=300.0,
            )[0]
        )
        with self.lock:
            self.budget.add(float((payload.get("usage") or {}).get("cost") or 0.0))
        return payload["choices"][0]["message"]["content"] or ""


def refuse_to_overwrite(out: Path, record: Path) -> None:
    """Captions are paid evidence: a second run costs money AND destroys the first answer."""
    for path in (out, record):
        if path in (CAPTIONS, RECORD) and path.exists():
            raise SystemExit(
                f"{path.name} already exists — it is what the pilot bought. Re-running would"
                " spend again and overwrite the only copy: give --out/--record another path."
            )


def main(argv: list[str] | None = None, asker=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--out", type=Path, default=CAPTIONS)
    parser.add_argument("--record", type=Path, default=RECORD)
    parser.add_argument("--ledger", type=Path, default=LEDGER)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--concurrency", type=int, default=CONCURRENCY)
    parser.add_argument("--smoke", action="store_true", help="fake client, no network, no spend")
    parser.add_argument("--dry-run", action="store_true", help="the population, then stop")
    args = parser.parse_args(argv)
    refuse_to_overwrite(args.out, args.record)

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    images, polls, blind = pattern.population(manifest)
    sent = sum(min(len(entry["images"]), pattern.MAX_IMAGES) for entry in images)
    print(
        f"{len(images) + len(polls) + len(blind)} posts with no text of their own"
        f"\n  {len(images)} have images to caption"
        f" ({sum(len(entry['images']) for entry in images)} images, {sent} sent)"
        f"\n  {len(polls)} are polls and are transcribed, no model"
        f"\n  {len(blind)} have neither: {', '.join(blind) or '—'}"
    )
    if args.dry_run:
        return 0

    endpoint = {"tag": PINNED["tag"], "quantization": PINNED["quantization"]}
    ledger, key = None, None
    if asker is not None:
        ask, budget = asker, asker.budget
    elif args.smoke:
        budget = zero_shot.Budget(CAP_USD, CAP_USD)
        ask = pattern.FakeAsker(budget)
    else:
        key = evaluator.api_key()
        live = evaluator.verify_pin(key, MODEL, PINNED["tag"], PINNED["quantization"])
        endpoint |= {"served_quantization": live.get("quantization"), "status": live.get("status")}
        usage_now = zero_shot.total_usage(key)
        ledger = read_ledger(args.ledger, usage_now)
        args.ledger.parent.mkdir(parents=True, exist_ok=True)
        args.ledger.write_text(
            json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )  # anchored before the first request, never after
        spent_before = usage_now - ledger[anchor_key()]
        budget = zero_shot.Budget(CAP_USD, CAP_USD, spent_before=spent_before)
        print(f"ledger: {PHASE} spent ${spent_before:.4f}, headroom ${budget.headroom():.4f}")
        ask = Asker(key, budget)

    started = datetime.now(UTC).isoformat(timespec="seconds")
    outcomes = pattern.caption_all(
        images,
        ask,
        args.concurrency,
        args.root,
        lambda out: print(f"  {out['name']:<26} {out.get('unusable') or out['caption'][:90]}"),
    )
    if ledger is not None:
        budget.reconcile(zero_shot.total_usage(key) - ledger[anchor_key()])

    by_name = {entry["name"]: entry for entry in images}
    written = [
        pattern.record_for(
            by_name[out["name"]], out["caption"], "image", MODEL, out.get("images_sent", 0)
        )
        for out in outcomes
        if out["caption"]
    ]
    written += [
        pattern.record_for(entry, pattern.poll_caption(entry["poll"]), "poll", None, 0)
        for entry in polls
    ]
    written.sort(key=lambda row: (row["channel"], row["msg_id"]))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in written), encoding="utf-8"
    )

    unusable = [out for out in outcomes if not out["caption"]]
    record = {
        "timestamp": started,
        "phase": "5c1 — the ATB caption pilot",
        "contract": "docs/PROMPT-5c1-captions-pilot.md step 3",
        "task": TASK,
        "model": MODEL,
        "endpoint": endpoint,
        "smoke": bool(args.smoke),
        "attempts_per_post": ATTEMPTS,
        "prompt_sha256": {TASK: prompts.prompt_sha256(TASK)},
        "source": str(args.manifest.relative_to(REPO_ROOT))
        if args.manifest.is_relative_to(REPO_ROOT)
        else str(args.manifest),
        "population": {
            "media_only_posts": len(images) + len(polls) + len(blind),
            "captioned": sum(1 for row in written if row["kind"] == "image"),
            "transcribed_polls": len(polls),
            "unusable": [out["name"] for out in unusable],
            "no_surrogate_at_all": blind,
        },
        "images": {
            "sent": sum(out.get("images_sent", 0) for out in outcomes),
            "available": sum(len(entry["images"]) for entry in images),
            "max_per_request": pattern.MAX_IMAGES,
            "posts_truncated": sorted(
                out["name"]
                for out in outcomes
                if out.get("images_available", 0) > out.get("images_sent", 0)
            ),
        },
        "kinds": dict(Counter(row["kind"] for row in written)),
        "out": str(args.out.relative_to(REPO_ROOT))
        if args.out.is_relative_to(REPO_ROOT)
        else str(args.out),
        "out_sha256": sha256(args.out.read_bytes()).hexdigest(),
        "cost": {
            "requests": len(images),
            "usd": budget.run_spend,
            "phase_spend_usd": budget.phase_spend,
            "cap_usd": CAP_USD,
            "anchor": str(args.ledger.relative_to(REPO_ROOT))
            if args.ledger.is_relative_to(REPO_ROOT)
            else str(args.ledger),
        },
        "git": git_state(args.record),
        "note": (
            "the 19 posts of @atb_market_official's screen window that carry no text. Same model,"
            " endpoint and registered prompt as 4.5g2 so that step 4's before/after compares one"
            " instrument with itself; the budget is this pilot's own and is anchored in its own"
            " ledger. One attempt per post — a failed call is named, never re-asked."
        ),
    }
    args.record.parent.mkdir(parents=True, exist_ok=True)
    args.record.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if ledger is not None:
        ledger["runs"].append(
            {
                "model": MODEL,
                "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
                "usd": budget.run_spend,
                "requests": len(images),
                "note": f"5c1 caption pilot: {len(images)} media-only ATB posts captioned",
            }
        )
        args.ledger.write_text(
            json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    print(
        f"\n{record['population']['captioned']} captioned,"
        f" {len(unusable)} unusable · ${budget.run_spend:.4f} of ${CAP_USD:.2f}"
        f"\nwrote {record['out']} and {args.record.name}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
