"""Language guess for UA / RU / EN comments and posts.

A heuristic on purpose: it feeds stratification and the per-language slices of
G1a, where a wrong bucket costs a slightly uneven sample, not a wrong metric. No
model, no dependency, no training data.

The alphabet markers (і/ї/є/ґ against ы/э/ъ/ё) decide most of the corpus, but a
fifth of it is short Cyrillic text carrying no distinctive letter at all —
"Дякую" and "Спасибо" are both invisible to them. A small list of frequent words
that differ between the two languages resolves those.
"""

import re

UA_LETTERS = frozenset("іїєґ")
RU_LETTERS = frozenset("ыэъё")

UA_WORDS = frozenset(
    """що це як якщо щоб чи але наче мабуть звичайно взагалі теж також
    дякую дякуємо знижка знижки ціна ціни цін немає дуже вже або чому коли куди
    завжди зараз потім після тільки тут мене мені можна потрібно треба
    зробити купити працює буде були гроші смачно смачні гарно гарний гарна
    магазині наявність наявності ласка мають має чекаю замовлення""".split()
)
RU_WORDS = frozenset(
    """что это как если чтобы или но кажется наверное конечно вообще тоже также
    спасибо скидка скидки цена цены нет очень уже почему когда куда
    всегда сейчас потом после только здесь меня мне можно нужно надо
    сделать купить работает будет были деньги вкусно вкусные хорошо хороший
    магазине наличие пожалуйста имеют жду заказ""".split()
)

_CYRILLIC = re.compile(r"[а-яёіїєґ]")
_LATIN = re.compile(r"[a-z]")
_WORD = re.compile(r"[а-яёіїєґ']+")


def detect(text: str) -> str:
    """Return ``ua``, ``ru``, ``en`` or ``other`` (emoji, digits, undecidable)."""
    low = (text or "").lower()
    cyrillic = _CYRILLIC.findall(low)
    if not cyrillic:
        # Two letters keep "ok" and "new" as English but leave "+" and "😂" out.
        return "en" if len(_LATIN.findall(low)) >= 2 else "other"

    ua = sum(1 for char in cyrillic if char in UA_LETTERS)
    ru = sum(1 for char in cyrillic if char in RU_LETTERS)
    words = set(_WORD.findall(low))
    ua += len(words & UA_WORDS)
    ru += len(words & RU_WORDS)

    if ua > ru:
        return "ua"
    if ru > ua:
        return "ru"
    return "other"
