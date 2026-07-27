"""Offline tests for the irony heuristics that rank mining candidates.

The examples are the ones docs/annotation/comments.md declares sarcastic, quoted
from the guideline and present in data/raw/comments/. A miss costs a candidate
slot, so the bar here is "scores above zero", not "scores highest".
"""

from market_pulse.sarcasm import score

SARCASTIC = (
    "мабуть смачні млинці по 300-400 грн за кг.... таке враження, що вони не з муки, а з золота...",
    "Знову виграв працівник компанії або хтось із їхньої родини👍",
    "Софія,ми знову в прольоті,як фанера над Парижем😃😃😃",
    'Это по "Акции" а до "акции" было 932 за килограмм 😂😂😂',
    "Перевіряю і в не одному немає, як завжди акція є товару немає",
)


def test_the_guideline_examples_are_all_candidates():
    for text in SARCASTIC:
        points, fired = score(text)
        assert points > 0, f"missed: {text}"
        assert fired


def test_a_grievance_lifts_a_marker_that_alone_means_nothing():
    plain, _ = score("Виглядають дуже смачно, поживно і корисно 😂")
    bitter, _ = score("Дуже смачно, тільки ціна золота і знову немає в магазині 😂")
    assert plain < bitter


def test_a_retailer_reply_is_never_a_candidate():
    reply = "Дякуємо за ваш запит! Передамо його нашим колегам 🧡"
    assert score(reply) == (0, [])


def test_a_comment_without_words_is_not_a_candidate():
    for text in ("))))", "😂😂😂", "+", "Ага)))"):
        assert score(text) == (0, []), text


def test_the_counter_example_scores_below_the_real_thing():
    """`как всегда` marks both a sincere compliment and a recurring farce."""
    sincere, _ = score("Блинчики, как всегда, отменные ❤️")
    farce, _ = score("Перевіряю і в не одному немає, як завжди акція є товару немає")
    assert sincere < farce
