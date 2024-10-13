from learnle_site.games.crosswords import (
    START_X,
    START_Y,
    CrossWordsGrid
)
from tests.utils.crosswords.assertions import (
    assert_blocked_grid_item,
    assert_horizontal_word,
    assert_vertical_word
)


def test_empty_grid():
    grid = CrossWordsGrid()
    assert_blocked_grid_item(grid, START_X, START_Y)


def test_one_char_word():
    grid = CrossWordsGrid(['a'])
    assert_horizontal_word(grid, 'a')
    assert_blocked_grid_item(grid, START_X + 1, START_Y)


def test_two_char_word():
    grid = CrossWordsGrid(['ab'])
    assert_horizontal_word(grid, 'ab')


def test_two_words_same_length__first_letter_in_common():
    grid = CrossWordsGrid(['dig', 'dry'])
    assert_horizontal_word(grid, 'dig')
    assert_vertical_word(grid, 'dry')


def test_two_words_same_length__second_letter_in_common():
    grid = CrossWordsGrid(['dig', 'odd'])
    assert_horizontal_word(grid, 'dig')
    assert_vertical_word(grid, 'odd', start_y=-1)


def test_two_words_same_length__last_letter_in_common():
    grid = CrossWordsGrid(['dig', 'rug'])
    assert_horizontal_word(grid, 'dig')
    assert_vertical_word(grid, 'rug', start_x=2, start_y=-2)


def test_three_words__two_words_share_a_character():
    grid = CrossWordsGrid(['doggy', 'ding', 'trudge'])
    assert_horizontal_word(grid, 'doggy')
    assert_vertical_word(grid, 'ding')
    assert_vertical_word(grid, 'trudge', start_x=2, start_y=-4)


def test_three_words__second_fits_into_third():
    grid = CrossWordsGrid(['doggy', 'drag', 'amend'])
    assert_horizontal_word(grid, 'doggy')
    assert_vertical_word(grid, 'drag')
    assert_horizontal_word(grid, 'amend', start_y=2)


def test_four_words__second_fits_into_third__too_close_to_first_word():
    grid = CrossWordsGrid(['dorm', 'drag', 'arm', 'ridge', 'might', 'height'])
    assert_horizontal_word(grid, 'dorm')
    assert_vertical_word(grid, 'drag')
    assert_horizontal_word(grid, 'ridge', start_x=-3, start_y=3)


def test_single_word_should_not_intersects_other_words():
    grid = CrossWordsGrid(['mould', 'among', 'new', 'undo'])
    assert_horizontal_word(grid, 'mould')
    assert_vertical_word(grid, 'among', start_y=-1)
    assert_horizontal_word(grid, 'new', start_y=2)
    assert_vertical_word(grid, 'undo', start_y=-2, start_x=4)
