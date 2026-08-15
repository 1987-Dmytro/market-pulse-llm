#!/usr/bin/env python3
"""The pre-registration of 5c2-run: the three populations, their prices, the cap and the stop rules.

SPEC amendment 3.18 (5) — "5c2-run: one paid session under that cap" — and (7)(f): the registration
"exact-pins the chosen numbers by VALUE", because "the prep-c2 review's finding that the caps table
is pinned by inequalities binds here: the registered cap row gets equality tests, not ceilings".
Every number below is therefore an equality in `tests/test_prereg_5c2.py`, and the ceiling
(`cap <= remaining`) is an ADDITIONAL assertion beside them rather than the pin itself.

**Nothing here is measured.** The three populations are read out of three shipped records and the
three prices out of the paid measurements `results/projection_5c2.json` cites. What this producer
does is name them together, add them up, and refuse to write if the numbers moved under it:

* `make check` red — the registration would be made over a repo that does not pass its own verifier;
* any pinned input's sha256 disagreeing with what it says — a registration whose inputs moved is a
  claim about a repo that no longer exists (the B′ refusal precedent, `write_sku_prereg_b2`);
* the strip family not being exactly the ten marked blocks this law carries today.

**Two supersessions in one paragraph, because a reader will hit them together.**
`results/projection_5c2.json` ends at $7.6870 with `fits: false`, and this registration's LARGER
$7.8546 fits. Both are true and neither is a correction: the leaflet leg's population moved 78 →
159 (3.18 (7)(d) — the corpus on disk, not the window intersection), and the phase cap moved 30 →
33 (3.18 (7)(b)). The c2 record is a true statement of its write moment and is never regenerated.

    PYTHONPATH=src python3 scripts/write_prereg_5c2.py
"""

import argparse
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import census_c3a_posts as c3a  # noqa: E402
import positions_gm4_skub as driver  # noqa: E402
import projection_5c2 as projection  # noqa: E402
import runpod_guard as guard  # noqa: E402
import write_sku_prereg as prereg  # noqa: E402

from market_pulse import evidence  # noqa: E402

SPEC = REPO_ROOT / "docs" / "SPEC.md"
CENSUS_5C2 = REPO_ROOT / "results" / "census_5c2.json"
CENSUS_C3A = REPO_ROOT / "results" / "census_c3a_posts.json"
POSTCUT = REPO_ROOT / "results" / "postcut_c3b.json"
PROJECTION = REPO_ROOT / "results" / "projection_5c2.json"
RATE = REPO_ROOT / "results" / "srv2d_cost.json"
LEDGER = REPO_ROOT / "results" / "spend_phase4.json"
REGISTRY = REPO_ROOT / "config" / "registry.yaml"
LEXICON = REPO_ROOT / "config" / "lexicon.yaml"
POSITIONS = REPO_ROOT / "src" / "market_pulse" / "positions.py"
RECORD = REPO_ROOT / "results" / "prereg_5c2_run.json"

CHECK = ("make", "check")
"""The verifier, as the Makefile spells it. `tests/test_prereg_5c2.py` greps this back out of the
Makefile: a producer whose refusal is only ever exercised through an injected runner has tested the
injection and not the command."""

KEEP_BLOCKS = (
    "amendment-index",
    "sku-b-ratification",
    "sku-b-ratification-2",
    "sku-b-ratification-3",
    "sku-b-ratification-4",
    "sku-b-ratification-5",
    "sku-b-ratification-6",
    "sku-b-ratification-7",
    "sku-b-ratification-8",
    "amendment-3.18",
)
"""Every marked block `docs/SPEC.md` carries today — so the registered law IS the file as it stands.

B′ keeps two (the blocks that authorise it) because it was registered under a law whose other blocks
postdate the records it sits beside. This registration is written the same day as the amendment it
is made under, so there is no block in the file it does not register: 3.18 (7)(c) sends the run's
stop rules to 3.17 (10), which lives inside `sku-b-ratification-4`, and a pin that stripped it would
register a document that does not carry the discipline this record names.

What the strip still buys is the future: a block added LATER is taken off and this pin survives,
which is the only legal way to green a law that grew. That is also the constraint it puts on the
team lead — new text arrives inside its own marked block, and `tests/test_sku_prereg.py`'s literal
enumeration of these ten is what refuses to let it arrive quietly. A sealed registration is never
re-pinned to make it green.
"""

BLOCKS_TODAY = (*KEEP_BLOCKS, "amendment-3.19", "amendment-3.20")
"""Every marked block the file carries NOW: the ten the seal keeps, plus each one that arrived after.

Two questions were one constant until 3.19 landed, and they are not the same question. What the
REGISTERED LAW is was settled the day `results/prereg_5c2_run.json` was written and cannot move —
:data:`KEEP_BLOCKS`, ten names, and `pinned_sha256` still derives the sealed pin through them. What
`docs/SPEC.md` carries TODAY is a fact about the file, and it grows. Merging the two would have made
greening this producer re-pin a sealed record, which is exactly what it exists to refuse.

3.19 (operator, 2026-08-14, the 5c2-validate sitting): text-less comments are skipped before payment
from the next paid cycle on. It moves no number of the 5 075 rows this registration bought — (3)
says so out loud — so the strip takes it off and the pin survives. A twelfth block appends HERE and
nowhere else, and `check_the_strip_family_is_what_it_says` is what refuses until it does.

3.20 (operator, 2026-08-15, the Phase-6 command-centre plan) is that twelfth block, and it arrived
the way the sentence above predicted: the contract that landed it named three moving parts and this
constant was the fourth. It moves no number either — it rules on where the DASHBOARD's figures come
from — so the ten-name keep is untouched and the sealed pin still derives through it."""

DRIFT = projection.DRIFT
HALF_DOLLAR = 0.50


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def refuse(reason: str) -> None:
    raise SystemExit(f"refused: {reason}")


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def pinned_sha256(path: Path) -> str:
    """What this registration pins: for SPEC the law with every block it carries today, else the
    file as it sits."""
    if path == SPEC:
        return hashlib.sha256(prereg.registered_law(path, keep=KEEP_BLOCKS)).hexdigest()
    return sha256_of(path)


def check_the_strip_family_is_what_it_says(spec: Path) -> None:
    """The blocks in the file are exactly the ones this producer knows, or the strip is blind.

    Refusing here rather than silently stripping an unknown block is the whole point: a block that
    arrived since would otherwise be cut out of the registered law without anything saying so. The
    comparison is against :data:`BLOCKS_TODAY` and not :data:`KEEP_BLOCKS` — the keep is the sealed
    record's and never moves, and a producer that grew its keep to green itself would re-pin a
    registration instead of registering a run.
    """
    found = tuple(prereg.RATIFICATION_NAME.findall(spec.read_text(encoding="utf-8")))
    if found != BLOCKS_TODAY:
        refuse(
            f"{rel(spec)} carries the marked blocks {list(found)} and this producer knows"
            f" {list(BLOCKS_TODAY)}, of which the sealed pin keeps {list(KEEP_BLOCKS)}. A block that"
            " arrived since is text the registered law would be stripped of without a reader ever"
            " seeing it — add its name here and look at it"
        )


def suite_is_green(run=subprocess.run) -> tuple[dict, str]:
    """`make check`, run once — the fact the record carries, and the tail only a refusal prints.

    ``run`` is a seam and not a convenience: `tests/test_prereg_5c2.py` runs inside pytest, and a
    producer that shelled out to `make check` from a test would run the suite inside the suite. The
    test injects a verdict to exercise both branches AND greps :data:`CHECK` back out of the
    Makefile, because an injected runner proves the branch and says nothing about the command.

    The tail is returned BESIDE the record's block rather than inside it: pytest's last line carries
    the run's DURATION, and byte-identity under the same inputs is this record's gate. A field that
    moves because the machine was busy would void it on every second run.

    What the block says is therefore narrow and true: the verifier was green over the tree as it
    stood immediately BEFORE this write. On a re-run that includes this record's own tests, that is
    also the strongest statement available — a registration whose numbers moved would have reddened
    the equalities in `tests/test_prereg_5c2.py` and never reached the write at all.
    """
    done = run(CHECK, cwd=REPO_ROOT, capture_output=True, text=True)
    tail = ((done.stdout or "").strip().splitlines() or [(done.stderr or "").strip()])[-1]
    return {
        "command": " ".join(CHECK),
        "returncode": done.returncode,
        "green": done.returncode == 0,
        "measured": (
            "over the tree as it stood immediately before this write. The suite's last line is NOT"
            " kept here — it carries the run's duration and this record's gate is byte-identity"
        ),
    }, tail


def check_the_inputs_have_not_moved(out: Path) -> None:
    """Every sha256 an input record CLAIMS, re-hashed against the file it names.

    Re-hashing the files this producer is about to pin would be a tautology — the digests come from
    the same read — so what is checked here is the chain the record inherits and cannot see:

    * the D cut says which census it was computed over (`input.sha256`), and a cut built over an
      older census would carry a population that no longer belongs to the pinned window;
    * both upstream producers name themselves and the modules they borrow by sha (the 9c723a7
      finding), so a producer edited after its record was written is caught here rather than at the
      sitting;
    * a registration already on disk has its own `pinned_inputs`, and re-writing over it while any
      of them moved is exactly the "claim about a repo that no longer exists" this refuses.
    """
    cut = load(POSTCUT)
    if cut["input"]["sha256"] != sha256_of(CENSUS_C3A):
        refuse(
            f"{rel(POSTCUT)} was computed over a census hashing {cut['input']['sha256']} and"
            f" {rel(CENSUS_C3A)} now hashes {sha256_of(CENSUS_C3A)}. The D cut's population does"
            " not belong to the census this registration pins — re-run scripts/postcut_c3b.py"
        )
    for record_path in (CENSUS_C3A, POSTCUT):
        record = load(record_path)
        claims = {record["producer"]["script"]: record["producer"]["sha256"]} | record["producer"][
            "borrows"
        ]
        for path, digest in claims.items():
            if sha256_of(REPO_ROOT / path) != digest:
                refuse(
                    f"{rel(record_path)} names {path} at {digest} and it now hashes"
                    f" {sha256_of(REPO_ROOT / path)}. The record was written by code that has"
                    " changed since, so its numbers are not this repo's"
                )
    if out.exists():
        for path, digest in load(out)["pinned_inputs"].items():
            if pinned_sha256(REPO_ROOT / path) != digest:
                refuse(
                    f"{rel(out)} already pins {path} at {digest} and it now hashes"
                    f" {pinned_sha256(REPO_ROOT / path)}. A sealed registration is not re-pinned to"
                    " make it green — give the new one --out with another path and let the team"
                    " lead rule which is in force"
                )


def populations() -> dict:
    """The three legs' row counts, each read out of the record that counted it.

    The comment leg's selection is pinned by NINETEEN per-channel hashes rather than one: that is
    how `results/census_5c2.json` records it, and a hash-of-hashes invented here would be a number
    nothing else in the repo — least of all the run — could reproduce.
    """
    census = load(CENSUS_5C2)
    c3a_record = load(CENSUS_C3A)
    cut = load(POSTCUT)
    comments = {
        row["handle"]: row["comments"]["ids_sha256"]
        for row in census["channels"]
        if row["comments"] != "CANNOT ANSWER"
    }
    return {
        "comment": {
            "rows": census["totals"]["comments_unanswered_in_window"],
            "source": f"{rel(CENSUS_5C2)} :: totals.comments_unanswered_in_window",
            "sha256": sha256_of(CENSUS_5C2),
            "selection_pin": comments,
            "selection_pin_note": (
                "channels[].comments.ids_sha256, one per channel with a comment in the window —"
                " nineteen of them. The census records the selection this way and the run"
                " reproduces it channel by channel; a single hash over all of them would be a"
                " number no other reader in this repo can rebuild"
            ),
            "window": "2026-07-12 … 2026-08-09, the anchor ratified by 3.18 (7)(a)",
        },
        "leaflet_page": {
            "rows": c3a_record["leaflet_corpus"]["pages"],
            "source": f"{rel(CENSUS_C3A)} :: leaflet_corpus.pages",
            "sha256": sha256_of(CENSUS_C3A),
            "posts": c3a_record["leaflet_corpus"]["posts"],
            "selection_pin": c3a_record["leaflet_corpus"]["manifest"],
            "supersedes": {
                "was": load(PROJECTION)["window"]["leaflet_pages_unanswered"],
                "record": rel(PROJECTION),
                "why": (
                    "3.18 (7)(d): the population is the leaflet corpus ON DISK, «NOT"
                    " window-intersected» — «leaflets follow their own weekly cadence, and the"
                    " window clause of (4) binds the comment and post legs only». The c2 projection"
                    " priced the 78 pages inside the window and is a true statement of its write"
                    " moment; this registration buys all 159 and is not a correction of it"
                ),
            },
        },
        "post_text": {
            "rows": cut["kept"]["rows"],
            "source": f"{rel(POSTCUT)} :: kept.rows",
            "sha256": sha256_of(POSTCUT),
            "selection_pin": cut["kept"]["ids_sha256"],
            "selection_pin_note": (
                "sha256 of the kept ids, newline-joined in that record's order. The count says how"
                " many; this says WHICH, and a run that asked 44 other posts would not match it"
            ),
            "cut_from": cut["input"]["passed"],
            "rule": "3.18 (7)(g), the D cut — computed by scripts/postcut_c3b.py, never re-decided",
        },
    }


def prices(rate: float) -> dict:
    """One block per leg: the dollars corner, the wall-clock corner, and which model each is.

    Dv274's discipline, stated per field rather than once: the comment leg has TWO paid corners that
    disagree by 9% and each answers a different question, so a single `seconds_per_row` printed
    beside a single `usd` would be one number from each model with no denominator anybody could
    name. The other two legs have one corner each and say so.
    """
    comment = projection.comment_leg(rate, 0)["corners"]
    return {
        "comment": {
            "usd_model": {
                "value": comment["unit_cost"]["value"],
                "unit": "usd_per_1000_rows",
                "source": f"{rel(RATE)} :: measured.usd_per_1000_rows",
                "session": "srv-2d, 2026-08-08, serverless endpoint hbq25reui1tpj6",
                "why": "the CONSERVATIVE corner — that session's boot is already amortised inside it",
            },
            "seconds_model": {
                "value": comment["marginal_plus_boot"]["value"],
                "unit": "seconds_per_row",
                "source": f"{rel(RATE)} :: measured.like_for_like_seconds_per_row",
                "session": "srv-2d, 2026-08-08, serverless endpoint hbq25reui1tpj6",
                "why": (
                    "the MARGINAL corner, cold start taken out — the only corner whose seconds were"
                    " counted rather than divided out of a price, so the wall clock comes from here"
                ),
            },
        },
        "leaflet_page": {
            "usd_model": {
                "value": None,
                "unit": "usd_per_1000_rows",
                "source": "NO UNIT-COST CORNER",
                "why": (
                    "skub2 measured this leg in seconds, not in dollars per row: the dollars below"
                    " are its seconds at the settled rate, and the record says so rather than"
                    " printing a unit cost nothing measured"
                ),
            },
            "seconds_model": {
                "value": projection.leaflet_leg(rate, 0)["seconds_per_page"],
                "unit": "seconds_per_page",
                "source": (
                    "results/sku_b_positions_skub2.json ::"
                    " projection.per_gate[-1].marginal_seconds_per_call"
                ),
                "session": "skub2-run, 2026-08-12, the serverless POSITIONS endpoint",
                "why": "the last in-run gate, taken when all 108 done calls were pages",
            },
        },
        "post_text": {
            "usd_model": {
                "value": None,
                "unit": "usd_per_1000_rows",
                "source": "NO UNIT-COST CORNER",
                "why": "the same as the leaflet leg's — skub2's text leg was measured in seconds",
            },
            "seconds_model": {
                "value": c3a.b2.text_marginal(
                    load(REPO_ROOT / "results" / "sku_b_positions_skub2.json")
                ),
                "unit": "seconds_per_row",
                "source": "results/sku_b_positions_skub2.json :: derived, no single field holds it",
                "session": "skub2-run, 2026-08-12, the same session's TEXT leg — 30 rows, PAID",
                "why": (
                    "write_sku_projection_b2.text_marginal, the house derivation reused rather than"
                    " rewritten. 3.18 (7)(e) names this rate for this leg"
                ),
            },
        },
    }


def legs(rate: float, counts: dict) -> dict:
    """Each leg costed on its own population, at its own corners."""
    comment = projection.comment_leg(rate, counts["comment"]["rows"])
    leaflet = projection.leaflet_leg(rate, counts["leaflet_page"]["rows"])
    post = c3a.priced(counts["post_text"]["rows"], rate)
    return {
        "comment": {
            "rows": comment["window_rows"],
            "usd_with_drift": comment["corners"]["unit_cost"]["usd_with_drift"],
            "billed_seconds": comment["corners"]["marginal_plus_boot"]["billed_seconds"],
            "fixed_seconds": comment["fixed_seconds"],
        },
        "leaflet_page": {
            "rows": leaflet["window_pages"],
            "usd_with_drift": leaflet["corners"]["marginal_plus_boot"]["usd_with_drift"],
            "billed_seconds": leaflet["corners"]["marginal_plus_boot"]["billed_seconds"],
            "fixed_seconds": leaflet["fixed_seconds"],
        },
        "post_text": {
            "rows": post["rows"],
            "usd_with_drift": post["usd_with_drift"],
            "billed_seconds": post["billed_seconds"],
            "fixed_seconds": post["fixed_seconds"]["idle_tail"],
            "no_boot": post["fixed_seconds"]["boot"],
        },
    }


def budget() -> dict:
    """What is left of the phase, DERIVED from the live cap — never read off the ledger's own field.

    `results/spend_phase4.json :: sessions[-1].remaining_usd` is 6.1690 and it is not wrong: it was
    written under the 30 cap, and 3.18 (7)(b) says records written under an earlier cap are never
    re-scored by a later one. What that means for THIS producer is that the field cannot be used —
    `spent_usd` is the fact that survives the cap change, and the remainder is arithmetic over the
    cap in force. Both are printed with the cap each was computed under, because a reader who sees
    only one of them cannot tell which question it answers.
    """
    last = load(LEDGER)["sessions"][-1]
    return {
        "phase_cap_usd": guard.PHASE_CAP_USD,
        "cap_source": "scripts/runpod_guard.py :: PHASE_CAP_USD (the line that ENFORCES it)",
        "spent_usd": last["spent_usd"],
        "remaining_usd": round(guard.PHASE_CAP_USD - last["spent_usd"], 4),
        "remaining_is_derived": (
            "PHASE_CAP_USD - sessions[-1].spent_usd, not sessions[-1].remaining_usd — that field"
            " reads 6.1690 and is a true statement under the 30 cap it was written beside"
            " (3.18 (7)(b): records under an earlier cap are never re-scored)"
        ),
        "ledger_remaining_usd_under_its_own_cap": last["remaining_usd"],
        "cap_in_force_when_the_ledger_row_was_written": 30.00,
        "read_at": last["at"],
        "source": f"{rel(LEDGER)} :: sessions[-1]",
        "ledger_cap_usd": load(LEDGER)["phase4_cap_usd"],
    }


def session_cap(total_usd: float, money: dict) -> dict:
    """The three-leg total, rounded UP to the next half dollar, and checked against what is left."""
    cap = math.ceil(total_usd / HALF_DOLLAR) * HALF_DOLLAR
    return {
        "cap_usd": cap,
        "projected_usd_with_drift": round(total_usd, 4),
        "rounding": f"up to the next ${HALF_DOLLAR:.2f}",
        "remaining_usd": money["remaining_usd"],
        "fits": cap <= money["remaining_usd"],
        "headroom_usd": round(money["remaining_usd"] - cap, 4),
        "why": (
            "the cap is a LINE and not a forecast: it is rounded up so the run has room for the"
            " drift it already carries, and it is registered by VALUE (3.18 (7)(f)) so a later"
            " session cannot re-derive a bigger one from a moved input and call it the same cap"
        ),
    }


def stop_rules(cap: float, rate: float) -> dict:
    """3.18 (7)(c): "stop rules for a mid-run truncation are the pre-registration's to state"."""
    return {
        "go_no_go": {
            "law": "SPEC 3.17 (10)(a), applying unchanged (3.18 (5))",
            "rule": (
                "after the two non-gold warm-up calls, the driver re-projects the WHOLE run from"
                " the warm-up-measured marginal plus everything already billed, and REFUSES to make"
                " any gold call if that projection exceeds what is left of the"
                f" ${cap:.2f} session cap"
            ),
            "consequence": (
                "a session stopped at this gate has touched no gold and consumed no attempt; it"
                " returns to the team lead for a re-registration under the measured price"
            ),
            "the_warmup_must_cost_what_the_run_costs": (
                "3.17 (11)(c)'s lesson, which this run inherits: a 64x64 probe priced a leaflet page"
                " at 1/3.5 of the truth and the gate passed the run it exists to refuse. The"
                " warm-up inputs are REPRESENTATIVE ones — a real leaflet page and a real post row"
            ),
        },
        "mid_run_cap_gate": {
            "law": "SPEC 3.17 (10)(b)",
            "rule": (
                "a cap stop that fires after gold calls began is a finding about the CAP and not"
                " about the instrument. It closes nothing, fails no bar, and what happens next is a"
                " team-lead ruling — never a silent re-run"
            ),
        },
        "per_job_ceiling": {
            "law": "SPEC 3.17 (10)(c)",
            "rule": (
                "no single job may be CAPABLE of billing past the remaining cap on its own, and a"
                " job that ends TIMED_OUT ends the run with its unbought remainder recorded"
            ),
            "execution_timeout_s": driver.JOB_TIMEOUT_S,
            "worst_case_job_usd_with_drift": round(driver.JOB_TIMEOUT_S * rate * (1 + DRIFT), 4),
            "against_the_session_cap_usd": cap,
            "satisfied": driver.JOB_TIMEOUT_S * rate * (1 + DRIFT) < cap,
            "why_the_session_cap_and_not_the_phase_cap": (
                "the clause bounds one wedged job against what THIS run may still spend, and what"
                " this run may spend is its registered cap — the phase cap is a larger line that"
                " several sessions share"
            ),
        },
        "resume": {
            "rule": (
                "on any stop, the run resumes from the per-channel watermark plus the answered-set"
                " on disk: `comment`, `leaflet_page` and — since the fourth evidence kind —"
                " `post_text`, each written LAST for its input, so a row that was paid for is never"
                " bought twice and a row that was not is never skipped"
            ),
            "why_the_fourth_kind_is_named_here": (
                "until it existed the post leg had no marker and an interrupted pass re-bought"
                " every post that had answered `[]` or come back unparseable. That is a resume"
                " discipline with a hole in it, and the hole was priced in rows this cap pays for"
            ),
        },
    }


def validate_consequence() -> dict:
    """3.18 (6): the sitting is unbuildable unless the run PERSISTS its per-row evidence."""
    return {
        "law": "SPEC 3.18 (6), the operator sitting the phase does not close without",
        "the_run_must_persist": {
            "every_row": list(evidence.REQUIRED),
            "by_kind": {kind: list(fields) for kind, fields in evidence.KIND_FIELDS.items()},
        },
        "source": "src/market_pulse.evidence :: REQUIRED and KIND_FIELDS, the one place that names it",
        "why_the_fields_are_listed_here": (
            "a registration that said «the run persists evidence» would be satisfied by a run that"
            " persisted three fields. `results/predictions/LOST.md` is the precedent: a per-row dump"
            " that was never written and cannot be reconstructed at any price"
        ),
        "kinds": list(evidence.KINDS),
        "the_fourth_kind": (
            "`post_text`, ruled by the team lead at the c3a acceptance (Dv285). It carries nothing"
            " of its own — the post's text IS its `rendering` — and it is what makes «this post was"
            " read and yielded nothing» a fact on disk"
        ),
    }


def not_in_scope() -> dict:
    return {
        "the price-pair leg": (
            "bar 2 measured 0.4125 against 0.80 and 3.18 (2) admits it to NO price surface. It"
            " contributes only what 3.18 (1) allows: the code-computed depth and the"
            " printed-vs-computed disagreement flag"
        ),
        "the 8 809 posts the cut removes": (
            "3.18 (7)(e) filtered the leg and (7)(g) cut it again. The projection's 9 158-post raw"
            " bound «enters no cap and no session»"
        ),
        "other chains' leaflets": (
            "ATB-only for this cycle (3.18 (7)(d)); collecting the others is an authorised"
            " zero-cost prep, never inside this session"
        ),
        "the 11 338-row history": "a visibly deferred decision (3.18 (4)); this session buys a window",
        "aggregates": (
            "no promo aggregate is computed in 5c2-run. The legs of 3.18 (2) are verified on the"
            " window's own output at acceptance"
        ),
    }


def producer() -> dict:
    return {
        "script": rel(Path(__file__)),
        "sha256": sha256_of(Path(__file__)),
        "why": "no git block: `git status --porcelain` is a fact about the tree, not the measurement",
        "borrows": {
            rel(Path(module.__file__)): sha256_of(Path(module.__file__))
            for module in (projection, c3a, prereg, guard, driver)
        },
    }


def main(argv: list[str] | None = None, *, run=subprocess.run) -> int:
    """``run`` is the verifier seam — see :func:`suite_is_green`. It is a keyword argument and NOT
    a CLI flag on purpose: an operator cannot hand this producer a runner that always says green."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=RECORD)
    args = parser.parse_args(argv)

    check_the_strip_family_is_what_it_says(SPEC)
    verifier, tail = suite_is_green(run)
    if not verifier["green"]:
        refuse(
            f"`{verifier['command']}` exited {verifier['returncode']}. A pre-registration made over"
            f" a red repo registers a run nobody can reproduce — the last line was: {tail}"
        )

    pinned = {
        rel(path): pinned_sha256(path)
        for path in (
            SPEC,
            CENSUS_5C2,
            CENSUS_C3A,
            POSTCUT,
            PROJECTION,
            RATE,
            REGISTRY,
            LEXICON,
            POSITIONS,
        )
    }
    check_the_inputs_have_not_moved(args.out)

    rate = projection.cite(
        projection.RATE,
        "rate.usd_per_second",
        "the settled serverless rate — the field every projection in this repo has used since sku-b",
    )
    counts = populations()
    costed = legs(rate["value"], counts)
    money = budget()
    total = sum(leg["usd_with_drift"] for leg in costed.values())
    seconds = sum(leg["billed_seconds"] for leg in costed.values())
    cap = session_cap(total, money)

    record = {
        "phase": "5c2-run — one paid session, pre-registered",
        "class": (
            "PRE-REGISTRATION. Written BEFORE the session exists (3.18 (5)) and sealed: the run is"
            " judged against these numbers and they are never re-derived to fit what it spent"
        ),
        "contract": "docs/PROMPT-5c2-prep-c3b.md deliverable 2; docs/SPEC.md amendment 3.18 (5), (6), (7)",
        "authority": "docs/SPEC.md amendment 3.18 as it stands 2026-08-13, including (7)(a)–(g)",
        "pinned_by_value": (
            "3.18 (7)(f): «the registered cap row gets equality tests, not ceilings». Every number"
            " in `populations`, `prices`, `legs` and `session_cap` has an equality in"
            " tests/test_prereg_5c2.py; `session_cap.fits` is an ADDITIONAL check beside them"
        ),
        "verifier": verifier,
        "strip": {
            "keep": list(KEEP_BLOCKS),
            "why": (
                "every marked block docs/SPEC.md carries today, so the registered law IS the file as"
                " it stands. B′ keeps two because the rest postdate the records it sits beside; this"
                " registration is written the same day as its own amendment, and 3.18 (7)(c) sends"
                " the stop rules to 3.17 (10) inside sku-b-ratification-4 — a pin that stripped it"
                " would register a document not carrying the discipline this record names"
            ),
            "the_registered_law_is_the_file_as_it_stands": (
                "keeping all ten means the pin equals sha256 of the file TODAY. Its job starts the"
                " day they diverge: a block added later is stripped and this pin survives, which is"
                " the only legal way to green a law that grew. New text arrives inside its own"
                " marked block — a sealed registration is never re-pinned to make it green"
            ),
        },
        "pinned_inputs": pinned,
        "populations": counts,
        "prices": prices(rate["value"]),
        "rate": rate,
        "drift": {"factor": DRIFT, "why": "a contract term, not a measurement — carried unchanged"},
        "legs": costed,
        "whole_session": {
            "usd_with_drift": round(total, 4),
            "usd_source": "the conservative corner of each leg, summed",
            "billed_seconds": round(seconds, 1),
            "hours": round(seconds / 3600, 2),
            "jobs_at_the_execution_timeout": -(-int(seconds) // int(driver.JOB_TIMEOUT_S)),
            "workers_max": 1,
            "seconds_source": "the marginal corner of each leg — the only counted seconds",
            "why_it_is_larger_than_the_c2_projection_and_still_fits": (
                "$7.6870 with `fits: false` against $7.8546 with `fits: true` is TWO supersessions"
                " and no correction: the leaflet leg's population moved 78 → 159 (3.18 (7)(d)) and"
                " the phase cap moved 30 → 33 (3.18 (7)(b)). results/projection_5c2.json is a true"
                " statement of its write moment and is never regenerated"
            ),
        },
        "session_cap": cap,
        "budget": money,
        "stop_rules": stop_rules(cap["cap_usd"], rate["value"]),
        "validate_consequence": validate_consequence(),
        "not_in_scope": not_in_scope(),
        "producer": producer(),
    }
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"`{verifier['command']}` green: {verifier['green']} · {len(pinned)} inputs pinned")
    header = f"\n{'leg':<14}{'rows':>7}{'$ with drift':>14}{'seconds':>11}"
    print(header)
    print("-" * (len(header) - 1))
    for name, leg in record["legs"].items():
        print(
            f"{name:<14}{leg['rows']:>7}{leg['usd_with_drift']:>14.4f}{leg['billed_seconds']:>11.1f}"
        )
    whole = record["whole_session"]
    print(f"{'TOTAL':<14}{'':>7}{whole['usd_with_drift']:>14.4f}{whole['billed_seconds']:>11.1f}")
    print(
        f"\nsession cap ${cap['cap_usd']:.2f} (projected ${cap['projected_usd_with_drift']:.4f},"
        f" rounded {cap['rounding']})"
    )
    print(
        f"  remaining ${money['remaining_usd']:.4f} under the ${money['phase_cap_usd']:.2f} cap"
        f" — fits: {cap['fits']}, headroom ${cap['headroom_usd']:.4f}"
    )
    print(
        f"  the ledger's own remaining_usd reads ${money['ledger_remaining_usd_under_its_own_cap']:.4f}"
        f" under the ${money['cap_in_force_when_the_ledger_row_was_written']:.2f} cap it was written beside"
    )
    print(
        f"  wall clock {whole['hours']} h · {whole['jobs_at_the_execution_timeout']} jobs at 900 s"
    )
    print(f"\nwrote {rel(args.out)}")
    return 0 if cap["fits"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
