"""P1 — a deterministic post-processing layer over the frozen reader's rows. $0, pure, no I/O.

Ruling 06.09 (bb) + addendum, PHASE v18 §6.2: holdout-2 read RED on subject (0.7054) under the
instrument frozen at `d598573`, and 8 of its 33 subject misses were conventions codebook v1.2
already states — rules a program can apply, not judgements. The reader does not move for them (the
four pins stay); THIS layer runs after it and applies exactly three of those conventions:

  R1  a `post` row's subject IS the thread root                     (codebook §3: subject = root)
  R2  in a retailer's OWN channel a `post` row WITH signals is about the retailer:
      `chain` = the channel's owner                (§3: «сам канал и его посты = сеть → chain»)
  R3  a `sku`/`brand` row carrying `жалоба` whose comment says the STORE had none — the store-stock
      lexicon below — is about the store: `chain` = the thread's retailer. In the retailer's own
      channel that is the owner; under an aggregator it is the ONE registry chain the post names,
      and a post naming none or two leaves the row as it stands   (§3: «на полиці нема → chain»)

Nothing else — no sarcasm rule, no word-form rule (the addendum's own words). The rules run in
that order on every row; a row a rule rewrote carries the rule's name in `p1`, so a reading can
count what each one touched. Rows are COPIED, never edited in place: the reader's file is a
committed input and this layer may not move it.

The lexicon is the addendum's, verbatim; it was written from the codebook's words and the three
DEV error tables (dev-40, dev-2, dev-3) and never from holdout-3, which no reader has opened. Each
phrase matches at a word START and as a prefix — `прострочен` covers «прострочений» and
«прострочена», `нема` covers «немає» — on the comment's text after the grader's own normalisation
(NFC, lower, whitespace collapsed: `aggregates.promo_key`).

`chain` subjects are written the way the grader folds them: the owner as its chain ID, an
aggregator's chain as the post spelled it — `aggregates.chain_key` folds both to the chain id.
The owner's ID goes through `chain_key` too (ruling 09.09 (gg) item 2, shape (b)): the registry
gives one retailer two rows when it has two channels, and `chain_of_channel` is where the second
says whose it is — the NAME the owner used to be written under folds nowhere.
"""

from __future__ import annotations

import re

from market_pulse.aggregates import chain_key, promo_key
from market_pulse.registry import Registry, Source, chain_spellings

STORE_STOCK_LEXICON = (
    "немає",
    "нема",
    "не було",
    "нет в наличии",
    "небыло",
    "не знайшла",
    "не знайшов",
    "не можливо вхопити",
    "не можливо купити",
    "закінчується термін придатності",
    "прострочен",
)
"""Ruling 06.09 (bb) addendum, item (3) R3, verbatim — the codebook's words («наличие в магазине»,
§3) and the three DEV error tables. A word is added here by a ruling, never by a miss."""

COMPLAINT = "жалоба"
OWN_CHANNEL = "official_retail"
"""The registry `source_type` of a retailer's OWN channel — an aggregator (`@msuaaaa`) and a
community channel have no owner, so R2 never fires there and R3 reads the post instead."""

EDGE = "«»„“”‘’\"'()[]{}<>.,;:!?…-—–/\\|*#@"
"""Punctuation stripped off a token's EDGES when a post is scanned for chain names — «АТБ», or
Сільпо: — while an apostrophe INSIDE a token (McDonald’s) stays where the alias has it."""

_LEXICON = re.compile("|".join(rf"(?<!\w){re.escape(phrase)}" for phrase in STORE_STOCK_LEXICON))


def store_stock(text) -> bool:
    """Does this comment say the store had none? The lexicon at a word start, as a prefix."""
    return _LEXICON.search(promo_key(text or "")) is not None


def owner(channel, registry: Registry) -> Source | None:
    """The retailer whose OWN channel this is, or None for an aggregator / community channel."""
    key = str(channel or "").lower()
    for source in registry.sources:
        if source.source_type == OWN_CHANNEL and key in {
            one.lower() for one in source.telegram_channels
        }:
            return source
    return None


def chains_named(post, spellings: dict[str, tuple[str, ...]]) -> dict[str, str]:
    """chain id → the spelling the post used, over the registry's chain names (1- and 2-grams).

    `spellings` is `registry.chain_spellings()` — the same table `aggregates.chain_key` folds by,
    handed in so this function reads nothing. Insertion order is the post's order, and the caller
    reads the dict's SIZE: one chain named is the thread's retailer, none or two is no answer.
    """
    table = {promo_key(one): chain_id for chain_id, forms in spellings.items() for one in forms}
    tokens = [token.strip(EDGE) for token in str(post or "").split()]
    found: dict[str, str] = {}
    for gram in tokens + [f"{a} {b}" for a, b in zip(tokens, tokens[1:])]:
        chain_id = table.get(promo_key(gram)) if gram else None
        if chain_id:
            found.setdefault(chain_id, gram)
    return found


def apply(
    rows: list[dict],
    thread: dict,
    registry: Registry,
    spellings: dict[str, tuple[str, ...]] | None = None,
) -> list[dict]:
    """The three conventions over the reader's rows of ONE thread; new rows, inputs untouched.

    `thread` is what the reader saw and nothing more: `channel`, `thread_root`, `post` (its text)
    and `comments` — msg_id → text, the comment texts R3 reads. `spellings` defaults to the
    registry's chain aliases, read once per call; a caller over many threads passes them in.
    """
    spellings = chain_spellings() if spellings is None else spellings
    root = str(thread["thread_root"])
    own = owner(thread["channel"], registry)
    named = chains_named(thread.get("post"), spellings)
    retailer = (
        chain_key(own.id) if own else (next(iter(named.values())) if len(named) == 1 else None)
    )
    texts = {str(msg_id): text for msg_id, text in (thread.get("comments") or {}).items()}

    out = []
    for row in rows:
        new = dict(row)
        fired: list[str] = []
        kind = promo_key(new.get("subject_type") or "")
        signals = {promo_key(one) for one in (new.get("signal_types") or [])}
        if kind == "post" and promo_key(new.get("subject") or "") != promo_key(root):
            new["subject"] = root
            fired.append("R1")
        if kind == "post" and signals and own is not None:
            new.update(subject_type="chain", subject=retailer)
            fired.append("R2")
        elif (
            kind in ("sku", "brand")
            and COMPLAINT in signals
            and retailer is not None
            and store_stock(texts.get(str(new.get("msg_id"))))
        ):
            new.update(subject_type="chain", subject=retailer)
            fired.append("R3")
        if fired:
            new["p1"] = fired
        out.append(new)
    return out
