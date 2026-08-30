"""The promo-signal extractor's prompt — a NEW module, because `prompts.py` is pinned.

`src/market_pulse/prompts.py` is pinned by five sealed records (`docs/PROMPT-pass1-fewshot.md` D0.2
and the reader registrations), and `docs/PHASE-promo-pulse-1.md` §4 says new prompt text goes in a
new module. This is that module, and it holds exactly one contract: given a promo post and the
comments under it, name what each comment is ABOUT and what the thread SAYS.

Two things this file is deliberately built around.

**The prompt carries the annotator's law.** The codebook the team lead labels dev-40 by is rendered
INTO the prompt, not summarised beside it: where a guideline and a prompt disagree, the model obeys
the prompt and the grader scores the guideline, and the disagreement shows up as an unexplainable
error table ([[prompt_must_carry_the_annotators_law]]). :data:`CODEBOOK` is that law, and
:func:`render` puts it in front of every call.

**The version is the RENDER, not the file.** `signal.extractor_version` is
:func:`extractor_version`, the sha256 of the rendered text — a row has to say which instrument
produced it, and the module's own sha would move for a comment change that the model never saw,
while a template edit that changes what the model reads would move both. The render is what the
model read ([[the_identity_field_stops_covering_the_change]]).

Serving is unchanged and needs no flag: `local_llm.CHAT_TEMPLATE` carries
`"enable_thinking": False` as every client's default, and batch 1 is structural — the positions,
caption and reader legs each loop one item per forward (plan §5.11).
"""

from __future__ import annotations

import hashlib
import json

SUBJECT_TYPES = ("chain", "brand", "sku", "post")
"""What a comment can be about. Mirrors `aggregates.SUBJECT_TYPES`; asserted equal in the tests, so
the prompt and the table cannot drift into two vocabularies."""

SIGNAL_TYPES = ("жалоба", "похвала", "спрос", "привычка", "цена")
"""The five of `docs/PHASE-promo-pulse-1.md` §2 S2, in the codebook's own words."""

ATTRIBUTION_SOURCES = ("explicit", "reply_context", "post_context")
"""How the subject was established, weakest last."""

CODEBOOK = """Ти розмічаєш коментарі під ПРОМО-постом торгової мережі.

ПРО ЩО коментар (about):
  chain  — про мережу (АТБ, Сільпо, Varus, Фора, ЕКО, Епіцентр, Близенько, Сім23, Rozetka…)
  brand  — про торгову марку продукту (Яготинське, Галичина, Рудь, Лімо, Молокія…)
  sku    — про конкретну позицію з промо (назва + обʼєм/вага, або ціна цієї позиції)
  post   — про сам пост: акцію в цілому, її умови, строки, оформлення

ЗВІДКИ ти це знаєш (source):
  explicit       — субʼєкт названий у САМОМУ коментарі
  reply_context  — субʼєкт названий у коментарі, на який цей відповідає
  post_context   — субʼєкт названий тільки в пості

СИГНАЛ треду (signal), нуль або більше:
  жалоба    — скарга: якість, ціна зависока, обман, немає в наявності
  похвала   — схвалення: смак, ціна вигідна, якість
  спрос     — питання «де купити / чи є / коли буде»
  привычка  — «беру постійно», «завжди купуємо», рутина
  цена      — судження ПРО ЦІНУ як таку: дорого, дешево, дешевше ніж…

ПРАВИЛА
1. Кожен сигнал МУСИТЬ мати цитату — підрядок коментаря, слово в слово.
2. Якщо субʼєкт не встановлюється — не вгадуй: постав рядок в unsure з причиною.
3. Якщо клас не з переліку — не вигадуй новий: unsure з причиною.
4. Коментар без тексту (тільки стікер/фото) не розмічається взагалі.
5. Один тред може нести кілька сигналів про РІЗНІ субʼєкти — це різні рядки."""

TEMPLATE = """{codebook}

ПОСТ ({channel}, msg_id={thread_root}):
{post}

КОМЕНТАРІ:
{comments}

Поверни JSON: {{"about": [...], "signals": [...], "unsure": [...]}}
  about  : {{"msg_id": int, "subject_type": str, "subject": str, "source": str, "confidence": float}}
  signals: {{"type": str, "subject_type": str, "subject": str, "msg_id": int, "quote": str,
             "confidence": float}}
  unsure : {{"msg_id": int, "reason": str, "candidates": [str]}}"""


def render(channel: str, thread_root, post: str, comments: list[dict]) -> str:
    """The text the model reads, for one cooled thread. Deterministic — no clock, no ordering luck.

    Comments are rendered in msg_id order rather than store order: the store is append-only and a
    resumed collection can interleave, and a prompt whose lines move between runs would move
    `extractor_version` with them.
    """
    lines = "\n".join(
        f"[{row['msg_id']}] {(row.get('text') or '').strip()}"
        for row in sorted(comments, key=lambda row: int(row["msg_id"]))
    )
    return TEMPLATE.format(
        codebook=CODEBOOK,
        channel=channel,
        thread_root=thread_root,
        post=(post or "").strip() or "(без тексту — ціна в зображенні)",
        comments=lines,
    )


def extractor_version(rendered: str) -> str:
    """sha256 of the rendered prompt — what `signal.extractor_version` carries."""
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def codebook_version() -> str:
    """sha256 of the LAW alone, so a codebook change is visible without a thread to render.

    Separate from :func:`extractor_version` on purpose: every thread renders a different prompt and
    therefore a different version, so a per-row version cannot answer "did the law move?".
    """
    return hashlib.sha256(CODEBOOK.encode("utf-8")).hexdigest()


def vocabulary() -> dict:
    """The three closed lists, as the record writes them down beside a reading."""
    return {
        "subject_types": list(SUBJECT_TYPES),
        "signal_types": list(SIGNAL_TYPES),
        "attribution_sources": list(ATTRIBUTION_SOURCES),
        "codebook_sha256": codebook_version(),
    }


def parse(answer: str) -> dict:
    """The model's answer as a dict, or a counted parse failure — never an exception.

    An empty class eats parse failures when a refusal is silently read as "nothing found"
    ([[empty_class_eats_the_parse_failures]]), so an unparseable answer returns its own marked
    shape and the caller counts it as what it is.
    """
    try:
        body = json.loads(answer)
    except json.JSONDecodeError as bad:
        return {"about": [], "signals": [], "unsure": [], "parse_failure": str(bad)}
    if not isinstance(body, dict):
        return {"about": [], "signals": [], "unsure": [], "parse_failure": "not an object"}
    return {
        "about": body.get("about") or [],
        "signals": body.get("signals") or [],
        "unsure": body.get("unsure") or [],
        "parse_failure": None,
    }
