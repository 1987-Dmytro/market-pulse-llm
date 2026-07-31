"""The two zero-shot prompts and the parser that reads their answers back.

SPEC §7 names "zero-shot base LLM with fixed prompt" as one of the three
pre-registered baselines, so the prompt is part of the measurement: it is fixed
here, hashed into every result record, and sent byte-identically to every model
including the frontier reference row. Changing a word changes the baseline.

The prompts state the rules of `docs/annotation/comments.md` and
`docs/annotation/posts.md` — the same definitions the annotator worked from,
including the ones no model could guess (a promo-mechanic complaint is not
``price``; dairy as an ingredient is not relevant; ``launch`` beats ``promo``
when both apply). They carry **no labelled examples**: with examples this would
be a few-shot baseline, which is not what SPEC §7 pre-registered.

Everything lives in a single ``user`` message. Some serving stacks refuse a
system role for Gemma, and a request shape that works for three models out of
four is a comparison between three models and an error.

The parser is here rather than next to the HTTP client because it is the mirror
image of the prompt: the prompt promises a shape, :func:`parse_reply` is the
only thing allowed to decide whether that promise was kept.
"""

import hashlib
import json

from market_pulse.scorer import INTENTS, POST_TYPES, SENTIMENT_LABELS

TASKS = ("T1", "T2")

T1_PROMPT = """\
You label one comment from a Ukrainian food-retail Telegram channel (retail chains and \
discount aggregators). Comments are in Ukrainian or Russian. Judge the text you are given, \
never the thread around it.

Return three labels.

sentiment — the attitude the author expresses towards the product, the price or the \
retailer, not their mood.
- "positive": praise, thanks, satisfaction.
- "negative": complaint, disappointment, accusation.
- "neutral": a question, a factual statement or a request carrying no evaluation.
Sarcasm outranks the surface wording: a sarcastic compliment is "negative". If praise and \
complaint are mixed, take the dominant one; if neither dominates, "neutral". For a comment \
that is only emoji, read the emoji when it is unambiguous.

sarcasm — true when the literal reading contradicts the intended one: irony, mock praise, \
bitter exaggeration. It is a flag, not a sentiment: "negative" can carry either value. \
Emoji alone never decide it — the contradiction has to be in the text.

intents — what the comment is about. Any subset of these five, possibly empty:
- "taste": flavour, smell, texture.
- "price": cost, discount, promo value — what the buyer pays. A complaint that a promo \
mechanic is unfair (a rigged giveaway, unclear terms) is not "price".
- "packaging": package, volume, label, portion.
- "quality": freshness, spoilage, composition, production.
- "availability": presence in a store, stock, delivery of the product.
A complaint about service alone — the app, a delivery slot, loyalty points — touches no \
product intent: return [].

Answer with one JSON object and nothing else: no explanation, no code fence.
{"sentiment": "positive|negative|neutral", "sarcasm": true|false, "intents": ["price"]}\
"""

T2_PROMPT = """\
You label one post from a Ukrainian food-retail Telegram channel (retail chains and \
discount aggregators). Posts are in Ukrainian or Russian. Judge the text only — you cannot \
see the images.

Return three labels.

relevant — true when the post mentions, promotes or announces a product in the tracked \
category: dairy (milk, kefir and ryazhanka, yogurt, curd and syrky, sour cream, butter, \
cheese, dairy desserts, plant-based milk analogs) or ice cream in any format. One \
qualifying product inside a list of many is enough. Decided cases: dairy used as an \
ingredient in a prepared dish (pizza with cheese, a cheesecake) is false; plant-based \
analogs are true; eggs, mayonnaise, margarine, condensed milk and cheese-flavoured snacks \
are false; naming the category with no product at all is true.

post_type — exactly one of three, labelled for every post, relevant or not.
- "launch": a first-time announcement of a new product, flavour, format or collection. \
The claim has to be that the product is new, not that it is cheap.
- "promo": discounts, price offers, giveaways, loyalty campaigns. A repeated promo of \
something announced earlier is "promo"; so is a returning seasonal item; so is a discount \
on an item merely described as new.
- "other": everything else — recipes, holidays, channel news, service notices, polls.
When a new product is introduced together with an opening discount, "launch" wins.

brands — every brand named as the maker of a product in the tracked category. Brands of \
non-tracked products in the same post are not extracted. Strip "TM"/"ТМ" markers and quotes, \
and keep the spelling as written. Private labels count as brands. A chain name used as a \
product brand is a brand; the same chain name naming the shop is not. The same brand twice \
is one entry. No qualifying brand — the common case, including for relevant posts that only \
name a category — is [].

Answer with one JSON object and nothing else: no explanation, no code fence.
{"relevant": true|false, "post_type": "launch|promo|other", "brands": [{"mention": "brand as written"}]}\
"""

PROMPTS = {"T1": T1_PROMPT, "T2": T2_PROMPT}
DELIMITERS = {"T1": "comment", "T2": "post"}


class ParseError(ValueError):
    """A reply that is not a valid answer. Its ``reason`` is what gets counted."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def prompt_sha256(task: str) -> str:
    """SHA256 of the fixed prompt — the field that makes a record reproducible."""
    return hashlib.sha256(PROMPTS[task].encode("utf-8")).hexdigest()


def build_messages(task: str, text: str) -> list[dict]:
    """The whole request: instructions and the one row, in a single user turn.

    The row is fenced in a tag so that a comment ending in "Answer with one JSON
    object" cannot read as instructions — retail comment threads contain
    everything, and a prompt-shaped comment must not get a different request
    than its neighbours.
    """
    tag = DELIMITERS[task]
    return [{"role": "user", "content": f"{PROMPTS[task]}\n\n<{tag}>\n{text}\n</{tag}>"}]


def _object(reply: str) -> dict:
    """The JSON object inside a reply, tolerant of wrappers, strict about content.

    A ```json fence or a sentence before the brace is formatting, not a different
    answer, so unwrapping happens before validation and is not a failure. What is
    inside the braces is judged exactly as it comes.
    """
    text = reply.strip()
    if not text:
        raise ParseError("empty reply")
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
    start = text.find("{")
    if start < 0:
        raise ParseError("no JSON object in reply")
    try:
        # decoding from the brace, so what comes back is an object or nothing
        value, _ = json.JSONDecoder().raw_decode(text[start:])
    except ValueError:
        raise ParseError("malformed JSON") from None
    return value


def _flag(value, field: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.strip().casefold() in ("true", "false"):
        return value.strip().casefold() == "true"
    raise ParseError(f"{field} is not a boolean")


def _choice(value, field: str, allowed: tuple[str, ...]) -> str:
    if not isinstance(value, str):
        raise ParseError(f"{field} is not a string")
    label = value.strip().casefold()
    if label not in allowed:
        raise ParseError(f"{field} outside its domain")
    return label


def _require(payload: dict, *fields: str) -> None:
    missing = [field for field in fields if field not in payload]
    if missing:
        raise ParseError(f"missing field: {missing[0]}")


def parse_reply(task: str, reply: str) -> dict:
    """One model reply -> the labels, or :class:`ParseError` naming what is wrong.

    Strict at the level of the whole answer: one out-of-domain field invalidates
    the object, because the object is one answer. A row that fails here is
    counted and excluded, never coerced to a default label — handing a model that
    could not answer the majority class would flatter it exactly where it is
    weakest (docs/PROMPT-3b.md; ADR 3b-infra-and-precision §(e)).
    """
    payload = _object(reply)
    if task == "T1":
        _require(payload, "sentiment", "sarcasm", "intents")
        intents = payload["intents"]
        if isinstance(intents, str):  # a lone label instead of a list of one
            intents = [intents]
        if not isinstance(intents, list):
            raise ParseError("intents is not a list")
        return {
            "sentiment": _choice(payload["sentiment"], "sentiment", SENTIMENT_LABELS),
            "sarcasm": _flag(payload["sarcasm"], "sarcasm"),
            "intents": sorted({_choice(item, "intents", INTENTS) for item in intents}),
        }
    if task == "T2":
        _require(payload, "relevant", "post_type", "brands")
        brands = payload["brands"]
        if not isinstance(brands, list):
            raise ParseError("brands is not a list")
        mentions = []
        for entry in brands:
            # `["Rud"]` and `[{"mention": "Rud"}]` are the same answer written two
            # ways; anything else is not an answer about brands.
            mention = (
                entry
                if isinstance(entry, str)
                else entry.get("mention")
                if isinstance(entry, dict)
                else None
            )
            if not isinstance(mention, str) or not mention.strip():
                raise ParseError("brand entry without a mention")
            mentions.append({"mention": " ".join(mention.split())})
        return {
            "relevant": _flag(payload["relevant"], "relevant"),
            "post_type": _choice(payload["post_type"], "post_type", POST_TYPES),
            "brands": mentions,
        }
    raise ValueError(f"unknown task: {task}")
