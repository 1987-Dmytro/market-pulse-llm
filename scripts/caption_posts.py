#!/usr/bin/env python3
"""What a media-only post says, so that nobody has to judge its comments blind (4.5g2).

`results/post_media_45g2.json` holds the parents in play. 41 of them have no text of their own,
and they turn out to be two different things:

- **21 are pictures.** A vision model describes them, under `prompts.CAPTION_POST_PROMPT` —
  registered beside the label prompts, hashed like them, and pinned in every record here. The
  whole album travels in one request: the price, the date or the question can be on any item.
- **16 are polls.** Their question and options are transcribed straight from Telegram, where
  they have been all along — `raw_store.post_record` stores `message.raw_text`, which a poll
  leaves empty, so the corpus recorded these posts as silent. No model is involved and none is
  recorded; a transcript is not a description and the two are tagged differently in the prompt.

The remaining four (a video, an audio message, two giveaways) get nothing and are named. A guess
would be indistinguishable in the file from a caption somebody could check.

    python3.11 scripts/caption_posts.py --dry-run
    python3.11 scripts/caption_posts.py --model qwen/qwen3.5-flash-02-23 --limit 3 \\
        --out results/smoke/bakeoff.jsonl        # a few rows, to compare two models
    python3.11 scripts/caption_posts.py

Writes `data/annotation/post_captions.jsonl` and `results/captions_45g2.json`.
"""

import argparse
import base64
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
from market_pulse import prompts, zero_shot  # noqa: E402

MANIFEST = REPO_ROOT / "results" / "post_media_45g2.json"
CAPTIONS = REPO_ROOT / "data" / "annotation" / "post_captions.jsonl"
RECORD = REPO_ROOT / "results" / "captions_45g2.json"
LEDGER = REPO_ROOT / "results" / "spend_45g2.json"

PHASE = "45g2"
CAP_USD = 0.75
"""The whole 4.5g2 budget, shared with the re-precheck. One anchor, one cap — declared here
rather than imported from `relabel_emptied`, whose $1.25 and whose anchor belong to 4.5g."""

VISION = {
    "qwen/qwen3.5-flash-02-23": {"tag": "alibaba/fp8", "quantization": "fp8"},
    "mistralai/mistral-small-3.2-24b-instruct": {"tag": "deepinfra/fp8", "quantization": "fp8"},
    "google/gemini-2.5-flash-lite": {"tag": "google-ai-studio", "quantization": None},
}
"""The vision endpoints this may use, pinned like every other endpoint in the repo.

None of them is the model under test: `google/gemma-4-31b-it` never captions and never labels
here, because a description it wrote would make its own eval partly a measure of agreement with
itself. Which one is the default was decided by captioning three real images with each and
reading the output — see the ADR."""

MODEL = "qwen/qwen3.5-flash-02-23"
MAX_TOKENS = 400
"""Enough for the answer the prompt asks for and not enough for the one it forbids. Measured: a
six-image leaflet transcribed item by item runs past 600 tokens and never reaches its summary
sentence, which is what made the prompt say `do not list every item` in the first place."""
CONCURRENCY = 4
SEED = 42
MAX_IMAGES = 6
"""How many of an album's images travel in one request. Ten-item albums exist and the tail is
usually more of the same product; the count actually sent is recorded per post, so a caption
written from six of nine images says so."""


def data_url(path: Path) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def poll_caption(poll: dict) -> str:
    """A poll as one block of text: the question, then its options one per line."""
    return "\n".join([poll["question"], *(f"— {option}" for option in poll["options"])])


def population(manifest: dict) -> tuple[list[dict], list[dict], list[str]]:
    """The posts to caption, the posts to transcribe, and the ones nothing can speak for."""
    images, polls, blind = [], [], []
    for name, entry in manifest["entries"].items():
        if entry["post_has_text"]:
            continue
        if entry["images"]:
            images.append({"name": name, **entry})
        elif entry["poll"]:
            polls.append({"name": name, **entry})
        else:
            blind.append(name)
    return images, polls, sorted(blind)


class Asker:
    """One pinned vision endpoint, one budget, retries — and one description per post."""

    def __init__(self, key, model, tag, quantization, budget):
        self.key, self.model, self.tag, self.quantization = key, model, tag, quantization
        self.budget = budget
        self.lock = threading.Lock()

    def __call__(self, urls: list[str]) -> str:
        payload = zero_shot.call_with_retry(
            lambda: zero_shot.post(
                "/chat/completions",
                zero_shot.request_body(
                    model=self.model,
                    messages=prompts.caption_messages(urls),
                    tag=self.tag,
                    quantization=self.quantization,
                    max_tokens=MAX_TOKENS,
                    seed=SEED,
                ),
                self.key,
                timeout=300.0,
            )[0],
            attempts=6,
        )
        with self.lock:
            self.budget.add(float((payload.get("usage") or {}).get("cost") or 0.0))
        return payload["choices"][0]["message"]["content"] or ""


class FakeAsker:
    """`--smoke`: the write path, no network, no spend. One reply is empty on purpose."""

    def __init__(self, budget):
        self.budget = budget
        self.calls = 0
        self.lock = threading.Lock()

    def __call__(self, urls: list[str]) -> str:
        with self.lock:
            self.calls += 1
            self.budget.add(0.0005)
            return "" if self.calls % 9 == 0 else f"Полиця з молочними продуктами ({len(urls)})."


def caption_all(posts: list[dict], ask, concurrency: int, root: Path, on_row) -> list[dict]:
    """One outcome per post, persisted as each lands — a lost caption is money spent twice."""

    def one(entry: dict) -> dict:
        sent = entry["images"][:MAX_IMAGES]
        try:
            reply = ask([data_url(root / item["file"]) for item in sent])
        except (zero_shot.ApiError, OSError) as err:
            return {"name": entry["name"], "caption": None, "unusable": f"api: {err}"}
        if not reply.strip():
            return {"name": entry["name"], "caption": None, "unusable": "empty reply"}
        return {
            "name": entry["name"],
            "caption": " ".join(reply.split()),
            "images_sent": len(sent),
            "images_available": len(entry["images"]),
        }

    out = []
    with ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool:
        for outcome in pool.map(one, posts):
            out.append(outcome)
            on_row(outcome)
    return out


def record_for(entry: dict, caption: str, kind: str, model: str | None, sent: int) -> dict:
    return {
        "channel": entry["channel"],
        "msg_id": entry["msg_id"],
        "kind": kind,
        "caption": caption,
        "model": model,
        "prompt_sha256": prompts.prompt_sha256(prompts.CAPTION_TASK) if model else None,
        "images": [
            {"file": item["file"], "sha256": item["sha256"]} for item in entry["images"][:sent]
        ],
        "poll": entry["poll"] if kind == "poll" else None,
    }


def main(argv: list[str] | None = None, asker=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--out", type=Path, default=CAPTIONS)
    parser.add_argument("--record", type=Path, default=RECORD)
    parser.add_argument("--ledger", type=Path, default=LEDGER)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--model", default=MODEL, choices=sorted(VISION))
    parser.add_argument("--limit", type=int, default=0, help="first N images, for a comparison")
    parser.add_argument("--only", nargs="+", default=None, help="these posts only, by channel:id")
    parser.add_argument("--concurrency", type=int, default=CONCURRENCY)
    parser.add_argument("--smoke", action="store_true", help="fake client, no network, no spend")
    parser.add_argument("--dry-run", action="store_true", help="the population, then stop")
    args = parser.parse_args(argv)
    if args.smoke:
        smoke = REPO_ROOT / "results" / "smoke"
        args.record, args.out = smoke / args.record.name, smoke / args.out.name

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    images, polls, blind = population(manifest)
    if args.only:
        images = [entry for entry in images if entry["name"] in set(args.only)]
        polls = [entry for entry in polls if entry["name"] in set(args.only)]
    if args.limit:
        images, polls = images[: args.limit], []
    print(
        f"{len(images) + len(polls) + len(blind)} posts with no text of their own"
        f"\n  {len(images)} have images to caption"
        f" ({sum(len(entry['images']) for entry in images)} images,"
        f" {sum(min(len(entry['images']), MAX_IMAGES) for entry in images)} sent)"
        f"\n  {len(polls)} are polls and are transcribed, no model"
        f"\n  {len(blind)} have neither: {', '.join(blind) or '—'}"
    )
    if args.dry_run:
        return 0

    pinned = VISION[args.model]
    endpoint = {"tag": pinned["tag"], "quantization": pinned["quantization"]}
    ledger, key = None, None
    if asker is not None:
        ask, budget = asker, asker.budget
    elif args.smoke:
        budget = zero_shot.Budget(CAP_USD, CAP_USD)
        ask = FakeAsker(budget)
    else:
        key = evaluator.api_key()
        live = evaluator.verify_pin(key, args.model, pinned["tag"], pinned["quantization"])
        endpoint |= {"served_quantization": live.get("quantization"), "status": live.get("status")}
        usage_now = zero_shot.total_usage(key)
        ledger = relabel.read_ledger(args.ledger, PHASE, CAP_USD, usage_now)
        relabel.write_json(args.ledger, ledger)  # anchored before the first request, never after
        spent_before = usage_now - ledger[relabel.anchor_key(PHASE)]
        budget = zero_shot.Budget(CAP_USD, CAP_USD, spent_before=spent_before)
        print(f"ledger: {PHASE} spent ${spent_before:.4f}, headroom ${budget.headroom():.4f}")
        ask = Asker(key, args.model, pinned["tag"], pinned["quantization"], budget)

    started = datetime.now(UTC).isoformat(timespec="seconds")
    outcomes = caption_all(
        images,
        ask,
        args.concurrency,
        args.root,
        lambda out: print(f"  {out['name']:<26} {out.get('unusable') or out['caption'][:90]}"),
    )
    if ledger is not None:
        budget.reconcile(zero_shot.total_usage(key) - ledger[relabel.anchor_key(PHASE)])

    by_name = {entry["name"]: entry for entry in images}
    written = [
        record_for(
            by_name[out["name"]], out["caption"], "image", args.model, out.get("images_sent", 0)
        )
        for out in outcomes
        if out["caption"]
    ]
    written += [record_for(entry, poll_caption(entry["poll"]), "poll", None, 0) for entry in polls]
    written.sort(key=lambda row: (row["channel"], row["msg_id"]))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in written), encoding="utf-8"
    )

    unusable = [out for out in outcomes if not out["caption"]]
    record = {
        "timestamp": started,
        "task": prompts.CAPTION_TASK,
        "model": args.model,
        "endpoint": endpoint,
        "smoke": bool(args.smoke),
        "prompt_sha256": {prompts.CAPTION_TASK: prompts.prompt_sha256(prompts.CAPTION_TASK)},
        "source": relabel.rel(args.manifest),
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
            "max_per_request": MAX_IMAGES,
            "posts_truncated": sorted(
                out["name"]
                for out in outcomes
                if out.get("images_available", 0) > out.get("images_sent", 0)
            ),
        },
        "kinds": dict(Counter(row["kind"] for row in written)),
        "out": relabel.rel(args.out),
        "out_sha256": sha256(args.out.read_bytes()).hexdigest(),
        "cost": {
            "requests": len(images),
            "usd": budget.run_spend,
            "phase_spend_usd": budget.phase_spend,
            "cap_usd": CAP_USD,
        },
        "git": git_state(args.record),
        "note": (
            "What stands in for a media-only post's missing text. `image` rows were written by"
            " the pinned vision model under the registered caption prompt; `poll` rows are"
            " Telegram's own question and options, transcribed, with no model involved — which is"
            " why they carry no model and no prompt hash. The two are tagged differently where"
            " they reach a labelling prompt (prompts.POST_SURROGATE)."
        ),
    }
    if ledger is not None:
        ledger["runs"].append(
            {
                "model": args.model,
                "timestamp": started,
                "usd": budget.run_spend,
                "requests": len(images),
                "note": f"{PHASE}: {len(images)} media-only posts captioned by a vision model",
            }
        )
        relabel.write_json(args.ledger, ledger)
    relabel.append_record(args.record, record)

    print(
        f"\n{len(written)} surrogates written ({record['kinds']}) ·"
        f" {len(unusable)} unusable · {len(blind)} posts left with nothing"
        f"\ncost ${budget.run_spend:.4f} of the ${CAP_USD:.2f} 4.5g2 cap"
        f"\nwrote {relabel.rel(args.out)} and {relabel.rel(args.record)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
