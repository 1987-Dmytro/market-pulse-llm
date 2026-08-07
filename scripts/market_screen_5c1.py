#!/usr/bin/env python3
"""Which market does a source sell into? ($0, offline, report-only.)

Canon: `docs/SPEC.md` §3.11 (4), "Market-origin screen" (operator ruling 2026-08-08) — the gate
REQUIRES UA-market evidence and excludes RF-market channels **regardless of language**, because
RU-language is not RF: Ukrainian consumers write in Russian. So the discriminators are market
FACTS — currency in price posts, retailer names, locations, domains, the RF legal-regime
disclaimers — and never the alphabet. The language question is
`scripts/language_census_5c1.py`'s, and the two answer different things about the same window.

This screen is REPORT-ONLY. It writes its record and nothing else: no exclusion, no registry
edit, no Telegram. Every flag goes to the operator, who rules.

**The evidence is a quoted line, never a counter.** A count cannot be checked and a substring
match is not a finding: `grep -i "сочи"` matches «просочився» — *soaked through*, in a Ukrainian
recipe — in three innocent feeds. Every hit here carries the line it came from and the term that
matched it, so a wrong one is visible at a glance rather than hidden inside a number.

    PYTHONPATH=src python3 scripts/market_screen_5c1.py
"""

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import language_census_5c1 as census  # noqa: E402
from build_audit_pack import git_state  # noqa: E402

from market_pulse.registry import load_registry  # noqa: E402

REGISTRY = REPO_ROOT / "config" / "registry.yaml"
RECORD = REPO_ROOT / "results" / "market_screen_5c1.json"

EXAMPLE_LIMIT = 4
LINE_CHARS = 180

SIGNALS: dict[str, dict[str, tuple[tuple[str, str], ...]]] = {
    # (name, pattern). Every pattern is anchored on word boundaries or a symbol, because the
    # failure mode this screen exists to avoid is a substring that reads like a finding.
    "ua": {
        "currency": (
            ("грн", r"\bгрн\b\.?"),
            ("₴", r"₴"),
            ("гривня", r"\bгривн[іяею]\b|\bгривень\b"),
            ("UAH", r"\bUAH\b"),
        ),
        "retailer": (
            ("АТБ", r"\bАТБ\b"),
            ("Сільпо", r"\bСільпо\b|\bСилпо\b"),
            ("Varus", r"\bVarus\b|\bВарус\b"),
            ("Novus", r"\bNovus\b|\bНовус\b"),
            ("Фора", r"\bФора\b"),
            ("ЕКО Маркет", r"\bЕКО[ -]?Маркет\b"),
            ("Епіцентр", r"\bЕпіцентр\b|\bЭпицентр\b"),
            ("Rozetka", r"\bRozetka\b|\bРозетка\b"),
        ),
        "location": (
            ("Київ", r"\bКиїв\w*\b|\bКиев\w*\b"),
            ("Львів", r"\bЛьвів\w*\b|\bЛьвов\w*\b"),
            ("Одеса", r"\bОдес[аиіыу]\w*\b"),
            ("Харків", r"\bХарків\w*\b|\bХарьков\w*\b"),
            ("Дніпро", r"\bДніпр[оа]\b|\bДнепр[оа]?\b"),
            ("Полтава", r"\bПолтав\w*\b"),
            ("Кременчук", r"\bКременчу[кг]\w*\b"),
        ),
        "domain": (("*.ua", r"\b[\w-]+\.ua\b"),),
        "phone": (("+380", r"\+380"),),
    },
    "rf": {
        "currency": (
            ("₽", r"₽"),
            ("руб", r"\bруб\b\.?|\bрубл(?:ь|я|ей|и|ями)\b"),
            ("RUB", r"\bRUB\b"),
        ),
        "retailer": (
            # SPEC names these three; the rest are the same class of fact. `Лента` is deliberately
            # absent — it is an ordinary word in a recipe («стрічка/лента») and would flag on food.
            ("Пятёрочка", r"\bПят[ёе]рочк\w*\b"),
            ("Магнит", r"\bМагнит\w*\b"),
            ("Перекрёсток", r"\bПерекр[ёе]сток\w*\b"),
            ("ВкусВилл", r"\bВкус[Вв]илл\w*\b"),
            ("Дикси", r"\bДикси\b"),
            ("Wildberries", r"\bWildberries\b|\bВайлдберриз\b"),
            ("Ozon", r"\bOzon\b|\bОзон\b"),
            ("Яндекс Еда/Лавка/Маркет", r"\bЯндекс[ .]?(?:Еда|Еды|Лавк\w*|Маркет)\b"),
            ("Красное&Белое", r"\bКрасное\s*[&и]\s*Белое\b"),
            ("Светофор", r"\bСветофор\b"),
        ),
        "location": (
            # `\b` is what separates «Сочи» from «просочився»: the trap that made this rule.
            ("Сочи", r"\bСочи\b"),
            ("Красная Поляна", r"\bКрасн(?:ая|ой|ую) Полян\w*\b"),
            ("Москва", r"\bМоскв[аеуыой]\b|\bМоскве\b"),
            ("Санкт-Петербург", r"\bСанкт-Петербург\w*\b|\bСПб\b"),
            ("Екатеринбург", r"\bЕкатеринбург\w*\b"),
            ("Новосибирск", r"\bНовосибирск\w*\b"),
            ("Краснодар", r"\bКраснодар\w*\b"),
            ("Ростов-на-Дону", r"\bРостов[- ]на[- ]Дону\b"),
        ),
        "domain": (("*.ru", r"\b[\w-]+\.ru\b"), (".рф", r"\b[\w-]+\.рф\b")),
        "disclaimer": (
            ("запрещён в РФ", r"запрещ[её]н\w*\s+(?:на территории\s+)?(?:РФ|России)"),
            ("иноагент", r"\bиноагент\w*\b|признан\w*\s+иностранным агентом"),
            ("экстремистская", r"\bэкстремистск\w*\b"),
        ),
    },
}
"""What counts as evidence, per side, per signal.

Deliberately NOT here: the country's own name and the bare «РФ». A Ukrainian channel writes both
constantly — about the war, not about a market — and a screen that flags every news mention
answers a different question than the one SPEC asks. What stays is concrete: what you pay with,
where you shop, where you are, what domain you link, and the disclaimers only an RF publisher
carries."""

CONTROLS = {
    # Pre-registered before the run, with the direction each must come back in. Two channel-level
    # and two row-level, plus the negative control that made the rule: a Ukrainian recipe line
    # containing «просочився» must produce NO RF hit at all.
    "@offspringrus": "RF_FLAG",
    "@dpssgovua": "UA_EVIDENCE",
}
ROW_CONTROLS = (
    ("@tretyakovaele", "Сочи", "rf"),
    ("@retsepty5", "Яндекс", "rf"),
)
TRAP_LINE = "Поставити салат у холодильник на 1–2 години, щоб добре просочився"
"""Verbatim from data/raw/posts/mameni_recepti.jsonl — the line a substring screen calls Sochi."""

COMPILED = {
    side: tuple(
        (signal, term, re.compile(pattern))
        for signal, terms in signals.items()
        for term, pattern in terms
    )
    for side, signals in SIGNALS.items()
}


def hits_in(text: str) -> dict[str, list[dict]]:
    """Every market fact in one post, each carrying the line it was found in."""
    found: dict[str, list[dict]] = {"ua": [], "rf": []}
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    for side, patterns in COMPILED.items():
        for signal, term, pattern in patterns:
            for line in lines:
                if match := pattern.search(line):
                    found[side].append(
                        {
                            "signal": signal,
                            "term": term,
                            "matched": match.group(0),
                            "line": " ".join(line.split())[:LINE_CHARS],
                        }
                    )
                    break  # one line per term per post: evidence, not a tally
    return found


def verdict_for(rf: list[dict], ua: list[dict]) -> str:
    """RF evidence outranks UA evidence, and neither is a silent pass.

    SPEC §3.11 (4): the gate REQUIRES UA-market evidence and excludes RF-market channels, with
    ambiguity going to the operator. So a source carrying both is FLAGGED rather than averaged —
    the operator reads the lines and rules — and a source carrying neither cannot be certified.
    """
    if rf:
        return "RF_FLAG"
    return "UA_EVIDENCE" if ua else "NO_EVIDENCE"


def screen_source(handle: str, since: str) -> dict:
    posts = census.posts_in_window(handle, since)
    rf: list[dict] = []
    ua: list[dict] = []
    rf_posts = ua_posts = 0
    for row in posts:
        found = hits_in(row.get("text") or "")
        rf_posts += bool(found["rf"])
        ua_posts += bool(found["ua"])
        for side, bucket in (("rf", rf), ("ua", ua)):
            for hit in found[side]:
                if len(bucket) < EXAMPLE_LIMIT and hit["term"] not in {h["term"] for h in bucket}:
                    bucket.append({**hit, "msg_id": row.get("msg_id"), "date": row.get("date")})
    return {
        "handle": handle,
        "posts_in_window": len(posts),
        "posts_with_rf_evidence": rf_posts,
        "posts_with_ua_evidence": ua_posts,
        "verdict": verdict_for(rf, ua),
        "rf_evidence": rf,
        "ua_evidence": ua,
    }


def run_controls(since: str) -> dict:
    """The screen's exam, taken before its verdicts are read."""
    out = {}
    for handle, expected in CONTROLS.items():
        measured = screen_source(handle, since)
        out[handle] = {
            "kind": "channel",
            "expected": expected,
            "measured": measured["verdict"],
            "evidence": (measured["rf_evidence"] or measured["ua_evidence"])[:2],
            "ok": measured["verdict"] == expected,
        }
    for handle, marker, side in ROW_CONTROLS:
        rows = [
            row
            for row in census.posts_in_window(handle, since)
            if marker in (row.get("text") or "")
        ]
        hits = [hit for row in rows for hit in hits_in(row.get("text") or "")[side]]
        out[f"{handle} :: {marker}"] = {
            "kind": "row",
            "expected": f"{side} evidence in the row the operator cited",
            "rows_found": len(rows),
            "evidence": hits[:2],
            "ok": bool(rows) and bool(hits),
        }
    trap = hits_in(TRAP_LINE)
    out["negative control :: просочився"] = {
        "kind": "negative",
        "expected": "no RF evidence — «просочився» is not «Сочи»",
        "line": TRAP_LINE,
        "evidence": trap["rf"],
        "ok": not trap["rf"],
    }
    return out


def print_table(rows: list[dict]) -> None:
    header = f"{'channel':<30}{'posts':>6}{'rf':>5}{'ua':>5}  verdict / first evidence"
    print(f"\n{header}\n{'-' * len(header)}")
    for row in rows:
        first = (row["rf_evidence"] or row["ua_evidence"] or [{}])[0]
        shown = f"{first.get('term', '—')}: {first.get('line', '')}" if first else "—"
        print(
            f"{row['handle'][:29]:<30}{row['posts_in_window']:>6}"
            f"{row['posts_with_rf_evidence']:>5}{row['posts_with_ua_evidence']:>5}  "
            f"{row['verdict']:<13}{shown[:70]}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=RECORD, help="where to write the record")
    parser.add_argument("--only", metavar="HANDLE", nargs="+", help="screen only these handles")
    args = parser.parse_args(argv)

    since = census.window_since()
    registry = load_registry(REGISTRY)
    handles = [handle for source in registry.sources for handle in source.telegram_channels]
    if args.only:
        if missing := set(args.only) - set(handles):
            raise SystemExit(f"--only names handles the registry does not carry: {sorted(missing)}")
        handles = [handle for handle in handles if handle in args.only]

    segment = {
        handle: source.audience
        for source in registry.sources
        for handle in source.telegram_channels
    }
    rows = [{**screen_source(handle, since), "audience": segment[handle]} for handle in handles]
    order = {"RF_FLAG": 0, "NO_EVIDENCE": 1, "UA_EVIDENCE": 2}
    rows.sort(key=lambda r: (order[r["verdict"]], -r["posts_with_rf_evidence"]))

    controls = run_controls(since)
    reportable = all(control["ok"] for control in controls.values())
    by_verdict: dict[str, int] = {}
    for row in rows:
        by_verdict[row["verdict"]] = by_verdict.get(row["verdict"], 0) + 1

    record = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "phase": "5c1 day-2 pre-flight",
        "asks": "which market does each source sell into — a question about facts, not language",
        "contract": "docs/SPEC.md §3.11 (4), 'Market-origin screen' (operator ruling 2026-08-08)",
        "report_only": (
            "no exclusion, no registry edit, no Telegram. Every flag goes to the operator, who"
            " rules; this screen never removes a source"
        ),
        "window": {"since": since, "source": "data/raw/posts/, the window of collect_5c1.json"},
        "rules": {
            "verdicts": {
                "RF_FLAG": "at least one RF market fact, quoted",
                "UA_EVIDENCE": "UA market facts and no RF one",
                "NO_EVIDENCE": "neither — the gate's «REQUIRES UA evidence» is unmet, which is a"
                " finding about the channel's posts, not a verdict about its market",
            },
            "evidence": "a quoted line with the term that matched it, never a counter",
            "signals": {side: sorted(signals) for side, signals in SIGNALS.items()},
            "deliberately_excluded": (
                "the country's own name and the bare «РФ» — a Ukrainian channel writes both about"
                " the war, not about a market"
            ),
        },
        "controls": controls,
        "verdicts_reportable": reportable,
        "summary": {"n": len(rows), "by_verdict": by_verdict},
        "sources": rows,
        "git": git_state(args.out),
    }
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print_table(rows)
    print(f"\n{len(rows)} sources · " + " · ".join(f"{k} {v}" for k, v in by_verdict.items()))
    for name, control in controls.items():
        print(f"control {name:<34}{'OK' if control['ok'] else 'FAILED'} — {control['expected']}")
    shown = args.out.relative_to(REPO_ROOT) if args.out.is_relative_to(REPO_ROOT) else args.out
    print(f"\nwrote {shown}")
    if not reportable:
        print("STOP: a control came back wrong, so the verdict column is not reportable.")
        return 1
    print("REPORT ONLY: every flag is the operator's to rule, and nothing here removes a source.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
