import pytest

from learnle_site.games.crosswords import CrossWordsGridException, GridPosition, CrossWordsGrid


def assert_letter_grid_item(grid: CrossWordsGrid, character: str, x: int, y: int):
    grid_item = grid.at(x, y)
    assert not grid_item.is_blocked()
    assert grid_item.position() == GridPosition(x, y)
    assert grid_item.text() == character


def assert_blocked_grid_item(grid: CrossWordsGrid, x: int, y: int):
    grid_item = grid.at(x, y)
    assert grid_item.is_blocked()
    assert grid_item.position() == GridPosition(x, y)
    with pytest.raises(CrossWordsGridException):
        grid_item.text()


def assert_horizontal_word(grid: CrossWordsGrid, word: str, start_x: int = 0, start_y: int = 0):
    for idx, char in enumerate(word):
        assert_letter_grid_item(grid, char, start_x + idx, start_y)


def assert_vertical_word(grid: CrossWordsGrid, word: str, start_x: int = 0, start_y: int = 0):
    for idx, char in enumerate(word):
        assert_letter_grid_item(grid, char, start_x, start_y + idx)
