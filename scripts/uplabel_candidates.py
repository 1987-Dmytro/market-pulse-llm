#!/usr/bin/env python3
"""What the corpus still holds to up-label, and what calibrating it would cost (4.5d).

The 4.5d gate decides an appetite — how many more rows to label alongside the
taxonomy-v2 re-label. That decision needs two things this script produces and
nothing else: **counts** of what is actually labelable, and the **operator hours**
the pre-registered calibration would take. Nothing here labels a row.

Two exclusions decide the counts and both are easy to leave out by accident:

- **already labelled** — 3,771 comment rows carry labels across five files, not the
  2,000-row batch alone.
- **thread-mates of an evaluation row** — the split is by thread (`channel`,
  `parent_msg_id`) so that no test comment's thread-mate can be trained on
  (docs/frozen-testsets.md). An up-label pool feeds training, so a raw count that
  ignores threads offers rows that may not legally be labelled.

The two heuristics only rank; whether a row is really about service or really
ironic is decided by the guideline, by a human or a model reading it. `service`
keywords are UA+RU forms of the six shapes amendment 3.8 names, and the irony
score is the one `market_pulse.sarcasm` already uses for mining.

    python3.11 scripts/uplabel_candidates.py

Writes `results/uplabel_candidates.json`; reads only, labels nothing.
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))  # the package is not pip-installed

from market_pulse.sarcasm import score  # noqa: E402

RAW = REPO_ROOT / "data" / "raw" / "comments"
FROZEN = REPO_ROOT / "data" / "frozen"
ANNOTATION = REPO_ROOT / "data" / "annotation"
OUT = REPO_ROOT / "results" / "uplabel_candidates.json"
PROBE_ROWS = REPO_ROOT / "results" / "relabel_45d_probe_rows.jsonl"

LABELLED = (
    FROZEN / "comments_train.jsonl",
    FROZEN / "comments_test.jsonl",
    FROZEN / "sarcasm_holdout.jsonl",
    ANNOTATION / "sarcasm_candidates.jsonl",
    ANNOTATION / "sarcasm_holdout_pool.jsonl",
)
"""Every file that already holds a labelled comment row. Five, not one."""

EVALUATION = (FROZEN / "comments_test.jsonl", FROZEN / "sarcasm_holdout.jsonl")

SERVICE_SIGNALS = {
    "delivery / order": (
        r"доставк|замовлен|заказ|кур'єр|курьер|самовив|самовыв|відправ|отправ|"
        r"замовл|заказыв|посилк|посылк"
    ),
    "app / site / checkout": (
        r"додаток|додатку|приложени|сайт|касі|касс|на касі|чек\b|термінал|"
        r"оплат|розрахув|расчет|онлайн|застосун"
    ),
    "support / staff": (
        r"підтримк|поддержк|гаряч[аоуі]{1,2}\s*лін|горяч[аяую]{1,2}\s*лини|оператор|"
        r"консультант|менеджер|персонал|продавец|продавч|продавщ|касир|кассир|"
        r"охорон|охран|адмін|админ|працівник|сотрудник|обслуговув|обслужив"
    ),
    "loyalty / points": r"бонус|\bбал[иіыов]|карт[аиуко][^\w]*(клієнт|клиент|варус|лоял)|лояльн",
    "promo mechanics / giveaway": (
        r"розіграш|розыгрыш|конкурс|переможц|победител|виграв|виграл|выиграл|"
        r"умови акці|условия акци|правила акці|правила акци|призов|приз\b"
    ),
    "queue / shop floor": r"черг[аиу]|очеред|каса\b|відділ|отдел|магазин[^\w]*закр|не працю",
}
SERVICE = {name: re.compile(pattern, re.IGNORECASE) for name, pattern in SERVICE_SIGNALS.items()}
IRONY_STRONG = 3
"""An irony score of 3 means a signal *pair* fired — `market_pulse.sarcasm` is built
so that a lone marker is only worth a look and a pair is where irony lives."""

BOT = re.compile(r"^[+＋➕\s]+$")
"""Participation markers under giveaway posts — the corpus' most repeated string,
and never a reaction (docs/annotation/comments.md)."""

TIERS = (2000, 5000, 9000)
STRATA = ("service-rich", "sarcasm-rich", "general")
CALIBRATION_SAMPLE = 100
"""SPEC §8 and the guideline's own quality control: agreement is measured by
re-reading *a random 100 rows*. The number is pre-registered, so it is not resized
here — and it does not need to be, because binomial precision depends on the sample
and not on the population it is drawn from."""
AGREEMENT_BAR = 0.90
REVIEW_ROWS_PER_HOUR = 150
"""Verdict-style review — a label is shown and the operator agrees or does not.

Provenance, both from this project: the operator ruled 244 blind verdicts in the
4.5a audit in one sitting, and the team lead's own estimate for the 28-block law
pack was 10–15 minutes (~130 rows/h). 150 is the middle of that; the report prints
the band, because an hours table without a stated rate is a guess wearing a table."""
RATE_BAND = (120, 180)


def load(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"{path.relative_to(REPO_ROOT)}: not found")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def normalised(text: str) -> str:
    return " ".join(text.split()).lower()


def thread_of(row: dict) -> tuple:
    return (row["channel"], row["parent_msg_id"])


def excluded() -> tuple[set[str], set[str], set[tuple]]:
    """Ids and texts already labelled, and the threads an evaluation row sits in."""
    rows = {path: load(path) for path in LABELLED}
    ids = {row["id"] for batch in rows.values() for row in batch}
    texts = {normalised(row["text"]) for batch in rows.values() for row in batch}
    threads = {thread_of(row) for path in EVALUATION for row in rows[path]}
    # a scoreable train row's thread is training's already — labelling more of it
    # adds rows, not threads, and cannot leak an evaluation row that is not there
    return ids, texts, threads


def funnel() -> tuple[list[dict], dict]:
    """The labelable pool, and how much every exclusion took out of the corpus."""
    corpus = [
        {**record, "id": f"{record['channel']}:{record['msg_id']}"}
        for source in sorted(RAW.glob("*.jsonl"))
        for record in load(source)
    ]
    ids, texts, threads = excluded()
    steps = {"corpus": len(corpus)}

    rows = [row for row in corpus if row["text"].strip()]
    steps["no text (media only)"] = len(corpus) - len(rows)

    fresh = [row for row in rows if row["id"] not in ids]
    steps["already labelled"] = len(rows) - len(fresh)

    free = [row for row in fresh if thread_of(row) not in threads]
    steps["in a test or holdout thread"] = len(fresh) - len(free)

    pool, seen, copies, repeats = [], set(), 0, 0
    for row in free:
        text = normalised(row["text"])
        if text in texts:
            copies += 1
        elif text in seen:
            repeats += 1
        else:
            seen.add(text)
            pool.append(row)
    steps["verbatim copy of a labelled text"] = copies
    steps["repeat of another candidate"] = repeats
    steps["labelable pool"] = len(pool)
    return pool, steps


def classify(pool: list[dict]) -> dict:
    """Every labelable row put in its strata — a row can be in both."""
    service, irony, both, bots, weak = [], [], [], [], []
    per_signal = dict.fromkeys(SERVICE, 0)
    top = 0
    for row in pool:
        text = row["text"]
        hits = [name for name, pattern in SERVICE.items() if pattern.search(text)]
        for name in hits:
            per_signal[name] += 1
        points = score(text)[0]
        top = max(top, points)
        if points:
            weak.append(row)
        ironic = points >= IRONY_STRONG
        if hits:
            service.append(row)
        if ironic:
            irony.append(row)
        if hits and ironic:
            both.append(row)
        if BOT.match(text):
            bots.append(row)
    general = [
        row
        for row in pool
        if not any(pattern.search(row["text"]) for pattern in SERVICE.values())
        and score(row["text"])[0] < IRONY_STRONG
    ]
    return {
        "service-rich": len(service),
        "sarcasm-rich": len(irony),
        "any irony signal at all": len(weak),
        "highest irony score in the pool": top,
        "in both": len(both),
        "general": len(general),
        "of the general pool, bot participation markers": len(bots),
        "service signals (a row can fire several)": per_signal,
    }


def heuristic_against_the_probe() -> dict | None:
    """What the keyword sweep would have said about the 50 rows a model re-labelled.

    Fifty rows decide nothing, and this is the only place in the project where a
    `service` label and a raw text sit next to each other. Reported as a caveat on
    the counts above, never as a validation of them.
    """
    if not PROBE_ROWS.exists():
        return None
    rows = load(PROBE_ROWS)
    fires = [any(pattern.search(row["text"]) for pattern in SERVICE.values()) for row in rows]
    labelled = ["service" in row["intents"] for row in rows]
    hit = sum(1 for f, s in zip(fires, labelled) if f and s)
    return {
        "rows": len(rows),
        "labelled service": sum(labelled),
        "heuristic fires": sum(fires),
        "both": hit,
        "recall": hit / sum(labelled) if any(labelled) else 0.0,
        "precision": hit / sum(fires) if any(fires) else 0.0,
    }


def growth(steps: dict) -> dict:
    """How fast the ceiling rises on its own — the tiers need this to mean anything.

    Only two channels in the registry have comments enabled
    (`data/entry_check_report.json`), and both are backfilled to their oldest
    reachable post, so the pool grows at the rate the two threads are written.
    """
    months: dict[str, int] = {}
    for source in sorted(RAW.glob("*.jsonl")):
        for record in load(source):
            months[record["date"][:7]] = months.get(record["date"][:7], 0) + 1
    recent = sorted(months)[-4:-1]  # the last three complete months
    per_month = sum(months[month] for month in recent) / len(recent)
    with_text = steps["corpus"] - steps["no text (media only)"]
    free = with_text - steps["already labelled"] - steps["in a test or holdout thread"]
    # A future month is charged for the two exclusions that will apply to it — no
    # text, and a text somebody already said — and not for the evaluation threads,
    # which sit under posts that are already in the past.
    fresh_share = (with_text / steps["corpus"]) * (steps["labelable pool"] / free)
    return {
        "comments per month (last 3 complete)": round(per_month, 1),
        "months": {month: months[month] for month in recent},
        "labelable share, this corpus": round(
            steps["labelable pool"] / (steps["corpus"] - steps["already labelled"]), 3
        ),
        "labelable share, a fresh month": round(fresh_share, 3),
        "labelable rows per month": round(per_month * fresh_share, 1),
    }


def calibration() -> dict:
    """Sample sizes and operator hours for the two calibrations, per tier.

    The sample does not grow with the tier and the hours barely move: what a bigger
    appetite buys is more *rows*, and what it risks is more rows to redo if a
    stratum misses the bar. That asymmetry is the finding, so it is printed rather
    than hidden inside a total.
    """
    low, high = RATE_BAND

    def hours(rows: int) -> dict:
        return {
            "rows": rows,
            "hours": rows / REVIEW_ROWS_PER_HOUR,
            "band_hours": [rows / high, rows / low],
        }

    relabel_rows = CALIBRATION_SAMPLE + CALIBRATION_SAMPLE // 2
    return {
        "bar": AGREEMENT_BAR,
        "sample": CALIBRATION_SAMPLE,
        "rate_rows_per_hour": REVIEW_ROWS_PER_HOUR,
        "rate_band": list(RATE_BAND),
        "precision_at_n100_pp": 5.9,  # 1.96 * sqrt(0.9 * 0.1 / 100), the 95% band at the bar
        "relabel": {
            "gated": hours(CALIBRATION_SAMPLE),
            "with the changed-row diagnostic": hours(relabel_rows),
        },
        "uplabel": {f"+{tier // 1000}k": hours(CALIBRATION_SAMPLE * len(STRATA)) for tier in TIERS},
        "second round if a stratum misses the bar": hours(CALIBRATION_SAMPLE),
    }


def tier_table(counts: dict) -> list[dict]:
    """Whether each tier is reachable, and out of which strata."""
    service, irony, both = counts["service-rich"], counts["sarcasm-rich"], counts["in both"]
    targeted = service + irony - both
    rows = []
    for tier in TIERS:
        rows.append(
            {
                "tier": f"+{tier // 1000}k",
                "rows": tier,
                "from the targeted strata": min(tier, targeted),
                "from the general pool": max(0, tier - targeted),
                "reachable": tier <= targeted + counts["general"],
            }
        )
    return rows


def render(record: dict) -> str:
    """The tables the plan quotes — generated once, so the doc cannot drift."""
    out = ["| step | rows |", "|---|---|"]
    for name, value in record["funnel"].items():
        prefix = "**" if name in ("corpus", "labelable pool") else ""
        out.append(f"| {prefix}{name}{prefix} | {prefix}{value}{prefix} |")

    counts = record["strata"]
    out += ["", "| stratum | rows | heuristic |", "|---|---|---|"]
    out.append(f"| service-rich | {counts['service-rich']} | UA+RU keywords, 6 groups |")
    out.append(f"| sarcasm-rich | {counts['sarcasm-rich']} | `market_pulse.sarcasm` score >= 3 |")
    out.append(
        f"| ... any irony signal at all | {counts['any irony signal at all']} |"
        f" score >= 1; the pool's highest is {counts['highest irony score in the pool']} |"
    )
    out.append(f"| in both | {counts['in both']} | — |")
    out.append(f"| general (neither) | {counts['general']} | — |")
    out.append(
        f"| ... of which bot `+` markers | {counts['of the general pool, bot participation markers']}"
        " | `unclear` by rule, never labelled |"
    )

    out += ["", "| tier | rows | from the targeted strata | from the general pool | reachable |"]
    out.append("|---|---|---|---|---|")
    pool = record["funnel"]["labelable pool"]
    rate = record["growth"]["labelable rows per month"]
    for row in record["tiers"]:
        short = row["rows"] - pool
        out.append(
            f"| {row['tier']} | {row['rows']} | {row['from the targeted strata']} |"
            f" {row['from the general pool']} |"
            f" {'yes' if row['reachable'] else f'NO — {short} short, ~{short / rate:.1f} months'} |"
        )

    plan = record["calibration"]
    out += ["", "| calibration | rows to review | operator hours |", "|---|---|---|"]
    out.append(
        f"| re-label, gated sample | {plan['relabel']['gated']['rows']} |"
        f" {plan['relabel']['gated']['hours']:.1f} |"
    )
    out.append(
        "| re-label, + changed-row diagnostic |"
        f" {plan['relabel']['with the changed-row diagnostic']['rows']} |"
        f" {plan['relabel']['with the changed-row diagnostic']['hours']:.1f} |"
    )
    for tier, entry in plan["uplabel"].items():
        out.append(
            f"| up-label {tier}, {len(STRATA)} strata | {entry['rows']} | {entry['hours']:.1f} |"
        )
    second = plan["second round if a stratum misses the bar"]
    out.append(f"| second round if a stratum misses | {second['rows']} | {second['hours']:.1f} |")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)

    pool, steps = funnel()
    counts = classify(pool)
    record = {
        "funnel": steps,
        "strata": counts,
        "growth": growth(steps),
        "tiers": tier_table(counts),
        "calibration": calibration(),
        "heuristic_vs_probe": heuristic_against_the_probe(),
        "sources": {
            "corpus": sorted(str(p.relative_to(REPO_ROOT)) for p in RAW.glob("*.jsonl")),
            "labelled": [str(p.relative_to(REPO_ROOT)) for p in LABELLED],
            "evaluation threads from": [str(p.relative_to(REPO_ROOT)) for p in EVALUATION],
        },
        "note": "Counts and overlaps only — nothing here labels a row.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(render(record))
    print("\nservice signals, rows firing each (a row can fire several):")
    for name, count in counts["service signals (a row can fire several)"].items():
        print(f"  {name:<28}{count:>6}")
    if check := record["heuristic_vs_probe"]:
        print(
            f"\nthe keyword sweep against the {check['rows']} re-labelled probe rows:"
            f" recall {check['recall']:.0%} ({check['both']}/{check['labelled service']}),"
            f" precision {check['precision']:.0%} ({check['both']}/{check['heuristic fires']})"
            " — 50 rows, a caveat and not a validation"
        )
    print(f"\nwrote {args.out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
