#!/usr/bin/env python3
"""The README's «Results» block, from result files — regenerated, never typed.

    PYTHONPATH=src python3.11 scripts/build_readme_results.py        # rewrites README.md between the markers

Ruling 06.09 (cc) addendum, «ship as measured»: the S2 numbers go into the README with their files,
and the README fails loudly when a file is missing. The block is the same holdout readings the
screen prints — the product's own pipeline first since ruling 08.09 (dd), the three raw-answer
readings under it — read by the same function, `build_promo_screen.s2_readings`, and closed by the
same sentence, `build_promo_screen.S2_BOUNDARY`, so the README and the screen cannot disagree about
a number or about what separates the shipped row from the readings. A missing source is that
reader's own named refusal; missing markers are this script's. Running it twice writes the same
bytes: nothing here reads a clock.

PHASE-ship-1 §1 (c) makes the README the product's front page, and a front page carries figures:
what the instrument holds, the S1 bar, the S2 readings, and the fine-tuned model beside the base it
was trained from. All four sections are written HERE, between one pair of markers, for the reason
the S2 block already existed — a figure typed into prose is a figure no file can move
([[the_cheap_file_gets_the_expected_number]]), and every row names the file and the field it was
read from. The base-vs-fine-tune table is the v3 RE-SCORES (`results/rescores_v3.json`): base and
both fine-tune arms scored against ONE gold version, which is the only comparison that is a
comparison — the shipped 4.5h2 verdict is a different test set and is quoted as its own line
([[a_settlement_and_its_reference_measure_different_kinds]]).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_promo_screen as screen  # noqa: E402

README = REPO_ROOT / "README.md"
START = (
    "<!-- RESULTS — written by scripts/build_readme_results.py from the result files each row"
    " names; regenerate with `make promo-screen`, never edit -->"
)
END = "<!-- /RESULTS -->"

FRONT = "front_data.json"
GRADE = "grade_positions_50.json"
RESCORES = "rescores_v3.json"
VERDICT = "verdict_45h2.json"
WEEKLY = "weekly"


def load(path: Path) -> dict | list:
    """A source of this block, or the same kind of named refusal every reader here makes."""
    if not path.exists():
        raise SystemExit(
            f"build-readme REFUSED: missing {path.relative_to(REPO_ROOT)} — the README prints"
            " figures out of result files and writes no partial block"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def holdings(results: Path) -> list[str]:
    """«What the instrument holds today» — the populations the app shows, each naming its field.

    Every source is resolved under the SAME `results` directory the S2 rows are read from: the
    two halves of one block may not come from two trees, which is what `--results` would have
    done while the console line claimed one ([[two_values_for_one_input_get_quoted_kindly]]).
    """
    front = load(results / FRONT)
    positions = front["positions"]
    threads = front["status"]["threads"]
    reactions = front["reactions_v2"]
    region = front["region"]
    weekly = results / WEEKLY
    weeks = sorted(path.name for path in weekly.glob("positions_*.jsonl"))
    if not weeks:
        raise SystemExit(
            f"build-readme REFUSED: no positions_<ISO-week>.jsonl under {weekly} — the weekly row"
            " is a count over those files and an empty glob has nothing to count"
        )
    weekly_rows = sum(
        len([line for line in (weekly / name).read_text(encoding="utf-8").splitlines() if line])
        for name in weeks
    )
    screen_rows = len(load(results / screen.EXPORT.name)["screen"]["positions"])
    money = front["status"]["money"]
    rows = [
        (
            "promo positions on the screen",
            f"{screen_rows}",
            "`results/promo_screen_data.json` :: screen.positions",
        ),
        (
            "positions in the table, page-true",
            f"{len(positions['rows'])} · {positions['excluded']['n']} excluded"
            f" ({positions['corrected']} corrected by leaflet page)",
            "`results/front_data.json` :: positions",
        ),
        (
            "promo threads read for reactions",
            f"{threads['read']} of {threads['product_population']} · {threads['queue']} queued",
            "`results/front_data.json` :: status.threads",
        ),
        (
            "signal rows under those threads",
            f"{reactions['rows']}",
            "`results/front_data.json` :: reactions_v2",
        ),
        (
            "weeks in the committed dataset",
            f"{len(weeks)} ({weeks[0].split('_')[1].split('.')[0]}–"
            f"{weeks[-1].split('_')[1].split('.')[0]}) · {weekly_rows} rows counted over them",
            "`results/weekly/positions_<ISO-week>.jsonl`",
        ),
        (
            "Poltava-region channels watched",
            f"{region['totals']['channels']} · {region['totals']['posts']} posts ·"
            f" {region['totals']['comments']} comments",
            "`results/front_data.json` :: region.totals",
        ),
        (
            "region comment sample",
            f"{region['sample']['threads_read']} of {region['sample']['threads_total']} threads"
            f" · {region['sample']['outstanding']} outstanding",
            "`results/region_collect_report.json` :: totals",
        ),
        (
            "watchlist mentions in the region",
            f"{region['totals']['mentions']} — the baseline, not an empty screen",
            "`results/front_data.json` :: region.totals.mentions",
        ),
        (
            "money spent in the current cycle",
            f"${money['spent_usd']:.4f} of the ${money['cap_usd']:.2f} cap",
            # Two fields, and they do NOT live in one place: the spend is the ledger's last session
            # row, the cap is a top-level field of the same file. One citation covering both would
            # send a reader into `sessions[-1]` for a cap that is not there.
            f"`{money['from']}.spent_usd` · `cycle3_cap_usd`",
        ),
    ]
    lines = [
        "**What the instrument holds today.** Every figure is a field of the file beside it —"
        " the weekly row the one count, over the files its pattern names.",
        "",
        "| what | value | file :: field |",
        "|---|---|---|",
    ]
    lines += [f"| {what} | {value} | {source} |" for what, value, source in rows]
    return lines


def s1(results: Path) -> list[str]:
    """The S1 bar — published as measured, RED, with the two limits the grade file carries."""
    grade = load(results / GRADE)
    completeness = grade["bars"]["completeness"]
    accuracy = grade["bars"]["price_accuracy"]
    readings = grade["readings"]
    return [
        "**S1 — positions read off leaflet pages, graded on the team lead's blind gold.** The bar"
        " is RED and ships RED: the reader finds a quarter of the rows a human finds on the same"
        " pages, and prices what it does find.",
        "",
        "| reading | value | bar | file |",
        "|---|---|---|---|",
        f"| completeness | {completeness['value']:.4f} ({completeness['matched']}/"
        f"{completeness['gold']}) {'✅' if completeness['held'] else '❌'} |"
        f" {completeness['bar']:.2f} | `results/grade_positions_50.json` :: bars.completeness |",
        f"| promo-price accuracy | {accuracy['value']:.4f} ({accuracy['right']}/"
        f"{accuracy['scored']}) {'✅' if accuracy['held'] else '❌'} | {accuracy['bar']:.2f} |"
        " `results/grade_positions_50.json` :: bars.price_accuracy |",
        "",
        f"Gold rows no prediction reached: {readings['gold_rows_no_prediction_reached']}."
        f" Predicted rows no gold row claims: {readings['predicted_rows_no_gold_row_claims']}."
        f" The gold is `{grade['gold']}`, written blind by the team lead.",
    ]


def model(results: Path) -> list[str]:
    """Base vs fine-tune on ONE gold version, and the shipped verdict as its own line.

    The gate rows are selected by their METRIC, never by their position in the list: `G1d` appears
    twice (post_type, then relevance beside it) and an index would silently print the second one
    ([[a_block_selected_by_ordinal_runs_the_wrong_block]]). The «one gold version» in the sentence
    is CHECKED across the records rather than read off the first of them, for the same reason: the
    whole claim of the table is that its columns compare.
    """
    rescores = load(results / RESCORES)
    verdict = load(results / VERDICT)
    golds = {record["gold_version"] for record in rescores}
    if len(golds) != 1:
        raise SystemExit(
            f"build-readme REFUSED: {results / RESCORES} carries {sorted(golds)} — the table's"
            " claim is that one gold scored every row, and rows from two golds do not compare"
        )
    names = {
        None: "base — zero-shot, no training",
        "real-only": "fine-tune, real data only",
        "with-synthetic": "fine-tune + synthetic sarcasm",
    }

    def gate(record: dict, name: str, metric: str = "") -> str:
        """One cell. A gate the record does not carry at all is a REFUSAL, not a dash: «—» is the
        file's own «not computable here» (G1b needs a fine-tune) and the two may not look alike."""
        for entry in record["gates"]:
            if entry["gate"] != name or (metric and metric not in entry["metric"]):
                continue
            if "values" in entry:
                return f"{entry['values']['overall']:.4f}"
            return "—" if entry.get("value") is None else f"{entry['value']:.4f}"
        raise SystemExit(
            f"build-readme REFUSED: the {record['arm'] or 'base'} row of {results / RESCORES}"
            f" carries no {name}{' ' + metric if metric else ''} — a column the file cannot fill"
            " is not a dash"
        )

    lines = [
        "**The model: the fine-tune beside the base it was trained from.** One gold version for"
        f" every row ({golds.pop()}), so the columns compare; every value is"
        " `results/rescores_v3.json`'s own field.",
        "",
        "| arm | sentiment macro-F1 | sarcasm fix-rate | intents micro-F1 | post_type macro-F1 |"
        " brand F1 |",
        "|---|---|---|---|---|---|",
    ]
    for record in rescores:
        lines.append(
            f"| {names.get(record['arm'], record['arm'])} | {gate(record, 'G1a')} |"
            f" {gate(record, 'G1b')} | {gate(record, 'G1c')} |"
            f" {gate(record, 'G1d', 'post_type')} | {gate(record, 'G1e')} |"
        )
    lines += [
        "",
        f"The shipped decision was taken at step {verdict['step']} on test set"
        f" {verdict['testset_version']} — a LATER gold than the table above, so its numbers are not"
        f" this table's: {verdict['passed']} of {verdict['of']} gates held"
        f" (`results/verdict_45h2.json` :: verdicts), and the app's Методологія tab prints the same"
        " line. The model is `google/gemma-4-31b-it` + a QLoRA adapter, run on a rented GPU.",
    ]
    return lines


def block(rows: list[dict]) -> str:
    """The markdown the markers enclose: one row per reading, the boundary, then the tie count.

    The two bars in the opening sentence are READ off the first reading's record like every other
    number here — typing «0.80» would put a threshold in prose, where no file can move it
    ([[a_threshold_that_lives_in_prose]]); each row's own cell still carries its own file's bar.
    The tie sentence follows the row `S2_SOURCES` flags, which ruling 08.09 (dd) item 6 pins to the
    P1 reading — the loop record carries a tie count of its own and printing both, unlabelled,
    would read as one set counted twice. It NAMES that row, for the same reason: a count printed
    under a four-row table attaches itself to whichever row the reader was looking at
    ([[a_published_number_has_one_reader]]).
    """
    bars = rows[0]["bars"]
    lines = [
        "**S2 — reactions under promo posts, graded on the frozen holdouts.** Per comment: what it"
        f" is about (subject, bar {bars['subject_agreement']['bar']:.2f}); per thread: what it says"
        f" (signal types, bar {bars['signal_type_agreement']['bar']:.2f}). Shipped as"
        " measured (ruling 06.09 (cc)); every number below is the named file's.",
        "",
        "| reading | subject | signal | file |",
        "|---|---|---|---|",
    ]
    for row in rows:
        sub, sig = row["bars"]["subject_agreement"], row["bars"]["signal_type_agreement"]
        lines.append(
            f"| {row['label']} | {sub['value']:.4f} ({row['agreed']}/{row['comments']})"
            f" {'✅' if sub['held'] else '❌'} bar {sub['bar']:.2f}"
            f" | {sig['value']:.4f} {'✅' if sig['held'] else '❌'} bar {sig['bar']:.2f}"
            f" | `{row['file']}` :: {row['block']} |"
        )
    lines += ["", screen.S2_BOUNDARY]
    for row in rows:
        if row["misses"]:
            lines += [
                "",
                f"Of the {row['misses']['total']} comments «{row['label']}» still misses,"
                f" {row['misses']['gold_unsure']} are rows the gold itself marked `unsure` — the"
                " codebook allows two readings there (a store-stock complaint: the chain or the"
                " product; a post in the chain's own channel: the chain or the post).",
            ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readme", type=Path, default=README)
    parser.add_argument("--results", type=Path, default=screen.RESULTS)
    args = parser.parse_args(argv)

    text = args.readme.read_text(encoding="utf-8")
    if START not in text or END not in text or text.index(START) > text.index(END):
        raise SystemExit(
            f"build-readme REFUSED: {args.readme} carries no `{END}` block to write into — the"
            " markers are the contract, and a README without them is not edited blind"
        )
    rows = screen.s2_readings(args.results)
    body = "\n\n".join(
        [
            "\n".join(holdings(args.results)),
            "\n".join(s1(args.results)),
            block(rows),
            "\n".join(model(args.results)),
        ],
    )
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    args.readme.write_text(f"{head}{START}\n{body}\n{END}{tail}", encoding="utf-8")
    print(
        f"wrote the results block of {args.readme}: holdings + S1 + {len(rows)} S2 readings"
        f" + base-vs-fine-tune, from {args.results}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
