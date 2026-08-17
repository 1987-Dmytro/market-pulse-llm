#!/usr/bin/env python3
"""reader-v5 — the Mac half: the two-leg pack, the pod's clock, and the replies turned into evidence.

reader-v4's driver with three changes and no others, and the pieces that must not differ are
IMPORTED from it rather than retyped — the registration check, the seconds arithmetic, the boot
deadline and the usable-seconds rule.

**1. The pack has two legs and a UNIT is a request.** Leg A is the 23 whole threads; leg B is one
thread in three chunks. They are projected apart and read in that order, so a stop inside leg B
leaves leg A complete and its four bars scored.

**2. Gate records APPEND.** `results/reader_v5_run.json` keeps `gates` as a LIST and every
WAIT/GO/KILL snapshot is appended. reader-v4's record overwrote its own first GO snapshot; the
arithmetic was re-checked by hand afterwards and agreed, which is luck and not a property.

**3. The ingest MERGES leg B and censuses the echo.** Each unit is parsed here, under the pinned
parser; leg B's three verdicts are merged by `market_pulse.reader_v5.merge`, and every unit carries
the three-state completeness census beside its verdict.

    PYTHONPATH=src python3.11 scripts/read_threads_reader_v5.py --pack results/reader_v5_pack.json
    PYTHONPATH=src python3.11 scripts/read_threads_reader_v5.py --open --pod-id <ID> \\
        --created-at 2026-08-17T18:00:00Z --usd-per-hour <costPerHr> --card '<the card>'
    PYTHONPATH=src python3.11 scripts/read_threads_reader_v5.py --gate --raw results/reader_v5_pod.jsonl
    PYTHONPATH=src python3.11 scripts/read_threads_reader_v5.py --ingest --raw results/reader_v5_pod.jsonl
"""

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gate_census_w1_reader as reader_cell  # noqa: E402
import probe_b_population as subset  # noqa: E402
import read_threads_reader_v4 as v4  # noqa: E402
import runpod_guard as guard  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import prompts, reader_v5  # noqa: E402

PHASE = "reader-v5"
PREREG = REPO_ROOT / "results" / "prereg_reader_probe_v5.json"
LEDGER = guard.step_ledger_path(PHASE)
PACK = REPO_ROOT / "results" / "reader_v5_pack.json"
RAW = REPO_ROOT / "results" / "reader_v5_pod.jsonl"
EVIDENCE = REPO_ROOT / "results" / "reader_v5_w1.jsonl"
RECORD = REPO_ROOT / "results" / "reader_v5_run.json"

rel = v4.rel
stamp = v4.stamp
elapsed_since = v4.elapsed_since
usable_seconds = v4.usable_seconds
rate_of = v4.rate_of
deadlines = v4.deadlines


def registration() -> dict:
    """The pre-registration, refused unless it is committed and unmodified — v4's check, its file."""
    for argv, message in (
        (
            ["git", "ls-files", "--error-unmatch", str(PREREG)],
            f"{rel(PREREG)} is not tracked by git. The registration is the pre-registration: until"
            " it is committed, nothing stops it from being rewritten once the numbers are in.",
        ),
        (
            ["git", "diff", "HEAD", "--quiet", "--", str(PREREG)],
            f"{rel(PREREG)} differs from HEAD. The committed registration is the one this run is"
            " read against — and it is FROZEN: restore the file, do not commit the change.",
        ),
    ):
        if subprocess.run(argv, cwd=REPO_ROOT, capture_output=True).returncode != 0:
            raise SystemExit(message)
    return json.loads(PREREG.read_text(encoding="utf-8"))


def build_pack(record: dict) -> dict:
    """Every UNIT as the pod will be given it, each held to the registration's own sha.

    Both legs are rebuilt from the stores and compared against the record — the population digest
    says WHICH threads and the per-unit rendering sha says WHAT each request is. It runs here, on
    the Mac, before anything is created: a comment edited in the store costs $0 to discover now and
    a pod's boot to discover later.
    """
    task = record["instruments"]["task"]
    kept = {subset.key(one["channel"], one["post_id"]): one for one in subset.population()}
    leg_a = record["population"]["leg_a"]
    if leg_a["enumeration"]["digest"] != subset.digest(subset.population()):
        raise SystemExit("leg A's population digest moved — the pairing this run rests on is gone.")

    items = []
    for one in leg_a["enumeration"]["threads"]:
        thread = kept[one["thread"]]
        items.append(
            _item(
                thread["channel"],
                thread["post_id"],
                thread["post_text"],
                [(row["msg_id"], row["text"]) for row in thread["comments"]],
                task,
                leg="A",
                unit_id=one["thread"],
                pinned=one["rendering_sha256"],
                cases=one["cases"],
            )
        )

    leg_b = record["population"]["leg_b"]
    source = next(
        one
        for one in reader_cell.population()
        if subset.key(one["channel"], one["post_id"]) == leg_b["thread"]
    )
    texts = {row["msg_id"]: row["text"] for row in source["comments"]}
    if [row["msg_id"] for row in source["comments"]] != leg_b["msg_ids"]:
        raise SystemExit(f"{leg_b['thread']}: its payable comments moved — stop and report.")
    for one in leg_b["items"]:
        index, total = one["part"]
        items.append(
            _item(
                source["channel"],
                source["post_id"],
                source["post_text"],
                [(msg_id, texts[msg_id]) for msg_id in one["msg_ids"]],
                task,
                leg="B",
                unit_id=one["id"],
                pinned=one["rendering_sha256"],
                part=(index, total),
            )
        )

    return {
        "phase": PHASE,
        "registration": {"record": rel(PREREG), "sha256": summary.sha256_of(PREREG)},
        "task": task,
        # COPIED and not aliased: a pack that shares the registration's own dicts can be edited into
        # agreeing with itself, and the pod's whole handshake is that these two differ when the
        # volume is behind
        "instruments": {
            "prompt_sha256": dict(record["instruments"]["prompt_sha256"]),
            "parser": {"sha256": record["instruments"]["parser"]["sha256"]},
        },
        "serving": dict(record["instruments"]["serving"]),
        "items": items,
        "reading": (
            "the pod renders each item itself, chunk header included, and refuses unless its sha"
            " equals the one above. Shipping the rendered string would only prove the two machines"
            " agree about a string; what has to be true is that the model is shown what the"
            " registration registered"
        ),
    }


def _item(channel, post_id, post, comments, task, *, leg, unit_id, pinned, part=None, cases=None):
    content = prompts.reader_messages_gm4(channel, post_id, post, comments, task=task, part=part)[
        0
    ]["content"]
    got = hashlib.sha256(content.encode("utf-8")).hexdigest()
    if got != pinned:
        raise SystemExit(
            f"{unit_id}: this checkout renders {got[:16]}… and the registration pinned"
            f" {pinned[:16]}… — the request moved since the registration. Stop and report."
        )
    return {
        "id": unit_id,
        "leg": leg,
        "thread": f"{channel}:{post_id}",
        "channel": channel,
        "post_id": post_id,
        "post": post,
        "comments": [[msg_id, text] for msg_id, text in comments],
        "msg_ids": [msg_id for msg_id, _ in comments],
        "payable_comments": len(comments),
        "part": None if part is None else list(part),
        "cases": cases or [],
        "rendering_sha256": got,
        "rendered_chars": len(content),
    }


def projection(record: dict, rate: float, rows: list[dict], elapsed: float, pack: dict) -> dict:
    """The full-pass gate over UNITS, with both legs of the registration's inequality.

    v4's rule and probe-a's and probe-b's, kept: BOTH projections are computed and the PESSIMISTIC
    one binds — unread units ÷ read units, and unread payable comments ÷ read payable comments. A
    single-leg projection is looser in the one direction a cap guard may not be loose in, and this
    run's units carry between 0 and 16 payable comments.
    """
    usable = usable_seconds(record, rate)
    read = len(rows)
    if not read:
        raise SystemExit("no replies yet — there is nothing to project from")
    payable = {one["id"]: one["payable_comments"] for one in pack["items"]}
    measured = sum(float(row["seconds"]) for row in rows)
    of = len(pack["items"])
    unread = of - read
    read_payable = sum(payable[row["id"]] for row in rows) or 1
    unread_payable = sum(payable.values()) - read_payable
    by_unit, by_payable = unread / read, unread_payable / read_payable
    factor = max(by_unit, by_payable)
    projected = elapsed + factor * measured
    affordable = (usable - elapsed) / (factor * read) if unread else float("inf")
    return {
        "units_read": read,
        "units_unread": unread,
        "legs_read": sorted({row.get("leg") or "?" for row in rows}),
        "payable_comments_read": read_payable,
        "payable_comments_unread": unread_payable,
        "elapsed_since_create_seconds": round(elapsed, 1),
        "measured_seconds": round(measured, 3),
        "measured_seconds_per_unit": round(measured / read, 3),
        "projections": {
            "by_unit": {"factor": round(by_unit, 4), "seconds": round(measured * by_unit, 1)},
            "by_payable_comment": {
                "factor": round(by_payable, 4),
                "seconds": round(measured * by_payable, 1),
            },
            "binding": {
                "factor": round(factor, 4),
                "seconds": round(factor * measured, 1),
                "which": "by_unit" if by_unit >= by_payable else "by_payable_comment",
            },
        },
        "usable_seconds": round(usable, 1),
        "projected_total_seconds": round(projected, 1),
        "headroom_seconds": round(usable - projected, 1),
        "seconds_per_unit_that_still_fits": round(affordable, 3),
        "the_verdict_re_derives_from_here": (
            "`measured_seconds_per_unit` ≤ `seconds_per_unit_that_still_fits` IS the verdict. The"
            " dollars below are the same statement rounded, and at the margin both sides of it"
            " print the same figure"
        ),
        "usd": {
            "cap_usd_all_in": float(record["money"]["cap_usd_all_in"]),
            "spent_so_far_usd": round(elapsed * rate, 4),
            "projected_total_usd": round(projected * rate, 4),
        },
        "verdict": "GO" if projected <= usable else "STOP",
    }


def ingest(record: dict, raw: list[dict], pack: dict) -> list[dict]:
    """The pod's raw replies turned into evidence — parsed here, merged here, censused here.

    Leg B's three chunk verdicts become ONE row for the thread, through
    `market_pulse.reader_v5.merge`; the chunks are kept beside it, because a merged verdict whose
    parts nobody could look at is a verdict nobody can argue with.
    """
    task = record["instruments"]["task"]
    items = {one["id"]: one for one in pack["items"]}
    rows, chunks = [], {}
    for one in raw:
        item = items[one["id"]]
        if one["rendering_sha256"] != item["rendering_sha256"]:
            raise SystemExit(
                f"{one['id']}: the pod answered a request whose sha is"
                f" {one['rendering_sha256'][:16]}… and the pack pinned"
                f" {item['rendering_sha256'][:16]}… — stop and report."
            )
        try:
            parsed, reason = prompts.parse_reply(task, one["reply"]), None
        except prompts.ParseError as err:
            parsed, reason = None, err.reason
        row = {
            "id": one["id"],
            "leg": item["leg"],
            "thread": item["thread"],
            "part": item["part"],
            "channel": item["channel"],
            "post_id": item["post_id"],
            "cases": item["cases"],
            "msg_ids": item["msg_ids"],
            "payable_comments": item["payable_comments"],
            "task": task,
            "prompt_sha256": record["instruments"]["prompt_sha256"][task],
            "rendering_sha256": one["rendering_sha256"],
            "request": prompts.reader_messages_gm4(
                item["channel"],
                item["post_id"],
                item["post"],
                [(int(msg_id), text) for msg_id, text in item["comments"]],
                task=task,
                part=None if item["part"] is None else tuple(item["part"]),
            )[0]["content"],
            "reply": one["reply"],
            "balanced": one.get("balanced"),
            "emitted_chars": one.get("emitted_chars"),
            "cut_chars": one.get("cut_chars"),
            "finish_reason": one.get("finish_reason"),
            "usage": one.get("usage"),
            "parsed": parsed,
            "repairs": None if parsed is None else parsed["repairs"],
            "parse_error": reason,
            "echo": None if parsed is None else reader_v5.echo(item["msg_ids"], parsed),
            "seconds": {"worker": float(one["seconds"])},
            "elapsed_since_start": one.get("elapsed_since_start"),
            "boot_seconds": one.get("boot_seconds"),
        }
        rows.append(row)
        if item["leg"] == "B":
            chunks.setdefault(item["thread"], []).append(row)

    for thread, parts in chunks.items():
        parts.sort(key=lambda row: row["part"][0])
        verdicts = [row["parsed"] for row in parts if row["parsed"]]
        merged, error = None, None
        if len(verdicts) == len(parts):
            try:
                merged = reader_v5.merge(verdicts)
            except reader_v5.MergeError as err:
                error = err.reason
        else:
            error = f"{len(parts) - len(verdicts)} of {len(parts)} chunks did not parse"
        ids = [msg_id for row in parts for msg_id in row["msg_ids"]]
        rows.append(
            {
                "id": f"{thread}#merged",
                "leg": "B",
                "thread": thread,
                "part": None,
                "merged_from": [row["id"] for row in parts],
                "msg_ids": ids,
                "payable_comments": len(ids),
                "task": task,
                "parsed": merged,
                "merge_error": error,
                "echo": None if merged is None else reader_v5.echo(ids, merged),
                "seconds": {"worker": round(sum(row["seconds"]["worker"] for row in parts), 3)},
                "reading": (
                    "a DERIVED row: it is the three chunk rows above put together and it carries no"
                    " reply of its own. Leg B's mechanical bars are scored on it and it never enters"
                    " a bar of leg A"
                ),
            }
        )
    return rows


def raw_rows(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"{rel(path)}: the pod has written nothing yet")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def run_record() -> dict:
    if not RECORD.exists():
        raise SystemExit(f"{rel(RECORD)} does not exist — the pod was never opened with --open")
    return json.loads(RECORD.read_text(encoding="utf-8"))


def save(record: dict) -> None:
    RECORD.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def append_gate(state: dict, gate: dict, kind: str) -> dict:
    """Every snapshot APPENDED, none overwritten — the one lesson v4's own record left behind.

    v4 wrote `go_no_go` and `boot_kill` as scalars, so its first GO snapshot was displaced by the
    re-gate at twelve threads and the arithmetic had to be re-checked by hand against the jsonl. It
    agreed, which is luck. A list cannot lose a reading ([[the_marker_is_written_last]]).
    """
    state.setdefault("gates", []).append(
        {"kind": kind, "at": datetime.now(UTC).isoformat(timespec="seconds"), **gate}
    )
    state["latest"] = {"kind": kind, "verdict": gate["verdict"]}
    save(state)
    return state


def main(argv: list[str] | None = None, now: datetime | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", nargs="?", const=str(PACK), help="build and verify the pack")
    parser.add_argument(
        "--open", action="store_true", help="record the pod and print the deadlines"
    )
    parser.add_argument("--pod-id")
    parser.add_argument("--created-at", help="the create response's stamp — the meter's zero")
    parser.add_argument("--usd-per-hour", type=float, help="costPerHr, read back from create")
    parser.add_argument("--card", help="the card the create response actually gave")
    parser.add_argument("--deadlines", action="store_true", help="the boot deadline, right now")
    parser.add_argument("--gate", action="store_true", help="the boot kill rule / the full pass")
    parser.add_argument("--ingest", action="store_true", help="the pod's replies -> the evidence")
    parser.add_argument("--raw", type=Path, default=RAW)
    parser.add_argument("--generation-started-at", help="when the on-pod runner was launched")
    args = parser.parse_args(argv)

    record = registration()

    if args.pack:
        pack = build_pack(record)
        Path(args.pack).write_text(
            json.dumps(pack, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        legs = {leg: sum(1 for one in pack["items"] if one["leg"] == leg) for leg in ("A", "B")}
        print(f"pack {args.pack} · {len(pack['items'])} units, every sha matches the record")
        print(f"  leg A {legs['A']} threads · leg B {legs['B']} chunks")
        print(
            f"  task {pack['task']} · parser {pack['instruments']['parser']['sha256'][:16]}…"
            f" · ceiling {pack['serving']['output_tokens']} output tokens"
        )
        return 0

    if args.open:
        for name in ("pod_id", "created_at", "usd_per_hour", "card"):
            if getattr(args, name) is None:
                parser.error(f"--open needs --{name.replace('_', '-')}")
        if not LEDGER.exists():
            raise SystemExit(
                f"{rel(LEDGER)} does not exist: the step's spend anchor is written by"
                f" `runpod_guard.py --step {PHASE} --step-cap"
                f" {record['money']['cap_usd_all_in']}` and the runbook writes it BEFORE anything"
                " billable. A pod that exists against no counter is a pod nothing is measuring."
            )
        pod = {
            "pod_id": args.pod_id,
            "created_at": args.created_at,
            "card": args.card,
            "usd_per_hour": args.usd_per_hour,
            "usd_per_second": round(args.usd_per_hour / 3600.0, 9),
            "card_registered": record["money"]["meter"]["card_requested"],
            "usd_per_hour_worked_example": record["money"]["meter"]["worked_example_usd_per_hour"],
            "priced_at_or_under_the_example": args.usd_per_hour
            <= record["money"]["meter"]["worked_example_usd_per_hour"],
        }
        rate = rate_of(pod)
        gate = deadlines(record, rate, elapsed_since(args.created_at, now))
        state = {"phase": PHASE, "pod": pod, "gates": []}
        append_gate(state, gate, "open")
        print(json.dumps(pod, ensure_ascii=False, indent=2))
        print(json.dumps(gate, ensure_ascii=False, indent=2))
        return 0

    if args.deadlines or args.gate:
        state = _stamped(run_record(), args.generation_started_at)
        rate = rate_of(state["pod"])
        elapsed = elapsed_since(state["pod"]["created_at"], now)
        launched = state["pod"].get("generation_started_at")
        generation_at = (
            None if not launched else elapsed_since(state["pod"]["created_at"], stamp(launched))
        )
        rows = raw_rows(args.raw) if args.raw.exists() else []
        pack = json.loads(PACK.read_text(encoding="utf-8"))

    if args.deadlines or (args.gate and not rows):
        gate = deadlines(record, rate, elapsed, generation_at) | {
            "read_from": _read_from(args.raw),
        }
        append_gate(state, gate, "boot_kill")
        print(json.dumps(gate, ensure_ascii=False, indent=2))
        if not args.gate:
            return 0
        print(
            f"VERDICT {gate['verdict']} — no reply in {rel(args.raw)}"
            f" (copied back at {gate['read_from']['copied_back_at']})"
        )
        return 2 if gate["verdict"] == "KILL" else 3

    if args.gate:
        by_id = {one["id"]: one for one in pack["items"]}
        gate = projection(
            record,
            rate,
            [row | {"leg": by_id[row["id"]]["leg"]} for row in rows],
            elapsed,
            pack,
        ) | {"read_from": _read_from(args.raw)}
        append_gate(state, gate, "full_pass")
        print(json.dumps(gate, ensure_ascii=False, indent=2))
        print(f"VERDICT {gate['verdict']} — {rel(RECORD)}")
        return 0 if gate["verdict"] == "GO" else 2

    if args.ingest:
        pack = json.loads(PACK.read_text(encoding="utf-8"))
        rows = ingest(record, raw_rows(args.raw), pack)
        with EVIDENCE.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                handle.flush()
        parsed = sum(1 for row in rows if row["parsed"])
        print(
            f"{rel(EVIDENCE)} · {len(rows)} rows · {parsed} parsed · {len(rows) - parsed} refused"
        )
        for row in rows:
            state = "parsed" if row["parsed"] else f"REFUSED ({row.get('parse_error')})"
            echo = row.get("echo") or {}
            absent = f" · absent {echo['absent']}" if echo.get("absent") else ""
            print(
                f"  [{row['leg']}] {row['id']:40s} {row['payable_comments']:3d} payable ·"
                f" {row['seconds']['worker']:6.1f} s · {state}{absent}"
            )
        return 0

    raise SystemExit("one of --pack / --open / --deadlines / --gate / --ingest is required")


def _stamped(state: dict, launched: str | None) -> dict:
    """v4's `stamp_generation`, with this driver's `save`: the stamp is written once and never
    overwritten, because the deadline it places is the reason the run may be killed."""
    if launched and not state["pod"].get("generation_started_at"):
        state["pod"]["generation_started_at"] = launched
        save(state)
    return state


def _read_from(path: Path) -> dict:
    """Which FILE the gate read, and when it was copied back — Dv453, kept.

    «No reply has landed» is a statement about a file, and the pod writes to its own.
    """
    return {
        "path": rel(path),
        "exists": path.exists(),
        "copied_back_at": (
            None
            if not path.exists()
            else datetime.fromtimestamp(path.stat().st_mtime, UTC).isoformat(timespec="seconds")
        ),
        "rule": (
            "copy the partial jsonl back BEFORE every gate: a KILL read off a file nobody refreshed"
            " would kill a healthy run and put the wrong reason in this record"
        ),
    }


if __name__ == "__main__":
    raise SystemExit(main())
