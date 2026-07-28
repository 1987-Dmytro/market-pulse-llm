from market_pulse.synthetic import build_index, closest, frame_counts, jaccard, shingles

REAL = [
    "Аж 1 ГРИВНЯ? Оце ви ЩЕДРі)))))",
    "Товарів немає в магазинах, навіщо ця щедрість",
]


def test_shingles_are_word_trigrams_without_punctuation_or_emoji():
    assert shingles("Аж 1 гривня знижки 😂") == {"аж 1 гривня", "1 гривня знижки"}


def test_a_text_shorter_than_the_window_is_one_shingle():
    assert shingles("Цiни космос") == {"цiни космос"}


def test_jaccard_of_disjoint_and_identical_sets():
    assert jaccard({"a b c"}, {"x y z"}) == 0.0
    assert jaccard({"a b c"}, {"a b c"}) == 1.0


def test_closest_catches_a_paraphrase_of_a_real_row():
    # Only the last word differs, so 4 of each row's 5 trigrams are shared and
    # the union is 6: 4/6 — above any threshold a copy check would use.
    near = "Товарів немає в магазинах, навіщо ця акція"
    row, score = closest(near, REAL, build_index(REAL))
    assert row == 1
    assert score == 4 / 6


def test_closest_leaves_an_unrelated_row_alone():
    row, score = closest("Замовлення збирали шість годин, красені", REAL, build_index(REAL))
    assert (row, score) == (-1, 0.0)


def test_frame_counts_see_a_repeated_opening_pairwise_checks_miss():
    texts = ["Ага, знову акція одного дня", "Ага, знову цінник не той", "Дякую за увагу"]
    lead, tail = frame_counts(texts)
    assert lead["ага знову"] == 2
    assert lead["дякую за"] == 1
    assert tail.most_common(1)[0][1] == 1
