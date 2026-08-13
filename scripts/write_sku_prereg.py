#!/usr/bin/env python3
"""Write `results/sku_pilot_prereg_v4.json` — sku-b's three bars, on a fresh ledger ($0).

Deliverable 5 of `docs/PROMPT-sku-a.md`, re-registered by uni-b deliverable D(2) under SPEC
3.17 (8), by sku-b-v3-prep D1 under SPEC 3.17 (11) and again by sku-b-v4-prep D1 under SPEC
3.17 (12). A pre-registration that is not committed is not a pre-registration, and a
pre-registration committed after the artifact it judges is a rationalisation: git history is the
only witness to the ordering, so this file goes in its own commit — before any artifact of the v4
session exists.

**Each version is registered BESIDE the last, never over it.** v1 (`b1bfa40d…`), v2 (`d4ced2a8…`)
and v3 (`a80e8e55…`) are not edited and not deleted: they are what was registered, they stay
byte-identical under sealed tests, and each record names its predecessor in `supersedes` with the
reason. v1 → v2 moved PINS (the ladder's hash followed the `fat` → `attribute` rename and the pack
manifest was rebuilt over it). v2 → v3 moved the ATTEMPT CLAUSE and nothing else about the
measurement: the (10)(b) stop at 17 of 138 gold calls resolves as RESUME, so the clause became
3.17 (11)'s, the cap became $0.45, the warm-up inputs became representative, and a
`resume.bought_already` block pinned what the first session already bought.

v3 → v4 moves LESS than that, and the reason is the shape of what happened: v3's session was
refused by the (10)(a) gate on its own representative probe, before the first gold call, so it
consumed no attempt and bought nothing. Nothing it measured belongs to a bar. What moves is the
cap ($0.45 → $0.65, 3.17 (12)(a)) and the two names that decide which anchor the next session
enforces that cap against (3.17 (12)(b) — the Dv167 finding: a refused session's spend is the
PHASE's overhead and never the next attempt's burden, and cap, ledger and phase are set TOGETHER
or one of them is silently another session's). The whole `resume` block — population, the (11)(c)
warm-up pins, `bought_already`'s 17 of 138 — every bar, threshold, reachability rule and all five
R1–R5 readings are byte-equal to v3 and asserted so.

Three things it carries, and the second is the one that costs work:

* **the bars, verbatim.** Quoted out of `docs/SPEC.md` amendment 3.17 (6) and checked against it on
  every run — a bar retyped is a bar that can drift from the law it claims to be.
* **the procedure for each one.** A ratio needs a denominator, and every denominator here had a
  question SPEC does not answer: the leaflet gold exists per POST while the bar says "per page", 4 of
  the 19 posts have an empty gold set, and bar 2's denominator is discovered by the run itself. Each
  reading is written down with what it excludes, and the ones that are the EXECUTOR's rather than
  SPEC's are listed in `ratification_required` — sku-b is one paid attempt and a failed bar closes B
  by measurement, so a denominator nobody ratified is a session spent against a void.
* **the inputs, pinned.** The reference record, the pack manifest, the census frame, the tier
  ladder's own hash and both prompt shas. Bar 3's gold is computed from the operator's ticks by
  `positions.tier_from_presence`, so the ladder is an input like any other. `docs/SPEC.md` is
  pinned as its REGISTERED LAW — the file with amendment 3.17 (7)'s marked block stripped, see
  `registered_law` — because that amendment records the ratification of readings already in here
  and a pin that follows the file is not a pin.

    PYTHONPATH=src python3 scripts/write_sku_prereg.py
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_sku_text_pack as text_pack  # noqa: E402

from build_audit_pack import git_state  # noqa: E402

from market_pulse import positions, prompts  # noqa: E402
from market_pulse.registry import registry_before_the_latin_aliases  # noqa: E402

SPEC = REPO_ROOT / "docs" / "SPEC.md"
REFERENCE = REPO_ROOT / "results" / "sku_reference_leaflet.json"
PACK_MANIFEST = REPO_ROOT / "results" / "sku_text_pack_manifest.json"
CENSUS = REPO_ROOT / "results" / "sku_prefilter_census.json"
REGISTRY = REPO_ROOT / "config" / "registry.yaml"
LEXICON = REPO_ROOT / "config" / "lexicon.yaml"
SUPERSEDED = REPO_ROOT / "results" / "sku_pilot_prereg_v3.json"
RECORD = REPO_ROOT / "results" / "sku_pilot_prereg_v4.json"
BOUGHT_UNDER = REPO_ROOT / "results" / "sku_pilot_prereg_v2.json"
"""Two different questions, and v4 is the version where they stop having the same answer.

`SUPERSEDED` is the record this one is registered BESIDE — v3, retired UNSPENT: its session was
refused at the (10)(a) gate before the first gold call. `BOUGHT_UNDER` is what the 17 paid answers
were actually bought under, which is v2 and stays v2 however many re-registrations follow it."""

REFUSED = REPO_ROOT / "results" / "sku_b_positions_v3.json"
"""The (10)(a) refusal record, pinned in `supersedes` because it is the evidence for the one claim
v4 inherits without re-deriving: the v3 session bought NOTHING, so the population is still 121."""

SERVING_PIN = REPO_ROOT / "results" / "sku_pilot_serving.json"
RUN_RECORD = REPO_ROOT / "results" / "sku_b_positions.json"
RUN_DUMP = REPO_ROOT / "results" / "sku_b_positions.jsonl"
"""What the interrupted session left behind, pinned into `resume.bought_already`.

Not `pinned_inputs`: those are the bar's INPUTS and they are byte-equal to v2 by construction. These
three are EVIDENCE of what was already bought, and the resumed run refuses to start unless they
still hash to what is registered here (SPEC 3.17 (11)(a): each element is bought exactly once)."""

SUPERSEDES_REASON = (
    "v3 was registered and never spent: its session was refused at the (10)(a) gate on the"
    " representative probe (11)(c) registered, before the first gold call, so it bought nothing and"
    " consumed no attempt. SPEC 3.17 (12) authorises ONE more resumed session in its place. What"
    " moves is the CAP ($0.45 → $0.65, (12)(a): sized to admit the gate's own pessimistic"
    " projection of ~$0.60, whose probe is a deep leaflet page and prices above the first-six-page"
    " population's drawn marginal) and the two NAMES that decide which anchor that cap is enforced"
    " against ((12)(b): each attempt runs under its own fresh anchor with cap, ledger and phase set"
    " together). No bar, no threshold, no reachability rule, no registered reading and nothing in"
    " `resume` moves — not the population, not the (11)(c) warm-up pins, not bought_already's 17 of"
    " 138. So v3 is not edited: it stays exactly as it was registered, it is what the refused"
    " session ran under, and this record is registered BESIDE it, before the v4 session"
)

BARS = {
    "leaflet_brand_recall": "leaflet brand-recall ≥ 0.75 per page vs audit-visible brands",
    "price_pair_accuracy": (
        "price-pair accuracy ≥ 0.80 on positions carrying a crossed-out price (verified by"
        " team-lead read of the per-position dump against the images at acceptance)"
    ),
    "text_tier_accuracy": "text tier-assignment accuracy ≥ 0.85 vs adjudicated rows",
}
"""The three bars of SPEC 3.17 (6), word for word. Checked against the file on every run."""

ONE_ATTEMPT = (
    "sku-b (one paid session, cap $0.35 GPU): the two-leg pilot (19 ATB posts page-wise; ~30"
    ' adjudicated text rows), one attempt; a failed bar closes B as "instrument not ready" by'
    " measurement."
)
GREEN_GATE = "Integration into the 5c2 loop only on a green gate."

RESUME_CLAUSE = (
    "The (10)(b) stop at 17 of 138 gold calls resolves as RESUME: the registered population is"
    " bought to completion in ONE additional paid session under a re-registration"
    " (results/sku_pilot_prereg_v3.json, registered BESIDE v2 before the resumed session)."
)
"""SPEC 3.17 (11)'s own sentence. It REPLACES (6)'s one-attempt clause in `attempts.verbatim` and
does not delete it — (6) is what the first session was bought under and it is quoted beside."""

RESUME_READINGS = {
    "a": (
        "each element of the registered population (108 pages + 30 rows) is bought EXACTLY ONCE"
        " across the program — the resumed session buys only the 121 recorded as unbought, and the"
        " 17 existing answers (including the one parse refusal) enter the bars as they stand, never"
        " re-asked"
    ),
    "b": (
        "the instrument is FROZEN as registered — prompts, parser and serving pin unchanged; the"
        " superscript and asterisk findings are a post-pilot NAMED revision, never an in-flight edit"
    ),
    "c": (
        "for the resumed session the warm-up of (9) becomes REPRESENTATIVE: one real UNSENT page (of"
        " the 51 outside the R2 gold) and one real pre-filtered text row outside the 30-row pack;"
        " warm-up answers are never scored"
    ),
    "d": (
        "the resumed session's cap is $0.45, priced from the measured marginals; the go/no-go and"
        " every reading of (10) apply unchanged against that cap"
    ),
    "e": (
        "the team lead's calibration read of the 13 prefix pairs (6 correct) is NON-GATING: bar 2 is"
        " scored only by the team-lead read over the pairs of the COMPLETED population at acceptance"
    ),
}
"""(11)(a)–(e), transcribed rather than redesigned, and checked against `docs/SPEC.md` on every run
by the same function that checks the bars. A reading paraphrased here is a reading the resumed
session could be held to and the law does not contain."""

BARS_UNCHANGED = "The three bars' verbatim texts, thresholds and R1–R5 are unchanged."

V4_HEADLINE = (
    "The v3 session was refused by the (10)(a) gate on a representative probe (14.808 s/page from"
    " the registered unsent page) and consumed no attempt."
)
"""SPEC 3.17 (12)'s own finding, and the whole reason this record exists rather than a v3 re-run."""

V4_READINGS = {
    "a": (
        "ONE more resumed session is authorised under a v4 re-registration"
        " (results/sku_pilot_prereg_v4.json, BESIDE v3, before the session), cap **$0.65** — sized"
        " to admit the gate's own pessimistic projection (~$0.60), whose probe is structurally a"
        " DEEP leaflet page and prices above the first-six-page gold population's drawn marginal"
        " (5.0772 s, n=17); the in-run gate still protects the middle."
    ),
    "b": (
        "**A session refused at the (10)(a) gate charges the PHASE ledger, never the next attempt's"
        " cap:** each registered attempt runs under its own fresh anchor and its own"
        " cap/ledger/phase constants, set together (the Dv167 finding)."
    ),
    "c": (
        "The warm-up inputs remain the REGISTERED ones of v3 — the same unsent page and the same"
        " non-pack row, re-verified by hash, never re-picked."
    ),
    "d": (
        "Every reading of (10) and (11) otherwise applies unchanged; the population is still the 121"
        " unbought elements, each element of the 138 bought exactly once across the program."
    ),
}
"""(12)(a)–(d), transcribed rather than redesigned and checked against `docs/SPEC.md` by the same
function that checks the bars. The markdown emphasis is carried because the check is verbatim: a
quote that tidies the law is a quote that can drift from it."""

RESUME_CAP_USD = 0.65
"""SPEC 3.17 (12)(a). Transcribed, not chosen. (11)(d)'s $0.45 is what v3 was registered under and
it is not edited anywhere — it stays in `resume.readings.d` as the reading v3 ran under, superseded
here by (12)(a) and not overwritten by it."""

RESUME_PHASE = "sku-b-v4"
RESUME_LEDGER = REPO_ROOT / "results" / "spend_sku_b_v4.json"
"""SPEC 3.17 (12)(b): the cap above and these two names are ONE decision, so they are registered
together and the driver's copies are asserted equal to them.

Dv167 is what this pays: v3's three constants were a cap, a ledger path and a phase key living in
three places, and a second `--resume` after the refusal would have read the v3 anchor, subtracted a
refused session's $0.1526 from a cap priced without it, and refused again on arithmetic nobody
chose. A refusal charges the PHASE, and the next attempt starts on a fresh anchor of its own."""


def verbatim(spec: Path) -> str:
    """The amendment as one line, so a quote can be checked against it regardless of wrapping."""
    return " ".join(spec.read_text(encoding="utf-8").split())


def check_the_bars_are_the_laws(spec: Path) -> None:
    law = verbatim(spec)
    quoted = {
        **BARS,
        "one_attempt": ONE_ATTEMPT,
        "green_gate": GREEN_GATE,
        "resume_clause": RESUME_CLAUSE,
        "bars_unchanged": BARS_UNCHANGED,
        "v4_headline": V4_HEADLINE,
        **{f"reading_{key}": text for key, text in RESUME_READINGS.items()},
        **{f"v4_reading_{key}": text for key, text in V4_READINGS.items()},
    }
    for name, bar in quoted.items():
        if bar not in law:
            raise SystemExit(
                f"{name}: this text is not in docs/SPEC.md as written. A pre-registration that"
                " paraphrases its own bar cannot be held to it"
            )


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


RATIFICATION_BEGIN = "<!-- sku-b-ratification begin"
RATIFICATION_END = "<!-- sku-b-ratification end -->"
RATIFICATION_NAME = re.compile(
    r"^<!-- (sku-b-ratification(?:-\d+)?|amendment-(?:index|3\.\d+)) begin", re.MULTILINE
)
"""Every marked block `docs/SPEC.md` wears, by name — the family the strip takes off before hashing.

**What the family is FOR.** `pinned_inputs` holds the WHOLE spec, and the spec keeps growing after a
registration is sealed. Text that arrives later and moves no bar of the record it would break wears
its own markers, so the REGISTERED LAW is what is left when they all come off: the ratifications of
readings a record already carries (3.17 (7)–(14), `sku-b-ratification` … `-8`), the amendment index
repaired 2026-08-13 (`amendment-index`, a finding aid — the heading's `rev. 3.14` is deliberately
NOT corrected, because the pins hash that line), and an amendment ruled after the pin was taken
(`amendment-3.18`). Extending this expression is the only legal way to green a law that grew;
re-pinning a sealed registration is not — those records are the pilot's witness.

**A block this expression does not know is not stripped**, so the pin stops re-deriving and
`tests/test_sku_prereg.py::test_every_pinned_input_still_hashes_to_what_it_says` goes RED. That is
the design: an amendment cannot arrive quietly. Greening it is one name here and one line in that
test's literal enumeration, both of which have to be looked at.

One expression, one implementation: `write_sku_prereg_b2.py` and both test modules reach
`registered_law` through this module, so this is the single point of change."""


def registered_law(spec: Path, keep: tuple[str, ...] = ()) -> bytes:
    """`docs/SPEC.md` with every marked ratification block cut out except those named in ``keep``.

    ``keep`` is empty for v1–v4 and that is the whole of their story: each was registered before the
    blocks existed. It is NOT empty for B′, which is registered UNDER 3.17 (13) — a pin taken over a
    law with its own authority stripped out would be a pin on a document that does not authorise the
    run it registers. One implementation with a parameter, rather than a second strip beside it,
    because the two would drift and only one of them writes the records.

    A ratification amendment records that readings this record already carries were accepted — it
    moves no bar, no threshold and no denominator — but it moves the file's bytes, and the pin
    predates it. Re-pinning would make the pin follow the file instead of holding it, so each such
    block wears its own markers and the REGISTERED LAW is what is left when they all come off.
    Stripping ALL of them (uni-b, for 3.17 (8)) rather than the first is what keeps the v1 pin
    `973c8789…` re-derivable after the second amendment lands: a strip that knew one block would
    leave (8) in the hash and the pre-registration would stop verifying at this commit.

    One implementation, called by the producer and by `tests/test_sku_prereg.py`: a second copy of
    this strip would drift from the one that writes the record and nothing downstream could see it.
    """
    text = spec.read_text(encoding="utf-8")
    if unknown := sorted(set(keep) - set(RATIFICATION_NAME.findall(text))):
        raise SystemExit(f"{rel(spec)}: asked to keep {unknown}, which the file does not carry")
    for name in RATIFICATION_NAME.findall(text):
        if name in keep:
            continue
        begin, end_marker = f"<!-- {name} begin", f"<!-- {name} end -->"
        if text.count(begin) != 1 or text.count(end_marker) != 1:
            raise SystemExit(f"{rel(spec)}: ratification block {name} must appear exactly once")
        start = text.index(begin)
        end = text.index(end_marker, start) + len(end_marker)
        if (start and text[start - 1] != "\n") or not text[end:].startswith("\n"):
            raise SystemExit(f"{rel(spec)}: ratification block {name} does not own whole lines")
        text = text[:start] + text[end + 1 :]
    return text.encode("utf-8")


def registered_bytes(path: Path) -> bytes:
    """The bytes THIS registration registered — not always the bytes on disk today.

    Two inputs have moved since under an amendment that says so out loud, and each is undone by the
    function that owns it: `docs/SPEC.md` by :func:`registered_law` (the marked ratification blocks
    come off) and `config/registry.yaml` by
    :func:`market_pulse.registry.registry_before_the_latin_aliases` (SPEC 3.17 (13)(b)'s three
    Latin display names come out). Everything else is hashed as it sits.

    This producer writes v1–v4, all of which predate (13)(b). B′ registers the AMENDED registry and
    has its own producer — a pre-registration that reached back through this function would pin the
    alias table it is being written to replace.
    """
    if path == SPEC:
        return registered_law(path)
    if path == REGISTRY:
        return registry_before_the_latin_aliases(path)
    return path.read_bytes()


def pinned_sha256(path: Path) -> str:
    """What the pre-registration pins — see :func:`registered_bytes`."""
    return hashlib.sha256(registered_bytes(path)).hexdigest()


WARMUP_SEED = 42
"""The same seed the pack was drawn under. One seed in this pilot, so a reader does not have to ask
which draw a number came from."""


def resume_warmup(reference: dict, manifest: dict) -> dict:
    """SPEC 3.17 (11)(c): the two REPRESENTATIVE warm-up inputs, picked once and REGISTERED.

    The interrupted session opened on a generated 64x64 image and an invented row. They answered in
    1.436 s and 0.756 s, the go/no-go of (10)(a) priced 138 gold calls off those marginals and let
    the run proceed — and the first real leaflet page cost 5.0772 s, 3.54x the warm-up. The gate
    passed the run it exists to refuse, and the defect was the PROBE rather than the arithmetic:
    seconds are seconds, and nothing inside the gate could see that a thumbnail and a 7 MB leaflet
    page are the same op on different work.

    So the probe is fixed on the axis that moves the number, and left deliberately unrepresentative
    on the axis that must not move: both inputs are REAL and full-size, and neither is gold. The
    page is one of the 51 the reference records as NOT sent — outside R2's registered page set, so
    bar 1 cannot see it — and the row is one the pre-filter passed and the 30-row pack did not draw.

    Picked HERE and pinned, not re-derived by the driver. A registered input the paid run looks up
    cannot drift from the one that was registered; a rule the paid run re-runs can — and this is the
    session where a warm-up input that quietly landed inside the gold would contaminate the very
    denominator the resume exists to complete.
    """
    import random

    sent = {page["file"] for post in reference["posts"] for page in post["pages_sent"]}
    unsent = [file for post in reference["posts"] for file in post["pages_not_sent"]]
    expected = reference["population"]["pages_available"] - reference["population"]["pages_sent"]
    if len(unsent) != expected or set(unsent) & sent:
        raise SystemExit(
            f"{rel(REFERENCE)}: {len(unsent)} unsent pages against {expected} the population"
            f" implies, {len(set(unsent) & sent)} of them also sent. (11)(c)'s warm-up page has to"
            " come from outside the registered 108, and this reference cannot say which those are"
        )
    page = random.Random(WARMUP_SEED).choice(unsent)
    page_path = REPO_ROOT / page
    if not page_path.exists():
        raise SystemExit(f"{page}: (11)(c)'s warm-up page is not on disk")

    _, frame = text_pack.frame_from_census(CENSUS)
    drawn = set(manifest["ids"])
    outside = [row for row in frame if row["id"] not in drawn]
    if len(outside) != len(frame) - len(drawn):
        raise SystemExit(
            f"{rel(CENSUS)}: the 30-row pack's ids are not all in the frame — the warm-up row"
            " cannot be proved to sit outside a pack whose rows this frame does not contain"
        )
    row = random.Random(WARMUP_SEED).choice(outside)
    text = text_pack.store_text(row)
    if not text.strip():
        raise SystemExit(f"{row['id']}: the drawn warm-up row has no text; it would price nothing")

    return {
        "verbatim": RESUME_READINGS["c"],
        "why": (
            "the first session's warm-up priced a leaflet page at 1.436 s and the pages cost 5.0772"
            " s. A probe that is cheap on the axis being measured makes the go/no-go a gate that"
            " passes the run it exists to refuse — see results/sku_b_positions.json ::"
            " projection.go_no_go against projection.per_gate[0]"
        ),
        "seed": WARMUP_SEED,
        "page": {
            "rule": (
                "random.Random(42).choice over the pages results/sku_reference_leaflet.json records"
                " as NOT sent, in the reference's own order"
            ),
            "file": page,
            "sha256": sha256_of(page_path),
            "bytes": page_path.stat().st_size,
            "population": len(unsent),
            "not_gold": (
                "outside the 108 sent pages, so it is outside R2's registered page set and no bar"
                " reads it. A brand printed on it is in no gold set"
            ),
        },
        "text": {
            "rule": (
                "random.Random(42).choice over the census frame's rows whose id is not in the"
                " 30-row pack, in the census's own order"
            ),
            "id": row["id"],
            "channel": row["channel"],
            "carrier": row["carrier"],
            "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "text_chars": len(text),
            "read_by": "build_sku_text_pack.store_text — the raw store, the same reader the pack used",
            "population": len(outside),
            "not_gold": (
                "one of the pre-filtered rows the seed-42 pack did NOT draw, so it is outside bar"
                " 3's adjudicated set. The text itself is not copied here: it is a collected row"
                " and the raw store is where it lives — the sha is what proves the resumed session"
                " read the same one"
            ),
        },
        "never_scored": (
            "both answers are recorded in the run record and enter NO bar artifact. What they buy is"
            " the cold start, the proof the instrument answers, and the only honest marginal that"
            " exists before the first gold call of the resumed session"
        ),
    }


def bought_already() -> dict:
    """SPEC 3.17 (11)(a): what the interrupted session already bought, pinned so it is never rebought.

    Everything here is READ out of `results/sku_b_positions.json` and re-derived against the files
    on disk. Four agreements are checked rather than assumed, because each one is a way the resume
    could quietly buy the wrong thing: the record must have been written under v2 as v2 now stands,
    under the serving pin as it now stands ((11)(b): the instrument is frozen), over the dump as it
    now hashes, and its asked and unbought sets must partition the registered 138 with no id in both.
    """
    run = json.loads(RUN_RECORD.read_text(encoding="utf-8"))
    asked = [row["source"] for row in run["outcomes"]]
    unbought = list(run["population"]["unbought"])
    agreements = {
        f"the run was bought under {rel(BOUGHT_UNDER)} as it now stands": (
            run["prereg"]["sha256"],
            sha256_of(BOUGHT_UNDER),
        ),
        f"the run served under {rel(SERVING_PIN)} as it now stands": (
            run["serving_pin"]["sha256"],
            sha256_of(SERVING_PIN),
        ),
        f"the record describes {rel(RUN_DUMP)} as it now hashes": (
            run["dump"]["sha256"],
            sha256_of(RUN_DUMP),
        ),
    }
    for claim, (recorded, on_disk) in agreements.items():
        if recorded != on_disk:
            raise SystemExit(
                f"{claim} — it does not: the record says {recorded[:16]}… and the file hashes"
                f" {on_disk[:16]}…. A resume registered against a moved artifact would buy against"
                " evidence nobody can re-derive; stop and report."
            )
    if len(set(asked)) != len(asked) or set(asked) & set(unbought):
        raise SystemExit(
            f"{rel(RUN_RECORD)}: {len(asked)} asked ids with {len(set(asked))} distinct and"
            f" {len(set(asked) & set(unbought))} of them also unbought. (11)(a) buys each element"
            " EXACTLY ONCE and this record cannot say which those are."
        )
    registered = run["population"]["pages_sent"] + run["population"]["text_rows"]
    if len(asked) + len(unbought) != registered:
        raise SystemExit(
            f"{rel(RUN_RECORD)}: {len(asked)} asked + {len(unbought)} unbought against"
            f" {registered} registered. The resume's population is the difference and it does not"
            " add up."
        )
    return {
        "verbatim": RESUME_READINGS["a"],
        "why": (
            "the resumed session's population is this record's `unbought` and nothing else. Pinned"
            " by sha so a run against a moved record refuses: these are answers that were PAID for"
            " once, under a one-attempt clause, and there is no second draw for any of them"
        ),
        "run_record": {"path": rel(RUN_RECORD), "sha256": sha256_of(RUN_RECORD)},
        "dump": {
            "path": rel(RUN_DUMP),
            "sha256": sha256_of(RUN_DUMP),
            "rows": run["dump"]["rows"],
            "price_pairs_n": run["dump"]["price_pairs"]["n"],
        },
        "serving_pin": {
            "path": rel(SERVING_PIN),
            "sha256": sha256_of(SERVING_PIN),
            "why": (
                "(11)(b): the instrument is FROZEN as registered. The resumed session serves under"
                " the same pin the 17 answers were bought under — pinned in this record so a"
                " re-created endpoint under a different configuration cannot pass the identity stop"
                " and still be reported against these bars"
            ),
        },
        "bought_under": {"path": rel(BOUGHT_UNDER), "sha256": sha256_of(BOUGHT_UNDER)},
        "asked": sorted(asked),
        "n_asked": len(asked),
        "unbought": sorted(unbought),
        "n_unbought": len(unbought),
        "unreadable": run["extraction"]["unreadable"],
        "unreadable_reading": (
            "(11)(a): the parse refusal enters bar 3's accounting AS IT STANDS. It is an answer the"
            " session paid for, it is excluded by its reason and counted — not re-asked, and not"
            " turned into an empty page by a resume that found it inconvenient"
        ),
    }


def refused_nothing_bought() -> dict:
    """SPEC 3.17 (12): the v3 session's record, pinned — and READ, because the pin is not the claim.

    v4 inherits v3's population without re-deriving it, and that inheritance rests on one fact: the
    refused session bought nothing. A sha alone proves the file has not moved since; it says nothing
    about what is inside it. So the two fields that carry the claim are checked here, and a v3 record
    that reached the gold would stop this write instead of being registered around.
    """
    record = json.loads(REFUSED.read_text(encoding="utf-8"))
    asked = record["population"]["asked"]
    if not record.get("stopped_before_gold") or asked:
        raise SystemExit(
            f"{rel(REFUSED)} says stopped_before_gold={record.get('stopped_before_gold')!r} with"
            f" {asked} source(s) asked. (12) registers v4 over the population v3 left untouched; a"
            " v3 session that bought something means elements this record does not know about have"
            " answers, and the v4 run would buy them twice. Stop and report."
        )
    return {
        "path": rel(REFUSED),
        "sha256": sha256_of(REFUSED),
        "stopped_before_gold": True,
        "asked": asked,
        "cost_usd": record["cost"]["usd"],
        "why": (
            "the (10)(a) refusal, pinned as EVIDENCE rather than quoted as a story. It is what makes"
            " v4's population still 121: the session was refused before the first gold call, so no"
            " element of the 138 changed hands and resume.bought_already is still the FIRST"
            " session's 17. Both halves of that are checked when this record is written and again"
            " before the v4 run — the bytes against this sha, and stopped_before_gold/asked against"
            " what they say. Its $0.1416 is the phase's overhead under (12)(b) and is charged to"
            " results/spend_sku_b_v3.json, never to this attempt's cap"
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=RECORD)
    args = parser.parse_args(argv)
    check_the_bars_are_the_laws(SPEC)

    reference = json.loads(REFERENCE.read_text(encoding="utf-8"))
    census = json.loads(CENSUS.read_text(encoding="utf-8"))
    pack = json.loads(PACK_MANIFEST.read_text(encoding="utf-8"))
    scoreable = reference["gold"]["posts_with_a_non_empty_gold_set"]
    empty = reference["gold"]["posts_with_an_empty_gold_set"]
    warmup = resume_warmup(reference, pack)
    already = bought_already()
    refused = refused_nothing_bought()

    record = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "phase": "sku-b — the position-layer pilot, resumed on a fresh ledger",
        "written_by": "sku-b-v4-prep (executor, $0), docs/PROMPT-sku-b-v4-prep.md deliverable 1",
        "authority": "docs/SPEC.md amendment 3.17 (6), (10)(b), (11), (12)",
        "class": (
            "PRE-REGISTRATION. Committed in its own commit before any artifact of the v4 session"
            " exists in the repo; git history is the only witness to that ordering. THREE sku-b run"
            " artifacts do exist and all three are pinned here — the first session's record and dump"
            " in resume.bought_already, and the refused v3 session's record in"
            " supersedes.refused_record. Nothing here is a result"
        ),
        "supersedes": {
            "record": rel(SUPERSEDED),
            "sha256": sha256_of(SUPERSEDED),
            "reason": SUPERSEDES_REASON,
            "authority": "docs/SPEC.md amendment 3.17 (12), ratified at the sku-b-v3-run acceptance",
            "verbatim": V4_HEADLINE,
            "readings": {key: V4_READINGS[key] for key in ("a", "b", "c", "d")},
            "refused_record": refused,
            "unchanged": (
                "every bar's verbatim text and threshold, the direction, both reachability rules,"
                " attempts.verbatim/.count/.on_failure/.on_success, all five R1–R5 readings, both"
                " instrument shas, the ladder, every pinned input and the WHOLE resume block —"
                " population, the (11)(c) warm-up pins and bought_already's 17 of 138 — are"
                " BYTE-EQUAL to v3, asserted leaf by leaf in tests/test_sku_prereg.py, not claimed"
            ),
            "moved": [
                "attempts.cap_usd (0.45 → 0.65, SPEC 3.17 (12)(a): sized to admit the gate's own"
                " pessimistic projection of ~$0.60, whose probe is structurally a deep leaflet page"
                " and prices above the first-six-page population's drawn marginal of 5.0772 s)",
                "attempts.phase and attempts.ledger (new: sku-b-v4 and results/spend_sku_b_v4.json,"
                " SPEC 3.17 (12)(b) — the cap, the ledger and the phase are ONE decision and are"
                " registered together, which is what Dv167 found missing; attempts.authority is new"
                " beside them and names which reading each comes from, because the clause the cap"
                " sits under is still (11)'s)",
                "supersedes (this record names v3 as its parent, transcribes (12)(a)–(d) and pins"
                " the (10)(a) refusal record results/sku_b_positions_v3.json — whose"
                " stopped_before_gold is what proves the population did not move)",
            ],
            "moved_metadata": [
                "phase, written_by, authority, class — this record's own description of itself,"
                " which cannot stay v3's without lying: v3 was written before a session that was"
                " then refused, and this one is written after that refusal",
                "generated_at, git — stamped by the producer on every build",
            ],
        },
        "attempts": {
            "verbatim": RESUME_CLAUSE,
            "count": 1,
            "cap_usd": RESUME_CAP_USD,
            "phase": RESUME_PHASE,
            "ledger": rel(RESUME_LEDGER),
            "authority": (
                "the clause above is SPEC 3.17 (11)'s and is unchanged, so its parenthetical still"
                " names the registration v3 WAS — it is quoted as registered, not edited to point at"
                " this file. What authorises this attempt is 3.17 (12): (12)(a) for the $0.65 cap,"
                " which supersedes (11)(d)'s $0.45 without overwriting it in resume.readings, and"
                " (12)(b) for the phase and ledger names beside it. Both are transcribed verbatim in"
                " supersedes.readings"
            ),
            "on_failure": (
                "a failed bar closes B as 'instrument not ready' BY MEASUREMENT. No retry, no"
                " re-prompt, no second draw: a bar re-run after its own result is not the bar that"
                " was registered"
            ),
            "on_success": GREEN_GATE,
        },
        "bars": {
            "leaflet_brand_recall": {
                "verbatim": BARS["leaflet_brand_recall"],
                "threshold": 0.75,
                "direction": ">=",
                "gold": {
                    "path": rel(REFERENCE),
                    "sha256": sha256_of(REFERENCE),
                    "pairs": reference["gold"]["pairs"],
                    "key": reference["gold"]["definition"],
                },
                "extraction_unit": (
                    "one PAGE, one call, under the registered prompt positions_post_gm4 (SPEC"
                    " 3.17 (4)). The page set is EXACTLY the 108 pages the reference names as sent —"
                    " not the 159 available. A brand printed on an unsent page is not in the gold,"
                    " so reading one would be scored as a false positive for being right"
                ),
                "denominator": (
                    "the 15 posts whose gold brand set is non-empty. Recall is computed PER POST as"
                    " |extracted ∩ gold| / |gold|, over the union of that post's page answers, and"
                    " the bar reads the MACRO MEAN of those 15 values. The micro reading over all 55"
                    " pairs is reported beside it and gates nothing"
                ),
                "why_not_per_page": (
                    "the bar says 'per page' and the gold cannot be split that way: one Opus"
                    " reviewer judged the whole sent set of a post and named what was visible across"
                    " it, so no artifact in this repo attributes a brand to a page. Building"
                    " per-page gold would be a new adjudication and is not in this contract. THIS IS"
                    " THE EXECUTOR'S READING — see ratification_required"
                ),
                "excluded": {
                    "posts": empty,
                    "why": (
                        "an empty gold set makes recall undefined, and an absolute bar over it fails"
                        " by arithmetic rather than by measurement"
                    ),
                    "instead": (
                        "they are a PRECISION probe: every brand extracted on their pages is a false"
                        " positive and is reported with its page. Their reviewer notes say what is"
                        " actually on them (summer non-food and similar)"
                    ),
                },
                "reported_never_gated": (
                    "precision on the 15 scoreable posts. The gold is ONE reviewer's reading in the"
                    " REVIEW class of SPEC 3.16 (1), so a brand the pilot finds and the reviewer did"
                    " not is not evidence of a false positive — SPEC gates recall only, and this"
                    " pre-registration does not widen it"
                ),
                "reachable": (
                    f"yes, measured before the run: {scoreable} of 19 posts carry a non-empty"
                    " gold set and 55 pairs sit on them"
                ),
            },
            "price_pair_accuracy": {
                "verbatim": BARS["price_pair_accuracy"],
                "threshold": 0.80,
                "direction": ">=",
                "denominator": (
                    "extracted positions carrying a crossed-out price — `price_old is not None` on a"
                    " position whose carrier is leaflet_page. Discovered BY THE RUN: nothing before"
                    " it can say how many of the 108 pages print an old price"
                ),
                "numerator": (
                    "positions whose (price_promo, price_old) pair the team lead marks correct"
                    " against the page image at acceptance. Both numbers, as one verdict: a right"
                    " promo beside a wrong old price is a wrong pair, because depth is computed from"
                    " the two of them"
                ),
                "procedure": (
                    "sku-b writes a per-position dump — one row per extracted position carrying"
                    " item, page number, the page's file and sha256, brand_raw, brand_id, line,"
                    " category, size, fat, price_promo, price_old, discount_pct_printed,"
                    " price_qualifier, the code-assigned tier, depth() and"
                    " depth_disagrees_with_printed(). The team lead opens each cited page image and"
                    " marks the pair correct or incorrect. The executor never scores its own sample"
                    " (SPEC §10), and the dump is what makes the read possible without re-running"
                    " anything"
                ),
                "reachability": {
                    "rule": (
                        "n >= 10 pairs: the bar is SCORED. 1 <= n < 10: the accuracy is REPORTED"
                        " with its n and the bar is NOT_SCORED — neither a PASS nor a closure of B,"
                        " and the team lead rules at acceptance whether the small-n reading stands."
                        " n = 0: NOT_REACHABLE, and the finding is that the pages carry no"
                        " crossed-out prices at all"
                    ),
                    "why": (
                        "at a 0.80 bar one error costs 10 pp at n=10 and 33 pp at n=3, so a small"
                        " denominator makes the threshold an artefact of arithmetic. Fixed here"
                        " rather than after the run, when the n is known and the temptation is"
                        " obvious. THIS IS THE EXECUTOR'S THRESHOLD — see ratification_required"
                    ),
                },
                "printed_percentage": (
                    "never substitutes the pair (SPEC 3.17 (3)). A position with a printed % and one"
                    " price is not in this denominator, and depth() returns None there"
                ),
            },
            "text_tier_accuracy": {
                "verbatim": BARS["text_tier_accuracy"],
                "threshold": 0.85,
                "direction": ">=",
                "gold": {
                    "pack": pack["pack"],
                    "manifest": rel(PACK_MANIFEST),
                    "manifest_sha256": sha256_of(PACK_MANIFEST),
                    "rows": pack["rows"],
                    "by_carrier": pack["draw"]["by_carrier"],
                    "computed_by": pack["ladder"]["function"],
                    "ladder_sha256": pack["ladder"]["sha256"],
                },
                "denominator": (
                    "the adjudicated rows that came back with a legal tick set. A row the operator"
                    " left untouched is not gold and is not counted"
                ),
                "comparison": (
                    "per ROW, the gold tier against the model's tier, both from the SAME function:"
                    " positions.tier_from_presence for the ticks, positions.tier for each parsed"
                    " position. A row naming several products is compared on its HIGHEST rung, and a"
                    " row whose ticks are all empty has gold `none` — the model must return [] to"
                    " agree with it"
                ),
                "unreadable_rows": (
                    "a reply the strict parser refuses is NOT scored as `none`. It is counted by its"
                    " reason, listed by id, and excluded from the denominator: an unreadable reply"
                    " and an empty answer are different outcomes, and conflating them would report"
                    " parse failures as rows with nothing in them. If unreadable rows exceed 10% of"
                    " the adjudicated set the bar is NOT_SCORED — the instrument did not answer"
                ),
                "reachability": {
                    "rule": (
                        "n >= 20 adjudicated rows: SCORED. Below that, REPORTED with its n and"
                        " NOT_SCORED"
                    ),
                    "why": "30 are drawn; a bar at 0.85 over fewer than 20 rows moves 5 pp per row",
                },
                "carrier": (
                    f"pooled over both carriers as drawn: {pack['draw']['by_carrier']}. Comments are"
                    f" {census['frame']['by_carrier']['comment']['passed']} of the frame's"
                    f" {census['frame']['rows']} rows, so this bar prices the POST leg. Whether the"
                    " comment carrier needs a bar of its own is a team-lead ruling — see"
                    " ratification_required"
                ),
                "also_measures": (
                    "the pre-filter's precision. A drawn row adjudicated as naming no position is a"
                    " pre-filter false positive; the frame is dominated by recipe feeds"
                    " (results/sku_prefilter_census.json), and this sample is the only thing that"
                    " prices it. Reported, not gated — SPEC does not put a bar on the filter"
                ),
            },
        },
        "ratification_required": [
            {
                "id": "R1",
                "bar": "leaflet_brand_recall",
                "question": (
                    "the bar says 'per page' and the gold is per POST. Registered reading: recall"
                    " per post over the union of its page answers, macro-averaged over the 15"
                    " posts with a non-empty gold set"
                ),
                "if_refused": (
                    "per-page gold does not exist and building it is a new adjudication. sku-b must"
                    " NOT run until this line is ratified: one attempt against a denominator nobody"
                    " agreed to is the paid session wasted"
                ),
            },
            {
                "id": "R2",
                "bar": "leaflet_brand_recall",
                "question": (
                    "the page set is the 108 pages the caption run SENT, not the 159 available. For"
                    " 15 of 19 posts that is the first six pages of a longer leaflet"
                ),
                "if_refused": (
                    "reading all 159 pages means brands with no gold behind them, which would score"
                    " as false positives for being correct"
                ),
            },
            {
                "id": "R3",
                "bar": "leaflet_brand_recall",
                "question": f"the 4 posts with an empty gold set are out of the recall average: {empty}",
                "if_refused": "recall is undefined there; the alternative is a bar that fails by arithmetic",
            },
            {
                "id": "R4",
                "bar": "price_pair_accuracy",
                "question": "n >= 10 pairs to score the bar; 1..9 reports and does not score; 0 is NOT_REACHABLE",
                "if_refused": "the team lead sets another n, in writing, before the run",
            },
            {
                "id": "R5",
                "bar": "text_tier_accuracy",
                "question": (
                    "unreadable replies are excluded and counted (>10% blocks the bar); n >= 20"
                    " adjudicated rows to score; both carriers pooled as drawn"
                ),
                "if_refused": "a stratified redraw is a different pack and this one is already built",
            },
        ],
        "resume": {
            "verbatim": RESUME_CLAUSE,
            "authority": "docs/SPEC.md amendment 3.17 (11), ratified at the sku-b-run acceptance",
            "readings": {key: RESUME_READINGS[key] for key in ("a", "b", "c", "d", "e")},
            "bars_unchanged": BARS_UNCHANGED,
            "supersedes_clause": {
                "verbatim": ONE_ATTEMPT,
                "why": (
                    "SPEC 3.17 (6)'s clause is what the first session was bought under and it is"
                    " not deleted by (11): the 17 answers it paid for stand, and this record quotes"
                    " it so a reader can see which clause each half of the population came from"
                ),
            },
            "population": {
                "registered": 138,
                "already_bought": 17,
                "to_buy": 121,
                "why": (
                    "the resumed session's population is exactly resume.bought_already.unbought."
                    " Bar 1's denominator is still R2's 108 sent pages and bar 3's is still the 30"
                    " adjudicated rows — the resume completes the population, it does not redefine"
                    " it"
                ),
            },
            "warmup": warmup,
            "bought_already": already,
            "instrument_frozen": {
                "verbatim": RESUME_READINGS["b"],
                "prompts": "the two shas in `instruments` below, byte-equal to v2",
                "serving_pin": "resume.bought_already.serving_pin, byte-equal to what the run served",
                "named_revision": (
                    "the superscript kopeck and the asterisk qualifier the team lead's calibration"
                    " read found are a POST-pilot revision registered beside these prompts, never an"
                    " edit inside the measurement. A prompt revised mid-pilot makes the 17 bought"
                    " answers and the 121 resumed ones two different instruments"
                ),
            },
            "calibration_read_is_not_a_bar": {
                "verbatim": RESUME_READINGS["e"],
                "why": (
                    "6 of 13 pairs is a READ of a 17-page prefix, and bar 2 is registered over the"
                    " completed population. Recorded because it is the strongest available signal"
                    " about what the resumed session will measure, and gating nothing because a"
                    " prefix is not the sample the bar was registered on"
                ),
            },
        },
        "instruments": {
            "positions_post_gm4": prompts.prompt_sha256("positions_post_gm4"),
            "positions_text_gm4": prompts.prompt_sha256("positions_text_gm4"),
            "note": (
                "the two registered prompts of SPEC 3.17 (5), pinned here so the pilot cannot be"
                " run under a revised text and reported against these bars. A revision is a new"
                " registration beside them, never an edit"
            ),
        },
        "pinned_inputs": {
            rel(path): pinned_sha256(path)
            for path in (SPEC, REFERENCE, PACK_MANIFEST, CENSUS, REGISTRY, LEXICON)
        },
        "ladder": {
            "sha256": positions.ladder_sha256(),
            "table": positions.ladder_table(),
            "why": (
                "bar 3's gold is computed from the operator's ticks by this ladder and the model's"
                " tier by the same function, so the ladder is an INPUT to the bar. Pinned as its"
                " whole 32-row table, not only as a hash, so a future reader can see what was"
                " registered without running this code"
            ),
        },
        "not_in_scope": {
            "the 5c3 rulings": (
                "«Варто» text-matching OFF and «Селянське» anchored-only are the 5c3 named revision"
                " (knowledge/decisions/sitting-2026-08-10-composition-signed.md) and are NOT applied"
                " to brand resolution here. A «Варто» the model reads off a page resolves like any"
                " other name, and the leaflet gold contains it because the reviewer saw it printed"
            ),
            "the 141 names": (
                "still outside the watchlist, so they resolve to `raw:` keys on both sides of bar 1."
                " That is symmetric and does not move the recall"
            ),
            "the frozen family": "T1v2, the frozen sets, results/baselines.json and the adapter are untouched",
            "aggregates": (
                "no promo aggregate is computed anywhere in sku-b. Question 7's brand x category x"
                " week rollup is 5c2's, and consumer quotes never enter it (SPEC 3.17 (4))"
            ),
        },
        "git": git_state(args.out),
    }
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"wrote {rel(args.out)}")
    for name, bar in record["bars"].items():
        print(f"  {name:<22} {bar['direction']} {bar['threshold']}  ({bar['verbatim'][:52]}…)")
    print(
        f"  {len(record['ratification_required'])} line(s) need a team-lead word before sku-b runs"
    )
    print(
        f"  ladder {positions.ladder_sha256()[:16]}… · prompts {record['instruments']['positions_post_gm4'][:8]}…/"
        f"{record['instruments']['positions_text_gm4'][:8]}…"
    )
    resume = record["resume"]
    print(
        f"  resume        {resume['population']['already_bought']} bought,"
        f" {resume['population']['to_buy']} to buy of {resume['population']['registered']}"
        f"\n  attempt       cap ${record['attempts']['cap_usd']:.2f} ·"
        f" phase {record['attempts']['phase']} · ledger {record['attempts']['ledger']}"
        f"\n  warm-up page  {warmup['page']['file']} ({warmup['page']['bytes'] / 1e6:.2f} MB,"
        f" 1 of {warmup['page']['population']} never sent)"
        f"\n  warm-up row   {warmup['text']['id']} {warmup['text']['carrier']}"
        f" ({warmup['text']['text_chars']} chars, 1 of {warmup['text']['population']} outside the pack)"
        f"\n  supersedes    {rel(SUPERSEDED)} {record['supersedes']['sha256'][:16]}…"
        f"\n  refused       {refused['path']} {refused['sha256'][:16]}…"
        f" (stopped_before_gold, {refused['asked']} asked, ${refused['cost_usd']:.4f} to the phase)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
