#!/usr/bin/env python3
"""Write `results/sku_projection.json` — what sku-b will cost, from what past runs measured ($0).

Deliverable 6 of `docs/PROMPT-sku-b-prep.md`. A projection is ARITHMETIC OVER NAMED ARTIFACTS: no
new measurement, no paid call, and every input below is read out of a file whose path and sha are
recorded beside the number. Nothing here is typed from memory.

Three things it refuses to do, and each is a way a projection lies:

* **it never multiplies an all-in per-post figure by a count.** `results/captions_gm4_atb19.json`
  says the vis-b session cost $0.3869 — that is a BALANCE DELTA for the whole session, boot and
  staging inside it, and $0.3869 / 19 posts is a number about the account and not about a post.
  What transfers is the MARGINAL second, with the cold start subtracted once and added back once.
* **it never hides the cold start inside the marginal.** vis-b's own re-pilot did exactly that and
  its per-post rate came out 2x too high (the ADR retraction quoted in
  `caption_gm4_5c1.projection`). The boot is subtracted before the rate is taken, and it is carried
  as a RANGE — $0.0563 measured on a real endpoint, $0.0733 pre-registered — because which one the
  paid session pays is not knowable in advance.
* **it never quotes one number.** The decode-length uplift is an ASSUMPTION, stated as a constant
  with its justification, and the total is reported at the assumption and without it. A projection
  whose sensitivity is invisible reads as a measurement.

    PYTHONPATH=src python3 scripts/write_sku_projection.py
"""

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import positions_gm4_skub as driver  # noqa: E402

from market_pulse import local_llm, provenance  # noqa: E402

RATE = REPO_ROOT / "results" / "srv2d_cost.json"
PAGE_SOURCE = REPO_ROOT / "results" / "captions_gm4_atb19.json"
PAGE_CORROBORATION = REPO_ROOT / "results" / "captions_gm4_visc.json"
REFERENCE = REPO_ROOT / "results" / "sku_reference_leaflet.json"
MANIFEST = REPO_ROOT / "results" / "sku_text_pack_manifest.json"
RECORD = REPO_ROOT / "results" / "sku_projection.json"

COLD_START_USD_PREREGISTERED = 0.0733
"""SPEC 3.15 (3) / runbook §C.1: 239.022 s at the settled rate, registered before vis-b ran."""

COLD_START_USD_MEASURED = 0.0563
"""What an endpoint actually booted in, read off `results/captions_gm4_visc.json ::
projection.per_slice[].cold_start_usd_measured_here` (183.58 s). Carried BESIDE the pre-registered
figure and never substituted into it — a pre-registration is a file, not a preference."""

CAPTION_CEILING = local_llm.CAPTION_MAX_NEW_TOKENS
POSITIONS_CEILING = local_llm.POSITIONS_MAX_NEW_TOKENS
SRV2D_CEILING = local_llm.MAX_NEW_TOKENS

UPLIFT_NOTE = (
    "ASSUMPTION, not a measurement. A positions reply is a JSON array and a caption is one"
    " sentence, so the positions leg decodes more tokens per call — but no artifact prices a"
    " positions reply, because none has ever been generated. The uplift used is the RATIO OF THE"
    " REGISTERED CEILINGS of the source instrument and this one (800/400 for the page leg against"
    " vis-b's captions, 800/256 for the text leg against srv-2d's rows). A ceiling bounds the"
    " longest honest answer, so this is an UPPER bound on the decode and the projection at"
    " uplift 1.0 is reported beside it as the lower one. Two biases, in opposite directions and"
    " both stated: applying the uplift to the WHOLE marginal over-counts, because the image"
    " prefill does not grow with the reply; and taking a per-image rate from a 5.7-image-per-call"
    " run under-counts the per-call overhead of a 1-image-per-call one."
)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def load(path: Path) -> tuple[dict, str]:
    return (
        json.loads(path.read_text(encoding="utf-8")),
        hashlib.sha256(path.read_bytes()).hexdigest(),
    )


def per_image_seconds(record: dict, boot_seconds: float) -> dict:
    """The marginal second per IMAGE, boot subtracted once.

    Per image and not per post: vis-b made one call per POST carrying up to six pages, and sku-b
    makes one call per PAGE (SPEC 3.17 (4)). A per-post figure multiplied by 108 would be pricing
    108 albums.
    """
    worker = float(record["timing"]["worker_seconds"])
    images = int(record["images"]["sent"])
    marginal = (worker - boot_seconds) / images
    return {
        "worker_seconds": worker,
        "boot_seconds": round(boot_seconds, 3),
        "images": images,
        "posts": record["timing"]["rows"],
        "images_per_call": round(images / record["timing"]["rows"], 2),
        "marginal_seconds_per_image": round(marginal, 4),
    }


def build(out: Path) -> dict:
    rate_record, rate_sha = load(RATE)
    page_record, page_sha = load(PAGE_SOURCE)
    other_record, other_sha = load(PAGE_CORROBORATION)
    reference, reference_sha = load(REFERENCE)
    manifest, manifest_sha = load(MANIFEST)

    rate = float(rate_record["rate"]["usd_per_second"])
    text_row_seconds = float(rate_record["measured"]["like_for_like_seconds_per_row"])
    boot_preregistered = COLD_START_USD_PREREGISTERED / rate
    boot_measured = float(other_record["projection"]["per_slice"][0]["boot_seconds"])

    page_rate = per_image_seconds(page_record, boot_preregistered)
    other_rate = per_image_seconds(other_record, boot_measured)

    n_pages = int(reference["population"]["pages_sent"])
    n_rows = int(manifest["rows"])
    page_uplift = POSITIONS_CEILING / CAPTION_CEILING
    text_uplift = POSITIONS_CEILING / SRV2D_CEILING
    per_page = page_rate["marginal_seconds_per_image"]

    def corner(uplift: bool, cold_usd: float) -> dict:
        up_page = page_uplift if uplift else 1.0
        up_text = text_uplift if uplift else 1.0
        page_usd = n_pages * per_page * up_page * rate
        text_usd = n_rows * text_row_seconds * up_text * rate
        # SPEC 3.17 (9) opens the session on NON-gold inputs: one image and one row
        warm_usd = (per_page * up_page + text_row_seconds * up_text) * rate
        total = page_usd + text_usd + warm_usd + cold_usd
        return {
            "decode_uplift": {"page": round(up_page, 4), "text": round(up_text, 4)},
            "cold_start_usd": cold_usd,
            "page_leg_usd": round(page_usd, 4),
            "text_leg_usd": round(text_usd, 4),
            "warmup_usd": round(warm_usd, 4),
            "total_usd": round(total, 4),
            "cap_usd": driver.CAP_USD,
            "headroom_usd": round(driver.CAP_USD - total, 4),
            "headroom_share_of_cap": round((driver.CAP_USD - total) / driver.CAP_USD, 4),
            "fits": total <= driver.CAP_USD,
        }

    corners = {
        "lower — no decode uplift, cold start as measured": corner(False, COLD_START_USD_MEASURED),
        "lower — no decode uplift, cold start pre-registered": corner(
            False, COLD_START_USD_PREREGISTERED
        ),
        "stated — ceiling-ratio uplift, cold start as measured": corner(
            True, COLD_START_USD_MEASURED
        ),
        "stated — ceiling-ratio uplift, cold start pre-registered": corner(
            True, COLD_START_USD_PREREGISTERED
        ),
    }
    worst = max(corners.values(), key=lambda cell: cell["total_usd"])
    best = min(corners.values(), key=lambda cell: cell["total_usd"])

    return {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "phase": "sku-b — the paid attempt, priced before it is authorised",
        "written_by": "sku-b-prep (executor, $0), docs/PROMPT-sku-b-prep.md deliverable 6",
        "class": (
            "PROJECTION. Arithmetic over named artifacts — no new measurement was taken and no"
            " paid call was made to produce it. Every input names the file it came from"
        ),
        "rate": {
            "usd_per_second": rate,
            "source": f"{rel(RATE)} :: rate.usd_per_second",
            "sha256": rate_sha,
            "corroboration": rate_record["rate"]["corroboration"],
        },
        "page_leg": {
            "calls": n_pages,
            "unit": "one PAGE, one call (SPEC 3.17 (4))",
            "source": {
                "path": rel(PAGE_SOURCE),
                "sha256": page_sha,
                "why": (
                    "the freshest record that PAID for ATB leaflet captions, and it captioned"
                    " EXACTLY the 108 images sku-b's page leg sends — the same files, the same"
                    " encoding, the same base at the same revision"
                ),
                **page_rate,
            },
            "corroboration": {
                "path": rel(PAGE_CORROBORATION),
                "sha256": other_sha,
                "why": (
                    "an independent session on the same base with a different album size. Its"
                    " per-image marginal agrees with vis-b's to under half a percent, which is"
                    " what makes a two-point rate a rate rather than one run's weather"
                ),
                **other_rate,
            },
            "never_used": {
                "session_usd": page_record["cost"]["usd"],
                "why": (
                    "a BALANCE DELTA for the whole vis-b session — staging, boot and every job"
                    " inside it. Divided by 19 posts it reads $0.0204 per post, and multiplying"
                    " that by a page count would price 108 albums plus 108 cold starts"
                ),
            },
        },
        "text_leg": {
            "calls": n_rows,
            "unit": "one ROW, one call, no image",
            "source": {
                "path": rel(RATE),
                "field": "measured.like_for_like_seconds_per_row",
                "seconds_per_row": text_row_seconds,
                "why": (
                    "srv-2d's 758-row parity pass: the same base on the same serverless runtime,"
                    " text in and JSON out, with no image on the wire. It is the only artifact"
                    " that prices an image-free call on this stack"
                ),
            },
        },
        "assumptions": {
            "decode_uplift": UPLIFT_NOTE,
            "ceilings": {
                "captions (vis-b)": CAPTION_CEILING,
                "srv-2d rows": SRV2D_CEILING,
                "positions (SPEC 3.17 (9))": POSITIONS_CEILING,
            },
            "cold_start": {
                "measured_usd": COLD_START_USD_MEASURED,
                "measured_seconds": boot_measured,
                "measured_source": (
                    f"{rel(PAGE_CORROBORATION)} ::"
                    " projection.per_slice[0].cold_start_usd_measured_here"
                ),
                "preregistered_usd": COLD_START_USD_PREREGISTERED,
                "preregistered_seconds": round(boot_preregistered, 3),
                "preregistered_source": "SPEC 3.15 (3) / runbook §C.1, via caption_gm4_5c1",
                "why_a_range": (
                    "which boot the paid session pays is not knowable in advance — it depends on"
                    " whether the endpoint's weights are warm. Both are carried and neither is"
                    " substituted into the other"
                ),
            },
            "one_attempt": (
                "no retry is priced, because none is permitted: SPEC 3.17 (6) gives the pilot one"
                " attempt and a failed bar closes B by measurement"
            ),
        },
        "corners": corners,
        # NOT called `verdict`: tests/test_sku_prereg.py refuses a `verdict` key anywhere in
        # results/sku_*.json, because a pre-registration that scores itself is not one. This block
        # is a reading against the CAP and not against a bar, and the guard is right to be narrow —
        # the fix is the field's name, never the gate.
        "against_the_cap": {
            "cap_usd": driver.CAP_USD,
            "lowest_usd": best["total_usd"],
            "highest_usd": worst["total_usd"],
            "fits_at_every_corner": all(cell["fits"] for cell in corners.values()),
            "reading": (
                f"the pilot fits the ${driver.CAP_USD:.2f} cap comfortably at the lower corner"
                f" (${best['total_usd']:.4f}, {best['headroom_share_of_cap']:.0%} headroom) and"
                f" sits ON the cap at the stated upper one (${worst['total_usd']:.4f}). The"
                " decode uplift is the whole spread: it is an assumption about a reply nothing"
                " has generated yet, and the warm-up call of SPEC 3.17 (9) is the first thing"
                " that will price it for real"
            ),
            "what_an_early_stop_costs": (
                "the driver re-projects before every job and stops when the run would pass what"
                " is left of the cap, so an overrun is impossible — but a page leg that stops"
                " early is NOT a cheaper pilot. Bar 1's registered page set is EXACTLY the 108"
                " sent pages (results/sku_pilot_prereg_v2.json :: R2), and a post whose pages were"
                " partly bought has a gold set written against all of them. Fewer pages moves the"
                " numerator and not the denominator, which reads as a model that missed brands."
                " If the stop fires, the finding is about the cap and not about the instrument"
            ),
        },
        "pinned_inputs": {
            rel(RATE): rate_sha,
            rel(PAGE_SOURCE): page_sha,
            rel(PAGE_CORROBORATION): other_sha,
            rel(REFERENCE): reference_sha,
            rel(MANIFEST): manifest_sha,
        },
        "git": provenance.git_state(out),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=RECORD)
    args = parser.parse_args(argv)

    record = build(args.out)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"wrote {rel(args.out)}")
    page = record["page_leg"]["source"]
    other = record["page_leg"]["corroboration"]
    print(
        f"  page rate     {page['marginal_seconds_per_image']} s/image"
        f" ({rel(PAGE_SOURCE)}, boot {page['boot_seconds']}s subtracted)"
        f"\n  corroborated  {other['marginal_seconds_per_image']} s/image ({rel(PAGE_CORROBORATION)})"
        f"\n  text rate     {record['text_leg']['source']['seconds_per_row']} s/row"
        f" ({rel(RATE)} :: measured.like_for_like_seconds_per_row)"
    )
    for name, cell in record["corners"].items():
        print(
            f"  {name:<58} ${cell['total_usd']:.4f}"
            f"  headroom ${cell['headroom_usd']:+.4f}"
            f"  {'fits' if cell['fits'] else 'OVER THE CAP'}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
