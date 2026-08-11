#!/usr/bin/env python3
"""The sku-b position pilot: 108 leaflet pages and 30 text rows, one attempt. (PAID — see --smoke.)

SPEC 3.17 (6) buys ONE paid session at a $0.35 cap and a failed bar closes B as "instrument not
ready" BY MEASUREMENT — no retry, no re-prompt, no second draw. 3.17 (9) fixes what serves it:
SERVING_CONFIG=POSITIONS, the NF4 base at the pinned revision with the adapter OFF, greedy,
batch 1, max_new_tokens 800, and a smoke call on NON-gold inputs before either leg touches gold.
The bars, their denominators and the five ratified readings are `results/sku_pilot_prereg_v2.json`.

What it does NOT do, and each omission is somebody's expensive evening:

- **No default endpoint id.** `--endpoint-id` or `$RUNPOD_POSITIONS_ENDPOINT`, and a refusal
  otherwise: a run against whatever id was last in a shell variable is a run against an unknown
  configuration.
- **No retries.** A page or a row whose job errors is named in the record and never re-asked. One
  attempt is the pre-registration, not a setting.
- **No shared ledger.** Three constants below are this contract's own — its phase name, the $0.35
  cap SPEC 3.17 (6) wrote, and its own anchor file. `relabel.read_ledger` renders another phase's
  briefing path inside a money record; `scripts/caption_atb_5c1.py` writes its own anchor instead
  and this copies that pattern, not the helper.
- **No hidden model swap.** The worker is asked what it loaded and the run stops before the first
  paid call unless it answers exactly `results/sku_pilot_serving.json :: expected_worker`. Not one
  value of that block is restated here.
- **No job that can out-bill the cap.** 3.17 (10)(c): the projection gate re-prices BETWEEN jobs
  and cannot see inside one, so :data:`JOB_TIMEOUT_S` is what bounds a wedged worker — sized under
  the cap on its own — and a job the CLOCK kills ends the run rather than the batch. And before any
  of that, 3.17 (10)(a): after the two warm-up calls the whole run is priced from what they
  measured, and a projection over what is left of the cap refuses BEFORE the first gold call, which
  consumes no attempt.
- **No salvage.** `positions.parse_positions` is strict at the level of the whole reply, and a
  refusal is counted by its reason and excluded — never read as a page with no dairy on it. `[]`
  and "unreadable" are different outcomes and conflating them reports parse failures as empty
  pages.
- **No shortened album.** Pages are packed into jobs under :data:`MAX_PAYLOAD_MB` and a page that
  exceeds it on its own is a refusal, not a re-encode: SPEC 3.17 (4) is one page per call, and an
  image dropped or shrunk to fit is a different instrument for that one page.

- **No element bought twice.** `--resume` (SPEC 3.17 (11)) buys ONLY what
  `results/sku_b_positions.json` records as unbought, under the re-registration that pins it. It
  refuses if a pin has moved, if an id the registration calls unbought already carries an answer, if
  the selection contains an id the first session bought, or if the merged outcomes name any source
  twice. The warm-up stops being synthetic: (11)(c)'s registered real page and real row, because the
  probe — not the arithmetic — is what let the first session's go/no-go pass a run it should have
  refused.

    PYTHONPATH=src python3 scripts/positions_gm4_skub.py --dry-run
    PYTHONPATH=src python3 scripts/positions_gm4_skub.py --smoke
    PYTHONPATH=src python3 scripts/positions_gm4_skub.py --endpoint-id <id>
    PYTHONPATH=src python3 scripts/positions_gm4_skub.py --resume --dry-run
    PYTHONPATH=src python3 scripts/positions_gm4_skub.py --resume --endpoint-id <id>
"""

import argparse
import csv
import json
import os
import sys
from collections import Counter
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_sku_text_pack as pack  # noqa: E402
import caption_posts as media  # noqa: E402
import caption_gm4_5c1 as leader  # noqa: E402
import runpod_guard as guard  # noqa: E402

from market_pulse import positions, prompts, provenance, serving  # noqa: E402
from market_pulse.brands import watchlist_aliases  # noqa: E402
from market_pulse.registry import load_registry  # noqa: E402
from market_pulse.zero_shot import ApiError  # noqa: E402

PHASE = "sku-b"
CAP_USD = 0.35
LEDGER = REPO_ROOT / "results" / "spend_sku_b.json"
"""This contract's three constants. The cap is SPEC 3.17 (6)'s, transcribed rather than chosen: it
buys the whole two-leg pilot and nothing else. One anchor key, written before the first job, and it
may never be regenerated — delete it and the counter silently restarts at today's balance."""

RESUME_PHASE = "sku-b-v3"
RESUME_CAP_USD = 0.45
RESUME_LEDGER = REPO_ROOT / "results" / "spend_sku_b_v3.json"
"""The same three, for the RESUMED session of SPEC 3.17 (11). Its own anchor, because the first
session's is spent: `results/spend_sku_b.json` measures a balance from before a $0.1965 run, and a
resumed session enforcing its cap against that anchor would start 0.1965 in the red on a cap that
was priced without it. (11)(d)'s $0.45 is transcribed, not chosen."""

REFERENCE = REPO_ROOT / "results" / "sku_reference_leaflet.json"
MANIFEST = REPO_ROOT / "results" / "sku_text_pack_manifest.json"
PREREG = REPO_ROOT / "results" / "sku_pilot_prereg_v2.json"
PREREG_RESUME = REPO_ROOT / "results" / "sku_pilot_prereg_v3.json"
PIN = REPO_ROOT / "results" / "sku_pilot_serving.json"
REGISTRY = REPO_ROOT / "config" / "registry.yaml"

DUMP = REPO_ROOT / "results" / "sku_b_positions.jsonl"
RECORD = REPO_ROOT / "results" / "sku_b_positions.json"

RESUME_DUMP = REPO_ROOT / "results" / "sku_b_positions_v3.jsonl"
RESUME_RECORD = REPO_ROOT / "results" / "sku_b_positions_v3.json"
"""The resumed session writes NEW files and appends the first session's rows into them.

Not an in-place append, and the reason is forced rather than chosen: `sku_pilot_prereg_v3.json ::
resume.bought_already.dump.sha256` pins `sku_b_positions.jsonl` as it stands, so appending to it
would break the pin in the same commit the rows landed — and that pin is what proves the 17 answers
were not re-asked. The sealed pair stays evidence; this pair is the merged bar input, and every row
in it names the session that bought it."""

FAMILY = positions.DEFAULT_FAMILY
"""Whose instruments produced the replies. `positions_post_gm4` and `positions_text_gm4` are the
DAIRY family's registered prompts and they ask for `"fat"` on the wire; the schema field is
`attribute_pct` (SPEC 3.17 (8)). Everything below reads the wire through `positions.wire_key`, and
never `row["attribute"]` — that key returns a legal "absent" on every row instead of an error."""

MAX_PAYLOAD_MB = 8.0
"""The job budget, under RunPod's documented 10 MB `/run` ceiling, NUMERIC so it can be compared.

vis-b measured the same encoding on the same pictures: the largest six-image ATB post encodes to
3.68 MB, so a single page sits far below this and the packing is what keeps a multi-page job under
the wire. A page over budget on its own is a refusal — see the module docstring."""

ENDPOINT_ENV = "RUNPOD_POSITIONS_ENDPOINT"
JOB_TIMEOUT_S = 900.0
JOB_TTL_S = 3600.0
"""Seconds. `serving.execution_policy` is the one place they become milliseconds.

SPEC 3.17 (10)(c): **no single job may be CAPABLE of billing past the remaining cap on its own.**
The projection gate below re-prices BETWEEN jobs and cannot see inside one, so the execution
timeout is the only thing bounding a wedged worker — and at 1800 s one such job bills
1800 x $0.00030669 = **$0.5520**, which is 1.58x the whole $0.35 cap with every guard here
reporting normally. 900 s bills $0.2760, under the cap on its own, and is still more than twice
the longest job the projection predicts: the text leg is ONE job carrying all 30 rows
(30 x 4.262 s x 3.125 decode uplift ~ 400 s) and the page leg's largest of 7 is 17 pages ~ 80 s.
`scripts/runbook_5b.md` and `scripts/runbook_srv2b.md` already create endpoints at
`--execution-timeout 900`.

The ttl is a DIFFERENT clock — it starts at submission, so it has to cover the queue as well as
the run — and 3.17 (10)(c) is about what a worker can bill, which is the execution one."""

IDLE_TAIL_SECONDS = 60.0
"""Seconds a serverless worker keeps billing after the last job, and a term in every projection.

Serverless bills wall uptime, not jobs: the worker stays up for the endpoint's `--idle-timeout`
before it scales to zero, and that tail is charged to whoever woke it. Every endpoint this repo's
runbooks create uses `--idle-timeout 60` (`scripts/runbook_5b.md`, `runbook_srv2b.md`,
`runbook_vis_b.md`), which is $0.0184 at the settled rate — larger than the $0.0104 of headroom the
projection's stated corner had before this term was added. A cap arithmetic that leaves it out is
short by more than the margin it is reasoning about."""

WARMUP_ROW = "Тестовий рядок поза пакетом: молоко 1 л 45,90 грн."
"""SPEC 3.17 (9): the paid session opens on NON-gold inputs before either leg touches gold. This
row is deliberately not one of the 30 — the pack's ids are checked against it — and the warm-up
image is generated, not a leaflet page. What the warm-up buys is the cold start and the proof that
the instrument answers at all, paid for on inputs no bar is scored on."""


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def anchor_key(phase: str = PHASE) -> str:
    return f"runpod_balance_at_{phase}_start"


def read_ledger(path: Path, balance_now: float, phase: str = PHASE, cap: float = CAP_USD) -> dict:
    """This session's anchor, created before the first job or refused if it is another's."""
    key = anchor_key(phase)
    if path.exists():
        ledger = json.loads(path.read_text(encoding="utf-8"))
        if key not in ledger:
            raise SystemExit(
                f"{path.name} carries no {key} — it is another phase's anchor. Spending"
                " against it would enforce this cap on the wrong balance."
            )
        return ledger
    return {
        key: balance_now,
        "cap_usd": cap,
        "note": (
            f"RunPod account balance read before the first job of {phase}, the paid session of"
            f" SPEC 3.17 (6)/(11). Session spend = this anchor minus the balance now, enforced"
            f" against the ${cap:.2f} cap the amendment pre-registered. The Phase 4 cap is enforced"
            " separately against results/spend_phase4.json, and neither anchor may be regenerated:"
            " delete this file and the counter silently restarts at today's balance."
        ),
        "runs": [],
    }


def spend_now(ledger: dict, phase: str = PHASE) -> tuple[float, float]:
    """(balance, spend). The delta is a FLOOR — RunPod settles it minutes to hours late (Dv33)."""
    balance = guard.balance()
    return balance, float(ledger[anchor_key(phase)]) - balance


def spend_or_note(
    ledger: dict | None, phase: str = PHASE
) -> tuple[float | None, float | None, str | None]:
    """:func:`spend_now`, or (None, None, why) — a balance read must never lose the run's record.

    `guard.balance()` shells out to `runpodctl` and parses its JSON, so it can die on a network
    blip, a CLI update, an auth expiry or a schema change. Read AFTER the paid legs, and every one
    of those failures would have aborted `main` between the last paid call and the only write of
    the record — which, in a session that gets ONE attempt, throws away the evidence rather than
    the money. The anchor file survives regardless, so the spend stays recoverable by hand.

    The catch is deliberately blind. Narrowing it to the exceptions this path is known to raise
    would re-open the hole for the next one, and there is nothing above this frame that could do
    anything useful with the exception anyway.
    """
    if ledger is None:
        return None, None, None
    try:
        balance, spent = spend_now(ledger, phase)
    except Exception as err:  # noqa: BLE001 — see the docstring: the record outranks the reason
        return (
            None,
            None,
            f"the balance read failed after the paid legs: {type(err).__name__}: {err}",
        )
    return balance, spent, None


# --- the two populations ------------------------------------------------------------------------


def pages(reference: dict, root: Path = REPO_ROOT) -> list[dict]:
    """The 108 pages the reference names as SENT, each verified against the bytes on disk.

    Never the 159 available. Bar 1's gold is one Opus reviewer's reading of the sent set, so a
    brand printed on a page nobody sent is not in the gold and reading it would be scored as a
    false positive for being right (`sku_pilot_prereg_v2.json :: R2`).

    The sha is re-checked here rather than trusted from `images_verified`: that field records what
    was true when the reference was built, and a page whose bytes moved since is a different image
    under a gold set that was written against the old one.
    """
    out, missing, moved = [], [], []
    for post in reference["posts"]:
        for page in post["pages_sent"]:
            path = root / page["file"]
            if not path.exists():
                missing.append(page["file"])
                continue
            if sha256(path.read_bytes()).hexdigest() != page["sha256"]:
                moved.append(page["file"])
                continue
            url = media.data_url(path)
            out.append(
                {
                    "item": post["item"],
                    "page": page["page"],
                    "file": page["file"],
                    "sha256": page["sha256"],
                    "url": url,
                    "bytes": len(url),
                }
            )
    if missing or moved:
        raise SystemExit(
            f"{len(missing)} page(s) are not on disk and {len(moved)} no longer hash to what"
            f" {rel(REFERENCE)} pinned — {', '.join((missing + moved)[:3])}…. The gold was written"
            " against those bytes; stop and report rather than sending whatever is there now."
        )
    return out


def rows(manifest: dict, path: Path) -> list[dict]:
    """The 30 adjudicated rows, read back through the columns the operator was told not to touch.

    Two things are checked before a single row is sent, and both are cheap: the ids and their order
    against the manifest, and `given_sha256` over the given columns — a row whose `text` moved is a
    row adjudicated against a different question, and bar 3 would be scored on the new one.

    The five TICK columns are gold and are deliberately NOT read here. They are the answer; sending
    them to the model would be asking it to agree with itself.
    """
    with path.open(encoding="utf-8-sig", newline="") as handle:
        table = list(csv.DictReader(handle, delimiter=pack.DELIMITER))
    if [row["id"] for row in table] != manifest["ids"]:
        raise SystemExit(
            f"{rel(path)}: the ids or their order moved against {rel(MANIFEST)} — {len(table)} rows"
            f" against {len(manifest['ids'])}. This is not the pack the bar was registered on."
        )
    given = pack.given_sha256(table)
    if given != manifest["given_sha256"]:
        raise SystemExit(
            f"{rel(path)}: the given columns hash {given[:16]}… and the manifest pins"
            f" {manifest['given_sha256'][:16]}… — a row was adjudicated against a different question"
        )
    return [{key: row[key] for key in pack.GIVEN} for row in table]


def jobs(items: list[dict], budget_mb: float, key: str = "bytes") -> list[list[dict]]:
    """Whole items packed into jobs under a byte budget. Nothing is ever split or shrunk.

    A page is one request by construction (SPEC 3.17 (4)), so the packing unit is the page and a
    single page over budget is a refusal rather than a re-encode: dropping resolution to fit would
    silently change the instrument for exactly the densest pages.
    """
    budget = budget_mb * 1_000_000
    over = [item.get("file") or item.get("id") for item in items if item.get(key, 0) > budget]
    if over:
        raise SystemExit(
            f"{', '.join(str(name) for name in over)} encode above the {budget_mb} MB job budget on"
            " their own. RunPod's /run ceiling is 10 MB; raise --max-payload-mb deliberately if"
            " there is room, but a page never travels re-encoded or without its own call."
        )
    out, current, size = [], [], 0
    for item in items:
        if current and size + item.get(key, 0) > budget:
            out.append(current)
            current, size = [], 0
        current.append(item)
        size += item.get(key, 0)
    return out + [current] if current else out


# --- the resume of SPEC 3.17 (11) ----------------------------------------------------------------

BOUGHT_BY = "bought_by"
"""The one column the resumed dump adds to the registered seventeen.

Bar 2 is a human reading rows against page images, and the merged dump carries rows from two paid
sessions. Which session bought a row is not decoration: it is what lets the team lead see that the
17-page prefix they already calibrated on is the same 17 rows, and it is the only place the
provenance can live once the two dumps are one file."""


def resume_plan(prereg: dict, pin_sha: str, root: Path = REPO_ROOT) -> dict:
    """What the resumed session may buy, and the refusals that decide it (SPEC 3.17 (11)(a)).

    Everything is read back through the registration rather than through the run record alone: the
    pre-registration is what was signed, the record is the evidence, and a resume is only honest
    when the two agree. Three refusals, and each one is a different way the same $0.19 gets spent
    twice:

    * **a pin that moved.** The record, the dump and the serving pin are pinned in
      `resume.bought_already`. A run against a moved record would buy against evidence nobody can
      re-derive — and a moved serving pin is (11)(b) broken: the resumed half would be a different
      instrument from the bought half, with one set of bars over both.
    * **an unbought id that already carries an answer.** If a page the registration lists as
      unbought turns up in the record's own outcomes, then the two disagree about what was bought
      and neither can be trusted to say which 121 elements are left.
    * **a registration that does not match the record.** The lists are compared as sets, not
      counted: 121 of the wrong ids is still 121.

    The third refusal of the brief — a BOUGHT id requested again — is not here. It guards the
    selection rather than the registration and fires in :func:`resume_population`, which is the code
    that could actually make that mistake.
    """
    resume = prereg.get("resume")
    if not resume:
        raise SystemExit(
            "the pre-registration carries no `resume` block: --resume runs under SPEC 3.17 (11) and"
            f" its registration is {rel(PREREG_RESUME)}. Pass --prereg pointing at it, or drop"
            " --resume — a resumed session registered under v2 would claim a cap and a population"
            " that record does not contain."
        )
    already = resume["bought_already"]
    run_record = root / already["run_record"]["path"]
    run_dump = root / already["dump"]["path"]
    for label, path, pinned in (
        ("the run record", run_record, already["run_record"]["sha256"]),
        ("the per-position dump", run_dump, already["dump"]["sha256"]),
    ):
        if not path.exists():
            raise SystemExit(
                f"{rel(path)} is not on disk, and {label} is what the resume buys around"
            )
        on_disk = sha256(path.read_bytes()).hexdigest()
        if on_disk != pinned:
            raise SystemExit(
                f"{label} hashes {on_disk[:16]}… and {rel(PREREG_RESUME)} pins {pinned[:16]}… —"
                " the resume is registered against bytes that have since moved. Stop and report;"
                " nothing here may be re-bought to make the numbers agree."
            )
    if pin_sha != already["serving_pin"]["sha256"]:
        raise SystemExit(
            f"the serving pin hashes {pin_sha[:16]}… and the registration pins"
            f" {already['serving_pin']['sha256'][:16]}… — SPEC 3.17 (11)(b) freezes the instrument,"
            " and a resumed half served under a different configuration is not the same instrument"
            " the 17 bought answers came from."
        )

    run = json.loads(run_record.read_text(encoding="utf-8"))
    asked = {row["source"] for row in run["outcomes"]}
    registered = set(already["unbought"])
    answered = sorted(registered & asked)
    if answered:
        raise SystemExit(
            f"{len(answered)} id(s) the registration lists as UNBOUGHT already carry an answer in"
            f" {rel(run_record)} — {', '.join(answered[:3])}…. (11)(a) buys each element exactly"
            " once and these two artifacts disagree about which were bought. Stop and report."
        )
    if registered != set(run["population"]["unbought"]):
        raise SystemExit(
            f"{rel(PREREG_RESUME)} registers {len(registered)} unbought ids and {rel(run_record)}"
            f" names {len(run['population']['unbought'])} — and they are not the same set. The"
            " resumed population is what was REGISTERED; a run against a different one is a"
            " different sample."
        )
    return {
        "prereg": resume,
        "to_buy": registered,
        "already_asked": asked,
        "run": run,
        "run_record": run_record,
        "run_dump": run_dump,
    }


def resume_population(items: list[dict], plan: dict, leg: str) -> list[dict]:
    """The leg's items narrowed to what is still unbought, in the registered order.

    The refusal here is the one the brief calls "a bought id is requested again", and it guards
    THIS function: a filter that inverted its condition, or an id space that looked comparable and
    was not, would send the paid run at pages somebody already paid for. It is checked on what is
    about to travel rather than on what was registered, because that is the value that ends up on
    the wire.
    """
    keep = [
        item | {BOUGHT_BY: RESUME_PHASE}
        for item in items
        if (item.get("file") or item["id"]) in plan["to_buy"]
    ]
    rebought = [
        item.get("file") or item["id"]
        for item in keep
        if (item.get("file") or item["id"]) in plan["already_asked"]
    ]
    if rebought:
        raise SystemExit(
            f"the {leg} leg selected {len(rebought)} id(s) the first session already bought —"
            f" {', '.join(rebought[:3])}…. SPEC 3.17 (11)(a): each element is bought EXACTLY ONCE"
            " across the program, and there is no second draw for any of them."
        )
    return keep


def merge_sessions(plan: dict, outcomes: list[dict], dumped: list[dict]) -> dict:
    """Both paid sessions as ONE bar input, every row naming the session that bought it.

    The bars are registered over the whole population — 108 pages and 30 rows — and after a resume
    that population lives in two records. Scoring from either alone would report a fraction of a
    bar as the bar; scoring from a hand-merged pair would be an artifact nobody can re-derive. So
    the merge happens here, in the run that knows both halves, and the result is what the team lead
    and the scorer read.

    The invariant of SPEC 3.17 (11)(a) is checked on the OUTPUT rather than on the plan: no source
    appears twice in the merged outcomes. The plan's refusals guard the inputs, and this one guards
    the thing that would actually be scored — a duplicate here means an element was bought twice,
    and no cap or gate downstream can see it.
    """
    previous_rows = [
        json.loads(line) | {BOUGHT_BY: PHASE}
        for line in plan["run_dump"].read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    previous_outcomes = [row | {BOUGHT_BY: PHASE} for row in plan["run"]["outcomes"]]
    for row in outcomes:
        row[BOUGHT_BY] = RESUME_PHASE
    merged = previous_outcomes + outcomes
    twice = [source for source, n in Counter(row["source"] for row in merged).items() if n > 1]
    if twice:
        raise SystemExit(
            f"{len(twice)} source(s) carry an answer from BOTH sessions — {', '.join(twice[:3])}…."
            " SPEC 3.17 (11)(a) buys each element exactly once; the merged record would score one"
            " of them twice and nothing downstream could see it. Stop and report."
        )
    return {
        "outcomes": merged,
        "dumped": previous_rows + dumped,
        "previous": {
            "phase": PHASE,
            "record": rel(plan["run_record"]),
            "record_sha256": sha256(plan["run_record"].read_bytes()).hexdigest(),
            "dump": rel(plan["run_dump"]),
            "dump_sha256": sha256(plan["run_dump"].read_bytes()).hexdigest(),
            "prereg": plan["run"]["prereg"],
            "asked": len(previous_outcomes),
            "dump_rows": len(previous_rows),
        },
    }


def resume_warmup_inputs(prereg_resume: dict, reference: dict, manifest: dict, root: Path) -> dict:
    """SPEC 3.17 (11)(c)'s two REGISTERED warm-up inputs, re-verified before they are sent.

    Read out of the pre-registration and not re-picked. The rule that chose them is the producer's
    (`write_sku_prereg.resume_warmup`), and re-deriving it here would be a second implementation
    that can disagree with the registered one — with the disagreement landing on the go/no-go's
    input, which is the number this whole amendment exists to fix.

    What IS re-checked is the property (11)(c) cares about: neither input is gold. A registered
    page that had drifted into the 108 sent ones would spend a warm-up on a page bar 1 scores, and
    a registered row inside the 30 would do the same to bar 3. Both hashes are re-derived too — the
    page from disk and the row from the raw store — because a warm-up that priced a different input
    than the registered one is the 64x64 failure with better paperwork.
    """
    warmup = prereg_resume["warmup"]
    sent = {page["file"] for post in reference["posts"] for page in post["pages_sent"]}
    page_file = warmup["page"]["file"]
    if page_file in sent:
        raise SystemExit(
            f"{page_file} is one of the {len(sent)} SENT pages: the registered warm-up page is"
            " inside bar 1's page set (R2) and a warm-up answer on it would be paid for on gold."
        )
    page_path = root / page_file
    if not page_path.exists():
        raise SystemExit(f"{page_file}: the registered warm-up page is not on disk")
    page_sha = sha256(page_path.read_bytes()).hexdigest()
    if page_sha != warmup["page"]["sha256"]:
        raise SystemExit(
            f"{page_file} hashes {page_sha[:16]}… and the registration pins"
            f" {warmup['page']['sha256'][:16]}… — the warm-up would price a different image"
        )

    row = warmup["text"]
    if row["id"] in set(manifest["ids"]):
        raise SystemExit(
            f"{row['id']} is one of the 30 adjudicated rows: the registered warm-up row is inside"
            " bar 3's gold and 3.17 (9) opens on inputs NO bar is scored on."
        )
    text = pack.store_text({"id": row["id"], "carrier": row["carrier"]})
    text_sha = sha256(text.encode("utf-8")).hexdigest()
    if text_sha != row["text_sha256"]:
        raise SystemExit(
            f"{row['id']} reads {len(text)} chars hashing {text_sha[:16]}… and the registration"
            f" pins {row['text_sha256'][:16]}… — the raw store moved under a registered input"
        )
    return {
        "page_url": media.data_url(page_path),
        "text": text,
        "page": {"file": page_file, "sha256": page_sha, "bytes": page_path.stat().st_size},
        "row": {"id": row["id"], "carrier": row["carrier"], "text_sha256": text_sha},
    }


# --- the dump's columns, read out of the pre-registration ----------------------------------------

PHRASE_FIELDS = {
    "page number": ("page",),
    "the page's file and sha256": ("file", "sha256"),
    "the code-assigned tier": ("tier",),
    "depth()": ("depth",),
    "depth_disagrees_with_printed()": ("depth_disagrees_with_printed",),
}
"""The only prose in the registered sentence that is not already a field name. Everything else —
`item`, `brand_raw`, `brand_id`, `line`, `category`, `size`, `fat`, the three price fields and
`price_qualifier` — is itself."""


def dump_fields(prereg: dict) -> tuple[str, ...]:
    """The dump's columns, DERIVED from `bars.price_pair_accuracy.procedure`, not copied.

    The team lead reads this dump against the page images and marks each price pair correct or
    incorrect; that is bar 2. A column list retyped here could drift from the sentence that was
    registered, and the drift would show up as a field the reader expected and did not get — or,
    worse, as a column silently named something the gold does not describe.

    Note what the sentence says: `fat`. The pre-registration keeps every bar byte-equal to v1, so
    the procedure was written before the schema field became `attribute` (SPEC 3.17 (8)) — which
    makes this the WIRE name, and :func:`row_for` looks it up through `positions.wire_key`.
    """
    sentence = prereg["bars"]["price_pair_accuracy"]["procedure"]
    listed = sentence.split("carrying ", 1)[1].split(". ", 1)[0]
    out: list[str] = []
    for chunk in (part.strip() for part in listed.split(", ")):
        # a whole chunk first: "the page's file and sha256" carries an `and` INSIDE one phrase,
        # and splitting before looking it up produced a column literally called
        # "the page's file" — legal-looking, unreadable by the team lead, caught by the shape
        # check below rather than by review
        if chunk in PHRASE_FIELDS:
            out.extend(PHRASE_FIELDS[chunk])
            continue
        for phrase in (part.strip() for part in chunk.split(" and ")):
            out.extend(PHRASE_FIELDS.get(phrase, (phrase,)))
    unnamed = [field for field in out if not field.isidentifier()]
    if unnamed:
        raise SystemExit(
            f"{unnamed} came out of the registered sentence as prose rather than as field names —"
            f" PHRASE_FIELDS does not cover it. The dump's columns are what bar 2 is read off;"
            " stop and report rather than writing a column nobody can address."
        )
    return tuple(out)


def row_for(position: positions.Position, source: dict, fields: tuple[str, ...]) -> dict:
    """One extracted position as the dump's row, in the registered column order."""
    attribute = positions.wire_key("attribute", FAMILY)
    values = {
        "item": source.get("item") or source.get("id"),
        "page": source.get("page"),
        "file": source.get("file"),
        "sha256": source.get("sha256"),
        "brand_raw": position.brand_raw,
        "brand_id": position.brand_id,
        "line": position.line,
        "category": position.category,
        "size": None
        if position.size_value is None
        else f"{position.size_value:g} {position.size_unit}",
        attribute: position.attribute_pct,
        "price_promo": position.price_promo,
        "price_old": position.price_old,
        "discount_pct_printed": position.discount_pct_printed,
        "price_qualifier": position.price_qualifier,
        "tier": position.tier(),
        "depth": position.depth(),
        "depth_disagrees_with_printed": position.depth_disagrees_with_printed(),
        # only in the resumed session's column list; the item carries it, so a row cannot be
        # stamped with a session it did not travel in
        BOUGHT_BY: source.get(BOUGHT_BY),
    }
    missing = [field for field in fields if field not in values]
    if missing:
        raise SystemExit(
            f"the pre-registration's dump sentence names {missing}, which this writer cannot"
            " produce. The bar is read off these columns — stop and report."
        )
    return {field: values[field] for field in fields}


# --- the run ------------------------------------------------------------------------------------


class FakeEndpoint:
    """`--smoke`: the whole path, no network, no spend. Two replies are broken ON PURPOSE.

    One reply is unparseable and one is `[]`, because those two are the outcomes the record must
    keep apart: a refusal is counted by reason and excluded from the bar's denominator, and an
    empty array is a page the model says has no dairy on it.
    """

    SMOKE_BOOT_SECONDS = 183.58
    """vis-c's measured cold start (`results/captions_gm4_visc.json`). A SYNTHETIC clock, and the
    record says so (`timing.smoke: true`) — but a fake whose `timing()` reported nothing left the
    §C.1 gate with a marginal of zero, which is a gate that can never fire and therefore a gate
    nothing proves. Its first real call raised `KeyError` on this very dict."""

    SMOKE_SECONDS_PER_CALL = 2.5
    """Between vis-b's 2.34 s/image and srv-2d's 4.26 s/row, so a smoke at the real population
    projects into the same order of magnitude the $0.35 cap lives in."""

    WARMUP_CALLS = 2
    """SPEC 3.17 (9) makes exactly two non-gold calls, and the fake has to know where they end.

    ``gold_seconds_per_call`` defaults to the same rate, so nothing changes unless a caller asks
    for it. What it buys is the one scenario the IN-RUN gate exists for and the go/no-go of
    3.17 (10)(a) cannot cover: a warm-up that priced cheap and legs that turned out expensive. On
    a flat clock the two gates compute the identical number by construction — if the go/no-go
    passes, the in-run stop can never fire — so a fake that could not get slower would have left
    the mid-leg path unprovable through `main`."""

    def __init__(
        self, worker: dict, categories, gold_seconds_per_call: float | None = None
    ) -> None:
        self.gold_seconds_per_call = (
            self.SMOKE_SECONDS_PER_CALL if gold_seconds_per_call is None else gold_seconds_per_call
        )
        self.worker = worker
        self.jobs = 0
        self.calls = 0
        self.dump_path = None
        self.asked: list[tuple[str, int]] = []
        # The category the fake answers with is checked against the registry's own keys. Without
        # this the smoke reported 111 of 138 sources unreadable — the fake said «морозиво» and the
        # taxonomy is keyed `ice-cream` — and that reads exactly like a finding about the parser
        # instead of a defect in the fixture. A probe must not create what it measures.
        self.category = "ice-cream"
        if self.category not in categories:
            raise SystemExit(
                f"the smoke answers with category {self.category!r}, which config/registry.yaml"
                f" does not carry ({sorted(categories)}). Every reply would be refused and the"
                " smoke would prove the opposite of what it exists to prove."
            )

    def info(self) -> dict:
        # counted, because the real client counts it: `EndpointClient._run` increments `calls` for
        # every terminal submission and the handshake is one. A fake whose `calls` skipped it would
        # make `cost.jobs_submitted` mean one thing under test and another in production — which is
        # the shape of the Dv153 defect this field exists to close.
        self.jobs += 1
        return dict(self.worker) | {"weights_dir": "<smoke>"}

    def positions(self, task: str, items: list) -> list[dict]:
        if task not in prompts.POSITIONS:
            raise ValueError(f"{task}: the smoke serves {sorted(prompts.POSITIONS)}")
        self.jobs += 1
        self.calls += len(items)
        self.asked.append((task, len(items)))
        replies = []
        for index, _ in enumerate(items):
            seat = self.jobs * 10 + index
            if seat % 7 == 0:
                content = '[{"brand": "Рудь", '  # truncated mid-object: a parse failure
            elif seat % 5 == 0:
                content = "[]"  # a page with nothing tracked on it — NOT a failure
            else:
                content = (
                    '[{"brand": "Рудь", "category": "' + self.category + '", "size": "450 г",'
                    ' "fat": "12%", "price_promo": "89,90 грн", "price_old": "129,90 грн",'
                    ' "discount_pct_printed": "-31%"}]'
                )
            replies.append(
                {
                    "content": content,
                    "finish_reason": "length" if seat % 7 == 0 else "stop",
                    "cost": 0.0,
                    "usage": {"prompt_tokens": 0, "completion_tokens": 0},
                    "generation_id": None,
                }
            )
        return replies

    def timing(self) -> dict:
        """A synthetic clock, labelled as one. `worker_seconds` is what the gate divides by, so a
        fake that reported none made the projection unmeasurable and its arithmetic unprovable."""
        warm = min(self.calls, self.WARMUP_CALLS)
        gold = max(self.calls - self.WARMUP_CALLS, 0)
        return {
            "calls": self.jobs,
            "rows": self.calls,
            "worker_seconds": round(
                self.SMOKE_BOOT_SECONDS
                + warm * self.SMOKE_SECONDS_PER_CALL
                + gold * self.gold_seconds_per_call,
                3,
            ),
            "wall_seconds": 0.0,
            "smoke": True,
        }


def parse(reply: dict, carrier: str, task: str, categories, aliases) -> tuple[list, str | None]:
    """One reply → its positions, or (—, reason). A refusal is a REASON, never an empty answer."""
    try:
        found = positions.parse_positions(
            reply.get("content") or "",
            categories=categories,
            carrier=carrier,
            price_origin=positions.origin_of(carrier)
            if carrier in positions.CARRIER_ORIGIN
            else "retail_leaflet",
            extraction_source=task,
            aliases=aliases,
            family=FAMILY,
        )
    except positions.SchemaError as err:
        return [], err.reason
    return found, None


def run_leg(
    client,
    task: str,
    carrier_of,
    packed: list[list[dict]],
    categories,
    aliases,
    fields: tuple[str, ...],
    dump_prefix: str | None,
    on_job,
    outcomes: list[dict],
    dumped: list[dict],
    stop=None,
) -> str | None:
    """One job per pack, in order, appending to the RUN's outcome and dump lists.

    Returns the reason the RUN ended, or None if this leg simply finished. A job the CLOCK killed
    (`serving.JobExpired` — RunPod's `TIMED_OUT`, or the client's deadline) ends the whole run and
    not just the batch, per SPEC 3.17 (10)(c): it billed the entire execution timeout, so nothing
    about it says the next job will be cheaper, and the one-attempt clause forfeits its items
    either way. Every OTHER job failure stays what it was — named against its items, and the leg
    continues.

    A job that fails is named against every source in it and never re-asked; ``stop`` is the
    re-projection gate and the sources it skips are left out of the outcomes rather than marked
    failed — nothing was asked for them.

    ``outcomes`` and ``dumped`` are the run's accumulators, not this leg's, and that is the whole
    point: the gate prices what the SESSION has spent against what the SESSION will spend, and a
    per-leg counter would restart the arithmetic at zero when the text leg opened while the billed
    seconds carried the whole page leg.

    **Their order matters and they are not what comes back.** They are mutated in place and they
    are the only two list arguments here; a caller that swapped them would write an empty dump
    beside outcomes full of extraction rows, and every count downstream would still add up.
    """

    def forfeit(index: int, batch: list[dict], err) -> None:
        outcomes.extend(
            {
                "source": item.get("file") or item["id"],
                "item": item.get("item") or item.get("id"),
                "n_positions": None,
                "unreadable": f"job {index}: {err}",
            }
            for item in batch
        )

    for index, batch in enumerate(packed):
        if stop is not None and (reason := stop()):
            print(f"  STOP before {task} job {index:02d}: {reason}", flush=True)
            return None
        if dump_prefix is not None:
            client.dump_path = f"{dump_prefix}_{task}_{index:02d}.jsonl"
        # a page travels as a ONE-image album (SPEC 3.17 (4)); a row travels as its text
        payload = [[item["url"]] if "url" in item else item["text"] for item in batch]
        try:
            replies = client.positions(task, payload)
        except serving.JobExpired as err:
            forfeit(index, batch, err)
            on_job(index, batch, None)
            print(f"  RUN ENDS on {task} job {index:02d}: the clock killed it", flush=True)
            return (
                f"{task} job {index} was ended by the CLOCK ({err}). SPEC 3.17 (10)(c): a job that"
                f" ends TIMED_OUT billed the whole {JOB_TIMEOUT_S:.0f}s execution timeout and says"
                " nothing about the next one, so the run ends and its remainder is unbought"
            )
        except (ApiError, ValueError, OSError) as err:
            forfeit(index, batch, err)
            on_job(index, batch, None)
            continue
        for item, reply in zip(batch, replies):
            carrier = carrier_of(item)
            found, reason = parse(reply, carrier, task, categories, aliases)
            outcomes.append(
                {
                    "source": item.get("file") or item["id"],
                    "item": item.get("item") or item.get("id"),
                    "carrier": carrier,
                    "n_positions": None if reason else len(found),
                    "unreadable": reason,
                    "finish_reason": reply.get("finish_reason"),
                    "sha8": sha256(
                        serving.positions_key(
                            [item["url"]] if "url" in item else item["text"]
                        ).encode("utf-8")
                    ).hexdigest()[:8],
                }
            )
            dumped += [row_for(position, item, fields) for position in found]
        on_job(index, batch, replies)


def billed_seconds(client) -> float:
    """What the worker reports as billed so far, or 0.0 when it does not report at all.

    Read through ``.get`` and not ``[...]``: `timing()` is a client's own dict and a client that
    never made a call has no ``worker_seconds`` in it. Indexing it raised `KeyError` inside the
    gate, which is a crash on the one path a $0 contract can prove and a paid run cannot afford.
    """
    return float((client.timing() or {}).get("worker_seconds") or 0.0)


def projection(*, opened_seconds: float, billed: float, done: int, total: int, rate: float) -> dict:
    """What the run will cost, from what it has ALREADY been billed. The stop reads this.

    Deliberately not `caption_gm4_5c1.projection`, which this driver otherwise follows. That one
    prices `rows_total x marginal + COLD_START_USD` — a caption constant (vis-b's $0.0733), which
    this contract has no business re-adding: the boot has already been billed by the time any gate
    runs, and adding a pre-registered figure on top of measured seconds double-counts it. Here
    everything paid is in ``billed`` and only what is LEFT is projected.

    ``opened_seconds`` is the clock after the `info` handshake AND the 3.17 (9) warm-up, so the
    marginal is the legs' own and carries neither the cold start nor the two non-gold calls. Those
    are still charged — they are inside ``billed`` — they are just not multiplied by 138.

    ``done`` and ``total`` count CALLS across both legs. The marginal is therefore a blend once the
    text leg opens, and that is the honest reading with one instrument and two input shapes: no
    artifact prices a positions call on either shape yet, so a per-leg rate table here would be two
    guesses instead of one measurement. It self-corrects — every gate re-reads the clock.

    :data:`IDLE_TAIL_SECONDS` is inside ``projected_usd`` and outside ``spent_usd``, which is what
    each of the two words means: the tail has not been billed yet and it WILL be, because the
    worker keeps running after the last job. It is not in the marginal either — it is charged once
    per session, not once per call.
    """
    marginal = (billed - opened_seconds) / max(done, 1)
    remaining = max(total - done, 0) * marginal
    return {
        "calls_done": done,
        "calls_total": total,
        "opened_seconds": round(opened_seconds, 3),
        "billed_seconds": round(billed, 3),
        "marginal_seconds_per_call": round(marginal, 4),
        "idle_tail_seconds": IDLE_TAIL_SECONDS,
        "spent_usd": round(billed * rate, 4),
        "remaining_usd": round(remaining * rate, 4),
        "projected_usd": round((billed + remaining + IDLE_TAIL_SECONDS) * rate, 4),
    }


def go_no_go(
    *,
    billed: float,
    page_marginal: float,
    text_marginal: float,
    n_pages: int,
    n_rows: int,
    rate: float,
    budget: float | None,
) -> dict:
    """SPEC 3.17 (10)(a): price the WHOLE run from the warm-up, before the first gold call.

    The in-run gate below cannot answer this question. It needs a gold call to have a marginal at
    all, so by the time it first fires the pilot has already bought something — and under the
    one-attempt clause a run stopped after two pages is the most expensive outcome available: the
    money is gone and no bar is scoreable. This is the one gate that can refuse while the session
    is still worth nothing, and (10)(a) says a session stopped here has consumed NO attempt.

    Each leg is priced from ITS OWN warm-up call, because the two shapes are not the same call:
    the page leg sends an image and the text leg sends a string. Two measurements of one call each
    is a thin instrument and it is the only one that exists before gold — the in-run gate re-prices
    on real volume from the first job onward.
    """
    gold_seconds = n_pages * page_marginal + n_rows * text_marginal
    projected = (billed + gold_seconds + IDLE_TAIL_SECONDS) * rate
    return {
        "when": "after the two non-gold warm-up calls of SPEC 3.17 (9), before the first gold call",
        "billed_seconds": round(billed, 3),
        "page_marginal_seconds": round(page_marginal, 4),
        "text_marginal_seconds": round(text_marginal, 4),
        "gold_calls": n_pages + n_rows,
        "gold_seconds": round(gold_seconds, 3),
        "idle_tail_seconds": IDLE_TAIL_SECONDS,
        "projected_usd": round(projected, 4),
        "budget_usd": budget,
        "refuse": budget is not None and round(projected, 4) > budget,
    }


def warmup(
    client,
    task_page: str,
    task_text: str,
    clock=None,
    page_url: str | None = None,
    text: str | None = None,
) -> dict:
    """SPEC 3.17 (9): a paid call on NON-gold inputs before either leg touches gold.

    A synthetic image and a row that is not in the 30-row pack. What it buys is the cold start and
    the proof that the instrument answers at all, on inputs no bar is scored on — so a worker that
    comes back unparseable costs the warm-up rather than a leg of the gold.

    It also buys the only per-leg price that exists before gold, which is why the clock is read
    BETWEEN the two calls rather than once at the end: :func:`go_no_go` prices 108 pages and 30
    rows separately, and a single blended figure would charge the image leg's seconds to the text
    leg's 30 calls. ``clock`` is :func:`billed_seconds` and is injected so a caller can prove the
    arithmetic without a worker.

    ``page_url`` and ``text`` are SPEC 3.17 (11)(c): for the RESUMED session the probe stops being
    synthetic. The first session's 64x64 image answered in 1.436 s, the go/no-go multiplied that by
    138 and let the run proceed, and the first real page cost 5.0772 s — the gate passed the run it
    exists to refuse, and the arithmetic was right. The inputs are the registered ones and this
    function does not choose them; it only sends what it is given.
    """
    clock = billed_seconds if clock is None else clock
    if page_url is None:
        import base64
        import io

        from PIL import Image

        buffer = io.BytesIO()
        Image.new("RGB", (64, 64), (240, 240, 240)).save(buffer, format="JPEG")
        page_url = "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")
    out, before = {}, clock(client)
    for task, item in ((task_page, [page_url]), (task_text, WARMUP_ROW if text is None else text)):
        reply = client.positions(task, [item])[0]
        now = clock(client)
        out[task] = {
            "content": (reply.get("content") or "")[:200],
            "finish_reason": reply.get("finish_reason"),
            "marginal_seconds": round(now - before, 4),
        }
        before = now
    return out


def main(argv: list[str] | None = None, client=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint-id", default="", help=f"or ${ENDPOINT_ENV}; NO default")
    parser.add_argument("--reference", type=Path, default=REFERENCE)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--pack", type=Path, default=None, help="default: the manifest's own pack")
    parser.add_argument("--prereg", type=Path, default=None, help=f"default: {rel(PREREG)}")
    parser.add_argument("--pin", type=Path, default=PIN)
    parser.add_argument("--ledger", type=Path, default=None, help=f"default: {rel(LEDGER)}")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="SPEC 3.17 (11): buy ONLY what results/sku_b_positions.json records as unbought",
    )
    parser.add_argument("--out", type=Path, default=None, help="the per-position dump (jsonl)")
    parser.add_argument("--record", type=Path, default=None)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--leg", choices=("page", "text", "both"), default="both")
    parser.add_argument("--max-payload-mb", type=float, default=MAX_PAYLOAD_MB)
    parser.add_argument("--dump-prefix", default=None, help="a path prefix on the network volume")
    parser.add_argument("--smoke", action="store_true", help="fake client, no network, no spend")
    parser.add_argument("--dry-run", action="store_true", help="the population and the jobs, stop")
    parser.add_argument(
        "--project-stop-usd",
        type=float,
        default=None,
        help="stop before a job once the run projects above this. Default: what is left of the cap",
    )
    args = parser.parse_args(argv)

    # Every default follows the mode, and each one is a way a resumed session could quietly be the
    # first one again: v2's registration has no resume block and a $0.35 cap, the first session's
    # anchor measures a balance from before its own $0.1965, and its artifacts are the evidence the
    # registration pins. A flag that changed the population and left the money and the paperwork
    # pointing at the interrupted run would enforce the wrong cap over the right pages.
    args.prereg = args.prereg or (PREREG_RESUME if args.resume else PREREG)
    args.ledger = args.ledger or (RESUME_LEDGER if args.resume else LEDGER)
    phase = RESUME_PHASE if args.resume else PHASE
    cap = RESUME_CAP_USD if args.resume else CAP_USD

    out = args.out or (RESUME_DUMP if args.resume else DUMP)
    record_path = args.record or (RESUME_RECORD if args.resume else RECORD)
    if args.smoke:
        # A smoke on the real paths fills the paid artifacts with fake extractions and then makes
        # the real run refuse to overwrite them. The 4.5g2 redirect, for the same reason.
        #
        # Each path redirects on ITS OWN default. The redirect used to need BOTH of them unset, so
        # `--smoke --out /tmp/x` wrote a fake RECORD at results/sku_b_positions.json — the exact
        # artifact the paid run then refuses to overwrite, planted by the $0 path.
        smoke = REPO_ROOT / "results" / "smoke"
        out = out if args.out else smoke / out.name
        record_path = record_path if args.record else smoke / record_path.name

    reference = json.loads(args.reference.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    prereg = json.loads(args.prereg.read_text(encoding="utf-8"))
    pin = json.loads(args.pin.read_text(encoding="utf-8"))
    fields = dump_fields(prereg)

    plan = (
        resume_plan(prereg, sha256(args.pin.read_bytes()).hexdigest(), args.root)
        if args.resume
        else None
    )

    page_items = pages(reference, args.root) if args.leg in ("page", "both") else []
    pack_path = args.pack or (args.root / manifest["pack"])
    text_items = []
    if args.leg in ("text", "both"):
        text_items = [
            row | {"bytes": len(row["text"].encode("utf-8"))} for row in rows(manifest, pack_path)
        ]
        if any(row["text"].strip() == WARMUP_ROW.strip() for row in text_items):
            raise SystemExit(
                "the warm-up row is one of the 30 — 3.17 (9) opens on inputs NO bar is scored on"
            )
    registered_pages, registered_rows = len(page_items), len(text_items)
    if plan is not None:
        page_items = resume_population(page_items, plan, "page")
        text_items = resume_population(text_items, plan, "text")
        fields = (*fields, BOUGHT_BY)

    page_jobs = jobs(page_items, args.max_payload_mb)
    text_jobs = jobs(text_items, args.max_payload_mb)

    print(
        f"page leg   {len(page_items)} pages sent"
        f" (of {reference['population']['pages_available']} available,"
        f" {reference['population']['posts']} posts) in {len(page_jobs)} job(s),"
        f" largest {max((sum(p['bytes'] for p in j) for j in page_jobs), default=0) / 1e6:.2f} MB"
        f"\ntext leg   {len(text_items)} rows in {len(text_jobs)} job(s)"
        f"\ndump       {len(fields)} columns: {', '.join(fields)}"
    )
    if plan is not None:
        already = plan["prereg"]["bought_already"]
        print(
            f"resume     SPEC 3.17 (11) under {rel(args.prereg)}"
            f"\n  bought    {already['n_asked']} of"
            f" {registered_pages + registered_rows} by {rel(plan['run_record'])}, never re-asked"
            f"\n  to buy    {len(page_items)} page(s) + {len(text_items)} row(s)"
            f" = {len(page_items) + len(text_items)} of {already['n_unbought']} registered"
            f"\n  cap       ${cap:.2f} (11)(d) · anchor {rel(args.ledger)}"
        )
    if args.dry_run:
        for item in page_items[:3]:
            print(f"  page {item['item']} p{item['page']} {item['bytes'] / 1e6:.2f} MB")
        for row in text_items[:3]:
            print(f"  row  {row['id']} {row['carrier']} {row['text'][:60]}…")
        return 0

    # BELOW the dry run on purpose. `--dry-run` writes nothing, and the paid artifacts exist
    # forever once a session has bought them — with this check above the early return, the $0 path
    # the run contract puts in its first gate stops working the day it is first needed to look at
    # the population without spending.
    for path in (out, record_path):
        if path.exists():
            raise SystemExit(
                f"{path} already exists — it is what a paid run bought. Re-running would spend"
                " again and overwrite the only copy: give --out/--record another path."
            )

    registry = load_registry(args.root / rel(REGISTRY))
    categories = positions.category_keys(registry.taxonomy)
    aliases = watchlist_aliases(registry.watchlist)

    endpoint_id = args.endpoint_id or os.environ.get(ENDPOINT_ENV, "")
    ledger, spent_before = None, None
    if client is not None:
        pass
    elif args.smoke:
        client = FakeEndpoint(pin["expected_worker"], categories)
    else:
        if not endpoint_id:
            raise SystemExit(
                f"no endpoint id: pass --endpoint-id or set ${ENDPOINT_ENV}. There is no default"
                " on purpose — a run against whatever id was last in a shell variable is a run"
                " against an unknown configuration."
            )
        from eval_zero_shot import runpod_api_key  # noqa: PLC0415

        balance = guard.balance()
        ledger = read_ledger(args.ledger, balance, phase, cap)
        args.ledger.parent.mkdir(parents=True, exist_ok=True)
        args.ledger.write_text(
            json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )  # anchored before the first job, never after
        balance, spent_before = spend_now(ledger, phase)
        print(f"ledger: spent ${spent_before:.4f} of ${cap:.2f} (balance ${balance:.2f})")
        if spent_before >= cap:
            raise SystemExit(
                f"REFUSED: the ${cap:.2f} cap is reached (${spent_before:.4f} spent). Stop and"
                " report — an overrun aborts, it does not raise the cap."
            )
        client = serving.EndpointClient(
            endpoint_id,
            runpod_api_key(),
            forward_batch_size=1,  # SPEC 3.17 (9): batch 1, always
            policy=serving.execution_policy(JOB_TIMEOUT_S, JOB_TTL_S),
            job_timeout=JOB_TTL_S + 300.0,
            submit="run",
        )

    # The identity stop. Not one value of `expected_worker` is restated here: the pin is the check.
    info = serving.assert_serving(client.info(), pin["expected_worker"])
    print(
        f"endpoint       {endpoint_id or '<smoke>'} · {info['serving_config']}/{info['merge_state']}"
        f"\n  revision      {info.get('revision_requested')}"
        f"\n  ceiling       {info.get('max_new_tokens')} new tokens, greedy, batch 1"
        f"\n  prompts       "
        + " · ".join(f"{k} {v[:12]}…" for k, v in info["positions_prompt_sha256"].items())
    )

    started = datetime.now(UTC).isoformat(timespec="seconds")
    # after `info` and before the warm-up: on a cold endpoint this is the weight load
    boot_seconds = billed_seconds(client)
    rate = leader.rate_usd_per_second()

    calls_total = len(page_items) + len(text_items)
    budget = args.project_stop_usd
    if ledger is not None:
        # `--project-stop-usd` TIGHTENS the cap, it never replaces it. It used to be taken as the
        # budget outright, so a value above what is left of the $0.35 cap disabled the in-run stop
        # entirely — a flag that reads like a safety knob and can only ever loosen the one guard.
        left = round(cap - spent_before, 4)
        budget = left if budget is None else min(budget, left)
    projections: list[dict] = []

    # everything both records carry, built once so the go/no-go stop below cannot drift from the
    # record a completed run writes
    head = {
        "timestamp": started,
        "phase": (
            "sku-b — the position-layer pilot, the resumed session"
            if args.resume
            else "sku-b — the position-layer pilot, one paid attempt"
        ),
        "contract": (
            "docs/PROMPT-sku-b-v3-prep.md deliverable 2; docs/SPEC.md amendment 3.17 (9), (10), (11)"
            if args.resume
            else "docs/PROMPT-sku-b-prep.md deliverable 2 + docs/PROMPT-sku-b-prep-fix.md;"
            " docs/SPEC.md amendment 3.17 (6), (9), (10)"
        ),
        "prereg": {
            "path": rel(args.prereg),
            "sha256": sha256(args.prereg.read_bytes()).hexdigest(),
        },
        "serving_pin": {
            "path": rel(args.pin),
            "sha256": sha256(args.pin.read_bytes()).hexdigest(),
        },
        "endpoint": {"id": endpoint_id or None, "worker": info},
        "smoke": bool(args.smoke),
        "attempts_per_job": 1,
    }

    probe = (
        resume_warmup_inputs(plan["prereg"], reference, manifest, args.root)
        if plan is not None
        else None
    )
    opened = warmup(
        client,
        prompts.POSITIONS_TASK_PAGE,
        prompts.POSITIONS_TASK_TEXT,
        page_url=None if probe is None else probe["page_url"],
        text=None if probe is None else probe["text"],
    )
    for task, reply in opened.items():
        print(
            f"  warm-up {task:<20} {reply['finish_reason']}"
            f"  {reply['marginal_seconds']}s  {reply['content'][:50]}"
        )
    # after the warm-up: everything charged before the first gold call. The legs' marginal is
    # measured from HERE, so neither the cold start nor the two non-gold calls is multiplied by 138
    opened_seconds = billed_seconds(client)

    warmup_block = {
        "why": "SPEC 3.17 (9): a call on NON-gold inputs before either leg touches gold",
        "inputs": (
            {"page": "a generated 64x64 image", "text": WARMUP_ROW}
            if probe is None
            else {
                "page": probe["page"],
                "text": probe["row"],
                "why": (
                    "SPEC 3.17 (11)(c): REPRESENTATIVE and still non-gold. The page is one of the 51"
                    " the reference records as never sent and the row is one the pre-filter passed"
                    " and the 30-row pack did not draw — both registered in"
                    f" {rel(args.prereg)} :: resume.warmup and re-verified here against the bytes"
                ),
            }
        ),
        "replies": opened,
    }
    verdict = go_no_go(
        billed=opened_seconds,
        page_marginal=opened[prompts.POSITIONS_TASK_PAGE]["marginal_seconds"],
        text_marginal=opened[prompts.POSITIONS_TASK_TEXT]["marginal_seconds"],
        n_pages=len(page_items),
        n_rows=len(text_items),
        rate=rate,
        budget=budget,
    )
    print(
        f"  go/no-go      {verdict['gold_calls']} gold calls project"
        f" ${verdict['projected_usd']:.4f}"
        + (
            "  (no budget: nothing to refuse against)"
            if budget is None
            else f" against ${budget:.4f} left of the cap"
            f" — {'REFUSE' if verdict['refuse'] else 'proceed'}"
        ),
        flush=True,
    )
    if verdict["refuse"]:
        # SPEC 3.17 (10)(a). No gold call is made, so no gold artifact exists: the dump is never
        # written, and this record is the whole output of the session. The attempt is NOT consumed.
        balance, spent, cost_note = spend_or_note(ledger, phase)
        record_path.parent.mkdir(parents=True, exist_ok=True)
        record_path.write_text(
            json.dumps(
                head
                | {
                    "stopped_before_gold": True,
                    "why": (
                        "SPEC 3.17 (10)(a): after the two non-gold warm-up calls the whole run"
                        f" projects ${verdict['projected_usd']:.4f} against ${budget:.4f} left of"
                        f" the ${cap:.2f} cap. Refused BEFORE the first gold call, which is the"
                        " only stop that leaves nothing half-bought — and under (10)(a) it consumes"
                        " NO attempt. The pilot returns to the team lead for a re-registration"
                        " under the measured price"
                    ),
                    "warmup": warmup_block,
                    "population": {
                        "pages_sent": len(page_items),
                        "text_rows": len(text_items),
                        "asked": 0,
                        "unbought": sorted(
                            (item.get("file") or item["id"])
                            for packed in (page_jobs, text_jobs)
                            for job in packed
                            for item in job
                        ),
                    },
                    "dump": {"path": None, "rows": 0, "why": "no gold call was made"},
                    "projection": {
                        "rate_usd_per_second": rate,
                        "rate_source": "results/srv2d_cost.json :: rate.usd_per_second",
                        "stop_at_usd": budget,
                        "boot_seconds": round(boot_seconds, 3),
                        "boot_usd": round(boot_seconds * rate, 4),
                        "warmup_seconds": round(opened_seconds - boot_seconds, 3),
                        "opened_seconds": round(opened_seconds, 3),
                        "go_no_go": verdict,
                        "per_gate": [],
                    },
                    "cost": {
                        "jobs": 0,
                        "usd": None if spent is None else round(spent, 4),
                        "cap_usd": cap,
                        "anchor": rel(args.ledger),
                        "read_failed": cost_note,
                        "reading": (
                            "what the handshake and the two warm-up calls cost. A FLOOR — the"
                            " balance settles minutes to hours behind the resource (Dv33)"
                        ),
                    },
                    "timing": client.timing(),
                    "git": provenance.git_state(record_path),
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        raise SystemExit(
            f"REFUSED before the first gold call: the run projects"
            f" ${verdict['projected_usd']:.4f} against ${budget:.4f} left of the ${cap:.2f}"
            f" cap (SPEC 3.17 (10)(a)). No gold call was made and NO attempt was consumed —"
            f" {rel(record_path)} is the record. Stop and report; the pilot needs a re-registration"
            " under the measured price, not a raised cap."
        )

    def gate() -> str | None:
        """Re-price the whole run before every job but the first. Cross-leg by construction."""
        done = len(outcomes)
        if not done:
            return None  # nothing has been billed for a call yet; there is no marginal to read
        seen = projection(
            opened_seconds=opened_seconds,
            billed=billed_seconds(client),
            done=done,
            total=calls_total,
            rate=rate,
        )
        projections.append(seen)
        print(
            f"  after {done}/{calls_total}: {seen['marginal_seconds_per_call']}s/call ·"
            f" ${seen['spent_usd']:.4f} spent → ${seen['projected_usd']:.4f} projected",
            flush=True,
        )
        if budget is not None and seen["projected_usd"] > budget:
            return (
                f"the run projects ${seen['projected_usd']:.4f} against ${budget:.4f} left of the"
                f" ${cap:.2f} cap. A cap is not raised to finish a run"
            )
        return None

    def announce(leg: str):
        def on_job(index, batch, replies):
            print(
                f"  {leg} job {index:02d}  {len(batch)} item(s)  {'ok' if replies else 'FAILED'}"
                f"  {sum(item['bytes'] for item in batch) / 1e6:.2f} MB"
            )

        return on_job

    outcomes, dumped, ended_by = [], [], None
    for leg, task, packed, carrier_of in (
        ("page", prompts.POSITIONS_TASK_PAGE, page_jobs, lambda item: "leaflet_page"),
        ("text", prompts.POSITIONS_TASK_TEXT, text_jobs, lambda item: item["carrier"]),
    ):
        before = len(outcomes)
        ended_by = run_leg(
            client,
            task,
            carrier_of,
            packed,
            categories,
            aliases,
            fields,
            args.dump_prefix,
            announce(leg),
            outcomes,
            dumped,
            gate if budget is not None else None,
        )
        for row in outcomes[before:]:
            row["leg"] = leg
        if ended_by:
            break  # SPEC 3.17 (10)(c): a job the clock killed ends the RUN, not just the leg

    # this SESSION's own accounting, taken before the merge: `unbought` is what THIS run did not
    # buy of what it set out to buy, and a merged denominator would report the first session's
    # completed pages as bought by this one
    asked_here = len(outcomes)
    asked = {row["source"] for row in outcomes}
    unbought = sorted(
        (item.get("file") or item["id"])
        for packed in (page_jobs, text_jobs)
        for job in packed
        for item in job
        if (item.get("file") or item["id"]) not in asked
    )
    merged = merge_sessions(plan, outcomes, dumped) if plan is not None else None
    if merged is not None:
        outcomes, dumped = merged["outcomes"], merged["dumped"]

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in dumped), encoding="utf-8"
    )

    unreadable = [row for row in outcomes if row["unreadable"]]
    by_reason = Counter(row["unreadable"] for row in unreadable)
    empty = [row for row in outcomes if row["n_positions"] == 0]
    balance, spent, cost_note = spend_or_note(ledger, phase)
    with_old_price = [row for row in dumped if row.get("price_old") is not None]

    record = head | {
        "stopped_before_gold": False,
        "ended_by": ended_by,
        "warmup": warmup_block,
        "population": {
            "pages_sent": registered_pages,
            "pages_available": reference["population"]["pages_available"],
            "posts": reference["population"]["posts"],
            "text_rows": registered_rows,
            "asked": len(outcomes),
            "asked_this_session": asked_here,
            "unbought": unbought,
        },
        "extraction": {
            "positions": len(dumped),
            "by_tier": dict(Counter(row["tier"] for row in dumped)),
            "empty_answers": [row["source"] for row in empty],
            "unreadable": [
                {"source": row["source"], "reason": row["unreadable"]} for row in unreadable
            ],
            "unreadable_by_reason": dict(by_reason),
            "unreadable_share": round(len(unreadable) / len(outcomes), 4) if outcomes else None,
            "reading": (
                "an unreadable reply and an empty array are DIFFERENT outcomes and are counted"
                " separately. A refusal is excluded from bar 3's denominator by its reason"
                " (results/sku_pilot_prereg_v2.json :: bars.text_tier_accuracy.unreadable_rows);"
                " an empty array is a source that names no tracked position, which is an answer"
            ),
            "truncated_replies": sorted(
                row["source"] for row in outcomes if row.get("finish_reason") == "length"
            ),
        },
        "dump": {
            "path": rel(out) if out.is_relative_to(REPO_ROOT) else str(out),
            "sha256": sha256(out.read_bytes()).hexdigest(),
            "rows": len(dumped),
            "columns": list(fields),
            "columns_source": f"{rel(args.prereg)} :: bars.price_pair_accuracy.procedure",
            "wire_key": {
                "attribute": positions.wire_key("attribute", FAMILY),
                "why": (
                    "the schema field is `attribute_pct` (SPEC 3.17 (8)) and the registered dairy"
                    " prompts ask for `fat` on the wire. The dump carries the WIRE name because"
                    " that is the name the pre-registered sentence uses"
                ),
            },
            "price_pairs": {
                "n": len(with_old_price),
                "reachability": prereg["bars"]["price_pair_accuracy"]["reachability"]["rule"],
                "note": (
                    "the denominator of bar 2, discovered BY THIS RUN. The bar is scored by the"
                    " team lead against the page images at acceptance — the executor never scores"
                    " its own sample (SPEC §10)"
                ),
            },
        },
        "outcomes": outcomes,
        "timing": client.timing(),
        "projection": {
            "rate_usd_per_second": rate,
            "rate_source": "results/srv2d_cost.json :: rate.usd_per_second",
            "stop_at_usd": budget,
            # what was billed before the first gold call, split so the report of this run can be
            # compared against results/sku_projection.json's two cold-start corners
            "boot_seconds": round(boot_seconds, 3),
            "boot_usd": round(boot_seconds * rate, 4),
            "warmup_seconds": round(opened_seconds - boot_seconds, 3),
            "opened_seconds": round(opened_seconds, 3),
            "go_no_go": verdict,
            "per_gate": projections,
            "stopped_early": bool(unbought),
            "reading": (
                "the stop prices what is LEFT against what is already billed — it never re-adds a"
                " pre-registered cold start on top of measured seconds, because by the time any"
                " gate runs the boot has been paid and is inside `billed_seconds`. `calls_done`"
                " counts across BOTH legs, and the idle tail the worker bills after the last job"
                " is inside `projected_usd` and outside `spent_usd`"
            ),
        },
        "cost": {
            "jobs_planned": len(page_jobs) + len(text_jobs),
            "jobs_submitted": (client.timing() or {}).get("calls"),
            "jobs_reading": (
                "`jobs_planned` is what the packing set out to send and it does NOT shrink when a"
                " stop fires: the run stopped at 17 of 138 recorded 8 planned against 4 submitted,"
                " and read as a job count it said the session ran twice the work it did."
                " `jobs_submitted` is `timing().calls` — the client's own counter of terminal /run"
                " submissions, which on the real endpoint client includes the `info` handshake and"
                " always includes the two warm-up calls. There is no health read on this client, so"
                " this is the nearest honest number and it is named rather than passed off as a"
                " count of gold jobs"
            ),
            "usd": None if spent is None else round(spent, 4),
            "cap_usd": cap,
            "anchor": rel(args.ledger),
            "read_failed": cost_note,
            "reading": (
                "the RunPod balance delta against this session's own anchor. It is a FLOOR — the"
                " balance settles minutes to hours behind the resource (Dv33) — and runpod_guard's"
                " itemised corroboration is the phase-level check, not this one. A `usd` of null"
                " beside a `read_failed` means the balance could not be read AFTER the paid legs:"
                " the anchor survives, so the spend is recoverable by hand, and the record is kept"
                " rather than lost to the crash."
            ),
        },
        "git": provenance.git_state(record_path),
    }
    if merged is not None:
        record["resume"] = {
            "authority": "docs/SPEC.md amendment 3.17 (11), registered in " + rel(args.prereg),
            "reading": (
                "this record is the MERGED bar input: `outcomes` and the dump carry both paid"
                " sessions' answers, every row naming the session that bought it in"
                f" `{BOUGHT_BY}`. The bars are registered over the whole population and after a"
                " resume that population lives in two records — scoring from either alone would"
                " report a fraction of a bar as the bar"
            ),
            "sessions": [
                merged["previous"],
                {
                    "phase": RESUME_PHASE,
                    "record": rel(record_path)
                    if record_path.is_relative_to(REPO_ROOT)
                    else str(record_path),
                    "dump": record["dump"]["path"],
                    "dump_sha256": record["dump"]["sha256"],
                    "prereg": record["prereg"],
                    "asked": asked_here,
                    "note": (
                        "no sha for this record: a file cannot carry its own hash. The dump's is"
                        " here because the dump is written before this record is assembled"
                    ),
                },
            ],
            "bought_exactly_once": (
                "checked on the merged outcomes, not on the plan: no source appears twice. The"
                " plan's refusals guard what goes on the wire; this guards what gets scored"
            ),
        }
    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if ledger is not None:
        ledger["runs"].append(
            {
                "at": datetime.now(UTC).isoformat(timespec="seconds"),
                "balance": balance,
                "step_spent_usd": None if spent is None else round(spent, 4),
                "note": f"{len(outcomes)} sources asked, {len(dumped)} positions extracted"
                + ("" if cost_note is None else f" — {cost_note}"),
            }
        )
        args.ledger.write_text(
            json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    # per-source lines, not only aggregates: a runbook step can `test -s` this and a reader can see
    # which page or row produced what without opening the dump
    for row in outcomes:
        state = (
            f"UNREADABLE {row['unreadable']}"
            if row["unreadable"]
            else f"{row['n_positions']} position(s)"
        )
        print(f"  {row['leg']:<4} {row['source']:<62} {state}")
    print(
        f"\n{len(dumped)} positions from {len(outcomes)} sources"
        f" · {len(unreadable)} unreadable · {len(empty)} empty"
        f" · {len(with_old_price)} carry a crossed-out price"
        f" · {'$%.4f' % spent if spent is not None else 'no spend'} of ${cap:.2f}"
        f"\nwrote {record['dump']['path']} and {rel(record_path)}"
    )
    if ended_by:
        print(f"STOP AND REPORT: the run ended early — {ended_by}")
    if cost_note:
        print(f"STOP AND REPORT: {cost_note}. The record is written; read the anchor by hand.")
    if unreadable and not args.smoke:
        print("STOP AND REPORT: a reply was refused by the parser. No retry is made.")
    if spent is not None and spent >= cap:
        print("STOP AND REPORT: the cap is reached. An overrun aborts, it does not raise a cap.")
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
