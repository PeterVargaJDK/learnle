from learnle.application.model import CrosswordPuzzleLetter
from learnle.utils.crossword_grid import (
    UnpackedCrosswordGrid,
    PackedCrosswordGrid,
)
from learnle.datatypes import Dimensions, Position
from tests.crossword.assertions import assert_grid_equals


def add_words_and_assert_success(grid, *words):
    for word in words:
        assert grid.add_word(word)


def test_empty_grid():
    grid = UnpackedCrosswordGrid()
    assert_grid_equals(grid, '■')


def test_add_word__one_character():
    grid = UnpackedCrosswordGrid()
    assert grid.add_word('a')
    assert_grid_equals(
        grid,
        """
    A
    """,
    )


def test_add_word__two_characters():
    grid = UnpackedCrosswordGrid()
    assert grid.add_word('ab')
    assert_grid_equals(
        grid,
        """
    AB
    """,
    )


def test_add_word__two_words__first_letter_in_common():
    grid = UnpackedCrosswordGrid()
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


def test_add_word__two_words__second_letter_in_common():
    grid = UnpackedCrosswordGrid()
    add_words_and_assert_success(grid, 'dig', 'odd')
    assert_grid_equals(
        grid,
        """
    O■■
    DIG
    D■■
    """,
    )


def test_add_word__two_words__last_letter_in_common():
    grid = UnpackedCrosswordGrid()
    add_words_and_assert_success(grid, 'dig', 'rug')
    assert_grid_equals(
        grid,
        """
    ■■R
    ■■U
    DIG
    """,
    )


def test_add_word__two_words_cannot_fit_together():
    grid = UnpackedCrosswordGrid()
    assert grid.add_word('dig')
    assert not grid.add_word('nope')
    assert_grid_equals(
        grid,
        """
    DIG
    """,
    )


def test_add_word__three_words__two_words_share_a_character():
    grid = UnpackedCrosswordGrid()
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


def test_add_word__three_words__second_word_shares_a_character_with_third():
    grid = UnpackedCrosswordGrid()
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


def test_add_word__multiple_words__each_sharing_a_character_with_another():
    grid = UnpackedCrosswordGrid()
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


def test_add_word__last_word_would_intersect_two_words_without_matching_characters():
    grid = UnpackedCrosswordGrid()
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


def test_add_word__last_word_intersects_other_words___common_letters_intersect():
    grid = UnpackedCrosswordGrid()
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


def test_add_word__last_word_would_touch_another__cannot_fit():
    grid = UnpackedCrosswordGrid()
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


def test_add_word__maximum_dimensions_exceeded():
    grid = UnpackedCrosswordGrid(maximum_dimensions=Dimensions(5, 4))
    add_words_and_assert_success(grid, 'abcde', 'feff')
    assert not grid.add_word('fiiiiiiii')
    assert_grid_equals(
        grid,
        """
    ■■■■F
    ABCDE
    ■■■■F
    ■■■■F
    """,
    )


def test_add_word__word_forced_to_choose_intersection_that_fits_dimensions():
    grid = UnpackedCrosswordGrid(maximum_dimensions=Dimensions(5, 5))
    add_words_and_assert_success(grid, 'fbcdh', 'efghi', 'hyyyy')
    assert_grid_equals(
        grid,
        """
    E■■■■
    FBCDH
    G■■■■
    HYYYY
    I■■■■
    """,
    )


def test_packed_grid():
    grid = UnpackedCrosswordGrid()
    add_words_and_assert_success(grid, 'abc', 'defa', 'ghd')

    packed_grid = PackedCrosswordGrid(grid)
    assert list(packed_grid.letters()) == [
        CrosswordPuzzleLetter(character='a', position=Position(x=2, y=3)),
        CrosswordPuzzleLetter(character='b', position=Position(x=3, y=3)),
        CrosswordPuzzleLetter(character='c', position=Position(x=4, y=3)),
        CrosswordPuzzleLetter(character='d', position=Position(x=2, y=0)),
        CrosswordPuzzleLetter(character='e', position=Position(x=2, y=1)),
        CrosswordPuzzleLetter(character='f', position=Position(x=2, y=2)),
        CrosswordPuzzleLetter(character='g', position=Position(x=0, y=0)),
        CrosswordPuzzleLetter(character='h', position=Position(x=1, y=0)),
    ]
    assert packed_grid.dimensions() == grid.dimensions
