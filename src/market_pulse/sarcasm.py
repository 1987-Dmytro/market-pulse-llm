"""Heuristic irony scoring — for ranking mining candidates, never for labelling.

G1b needs 150–200 curated sarcastic comments and the 2,000-row batch yielded far
fewer, so the rest of the corpus has to be mined. The score below only decides
which comments are worth an annotator's eyes; whether a comment is actually
ironic is decided by hand against docs/annotation/comments.md.

The signals are the ones the corpus repeats: laughter parens and laughing emoji
next to a complaint, rhetorical questions, thanks wrapped around a grievance,
praise words next to a price, promo words in scare quotes, and mock
congratulation of a giveaway winner.
"""

import re

# A marker on its own is not irony — the guideline is explicit that emoji never
# decide — so the laughter and praise signals only pay off next to a grievance.
SIGNALS = {
    "laugh": r"\){3,}|[😂🤣🙃😜😅😆😉😀😃😄🤦🙄🥲🤷]",
    "complaint": (
        r"дорог|дешев|ціна|цена|грн|обман|брехн|вранн|немає|нема\b|нет\b|зникл|"
        r"підвищ|повыс|знову|знов\b|опять|жадн|обдир|дурн|лохотрон|розвод|ганьб|"
        r"розчарув|погано|плохо|жах|кошмар|ніколи|никогда|дурак|скам|фейк|намах|"
        r"обдур|підстав|кинул|кинули|хамств|знущ"
    ),
    "rhetorical": (
        r"(серйозно|серьезно|невже|хіба|та ну|правда|справді|это как|це як|"
        r"ви думаєте|вы думаете|навіщо|для чого|і що|а що)[^.?!]*\?"
    ),
    "thanks": r"дякую|дяку[єе]мо|спасибо|благодар",
    "praise": r"молодц|супер|чудов|прекрасн|красав|щедр|смачн|вкусн|шикарн|найкращ|аж бігом",
    "scare_quotes": r"[«\"“'”]\s*(акц|знижк|скидк|подар|розіграш|новинк|варус|сільпо|атб)",
    "as_always": r"як завжди|как всегда|як зазвичай",
    "congrats": r"(віта|поздравля|вітаю)[^.!?]{0,40}(переможц|победител|счастливчик|щасливчик)",
    "gold": r"золот|фанер|прольот|пролете",
    # The corpus' loudest irony cluster: every giveaway draws accusations that the
    # winner works there. Guideline example 2 is one of these.
    "rigged": (
        r"працівник|співробітник|сотрудник|корпоративн|свої люди|своїм|родич|"
        r"родин|блат|знову виграв|опять выиграл|один і той же|одні й ті самі"
    ),
}
PATTERNS = {name: re.compile(pattern, re.IGNORECASE) for name, pattern in SIGNALS.items()}

# A signal on its own only says "worth a look" — the pairs are where irony lives,
# and the ranking exists to put the pairs first, not to keep the rest out.
WEIGHT = {
    "laugh": 1,
    "complaint": 1,
    "rhetorical": 2,
    "thanks": 1,
    "praise": 1,
    "scare_quotes": 3,
    "as_always": 2,
    "congrats": 3,
    "gold": 2,
    "rigged": 1,
}
PAIRS = {
    ("laugh", "complaint"): 3,
    ("praise", "complaint"): 3,
    ("thanks", "complaint"): 2,
    ("laugh", "rhetorical"): 2,
    ("praise", "rhetorical"): 2,
    ("rigged", "congrats"): 3,
    ("rigged", "laugh"): 2,
    ("rigged", "complaint"): 2,
    # `как всегда` marks a sincere compliment as often as a recurring farce; the
    # grievance next to it is what separates them (comments.md, counter-example).
    ("as_always", "complaint"): 2,
}

# The chains answer in their own threads; the guideline marks those `unclear`
# without exception, so they can never become sarcasm candidates.
RETAILER = re.compile(
    r"🧡|дяку[єе]мо за (ваш|звернен|запит|відгук)|передам[оу]|біжимо до вас|"
    r"розуміємо вас|в приватн[іи] повідомлен",
    re.IGNORECASE,
)
LETTERS = re.compile(r"[^\W\d_]", re.UNICODE)
MIN_LETTERS = 8


def signals(text: str) -> list[str]:
    return [name for name, pattern in PATTERNS.items() if pattern.search(text)]


def score(text: str) -> tuple[int, list[str]]:
    """Irony likelihood and the signals behind it; 0 means "not a candidate"."""
    if len(LETTERS.findall(text)) < MIN_LETTERS or RETAILER.search(text):
        return 0, []
    fired = signals(text)
    points = sum(WEIGHT[name] for name in fired)
    points += sum(bonus for pair, bonus in PAIRS.items() if set(pair) <= set(fired))
    return points, fired
