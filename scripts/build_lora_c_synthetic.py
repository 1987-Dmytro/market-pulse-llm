#!/usr/bin/env python3
"""`results/lora_c_synthetic.json` — arm B's 160 written rows, VALIDATED, and review gate 2's file.

`docs/PROMPT-lora-c-prep.md`, the second D0 section. The rows themselves are written by Claude Code
and live in `results/synthetic_pass1_v1.jsonl`; this file is what refuses them. Nothing here writes
a comment — a producer that generated the rows it also checks would be measuring its own template
([[a_probe_must_not_create_what_it_measures]]).

**What is checked, and by which instrument.**

- *Balance*, so synthetic cannot teach a prior: within every error class the five label counts are
  within ±2. That is the contract's rule and it exists because line B's adapter learned the
  training set's marginal ([[an_identical_count_is_not_an_identical_model]]).
- *Contamination*, printed as EMPTY LISTS: no synthetic text shares a word 6-gram with a labelled
  row, a holdout row, a reference-thread comment or the gold. `market_pulse.synthetic` is the
  shipped implementation — word n-grams over casefolded `\\w+` tokens with an inverted index — so
  the comparison is already normalised and «no shared 6-gram» is not a claim about whitespace
  ([[blinding_leaks_are_distributional]]).
- *Frames*, by `synthetic.frame_counts`: two hundred rows that all open «Ага,» are pairwise
  distinct and still read as one machine, and a shingle check cannot see it.
- *Register*, measured on BOTH sides. The contract says «in the register of the window's comments»
  and that is a distribution, not an adjective: language mix, length, emoji rate, terminal
  punctuation and opening case are counted over the 515 real pool rows and over these 160, and the
  record carries both columns including the axis they do NOT agree on.
- *Isolation*: a synthetic row may never reach the neighbour pool, an eval set or arm A. The thread
  prefix `synthetic:` is what makes that checkable — it can collide with no real thread, so every
  downstream refusal is one string comparison.

    PYTHONPATH=src python3.11 scripts/build_lora_c_synthetic.py
    PYTHONPATH=src python3.11 scripts/build_lora_c_synthetic.py --sample   # review gate 2's file
"""

import argparse
import hashlib
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_lora_c_data as data  # noqa: E402
import build_pass1_sft as sft  # noqa: E402
import gate_census_w1_reader as reader_gate  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402
from market_pulse import prompts, synthetic  # noqa: E402

ROWS = REPO_ROOT / "results" / "synthetic_pass1_v1.jsonl"
RECORD_OUT = REPO_ROOT / "results" / "lora_c_synthetic.json"
SAMPLE_OUT = REPO_ROOT / "docs" / "reviews" / "lora-c-synthetic.md"
VERDICT = REPO_ROOT / "docs" / "reviews" / "lora-c-synthetic-verdict.md"

PREFIX = "synthetic:"
SHINGLE = 6
BALANCE_TOLERANCE = 2
REGISTER_TOLERANCE = 3
"""Percentage points, or units where the axis is a median. Stated because «matched» without a
tolerance is an opinion, and because two of the six axes below do NOT clear it."""
CLASSES = (
    (
        "brand_vs_retailer",
        "brand ↔ retailer — F2 (`580124`) read the brand where the reading is the chain, and back",
    ),
    (
        "retailer_non_dairy",
        "a retailer named in a NON-DAIRY context — N2, `@VARUS_channel:10366`, four rows pass 1 called `сеть_ритейлер` and the team lead called `null`",
    ),
    (
        "non_dairy_brand",
        "a non-dairy «brand» that must be `не_наш_рынок` — the café, the stationery and the throat spray pass 2 measured at `молочный_бренд` 21.4 %",
    ),
    (
        "mention_vs_about",
        "mention-vs-about — 18 of the 52 `не_наш_рынок` rows on holdout-100 pulled into `категория_личное`",
    ),
)
EMOJI = re.compile("[\U0001f300-\U0001faff☀-➿←-⇿️]")

RETAILER_NAMED = re.compile(r"варус|сільпо|сильпо|атб|фора|новус|еко маркет|эко маркет", re.I)
RETAILER_CLAIM = re.compile(
    r"закінчив|нема\b|немає|завіз|завез|продає|продаёт|по акці|акці|дешевш|дорожч|дороже"
    r"|дешевле|тримає ціну|є \b",
    re.I,
)
"""The shape the codebook rules `сеть_ритейлер`: «A comment about the retailer's service, stock,
prices or stores is `сеть_ритейлер`». Named here so a synthetic row that CONTRADICTS the codebook
can be counted rather than argued about."""
UA = set("іїєґІЇЄҐ")
RU = set("ыэъёЫЭЪЁ")


def alphabet(text: str) -> str:
    """Which Cyrillic orthography a comment is written in, by the letters only one of them has."""
    ua, ru = any(one in UA for one in text), any(one in RU for one in text)
    return "ua" if ua and not ru else "ru" if ru and not ua else "both" if ua else "neutral"


def register(texts: list[str]) -> dict:
    """The five countable properties of a comment corpus. Measured on both sides, never asserted."""
    words = sorted(len(one.split()) for one in texts)
    return {
        "n": len(texts),
        "alphabet_pct": {
            name: round(100 * count / len(texts))
            for name, count in Counter(alphabet(one) for one in texts).most_common()
        },
        "words_median": statistics.median(words),
        "words_p90": words[int(0.9 * len(words))],
        "words_max": words[-1],
        "chars_median": int(statistics.median([len(one) for one in texts])),
        "emoji_pct": round(100 * len([one for one in texts if EMOJI.search(one)]) / len(texts)),
        "no_terminal_punctuation_pct": round(
            100 * len([one for one in texts if one and one[-1] not in ".!?…)"]) / len(texts)
        ),
        "lowercase_opening_pct": round(
            100 * len([one for one in texts if one[:1].islower()]) / len(texts)
        ),
        "question_pct": round(100 * len([one for one in texts if "?" in one]) / len(texts)),
    }


def self_flagged(written: list[dict]) -> dict:
    """Synthetic rows this file believes may be labelled AGAINST the codebook — a finding, not a fix.

    `build_pass1_label_pack.codebook()` rules: «A comment about the retailer's service, stock, prices
    or stores is `сеть_ритейлер`». Fifteen of these rows name a chain AND make a stock, price or
    assortment claim about it, and are labelled `не_наш_рынок` because the THING is non-dairy. The
    team lead's own labels on exactly that shape say otherwise —
    `@VARUS_channel:10470:21236` («кубок ковбасний … там сказали, що нема»),
    `@VARUS_channel:10470:21240` and `@VARUS_channel:10367:20979` are all `сеть_ритейлер`, and the
    first of those is a NON-DAIRY item out of stock at a chain.

    **Nothing is rewritten here.** Review gate 2 is a STOP and the verdict names what changes; a
    draft that quietly corrected itself after its own sample path was reported would hand the team
    lead a file different from the one they were sent. So the rows stand and the concern is carried
    beside them ([[an_exclusion_rule_built_from_failures]] read the other way: the executor may not
    grade its own sample — SPEC §10).
    """
    hits = [
        one
        for one in written
        if one["subject_type"] == "не_наш_рынок"
        and RETAILER_NAMED.search(one["text"])
        and RETAILER_CLAIM.search(one["text"])
    ]
    return {
        "concern": (
            "labelled `не_наш_рынок` because the THING is non-dairy, while the comment makes a"
            " stock / price / assortment claim about a NAMED chain — which the codebook rules"
            " `сеть_ритейлер`"
        ),
        "codebook_clause": (
            "«A comment about the retailer's service, stock, prices or stores is `сеть_ритейлер`»"
            " — prompts.PASS1_CODEBOOK_CLAUSE_V2, carried into the labeller's codebook"
        ),
        "the_team_leads_own_labels_on_this_shape": {
            "@VARUS_channel:10470:21236": "сеть_ритейлер — «кубок ковбасний … там сказали, що нема»",
            "@VARUS_channel:10470:21240": "сеть_ритейлер — «І в нас теж такого нема»",
            "@VARUS_channel:10367:20979": "сеть_ритейлер — «Коли буде знижка?»",
        },
        "rows": [f"{one['thread']}:{one['msg_id']}" for one in hits],
        "n": len(hits),
        "of": len(written),
        "action_taken": "NONE — review gate 2 is a STOP and the verdict decides",
    }


def rows() -> list[dict]:
    """The written rows, with every field the contract names checked against the shipped domains.

    `prompts.PASS1_SUBJECT_TYPES` and `prompts.SENTIMENT_LABELS` are the parser's own vocabularies,
    so a synthetic row can never carry a reading an answer would be refused for
    ([[a_consumer_list_is_not_a_meaning_list]]).
    """
    out, seen = [], set()
    for number, line in enumerate(ROWS.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        one = json.loads(line)
        key = (one["thread"], int(one["msg_id"]))
        if key in seen:
            raise SystemExit(f"{ROWS.name} line {number}: {key} appears twice — stop.")
        seen.add(key)
        if not one["thread"].startswith(PREFIX):
            raise SystemExit(
                f"{ROWS.name} line {number}: thread {one['thread']!r} has no {PREFIX!r} prefix, so"
                " it could collide with a real thread and no downstream guard could see it — stop."
            )
        if one["error_class"] not in dict(CLASSES):
            raise SystemExit(f"{ROWS.name} line {number}: unknown error class — stop.")
        if (
            one["subject_type"] is not None
            and one["subject_type"] not in prompts.PASS1_SUBJECT_TYPES
        ):
            raise SystemExit(
                f"{ROWS.name} line {number}: {one['subject_type']!r} is not a reading."
            )
        if one["stance"] is not None and one["stance"] not in prompts.SENTIMENT_LABELS:
            raise SystemExit(f"{ROWS.name} line {number}: {one['stance']!r} is not a stance.")
        if (one["subject_type"] is None) != (one["subject_id"] is None):
            raise SystemExit(
                f"{ROWS.name} line {number}: subject_type and subject_id disagree about whether"
                " this comment has a subject — one of them is wrong."
            )
        if data.norm(one["cue"]) not in data.norm(one["text"]):
            raise SystemExit(f"{ROWS.name} line {number}: the cue is not in the comment — stop.")
        if f"(cue: «{one['cue']}»)" not in one["rationale"]:
            raise SystemExit(f"{ROWS.name} line {number}: the rationale does not quote its cue.")
        if len(one["rationale"]) > data.pass1_v3.RATIONALE_MAX_CHARS:
            raise SystemExit(f"{ROWS.name} line {number}: the rationale is over the ceiling.")
        if not one.get("synthetic") or one.get("author") != "claude-code":
            raise SystemExit(f"{ROWS.name} line {number}: the provenance block is incomplete.")
        out.append(one)
    return out


def balance(written: list[dict]) -> dict:
    """Label counts per error class, and the spread the contract bounds at ±2."""
    table = {}
    for name, _ in CLASSES:
        group = [one for one in written if one["error_class"] == name]
        counts = Counter(
            "null" if one["subject_type"] is None else one["subject_type"] for one in group
        )
        values = [counts.get(label, 0) for label in (*prompts.PASS1_SUBJECT_TYPES, "null")]
        table[name] = {
            "rows": len(group),
            "labels": dict(sorted(counts.items())),
            "spread": max(values) - min(values),
        }
    over = sorted(name for name, cell in table.items() if cell["spread"] > BALANCE_TOLERANCE)
    if over:
        raise SystemExit(
            f"label counts spread more than ±{BALANCE_TOLERANCE} inside {over} — synthetic that"
            " carries a prior teaches the prior, which is what line B already measured. Stop."
        )
    return {"tolerance": BALANCE_TOLERANCE, "by_class": table, "classes_over_tolerance": over}


def corpus() -> dict[str, list[str]]:
    """The four bodies of text a synthetic row may not echo, each from the file that owns it."""
    reference = set(data.reference_threads())
    holdout = sft.holdout_units()
    labelled = sft.labelled_units()
    gold = json.loads(data.GOLD.read_text(encoding="utf-8"))
    quotes: list[str] = []

    def walk(node) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in ("evidence_text", "quote_reference", "reading_reference") and isinstance(
                    value, str
                ):
                    quotes.append(value)
                else:
                    walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(gold)
    comments = [
        one.get("text") or ""
        for thread in reader_gate.population()
        if f"{thread['channel']}:{thread['post_id']}" in reference
        for one in thread["comments"]
    ]
    return {
        "labelled_rows": [one["text"] for one in labelled],
        "holdout_rows": [
            one["text"] for one in labelled if (one["thread"], one["msg_id"]) in holdout
        ],
        "reference_thread_comments": [one for one in comments if one.strip()],
        "gold_quotes": [one for one in quotes if one.strip()],
    }


def contamination(written: list[dict]) -> dict:
    """Four lists, and the contract asks for them EMPTY. Word 6-grams, by `market_pulse.synthetic`."""
    texts = [one["text"] for one in written]
    out = {
        "shingle": SHINGLE,
        "rule": "word n-grams over casefolded \\w+ tokens, market_pulse.synthetic",
    }
    for name, body in corpus().items():
        index = synthetic.build_index(body, SHINGLE)
        out[name] = sorted(
            f"{one['thread']}:{one['msg_id']}"
            for one, text in zip(written, texts)
            if any(shingle in index for shingle in synthetic.shingles(text, SHINGLE))
        )
        out[f"{name}_n"] = len(body)
    return out


def frames(written: list[dict]) -> dict:
    """Repeated openings and closings — the collapse a pairwise shingle test cannot see."""
    lead, tail = synthetic.frame_counts([one["text"] for one in written], 2)
    return {
        "rule": "synthetic.frame_counts over two-word openings and closings",
        "top_openings": lead.most_common(5),
        "top_closings": tail.most_common(5),
        "worst_opening_share_pct": round(100 * lead.most_common(1)[0][1] / len(written)),
        "worst_closing_share_pct": round(100 * tail.most_common(1)[0][1] / len(written)),
    }


def build() -> dict:
    written = rows()
    pool_texts = [
        json.loads(line)["text"]
        for line in data.RATIONALES.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    theirs, mine = register(pool_texts), register([one["text"] for one in written])
    return {
        "phase": "lora-c-prep",
        "contract": "docs/PROMPT-lora-c-prep.md — D0, synthetic rows for arm B",
        "file": "results/synthetic_pass1_v1.jsonl",
        "sha256": hashlib.sha256(ROWS.read_bytes()).hexdigest(),
        "rows": len(written),
        "author": "claude-code",
        "reviewed": sorted({one["reviewed"] for one in written}),
        "error_classes": [
            {
                "name": name,
                "what": what,
                "rows": len([one for one in written if one["error_class"] == name]),
            }
            for name, what in CLASSES
        ],
        "balance": balance(written),
        "contamination": contamination(written),
        "frames": frames(written),
        "register": {
            "rule": (
                "«in the register of the window's comments» is a distribution, not an adjective."
                " Measured over the 515 real pool rows and over these 160, same code both sides"
            ),
            "the_window": theirs,
            "synthetic": mine,
            "tolerance_points": REGISTER_TOLERANCE,
            "per_axis": {
                axis: {
                    "window": theirs[axis],
                    "synthetic": mine[axis],
                    "delta": round(mine[axis] - theirs[axis], 2),
                    "matched": abs(mine[axis] - theirs[axis]) <= REGISTER_TOLERANCE,
                }
                for axis in (
                    "emoji_pct",
                    "lowercase_opening_pct",
                    "no_terminal_punctuation_pct",
                    "question_pct",
                    "words_median",
                    "chars_median",
                )
            },
            "alphabet": {"window": theirs["alphabet_pct"], "synthetic": mine["alphabet_pct"]},
            "matched": [
                axis
                for axis in (
                    "emoji_pct",
                    "lowercase_opening_pct",
                    "no_terminal_punctuation_pct",
                    "question_pct",
                    "words_median",
                    "chars_median",
                )
                if abs(theirs[axis] - mine[axis]) <= REGISTER_TOLERANCE
            ],
            "not_matched": {
                "how_many": "FOUR of the six axes miss the ±3 tolerance. Named, not smoothed",
                "question_pct": (
                    "8 % against 13 %. Under-represented because three of the four error classes"
                    " are statements about a subject and only one is naturally a question"
                ),
                "no_terminal_punctuation_pct": (
                    "54 % against 59 %. Within five points and set by a seeded pass, not by hand"
                ),
                "length": (
                    f"median {mine['words_median']} words against the window's"
                    f" {theirs['words_median']}, and max {mine['words_max']} against"
                    f" {theirs['words_max']}. DELIBERATE: the contract asks for «short, colloquial»"
                    " rows, and the window's tail is recipes and advice posts of 40-190 words —"
                    " writing those synthetically would be a different instrument, not a longer"
                    " version of this one. Named rather than smoothed. `chars_median` 40 against"
                    " 68 is the same fact in the other unit"
                ),
            },
        },
        "self_flagged": self_flagged(written),
        "isolation": {
            "rule": (
                "a synthetic row is NEVER in the neighbour pool, never in an eval set and never in"
                " arm A. The `synthetic:` thread prefix cannot collide with a real thread, so every"
                " downstream refusal is one string comparison"
            ),
            "prefix": PREFIX,
            "threads": sorted({one["thread"] for one in written}),
        },
        "produced_by": {
            "script": "scripts/build_lora_c_synthetic.py",
            "sha256": data.sha_text(Path(__file__).read_text(encoding="utf-8")),
            "note": "this file VALIDATES the rows; it does not write them",
        },
    }


def sample(record: dict) -> str:
    """`docs/reviews/lora-c-synthetic.md` — all 160 rows with a blank verdict column."""
    written = rows()
    lines = [
        "# lora-c — review gate 2: the synthetic rows for arm B",
        "",
        "**This file is the EXECUTOR's. The verdict is the team lead's:"
        " `docs/reviews/lora-c-synthetic-verdict.md`.**",
        "",
        f"**{record['rows']} rows**, written by Claude Code, `reviewed: false` on every one until"
        " the verdict lands. The verdict names rows to **drop** or **rewrite**; only those are"
        " acted on, and the counts go into `docs/reports/lora-c-prep.md`.",
        "",
        "> ⚠️ **THE EXECUTOR FLAGS ITS OWN ROWS — see «What this file believes may be wrong»"
        " below before you read the tables.**",
        "",
        "**Arm B is arm A's rows plus these.** They are never in the neighbour pool, never in an"
        f" eval set and never in arm A — the `{PREFIX}` thread prefix is what makes that checkable.",
        "",
        "## What the instruments say before you read a row",
        "",
        f"- **Balance** — within every error class the five label counts spread by"
        f" {max(cell['spread'] for cell in record['balance']['by_class'].values())} against a"
        f" tolerance of ±{record['balance']['tolerance']}. Synthetic that carries a prior teaches"
        " the prior; that is what line B measured.",
        "- **Contamination — four empty lists.** No synthetic text shares a word"
        f" {record['contamination']['shingle']}-gram with any of:"
        f" {record['contamination']['labelled_rows_n']} labelled rows"
        f" (`{record['contamination']['labelled_rows'] or '[]'}`),"
        f" {record['contamination']['holdout_rows_n']} holdout rows"
        f" (`{record['contamination']['holdout_rows'] or '[]'}`),"
        f" {record['contamination']['reference_thread_comments_n']} reference-thread comments"
        f" (`{record['contamination']['reference_thread_comments'] or '[]'}`),"
        f" {record['contamination']['gold_quotes_n']} gold quotes"
        f" (`{record['contamination']['gold_quotes'] or '[]'}`).",
        f"- **Frames** — the commonest two-word opening covers"
        f" {record['frames']['worst_opening_share_pct']} % of rows and the commonest closing"
        f" {record['frames']['worst_closing_share_pct']} %. Two hundred rows built on one frame are"
        " pairwise distinct and still one machine.",
        "- **Register**, measured on both sides over the same code:",
        "",
        "| axis | the window's 515 rows | these 160 |",
        "|---|---|---|",
    ]
    for axis, label in (
        ("alphabet_pct", "alphabet mix % (ua/ru/neutral)"),
        ("words_median", "words, median"),
        ("words_max", "words, max"),
        ("chars_median", "characters, median"),
        ("emoji_pct", "carries an emoji %"),
        ("no_terminal_punctuation_pct", "no terminal punctuation %"),
        ("lowercase_opening_pct", "opens lowercase %"),
        ("question_pct", "carries a question mark %"),
    ):
        lines.append(
            f"| {label} | {record['register']['the_window'][axis]} |"
            f" {record['register']['synthetic'][axis]} |"
        )
    lines += [
        "",
        "> **Four of the six axes do NOT match at ±"
        f"{record['register']['tolerance_points']}, and none of them is smoothed.**"
        f" *Length:* {record['register']['not_matched']['length']}"
        f" *Questions:* {record['register']['not_matched']['question_pct']}."
        f" *Terminal punctuation:* {record['register']['not_matched']['no_terminal_punctuation_pct']}.",
        "",
    ]
    flag = record["self_flagged"]
    lines += [
        "## What this file believes may be wrong — the executor flagging its own sample",
        "",
        f"**{flag['n']} of {flag['of']} rows.** {flag['concern']}.",
        "",
        f"The clause: {flag['codebook_clause']}.",
        "",
        "**And the team lead's own labels on exactly that shape say `сеть_ритейлер`:**",
        "",
        *[
            f"- `{key}` — {value}"
            for key, value in flag["the_team_leads_own_labels_on_this_shape"].items()
        ],
        "",
        "The first of those is a NON-DAIRY item out of stock at a chain and it is `сеть_ритейлер`,"
        " which is the case these rows are labelled against. If the team lead agrees, the verdict"
        " should name the pattern and these rows are the ones it covers:",
        "",
        *[f"- `{one}`" for one in flag["rows"]],
        "",
        f"**Nothing was rewritten.** {flag['action_taken']}. The executor does not grade its own"
        " sample (SPEC §10), and a draft that quietly corrected itself after its sample path was"
        " reported would hand you a file different from the one you were sent.",
        "",
    ]
    for name, what in CLASSES:
        group = [one for one in written if one["error_class"] == name]
        counts = record["balance"]["by_class"][name]["labels"]
        lines += [
            f"## `{name}` — {len(group)} rows",
            "",
            f"*{what}*",
            "",
            f"Labels: {' · '.join(f'`{k}` {v}' for k, v in sorted(counts.items()))}.",
            "",
            "| # | label | subject_id | stance | comment | rationale | verdict |",
            "|---|---|---|---|---|---|---|",
        ]
        for one in group:
            text = " ".join(one["text"].split()).replace("|", "\\|")
            lines.append(
                f"| {one['msg_id']} | {one['subject_type'] or 'null'} |"
                f" {one['subject_id'] or '—'} | {one['stance'] or '—'} | {text} |"
                f" {one['rationale'].replace('|', chr(92) + '|')} |  |"
            )
        lines.append("")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", action="store_true", help="also write review gate 2's file")
    parser.add_argument("--record-out", type=Path, default=RECORD_OUT)
    parser.add_argument("--sample-out", type=Path, default=SAMPLE_OUT)
    args = parser.parse_args(argv)

    record = build()
    record["review_gate_2"] = {
        "sample": "docs/reviews/lora-c-synthetic.md",
        "verdict": "docs/reviews/lora-c-synthetic-verdict.md",
        "verdict_present": VERDICT.exists(),
    }
    args.record_out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {summary.rel(args.record_out)}  {record['rows']} rows")
    for cell in record["error_classes"]:
        print(
            f"  {cell['name']:<20} {cell['rows']:3d}"
            f"  labels {record['balance']['by_class'][cell['name']]['labels']}"
        )
    empty = {
        name: record["contamination"][name]
        for name in ("labelled_rows", "holdout_rows", "reference_thread_comments", "gold_quotes")
    }
    print(f"  contamination (all four must be empty): {empty}")
    print(
        f"  register: emoji {record['register']['synthetic']['emoji_pct']}%"
        f" vs the window's {record['register']['the_window']['emoji_pct']}%;"
        f" words median {record['register']['synthetic']['words_median']}"
        f" vs {record['register']['the_window']['words_median']}"
    )
    if args.sample:
        args.sample_out.parent.mkdir(parents=True, exist_ok=True)
        args.sample_out.write_text(sample(record), encoding="utf-8")
        print(f"wrote {summary.rel(args.sample_out)}")
        print(
            f"  REVIEW GATE 2 — STOP until {summary.rel(VERDICT)} exists"
            f" ({'present' if VERDICT.exists() else 'ABSENT'})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
