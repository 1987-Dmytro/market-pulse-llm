#!/usr/bin/env python3
"""`docs/REFERENCE-signals-w1.md` → `results/reader_gold_w1.json` — structured, never reinterpreted.

**What is transcribed and what is computed.** The team lead's reading is DATA here: every signal,
every entity case, every noise thread and every msg-id below is his, and :func:`assert_transcribed`
holds each quoted phrase to the reference file itself, whitespace-normalised, so a paraphrase
introduced by the executor fails the build ([[verbatim_quotes_must_be_grepped]]). What the producer
computes is everything the file cannot know about itself: whether each named msg-id exists in the
evidence store, what the store's own text for it is, whether the reference's quote survives in that
text, which thread the store puts it in, and whether the thread is inside the probe's population.

**The store is the truth (D2's own words).** Where the two disagree the record carries BOTH — the
reference's wording under `quote_reference`, the store's under `evidence_text` — and names the
disagreement rather than choosing. Three kinds are already known and are findings for the report,
not edits to a team-lead file: quotes the reference compressed, one msg-id whose thread in the store
is not the thread the reference names, and four threads the gate's own silencers removed from the
population before the reader can ever see them.

**The derivation rules, once, in the record.** A per-comment row is not a second reading: it carries
the subject and the stance of the SIGNAL the reference attributes that msg-id to (plan §3's example
does exactly that), or the reading the reference states for the comment directly, which wins. Where
the reference states neither, the field is `null` — «not stated» — and the scorer does not score it.
жалоба reads negative and похвала positive; спрос, привычка and тренд carry no stance, and inventing
one would be the reinterpretation D2 forbids.

    PYTHONPATH=src python3 scripts/write_reader_gold.py
    PYTHONPATH=src python3 scripts/write_reader_gold.py --out /tmp/again.json   # the pair
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_aggregates as builder  # noqa: E402
import gate_census_w1 as census  # noqa: E402
import reader_population as population  # noqa: E402
import window_summary_5c2 as summary  # noqa: E402

from market_pulse import loop, prompts  # noqa: E402

REFERENCE = REPO_ROOT / "docs" / "REFERENCE-signals-w1.md"
PLAN = REPO_ROOT / "docs" / "PLAN-comment-signals.md"
PRODUCT = REPO_ROOT / "docs" / "PRODUCT.md"
OUT = REPO_ROOT / "results" / "reader_gold_w1.json"

ASPECT_OF = {
    "вкус": "taste",
    "цена": "price",
    "упаковка": "packaging",
    "качество": "quality",
    "наличие": "availability",
    "сервис": "service",
}
"""The reference's aspect words in the six the repo already labels with.

Not a translation chosen here: `docs/PRODUCT.md` question 2 answers itself with exactly these six
Russian words, and `scorer.INTENTS_V2` is exactly these six English ones — the aspect layer the
model already has. The plan's §3 last paragraph is why they must be the same six: the stance layer
ADDS a subject to the existing heads, and «расхождения двух слоёв — отдельная колонка честности» is
impossible between two vocabularies."""

STANCE_OF = {"жалоба": "negative", "похвала": "positive"}
"""The only two signal words that state an attitude. спрос, привычка and тренд do not, and a stance
derived for them would be the executor's reading of the team lead's reading."""

# --- the transcription ----------------------------------------------------------------------------

FLAGSHIPS = [
    {
        "id": "F1",
        "channel": "@VARUS_channel",
        "post_id": 10613,
        "title": "«День морозива»",
        "signals": [
            {
                "id": "F1a",
                "signal_type": "жалоба",
                "subject_type": "сеть_ритейлер",
                "subject_id": "varus",
                "aspect_reference": "качество",
                "evidence": [21626],
                "reading_reference": "холодовая цепь",
                "quote_reference": (
                    "з нього просто тече вода, перемерзше… Повернення робив не один я"
                ),
            },
            {
                "id": "F1b",
                "signal_type": "спрос",
                "subject_type": "категория",
                "subject_id": "морозиво без цукру",
                "aspect_reference": "наличие",
                "evidence": [21599, 21601],
                "reading_reference": "ответ сети с SKU Рудь/Лімо",
                "quote_reference": None,
            },
            {
                "id": "F1c",
                "signal_type": "похвала",
                # the reference states the type and the aspect and no subject at all
                "subject_type": None,
                "subject_id": None,
                "aspect_reference": "вкус",
                "evidence": [21629],
                "reading_reference": None,
                "quote_reference": None,
            },
        ],
    },
    {
        "id": "F2",
        "channel": "@matusi_ukr",
        "post_id": 22303,
        "title": "«Ласунка, склад»",
        "signals": [
            {
                "id": "F2a",
                "signal_type": "жалоба",
                "subject_type": "молочный_бренд",
                "subject_id": "lasunka",
                "aspect_reference": "наличие",
                "evidence": [580124],
                "reading_reference": "рыночное событие (разрушен склад",
                "quote_reference": None,
            }
        ],
        "fork": {
            "msg_id": 580129,
            "subject_type": "категория_личное",
            "quote_reference": "Ніяке не люблю. Хоч ласунка, хоч інше",
            "reading_reference": "НЕ\n  бренд-негатив — обязательная развилка",
        },
    },
    {
        "id": "F3",
        "channel": "@mandziak",
        "post_id": 3676,
        "title": "«пицца из творога»",
        "signals": [
            {
                "id": "F3a",
                "signal_type": "привычка",
                "subject_type": "категория",
                "subject_id": "творог",
                "aspect_reference": None,
                "evidence": [47899, 47902],
                "reading_reference": "упоминание ритейлера при категорийной привычке",
                "quote_reference": "творог нежирний з АТБ, в пачці 300 г, сам такий купляю",
            }
        ],
    },
    {
        "id": "F4",
        "channel": "@mandziak",
        "post_id": 3703,
        "title": None,
        "signals": [
            {
                "id": "F4a",
                "signal_type": "тренд",
                "subject_type": "категория",
                "subject_id": "функциональная молочка",
                "aspect_reference": None,
                "evidence": [48276, 48283],
                "reading_reference": "ежедневный протеиновый коктейль",
                "quote_reference": "добираю білок пудінгами і йогуртами з протеїном",
            }
        ],
    },
    {
        "id": "F5",
        "channel": "@matusi_ukr",
        "post_id": 22272,
        "title": None,
        "signals": [
            {
                "id": "F5a",
                "signal_type": "привычка",
                "subject_type": "категория",
                "subject_id": "baby-food",
                "aspect_reference": None,
                "evidence": [579379, 579457],
                "reading_reference": None,
                "quote_reference": "давати вночі\n  кефір/ряжанку/молоко",
            }
        ],
    },
]

ENTITY_CASES = [
    {
        "id": "E1",
        "channel": "@matusi_ukr",
        "post_id": 22242,
        "msg_id": 578951,
        "name": 'дитячий центр "Гармонія"',
        "subject_type": "не_наш_рынок",
        "reading_reference": "тема треда: английский для детей",
    },
    {
        "id": "E2",
        "channel": "@VARUS_channel",
        "post_id": 10360,
        # the name is printed in the POST — the reference names no msg-id for it, and the record
        # carries null rather than the id of a comment that does not say it
        "msg_id": None,
        "name": "Молоко Дитяче 3,2% ТМ Селянське",
        "subject_type": "молочный_бренд",
        "reading_reference": "контекст каталога",
    },
    {
        "id": "E3",
        "channel": "@VARUS_channel",
        "post_id": 10348,
        "msg_id": 20664,
        "name": "Зайшла в Varus на Деміївській",
        "subject_type": "сеть_ритейлер",
        "reading_reference": "не private-label бренд varus-pl",
    },
    {
        "id": "E4a",
        "channel": "@mandziak",
        "post_id": 3684,
        "msg_id": 48099,
        "name": "чи варто…",
        # an adverb is not an entity, and the four readings have no word for «not a name». The gold
        # claim is an ABSENCE: the reader must not report a Varto entity in this thread
        "subject_type": None,
        "expected": "absent",
        "reading_reference": "наречие,\n  никакого бренда Varto",
    },
    {
        "id": "E4b",
        "channel": "@mandziak",
        "post_id": 3689,
        "msg_id": 48054,
        "name": "чи варто…",
        "subject_type": None,
        "expected": "absent",
        "reading_reference": "наречие,\n  никакого бренда Varto",
    },
]

NOISE_THREADS = [
    {
        "id": "N1",
        "channel": "@VARUS_channel",
        "post_id": 10529,
        "class": "плюс_спам",
        "reading_reference": "десятки «+»",
    },
    {
        "id": "N2",
        "channel": "@VARUS_channel",
        "post_id": 10366,
        "class": "плюс_спам",
        "msg_id": 20916,
        "reading_reference": "msg 20916 «1»",
    },
    {
        "id": "N3",
        "channel": "@sashafitnesslife",
        "post_id": 3939,
        "class": "плюс_спам",
        "reading_reference": "29 × «Тест»",
    },
    {
        "id": "N4",
        "channel": "@retsepty",
        "post_id": 7312,
        "class": "скам",
        "reading_reference": "«работа 20 000 гривен…»",
    },
    {
        "id": "N5",
        "channel": "@retsepty",
        "post_id": 7325,
        "class": "скам",
        "reading_reference": "«работа 20 000 гривен…»",
    },
    {
        "id": "N6",
        "channel": "@retsepty",
        "post_id": 7327,
        "class": "скам",
        "reading_reference": "«работа 20 000 гривен…»",
    },
]

SECONDARY = [
    {
        "id": "S1",
        "channel": "@VARUS_channel",
        "post_id": 10529,
        "msg_id": 21420,
        "signal_type": "жалоба",
        "subject_type": "сеть_ритейлер",
        "aspect_reference": "наличие",
        "reading_reference": "сарказм-жалоба",
        "quote_reference": "половина товаров закончилась, гениально",
    },
    {
        "id": "S2",
        "channel": "@VARUS_channel",
        "post_id": 10593,
        "msg_id": 21507,
        "signal_type": "жалоба",
        "subject_type": "сеть_ритейлер",
        "aspect_reference": "сервис",
        "reading_reference": "промокод не работает",
        "quote_reference": None,
    },
    {
        "id": "S3",
        "channel": "@VARUS_channel",
        "post_id": 10360,
        "msg_id": 20737,
        "signal_type": "жалоба",
        "subject_type": "сеть_ритейлер",
        "aspect_reference": "наличие",
        "reading_reference": "акционного нет на полке",
        "quote_reference": None,
    },
    {
        "id": "S4",
        "channel": "@VARUS_channel",
        "post_id": None,
        "msg_id": 21199,
        "signal_type": None,
        "subject_type": "сеть_ритейлер",
        "aspect_reference": None,
        "reading_reference": "Ритейл-сервис-кластер VARUS: пицца",
        "quote_reference": None,
    },
    {
        "id": "S5",
        "channel": "@VARUS_channel",
        "post_id": None,
        "msg_id": 21256,
        "signal_type": None,
        "subject_type": "сеть_ритейлер",
        "aspect_reference": None,
        "reading_reference": "доставка",
        "quote_reference": None,
    },
    {
        "id": "S6",
        "channel": "@VARUS_channel",
        "post_id": None,
        "msg_id": 21566,
        "signal_type": None,
        "subject_type": "сеть_ритейлер",
        "aspect_reference": "качество",
        "reading_reference": "рыба",
        "quote_reference": None,
    },
]
"""The reference's S list, non-gating (adjudication input). The fish cluster is named as a RANGE —
«21566–21578» — and only its first id is carried: a range is not an enumeration, and inventing the
thirteen ids between the ends would be the executor writing gold."""

PER_COMMENT = [
    # (msg_id, derived_from, subject_type, subject_id, stance, aspect_reference, why)
    (21626, "F1a", "сеть_ритейлер", "varus", "negative", "качество", "signal"),
    (21599, "F1b", "категория", "морозиво без цукру", None, "наличие", "signal"),
    (21601, "F1b", "категория", "морозиво без цукру", None, "наличие", "signal"),
    (21629, "F1c", None, None, "positive", "вкус", "signal"),
    (580124, "F2a", "молочный_бренд", "lasunka", "negative", "наличие", "signal"),
    (580129, "F2.fork", "категория_личное", None, None, None, "stated"),
    (47899, "F3a", "категория", "творог", None, None, "signal"),
    (47902, "F3a", "категория", "творог", None, None, "signal"),
    (48276, "F4a", "категория", "функциональная молочка", None, None, "signal"),
    (48283, "F4a", "категория", "функциональная молочка", None, None, "signal"),
    (579379, "F5a", "категория", "baby-food", None, None, "signal"),
    (579457, "F5a", "категория", "baby-food", None, None, "signal"),
    (578951, "E1", "не_наш_рынок", None, None, None, "stated"),
    (20664, "E3", "сеть_ритейлер", None, None, None, "stated"),
]
"""Every msg-id the reference names explicitly, and nothing else — D2's own scope.

`why` says which rule made the row: `stated` where the reference gives the comment its own reading
(and that reading wins), `signal` where the row inherits from the signal it is evidence for. The two
«чи варто» ids are NOT here: their gold claim is an absence, which is scored in the entity bar and
has no subject_type to agree on. 20916 is not here either — the store puts it under another post,
and a row keyed to a thread the reader was never given could only ever be a miss."""


def assert_transcribed(*phrases) -> None:
    """Every phrase above must be IN the reference file, whitespace-normalised.

    The file is hard-wrapped prose, so a quote that spans a line break carries the wrap; comparing
    normalised text is what lets the transcription be checked at all. Anything that fails here is a
    paraphrase, which is the one thing D2 forbids.
    """
    body = " ".join(REFERENCE.read_text(encoding="utf-8").split())
    for phrase in phrases:
        if phrase is None:
            continue
        flat = " ".join(str(phrase).split())
        if flat not in body:
            raise SystemExit(
                f"{flat!r} is not in {summary.rel(REFERENCE)} — the gold may only carry the"
                " reference's own words, and this one has been paraphrased"
            )


def normalise(text: str) -> str:
    """Whitespace collapsed, NBSP folded, case folded — how a quote is compared to the store.

    Case folded because the reference quotes phrases INSIDE its own sentences: «чи варто…» is the
    same words as the store's «Чи варто до вас йти?», and reporting that as a rewritten quote
    would bury the four that really were tightened under two that only lost a capital letter.
    """
    return " ".join(text.replace(" ", " ").split()).casefold()


def quote_state(quote: str | None, texts: list[str]) -> dict:
    """How the reference's quote stands against the store's own text for its evidence.

    Three states, computed and never asserted by hand: `verbatim` (a substring), `fragmented` (every
    piece of an elided quote is a substring, which is what «…» means) and `compressed` (neither —
    the team lead tightened the wording, and the store's text is what the record carries).
    """
    if quote is None:
        return {"state": "none"}
    body = " ".join(normalise(one) for one in texts)
    flat = normalise(quote)
    if flat in body:
        return {"state": "verbatim"}
    elided = "…" in flat or "..." in flat
    pieces = [normalise(one) for one in re.split(r"…|\.\.\.", flat) if normalise(one)]
    # the ellipsis is the elision, and it elides at the END as often as in the middle: «чи варто…»
    # is one piece and still an elided quote, so the state turns on the mark and not on the count
    if elided and pieces and all(piece in body for piece in pieces):
        return {"state": "fragmented", "pieces": pieces}
    return {
        "state": "compressed",
        "missing": [piece for piece in pieces if piece not in body],
    }


def why_outside(thread: dict, gate) -> dict:
    """Which of the gate's silencers removed this thread — measured, one at a time.

    A case the reference calls obligatory and the population does not contain is not a reader
    failure and must not be scored as one. What it is instead is a fact about the GATE, and the
    only honest way to state it is the same way the census decomposed its own silencers: run the
    keep predicate with none of them and with each of them alone, and name the ones that alone
    take the thread away.
    """
    aliases, rules, categories = gate

    def passes(active: tuple[str, ...]) -> bool:
        surviving = [row for row in thread["comments"] if not census.silenced_comment(row, active)]
        texts = [(thread["post_text"], census.POST_CARRIER)] + [
            (summary.comment_text(row), census.CARRIER) for row in surviving
        ]
        rule = rules if "varto_rule" in active else None
        return any(
            one["brands"] or one["categories"]
            for one in (
                census.hits(text, categories, aliases, rule, carrier) for text, carrier in texts
            )
        )

    bare = passes(())
    return {
        "in_the_window": True,
        "passes_the_gate_with_no_silencer": bare,
        "removed_by": [name for name in census.SILENCERS if bare and not passes((name,))],
        "reading": (
            "the thread's only lexicon hit is one this silencer takes away, so the gate drops the"
            " whole thread — before payment, and therefore before the reader can resolve anything"
            " in it"
        ),
    }


def evidence_index() -> dict:
    """`(channel, msg_id) -> the row`, over every comment the window bought."""
    rows = {}
    for path in summary.leg_files(builder.DERIVED, loop.RECORD_TYPE):
        for row in summary.read_rows(path):
            rows[(row["channel"], int(row["msg_id"]))] = row
    return rows


def build(kept: list[dict], rows: dict, posts: dict, threads: list[dict], gate) -> dict:
    """The record: the transcription, each row met with the store, each thread with the population."""
    inside = {(one["channel"], one["post_id"]): one for one in kept}
    window = {(one["channel"], one["post_id"]): one for one in threads}

    def comment(channel: str, msg_id: int) -> dict:
        """One named msg-id, as the evidence store has it — including «it is not there»."""
        row = rows.get((channel, msg_id))
        if row is None:
            return {"msg_id": msg_id, "in_the_store": False}
        text = summary.comment_text(row)
        parent = int(row["parent_msg_id"])
        thread = inside.get((channel, parent))
        return {
            "msg_id": msg_id,
            "in_the_store": True,
            "post_id_in_the_store": parent,
            "evidence_text": text,
            "payable": loop.has_text(text),
            "in_the_population": bool(thread)
            and any(one["msg_id"] == msg_id for one in thread["comments"]),
        }

    def thread_state(channel: str, post_id: int | None) -> dict:
        one = inside.get((channel, post_id))
        state = {
            "in_the_population": one is not None,
            "payable_comments": len(one["comments"]) if one else None,
        }
        if one is None and post_id is not None:
            thread = window.get((channel, post_id))
            state["outside_because"] = (
                why_outside(thread, gate) if thread else {"in_the_window": False}
            )
        return state

    flagships = []
    for case in FLAGSHIPS:
        assert_transcribed(case["title"])
        signals = []
        for signal in case["signals"]:
            assert_transcribed(signal["quote_reference"], signal["reading_reference"])
            evidence = [comment(case["channel"], msg_id) for msg_id in signal["evidence"]]
            texts = [one["evidence_text"] for one in evidence if one.get("evidence_text")]
            signals.append(
                {
                    **{key: value for key, value in signal.items() if key != "aspect_reference"},
                    "aspect": ASPECT_OF.get(signal["aspect_reference"]),
                    "aspect_reference": signal["aspect_reference"],
                    "stance": STANCE_OF.get(signal["signal_type"]),
                    "quote": quote_state(signal["quote_reference"], texts),
                    "evidence_rows": evidence,
                }
            )
        entry = {
            **{key: value for key, value in case.items() if key != "signals"},
            "thread": thread_state(case["channel"], case["post_id"]),
            "signals": signals,
        }
        if fork := case.get("fork"):
            assert_transcribed(fork["quote_reference"], fork["reading_reference"])
            row = comment(case["channel"], fork["msg_id"])
            entry["fork"] = {
                **fork,
                "quote": quote_state(fork["quote_reference"], [row.get("evidence_text", "")]),
                "evidence_row": row,
            }
        flagships.append(entry)

    entities = []
    for case in ENTITY_CASES:
        assert_transcribed(case["name"], case["reading_reference"])
        row = comment(case["channel"], case["msg_id"]) if case["msg_id"] else None
        post = posts.get((case["channel"], case["post_id"]), "")
        entities.append(
            {
                **case,
                "thread": thread_state(case["channel"], case["post_id"]),
                "evidence_row": row,
                # E2's name is printed in the post, so the post is where the quote must be found
                "quote": quote_state(case["name"], [row["evidence_text"]] if row else [post]),
            }
        )

    noise = []
    for case in NOISE_THREADS:
        assert_transcribed(case["reading_reference"])
        entry = {**case, "thread": thread_state(case["channel"], case["post_id"])}
        if msg_id := case.get("msg_id"):
            entry["evidence_row"] = comment(case["channel"], msg_id)
        noise.append(entry)

    secondary = []
    for case in SECONDARY:
        assert_transcribed(case["reading_reference"], case["quote_reference"])
        row = comment(case["channel"], case["msg_id"])
        secondary.append(
            {
                **{key: value for key, value in case.items() if key != "aspect_reference"},
                "aspect": ASPECT_OF.get(case["aspect_reference"]),
                "aspect_reference": case["aspect_reference"],
                "quote": quote_state(case["quote_reference"], [row.get("evidence_text", "")]),
                "evidence_row": row,
            }
        )

    per_comment = []
    for msg_id, source, subject_type, subject_id, stance, aspect, why in PER_COMMENT:
        channel = next(
            case["channel"]
            for case in (*FLAGSHIPS, *ENTITY_CASES)
            if case["id"] == source.split(".")[0] or source.startswith(case["id"])
        )
        row = comment(channel, msg_id)
        per_comment.append(
            {
                "msg_id": msg_id,
                "channel": channel,
                "derived_from": source,
                "rule": why,
                "subject_type": subject_type,
                "subject_id": subject_id,
                "stance": stance,
                "aspect": ASPECT_OF.get(aspect),
                # what the scorer may compare: a field the reference does not state is not gold
                "scored_fields": [
                    name
                    for name, value in (("subject_type", subject_type), ("stance", stance))
                    if value is not None
                ],
                "evidence_row": row,
            }
        )

    def split(cases: list[dict]) -> dict:
        return {
            "reachable": [one["id"] for one in cases if one["thread"]["in_the_population"]],
            "unreachable": [
                {"id": one["id"], "cause": one["thread"].get("outside_because")}
                for one in cases
                if not one["thread"]["in_the_population"]
            ],
        }

    conflicts = []
    for case in noise:
        signals_here = [
            one["id"]
            for one in secondary
            if one["channel"] == case["channel"]
            and one["evidence_row"].get("post_id_in_the_store") == case["post_id"]
        ]
        if signals_here:
            conflicts.append(
                {
                    "kind": "a noise thread the reference itself reads a signal in",
                    "case": case["id"],
                    "thread": f"{case['channel']}:{case['post_id']}",
                    "secondary": signals_here,
                    "reading": (
                        "the N list calls this thread noise and the S list names a signal inside"
                        " it. The store has the second: the thread's surviving comments are"
                        f" {case['thread']['payable_comments']}, not the «десятки «+»» the N list"
                        " describes. Bar 3 cannot score both readings and the record chooses"
                        " neither — the sitting does"
                    ),
                }
            )
        row = case.get("evidence_row") or {}
        if row.get("in_the_store") and row["post_id_in_the_store"] != case["post_id"]:
            conflicts.append(
                {
                    "kind": "a named msg-id the store puts under another post",
                    "case": case["id"],
                    "msg_id": row["msg_id"],
                    "post_id_in_the_reference": case["post_id"],
                    "post_id_in_the_store": row["post_id_in_the_store"],
                    "evidence_text": row["evidence_text"],
                }
            )
    compressed = [
        {"case": one, "missing": two["missing"]}
        for one, two in (
            *((s["id"], s["quote"]) for case in flagships for s in case["signals"]),
            *((case["id"], case["quote"]) for case in entities),
            *((case["id"], case["quote"]) for case in secondary),
        )
        if two["state"] == "compressed"
    ]
    if compressed:
        conflicts.append(
            {
                "kind": "quotes the reference tightened",
                "cases": compressed,
                "reading": (
                    "the reference's quotes are a reading aid, not extracts: none of them can be"
                    " grepped in the store as written. `evidence_text` is what the reader will be"
                    " given, and it is what any quote check must run against"
                ),
            }
        )

    return {
        "window": builder.WINDOW_ID,
        "contract": "docs/PROMPT-probe-a.md D2",
        "reachability": {
            "flagships": split(flagships),
            "entity_cases": split(entities),
            "noise_threads": split(noise),
            "per_comment": {
                "rows": len(per_comment),
                "inside_the_population": [
                    one["msg_id"] for one in per_comment if one["evidence_row"]["in_the_population"]
                ],
                "outside_the_population": [
                    one["msg_id"]
                    for one in per_comment
                    if not one["evidence_row"]["in_the_population"]
                ],
            },
            "reading": (
                "a case whose thread the gate removed before payment cannot be answered by the"
                " reader at all: it is a fact about the gate, and a bar scored over it would fail"
                " by arithmetic rather than by reading. The bars of"
                " `results/prereg_reader_probe.json` are registered over the reachable rows, with"
                " the unreachable ones named and returned to the operator"
            ),
        },
        "conflicts": conflicts,
        "authority": {
            summary.rel(REFERENCE): summary.sha256_of(REFERENCE),
            summary.rel(PLAN): summary.sha256_of(PLAN),
            summary.rel(PRODUCT): summary.sha256_of(PRODUCT),
        },
        "reading_rule": (
            "the per-comment bar is counted ONLY over the msg-ids this reference names explicitly"
            " (its own closing rule). Everything else the machine returns is adjudication input,"
            " and this file is never re-read against the machine's answer"
        ),
        "derivation": {
            "aspects": ASPECT_OF,
            "aspects_authority": (
                "docs/PRODUCT.md question 2 names these six Russian words and scorer.INTENTS_V2 is"
                " the same six in English — the aspect layer the model already has"
            ),
            "stance": STANCE_OF,
            "stance_rule": (
                "жалоба reads negative and похвала positive; спрос, привычка and тренд state no"
                " attitude and carry none. A stance invented for them would be the executor"
                " reinterpreting the reference, which D2 forbids"
            ),
            "per_comment_rule": (
                "a per-comment row carries the reading the reference states for that comment where"
                " it states one (`rule: stated`), else the subject and stance of the signal it is"
                " evidence for (`rule: signal`, the shape of plan §3's own example). A field the"
                " reference does not state is null and is not in `scored_fields`"
            ),
            "quote_rule": (
                "`quote_reference` is the reference's wording, `evidence_text` the store's."
                " `quote.state` is recomputed from the store on every build: verbatim, fragmented"
                " (an elided quote whose every piece is present) or compressed"
            ),
        },
        "population": {
            "record": summary.rel(population.CENSUS),
            "sha256": population.census_sha256(),
            "cell": population.CELL,
            "threads": len(kept),
            "payable_comments": sum(len(one["comments"]) for one in kept),
        },
        "flagships": flagships,
        "entity_cases": entities,
        "noise_threads": noise,
        "secondary": secondary,
        "per_comment": per_comment,
        "evidence_store": {
            summary.rel(path): summary.sha256_of(path)
            for path in summary.leg_files(builder.DERIVED, loop.RECORD_TYPE)
        },
        "instrument": {
            "task": prompts.READER_TASK,
            "prompt_sha256": prompts.prompt_sha256(prompts.READER_TASK),
        },
        "producer": {
            "script": summary.rel(Path(__file__)),
            "sha256": summary.sha256_of(Path(__file__)),
            "borrowed": {
                name: summary.sha256_of(REPO_ROOT / name)
                for name in (
                    "scripts/reader_population.py",
                    "scripts/gate_census_w1.py",
                    "scripts/window_summary_5c2.py",
                    "src/market_pulse/prompts.py",
                )
            },
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)

    record = build(
        population.population(),
        evidence_index(),
        census.raw_posts(),
        population.window(),
        population.gate(),
    )
    args.out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {summary.rel(args.out)}  sha256 {summary.sha256_of(args.out)[:16]}…")
    rows = record["per_comment"]
    scored = [one for one in rows if one["evidence_row"]["in_the_population"]]
    print(
        f"  per-comment gold {len(rows)} rows · {len(scored)} inside the population ·"
        f" {len(rows) - len(scored)} outside"
    )
    for name, cases in (
        ("flagships", record["flagships"]),
        ("entity cases", record["entity_cases"]),
        ("noise threads", record["noise_threads"]),
    ):
        outside = [one["id"] for one in cases if not one["thread"]["in_the_population"]]
        print(f"  {name:14s} {len(cases)} · outside the population: {outside or 'none'}")
    states = {}
    for case in record["flagships"]:
        for signal in case["signals"]:
            states[signal["quote"]["state"]] = states.get(signal["quote"]["state"], 0) + 1
    print(f"  flagship quotes by state: {states}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
