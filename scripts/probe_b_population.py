#!/usr/bin/env python3
"""probe-b's population — a registered SUBSET, enumerated, with four threads INJECTED past the gate.

**Why a subset.** probe-a measured 54.8 s a thread on an L4 and its go/no-go stopped the run: the
111-thread cell prices at $1.87–$4.18, above both the phase remainder and the ≤30-minute budget.
`docs/PROMPT-probe-b.md` D2 registers the threads the reference's cases actually live in instead —
every gating bar except «how many of the 111 are signal-bearing» is scored over them.

**Why four of them are injected.** SPEC 3.21 (1)'s marker rule takes away the only lexicon hit of
E1, E4a, E4b and N3, so the gate drops those whole threads BEFORE payment and the reader is never
shown them. probe-a measured that and registered bars 2 and 3 over what was left — 2 of 2 entity
cases instead of 4 of 4. This contract buys the four directly, from outside the billing gate, and
marks them `injected: true`:

- they exist to make the operator's obligatory cases reachable, and nothing else;
- they NEVER enter a production aggregate, and never a window or per-thread price for the 111 —
  the gate does not deliver them, so a rate measured over them would price a population nobody has;
- they DO cost money and are inside probe-b's cap, because they are threads this run buys.

Whether the production gate should deliver them at all is the sitting's question, not this file's.

**What a thread carries** is what `scripts/reader_population.py` builds: the post's text and its
payable comments, the same silencers applied to the comments, so an injected thread differs from a
gated one only in how it got here.

    PYTHONPATH=src python3 scripts/probe_b_population.py
"""

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gate_census_w1 as census  # noqa: E402
import reader_population as cell  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import loop  # noqa: E402

GOLD = REPO_ROOT / "results" / "reader_gold_w1.json"


INJECTED = {
    "@matusi_ukr:22242": "E1",
    "@mandziak:3684": "E4a",
    "@mandziak:3689": "E4b",
    "@sashafitnesslife:3939": "N3",
}
"""The four threads the gate removes before payment, named by the case each of them carries.

Written as a literal map and checked against the gold's own reachability block below, so the list
cannot quietly grow: an injected thread is one the operator's cases require and the production gate
does not deliver, and any other thread bought this way would be the executor widening its own
sample ([[a_dimension_belongs_to_the_registry]])."""

WARM_UP = ("@mandziak:3701", "@VARUS_channel:10451", "@tarilka_malyuka:715")
"""probe-a's registered draw, re-read under v2 so the two instruments are compared on the same
threads. They were drawn from the MIDDLE third of the 111 by size; where they land inside THIS
population is recorded in the registration, because a warm-up's representativeness is a fact about
where it sits in the sample it prices."""


def key(channel: str, post_id) -> str:
    return f"{channel}:{post_id}"


def gold_threads() -> dict[str, list[str]]:
    """Every thread the reference names, and which of its cases live there.

    Read from `results/reader_gold_w1.json` rather than transcribed: the gold is the reference
    structured, it is sha-pinned by the registration, and a hand-typed list here would be a second
    reading of the same document that could disagree with it.
    """
    gold = json.loads(summary.read_text_or_refuse(GOLD))
    threads: dict[str, list[str]] = {}
    for group in ("flagships", "entity_cases", "noise_threads"):
        for one in gold[group]:
            threads.setdefault(key(one["channel"], one["post_id"]), []).append(one["id"])
    # the S list names msg_ids and, for three of its six rows, no post at all — the store is what
    # resolves those, and the gold already recorded which post each id sits under (Dv384's shape)
    for one in gold["secondary"]:
        row = one["evidence_row"]
        threads.setdefault(key(one["channel"], row["post_id_in_the_store"]), []).append(one["id"])
    for one in gold["per_comment"]:
        row = one["evidence_row"]
        threads.setdefault(key(one["channel"], row["post_id_in_the_store"]), []).append(
            f"pc:{one['msg_id']}"
        )
    return threads


def build(thread: dict) -> dict:
    """One window thread in the shape the reader is given it — the census's own construction."""
    surviving = [
        row for row in thread["comments"] if not census.silenced_comment(row, census.SILENCERS)
    ]
    payable = [
        {"msg_id": int(row["msg_id"]), "text": summary.comment_text(row)}
        for row in surviving
        if loop.has_text(summary.comment_text(row))
    ]
    return {
        "channel": thread["channel"],
        "post_id": thread["post_id"],
        "post_text": thread["post_text"],
        "comments": payable,
        "silenced": len(thread["comments"]) - len(surviving),
        "text_less": len(surviving) - len(payable),
    }


def population() -> list[dict]:
    """The registered subset, in one fixed order, each thread saying why it is here.

    Sorted by `channel:post_id` and never by size or by case: the order is part of the digest, and
    an order that depended on a measurement would move the pin whenever the measurement did
    ([[an_order_key_that_is_not_total]])."""
    gated = {key(one["channel"], one["post_id"]) for one in cell.population()}
    by_key = {key(one["channel"], one["post_id"]): one for one in cell.window()}

    wanted = gold_threads()
    for name in WARM_UP:
        wanted.setdefault(name, []).append("warm-up")

    missing = sorted(name for name in wanted if name not in by_key)
    if missing:
        raise SystemExit(f"threads the registration names are not in the window at all: {missing}")

    kept = []
    for name in sorted(wanted):
        thread = build(by_key[name])
        thread["cases"] = sorted(wanted[name])
        thread["injected"] = name not in gated
        thread["in_the_census_cell"] = name in gated
        kept.append(thread)
    assert_the_injected_are_the_four_the_gate_removes(kept)
    return kept


def assert_the_injected_are_the_four_the_gate_removes(kept: list[dict]) -> None:
    """The injected set is EXACTLY the literal above, and every one of them really is outside.

    Both directions, because either alone passes for the wrong reason: a thread marked injected that
    the census cell holds would be a mislabelled row in a record the sitting reads, and a thread the
    gate removed but nobody marked would be paid-for evidence entering an aggregate that must not
    have it.
    """
    outside = {key(one["channel"], one["post_id"]) for one in kept if one["injected"]}
    if outside != set(INJECTED):
        raise SystemExit(
            f"the threads outside the census cell are {sorted(outside)} and the registration"
            f" injects {sorted(INJECTED)}. Stop and report — one of the two is describing a"
            " population nobody registered."
        )
    reach = json.loads(summary.read_text_or_refuse(GOLD))["reachability"]
    unreachable = {
        one["id"]
        for group in ("entity_cases", "noise_threads", "flagships")
        for one in reach[group]["unreachable"]
    }
    if unreachable != set(INJECTED.values()):
        raise SystemExit(
            f"the gold calls {sorted(unreachable)} unreachable and this file injects"
            f" {sorted(INJECTED.values())} — the two readings of the marker rule disagree"
        )


def digest(kept: list[dict]) -> str:
    """A digest over the LIST, so the pin is the population and not its size.

    `channel:post_id` and every payable msg_id, in the enumeration's order, with the injected flag
    inside the line: a subset that swapped a gated thread for an injected one of the same shape
    would otherwise hash the same ([[the_guard_hashes_the_half_that_cannot_move]]).
    """
    body = "\n".join(
        f"{key(one['channel'], one['post_id'])}\t{'injected' if one['injected'] else 'gated'}\t"
        + ",".join(str(row["msg_id"]) for row in one["comments"])
        for one in kept
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def main(argv: list[str] | None = None) -> int:
    kept = population()
    payable = sum(len(one["comments"]) for one in kept)
    injected = [one for one in kept if one["injected"]]
    print(
        f"probe-b population: {len(kept)} threads · {payable} payable comments ·"
        f" {len(injected)} injected"
    )
    print(f"  digest {digest(kept)[:16]}…")
    for one in kept:
        mark = "INJ" if one["injected"] else "   "
        print(
            f"  {mark} {key(one['channel'], one['post_id']):32s}"
            f" {len(one['comments']):3d} payable · {','.join(one['cases'])}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
