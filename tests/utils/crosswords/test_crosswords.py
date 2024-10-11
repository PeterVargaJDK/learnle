from abc import ABC, abstractmethod

import pytest


class CrossWordsGridException(Exception):
    pass


class GridItem(ABC):

    @abstractmethod
    def is_blocked(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def position(self) -> tuple[int, int]:
        raise NotImplementedError

    @abstractmethod
    def text(self) -> str:
        raise NotImplementedError


class BlockedGridItem(GridItem):

    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y

    def is_blocked(self) -> bool:
        return True

    def position(self) -> tuple[int, int]:
        return self._x, self._y

    def text(self) -> str:
        raise CrossWordsGridException('Blocked grid item does not have a text representation')


class LetterGridItem(GridItem):
    def __init__(self, char: str, x: int, y: int):
        self._char = char
        self._x = x
        self._y = y

    def is_blocked(self) -> bool:
        return False

    def position(self) -> tuple[int, int]:
        return self._x, self._y

    def text(self) -> str:
        return self._char


class CrossWordsGrid:

    @staticmethod
    def _key(x: int, y: int) -> str:
        return f'{x}-{y}'

    def __init__(self, words: list[str] | None = None):
        x, y = 0, 0
        self._items = {}
        if words:
            for word in words:
                for char in word:
                    self._items[self._key(x, y)] = LetterGridItem(char, x, y)
                    x += 1

    def at(self, x: int, y: int) -> GridItem:
        if not self._items or self._key(x, y) not in self._items:
            return BlockedGridItem(x, y)

        return self._items[self._key(x, y)]


START_X = 0
START_Y = 0


def assert_letter_grid_item(grid: CrossWordsGrid, character: str, x: int, y: int):
    grid_item = grid.at(x, y)
    assert not grid_item.is_blocked()
    assert grid_item.position() == (x, y)
    assert grid_item.text() == character


def assert_blocked_grid_item(grid: CrossWordsGrid, x: int, y: int):
    grid_item = grid.at(x, y)
    assert grid_item.is_blocked()
    assert grid_item.position() == (x, y)
    with pytest.raises(CrossWordsGridException):
        grid_item.text()


def test_empty_grid():
    grid = CrossWordsGrid()
    assert_blocked_grid_item(grid, START_X, START_Y)


def test_one_char_word():
    grid = CrossWordsGrid(['a'])
    assert_letter_grid_item(grid, 'a', START_X, START_Y)
    assert_blocked_grid_item(grid, START_X + 1, START_Y)


def test_two_char_word():
    grid = CrossWordsGrid(['ab'])
    assert_letter_grid_item(grid, 'a', START_X, START_Y)
    assert_letter_grid_item(grid, 'b', START_X + 1, START_Y)


# def test_long_word():
#     pass
#
#
# def test_two_long_words():
#     pass
#
#
# def test_three_long_words():
#     pass
#
#
# def test_long_word_and_short_word():
#     pass
