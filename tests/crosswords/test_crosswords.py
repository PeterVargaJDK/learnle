from learnle_site.games.crosswords import CrossWordsGrid
from tests.crosswords.assertions import assert_grid_equals


def add_words_and_assert_success(grid, *words):
    for word in words:
        assert grid.add_word(word)


def test_empty_grid():
    grid = CrossWordsGrid()
    assert_grid_equals(grid, '■')


def test_one_char_word():
    grid = CrossWordsGrid()
    assert grid.add_word('a')
    assert_grid_equals(
        grid,
        """
    A
    """,
    )


def test_two_char_word():
    grid = CrossWordsGrid()
    assert grid.add_word('ab')
    assert_grid_equals(
        grid,
        """
    AB
    """,
    )


def test_two_words_same_length__first_letter_in_common():
    grid = CrossWordsGrid()
    assert grid.add_word('dig')
    assert grid.add_word('dry')
    assert_grid_equals(
        grid,
        """
    DIG
    R■■
    Y■■
    """,
    )


def test_two_words__cannot_fit_together():
    grid = CrossWordsGrid()
    assert grid.add_word('dig')
    assert not grid.add_word('nope')
    assert_grid_equals(
        grid,
        """
    DIG
    """,
    )


def test_two_words_same_length__second_letter_in_common():
    grid = CrossWordsGrid()
    add_words_and_assert_success(grid, 'dig', 'odd')
    assert_grid_equals(
        grid,
        """
    O■■
    DIG
    D■■
    """,
    )


def test_two_words_same_length__last_letter_in_common():
    grid = CrossWordsGrid()
    add_words_and_assert_success(grid, 'dig', 'rug')
    assert_grid_equals(
        grid,
        """
    ■■R
    ■■U
    DIG
    """,
    )


def test_three_words__two_words_share_a_character():
    grid = CrossWordsGrid()
    add_words_and_assert_success(grid, 'doggy', 'ding', 'trudge')
    assert_grid_equals(
        grid,
        """
    ■■T■■
    ■■R■■
    ■■U■■
    ■■D■■
    DOGGY
    I■E■■
    N■■■■
    G■■■■
    """,
    )


def test_three_words__second_fits_into_third():
    grid = CrossWordsGrid()
    add_words_and_assert_success(grid, 'doggy', 'drag', 'amend')
    assert_grid_equals(
        grid,
        """
    DOGGY
    R■■■■
    AMEND
    G■■■■
    """,
    )


def test_four_words__second_fits_into_third__too_close_to_first_word():
    grid = CrossWordsGrid()
    add_words_and_assert_success(
        grid, 'dorm', 'drag', 'arm', 'ridge', 'might', 'height'
    )
    assert_grid_equals(
        grid,
        """
    ■■■■■A■
    ■■■DORM
    ■■■R■M■
    ■M■A■■■
    RIDGE■■
    ■G■■■■■
    ■HEIGHT
    ■T■■■■■
    """,
    )


def test_single_word_should_not_intersects_other_words():
    grid = CrossWordsGrid()
    add_words_and_assert_success(grid, 'mould', 'among', 'new', 'undo')
    assert_grid_equals(
        grid,
        """
    ■■■■U
    A■■■N
    MOULD
    O■■■O
    NEW■■
    G■■■■
    """,
    )


def test_single_word_should_intersects_other_words_if_only_common_letters_intersect():
    grid = CrossWordsGrid()
    add_words_and_assert_success(grid, 'mould', 'among', 'new', 'unwind')
    assert_grid_equals(
        grid,
        """
    A■■■■
    MOULD
    O■N■■
    NEW■■
    G■I■■
    ■■N■■
    ■■D■■
    """,
    )


def test_cannot_fit_touching_word():
    grid = CrossWordsGrid()
    add_words_and_assert_success(grid, 'efg', 'bde', 'jigc')
    assert not grid.add_word('abc')
    assert_grid_equals(
        grid,
        """
    B■J
    D■I
    EFG
    ■■C
    """,
    )
