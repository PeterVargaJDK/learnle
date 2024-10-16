import pytest

from learnle_site.games.crosswords import (
    CrossWordsGridException,
    CrossWordsGrid,
    Letter
)
from learnle_site.utils import (
    Position,
    Dimensions
)

BLOCKED_ITEM_MARKER = '■'


def assert_letter_grid_item(grid: CrossWordsGrid, character: str, x: int, y: int):
    grid_item = grid.at(x, y)
    assert not grid_item.is_blocked
    assert grid_item.position == Position(x, y)
    assert grid_item.text == character


def assert_blocked_grid_item(grid: CrossWordsGrid, x: int, y: int):
    grid_item = grid.at(x, y)
    assert grid_item.is_blocked
    assert grid_item.position == Position(x, y)
    with pytest.raises(CrossWordsGridException):
        assert grid_item.text


def assert_horizontal_word(grid: CrossWordsGrid, word: str, start_x: int = 0, start_y: int = 0):
    for idx, char in enumerate(word):
        assert_letter_grid_item(grid, char, start_x + idx, start_y)


def assert_vertical_word(grid: CrossWordsGrid, word: str, start_x: int = 0, start_y: int = 0):
    for idx, char in enumerate(word):
        assert_letter_grid_item(grid, char, start_x, start_y + idx)


def assert_grid_equals(grid: CrossWordsGrid, expected_grid_text_view: str):
    actual_clean_text_view = grid.text_view()
    lines = []
    for line in expected_grid_text_view.strip().splitlines():
        lines.append(line.strip())
    assert actual_clean_text_view == '\n'.join(lines)
    assert grid.dimensions == Dimensions(len(lines[0]), len(lines))

