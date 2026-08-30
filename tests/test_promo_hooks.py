"""K11 — the four hooks between calls, both directions, with a negative control per hook.

The claim under test is not "the hooks pass on good rows". It is «a hook failure is a COUNTED ROW,
not an exception» (`docs/PHASE-promo-pulse-1.md` §2 S4): a bad row must be dropped, counted under
the hook that caught it, and must not take the good rows of the same answer down with it. A suite
that only fed clean rows would be green over a screen that raised on every real one
([[guard_selftest_negative_control]]).
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from market_pulse import aggregates, promo_hooks, promo_prompts  # noqa: E402

COMMENTS = [
    {"msg_id": "101", "text": "Яготинське знову подорожчало, беру щотижня"},
    {"msg_id": "102", "text": "а де це є? у нас нема"},
    {"msg_id": "103", "text": ""},
]
BRANDS = {"yagotynske", "Яготинське", "rud"}
VOCAB = promo_prompts.vocabulary()


def about(**over):
    row = {
        "msg_id": "101",
        "subject_type": "brand",
        "subject": "Яготинське",
        "source": "explicit",
        "confidence": 0.9,
    }
    return {**row, **over}


def signal(**over):
    row = {
        "type": "цена",
        "subject_type": "brand",
        "subject": "Яготинське",
        "msg_id": "101",
        "quote": "знову подорожчало",
        "confidence": 0.8,
    }
    return {**row, **over}


def screen(about_rows=None, signal_rows=None, **rest):
    answer = {"about": about_rows or [], "signals": signal_rows or [], "unsure": [], **rest}
    return promo_hooks.screen(answer, COMMENTS, BRANDS, VOCAB)


def test_a_clean_answer_keeps_every_row_and_counts_nothing():
    got = screen([about()], [signal()])
    assert got["rows_in"] == got["rows_kept"] == 2
    assert got["failures"] == []
    assert got["counts"] == dict.fromkeys(promo_hooks.HOOKS, 0)


def test_a_msg_id_the_thread_does_not_hold_is_counted_not_raised():
    got = screen([about(msg_id="999")], [signal()])
    assert got["rows_kept"] == 1, "the good row survives the bad one"
    assert got["counts"]["msg_id_exists"] == 1
    assert [f["hook"] for f in got["failures"]] == ["msg_id_exists"]
    assert got["failures"][0]["msg_id"] == "999"


def test_a_quote_that_is_not_in_the_comment_is_counted():
    """The evidence hook. A paraphrase is the failure this exists for, so the bad quote here is a
    plausible rewording of the real sentence and not a random string."""
    got = screen([], [signal(quote="ціна знову зросла")])
    assert got["rows_kept"] == 0
    assert got["counts"]["quote_is_a_substring"] == 1
    got = screen([], [signal(quote="  знову   подорожчало ")])
    assert got["rows_kept"] == 1, "whitespace is collapsed on both sides, and only whitespace"


def test_case_is_not_folded_in_a_quote():
    """A quote is what the person wrote. Folding case would let through the one class of edit a
    reader would notice at a glance."""
    assert screen([], [signal(quote="Знову Подорожчало")])["counts"]["quote_is_a_substring"] == 1


def test_an_empty_brand_is_the_one_state_neither_half_of_the_pair_can_hold():
    """`brand ∈ registry or the store's unresolved state`. Unresolved is LEGAL — `brand_id IS NULL`
    with the surface form in `brand_raw` — so an unknown brand passes and is REPORTED, and only a
    brand row with nothing to resolve and nothing to keep fails."""
    assert screen([about(subject="Молокія")], [])["rows_kept"] == 1
    assert screen([about(subject="Молокія")], [])["brand_states"] == {
        "resolved": 0,
        "raw": 1,
        "note": screen([], [])["brand_states"]["note"],
    }
    assert screen([about(subject="Яготинське")], [])["brand_states"]["resolved"] == 1
    bad = screen([about(subject="   ")], [])
    assert bad["rows_kept"] == 0 and bad["counts"]["brand_is_resolvable"] == 1


def test_a_chain_or_sku_subject_is_not_held_to_the_watchlist():
    """The hook is about brands. A chain is not a watchlist row and never was."""
    assert screen([about(subject_type="chain", subject="АТБ")], [])["rows_kept"] == 1
    assert screen([about(subject_type="sku", subject="Молоко 2.5% 900 г")], [])["rows_kept"] == 1


def test_a_class_outside_the_closed_lists_is_counted_and_never_widens_them():
    """A sixth signal type is an `unsure` row, never a new member. The hook is what makes that true
    of the wire as well as of the codebook."""
    assert screen([], [signal(type="сарказм")])["counts"]["schema_valid"] == 1
    assert screen([about(source="guessed")], [])["counts"]["schema_valid"] == 1
    assert screen([about(subject_type="person")], [])["counts"]["schema_valid"] == 1


def test_a_missing_required_field_is_counted_under_schema_and_names_the_field():
    got = screen([], [signal(quote=None)])
    assert got["counts"]["schema_valid"] == 1
    assert "missing quote" in got["failures"][0]["detail"]


def test_one_row_can_fail_two_hooks_and_is_counted_under_each():
    """The per-hook counts have to add up to something a reader can act on, which means a row that
    is wrong twice is counted twice — a per-ROW count could not say which check to fix."""
    got = screen([], [signal(msg_id="999", quote="нема такого")])
    assert got["rows_kept"] == 0
    assert got["counts"]["msg_id_exists"] == 1
    # the quote hook does not double-count a row whose comment does not exist: one failure per cause
    assert got["counts"]["quote_is_a_substring"] == 0
    both = screen([], [signal(type="сарказм", quote="нема такого")])
    assert both["counts"]["schema_valid"] == 1 and both["counts"]["quote_is_a_substring"] == 1


def test_a_parse_failure_is_carried_and_is_not_an_empty_answer():
    """An empty `about` from a refusal and an empty one from a quiet thread are two different
    things, and a class that swallowed the first would read as the second."""
    assert promo_prompts.parse("not json")["parse_failure"]
    assert screen([], [], parse_failure="Expecting value")["parse_failure"] == "Expecting value"
    assert screen([], [])["parse_failure"] is None


def test_the_prompt_and_the_tables_share_one_vocabulary():
    """Two closed lists for one concept is how a typo becomes its own bucket in every rollup."""
    assert promo_prompts.SUBJECT_TYPES == aggregates.SUBJECT_TYPES
    assert promo_prompts.SIGNAL_TYPES == aggregates.SIGNAL_TYPES
    assert promo_prompts.ATTRIBUTION_SOURCES == aggregates.ATTRIBUTION_SOURCES


def test_the_render_carries_the_law_and_the_version_is_the_render():
    """The prompt must carry the annotator's law, or the grader scores a guideline the model never
    read. And `extractor_version` is the RENDER: a comment change in the module must not move it,
    a template change must."""
    rendered = promo_prompts.render("@VARUS_channel", 4519, "Знижки тижня", COMMENTS)
    assert promo_prompts.CODEBOOK in rendered
    for name in promo_prompts.SIGNAL_TYPES:
        assert name in rendered, name
    assert "[101]" in rendered and "[103]" in rendered
    assert promo_prompts.extractor_version(rendered) != promo_prompts.codebook_version()
    # deterministic: the comments are rendered in msg_id order, not store order
    shuffled = promo_prompts.render("@VARUS_channel", 4519, "Знижки тижня", COMMENTS[::-1])
    assert promo_prompts.extractor_version(shuffled) == promo_prompts.extractor_version(rendered)
