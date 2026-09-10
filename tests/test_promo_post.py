"""P1's three conventions, each in BOTH directions — the ONE test ruling 06.09 (bb) addendum asks
for (a product component's invariant, PHASE §3.3): a rule that fires where the codebook says and
stays quiet one step outside it. Driven against the real registry and the real alias table, because
«own channel» and «a registry chain named in the post» are facts of those two files.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from market_pulse import promo_post  # noqa: E402
from market_pulse.registry import chain_spellings, load_registry  # noqa: E402

REGISTRY = load_registry(REPO_ROOT / "config" / "registry.yaml")
SPELLINGS = chain_spellings()
OWN = "@VARUS_channel"  # a retailer's own channel (official_retail, owner `varus`)
OWNER = promo_post.owner(OWN, REGISTRY).id
"""What R2/R3 write for the own channel — the owner's chain ID, read off the registry rather
than spelled here: ruling 09.09 (gg) item 2 (b) moved it from the registry NAME, and a chain
whose second channel folds (`marketopt_private`) has no NAME that could fold at all."""
AGG = "@msuaaaa"  # the aggregator: no owner, the retailer is whoever the post names
ROOT = "4519"


def row(msg_id, kind, subject, *types):
    return {
        "channel": OWN,
        "thread_root": ROOT,
        "msg_id": msg_id,
        "subject_type": kind,
        "subject": subject,
        "source": "explicit",
        "signal_types": list(types),
    }


def thread(channel=OWN, post="Молоко Яготинське −20%", **comments):
    return {"channel": channel, "thread_root": ROOT, "post": post, "comments": comments}


def apply(rows, thread_):
    return promo_post.apply(rows, thread_, REGISTRY, SPELLINGS)


def test_r1_a_post_row_gets_the_thread_root_and_nothing_else_moves():
    """K8 compares `post` exactly, and the reader twice wrote the PARENT comment's id."""
    rows = [row("102", "post", "101"), row("103", "post", ROOT), row("104", "chain", "VARUS")]
    before = [dict(one) for one in rows]
    got = apply(rows, thread())
    assert (got[0]["subject"], got[0]["p1"]) == (ROOT, ["R1"])
    assert "p1" not in got[1] and got[1]["subject"] == ROOT, "already the root: untouched"
    assert "p1" not in got[2] and got[2] == rows[2], "a chain row is not R1's"
    assert rows == before, "the reader's rows are copied, never edited in place"


def test_r2_fires_only_in_the_retailers_own_channel_and_only_with_signals():
    """«В канале ритейлера сам канал и его посты = сеть»: a post-error with a signal is about
    VARUS in @VARUS_channel, stays `post` under the aggregator, and noise (no signals) stays
    `post` everywhere — R1 alone touches it."""
    with_signal = row("102", "post", "101", "жалоба", "цена")
    noise = row("103", "post", "101")
    own = apply([with_signal, noise], thread(OWN))
    assert (own[0]["subject_type"], own[0]["subject"]) == ("chain", OWNER)
    assert own[0]["p1"] == ["R1", "R2"]
    assert (own[1]["subject_type"], own[1]["subject"], own[1]["p1"]) == ("post", ROOT, ["R1"])
    agg = apply([with_signal], thread(AGG, post="Акція в АТБ"))
    assert (agg[0]["subject_type"], agg[0]["subject"], agg[0]["p1"]) == ("post", ROOT, ["R1"])
    community = apply([with_signal], thread("@matusi_ukr"))
    assert community[0]["subject_type"] == "post", "a community channel has no owner"


def test_r3_fires_on_a_store_stock_complaint_and_names_the_threads_retailer():
    """«на полиці нема → chain». Fires: a `sku` with `жалоба` whose comment is in the lexicon,
    to the owner in the own channel and to the ONE chain the post names under the aggregator.
    Stays: no `жалоба`, no lexicon word, a `chain`/`post` row, an aggregator post naming none
    or two chains. The lexicon matches a prefix at a word start."""
    stock = row("102", "sku", "молоко Яготинське", "жалоба")
    own = apply(
        [
            stock,
            row("103", "sku", "молоко", "жалоба"),
            row("104", "sku", "молоко", "спрос"),
            row("105", "brand", "Яготинське", "жалоба"),
            row("106", "chain", "АТБ", "жалоба"),
        ],
        thread(
            OWN,
            **{
                "102": "Приїхала — нема на полиці",
                "103": "Кисле, більше не куплю",
                "104": "А немає в Полтаві?",
                "105": "Прострочений товар лежить",
                "106": "В АТБ немає такого",
            },
        ),
    )
    assert (own[0]["subject_type"], own[0]["subject"], own[0]["p1"]) == ("chain", OWNER, ["R3"])
    assert "p1" not in own[1], "a complaint about the product itself stays a `sku`"
    assert "p1" not in own[2], "a stock QUESTION (`спрос`) is not a complaint"
    assert (own[3]["subject_type"], own[3]["subject"]) == ("chain", OWNER), "prefix «прострочен»"
    assert "p1" not in own[4], "a `chain` row is not R3's"

    one = apply([stock], thread(AGG, post="Знижки в АТБ до −30%", **{"102": "Нема в наявності"}))
    assert (one[0]["subject_type"], one[0]["subject"], one[0]["p1"]) == ("chain", "АТБ", ["R3"])
    two = apply([stock], thread(AGG, post="АТБ і Сільпо: акції", **{"102": "Нема в наявності"}))
    assert "p1" not in two[0], "two chains named: no answer, the row stays"
    none = apply([stock], thread(AGG, post="Вигідні пропозиції в Аврора", **{"102": "Нема"}))
    assert "p1" not in none[0], "Аврора is not a registry chain: the row stays"
    assert promo_post.chains_named("«Сільпо», АТБ.", SPELLINGS) == {"silpo": "Сільпо", "atb": "АТБ"}
