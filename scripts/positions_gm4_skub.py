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

    PYTHONPATH=src python3 scripts/positions_gm4_skub.py --dry-run
    PYTHONPATH=src python3 scripts/positions_gm4_skub.py --smoke
    PYTHONPATH=src python3 scripts/positions_gm4_skub.py --endpoint-id <id>
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

REFERENCE = REPO_ROOT / "results" / "sku_reference_leaflet.json"
MANIFEST = REPO_ROOT / "results" / "sku_text_pack_manifest.json"
PREREG = REPO_ROOT / "results" / "sku_pilot_prereg_v2.json"
PIN = REPO_ROOT / "results" / "sku_pilot_serving.json"
REGISTRY = REPO_ROOT / "config" / "registry.yaml"

DUMP = REPO_ROOT / "results" / "sku_b_positions.jsonl"
RECORD = REPO_ROOT / "results" / "sku_b_positions.json"

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


def anchor_key() -> str:
    return f"runpod_balance_at_{PHASE}_start"


def read_ledger(path: Path, balance_now: float) -> dict:
    """This session's anchor, created before the first job or refused if it is another's."""
    if path.exists():
        ledger = json.loads(path.read_text(encoding="utf-8"))
        if anchor_key() not in ledger:
            raise SystemExit(
                f"{path.name} carries no {anchor_key()} — it is another phase's anchor. Spending"
                " against it would enforce this cap on the wrong balance."
            )
        return ledger
    return {
        anchor_key(): balance_now,
        "cap_usd": CAP_USD,
        "note": (
            "RunPod account balance read before the first job of sku-b, the single paid session of"
            f" SPEC 3.17 (6). Session spend = this anchor minus the balance now, enforced against"
            f" the ${CAP_USD:.2f} cap the amendment pre-registered. The Phase 4 cap is enforced"
            " separately against results/spend_phase4.json, and neither anchor may be regenerated:"
            " delete this file and the counter silently restarts at today's balance."
        ),
        "runs": [],
    }


def spend_now(ledger: dict) -> tuple[float, float]:
    """(balance, spend). The delta is a FLOOR — RunPod settles it minutes to hours late (Dv33)."""
    balance = guard.balance()
    return balance, float(ledger[anchor_key()]) - balance


def spend_or_note(ledger: dict | None) -> tuple[float | None, float | None, str | None]:
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
        balance, spent = spend_now(ledger)
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


def warmup(client, task_page: str, task_text: str, clock=None) -> dict:
    """SPEC 3.17 (9): a paid call on NON-gold inputs before either leg touches gold.

    A synthetic image and a row that is not in the 30-row pack. What it buys is the cold start and
    the proof that the instrument answers at all, on inputs no bar is scored on — so a worker that
    comes back unparseable costs the warm-up rather than a leg of the gold.

    It also buys the only per-leg price that exists before gold, which is why the clock is read
    BETWEEN the two calls rather than once at the end: :func:`go_no_go` prices 108 pages and 30
    rows separately, and a single blended figure would charge the image leg's seconds to the text
    leg's 30 calls. ``clock`` is :func:`billed_seconds` and is injected so a caller can prove the
    arithmetic without a worker.
    """
    import base64
    import io

    from PIL import Image

    clock = billed_seconds if clock is None else clock
    buffer = io.BytesIO()
    Image.new("RGB", (64, 64), (240, 240, 240)).save(buffer, format="JPEG")
    synthetic = "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")
    out, before = {}, clock(client)
    for task, item in ((task_page, [synthetic]), (task_text, WARMUP_ROW)):
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
    parser.add_argument("--prereg", type=Path, default=PREREG)
    parser.add_argument("--pin", type=Path, default=PIN)
    parser.add_argument("--ledger", type=Path, default=LEDGER)
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

    out = args.out or DUMP
    record_path = args.record or RECORD
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
    for path in (out, record_path):
        if path.exists():
            raise SystemExit(
                f"{path} already exists — it is what a paid run bought. Re-running would spend"
                " again and overwrite the only copy: give --out/--record another path."
            )

    reference = json.loads(args.reference.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    prereg = json.loads(args.prereg.read_text(encoding="utf-8"))
    pin = json.loads(args.pin.read_text(encoding="utf-8"))
    fields = dump_fields(prereg)

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
    if args.dry_run:
        for item in page_items[:3]:
            print(f"  page {item['item']} p{item['page']} {item['bytes'] / 1e6:.2f} MB")
        for row in text_items[:3]:
            print(f"  row  {row['id']} {row['carrier']} {row['text'][:60]}…")
        return 0

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
        ledger = read_ledger(args.ledger, balance)
        args.ledger.parent.mkdir(parents=True, exist_ok=True)
        args.ledger.write_text(
            json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )  # anchored before the first job, never after
        balance, spent_before = spend_now(ledger)
        print(f"ledger: spent ${spent_before:.4f} of ${CAP_USD:.2f} (balance ${balance:.2f})")
        if spent_before >= CAP_USD:
            raise SystemExit(
                f"REFUSED: the ${CAP_USD:.2f} cap is reached (${spent_before:.4f} spent). Stop and"
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
        left = round(CAP_USD - spent_before, 4)
        budget = left if budget is None else min(budget, left)
    projections: list[dict] = []

    # everything both records carry, built once so the go/no-go stop below cannot drift from the
    # record a completed run writes
    head = {
        "timestamp": started,
        "phase": "sku-b — the position-layer pilot, one paid attempt",
        "contract": (
            "docs/PROMPT-sku-b-prep.md deliverable 2 + docs/PROMPT-sku-b-prep-fix.md;"
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

    opened = warmup(client, prompts.POSITIONS_TASK_PAGE, prompts.POSITIONS_TASK_TEXT)
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
        "inputs": {"page": "a generated 64x64 image", "text": WARMUP_ROW},
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
        balance, spent, cost_note = spend_or_note(ledger)
        record_path.parent.mkdir(parents=True, exist_ok=True)
        record_path.write_text(
            json.dumps(
                head
                | {
                    "stopped_before_gold": True,
                    "why": (
                        "SPEC 3.17 (10)(a): after the two non-gold warm-up calls the whole run"
                        f" projects ${verdict['projected_usd']:.4f} against ${budget:.4f} left of"
                        f" the ${CAP_USD:.2f} cap. Refused BEFORE the first gold call, which is the"
                        " only stop that leaves nothing half-bought — and under (10)(a) it consumes"
                        " NO attempt. The pilot returns to the team lead for a v3 registration"
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
                        "cap_usd": CAP_USD,
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
            f" ${verdict['projected_usd']:.4f} against ${budget:.4f} left of the ${CAP_USD:.2f}"
            f" cap (SPEC 3.17 (10)(a)). No gold call was made and NO attempt was consumed —"
            f" {rel(record_path)} is the record. Stop and report; the pilot needs a v3"
            " registration under the measured price, not a raised cap."
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
                f" ${CAP_USD:.2f} cap. A cap is not raised to finish a run"
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

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in dumped), encoding="utf-8"
    )

    unreadable = [row for row in outcomes if row["unreadable"]]
    by_reason = Counter(row["unreadable"] for row in unreadable)
    empty = [row for row in outcomes if row["n_positions"] == 0]
    asked = {row["source"] for row in outcomes}
    unbought = sorted(
        (item.get("file") or item["id"])
        for packed in (page_jobs, text_jobs)
        for job in packed
        for item in job
        if (item.get("file") or item["id"]) not in asked
    )
    balance, spent, cost_note = spend_or_note(ledger)
    with_old_price = [row for row in dumped if row.get("price_old") is not None]

    record = head | {
        "stopped_before_gold": False,
        "ended_by": ended_by,
        "warmup": warmup_block,
        "population": {
            "pages_sent": len(page_items),
            "pages_available": reference["population"]["pages_available"],
            "posts": reference["population"]["posts"],
            "text_rows": len(text_items),
            "asked": len(outcomes),
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
            "jobs": len(page_jobs) + len(text_jobs),
            "usd": None if spent is None else round(spent, 4),
            "cap_usd": CAP_USD,
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
        f" · {'$%.4f' % spent if spent is not None else 'no spend'} of ${CAP_USD:.2f}"
        f"\nwrote {record['dump']['path']} and {rel(record_path)}"
    )
    if ended_by:
        print(f"STOP AND REPORT: the run ended early — {ended_by}")
    if cost_note:
        print(f"STOP AND REPORT: {cost_note}. The record is written; read the anchor by hand.")
    if unreadable and not args.smoke:
        print("STOP AND REPORT: a reply was refused by the parser. No retry is made.")
    if spent is not None and spent >= CAP_USD:
        print("STOP AND REPORT: the cap is reached. An overrun aborts, it does not raise a cap.")
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
