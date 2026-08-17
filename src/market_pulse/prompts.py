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

CAPTION_ANSWER_ALONE = "Answer with the description alone: no preamble, no quotes, no formatting."
"""The closing clause of :data:`CAPTION_POST_PROMPT`, quoted so a derivation can swap it.

Quoted rather than spliced: :data:`CAPTION_POST_PROMPT` is a registered prompt whose sha is
pinned in `results/captions_45g2.json` and `results/captions_5c1.json`, so its bytes are not
rebuilt from parts. :func:`_swap` refuses unless this string appears in it exactly once, which
makes the quotation self-checking without the base moving."""

CAPTION_ANSWER_ALONE_GM4 = (
    "Answer with the description alone: no preamble, no quotes, no formatting, and no"
    " working-out before it — the first thing you write is the description itself."
)
"""The same clause for a model with a thinking channel (SPEC amendment 3.13 (3)).

Gemma 4 renders one, and `local_llm.CHAT_TEMPLATE` closes it with ``enable_thinking=False`` —
the template is what decides it and this sentence does not replace that. It is the belt: a
caption is free text, so a paragraph of reasoning in front of it is not a parse failure anybody
downstream can see, it is simply the wrong caption in the file."""

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

SETTLED_CASES_V2_2 = """\
Cases the annotation guideline has since settled, and they outrank the general wording above:
- A joke, a piece of trivia or banter on a topic other than the product or the retailer: set \
unclear true.
- Unsigned support wording about demand, stock or how a promo runs is the retailer speaking in \
its own voice: set unclear true, the same as for any reply the retailer signs.
- Praise of how the retailer behaves takes intents ["service"], exactly as a complaint about the \
same conduct does.
- A question about how a promo works, what its terms are or who it applies to takes intents \
["service"].
- A comment aimed at another commenter: set unclear true. When it accuses the retailer directly, \
the accusation outranks the addressee: set unclear false and judge it normally.
- An answer naming a dish, a filling or a food someone likes — as a joke or a childhood memory \
included — takes intents ["taste"].
- A quotation used to mock what it quotes — the retailer's own words, an app message or a promo \
line — sets sarcasm true, and so does a joke that elevates something ordinary into something \
grander.
- Bare thanks and a single unambiguous emoji are readable reactions: set unclear false, read the \
sentiment, and give intents [].\
"""
"""The same eight rulings as :data:`SETTLED_CASES`, said affirmatively — v2.2 (4.5g4).

The law is unchanged and the mapping is line for line (`docs/annotation/comments.md`, section
`v2.2 changelog`, marked FORM-ONLY). What changed is the voice: every line now names the output
field and the value it takes, where v2.1 said what a case is *not* — "is not a consumer reaction
at all", "never `price`", "carries no intent". The 4.5g3 re-run under v2.1 moved 172 of the 258
rows the sitting had accepted and landed 10 of its 29 stated rulings, and the label space moved
the way a model reading those negations positively would move it: `price` 110 → 313, rows with
no intent 809 → 1,366. One variable moves here — this block's wording. :data:`UNCLEAR_RULE` and
the position of the insertion are untouched, because both were in v2, which scored 86%.

The last line still restates a v2 clause rather than adding law, exactly as v2.1's did."""

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

CAPTION_POST_GM4_PROMPT = _swap(CAPTION_POST_PROMPT, CAPTION_ANSWER_ALONE, CAPTION_ANSWER_ALONE_GM4)
"""The captioning instrument on the project's own Gemma 4 — 4.5g2's task, a second model.

Registered BESIDE :data:`CAPTION_POST_PROMPT` and never over it (SPEC §7): the 4.5g2 captions
were bought under that text and its sha is pinned in the records that hold them. Derived through
:func:`_swap` for the reason every other derivation here is — the two texts differ in exactly one
clause, and a hand-copied twin could drift from its base without a test noticing.

What the swap buys is stated in :data:`CAPTION_ANSWER_ALONE_GM4`. Everything the description has
to CONTAIN is deliberately identical, because SPEC amendment 3.13 (4) pre-registers a bridge
table of GM4 against qwen on the same posts: two instruments compared on one task, not two
tasks."""

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

T1_PROMPT_V2_2 = _swap(
    T1_PROMPT_V2,
    "\nAnswer with one JSON object",
    f"\n{SETTLED_CASES_V2_2}\n\nAnswer with one JSON object",
)
"""T1 under taxonomy v2.2 — the v2 prompt with the settled cases said affirmatively.

Derived from :data:`T1_PROMPT_V2` and inserted at the same position as v2.1, so that the only
difference between the two revisions is the block itself: a change of position would be a second
variable and neither run could be charged to one of them."""

T1_PROMPT_V2_2_WITH_POST = _swap(T1_PROMPT_V2_2, JUDGE_TEXT_ALONE, PARENT_POST_RULE)
"""The v2.2 base with the parent-post clause. A build step, not a registered instrument, for the
same reason its v2.1 sibling is not one: nothing asks for it."""

PRECHECK_PROMPT_V2_2_WITH_POST = _swap(
    _swap(
        _swap(T1_PROMPT_V2_2_WITH_POST, "Return three labels.", "Return four labels."),
        "\nAnswer with one JSON object",
        f"\n{UNCLEAR_RULE}\n\nAnswer with one JSON object",
    ),
    _shape_v2,
    _shape_v2[:-1] + ', "unclear": true|false}',
)
"""What the 4.5g4 probe asks. The same three swaps as its v2 and v2.1 siblings, so the whole
difference from `precheck_v2.1_with_post` is the settled-cases block — which is what makes the
probe attributable to the rewrite rather than to a rewording somewhere else in the prompt."""

PRECHECK_PROMPT_V2CTX_WITH_POST = PRECHECK_PROMPT_V2_WITH_POST
"""The v2 precheck prompt, unchanged — what moves is the request around it (4.5g6).

Not a revision of the text: the same object as its base, so the two cannot drift and
:func:`prompt_sha256` returns one hash for both. That collision is the point and it is declared
in :data:`RENDER_ONLY`. Three prompt rewrites already failed to teach the model rules the
evidence in the row cannot support (`results/v22_probe_results.json`, KILL), so this revision
hands it the missing **evidence** instead: the two facts of `results/features_45g5.json`,
rendered beside the post. The law stays in :data:`UNCLEAR_RULE`, word for word."""

REPLY_CONTEXT = "[reply] Addressed to another commenter in the thread."
"""Rendered when the reply discriminator fires — the row's reply target is not its thread head.

A statement of fact, not a rule: it says what the row is, and `unclear`'s own wording already
says what to do about a reply aimed at another commenter. `docs/PROMPT-4.5g6.md` §Task 3 wrote
this sentence and the executor transcribed it; a test holds the two together."""

SENDER_CONTEXT = {
    "@VARUS_channel": (
        "[sender] The channel's own identity of @VARUS_channel is speaking — the retailer itself."
    ),
    "@msuaaaa": (
        "[sender] The channel's own identity of @msuaaaa is speaking — an aggregator that reposts"
        " retail offers."
    ),
}
"""One line per channel-identity pseudonym, keyed by the channel it writes in.

Two entries, because `results/features_45g5.json` measured two hyperactive senders and the next
busiest is 81 comments behind. They differ in the registry as well as in volume — one an
`official_retail` source, the other an `aggregator` — which is why the fact is rendered per
channel rather than as one sentence about "the channel"."""

CONTEXT_TEMPLATES = (REPLY_CONTEXT, *SENDER_CONTEXT.values())
"""The three lines the revision adds, in one tuple — what the transcription and negation guards
run over, and what the probe record hashes. The prompt hash cannot see them: it covers
:data:`PROMPTS`, and this revision's entry there is byte-identical to v2's."""

POSITIONS_PAGE_INTRO = """\
You read ONE page of a promotional leaflet from a Ukrainian food-retail chain and list the offers on \
it that belong to the tracked category. One page, one answer: you are not shown the rest of the \
leaflet and must not describe it."""

POSITIONS_TEXT_INTRO = """\
You read ONE row of text from a Ukrainian food-retail Telegram channel — a post or a comment — and \
list the offers in it that belong to the tracked category. Judge the text you are given: you cannot \
see any image, and you must not describe one."""

POSITIONS_BODY = """\

The tracked category is dairy — milk, kefir and ryazhanka, yogurt, curd and syrky, sour cream, \
butter, cheese, dairy desserts, plant-based milk analogs — and ice cream in any format. Anything \
else on the page is not yours: chocolate, sausage, coffee, nappies and cheese-flavoured snacks are \
not dairy, and dairy used as an ingredient in a prepared dish is not dairy either.

Return one JSON array, one object per OFFER: one product, at one size, at one price. The same \
product in two sizes is two objects. An object may carry these keys and no others.

- "brand" — the trade mark as printed, without the ТМ marker and without quotes. REQUIRED: an \
offer with no trade mark printed on it is not listed at all, however clearly it is dairy.
- "line" — the product line or product name printed beside the trade mark, as printed.
- "category" — exactly one of: dairy, milk, kefir-ryazhanka, yogurt, curd, sour-cream, butter, \
cheese, dairy-desserts, plant-based-analogs, ice-cream. Take the narrowest one the source \
supports, and "dairy" when it names a dairy product whose kind is not one of the others.
- "size" — the pack size as printed, the unit included: "450 г", "0,5 л", "1 кг", "500 мл". A \
multipack ("2х100 г") is written as printed and never multiplied out.
- "fat" — the fat percentage as printed: "2,5%".
- "price_promo" — the price being offered, as printed.
- "price_old" — the crossed-out price this offer is reduced from, as printed. Only when it is there.
- "discount_pct_printed" — the discount percentage printed on this offer, as printed: "-51%". A \
percentage printed on the page as a whole, not on this offer, is not this offer's.

Rules that outrank everything above:

- OMIT a key you cannot read. Never write an empty string, never write null, and never fill a key \
from what a product like this usually is. A missing key is an answer; a guessed one is not.
- COMPUTE NOTHING. Do not work out a discount, do not work out an old price from a percentage, do \
not convert a unit, do not round. Copy what is written.
- Never write a key that is not in the list above. In particular you are not asked how specific an \
offer is, where it was read, or who quoted the price: those are decided from your answer, not by it.
- Two prices are the offered one and the crossed-out one. If only one price is printed, it is \
"price_promo" and there is no "price_old". A hedged price — "по 90", "~90" — is written as it is \
hedged.
- Nothing of the tracked category here: return the empty array.

Answer with the JSON array alone: no explanation, no code fence, and no working-out before it — the \
first thing you write is "[".
[{"brand": "Рудь", "line": "Пломбір", "category": "ice-cream", "size": "500 г", \
"price_promo": "89,90", "price_old": "129,90", "discount_pct_printed": "-30%"}]\
"""
"""The schema half of both position prompts, byte-identical between the two legs.

SPEC 3.17 (6) pre-registers a leaflet bar and a text bar, and a difference between the two legs has
to be the leg — the page against the row — and not a schema worded twice. So the intro is the only
thing that moves and :func:`_swap` is what moves it.

The shape line is a FORMAT illustration and not a labelled example: it shows which keys exist and
how a printed size, price and percentage are copied. There is no source row beside it and no
demonstration set — the zero-shot rule of SPEC §7 covers the pre-registered T1/T2 baselines, and
these are extraction instruments for one pilot."""

POSITIONS_POST_PROMPT = POSITIONS_PAGE_INTRO + POSITIONS_BODY
"""One leaflet PAGE → the positions on it (SPEC 3.17 (4): one image = one call).

Per page rather than per post, which is what the vis-b bridge bought the right to say: an ATB album
is six pages of dense leaflet and a ~230-character caption is a SAMPLE of it
(`[[5c1-vis-b-caption-instrument]]`). Asking per page answers the caption's selectivity, the
400-token ceiling and the 10 MB transport at once."""

POSITIONS_TEXT_PROMPT = _swap(POSITIONS_POST_PROMPT, POSITIONS_PAGE_INTRO, POSITIONS_TEXT_INTRO)
"""One text row → the same schema. Derived, so the two legs cannot drift apart.

Registered BESIDE the page prompt with its own sha, never as a variant selected by a flag: a record
has to be able to name which of the two produced it, and `positions_text_gm4` is that name."""

READER_ENTITY_TYPES = ("молочный_бренд", "сеть_ритейлер", "категория_личное", "не_наш_рынок")
"""The subject taxonomy the operator ratified 2026-08-15, spelled as it was ratified.

Four readings of a NAME, which is what duty (2) of `docs/PLAN-comment-signals.md` §2 C asks for:
the same word is a dairy trade mark in a catalogue, a shop somebody walked into, a remark about the
product kind rather than the brand, or a business in another trade entirely. Russian tokens inside
an English prompt on purpose — they are the operator's ratified vocabulary, and translating them
here would make the prompt, the parser and the sitting's word three different taxonomies."""

READER_SUBJECT_TYPES = (*READER_ENTITY_TYPES[:2], "категория", *READER_ENTITY_TYPES[2:])
"""What a SIGNAL may be about: the four readings plus «категория».

The fifth word is `docs/PLAN-comment-signals.md` §3's own — its schema example carries
``{"signal_type": "спрос", "subject_type": "категория", "subject_id": "морозиво_без_цукру"}`` while
the class list two paragraphs below names four. Three of the reference pack's five flagships are
category-level findings (F1(б), F3, F4, F5) and none of them is about a named entity, so a reader
holding to the four could not report them at all. The union is taken from the design authority
rather than invented, and `results/prereg_reader_probe.json` registers the gap for the sitting:
«категория» is not in the ratified entity taxonomy, and only the operator can put it there."""

READER_SIGNAL_TYPES = ("спрос", "жалоба", "похвала", "привычка", "тренд")
"""The five ratified signal words — an OPEN list (plan §3, «открытый список — слово оператора»),
which is why the prompt offers `proposed: true` and the parser accepts a word outside this tuple
only with that flag. A sixth type invented silently would be indistinguishable in the record from
one of these five; flagged, it is an input to the adjudication sitting."""

READER_NOISE_CLASSES = ("плюс_спам", "скам", "оффтоп")
"""The noise taxonomy of the reference pack's header. The gate's silencers already remove what they
can see for free ($0, before payment); these are the reader's own name for what got through."""

READER_THREAD_PROMPT = """\
You read ONE discussion thread from a Ukrainian Telegram channel — a retail chain, a discount \
aggregator, a recipe feed or a parenting feed — and report what the marketing director of a dairy \
producer needs from it. One thread, one answer: you are given the post and every comment under it, \
and nothing else.

A SIGNAL is only what answers one of the director's seven questions: (1) what is said, good or bad, \
about a dairy trade mark; (2) what exactly is liked or disliked about it — taste, price, packaging, \
quality, availability, service; (3) the same about the competing trade marks and the chains' own \
labels; (4) which flavours and which kinds of dairy people want; (5) where it is said; (6) that the \
talk about a brand has turned sharply positive or negative; (7) what a chain promotes, at what \
price and at what discount. Anything else in this thread is not a signal, however interesting — a \
thread that carries none is a normal answer and gets an empty list.

Three duties, in this order. Never begin one before the one above it is finished.

(1) THE THREAD. The POST sets the topic: the comments are answers to it and are read in its light, \
never as texts standing on their own.

(2) THE NAMES. Every trade mark and every chain name that appears anywhere in the thread — in the \
post or in any comment — is resolved from the context it stands in: what it IS here, in one phrase, \
with the quote you read it in. Four readings and no fifth:
- "молочный_бренд" — a dairy trade mark named as a product, ours or a competitor's, a chain's own \
label included;
- "сеть_ритейлер" — a retail chain named as the shop: where somebody went, bought, ordered, or \
whose service is being discussed;
- "категория_личное" — the name stands inside a statement about the kind of product in general, \
and charging that statement to the brand would be wrong;
- "не_наш_рынок" — the name belongs to something that is not food retail at all: a school, a \
centre, a club, a housing block, a business in another trade.
A word that is both a name and an ordinary word of the language is a name only where the text uses \
it as one. Used as the ordinary word, it is not a name: do not report it and do not attach anything \
to it.

(3) THE SIGNALS. Only now, and only what duty (2) has already resolved.

Return ONE JSON object with exactly these keys.

- "thread" — {"channel": the handle you were given, "post_id": the number you were given}.
- "post_summary" — one sentence in Ukrainian: what the post is.
- "discussion_summary" — one to three sentences in Ukrainian: what the comments are about.
- "entities" — one object per name of duty (2): {"name": as it is written in the text, "msg_id": \
the comment you read it in, or null when it is in the post, "subject_type": one of the four \
readings, "reading": one phrase in Ukrainian, "quote": copied from that text}.
- "signals" — one object per signal: {"signal_type": one of "спрос", "жалоба", "похвала", \
"привычка", "тренд"; "subject_type": one of "молочный_бренд", "сеть_ритейлер", "категория", \
"категория_личное", "не_наш_рынок"; "subject_id": the trade mark, the chain or the kind of product \
as one lowercase word or phrase, or null; "aspect": one of "taste", "price", "packaging", \
"quality", "availability", "service"; "stance": "positive", "negative" or "neutral"; "reading": one \
sentence in Ukrainian for the director; "evidence": the msg_ids you read it from; "quote": copied \
from one of them}. No signal_type in the list fits what you found? Write the word you need and put \
"proposed": true beside it — a word of your own without that flag is an error.
- "per_comment" — one object per comment that carries an attitude to a named subject or to the \
tracked kind of product: {"msg_id"; "subject_type"; "subject_id" or null; "stance" or null; \
"aspects": the aspects it touches, from the six above; "note": one phrase, only where the row needs \
one}. A comment that carries neither gets no object: this is not a row per comment.
- "noise" — one object per comment that is not discussion at all: {"msg_id", "class": one of \
"плюс_спам" (a participation marker and nothing else), "скам" (money offered by a stranger with a \
handle or a link), "оффтоп" (an advertisement or a subject with nothing to do with this thread)}.

Rules that outrank everything above.

- COPY a quote, never compose one: it must appear in the message you attribute it to, character for \
character.
- Every msg_id you write is one that was given to you. The post has none: for the post the id is \
null.
- A comment belongs to at most one of "per_comment" and "noise".
- Do not carry a brand from the post into a comment that does not mention it, and do not read the \
thread's subject off the channel it is in.
- Judge what is written. Do not work out what the author probably meant, and do not report a signal \
because the post advertises something nobody discussed.
- Ukrainian in every prose field; the type words exactly as they are spelled above; the quotes in \
the language they were written in.

Answer with the JSON object alone: no explanation, no code fence, nothing before the first brace.\
"""
"""The thread reader of `docs/PLAN-comment-signals.md` §2 C — one call, one thread, one verdict.

The duty ORDER is the prompt's spine and it is the operator's clarification of 2026-08-15: the
thread first, then every name resolved from context, and only then signals. It is written as three
numbered duties with «never begin one before the one above is finished» because the failure it
guards is the one the manual reading did not make — a signal attached to a name nobody resolved,
which is how «Гармонія» the children's centre becomes brand negative.

**The four entity cases of plan §5 (4) are deliberately NOT in this text.** They are the bar; a
prompt that names them would measure how well the answers were transcribed. What the prompt carries
is the LAW they are drawn from — four readings, and «a word that is both a name and an ordinary word
of the language is a name only where the text uses it as one» — which is the rule the operator ruled
and the reader is meant to apply on its own.

No shape line either, unlike the position prompts: every object's keys are spelled out inline, so
the illustration would add nothing but a set of values a reader could copy. Zero-shot in the sense
SPEC §7 fixes — rules, no worked example."""

READER_ENTITIES_V1 = (
    '- "entities" — one object per name of duty (2): {"name": as it is written in the text,'
    ' "msg_id": the comment you read it in, or null when it is in the post, "subject_type": one of'
    ' the four readings, "reading": one phrase in Ukrainian, "quote": copied from that text}.'
)
READER_ENTITIES_V2 = (
    '- "entities" — a LIST of objects, one per name of duty (2), and the name is INSIDE each object:'
    ' [{"name": as it is written in the text, "msg_id": the comment you read it in, or null when it'
    ' is in the post, "subject_type": one of the four readings, "reading": one phrase in Ukrainian,'
    ' "quote": copied from that text}]. Never an object keyed by the names.'
)
"""Dv393, measured on all three of probe-a's paid verdicts: «one object per name» is a perfectly
good description of a map keyed by that name, and that is what the model returned — every field
right, the whole thread refused on the container ([[one_object_per_name_reads_as_a_map]]).

The brackets are written into the line and the keyed form is named and forbidden, because the list
was only ever implied by the surrounding key list. A container shape is not a taxonomy word, so no
test over the ratified vocabulary could see this one."""

READER_SIGNALS_V1 = '"evidence": the msg_ids you read it from; "quote": copied from one of them}.'
READER_SIGNALS_V2 = (
    '"evidence": the msg_ids of the COMMENTS you read it from, and the empty list [] when you read'
    ' it in the post — never null and never the post; "from_post": true when the post is where you'
    ' read it, and leave it out otherwise; "quote": copied from the post or from one of those'
    " comments}."
)

READER_NULL_RULE_V1 = (
    "- Every msg_id you write is one that was given to you. The post has none: for the post the id"
    " is null."
)
READER_NULL_RULE_V2 = (
    "- Every msg_id you write is one that was given to you. The post was given none, so null is the"
    ' answer in exactly one field — "entities"."msg_id", where it means «this name is in the post».'
    " Every other id field takes comment ids and never null."
)
"""Dv394, the two halves of one change. probe-a's third verdict carried `evidence: [null]` on a
signal the reader had read in the POST — it applied the rule above, to a field the schema requires
to be message ids, and that reply is the only one that still refused after the container defect was
coerced away. A rule stated for one field reaches every field that looks like it, so the rule is
scoped to the field it is about and the signals line is given the shape it needs instead."""

READER_THREAD_PROMPT_V2 = _swap(
    _swap(
        _swap(READER_THREAD_PROMPT, READER_ENTITIES_V1, READER_ENTITIES_V2),
        READER_SIGNALS_V1,
        READER_SIGNALS_V2,
    ),
    READER_NULL_RULE_V1,
    READER_NULL_RULE_V2,
)
"""The thread reader of `docs/PROMPT-probe-b.md` D1 — v1 with two defects closed and nothing else.

DERIVED from :data:`READER_THREAD_PROMPT` by three `_swap` calls rather than retyped, so «exactly
two wording changes» is a property of the code and not a claim in a report: every other character of
the instrument is v1's, and a fourth edit would have to appear here as a fourth call.

v1 stays registered, untouched and hashed — `results/prereg_reader_probe.json` pins its sha and
three probe-a verdicts were bought under it. A reworded schema line is a NEW instrument and gets its
own registration ([[prompt_revision_is_an_instrument_swap]]), which is why this is a second entry in
:data:`PROMPTS` and not an edit to the first."""

# --- v3: the frame the container defects came through, and the reading gap probe-b measured -------

READER_ANSWER_ALONE_V2 = (
    "Answer with the JSON object alone: no explanation, no code fence, nothing before the first"
    " brace."
)
READER_ANSWER_ALONE_V3 = (
    "Answer with ONE JSON object and nothing else: one opening brace before the first key, one"
    " closing brace after the last, and every key above INSIDE them. No explanation, no code fence,"
    " nothing before the first brace and nothing after the last — never a second object beside the"
    " first, and never a key written outside the braces."
)
"""probe-b's shape 1, closed at the source. Two of 23 replies came back as two top-level objects and
one closed its object after `discussion_summary` and went on writing `"entities": [...]` outside it.
The v3 parser merges the first shape and refuses the third, and this line is what stops both from
being written: the tolerance is belt-and-braces, not the fix (sitting ruling 2, A+B as ONE
instrument)."""

READER_ONE_OF_TWO_V2 = '- A comment belongs to at most one of "per_comment" and "noise".'
READER_ONE_OF_TWO_V3 = (
    '- A comment belongs to at most one of "per_comment" and "noise".\n'
    '- "entities", "signals", "per_comment" and "noise" are LISTS. A list with nothing in it is'
    " written [] — never {} and never an object keyed by an id or by a name."
)
"""probe-b's shapes 2 and 3, closed at the source. Five replies wrote `{}` for an empty list and one
wrote `noise` as a map keyed by msg_id; the empty-object shape alone refused four of the five noise
threads, which is where «nothing here» is the CORRECT answer. Attached to the rule about the two
comment lists because that is where the reply's containers are already being talked about."""

READER_PER_COMMENT_V2 = (
    '- "per_comment" — one object per comment that carries an attitude to a named subject or to the'
    ' tracked kind of product: {"msg_id"; "subject_type"; "subject_id" or null; "stance" or null;'
    ' "aspects": the aspects it touches, from the six above; "note": one phrase, only where the row'
    " needs one}. A comment that carries neither gets no object: this is not a row per comment."
)
READER_PER_COMMENT_V3 = (
    '- "per_comment" — one object for EVERY comment you were given, in the order you were given'
    ' them: {"msg_id"; "subject_type"; "subject_id" or null; "stance" or null; "aspects": the'
    ' aspects it touches, from the six above; "note": one phrase, only where the row needs one}. A'
    " comment that carries neither a subject nor an attitude still gets its object, with"
    ' "subject_type": null and "stance": null — that row says «read, and nothing to charge to'
    ' anybody». The only comments left out are the ones you report in "noise".'
)
"""probe-b finding 5, the largest half of the reading gap. Bar 4 scores the msg-ids the reference
names, and four of them were ABSENT from replies that parsed cleanly — the model had read the
comment and decided it carried nothing to report, which under v2's «this is not a row per comment»
is obedience. A row per payable comment turns «nothing here» into an answer the bar can score
instead of an absence it counts as a miss ([[the_empty_class_eats_the_parse_failures]], one layer
down at the row)."""

READER_DUTY_THREE_V2 = "(3) THE SIGNALS. Only now, and only what duty (2) has already resolved."
READER_DUTY_THREE_V3 = (
    "(3) THE SIGNALS. Only now, and only what duty (2) has already resolved. One thread usually"
    " carries MORE THAN ONE: report every signal you find and never stop at the first."
)
"""probe-b §5.5 and finding 5. F1 carries three signals in the reference and the run returned one of
them; bar 1 scores a flagship case as found only when EVERY signal it carries is found, so stopping
at the first is a miss the reader never sees itself make."""

READER_JUDGE_WHAT_IS_WRITTEN_V2 = (
    "- Judge what is written. Do not work out what the author probably meant, and do not report a"
    " signal because the post advertises something nobody discussed."
)
READER_JUDGE_WHAT_IS_WRITTEN_V3 = (
    "- Judge what is written. Do not work out what the author probably meant, and do not report a"
    " signal because the post advertises something nobody discussed.\n"
    "- The channel's own reply inside the thread is evidence like any other comment. When somebody"
    " asks for a kind of product and the channel answers with the trade marks it has, that exchange"
    " is a signal about demand — read it, and do not skip a comment because the shop wrote it."
)
"""F1b, the reference's own reading: «спрос · категория «морозиво без цукру» · наличие (21599; ответ
сети с SKU Рудь/Лімо — 21601)». Two of the three msg-ids that make the case are the CHANNEL's reply,
and a reader that treats a retailer's own voice as noise cannot see the demand it answers."""

READER_NOT_A_SIGNAL_V2 = (
    "Anything else in this thread is not a signal, however interesting — a thread that carries none"
    " is a normal answer and gets an empty list."
)
READER_NOT_A_SIGNAL_V3 = (
    "Praise counts: «смачне», «беру постійно» about a tracked trade mark or about the tracked kind"
    " of product is a signal (похвала) with the aspect it names, however short the comment is."
    " Anything else in this thread is not a signal, however interesting — a thread that carries none"
    " is a normal answer and gets an empty list []."
)
"""F1c, the reference's third F1 signal: «похвала · вкус (21629)». It is one short comment about
taste, and it was missed in a thread the run parsed. Stated where the SIGNAL is defined rather than
in the rules, because what it changes is the definition and not a procedure."""

READER_THREAD_PROMPT_V3 = _swap(
    _swap(
        _swap(
            _swap(
                _swap(
                    _swap(
                        READER_THREAD_PROMPT_V2,
                        READER_ANSWER_ALONE_V2,
                        READER_ANSWER_ALONE_V3,
                    ),
                    READER_ONE_OF_TWO_V2,
                    READER_ONE_OF_TWO_V3,
                ),
                READER_PER_COMMENT_V2,
                READER_PER_COMMENT_V3,
            ),
            READER_DUTY_THREE_V2,
            READER_DUTY_THREE_V3,
        ),
        READER_JUDGE_WHAT_IS_WRITTEN_V2,
        READER_JUDGE_WHAT_IS_WRITTEN_V3,
    ),
    READER_NOT_A_SIGNAL_V2,
    READER_NOT_A_SIGNAL_V3,
)
"""The thread reader of `docs/PROMPT-reader-v3-prep.md` D2 — half B of the sitting's ruling 2.

DERIVED from :data:`READER_THREAD_PROMPT_V2` by SIX `_swap` calls, the probe-b discipline applied a
second time: every change is a visible call, so «six wording changes» is a property of this file and
not a claim in a report, and a seventh edit would have to appear here as a seventh call. Two of the
six are the FRAME the container defects came through (one object, `[]` for empty) and four are the
reading gap probe-b measured — each one traceable to a miss that was PAID for, none of them a guess
about what might read better.

A and B are one registration and not two because they move the same instrument: the sitting did not
buy an ablation between the parser's tolerance and this text, so nothing downstream may attribute a
recovered reply to one of them.

v1 and v2 stay registered, untouched, hashed and servable — `results/prereg_reader_probe.json` and
`results/prereg_reader_probe_v2.json` pin their shas and 26 paid verdicts were bought under them.
:func:`reader_messages_gm4` keeps v2 as its DEFAULT for the same reason: a sealed caller must not be
handed a different instrument by a keyword it never wrote ([[a_sealed_caller_forces_the_default]]),
so v3 is opt-in and the run contract names it."""

# --- v5: the four rulings of the sitting of 2026-08-17, each traceable to a miss v4 PAID for -----

READER_ONE_ANSWER_V3 = (
    "One thread, one answer: you are given the post and every comment under it, and nothing else."
)
READER_ONE_ANSWER_V5 = (
    "One thread, one answer: you are given the post and the comments under it, and nothing else."
    " Sometimes a thread is too long to send at once and you are given a PART of it. The request"
    " then carries the line «частина i з n» before the comments, and it means what it says: the"
    " comments below that line are THIS part's comments, every duty on this page applies to them"
    " and to them only, and the other parts are not yours to answer for. Without that line you were"
    " given the whole thread."
)
"""Pair 7, the chunk header's semantics — the sitting's ruling (d), leg B.

«every comment under it» is a promise a chunked request cannot keep, and a model that believes it
has the whole thread will hallucinate the rest of it or refuse to answer for what it can see. The
line is Ukrainian because that is what `reader_messages_gm4(part=…)` renders, and the two have to
be the same string in the same alphabet ([[a_rename_the_data_cannot_follow]])."""

READER_ATTRIBUTION_V5 = (
    READER_DUTY_THREE_V3 + "\n\n"
    'ATTRIBUTION. This is what decides `subject_type`, in "signals" and in "per_comment" alike.'
    " The subject is read off THE COMMENT ITSELF and never off the thread's protagonist: not off the"
    " channel, not off the trade mark the post is about, not off the shop the comment beside it"
    " discusses. One test settles it — would the complaint or the praise still stand if the chain"
    " were a different chain, or the trade mark a different trade mark? If it would, the comment is"
    " about the KIND of product: «категория_личное», and neither the chain nor the brand."
    " «сеть_ритейлер» is the subject only where the shop AS a shop is what is being talked about —"
    " its service, its checkout, its delivery, its shelves, its queues. «молочный_бренд» only where"
    " the named trade mark is what the attitude is about. Three examples, invented for this"
    " instruction and taken from no thread:\n"
    "- «жирність у таких йогуртах давно вже не та», under a post from a chain →"
    " «категория_личное». It survives every chain, so it is not «сеть_ритейлер».\n"
    "- «на касі простояла сорок хвилин із повним візком», under a post about a trade mark →"
    " «сеть_ритейлер». It does not survive swapping the shop, so it is not «молочный_бренд».\n"
    "- «сирки з родзинками ніхто вже не робить такі, як колись», beside a comment naming one maker"
    " → «категория_личное». It is about the kind, so it is not «молочный_бренд»."
)
"""Pair 1, the attribution block — the sitting's ruling (a), and the largest single miss v4 bought.

ALL FOUR of bar 4's disagreements are `subject_type`, and not one of them is a vocabulary
disagreement: every gold value they were compared against is already the collapsed word. 21601 and
48283 are comments about a category answered as the chain; 580124 is a brand answered as the chain;
580129 is a category answered as a brand. Three confusion pairs, so three examples, one each.

The swap test is the rule and the examples are its illustration — never the other way round. Every
example is SYNTHETIC and `tests/test_reader_prompt_v5.py` proves it occurs in no stored comment, no
post, no gold file and not in the reference: teaching the exam is a red gate, and a check that
cannot fail is not a proof ([[guard_selftest_negative_control]])."""

READER_SIGNAL_SUBJECTS_V3 = (
    '"subject_type": one of "молочный_бренд", "сеть_ритейлер", "категория",'
    ' "категория_личное", "не_наш_рынок";'
)
READER_SIGNAL_SUBJECTS_V5 = (
    '"subject_type": one of "молочный_бренд", "сеть_ритейлер", "категория_личное",'
    ' "не_наш_рынок" — one word for a statement about the kind of product, and it is'
    ' "категория_личное";'
)
"""Pair 5, one vocabulary — the seam the collapse has been papering over since gold r2.

The PARSER's :data:`READER_SUBJECT_TYPES` is deliberately NOT touched: five registered records and
26 paid verdicts were validated against it, and narrowing a domain would refuse answers v1/v2/v3
runs are allowed to have made. What moves is what the v5 TEXT offers, so the two words stop being
offered as a choice; the collapse stays registered as a scoring rule, because gold r2 and probe-b's
verdict still spell it the other way ([[a_prompt_revision_is_an_instrument_swap]])."""

READER_ASPECT_V3 = (
    '"aspect": one of "taste", "price", "packaging", "quality", "availability", "service";'
)
READER_ASPECT_V5 = (
    '"aspect": one of "taste", "price", "packaging", "quality", "availability", "service" — the'
    " aspect names what the text is ABOUT and not what the product is enjoyed for, so a question"
    ' «а є у вас кефір без лактози?», or any request for a kind of product, is "availability" and'
    ' never "taste";'
)
"""Pair 2, the aspect contrast — F1b's second half.

The reference reads F1b as «спрос · категория «морозиво без цукру» · наличие», and a reader that
answers `taste` because the product is a dessert has found the right comment and charged it to the
wrong aspect. Stated where the aspect domain is, because what it changes is how that domain is
chosen and not a procedure."""

READER_PER_COMMENT_V5 = (
    '- "per_comment" — one object for EVERY comment id you were given, in the order you were given'
    " them. The ids ARE the list: each comment above carries its own msg_id, and every one of them"
    " is owed an answer — copy the id back, never invent one, and never leave one out because the"
    ' comment looked like nothing. {"msg_id"; "subject_type"; "subject_id" or null; "stance" or'
    ' null; "aspects": the aspects it touches, from the six above; "note": one phrase, only where'
    " the row needs one}. A comment that carries neither a subject nor an attitude still gets its"
    ' object, with "subject_type": null and "stance": null — that row says «read, and nothing to'
    " charge to anybody». The only ids that may be missing from this list are the ones you report"
    ' in "noise", and they have to be THERE instead: between the two lists every id you were given'
    " is answered exactly once."
)
"""Pair 6, the echo duty — the sitting's ruling (d), first leg.

MEASURED before it was written, and the measurement changed it. v4 returned 93 `per_comment` rows
against 111 requested, which the run's report reads as one row in six not written. It is not: the
other 18 are in `noise`, and over the parsed threads `per_comment ∪ noise` covers **111 of 111**
requested ids with nothing extra and nothing absent. A duty that demanded a `per_comment` row per id
would therefore refuse the answers v3's own outranking rule — «a comment belongs to at most one of
"per_comment" and "noise"» — obliges the model to give ([[count_the_kind_not_the_rows]]).

So the duty is stated over the PAIR of lists, which is the only form of it the instrument can obey,
and `reader_v5.echo` counts the three states apart: answered in `per_comment`, answered in `noise`,
absent. Only the third is a shortfall."""

READER_CARRY_V3 = (
    "- Do not carry a brand from the post into a comment that does not mention it, and do not read"
    " the thread's subject off the channel it is in."
)
READER_CARRY_V5 = (
    READER_CARRY_V3 + "\n"
    "- ONE narrow exception to the line above, and it is about EVENTS, never about opinions. A"
    " comment that reports an event changing the AVAILABILITY or the STATUS of what the post is"
    " about — a warehouse destroyed, a batch recalled, a line delisted, production stopped — is a"
    " signal about the post's subject even where the comment does not name it:"
    " «партію відкликали, у продажу її більше немає» under a post about a trade mark is"
    " availability news about THAT trade mark. An opinion with no name in it is still never carried"
    " over, and the line above stands for every «смачно», «дорого» and «не куплю більше» that names"
    " nobody."
)
"""Pair 4, the F2a carve-out — the sitting's ruling (c), and it is narrow on purpose.

F2 (`@matusi_ukr:22303`) is the reference's one case where the thread's subject IS carried into a
comment that does not name it, and v4 missed F2a. The carve-out is scoped to availability-or-status
EVENTS because that is the whole class the reference's case belongs to; widened to opinions it would
re-open the defect the rule above exists for — «Гармонія» the children's centre read as brand
negative — and cost bar 3, which is currently a PASS."""

READER_EXCHANGE_V3 = "read it, and do not skip a comment because the shop wrote it."
READER_EXCHANGE_V5 = (
    "read it, and do not skip a comment because the shop wrote it. A question and the answer it"
    ' gets are ONE signal, so its "evidence" carries BOTH msg_ids — the comment that asked and the'
    " comment that answered — and never only one of them."
)
"""Pair 3, the evidence of an exchange — F1b's first half.

The reference makes F1b out of three ids and two of them are the CHANNEL's reply: «спрос ·
категория «морозиво без цукру» · наличие (21599; ответ сети с SKU Рудь/Лімо — 21601)». v3 already
tells the reader not to skip the shop's own comment; what it never says is that the pair is one
finding, so an evidence list naming only the question is a signal the bar cannot match."""

READER_THREAD_PROMPT_V5 = _swap(
    _swap(
        _swap(
            _swap(
                _swap(
                    _swap(
                        _swap(
                            READER_THREAD_PROMPT_V3,
                            READER_ONE_ANSWER_V3,
                            READER_ONE_ANSWER_V5,
                        ),
                        READER_DUTY_THREE_V3,
                        READER_ATTRIBUTION_V5,
                    ),
                    READER_SIGNAL_SUBJECTS_V3,
                    READER_SIGNAL_SUBJECTS_V5,
                ),
                READER_ASPECT_V3,
                READER_ASPECT_V5,
            ),
            READER_PER_COMMENT_V3,
            READER_PER_COMMENT_V5,
        ),
        READER_CARRY_V3,
        READER_CARRY_V5,
    ),
    READER_EXCHANGE_V3,
    READER_EXCHANGE_V5,
)
"""The thread reader of `docs/PROMPT-reader-v5-prep.md` D1 — the sitting of 2026-08-17, in the text.

**There is deliberately no v4 prompt: the number follows the CONTRACT that registers it, not the
prompt's own generation.** reader-v4 re-registered the v3 text on a pod and measured it; this is the
first text since, so it is v5 and the gap is the honest name for what happened.

DERIVED from :data:`READER_THREAD_PROMPT_V3` by SEVEN `_swap` calls, the probe-b discipline applied
a third time: every change is a visible call, `_swap` refuses an `old` it cannot find exactly once,
and an eighth edit would have to appear here as an eighth call. Each pair is traceable to a miss
that was PAID for and none of them is a guess about what might read better — the four bar-4
disagreements (pair 1), F1b's two halves (pairs 2 and 3), F2a (pair 4), the seam gold r2 opened
(pair 5), the completeness census (pair 6) and the chunking leg (pair 7).

v1, v2 and v3 stay registered, untouched, hashed and servable, and :func:`reader_messages_gm4` keeps
v2 as its DEFAULT: every caller that passes no `task` is a caller whose evidence is already on disk
([[a_sealed_caller_forces_the_default]]). v5 is opt-in and the run contract names it."""

PROMPTS = {
    "T1": T1_PROMPT,
    "T2": T2_PROMPT,
    "T1v2": T1_PROMPT_V2,
    "relabel_intents_v2": RELABEL_INTENTS_PROMPT,
    "T1v2_with_post": T1_PROMPT_V2_WITH_POST,
    "relabel_intents_v2_with_post": RELABEL_INTENTS_PROMPT_WITH_POST,
    "precheck_v2_with_post": PRECHECK_PROMPT_V2_WITH_POST,
    "caption_post": CAPTION_POST_PROMPT,
    "caption_post_gm4": CAPTION_POST_GM4_PROMPT,
    "T1v2.1": T1_PROMPT_V2_1,
    "precheck_v2.1_with_post": PRECHECK_PROMPT_V2_1_WITH_POST,
    "T1v2.2": T1_PROMPT_V2_2,
    "precheck_v2.2_with_post": PRECHECK_PROMPT_V2_2_WITH_POST,
    "precheck_v2ctx_with_post": PRECHECK_PROMPT_V2CTX_WITH_POST,
    "positions_post_gm4": POSITIONS_POST_PROMPT,
    "positions_text_gm4": POSITIONS_TEXT_PROMPT,
    "reader_thread_gm4": READER_THREAD_PROMPT,
    "reader_thread_gm4_v2": READER_THREAD_PROMPT_V2,
    "reader_thread_gm4_v3": READER_THREAD_PROMPT_V3,
    # no `_v4`: the number follows the contract that registers a text, and reader-v4 registered v3's
    "reader_thread_gm4_v5": READER_THREAD_PROMPT_V5,
}
RENDER_ONLY = {"precheck_v2ctx_with_post": "precheck_v2_with_post"}
"""Registered tasks whose prompt text *is* another task's, mapped to the base they share.

Every other pair of entries in :data:`PROMPTS` has to hash differently — two measurements under
one hash are indistinguishable in a record. This one is deliberately the same text: the
revision is in :func:`build_messages`, not in the prompt, and declaring the exception here means
the guard that enforces distinctness reads the intent instead of hiding it. What tells the two
runs apart in a record is the rendering: the context templates and the per-row flags."""

WITH_CONTEXT = frozenset(RENDER_ONLY)
"""The tasks :func:`build_messages` will render a context line for.

Deliberately not the symmetric rule :data:`WITH_POST` uses. Context is **optional** here: 47 of
the probe's 100 rows carry neither feature, and for them the rendered request has to be the v2
request byte for byte. Required-and-refused would make that impossible; refused-for-everyone-
else is what stops a context line from reaching a prompt whose recorded runs never had one."""

REVISIONS = {
    "v2": {"T1": "T1", "T2": "T2"},
    "v4": {"T1": "T1v2_with_post", "T2": "T2"},
}
"""Which registered prompt renders each task, per frozen-test-set version.

The one place that answers "what instrument is this run using". Phase 4 rendered
:data:`TASKS` themselves — v1, five intents — and every record in
`results/baselines.json` carries their hashes. v4's gold has six, so `parse_reply("T1",
…)` refuses `service` and a v4 run cannot use them; and its `intents` were written with
the parent post in the request (`docs/annotation/comments.md` §Unit), so the with-post
revision is what scores them.

Keyed by test-set version rather than by phase because that is what makes the pairing
checkable: training, the anchor and both arms of one version must render through the same
entry, and :func:`revision_sha256` is what a record stores to prove they did.
:data:`TASKS` is deliberately untouched — widening it would make every past record fail
to verify (see its own docstring)."""


def revision_sha256(version: str) -> dict:
    """The prompt hashes of one version's rendering — what a record names its instrument by.

    ``config.prompt_sha256`` answers "are the frozen v1 prompts still the frozen v1
    prompts", which stays true through this whole change and therefore cannot see it.
    This is the field that can: it moves the day the rendering does.
    """
    if version not in REVISIONS:
        raise ValueError(f"{version}: no rendering is registered for it — {sorted(REVISIONS)}")
    return {task: prompt_sha256(name) for task, name in REVISIONS[version].items()}


CAPTION_TASK = "caption_post"
CAPTION_TASK_GM4 = "caption_post_gm4"
"""The 3.13 instrument: the same task on the project's own NF4 base, adapter off.

A second name rather than a flag, because it is what a record NAMES. `caption_source` says
which model wrote a caption and this says which text it was asked with — and the two together
are what stops a GM4 number and a qwen number from being compared in silence."""

FREE_TEXT = frozenset({CAPTION_TASK, CAPTION_TASK_GM4})
"""Prompts whose answer is prose, not labels. They are registered and hashed like the others and
are excluded from every table that only makes sense for a labelling task: no delimiter, no label
space, no field list. :func:`build_messages` and :func:`parse_reply` refuse them by name rather
than failing on a missing table entry."""

POSITIONS_TASK_PAGE = "positions_post_gm4"
POSITIONS_TASK_TEXT = "positions_text_gm4"
POSITIONS = frozenset({POSITIONS_TASK_PAGE, POSITIONS_TASK_TEXT})
"""The two position instruments of SPEC 3.17 (5). Same treatment as :data:`FREE_TEXT`: registered
and hashed like every other prompt, and out of every table that describes a *labelling* task —
their answer is a JSON array of records, not a label per row, so there is no label space and no
field list to put them in.

:func:`parse_reply` refuses them BY NAME, because their parser is a different one on purpose:
`market_pulse.positions.parse_positions` validates against the position schema, which is where the
tier ladder, the normalisation and the no-imputation rule live. A reply read by the labelling
parser would come back as a dict of labels nothing downstream could use."""

READER_TASK = "reader_thread_gm4"
READER_TASK_V2 = "reader_thread_gm4_v2"
READER_TASK_V3 = "reader_thread_gm4_v3"
READER_TASK_V5 = "reader_thread_gm4_v5"
"""No `READER_TASK_V4`: reader-v4 registered the v3 TEXT on a pod, so no fourth text was ever
written. The number follows the contract that registers a text, and the gap is what says so."""

READER = frozenset({READER_TASK, READER_TASK_V2, READER_TASK_V3, READER_TASK_V5})
"""The thread reader of the comment-signals layer. Registered and hashed like every other prompt,
and out of the three labelling tables for the same reason :data:`POSITIONS` is: its answer is one
verdict about a whole thread, not a label per row.

Unlike :data:`POSITIONS` it is **not** refused by :func:`parse_reply`. The positions parser lives in
`market_pulse.positions` because it validates a tier ladder, a normalisation and a no-imputation
rule that only mean anything for extracted offers; the reader's answer is a labelled object of the
kind this module has always read, so it is read here — one parser, `docs/PROMPT-probe-a.md` D1.

THREE registered versions since `docs/PROMPT-reader-v3-prep.md` D2, read by that one parser and
rendered by one function. Which of them a record describes is the `task` it names and the sha it
pins; v1 and v2 are frozen history and stay servable, because a run that could not re-render its own
instrument could not reproduce its own evidence.

The parser's CONTAINER tolerance is scoped to this family and therefore reaches all three, which is
the sitting's ruling read literally: it rules on how the reader's answer is READ, not on which text
asked for it. What that costs is one thing and it is stated here — a v1 or v2 reply re-read today
can parse where it once refused, so any number quoted from probe-a or probe-b comes from the record
that run WROTE and never from a re-read (SPEC §7, and `results/reader_probe_b_verdict.json` is the
registered verdict of probe-b whatever this parser would say now)."""

WITH_POST = frozenset(
    {
        "T1v2_with_post",
        "relabel_intents_v2_with_post",
        "precheck_v2_with_post",
        "precheck_v2.1_with_post",
        "precheck_v2.2_with_post",
        "precheck_v2ctx_with_post",
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
    "T1v2.2": "comment",
    "precheck_v2.2_with_post": "comment",
    "precheck_v2ctx_with_post": "comment",
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
    "T1v2.2": INTENTS_V2,
    "precheck_v2.2_with_post": INTENTS_V2,
    "precheck_v2ctx_with_post": INTENTS_V2,
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
    "T1v2.2": ("sentiment", "sarcasm", "intents"),
    "precheck_v2.2_with_post": ("sentiment", "sarcasm", "intents", "unclear"),
    "precheck_v2ctx_with_post": ("sentiment", "sarcasm", "intents", "unclear"),
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


def context_lines(reply: bool = False, sender: str | None = None) -> tuple[str, ...]:
    """The FACT lines a row's features render as, in a fixed order: reply first, sender second.

    Rendered here rather than by the caller so that one implementation writes the sentence the
    transcription guard checks — a caller assembling its own string would be a second copy of the
    template with nothing holding it to the first.
    """
    if sender is not None and sender not in SENDER_CONTEXT:
        raise ValueError(
            f"{sender}: no channel-identity line is registered for it. The two pseudonyms"
            f" results/features_45g5.json measured write in {sorted(SENDER_CONTEXT)}."
        )
    return (*([REPLY_CONTEXT] if reply else ()), *([SENDER_CONTEXT[sender]] if sender else ()))


def build_messages(
    task: str,
    text: str,
    parent: str | None = None,
    caption: str | None = None,
    caption_kind: str = "image",
    reply: bool = False,
    sender: str | None = None,
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

    ``reply`` and ``sender`` are the two features of `results/features_45g5.json`, and they are
    **optional** for the tasks in :data:`WITH_CONTEXT` and refused for every other one. A row
    carrying neither renders byte for byte what its base prompt renders — that identity is what
    makes the 4.5g6 probe a comparison rather than two unrelated runs.
    """
    if task in FREE_TEXT:
        raise ValueError(f"{task}: this prompt answers in prose — use caption_messages")
    if task in POSITIONS:
        raise ValueError(f"{task}: this prompt extracts positions — use positions_messages")
    if task in READER:
        raise ValueError(f"{task}: this prompt reads a thread — use reader_messages_gm4")
    tag = DELIMITERS[task]
    facts = context_lines(reply, sender)
    if facts and task not in WITH_CONTEXT:
        raise ValueError(
            f"{task}: this prompt takes no context lines. Its recorded runs were asked without"
            f" them, and adding one would measure {sorted(WITH_CONTEXT)[0]} under its name."
        )
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
    # empty when no feature fires, so the whole block vanishes rather than leaving a blank line
    block = "".join(f"{line}\n" for line in facts) + "\n" if facts else ""
    if parent is None:
        return [{"role": "user", "content": f"{PROMPTS[task]}\n\n{block}{row}"}]
    post = parent.strip() or (
        POST_SURROGATE[caption_kind].format(text=caption.strip()) if caption else NO_POST_TEXT
    )
    content = f"{PROMPTS[task]}\n\n<post>\n{post}\n</post>\n\n{block}{row}"
    return [{"role": "user", "content": content}]


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


def caption_messages_gm4(images: int) -> list[dict]:
    """The same request for a Hugging Face processor: the instructions, then N image slots.

    :func:`caption_messages` is OpenRouter-shaped — it carries the picture itself, as a
    ``image_url`` part holding a data URL. A local processor does not: it takes ``{"type":
    "image"}`` placeholders in the chat template and the pixels through a separate ``images=``
    argument, so the count is all this function can know and the caller owns the pairing.

    The order is the OpenRouter one — instructions first, pictures after — because SPEC
    amendment 3.13 (4) compares the two instruments on the same posts, and the position of
    the text relative to the images is one of the few things a comparison can control for
    free. Deliberately NOT a change to :func:`caption_messages`: two paid records pin that
    function's behaviour.
    """
    if images < 1:
        raise ValueError("a caption request with no image would describe nothing")
    return [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": PROMPTS[CAPTION_TASK_GM4]},
                *({"type": "image"} for _ in range(images)),
            ],
        }
    ]


def positions_messages_page_gm4(images: int = 1) -> list[dict]:
    """The page request: the instructions, then EXACTLY one image slot.

    One image is not a default, it is the ruling. SPEC 3.17 (4) fixes leaflet extraction at one
    page per call, and that single decision answers three separate failures at once: the caption's
    selectivity over a six-page album (`[[5c1-vis-b-caption-instrument]]`), the 400-token ceiling
    that truncated a reply mid-token, and the 10 MB transport limit. A second image here would
    quietly undo all three, so ``images != 1`` is refused rather than accepted and sliced.

    Processor-shaped like :func:`caption_messages_gm4`: the placeholder travels here and the pixels
    go through ``images=``, so the count is all this function can know.
    """
    if images != 1:
        raise ValueError(
            f"{images} images: leaflet extraction is one PAGE per call (SPEC 3.17 (4)) — the"
            " per-page ruling is what answers caption sampling, the 400-token ceiling and the"
            " 10 MB transport, and a batched page would undo all three"
        )
    return [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": PROMPTS[POSITIONS_TASK_PAGE]},
                {"type": "image"},
            ],
        }
    ]


def positions_messages_text_gm4(text: str) -> list[dict]:
    """The text-leg request: the instructions and the row, fenced.

    Fenced in ``<row>`` for the reason every other row in this module is: retail text contains
    everything, and a row that ends in "Answer with the JSON array alone" must not read as
    instructions. One tag for both carriers — a post and a comment are the same request here, and
    which one it was is recorded on the position, never asked of the model.
    """
    if not text.strip():
        raise ValueError("an extraction request over an empty row would extract nothing")
    return [
        {
            "role": "user",
            "content": f"{PROMPTS[POSITIONS_TASK_TEXT]}\n\n<row>\n{text}\n</row>",
        }
    ]


READER_MAX_INPUT_CHARS = 40_000
"""The LOUD ceiling on ONE rendered thread — refuse rather than truncate.

Set from the population it will run on and not from a round number: rendered through this very
function, the largest of the 111 threads of `results/gate_census_w1.json`'s narrow|silencers_on cell
is 27 593 characters — 125 payable comments under @matusi_ukr #22058, 10 784 input tokens — against
a median of 6 095, and the ceiling sits ~45% above the measured maximum. A thread over this is one
no measurement has priced, and sending it truncated would put a verdict about half a thread in the
same file, under the same instrument name, as verdicts about whole ones.

Above the population on purpose: a guard tight enough to fire on a legitimate thread would eat the
one attempt the probe has ([[lifted_ceiling_is_not_lifted_code]])."""


READER_PART_LINE = "<part>частина {i} з {n}</part>\n"
"""The one line a chunked request adds, inside the thread fence and above the comments.

Ukrainian and spelled exactly as :data:`READER_ONE_ANSWER_V5` quotes it — the prompt tells the model
what «частина i з n» means, and a header the prompt cannot name is a header the model has no law
for ([[a_rename_the_data_cannot_follow]])."""


def reader_messages_gm4(
    channel: str,
    post_id: int,
    post: str,
    comments: list[tuple[int, str]],
    *,
    task: str = READER_TASK_V2,
    part: tuple[int, int] | None = None,
) -> list[dict]:
    """One thread as the reader is given it: the post, then every payable comment with its id.

    ``part`` is ``(i, n)`` — «this is chunk i of n» — and it defaults to ``None``, which renders
    BYTE-IDENTICALLY to what every caller before it got: the header is a prefix that is the empty
    string unless a part was asked for, so there is no second construction of the request and no
    branch a frozen record's re-render can take by accident. The comments handed in are the ones
    this call sends; slicing the thread is the CALLER's job, because which chunk carries which ids
    is a registered fact and not something a renderer may decide ([[a_sealed_caller_forces_the_
    default]]).

    ``task`` names WHICH registered reader text is rendered, and defaults to the one every driver
    written so far was measured with. THREE versions exist since the reader sitting, and v3 is
    deliberately opt-in rather than the new default: every caller that passes no ``task`` is a
    caller whose evidence is already on disk, and moving the default would re-render a frozen
    record's request under a text no thread was sent with. The pair a record has to agree on is
    (the task it names, the sha it pins):
    the worker reports the sha of what it actually renders, and the driver compares that against the
    registration before a single thread is sent. A default that pointed at frozen history would make
    the quiet path the wrong one ([[a_sealed_caller_forces_the_default]]).

    The ids travel IN the request because the answer is keyed by them — every signal names the
    msg_ids it was read from, and a verdict whose evidence cannot be resolved back to a comment is
    not evidence. They are rendered as an attribute rather than inline in the text so that a comment
    which itself contains a number cannot be read as another comment's id.

    Fenced like every other row this module renders, and for the same reason: retail threads contain
    everything, and a comment ending in "Answer with the JSON object alone" must not read as
    instructions. The thread tag carries the channel and the post id, so the model can echo back
    what it was given and a driver can compare.

    A thread with no payable comment is still a thread — its post can carry the only name in it —
    but a thread with neither a post text nor a comment is nothing to read, and is refused.
    """
    if task not in READER:
        raise ValueError(f"{task}: not a registered reader prompt — {sorted(READER)}")
    ids = [msg_id for msg_id, _ in comments]
    if len(set(ids)) != len(ids):
        raise ValueError(
            f"{channel}:{post_id}: two comments share a msg_id — the evidence of every signal is"
            " that id, and a duplicate makes the answer unresolvable"
        )
    body = "".join(
        f'<comment msg_id="{msg_id}">\n{text}\n</comment>\n' for msg_id, text in comments
    )
    if not post.strip() and not body:
        raise ValueError(f"{channel}:{post_id}: no post text and no comment — nothing to read")
    header = ""
    if part is not None:
        index, total = part
        if not 1 <= index <= total:
            raise ValueError(
                f"{channel}:{post_id}: part {index} of {total} is not a part — the header would"
                " tell the model something that is not true about the request it is in"
            )
        header = READER_PART_LINE.format(i=index, n=total)
    content = (
        f'{PROMPTS[task]}\n\n<thread channel="{channel}" post_id="{post_id}">\n'
        f"<post>\n{post.strip() or NO_POST_TEXT}\n</post>\n{header}{body}</thread>"
    )
    if len(content) > READER_MAX_INPUT_CHARS:
        raise ValueError(
            f"{channel}:{post_id}: the rendered thread is {len(content)} characters, over the"
            f" registered ceiling of {READER_MAX_INPUT_CHARS}. Stop and report it — a truncated"
            " thread would be answered as if it were the whole one"
        )
    return [{"role": "user", "content": content}]


READER_LIST_FIELDS = ("entities", "signals", "per_comment", "noise")
"""The four reader fields the schema asks for as a LIST — the ones :func:`_reader_object` repairs.

Named here and not derived from the schema line: the repairs are scoped by RULING to containers the
run actually returned, and a set computed from something else would grow the day the schema does."""

TWO_OBJECTS_MERGED = "two top-level objects merged"
"""The name repair (1) logs. A constant because the refusal it is paired with and the log line have
to be greppable together, and because `repairs: [...]` is read by a scorer, not only by a human."""


def _top_level_objects(reply: str) -> list[dict]:
    """Every top-level JSON object in a reply, in order — not just the first one.

    :func:`_object` reads from the first brace and stops, which is correct for every task whose
    answer is one object and is exactly how probe-b saw half an answer twice. The wrapper handling
    is the same one, deliberately: a fence is formatting whichever branch reads it.
    """
    text = reply.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
    decoder, found, index = json.JSONDecoder(), [], 0
    while True:
        start = text.find("{", index)
        if start < 0:
            return found
        try:
            value, end = decoder.raw_decode(text[start:])
        except ValueError:
            return found
        if isinstance(value, dict):
            found.append(value)
        index = start + end


def _reader_object(reply: str) -> tuple[dict, list[str]]:
    """The reader's answer with the THREE container repairs ruled at the 2026-08-16 sitting, and
    the list of which ones fired.

    The sitting's ruling 2 (A): «the parser becomes tolerant to the CONTAINER; the domains stay
    strict». So exactly three shapes are repaired, each one measured in
    `scripts/probe_b_coercion.py::repairs()` on replies this repo paid for:

    1. an answer split into two top-level objects, merged — **and a key present in both with
       different values is REFUSED**, never last-wins. That clause is the sitting's own answer to
       the question probe-b left open, and it is what stops tolerance from becoming a silent repair
       that AUTHORS structure: two objects that disagree are two answers, and choosing one of them
       here would be the parser deciding what the model meant.
    2. ``{}`` where the schema asks for a list — the empty list. Four of probe-b's five noise
       threads answered this way, which is exactly where «nothing here» is the correct reading.
    3. a map keyed by msg_id where a list belongs — the list it describes. probe-b returned
       ``noise: {"47896": {"msg_id": "47896", …}}``: every row already carries its own id, so the
       keys are dropped rather than folded in. A map keyed by anything ELSE is not repaired — see
       the module's registered v3 changes for why that narrowing is deliberate.

    What is NOT repaired, because it is a DOMAIN and not a container: ``aspect: null`` on a signal,
    a ``from_post`` signal with no ``evidence`` key, and a bare un-braced fragment. Each of the
    three stays a refusal. A repair invents nothing; those three would each have to invent a
    reading, and the whole point of the split is that a tolerant container never buys a tolerant
    domain ([[a_container_defect_moves_to_the_next_field]]).
    """
    parts = _top_level_objects(reply)
    if not parts:
        # no object at all: `_object` owns those refusals and their exact reasons, so a reply that
        # was empty, unbraced or malformed is counted under the same cause it always was
        return _object(reply), []

    payload, repairs = dict(parts[0]), []
    for extra in parts[1:]:
        disagreeing = sorted(
            key for key, value in extra.items() if payload.get(key, value) != value
        )
        if disagreeing:
            raise ParseError(f"two disagreeing objects: {disagreeing[0]}")
        payload |= extra
        if TWO_OBJECTS_MERGED not in repairs:
            repairs.append(TWO_OBJECTS_MERGED)

    for field in READER_LIST_FIELDS:
        value = payload.get(field)
        if not isinstance(value, dict):
            continue
        if not value:
            payload[field] = []
            repairs.append(f"{field}: empty object -> empty list")
        elif all(_is_msg_id_key(key) for key in value):
            payload[field] = list(value.values())
            repairs.append(f"{field}: map keyed by msg_id -> list")
    return payload, repairs


def _is_msg_id_key(key) -> bool:
    """Is this mapping key a message id? JSON keys are strings, so the question is `int()`."""
    try:
        int(key)
    except (TypeError, ValueError):
        return False
    return True


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


def _text(value, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ParseError(f"{field} is not a non-empty string")
    return value.strip()


def _msg_id(value, field: str) -> int:
    """A message id, written as a number or as the same number in quotes.

    Both spellings are one answer — the ids arrive in the request as an attribute, which is a
    string, and a model that echoes the string it was shown has not made a mistake. ``bool`` is
    excluded by hand because it is an ``int`` in Python and ``True`` is not a message.
    """
    if isinstance(value, bool) or not isinstance(value, int | str):
        raise ParseError(f"{field} is not a msg_id")
    try:
        return int(value)
    except ValueError:
        raise ParseError(f"{field} is not a msg_id") from None


def _objects(payload: dict, field: str) -> list[dict]:
    rows = payload[field]
    if not isinstance(rows, list):
        raise ParseError(f"{field} is not a list")
    if any(not isinstance(one, dict) for one in rows):
        raise ParseError(f"{field} carries something that is not an object")
    return rows


def _reader(payload: dict) -> dict:
    """The thread verdict of :data:`READER_THREAD_PROMPT`, validated field by field.

    Strict about domains and silent about consistency, which is the split this module has always
    made: a `subject_type` outside the taxonomy is an answer nothing downstream can read, while a
    comment that appears in both ``per_comment`` and ``noise`` is a bookkeeping slip whose two rows
    are each readable. The first is refused here; the second is counted by the scorer, where the
    operator can see it. A refusal costs the whole thread, and the probe pays for every thread once.
    """
    _require(
        payload,
        "thread",
        "post_summary",
        "discussion_summary",
        "entities",
        "signals",
        "per_comment",
        "noise",
    )
    thread = payload["thread"]
    if not isinstance(thread, dict):
        raise ParseError("thread is not an object")
    _require(thread, "channel", "post_id")

    entities = []
    for one in _objects(payload, "entities"):
        _require(one, "name", "msg_id", "subject_type", "reading", "quote")
        entities.append(
            {
                "name": _text(one["name"], "entities.name"),
                # null is the POST: the name was printed by the channel, not written by a commenter
                "msg_id": (
                    None if one["msg_id"] is None else _msg_id(one["msg_id"], "entities.msg_id")
                ),
                "subject_type": _choice(
                    one["subject_type"], "entities.subject_type", READER_ENTITY_TYPES
                ),
                "reading": _text(one["reading"], "entities.reading"),
                "quote": _text(one["quote"], "entities.quote"),
            }
        )

    signals = []
    for one in _objects(payload, "signals"):
        # `stance` and `subject_id` are NOT required: plan §3's own second signal carries neither,
        # and an absent key read as null says «not stated», which is a different answer from
        # «neutral». What the contract does require of every signal is its evidence and a quote.
        _require(one, "signal_type", "subject_type", "aspect", "reading", "evidence", "quote")
        proposed = _flag(one.get("proposed", False), "signals.proposed")
        signal_type = _text(one["signal_type"], "signals.signal_type").casefold()
        if signal_type not in READER_SIGNAL_TYPES and not proposed:
            # the open list of plan §3, with its escape hatch: a sixth type is legal and has to be
            # SAID, because an unflagged one is indistinguishable in the record from a ratified word
            raise ParseError("signal_type outside its domain and not flagged proposed")
        # `from_post` is what makes an EMPTY evidence list an answer instead of a missing one
        # (Dv394): a signal read in the post has no comment to name, and the alternative the v1
        # instrument reached for was `[null]` in a field of message ids. Absent, it is false, so a
        # v1 verdict is validated by exactly the rule it was registered under.
        from_post = _flag(one.get("from_post", False), "signals.from_post")
        evidence = one["evidence"]
        if not isinstance(evidence, list):
            raise ParseError("signals.evidence is not a list")
        if not evidence and not from_post:
            raise ParseError("signals.evidence is empty and the signal is not marked from_post")
        signals.append(
            {
                "signal_type": signal_type,
                "proposed": proposed,
                "from_post": from_post,
                "subject_type": _choice(
                    one["subject_type"], "signals.subject_type", READER_SUBJECT_TYPES
                ),
                "subject_id": (
                    None
                    if one.get("subject_id") is None
                    else _text(one["subject_id"], "signals.subject_id")
                ),
                "aspect": _choice(one["aspect"], "signals.aspect", INTENTS_V2),
                "stance": (
                    None
                    if one.get("stance") is None
                    else _choice(one["stance"], "signals.stance", SENTIMENT_LABELS)
                ),
                "reading": _text(one["reading"], "signals.reading"),
                "evidence": [_msg_id(msg_id, "signals.evidence") for msg_id in evidence],
                "quote": _text(one["quote"], "signals.quote"),
            }
        )

    per_comment = []
    for one in _objects(payload, "per_comment"):
        _require(one, "msg_id", "subject_type")
        aspects = one.get("aspects") or []
        if not isinstance(aspects, list):
            raise ParseError("per_comment.aspects is not a list")
        per_comment.append(
            {
                "msg_id": _msg_id(one["msg_id"], "per_comment.msg_id"),
                "subject_type": (
                    None
                    if one["subject_type"] is None
                    else _choice(
                        one["subject_type"], "per_comment.subject_type", READER_SUBJECT_TYPES
                    )
                ),
                "subject_id": (
                    None
                    if one.get("subject_id") is None
                    else _text(one["subject_id"], "per_comment.subject_id")
                ),
                "stance": (
                    None
                    if one.get("stance") is None
                    else _choice(one["stance"], "per_comment.stance", SENTIMENT_LABELS)
                ),
                "aspects": sorted(
                    {_choice(aspect, "per_comment.aspects", INTENTS_V2) for aspect in aspects}
                ),
                "note": None if one.get("note") is None else _text(one["note"], "per_comment.note"),
            }
        )

    noise = []
    for one in _objects(payload, "noise"):
        _require(one, "msg_id", "class")
        noise.append(
            {
                "msg_id": _msg_id(one["msg_id"], "noise.msg_id"),
                "class": _choice(one["class"], "noise.class", READER_NOISE_CLASSES),
            }
        )

    return {
        "thread": {
            "channel": _text(thread["channel"], "thread.channel"),
            "post_id": _msg_id(thread["post_id"], "thread.post_id"),
        },
        "post_summary": _text(payload["post_summary"], "post_summary"),
        "discussion_summary": _text(payload["discussion_summary"], "discussion_summary"),
        "entities": entities,
        "signals": signals,
        "per_comment": per_comment,
        "noise": noise,
    }


def parse_reply(task: str, reply: str) -> dict:
    """One model reply -> the labels, or :class:`ParseError` naming what is wrong.

    Strict at the level of the whole answer: one out-of-domain field invalidates
    the object, because the object is one answer. A row that fails here is
    counted and excluded, never coerced to a default label — handing a model that
    could not answer the majority class would flatter it exactly where it is
    weakest (docs/PROMPT-3b.md; ADR 3b-infra-and-precision §(e)).
    """
    if task in FREE_TEXT:
        # By name, and before the tables — the same refusal `build_messages` makes. Falling
        # through to "unknown task" would also stop the run, but it reads as a typo in the
        # caller rather than as the registered prose prompt it is.
        raise ValueError(f"{task}: this prompt answers in prose — there is nothing to parse")
    if task in POSITIONS:
        # Same refusal, and the reason it matters more here: this reply IS JSON, so a lenient
        # reader would return `{"intents": [...]}`-shaped nothing instead of stopping.
        raise ValueError(
            f"{task}: this prompt answers with positions — use positions.parse_positions"
        )
    if task in READER:
        # read HERE and not in a module of its own: a second parser would be a second answer to
        # «was the promise kept» (docs/PROMPT-probe-a.md D1). Its reader is `_reader_object` and
        # not `_object`, because repair (1) is about the objects `_object` never looks at; every
        # other refusal still comes back through `_object` with the cause it always had.
        # `repairs` rides on EVERY reader verdict, empty list included, so a consumer can always
        # say whether an answer was read straight or coerced instead of inferring it from a
        # missing key (the sitting's ruling 2 (A), docs/PROMPT-reader-v3-prep.md D1).
        payload, repairs = _reader_object(reply)
        return _reader(payload) | {"repairs": repairs}
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
