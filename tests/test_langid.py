"""Language heuristic, checked on real strings from the collected corpus."""

import pytest
from market_pulse.langid import detect

UA = [
    "Перевіряю і в не одному немає, як завжди акція є товару немає",  # letter markers
    "Дякую за чудову рекомендацію",  # no marker letter at all, decided by words
    "Виглядають дуже смачно, поживно і корисно",
    "Як завжди коменти чистять? Чому ж ви так нас людей боїтеся?",
]
RU = [
    "Здорово конечно, но их в маркете нет, паприка только по скидке",
    "У меня тоже не работает, при чем меня выкинуло с акаунта",  # no ы/э/ъ/ё
    'Это по "Акции" а до "акции" было 932 за килограмм',
    "Арахис прелый как всегда небось",
]
EN = ["new flavour available", "ok", "Nutri-Score system"]
OTHER = ["", "+", "😂😂😂", "👍", "Вишня", "42"]


@pytest.mark.parametrize("text", UA)
def test_ukrainian(text):
    assert detect(text) == "ua"


@pytest.mark.parametrize("text", RU)
def test_russian(text):
    assert detect(text) == "ru"


@pytest.mark.parametrize("text", EN)
def test_english(text):
    assert detect(text) == "en"


@pytest.mark.parametrize("text", OTHER)
def test_undecidable_is_not_guessed(text):
    # Short Cyrillic words like "Вишня" are the same in both languages: a bucket
    # is honest, a guess would silently skew the per-language slice of G1a.
    assert detect(text) == "other"


def test_none_is_tolerated():
    assert detect(None) == "other"


def test_latin_brand_in_a_ukrainian_sentence_stays_ukrainian():
    assert detect("Наявність перевіряйте в додатку або на сайті VARUS.UA") == "ua"
