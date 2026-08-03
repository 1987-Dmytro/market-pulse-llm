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

from market_pulse.scorer import INTENTS, INTENTS_V2, POST_TYPES, SENTIMENT_LABELS

TASKS = ("T1", "T2")
"""The prompt identity of every recorded run — v1, and frozen.

``records.assert_prompt_sha`` builds the map it compares against stored records out
of exactly this tuple, so a sixth prompt joining it would make every past record
fail to verify. Taxonomy v2's prompts live in :data:`PROMPTS` beside these two and
are named by whoever asks for them."""

SERVICE_INTENT = (
    "interaction with the retailer as a service: in-store and online service, the delivery "
    "process, the app and the checkout, the support hotline, staff, and how promos and "
    "giveaways are organised — mechanics, fairness, communication"
)
"""The sixth intent, in the words SPEC amendment 3.8 approved.

One sentence, three readers: `docs/annotation/comments.md` (the law the annotator
works from), :data:`T1_PROMPT_V2` (what the model is scored against) and
:data:`RELABEL_INTENTS_PROMPT` (what re-labels the corpus). Three renderings of one
definition drift apart silently, so the two prompts embed this constant and a test
holds the guideline to the same words."""

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

T1_PROMPT_V2 = f"""\
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

intents — what the comment is about. Any subset of these six, possibly empty:
- "taste": flavour, smell, texture.
- "price": cost, discount, promo value — what the buyer pays. A question or a complaint about \
a promo mechanic — how a discount is applied, whether a giveaway is fair, what the terms say — \
is not "price", it is "service".
- "packaging": package, volume, label, portion.
- "quality": freshness, spoilage, composition, production.
- "availability": presence in a store, stock, delivery of the product. The product itself, not \
the process around the order: a slot moved, a courier, an order that cannot be cancelled is \
"service".
- "service": {SERVICE_INTENT}.
The first five are about the product and "service" is about the retailer; a comment can carry \
both. A bare participation marker under a giveaway post, an emoji-only comment, bare thanks and \
banter about neither the product nor the retailer carry no intent at all: return [].

Answer with one JSON object and nothing else: no explanation, no code fence.
{{"sentiment": "positive|negative|neutral", "sarcasm": true|false, "intents": ["price"]}}\
"""
"""The T1 prompt under taxonomy v2 — registered beside v1, never instead of it.

Word-for-word ``T1_PROMPT`` outside the ``intents`` block: G1c under v2 has to move
because the label space moved, not because the sentiment instructions were reworded
on the way past."""

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

RELABEL_INTENTS_PROMPT = f"""\
You re-label ONE field of an already-annotated comment from a Ukrainian food-retail Telegram \
channel (retail chains and discount aggregators). Comments are in Ukrainian or Russian. Judge \
the text you are given, never the thread around it.

intents — what the comment is about. Any subset of these six, possibly empty:
- "taste": flavour, smell, texture.
- "price": cost, discount, promo value — what the buyer pays.
- "packaging": package, volume, label, portion.
- "quality": freshness, spoilage, composition, production.
- "availability": presence in a store, stock, delivery of the product. The product itself, not \
the process around the order.
- "service": {SERVICE_INTENT}.

The first five are about the product and "service" is about the retailer; a comment can carry \
both, and a comment can carry none. The cases that repeat:
- a question or a complaint about a promo mechanic — how a discount is applied, whether a \
giveaway is fair, what the terms say — is "service", not "price";
- distrust of a draw, or an accusation that it is rigged, is "service";
- a delivery slot moved, a courier, an order that cannot be cancelled, the app, the checkout, \
the hotline, the queue, the staff: "service". A product missing from the shelf: "availability";
- a bare participation marker under a giveaway post ("+", "++++", "➕") is not a reaction: [];
- emoji only, bare thanks, and jokes about neither the product nor the retailer: [].

Return the intents of this comment and nothing else. Do not judge its sentiment, its sarcasm or \
whether it is clear — those labels are already set and you are not being asked about them.

Answer with one JSON object and nothing else: no explanation, no code fence. Always write the \
"intents" key, with an empty list when the comment is about none of the six.
{{"intents": ["price"]}}\
"""
"""The annotation prompt of the taxonomy-v2 re-label — one field, by construction.

Not :data:`T1_PROMPT_V2`: that one is the pre-registered measurement instrument
(SPEC §7), and a re-label that asked it for three labels would have to be trusted
not to write the other two back. Asking only for ``intents`` makes "sentiment,
sarcasm and unclear untouched" a property of the request rather than a promise
about the code that reads the reply."""

JUDGE_TEXT_ALONE = "Judge the text you are given, never the thread around it."
"""The sentence every prompt above carries — and the one that disagreed with the law.

`docs/annotation/comments.md` §Unit has told the annotator since Phase 2 to judge the
comment on its own text "plus the parent post only when the comment is meaningless
without it". Gold was written under that rule and the model was scored without it, which
is what emptied 97 short replies of their intents in 4.5e (`results/drop_45f.json`)."""

PARENT_POST_RULE = (
    "You are given the comment and the post it replies to. Judge the comment on its own text, "
    "and read the post only when the comment is meaningless without it — a bare agreement, a "
    "participation marker, a two-word answer to a question the post asked. Never label from "
    "other comments: you cannot see them."
)
"""The guideline's §Unit rule in the prompt's voice — one clause, three with-post prompts.

Same discipline as :data:`SERVICE_INTENT`: a rule rendered separately in three places
drifts apart silently, so it is written once and a test holds the three to it."""

NO_POST_TEXT = "(this post has no text of its own — it is an image or a video)"
"""What a media-only parent renders as when nothing can speak for it. 23 of the 97 emptied rows
and 424 of the 1,912 up-label candidates have one, and an empty tag would read as "the post said
nothing". Where 4.5g2 fetched the image and captioned it, :data:`IMAGE_DESCRIPTION` is used
instead — this string is what is left when the media could not be fetched at all."""

POST_SURROGATE = {
    "image": "[image description] {text}",
    "poll": "[poll] {text}",
}
"""What stands in for a media-only post's missing text, and what the model is told it is.

Two kinds, because 4.5g2 found two: an image, described by a vision model, and a poll, whose
question and options Telegram carries in a field the collector never read. Both are tagged
rather than pasted in bare — a description of a picture is not the post's own words, and a
labeller told otherwise would weigh it as if it were. `[[45g2-captions-and-quiz-rulings]]`."""

CAPTION_POST_PROMPT = """\
You describe the image of one post from a Ukrainian food-retail Telegram channel (retail chains \
and discount aggregators). The post has no text of its own, so this image is everything a reader \
has, and your description is what somebody labelling the comments under it will read instead.

Transcribe, exactly as written, the text that tells a reader what this post is: the question it \
asks and the options it offers, the headline of an offer, the dates it runs for, the shop or \
brand named at the top. Then add one sentence saying what the image shows as a whole — which \
kinds of product, and whether it is a promotion, a new product or something else.

Do not list every item on a price leaflet. Name the kinds of goods and at most the few most \
prominent products, and never write the same line twice.

Write the whole answer, the closing sentence included, in the language of the text in the image, \
and in Ukrainian if it carries none. State what is there and nothing else: no marketing copy, no \
guess at what the post is trying to achieve, no opinion about the product. If the image cannot \
be read, say exactly that and nothing more.

Answer with the description alone: no preamble, no quotes, no formatting."""
"""The 4.5g2 captioning instrument, registered beside the label prompts and hashed like them.

Its answer is free text rather than a JSON object, so it is the one entry in :data:`PROMPTS`
that :func:`parse_reply` cannot read and :func:`build_messages` will not render — see
:data:`FREE_TEXT`. It is in the registry anyway because the caption it produces reaches a
labelling prompt, and a record that cannot name the prompt that wrote its input describes a run
nobody can reproduce."""

SETTLED_CASES = """\
Cases the annotation guideline has since settled, and they outrank the general wording above:
- A joke, a piece of trivia or banter about neither a product nor the retailer is not a consumer \
reaction at all.
- A reply written by the retailer in its own voice counts as one even when it carries none of the \
usual markers: unsigned support wording about demand, stock or how a promo runs is the retailer \
speaking, not a customer.
- Praise of how the retailer behaves is "service", exactly as a complaint about the same conduct \
would be.
- A question about how a promo works, what its terms are or who it applies to is "service" — \
never "price", and never no intent at all.
- A comment aimed at another commenter rather than at the retailer is not a reaction to judge, \
unless it accuses the retailer directly: that outranks who it is addressed to and is judged \
normally.
- An answer naming a dish, a filling or a food someone likes — including as a joke or a childhood \
memory — is "taste".
- A quotation used to mock what it quotes, whether the retailer's own words, an app message or a \
promo line, is sarcasm. So is a joke that elevates something ordinary into something it is not.
- Bare thanks and a single unambiguous emoji are readable reactions and are judged, not set \
aside: read the sentiment, and the comment carries no intent.\
"""
"""The v2.1 rulings of `docs/annotation/comments.md`, in the prompt's voice.

Eight lines for eight boundary cases the 4.5g sitting settled, written from the changelog and
not beside it: where the guideline and the prompt disagree the gap is charged to the model. The
last line restates a v2 clause rather than adding law — the sitting applied it as written and
the precheck had been over-marking those rows."""

UNCLEAR_RULE = """\
unclear — true when the row must not be scored at all: it is not a consumer reaction, or it \
cannot be read. Mark it for a participation marker under a giveaway post, for ambiguous or mixed \
emoji, for a reply aimed at another commenter rather than at the retailer, for a reply written by \
the retailer in its own corporate voice, and for any text that is neither Ukrainian, Russian nor \
English or cannot be read at all. Prefer it over a guess, but do not use it to avoid a decision \
you can make. Give the other three labels anyway where you can — an unclear row is excluded from \
scoring either way.\
"""
"""The fourth field, in the words of `docs/annotation/comments.md` §Decision rules and
§Quality control. Asked rather than defaulted: 37% of the labelled corpus carries it, and
writing ``false`` into 1,912 rows would coerce the field that decides what is scored."""


def _swap(text: str, old: str, new: str) -> str:
    """One occurrence replaced, or a refusal — a no-op replace would ship a prompt that lies."""
    if text.count(old) != 1:
        raise ValueError(f"{old[:40]!r} appears {text.count(old)} times, expected exactly one")
    return text.replace(old, new)


T1_PROMPT_V2_WITH_POST = _swap(T1_PROMPT_V2, JUDGE_TEXT_ALONE, PARENT_POST_RULE)
"""T1 under taxonomy v2, with the parent post — derived, so it cannot drift from its base.

Registered beside :data:`T1_PROMPT_V2` and never over it: `results/relabel_45e.json` and
`results/relabel_probe_45d.json` pin that prompt's SHA256, and a record whose prompt moved
is a different measurement under the same name (SPEC §7)."""

RELABEL_INTENTS_PROMPT_WITH_POST = _swap(RELABEL_INTENTS_PROMPT, JUDGE_TEXT_ALONE, PARENT_POST_RULE)

_shape_v2 = (
    '{"sentiment": "positive|negative|neutral", "sarcasm": true|false, "intents": ["price"]}'
)
PRECHECK_PROMPT_V2_WITH_POST = _swap(
    _swap(
        _swap(T1_PROMPT_V2_WITH_POST, "Return three labels.", "Return four labels."),
        "\nAnswer with one JSON object",
        f"\n{UNCLEAR_RULE}\n\nAnswer with one JSON object",
    ),
    _shape_v2,
    _shape_v2[:-1] + ', "unclear": true|false}',
)
"""All four comment fields at once — the up-label precheck's instrument (4.5g).

New rather than a revision: no v1 prompt asks for ``unclear``, so there is nothing to
register this one beside. Assembled from :data:`T1_PROMPT_V2_WITH_POST` so that the three
labels it shares with the eval prompt are the same bytes and stay that way."""

T1_PROMPT_V2_1 = _swap(
    T1_PROMPT_V2,
    "\nAnswer with one JSON object",
    f"\n{SETTLED_CASES}\n\nAnswer with one JSON object",
)
"""T1 under taxonomy v2.1 — the v2 prompt with the sitting's rulings, registered beside it.

Derived rather than retyped, for the reason every revision here is: `results/precheck_45g.json`
and `results/recheck_45g2.json` pin `precheck_v2_with_post`, and the 4.5g3 re-run is a second
measurement of the same corpus. Two prompts under one name would make the two records
indistinguishable."""

T1_PROMPT_V2_1_WITH_POST = _swap(T1_PROMPT_V2_1, JUDGE_TEXT_ALONE, PARENT_POST_RULE)
"""The v2.1 base with the parent-post clause. A build step, not a registered instrument: nothing
asks for it, and a prompt in the registry that no run can name is a hash nobody can check."""

PRECHECK_PROMPT_V2_1_WITH_POST = _swap(
    _swap(
        _swap(T1_PROMPT_V2_1_WITH_POST, "Return three labels.", "Return four labels."),
        "\nAnswer with one JSON object",
        f"\n{UNCLEAR_RULE}\n\nAnswer with one JSON object",
    ),
    _shape_v2,
    _shape_v2[:-1] + ', "unclear": true|false}',
)
"""What the second round asks. The same four fields, the same shape and the same three swaps as
:data:`PRECHECK_PROMPT_V2_WITH_POST` — the failed strata are re-labelled on the rules that moved
and on nothing else, so a difference in the returned labels is the rulings and not the wording."""

PROMPTS = {
    "T1": T1_PROMPT,
    "T2": T2_PROMPT,
    "T1v2": T1_PROMPT_V2,
    "relabel_intents_v2": RELABEL_INTENTS_PROMPT,
    "T1v2_with_post": T1_PROMPT_V2_WITH_POST,
    "relabel_intents_v2_with_post": RELABEL_INTENTS_PROMPT_WITH_POST,
    "precheck_v2_with_post": PRECHECK_PROMPT_V2_WITH_POST,
    "caption_post": CAPTION_POST_PROMPT,
    "T1v2.1": T1_PROMPT_V2_1,
    "precheck_v2.1_with_post": PRECHECK_PROMPT_V2_1_WITH_POST,
}
CAPTION_TASK = "caption_post"
FREE_TEXT = frozenset({CAPTION_TASK})
"""Prompts whose answer is prose, not labels. They are registered and hashed like the others and
are excluded from every table that only makes sense for a labelling task: no delimiter, no label
space, no field list. :func:`build_messages` and :func:`parse_reply` refuse them by name rather
than failing on a missing table entry."""

WITH_POST = frozenset(
    {
        "T1v2_with_post",
        "relabel_intents_v2_with_post",
        "precheck_v2_with_post",
        "precheck_v2.1_with_post",
    }
)
"""The tasks whose request carries the parent post. :func:`build_messages` requires one for
each of them and refuses one for every other task, so a caller cannot half-apply the change:
a with-post prompt rendered without a post promises the model something that is not there."""

DELIMITERS = {
    "T1": "comment",
    "T2": "post",
    "T1v2": "comment",
    "relabel_intents_v2": "comment",
    "T1v2_with_post": "comment",
    "relabel_intents_v2_with_post": "comment",
    "precheck_v2_with_post": "comment",
    "T1v2.1": "comment",
    "precheck_v2.1_with_post": "comment",
}
INTENTS_OF = {
    "T1": INTENTS,
    "T1v2": INTENTS_V2,
    "relabel_intents_v2": INTENTS_V2,
    "T1v2_with_post": INTENTS_V2,
    "relabel_intents_v2_with_post": INTENTS_V2,
    "precheck_v2_with_post": INTENTS_V2,
    "T1v2.1": INTENTS_V2,
    "precheck_v2.1_with_post": INTENTS_V2,
}
"""The label space each prompt promises — v1 asks for five, the v2 prompts for six.

Routed by task rather than by a module-level constant so that ``parse_reply("T1",
...)`` keeps refusing ``service``: a v1 record's numbers were produced by a parser
that could not accept it, and re-running that path leniently would produce a
different measurement under the same name."""

COMMENT_FIELDS = {
    "T1": ("sentiment", "sarcasm", "intents"),
    "T1v2": ("sentiment", "sarcasm", "intents"),
    "T1v2_with_post": ("sentiment", "sarcasm", "intents"),
    "relabel_intents_v2": ("intents",),
    "relabel_intents_v2_with_post": ("intents",),
    "precheck_v2_with_post": ("sentiment", "sarcasm", "intents", "unclear"),
    "T1v2.1": ("sentiment", "sarcasm", "intents"),
    "precheck_v2.1_with_post": ("sentiment", "sarcasm", "intents", "unclear"),
}
"""What each comment prompt asks for, and therefore what :func:`parse_reply` returns.

A table rather than a chain of ``if task ==``: the re-label's contract is that
``sentiment``, ``sarcasm`` and ``unclear`` cannot move through a path that never carries
them, and that is only true while the fields a task returns are the fields it asked for."""


class ParseError(ValueError):
    """A reply that is not a valid answer. Its ``reason`` is what gets counted."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def prompt_sha256(task: str) -> str:
    """SHA256 of the fixed prompt — the field that makes a record reproducible."""
    return hashlib.sha256(PROMPTS[task].encode("utf-8")).hexdigest()


def build_messages(
    task: str,
    text: str,
    parent: str | None = None,
    caption: str | None = None,
    caption_kind: str = "image",
) -> list[dict]:
    """The whole request: instructions, the parent post if the task takes one, and the row.

    The row is fenced in a tag so that a comment ending in "Answer with one JSON
    object" cannot read as instructions — retail comment threads contain
    everything, and a prompt-shaped comment must not get a different request
    than its neighbours. The post is fenced the same way and for the same reason.

    ``parent`` is required by exactly the tasks in :data:`WITH_POST` and refused by
    every other one. ``""`` is a parent that exists and has no text of its own; only
    ``None`` means no post was given, and for a with-post task that is a defect in the
    caller, not a row to render without one.

    ``caption`` is what stands in for a media-only post — a description of its image or
    the text of its poll, per ``caption_kind`` — and it is refused wherever it would not
    be read: by a task that takes no post at all, and by a post that has text of its own.
    "The post's text if there is any, else the surrogate" is one rule, and a caption
    silently ignored beside a text post would let two callers disagree about it without
    either of them failing.
    """
    if task in FREE_TEXT:
        raise ValueError(f"{task}: this prompt answers in prose — use caption_messages")
    tag = DELIMITERS[task]
    if (task in WITH_POST) != (parent is not None):
        raise ValueError(
            f"{task}: this prompt {'requires' if task in WITH_POST else 'takes no'} parent post,"
            f" and {'none' if parent is None else 'one'} was given"
        )
    if caption is not None and (parent is None or parent.strip()):
        raise ValueError(
            f"{task}: a caption stands in for a post that has no text of its own, and this one"
            f" {'takes no post' if parent is None else 'has text of its own'}"
        )
    if caption is not None and caption_kind not in POST_SURROGATE:
        raise ValueError(f"{caption_kind}: not one of {sorted(POST_SURROGATE)}")
    row = f"<{tag}>\n{text}\n</{tag}>"
    if parent is None:
        return [{"role": "user", "content": f"{PROMPTS[task]}\n\n{row}"}]
    post = parent.strip() or (
        POST_SURROGATE[caption_kind].format(text=caption.strip()) if caption else NO_POST_TEXT
    )
    return [{"role": "user", "content": f"{PROMPTS[task]}\n\n<post>\n{post}\n</post>\n\n{row}"}]


def caption_messages(images: list[str]) -> list[dict]:
    """The captioning request: the instructions, then every image of one post.

    A post is an album as often as it is one picture, and its text — the poll question, the
    price, the date — can be on any of them. So the images travel together in one request and
    come back as one description: a caption per image would leave whoever reads it deciding
    which picture the post was.
    """
    if not images:
        raise ValueError("a caption request with no image would describe nothing")
    return [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": PROMPTS[CAPTION_TASK]},
                *({"type": "image_url", "image_url": {"url": url}} for url in images),
            ],
        }
    ]


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
    if fields := COMMENT_FIELDS.get(task):
        _require(payload, *fields)
        intents = payload["intents"]
        if isinstance(intents, str):  # a lone label instead of a list of one
            intents = [intents]
        if not isinstance(intents, list):
            raise ParseError("intents is not a list")
        labels = {}
        if "sentiment" in fields:
            labels["sentiment"] = _choice(payload["sentiment"], "sentiment", SENTIMENT_LABELS)
        if "sarcasm" in fields:
            labels["sarcasm"] = _flag(payload["sarcasm"], "sarcasm")
        labels["intents"] = sorted({_choice(i, "intents", INTENTS_OF[task]) for i in intents})
        if "unclear" in fields:
            labels["unclear"] = _flag(payload["unclear"], "unclear")
        return labels
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
