#!/usr/bin/env python3
"""Captions from the project's own Gemma 4, on the serverless endpoint. (PAID — see --session.)

SPEC amendment 3.13 retires the paid API caption instrument: captions come from the NF4 BASE at
the pinned revision with the ADAPTER OFF, greedy, batch 1, under its own registered prompt
`caption_post_gm4`. 3.14 fixes where that runs — the endpoint srv-2d proved, not a pod. This is
the driver for both sessions the amendment pre-registers, vis-b and vis-c.

What it does NOT do, and each omission is somebody's expensive evening:

- **No default endpoint id.** A caption run against whatever id was last in a shell variable is
  a run against an unknown configuration. `--endpoint-id` or `$RUNPOD_CAPTION_ENDPOINT`, and a
  refusal otherwise.
- **No retries.** `zero_shot.call_with_retry` defaults to four and a serverless worker bills
  while it fails; a slice whose job errors is named in the record and not re-asked.
- **No shared ledger.** Three constants below are this contract's own — its phase name, the
  caps SPEC 3.13 (4) wrote, and its own ledger file. `relabel.read_ledger` renders
  `docs/PROMPT-5.c1captions.md` inside a money record for any 5c1 phase name, which is a path
  that does not exist; `scripts/caption_atb_5c1.py` writes its own anchor instead and this
  copies that, not the helper.
- **No hidden model swap.** The worker is asked what it loaded and the run stops before the
  first paid caption unless it answers CAPTION, `base-no-adapter`, and the same
  `caption_post_gm4` sha this checkout holds.

The pictures travel INSIDE the job as base64 data URLs, exactly as the API instrument encoded
them. `data/annotation/**` is gitignored, so the media cannot ride to the worker on the network
volume with the weights — the volume stays what srv-2d made it, the dump and log channel. That
puts RunPod's documented payload ceiling on the critical path: **/run is 10 MB**, and one ATB
post at six images measures 3.68 MB encoded. Slices are packed against
:data:`MAX_PAYLOAD_MB` and a post is never split.

    PYTHONPATH=src python3 scripts/caption_gm4_5c1.py --scope atb19 --dry-run
    PYTHONPATH=src python3 scripts/caption_gm4_5c1.py --scope atb19 --smoke
    PYTHONPATH=src python3 scripts/caption_gm4_5c1.py --scope atb19 --endpoint-id <id>
"""

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import caption_posts as pattern  # noqa: E402
import runpod_guard as guard  # noqa: E402
from build_audit_pack import git_state  # noqa: E402

from market_pulse import local_llm, prompts, serving  # noqa: E402
from market_pulse.zero_shot import ApiError  # noqa: E402

PHASE = "5c1vis"
SESSIONS = {"vis-b": 1.00, "vis-c": 1.50}
LEDGER = REPO_ROOT / "results" / "spend_5c1_vis.json"
"""This contract's three constants. The caps are SPEC amendment 3.13 (4)'s, transcribed rather
than chosen: vis-b buys the smoke, the rate measure, the 19-post re-pilot and the bridge; vis-c
buys the remaining 232 posts. One ledger, one anchor key per session, and neither may be
regenerated — delete it and the counter silently restarts at today's balance."""

MANIFEST = REPO_ROOT / "results" / "post_media_5c1.json"
OUT_DIR = REPO_ROOT / "data" / "annotation" / "captions_5c1"

TASK = prompts.CAPTION_TASK_GM4
SOURCE = "gm4-nf4-base"
"""The `caption_source` every row this script writes carries (SPEC amendment 3.13 (3))."""

MAX_IMAGES = pattern.MAX_IMAGES
"""Six, the same as the API instrument sent. Not re-decided: the 3.13 (4) bridge compares GM4
against qwen on identical posts, and a different number of pictures per post would make it a
comparison of two inputs as well as two models."""

MAX_PAYLOAD_MB = 8.0
"""The slice budget, under RunPod's documented 10 MB `/run` ceiling.

Measured on this manifest: the largest six-image post encodes to 3.68 MB, the median to 2.9 MB.
So a slice is two or three posts and the headroom absorbs the JSON overhead. Exceeding the
ceiling fails the job, not the request — on a billed endpoint, at the smoke."""

ENDPOINT_ENV = "RUNPOD_CAPTION_ENDPOINT"
JOB_TIMEOUT_S = 1800.0
JOB_TTL_S = 3600.0
"""Seconds. `serving.execution_policy` is the one place they become milliseconds."""


def anchor_key(session: str) -> str:
    return f"runpod_balance_at_{PHASE}_{session}_start"


def read_ledger(path: Path, session: str, cap: float, balance_now: float) -> dict:
    """This session's anchor, created before the first job or refused if it is another's."""
    ledger = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    key = anchor_key(session)
    if key not in ledger:
        ledger[key] = balance_now
        ledger[f"{PHASE}_{session}_cap_usd"] = cap
        ledger.setdefault("gpu_sessions", [])
        ledger["gpu_note"] = (
            "RunPod account balance read before the first caption job of a 5c1 vis session."
            " Session spend = its own anchor minus the balance now, enforced against the cap"
            f" SPEC amendment 3.13 (4) pre-registered ({', '.join(f'{s} ${c:.2f}' for s, c in SESSIONS.items())})."
            " The Phase 4 cap is enforced separately against results/spend_phase4.json, and"
            " neither anchor may be regenerated."
        )
    return ledger


def spend_now(ledger: dict, session: str) -> tuple[float, float]:
    """(balance, spend) for this session. The delta is a FLOOR — RunPod settles it late."""
    balance = guard.balance()
    return balance, float(ledger[anchor_key(session)]) - balance


def albums(entries: list[dict], root: Path) -> list[dict]:
    """One post → its images as data URLs, capped at :data:`MAX_IMAGES`, with the sent bytes."""
    out = []
    for entry in entries:
        sent = entry["images"][:MAX_IMAGES]
        urls = [pattern.data_url(root / item["file"]) for item in sent]
        out.append(
            {
                "name": entry["name"],
                "urls": urls,
                "images_sent": len(sent),
                "images_available": len(entry["images"]),
                # The worker hashes exactly this to key its dump row; the record carries it so
                # a dump recovered on its own can be matched back to posts.
                "sha8": sha256(serving.album_key(urls).encode("utf-8")).hexdigest()[:8],
                "bytes": sum(len(url) for url in urls),
            }
        )
    return out


def slices(packed: list[dict], budget_mb: float) -> list[list[dict]]:
    """Whole posts packed into jobs under a byte budget. A post is never split across jobs.

    An album is one request by construction (`prompts.caption_messages_gm4`): the price, the
    date or the poll question can be on any picture of it. So the packing unit is the post, and
    a single post over budget is a refusal rather than a truncation — dropping images to fit
    would silently change the instrument for that one post.
    """
    budget = budget_mb * 1_000_000
    over = [post["name"] for post in packed if post["bytes"] > budget]
    if over:
        raise SystemExit(
            f"{', '.join(over)} encode above the {budget_mb} MB slice budget on their own."
            " RunPod's /run ceiling is 10 MB; raise --max-payload-mb deliberately if there is"
            " room, but do not let a post travel without its album."
        )
    out, current, size = [], [], 0
    for post in packed:
        if current and size + post["bytes"] > budget:
            out.append(current)
            current, size = [], 0
        current.append(post)
        size += post["bytes"]
    return out + [current] if current else out


def expected_worker() -> dict:
    """What the endpoint has to say it is before the first paid caption.

    `caption_prompt_sha256` is the one this checkout renders. The volume carries its own
    `repo/`, and a `git fetch` naming a missing ref leaves the old FETCH_HEAD so the merge after
    it prints "Already up to date" and moves nothing — a worker a session behind would caption
    happily under the previous prompt text.
    """
    return {
        "serving_config": serving.CAPTION_CONFIG,
        "merge_state": serving.MERGE_STATE[serving.CAPTION_CONFIG],
        "adapter_sha256": None,
        "caption_prompt_sha256": prompts.prompt_sha256(TASK),
    }


class FakeEndpoint:
    """`--smoke`: the whole write path, no network, no spend. One reply is empty on purpose."""

    def __init__(self) -> None:
        self.jobs = 0
        self.dump_path = None

    def info(self) -> dict:
        return expected_worker() | {"weights_dir": "<smoke>", "revision_requested": "<smoke>"}

    def caption(self, task: str, batch: list[list[str]]) -> list[dict]:
        if task != TASK:
            raise ValueError(f"{task}: the smoke serves {TASK}")
        self.jobs += 1
        return [
            {
                "content": "" if (self.jobs + n) % 7 == 0 else f"Полиця з молочними ({len(a)}).",
                "finish_reason": "stop",
                "cost": 0.0,
                "usage": {"prompt_tokens": 0, "completion_tokens": 0},
                "generation_id": None,
            }
            for n, a in enumerate(batch)
        ]

    def timing(self) -> dict:
        return {"calls": self.jobs, "rows": 0, "wall_seconds": 0.0, "smoke": True}


SETTLED_RATE = REPO_ROOT / "results" / "srv2d_cost.json"
COLD_START_USD = 0.0733
"""SPEC 3.15 (3) / runbook §C.1, pre-registered: 239.022 s at the settled rate. A pre-registration
is a file, not a preference — the measured start of THIS session is reported beside it and never
swapped into the formula."""


def rate_usd_per_second(path: Path = SETTLED_RATE) -> float:
    return float(json.loads(path.read_text(encoding="utf-8"))["rate"]["usd_per_second"])


def projection(
    boot_seconds: float, worker_seconds: float, rows_done: int, rows_total: int, rate: float
) -> dict:
    """What the whole run will cost, from what it has cost so far. The §C.1 stop, per slice.

    The first timed call is the `info` handshake, and on a cold endpoint it CARRIES the weight
    load — vis-b's re-pilot hid a whole cold start inside `worker_seconds` and made its per-post
    rate 2x too high (the ADR's retraction). So the boot is subtracted before the per-post rate
    is taken, and added back once, as the pre-registered constant.
    """
    marginal_s = max(worker_seconds - boot_seconds, 0.0) / max(rows_done, 1)
    return {
        "rows_done": rows_done,
        "rows_total": rows_total,
        "boot_seconds": round(boot_seconds, 3),
        "marginal_seconds_per_row": round(marginal_s, 3),
        "marginal_usd_per_row": round(marginal_s * rate, 6),
        # the pre-registered formula, which is the one the stop is taken on
        "projected_usd": round(rows_total * marginal_s * rate + COLD_START_USD, 4),
        "cold_start_usd_preregistered": COLD_START_USD,
        # reported BESIDE it: this session's own boot, never substituted into the line above
        "cold_start_usd_measured_here": round(boot_seconds * rate, 4),
        "projected_usd_on_the_measured_start": round(
            rows_total * marginal_s * rate + boot_seconds * rate, 4
        ),
    }


def run(
    client,
    jobs: list[list[dict]],
    dump_prefix: str | None,
    on_slice,
    stop=None,
) -> list[dict]:
    """One job per slice, in order. A slice that fails is named and never re-asked.

    ``stop(index, rows_done)`` is the §C.1 re-projection gate: it returns a reason to halt, and
    the slices not bought are left out of the outcomes rather than marked failed — nothing was
    asked for them.
    """
    outcomes = []
    for index, batch in enumerate(jobs):
        if stop is not None and index and (reason := stop(index, len(outcomes))):
            print(f"  STOP before job {index:02d}: {reason}", flush=True)
            break
        if dump_prefix is not None:
            client.dump_path = f"{dump_prefix}_{index:02d}.jsonl"
        try:
            replies = client.caption(TASK, [post["urls"] for post in batch])
        except (ApiError, ValueError, OSError) as err:
            outcomes += [
                {"name": post["name"], "caption": None, "unusable": f"job {index}: {err}"}
                for post in batch
            ]
            on_slice(index, batch, None)
            continue
        for post, reply in zip(batch, replies):
            text = " ".join((reply.get("content") or "").split())
            outcomes.append(
                {
                    "name": post["name"],
                    "caption": text or None,
                    "unusable": None if text else "empty reply",
                    "images_sent": post["images_sent"],
                    "images_available": post["images_available"],
                    "sha8": post["sha8"],
                    "finish_reason": reply.get("finish_reason"),
                }
            )
        on_slice(index, batch, replies)
    return outcomes


def main(argv: list[str] | None = None, client=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", required=True, help="names the outputs: captions_gm4_<scope>")
    parser.add_argument("--session", choices=sorted(SESSIONS), default="vis-b")
    parser.add_argument("--endpoint-id", default="", help=f"or ${ENDPOINT_ENV}; NO default")
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--record", type=Path, default=None)
    parser.add_argument("--ledger", type=Path, default=LEDGER)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--only", nargs="+", default=None, help="these posts only, by channel:id")
    parser.add_argument("--max-payload-mb", type=float, default=MAX_PAYLOAD_MB)
    parser.add_argument("--dump-prefix", default=None, help="a path prefix on the network volume")
    parser.add_argument("--smoke", action="store_true", help="fake client, no network, no spend")
    parser.add_argument("--dry-run", action="store_true", help="the population and slices, stop")
    parser.add_argument(
        "--project-stop-usd",
        type=float,
        default=None,
        help="§C.1: stop before a slice once the run projects above this. Default: what is left"
        " of the session cap on the ledger",
    )
    args = parser.parse_args(argv)

    out = args.out or OUT_DIR / f"gm4_{args.scope}.jsonl"
    record_path = args.record or REPO_ROOT / "results" / f"captions_gm4_{args.scope}.json"
    if args.smoke and (args.out, args.record) == (None, None):
        # A smoke on the real paths fills the paid artifacts with fake captions and then makes
        # the real run refuse to overwrite them. The 4.5g2 redirect, for the same reason.
        smoke = REPO_ROOT / "results" / "smoke"
        out, record_path = smoke / out.name, smoke / record_path.name
    for path in (out, record_path):
        if path.exists():
            raise SystemExit(
                f"{path} already exists — it is what a paid run bought. Re-running would spend"
                " again and overwrite the only copy: give --out/--record another path."
            )

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    images, polls, blind = pattern.population(manifest)
    if args.only:
        wanted = set(args.only)
        images = [entry for entry in images if entry["name"] in wanted]
        polls = [entry for entry in polls if entry["name"] in wanted]
        # `blind` is filtered too, or a one-post smoke reports the whole manifest's
        # `no_surrogate_at_all` in its record — a count about posts the run never looked at
        blind = [name for name in blind if name in wanted]
    packed = albums(images, args.root)
    jobs = slices(packed, args.max_payload_mb)
    print(
        f"{len(images) + len(polls) + len(blind)} posts with no text of their own"
        f"\n  {len(images)} have images to caption"
        f" ({sum(len(e['images']) for e in images)} images,"
        f" {sum(p['images_sent'] for p in packed)} sent)"
        f"\n  {len(polls)} are polls and are transcribed, no model"
        f"\n  {len(blind)} have neither: {', '.join(blind) or '—'}"
        f"\n  {len(jobs)} jobs at ≤{args.max_payload_mb} MB"
        f" (largest {max((sum(p['bytes'] for p in j) for j in jobs), default=0) / 1e6:.2f} MB)"
    )
    if args.dry_run:
        return 0

    endpoint_id = args.endpoint_id or os.environ.get(ENDPOINT_ENV, "")
    ledger, session_cap = None, SESSIONS[args.session]
    if client is not None:
        pass
    elif args.smoke:
        client = FakeEndpoint()
    else:
        if not endpoint_id:
            raise SystemExit(
                f"no endpoint id: pass --endpoint-id or set ${ENDPOINT_ENV}. There is no"
                " default on purpose — a caption run against whatever id was last in a shell"
                " variable is a run against an unknown configuration."
            )
        from eval_zero_shot import runpod_api_key  # noqa: PLC0415

        balance = guard.balance()
        ledger = read_ledger(args.ledger, args.session, session_cap, balance)
        args.ledger.parent.mkdir(parents=True, exist_ok=True)
        args.ledger.write_text(
            json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )  # anchored before the first job, never after
        balance, spent = spend_now(ledger, args.session)
        print(
            f"ledger: {args.session} spent ${spent:.4f} of ${session_cap:.2f} (balance ${balance:.2f})"
        )
        if spent >= session_cap:
            raise SystemExit(
                f"REFUSED: {args.session}'s ${session_cap:.2f} cap is reached (${spent:.4f}"
                " spent). Stop and report — an overrun aborts, it does not raise the cap."
            )
        client = serving.EndpointClient(
            endpoint_id,
            runpod_api_key(),
            forward_batch_size=1,  # SPEC amendment 3.13 (3): batch 1, always
            policy=serving.execution_policy(JOB_TIMEOUT_S, JOB_TTL_S),
            job_timeout=JOB_TTL_S + 300.0,
            submit="run",
        )

    info = serving.assert_serving(client.info(), expected_worker())
    print(
        f"endpoint       {endpoint_id or '<smoke>'} · {info['serving_config']}/{info['merge_state']}"
    )
    print(f"  revision      {info.get('revision_requested')}")
    print(f"  prompt        {TASK} {info['caption_prompt_sha256'][:12]}…")

    started = datetime.now(UTC).isoformat(timespec="seconds")
    # After `info` and before the first caption: on a cold endpoint this is the weight load.
    boot_seconds = float(client.timing().get("worker_seconds") or 0.0)
    rate = rate_usd_per_second()
    rows_total = sum(len(job) for job in jobs)
    budget = args.project_stop_usd
    if budget is None and ledger is not None:
        budget = round(session_cap - spent, 4)
    projections = []

    def gate(index: int, rows_done: int) -> str | None:
        seen = projection(
            boot_seconds, float(client.timing()["worker_seconds"]), rows_done, rows_total, rate
        )
        projections.append({"before_job": index, **seen})
        print(
            f"  §C.1 after {rows_done}/{rows_total} rows: ${seen['marginal_usd_per_row']:.6f}/post"
            f" → ${seen['projected_usd']:.4f} projected"
            f" (measured start ${seen['cold_start_usd_measured_here']:.4f}"
            f" vs pre-registered ${COLD_START_USD})",
            flush=True,
        )
        if budget is not None and seen["projected_usd"] > budget:
            return (
                f"the run projects ${seen['projected_usd']:.4f} against ${budget:.4f} left of the"
                f" ${session_cap:.2f} cap. A cap is not raised to finish a run"
            )
        return None

    outcomes = run(
        client,
        jobs,
        args.dump_prefix,
        lambda i, batch, replies: print(
            f"  job {i:02d}  {len(batch)} posts  {'ok' if replies else 'FAILED'}"
            f"  {sum(p['bytes'] for p in batch) / 1e6:.2f} MB"
        ),
        gate if budget is not None else None,
    )

    by_name = {entry["name"]: entry for entry in images}
    written = [
        pattern.record_for(
            by_name[out_row["name"]],
            out_row["caption"],
            "image",
            local_llm.MODEL_ID,
            out_row.get("images_sent", 0),
            SOURCE,
            task=TASK,
        )
        for out_row in outcomes
        if out_row["caption"]
    ]
    written += [
        pattern.record_for(entry, pattern.poll_caption(entry["poll"]), "poll", None, 0, None)
        for entry in polls
    ]
    written.sort(key=lambda row: (row["channel"], row["msg_id"]))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in written), encoding="utf-8"
    )

    balance, spent = (None, None) if ledger is None else spend_now(ledger, args.session)
    unusable = [row for row in outcomes if not row["caption"]]
    asked = {row["name"] for row in outcomes}
    unbought = sorted(post["name"] for job in jobs for post in job if post["name"] not in asked)
    record = {
        "timestamp": started,
        "phase": f"5c1 {args.session} — the GM4 caption instrument",
        "contract": "docs/PROMPT-5c1-vis-a.md deliverable 4",
        "task": TASK,
        "caption_source": SOURCE,
        "caption_sources": sorted({row["caption_source"] for row in written if row["model"]}),
        "endpoint": {"id": endpoint_id or None, "worker": info},
        "smoke": bool(args.smoke),
        "attempts_per_slice": 1,
        "prompt_sha256": {TASK: prompts.prompt_sha256(TASK)},
        "source": str(args.manifest.relative_to(REPO_ROOT))
        if args.manifest.is_relative_to(REPO_ROOT)
        else str(args.manifest),
        "population": {
            "media_only_posts": len(images) + len(polls) + len(blind),
            "captioned": sum(1 for row in written if row["kind"] == "image"),
            "transcribed_polls": len(polls),
            "unusable": [{"name": r["name"], "why": r["unusable"]} for r in unusable],
            "no_surrogate_at_all": blind,
        },
        "jobs": [
            {
                "i": i,
                "posts": [post["name"] for post in batch],
                "sha8": [post["sha8"] for post in batch],
                "megabytes": round(sum(post["bytes"] for post in batch) / 1e6, 3),
                "dump_path": None
                if args.dump_prefix is None
                else f"{args.dump_prefix}_{i:02d}.jsonl",
            }
            for i, batch in enumerate(jobs)
        ],
        "images": {
            "sent": sum(post["images_sent"] for post in packed),
            "available": sum(len(entry["images"]) for entry in images),
            "max_per_request": MAX_IMAGES,
            "posts_truncated": sorted(
                post["name"] for post in packed if post["images_available"] > post["images_sent"]
            ),
        },
        "truncated_replies": sorted(
            row["name"] for row in outcomes if row.get("finish_reason") == "length"
        ),
        "timing": client.timing(),
        # §C.1 (SPEC 3.15 (3)): the run re-priced before every slice but the first, from its own
        # measured seconds with the boot subtracted, and stopped the moment the projection went
        # past what was left of the cap. `unbought` is what was never asked for — not a failure.
        "projection": {
            "rate_usd_per_second": rate,
            "rate_source": "results/srv2d_cost.json :: rate.usd_per_second",
            "stop_at_usd": budget,
            "per_slice": projections,
            "stopped_early": bool(unbought),
            "unbought": unbought,
        },
        "out": str(out.relative_to(REPO_ROOT)) if out.is_relative_to(REPO_ROOT) else str(out),
        "out_sha256": sha256(out.read_bytes()).hexdigest(),
        "cost": {
            "jobs": len(jobs),
            "usd": None if spent is None else round(spent, 4),
            "cap_usd": session_cap,
            "session": args.session,
            "anchor": str(args.ledger.relative_to(REPO_ROOT))
            if args.ledger.is_relative_to(REPO_ROOT)
            else str(args.ledger),
            "reading": (
                "the RunPod balance delta against this session's own anchor. It is a FLOOR —"
                " the balance settles minutes to hours behind the resource (Dv33) — and"
                " runpod_guard's itemised corroboration is the phase-level check, not this one."
            ),
        },
        "git": git_state(record_path),
        "note": (
            "Captions from the project's own NF4 base at the pinned revision, adapter OFF,"
            f" greedy, forward batch 1, under the registered {TASK} prompt (SPEC amendment"
            " 3.13 (3)). The pictures travelled inside the job as base64; the network volume"
            " carried the per-post dump. One attempt per slice — a job that failed is named"
            " here and was never re-asked."
        ),
    }
    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if ledger is not None:
        ledger["gpu_sessions"].append(
            {
                "at": datetime.now(UTC).isoformat(timespec="seconds"),
                "balance": balance,
                "step_spent_usd": round(spent, 4),
                "note": (
                    f"{args.session} {args.scope}: {record['population']['captioned']} of"
                    f" {len(images)} media-only posts captioned in {len(jobs)} jobs"
                ),
            }
        )
        args.ledger.write_text(
            json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    print(
        f"\n{record['population']['captioned']} captioned, {len(unusable)} unusable"
        f" · {'$%.4f' % spent if spent is not None else 'no spend'} of ${session_cap:.2f}"
        f"\nwrote {record['out']} and {record_path.name}"
    )
    if unusable:
        # The fake client empties one reply in every seven on purpose, so the smoke exercises
        # this branch and the record's `unusable` list — but it must not exit non-zero, or a
        # runbook step whose whole job is to prove the write path reads as a failed run.
        print(
            "STOP AND REPORT: a slice or a post came back without a caption. No retry is made."
            if not args.smoke
            else "smoke: the fake client empties one reply in seven, and those rows are named"
            " in the record rather than written as captions"
        )
        if not args.smoke:
            return 3
    if spent is not None and spent >= session_cap:
        print("STOP AND REPORT: the cap is reached. An overrun aborts, it does not raise a cap.")
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
