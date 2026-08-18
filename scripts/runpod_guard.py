#!/usr/bin/env python3
"""The $25 Phase 4 GPU cap, enforced before a pod starts rather than after.

SPEC amendment 3.4 (4) fixes a hard cap of $25 across all of Phase 4, "checked
against RunPod billing before every start". This is that check, in the shape
`zero_shot.Budget` already proved on OpenRouter: two readings of the same
spend, and the pessimistic one wins.

- **Balance delta.** `results/spend_phase4.json` anchors the RunPod balance as
  it stood when Phase 4 opened; spend is that anchor minus the balance now.
  Always available, and it counts everything RunPod charges for — including a
  network volume, which bills while the pod is stopped. "Pod stopped" is not
  "spend stopped".
- **Billing history.** `runpodctl billing pods` / `billing network-volume` /
  `billing serverless` since the anchor timestamp — all three kinds the CLI
  offers, kept APART rather than summed on the way in (SPEC 3.23 (4)).
  Corroboration, and the thing the amendment names.
  It is read defensively: an unrecognised payload is reported as unreadable and
  never silently becomes $0.00 of spend.

The anchor file is `spend_3b.json`'s sibling and carries its footgun: delete or
regenerate it and the phase counter silently resets to zero at today's balance.

A step inside the phase can carry its own smaller cap — `docs/PROMPT-4.5h2.md` fixes
$9.00 of the phase's headroom — and it is enforced the same way, against its own anchor
in its own file. Two caps, both binding, neither able to spend the other's room. A step
takes BOTH readings too (Dv411), and it can be CLOSED (Dv412): a closed step is priced
by the settled figure its closing entry carries, never by a delta that goes on growing
at the network volume's rate for as long as the volume exists.

A ledger that has been CLOSED stops reporting a live delta. Phase 4 closes at its final
reading, and what replaces it is the $20.00 cycle-2 line of SPEC amendment 3.23, anchored
at the first balance this guard reads after the line's law is in force (3.24 (1)).

    python3.11 scripts/runpod_guard.py                 # before a start; exit 1 refuses
    python3.11 scripts/runpod_guard.py --note "4a zero-shot run"   # log a session
    python3.11 scripts/runpod_guard.py --step 45h2 --step-cap 9.00
    python3.11 scripts/runpod_guard.py --step probe-b --step-cap 0.35 --close \
        --since 2026-08-15T20:31:00+00:00 --until 2026-08-15T21:00:00+00:00 \
        --expect-ms 1514000 --tolerance 0.07 --note "probe-b closed"

Every command above is driven through :func:`parse` by the suite. A required flag added to a step
close silently broke this block once already — the example predated `--tolerance` and argparse
exited 2 on it — and a documented command nobody runs is a claim nobody checks.
"""

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LEDGER = REPO_ROOT / "results" / "spend_phase4.json"
CYCLE2_LEDGER = REPO_ROOT / "results" / "spend_cycle2.json"

BILLING_KINDS = ("pods", "network-volume", "serverless")
"""Every kind `runpodctl billing` offers, in the order the walk asks for them."""

ALWAYS_ON_KINDS = ("network-volume",)
"""The kinds that bill whether or not anything of ours is running.

SPEC amendment 3.23 (4): a step reading names the volume's rent separately from the step's own
resources, never inside a probe's figure. Dv412 measured what happens when it does not — probe-b's
100 GB volume drains ~$0.0092 an hour, so the step read $0.2907 at deletion, $0.3132 two hours later
and $0.4493 at thirteen, and the guard refused every further command for a charge that had nothing
to do with probe-b. The split is BY KIND and not by arithmetic: subtracting an hourly rate would be
a second model of the bill beside the bill."""

BILLING_BUCKET = "hour"
"""The bucket `docs/reports/pass1-probe.md` §(3)'s bounded probe used. Cosmetic for a total —
see :func:`billing_by_kind` for the measurement that says so — and it is what the contract names."""

MS_BAND = 0.01
"""How far a bounded walk's milliseconds may sit from the run record's own billed span.

DERIVED, both ends measured on this stack: `pass1-probe-b`'s complete walk reads 657 684 ms against
a record of 657 000 — **+0.104%** — while `pass1-probe`'s partial walk reads 300 000 against 427 000
— **-29.7%**, unchanged over a day. 1% is an order of magnitude above the one measured convergence
and a factor of thirty below the one measured shortfall, so it separates them without sitting on
either. The band is TWO-SIDED: over-reading is the $86.49 class arriving through a window that is
too wide, and a floor-only rule would wave it through."""

MS_FLOOR = 1_000
"""The run record publishes `billed_seconds` to whole seconds, so a walk may legitimately differ by
up to a second. Below this the band is the rounding and not a tolerance."""

PHASE_CAP_USD = 33.00
"""SPEC amendment 3.4 (4), raised 25 → 30 by amendment 3.18 (3) and 30 → 33 by amendment 3.18 (7)(b)
(operator, both 2026-08-13). Not a target — the line the run does not cross.

This constant is what the guard ENFORCES: `read_ledger` returns the ledger untouched when the file
exists, so `phase4_cap_usd` in `results/spend_phase4.json` is documentation and moves WITH this line
or it is a lie waiting to be quoted. What neither raise moves: the anchor (35.00 read
2026-08-01T08:34:09Z), `anchored_at`, and every session already logged. No money was added — the
raise lifts an artificial line, and the refusal on a balance ABOVE the anchor stays in force.

Records WRITTEN under an earlier cap are not re-scored by it either (3.18 (7)(b)): the prep-c2
projection's `fits: false` is a true sentence about $6.1690 remaining on 2026-08-13T07:59, and the
tests that read it pin the cap that was IN FORCE at its write moment — `repair_phase4_ledger
.CAP_IN_FORCE_USD` is the same pattern, one cap earlier."""

CYCLE2_CAP_USD = 20.00
"""SPEC amendment 3.23 (1), operator ruling 2026-08-16: the cycle-2 budget line.

The line that replaces the Phase 4 cap once Phase 4 is CLOSED — not a raise of it. The phase's own
$33.00 stays exactly where it is and every record written under it keeps its numbers (3.18 (7)(b),
applied a third time): a line opened after a phase closed cannot reach back into what that phase
bought. This constant is what ENFORCES the line, and `cycle2_cap_usd` in
`results/spend_cycle2.json` moves with it or it is a lie waiting to be quoted."""


def runpodctl(*args: str):
    """One read-only runpodctl call, as JSON. Never creates or destroys anything."""
    result = subprocess.run(
        ["runpodctl", *args, "--output", "json"], capture_output=True, text=True, check=True
    )
    return json.loads(result.stdout)


def balance() -> float:
    """The account balance RunPod itself reports, in dollars."""
    return float(runpodctl("user")["clientBalance"])


def sum_costs(payload) -> tuple[float, bool]:
    """Every cost-like number in a billing payload, and whether it was readable.

    The billing schema is not documented and was empty when this was written,
    so the walk is deliberately broad: anything under a key containing "cost" or
    "amount" counts. Over-counting refuses a start too early, which is the safe
    direction for a cap; inventing a zero is the one outcome this must not have.
    """
    total, seen = 0.0, False
    stack = [payload]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            for key, value in node.items():
                if isinstance(value, int | float) and not isinstance(value, bool):
                    if "cost" in key.lower() or "amount" in key.lower():
                        total += float(value)
                        seen = True
                else:
                    stack.append(value)
        elif isinstance(node, list):
            stack.extend(node)
    return total, seen


def billing_by_kind(
    anchored_at: str, until: str | None = None
) -> tuple[dict[str, float], str, int]:
    """Pods, network volumes and serverless over a WINDOW: the dollars PER KIND, how they read, and
    the milliseconds the walk covered.

    All three kinds `runpodctl billing` offers. The walk knew the first two only until
    srv-2b, where a crash-looping worker billed ~$0.55 that this reading could not see —
    an $0.86 under-count against the balance delta. `spend()` takes the max of the two, so
    the cap held; the corroborating number SPEC 3.4 (4) actually names did not.

    The kinds are kept APART on the way out rather than summed on the way in. That is 3.23 (4) and
    it is the difference between «this step cost $0.4396» and «this step cost $0.3132 and the volume
    it sat on rented for $0.1264 while it did» — see :data:`ALWAYS_ON_KINDS`. `how` is the only field
    that says whether the dictionary means anything: on anything but ``"read"`` the totals are
    partial or absent and the caller must treat the reading as UNAVAILABLE, never as $0.00.

    `until` is the END of the window and it is the whole of `docs/PROMPT-guard-until.md`. Without it
    the walk runs to NOW, so (a) an OPEN step accrues the network volume's drip forever and drifts
    over its own cap for a reason that is not the pod, and (b) `--close --since <an old window>`
    settles that step on every dollar billed since — measured at 2.6x-120x over seven ledgers,
    $86.49 against ~$13.4 recorded (docs/reports/pass1-probe.md, Dv483).

    `--bucket-size` is passed on EVERY call, bounded or not, and it is the `hour` that report's
    bounded probe used. Measured on the live account before it was wired: the bucket changes the row
    GROUPING and never the total — 2026-07-20 to 2026-08-18 reads $18.60995761 over 122 329 741 ms
    under `day` (26 rows) and under `hour` (78 rows) alike, and the volume $3.76250014 under both —
    so this is not a basis change for the live cap readings, which is the one thing it must not be.

    The third return is `timeBilledMs` summed across the walk. A settlement is a reading too
    (Dv488): billing posts LATE, so a bounded walk can be a partial one, and the only thing that can
    tell the two apart is the run record's own billed span. The caller compares them; this function
    reports what it saw.
    """
    lines, readable, empty, ms = {}, False, True, 0
    bounds = ("--end-time", until) if until else ()
    for kind in BILLING_KINDS:
        try:
            payload = runpodctl(
                "billing",
                kind,
                "--start-time",
                anchored_at,
                *bounds,
                "--bucket-size",
                BILLING_BUCKET,
            )
        except (OSError, subprocess.CalledProcessError, ValueError) as err:
            return lines, f"unreadable ({type(err).__name__})", ms
        if payload:
            empty = False
        found, seen = sum_costs(payload)
        lines[kind] = found
        ms += sum_ms(payload)
        readable |= seen
    if empty:
        return lines, "no billing rows yet", ms
    return lines, "read" if readable else "unreadable (no cost field in the payload)", ms


def sum_ms(payload) -> int:
    """Every `timeBilledMs` in a billing payload. Same broad walk as :func:`sum_costs`, same reason."""
    total, stack = 0, [payload]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "timeBilledMs" and isinstance(value, int | float):
                    total += int(value)
                else:
                    stack.append(value)
        elif isinstance(node, list):
            stack.extend(node)
    return total


def recorded_reading(sessions: list[dict]) -> float | None:
    """The figure the ledger itself last recorded for this step, or None if it never recorded one.

    The right-hand side of the tolerance gate. It is a BALANCE DELTA at a moment and the walk is a
    billing reading, so the two are not the same instrument — and on `pass1-probe-b` the difference
    is measured rather than assumed: the ledger's $0.0853189556 is exactly what the same bounded
    walk returns truncated at 09:52:00, seven minutes before the reading was taken. The balance
    LAGS. That is a finding about the right-hand side, not a licence to widen the gate.
    """
    for row in reversed(sessions):
        if not row.get("closed") and isinstance(row.get("step_spent_usd"), int | float):
            return float(row["step_spent_usd"])
    return None


def own_resources(lines: dict[str, float]) -> float:
    """What was billed for the run itself: every kind except the ones that bill regardless."""
    return sum(amount for kind, amount in lines.items() if kind not in ALWAYS_ON_KINDS)


def spend(anchor_balance: float, balance_now: float, billing_total: float) -> float:
    """The pessimistic reading of what a ledger has cost so far."""
    return max(anchor_balance - balance_now, billing_total)


def closing_entry(sessions: list[dict]) -> dict | None:
    """The entry that CLOSED this ledger, or None while it is open.

    Keyed on a typed field and never on a phrase in `note`: the note is what a human writes, and a
    ledger whose state is inferred from prose has a state nobody can test. Closure is append-only —
    the entry lands beside the sessions already there and moves none of them — so the LAST one that
    says `closed` is the closure, and a ledger reopened by a later entry would say so with its own.
    """
    for row in reversed(sessions):
        if row.get("closed"):
            return row
    return None


def step_anchor_key(step: str) -> str:
    return f"runpod_balance_at_{step}_start"


def step_ledger_path(step: str) -> Path:
    """The step's ledger, under ONE spelling: `sku-b` and `sku_b` are the same step.

    Dv151, measured: `--step sku-b` created `results/spend_sku-b.json` beside the driver's own
    `results/spend_sku_b.json`, holding the balance AFTER the step had spent $0.0943 and a
    `step_spent_usd` of 0.0. Every number in it was false and none of them looked it — a second
    anchor for one step is a counter that restarts at today's balance, which is the footgun this
    module's docstring warns about, arriving through a naming convention instead of a delete.

    Dv392, measured on probe-a: normalising here was only half the fix. `--note` rebuilt the path
    from the raw step name, so the anchor was READ from `spend_probe_a.json` and the session note
    APPENDED to `spend_probe-a.json` — the same two-anchor footgun, from the same step, in one
    command. There is now exactly one call of this function per invocation and every write uses its
    result ([[a_guard_on_one_path_is_not_a_guard]]).
    """
    return REPO_ROOT / "results" / f"spend_{step.replace('-', '_')}.json"


def anchor_key_in(ledger: dict, step: str) -> str | None:
    """The step's anchor key as this ledger actually spells it, or None if it has none.

    Normalising the FILE is not enough on its own: the driver writes `runpod_balance_at_sku-b_start`
    into `spend_sku_b.json`, so the two halves of one step disagree about the separator inside the
    same document. Both spellings are looked for before anything is created — an anchor that exists
    is never written twice, whichever way its step was typed.
    """
    for key in dict.fromkeys(
        (
            step_anchor_key(step),
            step_anchor_key(step.replace("-", "_")),
            step_anchor_key(step.replace("_", "-")),
        )
    ):
        if key in ledger:
            return key
    return None


def read_step(path: Path, step: str, cap: float, balance_now: float) -> dict:
    """A step's own anchor, created once beside whatever else its ledger already holds.

    The step ledger is shared with the step's OpenRouter anchor on purpose: one file per
    step, so "what did 4.5h2 cost" is one document rather than two that can disagree. The
    GPU anchor is a separate key and is written once, before the step's first pod.
    """
    ledger = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    key = anchor_key_in(ledger, step) or step_anchor_key(step)
    if key not in ledger:
        ledger[key] = balance_now
        # WHEN the balance was read, so the step's second reading has a window to ask for. The
        # driver of a step writes this key under the same name and the same meaning, so `setdefault`
        # rather than an assignment: whichever of the two anchored first owns the timestamp, and a
        # step ledger that already carries one is never given a later time it did not happen at.
        ledger.setdefault("anchored_at", datetime.now(UTC).isoformat(timespec="seconds"))
        ledger[f"{step}_gpu_cap_usd"] = cap
        ledger.setdefault("gpu_sessions", [])
        ledger["gpu_note"] = (
            f"RunPod account balance read before the first pod of {step}. Step spend = the"
            f" pessimistic maximum of this anchor minus the balance now and the billing walk"
            f" since `anchored_at` (SPEC 3.23 (4), Dv411), enforced against ${cap:.2f}. The"
            " SPEC amendment 3.4 (4) phase cap is enforced separately, against"
            " results/spend_phase4.json, and neither anchor may be regenerated."
        )
    return ledger


def step_reading(step_ledger: dict, key: str, balance_now: float, until: str | None = None) -> dict:
    """A step's TWO readings and the verdict they make — Dv411, the phase's own rule applied down.

    Three states, and collapsing any two of them rebuilds the defect one layer up:

    * both readings exist — the verdict is the pessimistic MAXIMUM, exactly as `spend()` takes it
      for a phase, and `lines` carries the decomposition 3.23 (4) asks the print for;
    * the anchor time is on disk and billing answers «no rows yet» or unreadable — the second
      reading is UNAVAILABLE and not zero, so the delta stands ALONE and is a LOWER BOUND;
    * the ledger carries no anchor time at all — the walk cannot even be asked. That is a different
      sentence from the one above and it prints as one: a ledger written before the guard learned to
      record the moment has no window, and pretending it answered «no rows» would hide that.
    """
    anchor = float(step_ledger[key])
    delta = anchor - balance_now
    reading = {"anchor": anchor, "key": key, "delta": delta, "lines": None, "spent": delta}
    since = step_ledger.get("anchored_at")
    if since is None:
        reading["how"] = (
            "UNAVAILABLE — this ledger records no anchor time, so the billing walk has no window"
            " to ask for and the delta stands alone as a LOWER BOUND"
        )
        return reading
    lines, how, _ms = billing_by_kind(since, until)
    if how != "read":
        reading["how"] = f"UNAVAILABLE ({how}) — the delta stands alone as a LOWER BOUND"
        return reading
    return reading | {"lines": lines, "how": how, "spent": max(delta, sum(lines.values()))}


def read_ledger(balance_now: float) -> dict:
    """The anchor, created once. Never regenerated — see the module docstring."""
    if LEDGER.exists():
        return json.loads(LEDGER.read_text(encoding="utf-8"))
    return {
        "phase4_cap_usd": PHASE_CAP_USD,
        "runpod_balance_at_phase4_start": balance_now,
        "anchored_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "note": (
            "RunPod account balance read at the start of Phase 4, before the first pod or"
            " network volume existed. Phase spend = this anchor minus the balance now, and"
            " the $25 cap of SPEC amendment 3.4 (4) is enforced against that difference."
            " Delete or regenerate this file and the counter silently restarts at today's"
            " balance — the same footgun results/spend_3b.json carries."
        ),
        "sessions": [],
    }


def read_cycle2(balance_now: float) -> dict:
    """The cycle-2 line's ledger, anchored once — at whatever the balance reads.

    SPEC amendment 3.24 (1). There was a threshold here: 3.23 (2) let the anchor be taken only on a
    reading of $40.00 or more, and this function returned None below it so the caller could print
    what it read before refusing. The clause is REPEALED — it was derived from an assumption about a
    top-up still to come, and the $20.00 had already landed on 2026-08-15 — so there is no reading
    at which anchoring is refused and no state in which this returns nothing.

    What the repeal does NOT change is the one-shot: the anchor is written once and never
    regenerated, so the first call after the amendment lands is the one that fixes the line's
    starting number. That is why it is taken by a deliberate, supervised run and not as a side
    effect of some other command.
    """
    if CYCLE2_LEDGER.exists():
        return json.loads(CYCLE2_LEDGER.read_text(encoding="utf-8"))
    return {
        "cycle2_cap_usd": CYCLE2_CAP_USD,
        "runpod_balance_at_cycle2_start": balance_now,
        "anchored_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "note": (
            "RunPod account balance read at the start of cycle 2 — the first guard reading taken"
            " after SPEC amendment 3.24 landed, by a deliberate supervised run (3.24 (1)). No"
            " threshold gates it: 3.23 (2)'s $40.00 floor is repealed, because the operator's $20"
            " top-up landed 2026-08-15 and IS this balance. Cycle-2 spend = the pessimistic maximum"
            " of this anchor minus the balance now and the billing walk since the timestamp above,"
            " and the $20.00 line of 3.23 (1) is enforced against it. Delete or regenerate this"
            " file and the counter silently restarts at today's balance — the same footgun"
            " results/spend_phase4.json carries. Phase 4 is closed and is NOT re-scored by this"
            " line: what it bought was bought under the $33.00 cap of 3.18 (7)(b)."
        ),
        "sessions": [],
    }


def write_ledger_at(path: Path, ledger: dict) -> None:
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_ledger(ledger: dict) -> None:
    write_ledger_at(LEDGER, ledger)


def print_kinds(lines: dict[str, float] | None, indent: str) -> None:
    """The decomposition SPEC 3.23 (4) asks a reading to print: one line per billed kind.

    The always-on kinds are LABELLED rather than dropped. A reader who sees only the total cannot
    tell a run that cost $0.31 while a volume it did not create rented for $0.13 beside it from a
    run that cost $0.44, and that indistinguishability is the whole of Dv412.
    """
    for kind in BILLING_KINDS:
        if not lines or kind not in lines:
            continue
        aside = (
            "   <- always on, beside the run and never inside it" if kind in ALWAYS_ON_KINDS else ""
        )
        print(f"{indent}{kind:<15} ${lines[kind]:.4f}{aside}")


def enforce(
    name: str, cap: float, anchor: float, anchored_at: str, balance_now: float
) -> tuple[float, dict[str, float], str, list[str]]:
    """Read a capped ledger BOTH ways, print what it read, and return the spend and what refuses.

    One implementation for the Phase 4 cap and for the cycle-2 line of SPEC 3.23 (1): they are the
    same instrument with two constants, and a second copy of this arithmetic would be a second place
    for the pessimistic rule of Dv33 to be half-applied — which is exactly how `--step` came to have
    one reading where the phase had two.

    Nothing is written here. A reading and a refusal are separate from a record, which is what lets
    the caller print every leg before it decides the exit code: a guard that returns on the first
    refusal cannot show the step figure the refusal is about.
    """
    lines, how, _ms = billing_by_kind(anchored_at)
    billing_total = sum(lines.values())
    spent = spend(anchor, balance_now, billing_total)

    print(f"anchor            ${anchor:.2f} at {anchored_at}")
    print(f"balance now       ${balance_now:.2f}")
    print(f"  balance delta   ${anchor - balance_now:.4f}")
    print(f"  billing since   ${billing_total:.4f} ({how})")
    print_kinds(lines if how == "read" else None, "    ")
    if how.startswith("unreadable"):
        # The cap still holds — the balance delta is the binding reading and it
        # cannot be fooled by a schema change. But a corroborating number that
        # silently became $0.00 must say so out loud, not blend into the table.
        print(
            "  WARNING: the billing payload could not be read, so only the balance delta is"
            " counting. Look at `runpodctl billing pods` by hand before the next start.",
            file=sys.stderr,
        )
    print(f"{name} SPENT     ${spent:.4f} of ${cap:.2f}")
    print(f"REMAINING         ${cap - spent:.4f}")

    refusals = []
    if balance_now > anchor:
        refusals.append(
            f"the balance (${balance_now:.2f}) is above {name}'s anchor (${anchor:.2f}), so the"
            f" account was topped up after {name} opened and the delta no longer measures it."
            " Re-anchoring is an operator decision, not a script's."
        )
    if spent >= cap:
        refusals.append(
            f"the ${cap:.2f} {name} cap is reached (${spent:.4f} spent). Stop and report — a cap"
            " is not raised to finish a run."
        )
    return spent, lines, how, refusals


def complete(walk_ms: int, expect_ms: int | None) -> bool:
    """Did the bounded walk cover the run record's own billed span?

    Dv488, as a function: at 17:23Z the v5b walk answered «no billing rows yet» and refused; by
    18:37Z it had posted 1 514 000 ms; in between it offered 29% of the truth and a close would have
    settled on it. «Readable» and «complete» are different states and only the run record can tell
    them apart. With no record to compare against — every one of the 22 old ledgers — there is
    nothing to check and the caller's dollar tolerance is the only gate."""
    if expect_ms is None:
        return True
    return abs(walk_ms - expect_ms) <= max(MS_FLOOR, MS_BAND * expect_ms)


def closing_record(
    *,
    anchored_at: str,
    balance_now: float,
    anchor: float,
    lines: dict,
    how: str,
    note: str,
    until: str | None = None,
    walk_ms: int = 0,
    expect_ms: int | None = None,
) -> dict | None:
    """The common half of a closing entry, or None when the walk cannot settle anything.

    A closing entry states a SETTLED figure, so a walk that answered «no billing rows yet» or came
    back unreadable cannot produce one: closing on it would freeze a zero into a record that is
    never re-derived. Refusing to close is recoverable; a wrong settlement is the one outcome that
    is not. The caller adds the headline field its ledger names — `spent_usd` for a phase or a line,
    `settled_usd` for a step — because they are not the same number and must not share a key.

    Every figure is derived from the ROUNDED lines and not from the full-precision walk, so the
    entry re-derives from what it publishes: a reader who adds up `billing_by_kind` gets
    `billing_since_usd`, and the step's headline is the same sum with the always-on kinds left out.
    Measured the other way round first — the headline came from the unrounded walk and disagreed
    with its own decomposition by $0.000001, which is the whole distance between a record and a
    record that can be checked.
    """
    if how != "read" or not complete(walk_ms, expect_ms):
        return None
    published = {kind: round(value, 6) for kind, value in lines.items()}
    return {
        "at": datetime.now(UTC).isoformat(timespec="seconds"),
        "closed": True,
        "balance": balance_now,
        "window_start": anchored_at,
        "window_end": until,
        "walk_ms": walk_ms,
        "expected_ms": expect_ms,
        "balance_delta_usd": round(anchor - balance_now, 6),
        "billing_since_usd": round(sum(published.values()), 6),
        "billing_by_kind": published,
        "note": note,
    }


def line_reading(live: dict, balance_now: float, *, note: str, at: str | None = None) -> dict:
    """One reading of the LIVE ledger — the shape both the `--note` path and a step close write.

    One function because the two are the same fact: the guard looked at the account at a moment and
    this is what it saw. Two spellings of it would be two shapes in one file, and the check that
    reads them matches on `balance`.
    """
    return {
        "at": at or datetime.now(UTC).isoformat(timespec="seconds"),
        "balance": balance_now,
        "spent_usd": round(live["spent"], 4),
        "remaining_usd": round(live["cap"] - live["spent"], 4),
        "balance_delta_usd": round(live["anchor"] - balance_now, 4),
        "billing_since_usd": round(sum(live["lines"].values()), 6),
        "billing_read": live["how"],
        "note": note,
    }


def parse(argv: list[str] | None = None) -> argparse.Namespace:
    """The command line, and every cross-check that decides whether it is one.

    Separate from :func:`main` so the examples in this module's docstring can be driven against it
    without a balance, a ledger or a write — which is the only thing that could have caught
    `--tolerance` breaking the block above.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--note", help="record this reading as a pod session in the ledger")
    parser.add_argument("--step", help="also enforce a step cap, anchored in its own ledger")
    parser.add_argument("--step-cap", type=float, help="the step's cap in USD")
    parser.add_argument("--step-ledger", type=Path, default=None)
    parser.add_argument(
        "--close",
        action="store_true",
        help="append a CLOSING entry — the settled figure and its decomposition by kind",
    )
    parser.add_argument(
        "--since",
        help="the closing walk's window start, for a ledger anchored before the guard recorded one",
    )
    parser.add_argument(
        "--until",
        help="the walk's END, ISO-8601. Bounds the step reading AND the closing walk",
    )
    parser.add_argument(
        "--expect-ms",
        type=int,
        help="the run record's own billed span; a walk outside MS_BAND of it is PARTIAL, not a read",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        help="how far a settled figure may sit from the ledger's own recorded reading, as a"
        " fraction. NO default: the control table the contract named cannot yield one, so the"
        " caller says the number or there is no close",
    )
    args = parser.parse_args(argv)
    if bool(args.step) != bool(args.step_cap):
        parser.error("--step and --step-cap go together: a cap with no anchor is not a cap")
    if args.close and not args.note:
        parser.error("--close writes a closing entry and a closing entry says why it closed")
    if args.since and not args.close:
        parser.error("--since is the closing walk's window and means nothing without --close")
    if args.close and args.step and args.tolerance is None:
        parser.error(
            "--close on a step needs --tolerance: a settled figure is checked against the ledger's"
            " own recorded reading, and this module has no number it is entitled to supply"
        )
    if args.expect_ms is not None and not args.close:
        parser.error("--expect-ms is the completeness gate on a close and means nothing without it")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse(argv)

    balance_now = balance()
    refusals: list[str] = []

    # --- the phase, or the line that replaced it -----------------------------------------------
    ledger = read_ledger(balance_now)
    phase_closed = closing_entry(ledger["sessions"])
    live = None
    if phase_closed is None:
        anchor = float(ledger["runpod_balance_at_phase4_start"])
        spent, lines, how, said = enforce(
            "PHASE 4", PHASE_CAP_USD, anchor, ledger["anchored_at"], balance_now
        )
        refusals += said
        live = {
            "ledger": ledger,
            "path": LEDGER,
            "cap": PHASE_CAP_USD,
            "anchor": anchor,
            "anchored_at": ledger["anchored_at"],
            "spent": spent,
            "lines": lines,
            "how": how,
        }
        if not LEDGER.exists():
            write_ledger(ledger)
            print(f"anchored {LEDGER.name} — commit it and never regenerate it")
    else:
        print(
            f"PHASE 4 CLOSED    ${phase_closed['spent_usd']:.4f} of ${PHASE_CAP_USD:.2f}"
            f"  (final reading {phase_closed['at']})"
        )
        print_kinds(phase_closed.get("billing_by_kind"), "  ")
        # 3.24 (1): no threshold gates the anchor any more, so there is no «NOT ANCHORED» state and
        # no inter-ledger gap for the guard to report. 3.23 (3) still describes what that gap was —
        # it is closed by this reading, not by a branch.
        cycle = read_cycle2(balance_now)
        anchor = float(cycle["runpod_balance_at_cycle2_start"])
        spent, lines, how, said = enforce(
            "CYCLE 2", CYCLE2_CAP_USD, anchor, cycle["anchored_at"], balance_now
        )
        refusals += said
        live = {
            "ledger": cycle,
            "path": CYCLE2_LEDGER,
            "cap": CYCLE2_CAP_USD,
            "anchor": anchor,
            "anchored_at": cycle["anchored_at"],
            "spent": spent,
            "lines": lines,
            "how": how,
        }
        if not CYCLE2_LEDGER.exists():
            write_ledger_at(CYCLE2_LEDGER, cycle)
            print(f"anchored {CYCLE2_LEDGER.name} — commit it and never regenerate it")

    # --- closing the live ledger ----------------------------------------------------------------
    if args.close and not args.step:
        if live is None:
            refusals.append(
                "there is nothing live to close: Phase 4 is closed already and the cycle-2 line has"
                " no anchor yet."
            )
        else:
            # The window and the figures have to be the SAME walk. `enforce` read from the ledger's
            # own anchor with no end bound, so a `--since`/`--until` close taking its lines would
            # record a `window_start` the numbers were never measured over. Re-walk when a window
            # was supplied; keep `enforce`'s reading when it was not, so the ordinary close costs
            # no second call.
            window = args.since or live["anchored_at"]
            lines, how, walk_ms = live["lines"], live["how"], 0
            if args.since or args.until:
                lines, how, walk_ms = billing_by_kind(window, args.until)
            entry = closing_record(
                anchored_at=window,
                balance_now=balance_now,
                anchor=live["anchor"],
                lines=lines,
                how=how,
                note=args.note,
                until=args.until,
                walk_ms=walk_ms,
                expect_ms=args.expect_ms,
            )
            if entry is None:
                refusals.append(
                    f"the billing walk answered «{how}» and covered {walk_ms} ms against an expected"
                    f" {args.expect_ms}, so there is no settled figure to close on. A closing entry"
                    " is never re-derived — refusing is the recoverable outcome."
                )
            else:
                # from the entry's OWN two readings, so `spent_usd` is the pessimistic maximum of
                # the numbers a reader can see rather than of a pair only this process held
                settled = max(entry["balance_delta_usd"], entry["billing_since_usd"])
                entry |= {
                    "spent_usd": round(settled, 4),
                    "remaining_usd": round(live["cap"] - settled, 4),
                }
                live["ledger"]["sessions"].append(entry)
                write_ledger_at(live["path"], live["ledger"])
                print(f"CLOSED {live['path'].name} at ${entry['spent_usd']:.4f} — entry APPENDED")

    # --- a step's own cap, inside the line's ------------------------------------------------------
    step_ledger, step_path, step_spent, anchor_is_new = None, None, None, False
    if args.step:
        path = step_path = args.step_ledger or step_ledger_path(args.step)
        on_disk = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        step_ledger = read_step(path, args.step, args.step_cap, balance_now)
        key = anchor_key_in(step_ledger, args.step)
        anchor_is_new = anchor_key_in(on_disk, args.step) is None
        shut = closing_entry(step_ledger.get("gpu_sessions", []))

        if args.close and shut is None:
            since = args.since or step_ledger.get("anchored_at")
            if anchor_is_new:
                refusals.append(
                    f"{args.step} has no anchor on disk — a step that never ran cannot be closed."
                )
            elif since is None:
                refusals.append(
                    f"{path.name} carries no `anchored_at` and no --since was given, so the closing"
                    " walk has no window to ask for."
                )
            else:
                lines, how, walk_ms = billing_by_kind(since, args.until)
                shut = closing_record(
                    anchored_at=since,
                    balance_now=balance_now,
                    anchor=float(step_ledger[key]),
                    lines=lines,
                    how=how,
                    note=args.note,
                    until=args.until,
                    walk_ms=walk_ms,
                    expect_ms=args.expect_ms,
                )
                settled = shut and round(own_resources(shut["billing_by_kind"]), 6)
                recorded = recorded_reading(step_ledger.get("gpu_sessions", []))
                off = (
                    None
                    if shut is None or recorded in (None, 0)
                    else abs(settled - recorded) / abs(recorded)
                )
                if shut is None:
                    refusals.append(
                        f"the billing walk over {args.step}'s window answered «{how}» and covered"
                        f" {walk_ms} ms against the run record's {args.expect_ms}, so there is no"
                        " settled figure to close on. A PARTIAL walk is a third state and settling"
                        " on it freezes a number that is never re-derived."
                    )
                elif off is not None and off > args.tolerance:
                    # BEFORE the write, and it is the whole reason the gate exists: the $86.49 class
                    # arrives as a plausible number, not as an error. Both figures go in the
                    # refusal so the debt can be carried NAMED.
                    shut = None
                    refusals.append(
                        f"{args.step} settles at ${settled:.6f} against its own recorded reading of"
                        f" ${recorded:.6f} — {off:.1%} off, outside the registered tolerance of"
                        f" {args.tolerance:.1%}. NOT closed: a close outside the band is a refusal,"
                        " never a rounding, and the ledger stays OPEN and named."
                    )
                if shut is not None:
                    # `settled_usd` and the `step_spent_usd` of the entries above it are NOT the
                    # same number and deliberately do not share a key: the older field is a balance
                    # delta at a moment, this one is what the step's OWN resources billed, with the
                    # always-on kinds left outside it (3.23 (4)).
                    shut["settled_usd"] = settled
                    shut["recorded_reading_usd"] = recorded
                    shut["tolerance"] = args.tolerance
                    step_ledger.setdefault("gpu_sessions", []).append(shut)
                    write_ledger_at(path, step_ledger)
                    print(f"CLOSED {path.name} at ${shut['settled_usd']:.4f} — entry APPENDED")
                    # and the LIVE ledger hears about it. A step's close takes a fresh balance
                    # reading that existed nowhere else: the `--note` branch below is skipped for
                    # every `--close`, and it is skipped again when a cap refusal returns before it,
                    # so a settled step could leave a reading only its own file carried — which is
                    # exactly the silence tests/test_repair_phase4_ledger.py exists to catch, and it
                    # caught this one. Written HERE, beside the entry it witnesses, so a refusal
                    # after it cannot take the witness with it.
                    if live is not None:
                        live["ledger"]["sessions"].append(
                            line_reading(
                                live,
                                balance_now,
                                at=shut["at"],
                                note=(
                                    f"{args.step} CLOSED at ${shut['settled_usd']:.4f} —"
                                    f" {args.note}"
                                ),
                            )
                        )
                        write_ledger_at(live["path"], live["ledger"])

        if shut is not None:
            step_spent = shut["settled_usd"]
            print(
                f"{args.step.upper()} CLOSED     ${step_spent:.4f} of ${args.step_cap:.2f}"
                f"  (settled at {shut['at']}, window from {shut['window_start']})"
            )
            print_kinds(shut.get("billing_by_kind"), "  ")
        else:
            reading = step_reading(step_ledger, key, balance_now, args.until)
            step_spent = reading["spent"]
            print(
                f"{args.step.upper()} SPENT      ${step_spent:.4f} of ${args.step_cap:.2f}"
                f"  (anchor ${reading['anchor']:.2f} from {key})"
            )
            print(f"  balance delta   ${reading['delta']:.4f}")
            if reading["lines"] is None:
                print(f"  billing since   {reading['how']}")
            else:
                print(f"  billing since   ${sum(reading['lines'].values()):.4f} (read)")
                print_kinds(reading["lines"], "    ")
                print(
                    f"  step resources  ${own_resources(reading['lines']):.4f}"
                    "   (every kind except the always-on ones)"
                )

        if step_spent >= args.step_cap:
            refusals.append(
                f"{args.step}'s ${args.step_cap:.2f} cap is reached (${step_spent:.4f} spent)."
                " Stop and report — an overrun aborts, it does not raise the cap."
            )

    if refusals:
        for reason in refusals:
            print(f"\nREFUSED: {reason}", file=sys.stderr)
        return 1

    if args.step and anchor_is_new:
        write_ledger_at(step_path, step_ledger)
        print(f"anchored {step_path.name} for {args.step} — commit it and never regenerate it")

    if args.note and not args.close:
        if step_ledger is not None:
            step_ledger["gpu_sessions"].append(
                {
                    "at": datetime.now(UTC).isoformat(timespec="seconds"),
                    "balance": balance_now,
                    "step_spent_usd": round(step_spent, 4),
                    "note": args.note,
                }
            )
            # the SAME path the anchor was read from, and not a second construction of it: the
            # write used to spell `spend_{step}.json` while the read normalised the separator, so
            # one `--step probe-a --note …` maintained two ledgers for one step (Dv392)
            write_ledger_at(step_path, step_ledger)
        if live is not None:
            live["ledger"]["sessions"].append(line_reading(live, balance_now, note=args.note))
            write_ledger_at(live["path"], live["ledger"])
        print(f"logged: {args.note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
