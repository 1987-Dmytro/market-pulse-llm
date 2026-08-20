#!/usr/bin/env python3
"""`results/prereg_pass1_probe_b.json` — the same instrument, one boot constant, a second attempt.

**The instrument does not move, and that is CHECKED rather than claimed.** This producer CALLS
`write_pass1_prereg.build()` (the v5b idiom, a generation later) and refuses unless it rebuilds
pass1-probe's own frozen record byte for byte FIRST. Everything bar P1 is scored on — the
`pass1_comment_gm4_v1` text and its sha, the parser, the four subject types, gold r2, the 64-unit
population and its per-item rendering shas, the bar and its loss budget, the census rules, the
one-attempt class and the return-to-sitting clause — is therefore object-equal to the frozen record
BY CONSTRUCTION, and :data:`MOVED` is the whole diff, asserted both ways.

**What moves is ONE constant, in two cells.** The registration charged a 192.1 s boot because that
was the only boot this stack had measured. pass1-probe measured a second one — [267, 293] s on the
same card, the same volume and the same weights — and the boot ceiling, not the cap, is what came
within 0.6–26.6 s of killing that run before its own `KeyError` did. The operator's ruling of
2026-08-17 (late evening): charge the MAXIMUM of the two measurements, 300 s, and lift the ceiling
to 420 s. The cap does not move and no bar does.

**Two transport defects the paid attempt found are closed here rather than described.**

* `money.arithmetic.boot_deadline_rule` is ADDED. `read_threads_reader_v4.deadlines` reads that key
  by name; the pass1-probe record spelled it `boot_kill_rule` and `--deadlines` raised `KeyError`
  with the meter running, on a record that could no longer be edited. A registered field no shipped
  command can read is a red gate at $0 here ([[a_frozen_record_is_an_input_to_shipped_code]]).
* `money.arithmetic.worst_case` is ADDED, with its arithmetic spelled out, because the contract's
  own worst-case figure does not reproduce and a number nobody can re-derive is a number that gets
  re-decided.

    PYTHONPATH=src python3.11 scripts/write_pass1_prereg_b.py
    PYTHONPATH=src python3.11 scripts/write_pass1_prereg_b.py --out /tmp/again.json   # the pair
"""

import argparse
import json
import sys
from contextlib import contextmanager
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import window_summary_5c2 as summary  # noqa: E402
import write_pass1_prereg as p1  # noqa: E402

OUT = REPO_ROOT / "results" / "prereg_pass1_probe_b.json"
PACK_PATH = REPO_ROOT / "results" / "pass1_probe_b_pack.json"
CONTRACT = REPO_ROOT / "docs" / "PROMPT-pass1-probe-b.md"
SUPERSEDES = REPO_ROOT / "results" / "prereg_pass1_probe.json"
SUPERSEDED_PACK = REPO_ROOT / "results" / "pass1_probe_pack.json"
P1_RUN = REPO_ROOT / "results" / "pass1_probe_run.json"
P1_REPORT = REPO_ROOT / "docs" / "reports" / "pass1-probe.md"

PHASE = "pass1-probe-b"

BOOT_CHARGED_S = 300.0
"""The MAXIMUM of the two boots this stack has measured, not the minimum and not a mean.

v5b: 192.13 s, read off its own evidence. pass1-probe: [267, 293] s, a BOUND rather than a reading —
the only witness to the crash moment is the watcher's ALIVE/DEAD pair and the pod is gone. 300 s is
above both and it is charged in full against the cap, so the projection cannot be optimistic about
provisioning the way the first registration was."""

BOOT_KILL_S = 420.0
"""The ceiling the first reply must land inside, measured from the GENERATION process starting.

At 300 s it sat 0.6–26.6 s above the observed load and it was the binding leg of the gate — the
money was never the constraint. 420 s clears the worst boot observed by 127 s. It also hands the
binding leg BACK to affordability whenever staging takes longer than
`pre_generation_budget_seconds` (83.2 s); pass1-probe's staging took 92 s, so on the evidence this
run's binding deadline is the money again, at 503.2 s of create-elapsed."""


SHIPPED_MEASURED_RATE = p1.measured_rate
"""Captured at IMPORT, before any swap, so the wrapper below cannot recurse into itself."""


def measured_rate() -> dict:
    """pass1-probe's own reading with the boot block replaced by the two-measurement one.

    Only `boot` moves. The per-call ceiling — v5b's cheapest observed call, 6.402 s — is what bar
    P1's affordability is solved against and it is not this contract's to touch.
    """
    reading = SHIPPED_MEASURED_RATE()
    v5b_boot = float(reading["boot"]["seconds"])
    return reading | {
        "boot": {
            "seconds": BOOT_CHARGED_S,
            "rule": (
                "the MAXIMUM of the two boots this stack has measured, charged in full. A boot"
                " charged from one measurement is a constant assumed from a sample of one, and the"
                " sample of two spreads 1.4x-1.5x"
            ),
            "measurements": [
                {
                    "run": "reader-v5b",
                    "record": summary.rel(p1.V5B_EVIDENCE),
                    "seconds": v5b_boot,
                    "kind": "READING — the pod answered and its own row carries boot_seconds",
                },
                {
                    "run": "pass1-probe",
                    "record": summary.rel(P1_RUN),
                    "seconds_bound": [267, 293],
                    "kind": (
                        "BOUND — the runner crashed after the weights loaded and the only witness"
                        " to the moment is the watcher's ALIVE 18:47:23Z / DEAD 18:47:49Z pair,"
                        " less the 92 s of create-elapsed at which the generation process launched"
                    ),
                },
            ],
            "charged": BOOT_CHARGED_S,
            "why_the_max": (
                "the same card, the same network volume and the same weights loaded in 192.1 s once"
                " and in 267-293 s the next night. Nothing in either run explains the spread, so it"
                " is treated as variance of the boot and the pessimistic end is the one registered"
            ),
        }
    }


@contextmanager
def as_probe_b():
    """pass1-probe's producer, pointed at this contract's constants for the length of one call.

    `scripts/write_pass1_prereg.py` hashes ITSELF into the record it wrote (`producer.sha256`) and
    that record is frozen, so it cannot grow the parameters this contract would like it to have.
    Swapping its module globals around the call is the one way to reuse the arithmetic instead of
    writing a second spelling of a cap computation ([[a_sealed_caller_forces_the_default]]).

    Every name is asserted to EXIST before it is replaced: a rename in the shipped producer must be
    a loud failure here, never a silent second implementation.
    """
    ours = {
        "PHASE": PHASE,
        "BOOT_KILL_S": BOOT_KILL_S,
        "OUT": OUT,
        "PACK_PATH": PACK_PATH,
        "measured_rate": measured_rate,
    }
    keep = {}
    for name in ours:
        if not hasattr(p1, name):
            raise SystemExit(
                f"scripts/write_pass1_prereg.py has no `{name}` any more, so this producer is"
                " replacing something that no longer exists and the b-record would silently carry"
                " pass1-probe's own constant. Stop and report."
            )
        keep[name] = getattr(p1, name)
    for name, value in ours.items():
        setattr(p1, name, value)
    try:
        yield
    finally:
        for name, value in keep.items():
            setattr(p1, name, value)


# --- the diff, enumerated ---------------------------------------------------------------------------

OPAQUE = ("money.arithmetic.full_pass_over_the_registered_order",)
"""Subtrees compared as ONE path.

The gate table carries 64 rows and every headroom and margin in it moves by construction when the
boot charge does — enumerating 128 leaves would bury the discrimination rather than provide it. What
the table must NOT do is reorder or re-verdict, and that is checked separately and directly by
:func:`the_registered_order_is_unmoved`."""

MOVED = (
    "authority.docs/reports/pass1-probe.md",
    "authority.results/pass1_probe_pack.json",
    "authority.results/pass1_probe_run.json",
    "authority.results/prereg_pass1_probe.json",
    "contract.docs/PROMPT-pass1-probe-b.md",
    "frozen_when_the_pod_exists",
    "go_no_go.gates.2_boot_kill.boot_kill_seconds",
    "money.arithmetic.boot_deadline_rule",
    "money.arithmetic.boot_kill_rule",
    "money.arithmetic.boot_kill_seconds",
    "money.arithmetic.boot_seconds_charged",
    "money.arithmetic.full_pass_over_the_registered_order",
    "money.arithmetic.pre_generation_budget_seconds",
    "money.arithmetic.which_leg_binds",
    "money.arithmetic.worst_case",
    "money.guard",
    "money.reading.boot.charged",
    "money.reading.boot.measurements",
    "money.reading.boot.rule",
    "money.reading.boot.seconds",
    "money.reading.boot.why_the_max",
    "phase",
    "producer.calls",
    "producer.script",
    "producer.sha256",
    "supersedes",
    "transport.boot_kill_seconds",
    "transport.pod_log",
)
"""Every path of the frozen record this contract may move, and the whole of it.

Asserted in BOTH directions: a path that moved and is not here is an instrument change wearing a
transport contract's clothes, and a path here that did NOT move is an enumeration that has gone
stale and stopped discriminating ([[a_law_that_grows_loudly]])."""

PACK_MOVED = ("phase", "registration.record")
"""The pack's whole diff. `items` — the 64 units, their order, their texts and their rendering
shas — is what P1 is measured on and it does not appear here."""


def moved_paths(older: dict, newer: dict, opaque: tuple[str, ...] = OPAQUE) -> list[str]:
    """Dotted paths of every leaf that differs, with `opaque` subtrees reported as one path."""
    found: list[str] = []

    def walk(left, right, prefix: list[str]) -> None:
        path = ".".join(prefix)
        if path in opaque:
            if left != right:
                found.append(path)
            return
        if isinstance(left, dict) and isinstance(right, dict):
            for key in sorted(set(left) | set(right)):
                if key not in left or key not in right:
                    found.append(".".join([*prefix, key]))
                else:
                    walk(left[key], right[key], [*prefix, key])
            return
        if left != right:
            found.append(path)

    walk(older, newer, [])
    return sorted(found)


def module_pin_paths(record: dict) -> set[str]:
    """Every path of `record` that carries `src/market_pulse/prompts.py`'s LIVE sha.

    The one class of move this producer's self-check may forgive, and it is derived rather than
    listed: `docs/PROMPT-pass1-fewshot.md` D0.2 registered a second pass-1 TEXT in that module and
    ruled old records' pins of it «moved since», never re-pinned. A module sha moves whenever any
    sibling text is added; the registered `prompt_sha256` map is what says whether the INSTRUMENT
    moved, and the caller checks that separately and refuses on it
    ([[the_identity_field_stops_covering_the_change]]).
    """
    live = summary.sha256_of(REPO_ROOT / "src" / "market_pulse" / "prompts.py")

    def walk(node, prefix: list[str]):
        if isinstance(node, dict):
            for key, value in node.items():
                yield from walk(value, [*prefix, str(key)])
        elif isinstance(node, list):
            for index, value in enumerate(node):
                yield from walk(value, [*prefix, str(index)])
        elif node == live:
            yield ".".join(prefix)

    return set(walk(record, []))


def the_registered_order_is_unmoved(older: dict, newer: dict) -> list[str]:
    """What the opaque gate-table range costs, closed — or the gaps.

    Allowing the subtree wholesale would go blind to exactly the change that would matter: a unit
    reordered, a verdict flipped, or a STOP appearing where there was none. Each of those is
    compared here directly, and the frozen table is the authority
    ([[a_hash_is_not_the_claim_it_carries]]).
    """
    gaps = []
    was = older["money"]["arithmetic"]["full_pass_over_the_registered_order"]
    now = newer["money"]["arithmetic"]["full_pass_over_the_registered_order"]
    if [one["unit"] for one in was["per_unit"]] != [one["unit"] for one in now["per_unit"]]:
        gaps.append("the pack's order through the gate moved")
    if [one["verdict"] for one in was["per_unit"]] != [one["verdict"] for one in now["per_unit"]]:
        gaps.append("a unit's gate verdict changed")
    for key in ("first_stop_after_units", "per_call_seconds", "unit_one_without_any_boot"):
        if was[key] != now[key]:
            gaps.append(f"{key}: {was[key]!r} -> {now[key]!r}")
    return gaps


def worst_case(arithmetic: dict) -> dict:
    """The most this attempt can bill while still inside every deadline it registers.

    Published with its arithmetic because the contract's own figure does not reproduce: $0.175 is
    `(usable_seconds - delete_margin) x rate`, which subtracts the 60 s margin a second time after
    `usable_seconds` already took it off. Named rather than quietly corrected — and the difference
    decides nothing, because every construction of the worst case is inside the $0.20 cap.
    """
    rate = p1.CARD_USD_PER_HOUR_EXAMPLE / 3600.0
    reading = float(arithmetic["reading_projection_seconds"])
    margin = float(arithmetic["delete_margin_seconds"])
    seconds = BOOT_KILL_S + reading + margin
    contract_seconds = float(arithmetic["usable_seconds"]) - margin
    return {
        "rule": (
            "the boot ceiling burned in full, then all 64 units at the registered per-call bound,"
            " then the delete margin. Nothing above it is reachable without a gate firing first"
        ),
        "boot_kill_seconds": BOOT_KILL_S,
        "reading_projection_seconds": reading,
        "delete_margin_seconds": margin,
        "seconds": round(seconds, 3),
        "usd_at_the_worked_example": round(seconds * rate, 6),
        "cap_usd_all_in": p1.CAP_USD,
        "fits_the_cap": seconds * rate <= p1.CAP_USD,
        "the_contracts_figure": {
            "stated_usd": 0.175,
            "reproduces_as": "(usable_seconds - delete_margin_seconds) x usd_per_second",
            "seconds": round(contract_seconds, 3),
            "usd": round(contract_seconds * rate, 6),
            "why_it_is_not_registered": (
                "`usable_seconds` is already the cap's seconds LESS the delete margin, so that"
                " construction charges the margin twice and lands below the reachable worst case."
                " Both are inside the cap, so nothing about go/no-go turns on which one is right"
            ),
        },
    }


def build() -> tuple[dict, dict]:
    unchanged = p1.build()
    frozen = json.loads(summary.read_text_or_refuse(SUPERSEDES))
    if unchanged != frozen:
        moved = moved_paths(frozen, unchanged, opaque=())
        allowed = module_pin_paths(unchanged)
        if (
            set(moved) - allowed
            or frozen["instruments"]["prompt_sha256"] != (unchanged["instruments"]["prompt_sha256"])
        ):
            raise SystemExit(
                f"{summary.rel(SUPERSEDES)} no longer rebuilds from its own producer —"
                f" {sorted(set(moved) - allowed)} differ beyond the module pins. pass1-probe-b"
                " registers the SAME instrument, so a moved path here means the instrument moved"
                " and the two attempts would not be comparable. Stop and report."
            )

    with as_probe_b():
        rebuilt = p1.build()
        pack = p1.build_pack(rebuilt)

    arithmetic = rebuilt["money"]["arithmetic"]
    record = rebuilt | {
        "contract": {
            summary.rel(CONTRACT): summary.sha256_of(CONTRACT),
            summary.rel(p1.CONTRACT): summary.sha256_of(p1.CONTRACT),
        },
        "authority": frozen["authority"]
        | {
            summary.rel(path): summary.sha256_of(path)
            for path in (P1_RUN, P1_REPORT, SUPERSEDES, SUPERSEDED_PACK)
        },
        "supersedes": {
            "record": summary.rel(SUPERSEDES),
            "sha256": summary.sha256_of(SUPERSEDES),
            "state": (
                "pass1-probe stays FROZEN and is not withdrawn. Bar P1 is UNSCORED: the pod it"
                " registered was billed 427.0 s, loaded the weights and read nothing, because the"
                " runner's swapped render did not answer the READER probe"
                " `local_llm.ReaderClient.__init__` makes. The instrument it registered was never"
                " exercised, which is why this registration re-registers it rather than revising it"
            ),
            "ruling": "the operator, 2026-08-17 late evening, on the pass1-probe report",
            "run_record": {
                "record": summary.rel(P1_RUN),
                "sha256": summary.sha256_of(P1_RUN),
                "reading": (
                    "two appended gate snapshots — an `open` WAIT at 5.6 s and a `gate0` GO at"
                    " 23.4 s against a 180 s dead-man — and one segment: 427.0 billed seconds,"
                    " $0.087772, zero replies"
                ),
            },
            "what_it_changes": [
                f"the boot CHARGE: {float(frozen['money']['arithmetic']['boot_seconds_charged'])}"
                f" -> {BOOT_CHARGED_S} s, the max of the stack's two measurements",
                f"the boot CEILING `BOOT_KILL_S`: "
                f"{float(frozen['money']['arithmetic']['boot_kill_seconds'])} -> {BOOT_KILL_S} s",
                "`money.arithmetic.boot_deadline_rule`, ADDED — the key"
                " `read_threads_reader_v4.deadlines` reads by name, absent from the frozen record,"
                " which is why `--deadlines` raised KeyError on a live pod",
                "`money.arithmetic.worst_case`, ADDED — the reachable worst case with its"
                " arithmetic, so the figure cannot be re-decided later",
                "`transport.pod_log`, ADDED — the pod's log travels beside the jsonl before every"
                " gate. pass1-probe's only traceback survived as a screen read",
                "the gate table, RE-SOLVED at the new boot charge. Same order, same 64 verdicts,"
                " still no STOP; the tightest margin falls 4.938 -> 3.226 s/unit",
                "nothing else. The cap, the bar, the population, the prompt, the parser and the"
                " return-to-sitting clause are object-equal and checked both ways",
            ],
            "what_it_keeps": (
                "EVERYTHING bar P1 is scored on, object-equal and checked by rebuilding"
                " pass1-probe's own record from pass1-probe's own producer before one key of it is"
                " overridden: the `pass1_comment_gm4_v1` text and its sha, the renderer, the"
                " parser and its four subject types, gold r2, the 64-unit population and its"
                " per-item rendering shas, bar P1 >=12/14 with its loss budget and bar 4's own"
                " comparison, the census rules, the serving configuration and the 256-token"
                " ceiling, the one-attempt class and the return-to-sitting clause"
            ),
        },
        "frozen_when_the_pod_exists": [
            summary.rel(OUT),
            summary.rel(PACK_PATH),
            *frozen["frozen_when_the_pod_exists"][2:],
        ],
        "transport": rebuilt["transport"]
        | {
            "pod_log": (
                "the on-pod log is scp'd back INSIDE the poll loop, beside the partial jsonl, before"
                " every gate. pass1-probe's only traceback was transcribed off a screen while the"
                " pod was still alive and died with it; an evidence artifact that exists only as a"
                " session read is an artifact the next contract cannot check"
            ),
        },
    }
    record["money"]["arithmetic"] = arithmetic | {
        "boot_kill_rule": (
            "the FIRST reply must land within this many seconds of the generation process starting,"
            " and within the affordability deadline measured from `pod create`. The binding one is"
            " whichever comes first on the create-elapsed axis. This stack's two measured boots are"
            f" {float(frozen['money']['arithmetic']['boot_seconds_charged'])} s and [267, 293] s,"
            f" so {BOOT_KILL_S:.0f} s clears the worse of them by 127 s and is a deadline rather"
            " than a forecast"
        ),
        "boot_deadline_rule": (
            f"min(boot_kill_seconds {BOOT_KILL_S:.0f} s measured from the generation process"
            " starting, usable_seconds - reading projection measured from `pod create`). Both"
            " numbers are printed at the gate and both land in the run record. The key exists"
            " because `read_threads_reader_v4.deadlines` reads it BY NAME and pass1-probe's record"
            " spelled it `boot_kill_rule`, which raised KeyError with the meter running"
        ),
        "which_leg_binds": (
            f"the boot ceiling binds only while the generation process starts within"
            f" {arithmetic['pre_generation_budget_seconds']} s of `pod create`; after that the"
            " affordability deadline at"
            f" {arithmetic['affordability_deadline_seconds']} s does. pass1-probe's staging took"
            " 92 s, so on the only evidence there is the MONEY binds this attempt and the boot"
            " ceiling does not"
        ),
        "worst_case": worst_case(arithmetic),
    }
    record["producer"] = {
        "script": summary.rel(Path(__file__)),
        "sha256": summary.sha256_of(Path(__file__)),
        "calls": {
            summary.rel(REPO_ROOT / "scripts" / "write_pass1_prereg.py"): summary.sha256_of(
                REPO_ROOT / "scripts" / "write_pass1_prereg.py"
            ),
            "rule": (
                "pass1-probe's producer is CALLED and its output is compared to pass1-probe's"
                " frozen record before one key of it is overridden. That check is what «the"
                " instrument does not move» means here — a claim in prose would be a claim; this is"
                " a refusal"
            ),
        },
        "borrowed": rebuilt["producer"]["borrowed"],
        "rule": rebuilt["producer"]["rule"],
    }

    if gaps := the_registered_order_is_unmoved(frozen, record):
        raise SystemExit(
            f"the gate table was re-solved at a boot charge of {BOOT_CHARGED_S} s and more than its"
            f" numbers moved — {gaps}. The pack's order and its verdicts are what the registration"
            " registered. Stop and report."
        )
    # the enumeration, PLUS the paths that pin `prompts.py` — derived from the record and never
    # listed. D0.2 of docs/PROMPT-pass1-fewshot.md registered a second pass-1 text in that module
    # and ruled its old pins «moved since»; the registered `prompt_sha256` map is what says whether
    # the INSTRUMENT moved, and it is compared whole two lines down
    allowed = set(MOVED) | module_pin_paths(record)
    if (found := moved_paths(frozen, record)) != sorted(allowed):
        raise SystemExit(
            "the diff against pass1-probe's frozen record is not the enumerated one."
            f" unexpected: {sorted(set(found) - allowed)} ·"
            f" enumerated but unmoved: {sorted(allowed - set(found))}. This contract may move a"
            " boot constant and its transport; anything else is an instrument change. Stop."
        )
    if frozen["instruments"]["prompt_sha256"] != record["instruments"]["prompt_sha256"]:
        raise SystemExit(
            "the registered pass-1 TEXT moved, and that is the one thing this contract may not do:"
            f" {frozen['instruments']['prompt_sha256']} → {record['instruments']['prompt_sha256']}."
            " The two attempts would not be comparable. Stop and report."
        )
    frozen_pack = json.loads(summary.read_text_or_refuse(SUPERSEDED_PACK))
    pack_allowed = set(PACK_MOVED) | module_pin_paths(pack)
    if (found := moved_paths(frozen_pack, pack, opaque=())) != sorted(pack_allowed):
        raise SystemExit(
            "the pack is not object-equal to pass1-probe's outside its registration pointer —"
            f" unexpected: {sorted(set(found) - pack_allowed)} ·"
            f" enumerated but unmoved: {sorted(pack_allowed - set(found))}. Stop."
        )
    if frozen_pack["instruments"]["prompt_sha256"] != pack["instruments"]["prompt_sha256"]:
        raise SystemExit("the pack's registered pass-1 TEXT moved — the units are not comparable.")
    return record, pack


def build_pack(record: dict) -> dict:
    """The b-pack, for the transport's `--pack` check: pass1-probe's builder under the same swap."""
    with as_probe_b():
        return p1.build_pack(record)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--pack", type=Path, default=PACK_PATH)
    args = parser.parse_args(argv)
    record, pack = build()
    for path, payload in ((args.out, record), (args.pack, pack)):
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {summary.rel(path)}  sha256 {summary.sha256_of(path)[:16]}…")

    sums = record["money"]["arithmetic"]
    table = sums["full_pass_over_the_registered_order"]
    print(
        f"  cap ${p1.CAP_USD:.2f} buys {sums['seconds_the_cap_buys']:.1f} s ·"
        f" usable {sums['usable_seconds']:.1f} s ·"
        f" {sums['units']} units at {sums['seconds_per_call_registered']:.3f} s"
    )
    print(
        f"  reading projection {sums['reading_projection_seconds']:.1f} s ·"
        f" boot charged {sums['boot_seconds_charged']:.1f} s ·"
        f" ceiling {sums['boot_kill_seconds']:.0f} s ·"
        f" budget {sums['pre_generation_budget_seconds']:.1f} s ·"
        f" affordability {sums['affordability_deadline_seconds']:.1f} s"
    )
    worst = sums["worst_case"]
    print(
        f"  worst case {worst['seconds']:.1f} s = ${worst['usd_at_the_worked_example']:.5f}"
        f" of ${worst['cap_usd_all_in']:.2f} -> fits {worst['fits_the_cap']}"
        f"  (the contract's $0.175 = ${worst['the_contracts_figure']['usd']:.5f},"
        " the delete margin charged twice)"
    )
    print(
        f"  full pass: first STOP after {table['first_stop_after_units']} unit(s) ·"
        f" tightest margin {table['tightest']['margin_seconds_per_unit']:.3f} s/unit at unit"
        f" {table['tightest']['after']} ({table['tightest']['unit']})"
    )
    print(f"  the whole diff against {summary.rel(SUPERSEDES)}: {len(MOVED)} paths, enumerated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
