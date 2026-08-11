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
JOB_TIMEOUT_S = 1800.0
JOB_TTL_S = 3600.0
"""Seconds. `serving.execution_policy` is the one place they become milliseconds."""

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

    def __init__(self, worker: dict, categories) -> None:
        self.worker = worker
        self.jobs = 0
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
        return {"calls": self.jobs, "rows": 0, "wall_seconds": 0.0, "smoke": True}


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
    stop=None,
) -> tuple[list[dict], list[dict]]:
    """One job per pack, in order. Returns (per-source outcomes, dump rows).

    A job that fails is named against every source in it and never re-asked; ``stop`` is the
    re-projection gate and the sources it skips are left out of the outcomes rather than marked
    failed — nothing was asked for them.
    """
    outcomes, dumped = [], []
    for index, batch in enumerate(packed):
        if stop is not None and index and (reason := stop(len(outcomes))):
            print(f"  STOP before job {index:02d}: {reason}", flush=True)
            break
        if dump_prefix is not None:
            client.dump_path = f"{dump_prefix}_{task}_{index:02d}.jsonl"
        # a page travels as a ONE-image album (SPEC 3.17 (4)); a row travels as its text
        payload = [[item["url"]] if "url" in item else item["text"] for item in batch]
        try:
            replies = client.positions(task, payload)
        except (ApiError, ValueError, OSError) as err:
            outcomes += [
                {
                    "source": item.get("file") or item["id"],
                    "item": item.get("item") or item.get("id"),
                    "n_positions": None,
                    "unreadable": f"job {index}: {err}",
                }
                for item in batch
            ]
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
    return outcomes, dumped


def warmup(client, task_page: str, task_text: str) -> dict:
    """SPEC 3.17 (9): a paid call on NON-gold inputs before either leg touches gold.

    A synthetic image and a row that is not in the 30-row pack. What it buys is the cold start and
    the proof that the instrument answers at all, on inputs no bar is scored on — so a worker that
    comes back unparseable costs the warm-up rather than a leg of the gold.
    """
    import base64
    import io

    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (64, 64), (240, 240, 240)).save(buffer, format="JPEG")
    synthetic = "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")
    out = {}
    for task, item in ((task_page, [synthetic]), (task_text, WARMUP_ROW)):
        reply = client.positions(task, [item])[0]
        out[task] = {
            "content": (reply.get("content") or "")[:200],
            "finish_reason": reply.get("finish_reason"),
        }
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
    if args.smoke and (args.out, args.record) == (None, None):
        # A smoke on the real paths fills the paid artifacts with fake extractions and then makes
        # the real run refuse to overwrite them. The 4.5g2 redirect, for the same reason.
        smoke = REPO_ROOT / "results" / "smoke"
        out, record_path = smoke / out.name, smoke / record_path.name
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
    ledger = None
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
        balance, spent = spend_now(ledger)
        print(f"ledger: spent ${spent:.4f} of ${CAP_USD:.2f} (balance ${balance:.2f})")
        if spent >= CAP_USD:
            raise SystemExit(
                f"REFUSED: the ${CAP_USD:.2f} cap is reached (${spent:.4f} spent). Stop and"
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
    boot_seconds = float(client.timing().get("worker_seconds") or 0.0)
    rate = leader.rate_usd_per_second()

    opened = warmup(client, prompts.POSITIONS_TASK_PAGE, prompts.POSITIONS_TASK_TEXT)
    for task, reply in opened.items():
        print(f"  warm-up {task:<20} {reply['finish_reason']}  {reply['content'][:60]}")

    rows_total = len(page_items) + len(text_items)
    budget = args.project_stop_usd
    if budget is None and ledger is not None:
        budget = round(CAP_USD - spent, 4)
    projections: list[dict] = []

    def gate(done: int) -> str | None:
        seen = leader.projection(
            boot_seconds, float(client.timing()["worker_seconds"]), done, rows_total, rate
        )
        projections.append(seen)
        print(
            f"  after {done}/{rows_total}: ${seen['marginal_usd_per_row']:.6f}/call →"
            f" ${seen['projected_usd']:.4f} projected",
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

    outcomes, dumped = [], []
    for leg, task, packed, carrier_of in (
        ("page", prompts.POSITIONS_TASK_PAGE, page_jobs, lambda item: "leaflet_page"),
        ("text", prompts.POSITIONS_TASK_TEXT, text_jobs, lambda item: item["carrier"]),
    ):
        got, wrote = run_leg(
            client,
            task,
            carrier_of,
            packed,
            categories,
            aliases,
            fields,
            args.dump_prefix,
            announce(leg),
            gate if budget is not None else None,
        )
        for row in got:
            row["leg"] = leg
        outcomes += got
        dumped += wrote

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
    balance, spent = (None, None) if ledger is None else spend_now(ledger)
    with_old_price = [row for row in dumped if row.get("price_old") is not None]

    record = {
        "timestamp": started,
        "phase": "sku-b — the position-layer pilot, one paid attempt",
        "contract": "docs/PROMPT-sku-b-prep.md deliverable 2; docs/SPEC.md amendment 3.17 (6), (9)",
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
        "warmup": {
            "why": "SPEC 3.17 (9): a call on NON-gold inputs before either leg touches gold",
            "inputs": {"page": "a generated 64x64 image", "text": WARMUP_ROW},
            "replies": opened,
        },
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
            "per_gate": projections,
            "stopped_early": bool(unbought),
        },
        "cost": {
            "jobs": len(page_jobs) + len(text_jobs),
            "usd": None if spent is None else round(spent, 4),
            "cap_usd": CAP_USD,
            "anchor": rel(args.ledger),
            "reading": (
                "the RunPod balance delta against this session's own anchor. It is a FLOOR — the"
                " balance settles minutes to hours behind the resource (Dv33) — and runpod_guard's"
                " itemised corroboration is the phase-level check, not this one."
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
                "step_spent_usd": round(spent, 4),
                "note": f"{len(outcomes)} sources asked, {len(dumped)} positions extracted",
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
    if unreadable and not args.smoke:
        print("STOP AND REPORT: a reply was refused by the parser. No retry is made.")
    if spent is not None and spent >= CAP_USD:
        print("STOP AND REPORT: the cap is reached. An overrun aborts, it does not raise a cap.")
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
