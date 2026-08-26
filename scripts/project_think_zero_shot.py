#!/usr/bin/env python3
"""Rung 2 for `think-zero-shot-d2`: what the rest of the programme costs at the MEASURED rate.

The registration grades nothing — it registers readings — so there is no `gate_think_zero_shot.py`
and no `--watch`. What it does register is a rung that fires seven times: after the smoke and after
every stage, against a cap of $8.00 at the price the create returned. This is that arithmetic, and
it exists as a file so it is not re-derived by hand on a live clock ([[a_budget_is_not_an_elapsed]]).

Nothing here is typed. The stages, their units and the cap come out of the record; the rate comes
out of `results/measurements.jsonl` by NAME, so the smoke's own reading is what prices the
remainder and a remembered number cannot get in (the 97 s/thread error, 26.08); what is already
answered is counted from the out-files themselves, exactly as `reader_v5_pod_runner.already_answered`
counts it — the smoke's thread is one of the remainder's 68 and stage 7 must not be priced for it.

    python3 scripts/project_think_zero_shot.py --usd-per-hour 0.79 --elapsed-seconds 1830 \
        --run-dir results --load-seconds 60

Verdicts are the record's own rung 2: at or under the cap GO, over it by ≤20% ASK, over by more
KILL. `stop_after` names the last stage that still fits UNDER the cap, which is what a KILL needs
to know — the value order is the drop order, from the end.
"""

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RECORD = "prereg_think_zero_shot.json"
#: Which ledger row prices a stage. The discriminator is the stage's own output ceiling — pass 2
#: reasons over a thread at 8 000 tokens, pass 1 over one comment at 4 000 — never a list of names.
RATE_OF = {4000: "think_pass1_seconds_per_call", 8000: "think_pass2_seconds_per_thread"}
ASK_BAND = 1.20


def rates(ledger: Path) -> dict[str, float]:
    """The LAST row written under each name — a re-measure supersedes, it does not average."""
    out: dict[str, float] = {}
    for line in ledger.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            out[row["name"]] = float(row["value"])
    return out


def answered(run_dir: Path, out_file: str) -> int:
    """Rows already in an out-file, the way the runner's resume clause counts them."""
    path = run_dir / out_file
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def legs_of(stage: dict) -> list[dict]:
    """The legs the STAGE'S OWN COMMAND generates, which is not always the legs its pack carries.

    Stages 3 and 5 share one pack holding both dev legs and are run `--only v2` and `--only base`
    — the value order buys v2 first so a KILL still leaves a column. Pricing both legs at stage 3
    charges 400 units for a command that generates 200 and leaves stage 5 free, which reads as a
    programme that fits when it does not. The selector is the record's own `note`, not a list here.
    """
    note = stage.get("note", "")
    if not note.startswith("--only "):
        return stage["legs"]
    wanted = note.split(None, 1)[1].strip()
    picked = [leg for leg in stage["legs"] if leg["name"] == wanted]
    assert picked, f"stage {stage['order']} says `{note}` and has no leg called {wanted!r}"
    return picked


def plan(record: dict, run_dir: Path, ledger: dict[str, float], load_seconds: float) -> list[dict]:
    """One row per stage still owed, in the record's own value order, priced at its family's rate.

    A stage is a separate process, so every one of them pays the model load again; that is the
    shape of «one command per stage» and it is charged here rather than discovered on the bill.
    """
    import sys

    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import reader_v5_pod_runner as runner

    seen: dict[str, int] = {}
    rows = []
    for stage in record["stages"]:
        name = RATE_OF[stage["output_tokens"]]
        rate = ledger.get(name)
        owed = 0
        for leg in legs_of(stage):
            out = runner.out_name(leg["out"], stage["serving_config"])
            already = seen.get(out, answered(run_dir, out))
            owed += max(0, leg["units"] - already)
            seen[out] = max(already, leg["units"])
        rows.append(
            {
                "order": stage["order"],
                "stage": stage["stage"],
                "units": owed,
                "rate_name": name,
                "rate": rate,
                "seconds": None if rate is None else load_seconds + owed * rate,
            }
        )
    return [row for row in rows if row["units"]]


def project(record: dict, rows: list[dict], usd_per_hour: float, elapsed: float) -> dict:
    cap = record["money"]["cap_usd"]
    spent = elapsed * usd_per_hour / 3600
    running, stop_after, table = spent, None, []
    for row in rows:
        if row["seconds"] is None:
            raise SystemExit(
                f"stage {row['order']} has no rate: `{row['rate_name']}` is not in the ledger."
                " The smoke writes it — project nothing until it has."
            )
        running += row["seconds"] * usd_per_hour / 3600
        table.append({**row, "cumulative_usd": round(running, 4)})
        if running <= cap:
            stop_after = row["order"]
    over = running / cap if cap else float("inf")
    return {
        "usd_per_hour": usd_per_hour,
        "spent_usd": round(spent, 4),
        "projected_usd": round(running, 4),
        "cap_usd": cap,
        "over_cap_ratio": round(over, 4),
        "verdict": "GO" if over <= 1 else ("ASK" if over <= ASK_BAND else "KILL"),
        "stop_after_stage": stop_after,
        "table": table,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--usd-per-hour", type=float, required=True, help="the CREATE's price")
    parser.add_argument("--elapsed-seconds", type=float, required=True, help="since pod create")
    parser.add_argument("--run-dir", type=Path, default=REPO_ROOT / "results")
    parser.add_argument("--ledger", type=Path, default=REPO_ROOT / "results" / "measurements.jsonl")
    parser.add_argument("--load-seconds", type=float, default=60.0, help="model load, per stage")
    parser.add_argument("--record", type=Path, default=REPO_ROOT / "results" / RECORD)
    args = parser.parse_args(argv)

    record = json.loads(args.record.read_text(encoding="utf-8"))
    rows = plan(record, args.run_dir, rates(args.ledger), args.load_seconds)
    out = project(record, rows, args.usd_per_hour, args.elapsed_seconds)
    print(f"spent ${out['spent_usd']:.4f} of ${out['cap_usd']:.2f} at ${args.usd_per_hour:.4f}/h")
    for row in out["table"]:
        print(
            f"  {row['order']} {row['stage']:<28} {row['units']:>4} u"
            f" × {row['rate']:>7.2f}s + {args.load_seconds:.0f}s load"
            f" = {row['seconds']:>8.1f}s → ${row['cumulative_usd']:.4f}"
        )
    print(
        f"{out['verdict']} — projected ${out['projected_usd']:.4f}"
        f" = {out['over_cap_ratio']:.2f}× the cap"
        f" · everything through stage {out['stop_after_stage']} fits"
    )
    return 0 if out["verdict"] == "GO" else 1


if __name__ == "__main__":
    raise SystemExit(main())
